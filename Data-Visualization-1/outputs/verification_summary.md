# EcoMove report verification (generated 2026-11-15)

Environment: Python 3.13.9 (Anaconda). pandas 2.3.3, openpyxl 3.1.5, matplotlib 3.10.6, seaborn 0.13.2, streamlit 1.51.0 were already installed. No venv needed.

## Scripts
- EcoMove_Analysis.py ran with zero errors/warnings and no edits. 9 figures written to figs/ (fig1..fig9). Log: outputs/analysis_run_log.txt
- app.py loads (HTTP 200, health "ok"). Headless AppTest: 7 filter scenarios (default, Milan, Park and Ride, Milan+P&R, 2025 only, Milan+P&R+H1-2024, start>end) - KPI cards equal an independent pandas recompute in all 7; 5 charts render with no exceptions; empty selection shows 0 / N/A with no crash; start>end shows the warning.
- Only warning: `use_container_width` is deprecated in Streamlit (app.py line 193). Still works in 1.51. Fix if wanted: `use_container_width=True` -> `width="stretch"` (but then Appendix B no longer matches app.py).

## Numbers in the report vs data
All quantitative claims checked (about 150 figures) match the data. Differences found:
1. Sec 3.3.8: "effect ... is largest for bike share (1.1 to 4.9 minutes) and metro (3.0 to 7.5)". Values are right, but the claim is not. Absolute rise from Clear to Snow: Park and Ride +4.92, Tram +4.92, Metro +4.42, Bus +4.40, Bike +3.75, E-Scooter +3.75. Relative rise: Bike 4.4x, E-Scooter 3.9x, Metro 2.5x. Metro is not top-2 on either basis.
2. Header says "Word Count: 2750". Measured: Exec Summary to Conclusion = 2,997 incl. headings and captions; 2,823 excl. captions; 2,705 excl. captions and headings. None equals 2750. Adding references (294 words) would give 3,291.
3. Sec 3.3.9 "51,600 passengers" is 51,558 (rounding, acceptable).
Not wrong but loose: "3.5 to 4.5 times" (actual 3.5x-4.5x depending on baseline, ok).

## Non-numeric problems seen
- Student number is still "[ENTER YOUR STUDENT NUMBER]" in the title table and page header.
- Many commas/hyphens missing in the text; garbled sentences: 4.2 "No user testing with managers was done,." ; 4.3 "No significance. Confidence intervals were made." and "distributionsre multimodal"; Conclusion "limitations were."; 4.1 "attention before reading (2014)" (author missing); references "2Nd edn", "And McGill".
- Body heading reads "CONCLUSION" without the "5." that the TOC shows.
- Figures 1-3 screenshots come from a Jupyter notebook (df_clean, display(), literal "\\n" in print strings), not from the submitted script; Figs 13-15 show a Windows "Activate Windows" watermark and are very small text.
- Fig 13 monthly chart was captured mid-render (stray bars).
- Appendix A and B are identical to EcoMove_Analysis.py and app.py (whitespace-insensitive).
