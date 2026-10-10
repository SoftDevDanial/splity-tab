"""Render checks for round-2 direction G (Glass Console).

Run: python -B check_g.py
Opens g.html by its file:/// URL in headless Chromium (scrollbars shown) at 390 x 844, 360 x 780 and 1280 x 800,
plus 768 x 1024 and reduced motion as extras. navigator.clipboard is replaced before load by a stand-in that only
records writes, and document.execCommand is wrapped to count any "copy". Every request that is not file: or data:
is aborted and logged. Writes results.json and the screenshots beside this script. Every wait is bounded and the
browser is closed in a finally block.
"""
import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROUND = HERE.parent.parent
PAGE = ROUND / "g.html"
NOTES = ROUND / "g.md"
URL = PAGE.as_uri()
SPLIT = ROUND.parents[3]
WAIT_MS = 4000

CLIP_STUB = """
(() => {
  window.__clipWrites = [];
  window.__clipFail = false;
  window.__execCopy = 0;
  const stub = {
    __stub: true,
    writeText(t) { if (window.__clipFail) return Promise.reject(new Error('blocked')); window.__clipWrites.push(String(t)); return Promise.resolve(); },
    write() { window.__clipWrites.push('[write]'); return Promise.resolve(); },
    readText() { return Promise.resolve(''); },
    read() { return Promise.resolve([]); },
  };
  Object.defineProperty(Navigator.prototype, 'clipboard', { get() { return stub; }, configurable: true });
  const ex = Document.prototype.execCommand;
  Document.prototype.execCommand = function (cmd, ...rest) {
    if (String(cmd).toLowerCase() === 'copy' || String(cmd).toLowerCase() === 'cut') { window.__execCopy++; return false; }
    return ex.call(this, cmd, ...rest);
  };
})();
"""

R = {"console_errors": [], "page_errors": [], "network": [], "fails": [], "figures": {}, "addup": {},
     "noscroll_1280": {}, "frame": {}, "overflow_360": {}, "strip": {}, "proto_tab": {}, "order": {},
     "contrast": {}, "icons": {}, "dashes": {}, "targets": {}, "clipboard": {}, "motion": {}, "shots": []}


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
R["dashes"]["g.html"] = {"em": src.count("—"), "en": src.count("–")}
check(src.count("—") == 0 and src.count("–") == 0, "long dashes in g.html")
if NOTES.exists():
    md = NOTES.read_text(encoding="utf-8")
    R["dashes"]["g.md"] = {"em": md.count("—"), "en": md.count("–")}
    check(md.count("—") == 0 and md.count("–") == 0, "long dashes in g.md")
ref = {}
for name, d in re.findall(r'(\w+): "(M[^"]+)"', (SPLIT / "src" / "ui" / "icons.js").read_text(encoding="utf-8")):
    ref[name] = d
for f in ("b.html", "a.html"):
    for sym, d in re.findall(r'<symbol id="i-([\w-]+)" viewBox="0 0 256 256"><path d="([^"]+)"', (ROUND.parent / "round-1" / f).read_text(encoding="utf-8")):
        ref.setdefault(sym, d)
for sym, d in re.findall(r'<symbol id="i-([\w-]+)" viewBox="0 0 256 256"><path d="([^"]+)"', src):
    R["icons"][sym] = "match" if ref.get(sym) == d else "MISMATCH"
    check(ref.get(sym) == d, f"icon {sym} differs from source")
check(src.count("<symbol") == len(R["icons"]), "a symbol was not compared")
check("https://" not in src and "http://" not in src.replace("http://www.w3.org/2000/svg", ""), "a remote URL in g.html")

# ---------- page helpers ----------
JS_ROWS = """() => [...document.querySelectorAll('#rbody .r-shares li')].map(li => ({
  name: li.querySelector('.nm').textContent,
  share: li.querySelector('.amt').textContent,
  wk: li.querySelector('.wk') ? li.querySelector('.wk').textContent.replace(/\\s+/g, ' ').trim() : null
}))"""
JS_RECEIPT = """() => { const t = (s) => { const e = document.querySelector(s); return e ? e.textContent.replace(/\\s+/g, ' ').trim() : null; };
  return { total: t('#rTotal'), lines: [...document.querySelectorAll('#rbody .r-lines > div')].map(d => d.querySelector('dt').textContent + ' = ' + d.querySelector('dd').textContent),
           proof: t('#addsUp'), proofWork: t('#rbody .r-check .wk'), spare: t('#spareLine'), rule: t('#spareBtn'), legend: t('#rbody .r-head span') }; }"""
JS_ADDUP = """() => { const c = (s) => s ? Number(String(s).replace(/[^0-9]/g, '')) : null;
  const shares = [...document.querySelectorAll('#rbody .r-shares .amt')].map(e => c(e.textContent));
  const t = document.querySelector('#rTotal'), p = document.querySelector('#addsUp');
  return { shares, sum: shares.reduce((a, b) => a + b, 0), total: t ? c(t.textContent) : null, proof: p ? c(p.textContent) : null }; }"""
