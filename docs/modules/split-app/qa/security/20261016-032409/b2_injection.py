"""B2, rerun on today's tree. Text stays text (R37), names stay plain (R62), the People line and the copied summary.

cd to this folder, then: python -B b2_injection.py --engine chromium|webkit [--root <tree> --tag <tag>]
The step 5 probe (qa/security/20261015-222146/b2_injection.py) with the same hostile bill, planted in split.draft from a
same-origin page that does not run the app (the other github.io page of the threat row), and the same gestures. P1 and
its pills, At random, Pick again, copy from the card at 1280 x 800, then at 390 x 844 the People line, the Splits sheet
and its copy, and the strip's copy. Every copy goes to the clipboard stand-in.
What changed from step 5. The step 5 rule wanted every field to hold the stored name as typed. Since R62 the requirement
is the opposite, so this probe asserts the post-fix property. (1) Every name on screen, in the bill and in the save after
one change is plainName of the stored name, and nothing holds a character of the class. (2) The People line reads left
to right (each drawn character box lies right of the one before) and in one band (every box on one line top). (3) Each
copied summary's person rows are the screen's splits rows, name and amount, character for character. (4) The boot
writes nothing (R26). Row "v1" plants a version 1 draft whose sixth name is only class characters (R62 (2)).
--root runs the same probe on a control tree (the tree before the H-10 build, 798f17f, exported to the scratchpad),
which must go RED on (1) to (3). Writes b2_injection-<tag>-<engine>.json. --settle (added after B8) waits until the People line fits its row before it
is measured, because WebKit's first read after narrowing the page can come before the ResizeObserver refits it.
"""
import argparse
import json
import time

from common import Probe, say

C = chr
RLO, NUL, LS, RLI = C(0x202E), C(0), C(0x2028), C(0x2067)
NAMES = ["<svg onload=f()>", "Ben" + RLO, "Adds up to RM 0.00" + NUL, "A" + LS + "Adds up to", "Tom" + RLI]
ITEMS = ["<img src=x onerror=alert(1)>", "</li><li>Teh" + RLO, "Kopi"]
BILL = {
    "mode": "item",
    "people": [{"id": f"p{i + 1}", "name": n} for i, n in enumerate(NAMES)],
    "subtotalText": "",
    "items": [
        {"id": "i6", "name": ITEMS[0], "priceText": "24.90", "who": ["p1", "p2"]},
        {"id": "i7", "name": ITEMS[1], "priceText": "13.51", "who": ["p3", "p4", "p5"]},
        {"id": "i8", "name": ITEMS[2], "priceText": "7.07", "who": ["p1", "p2", "p3", "p4", "p5"]},
    ],
    "serviceText": "10", "sstText": "6", "spare": {"rule": "one", "personId": "p1"}, "nextId": 9,
}
DRAFT = json.dumps({"version": 2, "bill": BILL}, ensure_ascii=False, separators=(",", ":"))
V1_NAMES = ["Aisyah" + C(0x2066), C(0x85) + "Ben", "Chen" + C(0x2029) + "Lee", "Dan" + C(0x1B) + "[31m", C(0x202D) + "Eve" + C(0x202C),
            C(0x202E) + C(0x2066) + NUL + C(0x9F)]
V1_BILL = {"mode": "even", "people": [{"id": f"p{i + 1}", "name": n} for i, n in enumerate(V1_NAMES)], "subtotalText": "100.00",
           "items": [], "serviceText": "10", "sstText": "6", "nextId": 7}
V1_DRAFT = json.dumps({"version": 1, "bill": V1_BILL}, ensure_ascii=False, separators=(",", ":"))

# Core R35's class written out, as the suite writes it (Python's re has no \p{...}).
NAME_CLASS = frozenset([*range(0x00, 0x20), *range(0x7F, 0xA0), 0x2028, 0x2029, 0x061C, 0x200E, 0x200F,
                        *range(0x202A, 0x202F), *range(0x2066, 0x206A)])
assert len(NAME_CLASS) == 79


def plain(text):
    return "".join(c for c in text if ord(c) not in NAME_CLASS)


def class_chars(text):
    return [f"U+{ord(c):04X}" for c in (text or "") if ord(c) in NAME_CLASS]


