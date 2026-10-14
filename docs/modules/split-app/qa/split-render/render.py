"""Render check of the Split block and the Subtotal block (task A7, R8, R9, R10), headless Chromium, dark and reduced motion.

Each case opens the app from a seed and the golden of that state at the same size. It compares the R3 walk of #splitBlk
and of #evenBlock on both sides (support.first_diff), and measures every part of the two blocks on both sides: the box
(x, y, width, height) and the computed look (colour, fill, background, font, line height, borders, radii, padding,
shadow, outline, cursor, alignment, grid). A part that is not displayed is null. Writes boxes.json and two screenshots
into a new <stamp>-chromium folder beside this script. Nothing is written elsewhere.
Run from the project root: python docs/modules/split-app/qa/split-render/render.py
"""
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("tests/browser").resolve()))
import rig  # noqa: E402
import seeds  # noqa: E402
import support  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

SIZES = {"390": (390, 844), "360": (360, 780), "1280": (1280, 800)}
STYLES = ["color", "fill", "backgroundColor", "fontSize", "fontWeight", "lineHeight", "borderTopWidth", "borderTopColor",
          "borderRightWidth", "borderLeftWidth", "borderBottomWidth", "borderTopLeftRadius", "borderTopRightRadius",
          "borderBottomRightRadius", "borderBottomLeftRadius", "paddingTop", "paddingRight", "paddingBottom",
          "paddingLeft", "boxShadow", "outlineStyle", "outlineWidth", "outlineColor", "outlineOffset", "cursor",
          "textAlign", "gridTemplateColumns", "marginTop"]
MEASURE_JS = """(styles) => {
  const parts = { split: '#splitBlk', splitH: '#splitH', switch: '#splitBlk .mode-sw', evenLabel: 'label[for=modeEven]',
    itemLabel: 'label[for=modeItem]', even: '#evenBlock', subLabel: 'label[for=evenSub]', field: '#evenField',
    unit: '#evenField > .unit', input: '#evenSub', err: '#evenErr', errIcon: '#evenErr > svg' };
  const found = {};
  for (const [name, selector] of Object.entries(parts)) {
    const el = document.querySelector(selector);
    if (!el || el.getClientRects().length === 0) { found[name] = null; continue; }
    const r = el.getBoundingClientRect(), style = getComputedStyle(el);
    found[name] = { box: [r.x, r.y, r.width, r.height].map((n) => Math.round(n * 100) / 100),
      styles: Object.fromEntries(styles.map((s) => [s, style[s]])) };
  }
  return found;
}"""
# name -> (seed, size, golden)
CASES = {
    "K2-390": (seeds.S2, "390", "bill-even"),
    "K2-360": (seeds.S2, "360", "bill-even"),
    "K2-1280": (seeds.S2, "1280", "bill-even"),
    "empty-390": (None, "390", "bill-empty"),
    "empty-360": (None, "360", "bill-empty"),
    "empty-1280": (None, "1280", "bill-empty"),
}


def context(browser, size, **options):
    width, height = SIZES[size]
    return rig.new_context(browser, viewport={"width": width, "height": height}, device_scale_factor=1,
                           color_scheme="dark", reduced_motion="reduce", **options)


def differences(app, golden):
    """The parts whose box (within 0.5 px) or look differ, or that one side lacks."""
    found = {}
    for name in sorted(set(app) | set(golden)):
        a, g = app.get(name), golden.get(name)
        if a is None or g is None:
            if a != g:
                found[name] = {"app": a, "golden": g}
            continue
        if not all(abs(x - y) <= 0.5 for x, y in zip(a["box"], g["box"])) or a["styles"] != g["styles"]:
            found[name] = {"app": a, "golden": g}
    return found


def main():
    folder = Path(__file__).resolve().parent / (datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-chromium")
    folder.mkdir(parents=True)
    server = rig.StaticServer(rig.ROOT).start()
    found = {}
    try:
        with sync_playwright() as playwright:
            browser = rig.launch(playwright, "chromium")
            for name, (seed, size, golden_name) in CASES.items():
                options = {"storage_state": rig.storage_state(server.base, seed)} if seed else {}
                app = context(browser, size, **options).new_page()
                app.goto(server.base + "/")
                app.mouse.move(0, 0)  # no hover colour is measured
                golden = context(browser, size).new_page()
                golden.goto((support.GOLDEN_DIR / f"{golden_name}.html").as_uri())
                pair = [page.evaluate(MEASURE_JS, STYLES) for page in (app, golden)]
                walks = {block: support.first_diff(support.dom_walk(app, block), support.dom_walk(golden, block))
                         for block in ("#splitBlk", "#evenBlock")}
                found[name] = {"walk_first_diff": walks, "differences": differences(*pair), "app": pair[0], "golden": pair[1]}
                if name == "K2-390":
                    top = pair[1]["split"]["box"][1] - 16
                    clip = {"x": 0, "y": top, "width": 390, "height": 180}
                    app.screenshot(path=str(folder / f"{name}-app.png"), clip=clip)
                    golden.screenshot(path=str(folder / f"{name}-golden.png"), clip=clip)
            browser.close()
    finally:
        server.stop()
        print("server stopped")
    (folder / "boxes.json").write_text(json.dumps(found, indent=1), encoding="utf-8")
    for name, entry in found.items():
        print(name, "walk:", entry["walk_first_diff"], "| parts differing:", sorted(entry["differences"]) or "none")
    print("wrote", folder)


main()
