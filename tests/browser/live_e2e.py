"""Cold-boot live gate (qa.md, "Cold-boot live-e2e gate"). Run from the project root: python tests/browser/live_e2e.py

A person's first session, end to end, against the shipped index.html served by python -m http.server, in a fresh
headless Chromium with a new context: no storage_state, no bypass_csp (so the strict policy is live for the whole
run) and one init script, the clipboard recorder (CG-7), so the operating system clipboard is never touched, not
even to read it. Only real gestures change the app (mouse clicks, typing, key presses, a reload). page.evaluate
is used to read, never to change anything.

Evidence goes to docs/modules/split-app/qa/live-e2e/<YYYYMMDD-HHMMSS>/: one NN-<step>.png per step, steps.log
(one line per step, "NN | gesture: ... | assertion: ... | PASS or FAIL"), console.log, network.log,
clipboard-s2.txt, clipboard-s1.txt and summary.json. Exit status 0 when every step passes, 1 otherwise.
"""
import datetime
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

import rig
import support

EVIDENCE_ROOT = rig.ROOT / "docs" / "modules" / "split-app" / "qa" / "live-e2e"
INIT_SCRIPTS = ["tests/browser/clipboard/recorder.js"]  # the only one (CG-7)
VIEWPORT = {"width": 390, "height": 844}

# Expected screens. The copy blocks are the S2 and S1 blocks of split-core spec R24, joined with "\n".
S3_STATE = {"people": ["Person 1", "Person 2"], "removeDisabled": [True, True], "mode": "even", "subtotal": "",
            "rates": ["10", "6"], "notes": 0, "errors": 0}
S3_PANEL = "Shares\nEnter the subtotal to see the shares."
S2_SUMMARY = [["Subtotal", "RM 100.00", ""], ["+Service charge", "RM 10.00", "10% of RM 100.00"],
              ["+SST", "RM 6.60", "6% of RM 110.00"], ["=Total", "RM 116.60", ""]]
S2_ROWS = [["Aisyah", "RM 38.87"], ["Ben", "RM 38.87"], ["Chen", "RM 38.86"]]
S2_CHECK = [["Adds up to", "RM 116.60"]]
S2_COPY = ("Bill split\nTotal RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)\n"
           "Aisyah RM 38.87\nBen RM 38.87\nChen RM 38.86\nAdds up to RM 116.60")
S1_ITEMS = [("Nasi lemak ayam", "15.90", ["Aisyah"]), ("Char kuey teow", "13.50", ["Ben"]),
            ("Mee goreng mamak", "12.00", ["Chen"]), ("Satay, 10 sticks", "18.00", ["Aisyah", "Chen"])]
S1_ITEM_STATE = [["Nasi lemak ayam", "15.90", "true", "false", "false"], ["Char kuey teow", "13.50", "false", "true", "false"],
                 ["Mee goreng mamak", "12.00", "false", "false", "true"], ["Satay, 10 sticks", "18.00", "true", "false", "true"]]
S1_SUMMARY = [["Subtotal", "RM 59.40", ""], ["+Service charge", "RM 5.94", "10% of RM 59.40"],
              ["+SST", "RM 3.92", "6% of RM 65.34"], ["=Total", "RM 69.26", ""]]
S1_ROWS = [["Aisyah", "RM 24.90", "RM 4.14", "RM 29.04"], ["Ben", "RM 13.50", "RM 2.24", "RM 15.74"],
           ["Chen", "RM 21.00", "RM 3.48", "RM 24.48"]]
S1_CHECK = [["Adds up to", "RM 59.40", "RM 9.86", "RM 69.26"]]
S1_COPY = ("Bill split\nTotal RM 69.26 (subtotal RM 59.40, service 10% RM 5.94, SST 6% RM 3.92)\n"
           "Aisyah RM 29.04\nBen RM 15.74\nChen RM 24.48\nAdds up to RM 69.26")

