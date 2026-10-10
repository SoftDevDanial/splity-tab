"""Regression QA, step 1: run each suite once and record counts and times.

Runs from the project root, the two commands in CLAUDE.md:
  node --test "tests/**/*.test.js"
  python -m pytest tests/browser -q -p no:cacheprovider      (plus --junitxml into this folder)
Also writes the pytest collection (every node id) so the scenario table can name parametrised rows.
SPLIT_EVIDENCE is removed from the environment so the suite writes nothing under qa/functional/.
Writes only into this folder. Never modifies the project.
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
NODE = r"C:\Program Files\nodejs\node.exe"


def run(label, args, out_name, timeout):
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
    return {"label": label, "args": args, "exit_status": proc.returncode,
            "seconds": round(elapsed, 1), "output_file": out_name, "text": text}


def main():
    summary = {"started": time.strftime("%Y-%m-%dT%H:%M:%S"), "root": str(ROOT),
               "python": sys.executable, "node": NODE}

    node = run("node unit tests", [NODE, "--test", "tests/**/*.test.js"], "node-test.txt", 600)
    text = node.pop("text")
    node["tests"] = int(re.search(r"^# tests (\d+)", text, re.M).group(1))
    node["pass"] = int(re.search(r"^# pass (\d+)", text, re.M).group(1))
    node["fail"] = int(re.search(r"^# fail (\d+)", text, re.M).group(1))
    node["skipped"] = int(re.search(r"^# skipped (\d+)", text, re.M).group(1))
    node["todo"] = int(re.search(r"^# todo (\d+)", text, re.M).group(1))
    summary["node"] = node

    collect = run("pytest collect", [sys.executable, "-m", "pytest", "tests/browser", "--collect-only", "-q",
                                     "-p", "no:cacheprovider"], "pytest-collect.txt", 300)
    collect.pop("text")
    summary["pytest_collect"] = collect

    browser = run("pytest browser suite",
                  [sys.executable, "-m", "pytest", "tests/browser", "-q", "-p", "no:cacheprovider",
                   "--junitxml", str(HERE / "junit.xml")],
                  "pytest.txt", 600)
    text = browser.pop("text")
    last = [line for line in text.splitlines() if line.strip()][-1]
    browser["last_line"] = last
    browser["passed"] = int((re.search(r"(\d+) passed", last) or [None, 0])[1]) if re.search(r"(\d+) passed", last) else 0
    browser["failed"] = int(m.group(1)) if (m := re.search(r"(\d+) failed", last)) else 0
    browser["errors"] = int(m.group(1)) if (m := re.search(r"(\d+) error", last)) else 0
    summary["pytest_browser"] = browser

    (HERE / "suites-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "args"} if isinstance(v, dict) else v
                      for k, v in summary.items()}, indent=2))


if __name__ == "__main__":
    main()
