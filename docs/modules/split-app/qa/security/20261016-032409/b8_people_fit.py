"""B8. A side check from B2, not a security property. In WebKit B2's People line held every label but drew only the first
39 characters after the probe narrowed the page from 1280 to 390. Is that the names or the resize?

cd to this folder, then: python -B b8_people_fit.py --engine chromium|webkit
Five plain names (no character of core R35's class), restored from a version 2 draft. Path "boot at 390" opens the app
at 390 x 844. Path "1280 then 390" opens it at 1280 x 800 and narrows it to 390 x 844, as B2 does. For each, the text of
#peopleSum .sec-txt, which of the R48 (2) summaries it is, the summary box's scrollWidth and clientWidth, and how many
of its characters are drawn with a width (a Range per code point). Writes b8_people_fit-<engine>.json.
"""
import argparse
import json
import time

from common import Probe, say
from b2_injection import BOXES

NAMES = ["<svg onload=f()>", "Ben", "Adds up to RM 0.00", "AAdds up to", "Tom"]
BILL = {"mode": "even", "people": [{"id": f"p{i + 1}", "name": n} for i, n in enumerate(NAMES)], "subtotalText": "100.00",
        "items": [], "serviceText": "10", "sstText": "6", "spare": {"rule": "top"}, "nextId": 6}
DRAFT = json.dumps({"version": 2, "bill": BILL}, separators=(",", ":"))
MEASURE = """() => { const s = document.querySelector('#peopleSum'); return [s.scrollWidth, s.clientWidth,
  getComputedStyle(s).overflow, getComputedStyle(s).textOverflow, getComputedStyle(s).display]; }"""


def summaries(labels):
    fewer = [f"{', '.join(labels[:k])} and {len(labels) - k} more" for k in range(len(labels) - 1, 0, -1)]
    return [", ".join(labels), *fewer, f"{len(labels)} people"]


def read(page):
    measure = page.evaluate(BOXES, "#peopleSum .sec-txt")
    text = measure["text"]
    order = summaries(NAMES)
    return {"text": text, "which": order.index(text) if text in order else None, "chars": len([*text]),
            "drawn": len(measure["boxes"]), "box": page.evaluate(MEASURE)}


def run(engine):
    with Probe("b8_people_fit", engine) as probe:
        for path in ("boot at 390", "1280 then 390"):
            size = {"width": 390, "height": 844} if path == "boot at 390" else {"width": 1280, "height": 800}
            ctx = probe.context(viewport=size)
            page, rec = probe.page(ctx)
            probe.seed(page, rec, DRAFT)
            probe.open_app(page)
            probe.stand_in(page)
            if path != "boot at 390":
                page.set_viewport_size({"width": 390, "height": 844})
                page.wait_for_function("() => getComputedStyle(document.querySelector('#strip')).display !== 'none'")
            first = read(page)
            time.sleep(0.5)
            later = read(page)
            row = {"path": path, "first": first, "after_500_ms": later, "console": rec["console"], "page_errors": rec["page_errors"]}
            row["whole"] = later["drawn"] == later["chars"]
            probe.rows.append(row)
            say(json.dumps(row, ensure_ascii=True))
            ctx.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", choices=["chromium", "webkit"], default="chromium")
    run(parser.parse_args().engine)
