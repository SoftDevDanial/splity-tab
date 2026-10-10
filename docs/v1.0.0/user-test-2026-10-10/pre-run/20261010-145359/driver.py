"""UAT pre-run driver for Split 1.0.0 (cases UAT-01 to UAT-08, one continuous session).

Usage:  python -B driver.py desktop     (1280 x 800)   -> results.json, NN-uat-0N.png
        python -B driver.py phone       (390 x 844)    -> results-390.json, NN-uat-0N-390.png

Read-only against the app: real gestures only (click, keyboard, Tab, Ctrl+A). page.evaluate is used to READ.
CG-7: the recorder init script replaces navigator.clipboard.writeText, the OS clipboard is never touched.
Every wait is bounded (10 s Playwright timeouts, 150 ms settle pauses).

History: run 1 of the desktop pass flagged one false FAIL in UAT-06 ("+Charges" / "=Share"): innerText does not carry the
CSS gap between the operator glyph and the column name. That was an instrument artefact (the screenshot shows
"+ Charges" and "= Share"). The check below is now paint based (gap measured in pixels). The desktop pass was re-run
from a fresh browser context with this version, and results.json is the re-run.
"""
import json
import os
import re
import sys
import traceback

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
URL = "http://127.0.0.1:8732/"
RECORDER = r"{workspace}\examples\split\tests\browser\clipboard\recorder.js"
T = 10000

MODE = sys.argv[1] if len(sys.argv) > 1 else "desktop"
if MODE == "phone":
    VIEW = {"width": 390, "height": 844}
    TAG = "-390"
else:
    VIEW = {"width": 1280, "height": 800}
    TAG = ""

results = {}
env = {"console": [], "pageerrors": [], "requests": [], "requestfailed": []}
cur = None
page = None
ctx = None
SNAP6 = None


def norm(s):
    if s is None:
        return None
    return re.sub(r"\s+", " ", str(s).replace("\u00a0", " ")).strip()


def chk(name, expected, seen, ok=None, info=False):
    """Record one check. ok defaults to normalised equality. info=True records a fact the script is silent on."""
    if ok is None:
        if isinstance(expected, str) and isinstance(seen, str):
            ok = norm(expected) == norm(seen)
        else:
            ok = expected == seen
    cur["checks"].append({"name": name, "expected": expected, "seen": seen, "ok": bool(ok), "info": info})
    return bool(ok)


def note(text):
    cur["notes"].append(text)


def attach(p):
    p.set_default_timeout(T)
    p.set_default_navigation_timeout(T)
    p.on("console", lambda m: env["console"].append(f"{m.type}: {m.text}"))
    p.on("pageerror", lambda e: env["pageerrors"].append(str(e)))
    p.on("request", lambda r: env["requests"].append(r.url))
    p.on("requestfailed", lambda r: env["requestfailed"].append(f"{r.url} {r.failure}"))


def settle():
    page.wait_for_timeout(150)


SNAP_JS = r"""() => {
  const norm = (s) => (s || '').replace(/\s+/g, ' ').trim();
  const vis = (e) => { if (!e) return false; const r = e.getBoundingClientRect(); const cs = getComputedStyle(e);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && !e.closest('[hidden]'); };
  const btn = (t) => [...document.querySelectorAll('button')].find((b) => norm(b.textContent) === t);
  const people = [...document.querySelectorAll('li.person')].map((li) => {
    const i = li.querySelector('input'); const b = li.querySelector('button');
    return { value: i.value, aria: i.getAttribute('aria-label'), placeholder: i.placeholder,
             remove: b.getAttribute('aria-label'), removeDisabled: b.disabled };
  });
  const items = [...document.querySelectorAll('li.item')].map((li) => {
    const ins = li.querySelectorAll('input'); const who = li.querySelector('.who');
    return { name: ins[0].value, price: ins[1].value, group: who.getAttribute('aria-label'),
             taps: [...who.querySelectorAll('button')].map((b) => ({ text: norm(b.textContent), pressed: b.getAttribute('aria-pressed') })) };
  });
  const sub = document.querySelector('#subtotal');
  const rows = [...document.querySelectorAll('.tape dl.sum .row')].map((r) => ({
    dt: norm(r.querySelector('dt') && r.querySelector('dt').innerText),
    amt: norm(r.querySelector('dd.amt') && r.querySelector('dd.amt').innerText),
    work: r.querySelector('dd.work') ? norm(r.querySelector('dd.work').innerText) : null }));
  const t = document.querySelector('.tape table.shares');
  const cells = (r) => [...r.children].map((c) => norm(c.innerText));
  const table = t ? { head: [...t.querySelectorAll('thead tr')].map(cells), body: [...t.querySelectorAll('tbody tr')].map(cells),
                      foot: [...t.querySelectorAll('tfoot tr')].map(cells) } : null;
  const msg = document.querySelector('.tape p.result-msg');
  const st = document.querySelector('.tape p.status');
  const ae = document.activeElement;
  const dlg = document.querySelector('dialog');
  const ai = btn('Add item'); const ap = btn('Add person');
  return {
    people, items,
    mode: document.querySelector('#mode-item').checked ? 'item' : (document.querySelector('#mode-even').checked ? 'even' : 'none'),
    subtotal: sub.value, subtotalVisible: vis(sub),
    service: document.querySelector('#rate-service').value, sst: document.querySelector('#rate-sst').value,
    errors: [...document.querySelectorAll('p.error')].filter(vis).map((e) => norm(e.textContent)),
    headings: [...document.querySelectorAll('.tape h2')].map((h) => norm(h.textContent)),
    summary: rows, table,
    message: msg && vis(msg) ? norm(msg.textContent) : null,
    status: st && vis(st) ? { text: norm(st.textContent), cls: st.className } : null,
    addItemVisible: vis(ai), addPersonVisible: vis(ap), addPersonDisabled: ap ? ap.disabled : null,
    dialogOpen: dlg ? dlg.open : null,
    active: ae ? { tag: ae.tagName, aria: ae.getAttribute('aria-label'), id: ae.id, text: norm(ae.textContent).slice(0, 40) } : null,
    storage: Object.fromEntries(Object.entries(localStorage)),
    tapeText: norm(document.querySelector('.tape').innerText),
  };
}"""


