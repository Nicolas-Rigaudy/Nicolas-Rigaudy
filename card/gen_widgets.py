#!/usr/bin/env python3
"""Build the widgets under assets/widgets/: metro map, blueprint and system loop, in Catppuccin Macchiato.

    python3 card/gen_widgets.py
"""
import math
import pathlib
from html import escape

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "assets" / "widgets"
W, H = 450, 503
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"
SANS = "'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
P = dict(base="#24273a", mantle="#1e2030", crust="#181926", s0="#363a4f", s1="#494d64", s2="#5b6078",
         ov="#8087a2", sub="#a5adcb", text="#cad3f5", blue="#8aadf4", mauve="#c6a0f6", teal="#8bd5ca",
         sky="#91d7e3", sapphire="#7dc4e4", peach="#f5a97f", green="#a6da95", yellow="#eed49f", red="#ed8796",
         lavender="#b7bdf8", pink="#f5bde6")

PROJECTS = [  # name, language, one-word role
    ("CR-0W", "Python", "agents"),
    ("Archeotech shell", "QML", "desktop"),
    ("LazyTF", "Go", "terraform"),
    ("Lorenzini Track", "Python", "telemetry"),
    ("Stacks", "TypeScript", "obsidian"),
    ("Dotfiles", "Shell", "arch"),
]


def t(x, y, s, size, fill, font=MONO, weight="normal", anchor="start", extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}px" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{extra}>{escape(s)}</text>')


def frame(body, title, sub, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>{defs}</defs>'
            f'<rect width="{W}" height="{H}" rx="16" fill="{P["base"]}"/>'
            f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{P["s0"]}"/>'
            + t(22, 34, title, 13, P["text"], weight="bold") + t(W - 22, 34, sub, 10, P["s2"], anchor="end")
            + f'<line x1="22" y1="46" x2="{W-22}" y2="46" stroke="{P["s0"]}"/>' + body + "</svg>\n")


def metro():
    """Four lines (Cloud, Backend, IoT, Terminal); projects are interchanges, skills are stations."""
    S = {  # name: (x, y, label dx, label dy, anchor, kind) kind: 0 skill, 1 project, 2 hub
        "Arch Linux": (40, 110, 0, -13, "start", 0), "Dotfiles": (105, 110, 0, 26, "middle", 1),
        "Archeotech": (172, 110, 0, 26, "middle", 1), "LazyTF": (245, 110, 0, -16, "middle", 1),
        "CR-0W": (330, 110, 0, -16, "middle", 1), "Agents": (410, 110, 0, -13, "end", 0),
        "AWS": (40, 190, 0, -13, "start", 0), "Terraform": (105, 190, 0, -13, "middle", 0),
        "Circle Mobility": (225, 270, -22, 4, "end", 2), "Architecture": (305, 350, 14, 4, "start", 0),
        "Python": (40, 350, 0, 22, "start", 0), "TypeScript": (95, 350, 0, -13, "middle", 0),
        "Stacks": (145, 350, 0, 26, "middle", 1), "Go": (185, 310, -12, 4, "end", 0),
        "Sensors": (40, 430, 0, -13, "start", 0), "MQTT": (105, 430, 0, -13, "middle", 0),
        "Teaching": (165, 430, 0, -13, "middle", 0),
        "Lorenzini Track": (330, 270, 0, -16, "middle", 1), "Open Data": (410, 270, 0, 22, "end", 0),
    }
    lines = {  # colour, path through points (stations by name or raw corners)
        "Cloud": (P["blue"], ["AWS", "Terraform", (145, 190), "Circle Mobility", "Architecture"]),
        "Backend": (P["mauve"], ["Python", "TypeScript", "Stacks", "Go", "Circle Mobility", (330, 165), "CR-0W", "Agents"]),
        "IoT": (P["sapphire"], ["Sensors", "MQTT", "Teaching", (225, 430), "Circle Mobility", "Lorenzini Track", "Open Data"]),
        "Terminal": (P["peach"], ["Arch Linux", "Dotfiles", "Archeotech", "LazyTF", "CR-0W"]),
    }
    b = []
    for name, (c, pts) in lines.items():
        xy = [S[p][:2] if isinstance(p, str) else p for p in pts]
        d = "M" + " L".join(f"{x},{y}" for x, y in xy)
        b.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>')
        b.append(f'<circle r="4" fill="{P["text"]}"><animateMotion path="{d}" dur="{6 + len(xy)}s" '
                 f'repeatCount="indefinite" keyPoints="0;1;0" keyTimes="0;.5;1" calcMode="linear"/></circle>')
    for label, (x, y, dx, dy, anchor, proj) in S.items():
        if proj == 2:  # the hub: a large ring where three lines meet
            b.append(f'<circle cx="{x}" cy="{y}" r="15" fill="{P["base"]}" stroke="{P["text"]}" stroke-width="4"/>'
                     f'<circle cx="{x}" cy="{y}" r="15" fill="none" stroke="{P["lavender"]}" stroke-opacity=".6">'
                     f'<animate attributeName="r" values="15;24;15" dur="3s" repeatCount="indefinite"/>'
                     f'<animate attributeName="stroke-opacity" values=".6;0;.6" dur="3s" repeatCount="indefinite"/></circle>')
        elif proj:
            b.append(f'<rect x="{x-9}" y="{y-9}" width="18" height="18" rx="9" fill="{P["base"]}" stroke="{P["text"]}" stroke-width="3"/>')
        else:
            b.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{P["base"]}" stroke="{P["text"]}" stroke-width="2.5"/>')
        b.append(t(x + dx, y + dy, label, (10.5, 10.5, 12)[proj] if proj else 9.5, P["text"] if proj else P["sub"],
                   weight="bold" if proj else "normal", anchor=anchor,
                   extra=f' stroke="{P["base"]}" stroke-width="3" paint-order="stroke"'))
    ly = H - 34
    for k, (name, (c, _)) in enumerate(lines.items()):
        x = 24 + k * 106
        b += [f'<rect x="{x}" y="{ly-8}" width="22" height="7" rx="3.5" fill="{c}"/>', t(x + 28, ly, name, 10, P["sub"])]
    b.append(f'<line x1="22" y1="{H-58}" x2="{W-22}" y2="{H-58}" stroke="{P["s0"]}"/>')
    n_proj = sum(v[5] == 1 for v in S.values())
    n_skill = sum(v[5] == 0 for v in S.values())
    return frame("".join(b), "NETWORK MAP", f"{len(lines)} LINES · {n_proj} PROJECTS · {n_skill} SKILLS")


