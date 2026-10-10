"""Regression solver round 2, split-app (RG-CR-08). Runs the browser suite, or a selection of it, in a scratch copy of the project with
at most one mutation applied. The project's src/ and tests/ are only read: the copy lives in scratch/ inside this evidence folder
and is rebuilt from the project on every run, so no mutant can be left behind in src/. Same shape as the round 1 scratch_run.py
(qa/regression-solver/20261009-222856/), with the mutants this round needs.

Usage: python scratch_run.py <label> [--mutant NAME] [-k EXPRESSION] [--tb STYLE] [--timeout SECONDS] [--keep] [--cleanup]
  RED  no mutation: the scratch copy is the project as it is now (used before the fix, so the new rows run against the unfixed src/
       without leaving failure screenshots in the project's qa/functional/ folder)
  B1   items.js Remove drops the count test: HEAD's line, `() => { swallowRepeatClicks(); onRemove(id); }`
  B2   people.js Remove drops the count test: the same
  M3   items.js Remove arms no guard but keeps the count test (round 1's M3, rebuilt for the new line)
  M4   people.js Remove arms no guard but keeps the count test (round 1's M4, rebuilt)
Every edit must match its text exactly the expected number of times, or the run stops before pytest starts. The project's src/ and
tests/browser are hashed (SHA-256 of every file) before and after, and the result is printed.
The full output goes to run-<label>.txt next to this script (header line, then pytest's output). `--cleanup` only deletes scratch/.
Clipboard: the suite's rig only (recorder), never the system clipboard.
"""
import argparse
import hashlib
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[5]
SCRATCH = HERE / "scratch"
assert (PROJECT / "index.html").is_file(), PROJECT

COPY = ["index.html", "CLAUDE.md", "src", "tests/browser", "docs/design"]  # CLAUDE.md: test_R1 fetches it from the served root

FIXED_REMOVE = 'remove.addEventListener("click", (event) => { swallowRepeatClicks(); if (!isRepeatClick(event)) onRemove(id); });'
HEAD_REMOVE = 'remove.addEventListener("click", () => { swallowRepeatClicks(); onRemove(id); });'
NO_GUARD_REMOVE = 'remove.addEventListener("click", (event) => { if (!isRepeatClick(event)) onRemove(id); });'
MUTANTS = {
    # name: (what it is, [(file, old text, new text, how many times old text must occur)])
    "RED": ("no mutation (the project as it is)", []),
    "B1": ("items.js Remove drops the count test (HEAD's line)", [("src/ui/items.js", FIXED_REMOVE, HEAD_REMOVE, 1)]),
    "B2": ("people.js Remove drops the count test (HEAD's line)", [("src/ui/people.js", FIXED_REMOVE, HEAD_REMOVE, 1)]),
    # M3 and M4 are round 1's mutants "a Remove arms no guard", rebuilt for the new line: the count test stays, the arming goes.
    # Run after the fix to see whether the count test now hides the missing arming (it must not).
    "M3": ("items.js Remove arms no guard, keeps the count test", [("src/ui/items.js", FIXED_REMOVE, NO_GUARD_REMOVE, 1)]),
    "M4": ("people.js Remove arms no guard, keeps the count test", [("src/ui/people.js", FIXED_REMOVE, NO_GUARD_REMOVE, 1)]),
}


def digest(*folders):
    out = {}
    for folder in folders:
        for path in sorted(folder.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                out[str(path.relative_to(PROJECT))] = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    return out


def build_scratch():
    assert SCRATCH.resolve().is_relative_to(HERE), "scratch must live inside the evidence folder"
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    for name in COPY:
        source = PROJECT / name
        target = SCRATCH / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copyfile(source, target)


def apply_mutant(name):
    what, edits = MUTANTS[name]
    for relative, old, new, expected in edits:
        path = SCRATCH / relative
        text = path.read_bytes().decode("utf-8")
        found = text.count(old)
        if found != expected:
            sys.exit(f"mutant {name}: expected {expected} match(es) of {old!r} in {relative}, found {found}")
        path.write_bytes(text.replace(old, new).encode("utf-8"))
    return what


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("label")
    parser.add_argument("--mutant", default="RED")
    parser.add_argument("-k", dest="select")
    parser.add_argument("--tb", default="short")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--keep", action="store_true", help="leave scratch/ in place at the end")
    parser.add_argument("--cleanup", action="store_true", help="delete scratch/ and stop")
    args = parser.parse_args()
    if args.cleanup:
        shutil.rmtree(SCRATCH, ignore_errors=True)
        print(f"scratch/ removed, exists now: {SCRATCH.exists()}")
        return

    before = digest(PROJECT / "src", PROJECT / "tests" / "browser")
    build_scratch()
    what = apply_mutant(args.mutant)
    command = [sys.executable, "-B", "-m", "pytest", "tests/browser", "-q", "-p", "no:cacheprovider", f"--tb={args.tb}", "-rf"]
    if args.select:
        command += ["-k", args.select]
    print(f"{args.label}: {args.mutant} = {what}; select {args.select!r}", flush=True)
    started = time.time()
    try:
        done = subprocess.run(command, cwd=SCRATCH, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=args.timeout)
        output, status = done.stdout + done.stderr, done.returncode
    except subprocess.TimeoutExpired as expired:
        output, status = f"gave up after {args.timeout} s\n{expired.stdout or ''}", 124
    header = f"# {args.label}: mutant {args.mutant} ({what}); select {args.select!r}; exit {status}; {time.time() - started:.1f} s wall\n"
    (HERE / f"run-{args.label}.txt").write_text(header + output, encoding="utf-8")
    lines = output.splitlines()
    for line in lines:
        if "server STARTED" in line or "server STOPPED" in line:
            print("  " + line)
    failed = [line for line in lines if line.startswith("FAILED")]
    summary = [line for line in lines if (" passed" in line or " failed" in line) and not line.startswith("FAILED")]
    print(f"{args.label}: {summary[-1] if summary else 'no summary'}")
    for line in failed[:200]:
        print("    " + line[:230])
    if len(failed) > 200:
        print(f"    ... {len(failed) - 200} more failing ids in run-{args.label}.txt")
    if not args.keep:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    after = digest(PROJECT / "src", PROJECT / "tests" / "browser")
    print("project src/ and tests/browser unchanged (SHA-256 of every file equal before and after)" if before == after
          else "PROJECT FILES CHANGED")
    print(f"scratch/ exists now: {SCRATCH.exists()}")


main()
