"""Candidate test for RG-CR-08 (regression re-check). Not part of the project suite: run_mutants.py --extra-test copies it into a
scratch copy of tests/browser/ and runs it with the suite's own fixtures (open_app, rig.new_context, the clipboard recorder).

A price error appears when its field is left and pushes everything under it down by a line. A blur caused by a press waits for
the mouseup (RD-3), so the click on the chip that was pressed is not lost, but the SECOND press of a double click, triple click
or double tap then lands on what was a line higher: for a chip at the right end of the first chip row that is its own item's
Remove button. A Remove acts on every click that reaches it (071577a), and no armed guard is outstanding, so the item goes.

How the point is found: a scout page makes the price bad, leaves the field by Tab (the error shows at once) and looks, for every
4 px point of every chip as laid out BEFORE the error, at what lies under that point AFTER it. The first point that is a Remove
button is where the test presses, on a second page where the field still has focus, so the press itself causes the blur.
Eight people with ordinary names at 375 and 390 px is a layout where this happens (probe_toggle_remove.py has the whole map).
If a later layout leaves no such point the test fails loudly, because then it would probe nothing.
"""
import json

import pytest

import seeds

NAMES = ["Aisyah", "Ben", "Chen", "Devi", "Farid", "Grace", "Hafiz", "Indra"]
EIGHT_PEOPLE = seeds.changed(seeds.S1, lambda d: d["bill"].update(
    people=[{"id": f"p{n}", "name": name} for n, name in enumerate(NAMES, start=1)], nextId=20))
SETTLE_JS = "() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))"
CHIPS_JS = """() => {
  window.testChips = [...document.querySelectorAll('.who button')];
  return window.testChips.map((node, index) => { const r = node.getBoundingClientRect(); return { index, x: r.x, y: r.y, w: r.width, h: r.height }; });
}"""
LANDINGS_JS = """(boxes) => {
  const found = [];
  for (const b of boxes) {
    const item = window.testChips[b.index].closest('li.item');
    for (let x = b.x + 2; x < b.x + b.w - 1; x += 4) for (let y = b.y + 2; y < b.y + b.h - 1; y += 4) {
      const under = document.elementFromPoint(x, y);
      const button = under && under.closest('button');
      if (button && /^Remove/.test(button.getAttribute('aria-label') || '') && button.closest('li.item') === item) found.push([x, y]);
    }
  }
  return found;
}"""


def stored_items(page):
    return json.loads(page.evaluate("localStorage.getItem('split.draft')"))["bill"]["items"]


@pytest.mark.parametrize("gesture", ["mouse-double", "mouse-triple", "touch-double"])
@pytest.mark.parametrize("width", [375, 390])
def test_R12_a_repeat_press_on_a_chip_under_a_pending_price_error_never_removes_the_item(open_app, width, gesture):
    scout = open_app(seed=EIGHT_PEOPLE, viewport=(width, 3000)).page
    boxes = scout.evaluate(CHIPS_JS)
    price = scout.get_by_role("textbox", name="Item 1 price in RM", exact=True)
    price.fill("abc")
    price.press("Tab")
    scout.evaluate(SETTLE_JS)
    landings = scout.evaluate(LANDINGS_JS, boxes)
    assert landings, "no chip point lies over its own Remove once the error shows: this test no longer probes anything"
    x, y = landings[0]

    page = open_app(seed=EIGHT_PEOPLE, viewport=(width, 3000), touch=gesture == "touch-double").page
    before = stored_items(page)
    page.get_by_role("textbox", name="Item 1 price in RM", exact=True).fill("abc")  # focus stays: the press below blurs it
    if gesture == "mouse-double":
        page.mouse.dblclick(x, y)
    elif gesture == "mouse-triple":
        page.mouse.click(x, y, click_count=3)
    else:
        page.touchscreen.tap(x, y)
        page.touchscreen.tap(x, y)
    page.evaluate(SETTLE_JS)
    after = stored_items(page)
    assert [item["id"] for item in after] == [item["id"] for item in before]  # no item went
