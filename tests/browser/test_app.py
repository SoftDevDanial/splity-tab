"""Functional suite for split-app. One test per scenario row of qa.md, named test_R<n>_<what>.

Run from the project root: python -m pytest tests/browser -q
Real gestures only. State that is not under test is set up with fill() and clicks on visible controls,
never through a hook in the app (there is none).
"""
import ast
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

import pytest

import rig
import seeds
import support
from expected import (EVEN_MESSAGE, S1_CHECK, S1_COPY, S1_ITEMS, S1_ROWS, S1_SUMMARY, S2_CHECK, S2_COPY, S2_ROWS,
                      S2_SUMMARY)
from support import CSP, GOLDEN_V1_DIR, ROOT, dom_walk, first_diff, golden_walk, open_golden, panel_text, person_field


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
    golden = (GOLDEN_V1_DIR / "system.css").read_bytes()
    # RC-5: the shipped stylesheet is the golden's bytes plus one trailing rule, so hidden elements stay hidden.
    assert (ROOT / "src" / "system.css").read_bytes() == golden + b"\n[hidden] { display: none !important; }\n"
    assert session.problems() == []
    assert ("GET", session.base + "/src/system.css") in session.requests


def test_R1_page_works_from_a_sub_path(open_app):
    # The target is a GitHub Pages project path (/split/), so the app must work one folder down. The only way to serve
    # it there is a server rooted at the parent folder, which also serves the sibling projects on 127.0.0.1 while this
    # test runs. Accepted (ORCH, WR-11): loopback only, test-only, stopped in this test.
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
    assert first_diff(app, golden_walk(plain_context, golden, folder=GOLDEN_V1_DIR)) is None, state


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
    specimen = support.open_golden(plain_context, "states", folder=GOLDEN_V1_DIR).locator('section[aria-labelledby="spec-s8a"] button[disabled]')
    assert support.specimen_props(add, ["cursor"]) == support.specimen_props(specimen, ["cursor"])
    assert add.evaluate("(el) => getComputedStyle(el).cursor") == "not-allowed"
    box = add.bounding_box()
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    assert page.locator("li.person").count() == 12


def test_R6_a_restored_twelve_person_bill_shows_the_limit_state(open_app, plain_context):
    # qa.md ST-08 boots the S8 seed: the limit state as a restored bill, not only as the end of nine clicks.
    page = open_app(seed=seeds.S8).page
    add = page.get_by_role("button", name="Add person")
    assert page.locator("li.person").count() == 12 and add.is_disabled()
    assert person_field(page, 12).input_value() == "Mei Ling" and stored_text(page) == seeds.S8  # a restore writes nothing
    specimen = support.open_golden(plain_context, "states", folder=GOLDEN_V1_DIR).locator('section[aria-labelledby="spec-s8a"] button[disabled]')
    assert support.specimen_props(add, ["cursor"]) == support.specimen_props(specimen, ["cursor"])
    cells = page.eval_on_selector_all(
        "section[aria-labelledby=h-people] ul.cells > li",
        "(els) => els.map((el) => { const box = el.getBoundingClientRect(); return [Math.round(box.left), Math.round(box.top)]; })")
    assert len(cells) == 13
    assert len({top for _, top in cells[:12]}) == 6 and len({left for left, _ in cells[:12]}) == 2  # six rows of two at 390
    assert cells[12][0] == cells[0][0] and cells[12][1] > cells[11][1]  # Add person is the next cell
    assert panel_text(page) == EVEN_MESSAGE


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


@pytest.mark.chromium_only(reason="Needs a CDP session (Input.imeSetComposition, Input.insertText), "
                                  "which Playwright gives in Chromium only.")
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


# ---------------------------------------------------------------- Task 4: mode and subtotal (R8, R9, R10)

def subtotal_field(page):
    return page.get_by_role("textbox", name="Subtotal in RM", exact=True)


def switch_to(page, label):
    page.get_by_text(label, exact=True).click()


def test_R8_switching_modes_keeps_the_subtotal(open_app):
    page = open_app().page
    support.replace_text(page, subtotal_field(page), "100.00")
    switch_to(page, "By item")
    assert page.locator("#mode-item").is_checked() and not page.locator("#subtotal").is_visible()
    assert panel_text(page) == "Shares\nAdd an item to see the shares."
    switch_to(page, "Even")
    assert page.locator("#mode-even").is_checked() and subtotal_field(page).input_value() == "100.00"


def test_R8_arrow_keys_move_between_the_modes(open_app):
    page = open_app().page
    for _ in range(12):
        page.keyboard.press("Tab")
        if page.evaluate("document.activeElement.id") == "mode-even":
            break
    assert page.evaluate("document.activeElement.id") == "mode-even"
    page.keyboard.press("ArrowRight")
    assert page.locator("#mode-item").is_checked() and page.evaluate("document.activeElement.id") == "mode-item"


def test_R9_subtotal_field_has_its_unit_label_and_input_mode(open_app):
    page = open_app().page
    field = subtotal_field(page)
    assert field.get_attribute("id") == "subtotal"
    assert [field.get_attribute(a) for a in ("type", "inputmode", "autocomplete")] == ["text", "decimal", "off"]
    wrapper = page.locator("span.field.money:has(#subtotal)")
    assert wrapper.locator(".unit").inner_text() == "RM" and wrapper.locator("input").count() == 1
    support.replace_text(page, field, "100.00")
    assert field.input_value() == "100.00"


# The three inline error texts (spec, Copy), each exact. A case that showed another field's text must fail.
AMOUNT_MESSAGE, SERVICE_MESSAGE, SST_MESSAGE = "Enter an amount like 12.50", "Enter a rate from 0 to 30", "Enter a rate from 0 to 20"

# Rows are added with the field's own task: item prices (task 5), Service charge and SST (task 6).
ERROR_CASES = [
    pytest.param(lambda page: None, lambda page: page.locator("#subtotal"), "0", AMOUNT_MESSAGE, "subtotal-error", "12.50", id="subtotal"),
    pytest.param(lambda page: build_s1(page), lambda page: item_price(page, 2), "13.505", AMOUNT_MESSAGE, "price-error-i5", "13.50", id="item-price"),
    pytest.param(lambda page: None, lambda page: rate_field(page, "Service charge"), "31", SERVICE_MESSAGE, "rate-service-error", "10", id="service"),
    pytest.param(lambda page: None, lambda page: rate_field(page, "SST"), "20.01", SST_MESSAGE, "rate-sst-error", "6", id="sst"),
]


@pytest.mark.parametrize("setup, field_of, bad, message, error_id, good", ERROR_CASES)
def test_R10_an_inline_error_waits_for_the_field_to_be_left(open_app, setup, field_of, bad, message, error_id, good):
    page = open_app().page
    setup(page)
    field = field_of(page)
    support.replace_text(page, field, bad)
    assert page.locator(f"#{error_id}").count() == 0
    page.keyboard.press("Tab")
    assert page.locator(f"p.error#{error_id}").inner_text() == message
    assert field.get_attribute("aria-invalid") == "true"
    assert field.get_attribute("aria-describedby").split()[0] == error_id
    support.replace_text(page, field, "")
    page.keyboard.type(good[0])
    assert page.locator(f"#{error_id}").count() == 0 and field.get_attribute("aria-invalid") is None
    page.keyboard.type(good[1:])
    assert field.input_value() == good


@pytest.mark.parametrize("setup, field_of, bad, message, error_id, good", ERROR_CASES)
def test_R10_a_cleared_error_does_not_come_back_until_the_field_is_left_again(
        open_app, setup, field_of, bad, message, error_id, good):
    # WR-03 / K1: (c) says the error goes at valid text and "does not come back until the field next loses focus".
    page = open_app().page
    setup(page)
    field = field_of(page)
    support.replace_text(page, field, bad)
    page.keyboard.press("Tab")
    assert page.locator(f"p.error#{error_id}").count() == 1
    support.replace_text(page, field, good[0])  # one valid character over the whole text, typed in the field
    assert page.locator(f"#{error_id}").count() == 0
    page.keyboard.type("x")  # bad again, and the field still has focus
    assert page.locator(f"#{error_id}").count() == 0 and field.get_attribute("aria-invalid") is None
    page.keyboard.press("Tab")
    assert page.locator(f"p.error#{error_id}").inner_text() == message and field.get_attribute("aria-invalid") == "true"


def test_R10_an_empty_field_never_shows_an_error(open_app):
    page = open_app().page
    subtotal_field(page).click()
    page.keyboard.press("Tab")
    assert page.locator("p.error").count() == 0 and page.locator("[aria-invalid]").count() == 0
    assert panel_text(page) == EVEN_MESSAGE


def test_R10_typing_bad_text_in_a_focused_field_shows_no_error_early(open_app):
    page = open_app().page
    subtotal_field(page).click()
    page.keyboard.type("abc")
    assert page.locator("p.error").count() == 0 and panel_text(page) == EVEN_MESSAGE


def test_R10_an_error_survives_a_mode_switch(open_app):
    page = open_app().page
    support.replace_text(page, subtotal_field(page), "0")
    page.keyboard.press("Tab")
    switch_to(page, "By item")
    switch_to(page, "Even")
    assert page.locator("p.error#subtotal-error").inner_text() == "Enter an amount like 12.50"


# ---------------------------------------------------------------- Task 5: items (R7, R11 to R14, R10, R34)

def item_name(page, number):
    return page.get_by_label(f"Item {number} name", exact=True)


def item_price(page, number):
    return page.get_by_label(f"Item {number} price in RM", exact=True)


def who_group(page, item_label):
    return page.get_by_role("group", name=f"Who had {item_label}", exact=True)


def toggle(page, item_label, person):
    return who_group(page, item_label).get_by_role("button", name=person, exact=True)


def add_item_named(page, name, price, people=()):
    page.get_by_role("button", name="Add item").click()
    number = page.locator("li.item").count()
    item_name(page, number).fill(name)
    item_price(page, number).fill(price)
    for person in people:
        toggle(page, name, person).click()


def build_s1(page):
    """The S1 bill by gestures: Aisyah, Ben, Chen, By item, the four items with their taps."""
    three_people(page)
    switch_to(page, "By item")
    for name, price, people in S1_ITEMS:
        add_item_named(page, name, price, people)


def test_R5_renaming_an_item_updates_its_accessible_names(open_app):
    page = open_app().page
    build_s1(page)
    support.replace_text(page, item_name(page, 4), "Satay")
    assert remove_button(page, "Satay").count() == 1 and who_group(page, "Satay").count() == 1


def test_R5_a_person_label_follows_the_name_into_every_toggle(open_app):
    page = open_app().page
    build_s1(page)
    person_field(page, 3).click()
    page.keyboard.press("End")
    page.keyboard.type(" Wei")
    for name, _, _ in S1_ITEMS:
        assert who_group(page, name).get_by_role("button").all_inner_texts() == ["Aisyah", "Ben", "Chen Wei"]
    support.replace_text(page, person_field(page, 2), "")
    for name, _, _ in S1_ITEMS:
        assert who_group(page, name).get_by_role("button").all_inner_texts() == ["Aisyah", "Person 2", "Chen Wei"]


def test_R7_removing_a_person_takes_them_off_every_item(open_app):
    page = open_app().page
    build_s1(page)
    remove_button(page, "Chen").click()
    assert [f.input_value() for f in page.locator("li.person input").all()] == ["Aisyah", "Ben"]
    for name, _, _ in S1_ITEMS:
        assert who_group(page, name).get_by_role("button").all_inner_texts() == ["Aisyah", "Ben"]


def test_R8_switching_modes_keeps_both_sets_of_input(open_app):
    page = open_app().page
    support.replace_text(page, subtotal_field(page), "100.00")
    switch_to(page, "By item")
    add_item_named(page, "Tea", "5.00", ["Person 1"])
    assert page.locator("ol.items").is_visible() and not page.locator("#subtotal").is_visible()
    switch_to(page, "Even")
    assert subtotal_field(page).input_value() == "100.00" and not page.locator("ol.items").is_visible()
    switch_to(page, "By item")
    assert item_name(page, 1).input_value() == "Tea" and item_price(page, 1).input_value() == "5.00"
    assert toggle(page, "Tea", "Person 1").get_attribute("aria-pressed") == "true"


def test_R11_item_rows_carry_their_names_and_labels(open_app):
    page = open_app().page
    build_s1(page)
    for number, (name, price, _) in enumerate(S1_ITEMS, start=1):
        field = item_name(page, number)
        assert field.input_value() == name
        assert [field.get_attribute(a) for a in ("placeholder", "maxlength", "autocomplete", "type")] == [
            f"Item {number}", "40", "off", "text"]
        money = item_price(page, number)
        assert money.input_value() == price
        assert [money.get_attribute(a) for a in ("inputmode", "autocomplete", "type")] == ["decimal", "off", "text"]
        wrapper = page.locator(f'span.field.money:has(input[aria-label="Item {number} price in RM"])')
        assert wrapper.locator(".unit").inner_text() == "RM"
        assert remove_button(page, name).is_enabled()


def test_R12_add_an_item_remove_one_and_reach_the_limit(open_app, plain_context):
    page = open_app().page
    switch_to(page, "By item")
    add = page.get_by_role("button", name="Add item")
    add.click()
    assert page.locator("li.item").count() == 1
    assert item_name(page, 1).input_value() == "" and item_name(page, 1).get_attribute("placeholder") == "Item 1"
    assert item_price(page, 1).input_value() == "" and toggle_states(page, 1) == ["false", "false"]
    assert panel_text(page) == "Shares\nAdd an item to see the shares."
    for _ in range(49):
        add.click()
    assert page.locator("li.item").count() == 50 and add.is_disabled()
    specimen = support.open_golden(plain_context, "states", folder=GOLDEN_V1_DIR).locator('section[aria-labelledby="spec-s8a"] button[disabled]')
    assert support.specimen_props(add, ["cursor"]) == support.specimen_props(specimen, ["cursor"])
    page.locator("li.item").nth(1).get_by_role("button", name="Remove Item 2").click()
    assert page.locator("li.item").count() == 49 and add.is_enabled()


def toggle_states(page, number):
    return [b.get_attribute("aria-pressed") for b in page.locator("li.item").nth(number - 1).locator("button.tap").all()]


