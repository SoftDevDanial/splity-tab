"""Measure g2.html (read only) where its look is set by script, so the static goldens can reproduce it.

Run: python -B g2_measure.py
Opens round-2/g2.html by its file:/// URL in headless Chromium and records, per state and width, the strip's height,
the item frame's overflow and fades, the section summaries, the Splits sheet's scroll, and where P1 sits.
navigator.clipboard is replaced before load and Copy summary is never pressed. Every request that is not file: or
data: is aborted. Writes g2-measure.json beside this script. Every wait is bounded, the browser closes in finally.
"""
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
G2 = HERE.parent.parent / "round-2" / "g2.html"
OUT = HERE / "g2-measure.json"
WAIT_MS = 4000

CLIP_STUB = """
(() => {
  const stub = { __stub: true, writeText() { return Promise.resolve(); }, write() { return Promise.resolve(); },
                 readText() { return Promise.resolve(''); }, read() { return Promise.resolve([]); } };
  Object.defineProperty(Navigator.prototype, 'clipboard', { get() { return stub; }, configurable: true });
  const ex = Document.prototype.execCommand;
  Document.prototype.execCommand = function (cmd, ...rest) { if (/^(copy|cut)$/i.test(String(cmd))) return false; return ex.call(this, cmd, ...rest); };
})();
"""

JS_M = """() => {
  const q = (s) => document.querySelector(s);
  const rect = (e) => { if (!e || !e.getClientRects().length) return null; const r = e.getBoundingClientRect();
    return [Math.round(r.left * 10) / 10, Math.round(r.top * 10) / 10, Math.round(r.width * 10) / 10, Math.round(r.height * 10) / 10]; };
  const strip = q('#strip'), list = q('#itemList'), fw = q('#frameWrap'), box = q('#sheetScroll'), pop = q('#spareDlg');
  const txt = (s) => { const e = q(s); return e ? e.textContent.replace(/\\s+/g, ' ').trim() : null; };
  return {
    stripH: strip.offsetHeight, stripRect: rect(strip), stripVar: getComputedStyle(document.documentElement).getPropertyValue('--strip-h'),
    docH: document.documentElement.scrollHeight, viewport: [innerWidth, innerHeight],
    frame: list ? { scrollH: list.scrollHeight, clientH: list.clientHeight, up: fw.hasAttribute('data-up'), down: fw.hasAttribute('data-down'), rect: rect(fw) } : null,
    peopleSum: txt('#peopleSum .sec-txt'), chargesSum: txt('#chargesSum .sec-txt'),
    peopleOpen: q('#peopleBlk').dataset.open, chargesOpen: q('#chargesBlk').dataset.open,
    sheetOpen: q('#splitsDlg').open, sheet: q('#splitsDlg').open ? { scrollTop: box.scrollTop, scrollH: box.scrollHeight, clientH: box.clientHeight,
      padB: box.style.paddingBottom, sheetRect: rect(q('#splitsDlg .sheet')), boxRect: rect(box), head: rect(q('#rbody .r-head')), splits: rect(q('#splits')) } : null,
    popOpen: pop.open, pop: pop.open ? { rect: rect(pop), offH: pop.offsetHeight, left: pop.style.left, top: pop.style.top } : null,
    chip: rect(q('#spareBtn')), card: rect(q('#card')), splitsRect: rect(q('#splits')),
    stripText: txt('#stripInfo'), stripStatus: txt('#stripStatus'), cardStatus: txt('#cardStatus'),
    notes: txt('#notes'), splitsRows: [...document.querySelectorAll('#rbody .r-splits li')].map(li => li.textContent.replace(/\\s+/g, ' ').trim()),
  };
}"""

R = {}

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, ignore_default_args=["--hide-scrollbars"])
    try:
        for (w, h, phone) in ((390, 844, True), (360, 780, False), (1280, 800, False)):
            ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, is_mobile=phone,
                                      has_touch=phone, reduced_motion="reduce")
            ctx.add_init_script(CLIP_STUB)
            page = ctx.new_page()
            page.set_default_timeout(WAIT_MS)
            page.route("**/*", lambda r: r.continue_() if r.request.url.startswith(("file:", "data:")) else r.abort())
            page.goto(G2.as_uri(), wait_until="load")
            page.wait_for_timeout(300)
            desk = w >= 1024

            def run(key):
                page.mouse.move(2, 2)
                page.evaluate(f"() => {{ if (document.activeElement) document.activeElement.blur(); window.__g.run('{key}'); }}")
                page.wait_for_timeout(250)

            def rec(name):
                R[f"{name} {w}"] = page.evaluate(JS_M)

            for key in ("k1", "k1open", "k2", "p1", "p2", "m1", "s1", "s2", "s2rate", "s3", "s4ok", "s4fail", "s5", "s6", "s7", "w1"):
                run(key)
                rec(key)
            # S6 with People open (ruling 1)
            run("s6")
            if not desk:
                page.click("#peopleBtn")
                page.wait_for_timeout(300)
            rec("s6open")
            # P1 on K2, One person, Ben
            run("k2")
            if not desk:
                page.click("#splitsBtn")
                page.wait_for_timeout(300)
            page.click("#spareBtn")
            page.wait_for_selector("#spareDlg[open]")
            page.wait_for_timeout(250)
            page.click('label.choice:has(input[value="one"])')
            page.wait_for_timeout(200)
            page.click('#pickList label:has(input[value="2"]) .pill-face')
            page.wait_for_timeout(250)
            page.mouse.move(2, 2)
            page.evaluate("document.activeElement && document.activeElement.blur()")
            rec("p1one")
            # P1 on K2, At random with Ben and Chen drawn (a fixed draw set on the live state)
            run("k2")
            page.evaluate("""() => { const S = window.__g.state(); S.spare = { rule: 'random', pid: null, perm: [2, 3, 1] };
              const i = document.querySelector('#svc'); i.dispatchEvent(new Event('input', { bubbles: true })); }""")
            page.wait_for_timeout(150)
            if not desk:
                page.click("#splitsBtn")
                page.wait_for_timeout(300)
            page.click("#spareBtn")
            page.wait_for_selector("#spareDlg[open]")
            page.wait_for_timeout(250)
            page.mouse.move(2, 2)
            page.evaluate("document.activeElement && document.activeElement.blur()")
            rec("p1rand")
            ctx.close()
    finally:
        browser.close()

OUT.write_text(json.dumps(R, indent=1), encoding="utf-8")
for k, v in R.items():
    print(k, "| stripH", v["stripH"], "| docH", v["docH"], "| frame", v["frame"] and (v["frame"]["scrollH"], v["frame"]["clientH"], v["frame"]["up"], v["frame"]["down"]),
          "| sums", v["peopleSum"], "/", v["chargesSum"], "| sheet", v["sheet"] and (v["sheet"]["scrollTop"], v["sheet"]["scrollH"], v["sheet"]["clientH"], v["sheet"]["padB"]),
          "| pop", v["pop"], "| chip", v["chip"], "| card", v["card"])
