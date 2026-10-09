"""Ghost-click follow-up: every share toggle of the S1 bill (4 items x 3 people = 12 toggles), at 360x640.

One page per gesture. For each toggle in turn: double click (expect: two flips, back to where it was), triple click
(expect: one net flip of that toggle only), double tap (expect: back to where it was). After each gesture every other
toggle, every name and every price must be unchanged. A toggle's layout never moves, so the second click should land on the
same toggle; the log of click targets proves it.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import seeds  # noqa: E402

PRESSED_JS = "() => [...document.querySelectorAll('li.item')].map((li) => [...li.querySelectorAll('.tap')].map((b) => b.getAttribute('aria-pressed') === 'true'))"
OTHER_JS = "() => ({ people: [...document.querySelectorAll('li.person input')].map((i) => i.value), items: [...document.querySelectorAll('li.item')].map((li) => [li.querySelectorAll('input')[0].value, li.querySelectorAll('input')[1].value]) })"
ITEMS = ["Nasi lemak ayam", "Char kuey teow", "Mee goreng mamak", "Satay, 10 sticks"]
PEOPLE = ["Aisyah", "Ben", "Chen"]


def body(browser, server, results):
    base = server.base
    for gesture in ("dbl", "triple", "tap2"):
        ctx, page, cap = common.open_page(browser, base, seed=seeds.S1, viewport=(360, 640), touch=gesture == "tap2")
        try:
            common.settle(page)
            others0 = page.evaluate(OTHER_JS)
            for i, item in enumerate(ITEMS):
                for j, person in enumerate(PEOPLE):
                    before = page.evaluate(PRESSED_JS)
                    x, y = common.centre(page.get_by_role("group", name=f"Who had {item}").get_by_role("button", name=person, exact=True))
                    page.evaluate("() => { window.evlog = []; }")
                    if gesture == "dbl":
                        page.mouse.dblclick(x, y)
                    elif gesture == "triple":
                        page.mouse.click(x, y, click_count=3)
                    else:
                        page.touchscreen.tap(x, y)
                        page.touchscreen.tap(x, y)
                    common.settle(page, 80)
                    after = page.evaluate(PRESSED_JS)
                    targets = {e["target"] for e in page.evaluate("() => window.evlog") if e["type"] == "click"}
                    expected = [row[:] for row in before]
                    if gesture == "triple":
                        expected[i][j] = not expected[i][j]
                    ok = after == expected and page.evaluate(OTHER_JS) == others0 and len(targets) == 1 and not cap.problems(base)
                    results["cases"].append({"case": f"{gesture} on {person} of {item}", "ok": ok, "targets": sorted(targets)})
                    if not ok:
                        print(f"FAIL {gesture} {person} / {item}: before {before} after {after} targets {targets}")
            bad = [c for c in results["cases"] if not c["ok"] and c["case"].startswith(gesture)]
            print(f"{gesture}: 12 toggles, {12 - len(bad)} behave as expected (all clicks on the same toggle, nothing else changed)")
        finally:
            ctx.close()


if __name__ == "__main__":
    common.run_probe("p6c-every-toggle", body)
