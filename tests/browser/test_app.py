"""Functional suite for split-app. One test per scenario row of qa.md, named test_R<n>_<what>.

Run from the project root: python -m pytest tests/browser -q
Real gestures only. State that is not under test is set up with fill() and clicks on visible controls,
never through a hook in the app (there is none).
"""
import json
import re
import urllib.request

import pytest

import rig
import seeds
import support
from support import CSP, ROOT, dom_walk, first_diff, golden_walk, panel_text, person_field


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


# ---------------------------------------------------------------- Task 2: shell and boot (R1, R2, R3, R38)
HEAD_SUMMARY_JS = """() => [...document.head.children].map((e) => [e.tagName.toLowerCase(),
  Object.fromEntries([...e.attributes].map((a) => [a.name, a.value])), e.tagName === 'TITLE' ? e.textContent : ''])"""
SOURCE_URL = re.compile(r"""(?:\b(?:src|href)\s*=\s*["']\s*(/|[A-Za-z][A-Za-z0-9+.-]*:)|\bfrom\s*["'](?![.]{1,2}/)|\bimport\s*\(\s*["'](?![.]{1,2}/))""")
NAMESPACE_CALL = 'createElementNS("http://www.w3.org/2000/svg"'
SAMPLE_NAMES = ["Aisyah", "Ben", "Chen", "Devi", "Farid", "Grace", "Hafiz", "Indra", "Jia Hui", "Kumar", "Lina",
                "Mei Ling", "Nasi lemak", "Char kuey teow", "Mee goreng", "Satay"]


def test_R1_entry_point_loads_only_its_own_files(open_app):
    session = open_app()
    assert session.page.evaluate(HEAD_SUMMARY_JS) == [
        ["meta", {"charset": "utf-8"}, ""],
        ["meta", {"name": "viewport", "content": "width=device-width, initial-scale=1"}, ""],
        ["meta", {"http-equiv": "Content-Security-Policy", "content": CSP}, ""],
        ["title", {}, "Split"],
        ["link", {"rel": "stylesheet", "href": "src/system.css"}, ""],
        ["script", {"type": "module", "src": "src/main.js"}, ""],
    ]
    assert session.page.evaluate("document.documentElement.lang") == "en"
    golden = (ROOT / "docs" / "design" / "system.css").read_bytes()
    # RC-5: the shipped stylesheet is the golden's bytes plus one trailing rule, so hidden elements stay hidden.
    assert (ROOT / "src" / "system.css").read_bytes() == golden + b"\n[hidden] { display: none !important; }\n"
    assert session.problems() == []
    assert ("GET", session.base + "/src/system.css") in session.requests


def test_R1_page_works_from_a_sub_path(open_app):
    parent = rig.StaticServer(ROOT.parent).start()
    try:
        folder = f"/{ROOT.name}"
        session = open_app(base_server=parent, path=folder + "/", prefix=folder)
        assert panel_text(session.page) == "Shares\nEnter the subtotal to see the shares."
        assert session.page.locator("li.person").count() == 2
        assert session.problems() == []
    finally:
        parent.stop()
    for name, text in support.shipped_text().items():
        assert not SOURCE_URL.search(text.replace(NAMESPACE_CALL, "")), name
        if name == "index.html":
            assert "://" not in text


def test_R2_cold_boot_is_a_new_bill_with_no_seed(open_app):
    page = open_app().page
    assert [field.input_value() for field in page.locator("li.person input").all()] == ["Person 1", "Person 2"]
    assert all(button.is_disabled() for button in page.locator("li.person button").all())
    assert page.locator("#mode-even").is_checked() and not page.locator("#mode-item").is_checked()
    assert page.locator("#subtotal").input_value() == ""
    assert (page.locator("#rate-service").input_value(), page.locator("#rate-sst").input_value()) == ("10", "6")
    assert page.locator("p.error").count() == 0 and page.locator("[aria-invalid]").count() == 0
    assert panel_text(page) == "Shares\nEnter the subtotal to see the shares."
    assert page.evaluate("localStorage.getItem('split.draft')") is None
    assert page.evaluate("Object.getOwnPropertyNames(window).filter((n) => n.startsWith('__'))") == []


