"""B3. R38 (CSP and the four CSSOM targets), R39 (nothing leaves the device) and PD-19 (Math.random only into the draws).

python docs/modules/split-app/qa/security/20261015-222146/b3_csp_network_style_random.py --engine chromium|webkit
Three pages in one context each, every gesture real (click, type, press). Page A: cold boot at 390 x 844, typing,
sections, the strip, the Splits sheet, P1 over it (One person, a pill, At random, Pick again), Escape, copies, By item
with an item, the New bill dialog (Cancel, then Start new bill). Page B: a restored At random bill at 1280 x 800, P1
beside the card, the card's Pick again, a resize across 1024 px with P1 open. Page C: a twelve person even bill at
1280 x 800 (the `many` list). An init script records each Math.random call with its stack (observation only).
After the flows, four positive controls show the listener sees a violation. Writes b3_csp_network_style_random-<engine>.json.
"""
import argparse
import json

from common import Probe, say

RANDOM_SPY = """(() => {
  const real = Math.random;
  window.testRandomCalls = [];
  Math.random = function random() {
    const stack = (new Error().stack || '').split('\\n').filter((l) => l.includes('/src/')).slice(0, 4).join(' | ');
    window.testRandomCalls.push(stack);
    return real();
  };
})();"""

STYLES = """() => [...document.querySelectorAll('[style]')].map((n) =>
  (n.id ? '#' + n.id : n.tagName.toLowerCase() + '.' + [...n.classList].join('.')) + ' => ' + n.getAttribute('style'))"""


def s2_random():
    bill = {"mode": "even", "people": [{"id": "p1", "name": "Aisyah"}, {"id": "p2", "name": "Ben"}, {"id": "p3", "name": "Chen"}],
            "subtotalText": "100.00", "items": [], "serviceText": "10", "sstText": "6",
            "spare": {"rule": "random", "order": ["p2", "p3", "p1"]}, "nextId": 4}
    return json.dumps({"version": 2, "bill": bill})


def twelve():
    people = [{"id": f"p{i}", "name": f"P{i}"} for i in range(1, 13)]
    bill = {"mode": "even", "people": people, "subtotalText": "100.05", "items": [], "serviceText": "10", "sstText": "6",
            "spare": {"rule": "top"}, "nextId": 13}
    return json.dumps({"version": 2, "bill": bill})


def type_into(page, selector, text):
    page.locator(selector).click()
    page.keyboard.press("Control+A")
    page.keyboard.type(text)


def wait_closed(page, dialog_id):
    page.wait_for_function(f"() => !document.querySelector('#{dialog_id}').open", timeout=2000)


def page_a(probe, page, out):
    page.goto(probe.base + "/")
    page.wait_for_function("() => document.querySelector('#rbody').children.length > 0")
    out["stand_in"] = probe.stand_in(page)
    names = page.locator("#peopleList input")
    names.nth(0).click(); page.keyboard.type("Aisyah")
    names.nth(1).click(); page.keyboard.type("Ben")
    page.locator("#peopleBlk button.btn", has_text="Add person").click()
    page.keyboard.type("Chen")
    page.locator("#chargesBtn").click()
    type_into(page, "#svc", "10")
    type_into(page, "#sst", "6")
    type_into(page, "#evenSub", "100.00")
    page.wait_for_function("() => document.querySelector('#stripTotal')")
    out["strip_total"] = page.locator("#stripTotal").text_content()
    page.locator("#splitsBtn").click()
    page.wait_for_function("() => document.querySelector('#splitsDlg').open")
    page.locator("#splitsDlg .r-spare button[aria-haspopup=dialog]").click()
    page.wait_for_function("() => document.querySelector('#spareDlg').open")
    out["styles_p1_over_sheet"] = page.evaluate(STYLES)
    page.locator("#spareDlg label.choice", has_text="One person").click()
    page.wait_for_function("() => document.querySelector('#pickList .pill')")
    page.locator("#pickList label.pill").nth(1).click()
    page.locator("#spareDlg label.choice", has_text="At random").click()
    page.wait_for_function("() => document.querySelector('#pickAgainSheet')")
    page.locator("#pickAgainSheet").click()
    out["styles_p1_random"] = page.evaluate(STYLES)
    page.keyboard.press("Escape")
    wait_closed(page, "spareDlg")
    page.locator("#splitsDlg .r-spare button.chip-btn", has_text="Pick again").click()
    page.locator("#splitsDlg .r-copy").click()
    page.wait_for_function("() => window.testClipboardWrites >= 1")
    page.locator("#splitsDlg button[aria-label=Close]").click()
    wait_closed(page, "splitsDlg")
    page.locator("#stripCopy").click()
    page.wait_for_function("() => window.testClipboardWrites >= 2")
    page.locator("label", has_text="By item").click()
    page.locator("#itemsBlock button.btn", has_text="Add item").click()
    page.keyboard.type("Nasi lemak")
    page.locator("#itemList input[inputmode=decimal]").first.click()
    page.keyboard.type("24.90")
    page.locator("#itemList .tap").first.click()
    page.locator("#peopleBtn").click()
    page.locator("#newBill").click()
    page.wait_for_function("() => document.querySelector('#newDlg').open")
    page.locator("#newDlg button", has_text="Cancel").click()
    wait_closed(page, "newDlg")
    page.locator("#newBill").click()
    page.wait_for_function("() => document.querySelector('#newDlg').open")
    page.locator("#startNew").click()
    wait_closed(page, "newDlg")
    out["styles_end_a"] = page.evaluate(STYLES)


