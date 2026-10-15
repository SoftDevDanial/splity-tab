"""B7. Names stay plain at the name fields (R62 (1) and (2)), by every route a browser run can drive without the clipboard.

cd to this folder, then: python -B b7_name_inputs.py --engine chromium|webkit [--root <tree> --tag <tag>]
A plain S2 bill (Aisyah, Ben, Chen, even, RM 100.00) is planted in split.draft from a same-origin page and opened at
390 x 844. Each case puts hostile text into a name field by one route, then reads the field (value, caret, focus), the
bill as saved, the People line (folded, one box per drawn character), the splits rows and a copy from the strip.
Routes. "type", page.keyboard.type, one key or insert per character. "insert", page.keyboard.insert_text, one trusted
input event with the whole text, as a paste or a drop arrives. "paste-model" and "drop-model", the browser's own effect
of a paste or a drop modelled in the page (setRangeText at the selection, then an input event of inputType
insertFromPaste or insertFromDrop), because a real paste reads the system clipboard, which no run may touch.
"undo" and "redo", Control+Z and then Control+Y (Control+Shift+Z as well) after a removal, to see whether the browser's
history can bring a removed character back. "ime" (Chromium only), a CDP composition holding U+202E, then its commit.
The post-fix property for every case. The field, the bill, the save and every label hold no character of core R35's
class, the People line reads left to right in one band, the strip's copy rows equal the splits rows, and nothing logs.
--root runs the same cases on a control tree (798f17f, before the H-10 build), which must go RED.
Writes b7_name_inputs-<tag>-<engine>.json.
"""
import argparse
import json

from common import Probe, say
from b2_injection import NAME_CLASS, BOXES, ROWS_IN, STRUCTURE, class_chars, copy_matches, line_reading, plain

C = chr
RLO, RLI, PDI, LS, NUL, NEL, ESC = C(0x202E), C(0x2067), C(0x2069), C(0x2028), C(0), C(0x85), C(0x1B)
S2 = {"mode": "even", "people": [{"id": "p1", "name": "Aisyah"}, {"id": "p2", "name": "Ben"}, {"id": "p3", "name": "Chen"}],
      "subtotalText": "100.00", "items": [], "serviceText": "10", "sstText": "6", "spare": {"rule": "top"}, "nextId": 4}
S1 = {"mode": "item", "people": [{"id": "p1", "name": "Aisyah"}, {"id": "p2", "name": "Ben"}, {"id": "p3", "name": "Chen"}],
      "subtotalText": "", "items": [{"id": "i4", "name": "Nasi", "priceText": "24.90", "who": ["p1"]},
                                    {"id": "i5", "name": "Teh", "priceText": "13.50", "who": ["p2", "p3"]}],
      "serviceText": "10", "sstText": "6", "spare": {"rule": "top"}, "nextId": 6}
draft = lambda bill: json.dumps({"version": 2, "bill": bill}, ensure_ascii=False, separators=(",", ":"))

MODEL = """([kind, text]) => { const el = document.activeElement;
  el.setRangeText(text, el.selectionStart, el.selectionEnd, 'end');
  el.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: kind, data: kind === 'insertFromPaste' ? null : text })); }"""
FIELD = "() => { const el = document.activeElement; return [el.tagName, el.value, el.selectionStart, el.selectionEnd]; }"
RECORD = """() => { window.testInputs = [];
  window.addEventListener('input', (e) => window.testInputs.push([e.inputType, e.target.value, e.target.selectionStart]), true); }"""

# (case, bill, field selector index, route, text, setup keys before the text)
CASES = [
    ("type RLO after Ben", S2, 1, "type", "x" + RLO + "y", ["End"]),
    ("insert RLO after Ben", S2, 1, "insert", RLO + " and 3 more", ["End"]),
    ("insert mid-name, caret check", S2, 1, "insert", RLO + "x" + RLI, ["End", "ArrowLeft"]),
    ("paste-model LS, NUL, NEL, ESC", S2, 1, "paste-model", "a" + LS + "b" + NUL + NEL + "c" + ESC + "[31m", ["End"]),
    ("drop-model RLI without PDI", S2, 0, "drop-model", RLI + "Zed", ["End"]),
    ("paste-model only class characters into an emptied field", S2, 1, "paste-model", RLO + RLI + NUL + LS, ["Control+A", "Backspace"]),
    ("insert markup and RLO into an item name", S1, "item0", "insert", "<img src=x onerror=alert(1)>" + RLO, ["Control+A"]),
    ("insert 30 letters with controls at maxlength", S2, 2, "insert", ("ab" + RLO) * 10, ["Control+A"]),
]


