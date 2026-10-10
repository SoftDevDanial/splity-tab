"""Regression QA, diagnostic for flow 5 part B: where the chips of item 1 sit at 390 x 844, and what the scout finds.

Builds the bill by real gestures (8 people, one priced item "Tea" at 10.00), then measures the chip boxes before any
error, leaves the price field with "abc" (Tab), and measures again. Also reports the viewport height, the page
height and the scroll position, because a chip below the viewport cannot be probed or pressed.
Writes probe-chips.json here.
"""
import json
import sys
from pathlib import Path

EVID = Path(__file__).resolve().parent
sys.path.insert(0, str(EVID))

import harness_common as hc  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

EIGHT = ["Aisyah", "Ben", "Chen", "Devi", "Farid", "Grace", "Hafiz", "Indra"]
LOG = hc.Log(EVID / "probe-chips-run.txt")
MEASURE_JS = """() => ({ innerHeight: window.innerHeight, innerWidth: window.innerWidth, scrollY: window.scrollY,
  pageHeight: document.documentElement.scrollHeight })"""


def type_into(page, locator, text):
    locator.click()
    page.keyboard.press("Control+A")
    page.keyboard.type(text)


def main():
    out = {}
    server = hc.start_server(LOG)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            session = hc.Session(browser, server.base)
            try:
                page = session.page
                page.goto(server.base + "/")
                type_into(page, hc.person(page, 1), EIGHT[0])
                type_into(page, hc.person(page, 2), EIGHT[1])
                for name in EIGHT[2:]:
                    hc.button(page, "Add person").click()
                    type_into(page, hc.person(page, page.locator("li.person").count()), name)
                hc.switch_mode(page, "By item")
                hc.button(page, "Add item").click()
                type_into(page, hc.item_name(page, 1), "Tea")
                type_into(page, hc.item_price(page, 1), "10.00")
                hc.settle(page)
                out["before"] = {"viewport": page.evaluate(MEASURE_JS), "chips": page.evaluate(hc.CHIP_BOXES_JS)}
                type_into(page, hc.item_price(page, 1), "abc")
                page.keyboard.press("Tab")
                hc.settle(page)
                out["after_error"] = {"viewport": page.evaluate(MEASURE_JS), "chips": page.evaluate(hc.CHIP_BOXES_JS),
                                      "landings": page.evaluate(hc.OVER_ITS_OWN_REMOVE_JS, out["before"]["chips"]),
                                      "remove_under_chip_centres": page.evaluate(
                                          "() => [...document.querySelectorAll('li.item button.icon-btn')]"
                                          ".map((b) => [b.getAttribute('aria-label'), Math.round(b.getBoundingClientRect().x),"
                                          " Math.round(b.getBoundingClientRect().y), Math.round(b.getBoundingClientRect().width)])")}
                out["screenshot"] = "probe-chips-after-error.png"
                page.screenshot(path=str(EVID / out["screenshot"]), full_page=True)
                hc.settle(page)
            finally:
                session.close()
            browser.close()
    finally:
        server.stop()
    (EVID / "probe-chips.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    LOG.say(json.dumps({k: (v if k != "before" and k != "after_error" else {"viewport": v["viewport"],
                                                                        "chips": len(v["chips"])}) for k, v in out.items()}))
    LOG.save()


if __name__ == "__main__":
    main()
