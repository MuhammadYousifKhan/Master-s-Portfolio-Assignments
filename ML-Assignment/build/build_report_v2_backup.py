import re
from pathlib import Path
import nbformat
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
OUT = ROOT / "COM7022_Assignment_Report.docx"
STUDENT_ID = "[YOUR STUDENT ID]"

doc = Document()
sec = doc.sections[0]
sec.left_margin = sec.right_margin = Inches(1)
sec.top_margin = sec.bottom_margin = Inches(0.9)

normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(11)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.1
for name, size in [("Heading 1", 16), ("Heading 2", 13), ("Heading 3", 11.5)]:
    st = doc.styles[name]
    st.font.name = "Calibri"
    st.font.size = Pt(size)
    st.font.bold = True
    st.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")

counted = []
fig_no = [0]
tab_no = [0]


def para(text, bold_lead=None, count=True, align=None):
    p = doc.add_paragraph()
    if bold_lead:
        r = p.add_run(bold_lead + " ")
        r.bold = True
    p.add_run(text)
    if align:
        p.alignment = align
    if count:
        counted.append((bold_lead + " " if bold_lead else "") + text)
    return p


def bullet(text, bold_lead=None):
    p = doc.add_paragraph(style="List Bullet")
    if bold_lead:
        r = p.add_run(bold_lead + " ")
        r.bold = True
    p.add_run(text)
    counted.append((bold_lead + " " if bold_lead else "") + text)


def figure(file, caption, width=6.2):
    fig_no[0] += 1
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(FIG / file), width=Inches(width))
    p.paragraph_format.keep_with_next = True
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = c.add_run(f"Figure {fig_no[0]}: {caption}")
    r.italic = True
    r.font.size = Pt(9.5)
    return fig_no[0]


def shade(cell, colour):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), colour)
    tcPr.append(shd)


