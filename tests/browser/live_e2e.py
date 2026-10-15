"""Cold-boot live gate of v1.1.0 (qa.md, "Cold-boot live-e2e gate", spec R41). Run from the project root:
    python tests/browser/live_e2e.py [--engine chromium|webkit] [--control seeded] [--base-url http://127.0.0.1:<port>/]

A person's first session, end to end, against the shipped index.html, in a headless browser launched by rig.launch
(Chromium when no engine is named, R58) and one context made by rig.new_context. That context gets no stored bill, no
bypass_csp (the shipped policy is live for the whole run), no permission, and two init scripts, the clipboard recorder
(the operating system clipboard is never touched, not even read) and the CSP listener. Only real gestures change the app
(mouse clicks, typing, key presses, a reload, a new page). page.evaluate only reads.

--control seeded is the gate's control (qa.md, "Control mode"). The one context then holds the K2 bill as storage_state,
so the run must stop red at step 1 on the cold-boot assertions while the clipboard check passes. It can only make a run
fail. --base-url names the app as the caller already serves it from the project root, so the control and the green run
of an engine meet the same server. Without it the script serves the project root itself and stops that server at the end.

Evidence goes to docs/modules/split-app/qa/live-e2e/<YYYYMMDD-HHMMSS>-<engine>/, or -<engine>-control/ for the control:
NN-<slug>.jpg per step (the page's newest screencast frame once the step's checks are done, never a screenshot, which in
WebKit adds a stylesheet the policy refuses, R59 (4)), steps.log (each step's line, then one line per assertion),
console.log, network.log, clipboard-s2.txt, clipboard-s1.txt and summary.json. Exit status 0 only when every step and
every run check passed, which a control run never does.
"""
import argparse
import datetime
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

import rig
import seeds
import support
from expected import COLD_BOOT, S1_COPY, S1_ITEMS, S1_PROOF, S1_SPLITS, S2_COPY, S2_PROOF, S2_SPLITS

EVIDENCE_ROOT = rig.ROOT / "docs" / "modules" / "split-app" / "qa" / "live-e2e"
INIT_SCRIPTS = ["tests/browser/clipboard/recorder.js", "tests/browser/csp/listener.js"]  # in this order (qa.md, Rules)
VIEWPORT = {"width": 390, "height": 844}
STEPS = 9
ACTION_TIMEOUT_MS = 10_000  # bounds every click, key press and navigation
CLOSE_TIMEOUT_MS = 2_000  # M1 gives focus back in its close event, a task after the click (spec R59 (2))
QUIET_SECONDS, CAPTURE_LIMIT_SECONDS = 0.4, 5
CARD, SHEET = "#rbody", "#splitsDlg .rbody"
SHEET_SPARE_CHIP = "#splitsDlg .r-spare-acts button[aria-haspopup=dialog]"
P1_CLOSE, SHEET_CLOSE = "#spareDlg button[aria-label=Close]", "#splitsDlg button[aria-label=Close]"
PEOPLE = ["Aisyah", "Ben", "Chen"]
# The K1 items as ITEMS_JS reads them, the name, the price, then aria-pressed on each person's toggle.
K1_ITEMS = [[name, price, *("true" if person in had else "false" for person in PEOPLE)] for name, price, had in S1_ITEMS]
TOP_OF_THE_LIST = [amount for _, amount, _ in S2_SPLITS]  # K2's splits with the spare sen at the top (spec R20)
# Step 1's assertions that the control must see pass (the stand-in) and fail (the cold boot), qa.md "Control mode".
STAND_IN = "the clipboard stand-in is in place, writeText is not native and nothing was written"
NO_DRAFT = "split.draft is absent"
COLD_BOOT_PROPERTY = ("cold boot: bill-empty open", "cold boot: bill-empty strip", NO_DRAFT)

# Reads only. test_R41_the_gate_uses_real_gestures_and_reads_only keeps every evaluate argument on its read-only list.
STAND_IN_JS = """() => { const clip = navigator.clipboard;
  return [typeof clip?.writeText === 'function' && !Function.prototype.toString.call(clip.writeText).includes('[native code]'),
          window.testClipboardWrites]; }"""
