"""Gate honesty, part 2: what the 141 and 103 pixels of the M1 pairs are.

The harness pairs for new-bill-dialog differ from the golden by a few pixels (at most 2 of 255 on a channel) at 390 and 1280, while the other
eight pairs are byte-identical. The claim in qa.md is that this is anti-aliasing at glyph edges: the golden draws its dialog in the page flow,
the app's dialog is in the browser's top layer. This script tests that claim. It opens the golden M1 in memory, turns its static dialog into a
native modal (removes the stand-in .backdrop and the inert attribute, closes the static dialog and calls showModal()), and compares that
render with the app opened by a REAL mouse click on "New bill" (no synthetic click, no blur). The golden file is never written.

Also records: the app opened as the harness setup script does it (synthetic click then blur) against the same native golden, and the
position of the differing pixels of the static golden against the app.

usage: python m1_native.py
"""
import sys

sys.dont_write_bytecode = True
import io

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

import common as C

NATIVE_JS = """() => {
  const b = document.querySelector('.backdrop'); if (b) b.remove();
  const app = document.querySelector('.app'); if (app) app.removeAttribute('inert');
  const d = document.querySelector('dialog'); d.removeAttribute('open'); d.showModal();
  document.activeElement && document.activeElement.blur && document.activeElement.blur();
}"""


def shot(page):
    return np.asarray(Image.open(io.BytesIO(page.screenshot(full_page=True, animations="disabled"))).convert("RGB"), dtype=np.int32)


def diff(a, b):
    if a.shape != b.shape:
        return {"size_differs": [list(a.shape[:2]), list(b.shape[:2])]}
    d = np.abs(a - b).max(axis=2)
    n = int((d > 0).sum())
    box = None
    if n:
        ys, xs = np.nonzero(d)
        box = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    return {"any_level": n, "max_delta": int(d.max()), "box": box}


def main():
    rows = []
    server = C.rig.StaticServer(C.ROOT, say=print)
    try:
        server.start()
        with sync_playwright() as pw:
            browser = C.launch(pw)
            for vp in ((360, 780), (390, 844), (600, 900), (1024, 768), (1280, 800)):
                g_static = shot(C.open_golden(C.gold_ctx(browser, vp), "new-bill-dialog").page)
                gn = C.open_golden(C.gold_ctx(browser, vp), "new-bill-dialog")
                gn.page.evaluate(NATIVE_JS)
                gn.page.wait_for_timeout(100)
                g_native = shot(gn.page)
                actx = C.app_ctx(browser, server.base, vp, seed=C.seeds.S2)
                a = C.open_app(actx, server.base)
                C.new_bill_by_mouse(a)
                a_img = shot(a.page)
                actx2 = C.app_ctx(browser, server.base, vp, seed=C.seeds.S2)
                a2 = C.open_app(actx2, server.base)
                a2.page.evaluate("""async () => { const f = () => new Promise((r) => requestAnimationFrame(() => r()));
                  document.querySelector('header .btn').click(); await f(); await f(); document.activeElement.blur(); await f(); await f(); }""")
                a2_img = shot(a2.page)
                row = {"viewport": f"{vp[0]}x{vp[1]}", "static_golden_vs_app_real_click": diff(g_static, a_img), "native_golden_vs_app_real_click": diff(g_native, a_img),
                       "native_golden_vs_app_harness_setup": diff(g_native, a2_img), "static_golden_vs_native_golden": diff(g_static, g_native)}
                rows.append(row)
                print(vp, row)
            browser.close()
    finally:
        server.stop()
    C.dump("m1_native.json", rows)


if __name__ == "__main__":
    main()
