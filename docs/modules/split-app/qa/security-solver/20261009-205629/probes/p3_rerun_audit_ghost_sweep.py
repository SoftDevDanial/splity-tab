"""Re-runs the security audit's own ghost-click sweep (123 rows, 21 controls) on the fixed tree, unchanged.

The audit's script and helper are imported read-only from qa/security/20261009-201702/ (no bytecode written there). Only the
folder that receives results-p6-ghost-sweep-after.json is switched to this folder. Then it prints, per control, how many rows
equal a single click in data and in UI, and lists every row that does not. The audit found 13 rows that differ in data
(5 toggles, by design, and 8 of SEC-01) and 46 that differ in UI only. Run: python -B probes/p3_rerun_audit_ghost_sweep.py
"""
import sys
from collections import defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
AUDIT = HERE.parents[2] / "security" / "20261009-201702"
sys.path.insert(0, str(AUDIT))
import common as audit_common  # noqa: E402  (the audit's helper, read only)

audit_common.HERE = HERE  # the results file lands here, not in the audit's folder
import p6_ghost_sweep  # noqa: E402

results = audit_common.run_probe("p6-ghost-sweep-after", p6_ghost_sweep.body)

by_control = defaultdict(list)
for row in results["cases"]:
    by_control[row["control"]].append(row)
print("\n=== summary: rows per control that equal a single click ===")
total = data_diff = ui_diff = problems = 0
for name, rows in by_control.items():
    d = [r for r in rows if not r["data_equal_single"]]
    u = [r for r in rows if r["data_equal_single"] and not r["ui_equal_single"]]
    total += len(rows); data_diff += len(d); ui_diff += len(u); problems += sum(1 for r in rows if r["problems"])
    print(f"{name:28} rows {len(rows):2}  differ in data {len(d):2}  differ in UI only {len(u):2}")
    for r in d + u:
        print(f"      {'DATA' if r in d else 'UI  '} {r['viewport']:9} {r['gesture']:6} after focus {r['after']['focus']!r} single focus {r['single']['focus']!r} "
              f"people {len(r['after']['people'])} vs {len(r['single']['people'])}, items {len(r['after']['items'])} vs {len(r['single']['items'])}, "
              f"dialogOpen {r['after']['dialogOpen']} vs {r['single']['dialogOpen']}")
print(f"TOTAL rows {total}, differ in data {data_diff}, differ in UI only {ui_diff}, rows with a console error, page error or foreign request: {problems}")