def page_b(probe, page, out):
    probe.seed(page, out["_rec"], s2_random())
    page.goto(probe.base + "/")
    page.wait_for_function("() => document.querySelector('#spareBtn')")
    probe.stand_in(page)
    page.locator("#pickAgain").click()
    page.locator("#spareBtn").click()
    page.wait_for_function("() => document.querySelector('#spareDlg').open")
    out["styles_p1_desktop"] = page.evaluate(STYLES)
    page.locator("#pickAgainSheet").click()
    page.set_viewport_size({"width": 800, "height": 800})
    page.wait_for_function("() => !document.querySelector('#spareDlg').style.left")
    out["styles_p1_after_narrowing"] = page.evaluate(STYLES)
    page.set_viewport_size({"width": 1280, "height": 800})
    page.wait_for_function("() => document.querySelector('#spareDlg').style.left !== ''")
    page.locator("#spareDlg button[aria-label=Close]").click()
    wait_closed(page, "spareDlg")
    page.locator("#copyBtn").click()
    page.wait_for_function("() => window.testClipboardWrites >= 1")
    out["styles_end_b"] = page.evaluate(STYLES)


def page_c(probe, page, out):
    probe.seed(page, out["_rec"], twelve())
    page.goto(probe.base + "/")
    page.wait_for_function("() => document.querySelector('ul.r-splits.many')")
    probe.stand_in(page)
    out["styles_many"] = page.evaluate(STYLES)


CONTROLS = """async () => {
  const before = window.testCspViolations.length;
  const s = document.createElement('script'); s.textContent = 'window.inlineRan = 1'; document.body.append(s);
  const d = document.createElement('div'); d.setAttribute('style', 'color: red'); document.body.append(d);
  let fetched = 'not tried';
  try { await fetch('/'); fetched = 'resolved'; } catch (e) { fetched = 'rejected'; }
  const img = new Image(); img.src = 'http://127.0.0.1:9/x.png'; document.body.append(img);
  await new Promise((r) => setTimeout(r, 300));
  const added = window.testCspViolations.slice(before).map((v) => v.violatedDirective);
  d.remove(); img.remove(); s.remove();
  return { inlineRan: window.inlineRan ?? null, fetched, added };
}"""


def run(engine):
    with Probe("b3_csp_network_style_random", engine) as probe:
        out = {}
        ctx = probe.context(extra_scripts=[RANDOM_SPY], viewport={"width": 390, "height": 844})
        try:
            for name, flow, size in (("A", page_a, (390, 844)), ("B", page_b, (1280, 800)), ("C", page_c, (1280, 800))):
                page, rec = probe.page(ctx)
                page.set_viewport_size({"width": size[0], "height": size[1]})
                part = {"_rec": rec}
                try:
                    flow(probe, page, part)
                    part["flow"] = "completed"
                except Exception as error:  # noqa: BLE001
                    part["flow"] = f"broke: {type(error).__name__}: {str(error)[:300]}"
                part.pop("_rec")
                part["csp"] = probe.violations(page)
                part["random_calls"] = page.evaluate("() => window.testRandomCalls")
                part["clipboard_writes"] = page.evaluate("() => window.testClipboardWrites")
                part["clipboard_refused"] = page.evaluate("() => window.testClipboardRefused")
                part.update(console=rec["console"], page_errors=rec["page_errors"], dialogs=rec["dialogs"],
                            requests=rec["requests"], off_rule_requests=probe.off_rule_requests(rec))
                if name == "C":
                    part["positive_controls"] = page.evaluate(CONTROLS)
                    part["off_rule_requests_after_controls"] = probe.off_rule_requests(rec)
                out[name] = part
                page.close()
        finally:
            ctx.close()
        allowed_style = ("--strip-h", "--rows", "left", "bottom", "padding-bottom")
        style_lines = [line for key, value in out.items() for k2, lines in value.items() if k2.startswith("styles") for line in lines]
        out["style_lines_distinct"] = sorted(set(style_lines))
        out["style_props_outside_r38"] = sorted({decl.split(":")[0].strip() for line in style_lines for decl in line.split(" => ")[1].split(";")
                                                 if decl.strip() and decl.split(":")[0].strip() not in allowed_style})
        calls = [c for part in ("A", "B", "C") for c in out[part]["random_calls"]]
        out["random_calls_total"] = len(calls)
        out["random_calls_outside_spare_js"] = [c for c in calls if "/src/core/spare.js" not in c]
        out["pass"] = (all(out[p]["flow"] == "completed" and not out[p]["csp"] and not out[p]["console"] and not out[p]["page_errors"]
                           and not out[p]["off_rule_requests"] and out[p]["clipboard_refused"] == 0 for p in ("A", "B", "C"))
                       and not out["style_props_outside_r38"] and not out["random_calls_outside_spare_js"] and calls)
        probe.rows.append(out)
        say(json.dumps({"pass": out["pass"], "flows": {p: out[p]["flow"] for p in "ABC"},
                        "csp": {p: len(out[p]["csp"]) for p in "ABC"}, "console": {p: out[p]["console"] for p in "ABC"},
                        "page_errors": {p: out[p]["page_errors"] for p in "ABC"},
                        "requests": {p: len(out[p]["requests"]) for p in "ABC"}, "off_rule": {p: out[p]["off_rule_requests"] for p in "ABC"},
                        "styles": out["style_lines_distinct"], "style_outside": out["style_props_outside_r38"],
                        "random_calls": out["random_calls_total"], "random_outside": out["random_calls_outside_spare_js"][:3],
                        "controls": out["C"].get("positive_controls"), "off_rule_after_controls": out["C"].get("off_rule_requests_after_controls")},
                       indent=1))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", choices=["chromium", "webkit"], default="chromium")
    run(parser.parse_args().engine)
