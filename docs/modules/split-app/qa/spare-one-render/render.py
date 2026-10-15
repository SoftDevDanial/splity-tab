"""Render check of P1 with One person and its picker (task A14, R53, qa.md checklist PO), headless Chromium, dark and
reduced motion.

The app on the ONE seed (K2 with One person, Ben) after the clicks of qa.md (below 1024 px Splits and then the sheet's
spare chip, from 1024 px #spareBtn) beside docs/design/spare-sen-one.html, at 390 x 844, 360 x 780 and 1280 x 800.
1. The R3 walk of the whole page and of #spareDlg (support.first_diff).
2. Every element of #spareDlg, and of the part behind it that holds the spare line (the Splits sheet below 1024 px, the
   card from 1024 px), each named by its path of tag and classes, with its computed look (STYLES) and its box relative
   to that part's own top left corner, and the part's own box in the viewport.
3. The P1 values. The scrim (the app's ::backdrop against the golden's div.backdrop.light), #sheetScroll's padding and
   scroll, P1's box, the pills (value, checked, name) and where focus is (the golden has no script, so no focus).
A copy of qa/spare-render/render.py (task A13), whose script runs on import, with the seed, the golden and the pills.
Writes result.json and screenshots into a new <stamp>-chromium folder beside this script. Nothing is written elsewhere.
Run from the project root, python docs/modules/split-app/qa/spare-one-render/render.py
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

GOLDEN = "spare-sen-one"
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
  const box = dialog.getBoundingClientRect();
  return {
    scrim: stand_in ? getComputedStyle(stand_in).backgroundColor : getComputedStyle(dialog, '::backdrop').backgroundColor,
    sheetPadding: scroll ? getComputedStyle(scroll).paddingBottom : null, sheetScrollTop: scroll ? scroll.scrollTop : null,
    box: [box.left, box.top, box.width, box.height, box.bottom].map((v) => Math.round(v * 100) / 100),
    pills: [...dialog.querySelectorAll('#pickList label.pill')].map((pill) => {
      const input = pill.querySelector('input');
      return [input.value, input.checked, pill.textContent.trim()];
    }),
    focus: active === document.body ? 'body' : (active.name ? `${active.name} ${active.value}` : active.localName),
  };
}"""
CHIP_JS = "() => { const chip = document.querySelector('#spareBtn'); return chip && [chip.textContent.trim(), chip.getAttribute('aria-label')]; }"
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
                app = context(browser, size, storage_state=rig.storage_state(server.base, seeds.ONE)).new_page()
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
                    "chip": {"app": app.evaluate(CHIP_JS), "golden": golden.evaluate(CHIP_JS)},
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
        print("   chip:", entry["chip"])
    print("wrote", folder)


main()
