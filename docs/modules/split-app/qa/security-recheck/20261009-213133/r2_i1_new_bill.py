"""Re-check item 2: I-1 as fixed (a double click or double tap on New bill).

For 360x640, 390x844 and 1280x800, a mouse double click and a touchscreen double tap on New bill must leave the dialog OPEN with
focus on Cancel. Straight after (no wait), one deliberate single click or tap on Cancel, on Start new bill or on the backdrop must
each work at once (dialog closed, focus back on New bill, Cancel and backdrop leave the draft alone, Start resets it): 18 rows.
Extra rows: a triple click, Esc after a double click, a click or tap on the backdrop over the New bill spot 600 ms later (the
only place a deliberate press and the guard could meet), and a control row on the tree before the fixes (the dialog shuts again).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rc  # noqa: E402
from rc import seeds, btn  # noqa: E402

VPS = [(360, 640), (390, 844), (1280, 800)]
FOLLOWS = ["cancel", "start", "backdrop"]


def state(page):
    return page.evaluate("""() => {
      const a = document.activeElement;
      const dialog = document.querySelector('dialog');
      return { open: dialog.open, focus: a ? (a.getAttribute('aria-label') || a.textContent.trim().slice(0, 30) || a.tagName.toLowerCase()) : null,
               draft: localStorage.getItem('split.draft') };
    }""")


def follow_point(page, follow):
    if follow == "cancel":
        return rc.centre(btn(page, "Cancel"))
    if follow == "start":
        return rc.centre(btn(page, "Start new bill"))
    return (10, 10)


def row_open(browser, base, vp, gest, follow=None, legacy=None, extra=None):
    touch = gest == "tap2"
    kwargs = dict(seed=seeds.S2, viewport=vp, touch=touch)
    ctx, page, cap = rc.open_legacy_page(browser, base, legacy, **kwargs) if legacy else rc.open_page(browser, base, **kwargs)
    try:
        rc.settle(page)
        x, y = rc.centre(btn(page, "New bill"))
        rc.reset_log(page)
        rc.gesture(page, gest, x, y)
        a = state(page)  # one evaluate, a few ms after the gesture
        out = {"viewport": f"{vp[0]}x{vp[1]}", "gesture": gest, "follow": follow, "opener_point": [round(x), round(y)],
               "after_gesture_open": a["open"], "after_gesture_focus": a["focus"],
               "gesture_clicks": rc.clicks(page, ("mousedown", "click"))}
        if follow:
            fx, fy = follow_point(page, follow)
            rc.reset_log(page)
            rc.gesture(page, "tap1" if touch else "single", fx, fy)
            rc.settle(page, 150)
            b = state(page)
            seed_bill = seeds.S2
            out.update({
                "follow_point": [round(fx), round(fy)], "follow_clicks": rc.clicks(page, ("mousedown", "click")),
                "after_follow_open": b["open"], "after_follow_focus": b["focus"],
                "draft_unchanged": b["draft"] == seed_bill, "draft_reset": ('"subtotalText":""' in (b["draft"] or "")) and b["draft"] != seed_bill,
            })
            want_reset = follow == "start"
            out["pass"] = (a["open"] and a["focus"] == "Cancel" and not b["open"] and b["focus"] == "New bill"
                           and (out["draft_reset"] if want_reset else out["draft_unchanged"])
                           and all(c.endswith(":reached") for c in out["follow_clicks"]) and not cap.problems(base))
        elif extra == "esc":
            page.keyboard.press("Escape")
            rc.settle(page, 100)
            b = state(page)
            out.update({"after_esc_open": b["open"], "after_esc_focus": b["focus"], "draft_unchanged": b["draft"] == seeds.S2})
            out["pass"] = a["open"] and a["focus"] == "Cancel" and not b["open"] and b["focus"] == "New bill" and out["draft_unchanged"]
        elif extra == "opener-spot-600ms":
            page.wait_for_timeout(600)
            rc.reset_log(page)
            rc.gesture(page, "tap1" if touch else "single", x, y)  # the backdrop is drawn over the New bill button now
            rc.settle(page, 150)
            b = state(page)
            out.update({"follow_clicks": rc.clicks(page, ("mousedown", "click")), "after_follow_open": b["open"], "after_follow_focus": b["focus"],
                        "draft_unchanged": b["draft"] == seeds.S2})
            out["pass"] = a["open"] and not b["open"] and b["focus"] == "New bill" and out["draft_unchanged"]
        else:
            out["pass"] = a["open"] and a["focus"] == "Cancel" and not cap.problems(base)
        out["problems"] = cap.problems(base)
        return out
    finally:
        ctx.close()


def body(browser, server, results):
    base = server.base

    def record(label, row, expect_pass=True):
        row["section"] = label
        results["cases"].append(row)
        ok = row["pass"] == expect_pass
        tag = "PASS" if ok else "FAIL"
        extra = {k: v for k, v in row.items() if k in ("after_follow_open", "after_follow_focus", "after_esc_open", "after_esc_focus", "draft_unchanged", "draft_reset")}
        print(f"{tag} {label:34} {row['viewport']:9} {row['gesture']:6} follow={row['follow']!s:9} opened={row['after_gesture_open']} focus={row['after_gesture_focus']!r} {extra} "
              f"follow_clicks={[c for c in row.get('follow_clicks', []) if c.startswith('click')]}")

    for vp in VPS:
        for gest in ("dbl", "tap2"):
            for follow in FOLLOWS:
                record("dbl/tap2 then deliberate click", row_open(browser, base, vp, gest, follow))
    record("triple click leaves it open", row_open(browser, base, VPS[1], "triple"))
    record("dbl then Esc", row_open(browser, base, VPS[1], "dbl", extra="esc"))
    record("double tap then Esc", row_open(browser, base, VPS[1], "tap2", extra="esc"))
    for vp, gest in ((VPS[0], "dbl"), (VPS[2], "dbl"), (VPS[0], "tap2")):
        record("backdrop over New bill at 600 ms", row_open(browser, base, vp, gest, extra="opener-spot-600ms"))
    legacy = rc.legacy_sources()
    # control: before the fix a double click shuts the dialog again, so "opened" is False and the row is expected to fail
    row = row_open(browser, base, VPS[1], "dbl", legacy=legacy)
    record("control: tree before the fixes", row, expect_pass=False)
    mine = [r for r in results["cases"] if not r["section"].startswith("control")]
    print(f"\nFIXED TREE: {sum(r['pass'] for r in mine)} of {len(mine)} rows pass; CONTROL row shows the old defect: {not results['cases'][-1]['pass']}")


if __name__ == "__main__":
    rc.run_probe("r2-i1-new-bill", body)
