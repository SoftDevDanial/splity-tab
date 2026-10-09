"""Regression re-check, split-app. Mutants of the guard and of the Add handlers, a candidate fix for RG-CR-08, and a candidate test.

Usage: python run_mutants.py [--full] [--keep] [--extra-test] <name> [<name> ...]     names: BASE M1 M2 M9 M10 A1 A2 FIXA
Everything happens in scratch-<name>/ inside this evidence folder: index.html, src/, tests/browser/, docs/design/ and CLAUDE.md are
copied from the project, then the replacements of the named mutant are applied in memory to the scratch files. The project's
src/ and tests/browser are never written (a before and after SHA-256 of every file under them is printed). A replacement that
matches nothing, or more than once, stops the run: a mutant that did not apply would be a pass that proves nothing.
The selection is the tests that name R6, R7, R12, R29, R30 or R34 (218 of the 421); --full runs all 421.
--extra-test copies test_rg_cr_08_candidate.py from this folder into the scratch tests/browser/ (the candidate test for RG-CR-08)
and adds it to the selection.
--keep leaves the scratch folders in place (the default removes them at the end; they hold copies, not evidence).
Results go to mutant-results-<names>.txt next to this script.

M1   the removal pair removes the click listener twice, so the mousedown listener is never removed (RG-CR-02)
M2   the removal pair removes the mousedown listener twice, so the click listener is never removed (the mirror of M1)
M9   the guard never registers its mousedown listener (the press side is gone, the click side stays)
M10  the guard never registers its click listener (the click side is gone, the press side stays)
A1   Add person arms no guard (RG-CR-01)
A2   Add item arms no guard (RG-CR-01, BUILD.md call 20)
FIXA the candidate fix for RG-CR-08: isRepeatClick is exported again and both Remove handlers ignore a repeat click (as before
     071577a) as well as arming the guard
"""
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[5]
SELECT = "R6 or R7 or R12 or R29 or R30 or R34"
TIMEOUT_SECONDS = 1200

DOM = "src/ui/dom.js"
PEOPLE = "src/ui/people.js"
ITEMS = "src/ui/items.js"
REMOVE_NOW = 'remove.addEventListener("click", () => { swallowRepeatClicks(); onRemove(id); });'
REMOVE_FIXED = 'remove.addEventListener("click", (event) => { swallowRepeatClicks(); if (!isRepeatClick(event)) onRemove(id); });'
IMPORT_NOW = "import { block, el, swallowRepeatClicks, setAttr,"
IMPORT_FIXED = "import { block, el, isRepeatClick, swallowRepeatClicks, setAttr,"
MUTANTS = {
    "BASE": [],
    "M1": [(DOM, 'document.removeEventListener("mousedown", guard, true);', 'document.removeEventListener("click", guard, true);')],
    "M2": [(DOM, 'document.removeEventListener("click", guard, true);', 'document.removeEventListener("mousedown", guard, true);')],
    "M9": [(DOM, 'document.addEventListener("mousedown", guard, true);', "/* mutant M9: no press listener */")],
    "M10": [(DOM, 'document.addEventListener("click", guard, true);', "/* mutant M10: no click listener */")],
    "A1": [(PEOPLE, "{ swallowRepeatClicks(); onAdd(); }", "{ onAdd(); }")],
    "A2": [(ITEMS, "{ swallowRepeatClicks(); onAdd(); }", "{ onAdd(); }")],
    "FIXA": [
        (DOM, "const isRepeatClick = (event) => event.detail > 1;", "export const isRepeatClick = (event) => event.detail > 1;"),
        (PEOPLE, IMPORT_NOW, IMPORT_FIXED), (PEOPLE, REMOVE_NOW, REMOVE_FIXED),
        (ITEMS, IMPORT_NOW, IMPORT_FIXED), (ITEMS, REMOVE_NOW, REMOVE_FIXED),
    ],
}


def digest(*folders):
    out = {}
    for folder in folders:
        for p in sorted(folder.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                out[str(p.relative_to(PROJECT))] = hashlib.sha256(p.read_bytes()).hexdigest()[:12]
    return out


def build_scratch(scratch, extra_test):
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir()
    shutil.copy(PROJECT / "index.html", scratch / "index.html")
    shutil.copy(PROJECT / "CLAUDE.md", scratch / "CLAUDE.md")
    shutil.copytree(PROJECT / "src", scratch / "src")
    shutil.copytree(PROJECT / "tests" / "browser", scratch / "tests" / "browser", ignore=shutil.ignore_patterns("__pycache__", "*.png"))
    shutil.copytree(PROJECT / "docs" / "design", scratch / "docs" / "design")
    if extra_test:
        shutil.copy(HERE / "test_rg_cr_08_candidate.py", scratch / "tests" / "browser" / "test_rg_cr_08_candidate.py")


def run(name, full, extra_test):
    scratch = HERE / f"scratch-{name}"
    build_scratch(scratch, extra_test)
    for rel, old, new in MUTANTS[name]:
        path = scratch / rel
        text = path.read_bytes().decode("utf-8")
        if text.count(old) != 1:
            raise SystemExit(f"{name}: the replacement matched {text.count(old)} times in {rel}, expected exactly 1: {old!r}")
        path.write_bytes(text.replace(old, new).encode("utf-8"))
    command = [sys.executable, "-m", "pytest", "tests/browser", "-q", "-p", "no:cacheprovider", "--tb=no", "-rf"]
    if not full:
        command += ["-k", SELECT + (" or rg_cr_08" if extra_test else "")]
    done = subprocess.run(command, cwd=scratch, capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
    lines = done.stdout.splitlines()
    failed = [line for line in lines if line.startswith("FAILED")]
    summary = [line for line in lines if (" passed" in line or " failed" in line) and not line.startswith("FAILED")]
    return scratch, (summary[-1] if summary else "no summary: " + done.stdout[-400:]), failed


def main():
    args = sys.argv[1:]
    full, keep, extra = "--full" in args, "--keep" in args, "--extra-test" in args
    names = [a for a in args if not a.startswith("--")]
    before = digest(PROJECT / "src", PROJECT / "tests" / "browser")
    out = []
    for name in names:
        scratch, summary, failed = run(name, full, extra)
        block = [f"{name}{' (+candidate test)' if extra else ''}{' (full suite)' if full else ''}: {summary}"] + [f"    {line}" for line in failed]
        out.extend(block)
        print("\n".join(block), flush=True)
        if not keep:
            shutil.rmtree(scratch, ignore_errors=True)
    after = digest(PROJECT / "src", PROJECT / "tests" / "browser")
    verdict = "project src/ and tests/browser unchanged (SHA-256 of every file equal before and after)" if before == after else "PROJECT FILES CHANGED"
    out.append(verdict)
    print(verdict, flush=True)
    (HERE / ("mutant-results-" + "-".join(names) + ("-extra" if extra else "") + ("-full" if full else "") + ".txt")).write_text("\n".join(out) + "\n", encoding="utf-8")


main()
