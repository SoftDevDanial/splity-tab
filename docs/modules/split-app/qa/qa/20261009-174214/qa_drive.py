"""Independent QA driver for split-app (finder, read-only on the app).

Starts its own `python -m http.server` on a free loopback port, drives headless Chromium with real gestures,
and compares every money figure on screen to split-core computed in Node (oracle.mjs) or to the hand-typed
values of qa.md. CG-7: every context installs tests/browser/clipboard/<script>.js (the recorder by default) plus a
guard that refuses clipboard reads, and no permission is ever granted, so the operating system clipboard is never
touched, not even to read it. Prints PASS / FAIL / OBS lines and writes driver-results.json next to this file.
Usage: python qa_drive.py [F1 F2 ...]   (no argument runs every flow)
"""
import json
import random
import socket
import subprocess
import sys
import time
import traceback
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path("{workspace}/examples/split")
OUT = Path(__file__).resolve().parent
SHOTS = OUT / "shots"
ORACLE = OUT / "oracle.mjs"
CLIP_DIR = ROOT / "tests" / "browser" / "clipboard"
BASE = ""

GUARD_JS = """(() => { if (typeof Clipboard === 'function') {
  const refuse = () => Promise.reject(new DOMException('QA driver never reads the clipboard', 'NotAllowedError'));
  Clipboard.prototype.readText = refuse; Clipboard.prototype.read = refuse; } })();"""

S2 = ('{"version":1,"bill":{"mode":"even","people":[{"id":"p1","name":"Aisyah"},{"id":"p2","name":"Ben"},{"id":"p3","name":"Chen"}],'
      '"subtotalText":"100.00","items":[],"serviceText":"10","sstText":"6","nextId":4}}')
S1 = ('{"version":1,"bill":{"mode":"item","people":[{"id":"p1","name":"Aisyah"},{"id":"p2","name":"Ben"},{"id":"p3","name":"Chen"}],'
      '"subtotalText":"","items":[{"id":"i4","name":"Nasi lemak ayam","priceText":"15.90","who":["p1"]},'
      '{"id":"i5","name":"Char kuey teow","priceText":"13.50","who":["p2"]},{"id":"i6","name":"Mee goreng mamak","priceText":"12.00","who":["p3"]},'
      '{"id":"i7","name":"Satay, 10 sticks","priceText":"18.00","who":["p1","p3"]}],"serviceText":"10","sstText":"6","nextId":8}}')
S5 = S1.replace('"name":"Mee goreng mamak","priceText":"12.00","who":["p3"]', '"name":"Mee goreng mamak","priceText":"12.00","who":[]')
assert S5 != S1

MSG = {"rates": "Check the charges to see the shares.", "subtotal": "Enter the subtotal to see the shares.",
       "no-items": "Add an item to see the shares.", "prices": "Give every item a price to see the shares."}
S1_ROWS = [["Aisyah", "RM 24.90", "RM 4.14", "RM 29.04"], ["Ben", "RM 13.50", "RM 2.24", "RM 15.74"], ["Chen", "RM 21.00", "RM 3.48", "RM 24.48"]]
S1_FOOT = [["Adds up to", "RM 59.40", "RM 9.86", "RM 69.26"]]
S1_SUM = [["Subtotal", "RM 59.40", ""], ["+Service charge", "RM 5.94", "10% of RM 59.40"], ["+SST", "RM 3.92", "6% of RM 65.34"], ["=Total", "RM 69.26", ""]]
S2_ROWS = [["Aisyah", "RM 38.87"], ["Ben", "RM 38.87"], ["Chen", "RM 38.86"]]
S2_FOOT = [["Adds up to", "RM 116.60"]]
S2_SUM = [["Subtotal", "RM 100.00", ""], ["+Service charge", "RM 10.00", "10% of RM 100.00"], ["+SST", "RM 6.60", "6% of RM 110.00"], ["=Total", "RM 116.60", ""]]
S1_ITEMS = [("Nasi lemak ayam", "15.90", ["Aisyah"]), ("Char kuey teow", "13.50", ["Ben"]),
            ("Mee goreng mamak", "12.00", ["Chen"]), ("Satay, 10 sticks", "18.00", ["Aisyah", "Chen"])]
S2_COPY = ("Bill split\nTotal RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)\n"
           "Aisyah RM 38.87\nBen RM 38.87\nChen RM 38.86\nAdds up to RM 116.60")
S1_COPY = ("Bill split\nTotal RM 69.26 (subtotal RM 59.40, service 10% RM 5.94, SST 6% RM 3.92)\n"
           "Aisyah RM 29.04\nBen RM 15.74\nChen RM 24.48\nAdds up to RM 69.26")
FAILED_COPY = "Could not copy. Your browser blocked the clipboard."

RESULTS = []
OBS = []


def check(flow, name, ok, detail=""):
    RESULTS.append({"flow": flow, "check": name, "ok": bool(ok), "detail": str(detail)[:1500]})
    print(("PASS " if ok else "FAIL "), flow, "|", name, ("| " + str(detail)[:900]) if not ok else "", flush=True)


def observe(flow, text):
    OBS.append({"flow": flow, "note": text})
    print("OBS  ", flow, "|", text, flush=True)


# ------------------------------------------------------------------ server and oracle
def free_port():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def oracle(bills):
    done = subprocess.run(["node", str(ORACLE), str(ROOT).replace("\\", "/")], input=json.dumps({"bills": bills}),
                          capture_output=True, text=True, encoding="utf-8", timeout=30)
    if done.returncode:
        raise RuntimeError("oracle failed: " + done.stderr)
    data = json.loads(done.stdout)
    return data["results"], data["newBill"]


# ------------------------------------------------------------------ session
class Session:
    def __init__(self, browser, flow, viewport=(390, 844), touch=False, reduced_motion=None, clipboard="recorder",
                 seed=None, init_scripts=(), goto=True):
        self.flow, self.clipboard = flow, clipboard
        options = {"viewport": {"width": viewport[0], "height": viewport[1]}, "device_scale_factor": 1, "color_scheme": "light"}
        if reduced_motion:
            options["reduced_motion"] = reduced_motion
        if touch:
            options["has_touch"] = True
        if seed is not None:
            options["storage_state"] = {"cookies": [], "origins": [{"origin": BASE, "localStorage": [{"name": "split.draft", "value": seed}]}]}
        # Never permissions, never bypass_csp (CG-7, R38).
        self.ctx = browser.new_context(**options)
        self.ctx.set_default_timeout(8000)
        self.ctx.set_default_navigation_timeout(15000)
        self.ctx.add_init_script(script=(CLIP_DIR / f"{clipboard}.js").read_text(encoding="utf-8"))
        self.ctx.add_init_script(script=GUARD_JS)
        for script in init_scripts:
            self.ctx.add_init_script(script=script)
        self.console, self.errors, self.requests = [], [], []
        self.ctx.on("page", self._watch)
        self.page = self.ctx.new_page()
        if goto:
            self.open()

    def _watch(self, page):
        page.on("console", lambda m: self.console.append((m.type, m.text)))
        page.on("pageerror", lambda e: self.errors.append(str(e)))
        page.on("request", lambda r: self.requests.append((r.method, r.url)))

    def guard(self, page):
        if self.clipboard == "recorder":
            ok = page.evaluate("() => typeof Clipboard === 'function' && !Clipboard.prototype.writeText.toString().includes('[native code]')")
        elif self.clipboard == "reject":
            ok = page.evaluate("() => !Clipboard.prototype.writeText.toString().includes('[native code]')")
        else:
            ok = page.evaluate("() => navigator.clipboard === undefined")
        if not ok:
            raise SystemExit("CG-7 guard: the clipboard stub is not in place, refusing to continue")

    def open(self, page=None):
        page = page or self.page
        page.goto(BASE + "/")
        self.guard(page)
        return page

    def reload(self, page=None):
        page = page or self.page
        page.reload()
        self.guard(page)

    def problems(self):
        found = [f"console {k}: {t}" for k, t in self.console if k == "error" or "Content Security Policy" in t]
        found += [f"page error: {e}" for e in self.errors]
        for method, url in self.requests:
            path = url[len(BASE):] if url.startswith(BASE) else url
            if not (method == "GET" and url.startswith(BASE) and (path in ("/", "/src/system.css", "/favicon.ico") or path.startswith("/src/"))):
                found.append(f"request: {method} {url}")
        return found

    def close(self, record=True):
        if record:
            found = self.problems()
            check(self.flow, "no console error, page error, CSP line or foreign request", not found, "; ".join(found))
        self.ctx.close()


