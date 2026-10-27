#!/usr/bin/env python3
"""Build assets/tcg.svg: a trading card in the style of a Pokemon ex, in the card's Catppuccin palette,
with an animated holo rim, foil, sparkles and a light sweep. The art is the ASCII portrait from portrait.txt.

    python3 card/gen_tcg.py
"""
import pathlib
import random
from html import escape

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "assets" / "tcg.svg"
ART = (HERE / "portrait.txt").read_text().split("\n")[:-1]
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"
SANS = "'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"


def t(x, y, s, size, fill, font=SANS, weight="normal", anchor="start", style=""):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}px" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{style}>{escape(s)}</text>')


def energy(cx, cy, kind, r=9):
    """Energy symbol: a coloured disc with a short glyph, one per skill type."""
    col, g = {"cloud": ("#8aadf4", "☁"), "backend": ("#c6a0f6", "{}"), "iot": ("#7dc4e4", "◉"),
              "any": ("#cad3f5", "★")}[kind]
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}" stroke="#181926" stroke-width="1.2"/>'
            f'<text x="{cx}" y="{cy + r * 0.38:.1f}" font-family="{SANS}" font-size="{r * 1.05:.1f}px" font-weight="bold" '
            f'fill="#181926" text-anchor="middle">{escape(g)}</text>')


