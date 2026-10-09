"""Widths 320 to 1280 in steps of 10 (heights 568, 844 and 1000): which control is under the pointer after the note is gone?

Companion of p1_dismiss_note.py. A double click on "Dismiss note" is only a way into a Remove button if one of these rows says
"Remove". The note is the unreadable-draft note (seed B1), three people (one Add person click), so Remove is enabled.
Prints only a summary and the rows that are not a heading, a div or the page body.
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import seeds  # noqa: E402

UNDER_JS = """([x, y]) => { const e = document.elementFromPoint(x, y); if (!e) return null; const b = e.closest('button, input, label') || e;
  return b.tagName.toLowerCase() + (b.getAttribute('aria-label') ? ' [' + b.getAttribute('aria-label') + ']' : '') + (b.disabled ? ' (disabled)' : ''); }"""


def body(browser, server):
    seen = Counter()
    interesting = []
    for height in (568, 844, 1000):
        for width in range(320, 1281, 10):
            ctx, page, errors = common.open_page(browser, server.base, seed=seeds.UNREADABLE["B1"], viewport=(width, height))
            try:
                page.get_by_role("button", name="Add person", exact=True).click()
                common.settle(page, 30)
                x, y = common.centre(page.get_by_role("button", name="Dismiss note", exact=True))
                page.get_by_role("button", name="Dismiss note", exact=True).click()
                common.settle(page, 30)
                under = page.evaluate(UNDER_JS, [x, y])
                seen[under] += 1
                if under and ("button" in under or "input" in under or "label" in under):
                    interesting.append((width, height, under))
            finally:
                ctx.close()
    print("under the pointer after the note is dismissed, over", sum(seen.values()), "viewports:")
    for what, count in seen.most_common():
        print(f"  {count:4}  {what}")
    print("rows where it is a control:", interesting[:40], "... total", len(interesting))


if __name__ == "__main__":
    common.run_probe(body)
