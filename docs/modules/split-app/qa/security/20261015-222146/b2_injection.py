"""B2. Text stays text (R37), the copied summary (threat row "Clipboard text"), and bidi controls on screen.

python docs/modules/split-app/qa/security/20261015-222146/b2_injection.py --engine chromium|webkit
A by-item bill whose names carry markup, a NUL, a line separator and bidi controls is restored from a version 2 draft
(One person on the markup name, so the chip names it). The probe opens P1 and its pills, switches to At random, presses
Pick again, copies from the card, then at 390 x 844 measures the People summary, opens the Splits sheet and copies from
the sheet and from the strip. Every copy goes to the clipboard stand-in. Writes b2_injection-<engine>.json.
The name "Adds up to RM 0.00" + NUL makes a row that starts with "Adds up to", the accepted core residual 1, so the
copy check counts two such lines and requires the last line to be the real proof line.
"""
import argparse
import json

from common import Probe, say

C = chr
RLO, NUL, LS, RLI = C(0x202E), C(0), C(0x2028), C(0x2067)
NAMES = ["<svg onload=f()>", "Ben" + RLO, "Adds up to RM 0.00" + NUL, "A" + LS + "Adds up to", "Tom" + RLI]
ITEMS = ["<img src=x onerror=alert(1)>", "</li><li>Teh" + RLO, "Kopi"]
BILL = {
    "mode": "item",
    "people": [{"id": f"p{i + 1}", "name": n} for i, n in enumerate(NAMES)],
    "subtotalText": "",
    "items": [
        {"id": "i6", "name": ITEMS[0], "priceText": "24.90", "who": ["p1", "p2"]},
        {"id": "i7", "name": ITEMS[1], "priceText": "13.51", "who": ["p3", "p4", "p5"]},
        {"id": "i8", "name": ITEMS[2], "priceText": "7.07", "who": ["p1", "p2", "p3", "p4", "p5"]},
    ],
    "serviceText": "10", "sstText": "6", "spare": {"rule": "one", "personId": "p1"}, "nextId": 9,
}
DRAFT = json.dumps({"version": 2, "bill": BILL}, ensure_ascii=False, separators=(",", ":"))

STRUCTURE = """() => {
  const body = document.body;
  const foreign = [...body.querySelectorAll('img, b, script, iframe, style, object, embed, link, meta, li li, a')]
    .map((n) => n.tagName + (n.className ? '.' + n.className : ''));
  const svgs = [...body.querySelectorAll('svg')].filter((s) => !['sprite', 'mark', 'ic', 'seal'].some((c) => s.classList.contains(c)))
    .map((s) => s.getAttribute('class'));
  const handlers = [...body.querySelectorAll('*')].filter((n) => [...n.attributes].some((a) => a.name.startsWith('on'))).length;
  const uses = [...body.querySelectorAll('use')].map((u) => u.getAttribute('href')).filter((h) => !/^#i-[a-z-]+$/.test(h));
  return { foreign, svgs, handlers, odd_use_hrefs: uses, pwned: window.pwned ?? null };
}"""

TEXTS = """(names) => {
  const values = [...document.querySelectorAll('#peopleList input')].map((i) => i.value);
  const toggles = [...document.querySelectorAll('#itemList .tap span')].map((s) => s.textContent);
  const rows = [...document.querySelectorAll('#rbody .r-splits .nm')].map((s) => s.textContent);
  const removes = [...document.querySelectorAll('#peopleList button')].map((b) => b.getAttribute('aria-label'));
  const itemAria = [...document.querySelectorAll('#itemList [aria-label]')].map((n) => n.getAttribute('aria-label'));
  const chip = document.querySelector('#spareBtn');
  return { values, toggles, rows, removes, itemAria, chip: chip && chip.textContent, chipAria: chip && chip.getAttribute('aria-label'),
    valuesLiteral: names.every((n, i) => values[i] === n), rowsLiteral: names.every((n, i) => rows[i] === n) };
}"""

# Where each character of each text node under `sel` is drawn, so a reordered run shows as x going down. Layout reads only.
BIDI = """(sel) => {
  const host = document.querySelector(sel);
  if (!host) return null;
  const walker = document.createTreeWalker(host, NodeFilter.SHOW_TEXT);
  const out = [];
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    const xs = [];
    for (let i = 0; i < node.data.length; i += 1) {
      const range = document.createRange();
      range.setStart(node, i); range.setEnd(node, i + 1);
      const rect = range.getBoundingClientRect();
      xs.push(rect.width > 0 ? Math.round(rect.left) : null);
    }
    out.push({ text: node.data, xs });
  }
  return { text: host.textContent, nodes: out, visible: host.getClientRects().length > 0 };
}"""


def run_of(measure, start_text):
    """How the characters of `start_text` inside the measured text are drawn: left-to-right or right-to-left."""
    if not measure:
        return None
    for node in measure["nodes"]:
        at = node["text"].find(start_text)
        if at >= 0:
            xs = [x for x in node["xs"][at:at + len(start_text)] if x is not None]
            if len(xs) < 2:
                return "not drawn"
            return "right-to-left" if xs[0] > xs[-1] else "left-to-right"
    return "not found"