def blueprint():
    """Exploded assembly: projects as parts of one system, with a parts list."""
    grid = (f'<pattern id="g" width="15" height="15" patternUnits="userSpaceOnUse">'
            f'<path d="M15,0 L0,0 0,15" fill="none" stroke="{P["blue"]}" stroke-opacity=".12" stroke-width="1"/></pattern>')
    b = [f'<rect x="12" y="52" width="{W-24}" height="{H-64}" rx="8" fill="#1a2238"/>',
         f'<rect x="12" y="52" width="{W-24}" height="{H-64}" rx="8" fill="url(#g)"/>']
    # core and parts
    cx, cy = 150, 210
    b += [f'<rect x="{cx-46}" y="{cy-28}" width="92" height="56" rx="4" fill="none" stroke="{P["blue"]}" stroke-width="1.6"/>',
          t(cx, cy - 4, "CLEAR", 11, P["blue"], weight="bold", anchor="middle"),
          t(cx, cy + 12, "TOOLS", 11, P["blue"], weight="bold", anchor="middle")]
    parts = [(-95, -100), (0, -118), (95, -100), (-95, 100), (0, 118), (95, 100)]
    for k, ((dx, dy), (name, lang, role)) in enumerate(zip(parts, PROJECTS)):
        px, py = cx + dx, cy + dy
        b += [f'<line x1="{cx + dx * .3:.0f}" y1="{cy + (28 if dy > 0 else -28)}" x2="{px}" y2="{py + (-14 if dy > 0 else 14)}" '
              f'stroke="{P["sky"]}" stroke-width="1" stroke-dasharray="3 3"/>',
              f'<rect x="{px-34}" y="{py-14}" width="68" height="28" rx="3" fill="#1a2238" stroke="{P["sky"]}" stroke-width="1.3"/>',
              t(px, py + 4, f"{k+1:02d}", 12, P["sky"], weight="bold", anchor="middle")]
    # dimension line
    b += [f'<line x1="40" y1="{cy+150}" x2="260" y2="{cy+150}" stroke="{P["s2"]}" stroke-width="1"/>',
          f'<line x1="40" y1="{cy+144}" x2="40" y2="{cy+156}" stroke="{P["s2"]}"/><line x1="260" y1="{cy+144}" x2="260" y2="{cy+156}" stroke="{P["s2"]}"/>',
          t(150, cy + 145, "since 2014", 9, P["s2"], anchor="middle")]
    # parts list
    lx, ly = 290, 80
    b += [f'<rect x="{lx-8}" y="{ly-16}" width="{W-lx-14}" height="{24 + 34 * len(PROJECTS)}" fill="none" stroke="{P["blue"]}" stroke-opacity=".5"/>',
          t(lx, ly, "PARTS LIST", 10, P["blue"], weight="bold")]
    for k, (name, lang, role) in enumerate(PROJECTS):
        y = ly + 24 + k * 34
        b += [t(lx, y, f"{k+1:02d}", 10, P["sky"], weight="bold"), t(lx + 24, y, name, 10, P["text"], weight="bold"),
              t(lx + 24, y + 13, f"{lang} · {role}", 9, P["sub"])]
    # stack strip
    sy = H - 56
    b.append(t(24, sy, "MATERIALS", 9, P["blue"], weight="bold"))
    x = 24
    for s in ["Python", "Go", "Terraform", "AWS", "QML", "TypeScript", "MQTT"]:
        w = len(s) * 6.3 + 14
        b += [f'<rect x="{x}" y="{sy+8}" width="{w:.0f}" height="18" rx="3" fill="none" stroke="{P["sky"]}" stroke-opacity=".7"/>',
              t(x + w / 2, sy + 21, s, 9.5, P["text"], anchor="middle")]
        x += w + 6
    # scan line
    b.append(f'<rect x="12" y="52" width="{W-24}" height="2" fill="{P["sky"]}" opacity=".35">'
             f'<animate attributeName="y" values="52;{H-14};52" dur="8s" repeatCount="indefinite"/></rect>')
    return frame("".join(b), "EXPLODED ASSEMBLY", "6 PARTS · NR-001", grid)


