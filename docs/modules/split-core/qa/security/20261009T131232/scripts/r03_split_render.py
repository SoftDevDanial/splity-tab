"""R03. Real consumers of the HEAD summary text: Python str.splitlines, a NUL-terminated read, and headless
Chromium layout (visual lines and bidi order). Never touches the OS clipboard. Writes no file.
Usage: python -P -B r03_split_render.py <scripts-dir>
"""
import json
import os
import subprocess
import sys

from playwright.sync_api import sync_playwright

HERE = sys.argv[1]
cases = json.loads(subprocess.run(
    ["node", os.path.join(HERE, "r02-texts.mjs")], capture_output=True, text=True, encoding="utf-8",
    timeout=60, cwd=HERE, check=True).stdout)

print(f"python pid {os.getpid()}; cases {len(cases)}")
print("\n== Python str.splitlines and a NUL-terminated read on every case ==")
split_bad = []
for c in cases:
    text = c["text"]
    n = len(text.splitlines())
    cut = text.split("\x00", 1)[0]
    if n != 6 or cut != text:
        split_bad.append((c["title"], n, cut != text))
print(f"cases where splitlines != 6 lines or a NUL cuts the text: {len(split_bad)} of {len(cases)} {split_bad[:5]}")

MEASURE = r"""
({ text, mode }) => {
  const host = document.getElementById('host');
  host.replaceChildren();
  const box = document.createElement('div');
  box.style.whiteSpace = mode === 'pre-wrap' ? 'pre-wrap' : 'pre';
  box.style.font = '16px monospace';
  box.style.width = '1800px';
  host.appendChild(box);
  const LF = String.fromCodePoint(10);
  const nodes = [];
  if (mode === 'br') {
    text.split(LF).forEach((line, i) => {
      if (i) box.appendChild(document.createElement('br'));
      const t = document.createTextNode(line); box.appendChild(t); nodes.push(t);
    });
  } else {
    const t = document.createTextNode(text); box.appendChild(t); nodes.push(t);
  }
  const chars = [];
  const range = document.createRange();
  for (const node of nodes) {
    const s = node.data;
    for (let i = 0; i < s.length; i++) {
      if (s[i] === LF) continue;
      range.setStart(node, i); range.setEnd(node, i + 1);
      const r = range.getClientRects()[0] || range.getBoundingClientRect();
      chars.push({ c: s[i], top: Math.round(r.top), left: r.left });
    }
  }
  const lines = new Map();
  for (const ch of chars) { if (!lines.has(ch.top)) lines.set(ch.top, []); lines.get(ch.top).push(ch); }
  return [...lines.keys()].sort((a, b) => a - b).map((t) => {
    const cs = lines.get(t);
    return { logical: cs.map((c) => c.c).join(''), visual: [...cs].sort((a, b) => a.left - b.left).map((c) => c.c).join('') };
  });
}
"""


def esc(s):
    return "".join(c if 32 <= ord(c) < 127 else f"<U+{ord(c):04X}>" for c in s)


with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    try:
        info = browser.new_browser_cdp_session().send("SystemInfo.getProcessInfo")
        pids = [(p["type"], p["id"]) for p in info.get("processInfo", [])]
    except Exception as exc:  # noqa: BLE001 - PID discovery is best effort; the sweep covers the rest
        pids = [("unknown", str(exc))]
    print(f"\nchromium {browser.version}; chromium processes {pids}")
    page = browser.new_page(viewport={"width": 1900, "height": 900})
    page.set_content("<!doctype html><meta charset=utf-8><body style='margin:0'><div id=host></div>")
    print("\n== Chromium layout: 6 visual lines, the hostile row still shows its share in reading order, other rows untouched ==")
    render_bad = 0
    for c in cases:
        for mode in ("pre", "pre-wrap", "br"):
            lines = page.evaluate(MEASURE, {"text": c["text"], "mode": mode})
            problems = []
            if len(lines) != 6:
                problems.append(f"{len(lines)} visual lines")
            else:
                for i, l in enumerate(lines):
                    if i == c["row"]:
                        if c["share"] not in l["visual"]:
                            problems.append(f"row reads '{esc(l['visual'])}'")
                    elif l["visual"] != l["logical"]:
                        problems.append(f"line {i + 1} reordered '{esc(l['visual'])}'")
            if problems:
                render_bad += 1
            if problems or not c["title"].startswith("class "):
                if mode == "pre":
                    row = lines[c["row"]]["visual"] if len(lines) == 6 else "?"
                    print(f"{'FAIL' if problems else 'OK  '} {c['title']:46} {mode:8} row visual '{esc(row)}' {'; '.join(problems)}")
    print(f"class cases: {sum(1 for c in cases if c['title'].startswith('class '))}; layout failures over all cases and 3 modes: {render_bad}")
    browser.close()
print("\nbrowser closed")
