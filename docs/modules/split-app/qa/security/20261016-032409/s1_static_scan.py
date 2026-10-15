"""S1. A text scan of the shipped files (index.html and src/), today's tree and the control tree (798f17f), reading only.

cd to this folder, then: python -B s1_static_scan.py <control tree>
The banned lists of R37 (markup sinks), R38 (style writes) and R39 (network), plus storage, messaging, navigation and
dynamic code APIs that no requirement allows, plus every RegExp use of NAME_CONTROLS (.test, .exec, .match, .search,
.split, .lastIndex, .compile) and every writer of an input's value or selection. Each hit is the file, the line text
and the count, so the delta 798f17f..HEAD shows as hits that differ. Writes s1_static_scan.json here.
"""
import json
import re
import sys
from pathlib import Path

from common import ROOT, write_here

PATTERNS = {
    "R37 markup sinks": r"innerHTML|outerHTML|insertAdjacentHTML|document\.write|\beval\(|new Function\(|setAttribute\(\s*[\"']on|createContextualFragment|DOMParser|<template|srcdoc",
    "R38 style writes": r"setAttribute\(\s*[\"']style|cssText|insertRule|new CSSStyleSheet|adoptedStyleSheets|<style|\.style\.[a-zA-Z]+\s*=[^=]",
    "R38 allowed style calls": r"style\.(setProperty|removeProperty)\(",
    "R39 network": r"fetch\(|XMLHttpRequest|WebSocket|EventSource|sendBeacon|serviceWorker|navigator\.share|RTCPeerConnection|importScripts|import\(",
    "storage other than localStorage": r"sessionStorage|indexedDB|document\.cookie|caches\.|CookieStore|navigator\.storage|FileSystem|showSaveFilePicker",
    "localStorage": r"localStorage",
    "messaging and navigation": r"postMessage|BroadcastChannel|window\.open|location\s*=|location\.(href|assign|replace)|history\.(push|replace)State|SharedWorker|new Worker",
    "timers": r"setTimeout|setInterval|requestIdleCallback",
    "NAME_CONTROLS uses": r"NAME_CONTROLS[^;\n]*",
    "regex statefulness on a shared class": r"NAME_CONTROLS\s*\.\s*(test|exec|lastIndex|compile)|\.(match|matchAll|search|split)\(\s*NAME_CONTROLS",
    "input value or selection writes": r"\.value\s*=[^=]|setSelectionRange|setRangeText|selectionStart\s*=|execCommand",
    "scheme strings": r"[a-zA-Z][a-zA-Z0-9+.-]*://",
    "clipboard": r"clipboard",
}


def scan(root):
    files = [root / "index.html", *sorted((root / "src").rglob("*.js")), *sorted((root / "src").rglob("*.css")), *sorted((root / "src").rglob("*.svg"))]
    out = {}
    for label, pattern in PATTERNS.items():
        hits = []
        for path in files:
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for match in re.finditer(pattern, line):
                    hits.append({"file": path.relative_to(root).as_posix(), "match": match.group(0)[:80], "line": line.strip()[:160]})
        out[label] = hits
    return out


head = scan(ROOT)
control = scan(Path(sys.argv[1]))
delta = {}
for label in PATTERNS:
    key = lambda h: (h["file"], h["line"])  # noqa: E731
    new = [h for h in head[label] if key(h) not in {key(c) for c in control[label]}]
    gone = [h for h in control[label] if key(h) not in {key(c) for c in head[label]}]
    delta[label] = {"head": len(head[label]), "control": len(control[label]), "new_in_head": new, "gone_from_head": gone}
write_here("s1_static_scan.json", {"head": head, "control_951f277": control, "delta": delta})
for label, d in delta.items():
    print(f"{label}: head {d['head']} control {d['control']} new {len(d['new_in_head'])} gone {len(d['gone_from_head'])}")
    for h in d["new_in_head"]:
        print(f"   + {h['file']}: {h['line']}")
    for h in d["gone_from_head"]:
        print(f"   - {h['file']}: {h['line']}")
for label in ("R37 markup sinks", "R38 style writes", "R39 network", "storage other than localStorage", "messaging and navigation",
              "regex statefulness on a shared class"):
    print(f"HEAD {label}: {[(h['file'], h['match']) for h in head[label]]}")
