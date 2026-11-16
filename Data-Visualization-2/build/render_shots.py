from pathlib import Path

import nbformat
from PIL import Image, ImageDraw, ImageFont
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Token

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "assets"
OUT.mkdir(exist_ok=True)

BG_CODE = (247, 247, 247)
BG_OUT = (255, 255, 255)
BORDER = (207, 207, 207)
DEFAULT = (33, 33, 33)
LABEL = (48, 63, 159)
FONT = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 19)
LABEL_FONT = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 17)
CW = FONT.getlength("M")
LH = 26
PAD = 16
GUTTER = 92
WRAP = 120
MAX_LINES = 46

COLOURS = [
    (Token.Keyword, (0, 128, 0)),
    (Token.Name.Builtin, (0, 128, 0)),
    (Token.Name.Function, (0, 0, 255)),
    (Token.Literal.String, (186, 33, 33)),
    (Token.Literal.Number, (0, 136, 0)),
    (Token.Operator, (170, 34, 255)),
    (Token.Comment, (64, 128, 128)),
]


def colour_for(tok):
    for t, c in COLOURS:
        if tok in t:
            return c
    return DEFAULT


def wrap(segments):
    lines, cur, n = [], [], 0
    for text, col in segments:
        while text:
            room = WRAP - n
            if len(text) <= room:
                cur.append((text, col))
                n += len(text)
                text = ""
            else:
                cur.append((text[:room], col))
                lines.append(cur)
                cur, n = [("    ", DEFAULT)], 4
                text = text[room:]
    lines.append(cur)
    return lines


def draw(rows, path, label, bg):
    while rows and not any(t.strip() for t, _ in rows[-1]):
        rows = rows[:-1]
    rows = rows[:MAX_LINES] +([[("...", DEFAULT)]] if len(rows) > MAX_LINES else [])
    width = int(max([sum(len(t) for t, _ in r) for r in rows] + [40]) * CW) + GUTTER + 2 * PAD
    img = Image.new("RGB", (width, len(rows) * LH + 2 * PAD), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([GUTTER - 6, 2, width - 3, img.height - 3], fill=bg, outline=BORDER)
    d.text((6, PAD + 2), label, font=LABEL_FONT, fill=LABEL if label.startswith("In") else (216, 67, 21))
    for i, r in enumerate(rows):
        x = GUTTER + PAD - 6
        for t, c in r:
            d.text((x, PAD + i * LH), t, font=FONT, fill=c)
            x += len(t) * CW
    img.save(path)


def render_code(src, path, n):
    rows, cur = [], []
    for tok, val in lex(src.rstrip("\n"), PythonLexer()):
        for i, part in enumerate(val.split("\n")):
            if i > 0:
                rows.append(cur)
                cur = []
            if part:
                cur.append((part, colour_for(tok)))
    rows.append(cur)
    wrapped = [w for r in rows for w in wrap(r)]
    draw(wrapped, path, f"In [{n}]:", BG_CODE)


def render_text(text, path, n):
    rows = [w for ln in text.rstrip("\n").split("\n") for w in wrap([(ln.rstrip(), DEFAULT)])]
    draw(rows, path, f"Out[{n}]:", BG_OUT)


nb = nbformat.read(ROOT / "COM7021_EcoMove_Analysis.ipynb", 4)
n = 0
for i, cell in enumerate(nb.cells):
    if cell.cell_type != "code":
        continue
    n += 1
    render_code(cell.source, OUT / f"code_{i:02d}.png", n)
    parts = []
    for o in cell.outputs:
        if o.output_type == "stream":
            parts.append(o.text)
        elif o.output_type == "execute_result" and "text/plain" in o.data:
            parts.append(o.data["text/plain"])
    if parts:
        render_text("\n".join(p.rstrip("\n") for p in parts), OUT / f"out_{i:02d}.png", n)
print("rendered", len(list(OUT.glob("code_*.png"))), "code and", len(list(OUT.glob("out_*.png"))), "output images")
