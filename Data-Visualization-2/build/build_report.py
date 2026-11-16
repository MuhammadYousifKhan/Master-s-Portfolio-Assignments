import json
import re
from pathlib import Path

import nbformat
from PIL import Image
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
ASSET = Path(__file__).resolve().parent / "assets"
OUT = ROOT / "COM7021 Data Visualisation Report.docx"
BODY_TXT = Path(__file__).resolve().parent / "report_body.txt"

BLUE = RGBColor(0x2E, 0x6F, 0xB5)
NAVY = RGBColor(0x1F, 0x3A, 0x5F)
FONT = "Times New Roman"
MONO = "Consolas"

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
sec.left_margin = sec.right_margin = Inches(1)
sec.top_margin = Inches(1.1)
sec.bottom_margin = Inches(0.9)
sec.header_distance = Inches(0.3)

normal = doc.styles["Normal"]
normal.font.name = FONT
normal.font.size = Pt(11)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.15
for name, size, colour in [("Heading 1", 16, RGBColor(0, 0, 0)), ("Heading 2", 13, BLUE), ("Heading 3", 11, BLUE)]:
    st = doc.styles[name]
    st.font.name = FONT
    st.font.size = Pt(size)
    st.font.bold = True
    st.font.italic = False
    st.font.color.rgb = colour
    for attr in ("w:eastAsia", "w:ascii", "w:hAnsi"):
        st.element.rPr.rFonts.set(qn(attr), FONT)
    st.paragraph_format.space_before = Pt(12 if name != "Heading 3" else 8)
    st.paragraph_format.space_after = Pt(4)
    st.paragraph_format.keep_with_next = True

counted = []
state = {"section": "front", "fig": 0, "tab": 0}


def add_field(run, instr, placeholder="1"):
    for kind in ("begin", None, "separate", "text", "end"):
        if kind is None:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = instr
        elif kind == "text":
            el = OxmlElement("w:t")
            el.text = placeholder
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


def shade(cell, colour):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), colour)
    tcPr.append(shd)


def para(text, lead=None, count=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=None):
    p = doc.add_paragraph()
    p.alignment = align
    if lead:
        p.add_run(lead + " ").bold = True
    run = p.add_run(text)
    if size:
        run.font.size = Pt(size)
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


def h1(text):
    state["section"] = text
    doc.add_heading(text, level=1)


def h2(text):
    doc.add_heading(text, level=2)


def h3(text):
    doc.add_heading(text, level=3)


def figure(file, caption, width=6.0):
    state["fig"] += 1
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(FIG / file), width=Inches(width))
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.add_run(f"Figure {state['fig']}: {caption}").font.size = Pt(10)


def shot_width(path, cap):
    w, _ = Image.open(path).size
    return min(cap, w / 190)


def label_par(cell, text, first=False):
    p = cell.paragraphs[0] if first else cell.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    p.add_run(text).bold = True
    return p


