"""Regression QA, step 3: driven checks for the parts of scenarios that no passing suite test covers.

Each check drives the real page in headless Chromium with real gestures (clicks, typing, key presses) and records what it
saw. Seeds go through storage_state (the suite's own load path); no hook is injected into the app.
  D1  R5   renaming a person updates the toggles, the shares row and the remove name on each keystroke (S1 seed)
  D2  R38  the strict policy blocks nothing: S1 seed, and S2 seed with the New bill dialog open
  D3  R23  a blocked clipboard leaves the bill unchanged (S2 seed, reject.js)
Writes driven-checks.json and driven-checks-run.txt here, and screenshots under driven/.
"""
import datetime
import json
import sys
from pathlib import Path

EVID = Path(__file__).resolve().parent
sys.path.insert(0, str(EVID))

import harness_common as hc  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

SHOTS = EVID / "driven"
SHOTS.mkdir(exist_ok=True)
LOG = hc.Log(EVID / "driven-checks-run.txt")
CHECKS = hc.Checks()
LABEL_ITEMS = ["Nasi lemak ayam", "Char kuey teow", "Mee goreng mamak", "Satay, 10 sticks"]


def d1_rename_per_keystroke(browser, base):
    group = "D1 R5 rename per keystroke, S1 seed"
    session = hc.Session(browser, base, seed=hc.seeds.S1)
    try:
        page = session.page
        page.goto(base + "/")
        hc.person(page, 3).click()
        page.keyboard.press("End")
        page.screenshot(path=str(SHOTS / "d1-before.png"), full_page=True)
        typed = "Chen"
        for key in " Wei":
            page.keyboard.type(key)
            typed += key
            label = typed.strip()
            toggles = [hc.who_group(page, item).get_by_role("button").all_inner_texts() for item in LABEL_ITEMS]
            shares = hc.table_rows(page, "tbody")[2][0]
            remove = page.locator("li.person").nth(2).get_by_role("button").get_attribute("aria-label")
            CHECKS.expect(group, f"after typing {typed!r}", "field 3 holds the typed text", typed,
                          hc.person(page, 3).input_value())
            CHECKS.expect(group, f"after typing {typed!r}", "all four toggles end in the trimmed label",
                          [["Aisyah", "Ben", label]] * 4, toggles)
            CHECKS.expect(group, f"after typing {typed!r}", "shares row name", label, shares)
            CHECKS.expect(group, f"after typing {typed!r}", "remove button name", f"Remove {label}", remove)
        page.screenshot(path=str(SHOTS / "d1-after.png"), full_page=True)
        hc.button(page, "Copy summary").click()
        clip = page.evaluate("window.testClipboardText")
        CHECKS.expect(group, "Copy summary", "line 5 of the copied text", "Chen Wei RM 24.48", clip.splitlines()[4])
        CHECKS.expect(group, "end", "Chen's shares row after the rename",
                      ["Chen Wei", "RM 21.00", "RM 3.48", "RM 24.48"], hc.table_rows(page, "tbody")[2])
        CHECKS.expect(group, "end", "problems", [], session.problems())
    finally:
        session.close()


def d2_strict_policy(browser, base):
    group = "D2 R38 strict policy, S1 seed"
    session = hc.Session(browser, base, seed=hc.seeds.S1)
    try:
        page = session.page
        page.goto(base + "/")
        CHECKS.expect(group, "S1 seed", "body background from the stylesheet", "rgb(238, 240, 238)",
                      page.evaluate("getComputedStyle(document.body).backgroundColor"))
        CHECKS.expect(group, "S1 seed", "people rows and Charges inputs exist", [3, 1, 1],
                      [page.locator("li.person input").count(), page.locator("#rate-service").count(),
                       page.locator("#rate-sst").count()])
        CHECKS.expect(group, "S1 seed", "the S1 table", hc.expected.S1_ROWS, hc.table_rows(page, "tbody"))
        CHECKS.expect(group, "S1 seed", "the S1 check row", hc.expected.S1_CHECK, hc.table_rows(page, "tfoot"))
        CHECKS.expect(group, "S1 seed", "elements under body with a style attribute", 0,
                      page.evaluate("document.querySelectorAll('body [style]').length"))
        page.screenshot(path=str(SHOTS / "d2a-s1-seed.png"), full_page=True)
        CHECKS.expect(group, "S1 seed", "no CSP message, no page error, no request outside the rules", [],
                      session.problems())
    finally:
        session.close()

    group = "D2 R38 strict policy, S2 seed with the dialog open"
    session = hc.Session(browser, base, seed=hc.seeds.S2)
    try:
        page = session.page
        page.goto(base + "/")
        hc.button(page, "New bill").click()
        CHECKS.expect(group, "dialog", "dialog is open", True, hc.dialog_open(page))
        CHECKS.expect(group, "S2 seed", "body background from the stylesheet", "rgb(238, 240, 238)",
                      page.evaluate("getComputedStyle(document.body).backgroundColor"))
        CHECKS.expect(group, "S2 seed", "people rows and Charges inputs exist", [3, 1, 1],
                      [page.locator("li.person input").count(), page.locator("#rate-service").count(),
                       page.locator("#rate-sst").count()])
        CHECKS.expect(group, "S2 seed", "the S2 table under the dialog", hc.expected.S2_ROWS,
                      hc.table_rows(page, "tbody"))
        CHECKS.expect(group, "S2 seed", "the S2 check row under the dialog", hc.expected.S2_CHECK,
                      hc.table_rows(page, "tfoot"))
        CHECKS.expect(group, "S2 seed", "elements under body with a style attribute", 0,
                      page.evaluate("document.querySelectorAll('body [style]').length"))
        page.screenshot(path=str(SHOTS / "d2b-s2-dialog.png"), full_page=True)
        CHECKS.expect(group, "S2 seed", "no CSP message, no page error, no request outside the rules", [],
                      session.problems())
    finally:
        session.close()


