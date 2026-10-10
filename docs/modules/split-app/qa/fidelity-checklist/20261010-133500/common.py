"""Shared helpers for the split-app fidelity checklist scripts (finder evidence, read-only on the product).

Everything here reads the product. Nothing writes outside the evidence folder this file sits in.
Contexts are made with rig.new_context, so every one carries a clipboard recorder (or the reject script):
no run can reach the operating system clipboard, and bypass_csp is never set, so the shipped CSP is live.
"""
import sys

sys.dont_write_bytecode = True

import json
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT / "tests" / "browser"))
import rig  # noqa: E402
import seeds  # noqa: E402

DESIGN = ROOT / "docs" / "design"
CHROMIUM_ARGS = ["--force-color-profile=srgb", "--hide-scrollbars", "--disable-lcd-text"]
FIVE = [(360, 780), (390, 844), (600, 900), (1024, 768), (1280, 800)]
EDGES = [(599, 900), (1023, 768)]

# screen -> (golden file, seed text or None)
SCREENS = {
    "bill-empty": ("bill-empty", None),
    "bill-even": ("bill-even", seeds.S2),
    "bill-items": ("bill-items", seeds.S1),
    "bill-unassigned": ("bill-unassigned", seeds.S5),
    "new-bill-dialog": ("new-bill-dialog", seeds.S2),
}

# ---- colours (system.css tokens as computed rgb strings) ----
TOKENS = {
    "page": "#EEF0EE", "surface": "#FBFCFB", "field": "#FDFEFD", "ink": "#141917", "ink-hover": "#2A302D",
    "ink-muted": "#4A524E", "ink-disabled": "#9AA19D", "on-ink": "#F3F5F4", "line": "#C9CECB",
    "line-strong": "#78807C", "hover": "#E3E7E4", "accent": "#0B6B4D", "error": "#B42318",
}


