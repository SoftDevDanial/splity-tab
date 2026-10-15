"""Render check of the copy status line (task A10, R22, R23), headless Chromium, dark and reduced motion.

The goldens are the S4 pieces of docs/design/states.html, "S4 on the card, copied and blocked (desktop)" opened at
1280 x 800 and "S4 on the strip, copied and blocked (phone)" opened at 390 x 844 (states.md, reference widths). Each case
opens the app from the K2 seed at the same size with the clipboard recorder (copied) or reject.js (blocked), clicks the
Copy summary shown there (#copyBtn on the card, #stripCopy on the strip) and compares its p.status with the piece's.
1. The R3 walk of the paragraph (support.dom_walk). The app's id (cardStatus, stripStatus) is left out, because the
   piece is specimen chrome without one (allowed difference 5), and the R3 walk of the whole goldens checks the ids.
2. The computed look of the paragraph and of its icon.
3. The geometry that does not depend on the width of the box around it: the icon's size and its place in the paragraph,
   the gap from the icon to the text, the text's first line, the number of lines, the paragraph's height, how far the
   content sits off centre, and on the card the space between Copy summary and the paragraph.
The width of the box around the paragraph is recorded for both sides and never compared. The piece's card is one 358 px
column of the specimen page and the strip piece sits in a frame, so neither is as wide as the app's. The strip's place
of the status beside or under the Total is task A11's (the strip's content, R49), so it is recorded, not compared.
Writes result.json and a screenshot of each side into a new <stamp>-chromium folder beside this script, nothing else.
Run from the project root: python docs/modules/split-app/qa/status-render/render.py
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

P_PROPS = ["display", "alignItems", "justifyContent", "columnGap", "rowGap", "marginTop", "fontSize", "fontWeight",
           "lineHeight", "fontFamily", "letterSpacing", "color", "textAlign", "whiteSpace", "paddingTop", "paddingBottom"]
SVG_PROPS = ["width", "height", "fill", "flexShrink", "verticalAlign", "marginTop", "display"]
MEASURE_JS = """([selector, pProps, svgProps]) => {
  const p = document.querySelector(selector);
  if (!p) return null;
  const svg = p.querySelector(':scope > svg'), text = [...p.childNodes].find((node) => node.nodeType === 3);
  const range = document.createRange();
  range.selectNode(text);
  const lines = [...range.getClientRects()].filter((r) => r.width > 0);
  const round = (v) => Math.round(v * 100) / 100;
  const box = p.getBoundingClientRect(), icon = svg.getBoundingClientRect(), around = p.parentElement.getBoundingClientRect();
  const left = Math.min(icon.left, ...lines.map((r) => r.left)), right = Math.max(icon.right, ...lines.map((r) => r.right));
  const before = p.previousElementSibling, pick = (el, names) => { const s = getComputedStyle(el); return Object.fromEntries(names.map((n) => [n, s[n]])); };
  return {
    compared: {
      pStyles: pick(p, pProps), svgStyles: pick(svg, svgProps),
      iconSize: [round(icon.width), round(icon.height)], iconInP: [round(icon.left - box.left), round(icon.top - box.top)],
      iconToText: round(lines[0].left - icon.right), firstLineTopInP: round(lines[0].top - box.top),
      lines: new Set(lines.map((r) => round(r.top))).size, pHeight: round(box.height), offCentre: round((left - box.left) - (box.right - right)),
      belowCopy: before && before.matches('button.r-copy') ? round(box.top - before.getBoundingClientRect().bottom) : null,
    },
    recorded: { pWidth: round(box.width), aroundWidth: round(around.width), pBox: [box.x, box.y, box.width, box.height].map(round),
      around: p.parentElement.localName + '.' + [...p.parentElement.classList].join('.') },
  };
}"""
CASES = {  # name -> (size, clipboard script, app button, app paragraph, golden paragraph, what each screenshot shows)
    "card-copied": ((1280, 800), "recorder", "#copyBtn", "#cardStatus",
                    'section[aria-labelledby="c-s4-card"] div.card:nth-of-type(1) p.status', "div.rbody"),
    "card-blocked": ((1280, 800), "reject", "#copyBtn", "#cardStatus",
                     'section[aria-labelledby="c-s4-card"] div.card:nth-of-type(2) p.status', "div.rbody"),
    "strip-copied": ((390, 844), "recorder", "#stripCopy", "#stripStatus",
                     'section[aria-labelledby="c-s4-strip"] div.spec-frame:nth-of-type(1) p.status', "div.strip"),
    "strip-blocked": ((390, 844), "reject", "#stripCopy", "#stripStatus",
                      'section[aria-labelledby="c-s4-strip"] div.spec-frame:nth-of-type(2) p.status', "div.strip"),
}


def context(browser, size, **options):
    return rig.new_context(browser, viewport={"width": size[0], "height": size[1]}, device_scale_factor=1,
                           color_scheme="dark", reduced_motion="reduce", **options)


def without_id(walk):
    walk["attrs"].pop("id", None)
    return walk


def differences(app, golden, path=""):
    """Every compared value that differs (numbers within 0.5 px count as equal), as path -> [app, golden]."""
    if isinstance(app, dict) and isinstance(golden, dict):
        found = {}
        for key in sorted(set(app) | set(golden)):
            found.update(differences(app.get(key), golden.get(key), f"{path}/{key}"))
        return found
    if isinstance(app, list) and isinstance(golden, list) and len(app) == len(golden):
        found = {}
        for index, (a, g) in enumerate(zip(app, golden)):
            found.update(differences(a, g, f"{path}[{index}]"))
        return found
    if isinstance(app, (int, float)) and isinstance(golden, (int, float)):
        return {} if abs(app - golden) <= 0.5 else {path: [app, golden]}
    return {} if app == golden else {path: [app, golden]}


def shot(page, paragraph, holder, path):
    """A screenshot of the box `holder` around the paragraph (the card's rbody or the strip), 8 px out."""
    box = page.locator(paragraph).evaluate(f"(p) => {{ const b = p.closest('{holder}').getBoundingClientRect(); "
                                           "return [b.x, b.y, b.width, b.height]; }")
    page.screenshot(path=str(path), full_page=True,  # the pieces of states.html lie below the first screen
                    clip={"x": max(box[0] - 8, 0), "y": max(box[1] - 8, 0), "width": box[2] + 16, "height": box[3] + 16})


def main():
    folder = Path(__file__).resolve().parent / (datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-chromium")
    folder.mkdir(parents=True)
    server = rig.StaticServer(rig.ROOT).start()
    found = {}
    try:
        with sync_playwright() as playwright:
            browser = rig.launch(playwright, "chromium")
            for name, (size, clipboard, button, mine, theirs, holder) in CASES.items():
                app = context(browser, size, clipboard=clipboard,
                              storage_state=rig.storage_state(server.base, seeds.S2)).new_page()
                app.goto(server.base + "/")
                app.locator(button).click()
                app.evaluate("() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))")
                app.mouse.move(0, 0)  # no hover colour is measured
                golden = context(browser, size).new_page()
                golden.goto((support.GOLDEN_DIR / "states.html").as_uri())
                a = app.evaluate(MEASURE_JS, [mine, P_PROPS, SVG_PROPS])
                g = golden.evaluate(MEASURE_JS, [theirs, P_PROPS, SVG_PROPS])
                walk = support.first_diff(without_id(support.dom_walk(app, mine)), support.dom_walk(golden, theirs))
                found[name] = {"walk_first_diff": walk, "differences": differences(a["compared"], g["compared"]),
                               "app": a, "golden": g}
                shot(app, mine, holder, folder / f"{name}-app.png")
                shot(golden, theirs, holder, folder / f"{name}-golden.png")
            browser.close()
    finally:
        server.stop()
        print("server stopped")
    (folder / "result.json").write_text(json.dumps(found, indent=1), encoding="utf-8")
    for name, entry in found.items():
        print(name, "| walk:", entry["walk_first_diff"], "| differences:", entry["differences"] or "none",
              "| width around app/golden:", entry["app"]["recorded"]["aroundWidth"], entry["golden"]["recorded"]["aroundWidth"],
              "| lines app/golden:", entry["app"]["compared"]["lines"], entry["golden"]["compared"]["lines"])
    print("wrote", folder)


main()
