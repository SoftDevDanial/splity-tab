"""Interaction states: hover, keyboard focus, pressed, disabled, placeholder, motion. The same gesture is made on the golden and on
the running app, and the WHOLE page (every rendered element, every computed property, ::before and ::after) is compared after each one.

Rows IX-01 to IX-20 (the finder's own ids, taken from the component inventory of system.md, because the checklist in qa.md has no
rows for hover, focus or pressed). Goldens are static files, the app is the real page; the gesture is a real Playwright mouse move,
mouse down or Tab key press on both.

usage: python interactions.py
"""
import sys

sys.dont_write_bytecode = True

from playwright.sync_api import sync_playwright

import common as C
from dom_diff import compare
from rows_lib import Ctx, Rows, note

INK, MUTED, DIS = C.rgb("ink"), C.rgb("ink-muted"), C.rgb("ink-disabled")
FIELD, LINE, LINES, HOVER, INKH = C.rgb("field"), C.rgb("line"), C.rgb("line-strong"), C.rgb("hover"), C.rgb("ink-hover")
ON, ACC, ERR = C.rgb("on-ink"), C.rgb("accent"), C.rgb("error")


def walk_equal(g, a):
    r = compare(g.walk(), a.walk())
    n = len(r["structural"]) + len(r["attr_diffs"]) + len(r["text_diffs"]) + len(r["value_diffs"]) + len(r["rect_diffs"]) + len(r["style_diffs"]) + len(r["pseudo_diffs"])
    detail = ""
    if n:
        bits = []
        for d in r["style_diffs"][:3]:
            bits.append(f"{d['el']}: " + ", ".join(f"{k} {v[0]} vs {v[1]}" for k, v in list(d["props"].items())[:3]))
        bits += [f"rect {d['el']} {d['golden']} vs {d['app']}" for d in r["rect_diffs"][:2]]
        bits += [str(s) for s in r["structural"][:2]]
        detail = "; ".join(bits)
    return n == 0, r["paired"], detail


def descr(pg):
    return pg.js("""() => { const e = document.activeElement; if (!e || e === document.body) return 'body';
      return e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + '[' + (e.getAttribute('aria-label') || e.getAttribute('name') || e.textContent.trim().slice(0, 20)) + ']'
        + (e.type === 'radio' ? '(' + (e.checked ? 'checked' : 'unchecked') + ')' : ''); }""")


def hover_rows(browser, base, R, errors, vp):
    """Hover over each hoverable control on S1 and S3, golden and app, compare the whole page."""
    rows = []
    for screen, targets in (
        ("bill-items", [("IX-01", "header .btn", "New bill (outline button)"),
                        ("IX-01", "ul.cells > li:last-child .btn", "Add person (outline button)"),
                        ("IX-01", "section[aria-labelledby=h-items] > .btn", "Add item (outline button)"),
                        ("IX-02", "button.copy", "Copy summary (primary button)"),
                        ("IX-03", "li.field.person:nth-child(1) .icon-btn", "Person remove (icon button)"),
                        ("IX-03", "li.item:nth-child(1) .item-line > .icon-btn", "Item remove (icon button)"),
                        ("IX-04", "li.item:nth-child(1) .who .tap:nth-child(2)", "toggle off (Ben)"),
                        ("IX-04", "li.item:nth-child(1) .who .tap:nth-child(1)", "toggle on (Aisyah)"),
                        ("IX-05", "label[for=mode-even]", "mode label, unchecked (Even)"),
                        ("IX-05", "label[for=mode-item]", "mode label, checked (By item)")]),
        ("bill-empty", [("IX-06", "li.field.person:nth-child(1) .icon-btn", "disabled person remove (no hover)"),
                        ("IX-06", "li.field.person:nth-child(2) .icon-btn", "disabled person remove 2 (no hover)")]),
    ):
        golden, seed = C.SCREENS[screen]
        for rid, sel, label in targets:
            gctx, actx = C.gold_ctx(browser, vp, motion="reduce"), C.app_ctx(browser, base, vp, seed=seed, motion="reduce")
            g, a = C.open_golden(gctx, golden), C.open_app(actx, base)
            g.page.hover(sel)
            a.page.hover(sel)
            g.page.wait_for_timeout(80)
            a.page.wait_for_timeout(80)
            ok, n, detail = walk_equal(g, a)
            el = a.one(sel)
            hov = el["hover"]
            bg, col = el["cs"]["background-color"], el["cs"]["color"]
            lit_ok = hov
            if "disabled" in label:
                lit_ok &= bg == "rgba(0, 0, 0, 0)" and col == DIS
            elif "primary" in label:
                lit_ok &= bg == INKH
            elif "toggle on" in label or "checked (By" in label:
                lit_ok &= bg == INK
            elif "icon button" in label:
                lit_ok &= bg == HOVER and col == INK
            else:
                lit_ok &= bg == HOVER
            R.add(rid, vp[0], ok and lit_ok, f"{screen} hover {label}: matches :hover={hov}, bg {bg}, colour {col}; whole page equal to the golden under the same hover ({n} elements, {'0 differences' if ok else detail})")
            errors += [(rid, vp, m) for m in a.console]
            gctx.close()
            actx.close()


