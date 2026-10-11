"""Render checks for the v1.1.0 final goldens (sdlc:design steps 6 and 8).

Run: python -B check_final.py
Opens every golden in final/ by its file:/// URL in headless Chromium at 390 x 844 (a touch phone, overlay
scrollbars), 360 x 780 (classic scrollbars, the stricter width) and 1280 x 800. Records console and page errors,
network requests (anything not file: or data: is aborted and logged), sideways scroll, page scroll at 1280 x 800,
touch targets, money sums, the strip against the inputs, and "Shares" in the visible text and accessible names.
Opens round-2/g2.html (read only, its Prototype states tab hidden by an injected style, the clipboard replaced by a
stand-in before load, Copy summary never pressed) at the same state and width, screenshots both, diffs the pixels
in a blank data: page and writes a side by side image. Recomputes the contrast table from system.css. Writes
results.json and shots/ beside this script. Every wait is bounded and the browser closes in a finally block.
"""
import base64
import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
FINAL = HERE.parent
ROUND2 = FINAL.parent / "round-2"
G2 = ROUND2 / "g2.html"
SHOTS = HERE / "shots"
SHOTS.mkdir(exist_ok=True)
WAIT_MS = 4000
SIZES = [(390, 844, True), (360, 780, False), (1280, 800, False)]

# golden file -> how g2 reaches the same state (its Prototype states keys, then design controls)
RECIPES = {
    "bill-items.html": ["k1"],
    "bill-items-open.html": ["k1open"],
    "bill-even.html": ["k2"],
    "spare-sen.html": ["p1"],
    "spare-sen-one.html": ["k2", "sheet", "spare", "one", "ben"],
    "spare-sen-random.html": ["k2", "random-bc", "sheet", "spare"],
    "splits-sheet.html": ["p2"],
    "new-bill-dialog.html": ["m1"],
    "bill-empty.html": ["s1"],
    "amount-error.html": ["s2"],
    "rate-error.html": ["s2rate"],
    "bill-unassigned.html": ["s3"],
    "summary-copied.html": ["s4ok"],
    "copy-blocked.html": ["s4fail"],
    "save-warning.html": ["s5"],
    "bill-unreadable.html": ["s6", "people"],
    "bill-twelve.html": ["s7"],
    "bill-large.html": ["w1"],
    "states.html": None,
}
OPEN_SECTION = {"bill-items-open.html", "bill-empty.html", "bill-unreadable.html", "rate-error.html"}

CLIP_STUB = """
(() => {
  window.__clipWrites = 0; window.__execCopy = 0;
  const stub = { __stub: true, writeText() { window.__clipWrites++; return Promise.resolve(); }, write() { window.__clipWrites++; return Promise.resolve(); },
                 readText() { return Promise.resolve(''); }, read() { return Promise.resolve([]); } };
  Object.defineProperty(Navigator.prototype, 'clipboard', { get() { return stub; }, configurable: true });
  const ex = Document.prototype.execCommand;
  Document.prototype.execCommand = function (cmd, ...rest) { if (/^(copy|cut)$/i.test(String(cmd))) { window.__execCopy++; return false; } return ex.call(this, cmd, ...rest); };
})();
"""

R = {"console_errors": [], "page_errors": [], "network": [], "fails": [], "passes": 0, "static": {}, "pages": {},
     "contrast": {}, "markdown": {}, "clipboard": {}, "summary": {}}


def check(cond, label):
    if cond:
        R["passes"] += 1
    else:
        R["fails"].append(label)
    return cond


# ---------- static file checks ----------
css = (FINAL / "system.css").read_text(encoding="utf-8")
g2src = G2.read_text(encoding="utf-8")
g2_syms = re.findall(r"<symbol[^\n]+</symbol>", g2src)
g2_defs = re.search(r"<defs>.*?</defs>", g2src, re.S).group(0)
present = [f for f in RECIPES if (FINAL / f).exists()]
R["static"]["goldens present"] = present
for f in present:
    src = (FINAL / f).read_text(encoding="utf-8")
    first = re.search(r"<style>\n(.*?)</style>", src, re.S)
    s = {"first style is system.css": bool(first) and first.group(1) == css,
         "symbol lines as g2": re.findall(r"<symbol[^\n]+</symbol>", src) == g2_syms,
         "gradient defs as g2": g2_defs in src,
         "script tags": src.count("<script"),
         "remote urls": len(re.findall(r"https?://(?!www\.w3\.org/2000/svg)", src)),
         "em dashes": src.count("\u2014"), "en dashes": src.count("\u2013"),
         "mark svgs": src.count('class="mark"'),
         "md present": (FINAL / f.replace(".html", ".md")).exists()}
    R["static"][f] = s
    check(s["first style is system.css"], f"{f}: first <style> is not system.css byte for byte")
    check(s["symbol lines as g2"] and s["gradient defs as g2"], f"{f}: icon sprite differs from g2")
    check(s["script tags"] == 0, f"{f}: has a script")
    check(s["remote urls"] == 0, f"{f}: remote url")
    check(s["em dashes"] == 0 and s["en dashes"] == 0, f"{f}: long dash")
    check(s["mark svgs"] == 1, f"{f}: mark svg count {s['mark svgs']}")
for p in sorted(FINAL.glob("*.md")) + [FINAL / "system.css", FINAL / "LINKS.json"]:
    if not p.exists():
        continue
    t = p.read_text(encoding="utf-8")
    d = {"em": t.count("\u2014"), "en": t.count("\u2013")}
    if p.suffix == ".md":
        bad, fence = [], False
        for i, line in enumerate(t.splitlines(), 1):
            if line.startswith("```"):
                fence = not fence
                continue
            if fence or line.lstrip().startswith("|"):
                continue
            prose = re.sub(r"`[^`]*`", "", line)
            if ":" in prose or ";" in prose:
                bad.append(f"{i}: {line[:90]}")
        d["prose colons or semicolons"] = bad[:12]
        check(not bad, f"{p.name}: colon or semicolon in prose {bad[:3]}")
    R["markdown"][p.name] = d
    check(d["em"] == 0 and d["en"] == 0, f"{p.name}: long dash")

