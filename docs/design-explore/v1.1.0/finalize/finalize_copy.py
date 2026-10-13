"""Finalize gate copy: docs/design-explore/v1.1.0/final/ -> docs/design/, SHA-256 verified.

Copies every golden .html and .md, system.css, LINKS.json and sample-history.json (when present).
Leaves checks/ (path bound to round-2/ and logo/) and SELF-CRITIQUE.md (step 8 record) in design-explore.
Usage: python -B finalize_copy.py <app root> [--dry]
"""
import hashlib
import shutil
import sys
from pathlib import Path

KEEP_OUT = {"SELF-CRITIQUE.md"}
EXTRA = {"system.css", "LINKS.json", "sample-history.json"}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


root = Path(sys.argv[1]).resolve()
dry = "--dry" in sys.argv
src = root / "docs/design-explore/v1.1.0/final"
dst = root / "docs/design"
files = sorted(p for p in src.iterdir() if p.is_file() and p.name not in KEEP_OUT
               and (p.suffix in (".html", ".md") or p.name in EXTRA))
new = replaced = same = 0
for p in files:
    t = dst / p.name
    state = "new" if not t.exists() else ("same" if sha(t) == sha(p) else "replace")
    if not dry:
        shutil.copy2(p, t)
        if sha(t) != sha(p):
            print(f"HASH MISMATCH {p.name}")
            sys.exit(1)
    new += state == "new"
    replaced += state == "replace"
    same += state == "same"
    print(f"{state:8} {p.name}")
left = sorted(q.name for q in dst.iterdir() if q.is_file() and not (src / q.name).exists())
print(f"\n{len(files)} files, {new} new, {replaced} replaced, {same} unchanged, all hashes match" + (" (dry run)" if dry else ""))
print("in docs/design but not in final/:", left)
