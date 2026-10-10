"""Render checks for round-2 direction F (Orbit Console).

Run: python -B check_f.py
Opens f.html by file URL in headless Chromium (scrollbars shown) at 390 x 844, 360 x 780 and 1280 x 800.
navigator.clipboard is replaced before load by a stand-in that only records writes. Every request that is not
file: or data: is aborted and logged. Writes results.json and the screenshots beside this script.
"""
import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROUND = HERE.parent.parent
PAGE = ROUND / "f.html"
URL = PAGE.as_uri()
SPLIT = ROUND.parents[3]
WAIT_MS = 4000

CLIP_STUB = """
(() => {
  window.__clipWrites = [];
  window.__clipFail = false;
  const stub = {
    writeText(t) { if (window.__clipFail) return Promise.reject(new Error('blocked')); window.__clipWrites.push(String(t)); return Promise.resolve(); },
    write() { return Promise.resolve(); },
    readText() { return Promise.resolve(''); },
    read() { return Promise.resolve([]); },
  };
  Object.defineProperty(Navigator.prototype, 'clipboard', { get() { return stub; }, configurable: true });
})();
"""

R = {"console_errors": [], "page_errors": [], "network": [], "fails": [], "figures": {}, "noscroll_1280": {},
     "frame": {}, "overflow_360": {}, "proto_tab": {}, "order": {}, "contrast": {}, "icons": {}, "dashes": None,
     "fills": {}, "targets": {}, "arcs": {}, "shots": []}


def check(cond, label):
    if not cond:
        R["fails"].append(label)
    return cond


