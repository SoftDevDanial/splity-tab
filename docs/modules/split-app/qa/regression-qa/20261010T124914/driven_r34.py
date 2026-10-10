"""Regression QA, driven check D4 for R34 "Focus after adding or removing" (qa.md rows b to f, on the S1 seed).

The suite's focus tests start from a three-person bill with no items (test_R34_focus_moves_to_the_name_field_at_the_removed_position),
or from an S1 bill built by gestures (test_R34_focus_after_adding_or_removing_an_item). qa.md states these rows on the S1 seed,
so each row is driven here from the S1 seed with one real click, and the focused field and its value are read.
Writes driven-r34.json and driven-r34-run.txt here.
"""
import datetime
import json
import sys
from pathlib import Path

EVID = Path(__file__).resolve().parent
sys.path.insert(0, str(EVID))

import harness_common as hc  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

LOG = hc.Log(EVID / "driven-r34-run.txt")
CHECKS = hc.Checks()
GROUP = "D4 R34 focus after a click, S1 seed"
# (qa.md row, the control clicked, the field focus must reach, the value that field must hold)
ROWS = [
    ("row b", "Remove Ben", "Person 2 name", "Chen"),
    ("row c", "Remove Chen", "Person 2 name", "Ben"),
    ("row d", "Add item", "Item 5 name", ""),
    ("row e", "Remove Char kuey teow", "Item 2 name", "Mee goreng mamak"),
    ("row f", "Remove Satay, 10 sticks", "Item 3 name", "Mee goreng mamak"),
]


def main():
    started = datetime.datetime.now().isoformat(timespec="seconds")
    server = hc.start_server(LOG)
    record = {"started": started, "server_port": server.port, "server_pid": server.process.pid}
    try:
        base = server.base
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            record["chromium"] = browser.version
            record["chromium_pids_while_open"] = hc.chromium_pids()
            try:
                for row, control, field_label, value in ROWS:
                    session = hc.Session(browser, base, seed=hc.seeds.S1)
                    try:
                        page = session.page
                        page.goto(base + "/")
                        hc.settle(page)
                        hc.button(page, control).click()
                        hc.settle(page)
                        focused = {"label": hc.active_label(page),
                                   "value": page.evaluate("document.activeElement.value === undefined ? null : document.activeElement.value")}
                        CHECKS.expect(GROUP, f"{row}: {control}", "focus on", field_label, focused["label"])
                        CHECKS.expect(GROUP, f"{row}: {control}", "the focused field holds", value, focused["value"])
                        CHECKS.expect(GROUP, f"{row}: {control}", "problems", [], session.problems())
                    finally:
                        session.close()
            finally:
                browser.close()
            record["chromium_pids_after_close"] = hc.chromium_pids()
    finally:
        server.stop()
        record["server_port_free_after_stop"] = hc.rig.port_is_free(server.port)
        record["ended"] = datetime.datetime.now().isoformat(timespec="seconds")
        failed = CHECKS.failed()
        record["result"] = "PASS" if not failed else "FAIL"
        record["counts"] = {"pass": sum(r["result"] == "PASS" for r in CHECKS.rows), "fail": len(failed)}
        record["checks"] = CHECKS.rows
        (EVID / "driven-r34.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        LOG.say(f"driven R34 rows {record['result']} {record['counts']}")
        LOG.save()
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
