"""Regression QA, step 4: the five everyday flows, by hand, at 390 x 844 on the shipped index.html.

Served by python -m http.server on a free loopback port from the project root (rig.StaticServer). Every context starts
with empty storage (no seed), and every change is a real click, typed key or key press (Playwright). The clipboard is the
suite's recorder (CG-7), so the OS clipboard is never touched. Each flow screenshots its end state into flows/.
  F1 even split, F2 by item, F3 a wrong price, F4 come back (reload, Cancel, start over),
  F5 double presses (double click on Add person; a double click on a chip under a pending price error).
Writes flows.json and flows-run.txt here.

History, kept as files in this folder (the final run is flows.json):
  flows-attempt-1.json: two defects in this script (one expectation ignored that R18 keeps the bill summary on screen
    while an item has no person, and one check had no "what" argument). The app was not at fault.
  flows-attempt-2-one-item.json: part B used a one-item bill, which has no chip whose Remove lies under it after the
    error (probe-scout.json). Part B now builds the four-item S1 bill, as the suite's RG-CR-08 test does.
  flows-attempt-3-stale-scroll.json: part B measured the chips before clicking the price field, and that click scrolled
    the page, so the points were stale. Part B now scrolls to the top with the wheel and measures and presses at scrollY 0.
"""
import datetime
import json
import sys
from pathlib import Path

EVID = Path(__file__).resolve().parent
sys.path.insert(0, str(EVID))

import harness_common as hc  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

SHOTS = EVID / "flows"
SHOTS.mkdir(exist_ok=True)
LOG = hc.Log(EVID / "flows-run.txt")
CHECKS = hc.Checks()
EX = hc.expected
EVEN_START = "Shares\nEnter the subtotal to see the shares."
NEEDS_PERSON = "Shares\n1 item still needs a person. Tap who had it to see the shares."
TEA_SUMMARY = [["Subtotal", "RM 10.00", ""], ["+Service charge", "RM 1.00", "10% of RM 10.00"],
               ["+SST", "RM 0.66", "6% of RM 11.00"], ["=Total", "RM 11.66", ""]]
NEW_BILL = {"version": 1, "bill": {"mode": "even", "people": [{"id": "p1", "name": "Person 1"},
                                                              {"id": "p2", "name": "Person 2"}],
                                   "subtotalText": "", "items": [], "serviceText": "10", "sstText": "6", "nextId": 3}}
EIGHT = ["Aisyah", "Ben", "Chen", "Devi", "Farid", "Grace", "Hafiz", "Indra"]
SCROLL_Y_JS = "() => window.scrollY"


def type_into(page, locator, text):
    """A real click on the field, Control+A to select what is there, then the text key by key."""
    locator.click()
    page.keyboard.press("Control+A")
    page.keyboard.type(text)


def add_person(page, name):
    hc.button(page, "Add person").click()
    type_into(page, hc.person(page, page.locator("li.person").count()), name)


def add_item(page, number, name, price, people):
    hc.button(page, "Add item").click()
    type_into(page, hc.item_name(page, number), name)
    type_into(page, hc.item_price(page, number), price)
    for who in people:
        hc.toggle(page, name, who).click()


def scroll_to_top(page):
    """Real wheel gestures back to the top of the page, then the scroll position is read."""
    page.mouse.move(195, 420)
    for _ in range(6):
        page.mouse.wheel(0, -2000)
        hc.settle(page)
        if page.evaluate(SCROLL_Y_JS) == 0:
            break
    return page.evaluate(SCROLL_Y_JS)


def shot(page, name):
    page.screenshot(path=str(SHOTS / name), full_page=True)


def aria_pressed(page, item_label):
    return hc.who_group(page, item_label).get_by_role("button").evaluate_all(
        "(els) => els.map((e) => e.getAttribute('aria-pressed'))")


def stored_bill(page):
    text = hc.stored(page)
    return json.loads(text) if text is not None else None


