"""Runs tests/browser/live_e2e.py unchanged, but into a scratch folder of this evidence folder.

The gate writes to EVIDENCE_ROOT (the official qa/live-e2e/ folder). This driver imports the gate as a module and points that one
variable at live-gate-check/ next to this script, then calls main(). Nothing in the product or in the official folder is touched.
Same approach as the security solver's p5_live_gate_scratch.py. Exit status is the gate's: 0 when 7 of 7 steps pass.
Run from the project root: python -B <this file>
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT / "tests" / "browser"))
import live_e2e  # noqa: E402

live_e2e.EVIDENCE_ROOT = HERE / "live-gate-check"
sys.exit(live_e2e.main())
