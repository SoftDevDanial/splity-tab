"""Re-check item 5 (live part): the shipped CSP stays live on the paths the changed files drive, with 0 violations and same-origin GETs only.

Flows (each through real gestures, `rig.new_context`, no bypass_csp, no permissions):
  F1 390x844 mouse, seed S1: double click Remove Chen, double click Remove of the last item, Add item and type a price, double click its Remove,
     double click New bill, click Start new bill, Add person and keyboard Enter on a Remove, New bill and Cancel, New bill and the backdrop,
     New bill and Esc.
  F2 360x640 touch, seed S2: double tap Remove Chen, double tap New bill, tap Cancel, tap New bill and tap Start new bill.
  F3 cold boot (no draft), one reload.
After each flow: window.csp (every securitypolicyviolation), console errors and CSP messages, page errors, every request (must be a GET for / or
a file under /src/), the localStorage keys, cookies. Then positive controls: an inline script and a same-origin fetch from inside the page must
be blocked and recorded, and rig.new_context must refuse bypass_csp and permissions.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rc  # noqa: E402
from rc import seeds, btn  # noqa: E402


def finish(page, cap, base, label, results):
    rc.settle(page, 150)
    csp = page.evaluate("() => window.csp")
    keys = page.evaluate("() => Object.keys(localStorage)")
    cookie = page.evaluate("() => document.cookie")
    urls = sorted({f"{m} {u[len(base):] if u.startswith(base) else u}" for m, u in cap.requests})
    statuses = sorted({s for s, _ in cap.responses})
    problems = cap.problems(base)
    row = {"case": label, "csp_violations": csp, "console": cap.console, "page_errors": cap.errors, "request_count": len(cap.requests),
           "distinct_requests": urls, "statuses": statuses, "failed": cap.failed, "localStorage_keys": keys, "cookie": cookie, "problems": problems,
           "pass": not csp and not cap.errors and not problems and not cap.failed and set(keys) <= {"split.draft"} and cookie == "" and set(statuses) <= {200, 304}}
    results["cases"].append(row)
    print(("PASS " if row["pass"] else "FAIL ") + label, {k: v for k, v in row.items() if k not in ("case", "pass")})


def body(browser, server, results):
    base = server.base

    ctx, page, cap = rc.open_page(browser, base, seed=seeds.S1, viewport=(390, 844))
    try:
        rc.settle(page)
        page.mouse.dblclick(*rc.centre(btn(page, "Remove Chen")))
        rc.settle(page, 100)
        page.mouse.dblclick(*rc.centre(btn(page, "Remove Satay, 10 sticks")))
        rc.settle(page, 100)
        btn(page, "Add item").click()
        page.keyboard.press("Tab")  # name field to price field
        page.keyboard.type("12.50")
        page.mouse.dblclick(*rc.centre(btn(page, "Remove Item 4")))
        rc.settle(page, 100)
        page.mouse.dblclick(*rc.centre(btn(page, "New bill")))
        rc.settle(page, 100)
        btn(page, "Start new bill").click()
        rc.settle(page, 100)
        btn(page, "Add person").click()
        page.locator("li.person .icon-btn").nth(2).focus()
        page.keyboard.press("Enter")
        rc.settle(page, 80)
        btn(page, "New bill").click()
        btn(page, "Cancel").click()
        rc.settle(page, 80)
        btn(page, "New bill").click()
        page.mouse.click(10, 10)
        rc.settle(page, 80)
        btn(page, "New bill").click()
        page.keyboard.press("Escape")
        finish(page, cap, base, "F1 390x844 mouse and keyboard flow over people.js, items.js, dialog.js", results)
    finally:
        ctx.close()

    ctx, page, cap = rc.open_page(browser, base, seed=seeds.S2, viewport=(360, 640), touch=True)
    try:
        rc.settle(page)
        x, y = rc.centre(btn(page, "Remove Chen"))
        page.touchscreen.tap(x, y)
        page.touchscreen.tap(x, y)
        rc.settle(page, 100)
        x, y = rc.centre(btn(page, "New bill"))
        page.touchscreen.tap(x, y)
        page.touchscreen.tap(x, y)
        rc.settle(page, 100)
        page.touchscreen.tap(*rc.centre(btn(page, "Cancel")))
        rc.settle(page, 100)
        page.touchscreen.tap(*rc.centre(btn(page, "New bill")))
        page.wait_for_timeout(500)
        page.touchscreen.tap(*rc.centre(btn(page, "Start new bill")))
        finish(page, cap, base, "F2 360x640 touch flow", results)
    finally:
        ctx.close()

    ctx, page, cap = rc.open_page(browser, base, viewport=(390, 844))
    try:
        rc.settle(page)
        page.reload()
        finish(page, cap, base, "F3 cold boot and reload (no draft)", results)
    finally:
        ctx.close()

    # positive controls: the policy is live and the recorder sees it
    ctx, page, cap = rc.open_page(browser, base, seed=seeds.S2, viewport=(390, 844))
    try:
        rc.settle(page)
        page.evaluate("""() => { const s = document.createElement('script'); s.textContent = 'window.__ran = 1'; document.body.append(s); }""")
        page.evaluate("""() => fetch('/').then(() => 'allowed', () => 'blocked').then((v) => { window.__fetch = v; })""")
        rc.settle(page, 200)
        ran = page.evaluate("() => window.__ran === 1")
        fetch = page.evaluate("() => window.__fetch")
        csp = page.evaluate("() => window.csp")
        row = {"case": "positive control: inline script and same-origin fetch from the page", "inline_script_ran": ran, "fetch_result": fetch,
               "violations": csp, "pass": (not ran) and fetch == "blocked" and len(csp) >= 2}
        results["cases"].append(row)
        print(("PASS " if row["pass"] else "FAIL ") + row["case"], {k: v for k, v in row.items() if k != "case"})
    finally:
        ctx.close()

    refused = {}
    for option, value in (("bypass_csp", True), ("permissions", ["clipboard-read"])):
        try:
            rc.rig.new_context(browser, **{option: value})
            refused[option] = False
        except ValueError as exc:
            refused[option] = str(exc)
    row = {"case": "rig.new_context refuses bypass_csp and permissions", "refused": refused, "pass": all(isinstance(v, str) for v in refused.values())}
    results["cases"].append(row)
    print(("PASS " if row["pass"] else "FAIL ") + row["case"], refused)


if __name__ == "__main__":
    rc.run_probe("r5-csp-live", body)
