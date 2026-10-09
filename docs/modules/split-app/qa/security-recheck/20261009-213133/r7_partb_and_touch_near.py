"""Re-check items 1 and 3, two extra measurements.

PART B  The audit's p6b part B (RD-3), unchanged and on the fixed tree: an invalid price is typed into item 1 and the field keeps focus,
        then a double click or double tap on a control below it. The first press blurs the field, the error line appears, everything
        under it moves down, and the second press may land on a Remove button. That is the one case where a repeat press can reach a
        Remove button without a Remove click having armed the guard first (the old handlers dropped such a press with their own
        count test; the new ones do not, BUILD.md judgment call 18). 5 controls x (double click, double tap) = 10 rows, each against a
        single click. The summary line says whether any click of the gesture reached a Remove button that was not the one aimed at.
TOUCH   Tap Remove P2, 60 ms later tap the name field of the row that moved up, 30, 40 and 60 px to the left of the Remove spot:
        Chromium's tap count is a measurement; a deliberate tap on a control 30 px or more away must carry count 1 and reach the field.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rc  # noqa: E402
from rc import seeds, btn  # noqa: E402

import p6b_layout_scan  # noqa: E402  (the audit's script, read only)

FIVE = seeds.changed(seeds.S2, lambda d: d["bill"].update(people=[{"id": f"p{n}", "name": f"P{n}"} for n in range(1, 6)], nextId=6))


def body(browser, server, results):
    base = server.base
    n0 = len(results["cases"])
    p6b_layout_scan.part_b(browser, server, results)
    part_b_rows = results["cases"][n0:]
    for row in part_b_rows:
        row["section"] = "part B"
        hits = [e for e in row["events"] if "Remove" in e and e.startswith("click")]
        row["remove_clicks"] = hits
    aimed = {"remove-item2": "Remove Char kuey teow", "remove-person-3": "Remove Chen"}
    stray = [r for r in part_b_rows if any(aimed.get(r["control"], "\0") not in h for h in r["remove_clicks"])]
    print(f"\nPART B: {len(part_b_rows)} rows, data equal to a single click in {sum(1 for r in part_b_rows if r['data_equal_single'])}, "
          f"rows where a click reached a Remove button other than the aimed one: {len(stray)}, rows with problems: {sum(1 for r in part_b_rows if r['problems'])}")
    for r in part_b_rows:
        print(f"  {r['control']:20} {r['gesture']:5} data==single {r['data_equal_single']!s:5} remove clicks {r['remove_clicks']}")

    for vp in ((390, 844), (360, 640)):
        for d in (30, 40, 60):
            if vp[0] == 360 and d != 30:
                continue
            ctx, page, cap = rc.open_page(browser, base, seed=FIVE, viewport=vp, touch=True)
            try:
                rc.settle(page)
                rx, ry = rc.centre(btn(page, "Remove P2"))
                rc.reset_log(page)
                page.touchscreen.tap(rx, ry)
                page.wait_for_timeout(60)
                page.touchscreen.tap(rx - d, ry)
                rc.settle(page, 120)
                ev = rc.clicks(page, ("mousedown", "click"))
                row = {"section": "touch near", "viewport": f"{vp[0]}x{vp[1]}", "offset_px": d, "events": ev, "people": [p["id"] for p in rc.bill(page)["people"]],
                       "focus": rc.snap(page)["focus"], "problems": cap.problems(base)}
                row["pass"] = len(ev) == 4 and all(e.endswith(":reached") for e in ev) and ev[2].startswith("mousedown:1:") and ev[3].startswith("click:1:") and not row["problems"]
                results["cases"].append(row)
                print(("PASS " if row["pass"] else "FAIL ") + f"tap Remove P2, 60 ms, tap {d} px to the left, {vp[0]}x{vp[1]}", ev, "focus", row["focus"])
            finally:
                ctx.close()


if __name__ == "__main__":
    rc.run_probe("r7-partb-and-touch-near", body)
