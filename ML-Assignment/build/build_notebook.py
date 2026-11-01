import sys
from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "COM7022_Task1_Clustering.ipynb"

cells = []


def md(text):
    cells.append(nbf.v4.new_markdown_cell(text.strip()))


def code(text):
    cells.append(nbf.v4.new_code_cell(text.strip()))


md("""
# COM7022 Machine Learning: Task 1, Clustering e-commerce products

Student ID: **[YOUR STUDENT ID]**

Goal: group the products in the sales dataset by their characteristics and sales performance using K-Means, Hierarchical clustering and DBSCAN, then compare the models and describe the clusters.
""")

md("## 1. Libraries and settings")
code("""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import (silhouette_score, silhouette_samples, davies_bouldin_score,
                             calinski_harabasz_score, adjusted_rand_score)

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", font_scale=0.95)
pd.set_option("display.max_columns", 20)
pd.set_option("display.width", 150)
pd.set_option("display.max_colwidth", 22)

SEED = 42
FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)
COLOURS = ["#2f6db5", "#e07b39", "#3a9d5d", "#c4453c", "#8064a2", "#7f7f7f"]
""")

md("## 2. Loading and understanding the data")
code("""
df_raw = pd.read_csv("assignquestion.csv", encoding="utf-8-sig")
print("Shape:", df_raw.shape)
df_raw.head(3)
""")
code("""
df_raw.info()
print("\\nDuplicate rows:", df_raw.duplicated().sum())
print("Unique brands:", df_raw["Item_Name"].nunique())
print("Unique category labels:", df_raw["Catatory"].nunique())
print("Unique locations:", df_raw["itemLocation"].nunique())
""")
code("""
df_raw.describe().round(2)
""")
code("""
missing = df_raw.isna().sum()
missing = missing[missing > 0].sort_values()

fig, ax = plt.subplots(figsize=(7, 3.2))
ax.barh(missing.index, missing.values, color="#c4453c")
for i, v in enumerate(missing.values):
    ax.text(v + 1, i, f"{v} ({v / len(df_raw):.1%})", va="center", fontsize=9)
ax.set_xlabel("Missing values")
ax.set_title("Missing values per column (raw data)")
ax.set_xlim(0, missing.max() * 1.3)
plt.tight_layout()
plt.savefig(FIG_DIR / "fig01_missing_values.png", dpi=150)
plt.show()
""")
md("The `text` and `priceWithCurrency` columns repeat information from other columns, so they can be used to fill some of the gaps.")
code("""
print(df_raw["text"].str.replace(r"[\\d,]+", "N", regex=True).value_counts(), "\\n")
print(df_raw["priceWithCurrency"].str.extract(r"^(\\D+)")[0].value_counts(), "\\n")
print(df_raw["Catatory"].value_counts().head(12))
""")

