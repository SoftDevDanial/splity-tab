"""Regression code review, split-app. Probe 1: does the first click of a double click on Add person or Add item
leave the NEW row's Remove button under the pointer?

Reason. Before the security solver (071577a) the Remove handlers ignored any click with a count above 1, whatever
armed or did not arm a guard. Since 071577a they call swallowRepeatClicks() and then remove, so a repeat click
that reaches a Remove button with no guard armed now removes. Add person and Add item do not arm the guard.

Usage: python probe_add_geometry.py <root> <label>
<root> is the folder that holds index.html and src/ (the project, or a scratch copy of 61c3cd3).
Reads nothing but the page. Writes one JSON file next to this script. Clipboard: rig.new_context only (recorder).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[5]
assert (PROJECT / "index.html").is_file(), PROJECT
sys.path.insert(0, str(PROJECT / "tests" / "browser"))

import rig  # noqa: E402
import seeds  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

ROOT = Path(sys.argv[1]).resolve()
LABEL = sys.argv[2]
WIDTHS = [320, 360, 375, 390, 412, 600, 768, 1024, 1280]
HEIGHT = 1400  # tall, so the whole bill is on screen and nothing scrolls


def people_seed(count):
    def edit(draft):
        draft["bill"]["people"] = [{"id": f"p{n}", "name": f"P{n}"} for n in range(1, count + 1)]
        draft["bill"]["nextId"] = count + 1
    return seeds.changed(seeds.S2, edit)


def items_seed(count):
    def edit(draft):
        draft["bill"]["items"] = draft["bill"]["items"][:count]
    return seeds.changed(seeds.S1, edit)


def open_page(browser, base, seed, width, touch=False):
    options = {"viewport": {"width": width, "height": HEIGHT}, "device_scale_factor": 1, "color_scheme": "light"}
    if touch:
        options["has_touch"] = True
    if seed is not None:
        options["storage_state"] = rig.storage_state(base, seed)
    context = rig.new_context(browser, **options)
    page = context.new_page()
    page.goto(base + "/")
    return context, page


def centre(box):
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def overlap(a, b):
    x0, x1 = max(a["x"], b["x"]), min(a["x"] + a["width"], b["x"] + b["width"])
    y0, y1 = max(a["y"], b["y"]), min(a["y"] + a["height"], b["y"] + b["height"])
    return None if x0 >= x1 or y0 >= y1 else {"x": [x0, x1], "y": [y0, y1], "point": [(x0 + x1) / 2, (y0 + y1) / 2]}


def probe(browser, base, kind, width, count):
    rows_sel, button_name, seed = (("li.person", "Add person", people_seed(count)) if kind == "people"
                                   else ("li.item", "Add item", items_seed(count)))
    context, page = open_page(browser, base, seed, width)
    try:
        add = page.get_by_role("button", name=button_name, exact=True)
        before = add.bounding_box()
        scroll_before = page.evaluate("window.scrollY")
        page.mouse.click(*centre(before))  # one ordinary click, to see where the new row's Remove button lands
        rows_after = page.locator(rows_sel).count()
        if rows_after != count + 1:
            return {"kind": kind, "width": width, "before": count, "error": f"rows after one click: {rows_after}"}
        remove = page.locator(rows_sel).nth(count).locator("button.icon-btn").bounding_box()
        return {"kind": kind, "width": width, "before": count, "add_button": before, "new_remove": remove,
                "scroll_moved": page.evaluate("window.scrollY") - scroll_before, "overlap": overlap(before, remove)}
    finally:
        context.close()


def main():
    server = rig.StaticServer(ROOT).start()
    rows = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                for width in WIDTHS:
                    for count in (2, 3, 4, 5, 11):
                        rows.append(probe(browser, server.base, "people", width, count))
                    for count in (1, 2, 4):
                        rows.append(probe(browser, server.base, "items", width, count))
            finally:
                browser.close()
    finally:
        server.stop()
    hits = [row for row in rows if row.get("overlap")]
    errors = [row for row in rows if "error" in row]
    out = HERE / f"geometry-{LABEL}.json"
    out.write_text(json.dumps({"label": LABEL, "root": str(ROOT), "rows": len(rows), "with_overlap": len(hits),
                               "errors": errors, "hits": hits, "all": rows}, indent=1), encoding="utf-8")
    print(f"{LABEL}: {len(rows)} geometry rows, {len(errors)} errors, {len(hits)} where the new row's Remove button is under the Add button")
    for row in hits:
        print("  ", row["kind"], "w", row["width"], "n", row["before"], "overlap x", [round(v, 1) for v in row["overlap"]["x"]],
              "y", [round(v, 1) for v in row["overlap"]["y"]], "scroll moved", row["scroll_moved"])
    for row in errors:
        print("   ERROR", row)


main()
