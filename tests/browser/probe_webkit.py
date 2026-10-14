"""The WebKit probes of task A0 (spec R59). Run from the project root: python tests/browser/probe_webkit.py --engine webkit

Measures, in the named engine on this machine, the behaviour R59 leaves open: the click count (detail) of a quick
double tap, the order of a tap's pointer and mouse events, isSecureContext and typeof Clipboard on http://127.0.0.1,
whether an init script can redefine window.localStorage, the console text of a CSP violation and of a denied
localStorage, focus after a mouse click on a radio's label and on a radio, and the Content-Type the test server
sends for an .svg file. Writes probes.json into docs/modules/split-app/qa/webkit-baseline/<YYYYMMDD-HHMMSS>/.

The browser comes from rig.launch and every context from rig.new_context, so the clipboard recorder loads before
each page. Each page is checked for it before its first gesture, and the run stops with an error when it is
missing. Nothing reaches the operating system clipboard. The served pages are only read. Exit status 0 when every
probe ran, 1 otherwise. Test-side only.
"""
import argparse
import datetime
import json
import sys
import urllib.request

from playwright.sync_api import sync_playwright

import rig

EVIDENCE_ROOT = rig.ROOT / "docs" / "modules" / "split-app" / "qa" / "webkit-baseline"
STATIC_PAGE = "/docs/design/bill-even.html"  # served and read only, it holds no script
SVG_FILE = "/docs/brand/mark.svg"
SETTLE_MS = 500  # how long a probe listens for console messages after its trigger

STAND_IN_JS = """() => ({ writes: window.testClipboardWrites,
  native: !!(navigator.clipboard && navigator.clipboard.writeText)
    && String(navigator.clipboard.writeText).includes("[native code]") })"""
# Probe pages are written with set_content, so the app's own styling decides nothing here.
TAP_PAGE = '<!doctype html><title>tap</title><button id="target" type="button" style="width:200px;height:80px">Tap</button>'
FOCUS_PAGE = """<!doctype html><title>focus</title><fieldset><legend>Mode</legend>
<input type="radio" name="mode" id="even" value="even" checked><label for="even">Even</label>
<input type="radio" name="mode" id="item" value="item"><label for="item">By item</label></fieldset>"""
RECORD_EVENTS_JS = """() => { window.probeEvents = [];
  for (const type of ["touchstart", "touchend", "pointerdown", "pointerup", "mousedown", "mouseup", "click"]) {
    document.addEventListener(type, (event) => window.probeEvents.push({ type, detail: event.detail }), true);
  } }"""
ACTIVE_JS = "() => ({ tag: document.activeElement.tagName.toLowerCase(), id: document.activeElement.id })"
DENY_STORAGE_JS = """(() => { try {
  Object.defineProperty(window, "localStorage", { configurable: true,
    get() { throw new DOMException("probe denied", "SecurityError"); } });
  window.probeRedefined = true;
} catch (error) { window.probeRedefined = String(error); } })();"""
READ_STORAGE_JS = """() => { try { localStorage.length; return { threw: false }; }
  catch (error) { return { threw: true, name: error.name, message: error.message }; } }"""
TOUCH_STORAGE_JS = 'localStorage.setItem("probe.key", "1");'
INLINE_SCRIPT_JS = """() => { window.probeViolations = [];
  document.addEventListener("securitypolicyviolation",
    (event) => window.probeViolations.push({ violatedDirective: event.violatedDirective, blockedURI: event.blockedURI }));
  const script = document.createElement("script"); script.textContent = "window.probeRan = true"; document.head.append(script); }"""


class StandInMissing(RuntimeError):
    """The clipboard recorder is not in place, so no gesture may happen on this page."""


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="R59 probes of task A0.")
    parser.add_argument("--engine", choices=list(rig.ENGINES), required=True, help="browser engine (R58)")
    return parser.parse_args(argv)


def require_stand_in(page, where):
    """Reads the recorder's state and stops the run unless it is in place (constitution, Browser gates)."""
    state = page.evaluate(STAND_IN_JS)
    if state["writes"] != 0 or state["native"]:
        raise StandInMissing(f"{where}: clipboard stand-in missing ({state})")
    return state


def with_logs(context):
    """Collects console messages and page errors of every page the context opens."""
    logs = {"console": [], "page_errors": []}
    context.on("page", lambda page: (
        page.on("console", lambda message: logs["console"].append({"type": message.type, "text": message.text})),
        page.on("pageerror", lambda error: logs["page_errors"].append(str(error)))))
    return logs


def probe_taps(browser):
    """One tap and one quick double tap on a button, in a touch context: event order and click detail."""
    context = rig.new_context(browser, has_touch=True, viewport={"width": 390, "height": 844})
    try:
        page = context.new_page()
        page.set_content(TAP_PAGE)
        stand_in = require_stand_in(page, "tap page")
        page.evaluate(RECORD_EVENTS_JS)
        box = page.locator("#target").bounding_box()
        x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        page.touchscreen.tap(x, y)
        single = page.evaluate("window.probeEvents.splice(0)")
        page.touchscreen.tap(x, y)
        page.touchscreen.tap(x, y)
        double = page.evaluate("window.probeEvents.splice(0)")
        return {"stand_in_before_first_gesture": stand_in, "one_tap_order": [event["type"] for event in single],
                "one_tap_events": single, "quick_double_tap_click_details": [event["detail"] for event in double
                                                                             if event["type"] == "click"],
                "quick_double_tap_events": double}
    finally:
        context.close()


