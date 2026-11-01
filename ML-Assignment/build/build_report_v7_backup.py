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
OUT = ROOT / "COM7022_Assignment_Report_v4.docx"

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
para("Anyone selling perfume online ends up with a long list of products, and it quickly becomes hard to tell which ones deserve attention. Managing a range like that is easier when similar products are grouped, because effort can then go to the groups that matter. In this report I apply clustering to 1,000 perfume listings to find such groups from their characteristics and sales performance.")
para("The report follows the two tasks in the brief. Task 1, the practical project, takes up sections 2 to 4. This is where I clean the data, pick the features and explain why, and then try K-Means, hierarchical clustering and DBSCAN before comparing them. Task 2 is the critical report for executives and covers sections 5 to 7. In it I look back at whether the methods were a good fit, explain why I settled on one model and suggest what the business could do next.")
para("I did all of the analysis in Python with pandas, SciPy and scikit-learn (Pedregosa et al., 2011). Each step below shows the code with its output, and the complete notebook code is given in the appendix.")

h1("2. Methodology")
h2("2.1 Data Collection and Overview")
h3("Libraries Used")
shots(2, show_out=False)
para("The code starts by importing the libraries. Most of the work uses pandas and scikit-learn, with SciPy for the dendrogram and matplotlib and seaborn for the charts. I set the random seed to 42 so that running the notebook again gives the same numbers.")
h3("Loading the Dataset")
shots(4)
para("When I first opened the CSV, the first column name started with a hidden character (a byte order mark), so I read it with the utf-8-sig encoding. That gives 1,000 rows and ten columns. Only price, available and sold are numeric and the other seven are text, so much of the useful information sits inside text columns.")
h3("Data Types and Summary Statistics")
shots(5, 6)
para("The info() output shows no duplicate rows, so no records needed removing. Skew is already visible in the summary statistics. The median price is 35.71 against a maximum of 259.09, and the median of sold is 49.5 against a maximum of 54,052.")

h2("2.2 Exploratory Data Analysis (EDA)")
h3("Missing Value Analysis")
fig = figure("fig01_missing_values.png", "Missing values per column in the raw data", 5.0)
para("Figure 1 gives the number of missing values in each column. Units available is missing for 111 listings (11.1%) and the update time for 53 (5.3%), while every other column has fewer than ten gaps. These gaps are not spread at random. When I checked, most of them were listings where the stock text says 'Limited quantity' or 'Last One', so the seller simply never gave a number. I therefore filled gaps from related columns where I could, rather than deleting rows.")
h3("Text Fields")
shots(9)
para("The stock text uses a small set of patterns, for example 'N available / N sold', 'More than N available / N sold', 'Limited quantity available / N sold' and 'Last One / N sold'. From the price text, 996 prices are in US dollars and three are in Canadian dollars. The category column contains 63 different labels and had to be cleaned before use.")

h2("2.3 Data Preprocessing and Cleaning")
h3("Repairing and Creating Columns")
shots(11)
para("Other columns were enough to fix most gaps. I took the five missing prices from the price with currency text and converted the three Canadian dollar prices at an assumed rate of 0.73. Two missing sold counts were recovered from the stock text. The other six I set to zero, on the assumption that those listings had not yet made a sale. I gave the 47 'Last One' listings an availability of 1 and filled the remaining gaps in availability and update time with the median.")
para("I also created two features from the text. Bottle size in millilitres came from the listing title and was found for 93.7% of listings; the rest received the median, and ounces were converted at 29.57 ml. The update time was turned into days since update, measured back from the newest timestamp in the file (24 May 2024).")
h3("Grouping the Category Labels")
shots(13)
fig = figure("fig02_categories_locations.png", "Listings by grouped category and by item location", 6.0)
para("Many of the 63 category labels were spelling variants of each other, such as 'Eau de Parfum' and 'Eau De Parfum'. Simple text rules reduced them to four groups: Eau de Toilette (463 listings), Eau de Parfum/Parfum (394), Other (73) and Cologne (70). Figure 2 also shows that 912 of the 1,000 listings ship from the United States, so location varies very little.")