# ---------- contrast ----------
def parse_colour(s):
    s = s.strip()
    if s.startswith("#"):
        h = s[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return [int(h[i:i + 2], 16) for i in (0, 2, 4)] + [1.0]
    m = re.match(r"rgba?\(([^)]+)\)", s)
    parts = [p.strip() for p in m.group(1).replace("/", ",").split(",")]
    rgb = [float(p) for p in parts[:3]]
    a = float(parts[3]) if len(parts) > 3 else 1.0
    return rgb + [a]


def over(fg, bg):
    a = fg[3]
    return [fg[i] * a + bg[i] * (1 - a) for i in range(3)] + [1.0]


def lum(c):
    lin = []
    for v in c[:3]:
        v = v / 255
        lin.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


# ---------- static file checks ----------
src = PAGE.read_text(encoding="utf-8")
R["dashes"] = {"em": src.count("—"), "en": src.count("–"), "middle_dot": src.count("·")}
check(R["dashes"]["em"] == 0 and R["dashes"]["en"] == 0, "long dashes in f.html")
ref = {}
for name, d in re.findall(r'(\w+): "(M[^"]+)"', (SPLIT / "src" / "ui" / "icons.js").read_text(encoding="utf-8")):
    ref[name] = d
for f in ("d.html", "a.html"):
    for sym, d in re.findall(r'<symbol id="i-([\w-]+)" viewBox="0 0 256 256"><path d="([^"]+)"', (ROUND.parent / "round-1" / f).read_text(encoding="utf-8")):
        ref.setdefault(sym, d)
for sym, d in re.findall(r'<symbol id="i-([\w-]+)" viewBox="0 0 256 256"><path d="([^"]+)"', src):
    R["icons"][sym] = "match" if ref.get(sym) == d else "MISMATCH"
    check(ref.get(sym) == d, f"icon {sym} differs from source")

# ---------- page helpers ----------
JS_ROWS = """() => [...document.querySelectorAll('#result .legend .row')].map(r => ({
  name: r.querySelector('.nm').firstChild.textContent,
  sen: r.querySelector('.sen') ? r.querySelector('.sen').textContent : '',
  items: r.querySelector('.it') ? r.querySelector('.it').textContent : null,
  charges: r.querySelector('.ch') ? r.querySelector('.ch').textContent : null,
  share: (r.querySelector('.sh').textContent.match(/RM [\\d,]+\\.\\d\\d/) || [''])[0]
}))"""
JS_FOOT = """() => { const f = document.querySelector('#result .foot'); if (!f) return null;
  return { items: f.querySelector('.it') ? f.querySelector('.it').textContent : null,
           charges: f.querySelector('.ch') ? f.querySelector('.ch').textContent : null,
           share: f.querySelector('.sh').textContent }; }"""
JS_BILL = """() => [...document.querySelectorAll('#bill > div')].map(d => d.querySelector('dt').textContent + ' = ' + d.querySelector('dd').textContent)"""
JS_OVERFLOW = """() => {
  const vw = document.documentElement.clientWidth;
  const bad = [];
  for (const el of document.querySelectorAll('body *')) {
    if (el.closest('.sprite, .sr-only, dialog:not([open]), [hidden], title, #protoPanel')) continue;
    const r = el.getBoundingClientRect();
    if (!r.width && !r.height) continue;
    if (r.right > vw + 0.5 || r.left < -0.5) bad.push((el.id ? '#' + el.id : el.tagName.toLowerCase() + '.' + (el.getAttribute('class') || '')) + ' ' + Math.round(r.left) + '..' + Math.round(r.right));
  }
  return { scrollWidth: document.documentElement.scrollWidth, clientWidth: vw, bad: bad.slice(0, 12) };
}"""
JS_NOSCROLL = """() => {
  const de = document.documentElement;
  const box = (sel) => { const e = document.querySelector(sel); return e ? { scrollHeight: e.scrollHeight, clientHeight: e.clientHeight } : null; };
  return { docScrollHeight: de.scrollHeight, viewport: window.innerHeight, bodyScrollHeight: document.body.scrollHeight,
           receipt: box('#receiptSlot'), inputs: box('#inputs'), frame: box('#ilist') };
}"""
# Content boxes the prototype tab must never cover. Structural wrappers that only hold padding are skipped.
JS_TAB = """() => {
  const tab = document.querySelector('#protoTab').getBoundingClientRect();
  const skip = new Set(['HTML', 'BODY', 'MAIN', 'SECTION', 'FIELDSET', 'UL', 'OL']);
  const skipIds = new Set(['app', 'layout', 'inputs', 'receiptSlot', 'billInputs', 'notes', 'protoTab']);
  const hits = [];
  const hit = (a, b) => a.left < b.right - 0.5 && b.left < a.right - 0.5 && a.top < b.bottom - 0.5 && b.top < a.bottom - 0.5;
  for (const el of document.querySelectorAll('body *')) {
    if (el.closest('.sprite, .sr-only, dialog, [hidden], title, #protoPanel')) continue;
    if (skip.has(el.tagName) || skipIds.has(el.id)) continue;
    if (el.classList.contains('items-block') || el.classList.contains('bill-inputs')) continue;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    if (hit(tab, r)) hits.push((el.id ? '#' + el.id : el.tagName.toLowerCase() + '.' + (el.getAttribute('class') || '')) + ' ' + Math.round(r.left) + ',' + Math.round(r.top));
  }
  const dock = document.querySelector('#dock').getBoundingClientRect();
  const top = document.querySelector('.top').getBoundingClientRect();
  return { tab: [Math.round(tab.left), Math.round(tab.top), Math.round(tab.width), Math.round(tab.height)],
           hits: hits.slice(0, 10), dock: dock.height ? hit(tab, dock) : false, header: hit(tab, top) };
}"""
JS_ORDER = """() => {
  const y = (sel) => { const e = document.querySelector(sel); return e ? Math.round(e.getBoundingClientRect().top) : null; };
  return { charges: y('#h-charges'), mode: y('#mode'), people: y('#h-people'), items: y('#h-items') ?? y('#subtotal'),
           receiptInSheet: !!document.querySelector('#sheetBody #orbit'), receiptInSlot: !!document.querySelector('#receiptSlot #orbit') };
}"""
JS_FILLS = """() => {
  const out = [];
  for (const b of document.querySelectorAll('button, .mode label')) {
    if (b.closest('#protoPanel, .sprite') || b.id === 'protoTab') continue;
    const r = b.getBoundingClientRect();
    if (!r.width) continue;
    const bg = getComputedStyle(b).backgroundColor;
    out.push({ el: b.id || b.className || b.textContent.trim().slice(0, 20), bg });
  }
  return out;
}"""
JS_TARGETS = """() => {
  const small = [];
  for (const b of document.querySelectorAll('button, input, .mode label')) {
    if (b.closest('#protoPanel, dialog:not([open]), [hidden]') || b.id === 'protoTab' || b.type === 'radio') continue;
    const r = b.getBoundingClientRect();
    if (!r.width) continue;
    if (r.height < 43.5 || r.width < 43.5) small.push((b.id || b.className || b.getAttribute('aria-label') || '') + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
  }
  return small;
}"""
JS_ARCS = """() => {
  const segs = [...document.querySelectorAll('#ring .seg')];
  const lens = segs.map(p => p.getTotalLength());
  const sum = lens.reduce((a, b) => a + b, 0);
  return Math.max(0, ...segs.map((p, i) => Math.abs(lens[i] / sum - (+p.dataset.share / +p.dataset.total))));
}"""


def rows(page):
    return page.evaluate(JS_ROWS)


def shares(page):
    return [(r["name"], r["share"], r["sen"]) for r in rows(page)]


def idle(page):
    page.wait_for_function("window.__ringIdle === true", timeout=WAIT_MS)
    page.wait_for_timeout(150)


def state(page, key):
    page.evaluate(f"window.__loadState('{key}')")
    idle(page)


def shot(page, name, full=False):
    path = HERE / f"{name}.png"
    page.screenshot(path=str(path), full_page=full)
    R["shots"].append(path.name)


def text(page, sel):
    return page.eval_on_selector(sel, "e => e.textContent.replace(/\\s+/g, ' ').trim()")


def is_open(page, sel):
    return page.eval_on_selector(sel, "d => d.open")


def noscroll(page, label):
    v = page.evaluate(JS_NOSCROLL)
    R["noscroll_1280"][label] = v
    check(v["docScrollHeight"] == v["viewport"] == 800, f"1280 {label}: page scrolls ({v['docScrollHeight']})")
    check(v["receipt"]["scrollHeight"] <= v["receipt"]["clientHeight"], f"1280 {label}: receipt column overflows")
    check(v["inputs"]["scrollHeight"] <= v["inputs"]["clientHeight"], f"1280 {label}: input pane overflows")


def tab_check(page, label):
    v = page.evaluate(JS_TAB)
    R["proto_tab"][label] = v
    check(not v["hits"] and not v["dock"] and not v["header"], f"proto tab overlaps content at {label}: {v}")


def overflow360(page, label):
    v = page.evaluate(JS_OVERFLOW)
    R["overflow_360"][label] = v
    check(v["scrollWidth"] <= v["clientWidth"] and not v["bad"], f"360 {label}: sideways overflow {v}")


K1_ROWS = [
    {"name": "Aisyah", "sen": "+1 sen", "items": "RM 24.90", "charges": "RM 4.14", "share": "RM 29.04"},
    {"name": "Ben", "sen": "", "items": "RM 13.50", "charges": "RM 2.24", "share": "RM 15.74"},
    {"name": "Chen", "sen": "", "items": "RM 21.00", "charges": "RM 3.48", "share": "RM 24.48"},
]
K1_BILL = ["Subtotal = RM 59.40", "Service charge10% of RM 59.40 = RM 5.94", "SST6% of RM 65.34 = RM 3.92", "Total = RM 69.26"]
K2_BILL = ["Subtotal = RM 100.00", "Service charge10% of RM 100.00 = RM 10.00", "SST6% of RM 110.00 = RM 6.60", "Total = RM 116.60"]


def figures_k1(page, where):
    got = rows(page)
    R["figures"][f"K1 rows {where}"] = got
    check(got == K1_ROWS, f"K1 rows {where}: {got}")
    foot = page.evaluate(JS_FOOT)
    R["figures"][f"K1 adds up {where}"] = foot
    check(foot == {"items": "RM 59.40", "charges": "RM 9.86", "share": "RM 69.26"}, f"K1 foot {where}: {foot}")
    bill = page.evaluate(JS_BILL)
    R["figures"][f"K1 bill {where}"] = bill
    check(bill == K1_BILL, f"K1 bill {where}: {bill}")
    sp = text(page, "#spare")
    R["figures"][f"K1 spare {where}"] = sp
    check(sp.startswith("1 sen left over") and "Top of the list" in sp, f"K1 spare {where}: {sp}")
    cen = text(page, "#centre")
    check(cen == "TotalRM69.26", f"K1 centre {where}: {cen}")


def figures_k2(page, where):
    got = shares(page)
    R["figures"][f"K2 shares {where}"] = got
    check(got == [("Aisyah", "RM 38.87", "+1 sen"), ("Ben", "RM 38.87", "+1 sen"), ("Chen", "RM 38.86", "")], f"K2 shares {where}: {got}")
    bill = page.evaluate(JS_BILL)
    R["figures"][f"K2 bill {where}"] = bill
    check(bill == K2_BILL, f"K2 bill {where}: {bill}")
    sp = text(page, "#spare")
    check(sp.startswith("2 sen left over") and "Top of the list" in sp, f"K2 spare {where}: {sp}")
    foot = page.evaluate(JS_FOOT)
    check(foot and foot["share"] == "RM 116.60", f"K2 foot {where}: {foot}")


with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, ignore_default_args=["--hide-scrollbars"])
    try:
        def new_page(w, h, reduced=False, phone=False):
            # phone=True emulates a touch phone (overlay scrollbars) for honest 390 screenshots.
            # 360 stays a desktop-style window with classic scrollbars, the stricter width test.
            ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1,
                                      is_mobile=phone, has_touch=phone,
                                      reduced_motion="reduce" if reduced else "no-preference")
            ctx.add_init_script(CLIP_STUB)
            pg = ctx.new_page()
            pg.set_default_timeout(WAIT_MS)
            tag = f"{w}{'rm' if reduced else ''}"
            pg.on("console", lambda m: R["console_errors"].append(f"{tag}: {m.text}") if m.type == "error" else None)
            pg.on("pageerror", lambda e: R["page_errors"].append(f"{tag}: {e}"))

            def route(r):
                if r.request.url.startswith("file:") or r.request.url.startswith("data:"):
                    r.continue_()
                else:
                    R["network"].append(r.request.url)
                    r.abort()
            pg.route("**/*", route)
            pg.goto(URL, wait_until="load")
            idle(pg)
            return ctx, pg

        # ================= 390 x 844 =================
        ctx, page = new_page(390, 844, phone=True)
        shot(page, "k1-390")
        shot(page, "k1-390-full", full=True)
        R["order"]["390"] = page.evaluate(JS_ORDER)
        o = R["order"]["390"]
        check(o["charges"] < o["mode"] < o["people"] < o["items"], f"390 input order {o}")
        check(o["receiptInSheet"] and not o["receiptInSlot"], "390 receipt not in the sheet")
        check(o["people"] < 844, "390 People not on the first screen")
        check(page.evaluate("window.scrollY") == 0, "390 starts scrolled")
        dock_total = text(page, "#dockInfo")
        R["figures"]["K1 bar 390"] = dock_total
        check(dock_total == "TotalRM69.26", f"K1 bar total {dock_total}")
        tab_check(page, "390 K1 top")
        R["targets"]["390 K1"] = page.evaluate(JS_TARGETS)
        R["fills"]["390 K1"] = page.evaluate(JS_FILLS)

        # P2 Shares sheet from the bar
        page.click("#sharesBtn")
        page.wait_for_selector("#sharesDlg[open]")
        idle(page)
        page.wait_for_timeout(300)
        shot(page, "p2-390")
        figures_k1(page, "390 sheet")
        R["arcs"]["K1 390"] = page.evaluate(JS_ARCS)
        R["targets"]["390 P2"] = page.evaluate(JS_TARGETS)
        R["fills"]["390 P2"] = page.evaluate(JS_FILLS)
        page.eval_on_selector(".sheet-body", "e => e.scrollTop = e.scrollHeight")
        page.wait_for_timeout(150)
        shot(page, "p2-390-bill")
        page.eval_on_selector(".sheet-body", "e => e.scrollTop = 0")
        # Copy summary inside the sheet writes the 1.0 text to the stand-in clipboard
        page.click("#copyBtn")
        page.wait_for_timeout(150)
        clip = page.evaluate("window.__clipWrites")
        R["figures"]["K1 summary text"] = clip[-1] if clip else None
        check(clip and clip[-1] == "Bill split\nTotal RM 69.26 (subtotal RM 59.40, service 10% RM 5.94, SST 6% RM 3.92)\nAisyah RM 29.04\nBen RM 15.74\nChen RM 24.48\nAdds up to RM 69.26", f"K1 summary text {clip}")
        check(text(page, "#status") == "Summary copied", "S4 copied status in sheet")
        # P1 from the sheet, One person, Ben
        page.click("#spareBtn")
        page.wait_for_selector("#spareDlg[open]")
        page.wait_for_timeout(250)
        shot(page, "p1-390")
        page.click('#choices [data-v="one"]')
        page.wait_for_timeout(200)
        shot(page, "p1-picker-390")
        page.click('#picker [data-person="b"]')
        idle(page)
        got = shares(page)
        R["figures"]["K1 one Ben"] = got
        check(got == [("Aisyah", "RM 29.03", ""), ("Ben", "RM 15.75", "+1 sen"), ("Chen", "RM 24.48", "")], f"K1 one Ben {got}")
        check(is_open(page, "#sharesDlg"), "sheet should stay open after the picker closes")
        shot(page, "k1-one-ben-390")
        # K1 At random gives the one sen to someone, and it varies
        page.click("#spareBtn")
        page.click('#choices [data-v="random"]')
        idle(page)
        draws = []
        for _ in range(12):
            draws.append(tuple(n for n, s, sen in shares(page) if sen))
            page.click("#pickAgain")
            idle(page)
        R["figures"]["K1 random draws"] = draws
        check(all(len(d) == 1 for d in draws), "K1 random: one person per draw")
        # Esc closes P1 first, then the sheet. Backdrop and Close shut the sheet
        page.click("#spareBtn")
        page.wait_for_selector("#spareDlg[open]")
        page.keyboard.press("Escape")
        page.wait_for_timeout(150)
        check(not is_open(page, "#spareDlg") and is_open(page, "#sharesDlg"), "Esc closes P1 only")
        page.click("#spareBtn")
        page.wait_for_selector("#spareDlg[open]")
        page.mouse.click(195, 30)
        page.wait_for_timeout(150)
        check(not is_open(page, "#spareDlg"), "backdrop closes P1")
        page.keyboard.press("Escape")
        page.wait_for_timeout(150)
        check(not is_open(page, "#sharesDlg"), "Esc closes the sheet")
        page.click("#sharesBtn")
        page.wait_for_selector("#sharesDlg[open]")
        page.mouse.click(195, 20)
        page.wait_for_timeout(150)
        check(not is_open(page, "#sharesDlg"), "backdrop closes the sheet")
        page.click("#sharesBtn")
        page.wait_for_selector("#sharesDlg[open]")
        page.click("#sharesDlg [data-close]")
        page.wait_for_timeout(150)
        check(not is_open(page, "#sharesDlg"), "Close shuts the sheet")
        tab_check(page, "390 tab with sheet closed")

        # K2 by the design's own switch
        state(page, "K1")
        page.click("label:has(#m-even)")
        idle(page)
        figures_k2(page, "390 via switch")
        shot(page, "k2-390")
        page.click("#sharesBtn")
        page.wait_for_selector("#sharesDlg[open]")
        idle(page)
        page.wait_for_timeout(300)
        shot(page, "p2-k2-390")
        page.click("#spareBtn")
        page.click('#choices [data-v="one"]')
        page.click('#picker [data-person="b"]')
        idle(page)
        got = shares(page)
        R["figures"]["K2 one Ben"] = got
        check(got == [("Aisyah", "RM 38.86", ""), ("Ben", "RM 38.88", "+2 sen"), ("Chen", "RM 38.86", "")], f"K2 one Ben {got}")
        page.click("#spareBtn")
        page.click('#choices [data-v="random"]')
        idle(page)
        draws = []
        for _ in range(12):
            s = shares(page)
            draws.append(tuple(n for n, sh, sen in s if sen))
            check(sorted(sh for n, sh, sen in s) == ["RM 38.86", "RM 38.87", "RM 38.87"], f"K2 random figures {s}")
            page.click("#pickAgain")
            idle(page)
        R["figures"]["K2 random draws"] = draws
        check(all(len(d) == 2 for d in draws), "K2 random: two different people get one sen each")
        check(len(set(draws)) > 1, "K2 random: the pair changes between draws")
        page.keyboard.press("Escape")
        page.wait_for_timeout(150)

        # M1
        state(page, "K1")
        page.click("#newBill")
        page.wait_for_selector("#newDlg[open]")
        page.wait_for_timeout(250)
        shot(page, "m1-390")
        R["figures"]["M1"] = text(page, "#newDlg")
        check(R["figures"]["M1"] == "Start a new bill? This clears the people, items and amounts. Start new bill Cancel", f"M1 {R['figures']['M1']}")
        R["fills"]["390 M1"] = page.evaluate(JS_FILLS)
        page.keyboard.press("Escape")
        page.wait_for_timeout(150)
        check(not is_open(page, "#newDlg"), "Esc closes M1")
        page.click("#newBill")
        page.wait_for_selector("#newDlg[open]")
        page.mouse.click(10, 10)
        page.wait_for_timeout(150)
        check(not is_open(page, "#newDlg"), "backdrop closes M1")
        page.click("#newBill")
        page.click("#newDlg [data-close]")
        check(not is_open(page, "#newDlg"), "Cancel closes M1")
        page.click("#newBill")
        page.click("#confirmNew")
        idle(page)
        s1 = page.evaluate("""() => ({ people: [...document.querySelectorAll('#plist input')].map(i => i.value + '|' + i.placeholder),
            even: document.querySelector('#m-even').checked, subtotal: document.querySelector('#subtotal').value,
            svc: document.querySelector('#svc').value, sst: document.querySelector('#sst').value,
            bar: document.querySelector('#dockInfo').textContent, centre: document.querySelector('#centre').textContent })""")
        R["figures"]["S1 via Start new bill"] = s1
        check(s1 == {"people": ["|Person 1", "|Person 2"], "even": True, "subtotal": "", "svc": "10", "sst": "6",
                     "bar": "Enter the subtotal to see the shares.", "centre": "Enter the subtotal to see the shares."}, f"S1 {s1}")
        shot(page, "s1-390")

        # States with no natural trigger
        state(page, "S2")
        R["figures"]["S2"] = text(page, "#billInputs")
        check("Enter an amount like 12.50" in R["figures"]["S2"], "S2 error copy")
        shot(page, "s2-390")
        state(page, "S3")
        R["figures"]["S3 bar"] = text(page, "#dockInfo")
        R["figures"]["S3 receipt"] = text(page, "#result")
        check(R["figures"]["S3 bar"] == "1 item still needs a person. Tap who had it to see the shares.", "S3 bar copy")
        check(R["figures"]["S3 receipt"] == "1 item still needs a person. Tap who had it to see the shares.", "S3 receipt copy")
        check(page.evaluate("document.querySelector('#dockCopy').disabled"), "S3 copy disabled")
        shot(page, "s3-390")
        state(page, "S4b")
        R["figures"]["S4 blocked"] = text(page, "#dockStatus")
        check(R["figures"]["S4 blocked"] == "Could not copy. Your browser blocked the clipboard.", "S4 blocked copy")
        shot(page, "s4b-390")
        # the blocked path through the real button
        state(page, "K1")
        page.evaluate("window.__clipFail = true")
        page.click("#dockCopy")
        page.wait_for_timeout(150)
        check(text(page, "#dockStatus") == "Could not copy. Your browser blocked the clipboard.", "S4 blocked by the bar button")
        page.evaluate("window.__clipFail = false")
        page.click("#dockCopy")
        page.wait_for_timeout(150)
        R["figures"]["S4 copied (bar)"] = text(page, "#dockStatus")
        check(R["figures"]["S4 copied (bar)"] == "Summary copied", "S4 copied by the bar button")
        shot(page, "s4a-390")
        state(page, "S5")
        R["figures"]["S5"] = text(page, "#notes")
        check(R["figures"]["S5"] == "This bill is not being saved on this device. It will be lost when you close this tab.", "S5 copy")
        tab_check(page, "390 S5")
        shot(page, "s5-390")
        state(page, "S6")
        R["figures"]["S6"] = text(page, "#notes")
        check(R["figures"]["S6"] == "Your saved bill could not be read, so a new one was started.", "S6 copy")
        shot(page, "s6-390")
        page.click('#notes [aria-label="Dismiss note"]')
        check(text(page, "#notes") == "", "S6 dismiss")
        state(page, "S7")
        check(page.eval_on_selector("#addPerson", "b => b.disabled"), "S7 add person disabled")
        check(page.evaluate("document.querySelectorAll('#plist .person').length") == 12, "S7 has 12 people")
        shot(page, "s7-390-full", full=True)
        # W2 at 390: the item frame scrolls inside itself
        state(page, "W2")
        fr = page.evaluate("() => { const f = document.querySelector('#ilist'); return { sh: f.scrollHeight, ch: f.clientHeight, down: document.querySelector('#frameWrap').hasAttribute('data-down') }; }")
        R["frame"]["W2 390"] = fr
        check(fr["sh"] > fr["ch"] and fr["down"], f"W2 390 frame does not scroll {fr}")
        page.eval_on_selector("#billInputs", "e => e.scrollIntoView({ block: 'start' })")
        page.eval_on_selector("#ilist", "e => e.scrollTop = 360")
        page.wait_for_timeout(250)
        fr2 = page.evaluate("() => ({ top: document.querySelector('#ilist').scrollTop, up: document.querySelector('#frameWrap').hasAttribute('data-up'), down: document.querySelector('#frameWrap').hasAttribute('data-down') })")
        R["frame"]["W2 390 scrolled"] = fr2
        check(fr2["top"] > 0 and fr2["up"] and fr2["down"], f"W2 390 frame fades {fr2}")
        shot(page, "w2-390")
        tab_check(page, "390 W2 scrolled to items")
        page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        page.wait_for_timeout(100)
        tab_check(page, "390 W2 page bottom")
        w2 = shares(page)
        w2tot = text(page, "#dockInfo")
        R["figures"]["W2 (prototype only)"] = {"rows": rows(page), "bar": w2tot, "bill": page.evaluate(JS_BILL)}
        cents = lambda s: int(s.replace("RM ", "").replace(",", "").replace(".", ""))
        check(sum(cents(s) for n, s, sen in w2) == cents(page.evaluate(JS_FOOT)["share"]), "W2 shares add up")

        # Prototype panel open
        state(page, "K1")
        page.click("#protoTab")
        page.wait_for_timeout(150)
        shot(page, "proto-panel-390")
        pp = page.evaluate("() => { const p = document.querySelector('#protoPanel').getBoundingClientRect(); const d = document.querySelector('#dock').getBoundingClientRect(); return { bottom: p.bottom, dockTop: d.top }; }")
        R["proto_tab"]["390 panel vs bar"] = pp
        check(pp["bottom"] <= pp["dockTop"], f"proto panel overlaps the pinned bar {pp}")
        page.click("#protoClose")
        # the tab sits under an open popup's backdrop
        page.click("#newBill")
        page.wait_for_selector("#newDlg[open]")
        under = page.evaluate("() => { const r = document.querySelector('#protoTab').getBoundingClientRect(); const e = document.elementFromPoint(r.left + 7, r.top + r.height / 2); return e ? (e.id || e.tagName) : null; }")
        R["proto_tab"]["390 under backdrop"] = under
        check(under != "protoTab", "proto tab above the backdrop")
        page.keyboard.press("Escape")
        ctx.close()

        # ================= 360 x 780 =================
        ctx, page = new_page(360, 780)
        shot(page, "k1-360")
        overflow360(page, "K1")
        tab_check(page, "360 K1")
        for key in ["K2", "S1", "S2", "S3", "S4b", "S5", "S6", "S7", "W1", "W2"]:
            state(page, key)
            overflow360(page, key)
        state(page, "W1")
        R["figures"]["W1 bar"] = text(page, "#dockInfo")
        check(R["figures"]["W1 bar"] == "TotalRM1,193.87", f"W1 bar {R['figures']['W1 bar']}")
        overflow360(page, "W1 page bottom")
        page.click("#sharesBtn")
        page.wait_for_selector("#sharesDlg[open]")
        idle(page)
        page.wait_for_timeout(300)
        overflow360(page, "W1 sheet")
        R["figures"]["W1 sheet rows"] = rows(page)
        R["figures"]["W1 bill"] = page.evaluate(JS_BILL)
        check(page.evaluate(JS_BILL)[-1] == "Total = RM 1,193.87", "W1 total in the sheet")
        coll = page.evaluate("""() => { const out = []; const hit = (a, b) => a.left < b.right - 0.5 && b.left < a.right - 0.5 && a.top < b.bottom - 0.5 && b.top < a.bottom - 0.5;
          for (const row of document.querySelectorAll('#result .row, #result .foot')) { const p = [...row.querySelectorAll('.nm, .wk, .sh')];
            for (let i = 0; i < p.length; i++) for (let j = i + 1; j < p.length; j++) if (hit(p[i].getBoundingClientRect(), p[j].getBoundingClientRect())) out.push(row.textContent); }
          const c = document.querySelector('#centre .c-fig'); if (c && c.getBoundingClientRect().width > document.querySelector('#centre').getBoundingClientRect().width + 0.5) out.push('centre figure too wide');
          return out; }""")
        R["figures"]["W1 360 collisions"] = coll
        check(not coll, f"W1 360 collisions {coll}")
        shot(page, "w1-360-sheet")
        page.keyboard.press("Escape")
        page.wait_for_timeout(150)
        shot(page, "w1-360")
        state(page, "K1")
        page.click("#sharesBtn")
        page.wait_for_selector("#sharesDlg[open]")
        idle(page)
        page.wait_for_timeout(300)
        overflow360(page, "P2")
        shot(page, "p2-360")
        page.click("#spareBtn")
        page.wait_for_selector("#spareDlg[open]")
        page.wait_for_timeout(250)
        overflow360(page, "P1")
        page.keyboard.press("Escape")
        page.keyboard.press("Escape")
        page.wait_for_timeout(150)
        page.click("#newBill")
        page.wait_for_selector("#newDlg[open]")
        page.wait_for_timeout(250)
        overflow360(page, "M1")
        shot(page, "m1-360")
        page.keyboard.press("Escape")
        R["targets"]["360 K1"] = page.evaluate(JS_TARGETS)
        ctx.close()

        # ================= 1280 x 800 =================
        ctx, page = new_page(1280, 800)
        shot(page, "k1-1280")
        figures_k1(page, "1280")
        R["arcs"]["K1 1280"] = page.evaluate(JS_ARCS)
        noscroll(page, "K1")
        R["order"]["1280"] = page.evaluate(JS_ORDER)
        o = R["order"]["1280"]
        check(o["charges"] < o["mode"] < o["people"] < o["items"], f"1280 input order {o}")
        check(o["receiptInSlot"], "1280 receipt not beside the inputs")
        tab_check(page, "1280 K1")
        R["targets"]["1280 K1"] = page.evaluate(JS_TARGETS)
        R["fills"]["1280 K1"] = page.evaluate(JS_FILLS)
        fr = page.evaluate("() => { const f = document.querySelector('#ilist'); return { sh: f.scrollHeight, ch: f.clientHeight }; }")
        R["frame"]["K1 1280"] = fr
        page.click("#spareBtn")
        page.wait_for_selector("#spareDlg[open]")
        page.wait_for_timeout(250)
        shot(page, "p1-1280")
        page.click('#choices [data-v="one"]')
        page.wait_for_timeout(250)
        shot(page, "p1-picker-1280")
        page.click('#picker [data-person="b"]')
        idle(page)
        got = shares(page)
        R["figures"]["K1 one Ben 1280"] = got
        check(got == [("Aisyah", "RM 29.03", ""), ("Ben", "RM 15.75", "+1 sen"), ("Chen", "RM 24.48", "")], f"K1 one Ben 1280 {got}")
        shot(page, "k1-one-ben-1280")
        page.click("#newBill")
        page.wait_for_selector("#newDlg[open]")
        page.wait_for_timeout(250)
        shot(page, "m1-1280")
        page.keyboard.press("Escape")
        state(page, "K2")
        figures_k2(page, "1280")
        noscroll(page, "K2")
        shot(page, "k2-1280")
        state(page, "S7")
        noscroll(page, "S7")
        R["figures"]["S7 1280 shares"] = shares(page)
        check(page.eval_on_selector("#addPerson", "b => b.disabled"), "S7 1280 add person disabled")
        R["arcs"]["S7 1280"] = page.evaluate(JS_ARCS)
        shot(page, "s7-1280")
        state(page, "W2")
        noscroll(page, "W2")
        fr = page.evaluate("() => { const f = document.querySelector('#ilist'); return { sh: f.scrollHeight, ch: f.clientHeight, down: document.querySelector('#frameWrap').hasAttribute('data-down') }; }")
        R["frame"]["W2 1280"] = fr
        check(fr["sh"] > fr["ch"] and fr["down"], f"W2 1280 frame does not scroll {fr}")
        shot(page, "w2-1280")
        page.hover("#ilist")
        page.mouse.wheel(0, 500)
        page.wait_for_timeout(300)
        fr2 = page.evaluate("() => ({ top: document.querySelector('#ilist').scrollTop, winY: window.scrollY, up: document.querySelector('#frameWrap').hasAttribute('data-up') })")
        R["frame"]["W2 1280 after wheel"] = fr2
        check(fr2["top"] > 0 and fr2["winY"] == 0 and fr2["up"], f"W2 1280 wheel scrolls the frame, not the page {fr2}")
        noscroll(page, "W2 scrolled")
        shot(page, "w2-1280-scrolled")
        R["figures"]["W2 1280 rows (prototype only)"] = rows(page)
        state(page, "S3")
        noscroll(page, "S3 (extra)")
        shot(page, "s3-1280")
        state(page, "S5")
        noscroll(page, "S5 (extra)")
        tab_check(page, "1280 S5")
        shot(page, "s5-1280")
        state(page, "S6")
        noscroll(page, "S6 (extra)")
        shot(page, "s6-1280")
        state(page, "S1")
        shot(page, "s1-1280")
        # hover a share row lights its segment
        state(page, "K1")
        page.hover('.legend .row[data-id="b"]')
        page.wait_for_timeout(250)
        R["figures"]["hover lit"] = page.evaluate("[...document.querySelectorAll('#ring .on')].map(e => e.tagName + ':' + e.dataset.id)")
        shot(page, "hover-ben-1280")
        page.mouse.move(5, 400)
        # keyboard focus is visible on Copy summary
        page.focus("#spareBtn")
        page.keyboard.press("Tab")
        page.wait_for_timeout(100)
        R["figures"]["focus after spare button"] = page.evaluate("document.activeElement.id")
        R["figures"]["focus outline"] = page.evaluate("getComputedStyle(document.activeElement).outlineStyle + ' ' + getComputedStyle(document.activeElement).outlineColor")
        shot(page, "focus-copy-1280")
        tokens = page.evaluate("""() => { const cs = getComputedStyle(document.documentElement); const out = {};
          for (const n of ['l0','l1','l2','l3','l4','l5','field','line-strong','text','text-muted','accent','accent-ink','accent-line','accent-tint','error-ink','danger-tint','warn-ink','warn-bg','info-bg','focus','on-person','p1','p2','p3','p4','p5','p6','p7','p8','p9','p10','p11','p12']) out[n] = cs.getPropertyValue('--' + n).trim();
          return out; }""")
        ctx.close()

        # ================= in-between widths (looked at, not part of the brief's gates) =================
        ctx, page = new_page(1024, 768)
        shot(page, "k1-1024")
        R["figures"]["1024 x 768 K1"] = page.evaluate(JS_NOSCROLL)
        ctx.close()
        ctx, page = new_page(768, 1024, phone=True)
        shot(page, "k1-768")
        page.click("#sharesBtn")
        page.wait_for_selector("#sharesDlg[open]")
        idle(page)
        page.wait_for_timeout(300)
        shot(page, "p2-768")
        ctx.close()

        # ================= reduced motion =================
        ctx, page = new_page(390, 844, reduced=True)
        R["figures"]["reduced motion idle at load"] = page.evaluate("window.__ringIdle === true")
        page.click("#sharesBtn")
        page.wait_for_selector("#sharesDlg[open]")
        R["figures"]["reduced motion idle on sheet open"] = page.evaluate("window.__ringIdle === true")
        check(R["figures"]["reduced motion idle on sheet open"], "reduced motion still tweens the ring")
        ctx.close()
    finally:
        browser.close()