# ------------------------------------------------------------------ page helpers
READ_PANEL_JS = """() => {
  const tape = document.querySelector('div.tape');
  const cells = (tr) => [...tr.children].map((c) => c.textContent.trim());
  const table = tape.querySelector('table.shares');
  const msg = tape.querySelector('p.result-msg');
  const status = tape.querySelector('p.status');
  return {
    message: msg ? msg.textContent.trim() : null,
    summary: [...tape.querySelectorAll('dl.sum .row')].map((r) => [r.querySelector('dt').textContent.trim(),
      r.querySelector('.amt').textContent.trim(), r.querySelector('.work') ? r.querySelector('.work').textContent.trim() : '']),
    table: !!table,
    heads: table ? [...table.querySelectorAll('thead th')].map((c) => c.textContent.trim()) : [],
    rows: table ? [...table.querySelectorAll('tbody tr')].map(cells) : [],
    foot: table ? [...table.querySelectorAll('tfoot tr')].map(cells) : [],
    hasCopy: !!tape.querySelector('button.copy'),
    hasStatus: !!status,
    statusText: status ? status.textContent : null,
    statusClass: status ? status.className : null,
    sections: tape.querySelectorAll('section.tape-section').length,
  };
}"""

SNAPSHOT_JS = """() => ({
  people: [...document.querySelectorAll('li.person input')].map((i) => i.value),
  mode: document.querySelector('input[name=mode]:checked').value,
  subtotal: document.querySelector('#subtotal') ? document.querySelector('#subtotal').value : null,
  items: [...document.querySelectorAll('li.item')].map((li) => [...li.querySelectorAll('input')].map((i) => i.value)
    .concat([...li.querySelectorAll('.tap')].map((b) => b.getAttribute('aria-pressed')))),
  rates: [document.querySelector('#rate-service').value, document.querySelector('#rate-sst').value],
})"""

# Only errors that are displayed: a hidden block (the other mode) keeps its flags and its error paragraph in the DOM
# with the hidden attribute (spec: "a block that is not rendered is either absent or carries the hidden attribute").
ERRORS_JS = """() => {
  const shown = (e) => e.getClientRects().length > 0;
  return {
    errors: [...document.querySelectorAll('p.error')].filter(shown).map((e) => [e.id, e.textContent]),
    invalid: [...document.querySelectorAll('[aria-invalid]')].filter(shown).map((e) => e.id || e.getAttribute('aria-label')),
  };
}"""

ACTIVE_NAME_JS = """() => { const el = document.activeElement; if (!el) return null;
  return el.getAttribute('aria-label') || (el.labels && el.labels.length ? el.labels[0].textContent.trim() : '') || el.textContent.trim() || el.id; }"""

RING_JS = """() => { const el = document.activeElement;
  const lit = (n) => { if (!n) return false; const s = getComputedStyle(n); return s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0; };
  return { name: el.getAttribute('aria-label') || (el.labels && el.labels.length ? el.labels[0].textContent.trim() : '') || el.textContent.trim(),
    visible: el.matches(':focus-visible'), ring: lit(el) || lit(el.closest('.field')) || lit(el.closest('fieldset.mode')) }; }"""

OVERFLOW_JS = """() => { const w = window.innerWidth; const bad = [];
  for (const e of document.querySelectorAll('body *')) { if (getComputedStyle(e).display === 'none') continue;
    if (e.closest('.sr-only') || e.classList.contains('sr-only')) continue; const r = e.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue; if (r.right > w + 0.5 || r.left < -0.5) bad.push(e.tagName.toLowerCase() + '.' + e.className + ' ' + Math.round(r.left) + '..' + Math.round(r.right)); }
  return { scrollWidth: document.documentElement.scrollWidth, innerWidth: w, bad: bad.slice(0, 6) }; }"""


def person(p, i):
    return p.get_by_label(f"Person {i} name", exact=True)


def item_name(p, j):
    return p.get_by_label(f"Item {j} name", exact=True)


def item_price(p, j):
    return p.get_by_label(f"Item {j} price in RM", exact=True)


def button(p, name):
    return p.get_by_role("button", name=name, exact=True)


def toggle(p, item, who):
    return p.get_by_role("group", name=f"Who had {item}", exact=True).get_by_role("button", name=who, exact=True)


def replace(p, loc, text):
    loc.click()
    p.keyboard.press("Control+A")
    if text:
        p.keyboard.type(text)
    else:
        p.keyboard.press("Backspace")


def mode(p, label):
    p.locator("label[for=mode-item]" if label == "item" else "label[for=mode-even]").click()


def stored_text(p):
    return p.evaluate("localStorage.getItem('split.draft')")


def stored_bill(p):
    return json.loads(stored_text(p))["bill"]


def snapshot(p):
    return p.evaluate(SNAPSHOT_JS)


def active_name(p):
    return p.evaluate(ACTIVE_NAME_JS)


def panel(p):
    return p.evaluate(READ_PANEL_JS)


def norm_rows(rows):
    return [[c.strip() for c in row] for row in rows]


def panel_diff(exp, got):
    d = []
    kind = exp["kind"]
    if kind == "blocked":
        if got["message"] != MSG[exp["reason"]]:
            d.append(f"message {got['message']!r} want {MSG[exp['reason']]!r}")
        if got["summary"] or got["table"] or got["hasCopy"] or got["hasStatus"] or got["sections"] != 1:
            d.append(f"blocked panel holds more than the message: {got['sections']} sections, summary {bool(got['summary'])}, table {got['table']}, copy {got['hasCopy']}")
    elif kind == "unassigned":
        count = exp["count"]
        want = ("1 item still needs a person. Tap who had it to see the shares." if count == 1
                else f"{count} items still need a person. Tap who had each one to see the shares.")
        if got["message"] != want:
            d.append(f"message {got['message']!r} want {want!r}")
        if norm_rows(got["summary"]) != norm_rows(exp["summary"]):
            d.append(f"summary {got['summary']} want {exp['summary']}")
        if got["table"] or got["hasCopy"] or got["hasStatus"]:
            d.append("unassigned panel shows a table, copy button or status")
    else:
        if got["message"] is not None:
            d.append(f"unexpected message {got['message']!r}")
        if norm_rows(got["summary"]) != norm_rows(exp["summary"]):
            d.append(f"summary {got['summary']} want {exp['summary']}")
        if norm_rows(got["rows"]) != norm_rows(exp["rows"]):
            d.append(f"rows {got['rows']} want {exp['rows']}")
        if norm_rows(got["foot"]) != [["Adds up to"] + exp["check"]]:
            d.append(f"check row {got['foot']} want {exp['check']}")
        heads = ["Person", "Share"] if kind == "even" else ["Person", "Items", "+Charges", "=Share"]
        if got["heads"] != heads:
            d.append(f"heads {got['heads']} want {heads}")
        if not got["hasCopy"] or not got["hasStatus"]:
            d.append("copy button or status missing")
    return d


def verify_panel(flow, label, p, bill=None):
    bill = bill or stored_bill(p)
    exp = oracle([bill])[0][0]
    diff = panel_diff(exp, panel(p))
    check(flow, label, not diff, "; ".join(diff))
    return exp


def errors_now(p):
    return p.evaluate(ERRORS_JS)


def shot(p, name):
    SHOTS.mkdir(exist_ok=True)
    p.screenshot(path=str(SHOTS / f"{name}.png"))


def centre(loc):
    loc.scroll_into_view_if_needed()
    b = loc.bounding_box()
    return b["x"] + b["width"] / 2, b["y"] + b["height"] / 2


def add_item_by_gestures(p, name, price, people):
    button(p, "Add item").click()
    p.keyboard.type(name)  # Add item moves focus to the new name field (R34), so typing lands there
    j = p.locator("li.item").count()
    typed = item_name(p, j).input_value() == name
    replace(p, item_price(p, j), price)
    for who in people:
        toggle(p, name, who).click()
    return typed


def build_three_people(p):
    replace(p, person(p, 1), "Aisyah")
    replace(p, person(p, 2), "Ben")
    button(p, "Add person").click()
    p.keyboard.type("Chen")


