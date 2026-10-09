"""Shared helpers for the split-app security probes (security finder, read-only on the product).

Every browser context comes from rig.new_context (the clipboard recorder is on, `permissions` and
`bypass_csp` are refused). On top of that every context gets PROBE_JS: a second CG-7 guard that rejects
Clipboard.readText, read and write, an event recorder, a CSP violation recorder and a hostile-payload
tripwire (window.f and window.alert count themselves in window.pwned).
Nothing here touches the operating system clipboard. Results are written next to the scripts.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]  # .../examples/split
sys.path.insert(0, str(ROOT / "tests" / "browser"))

import rig  # noqa: E402
import seeds  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover
    pass

PROBE_JS = r"""
(() => {
  window.cg7Violations = 0;
  if (typeof Clipboard === "function") {
    for (const name of ["readText", "read", "write"]) {
      Clipboard.prototype[name] = function () {
        window.cg7Violations += 1;
        return Promise.reject(new DOMException("blocked by the probe", "NotAllowedError"));
      };
    }
  }
  window.pwned = 0;
  window.f = () => { window.pwned += 1; };
  window.alert = () => { window.pwned += 1; };
  window.csp = [];
  document.addEventListener("securitypolicyviolation", (e) => {
    window.csp.push(e.violatedDirective + " | " + e.blockedURI);
  }, true);
  window.evlog = [];
  const label = (node) => {
    const el = node && node.closest ? (node.closest("button, input, label, dialog, a, select, textarea") || node) : node;
    if (!el || !el.tagName) return String(el);
    const tag = el.tagName.toLowerCase();
    const aria = el.getAttribute("aria-label");
    const own = el.children.length === 0 ? (el.textContent || "").trim().slice(0, 24) : "";
    const cls = typeof el.className === "string" && el.className ? "." + el.className.trim().replace(/\s+/g, ".") : "";
    return tag + (el.id ? "#" + el.id : "") + cls + (aria ? " [" + aria + "]" : "") + (own ? " \"" + own + "\"" : "");
  };
  const pending = new WeakMap();
  for (const type of ["mousedown", "mouseup", "click", "dblclick", "contextmenu"]) {
    window.addEventListener(type, (e) => {
      const rec = { type, detail: e.detail, button: e.button, target: label(e.target), x: Math.round(e.clientX), y: Math.round(e.clientY), reached: false };
      pending.set(e, rec);
      window.evlog.push(rec);
      setTimeout(() => { rec.prevented = e.defaultPrevented; }, 0);
    }, true);
    window.addEventListener(type, (e) => { const rec = pending.get(e); if (rec) rec.reached = true; }, false);
  }
})();
"""

SNAP_JS = r"""() => {
  const label = (el) => !el ? null : (el.getAttribute("aria-label") || (el.labels && el.labels.length ? el.labels[0].textContent.trim() : "") || el.textContent.trim().slice(0, 30) || el.tagName.toLowerCase());
  const mode = document.querySelector("input[name=mode]:checked");
  const field = (sel) => { const n = document.querySelector(sel); return n ? n.value : null; };
  return {
    draft: localStorage.getItem("split.draft"),
    mode: mode ? mode.value : null,
    people: [...document.querySelectorAll("li.person input")].map((i) => i.value),
    items: [...document.querySelectorAll("li.item")].map((li) => ({
      name: li.querySelector("input").value,
      price: li.querySelectorAll("input")[1].value,
      who: [...li.querySelectorAll(".tap")].map((b) => b.textContent + ":" + b.getAttribute("aria-pressed")),
    })),
    subtotal: field("#subtotal"), service: field("#rate-service"), sst: field("#rate-sst"),
    dialogOpen: document.querySelector("dialog").open,
    note: !!document.querySelector(".note"),
    status: (document.querySelector("p.status") || { textContent: null }).textContent,
    focus: label(document.activeElement),
  };
}"""


class Cap:
    """Console, page-error, request, response and failed-request log of one page."""

    def __init__(self):
        self.console, self.errors, self.requests, self.responses, self.failed = [], [], [], [], []

    def attach(self, page):
        page.on("console", lambda m: self.console.append((m.type, m.text)))
        page.on("pageerror", lambda e: self.errors.append(str(e)))
        page.on("request", lambda r: self.requests.append((r.method, r.url)))
        page.on("response", lambda r: self.responses.append((r.status, r.url)))
        page.on("requestfailed", lambda r: self.failed.append((r.url, r.failure)))
        return self

    def problems(self, base):
        found = [f"console {k}: {t}" for k, t in self.console if k == "error" or "Content Security Policy" in t or "Refused" in t]
        found += [f"page error: {e}" for e in self.errors]
        for method, url in self.requests:
            own = url.startswith(base + "/")
            path = url[len(base):] if own else url
            ok = method == "GET" and own and (path == "/" or path == "/src/system.css" or path.startswith("/src/") or path == "/favicon.ico")
            if not ok:
                found.append(f"request: {method} {url}")
        return found


def open_page(browser, base, *, seed=None, viewport=(390, 844), touch=False, clipboard="recorder", extra_scripts=(), path="/", goto=True):
    options = {"viewport": {"width": viewport[0], "height": viewport[1]}, "device_scale_factor": 1, "color_scheme": "light"}
    if touch:
        options["has_touch"] = True
    if seed is not None:
        options["storage_state"] = rig.storage_state(base, seed)
    context = rig.new_context(browser, clipboard=clipboard, init_scripts=[PROBE_JS, *extra_scripts], **options)
    cap = Cap()
    page = context.new_page()
    cap.attach(page)
    if goto:
        page.goto(base + path)
    return context, page, cap


def settle(page, ms=120):
    page.evaluate("() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))")
    page.wait_for_timeout(ms)


def centre(locator):
    locator.scroll_into_view_if_needed()
    box = locator.bounding_box()
    return (box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)


def snap(page):
    return page.evaluate(SNAP_JS)


def run_probe(name, body):
    """Start a loopback server and headless Chromium, call body(browser, server, results), always stop both."""
    server = rig.StaticServer(ROOT).start()
    results = {"probe": name, "server_pid": server.process.pid, "port": server.port, "started": time.strftime("%Y-%m-%d %H:%M:%S"), "cases": []}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            results["chromium"] = browser.version
            try:
                body(browser, server, results)
            finally:
                browser.close()
    finally:
        server.stop()
    out = HERE / f"results-{name}.json"
    out.write_text(json.dumps(results, indent=1, ensure_ascii=True, default=str), encoding="utf-8")
    print(f"wrote {out.name}: {len(results['cases'])} cases")
    return results
