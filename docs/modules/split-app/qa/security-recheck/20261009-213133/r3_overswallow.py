"""Re-check item 3: can the moved guard (swallowRepeatClicks, src/ui/dom.js) swallow a deliberate action, or stay armed?

A  mouse: a deliberate click on a DIFFERENT control right after a Remove (Add person, another Remove, Add item).
B  touch: the same by tap 60 ms later (Chromium assigns the tap count, so `detail` is a measurement), and the same spot at 60 and 450 ms.
C  keyboard: Enter and Space on Remove repeated quickly (Remove, Tab, Remove), a held Enter and a held Space on five kinds of Remove.
D  right and middle button around a Remove. (First run: the middle row failed because Chromium starts autoscroll on a middle press and
   uses the next left click to end it, so that click never reaches the page, see r3b_followups.py section M. The row now ends the
   autoscroll with a click on a heading, which is a harness step and not a user action on a control.)
E  a Remove click right after the guard was armed by a dialog close (mouse and touch).
F  guard lifetime on paths the solver did not run: Remove then typing then a real double click on a name field, accumulation, no timer,
   a press on a disabled Remove, Esc after opening the dialog then an immediate second tap on New bill.
Rows with pass=None are measurements without a pass line (the design decides). Mouse clicks carry click count 1 here because a click on
another control is a new click series; a touch tap gets Chromium's own count.
"""
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rc  # noqa: E402
from rc import seeds, btn  # noqa: E402

VPS = [(360, 640), (390, 844), (1280, 800)]
FIVE = seeds.changed(seeds.S2, lambda d: d["bill"].update(people=[{"id": f"p{n}", "name": f"P{n}"} for n in range(1, 6)], nextId=6))
ONE_ITEM = seeds.changed(seeds.S1, lambda d: d["bill"].update(items=d["bill"]["items"][:1]))

LIGHT = """() => {
  const a = document.activeElement;
  return { p: document.querySelectorAll('li.person').length, i: document.querySelectorAll('li.item').length,
           f: a ? (a.getAttribute('aria-label') || a.textContent.trim().slice(0, 24) || a.tagName.toLowerCase()) : null };
}"""


def ids(page):
    b = rc.bill(page)
    return {"people": [p["id"] for p in b["people"]], "items": [i["id"] for i in b["items"]], "nextId": b["nextId"],
            "blank_people": [p["id"] for p in b["people"] if p["name"] == ""], "blank_items": [i["id"] for i in b["items"] if i["name"] == "" and i["priceText"] == ""]}


def start(browser, base, seed, vp, touch=False):
    ctx, page, cap = rc.open_page(browser, base, seed=seed, viewport=vp, touch=touch)
    rc.settle(page)
    return ctx, page, cap


def dist(a, b):
    return round(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5)


def reached(events):
    return bool(events) and all(e.endswith(":reached") for e in events)