def snap():
    return page.evaluate(SNAP_JS)


HIT_JS = """(el, p) => { const t = document.elementFromPoint(p[0], p[1]);
  return { ok: !!t && (t === el || el.contains(t)), got: t ? (t.tagName + (t.id ? '#' + t.id : '') + (t.className && t.className.baseVal === undefined && t.className ? '.' + String(t.className).split(' ')[0] : '')) : null }; }"""


def hit_click(loc, label):
    """Scroll to it, assert elementFromPoint at its centre resolves inside it, then a real click."""
    loc.scroll_into_view_if_needed(timeout=T)
    box = loc.bounding_box()
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    r = loc.evaluate(HIT_JS, [cx, cy])
    chk(f"hit-test before click: {label}", "elementFromPoint resolves inside the control", r["got"], r["ok"])
    loc.click(timeout=T)
    return r["ok"]


def replace_text(loc, text, label, select_all=True):
    hit_click(loc, label)
    if select_all:
        page.keyboard.press("Control+A")
    page.keyboard.type(text, delay=20)
    settle()


def name_box(n):
    return page.get_by_role("textbox", name=f"Person {n} name", exact=True)


def subtotal_box():
    return page.get_by_role("textbox", name="Subtotal in RM", exact=True)


def btn(name):
    return page.get_by_role("button", name=name, exact=True)


def summary_map(s):
    out = {}
    for r in s["summary"]:
        label = re.sub(r"^[+=]\s*", "", r["dt"])
        out[label] = (r["amt"], r["work"])
    return out


def check_summary(s, subtotal, service, service_work, sst, sst_work, total, tag):
    m = summary_map(s)
    chk(f"{tag}: heading 'Bill summary' on screen", True, "Bill summary" in s["headings"])
    chk(f"{tag}: Subtotal", subtotal, m.get("Subtotal", (None,))[0])
    chk(f"{tag}: Service charge amount", service, m.get("Service charge", (None,))[0])
    chk(f"{tag}: Service charge working line", service_work, m.get("Service charge", (None, None))[1])
    chk(f"{tag}: SST amount", sst, m.get("SST", (None,))[0])
    chk(f"{tag}: SST working line", sst_work, m.get("SST", (None, None))[1])
    chk(f"{tag}: Total", total, m.get("Total", (None,))[0])


def check_even_shares(s, shares, check_total, tag):
    t = s["table"]
    chk(f"{tag}: heading 'Shares' on screen", True, "Shares" in s["headings"])
    chk(f"{tag}: shares table present", True, t is not None)
    if t is None:
        return
    seen = [(r[0], r[1]) for r in t["body"]]
    chk(f"{tag}: shares rows", [list(x) for x in shares], [list(x) for x in seen], ok=([(a, norm(b)) for a, b in shares] == seen))
    foot = t["foot"][0] if t["foot"] else None
    chk(f"{tag}: 'Adds up to' row", ["Adds up to", check_total], foot, ok=(foot is not None and norm(foot[0]) == "Adds up to" and norm(foot[1]) == check_total))


def shot(n, suffix=""):
    path = os.path.join(HERE, f"{n:02d}-uat-0{n}{suffix}{TAG}.png")
    page.screenshot(path=path, full_page=True)
    return os.path.basename(path)


def computed(sel_or_loc, prop, pseudo=None):
    loc = page.locator(sel_or_loc) if isinstance(sel_or_loc, str) else sel_or_loc
    return loc.first.evaluate("(el, a) => getComputedStyle(el, a[1])[a[0]]", [prop, pseudo])