TWO_FRAMES_JS = "() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))"
OPEN_DIALOGS_JS = "() => [...document.querySelectorAll('dialog')].filter((d) => d.open).map((d) => [d.id, d.matches(':modal')])"
PICKED_JS = """() => [...document.querySelectorAll('#pickList label.pill')].filter((pill) => pill.querySelector('input').checked)
  .map((pill) => pill.textContent.trim())"""
SECTIONS_JS = "() => ['#peopleBlk', '#chargesBlk'].map((selector) => document.querySelector(selector)?.dataset.open ?? null)"
ITEMS_JS = """() => [...document.querySelectorAll('li.item')].map((li) => [...li.querySelectorAll('input')].map((i) => i.value)
  .slice(0, 2).concat([...li.querySelectorAll('.tap')].map((b) => b.getAttribute('aria-pressed'))))"""
FOCUS_ON_NEW_BILL_JS = "() => document.activeElement?.id === 'newBill'"


def format_step(number, gesture, assertion, verdict):
    """One steps.log line. The gesture is what was done, the assertion is what was expected afterwards."""
    return f"{number:02d} | gesture: {gesture} | assertion: {assertion} | {verdict}"


def request_is_allowed(base, method, url):
    """qa.md, "Console and network": a same-origin GET for the page, its stylesheet, a file under /src/ or the favicon."""
    parts = urlsplit(url)
    path = parts.path
    return (method == "GET" and f"{parts.scheme}://{parts.netloc}" == base
            and (path in ("/", "/src/system.css", "/favicon.ico") or path.startswith("/src/")))


def first_line(error):
    return (str(error).strip().splitlines() or [""])[0][:300]


def cents(amounts):
    """The sum of money texts such as "RM 38.87" in sen, None when there are none to add."""
    return sum(int(re.sub(r"[^0-9]", "", amount)) for amount in amounts) if amounts else None


class StepFailed(Exception):
    """A step failed. The run stops there and still writes its evidence (qa.md, "Evidence artifact")."""


