"""Render check of the strip (task A11, R49), headless Chromium, dark and reduced motion.

Part 1, the phone goldens. Each golden that draws the strip is opened at 390 x 844 and 360 x 780 beside the app on the
seed of that state (after the golden's clicks, for bill-items-open). It compares the R3 walk of #strip
(support.first_diff), then every element of #strip on both sides, each named by its path of tag and classes: the box
(x, y, width, height, within 0.5 px) and the computed look (STYLES). It also compares what --strip-h drives on the page:
the root's computed --strip-h (the golden's "Golden only" value, or the CSS's 111px, against the app's measured one),
.work's bottom padding, html's scroll-padding-bottom and the page's scroll height.
Part 2, the strip pieces of states.html at 390 x 844 (states.md): "S4 on the strip, copied and blocked" against the app
on K2 after a click on #stripCopy (the clipboard recorder, then reject.js), and "By item, nothing to work out yet"
against a cold boot after a click on "By item". The pieces are specimen chrome without ids (allowed difference 5), sit
in a 358 px frame and are positioned relative (.spec .strip), so the walk leaves the app's ids and the aria-controls
that names one out, the look leaves out position and the grid tracks (resolved in px from the width, compared as the
ratio of the two buttons instead), and boxes are recorded but never compared. The heights, the status's place beside or
under the Total, its number of lines and the message's lines are compared. The pieces draw K1's 69.26 where the app's
K2 shows 116.60 (ST-07), so the figure's text is recorded, and the walk takes the piece's.
Writes result.json and screenshots into a new <stamp>-chromium folder beside this script. Nothing is written elsewhere.
Run from the project root: python docs/modules/split-app/qa/strip-render/render.py
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

STYLES = ["color", "fill", "backgroundColor", "backgroundImage", "fontSize", "fontWeight", "lineHeight", "fontFamily",
          "letterSpacing", "borderTopWidth", "borderTopColor", "borderBottomWidth", "borderLeftColor", "borderTopLeftRadius",
          "borderTopRightRadius", "paddingTop", "paddingRight", "paddingBottom", "paddingLeft", "marginTop", "marginBottom",
          "boxShadow", "textAlign", "alignItems", "justifyContent", "columnGap", "rowGap", "gridTemplateColumns",
          "whiteSpace", "display", "position", "zIndex", "opacity", "transform", "cursor", "backdropFilter"]
MEASURE_JS = """([root, styles]) => {
  const found = {}, round = (v) => Math.round(v * 100) / 100;
  const look = (el) => { const s = getComputedStyle(el); return Object.fromEntries(styles.map((n) => [n, s[n]])); };
  const visit = (el, path) => {
    const counts = {};
    for (const child of el.children) {
      const label = child.localName + [...child.classList].map((name) => '.' + name).join('');
      counts[label] = (counts[label] ?? -1) + 1;
      const name = `${path}/${label}[${counts[label]}]`;
      if (child.getClientRects().length === 0) { found[name] = null; continue; }
      const box = child.getBoundingClientRect();
      found[name] = { box: [box.x, box.y, box.width, box.height].map(round), styles: look(child) };
      visit(child, name);
    }
  };
  const strip = document.querySelector(root), box = strip.getBoundingClientRect();
  found.strip = { box: [box.x, box.y, box.width, box.height].map(round), styles: look(strip) };
  visit(strip, 'strip');
  return found;
}"""
PAGE_JS = """() => ({ stripH: getComputedStyle(document.documentElement).getPropertyValue('--strip-h').trim(),
  workPaddingBottom: getComputedStyle(document.querySelector('.work')).paddingBottom,
  scrollPaddingBottom: getComputedStyle(document.documentElement).scrollPaddingBottom,
  scrollHeight: document.documentElement.scrollHeight })"""
# The status's place against the Total and its lines, and the message's lines, for one strip root.
LINES_JS = """(root) => {
  const strip = document.querySelector(root), info = strip.querySelector('.strip-info'), status = strip.querySelector('p.status');
  const lines = (el) => { if (!el) return 0; const text = [...el.childNodes].find((n) => n.nodeType === 3); if (!text) return 0;
    const range = document.createRange(); range.selectNode(text);
    return new Set([...range.getClientRects()].filter((r) => r.width > 0).map((r) => Math.round(r.top))).size; };
  let place = null;
  if (status && status.checkVisibility()) {
    const s = status.getBoundingClientRect(), i = info.getBoundingClientRect();
    place = s.left >= i.right - 0.5 && s.top < i.bottom && s.bottom > i.top ? 'beside' : s.top >= i.bottom - 0.5 ? 'under' : 'overlapping';
  }
  return { height: Math.round(strip.getBoundingClientRect().height * 100) / 100, statusPlace: place,
           statusLines: place ? lines(status) : 0, messageLines: lines(strip.querySelector('p.s-msg')),
           figure: strip.querySelector('.s-fig')?.textContent ?? null };
}"""
GOLDENS = {  # golden -> (seed, clicks after load)
    "bill-items": (seeds.S1, ()), "bill-items-open": (seeds.S1, ("#peopleBtn", "#chargesBtn")), "bill-even": (seeds.S2, ()),
    "bill-empty": (None, ()), "rate-error": (seeds.RE, ()), "bill-unassigned": (seeds.S5, ()),
    "bill-unreadable": (seeds.UNREADABLE["B1"], ()), "bill-twelve": (seeds.T12, ()), "bill-large": (seeds.W1, ()),
}
SIZES = {390: (390, 844), 360: (360, 780)}
PIECES = {  # name -> (seed, clipboard, the app's gesture, the piece's div.strip in states.html)
    "S4-copied": (seeds.S2, "recorder", "#stripCopy", 'section[aria-labelledby="c-s4-strip"] div.spec-frame:nth-of-type(1) div.strip'),
    "S4-blocked": (seeds.S2, "reject", "#stripCopy", 'section[aria-labelledby="c-s4-strip"] div.spec-frame:nth-of-type(2) div.strip'),
    "by-item-empty": (None, "recorder", "text=By item", 'section[aria-labelledby="c-empty-item"] div.strip'),
}
NOT_FOR_PIECES = {"position", "zIndex", "gridTemplateColumns"}
# The ratio of Splits to Copy summary on the strip's second row, 1 to 1.3 in system.css.
ACTS_RATIO_JS = """(root) => { const [a, b] = [...document.querySelector(root).querySelectorAll('.strip-acts > .btn')];
  return Math.round(b.getBoundingClientRect().width / a.getBoundingClientRect().width * 1000) / 1000; }"""


def context(browser, size, **options):
    return rig.new_context(browser, viewport={"width": size[0], "height": size[1]}, device_scale_factor=1,
                           color_scheme="dark", reduced_motion="reduce", **options)


def settle(page):
    page.evaluate("() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))")


def as_specimen(walk, figure):
    """The app's walk without its ids and aria-controls, with the figure's text set to the piece's `figure`."""
    walk["attrs"].pop("id", None)
    walk["attrs"].pop("aria-controls", None)
    if walk["cls"] == "s-fig" and figure is not None:
        walk["text"] = figure
    for child in walk["children"]:
        as_specimen(child, figure)
    return walk