JS_OVERFLOW = """() => {
  const vw = document.documentElement.clientWidth;
  const bad = [];
  for (const el of document.querySelectorAll('body *')) {
    if (el.closest('.sprite, .sr, dialog:not([open]), [hidden], title, #protoPanel')) continue;
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
           docScrollWidth: de.scrollWidth, stage: box('#stage'), work: box('#work'), frame: box('#itemList') };
}"""
JS_ORDER = """() => {
  const y = (sel) => { const e = document.querySelector(sel); return e && !e.hidden ? Math.round(e.getBoundingClientRect().top) : null; };
  return { people: y('#peopleBlk'), charges: y('#chargesBlk'), split: y('#splitBlk'), items: y('#itemsBlock') ?? y('#evenBlock'),
           receiptInSheet: !!document.querySelector('#sheetScroll #rbody'), receiptInCard: !!document.querySelector('#card #rbody'),
           stageShown: getComputedStyle(document.querySelector('#stage')).display !== 'none',
           stripShown: getComputedStyle(document.querySelector('#strip')).display !== 'none' };
}"""
# Content boxes the prototype tab must never cover. Structural wrappers that only hold padding are skipped.
JS_TAB = """() => {
  const tab = document.querySelector('#protoTab').getBoundingClientRect();
  const skip = new Set(['HTML', 'BODY', 'MAIN', 'SECTION', 'UL', 'OL']);
  const skipIds = new Set(['app', 'layout', 'work', 'stage', 'protoTab']);
  const hits = [];
  const hit = (a, b) => a.left < b.right - 0.5 && b.left < a.right - 0.5 && a.top < b.bottom - 0.5 && b.top < a.bottom - 0.5;
  for (const el of document.querySelectorAll('body *')) {
    if (el.closest('.sprite, .sr, dialog, [hidden], title, #protoPanel')) continue;
    if (skip.has(el.tagName) || skipIds.has(el.id)) continue;
    if (el.classList.contains('blk') || el.classList.contains('top')) continue;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    if (hit(tab, r)) hits.push((el.id ? '#' + el.id : el.tagName.toLowerCase() + '.' + (el.getAttribute('class') || '')) + ' ' + Math.round(r.left) + ',' + Math.round(r.top));
  }
  const strip = document.querySelector('#strip').getBoundingClientRect();
  const top = document.querySelector('.top').getBoundingClientRect();
  return { tab: [Math.round(tab.left), Math.round(tab.top), Math.round(tab.width), Math.round(tab.height)],
           hits: hits.slice(0, 10), strip: strip.height ? hit(tab, strip) : false, header: hit(tab, top) };
}"""
# Every control in the working that is visible (clipped by the item frame where it sits inside it) and touches the strip
JS_STRIP_OVERLAP = """() => {
  const s = document.querySelector('#strip').getBoundingClientRect();
  const fw = document.querySelector('#frameWrap').getBoundingClientRect();
  const hits = [];
  for (const el of document.querySelectorAll('#work input:not([type=radio]), #work button, #work .mode-sw label, #work .err:not([hidden]), #work .hint')) {
    if (el.closest('[hidden]')) continue;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    let top = r.top, bottom = r.bottom;
    if (el.closest('#frameWrap')) { top = Math.max(top, fw.top); bottom = Math.min(bottom, fw.bottom); if (bottom <= top) continue; }
    if (bottom > s.top + 0.5 && top < s.bottom) hits.push((el.id || el.getAttribute('aria-label') || el.textContent.trim().slice(0, 24)) + ' ' + Math.round(top) + '..' + Math.round(bottom));
  }
  return { stripTop: Math.round(s.top), scrollY: Math.round(window.scrollY), hits: hits.slice(0, 10) };
}"""
JS_FIRST_SCREEN = """() => {
  const s = document.querySelector('#strip').getBoundingClientRect().top;
  const b = (sel) => Math.round(document.querySelector(sel).getBoundingClientRect().bottom);
  return { stripTop: Math.round(s), people: b('#peopleBlk'), charges: b('#chargesBlk'), split: b('#splitBlk') };
}"""
JS_FOCUS = """() => {
  const a = document.activeElement;
  const inWork = document.querySelector('#work').contains(a);
  const box = a.type === 'radio' ? a.nextElementSibling : a;
  const r = box.getBoundingClientRect();
  const s = document.querySelector('#strip').getBoundingClientRect();
  const fw = document.querySelector('#frameWrap').getBoundingClientRect();
  let ok = r.top >= -0.5 && r.bottom <= s.top + 0.5;
  if (a.closest('#frameWrap')) ok = ok && r.top >= fw.top - 0.5 && r.bottom <= fw.bottom + 0.5;
  return { inWork, id: a.id || a.getAttribute('aria-label') || a.textContent.trim().slice(0, 30), top: Math.round(r.top), bottom: Math.round(r.bottom), stripTop: Math.round(s.top), ok };
}"""
JS_TARGETS = """() => {
  const small = [];
  for (const b of document.querySelectorAll('button, input, .mode-sw label, .choice, .pill-face')) {
    if (b.closest('#protoPanel, dialog:not([open]), [hidden]') || b.id === 'protoTab' || b.type === 'radio') continue;
    const r = b.getBoundingClientRect();
    if (!r.width) continue;
    if (r.height < 43.5 || r.width < 43.5) small.push((b.id || b.getAttribute('aria-label') || b.className || '') + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
  }
  return small;
}"""


def rows(page):
    return page.evaluate(JS_ROWS)


def shares(page):
    return [(r["name"], r["share"]) for r in rows(page)]


def settle(page, ms=150):
    page.wait_for_timeout(ms)


def run(page, key):
    page.evaluate(f"() => {{ if (document.activeElement) document.activeElement.blur(); window.__g.run('{key}'); }}")
    settle(page, 200)


JS_P1_COVER = """() => {
  const p = document.querySelector('#spareDlg').getBoundingClientRect();
  const s = document.querySelector('#shares').getBoundingClientRect();
  const box = document.querySelector('#sheetScroll');
  const inSheet = !!box.querySelector('#shares');
  const viewTop = inSheet ? box.getBoundingClientRect().top : 0;
  const covered = !(p.top >= s.bottom - 0.5 || p.left >= s.right - 0.5 || p.right <= s.left + 0.5);
  return { popTop: Math.round(p.top), popLeft: Math.round(p.left), sharesTop: Math.round(s.top), sharesBottom: Math.round(s.bottom), sharesRight: Math.round(s.right),
           covered, sharesVisible: s.top >= viewTop - 0.5 };
}"""


def p1_cover(page, label):
    v = page.evaluate(JS_P1_COVER)
    R["figures"][f"P1 vs shares, {label}"] = v
    check(not v["covered"] and v["sharesVisible"], f"P1 covers or hides the shares at {label}: {v}")


def shot(page, name, full=False):
    path = HERE / f"{name}.png"
    page.screenshot(path=str(path), full_page=full)
    R["shots"].append(path.name)


def text(page, sel):
    return page.eval_on_selector(sel, "e => e.textContent.replace(/\\s+/g, ' ').trim()")


def is_open(page, sel):
    return page.eval_on_selector(sel, "d => d.open")


def addup(page, label):
    v = page.evaluate(JS_ADDUP)
    R["addup"][label] = v
    check(v["shares"] and v["sum"] == v["total"] == v["proof"], f"shares do not add up at {label}: {v}")
    return v


def noscroll(page, label):
    v = page.evaluate(JS_NOSCROLL)
    R["noscroll_1280"][label] = v
    check(v["docScrollHeight"] <= v["viewport"] and v["bodyScrollHeight"] <= v["viewport"], f"1280 {label}: page scrolls ({v['docScrollHeight']})")
    check(v["stage"]["scrollHeight"] <= v["stage"]["clientHeight"], f"1280 {label}: receipt column overflows {v['stage']}")
    check(v["work"]["scrollHeight"] <= v["work"]["clientHeight"], f"1280 {label}: input column overflows {v['work']}")


def tab_check(page, label):
    v = page.evaluate(JS_TAB)
    R["proto_tab"][label] = v
    check(not v["hits"] and not v["strip"] and not v["header"], f"proto tab overlaps content at {label}: {v}")


def overflow360(page, label):
    v = page.evaluate(JS_OVERFLOW)
    R["overflow_360"][label] = v
    check(v["scrollWidth"] <= v["clientWidth"] and not v["bad"], f"360 {label}: sideways overflow {v}")


