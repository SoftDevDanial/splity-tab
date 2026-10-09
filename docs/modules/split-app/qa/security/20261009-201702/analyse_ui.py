"""Prints, for every case of the ghost sweep whose UI state differs from a single click, which UI keys differ
(dialog open, note, status line, focused control). Read-only on results-p6-ghost-sweep.json."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "results-p6-ghost-sweep.json").read_text(encoding="utf-8"))
seen = {}
for case in data["cases"]:
    if case["ui_equal_single"] and case["data_equal_single"]:
        continue
    keys = ["dialogOpen", "note", "status", "focus"]
    diffs = {k: (case["single"][k], case["after"][k]) for k in keys if case["single"][k] != case["after"][k]}
    sig = (case["control"], case["gesture"], json.dumps(diffs, sort_keys=True))
    seen.setdefault(sig, []).append(case["viewport"])
for (control, gesture, diffs), viewports in seen.items():
    print(f"{control:26} {gesture:6} {','.join(viewports):28} single->after {diffs}")