def test_R13_tapping_a_person_on_an_item(open_app):
    page = open_app().page
    build_s1(page)
    assert [toggle_states(page, n) for n in (1, 2, 3, 4)] == [
        ["true", "false", "false"], ["false", "true", "false"], ["false", "false", "true"], ["true", "false", "true"]]
    ben = toggle(page, "Satay, 10 sticks", "Ben")
    ben.click()
    assert ben.get_attribute("aria-pressed") == "true"
    ben.click()
    assert ben.get_attribute("aria-pressed") == "false"


def test_R14_a_price_error_sits_in_the_item_line(open_app, plain_context):
    page = open_app().page
    build_s1(page)
    support.replace_text(page, item_price(page, 2), "13.505")
    page.keyboard.press("Tab")
    error = page.locator("p.error#price-error-i5")
    assert error.evaluate("(e) => e === e.parentElement.lastElementChild && e.parentElement.className") == "item-line"
    assert item_price(page, 2).get_attribute("aria-describedby") == "price-error-i5"
    specimen = support.open_golden(plain_context, "states", folder=GOLDEN_V1_DIR).locator("#s4-price-error")
    extra = ["textAlign", "marginTop"]
    assert support.specimen_props(error, extra) == support.specimen_props(specimen, extra)
    assert error.evaluate("(e) => getComputedStyle(e).textAlign") == "right"


@pytest.mark.parametrize("action, target", [
    ("Add item", "Item 5 name"), ("Remove Char kuey teow", "Item 2 name"), ("Remove Satay, 10 sticks", "Item 3 name")])
def test_R34_focus_after_adding_or_removing_an_item(open_app, action, target):
    page = open_app().page
    build_s1(page)
    page.get_by_role("button", name=action, exact=True).click()
    assert support.active_label(page) == target


def test_R34_removing_the_last_item_focuses_add_item(open_app):
    page = open_app().page
    switch_to(page, "By item")
    page.get_by_role("button", name="Add item").click()
    page.get_by_role("button", name="Remove Item 1").click()
    assert support.active_label(page) == "Add item"


@pytest.mark.parametrize("field_of, text", [(lambda page: item_name(page, 1), "Nasi"), (lambda page: item_price(page, 1), "15.90")])
def test_R33_typing_in_an_item_field_keeps_focus_and_caret(open_app, field_of, text):
    page = open_app().page
    build_s1(page)
    type_and_watch(page, field_of(page), text)


# ---------------------------------------------------------------- Task 6: charges (R15, R10)
def rate_field(page, label):
    return page.get_by_role("textbox", name=f"{label} in percent", exact=True)


def test_R15_charges_block_and_its_defaults(open_app):
    page = open_app().page
    for label, value in (("Service charge", "10"), ("SST", "6")):
        field = rate_field(page, label)
        assert field.input_value() == value and field.get_attribute("aria-describedby") == "charges-hint"
        assert [field.get_attribute(a) for a in ("inputmode", "autocomplete", "type")] == ["decimal", "off", "text"]
        wrapper = page.locator(f"span.field.percent:has(#{field.get_attribute('id')})")
        assert wrapper.locator("input + .unit").inner_text() == "%"
    assert page.locator("p.hint#charges-hint").inner_text() == "Set a charge to 0 if your bill already includes it."


def test_R15_a_rate_error_names_both_ids_and_its_range(open_app, plain_context):
    page = open_app().page
    support.replace_text(page, rate_field(page, "Service charge"), "31")
    page.keyboard.press("Tab")
    error = page.locator("p.error#rate-service-error")
    assert error.inner_text() == "Enter a rate from 0 to 30"
    assert error.evaluate("(e) => e === e.parentElement.lastElementChild && e.parentElement.querySelector('label').textContent") == "Service charge in percent"
    assert rate_field(page, "Service charge").get_attribute("aria-describedby") == "rate-service-error charges-hint"
    specimen = support.open_golden(plain_context, "states", folder=GOLDEN_V1_DIR).locator("#s4-subtotal-error")  # ST-10: styled as ST-01
    assert support.specimen_props(error, ["marginTop"]) == support.specimen_props(specimen, ["marginTop"])


def test_R10_an_empty_rate_never_shows_an_error(open_app):
    page = open_app().page
    support.replace_text(page, rate_field(page, "Service charge"), "")
    page.keyboard.press("Tab")
    assert page.locator("p.error").count() == 0 and page.locator("[aria-invalid]").count() == 0
    assert panel_text(page) == "Shares\nCheck the charges to see the shares."


# ---------------------------------------------------------------- Task 7: the bill panel (R3, R16 to R21)
COPY_BUTTON = "button.copy"


def table_cells(page, part):
    """Cell texts of table.shares thead, tbody or tfoot, one list per row."""
    return page.evaluate(
        "(part) => [...document.querySelectorAll(`table.shares ${part} tr`)].map((tr) => [...tr.children].map((c) => c.textContent.trim()))",
        part)


def summary_rows(page):
    return page.evaluate(
        "() => [...document.querySelectorAll('dl.sum .row')].map((r) => [r.querySelector('dt').textContent.trim(),"
        " r.querySelector('.amt').textContent.trim(), (r.querySelector('.work') || { textContent: '' }).textContent.trim()])")


def build_s2(page):
    """The S2 bill by gestures: Aisyah, Ben, Chen, Even, Subtotal 100.00."""
    three_people(page)
    subtotal_field(page).fill("100.00")


def build_s5(page):
    build_s1(page)
    toggle(page, "Mee goreng mamak", "Chen").click()


@pytest.mark.parametrize("state, build, golden", [
    ("S2", build_s2, "bill-even"), ("S1", build_s1, "bill-items"), ("S5", build_s5, "bill-unassigned")])
def test_R3_rendered_markup_matches_its_golden_by_gestures(open_app, plain_context, state, build, golden):
    page = open_app().page
    build(page)
    assert first_diff(dom_walk(page), golden_walk(plain_context, golden, folder=GOLDEN_V1_DIR)) is None, state


def test_R9_a_subtotal_drives_the_even_split(open_app):
    page = open_app().page
    subtotal_field(page).fill("100.00")
    assert summary_rows(page) == S2_SUMMARY
    assert table_cells(page, "tbody") == [["Person 1", "RM 58.30"], ["Person 2", "RM 58.30"]]


def test_R16_the_panel_follows_every_keystroke_and_stays_quiet(open_app):
    page = open_app().page
    build_s2(page)
    support.replace_text(page, subtotal_field(page), "5")
    assert summary_rows(page)[3][1] == "RM 5.83" and [r[1] for r in table_cells(page, "tbody")] == ["RM 1.95", "RM 1.94", "RM 1.94"]
    page.keyboard.type("0")
    assert summary_rows(page)[3][1] == "RM 58.30" and [r[1] for r in table_cells(page, "tbody")] == ["RM 19.44", "RM 19.43", "RM 19.43"]
    assert live_elements_in_tape(page) == ["p.status[role=status]"]


def live_elements_in_tape(page):
    """Every element of div.tape (itself included) that is live: an aria-live attribute or a status, alert or log role."""
    return page.evaluate("""() => [...document.querySelectorAll('div.tape, div.tape *')]
        .filter((e) => e.hasAttribute('aria-live') || ['status', 'alert', 'log'].includes(e.getAttribute('role')))
        .map((e) => `${e.tagName.toLowerCase()}.${e.className}[role=${e.getAttribute('role')}]`)""")


def test_R16_the_status_is_the_only_live_element_and_only_while_the_table_is(open_app):
    # RD-2 (qa.md, 2026-10-09): p.status[role=status] is the one live element in the tape. The tape and its
    # sections carry no aria-live and no role, and a blocked or unassigned panel has no live element at all.
    page = open_app().page
    assert live_elements_in_tape(page) == []  # S3: only the Shares message
    build_s2(page)
    assert live_elements_in_tape(page) == ["p.status[role=status]"]
    assert page.locator("div.tape [aria-live], div.tape section[role], div.tape[role], div.tape[aria-live]").count() == 0
    support.replace_text(page, subtotal_field(page), "")
    assert live_elements_in_tape(page) == []
    unassigned = open_app().page
    build_s5(unassigned)
    assert live_elements_in_tape(unassigned) == []


BLOCKED_CASES = [
    pytest.param(lambda page: (build_s2(page), support.replace_text(page, rate_field(page, "Service charge"), "")),
                 "Check the charges to see the shares.", id="rate-empty"),
    pytest.param(lambda page: (build_s1(page), support.replace_text(page, rate_field(page, "SST"), "25")),
                 "Check the charges to see the shares.", id="rate-too-high"),
    pytest.param(lambda page: (build_s2(page), support.replace_text(page, subtotal_field(page), "")),
                 "Enter the subtotal to see the shares.", id="subtotal-empty"),
    pytest.param(lambda page: switch_to(page, "By item"), "Add an item to see the shares.", id="no-items"),
    pytest.param(lambda page: (switch_to(page, "By item"), page.get_by_role("button", name="Add item").click()),
                 "Add an item to see the shares.", id="item-unpriced"),
    pytest.param(lambda page: (build_s1(page), support.replace_text(page, item_price(page, 1), "abc")),
                 "Give every item a price to see the shares.", id="item-bad-price"),
]


@pytest.mark.parametrize("setup, message", BLOCKED_CASES)
def test_R17_when_the_shares_cannot_be_worked_out(open_app, setup, message):
    page = open_app().page
    setup(page)
    assert panel_text(page) == f"Shares\n{message}"
    assert page.locator("div.tape section").count() == 1 and page.locator("div.tape table, h2#h-summary, p.status").count() == 0
    assert page.locator(COPY_BUTTON).count() == 0


def test_R18_items_that_still_need_a_person(open_app):
    page = open_app().page
    build_s1(page)
    toggle(page, "Mee goreng mamak", "Chen").click()
    assert [row[1] for row in summary_rows(page)] == ["RM 59.40", "RM 5.94", "RM 3.92", "RM 69.26"]
    assert panel_text(page).splitlines()[-2:] == ["Shares", "1 item still needs a person. Tap who had it to see the shares."]
    assert page.locator("div.tape table, p.status").count() == 0 and page.locator(COPY_BUTTON).count() == 0
    toggle(page, "Char kuey teow", "Ben").click()
    assert panel_text(page).splitlines()[-1] == "2 items still need a person. Tap who had each one to see the shares."
    toggle(page, "Mee goreng mamak", "Chen").click()
    toggle(page, "Char kuey teow", "Ben").click()
    assert table_cells(page, "tbody") == S1_ROWS and table_cells(page, "tfoot") == S1_CHECK
    assert page.locator(COPY_BUTTON).count() == 1


def test_R7_removing_a_person_can_leave_an_item_without_anyone(open_app):
    page = open_app().page
    build_s1(page)
    remove_button(page, "Chen").click()
    assert panel_text(page).splitlines()[-1] == "1 item still needs a person. Tap who had it to see the shares."


@pytest.mark.parametrize("build, expected", [(build_s2, S2_SUMMARY), (build_s1, S1_SUMMARY)], ids=["S2", "S1"])
def test_R19_the_bill_summary_shows_its_working(open_app, build, expected):
    page = open_app().page
    build(page)
    assert summary_rows(page) == expected
    assert page.locator("dl.sum .row.total .amt > span.final").inner_text() == expected[3][1]


def test_R19_a_charge_of_zero_is_allowed_and_still_shown(open_app):
    page = open_app().page
    build_s2(page)
    support.replace_text(page, rate_field(page, "Service charge"), "0")
    assert page.locator("p.error").count() == 0
    rows = summary_rows(page)
    assert rows[1] == ["+Service charge", "RM 0.00", "0% of RM 100.00"] and rows[2] == ["+SST", "RM 6.00", "6% of RM 100.00"]
    assert [row[1] for row in table_cells(page, "tbody")] == ["RM 35.34", "RM 35.33", "RM 35.33"]


def test_R20_the_even_split_from_a_cold_boot(open_app):
    page = open_app().page
    three_people(page)
    support.replace_text(page, subtotal_field(page), "100.00")
    assert [cell for row in table_cells(page, "thead") for cell in row] == ["Person", "Share"]
    assert page.locator("table.shares thead").get_attribute("class") == "sr-only"
    assert table_cells(page, "tbody") == S2_ROWS and table_cells(page, "tfoot") == S2_CHECK


def test_R21_the_by_item_split_from_gestures(open_app):
    page = open_app().page
    build_s2(page)
    build_items_after_switch(page)
    assert table_cells(page, "thead") == [["Person", "Items", "+Charges", "=Share"]]
    assert table_cells(page, "tbody") == S1_ROWS and table_cells(page, "tfoot") == S1_CHECK


def build_items_after_switch(page):
    switch_to(page, "By item")
    for name, price, people in S1_ITEMS:
        add_item_named(page, name, price, people)


def test_R21_someone_who_had_nothing_is_still_listed(open_app):
    page = open_app().page
    three_people(page)
    switch_to(page, "By item")
    add_item_named(page, "Tea", "10.00", ["Ben"])
    add_item_named(page, "Cake", "5.01", ["Ben", "Chen"])
    assert table_cells(page, "tbody") == [["Aisyah", "RM 0.00", "RM 0.00", "RM 0.00"],
                                          ["Ben", "RM 12.51", "RM 2.08", "RM 14.59"],
                                          ["Chen", "RM 2.50", "RM 0.41", "RM 2.91"]]
    assert table_cells(page, "tfoot") == [["Adds up to", "RM 15.01", "RM 2.49", "RM 17.50"]]


def test_R13_tapping_a_person_changes_the_shares(open_app):
    page = open_app().page
    build_s1(page)
    toggle(page, "Satay, 10 sticks", "Ben").click()
    assert table_cells(page, "tbody") == [["Aisyah", "RM 21.90", "RM 3.64", "RM 25.54"],
                                          ["Ben", "RM 19.50", "RM 3.24", "RM 22.74"],
                                          ["Chen", "RM 18.00", "RM 2.98", "RM 20.98"]]
    assert table_cells(page, "tfoot") == S1_CHECK
    toggle(page, "Satay, 10 sticks", "Ben").click()
    assert table_cells(page, "tbody") == S1_ROWS


def test_R5_a_blank_name_reads_as_its_position_in_the_shares_row(open_app):
    page = open_app().page
    build_s1(page)
    support.replace_text(page, person_field(page, 2), "")
    assert table_cells(page, "tbody")[1][0] == "Person 2"


