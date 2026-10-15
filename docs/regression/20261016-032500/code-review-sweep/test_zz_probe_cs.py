"""Code-review probe for the consistency sweep (2026-10-16), scratch copy only, never under the project's tests/.

Question. When a name field's input event brings only characters of the class (R62), plainNameField gives back the
stored name, and main.js commits setPersonName or setItemName with an equal name. core returns a new Bill object for
an equal name, so does commit save, and does it clear the copy status? Spec app R25 says a commit that leaves the bill
unchanged writes nothing, and R24 rule 10 says only the next change to the bill clears the copy status.
Each row prints PROBE lines and asserts nothing, so every row reports what it measured. Read-only towards the
operating system clipboard (the recorder stand-in of rig.new_context).
"""
import pytest

import seeds
import support
from test_app import COPIED, RECORD_INPUT_JS, click_copy, insert, open_people_first, status_lines, stored_text

ROWS = [
    ("person", "‮", "only a class character (RLO) into Person 2 name"),
    ("person", "x", "control row, an ordinary letter into Person 2 name"),
    ("item", " ", "only a class character (LS) into the K1 item 2 name"),
]


@pytest.mark.parametrize("field, text, why", ROWS, ids=["person-RLO", "person-x", "item-LS"])
def test_probe_a_class_only_input_and_the_commit(open_app, field, text, why):
    seed = seeds.S2 if field == "person" else seeds.S1
    page = open_app(seed=seed, init_scripts=[support.storage_driver("count-set")]).page
    noted = stored_text(page)
    click_copy(page, "#stripCopy")
    before = status_lines(page)["strip"]
    if field == "person":
        open_people_first(page)
        target = support.person_field(page, 2)
    else:
        target = page.locator("li.item").nth(1).locator("input[type=text]").first
    target.click()
    page.keyboard.press("End")
    page.evaluate(RECORD_INPUT_JS)
    missed = insert(page, text)
    after = status_lines(page)["strip"]
    print(f"PROBE {field} {why}: not inserted {missed}, field now {target.input_value()!r}, "
          f"setItem calls {page.evaluate('window.testSetItemCalls')}, stored text unchanged {stored_text(page) == noted}, "
          f"strip status before copied {before == COPIED}, after copied {after == COPIED}, after {after}")
