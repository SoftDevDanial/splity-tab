"""Regression re-check, split-app. Three small claims of the documents, measured.

 1. gesture_at (tests/browser/test_app.py): "A triple click is three presses with click counts 1, 2 and 3, as Playwright's
    click(click_count=3) sends them." The click counts of the mousedown and click events a triple click sends are logged.
 2. README "Known limits": "A double click on Dismiss note or a mode label moves keyboard focus to the page. No data changes."
    The focused element after the double click and whether the stored bill equals the one a single click leaves.
 3. spec R7 / dom.js / BUILD.md call 18: Dismiss note's repeat press "lands on a heading or a div, never on a control":
    the element under the centre of the button after the note is gone, at the three standard sizes (the 2646-point scan of the
    whole button is in probe_unarmed.py part A).
Usage: python probe_claims.py     Clipboard: rig.new_context only (recorder), no permissions, no bypass_csp (CG-7).
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

SETTLE_JS = "() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))"
ACTIVE_JS = "() => { const a = document.activeElement; return a.tagName + (a.getAttribute('aria-label') ? ' [' + a.getAttribute('aria-label') + ']' : ''); }"
UNDER_JS = "([x, y]) => { const e = document.elementFromPoint(x, y); return e.tagName.toLowerCase() + '.' + (e.className || ''); }"
RECORD_JS = """() => {
  window.log = { mousedown: [], click: [] };
  for (const type of ['mousedown', 'click']) document.addEventListener(type, (e) => window.log[type].push(e.detail), true);
}"""
RESULTS = {}


def open_page(browser, base, seed, size=(390, 844), touch=False):
    options = {"viewport": {"width": size[0], "height": size[1]}, "device_scale_factor": 1, "color_scheme": "light"}
    if touch:
        options["has_touch"] = True
    if seed is not None:
        options["storage_state"] = rig.storage_state(base, seed)
    context = rig.new_context(browser, **options)
    page = context.new_page()
    page.goto(base + "/")
    return context, page


def stored(page):
    text = page.evaluate("localStorage.getItem('split.draft')")
    return json.loads(text)["bill"] if text else None


def main():
    server = rig.StaticServer(PROJECT).start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                # 1
                context, page = open_page(browser, server.base, seeds.S2)
                try:
                    page.evaluate(RECORD_JS)
                    box = page.locator("h1.wordmark").bounding_box()
                    page.mouse.click(box["x"] + box["width"] + 30, box["y"] + box["height"] / 2, click_count=3)
                    log = page.evaluate("window.log")
                    RESULTS["triple_click_counts"] = log
                    print("1. triple click, counts seen by the document:", log)
                finally:
                    context.close()
                # 2 and 3
                for size in ((360, 640), (390, 844), (1280, 800)):
                    for what, seed, make in (("Dismiss note", seeds.UNREADABLE["B1"], None), ("By item", seeds.S2, None), ("Even", seeds.S1, None)):
                        twin = {}
                        for kind in ("single", "dbl"):
                            context, page = open_page(browser, server.base, seed, size)
                            try:
                                if what == "Dismiss note":
                                    page.get_by_role("button", name="Add person", exact=True).click()
                                    loc = page.get_by_role("button", name="Dismiss note", exact=True)
                                else:
                                    loc = page.locator("fieldset.mode label", has_text=what).first
                                box = loc.bounding_box()
                                point = (box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                                if kind == "single":
                                    page.mouse.click(*point)
                                else:
                                    page.mouse.dblclick(*point)
                                page.evaluate(SETTLE_JS)
                                twin[kind] = {"bill": stored(page), "focus": page.evaluate(ACTIVE_JS), "under": page.evaluate(UNDER_JS, list(point))}
                            finally:
                                context.close()
                        same = twin["single"]["bill"] == twin["dbl"]["bill"]
                        RESULTS[f"{what} {size[0]}x{size[1]}"] = {"same_bill_as_single_click": same, "focus_single": twin["single"]["focus"],
                                                                  "focus_double": twin["dbl"]["focus"], "under_after": twin["single"]["under"]}
                        print(f"2/3. {what:<13} {size[0]}x{size[1]:<4} bill equal to a single click: {same}, focus after single {twin['single']['focus']!r}, "
                              f"after double {twin['dbl']['focus']!r}, under the pointer {twin['single']['under']}")
            finally:
                browser.close()
    finally:
        server.stop()
        (HERE / "claims-results.json").write_text(json.dumps(RESULTS, indent=1), encoding="utf-8")


main()
