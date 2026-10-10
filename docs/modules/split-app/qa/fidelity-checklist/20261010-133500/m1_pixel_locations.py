"""Where the differing pixels of the two M1 gate pairs are. Each pixel that differs at any level between the gate's golden.png and candidate.png is
classed as: on a rounded corner (within 7 px of a corner of an element whose border-radius is above 0, taken from the golden's own DOM at that
viewport), or elsewhere (then its element is named). Reads the gate run folder, opens the golden in Chromium only to read element rectangles.

usage: python m1_pixel_locations.py <gate run folder>
"""
import sys

sys.dont_write_bytecode = True
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

import common as C

RECTS = """() => Array.from(document.querySelectorAll('body *')).filter((e) => getComputedStyle(e).display !== 'none' && e.getClientRects().length > 0).map((e) => {
  const cs = getComputedStyle(e); const r = e.getBoundingClientRect();
  return { tag: e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.split(' ')[0] : ''), x: r.x, y: r.y + scrollY, w: r.width, h: r.height,
           radius: parseFloat(cs.borderTopLeftRadius) || 0, text: Array.from(e.childNodes).some((n) => n.nodeType === 3 && n.nodeValue.trim().length) }; })"""


def main():
    run = Path(sys.argv[1])
    out = []
    with sync_playwright() as pw:
        browser = C.launch(pw)
        for vp in ((390, 844), (1280, 800)):
            ctx = C.gold_ctx(browser, vp)
            g = C.open_golden(ctx, "new-bill-dialog")
            els = g.js(RECTS)
            ctx.close()
            folder = run / f"new-bill-dialog-{vp[0]}x{vp[1]}"
            a = np.asarray(Image.open(folder / "golden.png").convert("RGB"), dtype=np.int32)
            b = np.asarray(Image.open(folder / "candidate.png").convert("RGB"), dtype=np.int32)
            d = np.abs(a - b).max(axis=2)
            ys, xs = np.nonzero(d)
            rounded = [e for e in els if e["radius"] > 0]
            on_corner, elsewhere = 0, []
            for x, y in zip(xs.tolist(), ys.tolist()):
                near = False
                for e in rounded:
                    for cx, cy in ((e["x"], e["y"]), (e["x"] + e["w"], e["y"]), (e["x"], e["y"] + e["h"]), (e["x"] + e["w"], e["y"] + e["h"])):
                        if abs(x + 0.5 - cx) <= 7 and abs(y + 0.5 - cy) <= 7:
                            near = True
                            break
                    if near:
                        break
                if near:
                    on_corner += 1
                else:
                    inside = [e["tag"] for e in els if e["text"] and e["x"] <= x <= e["x"] + e["w"] and e["y"] <= y <= e["y"] + e["h"]]
                    elsewhere.append({"pixel": [x, y], "delta": int(d[y, x]), "text_elements_here": inside[-2:]})
            row = {"viewport": f"{vp[0]}x{vp[1]}", "differing_pixels": int(len(xs)), "max_delta": int(d.max()), "on_a_rounded_corner": on_corner, "elsewhere": len(elsewhere),
                   "elsewhere_detail": elsewhere[:12], "rounded_elements": len(rounded)}
            out.append(row)
            print({k: v for k, v in row.items() if k != "elsewhere_detail"})
            for e in elsewhere[:8]:
                print("   ", e)
        browser.close()
    C.dump("m1_pixel_locations.json", out)


if __name__ == "__main__":
    main()