def rgb(token):
    h = TOKENS.get(token, token).lstrip("#")
    return "rgb(%d, %d, %d)" % (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


SCRIM = "rgba(20, 25, 23, 0.48)"

# Shorthands that getComputedStyle does not list when iterated (it lists longhands), read by name so they can be compared and checked.
SHORTHANDS = ("overflow", "gap", "background-position", "transition", "outline", "inset", "margin", "padding", "border-radius", "flex",
              "font", "white-space", "text-wrap", "font-variant", "list-style")

# ---- the in-page walkers ----
WALK_JS = r"""
(shorthands) => {
  const out = [];
  const sx = window.scrollX, sy = window.scrollY;
  const dumpCS = (cs) => { const o = {}; for (let i = 0; i < cs.length; i++) { const p = cs[i]; o[p] = cs.getPropertyValue(p); }
    for (const s of shorthands) o[s] = cs.getPropertyValue(s); return o; };
  const norm = (s) => s.replace(/\s+/g, ' ').trim();
  function rec(el, depth, parent) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none') return;
    const r = el.getBoundingClientRect();
    const attrs = {}; for (const a of el.attributes) attrs[a.name] = a.value;
    let own = ''; for (const n of el.childNodes) if (n.nodeType === 3) own += n.nodeValue;
    const idx = out.length;
    const item = { idx, depth, parent, tag: el.tagName.toLowerCase(), id: el.id || '',
      cls: (el.getAttribute('class') || '').split(/\s+/).filter(Boolean).sort().join(' '),
      attrs, text: norm(own), rect: [r.x + sx, r.y + sy, r.width, r.height], cs: dumpCS(cs) };
    for (const pe of ['::before', '::after']) {
      const pcs = getComputedStyle(el, pe);
      if (pcs.content !== 'none' && pcs.content !== 'normal') item[pe] = dumpCS(pcs);
    }
    if (el.tagName === 'INPUT') { item.value = el.value; item.checked = el.checked; item.disabled = el.disabled; }
    if (el.tagName === 'BUTTON') item.disabled = el.disabled;
    out.push(item);
    for (const c of el.children) rec(c, depth + 1, idx);
  }
  for (const c of document.body.children) rec(c, 0, -1);
  return out;
}
"""

# One element (the n-th match among elements that are really rendered), with everything a row may want.
ONE_JS = r"""
([sel, nth, shorthands]) => {
  const list = Array.from(document.querySelectorAll(sel)).filter((e) => e.getClientRects().length > 0);
  const el = list[nth];
  if (!el) return null;
  const sx = window.scrollX, sy = window.scrollY;
  const dumpCS = (cs) => { const o = {}; for (let i = 0; i < cs.length; i++) { const p = cs[i]; o[p] = cs.getPropertyValue(p); }
    for (const s of shorthands) o[s] = cs.getPropertyValue(s); return o; };
  const cs = getComputedStyle(el);
  const r = el.getBoundingClientRect();
  const attrs = {}; for (const a of el.attributes) attrs[a.name] = a.value;
  let own = ''; for (const n of el.childNodes) if (n.nodeType === 3) own += n.nodeValue;
  const item = { n: list.length, tag: el.tagName.toLowerCase(), id: el.id || '', cls: (el.getAttribute('class') || ''),
    attrs, text: (el.textContent || '').replace(/\s+/g, ' ').trim(), own: own.replace(/\s+/g, ' ').trim(),
    rect: [r.x + sx, r.y + sy, r.width, r.height], cs: dumpCS(cs) };
  for (const pe of ['::before', '::after']) {
    const pcs = getComputedStyle(el, pe);
    if (pcs.content !== 'none' && pcs.content !== 'normal') item[pe] = dumpCS(pcs);
  }
  if (el.tagName === 'INPUT') { item['::placeholder'] = dumpCS(getComputedStyle(el, '::placeholder')); }
  if (el.tagName === 'INPUT') { item.value = el.value; item.checked = el.checked; item.disabled = el.disabled; item.focused = document.activeElement === el; }
  if (el.tagName === 'BUTTON') { item.disabled = el.disabled; item.focused = document.activeElement === el; }
  item.focusVisible = el.matches(':focus-visible');
  item.hover = el.matches(':hover');
  return item;
}
"""

COUNT_JS = r"""
(sel) => Array.from(document.querySelectorAll(sel)).filter((e) => e.getClientRects().length > 0).length
"""


class Pg:
    """A page with the small query helpers the row scripts use."""

    def __init__(self, page, label):
        self.page, self.label = page, label
        self.console = []
        page.on("console", lambda m: self.console.append((m.type, m.text)) if m.type in ("error", "warning") else None)
        page.on("pageerror", lambda e: self.console.append(("pageerror", str(e))))

    def one(self, sel, nth=0):
        return self.page.evaluate(ONE_JS, [sel, nth, list(SHORTHANDS)])

    def count(self, sel):
        return self.page.evaluate(COUNT_JS, sel)

    def walk(self):
        return self.page.evaluate(WALK_JS, list(SHORTHANDS))

    def js(self, expr, arg=None):
        return self.page.evaluate(expr, arg) if arg is not None else self.page.evaluate(expr)


def launch(pw):
    return pw.chromium.launch(args=CHROMIUM_ARGS)


def gold_ctx(browser, size, motion="reduce", scheme="light", **opts):
    return browser.new_context(viewport={"width": size[0], "height": size[1]}, device_scale_factor=1,
                               reduced_motion=motion, color_scheme=scheme, **opts)


def app_ctx(browser, base, size, seed=None, motion="reduce", scheme="light", clipboard="recorder", **opts):
    kw = dict(viewport={"width": size[0], "height": size[1]}, device_scale_factor=1, reduced_motion=motion, color_scheme=scheme)
    if seed is not None:
        kw["storage_state"] = rig.storage_state(base, seed)
    kw.update(opts)
    return rig.new_context(browser, clipboard=clipboard, **kw)


def open_golden(ctx, name):
    pg = Pg(ctx.new_page(), "golden:" + name)
    pg.page.goto((DESIGN / f"{name}.html").as_uri(), wait_until="load")
    pg.page.wait_for_timeout(150)
    return pg


def open_app(ctx, base, label="app"):
    pg = Pg(ctx.new_page(), label)
    pg.page.goto(base + "/", wait_until="networkidle")
    pg.page.wait_for_timeout(150)
    return pg


def new_bill_by_mouse(pg):
    """M1 by a real mouse click on the header button, the way a person opens it (no synthetic click, no blur)."""
    pg.page.click("header .btn")
    pg.page.wait_for_timeout(200)


# ---- diff helpers ----
def sig(item):
    return f"{item['depth']}|{item['tag']}|{item['id']}|{item['cls']}"


def style_diff(a, b, ignore=()):
    out = {}
    for k in sorted(set(a) | set(b)):
        if k in ignore:
            continue
        if a.get(k) != b.get(k):
            out[k] = [a.get(k), b.get(k)]
    return out


def rect_equal(a, b, tol=0.01):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def now():
    return time.strftime("%Y%m%d-%H%M%S")


def dump(name, data):
    (HERE / name).write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