def test_R8_the_panel_follows_each_mode(open_app):
    page = open_app().page
    support.replace_text(page, subtotal_field(page), "100.00")
    switch_to(page, "By item")
    add_item_named(page, "Tea", "5.00", ["Person 1"])
    assert summary_rows(page)[3][1] == "RM 5.83"
    switch_to(page, "Even")
    assert summary_rows(page)[3][1] == "RM 116.60"


# ---------------------------------------------------------------- Task 8: copy summary (R22 to R24, R5, R42)
FAILED_COPY = "Could not copy. Your browser blocked the clipboard."


def copy_summary(page):
    page.get_by_role("button", name="Copy summary").click()


def status_of(page):
    status = page.locator("p.status")
    return status.inner_text() if status.count() else None, status.get_attribute("class") if status.count() else None


@pytest.mark.parametrize("build, expected", [(build_s2, S2_COPY), (build_s1, S1_COPY)], ids=["S2", "S1"])
def test_R22_copy_summary_puts_the_exact_text_on_the_clipboard(open_app, build, expected):
    page = open_app().page
    build(page)
    copy_summary(page)
    assert status_of(page) == ("Summary copied", "status")
    assert page.evaluate("window.testClipboardText") == expected and page.evaluate("window.testClipboardWrites") == 1


def test_R23_the_browser_blocks_the_clipboard(open_app):
    page = open_app(clipboard="reject").page
    build_s2(page)
    before = panel_text(page)
    copy_summary(page)
    assert status_of(page) == (FAILED_COPY, "status status-failure")
    assert panel_text(page).replace(FAILED_COPY, "").strip() == before.strip()


def test_R23_the_clipboard_api_is_missing(open_app):
    page = open_app(clipboard="missing").page
    build_s2(page)
    copy_summary(page)
    assert status_of(page) == (FAILED_COPY, "status status-failure")


def test_R24_the_status_lives_as_long_as_the_table(open_app):
    page = open_app().page
    build_s2(page)
    status = page.locator("p.status")
    assert status.count() == 1 and status.inner_text() == "" and not status.is_visible()
    copy_summary(page)
    assert status.inner_text() == "Summary copied"
    person_field(page, 1).click()
    page.keyboard.press("End")
    page.keyboard.type("x")
    assert status_of(page)[0] == "Summary copied"
    support.replace_text(page, subtotal_field(page), "")
    assert page.locator("p.status").count() == 0
    subtotal_field(page).fill("100.00")
    assert status_of(page) == ("", "status")


def test_R22_a_failed_copy_is_replaced_by_the_next_attempt(open_app):
    page = open_app(clipboard="reject").page
    build_s2(page)
    copy_summary(page)
    page.evaluate("Clipboard.prototype.writeText = () => Promise.resolve()")
    copy_summary(page)
    assert status_of(page) == ("Summary copied", "status")


def test_R24_a_copy_that_finishes_after_the_table_left_sets_no_status(open_app):
    # The browser may take a while to decide (a permission prompt). If the panel turns into a message meanwhile, the
    # late answer must not leave a status behind for the table that comes back.
    page = open_app().page
    build_s2(page)
    # The function form: Playwright calls a function that a string expression evaluates to, and would wait for this one.
    page.evaluate("() => { Clipboard.prototype.writeText = () => new Promise((resolve) => { window.finishCopy = resolve; }); }")
    copy_summary(page)
    support.replace_text(page, subtotal_field(page), "")
    assert page.locator("p.status").count() == 0 and panel_text(page) == EVEN_MESSAGE
    page.evaluate("window.finishCopy()")
    settle(page)
    assert page.locator("p.status").count() == 0
    subtotal_field(page).fill("100.00")
    assert status_of(page) == ("", "status")


def test_R5_a_new_name_reaches_the_copied_text(open_app):
    page = open_app().page
    build_s1(page)
    person_field(page, 3).click()
    page.keyboard.press("End")
    page.keyboard.type(" Wei")
    copy_summary(page)
    assert page.evaluate("window.testClipboardText").splitlines()[4] == "Chen Wei RM 24.48"


def test_R42_duplicate_names_through_the_whole_flow(open_app):
    page = open_app().page
    person_field(page, 1).fill("Ben")
    person_field(page, 2).fill("Ben")
    add_person_named(page, "Chen")
    subtotal_field(page).fill("100.00")
    assert page.locator("p.error, div.note").count() == 0
    assert table_cells(page, "tbody") == [["Ben", "RM 38.87"], ["Ben", "RM 38.87"], ["Chen", "RM 38.86"]]
    assert table_cells(page, "tfoot") == S2_CHECK and remove_button(page, "Ben").count() == 2
    copy_summary(page)
    assert page.evaluate("window.testClipboardText").splitlines()[2:4] == ["Ben RM 38.87", "Ben RM 38.87"]
    switch_to(page, "By item")
    add_item_named(page, "Tea", "10.00")
    who_group(page, "Tea").get_by_role("button", name="Ben", exact=True).nth(1).click()
    assert [b.get_attribute("aria-pressed") for b in who_group(page, "Tea").get_by_role("button").all()] == ["false", "true", "false"]
    assert table_cells(page, "tbody") == [["Ben", "RM 0.00", "RM 0.00", "RM 0.00"],
                                          ["Ben", "RM 10.00", "RM 1.66", "RM 11.66"],
                                          ["Chen", "RM 0.00", "RM 0.00", "RM 0.00"]]
    assert table_cells(page, "tfoot") == [["Adds up to", "RM 10.00", "RM 1.66", "RM 11.66"]]
    remove_button(page, "Ben").nth(1).click()
    assert [f.input_value() for f in page.locator("li.person input").all()] == ["Ben", "Chen"]
    assert panel_text(page).splitlines()[-1] == "1 item still needs a person. Tap who had it to see the shares."


# ---------------------------------------------------------------- Task 9: the draft (R25 to R28, with R3, R8, R10, R24, R26, R42)
NEW_BILL_DRAFT = ('{"version":2,"bill":{"mode":"even","people":[{"id":"p1","name":"Person 1"},{"id":"p2","name":"Person 2"}],'
                  '"subtotalText":"","items":[],"serviceText":"10","sstText":"6","spare":{"rule":"top"},"nextId":3}}')
SNAPSHOT_JS = """() => ({
  people: [...document.querySelectorAll('li.person input')].map((i) => i.value),
  mode: document.querySelector('input[name=mode]:checked').value,
  subtotal: document.querySelector('#subtotal').value,
  items: [...document.querySelectorAll('li.item')].map((li) => [...li.querySelectorAll('input')].map((i) => i.value)
    .concat([...li.querySelectorAll('.tap')].map((b) => b.getAttribute('aria-pressed')))),
  rates: [document.querySelector('#rate-service').value, document.querySelector('#rate-sst').value],
})"""


def stored(page):
    text = page.evaluate("localStorage.getItem('split.draft')")
    return text if text is None else json.loads(text)


def stored_text(page):
    return page.evaluate("localStorage.getItem('split.draft')")


def snapshot(page):
    return page.evaluate(SNAPSHOT_JS)


@pytest.mark.parametrize("change, check", [
    (lambda page: person_field(page, 1).fill("A"), lambda bill: bill["people"][0]["name"] == "A"),
    (lambda page: page.get_by_role("button", name="Add person").click(), lambda bill: len(bill["people"]) == 3 and bill["nextId"] == 4),
    (lambda page: subtotal_field(page).fill("1"), lambda bill: bill["subtotalText"] == "1"),
    (lambda page: switch_to(page, "By item"), lambda bill: bill["mode"] == "item"),
    (lambda page: (switch_to(page, "By item"), page.get_by_role("button", name="Add item").click()),
     lambda bill: bill["items"] == [{"id": "i3", "name": "", "priceText": "", "who": []}]),
    (lambda page: rate_field(page, "SST").fill("8"), lambda bill: bill["sstText"] == "8"),
    # A removal is a change too (WR-05, mutant RM: it updated the screen and forgot to save). The id counter never goes back.
    (lambda page: (page.get_by_role("button", name="Add person").click(), remove_button(page, "Person 3").click()),
     lambda bill: [p["id"] for p in bill["people"]] == ["p1", "p2"] and bill["nextId"] == 4),
    (lambda page: (switch_to(page, "By item"), page.get_by_role("button", name="Add item").click(),
                   page.get_by_role("button", name="Remove Item 1").click()),
     lambda bill: bill["items"] == [] and bill["nextId"] == 4),
], ids=["name", "add-person", "subtotal", "mode", "add-item", "sst", "remove-person", "remove-item"])
def test_R25_every_change_is_saved(open_app, change, check):
    page = open_app().page
    assert stored(page) is None
    change(page)
    draft = stored(page)
    assert list(draft) == ["version", "bill"] and draft["version"] == 2 and check(draft["bill"])


def test_R25_leaving_a_field_or_copying_does_not_save(open_app):
    page = open_app(seed=seeds.S2).page
    assert stored_text(page) == seeds.S2
    subtotal_field(page).click()
    page.keyboard.press("Tab")
    copy_summary(page)
    assert stored_text(page) == seeds.S2


def test_R25_a_cold_boot_and_a_reload_write_nothing(open_app):
    page = open_app().page
    page.reload()
    assert stored_text(page) is None


@pytest.mark.parametrize("build, seed", [(build_s2, seeds.S2), (lambda page: (build_s2(page), build_items_after_switch(page)), None)],
                         ids=["S2", "S1-after-a-subtotal"])
def test_R25_a_bill_built_by_gestures_is_stored_like_its_seed(open_app, build, seed):
    page = open_app().page
    build(page)
    if seed is not None:
        assert stored_text(page) == seed
    else:  # the S1 seed has an empty subtotal; here "100.00" was typed first and must survive in the draft
        assert stored(page)["bill"] == dict(json.loads(seeds.S1)["bill"], subtotalText="100.00")


@pytest.mark.parametrize("seed", [seeds.S2, seeds.S1, seeds.S5], ids=["S2", "S1", "S5"])
def test_R26_a_restored_bill_looks_like_the_one_built_by_gestures(open_app, seed):
    builders = {seeds.S2: build_s2, seeds.S1: build_s1, seeds.S5: build_s5}
    built = open_app()
    builders[seed](built.page)
    restored = open_app(seed=seed)
    assert snapshot(restored.page) == snapshot(built.page)
    assert stored_text(restored.page) == seed  # restoring writes nothing


@pytest.mark.parametrize("seed, golden", [(seeds.S2, "bill-even"), (seeds.S1, "bill-items"), (seeds.S5, "bill-unassigned")],
                         ids=["S2", "S1", "S5"])
def test_R3_a_restored_bill_matches_its_golden(open_app, plain_context, seed, golden):
    assert first_diff(dom_walk(open_app(seed=seed).page), golden_walk(plain_context, golden, folder=GOLDEN_V1_DIR)) is None


def test_R3_the_note_matches_its_specimen(open_app, plain_context):
    # WR-05 (mutant LIVE2: a stray aria-live on the wrapper and aria-pressed on the button). S7 is walked as a part of
    # the page, because the specimen frame in states.html carries specimen-only markup around it (allowed difference 6).
    app = dom_walk(open_app(seed=seeds.UNREADABLE["B1"]).page, "div.note-wrap")
    golden = golden_walk(plain_context, "states", selector='section[aria-labelledby="spec-s7"] div.note-wrap', folder=GOLDEN_V1_DIR)
    assert first_diff(app, golden) is None


def test_R3_the_open_dialog_and_the_page_behind_it_match_their_golden(open_app, plain_context):
    # The golden draws the scrim as div.backdrop and marks .app inert (allowed difference 4), so the walk compares the
    # dialog and the page behind it, the two parts that are the same markup in both.
    page = open_app(seed=seeds.S2).page
    open_dialog(page)
    golden = open_golden(plain_context, "new-bill-dialog", folder=GOLDEN_V1_DIR)
    for part in ("dialog.dialog", "div.app"):
        assert first_diff(dom_walk(page, part), dom_walk(golden, part)) is None, part


def test_R26_come_back_later(open_app):
    session = open_app()
    page = session.page
    build_s2(page)
    build_items_after_switch(page)
    before = snapshot(page)
    page.close()
    again = session.new_page()
    session.open("/", page=again)
    assert snapshot(again) == before and again.locator("#mode-item").is_checked()
    assert table_cells(again, "tbody") == S1_ROWS and table_cells(again, "tfoot") == S1_CHECK
    switch_to(again, "Even")
    assert subtotal_field(again).input_value() == "100.00"
    assert summary_rows(again)[3][1] == "RM 116.60"


def test_R8_both_sets_of_input_survive_a_reload(open_app):
    page = open_app().page
    subtotal_field(page).fill("100.00")
    switch_to(page, "By item")
    add_item_named(page, "Tea", "5.00", ["Person 1"])
    page.reload()
    assert page.locator("#mode-item").is_checked() and item_name(page, 1).input_value() == "Tea"
    assert toggle(page, "Tea", "Person 1").get_attribute("aria-pressed") == "true" and summary_rows(page)[3][1] == "RM 5.83"
    switch_to(page, "Even")
    assert subtotal_field(page).input_value() == "100.00" and summary_rows(page)[3][1] == "RM 116.60"


@pytest.mark.parametrize("name", ["G1", "G2", "G3"])
def test_R26_odd_but_readable_drafts_load(open_app, name):
    seed = seeds.ODD_READABLE[name]
    page = open_app(seed=seed).page
    assert page.locator("div.note").count() == 0
    if name == "G2":
        assert person_field(page, 1).input_value() == seeds.FLAGS_20
    else:
        assert snapshot(page) == snapshot(open_app(seed=seeds.S2).page)
    if name == "G3":
        assert page.evaluate("({}).polluted") is None
    if name == "G1":
        subtotal_field(page).fill("100.0")
        text = stored_text(page)
        assert "extra" not in text and "colour" not in text and json.loads(text)["bill"]["subtotalText"] == "100.0"


@pytest.mark.parametrize("name", list(seeds.UNREADABLE))
def test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note(open_app, name):
    session = open_app(seed=seeds.UNREADABLE[name])
    page = session.page
    note = page.locator("div.note-wrap > div.note[role=status]")
    assert note.locator("p").inner_text() == "Your saved bill could not be read, so a new one was started."
    assert note.get_by_role("button", name="Dismiss note").count() == 1
    assert page.evaluate("document.querySelector('.bar').nextElementSibling.className") == "note-wrap"
    assert [f.input_value() for f in page.locator("li.person input").all()] == ["Person 1", "Person 2"]
    assert page.locator("#mode-even").is_checked() and subtotal_field(page).input_value() == ""
    assert panel_text(page) == EVEN_MESSAGE
    assert stored_text(page) == NEW_BILL_DRAFT
    page.reload()
    assert page.locator("div.note").count() == 0 and stored_text(page) == NEW_BILL_DRAFT