# ------------------------------------------------------------------ F1 even split from a cold boot
def flow_even(browser):
    F = "F1 even split from a cold boot"
    s = Session(browser, F)
    p = s.page
    check(F, "cold boot people", [i.input_value() for i in p.locator("li.person input").all()] == ["Person 1", "Person 2"])
    check(F, "cold boot removes disabled", all(b.is_disabled() for b in p.locator("li.person button").all()))
    check(F, "cold boot Even checked, subtotal empty, 10 and 6",
          p.locator("#mode-even").is_checked() and p.locator("#subtotal").input_value() == "" and
          (p.locator("#rate-service").input_value(), p.locator("#rate-sst").input_value()) == ("10", "6"))
    check(F, "cold boot panel is the Shares heading and the subtotal message",
          panel(p)["message"] == MSG["subtotal"] and panel(p)["sections"] == 1 and not panel(p)["summary"])
    check(F, "cold boot writes nothing to storage", stored_text(p) is None)
    check(F, "cold boot has no __ hook on window", p.evaluate("Object.getOwnPropertyNames(window).filter((n) => n.startsWith('__'))") == [])
    shot(p, "f1-01-cold-boot")
    build_three_people(p)
    check(F, "Add person focuses the new empty name", True if person(p, 3).input_value() == "Chen" else False)
    sub = p.locator("#subtotal")
    sub.click()
    for n, key in enumerate("100.00", start=1):
        p.keyboard.type(key)
        verify_panel(F, f"panel follows keystroke {n} ({'100.00'[:n]!r})", p)
        if n == 1:
            check(F, "no error while typing", errors_now(p) == {"errors": [], "invalid": []})
    got = panel(p)
    check(F, "hand-typed S2 figures", got["summary"] == S2_SUM and got["rows"] == S2_ROWS and got["foot"] == S2_FOOT,
          f"{got['summary']} {got['rows']} {got['foot']}")
    check(F, "stored draft equals the S2 seed", json.loads(stored_text(p)) == json.loads(S2), stored_text(p))
    shot(p, "f1-02-even-s2")
    for text in ["0.01", "0.05", "1", "99999.99", "100000", "12.345", "1,000", "7.00", "33.33", "0", "abc"]:
        replace(p, sub, text)
        verify_panel(F, f"subtotal {text!r} panel", p)
        p.keyboard.press("Tab")
        exp = oracle([stored_bill(p)])[0][0]["invalid"]["subtotal"]
        shown = bool(p.locator("p.error#subtotal-error").count())
        check(F, f"subtotal {text!r} error after leaving iff invalid", shown == exp, f"shown {shown} expected {exp}")
        if shown:
            check(F, f"subtotal {text!r} aria-invalid and describedby", sub.get_attribute("aria-invalid") == "true" and
                  sub.get_attribute("aria-describedby").split()[0] == "subtotal-error")
    replace(p, sub, "100.00")
    for _ in range(9):
        button(p, "Add person").click()
    check(F, "12 people and Add person disabled", p.locator("li.person").count() == 12 and button(p, "Add person").is_disabled())
    verify_panel(F, "12-way even split", p)
    s.close()


# ------------------------------------------------------------------ F2 by-item S1, shared items, S5, blocked messages
def flow_items(browser):
    F = "F2 by-item S1 bill"
    s = Session(browser, F)
    p = s.page
    build_three_people(p)
    replace(p, p.locator("#subtotal"), "100.00")
    mode(p, "item")
    verify_panel(F, "By item with no items: Add an item message", p)
    for name, price, people in S1_ITEMS:
        ok = add_item_by_gestures(p, name, price, people)
        check(F, f"item {name!r} typed into the focused new field", ok)
        verify_panel(F, f"panel after item {name!r}", p)
    got = panel(p)
    check(F, "hand-typed S1 figures", got["summary"] == S1_SUM and got["rows"] == S1_ROWS and got["foot"] == S1_FOOT,
          f"{got['summary']} {got['rows']} {got['foot']}")
    check(F, "heads are Person, Items, +Charges, =Share", got["heads"] == ["Person", "Items", "+Charges", "=Share"])
    bill = stored_bill(p)
    check(F, "stored draft equals the S1 bill with the typed 100.00 subtotal",
          bill == dict(json.loads(S1)["bill"], subtotalText="100.00"), json.dumps(bill))
    shot(p, "f2-01-s1")
    toggle(p, "Satay, 10 sticks", "Ben").click()
    got = panel(p)
    check(F, "Ben joins Satay: hand-typed figures", got["rows"] == [["Aisyah", "RM 21.90", "RM 3.64", "RM 25.54"], ["Ben", "RM 19.50", "RM 3.24", "RM 22.74"],
                                                                     ["Chen", "RM 18.00", "RM 2.98", "RM 20.98"]] and got["foot"] == S1_FOOT, str(got["rows"]))
    verify_panel(F, "Ben joins Satay vs oracle", p)
    toggle(p, "Satay, 10 sticks", "Ben").click()
    check(F, "Ben leaves Satay: S1 returns", panel(p)["rows"] == S1_ROWS)
    toggle(p, "Mee goreng mamak", "Chen").click()
    got = panel(p)
    check(F, "S5 unassigned: summary kept, message, no table/copy/status",
          got["summary"] == S1_SUM and got["message"] == "1 item still needs a person. Tap who had it to see the shares." and
          not got["table"] and not got["hasCopy"] and not got["hasStatus"], str(got))
    check(F, "S5 no error styling on items or toggles", errors_now(p) == {"errors": [], "invalid": []} and
          p.locator("li.item .error, .tap[aria-invalid]").count() == 0)
    shot(p, "f2-02-s5")
    verify_panel(F, "S5 vs oracle", p)
    toggle(p, "Char kuey teow", "Ben").click()
    got = panel(p)
    check(F, "two items need a person: plural message", got["message"] == "2 items still need a person. Tap who had each one to see the shares.", got["message"])
    verify_panel(F, "two unassigned vs oracle", p)
    toggle(p, "Mee goreng mamak", "Chen").click()
    toggle(p, "Char kuey teow", "Ben").click()
    check(F, "both toggles back: S1 table returns", panel(p)["rows"] == S1_ROWS and panel(p)["foot"] == S1_FOOT)
    button(p, "Remove Chen").click()
    verify_panel(F, "Chen removed (items need a person)", p)
    check(F, "Chen is off every group", all(p.get_by_role("group", name=f"Who had {n}", exact=True).get_by_role("button").all_inner_texts() == ["Aisyah", "Ben"]
                                              for n, _, _ in S1_ITEMS))
    s.close()
    cases = [
        ("rates (empty service)", S2, lambda q: replace(q, q.locator("#rate-service"), ""), "rates"),
        ("rates (SST 25)", S1, lambda q: replace(q, q.locator("#rate-sst"), "25"), "rates"),
        ("subtotal emptied", S2, lambda q: replace(q, q.locator("#subtotal"), ""), "subtotal"),
        ("no items", None, lambda q: mode(q, "item"), "no-items"),
        ("unpriced item", None, lambda q: (mode(q, "item"), button(q, "Add item").click()), "prices"),
        ("price abc", S1, lambda q: replace(q, item_price(q, 1), "abc"), "prices"),
    ]
    for label, seed, act, reason in cases:
        s = Session(browser, F + " blocked", seed=seed)
        act(s.page)
        exp = oracle([stored_bill(s.page)])[0][0]
        check(F, f"blocked: {label} is reason {reason}", exp["kind"] == "blocked" and exp["reason"] == reason, str(exp))
        verify_panel(F, f"blocked: {label} panel", s.page)
        s.close()
    s = Session(browser, F + " I2")
    p = s.page
    build_three_people(p)
    mode(p, "item")
    add_item_by_gestures(p, "Tea", "10.00", ["Ben"])
    add_item_by_gestures(p, "Cake", "5.01", ["Ben", "Chen"])
    got = panel(p)
    check(F, "I2 hand-typed: Aisyah listed with RM 0.00", got["rows"] == [["Aisyah", "RM 0.00", "RM 0.00", "RM 0.00"], ["Ben", "RM 12.51", "RM 2.08", "RM 14.59"],
                                                                         ["Chen", "RM 2.50", "RM 0.41", "RM 2.91"]] and got["foot"] == [["Adds up to", "RM 15.01", "RM 2.49", "RM 17.50"]], str(got["rows"]))
    verify_panel(F, "I2 vs oracle", p)
    s.close()