def card(attacks=None):
    W2, H2 = 360, 503
    ink, sub = "#f4f5fb", "#b8c0e0"
    attacks = attacks or [
        (["iot", "any"], "MQTT Broadcast", "20×", ["20 damage to each opposing device subscribed to this topic."]),
        (["cloud", "backend", "any"], "Spawn Agents", "40×", ["Attach an agent to each Benched repo. 40 damage for each."]),
    ]
    b = [f'<clipPath id="card"><rect width="{W2}" height="{H2}" rx="18"/></clipPath>',
         f'<g clip-path="url(#card)">',
         # silver frame and full-bleed foil background
         f'<rect width="{W2}" height="{H2}" fill="url(#rim)"/>',
         f'<rect x="10" y="10" width="{W2-20}" height="{H2-20}" rx="10" fill="url(#deep)"/>',
         f'<rect x="10" y="10" width="{W2-20}" height="{H2-20}" rx="10" fill="url(#foil)" opacity=".2" style="mix-blend-mode:screen"/>',
         f'<rect x="10" y="10" width="{W2-20}" height="{H2-20}" rx="10" fill="url(#lines)" opacity=".25"/>']
    # art: the portrait, large, behind the header
    cols, rows = max(map(len, ART)), len(ART)
    fs = 8.4
    lh = fs * 1.12
    x0, y0 = W2 / 2 - cols * fs * 0.602 / 2 + 20, 70
    b.append(f'<text font-family="{MONO}" font-size="{fs}px" font-weight="bold" xml:space="preserve" '
             f'fill="url(#artfill)" style="filter:url(#glow)">')
    for n, r in enumerate(ART):
        b.append(f'<tspan x="{x0:.1f}" y="{y0 + n * lh:.1f}">{escape(r)}</tspan>')
    b.append("</text>")
    # sparkles
    rng = random.Random(3)
    for _ in range(16):
        x, y, s = rng.uniform(20, W2 - 20), rng.uniform(40, 300), rng.uniform(3, 7)
        d = rng.uniform(0, 3)
        b.append(f'<path d="M{x},{y-s} L{x+s*.25},{y-s*.25} L{x+s},{y} L{x+s*.25},{y+s*.25} L{x},{y+s} '
                 f'L{x-s*.25},{y+s*.25} L{x-s},{y} L{x-s*.25},{y-s*.25}Z" fill="#fff" opacity="0">'
                 f'<animate attributeName="opacity" values="0;.9;0" dur="2.6s" begin="{d:.2f}s" repeatCount="indefinite"/></path>')
    # flavour line at the foot of the art
    b.append(f'<rect x="16" y="264" width="{W2-32}" height="30" fill="#181926" opacity=".8"/>')
    for k, line in enumerate(["In the grim darkness of production, there is only uptime.", "The pipeline protects."]):
        b.append(t(W2 / 2, 276 + k * 12, line, 9, "#b8c0e0", anchor="middle", style=' font-style="italic"'))
    # light sweep over everything
    b.append(f'<rect x="10" y="10" width="{W2-20}" height="{H2-20}" fill="url(#sweep)"/>')
    # header
    b += [f'<path d="M16,18 h196 l-8,15 h-188z" fill="url(#silver)"/>',
          t(22, 30, "STAGE 2 · ENGINEERING MANAGER", 9.5, "#181926", weight="bold"),
          f'<circle cx="38" cy="58" r="20" fill="url(#silver)"/><circle cx="38" cy="58" r="16" fill="#1e2030"/>',
          *[f'<line x1="{38 + d}" y1="47" x2="{38 + d}" y2="69" stroke="#7dc4e4" stroke-width="1.6"/>' for d in (-5, 0, 5)],
          *[f'<line x1="27" y1="{58 + d}" x2="49" y2="{58 + d}" stroke="#7dc4e4" stroke-width="1.6"/>' for d in (-5, 0, 5)],
          '<rect x="31" y="51" width="14" height="14" rx="2" fill="#1e2030" stroke="#7dc4e4" stroke-width="1.6"/>',
          '<circle cx="34.5" cy="54.5" r="1.3" fill="#7dc4e4"/>',
          t(64, 58, "Nicolas", 25, ink, weight="900", style=' stroke="#181926" stroke-width="3" paint-order="stroke"'),
          t(168, 58, "ex", 25, "url(#exfill)", weight="900", style=' font-style="italic" stroke="#181926" stroke-width="3" paint-order="stroke"'),
          t(64, 73, "Evolves from IoT Engineer", 9, sub, style=' font-style="italic"'),
          t(W2 - 98, 56, "HP", 10, ink, weight="bold", style=' stroke="#181926" stroke-width="2" paint-order="stroke"'),
          t(W2 - 34, 58, "1997", 22, ink, weight="900", anchor="end", style=' stroke="#181926" stroke-width="3" paint-order="stroke"'),
          energy(W2 - 20, 50, "cloud", 10)]
    # lower panel
    py = 296
    b.append(f'<rect x="16" y="{py}" width="{W2-32}" height="{H2-py-26}" rx="8" fill="#181926" opacity=".8"/>')
    y = py + 22
    b += [f'<rect x="26" y="{y-13}" width="60" height="17" rx="8.5" fill="#ed8796"/>',
          t(56, y, "Ability", 11, "#181926", weight="bold", anchor="middle", style=' font-style="italic"'),
          t(94, y, "Sprint Planning", 15, "#ed8796", weight="bold"),
          t(26, y + 16, "Once per turn, look at the top 5 cards of your deck and put", 9.5, sub),
          t(26, y + 28, "them back in any order.", 9.5, sub)]
    y += 54
    for cost, name, dmg, desc in attacks:
        for k, c in enumerate(cost):
            b.append(energy(32 + k * 19, y - 5, c, 8))
        b += [t(W2 / 2 + 14, y, name, 15.5, ink, weight="bold", anchor="middle"),
              t(W2 - 26, y, dmg, 16, ink, weight="900", anchor="end")]
        for k, d in enumerate(desc):
            b.append(t(26, y + 16 + k * 12, d, 9.5, sub))
        y += 22 + 12 * len(desc) + 4
    # weakness strip
    y = H2 - 44
    b += [f'<line x1="24" y1="{y-12}" x2="{W2-24}" y2="{y-12}" stroke="#494d64"/>',
          t(26, y, "weakness", 8, sub), t(72, y, "Merge conflicts ×2", 9.5, ink, weight="bold"),
          t(172, y, "resistance", 8, sub), t(218, y, "Bug -30", 9.5, ink, weight="bold"),
          t(258, y, "retreat", 8, sub), energy(300, y - 3, "any", 6), energy(315, y - 3, "any", 6),
          "</g>"]
    defs = ('<linearGradient id="silver" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#b7bdf8"/>'
            '<stop offset=".35" stop-color="#8aadf4"/><stop offset=".6" stop-color="#c6a0f6"/><stop offset="1" stop-color="#91d7e3"/></linearGradient>'
            '<linearGradient id="rim" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0" stop-color="#c6a0f6"/><stop offset=".3" stop-color="#8aadf4"/><stop offset=".55" stop-color="#7dc4e4"/>'
            '<stop offset=".8" stop-color="#f5a97f"/><stop offset="1" stop-color="#c6a0f6"/>'
            '<animateTransform attributeName="gradientTransform" type="rotate" from="0 .5 .5" to="360 .5 .5" dur="10s" repeatCount="indefinite"/>'
            '</linearGradient>'
            '<radialGradient id="deep" cx=".55" cy=".3" r=".9"><stop offset="0" stop-color="#24273a"/>'
            '<stop offset=".6" stop-color="#1e2030"/><stop offset="1" stop-color="#181926"/></radialGradient>'
            '<linearGradient id="foil" x1="0" y1="0" x2="1" y2="1" gradientUnits="objectBoundingBox">'
            '<stop offset="0" stop-color="#ed8796"/><stop offset=".2" stop-color="#f5a97f"/><stop offset=".4" stop-color="#eed49f"/>'
            '<stop offset=".55" stop-color="#a6da95"/><stop offset=".7" stop-color="#7dc4e4"/><stop offset=".85" stop-color="#8aadf4"/>'
            '<stop offset="1" stop-color="#c6a0f6"/>'
            '<animateTransform attributeName="gradientTransform" type="translate" values="-.5 -.5;.5 .5;-.5 -.5" dur="9s" repeatCount="indefinite"/>'
            '</linearGradient>'
            '<pattern id="lines" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(35)">'
            '<line x1="0" y1="0" x2="0" y2="6" stroke="#fff" stroke-width="1" opacity=".25"/></pattern>'
            '<linearGradient id="sweep" x1="0" y1="0" x2="1" y2=".4">'
            '<stop offset=".35" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".22"/>'
            '<stop offset=".65" stop-color="#fff" stop-opacity="0"/>'
            '<animateTransform attributeName="gradientTransform" type="translate" values="-1.2 0;1.2 0;1.2 0" keyTimes="0;.45;1" dur="6s" repeatCount="indefinite"/>'
            '</linearGradient>'
            '<linearGradient id="artfill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f5bde6"/>'
            '<stop offset=".5" stop-color="#b7bdf8"/><stop offset="1" stop-color="#91d7e3"/></linearGradient>'
            '<linearGradient id="exfill" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f5bde6"/>'
            '<stop offset=".5" stop-color="#eed49f"/><stop offset="1" stop-color="#8bd5ca"/></linearGradient>'
            '<filter id="glow"><feGaussianBlur stdDeviation="1.2" result="b"/><feMerge><feMergeNode in="b"/>'
            '<feMergeNode in="SourceGraphic"/></feMerge></filter>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W2}" height="{H2}" viewBox="0 0 {W2} {H2}">'
            f"<defs>{defs}</defs>{''.join(b)}</svg>\n")


if __name__ == "__main__":
    OUT.write_text(card())
