"""Shared helpers for the regression QA scripts in this folder (step 3 and the hand-driven flows).

Test-side only. It reads the project and never writes to it; every file it writes lands in the evidence folder that
the caller passes in. It reuses the suite's own helpers (support, seeds, expected) so the driven checks read the page
the same way the suite does. Every browser context is made by rig.new_context, so the clipboard is always the suite's
recorder (CG-7), and no permission is granted and no policy is bypassed (rig refuses both).
"""
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(r"{workspace}\examples\split")
TESTS = ROOT / "tests" / "browser"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

import rig  # noqa: E402
import seeds  # noqa: E402
import support  # noqa: E402
import expected  # noqa: E402

POWERSHELL = r"C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe"
FAILED_COPY = "Could not copy. Your browser blocked the clipboard."

TABLE_JS = ("(part) => [...document.querySelectorAll(`table.shares ${part} tr`)]"
            ".map((tr) => [...tr.children].map((c) => c.textContent.trim()))")
SUMMARY_JS = ("() => [...document.querySelectorAll('dl.sum .row')].map((r) => [r.querySelector('dt').textContent.trim(),"
              " r.querySelector('.amt').textContent.trim(), (r.querySelector('.work') || { textContent: '' }).textContent.trim()])")
STATE_JS = """() => ({
  people: [...document.querySelectorAll('li.person input')].map((i) => i.value),
  removeDisabled: [...document.querySelectorAll('li.person button')].map((b) => b.disabled),
  mode: document.querySelector('input[name=mode]:checked').value,
  subtotal: document.querySelector('#subtotal') ? document.querySelector('#subtotal').value : null,
  items: [...document.querySelectorAll('li.item')].map((li) => [...li.querySelectorAll('input')].map((i) => i.value)
    .concat([...li.querySelectorAll('.tap')].map((b) => b.getAttribute('aria-pressed')))),
  rates: [document.querySelector('#rate-service').value, document.querySelector('#rate-sst').value],
  notes: document.querySelectorAll('div.note').length,
  errors: document.querySelectorAll('p.error').length,
})"""
CHIP_BOXES_JS = """() => {
  window.qaChips = [...document.querySelectorAll('.who button')];
  return window.qaChips.map((node, index) => { const r = node.getBoundingClientRect(); return { index, x: r.x, y: r.y, w: r.width, h: r.height }; });
}"""
OVER_ITS_OWN_REMOVE_JS = """(boxes) => {
  const found = [];
  for (const b of boxes) {
    const item = window.qaChips[b.index].closest('li.item');
    for (let x = b.x + 2; x < b.x + b.w - 1; x += 4) for (let y = b.y + 2; y < b.y + b.h - 1; y += 4) {
      const under = document.elementFromPoint(x, y);
      const button = under && under.closest('button');
      if (button && /^Remove/.test(button.getAttribute('aria-label') || '') && button.closest('li.item') === item) {
        found.push([x, y, button.getAttribute('aria-label')]);
      }
    }
  }
  return found;
}"""
SETTLE_JS = "() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))"


def chromium_pids():
    """PIDs of the Chromium processes Playwright started (its temporary profile is on their command line).

    The query skips its own PowerShell process ($PID), which carries the same words in its command line.
    """
    script = ("Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -ne $PID -and "
              "$_.CommandLine -like '*playwright_chromiumdev_profile*' } | ForEach-Object { $_.ProcessId }")
    done = subprocess.run([POWERSHELL, "-NoProfile", "-Command", script], capture_output=True, text=True, timeout=60)
    return sorted(int(token) for token in done.stdout.split() if token.isdigit())


class Log:
    """Prints a line and keeps it for a log file in the evidence folder."""

    def __init__(self, path):
        self.path = Path(path)
        self.lines = []

    def say(self, text):
        print(text, flush=True)
        self.lines.append(str(text))

    def save(self):
        self.path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")


def start_server(log):
    """python -m http.server on a free loopback port from the project root (rig.StaticServer, the same command)."""
    return rig.StaticServer(ROOT, say=log.say).start()


