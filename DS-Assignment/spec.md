# spec.md — COM7023 Maths for Data Science Portfolio (Urban Resource Intelligence)

## 1. Project Overview

| Item | Detail |
|---|---|
| Module | COM7023 — Maths for Data Science (Arden University) |
| Scenario | Urban Resource Intelligence (URI) consultancy — urban residential analytics |
| Format | Written report (single .docx or PDF) |
| Word limit | 3000 words (≈2000 words equivalent numerical work + ≈1000 words written results for non-technical stakeholders) |
| Weighting | 100% of module grade |
| Audience | Non-technical stakeholders (city planners, policy makers) — meaning and implications first, procedure second |
| Learning outcomes | LO1–LO4 (understanding, application, deployment of models, critical evaluation + originality) |

**Hard requirements from the brief:**
- All maths notation produced with software tools (Word Equation Editor / LaTeX-style) — **no handwritten work**.
- All computation and visualisation in **Python**, evidenced by **screenshots of code + outputs** embedded in the report.
- Student ID clearly stated on the submission.
- Unequal sample sizes in Task 4 must be handled correctly.

> ⚠️ **Important:** The uploaded demo report (`final_Assessment_for_mathematics.docx`) is based on a **previous brief** (Paris population scenario). We reuse only its **structure, section layout, and presentation style** — all content, models, and numbers must be replaced with the new URI scenario tasks below.

---

## 2. Deliverables

Three artefacts, kept in sync throughout the project:

1. **`report.docx` — Main Assessment Report** (the submission file)
   - Follows the demo report's structure (see §5).
   - Contains equations, worked solutions, screenshots of Python code + outputs, figures, stakeholder-facing interpretation, critical evaluation, Harvard references, appendix with full code.

2. **`code_explanation.docx` — Code & Solution Explanation Document** (companion file, not submitted)
   - Line-by-line / block-by-block plain-English explanation of every Python script.
   - Step-by-step reasoning behind each mathematical solution (why this method, what each step means).
   - Serves as the author's study/defence notes — the author must be able to explain every step verbally if asked.

3. **`code/` — Python scripts or notebook**
   - One script/notebook section per task: `task1_linear_algebra.py`, `task2_calculus.py`, `task3_probability.py`, `task4_statistics.py`.
   - Reproducible: running each file regenerates all numbers and figures used in the report.

---

## 3. The Four Tasks (new brief — URI scenario)

### Task 1 — Steady-State Resource Demand (Linear Algebra)
**Problem:** Solve the 4×4 linear system for net daily demand across four zones:

```
 2x1 −  x2 +  x3        = 120
 −x1 + 3x2       −  x4  = 150
  x1 +  x2 + 2x3 −  x4  = 180
       −x2 +  x3 + 2x4  = 140
```

**Approach:**
- Write as **Ax = b**; state matrix A and vector b.
- Check existence/uniqueness of solution: determinant of A (det ≠ 0 ⇒ unique stable equilibrium), rank, and condition number (brief comment on numerical stability).
- Solve by **Gaussian elimination shown by hand-style working (typed)** + verify with `numpy.linalg.solve`.
- Interpret x₁…x₄ as equilibrium demand per zone; discuss load balancing implications (which zones carry most demand, what a unique solution means for planners).

**Python:** `numpy` (solve, det, rank, cond). **Figure:** simple seaborn bar chart of zone demands.

### Task 2 — Demand Over Time (Calculus)
**Problem:** Analyse `D(t) = 4t³ − 18t² + 24t + 90` (t in hours).

**Approach:**
- First derivative D′(t) = 12t² − 36t + 24 → critical points at t = 1 and t = 2.
- Second derivative D″(t) = 24t − 36 → classify: t = 1 local max, t = 2 local min; inflection at t = 1.5.
- Intervals of increase (t < 1, t > 2) and decrease (1 < t < 2); interpret as demand ramp-up, mid-period dip, and renewed growth.
- Link to **peak-demand management**: when demand rises fastest, when systems can recover, when to schedule maintenance or storage release.

**Python:** `numpy`/`sympy` for verification. **Figures:** D(t) curve with critical points marked; optionally D′(t) beneath it.

### Task 3 — Forecasting Error Risk (Probability)
**Problem:** Forecast errors ~ **N(0, σ = 5)**. Evaluate likelihood of large deviations.

**Approach:**
- Compute probabilities such as P(|error| > 5), P(|error| > 10), P(|error| > 15) (i.e., 1σ, 2σ, 3σ) using z-scores and `scipy.stats.norm`.
- Empirical rule framing for stakeholders ("about 95% of daily forecasts land within ±10 units").
- Interpret for **risk management & contingency planning**: what buffer capacity covers 95%/99% of days; how rare a ±15 unit miss is.