# ---------- page helpers ----------
JS_VIS = """(sel) => [...document.querySelectorAll(sel)].find(e => e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden') || null"""
JS_SUMS = """() => {
  const vis = (e) => e && e.getClientRects().length > 0;
  const c = (s) => s == null ? null : Number(String(s).replace(/[^0-9]/g, ''));
  const out = {};
  const bodies = [...document.querySelectorAll('.rbody')].filter(vis);
  const anyBody = bodies[0] || document.querySelector('.rbody');
  const read = (b) => {
    if (!b) return null;
    const t = b.querySelector('.r-amount');
    const lines = [...b.querySelectorAll('.r-lines dd')].map(d => c(d.textContent));
    const rows = [...b.querySelectorAll('.r-splits li')].map(li => {
      const wk = li.querySelector('.wk');
      const parts = wk ? wk.textContent.split('+').map(x => c(x)) : null;
      return { name: li.querySelector('.nm').textContent, share: c(li.querySelector('.amt').textContent), parts };
    });
    const proof = b.querySelector('.r-check .amt');
    const pw = b.querySelector('.r-check .wk');
    return { total: t ? c(t.textContent) : null, lines, rows, proof: proof ? c(proof.textContent) : null,
             proofParts: pw ? pw.textContent.split('+').map(x => c(x)) : null,
             spare: b.querySelector('.r-spare p') ? b.querySelector('.r-spare p').textContent : null };
  };
  out.visible = bodies.length;
  out.receipt = read(anyBody);
  const st = document.querySelector('#stripTotal');
  out.stripTotal = st ? c(st.textContent) : null;
  const prices = [...document.querySelectorAll('.item .money input')].map(i => i.value);
  out.prices = prices;
  return out;
}"""
JS_OVERFLOW = """() => {
  const vw = document.documentElement.clientWidth; const bad = [];
  for (const el of document.querySelectorAll('body *')) {
    if (el.closest('.sprite, .sr, dialog:not([open]), [hidden], title')) continue;
    const r = el.getBoundingClientRect();
    if (!r.width && !r.height) continue;
    if (r.right > vw + 0.5 || r.left < -0.5) bad.push((el.id ? '#' + el.id : el.tagName.toLowerCase() + '.' + (el.getAttribute('class') || '')) + ' ' + Math.round(r.left) + '..' + Math.round(r.right));
  }
  return { scrollWidth: document.documentElement.scrollWidth, clientWidth: vw, bad: bad.slice(0, 12) };
}"""
JS_NOSCROLL = """() => { const de = document.documentElement; const box = (s) => { const e = document.querySelector(s); return e && e.getClientRects().length ? { sh: e.scrollHeight, ch: e.clientHeight } : null; };
  return { docH: de.scrollHeight, bodyH: document.body.scrollHeight, vh: innerHeight, stage: box('.stage'), work: box('.work') }; }"""
JS_TARGETS = """() => { const small = [];
  for (const b of document.querySelectorAll('button, input, .mode-sw label, .choice, .pill-face, .tap')) {
    if (b.closest('dialog:not([open]), [hidden], .proto-panel') || b.classList.contains('proto-tab') || b.type === 'radio') continue;
    const r = b.getBoundingClientRect();
    if (!r.width || !b.getClientRects().length) continue;
    if (r.height < 43.5 || r.width < 43.5) small.push((b.id || b.getAttribute('aria-label') || b.textContent.trim().slice(0, 20) || b.className) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
  }
  return small; }"""
JS_STRIP_FIRST = """() => { const s = document.querySelector('#strip'); if (!s || !s.getClientRects().length) return null;
  const top = s.getBoundingClientRect().top; const b = (sel) => { const e = document.querySelector(sel); return e && e.getClientRects().length ? Math.round(e.getBoundingClientRect().bottom) : null; };
  return { stripTop: Math.round(top), people: b('#peopleBlk'), charges: b('#chargesBlk'), split: b('#splitBlk') }; }"""
JS_STRIP_END = """() => { const s = document.querySelector('#strip').getBoundingClientRect(); const fw = document.querySelector('.frame-wrap'); const f = fw && fw.getClientRects().length ? fw.getBoundingClientRect() : null;
  const hits = [];
  for (const el of document.querySelectorAll('#work input:not([type=radio]), #work button, #work .mode-sw label, #work .err:not([hidden]), #work .hint')) {
    if (el.closest('[hidden]') || !el.getClientRects().length) continue;
    const r = el.getBoundingClientRect(); let top = r.top, bottom = r.bottom;
    if (f && fw.contains(el)) { top = Math.max(top, f.top); bottom = Math.min(bottom, f.bottom); if (bottom <= top) continue; }
    if (bottom > s.top + 0.5 && top < s.bottom) hits.push((el.id || el.getAttribute('aria-label') || el.textContent.trim().slice(0, 24)) + ' ' + Math.round(top) + '..' + Math.round(bottom));
  }
  return { stripTop: Math.round(s.top), scrollY: Math.round(scrollY), docH: document.documentElement.scrollHeight, hits }; }"""
JS_FOCUS = """() => { const a = document.activeElement; const work = document.querySelector('#work');
  const inWork = !!work && work.contains(a); const box = a.type === 'radio' ? a.nextElementSibling : a; const r = box.getBoundingClientRect();
  const s = document.querySelector('#strip').getBoundingClientRect(); const fw = document.querySelector('.frame-wrap');
  let ok = r.top >= -0.5 && r.bottom <= s.top + 0.5;
  if (fw && fw.contains(a)) { const f = fw.getBoundingClientRect(); ok = ok && r.top >= f.top - 0.5 && r.bottom <= f.bottom + 0.5; }
  return { inWork, id: a.id || a.getAttribute('aria-label') || a.textContent.trim().slice(0, 30), top: Math.round(r.top), bottom: Math.round(r.bottom), stripTop: Math.round(s.top), ok }; }"""
