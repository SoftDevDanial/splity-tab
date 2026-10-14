"""Fixtures for the functional suite: a loopback static server, one headless browser, and a capturing session.

The browser is the engine of --engine (chromium, the default, or webkit), launched by rig.launch (R58). A test
marked chromium_only(reason=...) is a skip with that reason in any other engine, and every skip is listed and
counted, never reported as a pass.
Every scenario gets a new context (rig.new_context, with the clipboard recorder unless it names another
script), records console messages, page errors and requests, and fails at teardown on a console error, a CSP
violation, a page error or a request that is not a same-origin GET for the page's own files (qa.md,
"Console and network"). A failed scenario leaves a screenshot in the evidence folder, <stamp>-<engine>.
Set SPLIT_EVIDENCE=1 to also write pytest.txt, junit.xml and skips.txt there, each naming the engine and the
browser version.
"""
import datetime
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

import rig

EVIDENCE_ROOT = rig.ROOT / "docs" / "modules" / "split-app" / "qa" / "functional"
CSP_LISTENER = (Path(__file__).resolve().parent / "csp" / "listener.js").read_text(encoding="utf-8")
_evidence = {"dir": None, "engine": rig.DEFAULT_ENGINE, "browser_version": None, "lines": [], "skips": []}


def evidence_dir():
    """The run's evidence folder, <stamp>-<engine> (R58), made on first use (a failure screenshot, or SPLIT_EVIDENCE=1)."""
    if _evidence["dir"] is None:
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        _evidence["dir"] = EVIDENCE_ROOT / f"{stamp}-{_evidence['engine']}"
        _evidence["dir"].mkdir(parents=True, exist_ok=True)
    return _evidence["dir"]


def pytest_addoption(parser):
    parser.addoption("--engine", choices=list(rig.ENGINES), default=rig.DEFAULT_ENGINE,
                     help="browser engine of this run (R58)")


def pytest_configure(config):
    _evidence["engine"] = config.getoption("engine")
    config.addinivalue_line("markers", "chromium_only(reason): runs in Chromium only, and is a counted skip "
                                       "with that reason in any other engine (R58)")
    if os.environ.get("SPLIT_EVIDENCE"):
        config.option.xmlpath = str(evidence_dir() / "junit.xml")


def pytest_collection_modifyitems(config, items):
    """Turns chromium_only into a skip with its own reason outside Chromium. A mark without a reason stops the run."""
    for item in items:
        marker = item.get_closest_marker("chromium_only")
        if marker is None:
            continue
        reason = marker.kwargs.get("reason")
        if not reason:
            raise pytest.UsageError(f"{item.nodeid}: chromium_only needs reason=...")
        if config.getoption("engine") != "chromium":
            item.add_marker(pytest.mark.skip(reason=reason))


def skip_reason(report):
    """The reason of a skipped or xfailed report, as junit.xml counts both as skipped."""
    if hasattr(report, "wasxfail"):
        return f"xfail {report.wasxfail}".strip()
    longrepr = report.longrepr
    return longrepr[2].removeprefix("Skipped: ") if isinstance(longrepr, tuple) else str(longrepr)


def pytest_runtest_logreport(report):
    if report.skipped:
        _evidence["skips"].append(f"{report.nodeid} | {skip_reason(report)}")
    if os.environ.get("SPLIT_EVIDENCE") and (report.when == "call" or report.failed or report.skipped):
        _evidence["lines"].append(f"{report.outcome.upper():8} {report.when:8} {report.nodeid} ({report.duration:.2f}s)")


def run_header():
    return f"engine {_evidence['engine']}, browser version {_evidence['browser_version']}"


def pytest_terminal_summary(terminalreporter):
    terminalreporter.write_line(f"{run_header()}, skipped {len(_evidence['skips'])}")
    for line in _evidence["skips"]:
        terminalreporter.write_line(f"  skipped: {line}")


def pytest_sessionfinish(session, exitstatus):
    if os.environ.get("SPLIT_EVIDENCE"):
        folder = evidence_dir()
        (folder / "pytest.txt").write_text("\n".join([run_header(), *_evidence["lines"]]) + f"\nexit status {exitstatus}\n",
                                           encoding="utf-8")
        (folder / "skips.txt").write_text("\n".join([run_header(), *_evidence["skips"]]) + f"\ncount {len(_evidence['skips'])}\n",
                                          encoding="utf-8")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    setattr(item, "rep_" + call.when, outcome.get_result())


