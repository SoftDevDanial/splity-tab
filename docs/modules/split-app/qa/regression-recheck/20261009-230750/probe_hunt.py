"""Regression re-check, split-app. Can the new arming on Add person and Add item swallow a deliberate action?

Usage: python probe_hunt.py   (serves the project root on a free loopback port, headless Chromium, stops both)
Writes hunt-results.json next to this script and prints one PASS or FAIL line per case.
Clipboard: rig.new_context only (recorder), no permissions, no bypass_csp (CG-7).

Cases
 K  keyboard: Enter and Space on Add person / Add item, repeated, then Tab + Enter on the new Remove (a key press has count 0)
 D  deliberate: Add by mouse, then a click of its own (count 1) on the new name field, on the new Remove, on another control
 W  word: Add (mouse and keyboard), type two words, double click a word, a word must be selected
 C  caps: a repeat press on the 12th person and on the 50th item
 S  stack: guards left over by keyboard Add / Remove, then one mouse press with count 1 clears them all
Windows Chromium selects the trailing space with a word ("Siti "), so a selection is compared after strip().
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[5]
assert (PROJECT / "index.html").is_file(), PROJECT
sys.path.insert(0, str(PROJECT / "tests" / "browser"))

import rig  # noqa: E402
import seeds  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

RESULTS = []
SELECTION_JS = "() => { const i = document.activeElement; return (i.value || '').slice(i.selectionStart, i.selectionEnd); }"
ACTIVE_JS = "() => document.activeElement.getAttribute('aria-label') || document.activeElement.textContent.trim() || document.activeElement.tagName"
SETTLE_JS = "() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))"


def people_bill(count):
    return seeds.changed(seeds.S2, lambda d: d["bill"].update(
        people=[{"id": f"p{n}", "name": f"P{n}"} for n in range(1, count + 1)], nextId=count + 1))


def items_bill(count):
    def edit(d):
        base = d["bill"]["items"][0]
        d["bill"]["items"] = [dict(base, id=f"i{n}", name=f"I{n}") for n in range(4, 4 + count)]
        d["bill"]["nextId"] = 4 + count
    return seeds.changed(seeds.S1, edit)


def fresh(browser, base, seed, size=(390, 844), touch=False):
    options = {"viewport": {"width": size[0], "height": size[1]}, "device_scale_factor": 1, "color_scheme": "light",
               "storage_state": rig.storage_state(base, seed)}
    if touch:
        options["has_touch"] = True
    context = rig.new_context(browser, **options)
    page = context.new_page()
    errors = []
    page.on("console", lambda m: errors.append(f"console {m.type}: {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(f"page error: {e}"))
    page.goto(base + "/")
    return context, page, errors


def stored(page):
    return json.loads(page.evaluate("localStorage.getItem('split.draft')"))["bill"]


def settle(page):
    page.evaluate(SETTLE_JS)


def record(case, ok, detail):
    RESULTS.append({"case": case, "ok": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + case + "   " + str(detail))


def press_point(button, place):
    button.scroll_into_view_if_needed()
    box = button.bounding_box()
    return box["x"] + (box["width"] - 22 if place == "right-edge" else box["width"] / 2), box["y"] + box["height"] / 2


def middle(box, dx=None):
    return (box["x"] + (box["width"] / 2 if dx is None else dx), box["y"] + box["height"] / 2)


# ----------------------------------------------------------------------------------------------- K: keyboard
def case_keyboard_people(browser, base):
    context, page, errors = fresh(browser, base, people_bill(3))
    try:
        add = page.get_by_role("button", name="Add person", exact=True)
        log = []
        for step in range(9):  # 3 -> 12
            if step % 2 == 0:
                add.focus()
                page.keyboard.press("Enter")
            else:  # the real path: from the new name, Tab to its Remove, Tab to Add person, Space
                page.keyboard.press("Tab")
                page.keyboard.press("Tab")
                page.keyboard.press("Space")
            settle(page)
            log.append((len(stored(page)["people"]), page.evaluate(ACTIVE_JS)))
        bill = stored(page)
        ok = [n for n, _ in log] == list(range(4, 13)) and bill["nextId"] == 13 and all(label == f"Person {n} name" for n, label in log)
        record("K1 keyboard Enter and Space on Add person x9 each add exactly one, focus on the new name", ok and not errors, log[-3:])
        # a key press on the new row's Remove is never held back, although 9 guards are outstanding
        page.keyboard.press("Tab")  # the new row's Remove
        page.keyboard.press("Enter")
        settle(page)
        record("K2 Tab + Enter on a Remove with guards outstanding removes one person", len(stored(page)["people"]) == 11, len(stored(page)["people"]))
        # one mouse press of count 1 clears every outstanding guard: the next double click selects a word
        page.get_by_role("button", name="Remove Person 5", exact=True).click()
        record("K2b a mouse click on a Remove after the keyboard adds removes one person", len(stored(page)["people"]) == 10, len(stored(page)["people"]))
        field = page.get_by_label("Person 1 name", exact=True)
        field.fill("Siti Nur")
        field.dblclick(position={"x": 14, "y": 12})
        settle(page)
        sel = page.evaluate(SELECTION_JS)
        record("S1 after the guards of 9 keyboard Adds, a Remove click and a double click on a name still selects the word", sel.strip() == "Siti", repr(sel))
    finally:
        context.close()


def case_keyboard_items(browser, base):
    context, page, errors = fresh(browser, base, items_bill(1))
    try:
        add = page.get_by_role("button", name="Add item", exact=True)
        log = []
        for step in range(6):
            add.focus()
            page.keyboard.press("Enter" if step % 2 == 0 else "Space")
            settle(page)
            log.append((len(stored(page)["items"]), page.evaluate(ACTIVE_JS)))
        ok = [n for n, _ in log] == list(range(2, 8)) and all(label == f"Item {n} name" for n, label in log)
        record("K3 keyboard Enter and Space on Add item x6 each add exactly one, focus on the new name", ok and not errors, log[-2:])
    finally:
        context.close()


# ----------------------------------------------------------------------------------------------- D: deliberate
def case_deliberate(browser, base):
    for kind in ("people", "items"):
        seed = people_bill(3) if kind == "people" else items_bill(2)
        label = "Add person" if kind == "people" else "Add item"
        noun = "Person" if kind == "people" else "Item"
        rows = "li.person" if kind == "people" else "li.item"
        for place in ("right-edge", "centre"):
            context, page, errors = fresh(browser, base, seed)
            try:
                add = page.get_by_role("button", name=label, exact=True)
                page.mouse.click(*press_point(add, place))
                n = page.locator(rows).count()
                # 1: a click of its own (count 1) on the new row's name field, straight after, then typing
                name = page.get_by_label(f"{noun} {n} name", exact=True)
                page.mouse.click(*middle(name.bounding_box(), dx=30))
                page.keyboard.type("Ali")
                typed = name.input_value()
                record(f"D1 {label} ({place}) then a click on the new name and typing keeps the text", typed == "Ali", repr(typed))
                # 2: a click of its own on the new row's Remove removes it (not swallowed)
                remove = page.locator(rows).nth(n - 1).locator("button.icon-btn").first
                page.mouse.click(*middle(remove.bounding_box()))
                settle(page)
                record(f"D2 {label} ({place}) then a click of its own on the new Remove removes that row", page.locator(rows).count() == n - 1, page.locator(rows).count())
                record(f"D3 {label} ({place}) no console or page error", not errors, errors)
            finally:
                context.close()
    # another control straight after: the mode label
    context, page, errors = fresh(browser, base, people_bill(3))
    try:
        page.mouse.click(*press_point(page.get_by_role("button", name="Add person", exact=True), "right-edge"))
        page.get_by_text("By item", exact=True).click()
        settle(page)
        record("D4 Add person then a click of its own on the mode label By item switches the mode", stored(page)["mode"] == "item", stored(page)["mode"])
    finally:
        context.close()


# ----------------------------------------------------------------------------------------------- W: word select
def case_word(browser, base):
    for kind in ("people", "items"):
        for how in ("mouse", "keyboard"):
            seed = people_bill(3) if kind == "people" else items_bill(2)
            label = "Add person" if kind == "people" else "Add item"
            noun = "Person" if kind == "people" else "Item"
            context, page, errors = fresh(browser, base, seed)
            try:
                add = page.get_by_role("button", name=label, exact=True)
                if how == "mouse":
                    page.mouse.click(*press_point(add, "right-edge" if kind == "people" else "centre"))
                else:
                    add.focus()
                    page.keyboard.press("Enter")
                settle(page)
                page.keyboard.type("Teh tarik" if kind == "items" else "Siti Nur")
                n = page.locator("li.person" if kind == "people" else "li.item").count()
                field = page.get_by_label(f"{noun} {n} name", exact=True)
                box = field.bounding_box()
                for word, x in (("first", 18), ("second", 62 if kind == "items" else 52)):
                    page.mouse.dblclick(box["x"] + x, box["y"] + box["height"] / 2)
                    settle(page)
                    sel = page.evaluate(SELECTION_JS)
                    record(f"W {label} by {how}, type, double click the {word} word selects a word", sel.strip() != "", repr(sel))
            finally:
                context.close()


# ----------------------------------------------------------------------------------------------- C: caps
def case_caps(browser, base):
    cases = [("people", people_bill(11), "Add person", 12), ("items", items_bill(49), "Add item", 50)]
    for kind, seed, label, after in cases:
        for gesture in ("mouse-double", "mouse-triple", "touch-double"):
            for place in ("right-edge", "centre"):
                context, page, errors = fresh(browser, base, seed, touch=gesture == "touch-double")
                try:
                    add = page.get_by_role("button", name=label, exact=True)
                    point = press_point(add, place)
                    if gesture == "mouse-double":
                        page.mouse.dblclick(*point)
                    elif gesture == "mouse-triple":
                        page.mouse.click(*point, click_count=3)
                    else:
                        page.touchscreen.tap(*point)
                        page.touchscreen.tap(*point)
                    settle(page)
                    bill = stored(page)
                    count = len(bill["people" if kind == "people" else "items"])
                    focus = page.evaluate(ACTIVE_JS)
                    expect_focus = ("Person" if kind == "people" else "Item") + f" {after} name"
                    expect_next = 13 if kind == "people" else 4 + 49 + 1
                    ok = count == after and bill["nextId"] == expect_next and focus == expect_focus and not errors
                    record(f"C {label} at the cap, {gesture}, {place}", ok, (count, bill["nextId"], focus, errors))
                finally:
                    context.close()


# ----------------------------------------------------------------------------------------------- S: stack
def case_stack(browser, base):
    context, page, errors = fresh(browser, base, people_bill(4))
    try:
        page.get_by_role("button", name="Remove P4", exact=True).click()
        page.get_by_role("button", name="Add person", exact=True).click()
        n = len(stored(page)["people"])
        record("S2 Remove click then Add click (count 1 each) = 4 people", n == 4, n)
        page.get_by_role("button", name="Add person", exact=True).dblclick()
        settle(page)
        n = len(stored(page)["people"])
        record("S3 then a double click on Add person adds exactly one", n == 5, n)
    finally:
        context.close()


def main():
    server = rig.StaticServer(PROJECT).start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                case_keyboard_people(browser, server.base)
                case_keyboard_items(browser, server.base)
                case_deliberate(browser, server.base)
                case_word(browser, server.base)
                case_caps(browser, server.base)
                case_stack(browser, server.base)
            finally:
                browser.close()
    finally:
        server.stop()
        (HERE / "hunt-results.json").write_text(json.dumps(RESULTS, indent=1), encoding="utf-8")
    failed = [r for r in RESULTS if not r["ok"]]
    print(f"{len(RESULTS)} cases, {len(failed)} failed")


main()
