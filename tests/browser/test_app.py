"""Functional suite for split-app. One test per scenario row of qa.md, named test_R<n>_<what>.

Run from the project root: python -m pytest tests/browser -q
Real gestures only. State that is not under test is set up with fill() and clicks on visible controls,
never through a hook in the app (there is none).
"""
import ast
import hashlib
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from xml.etree import ElementTree

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

import rig
import seeds
import support
from expected import (BLOCKED_CARD, EVEN_MESSAGE, S1_CHECK, S1_COPY, S1_ITEMS, S1_ROWS, S1_SUMMARY, S2_CHECK, S2_COPY,
                      S2_ROWS, S2_SUMMARY)
from support import (CSP, GOLDEN_DIR, GOLDEN_V1_DIR, ROOT, card_text, dom_walk, first_diff, golden_walk, open_golden,
                     panel_text, person_field, walk_entries)


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
    assert len(seeds.UNREADABLE) == 32 and len(set(seeds.UNREADABLE.values())) == 32  # qa.md B1 to B32 (v1.1.0)
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


GOLDEN_CSS_LF_BYTES = 33070
GOLDEN_CSS_LF_SHA256 = "66807273b62f87e05caa931faac40a4bcac1cf7294b2cf38a9f046154b6d3c08"  # the committed LF blob (spec R1)


def lf_bytes(path):
    return path.read_bytes().replace(b"\r\n", b"\n")


def same_stylesheet(shipped, golden):
    """R1's comparison. Both files with every CRLF turned into LF, then byte for byte, so any checkout agrees."""
    return lf_bytes(shipped) == lf_bytes(golden)


def test_R1_entry_point_loads_only_its_own_files(open_app, tmp_path):
    session = open_app()
    assert session.page.evaluate(HEAD_SUMMARY_JS) == [
        ["meta", {"charset": "utf-8"}, ""],
        ["meta", {"name": "viewport", "content": "width=device-width, initial-scale=1, viewport-fit=cover"}, ""],
        ["meta", {"name": "color-scheme", "content": "dark"}, ""],
        ["meta", {"http-equiv": "Content-Security-Policy", "content": CSP}, ""],
        ["title", {}, "Danial's Splity Tab"],
        ["link", {"rel": "icon", "type": "image/svg+xml", "href": "src/icon.svg"}, ""],
        ["link", {"rel": "stylesheet", "href": "src/system.css"}, ""],
        ["script", {"type": "module", "src": "src/main.js"}, ""],
    ]
    assert session.page.evaluate("document.documentElement.lang") == "en"
    shipped, golden = ROOT / "src" / "system.css", GOLDEN_DIR / "system.css"
    assert same_stylesheet(shipped, golden)
    for path in (shipped, golden):
        turned = lf_bytes(path)
        assert (len(turned), hashlib.sha256(turned).hexdigest()) == (GOLDEN_CSS_LF_BYTES, GOLDEN_CSS_LF_SHA256), path.name
    # The comparison's own control: a CRLF copy still matches, a copy with one rule changed does not.
    crlf_copy, changed_copy = tmp_path / "crlf.css", tmp_path / "changed.css"
    crlf_copy.write_bytes(lf_bytes(golden).replace(b"\n", b"\r\n"))
    changed_copy.write_bytes(lf_bytes(golden).replace(b"[hidden] { display: none !important; }", b"[hidden] { display: block !important; }"))
    assert same_stylesheet(crlf_copy, golden) and not same_stylesheet(changed_copy, golden)
    assert session.problems() == []
    assert ("GET", session.base + "/src/system.css") in session.requests


def test_R1_every_url_in_the_page_is_relative():
    # The static half of "The page works from a sub-path", kept apart so it guards while the screen half waits (BUILD.md, A2).
    for name, text in support.shipped_text().items():
        assert not SOURCE_URL.search(text.replace(NAMESPACE_CALL, "")), name
        if name == "index.html":
            assert "://" not in text


@pytest.mark.xfail(strict=True, reason="task A11")
def test_R1_page_works_from_a_sub_path(open_app):
    # The target is a GitHub Pages project path (/split/), so the app must work one folder down. The only way to serve
    # it there is a server rooted at the parent folder, which also serves the sibling projects on 127.0.0.1 while this
    # test runs. Accepted (ORCH, WR-11): loopback only, test-only, stopped in this test.
    parent = rig.StaticServer(ROOT.parent).start()
    try:
        folder = f"/{ROOT.name}"
        session = open_app(base_server=parent, path=folder + "/", prefix=folder)
        assert session.page.evaluate("document.querySelector('link[rel=icon]').href").endswith(f"{folder}/src/icon.svg")
        assert cold_boot_state(session.page) == COLD_BOOT
        assert session.problems() == []
    finally:
        parent.stop()


# R2's first render, read in one pass so a part that is not built yet fails at once instead of waiting for it.
COLD_BOOT_JS = """() => {
  const one = (selector) => document.querySelector(selector);
  const attr = (selector, name) => one(selector)?.getAttribute(name) ?? null;
  const field = (selector) => one(selector) ? [one(selector).value, one(selector).placeholder] : null;
  const copy = one('#stripCopy');
  return {
    names: [...document.querySelectorAll('li.field.person input')].map((input) => input.value),
    removesDisabled: [...document.querySelectorAll('li.field.person button')].map((button) => button.disabled),
    evenChecked: one('#modeEven')?.checked ?? null,
    subtotal: field('#evenSub'),
    subtotalErrorHidden: one('p.err#evenErr')?.hidden ?? null,
    rates: [one('#svc')?.value ?? null, one('#sst')?.value ?? null],
    open: [attr('#peopleBlk', 'data-open'), attr('#peopleBtn', 'aria-expanded'), attr('#chargesBlk', 'data-open')],
    totalHolds: [...(one('#rbody > div.r-total')?.children ?? [])].map((el) => `${el.localName}.${el.className}`),
    emptyIcon: attr('#rbody > div.r-empty > svg.ic > use', 'href'),
    strip: one('#stripInfo')?.innerText.trim() ?? null,
    stripCopy: copy ? { shown: copy.checkVisibility(), disabled: copy.disabled } : null,
  };
}"""
COLD_BOOT = {
    "names": ["Person 1", "Person 2"], "removesDisabled": [True, True], "evenChecked": True, "subtotal": ["", "0.00"],
    "subtotalErrorHidden": True, "rates": ["10", "6"], "open": ["true", "true", "false"],
    "card": BLOCKED_CARD["subtotal"], "totalHolds": ["span.r-label"], "emptyIcon": "#i-mark",
    "strip": "Enter the subtotal to see the splits.", "stripCopy": {"shown": True, "disabled": True},
}


def cold_boot_state(page):
    return {**page.evaluate(COLD_BOOT_JS), "card": card_text(page)}


@pytest.mark.xfail(strict=True, reason="task A11")
def test_R2_cold_boot_is_a_new_bill_with_no_seed(open_app):
    page = open_app().page
    assert cold_boot_state(page) == COLD_BOOT
    assert page.evaluate("localStorage.getItem('split.draft')") is None
    assert page.evaluate("Object.getOwnPropertyNames(window).filter((n) => n.startsWith('__'))") == []


def test_R2_no_sample_data_ships():
    for name, text in support.shipped_text().items():
        for sample in SAMPLE_NAMES:
            assert not re.search(rf"\b{re.escape(sample)}\b", text, re.IGNORECASE), f"{sample} in {name}"


VIEWPORTS = {390: (390, 844), 360: (360, 780), 1280: (1280, 800)}
SHEET_SPARE_CHIP = "#splitsDlg .r-spare-acts button[aria-haspopup=dialog]"
SPARE_OPENERS = {"phone": ("#splitsBtn", SHEET_SPARE_CHIP), "desktop": ("#spareBtn",)}
# qa.md, "The rendered markup matches its golden": golden -> (seed, the clicks after load below and from 1024 px,
# and per width the task that completes the state, the reason of its xfail until that task removes it).
R3_STATES = {
    "bill-items": (seeds.S1, {}, {390: "A11", 360: "A11", 1280: "A13"}),
    "bill-items-open": (seeds.S1, {"phone": ("#peopleBtn", "#chargesBtn")}, {390: "A11", 360: "A11"}),
    "bill-even": (seeds.S2, {}, {390: "A11", 360: "A11", 1280: "A13"}),
    "spare-sen": (seeds.S1, SPARE_OPENERS, {390: "A13", 360: "A13", 1280: "A13"}),
    "spare-sen-one": (seeds.ONE, SPARE_OPENERS, {390: "A14", 360: "A14", 1280: "A14"}),
    "spare-sen-random": (seeds.RND, SPARE_OPENERS, {390: "A15", 360: "A15", 1280: "A15"}),
    "splits-sheet": (seeds.S1, {"phone": ("#splitsBtn",)}, {390: "A13", 360: "A13"}),
    "new-bill-dialog": (seeds.S1, {"phone": ("#newBill",), "desktop": ("#newBill",)}, {390: "A16", 360: "A16", 1280: "A16"}),
    "bill-empty": (None, {}, {390: "A11", 360: "A11", 1280: "A7"}),
    "rate-error": (seeds.RE, {}, {390: "A11", 360: "A11", 1280: "A8"}),
    "bill-unassigned": (seeds.S5, {}, {390: "A11", 360: "A11", 1280: "A9"}),
    "bill-unreadable": (seeds.UNREADABLE["B1"], {}, {390: "A11", 360: "A11", 1280: "A7"}),
    "bill-twelve": (seeds.T12, {}, {390: "A11", 360: "A11", 1280: "A13"}),
    "bill-large": (seeds.W1, {}, {390: "A11", 360: "A11", 1280: "A13"}),
}
R3_PAIRS = [pytest.param(golden, width, marks=pytest.mark.xfail(strict=True, reason=f"task {task}"), id=f"{golden}-{width}")
            for golden, (_, _, tasks) in R3_STATES.items() for width, task in tasks.items()]


def click_after_load(page, selectors):
    """The clicks that reach a golden's state. A control the page does not hold yet fails at once, not after a wait."""
    for selector in selectors:
        control = page.locator(selector)
        assert control.count() == 1, f"after-load control {selector} is not on the page"
        control.click()


@pytest.mark.parametrize("golden, width", R3_PAIRS)
def test_R3_rendered_markup_matches_its_golden(open_app, plain_context, golden, width):
    seed, after_load, _ = R3_STATES[golden]
    page = open_app(seed=seed, viewport=VIEWPORTS[width]).page
    click_after_load(page, after_load.get("desktop" if width >= 1024 else "phone", ()))
    assert first_diff(dom_walk(page), golden_walk(plain_context, golden, VIEWPORTS[width])) is None


def edited_walk(walk, matches, edit):
    """A deep copy of a walk with `edit` applied to the first entry that `matches`."""
    copy = json.loads(json.dumps(walk))
    edit(next(entry for entry in walk_entries(copy) if matches(entry)))
    return copy


@pytest.mark.xfail(strict=True, reason="task A12")
def test_R3_the_walk_sees_every_rendered_element_and_flags_each_kind_of_change(open_app):
    page = open_app(seed=seeds.S1).page
    walk = dom_walk(page)
    assert len(list(walk_entries(walk))) > 40
    pressed = edited_walk(walk, lambda e: e["tag"] == "button" and "tap" in e["cls"].split() and e["attrs"].get("aria-pressed") == "true",
                          lambda e: e["attrs"].update({"aria-pressed": "false"}))
    found = first_diff(walk, pressed)
    assert re.search(r"button\.tap\[\d+\]: attr aria-pressed app='true' golden='false'$", found), found
    opened = edited_walk(walk, lambda e: e["attrs"].get("id") == "peopleBlk", lambda e: e["attrs"].update({"data-open": "true"}))
    found = first_diff(walk, opened)
    assert re.search(r"div\.blk\.sec\[\d+\]: attr data-open app='false' golden='true'$", found), found
    shorter = edited_walk(walk, lambda e: e["attrs"].get("id") == "itemList", lambda e: e["children"].pop())
    found = first_diff(walk, shorter)
    assert re.search(r"ul\.frame\[\d+\]: children ", found), found
    page.locator("#splitsBtn").click()
    found = first_diff(walk, dom_walk(page))
    assert found.startswith("body: children ") and "dialog.sheet-dlg" in found, found


def test_R38_policy_is_exact_and_nothing_inline():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert re.findall(r'<meta http-equiv="Content-Security-Policy" content="([^"]*)">', html) == [CSP]
    assert html.count("Content-Security-Policy") == 1
    assert "<style" not in html and not re.search(r"\sstyle\s*=", html)
    assert not re.search(r"<script(?![^>]*\ssrc=)", html) and not re.search(r"\son[a-z]+\s*=", html)


