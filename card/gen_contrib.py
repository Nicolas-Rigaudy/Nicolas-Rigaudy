#!/usr/bin/env python3
"""Build assets/widgets/contributions.svg: the last year of contributions as a scrolling isometric Breakout,
in the style of Ball x Pit. Bricks are the days with contributions, taller for busier days.

    python3 card/gen_contrib.py           # from the cached calendar in card/contributions.json
    python3 card/gen_contrib.py --fetch   # refresh the cache first (needs GITHUB_TOKEN), as the daily Action does
"""
import json
import os
import pathlib
import random
import sys
import urllib.request

HERE = pathlib.Path(__file__).parent
CACHE = HERE / "contributions.json"
OUT = HERE.parent / "assets" / "widgets" / "contributions.svg"
USER = "Nicolas-Rigaudy"
QUERY = ('query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{totalContributions '
         'weeks{contributionDays{date contributionCount contributionLevel}}}}}}')


def fetch():
    req = urllib.request.Request("https://api.github.com/graphql", method="POST",
                                 data=json.dumps({"query": QUERY, "variables": {"u": USER}}).encode(),
                                 headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}"})
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    CACHE.write_text(json.dumps(data, indent=1) + "\n")


if "--fetch" in sys.argv:
    fetch()
CAL = json.loads(CACHE.read_text())["data"]["user"]["contributionsCollection"]["contributionCalendar"]
LV = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
GRID = [[LV[d["contributionLevel"]] for d in w["contributionDays"]] for w in CAL["weeks"]]  # [week][day]
COUNT = [[d["contributionCount"] for d in w["contributionDays"]] for w in CAL["weeks"]]
GRID = [w + [0] * (7 - len(w)) for w in GRID]  # the current week is partial
COUNT = [w + [0] * (7 - len(w)) for w in COUNT]
NW = len(GRID)
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"
P = dict(base="#24273a", mantle="#1e2030", crust="#181926", s0="#363a4f", s1="#494d64", s2="#5b6078",
         sub="#a5adcb", text="#cad3f5", blue="#8aadf4", mauve="#c6a0f6", sapphire="#7dc4e4", peach="#f5a97f",
         green="#a6da95", yellow="#eed49f", red="#ed8796", pink="#f5bde6", lavender="#b7bdf8", sky="#91d7e3")
W = 830


def frame(body, title, h, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}"><defs>{defs}</defs>'
            f'<rect width="{W}" height="{h}" rx="14" fill="{P["base"]}"/>'
            f'<text x="18" y="30" font-family="{MONO}" font-size="12" font-weight="bold" fill="{P["text"]}">{title}</text>'
            f'<text x="{W-18}" y="30" font-family="{MONO}" font-size="10" fill="{P["s2"]}" text-anchor="end">'
            f'{CAL["totalContributions"]} contributions in the last year</text>{body}</svg>\n')


