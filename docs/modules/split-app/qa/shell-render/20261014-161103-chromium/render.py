"""Scratch render check for task A2, not part of the suite. Run from the project root.

Renders the cold boot and docs/design/bill-empty.html (read only, served) at 1280 x 800 and 390 x 844 in headless
Chromium through the rig, presses nothing, and records a screenshot of each and the boxes of the shell's parts.
"""
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, "tests/browser")
import rig  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

PARTS = ["header.top", "div.brand", "svg.mark", "h1.word", "#notes", "#newBill", "main.layout", "#stage", "#card", "#rbody",
         "div.r-total", "div.r-empty", "div.r-empty svg", "#work", "#strip", "#stripInfo", "#splitsBtn", "#stripCopy"]
BOXES_JS = """(parts) => Object.fromEntries(parts.map((s) => {
  const el = document.querySelector(s);
  if (!el) return [s, null];
  const b = el.getBoundingClientRect(), cs = getComputedStyle(el);
  return [s, { box: [b.x, b.y, b.width, b.height].map((n) => Math.round(n * 10) / 10), display: cs.display,
               color: cs.color, background: cs.backgroundColor, font: `${cs.fontWeight} ${cs.fontSize}/${cs.lineHeight}`,
               text: (el.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 80) }];
}))"""

out = Path("docs/modules/split-app/qa/shell-render") / (datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-chromium")
out.mkdir(parents=True, exist_ok=False)
record = {}
server = rig.StaticServer().start()
try:
    with sync_playwright() as playwright:
        browser = rig.launch(playwright, "chromium")
        try:
            for width, height in ((1280, 800), (390, 844)):
                for name, path in (("app", "/"), ("golden", "/docs/design/bill-empty.html")):
                    context = rig.new_context(browser, viewport={"width": width, "height": height}, device_scale_factor=1,
                                              color_scheme="dark", reduced_motion="reduce")
                    try:
                        page = context.new_page()
                        page.goto(server.base + path)
                        page.wait_for_timeout(300)
                        page.screenshot(path=str(out / f"{name}-{width}.png"))
                        record[f"{name}-{width}"] = page.evaluate(BOXES_JS, PARTS)
                    finally:
                        context.close()
        finally:
            browser.close()
finally:
    server.stop()
(out / "boxes.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
print(out.as_posix())
