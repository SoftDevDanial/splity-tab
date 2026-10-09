"""Reads results-p6-ghost-sweep.json and prints, per control, a one-line summary and every case that differs
from a single click (with the click events), so the full table of the sweep fits on a screen. Read-only."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "results-p6-ghost-sweep.json").read_text(encoding="utf-8"))
only = sys.argv[1:]
by_control = {}
for case in data["cases"]:
    by_control.setdefault(case["control"], []).append(case)

print(f"cases {len(data['cases'])}")
for name, cases in by_control.items():
    if only and name not in only:
        continue
    bad = [c for c in cases if not (c["data_equal_single"] and c["ui_equal_single"])]
    data_bad = [c for c in cases if not c["data_equal_single"]]
    print(f"\n== {name}: {len(cases)} cases, {len(bad)} differ from a single click, {len(data_bad)} differ in data, "
          f"{sum(1 for c in cases if c['problems'])} with problems")
    for c in cases:
        verdict = "data" if not c["data_equal_single"] else ("ui" if not c["ui_equal_single"] else "same")
        print(f"  {c['viewport']:9} {c['gesture']:6} -> {verdict:5} equal-to-initial={c['data_equal_initial']}")
        if verdict != "same" or only:
            for line in c["events"]:
                print("        ", line)
            if verdict == "data":
                print("         single:", c["single"]["people"], [i["name"] for i in c["single"]["items"]], c["single"]["focus"])
                print("         after :", c["after"]["people"], [i["name"] for i in c["after"]["items"]], c["after"]["focus"])