def test_R2_no_sample_data_ships():
    for name, text in support.shipped_text().items():
        for sample in SAMPLE_NAMES:
            assert not re.search(rf"\b{re.escape(sample)}\b", text, re.IGNORECASE), f"{sample} in {name}"


@pytest.mark.parametrize("state, seed, golden", [("S3", None, "bill-empty")])
def test_R3_rendered_markup_matches_its_golden(open_app, plain_context, state, seed, golden):
    app = dom_walk(open_app(seed=seed).page)
    assert first_diff(app, golden_walk(plain_context, golden)) is None, state


def test_R3_the_walk_sees_every_rendered_element_and_flags_a_change(open_app):
    app = dom_walk(open_app().page)

    def count(entry):
        return 1 + sum(count(child) for child in entry["children"])

    assert count(app) > 40
    changed = json.loads(json.dumps(app))
    changed["children"][0]["children"][0]["children"][0]["text"] = "Different"  # the wordmark
    assert "app='Split' golden='Different'" in first_diff(app, changed)


def test_R38_policy_is_exact_and_nothing_inline():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert re.findall(r'<meta http-equiv="Content-Security-Policy" content="([^"]*)">', html) == [CSP]
    assert html.count("Content-Security-Policy") == 1
    assert "<style" not in html and not re.search(r"\sstyle\s*=", html)
    assert not re.search(r"<script(?![^>]*\ssrc=)", html) and not re.search(r"\son[a-z]+\s*=", html)


def test_R38_strict_policy_blocks_nothing_the_app_needs(open_app):
    session = open_app()
    page = session.page
    assert page.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(238, 240, 238)"
    assert page.locator("li.person").count() == 2 and page.locator("#rate-service").count() == 1
    assert panel_text(page) == "Shares\nEnter the subtotal to see the shares."
    assert page.locator("body [style]").count() == 0
    assert session.problems() == []


# ---------------------------------------------------------------- Task 3: people (R4 to R7, R33, R34, R42)
def add_person_named(page, name):
    page.get_by_role("button", name="Add person").click()
    person_field(page, page.locator("li.person").count()).fill(name)


def three_people(page):
    """Aisyah, Ben and Chen, set up with fill() and the Add person button."""
    person_field(page, 1).fill("Aisyah")
    person_field(page, 2).fill("Ben")
    add_person_named(page, "Chen")


def remove_button(page, label):
    return page.get_by_role("button", name=f"Remove {label}", exact=True)


def test_R4_person_rows_carry_their_names_and_labels(open_app):
    page = open_app().page
    three_people(page)
    for number, name in enumerate(["Aisyah", "Ben", "Chen"], start=1):
        field = person_field(page, number)
        assert field.input_value() == name
        assert [field.get_attribute(a) for a in ("placeholder", "maxlength", "autocomplete", "type")] == [
            f"Person {number}", "20", "off", "text"]
        assert remove_button(page, name).is_enabled()


def test_R4_a_blank_name_falls_back_to_its_position_but_not_in_the_field(open_app):
    page = open_app().page
    three_people(page)
    support.replace_text(page, person_field(page, 2), "")
    assert person_field(page, 2).input_value() == ""
    assert person_field(page, 2).get_attribute("placeholder") == "Person 2"
    assert remove_button(page, "Person 2").count() == 1
    support.replace_text(page, person_field(page, 2), "   ")  # spaces only count as blank (PD-2)
    assert person_field(page, 2).input_value() == "   " and remove_button(page, "Person 2").count() == 1


def test_R5_renaming_a_person_updates_the_remove_name_on_each_keystroke(open_app):
    page = open_app().page
    three_people(page)
    person_field(page, 3).click()
    page.keyboard.press("End")
    typed = "Chen"
    for key in " Wei":
        page.keyboard.type(key)
        typed += key
        assert remove_button(page, typed.strip()).count() == 1
    assert person_field(page, 3).input_value() == "Chen Wei"