# ---------- contrast table ----------
t = {k: parse_colour(v) for k, v in tokens.items()}
tint_l3 = over(t["accent-tint"], t["l3"])
tint_l2 = over(t["accent-tint"], t["l2"])
tint_l1 = over(t["accent-tint"], t["l1"])
danger_l3 = over(t["danger-tint"], t["l3"])
pairs = [
    ("body text on input pane l2", t["text"], t["l2"], 4.5), ("body text on receipt panel l3", t["text"], t["l3"], 4.5),
    ("body text on page l1", t["text"], t["l1"], 4.5), ("body text on field", t["text"], t["field"], 4.5),
    ("body text on lit row l4", t["text"], t["l4"], 4.5), ("body text on indigo tint (chosen mode, tapped person)", t["text"], tint_l2, 4.5),
    ("muted text on l1", t["text-muted"], t["l1"], 4.5), ("muted text on l2", t["text-muted"], t["l2"], 4.5),
    ("muted text on l3", t["text-muted"], t["l3"], 4.5), ("muted text on l4", t["text-muted"], t["l4"], 4.5),
    ("muted text on field (placeholder)", t["text-muted"], t["field"], 4.5), ("muted text on indigo tint (proof work line)", t["text-muted"], tint_l3, 4.5),
    ("indigo text on l3 (+1 sen, status)", t["accent-ink"], t["l3"], 4.5), ("indigo text on l2", t["accent-ink"], t["l2"], 4.5),
    ("indigo text on l1", t["accent-ink"], t["l1"], 4.5), ("indigo text on tint over l3 (Copy summary, Adds up to)", t["accent-ink"], tint_l3, 4.5),
    ("indigo text on tint over l1", t["accent-ink"], tint_l1, 4.5),
    ("indigo outline on l3 (Copy summary edge)", t["accent-line"], t["l3"], 3.0), ("indigo outline on field (switch)", t["accent-line"], t["field"], 3.0),
    ("indigo outline on l1 (tapped person edge)", t["accent-line"], t["l1"], 3.0),
    ("control border on l1", t["line-strong"], t["l1"], 3.0), ("control border on l2", t["line-strong"], t["l2"], 3.0),
    ("control border on l3", t["line-strong"], t["l3"], 3.0), ("control border on field", t["line-strong"], t["field"], 3.0),
    ("focus ring on l1", t["focus"], t["l1"], 3.0), ("focus ring on l3", t["focus"], t["l3"], 3.0),
    ("error text on l1", t["error-ink"], t["l1"], 4.5), ("error text on l2", t["error-ink"], t["l2"], 4.5),
    ("Start new bill text on its tint", t["error-ink"], danger_l3, 4.5), ("Start new bill outline on l3", t["error-ink"], t["l3"], 3.0),
    ("warning text on warning band", t["text"], t["warn-bg"], 4.5), ("warning icon on warning band", t["warn-ink"], t["warn-bg"], 3.0),
    ("note text on info band", t["text"], t["info-bg"], 4.5),
]
for i in range(1, 13):
    p = t[f"p{i}"]
    pairs.append((f"p{i} on l3 (ring segment)", p, t["l3"], 3.0))
    pairs.append((f"p{i} on l1 (hollow person letter)", p, t["l1"], 4.5))
    pairs.append((f"tag text on p{i}", t["on-person"], p, 4.5))
