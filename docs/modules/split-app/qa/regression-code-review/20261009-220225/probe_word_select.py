"""Regression code review, split-app. Probe 3: the user-visible cost of a guard that never lets go of its mousedown
listener (mutant M1). After a Remove click and one ordinary click, does a double click on a name still select the word?

Usage: python probe_word_select.py <root> <label>
Writes word-select-<label>.json next to this script. Clipboard: rig.new_context only (recorder).
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


def centre(box):
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def selected(page):
    return page.evaluate("() => { const i = document.activeElement; return i.value.slice(i.selectionStart, i.selectionEnd); }")


def main():
    server = rig.StaticServer(ROOT).start()
    result = {}
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                context = rig.new_context(browser, viewport={"width": 390, "height": 844}, device_scale_factor=1,
                                          storage_state=rig.storage_state(server.base, seeds.S2))
                page = context.new_page()
                page.goto(server.base + "/")
                name = page.get_by_label("Person 1 name", exact=True)
                # 1. a double click on a name before any Remove: the control
                name.dblclick()
                result["word selected before any Remove click"] = selected(page)
                # 2. one Remove click (arms the guard), then one ordinary click elsewhere (ends it)
                page.get_by_role("button", name="Remove Chen", exact=True).click()
                page.wait_for_timeout(700)
                page.mouse.click(5, 400)
                page.wait_for_timeout(700)
                # 3. the same double click again
                name.dblclick()
                result["word selected after a Remove click and one ordinary click"] = selected(page)
                context.close()
            finally:
                browser.close()
    finally:
        server.stop()
    (HERE / f"word-select-{LABEL}.json").write_text(json.dumps({"label": LABEL, "root": str(ROOT), **result}, indent=1), encoding="utf-8")
    print(LABEL, json.dumps(result))


main()