SEL = ['.top', '.brand', '#newBill', '.notes', '.note', '.card', '.r-amount', '.r-lines', '.r-head', '.r-splits', '.r-check', '.r-spare', '.chip-btn',
       '.r-copy', '.r-empty', '.r-msg', '.status', '#peopleBtn', '#chargesBtn', '.people', '#addPerson', '#svc', '#sst', '.err', '.hint', '#splitBlk',
       '.mode-sw', '#evenSub', '#addItem', '.frame-wrap', '.item', '.tap', '.strip', '.strip-info', '#splitsBtn', '#stripCopy', '.sheet', '.sheet-scroll',
       '.pop', '.pick', '.modal']
JS_RECTS = """(sels) => { const out = {}; for (const s of sels) { const e = [...document.querySelectorAll(s)].find(x => x.getClientRects().length && !x.closest('.proto-panel'));
  if (!e) { out[s] = null; continue; } const r = e.getBoundingClientRect(); out[s] = [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)]; } return out; }"""
JS_TEXT = """() => { const p = document.querySelector('.proto-panel'); if (p) p.hidden = true; const t = document.querySelector('.proto-tab'); if (t) t.hidden = true;
  return document.body.innerText.replace(/[ \\t]+/g, ' ').split('\\n').map(s => s.trim()).filter(Boolean); }"""
JS_INPUTS = """() => [...document.querySelectorAll('input')].filter(i => i.getClientRects().length || (i.type === 'radio' && i.closest('label, .mode-sw, .pill, .choice') && i.closest('label, .mode-sw, .pill, .choice').getClientRects().length))
  .map(i => [i.type, i.value, i.placeholder || '', i.getAttribute('aria-label') || '', i.checked ? 'checked' : '', i.getAttribute('aria-invalid') || ''])"""
SHARES_RE = re.compile(r"\bshares?\b", re.I)
JS_STYLE = """(sel) => { const e = [...document.querySelectorAll(sel)].find(x => x.getClientRects().length); if (!e) return null; const s = getComputedStyle(e);
  const keys = ['color', 'backgroundColor', 'borderTopColor', 'borderTopWidth', 'boxShadow', 'fontSize', 'fontWeight', 'lineHeight', 'fontFamily', 'paddingTop', 'paddingLeft', 'paddingRight', 'borderRadius', 'minHeight', 'gap', 'textAlign'];
  const style = {}; for (const k of keys) style[k] = s[k];
  return { style, text: e.textContent.replace(/\\s+/g, ' ').trim() }; }"""
# (label, selector in states.html, how g2 reaches it, selector in g2)
SPEC_PAIRS_PHONE = [
    ("S5 note", ".note.is-warn", ["s5"], ".note.is-warn"),
    ("S5 note text", ".note.is-warn p", ["s5"], ".note.is-warn p"),
    ("S4 copied, strip", ".strip .status:not(.is-fail)", ["s4ok"], "#stripStatus"),
    ("S4 blocked, strip", ".strip .status.is-fail", ["s4fail"], "#stripStatus"),
    ("S2 Subtotal field", ".sub-field.is-bad", ["s2"], "#evenField"),
    ("S2 Subtotal error", "#evenErr", ["s2"], "#evenErr"),
    ("Check marker, folded", ".sec-btn.is-bad .sec-sum", ["s2rate", "fold-charges"], "#chargesSum"),
    ("By item, nothing to work out, strip", ".strip .s-msg", ["s1", "byitem"], "#stripMsg"),
]
SPEC_PAIRS_DESK = [
    ("S4 copied, card", ".card .status:not(.is-fail)", ["s4ok"], "#cardStatus"),
    ("S4 blocked, card", ".card .status.is-fail", ["s4fail"], "#cardStatus"),
    ("S4 Copy summary, card", ".card .r-copy", ["s4ok"], "#copyBtn"),
]


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
            out.append([role, str(nm)])
    return out