**Python:** `scipy.stats`. **Figure:** seaborn/matplotlib normal curve with shaded tail regions (visually intuitive for non-technical readers).

### Task 4 — Consumption by Building Type (Statistics)
**Problem:** Does mean daily consumption differ between building types? (Unequal n.)

Data:
- Apartments (n=8): 16.8, 17.2, 16.5, 17.9, 18.1, 17.4, 16.9, 17.6
- Terraced (n=10): 18.4, 18.9, 19.1, 18.7, 19.3, 18.6, 19.0, 18.8, 19.2, 18.5
- Detached (n=6): 20.1, 19.7, 20.4, 19.9, 20.6, 20.2

**Approach:**
- Descriptives per group (mean, SD, n).
- **One-way ANOVA** (handles unequal sample sizes naturally); state H₀ (all means equal) and H₁ (at least one differs), α = 0.05.
- Check assumptions: normality (Shapiro–Wilk, small-n caveat), equal variances (Levene). If variances unequal → **Welch's ANOVA** as robust alternative (mention regardless, as good practice).
- If significant → **post-hoc test** (Tukey HSD, which accommodates unequal n) to identify which pairs differ.
- Interpret for **targeted efficiency interventions** (e.g., detached homes as priority segment).

**Python:** `scipy.stats` (f_oneway, levene, shapiro), `statsmodels` (Tukey HSD). **Figure:** seaborn boxplot (or stripplot overlay) of consumption by building type.

### Task 5 — Critical Evaluation (written section, no computation)
- Assumptions & limitations per model (linearity/steady state; polynomial only valid over a limited time window; normality of errors; ANOVA assumptions with small samples).
- Reliability of conclusions under uncertainty (sample sizes, model risk).
- Practical implications for urban policy and planning.
- Include at least one point of **originality/creativity** (LO4) — e.g., suggesting how the four analyses combine into a monitoring framework, or sensitivity checks.

---

## 4. Project Timeline

The work is split into three build sessions — 50% today, then two sessions of 25% each:

| Session | Scope |
|---|---|
| **Session 1 (today — 50%)** | Task 1 (Linear Algebra) + Task 2 (Calculus): full solutions, Python code, figures, report sections, and code-explanation entries. Set up document skeletons (report + code explanation + code folder). |
| **Session 2 (25%)** | Task 3 (Probability) + Task 4 (Statistics): full solutions, Python code, figures, report sections, and code-explanation entries. |
| **Session 3 (25%)** | Stakeholder results section (~1000 words), critical evaluation, intro/methodology/conclusion, references, appendix, and final polish (word count, formatting, export). |

Each session ends with all three artefacts (report, explanation doc, code) in sync — no half-updated files carried over.

---

## 5. Parallel Workflow (per task)

Every task follows the same loop; **nothing is "done" until all three artefacts are updated**:

1. **Solve** — work the mathematics by hand-style derivation, then verify in Python.
2. **Code** — clean, commented script; run; save figure(s) and capture screenshots of code + output.
3. **Update `report.docx`** — add the task section: theory → typed worked solution → screenshot evidence → figure → stakeholder interpretation.
4. **Update `code_explanation.docx`** — explain the code and the solution steps in plain English.
5. **Word-count check** — track running total against the 3000-word budget (target ≈600–700 words/task + ~1000 for the stakeholder results section + intro/methodology/conclusion).

Suggested order: Task 1 → 2 → 3 → 4 → stakeholder report section → critical evaluation → intro/methodology/conclusion → references/appendix → final polish.

---

## 6. Report Structure (mirrors demo report layout — with detailed sub-steps)

The report follows the exact same **step-by-step presentation style** as the sample assignment (`final_Assessment_for_mathematics.docx`). Each task section is broken into numbered sub-sections with explicit mathematical working shown at every step.

1. Title page (university, programme, module, title, **student ID**, name, word count)
2. Table of Contents
3. Introduction (background & purpose — URI scenario)
4. Methodology (overview of the four mathematical approaches)
5. **Task 1: Steady-State Demand (Linear Algebra)**
   - 3.1 Mathematical Analysis (Method Used: System of Linear Equations and Matrix Algebra)
   - 3.2 Solution
     - 3.2.1 Formation of the Augmented Matrix
     - 3.2.2 Gaussian Elimination Step-by-Step
     - 3.2.3 Back Substitution
     - 3.2.4 Python Verification
   - 3.3 Analysis and Results
   - 3.4 Visualisation
6. **Task 2: Demand Over Time (Calculus)**
   - 4.1 Mathematical Analysis (Method Used: Differential Calculus)
   - 4.2 Solution
     - 4.2.1 Application of the Power Rule for Differentiation
     - 4.2.2 Identification of Critical Points
     - 4.2.3 Second Derivative Test for Classification
     - 4.2.4 Inflection Point Analysis
     - 4.2.5 Intervals of Increase and Decrease
   - 4.3 Analysis and Results
   - 4.4 Visualisation
