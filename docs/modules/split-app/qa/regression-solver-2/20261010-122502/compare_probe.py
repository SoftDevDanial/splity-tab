"""Compares the probe run on the fixed tree (toggle-remove-fixed.json, this folder) with the re-check's run on HEAD a6cbbf8
(toggle-remove-head.json, qa/regression-recheck/20261009-230750/). Reads two JSON files, writes nothing.

Same layouts and same example point per configuration means the two runs pressed the same pixels, so the only thing that differs is the
tree. Then: how many of the affected layouts lost an item to the real double click and to the single click, on each tree, and in how many
the double click left exactly the bill that the single click leaves.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECHECK = HERE.parent.parent / "regression-recheck" / "20261009-230750"
mine = json.loads((HERE / "toggle-remove-fixed.json").read_text(encoding="utf-8"))["rows"]
head = json.loads((RECHECK / "toggle-remove-head.json").read_text(encoding="utf-8"))["rows"]


def lost(rows, kind):
    return sum(1 for r in rows if r["points_onto_a_remove"] and r[kind]["items_after"] < r[kind]["items_before"])


key = lambda r: (r["names"], r["people"], r["width"])
same = len(mine) == len(head) and all(
    key(a) == key(b) and a["points_onto_a_remove"] == b["points_onto_a_remove"] and a.get("example") == b.get("example")
    for a, b in zip(mine, head))
affected = [r for r in mine if r["points_onto_a_remove"]]
print(f"configurations: fixed {len(mine)}, HEAD a6cbbf8 {len(head)}; same layout scan and same example point in every one: {same}")
print(f"affected layouts (a chip point lands on its own item's Remove once the error shows): fixed {len(affected)}, "
      f"HEAD {sum(1 for r in head if r['points_onto_a_remove'])}")
print(f"real double click removed an item: HEAD {lost(head, 'dbl')} of {len(affected)}, fixed {lost(mine, 'dbl')} of {len(affected)}")
print(f"single click removed an item:      HEAD {lost(head, 'single')} of {len(affected)}, fixed {lost(mine, 'single')} of {len(affected)}")
print(f"fixed tree: the double click left exactly the bill that the single click leaves in "
      f"{sum(1 for r in affected if r['dbl']['after'] == r['single']['after'])} of {len(affected)}")
print(f"page errors during the affected runs, fixed tree: {sum(len(r[k]['page_errors']) for r in affected for k in ('dbl', 'single'))}")
