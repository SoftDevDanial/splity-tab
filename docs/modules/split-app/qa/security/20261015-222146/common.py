"""Shared helpers of the security finder's browser probes (step 5 of v1.1.0). Read-only on the product.

Every browser comes from rig.launch and every context from rig.new_context, so each context gets the clipboard
stand-in (recorder.js) before the page loads, plus the CSP listener and a guard that refuses clipboard reads. No
permission, no bypass_csp. Headless only. Each probe serves the project root (or `root`, used only by B4's control on
the v1.0.0 tree in the session scratchpad) with rig.StaticServer and stops it.
[Changed in this run after B1 to B3 ran: Probe gained the optional `root`. B1 to B3 pass none, so they serve the
project root exactly as before.]
"""
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT / "tests" / "browser"))
import rig  # noqa: E402

LISTENER = (ROOT / "tests" / "browser" / "csp" / "listener.js").read_text(encoding="utf-8")
# A second line of defence for the human's clipboard: any read or rich write rejects, and is counted.
CLIPBOARD_GUARD = """(() => {
  window.testClipboardRefused = 0;
  if (typeof Clipboard === "function") {
    for (const name of ["readText", "read", "write"]) {
      Clipboard.prototype[name] = function () { window.testClipboardRefused += 1; return Promise.reject(new Error("refused by probe")); };
    }
  }
})();"""
STAND_IN_CHECK = """() => {
  const write = navigator.clipboard && navigator.clipboard.writeText;
  const native = typeof write === "function" && Function.prototype.toString.call(write).includes("[native code]");
  return { writes: window.testClipboardWrites, hasClipboard: typeof Clipboard === "function", native };
}"""
ACTION_TIMEOUT_MS = 15000


def say(*parts):
    print(*parts, flush=True)


class Probe:
    """One engine, one server, a list of result rows written to <name>-<engine>.json beside the script."""

    def __init__(self, name, engine, root=None):
        self.name, self.engine = name, engine
        self.rows, self.facts = [], {"engine": engine, "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "root": str(root or ROOT)}
        self.server = rig.StaticServer(root=root or ROOT, say=lambda line: self.log(line))
        self.lines = []

    def log(self, line):
        self.lines.append(line)
        say(line)

    def __enter__(self):
        self.server.start()
        self.facts.update(server_pid=self.server.process.pid, port=self.server.port)
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self.browser = rig.launch(self._pw, self.engine)
        self.facts["browser_version"] = self.browser.version
        return self

    def __exit__(self, *exc):
        try:
            self.browser.close()
            self._pw.stop()
        finally:
            self.server.stop()
            self.facts["ended"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            self.facts["server_log"] = self.lines
            out = HERE / f"{self.name}-{self.engine}.json"
            out.write_text(json.dumps({"facts": self.facts, "rows": self.rows}, indent=1, ensure_ascii=True), encoding="utf-8")
            say(f"wrote {out.name}, {len(self.rows)} rows")
        return False

    @property
    def base(self):
        return self.server.base

    def context(self, extra_scripts=(), **options):
        options.setdefault("viewport", {"width": 390, "height": 844})
        options.setdefault("device_scale_factor", 1)
        options.setdefault("color_scheme", "dark")
        options.setdefault("reduced_motion", "reduce")
        ctx = rig.new_context(self.browser, clipboard="recorder", init_scripts=[LISTENER, CLIPBOARD_GUARD, *extra_scripts], **options)
        ctx.set_default_timeout(ACTION_TIMEOUT_MS)
        return ctx

    def page(self, ctx):
        page = ctx.new_page()
        rec = {"console": [], "page_errors": [], "requests": [], "dialogs": []}
        page.on("console", lambda m: rec["console"].append(f"{m.type}: {m.text[:300]}") if m.type in ("error", "warning") else None)
        page.on("pageerror", lambda e: rec["page_errors"].append(str(e)[:300]))
        page.on("request", lambda r: rec["requests"].append([r.method, r.url, r.resource_type]))
        page.on("dialog", lambda d: (rec["dialogs"].append(d.message), d.dismiss()))
        page.on("popup", lambda p: rec["dialogs"].append("popup " + p.url))
        return page, rec

    def seed(self, page, rec, text, via="/src/system.css"):
        """Writes `text` under split.draft from a same-origin document that does not run the app, then forgets those requests.
        B1 to B3 used /src/icon.svg, which the v1.0.0 tree does not have, so the default is now the stylesheet both trees hold."""
        page.goto(self.base + via)
        ok = page.evaluate("""(t) => { try { localStorage.setItem("split.draft", t); return localStorage.getItem("split.draft") === t; }
          catch (e) { return "setItem threw " + e.name; } }""", text)
        rec["requests"].clear()
        return ok

    def open_app(self, page, timeout_ms=ACTION_TIMEOUT_MS):
        t0 = time.perf_counter()
        page.goto(self.base + "/", timeout=timeout_ms)
        page.wait_for_function("() => document.querySelector('#rbody') && document.querySelector('#rbody').children.length > 0", timeout=timeout_ms)
        return round((time.perf_counter() - t0) * 1000)

    def stand_in(self, page):
        found = page.evaluate(STAND_IN_CHECK)
        if found["writes"] != 0 or found["native"]:
            raise RuntimeError(f"clipboard stand-in missing: {found}")
        return found

    def off_rule_requests(self, rec):
        bad = []
        origin = urlsplit(self.base)
        for method, url, kind in rec["requests"]:
            parts = urlsplit(url)
            same = (parts.scheme, parts.netloc) == (origin.scheme, origin.netloc)
            allowed = same and method == "GET" and (parts.path == "/" or parts.path.startswith("/src/") or parts.path == "/favicon.ico")
            if not allowed:
                bad.append([method, url, kind])
        return bad

    @staticmethod
    def violations(page):
        return page.evaluate("() => window.testCspViolations || []")

    @staticmethod
    def stored(page):
        return page.evaluate("() => localStorage.getItem('split.draft')")
