"""Render check of the two notes (task A3, R27, R46), headless Chromium, nothing pressed.

The unreadable note (B1 seed) against docs/design/bill-unreadable.html at 390 x 844, 360 x 780 and 1280 x 800: the
top bar's box, the note's box and computed styles, its text box, its icon and Dismiss note. The save warning (the
fail-get driver, so it shows at boot) at the same widths, against the S5 frame of docs/design/states.html at 390 for
the computed styles only, since the frame is narrower than the app. Writes boxes.json into a new
<stamp>-chromium folder beside this script. Run from the project root: python docs/modules/split-app/qa/note-render/render.py
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
PROPS = ["color", "backgroundColor", "fontSize", "fontWeight", "lineHeight", "borderTopColor", "borderTopWidth",
         "borderTopLeftRadius", "paddingTop", "paddingRight", "paddingBottom", "paddingLeft", "minHeight"]
MEASURE_JS = """([note, props]) => {
  const box = (el) => { if (!el) return null; const r = el.getBoundingClientRect(); return [r.x, r.y, r.width, r.height].map((n) => Math.round(n * 100) / 100); };
  const el = document.querySelector(note);
  const style = getComputedStyle(el);
  return { top: box(document.querySelector('header.top')), note: box(el), text: box(el.querySelector('p')),
           icon: box(el.querySelector(':scope > svg')), button: box(el.querySelector('button')),
           iconFill: getComputedStyle(el.querySelector(':scope > svg')).fill,
           styles: Object.fromEntries(props.map((name) => [name, style[name]])) };
}"""


def context(browser, viewport, **options):
    return rig.new_context(browser, viewport={"width": viewport[0], "height": viewport[1]}, device_scale_factor=1,
                           color_scheme="dark", reduced_motion="reduce", **options)


def main():
    folder = Path(__file__).resolve().parent / (datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-chromium")
    folder.mkdir(parents=True)
    server = rig.StaticServer(rig.ROOT).start()
    found = {}
    try:
        with sync_playwright() as playwright:
            browser = rig.launch(playwright, "chromium")
            for width, viewport in SIZES.items():
                app = context(browser, viewport, storage_state=rig.storage_state(server.base, seeds.UNREADABLE["B1"])).new_page()
                app.goto(server.base + "/")
                golden = context(browser, viewport).new_page()
                golden.goto((support.GOLDEN_DIR / "bill-unreadable.html").as_uri())
                pair = [page.evaluate(MEASURE_JS, ["#notes > div.note", PROPS]) for page in (app, golden)]
                found[f"unreadable-{width}"] = {"app": pair[0], "golden": pair[1], "equal": pair[0] == pair[1]}
                warn_context = context(browser, viewport, init_scripts=[support.storage_driver("fail-get")])
                warn = warn_context.new_page()
                warn.goto(server.base + "/")
                found[f"warning-{width}"] = {"app": warn.evaluate(MEASURE_JS, ["#notes > div.note", PROPS])}
            spec = context(browser, SIZES["390"]).new_page()
            spec.goto((support.GOLDEN_DIR / "states.html").as_uri())
            golden_warning = spec.evaluate(MEASURE_JS, ['section[aria-labelledby="c-s5"] div.notes > div.note', PROPS])
            app_warning = found["warning-390"]["app"]
            found["warning-390"].update(golden_frame=golden_warning,
                                        styles_equal=app_warning["styles"] == golden_warning["styles"],
                                        icon_fill_equal=app_warning["iconFill"] == golden_warning["iconFill"])
            browser.close()
    finally:
        server.stop()
    (folder / "boxes.json").write_text(json.dumps(found, indent=1), encoding="utf-8")
    for name, entry in found.items():
        print(name, {key: value for key, value in entry.items() if key in ("equal", "styles_equal", "icon_fill_equal")})
    print("wrote", folder / "boxes.json")


main()
