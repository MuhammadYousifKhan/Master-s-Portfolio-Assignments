from pathlib import Path
from collections import OrderedDict
import nbformat
from PIL import Image
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
ASSET = Path(__file__).resolve().parent / "assets"
OUT = ROOT / "COM7022_Assignment_Report_v3.docx"

BLUE = RGBColor(0x2E, 0x6F, 0xB5)
NAVY = RGBColor(0x1F, 0x3A, 0x5F)
SERIF = "Times New Roman"

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
sec.left_margin = sec.right_margin = Inches(1)
sec.top_margin = Inches(1.1)
sec.bottom_margin = Inches(0.9)
sec.header_distance = Inches(0.3)

normal = doc.styles["Normal"]
normal.font.name = SERIF
normal.font.size = Pt(11)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), SERIF)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.15
for name, size, colour in [("Heading 1", 16, RGBColor(0, 0, 0)), ("Heading 2", 13, BLUE), ("Heading 3", 11, BLUE)]:
    st = doc.styles[name]
    st.font.name = SERIF
    st.font.size = Pt(size)
    st.font.bold = True
    st.font.italic = False
    st.font.color.rgb = colour
    st.element.rPr.rFonts.set(qn("w:eastAsia"), SERIF)
    st.element.rPr.rFonts.set(qn("w:ascii"), SERIF)
    st.element.rPr.rFonts.set(qn("w:hAnsi"), SERIF)
    st.paragraph_format.space_before = Pt(12 if name != "Heading 3" else 8)
    st.paragraph_format.space_after = Pt(4)
    st.paragraph_format.keep_with_next = True

counted = []
state = {"section": "front", "fig": 0, "tab": 0}


def add_field(run, instr):
    for kind in ("begin", None, "separate", "text", "end"):
        if kind is None:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = instr
        elif kind == "text":
            el = OxmlElement("w:t")
            el.text = "1"
        else:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), kind)
        run._r.append(el)


hp = sec.header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
hp.add_run().add_picture(str(ASSET / "logo.png"), width=Inches(0.8))
fp = sec.footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = fp.add_run()
add_field(r, "PAGE")
fp.add_run(" | P a g e").font.color.rgb = RGBColor(0x59, 0x59, 0x59)


def para(text, lead=None, count=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY, italic=False):
    p = doc.add_paragraph()
    p.alignment = align
    if lead:
        p.add_run(lead + " ").bold = True
    run = p.add_run(text)
    run.italic = italic
    if count:
        counted.append((state["section"], (lead + " " if lead else "") + text))
    return p


def bullet(text, lead=None):
    p = doc.add_paragraph(style="List Bullet")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if lead:
        p.add_run(lead + " ").bold = True
    p.add_run(text)
    counted.append((state["section"], (lead + " " if lead else "") + text))


def numbered(text, lead):
    p = doc.add_paragraph(style="List Number")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run(lead + " ").bold = True
    p.add_run(text)
    counted.append((state["section"], lead + " " + text))


def h1(text):
    state["section"] = text
    doc.add_heading(text, level=1)


def h2(text):
    doc.add_heading(text, level=2)


def h3(text):
    doc.add_heading(text, level=3)


def centred_picture(path, width):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(path), width=Inches(width))
    return p


def figure(file, caption, width=6.0):
    state["fig"] += 1
    centred_picture(FIG / file, width)
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = c.add_run(f"Figure {state['fig']}: {caption}")
    r.font.size = Pt(10)
    return state["fig"]


def shade(cell, colour):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), colour)
    tcPr.append(shd)


def shot_width(path, cap):
    w, _ = Image.open(path).size
    return min(cap, w / 190)


def label_par(cell, text, first=False):
    p = cell.paragraphs[0] if first else cell.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    p.add_run(text).bold = True
    return p