md("## 3. Data cleaning")
code("""
df = df_raw.rename(columns={"Item_Name": "brand", "Catatory": "category_raw"}).copy()

price_text = df["priceWithCurrency"].fillna("").str.replace(",", "")
df["price"] = df["price"].fillna(price_text.str.extract(r"([\\d.]+)")[0].astype(float))
cad = price_text.str.startswith("C")
df.loc[cad, "price"] = df.loc[cad, "price"] * 0.73

stock_text = df["text"].fillna("").str.replace(",", "")
df["sold"] = df["sold"].fillna(stock_text.str.extract(r"(\\d+) sold")[0].astype(float))
df["sold"] = df["sold"].fillna(0)
df.loc[stock_text.str.startswith("Last One"), "available"] = 1
df["available"] = df["available"].fillna(df["available"].median())

updated = pd.to_datetime(df["lastUpdated"].str[:-4], format="%b %d, %Y %H:%M:%S", errors="coerce")
df["days_since_update"] = (updated.max() - updated).dt.total_seconds() / 86400
df["days_since_update"] = df["days_since_update"].fillna(df["days_since_update"].median())

details = df["details"].str.lower()
ml = details.str.extract(r"(\\d+(?:\\.\\d+)?)\\s*ml")[0].astype(float)
oz = details.str.extract(r"(\\d+(?:\\.\\d+)?)\\s*(?:fl\\.?\\s*)?oz")[0].astype(float)
df["size_ml"] = ml.fillna(oz * 29.57)
print("Size found in title for", f"{df['size_ml'].notna().mean():.1%}", "of listings")
df["size_ml"] = df["size_ml"].fillna(df["size_ml"].median())

df["brand"] = df["brand"].fillna("Unbranded").str.strip()
df["country"] = df["itemLocation"].str.split(",").str[-1].str.strip()
df["ships_from_us"] = (df["country"] == "United States").astype(int)

print("Prices converted from CAD:", cad.sum())
print("'Last One' listings set to 1 available:", stock_text.str.startswith("Last One").sum())
print("Latest update in data:", updated.max())
print("\\nMissing values after cleaning:")
print(df[["price", "sold", "available", "days_since_update", "size_ml", "brand"]].isna().sum())
""")
md("### Grouping the category labels")
code("""
cat = df["category_raw"].fillna("").str.lower()
rules = [cat.str.contains("toil|edt"),
         cat.str.contains("parf|perf|elixir|extrait"),
         cat.str.contains("cologne|edc")]
df["category"] = np.select(rules, ["Eau de Toilette", "Eau de Parfum/Parfum", "Cologne"], default="Other")

print(df["category"].value_counts(), "\\n")
print(df["country"].value_counts().head(6))

fig, axes = plt.subplots(1, 2, figsize=(11, 3.4))
df["category"].value_counts().plot(kind="bar", ax=axes[0], color=COLOURS[0], rot=0)
axes[0].set_title("Listings by grouped category")
axes[0].set_ylabel("Listings")
df["country"].value_counts().head(6).plot(kind="bar", ax=axes[1], color=COLOURS[1], rot=0)
axes[1].set_title("Listings by item location (top 6)")
plt.tight_layout()
plt.savefig(FIG_DIR / "fig02_categories_locations.png", dpi=150)
plt.show()
""")

md("## 4. Outliers and skewness")
code("""
num_cols = ["price", "sold", "available", "days_since_update", "size_ml"]

rows = []
for col in num_cols:
    q1, q3 = df[col].quantile([0.25, 0.75])
    iqr = q3 - q1
    n_out = ((df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)).sum()
    rows.append([col, df[col].median(), df[col].max(), n_out, df[col].skew(), np.log1p(df[col]).skew()])

outlier_table = pd.DataFrame(rows, columns=["feature", "median", "max", "IQR outliers", "skew raw", "skew log1p"])
outlier_table.round(2)
""")
code("""
fig, axes = plt.subplots(2, 5, figsize=(16, 5.5))
for i, col in enumerate(num_cols):
    axes[0, i].hist(df[col], bins=40, color=COLOURS[0])
    axes[0, i].set_title(f"{col} (raw)")
    axes[1, i].hist(np.log1p(df[col]), bins=40, color=COLOURS[2])
    axes[1, i].set_title(f"log(1 + {col})")
plt.tight_layout()
plt.savefig(FIG_DIR / "fig03_distributions_raw_vs_log.png", dpi=150)
plt.show()
""")

md("## 5. Feature selection")
code("""
X_log = np.log1p(df[num_cols])

fig, ax = plt.subplots(figsize=(6, 4.6))
sns.heatmap(X_log.corr(), annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, ax=ax)
ax.set_title("Correlation of log-transformed features")
plt.tight_layout()
plt.savefig(FIG_DIR / "fig04_correlation.png", dpi=150)
plt.show()
""")
md("Testing whether the one-hot encoded category should go into the distance calculation.")
code("""
X_std = StandardScaler().fit_transform(X_log)
dummies = pd.get_dummies(df[["category"]], dtype=float)
X_with_cat = np.hstack([X_std, StandardScaler().fit_transform(dummies)])

km_cat = KMeans(n_clusters=4, n_init=20, random_state=SEED).fit(X_with_cat)
print("Silhouette with category dummies:", round(silhouette_score(X_with_cat, km_cat.labels_), 3))
pd.crosstab(km_cat.labels_, df["category"], rownames=["cluster"])
""")

