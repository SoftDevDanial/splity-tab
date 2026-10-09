"""Does the second click of a double click on 'Dismiss note' reach anything? Scratch probe, not part of the project."""
import sys

sys.path.insert(0, "{workspace}/examples/split/tests/browser")
from playwright.sync_api import sync_playwright
import rig
import seeds

UNDER = """([x, y]) => { const e = document.elementFromPoint(x, y); if (!e) return null;
  const c = e.closest('button, input, label, a'); return c ? c.tagName.toLowerCase() + ':' + (c.getAttribute('aria-label') || c.textContent.trim().slice(0, 20)) + (c.disabled ? ':disabled' : '') : e.tagName.toLowerCase(); }"""
SETTLE = "() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))"

server = rig.StaticServer(rig.ROOT, say=print).start()
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for vp in [(360, 640), (375, 667), (390, 844), (412, 732), (1280, 800)]:
            for how in ("mouse", "touch"):
                options = {"viewport": {"width": vp[0], "height": vp[1]}, "device_scale_factor": 1,
                           "storage_state": rig.storage_state(server.base, seeds.UNREADABLE["B1"])}
                if how == "touch":
                    options["has_touch"] = True
                context = rig.new_context(browser, **options)
                page = context.new_page()
                page.set_default_timeout(8000)
                page.goto(server.base + "/")
                button = page.get_by_role("button", name="Dismiss note")
                box = button.bounding_box()
                x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
                before = page.evaluate("localStorage.getItem('split.draft')")
                page.keyboard.press("Tab")  # no-op, keeps focus handling identical
                if how == "touch":
                    page.touchscreen.tap(x, y)
                    page.touchscreen.tap(x, y)
                else:
                    page.mouse.dblclick(x, y)
                page.evaluate(SETTLE)
                after = page.evaluate("localStorage.getItem('split.draft')")
                under = page.evaluate(UNDER, [x, y])
                focus = page.evaluate("document.activeElement.getAttribute('aria-label') || document.activeElement.textContent.trim()")
                print(f"{vp} {how}: under the pointer now = {under}; draft changed = {before != after}; focus = {focus}")
                context.close()
        browser.close()
finally:
    server.stop()