class Session:
    """One browser context with its console, page-error and request logs. Empty storage unless seed is given."""

    def __init__(self, browser, base, *, seed=None, clipboard="recorder", viewport=(390, 844)):
        self.base = base
        options = {"viewport": {"width": viewport[0], "height": viewport[1]}, "device_scale_factor": 1,
                   "color_scheme": "light"}
        if seed is not None:
            options["storage_state"] = rig.storage_state(base, seed)
        self.console, self.page_errors, self.requests = [], [], []
        self.context = rig.new_context(browser, clipboard=clipboard, **options)
        self.context.on("page", self._watch)
        self.page = self.context.new_page()

    def _watch(self, page):
        page.on("console", lambda message: self.console.append(f"{message.type}: {message.text}"))
        page.on("pageerror", lambda error: self.page_errors.append(str(error)))
        page.on("request", lambda request: self.requests.append(f"{request.method} {request.url}"))

    def new_page(self):
        return self.context.new_page()

    def allowed(self, line):
        method, url = line.split(" ", 1)
        parts = urlsplit(url)
        own = f"{parts.scheme}://{parts.netloc}" == self.base
        return method == "GET" and own and (parts.path in ("/", "/src/system.css", "/favicon.ico")
                                            or parts.path.startswith("/src/"))

    def problems(self):
        found = [f"console {line}" for line in self.console if line.startswith("error:") or "Content Security Policy" in line]
        found += [f"page error: {error}" for error in self.page_errors]
        found += [f"request: {line}" for line in self.requests if not self.allowed(line)]
        return found

    def close(self):
        self.context.close()


class Checks:
    """Every expectation of a script, with its expected and observed value. A row is PASS only when they are equal."""

    def __init__(self):
        self.rows = []

    def expect(self, group, step, what, expected_value, observed):
        ok = observed == expected_value
        self.rows.append({"group": group, "step": step, "what": what, "expected": expected_value,
                          "observed": observed, "result": "PASS" if ok else "FAIL"})
        return ok

    def note(self, group, step, what, observed):
        """An observation recorded as data, with no expected value to match."""
        self.rows.append({"group": group, "step": step, "what": what, "expected": None, "observed": observed,
                          "result": "NOTE"})

    def failed(self):
        return [row for row in self.rows if row["result"] == "FAIL"]


def cents(text):
    """'RM 116.60' -> 11660. Only the plain amounts these screens show."""
    match = re.fullmatch(r"RM (\d+)\.(\d\d)", text.strip())
    return int(match.group(1)) * 100 + int(match.group(2)) if match else None


def table_rows(page, part):
    return page.evaluate(TABLE_JS, part)


def summary_rows(page):
    return page.evaluate(SUMMARY_JS)


def state(page):
    return page.evaluate(STATE_JS)


def stored(page):
    return page.evaluate("localStorage.getItem('split.draft')")


def panel(page):
    return support.panel_text(page)


def settle(page):
    page.evaluate(SETTLE_JS)


def active_label(page):
    return support.active_label(page)


def person(page, number):
    return support.person_field(page, number)


def item_name(page, number):
    return page.get_by_label(f"Item {number} name", exact=True)


def item_price(page, number):
    return page.get_by_label(f"Item {number} price in RM", exact=True)


def who_group(page, item_label):
    return page.get_by_role("group", name=f"Who had {item_label}", exact=True)


def toggle(page, item_label, who):
    return who_group(page, item_label).get_by_role("button", name=who, exact=True)


def subtotal(page):
    return page.get_by_role("textbox", name="Subtotal in RM", exact=True)


def rate(page, label):
    return page.get_by_role("textbox", name=f"{label} in percent", exact=True)


def button(page, name):
    return page.get_by_role("button", name=name, exact=True)


def switch_mode(page, label):
    page.locator("fieldset.mode label", has_text=label).click()


def copy_button(page):
    return page.locator("button.copy")


def dialog_open(page):
    return page.locator("dialog.dialog").evaluate("(d) => d.open")