# The four CSSOM targets of spec R38, each with the properties it may hold at that moment.
STYLE_OUTSIDE_TARGETS_JS = """() => [...document.querySelectorAll('[style]')].flatMap((el) => {
  const bothOpen = document.querySelector('#spareDlg')?.open && document.querySelector('#splitsDlg')?.open;
  const allowed = el === document.documentElement ? ['--strip-h']
    : el.matches('ul.r-splits.many') ? ['--rows']
    : el.matches('#spareDlg') && innerWidth >= 1024 ? ['left', 'bottom']
    : el.matches('#sheetScroll') && bothOpen ? ['padding-bottom'] : [];
  const extra = [...el.style].filter((name) => !allowed.includes(name));
  return extra.length ? [`${el.localName}#${el.id}.${el.className}: ${extra.join(' ')}`] : [];
})"""
K1_SPLITS = ["RM 29.04", "RM 15.74", "RM 24.48", "RM 69.26"]
# (state, golden of that state, seed, width, the clicks after load, the proof the module ran, the task that completes it)
POLICY_STATES = [
    ("cold-boot", "bill-empty", None, 390, (), "card-blocked", None),
    ("K1", "bill-items", seeds.S1, 390, (), "card-K1", "A9"),
    ("K1-new-bill", "new-bill-dialog", seeds.S1, 390, ("#newBill",), "dialog-open", None),
    ("K1-sheet-P1", "spare-sen", seeds.S1, 390, ("#splitsBtn", SHEET_SPARE_CHIP), "sheet-padding", "A13"),
    ("K2-P1-desktop", "bill-even", seeds.S2, 1280, ("#spareBtn",), "spare-place", "A13"),
]
POLICY_PROOFS = {  # proof -> (what the page shows, what it must show)
    "card-blocked": (card_text, BLOCKED_CARD["subtotal"]),
    "card-K1": (lambda page: page.evaluate("() => [...document.querySelectorAll('#splits .amt, #addsUp')].map((el) => el.textContent)"),
                K1_SPLITS),
    "dialog-open": (lambda page: page.evaluate("() => document.querySelector('#newDlg').matches(':modal')"), True),
    "sheet-padding": (lambda page: page.evaluate("() => document.querySelector('#sheetScroll')?.style.getPropertyValue('padding-bottom') ?? null"),
                      "271px"),
    "spare-place": (lambda page: page.evaluate("""() => { const dialog = document.querySelector('#spareDlg');
       return [dialog.style.getPropertyValue('left'), dialog.getBoundingClientRect().bottom]; }"""), ["574px", 560.8]),
}


@pytest.mark.parametrize("state, golden, seed, width, clicks, proof", [
    pytest.param(*row[:6], id=row[0], marks=[pytest.mark.xfail(strict=True, reason=f"task {row[6]}")] if row[6] else [])
    for row in POLICY_STATES])
def test_R38_strict_policy_blocks_nothing_the_app_needs(open_app, plain_context, state, golden, seed, width, clicks, proof):
    session = open_app(seed=seed, viewport=VIEWPORTS[width])
    page = session.page
    click_after_load(page, clicks)
    body_background = "getComputedStyle(document.body).backgroundColor"
    assert page.evaluate(body_background) == open_golden(plain_context, golden, VIEWPORTS[width]).evaluate(body_background)
    shows, expected = POLICY_PROOFS[proof]
    found = shows(page)
    if proof == "spare-place":
        assert found[0] == expected[0] and abs(found[1] - expected[1]) <= 0.5, found
    else:
        assert found == expected
    assert page.evaluate(STYLE_OUTSIDE_TARGETS_JS) == []
    assert session.problems() == []


# R38, the narrow CSSOM allowance and the one Web Animation (PD-22).
STYLE_TOKENS = ['setAttribute("style"', "setAttribute('style'", "cssText", "insertRule", "new CSSStyleSheet",
                "adoptedStyleSheets", "<style"]
DIRECT_STYLE_WRITE = re.compile(r"\.style\.[A-Za-z]+\s*=(?!=)")
STYLE_CALL = re.compile(r"""\bstyle\.(?:setProperty|removeProperty)\(\s*(?:(["'`])([^"'`]*)\1)?""")
STYLE_TARGETS = {"--strip-h", "--rows", "left", "bottom", "padding-bottom"}


def style_write_problems(name, text):
    found = [f"{token} in {name}" for token in STYLE_TOKENS if token in text]
    found += [f"direct style write {match.group(0)!r} in {name}" for match in DIRECT_STYLE_WRITE.finditer(text)]
    return found + [f"style call on {match.group(2)!r} in {name}" for match in STYLE_CALL.finditer(text)
                    if match.group(2) not in STYLE_TARGETS]


def test_R38_code_writes_style_only_to_the_four_allowed_targets(tmp_path):
    scripts = {name: text for name, text in support.shipped_text().items() if name.startswith("src/") and name.endswith(".js")}
    assert [problem for name, text in scripts.items() for problem in style_write_problems(name, text)] == []
    planted = tmp_path / "main.js"
    planted.write_text(scripts["src/main.js"] + '\ndocument.body.style.setProperty("color", "red");\n', encoding="utf-8")
    assert style_write_problems("planted main.js", planted.read_text(encoding="utf-8")) != []
    assert sum(text.count(".animate(") for text in scripts.values()) == 1


# ---------------------------------------------------------------- v1.1.0 task A2: the name, the mark and the tab icon (R43 to R45)
def test_R43_the_name_in_the_title_and_the_top_bar(open_app):
    page = open_app().page
    assert page.title() == "Danial's Splity Tab"
    found = page.evaluate("""() => {
      const brand = document.querySelector('header.top > div.brand');
      return { brand: brand ? [...brand.children].map((el) => `${el.localName}.${el.getAttribute('class')}`) : null,
               word: document.querySelector('div.brand > h1.word')?.textContent ?? null, text: document.body.textContent };
    }""")
    assert found["brand"] == ["svg.mark", "h1.word"] and found["word"] == "Splity Tab"
    assert found["text"].count("Splity Tab") == 1 and "Danial" not in found["text"]


SPRITE = re.compile(r'<svg class="sprite".*?</svg>', re.S)
MARK = re.compile(r'<svg class="mark".*?</svg>', re.S)
SPRITE_SYMBOLS = ["i-x", "i-plus", "i-copy", "i-check", "i-caret", "i-shuffle", "i-warning", "i-warning-circle", "i-mark", "i-seal-check"]


def test_R44_the_sprite_and_the_mark_are_the_goldens_bytes():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    golden = (GOLDEN_DIR / "bill-items.html").read_text(encoding="utf-8")
    sprite = SPRITE.search(html).group(0)
    assert sprite == SPRITE.search(golden).group(0)
    assert re.findall(r'<symbol id="([^"]+)"', sprite) == SPRITE_SYMBOLS and '<linearGradient id="seal-grad"' in sprite
    mark, golden_mark = MARK.search(html).group(0), MARK.search(golden).group(0)
    assert mark.startswith('<svg class="mark" viewBox="0 0 28 28" aria-hidden="true" focusable="false">')
    path_of = lambda text: re.findall(r'<path fill-rule="([^"]*)" d="([^"]*)"/>', text)
    assert len(re.findall(r"<path\b", mark)) == 1 and path_of(mark) == path_of(golden_mark) != []
    assert "xmlns" not in html


def test_R44_the_sprite_comes_first_and_the_empty_receipt_uses_the_mark(open_app):
    found = open_app().page.evaluate("""() => {
      const first = document.body.firstElementChild;
      const box = first.getBoundingClientRect(), mark = document.querySelector('div.brand > svg.mark').getBoundingClientRect();
      return { first: `${first.localName}.${first.getAttribute('class')}`, hidden: first.getAttribute('aria-hidden'),
               focusable: first.getAttribute('focusable'), size: [box.width, box.height], mark: [mark.width, mark.height],
               emptyIcon: document.querySelector('#card div.r-empty > svg.ic > use')?.getAttribute('href') ?? null };
    }""")
    assert found == {"first": "svg.sprite", "hidden": "true", "focusable": "false", "size": [0, 0], "mark": [28, 28],
                     "emptyIcon": "#i-mark"}


TAB_ICON_BYTES = 470
TAB_ICON_SHA256 = "7b5e4176a6182d23f06073ff181f01bbb73e2ac562f78d58a930ffb80fe7fef2"  # at planning time (spec R45)


def test_R45_the_tab_icon_file_is_the_goldens_icon():
    hrefs = []
    for golden in sorted(GOLDEN_DIR.glob("*.html")):
        links = re.findall(r'<link\b[^>]*\brel="icon"[^>]*>', golden.read_text(encoding="utf-8"))
        assert len(links) == 1, golden.name
        hrefs.append(re.search(r'\bhref="([^"]*)"', links[0]).group(1))
    assert len(hrefs) == 15 and len(set(hrefs)) == 1 and hrefs[0].startswith("data:")
    icon = (ROOT / "src" / "icon.svg").read_bytes()
    assert icon == urllib.parse.unquote(hrefs[0].split(",", 1)[1]).encode("utf-8")
    assert (len(icon), hashlib.sha256(icon).hexdigest()) == (TAB_ICON_BYTES, TAB_ICON_SHA256)
    root = ElementTree.fromstring(icon)
    assert (root.tag, root.get("viewBox")) == ("{http://www.w3.org/2000/svg}svg", "0 0 16 16")
    text = icon.decode("utf-8").lower()
    assert "#a3aaff" in text and re.search(r"@media\s*\(prefers-color-scheme:\s*light\)\s*\{[^}]*#1e2140", text)
    favicon = (ROOT / "docs" / "brand" / "favicon.svg").read_bytes()
    assert all(path.read_bytes() != favicon for path in (ROOT / "src").rglob("*") if path.is_file())
    assert all("favicon.svg" not in text and "brand/" not in text for text in support.shipped_text().values())


def test_R45_the_tab_icon_loads_under_the_live_policy(open_app):
    session = open_app()
    page = session.page
    assert page.evaluate("() => { const link = document.querySelector('link[rel=icon]'); return [link.type, link.href]; }") == [
        "image/svg+xml", session.base + "/src/icon.svg"]
    loaded = page.evaluate("""() => new Promise((resolve) => {
      const image = new Image();
      const timer = setTimeout(() => resolve({ load: false, gaveUp: 'after 5 s' }), 5000);
      image.onload = () => { clearTimeout(timer); resolve({ load: true, width: image.naturalWidth }); };
      image.onerror = () => { clearTimeout(timer); resolve({ load: false }); };
      image.src = 'src/icon.svg';
    })""")
    assert loaded["load"] and loaded["width"] > 0, loaded
    assert page.evaluate("window.testCspViolations") == []


# Draws src/icon.svg on a 64 x 64 canvas that is never put in the page, and lists the colours of its opaque pixels.
ICON_COLOURS_JS = """() => new Promise((resolve) => {
  const image = new Image();
  const timer = setTimeout(() => resolve({ error: 'gave up after 5 s' }), 5000);
  image.onload = () => {
    clearTimeout(timer);
    try {
      const canvas = document.createElement('canvas');
      canvas.width = 64; canvas.height = 64;
      const context = canvas.getContext('2d');
      context.drawImage(image, 0, 0, 64, 64);
      const data = context.getImageData(0, 0, 64, 64).data, opaque = [];
      for (let i = 0; i < data.length; i += 4) if (data[i + 3] === 255) opaque.push(`rgb(${data[i]}, ${data[i + 1]}, ${data[i + 2]})`);
      resolve({ opaque: opaque.length, colours: [...new Set(opaque)] });
    } catch (error) { resolve({ error: String(error) }); }
  };
  image.onerror = () => { clearTimeout(timer); resolve({ error: 'load failed' }); };
  image.src = 'src/icon.svg';
})"""


def test_R45_the_tab_icon_colour_follows_the_colour_scheme(open_app, engine, request):
    readings = {scheme: open_app(color_scheme=scheme).page.evaluate(ICON_COLOURS_JS) for scheme in ("dark", "light")}
    if engine == "chromium":
        assert readings["dark"]["opaque"] >= 20 and readings["dark"]["colours"] == ["rgb(163, 170, 255)"], readings
        assert readings["light"]["opaque"] >= 20 and readings["light"]["colours"] == ["rgb(30, 33, 64)"], readings
    else:  # Safari 26 draws one colour in both themes (WebKit bug 309949, accepted by the owner), so this is a record only
        record = request.getfixturevalue("evidence_folder") / "icon-colour.txt"
        record.write_text("".join(f"{scheme}: {json.dumps(reading)}\n" for scheme, reading in readings.items()), encoding="utf-8")
        assert [line.split(":")[0] for line in record.read_text(encoding="utf-8").splitlines()] == ["dark", "light"]


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


# v1.1.0 task A5. What the People content shows (R4, R6, R7), read in one pass, so a part that is not built yet fails on
# the assertion that names it and never on a wait. An icon reads as "class href".
PEOPLE_JS = """() => {
  const list = document.querySelector('ul.people#peopleList'), add = document.querySelector('#addPerson');
  const icons = (node) => [...node.querySelectorAll('svg')].map((svg) => `${svg.getAttribute('class')} ${svg.querySelector('use')?.getAttribute('href')}`);
  return {
    list: list && { labelledBy: list.getAttribute('aria-labelledby'), rows: [...list.children].map((li) => {
      const input = li.querySelector('input'), remove = li.querySelector('button');
      return { li: `${li.localName}.${li.className}`, value: input ? input.value : null,
        input: input && ['type', 'aria-label', 'placeholder', 'maxlength', 'autocomplete'].map((name) => input.getAttribute(name)),
        remove: remove && [remove.className, remove.getAttribute('aria-label'), remove.disabled, ...icons(remove)] };
    }) },
    add: add && [add.className, add.disabled, add.textContent.trim(), ...icons(add)],
  };
}"""
GOLDEN_LOOK = ["lineHeight", "cursor"]  # qa.md "Equal to the golden" adds line-height to the specimen list, the rows add cursor


def people_shown(page):
    """{ list: { labelledBy, rows } or None, add: Add person or None }, as PEOPLE_JS reads them."""
    return page.evaluate(PEOPLE_JS)


