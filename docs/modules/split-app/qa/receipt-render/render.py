"""Render check of the receipt on the card (task A9, R16 to R21), headless Chromium, dark and reduced motion, 1280 x 800
(the card is not displayed below 1024 px).

Each case opens the app from a seed and the golden of that state. It compares the R3 walk of #rbody on both sides
(support.first_diff), with the golden's div.r-spare left out, because the spare line and chip are task A13's (R51). It
then measures every element of #card on both sides, each named by its path of tag and classes (an index only among
siblings of the same name, so a missing r-spare does not rename what follows it): the box (x, y, width, height) and
the computed look (colour, fill, background, font, line height, borders, radii, padding, margins, shadow, alignment,
grid, white space). An element that is not displayed is null. A part whose only difference is its top edge, moved up by
exactly the golden r-spare's outer height (its margin-top plus its height), is reported as "moved by the spare line",
and so is the height of the card and of #rbody, the two boxes that hold it. Writes boxes.json and two screenshots into a new <stamp>-chromium folder beside this
script. Nothing is written elsewhere.
Run from the project root: python docs/modules/split-app/qa/receipt-render/render.py
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

SIZE = (1280, 800)
STYLES = ["color", "fill", "backgroundColor", "backgroundImage", "fontSize", "fontWeight", "lineHeight", "fontFamily",
          "letterSpacing", "borderTopWidth", "borderTopColor", "borderBottomWidth", "borderTopLeftRadius", "paddingTop",
          "paddingRight", "paddingBottom", "paddingLeft", "marginTop", "marginBottom", "boxShadow", "textAlign",
          "justifySelf", "alignSelf", "gridTemplateColumns", "gridTemplateRows", "gridColumnStart", "gridColumnEnd",
          "whiteSpace", "display", "position"]
MEASURE_JS = """(styles) => {
  const found = {};
  const visit = (el, path) => {
    const counts = {};
    for (const child of el.children) {
      const label = child.localName + [...child.classList].map((name) => '.' + name).join('');
      counts[label] = (counts[label] ?? -1) + 1;
      const name = `${path}/${label}[${counts[label]}]`;
      if (child.getClientRects().length === 0) { found[name] = null; continue; }
      const box = child.getBoundingClientRect(), style = getComputedStyle(child);
      found[name] = { box: [box.x, box.y, box.width, box.height].map((v) => Math.round(v * 100) / 100),
        styles: Object.fromEntries(styles.map((s) => [s, style[s]])) };
      visit(child, name);
    }
  };
  const card = document.querySelector('#card');
  const box = card.getBoundingClientRect();
  found.card = { box: [box.x, box.y, box.width, box.height].map((v) => Math.round(v * 100) / 100), styles: {} };
  visit(card, 'card');
  return found;
}"""
# name -> (seed, golden)
CASES = {
    "K1": (seeds.S1, "bill-items"), "K2": (seeds.S2, "bill-even"), "BU": (seeds.S5, "bill-unassigned"),
    "T12": (seeds.T12, "bill-twelve"), "W1": (seeds.W1, "bill-large"), "RE": (seeds.RE, "rate-error"),
    "BE": (None, "bill-empty"),
}
SPARE = "card/div.rbody[0]/div.r-spare[0]"
GROWS = ("card", "card/div.rbody[0]")  # the two boxes that hold the spare line, so only their height moves with it


def context(browser, **options):
    return rig.new_context(browser, viewport={"width": SIZE[0], "height": SIZE[1]}, device_scale_factor=1,
                           color_scheme="dark", reduced_motion="reduce", **options)


def without_spare(walk):
    """The golden's walk of #rbody with div.r-spare left out (task A13 draws it)."""
    walk["children"] = [child for child in walk["children"] if "r-spare" not in child["cls"].split()]
    return walk


def spare_height(golden):
    """The golden r-spare's outer height, its margin-top plus its height, or 0 when the golden has none."""
    spare = golden.get(SPARE)
    return 0 if not spare else spare["box"][3] + float(spare["styles"]["marginTop"].removesuffix("px"))


def differences(app, golden):
    """Every part that differs, sorted into "moved by the spare line" (only its top, or for the card only its height,
    moved by the golden spare's outer height) and "other". Parts of the golden's r-spare are listed apart."""
    shift = spare_height(golden)
    moved, other, spare_only = [], {}, []
    for name in sorted(set(app) | set(golden)):
        a, g = app.get(name), golden.get(name)
        if name.startswith(SPARE):
            spare_only.append(name)
            continue
        if a == g:
            continue
        if a and g and a["styles"] == g["styles"]:
            close = [abs(x - y) <= 0.5 for x, y in zip(a["box"], g["box"])]
            if all(close):
                continue
            dy, dh = g["box"][1] - a["box"][1], g["box"][3] - a["box"][3]
            if name not in GROWS and close[0] and close[2] and close[3] and abs(dy - shift) <= 0.5:
                moved.append(name)
                continue
            if name in GROWS and close[0] and close[1] and close[2] and abs(dh - shift) <= 0.5:
                moved.append(name)
                continue
        other[name] = {"app": a, "golden": g}
    return {"spare_outer_height": shift, "moved_by_the_spare_line": moved, "golden_spare_parts": spare_only, "other": other}


def main():
    folder = Path(__file__).resolve().parent / (datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-chromium")
    folder.mkdir(parents=True)
    server = rig.StaticServer(rig.ROOT).start()
    found = {}
    try:
        with sync_playwright() as playwright:
            browser = rig.launch(playwright, "chromium")
            for name, (seed, golden_name) in CASES.items():
                options = {"storage_state": rig.storage_state(server.base, seed)} if seed else {}
                app = context(browser, **options).new_page()
                app.goto(server.base + "/")
                app.mouse.move(0, 0)  # no hover colour is measured
                golden = context(browser).new_page()
                golden.goto((support.GOLDEN_DIR / f"{golden_name}.html").as_uri())
                pair = [page.evaluate(MEASURE_JS, STYLES) for page in (app, golden)]
                walk = support.first_diff(support.dom_walk(app, "#rbody"), without_spare(support.dom_walk(golden, "#rbody")))
                rows = app.evaluate("() => document.querySelector('#splits')?.style.getPropertyValue('--rows') ?? null")
                found[name] = {"walk_first_diff": walk, "rows_property": rows, **differences(*pair), "app": pair[0], "golden": pair[1]}
                if name in ("K1", "T12"):
                    box = pair[1]["card"]["box"]
                    clip = {"x": box[0] - 8, "y": box[1] - 8, "width": box[2] + 16, "height": box[3] + 16}
                    app.screenshot(path=str(folder / f"{name}-app.png"), clip=clip)
                    golden.screenshot(path=str(folder / f"{name}-golden.png"), clip=clip)
            browser.close()
    finally:
        server.stop()
        print("server stopped")
    (folder / "boxes.json").write_text(json.dumps(found, indent=1), encoding="utf-8")
    for name, entry in found.items():
        print(name, "walk:", entry["walk_first_diff"], "| --rows:", entry["rows_property"], "| spare outer height:",
              entry["spare_outer_height"], "| moved by it:", len(entry["moved_by_the_spare_line"]),
              "| golden spare parts:", len(entry["golden_spare_parts"]), "| other differences:", sorted(entry["other"]) or "none")
    print("wrote", folder)


main()
