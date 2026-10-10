"""Render checks for round-1 direction D (Share Orbit).

Run: python -B check_d.py
Opens d.html by file URL in headless Chromium, takes screenshots, and records console errors, sideways scroll,
ring arc lengths against the shares, figures, contrast ratios and icon path fidelity. Writes results.json here.
"""
import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROUND = HERE.parent.parent
PAGE = ROUND / "d.html"
URL = PAGE.as_uri()
SHOTS = HERE
WAIT_MS = 4000

results = {"console_errors": [], "page_errors": [], "network": [], "scroll": {}, "overflow": {}, "arcs": {},
           "figures": {}, "contrast": {}, "icons": {}, "dashes": None, "shots": []}


# ---------- contrast ----------
def lum(hex_colour):
    h = hex_colour.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


# ---------- static file checks ----------
src = PAGE.read_text(encoding="utf-8")
results["dashes"] = {"em": src.count("—"), "en": src.count("–"), "middle_dot": src.count("·")}

icons_js = (ROUND.parent.parent.parent.parent / "src" / "ui" / "icons.js").read_text(encoding="utf-8")
a_html = (ROUND / "a.html").read_text(encoding="utf-8")
ref = {}
for name, d in re.findall(r'(\w+): "(M[^"]+)"', icons_js):
    ref[name] = d
for sym, d in re.findall(r'<symbol id="i-([\w-]+)" viewBox="0 0 256 256"><path d="([^"]+)"', a_html):
    ref.setdefault(sym, d)
for sym, d in re.findall(r'<symbol id="i-([\w-]+)" viewBox="0 0 256 256"><path d="([^"]+)"', src):
    results["icons"][sym] = "match" if ref.get(sym) == d else "MISMATCH"


def ring_arcs(page):
    return page.evaluate("""() => {
      const segs = [...document.querySelectorAll('#ring .seg')];
      const lens = segs.map(p => p.getTotalLength());
      const sum = lens.reduce((a, b) => a + b, 0);
      return segs.map((p, i) => ({
        id: p.dataset.id, share: +p.dataset.share, total: +p.dataset.total,
        len: +lens[i].toFixed(3), lenFrac: +(lens[i] / sum).toFixed(5),
        shareFrac: +(+p.dataset.share / +p.dataset.total).toFixed(5)
      }));
    }""")


def overflow(page):
    return page.evaluate("""() => {
      const vw = document.documentElement.clientWidth;
      const bad = [];
      for (const el of document.querySelectorAll('body *')) {
        if (el.closest('.sprite, .sr-only, dialog:not([open]), [hidden], title')) continue;
        const r = el.getBoundingClientRect();
        if (!r.width && !r.height) continue;
        if (r.right > vw + 0.5 || r.left < -0.5) bad.push((el.id ? '#' + el.id : el.tagName.toLowerCase() + '.' + (el.getAttribute('class') || '')) + ' ' + Math.round(r.left) + '..' + Math.round(r.right));
      }
      return { scrollWidth: document.documentElement.scrollWidth, clientWidth: vw, bad: bad.slice(0, 12) };
    }""")


def collisions(page):
    """Text boxes inside a share row that overlap each other, and centre text wider than the ring hole."""
    return page.evaluate("""() => {
      const out = [];
      const hit = (a, b) => a.left < b.right - 0.5 && b.left < a.right - 0.5 && a.top < b.bottom - 0.5 && b.top < a.bottom - 0.5;
      for (const row of document.querySelectorAll('.res .row')) {
        const parts = [...row.querySelectorAll('.nm, .it, .ch, .sh')].filter(e => e.getBoundingClientRect().width);
        for (let i = 0; i < parts.length; i++) for (let j = i + 1; j < parts.length; j++) {
          if (parts[i].contains(parts[j]) || parts[j].contains(parts[i])) continue;
          if (hit(parts[i].getBoundingClientRect(), parts[j].getBoundingClientRect())) out.push(row.innerText.split('\\n')[0] + ': ' + parts[i].className + ' x ' + parts[j].className);
        }
        for (const p of parts) if (p.scrollWidth > p.clientWidth + 1 && p.className !== 'nm') out.push('clipped ' + p.className + ' ' + p.innerText);
      }
      const fig = document.querySelector('#centre .c-fig');
      if (fig) {
        const segs = document.querySelector('#ring .seg');
        const sw = segs ? +segs.getAttribute('stroke-width') : 0;
        const ring = document.querySelector('#ring').getBoundingClientRect();
        const w = fig.getBoundingClientRect().width;
        const centreBox = document.querySelector('#centre').getBoundingClientRect().width;
        if (w > centreBox + 0.5) out.push('centre figure ' + Math.round(w) + ' wider than hole box ' + Math.round(centreBox));
      }
      return out;
    }""")