class Gate:
    """The run's one context, its current page with that page's screencast, the logs and the evidence folder."""

    def __init__(self, folder):
        self.folder, self.base, self.context, self.page = folder, None, None, None
        self.frame, self.frame_at = None, 0.0
        self.lines, self.checks, self.step_checks, self.captures = [], [], {}, []
        self.console, self.page_errors, self.requests = [], [], []
        self.csp_gone, self.writes_gone = [], 0  # what documents already gone recorded (a closed page, a reload)
        self.steps_run = self.steps_passed = 0
        self.first_failing_step = self.failure = self.stand_in = None

    def watch(self, page):
        page.on("console", lambda message: self.console.append(f"{message.type}: {message.text}"))
        page.on("pageerror", lambda error: self.page_errors.append(str(error)))
        page.on("request", lambda request: self.requests.append(f"{request.method} {request.url}"))

    # --- the page and its capture ------------------------------------------------------------------------------
    def open_page(self):
        """A new page of the context, its screencast started once as it opens (R41). Measured on 2026-10-15, frames keep
        coming across the page's navigations and reloads in both engines, and only when the screen changes."""
        self.page = self.context.new_page()
        self.frame = None
        self.page.screencast.start(on_frame=self.keep_frame, size=VIEWPORT)

    def keep_frame(self, frame):
        self.frame, self.frame_at = frame["data"], time.monotonic()

    def leave_document(self):
        """Keeps what the document about to go recorded, since a reload or a new page starts both records afresh."""
        self.csp_gone += self.csp_record()
        self.writes_gone += self.page.evaluate("window.testClipboardWrites") or 0

    def close_page(self):
        self.leave_document()
        self.page.screencast.stop()
        self.page.close()

    def finish(self):
        """The run's findings once the steps are over (problems), with the last document's writes kept and its screencast
        stopped. None when the page can no longer be read, which the summary reports as a failure."""
        try:
            found = self.problems()
            self.leave_document()
            self.page.screencast.stop()
            return found
        except Exception as error:
            self.failure = self.failure or f"run end: {type(error).__name__}: {first_line(error)}"
            return None

    def capture(self, name):
        """The step's capture (R41, H-05): two animation frames, then the newest screencast frame once none has come for
        400 ms, at most 5 s. Never a screenshot, which in WebKit adds a stylesheet the policy refuses (R59 (4))."""
        self.page.evaluate(TWO_FRAMES_JS)
        waited_from = time.monotonic()
        while self.frame is None or time.monotonic() - max(waited_from, self.frame_at) < QUIET_SECONDS:
            if time.monotonic() - waited_from >= CAPTURE_LIMIT_SECONDS:
                raise RuntimeError("capture gave up after 5 s")
            self.page.wait_for_timeout(25)  # frames are delivered while Playwright waits
        (self.folder / name).write_bytes(self.frame)
        self.captures.append(name)

    # --- steps and assertions ----------------------------------------------------------------------------------
    def step(self, number, slug, *, gesture, assertion, body):
        """Run body (the gestures, then the reads and checks), capture the screen, log the step. A failure stops the run.

        gesture is what a person does in this step, assertion is what must be true afterwards. Both are keyword-only so a
        swap shows in the call (test_R41_the_step_log_puts_gesture_and_assertion_in_their_own_fields).
        """
        self.checks = self.step_checks[number] = []
        try:
            body()
        except Exception as error:  # a timeout or a missing control fails the step like a failed assertion
            self.checks.append(f"FAIL {type(error).__name__}: {first_line(error)}")
        try:
            self.capture(f"{number:02d}-{slug}.jpg")
        except Exception as error:
            self.checks.append(f"FAIL {first_line(error)}")
        failed = [line for line in self.checks if line.startswith("FAIL")]
        self.steps_run += 1
        lines = [format_step(number, gesture, assertion, "FAIL" if failed else "PASS"), *(f"    {line}" for line in self.checks)]
        self.lines += lines
        print("\n".join(lines), flush=True)
        if failed:
            self.first_failing_step, self.failure = number, f"step {number:02d}: " + "; ".join(failed)
            raise StepFailed(self.failure)
        self.steps_passed += 1

    def verify(self, what, actual, expected):
        """One assertion of the running step, one line of steps.log. A failed one fails the step, and the step goes on, so
        the log names every failed assertion (the control's RED names each cold-boot part, qa.md)."""
        self.checks.append(f"PASS {what}" if actual == expected else f"FAIL {what}: expected {expected!r}, got {actual!r}")

    def control_red(self):
        """Whether the run stopped at step 1 on the cold-boot property with the stand-in check passed (qa.md, control)."""
        lines = self.step_checks.get(1, [])
        return (self.first_failing_step == 1 and f"PASS {STAND_IN}" in lines
                and all(any(line.startswith(f"FAIL {what}:") for line in lines) for what in COLD_BOOT_PROPERTY))

    # --- reads -------------------------------------------------------------------------------------------------
    def csp_record(self):
        found = self.page.evaluate("window.testCspViolations")
        return found if isinstance(found, list) else [f"the CSP listener kept no record ({found!r})"]

    def problems(self):
        """Step 9's findings over the whole run so far: console errors (and any console text naming the policy), page
        errors, what the CSP listener recorded in every document, and requests outside the rule."""
        return {
            "console": [line for line in self.console if line.startswith("error:") or "Content Security Policy" in line],
            "page": list(self.page_errors),
            "csp": self.csp_gone + self.csp_record(),
            "requests": [line for line in self.requests if not request_is_allowed(self.base, *line.split(" ", 1))],
        }

    def open_dialogs(self):
        return self.page.evaluate(OPEN_DIALOGS_JS)

    def strip_reads(self):
        """"The strip reads" (qa.md, Phrases), the visible text of #stripInfo with its white space made single."""
        return " ".join(self.page.locator("#stripInfo").inner_text().split())

    def splits(self, root):
        """The splits rows [name, amount, working] and the proof [amount, working] of the receipt at root, None for a part
        the page does not hold."""
        found = support.receipt(self.page, root) or {}
        rows, proof = found.get("list"), found.get("proof")
        return rows and rows["rows"], proof and [proof["amount"], proof["working"]]

    def amounts(self, root):
        rows, _ = self.splits(root)
        return rows and [amount for _, amount, _ in rows]

    def bill_empty(self, when):
        found = support.cold_boot_state(self.page)
        for key, expected in COLD_BOOT.items():
            self.verify(f"{when}: bill-empty {key}", found.get(key), expected)

    def copied(self, text, writes, keep_as=None):
        """Checks the sheet's status and what the clipboard stand-in received after a Copy summary in the sheet."""
        self.page.evaluate(TWO_FRAMES_JS)  # the copy settles in a promise
        self.verify("the sheet's status", support.reads(self.page, SHEET + " > p.status"), "Summary copied")
        received = self.page.evaluate("window.testClipboardText")
        self.verify("the text the stand-in received", received, text)
        self.verify("the writes the stand-in counted", self.page.evaluate("window.testClipboardWrites"), writes)
        if keep_as and isinstance(received, str):
            (self.folder / keep_as).write_text(received, encoding="utf-8", newline="")  # exact, no added line end

    # --- gestures ----------------------------------------------------------------------------------------------
    def click(self, selector, text=None):
        """A mouse click on the one visible control at selector, narrowed to the one holding text."""
        (self.page.locator(selector, has_text=text) if text else self.page.locator(selector)).click()

    def choose(self, rule):
        self.click("#spareDlg label.choice", rule)


