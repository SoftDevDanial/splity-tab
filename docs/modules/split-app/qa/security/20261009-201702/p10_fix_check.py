"""Checks the two suggested fixes for SEC-01 without writing any project file.

The patched modules are served from memory: the script reads src/ui/people.js, src/ui/items.js and src/ui/dom.js, applies
a string replacement, and answers the browser's request for that URL with the patched text (Playwright route.fulfill). The
repository is not touched and no copy of src/ is written anywhere. Same-origin, same CSP, no bypass_csp.

Fix B (narrow): Add person ignores a repeat click, like the Remove buttons do (people.js only).
Fix A (general): a Remove click arms the same document-level guard as the dialog (dom.js gets swallowRepeatClicks,
people.js and items.js call it), so the repeat press is cancelled whatever it lands on.

For each fix: the SEC-01 repro (S2 remove Chen, S8 remove the twelfth person; double click, triple click, double tap) and
the behaviours that must not change (a double click on a middle Remove still removes one row, two separate clicks remove two,
Enter on a Remove button removes one, a single Add person click adds one, a double click on Add person adds one,
the dialog Cancel double click still changes nothing). The first block runs the shipped code and must show the repro FAIL.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import seeds  # noqa: E402

SRC = common.ROOT / "src" / "ui"
GUARD = '''
export function swallowRepeatClicks() {
  const guard = (event) => {
    if (!isRepeatClick(event)) {
      document.removeEventListener("mousedown", guard, true);
      document.removeEventListener("click", guard, true);
      return;
    }
    event.stopPropagation();
    event.preventDefault();
  };
  document.addEventListener("mousedown", guard, true);
  document.addEventListener("click", guard, true);
}
'''
REMOVE_OLD = 'remove.addEventListener("click", (event) => { if (!isRepeatClick(event)) onRemove(id); });'
REMOVE_NEW = 'remove.addEventListener("click", () => { swallowRepeatClicks(); onRemove(id); });'


def patched(option):
    people = (SRC / "people.js").read_text(encoding="utf-8")
    items = (SRC / "items.js").read_text(encoding="utf-8")
    dom = (SRC / "dom.js").read_text(encoding="utf-8")
    if option == "B":
        new = people.replace('add.addEventListener("click", onAdd);', 'add.addEventListener("click", (event) => { if (!isRepeatClick(event)) onAdd(); });')
        assert new != people
        return {"/src/ui/people.js": new}
    people_new = people.replace(REMOVE_OLD, REMOVE_NEW).replace("el, isRepeatClick, setAttr", "el, swallowRepeatClicks, setAttr")
    items_new = items.replace(REMOVE_OLD, REMOVE_NEW).replace("el, isRepeatClick, setAttr", "el, swallowRepeatClicks, setAttr")
    assert REMOVE_NEW in people_new and REMOVE_NEW in items_new and "swallowRepeatClicks, setAttr" in people_new and "swallowRepeatClicks, setAttr" in items_new
    return {"/src/ui/dom.js": dom + GUARD, "/src/ui/people.js": people_new, "/src/ui/items.js": items_new}


def serve(text):
    def handler(route, request):
        route.fulfill(status=200, content_type="text/javascript", body=text)
    return handler


def open_patched(browser, base, option, seed, vp, touch=False):
    ctx, page, cap = common.open_page(browser, base, seed=seed, viewport=vp, touch=touch, goto=False)
    if option:
        for path, text in patched(option).items():
            page.route(base + path, serve(text))
    page.goto(base + "/")
    common.settle(page)
    return ctx, page, cap


def draft_bill(page):
    return json.loads(page.evaluate("() => localStorage.getItem('split.draft')"))["bill"]


def gesture(page, kind, x, y):
    if kind == "dbl":
        page.mouse.dblclick(x, y)
    elif kind == "triple":
        page.mouse.click(x, y, click_count=3)
    elif kind == "tap2":
        page.touchscreen.tap(x, y)
        page.touchscreen.tap(x, y)
    else:
        page.mouse.click(x, y)
    common.settle(page, 200)


def repro(browser, base, option, results):
    for label, seed, button in (("S2 remove Chen", seeds.S2, "Remove Chen"), ("S8 remove Mei Ling", seeds.S8, "Remove Mei Ling")):
        for vp in ((360, 640), (390, 844), (1280, 800)):
            for kind in ("dbl", "triple", "tap2"):
                if kind == "tap2" and vp[0] == 1280:
                    continue
                ctx, page, cap = open_patched(browser, base, option, seed, vp, touch=kind == "tap2")
                try:
                    x, y = common.centre(page.get_by_role("button", name=button, exact=True))
                    before = len(json.loads(seed)["bill"]["people"])
                    gesture(page, kind, x, y)
                    after = len(draft_bill(page)["people"])
                    ok = after == before - 1 and not cap.problems(base)
                    results["cases"].append({"case": f"fix {option or 'none'}: {label} {vp[0]}x{vp[1]} {kind}", "ok": ok, "people_before": before, "people_after": after})
                    print(f"{'PASS' if ok else 'FAIL'} fix {option or 'none'}: {label:20} {vp[0]}x{vp[1]:<4} {kind:6} people {before} -> {after}")
                finally:
                    ctx.close()


def regressions(browser, base, option, results):
    def check(name, ok, **extra):
        results["cases"].append({"case": f"fix {option}: {name}", "ok": ok, **extra})
        print(f"{'PASS' if ok else 'FAIL'} fix {option}: {name} {extra or ''}")

    five = seeds.changed(seeds.S2, lambda d: d["bill"].update(people=[{"id": f"p{n}", "name": f"P{n}"} for n in range(1, 6)], nextId=6))
    ctx, page, cap = open_patched(browser, base, option, five, (390, 844))
    try:
        x, y = common.centre(page.get_by_role("button", name="Remove P2", exact=True))
        gesture(page, "dbl", x, y)
        check("double click on a middle Remove removes one row", len(draft_bill(page)["people"]) == 4)
        x, y = common.centre(page.get_by_role("button", name="Remove P3", exact=True))
        page.mouse.click(x, y)
        page.mouse.click(x, y)
        common.settle(page, 150)
        check("two separate clicks on a Remove remove two rows", len(draft_bill(page)["people"]) == 2, people=[p["name"] for p in draft_bill(page)["people"]])
    finally:
        ctx.close()
    ctx, page, cap = open_patched(browser, base, option, five, (390, 844))
    try:
        page.get_by_role("button", name="Remove P2", exact=True).focus()
        page.keyboard.press("Enter")
        common.settle(page, 100)
        check("Enter on a Remove button removes one row", len(draft_bill(page)["people"]) == 4)
    finally:
        ctx.close()
    ctx, page, cap = open_patched(browser, base, option, seeds.S2, (390, 844))
    try:
        page.get_by_role("button", name="Add person", exact=True).click()
        check("a single click on Add person adds one", len(draft_bill(page)["people"]) == 4)
        x, y = common.centre(page.get_by_role("button", name="Add person", exact=True))
        gesture(page, "dbl", x, y)
        check("a double click on Add person adds one (the second click lands on the new field, as before)", len(draft_bill(page)["people"]) == 5)
    finally:
        ctx.close()
    ctx, page, cap = open_patched(browser, base, option, seeds.S1, (360, 640))
    try:
        before = draft_bill(page)
        page.get_by_role("button", name="New bill", exact=True).click()
        x, y = common.centre(page.get_by_role("button", name="Cancel", exact=True))
        gesture(page, "dbl", x, y)
        after = draft_bill(page)
        check("a double click on Cancel still changes nothing", before == after and not common.snap(page)["dialogOpen"])
    finally:
        ctx.close()
    ctx, page, cap = open_patched(browser, base, option, seeds.S1, (360, 640))
    try:
        x, y = common.centre(page.get_by_role("button", name="Remove Char kuey teow", exact=True))
        gesture(page, "dbl", x, y)
        snap = common.snap(page)
        check("double click on a middle item Remove removes one item", len(draft_bill(page)["items"]) == 3, focus_after=snap["focus"])
    finally:
        ctx.close()


def body(browser, server, results):
    base = server.base
    print("--- no fix (the shipped code), the repro must FAIL ---")
    repro(browser, base, None, results)
    for option in ("B", "A"):
        print(f"--- fix {option} ---")
        repro(browser, base, option, results)
        regressions(browser, base, option, results)


if __name__ == "__main__":
    common.run_probe("p10-fix-check", body)
