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
para("A retailer selling online can have thousands of listings, each with its own price, stock level and sales record. Managing a range like that is easier when similar products are grouped, because effort can then go to the groups that matter. In this report I apply clustering to 1,000 perfume listings to find such groups from their characteristics and sales performance.")
para("The report follows the two tasks in the brief. Sections 2 to 4 cover Task 1, the practical project. There I prepare the data, choose and justify the features, apply K-Means, hierarchical clustering and DBSCAN, and compare the three with validation measures. Sections 5 to 7 cover Task 2, the critical report for an executive audience. They assess whether the methods suited the problem, justify the final model and set out recommendations that a non-technical reader can act on.")
para("For each listing the dataset records the brand, title, category, price, stock figure, units sold, last update time and item location. I did all of the analysis in Python with pandas, SciPy and scikit-learn (Pedregosa et al., 2011). Each step below shows the code with its output, and the complete notebook code is given in the appendix.")

h1("2. Methodology")
h2("2.1 Data Collection and Overview")
h3("Importing Required Libraries")
shots(2, show_out=False)
para("The first step was to import pandas and NumPy for handling the data, matplotlib and seaborn for the plots, SciPy for hierarchical linkage and scikit-learn for the clustering models and validation measures. I fixed the random seed at 42 so that every result can be reproduced.")
h3("Loading the Dataset")
shots(4)
para("Because the file begins with a byte order mark, I read it with the utf-8-sig encoding. It contains 1,000 rows and ten columns. Only price, available and sold are numeric and the other seven are text, so much of the useful information sits inside text columns.")
h3("Data Types and Summary Statistics")
shots(5, 6)
para("The info() output shows no duplicate rows, so no records needed removing. Skew is already visible in the summary statistics. The median price is 35.71 against a maximum of 259.09, and the median of sold is 49.5 against a maximum of 54,052. Section 2.4 deals with this.")

h2("2.2 Exploratory Data Analysis (EDA)")
h3("Missing Value Analysis")
fig = figure("fig01_missing_values.png", "Missing values per column in the raw data", 5.0)
para("Figure 1 gives the number of missing values in each column. Units available is missing for 111 listings (11.1%) and the update time for 53 (5.3%), while every other column has fewer than ten gaps. The gaps in availability are not random. Most belong to listings whose stock text reads 'Limited quantity' or 'Last One', where the seller wrote a description instead of a number. I therefore filled gaps from related columns where I could, rather than deleting rows.")
h3("Text Fields")
shots(9)
para("The stock text uses a small set of patterns, for example 'N available / N sold', 'More than N available / N sold', 'Limited quantity available / N sold' and 'Last One / N sold'. From the price text, 996 prices are in US dollars and three are in Canadian dollars. The category column contains 63 different labels and had to be cleaned before use.")

h2("2.3 Data Preprocessing and Cleaning")
h3("Repairing and Creating Columns")
shots(11)
para("Other columns were enough to fix most gaps. I took the five missing prices from the price with currency text and converted the three Canadian dollar prices at an assumed rate of 0.73. Two missing sold counts were recovered from the stock text. The other six I set to zero, on the assumption that those listings had not yet made a sale. I gave the 47 'Last One' listings an availability of 1 and filled the remaining gaps in availability and update time with the median.")
para("I also created two features from the text. Bottle size in millilitres came from the listing title and was found for 93.7% of listings; the rest received the median, and ounces were converted at 29.57 ml. The update time was turned into days since update, measured back from the newest timestamp in the file (24 May 2024). After this step the model columns had no missing values.")
h3("Grouping the Category Labels")
shots(13)
fig = figure("fig02_categories_locations.png", "Listings by grouped category and by item location", 6.0)
para("Many of the 63 category labels were spelling variants of each other, such as 'Eau de Parfum' and 'Eau De Parfum'. Simple text rules reduced them to four groups: Eau de Toilette (463 listings), Eau de Parfum/Parfum (394), Other (73) and Cologne (70). Figure 2 also shows that 912 of the 1,000 listings ship from the United States, so location varies very little.")