# ------------------------------------------------------------------ F3 charges edits
def flow_charges(browser):
    F = "F3 charges edits"
    s = Session(browser, F, seed=S2)
    p = s.page
    svc, sst = p.locator("#rate-service"), p.locator("#rate-sst")
    for a, b in [("0", "6"), ("12.5", "8"), ("30", "20"), ("0", "0"), ("7.25", "3.5"), ("10", "6")]:
        replace(p, svc, a)
        replace(p, sst, b)
        exp = verify_panel(F, f"service {a} / SST {b} panel", p)
        check(F, f"service {a} / SST {b} no error", errors_now(p) == {"errors": [], "invalid": []} and exp["kind"] == "even")
    replace(p, svc, "0")
    replace(p, sst, "6")
    got = panel(p)
    check(F, "service 0: working line '0% of RM 100.00', RM 0.00, SST RM 6.00 and shares 35.34/35.33/35.33",
          got["summary"][1] == ["+Service charge", "RM 0.00", "0% of RM 100.00"] and got["summary"][2] == ["+SST", "RM 6.00", "6% of RM 100.00"] and
          [r[1] for r in got["rows"]] == ["RM 35.34", "RM 35.33", "RM 35.33"], str(got["summary"]))
    for field, bad, good, eid, msg in [(svc, "31", "10", "rate-service-error", "Enter a rate from 0 to 30"),
                                       (sst, "20.01", "6", "rate-sst-error", "Enter a rate from 0 to 20")]:
        replace(p, field, bad)
        check(F, f"{bad}: no error while the field has focus", p.locator(f"#{eid}").count() == 0)
        verify_panel(F, f"{bad}: panel follows the bad text (Check the charges)", p)
        p.keyboard.press("Tab")
        err = p.locator(f"p.error#{eid}")
        check(F, f"{bad}: error shows after leaving with text {msg!r}", err.count() == 1 and err.inner_text() == msg)
        check(F, f"{bad}: aria-invalid and describedby '{eid} charges-hint'", field.get_attribute("aria-invalid") == "true" and
              field.get_attribute("aria-describedby") == f"{eid} charges-hint")
        check(F, f"{bad}: error is the last child of its cell", err.evaluate("(e) => e === e.parentElement.lastElementChild"))
        shot(p, f"f3-error-{eid}")
        field.click()
        p.keyboard.press("Control+A")
        p.keyboard.type(good[0])
        check(F, f"{bad}: error gone after the first valid key (Control+A then {good!r})", p.locator(f"#{eid}").count() == 0 and field.get_attribute("aria-invalid") is None)
        p.keyboard.type(good[1:])
        p.keyboard.press("Tab")
        check(F, f"{bad}: error does not come back after fixing", p.locator(f"#{eid}").count() == 0)
    replace(p, svc, "")
    p.keyboard.press("Tab")
    check(F, "empty service: no error, Check the charges message",
          errors_now(p) == {"errors": [], "invalid": []} and panel(p)["message"] == MSG["rates"])
    s.close()


# ------------------------------------------------------------------ F4 copy summary
def flow_copy(browser):
    F = "F4 copy summary"
    for label, seed, want in [("S2", S2, S2_COPY), ("S1", S1, S1_COPY)]:
        s = Session(browser, F, seed=seed)
        p = s.page
        got = panel(p)
        check(F, f"{label}: status exists, empty, not displayed", got["hasStatus"] and got["statusText"] == "" and
              not p.locator("p.status").is_visible())
        button(p, "Copy summary").click()
        got = panel(p)
        check(F, f"{label}: status 'Summary copied' with class exactly 'status'", got["statusText"] == "Summary copied" and got["statusClass"] == "status", str(got["statusText"]))
        text = p.evaluate("window.testClipboardText")
        check(F, f"{label}: recorder text equals the qa.md block", text == want, repr(text))
        exp = oracle([stored_bill(p)])[0][0]
        check(F, f"{label}: recorder text equals split-core summaryText", text == exp["copy"], repr(exp["copy"]))
        check(F, f"{label}: exactly one write", p.evaluate("window.testClipboardWrites") == 1)
        button(p, "Copy summary").click()
        check(F, f"{label}: a second click writes again and the status stays", p.evaluate("window.testClipboardWrites") == 2 and panel(p)["statusText"] == "Summary copied")
        if label == "S1":
            person(p, 3).click()
            p.keyboard.press("End")
            p.keyboard.type(" Wei")
            check(F, "S1: status survives a name edit while the table stays", panel(p)["statusText"] == "Summary copied")
            button(p, "Copy summary").click()
            check(F, "S1: next copy uses the new name on line 5", p.evaluate("window.testClipboardText").split("\n")[4] == "Chen Wei RM 24.48")
            replace(p, item_price(p, 1), "abc")
            check(F, "S1: status goes when the table goes", not panel(p)["hasStatus"])
            replace(p, item_price(p, 1), "15.90")
            check(F, "S1: status is back and empty when the table is back", panel(p)["hasStatus"] and panel(p)["statusText"] == "")
        shot(p, f"f4-copy-{label}")
        button(p, "Copy summary").click()
        s.reload()
        check(F, f"{label}: status is not saved (empty after reload)", panel(p)["statusText"] == "")
        s.close()
    for clip in ("reject", "missing"):
        s = Session(browser, F, seed=S2, clipboard=clip)
        p = s.page
        before = stored_text(p)
        button(p, "Copy summary").click()
        got = panel(p)
        check(F, f"{clip}.js: failure status text and class 'status status-failure'", got["statusText"] == FAILED_COPY and got["statusClass"] == "status status-failure", str(got["statusText"]) + "|" + str(got["statusClass"]))
        check(F, f"{clip}.js: bill and draft unchanged, table still there", stored_text(p) == before and got["rows"] == S2_ROWS)
        shot(p, f"f4-copy-{clip}")
        s.close()


# ------------------------------------------------------------------ F5 reload restore, F6 unreadable
def flow_restore(browser):
    F = "F5 reload restore"
    s = Session(browser, F)
    p = s.page
    build_three_people(p)
    replace(p, p.locator("#subtotal"), "100.00")
    mode(p, "item")
    for name, price, people in S1_ITEMS:
        add_item_by_gestures(p, name, price, people)
    replace(p, p.locator("#rate-service"), "12.5")
    replace(p, p.locator("#rate-sst"), "8")
    before = snapshot(p)
    before_panel = panel(p)
    s.reload()
    check(F, "same context reload: same screen", snapshot(p) == before)
    verify_panel(F, "reload: panel vs oracle", p)
    check(F, "reload: panel equals the one before", panel(p)["rows"] == before_panel["rows"] and panel(p)["summary"] == before_panel["summary"])
    mode(p, "even")
    check(F, "reload then Even shows the 100.00 typed earlier", p.locator("#subtotal").input_value() == "100.00")
    verify_panel(F, "Even after reload: panel vs oracle", p)
    mode(p, "item")
    check(F, "By item again shows the items as left", snapshot(p) == before)
    p.close()
    again = s.ctx.new_page()
    s.open(again)
    check(F, "new page in the same context: same screen", snapshot(again) == before)
    verify_panel(F, "new page: panel vs oracle", again)
    text = stored_text(again)
    s.reload(again)
    check(F, "restore does not rewrite the draft", stored_text(again) == text)
    s.close()
    bad = json.loads(S2)
    bad["bill"]["subtotalText"] = "0"
    bad["bill"]["serviceText"] = "31"
    s = Session(browser, F, seed=json.dumps(bad, separators=(",", ":")))
    e = errors_now(s.page)
    check(F, "restored bad subtotal and service rate show their errors at once",
          sorted(x[0] for x in e["errors"]) == ["rate-service-error", "subtotal-error"], str(e))
    s.close()


def flow_unreadable(browser):
    F = "F6 unreadable draft"
    base = json.loads(S2)

    def variant(**kw):
        d = json.loads(S2)
        d["bill"].update(kw)
        return json.dumps(d, separators=(",", ":"))

    cases = {
        "B1 not json": "not json",
        "B3 null": "null",
        "B4 version 2": json.dumps(dict(base, version=2), separators=(",", ":")),
        "B7 mode split": variant(mode="split"),
        "B9 13 people": variant(people=[{"id": f"p{i}", "name": f"N{i}"} for i in range(1, 14)], nextId=14),
        "B18 21-char name": variant(people=[{"id": "p1", "name": "ABCDEFGHIJKLMNOPQRSTU"}, {"id": "p2", "name": "Ben"}], nextId=3),
        "B19 newline in name": variant(people=[{"id": "p1", "name": "Ai\nsyah"}, {"id": "p2", "name": "Ben"}], nextId=3),
        "B22 nextId 3": variant(nextId=3),
        "B24 nextId 2e9": variant(nextId=2000000000),
        "B21 numeric subtotal": variant(subtotalText=100),
    }
    new_bill = oracle([base["bill"]])[1]
    for label, seed in cases.items():
        s = Session(browser, F, seed=seed)
        p = s.page
        note = p.locator("div.note-wrap > div.note[role=status]")
        ok = note.count() == 1 and note.locator("p").inner_text() == "Your saved bill could not be read, so a new one was started." and \
            note.get_by_role("button", name="Dismiss note").count() == 1
        check(F, f"{label}: note text, role and dismiss button", ok)
        check(F, f"{label}: S3 shows under the note", [i.input_value() for i in p.locator("li.person input").all()] == ["Person 1", "Person 2"] and
              panel(p)["message"] == MSG["subtotal"])
        check(F, f"{label}: draft now holds the new bill", json.loads(stored_text(p)) == {"version": 1, "bill": new_bill}, stored_text(p))
        if label.startswith("B1 "):
            shot(p, "f6-note-B1")
        s.reload()
        check(F, f"{label}: reload shows no note", p.locator("div.note").count() == 0)
        s.close()
    s = Session(browser, F, seed=cases["B1 not json"])
    p = s.page
    button(p, "Dismiss note").click()
    check(F, "dismiss removes the note and focuses Person 1 name", p.locator("div.note").count() == 0 and active_name(p) == "Person 1 name")
    s.close()
    s = Session(browser, F, seed=cases["B1 not json"])
    p = s.page
    button(p, "New bill").click()
    button(p, "Start new bill").click()
    check(F, "Start new bill does not hide or move the note", p.locator("div.note").count() == 1)
    s.close()
    g3 = json.dumps(base, separators=(",", ":")).replace('"bill":{', '"bill":{"__proto__":{"polluted":true},', 1)
    s = Session(browser, F, seed=g3)
    p = s.page
    check(F, "G3 __proto__ inside bill: loads as S2 with no note and no pollution",
          p.locator("div.note").count() == 0 and panel(p)["rows"] == S2_ROWS and p.evaluate("({}).polluted") is None)
    s.close()
    flags = "\U0001F1F2\U0001F1FE" * 20
    s = Session(browser, F, seed=variant(people=[{"id": "p1", "name": flags}, {"id": "p2", "name": "Ben"}], nextId=3))
    p = s.page
    check(F, "G2 twenty flag emoji load in full", p.locator("div.note").count() == 0 and person(p, 1).input_value() == flags)
    s.close()