md("## 6. Scaling and normalisation")
code("""
scalers = {"StandardScaler": StandardScaler(), "MinMaxScaler": MinMaxScaler(), "RobustScaler": RobustScaler()}

rows = []
spread = {}
for name, scaler in scalers.items():
    Xs = scaler.fit_transform(X_log)
    spread[name] = Xs.std(axis=0).round(2)
    for k in [3, 4, 5, 6]:
        labels = KMeans(n_clusters=k, n_init=20, random_state=SEED).fit_predict(Xs)
        rows.append([name, k, silhouette_score(Xs, labels)])

scaler_table = pd.DataFrame(rows, columns=["scaler", "k", "silhouette"]).pivot(index="scaler", columns="k", values="silhouette")
print(scaler_table.round(3), "\\n")
print("Standard deviation of each feature after scaling:")
pd.DataFrame(spread, index=num_cols).T
""")
code("""
X = StandardScaler().fit_transform(X_log)
print(X.shape)
print(pd.DataFrame(X, columns=num_cols).describe().loc[["mean", "std"]].round(2))
""")

md("## 7. Dimensionality reduction with PCA")
code("""
pca = PCA(random_state=SEED).fit(X)
ratio = pca.explained_variance_ratio_

fig, ax = plt.subplots(figsize=(6.5, 3.6))
ax.bar(range(1, 6), ratio, color=COLOURS[0], label="Individual")
ax.plot(range(1, 6), ratio.cumsum(), marker="o", color=COLOURS[1], label="Cumulative")
for i, v in enumerate(ratio.cumsum()):
    ax.text(i + 1, v + 0.03, f"{v:.0%}", ha="center", fontsize=9)
ax.set_xlabel("Principal component")
ax.set_ylabel("Explained variance")
ax.set_ylim(0, 1.12)
ax.set_title("PCA explained variance")
ax.legend(loc="center right")
plt.tight_layout()
plt.savefig(FIG_DIR / "fig05_pca_variance.png", dpi=150)
plt.show()

loadings = pd.DataFrame(pca.components_[:2].T, index=num_cols, columns=["PC1", "PC2"])
loadings.round(2)
""")
code("""
X_pca = PCA(n_components=2, random_state=SEED).fit_transform(X)
""")

md("## 8. K-Means")
code("""
rows = []
for k in range(2, 11):
    km = KMeans(n_clusters=k, n_init=20, random_state=SEED).fit(X)
    rows.append([k, km.inertia_, silhouette_score(X, km.labels_),
                 davies_bouldin_score(X, km.labels_), calinski_harabasz_score(X, km.labels_)])
k_table = pd.DataFrame(rows, columns=["k", "inertia", "silhouette", "davies_bouldin", "calinski_harabasz"])

fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
axes[0].plot(k_table["k"], k_table["inertia"], marker="o", color=COLOURS[0])
axes[0].set_title("Elbow method")
axes[0].set_xlabel("k")
axes[0].set_ylabel("Inertia (WCSS)")
axes[1].plot(k_table["k"], k_table["silhouette"], marker="o", color=COLOURS[2])
axes[1].set_title("Silhouette score by k")
axes[1].set_xlabel("k")
axes[1].set_ylabel("Silhouette")
plt.tight_layout()
plt.savefig(FIG_DIR / "fig06_kmeans_elbow_silhouette.png", dpi=150)
plt.show()
k_table.round(3)
""")
md("Checking how stable each k is when only the random starting point changes (adjusted Rand index against the seed-42 solution).")
code("""
rows = []
for k in range(3, 7):
    base = KMeans(n_clusters=k, n_init=20, random_state=SEED).fit_predict(X)
    scores = [adjusted_rand_score(base, KMeans(n_clusters=k, n_init=1, random_state=s).fit_predict(X)) for s in range(20)]
    rows.append([k, np.mean(scores), np.min(scores)])
pd.DataFrame(rows, columns=["k", "mean ARI", "min ARI"]).round(3)
""")
code("""
kmeans = KMeans(n_clusters=5, n_init=20, random_state=SEED).fit(X)
df["kmeans"] = kmeans.labels_
print(df["kmeans"].value_counts().sort_index())
""")