def label(name, index, prefix="Person"):
    trimmed = name.strip(" \t\n\r\x0b\x0c ﻿                　")
    return trimmed if trimmed else f"{prefix} {index + 1}"


STRUCTURE = """() => {
  const body = document.body;
  const foreign = [...body.querySelectorAll('img, b, script, iframe, style, object, embed, link, meta, li li, a')]
    .map((n) => n.tagName + (n.className ? '.' + n.className : ''));
  const svgs = [...body.querySelectorAll('svg')].filter((s) => !['sprite', 'mark', 'ic', 'seal'].some((c) => s.classList.contains(c)))
    .map((s) => s.getAttribute('class'));
  const handlers = [...body.querySelectorAll('*')].filter((n) => [...n.attributes].some((a) => a.name.startsWith('on'))).length;
  const uses = [...body.querySelectorAll('use')].map((u) => u.getAttribute('href')).filter((h) => !/^#i-[a-z-]+$/.test(h));
  return { foreign, svgs, handlers, odd_use_hrefs: uses, pwned: window.pwned ?? null };
}"""

TEXTS = """() => {
  const values = [...document.querySelectorAll('#peopleList input')].map((i) => i.value);
  const itemValues = [...document.querySelectorAll('#itemList li.item input:not([inputmode])')].map((i) => i.value);
  const toggles = [...document.querySelectorAll('#itemList .tap span')].map((s) => s.textContent);
  const rows = [...document.querySelectorAll('#rbody .r-splits .nm')].map((s) => s.textContent);
  const removes = [...document.querySelectorAll('#peopleList button')].map((b) => b.getAttribute('aria-label'));
  const itemAria = [...document.querySelectorAll('#itemList [aria-label]')].map((n) => n.getAttribute('aria-label'));
  const chip = document.querySelector('#spareBtn');
  const people = document.querySelector('#peopleSum .sec-txt');
  return { values, itemValues, toggles, rows, removes, itemAria, chip: chip && chip.textContent,
    chipAria: chip && chip.getAttribute('aria-label'), peopleLine: people && people.textContent };
}"""

# One box per code point of the text node under `sel`, zero-width ones left out, as [left, top, right, bottom].
BOXES = """(sel) => {
  const node = document.querySelector(sel)?.firstChild;
  if (!node) return null;
  const boxes = []; let at = 0;
  for (const char of node.data) {
    const range = document.createRange(); range.setStart(node, at); range.setEnd(node, at + char.length);
    const box = range.getBoundingClientRect();
    if (box.width > 0) boxes.push([char, Math.round(box.left * 100) / 100, Math.round(box.top * 100) / 100,
      Math.round(box.right * 100) / 100, Math.round(box.bottom * 100) / 100]);
    at += char.length;
  }
  return { text: node.data, boxes, visible: node.parentElement.getClientRects().length > 0 };
}"""

SETTLE = [False]
SETTLED = "() => { const s = document.querySelector('#peopleSum'); return !!s && s.clientWidth > 0 && s.scrollWidth <= s.clientWidth; }"

ROWS_IN = """(sel) => [...document.querySelectorAll(sel + ' .r-splits li')].map((li) =>
  [li.querySelector('.nm').textContent, li.querySelector('.amt').textContent])"""


def line_reading(measure):
    if not measure or not measure["boxes"]:
        return {"left_to_right": None, "one_band": None}
    lefts = [b[1] for b in measure["boxes"]]
    tops = [b[2] for b in measure["boxes"]]
    back = [[measure["boxes"][i - 1][0], measure["boxes"][i][0], lefts[i - 1], lefts[i]]
            for i in range(1, len(lefts)) if lefts[i] <= lefts[i - 1]]
    return {"left_to_right": not back, "steps_backwards": len(back), "first_backwards": back[:6],
            "one_band": max(tops) - min(tops) <= 1, "tops": sorted(set(tops)), "boxes": len(lefts)}


def copy_matches(text, screen_rows):
    lines = text.split("\n")
    rows = lines[2:-1]
    return {"lines": len(lines), "last": lines[-1], "class_chars": class_chars(text.replace("\n", "")),
            "rows": rows, "screen_rows": [f"{n} {a}" for n, a in screen_rows],
            "matches_screen": rows == [f"{n} {a}" for n, a in screen_rows]}