def flow1_even_split(browser, base):
    group = "F1 even split"
    session = hc.Session(browser, base)
    try:
        page = session.page
        page.goto(base + "/")
        CHECKS.expect(group, "cold boot", "people fields", ["Person 1", "Person 2"],
                      [hc.person(page, 1).input_value(), hc.person(page, 2).input_value()])
        CHECKS.expect(group, "cold boot", "panel", EVEN_START, hc.panel(page))
        type_into(page, hc.person(page, 1), "Aisyah")
        type_into(page, hc.person(page, 2), "Ben")
        add_person(page, "Chen")
        type_into(page, hc.subtotal(page), "100.00")
        hc.settle(page)
        CHECKS.expect(group, "subtotal 100.00 typed", "shares rows", EX.S2_ROWS, hc.table_rows(page, "tbody"))
        CHECKS.expect(group, "subtotal 100.00 typed", "Adds up to row", EX.S2_CHECK, hc.table_rows(page, "tfoot"))
        CHECKS.expect(group, "subtotal 100.00 typed", "bill summary", EX.S2_SUMMARY, hc.summary_rows(page))
        CHECKS.expect(group, "subtotal 100.00 typed", "default charges", ["10", "6"],
                      [hc.rate(page, "Service charge").input_value(), hc.rate(page, "SST").input_value()])
        shares = [hc.cents(row[1]) for row in hc.table_rows(page, "tbody")]
        CHECKS.expect(group, "shares add up", "three shares add up to the Adds up to amount", 11660, sum(shares))
        CHECKS.expect(group, "shares add up", "Adds up to amount equals the bill total", 11660,
                      hc.cents(hc.table_rows(page, "tfoot")[0][1]))
        hc.button(page, "Copy summary").click()
        hc.settle(page)
        CHECKS.expect(group, "Copy summary", "status text", "Summary copied", page.locator("p.status").inner_text())
        CHECKS.expect(group, "Copy summary", "status class", "status", page.locator("p.status").get_attribute("class"))
        CHECKS.expect(group, "Copy summary", "copied text", EX.S2_COPY, page.evaluate("window.testClipboardText"))
        CHECKS.expect(group, "Copy summary", "clipboard writes", 1, page.evaluate("window.testClipboardWrites"))
        shot(page, "flow1-even-split-end.png")
        CHECKS.expect(group, "end", "console, page errors and requests", [], session.problems())
    finally:
        session.close()


def flow2_by_item(browser, base):
    group = "F2 by item"
    session = hc.Session(browser, base)
    try:
        page = session.page
        page.goto(base + "/")
        type_into(page, hc.person(page, 1), "Aisyah")
        type_into(page, hc.person(page, 2), "Ben")
        add_person(page, "Chen")
        hc.switch_mode(page, "By item")
        for number, (name, price, people) in enumerate(EX.S1_ITEMS, start=1):
            add_item(page, number, name, price, people)
        hc.settle(page)
        CHECKS.expect(group, "four items entered", "items", 4, page.locator("li.item").count())
        CHECKS.expect(group, "four items entered", "who had each (aria-pressed, Aisyah Ben Chen)",
                      [["true", "false", "false"], ["false", "true", "false"], ["false", "false", "true"],
                       ["true", "false", "true"]],
                      [aria_pressed(page, name) for name, _, _ in EX.S1_ITEMS])
        rows = hc.table_rows(page, "tbody")
        CHECKS.expect(group, "shares", "shares rows", EX.S1_ROWS, rows)
        CHECKS.expect(group, "shares", "Adds up to row", EX.S1_CHECK, hc.table_rows(page, "tfoot"))
        CHECKS.expect(group, "shares", "bill summary", EX.S1_SUMMARY, hc.summary_rows(page))
        total = hc.cents(hc.summary_rows(page)[3][1])
        CHECKS.expect(group, "shares add up", "the three shares add up to the Total", total,
                      sum(hc.cents(row[3]) for row in rows))
        CHECKS.expect(group, "shares add up", "each share is items plus charges", [True] * 3,
                      [hc.cents(r[1]) + hc.cents(r[2]) == hc.cents(r[3]) for r in rows])
        CHECKS.expect(group, "shares add up", "items column adds up to the subtotal", hc.cents("RM 59.40"),
                      sum(hc.cents(r[1]) for r in rows))
        CHECKS.expect(group, "shares add up", "charges column adds up to service plus SST", hc.cents("RM 9.86"),
                      sum(hc.cents(r[2]) for r in rows))
        CHECKS.note(group, "headings", "table heads as rendered (innerText)",
                    page.locator("table.shares thead").inner_text())
        CHECKS.note(group, "headings", "table heads as textContent", hc.table_rows(page, "thead"))
        shot(page, "flow2-by-item-end.png")
        CHECKS.expect(group, "end", "console, page errors and requests", [], session.problems())
    finally:
        session.close()