h2("2.4 Feature Engineering and Selection")
h3("Feature Selection")
para("For the clustering I kept five numeric columns: price, sold, available, days since update and size in ml. Price and size describe the product itself, sold and available show how it is trading, and days since update shows how actively the seller looks after it. Brand and location were left out. With 246 brands and 276 locations, one-hot encoding would add hundreds of mostly empty columns, and those would end up controlling the distances.")
h3("Testing the Category Variable")
shots(20)
para("Category was tried as a one-hot encoded input. The resulting clusters were exactly the four category groups. The silhouette rose to 0.355, but only because dummy variables separate easily, and the clusters told me nothing about sales. Category, brand and country were therefore kept for describing the clusters after fitting.")
h3("Outliers and Skewness")
shots(15)
figure("fig03_distributions_raw_vs_log.png", "Histograms of each feature, raw (top row) and after log(1 + x) (bottom row)", 6.4)
para("Every numeric feature had a long right tail. The skewness was 9.75 for sold, 8.65 for available and 13.31 for days since update. Under the IQR rule, between 54 and 476 listings per feature counted as outliers. These are genuine products, though. Some best sellers have more than 50,000 sales, and removing them would lose the listings the business cares about most. Instead I applied log(1 + x), which cut skewness to 0.11 for price and 0.50 for sold (Figure 3). Size stayed negatively skewed (-2.79) because of the small sample bottles.")
h3("Correlation")
figure("fig04_correlation.png", "Correlation matrix of the log-transformed features", 4.2)
para("The strongest correlation between two features is 0.44, between sold and available, and price and size correlate at 0.35 (Figure 4). The features are related without being redundant, so all five were kept.")
h3("Scaling and Normalisation")
shots(22, 23)
para("Because all three algorithms measure distances, a column with large numbers would outweigh the rest unless the data is scaled. To choose a scaler I ran K-Means at k = 5 once with each. StandardScaler gave a silhouette of 0.255, MinMaxScaler 0.267 and RobustScaler 0.802. The RobustScaler result is misleading. Because most bottles are 100 ml, the interquartile range of size is tiny, and after scaling the size column had a standard deviation of 159. Almost every distance was then decided by that one feature. I went with StandardScaler, which leaves every feature with a mean of 0 and a standard deviation of 1.")

h2("2.5 Reducing Dimensions with PCA")
shots(25)
figure("fig05_pca_variance.png", "PCA scree plot with cumulative explained variance", 4.6)
para("I ran PCA on the standardised data mainly so that it could be plotted. Two components keep 59.7% of the variance and three keep 77.8% (Figure 5; Jolliffe, 2002). Sold (0.67) and available (0.65) have the biggest loadings on PC1, so the first component is really about sales volume and stock. PC2 is driven by size (0.67) and price (0.61). The models themselves were fitted on all five scaled features.")

h1("3. Model Development")
h2("3.1 Choosing the Number of Clusters")
shots(28)
figure("fig06_kmeans_elbow_silhouette.png", "Elbow curve and silhouette score for K-Means", 6.0)
para("For K-Means I used k-means++ starting points (Arthur and Vassilvitskii, 2007) with 20 starts, and tried every k from 2 to 10. The silhouette barely moved between k = 3 and k = 6, staying between 0.246 and 0.255, and its highest value was at k = 5. The elbow in Figure 6 is not sharp and the bend falls between 4 and 6. Two other scores leaned slightly towards k = 6: Davies-Bouldin was 1.155 against 1.210, and Calinski-Harabasz 326.7 against 320.7. I kept k = 5. It had the best silhouette, and the only real change at k = 6 was that the large slow-selling group divided into a premium part (median price 80) and a budget part (27). That did not seem worth an extra cluster.")
shots(30)
para("I was also worried that the result might depend on the random start. So I ran K-Means again from 20 single random starts and compared each run with my final solution using the adjusted Rand index. At k = 5 the average agreement was 0.90 but the worst was 0.41, so an unlucky start can land in a different local optimum. Running 20 starts reduces this risk.")

h2("3.2 Model Selection and Training")
para("I picked three models that define a cluster in different ways. K-Means puts each listing with its nearest centre, so it tends to find compact, round groups. Ward's method starts with every listing on its own and keeps merging the two groups that add the least variance (Ward, 1963). DBSCAN works differently again: it grows clusters out of dense areas and leaves isolated points as noise (Ester et al., 1996). The final fits appear side by side below, followed by the tuning for each.")
side_by_side(["K-Means (k = 5)", "Hierarchical (Ward, k = 5)", "DBSCAN (eps = 1.2)"], [31, 35, 39],
             ["Groups around centres, with all 1,000 listings assigned. Cluster sizes run from 71 to 382.",
              "Joins the closest listings one merge at a time. Cluster sizes run from 70 to 402.",
              "61 listings (6.1%) end up as noise, and 898 of the rest fall into a single cluster."])
