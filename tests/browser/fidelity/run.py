"""Fidelity gate runner (qa.md, "Fidelity gate"). Run from the project root: python tests/browser/fidelity/run.py

Serves the app, then runs the unmodified sdlc harness (fidelity.py) for the two CONTROLS and then once per pair of
PAIRS, the 40 state and width pairs of qa.md, each into its own folder under
docs/modules/split-app/qa/fidelity/<YYYYMMDD-HHMMSS>/ with run.log beside them. Chromium only, as the goldens are
Chromium renders and the harness has no other browser (R40, R58).
The harness is started with sys.executable (CG-11): the Python that runs this script must hold Playwright,
Pillow and numpy. No virtual environment is made and nothing is installed. This file adds no rendering or diff
logic. It only manages the server, builds the command lines and reads each report.json for the verdict.

The controls run first. If one does not behave as qa.md says, the run stops with a CONTROL FAIL line and its verdict
is NOT RUN. A pair passes only when the harness exits 0 and report.json has "dimensions_match": true and
"mismatch_pixels": 0. A non-zero count is a finding for the human, never something to hide with a higher --threshold.
Exit status: 0 when both controls behave and every pair passes, 1 otherwise. Set SDLC_HARNESS to run a harness other
than the default.
"""
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # rig.py sits next to the browser tests
import rig  # noqa: E402

DEFAULT_HARNESS = Path("{sdlc}/harness/fidelity.py")


def harness_path(environ=os.environ):
    """The harness to run: SDLC_HARNESS when it is set and not blank, else the plugin copy on the owner's machine."""
    return Path(environ.get("SDLC_HARNESS") or DEFAULT_HARNESS)


HARNESS = harness_path()
EVIDENCE_ROOT = rig.ROOT / "docs" / "modules" / "split-app" / "qa" / "fidelity"
PHONES = ("390x844", "360x780")
ALL_WIDTHS = (*PHONES, "1280x800")
# qa.md "Fidelity gate", the table: golden, seed script (--candidate-init-script), after-load script
# (--candidate-after-load) and viewports. bill-empty has no seed, as each render is a fresh browser that boots cold.
SCREENS = (
    ("bill-items", "seed-s1.js", None, ALL_WIDTHS),
    ("bill-items-open", "seed-s1.js", "open-sections.js", PHONES),
    ("bill-even", "seed-s2.js", None, ALL_WIDTHS),
    ("spare-sen", "seed-s1.js", "open-spare.js", ALL_WIDTHS),
    ("spare-sen-one", "seed-one.js", "open-spare.js", ALL_WIDTHS),
    ("spare-sen-random", "seed-rnd.js", "open-spare.js", ALL_WIDTHS),
    ("splits-sheet", "seed-s1.js", "open-splits.js", PHONES),
    ("new-bill-dialog", "seed-s1.js", "open-new-bill.js", ALL_WIDTHS),
    ("bill-empty", None, None, ALL_WIDTHS),
    ("rate-error", "seed-re.js", None, ALL_WIDTHS),
    ("bill-unassigned", "seed-s5.js", None, ALL_WIDTHS),
    ("bill-unreadable", "seed-b1.js", None, ALL_WIDTHS),
    ("bill-twelve", "seed-t12.js", None, ALL_WIDTHS),
    ("bill-large", "seed-w1.js", None, ALL_WIDTHS),
)
PAIRS = tuple((screen, seed, after_load, viewport) for screen, seed, after_load, viewports in SCREENS
              for viewport in viewports)
# qa.md "Controls". Each renders the golden bill-items at 390 x 844 against a candidate path, with no script.
# The self-compare reads that golden through the test server (never written) and must give 0 pixels, so the flags and
# the harness add no noise. The no-seed render is the cold app and must give more than 0, so the gate can fail.
CONTROL_GOLDEN, CONTROL_VIEWPORT = "bill-items", "390x844"
CONTROLS = (
    ("control-self", f"/docs/design/{CONTROL_GOLDEN}.html", "0 mismatching pixels and equal sizes",
     lambda report: report["dimensions_match"] is True and report["mismatch_pixels"] == 0),
    ("control-noseed", "/", "more than 0 mismatching pixels", lambda report: report["mismatch_pixels"] > 0),
)
FIXED_TIME = "2026-10-13T09:00:00"
THRESHOLD = "0.01"
RUN_TIMEOUT_SECONDS = 180