# Reads only.
STATE_JS = """() => ({
  people: [...document.querySelectorAll('li.person input')].map((i) => i.value),
  removeDisabled: [...document.querySelectorAll('li.person button')].map((b) => b.disabled),
  mode: document.querySelector('input[name=mode]:checked').value,
  subtotal: document.querySelector('#subtotal') ? document.querySelector('#subtotal').value : null,
  rates: [document.querySelector('#rate-service').value, document.querySelector('#rate-sst').value],
  notes: document.querySelectorAll('div.note').length,
  errors: document.querySelectorAll('p.error').length,
})"""
ITEMS_JS = """() => [...document.querySelectorAll('li.item')].map((li) => [...li.querySelectorAll('input')].map((i) => i.value)
  .slice(0, 2).concat([...li.querySelectorAll('.tap')].map((b) => b.getAttribute('aria-pressed'))))"""
SUMMARY_JS = """() => [...document.querySelectorAll('dl.sum .row')].map((r) => [r.querySelector('dt').textContent.trim(),
  r.querySelector('.amt').textContent.trim(), (r.querySelector('.work') || { textContent: '' }).textContent.trim()])"""
TABLE_JS = """(part) => [...document.querySelectorAll(`table.shares ${part} tr`)].map((tr) => [...tr.children].map((c) => c.textContent.trim()))"""
ACTIVE_JS = "() => document.activeElement.getAttribute('aria-label') || document.activeElement.textContent.trim()"


def format_step(number, gesture, assertion, verdict):
    """One steps.log line. The gesture is what was done, the assertion is what was expected afterwards."""
    return f"{number:02d} | gesture: {gesture} | assertion: {assertion} | {verdict}"


def expect(actual, expected, what):
    if actual != expected:
        raise AssertionError(f"{what}: expected {expected!r}, got {actual!r}")


def request_is_allowed(base, method, url):
    parts = urlsplit(url)
    path = parts.path
    return (method == "GET" and f"{parts.scheme}://{parts.netloc}" == base
            and (path in ("/", "/src/system.css", "/favicon.ico") or path.startswith("/src/")))


class Gate:
    """The one browser session of the run, its logs and its evidence folder."""

    def __init__(self, folder, base):
        self.folder, self.base = folder, base
        self.page = None
        self.steps, self.console, self.page_errors, self.requests = [], [], [], []
        self.failure = None

    def watch(self, page):
        page.on("console", lambda message: self.console.append(f"{message.type}: {message.text}"))
        page.on("pageerror", lambda error: self.page_errors.append(str(error)))
        page.on("request", lambda request: self.requests.append(f"{request.method} {request.url}"))

    def step(self, number, slug, *, gesture, assertion, body):
        """Run body (the gestures, then the reads and checks), take the screenshot, log the line. A failure stops the run.

        gesture is what a person does in this step, assertion is what must be true afterwards. Both are keyword-only
        so a swap shows in the call (test_R41_every_step_has_its_gesture_and_its_assertion_in_the_right_field).
        """
        verdict = "PASS"
        try:
            body()
        except Exception as error:  # a failed check or a timeout both fail the step
            verdict, self.failure = "FAIL", f"step {number:02d}: {type(error).__name__}: {error}"
        # A control that just changed state is mid-transition for 120 ms, so the picture waits for that to end.
        self.page.wait_for_function("() => document.getAnimations().length === 0")
        self.page.screenshot(path=str(self.folder / f"{number:02d}-{slug}.png"), full_page=True)
        self.steps.append(format_step(number, gesture, assertion, verdict))
        print(self.steps[-1], flush=True)
        if verdict == "FAIL":
            raise RuntimeError(self.failure)

    # --- reads -------------------------------------------------------------------------------------------------
    def panel(self):
        return support.panel_text(self.page)

    def expect_s3(self, what):
        expect(self.page.evaluate(STATE_JS), S3_STATE, f"{what}: the fields")
        expect(self.panel(), S3_PANEL, f"{what}: the panel")

    def expect_status(self, text, writes, copied):
        expect(self.page.locator("p.status").inner_text(), "Summary copied", "the copy status")
        expect(self.page.locator("p.status").get_attribute("class"), "status", "the copy status class")
        expect(self.page.evaluate("window.testClipboardText"), text, "the text the recorder received")
        expect(self.page.evaluate("window.testClipboardWrites"), writes, "the number of writes")
        (self.folder / copied).write_text(text, encoding="utf-8", newline="")  # exact, no added line end

    def expect_s1(self, what):
        expect(self.page.evaluate(ITEMS_JS), S1_ITEM_STATE, f"{what}: the items")
        expect(self.page.evaluate(SUMMARY_JS), S1_SUMMARY, f"{what}: the bill summary")
        expect(self.page.evaluate(TABLE_JS, "tbody"), S1_ROWS, f"{what}: the shares rows")
        expect(self.page.evaluate(TABLE_JS, "tfoot"), S1_CHECK, f"{what}: the check row")

    # --- gestures ----------------------------------------------------------------------------------------------
    def click_label(self, text):
        self.page.locator("fieldset.mode label", has_text=text).click()

    def click_button(self, name):
        self.page.get_by_role("button", name=name, exact=True).click()


