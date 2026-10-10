"""FE element checklist rows for the five screen goldens (qa.md: S1, S2, S3, S5, M1), run on the running app against the golden.

usage: python rows_screens.py
Each screen is opened at 390x844 and at 1280x800 (and the 360x780 rows S2-28 and M1-09 at 360x780). The golden is opened at the
same size from its file. The app is reached by its real load path (storage_state seed) and, for M1, by a real mouse click on
"New bill". Results go to rows_screens.json.
"""
import sys

sys.dont_write_bytecode = True

from playwright.sync_api import sync_playwright

import common as C
from rows_lib import Ctx, Rows, ck, ck_count, note, parse_qa_rows

INK, MUTED, DIS = C.rgb("ink"), C.rgb("ink-muted"), C.rgb("ink-disabled")
FIELD, LINE, LINES = C.rgb("field"), C.rgb("line"), C.rgb("line-strong")
ON, ACC, ERR = C.rgb("on-ink"), C.rgb("accent"), C.rgb("error")
SURFACE = C.rgb("surface")
CLEAR = "rgba(0, 0, 0, 0)"
PEO = "section[aria-labelledby=h-people]"
ITM = "section[aria-labelledby=h-items]"
SUB = "section[aria-labelledby=h-subtotal]"
CHG = "section[aria-labelledby=h-charges]"
TAPE = "div.tape"
NATIVE_MODAL = ("overflow", "overflow-x", "overflow-y", "overflow-block", "overflow-inline", "max-height", "max-block-size", "overlay", "user-select", "interactivity")

ITEMS_S1 = [("Nasi lemak ayam", "15.90", [1, 0, 0]), ("Char kuey teow", "13.50", [0, 1, 0]),
            ("Mee goreng mamak", "12.00", [0, 0, 1]), ("Satay, 10 sticks", "18.00", [1, 0, 1])]
ITEMS_S5 = [ITEMS_S1[0], ITEMS_S1[1], ("Mee goreng mamak", "12.00", [0, 0, 0]), ITEMS_S1[3]]
PEOPLE3 = ["Aisyah", "Ben", "Chen"]
SUM_S1 = [("", "Subtotal", "RM 59.40", None), ("+", "Service charge", "RM 5.94", "10% of RM 59.40"), ("+", "SST", "RM 3.92", "6% of RM 65.34")]
SUM_S2 = [("", "Subtotal", "RM 100.00", None), ("+", "Service charge", "RM 10.00", "10% of RM 100.00"), ("+", "SST", "RM 6.60", "6% of RM 110.00")]
SHARES_S1 = [("Aisyah", "RM 24.90", "RM 4.14", "RM 29.04"), ("Ben", "RM 13.50", "RM 2.24", "RM 15.74"), ("Chen", "RM 21.00", "RM 3.48", "RM 24.48")]


