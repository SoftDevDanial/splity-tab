"""Fixtures for the functional suite: a loopback static server, headless Chromium, and a capturing session.

Every scenario gets a new context (rig.new_context, with the clipboard recorder unless it names another
script), records console messages, page errors and requests, and fails at teardown on a console error, a CSP
violation, a page error or a request that is not a same-origin GET for the page's own files (qa.md,
"Console and network"). A failed scenario leaves a screenshot in the evidence folder.
Set SPLIT_EVIDENCE=1 to also write pytest.txt and junit.xml there.
"""
import datetime
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import sync_playwright

import rig

EVIDENCE_ROOT = rig.ROOT / "docs" / "modules" / "split-app" / "qa" / "functional"
_evidence = {"dir": None, "lines": []}


def evidence_dir():
    """The run's evidence folder, made on first use (a failure screenshot, or SPLIT_EVIDENCE=1)."""
    if _evidence["dir"] is None:
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        _evidence["dir"] = EVIDENCE_ROOT / stamp
        _evidence["dir"].mkdir(parents=True, exist_ok=True)
    return _evidence["dir"]


def pytest_configure(config):
    if os.environ.get("SPLIT_EVIDENCE"):
        config.option.xmlpath = str(evidence_dir() / "junit.xml")


def pytest_runtest_logreport(report):
    if os.environ.get("SPLIT_EVIDENCE") and (report.when == "call" or report.failed):
        _evidence["lines"].append(f"{report.outcome.upper():8} {report.when:8} {report.nodeid} ({report.duration:.2f}s)")


def pytest_sessionfinish(session, exitstatus):
    if os.environ.get("SPLIT_EVIDENCE"):
        (evidence_dir() / "pytest.txt").write_text("\n".join(_evidence["lines"]) + f"\nexit status {exitstatus}\n", encoding="utf-8")


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

    def problems(self):
        found = [f"console {kind}: {text}" for kind, text in self.console
                 if kind == "error" or "Content Security Policy" in text]
        found += [f"page error: {error}" for error in self.page_errors]
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
def browser():
    with sync_playwright() as playwright:
        chromium = playwright.chromium.launch(headless=True)
        yield chromium
        chromium.close()


@pytest.fixture
def open_app(server, browser, request):
    """open_app(seed=None, clipboard="recorder", viewport=(390, 844), reduced_motion=None, init_scripts=(),
    path="/", goto=True, base_server=None, prefix="", allow_problems=False) -> Session"""
    sessions = []

    def factory(seed=None, clipboard="recorder", viewport=(390, 844), reduced_motion=None, init_scripts=(),
                path="/", goto=True, base_server=None, prefix="", allow_problems=False):
        target = base_server or server
        options = {"viewport": {"width": viewport[0], "height": viewport[1]},
                   "device_scale_factor": 1, "color_scheme": "light"}
        if reduced_motion:
            options["reduced_motion"] = reduced_motion
        if seed is not None:
            options["storage_state"] = rig.storage_state(target.base, seed)
        context = rig.new_context(browser, clipboard=clipboard, init_scripts=init_scripts, **options)
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
