"""Extra pixel runs the gate does not make: the same harness, the same flags and setup scripts as tests/browser/fidelity/run.py,
at 360x780, 600x900 and 1024x768 (the gate only does 390x844 and 1280x800). Not part of the gate. Evidence for the layouts
the spec names (360, 390, 600, 1024, 1280).

usage: python extra_pixel.py
Writes <HERE>/extra-<w>x<h>/<screen>/ for each pair, then exact_diff-style counts into extra_pixel.json.
"""
import sys

sys.dont_write_bytecode = True
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

import common as C

HARNESS = Path("{sdlc}/harness/fidelity.py")
VIEWPORTS = ["360x780", "600x900", "1024x768"]
SCREEN_SETUP = (
    ("bill-empty", None, None),
    ("bill-even", "seed-s2.js", None),
    ("bill-items", "seed-s1.js", None),
    ("bill-unassigned", "seed-s5.js", None),
    ("new-bill-dialog", "seed-s2.js", "open-new-bill.js"),
)


def main():
    server = C.rig.StaticServer(C.ROOT, say=print)
    rows = []
    try:
        server.start()
        for vp in VIEWPORTS:
            for screen, seed, after in SCREEN_SETUP:
                out = C.HERE / f"extra-{vp}" / screen
                cmd = [sys.executable, str(HARNESS), "--golden", f"./docs/design/{screen}.html", "--candidate", f"{server.base}/",
                       "--viewport", vp, "--dpr", "1", "--color-scheme", "light", "--browser-arg=--disable-lcd-text",
                       "--fixed-time", "2026-10-08T09:00:00", "--threshold", "0.01"]
                if seed:
                    cmd += ["--candidate-init-script", f"./tests/browser/fidelity/{seed}"]
                if after:
                    cmd += ["--candidate-after-load", f"./tests/browser/fidelity/{after}"]
                cmd += ["--out", str(out)]
                done = subprocess.run(cmd, cwd=C.ROOT, capture_output=True, text=True, timeout=180)
                report = json.loads((out / "report.json").read_text(encoding="utf-8"))
                g = np.asarray(Image.open(out / "golden.png").convert("RGB"), dtype=np.int32)
                c = np.asarray(Image.open(out / "candidate.png").convert("RGB"), dtype=np.int32)
                if g.shape == c.shape:
                    delta = np.abs(g - c).max(axis=2)
                    any_level, mx = int((delta > 0).sum()), int(delta.max())
                else:
                    any_level, mx = None, None
                rows.append({"viewport": vp, "screen": screen, "exit": done.returncode,
                             "harness_mismatch_pixels": report["mismatch_pixels"], "dimensions_match": report["dimensions_match"],
                             "golden_size": report["golden_size"], "candidate_size": report["candidate_size"],
                             "any_level_pixels": any_level, "max_channel_delta": mx})
                r = rows[-1]
                print(f"{vp:9} {screen:16} harness {r['harness_mismatch_pixels']:4} any-level {r['any_level_pixels']} (max {r['max_channel_delta']}) dims {r['dimensions_match']} {r['golden_size']} / {r['candidate_size']}")
    finally:
        server.stop()
    C.dump("extra_pixel.json", rows)


if __name__ == "__main__":
    main()