# ------------------------------------------------------------------ F7 new bill dialog
def flow_new_bill(browser):
    F = "F7 New bill dialog"

    ways = ["cancel", "escape", "backdrop corner (10,10)", "backdrop over Person 1 name", "backdrop over a toggle", "backdrop over Add person",
            "backdrop bottom-right", "backdrop over New bill itself"]
    for way in ways:
        s = Session(browser, F, seed=S1)
        p = s.page
        before_text, before_snap = stored_text(p), snapshot(p)
        button(p, "New bill").click()
        dlg = p.locator("dialog.dialog")
        if way == "cancel":
            check(F, "opens modal, named, described, focus on Cancel", dlg.evaluate("(d) => d.matches(':modal')") and
                  p.get_by_role("dialog", name="Start a new bill?").count() == 1 and
                  p.locator("#dialog-text").inner_text() == "This clears the people, items and amounts." and active_name(p) == "Cancel")
            seen = []
            for _ in range(6):
                p.keyboard.press("Tab")
                seen.append(active_name(p))
            check(F, "Tab cycles Start new bill / Cancel only", seen == ["Start new bill", "Cancel"] * 3, str(seen))
            seen = []
            for _ in range(5):
                p.keyboard.press("Shift+Tab")
                seen.append(active_name(p))
            check(F, "Shift+Tab cycles Start new bill / Cancel only", seen == ["Start new bill", "Cancel", "Start new bill", "Cancel", "Start new bill"], str(seen))
            check(F, "page behind is clipped to the viewport", p.locator(".app").evaluate("(e) => e.getBoundingClientRect().height") == 844)
            p.mouse.move(195, 100)
            p.mouse.wheel(0, 600)
            check(F, "wheel over the page leaves scrollY at 0", p.evaluate("window.scrollY") == 0)
            shot(p, "f7-dialog-open")
            box = dlg.bounding_box()
            p.mouse.click(box["x"] + 6, box["y"] + 6)
            p.mouse.click(box["x"] + box["width"] / 2, box["y"] + 40)
            check(F, "a click inside the dialog box (padding, title) keeps it open", dlg.evaluate("(d) => d.open"))
            button(p, "Cancel").click()
        elif way == "escape":
            p.keyboard.press("Escape")
        elif way == "backdrop corner (10,10)":
            p.mouse.click(10, 10)
        elif way == "backdrop over Person 1 name":
            x, y = centre(person(p, 1))
            p.mouse.click(x, y)
        elif way == "backdrop over a toggle":
            x, y = centre(toggle(p, "Char kuey teow", "Aisyah"))
            p.mouse.click(x, y)
        elif way == "backdrop over Add person":
            x, y = centre(button(p, "Add person"))
            p.mouse.click(x, y)
        elif way == "backdrop bottom-right":
            p.mouse.click(385, 840)
        elif way == "backdrop over New bill itself":
            x, y = centre(button(p, "New bill"))
            p.mouse.click(x, y)
        check(F, f"{way}: dialog closed", not dlg.evaluate("(d) => d.open"))
        check(F, f"{way}: focus is on New bill", active_name(p) == "New bill", active_name(p))
        check(F, f"{way}: draft and screen unchanged", stored_text(p) == before_text and snapshot(p) == before_snap)
        verify_panel(F, f"{way}: panel still S1", p)
        s.close()
    s = Session(browser, F, seed=S1)
    p = s.page
    button(p, "New bill").click()
    button(p, "Start new bill").click()
    new_bill = oracle([json.loads(S1)["bill"]])[1]
    check(F, "Start: dialog closed, focus on New bill", not p.locator("dialog.dialog").evaluate("(d) => d.open") and active_name(p) == "New bill")
    check(F, "Start: S3 screen", [i.input_value() for i in p.locator("li.person input").all()] == ["Person 1", "Person 2"] and
          p.locator("#mode-even").is_checked() and p.locator("#subtotal").input_value() == "" and
          (p.locator("#rate-service").input_value(), p.locator("#rate-sst").input_value()) == ("10", "6") and panel(p)["message"] == MSG["subtotal"])
    check(F, "Start: draft equals split-core newBill()", json.loads(stored_text(p)) == {"version": 1, "bill": new_bill}, stored_text(p))
    shot(p, "f7-after-start")
    s.reload()
    check(F, "Start: reload still S3", panel(p)["message"] == MSG["subtotal"] and p.locator("li.person").count() == 2)
    s.close()
    s = Session(browser, F, seed=S2)
    p = s.page
    button(p, "Copy summary").click()
    button(p, "New bill").click()
    button(p, "Start new bill").click()
    check(F, "Start clears the copy status", not panel(p)["hasStatus"])
    replace(p, p.locator("#subtotal"), "100.00")
    check(F, "status is empty again when the table returns", panel(p)["hasStatus"] and panel(p)["statusText"] == "")
    s.close()
    bad = json.loads(S2)
    bad["bill"]["subtotalText"] = "0"
    bad["bill"]["sstText"] = "25"
    s = Session(browser, F, seed=json.dumps(bad, separators=(",", ":")))
    p = s.page
    check(F, "setup: two errors showing", len(errors_now(p)["errors"]) == 2)
    button(p, "New bill").click()
    button(p, "Start new bill").click()
    check(F, "Start clears all inline errors", errors_now(p) == {"errors": [], "invalid": []})
    replace(p, p.locator("#subtotal"), "abc")
    check(F, "typing bad text after a start-over shows no early error", errors_now(p)["errors"] == [])
    p.keyboard.press("Tab")
    check(F, "the error rule still works after a start-over", len(errors_now(p)["errors"]) == 1)
    s.close()