def idle(page):
    page.wait_for_function("window.__ringIdle === true", timeout=WAIT_MS)
    page.wait_for_timeout(250)


def shot(page, name, full=False):
    path = SHOTS / f"{name}.png"
    page.screenshot(path=str(path), full_page=full)
    results["shots"].append(str(path))


def text(page, sel):
    return page.eval_on_selector(sel, "e => e.innerText")


def state(page, key):
    page.evaluate(f"window.__loadState('{key}')")
    idle(page)


with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    try:
        def new_page(w, h):
            ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
            pg = ctx.new_page()
            pg.set_default_timeout(WAIT_MS)
            pg.on("console", lambda m: results["console_errors"].append(f"{w}: {m.text}") if m.type == "error" else None)
            pg.on("pageerror", lambda e: results["page_errors"].append(f"{w}: {e}"))

            def route(r):
                if r.request.url.startswith("file:") or r.request.url.startswith("data:"):
                    r.continue_()
                else:
                    results["network"].append(r.request.url)
                    r.abort()
            pg.route("**/*", route)
            pg.goto(URL, wait_until="load")
            idle(pg)
            return ctx, pg

        # ---------- 390 x 844 ----------
        ctx, page = new_page(390, 844)
        shot(page, "k1-390")
        shot(page, "k1-390-full", full=True)
        results["arcs"]["K1 top"] = ring_arcs(page)
        results["figures"]["K1 legend"] = text(page, "#result")
        results["figures"]["K1 bill"] = text(page, "#bill")
        results["figures"]["K1 centre"] = text(page, "#centre")
        results["figures"]["K1 spare"] = text(page, "#spare")

        # P1 open, then One person picker, pick Ben
        page.click("#spareBtn")
        page.wait_for_selector("#spareDlg[open]")
        page.wait_for_timeout(300)
        shot(page, "p1-390")
        page.click('#choices [data-v="one"]')
        page.wait_for_timeout(250)
        shot(page, "p1-picker-390")
        page.click('#picker [data-person="b"]')
        idle(page)
        results["arcs"]["K1 one Ben"] = ring_arcs(page)
        results["figures"]["K1 one Ben"] = text(page, "#result")
        shot(page, "k1-one-ben-390")
        # Esc and backdrop close P1
        page.click("#spareBtn")
        page.wait_for_selector("#spareDlg[open]")
        page.keyboard.press("Escape")
        page.wait_for_timeout(200)
        results["figures"]["P1 closes on Esc"] = not page.eval_on_selector("#spareDlg", "d => d.open")
        page.click("#spareBtn")
        page.wait_for_selector("#spareDlg[open]")
        page.mouse.click(195, 40)
        page.wait_for_timeout(200)
        results["figures"]["P1 closes on backdrop"] = not page.eval_on_selector("#spareDlg", "d => d.open")

        # K2 and its spare choices
        state(page, "K2")
        shot(page, "k2-390")
        results["arcs"]["K2 top"] = ring_arcs(page)
        results["figures"]["K2 legend"] = text(page, "#result")
        results["figures"]["K2 spare"] = text(page, "#spare")
        page.click("#spareBtn")
        page.click('#choices [data-v="one"]')
        page.click('#picker [data-person="b"]')
        idle(page)
        results["figures"]["K2 one Ben"] = text(page, "#result")
        results["arcs"]["K2 one Ben"] = ring_arcs(page)
        page.click("#spareBtn")
        page.click('#choices [data-v="random"]')
        idle(page)
        draws = []
        for _ in range(12):
            draws.append(page.evaluate("""() => [...document.querySelectorAll('.legend .row')].map(r => r.querySelector('.sh').innerText.replace(/^.*RM/, 'RM') + (r.querySelector('.sen') ? '*' : '')).join(' | ')"""))
            page.click("#pickAgain")
            idle(page)
        results["figures"]["K2 random draws"] = draws
        shot(page, "k2-random-390")

        # M1 open, Esc, backdrop, confirm
        state(page, "K1")
        page.click("#newBill")
        page.wait_for_selector("#newDlg[open]")
        page.wait_for_timeout(300)
        shot(page, "m1-390")
        page.keyboard.press("Escape")
        page.wait_for_timeout(200)
        results["figures"]["M1 closes on Esc"] = not page.eval_on_selector("#newDlg", "d => d.open")
        page.click("#newBill")
        page.wait_for_selector("#newDlg[open]")
        page.mouse.click(10, 10)
        page.wait_for_timeout(200)
        results["figures"]["M1 closes on backdrop"] = not page.eval_on_selector("#newDlg", "d => d.open")
        page.click("#newBill")
        page.click("#confirmNew")
        idle(page)
        results["figures"]["M1 confirm gives S1"] = text(page, "#centre")

        # Copy summary status by the design's own button
        state(page, "K1")
        page.click("#copyBtn")
        results["figures"]["S4 copied"] = text(page, "#status")

        # States without a natural trigger
        for key in ["S1", "S2", "S3", "S4b", "S5", "S6", "S7", "W1"]:
            state(page, key)
            shot(page, f"{key.lower()}-390", full=True)
        state(page, "S2")
        results["figures"]["S2"] = text(page, "#billInputs")
        state(page, "S3")
        results["figures"]["S3"] = text(page, "#result")
        state(page, "S4b")
        results["figures"]["S4 blocked"] = text(page, "#status")
        state(page, "S5")
        results["figures"]["S5"] = text(page, "#notes")
        state(page, "S6")
        results["figures"]["S6"] = text(page, "#notes") + " / " + text(page, "#centre")
        state(page, "S7")
        results["figures"]["S7 add disabled"] = page.eval_on_selector("#addPerson", "b => b.disabled")
        results["arcs"]["S7"] = ring_arcs(page)

        # Prototype states panel open (sits under popups, check it does not cover content when closed)
        state(page, "K1")
        page.click("#protoTab")
        page.wait_for_timeout(150)
        shot(page, "proto-panel-390")
        results["figures"]["proto tab box"] = page.eval_on_selector("#protoTab", "e => { const r = e.getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }")
        page.click("#protoClose")
        ctx.close()

        # ---------- 360 x 780 ----------
        ctx, page = new_page(360, 780)
        shot(page, "k1-360")
        results["overflow"]["K1 360"] = overflow(page)
        results["collisions"] = {"K1 360": collisions(page)}
        for key in ["K2", "S1", "S2", "S3", "S4b", "S5", "S6", "S7", "W1"]:
            state(page, key)
            results["overflow"][f"{key} 360"] = overflow(page)
            results["collisions"][f"{key} 360"] = collisions(page)
        state(page, "W1")
        shot(page, "w1-360")
        shot(page, "w1-360-full", full=True)
        results["figures"]["W1 centre"] = text(page, "#centre")
        results["figures"]["W1 legend"] = text(page, "#result")
        results["figures"]["W1 bill"] = text(page, "#bill")
        results["arcs"]["W1"] = ring_arcs(page)
        state(page, "K1")
        page.click("#spareBtn")
        page.wait_for_selector("#spareDlg[open]")
        page.wait_for_timeout(300)
        results["overflow"]["P1 360"] = overflow(page)
        shot(page, "p1-360")
        page.keyboard.press("Escape")
        page.click("#newBill")
        page.wait_for_selector("#newDlg[open]")
        page.wait_for_timeout(300)
        results["overflow"]["M1 360"] = overflow(page)
        shot(page, "m1-360")
        page.keyboard.press("Escape")
        ctx.close()

        # ---------- 1280 x 800 ----------
        ctx, page = new_page(1280, 800)
        shot(page, "k1-1280")
        shot(page, "k1-1280-full", full=True)
        results["collisions"]["K1 1280"] = collisions(page)
        results["figures"]["1280 orbit bottom"] = page.eval_on_selector("#orbit", "e => Math.round(e.getBoundingClientRect().bottom)")
        results["arcs"]["K1 1280"] = ring_arcs(page)
        page.click("#spareBtn")
        page.wait_for_selector("#spareDlg[open]")
        page.click('#choices [data-v="one"]')
        page.wait_for_timeout(300)
        shot(page, "p1-picker-1280")
        page.keyboard.press("Escape")
        page.click("#newBill")
        page.wait_for_selector("#newDlg[open]")
        page.wait_for_timeout(300)
        shot(page, "m1-1280")
        page.keyboard.press("Escape")
        state(page, "K2")
        shot(page, "k2-1280")
        state(page, "S3")
        shot(page, "s3-1280")
        state(page, "S7")
        shot(page, "s7-1280")
        state(page, "S5")
        shot(page, "s5-1280")
        # hover a share row: its segment and leader stay lit, the rest dim
        state(page, "K1")
        page.hover('.legend .row[data-id="b"]')
        page.wait_for_timeout(250)
        shot(page, "hover-ben-1280")
        results["figures"]["hover lit"] = page.evaluate("[...document.querySelectorAll('#ring .on')].map(e => e.tagName + ':' + e.dataset.id)")
        page.mouse.move(5, 5)
        # focus ring visibility on the Copy summary button
        state(page, "K1")
        results["figures"]["ring dim flag after re-render"] = page.evaluate("document.querySelector('#ring').hasAttribute('data-focus')")
        page.focus("#spareBtn")
        page.keyboard.press("Tab")
        page.wait_for_timeout(100)
        shot(page, "focus-copy-1280")
        results["figures"]["focused"] = page.evaluate("document.activeElement.id")
        # tokens for contrast
        tokens = page.evaluate("""() => {
          const cs = getComputedStyle(document.documentElement);
          const out = {};
          for (const n of ['bg','surface','raised','hover','line','line-strong','ink','ink-muted','ink-faint','coral','coral-hover','on-coral','amber','on-person','p1','p2','p3','p4','p5','p6','p7','p8','p9','p10','p11','p12']) out[n] = cs.getPropertyValue('--' + n).trim();
          return out;
        }""")
        ctx.close()

        # ---------- reduced motion ----------
        ctx = browser.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
        page = ctx.new_page()
        page.set_default_timeout(WAIT_MS)
        page.on("console", lambda m: results["console_errors"].append(f"rm: {m.text}") if m.type == "error" else None)
        page.on("pageerror", lambda e: results["page_errors"].append(f"rm: {e}"))
        page.goto(URL, wait_until="load")
        results["figures"]["reduced motion idle at load"] = page.evaluate("window.__ringIdle === true")
        ctx.close()
    finally:
        browser.close()

