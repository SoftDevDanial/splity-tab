"""Regression QA, diagnostic for flow 5 part B: does the scout find the press point the suite uses?

The suite's RG-CR-08 test (test_R7_a_repeat_press_on_a_chip_under_a_pending_price_error_never_removes_the_item) builds
its bill from a stored draft (eight people, the four S1 items) and probes at 390 x 3000. This script runs the same
scout on the same bill at 390 x 3000 and at 390 x 844, and on the one-item bill of flow 5, so the difference can be seen.
It uses the stored draft only as the suite does (storage_state); it is a diagnostic, not one of the five flows.
Writes probe-scout.json and probe-scout-run.txt here.
"""
import json
import sys
from pathlib import Path

EVID = Path(__file__).resolve().parent
sys.path.insert(0, str(EVID))

import harness_common as hc  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

LOG = hc.Log(EVID / "probe-scout-run.txt")
NAMES = ["Aisyah", "Ben", "Chen", "Devi", "Farid", "Grace", "Hafiz", "Indra"]
EIGHT_PEOPLE = hc.seeds.changed(hc.seeds.S1, lambda d: d["bill"].update(nextId=20, people=[
    {"id": f"p{n}", "name": name} for n, name in enumerate(NAMES, start=1)]))
ONE_ITEM_EIGHT = hc.seeds.changed(EIGHT_PEOPLE, lambda d: d["bill"].update(items=d["bill"]["items"][:1]))


def scout(browser, base, seed, width, height):
    session = hc.Session(browser, base, seed=seed, viewport=(width, height))
    try:
        page = session.page
        page.goto(base + "/")
        hc.settle(page)
        boxes = page.evaluate(hc.CHIP_BOXES_JS)
        price = page.get_by_role("textbox", name="Item 1 price in RM", exact=True)
        price.click()
        page.keyboard.press("Control+A")
        page.keyboard.type("abc")
        page.keyboard.press("Tab")
        hc.settle(page)
        landings = page.evaluate(hc.OVER_ITS_OWN_REMOVE_JS, boxes)
        return {"viewport": [width, height], "chips": len(boxes), "first_chip": boxes[0] if boxes else None,
                "landings": len(landings), "first_landing": landings[0] if landings else None,
                "scrollY": page.evaluate("window.scrollY")}
    finally:
        session.close()


def main():
    out = {}
    server = hc.start_server(LOG)
    try:
        base = server.base
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                out["suite_bill_390x3000"] = scout(browser, base, EIGHT_PEOPLE, 390, 3000)
                out["suite_bill_390x844"] = scout(browser, base, EIGHT_PEOPLE, 390, 844)
                out["one_item_390x844"] = scout(browser, base, ONE_ITEM_EIGHT, 390, 844)
                out["one_item_390x3000"] = scout(browser, base, ONE_ITEM_EIGHT, 390, 3000)
                out["suite_bill_375x3000"] = scout(browser, base, EIGHT_PEOPLE, 375, 3000)
            finally:
                browser.close()
    finally:
        server.stop()
    (EVID / "probe-scout.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    for key, value in out.items():
        LOG.say(f"{key}: chips {value['chips']}, landings {value['landings']}, scrollY {value['scrollY']}, "
                f"first landing {value['first_landing']}")
    LOG.save()


if __name__ == "__main__":
    main()
