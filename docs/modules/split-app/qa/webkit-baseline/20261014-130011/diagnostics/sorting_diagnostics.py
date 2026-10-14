"""A0 sorting diagnostics, evidence only (not part of the suite). Run from the project root:
python docs/modules/split-app/qa/webkit-baseline/20261014-130011/diagnostics/sorting_diagnostics.py

Measures in Chromium and WebKit the three behaviours behind WebKit failures that probes.json does not cover:
1. a touch tap on #charges-hint after an invalid Service charge (test_R10_a_press_below_an_invalid_field_..., service and sst touch),
2. the dialog's state and focus polled right after Escape, S2 seed (test_R30_..._[escape]),
3. console messages on the app page around page.screenshot (the live gate's step 7 in WebKit).
Headless, browsers from rig.launch, contexts from rig.new_context with the clipboard recorder, checked before the
first gesture. Writes sorting_diagnostics.json beside this file and nothing else. Screenshots stay in memory.
"""
import datetime
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[6]
sys.path.insert(0, str(ROOT / "tests" / "browser"))
import rig  # noqa: E402
import seeds  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

POLL_READS = 60
STAND_IN_JS = """() => window.testClipboardWrites === 0 && !(navigator.clipboard && navigator.clipboard.writeText
  && String(navigator.clipboard.writeText).includes("[native code]"))"""
EVENTS_JS = """() => { window.diag = [];
  for (const type of ["touchstart", "touchend", "pointerdown", "pointerup", "mousedown", "mouseup", "click", "focusout"]) {
    document.addEventListener(type, (e) => window.diag.push(type + ":" + (e.target.id || e.target.tagName.toLowerCase())), true);
  } }"""
STATE_JS = """() => ({ open: document.querySelector("dialog.dialog").open,
  active: document.activeElement.id || document.activeElement.tagName.toLowerCase() + ":" + document.activeElement.textContent.trim().slice(0, 12) })"""
PHONE = {"viewport": {"width": 390, "height": 844}, "device_scale_factor": 1, "color_scheme": "light"}


def checked_page(context, url):
    page = context.new_page()
    page.goto(url)
    if not page.evaluate(STAND_IN_JS):
        raise RuntimeError("clipboard stand-in missing")
    return page


def tap_on_hint(browser, base):
    context = rig.new_context(browser, has_touch=True, **PHONE)
    try:
        page = checked_page(context, base + "/")
        page.locator("#rate-service").click()
        page.keyboard.press("Control+A")
        page.keyboard.type("31")
        page.evaluate(EVENTS_JS)
        hint = page.locator("#charges-hint")
        hint.scroll_into_view_if_needed()
        box = hint.bounding_box()
        page.touchscreen.tap(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        page.wait_for_timeout(300)
        return {"events": page.evaluate("window.diag"), "active": page.evaluate("document.activeElement.id || document.activeElement.tagName"),
                "error_shown": page.locator("#rate-service-error").count()}
    finally:
        context.close()


def escape_transitions(browser, base):
    context = rig.new_context(browser, storage_state=rig.storage_state(base, seeds.S2), **PHONE)
    try:
        page = checked_page(context, base + "/")
        page.get_by_role("button", name="New bill", exact=True).click()
        page.keyboard.press("Escape")
        seen = [page.evaluate(STATE_JS)]
        for _ in range(POLL_READS):
            state = page.evaluate(STATE_JS)
            if state != seen[-1]:
                seen.append(state)
        return {"states_after_escape_in_order": seen, "reads": POLL_READS + 1}
    finally:
        context.close()


def screenshot_console(browser, base):
    context = rig.new_context(browser, **PHONE)
    messages = []
    context.on("page", lambda page: page.on("console", lambda m: messages.append(f"{m.type}: {m.text}")))
    try:
        page = checked_page(context, base + "/")
        page.wait_for_timeout(200)
        before = list(messages)
        page.screenshot(full_page=True)
        page.screenshot(full_page=True, caret="initial")
        page.wait_for_timeout(200)
        return {"before_any_screenshot": before, "after_two_screenshots": messages[len(before):]}
    finally:
        context.close()


def main():
    record = {"started": datetime.datetime.now().isoformat(timespec="seconds")}
    server = rig.StaticServer(ROOT, say=lambda line: record.setdefault("server_log", []).append(line)).start()
    try:
        with sync_playwright() as playwright:
            for engine in rig.ENGINES:
                browser = rig.launch(playwright, engine)
                try:
                    record[engine] = {"browser_version": browser.version, "tap_on_hint": tap_on_hint(browser, server.base),
                                      "escape_transitions": escape_transitions(browser, server.base),
                                      "screenshot_console": screenshot_console(browser, server.base)}
                finally:
                    browser.close()
    finally:
        server.stop()
        record["ended"] = datetime.datetime.now().isoformat(timespec="seconds")
        (HERE / "sorting_diagnostics.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print("written", HERE / "sorting_diagnostics.json")


if __name__ == "__main__":
    main()