def shots(idxs):
    t = doc.add_table(rows=1, cols=1)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = t.rows[0].cells[0]
    first = True
    for i in idxs:
        for kind, label in [("code", "Code"), ("out", "Output")]:
            path = ASSET / f"{kind}_{i:02d}.png"
            if path.exists():
                label_par(cell, label, first)
                first = False
                q = cell.add_paragraph()
                q.alignment = WD_ALIGN_PARAGRAPH.CENTER
                q.paragraph_format.space_after = Pt(4)
                q.add_run().add_picture(str(path), width=Inches(shot_width(path, 5.9)))
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def table(caption, header, rows, widths, size=9, count=False):
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
            if count:
                counted.append((state["section"], str(v)))
    for row in t.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Inches(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def cover():
    fields = [("Awarding Body:", "Arden University"),
              ("Programme Name:", "[                    ]"),
              ("Module Name (and Part if applicable):", "Data Visualisation (COM7021)"),
              ("Assessment Title:", "Data Visualisation Report: EcoMove Mobility Investigation"),
              ("Student Number:", "[STUDENT ID]"),
              ("Tutor Name:", "[TUTOR NAME]"),
              ("Word Count:", "WORDCOUNT")]
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
    add_field(p.add_run(), r'TOC \o "1-2" \h \z \u', "Right-click here and choose Update Field to show the contents.")
    upd = OxmlElement("w:updateFields")
    upd.set(qn("w:val"), "true")
    doc.settings.element.append(upd)
    doc.add_page_break()


F = json.loads((Path(__file__).resolve().parent / "facts.json").read_text(encoding="utf-8"))
D, N = F["data"], F["network"]
V1, V2, V3, V4 = F["v1_reliability_trend"], F["v2_weekday_pattern"], F["v3_event_uplift"], F["v4_city_recovery_change"]
V5, V6, V7, V8, V9 = F["v5_energy_efficiency"], F["v6_unit_economics"], F["v7_city_investment"], F["v8_accessibility_matrix"], F["v9_mode_profile"]
c4, c7 = V4["cities"], V7["cities"]

cover()
toc()

W = V1["weather"]
CI = V2["city_index"]

h1("Executive Summary")
para(f"This report analyses {D['rows']:,} EcoMove service records from {D['date_min']} to {D['date_max']} in Python. The records cover {D['cities']} cities in {D['countries']} countries and {D['modes']} transport modes. Nine static visuals and a Streamlit dashboard support decisions on route planning, reliability, sustainability, accessibility and investment.")
para(f"Five findings stand out. Bus is the weakest service, ranking last on punctuality in all {V1['months']} months and falling in the accessibility priority zone in every city. Snow lowers on-time performance by {W['snow_drop_min']} to {W['snow_drop_max']} points, whatever the mode. Mass transit covers its costs in every city ({V7['mass_recovery_min']}% to {V7['mass_recovery_max']}%), and city deficits are associated with micromobility's share of cost. Event days raise demand per record by {V3['uplift_min']}% to {V3['uplift_max']}% without any fare premium. Bus saves {V5['modes']['Bus']['co2_per_kwh']} kg of CO2 per kWh, about half the Metro figure ({V5['modes']['Metro']['co2_per_kwh']} kg).")

h1("1. Context and Aims")
para(f"EcoMove runs metro, tram, bus, park and ride, bike share and e-scooter services in {D['countries']} European countries. The brief asks for a Python investigation (Task 1) and a reflective report (Task 2). The design serves two audiences. Senior managers need a few clear messages, each tied to a decision. Analysts need the method, the data checks and the code, which are in Appendices A and B. All figures were calculated in Python and checked automatically against the computed results.")

h1("2. Part A: Visual Investigation (Task 1)")
h2("2.1 Data preparation and quality checks")
para(f"The workbook holds {D['rows']:,} rows and {D['cols_raw']} columns. It has {D['nulls']} missing values and {D['duplicates']} duplicate rows. Dates were stored as Excel serial numbers and were converted; the records cover {D['days_covered']} of the {D['days_in_range']} days in the period.")
para(f"Zero values were kept because they fit the service type. All {D['zero_energy_rows']} zero-energy rows are Bike Share, so Bike Share is left out of energy ratios, and all {D['zero_complaint_rows']} zero-complaint rows are micromobility. Groups have different record counts, so comparisons use per-record means or ratios such as cost recovery (revenue divided by operating cost) and complaints per 1,000 passengers.")
shots([2, 4, 6, 7, 9])

h2("2.2 Design approach")
para("Each visual answers one management question. The main comparisons use position on a common scale, which Cleveland and McGill (1984) found to be the most accurately read encoding; colour intensity is reserved for heatmaps. Colours come from Paul Tol's colour-blind-safe scheme (Tol, 2021) and the cividis map (Nuñez, Anderton and Renslow, 2018), so red and green never carry meaning alone. Plain titles and direct labels keep clutter down (Few, 2006; Tufte, 2001). Table 1 maps each visual to the brief.")
table("Visuals mapped to the brief's techniques",
      ["Visual", "Chart type", "Technique", "Management question"],
      [["1", "Small multiples and dot plot", "Time series", "Is reliability drifting, and how much does weather matter?"],
       ["2", "Indexed heatmaps", "Comparison", "When and where is demand highest?"],
       ["3", "Dumbbell", "Comparison", "Who absorbs event crowds?"],
       ["4", "Slope chart", "Comparison over time", "Which cities crossed break-even?"],
       ["5", "Log-log scatter", "Relationship", "Which modes turn energy into CO2 savings?"],
       ["6", "Split violin", "Distribution", "Do margins depend on price or cost?"],
       ["7", "Lollipop", "Performance indicator", "What sets city cost recovery?"],
       ["8", "Quadrant bubble chart", "Performance indicator", "Where should accessibility money go first?"],
       ["9", "Radar small multiples", "Performance profile", "What is each mode good and bad at?"],
       ["D", "Streamlit dashboard", "Interactive dashboard", "All of the above, filtered"]],
      [0.55, 1.75, 1.6, 2.6])

h2("2.3 Visual 1: reliability over time and in bad weather")
figure("fig01_reliability_small_multiples.png", "Monthly on-time percentage by mode, and mean on-time by weather and mode.", 6.5)
shots([11])
para(f"The question is whether weak reliability persists, and how exposed it is to weather. Small multiples share one axis, so each mode can be read alone (Tufte, 2001); the dot plot places every mode on one scale for each weather type. On-time percentage is used as the delay measure because the two are almost perfectly correlated (r = {V1['corr_ontime_delay']} per record).", "Purpose and design.")
para(f"There was little change in network reliability. It averaged {V1['network_2024']}% in 2024 and {V1['network_2025']}% in 2025, and no month fell outside {V1['network_month_min']}% to {V1['network_month_max']}%. Bus was last every month and its best month ({V1['modes']['Bus']['max']}%) was lower than Tram's worst month ({V1['modes']['Tram']['min']}%). Changes in weather affect timing more than changes in the month. In snow, each mode sees a drop in on-time by {W['snow_drop_min']} to {W['snow_drop_max']} points, Bus drops to {W['bus_snow']}% and the mean rating drops from {W['rating_clear']} to {W['rating_snow']}. Reliability gaps are between the modes and not between cities, as city averages fall between {V1['city_ontime_min']}% and {V1['city_ontime_max']}%.", "What it shows.")
para("Bus requires a long-term programme, not seasonal solutions, and plans for winter should be for all modes.", "Implication.")

h2("2.4 Visual 2: when and where demand concentrates")
figure("fig02_weekday_heatmap.png", "Demand index by weekday and mode, and by city and mode (100 = the mode's own average per record).", 6.5)
shots([13])
para("Planners should be able to observe when and where demand peaks. The modes are indexed to their respective averages, so that the colour scale for small modes is the same as the colour scale for large modes, and comparisons between cities are not affected by mode mix.", "Purpose and design.")
para(f"Weekend records have {V2['weekend_drop_pct']}% fewer passengers than weekday records. The fall is largest on Metro ({V2['weekend_drop_by_mode_pct']['Metro']}%) and Park and Ride ({V2['weekend_drop_by_mode_pct']['Park and Ride']}%), yet weekend on-time ({V2['ontime_weekend']}%) is no better than weekday ({V2['ontime_weekday']}%). The high-demand cities are {V2['city_top2'][0]} and {V2['city_top2'][1]}, with {V2['top2_min_index']} or more points in each mode, while {V2['city_bottom']} has {CI[V2['city_bottom']]['min']}-{CI[V2['city_bottom']]['max']} points. Country does not say a lot about demand: in France, Paris averages {CI['Paris']['mean']:.0f} and Lyon {CI['Lyon']['mean']:.0f}.", "What it shows.")
para(f"The frequency of weekend Metro and Park and Ride can be discussed, and in the case of peak period capacity planning, the starting point should be {V2['city_top2'][0]} and {V2['city_top2'][1]}.", "Implication.")

h2("2.5 Visual 3: who gains most on event days")
figure("fig03_event_dumbbell.png", "Mean passengers per record on normal and event days by mode (log scale), with uplift.")
shots([15])
para("For operations teams, the question is which modes are event crowd absorbers. A dumbbell places the normal level, the event level and the gap on one line per mode, while a log scale keeps Metro and micromobility on the same axis.", "Purpose and design.")
para(f"Uplift is between {V3['uplift_min']}% ({V3['uplift_min_mode']}) and {V3['uplift_max']}% ({V3['uplift_max_mode']}), and Park and Ride increases by {V3['modes']['Park and Ride']['uplift_pct']}%. Metro gets the largest absolute increase, having {V3['modes']['Metro']['extra_pax']:,.0f} additional passengers per record. There is no price premium on the additional demand, with revenue per passenger of €{V3['rev_per_pax_event']} on event days against €{V3['rev_per_pax_normal']} on other days.", "What it shows.")
para("Event planning should begin with Metro and Park and Ride capacity, and try an event fare.", "Implication.")

h2("2.6 Visual 4: which cities crossed break-even")
figure("fig04_city_recovery_slope.png", "Cost recovery by city, 2024 against 2025, with the 100% break-even line.")
shots([17])
para("A direction of travel, not a one-year ranking, is needed for finance leads. A slope chart displays a rise or fall as a line angle, is marked at both ends with the values, and only colours the cities that cross the break-even mark (Kirk, 2019).", "Purpose and design.")
para(f"In both years, network cost recovery was {V4['network_2024']}%, although there was some movement for individual cities. Munich fell from {c4['Munich']['2024']}% to {c4['Munich']['2025']}%, Milan from {c4['Milan']['2024']}% to {c4['Milan']['2025']}% and Amsterdam from {c4['Amsterdam']['2024']}% to {c4['Amsterdam']['2025']}%, while Berlin, Paris and Vienna rose above 100%. In every city, mass transit alone recovered {V4['mass_min_any_city_year']}% or more. In the same period, the share of Milan's records from micromobility grew from {c4['Milan']['micro_record_share_2024']:.0f}% to {c4['Milan']['micro_record_share_2025']:.0f}%.", "What it shows.")
para("Munich, Milan and Amsterdam should be on a finance watchlist for 2026, and the review must begin with service mix.", "Implication.")

h2("2.7 Visual 5: energy used against CO2 saved")
figure("fig05_energy_co2_scatter.png", "Energy consumption against CO2 saved per record (log-log), by mode, with fitted lines.")
shots([19])
para(f"Sustainability leads need to understand which modes are translating energy into carbon savings. A scatter represents the relationship, as well as the spread of the relationship, and the log axes indicate a near-linear relationship over three orders of magnitude. The {V5['rows_excluded_zero_kwh']} zero-energy Bike Share records are not included.", "Purpose and design.")
para(f"The network saves {V5['network_co2_per_kwh']} kg of CO2 per kWh. Metro saves {V5['modes']['Metro']['co2_per_kwh']} kg, Park and Ride {V5['modes']['Park and Ride']['co2_per_kwh']} kg and Tram {V5['modes']['Tram']['co2_per_kwh']} kg. Bus saves {V5['modes']['Bus']['co2_per_kwh']} kg, the lowest amount among the energy-reporting modes, but accounts for {V5['bus_share_energy_pct']}% of all the energy used.", "What it shows.")
para("Energy efficiency of the bus fleet should be a priority for sustainability investment.", "Implication.")

h2("2.8 Visual 6: the shape of unit economics")
figure("fig06_unit_economics_violin.png", "Split violins of revenue and cost per passenger by mode (log scale), with quartiles.")
shots([21])
para("The question is: is the margin based on price, or is it based on cost? Split violins show full distributions, which would be masked by a bar of averages (Healy, 2018).", "Purpose and design.")
para(f"Costs vary widely and fares are in narrow bands. Between modes, the margin gap follows fares: the median fare is €{V6['modes']['Park and Ride']['rev_pp_median']} for Park and Ride and €{V6['modes']['Bus']['rev_pp_median']} for Bus. The cost per passenger in Bus varies between €{V6['modes']['Bus']['cost_pp_min']} and €{V6['modes']['Bus']['cost_pp_max']}, and the fares vary between €{V6['modes']['Bus']['rev_pp_min']} and €{V6['modes']['Bus']['rev_pp_max']}, with {V6['modes']['Bus']['loss_record_pct']}% of Bus records losing money.", "What it shows.")
para("Fare policy helps to create a difference between modes, but for Bus the fastest lever is cost per passenger.", "Implication.")

h2("2.9 Visual 7: what sets city cost recovery")
figure("fig07_city_recovery_lollipop.png", "Cost recovery by city for all modes and mass transit only, and micromobility share of cost.")
shots([23])
para("Investment boards should have an idea of whether loss-making cities have weak core networks or not. Two markers are used for each city to indicate the impact of micromobility, and an aligned bar panel displays the share of costs for micromobility.", "Purpose and design.")
para(f"Overall, {V7['cities_net_loss']} out of {D['cities']} cities suffer a net loss; Paris is narrowly missing break-even ({V7['paris_recovery_2dp']}%). Every city recovers {V7['mass_recovery_min']}% to {V7['mass_recovery_max']}% without micromobility. Micromobility's percentage of city cost varies between {V7['micro_share_min']}% in {V7['micro_share_min_city']} and {V7['micro_share_max']}% in {V7['micro_share_max_city']} and is inversely correlated with recovery at r = {V7['corr_micro_share_vs_recovery']}. Part of that link is arithmetic, with only {D['cities']} cities and micromobility recovering so little of its cost. It is an association and not evidence of cause.", "What it shows.")
para("City funding discussions should consider micromobility as a separately funded service.", "Implication.")

h2("2.10 Visual 8: an accessibility priority matrix")
figure("fig08_accessibility_matrix.png", "Complaints volume (log) against complaints per 1,000 passengers for 72 city-mode services.")
shots([25])
para(f"Accessibility teams should distinguish between services that have a lot of complaints and those that have lots of complaints in relation to their use. There are four action groups when splitting at the median volume ({V8['median_volume']:,.0f}) and the network rate ({V8['network_rate']} per 1,000).", "Purpose and design.")
para(f"In the act-first quadrant, {V8['n_high_high']} services were located and {V8['high_high_by_mode']['Bus']} of these were Bus, which is the Bus service in every city. Only {V8['metro_combos_above_rate']} Metro service (Berlin) is represented there, so the high number of complaints in Metro is primarily related to the number of passengers. Small E-Scooter services in Hamburg ({V8['top_rate'][0][2]}) and Milan ({V8['top_rate'][1][2]}) have the highest rates.", "What it shows.")
para("The primary accessibility programme should be Bus, with the E-Scooter hotspots being local fixes.", "Implication.")

h2("2.11 Visual 9: mode profiles at a glance")
figure("fig09_mode_radar.png", "Radar small multiples scoring each mode from 0 (worst) to 1 (best) on five indicators.")
shots([27, 29])
para("Executives would like to see the good and the bad of each mode in one view. Radar charts can provide a brief summary of shape but can be misleading about area (Few, 2005), so the radar is only used as an overview, in conjunction with the headline table above.", "Purpose and design.")
para(f"Bus has the smallest shape. Bike Share leads on punctuality ({V9['Bike Share']['on_time']}%) and rating ({V9['Bike Share']['rating']}), but recovers just {V9['Bike Share']['recovery']}% of its costs. Park and Ride ({V9['Park and Ride']['recovery']}%) and Tram ({V9['Tram']['recovery']}%) lead on cost recovery. The lowest score of Metro is {V9['Metro']['lowest_scaled_score']}, meaning that Metro does not reach the bottom of any axis.", "What it shows.")
para("There is no one mode that is best at all things, and investment decisions have to be based on trade-offs that are made openly.", "Implication.")

h2("2.12 Interactive dashboard")
para("The dashboard was created using Streamlit (Streamlit, 2026; Appendix B). It is based on the overview, zoom and filter, details-on-demand pattern (Heer and Shneiderman, 2012). All views share seven sidebar filters (dates, country, city, mode, route type, weather and event day). Six KPI cards compare the selection to the network, and five tabs correspond to the decision areas identified in the brief: route planning, reliability, sustainability, accessibility and investment. Plotly charts display exact values when hovered over, and captions are dynamically updated from the filtered data.")
figure("dash_01_overview_route.png", "Dashboard default view: KPI cards and Route planning tab.", 6.3)
figure("dash_06_filtered.png", "Dashboard filtered to Bus on event days, Reliability tab.", 6.3)

h1("3. Part B: Reflective Report (Task 2)")
h2("3.1 Reaching technical and non-technical readers")
para("The visuals are sequenced: reliability, demand, money, carbon and accessibility, then a summary. Each chart has a simple title, direct labels and one implication, for non-technical managers. Lines, dumbbells and lollipops were selected because these are familiar shapes and readers judge position more accurately than area or angle (Cleveland and McGill, 1984; Ware, 2021). Technical readers get indexed values, log scales, fitted lines, quartiles and record counts. Cairo (2016) contends that a truthful chart should be honest about scale and uncertainty, so thin data, like monthly E-Scooter records, is flagged and not hidden. Each mode keeps one colour throughout, and titles explain highlight colours without relying on cultural readings of red and green.")
para("Some choices come at a cost. Log scales and the radar chart are more difficult for non-technical readers, therefore each has a plain caption and the radar chart is not used as the only evidence. Absolute size is not displayed when values are indexed, so the text always contains the actual values. A dashboard also requires more from the people using it than a static report; that is why the default view is meant to answer the basic questions without any filters.")

h2("3.2 Key findings")
bullet(f"In each mode, {V2['city_top2'][0]} and {V2['city_top2'][1]} are the leading cities. Weekend records are {V2['weekend_drop_pct']}% quieter and event days are {V3['uplift_min']}% to {V3['uplift_max']}% busier.", "Demand.")
bullet(f"In all {V1['months']} months, Bus is last, and snow costs every mode {W['snow_drop_min']}-{W['snow_drop_max']} on-time points.", "Delays.")
bullet(f"In all cities, mass transit recovers {V7['mass_recovery_min']}% to {V7['mass_recovery_max']}% of its costs. The cost share of micromobility is related to city deficits (r = {V7['corr_micro_share_vs_recovery']}).", "Cities, cost and revenue.")
bullet(f"The mean ratings are {W['rating_clear']} in clear weather and {W['rating_snow']} in snow, with all Bus services being accessibility priorities.", "Customers and accessibility.")
bullet(f"Bus saves {V5['modes']['Bus']['co2_per_kwh']} kg of CO2 per kWh, against Metro's {V5['modes']['Metro']['co2_per_kwh']} kg.", "Sustainability.")

h2("3.3 Dashboard effectiveness")
BE = F["dashboard_example_bus_event"]
para(f"Since one set of filters affects each view, a manager can pose a question without an analyst. Filtering to Bus on event days (Figure {state['fig']}) results in {BE['records']} records, {BE['on_time']}% of which were on time, {abs(BE['on_time_gap_vs_network'])} points lower than the network, and a mean rating of {BE['rating']}. The default KPI values were the same as the notebook's. The dashboard also has its limits. In that view, some months have only {BE['min_month_records']} records, and heavy filtering leaves small samples. It has not been tested by managers yet, and it reads a static file rather than live data. The next step is user testing, which is recommended by Few (2006), who argues that dashboards work when they are tested and adapted to use.")

h2("3.4 Recommendations and strategic decisions")
table("Recommendations with evidence, owners and measures",
      ["#", "Evidence", "Action", "Owner", "Measure", "When"],
      [["1", f"Bus last in all {V1['months']} months and in every city's priority quadrant", "Bus reliability and step-free access programme", "Head of Bus", "Bus on-time %, complaints per 1,000", "0-12 months"],
       ["2", f"Micromobility cost share against recovery, r = {V7['corr_micro_share_vs_recovery']}", "Fund micromobility separately; watch Munich, Milan, Amsterdam", "Finance Director", "City cost recovery", "6-18 months"],
       ["3", f"Event uplift up to {V3['uplift_max']}%, no fare premium", "Add Metro and Park and Ride event capacity; trial event fare", "Network Planning", "Event revenue per passenger", "0-6 months"],
       ["4", f"Weekends {V2['weekend_drop_pct']}% quieter, no punctuality gain", "Move weekend capacity to Bus", "Timetabling", "Weekend cost per passenger", "6-12 months"],
       ["5", f"Snow costs up to {W['snow_drop_max']} on-time points", "Winter resilience plan for all modes", "Operations", "Snow-day on-time %", "6-12 months"],
       ["6", f"Bus {V5['modes']['Bus']['co2_per_kwh']} kg CO2 per kWh against Metro {V5['modes']['Metro']['co2_per_kwh']}", "Bus energy efficiency in capital plan", "Fleet", "CO2 saved per kWh", "12-36 months"]],
      [0.25, 1.6, 1.75, 0.95, 1.15, 0.8], count=True)
para("The actions are divided into three groups. The quick win (3) safeguards event income. Service changes (1, 4 and 5) shift capacity to the weakest service and prepare the network for winter. Funding decisions (2 and 6) decide how to pay for micromobility and decarbonise the bus fleet. Because the data shows association and not cause, each action should start as a pilot and be evaluated on its dashboard measure.")

h2("3.5 Wider value of visualisation")
para("For the business, the city lollipop translates a deficit into a specific question which can be funded. Socially, the accessibility matrix places complaints next to the finances, where they cannot be traded away unseen. Environmentally, the energy scatter relates fleet selection to carbon outcomes, following the EU urban mobility framework (European Commission, 2021) and Sustainable Development Goal 11 (United Nations, 2015). In the public sector, decisions must be communicated to councils and citizens, and honest visuals can aid that accountability (Cairo, 2016). Locally, filtered city views give each city lead evidence for budget discussions, and at the network level the same views enable the board to compare cities equally.")

h2("3.6 Limitations")
para("Data are a sample of records, not a complete daily record, so ratios were used rather than totals. Capital spending may not be included in operating cost, and no significance tests were performed. Several subgroups are also small. The findings should, therefore, inform further research rather than be treated as proof.")

h1("4. Conclusion")
para(f"On average EcoMove's network is stable, but performance is variable beneath. Bus is the common failing, and snow is the main reliability issue. Deficits are associated with micromobility, and demand is clustered in {V2['city_top2'][0]} and {V2['city_top2'][1]} and on weekdays. The visuals and dashboard make these patterns into actions which can be tracked.")

state["section"] = "back"
doc.add_page_break()
doc.add_heading("References", level=1)
refs = [
    "Cairo, A. (2016) The Truthful Art: Data, Charts, and Maps for Communication. Berkeley, CA: New Riders.",
    "Cleveland, W.S. and McGill, R. (1984) 'Graphical perception: theory, experimentation, and application to the development of graphical methods', Journal of the American Statistical Association, 79(387), pp. 531-554.",
    "European Commission (2021) The New EU Urban Mobility Framework. COM(2021) 811 final. Brussels: European Commission.",
    "Few, S. (2005) 'Keep radar graphs below the radar - far below', Visual Business Intelligence Newsletter. Berkeley, CA: Perceptual Edge.",
    "Few, S. (2006) Information Dashboard Design: The Effective Visual Communication of Data. Sebastopol, CA: O'Reilly.",
    "Healy, K. (2018) Data Visualization: A Practical Introduction. Princeton, NJ: Princeton University Press.",
    "Heer, J. and Shneiderman, B. (2012) 'Interactive dynamics for visual analysis', Communications of the ACM, 55(4), pp. 45-54.",
    "Kirk, A. (2019) Data Visualisation: A Handbook for Data Driven Design. 2nd edn. London: SAGE.",
    "Nuñez, J.R., Anderton, C.R. and Renslow, R.S. (2018) 'Optimizing colormaps with consideration for color vision deficiency to enable accurate interpretation of scientific data', PLOS ONE, 13(7), e0199239.",
    "Streamlit (2026) Streamlit documentation. Available at: https://docs.streamlit.io (Accessed: 13 November 2026).",
    "Tol, P. (2021) Colour Schemes. SRON Technical Note SRON/EPS/TN/09-002, issue 3.2. Utrecht: SRON Netherlands Institute for Space Research.",
    "Tufte, E.R. (2001) The Visual Display of Quantitative Information. 2nd edn. Cheshire, CT: Graphics Press.",
    "United Nations (2015) Transforming Our World: The 2030 Agenda for Sustainable Development. A/RES/70/1. New York: United Nations.",
    "Ware, C. (2021) Information Visualization: Perception for Design. 4th edn. Cambridge, MA: Morgan Kaufmann.",
]
for ref in refs:
    para(ref, count=False, align=WD_ALIGN_PARAGRAPH.LEFT)


def code_block(text):
    for line in text.rstrip("\n").split("\n"):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(line if line else " ")
        r.font.name = MONO
        r._element.rPr.rFonts.set(qn("w:eastAsia"), MONO)
        r.font.size = Pt(8)


doc.add_page_break()
doc.add_heading("Appendix A: Analysis notebook code (COM7021_EcoMove_Analysis.ipynb)", level=1)
nb = nbformat.read(ROOT / "COM7021_EcoMove_Analysis.ipynb", 4)
k = 0
for cell in nb.cells:
    if cell.cell_type == "code":
        k += 1
        h = doc.add_paragraph()
        hr_ = h.add_run(f"Cell {k}")
        hr_.bold = True
        hr_.font.size = Pt(9)
        code_block(cell.source)
        doc.add_paragraph().paragraph_format.space_after = Pt(2)

doc.add_page_break()
doc.add_heading("Appendix B: Streamlit dashboard code (dashboard/app.py)", level=1)
app = ROOT / "dashboard" / "app.py"
code_block(app.read_text(encoding="utf-8") if app.exists() else "dashboard/app.py not found at build time")

doc.add_page_break()
doc.add_heading("Appendix C: Further dashboard screenshots", level=1)
for f, cap in [("dash_02_reliability.png", "Reliability tab, default filters."),
               ("dash_03_sustainability.png", "Sustainability tab, default filters."),
               ("dash_04_accessibility.png", "Accessibility tab, default filters."),
               ("dash_05_investment.png", "Investment tab, default filters.")]:
    if (FIG / f).exists():
        figure(f, cap, 6.3)


from docx.table import Table
from docx.text.paragraph import Paragraph

LABEL = re.compile(r"^(Figure|Table) \d+: |^\d+(\.\d+)*\.? ")
inside, part, text_out = False, None, []
tally = {"Task 1 (Executive Summary, sections 1 and 2)": 0, "Task 2 (sections 3 and 4)": 0}
for el in doc.element.body.iterchildren():
    tag = el.tag.split("}")[1]
    if tag == "p":
        p = Paragraph(el, doc)
        if p.style.name == "Heading 1":
            if p.text.startswith("Executive Summary"):
                inside = True
            elif p.text.startswith("References"):
                inside = False
            if inside:
                part = "Task 2 (sections 3 and 4)" if p.text[:2] in ("3.", "4.") else "Task 1 (Executive Summary, sections 1 and 2)"
        texts = [p.text] if inside else []
    elif tag == "tbl" and inside:
        texts = [c.text for row in Table(el, doc).rows for c in row.cells]
    else:
        texts = []
    for t in texts:
        tally[part] += len(t.split())
        text_out.append(LABEL.sub("", t))
total = sum(tally.values())
for k, v in tally.items():
    print(f"{v:5d}  {k}")
print(f"{total:5d}  TOTAL WORDS (all text from Executive Summary to Conclusion, including headings, captions and tables)")
assert total <= 3000, "over the 3,000-word limit"
assert tally["Task 2 (sections 3 and 4)"] <= 900, "Task 2 over its 900-word allowance"

for t in doc.tables:
    for row in t.rows:
        for c in row.cells:
            for p in c.paragraphs:
                for r_ in p.runs:
                    if "WORDCOUNT" in r_.text:
                        r_.text = r_.text.replace("WORDCOUNT", f"{total:,}")

BODY_TXT.write_text("\n".join(text_out), encoding="utf-8")
doc.core_properties.title = "EcoMove Mobility Visual Investigation"
doc.core_properties.author = "[STUDENT ID]"
doc.save(OUT)
print("saved", OUT)