def test_R6_add_person_until_the_limit(open_app, plain_context):
    page = open_app().page
    add = page.get_by_role("button", name="Add person")
    add.click()
    assert page.locator("li.person").count() == 3
    assert person_field(page, 3).input_value() == "" and person_field(page, 3).get_attribute("placeholder") == "Person 3"
    assert all(button.is_enabled() for button in page.locator("li.person button").all())
    for _ in range(9):
        add.click()
    assert page.locator("li.person").count() == 12 and add.is_disabled()
    specimen = support.open_golden(plain_context, "states").locator('section[aria-labelledby="spec-s8a"] button[disabled]')
    assert support.specimen_props(add, ["cursor"]) == support.specimen_props(specimen, ["cursor"])
    assert add.evaluate("(el) => getComputedStyle(el).cursor") == "not-allowed"
    box = add.bounding_box()
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    assert page.locator("li.person").count() == 12


def test_R7_remove_a_person(open_app):
    page = open_app().page
    three_people(page)
    remove_button(page, "Chen").click()
    assert [f.input_value() for f in page.locator("li.person input").all()] == ["Aisyah", "Ben"]
    assert all(button.is_disabled() for button in page.locator("li.person button").all())


@pytest.mark.parametrize("remove, now_at_two", [("Ben", "Chen"), ("Chen", "Ben")])
def test_R34_focus_moves_to_the_name_field_at_the_removed_position(open_app, remove, now_at_two):
    page = open_app().page
    page.get_by_role("button", name="Add person").click()
    assert support.active_label(page) == "Person 3 name"
    three_people_again = ["Aisyah", "Ben", "Chen"]
    for number, name in enumerate(three_people_again, start=1):
        person_field(page, number).fill(name)
    remove_button(page, remove).click()
    assert support.active_label(page) == "Person 2 name" and person_field(page, 2).input_value() == now_at_two


def type_and_watch(page, field, text):
    """R33: after every key the same element has focus and the caret sits after what was typed."""
    handle = field.element_handle()
    field.click()
    page.keyboard.press("Control+A")
    for count, key in enumerate(text, start=1):
        page.keyboard.type(key)
        assert page.evaluate("(el) => [el === document.activeElement, el.selectionStart]", handle) == [True, count]
    page.keyboard.press("Home")
    page.keyboard.type("X")
    assert page.evaluate("(el) => [el.value.startsWith('X'), el.selectionStart, el === document.activeElement]", handle) == [True, 1, True]


def test_R33_typing_in_a_person_name_keeps_focus_and_caret(open_app):
    page = open_app().page
    type_and_watch(page, person_field(page, 1), "Aisyah")


def test_R33_ime_composition_survives_a_render(open_app):
    page = open_app().page
    field = person_field(page, 1)
    handle = field.element_handle()
    field.click()
    page.keyboard.press("End")
    cdp = page.context.new_cdp_session(page)
    cdp.send("Input.imeSetComposition", {"text": "jia", "selectionStart": 3, "selectionEnd": 3})
    assert field.input_value().endswith("jia")
    cdp.send("Input.insertText", {"text": "家"})
    assert field.input_value().endswith("家") and "jia" not in field.input_value()
    assert page.evaluate("(el) => el === document.activeElement", handle)


def test_R42_duplicate_names_are_accepted_and_act_on_their_own_row(open_app):
    page = open_app().page
    person_field(page, 1).fill("Ben")
    person_field(page, 2).fill("Ben")
    add_person_named(page, "Chen")
    assert page.locator("p.error, div.note").count() == 0
    assert [f.input_value() for f in page.locator("li.person input").all()] == ["Ben", "Ben", "Chen"]
    assert remove_button(page, "Ben").count() == 2
    remove_button(page, "Ben").nth(1).click()
    assert [f.input_value() for f in page.locator("li.person input").all()] == ["Ben", "Chen"]


# ===== END OF TESTS (new tests go above this line) =====
