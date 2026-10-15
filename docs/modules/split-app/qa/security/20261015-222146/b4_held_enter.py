"""B4. SEC-04 of 1.0 (accepted for v1.0, to be fixed in v1.1.0) and R57 (a): a held Enter acts once.

python docs/modules/split-app/qa/security/20261015-222146/b4_held_enter.py --engine chromium|webkit [--root <dir> --tag <tag>]
The control is the same probe against the v1.0.0 tree (git archive v1.0.0 index.html src, unpacked in the session
scratchpad), which must show SEC-04 (a blank item added). The green run is the project root. A held key is one
keyboard.down, 520 ms (past the repeat delay), four more keyboard.down 35 ms apart (Playwright marks them repeat), one
keyboard.up. A window capture listener (observation only) records each keydown and its repeat flag, so the run shows
the repeats really came. Writes b4_held_enter-<tag>-<engine>.json.
"""
import argparse
import json
import time

from common import Probe, say

KEY_LOG = """(() => {
  window.testKeys = [];
  window.addEventListener('keydown', (e) => window.testKeys.push(e.key + (e.repeat ? ':repeat' : ':first')), true);
})();"""

ONE_ITEM = json.dumps({"version": 1, "bill": {
    "mode": "item", "people": [{"id": "p1", "name": "Aisyah"}, {"id": "p2", "name": "Ben"}, {"id": "p3", "name": "Chen"}],
    "subtotalText": "", "items": [{"id": "i7", "name": "Nasi lemak ayam", "priceText": "24.90", "who": ["p1"]}],
    "serviceText": "10", "sstText": "6", "nextId": 8}})
S2_TOP = json.dumps({"version": 1, "bill": {
    "mode": "even", "people": [{"id": "p1", "name": "Aisyah"}, {"id": "p2", "name": "Ben"}, {"id": "p3", "name": "Chen"}],
    "subtotalText": "100.00", "items": [], "serviceText": "10", "sstText": "6", "nextId": 4}})

FOCUS = """() => { const a = document.activeElement; if (!a || a === document.body) return 'body';
  return a.tagName.toLowerCase() + (a.id ? '#' + a.id : '') + ' ' + (a.getAttribute('aria-label') || a.textContent.trim().slice(0, 30)); }"""


def hold_enter(page):
    page.keyboard.down("Enter")
    time.sleep(0.52)
    for _ in range(4):
        page.keyboard.down("Enter")
        time.sleep(0.035)
    page.keyboard.up("Enter")
    time.sleep(0.3)


def bill_of(page):
    text = page.evaluate("() => localStorage.getItem('split.draft')")
    bill = json.loads(text)["bill"]
    return {"items": [[i["id"], i["name"]] for i in bill["items"]], "nextId": bill["nextId"], "people": len(bill["people"]),
            "spare": bill.get("spare")}


def case(probe, name, seed, size, target, check, head_only=False):
    if head_only and probe.facts["tag"] != "head":
        return
    ctx = probe.context(extra_scripts=[KEY_LOG], viewport={"width": size[0], "height": size[1]})
    row = {"case": name}
    try:
        page, rec = probe.page(ctx)
        probe.seed(page, rec, seed)
        page.goto(probe.base + "/")
        page.locator(target).wait_for()
        probe.stand_in(page)
        row["before"] = bill_of(page)
        page.locator(target).focus()
        row["focus_before"] = page.evaluate(FOCUS)
        page.evaluate("() => { window.testKeys.length = 0; }")
        hold_enter(page)
        row["keys"] = page.evaluate("() => window.testKeys")
        row["after"] = bill_of(page)
        row["focus_after"] = page.evaluate(FOCUS)
        row["dialogs_open"] = page.evaluate("() => [...document.querySelectorAll('dialog')].filter((d) => d.open).map((d) => d.id)")
        row["csp"] = probe.violations(page)
        row.update(console=rec["console"], page_errors=rec["page_errors"])
        row["repeats_seen"] = sum(1 for k in row["keys"] if k == "Enter:repeat")
        row["verdict"] = check(row)
    except Exception as error:  # noqa: BLE001
        row["error"] = f"{type(error).__name__}: {str(error)[:300]}"
        row["verdict"] = "ERROR"
    finally:
        ctx.close()
    probe.rows.append(row)
    say(f"{row['verdict']}: {name} | before {row.get('before')} | after {row.get('after')} | focus {row.get('focus_after')} | "
        f"repeats {row.get('repeats_seen')} | dialogs {row.get('dialogs_open')} {row.get('error', '')}")


def run(engine, root, tag):
    with Probe(f"b4_held_enter-{tag}", engine, root=root) as probe:
        probe.facts["tag"] = tag
        case(probe, "held Enter on Remove of the only item (SEC-04)", ONE_ITEM, (390, 844),
             'button[aria-label="Remove Nasi lemak ayam"]',
             lambda r: "HOLDS" if r["after"]["items"] == [] and r["after"]["nextId"] == r["before"]["nextId"] and "Add item" in r["focus_after"]
             and r["repeats_seen"] >= 3 else "FAILS")
        case(probe, "held Enter on New bill", S2_TOP, (390, 844), "#newBill",
             lambda r: "HOLDS" if r["dialogs_open"] == ["newDlg"] and "Cancel" in r["focus_after"] and r["after"] == r["before"]
             and r["repeats_seen"] >= 3 else "FAILS")
        case(probe, "held Enter on Splits (R50)", S2_TOP, (390, 844), "#splitsBtn",
             lambda r: "HOLDS" if r["dialogs_open"] == ["splitsDlg"] and r["after"] == r["before"] and r["repeats_seen"] >= 3 else "FAILS",
             head_only=True)
        case(probe, "held Enter on the spare chip (R52)", S2_TOP, (1280, 800), "#spareBtn",
             lambda r: "HOLDS" if r["dialogs_open"] == ["spareDlg"] and r["after"] == r["before"] and r["repeats_seen"] >= 3 else "FAILS",
             head_only=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", choices=["chromium", "webkit"], default="chromium")
    parser.add_argument("--root", default=None)
    parser.add_argument("--tag", default="head")
    args = parser.parse_args()
    run(args.engine, args.root, args.tag)
