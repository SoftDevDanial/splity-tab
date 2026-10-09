"""Who strips CR and LF from a name, and what does summaryText do with U+2028 and the other separators today? (spec gaps 3 and 4)

Part A. The threat-model row said "Inputs strip CR and LF". Measured here, in the running app and beside it:
  A1. four ways to put a line break into "Person 1 name" in the app: a typed Enter, execCommand('insertText') with LF and with CRLF,
      and a script that sets .value. What the field holds and what the draft holds afterwards.
  A2. the same assignment on a bare <input> in an about:blank page (no app code at all): the browser strips it by itself.
  A3. a <textarea> in the same bare page keeps the LF: the protection belongs to the input element, not to the app.
Part B. Names holding U+2028, U+2029, U+0085, a tab, NUL, a bidi override and the invisible ones, typed into Person 1, Copy summary,
  and the recorded clipboard text (the test recorder, never the operating system clipboard, CG-7). What is left of each in the copied text.
Prints only. No file is written. The special characters are built with chr(), so no escape text or raw invisible character sits in this file.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import seeds  # noqa: E402

LABEL = "Person 1 name"
SEPARATORS = {name: chr(code) for name, code in (
    ("U+2028", 0x2028), ("U+2029", 0x2029), ("U+0085", 0x85), ("tab", 0x09), ("NUL", 0x00), ("U+202E", 0x202E),
    ("U+200B", 0x200B), ("U+FEFF", 0xFEFF), ("U+00A0", 0xA0))}


def show(text):
    return text.encode("unicode_escape").decode("ascii")


def part_a(browser, server):
    ctx, page, errors = common.open_page(browser, server.base)
    try:
        field = page.get_by_label(LABEL, exact=True)

        def reset():
            field.click()
            page.keyboard.press("Control+A")
            page.keyboard.type("A")

        def report(way):
            value = field.input_value()
            draft = page.evaluate("() => localStorage.getItem('split.draft')")
            has_break = ("\n" in value) or ("\r" in value)
            in_draft = ("\\n" in (draft or "")) or ("\\r" in (draft or ""))
            print(f"A1 {way:34} field {show(value)!r:14} CR/LF in the field: {has_break}   CR/LF in the saved draft: {in_draft}")

        reset(); page.keyboard.type("B"); page.keyboard.press("Enter"); page.keyboard.type("C"); report("typed Enter between B and C")
        reset(); page.evaluate("() => document.execCommand('insertText', false, 'X\\nY')"); report("execCommand insertText LF")
        reset(); page.evaluate("() => document.execCommand('insertText', false, 'X\\r\\nY')"); report("execCommand insertText CRLF")
        page.evaluate("(label) => { const i = document.querySelector('input[aria-label=\"' + label + '\"]'); i.value = 'S\\nT\\rU'; }", LABEL)
        report("script sets .value to S LF T CR U")
        print("A1 errors:", errors or "none")
    finally:
        ctx.close()
    # A2, A3: a page with no app in it.
    ctx = common.rig.new_context(browser)
    try:
        bare = ctx.new_page()
        bare.goto("about:blank")
        print("A2 bare <input type=text>, value set to a LF b CR c:", show(bare.evaluate(
            "() => { const i = document.createElement('input'); i.type = 'text'; i.value = 'a\\nb\\rc'; return i.value; }")))
        print("A3 bare <textarea>,        value set to a LF b CR c:", show(bare.evaluate(
            "() => { const t = document.createElement('textarea'); t.value = 'a\\nb\\rc'; return t.value; }")))
    finally:
        ctx.close()


def part_b(browser, server):
    for name, char in SEPARATORS.items():
        ctx, page, errors = common.open_page(browser, server.base, seed=seeds.S2)
        try:
            field = page.get_by_label(LABEL, exact=True)
            field.click()
            page.keyboard.press("Control+A")
            page.keyboard.type(f"Q{char}Z")
            page.get_by_role("button", name="Copy summary", exact=True).click()
            common.settle(page, 50)
            copied = page.evaluate("() => window.testClipboardText")
            line = [row for row in copied.split("\n") if row.startswith("Q")]
            print(f"B  {name:7} typed -> field {show(field.input_value())!r:12} copied line {[show(r) for r in line]}  lines in the copied text: {len(copied.split(chr(10)))}"
                  f"{'  ERRORS ' + str(errors) if errors else ''}")
        finally:
            ctx.close()


def body(browser, server):
    part_a(browser, server)
    part_b(browser, server)


if __name__ == "__main__":
    common.run_probe(body)
