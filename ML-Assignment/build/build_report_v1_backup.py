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
para("The file holds 1,000 perfume listings with ten columns: brand, listing title, category, price, price with currency, units available, a stock text field, units sold, last updated time and item location. There were no duplicate rows, but several columns had gaps. Units available was the worst with 111 missing values (11.1%), followed by the update time with 53 (5.3%) (Figure 1).")
figure("fig01_missing_values.png", "Missing values per column in the raw data", 5.2)
para("Most gaps could be repaired from other columns. The five missing prices were read from the price with currency text, and three prices in Canadian dollars were converted at an assumed rate of 0.73. Two missing sold counts were taken from the stock text and the other six were set to zero, on the assumption that those listings had not sold yet. The 47 listings marked 'Last One' were given an availability of 1. The remaining missing availability values, mostly 'Limited quantity' listings, and the missing timestamps were filled with the median.")
para("Two features were built from text. Bottle size in millilitres was extracted from the listing title (found for 93.7% of listings, median for the rest, ounces converted at 29.57 ml). The update time was turned into days since update, counted back from the newest timestamp in the file (24 May 2024). The 63 spelling variants in the category column were grouped into four: Eau de Toilette (463 listings), Eau de Parfum/Parfum (394), Other (73) and Cologne (70).")

doc.add_heading("2. Feature selection and transformation", level=2)
para("Five numeric features were chosen: price, sold, available, days since update and size in ml. Together they describe what a product costs, how well it sells, how much stock is held, how recently the listing was touched and what size is on offer. Brand and location were excluded as inputs because they have 246 and 276 distinct values, and one-hot encoding that many levels would let sparse dummy columns dominate the distances.")
para("Category was tested as a one-hot encoded input. The clusters that came out matched the four category groups exactly, and the silhouette of 0.355 only showed that dummy variables are easy to separate. It said nothing about sales performance, so category, brand and country were kept for describing the clusters afterwards instead.")
para("The numeric features were strongly right-skewed. Skewness was 9.75 for sold, 8.65 for available and 13.31 for days since update. The IQR rule flagged between 54 and 476 listings per feature, but these are real products, for example best sellers with over 50,000 sales, and removing them would delete the listings the business cares about most. I applied log(1 + x) instead, which brought skewness down to 0.11 for price and 0.50 for sold (Figure 2). Size stayed negatively skewed (-2.79) because of the small sample bottles. The highest correlation between features was 0.44 (sold and available), so none was dropped.")
figure("fig03_distributions_raw_vs_log.png", "Feature distributions before (top) and after (bottom) the log transformation", 6.4)
para("Three scalers were compared using K-Means with k = 5. StandardScaler gave a silhouette of 0.255, MinMaxScaler 0.267 and RobustScaler 0.802. The RobustScaler figure is misleading. Most bottles are 100 ml, so the interquartile range of size is tiny and the scaled size column reached a standard deviation of 159, which meant one feature decided almost every distance. StandardScaler was used because it gives all five features the same spread.")

doc.add_heading("3. Dimensionality reduction", level=2)
para("PCA on the standardised features showed that two components explain 59.7% of the variance and three explain 77.8% (Figure 3). PC1 is driven by sold (0.67) and available (0.65), so it reflects sales volume and stock. PC2 is driven by size (0.67) and price (0.61). Because a third of the variance is lost with two components, PCA was used only for plotting, and the models were fitted on all five scaled features.")
figure("fig05_pca_variance.png", "Variance explained by each principal component", 4.6)