def test_R27_dismissing_the_note_moves_focus_to_the_first_name(open_app):
    page = open_app(seed=seeds.UNREADABLE["B1"]).page
    page.get_by_role("button", name="Dismiss note").click()
    assert page.locator("div.note-wrap").count() == 0 and support.active_label(page) == "Person 1 name"


STORAGE_BREAKERS = {
    "read-localStorage": "Object.defineProperty(window, 'localStorage', { get() { throw new DOMException('blocked', 'SecurityError'); } });",
    "getItem": "Storage.prototype.getItem = function () { throw new Error('read failed'); };",
    "setItem": "Storage.prototype.setItem = function () { throw new DOMException('full', 'QuotaExceededError'); };",
}


@pytest.mark.parametrize("script", STORAGE_BREAKERS.values(), ids=STORAGE_BREAKERS.keys())
def test_R28_the_app_works_without_storage(open_app, script):
    page = open_app(init_scripts=[script]).page
    subtotal_field(page).fill("100.00")
    page.get_by_role("button", name="Add person").click()
    assert summary_rows(page)[3][1] == "RM 116.60" and len(table_cells(page, "tbody")) == 3
    assert page.locator("div.note, p.error").count() == 0


def test_R10_a_restored_bad_field_shows_its_error_at_once(open_app):
    page = open_app(seed=seeds.with_bill(seeds.S2, subtotalText="0", serviceText="31")).page
    assert page.locator("p.error#subtotal-error").inner_text() == "Enter an amount like 12.50"
    assert page.locator("p.error#rate-service-error").inner_text() == "Enter a rate from 0 to 30"
    assert page.locator("p.error#rate-sst-error").count() == 0


def test_R24_the_status_is_not_saved(open_app):
    page = open_app(seed=seeds.S2).page
    copy_summary(page)
    assert status_of(page)[0] == "Summary copied"
    page.reload()
    assert status_of(page) == ("", "status")


def test_R42_the_draft_keeps_both_people_with_the_same_name(open_app):
    page = open_app().page
    person_field(page, 1).fill("Ben")
    person_field(page, 2).fill("Ben")
    add_person_named(page, "Chen")
    assert [p["name"] for p in stored(page)["bill"]["people"]] == ["Ben", "Ben", "Chen"]
    remove_button(page, "Ben").nth(1).click()
    assert [(p["id"], p["name"]) for p in stored(page)["bill"]["people"]] == [("p1", "Ben"), ("p3", "Chen")]


# ---------------------------------------------------------------- Task 10: the New bill dialog (R29 to R31, R27)
def new_bill_button(page):
    return page.get_by_role("button", name="New bill", exact=True)


def open_dialog(page):
    new_bill_button(page).click()
    return page.get_by_role("dialog", name="Start a new bill?")


def focused(page):
    return page.evaluate("document.activeElement.textContent.trim() || document.activeElement.id")


def test_R29_the_dialog_opens_with_the_safe_choice_focused(open_app):
    page = open_app(seed=seeds.S2).page
    dialog = open_dialog(page)
    assert dialog.evaluate("(d) => d.matches(':modal')") and dialog.get_attribute("aria-describedby") == "dialog-text"
    assert page.locator("#dialog-text").inner_text() == "This clears the people, items and amounts."
    assert [b.get_attribute("class") for b in dialog.get_by_role("button").all()] == ["btn btn-primary btn-large", "btn btn-outline btn-large"]
    assert focused(page) == "Cancel"
    page.keyboard.press("Tab")
    assert focused(page) == "Start new bill"
    page.keyboard.press("Tab")
    assert focused(page) == "Cancel"
    page.keyboard.press("Shift+Tab")
    page.keyboard.press("Shift+Tab")
    assert focused(page) == "Cancel"
    assert page.locator(".app").evaluate("(e) => e.getBoundingClientRect().height") == 844
    page.mouse.move(195, 100)
    page.mouse.wheel(0, 600)
    assert page.evaluate("window.scrollY") == 0


def test_R30_a_click_inside_the_dialog_box_keeps_it_open(open_app):
    # WR-05 (mutant J: every click that targets the dialog element closes it). The padding belongs to the element itself.
    page = open_app(seed=seeds.S2).page
    open_dialog(page)
    box = page.locator("dialog.dialog").bounding_box()
    inside = [(box["x"] + 3, box["y"] + 3), (box["x"] + box["width"] - 3, box["y"] + box["height"] - 3),
              centre_of(page.locator("#dialog-title")), centre_of(page.locator("#dialog-text"))]
    for point in inside:
        page.mouse.click(*point)
        assert dialog_is_open(page) is True, point
    assert stored_text(page) == seeds.S2


@pytest.mark.parametrize("close", ["cancel", "escape", "backdrop-corner", "backdrop-over-a-field"])
def test_R30_leaving_the_dialog_without_starting_over(open_app, close):
    page = open_app(seed=seeds.S2).page
    first_name = person_field(page, 1).bounding_box()
    open_dialog(page)
    if close == "cancel":
        page.get_by_role("button", name="Cancel").click()
    elif close == "escape":
        page.keyboard.press("Escape")
    elif close == "backdrop-corner":
        page.mouse.click(10, 10)
    else:
        page.mouse.click(first_name["x"] + first_name["width"] / 2, first_name["y"] + first_name["height"] / 2)
    assert page.locator("dialog.dialog").evaluate("(d) => d.open") is False
    assert focused(page) == "New bill" and stored_text(page) == seeds.S2
    assert snapshot(page) == snapshot(open_app(seed=seeds.S2).page) and summary_rows(page) == S2_SUMMARY


def test_R31_start_over(open_app):
    page = open_app(seed=seeds.S1).page
    open_dialog(page)
    page.get_by_role("button", name="Start new bill").click()
    assert page.locator("dialog.dialog").evaluate("(d) => d.open") is False and focused(page) == "New bill"
    assert [f.input_value() for f in page.locator("li.person input").all()] == ["Person 1", "Person 2"]
    assert page.locator("#mode-even").is_checked() and subtotal_field(page).input_value() == ""
    assert (rate_field(page, "Service charge").input_value(), rate_field(page, "SST").input_value()) == ("10", "6")
    assert panel_text(page) == EVEN_MESSAGE and stored_text(page) == NEW_BILL_DRAFT
    page.reload()
    assert panel_text(page) == EVEN_MESSAGE and page.locator("li.person").count() == 2


def test_R31_start_over_clears_the_copy_status(open_app):
    page = open_app(seed=seeds.S2).page
    copy_summary(page)
    assert status_of(page)[0] == "Summary copied"
    open_dialog(page)
    page.get_by_role("button", name="Start new bill").click()
    assert page.locator("p.status").count() == 0 and panel_text(page) == EVEN_MESSAGE
    subtotal_field(page).fill("100.00")
    assert status_of(page) == ("", "status")


def changed_price(seed, item_id, text):
    return seeds.changed(seed, lambda d: [i.update(priceText=text) for i in d["bill"]["items"] if i["id"] == item_id])


START_OVER_CASES = [
    pytest.param(seeds.with_bill(seeds.S2, subtotalText="0"), None, lambda page: subtotal_field(page), id="subtotal"),
    # Item i5 of S1 gets a bad price. After the start over, three new items get the ids i3, i4 and i5 again.
    pytest.param(changed_price(seeds.S1, "i5", "13.505"), "three-items", lambda page: item_price(page, 3), id="item-price"),
    pytest.param(seeds.with_bill(seeds.S2, serviceText="31"), None, lambda page: rate_field(page, "Service charge"), id="service"),
    pytest.param(seeds.with_bill(seeds.S2, sstText="25"), None, lambda page: rate_field(page, "SST"), id="sst"),
]


@pytest.mark.parametrize("seed, prepare, field_of", START_OVER_CASES)
def test_R31_start_over_clears_the_error_flags(open_app, seed, prepare, field_of):
    # The restored bad text shows its error at once (R10 b), so each case starts with the error on screen.
    page = open_app(seed=seed).page
    assert page.locator("p.error").count() == 1
    open_dialog(page)
    page.get_by_role("button", name="Start new bill").click()
    if prepare == "three-items":  # the new items get the ids i3, i4 and i5 again
        switch_to(page, "By item")
        for _ in range(3):
            page.get_by_role("button", name="Add item").click()
    assert page.locator("p.error").count() == 0 and page.locator("[aria-invalid]").count() == 0
    field = field_of(page)
    support.replace_text(page, field, "abc")
    assert page.locator("p.error").count() == 0 and page.locator("[aria-invalid]").count() == 0
    page.keyboard.press("Tab")
    assert page.locator("p.error").count() == 1 and field.get_attribute("aria-invalid") == "true"


def test_R27_the_note_is_not_touched_by_start_over(open_app):
    page = open_app(seed=seeds.UNREADABLE["B1"]).page
    open_dialog(page)
    page.get_by_role("button", name="Start new bill").click()
    assert page.locator("div.note").count() == 1
    page.get_by_role("button", name="Dismiss note").click()
    open_dialog(page)
    page.get_by_role("button", name="Start new bill").click()
    assert page.locator("div.note").count() == 0


# ---------------------------------------------------------------- RD-3: a press below a field that is being left (R10, CG-3)
# Leaving a bad amount or rate shows its error, which pushes everything under it down by one line. When the
# field is left by a press on a control under it, the press must still land on that control (RD-3, 2026-10-09).
RECORD_CLICKS_JS = """() => {
  window.testClicks = [];
  document.addEventListener('click', (event) => window.testClicks.push(event.target.id || event.target.tagName.toLowerCase()), true);
}"""
PRESS_CASES = [  # (seed, field, bad text, the control pressed under it, error id, the click's target, the error's text)
    pytest.param(None, lambda page: page.locator("#subtotal"), "0", lambda page: page.locator("#rate-service"),
                 "subtotal-error", "rate-service", AMOUNT_MESSAGE, id="subtotal"),
    pytest.param(seeds.S1, lambda page: item_price(page, 2), "13.505", lambda page: toggle(page, "Char kuey teow", "Aisyah"),
                 "price-error-i5", "button", AMOUNT_MESSAGE, id="item-price"),
    pytest.param(None, lambda page: rate_field(page, "Service charge"), "31", lambda page: page.locator("#charges-hint"),
                 "rate-service-error", "charges-hint", SERVICE_MESSAGE, id="service"),
    pytest.param(None, lambda page: rate_field(page, "SST"), "25", lambda page: page.locator("#charges-hint"),
                 "rate-sst-error", "charges-hint", SST_MESSAGE, id="sst"),
]


def centre_of(locator):
    """Where the middle of `locator` is now, after scrolling it into view (scrolling does not move focus)."""
    locator.scroll_into_view_if_needed()
    box = locator.bounding_box()
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def press(page, how, point):
    """One press and release at a point, by mouse or by a touch tap."""
    if how == "touch":
        page.touchscreen.tap(*point)
    else:
        page.mouse.click(*point)


@pytest.mark.parametrize("how", ["mouse", "touch"])
@pytest.mark.parametrize("seed, field_of, bad, below_of, error_id, lands_on, message", PRESS_CASES)
def test_R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on(
        open_app, how, seed, field_of, bad, below_of, error_id, lands_on, message):
    page = open_app(seed=seed, touch=how == "touch").page
    support.replace_text(page, field_of(page), bad)
    assert page.locator(f"#{error_id}").count() == 0  # CG-3: no error while the field still has focus
    page.evaluate(RECORD_CLICKS_JS)
    press(page, how, centre_of(below_of(page)))
    assert page.evaluate("window.testClicks") == [lands_on]
    assert page.locator(f"p.error#{error_id}").inner_text() == message
    assert field_of(page).get_attribute("aria-invalid") == "true"


@pytest.mark.parametrize("how", ["mouse", "touch"])
def test_R13_a_tap_below_an_invalid_price_toggles_that_person_and_then_shows_the_error(open_app, how):
    page = open_app(seed=seeds.S1, touch=how == "touch").page
    support.replace_text(page, item_price(page, 2), "13.505")  # invalid, and its error is not flagged yet
    aisyah = toggle(page, "Char kuey teow", "Aisyah")
    assert aisyah.get_attribute("aria-pressed") == "false" and page.locator("p.error").count() == 0
    press(page, how, centre_of(aisyah))
    assert aisyah.get_attribute("aria-pressed") == "true"
    assert sorted(stored(page)["bill"]["items"][1]["who"]) == ["p1", "p2"]
    assert page.locator("p.error#price-error-i5").inner_text() == "Enter an amount like 12.50"
    assert item_price(page, 2).get_attribute("aria-describedby") == "price-error-i5"


def test_R10_the_error_waits_for_the_mouse_button_to_come_up(open_app):
    page = open_app(seed=seeds.S1).page
    support.replace_text(page, item_price(page, 2), "13.505")
    x, y = centre_of(toggle(page, "Char kuey teow", "Aisyah"))
    page.mouse.move(x, y)
    page.mouse.down()
    assert support.active_label(page) != "Item 2 price in RM"  # the field has been left ...
    assert page.locator("p.error").count() == 0  # ... and its error waits for the release
    page.mouse.up()
    assert page.locator("p.error#price-error-i5").count() == 1
    assert toggle(page, "Char kuey teow", "Aisyah").get_attribute("aria-pressed") == "true"


@pytest.mark.parametrize("how", ["mouse", "touch", "held"])
def test_R10_a_keyboard_blur_shows_the_error_at_once_even_after_a_press(open_app, how):
    page = open_app(seed=seeds.S1, touch=how == "touch").page
    if how == "held":
        # A press that has not reported its end (the button is still down, as when its mouseup went to another window).
        # The key press that moves focus ends it, so the error must not wait for a release that may never come (WR-03).
        support.replace_text(page, item_price(page, 2), "13.505")
        x, y = centre_of(item_price(page, 2))
        page.mouse.move(x, y)
        page.mouse.down()
    else:
        press(page, how, centre_of(item_price(page, 2)))  # a finished press must not hold the next blur back
        assert support.active_label(page) == "Item 2 price in RM"
        page.keyboard.press("Control+A")
        page.keyboard.type("13.505")
    page.keyboard.press("Tab")
    assert page.locator("p.error#price-error-i5").count() == 1  # for "held", before the button comes up
    if how == "held":
        page.mouse.up()
        assert page.locator("p.error#price-error-i5").count() == 1