# ------------------------------------------------------------------ F8 double click / double tap
def flow_double_click(browser):
    F = "F8 double click and double tap"
    outcomes = {}
    for vp in [(390, 844), (360, 780), (1280, 800)]:
        for how in ["mouse dblclick", "mouse 2 clicks 80ms apart", "mouse 2 clicks 250ms apart", "touch 2 taps 60ms apart", "touch 2 taps 200ms apart"]:
            s = Session(browser, F, viewport=vp, touch=how.startswith("touch"), seed=S1)
            p = s.page
            before_text, before_snap = stored_text(p), snapshot(p)
            cx, cy = centre(button(p, "New bill"))
            if how == "mouse dblclick":
                p.mouse.dblclick(cx, cy)
            elif how.startswith("mouse"):
                gap = 80 if "80" in how else 250
                p.mouse.click(cx, cy)
                p.wait_for_timeout(gap)
                p.mouse.click(cx, cy)
            else:
                gap = 60 if "60" in how else 200
                p.touchscreen.tap(cx, cy)
                p.wait_for_timeout(gap)
                p.touchscreen.tap(cx, cy)
            p.wait_for_timeout(300)
            open_after = p.locator("dialog.dialog").evaluate("(d) => d.open")
            intact = stored_text(p) == before_text and snapshot(p) == before_snap
            outcomes[f"{vp[0]}x{vp[1]} {how}"] = "dialog open" if open_after else "dialog closed"
            check(F, f"{vp[0]}x{vp[1]} {how}: the bill is NOT wiped", intact, f"stored now {stored_text(p)[:80]}")
            if open_after:
                button(p, "Cancel").click()
            s.close()
    observe(F, "after a double click or double tap on New bill the dialog ends up: " + json.dumps(outcomes))
    s = Session(browser, F + " geometry", seed=S1)
    p = s.page
    worst = []
    sizes = [(320, 568), (360, 640), (360, 780), (375, 667), (390, 844), (414, 896), (568, 320), (640, 360), (667, 375), (736, 414), (812, 375),
             (844, 390), (896, 414), (1024, 768), (1280, 800), (1280, 300), (390, 300), (360, 260), (390, 220), (1280, 200), (360, 200)]
    for w, h in sizes:
        p.set_viewport_size({"width": w, "height": h})
        p.wait_for_timeout(50)
        b = button(p, "New bill").bounding_box()
        cx, cy = b["x"] + b["width"] / 2, b["y"] + b["height"] / 2
        button(p, "New bill").click()
        hit = p.evaluate("([x, y]) => { const e = document.elementFromPoint(x, y); if (!e) return null; "
                         "const b = e.closest('button'); return { tag: e.tagName.toLowerCase(), text: b ? b.textContent.trim() : null }; }", [cx, cy])
        if hit and hit["text"] in ("Start new bill", "Cancel"):
            worst.append((w, h, hit))
        p.mouse.click(cx, cy)  # the second click of a double click, wherever it lands
        p.wait_for_timeout(100)
        if stored_text(p) != S1:
            worst.append((w, h, "DRAFT CHANGED"))
        if p.locator("dialog.dialog").evaluate("(d) => d.open"):
            p.keyboard.press("Escape")
        p.wait_for_timeout(50)
    check(F, f"scan of {len(sizes)} viewports: no dialog button under the New bill button, and the second click never changes the draft", not worst, str(worst))
    s.close()
    landed = []
    for label, seed in [("S1", S1), ("S2", S2)]:
        for vp in [(390, 844), (360, 780), (375, 667), (1280, 800)]:
            for how in ["mouse", "touch"]:
                for target in ["Cancel", "Start new bill"]:
                    s = Session(browser, F, viewport=vp, touch=how == "touch", seed=seed)
                    p = s.page
                    before_text, before_snap = stored_text(p), snapshot(p)
                    button(p, "New bill").click()
                    cx, cy = centre(button(p, target))
                    if how == "mouse":
                        p.mouse.dblclick(cx, cy)
                    else:
                        p.touchscreen.tap(cx, cy)
                        p.touchscreen.tap(cx, cy)
                    p.wait_for_timeout(300)
                    if target == "Cancel":
                        same = stored_text(p) == before_text and snapshot(p) == before_snap
                        check(F, f"{label} {vp[0]}x{vp[1]} {how}: double click on Cancel changes nothing", same,
                              f"before {before_snap} after {snapshot(p)}")
                        if not same:
                            landed.append(f"{label} {vp} {how} Cancel")
                    else:
                        _, nb = oracle([json.loads(seed)["bill"]])
                        ok = json.loads(stored_text(p)) == {"version": 1, "bill": nb} and p.locator("li.person").count() == 2
                        check(F, f"{label} {vp[0]}x{vp[1]} {how}: double click on Start new bill leaves the fresh new bill", ok, stored_text(p))
                        if not ok:
                            landed.append(f"{label} {vp} {how} Start")
                    s.close()
    if landed:
        observe(F, "the second click of a double click on a dialog button reached the page behind: " + "; ".join(landed))


# ------------------------------------------------------------------ F9 keyboard only
def flow_keyboard(browser):
    F = "F9 keyboard only"
    s = Session(browser, F)
    p = s.page

    def tab_to(name, limit=40, back=False):
        for n in range(1, limit + 1):
            p.keyboard.press("Shift+Tab" if back else "Tab")
            if active_name(p) == name:
                return n
        raise AssertionError(f"Tab never reached {name!r}, stopped at {active_name(p)!r}")

    rings = []

    def ring():
        rings.append(p.evaluate(RING_JS))

    check(F, "first Tab reaches New bill", tab_to("New bill") == 1)
    ring()
    tab_to("Person 1 name")
    ring()
    p.keyboard.press("Control+A")
    p.keyboard.type("Aisyah")
    tab_to("Person 2 name")
    p.keyboard.press("Control+A")
    p.keyboard.type("Ben")
    check(F, "Tab from Person 2 skips the disabled remove buttons and reaches Add person", tab_to("Add person") == 1)
    ring()
    p.keyboard.press("Enter")
    check(F, "Enter on Add person focuses the new name field", active_name(p) == "Person 3 name")
    p.keyboard.type("Chen")
    tab_to("Even")
    ring()
    p.keyboard.press("ArrowRight")
    check(F, "ArrowRight on Even selects By item and focus follows", p.locator("#mode-item").is_checked() and active_name(p) == "By item")
    ring()
    tab_to("Add item")
    for j, (name, price, people) in enumerate(S1_ITEMS, start=1):
        if j > 1:
            tab_to("Add item")
        p.keyboard.press("Enter")
        check(F, f"Enter on Add item focuses Item {j} name", active_name(p) == f"Item {j} name")
        p.keyboard.type(name)
        tab_to(f"Item {j} price in RM")
        p.keyboard.type(price)
        tab_to(f"Remove {name}")
        ring()
        for who in ["Aisyah", "Ben", "Chen"]:
            tab_to(who)
            ring()
            if who in people:
                p.keyboard.press("Space" if who == people[0] else "Enter")
        check(F, f"item {j} toggles set by Space and Enter", [toggle(p, name, w).get_attribute("aria-pressed") == ("true" if w in people else "false")
                                                             for w in ["Aisyah", "Ben", "Chen"]] == [True] * 3)
    got = panel(p)
    check(F, "keyboard-built bill: hand-typed S1 rows and check row", got["rows"] == S1_ROWS and got["foot"] == S1_FOOT, str(got["rows"]))
    verify_panel(F, "keyboard-built bill vs oracle", p)
    tab_to("Add item")
    tab_to("Service charge in percent")
    p.keyboard.press("Control+A")
    p.keyboard.type("12.5")
    tab_to("SST in percent")
    p.keyboard.press("Control+A")
    p.keyboard.type("8")
    verify_panel(F, "rates 12.5 / 8 by keyboard vs oracle", p)
    tab_to("Copy summary")
    ring()
    p.keyboard.press("Enter")
    exp = oracle([stored_bill(p)])[0][0]
    check(F, "Enter on Copy summary: status and exact clipboard text", panel(p)["statusText"] == "Summary copied" and p.evaluate("window.testClipboardText") == exp["copy"])
    shot(p, "f9-keyboard-built")
    bad = [r["name"] for r in rings if not r["visible"] or not r["ring"]]
    check(F, f"every one of {len(rings)} sampled Tab stops is :focus-visible and shows a ring", not bad, str(bad))
    s.reload()
    tab_to("New bill")
    p.keyboard.press("Enter")
    check(F, "Enter on New bill opens the dialog with Cancel focused", p.locator("dialog.dialog").evaluate("(d) => d.open") and active_name(p) == "Cancel")
    p.keyboard.press("Tab")
    check(F, "Tab goes to Start new bill", active_name(p) == "Start new bill")
    p.keyboard.press("Tab")
    check(F, "Tab wraps to Cancel", active_name(p) == "Cancel")
    p.keyboard.press("Escape")
    check(F, "Escape closes and returns focus to New bill", not p.locator("dialog.dialog").evaluate("(d) => d.open") and active_name(p) == "New bill")
    p.keyboard.press("Enter")
    p.keyboard.press("Shift+Tab")
    check(F, "Shift+Tab from Cancel wraps to Start new bill", active_name(p) == "Start new bill")
    p.keyboard.press("Enter")
    nb = oracle([json.loads(S2)["bill"]])[1]
    check(F, "Enter on Start new bill: S3, draft is the new bill, focus on New bill",
          panel(p)["message"] == MSG["subtotal"] and json.loads(stored_text(p)) == {"version": 1, "bill": nb} and active_name(p) == "New bill")
    s.reload()
    tab_to("Person 1 name")
    p.keyboard.type("Zed")
    tab_to("New bill", back=True) if False else None
    p.keyboard.press("Shift+Tab")
    p.keyboard.press("Shift+Tab") if active_name(p) != "New bill" else None
    check(F, "Shift+Tab walks back to New bill", active_name(p) == "New bill", active_name(p))
    kept = stored_text(p)
    p.keyboard.press("Enter")
    p.keyboard.press("Enter")
    p.wait_for_timeout(200)
    check(F, "Enter twice on New bill does not start a new bill", stored_text(p) == kept)
    s.close()