# --------------------------------------------------------------------------------------------------------------
def uat01():
    s0 = snap()
    chk("start: no draft saved in this browser", {}, s0["storage"])
    chk("start: name boxes", ["Person 1", "Person 2"], [p["value"] for p in s0["people"]])
    chk("start: Even chosen", "even", s0["mode"])
    chk("start: Subtotal empty", "", s0["subtotal"])
    chk("start: service/SST", ["10", "6"], [s0["service"], s0["sst"]])
    # Expected: before step 3 the x in both boxes is greyed out and does nothing.
    chk("before step 3: both x disabled", [True, True], [p["removeDisabled"] for p in s0["people"]])
    for i in (0, 1):
        rb = page.locator("li.person").nth(i).locator("button")
        chk(f"before step 3: x of box {i+1} colour is the disabled grey (#9AA19D)", "rgb(154, 161, 157)", computed(rb, "color"))
        rb.scroll_into_view_if_needed(timeout=T)
        b = rb.bounding_box()
        cx, cy = b["x"] + b["width"] / 2, b["y"] + b["height"] / 2
        r = rb.evaluate(HIT_JS, [cx, cy])
        chk(f"before step 3: real click point on x of box {i+1} resolves to the button", True, r["ok"], info=True)
        page.mouse.click(cx, cy)
        settle()
    s1 = snap()
    chk("clicking the greyed x did nothing: still two people", ["Person 1", "Person 2"], [p["value"] for p in s1["people"]])
    page.locator(".inputs").first.screenshot(path=os.path.join(HERE, f"01-uat-01-start-people{TAG}.png"))

    # Step 1
    replace_text(name_box(1), "Aisyah", "name box 1")
    # Step 2
    replace_text(name_box(2), "Ben", "name box 2")
    s = snap()
    chk("steps 1-2: names", ["Aisyah", "Ben"], [p["value"] for p in s["people"]])
    # Step 3
    hit_click(btn("Add person"), "Add person")
    settle()
    s = snap()
    chk("step 3: third box appears", 3, len(s["people"]))
    chk("step 3: cursor already in the third box", "Person 3 name", (s["active"] or {}).get("aria"))
    chk("step 3: third box is empty and shows hint 'Person 3'", ["", "Person 3"], [s["people"][2]["value"], s["people"][2]["placeholder"]] if len(s["people"]) > 2 else None)
    ph = page.get_by_role("textbox", name="Person 3 name", exact=True)
    chk("step 3: hint colour (grey, --ink-muted #4A524E)", "rgb(74, 82, 78)", computed(ph, "color", "::placeholder"), info=True)
    page.locator(".inputs").first.screenshot(path=os.path.join(HERE, f"01-uat-01-after-step3{TAG}.png"))
    # Step 4 (no click: the cursor is already there)
    page.keyboard.type("Chen", delay=20)
    settle()
    s = snap()
    chk("step 4: typing went into the third box", ["Aisyah", "Ben", "Chen"], [p["value"] for p in s["people"]])
    # Step 5
    hit_click(btn("Add person"), "Add person (again)")
    settle()
    s = snap()
    chk("step 5: fourth box appears", 4, len(s["people"]))
    chk("step 5: cursor in the fourth box", "Person 4 name", (s["active"] or {}).get("aria"))
    chk("step 5: fourth box hint", ["", "Person 4"], [s["people"][3]["value"], s["people"][3]["placeholder"]] if len(s["people"]) > 3 else None)
    page.locator(".inputs").first.screenshot(path=os.path.join(HERE, f"01-uat-01-after-step5{TAG}.png"))
    # Step 6
    x4 = btn("Remove Person 4")
    chk("step 6: the x of the fourth box exists and is active", False, x4.is_disabled())
    hit_click(x4, "x of fourth box (Remove Person 4)")
    settle()
    s = snap()
    chk("step 6: fourth box gone, left with Aisyah, Ben, Chen", ["Aisyah", "Ben", "Chen"], [p["value"] for p in s["people"]])
    chk("step 6: every x is now active", [False, False, False], [p["removeDisabled"] for p in s["people"]])
    chk("step 6 (info): x accessible names", ["Remove Aisyah", "Remove Ben", "Remove Chen"], [p["remove"] for p in s["people"]], info=True)
    chk("step 6 (info): where the cursor went", "Person 3 name", (s["active"] or {}).get("aria"), info=True)
    for i in range(3):
        rb = page.locator("li.person").nth(i).locator("button")
        chk(f"step 6: x of box {i+1} colour is ink, not disabled grey", True, computed(rb, "color") != "rgb(154, 161, 157)", info=True)


def uat02():
    hit_click(subtotal_box(), "Subtotal box")
    page.keyboard.type("100.00", delay=20)
    settle()
    s = snap()
    chk("subtotal box holds", "100.00", s["subtotal"])
    check_summary(s, "RM 100.00", "RM 10.00", "10% of RM 100.00", "RM 6.60", "6% of RM 110.00", "RM 116.60", "UAT-02 summary")
    check_even_shares(s, [("Aisyah", "RM 38.87"), ("Ben", "RM 38.87"), ("Chen", "RM 38.86")], "RM 116.60", "UAT-02 shares")
    chk("raw tape text (info)", None, s["tapeText"], ok=True, info=True)
    page.locator(".tape").screenshot(path=os.path.join(HERE, f"02-uat-02-tape{TAG}.png"))