def run_steps(gate):
    def page():
        return gate.page  # step 5 swaps the page, so every body asks again

    def cold_boot():
        page().goto(gate.base + "/")
        expect(page().evaluate("() => !Clipboard.prototype.writeText.toString().includes('[native code]')"), True,
               "the clipboard recorder is installed before any gesture")
        gate.expect_s3("cold boot")
        expect(page().evaluate("localStorage.getItem('split.draft')"), None, "the stored draft")

    def even_split():
        support.replace_text(page(), support.person_field(page(), 1), "Aisyah")
        support.replace_text(page(), support.person_field(page(), 2), "Ben")
        gate.click_button("Add person")
        expect(page().evaluate(ACTIVE_JS), "Person 3 name", "focus after Add person")
        page().keyboard.type("Chen")
        support.replace_text(page(), page().get_by_role("textbox", name="Subtotal in RM", exact=True), "100.00")
        expect(page().evaluate(SUMMARY_JS), S2_SUMMARY, "the bill summary")
        expect(page().evaluate(TABLE_JS, "tbody"), S2_ROWS, "the shares rows")
        expect(page().evaluate(TABLE_JS, "tfoot"), S2_CHECK, "the check row")

    def copy_even():
        gate.click_button("Copy summary")
        gate.expect_status(S2_COPY, 1, "clipboard-s2.txt")

    def by_item():
        gate.click_label("By item")
        for number, (name, price, people) in enumerate(S1_ITEMS, start=1):
            gate.click_button("Add item")
            expect(page().evaluate(ACTIVE_JS), f"Item {number} name", f"focus after Add item {number}")
            page().keyboard.type(name)
            page().keyboard.press("Tab")
            expect(page().evaluate(ACTIVE_JS), f"Item {number} price in RM", f"Tab from item {number}'s name")
            page().keyboard.type(price)
            for person in people:
                page().get_by_role("group", name=f"Who had {name}", exact=True).get_by_role("button", name=person, exact=True).click()
        gate.expect_s1("by item")
        gate.click_button("Copy summary")
        gate.expect_status(S1_COPY, 2, "clipboard-s1.txt")

    def come_back():
        context = gate.page.context
        gate.page.close()
        gate.page = context.new_page()  # a new page of the same context, so the stored draft is all it has
        page().goto(gate.base + "/")
        expect(page().locator("#mode-item").is_checked(), True, "By item is checked")
        gate.expect_s1("come back")
        gate.click_label("Even")
        expect(page().locator("#subtotal").input_value(), "100.00", "the Subtotal that was typed earlier")
        expect(page().evaluate(TABLE_JS, "tbody"), S2_ROWS, "the even shares rows")
        expect(page().evaluate(TABLE_JS, "tfoot"), S2_CHECK, "the even check row")

    def start_over():
        gate.click_button("New bill")
        dialog = page().get_by_role("dialog", name="Start a new bill?")
        expect(dialog.evaluate("(d) => d.matches(':modal')"), True, "the dialog is modal")
        expect(page().locator("#dialog-text").inner_text(), "This clears the people, items and amounts.", "the dialog text")
        expect(page().evaluate(ACTIVE_JS), "Cancel", "focus when the dialog opens")
        gate.click_button("Start new bill")
        expect(page().locator("dialog.dialog").evaluate("(d) => d.open"), False, "the dialog is closed")
        expect(page().evaluate(ACTIVE_JS), "New bill", "focus after Start new bill")
        gate.expect_s3("after Start new bill")
        page().reload()
        gate.expect_s3("after the reload")

    def throughout():
        problems = [f"console: {line}" for line in gate.console if line.startswith("error:") or "Content Security Policy" in line]
        problems += [f"page error: {line}" for line in gate.page_errors]
        problems += [f"request: {line}" for line in gate.requests if not request_is_allowed(gate.base, *line.split(" ", 1))]
        expect(problems, [], "console errors, page errors, CSP violations and foreign requests")
        expect(len(gate.requests) > 0, True, "the request log recorded the run")

    gate.step(1, "cold-boot", gesture="open / with empty storage", body=cold_boot,
              assertion="the S3 screen (two people, Even, empty Subtotal, 10 and 6, only the Shares message) and no split.draft key")
    gate.step(2, "even-split", body=even_split,
              gesture="replace Person 1 with Aisyah and Person 2 with Ben, click Add person, type Chen, type 100.00 in Subtotal",
              assertion="Bill summary RM 100.00, 10.00, 6.60, 116.60, shares RM 38.87, RM 38.87, RM 38.86, Adds up to RM 116.60")
    gate.step(3, "copy-even", gesture="click Copy summary", body=copy_even,
              assertion="status Summary copied and the recorder holds the S2 block exactly")
    gate.step(4, "by-item", body=by_item,
              gesture="click By item, add the four S1 items by typing names and prices, tap their people, click Copy summary",
              assertion="S1 shares RM 29.04, RM 15.74, RM 24.48, check row RM 59.40, RM 9.86, RM 69.26, "
                        "and the recorder holds the S1 block exactly")
    gate.step(5, "come-back", body=come_back,
              gesture="close the page, open / in a new page of the same context, click Even",
              assertion="the S1 screen as left, then Subtotal 100.00 and the S2 shares")
    gate.step(6, "start-over", body=start_over,
              gesture="click New bill, then Start new bill, then reload",
              assertion="the dialog is modal with Cancel focused, then the S3 screen, and the S3 screen again after the reload")
    gate.step(7, "throughout", body=throughout,
              gesture="no gesture, the logs of steps 1 to 6 are read",
              assertion="zero console errors, zero page errors, no Content Security Policy violation, only same-origin GETs")