def loop():
    """Projects on a closed loop around a core; tech on an outer ring; a pulse runs the loop."""
    cx, cy, r = W / 2, 240, 108
    b = [f'<circle cx="{cx}" cy="{cy}" r="{r+48}" fill="none" stroke="{P["s0"]}" stroke-dasharray="2 6"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{P["s1"]}" stroke-width="2"/>',
         f'<circle id="ring" cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#arc)" stroke-width="2.5" '
         f'stroke-dasharray="120 {2 * math.pi * r - 120:.0f}">'
         f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="8s" repeatCount="indefinite"/></circle>',
         f'<circle cx="{cx}" cy="{cy}" r="44" fill="{P["mantle"]}" stroke="{P["mauve"]}" stroke-width="2"/>',
         f'<circle cx="{cx}" cy="{cy}" r="52" fill="none" stroke="{P["mauve"]}" stroke-opacity=".4">'
         f'<animate attributeName="r" values="46;60;46" dur="3s" repeatCount="indefinite"/>'
         f'<animate attributeName="stroke-opacity" values=".5;0;.5" dur="3s" repeatCount="indefinite"/></circle>',
         t(cx, cy - 4, "nicolas", 12, P["mauve"], weight="bold", anchor="middle"),
         t(cx, cy + 12, "@rigaudy", 11, P["blue"], anchor="middle")]
    colors = [P["mauve"], P["peach"], P["blue"], P["sapphire"], P["green"], P["yellow"]]
    for k, ((name, lang, role), c) in enumerate(zip(PROJECTS, colors)):
        a = -math.pi / 2 + k * 2 * math.pi / len(PROJECTS)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        b += [f'<line x1="{cx + 44 * math.cos(a):.1f}" y1="{cy + 44 * math.sin(a):.1f}" x2="{x:.1f}" y2="{y:.1f}" '
              f'stroke="{c}" stroke-opacity=".35" stroke-dasharray="3 4"/>',
              f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="{P["base"]}" stroke="{c}" stroke-width="2.5"/>',
              f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{c}"/>']
        name = name.replace("Archeotech shell", "Archeotech")
        lx, ly = cx + (r + 22) * math.cos(a), cy + (r + 22) * math.sin(a)
        anchor = "middle" if abs(math.cos(a)) < .3 else ("start" if math.cos(a) > 0 else "end")
        dy = -6 if math.sin(a) < -.5 else (14 if math.sin(a) > .5 else 0)
        b += [t(lx, ly + dy, name, 10.5, P["text"], weight="bold", anchor=anchor),
              t(lx, ly + dy + 12, lang, 9, P["sub"], anchor=anchor)]
    # stack strip
    sy = H - 56
    b.append(f'<line x1="22" y1="{sy-14}" x2="{W-22}" y2="{sy-14}" stroke="{P["s0"]}"/>')
    b.append(t(24, sy, "STACK", 9, P["mauve"], weight="bold"))
    x = 24
    for s_ in ["Python", "Go", "Terraform", "AWS", "MQTT", "QML", "TypeScript"]:
        w = len(s_) * 6.3 + 14
        b += [f'<rect x="{x}" y="{sy+8}" width="{w:.0f}" height="18" rx="9" fill="{P["mantle"]}" stroke="{P["s1"]}"/>',
              t(x + w / 2, sy + 21, s_, 9.5, P["sub"], anchor="middle")]
        x += w + 6
    defs = (f'<linearGradient id="arc" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{P["mauve"]}"/>'
            f'<stop offset="1" stop-color="{P["sapphire"]}"/></linearGradient>')
    return frame("".join(b), "CLOSED LOOP", "6 NODES · ONE SYSTEM", defs)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [("metro", metro), ("blueprint", blueprint), ("loop", loop)]:
        (OUT / f"{name}.svg").write_text(fn())
