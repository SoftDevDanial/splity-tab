"""Full-page evidence for the table overflow seen at 360 px when the amounts grow (outside the qa.md scenarios)."""
import json
import socket
import subprocess
import sys
import time
import urllib.request

import qa_drive as q
from playwright.sync_api import sync_playwright


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    server = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=q.ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    q.BASE = f"http://127.0.0.1:{port}"
    print("SERVER STARTED pid", server.pid, "port", port, flush=True)
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(q.BASE + "/", timeout=1).close()
                break
            except OSError:
                time.sleep(0.1)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            for factor in (10, 11, 12, 20):
                seed = q.scaled_s1(factor)
                s = q.Session(browser, "overflow", viewport=(360, 780), seed=seed)
                p = s.page
                o = p.evaluate(q.OVERFLOW_JS)
                foot = q.panel(p)["foot"][0]
                prices = [i["priceText"] for i in json.loads(seed)["bill"]["items"]]
                print(f"factor {factor} prices {prices} check row {foot} scrollWidth {o['scrollWidth']} / {o['innerWidth']}", flush=True)
                if factor in (12, 20):
                    q.SHOTS.mkdir(exist_ok=True)
                    p.screenshot(path=str(q.SHOTS / f"overflow-full-360-x{factor}.png"), full_page=True)
                s.close(record=False)
            browser.close()
    finally:
        server.kill()
        server.wait(10)
        print("SERVER STOPPED pid", server.pid, flush=True)


if __name__ == "__main__":
    main()
