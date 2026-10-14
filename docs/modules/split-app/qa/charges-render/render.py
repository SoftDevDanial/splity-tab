"""Render check of the Charges content (task A6, R15, R10), headless Chromium, dark and reduced motion.

Each case opens the app from a seed (clicking the header rows the case names) and the golden of that state at the same
size. It compares the R3 walk of #chargesBlk on both sides (support.first_diff), and measures every part of the Charges
body on both sides: the box (x, y, width, height) and the computed look (colour, fill, background, font, line height,
borders, radii, padding, shadow, outline, cursor, alignment, grid). The case "RE-svc-focused-390" has no golden (checklist
ST-15, not drawn): it records the look of the Service charge field with its error, before and after a Tab gives it focus.
Writes boxes.json and two screenshots into a new <stamp>-chromium folder beside this script. Nothing is written
elsewhere. Run from the project root: python docs/modules/split-app/qa/charges-render/render.py
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
  const parts = { body: '#chargesBody', inner: '#chargesBody > .sec-in', heading: '#chargesH', grid: '#chargesBody .charges',
    hint: '#chargeHint' };
  for (const id of ['svc', 'sst']) {
    Object.assign(parts, { [`${id}.cell`]: `.charges > div:has(#${id})`, [`${id}.label`]: `label[for=${id}]`,
      [`${id}.field`]: `div.field:has(> #${id})`, [`${id}.input`]: `#${id}`, [`${id}.unit`]: `#${id} + .unit`,
      [`${id}.err`]: `#${id}Err`, [`${id}.errIcon`]: `#${id}Err > svg` });
  }
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
# name -> (seed, size, header rows clicked in the app, golden)
CASES = {
    "K1-open-390": (seeds.S1, "390", ("#peopleBtn", "#chargesBtn"), "bill-items-open"),
    "K1-open-360": (seeds.S1, "360", ("#peopleBtn", "#chargesBtn"), "bill-items-open"),
    "K1-1280": (seeds.S1, "1280", (), "bill-items"),
    "RE-390": (seeds.RE, "390", (), "rate-error"),
    "RE-360": (seeds.RE, "360", (), "rate-error"),
    "RE-1280": (seeds.RE, "1280", (), "rate-error"),
    "empty-1280": (None, "1280", (), "bill-empty"),
}
FOCUS_JS = """() => { const field = document.querySelector('div.field:has(> #svc)'), s = getComputedStyle(field);
  return { active: document.activeElement.id, focusVisible: document.activeElement.matches(':focus-visible'),
    border: s.borderTopColor, boxShadow: s.boxShadow, outline: [s.outlineStyle, s.outlineWidth, s.outlineColor, s.outlineOffset] }; }"""


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


def focused_error_field(browser, base):
    """ST-15: RE at 390 x 844, the Service charge field with its error, then focused by Tab from the Charges row."""
    page = context(browser, "390", storage_state=rig.storage_state(base, seeds.RE)).new_page()
    page.goto(base + "/")
    before = page.evaluate(FOCUS_JS)
    page.locator("#chargesBtn").focus()
    page.keyboard.press("Tab")
    return {"before": before, "after_tab": page.evaluate(FOCUS_JS)}


def main():
    folder = Path(__file__).resolve().parent / (datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-chromium")
    folder.mkdir(parents=True)
    server = rig.StaticServer(rig.ROOT).start()
    found = {}
    try:
        with sync_playwright() as playwright:
            browser = rig.launch(playwright, "chromium")
            for name, (seed, size, clicks, golden_name) in CASES.items():
                options = {"storage_state": rig.storage_state(server.base, seed)} if seed else {}
                app = context(browser, size, **options).new_page()
                app.goto(server.base + "/")
                for selector in clicks:
                    app.locator(selector).click()
                app.mouse.move(0, 0)  # off the header row it clicked, so no hover colour is measured
                golden = context(browser, size).new_page()
                golden.goto((support.GOLDEN_DIR / f"{golden_name}.html").as_uri())
                pair = [page.evaluate(MEASURE_JS, STYLES) for page in (app, golden)]
                walk = support.first_diff(support.dom_walk(app, "#chargesBlk"), support.dom_walk(golden, "#chargesBlk"))
                found[name] = {"walk_first_diff": walk, "differences": differences(*pair), "app": pair[0], "golden": pair[1]}
                if name == "RE-390":
                    clip = {"x": 0, "y": 100, "width": 390, "height": 300}
                    app.screenshot(path=str(folder / f"{name}-app.png"), clip=clip)
                    golden.screenshot(path=str(folder / f"{name}-golden.png"), clip=clip)
            found["RE-svc-focused-390"] = focused_error_field(browser, server.base)
            browser.close()
    finally:
        server.stop()
    (folder / "boxes.json").write_text(json.dumps(found, indent=1), encoding="utf-8")
    for name, entry in found.items():
        if "walk_first_diff" in entry:
            print(name, "walk:", entry["walk_first_diff"], "| parts differing:", sorted(entry["differences"]) or "none")
        else:
            print(name, json.dumps(entry))
    print("wrote", folder)


main()