def flow3_wrong_price(browser, base):
    group = "F3 a wrong price"
    session = hc.Session(browser, base)
    try:
        page = session.page
        page.goto(base + "/")
        type_into(page, hc.person(page, 1), "Aisyah")
        type_into(page, hc.person(page, 2), "Ben")
        add_person(page, "Chen")
        hc.switch_mode(page, "By item")
        hc.button(page, "Add item").click()
        type_into(page, hc.item_name(page, 1), "Tea")
        type_into(page, hc.item_price(page, 1), "abc")
        hc.settle(page)
        CHECKS.expect(group, "abc typed, field still focused", "error paragraphs", 0, page.locator("p.error").count())
        CHECKS.expect(group, "abc typed, field still focused", "aria-invalid on the price", None,
                      hc.item_price(page, 1).get_attribute("aria-invalid"))
        CHECKS.expect(group, "abc typed, field still focused", "panel",
                      "Shares\nGive every item a price to see the shares.", hc.panel(page))
        page.keyboard.press("Tab")
        hc.settle(page)
        error = page.locator("p.error")
        error_id = error.get_attribute("id") if error.count() == 1 else None
        described = (hc.item_price(page, 1).get_attribute("aria-describedby") or "").split()
        CHECKS.expect(group, "left the field with Tab", "error paragraphs", 1, page.locator("p.error").count())
        CHECKS.expect(group, "left the field with Tab", "error text", "Enter an amount like 12.50",
                      error.inner_text() if error_id else None)
        CHECKS.expect(group, "left the field with Tab", "aria-invalid on the price", "true",
                      hc.item_price(page, 1).get_attribute("aria-invalid"))
        CHECKS.expect(group, "left the field with Tab", "aria-describedby starts with the error id", True,
                      bool(error_id) and bool(described) and described[0] == error_id)
        CHECKS.note(group, "left the field with Tab", "error id", error_id)
        CHECKS.expect(group, "left the field with Tab", "panel still waits for a price",
                      "Shares\nGive every item a price to see the shares.", hc.panel(page))
        shot(page, "flow3-error-shown.png")
        type_into(page, hc.item_price(page, 1), "10.00")
        hc.settle(page)
        CHECKS.expect(group, "fixed to 10.00", "error paragraphs", 0, page.locator("p.error").count())
        CHECKS.expect(group, "fixed to 10.00", "aria-invalid on the price", None,
                      hc.item_price(page, 1).get_attribute("aria-invalid"))
        CHECKS.expect(group, "fixed to 10.00", "price value", "10.00", hc.item_price(page, 1).input_value())
        CHECKS.expect(group, "fixed to 10.00", "focus stayed in the price field", "Item 1 price in RM",
                      hc.active_label(page))
        CHECKS.expect(group, "fixed to 10.00", "bill summary shows while no one is tapped (R18)", TEA_SUMMARY,
                      hc.summary_rows(page))
        CHECKS.expect(group, "fixed to 10.00", "panel asks for a person, below the summary", True,
                      hc.panel(page).endswith(NEEDS_PERSON))
        hc.toggle(page, "Tea", "Aisyah").click()
        hc.settle(page)
        CHECKS.expect(group, "tapped Aisyah", "shares rows",
                      [["Aisyah", "RM 10.00", "RM 1.66", "RM 11.66"], ["Ben", "RM 0.00", "RM 0.00", "RM 0.00"],
                       ["Chen", "RM 0.00", "RM 0.00", "RM 0.00"]], hc.table_rows(page, "tbody"))
        CHECKS.expect(group, "tapped Aisyah", "Adds up to row",
                      [["Adds up to", "RM 10.00", "RM 1.66", "RM 11.66"]], hc.table_rows(page, "tfoot"))
        shot(page, "flow3-wrong-price-end.png")
        CHECKS.expect(group, "end", "console, page errors and requests", [], session.problems())
    finally:
        session.close()


