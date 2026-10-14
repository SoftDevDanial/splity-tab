"""Hint tap probe (task A6, spec R59 (3)), headless Chromium and WebKit, the default context with has_touch.

On a cold boot with Charges opened and "31" typed in Service charge, one touch tap at the middle of p.hint#chargeHint,
three ways: no recorder, a recorder on window in the capture phase (the one test_R10_a_touch_tap_on_the_charges_hint_...
uses), and qa.md's body half (mousedown and click listeners on document.body in the bubble phase). For each it records
the mousedown and click events the recorder saw, where focus is 300 ms after the tap, and whether p.err#svcErr shows.
It shows whether a recorder changes what a WebKit tap does (BUILD.md, A17 judgment call 6, A6). Writes probe.json into a
new <stamp> folder beside this script and nothing else. Run from the project root:
python docs/modules/split-app/qa/hint-tap/probe.py
"""
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("tests/browser").resolve()))
import rig  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

RECORDERS = {"none": None, "window-capture": "window", "body-bubble": "body"}
RECORD_JS = """(where) => { window.probeSeen = [];
  const record = (event) => window.probeSeen.push(`${event.type}:${event.target.id || event.target.localName}`);
  for (const type of ['mousedown', 'click']) {
    if (where === 'window') window.addEventListener(type, record, true);
    else document.body.addEventListener(type, record);
  } }"""
STATE_JS = """() => ({ seen: window.probeSeen ?? null, active: document.activeElement.id || document.activeElement.localName,
  svcErrShows: document.querySelector('p.err#svcErr')?.hidden === false })"""


def tap_once(browser, base, how):
    context = rig.new_context(browser, viewport={"width": 390, "height": 844}, device_scale_factor=1, color_scheme="dark",
                              reduced_motion="reduce", has_touch=True)
    try:
        page = context.new_page()
        page.goto(base + "/")
        page.locator("#chargesBtn").click()
        page.locator("#svc").click()
        page.keyboard.press("Control+A")
        page.keyboard.type("31")
        if how:
            page.evaluate(RECORD_JS, how)
        hint = page.locator("#chargeHint")
        hint.scroll_into_view_if_needed()
        box = hint.bounding_box()
        page.touchscreen.tap(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        page.wait_for_timeout(300)
        return page.evaluate(STATE_JS)
    finally:
        context.close()


def main():
    folder = Path(__file__).resolve().parent / datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    folder.mkdir(parents=True)
    server = rig.StaticServer(rig.ROOT).start()
    found = {}
    try:
        with sync_playwright() as playwright:
            for engine in ("chromium", "webkit"):
                browser = rig.launch(playwright, engine)
                found[engine] = {"browser_version": browser.version,
                                 **{name: tap_once(browser, server.base, how) for name, how in RECORDERS.items()}}
                browser.close()
    finally:
        server.stop()
    (folder / "probe.json").write_text(json.dumps(found, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(found, indent=1))
    print("wrote", folder)


main()
