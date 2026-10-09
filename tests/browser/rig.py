"""Shared test rig: the static server lifecycle and the only way to make a browser context.

Used by conftest.py (the functional suite), live_e2e.py and fidelity/run.py, so all three start and stop
the server the same way (qa.md, "Server lifecycle") and no context can exist without a clipboard script.
Test-side only. Never loaded by index.html.
"""
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLIPBOARD_DIR = Path(__file__).resolve().parent / "clipboard"
CLIPBOARD_SCRIPTS = ("recorder", "reject", "missing")
READY_TRIES = 50
READY_WAIT_SECONDS = 0.1
STOP_WAIT_SECONDS = 10


def free_port():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def port_is_free(port):
    with socket.socket() as probe:
        try:
            probe.bind(("127.0.0.1", port))
        except OSError:
            return False
        return True


class StaticServer:
    """python -m http.server on a free loopback port, with a bounded start and a checked stop."""

    def __init__(self, root=ROOT, say=print):
        self.root, self.say = Path(root), say
        self.port = self.process = None

    @property
    def base(self):
        return f"http://127.0.0.1:{self.port}"

    def start(self):
        self.port = free_port()
        self.process = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(self.port), "--bind", "127.0.0.1"],
            cwd=self.root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        self.say(f"server STARTED pid {self.process.pid} port {self.port} root {self.root}")
        try:
            self._wait_until_ready()
        except BaseException:
            self.stop()
            raise
        return self

    def _wait_until_ready(self):
        for _ in range(READY_TRIES):
            if self.process.poll() is not None:
                raise RuntimeError(f"server exited early with code {self.process.returncode}")
            try:
                urllib.request.urlopen(self.base + "/", timeout=1).close()
                return
            except OSError:
                time.sleep(READY_WAIT_SECONDS)
        raise RuntimeError(f"server gave up after {READY_TRIES} tries")

    def stop(self):
        if self.process is None:
            return
        pid, port = self.process.pid, self.port
        self.process.kill()
        try:
            self.process.wait(STOP_WAIT_SECONDS)
        except subprocess.TimeoutExpired:
            self.say(f"server pid {pid} did not exit within {STOP_WAIT_SECONDS} s")
        self.say(f"server STOPPED pid {pid} port {port}, exited {self.process.poll() is not None}, "
                 f"port free again {port_is_free(port)}")
        self.process = None


def clipboard_script(name):
    if name not in CLIPBOARD_SCRIPTS:
        raise ValueError(f"unknown clipboard script {name!r}")
    return (CLIPBOARD_DIR / f"{name}.js").read_text(encoding="utf-8")


def new_context(browser, *, clipboard="recorder", init_scripts=(), **options):
    """The one place a browser context is made (CG-7, R38).

    Every context gets exactly one clipboard script, so no run can reach the operating system clipboard.
    No clipboard permission is ever granted and the policy is never bypassed, so both are refused here.
    """
    for forbidden in ("permissions", "bypass_csp"):
        if forbidden in options:
            raise ValueError(f"{forbidden} is never set on a test context")
    context = browser.new_context(**options)
    context.add_init_script(script=clipboard_script(clipboard))
    for script in init_scripts:
        context.add_init_script(script=script)
    return context


def storage_state(base, seed):
    """Playwright storage_state that holds one draft, so the app boots into it through its own load path."""
    return {"cookies": [], "origins": [
        {"origin": base, "localStorage": [{"name": "split.draft", "value": seed}]},
    ]}
