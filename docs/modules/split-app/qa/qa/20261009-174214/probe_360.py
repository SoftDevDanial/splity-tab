"""Probe: where does the by-item table first overflow at 360 px? (finder exploration, read-only)"""
import json
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path("{workspace}/examples/split")
CLIP = (ROOT / "tests" / "browser" / "clipboard" / "recorder.js").read_text(encoding="utf-8")


def bill(names, prices, who_all=True, service="10", sst="6", mode="item", subtotal=""):
    people = [{"id": f"p{i + 1}", "name": n} for i, n in enumerate(names)]
    items = [{"id": f"i{len(people) + k + 1}", "name": f"Dish {k + 1}", "priceText": pr, "who": [q["id"] for q in people]} for k, pr in enumerate(prices)]
    return json.dumps({"version": 1, "bill": {"mode": mode, "people": people, "subtotalText": subtotal, "items": items,
                                              "serviceText": service, "sstText": sst, "nextId": len(people) + len(items) + 1}}, separators=(",", ":"))


CASES = {
    "S1-like 3 people, short names, RM 59.40": bill(["Aisyah", "Ben", "Chen"], ["15.90", "13.50", "12.00", "18.00"]),
    "3 people 20-char names, RM 59.40": bill(["Muhammad Faiz Hakimi", "Nur Aisyah Humairah", "Lee Wei Jian Ming A"], ["15.90", "13.50", "12.00", "18.00"]),
    "3 people short names, RM 4 digits": bill(["Aisyah", "Ben", "Chen"], ["1590.00", "1350.00", "1200.00", "1800.00"]),
    "3 people 20-char names, RM 4 digits": bill(["Muhammad Faiz Hakimi", "Nur Aisyah Humairah", "Lee Wei Jian Ming A"], ["1590.00", "1350.00", "1200.00", "1800.00"]),
    "3 people short names, RM 5 digits": bill(["Aisyah", "Ben", "Chen"], ["15900.00", "13500.00", "12000.00", "18000.00"]),
    "3 people 20-char names, RM 5 digits": bill(["Muhammad Faiz Hakimi", "Nur Aisyah Humairah", "Lee Wei Jian Ming A"], ["15900.00", "13500.00", "12000.00", "18000.00"]),
    "3 people 20 W names, RM 59.40": bill(["W" * 20, "W" * 20, "W" * 20], ["15.90", "13.50", "12.00", "18.00"]),
    "3 people short names, RM 7 digits": bill(["Aisyah", "Ben", "Chen"], ["99999.99"] * 50),
    "even mode 12 people 20 W names": bill(["W" * 20] * 12, [], mode="even", subtotal="99999.99"),
    "even mode 3 people 20 W names": bill(["W" * 20] * 3, [], mode="even", subtotal="99999.99"),
}
OVERFLOW = """() => ({ scroll: document.documentElement.scrollWidth, inner: window.innerWidth,
  table: (document.querySelector('table.shares') || { getBoundingClientRect: () => ({ right: 0 }) }).getBoundingClientRect().right })"""

port = socket.socket()
port.bind(("127.0.0.1", 0))
number = port.getsockname()[1]
port.close()
server = subprocess.Popen([sys.executable, "-m", "http.server", str(number), "--bind", "127.0.0.1"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
base = f"http://127.0.0.1:{number}"
print("SERVER pid", server.pid, "port", number, flush=True)
try:
    for _ in range(50):
        try:
            urllib.request.urlopen(base + "/", timeout=1).close()
            break
        except OSError:
            time.sleep(0.1)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for width in (360, 390):
            for label, seed in CASES.items():
                ctx = browser.new_context(viewport={"width": width, "height": 780}, device_scale_factor=1, color_scheme="light",
                                          storage_state={"cookies": [], "origins": [{"origin": base, "localStorage": [{"name": "split.draft", "value": seed}]}]})
                ctx.set_default_timeout(8000)
                ctx.add_init_script(script=CLIP)
                page = ctx.new_page()
                page.goto(base + "/")
                print(width, "OVERFLOW" if page.evaluate(OVERFLOW)["scroll"] > width else "ok      ", label, page.evaluate(OVERFLOW), flush=True)
                ctx.close()
        browser.close()
finally:
    server.kill()
    server.wait(10)
    print("SERVER STOPPED pid", server.pid, flush=True)
