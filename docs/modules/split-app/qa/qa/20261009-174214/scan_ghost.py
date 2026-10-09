"""What sits under the dialog buttons once the dialog is gone? (second click of a double click on Cancel / Start new bill)

For each viewport and seed: open the dialog, note the centre of Cancel and of Start new bill, close with Escape and read the
element at the Cancel point; then click Start new bill once and read the element at the Start point on the fresh bill.
Also performs the real mouse double click on both buttons and reports whether the draft changed. Read-only on the app.
"""
import json
import socket
import subprocess
import sys
import time
import urllib.request

import qa_drive as q
from playwright.sync_api import sync_playwright

UNDER_JS = """([x, y]) => { const e = document.elementFromPoint(x, y); if (!e) return null;
  const c = e.closest('button, input, label, a, select, textarea');
  return c ? { tag: c.tagName.toLowerCase(), name: c.getAttribute('aria-label') || c.textContent.trim().slice(0, 30), disabled: !!c.disabled } : { tag: e.tagName.toLowerCase(), name: null, disabled: false }; }"""

SEEDS = {"S1": q.S1, "S2": q.S2, "S5": q.S5, "S3": None}
VIEWPORTS = [(320, 568), (360, 640), (360, 740), (360, 780), (360, 800), (375, 667), (375, 812), (390, 844), (393, 852), (412, 732), (412, 915),
             (414, 896), (430, 932), (768, 1024), (1024, 768), (1280, 800)]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    server = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=q.ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    q.BASE = f"http://127.0.0.1:{port}"
    print("SERVER STARTED pid", server.pid, "port", port, flush=True)
    rows = []
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(q.BASE + "/", timeout=1).close()
                break
            except OSError:
                time.sleep(0.1)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            for name, seed in SEEDS.items():
                for vp in VIEWPORTS:
                    s = q.Session(browser, "scan", viewport=vp, seed=seed)
                    p = s.page
                    before = q.stored_text(p)
                    q.button(p, "New bill").click()
                    cancel = q.centre(q.button(p, "Cancel"))
                    start = q.centre(q.button(p, "Start new bill"))
                    p.keyboard.press("Escape")
                    under_cancel = p.evaluate(UNDER_JS, list(cancel))
                    q.button(p, "New bill").click()
                    q.button(p, "Start new bill").click()
                    under_start = p.evaluate(UNDER_JS, list(start))
                    s.close(record=False)
                    # the real double clicks
                    changed = {}
                    for target in ("Cancel", "Start new bill"):
                        t = q.Session(browser, "scan", viewport=vp, seed=seed)
                        tp = t.page
                        b0, snap0 = q.stored_text(tp), q.snapshot(tp)
                        q.button(tp, "New bill").click()
                        x, y = q.centre(q.button(tp, target))
                        tp.mouse.dblclick(x, y)
                        tp.wait_for_timeout(150)
                        if target == "Cancel":
                            changed[target] = q.snapshot(tp) != snap0 or q.stored_text(tp) != b0
                        else:
                            fresh = json.loads(q.stored_text(tp))["bill"]
                            changed[target] = not (fresh["mode"] == "even" and len(fresh["people"]) == 2 and fresh["subtotalText"] == "" and fresh["items"] == []
                                                   and [pp["name"] for pp in fresh["people"]] == ["Person 1", "Person 2"])
                        t.close(record=False)
                    rows.append({"seed": name, "viewport": f"{vp[0]}x{vp[1]}", "under_cancel": under_cancel, "under_start_on_fresh_bill": under_start,
                                 "dblclick_cancel_changed_bill": changed["Cancel"], "dblclick_start_left_a_changed_new_bill": changed["Start new bill"]})
            browser.close()
    finally:
        server.kill()
        server.wait(10)
        print("SERVER STOPPED pid", server.pid, flush=True)
    for r in rows:
        flag = "HIT " if r["dblclick_cancel_changed_bill"] or r["dblclick_start_left_a_changed_new_bill"] else "ok  "
        print(flag, r["seed"], r["viewport"], "under Cancel:", r["under_cancel"], "| under Start (fresh bill):", r["under_start_on_fresh_bill"],
              "| dblclick Cancel changed:", r["dblclick_cancel_changed_bill"], "| dblclick Start changed new bill:", r["dblclick_start_left_a_changed_new_bill"], flush=True)
    hits = [r for r in rows if r["dblclick_cancel_changed_bill"] or r["dblclick_start_left_a_changed_new_bill"]]
    print("combinations", len(rows), "hits", len(hits), flush=True)
    (q.OUT / "scan-ghost-results.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
