# COM7023 — Maths for Data Science Portfolio

Repository for our Arden University assignment (Urban Resource Intelligence scenario).
We use **spec-driven development**: everything we build follows one plan file — `spec.md`.

---

## 📁 What's in this repo

| File / Folder | What it is |
|---|---|
| `spec.md` | **The plan.** Tasks, deliverables, timeline, rules. Read this first. |
| `report.docx` | The main report we will submit. |
| `code_explanation.docx` | Plain-English notes explaining every code block and solution step. |
| `code/` | Python scripts, one per task. |
| `Mathematics_for_Data_Science__COM7023.pdf` | The official assignment brief. |
| `final_Assessment_for_mathematics.docx` | Old demo report — **use only for structure/style, NOT content** (it's a different scenario). |

---

## 🧭 What is spec-driven development? (simple version)

Instead of jumping straight into work, we wrote a **spec** (specification) first.
The spec is the single source of truth. Rules:

1. **Never start work without reading `spec.md`.**
2. If the spec and your idea disagree → **the spec wins** (or we update the spec together first).
3. After finishing anything, check it against the **Definition of Done** checklist at the bottom of the spec.
4. Every task updates **three things together**: the code, the report, and the explanation doc. Never just one.

Think of the spec as the contract between us, and between us and the AI.

---

## 🤖 How to use the spec with an AI agent (Claude, etc.)

The AI should always read the spec **before** doing anything. Start every new session with a prompt like this:

### ✅ First prompt (copy-paste this)

```
I'm working on the COM7023 Maths for Data Science assignment.
Please read spec.md in this project first — it defines the scenario,
the four tasks, the deliverables, the session plan, and the rules.

Follow the spec exactly. We are currently on Session [1/2/3].
Today we will work on [Task X].

For each task, follow the workflow in the spec:
solve the maths step by step, write clean commented Python
(seaborn first, matplotlib if needed), generate the figure,
then help me update report.docx and code_explanation.docx.

Do not use content from the old demo report — only its structure.
Explain everything simply so I fully understand each step,
because I need to be able to explain this work myself.
```

### Tips for working with the AI

- Do **one task per conversation session** — keeps things focused.
- Always ask it to **verify hand calculations with Python** (numbers must match).
- If output doesn't match the spec (wrong library, too complicated, wrong figure style), point at the spec section and ask it to redo.
- Ask "explain this like I'm not a maths person" — the report audience is non-technical stakeholders.

---

## ✍️ Writing workflow (important — read this)

The AI helps with **maths, code, figures, and structure**. The **report text is written by us**.

The workflow is:

1. AI solves the task and explains it until you genuinely understand it.
2. AI gives you **rough working notes** (numbers, logic, bullet points) — not polished paragraphs.
3. **You write the report section yourself**, in your own words, from those notes.
4. You update `code_explanation.docx` in your own words too — this file is your proof to yourself that you understand every step.
5. Cite all textbook sources in Harvard style. Never copy sentences from books or the demo report.

### ⚠️ About AI detection and plagiarism tools

We are **not** using paraphrasing tools or any tricks to hide AI use. Two reasons:

- Those tricks don't reliably work, and getting flagged for AI misconduct on a module worth 100% of the grade can mean failing it.
- The only method that actually protects you is the honest one: **write the final text yourself and understand it well enough to explain it out loud** if a tutor asks.

Also: read **Arden's Statement on the Use of AI in Assessment** (linked in the brief). If our programme requires disclosing AI assistance, we disclose it. Honest and safe beats risky every time.

---

## 🗓️ Session plan (from spec.md)

| Session | Work |
|---|---|
| 1 (50%) | Task 1 (Linear Algebra) + Task 2 (Calculus) + document skeletons |
| 2 (25%) | Task 3 (Probability) + Task 4 (Statistics) |
| 3 (25%) | Stakeholder section, critical evaluation, intro/conclusion, references, appendix, polish |

---

## ✅ Quick checklist before you say "done" on any task

- [ ] Maths solved by hand-style working AND verified in Python
- [ ] Code runs cleanly and regenerates the figure
- [ ] Figure is simple, labelled, seaborn-styled
- [ ] Report section updated (theory → solution → screenshot → figure → interpretation)
- [ ] `code_explanation.docx` updated in your own words
- [ ] You can explain the whole task out loud without notes

Full checklist: see **Definition of Done** in `spec.md`.