doc.add_heading("4. Clustering models", level=2)
para("K-Means was run with k-means++ initialisation and 20 starts for k from 2 to 10. The silhouette score stayed between 0.246 and 0.255 for k = 3 to 6 and peaked at k = 5, and the elbow curve bends between 4 and 6 (Figure 4). Davies-Bouldin and Calinski-Harabasz were slightly better at k = 6 (1.155 and 326.7 against 1.210 and 320.7). I chose k = 5 for its higher silhouette and because k = 6 only splits the large slow-selling group into a premium part (median price 80) and a budget part (27). Rerunning K-Means from single random starts gave a mean adjusted Rand index of 0.90 against the chosen solution, but the lowest was 0.41, so a few starts end in a different local optimum. The 20 starts guard against this.", "K-Means.")
figure("fig06_kmeans_elbow_silhouette.png", "Elbow curve and silhouette score for K-Means", 6.2)
para("Ward linkage was applied to the same scaled data and the dendrogram was cut at five clusters (Figure 5). Average linkage produced a cluster with a single listing, and complete linkage at k = 6 produced a cluster of three, so Ward was the only linkage giving usable group sizes (smallest cluster 70).", "Hierarchical clustering.")
figure("fig07_dendrogram.png", "Ward dendrogram, truncated to the last 30 merges", 6.0)
para("min_samples was set to 10, twice the number of features, and the k-distance curve bends at an eps of about 1.38 (Figure 6). I tried eps from 0.8 to 1.4. Values of 1.0, 1.3 and 1.4 produced one cluster only, while 1.2 gave three clusters with 6.1% of listings labelled as noise. Even then 898 of the 939 clustered listings (95.6%) fall in a single cluster.", "DBSCAN.")
figure("fig08_kdistance.png", "Sorted 10-nearest-neighbour distances used to choose eps", 4.8)

doc.add_heading("5. Evaluation and model choice", level=2)
para("Silhouette, Davies-Bouldin and Calinski-Harabasz were used as internal validation measures (Rousseeuw, 1987; Davies and Bouldin, 1979). Noise points were removed before scoring DBSCAN. The results are in Table 1.")
table("Validation results for the three clustering models",
      ["Model", "Clusters", "Noise %", "Silhouette", "Davies-Bouldin", "Calinski-Harabasz", "Largest cluster %"],
      [["K-Means (k = 5)", 5, "0.0", "0.255", "1.210", "320.7", "38.2"],
       ["Hierarchical Ward (k = 5)", 5, "0.0", "0.205", "1.336", "267.4", "40.2"],
       ["DBSCAN (eps = 1.2)", 3, "6.1", "0.269", "0.981", "84.2", "95.6"]],
      [1.8, 0.7, 0.65, 0.8, 0.95, 0.95, 0.85], 8.5)
para("K-Means beat Ward on every measure, and its clusters agreed only moderately with Ward's (adjusted Rand index 0.52). DBSCAN has the best silhouette and Davies-Bouldin scores, but those come from splitting off a few small dense groups and discarding noise, which leaves one cluster holding 95.6% of the data. Its agreement with K-Means was close to chance (0.11). The overall K-Means silhouette of 0.255 indicates weak structure, which is not surprising for listing data that varies continuously, so the clusters should be read as useful groupings and not as natural categories.")
figure("fig09_pca_clusters.png", "Clusters from the three models projected onto the first two principal components", 6.5)
para("K-Means was selected as the final model. It gave the best scores of the two models that cover every listing, the clusters were similar in size and stable across restarts, and each one has a clear commercial meaning. Cluster 3 is the weakest, with 11.8% of its listings having a negative silhouette value (silhouette plot in the notebook).")

doc.add_heading("6. Cluster characteristics", level=2)
para("Table 2 gives the median profile of each K-Means cluster. Revenue is estimated as price multiplied by units sold, which treats the sold count as a lifetime total, so it shows relative importance and not actual turnover.")
table("Profile of the five K-Means clusters (medians)",
      ["Cluster", "Listings", "Price ($)", "Sold", "Available", "Days since update", "Size (ml)", "Revenue share"],
      [["0 Premium slow movers", 382, "49.99", 16, 5, "1.6", "100", "3.6%"],
       ["1 Core best sellers", 273, "32.98", 400, 10, "0.6", "101", "78.1%"],
       ["2 Minis and samples", 71, "15.95", 32, 8, "3.8", "2.5", "1.1%"],
       ["3 Stale listings", 195, "31.95", 31, 10, "15.8", "100", "2.8%"],
       ["4 High-stock volume lines", 79, "25.81", 993, 84, "1.1", "101", "14.5%"]],
      [1.75, 0.6, 0.65, 0.5, 0.65, 0.8, 0.6, 0.75], 8.5)
figure("fig11_cluster_profiles.png", "Cluster profiles: colour shows the mean z-score, numbers show the median", 5.4)
bullet("Higher priced (median $49.99), small stock and few sales. Largest cluster, with the highest share of Eau de Parfum and Parfum among the 100 ml groups.", "Premium slow movers (38.2%).")
bullet("Moderate price and about 400 sales per listing, recently updated. These 27.3% of listings account for an estimated 78% of revenue.", "Core best sellers.")
bullet("Bottles of about 2.5 ml at a median of $16, two thirds of them parfum. They are testers and samples, not full products.", "Minis and samples.")
bullet("Normal price and stock but not updated for a median of 15.8 days, against under 4 days for every other cluster, and low sales.", "Stale listings.")
bullet("Very high stock (median 84 units) and almost 1,000 sales per listing at a low price. Only 7.9% of listings but about 14.5% of revenue.", "High-stock volume lines.")