def test_R10_pressing_empty_space_also_waits_for_the_release(open_app):
    page = open_app().page
    support.replace_text(page, rate_field(page, "SST"), "25")
    box = page.locator("h1.wordmark").bounding_box()
    page.mouse.move(box["x"] + box["width"] + 40, box["y"] + box["height"] / 2)  # blank header space
    page.mouse.down()
    assert page.locator("p.error").count() == 0
    page.mouse.up()
    assert page.locator("p.error#rate-sst-error").count() == 1


def test_R10_a_press_that_ends_runs_each_waiting_handler_once(open_app):
    # WR-03 (mutant P1: the waiting handlers are never dropped, so every later release re-runs the old ones).
    page = open_app().page
    sub = page.locator("#subtotal")
    sub.click()
    page.keyboard.type("abc")
    box = page.locator("h1.wordmark").bounding_box()
    page.mouse.move(box["x"] + box["width"] + 40, box["y"] + box["height"] / 2)  # blank header space
    page.mouse.down()
    assert page.locator("p.error").count() == 0
    page.mouse.up()
    assert page.locator("p.error#subtotal-error").count() == 1  # the held-back blur ran once
    sub.click()
    page.keyboard.press("Control+A")
    page.keyboard.type("5")  # valid: the error goes
    page.keyboard.type("x")  # bad again, and the field still has focus, so no error until it is left
    assert page.locator("p.error").count() == 0
    page.mouse.click(*centre_of(sub))  # a press inside the focused field blurs nothing, so nothing may run
    assert page.locator("p.error").count() == 0


def test_R10_a_secondary_button_press_does_not_hold_the_error_back(open_app):
    # WR-03: a right click opens the context menu and on macOS and Linux the page gets no mouseup, so only the
    # primary button, the one that can produce a click, may hold a blur back.
    page = open_app().page
    support.replace_text(page, rate_field(page, "SST"), "25")
    box = page.locator("h1.wordmark").bounding_box()
    page.mouse.move(box["x"] + box["width"] + 40, box["y"] + box["height"] / 2)
    page.mouse.down(button="right")
    assert page.locator("p.error#rate-sst-error").count() == 1  # before any release
    page.mouse.up(button="right")


def test_R10_a_cancelled_press_releases_the_waiting_error(open_app):
    # A drag that the browser turns into a native drag ends with pointercancel and no mouseup. Playwright cannot start
    # one, so the event is dispatched on the document as the browser would (a read-only stand-in, no app hook).
    page = open_app().page
    support.replace_text(page, rate_field(page, "SST"), "25")
    box = page.locator("h1.wordmark").bounding_box()
    page.mouse.move(box["x"] + box["width"] + 40, box["y"] + box["height"] / 2)
    page.mouse.down()
    assert page.locator("p.error").count() == 0
    page.evaluate("() => document.dispatchEvent(new PointerEvent('pointercancel', { bubbles: true }))")
    assert page.locator("p.error#rate-sst-error").count() == 1  # before the button comes up
    page.mouse.up()


# ---------------------------------------------------------------- Code review CR-01, WR-01, WR-06: ghost clicks and the backdrop
# A double click or a double tap is two clicks. The first can close the dialog or remove a row, so the second lands on
# whatever is drawn under the pointer afterwards. `event.detail` is the click count: 1 for the first, 2 for the second.
PHONES = [(375, 667), (360, 640), (412, 732)]  # the sizes where QA and the code review reproduced it, with the S1 bill
# The click counts of the clicks and of the mouse presses that reach the page. The guard cancels both kinds (RG-CR-02), so a
# test of how long it lasts has to watch both: a guard that kept only its press listener changes no click.
RECORD_BODY_CLICKS_JS = """() => {
  window.testBodyClicks = [];
  window.testBodyPresses = [];
  document.body.addEventListener('click', (event) => window.testBodyClicks.push(event.detail), false);
  document.body.addEventListener('mousedown', (event) => window.testBodyPresses.push(event.detail), false);
}"""


def settle(page):
    """Two animation frames, so every click the browser still had queued from a gesture has been delivered."""
    page.evaluate("() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))")


WHOLE_DOUBLE_CLICK = {"presses": [1, 2], "clicks": [1, 2]}  # what the page sees of a real double click nobody holds back


def seen_by_the_page(page):
    """The click counts of the presses and clicks that reached the body since RECORD_BODY_CLICKS_JS. A cancelled one is missing."""
    return page.evaluate("({ presses: window.testBodyPresses, clicks: window.testBodyClicks })")


def activate_twice(page, how, point):
    """A double click (mouse) or a double tap (touch) at one point."""
    if how == "touch":
        page.touchscreen.tap(*point)
        page.touchscreen.tap(*point)
    else:
        page.mouse.dblclick(*point)
    settle(page)


def dialog_is_open(page):
    return page.locator("dialog.dialog").evaluate("(d) => d.open")


@pytest.mark.parametrize("how", ["mouse", "touch"])
@pytest.mark.parametrize("viewport", PHONES, ids=[f"{w}x{h}" for w, h in PHONES])
def test_R30_a_double_click_or_double_tap_on_cancel_changes_nothing(open_app, viewport, how):
    # CR-01 (QA F-1). On a by-item bill the control under Cancel is often a person's toggle.
    page = open_app(seed=seeds.S1, viewport=viewport, touch=how == "touch").page
    before = snapshot(page)
    open_dialog(page)
    activate_twice(page, how, centre_of(page.get_by_role("button", name="Cancel", exact=True)))
    assert dialog_is_open(page) is False and focused(page) == "New bill"
    assert stored_text(page) == seeds.S1 and snapshot(page) == before


@pytest.mark.parametrize("how", ["mouse", "touch"])
@pytest.mark.parametrize("target", ["Cancel", "Start new bill", "backdrop"])
def test_R30_the_second_click_of_a_double_activation_never_reaches_the_page(open_app, target, how):
    # The same close path serves all three clicks, and what sits under each depends on the bill and the size, so this
    # asks the question directly: of the two clicks, only the one that closed the dialog may reach the page.
    page = open_app(seed=seeds.S1, touch=how == "touch").page
    open_dialog(page)
    page.evaluate(RECORD_BODY_CLICKS_JS)
    point = (12, 12) if target == "backdrop" else centre_of(page.get_by_role("button", name=target, exact=True))
    activate_twice(page, how, point)
    assert dialog_is_open(page) is False
    assert page.evaluate("window.testBodyClicks") == [1]


def test_R30_a_triple_click_on_cancel_changes_nothing_either(open_app):
    page = open_app(seed=seeds.S1, viewport=PHONES[0]).page
    open_dialog(page)
    page.evaluate(RECORD_BODY_CLICKS_JS)
    x, y = centre_of(page.get_by_role("button", name="Cancel", exact=True))
    page.mouse.click(x, y, click_count=3)
    settle(page)
    assert page.evaluate("window.testBodyClicks") == [1] and stored_text(page) == seeds.S1


def test_R30_a_single_click_closes_as_before_and_the_next_double_click_is_not_held_back(open_app):
    page = open_app(seed=seeds.S1, viewport=PHONES[0]).page
    open_dialog(page)
    page.get_by_role("button", name="Cancel", exact=True).click()
    assert dialog_is_open(page) is False and focused(page) == "New bill"
    aisyah = toggle(page, "Char kuey teow", "Aisyah")
    assert aisyah.get_attribute("aria-pressed") == "false"
    page.evaluate(RECORD_BODY_CLICKS_JS)
    aisyah.dblclick()  # two real clicks on a toggle flip it twice: the guard of the closed dialog is gone
    settle(page)
    # The toggle alone cannot show it: swallowing both would leave it unpressed too. The presses and the clicks can.
    assert seen_by_the_page(page) == WHOLE_DOUBLE_CLICK
    assert aisyah.get_attribute("aria-pressed") == "false" and stored_text(page) == seeds.S1


def drag(page, start, end):
    """Press at `start`, move to `end` in steps and release there: a drag, such as selecting text."""
    page.mouse.move(*start)
    page.mouse.down()
    page.mouse.move(*end, steps=5)
    page.mouse.up()
    settle(page)


def test_R30_a_press_that_starts_in_the_dialog_and_ends_on_the_backdrop_keeps_it_open(open_app):
    # WR-06: the click is sent to the dialog element, which also owns the backdrop, but the user did not click the backdrop.
    page = open_app(seed=seeds.S2).page
    open_dialog(page)
    drag(page, centre_of(page.locator("#dialog-text")), (10, 10))
    assert dialog_is_open(page) is True


def test_R30_a_press_that_starts_on_the_backdrop_and_ends_in_the_dialog_keeps_it_open(open_app):
    page = open_app(seed=seeds.S2).page
    open_dialog(page)
    drag(page, (10, 10), centre_of(page.locator("#dialog-text")))
    assert dialog_is_open(page) is True


def test_R30_a_tap_on_the_backdrop_acts_as_cancel(open_app):
    page = open_app(seed=seeds.S2, touch=True).page  # a tap sends its mouse events after touchend, the press is still known
    open_dialog(page)
    page.touchscreen.tap(10, 10)
    settle(page)
    assert dialog_is_open(page) is False and focused(page) == "New bill" and stored_text(page) == seeds.S2


FIVE_PEOPLE = seeds.changed(seeds.S2, lambda d: d["bill"].update(
    people=[{"id": f"p{n}", "name": f"P{n}"} for n in range(1, 6)], nextId=6))
REMOVE_CASES = [  # (seed, the remove button, the row selector, rows before)
    pytest.param(seeds.S1, "Remove Char kuey teow", "li.item", 4, id="item-2-of-4"),
    pytest.param(FIVE_PEOPLE, "Remove P2", "li.person", 5, id="person-2-of-5"),
]


@pytest.mark.parametrize("how", ["mouse", "touch"])
@pytest.mark.parametrize("seed, button, rows, before", REMOVE_CASES)
def test_R7_a_double_click_or_double_tap_on_remove_removes_one_row(open_app, seed, button, rows, before, how):
    # WR-01: the row below slides under the pointer after the first click, and the second click removed that one too.
    page = open_app(seed=seed, touch=how == "touch").page
    assert page.locator(rows).count() == before
    activate_twice(page, how, centre_of(page.get_by_role("button", name=button, exact=True)))
    assert page.locator(rows).count() == before - 1


@pytest.mark.parametrize("seed, button, rows, before", REMOVE_CASES)
def test_R7_two_separate_clicks_and_a_key_press_still_remove_a_row_each(open_app, seed, button, rows, before):
    page = open_app(seed=seed).page
    x, y = centre_of(page.get_by_role("button", name=button, exact=True))
    page.mouse.click(x, y)
    page.mouse.click(x, y)  # a click of its own (count 1), not the tail of a double click
    assert page.locator(rows).count() == before - 2
    page.locator(rows).first.locator("button.icon-btn").focus()
    page.keyboard.press("Enter")  # a key press activates with count 0
    assert page.locator(rows).count() == before - 3


# ---------------------------------------------------------------- Security SEC-01: the repeat press on Remove (R7, R12, R34)
# A double click, a triple click or a double tap is two or three presses, and the first can move the layout under the
# pointer. Removing the last person moves "Add person" into the cell that row filled, so the second click pressed it and a
# blank person was saved (SEC-01). One guard, swallowRepeatClicks, cancels the repeat presses at the document whatever is
# under them, once the click that moved the layout has armed it. These rows name the gesture, the size and the bill, and
# check the rows, the draft and the focus.
SIZES = [(360, 640), (390, 844), (1280, 800)]
SIZE_IDS = [f"{w}x{h}" for w, h in SIZES]
GESTURES = ["single", "mouse-double", "mouse-triple", "touch-double"]  # "single" is the control: what one click does
ONE_ITEM = seeds.changed(seeds.S1, lambda d: d["bill"].update(items=d["bill"]["items"][3:]))
LAST_ROW_CASES = [  # (seed, the remove button, the row selector, where focus goes by R34 afterwards)
    pytest.param(seeds.S2, "Remove Chen", "li.person", "Person 2 name", id="S2-person-3-of-3"),
    pytest.param(seeds.S8, "Remove Mei Ling", "li.person", "Person 11 name", id="S8-person-12-of-12"),
    pytest.param(seeds.S1, "Remove Satay, 10 sticks", "li.item", "Item 3 name", id="S1-item-4-of-4"),
    pytest.param(ONE_ITEM, "Remove Satay, 10 sticks", "li.item", "Add item", id="S1-only-item"),
]


def gesture_at(page, gesture, point):
    """One of GESTURES at one point. A triple click is three presses with click counts 1, 2 and 3, as Playwright's
    `click(click_count=3)` sends them (one press with count 3 never happens)."""
    if gesture == "single":
        page.mouse.click(*point)
    elif gesture == "mouse-triple":
        page.mouse.click(*point, click_count=3)
    else:
        activate_twice(page, "touch" if gesture == "touch-double" else "mouse", point)
    settle(page)


def bill_without_last(seed, rows):
    """The bill that one click on the last row's Remove leaves: that person (or item) gone and nothing else changed."""
    bill = json.loads(seed)["bill"]
    gone = bill["people" if rows == "li.person" else "items"].pop()
    for item in bill["items"]:
        item["who"] = [person for person in item["who"] if person != gone["id"]]
    return bill


@pytest.mark.parametrize("gesture", GESTURES)
@pytest.mark.parametrize("viewport", SIZES, ids=SIZE_IDS)
@pytest.mark.parametrize("seed, button, rows, focus_after", LAST_ROW_CASES)
def test_R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing(
        open_app, seed, button, rows, focus_after, viewport, gesture):
    # SEC-01: the second click landed on "Add person" (people) and saved a blank person. The last item's second click
    # lands on inert space, so for items the focus check is what shows the guard: the press must not move focus to the body.
    page = open_app(seed=seed, viewport=viewport, touch=gesture == "touch-double").page
    before = page.locator(rows).count()
    gesture_at(page, gesture, centre_of(page.get_by_role("button", name=button, exact=True)))
    assert page.locator(rows).count() == before - 1
    assert stored(page)["bill"] == bill_without_last(seed, rows)  # no blank row, and the id counter did not move
    assert support.active_label(page) == focus_after


