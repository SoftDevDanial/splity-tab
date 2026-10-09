"""Regression code review, split-app. Runs the repeat-press tests (R7, R29, R30, R34 selection of test_app.py) against
mutated copies of the delta files. Everything happens in scratch-mutants/ inside this evidence folder. src/ is never touched.

Usage: python run_mutants.py <name> [<name> ...]     names: BASE M1 M2 M3 M4 M5 M6 M7 M8 FIX
Each run copies the mutant file over the scratch copy, runs pytest there (its own server, headless Chromium, bounded by a
timeout), prints the summary and the failing test ids, and puts the scratch copy back to the shipped file.
"""
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[5]
SCRATCH = HERE / "scratch-mutants"
FILES = SCRATCH / "mutant-files"
SELECT = "R7 or R29 or R30 or R34"
TIMEOUT_SECONDS = 600

# name -> (mutant file, target under src/ui/)
MUTANTS = {
    "BASE": (None, None),
    "M1": ("dom.M1.js", "dom.js"),
    "M2": ("dom.M2.js", "dom.js"),
    "M3": ("items.M3.js", "items.js"),
    "M4": ("people.M4.js", "people.js"),
    "M5": ("dialog.M5.js", "dialog.js"),
    "M6": ("dom.M6.js", "dom.js"),
    "M7": ("dom.M7.js", "dom.js"),
    "M8": ("dom.M8.js", "dom.js"),
    "FIX": ("people.FIX.js", "people.js"),
}


def run(name):
    source, target = MUTANTS[name]
    if source:
        shutil.copyfile(FILES / source, SCRATCH / "src" / "ui" / target)
    try:
        done = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/browser", "-q", "-p", "no:cacheprovider", "--tb=no", "-rf", "-k", SELECT],
            cwd=SCRATCH, capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
        lines = [line for line in done.stdout.splitlines() if line.startswith("FAILED") or " passed" in line or " failed" in line]
        failed = [line for line in lines if line.startswith("FAILED")]
        summary = [line for line in lines if not line.startswith("FAILED")]
        return summary[-1] if summary else "no summary", failed
    except subprocess.TimeoutExpired:
        return f"gave up after {TIMEOUT_SECONDS} s", []
    finally:
        if target:
            shutil.copyfile(PROJECT / "src" / "ui" / target, SCRATCH / "src" / "ui" / target)


def main():
    results = []
    for name in sys.argv[1:]:
        summary, failed = run(name)
        results.append(f"{name}: {summary}")
        results.extend(f"    {line}" for line in failed)
        print(results[-1 - len(failed)])
        for line in failed:
            print("    " + line)
    out = HERE / ("mutant-results-" + "-".join(sys.argv[1:]) + ".txt")
    out.write_text("\n".join(results) + "\n", encoding="utf-8")


main()
