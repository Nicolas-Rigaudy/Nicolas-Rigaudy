#!/usr/bin/env python3
"""Build assets/card.svg: a neofetch-style card with an ASCII portrait and dot-leader rows.

    python3 card/gen_card.py                      # card from the saved portrait.txt
    python3 card/gen_card.py --portrait face.png  # redo portrait.txt from a masked grayscale photo first

The portrait input is a grayscale image whose background is pure black (value 0).
Only the text rows in portrait.txt are kept in the repo, never the photo.
"""
import argparse
import pathlib
from html import escape

HERE = pathlib.Path(__file__).parent
PORTRAIT = HERE / "portrait.txt"
OUT = HERE.parent / "assets" / "card.svg"

SECTIONS = [
    ("nicolas@rigaudy", [
        ("OS", "Arch Linux, MangoWC"),
        ("Uptime", "Coding Since 2014"),
        ("Host", "Circle Mobility"),
        ("Role", "Engineering Manager"),
        ("Role.Architect", "Cloud and Backend"),
        ("Kernel", "IoT Engineer, ESME Sudria"),
        ("Certified", "AWS Solutions Architect"),
        None,
        ("Stack", "DevOps, Backend, Cloud, IoT"),
        ("Languages.Code", "Python (Main), Go, Terraform"),
        ("Languages.Real", "French, English, Some Spanish, Japanese"),
        None,
        ("Teaching", "IoT and Cloud, Engineering Schools"),
        ("Teaching.Topics", "Sensors, MQTT, AWS, Student Projects"),
        None,
        ("Hobbies", "Warhammer Painting, Gunpla, Gaming"),
        ("Sports", "Surfing, Snowboarding, Skiing, Golf, Running"),
    ]),
    ("Goal", [
        ("Mission", "Turn Complex Systems Into Clear Tools"),
        ("Mission.How", "One View to See, Steer and Ship"),
        ("Principles", "Terminal First, Automate the Rest"),
        ("Mindset", "Done > Perfect, Always Learning, Welcome Change"),
    ]),
    ("Contact", [
        ("Email.Personal", "nicolas.rigaudy@gmail.com"),
        ("Email.Work", "nicolas.rigaudy@circle-mobility.com"),
        ("LinkedIn", "in/nicolas-rigaudy"),
    ]),
]

# Catppuccin Macchiato. The card stays dark in both GitHub themes.
C = dict(bg="#24273a", key="#c6a0f6", sub="#f5a97f", val="#8aadf4", dot="#5b6078", head="#cad3f5",
         top="#c6a0f6", bottom="#7dc4e4")
COLS, FS, LH, CW = 62, 16, 21, 9.63  # chars per line, font px, line height, monospace advance at 16px
X0, TOP, PAD = 390, 34, 26
AFS = 10  # portrait font px, smaller for detail
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono','Liberation Mono',monospace"


def portrait_rows(path, cols=56, max_rows=60):
    """Grayscale photo to density-ramp rows."""
    from PIL import Image, ImageOps
    im = ImageOps.autocontrast(Image.open(path).convert("L"), cutoff=2)
    cw, chh = 10, 22
    rows = min(max_rows, round(cols * cw / im.width * im.height / chh))
    cols = min(cols, round(rows * chh / im.height * im.width / cw))
    ramp = " .:-=+*#%@"
    g = im.resize((cols, rows))
    return ["".join(ramp[min(len(ramp) - 1, g.getpixel((k, r)) * len(ramp) // 256)] for k in range(cols)).rstrip()
            for r in range(rows)]


def lines():
    out = []
    for i, (title, rows) in enumerate(SECTIONS):
        if i:
            out.append(("blank",))
        out.append(("head", title, i == 0))
        for r in rows:
            out.append(("dot",) if r is None else ("kv",) + r)
    return out


def mix(a, b, t):
    a, b = [int(a[i:i+2], 16) for i in (1, 3, 5)], [int(b[i:i+2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def tspan(t, c):
    return f'<tspan fill="{c}">{escape(t)}</tspan>'


def render(art):
    L = lines()
    W = X0 + int(COLS * CW) + PAD + 8
    H = TOP + LH * len(L) + PAD
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           f'<rect width="{W}" height="{H}" rx="14" fill="{C["bg"]}"/>']
    alh = LH * AFS / FS
    a0 = TOP - LH * 0.7 + max(0, (H - TOP - PAD - alh * len(art)) / 2) + alh * 0.7
    out.append(f'<text font-family="{FONT}" font-size="{AFS}px" xml:space="preserve">')
    for n, row in enumerate(art):
        if row.strip():
            t = n / max(1, len(art) - 1)
            out.append(f'<tspan x="{PAD + 8}" y="{a0 + n*alh:.1f}" fill="{mix(C["top"], C["bottom"], t)}">{escape(row)}</tspan>')
    out.append(f'</text><text font-family="{FONT}" font-size="{FS}px" xml:space="preserve">')
    for n, ln in enumerate(L):
        y = TOP + n * LH
        if ln[0] == "blank":
            continue
        if ln[0] == "dot":
            body = tspan(".", C["dot"])
        elif ln[0] == "head":
            title, first = ln[1], ln[2]
            if first:
                u, h = title.split("@")
                body = tspan(u, C["key"]) + tspan("@", C["dot"]) + tspan(h, C["val"])
                rest = COLS - len(title) - 1
            else:
                body = tspan("- ", C["dot"]) + tspan(title, C["head"])
                rest = COLS - len(title) - 3
            body += tspan(" " + "─" * rest, C["dot"])
        else:
            k, v = ln[1], ln[2]
            parts = k.split(".")
            kt = tspan(".", C["dot"]) + tspan(parts[0], C["key"])
            if len(parts) > 1:
                kt += tspan(".", C["dot"]) + tspan(parts[1], C["sub"])
            kt += tspan(":", C["dot"])
            fill = COLS - (1 + len(k) + 1) - len(v) - 2
            assert fill >= 3, f"line too long: {k}"
            body = kt + tspan(" " + "." * fill + " ", C["dot"]) + tspan(v, C["val"])
        out.append(f'<tspan x="{X0}" y="{y}">{body}</tspan>')
    out.append("</text></svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--portrait", help="masked grayscale photo to redo portrait.txt from")
    a = ap.parse_args()
    if a.portrait:
        PORTRAIT.write_text("\n".join(portrait_rows(a.portrait)) + "\n")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(render(PORTRAIT.read_text().split("\n")[:-1]))