def command(base_url, screen, seed, after_load, viewport, out, path="/"):
    cmd = [sys.executable, str(HARNESS),
           "--golden", f"./docs/design/{screen}.html", "--candidate", f"{base_url}{path}",
           "--viewport", viewport, "--dpr", "1", "--color-scheme", "dark",
           "--browser-arg=--disable-lcd-text",  # the top-layer dialog would otherwise get greyscale text only on one side
           "--fixed-time", FIXED_TIME, "--threshold", THRESHOLD]
    if seed:
        cmd += ["--candidate-init-script", f"./tests/browser/fidelity/{seed}"]
    if after_load:
        cmd += ["--candidate-after-load", f"./tests/browser/fidelity/{after_load}"]
    return cmd + ["--out", str(out)]


def run_harness(cmd, out, log):
    """Runs one harness command and logs its output. Gives (the report.json it wrote, "") or (None, why there is none)."""
    log(f"$ {' '.join(cmd)}")
    try:
        done = subprocess.run(cmd, cwd=rig.ROOT, capture_output=True, text=True, timeout=RUN_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        return None, f"harness did not finish within {RUN_TIMEOUT_SECONDS} s"
    for line in (done.stdout + done.stderr).strip().splitlines():
        log(f"  {line}")
    if done.returncode != 0:
        return None, f"harness exit {done.returncode}"
    try:
        return json.loads((out / "report.json").read_text(encoding="utf-8")), ""
    except (OSError, ValueError):
        return None, "no report.json"


def describe(report, why):
    if report is None:
        return why
    return (f"{report['mismatch_pixels']} mismatching pixels ({report['mismatch_pct']}%), "
            f"sizes {report['golden_size']} / {report['candidate_size']}")


def run_control(base_url, control, run_folder, log):
    """Runs one control and logs its CONTROL line. True when it behaves as qa.md says."""
    name, path, wants, holds = control
    out = run_folder / f"{name}-{CONTROL_VIEWPORT}"
    report, why = run_harness(command(base_url, CONTROL_GOLDEN, None, None, CONTROL_VIEWPORT, out, path), out, log)
    behaves = report is not None and holds(report)
    log(f"CONTROL {'PASS' if behaves else 'FAIL'} {name} {CONTROL_VIEWPORT}, wants {wants}, has {describe(report, why)}")
    return behaves


def run_pair(base_url, pair, run_folder, log):
    """Runs one pair. Gives (whether it passes, its PASS or FAIL line)."""
    screen, seed, after_load, viewport = pair
    out = run_folder / f"{screen}-{viewport}"
    report, why = run_harness(command(base_url, screen, seed, after_load, viewport, out), out, log)
    passed = report is not None and report["dimensions_match"] is True and report["mismatch_pixels"] == 0
    return passed, f"{'PASS' if passed else 'FAIL'}  {screen:16} {viewport:9} {describe(report, why)}"


def main():
    if not HARNESS.is_file():
        sys.exit(f"harness not found: {HARNESS} (set SDLC_HARNESS to the path of the sdlc harness fidelity.py)")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_folder = EVIDENCE_ROOT / stamp
    run_folder.mkdir(parents=True)  # never exist_ok, so a run cannot write into an earlier run's folder
    lines = []

    def log(text):
        print(text, flush=True)
        lines.append(text)

    def save_log():
        (run_folder / "run.log").write_text("\n".join(lines) + "\n", encoding="utf-8")

    log(f"fidelity gate {stamp}, python {sys.executable}, harness {HARNESS}")
    controls_behave, results = False, []
    server = rig.StaticServer(rig.ROOT, say=log)
    try:
        server.start()
        controls_behave = all(run_control(server.base, control, run_folder, log) for control in CONTROLS)  # stops at the first that does not
        if controls_behave:
            results = [run_pair(server.base, pair, run_folder, log) for pair in PAIRS]
    finally:
        server.stop()
        save_log()
    log("")
    if not controls_behave:
        log("NOT RUN, a control did not behave, so no pair counts")
        save_log()
        return 1
    for _, line in results:
        log(line)
    passed = sum(1 for ok, _ in results if ok)
    log(f"{passed} of {len(PAIRS)} pairs pass, evidence in {run_folder}")
    save_log()
    return 0 if passed == len(PAIRS) else 1


if __name__ == "__main__":
    sys.exit(main())