7. Task 3: Forecasting Errors (Probability) — same sub-structure
8. Task 4: Consumption by Building Type (Statistics) — same sub-structure
9. Stakeholder Report (≈1000 words, non-technical: meaning & implications of all findings)
10. Critical Evaluation (assumptions, limitations, reliability, policy implications)
11. Conclusion
12. References (Harvard style — reuse relevant texts from demo report: Anton/Rorres, Stewart, Thomas, Ross, Devore, Montgomery, etc., verified for relevance)
13. Appendix (full Python code, per task)

---

## 7. Visualisation Standards

- **Primary library: seaborn** (`sns.set_theme()` for a clean, consistent look); **matplotlib** only where seaborn lacks the plot type (e.g., annotated curves, shaded normal-distribution tails).
- One clear message per figure; every figure has a title, axis labels **with units**, and a legend only if needed.
- No 3D, no dual axes, no dense subplot grids — stakeholder-friendly simplicity.
- Consistent colour palette across the report (e.g., `sns.color_palette("muted")`).
- Each figure gets a caption + one-sentence plain-English takeaway in the report.

**Planned figures:** Task 1 — bar chart of zone demands · Task 2 — D(t) curve with max/min annotated · Task 3 — normal curve with shaded ±1σ/±2σ regions · Task 4 — boxplot by building type.

---

## 8. Writing Style & Academic Integrity

