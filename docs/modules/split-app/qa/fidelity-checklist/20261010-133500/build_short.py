"""Shortens the measured strings of the checklist rows for the report table (checklist_short.md in this folder).

Keeps the numbers and colours (as token names), drops attribute noise that every row repeats (type, autocomplete, aria-hidden, viewBox...).
Every full string stays in checklist_full.md.

usage: python build_short.py
"""
import sys

sys.dont_write_bytecode = True
import json
import re

import common as C

DROP_KEYS = {"@type", "@autocomplete", "@placeholder", "@aria-hidden", "@viewBox", "@focusable", "@inputmode", "@role", "@scope", "@for", "@name",
             "@value", "@aria-invalid", "cls", "tag", "disabled", "cursor", "focused", "focusVisible"}
TOKEN = {C.rgb(k): k for k in C.TOKENS}


def short_entry(text):
    text = text.replace(", = golden", "").replace(" = golden", "")
    m = re.match(r"^(.*?): (.*)$", text)
    if not m or "=" not in m.group(2):
        return re.sub(r"\s+", " ", text)
    label, rest = m.group(1), m.group(2)
    parts = []
    for kv in re.split(r", (?=[@\w:-]+=)", rest):
        k = kv.split("=", 1)[0]
        if k in DROP_KEYS:
            continue
        for rgbv, name in TOKEN.items():
            kv = kv.replace(rgbv, name)
        kv = re.sub(r"\btext=(.{0,34}).*", lambda mm: "text=" + mm.group(1), kv) if kv.startswith("text=") else kv
        parts.append(kv)
    label = re.sub(r"^(item|person|row|check|head) ", lambda mm: mm.group(1) + " ", label)
    return f"{label}: " + ", ".join(parts)


def main():
    rows = {}
    for f in ("rows_screens.json", "rows_states.json"):
        rows.update(json.loads((C.HERE / f).read_text(encoding="utf-8"))["rows"])
    qa = json.loads((C.HERE / "rows_screens.json").read_text(encoding="utf-8"))["qa"]
    out = []
    for rid in sorted(rows, key=lambda r: (r.split("-")[0], int(r.split("-")[1]))):
        by = rows[rid]
        vps = sorted(by, key=int)
        first = vps[0]
        seen = {short_entry(t) for _, t in by[first]}
        cell = f"{first}: " + " ; ".join(short_entry(t) for _, t in by[first])
        for vp in vps[1:]:
            diff = [short_entry(t) for _, t in by[vp] if short_entry(t) not in seen]
            cell += f" || {vp}: " + (" ; ".join(diff) if diff else "same as " + first)
        ok = all(o for v in by.values() for o, _ in v)
        out.append(f"| {rid} | {qa.get(rid, ('', ''))[0]} | {'PASS' if ok else 'FAIL'} | {cell} |")
    (C.HERE / "checklist_short.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(len(out), sum(len(x) for x in out))


if __name__ == "__main__":
    main()
