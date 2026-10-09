"""R38 (CSP live), R39 (nothing leaves the device) and the storage footprint.

Part A: six real flows with the shipped policy live (no bypass_csp). For each: every console message, every
securitypolicyviolation event, every request (method, url), every response status, WebSocket, worker, popup and
dialog events, and the footprint afterwards (localStorage keys, sessionStorage, cookies, IndexedDB, Cache Storage,
service workers, and any link, form, frame or src in the body).
Part B: positive controls. Things the page must NOT be able to do are tried from inside the page (nothing real is
requested: the targets are 127.0.0.1:9 or the page's own origin, and the policy blocks the request before it is made).
Each must raise a securitypolicyviolation or throw. A negative control proves the element count detects an injected node.
Note on eval: Playwright's page.evaluate runs through the inspector, which lifts the eval block of the page while it
runs (CDP allowUnsafeEvalBlockedByCSP defaults to true), so a first version of this probe wrongly saw `new Function`
succeed. The eval controls now run inside a timer task of the page itself, where the policy applies.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import seeds  # noqa: E402

FOOTPRINT_JS = """async () => ({
  localStorageKeys: Object.keys(localStorage),
  sessionStorageKeys: Object.keys(sessionStorage),
  cookie: document.cookie,
  indexedDB: indexedDB.databases ? (await indexedDB.databases()).map((d) => d.name) : 'n/a',
  caches: 'caches' in window ? await caches.keys() : 'n/a',
  serviceWorkers: navigator.serviceWorker ? (await navigator.serviceWorker.getRegistrations()).length : 'n/a',
  resources: performance.getEntriesByType('resource').map((r) => new URL(r.name).pathname),
  bodyLinksFormsFrames: document.body.querySelectorAll('a[href], form, iframe, embed, object, [src], link[href]').length,
})"""


def watch_extras(page, extras):
    page.on("websocket", lambda ws: extras.append(("websocket", ws.url)))
    page.on("worker", lambda w: extras.append(("worker", w.url)))
    page.on("popup", lambda p: extras.append(("popup", p.url)))
    page.on("download", lambda d: extras.append(("download", d.url)))
    page.on("dialog", lambda d: (extras.append(("dialog", d.message)), d.dismiss()))


def flow_cold(page):
    page.locator("#subtotal").click()
    page.keyboard.type("123.45")
    page.get_by_role("button", name="Add person").click()
    page.keyboard.type("Dina")
    page.get_by_role("button", name="Copy summary").click()
    page.locator("label[for=mode-item]").click()
    page.get_by_role("button", name="Add item").click()
    page.keyboard.type("Tea")
    page.keyboard.press("Tab")
    page.keyboard.type("abc")
    page.keyboard.press("Tab")


def flow_dialog(page):
    page.get_by_role("button", name="New bill").click()
    page.get_by_role("button", name="Cancel", exact=True).click()
    page.get_by_role("button", name="New bill").click()
    page.mouse.click(10, 10)
    page.get_by_role("button", name="New bill").click()
    page.get_by_role("button", name="Start new bill").click()


def flow_copy(page):
    page.get_by_role("button", name="Copy summary").click()


def flow_note(page):
    page.get_by_role("button", name="Dismiss note").click()


HOSTILE = seeds.changed(seeds.S1, lambda d: (d["bill"]["people"][0].update(name="<svg onload=f()>"),
                                             d["bill"]["items"][0].update(name="<img src=x onerror=alert(1)>")))
FLOWS = [
    ("A1 cold boot, type, add person, copy, By item, price error", dict(), flow_cold),
    ("A2 S1 restored, dialog: Cancel, backdrop, Start new bill", dict(seed=seeds.S1), flow_dialog),
    ("A3 copy refused by the browser (reject.js)", dict(seed=seeds.S2, clipboard="reject"), flow_copy),
    ("A4 clipboard API missing (missing.js)", dict(seed=seeds.S2, clipboard="missing"), flow_copy),
    ("A5 unreadable draft, note dismissed", dict(seed=seeds.UNREADABLE["B1"]), flow_note),
    ("A6 hostile names restored, copy", dict(seed=HOSTILE), flow_copy),
]


def part_a(browser, base, results):
    for name, options, flow in FLOWS:
        ctx, page, cap = common.open_page(browser, base, viewport=(390, 844), **options)
        extras = []
        watch_extras(page, extras)
        try:
            common.settle(page, 100)
            flow(page)
            common.settle(page, 150)
            footprint = page.evaluate(FOOTPRINT_JS)
            csp = page.evaluate("window.csp")
            pwned = page.evaluate("window.pwned")
            bad_console = [(k, t) for k, t in cap.console if k in ("error", "warning") or "Content Security Policy" in t or "Refused" in t]
            requests = sorted({(m, u.replace(base, "")) for m, u in cap.requests})
            statuses = sorted({(s, u.replace(base, "")) for s, u in cap.responses})
            ok = (not csp and not bad_console and not cap.errors and not extras and pwned == 0 and not cap.problems(base)
                  and footprint["sessionStorageKeys"] == [] and footprint["cookie"] == "" and footprint["indexedDB"] == []
                  and footprint["caches"] == [] and footprint["serviceWorkers"] == 0
                  and set(footprint["localStorageKeys"]) <= {"split.draft"} and footprint["bodyLinksFormsFrames"] == 0)
            results["cases"].append({"case": name, "ok": ok, "csp_violations": csp, "console_problem_messages": bad_console, "page_errors": cap.errors,
                                     "extras": extras, "requests": requests, "responses": statuses, "footprint": footprint, "pwned": pwned,
                                     "all_console": cap.console})
            print(f"{'PASS' if ok else 'FAIL'} {name}")
            print("     distinct requests:", len(requests), "all GET:", all(m == "GET" for m, _ in requests), "all 200:", all(s == 200 for s, _ in statuses),
                  "paths outside / and /src/:", [u for _, u in requests if u != "/" and not u.startswith("/src/")])
            print("     csp:", csp, "console problems:", bad_console, "extras:", extras, "pwned:", pwned)
            print("     footprint:", {k: v for k, v in footprint.items() if k != "resources"})
        finally:
            ctx.close()


def in_timer(body):
    """A script that runs `body` (a statement list that sets `out`) in a timer task of the page, outside the inspector's eval allowance."""
    return "() => new Promise((resolve) => { setTimeout(() => { let out; try { " + body + " } catch (e) { out = 'blocked:' + e.name; } resolve(out); }, 0); })"


