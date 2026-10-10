"""Row framework for the FE element checklist.

A row passes when, for every element it names, at every viewport it runs at:
  (A) the running app's element equals the golden's element: rectangle, own text, text content (white space between elements
      ignored, allowed difference 5), input value/checked/disabled, attributes (minus the allowed differences of spec.md), and every
      computed style property Chromium lists (about 400) plus the shorthands common.SHORTHANDS, plus ::before and ::after;
  (B) the literal values qa.md and the design notes give hold on the app's element.
Both halves are reported. Expectations are written from qa.md and system.css, never copied from a measurement.
"""
import sys

sys.dont_write_bytecode = True
import re

import common as C
from dom_diff import attr_diffs

ALIAS = {
    "fs": "font-size", "lh": "line-height", "fw": "font-weight", "color": "color", "bg": "background-color", "ls": "letter-spacing",
    "ta": "text-align", "disp": "display", "pos": "position", "cursor": "cursor", "op": "opacity", "gap": "gap", "mt": "margin-top",
    "mb": "margin-bottom", "ml": "margin-left", "mr": "margin-right", "pt": "padding-top", "pb": "padding-bottom",
    "pl": "padding-left", "pr": "padding-right", "bsh": "box-shadow", "olw": "outline-width", "ols": "outline-style",
    "olc": "outline-color", "olo": "outline-offset", "tf": "transform", "fill": "fill", "cols": "grid-template-columns",
    "bgi": "background-image", "ov": "overflow", "top": "top", "left": "left", "right": "right", "ws": "white-space",
    "fd": "flex-direction", "jc": "justify-content", "ai": "align-items", "bgsize": "background-size", "bgpos": "background-position",
    "mh": "min-height", "wf": "font-variant-numeric", "gc": "grid-column", "owrap": "overflow-wrap", "td": "text-decoration-line",
    "zi": "z-index", "va": "vertical-align", "float": "float", "pe": "pointer-events", "fam": "font-family",
    "trd": "transition-duration", "trp": "transition-property",
}
RECT = {"x": 0, "y": 1, "w": 2, "h": 3}
SIDES = {"bt": "top", "bb": "bottom", "bl": "left", "br": "right"}
TOKEN_BY_RGB = {C.rgb(k): k for k in C.TOKENS}


def border_of(cs, side):
    return f"{cs[f'border-{side}-width']} {cs[f'border-{side}-style']} {cs[f'border-{side}-color']}"


def fmt(v):
    if isinstance(v, float):
        return ("%.2f" % v).rstrip("0").rstrip(".")
    if isinstance(v, str):
        for t, name in TOKEN_BY_RGB.items():
            v = v.replace(t, name)
    return str(v)


def nospace(s):
    return re.sub(r"\s+", "", s or "")


def get(a, key):
    """Value of an expectation key on a one() record."""
    cs = a["cs"]
    if key in RECT:
        return a["rect"][RECT[key]]
    if key == "r":
        return a["rect"][0] + a["rect"][2]
    if key == "b":
        return a["rect"][1] + a["rect"][3]
    if key == "cx":
        return a["rect"][0] + a["rect"][2] / 2
    if key == "cy":
        return a["rect"][1] + a["rect"][3] / 2
    if key == "text":
        return a["text"]
    if key == "own":
        return a["own"]
    if key.startswith("@"):
        return a["attrs"].get(key[1:])
    if key in ("value", "checked", "disabled", "focused", "focusVisible", "hover", "n", "tag", "cls"):
        return a.get(key)
    if key in SIDES:
        return border_of(cs, SIDES[key])
    if key == "b4":
        parts = [border_of(cs, s) for s in ("top", "right", "bottom", "left")]
        return parts[0] if len(set(parts)) == 1 else " | ".join(parts)
    if key == "rad":
        parts = [cs[f"border-{c}-radius"] for c in ("top-left", "top-right", "bottom-right", "bottom-left")]
        return parts[0] if len(set(parts)) == 1 else " ".join(parts)
    if key == "radii":
        return " ".join(cs[f"border-{c}-radius"] for c in ("top-left", "top-right", "bottom-right", "bottom-left"))
    if key == "pad":
        return " ".join(cs[f"padding-{s}"] for s in ("top", "right", "bottom", "left"))
    if key == "mar":
        return " ".join(cs[f"margin-{s}"] for s in ("top", "right", "bottom", "left"))
    if key == "phcolor":
        return a["::placeholder"]["color"]
    return cs[ALIAS.get(key, key)]


