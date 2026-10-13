"""Copy an app's final/checks/*.py into the scratchpad with the golden folder pointed at docs/design.

FINAL becomes <app>/docs/design, every FINAL.parent (or HERE.parent.parent) lookup of round-2/ and logo/ goes to
<app>/docs/design-explore/v1.1.0, and outputs (results.json, shots/, compare/, peek/) land beside the copy.
Usage: python -B rehome_checks.py <app root> <out dir>
"""
import sys
from pathlib import Path

app = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
out.mkdir(parents=True, exist_ok=True)
src = app / "docs/design-explore/v1.1.0/final/checks"
design = app / "docs/design"
explore = app / "docs/design-explore/v1.1.0"
for p in sorted(src.glob("*.py")):
    t = p.read_text(encoding="utf-8")
    n0 = t
    pin = f'FINAL = {{P}}(r"{design}")\nEXPLORE = {{P}}(r"{explore}")'
    t = t.replace("FINAL = HERE.parent\n", pin.replace("{P}", "Path" if "from pathlib import Path" in t else "pathlib.Path") + "\n")
    t = t.replace("FINAL.parent", "EXPLORE")
    t = t.replace('HERE.parent.parent / "round-2"', f'pathlib.Path(r"{explore}") / "round-2"')
    t = t.replace('HERE.parent / "system.css"', f'pathlib.Path(r"{design}") / "system.css"')
    (out / p.name).write_text(t, encoding="utf-8")
    print(f"{p.name}: {'patched' if t != n0 else 'unchanged'}")
