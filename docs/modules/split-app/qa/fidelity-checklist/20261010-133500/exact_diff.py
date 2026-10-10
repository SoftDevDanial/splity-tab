"""Gate honesty, part 1: for each harness pair, count the pixels that differ at ANY level (threshold 0), not only above 0.01.

usage: python exact_diff.py <run folder> <output json name>
Reads golden.png and candidate.png of every <screen>-<viewport>/ folder in the run folder, plus report.json.
"""
import sys

sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

from common import dump

run = Path(sys.argv[1])
out_name = sys.argv[2]
rows = []
for folder in sorted(p for p in run.iterdir() if p.is_dir()):
    g_path, c_path, r_path = folder / "golden.png", folder / "candidate.png", folder / "report.json"
    if not (g_path.exists() and c_path.exists()):
        continue
    g = Image.open(g_path).convert("RGB")
    c = Image.open(c_path).convert("RGB")
    report = json.loads(r_path.read_text(encoding="utf-8"))
    ga, ca = np.asarray(g, dtype=np.int32), np.asarray(c, dtype=np.int32)
    same_size = g.size == c.size
    if same_size:
        delta = np.abs(ga - ca).max(axis=2)
        n_any = int((delta > 0).sum())
        max_delta = int(delta.max())
        if n_any:
            ys, xs = np.nonzero(delta)
            box = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
        else:
            box = None
    else:
        n_any, max_delta, box = None, None, None
    colours = len(np.unique(ga.reshape(-1, 3), axis=0))
    rows.append({
        "pair": folder.name,
        "golden_size": list(g.size), "candidate_size": list(c.size), "same_size": same_size,
        "harness_mismatch_pixels": report["mismatch_pixels"], "harness_threshold": report["threshold"],
        "dimensions_match": report["dimensions_match"],
        "pixels_differing_at_any_level": n_any, "max_channel_delta": max_delta, "differing_box": box,
        "golden_distinct_colours": colours,
        "golden_sha256": hashlib.sha256(g_path.read_bytes()).hexdigest()[:16],
        "candidate_sha256": hashlib.sha256(c_path.read_bytes()).hexdigest()[:16],
        "files_byte_identical": g_path.read_bytes() == c_path.read_bytes(),
    })
dump(out_name, rows)
for r in rows:
    print(f"{r['pair']:28} size {r['golden_size']} == {r['candidate_size']} {r['same_size']}  harness {r['harness_mismatch_pixels']}  any-level {r['pixels_differing_at_any_level']} (max {r['max_channel_delta']}) colours {r['golden_distinct_colours']} identical {r['files_byte_identical']}")
