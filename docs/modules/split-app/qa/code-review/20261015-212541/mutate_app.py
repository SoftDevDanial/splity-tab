"""Code-review finder (read-only) app mutants. Copies index.html, src/, tests/ and docs/design/ (read, never written) of
the project into scratch/app-mutants/<id>/, applies one exact single-occurrence edit, and runs the named browser tests
there, headless Chromium, through the project's own conftest (its server and contexts are the copy's, rooted in the copy).
Usage: python mutate_app.py <projectRoot> <outDir> <id> [<id> ...]
Run 2026-10-15 from the session scratch folder split-cr-step5/, on HEAD d58f4ce, Chromium 149.0.7827.55.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

root, out = Path(sys.argv[1]), Path(sys.argv[2])
MUTANTS = {
    "U1": ("src/ui/dom.js", "const previous = lastClick?.event === event ? clickBeforeLast : lastClick;",
           "const previous = lastClick;", "isRepeatClick compares a click with itself", "R57 or R7_ or R6_"),
    "U2": ("src/ui/spare-choice.js", "(shownChip() ?? splits).focus();", "splits.focus();",
           "P1 always gives focus to Splits", "R52"),
    "U3": ("src/ui/sections.js", "if (!open) revealing?.cancel();", "",
           "a fold does not cancel a running reveal", "R48"),
    "U4": ("src/ui/receipt.js", "if (many) list.style.setProperty(\"--rows\", String(Math.ceil(result.rows.length / 2)));",
           "if (many) list.style.setProperty(\"--rows\", String(Math.floor(result.rows.length / 2)));",
           "--rows floors instead of ceil (odd people counts)", "R20 or R38"),
}
results = []
for mid in sys.argv[3:]:
    file, before, after, what, select = MUTANTS[mid]
    dest = out / mid
    dest.mkdir(parents=True)  # never exist_ok, a run never reuses a folder
    shutil.copy2(root / "index.html", dest / "index.html")
    shutil.copytree(root / "src", dest / "src")
    shutil.copytree(root / "tests", dest / "tests", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(root / "docs" / "design", dest / "docs" / "design")
    target = dest / file
    text = target.read_bytes().decode("utf-8")
    hits = text.count(before)
    if hits != 1:
        results.append({"id": mid, "error": f"pattern found {hits} times"})
        continue
    target.write_bytes(text.replace(before, after).encode("utf-8"))
    run = subprocess.run([sys.executable, "-m", "pytest", "tests/browser/test_app.py", "-q", "-p", "no:cacheprovider",
                          "-k", select, "-x" if False else "-q"], cwd=dest, capture_output=True, text=True, timeout=900)
    (dest / "pytest.txt").write_text(run.stdout + run.stderr, encoding="utf-8")
    tail = [line for line in run.stdout.splitlines() if " passed" in line or " failed" in line or " error" in line][-1:]
    failed = [line.split(" ")[1] for line in run.stdout.splitlines() if line.startswith("FAILED ")]
    results.append({"id": mid, "file": file, "what": what, "select": select, "exit": run.returncode,
                    "summary": tail, "killed": run.returncode == 1 and bool(failed), "failed": failed[:10]})
(out / f"app-mutation-summary-{'-'.join(sys.argv[3:])}.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print(json.dumps(results, indent=1))
