"""Re-check item 4: the audit's 123-row ghost-click sweep, once, on the fixed tree.

The audit's script (qa/security/20261009-201702/p6_ghost_sweep.py) is imported read only and run unchanged: 21 controls, mouse double
click at 360x640, 390x844 and 1280x800, triple click at 360x640 and 1280x800, double tap at 360x640 and 390x844 (the 8 variant controls
run a double click at the three sizes and a double tap at 360x640), each against a single click on a fresh context. rc.py adds a CSP
violation read to every row's `problems`. The summary at the end separates data differences from UI-only differences.
Accepted by the brief: the toggles differ in data by design (two flips), and UI-only differences on the mode labels and Dismiss note.
"""
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rc  # noqa: E402

import p6_ghost_sweep  # noqa: E402  (the audit's script, read only)

results = rc.run_probe("r4-ghost-sweep", p6_ghost_sweep.body)

by_control = defaultdict(list)
for row in results["cases"]:
    by_control[row["control"]].append(row)
print("\n=== summary: rows per control against a single click ===")
total = data_diff = ui_diff = problems = 0
unexpected_data = []
for name, rows in by_control.items():
    d = [r for r in rows if not r["data_equal_single"]]
    u = [r for r in rows if r["data_equal_single"] and not r["ui_equal_single"]]
    total += len(rows)
    data_diff += len(d)
    ui_diff += len(u)
    problems += sum(1 for r in rows if r["problems"])
    if name != "toggle":
        unexpected_data += d
    print(f"{name:28} rows {len(rows):2}  differ in data {len(d):2}  differ in UI only {len(u):2}")
    for r in d + u:
        print(f"      {'DATA' if r in d else 'UI  '} {r['viewport']:9} {r['gesture']:6} after focus {r['after']['focus']!r} single focus {r['single']['focus']!r} "
              f"people {len(r['after']['people'])} vs {len(r['single']['people'])}, items {len(r['after']['items'])} vs {len(r['single']['items'])}, "
              f"dialogOpen {r['after']['dialogOpen']} vs {r['single']['dialogOpen']}")
print(f"TOTAL rows {total}, differ in data {data_diff}, differ in UI only {ui_diff}, rows with a console error, page error, CSP violation or foreign request: {problems}")
print(f"DATA differences on any control other than the toggles: {len(unexpected_data)}")