CONTROLS = {
    "new Function (eval) is blocked": (in_timer("out = 'ran:' + new Function('return 1')();"), "script-src (no unsafe-eval)"),
    "eval() is blocked": (in_timer("out = 'ran:' + eval('1');"), "script-src (no unsafe-eval)"),
    "setTimeout with a string is blocked": (in_timer("setTimeout('window.pwned = 77', 0); out = 'queued';"), "script-src (no unsafe-eval)"),
    "inline script element is blocked": ("""() => { const s = document.createElement('script'); s.textContent = 'window.pwned = 99'; document.head.append(s); return 'pwned=' + window.pwned; }""", "script-src"),
    "inline event handler on an inserted image is blocked": ("""() => { document.body.insertAdjacentHTML('beforeend', '<img src="http://127.0.0.1:9/x.png" onerror="f()">'); return 'inserted'; }""", "img-src and script-src-attr"),
    "cross-origin image is blocked": ("""() => { const i = new Image(); i.src = 'http://127.0.0.1:9/x.png'; return 'set'; }""", "img-src"),
    "same-origin fetch is blocked (connect-src none)": ("""async () => { try { await fetch('/src/main.js'); return 'fetched'; } catch (e) { return 'blocked:' + e.name; } }""", "connect-src"),
    "cross-origin fetch is blocked": ("""async () => { try { await fetch('http://127.0.0.1:9/'); return 'fetched'; } catch (e) { return 'blocked:' + e.name; } }""", "connect-src"),
    "XMLHttpRequest is blocked": ("""() => { try { const x = new XMLHttpRequest(); x.open('GET', '/'); x.send(); return 'sent'; } catch (e) { return 'blocked:' + e.name; } }""", "connect-src"),
    "WebSocket is blocked": ("""() => { try { new WebSocket('ws://127.0.0.1:9/'); return 'opened'; } catch (e) { return 'blocked:' + e.name; } }""", "connect-src"),
    "EventSource is blocked": ("""() => { try { new EventSource('/'); return 'opened'; } catch (e) { return 'blocked:' + e.name; } }""", "connect-src"),
    "sendBeacon is blocked": ("""() => { try { return 'queued:' + navigator.sendBeacon('/', 'a'); } catch (e) { return 'blocked:' + e.name; } }""", "connect-src"),
    "iframe is blocked": ("""() => { const f = document.createElement('iframe'); f.src = location.origin + '/'; document.body.append(f); return 'appended'; }""", "frame-src or child-src"),
    "form submission is blocked": ("""() => { const f = document.createElement('form'); f.action = 'http://127.0.0.1:9/'; f.method = 'post'; document.body.append(f); f.requestSubmit(); return 'submitted'; }""", "form-action"),
    "base element is blocked": ("""() => { const b = document.createElement('base'); b.href = 'http://127.0.0.1:9/'; document.head.append(b); return 'base=' + document.baseURI; }""", "base-uri"),
    "style element is blocked": ("""() => { const s = document.createElement('style'); s.textContent = 'body{display:none}'; document.head.append(s); return 'display=' + getComputedStyle(document.body).display; }""", "style-src"),
    "style attribute (setAttribute) is blocked": ("""() => { document.body.setAttribute('style', 'display:none'); return 'display=' + getComputedStyle(document.body).display; }""", "style-src"),
    "cross-origin stylesheet link is blocked": ("""() => { const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = 'http://127.0.0.1:9/x.css'; document.head.append(l); return 'appended'; }""", "style-src"),
    "cross-origin script element is blocked": ("""() => { const s = document.createElement('script'); s.src = 'http://127.0.0.1:9/x.js'; document.head.append(s); return 'appended'; }""", "script-src"),
    "dynamic import of a cross-origin module is blocked": ("""async () => { try { await import('http://127.0.0.1:9/x.js'); return 'imported'; } catch (e) { return 'blocked:' + e.name; } }""", "script-src"),
}