def pressed_rows(browser, base, R, errors, vp):
    for rid, sel, label, disabled_screen in (
        ("IX-07", "header .btn", "New bill", False), ("IX-07", "ul.cells > li:last-child .btn", "Add person", False),
        ("IX-07", "button.copy", "Copy summary", False), ("IX-07", "li.field.person:nth-child(1) .icon-btn", "person remove", False),
        ("IX-07", "li.item:nth-child(1) .who .tap:nth-child(2)", "toggle", False),
    ):
        golden, seed = C.SCREENS["bill-items"]
        gctx, actx = C.gold_ctx(browser, vp, motion="reduce"), C.app_ctx(browser, base, vp, seed=seed, motion="reduce")
        g, a = C.open_golden(gctx, golden), C.open_app(actx, base)
        for pg in (g, a):
            pg.page.hover(sel)
            pg.page.mouse.down()
            pg.page.wait_for_timeout(60)
        ok, n, detail = walk_equal(g, a)
        tf = a.one(sel)["cs"]["transform"]
        R.add(rid, vp[0], ok and tf == "matrix(1, 0, 0, 1, 0, 1)", f"pressed {label}: transform {tf} (1 px down); whole page equal to the golden under the same press ({n} elements, {'0 differences' if ok else detail})")
        for pg in (g, a):
            pg.page.mouse.move(2, 2)
            pg.page.mouse.up()
        stored = a.js("() => localStorage.getItem('split.draft')")
        R.add(rid, vp[0], stored == seed, f"{label}: releasing the press away from the control changed nothing (draft unchanged)")
        errors += [(rid, vp, m) for m in a.console]
        gctx.close()
        actx.close()
    # disabled: no shift, no hover, on the S3 screen
    golden, seed = C.SCREENS["bill-empty"]
    gctx, actx = C.gold_ctx(browser, vp, motion="reduce"), C.app_ctx(browser, base, vp, seed=seed, motion="reduce")
    g, a = C.open_golden(gctx, golden), C.open_app(actx, base)
    for pg in (g, a):
        pg.page.hover("li.field.person:nth-child(1) .icon-btn", force=True)
        pg.page.mouse.down()
    ok, n, detail = walk_equal(g, a)
    tf = a.one("li.field.person:nth-child(1) .icon-btn")["cs"]["transform"]
    R.add("IX-08", vp[0], ok and tf == "none", f"pressed disabled remove: transform {tf} (no shift); whole page equal to the golden ({n} elements, {'0 differences' if ok else detail})")
    for pg in (g, a):
        pg.page.mouse.up()
    gctx.close()
    actx.close()