class Session:
    """One browser context with its console, page-error and request logs."""

    def __init__(self, context, base, prefix=""):
        self.context, self.base, self.prefix = context, base, prefix
        self.console, self.page_errors, self.requests = [], [], []
        context.on("page", self._watch)
        self.page = context.new_page()

    def _watch(self, page):
        page.on("console", lambda message: self.console.append((message.type, message.text)))
        page.on("pageerror", lambda error: self.page_errors.append(str(error)))
        page.on("request", lambda request: self.requests.append((request.method, request.url)))

    def new_page(self):
        return self.context.new_page()

    def open(self, path="/", page=None):
        page = page or self.page
        page.goto(self.base + path)
        return page

    def request_is_allowed(self, method, url):
        parts = urlsplit(url)
        own = f"{parts.scheme}://{parts.netloc}" == self.base
        path = parts.path
        files = {self.prefix + "/", self.prefix + "/src/system.css", "/favicon.ico"}
        return method == "GET" and own and (path in files or path.startswith(self.prefix + "/src/"))

    def csp_violations(self):
        """What csp/listener.js recorded in every page still open (R38). A page that is closing reports nothing."""
        found = []
        for page in self.context.pages:
            try:
                found += page.evaluate("() => window.testCspViolations || []")
            except PlaywrightError:
                pass
        return found

    def problems(self):
        found = [f"console {kind}: {text}" for kind, text in self.console
                 if kind == "error" or "Content Security Policy" in text]
        found += [f"page error: {error}" for error in self.page_errors]
        found += [f"csp violation: {violation}" for violation in self.csp_violations()]
        found += [f"request: {method} {url}" for method, url in self.requests
                  if not self.request_is_allowed(method, url)]
        return found


@pytest.fixture(scope="session")
def server(request):
    reporter = request.config.pluginmanager.get_plugin("terminalreporter")
    running = rig.StaticServer(rig.ROOT, say=reporter.write_line if reporter else print).start()
    yield running
    running.stop()


@pytest.fixture(scope="session")
def engine(request):
    """The engine of this run, from --engine (R58). A test that asserts each engine's own result asks for it."""
    return request.config.getoption("engine")


@pytest.fixture(scope="session")
def browser(engine):
    with sync_playwright() as playwright:
        launched = rig.launch(playwright, engine)
        _evidence["browser_version"] = launched.version
        yield launched
        launched.close()


@pytest.fixture
def open_app(server, browser, request):
    """open_app(seed=None, clipboard="recorder", viewport=(390, 844), reduced_motion=None, init_scripts=(),
    path="/", goto=True, base_server=None, prefix="", allow_problems=False, touch=False, color_scheme="light") -> Session

    Every context also gets csp/listener.js, so a policy violation fails the scenario in either engine (R38)."""
    sessions = []

    def factory(seed=None, clipboard="recorder", viewport=(390, 844), reduced_motion=None, init_scripts=(),
                path="/", goto=True, base_server=None, prefix="", allow_problems=False, touch=False, color_scheme="light"):
        target = base_server or server
        options = {"viewport": {"width": viewport[0], "height": viewport[1]},
                   "device_scale_factor": 1, "color_scheme": color_scheme}
        if reduced_motion:
            options["reduced_motion"] = reduced_motion
        if touch:  # page.touchscreen.tap needs a context that has touch (RD-3)
            options["has_touch"] = True
        if seed is not None:
            options["storage_state"] = rig.storage_state(target.base, seed)
        context = rig.new_context(browser, clipboard=clipboard, init_scripts=(CSP_LISTENER, *init_scripts), **options)
        session = Session(context, target.base, prefix)
        session.allow_problems = allow_problems
        sessions.append(session)
        if goto:
            session.open(path)
        return session

    yield factory
    failed = getattr(request.node, "rep_call", None) is not None and request.node.rep_call.failed
    leftovers = []
    for number, session in enumerate(sessions, start=1):
        if failed:
            name = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.nodeid)
            session.page.screenshot(path=str(evidence_dir() / f"{name}-{number}.png"))
        if not session.allow_problems:
            leftovers += session.problems()
        session.context.close()
    if not failed and leftovers:
        pytest.fail("browser problems: " + "; ".join(leftovers), pytrace=False)


@pytest.fixture
def evidence_folder():
    """The run's evidence folder, for a scenario that records what it measured as information (R45 in WebKit)."""
    return evidence_dir()


@pytest.fixture
def plain_context(browser):
    """A context for pages the suite only reads (the goldens as files). Same rig, same clipboard script."""
    made = []

    def factory(**options):
        context = rig.new_context(browser, **options)
        made.append(context)
        return context

    yield factory
    for context in made:
        context.close()
