"""SEC-01 exact reproduction: a double click or double tap on the Remove button of the LAST person adds a blank person.

The second click of the double click lands on "Add person", which has slid under the pointer into the cell that
the removed row occupied. src/ui/people.js ignores a repeat click on a Remove button (WR-01), but the repeat click is not on a
Remove button here. Cases: S2 (Aisyah, Ben, Chen; Even, subtotal 100.00) removing Chen, and S8 (twelve people, Add person
disabled until the row goes) removing the twelfth. Gestures: single click (baseline), mouse double click, mouse triple click,
touchscreen double tap, at 360x640, 390x844 and 1280x800. Also the same gestures on the LAST item (to show Add item is not hit).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import seeds  # noqa: E402

VPS = [(360, 640), (390, 844), (1280, 800)]
GESTURES = ["single", "dbl", "triple", "tap2"]
SHARES_JS = "() => [...document.querySelectorAll('table.shares tbody tr')].map((tr) => tr.cells[0].textContent + ' ' + tr.cells[tr.cells.length - 1].textContent)"


def run(browser, base, seed, remove_name, vp, gesture):
    ctx, page, cap = common.open_page(browser, base, seed=seed, viewport=vp, touch=gesture == "tap2")
    try:
        common.settle(page)
        x, y = common.centre(page.get_by_role("button", name=remove_name, exact=True))
        before = json.loads(page.evaluate("() => localStorage.getItem('split.draft')") or seed)["bill"]
        page.evaluate("() => { window.evlog = []; }")
        if gesture == "single":
            page.mouse.click(x, y)
        elif gesture == "dbl":
            page.mouse.dblclick(x, y)
        elif gesture == "triple":
            page.mouse.click(x, y, click_count=3)
        else:
            page.touchscreen.tap(x, y)
            page.touchscreen.tap(x, y)
        common.settle(page, 200)
        after = json.loads(page.evaluate("() => localStorage.getItem('split.draft')"))["bill"]
        events = [f"{e['type']}:{e['detail']}:{e['target']}" for e in page.evaluate("() => window.evlog") if e["type"] == "click"]
        shares = page.evaluate(SHARES_JS)
        return {
            "people_before": [f"{p['id']}={p['name']!r}" for p in before["people"]], "people_after": [f"{p['id']}={p['name']!r}" for p in after["people"]],
            "items_after": len(after["items"]), "nextId_after": after["nextId"], "clicks": events, "shares": shares, "problems": cap.problems(base),
            "focus": common.snap(page)["focus"],
        }
    finally:
        ctx.close()


def body(browser, server, results):
    cases = [("S2 remove Chen (last of 3)", seeds.S2, "Remove Chen"), ("S8 remove Mei Ling (last of 12)", seeds.S8, "Remove Mei Ling"),
             ("S1 remove the last item (control: Add item is not hit)", seeds.S1, "Remove Satay, 10 sticks")]
    for label, seed, remove_name in cases:
        for vp in VPS:
            single = run(browser, server.base, seed, remove_name, vp, "single")
            for gesture in GESTURES[1:]:
                if gesture == "tap2" and vp[0] == 1280:
                    continue
                got = run(browser, server.base, seed, remove_name, vp, gesture)
                added_blank = len(got["people_after"]) > len(single["people_after"]) or got["items_after"] > single["items_after"]
                row = {"case": f"{label} {vp[0]}x{vp[1]} {gesture}", "added_unrequested_row": added_blank, "single": single, "gesture_result": got}
                results["cases"].append(row)
                print(f"{'ADDS A ROW' if added_blank else 'one removal  '} {label:55} {vp[0]}x{vp[1]:<4} {gesture:6} people {len(single['people_after'])} -> {len(got['people_after'])} "
                      f"items {single['items_after']} -> {got['items_after']} nextId {got['nextId_after']} last click {got['clicks'][-1] if got['clicks'] else None}")
                if added_blank and vp == VPS[1] and gesture == "dbl":
                    print("      after single:", single["people_after"], "shares", single["shares"])
                    print("      after double:", got["people_after"], "shares", got["shares"])


if __name__ == "__main__":
    common.run_probe("p9-sec01-repro", body)
