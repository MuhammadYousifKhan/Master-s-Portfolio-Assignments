# Data-Visualization-2: rules for every agent

This is the COM7021 Data Visualisation assessment (Arden University). Its inputs are:
- the brief: `[5442] - Data Visualisation - COM7021.pdf`
- the dataset: `[5442] EcoMoveMobility.xlsx`

Do not modify either file.

## Rule 1: must not look like Data-Visualization-1
`../Data-Visualization-1/` is a classmate's submission for the **same brief and dataset**. DV2 must look clearly different side by side.

- **Allowed to be the same:** Python, pandas, matplotlib, plotly and Streamlit (the user chose Streamlit).
- **Must differ:** figures, chart types, variables and groupings, captions, descriptions, report wording, headline insights, report styling and dashboard layout.
- Never reword DV1 text. Write fresh.

**DV1 do-not-repeat list** (do not use these as the core of any DV2 chart or finding):
- **Charts:**
  - bars of city passengers (coloured by country), mode passengers, delay, rating, CO2, revenue vs cost and complaints
  - monthly passenger-total line
  - delay box plot by mode
  - delay vs rating scatter
  - 10-variable correlation heatmap
  - diverging net revenue by mode
  - CO2 share vs passenger share, and CO2 per passenger
  - heatmaps of mode×weather delay and route×mode complaints per 100k
- **Insights:**
  - Metro has 63% of passengers and 70% of CO2
  - Bus is worst on delay (6.58 min)
  - delay–rating r = −0.82
  - micromobility loses €8.88M
  - Snow delay is 8.14 vs Clear 3.71
  - event days add about 1.3 min delay
  - Suburban Feeder complaint anomaly
  - annual decline is a record-count artefact
  - seasonality: April vs October
- **Dashboard:** single selects, 4 KPI cards, default `st.bar_chart`/`st.line_chart`, 20-row table, CSV download.
- **Style:** hand-typed contents page, Okabe-Ito palette, a "Decision use:" line closing each chart section. (Times New Roman is allowed: on 2026-11-13 the user asked for the Word report to use the same Arden house style as the ML report.)

## Rule 2: strictly factual
- Every number in the report must come from `build/facts.json`, which `build/facts.py` computes from the real data.
- `build/check_numbers.py` must pass before the report counts as done.
- Do not invent data, insights or references. If the data does not show an expected pattern, report what it does show.

## Rule 3: subagents
Use `sonnet` or `haiku` for routine subagent work. Subagents must not edit this file.

## Pipeline (run from this folder with `.venv\Scripts\python`)
1. `build/facts.py` → `build/facts.json`
2. `build/build_notebook.py` → `COM7021_EcoMove_Analysis.ipynb` (executed) and `figures/fig*.png`
3. `streamlit run dashboard/app.py`, then `build/shoot_dashboard.py` → `figures/dash_*.png`
4. `build/render_shots.py` → `build/assets/code_*.png` and `out_*.png`
5. `build/build_report.py` → `COM7021 Data Visualisation Report.docx`
6. `build/check_numbers.py`

## Status
- **2026-11-13:** the first full build is complete.
- **2026-11-13:** the report was checked against the brief and every gap fixed.
  - Every notebook step now has a Code/Output screenshot box in the body.
  - Visual 1 adds a weather panel, plus the on-time vs delay-minutes correlation (r = -0.97).
  - Visual 2 adds a city-by-mode demand panel, which also covers countries.
  - Streamlit is now cited in the text.
  - Task 2 was trimmed.
  - The report is 2,817 words counting all headings, captions and tables, which matches Word's own count: Task 1 is 1,951 of 2,100 and Task 2 is 866 of 900 (after the academic-humanizer pass).
- **2026-11-13:** the user's external paraphrase was applied to the prose only (Visual 1 to the Conclusion), with factual fixes; headings, captions and tables were kept. The report is now 2,984 words: Task 1 is 2,092 of 2,100 and Task 2 is 892 of 900. It is 45 pages, and `check_numbers.py` passes.
  - The report is 45 pages, and `check_numbers.py` passes.
- `build_report.py` counts every word from the Executive Summary to the Conclusion as it appears in the finished document, and fails if the total is over 3,000 or Task 2 is over 900. The user confirmed that the marker counts captions, headings and table text.
- Still for the user to do:
  - fill in `[STUDENT ID]`, `[TUTOR NAME]` and the Programme Name (cover and notebook)
  - decide on the AI-use disclosure
- After any change to `facts.py`, `build_notebook.py` or `build_report.py`, rerun the pipeline from step 1. Then update the contents list in Word.

## Conventions
- Notebook code cells have no comments.
- Figures are 150 dpi PNGs, using the Paul Tol colour-blind-safe palette and cividis for sequential scales.
- Compare groups with per-record means or ratios, because row counts differ by group.
- The report body must be 3,000 words or fewer. It uses a Word TOC field and Harvard referencing.
- The Word report copies the ML report's house style (`../ML-Assignment/build/build_report.py`): US Letter, Times New Roman 11 pt justified, black H1 and blue (#2E6FB5) H2/H3, Arden logo top right, "N | P a g e" footer, the one-column Arden cover table, "Table of Contents", centred "Figure N:"/"Table N:" captions, navy (#1F3A5F) table headers and boxed Code/Output screenshots. Do not reintroduce other colours or layouts.
- The cover shows `[STUDENT ID]` and `[TUTOR NAME]` placeholders until the user provides the values.