h3("Tuning the Hierarchical Model")
figure("fig07_dendrogram.png", "Ward dendrogram showing the last 30 merges", 6.0)
shots(34)
para("Ward linkage was applied to the scaled data and the dendrogram cut at five clusters (Figure 7). Average linkage produced a cluster containing a single listing, and complete linkage at k = 6 produced one of three, so only Ward gave usable cluster sizes (smallest 70).")
h3("Tuning DBSCAN")
shots(37)
figure("fig08_kdistance.png", "Sorted 10-nearest-neighbour distances used to choose eps", 4.6)
shots(38)
para("min_samples was set to 10, twice the number of features, and the k-distance curve bends at an eps of about 1.38 (Figure 8). I tested eps from 0.8 to 1.4. At 1.0, 1.3 and 1.4 DBSCAN found only one cluster, while 1.2 gave three clusters with 6.1% of listings as noise. Even then, one cluster held 898 of the 939 clustered listings (95.6%).")

h2("3.3 Model Evaluation Metrics")
para("Without labels, the clusters can only be judged by internal measures. The silhouette score, from -1 to 1, compares how close a listing is to its own cluster and to the nearest other one, and higher is better (Rousseeuw, 1987). The Davies-Bouldin index compares the spread of each cluster with the distance between centres, and lower is better (Davies and Bouldin, 1979). The Calinski-Harabasz index divides between-cluster variance by within-cluster variance, and higher is better. The adjusted Rand index measures how far two models agree. For DBSCAN, noise points were removed before scoring.")
shots(41, 42)
para("Section 4.3 brings the scores together. K-Means and Ward agree reasonably well (adjusted Rand index 0.52). DBSCAN hardly agrees with either of them, scoring 0.11 against both, so it is really giving a different answer to the question.")

h1("4. Results and Analysis")
h2("4.1 Visualisation Analysis")
figure("fig09_pca_clusters.png", "The three cluster solutions plotted on PC1 and PC2", 6.5)
para("In Figure 9 the three solutions are drawn on the first two principal components. For K-Means the groups mostly keep to their own areas. The high-volume cluster 4 sits out to the right, and the small samples in cluster 2 form a separate patch near the bottom. Ward's groups overlap more. DBSCAN shows one large cluster and a few small patches, in line with its 95.6% share.")
shots(44)
figure("fig10_silhouette_kmeans.png", "Silhouette plot for K-Means (k = 5)", 4.8)
para("In the silhouette plot (Figure 10), most listings have small positive values, which explains the low average of 0.255. Clusters 2 (0.369) and 4 (0.334) are the most clearly defined. Cluster 3 is the weakest, with a mean of 0.199 and 11.8% of its listings below zero.")

h2("4.2 Cluster Profiling")
shots(46)
output_only(47)
para("Table 1 lists the median profile of each K-Means cluster. To get a rough revenue figure I multiplied price by units sold. Since this treats the sold count as a lifetime total, it indicates relative importance rather than actual turnover.")
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
bullet("A median stock of 84 units and almost 1,000 sales per listing at a lower price. This is a small group, just 7.9% of listings, yet it brings in roughly 14.5% of revenue.", "High-stock volume lines.")

shots(48)
para("Figure 11 shows the differences clearly. Cluster 2 is well below average on size, cluster 4 well above on stock and sales, and cluster 3 stands out on days since update. Brand does not determine the segment. Giorgio Armani, for example, is in the top four brands of three different clusters. The minis cluster is the odd one out, because its most common brands are expensive ones such as Creed, Yves Saint Laurent and Chanel. That makes sense if these are testers of designer perfumes.")

h2("4.3 Model Performance Comparison")
table("Validation results for the three clustering models",
      ["Model", "Clusters", "Noise %", "Silhouette", "Davies-Bouldin", "Calinski-Harabasz", "Largest cluster %"],
      [["K-Means (k = 5)", 5, "0.0", "0.255", "1.210", "320.7", "38.2"],
       ["Hierarchical Ward (k = 5)", 5, "0.0", "0.205", "1.336", "267.4", "40.2"],
       ["DBSCAN (eps = 1.2)", 3, "6.1", "0.269", "0.981", "84.2", "95.6"]],
      [1.8, 0.7, 0.65, 0.8, 0.95, 0.95, 0.85], 8.5)