def shots(*cells, show_out=True):
    t = doc.add_table(rows=1, cols=1)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = t.rows[0].cells[0]
    first = True
    for idx in cells:
        code = ASSET / f"code_{idx:02d}.png"
        out = ASSET / f"out_{idx:02d}.png"
        label_par(cell, "Code", first)
        first = False
        p = cell.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(4)
        p.add_run().add_picture(str(code), width=Inches(shot_width(code, 5.9)))
        if show_out and out.exists():
            label_par(cell, "Output")
            p = cell.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(4)
            p.add_run().add_picture(str(out), width=Inches(shot_width(out, 5.9)))
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def output_only(idx):
    t = doc.add_table(rows=1, cols=1)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = t.rows[0].cells[0]
    out = ASSET / f"out_{idx:02d}.png"
    label_par(cell, "Output", True)
    p = cell.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(out), width=Inches(shot_width(out, 5.9)))
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def side_by_side(titles, cells, descs):
    t = doc.add_table(rows=4, cols=len(cells))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    w = 6.4 / len(cells)
    for i, (title, idx, desc) in enumerate(zip(titles, cells, descs)):
        c0 = t.rows[0].cells[i]
        c0.paragraphs[0].add_run(title).bold = True
        shade(c0, "DCE6F2")
        c1 = t.rows[1].cells[i]
        label_par(c1, "Code", True)
        c1.add_paragraph().add_run().add_picture(str(ASSET / f"code_{idx:02d}.png"), width=Inches(w - 0.2))
        c2 = t.rows[2].cells[i]
        label_par(c2, "Output", True)
        c2.add_paragraph().add_run().add_picture(str(ASSET / f"out_{idx:02d}.png"), width=Inches(min(w - 0.2, shot_width(ASSET / f'out_{idx:02d}.png', 5))))
        c3 = t.rows[3].cells[i]
        c3.paragraphs[0].add_run(desc).font.size = Pt(9.5)
        counted.append((state["section"], desc))
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def table(caption, header, rows, widths=None, size=9):
    state["tab"] += 1
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.add_run(f"Table {state['tab']}: {caption}").font.size = Pt(10)
    c.paragraph_format.keep_with_next = True
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        cell = t.rows[0].cells[i]
        run = cell.paragraphs[0].add_run(h)
        run.bold = True
        run.font.size = Pt(size)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shade(cell, "1F3A5F")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].paragraphs[0].add_run(str(v)).font.size = Pt(size)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Inches(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def cover():
    fields = [("Awarding Body:", "Arden University"),
              ("Programme Name:", "[                    ]"),
              ("Module Name (and Part if applicable):", "Machine Learning (COM7022)"),
              ("Assessment Title:", "Machine Learning Portfolio"),
              ("Student Number:", "[                    ]"),
              ("Tutor Name:", "[                    ]"),
              ("Word Count:", "3000")]
    doc.add_paragraph().paragraph_format.space_after = Pt(30)
    t = doc.add_table(rows=len(fields), cols=1)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for row, (label, value) in zip(t.rows, fields):
        c = row.cells[0]
        p = c.paragraphs[0]
        r = p.add_run(label)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(13)
        p.paragraph_format.space_after = Pt(8)
        p2 = c.add_paragraph()
        r2 = p2.add_run(value)
        r2.font.size = Pt(12)
        p2.paragraph_format.space_after = Pt(6)
    p = doc.add_paragraph()
    r = p.add_run("Please refer to the Word Count Policy on your Module Page for guidance")
    r.font.size = Pt(8)
    r.font.name = "Calibri"
    doc.add_page_break()


def toc():
    p = doc.add_paragraph()
    r = p.add_run("Table of Contents")
    r.bold = True
    r.font.size = Pt(16)
    p = doc.add_paragraph()
    run = p.add_run()
    b = OxmlElement("w:fldChar")
    b.set(qn("w:fldCharType"), "begin")
    ins = OxmlElement("w:instrText")
    ins.set(qn("xml:space"), "preserve")
    ins.text = r'TOC \o "1-2" \h \z \u'
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    txt = OxmlElement("w:t")
    txt.text = "Right-click here and choose Update Field to show the contents."
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    for el in (b, ins, sep, txt, end):
        run._r.append(el)
    upd = OxmlElement("w:updateFields")
    upd.set(qn("w:val"), "true")
    doc.settings.element.append(upd)
    doc.add_page_break()


cover()
toc()

h1("1. Introduction")
para("Online marketplaces hold thousands of product listings, and every listing carries a price, a stock level and a sales history. A retailer who wants to manage that range needs a way of grouping similar products so that effort goes where it matters. This report uses clustering on a dataset of 1,000 perfume listings to find those groups from their characteristics and sales performance.")
para("The work follows the two tasks in the brief. Task 1 is the practical project and is covered in sections 2 to 4. It prepares the data, selects and justifies features, applies K-Means, hierarchical clustering and DBSCAN, and compares them with validation measures. Task 2 is the critical report for an executive audience and is covered in sections 5 to 7. It judges how suitable the methods were, justifies the final model and gives recommendations that a non-technical reader can act on.")
para("Each listing in the dataset has a brand, title, category, price, stock figure, units sold, last update time and item location. All of the analysis was done in Python using pandas, SciPy and scikit-learn (Pedregosa et al., 2011). Every step below shows the code and its output, and the full notebook code is in the appendix.")

h1("2. Methodology")
h2("2.1 Data Collection and Overview")
h3("Importing Required Libraries")
shots(2, show_out=False)
para("I started by importing the libraries for data handling (pandas and NumPy), plotting (matplotlib and seaborn), hierarchical linkage (SciPy) and clustering with validation measures (scikit-learn). A random seed of 42 is fixed so that every result can be repeated.")
h3("Loading the Dataset")
shots(4)
para("The file was read with the utf-8-sig encoding because it starts with a byte order mark. It has 1,000 rows and ten columns. Seven are text and only price, available and sold are numeric, so a lot of the useful information is hidden inside the text columns.")
h3("Data Types and Summary Statistics")
shots(5, 6)
para("The info() output confirms that there are no duplicate rows, so nothing had to be removed. The summary statistics already show strong skew. Price has a median of 35.71 but a maximum of 259.09, and sold has a median of 49.5 but a maximum of 54,052. I come back to this in section 2.4.")

h2("2.2 Exploratory Data Analysis (EDA)")
h3("Missing Value Analysis")
fig = figure("fig01_missing_values.png", "Missing values per column in the raw data", 5.0)
para("Figure 1 shows the missing values in each column. Units available has 111 missing (11.1%) and the update time has 53 (5.3%). The other columns have fewer than ten each. The missing availability is not random. Most of it comes from listings whose stock text says 'Limited quantity' or 'Last One', which means the seller gave a description instead of a number. For that reason I repaired the gaps from related columns where possible and did not simply delete rows.")
h3("Text Fields")
shots(9)
para("The stock text follows a few clear patterns, such as 'N available / N sold', 'More than N available / N sold', 'Limited quantity available / N sold' and 'Last One / N sold'. The price text shows that 996 prices are in US dollars and three are in Canadian dollars. The category column has 63 different labels, so it needed cleaning before it could be used.")

h2("2.3 Data Preprocessing and Cleaning")
h3("Repairing and Creating Columns")
shots(11)
para("Most gaps could be fixed from other columns. Five missing prices were taken from the price with currency text. Three prices were in Canadian dollars, so I converted them at an assumed rate of 0.73. Two missing sold counts could be read from the stock text, and I set the other six to zero because I assumed those listings had not sold yet. The 47 'Last One' listings were given an availability of 1, and the remaining missing availability values and timestamps were filled with the median.")
para("Two new features came from the text. Bottle size in millilitres was pulled from the listing title, which worked for 93.7% of listings, with the median used for the rest and ounces converted at 29.57 ml. The update time became days since update, counted back from the newest timestamp in the file (24 May 2024). After this step none of the model columns had missing values.")
h3("Grouping the Category Labels")
shots(13)
fig = figure("fig02_categories_locations.png", "Listings by grouped category and by item location", 6.0)
para("Many of the 63 category labels were spelling variants, such as 'Eau de Parfum' and 'Eau De Parfum', so I grouped them with simple text rules into four: Eau de Toilette (463 listings), Eau de Parfum/Parfum (394), Other (73) and Cologne (70). Figure 2 also shows that 912 of the 1,000 listings ship from the United States, so location has very little variation.")

h2("2.4 Feature Engineering and Selection")
h3("Feature Selection")
para("I used five numeric features: price, sold, available, days since update and size in ml. These cover cost, sales, stock, how recently a listing was updated and bottle size, which is what the brief means by product characteristics and sales performance. Brand and location were left out as inputs. They have 246 and 276 distinct values, and one-hot encoding that many levels would create sparse columns that dominate the distance calculations.")
h3("Testing the Category Variable")
shots(20)
para("I did test category as a one-hot encoded input. The clusters matched the four category groups exactly. The silhouette of 0.355 was higher, but only because dummy variables are easy to separate, and it said nothing about sales. For that reason category, brand and country were only used afterwards to describe the clusters.")
h3("Outliers and Skewness")
shots(15)
figure("fig03_distributions_raw_vs_log.png", "Feature distributions before (top) and after (bottom) the log transformation", 6.4)
para("The numeric features were very right-skewed. Sold had a skewness of 9.75, available 8.65 and days since update 13.31. The IQR rule flagged between 54 and 476 listings per feature as outliers. However, these are real products. Some best sellers have over 50,000 sales, and deleting them would throw away the listings the business cares about most. I used log(1 + x) instead, which reduced skewness to 0.11 for price and 0.50 for sold (Figure 3). Size was still negatively skewed (-2.79) because of the small sample bottles.")
h3("Correlation")
figure("fig04_correlation.png", "Correlation matrix of the log-transformed features", 4.2)
para("The highest correlation between any two features is 0.44 (sold and available), and price with size is 0.35 (Figure 4). The features are related but not redundant, so I kept all five.")
h3("Scaling and Normalisation")
shots(22, 23)
para("K-Means, Ward linkage and DBSCAN all use distances, so features on larger scales would dominate. I compared three scalers with K-Means at k = 5. StandardScaler gave a silhouette of 0.255, MinMaxScaler 0.267 and RobustScaler 0.802. The RobustScaler score is misleading. Most bottles are 100 ml, so the interquartile range of size is very small and the scaled size column ended up with a standard deviation of 159. One feature was then deciding almost all of the distances. I used StandardScaler because it gives every feature the same spread.")

h2("2.5 Dimensionality Reduction with PCA")
shots(25)
figure("fig05_pca_variance.png", "Variance explained by each principal component", 4.6)
para("PCA on the standardised features shows that two components explain 59.7% of the variance and three explain 77.8% (Figure 5; Jolliffe, 2002). PC1 is mostly sold (0.67) and available (0.65), so it measures sales volume and stock. PC2 is mostly size (0.67) and price (0.61). Two components lose a lot of information, so I used PCA only for plotting and fitted the models on all five scaled features.")

h1("3. Model Development")
h2("3.1 Choosing the Number of Clusters")
shots(28)
figure("fig06_kmeans_elbow_silhouette.png", "Elbow curve and silhouette score for K-Means", 6.0)
para("I ran K-Means with k-means++ initialisation (Arthur and Vassilvitskii, 2007) and 20 starts for k from 2 to 10. The silhouette score stayed between 0.246 and 0.255 for k = 3 to 6 and was highest at k = 5, and the elbow curve bends somewhere between 4 and 6 (Figure 6). Davies-Bouldin and Calinski-Harabasz were slightly better at k = 6 (1.155 and 326.7 compared with 1.210 and 320.7). I stayed with k = 5. It had the highest silhouette, and at k = 6 the only real change was that the big slow-selling group split into a premium part (median price 80) and a budget part (27). That seemed a small gain for an extra cluster.")
shots(30)
para("I also reran K-Means from single random starts and compared each with my chosen solution using the adjusted Rand index. At k = 5 the mean was 0.90, but the lowest was 0.41, so some starts reach a different local optimum. Using 20 starts reduces this problem.")

h2("3.2 Model Selection and Training")
para("Three models were selected to represent different ideas of what a cluster is. K-Means builds round groups around centres. Hierarchical clustering with Ward linkage merges listings step by step (Ward, 1963). DBSCAN finds dense regions and labels everything else as noise (Ester et al., 1996). The final fits are shown side by side below, and the tuning behind each one follows.")
side_by_side(["K-Means (k = 5)", "Hierarchical (Ward, k = 5)", "DBSCAN (eps = 1.2)"], [31, 35, 39],
             ["Centre-based groups, with all 1,000 listings assigned. Sizes range from 71 to 382.",
              "Merges the closest listings step by step. Sizes range from 70 to 402.",
              "Marks 61 listings (6.1%) as noise and puts 898 of the rest in one cluster."])
h3("Hierarchical Clustering")
figure("fig07_dendrogram.png", "Ward dendrogram, truncated to the last 30 merges", 6.0)
shots(34)
para("I applied Ward linkage to the scaled data and cut the dendrogram at five clusters (Figure 7). Average linkage gave a cluster with only one listing and complete linkage at k = 6 gave one with three, so Ward was the only option with usable cluster sizes (smallest 70).")
h3("DBSCAN")
shots(37)
figure("fig08_kdistance.png", "Sorted 10-nearest-neighbour distances used to choose eps", 4.6)
shots(38)
para("I set min_samples to 10, which is twice the number of features, and the k-distance curve bends at an eps of about 1.38 (Figure 8). I tried eps from 0.8 to 1.4. Values of 1.0, 1.3 and 1.4 gave a single cluster, whereas 1.2 gave three clusters with 6.1% of listings marked as noise. Even so, 898 of the 939 clustered listings (95.6%) ended up in one cluster.")

h2("3.3 Model Evaluation Metrics")
para("Without labels, clusters can only be judged with internal measures. The silhouette score compares how close a listing is to its own cluster with the nearest other cluster, from -1 to 1, and higher is better (Rousseeuw, 1987). The Davies-Bouldin index compares cluster spread with the distance between centres, and lower is better (Davies and Bouldin, 1979). The Calinski-Harabasz index is a ratio of between-cluster to within-cluster variance, and higher is better. The adjusted Rand index shows how far two models agree. Noise points were removed before scoring DBSCAN.")
shots(41, 42)
para("The comparison table is in section 4.3. The adjusted Rand index between K-Means and Ward is 0.52, between K-Means and DBSCAN it is 0.11, and between Ward and DBSCAN it is also 0.11. So the two methods that cover every listing broadly agree, while DBSCAN gives a very different picture.")

h1("4. Results and Analysis")
h2("4.1 Visualisation Analysis")
figure("fig09_pca_clusters.png", "Clusters from the three models projected onto the first two principal components", 6.5)
para("Figure 9 shows the three solutions on the first two principal components. The K-Means clusters sit in fairly distinct regions, with the high-volume group (cluster 4) to the right and the small samples (cluster 2) in a separate patch at the bottom. Ward's groups overlap more. DBSCAN is one large cluster with a few small patches, which matches the 95.6% share.")
shots(44)
figure("fig10_silhouette_kmeans.png", "Silhouette plot for K-Means (k = 5)", 4.8)
para("The silhouette plot in Figure 10 shows that most listings sit just above zero, which is why the average is only 0.255. Cluster 2 (0.369) and cluster 4 (0.334) are the best defined. Cluster 3 is the weakest, with a mean of 0.199 and 11.8% of its listings below zero.")

h2("4.2 Cluster Profiling")
shots(46)
output_only(47)
para("Table 2 gives the median profile of each K-Means cluster. Revenue is estimated as price multiplied by units sold. This assumes the sold count is a lifetime total, so it shows relative importance and not real turnover.")
table("Profile of the five K-Means clusters (medians)",
      ["Cluster", "Listings", "Price ($)", "Sold", "Available", "Days since update", "Size (ml)", "Revenue share"],
      [["0 Premium slow movers", 382, "49.99", 16, 5, "1.6", "100", "3.6%"],
       ["1 Core best sellers", 273, "32.98", 400, 10, "0.6", "101", "78.1%"],
       ["2 Minis and samples", 71, "15.95", 32, 8, "3.8", "2.5", "1.1%"],
       ["3 Stale listings", 195, "31.95", 31, 10, "15.8", "100", "2.8%"],
       ["4 High-stock volume lines", 79, "25.81", 993, 84, "1.1", "101", "14.5%"]],
      [1.75, 0.6, 0.65, 0.5, 0.65, 0.8, 0.6, 0.75], 8.5)
figure("fig11_cluster_profiles.png", "Cluster profiles: colour shows the mean z-score, numbers show the median", 5.2)
bullet("The biggest group, and a fairly quiet one. Median price is $49.99, stock is low and sales are few. Among the full-size clusters it has the most Eau de Parfum and Parfum.", "Premium slow movers (38.2%).")
bullet("Mid-priced listings that sell around 400 units each and are kept up to date. They are 27.3% of listings but make up an estimated 78% of revenue.", "Core best sellers.")
bullet("Tiny bottles of about 2.5 ml at a median of $16. Two thirds are parfum, so I read these as testers and samples rather than normal products.", "Minis and samples.")
bullet("Nothing unusual about price or stock, but the median listing was last updated 15.8 days before the cut-off, while every other cluster is under 4 days. Sales are low.", "Stale listings.")
bullet("Median stock of 84 units and nearly 1,000 sales per listing, at a lower price. There are few of them (7.9% of listings), yet they bring in about 14.5% of revenue.", "High-stock volume lines.")

shots(48)
para("Figure 11 makes the differences easy to see. Cluster 2 is far below average on size, cluster 4 is far above on stock and sales, and cluster 3 stands out on days since update. Brand does not decide which segment a listing lands in. Giorgio Armani is among the four most common brands in three of the five clusters. The minis cluster is the only one led by high-end names (Creed, Yves Saint Laurent and Chanel), which fits the idea that these are testers of designer fragrances.")

h2("4.3 Model Performance Comparison")
table("Validation results for the three clustering models",
      ["Model", "Clusters", "Noise %", "Silhouette", "Davies-Bouldin", "Calinski-Harabasz", "Largest cluster %"],
      [["K-Means (k = 5)", 5, "0.0", "0.255", "1.210", "320.7", "38.2"],
       ["Hierarchical Ward (k = 5)", 5, "0.0", "0.205", "1.336", "267.4", "40.2"],
       ["DBSCAN (eps = 1.2)", 3, "6.1", "0.269", "0.981", "84.2", "95.6"]],
      [1.8, 0.7, 0.65, 0.8, 0.95, 0.95, 0.85], 8.5)
h3("K-Means")
para("K-Means scored best of the two models that place every listing in a cluster, with a silhouette of 0.255 and the highest Calinski-Harabasz value (320.7). Its clusters are similar in size and each has a clear commercial meaning. Its weakness is that it assumes roundish groups and needs k to be chosen.")
h3("Hierarchical Clustering")
para("Ward linkage scored lower on all three measures (0.205, 1.336 and 267.4) and only partly agreed with K-Means on which listings belong together (adjusted Rand index 0.52). Its dendrogram is useful for seeing how groups merge, but it is slow on large datasets.")
h3("DBSCAN")
para("DBSCAN has the best silhouette (0.269) and Davies-Bouldin score (0.981). This is because it separates a few small dense groups and ignores the noise, which leaves one cluster with 95.6% of the data. Its agreement with K-Means was barely above chance (0.11), so it gives almost no segmentation to act on.")

h1("5. Critical Evaluation")
para("Sections 5 to 7 are written for an executive reader and use the results from Task 1.")
h2("5.1 Executive Summary")
para("I split 1,000 fragrance listings into five segments based on price, sales, stock, listing age and bottle size. The main result is that the core best sellers are only 27% of listings but an estimated 78% of revenue. Another 20% of listings have not been updated for over two weeks and sell poorly. The segments overlap, so I would use them as a rough guide to where effort should go, not as exact categories.")
h2("5.2 Suitability of the Methods")
para("There is no labelled outcome to predict here, so clustering was the obvious type of method. What went into it mattered just as much as which algorithm I used (Hastie et al., 2009). Brand and location have hundreds of values and would have swamped the result. Category made the clusters repeat product type instead of showing sales behaviour. Sales and stock were heavily skewed, so I log-transformed and standardised them rather than deleting the best products.")
para("K-Means suits the problem because every listing needs a segment and it gives groups of a manageable size. Hierarchical clustering needs no choice of k in advance, but it scored lower here and becomes slow on larger datasets. DBSCAN is good at finding unusual listings, but this data has no clear gaps between groups, so it put most listings into one cluster.")
h2("5.3 Final Model Justification")
para("I chose K-Means. DBSCAN looked better on paper but was no use for segmenting, and Ward scored lower on every measure, so K-Means was the best of the two models that cover all the listings. The clusters are also a sensible size and I could explain each one in a sentence, which mattered for the business side. It is not perfect. A silhouette of 0.255 means the structure is weak, so decisions should rely on the segment profiles and not on listings near a boundary. A six-cluster solution is a fair alternative if the premium group needs splitting by price.")
h2("5.4 Limitations, Assumptions and Alternatives")
para("The data is a single snapshot from May 2024, so there is no way to see seasonality or trends. Most listings were updated in the last week, so 'stale' means older than the rest of this snapshot. Revenue is estimated from price and a lifetime sold count and not from sales dates.", "Data limitations.")
para("K-Means assumes round clusters of similar size, and all three methods rely on distances, which weakens in more dimensions. The Canadian dollar rate of 0.73 and the zero sold counts are assumptions, and median filling hides some real variation.", "Model assumptions.")
para("Ninety-one percent of the listings ship from the United States, so the results say little about other markets. The sold count favours older listings, which have had longer to sell, and could make newer products look weaker than they are.", "Potential biases.")
para("With more time I would add sale dates, brand tier and customer ratings. I would also try Gaussian mixture models, because they give each listing a probability of belonging to each segment, which suits overlapping groups better.", "Alternative approaches.")

h1("6. Business Recommendations")
figure("fig12_segment_share.png", "Share of listings and share of estimated revenue by segment", 5.6)
para("Core best sellers and high-stock volume lines together are 35% of listings and about 93% of estimated revenue (Figure 12). The largest group (38% of listings) has higher prices, little stock and few sales, and brings in under 4% of revenue. The findings lead to five recommendations, and none of them needs new data, so they could start straight away.")
numbered("Keep stock available and avoid unnecessary price changes for the core best sellers and high-stock lines, since they bring in most of the revenue.", "Look after the winners.")
numbered("Review the 195 stale listings in the next update cycle. Refresh the title, photos and price, or remove the ones that do not sell, and check whether sales change. The data cannot show whether staleness causes weak sales or follows from them.", "Refresh the stale listings.")
numbered("Trial price cuts or bundles on a small sample of premium slow movers before applying them to the whole segment, because the high prices may be intentional.", "Test before discounting.")
numbered("About 7% of listings are 2.5 ml samples. They behave very differently from full products and would distort averages, so report them separately in sales dashboards.", "Separate the samples.")
numbered("Rerun the model every month on new data to see whether listings move between segments.", "Monitor movement.")

h1("7. Conclusion")
para("This project grouped 1,000 perfume listings into five segments with K-Means after cleaning the data, log-transforming and standardising five features, and comparing three clustering methods. K-Means gave the most useful result even though its silhouette of 0.255 shows only weak separation. The most important finding is how concentrated sales are, with about a quarter of listings producing most of the estimated revenue. The recommendations focus on protecting those listings and fixing the stale ones. I would also repeat the analysis on a longer period before relying on the segment sizes. Future work should use dated sales data and test probabilistic models to get stronger and more reliable segments.")

counted_total = sum(len(t.split()) for _, t in counted)

h1("References")
state["section"] = "refs"
refs = [
    "Arthur, D. and Vassilvitskii, S. (2007) 'k-means++: the advantages of careful seeding', Proceedings of the 18th Annual ACM-SIAM Symposium on Discrete Algorithms, pp. 1027-1035.",
    "Davies, D.L. and Bouldin, D.W. (1979) 'A cluster separation measure', IEEE Transactions on Pattern Analysis and Machine Intelligence, PAMI-1(2), pp. 224-227.",
    "Ester, M., Kriegel, H.-P., Sander, J. and Xu, X. (1996) 'A density-based algorithm for discovering clusters in large spatial databases with noise', Proceedings of the Second International Conference on Knowledge Discovery and Data Mining, pp. 226-231.",
    "Hastie, T., Tibshirani, R. and Friedman, J. (2009) The Elements of Statistical Learning. 2nd edn. New York: Springer.",
    "Jolliffe, I.T. (2002) Principal Component Analysis. 2nd edn. New York: Springer.",
    "Pedregosa, F. et al. (2011) 'Scikit-learn: machine learning in Python', Journal of Machine Learning Research, 12, pp. 2825-2830.",
    "Rousseeuw, P.J. (1987) 'Silhouettes: a graphical aid to the interpretation and validation of cluster analysis', Journal of Computational and Applied Mathematics, 20, pp. 53-65.",
    "Ward, J.H. (1963) 'Hierarchical grouping to optimize an objective function', Journal of the American Statistical Association, 58(301), pp. 236-244.",
]
for ref in refs:
    para(ref, count=False, align=WD_ALIGN_PARAGRAPH.LEFT)

doc.add_page_break()
h1("Appendix")
nb = nbformat.read(ROOT / "COM7022_Task1_Clustering.ipynb", 4)
for cell in nb.cells:
    if cell.cell_type == "markdown" and cell.source.startswith("## "):
        h = doc.add_paragraph()
        h.add_run(cell.source.split("\n")[0].replace("## ", "")).bold = True
        h.paragraph_format.space_before = Pt(8)
        h.paragraph_format.keep_with_next = True
    elif cell.cell_type == "code":
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(cell.source)
        r.font.name = "Consolas"
        r.font.size = Pt(8)
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")

doc.save(OUT)
by_sec = OrderedDict()
for s, t in counted:
    by_sec[s] = by_sec.get(s, 0) + len(t.split())
for s, n in by_sec.items():
    print(f"{n:5d}  {s}")
print("TOTAL counted words:", counted_total)
