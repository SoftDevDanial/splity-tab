"""Regression QA, step 1, part 2: the browser suite, run once, plus the collection.

run_suites.py already ran the node suite once (its output is node-test.txt in this folder). It crashed
afterwards on a summary regex (the spec reporter prints "ℹ tests 275", not "# tests 275"), before pytest
ran. So the node counts here are parsed from the saved node-test.txt, and the node suite is NOT rerun.

This script runs, once each:
  python -m pytest tests/browser -q -p no:cacheprovider --junitxml <this folder>/junit.xml   (suite)
  python -m pytest tests/browser --collect-only -q -p no:cacheprovider                       (ids only)
SPLIT_EVIDENCE is removed from the environment so the suite writes nothing under qa/functional/.
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(r"{workspace}\examples\split")


def run(args, out_name, timeout):
    env = dict(os.environ)
    env.pop("SPLIT_EVIDENCE", None)
    env["PYTHONIOENCODING"] = "utf-8"
    started = time.time()
    proc = subprocess.run(args, cwd=str(ROOT), capture_output=True, timeout=timeout, env=env)
    elapsed = time.time() - started
    text = proc.stdout.decode("utf-8", "replace")
    if proc.stderr:
        text += "\n--- stderr ---\n" + proc.stderr.decode("utf-8", "replace")
    (HERE / out_name).write_text(text, encoding="utf-8")
    return text, proc.returncode, round(elapsed, 1)


def node_counts():
    text = (HERE / "node-test.txt").read_text(encoding="utf-8")
    found = {}
    for key in ("tests", "pass", "fail", "skipped", "todo", "cancelled"):
        match = re.search(rf"^ℹ {key} (\d+)", text, re.M)
        found[key] = int(match.group(1)) if match else None
    found["source"] = "node-test.txt (saved by run_suites.py, the one node run)"
    return found


def main():
    summary = {"started": time.strftime("%Y-%m-%dT%H:%M:%S"), "python": sys.executable,
               "root": str(ROOT), "node": node_counts()}

    collect_text, collect_status, collect_seconds = run(
        [sys.executable, "-m", "pytest", "tests/browser", "--collect-only", "-q", "-p", "no:cacheprovider"],
        "pytest-collect.txt", 300)
    summary["pytest_collect"] = {"exit_status": collect_status, "seconds": collect_seconds,
                                 "output_file": "pytest-collect.txt"}

    text, status, seconds = run(
        [sys.executable, "-m", "pytest", "tests/browser", "-q", "-p", "no:cacheprovider",
         "--junitxml", str(HERE / "junit.xml")],
        "pytest.txt", 600)
    last = [line for line in text.splitlines() if line.strip()][-1]
    summary["pytest_browser"] = {
        "command": "python -m pytest tests/browser -q -p no:cacheprovider --junitxml <evidence>/junit.xml",
        "exit_status": status, "seconds_wall": seconds, "last_line": last,
        "passed": int(m.group(1)) if (m := re.search(r"(\d+) passed", last)) else 0,
        "failed": int(m.group(1)) if (m := re.search(r"(\d+) failed", last)) else 0,
        "errors": int(m.group(1)) if (m := re.search(r"(\d+) error", last)) else 0,
        "output_file": "pytest.txt", "junit": "junit.xml",
    }
    (HERE / "suites-summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