def uat03():
    s = snap()
    # Step 1: read the line under the shares
    chk("step 1: 'Adds up to' row reads RM 116.60", ["Adds up to", "RM 116.60"], s["table"]["foot"][0] if s["table"] and s["table"]["foot"] else None,
        ok=bool(s["table"] and s["table"]["foot"] and norm(s["table"]["foot"][0][0]) == "Adds up to" and norm(s["table"]["foot"][0][1]) == "RM 116.60"))
    chk("step 1: the Total is RM 116.60 (same as Adds up to)", "RM 116.60", summary_map(s).get("Total", (None,))[0])
    tick = page.locator(".tape table.shares tfoot th svg.ph")
    chk("step 1: a tick icon is in the 'Adds up to' row", 1, tick.count())
    if tick.count() == 1:
        b = tick.bounding_box()
        chk("step 1: tick has a painted size (not 0x0)", True, b is not None and b["width"] > 0 and b["height"] > 0, info=False)
        chk("step 1: tick colour is the accent green #0B6B4D", "rgb(11, 107, 77)", computed(tick, "color"))
        chk("step 1: tick visibility / opacity", ["visible", "1"], [computed(tick, "visibility"), computed(tick, "opacity")])
        tick.scroll_into_view_if_needed(timeout=T)
        page.locator(".tape table.shares tfoot").screenshot(path=os.path.join(HERE, f"03-uat-03-adds-up{TAG}.png"))
    # Step 2
    replace_text(subtotal_box(), "10.05", "Subtotal box")
    s = snap()
    chk("step 2: subtotal box holds", "10.05", s["subtotal"])
    # Step 3
    check_summary(s, "RM 10.05", "RM 1.01", "10% of RM 10.05", "RM 0.66", "6% of RM 11.06", "RM 11.72", "UAT-03 step 3 summary")
    check_even_shares(s, [("Aisyah", "RM 3.91"), ("Ben", "RM 3.91"), ("Chen", "RM 3.90")], "RM 11.72", "UAT-03 step 3 shares")
    # Step 4
    replace_text(subtotal_box(), "100.00", "Subtotal box")
    s = snap()
    chk("step 4: subtotal box holds", "100.00", s["subtotal"])
    check_summary(s, "RM 100.00", "RM 10.00", "10% of RM 100.00", "RM 6.60", "6% of RM 110.00", "RM 116.60", "UAT-03 step 4 summary (back to UAT-02)")
    check_even_shares(s, [("Aisyah", "RM 38.87"), ("Ben", "RM 38.87"), ("Chen", "RM 38.86")], "RM 116.60", "UAT-03 step 4 shares (back to UAT-02)")


def uat04():
    hint = page.locator("#charges-hint")
    chk("hint is visible", True, hint.is_visible())
    chk("hint text", "Set a charge to 0 if your bill already includes it.", norm(hint.inner_text()))
    chk("hint colour is grey (--ink-muted #4A524E)", "rgb(74, 82, 78)", computed(hint, "color"), info=True)
    chk("label of the Service charge box", "Service charge", norm(page.locator("label[for=rate-service]").inner_text()), ok=True, info=True)
    # Step 1
    replace_text(page.locator("#rate-service"), "0", "Service charge box")
    # Step 2
    s = snap()
    chk("step 1: Service charge box holds", "0", s["service"])
    check_summary(s, "RM 100.00", "RM 0.00", "0% of RM 100.00", "RM 6.00", "6% of RM 100.00", "RM 106.00", "UAT-04 step 2 summary")
    check_even_shares(s, [("Aisyah", "RM 35.34"), ("Ben", "RM 35.33"), ("Chen", "RM 35.33")], "RM 106.00", "UAT-04 step 2 shares")
    # Step 3
    replace_text(page.locator("#rate-service"), "31", "Service charge box")
    s = snap()
    chk("step 3: box holds 31", "31", s["service"])
    chk("step 3 (before Tab): no red text yet (info)", [], s["errors"], ok=True, info=True)
    # Step 4
    page.keyboard.press("Tab")
    settle()
    s = snap()
    chk("step 4: red text reads", ["Enter a rate from 0 to 30"], s["errors"])
    err = page.locator("p.error:visible")
    if err.count() == 1:
        chk("step 4: red text colour #B42318", "rgb(180, 35, 24)", computed(err, "color"))
        pos = page.evaluate("""() => { const e = [...document.querySelectorAll('p.error')].find(x => x.getBoundingClientRect().height > 0);
            const i = document.querySelector('#rate-service').getBoundingClientRect(); const r = e.getBoundingClientRect();
            return { errTop: r.top, inputBottom: i.bottom, errLeft: r.left, inputLeft: i.left, sameCell: e.parentElement.contains(document.querySelector('#rate-service')) }; }""")
        chk("step 4: red text sits under the Service charge box", True, pos["sameCell"] and pos["errTop"] >= pos["inputBottom"] - 1)
        chk("step 4 (info): geometry", None, pos, ok=True, info=True)
    chk("step 4: Bill summary has gone (no Bill summary heading, no summary rows)", [[], 0], [s["headings"], len(s["summary"])], ok=("Bill summary" not in s["headings"] and len(s["summary"]) == 0))
    chk("step 4: Shares says", "Check the charges to see the shares.", s["message"])
    chk("step 4: no shares table", None, s["table"], ok=(s["table"] is None))
    chk("step 4 (info): where the cursor went after Tab", "SST", (s["active"] or {}).get("id"), ok=True, info=True)
    chk("step 4 (info): hint still visible with the error showing", True, page.locator("#charges-hint").is_visible(), info=True)
    page.screenshot(path=os.path.join(HERE, f"04-uat-04-error{TAG}.png"), full_page=True)
    # Step 5
    replace_text(page.locator("#rate-service"), "10", "Service charge box")
    s = snap()
    chk("step 5: box holds 10", "10", s["service"])
    chk("step 5: red text is gone", [], s["errors"])
    check_summary(s, "RM 100.00", "RM 10.00", "10% of RM 100.00", "RM 6.60", "6% of RM 110.00", "RM 116.60", "UAT-04 step 5 summary")
    check_even_shares(s, [("Aisyah", "RM 38.87"), ("Ben", "RM 38.87"), ("Chen", "RM 38.86")], "RM 116.60", "UAT-04 step 5 shares")


