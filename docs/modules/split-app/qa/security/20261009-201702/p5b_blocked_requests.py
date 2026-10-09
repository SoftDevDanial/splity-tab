"""R39 follow-up: the CSP controls of p5 again, this time listing the requests the browser reports as failed.

A request that the policy stops is reported by Chromium through Playwright as failed with the reason `csp`
(the DevTools blockedReason). This script runs each control of p5_csp_network once and prints, for every request to
a host other than the page's own origin, and for every request to the page's own origin beyond the app's own files,
whether it failed with `csp`. A request to 127.0.0.1:9 that was NOT blocked would fail with some other reason
(connection refused) or none. The eval controls are in p5 and need no request.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import seeds  # noqa: E402
from p5_csp_network import CONTROLS  # noqa: E402


def body(browser, server, results):
    base = server.base
    ctx, page, cap = common.open_page(browser, base, seed=seeds.S2, viewport=(390, 844))
    try:
        for name, (script, directive) in CONTROLS.items():
            if "eval" in name or "Function" in name or "setTimeout" in name:
                continue
            page.goto(base + "/")
            common.settle(page, 60)
            cap.requests.clear()
            cap.failed.clear()
            page.evaluate(script)
            page.wait_for_timeout(250)
            outside = sorted({u for _, u in cap.requests if not u.startswith(base)})
            own = sorted({u.replace(base, "") for m, u in cap.requests if u.startswith(base) and u.replace(base, "") not in ("/", "/favicon.ico") and not u.startswith(base + "/src/")})
            failed = {u.replace(base, ""): f for u, f in cap.failed}
            seen = outside + [base + u for u in own]
            reached_network = [u for u in seen if (failed.get(u.replace(base, "")) or "") != "csp"]
            row = {"case": name, "outside_requests": outside, "own_origin_requests_beyond_the_app_files": own, "failures": failed,
                   "requests_not_stopped_by_csp": reached_network, "ok": not reached_network}
            results["cases"].append(row)
            print(f"{'PASS' if row['ok'] else 'FAIL'} {name:52} requests seen {seen or '-'} failures {failed or '-'}")
    finally:
        ctx.close()


if __name__ == "__main__":
    common.run_probe("p5b-blocked-requests", body)
