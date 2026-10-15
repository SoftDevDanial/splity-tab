"""B4, rerun on today's tree. The threat rows "The bill, as the user left it" (pointer repeats, R7, R27, R57 (b)) and
"(v1.1.0) Keyboard auto-repeat" (R57 (a)), with Dismiss note, the armer task A23 added (1f1eb97).

cd to this folder, then: python -B b4_held_enter.py --engine chromium|webkit [--root <tree> --tag <tag>]
The four held-Enter cases of the step 5 probe (qa/security/20261015-222146/b4_held_enter.py) unchanged, then Dismiss note.
A held key is one keyboard.down, 520 ms (past the repeat delay), four more keyboard.down 35 ms apart (Playwright marks
them repeat), one keyboard.up. The note comes from an unreadable draft ("{"), which R27 replaces with newBill() saved
at once. A window listener in the capture phase logs each keydown and its repeat flag, so the run shows the repeats
came, and one in the bubble phase logs each click that reached the page, so a cancelled repeat press is not counted.
Dismiss note cases, at 390 x 844 and 1280 x 800. A held Enter, a double click and a triple click (page.mouse at the
button's centre). The property (R27 as changed 2026-10-16). The note is gone, focus is on New bill, no dialog is open,
People and Charges keep the state one click leaves, the stored draft is unchanged, and the only click that reached the
page is the one on Dismiss note.
--root runs the same cases on a control tree (798f17f, before A23), where the Dismiss cases must go RED.
Writes b4_held_enter-<tag>-<engine>.json.
"""
import argparse
import json
import time

from common import Probe, say

KEY_LOG = """(() => {
  window.testKeys = []; window.testClicks = [];
  window.addEventListener('keydown', (e) => window.testKeys.push(e.key + (e.repeat ? ':repeat' : ':first')), true);
  window.addEventListener('click', (e) => { const t = e.target.closest('button, [id]') || e.target;
    window.testClicks.push((t.id || t.getAttribute('aria-label') || t.tagName.toLowerCase()) + ':' + e.detail); });
})();"""

ONE_ITEM = json.dumps({"version": 1, "bill": {
    "mode": "item", "people": [{"id": "p1", "name": "Aisyah"}, {"id": "p2", "name": "Ben"}, {"id": "p3", "name": "Chen"}],
    "subtotalText": "", "items": [{"id": "i7", "name": "Nasi lemak ayam", "priceText": "24.90", "who": ["p1"]}],
    "serviceText": "10", "sstText": "6", "nextId": 8}})
S2_TOP = json.dumps({"version": 1, "bill": {
    "mode": "even", "people": [{"id": "p1", "name": "Aisyah"}, {"id": "p2", "name": "Ben"}, {"id": "p3", "name": "Chen"}],
    "subtotalText": "100.00", "items": [], "serviceText": "10", "sstText": "6", "nextId": 4}})
UNREADABLE = "{"

FOCUS = """() => { const a = document.activeElement; if (!a || a === document.body) return 'body';
  return a.tagName.toLowerCase() + (a.id ? '#' + a.id : '') + ' ' + (a.getAttribute('aria-label') || a.textContent.trim().slice(0, 30)); }"""
SECTIONS = """() => ['#peopleBtn', '#chargesBtn'].map((s) => { const b = document.querySelector(s);
  return b && getComputedStyle(b).display !== 'none' ? b.getAttribute('aria-expanded') : 'not shown'; })"""


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
            "spare": bill.get("spare"), "raw": text}


