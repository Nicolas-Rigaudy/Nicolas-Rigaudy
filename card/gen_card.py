#!/usr/bin/env python3
"""Build assets/card.svg: a neofetch-style card with an ASCII portrait and dot-leader rows, animated as a
terminal session (the prompt types `fastfetch`, then the output flushes row by row).

    python3 card/gen_card.py                      # card from the saved portrait.txt
    python3 card/gen_card.py --portrait face.png  # redo portrait.txt from a masked grayscale photo first

The portrait input is a grayscale image whose background is pure black (value 0).
Only the text rows in portrait.txt are kept in the repo, never the photo.
"""
import argparse
import pathlib
import random
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
TOP, PAD = 34, 26
CMD = "fastfetch"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono','Liberation Mono',monospace"


def portrait_rows(path, cols=44, max_rows=60):
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


def info_rows():
    """Card lines as (row index, svg) on the line grid; blank rows are skipped."""
    out = []
    for n, ln in enumerate(lines()):
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
        out.append((n, body))
    return out


def render(art, animate=False, output="rows"):
    """Static card, or animated like a terminal session: a prompt types `fastfetch`, the output flushes
    and a fresh prompt waits with a blinking cursor. output: rows (one screen row at a time), instant
    (all at once, as a real terminal), or baud (characters stream out like a slow serial line)."""
    rng = random.Random(7)  # fixed seed, so the typing rhythm is the same on every build
    info = info_rows()
    n_rows = len(lines())
    x_art = PAD + 8
    x0 = x_art + round((max(map(len, art)) + 3) * CW)
    W = x0 + int(COLS * CW) + PAD + 8
    top = TOP + (LH if animate else 0)  # the animated card gets a prompt row above the output
    H = top + LH * (n_rows + (2 if animate else 0)) + PAD - LH
    first = (n_rows - len(art)) // 2  # portrait rows sit on the same line grid, centred
    grid = {}  # row index -> list of (x, svg)
    for n, row in enumerate(art):
        if row.strip():
            grid.setdefault(first + n, []).append((x_art, tspan(row, mix(C["top"], C["bottom"], n / max(1, len(art) - 1)))))
    for n, body in info:
        grid.setdefault(n, []).append((x0, body))

    def text(x, y, body, extra=""):
        return f'<text x="{x}" y="{y:.1f}" font-family="{FONT}" font-size="{FS}px" xml:space="preserve"{extra}>{body}</text>'

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           f'<rect width="{W}" height="{H}" rx="14" fill="{C["bg"]}"/>']
    if not animate:
        for r in sorted(grid):
            out += [text(x, top + r * LH, body) for x, body in grid[r]]
        return "\n".join(out + ["</svg>"]) + "\n"

    prompt = tspan("nicolas", C["key"]) + tspan("@", C["dot"]) + tspan("rigaudy", C["val"]) + tspan(" ~ ❯ ", C["dot"])
    plen = 20  # prompt width in characters
    cur = f'width="{CW:.1f}" height="{FS * 1.2:.1f}" fill="{C["head"]}"'
    # Idle cursor, then keystrokes at an uneven human pace, then Enter.
    idle = 1.2
    times, t = [], idle
    for _ in CMD:
        t += rng.uniform(0.06, 0.24)
        times.append(t)
    enter = t + 0.45
    out.append(text(x_art, TOP, prompt))
    for k, ch in enumerate(CMD):
        out.append(text(x_art + (plen + k) * CW, TOP, tspan(ch, C["head"]),
                        f' visibility="hidden"><set attributeName="visibility" to="visible" begin="{times[k]:.2f}s"/'))
    xs = ";".join(f"{x_art + (plen + k) * CW:.1f}" for k in range(len(CMD) + 1))
    kt = ";".join(["0"] + [f"{(tk - idle) / (enter - idle):.4f}" for tk in times])
    out.append(f'<rect x="{x_art + plen * CW:.1f}" y="{TOP - FS * 0.95:.1f}" {cur}>'
               f'<animate attributeName="opacity" values="1;0" calcMode="discrete" dur="1s" repeatCount="indefinite" end="{idle:.2f}s"/>'
               f'<animate attributeName="x" values="{xs}" keyTimes="{kt}" calcMode="discrete" begin="{idle:.2f}s" dur="{enter - idle:.2f}s" fill="freeze"/>'
               f'<set attributeName="visibility" to="hidden" begin="{enter:.2f}s"/></rect>')
    # Output flushes one screen row at a time, logo and info together, with small stalls.
    t = enter + 0.25
    row_w = W - x_art - PAD
    for i, r in enumerate(sorted(grid)):
        if output == "rows":
            t += rng.uniform(0.01, 0.05) + (0.12 if rng.random() < 0.08 else 0)
        show = f' visibility="hidden"><set attributeName="visibility" to="visible" begin="{t:.2f}s"/'
        if output == "baud":
            # The whole row streams left to right through a widening clip, one row after another.
            dur = 0.11
            out.append(f'<clipPath id="r{i}"><rect x="{x_art}" y="{top + r * LH - FS:.1f}" width="0" height="{LH}">'
                       f'<animate attributeName="width" from="0" to="{row_w:.0f}" begin="{t:.2f}s" dur="{dur}s" fill="freeze"/></rect></clipPath>')
            out.append(f'<g clip-path="url(#r{i})">' + "".join(text(x, top + r * LH, body) for x, body in grid[r]) + "</g>")
            t += dur
            continue
        for x, body in grid[r]:
            out.append(text(x, top + r * LH, body, show))
    end = t + 0.3
    y = top + (n_rows + 1) * LH
    out.append(text(x_art, y, prompt, f' visibility="hidden"><set attributeName="visibility" to="visible" begin="{end:.2f}s"/'))
    out.append(f'<rect x="{x_art + plen * CW:.1f}" y="{y - FS * 0.95:.1f}" {cur} visibility="hidden">'
               f'<set attributeName="visibility" to="visible" begin="{end:.2f}s"/>'
               f'<animate attributeName="opacity" values="1;0" calcMode="discrete" dur="1s" begin="{end:.2f}s" repeatCount="indefinite"/></rect>')
    return "\n".join(out + ["</svg>"]) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--portrait", help="masked grayscale photo to redo portrait.txt from")
    a = ap.parse_args()
    if a.portrait:
        PORTRAIT.write_text("\n".join(portrait_rows(a.portrait)) + "\n")
    OUT.parent.mkdir(exist_ok=True)
    art = PORTRAIT.read_text().split("\n")[:-1]
    OUT.write_text(render(art, animate=True))