def strip_checks(page, label, first_screen=True):
    """The strip never covers the inputs: the first screen (a three-person bill), the page end, and every control
    while it has focus. With twelve people the first screen is recorded only, since People alone fill it."""
    page.evaluate("window.scrollTo(0, 0)")
    settle(page, 80)
    first = page.evaluate(JS_FIRST_SCREEN)
    out = {"first_screen": first, "first_screen_asserted": first_screen}
    if first_screen:
        check(first["people"] <= first["stripTop"] and first["charges"] <= first["stripTop"] and first["split"] <= first["stripTop"],
              f"{label}: People, Charges or Split under the strip on the first screen {first}")
    page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
    settle(page, 80)
    end = page.evaluate(JS_STRIP_OVERLAP)
    out["page_end"] = end
    check(not end["hits"], f"{label}: the strip covers a control at the page end {end}")
    # keyboard: Tab through every control in the working, each must sit above the strip while focused
    page.evaluate("window.scrollTo(0, 0)")
    page.focus("#newBill")
    bad, seen = [], 0
    for _ in range(220):
        page.keyboard.press("Tab")
        page.wait_for_timeout(45)
        f = page.evaluate(JS_FOCUS)
        if f["id"] in ("sharesBtn", "stripCopy"):
            break
        if not f["inWork"]:
            continue
        seen += 1
        if not f["ok"]:
            bad.append(f)
    out["tabbed_controls"] = seen
    out["covered_while_focused"] = bad[:8]
    check(seen > 5 and not bad, f"{label}: a focused control sat under the strip {bad[:3]} (seen {seen})")
    R["strip"][label] = out
    page.evaluate("window.scrollTo(0, 0)")


K1_ROWS = [
    {"name": "Aisyah", "share": "RM 29.04", "wk": "Items 24.90 + charges 4.14"},
    {"name": "Ben", "share": "RM 15.74", "wk": "Items 13.50 + charges 2.24"},
    {"name": "Chen", "share": "RM 24.48", "wk": "Items 21.00 + charges 3.48"},
]
K1_LINES = ["Subtotal = RM 59.40", "Service 10% = RM 5.94", "SST 6% = RM 3.92"]
K2_LINES = ["Subtotal = RM 100.00", "Service 10% = RM 10.00", "SST 6% = RM 6.60"]


def figures_k1(page, where):
    got = rows(page)
    R["figures"][f"K1 rows {where}"] = got
    check(got == K1_ROWS, f"K1 rows {where}: {got}")
    rc = page.evaluate(JS_RECEIPT)
    R["figures"][f"K1 receipt {where}"] = rc
    check(rc["total"] == "RM 69.26", f"K1 total {where}: {rc['total']}")
    check(rc["lines"] == K1_LINES, f"K1 lines {where}: {rc['lines']}")
    check(rc["proof"] == "RM 69.26" and rc["proofWork"] == "59.40 + 9.86", f"K1 adds up {where}: {rc}")
    check(rc["spare"] == "1 sen left over" and rc["rule"] == "Top of the list", f"K1 spare {where}: {rc}")
    check(rc["legend"] == "items + charges", f"K1 legend {where}: {rc['legend']}")
    addup(page, f"K1 {where}")


def figures_k2(page, where):
    got = shares(page)
    R["figures"][f"K2 shares {where}"] = got
    check(got == [("Aisyah", "RM 38.87"), ("Ben", "RM 38.87"), ("Chen", "RM 38.86")], f"K2 shares {where}: {got}")
    rc = page.evaluate(JS_RECEIPT)
    R["figures"][f"K2 receipt {where}"] = rc
    check(rc["total"] == "RM 116.60" and rc["lines"] == K2_LINES, f"K2 bill {where}: {rc}")
    check(rc["spare"] == "2 sen left over" and rc["rule"] == "Top of the list", f"K2 spare {where}: {rc}")
    addup(page, f"K2 {where}")


def p1_one_ben(page, expect, label):
    page.click("#spareBtn")
    page.wait_for_selector("#spareDlg[open]")
    settle(page, 250)
    page.click('label.choice:has(input[value="one"])')
    settle(page)
    p1_cover(page, f"{label} picker open")
    page.click('#pickList label:has(input[value="2"]) .pill-face')
    settle(page)
    p1_cover(page, f"{label} one Ben")
    got = shares(page)
    R["figures"][f"{label} one Ben"] = got
    check(got == expect, f"{label} one Ben {got}")
    check(page.evaluate("document.querySelector('#spareBtn').textContent.trim()") == "One person, Ben", f"{label} chip after one Ben")
    addup(page, f"{label} one Ben")


def p1_random(page, label, floor, people_with_sen, pick_sel):
    """floor: each person's share in cents before any spare sen. Every draw must give exactly people_with_sen
    different people one sen each, and Pick again must change who."""
    page.click('label.choice:has(input[value="random"])')
    settle(page)
    p1_cover(page, f"{label} at random")
    draws = []
    for i in range(12):
        v = addup(page, f"{label} random draw {i + 1}")
        draws.append(v["shares"])
        page.click(pick_sel)
        settle(page, 80)
    R["figures"][f"{label} random draws"] = draws
    names = [n for n, s in shares(page)]
    got_sen = [tuple(names[j] for j, x in enumerate(d) if x - floor[j] == 1) for d in draws]
    extra = [[x - floor[j] for j, x in enumerate(d)] for d in draws]
    R["figures"][f"{label} random recipients"] = got_sen
    check(all(sorted(e) == sorted([1] * people_with_sen + [0] * (len(floor) - people_with_sen)) for e in extra), f"{label} random: not one sen each to {people_with_sen} people {extra}")
    check(len(set(got_sen)) > 1, f"{label} random: the pick never changed {got_sen}")
    check(all(got_sen[i] != got_sen[i + 1] for i in range(len(got_sen) - 1)), f"{label} random: Pick again repeated the same pick {got_sen}")
    return draws