t = tokens
pairs = [
    ("ink on bg", "ink", "bg", 4.5), ("ink on surface", "ink", "surface", 4.5), ("ink on raised", "ink", "raised", 4.5),
    ("ink on hover", "ink", "hover", 4.5),
    ("ink-muted on bg", "ink-muted", "bg", 4.5), ("ink-muted on surface", "ink-muted", "surface", 4.5),
    ("ink-muted on raised", "ink-muted", "raised", 4.5),
    ("coral on bg", "coral", "bg", 4.5), ("coral on surface", "coral", "surface", 4.5), ("coral on raised", "coral", "raised", 4.5),
    ("on-coral on coral (Copy summary)", "on-coral", "coral", 4.5), ("on-coral on coral-hover", "on-coral", "coral-hover", 4.5),
    ("amber on bg", "amber", "bg", 4.5), ("amber on surface", "amber", "surface", 4.5), ("amber on raised", "amber", "raised", 3.0),
    ("line-strong on raised (control border)", "line-strong", "raised", 3.0), ("line-strong on bg", "line-strong", "bg", 3.0),
    ("line-strong on surface", "line-strong", "surface", 3.0),
    ("focus ring ink on bg", "ink", "bg", 3.0), ("coral border on raised", "coral", "raised", 3.0),
]
for i in range(1, 13):
    pairs.append((f"p{i} on surface (segment)", f"p{i}", "surface", 3.0))
    pairs.append((f"on-person on p{i} (tag text)", "on-person", f"p{i}", 4.5))
