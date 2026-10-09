"""Regression re-check, split-app. Controls that move rows and do not arm the guard: is there a data effect?

Usage: python probe_unarmed.py [A] [B] [C]   (default: all three parts)
Serves the project root on a free loopback port, headless Chromium, stops both. Prints a summary and writes
unarmed-results-<parts>.json next to this script.
Clipboard: rig.new_context only (recorder), no permissions, no bypass_csp (CG-7).

A  "Dismiss note": the solver measured the CENTRE of the button at 291 viewports and found a heading or a div every time.
   A repeat press can land anywhere on the 44 px button, so this scans 9 points of the whole button (corners and edges
   included) at widths 320 to 1280 step 20, heights 568 and 844, with 2, 3 and 5 people, and lists every point where an
   ENABLED button (not a heading, a div or an input) is under the pointer once the note is gone. For each such point it then
   performs the real double click there on a fresh page and reads the people before and after.
B  The two mode labels: a double click, a triple click and a double tap at the left, centre and right of each label, three
   sizes, from the even bill and the by-item bill, against the single click of the same label: same stored bill?
C  A price or rate error appears when its field is left and pushes everything under it down by a line (RD-3 holds the first
   press back until mouseup, so the click is not lost). The repeat press then lands on whatever is a line higher in the
   content. For every control under such a field, every point of its box (3 x 3), this reads what is under that point once the
   error shows and lists the points where it is a Remove, an Add, New bill, Copy, Dismiss, a toggle or a mode label (the controls
   that arm the guard themselves, Remove and Add, are skipped as the pressed control).
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[5]
assert (PROJECT / "index.html").is_file(), PROJECT
sys.path.insert(0, str(PROJECT / "tests" / "browser"))

import rig  # noqa: E402
import seeds  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

OUT = {"A": {}, "B": {}, "C": {}}
SETTLE_JS = "() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))"
CLASSIFY_JS = r"""
const SEL = 'button, input, label';
const classify = (e) => {
  if (!e) return 'nothing';
  const b = e.closest(SEL);
  if (!b) return 'non-control:' + e.tagName.toLowerCase();
  const al = b.getAttribute('aria-label') || '';
  const dis = b.disabled ? ' (disabled)' : '';
  if (b.tagName === 'LABEL') return 'mode-label';
  if (b.tagName === 'INPUT') return 'input:' + (al.replace(/\d+/, 'N') || b.type);
  if (/^Remove/.test(al)) return 'REMOVE' + dis;
  if (b.closest('.who')) return 'toggle' + dis;
  return 'button:' + ((b.textContent || '').trim().slice(0, 16) || al) + dis;
};
"""
UNDER_JS = "([x, y]) => { " + CLASSIFY_JS + " return classify(document.elementFromPoint(x, y)); }"


def open_page(browser, base, seed, size, touch=False):
    options = {"viewport": {"width": size[0], "height": size[1]}, "device_scale_factor": 1, "color_scheme": "light"}
    if seed is not None:
        options["storage_state"] = rig.storage_state(base, seed)
    if touch:
        options["has_touch"] = True
    context = rig.new_context(browser, **options)
    page = context.new_page()
    errors = []
    page.on("console", lambda m: errors.append(f"console {m.type}: {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(f"page error: {e}"))
    page.goto(base + "/")
    return context, page, errors


def settle(page, ms=0):
    page.evaluate(SETTLE_JS)
    if ms:
        page.wait_for_timeout(ms)


def stored(page):
    text = page.evaluate("localStorage.getItem('split.draft')")
    return json.loads(text)["bill"] if text else None


def active(page):
    return page.evaluate("() => document.activeElement.getAttribute('aria-label') || document.activeElement.textContent.trim() || document.activeElement.tagName")


def gesture(page, kind, point):
    if kind == "dbl":
        page.mouse.dblclick(*point)
    elif kind == "triple":
        page.mouse.click(*point, click_count=3)
    elif kind == "tap2":
        page.touchscreen.tap(*point)
        page.touchscreen.tap(*point)
    else:
        page.mouse.click(*point)
    settle(page)


# ------------------------------------------------------------------------------------------------------------------ A
def dismiss_ready(page, people):
    for _ in range(people - 2):
        page.get_by_role("button", name="Add person", exact=True).click()
    settle(page)
    return page.get_by_role("button", name="Dismiss note", exact=True)


def part_a(browser, base):
    seen, hits, rows = Counter(), [], 0
    grid = [2, 22, 42]
    for height in (568, 844):
        for width in range(320, 1281, 20):
            for people in (2, 3, 5):
                context, page, _ = open_page(browser, base, seeds.UNREADABLE["B1"], (width, height))
                try:
                    box = dismiss_ready(page, people).bounding_box()
                    if not box:
                        raise RuntimeError("no Dismiss note box")
                    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)  # the first click, centre
                    settle(page)
                    for dx in grid:
                        for dy in grid:
                            x, y = box["x"] + min(dx, box["width"] - 2), box["y"] + min(dy, box["height"] - 2)
                            what = page.evaluate(UNDER_JS, [x, y])
                            seen[what] += 1
                            rows += 1
                            if what.startswith(("REMOVE", "button:", "toggle", "mode-label")) and "(disabled)" not in what:
                                hits.append({"width": width, "height": height, "people": people, "dx": dx, "dy": dy, "under": what,
                                             "point": [x, y], "box": box})
                finally:
                    context.close()
    print(f"A. Dismiss note, {rows} points over {len(seen)} kinds of target:")
    for what, count in seen.most_common():
        print(f"   {count:5}  {what}")
    print(f"   points with an enabled control under them: {len(hits)}", flush=True)
    real = []
    tried = set()
    for hit in hits:
        key = (hit["width"], hit["height"], hit["people"], hit["under"])
        if key in tried or len(tried) >= 8:
            continue
        tried.add(key)
        context, page, _ = open_page(browser, base, seeds.UNREADABLE["B1"], (hit["width"], hit["height"]))
        try:
            dismiss_ready(page, hit["people"])
            before = stored(page)
            page.mouse.dblclick(*hit["point"])
            settle(page)
            after = stored(page)
            real.append({"hit": hit, "people_before": len(before["people"]), "people_after": len(after["people"]),
                         "bill_equal": before == after, "focus": active(page)})
        finally:
            context.close()
    for item in real:
        h = item["hit"]
        print(f"   REAL double click {h['width']}x{h['height']} {h['people']} people at ({h['dx']},{h['dy']}) under {h['under']}: "
              f"people {item['people_before']} -> {item['people_after']}, bill equal {item['bill_equal']}, focus {item['focus']!r}")
    OUT["A"] = {"points": rows, "kinds": dict(seen), "enabled_control_hits": hits, "real_double_clicks": real}


# ------------------------------------------------------------------------------------------------------------------ B
def part_b(browser, base):
    diffs, rows = [], 0
    for seed_name, seed in (("S2-even", seeds.S2), ("S1-item", seeds.S1)):
        for size in ((360, 640), (390, 844), (1280, 800)):
            for label in ("Even", "By item"):
                for place, frac in (("left", 0.1), ("centre", 0.5), ("right", 0.9)):
                    twin = {}
                    for kind in ("single", "dbl", "triple", "tap2"):
                        context, page, errors = open_page(browser, base, seed, size, touch=kind == "tap2")
                        try:
                            loc = page.locator("fieldset.mode label", has_text=label).first
                            box = loc.bounding_box()
                            gesture(page, kind, (box["x"] + box["width"] * frac, box["y"] + box["height"] / 2))
                            twin[kind] = {"bill": stored(page), "focus": active(page), "errors": errors}
                        finally:
                            context.close()
                    for kind in ("dbl", "triple", "tap2"):
                        rows += 1
                        if twin[kind]["bill"] != twin["single"]["bill"] or twin[kind]["errors"]:
                            diffs.append({"seed": seed_name, "size": size, "label": label, "place": place, "kind": kind,
                                          "single": twin["single"], "repeat": twin[kind]})
    print(f"B. mode labels: {rows} repeat-gesture rows against their single click, rows whose stored bill differs: {len(diffs)}", flush=True)
    OUT["B"] = {"rows": rows, "differences": diffs}


# ------------------------------------------------------------------------------------------------------------------ C
def five_people(seed):
    def edit(d):
        d["bill"]["people"] = [{"id": f"p{n}", "name": f"P{n}"} for n in range(1, 6)]
        d["bill"]["nextId"] = 9
    return seeds.changed(seed, edit)


C_CASES = [  # (name, seed, the field made bad)
    ("S1 item 1 price", seeds.S1, "Item 1 price in RM"),
    ("S1 item 2 price", seeds.S1, "Item 2 price in RM"),
    ("S1 item 4 price", seeds.S1, "Item 4 price in RM"),
    ("S1 service", seeds.S1, "Service charge in percent"),
    ("S1 sst", seeds.S1, "SST in percent"),
    ("S1+5 people item 1 price", five_people(seeds.S1), "Item 1 price in RM"),
    ("S1+5 people item 2 price", five_people(seeds.S1), "Item 2 price in RM"),
    ("S2 subtotal", seeds.S2, "Subtotal in RM"),
    ("S2 service", seeds.S2, "Service charge in percent"),
]
COLLECT_JS = "() => { " + CLASSIFY_JS + r"""
  const out = [];
  const nodes = [...document.querySelectorAll('button, input:not([type=radio]), .mode label')];
  for (const n of nodes) {
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
    for (const fx of [0.1, 0.5, 0.9]) for (const fy of [0.1, 0.5, 0.9]) {
      const x = b.x + b.w * fx, y = b.y + b.h * fy;
      const now = classify(document.elementFromPoint(x, y));
      if (now !== b.cls) out.push({ from: b.cls, name: b.name, to: now, x, y });
    }
  }
  return out;
}"""


def part_c(browser, base):
    armers = ("REMOVE", "button:Add person", "button:Add item")
    acting = ("REMOVE", "button:", "mode-label", "toggle")
    summary, candidates, total_points, shifted = Counter(), [], 0, 0
    for width in (320, 360, 390, 412, 600, 768, 1024, 1280):
        for name, seed, field in C_CASES:
            context, page, errors = open_page(browser, base, seed, (width, 3000))
            try:
                boxes = page.evaluate(COLLECT_JS)
                total_points += len(boxes) * 9
                target = page.get_by_role("textbox", name=field, exact=True)
                target.fill("abc")
                target.press("Tab")
                settle(page)
                if page.locator("p.error").count() == 0:
                    raise RuntimeError(f"no error showed for {name} at {width}")
                moved = page.evaluate(HITS_JS, boxes)
                shifted += len(moved)
                for m in moved:
                    if m["from"].startswith(armers) or "(disabled)" in m["to"]:
                        continue
                    if m["to"].startswith(acting):
                        summary[(m["from"], m["to"])] += 1
                        if m["to"].startswith(("REMOVE", "button:Add", "button:New bill", "button:Dismiss")):
                            candidates.append({"width": width, "case": name, "field": field, "move": m, "errors": errors})
            finally:
                context.close()
    print(f"C. error shift: {total_points} control points checked (8 widths x {len(C_CASES)} cases), {shifted} of them end under a different element")
    for (src, dst), count in summary.most_common(40):
        print(f"   {count:5}  pressed {src:<34} repeat press lands on {dst}")
    if not summary:
        print("   none: no repeat press lands on another acting control")
    print(f"   points where a Remove, an Add, New bill or Dismiss note ends up under a non-arming control: {len(candidates)}", flush=True)
    OUT["C"] = {"points": total_points, "ended_under_a_different_element": shifted,
                "landings": [{"from": k[0], "to": k[1], "count": v} for k, v in summary.items()],
                "destructive_candidates": candidates[:40]}


def main():
    parts = [a.upper() for a in sys.argv[1:]] or ["A", "B", "C"]
    server = rig.StaticServer(PROJECT).start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                if "A" in parts:
                    part_a(browser, server.base)
                if "B" in parts:
                    part_b(browser, server.base)
                if "C" in parts:
                    part_c(browser, server.base)
            finally:
                browser.close()
    finally:
        server.stop()
        (HERE / ("unarmed-results-" + "".join(parts) + ".json")).write_text(json.dumps(OUT, indent=1, default=str), encoding="utf-8")


main()
