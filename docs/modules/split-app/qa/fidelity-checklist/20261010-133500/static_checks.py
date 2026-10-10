"""Static and layout checks around the checklist rows.

 A. CSS: each golden's inline stylesheet against docs/design/system.css, and src/system.css against system.css plus the one allowed rule.
 B. Document: title, lang, doctype mode, viewport meta, html and body computed style (every property), the :root custom properties,
    golden against app, for the five screens at 390 and 1280.
 C. Icons: every svg.ph of each screen, golden against app (count, attributes, path data), and the four distinct paths against states.html.
 D. Layouts at 360, 390, 599, 600, 1023, 1024 and 1280: horizontal overflow, people grid columns, panel arrangement, widths, the dialog,
    app measured and golden measured side by side (an element that is not rendered, such as the hidden block of the other mode, reads null).

usage: python static_checks.py
"""
import sys

sys.dont_write_bytecode = True
import re

from playwright.sync_api import sync_playwright

import common as C

EXPECTED_TAIL = "\n[hidden] { display: none !important; }\n"
WIDTHS = [(360, 780), (390, 844), (599, 900), (600, 900), (1023, 768), (1024, 768), (1280, 800)]


def css_checks():
    sys_css = (C.DESIGN / "system.css").read_text(encoding="utf-8")
    src_css = (C.ROOT / "src" / "system.css").read_text(encoding="utf-8")
    out = {"src_equals_system_plus_hidden_rule": src_css == sys_css + EXPECTED_TAIL,
           "src_bytes": len((C.ROOT / "src" / "system.css").read_bytes()), "system_bytes": len((C.DESIGN / "system.css").read_bytes()), "goldens": {}}
    for name in ("bill-empty", "bill-even", "bill-items", "bill-unassigned", "new-bill-dialog", "states"):
        html = (C.DESIGN / f"{name}.html").read_text(encoding="utf-8")
        blocks = re.findall(r"<style>(.*?)</style>", html, re.S)
        first = blocks[0]
        out["goldens"][name] = {"style_blocks": len(blocks), "first_block_equals_system_css": first.strip() == sys_css.strip(),
                               "first_block_equals_system_css_exactly": first == sys_css or first == "\n" + sys_css}
    index = (C.ROOT / "index.html").read_text(encoding="utf-8")
    out["index_has_inline_style_or_script"] = bool(re.search(r"<style|<script(?![^>]*src=)| style=", index))
    return out


INFO_JS = """() => ({ title: document.title, lang: document.documentElement.lang, mode: document.compatMode,
  viewport: (document.querySelector('meta[name=viewport]') || {}).content, charset: document.characterSet, doctype: document.doctype ? document.doctype.name : null })"""


def doc_checks(browser, base):
    rows = []
    for screen, (golden, seed) in C.SCREENS.items():
        for vp in ((390, 844), (1280, 800)):
            gctx, actx = C.gold_ctx(browser, vp), C.app_ctx(browser, base, vp, seed=seed)
            g, a = C.open_golden(gctx, golden), C.open_app(actx, base)
            if screen == "new-bill-dialog":
                C.new_bill_by_mouse(a)
            ig, ia = g.js(INFO_JS), a.js(INFO_JS)
            res = {"screen": screen, "viewport": f"{vp[0]}x{vp[1]}", "document_golden": ig, "document_app": ia, "document_equal": ig == ia}
            for sel in ("html", "body"):
                eg, ea = g.one(sel), a.one(sel)
                res[f"{sel}_style_diffs"] = C.style_diff(eg["cs"], ea["cs"], ("interactivity",) if screen == "new-bill-dialog" else ())
                res[f"{sel}_properties_compared"] = len(eg["cs"])
            custom_g = {k: v for k, v in g.one("html")["cs"].items() if k.startswith("--")}
            custom_a = {k: v for k, v in a.one("html")["cs"].items() if k.startswith("--")}
            res["root_custom_properties"] = len(custom_g)
            res["root_custom_properties_equal"] = custom_g == custom_a
            rows.append(res)
            gctx.close()
            actx.close()
    return rows


ICON_JS = """() => Array.from(document.querySelectorAll('svg.ph')).filter((s) => s.getClientRects().length > 0).map((s) => ({
  place: (s.closest('button, th') ? (s.closest('button, th').getAttribute('aria-label') || s.closest('button, th').textContent.trim()) : '?'),
  attrs: Object.fromEntries(Array.from(s.attributes).map((a) => [a.name, a.value])),
  paths: Array.from(s.querySelectorAll('path')).map((p) => p.getAttribute('d')), w: s.getBoundingClientRect().width, h: s.getBoundingClientRect().height,
  fill: getComputedStyle(s).fill }))"""
DISTINCT_JS = "() => Array.from(new Set(Array.from(document.querySelectorAll('svg.ph path')).filter((p) => p.closest('svg').getClientRects().length > 0).map((p) => p.getAttribute('d'))))"