DIFF_JS = """async ([a, b]) => {
  const load = (src) => new Promise((ok, bad) => { const i = new Image(); i.onload = () => ok(i); i.onerror = bad; i.src = 'data:image/png;base64,' + src; });
  const [ia, ib] = await Promise.all([load(a), load(b)]);
  const w = Math.max(ia.width, ib.width), h = Math.max(ia.height, ib.height);
  const cv = (img) => { const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d'); x.fillStyle = '#ff00ff'; x.fillRect(0, 0, w, h); x.drawImage(img, 0, 0); return x.getImageData(0, 0, w, h).data; };
  const da = cv(ia), db = cv(ib);
  const CELL = 8, gw = Math.ceil(w / CELL), gh = Math.ceil(h / CELL), grid = new Uint16Array(gw * gh);
  let n = 0;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const k = (y * w + x) * 4;
    const d = Math.max(Math.abs(da[k] - db[k]), Math.abs(da[k + 1] - db[k + 1]), Math.abs(da[k + 2] - db[k + 2]));
    if (d > 24) { n++; grid[Math.floor(y / CELL) * gw + Math.floor(x / CELL)]++; } }
  const seen = new Uint8Array(gw * gh), boxes = [];
  for (let i = 0; i < gw * gh; i++) { if (grid[i] < 3 || seen[i]) continue; let q = [i], x0 = 1e9, y0 = 1e9, x1 = -1, y1 = -1, px = 0; seen[i] = 1;
    while (q.length) { const j = q.pop(), gx = j % gw, gy = Math.floor(j / gw); px += grid[j]; x0 = Math.min(x0, gx); y0 = Math.min(y0, gy); x1 = Math.max(x1, gx); y1 = Math.max(y1, gy);
      for (const [dx, dy] of [[1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,-1],[1,-1],[-1,1]]) { const nx = gx + dx, ny = gy + dy; if (nx < 0 || ny < 0 || nx >= gw || ny >= gh) continue; const m = ny * gw + nx; if (!seen[m] && grid[m] >= 3) { seen[m] = 1; q.push(m); } } }
    boxes.push([x0 * CELL, y0 * CELL, (x1 + 1) * CELL - x0 * CELL, (y1 + 1) * CELL - y0 * CELL, px]); }
  boxes.sort((p, q) => q[4] - p[4]);
  const GAP = 16, out = document.createElement('canvas'); out.width = w * 3 + GAP * 2; out.height = h; const o = out.getContext('2d');
  o.fillStyle = '#ffffff'; o.fillRect(0, 0, out.width, out.height); o.drawImage(ia, 0, 0); o.drawImage(ib, w + GAP, 0);
  o.drawImage(ia, (w + GAP) * 2, 0); o.fillStyle = 'rgba(0,0,0,0.55)'; o.fillRect((w + GAP) * 2, 0, w, h);
  o.strokeStyle = '#ff2d55'; o.lineWidth = 2; for (const bx of boxes) o.strokeRect((w + GAP) * 2 + bx[0], bx[1], bx[2], bx[3]);
  return { w, h, diffPixels: n, ratio: Math.round(n / (w * h) * 100000) / 1000, boxes: boxes.slice(0, 20), png: out.toDataURL('image/png').split(',')[1] };
}"""

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, ignore_default_args=["--hide-scrollbars"])
    try:
        def new_page(w, h, phone, url, reduced=True, tag=""):
            ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, is_mobile=phone, has_touch=phone,
                                      reduced_motion="reduce" if reduced else "no-preference")
            ctx.add_init_script(CLIP_STUB)
            pg = ctx.new_page()
            pg.set_default_timeout(WAIT_MS)
            pg.on("console", lambda m: R["console_errors"].append(f"{tag}: {m.text}") if m.type == "error" else None)
            pg.on("pageerror", lambda e: R["page_errors"].append(f"{tag}: {e}"))

            def route(r):
                if r.request.url.startswith(("file:", "data:")):
                    r.continue_()
                else:
                    R["network"].append(f"{tag}: {r.request.url}")
                    r.abort()
            pg.route("**/*", route)
            pg.on("request", lambda rq: R["network"].append(f"{tag}: {rq.url}") if not rq.url.startswith(("file:", "data:")) else None)
            pg.goto(url, wait_until="load")
            # a touch phone flashes its overlay scrollbar on load, so wait for it to fade before any screenshot
            pg.wait_for_timeout(1300 if phone else 250)
            return ctx, pg

        def g2_state(page, steps, desk):
            page.add_style_tag(content=".proto-tab, .proto-panel { display: none !important; }")
            for st in steps:
                if st == "fold-charges":
                    if not desk:
                        page.click("#chargesBtn"); page.wait_for_timeout(250)
                elif st == "byitem":
                    page.click('label[for="modeItem"]'); page.wait_for_timeout(250)
                elif st in ("sheet", "spare", "one", "ben", "random-bc", "people"):
                    if st == "sheet" and not desk:
                        page.click("#splitsBtn"); page.wait_for_timeout(300)
                    elif st == "spare":
                        page.click("#spareBtn"); page.wait_for_selector("#spareDlg[open]"); page.wait_for_timeout(250)
                    elif st == "one":
                        page.click('label.choice:has(input[value="one"])'); page.wait_for_timeout(200)
                    elif st == "ben":
                        page.click('#pickList label:has(input[value="2"]) .pill-face'); page.wait_for_timeout(250)
                    elif st == "random-bc":
                        page.evaluate("""() => { const S = window.__g.state(); S.spare = { rule: 'random', pid: null, perm: [2, 3, 1] };
                          document.querySelector('#svc').dispatchEvent(new Event('input', { bubbles: true })); }""")
                        page.wait_for_timeout(150)
                    elif st == "people" and not desk:
                        page.click("#peopleBtn"); page.wait_for_timeout(350)
                else:
                    page.evaluate(f"() => {{ if (document.activeElement) document.activeElement.blur(); window.__g.run('{st}'); }}")
                    page.wait_for_timeout(250)
            page.mouse.move(1, 1)
            page.evaluate("() => { if (document.activeElement) document.activeElement.blur(); }")
            page.wait_for_timeout(250)

        diff_ctx = browser.new_context(viewport={"width": 400, "height": 300})
        diff_page = diff_ctx.new_page()
        diff_page.set_default_timeout(60000)
        diff_page.set_content("<!doctype html><title>diff</title><body></body>")

        for f in present:
            url = (FINAL / f).as_uri()
            P = R["pages"].setdefault(f, {})
            for (w, h, phone) in SIZES:
                desk = w >= 1024
                tag = f"{f} {w}"
                out = P.setdefault(str(w), {})
                ctx, page = new_page(w, h, phone, url, tag=tag)
                name = f.replace(".html", "")
                gshot = page.screenshot(path=str(SHOTS / f"{name}-{w}.png"))
                out["rects"] = page.evaluate(JS_RECTS, SEL)
                # click points for LINKS.json (the Chen toggle on Mee goreng mamak, and the backdrop above a sheet or dialog)
                out["link_points"] = page.evaluate("""() => { const c = (e) => { if (!e || !e.getClientRects().length) return null; const r = e.getBoundingClientRect();
                  return { x: Math.round(r.left + r.width / 2), y: Math.round(r.top + r.height / 2), inView: r.top >= 0 && r.bottom <= innerHeight }; };
                  const sheet = document.querySelector('.sheet-dlg[open] .sheet'), pop = document.querySelector('.pop[open]'), modal = document.querySelector('.modal[open]');
                  return { chenOnMee: c(document.querySelector('.taps[aria-label="Who had Mee goreng mamak"] .tap:nth-child(3)')),
                           sheetTop: sheet && sheet.getClientRects().length ? Math.round(sheet.getBoundingClientRect().top) : null,
                           popRect: pop ? [Math.round(pop.getBoundingClientRect().left), Math.round(pop.getBoundingClientRect().top), Math.round(pop.getBoundingClientRect().right), Math.round(pop.getBoundingClientRect().bottom)] : null,
                           modalTop: modal ? Math.round(modal.getBoundingClientRect().top) : null }; }""")
                if not desk:
                    page.screenshot(path=str(SHOTS / f"{name}-{w}-full.png"), full_page=True)
                # sideways scroll, every width
                ov = page.evaluate(JS_OVERFLOW)
                out["sideways"] = ov
                check(ov["scrollWidth"] <= ov["clientWidth"] and not ov["bad"], f"{tag}: sideways overflow {ov}")
                if desk:
                    ns = page.evaluate(JS_NOSCROLL)
                    out["page_scroll"] = ns
                    check(ns["docH"] <= ns["vh"] and ns["bodyH"] <= ns["vh"], f"{tag}: page scrolls {ns}")
                    for k in ("stage", "work"):
                        if ns[k]:
                            check(ns[k]["sh"] <= ns[k]["ch"], f"{tag}: {k} column overflows {ns[k]}")
                small = page.evaluate(JS_TARGETS)
                out["targets_under_44"] = small
                check(not small, f"{tag}: targets under 44 px {small}")
                sums = page.evaluate(JS_SUMS)
                out["sums"] = sums
                rc = sums["receipt"]
                if rc and rc["total"] is not None and f != "states.html":
                    check(sum(rc["lines"]) == rc["total"], f"{tag}: bill lines do not add to the Total {rc}")
                    if rc["rows"]:
                        check(sum(r["share"] for r in rc["rows"]) == rc["total"] == rc["proof"], f"{tag}: splits do not add to the Total {rc}")
                        for r in rc["rows"]:
                            if r["parts"]:
                                check(sum(r["parts"]) == r["share"], f"{tag}: {r['name']} items + charges != split {r}")
                        if rc["proofParts"]:
                            check(sum(rc["proofParts"]) == rc["total"], f"{tag}: proof working != Total {rc['proofParts']}")
                            check(rc["proofParts"][0] == rc["lines"][0] and rc["proofParts"][1] == rc["lines"][1] + rc["lines"][2], f"{tag}: proof working != bill lines")
                            check(sum(r["parts"][0] for r in rc["rows"]) == rc["lines"][0], f"{tag}: items column != Subtotal")
                    if sums["stripTotal"] is not None:
                        check(sums["stripTotal"] == rc["total"], f"{tag}: strip Total != receipt Total")
                    good = [p for p in sums["prices"] if re.fullmatch(r"\d{1,5}(\.\d{1,2})?", p.strip())]
                    if sums["prices"] and rc["lines"]:
                        cents = sum(int(round(float(p) * 100)) for p in good)
                        check(cents == rc["lines"][0], f"{tag}: item prices {cents} != Subtotal {rc['lines'][0]}")
                # strip against inputs (phone, strip shown, no dialog)
                first = page.evaluate(JS_STRIP_FIRST)
                if first and not page.evaluate("!!document.querySelector('dialog[open]')"):
                    # with every section folded, People, Charges and Split sit above the strip on the first screen.
                    # A golden with a section open is recorded only, since the open section may fill the screen
                    sv = {"first_screen": first, "first_screen_asserted": f not in OPEN_SECTION}
                    if f not in OPEN_SECTION:
                        check(all(first[k] is None or first[k] <= first["stripTop"] for k in ("people", "charges", "split")),
                              f"{tag}: People, Charges or Split under the strip on the first screen {first}")
                    page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
                    page.wait_for_timeout(80)
                    end = page.evaluate(JS_STRIP_END)
                    sv["page_end"] = end
                    check(not end["hits"], f"{tag}: the strip covers a control at the page end {end}")
                    page.evaluate("window.scrollTo(0, 0)")
                    page.wait_for_timeout(60)
                    page.focus("#newBill")
                    bad, seen = [], 0
                    for _ in range(140):
                        page.keyboard.press("Tab")
                        page.wait_for_timeout(25)
                        fo = page.evaluate(JS_FOCUS)
                        if fo["id"] in ("splitsBtn", "stripCopy"):
                            break
                        if not fo["inWork"]:
                            continue
                        seen += 1
                        if not fo["ok"]:
                            bad.append(fo)
                    sv["tabbed"] = seen
                    sv["covered_while_focused"] = bad[:6]
                    check(seen >= 3 and not bad, f"{tag}: a focused control sat under the strip {bad[:3]} (seen {seen})")
                    out["strip"] = sv
                    page.evaluate("window.scrollTo(0, 0)")
                    page.evaluate("() => document.activeElement && document.activeElement.blur()")
                    page.wait_for_timeout(60)
                # Shares, visible text and accessible names
                txt = page.evaluate("document.body.innerText")
                names = ax_names(page)
                hits = SHARES_RE.findall(txt) + [n[1] for n in names if SHARES_RE.search(n[1])]
                out["shares_word"] = {"hits": hits[:6], "names_checked": len(names)}
                # an inert page (a dialog's stand-in) exposes few names, so only prove the tree was read
                check(not hits and len(names) > 0, f"{tag}: 'Shares' read {hits[:3]}")
                out["text"] = page.evaluate(JS_TEXT)
                out["inputs"] = page.evaluate(JS_INPUTS)
                out["ax"] = names
                ctx.close()

                # g2 at the same state and width
                steps = RECIPES[f]
                if steps:
                    gctx, gp = new_page(w, h, phone, G2.as_uri(), tag=f"g2 for {tag}")
                    g2_state(gp, steps, desk)
                    gp.screenshot(path=str(SHOTS / f"g2-{name}-{w}.png"))
                    g2shot = gp.screenshot()
                    grects = gp.evaluate(JS_RECTS, SEL)
                    gtext = gp.evaluate(JS_TEXT)
                    ginputs = gp.evaluate(JS_INPUTS)
                    gnames = ax_names(gp)
                    clip = gp.evaluate("() => ({ stub: !!(navigator.clipboard && navigator.clipboard.__stub), writes: window.__clipWrites, exec: window.__execCopy })")
                    R["clipboard"][f"g2 for {tag}"] = clip
                    check(clip["stub"] and clip["writes"] == 0 and clip["exec"] == 0, f"g2 for {tag}: clipboard touched {clip}")
                    gctx.close()
                    d = diff_page.evaluate(DIFF_JS, [base64.b64encode(gshot).decode(), base64.b64encode(g2shot).decode()])
                    (SHOTS / f"side-{name}-{w}.png").write_bytes(base64.b64decode(d.pop("png")))
                    out["vs_g2"] = {"diff": d,
                                    "rects_moved": {k: [out["rects"][k], grects[k]] for k in SEL if out["rects"][k] != grects[k]},
                                    "text_only_golden": [t for t in out["text"] if t not in gtext],
                                    "text_only_g2": [t for t in gtext if t not in out["text"]],
                                    "text_same_order": out["text"] == gtext,
                                    "inputs_same": out["inputs"] == ginputs,
                                    "inputs_golden": out["inputs"] if out["inputs"] != ginputs else "same",
                                    "inputs_g2": ginputs if out["inputs"] != ginputs else "same",
                                    "ax_only_golden": [n for n in names if n not in gnames][:30],
                                    "ax_only_g2": [n for n in gnames if n not in names][:30]}
                    # S6: the ruling. Record what differs from g2's own S6, where People stays folded
                    if f == "bill-unreadable.html":
                        gctx, gp = new_page(w, h, phone, G2.as_uri(), tag=f"g2 s6 unruled for {tag}")
                        g2_state(gp, ["s6"], desk)
                        raw = gp.screenshot()
                        gctx.close()
                        d2 = diff_page.evaluate(DIFF_JS, [base64.b64encode(gshot).decode(), base64.b64encode(raw).decode()])
                        (SHOTS / f"side-{name}-vs-g2-unruled-{w}.png").write_bytes(base64.b64decode(d2.pop("png")))
                        out["vs_g2_s6_unruled"] = d2
                # the specimen sheet: each piece against g2's own element in the same state, by computed style
                if f == "states.html" and w in (390, 1280):
                    pairs = SPEC_PAIRS_DESK if desk else SPEC_PAIRS_PHONE
                    res = {}
                    for label, ssel, steps, gsel in pairs:
                        ctx2, sp = new_page(w, h, phone, url, tag=f"{tag} spec")
                        mine = sp.evaluate(JS_STYLE, ssel)
                        ctx2.close()
                        gctx, gp = new_page(w, h, phone, G2.as_uri(), tag=f"g2 spec {label} {w}")
                        g2_state(gp, steps, desk)
                        theirs = gp.evaluate(JS_STYLE, gsel)
                        gctx.close()
                        # g2's header row summary starts with a visually hidden ", " (dropped at step 7, the row is described by its summary now)
                        same = mine is not None and theirs is not None and mine["style"] == theirs["style"] and mine["text"] == theirs["text"].removeprefix(", ")
                        res[label] = {"same": same, "states": mine, "g2": theirs}
                        check(same, f"{tag}: specimen {label} differs from g2 {mine} {theirs}")
                    out["specimen_vs_g2"] = res
                del out["ax"]
                del out["text"]
            # motion allowed: no errors, at 390
            mctx, mp = new_page(390, 844, True, url, reduced=False, tag=f"{f} 390 motion")
            mp.wait_for_timeout(2200)
            mctx.close()
        # LINKS.json: every file exists, every named control is on its source golden at that width, every point lands
        lpath = FINAL / "LINKS.json"
        if lpath.exists():
            links = json.loads(lpath.read_text(encoding="utf-8"))["links"]
            lres = []
            for ln in links:
                ok_files = (FINAL / ln["from"]).exists() and (FINAL / ln["to"]).exists()
                widths = [ln["width"]] if "width" in ln else [390, 360, 1280]
                for w in widths:
                    hgt = {390: 844, 360: 780, 1280: 800}[w]
                    lctx, lp2 = new_page(w, hgt, w == 390, (FINAL / ln["from"]).as_uri(), tag=f"links {ln['from']} {w}")
                    found = None
                    if "role" in ln:
                        loc = lp2.get_by_role(ln["role"], name=ln["name"], exact=True)
                        found = sum(1 for i in range(loc.count()) if loc.nth(i).is_visible() or ln["role"] == "radio")
                    elif "click" in ln:
                        found = lp2.evaluate("""([x, y]) => { const p = document.elementFromPoint(x, y); if (!p) return null;
                          const e = p.closest('button, label, input, .backdrop, .strip') || p;
                          const cls = typeof e.className === 'string' ? e.className : e.tagName;
                          return e.tagName.toLowerCase() + '.' + cls + ' ' + (e.getAttribute('aria-label') || e.textContent.trim().slice(0, 24)); }""", ln["click"])
                    else:
                        found = "key"
                    lctx.close()
                    good = ok_files and bool(found)
                    lres.append({"from": ln["from"], "to": ln["to"], "width": w, "trigger": ln.get("name") or ln.get("click") or ln.get("key"), "found": found})
                    check(good, f"LINKS {ln} at {w}: {found}")
            R["links"] = lres
        diff_ctx.close()
    finally:
        browser.close()

