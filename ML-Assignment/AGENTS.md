# AGENTS.md

Instructions for any agent or new session working in this folder. Read this file and the memory index first.

## Project
Machine Learning assignment (Maths for Data Science portfolio).

Files:
- `assignquestion (1).pdf` - the assignment questions (source of truth for requirements).
- `Machine learning Assessment Final.pdf` - assessment brief / marking material.
- `assignquestion.csv` - dataset, ~1000 rows. Columns: Item_Name, details, Catatory (sic), price, priceWithCurrency, available, text, sold, lastUpdated, itemLocation. Looks like scraped eBay-style perfume listings. Expect missing values (e.g. empty `price`, `sold`), mixed formats (price strings, "More than 10 available / 116 sold" text, dates with timezone) and a UTF-8 BOM at the start of the file.

Task (COM7022, Arden University): 
- Task 1 (60 marks): cluster the products in `assignquestion.csv` using K-Means, Hierarchical and DBSCAN. Needs cleaning, feature selection with justification, scaling and categorical encoding, PCA, model comparison with validation metrics, best-model justification, cluster profiles with business relevance. Python notebook with clean, commented code.
- Task 2 (40 marks): executive report for non-technical readers: method suitability, model comparison, final model justification, visuals, recommendations.
- Deliverable: one .docx/.pdf, 3000 words total, student ID visible, code in an appendix, screenshots of processes and results, Harvard referencing.
- `Machine learning Assessment Final.pdf` is another student's portfolio on a different problem (flight price regression). Use it only as a structure/style template: Introduction, Methodology (EDA, cleaning, feature engineering), Model development, Results, Critical evaluation, Recommendations, Conclusion, References, Appendix.
- Details are in memory file `assignment-requirements.md`.
- Report layout to copy from the reference PDF (cover table, TOC with page numbers, Code/Output screenshot blocks, Arden logo header, "N | Page" footer) is in memory file `reference-format.md`.
- Build tooling: use `.venv\Scripts\python` (global Python is broken). `build/build_notebook.py` creates and runs the notebook; `build/build_report.py` creates the Word report. Code cells must contain no comments.

Status: requirements extracted; no data analysis or code written yet. Update this section as that changes.
- PDF text extraction: the Read tool cannot render PDFs here (no poppler); use `python -m pip install pypdf` and extract text to the scratchpad.

## Session start checklist
1. Read this file.
2. Read `MEMORY.md` in the memory directory: `C:\Users\Raza\.claude\projects\d--Maths-for-Data-Science-Portfolio-ML-Assignment\memory\`.
3. Check the status line above and the memory entries before starting work.

## Memory rule (mandatory)
After EVERY update or change (new file, edit, decision, finding, completed step), update memory:
- One fact per file in the memory directory, with frontmatter (`name`, `description`, `metadata.type`).
- Add or update a one-line pointer in `MEMORY.md`. Update existing entries instead of duplicating; delete wrong ones.
- Do not record what the code or files already show; record decisions, progress, user preferences, and non-obvious findings.

## Subagent rules
- Delegate small, well-scoped tasks (reading a PDF section, cleaning one column, running one experiment) to subagents.
- Allowed models: `sonnet` (Sonnet 5.5) or `haiku` (Haiku 5.5) only. Use haiku for simple lookups/extraction, sonnet for analysis and code. Do not use other models unless the user says so.
- Brief each subagent fully: goal, input file paths, expected output format, what is already ruled out. Do not tell it your hypothesis as fact.
- Verify subagent output before relying on it, then record the result in memory.
- Subagents must not edit this file or the memory index; the main session does that.

## Working conventions
- Never modify the original PDFs or `assignquestion.csv`. Write cleaned data and outputs to new files (e.g. `data/`, `outputs/`, notebooks in `notebooks/`).
- Open the CSV with `encoding="utf-8-sig"`.
- Keep work reproducible: fixed random seeds, scripts/notebooks that run top to bottom.
- Report results honestly, including failures and skipped steps.
- Platform is Windows; use forward slashes or quote paths (the folder name has spaces).
- Ask the user before any outward-facing or hard-to-reverse action.

## Changelog
- 2026-11-01: AGENTS.md created; memory initialised.