def class_spelled(text):
    return "".join(f"U+{ord(c):04X}" if ord(c) in NAME_CLASS else c for c in text)


def people_field(page, index):
    if index == "item0":
        return page.locator("#itemList li.item input:not([inputmode])").first
    return page.locator("#peopleList input").nth(index)


def open_people(page):
    if page.locator("#peopleBtn").get_attribute("aria-expanded") == "false":
        page.locator("#peopleBtn").click()


def fold_people(page):
    if page.locator("#peopleBtn").get_attribute("aria-expanded") == "true":
        page.locator("#peopleBtn").click()


def read_after(probe, page, rec, row, copies):
    row["field"] = page.evaluate(FIELD)
    stored = json.loads(probe.stored(page))["bill"]
    row["saved_people"] = [p["name"] for p in stored["people"]]
    row["saved_items"] = [i["name"] for i in stored["items"]]
    row["inputs_seen"] = page.evaluate("() => window.testInputs")
    row["structure"] = page.evaluate(STRUCTURE)
    fold_people(page)
    measure = page.evaluate(BOXES, "#peopleSum .sec-txt")
    row["people_line"] = {"text": measure and measure["text"], **line_reading(measure)}
    page.locator("#stripCopy").click()
    page.wait_for_function(f"() => window.testClipboardWrites >= {copies}")
    row["copy_strip"] = copy_matches(page.evaluate("() => window.testClipboardText"), page.evaluate(ROWS_IN, "#rbody"))
    labels = page.evaluate("""() => [...document.querySelectorAll('#peopleList button, #itemList [aria-label]')]
      .map((n) => n.getAttribute('aria-label'))""")
    row["class_chars_anywhere"] = sorted({c for t in [*row["saved_people"], *row["saved_items"], row["field"][1],
                                                       row["people_line"]["text"] or "", *labels] for c in class_chars(t)})
    s = row["structure"]
    row["pass"] = (not row["class_chars_anywhere"] and row["people_line"]["left_to_right"] and row["people_line"]["one_band"]
                   and row["copy_strip"]["matches_screen"] and not s["foreign"] and not s["svgs"] and not s["handlers"]
                   and s["pwned"] is None and not probe.violations(page) and not rec["console"] and not rec["page_errors"]
                   and not probe.off_rule_requests(rec))


def one_case(probe, name, bill, index, route, text, keys):
    ctx = probe.context()
    page, rec = probe.page(ctx)
    row = {"case": name, "route": route, "text": [f"U+{ord(c):04X}" if ord(c) in NAME_CLASS else c for c in text]}
    probe.seed(page, rec, draft(bill))
    probe.open_app(page)
    probe.stand_in(page)
    page.evaluate(RECORD)
    open_people(page)
    field = people_field(page, index)
    before = field.input_value()
    field.click()
    for key in keys:
        page.keyboard.press(key)
    caret_before = page.evaluate(FIELD)[2]
    if route == "type":
        page.keyboard.type(text)
    elif route == "insert":
        page.keyboard.insert_text(text)
    elif route in ("paste-model", "drop-model"):
        page.evaluate(MODEL, ["insertFromPaste" if route == "paste-model" else "insertFromDrop", text])
    row["value_before"], row["caret_before"] = before, caret_before
    row["field_now"] = page.evaluate(FIELD)
    # R62 (1): the plain text of what the last input event left, and the caret p minus k, where p is that event's
    # selectionStart and k the class characters removed before p (the recorder runs before the app's listener).
    seen = page.evaluate("() => window.testInputs")
    raw, p = (seen[-1][1], seen[-1][2]) if seen else (None, None)
    row["last_input_raw"] = class_spelled(raw) if raw is not None else None
    row["value_expected"] = plain(raw) if raw is not None else None
    row["caret_expected"] = len(plain(raw[:p])) if raw is not None else None
    read_after(probe, page, rec, row, 1)
    f = row["field"]
    row["field_as_contracted"] = f[1] == row["value_expected"] and f[2] == f[3] == row["caret_expected"]
    row["pass"] = row["pass"] and row["field_as_contracted"] and len(seen) >= 1
    ctx.close()
    return row


