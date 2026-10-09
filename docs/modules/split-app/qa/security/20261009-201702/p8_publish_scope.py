"""Audit item 4: what would the repository root expose if it were served as is (GitHub Pages "serves the folder as is").

Part 1: the tracked files by area, by type, their size, the number of copies of src/ files outside src/, and the
local paths in them. Read-only git (ls-files, grep) on the repository.
Part 2: a loopback static server on the project root (the same command CLAUDE.md gives for serving) and GET requests for
sample URLs outside index.html and src/. A 200 means the file would be public from a root deployment. Nothing is written.
"""
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

ROOT = common.ROOT
LOCAL_PATH = re.compile(r"[CD]:[\\/](Users[\\/]{user}|Work[\\/]|{plugins})", re.I)


def git(*args):
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
    return out.stdout


def part1(results):
    files = git("ls-files", "-z").split("\0")
    files = [f for f in files if f]
    areas = Counter()
    sizes = Counter()
    for f in files:
        area = f.split("/")[0] if "/" in f else "(root file)"
        if area == "docs":
            parts = f.split("/")
            area = "docs/" + (parts[1] if len(parts) > 2 else "(file)") + ("/" + parts[2] if len(parts) > 3 and parts[1] == "modules" else "")
        areas[area] += 1
        try:
            sizes[area] += (ROOT / f).stat().st_size
        except OSError:
            pass
    served_by_design = [f for f in files if f == "index.html" or f.startswith("src/")]
    copies_of_src = [f for f in files if re.search(r"/src/(core|ui)/[^/]+\.js$|/src/[^/]+\.js$", f) and not f.startswith("src/")]
    mutant_dirs = sorted({re.sub(r"/src/.*$", "", f) for f in copies_of_src})
    types = Counter(Path(f).suffix.lower() or "(none)" for f in files)
    path_hits = Counter()
    hit_files = []
    for f in files:
        p = ROOT / f
        if p.suffix.lower() in (".png", ".ico", ".jpg", ".gif", ".woff", ".woff2"):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if LOCAL_PATH.search(text):
            hit_files.append(f)
            path_hits[f.split("/")[0] + "/" + (f.split("/")[1] if "/" in f else "")] += 1
    results["cases"].append({
        "case": "tracked files by area", "tracked_files": len(files), "served_by_design": len(served_by_design),
        "outside_the_two_served_areas": len(files) - len(served_by_design),
        "areas": {k: {"files": v, "bytes": sizes[k]} for k, v in sorted(areas.items(), key=lambda kv: -kv[1])},
        "types": dict(types.most_common(12)), "copies_of_src_files_outside_src": len(copies_of_src), "copy_roots": len(mutant_dirs),
        "copy_root_samples": mutant_dirs[:3], "files_with_a_local_path": len(hit_files), "local_path_by_area": dict(path_hits),
        "local_path_samples": hit_files[:5],
    })
    print(f"tracked files {len(files)}; served by design (index.html and src/) {len(served_by_design)}; everything else {len(files) - len(served_by_design)}")
    print("top areas:", {k: v for k, v in list(areas.most_common(8))})
    print(f"copies of src files outside src/: {len(copies_of_src)} in {len(mutant_dirs)} folders, e.g. {mutant_dirs[:2]}")
    print(f"text files containing a local path ({home}, {workspace}, {plugins}): {len(hit_files)}; by area {dict(path_hits)}")
    return files


def fetch(base, path):
    try:
        with urllib.request.urlopen(base + path, timeout=5) as r:
            body = r.read(400)
            return r.status, r.headers.get("Content-Type"), int(r.headers.get("Content-Length") or 0), body
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type"), 0, b""


def part2(server, results, files):
    base = server.base
    samples = [
        "/", "/index.html", "/src/main.js", "/CLAUDE.md", "/docs/constitution.md", "/docs/modules/split-app/spec.md",
        "/docs/progress/STATE.md", "/tests/browser/seeds.py", "/tests/browser/rig.py", "/.claude/settings.json", "/.gitignore",
        "/harness/", "/docs/", "/docs/modules/split-app/qa/security/", "/.git/HEAD", "/.git/config",
    ]
    mutant = next((f for f in files if "/mutants/" in f and f.endswith("/src/core/money.js")), None)
    png = next((f for f in files if f.endswith(".png") and "split-app" in f), None)
    log = next((f for f in files if f.endswith("run.log")), None)
    script = next((f for f in files if f.endswith("probe_double.py")), None)
    samples += [("/" + p) for p in (mutant, png, log, script) if p]
    rows = []
    for path in samples:
        status, ctype, length, body = fetch(base, path)
        rows.append({"path": path, "status": status, "content_type": ctype, "length": length})
        print(f"{status} {path:100} {ctype} {length}")
    results["cases"].append({"case": "sample URLs on a root-served copy", "rows": rows})


def body(browser, server, results):
    files = part1(results)
    part2(server, results, files)


if __name__ == "__main__":
    common.run_probe("p8-publish-scope", body)
