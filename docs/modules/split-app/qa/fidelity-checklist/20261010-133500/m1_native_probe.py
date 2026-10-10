"""Probe: which part of the harness's rendering makes the app's M1 render differ from the golden-as-native-modal by a few corner pixels?

m1_native.py (my own screenshots) gives 0 differing pixels at 390, m1_native_harness.py (the harness's render()) gives 46. Both sides of each comparison are
rendered in the same variant here. Variants switch on harness ingredients: bypass_csp, its freeze stylesheet (which can only be added with the CSP bypassed,
because the app's style-src 'self' blocks an injected style tag), its pinned clock, its 300 ms settle. The app is opened by the harness's own setup
(synthetic click, two frames, blur, two frames).

usage: python m1_native_probe.py
"""
import sys

sys.dont_write_bytecode = True
import datetime
import importlib.util
import io
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

import common as C

HARNESS = Path("{sdlc}/harness/fidelity.py")
spec = importlib.util.spec_from_file_location("sdlc_fidelity", HARNESS)
fid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fid)

NATIVE = """() => { const b = document.querySelector('.backdrop'); if (b) b.remove(); const app = document.querySelector('.app'); if (app) app.removeAttribute('inert');
  const d = document.querySelector('dialog'); d.removeAttribute('open'); d.showModal(); document.activeElement && document.activeElement.blur && document.activeElement.blur(); }"""
OPEN = """async () => { const f = () => new Promise((r) => requestAnimationFrame(() => r())); document.querySelector('header .btn').click(); await f(); await f(); document.activeElement.blur(); await f(); await f(); }"""


def shot(page):
    return np.asarray(Image.open(io.BytesIO(page.screenshot(full_page=True, animations="disabled"))).convert("RGB"), dtype=np.int32)


def render_variant(browser, url, vp, *, freeze, bypass, clock, settle, seed=None, native=False, open_js=None):
    ctx = browser.new_context(viewport={"width": vp[0], "height": vp[1]}, device_scale_factor=1, reduced_motion="reduce", color_scheme="light", bypass_csp=bypass)
    page = ctx.new_page()
    if clock:
        page.clock.set_fixed_time(datetime.datetime.fromisoformat("2026-10-08T09:00:00"))
    if seed:
        page.add_init_script(f'localStorage.setItem("split.draft", {seed!r});')
    page.goto(url, wait_until="networkidle")
    if native:
        page.evaluate(NATIVE)
    if open_js:
        page.evaluate(open_js)
    if freeze:
        page.add_style_tag(content=fid.FREEZE_CSS)
    if settle:
        page.wait_for_timeout(300)
    img = shot(page)
    ctx.close()
    return img


def diff(a, b):
    if a.shape != b.shape:
        return "size differs"
    return int((np.abs(a - b).max(axis=2) > 0).sum())


VARIANTS = (("plain (CSP on)", dict(freeze=False, bypass=False, clock=False, settle=False)),
            ("bypass_csp", dict(freeze=False, bypass=True, clock=False, settle=False)),
            ("bypass_csp + freeze css", dict(freeze=True, bypass=True, clock=False, settle=False)),
            ("pinned clock", dict(freeze=False, bypass=False, clock=True, settle=False)),
            ("300 ms settle", dict(freeze=False, bypass=False, clock=False, settle=True)),
            ("all four (the harness)", dict(freeze=True, bypass=True, clock=True, settle=True)))


def main():
    server = C.rig.StaticServer(C.ROOT, say=print)
    rows = []
    try:
        server.start()
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=["--force-color-profile=srgb", "--hide-scrollbars", "--disable-lcd-text"])
            gurl = (C.DESIGN / "new-bill-dialog.html").as_uri()
            aurl = server.base + "/"
            for vp in ((390, 844), (1280, 800)):
                for label, kw in VARIANTS:
                    g_native = render_variant(browser, gurl, vp, native=True, **kw)
                    g_static = render_variant(browser, gurl, vp, **kw)
                    app = render_variant(browser, aurl, vp, seed=C.seeds.S2, open_js=OPEN, **kw)
                    row = {"viewport": f"{vp[0]}x{vp[1]}", "variant": label, "native_golden_vs_app": diff(g_native, app), "static_golden_vs_app": diff(g_static, app),
                           "static_golden_vs_native_golden": diff(g_static, g_native)}
                    rows.append(row)
                    print(row)
            browser.close()
    finally:
        server.stop()
    C.dump("m1_native_probe.json", rows)


if __name__ == "__main__":
    main()