@pytest.mark.parametrize("how", ["mouse", "touch"])
@pytest.mark.parametrize("seed, button, rows, before", REMOVE_CASES)
def test_R34_after_a_double_click_on_remove_focus_is_where_one_click_puts_it(open_app, seed, button, rows, before, how):
    # The repeat press used to land on the next row's Remove button and move focus there (or to the body). Cancelled, it moves nothing.
    page = open_app(seed=seed, touch=how == "touch").page
    activate_twice(page, how, centre_of(page.get_by_role("button", name=button, exact=True)))
    assert support.active_label(page) == ("Item 2 name" if rows == "li.item" else "Person 2 name")


def test_R7_a_separate_click_on_what_slid_under_the_pointer_is_not_held_back(open_app):
    # The guard goes by click count, not by time or place: a click of its own (count 1) on the same spot is a new press.
    page = open_app(seed=seeds.S2).page
    point = centre_of(page.get_by_role("button", name="Remove Chen", exact=True))
    page.mouse.click(*point)
    under = page.evaluate("([x, y]) => document.elementFromPoint(x, y).closest('button').textContent.trim()", list(point))
    assert under == "Add person"  # the removal moved it under the pointer
    page.mouse.click(*point)
    assert [p["name"] for p in stored(page)["bill"]["people"]] == ["Aisyah", "Ben", ""]


def test_R7_the_guard_of_a_remove_click_ends_at_the_next_press(open_app):
    page = open_app(seed=seeds.S1, viewport=PHONES[0]).page
    page.get_by_role("button", name="Remove Nasi lemak ayam", exact=True).click()
    aisyah = toggle(page, "Char kuey teow", "Aisyah")  # item 1 now
    assert aisyah.get_attribute("aria-pressed") == "false"
    page.evaluate(RECORD_BODY_CLICKS_JS)
    aisyah.dblclick()  # two real clicks on a toggle flip it twice: the guard of the Remove click is gone
    settle(page)
    # Both presses and both clicks reached the page. The toggle alone cannot show it: swallowing both would leave it
    # unpressed too, and a guard that kept its press listener (RG-CR-02) cancels a press and changes no click.
    assert seen_by_the_page(page) == WHOLE_DOUBLE_CLICK
    assert aisyah.get_attribute("aria-pressed") == "false" and stored(page)["bill"]["items"][0]["who"] == ["p2"]


def test_R7_after_a_remove_click_a_double_click_on_a_name_still_selects_the_word(open_app):
    # The user-visible side of the same lifetime (RG-CR-02). The first press of this double click has count 1 and ends the
    # guard; a guard that kept its press listener would cancel the second press, and the word would not be selected.
    page = open_app(seed=seeds.S2).page
    page.get_by_role("button", name="Remove Chen", exact=True).click()
    person_field(page, 1).dblclick()
    selected = page.evaluate("() => { const i = document.activeElement; return i.value.slice(i.selectionStart, i.selectionEnd); }")
    assert selected == "Aisyah"


# ---------------------------------------------------------------- Regression RG-CR-01: the repeat press on Add person and Add item (R6, R12, R34)
# The guard was armed by the Remove buttons only. "Add person" fills its grid cell and the new person's row takes that cell,
# so the new row's Remove button (44 px wide, at the right end of the cell) sits under the right 44 px of the button that was
# just pressed. The repeat press of a double click, triple click or double tap then removed the blank row again: nothing was
# added, one id was spent and focus stayed on the previous name. "Add item" has no such overlap (its Remove button is at the
# other end of the row) and arms the same guard, so that one rule holds for every control that adds a row. Each row presses
# the middle of the button, or 22 px in from its right edge, which is the middle of the 44 px that the new Remove covers.
REPEAT_GESTURES = [gesture for gesture in GESTURES if gesture != "single"]
PRESS_PLACES = ["right-edge", "centre"]


def people_bill(count):
    """The S2 bill with `count` people, P1 to P{count}."""
    return seeds.changed(seeds.S2, lambda d: d["bill"].update(
        people=[{"id": f"p{n}", "name": f"P{n}"} for n in range(1, count + 1)], nextId=count + 1))


def items_bill(count):
    """The S1 bill cut to its first `count` items."""
    return seeds.changed(seeds.S1, lambda d: d["bill"].update(items=d["bill"]["items"][:count]))


def bill_after_one_add(seed, kind):
    """The bill that one click on Add person ("people") or Add item ("items") leaves: one blank row, the id counter one up."""
    bill = json.loads(seed)["bill"]
    number = bill["nextId"]
    if kind == "people":
        bill["people"].append({"id": f"p{number}", "name": ""})
    else:
        bill["items"].append({"id": f"i{number}", "name": "", "priceText": "", "who": []})
    bill["nextId"] = number + 1
    return bill


def press_point(button, place):
    """Where to press `button`: its middle, or 22 px in from its right edge (the middle of a new row's 44 px Remove button)."""
    button.scroll_into_view_if_needed()
    box = button.bounding_box()
    return box["x"] + (box["width"] - 22 if place == "right-edge" else box["width"] / 2), box["y"] + box["height"] / 2


@pytest.mark.parametrize("place", PRESS_PLACES)
@pytest.mark.parametrize("gesture", REPEAT_GESTURES)
@pytest.mark.parametrize("viewport", SIZES, ids=SIZE_IDS)
@pytest.mark.parametrize("people", [2, 3, 4, 5])
def test_R6_a_repeat_press_on_add_person_adds_one_person_and_keeps_it(open_app, people, viewport, gesture, place):
    # The "centre" rows are the control: the repeat press misses the new Remove button there, on every tree.
    seed = people_bill(people)
    page = open_app(seed=seed, viewport=viewport, touch=gesture == "touch-double").page
    gesture_at(page, gesture, press_point(page.get_by_role("button", name="Add person", exact=True), place))
    assert page.locator("li.person").count() == people + 1
    assert stored(page)["bill"] == bill_after_one_add(seed, "people")  # the blank row stayed, and one id was spent, not two
    assert support.active_label(page) == f"Person {people + 1} name"  # R34


@pytest.mark.parametrize("place", PRESS_PLACES)
@pytest.mark.parametrize("gesture", REPEAT_GESTURES)
@pytest.mark.parametrize("viewport", SIZES, ids=SIZE_IDS)
@pytest.mark.parametrize("items", [1, 4])
def test_R12_a_repeat_press_on_add_item_adds_one_item_and_never_reaches_the_page(open_app, items, viewport, gesture, place):
    # No Remove button slides under "Add item", so the bill cannot tell a guard from none. What the guard does is cancel the
    # repeat press before the page sees it, and the recorder on the body is what pins that.
    seed = items_bill(items)
    page = open_app(seed=seed, viewport=viewport, touch=gesture == "touch-double").page
    page.evaluate(RECORD_BODY_CLICKS_JS)
    gesture_at(page, gesture, press_point(page.get_by_role("button", name="Add item", exact=True), place))
    assert page.locator("li.item").count() == items + 1
    assert stored(page)["bill"] == bill_after_one_add(seed, "items")
    assert support.active_label(page) == f"Item {items + 1} name"  # R34
    assert seen_by_the_page(page) == {"presses": [1], "clicks": [1]}


# ---------------------------------------------------------------- Regression RG-CR-08: the repeat press on a chip under a price error (R7, R12)
# An amount that is not a number shows its error when its field is left, and the error line pushes everything under it down
# by one line. A blur caused by a press waits for the mouseup (RD-3), so the click on the chip that was pressed is not lost,
# but the repeat press of a double click, triple click or double tap lands on what was one line higher: for a chip at the
# right end of the first chip row that is its own item's Remove button. No click armed the guard (the pressed control was a
# chip), so the Remove has to ignore a repeat press itself. The point is found, not assumed: a scout page makes the price bad,
# leaves the field by Tab (the error shows at once) and asks, for every 4 px point of every chip as laid out before the
# error, what is under it afterwards. The press goes to the first such point on a second page whose price field still has
# focus, so the press itself causes the blur.
EIGHT_PEOPLE = seeds.changed(seeds.S1, lambda d: d["bill"].update(nextId=20, people=[
    {"id": f"p{n}", "name": name}
    for n, name in enumerate(["Aisyah", "Ben", "Chen", "Devi", "Farid", "Grace", "Hafiz", "Indra"], start=1)]))
CHIP_BOXES_JS = """() => {
  window.testChips = [...document.querySelectorAll('.who button')];
  return window.testChips.map((node, index) => { const r = node.getBoundingClientRect(); return { index, x: r.x, y: r.y, w: r.width, h: r.height }; });
}"""
OVER_ITS_OWN_REMOVE_JS = """(boxes) => {
  const found = [];
  for (const b of boxes) {
    const item = window.testChips[b.index].closest('li.item');
    for (let x = b.x + 2; x < b.x + b.w - 1; x += 4) for (let y = b.y + 2; y < b.y + b.h - 1; y += 4) {
      const under = document.elementFromPoint(x, y);
      const button = under && under.closest('button');
      if (button && /^Remove/.test(button.getAttribute('aria-label') || '') && button.closest('li.item') === item) found.push([x, y]);
    }
  }
  return found;
}"""


@pytest.mark.parametrize("gesture", REPEAT_GESTURES)
@pytest.mark.parametrize("width", [375, 390])
def test_R7_a_repeat_press_on_a_chip_under_a_pending_price_error_never_removes_the_item(open_app, width, gesture):
    scout = open_app(seed=EIGHT_PEOPLE, viewport=(width, 3000)).page  # tall: the whole bill is in view, so the scout's points are the second page's
    boxes = scout.evaluate(CHIP_BOXES_JS)
    price = scout.get_by_role("textbox", name="Item 1 price in RM", exact=True)
    price.fill("abc")
    price.press("Tab")
    settle(scout)
    landings = scout.evaluate(OVER_ITS_OWN_REMOVE_JS, boxes)
    assert landings, "no chip point lies over its own Remove once the error shows: this test no longer probes anything"
    page = open_app(seed=EIGHT_PEOPLE, viewport=(width, 3000), touch=gesture == "touch-double").page
    before = [item["id"] for item in stored(page)["bill"]["items"]]
    page.get_by_role("textbox", name="Item 1 price in RM", exact=True).fill("abc")  # focus stays: the press below blurs it
    gesture_at(page, gesture, landings[0])
    assert [item["id"] for item in stored(page)["bill"]["items"]] == before  # no item went


# ---------------------------------------------------------------- Security I-1: the repeat press on New bill (R29, R30)
# Opening the dialog puts its backdrop under the pointer, so the second click of a double click, triple click or double tap
# on "New bill" closed it again: the dialog flashed open and shut. Opening arms the same guard as closing does.
@pytest.mark.parametrize("gesture", ["mouse-double", "mouse-triple", "touch-double"])
@pytest.mark.parametrize("viewport", SIZES, ids=SIZE_IDS)
def test_R29_a_repeat_press_on_new_bill_leaves_the_dialog_open(open_app, viewport, gesture):
    page = open_app(seed=seeds.S1, viewport=viewport, touch=gesture == "touch-double").page
    page.evaluate(RECORD_BODY_CLICKS_JS)
    gesture_at(page, gesture, centre_of(new_bill_button(page)))
    assert dialog_is_open(page) is True and focused(page) == "Cancel"
    assert page.evaluate("window.testBodyClicks") == [1] and stored_text(page) == seeds.S1


@pytest.mark.parametrize("close", ["cancel", "backdrop", "escape"])
def test_R30_after_a_double_click_on_new_bill_one_deliberate_click_still_closes_it(open_app, close):
    page = open_app(seed=seeds.S1).page
    gesture_at(page, "mouse-double", centre_of(new_bill_button(page)))
    assert dialog_is_open(page) is True
    if close == "cancel":
        page.get_by_role("button", name="Cancel", exact=True).click()
    elif close == "backdrop":
        page.mouse.click(10, 10)
    else:
        page.keyboard.press("Escape")
    assert dialog_is_open(page) is False and focused(page) == "New bill" and stored_text(page) == seeds.S1


def test_R29_opening_by_keyboard_and_opening_again_straight_away_is_not_held_back(open_app):
    page = open_app(seed=seeds.S2).page
    new_bill_button(page).focus()
    page.keyboard.press("Enter")  # a key press activates with click count 0, which the guard lets through
    assert dialog_is_open(page) is True and focused(page) == "Cancel"
    page.keyboard.press("Enter")
    assert dialog_is_open(page) is False and focused(page) == "New bill"
    page.keyboard.press("Enter")
    assert dialog_is_open(page) is True and focused(page) == "Cancel"


def test_R29_the_guard_of_opening_ends_at_the_next_press(open_app):
    page = open_app(seed=seeds.S1, viewport=PHONES[0]).page
    open_dialog(page)
    page.keyboard.press("Escape")
    ben = toggle(page, "Nasi lemak ayam", "Ben")
    assert ben.get_attribute("aria-pressed") == "false"
    page.evaluate(RECORD_BODY_CLICKS_JS)
    ben.dblclick()  # two real clicks on a toggle flip it twice: nothing is left of the guard
    settle(page)
    # Both presses and both clicks reached the page. The toggle alone cannot show it: swallowing both would leave it
    # unpressed too.
    assert seen_by_the_page(page) == WHOLE_DOUBLE_CLICK
    assert ben.get_attribute("aria-pressed") == "false" and stored_text(page) == seeds.S1


# ---------------------------------------------------------------- Task 11: cross-cutting checks (R32, R33, R35, R36, R37, R39)
INK = "rgb(20, 25, 23)"  # --ink, the colour of the focus ring
RING = ["solid", "2px", INK, "2px"]
MODE_DOUBLE_RING = "rgb(253, 254, 253) 0px 0px 0px 3px inset, rgb(20, 25, 23) 0px 0px 0px 5px inset"
FOCUS_JS = """() => {
  const el = document.activeElement;
  const ring = (node) => { const s = getComputedStyle(node); return [s.outlineStyle, s.outlineWidth, s.outlineColor, s.outlineOffset]; };
  const field = el.closest('.field'), mode = el.closest('fieldset.mode');  // li.field.person or span.field
  return {
    name: el.getAttribute('aria-label') || (el.labels && el.labels.length ? el.labels[0].textContent.trim() : '') || el.textContent.trim(),
    visible: el.matches(':focus-visible'), kind: el.type || el.tagName.toLowerCase(), self: ring(el),
    field: field && ring(field), mode: mode && ring(mode),
    labelRing: mode ? getComputedStyle(el.labels[0]).boxShadow : null,
    personRemove: el.tagName === 'BUTTON' && !!el.closest('li.person'),
  };
}"""
TABBABLE_JS = """() => [...document.querySelectorAll('button, input')].filter((el) =>
  !el.disabled && el.getClientRects().length > 0 && (el.type !== 'radio' || el.checked)).length"""