def d3_blocked_clipboard_keeps_the_bill(browser, base):
    group = "D3 R23 browser blocks the clipboard, S2 seed"
    session = hc.Session(browser, base, seed=hc.seeds.S2, clipboard="reject")
    try:
        page = session.page
        page.goto(base + "/")
        before = {"draft": hc.stored(page), "state": hc.state(page), "panel": hc.panel(page),
                  "rows": hc.table_rows(page, "tbody"), "check": hc.table_rows(page, "tfoot")}
        hc.button(page, "Copy summary").click()
        hc.settle(page)
        status = page.locator("p.status")
        CHECKS.expect(group, "Copy summary", "status text", hc.FAILED_COPY, status.inner_text())
        CHECKS.expect(group, "Copy summary", "status class list", "status status-failure", status.get_attribute("class"))
        after = {"draft": hc.stored(page), "state": hc.state(page), "panel": hc.panel(page),
                 "rows": hc.table_rows(page, "tbody"), "check": hc.table_rows(page, "tfoot")}
        CHECKS.expect(group, "after the blocked copy", "stored draft text is the same", before["draft"], after["draft"])
        CHECKS.expect(group, "after the blocked copy", "the form state is the same", before["state"], after["state"])
        CHECKS.expect(group, "after the blocked copy", "the shares rows are the same", before["rows"], after["rows"])
        CHECKS.expect(group, "after the blocked copy", "the check row is the same", before["check"], after["check"])
        CHECKS.expect(group, "after the blocked copy", "the panel is the same apart from the status line",
                      before["panel"], after["panel"].replace(hc.FAILED_COPY, "").strip())
        page.screenshot(path=str(SHOTS / "d3-after-reject.png"), full_page=True)
        CHECKS.expect(group, "end", "problems", [], session.problems())
    finally:
        session.close()


def main():
    started = datetime.datetime.now().isoformat(timespec="seconds")
    server = hc.start_server(LOG)
    record = {"started": started, "server_port": server.port, "server_pid": server.process.pid}
    try:
        base = server.base
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            record["chromium"] = browser.version
            record["chromium_pids_while_open"] = hc.chromium_pids()
            LOG.say(f"chromium {browser.version} open, pids {record['chromium_pids_while_open']}")
            try:
                d1_rename_per_keystroke(browser, base)
                d2_strict_policy(browser, base)
                d3_blocked_clipboard_keeps_the_bill(browser, base)
            finally:
                browser.close()
            record["chromium_pids_after_close"] = hc.chromium_pids()
            LOG.say(f"chromium closed, pids left {record['chromium_pids_after_close']}")
    finally:
        server.stop()
        record["server_port_free_after_stop"] = hc.rig.port_is_free(server.port)
        record["ended"] = datetime.datetime.now().isoformat(timespec="seconds")
        failed = CHECKS.failed()
        record["result"] = "PASS" if not failed else "FAIL"
        record["counts"] = {"pass": sum(r["result"] == "PASS" for r in CHECKS.rows),
                            "fail": len(failed), "note": sum(r["result"] == "NOTE" for r in CHECKS.rows)}
        record["checks"] = CHECKS.rows
        (EVID / "driven-checks.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        LOG.say(f"driven checks {record['result']} {record['counts']}")
        LOG.save()
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