def part_b(browser, base, results):
    ctx, page, cap = common.open_page(browser, base, seed=seeds.S2, viewport=(390, 844))
    extras = []
    watch_extras(page, extras)
    try:
        for name, (script, directive) in CONTROLS.items():
            page.goto(base + "/")  # a fresh document for every control, so one cannot leave anything behind for the next
            common.settle(page, 60)
            outcome = page.evaluate(script)
            page.wait_for_timeout(200)
            csp = page.evaluate("window.csp")
            pwned = page.evaluate("window.pwned")
            held = (bool(csp) or str(outcome).startswith("blocked")) and pwned == 0
            results["cases"].append({"case": f"B {name}", "ok": held, "outcome": outcome, "csp": csp, "pwned": pwned, "expected_directive": directive})
            print(f"{'PASS' if held else 'FAIL'} B {name:54} outcome {outcome!r:24} pwned {pwned} violations {csp}")
        # negative control: an injected node must change the element count (the signature check has teeth)
        page.goto(base + "/")
        common.settle(page, 60)
        before = page.evaluate("() => document.querySelectorAll('*').length")
        page.evaluate("() => { document.body.insertAdjacentHTML('beforeend', '<b></b>'); }")
        after = page.evaluate("() => document.querySelectorAll('*').length")
        row = {"case": "B negative control: a node that reached the DOM changes the element count", "elements_before": before, "elements_after": after,
               "ok": after == before + 1}
        results["cases"].append(row)
        print(f"{'PASS' if row['ok'] else 'FAIL'} B negative control: elements {before} -> {after}")
        for forbidden in ({"bypass_csp": True}, {"permissions": ["clipboard-read"]}):
            try:
                common.rig.new_context(browser, **forbidden)
                refused = False
            except ValueError:
                refused = True
            results["cases"].append({"case": f"B the rig refuses {list(forbidden)[0]}", "ok": refused})
            print(f"{'PASS' if refused else 'FAIL'} B the rig refuses {list(forbidden)[0]}")
        external = sorted({u for _, u in cap.requests if not u.startswith(base)})
        results["cases"].append({"case": "B requests outside the page's own origin during part B (all blocked before they were made, see violations)",
                                 "external": external, "extras": extras})
        print("     requests outside the page's origin during part B:", external, "extras:", extras)
    finally:
        ctx.close()


def body(browser, server, results):
    part_a(browser, server.base, results)
    part_b(browser, server.base, results)


if __name__ == "__main__":
    common.run_probe("p5-csp-network", body)
