"""Render check of the Splits sheet (task A12, R50), headless Chromium, dark and reduced motion.

The app on K1 after a click on Splits beside docs/design/splits-sheet.html, at 390 x 844 and 360 x 780 (qa.md, P2).
1. The R3 walk of the whole page and of #splitsDlg (support.first_diff), as it is and with the golden's div.r-spare taken
   out, because the spare line and its chip are task A13's (R51) while the golden draws them.
2. Every element of #splitsDlg on both sides, each named by its path of tag and classes, with its computed look (STYLES)
   and its box relative to the dialog's own top left corner. The dialog sits on the bottom edge, so without div.r-spare
   every part above the spare line keeps its place from the top, and the parts below it and their boxes around it are
   shorter or higher by the spare line's share. That share is recorded as the golden's r-spare height and top margin.
3. The P2 checklist values. The scrim's colour (the app's ::backdrop against the golden's div.backdrop.under-sheet), the
   sheet's box, the top row, the grab, Close, the receipt's box and sides, whether #sheetScroll scrolls, Splits'
   aria-expanded, where focus is and the sheet's outline, and the strip behind.
Writes result.json and screenshots into a new <stamp>-chromium folder beside this script. Nothing is written elsewhere.
Run from the project root, python docs/modules/split-app/qa/sheet-render/render.py
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
  found.dialog = { box: [base.x, base.y, base.width, base.height].map(round), styles: look(top) };
  visit(top, 'dialog');
  return found;
}"""
P2_JS = """() => {
  const round = (v) => Math.round(v * 100) / 100;
  const box = (el) => { if (!el) return null; const b = el.getBoundingClientRect(); return [b.x, b.y, b.width, b.height].map(round); };
  const dialog = document.querySelector('#splitsDlg'), sheet = dialog.querySelector(':scope > .sheet');
  const scroll = sheet.querySelector('#sheetScroll'), rbody = scroll.querySelector('.rbody'), spare = rbody.querySelector('.r-spare');
  const stand_in = document.querySelector('div.backdrop.under-sheet');
  const s = sheet.getBoundingClientRect(), r = rbody.getBoundingClientRect();
  return {
    scrim: stand_in ? getComputedStyle(stand_in).backgroundColor : getComputedStyle(dialog, '::backdrop').backgroundColor,
    sheet: box(sheet), top: box(sheet.querySelector(':scope > .sheet-top')), grab: box(sheet.querySelector('.grab')),
    close: box(sheet.querySelector('.sheet-top > button')), rbody: box(rbody), rbodySides: [round(r.left - s.left), round(s.right - r.right)],
    scrolls: scroll.scrollHeight > scroll.clientHeight, expanded: document.querySelector('#splitsBtn').getAttribute('aria-expanded'),
    focusOnSheet: document.activeElement === sheet, outline: [getComputedStyle(sheet).outlineStyle, getComputedStyle(sheet).outlineWidth],
    spare: box(spare), spareMarginTop: spare ? getComputedStyle(spare).marginTop : null, strip: box(document.querySelector('#strip')),
    stripShown: document.querySelector('#strip').checkVisibility(),
  };
}"""
SIZES = {390: (390, 844), 360: (360, 780)}


def context(browser, size, **options):
    return rig.new_context(browser, viewport={"width": size[0], "height": size[1]}, device_scale_factor=1,
                           color_scheme="dark", reduced_motion="reduce", **options)


def settle(page):
    page.evaluate("() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))")


def without_spare(walk):
    """A walk with every div.r-spare taken out (the golden's spare line, task A13)."""
    walk["children"] = [without_spare(child) for child in walk["children"] if child["cls"] != "r-spare"]
    return walk


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
                app = context(browser, size, storage_state=rig.storage_state(server.base, seeds.S1)).new_page()
                app.goto(server.base + "/")
                app.locator("#splitsBtn").click()
                app.mouse.move(0, 0)  # no hover colour is measured
                settle(app)
                golden = context(browser, size).new_page()
                golden.goto((support.GOLDEN_DIR / "splits-sheet.html").as_uri())
                golden.mouse.move(0, 0)
                walks = {part: [support.dom_walk(page, part) for page in (app, golden)] for part in (None, "#splitsDlg")}
                found[str(width)] = {
                    "walk_first_diff": {part or "body": support.first_diff(*pair) for part, pair in walks.items()},
                    "walk_first_diff_without_the_goldens_spare_line": {
                        part or "body": support.first_diff(pair[0], without_spare(pair[1])) for part, pair in walks.items()},
                    "differences": differences(*[page.evaluate(MEASURE_JS, ["#splitsDlg", STYLES]) for page in (app, golden)]),
                    "p2": {"app": app.evaluate(P2_JS), "golden": golden.evaluate(P2_JS)},
                }
                app.screenshot(path=str(folder / f"splits-sheet-{width}-app.png"))
                golden.screenshot(path=str(folder / f"splits-sheet-{width}-golden.png"))
            browser.close()
    finally:
        server.stop()
        print("server stopped")
    (folder / "result.json").write_text(json.dumps(found, indent=1), encoding="utf-8")
    for width, entry in found.items():
        print(width, "| walk:", entry["walk_first_diff"], "| walk without the golden's spare line:",
              entry["walk_first_diff_without_the_goldens_spare_line"], "| differences:", sorted(entry["differences"]) or "none")
        print("   p2 app:", entry["p2"]["app"])
        print("   p2 golden:", entry["p2"]["golden"])
    print("wrote", folder)


main()