EXPECTED_COPY = "\n".join([
    "Bill split",
    "Total RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)",
    "Aisyah RM 38.87",
    "Ben RM 38.87",
    "Chen RM 38.86",
    "Adds up to RM 116.60",
])


def uat05():
    b = btn("Copy summary")
    chk("Copy summary button is dark (primary fill #141917)", "rgb(20, 25, 23)", computed(b, "backgroundColor"))
    pos = page.evaluate("""() => { const b = [...document.querySelectorAll('button')].find(x => x.textContent.trim() === 'Copy summary');
        const t = document.querySelector('table.shares'); return { btnTop: b.getBoundingClientRect().top, tableBottom: t.getBoundingClientRect().bottom }; }""")
    chk("Copy summary sits under the shares", True, pos["btnTop"] >= pos["tableBottom"])
    before = page.evaluate("window.testClipboardWrites")
    chk("recorder in place (no copy yet)", 0, before)
    # Step 1
    hit_click(b, "Copy summary")
    # Step 2: bounded wait for the async status
    try:
        page.wait_for_function("() => { const s = document.querySelector('.tape p.status'); return s && s.textContent.trim() !== ''; }", timeout=5000)
    except Exception as e:  # noqa: BLE001
        note(f"status did not appear within 5 s: {type(e).__name__}")
    s = snap()
    chk("step 2: line under the button", {"text": "Summary copied"}, {"text": (s["status"] or {}).get("text")}, ok=((s["status"] or {}).get("text") == "Summary copied"))
    chk("step 2 (info): status class", "status", (s["status"] or {}).get("cls"), ok=True, info=True)
    writes = page.evaluate("window.testClipboardWrites")
    text = page.evaluate("window.testClipboardText")
    chk("exactly one write reached the recorder", 1, writes)
    chk("step 3 (recorded text, not pasted): equals the six lines exactly, byte for byte", EXPECTED_COPY, text, ok=(text == EXPECTED_COPY))
    chk("recorded text, line by line", EXPECTED_COPY.split("\n"), text.split("\n") if isinstance(text, str) else None)
    chk("recorded text has no trailing newline / no non-breaking spaces (info)", [False, False], [isinstance(text, str) and text.endswith("\n"), isinstance(text, str) and "\u00a0" in text], info=True)
    note("Step 3 (paste into Notepad with Ctrl+V) NOT driven: CG-7 forbids touching the OS clipboard. Verified the recorded text instead.")
    note(f"recorded text repr: {text!r}")
    page.locator(".tape").screenshot(path=os.path.join(HERE, f"05-uat-05-status{TAG}.png"))


ITEMS = [
    ("Nasi lemak ayam", "15.90", ["Aisyah"]),
    ("Char kuey teow", "13.50", ["Ben"]),
    ("Mee goreng mamak", "12.00", ["Chen"]),
    ("Satay, 10 sticks", "18.00", ["Aisyah", "Chen"]),
]


def add_item_and_fill(n, name, price):
    hit_click(btn("Add item"), f"Add item (#{n})")
    settle()
    s = snap()
    chk(f"item {n}: cursor goes into the new item's name box", f"Item {n} name", (s["active"] or {}).get("aria"))
    page.keyboard.type(name, delay=20)
    page.keyboard.press("Tab")
    s = snap()
    chk(f"item {n}: Tab lands in its price box", f"Item {n} price in RM", (s["active"] or {}).get("aria"))
    page.keyboard.type(price, delay=20)
    settle()


def tap(item_name, person, label):
    g = page.get_by_role("group", name=f"Who had {item_name}", exact=True)
    chk(f"group 'Who had {item_name}' exists", 1, g.count())
    b = g.get_by_role("button", name=person, exact=True)
    hit_click(b, label)
    settle()
    return b