def clip_audit(page, label):
    v = page.evaluate("() => ({ stub: !!(navigator.clipboard && navigator.clipboard.__stub), execCopy: window.__execCopy, standInWrites: window.__clipWrites.length })")
    R["clipboard"][label] = v
    check(v["stub"] and v["execCopy"] == 0, f"clipboard audit {label}: {v}")


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
            pg.on("request", lambda rq: R["network"].append(rq.url) if not (rq.url.startswith("file:") or rq.url.startswith("data:")) and rq.url not in R["network"] else None)
            pg.goto(URL, wait_until="load")
            settle(pg, 300)
            return ctx, pg

        # ================= 390 x 844 =================
        ctx, page = new_page(390, 844, phone=True)
        shot(page, "k1-390")
        shot(page, "k1-390-full", full=True)
        R["figures"]["title"] = page.title()
        check(page.title() == "Danial's Splity Tab", f"title {page.title()}")
        R["figures"]["header"] = text(page, ".top .brand")
        check(R["figures"]["header"] == "Splity Tab", f"header text {R['figures']['header']}")
        o = page.evaluate(JS_ORDER)
        R["order"]["390"] = o
        check(o["people"] < o["charges"] < o["split"] < o["items"], f"390 input order {o}")
        check(o["receiptInSheet"] and not o["stageShown"] and o["stripShown"], f"390 receipt placement {o}")
        R["figures"]["K1 strip 390"] = text(page, "#stripInfo")
        check(R["figures"]["K1 strip 390"] == "TotalRM 69.26", f"K1 strip total {R['figures']['K1 strip 390']}")
        figures_k1(page, "390 (sheet content)")
        tab_check(page, "390 K1 top")
        page.evaluate("window.scrollTo(0, 400)")
        settle(page, 80)
        tab_check(page, "390 K1 scrolled 400")
        shot(page, "k1-390-scrolled")
        strip_checks(page, "390 K1")
        R["targets"]["390 K1"] = page.evaluate(JS_TARGETS)

        # P2 Shares sheet from the strip
        page.click("#sharesBtn")
        page.wait_for_selector("#sharesDlg[open]")
        settle(page, 350)
        shot(page, "p2-390")
        check(page.evaluate("document.querySelector('#sharesBtn').getAttribute('aria-expanded')") == "true", "Shares aria-expanded")
        figures_k1(page, "390 sheet")
        R["targets"]["390 P2"] = page.evaluate(JS_TARGETS)
        page.eval_on_selector("#sheetScroll", "e => e.scrollTop = e.scrollHeight")
        settle(page)
        shot(page, "p2-390-bottom")
        page.eval_on_selector("#sheetScroll", "e => e.scrollTop = 0")
        # Copy summary inside the sheet writes the 1.0 text to the stand-in clipboard
        page.click("#copyBtn")
        settle(page)
        clip = page.evaluate("window.__clipWrites")
        R["clipboard"]["K1 summary text"] = clip[-1] if clip else None
        check(clip and clip[-1] == "Bill split\nTotal RM 69.26 (subtotal RM 59.40, service 10% RM 5.94, SST 6% RM 3.92)\nAisyah RM 29.04\nBen RM 15.74\nChen RM 24.48\nAdds up to RM 69.26", f"K1 summary text {clip}")
        check(text(page, "#cardStatus") == "Summary copied", "S4 copied status in the sheet")
        shot(page, "s4-copied-in-sheet-390")
        # P1 from the sheet: One person, Ben
        p1_one_ben(page, [("Aisyah", "RM 29.03"), ("Ben", "RM 15.75"), ("Chen", "RM 24.48")], "K1 390")
        shot(page, "p1-one-ben-390")
        check(is_open(page, "#sharesDlg"), "the sheet stays open under P1")
        page.click('label.choice:has(input[value="one"])')
        settle(page)
        shot(page, "p1-picker-390")
        p1_random(page, "K1 390", [2903, 1574, 2448], 1, "#pickAgainSheet")
        shot(page, "p1-random-390")
        # Esc closes P1 first, then the sheet. Backdrop and Close shut the sheet
        page.keyboard.press("Escape")
        settle(page)
        check(not is_open(page, "#spareDlg") and is_open(page, "#sharesDlg"), "Esc closes P1 only")
        shot(page, "k1-random-sheet-390")
        page.click("#spareBtn")
        page.wait_for_selector("#spareDlg[open]")
        settle(page, 250)
        page.click('label.choice:has(input[value="top"])')
        settle(page)
        shot(page, "p1-390")
        page.mouse.click(195, 30)
        settle(page)
        check(not is_open(page, "#spareDlg"), "backdrop closes P1")
        page.keyboard.press("Escape")
        settle(page)
        check(not is_open(page, "#sharesDlg"), "Esc closes the sheet")
        check(page.evaluate("document.activeElement.id") == "sharesBtn", "focus returns to Shares")
        page.click("#sharesBtn")
        page.wait_for_selector("#sharesDlg[open]")
        page.mouse.click(195, 20)
        settle(page)
        check(not is_open(page, "#sharesDlg"), "backdrop closes the sheet")
        page.click("#sharesBtn")
        page.wait_for_selector("#sharesDlg[open]")
        page.click("#sharesDlg [data-close]")
        settle(page)
        check(not is_open(page, "#sharesDlg"), "Close shuts the sheet")
        tab_check(page, "390 tab with the sheet closed")

        # K2 by the design's own switch
        run(page, "k1")
        page.click("label[for=modeEven]")
        settle(page)
        figures_k2(page, "390 via switch")
        R["figures"]["K2 strip 390"] = text(page, "#stripInfo")
        check(R["figures"]["K2 strip 390"] == "TotalRM 116.60", f"K2 strip {R['figures']['K2 strip 390']}")
        shot(page, "k2-390")
        page.click("#sharesBtn")
        page.wait_for_selector("#sharesDlg[open]")
        settle(page, 350)
        shot(page, "p2-k2-390")
        p1_one_ben(page, [("Aisyah", "RM 38.86"), ("Ben", "RM 38.88"), ("Chen", "RM 38.86")], "K2 390")
        shot(page, "p1-k2-one-ben-390")
        p1_random(page, "K2 390", [3886, 3886, 3886], 2, "#pickAgainSheet")
        shot(page, "p1-k2-random-390")
        page.keyboard.press("Escape")
        settle(page)
        shot(page, "k2-random-sheet-390")
        page.keyboard.press("Escape")
        settle(page)

        # M1
        run(page, "k1")
        page.click("#newBill")
        page.wait_for_selector("#newDlg[open]")
        settle(page, 250)
        shot(page, "m1-390")
        R["figures"]["M1"] = text(page, "#newDlg")
        check(R["figures"]["M1"] == "Start a new bill? This clears the people, items and amounts. Start new bill Cancel", f"M1 {R['figures']['M1']}")
        R["targets"]["390 M1"] = page.evaluate(JS_TARGETS)
        page.keyboard.press("Escape")
        settle(page)
        check(not is_open(page, "#newDlg"), "Esc closes M1")
        page.click("#newBill")
        page.wait_for_selector("#newDlg[open]")
        page.mouse.click(10, 10)
        settle(page)
        check(not is_open(page, "#newDlg"), "backdrop closes M1")
        page.click("#newBill")
        page.click("#newDlg [data-close]")
        settle(page)
        check(not is_open(page, "#newDlg"), "Cancel closes M1")
        page.click("#newBill")
        page.click("#startNew")
        settle(page, 200)
        s1 = page.evaluate("""() => ({ people: [...document.querySelectorAll('#peopleList input')].map(i => i.value), even: document.querySelector('#modeEven').checked,
            subtotal: document.querySelector('#evenSub').value, svc: document.querySelector('#svc').value, sst: document.querySelector('#sst').value,
            strip: document.querySelector('#stripInfo').textContent.trim(), receipt: document.querySelector('#rbody').textContent.replace(/\\s+/g, ' ').trim(),
            copyDisabled: document.querySelector('#stripCopy').disabled })""")
        R["figures"]["S1 via Start new bill"] = s1
        check(s1 == {"people": ["Person 1", "Person 2"], "even": True, "subtotal": "", "svc": "10", "sst": "6",
                     "strip": "Enter the subtotal to see the shares.", "receipt": "TotalEnter the subtotal to see the shares.", "copyDisabled": True}, f"S1 {s1}")
        shot(page, "s1-390")
        page.click("#sharesBtn")
        page.wait_for_selector("#sharesDlg[open]")
        settle(page, 350)
        shot(page, "s1-sheet-390")
        page.keyboard.press("Escape")
        settle(page)

        # States with no natural trigger
        run(page, "s2")
        R["figures"]["S2"] = text(page, "#evenBlock")
        check("Enter an amount like 12.50" in R["figures"]["S2"] and page.eval_on_selector("#evenErr", "e => !e.hidden"), "S2 error copy")
        shot(page, "s2-390")
        run(page, "s3")
        R["figures"]["S3 strip"] = text(page, "#stripInfo")
        R["figures"]["S3 receipt"] = text(page, "#rbody .r-msg")
        msg3 = "1 item still needs a person. Tap who had it to see the shares."
        check(R["figures"]["S3 strip"] == msg3 and R["figures"]["S3 receipt"] == msg3, "S3 copy")
        check(page.evaluate("document.querySelector('#stripCopy').disabled"), "S3 copy disabled")
        check(page.evaluate("document.querySelector('.item[data-item=\"3\"]').classList.contains('needs')"), "S3 marker on Mee goreng mamak")
        page.eval_on_selector("#itemsBlock", "e => e.scrollIntoView({ block: 'start' })")
        settle(page)
        shot(page, "s3-390")
        page.click("#sharesBtn")
        page.wait_for_selector("#sharesDlg[open]")
        settle(page, 350)
        shot(page, "s3-sheet-390")
        page.keyboard.press("Escape")
        settle(page)
        run(page, "s4ok")
        R["figures"]["S4 copied (strip)"] = text(page, "#stripStatus")
        check(R["figures"]["S4 copied (strip)"] == "Summary copied", "S4 copied in the strip")
        shot(page, "s4-copied-390")
        run(page, "s4fail")
        R["figures"]["S4 blocked (strip)"] = text(page, "#stripStatus")
        check(R["figures"]["S4 blocked (strip)"] == "Could not copy. Your browser blocked the clipboard.", "S4 blocked copy")
        shot(page, "s4-blocked-390")
        # the blocked path through the real button
        run(page, "k1")
        page.evaluate("window.__clipFail = true")
        page.click("#stripCopy")
        settle(page)
        check(text(page, "#stripStatus") == "Could not copy. Your browser blocked the clipboard.", "S4 blocked by the strip button")
        page.evaluate("window.__clipFail = false")
        page.click("#stripCopy")
        settle(page)
        check(text(page, "#stripStatus") == "Summary copied", "S4 copied by the strip button")
        run(page, "s5")
        R["figures"]["S5"] = text(page, "#notes")
        check(R["figures"]["S5"] == "This bill is not being saved on this device. It will be lost when you close this tab.", "S5 copy")
        tab_check(page, "390 S5")
        shot(page, "s5-390")
        run(page, "s6")
        R["figures"]["S6"] = text(page, "#notes")
        check(R["figures"]["S6"] == "Your saved bill could not be read, so a new one was started.", "S6 copy")
        shot(page, "s6-390")
        page.click("#dismissNote")
        settle(page)
        check(text(page, "#notes") == "", "S6 dismiss")
        run(page, "s7")
        check(page.eval_on_selector("#addPerson", "b => b.disabled"), "S7 add person disabled")
        check(page.evaluate("document.querySelectorAll('#peopleList .person').length") == 12, "S7 has 12 people")
        addup(page, "S7 390")
        R["figures"]["S7 spare"] = text(page, "#spareLine")
        shot(page, "s7-390-full", full=True)
        strip_checks(page, "390 S7", first_screen=False)
        run(page, "w1")
        R["figures"]["W1 strip 390"] = text(page, "#stripInfo")
        check(R["figures"]["W1 strip 390"] == "TotalRM 1,193.87", f"W1 strip {R['figures']['W1 strip 390']}")
        addup(page, "W1 390")
        shot(page, "w1-390")
        # W2 at 390: the item frame scrolls inside itself
        run(page, "w2")
        addup(page, "W2 390")
        fr = page.evaluate("() => { const f = document.querySelector('#itemList'); return { sh: f.scrollHeight, ch: f.clientHeight, down: document.querySelector('#frameWrap').hasAttribute('data-down') }; }")
        R["frame"]["W2 390"] = fr
        check(fr["sh"] > fr["ch"] and fr["down"], f"W2 390 frame does not scroll {fr}")
        page.eval_on_selector("#itemsBlock", "e => e.scrollIntoView({ block: 'start' })")
        page.eval_on_selector("#itemList", "e => e.scrollTop = 360")
        settle(page, 250)
        fr2 = page.evaluate("() => ({ top: document.querySelector('#itemList').scrollTop, up: document.querySelector('#frameWrap').hasAttribute('data-up'), down: document.querySelector('#frameWrap').hasAttribute('data-down') })")
        R["frame"]["W2 390 scrolled"] = fr2
        check(fr2["top"] > 0 and fr2["up"] and fr2["down"], f"W2 390 frame fades {fr2}")
        shot(page, "w2-390")
        tab_check(page, "390 W2 scrolled to items")
        strip_checks(page, "390 W2")
        R["figures"]["W2 (prototype only)"] = {"rows": rows(page), "receipt": page.evaluate(JS_RECEIPT)}

        # Prototype panel open
        run(page, "k1")
        page.click("#protoTab")
        settle(page)
        shot(page, "proto-panel-390")
        pp = page.evaluate("() => { const p = document.querySelector('#protoPanel').getBoundingClientRect(); const d = document.querySelector('#strip').getBoundingClientRect(); return { bottom: p.bottom, stripTop: d.top }; }")
        R["proto_tab"]["390 panel vs strip"] = pp
        check(pp["bottom"] <= pp["stripTop"], f"proto panel overlaps the strip {pp}")
        page.click("#protoClose")
        # the tab sits under an open popup's backdrop
        for dlg, opener in (("#newDlg", "#newBill"), ("#sharesDlg", "#sharesBtn")):
            page.click(opener)
            page.wait_for_selector(f"{dlg}[open]")
            under = page.evaluate("() => { const r = document.querySelector('#protoTab').getBoundingClientRect(); const e = document.elementFromPoint(r.left + 7, r.top + r.height / 2); return e ? (e.id || e.tagName) : null; }")
            R["proto_tab"][f"390 under backdrop of {dlg}"] = under
            check(under != "protoTab", f"proto tab above the backdrop of {dlg}")
            page.keyboard.press("Escape")
            settle(page)
        clip_audit(page, "390 run")
        ctx.close()

        # ================= 360 x 780 =================
        ctx, page = new_page(360, 780)
        shot(page, "k1-360")
        overflow360(page, "K1")
        tab_check(page, "360 K1")
        for key in ["k2", "s1", "s2", "s3", "s4ok", "s4fail", "s5", "s6", "s7", "w1", "w2"]:
            run(page, key)
            overflow360(page, key.upper())
            tab_check(page, f"360 {key.upper()}")
        run(page, "s5")
        shot(page, "s5-360")
        run(page, "k1")
        strip_checks(page, "360 K1")
        run(page, "w2")
        strip_checks(page, "360 W2")
        run(page, "s7")
        strip_checks(page, "360 S7", first_screen=False)
        run(page, "w1")
        R["figures"]["W1 strip 360"] = text(page, "#stripInfo")
        check(R["figures"]["W1 strip 360"] == "TotalRM 1,193.87", f"W1 strip 360 {R['figures']['W1 strip 360']}")
        page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        settle(page)
        overflow360(page, "W1 page end")
        shot(page, "w1-360")
        page.click("#sharesBtn")
        page.wait_for_selector("#sharesDlg[open]")
        settle(page, 350)
        overflow360(page, "W1 sheet")
        R["figures"]["W1 sheet rows"] = rows(page)
        R["figures"]["W1 receipt"] = page.evaluate(JS_RECEIPT)
        check(R["figures"]["W1 receipt"]["total"] == "RM 1,193.87", "W1 total in the sheet")
        check([r["share"] for r in R["figures"]["W1 sheet rows"]][0] == "RM 1,153.65", f"W1 Aisyah share {R['figures']['W1 sheet rows']}")
        coll = page.evaluate("""() => { const out = []; const hit = (a, b) => a.left < b.right - 0.5 && b.left < a.right - 0.5 && a.top < b.bottom - 0.5 && b.top < a.bottom - 0.5;
          for (const row of document.querySelectorAll('#rbody .r-shares li, #rbody .r-check, #rbody .r-lines > div')) { const p = [...row.children];
            for (let i = 0; i < p.length; i++) for (let j = i + 1; j < p.length; j++) if (hit(p[i].getBoundingClientRect(), p[j].getBoundingClientRect())) out.push(row.textContent); }
          const a = document.querySelector('#rTotal'); if (a && a.scrollWidth > a.clientWidth + 0.5) out.push('total figure too wide');
          return out; }""")
        R["figures"]["W1 360 collisions"] = coll
        check(not coll, f"W1 360 collisions {coll}")
        shot(page, "w1-360-sheet")
        page.keyboard.press("Escape")
        settle(page)
        run(page, "k1")
        page.click("#sharesBtn")
        page.wait_for_selector("#sharesDlg[open]")
        settle(page, 350)
        overflow360(page, "P2")
        shot(page, "p2-360")
        page.click("#spareBtn")
        page.wait_for_selector("#spareDlg[open]")
        settle(page, 250)
        overflow360(page, "P1")
        p1_cover(page, "360 open")
        shot(page, "p1-360")
        page.click('label.choice:has(input[value="one"])')
        settle(page)
        overflow360(page, "P1 picker")
        p1_cover(page, "360 picker open")
        shot(page, "p1-picker-360")
        page.keyboard.press("Escape")
        page.keyboard.press("Escape")
        settle(page)
        page.click("#newBill")
        page.wait_for_selector("#newDlg[open]")
        settle(page, 250)
        overflow360(page, "M1")
        shot(page, "m1-360")
        page.keyboard.press("Escape")
        settle(page)
        page.click("#protoTab")
        settle(page)
        overflow360(page, "proto panel open")
        pp = page.evaluate("() => { const p = document.querySelector('#protoPanel').getBoundingClientRect(); const d = document.querySelector('#strip').getBoundingClientRect(); return { bottom: p.bottom, stripTop: d.top }; }")
        R["proto_tab"]["360 panel vs strip"] = pp
        check(pp["bottom"] <= pp["stripTop"], f"360 proto panel overlaps the strip {pp}")
        page.click("#protoClose")
        R["targets"]["360 K1"] = page.evaluate(JS_TARGETS)
        clip_audit(page, "360 run")
        ctx.close()

        # ================= 1280 x 800 =================
        ctx, page = new_page(1280, 800)
        shot(page, "k1-1280")
        figures_k1(page, "1280")
        noscroll(page, "K1")
        o = page.evaluate(JS_ORDER)
        R["order"]["1280"] = o
        check(o["people"] < o["charges"] < o["split"] < o["items"], f"1280 input order {o}")
        check(o["receiptInCard"] and o["stageShown"] and not o["stripShown"], f"1280 receipt placement {o}")
        tab_check(page, "1280 K1")
        R["targets"]["1280 K1"] = page.evaluate(JS_TARGETS)
        fr = page.evaluate("() => { const f = document.querySelector('#itemList'); return { sh: f.scrollHeight, ch: f.clientHeight, down: document.querySelector('#frameWrap').hasAttribute('data-down') }; }")
        R["frame"]["K1 1280"] = fr
        page.click("#spareBtn")
        page.wait_for_selector("#spareDlg[open]")
        settle(page, 250)
        shot(page, "p1-1280")
        pop = page.evaluate("() => { const p = document.querySelector('#spareDlg').getBoundingClientRect(); const s = document.querySelector('#shares').getBoundingClientRect(); return { popLeft: p.left, sharesRight: s.right }; }")
        R["figures"]["P1 1280 beside the card"] = pop
        check(pop["popLeft"] >= pop["sharesRight"], f"P1 covers the shares at 1280 {pop}")
        page.keyboard.press("Escape")
        settle(page)
        p1_one_ben(page, [("Aisyah", "RM 29.03"), ("Ben", "RM 15.75"), ("Chen", "RM 24.48")], "K1 1280")
        shot(page, "p1-picker-1280")
        page.keyboard.press("Escape")
        settle(page)
        shot(page, "k1-one-ben-1280")
        page.click("#spareBtn")
        page.wait_for_selector("#spareDlg[open]")
        p1_random(page, "K1 1280", [2903, 1574, 2448], 1, "#pickAgainSheet")
        page.keyboard.press("Escape")
        settle(page)
        shot(page, "k1-random-1280")
        page.click("#newBill")
        page.wait_for_selector("#newDlg[open]")
        settle(page, 250)
        shot(page, "m1-1280")
        page.keyboard.press("Escape")
        settle(page)
        run(page, "k2")
        figures_k2(page, "1280")
        noscroll(page, "K2")
        shot(page, "k2-1280")
        page.click("#spareBtn")
        page.wait_for_selector("#spareDlg[open]")
        p1_random(page, "K2 1280", [3886, 3886, 3886], 2, "#pickAgainSheet")
        shot(page, "p1-k2-random-1280")
        page.keyboard.press("Escape")
        settle(page)
        run(page, "s7")
        noscroll(page, "S7")
        addup(page, "S7 1280")
        R["figures"]["S7 1280 shares"] = shares(page)
        R["figures"]["S7 spare 1280"] = text(page, "#spareLine")
        check(page.eval_on_selector("#addPerson", "b => b.disabled"), "S7 1280 add person disabled")
        shot(page, "s7-1280")
        run(page, "w2")
        noscroll(page, "W2")
        addup(page, "W2 1280")
        fr = page.evaluate("() => { const f = document.querySelector('#itemList'); return { sh: f.scrollHeight, ch: f.clientHeight, down: document.querySelector('#frameWrap').hasAttribute('data-down'), up: document.querySelector('#frameWrap').hasAttribute('data-up') }; }")
        R["frame"]["W2 1280"] = fr
        check(fr["sh"] > fr["ch"] and fr["down"] and not fr["up"], f"W2 1280 frame does not show it scrolls {fr}")
        shot(page, "w2-1280")
        page.hover("#itemList")
        page.mouse.wheel(0, 500)
        settle(page, 300)
        fr2 = page.evaluate("() => ({ top: document.querySelector('#itemList').scrollTop, winY: window.scrollY, up: document.querySelector('#frameWrap').hasAttribute('data-up') })")
        R["frame"]["W2 1280 after wheel"] = fr2
        check(fr2["top"] > 0 and fr2["winY"] == 0 and fr2["up"], f"W2 1280 wheel scrolls the frame, not the page {fr2}")
        noscroll(page, "W2 after the frame scrolled")
        shot(page, "w2-1280-scrolled")
        R["figures"]["W2 1280 rows (prototype only)"] = rows(page)
        R["figures"]["W2 1280 receipt (prototype only)"] = page.evaluate(JS_RECEIPT)
        for key in ["s1", "s2", "s3", "s4ok", "s4fail", "s5", "s6", "w1"]:
            run(page, key)
            noscroll(page, key.upper() + " (extra)")
            shot(page, f"{key}-1280")
        run(page, "s5")
        tab_check(page, "1280 S5")
        # keyboard focus is visible on Copy summary
        run(page, "k1")
        page.focus("#spareBtn")
        page.keyboard.press("Tab")
        settle(page, 100)
        R["figures"]["focus after the spare chip"] = page.evaluate("document.activeElement.id")
        R["figures"]["focus outline"] = page.evaluate("getComputedStyle(document.activeElement).outlineStyle + ' ' + getComputedStyle(document.activeElement).outlineColor")
        check(R["figures"]["focus after the spare chip"] == "copyBtn" and R["figures"]["focus outline"].startswith("solid"), "focus ring on Copy summary")
        shot(page, "focus-copy-1280")
        page.click("#protoTab")
        settle(page)
        shot(page, "proto-panel-1280")
        page.click("#protoClose")
        tokens = page.evaluate("""() => { const cs = getComputedStyle(document.documentElement); const out = {};
          for (const n of ['l0','l1','l2','l3','l4','l5','field','line-strong','line-glass','text','text-muted','text-faint','accent','accent-hover','accent-ink','accent-line','accent-tint',
                           'on-accent','danger','danger-hover','on-danger','error-ink','warn-ink','warn-bg','info-bg','focus','scrim','scrim-light',
                           'glass-hi','glass-mid','glass-lo','glass-base','glass-dense','glass-solid','glass-edge','hair','total-ink'])
            out[n] = cs.getPropertyValue('--' + n).trim();
          return out; }""")
        glass_css = page.evaluate("() => ({ card: getComputedStyle(document.querySelector('#card')).backdropFilter, bodyBg: getComputedStyle(document.body).backgroundImage, cardBefore: getComputedStyle(document.querySelector('#card'), '::before').content, stageBefore: getComputedStyle(document.querySelector('#stage'), '::before').content })")
        R["figures"]["no glow (computed)"] = glass_css
        check(glass_css["bodyBg"] == "none", f"page background has an image {glass_css}")
        check(glass_css["cardBefore"] in ("none", "normal") and glass_css["stageBefore"] in ("none", "normal"), f"a light pool pseudo element {glass_css}")
        clip_audit(page, "1280 run")
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
        settle(page, 350)
        shot(page, "p2-768")
        page.click("#spareBtn")
        page.wait_for_selector("#spareDlg[open]")
        settle(page, 250)
        p1_cover(page, "768 open")
        shot(page, "p1-768")
        page.click('label.choice:has(input[value="one"])')
        settle(page)
        p1_cover(page, "768 picker open")
        shot(page, "p1-picker-768")
        ctx.close()

        # ================= reduced motion and reduced transparency =================
        ctx, page = new_page(1280, 800, reduced=True)
        R["motion"]["reduced: card foil animation"] = page.evaluate("getComputedStyle(document.querySelector('#card > .foil')).animationName")
        R["motion"]["reduced: card sheen animation"] = page.evaluate("getComputedStyle(document.querySelector('#card'), '::after').animationName")
        check(R["motion"]["reduced: card foil animation"] == "none" and R["motion"]["reduced: card sheen animation"] == "none", "reduced motion still animates")
        try:
            cdp = ctx.new_cdp_session(page)
            cdp.send("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-reduced-transparency", "value": "reduce"}]})
            settle(page, 150)
            rt = page.evaluate("() => ({ matches: matchMedia('(prefers-reduced-transparency: reduce)').matches, filter: getComputedStyle(document.querySelector('#card')).backdropFilter, bg: getComputedStyle(document.querySelector('#card')).backgroundColor })")
            R["motion"]["reduced transparency"] = rt
            if rt["matches"]:
                check(rt["filter"] == "none", f"reduced transparency keeps the blur {rt}")
            shot(page, "k1-1280-reduced-motion-and-transparency")
        except Exception as e:  # emulation not supported: recorded, not failed
            R["motion"]["reduced transparency"] = f"not emulated: {e}"
        ctx.close()
        ctx, page = new_page(390, 844, reduced=True, phone=True)
        page.click("#sharesBtn")
        page.wait_for_selector("#sharesDlg[open]")
        R["motion"]["reduced: sheet animation"] = page.evaluate("getComputedStyle(document.querySelector('#sharesDlg .sheet')).animationName")
        check(R["motion"]["reduced: sheet animation"] == "none", "reduced motion still slides the sheet")
        ctx.close()
    finally:
        browser.close()

