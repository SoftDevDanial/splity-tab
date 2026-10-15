"""B5. What the public copy would serve (CLAUDE.md Publish, threat row "What is published", SEC-02 of 1.0).

python docs/modules/split-app/qa/security/20261015-222146/b5_publish_scope.py
Read-only. Lists every file under src/ (tracked, untracked and ignored), every URL index.html and src/ name, the files
the app requests in a real run (from B3's request logs in this folder), and searches the publish set for local paths,
the owner's address, loopback hosts and schemes. Writes b5_publish_scope.json.
"""
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()


tracked = sorted(git("ls-files", "--", "index.html", "src"))
untracked = sorted(git("ls-files", "--others", "--exclude-standard", "--", "index.html", "src"))
ignored = sorted(git("ls-files", "--others", "--ignored", "--exclude-standard", "--", "index.html", "src"))
on_disk = sorted(str(p.relative_to(ROOT)).replace("\\", "/") for p in [ROOT / "index.html", *(ROOT / "src").rglob("*")] if p.is_file())

requested = set()
for name in ("b3_csp_network_style_random-chromium.json", "b3_csp_network_style_random-webkit.json"):
    data = json.loads((HERE / name).read_text(encoding="utf-8"))["rows"][0]
    for part in ("A", "B", "C"):
        for method, url, kind in data[part]["requests"]:
            path = "/" + url.split("/", 3)[3] if url.count("/") >= 3 else url
            if not path.endswith("x.png"):
                requested.add("index.html" if path == "/" else path.lstrip("/"))

PATTERNS = {
    "windows path": r"[A-Za-z]:[\\/]", "users dir": r"(?i)users[\\/]", "owner address": r"(?i)gmail|@[a-z0-9-]+\.[a-z]{2,}",
    "loopback": r"127\.0\.0\.1|localhost", "scheme": r"[a-zA-Z][a-zA-Z0-9+.-]*://", "todo": r"(?i)\btodo\b|\bfixme\b|\bxxx\b",
    "key-like": r"(?i)(api[_-]?key|secret|token|password)\s*[:=]",
}
hits = []
for rel in on_disk:
    text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    for label, pattern in PATTERNS.items():
        for match in re.finditer(pattern, text):
            line = text.count("\n", 0, match.start()) + 1
            hits.append({"file": rel, "kind": label, "line": line, "match": match.group(0)})

index = (ROOT / "index.html").read_text(encoding="utf-8")
refs = re.findall(r'(?:href|src)="([^"]+)"', index)
result = {
    "tracked": tracked, "untracked": untracked, "ignored": ignored, "on_disk": on_disk,
    "on_disk_not_tracked": sorted(set(on_disk) - set(tracked)),
    "index_refs": refs, "requested_in_b3": sorted(requested),
    "on_disk_never_requested": sorted(set(on_disk) - requested),
    "hits": hits,
    "nojekyll_in_repo": (ROOT / ".nojekyll").exists(),
}
(HERE / "b5_publish_scope.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k not in ("tracked", "on_disk")}, indent=1))
print("tracked", len(tracked), "on disk", len(on_disk))