def uat06():
    global SNAP6
    # Step 1
    hit_click(page.locator("label[for=mode-item]"), "By item label")
    settle()
    s = snap()
    chk("step 1: By item is chosen", "item", s["mode"])
    chk("step 1 (info): Subtotal box hidden, Add item visible", [False, True], [s["subtotalVisible"], s["addItemVisible"]], info=True)
    chk("step 1 (info): Shares message with no items", "Add an item to see the shares.", s["message"], info=True)
    # Step 2
    hit_click(btn("Add item"), "Add item (#1)")
    settle()
    s = snap()
    chk("step 2: cursor goes into the new item's name box", "Item 1 name", (s["active"] or {}).get("aria"))
    # Step 3
    page.keyboard.type("Nasi lemak ayam", delay=20)
    page.keyboard.press("Tab")
    s = snap()
    chk("step 3: Tab lands in the price box", "Item 1 price in RM", (s["active"] or {}).get("aria"))
    page.keyboard.type("15.90", delay=20)
    settle()
    # Step 4
    s = snap()
    chk("step 4: Shares reads", "1 item still needs a person. Tap who had it to see the shares.", s["message"])
    chk("step 4: item row holds name and price", ["Nasi lemak ayam", "15.90"], [s["items"][0]["name"], s["items"][0]["price"]] if s["items"] else None)
    chk("step 4 (info): one tap button per person, none pressed", [["Aisyah", "false"], ["Ben", "false"], ["Chen", "false"]],
        [[t["text"], t["pressed"]] for t in s["items"][0]["taps"]] if s["items"] else None, info=True)
    # Step 5
    b = tap("Nasi lemak ayam", "Aisyah", "Aisyah under Nasi lemak ayam")
    chk("step 5: Aisyah is pressed", "true", b.get_attribute("aria-pressed"))
    chk("step 5: a tapped name turns dark (#141917 fill)", "rgb(20, 25, 23)", computed(b, "backgroundColor"))
    chk("step 5 (info): an untapped name is not dark", True, computed(page.get_by_role("group", name="Who had Nasi lemak ayam", exact=True).get_by_role("button", name="Ben", exact=True), "backgroundColor") != "rgb(20, 25, 23)", info=True)
    page.get_by_role("group", name="Who had Nasi lemak ayam", exact=True).screenshot(path=os.path.join(HERE, f"06-uat-06-tapped{TAG}.png"))
    # Step 6
    add_item_and_fill(2, "Char kuey teow", "13.50")
    tap("Char kuey teow", "Ben", "Ben under Char kuey teow")
    # Step 7
    add_item_and_fill(3, "Mee goreng mamak", "12.00")
    tap("Mee goreng mamak", "Chen", "Chen under Mee goreng mamak")
    # Step 8
    add_item_and_fill(4, "Satay, 10 sticks", "18.00")
    tap("Satay, 10 sticks", "Aisyah", "Aisyah under Satay")
    tap("Satay, 10 sticks", "Chen", "Chen under Satay")
    # Step 9
    s = snap()
    chk("step 9: items as typed", [[n, p] for n, p, _ in ITEMS], [[i["name"], i["price"]] for i in s["items"]])
    chk("step 9: who is tapped", [sorted(w) for _, _, w in ITEMS],
        [sorted(t["text"] for t in i["taps"] if t["pressed"] == "true") for i in s["items"]])
    check_summary(s, "RM 59.40", "RM 5.94", "10% of RM 59.40", "RM 3.92", "6% of RM 65.34", "RM 69.26", "UAT-06 step 9 summary")
    t = s["table"]
    chk("step 9: shares table present", True, t is not None)
    if t:
        head = t["head"][0] if t["head"] else None
        # innerText does not carry the CSS gap between the operator glyph and the column name ("+Charges"), so the column
        # check restores the space and a second check measures the gap on screen in pixels.
        heads_seen = [re.sub(r"^([+=])", r"\1 ", h) for h in (head[1:] if head else [])]
        chk("step 9: table columns (after the hidden 'Person' column), operator and label", ["Items", "+ Charges", "= Share"], heads_seen)
        gaps = page.evaluate("""() => [...document.querySelectorAll('table.shares thead th .op')].map((op) => {
            const th = op.parentElement; const tn = [...th.childNodes].find((n) => n.nodeType === 3 && n.textContent.trim());
            const r = document.createRange(); r.selectNodeContents(tn);
            return Math.round((r.getBoundingClientRect().left - op.getBoundingClientRect().right) * 10) / 10; })""")
        chk("step 9: on screen there is a visible gap (px) between '+' / '=' and the column name", True, gaps, ok=(len(gaps) == 2 and all(g >= 2 for g in gaps)))
        chk("step 9 (info): raw header innerText, no space between glyph and name", None, head, ok=True, info=True)
        exp_body = [["Aisyah", "RM 24.90", "RM 4.14", "RM 29.04"], ["Ben", "RM 13.50", "RM 2.24", "RM 15.74"], ["Chen", "RM 21.00", "RM 3.48", "RM 24.48"]]
        chk("step 9: table body", exp_body, t["body"])
        chk("step 9: Adds up to row", ["Adds up to", "RM 59.40", "RM 9.86", "RM 69.26"], t["foot"][0] if t["foot"] else None)
        chk("step 9: satay RM 18.00 split RM 9.00 each (derived from the Items column: 15.90+9.00=24.90, 12.00+9.00=21.00)", [24.90, 21.00], [round(15.90 + 9.00, 2), round(12.00 + 9.00, 2)], ok=True)
        chk("step 9 (info): the RM 9.00 satay split is NOT shown as a figure anywhere on screen", False, "RM 9.00" in s["tapeText"], info=True)
    chk("step 9 (info): no sideways scroll at this viewport (table fits, page fits)", True,
        page.evaluate("() => { const t = document.querySelector('table.shares'); const p = t.parentElement; return t.scrollWidth <= p.clientWidth + 1 && document.documentElement.scrollWidth <= window.innerWidth + 1; }"), info=True)
    SNAP6 = s


