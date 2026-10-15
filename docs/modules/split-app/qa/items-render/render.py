"""Render check of the Items block and the item frame (task A8, R11 to R14, R18's marker, R56), headless Chromium, dark
and reduced motion.

Each case opens the app from a seed and the golden of that state at the same size. It compares the R3 walk of
#itemsBlock on both sides (support.first_diff), and measures every part of the block on both sides: the box (x, y,
width, height) and the computed look (colour, fill, background, font, line height, borders, radii, padding, shadow,
outline, cursor, alignment, grid). A part that is not displayed is null. It also compares the frame's two fades
(::before and ::after, which the app shows through data-up and data-down and the goldens through a "Golden only" style),
each item's ::before (the needs bar) and the list's scroll sizes. Writes boxes.json and two screenshots into a new
<stamp>-chromium folder beside this script. Nothing is written elsewhere.
Run from the project root: python docs/modules/split-app/qa/items-render/render.py
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
STYLES = ["color", "fill", "backgroundColor", "fontSize", "fontWeight", "lineHeight", "fontFamily", "borderTopWidth",
          "borderTopColor", "borderRightWidth", "borderLeftWidth", "borderBottomWidth", "borderTopLeftRadius",
          "borderTopRightRadius", "borderBottomRightRadius", "borderBottomLeftRadius", "paddingTop", "paddingRight",
          "paddingBottom", "paddingLeft", "boxShadow", "outlineStyle", "outlineWidth", "cursor", "textAlign",
          "gridTemplateColumns", "marginTop", "justifySelf"]
PSEUDO = ["content", "opacity", "top", "bottom", "left", "right", "width", "height", "backgroundColor", "backgroundImage",
          "borderTopLeftRadius"]
MEASURE_JS = """([styles, pseudo]) => {
  const one = (s) => document.querySelector(s), parts = {};
  Object.assign(parts, { block: one('#itemsBlock'), head: one('#itemsBlock > .blk-head'), itemsH: one('#itemsH'),
    add: one('#addItem'), addIcon: one('#addItem > svg'), frame: one('#frameWrap'), list: one('#itemList') });
  const items = [...document.querySelectorAll('#itemList > li')];
  items.forEach((li, i) => {
    const n = `item${i + 1}`, cells = [...(li.querySelector('.item-row')?.children ?? [])], taps = li.querySelector('.taps');
    Object.assign(parts, { [n]: li, [`${n}.row`]: li.querySelector('.item-row'), [`${n}.nameField`]: cells[0],
      [`${n}.name`]: cells[0]?.querySelector('input'), [`${n}.priceField`]: cells[1], [`${n}.unit`]: cells[1]?.querySelector('.unit'),
      [`${n}.price`]: cells[1]?.querySelector('input'), [`${n}.remove`]: cells[2], [`${n}.removeIcon`]: cells[2]?.querySelector('svg'),
      [`${n}.err`]: cells[3], [`${n}.errIcon`]: cells[3]?.querySelector('svg'), [`${n}.taps`]: taps });
    [...(taps?.children ?? [])].forEach((b, j) => Object.assign(parts, { [`${n}.tap${j + 1}`]: b,
      [`${n}.tap${j + 1}.icon`]: b.querySelector('svg'), [`${n}.tap${j + 1}.span`]: b.querySelector('span') }));
  });
  const found = {};
  for (const [name, el] of Object.entries(parts)) {
    if (!el || el.getClientRects().length === 0) { found[name] = null; continue; }
    const r = el.getBoundingClientRect(), style = getComputedStyle(el);
    found[name] = { box: [r.x, r.y, r.width, r.height].map((v) => Math.round(v * 100) / 100),
      styles: Object.fromEntries(styles.map((s) => [s, style[s]])) };
  }
  const look = (el, which) => { if (!el) return null; const s = getComputedStyle(el, which); return Object.fromEntries(pseudo.map((p) => [p, s[p]])); };
  found['frame::before'] = look(one('#frameWrap'), '::before');
  found['frame::after'] = look(one('#frameWrap'), '::after');
  items.forEach((li, i) => { found[`item${i + 1}::before`] = look(li, '::before'); });
  const list = one('#itemList');
  found.scroll = list && [list.scrollTop, list.scrollHeight, list.clientHeight];
  return found;
}"""
# name -> (seed, size, golden, clicks after load)
OPEN = ("#peopleBtn", "#chargesBtn")
CASES = {
    "K1-390": (seeds.S1, "390", "bill-items", ()), "K1-360": (seeds.S1, "360", "bill-items", ()),
    "K1-1280": (seeds.S1, "1280", "bill-items", ()),
    "K1-open-390": (seeds.S1, "390", "bill-items-open", OPEN), "K1-open-360": (seeds.S1, "360", "bill-items-open", OPEN),
    "BU-390": (seeds.S5, "390", "bill-unassigned", ()), "BU-360": (seeds.S5, "360", "bill-unassigned", ()),
    "BU-1280": (seeds.S5, "1280", "bill-unassigned", ()),
    "RE-390": (seeds.RE, "390", "rate-error", ()), "RE-360": (seeds.RE, "360", "rate-error", ()),
    "RE-1280": (seeds.RE, "1280", "rate-error", ()),
    "W1-390": (seeds.W1, "390", "bill-large", ()), "W1-360": (seeds.W1, "360", "bill-large", ()),
    "W1-1280": (seeds.W1, "1280", "bill-large", ()),
}


def context(browser, size, **options):
    width, height = SIZES[size]
    return rig.new_context(browser, viewport={"width": width, "height": height}, device_scale_factor=1,
                           color_scheme="dark", reduced_motion="reduce", **options)


def differences(app, golden):
    """The parts whose box (within 0.5 px) or look differ, or that one side lacks. Entries without a box (the pseudo
    elements, the scroll sizes) must be equal."""
    found = {}
    for name in sorted(set(app) | set(golden)):
        a, g = app.get(name), golden.get(name)
        if a is None or g is None or not isinstance(a, dict) or "box" not in a:
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
            for name, (seed, size, golden_name, clicks) in CASES.items():
                app = context(browser, size, storage_state=rig.storage_state(server.base, seed)).new_page()
                app.goto(server.base + "/")
                for selector in clicks:
                    app.locator(selector).click()
                app.mouse.move(0, 0)  # no hover colour is measured
                golden = context(browser, size).new_page()
                golden.goto((support.GOLDEN_DIR / f"{golden_name}.html").as_uri())
                pair = [page.evaluate(MEASURE_JS, [STYLES, PSEUDO]) for page in (app, golden)]
                walk = support.first_diff(support.dom_walk(app, "#itemsBlock"), support.dom_walk(golden, "#itemsBlock"))
                marks = app.evaluate("() => [document.querySelector('#frameWrap').getAttribute('data-up'),"
                                     " document.querySelector('#frameWrap').getAttribute('data-down')]")
                found[name] = {"walk_first_diff": walk, "marks": marks, "differences": differences(*pair),
                               "app": pair[0], "golden": pair[1]}
                if name in ("K1-390", "BU-1280"):
                    box = pair[1]["block"]["box"]
                    clip = {"x": max(box[0] - 16, 0), "y": max(box[1] - 16, 0), "width": box[2] + 32, "height": min(box[3] + 32, 700)}
                    app.screenshot(path=str(folder / f"{name}-app.png"), clip=clip, full_page=True)
                    golden.screenshot(path=str(folder / f"{name}-golden.png"), clip=clip, full_page=True)
            browser.close()
    finally:
        server.stop()
        print("server stopped")
    (folder / "boxes.json").write_text(json.dumps(found, indent=1), encoding="utf-8")
    for name, entry in found.items():
        print(name, "walk:", entry["walk_first_diff"], "| marks:", entry["marks"], "| parts differing:",
              sorted(entry["differences"]) or "none")
    print("wrote", folder)


main()
