"""Render check of the People content (task A5, R4, R6, R7), headless Chromium, dark and reduced motion.

Each case opens the app from a seed (clicking #peopleBtn where the case says) and the golden of that state at the same
size. It compares the R3 walk of #peopleBlk on both sides (support.first_diff), and measures every part of the People
body on both sides: the box (x, y, width, height) and the computed look (colour, fill, background, font, line height,
borders, radii, padding, shadow, cursor). A probe also records where Add person moves when K2 gains a fourth and a
fifth person at 390 x 844, and what then lies under its old centre (the comment on Add person in src/ui/people.js).
Writes boxes.json and two screenshots into a new <stamp>-chromium folder beside this script. Nothing is written
elsewhere. Run from the project root: python docs/modules/split-app/qa/people-render/render.py
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
          "paddingLeft", "boxShadow", "cursor", "textAlign", "gridTemplateColumns"]
MEASURE_JS = """(styles) => {
  const parts = { body: '#peopleBody', inner: '#peopleBody > .sec-in', head: '#peopleBody .blk-head', heading: '#peopleBody h2.blk-h',
    add: '#peopleBody .blk-head > button', addIcon: '#peopleBody .blk-head > button > svg', list: '#peopleBody ul' };
  const found = {};
  const measure = (name, el) => {
    if (!el || el.getClientRects().length === 0) { found[name] = null; return; }
    const r = el.getBoundingClientRect(), style = getComputedStyle(el);
    found[name] = { box: [r.x, r.y, r.width, r.height].map((n) => Math.round(n * 100) / 100),
      styles: Object.fromEntries(styles.map((s) => [s, style[s]])) };
  };
  for (const [name, selector] of Object.entries(parts)) measure(name, document.querySelector(selector));
  document.querySelectorAll('#peopleBody ul > li').forEach((li, i) => {
    measure(`row${i + 1}`, li);
    measure(`row${i + 1}.input`, li.querySelector('input'));
    measure(`row${i + 1}.remove`, li.querySelector('button'));
    measure(`row${i + 1}.x`, li.querySelector('button > svg'));
  });
  return found;
}"""
# name -> (seed, size, header rows clicked in the app, golden)
CASES = {
    "K1-open-390": (seeds.S1, "390", ("#peopleBtn",), "bill-items-open"),
    "K1-open-360": (seeds.S1, "360", ("#peopleBtn",), "bill-items-open"),
    "K1-1280": (seeds.S1, "1280", (), "bill-items"),
    "T12-1280": (seeds.T12, "1280", (), "bill-twelve"),
    "empty-390": (None, "390", (), "bill-empty"),
    "empty-360": (None, "360", (), "bill-empty"),
    "empty-1280": (None, "1280", (), "bill-empty"),
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


def add_person_probe(browser, base):
    """K2 at 390 x 844, People open: Add person's box, then one and two clicks on it, and what lies under its old centre."""
    page = context(browser, "390", storage_state=rig.storage_state(base, seeds.S2)).new_page()
    page.goto(base + "/")
    page.locator("#peopleBtn").click()
    add = page.locator("#addPerson")
    under_js = """([x, y]) => { const el = document.elementFromPoint(x, y);
      return el ? `${el.localName}${el.id ? '#' + el.id : ''}.${el.className} ${el.getAttribute('aria-label') || ''}`.trim() : null; }"""
    steps = []
    for _ in range(3):
        box = add.bounding_box()
        centre = [box["x"] + box["width"] / 2, box["y"] + box["height"] / 2]
        steps.append({"people": page.locator("#peopleList > li").count(), "add": [round(n, 2) for n in box.values()]})
        add.click()
        steps[-1]["under_old_centre_after_click"] = page.evaluate(under_js, centre)
    return steps


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
                golden = context(browser, size).new_page()
                golden.goto((support.GOLDEN_DIR / f"{golden_name}.html").as_uri())
                pair = [page.evaluate(MEASURE_JS, STYLES) for page in (app, golden)]
                walk = support.first_diff(support.dom_walk(app, "#peopleBlk"), support.dom_walk(golden, "#peopleBlk"))
                found[name] = {"walk_first_diff": walk, "differences": differences(*pair), "app": pair[0], "golden": pair[1]}
                if name == "K1-open-390":
                    clip = {"x": 0, "y": 0, "width": 390, "height": 420}
                    app.screenshot(path=str(folder / f"{name}-app.png"), clip=clip)
                    golden.screenshot(path=str(folder / f"{name}-golden.png"), clip=clip)
            found["add-person-probe-K2-390"] = add_person_probe(browser, server.base)
            browser.close()
    finally:
        server.stop()
    (folder / "boxes.json").write_text(json.dumps(found, indent=1), encoding="utf-8")
    for name, entry in found.items():
        if isinstance(entry, dict):
            print(name, "walk:", entry["walk_first_diff"], "| parts differing:", sorted(entry["differences"]) or "none")
        else:
            print(name, json.dumps(entry))
    print("wrote", folder)


main()
