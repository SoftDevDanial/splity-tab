"""Throwaway helpers for the code-review probes. Serves the scratch copy, never the repo.
CG-7: every context gets the recorder (or reject/missing) from the project's own rig plus a guard that
rejects every clipboard read. No permission is granted.
Run with cwd = the project root so that the relative evidence path lands in
docs/modules/split-app/qa/code-review/<stamp>/.
(Record copy. The live copies ran from the session scratchpad and import `rig`, `seeds` and `support`
from the scratch copy of the project, `scratchpad/base/tests/browser/`.)
"""
import json
import sys
from pathlib import Path

SCRATCH = Path("{temp}/claude/{project-id}/0fc4b490-9bf0-46ec-8ac8-08b33bc21485/scratchpad")
BASE = SCRATCH / "base"
EVIDENCE = Path("docs/modules/split-app/qa/code-review/20261009-181036")


def use_tree(tree):
    """Make `tree` (a copy of the project) the one that rig, seeds and support see."""
    sys.path.insert(0, str(Path(tree) / "tests" / "browser"))
    import rig, seeds, support  # noqa: E402
    return rig, seeds, support


GUARD = """(() => { if (typeof Clipboard === 'function') {
  for (const name of ['readText', 'read', 'write']) {
    Clipboard.prototype[name] = function () { return Promise.reject(new DOMException('blocked by the review guard', 'NotAllowedError')); };
  } } })();"""


class Run:
    def __init__(self, tree=BASE):
        self.rig, self.seeds, self.support = use_tree(tree)
        self.tree = Path(tree)
        self.results = []
        self.server = None
        self.playwright = None
        self.browser = None

    def start(self):
        from playwright.sync_api import sync_playwright
        self.server = self.rig.StaticServer(self.rig.ROOT, say=lambda line: print(line, flush=True)).start()
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        return self

    def stop(self):
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        finally:
            if self.server:
                self.server.stop()

    def session(self, seed=None, viewport=(390, 844), clipboard="recorder", touch=False, init_scripts=()):
        options = {"viewport": {"width": viewport[0], "height": viewport[1]}, "device_scale_factor": 1, "color_scheme": "light"}
        if touch:
            options["has_touch"] = True
        if seed is not None:
            options["storage_state"] = self.rig.storage_state(self.server.base, seed)
        context = self.rig.new_context(self.browser, clipboard=clipboard, init_scripts=[GUARD, *init_scripts], **options)
        s = Sess(context, self.server.base)
        return s

    def check(self, name, ok, detail=""):
        self.results.append({"check": name, "ok": bool(ok), "detail": detail})
        print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""), flush=True)

    def note(self, name, value):
        self.results.append({"note": name, "value": value})
        print("NOTE " + name + f"  {value}", flush=True)

    def save(self, filename):
        path = EVIDENCE / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("wrote", path, "exists", path.exists(), flush=True)


class Sess:
    def __init__(self, context, base):
        self.context, self.base = context, base
        self.console, self.errors, self.requests = [], [], []
        context.on("page", self._watch)
        self.page = context.new_page()

    def _watch(self, page):
        page.on("console", lambda m: self.console.append((m.type, m.text)))
        page.on("pageerror", lambda e: self.errors.append(str(e)))
        page.on("request", lambda r: self.requests.append((r.method, r.url)))

    def open(self, path="/"):
        self.page.goto(self.base + path)
        return self.page

    def stored(self):
        text = self.page.evaluate("localStorage.getItem('split.draft')")
        return text

    def close(self):
        self.context.close()