def person_rows(page):
    """The rows of ul.people#peopleList, or None when the page has no such list."""
    shown = people_shown(page)["list"]
    return shown and shown["rows"]


def person_row(number, value, name, disabled=False):
    """A row as spec R4 writes it, at 1-based `number`, holding `value`, its Remove named for `name`."""
    return {"li": "li.field person", "value": value,
            "input": ["text", f"Person {number} name", f"Person {number}", "20", "off"],
            "remove": ["icon-btn", f"Remove {name}", disabled, "ic #i-x"]}


def add_person_shown(disabled=False):
    """#addPerson as spec R6 writes it."""
    return ["btn btn-ghost", disabled, "Add person", "ic #i-plus"]


def test_R4_person_rows_carry_their_names_and_labels(open_app):
    # [v1.1.0] ul.people#peopleList, and the X icon through the sprite.
    page = open_app(seed=seeds.S1).page
    open_people_first(page)
    assert people_shown(page)["list"] == {"labelledBy": "peopleH", "rows": [
        person_row(1, "Aisyah", "Aisyah"), person_row(2, "Ben", "Ben"), person_row(3, "Chen", "Chen")]}


def test_R4_a_blank_name_falls_back_to_its_position_everywhere_but_the_field(open_app):
    # [v1.1.0] K1, and the People summary shows the fallback too. The card's splits row is task A9's (until then the 1.0
    # form, test_R5_a_blank_name_reads_as_its_position_in_the_shares_row).
    page = open_app(seed=seeds.S1).page
    open_people_first(page)
    support.replace_text(page, person_field(page, 2), "")
    rows = person_rows(page)
    assert rows is not None, "no ul.people#peopleList"
    assert rows[1] == person_row(2, "", "Person 2")
    for name, _, _ in S1_ITEMS:
        assert who_group(page, name).get_by_role("button").all_inner_texts() == ["Aisyah", "Person 2", "Chen"]
    page.locator("#peopleBtn").click()
    assert visible_text(page, "#peopleSum") == "Aisyah, Person 2, Chen"
    open_people_first(page)
    support.replace_text(page, person_field(page, 2), "   ")  # spaces only count as blank (PD-2 of 1.0)
    assert person_rows(page)[1] == person_row(2, "   ", "Person 2")


# After each key of a rename of the third person: their toggle in every item, their Remove name, the People summary.
RENAME_READS_JS = """() => ({
  toggles: [...document.querySelectorAll('li.item')].map((item) => item.querySelectorAll('button.tap')[2]?.textContent.trim() ?? null),
  remove: document.querySelectorAll('ul.people#peopleList > li')[2]?.querySelector('button')?.getAttribute('aria-label') ?? null,
  summary: document.querySelector('#peopleSum span.sec-txt')?.textContent ?? null,
})"""


def rename_chen_to_chen_wei(page, watch=None):
    """qa.md: click the end of "Person 3 name" and type " Wei", calling `watch(label so far)` after each key."""
    person_field(page, 3).click()
    page.keyboard.press("End")
    typed = "Chen"
    for key in " Wei":
        page.keyboard.type(key)
        typed += key
        if watch:
            watch(typed.strip())


def test_R5_renaming_a_person_updates_every_place_on_each_keystroke(open_app):
    # [v1.1.0] K1. The toggles, the Remove name and the People summary here. The card's splits row is task A9's (until
    # then the 1.0 form, test_R5_a_person_label_follows_the_name_into_every_toggle and the shares table tests), and the
    # sheet, the copy and the pills are the next test's.
    page = open_app(seed=seeds.S1).page
    open_people_first(page)

    def every_place_reads(label):
        assert page.evaluate(RENAME_READS_JS) == {"toggles": [label] * 4, "remove": f"Remove {label}",
                                                  "summary": f"Aisyah, Ben, {label}"}

    rename_chen_to_chen_wei(page, every_place_reads)
    assert person_field(page, 3).input_value() == "Chen Wei"


@pytest.mark.xfail(strict=True, reason="task A14")
def test_R5_a_new_name_reaches_the_sheet_the_copy_and_the_pills(open_app):
    # The rest of qa.md "Renaming a person updates every place on each keystroke". The sheet is task A12's, its Copy
    # summary A10 and A12, the spare chip in it A13 and the pills A14. Each read fails on its assertion, never on a wait.
    page = open_app(seed=seeds.S1).page
    open_people_first(page)
    rename_chen_to_chen_wei(page)
    page.locator("#splitsBtn").click()
    names = page.evaluate("() => [...document.querySelectorAll('#splitsDlg ul.r-splits > li > span.nm')].map((el) => el.textContent)")
    assert names == ["Aisyah", "Ben", "Chen Wei"], names
    page.locator("#splitsDlg .r-copy").click()
    assert page.evaluate("window.testClipboardText").splitlines()[4] == "Chen Wei RM 24.48"
    page.locator(SHEET_SPARE_CHIP).click()
    page.locator("#spareDlg label.choice", has_text="One person").click()
    pills = page.evaluate("() => [...document.querySelectorAll('#pickList label.pill .pill-face')].map((el) => el.textContent.trim())")
    assert pills == ["Aisyah", "Ben", "Chen Wei"], pills


def test_R6_add_person_until_the_limit(open_app, plain_context):
    # [v1.1.0] People is open on a cold boot below 1024 px, and the disabled look is compared with bill-twelve.html. The
    # 1.0 form compared it with a states.html specimen (B1).
    page = open_app().page
    assert people_shown(page)["add"] == add_person_shown(), "no #addPerson as spec R6 writes it"
    add = page.locator("#addPerson")
    add.click()
    assert person_rows(page) == [person_row(1, "Person 1", "Person 1"), person_row(2, "Person 2", "Person 2"),
                                 person_row(3, "", "Person 3")]
    for _ in range(9):
        add.click()
    assert len(person_rows(page)) == 12 and people_shown(page)["add"] == add_person_shown(disabled=True)
    page.locator("#peopleBtn").focus()
    page.keyboard.press("Tab")
    assert support.active_label(page) == "Person 1 name"  # Tab skips the disabled Add person
    page.set_viewport_size({"width": 1280, "height": 800})
    golden = open_golden(plain_context, "bill-twelve", VIEWPORTS[1280]).locator("#addPerson")
    assert support.specimen_props(add, GOLDEN_LOOK) == support.specimen_props(golden, GOLDEN_LOOK)
    assert add.evaluate("(el) => getComputedStyle(el).cursor") == "not-allowed"
    box = add.bounding_box()
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    assert len(person_rows(page)) == 12


def test_R6_removing_anyone_from_twelve_turns_add_person_back_on(open_app):
    # qa.md (plan check F5, bill-twelve.md). The v1.1.0 form of 1.0's test_R6_a_restored_twelve_person_bill_shows_the_limit_state,
    # which read a states.html specimen and the 1.0 grid cells (B1).
    page = open_app(seed=seeds.S8).page
    open_people_first(page)
    rows = person_rows(page)
    assert rows is not None and len(rows) == 12 and people_shown(page)["add"] == add_person_shown(disabled=True)
    assert stored_text(page) == seeds.S8  # a restore writes nothing
    remove_button(page, "Mei Ling").click()
    assert len(person_rows(page)) == 11 and people_shown(page)["add"] == add_person_shown()
    assert support.active_label(page) == "Person 11 name"
    page.locator("#peopleBtn").focus()
    page.keyboard.press("Tab")
    assert page.evaluate("document.activeElement.id") == "addPerson"
    page.locator("#addPerson").click()
    assert person_rows(page)[11] == person_row(12, "", "Person 12")
    assert people_shown(page)["add"] == add_person_shown(disabled=True)


def test_R7_remove_a_person(open_app):
    page = open_app().page
    three_people(page)
    remove_button(page, "Chen").click()
    assert [f.input_value() for f in page.locator("li.person input").all()] == ["Aisyah", "Ben"]
    assert all(button.is_disabled() for button in page.locator("li.person button").all())


@pytest.mark.parametrize("seed, action, target, value", [
    pytest.param(None, "Add person", "Person 3 name", "", id="cold-boot-add-person"),
    pytest.param(seeds.S1, "Remove Ben", "Person 2 name", "Chen", id="K1-remove-Ben"),
    pytest.param(seeds.S1, "Remove Chen", "Person 2 name", "Ben", id="K1-remove-Chen"),
])
def test_R34_focus_after_adding_or_removing_a_person(open_app, seed, action, target, value):
    # [v1.1.0] The person rows of qa.md "Focus after adding or removing", on K1 with People opened first.
    page = open_app(seed=seed).page
    open_people_first(page)
    page.get_by_role("button", name=action, exact=True).click()
    assert support.active_label(page) == target
    assert page.evaluate("document.activeElement.value") == value


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
    page = open_app(seed=seeds.S1).page  # [v1.1.0] K1 with People opened first
    open_people_first(page)
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
    assert card_text(page) == BLOCKED_CARD["no-prices"]  # the v1.1.0 card since task A2 (BUILD.md, A2, Q-A2-3)
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


def opened_rate_field(label):
    """A field_of for a rate row of an outline: Charges opened first (qa.md, it is folded below 1024 px since task A4,
    R48), then the rate field. Opening is a click only when Charges is folded, so calling it again changes nothing."""
    def field_of(page):
        open_charges_first(page)
        return rate_field(page, label)
    return field_of


# The three inline error texts (spec, Copy), each exact. A case that showed another field's text must fail.
AMOUNT_MESSAGE, SERVICE_MESSAGE, SST_MESSAGE = "Enter an amount like 12.50", "Enter a rate from 0 to 30", "Enter a rate from 0 to 20"

# Rows are added with the field's own task: item prices (task 5), Service charge and SST (task 6).
ERROR_CASES = [
    pytest.param(lambda page: None, lambda page: page.locator("#subtotal"), "0", AMOUNT_MESSAGE, "subtotal-error", "12.50", id="subtotal"),
    pytest.param(lambda page: build_s1(page), lambda page: item_price(page, 2), "13.505", AMOUNT_MESSAGE, "price-error-i5", "13.50", id="item-price"),
    pytest.param(lambda page: None, opened_rate_field("Service charge"), "31", SERVICE_MESSAGE, "rate-service-error", "10", id="service"),
    pytest.param(lambda page: None, opened_rate_field("SST"), "20.01", SST_MESSAGE, "rate-sst-error", "6", id="sst"),
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
    assert card_text(page) == BLOCKED_CARD["subtotal"]  # the v1.1.0 card since task A2 (BUILD.md, A2, Q-A2-3)


def test_R10_typing_bad_text_in_a_focused_field_shows_no_error_early(open_app):
    page = open_app().page
    subtotal_field(page).click()
    page.keyboard.type("abc")
    assert page.locator("p.error").count() == 0 and card_text(page) == BLOCKED_CARD["subtotal"]


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


def test_R7_removing_a_person_takes_them_off_every_item(open_app, plain_context):
    # [v1.1.0] qa.md "Remove a person and they leave every item" on K1, the disabled look compared with bill-empty.html.
    # The needs marker, the card's message and the strip are the next test's.
    page = open_app(seed=seeds.S1).page
    open_people_first(page)
    remove_button(page, "Chen").click()
    assert person_rows(page) == [person_row(1, "Aisyah", "Aisyah", disabled=True), person_row(2, "Ben", "Ben", disabled=True)]
    removes = "ul.people li.field.person button.icon-btn"
    golden = open_golden(plain_context, "bill-empty").locator(removes)
    for number in (0, 1):
        assert support.specimen_props(page.locator(removes).nth(number), GOLDEN_LOOK) == \
            support.specimen_props(golden.nth(number), GOLDEN_LOOK)
    for name, _, _ in S1_ITEMS:
        assert who_group(page, name).get_by_role("button").all_inner_texts() == ["Aisyah", "Ben"]


@pytest.mark.xfail(strict=True, reason="task A11")
def test_R7_the_item_left_with_nobody_needs_a_person_on_the_card_and_the_strip(open_app):
    # The rest of qa.md "Remove a person and they leave every item". The needs marker is task A8's, the card's div.r-msg
    # A9's and the strip's message A11's.
    page = open_app(seed=seeds.S1).page
    open_people_first(page)
    remove_button(page, "Chen").click()
    marked = page.evaluate("() => [...document.querySelectorAll('li.item.needs')].map((li) => li.querySelector('input').value)")
    assert marked == ["Mee goreng mamak"]
    message = "1 item still needs a person. Tap who had it to see the splits."
    assert support.reads(page, "#rbody div.r-msg") == message
    assert visible_text(page, "#stripInfo") == message


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


@pytest.mark.xfail(strict=True, reason="task A8")
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


@pytest.mark.xfail(strict=True, reason="task A8")
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
    open_charges_first(page)
    for label, value in (("Service charge", "10"), ("SST", "6")):
        field = rate_field(page, label)
        assert field.input_value() == value and field.get_attribute("aria-describedby") == "charges-hint"
        assert [field.get_attribute(a) for a in ("inputmode", "autocomplete", "type")] == ["decimal", "off", "text"]
        wrapper = page.locator(f"span.field.percent:has(#{field.get_attribute('id')})")
        assert wrapper.locator("input + .unit").inner_text() == "%"
    assert page.locator("p.hint#charges-hint").inner_text() == "Set a charge to 0 if your bill already includes it."


@pytest.mark.xfail(strict=True, reason="task A6")
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
    open_charges_first(page)
    support.replace_text(page, rate_field(page, "Service charge"), "")
    page.keyboard.press("Tab")
    assert page.locator("p.error").count() == 0 and page.locator("[aria-invalid]").count() == 0
    assert card_text(page) == BLOCKED_CARD["rates"]  # the v1.1.0 card since task A2 (BUILD.md, A2, Q-A2-3)


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


def test_R9_a_subtotal_drives_the_even_split(open_app):
    page = open_app().page
    subtotal_field(page).fill("100.00")
    assert summary_rows(page) == S2_SUMMARY
    assert table_cells(page, "tbody") == [["Person 1", "RM 58.30"], ["Person 2", "RM 58.30"]]


@pytest.mark.xfail(strict=True, reason="task A9")
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


@pytest.mark.xfail(strict=True, reason="task A9")
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
    pytest.param(lambda page: (build_s2(page), support.replace_text(page, opened_rate_field("Service charge")(page), "")),
                 "Check the charges to see the shares.", id="rate-empty"),
    pytest.param(lambda page: (build_s1(page), support.replace_text(page, opened_rate_field("SST")(page), "25")),
                 "Check the charges to see the shares.", id="rate-too-high"),
    pytest.param(lambda page: (build_s2(page), support.replace_text(page, subtotal_field(page), "")),
                 "Enter the subtotal to see the shares.", id="subtotal-empty"),
    pytest.param(lambda page: switch_to(page, "By item"), "Add an item to see the shares.", id="no-items"),
    pytest.param(lambda page: (switch_to(page, "By item"), page.get_by_role("button", name="Add item").click()),
                 "Add an item to see the shares.", id="item-unpriced"),
    pytest.param(lambda page: (build_s1(page), support.replace_text(page, item_price(page, 1), "abc")),
                 "Give every item a price to see the shares.", id="item-bad-price"),
]


