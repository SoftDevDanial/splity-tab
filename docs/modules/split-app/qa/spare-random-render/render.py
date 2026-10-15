"""Render check of P1 with At random and Pick again (task A15, R54, qa.md checklist PR), headless Chromium, dark and
reduced motion.

The app on the RND seed (K2 with At random, the order Ben, Chen, Aisyah, so Ben and Chen take the two sen as the golden
draws them) after the clicks of qa.md (below 1024 px Splits and then the sheet's spare chip, from 1024 px #spareBtn)
beside docs/design/spare-sen-random.html, at 390 x 844, 360 x 780 and 1280 x 800.
1. The R3 walk of the whole page and of #spareDlg (support.first_diff).
2. Every element of #spareDlg, and of the part behind it that holds the spare line (the Splits sheet below 1024 px, the
   card from 1024 px), each named by its path of tag and classes, with its computed look (STYLES) and its box relative
   to that part's own top left corner, and the part's own box in the viewport.
3. The PR values. The scrim, #sheetScroll's padding and scroll, P1's box, #randWrap's inset and Pick again's height,
   the receipt chips behind (their text, whether both sit on a line under the count, the gap between them), the spare
   chip's text and name, and where focus is (the golden has no script, so no focus).
A copy of qa/spare-one-render/render.py (task A14), whose script runs on import, with the seed, the golden and the R54
values. Writes result.json and screenshots into a new <stamp>-chromium folder beside this script. Nothing is written
elsewhere. Run from the project root, python docs/modules/split-app/qa/spare-random-render/render.py
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

GOLDEN = "spare-sen-random"
STYLES = ["color", "fill", "backgroundColor", "backgroundImage", "fontSize", "fontWeight", "lineHeight", "fontFamily",
          "letterSpacing", "borderTopWidth", "borderTopColor", "borderBottomWidth", "borderLeftColor", "borderTopLeftRadius",
          "borderTopRightRadius", "borderBottomLeftRadius", "paddingTop", "paddingRight", "paddingBottom", "paddingLeft",
          "marginTop", "marginBottom", "boxShadow", "textAlign", "alignItems", "justifyContent", "columnGap", "rowGap",
          "gridTemplateColumns", "whiteSpace", "display", "position", "opacity", "transform", "cursor", "backdropFilter",
          "outlineStyle", "outlineWidth", "overflowY", "maxHeight", "maxWidth"]
MEASURE_JS = """([root, styles]) => {
  const found = {}, round = (v) => Math.round(v * 100) / 100;
  const look = (el) => { const s = getComputedStyle(el); return Object.fromEntries(styles.map((n) => [n, s[n]])); };
  const top = document.querySelector(root), base = top.getBoundingClientRect();
  const boxOf = (el) => { const b = el.getBoundingClientRect(); return [b.x - base.x, b.y - base.y, b.width, b.height].map(round); };
  const visit = (el, path) => {
    const counts = {};
    for (const child of el.children) {
      const label = child.localName + [...child.classList].map((name) => '.' + name).join('');
      counts[label] = (counts[label] ?? -1) + 1;
      const name = `${path}/${label}[${counts[label]}]`;
      if (child.getClientRects().length === 0) { found[name] = null; continue; }
      found[name] = { box: boxOf(child), styles: look(child) };
      visit(child, name);
    }
  };
  found.root = { box: [base.x, base.y, base.width, base.height].map(round), styles: look(top) };
  visit(top, 'root');
  return found;
}"""
P1_JS = """() => {
  const dialog = document.querySelector('#spareDlg'), scroll = document.querySelector('#sheetScroll');
  const stand_in = document.querySelector('div.backdrop.light'), active = document.activeElement;
  const box = dialog.getBoundingClientRect(), wrap = dialog.querySelector('#randWrap');
  const button = wrap?.querySelector('#pickAgainSheet');
  return {
    scrim: stand_in ? getComputedStyle(stand_in).backgroundColor : getComputedStyle(dialog, '::backdrop').backgroundColor,
    sheetPadding: scroll ? getComputedStyle(scroll).paddingBottom : null, sheetScrollTop: scroll ? scroll.scrollTop : null,
    box: [box.left, box.top, box.width, box.height, box.bottom].map((v) => Math.round(v * 100) / 100),
    checked: dialog.querySelector('input[name=spareRule]:checked')?.value ?? null,
    pickers: [...dialog.querySelectorAll('#pickWrap, #randWrap')].map((el) => el.id),
    randWrap: wrap && [getComputedStyle(wrap).paddingLeft, button && [button.className, button.textContent.trim(),
      Math.round(button.getBoundingClientRect().height * 100) / 100]],
    focus: active === document.body ? 'body' : (active.name ? `${active.name} ${active.value}` : active.id || active.localName),
  };
}"""
# The spare line of the part behind P1: its count, its chips' text, whether every chip sits under the count (a second
# line, PR-04), the gap between the two chips (PR-03), and the spare chip's text and accessible name (PR-06).
CHIPS_JS = """(root) => {
  const spare = document.querySelector(root)?.querySelector('div.r-spare');
  if (!spare) return null;
  const count = spare.querySelector(':scope > p'), countBox = count.getBoundingClientRect();
  const chips = [...spare.querySelectorAll(':scope > div.r-spare-acts > button')];
  const boxes = chips.map((chip) => chip.getBoundingClientRect()), spareChip = chips.find((chip) => chip.hasAttribute('aria-haspopup'));
  return { count: count.textContent, chips: chips.map((chip) => chip.textContent.trim()),
    underCount: boxes.every((b) => b.top >= countBox.bottom - 0.5),
    gap: boxes.length === 2 ? Math.round((boxes[1].left - boxes[0].right) * 100) / 100 : null,
    spareChip: spareChip && [spareChip.textContent.trim(), spareChip.getAttribute('aria-label')] };
}"""
SPLITS_JS = "(root) => [...document.querySelector(root).querySelectorAll('ul.r-splits > li')].map((li) => li.textContent)"
SIZES = {390: (390, 844), 360: (360, 780), 1280: (1280, 800)}


def context(browser, size, **options):
    return rig.new_context(browser, viewport={"width": size[0], "height": size[1]}, device_scale_factor=1,
                           color_scheme="dark", reduced_motion="reduce", **options)


def settle(page):
    page.evaluate("() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))")


def differences(app, golden):
    """Every element whose look differs, or whose box differs by more than 0.5 px, or that only one side draws."""
    found = {}
    for name in sorted(set(app) | set(golden)):
        a, g = app.get(name), golden.get(name)
        if a is None or g is None:
            if a != g:
                found[name] = {"app": a and a["box"], "golden": g and g["box"]}
            continue
        looks = {k: [a["styles"][k], g["styles"][k]] for k in a["styles"] if a["styles"][k] != g["styles"][k]}
        box = any(abs(x - y) > 0.5 for x, y in zip(a["box"], g["box"]))
        if looks or box:
            found[name] = {"look": looks, "box": [a["box"], g["box"]] if box else None}
    return found


def main():
    folder = Path(__file__).resolve().parent / (datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-chromium")
    folder.mkdir(parents=True)
    server = rig.StaticServer(rig.ROOT).start()
    found = {}
    try:
        with sync_playwright() as playwright:
            browser = rig.launch(playwright, "chromium")
            for width, size in SIZES.items():
                phone = width < 1024
                app = context(browser, size, storage_state=rig.storage_state(server.base, seeds.RND)).new_page()
                app.goto(server.base + "/")
                for selector in ("#splitsBtn", "#splitsDlg .r-spare-acts button[aria-haspopup=dialog]") if phone else ("#spareBtn",):
                    app.locator(selector).click()
                app.mouse.move(0, 0)  # no hover colour is measured
                settle(app)
                golden = context(browser, size).new_page()
                golden.goto((support.GOLDEN_DIR / f"{GOLDEN}.html").as_uri())
                golden.mouse.move(0, 0)
                behind = "#splitsDlg" if phone else "#card"
                found[str(width)] = {
                    "walk_first_diff": {part or "body": support.first_diff(*[support.dom_walk(page, part) for page in (app, golden)])
                                        for part in (None, "#spareDlg")},
                    "differences": {part: differences(*[page.evaluate(MEASURE_JS, [part, STYLES]) for page in (app, golden)])
                                    for part in ("#spareDlg", behind)},
                    "p1": {"app": app.evaluate(P1_JS), "golden": golden.evaluate(P1_JS)},
                    "chips": {"app": app.evaluate(CHIPS_JS, behind), "golden": golden.evaluate(CHIPS_JS, behind)},
                    "splits": {"app": app.evaluate(SPLITS_JS, behind), "golden": golden.evaluate(SPLITS_JS, behind)},
                }
                app.screenshot(path=str(folder / f"{GOLDEN}-{width}-app.png"))
                golden.screenshot(path=str(folder / f"{GOLDEN}-{width}-golden.png"))
            browser.close()
    finally:
        server.stop()
        print("server stopped")
    (folder / "result.json").write_text(json.dumps(found, indent=1), encoding="utf-8")
    for width, entry in found.items():
        print(width, "| walk:", entry["walk_first_diff"], "| differences:",
              {part: sorted(diff) or "none" for part, diff in entry["differences"].items()})
        print("   p1:", entry["p1"])
        print("   chips:", entry["chips"])
        print("   splits:", entry["splits"])
    print("wrote", folder)


main()
