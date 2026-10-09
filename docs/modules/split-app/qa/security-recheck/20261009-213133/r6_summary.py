"""Reads the results-*.json files of this folder and prints the counts quoted in evidence.md and recheck-section.md. Writes nothing."""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    return json.loads((HERE / f"results-{name}.json").read_text(encoding="utf-8"))


total = 0
for name in ("r1-sec01-matrix", "r2-i1-new-bill", "r3-overswallow", "r3b-followups", "r3c-sec04-impact", "r4-ghost-sweep", "r5-csp-live", "r7-partb-and-touch-near"):
    data = load(name)
    cases = data["cases"]
    total += len(cases)
    passes = Counter(str(c.get("pass")) for c in cases)
    print(f"{name:24} rows {len(cases):3}  pass field {dict(passes)}  server pid {data['server_pid']} port {data['port']}  chromium {data.get('chromium')}")
print("TOTAL rows", total)

sweep = load("r4-ghost-sweep")["cases"]
print("\nsweep rows", len(sweep))
for r in [r for r in sweep if r["control"] == "toggle"]:
    print(f"  toggle {r['viewport']:9} {r['gesture']:6} data==single {r['data_equal_single']!s:5} data==initial (flipped back) {r['data_equal_initial']!s:5}")
print("UI-only differences by control:", dict(Counter(r["control"] for r in sweep if r["data_equal_single"] and not r["ui_equal_single"])))
print("data differences by control:", dict(Counter(r["control"] for r in sweep if not r["data_equal_single"])))
dialog = [r for r in sweep if r["control"] in ("new-bill", "start-new-bill", "cancel", "backdrop-corner", "backdrop-over-add-person")]
print("dialog controls (rows, data==single and ui==single):", Counter(r["control"] for r in dialog), "all equal:", all(r["data_equal_single"] and r["ui_equal_single"] for r in dialog))
print("new-bill rows (viewport, gesture, dialog open after, open after a single click, focus):",
      [(r["viewport"], r["gesture"], r["after"]["dialogOpen"], r["single"]["dialogOpen"], r["after"]["focus"]) for r in sweep if r["control"] == "new-bill"])
print("rows with a console error, page error, CSP violation or foreign request:", sum(1 for r in sweep if r["problems"]))
removes = [r for r in sweep if r["control"].startswith("remove-")]
print("remove rows:", len(removes), "all data==single:", all(r["data_equal_single"] for r in removes), "all ui==single:", all(r["ui_equal_single"] for r in removes),
      "blank people:", sum(1 for r in removes if any(p == "" for p in r["after"]["people"])))
stray = [(r["control"], r["viewport"], r["gesture"], e) for r in sweep if not r["control"].startswith("remove-") for e in r["events"] if "Remove" in e]
print("sweep click events from non-Remove controls that touched a Remove button:", len(stray))
