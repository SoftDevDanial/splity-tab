"""FE element checklist rows ST-01 to ST-15: the states of states.html, reached on the running app with real gestures
(clicks, typing, Tab, Remove) and compared with the specimen sheet's own elements.

"Equal to the specimen" here is stricter than qa.md asks: every computed style property Chromium lists, the shorthands in
common.SHORTHANDS, and ::before/::after, minus
  - the ones that follow only from box size (width, height, inline-size, block-size, perspective-origin, transform-origin, the grid tracks),
  - custom properties (--gutter and --price-width are set by the specimen frame on purpose, and change nothing a rule does not already show),
  - list-style and list-style-type (inherited from whichever ul.cells the element happens to sit in, and drawn only on a list item).
qa.md's own list (colour, background, font size and weight, borders, box-shadow, paddings, radii, cursor, text-align, margin-top)
is a subset of what is compared.

usage: python rows_states.py
"""
import sys

sys.dont_write_bytecode = True
import math

from playwright.sync_api import sync_playwright

import common as C
from rows_lib import Ctx, Rows, note

INK, MUTED, DIS = C.rgb("ink"), C.rgb("ink-muted"), C.rgb("ink-disabled")
FIELD, LINE, LINES = C.rgb("field"), C.rgb("line"), C.rgb("line-strong")
ON, ACC, ERR = C.rgb("on-ink"), C.rgb("accent"), C.rgb("error")
SPEC = "section[aria-labelledby={}]"


class Ign:
    NAMES = {"width", "height", "inline-size", "block-size", "perspective-origin", "transform-origin", "grid-template-columns", "grid-template-rows",
             "min-width", "max-width", "min-inline-size", "max-inline-size", "list-style", "list-style-type"}

    def __init__(self, extra=()):
        self.extra = set(extra)

    def __contains__(self, key):
        return key.startswith("--") or key in self.NAMES or key in self.extra


def one_of(pg, expr_js):
    """A one() record of the element an in-page expression returns (a list holding one element)."""
    return pg.page.evaluate(C.ONE_JS.replace("Array.from(document.querySelectorAll(sel))", "Array.from(" + expr_js + ")"), ["x", 0, list(C.SHORTHANDS)])


def field_of(pg, input_sel):
    return one_of(pg, "[document.querySelector(" + repr(input_sel) + ").closest('.field')]")


def spec_eq(rid, ctx, app_el, spec_el, label, extra_ignore=()):
    """Compare an app element record with a specimen element record; add the result to the row."""
    if app_el is None or spec_el is None:
        ctx.R.add(rid, ctx.vw, False, f"{label}: element missing (app {app_el is not None}, specimen {spec_el is not None})")
        return False
    ign = Ign(extra_ignore)
    sd = C.style_diff(app_el["cs"], spec_el["cs"], ign)
    compared = len([k for k in app_el["cs"] if k not in ign])
    ok = not sd
    text = f"{label}: equal to the specimen on {compared} computed properties" if ok else \
        f"{label}: DIFFERS FROM THE SPECIMEN " + ", ".join(f"{k}: {v[0]} vs {v[1]}" for k, v in list(sd.items())[:6])
    for pe in ("::before", "::after"):
        if (pe in app_el) != (pe in spec_el):
            ok, text = False, text + f" ({pe} presence differs)"
        elif pe in app_el:
            psd = C.style_diff(app_el[pe], spec_el[pe], ign)
            if psd:
                ok, text = False, text + f" ({pe} differs {list(psd)[:3]})"
    ctx.R.add(rid, ctx.vw, ok, text)
    return ok


def lit(ctx, rid, ok, text):
    note(ctx, rid, ok, text)


def type_over(pg, sel, text):
    pg.page.click(sel)
    pg.page.keyboard.press("Control+A")
    if text:
        pg.page.keyboard.type(text)
    else:
        pg.page.keyboard.press("Backspace")


def leave(pg):
    pg.page.keyboard.press("Tab")
    pg.page.wait_for_timeout(120)