h2("2.4 Feature Engineering and Selection")
h3("Feature Selection")
para("Five numeric features were used: price, sold, available, days since update and size in ml. Between them they describe what a product costs, how well it sells, how much stock is held, how recently the listing changed and what size it is, as the brief asks. I did not use brand or location as inputs. They have 246 and 276 distinct values, and one-hot encoding that many levels would produce sparse columns that dominate the distance calculations.")
h3("Testing the Category Variable")
shots(20)
para("Category was tried as a one-hot encoded input. The resulting clusters were exactly the four category groups. The silhouette rose to 0.355, but only because dummy variables separate easily, and the clusters told me nothing about sales. Category, brand and country were therefore kept for describing the clusters after fitting.")
h3("Outliers and Skewness")
shots(15)
figure("fig03_distributions_raw_vs_log.png", "Feature distributions before (top) and after (bottom) the log transformation", 6.4)
para("All the numeric features were strongly right-skewed, with skewness of 9.75 for sold, 8.65 for available and 13.31 for days since update. Under the IQR rule, between 54 and 476 listings per feature counted as outliers. These are genuine products, though. Some best sellers have more than 50,000 sales, and removing them would lose the listings the business cares about most. Instead I applied log(1 + x), which cut skewness to 0.11 for price and 0.50 for sold (Figure 3). Size stayed negatively skewed (-2.79) because of the small sample bottles.")
h3("Correlation")
figure("fig04_correlation.png", "Correlation matrix of the log-transformed features", 4.2)
para("The strongest correlation between two features is 0.44, between sold and available, and price and size correlate at 0.35 (Figure 4). The features are related without being redundant, so all five were kept.")
h3("Scaling and Normalisation")
shots(22, 23)
para("All three algorithms work with distances, so a feature measured on a larger scale would dominate the others. I tested three scalers with K-Means at k = 5. The silhouette was 0.255 with StandardScaler, 0.267 with MinMaxScaler and 0.802 with RobustScaler. The RobustScaler result is misleading. Because most bottles are 100 ml, the interquartile range of size is tiny, and after scaling the size column had a standard deviation of 159. Almost every distance was then decided by that one feature. I chose StandardScaler, which gives each feature the same spread.")

h2("2.5 Dimensionality Reduction with PCA")
shots(25)
figure("fig05_pca_variance.png", "Variance explained by each principal component", 4.6)
para("With PCA on the standardised features, two components explain 59.7% of the variance and three explain 77.8% (Figure 5; Jolliffe, 2002). PC1 loads mainly on sold (0.67) and available (0.65), so it represents sales volume and stock. PC2 loads mainly on size (0.67) and price (0.61). Two components would discard a lot of information, so PCA was used for plotting only and the models were fitted on all five scaled features.")

h1("3. Model Development")
h2("3.1 Choosing the Number of Clusters")
shots(28)
figure("fig06_kmeans_elbow_silhouette.png", "Elbow curve and silhouette score for K-Means", 6.0)
para("K-Means was run with k-means++ initialisation (Arthur and Vassilvitskii, 2007) and 20 starts for each k from 2 to 10. For k = 3 to 6 the silhouette score stayed between 0.246 and 0.255, peaking at k = 5, and the elbow curve bends between 4 and 6 (Figure 6). At k = 6, Davies-Bouldin and Calinski-Harabasz were slightly better (1.155 and 326.7, against 1.210 and 320.7). I kept k = 5. It had the best silhouette, and the only real change at k = 6 was that the large slow-selling group divided into a premium part (median price 80) and a budget part (27). That did not seem worth an extra cluster.")
shots(30)
para("To check stability I reran K-Means from single random starts and compared each run with my chosen solution using the adjusted Rand index. At k = 5 the mean was 0.90 and the lowest 0.41, which means some starts end in a different local optimum. Running 20 starts reduces this risk.")

