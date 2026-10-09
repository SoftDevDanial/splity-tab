"""Regression solver, split-app. Runs the browser suite, or a selection of it, in a scratch copy of the project with at most
one mutation applied. The project's src/ and tests/ are only read: every mutant lives in scratch/ inside this evidence
folder and is rebuilt from the project on each run, so nothing can be left behind in src/.

Usage: python scratch_run.py <label> [--mutant NAME] [-k EXPRESSION] [--tb STYLE] [--timeout SECONDS]
  Mutants M1 to M8 are the finder's (regression-code-review/20261009-220225), rebuilt here as exact text edits of the
  current files so they stay valid after the fix. A1 and A2 are new: Add person / Add item arm no guard.
  Every edit must match its text exactly the expected number of times, or the run stops before pytest starts.
Prints the pytest summary, the failing test ids and the server STARTED / STOPPED lines the rig writes. The full output goes
to run-<label>.txt next to this script. Clipboard: the suite's rig only (recorder), never the system clipboard.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[5]
SCRATCH = HERE / "scratch"
assert (PROJECT / "index.html").is_file(), PROJECT

COPY = ["index.html", "CLAUDE.md", "src", "tests/browser", "docs/design"]  # CLAUDE.md: test_R1 fetches it from the served root

GUARD_ADD = 'add.addEventListener("click", () => { swallowRepeatClicks(); onAdd(); });'
REMOVE_GUARDED = "{ swallowRepeatClicks(); onRemove(id); }"
MUTANTS = {
    # name: (what it is, [(file, old text, new text, how many times old text must occur)])
    "M1": ("guard never removes its mousedown listener (removes click twice)",
           [("src/ui/dom.js", 'document.removeEventListener("mousedown", guard, true);',
             'document.removeEventListener("click", guard, true);', 1)]),
    "M2": ("guard never removes its click listener (removes mousedown twice)",
           [("src/ui/dom.js", 'document.removeEventListener("click", guard, true);',
             'document.removeEventListener("mousedown", guard, true);', 1)]),
    "M3": ("item Remove arms no guard", [("src/ui/items.js", REMOVE_GUARDED, "{ onRemove(id); }", 1)]),
    "M4": ("person Remove arms no guard", [("src/ui/people.js", REMOVE_GUARDED, "{ onRemove(id); }", 1)]),
    "M5": ("New bill click arms no guard (I-1)",
           [("src/ui/dialog.js", 'opener.addEventListener("click", () => {\n    swallowRepeatClicks();\n',
             'opener.addEventListener("click", () => {\n', 1)]),
    "M6": ("a repeat is a click count above 2", [("src/ui/dom.js", "event.detail > 1", "event.detail > 2", 1)]),
    "M7": ("guard does not preventDefault", [("src/ui/dom.js", "    event.preventDefault();\n", "", 1)]),
    "M8": ("guard listens in the bubble phase", [("src/ui/dom.js", ", guard, true);", ", guard, false);", 4)]),
    "A1": ("Add person arms no guard (RG-CR-01)", [("src/ui/people.js", GUARD_ADD, 'add.addEventListener("click", onAdd);', 1)]),
    "A2": ("Add item arms no guard (the symmetric guard)", [("src/ui/items.js", GUARD_ADD, 'add.addEventListener("click", onAdd);', 1)]),
}


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
    parser.add_argument("--mutant")
    parser.add_argument("-k", dest="select")
    parser.add_argument("--tb", default="line")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--build-only", action="store_true", help="build scratch/ (with the mutant) and stop, to point a probe at it")
    args = parser.parse_args()

    build_scratch()
    what = apply_mutant(args.mutant) if args.mutant else "no mutation"
    if args.build_only:
        print(f"{args.label}: scratch/ built, {what}")
        return
    command = [sys.executable, "-B", "-m", "pytest", "tests/browser", "-q", "-p", "no:cacheprovider", f"--tb={args.tb}", "-rf"]
    if args.select:
        command += ["-k", args.select]
    print(f"{args.label}: {what}; select {args.select!r}", flush=True)
    try:
        done = subprocess.run(command, cwd=SCRATCH, capture_output=True, text=True, timeout=args.timeout)
        output = done.stdout + done.stderr
    except subprocess.TimeoutExpired as expired:
        output = f"gave up after {args.timeout} s\n{expired.stdout or ''}"
    (HERE / f"run-{args.label}.txt").write_text(output, encoding="utf-8")
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


main()