def run_viewport(browser, base, vw, vh, R, errors):
    vp = (vw, vh)
    sctx = C.gold_ctx(browser, vp)
    spec = C.open_golden(sctx, "states")
    s3ctx = C.gold_ctx(browser, vp)
    g3 = C.open_golden(s3ctx, "bill-empty")
    g5ctx = C.gold_ctx(browser, vp)
    g5 = C.open_golden(g5ctx, "bill-unassigned")

    def app(seed=None, clipboard="recorder", **kw):
        ctx = C.app_ctx(browser, base, vp, seed=seed, clipboard=clipboard, **kw)
        return ctx, C.open_app(ctx, base)

    c = Ctx(R, None, None, vw, "states")

    # ---------------- ST-01 subtotal error, ST-03 the same field focused
    actx, a = app()
    type_over(a, "input#subtotal", "0")
    pre = a.count("p.error")
    leave(a)
    lit(c, "ST-01", pre == 0, f"error not showing while the 0 is still being typed (p.error count {pre})")
    inp = a.one("input#subtotal")
    err = a.one("p.error#subtotal-error")
    lit(c, "ST-01", inp["attrs"].get("aria-invalid") == "true" and inp["attrs"].get("aria-describedby") == "subtotal-error",
        f"input#subtotal aria-invalid={inp['attrs'].get('aria-invalid')}, aria-describedby={inp['attrs'].get('aria-describedby')}, value {inp['value']!r}")
    lit(c, "ST-01", err is not None and err["text"] == "Enter an amount like 12.50", f"p.error#subtotal-error text {err['text'] if err else None!r}")
    prev = a.js("() => { const e = document.querySelector('#subtotal-error'); return e.previousElementSibling.className + '/' + e.previousElementSibling.tagName.toLowerCase(); }")
    lit(c, "ST-01", prev == "cells/div", f"p.error comes right after div.cells (previous sibling {prev})")
    spec_err = spec.one("#s4-subtotal-error")
    spec_eq("ST-01", c, err, spec_err, "p.error vs #s4-subtotal-error")
    lit(c, "ST-01", err["cs"]["margin-top"] == "8px" and spec_err["cs"]["margin-top"] == "8px" and err["cs"]["text-align"] == spec_err["cs"]["text-align"] == "start",
        f"margin-top {err['cs']['margin-top']}, text-align {err['cs']['text-align']} (left aligned, as the specimen)")
    app_field = field_of(a, "input#subtotal")
    spec_field = field_of(spec, "#s4-subtotal")
    spec_eq("ST-01", c, app_field, spec_field, "span.field.money (red border, 2 px inset shadow) vs the specimen's")
    lit(c, "ST-01", app_field["cs"]["border-top-color"] == ERR and app_field["cs"]["box-shadow"].startswith(ERR) and "inset" in app_field["cs"]["box-shadow"],
        f"border colour {app_field['cs']['border-top-color']}, box-shadow {app_field['cs']['box-shadow']}")
    a.page.click("input#subtotal")
    a.page.wait_for_timeout(100)
    spec.page.focus("#s4-subtotal")
    spec.page.wait_for_timeout(100)
    app_f, spec_f = field_of(a, "input#subtotal"), field_of(spec, "#s4-subtotal")
    spec_eq("ST-03", c, app_f, spec_f, "focused error field vs the specimen's field focused the same way")
    cs = app_f["cs"]
    lit(c, "ST-03", cs["border-top-color"] == ERR and cs["outline-width"] == "2px" and cs["outline-style"] == "solid" and cs["outline-color"] == INK
        and cs["outline-offset"] == "2px" and "inset" in cs["box-shadow"],
        f"focused error field keeps border {cs['border-top-color']} and inset shadow, gains outline {cs['outline-width']} {cs['outline-style']} {cs['outline-color']} offset {cs['outline-offset']}")
    spec.page.evaluate("document.activeElement.blur()")
    errors += [("ST-01", vp, m) for m in a.console]
    actx.close()

    # ---------------- ST-02 price error (S1 seed)
    actx, a = app(seed=C.seeds.S1)
    type_over(a, 'input[aria-label="Item 2 price in RM"]', "13.505")
    leave(a)
    perr = a.one("li.item:nth-child(2) .item-line > p.error")
    lit(c, "ST-02", perr is not None and perr["id"] == "price-error-i5" and perr["text"] == "Enter an amount like 12.50", f"p.error#{perr['id'] if perr else None} text {perr['text'] if perr else None!r}")
    last = a.js("() => document.querySelector('li.item:nth-child(2) .item-line').lastElementChild.id")
    lit(c, "ST-02", last == "price-error-i5", f"p.error is the last child of the item's div.item-line ({last})")
    spec_perr = spec.one("#s4-price-error")
    spec_eq("ST-02", c, perr, spec_perr, "p.error vs #s4-price-error")
    lit(c, "ST-02", perr["cs"]["text-align"] == "right" and perr["cs"]["margin-top"] == "0px" and perr["cs"]["grid-column-start"] == "1" and perr["cs"]["grid-column-end"] == "3",
        f"text-align {perr['cs']['text-align']}, margin-top {perr['cs']['margin-top']}, grid-column {perr['cs']['grid-column-start']} / {perr['cs']['grid-column-end']} (spans name and price)")
    pf = field_of(a, 'input[aria-label="Item 2 price in RM"]')
    sp = one_of(spec, "[document.querySelector('input[aria-label=\"Item 1 price in RM\"][aria-invalid=\"true\"]').closest('.field')]")
    spec_eq("ST-02", c, pf, sp, "price field span.field.money vs the specimen's price field")
    pin = a.one('input[aria-label="Item 2 price in RM"]')
    lit(c, "ST-02", pin["attrs"].get("aria-invalid") == "true" and pin["attrs"].get("aria-describedby") == "price-error-i5",
        f"price input aria-invalid={pin['attrs'].get('aria-invalid')}, aria-describedby={pin['attrs'].get('aria-describedby')}")
    gap_a = a.js("() => { const l = document.querySelector('li.item:nth-child(2) .item-line').getBoundingClientRect(); const w = document.querySelector('li.item:nth-child(2) .who'); return [w.getBoundingClientRect().top - l.bottom, getComputedStyle(w).marginTop, getComputedStyle(w).gap]; }")
    gap_s = spec.js("() => { const l = document.querySelector('#s4-price-error').parentElement.getBoundingClientRect(); const w = document.querySelector('#s4-price-error').closest('li').querySelector('.who'); return [w.getBoundingClientRect().top - l.bottom, getComputedStyle(w).marginTop, getComputedStyle(w).gap]; }")
    lit(c, "ST-02", gap_a == gap_s and gap_a[2] == "8px", f"toggles keep their gap: {gap_a} (app) vs {gap_s} (specimen)")
    errors += [("ST-02", vp, m) for m in a.console]
    actx.close()

    # ---------------- ST-04 / ST-05 copy success and failure
    for rid, clip, spec_key, text, cls in (("ST-04", "recorder", "spec-s6a", "Summary copied", "status"),
                                           ("ST-05", "reject", "spec-s6b", "Could not copy. Your browser blocked the clipboard.", "status status-failure")):
        actx, a = app(seed=C.seeds.S2, clipboard=clip)
        a.page.click("button.copy")
        a.page.wait_for_timeout(200)
        st = a.one("p.status")
        sp = spec.one(SPEC.format(spec_key) + " .status")
        lit(c, rid, st is not None and st["text"] == text and st["cls"] == cls and st["attrs"].get("role") == "status",
            f"p.status text {st['text'] if st else None!r}, class {st['cls'] if st else None!r}, role {st['attrs'].get('role') if st else None}")
        spec_eq(rid, c, st, sp, "p.status vs the specimen")
        btn = a.one("button.copy")
        gap = st["rect"][1] - (btn["rect"][1] + btn["rect"][3])
        lit(c, rid, abs(gap - 8) < 0.6 and st["cs"]["text-align"] == "center" and st["cs"]["margin-top"] == "8px" and st["cs"]["font-size"] == "14px"
            and st["cs"]["line-height"] == "20px" and st["cs"]["font-weight"] == "600" and st["cs"]["color"] == (INK if rid == "ST-04" else ERR),
            f"{gap:g} px under Copy summary, text-align {st['cs']['text-align']}, {st['cs']['font-size']}/{st['cs']['line-height']} {st['cs']['font-weight']}, colour {st['cs']['color']}")
        written = a.js("() => [window.testClipboardWrites ?? null, window.testClipboardText ? window.testClipboardText.split('\\n').length : null]")
        lit(c, rid, (written[0] == 1) if clip == "recorder" else (written[0] is None), f"clipboard recorder {written} (the real clipboard is never reached)")
        errors += [(rid, vp, m) for m in a.console]
        actx.close()

    # ---------------- ST-06 / ST-07 / ST-15 note
    actx, a = app(seed=C.seeds.UNREADABLE["B1"])
    note_el = a.one("div.note-wrap > div.note[role=status]")
    lit(c, "ST-06", note_el is not None, "div.note-wrap > div.note[role=status] present")
    order = a.js("() => Array.from(document.querySelector('.app').children).map((e) => e.tagName.toLowerCase() + '.' + e.className).join(' ')")
    lit(c, "ST-06", order == "header.bar div.note-wrap main.layout", f"between the header and the layout: {order}")
    txt = a.js("() => document.querySelector('.note p').textContent")
    lit(c, "ST-06", txt == "Your saved bill could not be read, so a new one was started.", f"text {txt!r}")
    dm = a.one(".note .icon-btn")
    lit(c, "ST-06", dm["attrs"].get("aria-label") == "Dismiss note" and dm["rect"][2] == 44 and dm["rect"][3] == 44, f"button aria-label {dm['attrs'].get('aria-label')!r}, {dm['rect'][2]:g} x {dm['rect'][3]:g}")
    spec_eq("ST-06", c, a.one(".note .icon-btn svg.ph"), spec.one(".note .icon-btn svg.ph"), "X icon svg vs the specimen's")
    pa = a.js("() => document.querySelector('.note .icon-btn svg path').getAttribute('d')")
    pb = spec.js("() => document.querySelector('.note .icon-btn svg path').getAttribute('d')")
    lit(c, "ST-06", pa == pb, f"X path data equal to the specimen's ({len(pa)} characters)")
    spec_eq("ST-06", c, note_el, spec.one(".note"), "div.note vs the specimen's .note")
    spec_eq("ST-06", c, a.one(".note p"), spec.one(".note p"), "div.note p vs the specimen's")
    spec_eq("ST-06", c, dm, spec.one(".note .icon-btn"), "Dismiss note button vs the specimen's")
    spec_eq("ST-06", c, a.one("h1.wordmark"), spec.one("p.wordmark"), "wordmark h1 (app) vs the specimen's p.wordmark (allowed difference 6, the tag only)")
    vals = a.js("() => Array.from(document.querySelectorAll('li.field.person input')).map((i) => i.value + '/' + i.getAttribute('aria-label')).join('|')")
    dis = a.js("() => Array.from(document.querySelectorAll('li.field.person .icon-btn')).map((b) => b.disabled + '/' + b.getAttribute('aria-label')).join('|')")
    lit(c, "ST-07", vals == "Person 1/Person 1 name|Person 2/Person 2 name" and dis == "true/Remove Person 1|true/Remove Person 2", f"people {vals}; removes {dis}")
    msg = a.js("() => [document.querySelector('p.result-msg').textContent, document.querySelector('#mode-even').checked, document.querySelector('#rate-service').value, document.querySelector('#rate-sst').value, document.querySelector('#subtotal').value]")
    lit(c, "ST-07", msg == ["Enter the subtotal to see the shares.", True, "10", "6", ""], f"panel and fields {msg}")
    spec_eq("ST-07", c, a.one("li.field.person:nth-child(1) .icon-btn"), spec.one(SPEC.format("spec-s7") + " li.field.person:nth-child(1) .icon-btn"), "Person 1 remove (disabled) vs the S7 frame's")
    if vw >= 1024:
        hdr, nwrap, nt = a.one("header.bar"), a.one(".note-wrap"), a.one(".note")
        hw = hdr["rect"][2] - float(hdr["cs"]["padding-left"][:-2]) - float(hdr["cs"]["padding-right"][:-2])
        nw = nwrap["rect"][2] - float(nwrap["cs"]["padding-left"][:-2]) - float(nwrap["cs"]["padding-right"][:-2])
        lit(c, "ST-15", abs(nt["rect"][2] - 1040) < 0.6 and abs(hw - 1040) < 0.6 and abs(nw - 1040) < 0.6,
            f"div.note {nt['rect'][2]:g} px wide, header content {hw:g}, note-wrap content {nw:g} (1040 expected)")
    errors += [("ST-06", vp, m) for m in a.console]
    actx.close()

    # ---------------- ST-08 12 people, Add person disabled
    actx, a = app(seed=C.seeds.S8)
    add = a.one("ul.cells > li:last-child .btn")
    sadd = spec.one(SPEC.format("spec-s8a") + " button[disabled]")
    lit(c, "ST-08", add["disabled"] is True and add["cs"]["cursor"] == "not-allowed", f"Add person disabled={add['disabled']}, cursor {add['cs']['cursor']}")
    lit(c, "ST-08", add["cs"]["background-color"] == "rgba(0, 0, 0, 0)" and add["cs"]["border-top-color"] == LINE and add["cs"]["color"] == DIS,
        f"fill {add['cs']['background-color']}, border {add['cs']['border-top-color']}, text {add['cs']['color']}")
    spec_eq("ST-08", c, add, sadd, "Add person (disabled) vs the S8 specimen (not its width)")
    plus = a.one("ul.cells > li:last-child .btn svg.ph")
    spec_eq("ST-08", c, plus, spec.one(SPEC.format("spec-s8a") + " button[disabled] svg.ph"), "plus icon of the disabled button")
    lit(c, "ST-08", plus["cs"]["fill"] == DIS, f"plus icon fill {plus['cs']['fill']}")
    ys = a.js("() => Array.from(document.querySelectorAll('ul.cells > li')).map((l) => Math.round(l.getBoundingClientRect().top))")
    cols = 2 if vw < 600 else 3
    rows = sorted(set(ys[:12]))
    lit(c, "ST-08", len(rows) == math.ceil(12 / cols) and ys[12] > rows[-1],
        f"{len(rows)} rows of {cols} for 12 people (expected {math.ceil(12 / cols)}), Add person in the next cell (top {ys[12]}, last person row top {rows[-1]})")
    errors += [("ST-08", vp, m) for m in a.console]
    actx.close()

    # ---------------- ST-09 two people, both removes disabled (S2, Remove Chen by a real click)
    actx, a = app(seed=C.seeds.S2)
    a.page.click('button[aria-label="Remove Chen"]')
    a.page.wait_for_timeout(100)
    for i in range(2):
        rm = a.one("li.field.person .icon-btn", i)
        lit(c, "ST-09", rm["disabled"] is True and rm["cs"]["color"] == DIS and rm["cs"]["cursor"] == "not-allowed" and rm["cs"]["border-top-color"] == LINES and rm["cs"]["border-left-color"] == LINE,
            f"remove {i + 1}: disabled={rm['disabled']}, colour {rm['cs']['color']}, cursor {rm['cs']['cursor']}, borders kept ({rm['cs']['border-top-color']}, left {rm['cs']['border-left-color']})")
        spec_eq("ST-09", c, rm, spec.one(SPEC.format("spec-s8b") + " .icon-btn[disabled]", i), f"remove {i + 1} vs the S8 2-people specimen")
        spec_eq("ST-09", c, a.one("li.field.person .icon-btn svg.ph", i), spec.one(SPEC.format("spec-s8b") + " .icon-btn[disabled] svg.ph", i), f"X icon {i + 1}")
    errors += [("ST-09", vp, m) for m in a.console]
    actx.close()

    # ---------------- ST-10 rate errors (cold boot)
    actx, a = app()
    type_over(a, "input#rate-service", "31")
    leave(a)
    type_over(a, "input#rate-sst", "20.01")
    leave(a)
    for fid, msg_, eid in (("rate-service", "Enter a rate from 0 to 30", "rate-service-error"), ("rate-sst", "Enter a rate from 0 to 20", "rate-sst-error")):
        e, i_ = a.one(f"p.error#{eid}"), a.one(f"input#{fid}")
        last = a.js("(id) => document.getElementById(id).closest('.cells > div').lastElementChild.id", fid)
        lit(c, "ST-10", e is not None and e["text"] == msg_ and last == eid and i_["attrs"].get("aria-invalid") == "true" and i_["attrs"].get("aria-describedby") == f"{eid} charges-hint",
            f"{eid} text {e['text'] if e else None!r}, last child of its cell ({last}), input aria-invalid {i_['attrs'].get('aria-invalid')}, aria-describedby {i_['attrs'].get('aria-describedby')!r}")
        spec_eq("ST-10", c, e, spec_err, f"p.error#{eid} vs #s4-subtotal-error")
        fw = field_of(a, f"input#{fid}")
        lit(c, "ST-10", fw["cs"]["border-top-color"] == ERR and "inset" in fw["cs"]["box-shadow"], f"{fid} field border {fw['cs']['border-top-color']}, box-shadow {fw['cs']['box-shadow']}")
    errors += [("ST-10", vp, m) for m in a.console]
    actx.close()

    # ---------------- ST-11 other panel messages, ST-12 plural
    res_msg = g3.one("p.result-msg")
    cases = []
    actx, a = app()
    type_over(a, "input#rate-service", "")
    a.page.wait_for_timeout(100)
    cases.append(("Check the charges to see the shares.", a.one("p.result-msg")))
    actx.close()
    actx, a = app()
    a.page.click("label[for=mode-item]")
    a.page.wait_for_timeout(100)
    cases.append(("Add an item to see the shares.", a.one("p.result-msg")))
    a.page.click("section[aria-labelledby=h-items] > .btn")
    a.page.wait_for_timeout(100)
    cases.append(("Give every item a price to see the shares.", a.one("p.result-msg")))
    errors += [("ST-11", vp, m) for m in a.console]
    actx.close()
    for text, el in cases:
        lit(c, "ST-11", el is not None and el["text"] == text, f"message {el['text'] if el else None!r}")
        spec_eq("ST-11", c, el, res_msg, f"p.result-msg ({text[:24]}...) vs S3's p.result-msg")
    actx, a = app(seed=C.seeds.S1)
    a.page.click('div[aria-label="Who had Mee goreng mamak"] .tap:nth-child(3)')
    a.page.click('div[aria-label="Who had Char kuey teow"] .tap:nth-child(2)')
    a.page.wait_for_timeout(100)
    el, sm = a.one("p.result-msg"), g5.one("p.result-msg")
    lit(c, "ST-12", el["text"] == "2 items still need a person. Tap who had each one to see the shares.", f"message {el['text']!r}")
    spec_eq("ST-12", c, el, sm, "plural p.result-msg vs S5's p.result-msg")
    lines = round(el["rect"][3] / 24)
    lit(c, "ST-12", lines == 2, f"{lines} lines ({el['rect'][3]:g} px tall at 24 px per line, S5's singular is {sm['rect'][3]:g})")
    errors += [("ST-12", vp, m) for m in a.console]
    actx.close()

    # ---------------- ST-13 Add item at 50 items
    seed49 = C.seeds.changed(C.seeds.S1, lambda d: C.seeds._many_items(d, 49))
    actx, a = app(seed=seed49)
    a.page.click("section[aria-labelledby=h-items] > .btn")
    a.page.wait_for_timeout(150)
    n_items = a.count("ol.items > li.item")
    add = a.one("section[aria-labelledby=h-items] > .btn")
    lit(c, "ST-13", n_items == 50 and add["disabled"] is True and add["cs"]["cursor"] == "not-allowed", f"{n_items} item rows, Add item disabled={add['disabled']}, cursor {add['cs']['cursor']}")
    spec_eq("ST-13", c, add, sadd, "Add item (disabled) vs the S8 specimen (not its width)")
    spec_eq("ST-13", c, a.one("section[aria-labelledby=h-items] > .btn svg.ph"), spec.one(SPEC.format("spec-s8a") + " button[disabled] svg.ph"), "plus icon of the disabled Add item")
    lit(c, "ST-13", add["rect"][2] < 358, f"natural width {add['rect'][2]:g} px (the specimen button fills a cell)")
    errors += [("ST-13", vp, m) for m in a.console]
    actx.close()

    sctx.close()
    s3ctx.close()
    g5ctx.close()