h2("3.2 Model Selection and Training")
para("I picked three models that define a cluster in different ways. K-Means forms round groups around centres. Hierarchical clustering with Ward linkage joins listings one merge at a time (Ward, 1963). DBSCAN looks for dense regions and labels the rest as noise (Ester et al., 1996). The final fits appear side by side below, followed by the tuning for each.")
side_by_side(["K-Means (k = 5)", "Hierarchical (Ward, k = 5)", "DBSCAN (eps = 1.2)"], [31, 35, 39],
             ["Groups around centres, with all 1,000 listings assigned. Cluster sizes run from 71 to 382.",
              "Joins the closest listings one merge at a time. Cluster sizes run from 70 to 402.",
              "Labels 61 listings (6.1%) as noise and places 898 of the others in one cluster."])
h3("Hierarchical Clustering")
figure("fig07_dendrogram.png", "Ward dendrogram, truncated to the last 30 merges", 6.0)
shots(34)
para("Ward linkage was applied to the scaled data and the dendrogram cut at five clusters (Figure 7). Average linkage produced a cluster containing a single listing, and complete linkage at k = 6 produced one of three, so only Ward gave usable cluster sizes (smallest 70).")
h3("DBSCAN")
shots(37)
figure("fig08_kdistance.png", "Sorted 10-nearest-neighbour distances used to choose eps", 4.6)
shots(38)
para("min_samples was set to 10, twice the number of features, and the k-distance curve bends at an eps of about 1.38 (Figure 8). I tested eps from 0.8 to 1.4. At 1.0, 1.3 and 1.4 DBSCAN found only one cluster, while 1.2 gave three clusters with 6.1% of listings as noise. Even then, one cluster held 898 of the 939 clustered listings (95.6%).")

h2("3.3 Model Evaluation Metrics")
para("Without labels, the clusters can only be judged by internal measures. The silhouette score, from -1 to 1, compares how close a listing is to its own cluster and to the nearest other one, and higher is better (Rousseeuw, 1987). The Davies-Bouldin index compares the spread of each cluster with the distance between centres, and lower is better (Davies and Bouldin, 1979). The Calinski-Harabasz index divides between-cluster variance by within-cluster variance, and higher is better. The adjusted Rand index measures how far two models agree. For DBSCAN, noise points were removed before scoring.")
shots(41, 42)
para("Section 4.3 brings the scores together. The adjusted Rand index is 0.52 between K-Means and Ward, 0.11 between K-Means and DBSCAN and also 0.11 between Ward and DBSCAN. The two methods that cover every listing therefore broadly agree, whereas DBSCAN tells a very different story.")

h1("4. Results and Analysis")
h2("4.1 Visualisation Analysis")
figure("fig09_pca_clusters.png", "Clusters from the three models projected onto the first two principal components", 6.5)
para("Figure 9 plots the three solutions on the first two principal components. The K-Means clusters occupy mostly separate regions: the high-volume group (cluster 4) is on the right and the small samples (cluster 2) form their own patch at the bottom. Ward's groups overlap more. DBSCAN shows one large cluster and a few small patches, in line with its 95.6% share.")
shots(44)
figure("fig10_silhouette_kmeans.png", "Silhouette plot for K-Means (k = 5)", 4.8)
para("In the silhouette plot (Figure 10), most listings have small positive values, which explains the low average of 0.255. Clusters 2 (0.369) and 4 (0.334) are the most clearly defined. Cluster 3 is the weakest, with a mean of 0.199 and 11.8% of its listings below zero.")

h2("4.2 Cluster Profiling")
shots(46)
output_only(47)
para("Table 2 lists the median profile of each K-Means cluster. Estimated revenue is price multiplied by units sold. Since this treats the sold count as a lifetime total, it indicates relative importance rather than actual turnover.")
table("Profile of the five K-Means clusters (medians)",
      ["Cluster", "Listings", "Price ($)", "Sold", "Available", "Days since update", "Size (ml)", "Revenue share"],
      [["0 Premium slow movers", 382, "49.99", 16, 5, "1.6", "100", "3.6%"],
       ["1 Core best sellers", 273, "32.98", 400, 10, "0.6", "101", "78.1%"],
       ["2 Minis and samples", 71, "15.95", 32, 8, "3.8", "2.5", "1.1%"],
       ["3 Stale listings", 195, "31.95", 31, 10, "15.8", "100", "2.8%"],
       ["4 High-stock volume lines", 79, "25.81", 993, 84, "1.1", "101", "14.5%"]],
      [1.75, 0.6, 0.65, 0.5, 0.65, 0.8, 0.6, 0.75], 8.5)
