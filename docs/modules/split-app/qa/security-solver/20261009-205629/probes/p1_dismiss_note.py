"""Does a double click on "Dismiss note" reach a Remove button that slides under the pointer?

Why this probe exists: the Remove handlers of people.js and items.js ignore a click whose count is above 1 today
(WR-01, `isRepeatClick`). Ruling 1 replaces that test with `swallowRepeatClicks()`, which is armed by the Remove click
itself. A repeat press that follows some OTHER control (here "Dismiss note", which takes the note out of the layout and so
moves the rows up) is not covered by that guard. If a Remove button can land under the pointer, dropping the handler test
would let the repeat press remove a person. The note only shows after an unreadable draft, which starts a new bill of two
people (both Remove buttons disabled), so the probe adds a person first (three people, Remove enabled), then dismisses.

Prints one line per viewport and gesture: the control under the pointer after the note is gone, the people before and
after, and the click log.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import seeds  # noqa: E402

VIEWPORTS = [(360, 640), (390, 844), (1280, 800)]
UNDER_JS = """([x, y]) => { const e = document.elementFromPoint(x, y); if (!e) return null; const b = e.closest('button, input, label') || e;
  return b.tagName.toLowerCase() + (b.getAttribute('aria-label') ? ' [' + b.getAttribute('aria-label') + ']' : '') + (b.disabled ? ' (disabled)' : ''); }"""


def body(browser, server):
    for vp in VIEWPORTS:
        for kind in ("dbl", "triple", "tap2"):
            ctx, page, errors = common.open_page(browser, server.base, seed=seeds.UNREADABLE["B1"], viewport=vp, touch=kind == "tap2")
            try:
                page.get_by_role("button", name="Add person", exact=True).click()
                common.settle(page)
                before = [p["name"] for p in common.draft(page)["people"]]
                point = common.centre(page.get_by_role("button", name="Dismiss note", exact=True))
                page.evaluate("() => { window.evlog = []; }")
                # What is under the pointer once the note is gone: dismiss with one click and look, in a twin page.
                common.gesture(page, kind, point)
                after = [p["name"] for p in common.draft(page)["people"]]
                under = page.evaluate(UNDER_JS, list(point))
                print(f"{vp[0]}x{vp[1]:<4} {kind:6} under the pointer afterwards: {under!s:34} people {len(before)} -> {len(after)} "
                      f"{'CHANGED' if before != after else 'same'}  clicks {[e for e in page.evaluate('() => window.evlog') if e.startswith('click')]} {errors or ''}")
            finally:
                ctx.close()


if __name__ == "__main__":
    common.run_probe(body)
