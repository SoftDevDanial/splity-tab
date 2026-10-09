"""Counts for the ghost sweep (results-p6-ghost-sweep.json) and a row count for every results file. Read-only."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
sweep = json.loads((HERE / "results-p6-ghost-sweep.json").read_text(encoding="utf-8"))["cases"]
data_diff = [c for c in sweep if not c["data_equal_single"]]
ui_only = [c for c in sweep if c["data_equal_single"] and not c["ui_equal_single"]]
same = [c for c in sweep if c["data_equal_single"] and c["ui_equal_single"]]
print(f"ghost sweep rows {len(sweep)}: same as a single click {len(same)}, UI-only difference {len(ui_only)}, data difference {len(data_diff)}")
by_control = {}
for c in data_diff:
    by_control.setdefault(c["control"], []).append(f"{c['viewport']}/{c['gesture']}")
for control, rows in by_control.items():
    print(f"  data differs: {control}: {len(rows)} rows {rows}")
by_ui = {}
for c in ui_only:
    by_ui.setdefault(c["control"], 0)
    by_ui[c["control"]] += 1
print("  ui-only rows by control:", by_ui)
print("  rows with console/page/request problems:", sum(1 for c in sweep if c["problems"]))
print("  controls:", len({c["control"] for c in sweep}), "viewports:", sorted({c["viewport"] for c in sweep}), "gestures:", sorted({c["gesture"] for c in sweep}))
total = 0
for path in sorted(HERE.glob("results-*.json")):
    cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
    total += len(cases)
    print(f"{path.name:34} {len(cases):4} rows")
print("total result rows", total)