@pytest.mark.xfail(strict=True, reason="task A9")
@pytest.mark.parametrize("setup, message", BLOCKED_CASES)
def test_R17_when_the_shares_cannot_be_worked_out(open_app, setup, message):
    page = open_app().page
    setup(page)
    assert panel_text(page) == f"Shares\n{message}"
    assert page.locator("div.tape section").count() == 1 and page.locator("div.tape table, h2#h-summary, p.status").count() == 0
    assert page.locator(COPY_BUTTON).count() == 0


@pytest.mark.xfail(strict=True, reason="task A9")
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


@pytest.mark.xfail(strict=True, reason="task A9")
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
    open_charges_first(page)
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


@pytest.mark.xfail(strict=True, reason="task A10")
@pytest.mark.parametrize("build, expected", [(build_s2, S2_COPY), (build_s1, S1_COPY)], ids=["S2", "S1"])
def test_R22_copy_summary_puts_the_exact_text_on_the_clipboard(open_app, build, expected):
    page = open_app().page
    build(page)
    copy_summary(page)
    assert status_of(page) == ("Summary copied", "status")
    assert page.evaluate("window.testClipboardText") == expected and page.evaluate("window.testClipboardWrites") == 1


@pytest.mark.xfail(strict=True, reason="task A10")
def test_R23_the_browser_blocks_the_clipboard(open_app):
    page = open_app(clipboard="reject").page
    build_s2(page)
    before = panel_text(page)
    copy_summary(page)
    assert status_of(page) == (FAILED_COPY, "status status-failure")
    assert panel_text(page).replace(FAILED_COPY, "").strip() == before.strip()


@pytest.mark.xfail(strict=True, reason="task A10")
def test_R23_the_clipboard_api_is_missing(open_app):
    page = open_app(clipboard="missing").page
    build_s2(page)
    copy_summary(page)
    assert status_of(page) == (FAILED_COPY, "status status-failure")


@pytest.mark.xfail(strict=True, reason="task A10")
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


@pytest.mark.xfail(strict=True, reason="task A10")
def test_R22_a_failed_copy_is_replaced_by_the_next_attempt(open_app):
    page = open_app(clipboard="reject").page
    build_s2(page)
    copy_summary(page)
    page.evaluate("Clipboard.prototype.writeText = () => Promise.resolve()")
    copy_summary(page)
    assert status_of(page) == ("Summary copied", "status")


@pytest.mark.xfail(strict=True, reason="task A10")
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


@pytest.mark.xfail(strict=True, reason="task A10")
def test_R5_a_new_name_reaches_the_copied_text(open_app):
    page = open_app().page
    build_s1(page)
    person_field(page, 3).click()
    page.keyboard.press("End")
    page.keyboard.type(" Wei")
    copy_summary(page)
    assert page.evaluate("window.testClipboardText").splitlines()[4] == "Chen Wei RM 24.48"


@pytest.mark.xfail(strict=True, reason="task A10")
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
    (lambda page: opened_rate_field("SST")(page).fill("8"), lambda bill: bill["sstText"] == "8"),
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


@pytest.mark.parametrize("setup, golden, golden_note", [
    pytest.param({"seed": seeds.UNREADABLE["B1"]}, "bill-unreadable", "#notes > div.note", id="unreadable-note"),
    pytest.param({"init_scripts": [support.storage_driver("fail-get")]}, "states",
                 'section[aria-labelledby="c-s5"] div.notes > div.note', id="save-warning"),
])
def test_R3_the_notes_match_their_goldens(open_app, plain_context, setup, golden, golden_note):
    # The v1.1.0 form of 1.0's note specimen test (WR-05, mutant LIVE2: a stray aria-live and aria-pressed). Each note
    # is walked as a part of the page. The save warning's golden is the S5 frame of states.html, whose div.notes is
    # specimen chrome without the id (allowed difference 5), so the note itself is walked on both sides.
    page = open_app(**setup).page
    assert page.locator("#notes > div.note").count() == 1
    assert first_diff(dom_walk(page, "#notes > div.note"), golden_walk(plain_context, golden, selector=golden_note)) is None


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
    assert section_state(again) == [FOLDED, FOLDED]  # R26, sections fold by R48 on a reload (task A4)
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


# ---------------------------------------------------------------- Task A3: the notes and the save warning (R27, R28, R46, R47)
D_A, D_B, D_C = (support.storage_driver(name) for name in ("fail-set", "fail-get", "fail-getitem"))
STORAGE_COMES_BACK = "window.dispatchEvent(new CustomEvent('test:storage', { detail: false }))"
NOTES_JS = """() => [...document.querySelectorAll('#notes > *')].map((note) => ({
  cls: note.className, role: note.getAttribute('role'),
  icons: [...note.querySelectorAll(':scope > svg.ic > use')].map((use) => use.getAttribute('href')),
  text: note.querySelector('p') ? note.querySelector('p').textContent : null,
  buttons: [...note.querySelectorAll('button')].map((button) => [button.type, button.className, button.id,
    button.getAttribute('aria-label'), [...button.querySelectorAll('svg.ic > use')].map((use) => use.getAttribute('href'))]),
}))"""
WARNING = {"cls": "note is-warn", "role": "status", "icons": ["#i-warning"], "buttons": [],
           "text": "This bill is not being saved on this device. It will be lost when you close this tab."}
UNREADABLE_NOTE = {"cls": "note", "role": "status", "icons": ["#i-warning-circle"],
                   "text": "Your saved bill could not be read, so a new one was started.",
                   "buttons": [["button", "icon-btn", "dismissNote", "Dismiss note", ["#i-x"]]]}


def notes(page):
    """What #notes holds, one entry per child, in order (R27, R46)."""
    return page.evaluate(NOTES_JS)


def screen_walk(page):
    """The R3 walk of the bill on screen, everything of div.app but the top bar's notes."""
    return [dom_walk(page, "main.layout"), dom_walk(page, "#strip")]


def type_into(page, locator, text):
    """qa.md "type Y into X": click the field and type key by key."""
    locator.click()
    page.keyboard.type(text)


def type_at_end(page, locator, text):
    """qa.md "type Y at the end of X": click the field, move the caret to the end, type key by key."""
    locator.click()
    page.keyboard.press("End")
    page.keyboard.type(text)


def new_bill_draft_with_first_name(name):
    draft = json.loads(NEW_BILL_DRAFT)
    draft["bill"]["people"][0]["name"] = name
    return draft


@pytest.mark.parametrize("name", list(seeds.UNREADABLE))
def test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note(open_app, name):
    page = open_app(seed=seeds.UNREADABLE[name]).page
    assert notes(page) == [UNREADABLE_NOTE]
    # The screen under the note is a cold boot's, the bill-empty screen of R2. From task A4 that walk also holds
    # #peopleBlk data-open "true" (R48, ruling 1 of S6), so People opening is checked by the same line.
    cold_boot = screen_walk(open_app().page)
    assert screen_walk(page) == cold_boot
    assert stored_text(page) == NEW_BILL_DRAFT
    page.reload()
    assert notes(page) == [] and screen_walk(page) == cold_boot


def test_R27_dismissing_the_note(open_app):
    page = open_app(seed=seeds.UNREADABLE["B1"]).page
    assert notes(page) == [UNREADABLE_NOTE]
    page.evaluate("window.testNote = document.querySelector('#notes > div.note')")
    place = page.locator("#notes > div.note").bounding_box()
    open_dialog(page)
    page.get_by_role("button", name="Start new bill").click()
    # Start new bill does not show, hide or move the note (R27): the same element, in the same place.
    assert notes(page) == [UNREADABLE_NOTE] and page.evaluate("document.querySelector('#notes > div.note') === window.testNote")
    assert page.locator("#notes > div.note").bounding_box() == place
    page.get_by_role("button", name="Dismiss note").click()
    assert page.locator("div.note").count() == 0 and page.evaluate("document.activeElement.id") == "newBill"  # rule 12
    open_dialog(page)
    page.get_by_role("button", name="Start new bill").click()
    assert page.locator("div.note").count() == 0


STORAGE_DRIVERS = {"D-b": D_B, "D-c": D_C, "D-a": D_A}


def add_a_person_after_a_subtotal(page):
    """The gestures of the R28 outline: type "100.00" into Subtotal and click "Add person"."""
    type_into(page, subtotal_field(page), "100.00")
    page.get_by_role("button", name="Add person").click()


@pytest.mark.parametrize("driver", STORAGE_DRIVERS.values(), ids=STORAGE_DRIVERS.keys())
def test_R28_the_app_works_without_storage(open_app, driver):
    # 1.0's "no message about storage shows" is retired by R46 and R47. The card is read through the 1.0 panel until
    # task A9 replaces it (R19, R20). No page error, console error or CSP violation is checked at teardown.
    page = open_app(init_scripts=[driver]).page
    add_a_person_after_a_subtotal(page)
    assert summary_rows(page)[3][1] == "RM 116.60" and len(table_cells(page, "tbody")) == 3


@pytest.mark.xfail(strict=True, reason="task A11")
@pytest.mark.parametrize("driver", STORAGE_DRIVERS.values(), ids=STORAGE_DRIVERS.keys())
def test_R28_the_strip_follows_the_bill_without_storage(open_app, driver):
    page = open_app(init_scripts=[driver]).page
    add_a_person_after_a_subtotal(page)
    assert " ".join(page.locator("#stripInfo").inner_text().split()) == "Total RM 116.60"  # "the strip reads" (R49)


DRIVER_OUTCOMES_JS = """(name) => {
  const outcome = (act) => { try { act(); return 'ok'; } catch (error) { return error.name; } };
  const comeBack = () => window.dispatchEvent(new CustomEvent('test:storage', { detail: false }));
  if (name === 'fail-set') return [outcome(() => localStorage.setItem('t', '1')), (comeBack(), outcome(() => localStorage.setItem('t', '1')))];
  if (name === 'fail-get') return [outcome(() => localStorage), (comeBack(), outcome(() => localStorage.length))];
  if (name === 'fail-getitem') return [outcome(() => localStorage.getItem('t'))];
  localStorage.setItem('t', '1');
  localStorage.setItem('t', '2');
  return [window.testSetItemCalls];
}"""


@pytest.mark.parametrize("name, expected", [("fail-set", ["QuotaExceededError", "ok"]), ("fail-get", ["SecurityError", "ok"]),
                                            ("fail-getitem", ["SecurityError"]), ("count-set", [2])])
def test_R46_the_storage_drivers_do_what_how_to_run_says(open_app, name, expected):
    # The drivers' own control. A page with no app script, so only the driver touches storage.
    page = open_app(path="/docs/design/bill-even.html", init_scripts=[support.storage_driver(name)], allow_problems=True).page
    assert page.evaluate(DRIVER_OUTCOMES_JS, name) == expected


def test_R46_a_cold_boot_with_working_storage_shows_no_warning(open_app):
    assert notes(open_app().page) == []


def test_R46_the_first_failed_save_shows_the_warning(open_app):
    page = open_app(init_scripts=[D_A]).page
    assert notes(page) == []
    support.replace_text(page, person_field(page, 1), "A")
    assert notes(page) == [WARNING]
    # The bill keeps working. The label follows the name and the card follows the bill (R5, R17). The People summary
    # that also reads "A" is task A4's (R48), and a cold boot is in Even mode, so it has no toggles.
    assert remove_button(page, "A").count() == 1 and card_text(page) == BLOCKED_CARD["subtotal"]