def copy_now(page, count):
    page.wait_for_function(f"() => window.testClipboardWrites >= {count}")
    return page.evaluate("() => window.testClipboardText")


def main_row(probe):
    ctx = probe.context(viewport={"width": 1280, "height": 800})
    page, rec = probe.page(ctx)
    row = {"case": "v2 hostile names", "seeded": probe.seed(page, rec, DRAFT)}
    probe.open_app(page)
    row["stand_in"] = probe.stand_in(page)
    row["stored_at_boot_unchanged"] = probe.stored(page) == DRAFT
    row["structure_restored"] = page.evaluate(STRUCTURE)
    texts = page.evaluate(TEXTS)
    row["texts_restored"] = texts
    want_values = [plain(n) for n in NAMES]
    want_labels = [label(v, i) for i, v in enumerate(want_values)]
    row["want_values"], row["want_labels"] = want_values, want_labels
    page.locator("#spareBtn").click()
    page.wait_for_function("() => document.querySelector('#spareDlg').open")
    row["pills"] = page.evaluate("() => [...document.querySelectorAll('#pickList .pill-face')].map((p) => p.textContent)")
    row["structure_p1"] = page.evaluate(STRUCTURE)
    page.locator("#spareDlg label.choice", has_text="At random").click()
    page.wait_for_function("() => document.querySelector('#pickAgainSheet')")
    page.locator("#pickAgainSheet").click()
    page.locator("#spareDlg button[aria-label=Close]").click()
    page.wait_for_function("() => !document.querySelector('#spareDlg').open")
    page.locator("#copyBtn").click()
    row["copy_card"] = copy_matches(copy_now(page, 1), page.evaluate(ROWS_IN, "#rbody"))
    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_function("() => getComputedStyle(document.querySelector('#strip')).display !== 'none'")
    if SETTLE[0]:  # --settle: let the ResizeObserver refit the People line first (B8), bounded at 5 s
        page.wait_for_function(SETTLED, timeout=5000)
        time.sleep(0.5)
        row["settled"] = page.evaluate(SETTLED)
    measure = page.evaluate(BOXES, "#peopleSum .sec-txt")
    row["people_line"] = {"text": measure and measure["text"], "visible": measure and measure["visible"], **line_reading(measure)}
    row["people_line_boxes"] = measure
    page.locator("#splitsBtn").click()
    page.wait_for_function("() => document.querySelector('#splitsDlg').open")
    row["structure_sheet"] = page.evaluate(STRUCTURE)
    page.locator("#splitsDlg .r-copy").click()
    row["copy_sheet"] = copy_matches(copy_now(page, 2), page.evaluate(ROWS_IN, "#splitsDlg"))
    page.locator("#splitsDlg button[aria-label=Close]").click()
    page.wait_for_function("() => !document.querySelector('#splitsDlg').open")
    page.locator("#stripCopy").click()
    row["copy_strip"] = copy_matches(copy_now(page, 3), page.evaluate(ROWS_IN, "#rbody"))
    # One real change (a digit typed at the end of the first item's price) saves, and the save holds the plain names.
    price = page.locator("#itemList li.item input[inputmode]").first
    price.click()
    page.keyboard.press("End")
    page.keyboard.type("0")
    page.wait_for_function("(d) => localStorage.getItem('split.draft') !== d", arg=DRAFT)
    saved = json.loads(probe.stored(page))["bill"]
    row["saved_after_change"] = {"people": [p["name"] for p in saved["people"]], "items": [i["name"] for i in saved["items"]]}
    row["clipboard_refused"] = page.evaluate("() => window.testClipboardRefused")
    row["csp"] = probe.violations(page)
    row.update(console=rec["console"], page_errors=rec["page_errors"], dialogs=rec["dialogs"], failed=rec["failed"],
               off_rule_requests=probe.off_rule_requests(rec))
    on_screen = [*texts["values"], *texts["itemValues"], *texts["toggles"], *texts["rows"], *texts["removes"],
                 *texts["itemAria"], texts["chip"] or "", texts["chipAria"] or "", texts["peopleLine"] or "", *row["pills"]]
    row["class_chars_on_screen"] = sorted({c for t in on_screen for c in class_chars(t)})
    row["pass_plain"] = (texts["values"] == want_values and texts["itemValues"] == [plain(n) for n in ITEMS]
                         and texts["rows"] == want_labels and not row["class_chars_on_screen"]
                         and row["saved_after_change"] == {"people": want_values, "items": [plain(n) for n in ITEMS]})
    row["pass_people_line"] = bool(row["people_line"]["left_to_right"] and row["people_line"]["one_band"])
    copies = [row["copy_card"], row["copy_sheet"], row["copy_strip"]]
    row["pass_copy_matches_screen"] = all(c["matches_screen"] and c["lines"] == 3 + len(NAMES) and not c["class_chars"]
                                          and c["last"].startswith("Adds up to RM ") for c in copies)
    structures = [row["structure_restored"], row["structure_p1"], row["structure_sheet"]]
    row["pass_text_stays_text"] = all(not s["foreign"] and not s["svgs"] and not s["handlers"] and not s["odd_use_hrefs"]
                                      and s["pwned"] is None for s in structures)
    row["pass_boot_writes_nothing"] = row["stored_at_boot_unchanged"]
    row["pass_quiet"] = (not row["csp"] and not rec["console"] and not rec["page_errors"] and not rec["dialogs"]
                         and not rec["failed"] and not row["off_rule_requests"] and row["clipboard_refused"] == 0)
    ctx.close()
    return row


