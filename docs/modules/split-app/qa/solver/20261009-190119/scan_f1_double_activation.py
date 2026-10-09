"""F-1 scan on the fixed code: a double click and a double tap on Cancel, on Start new bill and on the backdrop,
4 bills x 16 viewports x 2 gestures x 3 targets. Prints a compact result. Scratch script, not part of the project.
Contexts only through rig.new_context (the clipboard recorder is installed, no permission, no bypass)."""
import sys
import time

sys.path.insert(0, "{workspace}/examples/split/tests/browser")
from playwright.sync_api import sync_playwright
import rig
import seeds

NEW_BILL = ('{"version":1,"bill":{"mode":"even","people":[{"id":"p1","name":"Person 1"},{"id":"p2","name":"Person 2"}],'
            '"subtotalText":"","items":[],"serviceText":"10","sstText":"6","nextId":3}}')
SEEDS = {"S1": seeds.S1, "S2": seeds.S2, "S5": seeds.S5, "S3": None}
VIEWPORTS = [(320, 568), (360, 640), (360, 740), (360, 780), (360, 800), (375, 667), (375, 812), (390, 844), (393, 852),
             (412, 732), (412, 915), (414, 896), (430, 932), (768, 1024), (1024, 768), (1280, 800)]
SNAP = """() => ({
  people: [...document.querySelectorAll('li.person input')].map((i) => i.value),
  mode: document.querySelector('input[name=mode]:checked').value,
  items: [...document.querySelectorAll('li.item')].map((li) => [...li.querySelectorAll('input')].map((i) => i.value)
    .concat([...li.querySelectorAll('.tap')].map((b) => b.getAttribute('aria-pressed')))),
  rates: [document.querySelector('#rate-service').value, document.querySelector('#rate-sst').value],
})"""
SETTLE = "() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))"


def centre(locator):
    locator.scroll_into_view_if_needed()
    box = locator.bounding_box()
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


import os
SCAN_ROOT = os.environ.get("SCAN_ROOT") or rig.ROOT  # a baseline checkout to see the same scan fail
server = rig.StaticServer(SCAN_ROOT, say=print).start()
rows, failures = 0, []
started = time.time()
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for name, seed in SEEDS.items():
            for vp in VIEWPORTS:
                for how in ("mouse", "touch"):
                    for target in ("Cancel", "Start new bill", "backdrop"):
                        options = {"viewport": {"width": vp[0], "height": vp[1]}, "device_scale_factor": 1}
                        if how == "touch":
                            options["has_touch"] = True
                        if seed is not None:
                            options["storage_state"] = rig.storage_state(server.base, seed)
                        context = rig.new_context(browser, **options)
                        page = context.new_page()
                        page.set_default_timeout(8000)
                        try:
                            page.goto(server.base + "/")
                            stored = lambda: page.evaluate("localStorage.getItem('split.draft')")
                            before_draft, before_snap = stored(), page.evaluate(SNAP)
                            page.get_by_role("button", name="New bill", exact=True).click()
                            if target == "backdrop":
                                point = (6, 6)
                            else:
                                point = centre(page.get_by_role("button", name=target, exact=True))
                            if how == "touch":
                                page.touchscreen.tap(*point)
                                page.touchscreen.tap(*point)
                            else:
                                page.mouse.dblclick(*point)
                            page.evaluate(SETTLE)
                            closed = page.locator("dialog.dialog").evaluate("(d) => !d.open")
                            focus = page.evaluate("document.activeElement.textContent.trim()")
                            draft = stored()
                            if target == "Start new bill":
                                ok = closed and focus == "New bill" and draft == NEW_BILL
                            else:
                                ok = closed and focus == "New bill" and draft == before_draft and page.evaluate(SNAP) == before_snap
                            rows += 1
                            if not ok:
                                failures.append((name, vp, how, target, closed, focus))
                        finally:
                            context.close()
        browser.close()
finally:
    server.stop()
print(f"RESULT cases={rows} failures={len(failures)} seconds={time.time() - started:.0f}")
for item in failures[:30]:
    print("FAIL", item)
