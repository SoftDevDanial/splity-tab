"""Code-review finder (read-only) probe P2. R52's sheet scroll under P1 (makeRoom in src/ui/sheet.js) when the Splits
sheet is already scrolled past its Splits heading before P1 opens. Headless, every context from rig.new_context with the
clipboard recorder. Real gestures only (clicks, a mouse wheel). Writes nothing into the project. Prints one JSON object.
Usage: python probe_sheet_scroll.py <projectRoot> <engine> [<seed name in seeds.py>] [<width>x<height>]
"""
import json
import socket
import sys
from pathlib import Path

root = Path(sys.argv[1])
engine = sys.argv[2] if len(sys.argv) > 2 else "chromium"
SEED = sys.argv[3] if len(sys.argv) > 3 else "T12"
W, H = (int(v) for v in (sys.argv[4] if len(sys.argv) > 4 else "390x844").split("x"))
sys.path.insert(0, str(root / "tests" / "browser"))
import rig  # noqa: E402
import seeds  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

STATE_JS = """() => { const scroll = document.querySelector('#sheetScroll');
  const rows = scroll.querySelectorAll('ul.r-splits > li'), p1 = document.querySelector('#spareDlg');
  return { scrollTop: Math.round(scroll.scrollTop), maxScroll: scroll.scrollHeight - scroll.clientHeight,
    areaTop: scroll.getBoundingClientRect().top, headTop: scroll.querySelector('#sheetSplitsH').getBoundingClientRect().top,
    lastRowBottom: rows[rows.length - 1].getBoundingClientRect().bottom, rowsBelowP1Top: p1.open ?
      [...rows].filter((li) => li.getBoundingClientRect().bottom > p1.getBoundingClientRect().top).length : null,
    p1Open: p1.open, p1Top: p1.open ? p1.getBoundingClientRect().top : null,
    padding: scroll.style.getPropertyValue('padding-bottom') }; }"""
TWO_FRAMES = "() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))"
CHIP = "#splitsDlg .r-spare-acts button[aria-haspopup=dialog]"

log = []
server = rig.StaticServer(root, say=log.append).start()
out = {"engine": engine, "seed": SEED, "size": [W, H], "server": None}
try:
    with sync_playwright() as playwright:
        browser = rig.launch(playwright, engine)
        out["browser_version"] = browser.version
        for case in ("from-the-top", "scrolled-to-the-bottom-first"):
            context = rig.new_context(browser, viewport={"width": W, "height": H}, device_scale_factor=1,
                                      color_scheme="dark", reduced_motion="reduce",
                                      storage_state=rig.storage_state(server.base, getattr(seeds, SEED)))
            page = context.new_page()
            page.goto(server.base + "/")
            assert page.evaluate("window.testClipboardWrites") == 0
            page.click("#splitsBtn")
            page.evaluate(TWO_FRAMES)
            steps = {"sheet open": page.evaluate(STATE_JS)}
            if case == "scrolled-to-the-bottom-first":
                page.mouse.move(195, 500)
                for _ in range(10):
                    page.mouse.wheel(0, 400)
                    page.wait_for_timeout(60)
                page.evaluate(TWO_FRAMES)
                steps["after the wheel"] = page.evaluate(STATE_JS)
            page.click(CHIP)
            page.evaluate(TWO_FRAMES)
            steps["P1 open"] = page.evaluate(STATE_JS)
            out[case] = steps
            context.close()
        browser.close()
finally:
    server.stop()
    port = server.port if hasattr(server, "port") else None
out["server"] = log
with socket.socket() as probe:
    probe.settimeout(1)
    out["port_refuses_after_stop"] = probe.connect_ex(("127.0.0.1", int(log[0].split(" port ")[1].split()[0]))) != 0
print(json.dumps(out, indent=1))