# ------------------------------------------------------------------ F10 360 px
def scaled_s1(factor):
    base = [("Nasi lemak ayam", 15.90, ["p1"]), ("Char kuey teow", 13.50, ["p2"]), ("Mee goreng mamak", 12.00, ["p3"]), ("Satay, 10 sticks", 18.00, ["p1", "p3"])]
    bill = json.loads(S1)["bill"]
    bill["items"] = [{"id": f"i{4 + k}", "name": n, "priceText": f"{min(price * factor, 99999.99):.2f}", "who": who} for k, (n, price, who) in enumerate(base)]
    return json.dumps({"version": 1, "bill": bill}, separators=(",", ":"))


def flow_360(browser):
    F = "F10 360 px width"
    for label, seed in [("S3", None), ("S2", S2), ("S1", S1), ("S5", S5)]:
        s = Session(browser, F, viewport=(360, 780), seed=seed)
        p = s.page
        o = p.evaluate(OVERFLOW_JS)
        cols = p.evaluate("getComputedStyle(document.querySelector('section[aria-labelledby=h-people] ul.cells')).gridTemplateColumns.split(' ').length")
        check(F, f"{label}: no horizontal overflow", o["scrollWidth"] <= o["innerWidth"] and not o["bad"], str(o))
        check(F, f"{label}: people grid has 2 columns", cols == 2, cols)
        check(F, f"{label}: panel after the Charges block", p.evaluate(
            "document.querySelector('div.tape').getBoundingClientRect().top >= document.querySelector('section[aria-labelledby=h-charges]').getBoundingClientRect().bottom - 0.5"))
        if label != "S3":
            verify_panel(F, f"{label}: panel figures at 360", p, json.loads(seed)["bill"])
        shot(p, f"f10-{label}-360")
        s.close()
    s = Session(browser, F, viewport=(360, 780), seed=S2, clipboard="reject")
    p = s.page
    check(F, "S2 Subtotal field is 160 px wide", p.locator("span.field.money:has(#subtotal)").bounding_box()["width"] == 160)
    button(p, "Copy summary").click()
    st = p.locator("p.status.status-failure")
    b = st.bounding_box()
    check(F, "failure status: 40 px tall, centred, inside 360", b["height"] == 40 and b["x"] + b["width"] <= 360 and
          st.evaluate("(e) => getComputedStyle(e).textAlign") == "center" and st.evaluate("(e) => e.scrollWidth <= e.clientWidth"), str(b))
    shot(p, "f10-failure-status-360")
    button(p, "New bill").click()
    d = p.locator("dialog.dialog").bounding_box()
    check(F, "dialog 328 px wide, dialog-text 48 px, no overflow", d["width"] == 328 and p.locator("p.dialog-text").bounding_box()["height"] == 48 and
          p.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), str(d))
    shot(p, "f10-dialog-360")
    s.close()
    # Outside qa.md (R35 names S1, S2, S3, S5 only): where does the by-item table first overflow as the amounts grow?
    for width in (360, 390):
        first = None
        for factor in [1, 2, 5, 8, 10, 12, 15, 20, 30, 50, 100, 300, 1000, 1600]:
            seed = scaled_s1(factor)
            s = Session(browser, F + " amounts", viewport=(width, 780), seed=seed)
            p = s.page
            o = p.evaluate(OVERFLOW_JS)
            verify_panel(F, f"{width}px amounts x{factor}: panel vs oracle", p, json.loads(seed)["bill"])
            if o["scrollWidth"] > o["innerWidth"] and first is None:
                first = (factor, panel(p)["foot"][0], o["scrollWidth"])
                shot(p, f"f10-amounts-overflow-{width}")
            s.close(record=False)
        observe(F, f"[outside qa.md] {width} px, S1 bill with prices scaled: first horizontal overflow at (factor, check row, scrollWidth) = {first}")
    people = [{"id": f"p{i}", "name": "W" * 20} for i in range(1, 13)]
    items = [{"id": f"i{12 + k}", "name": "W" * 40, "priceText": "99999.99", "who": [q["id"] for q in people]} for k in range(1, 51)]
    stress = {"version": 1, "bill": {"mode": "item", "people": people, "subtotalText": "", "items": items, "serviceText": "30", "sstText": "20", "nextId": 63}}
    s = Session(browser, F + " stress", viewport=(360, 780), seed=json.dumps(stress, separators=(",", ":")))
    p = s.page
    o = p.evaluate(OVERFLOW_JS)
    verify_panel(F, "stress (12 people x 20 W, 50 items x 40 W, prices 99999.99) panel vs oracle", p, stress["bill"])
    if o["scrollWidth"] > o["innerWidth"]:
        observe(F, f"[outside qa.md] stress bill at 360 px overflows horizontally: {o}")
    shot(p, "f10-stress-360")
    s.close(record=False)
    s = Session(browser, F + " 320", viewport=(320, 640), seed=S1)
    o = s.page.evaluate(OVERFLOW_JS)
    if o["scrollWidth"] > o["innerWidth"] or o["bad"]:
        observe(F, f"[outside qa.md, below the 360 px floor] 320 x 640, S1: {o}")
    s.close(record=False)


# ------------------------------------------------------------------ F11 RD-3
def flow_rd3(browser):
    F = "F11 RD-3 press below an invalid field"
    record = """() => { window.testClicks = []; document.addEventListener('click', (e) => { const t = e.target;
      window.testClicks.push(t.id || t.getAttribute('aria-label') || t.tagName.toLowerCase() + ':' + (t.textContent || '').trim().slice(0, 20)); }, true); }"""
    cases = [
        ("subtotal 0 -> Service charge input", None, lambda q: q.locator("#subtotal"), "0", lambda q: q.locator("#rate-service"), "subtotal-error"),
        ("price 13.505 -> Aisyah toggle", S1, lambda q: item_price(q, 2), "13.505", lambda q: toggle(q, "Char kuey teow", "Aisyah"), "price-error-i5"),
        ("price 13.505 -> Remove (item 3)", S1, lambda q: item_price(q, 2), "13.505", lambda q: button(q, "Remove Mee goreng mamak"), "price-error-i5"),
        ("price 13.505 -> Add item", S1, lambda q: item_price(q, 2), "13.505", lambda q: button(q, "Add item"), "price-error-i5"),
        ("service 31 -> hint", None, lambda q: q.locator("#rate-service"), "31", lambda q: q.locator("#charges-hint"), "rate-service-error"),
        ("SST 25 -> hint", None, lambda q: q.locator("#rate-sst"), "25", lambda q: q.locator("#charges-hint"), "rate-sst-error"),
    ]
    for how in ["mouse", "touch"]:
        for label, seed, field_of, bad, target_of, err_id in cases:
            s = Session(browser, F, touch=how == "touch", seed=seed)
            p = s.page
            replace(p, field_of(p), bad)
            check(F, f"{how}: {label}: no error while focused", p.locator(f"#{err_id}").count() == 0)
            p.evaluate(record)
            tgt = target_of(p)
            before_pressed = tgt.get_attribute("aria-pressed") if "toggle" in label else None
            before_items = p.locator("li.item").count()
            x, y = centre(tgt)
            if how == "touch":
                p.touchscreen.tap(x, y)
            else:
                p.mouse.click(x, y)
            p.wait_for_timeout(150)
            clicks = p.evaluate("window.testClicks")
            check(F, f"{how}: {label}: exactly one click reached the control it started on", len(clicks) == 1, str(clicks))
            check(F, f"{how}: {label}: error shows after the press", p.locator(f"p.error#{err_id}").count() == 1)
            if "toggle" in label:
                check(F, f"{how}: {label}: toggle flipped once", tgt.get_attribute("aria-pressed") != before_pressed)
            if "Remove" in label:
                check(F, f"{how}: {label}: the item was removed once", p.locator("li.item").count() == before_items - 1)
            if "Add item" in label:
                check(F, f"{how}: {label}: one item added", p.locator("li.item").count() == before_items + 1)
            s.close()


# ------------------------------------------------------------------ F12 injection
def flow_injection(browser):
    F = "F12 text stays text"
    s = Session(browser, F, seed=S1)
    p = s.page
    dialogs = []
    p.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))
    svgs = p.locator("body svg").count()
    replace(p, person(p, 1), "<svg onload=f()>")
    replace(p, item_name(p, 1), "<img src=x onerror=alert(1)>")
    replace(p, item_name(p, 2), '"><script>alert(2)</script>')
    check(F, "names held exactly", person(p, 1).input_value() == "<svg onload=f()>" and item_name(p, 1).input_value() == "<img src=x onerror=alert(1)>")
    check(F, "toggles, shares row, remove names show literal text",
          p.get_by_role("button", name="<svg onload=f()>", exact=True).count() == 4 and
          p.locator("table.shares tbody tr").first.locator("th").inner_text() == "<svg onload=f()>" and
          p.get_by_role("button", name="Remove <svg onload=f()>", exact=True).count() == 1 and
          p.get_by_role("button", name="Remove <img src=x onerror=alert(1)>", exact=True).count() == 1 and
          p.get_by_role("group", name="Who had <img src=x onerror=alert(1)>", exact=True).count() == 1)
    check(F, "no img/script created, no handler attributes, svg count unchanged",
          p.locator("body img, body script").count() == 0 and p.locator("[onload],[onerror]").count() == 0 and p.locator("body svg").count() == svgs)
    button(p, "Copy summary").click()
    check(F, "clipboard line 3 is literal", p.evaluate("window.testClipboardText").split("\n")[2] == "<svg onload=f()> RM 29.04")
    s.reload()
    check(F, "after reload the names are still literal and no alert ran", person(p, 1).input_value() == "<svg onload=f()>" and dialogs == [])
    s.close()


