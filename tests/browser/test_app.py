"""Functional suite for split-app. One test per scenario row of qa.md, named test_R<n>_<what>.

Run from the project root: python -m pytest tests/browser -q
Real gestures only. State that is not under test is set up with fill() and clicks on visible controls,
never through a hook in the app (there is none).
"""
import json
import urllib.request

import pytest

import rig
import seeds

ROOT = rig.ROOT


# ---------------------------------------------------------------- Task 1: the rig (R1, R39)
def test_R1_harness_serves_the_project_root_over_loopback(server):
    assert server.base.startswith("http://127.0.0.1:")
    with urllib.request.urlopen(server.base + "/CLAUDE.md") as response:
        assert response.status == 200


def test_R1_harness_stops_its_server_and_frees_the_port():
    lines = []
    throwaway = rig.StaticServer(ROOT, say=lines.append).start()
    port, process = throwaway.port, throwaway.process
    assert not rig.port_is_free(port)
    throwaway.stop()
    assert process.poll() is not None and rig.port_is_free(port)
    assert "STARTED" in lines[0] and f"port {port}" in lines[0]
    assert "STOPPED" in lines[-1] and "port free again True" in lines[-1]


def test_R1_harness_wait_for_the_server_is_bounded(monkeypatch):
    def refuse(*args, **kwargs):
        raise OSError("refused")

    monkeypatch.setattr(rig.urllib.request, "urlopen", refuse)
    monkeypatch.setattr(rig, "READY_TRIES", 3)
    monkeypatch.setattr(rig, "READY_WAIT_SECONDS", 0)
    lines = []
    attempt = rig.StaticServer(ROOT, say=lines.append)
    with pytest.raises(RuntimeError, match="server gave up after 3 tries"):
        attempt.start()
    assert attempt.process is None and rig.port_is_free(attempt.port)


def test_R1_seeds_parse_and_differ_as_documented():
    s1, s2, s5, s8 = (json.loads(text) for text in (seeds.S1, seeds.S2, seeds.S5, seeds.S8))
    assert s2["bill"]["mode"] == "even" and s2["bill"]["subtotalText"] == "100.00"
    assert [p["name"] for p in s2["bill"]["people"]] == ["Aisyah", "Ben", "Chen"]
    assert s1["bill"]["mode"] == "item" and len(s1["bill"]["items"]) == 4
    assert s1["bill"]["items"][3]["who"] == ["p1", "p3"]
    assert s5["bill"]["items"][2]["who"] == [] and s5["bill"]["items"][0]["who"] == ["p1"]
    assert len(s8["bill"]["people"]) == 12 and s8["bill"]["nextId"] == 13
    assert len(seeds.UNREADABLE) == 24 and len(set(seeds.UNREADABLE.values())) == 24
    assert set(seeds.ODD_READABLE) == {"G1", "G2", "G3"}
    assert seeds.dump(json.loads(seeds.S2)) == seeds.S2 and seeds.dump(json.loads(seeds.S1)) == seeds.S1


def test_R39_clipboard_recorder_keeps_the_text_and_never_reaches_the_system(open_app):
    session = open_app(path="/docs/design/bill-even.html", allow_problems=True)
    page = session.page
    page.evaluate("navigator.clipboard.writeText('Bill split\\nTotal RM 1.00')")
    assert page.evaluate("window.testClipboardText") == "Bill split\nTotal RM 1.00"
    assert page.evaluate("window.testClipboardWrites") == 1
    assert "[native code]" not in page.evaluate("Clipboard.prototype.writeText.toString()")


def test_R39_clipboard_reject_script_refuses_the_write(open_app):
    page = open_app(clipboard="reject", path="/docs/design/bill-even.html", allow_problems=True).page
    name = page.evaluate("navigator.clipboard.writeText('x').then(() => 'resolved', (e) => e.name)")
    assert name == "NotAllowedError"


def test_R39_clipboard_missing_script_hides_the_api(open_app):
    page = open_app(clipboard="missing", path="/docs/design/bill-even.html", allow_problems=True).page
    assert page.evaluate("navigator.clipboard === undefined")


def test_R39_a_context_never_gets_a_permission_or_bypasses_the_policy(browser):
    for option in ({"permissions": ["clipboard-read"]}, {"bypass_csp": True}):
        with pytest.raises(ValueError):
            rig.new_context(browser, **option)
    with pytest.raises(ValueError):
        rig.new_context(browser, clipboard="native")


def test_R39_only_the_rig_makes_browser_contexts():
    direct, persistent = "new" + "_context(", "launch_persistent" + "_context"
    offenders = []
    for path in (ROOT / "tests" / "browser").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if path.name != "rig.py" and (direct in text.replace("rig." + direct, "") or persistent in text):
            offenders.append(path.name)
    assert offenders == []


def test_R39_the_request_log_flags_anything_but_same_origin_gets(open_app):
    session = open_app(path="/docs/design/bill-even.html", allow_problems=True)
    session.page.evaluate("fetch('/never-asked-for', { method: 'POST' }).catch(() => {})")
    session.page.wait_for_timeout(200)
    found = session.problems()
    assert any(entry.startswith("request: POST") for entry in found)
    assert any(entry.startswith("console error") for entry in found)  # the server answers a POST with 501


# ===== END OF TESTS (new tests go above this line) =====