figure("fig11_cluster_profiles.png", "Cluster profiles: colour shows the mean z-score, numbers show the median", 5.2)
bullet("The largest group, and a quiet one. The median price is $49.99, with low stock and few sales. Of the full-size clusters it has the highest share of Eau de Parfum and Parfum.", "Premium slow movers (38.2%).")
bullet("Mid-priced listings that sell about 400 units each and are kept up to date. They make up 27.3% of listings and an estimated 78% of revenue.", "Core best sellers.")
bullet("Very small bottles of about 2.5 ml with a median price of $16. Two thirds are parfum, so I treat them as testers and samples, not standard products.", "Minis and samples.")
bullet("Price and stock are typical, but the median listing was last updated 15.8 days before the cut-off, compared with under 4 days for every other cluster. Sales are low.", "Stale listings.")
bullet("A median stock of 84 units and almost 1,000 sales per listing at a lower price. Only 7.9% of listings fall here, but they account for about 14.5% of revenue.", "High-stock volume lines.")

shots(48)
para("Figure 11 shows the differences clearly. Cluster 2 is well below average on size, cluster 4 well above on stock and sales, and cluster 3 stands out on days since update. Brand does not determine the segment. Giorgio Armani is one of the four most common brands in three of the five clusters. Only the minis cluster is led by high-end names (Creed, Yves Saint Laurent and Chanel), which supports reading these as testers of designer fragrances.")

h2("4.3 Model Performance Comparison")
table("Validation results for the three clustering models",
      ["Model", "Clusters", "Noise %", "Silhouette", "Davies-Bouldin", "Calinski-Harabasz", "Largest cluster %"],
      [["K-Means (k = 5)", 5, "0.0", "0.255", "1.210", "320.7", "38.2"],
       ["Hierarchical Ward (k = 5)", 5, "0.0", "0.205", "1.336", "267.4", "40.2"],
       ["DBSCAN (eps = 1.2)", 3, "6.1", "0.269", "0.981", "84.2", "95.6"]],
      [1.8, 0.7, 0.65, 0.8, 0.95, 0.95, 0.85], 8.5)
h3("K-Means")
para("Of the two models that put every listing in a cluster, K-Means scored best, with a silhouette of 0.255 and the highest Calinski-Harabasz value (320.7). None of its clusters is very small (the smallest has 71 listings) and each has a clear commercial meaning. On the downside, it assumes round groups and k has to be chosen in advance.")
h3("Hierarchical Clustering")
para("Ward linkage was weaker on all three measures (0.205, 1.336 and 267.4) and only partly matched K-Means on which listings belong together (adjusted Rand index 0.52). The dendrogram helps to show how groups merge, but the method compares every pair of listings, so it slows down on large datasets.")
h3("DBSCAN")
para("DBSCAN has the best silhouette (0.269) and Davies-Bouldin score (0.981). These scores come from splitting off a few small dense groups and ignoring the noise, which leaves 95.6% of the data in one cluster. With an adjusted Rand index of only 0.11 against K-Means, it offers almost no segmentation to act on.")