# ---------- contrast, recomputed from system.css (glass composited over what sits behind it) ----------
def parse_colour(s):
    s = s.strip()
    if s.startswith("#"):
        h = s[1:]
        return [int(h[i:i + 2], 16) for i in (0, 2, 4)] + [1.0]
    m = re.match(r"rgba?\(([^)]+)\)", s)
    parts = [p.strip() for p in m.group(1).split(",")]
    return [float(p) for p in parts[:3]] + [float(parts[3]) if len(parts) > 3 else 1.0]


def over(fg, bg):
    a = fg[3]
    return [fg[i] * a + bg[i] * (1 - a) for i in range(3)] + [1.0]


def lum(c):
    lin = [(v / 255) / 12.92 if v / 255 <= 0.04045 else (((v / 255) + 0.055) / 1.055) ** 2.4 for v in c[:3]]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return round((max(la, lb) + 0.05) / (min(la, lb) + 0.05), 2)


root = re.search(r":root \{(.*?)\n\}", css, re.S).group(1)
tok = {k: v.strip() for k, v in re.findall(r"--([\w-]+):\s*([^;]+);", root)}
t = {k: parse_colour(v) for k, v in tok.items() if v.startswith("#") or v.startswith("rgb")}
l1, l2, l3, field = t["l1"], t["l2"], t["l3"], t["field"]
card_glass = over(t["glass-hi"], over(t["glass-base"], l2))
strip_glass = over(t["glass-hi"], over(t["glass-dense"], l2))
strip_glass_field = over(t["glass-hi"], over(t["glass-dense"], field))
strip_glass_worst = over(t["glass-hi"], over(t["glass-dense"], t["text"]))
sheet_glass = over(t["glass-hi"], over(t["glass-dense"], over(t["scrim"], l2)))
sheet_glass_worst = over(t["glass-hi"], over(t["glass-dense"], over(t["scrim"], t["text"])))
scrim_page = over(t["scrim"], l2)
light_page = over(t["scrim-light"], l2)
light_sheet = over(t["scrim-light"], sheet_glass)
chip_on_card = over(parse_colour("rgba(14, 18, 25, 0.45)"), card_glass)
strip_btn = over(parse_colour("rgba(14, 18, 25, 0.5)"), strip_glass)
note_info_edge = over(parse_colour("rgba(124, 133, 247, 0.38)"), l1)
note_warn_edge = over(parse_colour("rgba(242, 192, 99, 0.45)"), l1)
pairs = [
    ("Body text on the page", t["text"], l2, 4.5),
    ("Body text on a field", t["text"], field, 4.5),
    ("Body text on the top bar and in the item frame (l1)", t["text"], l1, 4.5),
    ("Body text on a dialog (l3)", t["text"], l3, 4.5),
    ("Body text on hover in a dialog (l5)", t["text"], t["l5"], 4.5),
    ("Muted text on the page (labels, hint, summary)", t["text-muted"], l2, 4.5),
    ("Muted text on a field (placeholder, RM, %)", t["text-muted"], field, 4.5),
    ("Muted text in the item frame (untapped person)", t["text-muted"], l1, 4.5),
    ("Muted text on a dialog", t["text-muted"], l3, 4.5),
    ("Body text on the indigo tint, tapped person (frame)", t["text"], over(t["accent-tint"], l1), 4.5),
    ("Body text on the indigo tint, chosen mode (field)", t["text"], over(t["accent-tint"], field), 4.5),
    ("Body text on the indigo tint, chosen pill (dialog)", t["text"], over(t["accent-tint"], l3), 4.5),
    ("Copy summary text on its indigo fill", t["on-accent"], t["accent"], 4.5),
    ("Copy summary text on its hover fill", t["on-accent"], t["accent-hover"], 4.5),
    ("Start new bill text on its red fill", t["on-danger"], t["danger"], 4.5),
    ("Start new bill text on its hover fill", t["on-danger"], t["danger-hover"], 4.5),
    ("Indigo check on the tint, tapped person (frame)", t["accent-ink"], over(t["accent-tint"], l1), 3.0),
    ("Indigo radio dot and pill check on a dialog", t["accent-ink"], l3, 3.0),
    ("Indigo edge of a tapped person (frame)", t["accent-line"], l1, 3.0),
    ("Indigo edge of the chosen mode (field)", t["accent-line"], field, 3.0),
    ("Indigo edge of a chosen pill (dialog)", t["accent-line"], l3, 3.0),
    ("Control border on the page", t["line-strong"], l2, 3.0),
    ("Control border on a field", t["line-strong"], field, 3.0),
    ("Control border on the top bar and in the frame", t["line-strong"], l1, 3.0),
    ("Control border on a dialog", t["line-strong"], l3, 3.0),
    ("Radio ring, unchosen, on a dialog", t["line-strong"], l3, 3.0),
    ("Focus ring on the page", t["focus"], l2, 3.0),
    ("Focus ring on the top bar and in the frame", t["focus"], l1, 3.0),
    ("Focus ring on a dialog", t["focus"], l3, 3.0),
    ("Error text on the page (rate error, Check marker)", t["error-ink"], l2, 4.5),
    ("Error text in the frame (price error)", t["error-ink"], l1, 4.5),
    ("Error edge on a field", t["error-ink"], field, 3.0),
    ("S3 amber marker in the frame", t["warn-ink"], l1, 3.0),
    ("S5 text on the warning band", t["text"], t["warn-bg"], 4.5),
    ("S5 icon on the warning band", t["warn-ink"], t["warn-bg"], 3.0),
    ("S6 text on the note band", t["text"], t["info-bg"], 4.5),
    ("S6 icon on the note band", t["accent-ink"], t["info-bg"], 3.0),
    ("S6 dismiss X (muted) on the note band", t["text-muted"], t["info-bg"], 3.0),
    ("Card: Total figure", t["total-ink"], card_glass, 4.5),
    ("Card: body text (names, Total label, Adds up to)", t["text"], card_glass, 4.5),
    ("Card: muted text (bill lines, working, sen left over)", t["text-muted"], card_glass, 4.5),
    ("Card: indigo Adds up to figure, status tick", t["accent-ink"], card_glass, 4.5),
    ("Card: S3 warning icon", t["warn-ink"], card_glass, 3.0),
    ("Card: S4 failure icon", t["error-ink"], card_glass, 3.0),
    ("Card: chip text on the chip fill", t["text"], chip_on_card, 4.5),
    ("Card: chip border", t["line-glass"], card_glass, 3.0),
    ("Card: focus ring", t["focus"], card_glass, 3.0),
    ("Strip: Total figure", t["total-ink"], strip_glass, 4.5),
    ("Strip: body text (Total label, status, messages)", t["text"], strip_glass, 4.5),
    ("Strip: body text over a field", t["text"], strip_glass_field, 4.5),
    ("Strip: Splits button text on its fill", t["text"], strip_btn, 4.5),
    ("Strip: Splits button border", t["line-glass"], strip_glass, 3.0),
    ("Strip: Splits button border over a field", t["line-glass"], strip_glass_field, 3.0),
    ("Strip: warning icon (S3)", t["warn-ink"], strip_glass, 3.0),
    ("Strip: focus ring", t["focus"], strip_glass, 3.0),
    ("Strip, worst case: body text over an unblurred white line", t["text"], strip_glass_worst, 4.5),
    ("Sheet: Total figure", t["total-ink"], sheet_glass, 4.5),
    ("Sheet: body text", t["text"], sheet_glass, 4.5),
    ("Sheet: muted text", t["text-muted"], sheet_glass, 4.5),
    ("Sheet: indigo Adds up to figure", t["accent-ink"], sheet_glass, 4.5),
    ("Sheet: chip border", t["line-glass"], sheet_glass, 3.0),
    ("Sheet: Close X (muted)", t["text-muted"], sheet_glass, 3.0),
    ("Sheet, worst case: muted text over an unblurred white line", t["text-muted"], sheet_glass_worst, 4.5),
    ("Fallback card: muted text", t["text-muted"], t["glass-solid"], 4.5),
    ("Fallback card: indigo figure", t["accent-ink"], t["glass-solid"], 4.5),
    ("Fallback card: chip border", t["line-glass"], t["glass-solid"], 3.0),
    ("Dialog surface against the scrimmed page (M1, P2)", l3, scrim_page, 1.0),
    ("Dialog edge line (white 10% over l3) against the scrimmed page", over(parse_colour("rgba(255, 255, 255, 0.10)"), l3), scrim_page, 1.0),
    ("Dialog edge (l5 grab) on the sheet", t["l5"], sheet_glass, 1.0),
    ("P1 surface against the light scrim over the page (desktop)", l3, light_page, 1.0),
    ("P1 surface against the light scrim over the sheet (phone)", l3, light_sheet, 1.0),
]
for label, fg, bg, need in pairs:
    r = ratio(fg, bg)
    R["contrast"][label] = {"ratio": r, "need": need, "pass": r >= need}
    check(r >= need, f"contrast {label} {r} < {need}")
