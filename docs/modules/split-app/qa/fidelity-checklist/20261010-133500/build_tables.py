"""Turns the row JSON files into the tables of the report. Reads rows_screens.json, rows_states.json, interactions.json,
static_checks.json and the qa.md checklist text; writes checklist_table.md (compact) and checklist_full.md (every measured string)
into this folder. Nothing outside the evidence folder is written.

usage: python build_tables.py
"""
import sys

sys.dont_write_bytecode = True
import json
import re

import common as C
from rows_lib import fmt


def load(name):
    return json.loads((C.HERE / name).read_text(encoding="utf-8"))


def squeeze(text):
    """A shorter measured string: drop the golden marker (reported once per row) and common noise."""
    text = text.replace(", = golden", "").replace(" = golden", "")
    text = re.sub(r"\s+", " ", text)
    return text


def row_cell(by_vp):
    """Compact measured cell: the first viewport in full, later viewports only where their text differs."""
    vps = sorted(by_vp, key=lambda v: int(v))
    base = {squeeze(t) for _, t in by_vp[vps[0]]}
    parts = []
    first = vps[0]
    parts.append(f"{first}: " + " ; ".join(squeeze(t) for _, t in by_vp[first]))
    for vp in vps[1:]:
        diff = [squeeze(t) for _, t in by_vp[vp] if squeeze(t) not in base]
        parts.append(f"{vp}: " + (" ; ".join(diff) if diff else "as " + first))
    return " | ".join(parts)


def main():
    qa = load("rows_screens.json")["qa"]
    all_rows = {}
    for f in ("rows_screens.json", "rows_states.json", "interactions.json"):
        all_rows.update(load(f)["rows"])
    lines_c, lines_f = [], []
    order = sorted(all_rows, key=lambda r: (r.split("-")[0], int(r.split("-")[1])))
    verdicts = {}
    for rid in order:
        by = all_rows[rid]
        ok = all(o for v in by.values() for o, _ in v)
        eq = all(("= golden" in t or "DIFFERS" not in t) for v in by.values() for _, t in v)
        verdicts[rid] = ok
        element = qa.get(rid, ("(finder row)", ""))[0]
        lines_c.append(f"| {rid} | {element} | {'PASS' if ok else 'FAIL'} | {row_cell(by)} |")
        for vp in sorted(by, key=int):
            for o, t in by[vp]:
                lines_f.append(f"{rid} {vp} {'PASS' if o else 'FAIL'} {t}")
    (C.HERE / "checklist_table.md").write_text("\n".join(lines_c) + "\n", encoding="utf-8")
    (C.HERE / "checklist_full.md").write_text("\n".join(lines_f) + "\n", encoding="utf-8")
    total = len(order)
    passed = sum(verdicts.values())
    by_prefix = {}
    for rid, ok in verdicts.items():
        p = rid.split("-")[0]
        by_prefix.setdefault(p, [0, 0])
        by_prefix[p][1] += 1
        by_prefix[p][0] += int(ok)
    print(f"rows {total}, pass {passed}, by prefix {by_prefix}")
    missing = sorted(set(qa) - set(all_rows))
    print("qa.md checklist ids with no result:", missing)
    n = sum(len(l) for l in lines_c)
    print("compact table characters:", n)


if __name__ == "__main__":
    main()