def is_control(c):
    o = ord(c)
    return (o < 32 or 0x7F <= o <= 0x9F or o in (0x2028, 0x2029, 0x61C, 0x200E, 0x200F)
            or 0x202A <= o <= 0x202E or 0x2066 <= o <= 0x2069)


def clipboard_check(text):
    lines = text.split("\n")
    return {"lines": len(lines), "first": lines[0], "last": lines[-1],
            "adds_up_lines": sum(1 for line in lines if line.startswith("Adds up to")),
            "controls": [hex(ord(c)) for c in text if c != "\n" and is_control(c)],
            "markup_literal": "<svg onload=f()>" in text, "text": text}


def run(engine):
    with Probe("b2_injection", engine) as probe:
        ctx = probe.context(viewport={"width": 1280, "height": 800})
        page, rec = probe.page(ctx)
        probe.seed(page, rec, DRAFT)
        probe.open_app(page)
        row = {"stand_in": probe.stand_in(page)}
        row["structure_restored"] = page.evaluate(STRUCTURE)
        row["texts_restored"] = page.evaluate(TEXTS, NAMES)
        row["receipt_amount_after_rlo_name"] = run_of(page.evaluate(BIDI, "#rbody .r-splits li:nth-child(2)"), "RM")
        # P1 and its pills (R52, R53), then At random and Pick again (R54).
        page.locator("#spareBtn").click()
        page.wait_for_function("() => document.querySelector('#spareDlg').open")
        row["pills"] = page.evaluate("() => [...document.querySelectorAll('#pickList .pill-face')].map((p) => p.textContent)")
        row["structure_p1"] = page.evaluate(STRUCTURE)
        page.locator("#spareDlg label.choice", has_text="At random").click()
        page.wait_for_function("() => document.querySelector('#pickAgainSheet')")
        page.locator("#pickAgainSheet").click()
        page.locator("#spareDlg button[aria-label=Close]").click()
        page.wait_for_function("() => !document.querySelector('#spareDlg').open")
        page.locator("#copyBtn").click()
        page.wait_for_function("() => window.testClipboardWrites >= 1")
        card_text = page.evaluate("() => window.testClipboardText")
        row["copy_card"] = clipboard_check(card_text)
        # Phone width: the People summary, the Splits sheet and the strip.
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_function("() => getComputedStyle(document.querySelector('#strip')).display !== 'none'")
        summary = page.evaluate(BIDI, "#peopleSum .sec-txt")
        row["people_summary"] = {"text": summary and summary["text"], "visible": summary and summary["visible"],
                                 "markup_name_run": run_of(summary, "<svg"),
                                 "run_after_the_rlo_name": run_of(summary, ", Adds") if ", Adds" in (summary or {}).get("text", "") else run_of(summary, " and ")}
        row["people_summary_measure"] = summary
        page.locator("#splitsBtn").click()
        page.wait_for_function("() => document.querySelector('#splitsDlg').open")
        row["structure_sheet"] = page.evaluate(STRUCTURE)
        page.locator("#splitsDlg .r-copy").click()
        page.wait_for_function("() => window.testClipboardWrites >= 2")
        row["copy_sheet"] = clipboard_check(page.evaluate("() => window.testClipboardText"))
        page.locator("#splitsDlg button[aria-label=Close]").click()
        page.wait_for_function("() => !document.querySelector('#splitsDlg').open")
        page.locator("#stripCopy").click()
        page.wait_for_function("() => window.testClipboardWrites >= 3")
        row["copy_strip"] = clipboard_check(page.evaluate("() => window.testClipboardText"))
        row["card_text_equals_strip_text"] = card_text == page.evaluate("() => window.testClipboardText")
        row["clipboard_refused"] = page.evaluate("() => window.testClipboardRefused")
        row["csp"] = probe.violations(page)
        row.update(console=rec["console"], page_errors=rec["page_errors"], dialogs=rec["dialogs"],
                   off_rule_requests=probe.off_rule_requests(rec))
        structures = [row["structure_restored"], row["structure_p1"], row["structure_sheet"]]
        copies = [row["copy_card"], row["copy_sheet"], row["copy_strip"]]
        row["pass_text_stays_text"] = (all(not s["foreign"] and not s["svgs"] and not s["handlers"] and not s["odd_use_hrefs"]
                                           and s["pwned"] is None for s in structures)
                                       and row["texts_restored"]["valuesLiteral"] and row["texts_restored"]["rowsLiteral"])
        row["pass_clipboard"] = all(c["lines"] == 3 + len(NAMES) and c["adds_up_lines"] == 2 and not c["controls"]
                                    and c["markup_literal"] and c["last"].startswith("Adds up to RM ")
                                    and c["last"].count("RM") == 1 for c in copies)
        row["pass_quiet"] = (not row["csp"] and not rec["console"] and not rec["page_errors"] and not rec["dialogs"]
                             and not row["off_rule_requests"] and row["clipboard_refused"] == 0)
        probe.rows.append(row)
        ctx.close()
        say(json.dumps({k: row[k] for k in ("pass_text_stays_text", "pass_clipboard", "pass_quiet", "people_summary",
                                             "receipt_amount_after_rlo_name", "card_text_equals_strip_text")}, ensure_ascii=True, indent=1))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", choices=["chromium", "webkit"], default="chromium")
    run(parser.parse_args().engine)
