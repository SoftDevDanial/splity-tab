"""Gate honesty, part 3: the M1 question under the HARNESS's own rendering conditions.

m1_native.py used my own screenshots. Here the harness's own render() function (imported from the unmodified fidelity.py, with the same flags
as the gate: --disable-lcd-text, fixed time 2026-10-08T09:00:00, light, dpr 1, full page, reduced motion, CSP bypassed, its freeze stylesheet) renders
the GOLDEN new-bill-dialog.html after a small after-load script turned its static dialog into a native modal. That picture is then compared with
the candidate.png the gate wrote for the app. The golden file is never written, the change is made in memory in the page only.

usage: python m1_native_harness.py <gate run folder>
"""
import sys

sys.dont_write_bytecode = True
import importlib.util
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

import common as C

HARNESS = Path("{sdlc}/harness/fidelity.py")
spec = importlib.util.spec_from_file_location("sdlc_fidelity", HARNESS)
fid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fid)

NATIVE_AFTER_LOAD = """
const b = document.querySelector('.backdrop'); if (b) b.remove();
const app = document.querySelector('.app'); if (app) app.removeAttribute('inert');
const d = document.querySelector('dialog'); d.removeAttribute('open'); d.showModal();
document.activeElement && document.activeElement.blur && document.activeElement.blur();
"""


def main():
    run = Path(sys.argv[1])
    rows = []
    out_dir = C.HERE / "m1_native_harness"
    out_dir.mkdir(exist_ok=True)
    with sync_playwright() as pw:
        for vp in ((390, 844), (1280, 800)):
            png = out_dir / f"golden-native-{vp[0]}x{vp[1]}.png"
            styles, size = fid.render(pw, str(C.DESIGN / "new-bill-dialog.html"), vp, 1.0, png, True, "light", ["--disable-lcd-text"],
                                      after_load=NATIVE_AFTER_LOAD, fixed_time="2026-10-08T09:00:00")
            gate_candidate = run / f"new-bill-dialog-{vp[0]}x{vp[1]}" / "candidate.png"
            gate_golden = run / f"new-bill-dialog-{vp[0]}x{vp[1]}" / "golden.png"
            a = np.asarray(Image.open(png).convert("RGB"), dtype=np.int32)
            c = np.asarray(Image.open(gate_candidate).convert("RGB"), dtype=np.int32)
            g = np.asarray(Image.open(gate_golden).convert("RGB"), dtype=np.int32)
            def diff(x, y):
                if x.shape != y.shape:
                    return {"size_differs": [list(x.shape[:2]), list(y.shape[:2])]}
                d = np.abs(x - y).max(axis=2)
                return {"any_level": int((d > 0).sum()), "max_delta": int(d.max())}
            rows.append({"viewport": f"{vp[0]}x{vp[1]}", "native_golden_vs_gate_candidate": diff(a, c), "native_golden_vs_gate_golden": diff(a, g), "gate_golden_vs_gate_candidate": diff(g, c)})
            print(rows[-1])
    C.dump("m1_native_harness.json", rows)


if __name__ == "__main__":
    main()
