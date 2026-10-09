"""Fidelity gate runner (qa.md, "Fidelity gate"). Run from the project root: python tests/browser/fidelity/run.py

Serves the app, then runs the unmodified sdlc harness (fidelity.py) once per golden screen and width, ten runs,
each into its own folder under docs/modules/split-app/qa/fidelity/<YYYYMMDD-HHMMSS>/<screen>-<viewport>/.
The harness is started with sys.executable (CG-11): the Python that runs this script must hold Playwright,
Pillow and numpy. No virtual environment is made and nothing is installed. This file adds no rendering or diff
logic. It only manages the server, builds the command lines and reads each report.json for the verdict.

A pair passes only when report.json has "dimensions_match": true and "mismatch_pixels": 0. A non-zero count is a
finding for the human, never something to hide with a higher --threshold.
Exit status: 0 when all ten pairs pass, 1 otherwise.
"""
import datetime
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # rig.py sits next to the browser tests
import rig  # noqa: E402

HARNESS = Path("{sdlc}/harness/fidelity.py")
EVIDENCE_ROOT = rig.ROOT / "docs" / "modules" / "split-app" / "qa" / "fidelity"
VIEWPORTS = ("390x844", "1280x800")
# (golden, seed script for --candidate-init-script, after-load script for --candidate-after-load)
SCREENS = (
    ("bill-empty", None, None),
    ("bill-even", "seed-s2.js", None),
    ("bill-items", "seed-s1.js", None),
    ("bill-unassigned", "seed-s5.js", None),
    ("new-bill-dialog", "seed-s2.js", "open-new-bill.js"),
)
FIXED_TIME = "2026-10-08T09:00:00"
THRESHOLD = "0.01"
RUN_TIMEOUT_SECONDS = 180


def command(base_url, screen, seed, after_load, viewport, out):
    cmd = [sys.executable, str(HARNESS),
           "--golden", f"./docs/design/{screen}.html", "--candidate", f"{base_url}/",
           "--viewport", viewport, "--dpr", "1", "--color-scheme", "light",
           "--browser-arg=--disable-lcd-text",  # the top-layer dialog would otherwise get greyscale text only on one side
           "--fixed-time", FIXED_TIME, "--threshold", THRESHOLD]
    if seed:
        cmd += ["--candidate-init-script", f"./tests/browser/fidelity/{seed}"]
    if after_load:
        cmd += ["--candidate-after-load", f"./tests/browser/fidelity/{after_load}"]
    return cmd + ["--out", str(out)]


def run_pair(base_url, screen, seed, after_load, viewport, run_folder, log):
    out = run_folder / f"{screen}-{viewport}"
    cmd = command(base_url, screen, seed, after_load, viewport, out)
    log(f"$ {' '.join(cmd)}")
    try:
        done = subprocess.run(cmd, cwd=rig.ROOT, capture_output=True, text=True, timeout=RUN_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        log(f"  harness did not finish within {RUN_TIMEOUT_SECONDS} s")
        return {"screen": screen, "viewport": viewport, "passed": False, "why": "timeout"}
    for line in (done.stdout + done.stderr).strip().splitlines():
        log(f"  {line}")
    try:
        report = json.loads((out / "report.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"screen": screen, "viewport": viewport, "passed": False, "why": f"no report (exit {done.returncode})"}
    passed = done.returncode == 0 and report["dimensions_match"] is True and report["mismatch_pixels"] == 0
    return {"screen": screen, "viewport": viewport, "passed": passed, "pixels": report["mismatch_pixels"],
            "pct": report["mismatch_pct"], "dimensions_match": report["dimensions_match"],
            "golden_size": report["golden_size"], "candidate_size": report["candidate_size"]}


def main():
    if not HARNESS.is_file():
        sys.exit(f"harness not found: {HARNESS}")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_folder = EVIDENCE_ROOT / stamp
    run_folder.mkdir(parents=True, exist_ok=True)
    lines = []

    def log(text):
        print(text, flush=True)
        lines.append(text)

    log(f"fidelity gate {stamp}, python {sys.executable}, harness {HARNESS}")
    results = []
    server = rig.StaticServer(rig.ROOT, say=log)
    try:
        server.start()
        for screen, seed, after_load in SCREENS:
            for viewport in VIEWPORTS:
                results.append(run_pair(server.base, screen, seed, after_load, viewport, run_folder, log))
    finally:
        server.stop()
        (run_folder / "run.log").write_text("\n".join(lines) + "\n", encoding="utf-8")
    log("")
    for result in results:
        verdict = "PASS" if result["passed"] else "FAIL"
        detail = (f"{result['pixels']} mismatching pixels ({result['pct']}%), sizes {result['golden_size']} / {result['candidate_size']}"
                  if "pixels" in result else result["why"])
        log(f"{verdict}  {result['screen']:16} {result['viewport']:9} {detail}")
    failed = [r for r in results if not r["passed"]]
    log(f"{len(results) - len(failed)} of {len(results)} pairs pass, evidence in {run_folder}")
    (run_folder / "run.log").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 1 if failed or len(results) != len(SCREENS) * len(VIEWPORTS) else 0


if __name__ == "__main__":
    sys.exit(main())