def same(got, want, tol):
    if isinstance(want, (int, float)) and not isinstance(want, bool) and isinstance(got, (int, float)):
        return abs(got - want) <= tol
    return got == want


class Rows:
    def __init__(self):
        self.d = {}

    def add(self, rid, vw, ok, text):
        if rid is None:
            return
        self.d.setdefault(rid, {}).setdefault(vw, []).append((ok, text))


class Ctx:
    def __init__(self, rows, app, gold, vw, screen):
        self.R, self.app, self.gold, self.vw, self.screen = rows, app, gold, vw, screen

    def cnt(self, sel, which="app", dom=False):
        pg = self.app if which == "app" else self.gold
        if dom:
            return pg.js("(s) => document.querySelectorAll(s).length", sel)
        return pg.count(sel)


def golden_equal(a, g, ignore=()):
    """(ok, short text). Whole-element comparison of the app's element against the golden's."""
    if g is None:
        return False, "golden has no such element"
    bad = []
    sd = C.style_diff(a["cs"], g["cs"], ignore)
    if sd:
        bad.append("styles " + ", ".join(f"{k}: {v[0]} vs {v[1]}" for k, v in list(sd.items())[:4]))
    if not C.rect_equal(a["rect"], g["rect"]):
        bad.append("rect %s vs %s" % ([round(v, 2) for v in a["rect"]], [round(v, 2) for v in g["rect"]]))
    if a["own"] != g["own"]:
        bad.append("own text %r vs %r" % (a["own"], g["own"]))
    if nospace(a["text"]) != nospace(g["text"]):
        bad.append("text %r vs %r" % (a["text"], g["text"]))
    for k in ("value", "checked", "disabled"):
        if a.get(k) != g.get(k):
            bad.append(f"{k} {a.get(k)} vs {g.get(k)}")
    ad, _ = attr_diffs(g, a)
    if ad:
        bad.append("attrs " + ", ".join(f"{d['attr']}: {d['golden']!r} vs {d['app']!r}" for d in ad[:4]))
    for pe in ("::before", "::after"):
        if (pe in a) != (pe in g):
            bad.append(f"{pe} presence differs")
        elif pe in a:
            psd = C.style_diff(a[pe], g[pe], ignore)
            if psd:
                bad.append(f"{pe} " + ", ".join(f"{k}: {v[0]} vs {v[1]}" for k, v in list(psd.items())[:3]))
    return (not bad), "; ".join(bad)


def ck(ctx, rid, sel, nth=0, exp=None, label=None, gsel=None, ignore=(), tol=0.51, golden=True):
    """Check one element of the app against the golden and against literal values. rid None means: skip."""
    if rid is None:
        return None
    exp = exp or {}
    name = label or sel
    a = ctx.app.one(sel, nth)
    if a is None:
        ctx.R.add(rid, ctx.vw, False, f"{name}: NOT FOUND in the app")
        return None
    ok, parts = True, []
    for key, want in exp.items():
        try:
            got = get(a, key)
        except KeyError:
            ok = False
            parts.append(f"{key}=?? (no such property)")
            continue
        good = same(got, want, tol)
        ok &= good
        parts.append(f"{key}={fmt(got)}" + ("" if good else f" EXPECTED {fmt(want)}"))
    eq_text = ""
    if golden and ctx.gold is not None:
        g = ctx.gold.one(gsel or sel, nth)
        eq, why = golden_equal(a, g, ignore)
        ok &= eq
        eq_text = "= golden" if eq else f"DIFFERS FROM GOLDEN ({why})"
    ctx.R.add(rid, ctx.vw, ok, f"{name}: " + ", ".join(parts + ([eq_text] if eq_text else [])))
    return a


def ck_count(ctx, rid, sel, want, label=None, dom=False):
    if rid is None:
        return
    got = ctx.cnt(sel, "app", dom)
    gwant = ctx.cnt(sel, "gold", dom) if ctx.gold is not None else None
    ok = got == want and (gwant is None or gwant == got)
    ctx.R.add(rid, ctx.vw, ok, f"{label or sel}: count {got}" + ("" if got == want else f" EXPECTED {want}") + (f", golden {gwant}" if gwant is not None else ""))


def note(ctx, rid, ok, text):
    ctx.R.add(rid, ctx.vw, ok, text)


def parse_qa_rows(path):
    """Id -> (element, expected) from the FE element checklist tables of qa.md."""
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| ((?:S1|S2|S3|S5|M1|ST)-\d+) \| (.*?) \| (.*) \|\s*$", line)
        if m:
            rows[m.group(1)] = (m.group(2).strip(), m.group(3).strip())
    return rows