def write_logs(gate):
    (gate.folder / "steps.log").write_text("\n".join(gate.steps) + "\n", encoding="utf-8")
    (gate.folder / "console.log").write_text("\n".join(gate.console) + ("\n" if gate.console else ""), encoding="utf-8")
    (gate.folder / "network.log").write_text("\n".join(gate.requests) + "\n", encoding="utf-8")


def main():
    started = datetime.datetime.now()
    folder = EVIDENCE_ROOT / started.strftime("%Y%m%d-%H%M%S")
    folder.mkdir(parents=True, exist_ok=True)
    server_lines = []

    def say(line):
        print(line, flush=True)
        server_lines.append(line)

    server = rig.StaticServer(rig.ROOT, say=say)
    gate = Gate(folder, None)
    facts = {"chromium": None, "port": None, "server_pid": None}
    try:
        server.start()
        facts.update(port=server.port, server_pid=server.process.pid)
        gate.base = server.base
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            facts["chromium"] = browser.version
            context = rig.new_context(browser, viewport=VIEWPORT, device_scale_factor=1, color_scheme="light")
            context.on("page", gate.watch)
            gate.page = context.new_page()
            try:
                run_steps(gate)
            except RuntimeError:
                pass  # recorded in gate.failure, reported below
            finally:
                context.close()
                browser.close()
    finally:
        server.stop()
        result = "PASS" if gate.failure is None and len(gate.steps) == 7 else "FAIL"
        write_logs(gate)
        (folder / "summary.json").write_text(json.dumps({
            "started": started.isoformat(timespec="seconds"), "ended": datetime.datetime.now().isoformat(timespec="seconds"),
            **facts, "viewport": VIEWPORT, "init_scripts": INIT_SCRIPTS, "storage_state": None, "bypass_csp": False,
            "steps": len(gate.steps), "failure": gate.failure, "server_log": server_lines, "result": result,
        }, indent=2) + "\n", encoding="utf-8")
    print(f"live gate {result}, evidence in {folder}")
    print("files:", ", ".join(sorted(path.name for path in folder.iterdir())))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