def icon_checks(browser, base):
    sctx = C.gold_ctx(browser, (390, 844))
    spec = C.open_golden(sctx, "states")
    sp = spec.js(DISTINCT_JS)
    gctx = C.gold_ctx(browser, (390, 844))
    gi = C.open_golden(gctx, "bill-items")
    gp = gi.js(DISTINCT_JS)
    rows = []
    for screen, (golden, seed) in C.SCREENS.items():
        for vp in ((390, 844), (1280, 800)):
            gctx2, actx = C.gold_ctx(browser, vp), C.app_ctx(browser, base, vp, seed=seed)
            g, a = C.open_golden(gctx2, golden), C.open_app(actx, base)
            if screen == "new-bill-dialog":
                C.new_bill_by_mouse(a)
            ig, ia = g.js(ICON_JS), a.js(ICON_JS)
            distinct_app = a.js(DISTINCT_JS)
            rows.append({"screen": screen, "viewport": f"{vp[0]}x{vp[1]}", "icons_golden": len(ig), "icons_app": len(ia), "equal": ig == ia,
                         "distinct_paths_app": len(distinct_app), "all_paths_in_golden_sets": all(d in set(gp) | set(sp) for d in distinct_app)})
            gctx2.close()
            actx.close()
    sctx.close()
    gctx.close()
    return {"specimen_distinct_paths": len(sp), "bill_items_distinct_paths": len(gp), "rows": rows}


LAYOUT_JS = """() => {
  const vis = (s) => { const e = Array.from(document.querySelectorAll(s)).find((x) => x.getClientRects().length > 0); return e || null; };
  const r = (s) => { const e = vis(s); if (!e) return null; const b = e.getBoundingClientRect(); return [Math.round(b.x * 100) / 100, Math.round(b.y * 100) / 100, Math.round(b.width * 100) / 100, Math.round(b.height * 100) / 100]; };
  const t = vis('div.tape');
  const d = document.querySelector('dialog.dialog');
  const peopleGrid = vis('section[aria-labelledby=h-people] ul.cells');
  return { scrollWidth: document.documentElement.scrollWidth, innerWidth: innerWidth, scrollHeight: document.documentElement.scrollHeight,
    header: r('header.bar'), layout: r('main.layout'), inputs: r('.inputs'), peopleGrid: r('section[aria-labelledby=h-people] ul.cells'),
    peopleCols: peopleGrid ? getComputedStyle(peopleGrid).gridTemplateColumns.split(' ').length : null,
    chargesBottom: (() => { const e = vis('section[aria-labelledby=h-charges]'); return e ? e.getBoundingClientRect().bottom + scrollY : null; })(),
    tape: r('div.tape'), tapePos: t ? getComputedStyle(t).position : null, tapeBorderTop: t ? getComputedStyle(t).borderTopWidth : null,
    priceField: r('.item-line .field.money'), subtotalField: r('section[aria-labelledby=h-subtotal] .field.money'),
    dialog: d && d.open ? r('dialog.dialog') : null, actionsDir: d && d.open ? getComputedStyle(d.querySelector('.dialog-actions')).flexDirection : null,
    dialogTextH: d && d.open ? r('p.dialog-text')[3] : null };
}"""


def layout_checks(browser, base):
    rows = []
    for screen, (golden, seed) in C.SCREENS.items():
        for vp in WIDTHS:
            gctx, actx = C.gold_ctx(browser, vp), C.app_ctx(browser, base, vp, seed=seed)
            g, a = C.open_golden(gctx, golden), C.open_app(actx, base)
            if screen == "new-bill-dialog":
                C.new_bill_by_mouse(a)
            lg, la = g.js(LAYOUT_JS), a.js(LAYOUT_JS)
            rows.append({"screen": screen, "viewport": f"{vp[0]}x{vp[1]}", "app": la, "golden": lg, "equal": la == lg,
                         "overflow": la["scrollWidth"] > la["innerWidth"]})
            gctx.close()
            actx.close()
    return rows


def main():
    out = {"css": css_checks()}
    server = C.rig.StaticServer(C.ROOT, say=print)
    try:
        server.start()
        with sync_playwright() as pw:
            browser = C.launch(pw)
            out["document"] = doc_checks(browser, server.base)
            out["icons"] = icon_checks(browser, server.base)
            out["layouts"] = layout_checks(browser, server.base)
            browser.close()
    finally:
        server.stop()
    C.dump("static_checks.json", out)
    css = out["css"]
    print("src/system.css == system.css + one rule:", css["src_equals_system_plus_hidden_rule"], css["src_bytes"], css["system_bytes"])
    for k, v in css["goldens"].items():
        print("golden", k, v)
    print("index.html inline style/script:", css["index_has_inline_style_or_script"])
    bad = [r for r in out["document"] if not (r["document_equal"] and not r["html_style_diffs"] and not r["body_style_diffs"] and r["root_custom_properties_equal"])]
    print("document checks:", len(out["document"]), "rows, failing", len(bad))
    for r in bad:
        print("  FAIL", r["screen"], r["viewport"], r["document_golden"], r["document_app"], list(r["html_style_diffs"])[:4], list(r["body_style_diffs"])[:4])
    ib = [r for r in out["icons"]["rows"] if not (r["equal"] and r["all_paths_in_golden_sets"])]
    print("icon checks:", len(out["icons"]["rows"]), "rows, failing", len(ib), out["icons"]["specimen_distinct_paths"], out["icons"]["bill_items_distinct_paths"])
    lb = [r for r in out["layouts"] if not r["equal"] or r["overflow"]]
    print("layout rows:", len(out["layouts"]), "not equal to golden or overflowing:", len(lb))
    for r in lb:
        print("  ", r["screen"], r["viewport"], "equal", r["equal"], "overflow", r["overflow"])
        if not r["equal"]:
            for k in r["app"]:
                if r["app"][k] != r["golden"][k]:
                    print("     ", k, "app", r["app"][k], "golden", r["golden"][k])


if __name__ == "__main__":
    main()