for label, fg, bg, need in pairs:
    r = ratio(fg, bg)
    R["contrast"][label] = {"ratio": r, "need": need, "pass": r >= need}
    check(r >= need, f"contrast {label} {r} < {need}")
R["tokens"] = tokens

# ---------- no bright filled buttons ----------
bright = []
for where, lst in R["fills"].items():
    for b in lst:
        c = parse_colour(b["bg"])
        if c[3] >= 0.5 and lum(c) > 0.05:
            bright.append(f"{where}: {b['el']} {b['bg']}")
R["bright_fills"] = bright
check(not bright, f"bright filled buttons {bright}")
for where, small in R["targets"].items():
    check(not small, f"touch targets under 44 px at {where}: {small}")
check(not R["console_errors"] and not R["page_errors"], "console or page errors")
check(not R["network"], "network requests")
for k, v in R["arcs"].items():
    check(v < 0.0005, f"ring arcs off at {k}: {v}")

(HERE / "results.json").write_text(json.dumps(R, indent=2), encoding="utf-8")

# ---------- summary ----------
print("console errors:", len(R["console_errors"]), R["console_errors"][:5])
print("page errors:", len(R["page_errors"]), R["page_errors"][:5])
print("network:", R["network"])
print("dashes:", R["dashes"])
print("icons:", R["icons"])
for k, v in R["noscroll_1280"].items():
    print("noscroll", k, v)
for k, v in R["frame"].items():
    print("frame", k, v)
for k, v in R["overflow_360"].items():
    print("overflow360", k, v["scrollWidth"], v["clientWidth"], v["bad"])
for k, v in R["proto_tab"].items():
    print("proto", k, v)
print("order:", R["order"])
print("arcs:", R["arcs"])
for k, v in R["figures"].items():
    print("fig", k, "=>", json.dumps(v)[:300])
for k, v in R["contrast"].items():
    print("contrast", k, v["ratio"], "PASS" if v["pass"] else "FAIL")
print("bright fills:", R["bright_fills"])
print("targets:", R["targets"])
print("shots:", len(R["shots"]))
print("FAILS:", len(R["fails"]))
for f in R["fails"]:
    print("  FAIL", f)
