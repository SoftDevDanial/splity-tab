"""QA finder (read-only) probe for the qa.md scenario "The accessible description of the amount fields is measured
and reported" (@R9 @R11 @chromium_only). Scratch script. It prints the four lines and writes nothing.
Run from the project root: python <this file>
"""
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests" / "browser"))
import rig  # noqa: E402
import seeds  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402


def description(page, client, selector):
    doc = client.send("DOM.getDocument", {"depth": 0})
    node = client.send("DOM.querySelector", {"nodeId": doc["root"]["nodeId"], "selector": selector})
    tree = client.send("Accessibility.getPartialAXTree", {"nodeId": node["nodeId"], "fetchRelatives": False})
    first = tree["nodes"][0]
    desc = first.get("description", {}).get("value", "")
    name = first.get("name", {}).get("value", "")
    return name, desc


def run_one(p, server, seed, selector, bad_text, label):
    browser = rig.launch(p, "chromium")
    context = rig.new_context(browser, viewport={"width": 390, "height": 844}, device_scale_factor=1,
                              color_scheme="dark", reduced_motion="reduce",
                              storage_state=rig.storage_state(server.base, seed))
    page = context.new_page()
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(server.base + "/")
    client = context.new_cdp_session(page)
    client.send("DOM.enable")
    client.send("Accessibility.enable")
    lines = []
    name, desc = description(page, client, selector)
    hidden_attr = page.eval_on_selector(selector, "el => el.getAttribute('aria-describedby')")
    lines.append(f"{label} | error hidden | name {name!r} | description {desc!r} | aria-describedby {hidden_attr!r}")
    page.click(selector)
    page.keyboard.press("Control+A")
    page.keyboard.type(bad_text, delay=20)
    page.keyboard.press("Tab")
    page.wait_for_timeout(300)
    invalid = page.eval_on_selector(selector, "el => el.getAttribute('aria-invalid')")
    name, desc = description(page, client, selector)
    lines.append(f"{label} | error shown after {bad_text!r} and Tab (aria-invalid {invalid!r}) | name {name!r} | description {desc!r}")
    context.close()
    browser.close()
    return lines, errors


def main():
    server = rig.StaticServer().start()
    out = []
    errs = []
    try:
        with sync_playwright() as p:
            l1, e1 = run_one(p, server, seeds.S1, 'input[aria-label="Char kuey teow price in RM"]', "13.505", "Char kuey teow price in RM (K1 seed)")
            l2, e2 = run_one(p, server, seeds.S2, "#evenSub", "0", "Subtotal in RM (K2 seed)")
            out = l1 + l2
            errs = e1 + e2
    finally:
        server.stop()
    print("\n".join(out))
    print("console/page errors:", json.dumps(errs))


main()