def body(browser, server, results):
    base = server.base

    def record(section, case, passed, **fields):
        row = {"section": section, "case": case, "pass": passed, **fields}
        results["cases"].append(row)
        tag = "INFO" if passed is None else ("PASS" if passed else "FAIL")
        print(f"{tag} [{section}] {case} {fields}")
        return row

    # ---------------------------------------------------------------- A mouse, a different control right after Remove
    for vp in VPS:
        ctx, page, cap = start(browser, base, FIVE, vp)
        try:
            rx, ry = rc.centre(btn(page, "Remove P2"))
            rc.reset_log(page)
            t0 = time.perf_counter()
            page.mouse.click(rx, ry)
            ax, ay = rc.centre(btn(page, "Add person"))
            page.mouse.click(ax, ay)
            gap = round((time.perf_counter() - t0) * 1000)
            rc.settle(page, 150)
            s = ids(page)
            record("A", f"Remove P2 then Add person at once, {vp[0]}x{vp[1]}",
                   s["people"] == ["p1", "p3", "p4", "p5", "p6"] and s["nextId"] == 7 and not cap.problems(base),
                   people=s["people"], nextId=s["nextId"], gap_ms=gap, distance_px=dist((rx, ry), (ax, ay)), clicks=rc.clicks(page, ("click",)))
        finally:
            ctx.close()
    ctx, page, cap = start(browser, base, FIVE, VPS[1])
    try:
        rx, ry = rc.centre(btn(page, "Remove P2"))
        rc.reset_log(page)
        page.mouse.click(rx, ry)
        qx, qy = rc.centre(btn(page, "Remove P4"))
        page.mouse.click(qx, qy)
        rc.settle(page, 150)
        s = ids(page)
        record("A", "Remove P2 then Remove P4 at once, 390x844", s["people"] == ["p1", "p3", "p5"] and not cap.problems(base),
               people=s["people"], distance_px=dist((rx, ry), (qx, qy)), clicks=rc.clicks(page, ("click",)))
    finally:
        ctx.close()
    ctx, page, cap = start(browser, base, seeds.S1, VPS[1])
    try:
        rx, ry = rc.centre(btn(page, "Remove Char kuey teow"))
        rc.reset_log(page)
        page.mouse.click(rx, ry)
        ax, ay = rc.centre(btn(page, "Add item"))
        page.mouse.click(ax, ay)
        rc.settle(page, 150)
        s = ids(page)
        record("A", "Remove item 2 then Add item at once, 390x844", s["items"] == ["i4", "i6", "i7", "i8"] and not cap.problems(base),
               items=s["items"], nextId=s["nextId"], distance_px=dist((rx, ry), (ax, ay)), clicks=rc.clicks(page, ("click",)))
    finally:
        ctx.close()

    # ---------------------------------------------------------------- B touch
    for vp in VPS[:2]:
        ctx, page, cap = start(browser, base, FIVE, vp, touch=True)
        try:
            rx, ry = rc.centre(btn(page, "Remove P2"))
            rc.reset_log(page)
            page.touchscreen.tap(rx, ry)
            page.wait_for_timeout(60)
            ax, ay = rc.centre(btn(page, "Add person"))
            page.touchscreen.tap(ax, ay)
            rc.settle(page, 150)
            s = ids(page)
            record("B", f"tap Remove P2, 60 ms, tap Add person, {vp[0]}x{vp[1]}",
                   s["people"] == ["p1", "p3", "p4", "p5", "p6"] and not cap.problems(base),
                   people=s["people"], distance_px=dist((rx, ry), (ax, ay)), clicks=rc.clicks(page, ("mousedown", "click")))
        finally:
            ctx.close()
    for delay in (450, 60):
        ctx, page, cap = start(browser, base, FIVE, VPS[1], touch=True)
        try:
            rx, ry = rc.centre(btn(page, "Remove P2"))
            rc.reset_log(page)
            page.touchscreen.tap(rx, ry)
            page.wait_for_timeout(delay)
            page.touchscreen.tap(rx, ry)  # the same spot: now the Remove of the row that moved up
            rc.settle(page, 150)
            s = ids(page)
            if delay == 450:
                record("B", "tap Remove P2, 450 ms, tap the same spot (next row's Remove), 390x844", s["people"] == ["p1", "p4", "p5"] and not cap.problems(base),
                       people=s["people"], clicks=rc.clicks(page, ("mousedown", "click")))
            else:
                record("B", "tap Remove P2, 60 ms, tap the same spot (design: held back as a double tap), 390x844", None,
                       people=s["people"], held_back=s["people"] == ["p1", "p3", "p4", "p5"], clicks=rc.clicks(page, ("mousedown", "click")))
        finally:
            ctx.close()

    # ---------------------------------------------------------------- C keyboard
    for key in ("Enter", "Space"):
        ctx, page, cap = start(browser, base, FIVE, VPS[1])
        try:
            btn(page, "Remove P2").focus()
            page.keyboard.press(key)
            f1 = page.evaluate(LIGHT)["f"]
            page.keyboard.press("Tab")
            f2 = page.evaluate(LIGHT)["f"]
            page.keyboard.press(key)
            rc.settle(page, 100)
            s = ids(page)
            record("C", f"{key} on Remove P2, Tab, {key} on the next Remove, no pause", s["people"] == ["p1", "p4", "p5"] and not cap.problems(base),
                   people=s["people"], focus_after_first=f1, focus_after_tab=f2, focus_end=page.evaluate(LIGHT)["f"])
        finally:
            ctx.close()
    held_cases = [
        ("held Enter on Remove of a middle person (P2 of 5)", FIVE, "Remove P2", "Enter", lambda s: s["people"] == ["p1", "p3", "p4", "p5"] and s["nextId"] == 6),
        ("held Enter on Remove of the last person (P5 of 5)", FIVE, "Remove P5", "Enter", lambda s: s["people"] == ["p1", "p2", "p3", "p4"] and s["nextId"] == 6),
        ("held Enter on Remove of a middle item (item 2 of 4)", seeds.S1, "Remove Char kuey teow", "Enter", lambda s: s["items"] == ["i4", "i6", "i7"] and s["nextId"] == 8),
        ("held Enter on Remove of the last item (item 4 of 4)", seeds.S1, "Remove Satay, 10 sticks", "Enter", lambda s: s["items"] == ["i4", "i5", "i6"] and s["nextId"] == 8),
        ("held Enter on Remove of the ONLY item", ONE_ITEM, "Remove Nasi lemak ayam", "Enter", lambda s: s["items"] == [] and s["nextId"] == 8),
        ("held Space on Remove of the ONLY item", ONE_ITEM, "Remove Nasi lemak ayam", "Space", lambda s: s["items"] == [] and s["nextId"] == 8),
    ]
    for label, seed, remove, key, check in held_cases:
        ctx, page, cap = start(browser, base, seed, VPS[1])
        try:
            btn(page, remove).focus()
            trail = []
            rc.reset_log(page)
            for _ in range(8):  # key repeat: keydown again and again with the key still down
                page.keyboard.down(key)
                page.wait_for_timeout(40)
                f = page.evaluate(LIGHT)
                trail.append(f"p{f['p']}/i{f['i']}/{f['f']}")
            page.keyboard.up(key)
            rc.settle(page, 120)
            s = ids(page)
            record("C", label + ", 8 key repeats over ~320 ms", check(s) and not cap.problems(base),
                   people=s["people"], items=s["items"], nextId=s["nextId"], blank_items=s["blank_items"], trail=trail, clicks=rc.clicks(page, ("click",)))
        finally:
            ctx.close()

    # ---------------------------------------------------------------- D right and middle button
    for button in ("right", "middle"):
        ctx, page, cap = start(browser, base, FIVE, VPS[1])
        try:
            hx, hy = rc.centre(page.locator("h2#h-people"))

            def end_autoscroll():
                if button == "middle":
                    page.mouse.click(hx, hy)  # eaten by the browser when a middle press started autoscroll (r3b section M)

            rx, ry = rc.centre(btn(page, "Remove P2"))
            page.mouse.click(rx, ry, button=button)
            rc.settle(page, 60)
            end_autoscroll()
            after_special = ids(page)["people"]
            page.mouse.click(rx, ry)  # a left click: removes, arms the guard
            ax, ay = rc.centre(btn(page, "Add person"))
            rc.reset_log(page)
            page.mouse.click(ax, ay, button=button)
            rc.settle(page, 60)
            end_autoscroll()
            after_special_2 = ids(page)["people"]
            page.mouse.click(ax, ay)  # a left click on Add person must still work
            rc.settle(page, 120)
            s = ids(page)
            record("D", f"{button} click on Remove (nothing), left Remove, {button} click on Add person (nothing), left Add person (works)",
                   after_special == ["p1", "p2", "p3", "p4", "p5"] and after_special_2 == ["p1", "p3", "p4", "p5"] and s["people"] == ["p1", "p3", "p4", "p5", "p6"] and not cap.problems(base),
                   after_special=after_special, after_special_2=after_special_2, final=s["people"], clicks=rc.clicks(page, ("click",)))
        finally:
            ctx.close()

    # ---------------------------------------------------------------- E Remove right after a dialog close armed the guard
    ctx, page, cap = start(browser, base, FIVE, VPS[1])
    try:
        btn(page, "New bill").click()
        rc.settle(page, 80)
        btn(page, "Cancel").click()
        rx, ry = rc.centre(btn(page, "Remove P2"))
        rc.reset_log(page)
        page.mouse.click(rx, ry)
        rc.settle(page, 120)
        s = ids(page)
        record("E", "mouse: New bill, Cancel, then Remove P2 at once, 390x844", s["people"] == ["p1", "p3", "p4", "p5"] and not cap.problems(base),
               people=s["people"], clicks=rc.clicks(page, ("mousedown", "click")))
    finally:
        ctx.close()
    ctx, page, cap = start(browser, base, FIVE, VPS[1], touch=True)
    try:
        page.touchscreen.tap(*rc.centre(btn(page, "New bill")))
        rc.settle(page, 80)
        cx, cy = rc.centre(btn(page, "Cancel"))
        page.touchscreen.tap(cx, cy)
        page.wait_for_timeout(60)
        rx, ry = rc.centre(btn(page, "Remove P2"))
        rc.reset_log(page)
        page.touchscreen.tap(rx, ry)
        rc.settle(page, 120)
        s = ids(page)
        d = dist((cx, cy), (rx, ry))
        record("E", "touch: tap New bill, tap Cancel, 60 ms, tap Remove P2, 390x844", s["people"] == ["p1", "p3", "p4", "p5"] and not cap.problems(base),
               people=s["people"], cancel_to_remove_px=d, clicks=rc.clicks(page, ("mousedown", "click")))
    finally:
        ctx.close()

    # ---------------------------------------------------------------- F guard lifetime
    ctx, page, cap = start(browser, base, FIVE, VPS[1])
    try:
        rx, ry = rc.centre(btn(page, "Remove P2"))
        page.mouse.click(rx, ry)  # single click: arms; the app puts focus in the name field of the row now at index 1
        page.keyboard.type("Zed")  # typing, no mouse press: nothing can disarm the guard
        typed = page.evaluate("() => [...document.querySelectorAll('li.person input')].map((i) => i.value)")
        tx, ty = rc.centre(page.get_by_label("Person 3 name", exact=True))
        rc.reset_log(page)
        page.mouse.dblclick(tx, ty)  # a real double click on a name field selects the word
        rc.settle(page, 80)
        sel = page.evaluate("() => { const a = document.activeElement; return { label: a.getAttribute('aria-label'), value: a.value, start: a.selectionStart, end: a.selectionEnd }; }")
        ev = rc.clicks(page, ("mousedown", "click"))
        record("F", "Remove (single), type 'Zed', then a real double click on a name field selects the word, 390x844",
               sel["start"] == 0 and sel["end"] == len(sel["value"]) and reached(ev) and not cap.problems(base),
               typed=typed, selection=sel, events=ev)
    finally:
        ctx.close()
    ctx, page, cap = start(browser, base, FIVE, VPS[1])
    try:
        rx, ry = rc.centre(btn(page, "Remove P2"))
        page.mouse.click(rx, ry)
        page.keyboard.type("Zed")
        hx, hy = rc.centre(page.locator("h2#h-people"))
        rc.reset_log(page)
        rc.press(page, hx, hy, 2)  # a lone press with count 2: held back while the guard is armed
        first = rc.clicks(page, ("mousedown", "click"))
        rc.reset_log(page)
        rc.press(page, hx, hy, 1)  # a count-1 press: always passes and disarms
        second = rc.clicks(page, ("mousedown", "click"))
        rc.reset_log(page)
        rc.press(page, hx, hy, 2)  # now a count-2 press passes
        third = rc.clicks(page, ("mousedown", "click"))
        record("F", "state probe after Remove + typing: lone count-2 press, then count 1, then count 2 (390x844)",
               reached(second) and reached(third),
               count2_while_armed=first, then_count1=second, then_count2=third,
               note="the first list says whether the guard is still armed after typing (a repeat press with no first press is not a real gesture)")
    finally:
        ctx.close()
    ctx, page, cap = start(browser, base, FIVE, VPS[1])
    try:
        for name in ("Remove P2", "Remove P3", "Remove P4"):  # three separate single clicks, 600 ms apart
            x, y = rc.centre(btn(page, name))
            page.mouse.click(x, y)
            page.wait_for_timeout(600)
        hx, hy = rc.centre(page.locator("h2#h-people"))
        rc.reset_log(page)
        rc.press(page, hx, hy, 1)
        rc.press(page, hx, hy, 2)
        ev = rc.clicks(page, ("mousedown", "click"))
        record("F", "three separate Remove clicks, then count 1 and count 2 on a heading: nothing is left armed (accumulation), 390x844",
               reached(ev) and ids(page)["people"] == ["p1", "p5"], events=ev, people=ids(page)["people"])
    finally:
        ctx.close()
    ctx, page, cap = start(browser, base, FIVE, VPS[1])
    try:
        rx, ry = rc.centre(btn(page, "Remove P2"))
        page.mouse.click(rx, ry)
        page.wait_for_timeout(3000)
        ax, ay = rc.centre(btn(page, "Add person"))
        rc.reset_log(page)
        rc.press(page, ax, ay, 2)
        late2 = rc.clicks(page, ("mousedown", "click"))
        rc.reset_log(page)
        rc.press(page, ax, ay, 1)
        late1 = rc.clicks(page, ("mousedown", "click"))
        record("F", "Remove, 3 s, a press with count 2 on Add person (no timer: held back), then count 1 (delivered), 390x844", None,
               count2_after_3s=late2, count1_after=late1, people=ids(page)["people"])
    finally:
        ctx.close()
    ctx, page, cap = start(browser, base, seeds.S2, VPS[1])
    try:
        rx, ry = rc.centre(btn(page, "Remove Chen"))
        page.mouse.click(rx, ry)  # 3 -> 2 people: both Remove buttons are disabled now
        disabled = page.evaluate("() => [...document.querySelectorAll('li.person .icon-btn')].map((b) => b.disabled)")
        bx, by = rc.centre(btn(page, "Remove Ben"))
        rc.reset_log(page)
        rc.press(page, bx, by, 1)  # a press on a disabled button
        on_disabled = rc.clicks(page, ("mousedown", "click"))
        hx, hy = rc.centre(page.locator("h2#h-people"))
        rc.reset_log(page)
        rc.press(page, hx, hy, 2)
        after = rc.clicks(page, ("mousedown", "click"))
        record("F", "Remove Chen (3 to 2 people, Removes now disabled), count-1 press on a disabled Remove, then a count-2 press on a heading", None,
               disabled=disabled, press_on_disabled_reached_document=on_disabled, count2_after=after)
    finally:
        ctx.close()
    ctx, page, cap = start(browser, base, seeds.S2, VPS[1], touch=True)
    try:
        nx, ny = rc.centre(btn(page, "New bill"))
        page.touchscreen.tap(nx, ny)
        rc.settle(page, 60)
        page.keyboard.press("Escape")
        page.wait_for_timeout(30)
        rc.reset_log(page)
        page.touchscreen.tap(nx, ny)
        rc.settle(page, 120)
        record("F", "touch: tap New bill, Esc, tap New bill again ~100 ms after the first tap (390x844)", None,
               dialog_open=rc.dialog_open(page), clicks=rc.clicks(page, ("mousedown", "click")),
               note="reachable only with a keyboard next to a touch screen, or a mouse user who presses Esc and clicks the same spot inside the double-click time")
    finally:
        ctx.close()

    scored = [r for r in results["cases"] if r["pass"] is not None]
    print(f"\nSCORED rows {len(scored)}: pass {sum(1 for r in scored if r['pass'])}, fail {sum(1 for r in scored if not r['pass'])}; measurement rows {len(results['cases']) - len(scored)}")


if __name__ == "__main__":
    rc.run_probe("r3-overswallow", body)