def focus_rows(browser, base, R, errors, vp):
    """Tab through the whole page on the golden and on the app; after every stop compare the whole page and the focused element."""
    for screen, rid in (("bill-items", "IX-09"), ("bill-even", "IX-10"), ("bill-empty", "IX-11")):
        golden, seed = C.SCREENS[screen]
        gctx, actx = C.gold_ctx(browser, vp, motion="reduce"), C.app_ctx(browser, base, vp, seed=seed, motion="reduce")
        g, a = C.open_golden(gctx, golden), C.open_app(actx, base)
        stops, bad, order_g, order_a, ring_bad = 0, [], [], [], []
        for i in range(60):
            g.page.keyboard.press("Tab")
            a.page.keyboard.press("Tab")
            dg, da = descr(g), descr(a)
            if dg == "body" and da == "body":
                break
            order_g.append(dg)
            order_a.append(da)
            ok, n, detail = walk_equal(g, a)
            stops += 1
            fe = a.js("""() => { const e = document.activeElement; const cs = getComputedStyle(e); const w = e.closest('.field') ? getComputedStyle(e.closest('.field')) : null;
              const m = e.closest('.mode') ? getComputedStyle(e.closest('.mode')) : null;
              return { fv: e.matches(':focus-visible'), own: [cs.outlineStyle, cs.outlineWidth, cs.outlineColor, cs.outlineOffset].join(' '),
                       wrap: w ? [w.outlineStyle, w.outlineWidth, w.outlineColor, w.outlineOffset].join(' ') : null, mode: m ? [m.outlineStyle, m.outlineWidth, m.outlineColor, m.outlineOffset].join(' ') : null,
                       shadow: e.tagName === 'INPUT' && e.type === 'radio' ? getComputedStyle(e.nextElementSibling).boxShadow : null }; }""")
            if not ok:
                bad.append(f"stop {stops} {da}: {detail}")
            tag = da
            if "radio" in tag or "mode-" in tag:
                good_ring = fe["fv"] and fe["mode"] == f"solid 2px {INK} 2px" and fe["shadow"] == f"{FIELD} 0px 0px 0px 3px inset, {INK} 0px 0px 0px 5px inset"
            elif tag.startswith("input"):
                good_ring = fe["fv"] and fe["wrap"] == f"solid 2px {INK} 2px" and fe["own"].startswith("none")
            elif "Remove Person" in tag or ("button[Remove" in tag and "-" in tag):
                good_ring = fe["fv"] and fe["own"] == f"solid 2px {INK} -3px"
            elif "Remove" in tag and "button" in tag and screen == "bill-items" and "Remove Aisyah" not in tag and "Remove Ben" not in tag and "Remove Chen" not in tag:
                good_ring = fe["fv"] and fe["own"] == f"solid 2px {INK} 2px"
            elif "Remove Aisyah" in tag or "Remove Ben" in tag or "Remove Chen" in tag:
                good_ring = fe["fv"] and fe["own"] == f"solid 2px {INK} -3px"
            else:
                good_ring = fe["fv"] and fe["own"] == f"solid 2px {INK} 2px"
            if not good_ring:
                ring_bad.append(f"{da}: {fe}")
        R.add(rid, vp[0], not bad, f"{screen}: {stops} Tab stops, the whole page equal to the golden after every stop ({'0 differences' if not bad else bad[:2]})")
        R.add(rid, vp[0], order_g == order_a, f"{screen}: Tab order equal to the golden's ({stops} stops: {' > '.join(order_a)})")
        R.add(rid, vp[0], not ring_bad, f"{screen}: every stop shows the system ring on the right element (2 px solid ink, 2 px offset; on the field wrapper for inputs; inset -3 px on the person Remove; outer ring plus the 3 px field and 2 px ink double ring on the mode switch)" + ("" if not ring_bad else f" BUT {ring_bad[:2]}"))
        errors += [(rid, vp, m) for m in a.console]
        gctx.close()
        actx.close()