S1_TAB_ORDER = ["New bill", "Person 1 name", "Remove Aisyah", "Person 2 name", "Remove Ben", "Person 3 name", "Remove Chen",
                "Add person", "By item"]
for _number, (_name, _price, _people) in enumerate(S1_ITEMS, start=1):
    S1_TAB_ORDER += [f"Item {_number} name", f"Item {_number} price in RM", f"Remove {_name}", "Aisyah", "Ben", "Chen"]
S1_TAB_ORDER += ["Add item", "Service charge in percent", "SST in percent", "Copy summary"]
TAB_CASES = [
    pytest.param(None, ["New bill", "Person 1 name", "Person 2 name", "Add person", "Even", "Subtotal in RM",
                        "Service charge in percent", "SST in percent"], id="S3"),
    pytest.param(seeds.S1, S1_TAB_ORDER, id="S1"),
    pytest.param(seeds.UNREADABLE["B1"], ["New bill", "Dismiss note", "Person 1 name", "Person 2 name", "Add person", "Even",
                                          "Subtotal in RM", "Service charge in percent", "SST in percent"], id="S7"),
]


def ring_problem(stop):
    """What is wrong with the ring of one Tab stop, or None (qa.md R32)."""
    if not stop["visible"]:
        return "not :focus-visible"
    if stop["kind"] == "radio":  # drawn on fieldset.mode, plus the double ring inside the label
        return None if stop["mode"] == RING and stop["labelRing"] == MODE_DOUBLE_RING else f"mode {stop['mode']} {stop['labelRing']}"
    if stop["kind"] == "text":  # drawn on span.field, never on the input
        return None if stop["field"] == RING and stop["self"][0] == "none" else f"field {stop['field']} input {stop['self']}"
    expected = ["solid", "2px", INK, "-3px"] if stop["personRemove"] else RING  # inset on the person remove button
    return None if stop["self"] == expected else f"control {stop['self']}"


@pytest.mark.parametrize("seed, order", TAB_CASES)
def test_R32_tab_order_follows_the_golden_and_every_stop_shows_its_ring(open_app, seed, order):
    page = open_app(seed=seed).page
    assert page.evaluate(TABBABLE_JS) == len(order)  # nothing reachable is left out of the list, disabled ones are not in it
    stops = []
    for _ in order:
        page.keyboard.press("Tab")
        stops.append(page.evaluate(FOCUS_JS))
    assert [stop["name"] for stop in stops] == order
    assert [(stop["name"], ring_problem(stop)) for stop in stops if ring_problem(stop)] == []


def test_R32_the_ring_check_has_teeth():
    good = {"visible": True, "kind": "text", "self": ["none", "0px", INK, "0px"], "field": RING, "mode": None, "labelRing": None, "personRemove": False}
    assert ring_problem(good) is None
    assert ring_problem(dict(good, visible=False)) and ring_problem(dict(good, field=["none", "0px", INK, "0px"]))
    assert ring_problem(dict(good, kind="button", self=RING, personRemove=True))  # needs -3px
    assert ring_problem(dict(good, kind="radio", mode=RING, labelRing="none"))


@pytest.mark.parametrize("seed, field_of, text", [
    (seeds.S2, subtotal_field, "100.00"),
    (seeds.S1, lambda page: rate_field(page, "Service charge"), "12.5"),
], ids=["subtotal", "service-charge"])
def test_R33_typing_in_an_amount_or_a_rate_keeps_focus_and_caret(open_app, seed, field_of, text):
    page = open_app(seed=seed).page
    type_and_watch(page, field_of(page), text)


LAYOUT_JS = """() => {
  const tape = document.querySelector('div.tape'), inputs = document.querySelector('div.inputs');
  return {
    overflow: document.documentElement.scrollWidth - window.innerWidth,
    columns: getComputedStyle(document.querySelector('section[aria-labelledby=h-people] ul.cells')).gridTemplateColumns.split(' ').length,
    tapeTop: tape.getBoundingClientRect().top, tapeLeft: tape.getBoundingClientRect().left, position: getComputedStyle(tape).position,
    chargesBottom: document.querySelector('section[aria-labelledby=h-charges]').getBoundingClientRect().bottom,
    inputsRight: inputs.getBoundingClientRect().right,
  };
}"""
LAYOUT_CASES = [
    pytest.param("S1", seeds.S1, (360, 780), 2, "after", id="S1-360"),
    pytest.param("S2", seeds.S2, (360, 780), 2, "after", id="S2-360"),
    pytest.param("S3", None, (360, 780), 2, "after", id="S3-360"),
    pytest.param("S5", seeds.S5, (360, 780), 2, "after", id="S5-360"),
    pytest.param("S1", seeds.S1, (390, 844), 2, "after", id="S1-390"),
    pytest.param("S1", seeds.S1, (1280, 800), 3, "right", id="S1-1280"),
    pytest.param("S3", None, (1280, 800), 3, "right", id="S3-1280"),
    pytest.param("M1", seeds.S2, (360, 780), 2, "after", id="M1-360"),
]


@pytest.mark.parametrize("state, seed, viewport, columns, panel", LAYOUT_CASES)
def test_R35_no_horizontal_overflow_and_the_layout_of_each_size(open_app, state, seed, viewport, columns, panel):
    page = open_app(seed=seed, viewport=viewport).page
    if state == "M1":
        open_dialog(page)
    found = page.evaluate(LAYOUT_JS)
    assert found["overflow"] <= 0, found
    assert found["columns"] == columns
    if panel == "after":  # under 1024 px the panel sits after the Charges block
        assert found["tapeTop"] >= found["chargesBottom"] - 0.5 and found["tapeLeft"] < found["inputsRight"]
    else:  # from 1024 px it is in the right column and sticky
        assert found["tapeLeft"] >= found["inputsRight"] - 0.5 and found["position"] == "sticky"


def test_R35_sizes_the_design_gives_at_360_by_780(open_app):
    page = open_app(seed=seeds.S2, clipboard="reject", viewport=(360, 780)).page
    assert page.locator("span.field.money:has(#subtotal)").bounding_box()["width"] == 160  # S2-28, bill-even.md
    copy_summary(page)
    status = page.locator("p.status.status-failure")
    box = status.bounding_box()
    assert status.inner_text() == FAILED_COPY and status.evaluate("(e) => getComputedStyle(e).textAlign") == "center"
    assert box["height"] == 40  # two 20 px lines (ST-14)
    assert status.evaluate("(e) => e.scrollWidth <= e.clientWidth") and box["x"] + box["width"] <= 360
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    dialog = open_dialog(page)
    assert dialog.bounding_box()["width"] == 328 and page.locator("p.dialog-text").bounding_box()["height"] == 48  # M1-09
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


def test_R35_content_width_of_the_header_and_the_note_at_1280_by_800(open_app):
    page = open_app(seed=seeds.UNREADABLE["B1"], viewport=(1280, 800)).page
    assert page.locator("div.note").bounding_box()["width"] == 1040  # ST-15
    bar = page.locator("header.bar")
    assert bar.bounding_box()["width"] == 1104
    assert bar.evaluate("(e) => [getComputedStyle(e).paddingLeft, getComputedStyle(e).paddingRight]") == ["32px", "32px"]


WATCH_TRANSITIONS_JS = """() => { window.testTransitions = [];
  document.addEventListener('transitionrun', (event) => window.testTransitions.push(event.propertyName), true); }"""


@pytest.mark.parametrize("setting, duration", [("reduce", "0s"), ("no-preference", "0.12s, 0.12s")])
def test_R36_motion_follows_the_users_setting(open_app, setting, duration):
    page = open_app(seed=seeds.S1, reduced_motion=setting).page
    for selector in (".btn", ".tap", ".icon-btn", ".mode label"):
        found = page.eval_on_selector_all(selector, "(els) => els.map((e) => getComputedStyle(e).transitionDuration)")
        assert found and set(found) == {duration}, selector
    assert page.evaluate("document.getAnimations().length") == 0  # nothing animates by itself
    page.evaluate(WATCH_TRANSITIONS_JS)
    toggle(page, "Mee goreng mamak", "Ben").click()
    right_after = page.evaluate("() => document.getAnimations().map((a) => [a.constructor.name, a.transitionProperty])")
    # The transitionrun events are sent with the next frame, so the list is read after two of them.
    page.evaluate("() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))")
    started = page.evaluate("window.testTransitions")
    if setting == "reduce":
        assert right_after == [] and started == []
    else:  # the colour change of the toggle runs, and it is the only thing that does
        assert right_after and all(kind == "CSSTransition" and prop in ("background-color", "color") for kind, prop in right_after)
        assert started and set(started) <= {"background-color", "color"}
    page.wait_for_timeout(500)
    assert page.evaluate("document.getAnimations().length") == 0


PERSON_PAYLOAD, ITEM_PAYLOAD, SCRIPT_PAYLOAD = "<svg onload=f()>", "<img src=x onerror=alert(1)>", '"><script>alert(2)</script>'


def test_R37_names_are_shown_as_text_and_never_as_markup(open_app):
    page = open_app(seed=seeds.S1).page
    dialogs = []
    page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.dismiss()))
    svgs_before = page.locator("body svg").count()
    support.replace_text(page, person_field(page, 1), PERSON_PAYLOAD)
    support.replace_text(page, item_name(page, 1), ITEM_PAYLOAD)
    support.replace_text(page, item_name(page, 2), SCRIPT_PAYLOAD)
    assert person_field(page, 1).input_value() == PERSON_PAYLOAD and len(PERSON_PAYLOAD) == 16  # nothing cut by maxlength 20
    assert item_name(page, 1).input_value() == ITEM_PAYLOAD and len(ITEM_PAYLOAD) == 28
    assert item_name(page, 2).input_value() == SCRIPT_PAYLOAD
    assert page.get_by_role("button", name=PERSON_PAYLOAD, exact=True).count() == 4  # that person's toggle in every item
    assert table_cells(page, "tbody")[0][0] == PERSON_PAYLOAD
    assert remove_button(page, PERSON_PAYLOAD).count() == 1
    assert page.get_by_role("button", name=f"Remove {ITEM_PAYLOAD}", exact=True).count() == 1
    assert who_group(page, ITEM_PAYLOAD).count() == 1 and who_group(page, SCRIPT_PAYLOAD).count() == 1
    found = page.evaluate("""() => ({
      markup: document.body.querySelectorAll('img, script').length,
      handlers: document.querySelectorAll('[onload], [onerror], [onclick]').length,
      svgClasses: [...document.querySelectorAll('body svg')].map((svg) => svg.getAttribute('class')),
    })""")
    assert found["markup"] == 0 and found["handlers"] == 0
    assert len(found["svgClasses"]) == svgs_before and set(found["svgClasses"]) == {"ph"}  # every svg is still an icon
    copy_summary(page)
    assert page.evaluate("window.testClipboardText").split("\n")[2] == f"{PERSON_PAYLOAD} RM 29.04"
    assert dialogs == []  # no alert ran


BANNED_APIS = ["innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function(", "createContextualFragment", "DOMParser"]
SET_ATTRIBUTE_ON = re.compile(r"""setAttribute\(\s*["'`]on""")
NETWORK_APIS = ["fetch(", "XMLHttpRequest", "WebSocket", "EventSource", "sendBeacon", "serviceWorker"]
SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://")
SVG_NAMESPACE = "http://www.w3.org/2000/svg"
NAMESPACE_CALLS = re.compile(r"""createElementNS\(\s*(["'`])""" + re.escape(SVG_NAMESPACE) + r"\1")


def banned_api_problems(name, text):
    found = [f"{token} in {name}" for token in BANNED_APIS if token in text]
    found += [f"setAttribute(on...) in {name}"] if SET_ATTRIBUTE_ON.search(text) else []
    return found + ([f"<template in {name}"] if "<template" in text else [])


def network_problems(name, text):
    found = [f"{token} in {name}" for token in NETWORK_APIS if token in text]
    without_icons = NAMESPACE_CALLS.sub("", text)  # the one allowed use of a scheme string (CG-10)
    found += [f"scheme string {match.group(0)} in {name}" for match in SCHEME.finditer(without_icons)]
    return found + ([f"namespace outside createElementNS in {name}"] if SVG_NAMESPACE in without_icons else [])


def test_R37_no_banned_api_in_the_shipped_files():
    scanned = {name: text for name, text in support.shipped_text().items() if name == "index.html" or name.startswith("src/")}
    assert len(scanned) > 15
    problems = []
    for name, text in scanned.items():
        problems += banned_api_problems(name, text)
    assert problems == []


def test_R37_the_banned_api_scan_has_teeth():
    for bad in ["el.innerHTML = x", "a.outerHTML", "insertAdjacentHTML('x')", "document.write(1)", "eval(x)", "new Function('a')",
                "el.setAttribute('onclick', f)", 'el.setAttribute("onload", f)', "range.createContextualFragment(x)", "new DOMParser()", "<template id=t>"]:
        assert banned_api_problems("x.js", bad), bad
    assert banned_api_problems("x.js", "el.setAttribute('aria-label', x); el.textContent = y") == []


def test_R39_nothing_leaves_the_device_by_the_static_scan():
    problems = []
    for name, text in support.shipped_text().items():
        problems += network_problems(name, text)
    assert problems == []
    assert "://" not in (ROOT / "index.html").read_text(encoding="utf-8")


