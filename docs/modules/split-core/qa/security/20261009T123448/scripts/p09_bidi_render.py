"""P09. Headless Chromium: how the summary texts render (visual lines, bidi reordering), and which
hostile characters an <input type="text"> lets through. Never touches the OS clipboard. Writes no file.
Usage: python -I -B p09_bidi_render.py <scripts-dir>
"""
import json
import os
import subprocess
import sys

from playwright.sync_api import sync_playwright

HERE = sys.argv[1]
texts = json.loads(subprocess.run(
    ["node", os.path.join(HERE, "p09-texts.mjs")], capture_output=True, text=True, encoding="utf-8",
    timeout=30, cwd=HERE, check=True).stdout)

MEASURE = r"""
({ text, mode }) => {
  const host = document.getElementById('host');
  host.replaceChildren();
  const box = document.createElement('div');
  box.style.whiteSpace = mode === 'pre-wrap' ? 'pre-wrap' : 'pre';
  box.style.font = '16px monospace';
  box.style.width = '1800px';
  host.appendChild(box);
  const nodes = [];
  const LF = String.fromCodePoint(10);
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
  const esc = (s) => [...s].map((c) => { const p = c.codePointAt(0); return p >= 32 && p < 127 ? c : '<U+' + p.toString(16).toUpperCase().padStart(4, '0') + '>'; }).join('');
  return [...lines.keys()].sort((a, b) => a - b).map((t) => {
    const cs = lines.get(t);
    const logical = cs.map((c) => c.c).join('');
    const visual = [...cs].sort((a, b) => a.left - b.left).map((c) => c.c).join('');
    return { visual: esc(visual), reordered: visual !== logical };
  });
}
"""

INPUT_CHARS = [
    ("LF", 0x0A), ("CR", 0x0D), ("VT", 0x0B), ("FF", 0x0C), ("NEL", 0x85), ("LS", 0x2028), ("PS", 0x2029),
    ("NUL", 0x00), ("FS", 0x1C), ("GS", 0x1D), ("RS", 0x1E), ("ESC", 0x1B), ("TAB", 0x09),
    ("RLO", 0x202E), ("RLI", 0x2067), ("RLM", 0x200F), ("ZWSP", 0x200B),
]

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    pids = []
    try:
        cdp = browser.new_browser_cdp_session()
        info = cdp.send("SystemInfo.getProcessInfo")
        pids = [(p["type"], p["id"]) for p in info.get("processInfo", [])]
    except Exception as exc:  # noqa: BLE001 - PID discovery is best effort; the sweep covers the rest
        pids = [("unknown", str(exc))]
    print(f"python pid {os.getpid()}; chromium {browser.version}; chromium processes {pids}")
    page = browser.new_page(viewport={"width": 1900, "height": 900})
    page.set_content("<!doctype html><meta charset=utf-8><body style='margin:0'><div id=host></div>")

    print("\n== rendering: visual lines (6 = no forged line) and bidi reordering ==")
    for name, text in texts.items():
        for mode in ("pre", "pre-wrap", "br"):
            lines = page.evaluate(MEASURE, {"text": text, "mode": mode})
            reordered = [i + 1 for i, l in enumerate(lines) if l["reordered"]]
            print(f"{name:42} {mode:8} visual lines {len(lines)}  reordered lines {reordered}")
            if mode == "pre" and (reordered or len(lines) != 6):
                for i, l in enumerate(lines):
                    print(f"      line {i + 1}: {l['visual']}")

    print("\n== <input type=text maxlength=20>: what survives keyboard.insert_text and a script .value set ==")
    page.set_content("<!doctype html><meta charset=utf-8><input id=i type=text maxlength=20 autocomplete=off>")
    for label, cp in INPUT_CHARS:
        page.evaluate("document.getElementById('i').value = ''")
        page.focus("#i")
        page.keyboard.insert_text("A" + chr(cp) + "B")
        typed = page.evaluate("[...document.getElementById('i').value].map((c) => c.codePointAt(0))")
        page.evaluate("(cp) => { document.getElementById('i').value = 'A' + String.fromCodePoint(cp) + 'B'; }", cp)
        scripted = page.evaluate("[...document.getElementById('i').value].map((c) => c.codePointAt(0))")
        print(f"{label:5} U+{cp:04X}  insert_text kept={cp in typed!s:5} value={typed}  script .value kept={cp in scripted!s:5}")
    browser.close()
print("\nbrowser closed")