def table(caption, header, rows, widths=None, size=9):
    tab_no[0] += 1
    c = doc.add_paragraph()
    r = c.add_run(f"Table {tab_no[0]}: {caption}")
    r.italic = True
    r.font.size = Pt(9.5)
    c.paragraph_format.keep_with_next = True
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        cell = t.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        run.bold = True
        run.font.size = Pt(size)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shade(cell, "1F3A5F")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            run = cells[i].paragraphs[0].add_run(str(v))
            run.font.size = Pt(size)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Inches(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return tab_no[0]


p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(120)
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Arden University")
r.font.size = Pt(18)
r.bold = True
for text, size, bold in [("Machine Learning (COM7022)", 24, True),
                         ("Assignment Portfolio", 16, False),
                         ("Clustering e-commerce products by characteristics and sales performance", 13, False)]:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.bold = bold
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(70)
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run(f"Student ID: {STUDENT_ID}")
r.font.size = Pt(14)
r.bold = True
doc.add_page_break()

doc.add_heading("Task 1: Practical Project", level=1)

doc.add_heading("1. Data and preparation", level=2)
para("The dataset has 1,000 perfume listings and ten columns: brand, listing title, category, price, price with currency, units available, a stock text field, units sold, last updated time and item location. I found no duplicate rows, but a number of columns had missing values. Units available had the most, with 111 missing (11.1%), followed by the update time with 53 (5.3%) (Figure 1).")
figure("fig01_missing_values.png", "Missing values per column in the raw data", 5.2)
para("Most of the gaps could be fixed using other columns. Five missing prices were taken from the price with currency text. Three prices were in Canadian dollars, so I converted them at an assumed rate of 0.73. Two missing sold counts could be read from the stock text, and I set the other six to zero because I assumed those listings had not sold yet. Listings marked 'Last One' (47 of them) were given an availability of 1. The rest of the missing availability values, mostly 'Limited quantity' listings, and the missing timestamps were filled with the median.")
para("Two new features came from the text columns. Bottle size in millilitres was pulled from the listing title, which worked for 93.7% of listings, and the median was used for the rest (ounces were converted at 29.57 ml). The update time became days since update, counted back from the newest timestamp in the file (24 May 2024). The category column had 63 different labels, many of them just spelling variants, so I grouped them into four: Eau de Toilette (463 listings), Eau de Parfum/Parfum (394), Other (73) and Cologne (70).")

doc.add_heading("2. Feature selection and transformation", level=2)
para("I used five numeric features: price, sold, available, days since update and size in ml. These cover cost, sales, stock, how recently a listing was updated and bottle size, which is what the brief means by product characteristics and sales performance. Brand and location were left out as inputs. They have 246 and 276 distinct values, and one-hot encoding that many levels would create a lot of sparse columns that would dominate the distance calculations.")
para("I did test category as a one-hot encoded input. The clusters that came out matched the four category groups exactly. The silhouette of 0.355 was higher, but only because dummy variables are easy to separate, and it told me nothing about sales. For that reason category, brand and country were only used afterwards to describe the clusters.")
para("The numeric features were strongly right-skewed. Skewness was 9.75 for sold, 8.65 for available and 13.31 for days since update. The IQR rule flagged between 54 and 476 listings per feature as outliers. However, these are genuine products, such as best sellers with over 50,000 sales, and deleting them would remove the listings the business cares about most. I used log(1 + x) instead, which reduced skewness to 0.11 for price and 0.50 for sold (Figure 2). Size was still negatively skewed (-2.79) because of the small sample bottles. The highest correlation between any two features was 0.44 (sold and available), so I kept all five.")
figure("fig03_distributions_raw_vs_log.png", "Feature distributions before (top) and after (bottom) the log transformation", 6.4)
para("I compared three scalers using K-Means with k = 5. StandardScaler gave a silhouette of 0.255, MinMaxScaler 0.267 and RobustScaler 0.802. The RobustScaler score is misleading. Most bottles are 100 ml, so the interquartile range of size is very small and the scaled size column ended up with a standard deviation of 159. One feature was then deciding almost all of the distances. I used StandardScaler because it gives every feature the same spread.")

doc.add_heading("3. Dimensionality reduction", level=2)
para("PCA on the standardised features showed that two components explain 59.7% of the variance and three explain 77.8% (Figure 3). PC1 is mostly sold (0.67) and available (0.65), so it measures sales volume and stock. PC2 is mostly size (0.67) and price (0.61). Two components lose a lot of information, so I only used PCA for plotting and fitted the models on all five scaled features.")
figure("fig05_pca_variance.png", "Variance explained by each principal component", 4.6)

doc.add_heading("4. Clustering models", level=2)
para("I ran K-Means with k-means++ initialisation and 20 starts for k from 2 to 10. The silhouette score stayed between 0.246 and 0.255 for k = 3 to 6 and was highest at k = 5, and the elbow curve bends somewhere between 4 and 6 (Figure 4). Davies-Bouldin and Calinski-Harabasz were slightly better at k = 6 (1.155 and 326.7 compared with 1.210 and 320.7). I still chose k = 5 because of the higher silhouette, and because k = 6 only splits the large slow-selling group into a premium part (median price 80) and a budget part (27). I also reran K-Means from single random starts. The mean adjusted Rand index against my chosen solution was 0.90, but the lowest was 0.41, so some starts reach a different local optimum. Using 20 starts reduces this problem.", "K-Means.")
figure("fig06_kmeans_elbow_silhouette.png", "Elbow curve and silhouette score for K-Means", 6.2)
para("I applied Ward linkage to the same scaled data and cut the dendrogram at five clusters (Figure 5). Average linkage gave a cluster with only one listing and complete linkage at k = 6 gave one with three, so Ward was the only option with usable cluster sizes (smallest 70).", "Hierarchical clustering.")
figure("fig07_dendrogram.png", "Ward dendrogram, truncated to the last 30 merges", 6.0)
para("I set min_samples to 10, which is twice the number of features, and the k-distance curve bends at an eps of about 1.38 (Figure 6). I tried eps from 0.8 to 1.4. Values of 1.0, 1.3 and 1.4 gave a single cluster, whereas 1.2 gave three clusters with 6.1% of listings marked as noise. Even so, 898 of the 939 clustered listings (95.6%) ended up in one cluster.", "DBSCAN.")
figure("fig08_kdistance.png", "Sorted 10-nearest-neighbour distances used to choose eps", 4.8)

doc.add_heading("5. Evaluation and model choice", level=2)
para("I used silhouette, Davies-Bouldin and Calinski-Harabasz as internal validation measures (Rousseeuw, 1987; Davies and Bouldin, 1979). Noise points were removed before scoring DBSCAN. The results are in Table 1.")
table("Validation results for the three clustering models",
      ["Model", "Clusters", "Noise %", "Silhouette", "Davies-Bouldin", "Calinski-Harabasz", "Largest cluster %"],
      [["K-Means (k = 5)", 5, "0.0", "0.255", "1.210", "320.7", "38.2"],
       ["Hierarchical Ward (k = 5)", 5, "0.0", "0.205", "1.336", "267.4", "40.2"],
       ["DBSCAN (eps = 1.2)", 3, "6.1", "0.269", "0.981", "84.2", "95.6"]],
      [1.8, 0.7, 0.65, 0.8, 0.95, 0.95, 0.85], 8.5)
para("K-Means did better than Ward on all three measures, and the two models only partly agreed on cluster membership (adjusted Rand index 0.52). DBSCAN has the best silhouette and Davies-Bouldin scores, but this is because it separates a few small dense groups and ignores the noise, which leaves one cluster with 95.6% of the data. It also agreed with K-Means barely more than chance (0.11). The K-Means silhouette of 0.255 shows weak structure. That is not surprising for listing data that changes gradually, so I treat the clusters as useful groupings and not as natural categories.")
figure("fig09_pca_clusters.png", "Clusters from the three models projected onto the first two principal components", 6.5)
para("I chose K-Means as the final model. It scored best of the two models that assign every listing to a cluster, the cluster sizes are reasonably balanced, the result was stable across restarts and each cluster has a clear business meaning. Cluster 3 is the weakest, with 11.8% of its listings having a negative silhouette value (silhouette plot in the notebook).")

doc.add_heading("6. Cluster characteristics", level=2)
para("Table 2 shows the median profile of each K-Means cluster. Revenue is estimated as price multiplied by units sold. This assumes the sold count is a lifetime total, so it shows relative importance and not real turnover.")
table("Profile of the five K-Means clusters (medians)",
      ["Cluster", "Listings", "Price ($)", "Sold", "Available", "Days since update", "Size (ml)", "Revenue share"],
      [["0 Premium slow movers", 382, "49.99", 16, 5, "1.6", "100", "3.6%"],
       ["1 Core best sellers", 273, "32.98", 400, 10, "0.6", "101", "78.1%"],
       ["2 Minis and samples", 71, "15.95", 32, 8, "3.8", "2.5", "1.1%"],
       ["3 Stale listings", 195, "31.95", 31, 10, "15.8", "100", "2.8%"],
       ["4 High-stock volume lines", 79, "25.81", 993, 84, "1.1", "101", "14.5%"]],
      [1.75, 0.6, 0.65, 0.5, 0.65, 0.8, 0.6, 0.75], 8.5)
figure("fig11_cluster_profiles.png", "Cluster profiles: colour shows the mean z-score, numbers show the median", 5.4)
bullet("The biggest cluster. Median price is $49.99 with little stock and few sales. It has the highest share of Eau de Parfum and Parfum of the full-size groups.", "Premium slow movers (38.2%).")
bullet("Medium price and around 400 sales per listing, and recently updated. This cluster has 27.3% of listings but an estimated 78% of revenue.", "Core best sellers.")
bullet("Bottles of about 2.5 ml with a median price of $16. Two thirds are parfum, so these look like testers and samples and not full products.", "Minis and samples.")
bullet("Normal price and stock but a median of 15.8 days since the last update, compared with under 4 days in every other cluster. Sales are low.", "Stale listings.")
bullet("Very high stock (median 84 units) and nearly 1,000 sales per listing at a low price. They are only 7.9% of listings but about 14.5% of revenue.", "High-stock volume lines.")

doc.add_page_break()
doc.add_heading("Task 2: Critical Report for Executives", level=1)

doc.add_heading("Summary", level=2)
para("I grouped 1,000 fragrance listings into five segments using price, sales, stock, listing age and bottle size. The core best sellers are 27% of listings but an estimated 78% of revenue, and a further 20% of listings have not been updated for over two weeks and sell poorly. The segments help show where to focus effort. They do overlap, though, so they should be used as a working guide and not as exact categories.")

doc.add_heading("How suitable were the methods?", level=2)
para("There is no labelled outcome to predict, so clustering was the right type of method. The choice of inputs mattered as much as the algorithm. Brand and location have hundreds of values and would have swamped the result. Category made the clusters just repeat product type instead of showing sales behaviour. I therefore used these only to describe the segments. Sales and stock were heavily skewed, with some listings selling over 50,000 units. Deleting them would have removed the best products, so I log-transformed and standardised the data to stop any one measure dominating.")
para("K-Means suits this problem because every listing needs a segment and it gives groups of a manageable size. Its weakness is that it assumes fairly round groups and the number of clusters has to be chosen. Hierarchical clustering does not need that choice in advance and the dendrogram is useful, but it scored lower here and becomes slow on larger datasets. DBSCAN is good at finding unusual listings, but this data has no clear gaps between groups, so it put most listings into one cluster.")

doc.add_heading("Model comparison and final choice", level=2)
para("Table 1 shows that K-Means scored better than hierarchical clustering on all three measures. DBSCAN had the highest silhouette but put 95.6% of listings in one group, which gives nothing to act on. I therefore chose K-Means for technical reasons (best scores among the models that cover all listings, stable across restarts) and business reasons (five segments of reasonable size that each mean something different). The silhouette of 0.255 only shows weak separation, so decisions should rely on the segment profiles and not on listings near a boundary. A six-cluster solution scored slightly better on two measures and is a fair alternative if the premium group needs splitting by price.")

doc.add_heading("Key findings", level=2)
figure("fig12_segment_share.png", "Share of listings and share of estimated revenue by segment", 5.8)
bullet("Core best sellers and high-stock volume lines together are 35% of listings and about 93% of estimated revenue.")
bullet("The largest group (38% of listings) has higher prices, little stock and few sales, and brings in under 4% of revenue.")
bullet("The 195 stale listings were last updated about two weeks before the rest. The data cannot show whether the lack of updates causes the weak sales or follows from them.")
bullet("About 7% of listings are 2.5 ml samples. They behave very differently from full products and would distort averages if left mixed in.")

doc.add_heading("Recommendations", level=2)
bullet("Keep stock levels and pricing steady for the core best sellers and high-stock lines, since they carry most of the revenue.")
bullet("Review the 195 stale listings in the next update cycle. Refresh the title, photos and price, or remove the ones that do not sell, and check whether sales change.")
bullet("Trial price cuts or bundles on a small sample of premium slow movers before applying them to the whole segment, because the high prices may be intentional.")
bullet("Report samples separately from full-size products in sales dashboards.")
bullet("Rerun the model each month on new data and see whether listings move between segments.")

doc.add_heading("Limitations and next steps", level=2)
para("The data is one snapshot from May 2024, so seasonality and trends cannot be seen. Revenue is estimated from price and a lifetime sold count and not from actual sales dates. Missing values were filled with medians and some zero sold counts are assumptions. In future I would add sale dates, brand tier and customer ratings, and try Gaussian mixture models, which give each listing a probability of belonging to a segment and cope better with overlapping groups.")

counted_words = sum(len(re.findall(r"\b[\w'’$%.,-]+\b", t)) for t in counted)

doc.add_page_break()
doc.add_heading("References", level=1)
refs = [
    "Davies, D.L. and Bouldin, D.W. (1979) 'A cluster separation measure', IEEE Transactions on Pattern Analysis and Machine Intelligence, PAMI-1(2), pp. 224-227.",
    "Ester, M., Kriegel, H.-P., Sander, J. and Xu, X. (1996) 'A density-based algorithm for discovering clusters in large spatial databases with noise', Proceedings of the Second International Conference on Knowledge Discovery and Data Mining, pp. 226-231.",
    "Hastie, T., Tibshirani, R. and Friedman, J. (2009) The Elements of Statistical Learning. 2nd edn. New York: Springer.",
    "Jolliffe, I.T. (2002) Principal Component Analysis. 2nd edn. New York: Springer.",
    "Pedregosa, F. et al. (2011) 'Scikit-learn: machine learning in Python', Journal of Machine Learning Research, 12, pp. 2825-2830.",
    "Rousseeuw, P.J. (1987) 'Silhouettes: a graphical aid to the interpretation and validation of cluster analysis', Journal of Computational and Applied Mathematics, 20, pp. 53-65.",
    "Ward, J.H. (1963) 'Hierarchical grouping to optimize an objective function', Journal of the American Statistical Association, 58(301), pp. 236-244.",
]
for ref in refs:
    para(ref, count=False)

doc.add_page_break()
doc.add_heading("Appendix: Python code", level=1)
nb = nbformat.read(ROOT / "COM7022_Task1_Clustering.ipynb", 4)
for i, cell in enumerate(nb.cells):
    if cell.cell_type == "markdown" and cell.source.startswith("## "):
        h = doc.add_paragraph()
        r = h.add_run(cell.source.split("\n")[0].replace("## ", ""))
        r.bold = True
        r.font.size = Pt(10)
        h.paragraph_format.space_before = Pt(8)
        h.paragraph_format.keep_with_next = True
    elif cell.cell_type == "code":
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(cell.source)
        r.font.name = "Consolas"
        r.font.size = Pt(7.5)
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")

doc.save(OUT)
print("saved", OUT)
print("counted words (Task 1 + Task 2 body text, excluding captions, tables, references, appendix):", counted_words)
