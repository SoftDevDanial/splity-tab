"""Threat row 4 (forged clipboard lines) and the control and bidi character list.

A. Line breaks pasted or inserted into a name field (Input.insertText, execCommand insertText, a typed Enter):
   what the field keeps, what is saved.
B. Control, separator and bidi characters in a person name, typed by insert_text and restored from a draft:
   the copied text must keep its line count (6 lines for the S2 bill), hold no control, separator or bidi
   control character, and carry no second "Adds up to" line.
The clipboard is the recorder stub (window.testClipboardText). The operating system clipboard is never touched.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import seeds  # noqa: E402

BAD_IN_TEXT = re.compile(r"[\x00-\x09\x0b-\x1f\x7f-\x9f  ‎‏‪-‮⁦-⁩؜]")

CHARS = [
    ("LS U+2028", " "), ("PS U+2029", " "), ("NEL U+0085", "\u0085"), ("VT U+000B", "\u000b"), ("FF U+000C", "\u000c"),
    ("NUL U+0000", "\u0000"), ("US U+001F", "\u001f"), ("DEL U+007F", "\u007f"), ("RLO U+202E", "‮"), ("LRI U+2066", "⁦"),
    ("LRM U+200E", "‎"), ("ALM U+061C", "؜"), ("ZWSP U+200B", "​"), ("BOM U+FEFF", "﻿"), ("NBSP U+00A0", " "),
]


def copy_text(page):
    page.get_by_role("button", name="Copy summary").click()
    common.settle(page, 60)
    return page.evaluate("() => window.testClipboardText")


def part_a(browser, base, results):
    ctx, page, cap = common.open_page(browser, base, seed=seeds.S2, viewport=(390, 844))
    try:
        common.settle(page)
        field = page.get_by_label("Person 1 name")
        item_probe = {}
        ways = {
            "insert_text LF": lambda: page.keyboard.insert_text("Ai\nsyah"),
            "insert_text CRLF": lambda: page.keyboard.insert_text("Ai\r\nsyah"),
            "insert_text LF at the end": lambda: page.keyboard.insert_text("Ai\n"),
            "execCommand insertText LF": lambda: page.evaluate("() => document.execCommand('insertText', false, 'Ai\\nsyah')"),
            "typed Enter key": lambda: (page.keyboard.type("Ai"), page.keyboard.press("Enter"), page.keyboard.type("syah")),
        }
        for label, act in ways.items():
            field.click()
            page.keyboard.press("Control+A")
            act()
            common.settle(page, 60)
            value = field.input_value()
            saved = json.loads(page.evaluate("() => localStorage.getItem('split.draft')"))["bill"]["people"][0]["name"]
            text = copy_text(page)
            lines = text.split("\n")
            ok = "\n" not in value and "\r" not in value and "\n" not in saved and len(lines) == 6 and sum(1 for ln in lines if ln.startswith("Adds up to")) == 1
            results["cases"].append({"case": f"A {label}", "ok": ok, "field_value": value, "saved_name": saved, "clip_lines": len(lines)})
            print(f"{'PASS' if ok else 'FAIL'} A {label:28} field={value!r} saved={saved!r} clipboard lines {len(lines)} row3={lines[2]!r}")
        # item name and price in by-item mode
        page.locator("label[for=mode-item]").click()
        page.get_by_role("button", name="Add item").click()
        name = page.get_by_label("Item 1 name")
        price = page.get_by_label("Item 1 price in RM")
        name.click()
        page.keyboard.insert_text("Tea\nOne")
        price.click()
        page.keyboard.insert_text("1\n2.50")
        common.settle(page, 60)
        saved = json.loads(page.evaluate("() => localStorage.getItem('split.draft')"))["bill"]["items"][0]
        ok = "\n" not in name.input_value() and "\n" not in price.input_value() and "\n" not in saved["name"] and "\n" not in saved["priceText"]
        results["cases"].append({"case": "A item name and price", "ok": ok, "name": saved["name"], "priceText": saved["priceText"]})
        print(f"{'PASS' if ok else 'FAIL'} A item name {saved['name']!r} price {saved['priceText']!r}")
    finally:
        ctx.close()


def check_clip(text):
    lines = text.split("\n")
    adds = [ln for ln in lines if ln.startswith("Adds up to")]
    return {"lines": len(lines), "adds_up_to_lines": len(adds), "bad_chars": sorted({hex(ord(c)) for c in text if BAD_IN_TEXT.match(c)}), "row3": lines[2] if len(lines) > 2 else None}


def part_b(browser, base, results):
    for how in ("typed", "restored"):
        ctx, page, cap = common.open_page(browser, base, seed=seeds.S2, viewport=(390, 844))
        try:
            common.settle(page)
            field = page.get_by_label("Person 1 name")
            for label, char in CHARS:
                name = f"A{char}B"
                if how == "typed":
                    field.click()
                    page.keyboard.press("Control+A")
                    page.keyboard.insert_text(name)
                    common.settle(page, 40)
                else:
                    page.evaluate("(t) => localStorage.setItem('split.draft', t)", seeds.changed(seeds.S2, lambda d: d["bill"]["people"][0].update(name=name)))
                    page.reload()
                    common.settle(page, 80)
                value = field.input_value()
                got = check_clip(copy_text(page))
                ok = got["lines"] == 6 and got["adds_up_to_lines"] == 1 and not got["bad_chars"]
                kept = value == name
                results["cases"].append({"case": f"B {how} {label}", "ok": ok, "field_keeps_char": kept, **got})
                print(f"{'PASS' if ok else 'FAIL'} B {how:8} {label:12} field keeps it: {kept!s:5} clipboard lines {got['lines']} bad chars {got['bad_chars']} row3 {got['row3']!r}")
        finally:
            ctx.close()


def body(browser, server, results):
    part_a(browser, server.base, results)
    part_b(browser, server.base, results)


if __name__ == "__main__":
    common.run_probe("p2-clipboard-text", body)