h1("5. Critical Evaluation")
para("Sections 5 to 7 are aimed at an executive reader and draw on the results of Task 1.")
h2("5.1 Executive Summary")
para("I divided 1,000 perfume listings into five segments using price, sales, stock, listing age and bottle size. The headline result is that the core best sellers make up only 27% of listings but an estimated 78% of revenue. A further 20% of listings, the stale group, sell poorly and have a median of 15.8 days since their last update. The segments overlap, so I would treat them as a rough guide to where effort should go, not as exact categories.")
h2("5.2 Suitability of the Methods")
para("As there is no labelled outcome to predict, clustering was the natural choice of method. The inputs mattered as much as the algorithm (Hastie et al., 2009). Brand and location, with hundreds of values each, would have swamped the result, and category made the clusters simply repeat the product type instead of showing sales behaviour. Sales and stock were heavily skewed, so I log-transformed and standardised them instead of deleting the best products.")
para("K-Means fits the problem because every listing needs a segment and it produces groups of a workable size. Hierarchical clustering does not need k in advance, but it scored lower here and slows down as the data grows. DBSCAN is useful for spotting unusual listings, but this data has no clear gaps between groups, so it placed most listings in one cluster.")
h2("5.3 Final Model Justification")
para("My final choice was K-Means. DBSCAN scored better on paper but could not segment the listings, and Ward was behind on every measure, so K-Means was the strongest of the two models that cover all listings. Its clusters are also of a usable size, and each can be explained in one sentence, which matters for business use. It has limits. A silhouette of 0.255 means the structure is weak, so decisions should rest on the segment profiles rather than on listings near a boundary. If the premium group needs splitting by price, a six-cluster solution is a reasonable alternative.")
h2("5.4 Limitations, Assumptions and Alternatives")
para("The data is one snapshot from May 2024, so seasonality and trends cannot be seen. Most listings were updated during the final week, so 'stale' only means older than the rest of this snapshot. Revenue is estimated from price and a lifetime sold count, not from dated sales.", "Data limitations.")
para("K-Means assumes round clusters of similar size, and all three methods depend on distances, which become less informative as more features are added. The 0.73 exchange rate and the zero sold counts are assumptions, and median filling hides some real variation.", "Model assumptions.")
para("Ninety-one percent of the listings ship from the United States, so the results say little about other markets. Older listings have had longer to build up sales, so the sold count may make newer products look weaker than they are.", "Potential biases.")
para("Given more time, I would add sale dates, brand tier and customer ratings. I would also test Gaussian mixture models, which give each listing a probability of belonging to each segment and so handle overlapping groups better.", "Alternative approaches.")

h1("6. Business Recommendations")
figure("fig12_segment_share.png", "Share of listings and share of estimated revenue by segment", 5.6)
para("Together, the core best sellers and high-stock volume lines account for 35% of listings and about 93% of estimated revenue (Figure 12). The largest group (38% of listings) combines higher prices, little stock and few sales, and brings in under 4% of revenue. These findings lead to five recommendations. None of them needs new data, so all could begin straight away.")
numbered("Keep the core best sellers and high-stock lines in stock and avoid unnecessary price changes, as they generate most of the revenue.", "Look after the winners.")
numbered("Review the 195 stale listings in the next update cycle. Update the title, photos and price, or remove listings that do not sell, then check whether sales change. The data cannot show whether staleness causes weak sales or results from them.", "Refresh the stale listings.")
numbered("Try price cuts or bundles on a small sample of premium slow movers before rolling them out to the whole segment, because the high prices may be deliberate.", "Test before discounting.")
numbered("Around 7% of listings are 2.5 ml samples. Their behaviour is very different from full-size products and would distort averages, so they should be reported separately in sales dashboards.", "Separate the samples.")
numbered("Rerun the model each month on new data to see whether listings move between segments.", "Monitor movement.")

h1("7. Conclusion")
para("In this project I grouped 1,000 perfume listings into five segments with K-Means. The data was cleaned, five features were log-transformed and standardised, and three clustering methods were compared. K-Means gave the most useful result, although its silhouette of 0.255 shows only weak separation. The key finding is how concentrated sales are: about a quarter of listings produce most of the estimated revenue. The recommendations therefore focus on protecting those listings and fixing the stale ones. Before relying on the segment sizes, I would repeat the analysis over a longer period. Future work should use dated sales data and test probabilistic models for more reliable segments.")

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
