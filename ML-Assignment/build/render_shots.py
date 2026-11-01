from pathlib import Path
import nbformat
from PIL import Image, ImageDraw, ImageFont
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Token

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "assets"
OUT.mkdir(exist_ok=True)

BG = (30, 30, 30)
DEFAULT = (212, 212, 212)
FONT = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 20)
CW = FONT.getlength("M")
LH = 28
PAD = 18
WRAP = 145

COLOURS = [
    (Token.Keyword, (197, 134, 192)),
    (Token.Name.Builtin, (78, 201, 176)),
    (Token.Name.Function, (220, 220, 170)),
    (Token.Name.Class, (78, 201, 176)),
    (Token.Literal.String, (206, 145, 120)),
    (Token.Literal.Number, (181, 206, 168)),
    (Token.Operator.Word, (197, 134, 192)),
    (Token.Comment, (106, 153, 85)),
]


def colour_for(tok):
    for t, c in COLOURS:
        if tok in t:
            return c
    return DEFAULT


def wrap_line(segments, width):
    lines, cur, n = [], [], 0
    for text, col in segments:
        while text:
            room = width - n
            if len(text) <= room:
                cur.append((text, col))
                n += len(text)
                text = ""
            else:
                cut = text.rfind(" ", 0, room)
                cut = room if cut <= 0 else cut + 1
                cur.append((text[:cut], col))
                lines.append(cur)
                cur, n = [("    ", DEFAULT)], 4
                text = text[cut:]
    lines.append(cur)
    return lines


def render_code(src, path):
    rows = []
    cur = []
    for tok, val in lex(src.rstrip("\n"), PythonLexer()):
        parts = val.split("\n")
        for i, part in enumerate(parts):
            if i > 0:
                rows.append(cur)
                cur = []
            if part:
                cur.append((part, colour_for(tok)))
    rows.append(cur)
    wrapped = []
    for r in rows:
        wrapped.extend(wrap_line(r, WRAP))
    width = int(max(sum(len(t) for t, _ in r) for r in wrapped) * CW) + 2 * PAD
    img = Image.new("RGB", (max(width, 520), len(wrapped) * LH + 2 * PAD), BG)
    d = ImageDraw.Draw(img)
    for i, r in enumerate(wrapped):
        x = PAD
        for t, c in r:
            d.text((x, PAD + i * LH), t, font=FONT, fill=c)
            x += len(t) * CW
    img.save(path)


def render_text(text, path):
    lines = []
    for ln in text.rstrip("\n").split("\n"):
        lines.append(ln.rstrip())
    width = int(max(len(l) for l in lines) * CW) + 2 * PAD
    img = Image.new("RGB", (max(width, 520), len(lines) * LH + 2 * PAD), BG)
    d = ImageDraw.Draw(img)
    for i, l in enumerate(lines):
        d.text((PAD, PAD + i * LH), l, font=FONT, fill=DEFAULT)
    img.save(path)


nb = nbformat.read(ROOT / "COM7022_Task1_Clustering.ipynb", 4)
for i, cell in enumerate(nb.cells):
    if cell.cell_type != "code":
        continue
    render_code(cell.source, OUT / f"code_{i:02d}.png")
    parts = []
    for o in cell.outputs:
        if o.output_type == "stream":
            parts.append(o.text)
        elif o.output_type == "execute_result" and "text/plain" in o.data:
            parts.append(o.data["text/plain"])
    if parts:
        render_text("\n".join(p.rstrip("\n") for p in parts), OUT / f"out_{i:02d}.png")
print("rendered", len(list(OUT.glob("code_*.png"))), "code and", len(list(OUT.glob("out_*.png"))), "output images")
