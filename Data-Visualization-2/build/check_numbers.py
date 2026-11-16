import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
facts = json.loads((HERE / "facts.json").read_text(encoding="utf-8"))
body = (HERE / "report_body.txt").read_text(encoding="utf-8")

values = []


def walk(x):
    if isinstance(x, bool):
        return
    if isinstance(x, (int, float)):
        values.append(abs(float(x)))
    elif isinstance(x, dict):
        for v in x.values():
            walk(v)
    elif isinstance(x, list):
        for v in x:
            walk(v)
    elif isinstance(x, str):
        for m in re.findall(r"\d+(?:\.\d+)?", x):
            values.append(float(m))


walk(facts)

STRUCTURAL = {
    1000: "per 1,000 denominator", 100: "break-even / index base", 11: "SDG 11",
    0: "horizon", 6: "horizon / table row", 12: "horizon / table row", 18: "horizon", 36: "horizon",
    1: "table row / scale", 2: "table row", 3: "table row", 4: "table row", 5: "table row",
    2024: "year", 2025: "year", 2026: "year",
    1984: "citation", 2001: "citation", 2005: "citation", 2006: "citation", 2012: "citation",
    2015: "citation", 2016: "citation", 2018: "citation", 2019: "citation", 2021: "citation",
}

problems, checked = [], 0
for m in re.finditer(r"(?<![A-Za-z])\d[\d,]*(?:\.\d+)?", body):
    raw = m.group(0).rstrip(",")
    x = float(raw.replace(",", ""))
    dec = len(raw.split(".")[1]) if "." in raw else 0
    tol = 0.5 * 10 ** (-dec) + 1e-9
    checked += 1
    if any(abs(x - v) <= tol for v in values):
        continue
    if dec == 0 and int(x) in STRUCTURAL:
        continue
    ctx = body[max(0, m.start() - 50): m.end() + 30].replace("\n", " ")
    problems.append(f"{raw!r}: ...{ctx}...")

print(f"checked {checked} numbers in the report body")
if problems:
    print(f"{len(problems)} number(s) not traceable to facts.json:")
    for p in problems:
        print("  ", p)
    sys.exit(1)
print("PASS: every number is traceable to facts.json or is structural (years, citations, horizons, 1,000/100 bases)")
