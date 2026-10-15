"""Code-review finder (read-only) probe P3. R20's --rows for an odd number of people. A 7-person even bill at 1280 x 800,
headless Chromium, served from <appRoot> (the project, or a mutant copy in scratch). Reads --rows and the distinct column
positions of the splits rows. Writes nothing. Usage: python probe_rows.py <projectRoot> <appRoot> [people]
"""
import json
import socket
import sys
from pathlib import Path

project, app = Path(sys.argv[1]), Path(sys.argv[2])
count = int(sys.argv[3]) if len(sys.argv) > 3 else 7
sys.path.insert(0, str(project / "tests" / "browser"))
import rig  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

people = [{"id": f"p{n}", "name": f"P{n}"} for n in range(1, count + 1)]
draft = json.dumps({"version": 2, "bill": {"mode": "even", "people": people, "subtotalText": "100.00", "items": [],
                    "serviceText": "10", "sstText": "6", "spare": {"rule": "top"}, "nextId": count + 1}})
READ_JS = """() => { const list = document.querySelector('#splits');
  const lefts = [...list.children].map((li) => Math.round(li.getBoundingClientRect().left));
  return { cls: list.className, rows: list.style.getPropertyValue('--rows'), columns: [...new Set(lefts)].length,
    listRight: Math.round(list.getBoundingClientRect().right), cardRight: Math.round(document.querySelector('#card').getBoundingClientRect().right),
    overflow: list.scrollWidth > list.clientWidth }; }"""
log = []
server = rig.StaticServer(app, say=log.append).start()
try:
    with sync_playwright() as playwright:
        browser = rig.launch(playwright, "chromium")
        context = rig.new_context(browser, viewport={"width": 1280, "height": 800}, device_scale_factor=1,
                                  color_scheme="dark", reduced_motion="reduce",
                                  storage_state=rig.storage_state(server.base, draft))
        page = context.new_page()
        page.goto(server.base + "/")
        found = page.evaluate(READ_JS)
        context.close()
        browser.close()
finally:
    server.stop()
port = int(log[0].split(" port ")[1].split()[0])
with socket.socket() as probe:
    probe.settimeout(1)
    refused = probe.connect_ex(("127.0.0.1", port)) != 0
print(json.dumps({"app": str(app), "people": count, "found": found, "server": log, "port_refuses_after_stop": refused}))
