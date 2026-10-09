"""Re-runs the project's own fidelity runner (tests/browser/fidelity/run.py, unmodified) with the evidence folder
pointed at this QA run. Same commands, same flags, same server lifecycle; only the output root differs.
"""
import importlib.util
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
RUNNER = Path("{workspace}/examples/split/tests/browser/fidelity/run.py")

spec = importlib.util.spec_from_file_location("fidelity_run", RUNNER)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.EVIDENCE_ROOT = OUT / "fidelity"
sys.exit(module.main())