def case(probe, name, seed, size, target, gesture, check):
    ctx = probe.context(extra_scripts=[KEY_LOG], viewport={"width": size[0], "height": size[1]})
    row = {"case": name, "size": size, "gesture": gesture}
    try:
        page, rec = probe.page(ctx)
        probe.seed(page, rec, seed)
        page.goto(probe.base + "/")
        page.locator(target).wait_for()
        probe.stand_in(page)
        row["before"] = bill_of(page)
        row["sections_before"] = page.evaluate(SECTIONS)
        page.evaluate("() => { window.testKeys.length = 0; window.testClicks.length = 0; }")
        if gesture == "held Enter":
            page.locator(target).focus()
            row["focus_before"] = page.evaluate(FOCUS)
            hold_enter(page)
        else:
            box = page.locator(target).bounding_box()
            x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
            page.mouse.click(x, y, click_count=2 if gesture == "double click" else 3)
            time.sleep(0.3)
        row["keys"] = page.evaluate("() => window.testKeys")
        row["clicks_reached"] = page.evaluate("() => window.testClicks")
        row["after"] = bill_of(page)
        row["sections_after"] = page.evaluate(SECTIONS)
        row["focus_after"] = page.evaluate(FOCUS)
        row["note_present"] = page.evaluate("() => !!document.querySelector('#dismissNote')")
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
    say(f"{row['verdict']}: {name} {size[0]} | after {({k: v for k, v in (row.get('after') or {}).items() if k != 'raw'})} | "
        f"focus {row.get('focus_after')} | repeats {row.get('repeats_seen')} | clicks {row.get('clicks_reached')} | "
        f"dialogs {row.get('dialogs_open')} | sections {row.get('sections_before')} -> {row.get('sections_after')} {row.get('error', '')}")


def dismiss_holds(r):
    one_click_state = r["sections_before"] if r["size"][0] >= 1024 else ["true", "false"]
    reached = [c for c in r["clicks_reached"]]
    ok = (not r["note_present"] and r["focus_after"].startswith("button#newBill") and r["dialogs_open"] == []
          and r["after"]["raw"] == r["before"]["raw"] and r["sections_after"] == one_click_state
          and reached == ["dismissNote:" + ("0" if r["gesture"] == "held Enter" else "1")]
          and not r["csp"] and not r["console"] and not r["page_errors"])
    if r["gesture"] == "held Enter":
        ok = ok and r["repeats_seen"] >= 3
    return "HOLDS" if ok else "FAILS"


def run(engine, root, tag):
    with Probe(f"b4_held_enter-{tag}", engine, root=root) as probe:
        probe.facts["tag"] = tag
        case(probe, "held Enter on Remove of the only item (SEC-04)", ONE_ITEM, (390, 844),
             'button[aria-label="Remove Nasi lemak ayam"]', "held Enter",
             lambda r: "HOLDS" if r["after"]["items"] == [] and r["after"]["nextId"] == r["before"]["nextId"] and "Add item" in r["focus_after"]
             and r["repeats_seen"] >= 3 else "FAILS")
        case(probe, "held Enter on New bill", S2_TOP, (390, 844), "#newBill", "held Enter",
             lambda r: "HOLDS" if r["dialogs_open"] == ["newDlg"] and "Cancel" in r["focus_after"] and r["after"] == r["before"]
             and r["repeats_seen"] >= 3 else "FAILS")
        case(probe, "held Enter on Splits (R50)", S2_TOP, (390, 844), "#splitsBtn", "held Enter",
             lambda r: "HOLDS" if r["dialogs_open"] == ["splitsDlg"] and r["after"] == r["before"] and r["repeats_seen"] >= 3 else "FAILS")
        case(probe, "held Enter on the spare chip (R52)", S2_TOP, (1280, 800), "#spareBtn", "held Enter",
             lambda r: "HOLDS" if r["dialogs_open"] == ["spareDlg"] and r["after"] == r["before"] and r["repeats_seen"] >= 3 else "FAILS")
        for size in ((390, 844), (1280, 800)):
            for gesture in ("held Enter", "double click", "triple click"):
                case(probe, f"{gesture} on Dismiss note (A23)", UNREADABLE, size, "#dismissNote", gesture, dismiss_holds)
        say(f"HOLDS {sum(r['verdict'] == 'HOLDS' for r in probe.rows)} of {len(probe.rows)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", choices=["chromium", "webkit"], default="chromium")
    parser.add_argument("--root", default=None)
    parser.add_argument("--tag", default="head")
    args = parser.parse_args()
    run(args.engine, args.root, args.tag)