doc.add_page_break()
doc.add_heading("Task 2: Critical Report for Executives", level=1)

doc.add_heading("Summary", level=2)
para("We grouped 1,000 fragrance listings into five segments using price, sales, stock, listing age and bottle size. One segment, the core best sellers, makes up 27% of listings but an estimated 78% of revenue, while another 20% of listings have not been updated for over two weeks and sell poorly. The grouping is a good guide for where to spend effort, but the segments overlap and should be treated as a working tool and not a precise classification.")

doc.add_heading("How suitable were the methods?", level=2)
para("The business question has no labelled answer, so unsupervised clustering was the right family of methods. The choice of inputs mattered as much as the algorithm. Brand and location have hundreds of values and would have swamped the results, and category made the clusters repeat the product type instead of showing sales behaviour, so these were used only to describe the segments. Sales and stock figures were heavily skewed, with a few listings selling over 50,000 units. Instead of deleting them, which would have removed the best products, the data was log-transformed and standardised so that no single measure dominated.")
para("K-Means suits this problem because every listing needs a segment and it produces groups of manageable size. Its weakness is that it assumes roughly round groups and needs the number of clusters to be chosen. Hierarchical clustering needs no such choice up front and gives a useful dendrogram, but it was less accurate here and cannot easily be rerun on larger datasets. DBSCAN finds unusual listings well, but our data has no clear gaps between groups, so it labelled most listings as one cluster.")

doc.add_heading("Model comparison and final choice", level=2)
para("Table 1 shows K-Means scored better than hierarchical clustering on all three validation measures. DBSCAN had the highest silhouette but placed 95.6% of listings in one group, which gives no segmentation to act on. K-Means was therefore chosen on both technical grounds (best scores among models covering all listings, stable across restarts) and business grounds (five segments of sensible size, each with a distinct commercial meaning). Its silhouette of 0.255 shows only weak separation, so decisions should rest on the segment profiles and not on individual boundary listings. A six-cluster solution scored slightly better on two measures and is a reasonable alternative if the premium group needs splitting by price.")

doc.add_heading("Key findings", level=2)
figure("fig12_segment_share.png", "Share of listings and share of estimated revenue by segment", 5.8)
bullet("Core best sellers and high-stock volume lines together are 35% of listings and about 93% of estimated revenue.", "Sales are concentrated.")
bullet("The largest group of listings (38%) sits at a higher price with few sales and little stock, producing under 4% of revenue.", "Premium lines sell slowly.")
bullet("The 195 stale listings share a clear trait, which is that they were last updated about two weeks earlier than the rest. Whether staleness causes weak sales or follows from them cannot be told from this data.", "Neglected listings.")
bullet("About 7% of listings are 2.5 ml samples. They behave very differently from full products and distort averages if left mixed in.", "Samples need separating.")

doc.add_heading("Recommendations", level=2)
bullet("Protect stock and keep pricing stable for the core best sellers and high-stock lines, since they carry most of the revenue.", "Prioritise the winners.")
bullet("Review the 195 stale listings in the next update cycle, refreshing the title, photos and price or retiring those that do not sell, and track whether sales move.", "Refresh or retire stale listings.")
bullet("Test price reductions or bundles on a sample of the premium slow movers before applying them to the whole segment, because high prices may be deliberate positioning.", "Test before discounting.")
bullet("Report samples separately from full-size products in sales dashboards.", "Separate samples.")
bullet("Rerun the model every month on fresh data and check whether listings move between segments.", "Monitor movement.")

doc.add_heading("Limitations and next steps", level=2)
para("The data is a single snapshot from May 2024, so seasonality and trends are not visible. Revenue is estimated from price and a lifetime sold count, not from actual sales dates. Missing values were filled with medians and some zero sold counts are assumptions. Future work could add sale dates, brand tier and customer ratings, and could test Gaussian mixture models, which give each listing a probability of belonging to a segment and handle overlapping groups better.")

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
