"""Regression QA, driven check for R40 (fidelity gate, "Looks right") and R41 (cold-boot live gate, "Works right").

Neither gate runs inside the suite, and each writes its own evidence under docs/modules/split-app/qa/, which this run may
not write to. So this script runs the gates' own code (tests/browser/fidelity/run.py main() and
tests/browser/live_e2e.py main()) unchanged, with only their EVIDENCE_ROOT pointed at this folder. Everything the gates
write lands under gates/ here. The fidelity harness ({sdlc}/harness/fidelity.py) is run as the
gate runs it, with --out inside gates/fidelity/.
Writes gates-run.txt here (a copy of everything printed) and reads the gates' own verdict files.
"""
import importlib.util
import json
import sys
from pathlib import Path

EVID = Path(__file__).resolve().parent
sys.path.insert(0, str(EVID))

import harness_common as hc  # noqa: E402  (also puts tests/browser on sys.path)

GATES = EVID / "gates"
LOG_PATH = EVID / "gates-run.txt"


class Tee:
    def __init__(self, stream, path):
        self.stream, self.file = stream, open(path, "w", encoding="utf-8")

    def write(self, text):
        self.stream.write(text)
        self.file.write(text)
        return len(text)

    def flush(self):
        self.stream.flush()
        self.file.flush()


def run_fidelity():
    path = hc.ROOT / "tests" / "browser" / "fidelity" / "run.py"
    spec = importlib.util.spec_from_file_location("fidelity_run", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.EVIDENCE_ROOT = GATES / "fidelity"
    print(f"HARNESS {module.HARNESS} exists {module.HARNESS.is_file()}", flush=True)
    code = module.main()
    return code


def run_live():
    import live_e2e
    live_e2e.EVIDENCE_ROOT = GATES / "live-e2e"
    code = live_e2e.main()
    return code


def main():
    GATES.mkdir(exist_ok=True)
    tee = Tee(sys.stdout, LOG_PATH)
    sys.stdout = tee
    started = hc.datetime_now() if hasattr(hc, "datetime_now") else None
    result = {"fidelity_exit": None, "live_exit": None}
    try:
        print("== R40 fidelity gate (tests/browser/fidelity/run.py, unchanged, evidence under gates/fidelity)", flush=True)
        result["fidelity_exit"] = run_fidelity()
        print("== R41 cold-boot live gate (tests/browser/live_e2e.py, unchanged, evidence under gates/live-e2e)", flush=True)
        result["live_exit"] = run_live()
    finally:
        sys.stdout = tee.stream
        tee.file.close()
    fidelity_folders = sorted(p for p in (GATES / "fidelity").glob("*") if p.is_dir())
    live_folders = sorted(p for p in (GATES / "live-e2e").glob("*") if p.is_dir())
    result["fidelity_run_folder"] = str(fidelity_folders[-1]) if fidelity_folders else None
    result["live_run_folder"] = str(live_folders[-1]) if live_folders else None
    if fidelity_folders:
        pairs = {}
        for pair in sorted(p for p in fidelity_folders[-1].glob("*") if p.is_dir()):
            report = pair / "report.json"
            pairs[pair.name] = json.loads(report.read_text(encoding="utf-8")) if report.is_file() else None
        result["fidelity_pairs"] = {name: (None if rep is None else {
            "dimensions_match": rep.get("dimensions_match"), "mismatch_pixels": rep.get("mismatch_pixels"),
            "mismatch_pct": rep.get("mismatch_pct")}) for name, rep in pairs.items()}
    if live_folders:
        summary = live_folders[-1] / "summary.json"
        result["live_summary"] = json.loads(summary.read_text(encoding="utf-8")) if summary.is_file() else None
    (EVID / "gates-summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print("gates-summary.json written", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