def render(T=42.0, VIEW=22, speed=15.0, splits=(4.0, 10.0, 17.0, 25.0), seed=11):
    """Breakout in Ball x Pit style: a VIEW-week window of the year scrolls toward a paddle on the short
    front edge, quickly through the quiet old months and slowly over the recent busy ones. Balls split from
    the lead ball, leave trails and spark on hits; bricks that reach the paddle line shatter."""
    A, B, OX, OY = 24.0, 12.0, 92.0, 360.0
    total = NW - VIEW + 2
    # scroll s(t): the first 60% of the year in 30% of the loop, the recent 40% in the remaining 70%
    SK = [(0.0, 0.0), (.3 * T, .6 * total), (T, total)]

    def scroll_at(t):
        for (t0, s0), (t1, s1) in zip(SK, SK[1:]):
            if t <= t1:
                return s0 + (s1 - s0) * (t - t0) / (t1 - t0)
        return total

    def pos(i, j):
        return OX + (i + j) * A, OY + (j - i) * B

    def shade(c, k):
        a, b = [int(c[i:i+2], 16) for i in (1, 3, 5)], [0x18, 0x19, 0x26]
        return "#" + "".join(f"{round(x + (y - x) * k):02x}" for x, y in zip(a, b))

    def cube2(x, y, z, c, s=.86):
        a, b = A * s, B * s
        return (f'<polygon points="{x-a},{y-z} {x},{y+b-z} {x},{y+b} {x-a},{y}" fill="{shade(c, .45)}"/>'
                f'<polygon points="{x+a},{y-z} {x},{y+b-z} {x},{y+b} {x+a},{y}" fill="{shade(c, .25)}"/>'
                f'<polygon points="{x},{y-b-z} {x+a},{y-z} {x},{y+b-z} {x-a},{y-z}" fill="{c}"/>')

    rng = random.Random(seed)
    alive = {(i, j) for i in range(NW) for j in range(7) if GRID[i][j]}
    gone = {}
    R = .3  # ball radius in cells
    HALF = 1.0  # half paddle length in cells, plus the ball radius
    vp, PSPEED = 3.0, 9.0  # paddle position (days) and top speed (days per second)
    paddle = [(0.0, vp)]
    balls = [dict(u=0.0, v=3.0, du=speed * .8, dv=speed * .6, born=0.0, lost=None, ev=[(0.0, 0.0, 3.0)])]
    pending = list(splits)
    breaks = {t for t, _ in SK[1:-1]}
    serve_at = None
    t, dt = 0.0, 1 / 240
    while t < T:
        sc = scroll_at(t)
        rate = (scroll_at(t + dt) - sc) / dt
        kink = any(t < bt <= t + dt for bt in breaks)
        live = [b for b in balls if b["lost"] is None]
        if not live and serve_at is None:
            serve_at = t + .6
        if serve_at is not None and t >= serve_at:
            serve_at = None
            ang = rng.uniform(.3, .7) * (1 if rng.random() < .5 else -1)
            nb = dict(u=sc - .4, v=vp, du=speed * (1 - ang * ang) ** .5 + rate, dv=speed * ang, born=t, lost=None,
                      ev=[(t, -.4, vp)])
            balls.append(nb)
            live = [nb]
        if pending and t >= pending[0] and live:
            pending.pop(0)
            b0 = live[0]
            ang = rng.uniform(.3, .8) * (1 if rng.random() < .5 else -1)
            nb = dict(u=b0["u"], v=b0["v"], du=speed * (1 - ang * ang) ** .5 * (1 if b0["du"] > rate else -1) + rate,
                      dv=speed * ang, born=t, lost=None, ev=[(t, b0["u"] - sc, b0["v"])])
            balls.append(nb)
            b0["ev"].append((t, b0["u"] - sc, b0["v"]))
            live.append(nb)
        # paddle: chase the ball that reaches the front edge first
        coming = [((b["u"] - sc + .55) / (rate - b["du"]), b) for b in live if b["du"] < rate]
        if coming:
            target = min(coming, key=lambda x: x[0])[1]["v"]
            vp += max(-PSPEED * dt, min(PSPEED * dt, target - vp))
            vp = max(.4, min(5.6, vp))
        for b in live:
            nu, nv = b["u"] + b["du"] * dt, b["v"] + b["dv"] * dt
            hit = False
            if nv < -.5 + R or nv > 6.5 - R:
                b["dv"], nv, hit = -b["dv"], b["v"], True
            if nu - sc > VIEW - .5 - R and b["du"] > rate:
                b["du"], nu, hit = 2 * rate - b["du"], b["u"], True
            if nu - sc < -.55 and b["du"] < rate:
                if abs(nv - vp) <= HALF + R:  # on the paddle: bounce with a little english from where it hit
                    ang = max(-.75, min(.75, (nv - vp) / (HALF + R) * .6 + rng.uniform(-.15, .15)))
                    b["du"], b["dv"] = speed * (1 - ang * ang) ** .5 + rate, speed * ang
                    nu, hit = b["u"], True
                else:  # missed: the ball is lost
                    b["lost"] = t
                    b["ev"].append((t, nu - sc, nv))
                    continue
            for cu in {round(nu - R), round(nu + R)}:
                for cv in {round(nv - R), round(nv + R)}:
                    c = (cu, cv)
                    if c in alive and c not in gone and -.5 <= cu - sc <= VIEW - .5 and not hit:
                        gone[c] = t
                        if abs(nu - cu) > abs(nv - cv):
                            b["du"] = 2 * rate - b["du"]
                        else:
                            b["dv"] = -b["dv"]
                        nu, nv, hit = b["u"], b["v"], True
            b["u"], b["v"] = nu, nv
            if hit or kink:
                b["ev"].append((t + dt, b["u"] - scroll_at(t + dt), b["v"]))
        for c in alive:  # bricks that reach the paddle line shatter
            if c not in gone and c[0] - sc < -.4:
                gone[c] = t
        if t - paddle[-1][0] >= .05:
            paddle.append((t, vp))
        t += dt
    paddle.append((T, vp))
    for b in balls:
        if b["lost"] is None:
            b["ev"].append((T, b["u"] - scroll_at(T), b["v"]))
        else:
            b["ev"].append((T,) + b["ev"][-1][1:])

    mx = max(max(w) for w in COUNT) or 1
    cols = [P["s1"], P["sapphire"], P["blue"], P["mauve"], P["pink"]]
    board = []
    for i, j in sorted(((i, j) for i in range(NW) for j in range(7)), key=lambda p: (p[1] - p[0], p[0])):
        x, y = pos(i, j)
        board.append(cube2(x, y, 2, P["s0"]))
        if (i, j) in alive:
            z = 8 + (COUNT[i][j] / mx) ** .5 * 46
            g = cube2(x, y, z, cols[GRID[i][j]])
            k = gone.get((i, j), T) / T
            if k < 1:
                k2 = min(.9999, k + .35 / T)
                board.append(f'<g>{g}<animate attributeName="visibility" values="visible;hidden;visible" '
                             f'keyTimes="0;{k:.4f};1" calcMode="discrete" dur="{T}s" repeatCount="indefinite"/></g>')
                board.append(f'<circle cx="{x}" cy="{y - z / 2}" r="0" fill="{P["peach"]}" opacity="0" filter="url(#glow)">'
                             f'<animate attributeName="r" values="0;0;20;20" keyTimes="0;{k:.4f};{k2:.4f};1" dur="{T}s" repeatCount="indefinite"/>'
                             f'<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;{k:.4f};{k2:.4f};1" dur="{T}s" repeatCount="indefinite"/></circle>')
            else:
                board.append(g)
    # the board scrolls toward the paddle: one week of travel moves the screen by (-A, +B)
    sv = ";".join(f"{-sk * A:.1f},{sk * B:.1f}" for _, sk in SK)
    skt = ";".join(f"{tk / T:.4f}" for tk, _ in SK)
    scroll = (f'<animateTransform attributeName="transform" type="translate" values="{sv}" keyTimes="{skt}" '
              f'dur="{T}s" repeatCount="indefinite"/>')
    c1, c4 = pos(-.5, -.5), pos(-.5, 6.5)
    c2, c3 = pos(VIEW + 1.5, -.5), pos(VIEW + 1.5, 6.5)  # clip past the back edge; the mask fades bricks in
    clip = f"{c1[0]},{c1[1] - 90} {c2[0]},{c2[1] - 90} {c3[0]},{c3[1]} {c4[0]},{c4[1] + 12} {c1[0] - A},{c1[1] + 12}"
    f0, f1 = pos(VIEW - 4, 3), pos(VIEW + .5, 3)
    out = [f'<g clip-path="url(#win)" mask="url(#fade)"><g>{"".join(board)}{scroll}</g></g>']
    # paddle on the front short edge, following the lead ball's day position
    kt = ";".join(f"{pt / T:.4f}" for pt, _ in paddle)
    pv = ";".join(f"{v * A:.1f},{v * B:.1f}" for _, v in paddle)
    px, py = pos(-1.0, 0)
    out.append(f'<g><line x1="{px - .9 * A}" y1="{py - .9 * B}" x2="{px + .9 * A}" y2="{py + .9 * B}" stroke="{P["lavender"]}" '
               f'stroke-width="8" stroke-linecap="round" filter="url(#glow)"/>'
               f'<animateTransform attributeName="transform" type="translate" values="{pv}" keyTimes="{kt}" dur="{T}s" repeatCount="indefinite"/></g>')
    # balls: shadow, trail and glowing ball, each visible from its birth
    hues = [P["text"], P["sky"], P["yellow"], P["green"], P["peach"]]
    for n, b in enumerate(balls):
        ev = b["ev"]
        if ev[0][0] > 0:
            ev = [(0.0,) + ev[0][1:]] + ev
        kt = ";".join(f"{e[0] / T:.4f}" for e in ev)
        pts = [pos(e[1], e[2]) for e in ev]
        vals, kts = (["hidden", "visible"], ["0", f'{b["born"] / T:.4f}']) if b["born"] else (["visible"], ["0"])
        if b["lost"] is not None:
            vals.append("hidden")
            kts.append(f'{b["lost"] / T:.4f}')
        vis = (f'<animate attributeName="visibility" values="{";".join(vals)}" keyTimes="{";".join(kts)}" calcMode="discrete" '
               f'dur="{T}s" repeatCount="indefinite"/>' if len(vals) > 1 else "")
        floor = ";".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        air = ";".join(f"{x:.1f},{y - 10:.1f}" for x, y in pts)
        mo = f'keyTimes="{kt}" calcMode="linear" dur="{T}s" repeatCount="indefinite"'
        c = hues[n % len(hues)]
        g = [f'<ellipse rx="7" ry="3.5" fill="#000" opacity=".45"><animateMotion values="{floor}" {mo}/></ellipse>']
        for k, (r, op) in enumerate([(5, .4), (4, .25), (3, .14)]):
            g.append(f'<circle r="{r}" fill="{c}" opacity="{op}"><animateMotion values="{air}" {mo} begin="{(k + 1) * .04:.2f}s"/></circle>')
        g.append(f'<circle r="6.5" fill="{c}" filter="url(#glow)"><animateMotion values="{air}" {mo}/></circle>')
        out.append(f'<g visibility="{vals[0]}">{vis}{"".join(g)}</g>')
    defs = (f'<clipPath id="win"><polygon points="{clip}"/></clipPath>'
            f'<linearGradient id="fg" gradientUnits="userSpaceOnUse" x1="{f0[0]}" y1="{f0[1]}" x2="{f1[0]}" y2="{f1[1]}">'
            '<stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
            f'<mask id="fade" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="470"><rect width="{W}" height="470" fill="url(#fg)"/></mask>'
            '<filter id="glow" x="-1" y="-1" width="3" height="3"><feGaussianBlur stdDeviation="2.5" result="b"/>'
            '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    return frame("".join(out), f"breakout ❯ pit · {len(balls)} balls · a year of commits", 470, defs)


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render())