R["tokens"] = tok

check(not R["console_errors"] and not R["page_errors"], "console or page errors")
check(not R["network"], "network requests")
R["summary"] = {"asserts": {"passed": R["passes"], "failed": len(R["fails"])},
                "console_errors": len(R["console_errors"]), "page_errors": len(R["page_errors"]), "network": len(R["network"])}
(HERE / "results.json").write_text(json.dumps(R, indent=1), encoding="utf-8")

print("goldens:", present)
print("console", len(R["console_errors"]), R["console_errors"][:4], "page", len(R["page_errors"]), R["page_errors"][:4], "network", len(R["network"]), R["network"][:4])
for f, s in R["static"].items():
    if isinstance(s, dict) and not (s["first style is system.css"] and s["symbol lines as g2"] and s["gradient defs as g2"]):
        print("STATIC", f, s)
for f, P in R["pages"].items():
    for w, out in P.items():
        v = out.get("vs_g2")
        if v:
            print(f"{f} {w}: diff {v['diff']['diffPixels']}px {v['diff']['ratio']}% boxes {v['diff']['boxes'][:4]} | moved {list(v['rects_moved'].items())[:4]} | text+ {v['text_only_golden'][:4]} text- {v['text_only_g2'][:4]} order {v['text_same_order']} inputs {v['inputs_same']} | ax+ {v['ax_only_golden'][:4]} ax- {v['ax_only_g2'][:4]}")
        lp = out.get("link_points") or {}
        if f in ("bill-items.html", "bill-unassigned.html", "splits-sheet.html", "spare-sen.html", "new-bill-dialog.html"):
            print(f"  link points {w}: {lp}")
        if out.get("vs_g2_s6_unruled"):
            u = out["vs_g2_s6_unruled"]
            print(f"  vs g2 S6 without the ruling {w}: {u['diffPixels']}px boxes {u['boxes'][:4]}")
        if out.get("specimen_vs_g2"):
            print(f"  specimen vs g2 {w}: " + ", ".join(f"{k} {'same' if v['same'] else 'DIFF'}" for k, v in out["specimen_vs_g2"].items()))
        if out.get("strip"):
            print(f"  strip {w}: first {out['strip']['first_screen']} end {out['strip']['page_end']['hits']} tabbed {out['strip']['tabbed']} bad {out['strip']['covered_while_focused'][:2]}")
for k, v in R["contrast"].items():
    if not v["pass"]:
        print("CONTRAST FAIL", k, v)
for l in R.get("links", []):
    if not isinstance(l["found"], int) or l["found"] != 1:
        print("link", l["from"], l["width"], l["trigger"], "->", l["found"])
print("links checked:", len(R.get("links", [])))
print("ASSERTS", R["summary"]["asserts"])
for x in R["fails"][:60]:
    print("  FAIL", x)