def differences(app, golden, compare_boxes=True, skip=()):
    """Every element whose look differs, or whose box differs by more than 0.5 px when boxes are compared."""
    found = {}
    for name in sorted(set(app) | set(golden)):
        a, g = app.get(name), golden.get(name)
        if a is None or g is None:
            if a != g:
                found[name] = {"app": a, "golden": g}
            continue
        looks = {k: [a["styles"][k], g["styles"][k]] for k in a["styles"] if k not in skip and a["styles"][k] != g["styles"][k]}
        box = compare_boxes and any(abs(x - y) > 0.5 for x, y in zip(a["box"], g["box"]))
        if looks or box:
            found[name] = {"look": looks, "box": [a["box"], g["box"]] if box else None}
    return found


def shot(page, root, path):
    box = page.locator(root).evaluate("(el) => { const b = el.getBoundingClientRect(); return [b.x, b.y, b.width, b.height]; }")
    page.screenshot(path=str(path), full_page=True,  # a piece of states.html can lie below the first screen
                    clip={"x": max(box[0] - 4, 0), "y": max(box[1] - 4, 0), "width": box[2] + 8, "height": box[3] + 8})


def main():
    folder = Path(__file__).resolve().parent / (datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-chromium")
    folder.mkdir(parents=True)
    server = rig.StaticServer(rig.ROOT).start()
    found = {"goldens": {}, "pieces": {}}
    try:
        with sync_playwright() as playwright:
            browser = rig.launch(playwright, "chromium")
            for golden_name, (seed, clicks) in GOLDENS.items():
                for width, size in SIZES.items():
                    options = {"storage_state": rig.storage_state(server.base, seed)} if seed else {}
                    app = context(browser, size, **options).new_page()
                    app.goto(server.base + "/")
                    for selector in clicks:
                        app.locator(selector).click()
                    app.mouse.move(0, 0)  # no hover colour is measured
                    settle(app)
                    golden = context(browser, size).new_page()
                    golden.goto((support.GOLDEN_DIR / f"{golden_name}.html").as_uri())
                    for selector in clicks:
                        golden.locator(selector).click()
                    golden.mouse.move(0, 0)
                    pair = [page.evaluate(MEASURE_JS, ["#strip", STYLES]) for page in (app, golden)]
                    pages = [page.evaluate(PAGE_JS) for page in (app, golden)]
                    walk = support.first_diff(support.dom_walk(app, "#strip"), support.dom_walk(golden, "#strip"))
                    key = f"{golden_name}-{width}"
                    found["goldens"][key] = {"walk_first_diff": walk, "differences": differences(*pair),
                                             "page": {"app": pages[0], "golden": pages[1], "equal": pages[0] == pages[1]},
                                             "lines": [app.evaluate(LINES_JS, "#strip"), golden.evaluate(LINES_JS, "#strip")]}
                    if width == 390:
                        shot(app, "#strip", folder / f"{key}-app.png")
                        shot(golden, "#strip", folder / f"{key}-golden.png")
            for name, (seed, clipboard, gesture, piece) in PIECES.items():
                options = {"storage_state": rig.storage_state(server.base, seed)} if seed else {}
                app = context(browser, SIZES[390], clipboard=clipboard, **options).new_page()
                app.goto(server.base + "/")
                app.locator(gesture).click()
                app.mouse.move(0, 0)
                settle(app)
                golden = context(browser, SIZES[390]).new_page()
                golden.goto((support.GOLDEN_DIR / "states.html").as_uri())
                a = app.evaluate(MEASURE_JS, ["#strip", STYLES])
                g = golden.evaluate(MEASURE_JS, [piece, STYLES])
                piece_walk = support.dom_walk(golden, piece)
                piece_figure = next((e["text"] for e in support.walk_entries(piece_walk) if e["cls"] == "s-fig"), None)
                walk = support.first_diff(as_specimen(support.dom_walk(app, "#strip"), piece_figure), piece_walk)
                lines = [app.evaluate(LINES_JS, "#strip"), golden.evaluate(LINES_JS, piece)]
                same = {k: lines[0][k] == lines[1][k] for k in ("height", "statusPlace", "statusLines", "messageLines")}
                ratios = [app.evaluate(ACTS_RATIO_JS, "#strip"), golden.evaluate(ACTS_RATIO_JS, piece)]
                found["pieces"][name] = {"walk_first_diff": walk, "differences": differences(a, g, False, NOT_FOR_PIECES),
                                         "lines": lines, "lines_equal": same, "acts_ratio": ratios,
                                         "widths": [a["strip"]["box"][2], g["strip"]["box"][2]]}
                shot(app, "#strip", folder / f"{name}-app.png")
                shot(golden, piece, folder / f"{name}-golden.png")
            browser.close()
    finally:
        server.stop()
        print("server stopped")
    (folder / "result.json").write_text(json.dumps(found, indent=1), encoding="utf-8")
    for key, entry in found["goldens"].items():
        print(key, "| walk:", entry["walk_first_diff"], "| differences:", sorted(entry["differences"]) or "none",
              "| page equal:", entry["page"]["equal"], entry["page"]["app"]["stripH"], "| lines app/golden:", entry["lines"])
    for key, entry in found["pieces"].items():
        print(key, "| walk:", entry["walk_first_diff"], "| differences:", sorted(entry["differences"]) or "none",
              "| lines equal:", entry["lines_equal"], "| lines app/golden:", entry["lines"], "| button ratio app/golden:",
              entry["acts_ratio"], "| widths:", entry["widths"])
    print("wrote", folder)


main()