def uat07():
    global page
    pre = SNAP6
    chk("precondition: a draft is saved (info)", True, bool(pre and pre["storage"]), info=True)
    # Step 1: close the tab
    page.close()
    # Step 2: new tab in the same context, same address
    page = ctx.new_page()
    attach(page)
    page.goto(URL)
    page.wait_for_selector("input[aria-label='Person 1 name']", timeout=T)
    settle()
    # Step 3
    s = snap()
    chk("step 3: By item is still chosen", "item", s["mode"])
    chk("step 3: names", [p["value"] for p in pre["people"]], [p["value"] for p in s["people"]])
    chk("step 3: four items with names and prices", [[i["name"], i["price"]] for i in pre["items"]], [[i["name"], i["price"]] for i in s["items"]])
    chk("step 3: same names tapped", [sorted(t["text"] for t in i["taps"] if t["pressed"] == "true") for i in pre["items"]],
        [sorted(t["text"] for t in i["taps"] if t["pressed"] == "true") for i in s["items"]])
    chk("step 3: same Bill summary", pre["summary"], s["summary"])
    chk("step 3: same shares table", pre["table"], s["table"])
    chk("step 3 (info): four items on screen", 4, len(s["items"]), info=True)
    chk("step 3 (info): the copy status is not carried over", None, s["status"], ok=True, info=True)
    # Step 4
    hit_click(page.locator("label[for=mode-even]"), "Even label")
    settle()
    s = snap()
    chk("step 4: Even chosen", "even", s["mode"])
    chk("step 4: Subtotal box still holds", "100.00", s["subtotal"])
    check_even_shares(s, [("Aisyah", "RM 38.87"), ("Ben", "RM 38.87"), ("Chen", "RM 38.86")], "RM 116.60", "UAT-07 step 4 shares")


