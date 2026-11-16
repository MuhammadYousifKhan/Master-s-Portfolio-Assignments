# Data Science Portfolio: Assignments

Worked solutions for four Data Science assessments from the Data Science programme at Arden University. Each folder is self-contained: the brief, the data, the Python code, the figures and the finished Word report.

The repository is shared as a **reference** for how to structure and carry out this kind of work: cleaning and exploring data, choosing and justifying methods, building figures and dashboards, and writing the findings up for a non-technical reader.

> **Academic integrity.** Use this work to learn the approach, then do your own analysis and write your own report. Submitting any of it, in whole or in part, as your own assessment would breach your institution's academic integrity rules. If you are on one of these modules, reuse the method, not the wording, figures or findings.

## What is in the repository

| Folder | Module | Topic | Main tools |
|---|---|---|---|
| [`DS-Assignment/`](DS-Assignment) | COM7023 Mathematics for Data Science | Four tasks: linear algebra, calculus, probability and statistics, applied to an urban resource scenario | NumPy, SciPy, SymPy, pandas, statsmodels, seaborn |
| [`ML-Assignment/`](ML-Assignment) | COM7022 Machine Learning | Customer-style segmentation of about 1,000 online perfume listings using K-Means, hierarchical clustering and DBSCAN | pandas, scikit-learn, seaborn |
| [`Data-Visualization-1/`](Data-Visualization-1) | COM7021 Data Visualization | Static figures and a Streamlit dashboard on the EcoMove city-transport dataset (5,000 service records, 12 cities) | pandas, matplotlib, seaborn, Streamlit |
| [`Data-Visualization-2/`](Data-Visualization-2) | COM7021 Data Visualization | A second, independent treatment of the same EcoMove brief, with a different set of charts and a different dashboard layout | pandas, matplotlib, Plotly, Streamlit |

## How to read each folder

### `DS-Assignment/`
- `spec.md`: the plan the work followed (tasks, deliverables, rules).
- `code/`: one script per task (`task1_linear_algebra.py` to `task4_statistics.py`).
- `figures/`: the plots the scripts produce.
- `final Report.docx` and `code_explanation.docx`: the report and a plain-English walk-through of the code.
- `README.md` inside the folder describes the workflow in more detail.

### `ML-Assignment/`
- `assignquestion.csv`: the dataset. `assignquestion (1).pdf` is the brief.
- `COM7022_Task1_Clustering.ipynb`: the full notebook (cleaning, feature selection, scaling, PCA, the three clustering methods, validation metrics, cluster profiles).
- `clustered_products.csv`: the dataset with each listing's final cluster label.
- `figures/`: the charts used in the report.
- `COM7022 Assignment Report.docx`: the executive report. `Final Assignment.docx` is the latest renamed copy.
- `build/`: the scripts that generate the notebook, the report and the screenshots.

### `Data-Visualization-1/`
- `assignquestion.xlsx`: the dataset.
- `EcoMove_Analysis.py`: loads, cleans and validates the data, prints the statistics quoted in the report and saves the nine figures into `figs/`.
- `app.py`: the Streamlit dashboard (city, mode and date filters, KPI cards, charts, filtered table and CSV download).
- `EcoMove_Data_Visualisation_Report_IEEE.docx`: the report with IEEE-style references. `..._FINAL.docx` is the earlier version.
- `outputs/`: run logs, the code and output screenshots used in the report, and backups.

### `Data-Visualization-2/`
- `[5442] EcoMoveMobility.xlsx` and the PDF brief: the inputs.
- `src/ecomove.py`: shared loading and cleaning code.
- `COM7021_EcoMove_Analysis.ipynb`: the analysis notebook.
- `dashboard/app.py`: the Streamlit dashboard.
- `figures/`: static figures and dashboard screenshots.
- `build/`: scripts that build the notebook and report and check every number quoted in the text against the data (`facts.json`).
- `COM7021 Data Visualisation Report.docx`: the report.

## Running the code

You need Python 3.10 or newer. Create a virtual environment per folder so the dependencies stay separate.

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
```

**DS-Assignment**
```bash
cd DS-Assignment
pip install -r requirements.txt
python code/task1_linear_algebra.py
```

**ML-Assignment** (no requirements file; install what the notebook imports)
```bash
cd ML-Assignment
pip install pandas numpy scikit-learn scipy matplotlib seaborn jupyter
jupyter notebook COM7022_Task1_Clustering.ipynb
```
Run the notebook from inside `ML-Assignment/` so it can find `assignquestion.csv`.

**Data-Visualization-1**
```bash
cd Data-Visualization-1
pip install pandas numpy matplotlib seaborn openpyxl streamlit
python EcoMove_Analysis.py     # writes figures to ./figs
streamlit run app.py           # opens the dashboard
```
Run both from inside the folder so `assignquestion.xlsx` is found.

**Data-Visualization-2**
```bash
cd Data-Visualization-2
pip install -r requirements.txt
streamlit run dashboard/app.py
```
The dashboard locates the workbook relative to its own folder, so it can be started from `Data-Visualization-2/`.

## Suggested way to use this as a reference

1. Read the brief in the folder, then try the task yourself first.
2. Compare your approach with the notebook or scripts: how the data was checked, which methods were picked and why.
3. Look at the report for how results are explained to a non-technical reader: a claim, the figure that supports it, and what a manager should do about it.
4. Check the figures against the data. Numbers in the reports come from the scripts, not from estimates.

## Notes

- Word reports are binary files; open them in Word or LibreOffice.
- Dataset files belong to the module and are included only so the code runs. They are not for redistribution.
- The `build/` folders hold helper scripts used to produce the reports. They are not needed to run the analysis.
