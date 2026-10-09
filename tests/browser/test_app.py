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


# ---------------------------------------------------------------- Task 4: mode and subtotal (R8, R9, R10)
EVEN_MESSAGE = "Shares\nEnter the subtotal to see the shares."


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


# Rows are added with the field's own task: item prices (task 5), Service charge and SST (task 6).
ERROR_CASES = [
    pytest.param(lambda page: None, lambda page: page.locator("#subtotal"), "0", "Enter an amount like 12.50", "subtotal-error", "12.50", id="subtotal"),
    pytest.param(lambda page: build_s1(page), lambda page: item_price(page, 2), "13.505", "Enter an amount like 12.50", "price-error-i5", "13.50", id="item-price"),
    pytest.param(lambda page: None, lambda page: rate_field(page, "Service charge"), "31", "Enter a rate from 0 to 30", "rate-service-error", "10", id="service"),
    pytest.param(lambda page: None, lambda page: rate_field(page, "SST"), "20.01", "Enter a rate from 0 to 20", "rate-sst-error", "6", id="sst"),
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
S1_ITEMS = [("Nasi lemak ayam", "15.90", ["Aisyah"]), ("Char kuey teow", "13.50", ["Ben"]),
            ("Mee goreng mamak", "12.00", ["Chen"]), ("Satay, 10 sticks", "18.00", ["Aisyah", "Chen"])]


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
    assert panel_text(page) == "Shares\nGive every item a price to see the shares."
    for _ in range(49):
        add.click()
    assert page.locator("li.item").count() == 50 and add.is_disabled()
    specimen = support.open_golden(plain_context, "states").locator('section[aria-labelledby="spec-s8a"] button[disabled]')
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
    specimen = support.open_golden(plain_context, "states").locator("#s4-price-error")
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
    specimen = support.open_golden(plain_context, "states").locator("#s4-subtotal-error")  # ST-10: styled as ST-01
    assert support.specimen_props(error, ["marginTop"]) == support.specimen_props(specimen, ["marginTop"])


def test_R10_an_empty_rate_never_shows_an_error(open_app):
    page = open_app().page
    support.replace_text(page, rate_field(page, "Service charge"), "")
    page.keyboard.press("Tab")
    assert page.locator("p.error").count() == 0 and page.locator("[aria-invalid]").count() == 0
    assert panel_text(page) == "Shares\nCheck the charges to see the shares."


# ---------------------------------------------------------------- Task 7: the bill panel (R3, R16 to R21)
S1_SUMMARY = [["Subtotal", "RM 59.40", ""], ["+Service charge", "RM 5.94", "10% of RM 59.40"],
              ["+SST", "RM 3.92", "6% of RM 65.34"], ["=Total", "RM 69.26", ""]]
S2_SUMMARY = [["Subtotal", "RM 100.00", ""], ["+Service charge", "RM 10.00", "10% of RM 100.00"],
              ["+SST", "RM 6.60", "6% of RM 110.00"], ["=Total", "RM 116.60", ""]]
S1_ROWS = [["Aisyah", "RM 24.90", "RM 4.14", "RM 29.04"], ["Ben", "RM 13.50", "RM 2.24", "RM 15.74"],
           ["Chen", "RM 21.00", "RM 3.48", "RM 24.48"]]
S1_CHECK = [["Adds up to", "RM 59.40", "RM 9.86", "RM 69.26"]]
S2_ROWS = [["Aisyah", "RM 38.87"], ["Ben", "RM 38.87"], ["Chen", "RM 38.86"]]
S2_CHECK = [["Adds up to", "RM 116.60"]]
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
    assert first_diff(dom_walk(page), golden_walk(plain_context, golden)) is None, state


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
                 "Give every item a price to see the shares.", id="item-unpriced"),
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
S2_COPY = ("Bill split\nTotal RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)\n"
           "Aisyah RM 38.87\nBen RM 38.87\nChen RM 38.86\nAdds up to RM 116.60")
S1_COPY = ("Bill split\nTotal RM 69.26 (subtotal RM 59.40, service 10% RM 5.94, SST 6% RM 3.92)\n"
           "Aisyah RM 29.04\nBen RM 15.74\nChen RM 24.48\nAdds up to RM 69.26")
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
NEW_BILL_DRAFT = ('{"version":1,"bill":{"mode":"even","people":[{"id":"p1","name":"Person 1"},{"id":"p2","name":"Person 2"}],'
                  '"subtotalText":"","items":[],"serviceText":"10","sstText":"6","nextId":3}}')
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
], ids=["name", "add-person", "subtotal", "mode", "add-item", "sst"])
def test_R25_every_change_is_saved(open_app, change, check):
    page = open_app().page
    assert stored(page) is None
    change(page)
    draft = stored(page)
    assert list(draft) == ["version", "bill"] and draft["version"] == 1 and check(draft["bill"])


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
    assert first_diff(dom_walk(open_app(seed=seed).page), golden_walk(plain_context, golden)) is None


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
PRESS_CASES = [
    pytest.param(None, lambda page: page.locator("#subtotal"), "0", lambda page: page.locator("#rate-service"),
                 "subtotal-error", "rate-service", id="subtotal"),
    pytest.param(seeds.S1, lambda page: item_price(page, 2), "13.505", lambda page: toggle(page, "Char kuey teow", "Aisyah"),
                 "price-error-i5", "button", id="item-price"),
    pytest.param(None, lambda page: rate_field(page, "Service charge"), "31", lambda page: page.locator("#charges-hint"),
                 "rate-service-error", "charges-hint", id="service"),
    pytest.param(None, lambda page: rate_field(page, "SST"), "25", lambda page: page.locator("#charges-hint"),
                 "rate-sst-error", "charges-hint", id="sst"),
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
@pytest.mark.parametrize("seed, field_of, bad, below_of, error_id, lands_on", PRESS_CASES)
def test_R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on(
        open_app, how, seed, field_of, bad, below_of, error_id, lands_on):
    page = open_app(seed=seed, touch=how == "touch").page
    support.replace_text(page, field_of(page), bad)
    assert page.locator(f"#{error_id}").count() == 0  # CG-3: no error while the field still has focus
    page.evaluate(RECORD_CLICKS_JS)
    press(page, how, centre_of(below_of(page)))
    assert page.evaluate("window.testClicks") == [lands_on]
    assert page.locator(f"p.error#{error_id}").inner_text() in ("Enter an amount like 12.50", "Enter a rate from 0 to 30", "Enter a rate from 0 to 20")
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


@pytest.mark.parametrize("how", ["mouse", "touch"])
def test_R10_a_keyboard_blur_shows_the_error_at_once_even_after_a_press(open_app, how):
    page = open_app(seed=seeds.S1, touch=how == "touch").page
    press(page, how, centre_of(item_price(page, 2)))  # a finished press must not hold the next blur back
    assert support.active_label(page) == "Item 2 price in RM"
    page.keyboard.press("Control+A")
    page.keyboard.type("13.505")
    page.keyboard.press("Tab")
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


# ===== END OF TESTS (new tests go above this line) =====