def test_R39_the_network_scan_has_teeth():
    ok = f'const node = document.createElementNS("{SVG_NAMESPACE}", tag);'
    assert network_problems("icons.js", ok) == []
    assert network_problems("icons.js", ok.replace('"', "'")) == [] and network_problems("icons.js", ok.replace('"', "`")) == []
    for bad in ["fetch('/x')", "new XMLHttpRequest()", "new WebSocket(u)", "new EventSource(u)", "navigator.sendBeacon(u)",
                "navigator.serviceWorker", "const u = 'https://example.com/a'", "import x from 'http://a.b/c.js'",
                f'document.createElementNS("urn:other", "svg"); // {SVG_NAMESPACE}', f'const ns = "{SVG_NAMESPACE}";',
                f'document.createElementNS(tag, "{SVG_NAMESPACE}")', f"// the icons use createElementNS and {SVG_NAMESPACE}"]:
        assert network_problems("x.js", bad), bad


def test_R39_icons_come_from_createElementNS_and_the_page_holds_its_icons(open_app):
    sources = {name: text for name, text in support.shipped_text().items() if name.startswith("src/")}
    calls = sum(text.count("createElementNS(") for text in sources.values())
    assert calls >= 1 and calls == sum(len(NAMESPACE_CALLS.findall(text)) for text in sources.values())  # every call names the namespace
    page = open_app(seed=seeds.S1).page
    icons = page.evaluate("""() => [...document.querySelectorAll('svg.ph')].map((svg) => ({
      place: svg.closest('button.copy') ? 'copy' : svg.closest('tfoot') ? 'check' : svg.closest('.btn-outline') ? 'plus' : svg.closest('.icon-btn') ? 'x' : '?',
      viewBox: svg.getAttribute('viewBox'), hidden: svg.getAttribute('aria-hidden'), focusable: svg.getAttribute('focusable'),
      paths: svg.children.length, namespace: svg.namespaceURI }))""")
    assert len(icons) == 11 and sorted(icon["place"] for icon in icons) == ["check"] + ["copy"] + ["plus"] * 2 + ["x"] * 7
    assert all(icon["viewBox"] == "0 0 256 256" and icon["hidden"] == "true" and icon["focusable"] == "false" and icon["paths"] == 1
               and icon["namespace"] == SVG_NAMESPACE for icon in icons)


def test_R39_a_whole_session_makes_only_same_origin_gets(open_app):
    session = open_app()
    page = session.page
    build_s1(page)
    copy_summary(page)
    open_dialog(page)
    page.get_by_role("button", name="Cancel").click()
    page.reload()
    paths = {url[len(session.base):] for method, url in session.requests if method == "GET" and url.startswith(session.base)}
    assert {"/", "/src/system.css", "/src/main.js"} <= paths
    assert all(session.request_is_allowed(method, url) for method, url in session.requests)
    assert session.problems() == []


# ---------------------------------------------------------------- Task 12: the fidelity setup and runner (R40)
# The gate itself is `python tests/browser/fidelity/run.py` (it takes about a minute and writes its evidence). These tests keep
# its inputs honest: the seed scripts equal the seeds, they boot the app through its own load path, and the runner follows CG-11.
FIDELITY_DIR = ROOT / "tests" / "browser" / "fidelity"
SEED_SCRIPT = re.compile(r"""\AlocalStorage\.setItem\("split\.draft", '([^'\\]*)'\);\n\Z""")


def load_runner():
    import importlib.util
    spec = importlib.util.spec_from_file_location("fidelity_run", FIDELITY_DIR / "run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.xfail(strict=True, reason="task A19")
@pytest.mark.parametrize("name, seed", [("seed-s1.js", seeds.S1), ("seed-s2.js", seeds.S2), ("seed-s5.js", seeds.S5)])
def test_R40_fidelity_seeds_match(name, seed):
    match = SEED_SCRIPT.match((FIDELITY_DIR / name).read_text(encoding="utf-8"))
    assert match, f"{name} must be exactly one localStorage.setItem statement"
    assert match.group(1) == seed  # the very text of seeds.py, byte for byte


@pytest.mark.xfail(strict=True, reason="task A19")
@pytest.mark.parametrize("name, seed", [("seed-s1.js", seeds.S1), ("seed-s2.js", seeds.S2), ("seed-s5.js", seeds.S5)])
def test_R40_a_seed_script_boots_the_app_through_its_own_load_path(open_app, name, seed):
    session = open_app(init_scripts=[(FIDELITY_DIR / name).read_text(encoding="utf-8")], allow_problems=True)
    scripted = session.page
    assert snapshot(scripted) == snapshot(open_app(seed=seed).page)
    assert page_has_no_note(scripted) and stored_text(scripted) == seed  # read as it is, never rewritten
    # An init script also runs in the blank first document, where storage is denied. The harness never shows that
    # error, the suite does, so it is the one problem this test accepts.
    assert [p for p in session.problems() if "Failed to read the 'localStorage' property" not in p] == []


def page_has_no_note(page):
    return page.locator("div.note").count() == 0


def test_R40_the_open_new_bill_script_leaves_the_dialog_open_without_a_ring(open_app):
    page = open_app(seed=seeds.S2).page
    page.evaluate(f"async () => {{ {(FIDELITY_DIR / 'open-new-bill.js').read_text(encoding='utf-8')}\n }}")  # as the harness runs it
    assert page.locator("dialog.dialog").evaluate("(d) => d.open && d.matches(':modal')")
    assert page.evaluate("document.activeElement === document.body && document.querySelectorAll(':focus-visible').length === 0")
    assert stored_text(page) == seeds.S2  # opening the dialog changes nothing


def test_R40_the_runner_uses_the_python_that_runs_pytest():
    source = (FIDELITY_DIR / "run.py").read_text(encoding="utf-8")
    assert "[sys.executable, str(HARNESS)" in source
    assert not re.search(r"\bpip\b|ensurepip|\bvenv\b|\.sdlc-harness|virtualenv", source)  # no environment, no installer
    import importlib
    for module in ("playwright", "PIL", "numpy"):  # the harness needs these, and the Python that runs this test has them
        importlib.import_module(module)


def test_R40_the_runner_takes_the_harness_from_the_environment_and_has_a_default():
    runner = load_runner()
    assert runner.harness_path({}) == runner.DEFAULT_HARNESS
    assert runner.harness_path({"SDLC_HARNESS": ""}) == runner.DEFAULT_HARNESS  # a blank variable is not a path
    assert runner.harness_path({"SDLC_HARNESS": "elsewhere/fidelity.py"}) == Path("elsewhere/fidelity.py")
    assert runner.HARNESS == runner.harness_path(os.environ)  # what the module picked at import


@pytest.mark.parametrize("screen, seed, after_load", [
    ("bill-empty", None, None), ("bill-even", "seed-s2.js", None), ("bill-items", "seed-s1.js", None),
    ("bill-unassigned", "seed-s5.js", None), ("new-bill-dialog", "seed-s2.js", "open-new-bill.js")])
def test_R40_the_runner_builds_the_documented_command(screen, seed, after_load):
    runner = load_runner()
    cmd = runner.command("http://127.0.0.1:1", screen, seed, after_load, "390x844", Path("out"))
    assert cmd[:2] == [sys.executable, str(runner.HARNESS)]
    assert cmd[cmd.index("--golden") + 1] == f"./docs/design/{screen}.html" and cmd[cmd.index("--candidate") + 1] == "http://127.0.0.1:1/"
    for flag, value in (("--viewport", "390x844"), ("--dpr", "1"), ("--color-scheme", "light"),
                        ("--fixed-time", "2026-10-08T09:00:00"), ("--threshold", "0.01")):
        assert cmd[cmd.index(flag) + 1] == value, flag
    assert "--browser-arg=--disable-lcd-text" in cmd
    assert ("--candidate-init-script" in cmd) == bool(seed) and ("--candidate-after-load" in cmd) == bool(after_load)
    if seed:
        assert cmd[cmd.index("--candidate-init-script") + 1] == f"./tests/browser/fidelity/{seed}"
    assert "--no-full-page" not in cmd
    assert len(runner.SCREENS) * len(runner.VIEWPORTS) == 10 and runner.VIEWPORTS == ("390x844", "1280x800")


# ---------------------------------------------------------------- Task 13: the cold-boot live gate (R41)
# The gate itself is `python tests/browser/live_e2e.py` (a few seconds, writes qa/live-e2e/<ts>/). These tests keep its
# script honest without running a second browser inside this one: what it expects, how it labels its steps, and that
# it uses real gestures only.
LIVE_SCRIPT = ROOT / "tests" / "browser" / "live_e2e.py"
ACTION_WORDS = {"open", "replace", "click", "close", "type", "press", "tap", "reload", "no"}


def live_gate_steps():
    tree = ast.parse(LIVE_SCRIPT.read_text(encoding="utf-8"))
    return [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "step" and isinstance(node.func.value, ast.Name) and node.func.value.id == "gate"]


def test_R41_the_step_log_puts_gesture_and_assertion_in_their_own_fields():
    import live_e2e
    assert live_e2e.format_step(3, "click it", "it is open", "PASS") == "03 | gesture: click it | assertion: it is open | PASS"
    steps = live_gate_steps()
    assert [call.args[0].value for call in steps] == [1, 2, 3, 4, 5, 6, 7]  # one call per numbered step of qa.md
    for call in steps:
        fields = {keyword.arg: keyword.value.value if isinstance(keyword.value, ast.Constant) else None for keyword in call.keywords}
        gesture, assertion = fields["gesture"], fields["assertion"]
        assert gesture and assertion, call.args[1].value
        assert gesture.split()[0] in ACTION_WORDS, f"step {call.args[0].value}: the gesture field holds {gesture!r}"
        assert assertion.split()[0] not in ACTION_WORDS, f"step {call.args[0].value}: the assertion field holds {assertion!r}"


def test_R41_the_gate_installs_the_clipboard_recorder_and_nothing_else():
    import live_e2e
    assert live_e2e.INIT_SCRIPTS == ["tests/browser/clipboard/recorder.js"]  # the recorder is the one init script (CG-7)


READS_ONLY = {"STATE_JS", "ITEMS_JS", "SUMMARY_JS", "TABLE_JS", "ACTIVE_JS"}
READ_EXPRESSIONS = {"window.testClipboardText", "window.testClipboardWrites", "localStorage.getItem('split.draft')",
                    "() => !Clipboard.prototype.writeText.toString().includes('[native code]')",
                    "(d) => d.matches(':modal')", "(d) => d.open"}


def test_R41_the_gate_uses_real_gestures_and_reads_only():
    source = LIVE_SCRIPT.read_text(encoding="utf-8")
    tree = ast.parse(source)
    keywords = {node.arg for node in ast.walk(tree) if isinstance(node, ast.keyword)}
    attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert not keywords & {"storage_state", "bypass_csp", "permissions"}  # a cold context, the strict policy live, no permission
    assert not attributes & {"fill", "dispatch_event", "check", "set_checked", "select_option", "route", "add_init_script",
                             "launch_persistent" + "_context"}  # no shortcut that is not a gesture
    made = "new" + "_context("  # spelled in two parts so test_R39_only_the_rig_makes_browser_contexts does not flag this file
    assert source.count("rig." + made) == 1 and source.count(made) == 1  # the one context comes from the rig
    seen = [node.args[0].id if isinstance(node.args[0], ast.Name) else node.args[0].value for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "evaluate"]
    assert seen and all(item in READS_ONLY | READ_EXPRESSIONS for item in seen), sorted(set(seen) - READS_ONLY - READ_EXPRESSIONS)


# ---------------------------------------------------------------- v1.1.0 task A0: the engine switch (R58)
BROWSER_DIR = ROOT / "tests" / "browser"
BROWSER_ENTRY_POINTS = {"launch", "launch_persistent" + "_context", "launch_server", "connect", "connect_over_cdp"}


class OptionRecorder:
    """Stands in for pytest's parser, so conftest.pytest_addoption can be called and its options read."""

    def __init__(self):
        self.options = {}

    def addoption(self, *names, **settings):
        self.options.update({name: settings for name in names})


def python_files_beside_the_rig():
    return [path for path in BROWSER_DIR.rglob("*.py") if path.name != "rig.py"]


def test_R58_the_engine_option_and_the_one_launch_place(request, pytestconfig):
    import conftest
    import live_e2e
    assert callable(getattr(conftest, "pytest_addoption", None)), "conftest.py adds --engine"
    parser = OptionRecorder()
    conftest.pytest_addoption(parser)
    engine_option = parser.options.get("--engine", {})
    assert list(engine_option.get("choices", ())) == ["chromium", "webkit"] and engine_option.get("default") == "chromium"
    assert request.getfixturevalue("engine") == pytestconfig.getoption("engine")
    assert any(line.startswith("chromium_only(reason") for line in pytestconfig.getini("markers"))
    assert live_e2e.parse_args([]).engine == "chromium" and live_e2e.parse_args(["--engine", "webkit"]).engine == "webkit"
    with pytest.raises(SystemExit):
        live_e2e.parse_args(["--engine", "firefox"])
    assert "--engine" not in (BROWSER_DIR / "fidelity" / "run.py").read_text(encoding="utf-8")  # fidelity is Chromium only
    passed = [f"{path.name}: {node.arg}" for path in python_files_beside_the_rig()
              for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
              if isinstance(node, ast.keyword) and node.arg in ("is_mobile", "bypass_csp")]
    assert passed == []


def test_R58_only_the_rig_launches_a_browser():
    offenders = []
    for path in python_files_beside_the_rig():
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            is_rig_launch = isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "rig"
            if isinstance(node, ast.Attribute) and node.attr in BROWSER_ENTRY_POINTS and not is_rig_launch:
                offenders.append(f"{path.relative_to(BROWSER_DIR).as_posix()}: .{node.attr}")
    assert offenders == []


def test_R58_the_rig_launches_headless_with_the_arguments_of_its_engine():
    assert callable(getattr(rig, "launch", None)), "rig.launch(playwright, engine) is the one launch place"

    class BrowserType:
        def __init__(self):
            self.calls = []

        def launch(self, **settings):
            self.calls.append(settings)
            return "a browser"

    playwright = type("Playwright", (), {})()
    playwright.chromium, playwright.webkit = BrowserType(), BrowserType()
    assert rig.ENGINES == ("chromium", "webkit") and set(rig.LAUNCH_ARGS) == set(rig.ENGINES)
    assert rig.launch(playwright, "webkit") == "a browser"
    assert playwright.webkit.calls == [{"headless": True, "args": rig.LAUNCH_ARGS["webkit"]}] and playwright.chromium.calls == []
    with pytest.raises(ValueError):
        rig.launch(playwright, "firefox")


# ===== END OF TESTS (new tests go above this line) =====