h3("K-Means")
para("K-Means came out on top of the two models that place every listing in a cluster. Its silhouette was 0.255 and its Calinski-Harabasz value of 320.7 was the highest of all three. The smallest cluster still has 71 listings, and I could give each cluster a clear business meaning.")
h3("Ward Linkage")
para("Ward did worse than K-Means on every measure (silhouette 0.205, Davies-Bouldin 1.336, Calinski-Harabasz 267.4), and the two only half agree on which listings go together (adjusted Rand index 0.52). The dendrogram was handy for seeing the merges, but Ward compares every pair of listings, which gets slow on a bigger catalogue.")
h3("DBSCAN")
para("On paper DBSCAN looks best (silhouette 0.269, Davies-Bouldin 0.981). The catch is that it only splits off two small dense groups and leaves out the noise, so one cluster still holds 95.6% of the data. With an adjusted Rand index of only 0.11 against K-Means, it offers almost no segmentation to act on.")

h1("5. Critical Evaluation")
para("Sections 5 to 7 are aimed at an executive reader and draw on the results of Task 1.")
h2("5.1 Summary of the Findings")
para("The 1,000 perfume listings fall into five segments once price, sales and stock are looked at alongside listing age and bottle size. The headline result is that the core best sellers make up only 27% of listings but an estimated 78% of revenue. Another 20% of the range, the stale group, sells poorly and had not been updated for a median of 15.8 days. The groups blur at the edges, so they are a guide for where to spend time, not hard categories.")
h2("5.2 Suitability of the Methods")
para("As there is no labelled outcome to predict, clustering was the natural choice of method. Picking the inputs mattered as much as picking the algorithm (Hastie et al., 2009). When I let category in, the clusters just copied it, so category, brand and location were kept out. Taking logs of the skewed sales and stock figures also stopped a few huge sellers from dragging the clusters around.")
para("If every product needs a segment, K-Means is the practical choice, and its groups are a size a team can work with. Ward does not need k up front, but it scored lower here. I would use DBSCAN for picking out odd listings rather than for segmenting, since these listings have no clear gaps between them and it lumped almost all of them together.")
h2("5.3 Final Model Justification")
para("My final choice was K-Means. It was the strongest model that covers every listing, and each of its clusters can be explained in one sentence, which matters for business use. It has limits. With a silhouette of only 0.255 the groups are not sharply separated, so decisions should follow each segment's overall profile, not the listings near a border. If the business wants the premium group split by price, the six-cluster version does that.")
h2("5.4 Limitations and Other Approaches")
para("The data is one snapshot from May 2024, so seasonality and trends cannot be seen. Most listings were updated during the final week, so 'stale' only means older than the rest of this snapshot. Revenue is estimated from price and a lifetime sold count, not from dated sales.", "Data limitations.")
para("K-Means assumes round clusters of similar size, and all three methods depend on distances, which become less informative as more features are added. The 0.73 exchange rate and the zero sold counts are assumptions, and median filling hides some real variation.", "Model assumptions.")
para("Ninety-one percent of the listings ship from the United States, so the results say little about other markets. Older listings have had longer to build up sales, so the sold count may make newer products look weaker than they are.", "Potential biases.")
para("Given more time, I would add sale dates, brand tier and customer ratings. I would also test Gaussian mixture models, which give each listing a probability of belonging to each segment and so handle overlapping groups better.", "Alternative approaches.")

h1("6. Business Recommendations")
figure("fig12_segment_share.png", "Share of listings and share of estimated revenue by segment", 5.6)
para("Together, the core best sellers and high-stock volume lines account for 35% of listings and about 93% of estimated revenue (Figure 12). The largest group (38% of listings) combines higher prices, little stock and few sales, and brings in under 4% of revenue. None of the five recommendations below needs new data.")
numbered("Keep the core best sellers and high-stock lines in stock and avoid unnecessary price changes, as they generate most of the revenue.", "Look after the winners.")
numbered("Review the 195 stale listings in the next update cycle. Update the title, photos and price, or remove listings that do not sell, then check whether sales change. The data cannot show whether staleness causes weak sales or results from them.", "Refresh the stale listings.")
numbered("Try price cuts or bundles on a small sample of premium slow movers before rolling them out to the whole segment, because the high prices may be deliberate.", "Test before discounting.")
numbered("Around 7% of listings are 2.5 ml samples. Their behaviour is very different from full-size products and would distort averages, so they should be reported separately in sales dashboards.", "Separate the samples.")
numbered("Rerun the model each month on new data to see whether listings move between segments.", "Monitor movement.")

h1("7. Conclusion")
para("In this project I grouped 1,000 perfume listings into five segments with K-Means. K-Means gave the most useful result, although its silhouette of 0.255 shows only weak separation. What surprised me most was how lopsided the sales are, with roughly a quarter of the listings bringing in most of the estimated revenue. That is why the recommendations are mainly about looking after those listings and sorting out the stale ones. Future work should use dated sales data and test probabilistic models for more reliable segments.")

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