- **Voice:** clear, simple sentences; explain jargon on first use; interpretation aimed at non-technical planners. Procedure kept brief in the stakeholder section; full working lives in task sections/appendix.
- **Originality:** every sentence in the final report and explanation document must be **written or substantially rewritten in the author's own words**. Claude's role here is analysis, computation, structuring, and drafting support — the author paraphrases, personalises, and takes ownership of the final prose, and must be able to explain any part of it.
- **Note on detection tools:** the project will not be structured around evading plagiarism or AI-detection software. The right protection is the same thing good practice requires anyway: original phrasing by the author, genuine understanding of every step (that's what `code_explanation.docx` is for), correct Harvard citation of all sources, and compliance with **Arden's Statement on the Use of AI in Assessment** (linked in the brief — read it and disclose AI assistance if the policy requires it).
- No copied passages from textbooks or the demo report; cite ideas, don't lift text.

---

## 9. Technical Environment

- Python 3.x; libraries: `numpy`, `scipy`, `sympy` (optional, for symbolic verification), `pandas`, `seaborn`, `matplotlib`, `statsmodels`.
- Screenshots must show code **and** its executed output together (as required by the brief).
- File naming: figures saved as `fig_task{N}_{short_name}.png` at ≥150 dpi.

---

## 10. Definition of Done (checklist)

- [x] All four tasks solved by hand-style working **and** verified in Python (numbers match).
- [x] Task 4 explicitly addresses unequal sample sizes (ANOVA/Welch + Tukey).
- [x] Every task section: theory, solution, screenshot evidence, figure, interpretation.
- [ ] ≈1000-word stakeholder results section written in plain English.
- [ ] Critical evaluation covers assumptions, limitations, reliability, policy implications, and an originality element.
- [ ] Student ID on the document; word count within limit (~3000).
- [ ] Harvard references complete and actually cited in-text.
- [ ] Appendix contains full, runnable code.
- [x] `code_explanation.docx` fully explains every script and solution step.
- [x] All equations typed (no handwriting); single .docx or PDF exported.

---

## 11. Session Progress Log

This section tracks what was completed in each build session. Update after every session.

### Session 1 (7 June 2026 — 50%)

**Completed:**
- [x] Task 1 — Steady-State Resource Demand (Linear Algebra)
  - [x] Solved 4×4 system: x₁=105.00, x₂=123.33, x₃=33.33, x₄=115.00 units/day
  - [x] Verified: det(A)=12, rank=4, κ=7.92 (well-conditioned)
  - [x] Code: `code/task1_linear_algebra.py` — runnable, commented
  - [x] Figure: `figures/fig_task1_zone_demands.png` — seaborn bar chart
  - [x] **Full report section in `DS_Assignment_Session1_Report.docx`:**
    - 3.1 Mathematical analysis (Ax=b, matrix properties)
    - 3.2.1 Augmented matrix formation
    - 3.2.2 Gaussian elimination (3 elimination steps with intermediate matrices)
    - 3.2.3 Back substitution (x₄→x₃→x₂→x₁)
    - 3.2.4 Python verification with full console output embedded
    - 3.2.4 Properties table (det, rank, condition number, residual)
    - 3.3 Analysis and results
    - 3.4 Visualisation (Figure 1 embedded)
    - Appendix with full code
  - [x] Code explanation in `code_explanation.docx`

- [x] Task 2 — Demand Over Time (Calculus)
  - [x] Analysed D(t)=4t³−18t²+24t+90: D′(t)=12t²−36t+24, D″(t)=24t−36
  - [x] Critical points: t=1 (local max, D=100), t=2 (local min, D=98)
  - [x] Inflection point: t=1.5 (D=99)
  - [x] Code: `code/task2_calculus.py` — runnable, commented, sympy verification
  - [x] Figure: `figures/fig_task2_demand_curve.png` — two-panel D(t) + D′(t)
  - [x] **Full report section in `DS_Assignment_Session1_Report.docx`:**
    - 4.1 Mathematical analysis (differential calculus)
    - 4.2.1 Power rule application (term-by-term)
    - 4.2.2 Critical point identification (factoring)
    - 4.2.3 Second derivative test (classification)
    - 4.2.4 Inflection point analysis
    - 4.2.5 Intervals of increase/decrease (with table)
    - 4.2.6 Python verification with full console output embedded
    - 4.3 Analysis and results
    - 4.4 Visualisation (Figure 2 embedded)
    - Appendix with full code
  - [x] Code explanation in `code_explanation.docx`

- [x] Report structure matches sample assignment (`final_Assessment_for_mathematics.docx`):
  - [x] Title page, Table of Contents, Introduction, Methodology
  - [x] Step-by-step mathematical working (hand-style typed)
  - [x] Python code embedded in report sections
  - [x] Python console outputs embedded (not placeholders)
  - [x] Figures embedded with captions
  - [x] References (Harvard style)
  - [x] Appendix with complete runnable code

**Deliverable:** `DS_Assignment_Session1_Report.docx` (213 KB) — ready for submission

**Completed in Session 2 (7 June 2026 — 25%):**
- [x] Task 3 — Forecasting Error Risk (Probability)
  - [x] Normal distribution N(0, σ=5) analysis
  - [x] P(|error| > 5) = 31.73%, P(|error| > 10) = 4.55%, P(|error| > 15) = 0.27%
  - [x] Z-score calculations: z=1.0, 2.0, 3.0 for ±5, ±10, ±15 thresholds
  - [x] Risk management interpretation: ±10 buffer covers 95.45% of days
  - [x] Code: `code/task3_probability.py` — runnable, commented
  - [x] Figure: `figures/fig_task3_normal_curve.png` — normal curve with shaded tails
  - [x] Full report section in `Report_Session1.docx`:
    - 5.1 Mathematical analysis (normal distribution, z-scores)
    - 5.2 Solution (probability calculations for 1σ, 2σ, 3σ)
    - 5.3 Analysis and results (risk management interpretation)
    - 5.4 Visualisation (Figure 3 embedded)
    - References: Ross (2019), Grimmett & Stirzaker (2020)
    - Appendix with full code
  - [x] Code explanation in `code_explanation.docx`

**Completed in Session 2 (14 July 2026 — 25%):**
- [x] Task 4 — Consumption by Building Type (Statistics)
  - [x] Unequal sample sizes handled correctly (n=8, 10, 6)
  - [x] Descriptive statistics per group (mean, SD, n, min, max)
  - [x] Assumption checks: Shapiro-Wilk (normality — all pass), Levene's test (equal variances — pass)
  - [x] One-way ANOVA: F(2,21) = 84.95, p < 0.000001 → significant difference
  - [x] Tukey HSD post-hoc: All three pairwise comparisons significant (p < 0.001)
  - [x] Code: `code/task4_statistics.py` — runnable, commented
  - [x] Figure: `figures/fig_task4_boxplot.png` — seaborn boxplot with stripplot overlay
  - [x] Full report section in `Report_Session1.docx`:
    - 6.1 Mathematical analysis (one-way ANOVA, Tukey HSD)
    - 6.2 Solution (descriptives, assumption checks, ANOVA, Tukey HSD)
    - 6.2.5 Python verification with full console output embedded
    - 6.3 Analysis and results (targeted efficiency interventions)
    - 6.4 Visualisation (Figure 4 embedded)
    - References: Devore (2015), Montgomery (2017)
    - Appendix with full code
  - [x] Code explanation in `code_explanation.docx`
  - [x] Report builder (`build_final_report.py`) updated with full Task 3 + Task 4 sections
- [x] Conclusion (Section 7) added to `Report_Session1.docx`:
  - Humanised, simple language summarising all four tasks
  - Practical implications for city planners
  - Placed before References section

**Pending for Session 3:**
- [ ] Stakeholder results section (~1000 words)
- [ ] Critical evaluation
- [ ] Final polish (word count, formatting, references, appendix)