# ---------- clipboard ----------
audits = [v for k, v in R["clipboard"].items() if isinstance(v, dict) and "stub" in v]
R["clipboard"]["stand-in writes, all runs"] = sum(v["standInWrites"] for v in audits)
R["clipboard"]["real clipboard writes"] = 0 if audits and all(v["stub"] and v["execCopy"] == 0 for v in audits) else "UNPROVEN"
check(R["clipboard"]["real clipboard writes"] == 0, "real clipboard writes not proven 0")

# ---------- contrast table, from the page's own tokens ----------
t = {k: parse_colour(v) for k, v in tokens.items()}
l1, l2, l3, field = t["l1"], t["l2"], t["l3"], t["field"]
tint_l1 = over(t["accent-tint"], l1)
tint_field = over(t["accent-tint"], field)
tint_l3 = over(t["accent-tint"], l3)
# The glass, lightest corner (where the top-left highlight sits), composited from the tokens
card_glass = over(t["glass-hi"], over(t["glass-base"], l2))
strip_glass = over(t["glass-hi"], over(t["glass-dense"], l2))
strip_glass_field = over(t["glass-hi"], over(t["glass-dense"], field))
strip_glass_worst = over(t["glass-hi"], over(t["glass-dense"], t["text"]))   # an unblurred line of white text right behind it
sheet_glass = over(t["glass-hi"], over(t["glass-dense"], over(t["scrim"], l2)))
sheet_glass_worst = over(t["glass-hi"], over(t["glass-dense"], over(t["scrim"], t["text"])))
solid = t["glass-solid"]
pairs = [
    ("body text on the page (l2)", t["text"], l2, 4.5),
    ("body text on a field", t["text"], field, 4.5),
    ("body text in the item frame (l1)", t["text"], l1, 4.5),
    ("body text on a dialog (l3)", t["text"], l3, 4.5),
    ("body text on the top bar (l1)", t["text"], l1, 4.5),
    ("muted text on the page (labels, hint)", t["text-muted"], l2, 4.5),
    ("muted text on a field (placeholder, RM, %)", t["text-muted"], field, 4.5),
    ("muted text in the item frame (untapped person)", t["text-muted"], l1, 4.5),
    ("muted text on a dialog", t["text-muted"], l3, 4.5),
    ("body text on the indigo tint, tapped person (frame)", t["text"], tint_l1, 4.5),
    ("body text on the indigo tint, chosen mode (field)", t["text"], tint_field, 4.5),
    ("body text on the indigo tint, chosen pill (dialog)", t["text"], tint_l3, 4.5),
    ("Copy summary text on its indigo fill", t["on-accent"], t["accent"], 4.5),
    ("Copy summary text on its hover fill", t["on-accent"], t["accent-hover"], 4.5),
    ("Start new bill text on its red fill", t["on-danger"], t["danger"], 4.5),
    ("Start new bill text on its hover fill", t["on-danger"], t["danger-hover"], 4.5),
    ("indigo ink on a dialog (chosen radio dot, pill check)", t["accent-ink"], l3, 3.0),
    ("indigo ink on the frame (tapped check)", t["accent-ink"], tint_l1, 3.0),
    ("indigo line on the frame (tapped person edge)", t["accent-line"], l1, 3.0),
    ("indigo line on a field (chosen mode edge)", t["accent-line"], field, 3.0),
    ("indigo line on a dialog (chosen pill edge)", t["accent-line"], l3, 3.0),
    ("control border on the page", t["line-strong"], l2, 3.0),
    ("control border on a field", t["line-strong"], field, 3.0),
    ("control border in the frame", t["line-strong"], l1, 3.0),
    ("control border on a dialog", t["line-strong"], l3, 3.0),
    ("control border on the top bar", t["line-strong"], l1, 3.0),
    ("focus ring on the page", t["focus"], l2, 3.0),
    ("focus ring in the frame", t["focus"], l1, 3.0),
    ("focus ring on a dialog", t["focus"], l3, 3.0),
    ("error text on the page", t["error-ink"], l2, 4.5),
    ("error text in the frame", t["error-ink"], l1, 4.5),
    ("error border on a field", t["error-ink"], field, 3.0),
    ("S3 marker in the frame", t["warn-ink"], l1, 3.0),
    ("S5 text on the warning band", t["text"], t["warn-bg"], 4.5),
    ("S5 icon on the warning band", t["warn-ink"], t["warn-bg"], 3.0),
    ("S6 text on the note band", t["text"], t["info-bg"], 4.5),
    ("S6 icon on the note band", t["accent-ink"], t["info-bg"], 3.0),
    # the glass card (desktop)
    ("card: Total figure", t["total-ink"], card_glass, 4.5),
    ("card: body text (names, Total label, Adds up to)", t["text"], card_glass, 4.5),
    ("card: muted text (bill lines, working, sen left over)", t["text-muted"], card_glass, 4.5),
    ("card: indigo Adds up to figure", t["accent-ink"], card_glass, 4.5),
    ("card: S3 warning icon", t["warn-ink"], card_glass, 3.0),
    ("card: S4 failure icon", t["error-ink"], card_glass, 3.0),
    ("card: chip border (spare sen, Pick again)", t["line-glass"], card_glass, 3.0),
    ("card: focus ring", t["focus"], card_glass, 3.0),
    # the strip (phone), over the page and over a field
    ("strip: Total figure", t["total-ink"], strip_glass, 4.5),
    ("strip: body text (Total label, status, messages)", t["text"], strip_glass, 4.5),
    ("strip: body text over a field", t["text"], strip_glass_field, 4.5),
    ("strip: Shares button border", t["line-glass"], strip_glass, 3.0),
    ("strip: Shares button border over a field", t["line-glass"], strip_glass_field, 3.0),
    ("strip: focus ring", t["focus"], strip_glass, 3.0),
    ("strip, worst case: body text over an unblurred white line", t["text"], strip_glass_worst, 4.5),
    # the sheet (phone)
    ("sheet: Total figure", t["total-ink"], sheet_glass, 4.5),
    ("sheet: body text", t["text"], sheet_glass, 4.5),
    ("sheet: muted text", t["text-muted"], sheet_glass, 4.5),
    ("sheet: indigo Adds up to figure", t["accent-ink"], sheet_glass, 4.5),
    ("sheet: chip border", t["line-glass"], sheet_glass, 3.0),
    ("sheet, worst case: muted text over an unblurred white line", t["text-muted"], sheet_glass_worst, 4.5),
    # the solid fallback card
    ("fallback card: muted text", t["text-muted"], solid, 4.5),
    ("fallback card: indigo figure", t["accent-ink"], solid, 4.5),
    ("fallback card: chip border", t["line-glass"], solid, 3.0),
    # prototype tool (not the design)
    ("prototype tab text", parse_colour("#1B1B1B"), parse_colour("#ECECE8"), 4.5),
]
for label, fg, bg, need in pairs:
    r = ratio(fg, bg)
    R["contrast"][label] = {"ratio": r, "need": need, "pass": r >= need}
    check(r >= need, f"contrast {label} {r} < {need}")