def run_steps(gate):
    def page():
        return gate.page  # step 7 opens a new page, so every body asks again

    def cold_boot():
        page().goto(gate.base + "/")
        found = page().evaluate(STAND_IN_JS)
        gate.stand_in = found == [True, 0]
        gate.verify(STAND_IN, found, [True, 0])
        gate.verify("the CSP listener is in place", page().evaluate("Array.isArray(window.testCspViolations)"), True)
        gate.bill_empty("cold boot")
        gate.verify(NO_DRAFT, page().evaluate("localStorage.getItem('split.draft')"), None)

    def even_split():
        support.replace_text(page(), support.person_field(page(), 1), "Aisyah")
        support.replace_text(page(), support.person_field(page(), 2), "Ben")
        page().get_by_role("button", name="Add person", exact=True).click()
        gate.verify("focus after Add person", support.active_label(page()), "Person 3 name")
        page().keyboard.type("Chen")
        support.replace_text(page(), page().get_by_role("textbox", name="Subtotal in RM", exact=True), "100.00")
        gate.verify("the strip reads", gate.strip_reads(), "Total RM 116.60")

    def splits_sheet():
        gate.click("#splitsBtn")
        gate.verify("the open dialogs", gate.open_dialogs(), [["splitsDlg", True]])
        rows, proof = gate.splits(SHEET)
        gate.verify("the sheet's splits", rows, S2_SPLITS)
        gate.verify("the sheet's spare line", support.reads(page(), SHEET + " > div.r-spare > p"), "2 sen left over")
        gate.verify("the sheet's proof", proof, S2_PROOF)
        gate.click(SHEET + " > button.r-copy")
        gate.copied(S2_COPY, 1, keep_as="clipboard-s2.txt")

    def one_person():
        gate.click(SHEET_SPARE_CHIP)
        gate.verify("the open dialogs", gate.open_dialogs(), [["splitsDlg", True], ["spareDlg", True]])
        gate.choose("One person")
        gate.verify("the checked pill", page().evaluate(PICKED_JS), ["Aisyah"])
        gate.verify("the sheet's splits", gate.amounts(SHEET), ["RM 38.88", "RM 38.86", "RM 38.86"])
        gate.click("#pickList label.pill", "Ben")
        gate.verify("the checked pill", page().evaluate(PICKED_JS), ["Ben"])
        gate.verify("the sheet's splits", gate.amounts(SHEET), ["RM 38.86", "RM 38.88", "RM 38.86"])

    def at_random():
        gate.choose("At random")
        drawn = gate.amounts(SHEET)
        gate.click("#pickAgainSheet")
        again = gate.amounts(SHEET)
        gate.verify(f"the splits after Pick again differ from the draw before it, {drawn}", again is not None and again != drawn, True)
        gate.verify("the splits after Pick again add up to RM 116.60, in sen", cents(again), 11660)
        gate.verify("the sheet's proof", gate.splits(SHEET)[1], S2_PROOF)
        gate.click(P1_CLOSE)
        gate.verify("the open dialogs", gate.open_dialogs(), [["splitsDlg", True]])
        rows = [f"{name} {amount}" for name, amount, _ in gate.splits(SHEET)[0] or []]
        gate.click(SHEET + " > button.r-copy")
        page().evaluate(TWO_FRAMES_JS)
        copied = page().evaluate("window.testClipboardText") or ""
        gate.verify("lines 3 to 5 of the copied text are the sheet's splits rows", copied.split("\n")[2:5], rows)
        gate.verify("the writes the stand-in counted", page().evaluate("window.testClipboardWrites"), 2)
        gate.click(SHEET_SPARE_CHIP)
        gate.choose("Top of the list")
        gate.verify("the sheet's splits", gate.amounts(SHEET), TOP_OF_THE_LIST)
        gate.click(P1_CLOSE)
        gate.click(SHEET_CLOSE)
        gate.verify("the open dialogs", gate.open_dialogs(), [])

    def by_item():
        gate.click("div.mode-sw label", "By item")
        for number, (name, price, had) in enumerate(S1_ITEMS, start=1):
            page().get_by_role("button", name="Add item", exact=True).click()
            gate.verify(f"focus after Add item {number}", support.active_label(page()), f"Item {number} name")
            page().keyboard.type(name)
            page().keyboard.press("Tab")
            gate.verify(f"focus after Tab from item {number}'s name", support.active_label(page()), f"{name} price in RM")
            page().keyboard.type(price)
            for person in had:
                page().get_by_role("group", name=f"Who had {name}", exact=True).get_by_role("button", name=person, exact=True).click()
        gate.verify("the strip reads", gate.strip_reads(), "Total RM 69.26")
        gate.click("#splitsBtn")
        rows, proof = gate.splits(SHEET)
        gate.verify("the sheet's splits with their working", rows, S1_SPLITS)
        gate.verify("the sheet's proof", proof, S1_PROOF)
        gate.click(SHEET + " > button.r-copy")
        gate.copied(S1_COPY, 3, keep_as="clipboard-s1.txt")
        gate.click(SHEET_CLOSE)
        gate.verify("the open dialogs", gate.open_dialogs(), [])

    def come_back():
        gate.close_page()
        gate.open_page()  # a new page of the same context, so the stored draft is all it has
        page().goto(gate.base + "/")
        gate.verify("By item is checked", page().locator("#modeItem").is_checked(), True)
        gate.verify("the items, their prices and who had them", page().evaluate(ITEMS_JS), K1_ITEMS)
        gate.verify("the sections, People and Charges", page().evaluate(SECTIONS_JS), ["false", "false"])
        rows, proof = gate.splits(CARD)
        gate.verify("the card's splits with their working", rows, S1_SPLITS)
        gate.verify("the card's proof", proof, S1_PROOF)
        gate.verify("the strip reads", gate.strip_reads(), "Total RM 69.26")
        gate.click("div.mode-sw label", "Even")
        gate.verify("the Subtotal", page().locator("#evenSub").input_value(), "100.00")
        gate.verify("the card's splits", gate.amounts(CARD), TOP_OF_THE_LIST)

    def start_over():
        gate.click("#newBill")
        gate.verify("the open dialogs", gate.open_dialogs(), [["newDlg", True]])
        gate.verify("focus when the dialog opens", support.active_label(page()), "Cancel")
        gate.click("#startNew")
        try:  # a bounded wait for M1's close task, then the checks below give the verdict
            page().wait_for_function(FOCUS_ON_NEW_BILL_JS, timeout=CLOSE_TIMEOUT_MS)
        except PlaywrightTimeoutError:
            pass
        gate.verify("the open dialogs", gate.open_dialogs(), [])
        gate.verify("focus after Start new bill", support.active_label(page()), "newBill")
        gate.bill_empty("after Start new bill")
        gate.leave_document()
        page().reload()
        gate.bill_empty("after the reload")

    def throughout():
        found = gate.problems()
        gate.verify("console errors and console text naming the Content Security Policy", found["console"], [])
        gate.verify("page errors", found["page"], [])
        gate.verify("CSP violations the listener recorded in every document", found["csp"], [])
        gate.verify("requests that are not same-origin GETs for the page's own files", found["requests"], [])
        gate.verify("the request log recorded the run", len(gate.requests) > 0, True)

    gate.step(1, "cold-boot", body=cold_boot,
              gesture="open / in the run's one new context",
              assertion="the clipboard stand-in is in place, the screen is bill-empty with People open and the strip "
                        "reading Enter the subtotal to see the splits., and split.draft is absent")
    gate.step(2, "even-split", body=even_split,
              gesture="replace Person 1 with Aisyah and Person 2 with Ben, click Add person, type Chen, type 100.00 in Subtotal",
              assertion="the strip reads Total RM 116.60")
    gate.step(3, "splits-sheet", body=splits_sheet,
              gesture="click Splits, then Copy summary in the sheet",
              assertion="the splits RM 38.87, RM 38.87, RM 38.86, 2 sen left over and the proof RM 116.60, then "
                        "Summary copied and the stand-in holds the S2 block exactly")
    gate.step(4, "one-person", body=one_person,
              gesture="click the sheet's spare chip, then One person, then tap the Ben pill",
              assertion="the Aisyah pill checked with RM 38.88, RM 38.86, RM 38.86, then RM 38.86, RM 38.88, RM 38.86")
    gate.step(5, "at-random", body=at_random,
              gesture="click At random and Pick again in P1, close P1, click Copy summary in the sheet, open P1 from the "
                      "chip, click Top of the list, close P1 and the sheet",
              assertion="the splits changed and add up to RM 116.60, lines 3 to 5 of the copied text are the sheet's "
                        "splits rows, then RM 38.87, RM 38.87, RM 38.86")
    gate.step(6, "by-item", body=by_item,
              gesture="click By item, add the four K1 items by typing their names and prices and tapping their people, "
                      "click Splits and Copy summary in the sheet, close the sheet",
              assertion="the strip reads Total RM 69.26, the K1 rows with their working and the proof RM 69.26, and the "
                        "stand-in holds the S1 block exactly")
    gate.step(7, "come-back", body=come_back,
              gesture="reload in a new page of the same context, then click Even",
              assertion="the K1 screen with both sections folded, then Subtotal 100.00 and RM 38.87, RM 38.87, RM 38.86")
    gate.step(8, "start-over", body=start_over,
              gesture="click New bill, then Start new bill, then reload",
              assertion="the dialog with Cancel focused, then bill-empty with People open and focus on New bill, and "
                        "bill-empty with People open again after the reload")
    gate.step(9, "throughout", body=throughout,
              gesture="no gesture, the records of steps 1 to 8 are read",
              assertion="zero console errors, zero page errors, zero CSP violations and only same-origin GETs")