def flow4_come_back(browser, base):
    group = "F4 come back"
    session = hc.Session(browser, base)
    try:
        page = session.page
        page.goto(base + "/")
        type_into(page, hc.person(page, 1), "Aisyah")
        type_into(page, hc.person(page, 2), "Ben")
        add_person(page, "Chen")
        type_into(page, hc.subtotal(page), "100.00")
        hc.settle(page)
        before = {"state": hc.state(page), "draft": hc.stored(page), "rows": hc.table_rows(page, "tbody")}
        page.reload()
        hc.settle(page)
        after = {"state": hc.state(page), "draft": hc.stored(page), "rows": hc.table_rows(page, "tbody")}
        CHECKS.expect(group, "reload", "the form as it was left", before["state"], after["state"])
        CHECKS.expect(group, "reload", "the stored draft as it was left", before["draft"], after["draft"])
        CHECKS.expect(group, "reload", "the shares as they were left", EX.S2_ROWS, after["rows"])
        shot(page, "flow4-reloaded.png")
        hc.button(page, "New bill").click()
        dialog = page.get_by_role("dialog", name="Start a new bill?")
        CHECKS.expect(group, "New bill", "dialog open and modal", True,
                      hc.dialog_open(page) and dialog.evaluate("(d) => d.matches(':modal')"))
        CHECKS.expect(group, "New bill", "focus on Cancel", "Cancel", hc.active_label(page))
        hc.button(page, "Cancel").click()
        hc.settle(page)
        CHECKS.expect(group, "Cancel", "dialog closed", False, hc.dialog_open(page))
        CHECKS.expect(group, "Cancel", "bill kept on screen", before["state"], hc.state(page))
        CHECKS.expect(group, "Cancel", "stored draft kept", before["draft"], hc.stored(page))
        CHECKS.expect(group, "Cancel", "focus back on New bill", "New bill", hc.active_label(page))
        hc.button(page, "New bill").click()
        hc.button(page, "Start new bill").click()
        hc.settle(page)
        now = hc.state(page)
        CHECKS.expect(group, "Start new bill", "dialog closed", False, hc.dialog_open(page))
        CHECKS.expect(group, "Start new bill", "people back to Person 1 and Person 2", ["Person 1", "Person 2"],
                      [hc.person(page, 1).input_value(), hc.person(page, 2).input_value()])
        CHECKS.expect(group, "Start new bill", "subtotal empty, Even, charges 10 and 6",
                      {"subtotal": "", "mode": "even", "rates": ["10", "6"]},
                      {"subtotal": now["subtotal"], "mode": now["mode"], "rates": now["rates"]})
        CHECKS.expect(group, "Start new bill", "panel", EVEN_START, hc.panel(page))
        CHECKS.expect(group, "Start new bill", "stored draft is the new bill", NEW_BILL, stored_bill(page))
        shot(page, "flow4-come-back-end.png")
        CHECKS.expect(group, "end", "console, page errors and requests", [], session.problems())
    finally:
        session.close()