def lay(vw):
    """Layout numbers system.css gives at a viewport width."""
    if vw >= 1024:
        return dict(cx=120, cw=1040, price=120, left_w=556, ncols=3, tape_x=740, tape_w=420)
    if vw >= 600:
        x0 = (vw - 560) / 2
        return dict(cx=x0 + 16, cw=528, price=120, left_w=528, ncols=int((528 + 8) // 148), tape_x=x0 + 16, tape_w=528)
    return dict(cx=16, cw=vw - 32, price=96, left_w=vw - 32, ncols=int((vw - 32 + 8) // 148), tape_x=0, tape_w=vw)


# ---------------------------------------------------------------- components
def header(ctx, ids):
    ck(ctx, ids.get("wordmark"), "h1.wordmark", exp={"text": "Split", "fs": "22px", "lh": "28px", "fw": "700", "color": INK, "ls": "-0.22px", "tag": "h1"})
    bar = ctx.app.one("header.bar")
    right = bar["rect"][0] + bar["rect"][2] - float(bar["cs"]["padding-right"][:-2])
    ck(ctx, ids.get("newbill"), "header.bar .btn.btn-outline",
       exp={"text": "New bill", "bg": FIELD, "b4": f"1px solid {LINES}", "fs": "15px", "lh": "20px", "fw": "600", "color": INK, "r": right, "rad": "6px"})


def people(ctx, ids, names, disabled_removes):
    L = lay(ctx.vw)
    ck(ctx, ids.get("h-people"), "h2#h-people", exp={"text": "People", "fs": "18px", "lh": "24px", "fw": "700", "tag": "h2", "mb": "12px"})
    for i, name in enumerate(names):
        li = f"{PEO} ul.cells > li.field.person:nth-child({i + 1})"
        ck(ctx, ids.get(f"p{i}f"), li + " input", label=f"person {i + 1} input",
           exp={"@aria-label": f"Person {i + 1} name", "value": name, "@maxlength": "20", "@type": "text", "@autocomplete": "off",
                "@placeholder": f"Person {i + 1}", "fs": "16px", "lh": "24px", "color": INK, "pad": "0px 12px 0px 12px", "h": 42})
        ck(ctx, ids.get(f"p{i}f"), li, label=f"person {i + 1} field wrapper",
           exp={"bg": FIELD, "b4": f"1px solid {LINES}", "rad": "6px", "h": 44, "cls": "field person"})
        rm = {"@aria-label": f"Remove {name}", "disabled": disabled_removes, "w": 44, "h": 44, "bt": f"1px solid {LINES}",
              "bb": f"1px solid {LINES}", "br": f"1px solid {LINES}", "bl": f"1px solid {LINE}", "radii": "0px 6px 6px 0px", "bg": CLEAR,
              "color": DIS if disabled_removes else MUTED, "cursor": "not-allowed" if disabled_removes else "pointer", "@type": "button"}
        ck(ctx, ids.get(f"p{i}r"), li + " .icon-btn", exp=rm, label=f"person {i + 1} remove")
        ck(ctx, ids.get(f"p{i}r"), li + " .icon-btn svg.ph", label=f"person {i + 1} remove X icon",
           exp={"w": 20, "h": 20, "fill": DIS if disabled_removes else MUTED, "@aria-hidden": "true", "@viewBox": "0 0 256 256", "@focusable": "false"})
    n = len(names)
    cell_w = (L["left_w"] - 8 * (L["ncols"] - 1)) / L["ncols"]
    ul = ctx.app.one(f"{PEO} ul.cells")
    col, row = n % L["ncols"], n // L["ncols"]
    add = f"{PEO} ul.cells > li:last-child .btn"
    ck(ctx, ids.get("add-person"), add, label="Add person",
       exp={"text": "Add person", "cls": "btn btn-outline", "disabled": False, "bg": FIELD, "b4": f"1px solid {LINES}", "w": cell_w, "h": 44,
            "x": ul["rect"][0] + col * (cell_w + 8), "y": ul["rect"][1] + row * 52, "fs": "15px", "fw": "600", "color": INK, "cursor": "pointer"})
    ck(ctx, ids.get("add-person"), add + " svg.ph", label="Add person plus icon", exp={"w": 18, "h": 18, "fill": MUTED})
    tracks = ul["cs"]["grid-template-columns"].split()
    ck(ctx, ids.get("grid"), f"{PEO} ul.cells", label="people grid", exp={"disp": "grid", "gap": "8px"})
    note(ctx, ids.get("grid"), len(tracks) == L["ncols"] and ul["cs"]["column-gap"] == "8px" and ul["cs"]["row-gap"] == "8px",
         f"people grid: {len(tracks)} columns ({ul['cs']['grid-template-columns']}), expected {L['ncols']} at {ctx.vw}, gaps {ul['cs']['column-gap']} / {ul['cs']['row-gap']}")


def mode(ctx, ids, checked):
    ck(ctx, ids.get("mode"), "fieldset.mode",
       exp={"disp": "grid", "bg": FIELD, "b4": f"1px solid {LINES}", "rad": "6px", "ov": "hidden", "mt": "24px"})
    ck(ctx, ids.get("mode"), "fieldset.mode legend", label="hidden legend", exp={"text": "Split mode", "cls": "sr-only", "w": 1, "h": 1})
    la, lb = ctx.app.one("fieldset.mode label", 0), ctx.app.one("fieldset.mode label", 1)
    note(ctx, ids.get("mode"), abs(la["rect"][2] - lb["rect"][2]) < 0.6 and la["rect"][3] == 44 and lb["rect"][3] == 44,
         f"two equal 44 px halves: {la['rect'][2]:g} x {la['rect'][3]:g} and {lb['rect'][2]:g} x {lb['rect'][3]:g}")
    ck(ctx, ids.get("mode"), "fieldset.mode label", nth=1, label="By item half (divider)", exp={"bl": f"1px solid {LINES}"})
    even = checked == "even"
    ck(ctx, ids.get("even"), "label[for=mode-even]", label="Even label",
       exp={"text": "Even", "bg": INK if even else CLEAR, "color": ON if even else INK, "fs": "15px", "lh": "20px", "fw": "600", "cursor": "pointer"})
    ck(ctx, ids.get("even"), "#mode-even", label="Even radio", exp={"checked": even, "@type": "radio", "@name": "mode", "@value": "even"})
    ck(ctx, ids.get("by-item"), "label[for=mode-item]", label="By item label",
       exp={"text": "By item", "bg": CLEAR if even else INK, "color": INK if even else ON, "fs": "15px", "lh": "20px", "fw": "600"})
    ck(ctx, ids.get("by-item"), "#mode-item", label="By item radio", exp={"checked": not even, "@type": "radio", "@name": "mode", "@value": "item"})


def subtotal(ctx, ids, value):
    L = lay(ctx.vw)
    cell_w = (L["left_w"] - 8 * (L["ncols"] - 1)) / L["ncols"]
    ck(ctx, ids.get("h-subtotal"), "h2#h-subtotal", exp={"fs": "18px", "lh": "24px", "fw": "700", "tag": "h2", "text": "Subtotal in RM"})
    ck(ctx, ids.get("h-subtotal"), "h2#h-subtotal label", label="label[for=subtotal]", exp={"@for": "subtotal", "text": "Subtotal in RM"})
    ck(ctx, ids.get("sub-field"), f"{SUB} .cells .field.money", label="Subtotal field",
       exp={"w": cell_w, "h": 44, "bg": FIELD, "b4": f"1px solid {LINES}", "rad": "6px", "cls": "field money", "x": L["cx"]})
    ck(ctx, ids.get("sub-field"), f"{SUB} .field.money .unit", label="RM unit", exp={"text": "RM", "color": MUTED, "@aria-hidden": "true", "pl": "8px"})
    ck(ctx, ids.get("sub-field"), "input#subtotal", label="input#subtotal",
       exp={"value": value, "@inputmode": "decimal", "@autocomplete": "off", "@type": "text", "@aria-invalid": None, "@aria-describedby": None,
            "ta": "right", "pad": "0px 8px 0px 4px", "fs": "16px"})
    ck_count(ctx, ids.get("sub-field"), "p.error", 0, label="p.error elements in the DOM", dom=True)


def items(ctx, ids, data):
    L = lay(ctx.vw)
    ck(ctx, ids.get("h-items"), "h2#h-items", exp={"text": "Items", "fs": "18px", "lh": "24px", "fw": "700", "tag": "h2"})
    for k, (name, price, who) in enumerate(data, start=1):
        li = f"{ITM} ol.items > li.item:nth-child({k})"
        if k == 1:
            ck(ctx, ids.get("sep"), li, label="item 1 (no separator)", exp={"bt": f"0px none {INK}", "pt": "0px", "pb": "16px", "cls": "item"})
        else:
            ck(ctx, ids.get("sep"), li, label=f"item {k} separator", exp={"bt": f"1px solid {LINE}", "pt": "16px", "pb": "16px", "cls": "item"})
        ck(ctx, ids.get(f"i{k}n"), li + " .item-line > .field:nth-child(1) input", label=f"item {k} name",
           exp={"value": name, "@aria-label": f"Item {k} name", "@maxlength": "40", "@autocomplete": "off", "@placeholder": f"Item {k}", "@type": "text", "fs": "16px", "lh": "24px"})
        ck(ctx, ids.get(f"i{k}n"), li + " .item-line > .field:nth-child(1)", label=f"item {k} name wrapper", exp={"bg": FIELD, "b4": f"1px solid {LINES}", "rad": "6px", "h": 44})
        ck(ctx, ids.get(f"i{k}p"), li + " .field.money", label=f"item {k} price field", exp={"w": L["price"], "h": 44, "bg": FIELD, "b4": f"1px solid {LINES}", "rad": "6px"})
        ck(ctx, ids.get(f"i{k}p"), li + " .field.money .unit", label=f"item {k} RM unit", exp={"text": "RM", "color": MUTED, "@aria-hidden": "true"})
        ck(ctx, ids.get(f"i{k}p"), li + " .field.money input", label=f"item {k} price input",
           exp={"value": price, "ta": "right", "@aria-label": f"Item {k} price in RM", "@inputmode": "decimal", "@autocomplete": "off", "@aria-invalid": None})
        ck(ctx, ids.get(f"i{k}r"), li + " .item-line > .icon-btn", label=f"item {k} remove",
           exp={"@aria-label": f"Remove {name}", "w": 44, "h": 44, "color": MUTED, "disabled": False, "bg": CLEAR, "rad": "6px", "cursor": "pointer"})
        ck(ctx, ids.get(f"i{k}r"), li + " .item-line > .icon-btn svg.ph", label=f"item {k} remove X icon", exp={"w": 20, "h": 20, "fill": MUTED})
        ck(ctx, ids.get(f"i{k}t"), li + " .who", label=f"item {k} toggle group",
           exp={"@role": "group", "@aria-label": f"Who had {name}", "gap": "8px", "mt": "8px", "disp": "flex"})
        for j, person in enumerate(PEOPLE3):
            on = bool(who[j])
            ck(ctx, ids.get(f"i{k}t"), li + f" .who .tap:nth-child({j + 1})", label=f"item {k} toggle {person}",
               exp={"text": person, "@aria-pressed": "true" if on else "false", "bg": INK if on else FIELD, "color": ON if on else INK,
                    "b4": f"1px solid {INK if on else LINES}", "h": 44, "fs": "15px", "lh": "20px", "fw": "600", "rad": "6px", "pad": "0px 12px 0px 12px", "cursor": "pointer"})
    ol = ctx.app.one(f"{ITM} ol.items")
    ck(ctx, ids.get("add-item"), f"{ITM} > .btn", label="Add item",
       exp={"text": "Add item", "cls": "btn btn-outline", "disabled": False, "bg": FIELD, "b4": f"1px solid {LINES}", "h": 44, "x": ol["rect"][0],
            "y": ol["rect"][1] + ol["rect"][3], "fs": "15px", "fw": "600", "cursor": "pointer"})
    add = ctx.app.one(f"{ITM} > .btn")
    note(ctx, ids.get("add-item"), add["rect"][2] < L["cw"] - 40, f"natural width {add['rect'][2]:g} px (not the full {L['cw']:g} px line)")
    ck(ctx, ids.get("add-item"), f"{ITM} > .btn svg.ph", label="Add item plus icon", exp={"w": 18, "h": 18, "fill": MUTED})


def charges(ctx, ids):
    L = lay(ctx.vw)
    cell_w = (L["left_w"] - 8 * (L["ncols"] - 1)) / L["ncols"]
    ck(ctx, ids.get("h-charges"), "h2#h-charges", exp={"text": "Charges", "fs": "18px", "lh": "24px", "fw": "700", "tag": "h2"})
    for i, (field_id, label, value, rid_l, rid_i) in enumerate((("rate-service", "Service charge", "10", "label-svc", "input-svc"),
                                                                ("rate-sst", "SST", "6", "label-sst", "input-sst"))):
        ck(ctx, ids.get(rid_l), f"label[for={field_id}]", label=f"{label} label",
           exp={"text": f"{label} in percent", "fs": "15px", "lh": "20px", "fw": "600", "disp": "block", "mb": "8px", "color": INK})
        ck(ctx, ids.get(rid_l), f"label[for={field_id}] .sr-only", label=f"{label} hidden ending", exp={"text": "in percent", "w": 1, "h": 1})
        ck(ctx, ids.get(rid_i), f"input#{field_id}", label=f"{label} input",
           exp={"value": value, "ta": "right", "@aria-describedby": "charges-hint", "@inputmode": "decimal", "@autocomplete": "off", "@aria-invalid": None,
                "pad": "0px 2px 0px 12px", "fs": "16px"})
        ck(ctx, ids.get(rid_i), f"{CHG} .cells > div:nth-child({i + 1}) .field.percent", label=f"{label} field",
           exp={"w": cell_w, "h": 44, "bg": FIELD, "b4": f"1px solid {LINES}", "rad": "6px", "x": L["cx"] + i * (cell_w + 8)})
        ck(ctx, ids.get(rid_i), f"{CHG} .cells > div:nth-child({i + 1}) .unit", label=f"{label} % unit", exp={"text": "%", "color": MUTED, "@aria-hidden": "true", "pr": "12px"})
    ck(ctx, ids.get("hint"), "p.hint#charges-hint", exp={"text": "Set a charge to 0 if your bill already includes it.", "fs": "14px", "lh": "20px", "color": MUTED, "mt": "8px", "fw": "400"})


def tape_frame(ctx, ids):
    L = lay(ctx.vw)
    if ctx.vw >= 1024:
        exp = {"w": 420, "x": L["tape_x"], "b4": f"1px solid {INK}", "rad": "6px", "pos": "sticky", "top": "24px", "pad": "24px 24px 24px 24px", "bg": SURFACE}
    elif ctx.vw >= 600:
        exp = {"w": L["tape_w"], "x": L["tape_x"], "b4": f"1px solid {INK}", "rad": "6px", "pad": "24px 24px 24px 24px", "bg": SURFACE}
    else:
        exp = {"w": L["tape_w"], "x": 0, "bt": f"2px solid {INK}", "bb": f"1px solid {LINE}", "bl": f"0px none {INK}", "br": f"0px none {INK}", "rad": "0px",
               "pad": "20px 16px 24px 16px", "mt": "32px", "bg": SURFACE}
    a = ck(ctx, ids.get("frame"), TAPE, label="panel frame", exp=exp)
    if ctx.vw >= 1024 and a and ids.get("frame"):
        ppl = ctx.app.one(PEO)
        note(ctx, ids.get("frame"), abs(a["rect"][1] - ppl["rect"][1]) < 0.6, f"panel top {a['rect'][1]:g} equals People block top {ppl['rect'][1]:g}")
        pg = ctx.app.page
        pg.evaluate("window.scrollTo(0, 120)")
        pg.wait_for_timeout(80)
        moved = pg.evaluate("document.querySelector('div.tape').getBoundingClientRect().top")
        reach = pg.evaluate("document.documentElement.scrollHeight - innerHeight")
        pg.evaluate("window.scrollTo(0, 0)")
        gone = ctx.gold.page
        gone.evaluate("window.scrollTo(0, 120)")
        gone.wait_for_timeout(80)
        gtop = gone.evaluate("document.querySelector('div.tape').getBoundingClientRect().top")
        gone.evaluate("window.scrollTo(0, 0)")
        note(ctx, ids.get("frame"), abs(moved - gtop) < 0.6, f"scrolled 120 px (page scrolls {reach} px): panel top {moved:g} in the app, {gtop:g} in the golden (sticky behaves the same)")
    return a


def summary(ctx, ids, rows, total, with_summary=True):
    if not with_summary:
        ck_count(ctx, ids.get("sum-gone"), "#h-summary", 0, label="Bill summary heading", dom=True)
        ck_count(ctx, ids.get("sum-gone"), "dl.sum", 0, label="dl.sum", dom=True)
        return
    ck(ctx, ids.get("h-summary"), "h2#h-summary", exp={"text": "Bill summary", "fs": "18px", "lh": "24px", "fw": "700", "tag": "h2"})
    for i, (op, label, amt, work) in enumerate(rows, start=1):
        row = f"dl.sum > .row:nth-child({i})"
        rid = ids.get(f"row{i}")
        ck(ctx, rid, row + " dt", label=f"row {i} label", exp={"text": f"{op}{label}", "fs": "16px"})
        ck(ctx, rid, row + " dt .op", label=f"row {i} operator", exp={"text": op, "color": MUTED, "fw": "600", "w": 20, "ta": "center", "@aria-hidden": "true", "mr": "8px"})
        ck(ctx, rid, row + " dd.amt", label=f"row {i} amount", exp={"text": amt, "ta": "right", "ws": "nowrap", "fs": "16px"})
        if work:
            ck(ctx, rid, row + " dd.work", label=f"row {i} working", exp={"text": work, "fs": "15px", "lh": "20px", "color": MUTED, "pl": "28px"})
        else:
            ck_count(ctx, rid, row + " dd.work", 0, label=f"row {i} working lines", dom=True)
    tot, rid = "dl.sum > .row.total", ids.get("total")
    a = ck(ctx, rid, tot, label="Total row", exp={"cls": "row total", "mt": "12px", "pt": "12px", "pos": "relative"})
    if a and rid:
        b = a["::before"]
        note(ctx, rid, b["content"] == '""' and b["border-top-width"] == "1px" and b["border-top-style"] == "solid" and b["border-top-color"] == INK and b["left"] == "28px"
             and b["right"] == "0px" and b["top"] == "0px" and b["position"] == "absolute",
             "1 px ink rule above from 28 px (::before: " + ", ".join(f"{k}={b[k]}" for k in ("position", "top", "left", "right", "border-top-width", "border-top-style", "border-top-color")) + ")")
    ck(ctx, rid, tot + " dt", label="Total label", exp={"text": "=Total", "fs": "18px", "fw": "700", "color": INK})
    ck(ctx, rid, tot + " dd.amt", label="Total amount cell", exp={"fs": "26px", "lh": "32px", "fw": "700", "ta": "right"})
    ck(ctx, rid, tot + " .final", label="span.final", exp={"text": total, "bb": f"3px double {INK}", "disp": "inline-block", "lh": "29.9px", "fs": "26px", "fw": "700"})


def shares_heading(ctx, ids, gap_after_summary=True):
    ck(ctx, ids.get("h-shares"), "h2#h-shares", exp={"text": "Shares", "fs": "18px", "lh": "24px", "fw": "700", "tag": "h2"})
    if gap_after_summary and ids.get("h-shares"):
        ck(ctx, ids.get("h-shares"), f"{TAPE} .tape-section:nth-child(2)", label="Shares section (32 px under the Total)", exp={"mt": "32px"})
        s1 = ctx.app.one(f"{TAPE} .tape-section:nth-child(1)")
        s2 = ctx.app.one(f"{TAPE} .tape-section:nth-child(2)")
        gap = s2["rect"][1] - (s1["rect"][1] + s1["rect"][3])
        note(ctx, ids.get("h-shares"), abs(gap - 32) < 0.6, f"gap between the Bill summary section and the Shares section {gap:g} px (32 expected)")


def table_item(ctx, ids, rows, check):
    t = "table.shares"
    sec = ctx.app.one(f"{TAPE} .tape-section:nth-child(2)")
    ck(ctx, ids.get("heads"), t, label="table.shares", exp={"cls": "shares", "@aria-labelledby": "h-shares", "mt": "8px", "w": sec["rect"][2]})
    for i, full in enumerate(("Person", "Items", "+Charges", "=Share"), start=1):
        sel = f"{t} thead th:nth-child({i})"
        if i == 1:
            ck(ctx, ids.get("heads"), sel + " .sr-only", label="head 1 (hidden Person)", exp={"text": "Person", "w": 1, "h": 1, "pos": "absolute"})
        else:
            ck(ctx, ids.get("heads"), sel, label=f"head {i}", exp={"text": full, "fs": "13px", "lh": "18px", "fw": "600", "color": MUTED, "ta": "right", "va": "bottom", "pt": "0px", "pb": "4px"})
            if full[0] in "+=":
                ck(ctx, ids.get("heads"), sel + " .op", label=f"head {i} operator", exp={"text": full[0], "disp": "inline", "mr": "4px", "@aria-hidden": "true"})
    for r, (name, items_, charges_, share) in enumerate(rows, start=1):
        row, rid = f"{t} tbody tr:nth-child({r})", ids.get(f"srow{r}")
        ck(ctx, rid, row + " th", label=f"row {r} name", exp={"text": name, "fs": "15px", "fw": "600", "color": INK, "ta": "left", "pl": "28px", "@scope": "row"})
        ck(ctx, rid, row + " td:nth-child(2)", label=f"row {r} items", exp={"text": items_, "fs": "14px", "color": MUTED, "ta": "right", "fw": "400", "ws": "nowrap"})
        ck(ctx, rid, row + " td:nth-child(3)", label=f"row {r} charges", exp={"text": charges_, "fs": "14px", "color": MUTED, "ta": "right", "fw": "400"})
        ck(ctx, rid, row + " td.share", label=f"row {r} share", exp={"text": share, "fs": "18px", "fw": "700", "color": INK, "ta": "right", "cls": "share"})
    check_row(ctx, ids, list(check))


def table_even(ctx, ids, rows, check):
    t = "table.shares"
    ck(ctx, ids.get("heads"), "thead.sr-only", label="thead.sr-only", exp={"cls": "sr-only", "w": 1, "h": 1, "pos": "absolute"})
    heads = ctx.app.js("() => Array.from(document.querySelectorAll('table.shares thead th')).map((t) => t.textContent.trim() + '/' + t.getAttribute('scope')).join('|')")
    note(ctx, ids.get("heads"), heads == "Person/col|Share/col", f"hidden heads read {heads}")
    for r, (name, share) in enumerate(rows, start=1):
        row, rid = f"{t} tbody tr:nth-child({r})", ids.get(f"srow{r}")
        ck(ctx, rid, row + " th", label=f"row {r} name", exp={"text": name, "fs": "15px", "fw": "600", "color": INK, "ta": "left", "pl": "28px", "@scope": "row"})
        ck(ctx, rid, row + " td.share", label=f"row {r} share", exp={"text": share, "fs": "18px", "fw": "700", "color": INK, "ta": "right"})
        ck_count(ctx, rid, row + " > *", 2, label=f"row {r} cells (no Items or Charges cell)", dom=True)
    check_row(ctx, ids, [check])


def check_row(ctx, ids, values):
    rid = ids.get("check")
    tf = "table.shares tfoot tr"
    ck(ctx, rid, tf + " th", label="check row label", exp={"text": "Adds up to", "color": ACC, "fs": "15px", "fw": "600", "ta": "left", "pl": "28px", "pt": "12px", "pb": "0px", "pos": "relative", "@scope": "row"})
    th = ctx.app.one(tf + " th")
    if rid and th:
        note(ctx, rid, "linear-gradient" in th["cs"]["background-image"] and th["cs"]["background-size"] == "100% 1px" and th["cs"]["background-position"] == "28px 0px"
             and th["cs"]["background-repeat"] == "no-repeat",
             f"1 px ink rule from 28 px in the name column (background {th['cs']['background-size']} at {th['cs']['background-position']}, {th['cs']['background-repeat']}, {th['cs']['background-image'][:44]})")
    ck(ctx, rid, tf + " th svg.ph", label="check icon",
       exp={"w": 18, "h": 18, "fill": ACC, "pos": "absolute", "left": "0px", "top": "14px", "x": th["rect"][0] if th else 0, "@aria-hidden": "true", "@viewBox": "0 0 256 256"})
    for i, v in enumerate(values, start=2):
        last = i == len(values) + 1
        exp = {"text": v, "bt": f"1px solid {INK}", "ta": "right", "pt": "12px", "pb": "0px"}
        exp.update({"fs": "18px", "fw": "700", "color": ACC, "cls": "share"} if last else {"fs": "14px", "fw": "400", "color": MUTED})
        ck(ctx, rid, tf + f" td:nth-child({i})", label=f"check cell {i - 1}", exp=exp)


def copy_and_status(ctx, ids, present=True):
    if not present:
        for sel, rid, label in (("button.copy", ids.get("copy"), "Copy summary button"), ("table.shares", ids.get("copy"), "shares table"), ("p.status", ids.get("status"), "p.status")):
            ck_count(ctx, rid, sel, 0, label=label, dom=True)
        return
    sh = ctx.app.one(f"{TAPE} .tape-section:nth-child(2)")
    table = ctx.app.one("table.shares")
    ck(ctx, ids.get("copy"), "button.copy", label="Copy summary",
       exp={"cls": "btn btn-primary btn-large btn-block copy", "text": "Copy summary", "bg": INK, "color": ON, "b4": f"1px solid {INK}", "h": 48, "w": sh["rect"][2],
            "mt": "24px", "fs": "16px", "lh": "24px", "fw": "600", "y": table["rect"][1] + table["rect"][3] + 24, "disabled": False, "cursor": "pointer", "rad": "6px"})
    ck(ctx, ids.get("copy"), "button.copy svg.ph", label="copy icon", exp={"w": 20, "h": 20, "fill": ON})
    probe = "() => { const p = document.querySelector('p.status'); return { n: document.querySelectorAll('p.status').length, display: getComputedStyle(p).display, text: p.textContent, role: p.getAttribute('role'), cls: p.className, rects: p.getClientRects().length }; }"
    s, g = ctx.app.js(probe), ctx.gold.js(probe)
    note(ctx, ids.get("status"), s["n"] == 1 and s["display"] == "none" and s["text"] == "" and s["role"] == "status" and s["cls"] == "status" and s["rects"] == 0 and s == g,
         f"p.status[role={s['role']}] present, text {s['text']!r}, class {s['cls']!r}, display {s['display']} (empty, not displayed), golden {'same' if s == g else g}")


# ---------------------------------------------------------------- screens
def ids_s1():
    d = {"wordmark": "S1-01", "newbill": "S1-02", "h-people": "S1-03", "p0f": "S1-04", "p0r": "S1-05", "p1f": "S1-06", "p1r": "S1-07", "p2f": "S1-08",
         "p2r": "S1-09", "add-person": "S1-10", "grid": "S1-11", "mode": "S1-12", "even": "S1-13", "by-item": "S1-14", "h-items": "S1-15", "sep": "S1-32",
         "add-item": "S1-33", "h-charges": "S1-34", "label-svc": "S1-35", "input-svc": "S1-36", "label-sst": "S1-37", "input-sst": "S1-38", "hint": "S1-39",
         "frame": "S1-40", "h-summary": "S1-41", "row1": "S1-42", "row2": "S1-43", "row3": "S1-44", "total": "S1-45", "h-shares": "S1-46", "heads": "S1-47",
         "srow1": "S1-48", "srow2": "S1-49", "srow3": "S1-50", "check": "S1-51", "copy": "S1-52", "status": "S1-53"}
    for k, base in ((1, 16), (2, 20), (3, 24), (4, 28)):
        d[f"i{k}n"], d[f"i{k}p"], d[f"i{k}r"], d[f"i{k}t"] = f"S1-{base:02d}", f"S1-{base + 1:02d}", f"S1-{base + 2:02d}", f"S1-{base + 3:02d}"
    return d


def screen_s1(ctx):
    ids = ids_s1()
    header(ctx, ids)
    people(ctx, ids, PEOPLE3, False)
    mode(ctx, ids, "item")
    items(ctx, ids, ITEMS_S1)
    ck_count(ctx, "S1-15", SUB, 0, label="Subtotal block (even mode only)")
    charges(ctx, ids)
    tape_frame(ctx, ids)
    summary(ctx, ids, SUM_S1, "RM 69.26")
    shares_heading(ctx, ids)
    table_item(ctx, ids, SHARES_S1, ("RM 59.40", "RM 9.86", "RM 69.26"))
    copy_and_status(ctx, ids)


def screen_s2(ctx):
    ids = {"wordmark": "S2-01", "newbill": "S2-02", "h-people": "S2-03", "p0f": "S2-04", "p0r": "S2-04", "p1f": "S2-04", "p1r": "S2-04", "p2f": "S2-04",
           "p2r": "S2-04", "add-person": "S2-05", "grid": "S2-06", "mode": "S2-07", "even": "S2-08", "by-item": "S2-09", "h-subtotal": "S2-10",
           "sub-field": "S2-11", "h-charges": "S2-13", "label-svc": "S2-13", "input-svc": "S2-13", "label-sst": "S2-13", "input-sst": "S2-13", "hint": "S2-13",
           "frame": "S2-14", "h-summary": "S2-15", "row1": "S2-16", "row2": "S2-17", "row3": "S2-18", "total": "S2-19", "h-shares": "S2-20", "heads": "S2-21",
           "srow1": "S2-22", "srow2": "S2-23", "srow3": "S2-24", "check": "S2-25", "copy": "S2-26", "status": "S2-27"}
    header(ctx, ids)
    people(ctx, ids, PEOPLE3, False)
    mode(ctx, ids, "even")
    subtotal(ctx, ids, "100.00")
    ck_count(ctx, "S2-12", ITM, 0, label="Items block (by-item mode only)")
    charges(ctx, ids)
    tape_frame(ctx, ids)
    summary(ctx, ids, SUM_S2, "RM 116.60")
    shares_heading(ctx, ids)
    table_even(ctx, ids, [("Aisyah", "RM 38.87"), ("Ben", "RM 38.87"), ("Chen", "RM 38.86")], "RM 116.60")
    copy_and_status(ctx, ids)


def msg_row(ctx, rid, text, lines):
    h = ctx.app.one("h2#h-shares")
    ck(ctx, rid, "p.result-msg", label="result message",
       exp={"text": text, "fs": "16px", "lh": "24px", "color": INK, "fw": "400", "mt": "8px", "h": 24 * lines, "x": h["rect"][0], "y": h["rect"][1] + h["rect"][3] + 8, "cls": "result-msg"})
    ck_count(ctx, rid, "p.result-msg", 1, label="p.result-msg elements", dom=True)


def screen_s3(ctx):
    ids = {"wordmark": "S3-01", "newbill": "S3-01", "h-people": "S3-01", "p0f": "S3-02", "p0r": "S3-03", "p1f": "S3-04", "p1r": "S3-05", "add-person": "S3-06",
           "grid": "S3-06", "mode": "S3-07", "even": "S3-07", "by-item": "S3-07", "h-subtotal": "S3-08", "sub-field": "S3-08", "h-charges": "S3-09",
           "label-svc": "S3-09", "input-svc": "S3-09", "label-sst": "S3-09", "input-sst": "S3-09", "hint": "S3-09", "frame": "S3-10", "sum-gone": "S3-11",
           "h-shares": "S3-12", "copy": "S3-14", "status": "S3-14"}
    header(ctx, ids)
    people(ctx, ids, ["Person 1", "Person 2"], True)
    mode(ctx, ids, "even")
    subtotal(ctx, ids, "")
    charges(ctx, ids)
    tape_frame(ctx, ids)
    summary(ctx, ids, [], "", with_summary=False)
    shares_heading(ctx, ids, gap_after_summary=False)
    msg_row(ctx, "S3-13", "Enter the subtotal to see the shares.", lines=1)
    copy_and_status(ctx, ids, present=False)


def screen_s5(ctx):
    ids = {k: "S5-01" for k in ("wordmark", "newbill", "h-people", "p0f", "p0r", "p1f", "p1r", "p2f", "p2r", "add-person", "grid", "mode", "even", "by-item")}
    ids.update({"h-items": "S5-10", "sep": "S5-11", "add-item": "S5-05", "h-charges": "S5-05", "label-svc": "S5-05", "input-svc": "S5-05", "label-sst": "S5-05",
                "input-sst": "S5-05", "hint": "S5-05", "frame": "S5-12", "h-summary": "S5-06", "row1": "S5-06", "row2": "S5-06", "row3": "S5-06", "total": "S5-06",
                "h-shares": "S5-07"})
    for k in (1, 2, 4):
        for part in "nprt":
            ids[f"i{k}{part}"] = "S5-02"
    for part in "npr":
        ids[f"i3{part}"] = "S5-03"
    ids["i3t"] = "S5-04"
    header(ctx, ids)
    people(ctx, ids, PEOPLE3, False)
    mode(ctx, ids, "item")
    items(ctx, ids, ITEMS_S5)
    charges(ctx, ids)
    a = tape_frame(ctx, ids)
    summary(ctx, ids, SUM_S1, "RM 69.26")
    shares_heading(ctx, ids)
    msg_row(ctx, "S5-08", "1 item still needs a person. Tap who had it to see the shares.", lines=2)
    for sel in ("table.shares", "button.copy", "p.status"):
        ck_count(ctx, "S5-09", sel, 0, label=sel, dom=True)
    ck_count(ctx, "S5-04", "p.error", 0, label="p.error elements", dom=True)
    ck_count(ctx, "S5-04", "[aria-invalid]", 0, label="aria-invalid attributes", dom=True)
    msg = ctx.app.one("p.result-msg")
    if a:
        pb = float(a["cs"]["padding-bottom"][:-2])
        bb = float(a["cs"]["border-bottom-width"][:-2])
        end = msg["rect"][1] + msg["rect"][3]
        note(ctx, "S5-12", abs((a["rect"][1] + a["rect"][3]) - (end + pb + bb)) < 0.6 and pb == 24.0,
             f"panel ends {a['rect'][1] + a['rect'][3]:g}, message ends {end:g}, padding-bottom {pb:g}, bottom border {bb:g} (the card ends 24 px under the message)")


def screen_m1(ctx):
    """New bill dialog over S2, opened by a real mouse click."""
    vw, vh = ctx.vw, ctx.app.page.viewport_size["height"]
    dlg = "dialog.dialog"
    ck(ctx, "M1-03", dlg, label="dialog box",
       exp={"w": min(400, vw - 32), "cx": vw / 2, "cy": vh / 2, "pad": "24px 24px 24px 24px", "bg": SURFACE, "b4": f"1px solid {INK}", "rad": "6px", "bsh": "none", "color": INK},
       ignore=NATIVE_MODAL)
    ck(ctx, "M1-04", "h2.dialog-title#dialog-title", exp={"text": "Start a new bill?", "fs": "18px", "lh": "24px", "fw": "700", "tag": "h2"}, ignore=("user-select",))
    d_ = ctx.app.one(dlg)
    nm = ctx.app.js("() => { const d = document.querySelector('dialog'); return { modal: d.matches(':modal'), open: d.open }; }")
    note(ctx, "M1-04", d_["attrs"].get("aria-labelledby") == "dialog-title" and d_["attrs"].get("aria-describedby") == "dialog-text" and nm["modal"] and nm["open"],
         f"dialog aria-labelledby={d_['attrs'].get('aria-labelledby')}, aria-describedby={d_['attrs'].get('aria-describedby')}, open={nm['open']}, :modal={nm['modal']} (showModal)")
    ttl = ctx.app.one("h2.dialog-title")
    ck(ctx, "M1-05", "p.dialog-text#dialog-text", exp={"text": "This clears the people, items and amounts.", "fs": "16px", "lh": "24px", "color": MUTED, "mt": "8px",
                                                       "y": ttl["rect"][1] + ttl["rect"][3] + 8}, ignore=("user-select",))
    ck(ctx, "M1-06", f"{dlg} .dialog-actions .btn:nth-child(1)", label="Start new bill",
       exp={"cls": "btn btn-primary btn-large", "text": "Start new bill", "bg": INK, "color": ON, "h": 48, "fs": "16px", "lh": "24px", "fw": "600"}, ignore=("user-select",))
    ck(ctx, "M1-07", f"{dlg} .dialog-actions .btn:nth-child(2)", label="Cancel",
       exp={"cls": "btn btn-outline btn-large", "text": "Cancel", "bg": FIELD, "b4": f"1px solid {LINES}", "color": INK, "h": 48, "fs": "16px", "fw": "600",
            "focused": True, "focusVisible": False, "ols": "none"}, ignore=("user-select",))
    act = ctx.app.one(f"{dlg} .dialog-actions")
    body = ctx.app.one("p.dialog-text")
    s, c = ctx.app.one(f"{dlg} .dialog-actions .btn", 0), ctx.app.one(f"{dlg} .dialog-actions .btn", 1)
    ck(ctx, "M1-08", f"{dlg} .dialog-actions", label="actions", exp={"disp": "flex", "gap": "8px", "mt": "24px", "y": body["rect"][1] + body["rect"][3] + 24}, ignore=("user-select",))
    if vw < 600:
        note(ctx, "M1-06", abs(s["rect"][2] - act["rect"][2]) < 0.6, f"Start new bill full width: {s['rect'][2]:g} of {act['rect'][2]:g}")
        gap = c["rect"][1] - (s["rect"][1] + s["rect"][3])
        note(ctx, "M1-08", abs(gap - 8) < 0.6 and act["cs"]["flex-direction"] == "column" and s["rect"][1] < c["rect"][1],
             f"stacked ({act['cs']['flex-direction']}), Start new bill above Cancel, {gap:g} px apart")
    else:
        note(ctx, "M1-06", s["rect"][2] < act["rect"][2] - 40 and abs(c["rect"][0] + c["rect"][2] - (act["rect"][0] + act["rect"][2])) < 0.6 and s["rect"][0] < c["rect"][0]
             and act["cs"]["flex-direction"] == "row",
             f"natural width {s['rect'][2]:g} of {act['rect'][2]:g}, right aligned row (Cancel right edge {c['rect'][0] + c['rect'][2]:g}, actions right {act['rect'][0] + act['rect'][2]:g}), Start new bill first")
        gap = c["rect"][0] - (s["rect"][0] + s["rect"][2])
        note(ctx, "M1-08", abs(gap - 8) < 0.6, f"buttons {gap:g} px apart in a row")
    sc = ctx.app.page.evaluate("() => { const cs = getComputedStyle(document.querySelector('dialog'), '::backdrop'); return { bg: cs.backgroundColor, pos: cs.position, top: cs.top, left: cs.left, right: cs.right, bottom: cs.bottom }; }")
    gsc = ctx.gold.page.evaluate("() => { const e = document.querySelector('.backdrop'); const cs = getComputedStyle(e); const r = e.getBoundingClientRect(); return { bg: cs.backgroundColor, pos: cs.position, w: r.width, h: r.height }; }")
    note(ctx, "M1-02", sc["bg"] == C.SCRIM and gsc["bg"] == C.SCRIM and sc["pos"] == "fixed" and gsc["pos"] == "fixed",
         f"app ::backdrop {sc['bg']} {sc['pos']} inset {sc['top']}/{sc['left']}/{sc['right']}/{sc['bottom']}, golden .backdrop {gsc['bg']} {gsc['pos']} {gsc['w']:g}x{gsc['h']:g}")
    app_ = ctx.app.one(".app")
    note(ctx, "M1-01", abs(app_["rect"][3] - vh) < 0.6 and app_["cs"]["overflow"] == "hidden" and app_["cs"]["position"] == "relative",
         f".app height {app_['rect'][3]:g} of viewport {vh}, overflow {app_['cs']['overflow']}, position {app_['cs']['position']}")
    ctx.app.page.mouse.move(vw / 2, 5)
    ctx.app.page.mouse.wheel(0, 700)
    ctx.app.page.wait_for_timeout(120)
    sy = ctx.app.page.evaluate("window.scrollY")
    hit = ctx.app.page.evaluate("() => { const b = document.querySelector('header .btn').getBoundingClientRect(); const e = document.elementFromPoint(b.x + 4, b.y + 4); return e.tagName.toLowerCase() + '.' + e.className; }")
    note(ctx, "M1-01", sy == 0 and hit.startswith("dialog"), f"mouse wheel leaves scrollY at {sy}; a hit on the header button lands on {hit} (page behind inert)")
    gh = ctx.gold.page.evaluate("() => { const a = document.querySelector('.app'); return { h: a.getBoundingClientRect().height, inert: a.hasAttribute('inert'), ov: getComputedStyle(a).overflow }; }")
    note(ctx, "M1-01", abs(gh["h"] - app_["rect"][3]) < 0.6 and gh["ov"] == app_["cs"]["overflow"], f"golden .app height {gh['h']:g}, overflow {gh['ov']}, inert {gh['inert']}")


def run():
    qa = parse_qa_rows(C.ROOT / "docs" / "modules" / "split-app" / "qa.md")
    R = Rows()
    server = C.rig.StaticServer(C.ROOT, say=print)
    errors = []
    try:
        server.start()
        with sync_playwright() as pw:
            browser = C.launch(pw)
            for vp in ((390, 844), (1280, 800)):
                for screen, fn in (("bill-items", screen_s1), ("bill-even", screen_s2), ("bill-empty", screen_s3), ("bill-unassigned", screen_s5), ("new-bill-dialog", screen_m1)):
                    golden, seed = C.SCREENS[screen]
                    gctx, actx = C.gold_ctx(browser, vp), C.app_ctx(browser, server.base, vp, seed=seed)
                    g, a = C.open_golden(gctx, golden), C.open_app(actx, server.base)
                    if screen == "new-bill-dialog":
                        C.new_bill_by_mouse(a)
                    fn(Ctx(R, a, g, vp[0], screen))
                    errors += [(screen, vp, m) for m in a.console]
                    gctx.close()
                    actx.close()
            vp = (360, 780)
            gctx, actx = C.gold_ctx(browser, vp), C.app_ctx(browser, server.base, vp, seed=C.seeds.S2)
            g, a = C.open_golden(gctx, "bill-even"), C.open_app(actx, server.base)
            ctx = Ctx(R, a, g, 360, "bill-even")
            ck(ctx, "S2-28", f"{SUB} .cells .field.money", label="Subtotal field at 360", exp={"w": 160, "h": 44, "cls": "field money"})
            sw = a.js("() => [document.documentElement.scrollWidth, window.innerWidth]")
            note(ctx, "S2-28", sw[0] <= sw[1], f"scrollWidth {sw[0]} <= innerWidth {sw[1]}")
            gctx.close()
            actx.close()
            gctx, actx = C.gold_ctx(browser, vp), C.app_ctx(browser, server.base, vp, seed=C.seeds.S2)
            g, a = C.open_golden(gctx, "new-bill-dialog"), C.open_app(actx, server.base)
            C.new_bill_by_mouse(a)
            ctx = Ctx(R, a, g, 360, "new-bill-dialog")
            ck(ctx, "M1-09", "dialog.dialog", label="dialog at 360", exp={"w": 328, "cx": 180, "cy": 390}, ignore=NATIVE_MODAL)
            ck(ctx, "M1-09", "p.dialog-text", label="body at 360", exp={"h": 48, "text": "This clears the people, items and amounts."}, ignore=("user-select",))
            sw = a.js("() => [document.documentElement.scrollWidth, window.innerWidth]")
            note(ctx, "M1-09", sw[0] <= sw[1], f"scrollWidth {sw[0]} <= innerWidth {sw[1]} with the dialog open")
            errors += [("360", m) for m in a.console]
            gctx.close()
            actx.close()
            browser.close()
    finally:
        server.stop()
    out = {"qa": {k: list(v) for k, v in qa.items()},
           "rows": {rid: {str(vw): [[ok, t] for ok, t in v] for vw, v in sorted(by.items())} for rid, by in sorted(R.d.items())}, "console_errors": errors}
    C.dump("rows_screens.json", out)
    fails = [rid for rid, by in R.d.items() if any(not ok for v in by.values() for ok, _ in v)]
    print(f"rows with results: {len(R.d)}, rows failing: {len(fails)} {sorted(fails)}")
    print("console errors:", errors)


if __name__ == "__main__":
    run()