def loopback_url(text):
    """--base-url, an app served on the loopback address as qa.md's server lifecycle serves it."""
    if not re.fullmatch(r"http://127\.0\.0\.1:\d+/?", text):
        raise argparse.ArgumentTypeError(f"expected http://127.0.0.1:<port>/, got {text!r}")
    return text.rstrip("/")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Cold-boot live gate of split-app (R41).")
    parser.add_argument("--engine", choices=list(rig.ENGINES), default=rig.DEFAULT_ENGINE, help="browser engine (R58)")
    parser.add_argument("--control", choices=["seeded"], default=None,
                        help="the gate's control, which boots from the K2 bill and must fail at step 1")
    parser.add_argument("--base-url", type=loopback_url, default=None,
                        help="an app already served from the project root, so a control and a green run share one server")
    return parser.parse_args(argv)


def write_evidence(gate, found, summary):
    folder = gate.folder
    (folder / "steps.log").write_text("\n".join(gate.lines) + "\n", encoding="utf-8")
    records = gate.console + [f"pageerror: {error}" for error in gate.page_errors] + [f"csp: {item}" for item in found["csp"]]
    (folder / "console.log").write_text("".join(f"{line}\n" for line in records), encoding="utf-8")
    (folder / "network.log").write_text("".join(f"{line}\n" for line in gate.requests), encoding="utf-8")
    (folder / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def main(argv=None):
    args = parse_args(argv)
    started = datetime.datetime.now()
    folder = EVIDENCE_ROOT / f"{started:%Y%m%d-%H%M%S}-{args.engine}{'-control' if args.control else ''}"
    folder.mkdir(parents=True)  # never exist_ok, so a run cannot write into an earlier run's folder
    server_log = []

    def say(line):
        print(line, flush=True)
        server_log.append(line)

    server = None if args.base_url else rig.StaticServer(rig.ROOT, say=say)
    gate, facts, found = Gate(folder), {"browser_version": None, "port": None, "server_pid": None}, None
    try:
        if server:
            server.start()
            gate.base = server.base
            facts.update(port=server.port, server_pid=server.process.pid)
        else:
            gate.base = args.base_url
            facts["port"] = urlsplit(gate.base).port
        with sync_playwright() as playwright:
            browser = rig.launch(playwright, args.engine)
            facts["browser_version"] = browser.version
            gate.context = rig.new_context(
                browser, clipboard=Path(INIT_SCRIPTS[0]).stem,
                init_scripts=[(rig.ROOT / script).read_text(encoding="utf-8") for script in INIT_SCRIPTS[1:]],
                viewport=VIEWPORT, device_scale_factor=1, color_scheme="dark", reduced_motion="reduce",
                storage_state=rig.storage_state(gate.base, seeds.S2) if args.control == "seeded" else None)
            gate.context.set_default_timeout(ACTION_TIMEOUT_MS)
            gate.context.on("page", gate.watch)
            try:
                gate.open_page()
                run_steps(gate)
            except StepFailed:
                pass  # recorded in the gate, reported below
            finally:
                found = gate.finish()
                gate.context.close()
                browser.close()
    except Exception as error:  # the server, the browser or the page broke outside a step
        gate.failure = gate.failure or f"run: {type(error).__name__}: {first_line(error)}"
    finally:
        if server:
            server.stop()
    found = found or {"console": [], "page": [], "csp": ["not read, the run broke first"], "requests": []}
    passed = args.control is None and gate.steps_passed == STEPS and not any(found.values())
    summary = {
        "started": started.isoformat(timespec="seconds"), "ended": datetime.datetime.now().isoformat(timespec="seconds"),
        "engine": args.engine, "browser_version": facts["browser_version"], "control": args.control,
        "base_url": gate.base, "port": facts["port"], "server_pid": facts["server_pid"],
        "server": "served by this run" if server else "served by the caller (--base-url)", "server_log": server_log,
        "viewport": VIEWPORT, "device_scale_factor": 1, "color_scheme": "dark", "reduced_motion": "reduce",
        "init_scripts": INIT_SCRIPTS, "storage_state": "the K2 bill (seeds.S2)" if args.control else None, "bypass_csp": False,
        "capture": "the page's newest screencast frame per step (JPEG), never a screenshot", "captures": gate.captures,
        "steps_planned": STEPS, "steps_run": gate.steps_run, "steps_passed": gate.steps_passed,
        "first_failing_step": gate.first_failing_step, "failure": gate.failure,
        "requests": len(gate.requests), "requests_outside_the_rule": len(found["requests"]),
        "console_errors": len(found["console"]), "page_errors": len(found["page"]), "csp_violations": len(found["csp"]),
        "clipboard_stand_in": gate.stand_in, "clipboard_writes": gate.writes_gone,
        "pass": passed, "result": "PASS" if passed else "FAIL",
    }
    if args.control:
        summary["control_red_on_its_property"] = gate.control_red()
    write_evidence(gate, found, summary)
    print(f"live gate {summary['result']}, evidence in {folder}")
    if args.control:
        print(f"CONTROL {args.control}", "RED at step 1 on its property" if summary["control_red_on_its_property"]
              else "NOT RED at step 1 on its property, so the gate cannot tell a seeded start from a cold one")
    print("files:", ", ".join(sorted(path.name for path in folder.iterdir())))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