for i in (1, 2, 3):
    pairs.append((f"p{i} on bg (hollow avatar letter)", f"p{i}", "bg", 4.5))
for label, fg, bgk, need in pairs:
    r = ratio(t[fg], t[bgk])
    results["contrast"][label] = {"ratio": r, "need": need, "pass": r >= need}
results["tokens"] = t

(HERE / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

# ---------- summary ----------
print("console errors:", len(results["console_errors"]), results["console_errors"][:5])
print("page errors:", len(results["page_errors"]), results["page_errors"][:5])
print("network requests blocked:", results["network"])
print("dashes:", results["dashes"])
print("icons:", results["icons"])
for k, v in results["overflow"].items():
    print("overflow", k, v["scrollWidth"], v["clientWidth"], v["bad"])
for k, v in results.get("collisions", {}).items():
    print("collisions", k, v)
for k, segs in results["arcs"].items():
    worst = max((abs(s["lenFrac"] - s["shareFrac"]) for s in segs), default=None)
    print("arcs", k, [(s["id"], s["share"], s["lenFrac"], s["shareFrac"]) for s in segs][:4], "worst diff", worst)
for k, v in results["figures"].items():
    print("fig", k, "=>", json.dumps(v)[:400])
for k, v in results["contrast"].items():
    print("contrast", k, v["ratio"], "PASS" if v["pass"] else "FAIL")
print("shots:", len(results["shots"]))