def run_360(browser, base, R, errors):
    vp = (360, 780)
    sctx = C.gold_ctx(browser, vp)
    spec = C.open_golden(sctx, "states")
    actx = C.app_ctx(browser, base, vp, seed=C.seeds.S2, clipboard="reject")
    a = C.open_app(actx, base)
    c = Ctx(R, a, spec, 360, "states")
    a.page.click("button.copy")
    a.page.wait_for_timeout(200)
    st = a.one("p.status")
    sp = spec.one(SPEC.format("spec-s6b") + " .status")
    lit(c, "ST-14", st["rect"][3] == 40 and st["cs"]["text-align"] == "center" and st["cls"] == "status status-failure",
        f"p.status {st['rect'][2]:g} x {st['rect'][3]:g} (two lines of 20 px), text-align {st['cs']['text-align']}, class {st['cls']!r}")
    lines = a.js("() => { const p = document.querySelector('p.status'); const r = document.createRange(); r.selectNodeContents(p); return new Set(Array.from(r.getClientRects()).map((x) => Math.round(x.top))).size; }")
    lit(c, "ST-14", lines == 2, f"the text wraps onto {lines} lines")
    lit(c, "ST-14", sp["rect"][3] == 40, f"the specimen's failure status is {sp['rect'][3]:g} px tall at 360 as well")
    sw = a.js("() => [document.documentElement.scrollWidth, window.innerWidth]")
    lit(c, "ST-14", sw[0] <= sw[1], f"scrollWidth {sw[0]} <= innerWidth {sw[1]} (no horizontal overflow)")
    spec_eq("ST-14", c, st, sp, "p.status at 360 vs the specimen")
    errors += [("ST-14", vp, m) for m in a.console]
    actx.close()
    sctx.close()


def main():
    R = Rows()
    errors = []
    server = C.rig.StaticServer(C.ROOT, say=print)
    try:
        server.start()
        with sync_playwright() as pw:
            browser = C.launch(pw)
            run_viewport(browser, server.base, 390, 844, R, errors)
            run_viewport(browser, server.base, 1280, 800, R, errors)
            run_360(browser, server.base, R, errors)
            browser.close()
    finally:
        server.stop()
    out = {"rows": {rid: {str(vw): [[ok, t] for ok, t in v] for vw, v in sorted(by.items())} for rid, by in sorted(R.d.items())}, "console_errors": errors}
    C.dump("rows_states.json", out)
    fails = sorted(rid for rid, by in R.d.items() if any(not ok for v in by.values() for ok, _ in v))
    print(f"rows with results {len(R.d)}: {sorted(R.d)}")
    print(f"failing rows {len(fails)}: {fails}")
    print("console errors:", errors)


if __name__ == "__main__":
    main()
