"""Regression re-check, split-app. RG-CR-08 probe: a double press on a "who had it" chip while a price error is pending removes the item.

Usage: python probe_toggle_remove.py <root> <label>
<root> is a folder with index.html and src/ (the project, a git archive of 61c3cd3, or a scratch copy with a fix applied).
Writes toggle-remove-<label>.json next to this script and prints a summary.

The mechanism (RD-3): a price error appears when its field is left, and a blur caused by a press waits until mouseup, so the
click on the control the user pressed is not lost. The error line pushes everything under it down, so the SECOND press of a
double click or double tap lands on whatever was a line higher in the content. For the first row of "who had it" chips that
is the item's own line, and at its right end that line holds the item's Remove button. Since 071577a a Remove acts on every
click that reaches it and relies on an earlier Remove, Add or dialog click having armed swallowRepeatClicks, which a chip does not.

For each name set, number of people and width: the item 1 price holds "abc" and has focus; every 4 px point of every chip of the
three items under it is checked for what lies under it once the error shows (scan), then the REAL double click is made at one
point that lands on a Remove and the stored bill is read before and after. A single click at the same point is the control.
Clipboard: rig.new_context only (recorder), no permissions, no bypass_csp (CG-7).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[5]
sys.path.insert(0, str(PROJECT / "tests" / "browser"))

import rig  # noqa: E402
import seeds  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

ROOT = Path(sys.argv[1]).resolve()
LABEL = sys.argv[2]
assert (ROOT / "index.html").is_file(), ROOT
SETTLE_JS = "() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))"
TWELVE = ["Aisyah", "Ben", "Chen", "Devi", "Farid", "Grace", "Hafiz", "Indra", "Jia Hui", "Kumar", "Lina", "Mei Ling"]
LONG = ["Muhammad Aiman", "Nur Aisyah Binti", "Wong Mei Ling", "Siti Nurhaliza", "Ahmad Farhan", "Lim Jia Hui", "Tan Wei Jie",
        "Raj Kumar", "Nurul Izzah", "Chong Kah Wai", "Hafizuddin", "Puteri Balqis"]
NAME_SETS = {"short": [f"P{n}" for n in range(1, 13)], "typical": TWELVE, "long": LONG}
WIDTHS = [360, 375, 390, 412, 600, 768, 1024, 1280]
PEOPLE = list(range(3, 13))

COLLECT_JS = r"""() => {
  window.__chips = [...document.querySelectorAll('.who button')];
  return window.__chips.map((n, index) => { const r = n.getBoundingClientRect(); return { index, name: n.textContent.trim(), x: r.x, y: r.y, w: r.width, h: r.height }; });
}"""
HITS_JS = r"""(boxes) => {
  const out = []; let total = 0;
  for (const b of boxes) {
    const chip = window.__chips[b.index];
    for (let x = b.x + 2; x < b.x + b.w - 1; x += 4) for (let y = b.y + 2; y < b.y + b.h - 1; y += 4) {
      total += 1;
      const e = document.elementFromPoint(x, y);
      const hit = e && e.closest('button');
      if (hit && /^Remove/.test(hit.getAttribute('aria-label') || '') && !hit.disabled) {
        out.push({ chip: b.name, x, y, remove: hit.getAttribute('aria-label'), sameItem: hit.closest('li.item') === chip.closest('li.item') });
      }
    }
  }
  return { total, hits: out };
}"""


def seed_for(names):
    def edit(d):
        d["bill"]["people"] = [{"id": f"p{n}", "name": name} for n, name in enumerate(names, start=1)]
        d["bill"]["nextId"] = 20
    return seeds.changed(seeds.S1, edit)


def open_page(browser, base, seed, width):
    context = rig.new_context(browser, viewport={"width": width, "height": 3000}, device_scale_factor=1, color_scheme="light",
                              storage_state=rig.storage_state(base, seed))
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(base + "/")
    return context, page, errors


def stored(page):
    return json.loads(page.evaluate("localStorage.getItem('split.draft')"))["bill"]


def summary_of(bill):
    return {"items": [i["name"] for i in bill["items"]], "who": [i["who"] for i in bill["items"]]}


def main():
    server = rig.StaticServer(ROOT).start()
    rows = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                for set_name, names in NAME_SETS.items():
                    for count in PEOPLE:
                        seed = seed_for(names[:count])
                        for width in WIDTHS:
                            context, page, _ = open_page(browser, server.base, seed, width)
                            try:
                                boxes = page.evaluate(COLLECT_JS)
                                field = page.get_by_role("textbox", name="Item 1 price in RM", exact=True)
                                field.fill("abc")
                                field.press("Tab")
                                page.evaluate(SETTLE_JS)
                                assert page.locator("p.error").count() == 1
                                scan = page.evaluate(HITS_JS, boxes)
                            finally:
                                context.close()
                            row = {"names": set_name, "people": count, "width": width, "chip_points": scan["total"],
                                   "points_onto_a_remove": len(scan["hits"]), "same_item": sum(1 for h in scan["hits"] if h["sameItem"])}
                            if scan["hits"]:
                                example = scan["hits"][0]
                                row["example"] = example
                                for kind in ("dbl", "single"):
                                    context, page, errors = open_page(browser, server.base, seed, width)
                                    try:
                                        before = stored(page)
                                        field = page.get_by_role("textbox", name="Item 1 price in RM", exact=True)
                                        field.fill("abc")  # focus stays in the field: the press itself blurs it
                                        if kind == "dbl":
                                            page.mouse.dblclick(example["x"], example["y"])
                                        else:
                                            page.mouse.click(example["x"], example["y"])
                                        page.evaluate(SETTLE_JS)
                                        after = stored(page)
                                        row[kind] = {"before": summary_of(before), "after": summary_of(after), "page_errors": errors,
                                                     "items_before": len(before["items"]), "items_after": len(after["items"])}
                                    finally:
                                        context.close()
                            rows.append(row)
            finally:
                browser.close()
    finally:
        server.stop()
    out = HERE / f"toggle-remove-{LABEL}.json"
    out.write_text(json.dumps({"label": LABEL, "root": str(ROOT), "rows": rows}, indent=1), encoding="utf-8")
    affected = [r for r in rows if r["points_onto_a_remove"]]
    removed = [r for r in affected if r["dbl"]["items_after"] < r["dbl"]["items_before"]]
    print(f"{LABEL}: {len(rows)} configurations, {len(affected)} with a chip point that lands on a Remove after the error, "
          f"{len(removed)} where the real double click removed an item, "
          f"{sum(1 for r in affected if r['single']['items_after'] < r['single']['items_before'])} where the single click did")
    for set_name in NAME_SETS:
        for width in WIDTHS:
            counts = [r["people"] for r in rows if r["names"] == set_name and r["width"] == width and r["points_onto_a_remove"]]
            gone = [r["people"] for r in removed if r["names"] == set_name and r["width"] == width]
            print(f"  names {set_name:<8} width {width:>4}: people with a landing {counts}  real double click removed an item for {gone}")


main()
