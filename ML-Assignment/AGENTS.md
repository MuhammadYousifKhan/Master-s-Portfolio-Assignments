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
- Deliverable: one .docx/.pdf, 3000 words total, student ID visible, code in an appendix, screenshots of processes and results, Harvard referencing (but on 2026-11-15 the user asked for IEEE: numbered [n] citations in order of first use, IEEE reference list; keep IEEE).
- `Machine learning Assessment Final.pdf` is another student's portfolio on a different problem (flight price regression). Use it only as a structure/style template: Introduction, Methodology (EDA, cleaning, feature engineering), Model development, Results, Critical evaluation, Recommendations, Conclusion, References, Appendix.
- Details are in memory file `assignment-requirements.md`.
- Report layout to copy from the reference PDF (cover table, TOC with page numbers, Code/Output screenshot blocks, Arden logo header, "N | Page" footer) is in memory file `reference-format.md`.
- Build tooling: use `.venv\Scripts\python` (global Python is broken). `build/build_notebook.py` creates and runs the notebook; `build/build_report.py` creates the Word report. Code cells must contain no comments.

Status (2026-11-14): the report file is now `COM7022 Assignment Report.docx` (the user renamed v4). It holds direct edits that `build/build_report.py` does not have, so never rebuild it from the script; edit the docx directly. Client feedback applied 2026-11-14: body at 2,996 words (after the 2026-11-14 humanize + partial StealthWriter swap) by Word's own count of everything from "1. Introduction" to the end of the Conclusion (headings, captions, tables and Code/Output labels included; references and appendix excluded); new "Checking for Duplicates" and "Missing Values Before and After Cleaning" Code/Output blocks in 2.3 (notebook cells 7 and 17); new 3.4 "Key Insights and Suggested Improvements". Remaining: student number, programme and tutor on the cover; re-run Turnitin on the rewritten text. Progress details are in memory file `build-progress.md`. Update this section as that changes.
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
- 2026-11-02: Turnitin-flagged passages in sections 2.4-4.2 replaced in v4.docx with the user's StealthWriter text (7 meaning fixes approved by the user); status updated.
- 2026-11-02: second swap, sections 4.2-6 (23 paragraphs, best of two StealthWriter versions plus 8 approved word fixes); TOC refreshed.
- 2026-11-14: client feedback: word count incl. tables/captions/headings cut to 2,971; duplicate check and missing before/after added (notebook + report + appendix); 3.4 added; Campello et al. (2013) reference added; TOC refreshed (36 pages).
- 2026-11-14: /text-humanize pass on all 54 body prose paragraphs (headings, captions, tables, numbers, citations unchanged); body 2,990; cover count 2990; TOC refreshed. Pre-pass backup in that session's scratchpad.
- 2026-11-14: StealthWriter swap from text.txt (lines 1-83 original, 90-172 paraphrase). Paraphrase was +406 words, so per the user only the 18 paragraphs that fit the 3,000 limit were swapped (meaning errors fixed); 36 keep the humanized text. Body 2,996, cover 2996, TOC refreshed. Pre-swap backup in that session's scratchpad.
- 2026-11-15: references and in-text citations converted from Harvard to IEEE ([1]-[9] by first use). Word count (Word, "1. Introduction" to end of Conclusion, incl. headings/captions/tables) = 3,337; the docx was already 3,358 before the change because of the user's own edits.
