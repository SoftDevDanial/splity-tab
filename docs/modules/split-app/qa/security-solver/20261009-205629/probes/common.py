"""Shared helpers for the security-solver probes (split-app, 2026-10-09).

Every browser context comes from rig.new_context (the clipboard recorder is on, `permissions` and `bypass_csp` are
refused). Nothing here touches the operating system clipboard (CG-7). Output goes to the console only: a probe writes
no file, and the evidence is the printed result that evidence.md quotes.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[6]  # .../examples/split
sys.path.insert(0, str(ROOT / "tests" / "browser"))

import rig  # noqa: E402
import seeds  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover
    pass

# A second CG-7 guard: reject the clipboard read calls, and record every click with its click count.
PROBE_JS = r"""
(() => {
  if (typeof Clipboard === "function") {
    for (const name of ["readText", "read", "write"]) {
      Clipboard.prototype[name] = function () { return Promise.reject(new DOMException("blocked by the probe", "NotAllowedError")); };
    }
  }
  window.evlog = [];
  const label = (node) => {
    const el = node && node.closest ? (node.closest("button, input, label, dialog, a") || node) : node;
    if (!el || !el.tagName) return String(el);
    const aria = el.getAttribute("aria-label");
    const own = el.children.length === 0 ? (el.textContent || "").trim().slice(0, 24) : "";
    return el.tagName.toLowerCase() + (aria ? " [" + aria + "]" : "") + (own ? " \"" + own + "\"" : "");
  };
  for (const type of ["mousedown", "click"]) {
    window.addEventListener(type, (e) => { window.evlog.push(type + ":" + e.detail + ":" + label(e.target) + (e.defaultPrevented ? ":prevented" : "")); }, false);
  }
})();
"""


def open_page(browser, base, *, seed=None, viewport=(390, 844), touch=False):
    options = {"viewport": {"width": viewport[0], "height": viewport[1]}, "device_scale_factor": 1, "color_scheme": "light"}
    if touch:
        options["has_touch"] = True
    if seed is not None:
        options["storage_state"] = rig.storage_state(base, seed)
    context = rig.new_context(browser, init_scripts=[PROBE_JS], **options)
    page = context.new_page()
    errors = []
    page.on("console", lambda m: errors.append(f"console {m.type}: {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(f"page error: {e}"))
    page.goto(base + "/")
    return context, page, errors


def settle(page, ms=150):
    page.evaluate("() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))")
    page.wait_for_timeout(ms)


def centre(locator):
    locator.scroll_into_view_if_needed()
    box = locator.bounding_box()
    return (box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)


def draft(page):
    text = page.evaluate("() => localStorage.getItem('split.draft')")
    return json.loads(text)["bill"] if text else None


def gesture(page, kind, point):
    x, y = point
    if kind == "single":
        page.mouse.click(x, y)
    elif kind == "dbl":
        page.mouse.dblclick(x, y)
    elif kind == "triple":
        page.mouse.click(x, y, click_count=3)
    elif kind == "tap2":
        page.touchscreen.tap(x, y)
        page.touchscreen.tap(x, y)
    else:
        raise ValueError(kind)
    settle(page)


def run_probe(body):
    """Start a loopback server and headless Chromium, call body(browser, server), always stop both."""
    server = rig.StaticServer(ROOT).start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            print("chromium", browser.version)
            try:
                body(browser, server)
            finally:
                browser.close()
    finally:
        server.stop()