def test_R46_the_warning_stays_while_saves_fail_and_a_reload_starts_without_it(open_app):
    page = open_app(init_scripts=[D_A]).page
    support.replace_text(page, person_field(page, 1), "A")
    assert notes(page) == [WARNING]
    add_a_person_after_a_subtotal(page)
    assert notes(page) == [WARNING]
    page.reload()
    assert notes(page) == []  # the boot read works (SW5)
    support.replace_text(page, person_field(page, 1), "A")
    assert notes(page) == [WARNING]


def test_R47_the_first_save_that_works_removes_the_warning(open_app):
    page = open_app(init_scripts=[D_A]).page
    support.replace_text(page, person_field(page, 1), "A")
    assert notes(page) == [WARNING]
    page.evaluate(STORAGE_COMES_BACK)
    type_at_end(page, person_field(page, 1), "B")
    assert notes(page) == [] and stored(page) == new_bill_draft_with_first_name("AB")  # the bill on screen (SW4)


@pytest.mark.parametrize("driver", [D_B, D_C], ids=["D-b", "D-c"])
def test_R46_a_failed_boot_read_shows_the_warning_in_the_first_render(open_app, driver):
    page = open_app(init_scripts=[driver]).page
    assert notes(page) == [WARNING]  # before any gesture, and no unreadable note
    assert screen_walk(page) == screen_walk(open_app().page)  # the bill-empty screen, People open from task A4


def test_R46_an_unreadable_draft_whose_reset_save_fails_shows_both_notes_the_warning_first(open_app):
    page = open_app(seed=seeds.UNREADABLE["B1"], init_scripts=[D_A]).page
    assert notes(page) == [WARNING, UNREADABLE_NOTE]  # CG-P5
    page.get_by_role("button", name="Dismiss note").click()
    assert notes(page) == [WARNING] and page.evaluate("document.activeElement.id") == "newBill"


def test_R47_a_storage_object_that_comes_back_clears_the_warning_without_a_reload(open_app):
    page = open_app(init_scripts=[D_B]).page
    assert notes(page) == [WARNING]
    page.evaluate(STORAGE_COMES_BACK)
    support.replace_text(page, person_field(page, 1), "A")
    assert notes(page) == [] and stored(page)["bill"]["people"][0]["name"] == "A"  # SW6


@pytest.mark.xfail(strict=True, reason="task A15")
def test_R47_a_change_that_writes_nothing_leaves_the_warning(open_app):
    page = open_app(seed=seeds.PA0, viewport=(1280, 800), init_scripts=[D_A]).page
    support.replace_text(page, person_field(page, 1), "A")
    assert notes(page) == [WARNING]
    page.evaluate(STORAGE_COMES_BACK)
    assert page.locator("#pickAgain").count() == 1  # the card's Pick again chip (R51, R54)
    page.locator("#pickAgain").click()
    splits = page.eval_on_selector_all("#splits > li > span.amt", "(amounts) => amounts.map((amount) => amount.textContent)")
    assert splits == ["RM 0.01", "RM 0.01", "RM 0.00"] and notes(page) == [WARNING]  # Pick again changed nothing (CG-P3)
    type_at_end(page, person_field(page, 1), "B")
    assert notes(page) == [] and stored(page)["bill"]["people"][0]["name"] == "AB"


WATCH_NOTES_JS = """() => { window.testNoteMutations = 0;
  new MutationObserver((records) => { window.testNoteMutations += records.length; }).observe(
    document.getElementById('notes'), { childList: true, subtree: true, characterData: true, attributes: true }); }"""


def test_R46_the_warnings_live_region_is_not_touched_on_every_keystroke(open_app):
    page = open_app(init_scripts=[D_A]).page
    support.replace_text(page, person_field(page, 1), "A")
    assert notes(page) == [WARNING]
    page.evaluate(WATCH_NOTES_JS)
    type_at_end(page, person_field(page, 1), "bcde")
    assert person_field(page, 1).input_value() == "Abcde" and page.evaluate("window.testNoteMutations") == 0  # SW7


# D-d. Filler keys from 1 MiB down to one character, then the first filler grows until even one more character is refused.
FILL_STORAGE_JS = """() => {
  let size = 1 << 20, count = 0;
  while (size >= 1) {
    try { localStorage.setItem(`test.fill.${count}`, 'x'.repeat(size)); count += 1; } catch { size = Math.floor(size / 2); }
  }
  let value = localStorage.getItem('test.fill.0'), grow = 1 << 20;
  while (grow >= 1) {
    try { localStorage.setItem('test.fill.0', value + 'x'.repeat(grow)); value += 'x'.repeat(grow); } catch { grow = Math.floor(grow / 2); }
  }
  return count;
}"""
EMPTY_STORAGE_JS = """() => Object.keys(localStorage).filter((key) => key.startsWith('test.fill.'))
  .forEach((key) => localStorage.removeItem(key))"""


def open_first(page, key):
    """qa.md "Open People first" and "open Charges first": below 1024 px, a click on the header row of the section
    `key` ("people" or "charges") when it is folded. From 1024 px the row is not shown and the step does nothing."""
    row = page.locator(f"#{key}Btn")
    if row.count() and row.is_visible() and row.get_attribute("aria-expanded") == "false":
        row.click()


def open_people_first(page):
    open_first(page, "people")


def open_charges_first(page):
    open_first(page, "charges")


def test_R46_a_real_full_storage_shows_the_warning_and_room_again_clears_it(open_app):
    page = open_app(seed=seeds.S1).page
    open_people_first(page)
    assert page.evaluate(FILL_STORAGE_JS) >= 1
    type_at_end(page, person_field(page, 3), " Wei")
    # The engine throws its own error through the app's own save. The card is read through the 1.0 panel until task A9.
    assert notes(page) == [WARNING] and table_cells(page, "tbody")[2][0] == "Chen Wei"
    page.evaluate(EMPTY_STORAGE_JS)
    type_at_end(page, person_field(page, 3), "x")
    assert notes(page) == [] and stored(page)["bill"]["people"][2]["name"] == "Chen Weix"


STORAGE_PROBES = ("QuotaExceededError", "SecurityError", "DOMException", "setTimeout", "setInterval", ".removeItem(")


def storage_problems(sources):
    """What the R47 scan finds in {name: text}. An error name, a timer or a removal anywhere, or a storage read or
    write other than the one boot read in loadDraft and the one write in saveDraft."""
    found = [f"{name}: {word}" for name, text in sources.items() for word in STORAGE_PROBES if word in text]
    for call in ("getItem(", "setItem("):
        count = sum(text.count(call) for text in sources.values())
        if count != 1:
            found.append(f"{call} {count} times")
    return found


def test_R47_the_app_reads_no_error_name_and_probes_nothing(tmp_path):
    # ".removeItem(" is the storage method. "removeItem(" alone also matches split-core's removeItem(bill, itemId),
    # which the Contracts import (BUILD.md, task A3, Q-A3-1).
    sources = {name: text for name, text in support.shipped_text().items() if name.startswith("src/")}
    assert storage_problems(sources) == []
    draft = sources["src/draft.js"]
    read = "text = storage.getItem(DRAFT_KEY);"
    assert read in draft
    planted = {"error-name": draft + '\nconst full = (e) => e.name === "QuotaExceededError";\n',
               "read-back": draft.replace(read, read + " storage.getItem(DRAFT_KEY);"),
               "timer": draft + "\nsetTimeout(() => {}, 0);\n"}
    for name, text in planted.items():
        copy = tmp_path / f"{name}-draft.js"
        copy.write_text(text, encoding="utf-8")
        assert storage_problems(dict(sources, **{"src/draft.js": copy.read_text(encoding="utf-8")})) != [], name


def test_R10_a_restored_bad_field_shows_its_error_at_once(open_app):
    page = open_app(seed=seeds.with_bill(seeds.S2, subtotalText="0", serviceText="31")).page
    assert page.locator("p.error#subtotal-error").inner_text() == "Enter an amount like 12.50"
    assert page.locator("p.error#rate-service-error").inner_text() == "Enter a rate from 0 to 30"
    assert page.locator("p.error#rate-sst-error").count() == 0


@pytest.mark.xfail(strict=True, reason="task A10")
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
    assert dialog.evaluate("(d) => d.matches(':modal')") and dialog.get_attribute("aria-describedby") == "newBody"
    assert dialog.get_attribute("aria-labelledby") == "newTitle"
    assert page.locator("#newBody").inner_text() == "This clears the people, items and amounts."
    assert [b.get_attribute("class") for b in dialog.get_by_role("button").all()] == ["btn btn-danger btn-lg", "btn btn-ghost btn-lg"]
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
    box = page.locator("dialog#newDlg").bounding_box()
    inside = [(box["x"] + 3, box["y"] + 3), (box["x"] + box["width"] - 3, box["y"] + box["height"] - 3),
              centre_of(page.locator("#newTitle")), centre_of(page.locator("#newBody"))]
    for point in inside:
        page.mouse.click(*point)
        assert dialog_is_open(page) is True, point
    assert stored_text(page) == seeds.S2


@pytest.mark.parametrize("close", ["cancel", "escape", "backdrop-corner", "backdrop-over-a-field"])
def test_R30_leaving_the_dialog_without_starting_over(open_app, close):
    page = open_app(seed=seeds.S2).page
    open_people_first(page)  # so a field is drawn under the backdrop (R48)
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
    assert page.locator("dialog#newDlg").evaluate("(d) => d.open") is False
    assert focused(page) == "New bill" and stored_text(page) == seeds.S2
    assert snapshot(page) == snapshot(open_app(seed=seeds.S2).page) and summary_rows(page) == S2_SUMMARY


def test_R31_start_over(open_app):
    page = open_app(seed=seeds.S1).page
    open_dialog(page)
    page.get_by_role("button", name="Start new bill").click()
    assert page.locator("dialog#newDlg").evaluate("(d) => d.open") is False and focused(page) == "New bill"
    assert section_state(page) == [OPEN, FOLDED]  # People open, Charges folded, as at load (R48, task A4)
    assert [f.input_value() for f in page.locator("li.person input").all()] == ["Person 1", "Person 2"]
    assert page.locator("#mode-even").is_checked() and subtotal_field(page).input_value() == ""
    open_charges_first(page)  # the rate fields sit in the folded Charges section below 1024 px
    assert (rate_field(page, "Service charge").input_value(), rate_field(page, "SST").input_value()) == ("10", "6")
    # The bill-empty card of R2, which task A2 builds (BUILD.md, A2, judgment call on the 1.0 tests).
    assert card_text(page) == BLOCKED_CARD["subtotal"] and stored_text(page) == NEW_BILL_DRAFT
    page.reload()
    assert card_text(page) == BLOCKED_CARD["subtotal"] and page.locator("li.person").count() == 2
    assert section_state(page) == [OPEN, FOLDED]  # an untouched new bill opens People again (CG-P4)


@pytest.mark.xfail(strict=True, reason="task A16")
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
    # Start new bill folds Charges (R48, R31), so the rate rows open it first.
    pytest.param(seeds.with_bill(seeds.S2, serviceText="31"), None, opened_rate_field("Service charge"), id="service"),
    pytest.param(seeds.with_bill(seeds.S2, sstText="25"), None, opened_rate_field("SST"), id="sst"),
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