def placeholder_motion_rows(browser, base, R, errors, vp):
    # placeholder: clear a name so the placeholder shows
    golden, seed = C.SCREENS["bill-items"]
    actx = C.app_ctx(browser, base, vp, seed=seed, motion="reduce")
    a = C.open_app(actx, base)
    a.page.click('input[aria-label="Person 2 name"]')
    a.page.keyboard.press("Control+A")
    a.page.keyboard.press("Backspace")
    el = a.one('input[aria-label="Person 2 name"]')
    ph = el["::placeholder"]
    R.add("IX-12", vp[0], ph["color"] == MUTED and ph["opacity"] == "1" and el["attrs"].get("placeholder") == "Person 2" and el["value"] == "",
          f"empty name field: placeholder {el['attrs'].get('placeholder')!r} in {ph['color']} at opacity {ph['opacity']} (ink muted, opacity 1, as system.css)")
    btn = a.js("() => document.querySelector('button[aria-label=\"Remove Person 2\"]') ? 'Remove Person 2 button named' : 'not found'")
    R.add("IX-12", vp[0], btn == "Remove Person 2 button named", f"blank name shows Person 2 elsewhere ({btn})")
    errors += [("IX-12", vp, m) for m in a.console]
    actx.close()
    # motion: no-preference gives the 120 ms colour transition, reduce gives 0s; golden the same
    for motion, want in (("no-preference", "0.12s, 0.12s"), ("reduce", "0s")):
        gctx, actx = C.gold_ctx(browser, vp, motion=motion), C.app_ctx(browser, base, vp, seed=seed, motion=motion)
        g, a = C.open_golden(gctx, golden), C.open_app(actx, base)
        parts = []
        ok = True
        for sel in ("header .btn", "button.copy", "li.field.person:nth-child(1) .icon-btn", "li.item:nth-child(1) .who .tap", "label[for=mode-even]"):
            ea, eg = a.one(sel), g.one(sel)
            td = ea["cs"]["transition-duration"]
            tp = ea["cs"]["transition-property"]
            ok &= td == want and td == eg["cs"]["transition-duration"] and tp == eg["cs"]["transition-property"]
            parts.append(f"{sel.split(' ')[-1]} {td} ({tp})")
        R.add("IX-13", vp[0], ok, f"prefers-reduced-motion {motion}: transition-duration {want} on buttons, toggles, icon buttons and mode labels, equal to the golden: " + "; ".join(parts))
        gctx.close()
        actx.close()
    # colour scheme: one light theme, so a dark preference changes nothing
    gctx, actx = C.gold_ctx(browser, vp, scheme="dark"), C.app_ctx(browser, base, vp, seed=seed, scheme="dark")
    g, a = C.open_golden(gctx, golden), C.open_app(actx, base)
    ok, n, detail = walk_equal(g, a)
    body_bg = a.one("body")["cs"]["background-color"]
    R.add("IX-14", vp[0], ok and body_bg == C.rgb("page"), f"colour scheme dark: body {body_bg} (one light theme, no dark mode), whole page equal to the golden ({n} elements, {'0 differences' if ok else detail})")
    gctx.close()
    actx.close()