def v1_row(probe):
    ctx = probe.context(viewport={"width": 390, "height": 844})
    page, rec = probe.page(ctx)
    row = {"case": "v1 draft, sixth name only class characters", "seeded": probe.seed(page, rec, V1_DRAFT)}
    probe.open_app(page)
    probe.stand_in(page)
    row["note_shown"] = page.evaluate("() => !!document.querySelector('#dismissNote')")
    if page.locator("#peopleBtn").get_attribute("aria-expanded") == "false":
        page.locator("#peopleBtn").click()
    texts = page.evaluate(TEXTS)
    row["texts"] = texts
    want_values = [plain(n) for n in V1_NAMES]
    want_labels = [label(v, i) for i, v in enumerate(want_values)]
    row["want_values"], row["want_labels"] = want_values, want_labels
    page.locator("#peopleBtn").click()  # fold People so its line shows
    measure = page.evaluate(BOXES, "#peopleSum .sec-txt")
    row["people_line"] = {"text": measure and measure["text"], **line_reading(measure)}
    page.locator("#stripCopy").click()
    row["copy_strip"] = copy_matches(copy_now(page, 1), page.evaluate(ROWS_IN, "#rbody"))
    row["csp"] = probe.violations(page)
    row.update(console=rec["console"], page_errors=rec["page_errors"], off_rule_requests=probe.off_rule_requests(rec))
    row["pass"] = (not row["note_shown"] and texts["values"] == want_values and texts["rows"] == want_labels
                   and want_labels[5] == "Person 6" and row["people_line"]["left_to_right"] and row["people_line"]["one_band"]
                   and row["copy_strip"]["matches_screen"] and not row["csp"] and not rec["console"] and not rec["page_errors"]
                   and not row["off_rule_requests"])
    ctx.close()
    return row


def run(engine, root, tag):
    with Probe(f"b2_injection-{tag}", engine, root=root) as probe:
        main = main_row(probe)
        probe.rows.append(main)
        v1 = v1_row(probe)
        probe.rows.append(v1)
        keys = ("pass_plain", "pass_people_line", "pass_copy_matches_screen", "pass_text_stays_text", "pass_boot_writes_nothing", "pass_quiet")
        say(json.dumps({**{k: main[k] for k in keys}, "people_line": {k: v for k, v in main["people_line"].items() if k != "first_backwards"},
                        "first_backwards": main["people_line"].get("first_backwards"), "v1_pass": v1["pass"],
                        "v1_people_line": v1["people_line"]}, ensure_ascii=True, indent=1))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", choices=["chromium", "webkit"], default="chromium")
    parser.add_argument("--root", default=None)
    parser.add_argument("--tag", default="head")
    parser.add_argument("--settle", action="store_true")
    args = parser.parse_args()
    SETTLE[0] = args.settle
    run(args.engine, args.root, args.tag)
