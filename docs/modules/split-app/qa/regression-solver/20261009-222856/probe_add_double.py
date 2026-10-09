"""Regression solver, split-app. Copy of the finder's probe_add_double.py (qa/regression-code-review/20261009-220225/), logic
unchanged, so the solver's run writes its JSON next to this copy and the finder's folder stays as the finder left it.

What does a double click, triple click or double tap on the part of "Add person" that the new row's Remove button lands on do?

Usage: python probe_add_double.py <root> <label>
<root> is the folder with index.html and src/ (the project, or a scratch copy).
For every viewport and starting bill it first measures where the new Remove button lands (one ordinary click on a
fresh page), then on a second fresh page performs the gesture at the middle of the overlap and reads the result:
people left, the stored id counter, what has focus. The centre of the button is the control row.
Writes one JSON file next to this script. Clipboard: rig.new_context only (recorder), no permissions.
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
SIZES = [(360, 640), (390, 844), (1280, 800)]
GESTURES = ["single", "mouse-double", "mouse-triple", "touch-double"]
STARTS = [2, 3, 4, 5]  # people before the add


def people_seed(count):
    def edit(draft):
        draft["bill"]["people"] = [{"id": f"p{n}", "name": f"P{n}"} for n in range(1, count + 1)]
        draft["bill"]["nextId"] = count + 1
    return seeds.changed(seeds.S2, edit)


def fresh(browser, base, count, size, touch):
    options = {"viewport": {"width": size[0], "height": size[1]}, "device_scale_factor": 1, "color_scheme": "light",
               "storage_state": rig.storage_state(base, people_seed(count))}
    if touch:
        options["has_touch"] = True
    context = rig.new_context(browser, **options)
    page = context.new_page()
    page.goto(base + "/")
    return context, page


def centre(box):
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def where_the_new_remove_lands(browser, base, count, size):
    context, page = fresh(browser, base, count, size, False)
    try:
        add = page.get_by_role("button", name="Add person", exact=True)
        add.scroll_into_view_if_needed()
        a = add.bounding_box()
        page.mouse.click(*centre(a))
        r = page.locator("li.person").nth(count).locator("button.icon-btn").bounding_box()
        x0, x1 = max(a["x"], r["x"]), min(a["x"] + a["width"], r["x"] + r["width"])
        y0, y1 = max(a["y"], r["y"]), min(a["y"] + a["height"], r["y"] + r["height"])
        return centre(a), (((x0 + x1) / 2, (y0 + y1) / 2) if x0 < x1 and y0 < y1 else None)
    finally:
        context.close()


def gesture(page, kind, point):
    if kind == "single":
        page.mouse.click(*point)
    elif kind == "mouse-double":
        page.mouse.dblclick(*point)
    elif kind == "mouse-triple":
        page.mouse.click(*point, click_count=3)
    else:
        page.touchscreen.tap(*point)
        page.touchscreen.tap(*point)
    page.evaluate("() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))")


def run_case(browser, base, count, size, kind, where, point):
    context, page = fresh(browser, base, count, size, kind == "touch-double")
    try:
        page.get_by_role("button", name="Add person", exact=True).scroll_into_view_if_needed()
        gesture(page, kind, point)
        draft = json.loads(page.evaluate("localStorage.getItem('split.draft')"))
        label = page.evaluate("document.activeElement.getAttribute('aria-label') || document.activeElement.textContent.trim() || document.activeElement.tagName")
        return {"people_before": count, "size": f"{size[0]}x{size[1]}", "gesture": kind, "where": where,
                "people_after": len(draft["bill"]["people"]), "nextId": draft["bill"]["nextId"],
                "names": [p["name"] for p in draft["bill"]["people"]], "focus": label,
                "dom_rows": page.locator("li.person").count()}
    finally:
        context.close()


def main():
    server = rig.StaticServer(ROOT).start()
    rows = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                for size in SIZES:
                    for count in STARTS:
                        centre_point, edge_point = where_the_new_remove_lands(browser, server.base, count, size)
                        for kind in GESTURES:
                            rows.append(run_case(browser, server.base, count, size, kind, "centre", centre_point))
                            if edge_point:
                                rows.append(run_case(browser, server.base, count, size, kind, "right edge (under new Remove)", edge_point))
            finally:
                browser.close()
    finally:
        server.stop()
    out = HERE / f"add-double-{LABEL}.json"
    out.write_text(json.dumps({"label": LABEL, "root": str(ROOT), "rows": rows}, indent=1), encoding="utf-8")
    print(f"{LABEL}: {len(rows)} rows")
    for row in rows:
        gain = row["people_after"] - row["people_before"]
        flag = "" if gain == 1 else f"   <-- people {gain:+d}"
        print(f'{row["size"]:>8} start {row["people_before"]} {row["gesture"]:<13} {row["where"]:<30} after {row["people_after"]} nextId {row["nextId"]} focus {row["focus"]!r}{flag}')


main()