R["tokens"] = tokens

for where, small in R["targets"].items():
    check(not small, f"touch targets under 44 px at {where}: {small}")
check(not R["console_errors"] and not R["page_errors"], "console or page errors")
check(not R["network"], "network requests")

(HERE / "results.json").write_text(json.dumps(R, indent=2), encoding="utf-8")

# ---------- summary ----------
print("console errors:", len(R["console_errors"]), R["console_errors"][:5])
print("page errors:", len(R["page_errors"]), R["page_errors"][:5])
print("network:", R["network"])
print("dashes:", R["dashes"])
print("icons:", R["icons"])
for k, v in R["noscroll_1280"].items():
    print("noscroll", k, v["docScrollHeight"], v["viewport"], v["stage"], v["work"], v["frame"])
for k, v in R["frame"].items():
    print("frame", k, v)
for k, v in R["overflow_360"].items():
    print("overflow360", k, v["scrollWidth"], v["clientWidth"], v["bad"])
for k, v in R["strip"].items():
    print("strip", k, json.dumps(v)[:300])
for k, v in R["proto_tab"].items():
    print("proto", k, v)
print("order:", R["order"])
for k, v in R["figures"].items():
    print("fig", k, "=>", json.dumps(v)[:300])
for k, v in R["addup"].items():
    if "random draw" not in k:
        print("addup", k, v["sum"], v["total"], v["proof"])
for k, v in R["contrast"].items():
    print("contrast", k, v["ratio"], "PASS" if v["pass"] else "FAIL")
print("motion:", R["motion"])
print("clipboard:", R["clipboard"])
print("targets:", R["targets"])
print("shots:", len(R["shots"]))
print("FAILS:", len(R["fails"]))
for f in R["fails"]:
    print("  FAIL", f)
