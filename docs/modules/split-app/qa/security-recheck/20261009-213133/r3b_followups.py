"""Re-check item 3, follow-ups after the first run of r3_overswallow.py.

M  the middle-button row of r3 failed on its first run: what Chromium does after a middle press (diagnosis, no app involved).
K  a held Enter on Remove of the ONLY item: on the fixed tree with a realistic hold (first repeat after ~520 ms), an ordinary press,
   the same on the tree before the fixes (is it older than the fix?), and four rows on a candidate fix served from memory
   (a `keydown` guard with `repeat` true added to swallowRepeatClicks in dom.js; no project file written).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rc  # noqa: E402
from rc import seeds, btn  # noqa: E402

VP = (390, 844)
FIVE = seeds.changed(seeds.S2, lambda d: d["bill"].update(people=[{"id": f"p{n}", "name": f"P{n}"} for n in range(1, 6)], nextId=6))
ONE_ITEM = seeds.changed(seeds.S1, lambda d: d["bill"].update(items=d["bill"]["items"][:1]))

NEW_GUARD = '''export function swallowRepeatClicks() {
  const disarm = () => {
    document.removeEventListener("mousedown", guard, true);
    document.removeEventListener("click", guard, true);
    document.removeEventListener("keydown", keyGuard, true);
  };
  const guard = (event) => {
    if (!isRepeatClick(event)) {
      disarm();
      return;
    }
    event.stopPropagation();
    event.preventDefault();
  };
  // A held Enter repeats keydown with `repeat` true. After the first press moved focus (to "Add item" when the last item
  // went), the repeats would press the control that took focus. A fresh key press (repeat false) disarms.
  const keyGuard = (event) => {
    if (!event.repeat) {
      disarm();
      return;
    }
    event.stopPropagation();
    event.preventDefault();
  };
  document.addEventListener("mousedown", guard, true);
  document.addEventListener("click", guard, true);
  document.addEventListener("keydown", keyGuard, true);
}
'''

KEYLOG = "() => { window.__keys = []; window.addEventListener('keydown', (e) => window.__keys.push(e.key + (e.repeat ? ':repeat' : ':first')), true); }"


def candidate_dom():
    text = (rc.ROOT / "src" / "ui" / "dom.js").read_text(encoding="utf-8")
    a = text.index("export function swallowRepeatClicks() {")
    b = text.index("export function setText")
    return {"src/ui/dom.js": text[:a] + NEW_GUARD + "\n" + text[b:]}


def ids(page):
    b = rc.bill(page)
    return {"people": [p["id"] for p in b["people"]], "items": [i["id"] for i in b["items"]], "nextId": b["nextId"],
            "blank_items": [i["id"] for i in b["items"] if i["name"] == "" and i["priceText"] == ""]}


def open_for(browser, base, seed, sources=None):
    if sources:
        ctx, page, cap = rc.open_legacy_page(browser, base, sources, seed=seed, viewport=VP)
    else:
        ctx, page, cap = rc.open_page(browser, base, seed=seed, viewport=VP)
    rc.settle(page)
    page.evaluate(KEYLOG)
    return ctx, page, cap


def hold(page, key, first_wait=520, repeats=4, gap=35):
    """Key down, then auto-repeat keydowns after the usual initial delay, then key up."""
    page.keyboard.down(key)
    page.wait_for_timeout(first_wait)
    for _ in range(repeats):
        page.keyboard.down(key)
        page.wait_for_timeout(gap)
    page.keyboard.up(key)
    rc.settle(page, 120)


def body(browser, server, results):
    base = server.base

    def record(section, case, passed, **fields):
        row = {"section": section, "case": case, "pass": passed, **fields}
        results["cases"].append(row)
        tag = "INFO" if passed is None else ("PASS" if passed else "FAIL")
        print(f"{tag} [{section}] {case} {fields}")

    # ------------------------------------------------ M diagnosis of the middle-button row
    ctx, page, cap = open_for(browser, base, FIVE)
    try:
        rx, ry = rc.centre(btn(page, "Remove P2"))
        hx, hy = rc.centre(page.locator("h2#h-people"))
        rc.reset_log(page)
        page.mouse.click(rx, ry, button="middle")
        rc.settle(page, 60)
        mid = rc.clicks(page, ("mousedown", "mouseup", "click"))
        rc.reset_log(page)
        page.mouse.click(hx, hy)
        rc.settle(page, 60)
        after_first_left = rc.clicks(page, ("mousedown", "mouseup", "click"))
        rc.reset_log(page)
        page.mouse.click(hx, hy)
        rc.settle(page, 60)
        after_second_left = rc.clicks(page, ("mousedown", "mouseup", "click"))
        record("M", "middle press on Remove P2, then two left clicks on a heading: does the page see the first one?", None,
               middle_events=mid, first_left_click_events=after_first_left, second_left_click_events=after_second_left, people=ids(page)["people"],
               note="no page event for the first left click means the browser used it to end middle-button autoscroll")
    finally:
        ctx.close()

    # ------------------------------------------------ K held Enter on Remove of the only item
    ctx, page, cap = open_for(browser, base, ONE_ITEM)
    try:
        btn(page, "Remove Nasi lemak ayam").focus()
        hold(page, "Enter")
        s = ids(page)
        record("K", "fixed tree: Enter held ~700 ms (first repeat at 520 ms) on Remove of the ONLY item", s["items"] == [] and not s["blank_items"],
               items=s["items"], nextId=s["nextId"], blank_items=s["blank_items"], keys=page.evaluate("() => window.__keys"),
               clicks=rc.clicks(page, ("click",)), focus=rc.snap(page)["focus"])
    finally:
        ctx.close()
    ctx, page, cap = open_for(browser, base, ONE_ITEM)
    try:
        btn(page, "Remove Nasi lemak ayam").focus()
        page.keyboard.press("Enter", delay=90)
        rc.settle(page, 120)
        s = ids(page)
        record("K", "fixed tree: an ordinary Enter press (90 ms) on Remove of the ONLY item", s["items"] == [] and not s["blank_items"] and s["nextId"] == 8,
               items=s["items"], nextId=s["nextId"], keys=page.evaluate("() => window.__keys"), focus=rc.snap(page)["focus"])
    finally:
        ctx.close()
    ctx, page, cap = open_for(browser, base, ONE_ITEM, sources=rc.legacy_sources())
    try:
        btn(page, "Remove Nasi lemak ayam").focus()
        hold(page, "Enter")
        s = ids(page)
        record("K", "CONTROL, tree before the fixes (06fa151): the same held Enter (expected to show the same blank item: older than the fix)",
               bool(s["blank_items"]), items=s["items"], nextId=s["nextId"], blank_items=s["blank_items"], keys=page.evaluate("() => window.__keys"))
    finally:
        ctx.close()
    cand = candidate_dom()
    ctx, page, cap = open_for(browser, base, ONE_ITEM, sources=cand)
    try:
        btn(page, "Remove Nasi lemak ayam").focus()
        hold(page, "Enter")
        s = ids(page)
        record("K", "CANDIDATE fix from memory: the same held Enter", s["items"] == [] and not s["blank_items"] and s["nextId"] == 8 and not cap.problems(base),
               items=s["items"], nextId=s["nextId"], blank_items=s["blank_items"], keys=page.evaluate("() => window.__keys"), focus=rc.snap(page)["focus"])
    finally:
        ctx.close()
    ctx, page, cap = open_for(browser, base, FIVE, sources=cand)
    try:
        btn(page, "Remove P2").focus()
        page.keyboard.press("Enter")
        page.keyboard.press("Tab")
        page.keyboard.press("Enter")
        rc.settle(page, 100)
        s = ids(page)
        record("K", "CANDIDATE fix from memory: Enter on Remove P2, Tab, Enter on the next Remove, no pause (separate presses still work)",
               s["people"] == ["p1", "p4", "p5"] and not cap.problems(base), people=s["people"])
    finally:
        ctx.close()
    ctx, page, cap = open_for(browser, base, FIVE, sources=cand)
    try:
        rx, ry = rc.centre(btn(page, "Remove P2"))
        page.mouse.click(rx, ry)  # arms the guard; focus is in the name field now
        before = page.evaluate("() => document.activeElement.value")
        page.keyboard.down("a")
        for _ in range(5):
            page.keyboard.down("a")
            page.wait_for_timeout(30)
        page.keyboard.up("a")
        value = page.evaluate("() => document.activeElement.value")
        record("K", "CANDIDATE fix from memory: mouse Remove, then a held letter key in the name field is not eaten", value == before + "aaaaaa" and not cap.problems(base),
               before=before, after=value)
    finally:
        ctx.close()
    ctx, page, cap = open_for(browser, base, seeds.S2, sources=cand)
    try:
        btn(page, "New bill").focus()
        hold(page, "Enter", first_wait=300, repeats=3)
        record("K", "CANDIDATE fix from memory: Enter held on New bill leaves the dialog open on Cancel (it alternates open and shut today)",
               rc.dialog_open(page) and rc.snap(page)["focus"] == "Cancel", dialog_open=rc.dialog_open(page), focus=rc.snap(page)["focus"],
               keys=page.evaluate("() => window.__keys"))
    finally:
        ctx.close()
    ctx, page, cap = open_for(browser, base, seeds.S2)
    try:
        btn(page, "New bill").focus()
        hold(page, "Enter", first_wait=300, repeats=3)
        record("K", "fixed tree, for comparison: Enter held on New bill (audit T1 saw it alternate)", None,
               dialog_open=rc.dialog_open(page), focus=rc.snap(page)["focus"], keys=page.evaluate("() => window.__keys"),
               draft_unchanged=rc.snap(page)["draft"] == seeds.S2)
    finally:
        ctx.close()


if __name__ == "__main__":
    rc.run_probe("r3b-followups", body)
