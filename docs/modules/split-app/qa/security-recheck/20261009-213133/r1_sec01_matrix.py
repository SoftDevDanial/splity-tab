"""Re-check item 1: SEC-01 as fixed.

Remove of the LAST person (S2 Chen, S8 the twelfth), of the last item and of the only item, with a mouse double click,
a mouse triple click and a touchscreen double tap at 360x640, 390x844 and 1280x800 (36 rows, a fresh context each).
The expectation is computed from the seed, not from a baseline run: exactly one row is gone, every other field of the saved
bill is as seeded, no person or item is blank, nextId is unchanged. Then 3 control rows on the tree BEFORE the fixes (served
from memory with route.fulfill, no project file written) to show the probe has teeth: they must show the defect.
"""
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rc  # noqa: E402
from rc import seeds  # noqa: E402

VPS = [(360, 640), (390, 844), (1280, 800)]
GESTURES = ["dbl", "triple", "tap2"]
ONE_ITEM = seeds.changed(seeds.S1, lambda d: d["bill"].update(items=d["bill"]["items"][:1]))

CASES = [
    dict(name="S2 last person (Remove Chen)", seed=seeds.S2, remove="Remove Chen", kind="person"),
    dict(name="S8 last of 12 (Remove Mei Ling)", seed=seeds.S8, remove="Remove Mei Ling", kind="person"),
    dict(name="S1 last item (Remove Satay, 10 sticks)", seed=seeds.S1, remove="Remove Satay, 10 sticks", kind="item"),
    dict(name="S1 only item (Remove Nasi lemak ayam)", seed=ONE_ITEM, remove="Remove Nasi lemak ayam", kind="item"),
]


def expected_bill(seed, kind):
    bill = copy.deepcopy(json.loads(seed)["bill"])
    if kind == "person":
        gone = bill["people"].pop()["id"]
        for item in bill["items"]:
            item["who"] = [w for w in item["who"] if w != gone]
    else:
        bill["items"].pop()
    return bill


def run(browser, base, case, vp, gest, legacy=None):
    kwargs = dict(seed=case["seed"], viewport=vp, touch=gest.startswith("tap"))
    ctx, page, cap = rc.open_legacy_page(browser, base, legacy, **kwargs) if legacy else rc.open_page(browser, base, **kwargs)
    try:
        rc.settle(page)
        x, y = rc.centre(rc.btn(page, case["remove"]))
        rc.reset_log(page)
        rc.gesture(page, gest, x, y)
        rc.settle(page, 250)
        before = json.loads(case["seed"])["bill"]
        after = rc.bill(page)
        want = expected_bill(case["seed"], case["kind"])
        blank_people = [p["id"] for p in after["people"] if p["name"] == ""]
        blank_items = [i["id"] for i in after["items"] if i["name"] == "" and i["priceText"] == ""]
        return {
            "case": case["name"], "viewport": f"{vp[0]}x{vp[1]}", "gesture": gest, "point": [round(x), round(y)],
            "people_before": len(before["people"]), "people_after": len(after["people"]),
            "items_before": len(before["items"]), "items_after": len(after["items"]),
            "nextId_before": before["nextId"], "nextId_after": after["nextId"],
            "blank_people": blank_people, "blank_items": blank_items,
            "bill_equals_expected": after == want,
            "clicks": rc.clicks(page, ("mousedown", "click")),
            "focus": rc.snap(page)["focus"], "problems": cap.problems(base),
        }
    finally:
        ctx.close()


def verdict(row):
    return (row["bill_equals_expected"] and row["nextId_after"] == row["nextId_before"]
            and not row["blank_people"] and not row["blank_items"] and not row["problems"])


def body(browser, server, results):
    base = server.base
    for case in CASES:
        for vp in VPS:
            for gest in GESTURES:
                row = run(browser, base, case, vp, gest)
                row["section"] = "fixed tree"
                row["pass"] = verdict(row)
                results["cases"].append(row)
                print(f"{'PASS' if row['pass'] else 'FAIL'} {case['name']:42} {row['viewport']:9} {gest:6} people {row['people_before']}->{row['people_after']} "
                      f"items {row['items_before']}->{row['items_after']} nextId {row['nextId_before']}->{row['nextId_after']} blank {row['blank_people'] + row['blank_items']} "
                      f"focus {row['focus']!r} clicks {[c for c in row['clicks'] if c.startswith('click')]}")
    legacy = rc.legacy_sources()
    for case, vp, gest in ((CASES[0], VPS[1], "dbl"), (CASES[0], VPS[0], "tap2"), (CASES[1], VPS[2], "triple")):
        row = run(browser, base, case, vp, gest, legacy=legacy)
        row["section"] = "control: tree before the fixes (06fa151) from memory"
        row["pass"] = not verdict(row)  # the control passes when the defect shows
        results["cases"].append(row)
        print(f"{'CONTROL-OK (defect shown)' if row['pass'] else 'CONTROL-NO-TEETH'} {case['name']:36} {row['viewport']:9} {gest:6} people {row['people_before']}->{row['people_after']} "
              f"nextId {row['nextId_before']}->{row['nextId_after']} blank {row['blank_people']}")
    fixed = [r for r in results["cases"] if r["section"] == "fixed tree"]
    ctrl = [r for r in results["cases"] if r["section"] != "fixed tree"]
    print(f"\nFIXED TREE: {sum(r['pass'] for r in fixed)} of {len(fixed)} rows pass; CONTROL: {sum(r['pass'] for r in ctrl)} of {len(ctrl)} show the defect")


if __name__ == "__main__":
    rc.run_probe("r1-sec01-matrix", body)