md("## 9. Hierarchical clustering")
code("""
Z = linkage(X, method="ward")

fig, ax = plt.subplots(figsize=(11, 4))
dendrogram(Z, truncate_mode="lastp", p=30, ax=ax, color_threshold=Z[-5, 2], above_threshold_color="grey")
ax.axhline(Z[-5, 2], color="red", linestyle="--", label="cut for 5 clusters")
ax.set_title("Ward dendrogram (last 30 merges)")
ax.set_xlabel("Cluster size")
ax.set_ylabel("Distance")
ax.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "fig07_dendrogram.png", dpi=150)
plt.show()
""")
code("""
rows = []
for method in ["ward", "complete", "average"]:
    for k in [3, 4, 5, 6]:
        labels = AgglomerativeClustering(n_clusters=k, linkage=method).fit_predict(X)
        rows.append([method, k, silhouette_score(X, labels), np.bincount(labels).min()])
hc_table = pd.DataFrame(rows, columns=["linkage", "k", "silhouette", "smallest cluster"])
hc_table.round(3)
""")
code("""
hier = AgglomerativeClustering(n_clusters=5, linkage="ward").fit(X)
df["hierarchical"] = hier.labels_
print(df["hierarchical"].value_counts().sort_index())
""")

md("## 10. DBSCAN")
code("""
min_samples = 2 * X.shape[1]
nn = NearestNeighbors(n_neighbors=min_samples).fit(X)
k_dist = np.sort(nn.kneighbors(X)[0][:, -1])

line = np.linspace(k_dist[0], k_dist[-1], len(k_dist))
knee = np.argmax(line - k_dist)
print("min_samples:", min_samples, "| knee of k-distance curve at eps =", round(k_dist[knee], 2))

fig, ax = plt.subplots(figsize=(7, 3.6))
ax.plot(k_dist, color=COLOURS[0])
ax.axhline(k_dist[knee], color="red", linestyle="--", label=f"knee ≈ {k_dist[knee]:.2f}")
ax.set_title(f"Sorted {min_samples}-nearest-neighbour distance")
ax.set_xlabel("Points sorted by distance")
ax.set_ylabel("Distance")
ax.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "fig08_kdistance.png", dpi=150)
plt.show()
""")
code("""
rows = []
for eps in [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4]:
    labels = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(X)
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    mask = labels != -1
    sil = silhouette_score(X[mask], labels[mask]) if n_clusters > 1 else np.nan
    sizes = np.bincount(labels[mask]).tolist() if n_clusters > 0 else []
    rows.append([eps, n_clusters, (labels == -1).mean(), sil, sizes])
pd.DataFrame(rows, columns=["eps", "clusters", "noise share", "silhouette (no noise)", "cluster sizes"]).round(3)
""")
code("""
dbscan = DBSCAN(eps=1.2, min_samples=min_samples).fit(X)
df["dbscan"] = dbscan.labels_
print(df["dbscan"].value_counts().sort_index())
""")

md("## 11. Comparing the three models")
code("""
def scores(name, labels):
    mask = labels != -1
    n_clusters = len(set(labels[mask]))
    return {"model": name,
            "clusters": n_clusters,
            "noise %": round(100 * (~mask).mean(), 1),
            "silhouette": silhouette_score(X[mask], labels[mask]),
            "davies_bouldin": davies_bouldin_score(X[mask], labels[mask]),
            "calinski_harabasz": calinski_harabasz_score(X[mask], labels[mask]),
            "largest cluster %": round(100 * np.bincount(labels[mask]).max() / mask.sum(), 1)}

comparison = pd.DataFrame([scores("K-Means (k=5)", df["kmeans"].values),
                           scores("Hierarchical Ward (k=5)", df["hierarchical"].values),
                           scores("DBSCAN (eps=1.2)", df["dbscan"].values)])
comparison.round(3)
""")
code("""
print("ARI K-Means vs Hierarchical:", round(adjusted_rand_score(df["kmeans"], df["hierarchical"]), 3))
print("ARI K-Means vs DBSCAN:", round(adjusted_rand_score(df["kmeans"], df["dbscan"]), 3))
print("ARI Hierarchical vs DBSCAN:", round(adjusted_rand_score(df["hierarchical"], df["dbscan"]), 3))
""")
code("""
fig, axes = plt.subplots(1, 3, figsize=(16, 4.6), sharex=True, sharey=True)
for ax, col, title in zip(axes, ["kmeans", "hierarchical", "dbscan"],
                          ["K-Means (k=5)", "Hierarchical Ward (k=5)", "DBSCAN (eps=1.2)"]):
    for lab in sorted(df[col].unique()):
        mask = df[col].values == lab
        colour = "#bbbbbb" if lab == -1 else COLOURS[lab]
        name = "noise" if lab == -1 else f"cluster {lab}"
        ax.scatter(X_pca[mask, 0], X_pca[mask, 1], s=10, alpha=0.7, color=colour, label=name)
    ax.set_title(title)
    ax.set_xlabel("PC1")
    ax.legend(fontsize=8, markerscale=1.5)
axes[0].set_ylabel("PC2")
plt.tight_layout()
plt.savefig(FIG_DIR / "fig09_pca_clusters.png", dpi=150)
plt.show()
""")
code("""
sil_values = silhouette_samples(X, df["kmeans"])

fig, ax = plt.subplots(figsize=(7, 4.2))
y_low = 10
for lab in range(5):
    vals = np.sort(sil_values[df["kmeans"] == lab])
    ax.fill_betweenx(np.arange(y_low, y_low + len(vals)), 0, vals, color=COLOURS[lab], alpha=0.8)
    ax.text(-0.08, y_low + len(vals) / 2, str(lab))
    y_low += len(vals) + 10
ax.axvline(sil_values.mean(), color="red", linestyle="--", label=f"mean = {sil_values.mean():.3f}")
ax.set_title("Silhouette plot for K-Means (k=5)")
ax.set_xlabel("Silhouette coefficient")
ax.set_yticks([])
ax.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "fig10_silhouette_kmeans.png", dpi=150)
plt.show()

pd.Series(sil_values).groupby(df["kmeans"]).agg(["mean", "min", lambda s: (s < 0).mean()]).round(3)
""")

