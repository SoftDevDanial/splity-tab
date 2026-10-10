"""Render checks for round-2 direction G2 (Glass Console, revised).

Run: python -B check_g2.py
Started from checks/g/check_g.py. Every G assert that still applies is kept, with the renamed ids (splitsBtn,
splitsDlg, splitsH, #splits, .r-splits) and the renamed copy ("splits"). Added: the People and Charges sections
below 1024 px, the "Shares" to "Splits" rename, and a side by side with g.html (opened read only) for the desktop
block positions at 1280 and the first Items field and Subtotal field at 390.

Opens g2.html by its file:/// URL in headless Chromium (scrollbars shown) at 390 x 844, 360 x 780 and 1280 x 800,
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
PAGE = ROUND / "g2.html"
BASE = ROUND / "g.html"
NOTES = ROUND / "g2.md"
URL = PAGE.as_uri()
BASE_URL = BASE.as_uri()
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

R = {"console_errors": [], "page_errors": [], "network": [], "fails": [], "passes": 0, "figures": {}, "addup": {},
     "noscroll_1280": {}, "frame": {}, "overflow_360": {}, "strip": {}, "proto_tab": {}, "order": {},
     "sections": {}, "rename": {}, "vs_g": {}, "contrast": {}, "icons": {}, "dashes": {}, "targets": {},
     "clipboard": {}, "motion": {}, "shots": []}


def check(cond, label):
    if cond:
        R["passes"] += 1
    else:
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
base_src = BASE.read_text(encoding="utf-8")
R["dashes"]["g2.html"] = {"em": src.count("—"), "en": src.count("–")}
check(src.count("—") == 0 and src.count("–") == 0, "long dashes in g2.html")
if NOTES.exists():
    md = NOTES.read_text(encoding="utf-8")
    R["dashes"]["g2.md"] = {"em": md.count("—"), "en": md.count("–")}
    check(md.count("—") == 0 and md.count("–") == 0, "long dashes in g2.md")
else:
    R["dashes"]["g2.md"] = "not written yet"
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
# every symbol line is G's line, byte for byte
g_syms = re.findall(r"<symbol[^\n]+</symbol>", base_src)
g2_syms = re.findall(r"<symbol[^\n]+</symbol>", src)
R["icons"]["same symbol lines as g.html"] = g_syms == g2_syms
check(g_syms == g2_syms, "symbol lines differ from g.html")
check("https://" not in src and "http://" not in src.replace("http://www.w3.org/2000/svg", ""), "a remote URL in g2.html")
# no user-facing "Shares" string left in the source (ids and money data names are not read by the person)
src_hits = re.findall(r'>\s*Shares\s*<|"Shares"|see the shares|Bill and shares|Shares sheet \(phone\)', src)
R["rename"]["source strings still saying Shares"] = src_hits
check(not src_hits, f"a user-facing Shares string in the source {src_hits}")

# ---------- page helpers ----------
JS_ROWS = """() => [...document.querySelectorAll('#rbody .r-splits li')].map(li => ({
  name: li.querySelector('.nm').textContent,
  share: li.querySelector('.amt').textContent,
  wk: li.querySelector('.wk') ? li.querySelector('.wk').textContent.replace(/\\s+/g, ' ').trim() : null
}))"""
JS_RECEIPT = """() => { const t = (s) => { const e = document.querySelector(s); return e ? e.textContent.replace(/\\s+/g, ' ').trim() : null; };
  return { total: t('#rTotal'), lines: [...document.querySelectorAll('#rbody .r-lines > div')].map(d => d.querySelector('dt').textContent + ' = ' + d.querySelector('dd').textContent),
           proof: t('#addsUp'), proofWork: t('#rbody .r-check .wk'), spare: t('#spareLine'), rule: t('#spareBtn'), legend: t('#rbody .r-head span'), heading: t('#splitsH') }; }"""
JS_ADDUP = """() => { const c = (s) => s ? Number(String(s).replace(/[^0-9]/g, '')) : null;
  const shares = [...document.querySelectorAll('#rbody .r-splits .amt')].map(e => c(e.textContent));
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
    if (el.classList.contains('blk') || el.classList.contains('top') || el.classList.contains('sec-body') || el.classList.contains('sec-in')) continue;
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
# The two sections below 1024 px
JS_SECS = """() => {
  const one = (k) => {
    const blk = document.querySelector('#' + k + 'Blk'), btn = document.querySelector('#' + k + 'Btn'), body = document.querySelector('#' + k + 'Body');
    const sum = document.querySelector('#' + k + 'Sum'), txt = sum.querySelector('.sec-txt');
    const r = btn.getBoundingClientRect(), tr = txt ? txt.getClientRects() : [];
    return { open: blk.dataset.open, expanded: btn.getAttribute('aria-expanded'), controls: btn.getAttribute('aria-controls'),
             controlsExists: !!document.getElementById(btn.getAttribute('aria-controls')),
             bodyShown: getComputedStyle(body).display !== 'none' && body.getBoundingClientRect().height > 0,
             headerShown: getComputedStyle(btn).display !== 'none' && r.height > 0,
             w: Math.round(r.width), h: Math.round(r.height), top: Math.round(r.top),
             summary: txt ? txt.textContent : null, summaryVisible: getComputedStyle(sum).visibility === 'visible',
             summaryFits: sum.scrollWidth <= sum.clientWidth, summaryLines: tr.length, summaryLineH: tr.length ? Math.round(tr[0].height) : null,
             bad: btn.classList.contains('is-bad'), sumColour: getComputedStyle(sum).color, sumWeight: getComputedStyle(sum).fontWeight, hasIcon: !!sum.querySelector('svg'),
             headingTag: btn.parentElement.tagName };
  };
  return { people: one('people'), charges: one('charges') };
}"""
JS_POS = """() => {
  const top = (s) => { const e = document.querySelector(s); return e && e.getClientRects().length ? Math.round(e.getBoundingClientRect().top + window.scrollY) : null; };
  const strip = document.querySelector('#strip').getBoundingClientRect().top;
  const fw = document.querySelector('#frameWrap').getBoundingClientRect();
  const lim = Math.min(strip, fw.bottom);
  const items = [...document.querySelectorAll('#itemList .item')].map(li => li.getBoundingClientRect());
  return { scrollY: Math.round(window.scrollY), firstItemField: top('#itemList .item .field'), subtotalField: top('#evenField'), stripTop: Math.round(strip),
           itemsFullyAboveStrip: items.filter(r => r.bottom <= lim + 0.5 && r.top >= fw.top - 0.5).length,
           itemsStartedAboveStrip: items.filter(r => r.top < lim - 0.5).length, itemsTotal: items.length };
}"""
BLOCKS = ['.top', '#newBill', '#stage', '#card', '#rTotal', '#rbody .r-lines', '#rbody .r-head', '#addsUp', '#spareLine', '#spareBtn', '#copyBtn',
          '#work', '#peopleBlk', '#peopleH', '#addPerson', '#peopleList', '#chargesBlk', '#chargesH', '#svc', '#sst', '#chargeHint',
          '#splitBlk', '#modeEven', '#evenBlock', '#evenSub', '#itemsBlock', '#addItem', '#frameWrap', '#itemList', '#itemList .item:first-child .field']
JS_BLOCKS = """(sels) => { const out = {}; for (const s of sels) { const e = document.querySelector(s);
  const box = e && e.type === 'radio' ? e.nextElementSibling : e;
  if (!box || !box.getClientRects().length) { out[s] = null; continue; }
  const r = box.getBoundingClientRect(); out[s] = [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)]; } return out; }"""

SHARES_RE = re.compile(r"\bshares?\b", re.I)


def rows(page):
    return page.evaluate(JS_ROWS)


def shares(page):
    return [(r["name"], r["share"]) for r in rows(page)]


def settle(page, ms=150):
    page.wait_for_timeout(ms)


def run(page, key):
    page.mouse.move(2, 2)   # off every control, so a screenshot never shows a hover left by the last tap
    page.evaluate(f"() => {{ if (document.activeElement) document.activeElement.blur(); window.__g.run('{key}'); }}")
    settle(page, 200)


def secs(page):
    return page.evaluate(JS_SECS)


JS_P1_COVER = """() => {
  const p = document.querySelector('#spareDlg').getBoundingClientRect();
  const s = document.querySelector('#splits').getBoundingClientRect();
  const box = document.querySelector('#sheetScroll');
  const inSheet = !!box.querySelector('#splits');
  const viewTop = inSheet ? box.getBoundingClientRect().top : 0;
  const covered = !(p.top >= s.bottom - 0.5 || p.left >= s.right - 0.5 || p.right <= s.left + 0.5);
  return { popTop: Math.round(p.top), popLeft: Math.round(p.left), sharesTop: Math.round(s.top), sharesBottom: Math.round(s.bottom), sharesRight: Math.round(s.right),
           covered, sharesVisible: s.top >= viewTop - 0.5 };
}"""


def p1_cover(page, label):
    v = page.evaluate(JS_P1_COVER)
    R["figures"][f"P1 vs splits, {label}"] = v
    check(not v["covered"] and v["sharesVisible"], f"P1 covers or hides the splits at {label}: {v}")


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
    check(v["shares"] and v["sum"] == v["total"] == v["proof"], f"splits do not add up at {label}: {v}")
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


def ax_names(page):
    cdp = page.context.new_cdp_session(page)
    try:
        cdp.send("Accessibility.enable")
        tree = cdp.send("Accessibility.getFullAXTree")
    finally:
        cdp.detach()
    out = []
    for n in tree.get("nodes", []):
        if n.get("ignored"):
            continue
        nm = (n.get("name") or {}).get("value")
        role = (n.get("role") or {}).get("value")
        if nm:
            out.append((role, str(nm)))
    return out


def no_shares(page, label):
    """'Shares' or 'shares' is absent from the visible text and from every accessible name."""
    txt = page.evaluate("document.body.innerText")
    names = ax_names(page)
    bad_txt = SHARES_RE.findall(txt)
    bad_names = [n for n in names if SHARES_RE.search(n[1])]
    R["rename"][f"no Shares, {label}"] = {"text_hits": bad_txt[:5], "name_hits": bad_names[:5], "accessible_names_checked": len(names)}
    check(not bad_txt and not bad_names and len(names) > 5, f"Shares still read at {label}: {bad_txt[:3]} {bad_names[:3]}")
    return names


def strip_checks(page, label, first_screen=True, min_seen=6):
    """The strip never covers the inputs: the first screen (a three-person bill), the page end, and every control
    while it has focus. With twelve people open the first screen is recorded only, since People alone fill it.
    min_seen proves the Tab walk ran. S7 folded in Even has four controls in the working (People, Charges, the
    checked Split radio, Subtotal), so it passes 4."""
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
        if f["id"] in ("splitsBtn", "stripCopy"):
            break
        if not f["inWork"]:
            continue
        seen += 1
        if not f["ok"]:
            bad.append(f)
    out["tabbed_controls"] = seen
    out["covered_while_focused"] = bad[:8]
    check(seen >= min_seen and not bad, f"{label}: a focused control sat under the strip {bad[:3]} (seen {seen}, need {min_seen})")
    R["strip"][label] = out
    page.evaluate("window.scrollTo(0, 0)")


K1_ROWS = [
    {"name": "Aisyah", "share": "RM 29.04", "wk": "Items 24.90 + charges 4.14"},
    {"name": "Ben", "share": "RM 15.74", "wk": "Items 13.50 + charges 2.24"},
    {"name": "Chen", "share": "RM 24.48", "wk": "Items 21.00 + charges 3.48"},
]
K1_LINES = ["Subtotal = RM 59.40", "Service 10% = RM 5.94", "SST 6% = RM 3.92"]
K2_LINES = ["Subtotal = RM 100.00", "Service 10% = RM 10.00", "SST 6% = RM 6.60"]
EMPTY_EVEN = "Enter the subtotal to see the splits."
MSG3 = "1 item still needs a person. Tap who had it to see the splits."


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
    check(rc["heading"] == "Splits", f"K1 receipt heading {where}: {rc['heading']}")
    addup(page, f"K1 {where}")


def figures_k2(page, where):
    got = shares(page)
    R["figures"][f"K2 splits {where}"] = got
    check(got == [("Aisyah", "RM 38.87"), ("Ben", "RM 38.87"), ("Chen", "RM 38.86")], f"K2 splits {where}: {got}")
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
    """floor: each person's split in cents before any spare sen. Every draw must give exactly people_with_sen
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


def folded_k1(page, label):
    """K1 on a phone: both sections folded, with the right summaries, header rows at least 44 px."""
    v = secs(page)
    R["sections"][f"K1 {label}"] = v
    p, c = v["people"], v["charges"]
    check(p["open"] == "false" and p["expanded"] == "false" and not p["bodyShown"] and p["headerShown"], f"{label} People not folded {p}")
    check(c["open"] == "false" and c["expanded"] == "false" and not c["bodyShown"] and c["headerShown"], f"{label} Charges not folded {c}")
    check(p["summary"] == "Aisyah, Ben, Chen" and p["summaryVisible"] and p["summaryFits"] and p["sumWeight"] == "400", f"{label} People summary {p}")
    check(c["summary"] == "Service 10%, SST 6%" and c["summaryVisible"] and c["summaryFits"] and not c["bad"], f"{label} Charges summary {c}")
    check(p["h"] >= 44 and c["h"] >= 44 and p["w"] >= 44 and c["w"] >= 44, f"{label} header rows under 44 px {p['h']} {c['h']}")
    check(p["controlsExists"] and c["controlsExists"] and p["headingTag"] == "H2" and c["headingTag"] == "H2", f"{label} header buttons not wired {v}")
    return v


def toggles(page, label):
    """aria-expanded flips on tap, Enter and Space, for both header buttons."""
    out = {}
    for k in ("people", "charges"):
        btn = f"#{k}Btn"
        seq = []
        page.click(btn)
        settle(page, 260)
        seq.append(("tap", secs(page)[k]["expanded"], secs(page)[k]["bodyShown"]))
        page.click(btn)
        settle(page, 120)
        seq.append(("tap", secs(page)[k]["expanded"], secs(page)[k]["bodyShown"]))
        page.focus(btn)
        page.keyboard.press("Enter")
        settle(page, 260)
        seq.append(("Enter", secs(page)[k]["expanded"], secs(page)[k]["bodyShown"]))
        page.keyboard.press("Enter")
        settle(page, 120)
        seq.append(("Enter", secs(page)[k]["expanded"], secs(page)[k]["bodyShown"]))
        page.keyboard.press("Space")
        settle(page, 260)
        seq.append(("Space", secs(page)[k]["expanded"], secs(page)[k]["bodyShown"]))
        page.keyboard.press("Space")
        settle(page, 120)
        seq.append(("Space", secs(page)[k]["expanded"], secs(page)[k]["bodyShown"]))
        out[k] = seq
        want = [("tap", "true", True), ("tap", "false", False), ("Enter", "true", True), ("Enter", "false", False), ("Space", "true", True), ("Space", "false", False)]
        check(seq == want, f"{label} {k} header does not toggle {seq}")
    R["sections"][f"toggles {label}"] = out


with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, ignore_default_args=["--hide-scrollbars"])
    try:
        def new_page(w, h, reduced=False, phone=False, url=URL):
            # phone=True emulates a touch phone (overlay scrollbars) for honest 390 screenshots.
            # 360 stays a desktop-style window with classic scrollbars, the stricter width test.
            ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1,
                                      is_mobile=phone, has_touch=phone,
                                      reduced_motion="reduce" if reduced else "no-preference")
            ctx.add_init_script(CLIP_STUB)
            pg = ctx.new_page()
            pg.set_default_timeout(WAIT_MS)
            tag = f"{'g ' if url == BASE_URL else ''}{w}{'rm' if reduced else ''}"
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
            pg.goto(url, wait_until="load")
            settle(pg, 300)
            return ctx, pg

        # ================= G, read only: the figures G2 is measured against =================
        gpos = {}
        ctx, page = new_page(390, 844, phone=True, url=BASE_URL)
        gpos["K1 390"] = page.evaluate(JS_POS)
        run(page, "k2")
        gpos["K2 390"] = page.evaluate(JS_POS)
        run(page, "w2")
        gpos["W2 390"] = page.evaluate(JS_POS)
        clip_audit(page, "g.html 390 (read only)")
        ctx.close()
        gblocks = {}
        ctx, page = new_page(1280, 800, url=BASE_URL)
        for key in ("k1", "k2", "s7", "w2"):
            run(page, key)
            gblocks[key] = page.evaluate(JS_BLOCKS, BLOCKS)
        clip_audit(page, "g.html 1280 (read only)")
        ctx.close()

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
        # the sections, folded on load
        folded_k1(page, "390")
        R["rename"]["bar button 390"] = text(page, "#splitsBtn")
        check(R["rename"]["bar button 390"] == "Splits", f"bar button {R['rename']['bar button 390']}")
        no_shares(page, "390 K1")
        # positions against G
        pos = {"K1 390": page.evaluate(JS_POS)}
        tab_check(page, "390 K1 top")
        page.evaluate("window.scrollTo(0, 400)")
        settle(page, 80)
        tab_check(page, "390 K1 scrolled 400")
        shot(page, "k1-390-scrolled")
        strip_checks(page, "390 K1")
        R["targets"]["390 K1"] = page.evaluate(JS_TARGETS)
        toggles(page, "390")
        # focus ring on a header button
        page.mouse.move(2, 2)
        page.focus("#chargesBtn")
        page.keyboard.press("Shift+Tab")
        page.keyboard.press("Tab")
        settle(page, 80)
        ring = page.evaluate("""() => { const a = document.activeElement, r = getComputedStyle(a, '::after'), b = a.getBoundingClientRect();
            return { id: a.id, focusVisible: a.matches(':focus-visible'), style: r.borderTopStyle, colour: r.borderTopColor, width: r.borderTopWidth,
                     ringLeft: Math.round(b.left + parseFloat(r.left)), textLeft: Math.round(a.querySelector('.sec-name').getBoundingClientRect().left),
                     ringRight: Math.round(b.right - parseFloat(r.right)), viewport: document.documentElement.clientWidth }; }""")
        R["sections"]["focus ring 390"] = ring
        check(ring["id"] == "chargesBtn" and ring["focusVisible"] and ring["style"] == "solid" and ring["width"] == "2px" and ring["colour"] == "rgb(163, 170, 255)"
              and ring["textLeft"] - ring["ringLeft"] >= 8 and ring["ringRight"] <= ring["viewport"], f"no clear focus ring on a header button {ring}")
        shot(page, "focus-charges-header-390")
        # both open at once, the prototype shortcut
        run(page, "k1open")
        v = secs(page)
        R["sections"]["K1 both open 390"] = v
        check(v["people"]["expanded"] == "true" and v["people"]["bodyShown"] and v["charges"]["expanded"] == "true" and v["charges"]["bodyShown"], f"K1 open shortcut {v}")
        check(not v["people"]["summaryVisible"] and not v["charges"]["summaryVisible"], f"summaries show while open {v}")
        check(page.eval_on_selector("#addPerson", "b => b.getBoundingClientRect().height > 0"), "Add person not shown inside People when open")
        o2 = page.evaluate(JS_ORDER)
        R["order"]["390 both open"] = o2
        check(o2["people"] < o2["charges"] < o2["split"] < o2["items"], f"390 order with both open {o2}")
        shot(page, "k1-open-390")
        shot(page, "k1-open-390-full", full=True)
        tab_check(page, "390 K1 both open")
        strip_checks(page, "390 K1 both open")
        R["targets"]["390 K1 both open"] = page.evaluate(JS_TARGETS)
        # a summary follows a name and a rate
        page.fill("#pn2", "Benjamin")
        settle(page, 80)
        page.fill("#svc", "8")
        settle(page, 80)
        page.click("#peopleBtn")
        page.click("#chargesBtn")
        settle(page, 120)
        v = secs(page)
        R["sections"]["summaries after a name and a rate change 390"] = {"people": v["people"]["summary"], "charges": v["charges"]["summary"]}
        check(v["people"]["summary"] == "Aisyah, Benjamin, Chen" and v["charges"]["summary"] == "Service 8%, SST 6%", f"summaries did not follow the edit {v}")
        check(text(page, "#stripInfo") != "TotalRM 69.26", "the total did not follow the new service rate")
        shot(page, "k1-edited-folded-390")

        # P2 Splits sheet from the strip
        run(page, "k1")
        page.click("#splitsBtn")
        page.wait_for_selector("#splitsDlg[open]")
        settle(page, 350)
        shot(page, "p2-390")
        check(page.evaluate("document.querySelector('#splitsBtn').getAttribute('aria-expanded')") == "true", "Splits aria-expanded")
        check(page.eval_on_selector("#splitsDlg", "d => d.getAttribute('aria-label')") == "Splits", "sheet name is not Splits")
        names = no_shares(page, "390 P2 sheet open")
        R["rename"]["sheet accessible name"] = [n for n in names if n[0] == "dialog"]
        check(("dialog", "Splits") in names, f"the sheet is not named Splits {[n for n in names if n[0] == 'dialog']}")
        figures_k1(page, "390 sheet")
        R["figures"]["sheet spare line 390"] = text(page, "#splitsDlg #spareLine")
        check(R["figures"]["sheet spare line 390"] == "1 sen left over", "1 sen left over is not in the sheet")
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
        check(is_open(page, "#splitsDlg"), "the sheet stays open under P1")
        page.click('label.choice:has(input[value="one"])')
        settle(page)
        shot(page, "p1-picker-390")
        p1_random(page, "K1 390", [2903, 1574, 2448], 1, "#pickAgainSheet")
        shot(page, "p1-random-390")
        # Esc closes P1 first, then the sheet. Backdrop and Close shut the sheet
        page.keyboard.press("Escape")
        settle(page)
        check(not is_open(page, "#spareDlg") and is_open(page, "#splitsDlg"), "Esc closes P1 only")
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
        check(not is_open(page, "#splitsDlg"), "Esc closes the sheet")
        check(page.evaluate("document.activeElement.id") == "splitsBtn", "focus returns to Splits")
        page.click("#splitsBtn")
        page.wait_for_selector("#splitsDlg[open]")
        page.mouse.click(195, 20)
        settle(page)
        check(not is_open(page, "#splitsDlg"), "backdrop closes the sheet")
        page.click("#splitsBtn")
        page.wait_for_selector("#splitsDlg[open]")
        page.click("#splitsDlg [data-close]")
        settle(page)
        check(not is_open(page, "#splitsDlg"), "Close shuts the sheet")
        tab_check(page, "390 tab with the sheet closed")

        # K2 by the design's own switch
        run(page, "k1")
        page.click("label[for=modeEven]")
        settle(page)
        figures_k2(page, "390 via switch")
        R["figures"]["K2 strip 390"] = text(page, "#stripInfo")
        check(R["figures"]["K2 strip 390"] == "TotalRM 116.60", f"K2 strip {R['figures']['K2 strip 390']}")
        v = secs(page)
        check(v["people"]["expanded"] == "false" and v["charges"]["expanded"] == "false", f"the switch opened a section {v}")
        page.evaluate("window.scrollTo(0, 0)")
        pos["K2 390"] = page.evaluate(JS_POS)
        shot(page, "k2-390")
        page.click("#splitsBtn")
        page.wait_for_selector("#splitsDlg[open]")
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

        # M1, and S1 through Start new bill: People opens, Charges stays folded
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
                     "strip": EMPTY_EVEN, "receipt": "Total" + EMPTY_EVEN, "copyDisabled": True}, f"S1 {s1}")
        v = secs(page)
        R["sections"]["S1 via Start new bill 390"] = v
        check(v["people"]["expanded"] == "true" and v["people"]["bodyShown"] and v["charges"]["expanded"] == "false" and not v["charges"]["bodyShown"], f"S1 via Start new bill: People open, Charges folded {v}")
        no_shares(page, "390 S1")
        shot(page, "s1-start-new-390")
        page.click("#splitsBtn")
        page.wait_for_selector("#splitsDlg[open]")
        settle(page, 350)
        shot(page, "s1-sheet-390")
        page.keyboard.press("Escape")
        settle(page)

        # States with no natural trigger
        run(page, "s1")
        v = secs(page)
        R["sections"]["S1 390"] = v
        check(v["people"]["expanded"] == "true" and v["people"]["bodyShown"] and v["charges"]["expanded"] == "false", f"S1: People open, Charges folded {v}")
        check(v["charges"]["summary"] == "Service 10%, SST 6%", f"S1 charges summary {v['charges']}")
        pos["S1 390"] = page.evaluate(JS_POS)
        shot(page, "s1-390")
        strip_checks(page, "390 S1")
        run(page, "s2")
        R["figures"]["S2"] = text(page, "#evenBlock")
        check("Enter an amount like 12.50" in R["figures"]["S2"] and page.eval_on_selector("#evenErr", "e => !e.hidden"), "S2 error copy")
        v = secs(page)
        R["sections"]["S2 amount 390"] = v
        check(v["people"]["expanded"] == "false" and v["charges"]["expanded"] == "false", f"S2 amount: a section opened {v}")
        shot(page, "s2-390")
        # S2 on a rate: Charges opens and shows the error
        run(page, "s2rate")
        v = secs(page)
        R["sections"]["S2 rate 390"] = v
        rate = page.evaluate("""() => ({ shown: !document.querySelector('#svcErr').hidden, text: document.querySelector('#svcErr').textContent.trim(),
            invalid: document.querySelector('#svc').getAttribute('aria-invalid'), described: document.querySelector('#svc').getAttribute('aria-describedby'),
            bad: document.querySelector('#svc').closest('.field').classList.contains('is-bad'),
            visible: document.querySelector('#svcErr').getBoundingClientRect().height > 0,
            sstDescribed: document.querySelector('#sst').getAttribute('aria-describedby') })""")
        R["sections"]["S2 rate error lines 390"] = page.evaluate("() => { const e = document.querySelector('#svcErr'); const r = document.createRange(); r.selectNodeContents(e); const tops = new Set([...r.getClientRects()].filter(x => x.width > 1 && x.height > 10 && x.height < 30).map(x => Math.round(x.top))); return { lines: tops.size, height: Math.round(e.getBoundingClientRect().height) }; }")
        R["sections"]["S2 rate error 390"] = rate
        check(v["charges"]["expanded"] == "true" and v["charges"]["bodyShown"] and v["people"]["expanded"] == "false", f"a rate error did not open Charges {v}")
        check(rate == {"shown": True, "text": "Enter a rate from 0 to 30", "invalid": "true", "described": "chargeHint svcErr", "bad": True, "visible": True, "sstDescribed": "chargeHint"}, f"S2 rate error {rate}")
        shot(page, "s2-rate-390")
        page.click("#chargesBtn")
        settle(page, 120)
        v = secs(page)
        R["sections"]["S2 rate folded 390"] = v["charges"]
        check(v["charges"]["expanded"] == "false" and v["charges"]["bad"] and v["charges"]["summary"] == "Check service charge" and v["charges"]["hasIcon"]
              and v["charges"]["sumColour"] == "rgb(255, 138, 143)" and v["charges"]["summaryVisible"] and v["charges"]["summaryFits"], f"a folded error is hidden {v['charges']}")
        shot(page, "s2-rate-folded-390")
        page.click("#chargesBtn")
        settle(page, 260)
        page.fill("#sst", "25")
        page.fill("#svc", "10")
        settle(page, 80)
        page.click("#chargesBtn")
        settle(page, 120)
        v = secs(page)
        R["sections"]["SST error folded 390"] = v["charges"]["summary"]
        check(v["charges"]["summary"] == "Check SST" and v["charges"]["bad"], f"SST error marker {v['charges']}")
        page.click("#chargesBtn")
        settle(page, 260)
        page.fill("#svc", "31")
        settle(page, 80)
        page.click("#chargesBtn")
        settle(page, 120)
        v = secs(page)
        R["sections"]["both rates folded 390"] = v["charges"]["summary"]
        check(v["charges"]["summary"] == "Check both rates" and v["charges"]["bad"] and v["charges"]["summaryFits"], f"both rates marker {v['charges']}")
        run(page, "s3")
        R["figures"]["S3 strip"] = text(page, "#stripInfo")
        R["figures"]["S3 receipt"] = text(page, "#rbody .r-msg")
        check(R["figures"]["S3 strip"] == MSG3 and R["figures"]["S3 receipt"] == MSG3, "S3 copy")
        check(page.evaluate("document.querySelector('#stripCopy').disabled"), "S3 copy disabled")
        check(page.evaluate("document.querySelector('.item[data-item=\"3\"]').classList.contains('needs')"), "S3 marker on Mee goreng mamak")
        no_shares(page, "390 S3")
        page.eval_on_selector("#itemsBlock", "e => e.scrollIntoView({ block: 'start' })")
        settle(page)
        shot(page, "s3-390")
        page.click("#splitsBtn")
        page.wait_for_selector("#splitsDlg[open]")
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
        v = secs(page)
        R["sections"]["S6 390 (brief: folded)"] = {"people": v["people"]["expanded"], "charges": v["charges"]["expanded"], "summary": v["people"]["summary"]}
        check(v["people"]["expanded"] == "false" and v["charges"]["expanded"] == "false", f"S6 sections {v}")
        shot(page, "s6-390")
        page.click("#dismissNote")
        settle(page)
        check(text(page, "#notes") == "", "S6 dismiss")
        # S7: twelve people, the summary on one line
        run(page, "s7")
        check(page.eval_on_selector("#addPerson", "b => b.disabled"), "S7 add person disabled")
        check(page.evaluate("document.querySelectorAll('#peopleList .person').length") == 12, "S7 has 12 people")
        v = secs(page)
        R["sections"]["S7 390"] = v["people"]
        check(v["people"]["expanded"] == "false" and v["people"]["summaryFits"] and v["people"]["summaryLines"] == 1 and v["people"]["summaryLineH"] <= 21
              and v["people"]["summary"].startswith("Aisyah, Ben, Chen") and v["people"]["summary"].endswith("more"), f"S7 summary {v['people']}")
        addup(page, "S7 390")
        R["figures"]["S7 spare"] = text(page, "#spareLine")
        shot(page, "s7-390")
        shot(page, "s7-390-full", full=True)
        strip_checks(page, "390 S7", min_seen=4)
        page.click("#peopleBtn")
        settle(page, 260)
        shot(page, "s7-people-open-390-full", full=True)
        strip_checks(page, "390 S7 People open", first_screen=False)
        R["targets"]["390 S7 People open"] = page.evaluate(JS_TARGETS)
        run(page, "w1")
        R["figures"]["W1 strip 390"] = text(page, "#stripInfo")
        check(R["figures"]["W1 strip 390"] == "TotalRM 1,193.87", f"W1 strip {R['figures']['W1 strip 390']}")
        addup(page, "W1 390")
        shot(page, "w1-390")
        # W2 at 390: the item frame scrolls inside itself
        run(page, "w2")
        pos["W2 390"] = page.evaluate(JS_POS)
        shot(page, "w2-390-top")
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
        no_shares(page, "390 prototype panel open")
        R["rename"]["prototype labels"] = page.evaluate("[...document.querySelectorAll('#protoList button')].map(b => b.textContent)")
        check("P2 Splits sheet (phone)" in R["rename"]["prototype labels"] and "K1 People and Charges open (phone)" in R["rename"]["prototype labels"], "prototype labels")
        pp = page.evaluate("() => { const p = document.querySelector('#protoPanel').getBoundingClientRect(); const d = document.querySelector('#strip').getBoundingClientRect(); return { bottom: p.bottom, stripTop: d.top }; }")
        R["proto_tab"]["390 panel vs strip"] = pp
        check(pp["bottom"] <= pp["stripTop"], f"proto panel overlaps the strip {pp}")
        page.click("#protoClose")
        # the tab sits under an open popup's backdrop
        for dlg, opener in (("#newDlg", "#newBill"), ("#splitsDlg", "#splitsBtn")):
            page.click(opener)
            page.wait_for_selector(f"{dlg}[open]")
            under = page.evaluate("() => { const r = document.querySelector('#protoTab').getBoundingClientRect(); const e = document.elementFromPoint(r.left + 7, r.top + r.height / 2); return e ? (e.id || e.tagName) : null; }")
            R["proto_tab"][f"390 under backdrop of {dlg}"] = under
            check(under != "protoTab", f"proto tab above the backdrop of {dlg}")
            page.keyboard.press("Escape")
            settle(page)
        # the open reveal runs when motion is allowed
        run(page, "k1")
        page.click("#chargesBtn")
        R["motion"]["open reveal animations (no-preference)"] = page.evaluate("document.getAnimations().filter(a => a.effect && a.effect.target && a.effect.target.id === 'chargesBody').length")
        check(R["motion"]["open reveal animations (no-preference)"] == 1, "no height reveal when opening a section")
        settle(page, 260)
        clip_audit(page, "390 run")
        ctx.close()

        # ================= 360 x 780 =================
        ctx, page = new_page(360, 780)
        shot(page, "k1-360")
        overflow360(page, "K1")
        tab_check(page, "360 K1")
        folded_k1(page, "360")
        pos["K1 360"] = page.evaluate(JS_POS)
        toggles(page, "360")
        for key in ["k1open", "k2", "s1", "s2", "s2rate", "s3", "s4ok", "s4fail", "s5", "s6", "s7", "w1", "w2"]:
            run(page, key)
            overflow360(page, key.upper())
            tab_check(page, f"360 {key.upper()}")
            # and with each section open
            for k in ("people", "charges"):
                if secs(page)[k]["expanded"] == "false":
                    page.click(f"#{k}Btn")
                    settle(page, 260)
                    overflow360(page, f"{key.upper()} {k} open")
                    page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
                    settle(page, 60)
                    overflow360(page, f"{key.upper()} {k} open, page end")
                    page.evaluate("window.scrollTo(0, 0)")
                    page.click(f"#{k}Btn")
                    settle(page, 120)
        run(page, "s7")
        v = secs(page)
        R["sections"]["S7 360"] = v["people"]
        check(v["people"]["summaryFits"] and v["people"]["summaryLines"] == 1 and v["people"]["summary"].endswith("more"), f"S7 360 summary {v['people']}")
        shot(page, "s7-360")
        run(page, "k1open")
        shot(page, "k1-open-360")
        shot(page, "k1-open-360-full", full=True)
        strip_checks(page, "360 K1 both open")
        R["targets"]["360 K1 both open"] = page.evaluate(JS_TARGETS)
        run(page, "s5")
        shot(page, "s5-360")
        run(page, "k1")
        strip_checks(page, "360 K1")
        run(page, "w2")
        strip_checks(page, "360 W2")
        run(page, "s7")
        strip_checks(page, "360 S7", min_seen=4)
        run(page, "w1")
        R["figures"]["W1 strip 360"] = text(page, "#stripInfo")
        check(R["figures"]["W1 strip 360"] == "TotalRM 1,193.87", f"W1 strip 360 {R['figures']['W1 strip 360']}")
        page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        settle(page)
        overflow360(page, "W1 page end")
        shot(page, "w1-360")
        page.click("#splitsBtn")
        page.wait_for_selector("#splitsDlg[open]")
        settle(page, 350)
        overflow360(page, "W1 sheet")
        R["figures"]["W1 sheet rows"] = rows(page)
        R["figures"]["W1 receipt"] = page.evaluate(JS_RECEIPT)
        check(R["figures"]["W1 receipt"]["total"] == "RM 1,193.87", "W1 total in the sheet")
        check([r["share"] for r in R["figures"]["W1 sheet rows"]][0] == "RM 1,153.65", f"W1 Aisyah split {R['figures']['W1 sheet rows']}")
        coll = page.evaluate("""() => { const out = []; const hit = (a, b) => a.left < b.right - 0.5 && b.left < a.right - 0.5 && a.top < b.bottom - 0.5 && b.top < a.bottom - 0.5;
          for (const row of document.querySelectorAll('#rbody .r-splits li, #rbody .r-check, #rbody .r-lines > div')) { const p = [...row.children];
            for (let i = 0; i < p.length; i++) for (let j = i + 1; j < p.length; j++) if (hit(p[i].getBoundingClientRect(), p[j].getBoundingClientRect())) out.push(row.textContent); }
          const a = document.querySelector('#rTotal'); if (a && a.scrollWidth > a.clientWidth + 0.5) out.push('total figure too wide');
          return out; }""")
        R["figures"]["W1 360 collisions"] = coll
        check(not coll, f"W1 360 collisions {coll}")
        shot(page, "w1-360-sheet")
        page.keyboard.press("Escape")
        settle(page)
        run(page, "k1")
        page.click("#splitsBtn")
        page.wait_for_selector("#splitsDlg[open]")
        settle(page, 350)
        overflow360(page, "P2")
        R["figures"]["sheet spare line 360"] = text(page, "#splitsDlg #spareLine")
        check(R["figures"]["sheet spare line 360"] == "1 sen left over", "1 sen left over is not in the sheet at 360")
        check(text(page, "#splitsH") == "Splits", "receipt heading in the sheet at 360")
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
        v = secs(page)
        R["sections"]["1280 K1"] = v
        check(not v["people"]["headerShown"] and not v["charges"]["headerShown"] and v["people"]["bodyShown"] and v["charges"]["bodyShown"], f"1280: a section header shows or a body is folded {v}")
        heads = page.evaluate("[...document.querySelectorAll('#work h2')].filter(h => h.getClientRects().length).map(h => h.textContent.trim())")
        R["sections"]["1280 visible headings"] = heads
        check(heads == ["People", "Charges", "Split", "Items"], f"1280 headings {heads}")
        no_shares(page, "1280 K1")
        check(text(page, "#splitsH") == "Splits", "receipt heading on the card")
        check(page.eval_on_selector("#stage", "e => e.getAttribute('aria-label')") == "Bill and splits", "the card's region name")
        tab_check(page, "1280 K1")
        R["targets"]["1280 K1"] = page.evaluate(JS_TARGETS)
        fr = page.evaluate("() => { const f = document.querySelector('#itemList'); return { sh: f.scrollHeight, ch: f.clientHeight, down: document.querySelector('#frameWrap').hasAttribute('data-down') }; }")
        R["frame"]["K1 1280"] = fr
        # the desktop page is G's, block for block
        for key in ("k1", "k2", "s7", "w2"):
            run(page, key)
            mine = page.evaluate(JS_BLOCKS, BLOCKS)
            diff = {s: {"g": gblocks[key][s], "g2": mine[s]} for s in BLOCKS if gblocks[key][s] != mine[s]}
            R["vs_g"][f"1280 {key.upper()} blocks that moved"] = diff
            R["vs_g"][f"1280 {key.upper()} blocks compared"] = len(BLOCKS)
            check(not diff, f"1280 {key.upper()} desktop layout differs from G {diff}")
        run(page, "k1")
        page.click("#spareBtn")
        page.wait_for_selector("#spareDlg[open]")
        settle(page, 250)
        shot(page, "p1-1280")
        pop = page.evaluate("() => { const p = document.querySelector('#spareDlg').getBoundingClientRect(); const s = document.querySelector('#splits').getBoundingClientRect(); return { popLeft: p.left, sharesRight: s.right }; }")
        R["figures"]["P1 1280 beside the card"] = pop
        check(pop["popLeft"] >= pop["sharesRight"], f"P1 covers the splits at 1280 {pop}")
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
        R["figures"]["S7 1280 splits"] = shares(page)
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
        for key in ["s1", "s2", "s2rate", "s3", "s4ok", "s4fail", "s5", "s6", "w1"]:
            run(page, key)
            noscroll(page, key.upper() + " (extra)")
            shot(page, f"{key}-1280")
            if key in ("s1", "s3"):
                no_shares(page, f"1280 {key.upper()}")
        run(page, "s2rate")
        rate = page.evaluate("() => ({ shown: document.querySelector('#svcErr').getBoundingClientRect().height > 0, svcTop: Math.round(document.querySelector('#svc').getBoundingClientRect().top), sstTop: Math.round(document.querySelector('#sst').getBoundingClientRect().top) })")
        R["sections"]["1280 S2 rate"] = rate
        check(rate["shown"] and rate["svcTop"] == rate["sstTop"], f"1280 rate error moves the other field {rate}")
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
        R["sections"]["768 K1"] = secs(page)
        check(R["sections"]["768 K1"]["people"]["expanded"] == "false" and R["sections"]["768 K1"]["people"]["headerShown"], "768 does not fold like a phone")
        page.click("#splitsBtn")
        page.wait_for_selector("#splitsDlg[open]")
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
        page.click("#peopleBtn")
        R["motion"]["reduced: open reveal animations"] = page.evaluate("document.getAnimations().length")
        R["motion"]["reduced: caret transition"] = page.evaluate("getComputedStyle(document.querySelector('#peopleBtn .sec-caret')).transitionDuration")
        check(R["motion"]["reduced: open reveal animations"] == 0 and R["motion"]["reduced: caret transition"] == "0s", "reduced motion still reveals a section")
        check(page.evaluate("document.querySelector('#peopleBtn').getAttribute('aria-expanded')") == "true", "reduced motion: People did not open")
        page.click("#splitsBtn")
        page.wait_for_selector("#splitsDlg[open]")
        R["motion"]["reduced: sheet animation"] = page.evaluate("getComputedStyle(document.querySelector('#splitsDlg .sheet')).animationName")
        check(R["motion"]["reduced: sheet animation"] == "none", "reduced motion still slides the sheet")
        ctx.close()
    finally:
        browser.close()

# ---------- G2 against G: the field positions at 390 ----------
R["vs_g"]["positions 390"] = {"g": gpos, "g2": pos}
R["vs_g"]["first Items field, K1 390"] = {"g": gpos["K1 390"]["firstItemField"], "g2": pos["K1 390"]["firstItemField"], "lifted_by": gpos["K1 390"]["firstItemField"] - pos["K1 390"]["firstItemField"]}
R["vs_g"]["Subtotal field, K2 390"] = {"g": gpos["K2 390"]["subtotalField"], "g2": pos["K2 390"]["subtotalField"], "lifted_by": gpos["K2 390"]["subtotalField"] - pos["K2 390"]["subtotalField"]}
R["vs_g"]["items above the strip, K1 390"] = {"g": [gpos["K1 390"]["itemsFullyAboveStrip"], gpos["K1 390"]["itemsStartedAboveStrip"]], "g2": [pos["K1 390"]["itemsFullyAboveStrip"], pos["K1 390"]["itemsStartedAboveStrip"]], "as": "[whole items, items begun]"}
R["vs_g"]["items above the strip, W2 390"] = {"g": [gpos["W2 390"]["itemsFullyAboveStrip"], gpos["W2 390"]["itemsStartedAboveStrip"]], "g2": [pos["W2 390"]["itemsFullyAboveStrip"], pos["W2 390"]["itemsStartedAboveStrip"]], "as": "[whole items, items begun]"}
check(pos["K1 390"]["firstItemField"] < gpos["K1 390"]["firstItemField"] - 150, f"the first Items field did not move up enough {R['vs_g']['first Items field, K1 390']}")
check(pos["K2 390"]["subtotalField"] < gpos["K2 390"]["subtotalField"] - 150, f"the Subtotal field did not move up enough {R['vs_g']['Subtotal field, K2 390']}")
check(pos["K1 390"]["firstItemField"] + 46 <= pos["K1 390"]["stripTop"], "the first Items field is under the strip")

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
    # G2: the section header rows and the rate error use existing pairs only
    ("G2 section name on the page (same pair as body text on the page)", t["text"], l2, 4.5),
    ("G2 section summary on the page (same pair as muted text on the page)", t["text-muted"], l2, 4.5),
    ("G2 section caret on the page (same pair as muted text, as a graphic)", t["text-muted"], l2, 3.0),
    ("G2 folded error marker, Check text and icon (same pair as error text on the page)", t["error-ink"], l2, 4.5),
    ("G2 rate error under a field (same pair as error text on the page)", t["error-ink"], l2, 4.5),
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
    ("strip: Splits button border", t["line-glass"], strip_glass, 3.0),
    ("strip: Splits button border over a field", t["line-glass"], strip_glass_field, 3.0),
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

R["asserts"] = {"passed": R["passes"], "failed": len(R["fails"]), "total": R["passes"] + len(R["fails"])}
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
    if v["bad"] or v["scrollWidth"] > v["clientWidth"]:
        print("overflow360", k, v["scrollWidth"], v["clientWidth"], v["bad"])
print("overflow360 states checked:", len(R["overflow_360"]))
for k, v in R["strip"].items():
    print("strip", k, json.dumps(v)[:300])
for k, v in R["proto_tab"].items():
    if isinstance(v, dict) and v.get("hits"):
        print("proto", k, v)
print("order:", R["order"])
for k, v in R["sections"].items():
    print("sections", k, "=>", json.dumps(v)[:400])
for k, v in R["rename"].items():
    print("rename", k, "=>", json.dumps(v)[:300])
for k, v in R["vs_g"].items():
    print("vs_g", k, "=>", json.dumps(v)[:400])
for k, v in R["figures"].items():
    print("fig", k, "=>", json.dumps(v)[:240])
for k, v in R["addup"].items():
    if "random draw" not in k:
        print("addup", k, v["sum"], v["total"], v["proof"])
for k, v in R["contrast"].items():
    if not v["pass"] or k.startswith("G2"):
        print("contrast", k, v["ratio"], "PASS" if v["pass"] else "FAIL")
print("motion:", R["motion"])
print("clipboard:", R["clipboard"])
print("targets:", R["targets"])
print("shots:", len(R["shots"]))
print("ASSERTS:", R["asserts"])
print("FAILS:", len(R["fails"]))
for f in R["fails"]:
    print("  FAIL", f)
