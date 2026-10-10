"""Reads the harness's own styles.json of every pair in a gate run folder and compares the golden side with the candidate side element by
element (path, text, rectangle, the 27 computed properties the harness dumps). The qa.md Per-element check names this file.

The harness's `text` is textContent with white space collapsed, cut at 80 characters. So two things move the cut and are NOT differences:
the white space the goldens keep between elements (allowed difference 5), and the text of the app's `hidden` blocks (textContent counts
display:none children, allowed difference 7). A text difference is therefore classed as `window` when the two texts agree up to the
shorter one once white space is removed, and as `hidden-block` when it sits on one of the three containers that hold the hidden block
(div.app, main.layout, div.inputs). Anything else is `other` and would be a finding.

usage: python styles_json_diff.py <run folder> <output json name>
"""
import sys

sys.dont_write_bytecode = True
import difflib
import json
from pathlib import Path

from common import dump

run = Path(sys.argv[1])
out_name = sys.argv[2]
HIDDEN_HOLDERS = {"div.app", "main.layout", "div.inputs"}
rows = []
for folder in sorted(p for p in run.iterdir() if p.is_dir()):
    sj = folder / "styles.json"
    if not sj.exists():
        continue
    data = json.loads(sj.read_text(encoding="utf-8"))
    g, c = data["golden"], data["candidate"]
    sm = difflib.SequenceMatcher(a=[e["path"] for e in g], b=[e["path"] for e in c], autojunk=False)
    only_g, only_c, rect_d, text_d, style_d, paired = [], [], [], [], [], 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for i, j in zip(range(i1, i2), range(j1, j2)):
                paired += 1
                a, b = g[i], c[j]
                if a["rect"] != b["rect"]:
                    rect_d.append([a["path"], a["rect"], b["rect"]])
                ta, tb = (a.get("text") or "").replace(" ", ""), (b.get("text") or "").replace(" ", "")
                if ta != tb:
                    n = min(len(ta), len(tb))
                    kind = "window" if ta[:n] == tb[:n] else ("hidden-block" if a["path"] in HIDDEN_HOLDERS else "other")
                    text_d.append({"path": a["path"], "kind": kind})
                sd = {k: [a["styles"][k], b["styles"].get(k)] for k in a["styles"] if a["styles"][k] != b["styles"].get(k)}
                if sd:
                    style_d.append([a["path"], sd])
        else:
            only_g += [g[i]["path"] for i in range(i1, i2)]
            only_c += [c[j]["path"] for j in range(j1, j2)]
    kinds = {}
    for t in text_d:
        kinds[t["kind"]] = kinds.get(t["kind"], 0) + 1
    rows.append({"pair": folder.name, "golden_elements": len(g), "candidate_elements": len(c), "paired": paired, "golden_only": only_g, "candidate_only": only_c,
                 "rect_diffs": len(rect_d), "text_diffs": kinds, "style_diffs": len(style_d), "style_diff_detail": style_d[:3]})
dump(out_name, rows)
for r in rows:
    print(f"{r['pair']:28} elements {r['golden_elements']}/{r['candidate_elements']} paired {r['paired']} golden-only {r['golden_only']} candidate-only {r['candidate_only']} rect {r['rect_diffs']} text {r['text_diffs']} style {r['style_diffs']} {r['style_diff_detail']}")
