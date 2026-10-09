"""Ghost-click follow-up (audit item 2): what lands under the pointer for the second click when the page is
scrolled so the control sits at different heights, and when an invalid price field has just been left.

Part A (position): a long by-item bill (8 items, 3 people), 360 x 640. The control is scrolled to a chosen
height (50..550 px from the top of the viewport), then one single click (baseline) and one double click in
fresh contexts. Controls: Add item, Remove of the last item, Remove of a middle item.
Part B (RD-3): type an invalid price into item 1 and stay in the field, then double click a control below it.
The first press blurs the field, the error appears when that press ends and everything under it moves down.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import seeds  # noqa: E402

LONG = seeds.changed(seeds.S1, lambda d: d["bill"].update(
    items=[{"id": f"i{n}", "name": f"Dish {n}", "priceText": f"{n + 9}.00", "who": [["p1"], ["p2"], ["p3"], ["p1", "p2"]][n % 4]} for n in range(4, 12)],
    nextId=12))
KEYS = ["draft", "mode", "people", "items"]


def scroll_control_to(page, locator, target_y):
    locator.scroll_into_view_if_needed()
    box = locator.bounding_box()
    page.evaluate("(dy) => window.scrollBy(0, dy)", box["y"] + box["height"] / 2 - target_y)
    page.wait_for_timeout(60)
    box = locator.bounding_box()
    return (box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)


def click_events(page):
    return [f"{e['type']}:{e['detail']}:{e['target']}:{'reached' if e['reached'] else 'SWALLOWED'}"
            for e in page.evaluate("() => window.evlog") if e["type"] in ("mousedown", "click")]


def control_locator(page, name):
    if name == "add-item":
        return page.get_by_role("button", name="Add item", exact=True)
    if name == "remove-last":
        return page.get_by_role("button", name="Remove Dish 11", exact=True)
    if name == "remove-middle":
        return page.get_by_role("button", name="Remove Dish 7", exact=True)
    raise ValueError(name)


def run_position(browser, base, name, target_y, gesture, touch=False):
    ctx, page, cap = common.open_page(browser, base, seed=LONG, viewport=(360, 640), touch=touch)
    try:
        common.settle(page)
        x, y = scroll_control_to(page, control_locator(page, name), target_y)
        before = common.snap(page)
        page.evaluate("() => { window.evlog = []; }")
        if gesture == "single":
            page.mouse.click(x, y)
        elif gesture == "dbl":
            page.mouse.dblclick(x, y)
        else:
            page.touchscreen.tap(x, y)
            page.touchscreen.tap(x, y)
        common.settle(page, 200)
        return before, common.snap(page), click_events(page), cap.problems(base), (round(x), round(y))
    finally:
        ctx.close()


def part_a(browser, server, results):
    for name in ("add-item", "remove-last", "remove-middle"):
        for target_y in (50, 150, 250, 350, 450, 550):
            _, single, _, _, _ = run_position(browser, server.base, name, target_y, "single")
            for gesture in ("dbl", "tap2"):
                before, after, events, problems, point = run_position(browser, server.base, name, target_y, gesture, touch=gesture == "tap2")
                same = all(after[k] == single[k] for k in KEYS)
                row = {"part": "A", "control": name, "target_y": target_y, "point": point, "gesture": gesture,
                       "data_equal_single": same, "events": events, "problems": problems,
                       "single_items": len(single["items"]), "after_items": len(after["items"]),
                       "single_who": [i["who"] for i in single["items"]][-2:], "after_who": [i["who"] for i in after["items"]][-2:]}
                results["cases"].append(row)
                print(f"A {name:13} y={target_y:3} {gesture:5} data==single {same!s:5} items {len(single['items'])}->{len(after['items'])} "
                      f"click2={events[2] if len(events) > 2 else '-'}")


def run_after_invalid_price(browser, base, target_name, gesture, touch=False):
    ctx, page, cap = common.open_page(browser, base, seed=seeds.S1, viewport=(390, 844), touch=touch)
    try:
        common.settle(page)
        price = page.get_by_label("Item 1 price in RM")
        price.fill("abc")  # focus stays in the field, no error yet (R10)
        targets = {
            "toggle-ben-item1": lambda: page.get_by_role("group", name="Who had Nasi lemak ayam").get_by_role("button", name="Ben", exact=True),
            "toggle-aisyah-item1": lambda: page.get_by_role("group", name="Who had Nasi lemak ayam").get_by_role("button", name="Aisyah", exact=True),
            "remove-item2": lambda: page.get_by_role("button", name="Remove Char kuey teow", exact=True),
            "add-item": lambda: page.get_by_role("button", name="Add item", exact=True),
            "remove-person-3": lambda: page.get_by_role("button", name="Remove Chen", exact=True),
        }
        x, y = common.centre(targets[target_name]())
        before = common.snap(page)
        page.evaluate("() => { window.evlog = []; }")
        if gesture == "single":
            page.mouse.click(x, y)
        elif gesture == "dbl":
            page.mouse.dblclick(x, y)
        else:
            page.touchscreen.tap(x, y)
            page.touchscreen.tap(x, y)
        common.settle(page, 200)
        return before, common.snap(page), click_events(page), cap.problems(base)
    finally:
        ctx.close()


def part_b(browser, server, results):
    for name in ("toggle-ben-item1", "toggle-aisyah-item1", "remove-item2", "add-item", "remove-person-3"):
        _, single, _, _ = run_after_invalid_price(browser, server.base, name, "single")
        for gesture in ("dbl", "tap2"):
            before, after, events, problems = run_after_invalid_price(browser, server.base, name, gesture, touch=gesture == "tap2")
            same = all(after[k] == single[k] for k in KEYS)
            row = {"part": "B", "control": name, "gesture": gesture, "data_equal_single": same, "events": events, "problems": problems,
                   "single_items": [i["who"] for i in single["items"]], "after_items": [i["who"] for i in after["items"]],
                   "single_people": single["people"], "after_people": after["people"]}
            results["cases"].append(row)
            print(f"B {name:20} {gesture:5} data==single {same!s:5} click2={events[2] if len(events) > 2 else '-'}")


def body(browser, server, results):
    part_a(browser, server, results)
    part_b(browser, server, results)


if __name__ == "__main__":
    common.run_probe("p6b-layout-scan", body)
