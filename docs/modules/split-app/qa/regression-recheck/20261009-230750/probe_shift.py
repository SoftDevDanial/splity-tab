"""Regression re-check, split-app. Follow-up of probe_unarmed.py part C: the layout shift of a field error (RD-3) puts another
control under a repeat press. This one scans finer (a point every 4 px across every control), with more people (3, 5, 8, 12),
widths 320 and 360 to 1280 step 20, and names every landing. Then it performs the REAL double click at an example point of each
distinct kind of landing, from a field that holds the bad text and has focus (so the press itself causes the blur, as a user does),
and reads what happened to the stored bill.

Usage: python probe_shift.py          writes shift-results.json next to this script
Clipboard: rig.new_context only (recorder), no permissions, no bypass_csp (CG-7).
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[5]
assert (PROJECT / "index.html").is_file(), PROJECT
sys.path.insert(0, str(PROJECT / "tests" / "browser"))

import rig  # noqa: E402
import seeds  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

SETTLE_JS = "() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))"
CLASSIFY_JS = r"""
const SEL = 'button, input, label';
const classify = (e) => {
  if (!e) return 'nothing';
  const b = e.closest(SEL);
  if (!b) return 'non-control:' + e.tagName.toLowerCase();
  const al = b.getAttribute('aria-label') || '';
  const dis = b.disabled ? ' (disabled)' : '';
  if (b.tagName === 'LABEL') return 'mode-label:' + (b.textContent || '').trim();
  if (b.tagName === 'INPUT') return 'input:' + (al.replace(/\d+/, 'N') || b.type);
  if (/^Remove/.test(al)) return 'REMOVE' + dis;
  if (b.closest('.who')) return 'toggle' + dis;
  return 'button:' + ((b.textContent || '').trim().slice(0, 16) || al) + dis;
};
"""
COLLECT_JS = "() => { " + CLASSIFY_JS + r"""
  const out = [];
  for (const n of document.querySelectorAll('button, input:not([type=radio]), .mode label')) {
    if (n.disabled) continue;
    const r = n.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    out.push({ cls: classify(n), name: n.getAttribute('aria-label') || (n.textContent || '').trim().slice(0, 18), x: r.x, y: r.y, w: r.width, h: r.height });
  }
  return out;
}"""
HITS_JS = "(boxes) => { " + CLASSIFY_JS + r"""
  const out = [];
  for (const b of boxes) {
    for (let x = b.x + 2; x < b.x + b.w - 1; x += 4) for (let y = b.y + 2; y < b.y + b.h - 1; y += 4) {
      const now = classify(document.elementFromPoint(x, y));
      if (now !== b.cls) out.push({ from: b.cls, name: b.name, to: now, x, y });
    }
  }
  return out;
}"""
ARMERS = ("REMOVE", "button:Add person", "button:Add item")
ACTING = ("REMOVE", "button:", "mode-label", "toggle")
DESTRUCTIVE = ("REMOVE", "button:Add", "button:New bill", "mode-label")


def people_seed(seed, count):
    def edit(d):
        d["bill"]["people"] = [{"id": f"p{n}", "name": f"P{n}"} for n in range(1, count + 1)]
        d["bill"]["nextId"] = 20
    return seeds.changed(seed, edit)


def open_page(browser, base, seed, size):
    context = rig.new_context(browser, viewport={"width": size[0], "height": size[1]}, device_scale_factor=1, color_scheme="light",
                              storage_state=rig.storage_state(base, seed))
    page = context.new_page()
    page.goto(base + "/")
    return context, page


def stored(page):
    return json.loads(page.evaluate("localStorage.getItem('split.draft')"))["bill"]


CASES = []
for people in (3, 5, 8, 12):
    for field in ("Item 1 price in RM", "Item 2 price in RM", "Item 4 price in RM"):
        CASES.append((f"S1 {people} people, {field}", people_seed(seeds.S1, people), field))
for people in (3, 12):
    for field in ("Subtotal in RM", "Service charge in percent", "SST in percent"):
        CASES.append((f"S2 {people} people, {field}", people_seed(seeds.S2, people), field))
WIDTHS = [320] + list(range(360, 1281, 20))


def main():
    server = rig.StaticServer(PROJECT).start()
    landings = Counter()
    examples = {}
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                for width in WIDTHS:
                    for name, seed, field in CASES:
                        context, page = open_page(browser, server.base, seed, (width, 3000))
                        try:
                            boxes = page.evaluate(COLLECT_JS)
                            target = page.get_by_role("textbox", name=field, exact=True)
                            target.fill("abc")
                            target.press("Tab")
                            page.evaluate(SETTLE_JS)
                            if page.locator("p.error").count() == 0:
                                raise RuntimeError(f"no error for {name} at {width}")
                            for hit in page.evaluate(HITS_JS, boxes):
                                if hit["from"].startswith(ARMERS) or "(disabled)" in hit["to"] or not hit["to"].startswith(ACTING):
                                    continue
                                key = (">=360" if width >= 360 else "<360", hit["from"], hit["to"])
                                landings[key] += 1
                                examples.setdefault(key, {"width": width, "case": name, "field": field, "seed": seed, **hit})
                        finally:
                            context.close()
            finally:
                # the real double click at one example of each landing that is not a toggle, a label or Copy onto a harmless input
                real = []
                for key, ex in examples.items():
                    if not ex["to"].startswith(DESTRUCTIVE):
                        continue
                    context, page = open_page(browser, server.base, ex["seed"], (ex["width"], 3000))
                    try:
                        before = stored(page)
                        field = page.get_by_role("textbox", name=ex["field"], exact=True)
                        field.fill("abc")  # focus stays in the field, so the press below is what blurs it
                        page.mouse.dblclick(ex["x"], ex["y"])
                        page.evaluate(SETTLE_JS)
                        after = stored(page)
                        real.append({"key": list(key), "width": ex["width"], "case": ex["case"], "point": [ex["x"], ex["y"]],
                                     "pressed": ex["name"], "lands_on": ex["to"],
                                     "mode": [before["mode"], after["mode"]], "items": [len(before["items"]), len(after["items"])],
                                     "people": [len(before["people"]), len(after["people"])],
                                     "who_changed": [i["who"] for i in before["items"]] != [i["who"] for i in after["items"]]})
                    finally:
                        context.close()
                browser.close()
    finally:
        server.stop()
    print("landings of a repeat press after a field error (a point every 4 px), grouped by supported width (>=360) or not:")
    for (band, src, dst), count in sorted(landings.items()):
        print(f"  {band:>5} {count:6}  pressed {src:<34} -> {dst}")
    print("real double clicks at one example of each destructive landing:")
    for row in real:
        print("  ", row)
    (HERE / "shift-results.json").write_text(json.dumps({"landings": [{"band": k[0], "from": k[1], "to": k[2], "count": v} for k, v in landings.items()],
                                                         "examples": {"|".join(k): {a: b for a, b in v.items() if a != "seed"} for k, v in examples.items()},
                                                         "real": real}, indent=1), encoding="utf-8")


main()
