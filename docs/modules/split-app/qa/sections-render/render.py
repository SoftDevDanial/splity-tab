"""Render check of the People and Charges header rows (task A4, R48), headless Chromium, dark and reduced motion.

Each case opens the app from a seed (clicking header rows where the case says) and the golden of that state at the
same size, and measures the rows, their names, summaries, icons and carets on both sides: the box (x, y, width,
height) and the computed colour, font, line height, visibility, transform and fill. The section bodies are measured
too, though their content is still the 1.0 People and Charges blocks until tasks A5 and A6. The folded "Check"
row is compared by its styles with the first specimen of "Charges folded with an error" in states.html. Writes
boxes.json and four screenshots into a new <stamp>-chromium folder beside this script. Nothing is written elsewhere.
Run from the project root: python docs/modules/split-app/qa/sections-render/render.py
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
PARTS = {
    "peopleBlk": "#peopleBlk", "peopleRow": "#peopleBtn", "peopleName": "#peopleName", "peopleSum": "#peopleSum",
    "peopleTxt": "#peopleSum .sec-txt", "peopleCaret": "#peopleBtn .sec-caret", "peopleBody": "#peopleBody",
    "chargesBlk": "#chargesBlk", "chargesRow": "#chargesBtn", "chargesName": "#chargesName", "chargesSum": "#chargesSum",
    "chargesIcon": "#chargesSum > svg.ic", "chargesTxt": "#chargesSum .sec-txt", "chargesCaret": "#chargesBtn .sec-caret",
    "chargesBody": "#chargesBody",
}
SPECIMEN_PARTS = {
    "chargesRow": "#st1ChargesSum", "chargesSum": "#st1ChargesSum", "chargesIcon": "#st1ChargesSum > svg.ic",
    "chargesTxt": "#st1ChargesSum .sec-txt", "chargesName": "#st1ChargesName",
}
STYLES = ["color", "fontSize", "fontWeight", "lineHeight", "visibility", "transform", "fill", "textAlign", "whiteSpace"]
MEASURE_JS = """([parts, styles]) => Object.fromEntries(Object.entries(parts).map(([name, selector]) => {
  let el = document.querySelector(selector);
  if (el && name === 'chargesRow' && el.matches('span')) el = el.closest('button');
  if (!el || el.getClientRects().length === 0) return [name, null];
  const r = el.getBoundingClientRect(), style = getComputedStyle(el);
  return [name, { box: [r.x, r.y, r.width, r.height].map((n) => Math.round(n * 100) / 100),
    styles: Object.fromEntries(styles.map((s) => [s, style[s]])),
    text: el.matches('.sec-txt') ? el.innerText : undefined, cls: el.getAttribute('class') }];
}))"""
# name -> (seed, size, header rows clicked in the app, golden)
CASES = {
    "K1-folded-390": (seeds.S1, "390", (), "bill-items"),
    "K1-folded-360": (seeds.S1, "360", (), "bill-items"),
    "K1-1280": (seeds.S1, "1280", (), "bill-items"),
    "K1-open-390": (seeds.S1, "390", ("#peopleBtn", "#chargesBtn"), "bill-items-open"),
    "K1-open-360": (seeds.S1, "360", ("#peopleBtn", "#chargesBtn"), "bill-items-open"),
    "RE-390": (seeds.RE, "390", (), "rate-error"),
    "T12-390": (seeds.T12, "390", (), "bill-twelve"),
    "T12-360": (seeds.T12, "360", (), "bill-twelve"),
    "empty-390": (None, "390", (), "bill-empty"),
}


def context(browser, size, **options):
    width, height = SIZES[size]
    return rig.new_context(browser, viewport={"width": width, "height": height}, device_scale_factor=1,
                           color_scheme="dark", reduced_motion="reduce", **options)


def differences(app, golden):
    """The parts whose box (within 0.5 px), styles, text or class differ."""
    found = {}
    for name in app:
        a, g = app[name], golden.get(name)
        if a is None or g is None:
            if a != g:
                found[name] = {"app": a, "golden": g}
            continue
        boxes_close = all(abs(x - y) <= 0.5 for x, y in zip(a["box"], g["box"]))
        if not boxes_close or a["styles"] != g["styles"] or a.get("text") != g.get("text") or a["cls"] != g["cls"]:
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
            for name, (seed, size, clicks, golden_name) in CASES.items():
                options = {"storage_state": rig.storage_state(server.base, seed)} if seed else {}
                app = context(browser, size, **options).new_page()
                app.goto(server.base + "/")
                for selector in clicks:
                    app.locator(selector).click()
                golden = context(browser, size).new_page()
                golden.goto((support.GOLDEN_DIR / f"{golden_name}.html").as_uri())
                pair = [page.evaluate(MEASURE_JS, [PARTS, STYLES]) for page in (app, golden)]
                found[name] = {"differences": differences(*pair), "app": pair[0], "golden": pair[1]}
                if name in ("K1-folded-390", "K1-open-390"):
                    clip = {"x": 0, "y": 0, "width": SIZES[size][0], "height": 560}
                    app.screenshot(path=str(folder / f"{name}-app.png"), clip=clip)
                    golden.screenshot(path=str(folder / f"{name}-golden.png"), clip=clip)
            folded = context(browser, "390", storage_state=rig.storage_state(server.base, seeds.RE)).new_page()
            folded.goto(server.base + "/")
            folded.locator("#chargesBtn").click()
            specimen = context(browser, "390").new_page()
            specimen.goto((support.GOLDEN_DIR / "states.html").as_uri())
            app_parts = folded.evaluate(MEASURE_JS, [{name: PARTS[name] for name in SPECIMEN_PARTS}, STYLES])
            spec_parts = specimen.evaluate(MEASURE_JS, [SPECIMEN_PARTS, STYLES])
            found["RE-folded-390-vs-specimen"] = {
                "styles_equal": {name: app_parts[name]["styles"] == spec_parts[name]["styles"] for name in SPECIMEN_PARTS},
                "sizes": {name: [app_parts[name]["box"][2:], spec_parts[name]["box"][2:]] for name in ("chargesIcon",)},
                "text": [app_parts["chargesTxt"]["text"], spec_parts["chargesTxt"]["text"]],
                "app": app_parts, "specimen": spec_parts,
            }
            browser.close()
    finally:
        server.stop()
    (folder / "boxes.json").write_text(json.dumps(found, indent=1), encoding="utf-8")
    for name, entry in found.items():
        if "differences" in entry:
            print(name, "differs in", sorted(entry["differences"]) or "nothing")
        else:
            print(name, entry["styles_equal"], entry["sizes"], entry["text"])
    print("wrote", folder)


main()
