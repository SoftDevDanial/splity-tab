"""Render check of M1, the New bill dialog (task A16, R29, qa.md checklist M1), headless Chromium, dark and reduced motion.

The app on the K1 seed after a mouse click on #newBill, beside docs/design/new-bill-dialog.html, at 390 x 844, 360 x 780
and 1280 x 800.
1. The R3 walk of the whole page and of #newDlg (support.first_diff).
2. Every element of #newDlg, each named by its path of tag and classes, with its computed look (STYLES) and its box
   relative to the dialog's top left corner, and the dialog's own box in the viewport.
3. The M1 values. The scrim (the app's ::backdrop, the golden's div.backdrop), whether the root scrolls, the dialog's
   box, the gaps of M1-04 and M1-07, the two buttons' fill, label colour and height, and where focus is (the golden has
   no script, so no focus). Focus is then dropped, as the fidelity script does (M1-08), before the screenshots.
4. The SHA-256 of the app's and the golden's screenshot at each width.
A copy of qa/spare-random-render/render.py (task A15), whose script runs on import, with the seed, the golden and the M1
values. Writes result.json and screenshots into a new <stamp>-chromium folder beside this script. Nothing is written
elsewhere. Run from the project root, python docs/modules/split-app/qa/new-bill-render/render.py
"""
import datetime
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("tests/browser").resolve()))
import rig  # noqa: E402
import seeds  # noqa: E402
import support  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

GOLDEN = "new-bill-dialog"
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
M1_JS = """() => {
  const dialog = document.querySelector('#newDlg'), stand_in = document.querySelector('div.backdrop'), active = document.activeElement;
  const round = (v) => Math.round(v * 100) / 100, box = (el) => el.getBoundingClientRect();
  const title = box(dialog.querySelector('#newTitle')), body = box(dialog.querySelector('#newBody')), acts = dialog.querySelector('.acts');
  const buttons = [...acts.querySelectorAll('button')];
  return {
    scrim: stand_in ? getComputedStyle(stand_in).backgroundColor : getComputedStyle(dialog, '::backdrop').backgroundColor,
    rootOverflow: getComputedStyle(document.documentElement).overflowY,
    box: [box(dialog).left, box(dialog).top, box(dialog).width, box(dialog).height].map(round),
    bodyBelowTitle: round(body.top - title.bottom), actsBelowBody: round(box(acts).top - body.bottom),
    buttons: buttons.map((b) => [b.textContent.trim(), getComputedStyle(b).backgroundColor, getComputedStyle(b).color,
      round(box(b).height), round(box(b).left), round(box(b).top), round(box(b).width)]),
    focus: active === document.body ? 'body' : (active.id || active.textContent.trim() || active.localName),
  };
}"""
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


def shot(page, path):
    page.screenshot(path=str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
                app.locator("#newBill").click()
                app.mouse.move(0, 0)  # no hover colour is measured
                settle(app)
                golden = context(browser, size).new_page()
                golden.goto((support.GOLDEN_DIR / f"{GOLDEN}.html").as_uri())
                golden.mouse.move(0, 0)
                found[str(width)] = {
                    "walk_first_diff": {part or "body": support.first_diff(*[support.dom_walk(page, part) for page in (app, golden)])
                                        for part in (None, "#newDlg")},
                    "differences": differences(*[page.evaluate(MEASURE_JS, ["#newDlg", STYLES]) for page in (app, golden)]),
                    "m1": {"app": app.evaluate(M1_JS), "golden": golden.evaluate(M1_JS)},
                }
                app.evaluate("() => document.activeElement.blur()")  # M1-08, as the fidelity script does
                settle(app)
                hashes = [shot(page, folder / f"{GOLDEN}-{width}-{side}.png") for page, side in ((app, "app"), (golden, "golden"))]
                found[str(width)]["screenshots_equal"] = hashes[0] == hashes[1]
            browser.close()
    finally:
        server.stop()
        print("server stopped")
    (folder / "result.json").write_text(json.dumps(found, indent=1), encoding="utf-8")
    for width, entry in found.items():
        print(width, "| walk:", entry["walk_first_diff"], "| differences:", sorted(entry["differences"]) or "none",
              "| screenshots equal:", entry["screenshots_equal"])
        print("   app:", entry["m1"]["app"])
        print("   golden:", entry["m1"]["golden"])
    print("wrote", folder)


main()