# ------------------------------------------------------------------ F13 differential run against split-core
NAMES = ["Aisyah", "Ben", "Chen", "", "  ", "Ben", "Mei Ling", "\u4f60\u597d", "A" * 20, "<b>x</b>", "Zoe", "\U0001F1F2\U0001F1FE", "Devi", "Farid", " Indra "]
ITEM_NAMES = ["Nasi lemak", "", "Teh tarik", "Satay, 10 sticks", "B" * 40, "<i>", "Roti canai", "  "]
SUBS = ["", "0", "1", "100", "100.00", "0.01", "99999.99", "100000", "12.345", "abc", "1,000", " 5 ", "5.5", ".5", "5.", "-3", "1e3"]
RATES = ["", "0", "10", "6", "30", "31", "20", "20.01", "7.5", "0.5", "abc", "-1", "5.555", "12.25", "0.01", " 8 "]


def gen_bill(rng):
    n = rng.randint(2, 12)
    people = [{"id": f"p{i + 1}", "name": rng.choice(NAMES)} for i in range(n)]
    next_id = n + 1
    items = []
    for _ in range(rng.choice([0, 1, 2, 3, 4, 6, 10, 20])):
        iid = f"i{next_id}"
        next_id += 1
        price = f"{rng.randint(1, 9999999) / 100:.2f}" if rng.random() < 0.85 else rng.choice(SUBS)
        items.append({"id": iid, "name": rng.choice(ITEM_NAMES), "priceText": price, "who": [q["id"] for q in people if rng.random() < 0.45]})
    sub = f"{rng.randint(1, 9999999) / 100:.2f}" if rng.random() < 0.8 else rng.choice(SUBS)
    return {"mode": rng.choice(["even", "item"]), "people": people, "subtotalText": sub, "items": items,
            "serviceText": rng.choice(RATES) if rng.random() < 0.6 else "10", "sstText": rng.choice(RATES) if rng.random() < 0.6 else "6", "nextId": next_id}


def flow_fuzz(browser, seed_value=20261009, count=90):
    F = "F13 differential run against split-core"
    rng = random.Random(seed_value)
    bills = [gen_bill(rng) for _ in range(count)]
    # Make sure the interesting kinds are present: clean valid bills in both modes.
    for k in range(0, count, 3):
        b = bills[k]
        b["serviceText"], b["sstText"] = "10", "6"
        if b["mode"] == "even":
            b["subtotalText"] = f"{rng.randint(100, 9999999) / 100:.2f}"
        else:
            for it in b["items"]:
                it["priceText"] = f"{rng.randint(1, 999999) / 100:.2f}"
                it["who"] = it["who"] or [b["people"][0]["id"]]
    expected, _ = oracle(bills)
    s = Session(browser, F)
    p = s.page
    kinds = {}
    failures = []
    for k, (bill, exp) in enumerate(zip(bills, expected)):
        text = json.dumps({"version": 1, "bill": bill}, separators=(",", ":"), ensure_ascii=False)
        p.evaluate("(t) => localStorage.setItem('split.draft', t)", text)
        s.reload()
        kinds[exp["kind"]] = kinds.get(exp["kind"], 0) + 1
        diff = panel_diff(exp, panel(p))
        if p.locator("div.note").count():
            diff.append("the app rejected a bill the decoder should accept")
        snap = snapshot(p)
        if snap["people"] != [q["name"] for q in bill["people"]] or snap["mode"] != bill["mode"] or snap["rates"] != [bill["serviceText"], bill["sstText"]]:
            diff.append(f"restored fields differ: {snap}")
        want_err = set()
        if exp["invalid"]["service"]:
            want_err.add("rate-service-error")
        if exp["invalid"]["sst"]:
            want_err.add("rate-sst-error")
        if bill["mode"] == "even" and exp["invalid"]["subtotal"]:
            want_err.add("subtotal-error")
        if bill["mode"] == "item":
            want_err |= {f"price-error-{iid}" for iid, bad in exp["invalid"]["prices"].items() if bad}
        got_err = {e[0] for e in errors_now(p)["errors"]}
        if got_err != want_err:
            diff.append(f"errors shown {sorted(got_err)} want {sorted(want_err)}")
        if diff:
            failures.append((k, diff, text[:300]))
    check(F, f"{count} random bills (seed {seed_value}, kinds {kinds}): panel, restored fields and displayed errors equal split-core", not failures,
          json.dumps(failures[:3], ensure_ascii=True)[:1500])
    s.close()


# ------------------------------------------------------------------ F14 storage unavailable
def flow_storage(browser):
    F = "F14 storage unavailable"
    breakers = {
        "reading window.localStorage throws": "Object.defineProperty(window, 'localStorage', { get() { throw new DOMException('blocked', 'SecurityError'); } });",
        "getItem throws": "Storage.prototype.getItem = function () { throw new Error('read failed'); };",
        "setItem throws": "Storage.prototype.setItem = function () { throw new DOMException('full', 'QuotaExceededError'); };",
    }
    for label, script in breakers.items():
        s = Session(browser, F, init_scripts=[script])
        p = s.page
        replace(p, p.locator("#subtotal"), "100.00")
        button(p, "Add person").click()
        got = panel(p)
        check(F, f"{label}: total RM 116.60 with three shares, no message", got["summary"][3][1] == "RM 116.60" and len(got["rows"]) == 3 and
              p.locator("div.note, p.error").count() == 0, str(got["summary"]))
        s.close()


# ------------------------------------------------------------------ main
def main():
    global BASE
    sys.stdout.reconfigure(encoding="utf-8")
    port = free_port()
    server = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=ROOT,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    BASE = f"http://127.0.0.1:{port}"
    print(f"SERVER STARTED pid {server.pid} port {port}", flush=True)
    only = set(sys.argv[1:])
    flows = [("F1", flow_even), ("F2", flow_items), ("F3", flow_charges), ("F4", flow_copy), ("F5", flow_restore), ("F6", flow_unreadable),
             ("F7", flow_new_bill), ("F8", flow_double_click), ("F9", flow_keyboard), ("F10", flow_360), ("F11", flow_rd3),
             ("F12", flow_injection), ("F13", flow_fuzz), ("F14", flow_storage)]
    version = None
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(BASE + "/", timeout=1).close()
                break
            except OSError:
                time.sleep(0.1)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            version = browser.version
            print("CHROMIUM", version, flush=True)
            for name, fn in flows:
                if only and name not in only:
                    continue
                try:
                    fn(browser)
                except SystemExit:
                    raise
                except Exception as exc:  # a crashed flow is a failure of that flow
                    check(name, "flow ran to the end", False, "".join(traceback.format_exception_only(type(exc), exc)).strip()[:600])
                    print(traceback.format_exc()[-1500:], flush=True)
            browser.close()
    finally:
        server.kill()
        try:
            server.wait(10)
        except subprocess.TimeoutExpired:
            print("server did not exit in 10 s", flush=True)
        with socket.socket() as probe:
            try:
                probe.bind(("127.0.0.1", port))
                freed = True
            except OSError:
                freed = False
        print(f"SERVER STOPPED pid {server.pid} port {port} exited {server.poll() is not None} port free again {freed}", flush=True)
    passed = sum(1 for r in RESULTS if r["ok"])
    failed = [r for r in RESULTS if not r["ok"]]
    summary = {"chromium": version, "passed": passed, "failed": len(failed), "failures": failed, "observations": OBS, "results": RESULTS}
    suffix = "-".join(sorted(only)) if only else "all"
    (OUT / f"driver-results-{suffix}.json").write_text(json.dumps(summary, indent=1, ensure_ascii=True), encoding="utf-8")
    per_flow = {}
    for r in RESULTS:
        slot = per_flow.setdefault(r["flow"], [0, 0])
        slot[0 if r["ok"] else 1] += 1
    print("PER FLOW (pass, fail):", json.dumps(per_flow), flush=True)
    print(f"TOTAL passed {passed} failed {len(failed)}", flush=True)


if __name__ == "__main__":
    main()