def undo_case(probe):
    """A removal, then the browser's own undo and redo. Whatever the history brings back arrives as an input event."""
    ctx = probe.context()
    page, rec = probe.page(ctx)
    row = {"case": "undo and redo after a removal", "route": "undo"}
    probe.seed(page, rec, draft(S2))
    probe.open_app(page)
    probe.stand_in(page)
    page.evaluate(RECORD)
    open_people(page)
    field = people_field(page, 1)
    field.click()
    page.keyboard.press("End")
    page.keyboard.type("Q")
    page.keyboard.insert_text(RLO + "Z")
    steps = [["after insert", page.evaluate(FIELD)]]
    for key in ("Control+Z", "Control+Z", "Control+Z", "Control+Y", "Control+Shift+Z", "Control+Y"):
        page.keyboard.press(key)
        steps.append([key, page.evaluate(FIELD), json.loads(probe.stored(page))["bill"]["people"][1]["name"]])
    row["steps"] = steps
    row["any_class_in_field_or_save"] = sorted({c for s in steps for t in s[1:] for c in class_chars(t if isinstance(t, str) else t[1])})
    read_after(probe, page, rec, row, 1)
    row["pass"] = row["pass"] and not row["any_class_in_field_or_save"]
    ctx.close()
    return row


def ime_case(probe):
    """Chromium only. A composition holding U+202E (CDP Input.imeSetComposition), then its commit (Input.insertText)."""
    ctx = probe.context()
    page, rec = probe.page(ctx)
    row = {"case": "IME composition holding RLO, then commit", "route": "ime"}
    probe.seed(page, rec, draft(S2))
    probe.open_app(page)
    probe.stand_in(page)
    page.evaluate(RECORD)
    open_people(page)
    people_field(page, 1).click()
    page.keyboard.press("End")
    cdp = ctx.new_cdp_session(page)
    cdp.send("Input.imeSetComposition", {"text": "k" + RLO, "selectionStart": 2, "selectionEnd": 2})
    row["during"] = page.evaluate(FIELD)
    cdp.send("Input.insertText", {"text": "k" + RLO + "j"})
    row["after_commit"] = page.evaluate(FIELD)
    read_after(probe, page, rec, row, 1)
    ctx.close()
    return row


def run(engine, root, tag):
    with Probe(f"b7_name_inputs-{tag}", engine, root=root) as probe:
        for case in CASES:
            row = one_case(probe, *case)
            probe.rows.append(row)
            say(f"{'ok  ' if row['pass'] else 'FAIL'} {row['case']}: field {json.dumps(row['field'], ensure_ascii=True)}"
                f" expected value {json.dumps(row['value_expected'], ensure_ascii=True)} caret {row['caret_expected']}"
                f" line {row['people_line']['left_to_right']}/{row['people_line']['one_band']} copy {row['copy_strip']['matches_screen']}"
                f" class {row['class_chars_anywhere']}")
        row = undo_case(probe)
        probe.rows.append(row)
        say(f"{'ok  ' if row['pass'] else 'FAIL'} undo: {json.dumps(row['steps'], ensure_ascii=True)}")
        if engine == "chromium":
            row = ime_case(probe)
            probe.rows.append(row)
            say(f"{'ok  ' if row['pass'] else 'FAIL'} ime: during {json.dumps(row['during'], ensure_ascii=True)}"
                f" after {json.dumps(row['after_commit'], ensure_ascii=True)} class {row['class_chars_anywhere']}")
        say(f"passed {sum(r['pass'] for r in probe.rows)} of {len(probe.rows)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", choices=["chromium", "webkit"], default="chromium")
    parser.add_argument("--root", default=None)
    parser.add_argument("--tag", default="head")
    args = parser.parse_args()
    run(args.engine, args.root, args.tag)