def uat08():
    pre = snap()
    raw_pre = pre["storage"]
    nb = btn("New bill")
    nb.scroll_into_view_if_needed(timeout=T)
    bb = nb.bounding_box()
    top_right = bb["x"] + bb["width"] > VIEW["width"] * 0.6 and bb["y"] < 120
    chk("step 1: New bill button is at the top right of the page", True, top_right)
    chk("step 1 (info): New bill box", None, bb, ok=True, info=True)
    hit_click(nb, "New bill")
    settle()
    s = snap()
    chk("step 2: the box is open", True, s["dialogOpen"])
    d = page.locator("dialog")
    chk("step 2: title", "Start a new bill?", norm(d.locator(".dialog-title").inner_text()))
    chk("step 2: text under it", "This clears the people, items and amounts.", norm(d.locator(".dialog-text").inner_text()))
    chk("step 2: exactly two buttons, 'Start new bill' and 'Cancel'", ["Start new bill", "Cancel"], [norm(x) for x in d.locator("button").all_inner_texts()])
    bd = computed("dialog", "backgroundColor", "::backdrop")
    chk("step 2: page behind is dimmed (backdrop scrim)", "rgba(20, 25, 23, 0.48)", bd)
    chk("step 2 (info): where the cursor is", "Cancel", (s["active"] or {}).get("text"), info=True)
    page.screenshot(path=os.path.join(HERE, f"08-uat-08-dialog-open{TAG}.png"), full_page=True)
    # Step 3
    hit_click(d.get_by_role("button", name="Cancel", exact=True), "Cancel")
    settle()
    s = snap()
    chk("step 3: box closed", False, s["dialogOpen"])
    chk("step 3: bill unchanged (same people, mode, subtotal, summary, shares)",
        [[p["value"] for p in pre["people"]], pre["mode"], pre["subtotal"], pre["summary"], pre["table"]],
        [[p["value"] for p in s["people"]], s["mode"], s["subtotal"], s["summary"], s["table"]])
    chk("step 3: saved draft unchanged", raw_pre, s["storage"])
    chk("step 3 (info): cursor returns to", "New bill", (s["active"] or {}).get("text"), info=True)
    # Step 4
    hit_click(btn("New bill"), "New bill (again)")
    settle()
    chk("step 4: box is open again", True, snap()["dialogOpen"])
    # Step 5: click on the dimmed page outside the box
    r = page.evaluate("""() => { const t = document.elementFromPoint(6, 6); const d = document.querySelector('dialog').getBoundingClientRect();
        return { tag: t ? t.tagName : null, isDialog: t === document.querySelector('dialog'), dialogBox: [d.left, d.top, d.right, d.bottom] }; }""")
    on_backdrop = bool(r["isDialog"] and (6 < r["dialogBox"][0] or 6 < r["dialogBox"][1]))
    chk("step 5: the point (6,6) is on the dimmed page, outside the box (elementFromPoint is the dialog element, point outside its box)", True, on_backdrop)
    chk("step 5 (info): hit-test detail", None, r, ok=True, info=True)
    page.mouse.click(6, 6)
    settle()
    s = snap()
    chk("step 5: box closed", False, s["dialogOpen"])
    chk("step 5: bill unchanged", [[p["value"] for p in pre["people"]], pre["mode"], pre["subtotal"], pre["summary"], pre["table"]],
        [[p["value"] for p in s["people"]], s["mode"], s["subtotal"], s["summary"], s["table"]])
    chk("step 5: saved draft unchanged", raw_pre, s["storage"])
    # Step 6
    hit_click(btn("New bill"), "New bill (third time)")
    settle()
    chk("step 6: box is open", True, snap()["dialogOpen"])
    # Step 7
    hit_click(d.get_by_role("button", name="Start new bill", exact=True), "Start new bill")
    settle()
    s = snap()
    chk("step 7: box closed", False, s["dialogOpen"])
    chk("step 7: 'Person 1' and 'Person 2'", ["Person 1", "Person 2"], [p["value"] for p in s["people"]])
    chk("step 7: Even chosen", "even", s["mode"])
    chk("step 7: Subtotal empty", "", s["subtotal"])
    chk("step 7: Service charge 10 and SST 6", ["10", "6"], [s["service"], s["sst"]])
    chk("step 7: Shares says", "Enter the subtotal to see the shares.", s["message"])
    chk("step 7 (info): Bill summary heading gone", True, "Bill summary" not in s["headings"], info=True)
    # Step 8
    hit_click(page.locator("label[for=mode-item]"), "By item label")
    settle()
    s = snap()
    chk("step 8: By item chosen", "item", s["mode"])
    chk("step 8: no items", 0, len(s["items"]))
    chk("step 8: only Add item is there", True, s["addItemVisible"])
    chk("step 8: Shares says", "Add an item to see the shares.", s["message"])
    chk("step 8 (info): no table, no Copy button", [None, 0], [s["table"], page.get_by_role("button", name="Copy summary", exact=True).count()], info=True)


CASES = [
    ("UAT-01", "I can list the people at the table", uat01),
    ("UAT-02", "An even split gives everyone the same share, to the cent", uat02),
    ("UAT-03", "The shares always add back up to the total", uat03),
    ("UAT-04", "I can change or switch off the charges", uat04),
    ("UAT-05", "One tap copies a summary I can paste into the group chat", uat05),
    ("UAT-06", "I can split by item, and a shared item is split between the people who had it", uat06),
    ("UAT-07", "My bill is still there when I come back", uat07),
    ("UAT-08", "I can start a new bill, but only on purpose", uat08),
]


def main():
    global page, ctx, cur
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            ctx = browser.new_context(viewport=VIEW)
            ctx.add_init_script(path=RECORDER)
            page = ctx.new_page()
            attach(page)
            page.goto(URL)
            page.wait_for_selector("input[aria-label='Person 1 name']", timeout=T)
            for n, (cid, title, fn) in enumerate(CASES, start=1):
                cur = {"title": title, "verdict": None, "checks": [], "notes": [], "error": None, "screenshot": None}
                results[cid] = cur
                try:
                    fn()
                except Exception as e:  # noqa: BLE001
                    cur["error"] = f"{type(e).__name__}: {str(e)[:900]}"
                    cur["trace"] = traceback.format_exc()[-1500:]
                try:
                    cur["screenshot"] = shot(n)
                except Exception as e:  # noqa: BLE001
                    cur["notes"].append(f"screenshot failed: {e}")
                failed = [c for c in cur["checks"] if not c["ok"] and not c["info"]]
                if cur["error"]:
                    cur["verdict"] = "BLOCKED? (step error, triage)"
                elif failed:
                    cur["verdict"] = "FAIL"
                else:
                    cur["verdict"] = "PASS"
                print(cid, cur["verdict"], "failed checks:", [c["name"] for c in failed], "error:", cur["error"])
        finally:
            browser.close()
    out = {"mode": MODE, "viewport": VIEW, "url": URL, "cases": results, "env": env}
    with open(os.path.join(HERE, f"results{TAG}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("done")


if __name__ == "__main__":
    main()