# ---------------------------------------------------------------- RD-3: a press below a field that is being left (R10, CG-3)
# Leaving a bad amount or rate shows its error, which pushes everything under it down by one line. When the
# field is left by a press on a control under it, the press must still land on that control (RD-3, 2026-10-09).
# A click is recorded by the button it falls in, or else by its target, so a press on a header row counts as that row
# whichever of its spans is under the point. A target with no id is recorded by its tag.
RECORD_CLICKS_JS = """() => {
  window.testClicks = [];
  document.addEventListener('click', (event) => { const hit = event.target.closest('button') || event.target;
    window.testClicks.push(hit.id || hit.tagName.toLowerCase()); }, true);
}"""
PRESS_CASES = [  # (seed, field, bad text, the control pressed under it, error id, the click's target, the error's text)
    # Since task A4 nothing sits under the Subtotal, and the target is the Charges header row above it, which the error
    # does not move (the v1.1.0 qa.md row). The click reaches it once and the error shows after.
    pytest.param(None, lambda page: page.locator("#subtotal"), "0", lambda page: page.locator("#chargesBtn"),
                 "subtotal-error", "chargesBtn", AMOUNT_MESSAGE, id="subtotal"),
    pytest.param(seeds.S1, lambda page: item_price(page, 2), "13.505", lambda page: toggle(page, "Char kuey teow", "Aisyah"),
                 "price-error-i5", "button", AMOUNT_MESSAGE, id="item-price"),
    pytest.param(None, opened_rate_field("Service charge"), "31", lambda page: page.locator("#charges-hint"),
                 "rate-service-error", "charges-hint", SERVICE_MESSAGE, id="service"),
    pytest.param(None, opened_rate_field("SST"), "25", lambda page: page.locator("#charges-hint"),
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
    support.replace_text(page, opened_rate_field("SST")(page), "25")
    box = page.locator("h1.word").bounding_box()
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
    box = page.locator("h1.word").bounding_box()
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
    support.replace_text(page, opened_rate_field("SST")(page), "25")
    box = page.locator("h1.word").bounding_box()
    page.mouse.move(box["x"] + box["width"] + 40, box["y"] + box["height"] / 2)
    page.mouse.down(button="right")
    assert page.locator("p.error#rate-sst-error").count() == 1  # before any release
    page.mouse.up(button="right")


def test_R10_a_cancelled_press_releases_the_waiting_error(open_app):
    # A drag that the browser turns into a native drag ends with pointercancel and no mouseup. Playwright cannot start
    # one, so the event is dispatched on the document as the browser would (a read-only stand-in, no app hook).
    page = open_app().page
    support.replace_text(page, opened_rate_field("SST")(page), "25")
    box = page.locator("h1.word").bounding_box()
    page.mouse.move(box["x"] + box["width"] + 40, box["y"] + box["height"] / 2)
    page.mouse.down()
    assert page.locator("p.error").count() == 0
    page.evaluate("() => document.dispatchEvent(new PointerEvent('pointercancel', { bubbles: true }))")
    assert page.locator("p.error#rate-sst-error").count() == 1  # before the button comes up
    page.mouse.up()


# ---------------------------------------------------------------- Code review CR-01, WR-01, WR-06: ghost clicks and the backdrop
# A double click or a double tap is two clicks. The first can close the dialog or remove a row, so the second lands on
# whatever is drawn under the pointer afterwards. `event.detail` is the click count: 1 for the first, 2 for the second,
# except that WebKit gives each tap of a double tap 1, which spec R57 (b) catches by time and place.
PHONES = [(375, 667), (360, 640), (412, 732)]  # the sizes where QA and the code review reproduced it, with the S1 bill
# qa.md "A body recorder", two halves. The body half keeps the click counts of the clicks and of the mouse presses that reach
# the page. The guard cancels both kinds (RG-CR-02), so a test of how long it lasts has to watch both: a guard that kept only
# its press listener changes no click. The window half (R57 (b), task A17) keeps every pointerdown, mousedown and click
# before the app's guard can cancel it, so the proof that a repeat was cancelled reads the events themselves, whatever lies
# under the point (19 WebKit cases passed at A2 only because the layout had moved). Resetting the arrays restarts both.
RECORD_BODY_CLICKS_JS = """() => {
  window.testBodyClicks = [];
  window.testBodyPresses = [];
  window.testGesture = [];
  document.body.addEventListener('click', (event) => window.testBodyClicks.push(event.detail), false);
  document.body.addEventListener('mousedown', (event) => window.testBodyPresses.push(event.detail), false);
  for (const type of ['pointerdown', 'mousedown', 'click']) window.addEventListener(type, (event) => window.testGesture.push(event), true);
}"""
RESET_RECORDER_JS = "() => { window.testBodyClicks = []; window.testBodyPresses = []; window.testGesture = []; }"
# Read after the gesture, so defaultPrevented is each event's state once its dispatch is over.
GESTURE_JS = """() => window.testGesture.map((event) => ({ type: event.type, pointerType: event.pointerType ?? null,
  detail: event.detail, timeStamp: event.timeStamp, x: event.clientX, y: event.clientY, prevented: event.defaultPrevented }))"""
GESTURE_PRESSES = {"single": 1, "mouse-double": 2, "mouse-triple": 3, "touch-double": 2}


def settle(page):
    """Two animation frames, so every click the browser still had queued from a gesture has been delivered."""
    page.evaluate("() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))")


WHOLE_DOUBLE_CLICK = {"presses": [1, 2], "clicks": [1, 2]}  # what the page sees of a real double click nobody holds back


def seen_by_the_page(page):
    """The click counts of the presses and clicks that reached the body since RECORD_BODY_CLICKS_JS. A cancelled one is missing."""
    return page.evaluate("({ presses: window.testBodyPresses, clicks: window.testBodyClicks })")


def presses_and_clicks(page):
    """The mousedown and the click events the window half of the recorder kept, in order, as two lists."""
    events = page.evaluate(GESTURE_JS)
    return [e for e in events if e["type"] == "mousedown"], [e for e in events if e["type"] == "click"]


def assert_only_press_1_and_click_1_reached_the_page(page, presses, tapped=False):
    """qa.md "Only press 1 and click 1 reached the page" for a gesture of `presses` presses (spec R57 (b)). The body
    counted one press and one click, the window saw every press and click of the gesture, and each one after the first
    was cancelled. For a double tap (`tapped`), its second click also came less than 500 ms after the first and within
    22 px, or the case fails and names the gap, because it did not test a double tap."""
    downs, clicks = presses_and_clicks(page)
    assert (len(downs), len(clicks)) == (presses, presses), (
        f"the window saw {len(downs)} presses and {len(clicks)} clicks, not {presses} of each")
    if tapped:
        gap = clicks[1]["timeStamp"] - clicks[0]["timeStamp"]
        across, down = abs(clicks[1]["x"] - clicks[0]["x"]), abs(clicks[1]["y"] - clicks[0]["y"])
        assert gap < 500 and across <= 22 and down <= 22, (
            f"not a double tap: the second click came {gap:.1f} ms after the first, {across} px across and {down} px down")
    uncancelled = [f"{kind} {number}" for kind, events in (("mousedown", downs), ("click", clicks))
                   for number, event in enumerate(events, start=1) if number > 1 and not event["prevented"]]
    assert uncancelled == [], f"a repeat reached the page uncancelled: {', '.join(uncancelled)}"
    assert seen_by_the_page(page) == {"presses": [1], "clicks": [1]}


def activate_twice(page, how, point):
    """A double click (mouse) or a double tap (touch) at one point."""
    if how == "touch":
        page.touchscreen.tap(*point)
        page.touchscreen.tap(*point)
    else:
        page.mouse.dblclick(*point)
    settle(page)


def dialog_is_open(page):
    return page.locator("dialog#newDlg").evaluate("(d) => d.open")


@pytest.mark.parametrize("how", ["mouse", "touch"])
@pytest.mark.parametrize("viewport", PHONES, ids=[f"{w}x{h}" for w, h in PHONES])
def test_R30_a_double_click_or_double_tap_on_cancel_changes_nothing(open_app, viewport, how):
    # CR-01 (QA F-1). On a by-item bill the control under Cancel is often a person's toggle.
    page = open_app(seed=seeds.S1, viewport=viewport, touch=how == "touch").page
    before = snapshot(page)
    open_dialog(page)
    page.evaluate(RECORD_BODY_CLICKS_JS)
    activate_twice(page, how, centre_of(page.get_by_role("button", name="Cancel", exact=True)))
    assert dialog_is_open(page) is False and focused(page) == "New bill"
    assert stored_text(page) == seeds.S1 and snapshot(page) == before
    # R57 (b): the end state alone passes at 360 x 640 in WebKit by layout, the recorder proves the second tap was cancelled.
    assert_only_press_1_and_click_1_reached_the_page(page, 2, tapped=how == "touch")


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
    assert_only_press_1_and_click_1_reached_the_page(page, 2, tapped=how == "touch")


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
    drag(page, centre_of(page.locator("#newBody")), (10, 10))
    assert dialog_is_open(page) is True


def test_R30_a_press_that_starts_on_the_backdrop_and_ends_in_the_dialog_keeps_it_open(open_app):
    page = open_app(seed=seeds.S2).page
    open_dialog(page)
    drag(page, (10, 10), centre_of(page.locator("#newBody")))
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
    if rows == "li.person":
        open_people_first(page)  # folded on a restored bill below 1024 px (R48)
    assert page.locator(rows).count() == before
    activate_twice(page, how, centre_of(page.get_by_role("button", name=button, exact=True)))
    assert page.locator(rows).count() == before - 1


@pytest.mark.parametrize("seed, button, rows, before", REMOVE_CASES)
def test_R7_two_separate_clicks_and_a_key_press_still_remove_a_row_each(open_app, seed, button, rows, before):
    page = open_app(seed=seed).page
    if rows == "li.person":
        open_people_first(page)  # folded on a restored bill below 1024 px (R48)
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
# The v1.1.0 sizes of these outlines (qa.md). The R6 and R7 rows use them since task A5, R12 moves with task A8 and R29
# with task A16, and SIZES goes with the last of them.
V11_SIZES = [(360, 780), (390, 844), (1280, 800)]
V11_SIZE_IDS = [f"{w}x{h}" for w, h in V11_SIZES]
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
@pytest.mark.parametrize("viewport", V11_SIZES, ids=V11_SIZE_IDS)
@pytest.mark.parametrize("seed, button, rows, focus_after", LAST_ROW_CASES)
def test_R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing(
        open_app, seed, button, rows, focus_after, viewport, gesture):
    # SEC-01: the second click landed on "Add person" (people) and saved a blank person. The last item's second click
    # lands on inert space, so for items the focus check is what shows the guard: the press must not move focus to the body.
    page = open_app(seed=seed, viewport=viewport, touch=gesture == "touch-double").page
    if rows == "li.person":
        open_people_first(page)  # folded on a restored bill below 1024 px (R48)
    before = page.locator(rows).count()
    page.evaluate(RECORD_BODY_CLICKS_JS)
    gesture_at(page, gesture, centre_of(page.get_by_role("button", name=button, exact=True)))
    assert page.locator(rows).count() == before - 1
    assert stored(page)["bill"] == bill_without_last(seed, rows)  # no blank row, and the id counter did not move
    assert support.active_label(page) == focus_after
    # R57 (b): for S2 and S8 the end state alone passes in WebKit by layout, the recorder proves the repeat was cancelled.
    assert_only_press_1_and_click_1_reached_the_page(page, GESTURE_PRESSES[gesture], tapped=gesture == "touch-double")


@pytest.mark.parametrize("how", ["mouse", "touch"])
@pytest.mark.parametrize("seed, button, rows, before", REMOVE_CASES)
def test_R34_after_a_double_click_on_remove_focus_is_where_one_click_puts_it(open_app, seed, button, rows, before, how):
    # The repeat press used to land on the next row's Remove button and move focus there (or to the body). Cancelled, it moves nothing.
    page = open_app(seed=seed, touch=how == "touch").page
    if rows == "li.person":
        open_people_first(page)  # folded on a restored bill below 1024 px (R48)
    activate_twice(page, how, centre_of(page.get_by_role("button", name=button, exact=True)))
    # qa.md "one row is gone" (task A5): a second removal also leaves focus on the name at position 2.
    assert page.locator(rows).count() == before - 1
    assert support.active_label(page) == ("Item 2 name" if rows == "li.item" else "Person 2 name")


def test_R7_a_separate_click_on_the_same_point_is_a_press_of_its_own(open_app):
    # [v1.1.0] qa.md "A press of its own is never held back", first part. Add person no longer slides under the pointer, so
    # the body recorder shows the second click reached the page. For a mouse the guard goes by click count, not by time or
    # place (spec R57 (b)). The 1.0 form, test_R7_a_separate_click_on_what_slid_under_the_pointer_is_not_held_back, read
    # Add person under the point.
    page = open_app(seed=seeds.S2).page
    open_people_first(page)
    page.evaluate(RECORD_BODY_CLICKS_JS)
    point = centre_of(page.get_by_role("button", name="Remove Chen", exact=True))
    page.mouse.click(*point)
    page.mouse.click(*point)  # a click of its own, count 1, at once
    settle(page)
    assert seen_by_the_page(page) == {"presses": [1, 1], "clicks": [1, 1]}
    assert [p["name"] for p in stored(page)["bill"]["people"]] == ["Aisyah", "Ben"]


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
    open_people_first(page)  # folded on a restored bill below 1024 px (R48)
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
@pytest.mark.parametrize("viewport", V11_SIZES, ids=V11_SIZE_IDS)
@pytest.mark.parametrize("people", [2, 3, 4, 5])
def test_R6_a_repeat_press_on_add_person_adds_one_person_and_keeps_it(open_app, people, viewport, gesture, place):
    # [v1.1.0] Add person is in the heading row (under the list below 1024 px), so no new Remove lies under it. The proof
    # is the body recorder. Below 1024 px a person who starts a new grid row pushes Add person down, and the repeat lands
    # on that person's name (measured, qa/people-render).
    seed = people_bill(people)
    page = open_app(seed=seed, viewport=viewport, touch=gesture == "touch-double").page
    open_people_first(page)  # folded on a restored bill below 1024 px (R48)
    page.evaluate(RECORD_BODY_CLICKS_JS)
    gesture_at(page, gesture, press_point(page.get_by_role("button", name="Add person", exact=True), place))
    assert page.locator("li.person").count() == people + 1
    assert stored(page)["bill"] == bill_after_one_add(seed, "people")  # the blank row stayed, and one id was spent, not two
    assert support.active_label(page) == f"Person {people + 1} name"  # R34
    # R57 (b): the end state alone passes in WebKit by layout, the recorder proves the repeat was cancelled.
    assert_only_press_1_and_click_1_reached_the_page(page, GESTURE_PRESSES[gesture], tapped=gesture == "touch-double")


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
    assert_only_press_1_and_click_1_reached_the_page(page, GESTURE_PRESSES[gesture], tapped=gesture == "touch-double")


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
    assert dialog_is_open(page) is True and focused(page) == "Cancel" and stored_text(page) == seeds.S1
    assert_only_press_1_and_click_1_reached_the_page(page, GESTURE_PRESSES[gesture], tapped=gesture == "touch-double")


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


# ---------------------------------------------------------------- v1.1.0 task A17: held keys and double taps (R57)
# (a) A held key sends keydown after keydown with `repeat` true. The click that removes the only item moves focus to
# "Add item", so each repeat of a held Enter added a blank item (SEC-04 of 1.0). (b) A double tap is one press in both
# engines. The double tap rows of R6, R7, R12, R29 and R30 above prove (b) through the body recorder, the Node table in
# tests/repeat.test.js pins its edges, and the last scenario here is its other side: a slow tap or a tap elsewhere acts.
def has_focus(locator):
    return locator.evaluate("(el) => el === document.activeElement")


def tab_until(page, locator, limit=60):
    """qa.md "press Tab until X has focus", at most `limit` presses."""
    for _ in range(limit):
        if has_focus(locator):
            return
        page.keyboard.press("Tab")
    assert has_focus(locator), f"Tab did not reach {locator} in {limit} presses"


def hold(page, key):
    """qa.md "hold": keyboard.down, 520 ms, four more keyboard.down (a key already down sends keydown with repeat true), keyboard.up."""
    page.keyboard.down(key)
    page.wait_for_timeout(520)
    for _ in range(4):
        page.keyboard.down(key)
    page.keyboard.up(key)
    settle(page)


def hold_enter_on_the_only_remove(open_app):
    """The first scenario's gesture on K1 with only its last item. Returns the page and the nextId noted before it."""
    page = open_app(seed=ONE_ITEM).page
    next_id = stored(page)["bill"]["nextId"]
    tab_until(page, page.get_by_role("button", name="Remove Satay, 10 sticks", exact=True))
    hold(page, "Enter")
    return page, next_id


def test_R57_a_held_enter_on_the_only_items_remove_removes_that_item_only(open_app):
    page, next_id = hold_enter_on_the_only_remove(open_app)
    bill = stored(page)["bill"]
    assert (len(bill["items"]), bill["nextId"]) == (0, next_id), "the held key's repeats added blank items"
    assert has_focus(page.get_by_role("button", name="Add item", exact=True))
    assert card_text(page) == BLOCKED_CARD["no-prices"]


@pytest.mark.xfail(strict=True, reason="task A11")
def test_R57_after_a_held_enter_on_the_only_remove_the_strip_reads_the_empty_message(open_app):
    # The strip half of the first scenario's last line. The strip's message is task A11's (R49).
    page, _ = hold_enter_on_the_only_remove(open_app)
    assert page.locator("#stripInfo").inner_text() == "Add each item and tap who had it to see the splits."


def test_R57_a_held_enter_on_new_bill_leaves_the_dialog_open_on_cancel(open_app):
    page = open_app(seed=seeds.S1).page
    tab_until(page, new_bill_button(page))
    # Four repeats on 1.0 closed and opened the dialog twice and ended open on Cancel, so the end state alone cannot
    # tell. The dialog must never close while the key is held.
    page.locator("dialog#newDlg").evaluate("(d) => { window.testCloses = 0; d.addEventListener('close', () => { window.testCloses += 1; }); }")
    hold(page, "Enter")
    assert page.evaluate("window.testCloses") == 0, "a repeat of the held Enter closed the dialog"
    assert dialog_is_open(page) is True and focused(page) == "Cancel" and stored_text(page) == seeds.S1


def test_R57_separate_presses_still_act_and_a_held_letter_still_types(open_app):
    page = open_app(seed=ONE_ITEM).page
    next_id = stored(page)["bill"]["nextId"]
    tab_until(page, page.get_by_role("button", name="Remove Satay, 10 sticks", exact=True))
    page.keyboard.press("Enter")
    assert has_focus(page.get_by_role("button", name="Add item", exact=True))
    page.keyboard.press("Enter")
    assert stored(page)["bill"]["items"] == [{"id": f"i{next_id}", "name": "", "priceText": "", "who": []}]
    name = page.get_by_role("textbox", name="Item 1 name", exact=True)
    assert has_focus(name)
    hold(page, "a")
    assert name.input_value() == "aaaaa"


def slow_tap_then_tap_elsewhere(open_app):
    """The gestures of qa.md "A slow second tap, or a quick tap elsewhere, is never held back", on K2 with touch at
    390 x 844. Returns what each part saw: the gap or the two points, the body's counts, whether the second tap's
    mousedown and click were cancelled, where focus is and the names in the draft after the part."""
    page = open_app(seed=seeds.S2, touch=True).page
    open_people_first(page)
    page.evaluate(RECORD_BODY_CLICKS_JS)
    add_person = page.get_by_role("button", name="Add person", exact=True)
    first_name = page.get_by_role("textbox", name="Person 1 name", exact=True)

    def part(first, second, wait):
        page.evaluate(RESET_RECORDER_JS)
        page.touchscreen.tap(*first)
        if wait:
            page.wait_for_timeout(wait)
        page.touchscreen.tap(*second)
        settle(page)
        downs, clicks = presses_and_clicks(page)
        seen = seen_by_the_page(page)
        return {"gap": clicks[1]["timeStamp"] - clicks[0]["timeStamp"], "first": first, "second": second,
                "counted": (len(seen["presses"]), len(seen["clicks"])),
                "cancelled": (downs[1]["prevented"], clicks[1]["prevented"]), "first_name_focused": has_focus(first_name),
                "names": [person["name"] for person in stored(page)["bill"]["people"]]}

    point = centre_of(add_person)
    slow = part(point, point, 600)
    elsewhere = part(centre_of(add_person), centre_of(first_name), 0)
    return slow, elsewhere


def test_R57_a_slow_second_tap_or_a_quick_tap_elsewhere_is_never_held_back(open_app):
    # The draft lines of the scenario are the next test.
    slow, elsewhere = slow_tap_then_tap_elsewhere(open_app)
    assert slow["gap"] >= 500, f"the second tap came {slow['gap']:.1f} ms after the first, so it was not a slow second tap"
    assert slow["counted"] == (2, 2), f"the body counted {slow['counted']} presses and clicks"
    assert slow["cancelled"] == (False, False), "the slow second tap was held back"
    (ax, ay), (bx, by) = elsewhere["first"], elsewhere["second"]
    assert abs(bx - ax) > 22 or abs(by - ay) > 22, f"Add person {(ax, ay)} and Person 1 name {(bx, by)} lie within 22 px"
    assert elsewhere["counted"] == (2, 2), f"the body counted {elsewhere['counted']} presses and clicks"
    assert elsewhere["cancelled"] == (False, False), "the quick tap elsewhere was held back"
    assert elsewhere["first_name_focused"] is True


def test_R57_a_slow_second_tap_and_a_quick_tap_elsewhere_change_the_draft_as_two_presses(open_app):
    # K2 has three people, so the first tap fills the second column and Add person stays under the point for the slow
    # second tap (on the 1.0 People block it moved a cell down, task A5).
    slow, elsewhere = slow_tap_then_tap_elsewhere(open_app)
    assert slow["names"] == ["Aisyah", "Ben", "Chen", "", ""]
    assert len(elsewhere["names"]) == 6


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


@pytest.mark.xfail(strict=True, reason="task A18")
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
    (seeds.S1, opened_rate_field("Service charge"), "12.5"),
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


@pytest.mark.xfail(strict=True, reason="task A18")
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


@pytest.mark.xfail(strict=True, reason="task A18")
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


@pytest.mark.xfail(strict=True, reason="task A18")
def test_R35_content_width_of_the_header_and_the_note_at_1280_by_800(open_app):
    page = open_app(seed=seeds.UNREADABLE["B1"], viewport=(1280, 800)).page
    assert page.locator("div.note").bounding_box()["width"] == 1040  # ST-15
    bar = page.locator("header.bar")
    assert bar.bounding_box()["width"] == 1104
    assert bar.evaluate("(e) => [getComputedStyle(e).paddingLeft, getComputedStyle(e).paddingRight]") == ["32px", "32px"]


WATCH_TRANSITIONS_JS = """() => { window.testTransitions = [];
  document.addEventListener('transitionrun', (event) => window.testTransitions.push(event.propertyName), true); }"""


@pytest.mark.parametrize("setting, duration", [
    ("reduce", "0s"),
    pytest.param("no-preference", "0.12s, 0.12s", marks=pytest.mark.xfail(strict=True, reason="task A18"))])
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


@pytest.mark.xfail(strict=True, reason="task A18")
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


TAB_ICON_ROOT_XMLNS = re.compile(r"""\A(<svg\b[^>]*?)\s+xmlns=(["'])""" + re.escape(SVG_NAMESPACE) + r"\2")


def network_problems(name, text):
    """R39. The two allowed scheme strings are the namespace as the first argument of createElementNS (CG-10) and,
    in src/icon.svg only, the xmlns of the root element. Anything else with a scheme is reported."""
    found = [f"{token} in {name}" for token in NETWORK_APIS if token in text]
    allowed_gone = NAMESPACE_CALLS.sub("", text)
    if name.endswith("icon.svg"):
        allowed_gone = TAB_ICON_ROOT_XMLNS.sub(r"\1", allowed_gone, count=1)
    found += [f"scheme string {match.group(0)} in {name}" for match in SCHEME.finditer(allowed_gone)]
    return found + ([f"namespace outside its two places in {name}"] if SVG_NAMESPACE in allowed_gone else [])


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


def test_R39_nothing_leaves_the_device_by_the_static_scan(tmp_path):
    shipped = support.shipped_text()
    assert "src/icon.svg" in shipped
    assert [problem for name, text in shipped.items() for problem in network_problems(name, text)] == []
    assert "://" not in shipped["index.html"]
    # The scan's teeth on planted copies: a second xmlns in the tab icon, another namespace in a script.
    icon_copy, script_copy = tmp_path / "icon.svg", tmp_path / "icons.js"
    icon_copy.write_text(shipped["src/icon.svg"].replace("<path ", f'<path xmlns="{SVG_NAMESPACE}" ', 1), encoding="utf-8")
    script_copy.write_text(shipped["src/ui/icons.js"] + '\nconst link = "http://www.w3.org/1999/xlink";\n', encoding="utf-8")
    for copy in (icon_copy, script_copy):
        assert network_problems(f"planted {copy.name}", copy.read_text(encoding="utf-8")) != [], copy.name


def test_R39_the_network_scan_has_teeth():
    ok = f'const node = document.createElementNS("{SVG_NAMESPACE}", tag);'
    assert network_problems("icons.js", ok) == []
    assert network_problems("icons.js", ok.replace('"', "'")) == [] and network_problems("icons.js", ok.replace('"', "`")) == []
    icon_root = f"<svg xmlns='{SVG_NAMESPACE}' viewBox='0 0 16 16'><path d='M0,0Z'/></svg>"
    assert network_problems("src/icon.svg", icon_root) == [] and network_problems("src/other.svg", icon_root) != []
    for bad in ["fetch('/x')", "new XMLHttpRequest()", "new WebSocket(u)", "new EventSource(u)", "navigator.sendBeacon(u)",
                "navigator.serviceWorker", "const u = 'https://example.com/a'", "import x from 'http://a.b/c.js'",
                f'document.createElementNS("urn:other", "svg"); // {SVG_NAMESPACE}', f'const ns = "{SVG_NAMESPACE}";',
                f'document.createElementNS(tag, "{SVG_NAMESPACE}")', f"// the icons use createElementNS and {SVG_NAMESPACE}"]:
        assert network_problems("x.js", bad), bad


ICON_NAMES = ["x", "plus", "copy", "check", "caret", "shuffle", "warning", "warning-circle", "mark", "seal-check"]


def test_R39_the_run_time_icons_come_from_createElementNS(open_app):
    sources = {name: text for name, text in support.shipped_text().items() if name.startswith("src/")}
    calls = sum(text.count("createElementNS(") for text in sources.values())
    assert calls >= 1 and calls == sum(len(NAMESPACE_CALLS.findall(text)) for text in sources.values())  # every call names the namespace
    svgs = open_app(seed=seeds.S1, viewport=(1280, 800)).page.evaluate("""() => [...document.querySelectorAll('body svg')].map((svg) => ({
      cls: svg.getAttribute('class'), first: svg === document.body.firstElementChild, inBrand: !!svg.closest('div.brand'),
      hidden: svg.getAttribute('aria-hidden'), focusable: svg.getAttribute('focusable'),
      children: [...svg.children].map((child) => [child.localName, child.getAttribute('href')]) }))""")
    assert svgs[0]["cls"] == "sprite" and svgs[0]["first"]
    assert [svg["inBrand"] for svg in svgs if svg["cls"] == "mark"] == [True]
    icons = [svg for svg in svgs if svg["cls"] not in ("sprite", "mark")]
    assert icons and all(svg["cls"].split()[0] in ("ic", "seal") for svg in icons), svgs
    allowed = [["use", f"#i-{name}"] for name in ICON_NAMES]
    assert all(svg["hidden"] == "true" and svg["focusable"] == "false" and len(svg["children"]) == 1 and svg["children"][0] in allowed
               for svg in icons), icons


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
    assert page.locator("dialog#newDlg").evaluate("(d) => d.open && d.matches(':modal')")
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


# ---------------------------------------------------------------- v1.1.0 task A4: sections, header rows, folds and the reveal (R48, R26)
# Each read is one page.evaluate that gives null for an element the page does not hold, so a missing part fails on the
# assertion that names it and never on a wait.
SECTION_STATE_JS = """() => ['people', 'charges'].map((key) => [
  document.getElementById(`${key}Blk`)?.getAttribute('data-open') ?? null,
  document.getElementById(`${key}Btn`)?.getAttribute('aria-expanded') ?? null])"""
FOLDED, OPEN = ["false", "false"], ["true", "true"]


def section_state(page):
    """[data-open, aria-expanded] of People, then of Charges (R48). A pair of equal values is a row that says what its
    section is."""
    return page.evaluate(SECTION_STATE_JS)


def displayed(page, *selectors):
    """For each selector, whether its element is rendered (it has a box, so neither it nor an ancestor has display
    none), or None when the page has no such element."""
    return page.evaluate("(selectors) => selectors.map((s) => { const el = document.querySelector(s); "
                         "return el ? el.getClientRects().length > 0 : null; })", list(selectors))


VISIBLE_TEXT_JS = "(s) => { const el = document.querySelector(s); return el ? el.innerText.replace(/\\s+/g, ' ').trim() : null; }"


def visible_text(page, selector):
    """qa.md "the visible text of X", its innerText with every run of white space made one space, or None."""
    return page.evaluate(VISIBLE_TEXT_JS, selector)


def settled_text(page, selector, expected, timeout_ms=2000):
    """The visible text of `selector` once it reads `expected`, or what it reads after `timeout_ms`. The wait is bounded,
    so a refit that never comes fails on the text it left, not on a timeout."""
    try:
        page.wait_for_function(f"([s, t]) => ({VISIBLE_TEXT_JS})(s) === t", arg=[selector, expected], timeout=timeout_ms)
    except PlaywrightTimeoutError:
        pass
    return visible_text(page, selector)


def start_over(page):
    """New bill, then Start new bill (R31)."""
    open_dialog(page)
    page.get_by_role("button", name="Start new bill").click()


def k1_started_over_and_reloaded(open_app):
    page = open_app(seed=seeds.S1).page
    start_over(page)
    page.reload()
    return page


def cold_boot_renamed_and_reloaded(open_app):
    page = open_app().page
    support.replace_text(page, person_field(page, 1), "A")
    page.reload()
    return page


# qa.md "Which section is open on load": the setup, then the data-open of People and of Charges at 390 x 844.
OPEN_ON_LOAD = [
    pytest.param(lambda open_app: open_app().page, "true", "false", id="cold-boot"),
    pytest.param(lambda open_app: open_app(seed=seeds.S1).page, "false", "false", id="K1"),
    pytest.param(lambda open_app: open_app(seed=seeds.RE).page, "false", "true", id="RE"),
    pytest.param(lambda open_app: open_app(seed=seeds.UNREADABLE["B1"]).page, "true", "false", id="B1"),
    pytest.param(k1_started_over_and_reloaded, "true", "false", id="K1-started-over-and-reloaded"),
    pytest.param(cold_boot_renamed_and_reloaded, "false", "false", id="cold-boot-renamed-and-reloaded"),
    pytest.param(lambda open_app: open_app(seed=seeds.with_bill(seeds.S2, serviceText="")).page, "false", "false",
                 id="K2-blank-rate"),
]


@pytest.mark.parametrize("setup, people, charges", OPEN_ON_LOAD)
def test_R48_which_section_is_open_on_load(open_app, setup, people, charges):
    # R26: a restored bill opens or folds its sections by R48, and nothing about them is saved.
    page = setup(open_app)
    assert section_state(page) == [[people, people], [charges, charges]]


SUMMARY_BOX_JS = """(el) => { const style = getComputedStyle(el);
  return { visibility: style.visibility, opacity: style.opacity, width: el.getBoundingClientRect().width }; }"""
ROW_WIRING_JS = """() => ['peopleBtn', 'chargesBtn'].map((id) => { const row = document.getElementById(id);
  return row && ['aria-controls', 'aria-labelledby', 'aria-describedby'].map((name) => row.getAttribute(name)); })"""


def test_R48_a_header_row_toggles_by_click_enter_and_space(open_app, plain_context):
    page = open_app(seed=seeds.S1).page
    assert page.evaluate(ROW_WIRING_JS) == [["peopleBody", "peopleName", "peopleSum"], ["chargesBody", "chargesName", "chargesSum"]]
    stored_before = stored_text(page)
    row = page.locator("#peopleBtn")
    row.click()
    assert section_state(page)[0] == OPEN and displayed(page, "#peopleBody") == [True]
    summary = page.locator("#peopleSum").evaluate(SUMMARY_BOX_JS)
    golden = open_golden(plain_context, "bill-items-open").locator("#peopleSum").evaluate(SUMMARY_BOX_JS)
    assert summary["visibility"] == golden["visibility"] == "hidden" and summary["opacity"] == golden["opacity"]
    assert abs(summary["width"] - golden["width"]) <= 0.5, (summary, golden)  # it keeps its box
    row.press("Enter")
    assert section_state(page)[0] == FOLDED and displayed(page, "#peopleBody") == [False]
    row.press("Space")
    assert section_state(page)[0] == OPEN and displayed(page, "#peopleBody") == [True]
    assert stored_text(page) == stored_before  # a fold is not a change, so nothing is saved


SUMMARY_FITS_JS = "() => { const sum = document.getElementById('peopleSum'); return sum ? sum.scrollWidth <= sum.clientWidth : null; }"


@pytest.mark.parametrize("seed, size, text", [
    pytest.param(seeds.S1, (390, 844), "Aisyah, Ben, Chen", id="K1-390"),
    pytest.param(seeds.T12, (390, 844), "Aisyah, Ben, Chen, Person 4 and 8 more", id="T12-390"),
    pytest.param(seeds.T12, (360, 780), "Aisyah, Ben, Chen and 9 more", id="T12-360"),
    pytest.param(seeds.T12W, (360, 780), "12 people", id="T12W-360"),
])
def test_R48_the_people_summary_fits_its_row(open_app, seed, size, text):
    page = open_app(seed=seed, viewport=size).page
    assert visible_text(page, "#peopleSum") == text
    assert page.evaluate(SUMMARY_FITS_JS) is True  # it shows whole, with no ellipsis


def test_R48_the_people_summary_refits_when_its_rows_width_changes(open_app):
    page = open_app(seed=seeds.T12).page
    assert visible_text(page, "#peopleSum") == "Aisyah, Ben, Chen, Person 4 and 8 more"
    page.set_viewport_size({"width": 360, "height": 780})
    assert settled_text(page, "#peopleSum", "Aisyah, Ben, Chen and 9 more") == "Aisyah, Ben, Chen and 9 more"


CHARGES_SUMMARY_JS = """() => { const row = document.getElementById('chargesBtn'), sum = document.getElementById('chargesSum');
  if (!row || !sum) return null;
  return { bad: row.classList.contains('is-bad'),
    holds: [...sum.children].map((el) => el.matches('svg.ic') ? el.querySelector('use')?.getAttribute('href') : `${el.localName}.${el.className}`),
    text: sum.querySelector('span.sec-txt')?.textContent ?? null }; }"""


def charges_summary(page):
    """The Charges row's is-bad class, what #chargesSum holds in order (an icon by its href) and the text of its
    span.sec-txt (R48 (2)), or None."""
    return page.evaluate(CHARGES_SUMMARY_JS)


@pytest.mark.parametrize("svc, sst, bad, text", [
    ("10", "6", False, "Service 10%, SST 6%"),
    ("", "6", True, "Check service charge"),
    ("10", "25", True, "Check SST"),
    ("31", "", True, "Check both rates"),
    ("12.50", "6.25", False, "Service 12.5%, SST 6.25%"),
], ids=["valid", "service-blank", "sst-too-high", "both", "fractions"])
def test_R48_the_charges_summary_names_a_rate_that_blocks(open_app, svc, sst, bad, text):
    # RULINGS-v1.1.0: a blank rate shows the marker too and never reads as 0.
    page = open_app(seed=seeds.S1).page
    open_charges_first(page)
    support.replace_text(page, rate_field(page, "Service charge"), svc)
    support.replace_text(page, rate_field(page, "SST"), sst)
    page.locator("#chargesBtn").click()
    holds = ["#i-warning-circle", "span.sec-txt"] if bad else ["span.sec-txt"]
    assert charges_summary(page) == {"bad": bad, "holds": holds, "text": text}


def type_25_into_sst(page):
    """qa.md: replace the text of "SST" with "2" and then type "5", with the field still focused."""
    sst = rate_field(page, "SST")
    support.replace_text(page, sst, "2")
    page.keyboard.type("5")
    return sst


def test_R48_the_charges_summary_follows_each_keystroke_not_the_error_timing(open_app):
    page = open_app(seed=seeds.S1).page
    open_charges_first(page)
    sst = type_25_into_sst(page)
    assert (charges_summary(page) or {}).get("text") == "Check SST"
    assert sst.get_attribute("aria-invalid") != "true"  # the field still has focus, so its error waits (R10)
    page.keyboard.press("Backspace")
    assert (charges_summary(page) or {}).get("text") == "Service 10%, SST 2%"


@pytest.mark.xfail(strict=True, reason="task A6")
def test_R48_the_charges_summary_reads_check_sst_while_its_error_paragraph_is_hidden(open_app):
    # The qa.md line "while p.err#sstErr still carries hidden", on the v1.1.0 Charges markup that task A6 builds.
    page = open_app(seed=seeds.S1).page
    open_charges_first(page)
    type_25_into_sst(page)
    assert (charges_summary(page) or {}).get("text") == "Check SST"
    assert page.evaluate("() => document.querySelector('p.err#sstErr')?.hidden ?? null") is True


def test_R48_only_the_header_row_and_start_new_bill_open_or_fold_a_section(open_app):
    page = open_app(seed=seeds.S1).page
    open_people_first(page)
    assert section_state(page) == [OPEN, FOLDED]
    type_into(page, item_price(page, 1), "abc")  # "Nasi lemak ayam price in RM" once task A8 names the price by its item (R11)
    page.keyboard.press("Tab")
    switch_to(page, "Even")
    switch_to(page, "By item")
    page.set_viewport_size({"width": 1280, "height": 800})
    page.set_viewport_size({"width": 390, "height": 844})
    assert section_state(page) == [OPEN, FOLDED]
    page.reload()
    assert section_state(page) == [FOLDED, FOLDED]  # the open state is never saved


def test_R48_on_the_desktop_both_sections_show(open_app):
    page = open_app(seed=seeds.S1).page
    page.set_viewport_size({"width": 1280, "height": 800})
    assert displayed(page, "#peopleBody", "#chargesBody", "#peopleBtn", "#chargesBtn") == [True, True, False, False]
    assert section_state(page) == [FOLDED, FOLDED]


@pytest.mark.xfail(strict=True, reason="task A6")
def test_R48_on_the_desktop_both_sections_show_their_own_headings(open_app):
    # h2#peopleH comes with task A5 and h2#chargesH with task A6.
    page = open_app(seed=seeds.S1).page
    page.set_viewport_size({"width": 1280, "height": 800})
    assert displayed(page, "h2#peopleH", "h2#chargesH") == [True, True]


REVEALS_JS = """() => document.getAnimations()
  .filter((animation) => !(animation instanceof CSSAnimation) && !(animation instanceof CSSTransition))
  .map((animation) => ({ target: animation.effect.target?.id ?? null, duration: animation.effect.getTiming().duration,
    frames: animation.effect.getKeyframes().map((frame) => [frame.height ?? null, String(frame.opacity ?? null)]) }))"""
HAS_STYLE_JS = "() => document.getElementById('peopleBody')?.hasAttribute('style') ?? null"


def nothing_runs_within(page, timeout_ms):
    """True once no animation of document.getAnimations() is running, False when one still is after `timeout_ms` (a
    bounded wait). Finished ones may stay listed: the foil sweep's fill is "both" in system.css, so its CSSAnimation is
    still there, finished, long after load (measured in both engines, BUILD.md, task A4)."""
    try:
        page.wait_for_function("() => document.getAnimations().every((a) => a.playState !== 'running')", timeout=timeout_ms)
        return True
    except PlaywrightTimeoutError:
        return False


def test_R48_opening_reveals_the_body_through_one_web_animation_and_folding_is_instant(open_app):
    # R48 (3) and the reveal lines of the R36 scenario "With motion allowed nothing loops" (PD-22).
    page = open_app(seed=seeds.S1, reduced_motion="no-preference").page
    assert nothing_runs_within(page, 3000)  # the strip's foil sweep on load has run out
    row = page.locator("#peopleBtn")
    row.click()
    reveals, has_style = page.evaluate(REVEALS_JS), page.evaluate(HAS_STYLE_JS)
    assert [(reveal["target"], reveal["duration"]) for reveal in reveals] == [("peopleBody", 200)] and has_style is False
    start, end = reveals[0]["frames"][0], reveals[0]["frames"][-1]
    assert start == ["0px", "0"] and end[1] == "1"
    assert nothing_runs_within(page, 1000) and page.evaluate(REVEALS_JS) == []  # nothing loops, and the reveal is gone
    full = page.locator("#peopleBody").evaluate("(el) => el.getBoundingClientRect().height")
    assert abs(float(end[0].removesuffix("px")) - full) <= 0.5 and page.evaluate(HAS_STYLE_JS) is False
    row.click()
    assert page.evaluate(REVEALS_JS) == [] and displayed(page, "#peopleBody") == [False]  # folding is instant


def test_R48_under_reduced_motion_a_section_opens_at_once(open_app):
    page = open_app(seed=seeds.S1).page  # reduced motion "reduce", the default context
    page.locator("#peopleBtn").click()
    assert page.evaluate("() => document.getAnimations().length") == 0 and displayed(page, "#peopleBody") == [True]


def test_R48_start_new_bill_opens_people_and_folds_charges(open_app):
    # R48 (1) with R31, the open state is reset as at load. The RE seed opens Charges at load (R10 b), so the fold shows.
    page = open_app(seed=seeds.RE).page
    start_over(page)
    assert section_state(page) == [OPEN, FOLDED]


# ===== END OF TESTS (new tests go above this line) =====