def flow5_double_presses(browser, base):
    group = "F5 double presses"
    session = hc.Session(browser, base)
    try:
        page = session.page
        page.goto(base + "/")
        hc.button(page, "Add person").dblclick()
        hc.settle(page)
        bill = stored_bill(page)
        CHECKS.expect(group, "A: double click on Add person", "person rows (2 before, so exactly one added)", 3,
                      page.locator("li.person").count())
        CHECKS.expect(group, "A: double click on Add person", "stored people count and id counter", [3, 4],
                      [len(bill["bill"]["people"]), bill["bill"]["nextId"]])
        CHECKS.expect(group, "A: double click on Add person", "focus on Person 3 name", "Person 3 name",
                      hc.active_label(page))
        shot(page, "flow5a-double-add-person.png")
        CHECKS.expect(group, "A: end", "console, page errors and requests", [], session.problems())
    finally:
        session.close()

    group = "F5 double presses, chip under a pending price error"
    session = hc.Session(browser, base)
    try:
        page = session.page
        page.goto(base + "/")
        type_into(page, hc.person(page, 1), EIGHT[0])
        type_into(page, hc.person(page, 2), EIGHT[1])
        for name in EIGHT[2:]:
            add_person(page, name)
        hc.switch_mode(page, "By item")
        for number, (name, price, people) in enumerate(EX.S1_ITEMS, start=1):
            add_item(page, number, name, price, people)
        hc.settle(page)
        CHECKS.expect(group, "B: eight people and the four S1 items", "person rows and item rows", [8, 4],
                      [page.locator("li.person").count(), page.locator("li.item").count()])
        before_ids = [item["id"] for item in stored_bill(page)["bill"]["items"]]
        # The probe: at scrollY 0, the chips before any error, then the same page after item 1's price shows an error.
        scroll_before_probe = scroll_to_top(page)
        CHECKS.expect(group, "B: probe at the top of the page", "scrollY", 0, scroll_before_probe)
        type_into(page, hc.item_price(page, 1), "abc")
        hc.settle(page)
        CHECKS.expect(group, "B: abc typed, field focused, no error yet", "error paragraphs", 0,
                      page.locator("p.error").count())
        CHECKS.expect(group, "B: abc typed, field focused, no error yet", "scrollY", 0, page.evaluate(SCROLL_Y_JS))
        boxes = page.evaluate(hc.CHIP_BOXES_JS)
        CHECKS.note(group, "B: scout", "chips before the error, all items", len(boxes))
        page.keyboard.press("Tab")
        hc.settle(page)
        CHECKS.expect(group, "B: scout, error shown", "error paragraphs", 1, page.locator("p.error").count())
        CHECKS.expect(group, "B: scout, error shown", "scrollY unchanged", 0, page.evaluate(SCROLL_Y_JS))
        landings = page.evaluate(hc.OVER_ITS_OWN_REMOVE_JS, boxes)
        CHECKS.note(group, "B: scout", "chip points lying over their own item's Remove after the error",
                    {"count": len(landings), "first": landings[0] if landings else None})
        type_into(page, hc.item_price(page, 1), "15.90")
        hc.settle(page)
        CHECKS.expect(group, "B: scout restored", "error paragraphs", 0, page.locator("p.error").count())
        page.close()
        page = session.new_page()
        page.goto(base + "/")
        hc.settle(page)
        CHECKS.expect(group, "B: second page loaded at the top", "scrollY", 0, page.evaluate(SCROLL_Y_JS))
        type_into(page, hc.item_price(page, 1), "abc")
        hc.settle(page)
        CHECKS.expect(group, "B: abc typed in a focused price field", "error paragraphs", 0,
                      page.locator("p.error").count())
        CHECKS.expect(group, "B: abc typed in a focused price field", "focus", "Item 1 price in RM",
                      hc.active_label(page))
        CHECKS.expect(group, "B: abc typed in a focused price field", "scrollY", 0, page.evaluate(SCROLL_Y_JS))
        if landings:
            x, y, label = landings[0]
            chips_before = aria_pressed(page, "Char kuey teow")
            page.mouse.dblclick(x, y)
            hc.settle(page)
            CHECKS.expect(group, "B: double click on the chip under the pending error", "items on the screen", 4,
                          page.locator("li.item").count())
            CHECKS.expect(group, "B: double click on the chip under the pending error", "item ids in the stored draft",
                          before_ids, [item["id"] for item in stored_bill(page)["bill"]["items"]])
            CHECKS.note(group, "B: after the double click", "point pressed and what lay under it",
                        {"x": x, "y": y, "label": label})
            CHECKS.note(group, "B: after the double click", "Char kuey teow toggles before and after",
                        [chips_before, aria_pressed(page, "Char kuey teow")])
            CHECKS.note(group, "B: after the double click", "error paragraphs now", page.locator("p.error").count())
        else:
            CHECKS.note(group, "B: not probed", "no chip point lies over its own Remove at 390 x 844 with this bill", None)
        shot(page, "flow5b-double-click-chip-end.png")
        CHECKS.expect(group, "B: end", "console, page errors and requests", [], session.problems())
    finally:
        session.close()


def main():
    started = datetime.datetime.now().isoformat(timespec="seconds")
    server = hc.start_server(LOG)
    record = {"started": started, "server_port": server.port, "server_pid": server.process.pid,
              "viewport": "390x844", "storage": "empty at the start of every flow"}
    try:
        base = server.base
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            record["chromium"] = browser.version
            record["chromium_pids_while_open"] = hc.chromium_pids()
            LOG.say(f"chromium {browser.version} open, pids {record['chromium_pids_while_open']}")
            try:
                for flow in (flow1_even_split, flow2_by_item, flow3_wrong_price, flow4_come_back,
                             flow5_double_presses):
                    LOG.say(f"running {flow.__name__}")
                    try:
                        flow(browser, base)
                    except Exception as error:  # a flow that cannot finish is a recorded failure, the rest still run
                        CHECKS.rows.append({"group": flow.__name__, "step": "aborted", "what": "the flow ran to its end",
                                            "expected": "no exception", "observed": f"{type(error).__name__}: {error}",
                                            "result": "FAIL"})
                        LOG.say(f"{flow.__name__} aborted: {type(error).__name__}: {error}")
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
        record["counts"] = {"pass": sum(r["result"] == "PASS" for r in CHECKS.rows), "fail": len(failed),
                            "note": sum(r["result"] == "NOTE" for r in CHECKS.rows)}
        record["checks"] = CHECKS.rows
        (EVID / "flows.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        LOG.say(f"five flows {record['result']} {record['counts']}")
        LOG.save()
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