def dialog_rows(browser, base, R, errors, vp):
    golden, seed = C.SCREENS["new-bill-dialog"]
    # keyboard open: focus on Cancel shows the ring; mouse open: it does not
    actx = C.app_ctx(browser, base, vp, seed=seed, motion="reduce")
    a = C.open_app(actx, base)
    a.page.focus("header .btn")
    a.page.keyboard.press("Enter")
    a.page.wait_for_timeout(150)
    c = a.one("dialog .dialog-actions .btn:nth-child(2)")
    R.add("IX-15", vp[0], c["focused"] and c["focusVisible"] and c["cs"]["outline-style"] == "solid" and c["cs"]["outline-width"] == "2px" and c["cs"]["outline-color"] == INK and c["cs"]["outline-offset"] == "2px",
          f"keyboard open: Cancel focused={c['focused']}, :focus-visible={c['focusVisible']}, outline {c['cs']['outline-width']} {c['cs']['outline-style']} {c['cs']['outline-color']} offset {c['cs']['outline-offset']}")
    a.page.keyboard.press("Tab")
    s = a.one("dialog .dialog-actions .btn:nth-child(1)")
    R.add("IX-15", vp[0], s["focused"] and s["focusVisible"] and s["cs"]["outline-style"] == "solid" and s["cs"]["outline-offset"] == "2px", f"Tab from Cancel: Start new bill focused={s['focused']}, ring {s['cs']['outline-width']} {s['cs']['outline-style']} offset {s['cs']['outline-offset']}")
    errors += [("IX-15", vp, m) for m in a.console]
    # primary button hover inside the dialog
    a.page.hover("dialog .dialog-actions .btn:nth-child(1)")
    a.page.wait_for_timeout(80)
    s = a.one("dialog .dialog-actions .btn:nth-child(1)")
    R.add("IX-16", vp[0], s["cs"]["background-color"] == INKH and s["cs"]["border-top-color"] == INKH, f"Start new bill hover: fill {s['cs']['background-color']}, border {s['cs']['border-top-color']} (ink hover)")
    a.page.hover("dialog .dialog-actions .btn:nth-child(2)")
    a.page.wait_for_timeout(80)
    c = a.one("dialog .dialog-actions .btn:nth-child(2)")
    R.add("IX-16", vp[0], c["cs"]["background-color"] == HOVER, f"Cancel hover: fill {c['cs']['background-color']} (hover fill)")
    actx.close()
    # the same two hovers on the golden dialog
    gctx = C.gold_ctx(browser, vp, motion="reduce")
    g = C.open_golden(gctx, golden)
    g.page.hover("dialog .dialog-actions .btn:nth-child(1)")
    g.page.wait_for_timeout(80)
    gs = g.one("dialog .dialog-actions .btn:nth-child(1)")
    g.page.hover("dialog .dialog-actions .btn:nth-child(2)")
    g.page.wait_for_timeout(80)
    gc = g.one("dialog .dialog-actions .btn:nth-child(2)")
    R.add("IX-16", vp[0], gs["cs"]["background-color"] == INKH and gc["cs"]["background-color"] == HOVER, f"golden dialog buttons give the same hover fills ({gs['cs']['background-color']}, {gc['cs']['background-color']})")
    gctx.close()


def main():
    R = Rows()
    errors = []
    server = C.rig.StaticServer(C.ROOT, say=print)
    try:
        server.start()
        with sync_playwright() as pw:
            browser = C.launch(pw)
            for vp in ((390, 844), (1280, 800)):
                hover_rows(browser, server.base, R, errors, vp)
                pressed_rows(browser, server.base, R, errors, vp)
                focus_rows(browser, server.base, R, errors, vp)
                placeholder_motion_rows(browser, server.base, R, errors, vp)
                dialog_rows(browser, server.base, R, errors, vp)
            browser.close()
    finally:
        server.stop()
    out = {"rows": {rid: {str(vw): [[ok, t] for ok, t in v] for vw, v in sorted(by.items())} for rid, by in sorted(R.d.items())}, "console_errors": errors}
    C.dump("interactions.json", out)
    fails = sorted(rid for rid, by in R.d.items() if any(not ok for v in by.values() for ok, _ in v))
    print(f"rows {sorted(R.d)}")
    print(f"failing rows {len(fails)}: {fails}")
    print("console errors:", errors)
    for rid, by in sorted(R.d.items()):
        for vw, v in by.items():
            for ok, t in v:
                if not ok:
                    print("FAIL", rid, vw, t[:500])


if __name__ == "__main__":
    main()