def probe_focus(browser):
    """document.activeElement after a mouse click on the label of a radio, and on a visible radio."""
    context = rig.new_context(browser, viewport={"width": 390, "height": 844})
    try:
        results = {}
        for name, selector in (("click_on_label_of_radio", "label[for=item]"), ("click_on_radio", "#item")):
            page = context.new_page()
            page.set_content(FOCUS_PAGE)
            stand_in = require_stand_in(page, name)
            page.locator(selector).click()
            results[name] = {"stand_in_before_first_gesture": stand_in, "clicked": selector,
                             "active_element": page.evaluate(ACTIVE_JS), "item_checked": page.locator("#item").is_checked()}
            page.close()
        return results
    finally:
        context.close()


def probe_secure_context(browser, base):
    context = rig.new_context(browser)
    try:
        page = context.new_page()
        page.goto(base + "/")
        return page.evaluate("""() => ({ url: location.href, isSecureContext, typeofClipboard: typeof Clipboard,
          typeofNavigatorClipboard: typeof navigator.clipboard,
          writeTextIsStandIn: !!(navigator.clipboard && navigator.clipboard.writeText)
            && !String(navigator.clipboard.writeText).includes("[native code]") })""")
    finally:
        context.close()


def probe_storage_redefinition(browser, base):
    """Whether an init script can make the window.localStorage getter throw (storage driver D-b)."""
    results = {}
    for name, scripts in (("control_no_driver", ()), ("with_driver", (DENY_STORAGE_JS,))):
        context = rig.new_context(browser, init_scripts=scripts)
        try:
            page = context.new_page()
            page.goto(base + STATIC_PAGE)
            results[name] = {"redefined": page.evaluate("window.probeRedefined === undefined ? null : window.probeRedefined"),
                             "read": page.evaluate(READ_STORAGE_JS)}
        finally:
            context.close()
    return results


def probe_csp_console(browser, base):
    """The console text when the shipped policy blocks an inline script on the app page."""
    context = rig.new_context(browser)
    logs = with_logs(context)
    try:
        page = context.new_page()
        page.goto(base + "/")
        before = len(logs["console"])
        page.evaluate(INLINE_SCRIPT_JS)
        page.wait_for_timeout(SETTLE_MS)
        return {"console": logs["console"][before:], "page_errors": logs["page_errors"],
                "violations": page.evaluate("window.probeViolations"), "inline_script_ran": page.evaluate("window.probeRan === true")}
    finally:
        context.close()


def probe_denied_storage_console(browser, base):
    """The console text when an init script touches localStorage in the blank first document (a fidelity seed does)."""
    context = rig.new_context(browser, init_scripts=(TOUCH_STORAGE_JS,))
    logs = with_logs(context)
    try:
        page = context.new_page()
        page.goto(base + STATIC_PAGE)
        page.wait_for_timeout(SETTLE_MS)
        return {"console": logs["console"], "page_errors": logs["page_errors"],
                "stored_on_the_served_page": page.evaluate("localStorage.getItem('probe.key')")}
    finally:
        context.close()


def probe_svg_type(base):
    with urllib.request.urlopen(base + SVG_FILE, timeout=5) as response:
        return {"path": SVG_FILE, "status": response.status, "content_type": response.headers.get("Content-Type")}


def main(argv=None):
    engine = parse_args(argv).engine
    started = datetime.datetime.now()
    folder = EVIDENCE_ROOT / started.strftime("%Y%m%d-%H%M%S")
    folder.mkdir(parents=True, exist_ok=True)
    server_lines = []

    def say(line):
        print(line, flush=True)
        server_lines.append(line)

    server = rig.StaticServer(rig.ROOT, say=say)
    record = {"started": started.isoformat(timespec="seconds"), "engine": engine, "browser_version": None,
              "launched_by": "rig.launch", "contexts_by": "rig.new_context", "probes": {}, "failure": None}
    try:
        server.start()
        record.update(port=server.port, server_pid=server.process.pid)
        with sync_playwright() as playwright:
            browser = rig.launch(playwright, engine)
            record["browser_version"] = browser.version
            try:
                probes = record["probes"]
                probes["taps"] = probe_taps(browser)
                probes["focus_after_mouse_click"] = probe_focus(browser)
                probes["secure_context_on_127_0_0_1"] = probe_secure_context(browser, server.base)
                probes["init_script_redefines_localStorage"] = probe_storage_redefinition(browser, server.base)
                probes["csp_violation_console"] = probe_csp_console(browser, server.base)
                probes["denied_localStorage_console"] = probe_denied_storage_console(browser, server.base)
                probes["svg_content_type"] = probe_svg_type(server.base)
            except Exception as error:  # a missing stand-in or a probe error both end the run, recorded below
                record["failure"] = f"{type(error).__name__}: {error}"
            finally:
                browser.close()
    finally:
        server.stop()
        record.update(ended=datetime.datetime.now().isoformat(timespec="seconds"), server_log=server_lines)
        (folder / "probes.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"probes {'FAILED: ' + record['failure'] if record['failure'] else 'done'}, written to {folder / 'probes.json'}")
    return 1 if record["failure"] else 0


if __name__ == "__main__":
    sys.exit(main())
