"""Probe of the Splits sheet's Pick again chip (task A15, R54), which no qa.md scenario presses (BUILD.md, F-A15-1).
On RND at 390 x 844, open Splits, then (1) click the sheet's Pick again chip and (2) focus it by script and press Enter.
Each step reads the sheet's rows, the draft's order, whether the chip has focus and whether it is the same node.
Headless, the clipboard stand-in in the context (rig.new_context). Writes result.json into a new <stamp>-<engine>
folder beside this script. Nothing is written elsewhere. Run from the project root,
python docs/modules/split-app/qa/sheet-pick-again-probe/probe.py <engine>
"""
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("tests/browser").resolve()))
import rig  # noqa: E402
import seeds  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

engine = sys.argv[1]
folder = Path(__file__).resolve().parent / f"{datetime.datetime.now():%Y%m%d-%H%M%S}-{engine}"
folder.mkdir(parents=True)
CHIP = "#splitsDlg .r-spare-acts button:not([aria-haspopup])"
READ_JS = """(chip) => ({
  rows: [...document.querySelectorAll('#splitsDlg ul.r-splits > li')].map((li) => li.textContent),
  order: JSON.parse(localStorage.getItem('split.draft') ?? 'null')?.bill.spare.order ?? null,
  chipText: document.querySelector(chip)?.textContent ?? null,
  chipFocused: document.activeElement === document.querySelector(chip),
  sameChip: window.testChip === document.querySelector(chip),
})"""
steps = {}
server = rig.StaticServer(rig.ROOT).start()
try:
    with sync_playwright() as playwright:
        browser = rig.launch(playwright, engine)
        context = rig.new_context(browser, viewport={"width": 390, "height": 844}, device_scale_factor=1, color_scheme="dark",
                                  reduced_motion="reduce", storage_state=rig.storage_state(server.base, seeds.RND))
        page = context.new_page()
        page.goto(server.base + "/")
        page.locator("#splitsBtn").click()
        steps["count"] = page.locator(CHIP).count()
        steps["before"] = page.evaluate(READ_JS, CHIP)
        page.locator(CHIP).click()
        steps["after click"] = page.evaluate(READ_JS, CHIP)
        page.evaluate("(chip) => { window.testChip = document.querySelector(chip); window.testChip.focus(); }", CHIP)
        page.keyboard.press("Enter")
        steps["after Enter"] = page.evaluate(READ_JS, CHIP)
        steps["stand-in clipboard writes"] = page.evaluate("window.testClipboardWrites")
        browser.close()
finally:
    server.stop()
(folder / "result.json").write_text(json.dumps(steps, indent=1), encoding="utf-8")
print(json.dumps(steps))
print("wrote", folder, sorted(p.name for p in folder.iterdir()))