md("## 12. Profiling the K-Means clusters")
code("""
df["revenue"] = df["price"] * df["sold"]

profile = df.groupby("kmeans").agg(listings=("price", "size"),
                                   median_price=("price", "median"),
                                   median_sold=("sold", "median"),
                                   median_available=("available", "median"),
                                   median_days_since_update=("days_since_update", "median"),
                                   median_size_ml=("size_ml", "median"),
                                   ships_from_us=("ships_from_us", "mean"),
                                   revenue=("revenue", "sum"))
profile["listing share %"] = 100 * profile["listings"] / len(df)
profile["revenue share %"] = 100 * profile["revenue"] / profile["revenue"].sum()
profile.round(2).T
""")
code("""
pd.crosstab(df["kmeans"], df["category"], normalize="index").mul(100).round(1)
""")
code("""
for lab in range(5):
    top = df.loc[df["kmeans"] == lab, "brand"].value_counts().head(4)
    print(lab, ", ".join(f"{b} ({n})" for b, n in top.items()))
""")
code("""
z = pd.DataFrame(X, columns=num_cols).groupby(df["kmeans"]).mean()

fig, ax = plt.subplots(figsize=(7.5, 3.8))
sns.heatmap(z, annot=profile[["median_price", "median_sold", "median_available",
                               "median_days_since_update", "median_size_ml"]].round(1).values,
            fmt="", cmap="RdBu_r", center=0, ax=ax, cbar_kws={"label": "mean z-score"})
ax.set_title("Cluster profiles (colour = z-score, number = median)")
ax.set_ylabel("K-Means cluster")
plt.tight_layout()
plt.savefig(FIG_DIR / "fig11_cluster_profiles.png", dpi=150)
plt.show()
""")
code("""
segment_names = {0: "SEG0", 1: "SEG1", 2: "SEG2", 3: "SEG3", 4: "SEG4"}
share = profile[["listing share %", "revenue share %"]].rename(index=segment_names)

ax = share.plot(kind="barh", figsize=(8, 3.8), color=[COLOURS[5], COLOURS[0]])
for container in ax.containers:
    ax.bar_label(container, fmt="%.1f%%", fontsize=8, padding=2)
ax.set_xlabel("% of total")
ax.set_ylabel("")
ax.set_title("Share of listings vs share of estimated revenue by segment")
ax.invert_yaxis()
plt.tight_layout()
plt.savefig(FIG_DIR / "fig12_segment_share.png", dpi=150)
plt.show()
""")
code("""
df.to_csv("clustered_products.csv", index=False)
""")


def build(names=None):
    nb = nbf.v4.new_notebook()
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    src = cells
    if names:
        for c in src:
            if c.cell_type == "code" and "segment_names = {" in c.source:
                c.source = c.source.replace('{0: "SEG0", 1: "SEG1", 2: "SEG2", 3: "SEG3", 4: "SEG4"}', names)
    nb.cells = src
    NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}}).execute()
    nbf.write(nb, OUT)
    print("written", OUT)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else None)
