"""Audit item 3: can swallowRepeatClicks (src/ui/dialog.js) swallow a deliberate action?

T1 keyboard: Enter and Space on New bill, Cancel and Start new bill, and a held Enter (auto-repeat).
T2 right and middle button on the backdrop and on Cancel, then a left click still works.
T3 presses that start and end in different places (WR-06 and its mirror images).
T4 a deliberate press right after the dialog closed: click count 1 passes, a lone press carrying count 2 or 3 is swallowed.
T5 touch: second tap on a different control at a distance and a delay after a tap that closed the dialog.
   Chromium's gesture code assigns the tap count, so the detail of the second tap is a measurement.
T6 the guard's lifetime after a keyboard close and after Esc.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import seeds  # noqa: E402


def events(page, kinds=("mousedown", "click")):
    return [f"{e['type']}:{e['detail']}:{e['target']}:{'reached' if e['reached'] else 'SWALLOWED'}"
            for e in page.evaluate("() => window.evlog") if e["type"] in kinds]


def reset(page):
    page.evaluate("() => { window.evlog = []; }")


def record(results, case, **fields):
    row = {"case": case, **fields}
    results["cases"].append(row)
    print(case, {k: v for k, v in fields.items() if k != "events"})
    if "events" in fields and fields["events"]:
        for line in fields["events"]:
            print("     ", line)


def btn(page, name):
    return page.get_by_role("button", name=name, exact=True)


def dialog_open(page):
    return page.evaluate("() => document.querySelector('dialog').open")


def focus_label(page):
    return common.snap(page)["focus"]


def open_dialog(page):
    btn(page, "New bill").click()
    common.settle(page, 80)


def t1_keyboard(browser, base, results):
    ctx, page, cap = common.open_page(browser, base, seed=seeds.S1, viewport=(390, 844))
    try:
        common.settle(page)
        for key in ("Enter", "Space"):
            btn(page, "New bill").focus()
            page.keyboard.press(key)
            common.settle(page, 50)
            opened = dialog_open(page)
            on_cancel = focus_label(page)
            page.keyboard.press(key)  # Cancel
            common.settle(page, 50)
            closed = not dialog_open(page)
            back_on = focus_label(page)
            page.keyboard.press(key)  # New bill again, straight after a keyboard close
            common.settle(page, 50)
            reopened = dialog_open(page)
            page.keyboard.press("Escape")
            common.settle(page, 50)
            record(results, f"T1 {key}: open, close with Cancel, reopen", opened=opened, focus_on_open=on_cancel, closed=closed,
                   focus_after_close=back_on, reopened_at_once=reopened, draft_unchanged=common.snap(page)["draft"] == seeds.S1)
        # Start new bill by keyboard, then reopen at once.
        btn(page, "New bill").focus()
        page.keyboard.press("Enter")
        page.keyboard.press("Tab")  # Cancel -> Start new bill
        on_start = focus_label(page)
        page.keyboard.press("Enter")
        common.settle(page, 50)
        after_start = common.snap(page)
        page.keyboard.press("Enter")  # focus is on New bill
        common.settle(page, 50)
        record(results, "T1 Enter on Start new bill, then Enter on New bill", focus_before=on_start,
               bill_reset=after_start["draft"] is not None and '"subtotalText":""' in after_start["draft"] and after_start["people"] == ["Person 1", "Person 2"],
               reopened_at_once=dialog_open(page), focus_now=focus_label(page))
        page.keyboard.press("Escape")
    finally:
        ctx.close()
    # Held Enter: auto-repeat keydowns walk Cancel -> New bill -> Cancel ... Start is never reached (focus opens on Cancel).
    ctx, page, cap = common.open_page(browser, base, seed=seeds.S1, viewport=(390, 844))
    try:
        common.settle(page)
        btn(page, "New bill").focus()
        trail = []
        for _ in range(12):
            page.keyboard.down("Enter")
            page.wait_for_timeout(40)
            trail.append((dialog_open(page), focus_label(page)))
        page.keyboard.up("Enter")
        common.settle(page, 100)
        record(results, "T1 held Enter x12 on New bill (auto-repeat)", trail=[f"{'open' if o else 'closed'}/{f}" for o, f in trail],
               draft_unchanged=common.snap(page)["draft"] == seeds.S1, problems=cap.problems(base))
    finally:
        ctx.close()


def t2_buttons(browser, base, results):
    ctx, page, cap = common.open_page(browser, base, seed=seeds.S1, viewport=(390, 844))
    try:
        common.settle(page)
        open_dialog(page)
        cx, cy = common.centre(btn(page, "Cancel"))
        for button in ("right", "middle"):
            page.mouse.click(cx, cy, button=button)
            common.settle(page, 50)
            on_cancel = (dialog_open(page), common.snap(page)["draft"] == seeds.S1)
            page.mouse.click(10, 10, button=button)
            common.settle(page, 50)
            on_backdrop = (dialog_open(page), common.snap(page)["draft"] == seeds.S1)
            record(results, f"T2 {button} click on Cancel and on the backdrop", on_cancel_open_and_draft_same=on_cancel,
                   on_backdrop_open_and_draft_same=on_backdrop)
        # stale "press began on the backdrop" flag: right press on the backdrop, then a left click on the dialog's own padding
        box = page.locator("dialog").bounding_box()
        page.mouse.move(10, 10)
        page.mouse.down(button="right")
        page.mouse.up(button="right")
        page.mouse.click(box["x"] + 3, box["y"] + 3)  # inside the box, on the dialog element itself
        common.settle(page, 50)
        record(results, "T2 right press on backdrop then a left click on the dialog padding", dialog_still_open=dialog_open(page))
        btn(page, "Cancel").click()
        common.settle(page, 50)
        record(results, "T2 a left click on Cancel afterwards still closes", closed=not dialog_open(page), focus=focus_label(page))
    finally:
        ctx.close()


def t3_presses(browser, base, results):
    ctx, page, cap = common.open_page(browser, base, seed=seeds.S1, viewport=(390, 844))
    try:
        common.settle(page)

        def drag(start, end):
            page.mouse.move(*start)
            page.mouse.down()
            page.mouse.move(*end, steps=5)
            page.mouse.up()
            common.settle(page, 60)

        open_dialog(page)
        box = page.locator("dialog").bounding_box()
        inside = (box["x"] + box["width"] / 2, box["y"] + 30)
        drag(inside, (10, 10))
        record(results, "T3 press in the dialog, release on the backdrop", dialog_open=dialog_open(page))
        drag((10, 10), inside)
        record(results, "T3 press on the backdrop, release in the dialog", dialog_open=dialog_open(page))
        cx, cy = common.centre(btn(page, "Cancel"))
        drag((cx, cy), (10, 10))
        record(results, "T3 press on Cancel, release on the backdrop", dialog_open=dialog_open(page), draft_same=common.snap(page)["draft"] == seeds.S1)
        drag((10, 10), (60, 90))
        record(results, "T3 press on the backdrop, release elsewhere on the backdrop", dialog_open=dialog_open(page), draft_same=common.snap(page)["draft"] == seeds.S1)
    finally:
        ctx.close()


def press(page, x, y, count):
    """One press and release that carries click count `count` (what the OS reports for a repeat), nothing before it."""
    page.mouse.move(x, y)
    page.mouse.down(click_count=count)
    page.mouse.up(click_count=count)


def t4_quick_clicks(browser, base, results):
    for count, pause in ((1, 0), (2, 0), (2, 3000), (3, 0)):
        ctx, page, cap = common.open_page(browser, base, seed=seeds.S2, viewport=(390, 844))
        try:
            common.settle(page)
            open_dialog(page)
            btn(page, "Cancel").click()
            page.wait_for_timeout(pause or 20)
            ax, ay = common.centre(btn(page, "Add person"))
            reset(page)
            press(page, ax, ay, count)
            common.settle(page, 100)
            record(results, f"T4 Cancel, {pause} ms, then one press with click count {count} on Add person (a different control)",
                   people_after=common.snap(page)["people"], events=events(page))
            reset(page)
            press(page, ax, ay, 1)
            common.settle(page, 100)
            record(results, "T4 ... and the next press with count 1 on the same spot", people_after=common.snap(page)["people"], events=events(page))
        finally:
            ctx.close()


def t5_touch(browser, base, results):
    for distance in (0, 8, 16, 24, 30, 80, 220):
        for delay in (60, 450):
            ctx, page, cap = common.open_page(browser, base, seed=seeds.S2, viewport=(390, 844), touch=True)
            try:
                common.settle(page)
                open_dialog(page)
                cx, cy = common.centre(btn(page, "Cancel"))
                reset(page)
                page.touchscreen.tap(cx, cy)
                page.wait_for_timeout(delay)
                page.touchscreen.tap(cx, cy - distance)
                common.settle(page, 100)
                evs = events(page)
                record(results, f"T5 tap Cancel, wait {delay} ms, tap {distance} px higher", second_press=(evs[2] if len(evs) > 2 else None),
                       second_click=(evs[3] if len(evs) > 3 else None), dialog_open=dialog_open(page))
            finally:
                ctx.close()


def toggle_state(page):
    return page.get_by_role("group", name="Who had Nasi lemak ayam").get_by_role("button", name="Ben", exact=True).get_attribute("aria-pressed")


def t6_lifetime(browser, base, results):
    for how in ("keyboard-close", "escape-close"):
        ctx, page, cap = common.open_page(browser, base, seed=seeds.S1, viewport=(390, 844))
        try:
            common.settle(page)
            btn(page, "New bill").focus()
            page.keyboard.press("Enter")
            if how == "keyboard-close":
                page.keyboard.press("Enter")  # Cancel is focused: a click with detail 0
            else:
                page.keyboard.press("Escape")
            common.settle(page, 60)
            tx, ty = common.centre(page.get_by_role("group", name="Who had Nasi lemak ayam").get_by_role("button", name="Ben", exact=True))
            reset(page)
            page.mouse.dblclick(tx, ty)
            common.settle(page, 100)
            record(results, f"T6 {how}, then a real double click on a toggle", toggle_after=toggle_state(page), expected="false (two flips)",
                   events=events(page))
        finally:
            ctx.close()


def body(browser, server, results):
    base = server.base
    for step in (t1_keyboard, t2_buttons, t3_presses, t4_quick_clicks, t5_touch, t6_lifetime):
        step(browser, base, results)


if __name__ == "__main__":
    common.run_probe("p7-swallow-scope", body)
