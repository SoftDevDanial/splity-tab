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
import subprocess
import sys
import types
import urllib.parse
import urllib.request
from pathlib import Path
from xml.etree import ElementTree

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

import rig
import seeds
import support
from expected import (BLOCKED_CARD, COLD_BOOT, S1_COPY, S1_ITEMS, S1_LINES, S1_PROOF, S1_SPLITS, S2_COPY,
                      S2_LINES, S2_PROOF, S2_SPLITS)
from support import (CSP, GOLDEN_DIR, ROOT, card_text, cold_boot_state, dom_walk, first_diff, golden_walk, open_golden,
                     person_field, receipt, walk_entries)


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
    assert set(seeds.ODD_READABLE) == {"G1", "G2", "G3", "G4", "G5", "G6", "G7"}
    assert seeds.S2_V1 == ('{"version":1,"bill":{"mode":"even","people":[{"id":"p1","name":"Aisyah"},{"id":"p2","name":"Ben"},'
                           '{"id":"p3","name":"Chen"}],"subtotalText":"100.00","items":[],"serviceText":"10","sstText":"6","nextId":4}}')
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


def test_R2_cold_boot_is_a_new_bill_with_no_seed(open_app):
    # COLD_BOOT (expected.py) and cold_boot_state (support.py) are shared with the live gate's steps 1 and 8 (task A20).
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
# the widths of its row).
EVERY_WIDTH = (390, 360, 1280)
R3_STATES = {
    "bill-items": (seeds.S1, {}, EVERY_WIDTH),
    "bill-items-open": (seeds.S1, {"phone": ("#peopleBtn", "#chargesBtn")}, (390, 360)),
    "bill-even": (seeds.S2, {}, EVERY_WIDTH),
    "spare-sen": (seeds.S1, SPARE_OPENERS, EVERY_WIDTH),
    "spare-sen-one": (seeds.ONE, SPARE_OPENERS, EVERY_WIDTH),
    "spare-sen-random": (seeds.RND, SPARE_OPENERS, EVERY_WIDTH),
    "splits-sheet": (seeds.S1, {"phone": ("#splitsBtn",)}, (390, 360)),
    "new-bill-dialog": (seeds.S1, {"phone": ("#newBill",), "desktop": ("#newBill",)}, EVERY_WIDTH),
    "bill-empty": (None, {}, EVERY_WIDTH),
    "rate-error": (seeds.RE, {}, EVERY_WIDTH),
    "bill-unassigned": (seeds.S5, {}, EVERY_WIDTH),
    "bill-unreadable": (seeds.UNREADABLE["B1"], {}, EVERY_WIDTH),
    "bill-twelve": (seeds.T12, {}, EVERY_WIDTH),
    "bill-large": (seeds.W1, {}, EVERY_WIDTH),
}
R3_PAIRS = [pytest.param(golden, width, id=f"{golden}-{width}") for golden, (_, _, widths) in R3_STATES.items() for width in widths]


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
    assert found is not None and found.startswith("body: children ") and "dialog.sheet-dlg" in found, found


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
# (state, golden of that state, seed, width, the clicks after load, the proof the module ran)
POLICY_STATES = [
    ("cold-boot", "bill-empty", None, 390, (), "card-blocked"),
    ("K1", "bill-items", seeds.S1, 390, (), "card-K1"),
    ("K1-new-bill", "new-bill-dialog", seeds.S1, 390, ("#newBill",), "dialog-open"),
    ("K1-sheet-P1", "spare-sen", seeds.S1, 390, ("#splitsBtn", SHEET_SPARE_CHIP), "sheet-padding"),
    ("K2-P1-desktop", "bill-even", seeds.S2, 1280, ("#spareBtn",), "spare-place"),
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


@pytest.mark.parametrize("state, golden, seed, width, clicks, proof", [pytest.param(*row, id=row[0]) for row in POLICY_STATES])
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
    # [v1.1.0] K1, and the People summary shows the fallback too, as does the card's second splits row (task A9).
    page = open_app(seed=seeds.S1).page
    open_people_first(page)
    support.replace_text(page, person_field(page, 2), "")
    rows = person_rows(page)
    assert rows is not None, "no ul.people#peopleList"
    assert rows[1] == person_row(2, "", "Person 2")
    for name, _, _ in S1_ITEMS:
        assert who_group(page, name).get_by_role("button").all_inner_texts() == ["Aisyah", "Person 2", "Chen"]
    splits, _ = card_rows(page)
    assert splits and splits[1][0] == "Person 2", splits
    page.locator("#peopleBtn").click()
    assert visible_text(page, "#peopleSum") == "Aisyah, Person 2, Chen"
    open_people_first(page)
    support.replace_text(page, person_field(page, 2), "   ")  # spaces only count as blank (PD-2 of 1.0)
    assert person_rows(page)[1] == person_row(2, "   ", "Person 2")


# After each key of a rename of the third person: their toggle in every item, their Remove name, the People summary.
RENAME_READS_JS = """() => ({
  toggles: [...document.querySelectorAll('li.item')].map((item) => item.querySelectorAll('button.tap')[2]?.textContent.trim() ?? null),
  card: document.querySelector('#rbody > ul.r-splits > li:nth-child(3) > span.nm')?.textContent ?? null,
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
    # [v1.1.0] K1. The toggles, the card's third splits row (task A9), the Remove name and the People summary here. The
    # sheet, the copy and the pills are the next test's.
    page = open_app(seed=seeds.S1).page
    open_people_first(page)

    def every_place_reads(label):
        assert page.evaluate(RENAME_READS_JS) == {"toggles": [label] * 4, "card": label, "remove": f"Remove {label}",
                                                  "summary": f"Aisyah, Ben, {label}"}

    rename_chen_to_chen_wei(page, every_place_reads)
    assert person_field(page, 3).input_value() == "Chen Wei"


def test_R5_a_new_name_reaches_the_sheet_the_copy_and_the_pills(open_app):
    # The rest of qa.md "Renaming a person updates every place on each keystroke". The sheet is task A12's, its Copy
    # summary A10 and A12, the spare chip in it A13 and the pills A14 (R53). Each read fails on its assertion, never on a wait.
    page = open_app(seed=seeds.S1).page
    open_people_first(page)
    rename_chen_to_chen_wei(page)
    page.locator("#splitsBtn").click()
    names = page.evaluate("() => [...document.querySelectorAll('#splitsDlg ul.r-splits > li > span.nm')].map((el) => el.textContent)")
    assert names == ["Aisyah", "Ben", "Chen Wei"], names
    page.locator("#splitsDlg .r-copy").click()
    assert page.evaluate("window.testClipboardText").splitlines()[4] == "Chen Wei RM 24.48"
    assert page.locator(SHEET_SPARE_CHIP).count() == 1, "the sheet holds no spare chip"  # task A13
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
    assert shown_errors(page) == [] and page.locator("div.note").count() == 0  # the 1.0 p.error is gone since task A8
    assert [f.input_value() for f in page.locator("li.person input").all()] == ["Ben", "Ben", "Chen"]
    assert remove_button(page, "Ben").count() == 2
    remove_button(page, "Ben").nth(1).click()
    assert [f.input_value() for f in page.locator("li.person input").all()] == ["Ben", "Chen"]


# ---------------------------------------------------------------- Task 4: mode and subtotal (R8, R9, R10)

def subtotal_field(page):
    return page.get_by_role("textbox", name="Subtotal in RM", exact=True)


def switch_to(page, label):
    page.get_by_text(label, exact=True).click()


# Which Split radio is checked and how many Subtotal and Items blocks the page holds (R8, the block of the other mode is
# absent from the DOM), read in one evaluate so a radio that is not there gives null instead of a wait.
SPLIT_STATE_JS = """() => ({ even: document.querySelector('#modeEven')?.checked ?? null,
  item: document.querySelector('#modeItem')?.checked ?? null, evenBlocks: document.querySelectorAll('#evenBlock').length,
  itemsBlocks: document.querySelectorAll('#itemsBlock').length })"""
EVEN_SHOWN = {"even": True, "item": False, "evenBlocks": 1, "itemsBlocks": 0}
ITEM_SHOWN = {"even": False, "item": True, "evenBlocks": 0, "itemsBlocks": 1}


def split_state(page):
    return page.evaluate(SPLIT_STATE_JS)


def test_R8_switching_modes_keeps_the_subtotal(open_app):
    page = open_app().page
    support.replace_text(page, subtotal_field(page), "100.00")
    switch_to(page, "By item")
    assert split_state(page) == ITEM_SHOWN
    assert card_text(page) == BLOCKED_CARD["no-prices"]  # the v1.1.0 card since task A2 (BUILD.md, A2, Q-A2-3)
    switch_to(page, "Even")
    assert split_state(page) == EVEN_SHOWN and subtotal_field(page).input_value() == "100.00"


def test_R8_arrow_keys_move_between_the_modes(open_app):
    page = open_app().page
    for _ in range(12):
        page.keyboard.press("Tab")
        if page.evaluate("document.activeElement.id") == "modeEven":
            break
    assert page.evaluate("document.activeElement.id") == "modeEven"
    page.keyboard.press("ArrowRight")
    assert split_state(page) == ITEM_SHOWN and page.evaluate("document.activeElement.id") == "modeItem"


# qa.md "Focus after a mouse click is the engine's own" (@per_engine, spec R59), the "By item" label row (task A7).
# Chromium focuses the radio, WebKit leaves document.activeElement on body (isMouseFocusable, the A0 probe).
@pytest.mark.parametrize("control, focused", [pytest.param("By item", "modeItem", id="by-item-label")])
def test_R59_focus_after_a_mouse_click_is_the_engines_own(open_app, engine, control, focused):
    page = open_app().page
    page.get_by_text(control, exact=True).click()
    active = page.evaluate("document.activeElement.id || document.activeElement.localName")
    assert active == (focused if engine == "chromium" else "body")


# The Split block and the Subtotal block of R8 and R9, read in one evaluate (null for a block that is not there).
SPLIT_MARKUP_JS = """() => {
  const tag = (el) => `${el.localName}${el.id ? '#' + el.id : ''}${[...el.classList].map((c) => '.' + c).join('')}`;
  const attrs = (el, names) => el && Object.fromEntries(names.map((name) => [name, el.getAttribute(name)]));
  const split = document.querySelector('div.blk.split#splitBlk'), even = document.querySelector('div.blk#evenBlock');
  const sw = split?.querySelector('div.mode-sw');
  return {
    split: split && { attrs: attrs(split, ['role', 'aria-labelledby']), children: [...split.children].map(tag),
      heading: split.querySelector('h2#splitH')?.textContent ?? null,
      switch: sw && [...sw.children].map((el) => el.localName === 'label' ? ['label', el.htmlFor, el.textContent]
        : ['input', el.type, el.name, el.id, el.value]) },
    legends: document.querySelectorAll('legend').length,
    even: even && { children: [...even.children].map(tag),
      label: attrs(even.children[0], ['for']), labelText: even.children[0]?.textContent ?? null,
      field: [...(even.querySelector('#evenField')?.children ?? [])].map((el) => [tag(el), el.getAttribute('aria-hidden'), el.textContent]),
      input: attrs(even.querySelector('input#evenSub'), ['type', 'inputmode', 'autocomplete', 'placeholder', 'aria-label',
        'aria-describedby', 'aria-invalid']),
      errorHidden: even.querySelector('p.err#evenErr')?.hidden ?? null },
  };
}"""
SPLIT_MARKUP = {
    "split": {"attrs": {"role": "group", "aria-labelledby": "splitH"}, "children": ["h2#splitH.blk-h", "div.mode-sw"],
              "heading": "Split", "switch": [["input", "radio", "mode", "modeEven", "even"], ["label", "modeEven", "Even"],
                                             ["input", "radio", "mode", "modeItem", "item"], ["label", "modeItem", "By item"]]},
    "legends": 0,
    "even": {"children": ["label.blk-h.solo", "div#evenField.field.money.sub-field", "p#evenErr.err"],
             "label": {"for": "evenSub"}, "labelText": "Subtotal",
             "field": [["span.unit", "true", "RM"], ["input#evenSub", None, ""]],
             "input": {"type": "text", "inputmode": "decimal", "autocomplete": "off", "placeholder": "0.00",
                       "aria-label": "Subtotal in RM", "aria-describedby": "evenErr", "aria-invalid": "false"},
             "errorHidden": True},
}


def test_R9_the_subtotal_field_drives_the_even_split(open_app):
    # qa.md "The subtotal field drives the even split", with the Split block of R8 (no legend). The splits after typing
    # are test_R9_a_subtotal_drives_the_even_split.
    page = open_app().page
    assert page.evaluate(SPLIT_MARKUP_JS) == SPLIT_MARKUP
    support.replace_text(page, subtotal_field(page), "100.00")
    assert subtotal_field(page).input_value() == "100.00" and page.locator("#rbody div.r-spare").count() == 0


def opened_rate_field(label):
    """A field_of for a rate row of an outline: Charges opened first (qa.md, it is folded below 1024 px since task A4,
    R48), then the rate field. Opening is a click only when Charges is folded, so calling it again changes nothing."""
    def field_of(page):
        open_charges_first(page)
        return rate_field(page, label)
    return field_of


# The three inline error texts (spec, Copy), each exact. A case that showed another field's text must fail.
AMOUNT_MESSAGE, SERVICE_MESSAGE, SST_MESSAGE = "Enter an amount like 12.50", "Enter a rate from 0 to 30", "Enter a rate from 0 to 20"

# The v1.1.0 inline error of one field (R10, R15), read in one evaluate on the input: p.err#<id> (null when the page holds
# no p.err of that id, so a missing part fails on the assertion and never on a wait), the input and its div.field.
FIELD_ERROR_JS = """(input, id) => { const p = document.getElementById(id), err = p && p.matches('p.err') ? p : null;
  const first = err?.firstElementChild;
  return { hidden: err ? err.hidden : null, text: err ? err.textContent : null,
    icon: first?.matches('svg.ic') ? first.querySelector('use')?.getAttribute('href') ?? null : null,
    invalid: input.getAttribute('aria-invalid'), describedBy: input.getAttribute('aria-describedby'),
    bad: input.closest('div.field')?.classList.contains('is-bad') ?? null }; }"""


def field_error(field, error_id):
    """What R10 says of one field: p.err#error_id's hidden, text and leading icon, the input's aria-invalid and
    aria-describedby, and whether its div.field has is-bad."""
    return field.evaluate(FIELD_ERROR_JS, error_id)


def error_state(message, described, shown):
    """The field_error of a field whose error shows or not, as spec R10 and the goldens give it."""
    return {"hidden": not shown, "text": message, "icon": "#i-warning-circle", "invalid": str(shown).lower(),
            "describedBy": described, "bad": shown}


SHOWN_ERRORS_JS = "() => [...document.querySelectorAll('p.err:not([hidden])')].map((p) => p.id)"


def shown_errors(page):
    """The ids of every inline error that shows (p.err without hidden, R10)."""
    return page.evaluate(SHOWN_ERRORS_JS)


def invalid_fields(page):
    return page.locator("[aria-invalid=true]").count()


# The rows of qa.md "An inline error waits for the field to be left" (task A6 the rates, rule 13, task A7 the Subtotal and
# task A8 the price, which name their error at all times, CG-P6). The seed is the row's setup, None for a cold boot.
RATE_ERROR_CASES = [
    pytest.param(None, subtotal_field, "0", AMOUNT_MESSAGE, "evenErr", "evenErr", "evenErr", "12.50", id="subtotal"),
    pytest.param(seeds.S1, lambda page: item_price(page, 2), "13.505", AMOUNT_MESSAGE, "ie2", "ie2", "ie2", "13.50", id="item-price"),
    pytest.param(None, opened_rate_field("Service charge"), "31", SERVICE_MESSAGE, "svcErr", "chargeHint", "chargeHint svcErr", "10", id="service"),
    pytest.param(None, opened_rate_field("SST"), "20.01", SST_MESSAGE, "sstErr", "chargeHint", "chargeHint sstErr", "6", id="sst"),
]


@pytest.mark.parametrize("seed, field_of, bad, message, error_id, described, shown_described, good", RATE_ERROR_CASES)
def test_R10_an_inline_error_waits_for_the_field_to_be_left(open_app, seed, field_of, bad, message, error_id, described,
                                                            shown_described, good):
    page = open_app(seed=seed).page
    field = field_of(page)
    support.replace_text(page, field, bad)
    assert field_error(field, error_id) == error_state(message, described, shown=False)
    page.keyboard.press("Tab")
    assert field_error(field, error_id) == error_state(message, shown_described, shown=True)
    support.replace_text(page, field, good[0])  # the first key that makes the text valid, with the field still focused
    assert field_error(field, error_id) == error_state(message, described, shown=False)
    page.keyboard.type(good[1:])
    assert field.input_value() == good


@pytest.mark.parametrize("seed, field_of, bad, message, error_id, described, shown_described, good", RATE_ERROR_CASES)
def test_R10_a_cleared_error_does_not_come_back_until_the_field_is_left_again(
        open_app, seed, field_of, bad, message, error_id, described, shown_described, good):
    # WR-03 / K1: (c) says the error goes at valid text and "does not come back until the field next loses focus".
    page = open_app(seed=seed).page
    field = field_of(page)
    support.replace_text(page, field, bad)
    page.keyboard.press("Tab")
    support.replace_text(page, field, good[0])
    page.keyboard.type("x")  # bad again, and the field still has focus
    assert field_error(field, error_id) == error_state(message, described, shown=False)
    page.keyboard.press("Tab")
    assert field_error(field, error_id) == error_state(message, shown_described, shown=True)


def leave_subtotal_and_service_charge_empty(page):
    """qa.md "An empty field never shows an error", its two When lines."""
    subtotal_field(page).click()
    page.keyboard.press("Tab")
    support.replace_text(page, opened_rate_field("Service charge")(page), "")
    page.keyboard.press("Tab")


def test_R10_an_empty_field_never_shows_an_error(open_app):
    # The v1.1.0 scenario (task A6). Its strip line is the next test, for task A11.
    page = open_app().page
    leave_subtotal_and_service_charge_empty(page)
    assert page.locator("p.err").count() >= 2 and shown_errors(page) == [] and invalid_fields(page) == 0
    assert card_text(page) == BLOCKED_CARD["rates"]
    page.locator("#chargesBtn").click()
    assert charges_summary(page) == {"bad": True, "holds": ["#i-warning-circle", "span.sec-txt"], "text": "Check service charge"}


def test_R10_an_empty_rate_leaves_the_strip_reading_check_the_charges(open_app):
    # The strip holds the message alone, with no "Total" before it as the card has (spec R17, R49).
    page = open_app().page
    leave_subtotal_and_service_charge_empty(page)
    assert visible_text(page, "#stripInfo") == "Check the charges to see the splits."


def test_R10_typing_bad_text_in_a_focused_field_shows_no_error_early(open_app):
    page = open_app().page
    subtotal_field(page).click()
    page.keyboard.type("abc")
    assert field_error(subtotal_field(page), "evenErr") == error_state(AMOUNT_MESSAGE, "evenErr", shown=False)
    assert card_text(page) == BLOCKED_CARD["subtotal"]
    assert visible_text(page, "#stripInfo") == "Enter the subtotal to see the splits."  # the strip reads (task A11, R49)


def test_R10_an_error_survives_a_mode_switch(open_app):
    page = open_app().page
    support.replace_text(page, subtotal_field(page), "0")
    page.keyboard.press("Tab")
    switch_to(page, "By item")
    switch_to(page, "Even")
    assert field_error(subtotal_field(page), "evenErr") == error_state(AMOUNT_MESSAGE, "evenErr", shown=True)


def accessible_description(page, selector):
    """The computed accessible description of the element at `selector`, as Chromium's accessibility tree gives it to a
    screen reader (CDP Accessibility.getPartialAXTree), "" when it has none."""
    cdp = page.context.new_cdp_session(page)
    try:
        cdp.send("DOM.enable")
        cdp.send("Accessibility.enable")
        root = cdp.send("DOM.getDocument", {"depth": 0})["root"]["nodeId"]
        node = cdp.send("DOM.querySelector", {"nodeId": root, "selector": selector})["nodeId"]
        found = cdp.send("Accessibility.getPartialAXTree", {"nodeId": node, "fetchRelatives": False})["nodes"][0]
        return found.get("description", {}).get("value", "")
    finally:
        cdp.detach()


# The seed, the field's accessible name and the text that makes it invalid, one row per page of the scenario (CG-P6).
DESCRIBED_FIELDS = [(seeds.S1, "Char kuey teow price in RM", "13.505"), (seeds.S2, "Subtotal in RM", "0")]


@pytest.mark.chromium_only(reason="Needs a CDP session (Accessibility.getPartialAXTree) to read the computed description, "
                                  "which Playwright gives in Chromium only.")
def test_R9_the_accessible_description_of_the_amount_fields_is_measured_and_reported(open_app, evidence_folder):
    # CG-P6, ruled by the owner (USER, 2026-10-13): built to the golden, the description is measured and reported to the
    # owner. So the lines name what was read and the test asserts only that the four exist (QA-S5-1).
    lines = []
    for seed, name, bad in DESCRIBED_FIELDS:
        page = open_app(seed=seed).page
        selector, field = f'input[aria-label="{name}"]', page.get_by_role("textbox", name=name, exact=True)
        for when in ("as loaded", f"after {bad!r} and Tab"):
            if when != "as loaded":
                support.replace_text(page, field, bad)
                page.keyboard.press("Tab")
            state = "error shown" if field.get_attribute("aria-invalid") == "true" else "error hidden"
            lines.append(f"{name} | {state} | description {accessible_description(page, selector)!r} | {when} | "
                         f"aria-describedby {field.get_attribute('aria-describedby')!r}")
    record = evidence_folder / "accessible-description.txt"
    record.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
    written = [line.split(" | ")[:2] for line in record.read_text(encoding="utf-8").splitlines()]
    assert written == [[name, state] for _, name, _ in DESCRIBED_FIELDS for state in ("error hidden", "error shown")]


# ---------------------------------------------------------------- Task 5: items (R7, R11 to R14, R10, R34)

def item_name(page, number):
    return page.get_by_label(f"Item {number} name", exact=True)


def item_price(page, number):
    """The price field of the item at 1-based `number`, found by its place, because since task A8 it is named by its
    item ("Char kuey teow price in RM", R11). The tests that check the name read it."""
    return page.locator("li.item").nth(number - 1).locator(".field.money input")


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
    # [v1.1.0] K1, and the price field's name follows the item name (R11, task A8).
    page = open_app(seed=seeds.S1).page
    support.replace_text(page, item_name(page, 4), "Satay")
    assert item_price(page, 4).get_attribute("aria-label") == "Satay price in RM"
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


def test_R7_the_item_left_with_nobody_needs_a_person_on_the_card_and_the_strip(open_app):
    # The rest of qa.md "Remove a person and they leave every item". The needs marker is built by task A8, the card's
    # div.r-msg by A9 and the strip's message by A11.
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
    assert split_state(page) == ITEM_SHOWN  # #evenBlock is not in the DOM and #itemsBlock is
    switch_to(page, "Even")
    assert split_state(page) == EVEN_SHOWN and subtotal_field(page).input_value() == "100.00"
    assert visible_text(page, "#stripInfo") == "Total RM 116.60"  # the strip reads (task A11, R49)
    switch_to(page, "By item")
    assert item_name(page, 1).input_value() == "Tea" and item_price(page, 1).input_value() == "5.00"
    assert toggle(page, "Tea", "Person 1").get_attribute("aria-pressed") == "true"
    assert visible_text(page, "#stripInfo") == "Total RM 5.83"


# v1.1.0 task A8. The Items block (R11 to R14), read in one pass, so a part that is not built yet fails on the assertion
# that names it and never on a wait. An icon reads as "class href", a part as "tag#id.class".
ITEMS_JS = """() => {
  const tag = (el) => `${el.localName}${el.id ? '#' + el.id : ''}${[...el.classList].map((c) => '.' + c).join('')}`;
  const icons = (node) => [...node.querySelectorAll('svg')].map((svg) => `${svg.getAttribute('class')} ${svg.querySelector('use')?.getAttribute('href')}`);
  const get = (el, names) => names.map((name) => el.getAttribute(name));
  const block = document.querySelector('div.blk.items-blk#itemsBlock'), add = document.querySelector('#addItem');
  const list = document.querySelector('div.frame-wrap#frameWrap > ul.frame#itemList');
  return {
    block: block && { children: [...block.children].map(tag), heading: block.querySelector('h2#itemsH')?.textContent ?? null,
      head: [...(block.querySelector(':scope > div.blk-head')?.children ?? [])].map(tag) },
    add: add && [add.className, add.disabled, add.textContent.trim(), ...icons(add)],
    list: list && { labelledBy: list.getAttribute('aria-labelledby'), rows: [...list.children].map((li) => {
      const cells = [...(li.querySelector(':scope > div.item-row')?.children ?? [])], taps = li.querySelector(':scope > div.taps');
      const name = cells[0]?.querySelector('input'), price = cells[1]?.querySelector('input'), unit = cells[1]?.querySelector('span.unit');
      return { li: li.className, cells: cells.map(tag),
        name: name && [name.value, ...get(name, ['type', 'maxlength', 'autocomplete', 'aria-label', 'placeholder'])],
        price: price && [price.value, unit && [unit.getAttribute('aria-hidden'), unit.textContent],
          ...get(price, ['type', 'inputmode', 'autocomplete', 'placeholder', 'aria-label', 'aria-invalid', 'aria-describedby'])],
        remove: cells[2] ? [cells[2].getAttribute('aria-label'), ...icons(cells[2])] : null,
        err: cells[3] ? [cells[3].hidden, cells[3].textContent, ...icons(cells[3])] : null,
        taps: taps && [taps.getAttribute('role'), taps.getAttribute('aria-label'), [...taps.children].map((b) =>
          [b.className, b.getAttribute('aria-pressed'), ...icons(b), b.querySelector(':scope > span')?.textContent ?? null])] };
    }) },
  };
}"""
ITEMS_BLOCK = {"children": ["div.blk-head", "div#frameWrap.frame-wrap"], "heading": "Items",
               "head": ["h2#itemsH.blk-h", "button#addItem.btn.btn-ghost"]}
THREE = ("Aisyah", "Ben", "Chen")


def items_shown(page):
    """{ block, add, list } of the Items block as ITEMS_JS reads them, each None when the page has no such part."""
    return page.evaluate(ITEMS_JS)


def item_rows(page):
    """The rows of ul.frame#itemList, or None when the page has no such list."""
    shown = items_shown(page)["list"]
    return shown and shown["rows"]


def add_item_shown(disabled=False):
    """#addItem as spec R12 writes it."""
    return ["btn btn-ghost", disabled, "Add item", "ic #i-plus"]


def item_row(number, name, price, label, pressed, people=THREE, error=False):
    """A row as spec R11, R13, R14 and R18 write it, at 1-based `number`, named for `label`, with one toggle per person
    of `people` and those in `pressed` on. An item that nobody had carries the needs marker."""
    bad = ".is-bad" if error else ""
    return {"li": "item" if pressed else "item needs",
            "cells": ["div.field", f"div.field.money{bad}", "button.icon-btn", f"p#ie{number}.err"],
            "name": [name, "text", "40", "off", f"Item {number} name", f"Item {number}"],
            "price": [price, ["true", "RM"], "text", "decimal", "off", "0.00", f"{label} price in RM", str(error).lower(), f"ie{number}"],
            "remove": [f"Remove {label}", "ic #i-x"],
            "err": [not error, AMOUNT_MESSAGE, "ic #i-warning-circle"],
            "taps": ["group", f"Who had {label}", [["tap", str(person in pressed).lower(), "ic #i-check", person] for person in people]]}


K1_ROWS = [item_row(number, name, price, name, pressed) for number, (name, price, pressed) in enumerate(S1_ITEMS, start=1)]


def test_R11_item_rows_carry_their_names_and_labels(open_app):
    # [v1.1.0] qa.md on K1. The price is named by its item and names its error paragraph, the last child of the row.
    page = open_app(seed=seeds.S1).page
    assert items_shown(page)["list"] == {"labelledBy": "itemsH", "rows": K1_ROWS}


def test_R12_add_an_item_remove_one_and_reach_the_limit(open_app, plain_context):
    # [v1.1.0] The heading row with #addItem, the no-prices card, and the disabled look compared with #addPerson of
    # bill-twelve.html. The 1.0 form compared it with a states.html specimen (B1). The strip line is the next test's.
    page = open_app().page
    switch_to(page, "By item")
    shown = items_shown(page)
    assert (shown["block"], shown["add"]) == (ITEMS_BLOCK, add_item_shown()), "no Items block as spec R12 writes it"
    add = page.locator("#addItem")
    add.click()
    assert item_rows(page) == [item_row(1, "", "", "Item 1", [], people=("Person 1", "Person 2"))]
    assert card_text(page) == BLOCKED_CARD["no-prices"]
    for _ in range(49):
        add.click()
    assert len(item_rows(page)) == 50 and items_shown(page)["add"] == add_item_shown(disabled=True)
    page.set_viewport_size({"width": 1280, "height": 800})
    golden = open_golden(plain_context, "bill-twelve", VIEWPORTS[1280]).locator("#addPerson")
    assert support.specimen_props(add, GOLDEN_LOOK) == support.specimen_props(golden, GOLDEN_LOOK)
    assert add.evaluate("(el) => getComputedStyle(el).cursor") == "not-allowed"
    remove_button(page, "Item 2").click()
    assert len(item_rows(page)) == 49 and items_shown(page)["add"] == add_item_shown()


def test_R12_a_new_item_leaves_the_strip_reading_add_each_item(open_app):
    # The strip line of qa.md "Add an item, remove one, and reach the limit". The strip's message is task A11's (R49).
    page = open_app().page
    switch_to(page, "By item")
    page.get_by_role("button", name="Add item", exact=True).click()
    assert visible_text(page, "#stripInfo") == "Add each item and tap who had it to see the splits."


def toggle_states(page, number):
    return [b.get_attribute("aria-pressed") for b in page.locator("li.item").nth(number - 1).locator("button.tap").all()]


def test_R13_tapping_a_person_on_an_item(open_app):
    # [v1.1.0] qa.md on K1 at 1280 x 800, each toggle the check icon and then the name, and the card's rows with their
    # working (task A9), and the spare line (task A13).
    page = open_app(seed=seeds.S1, viewport=VIEWPORTS[1280]).page
    toggle(page, "Satay, 10 sticks", "Ben").click()
    rows = item_rows(page)
    assert rows is not None and rows[3]["taps"] == item_row(4, "", "", "Satay, 10 sticks", THREE)["taps"]
    assert card_rows(page) == [[["Aisyah", "RM 25.54", "21.90 + 3.64"], ["Ben", "RM 22.74", "19.50 + 3.24"],
                                ["Chen", "RM 20.98", "18.00 + 2.98"]], S1_PROOF]
    assert support.reads(page, "#spareLine") == "2 sen left over"
    toggle(page, "Satay, 10 sticks", "Ben").click()
    assert item_rows(page) == K1_ROWS and card_rows(page) == [S1_SPLITS, S1_PROOF]


# A field_error read of p.err#ie2 that also says whether it is the last child of its div.item-row (R14).
LAST_IN_ROW_JS = """() => { const p = document.querySelector('p.err#ie2');
  return p ? p === p.parentElement.lastElementChild && p.parentElement.matches('div.item-row') : null; }"""


def test_R14_a_price_error_sits_in_the_item_row(open_app, plain_context):
    # [v1.1.0] qa.md, compared with the price piece of states.html (S2 on an amount). The 1.0 form read the 1.0 states.html
    # (B1). "Right aligned" is the golden's justify-self end, so the paragraph ends where the price field ends
    # (BUILD.md, A8, F-A8-1). Its text-align is compared with the piece's like every other property.
    page = open_app(seed=seeds.S1).page
    price = item_price(page, 2)
    support.replace_text(page, price, "13.505")
    page.keyboard.press("Tab")
    assert field_error(price, "ie2") == error_state(AMOUNT_MESSAGE, "ie2", shown=True)
    assert page.evaluate(LAST_IN_ROW_JS) is True
    piece = open_golden(plain_context, "states").locator('section[aria-labelledby="c-s2-price"]')
    look = [*GOLDEN_LOOK, "textAlign", "justifySelf"]
    assert support.specimen_props(page.locator("p.err#ie2"), look) == support.specimen_props(piece.locator("p.err#ie2"), look)
    wrapper = "li.item div.field.money.is-bad"
    assert support.specimen_props(page.locator(wrapper), GOLDEN_LOOK) == support.specimen_props(piece.locator(wrapper), GOLDEN_LOOK)
    ends = [page.locator(selector).evaluate("(el) => el.getBoundingClientRect().right") for selector in ("p.err#ie2", wrapper)]
    assert abs(ends[0] - ends[1]) <= 0.5, ends


@pytest.mark.parametrize("seed, action, target, value", [
    pytest.param(seeds.S1, "Add item", "Item 5 name", "", id="K1-add-item"),
    pytest.param(seeds.S1, "Remove Char kuey teow", "Item 2 name", "Mee goreng mamak", id="K1-remove-Char-kuey-teow"),
    pytest.param(seeds.S1, "Remove Satay, 10 sticks", "Item 3 name", "Mee goreng mamak", id="K1-remove-Satay"),
    pytest.param(None, "Remove Item 1", "addItem", "", id="cold-boot-remove-the-only-item"),
])
def test_R34_focus_after_adding_or_removing_an_item(open_app, seed, action, target, value):
    # [v1.1.0] The item rows of qa.md "Focus after adding or removing", with People opened first. The last row adds its one
    # item after "By item". "Add item" is #addItem, which support.active_label reads by its id.
    page = open_app(seed=seed).page
    open_people_first(page)
    if seed is None:
        switch_to(page, "By item")
        page.get_by_role("button", name="Add item", exact=True).click()
    page.get_by_role("button", name=action, exact=True).click()
    assert support.active_label(page) == target
    assert page.evaluate("document.activeElement.value") == value


NEEDS_JS = "() => [...document.querySelectorAll('li.item.needs')].map((li) => li.querySelector('input').value)"


def test_R18_every_item_with_nobody_carries_the_needs_marker(open_app):
    # The marker lines of qa.md "Items that still need a person" (spec R18, built by task A8). The card's and the strip's
    # messages are tasks A9 and A11 (until then the 1.0 form, test_R18_items_that_still_need_a_person).
    page = open_app(seed=seeds.S1).page
    assert page.evaluate(NEEDS_JS) == []
    toggle(page, "Mee goreng mamak", "Chen").click()
    assert page.evaluate(NEEDS_JS) == ["Mee goreng mamak"]
    toggle(page, "Char kuey teow", "Ben").click()
    assert page.evaluate(NEEDS_JS) == ["Char kuey teow", "Mee goreng mamak"]
    toggle(page, "Mee goreng mamak", "Chen").click()
    toggle(page, "Char kuey teow", "Ben").click()
    assert page.evaluate(NEEDS_JS) == []


# v1.1.0 task A8. The marks of the item frame (R56), [data-up, data-down] of #frameWrap, each "" while set and None
# while not, or None for a page with no frame.
FRAME_MARKS_JS = "() => { const w = document.querySelector('div.frame-wrap#frameWrap'); return w && [w.getAttribute('data-up'), w.getAttribute('data-down')]; }"
DOWN_ONLY, UP_ONLY, NEITHER = [None, ""], ["", None], [None, None]


@pytest.mark.parametrize("seed, width, marks", [
    pytest.param(seeds.S1, 1280, DOWN_ONLY, id="K1-1280"),
    pytest.param(seeds.S1, 390, NEITHER, id="K1-390"),
    pytest.param(seeds.W1, 360, DOWN_ONLY, id="W1-360"),
    pytest.param(seeds.W1, 390, NEITHER, id="W1-390"),
])
def test_R56_the_item_frame_marks_what_lies_above_and_below(open_app, seed, width, marks):
    page = open_app(seed=seed, viewport=VIEWPORTS[width]).page
    assert page.evaluate(FRAME_MARKS_JS) == marks


def frame_marks_once(page, expected, timeout_ms=2000):
    """The marks once they read `expected`, or what they read after `timeout_ms`. A wheel scroll may be animated, so the
    wait is bounded, and marks that never come fail on what they read then, not on a timeout."""
    try:
        page.wait_for_function(f"(expected) => JSON.stringify(({FRAME_MARKS_JS})()) === JSON.stringify(expected)",
                               arg=expected, timeout=timeout_ms)
    except PlaywrightTimeoutError:
        pass
    return page.evaluate(FRAME_MARKS_JS)


def test_R56_scrolling_the_frame_moves_the_marks(open_app):
    page = open_app(seed=seeds.S1, viewport=VIEWPORTS[1280]).page
    middle = page.evaluate("() => { const r = document.querySelector('#frameWrap')?.getBoundingClientRect();"
                           " return r ? [r.x + r.width / 2, r.y + r.height / 2] : null; }")
    assert middle is not None, "no #frameWrap"
    page.mouse.move(*middle)
    page.mouse.wheel(0, 2000)
    assert frame_marks_once(page, UP_ONLY) == UP_ONLY
    page.mouse.wheel(0, -2000)
    assert frame_marks_once(page, DOWN_ONLY) == DOWN_ONLY
    remove_button(page, "Nasi lemak ayam").click()
    remove_button(page, "Char kuey teow").click()
    assert frame_marks_once(page, NEITHER) == NEITHER


@pytest.mark.parametrize("field_of, text", [(lambda page: item_name(page, 1), "Nasi"), (lambda page: item_price(page, 1), "15.90")])
def test_R33_typing_in_an_item_field_keeps_focus_and_caret(open_app, field_of, text):
    page = open_app().page
    build_s1(page)
    type_and_watch(page, field_of(page), text)


# ---------------------------------------------------------------- Task 6: charges (R15, R10), v1.1.0 task A6
def rate_field(page, label):
    """The rate field named by its label.lbl, "Service charge" or "SST" (R15, no hidden ending since v1.1.0)."""
    return page.get_by_role("textbox", name=label, exact=True)


# qa.md "The Charges block and its defaults", read in one evaluate (null for a part the page does not hold).
CHARGES_BLOCK_JS = """() => { const one = (s) => document.querySelector(s);
  const cell = (id) => { const input = one(`input#${id}`); if (!input) return null;
    const unit = input.nextElementSibling;
    return { label: one(`label.lbl[for=${id}]`)?.textContent ?? null, value: input.value, field: input.parentElement.className,
      attrs: ['type', 'inputmode', 'autocomplete', 'aria-invalid', 'aria-describedby'].map((n) => input.getAttribute(n)),
      unit: unit?.matches('span.unit[aria-hidden=true]') ? unit.textContent : null }; };
  const err = (id) => { const p = one(`p.err#${id}`), first = p?.firstElementChild;
    return p && { text: p.textContent, hidden: p.hidden,
      icon: first?.matches('svg.ic') ? first.querySelector('use')?.getAttribute('href') ?? null : null }; };
  return { heading: one('h2.blk-h.solo#chargesH')?.textContent ?? null, svc: cell('svc'), sst: cell('sst'),
    svcErr: err('svcErr'), sstErr: err('sstErr'), hint: one('p.hint#chargeHint')?.textContent ?? null }; }"""
RATE_ATTRS = ["text", "decimal", "off", "false", "chargeHint"]


def test_R15_the_charges_block_and_its_defaults(open_app):
    page = open_app().page
    open_charges_first(page)
    assert page.evaluate(CHARGES_BLOCK_JS) == {
        "heading": "Charges",
        "svc": {"label": "Service charge", "value": "10", "field": "field pct", "attrs": RATE_ATTRS, "unit": "%"},
        "sst": {"label": "SST", "value": "6", "field": "field pct", "attrs": RATE_ATTRS, "unit": "%"},
        "svcErr": {"text": SERVICE_MESSAGE, "hidden": True, "icon": "#i-warning-circle"},
        "sstErr": {"text": SST_MESSAGE, "hidden": True, "icon": "#i-warning-circle"},
        "hint": "Set a charge to 0 if your bill already includes it."}
    assert displayed(page, "h2#chargesH") == [False]  # below 1024 px the header row names the section
    # Each label names its input, with no hidden " in percent" ending.
    for label, input_id in (("Service charge", "svc"), ("SST", "sst")):
        assert rate_field(page, label).evaluate_all("(els) => els.map((el) => el.id)") == [input_id]


def test_R15_a_rate_error_names_the_hint_first_and_then_its_error(open_app):
    # 1.0 put the error id first. Rule 13 puts the hint first. It rewrites the 1.0 test that read states.html (B1).
    page = open_app().page
    field = opened_rate_field("Service charge")(page)
    support.replace_text(page, field, "31")
    page.keyboard.press("Tab")
    assert field_error(field, "svcErr") == error_state(SERVICE_MESSAGE, "chargeHint svcErr", shown=True)
    in_cell = "() => document.querySelector('p.err#svcErr')?.parentElement.querySelector('label.lbl')?.getAttribute('for') ?? null"
    assert page.evaluate(in_cell) == "svc"


# ---------------------------------------------------------------- v1.1.0 task A9: the receipt and the card (R16 to R21)
# The receipt is read by support.receipt (RECEIPT_JS), shared with the live gate since task A20.
CARD_COPY = ["copyBtn", "btn btn-primary btn-block r-copy", "Copy summary", ["svg.ic", "#i-copy"]]
ONE_NEEDS = "1 item still needs a person. Tap who had it to see the splits."
TWO_NEED = "2 items still need a person. Tap who had each one to see the splits."


def card_figures(page):
    """The card's #rTotal and its splits (qa.md, "the splits are"), the figures the receipt follows on every change."""
    found = receipt(page)
    total = next((text for _, element_id, text in found["total"] or [] if element_id == "rTotal"), None)
    return [total, found["list"] and [row[1] for row in found["list"]["rows"]]]


def card_rows(page):
    """The card's splits rows and its proof, each as RECEIPT_JS gives them (None for a part the card does not hold)."""
    found = receipt(page)
    proof = found["proof"]
    return [found["list"] and found["list"]["rows"], proof and [proof["amount"], proof["working"]]]


def blocked_card(message):
    """The parts a blocked receipt holds (spec R17): the bare Total, then the mark and the message, nothing else."""
    return {"blocks": ["div.r-total", "div.r-empty"], "total": [["span.r-label", "", "Total"]],
            "note": ["div.r-empty", ["svg.ic", "#i-mark"], ["p", message]]}


# The strip's message and Copy summary (spec R17, R18, R49), null for a part the strip does not hold.
STRIP_MESSAGE_JS = """() => { const message = document.querySelector('#stripInfo > p.s-msg#stripMsg'), copy = document.querySelector('#stripCopy');
  return { message: message && [message.textContent, [...message.querySelectorAll('svg use')].map((use) => use.getAttribute('href'))],
           copy: copy && [copy.checkVisibility(), copy.disabled] }; }"""


def table_cells(page, part):
    """Cell texts of the 1.0 table.shares thead, tbody or tfoot, one list per row. Read only by a test marked for a later
    task (A18), which rewrites it to the receipt."""
    return page.evaluate(
        "(part) => [...document.querySelectorAll(`table.shares ${part} tr`)].map((tr) => [...tr.children].map((c) => c.textContent.trim()))",
        part)


def build_s2(page):
    """The S2 bill by gestures: Aisyah, Ben, Chen, Even, Subtotal 100.00."""
    three_people(page)
    subtotal_field(page).fill("100.00")


def build_s5(page):
    build_s1(page)
    toggle(page, "Mee goreng mamak", "Chen").click()


def test_R9_a_subtotal_drives_the_even_split(open_app):
    # [v1.1.0] The splits line of qa.md "The subtotal field drives the even split" (task A9). The field and the absent
    # spare line are test_R9_the_subtotal_field_drives_the_even_split.
    page = open_app().page
    subtotal_field(page).fill("100.00")
    assert card_rows(page) == [[["Person 1", "RM 58.30", None], ["Person 2", "RM 58.30", None]], ["RM 116.60", None]]


# Every element under `root` that is live, an aria-live attribute or a status, alert or log role, named by its id, a note
# of #notes by its place, and anything else by its tag and class (spec R16).
LIVE_JS = """(root) => [...document.querySelector(root).querySelectorAll('[aria-live], [role=status], [role=alert], [role=log]')]
  .map((el) => el.id ? `#${el.id}` : el.parentElement.id === 'notes' ? '#notes > div.note' : `${el.localName}.${el.className}`)"""


def test_R16_the_receipt_follows_every_keystroke_and_stays_quiet(open_app):
    # [v1.1.0] qa.md on K2 at 1280 x 800, the card and the strip. The sheet's line is the next test's (task A12).
    page = open_app(seed=seeds.S2, viewport=VIEWPORTS[1280]).page
    support.replace_text(page, subtotal_field(page), "5")
    assert card_figures(page) == ["RM 5.83", ["RM 1.95", "RM 1.94", "RM 1.94"]]
    page.keyboard.type("0")
    assert card_figures(page) == ["RM 58.30", ["RM 19.44", "RM 19.43", "RM 19.43"]]
    assert page.evaluate(LIVE_JS, "body") == ["#cardStatus", "#stripStatus"]


def test_R16_the_sheet_holds_one_live_element(open_app):
    # The sheet's line of qa.md "The receipt follows every keystroke and stays quiet" (R50, task A12).
    page = open_app(seed=seeds.S2, viewport=VIEWPORTS[1280]).page
    page.set_viewport_size({"width": 390, "height": 844})
    page.locator("#splitsBtn").click()
    assert page.evaluate(LIVE_JS, "#splitsDlg") == ["p.status"]


BLOCKED_CASES = [  # qa.md "When the splits cannot be worked out": the seed, the steps after load, the message
    pytest.param(seeds.S2, lambda page: support.replace_text(page, opened_rate_field("Service charge")(page), ""),
                 "Check the charges to see the splits.", id="K2-service-emptied"),
    pytest.param(seeds.S1, lambda page: support.replace_text(page, opened_rate_field("SST")(page), "25"),
                 "Check the charges to see the splits.", id="K1-sst-25"),
    pytest.param(seeds.S2, lambda page: support.replace_text(page, subtotal_field(page), ""),
                 "Enter the subtotal to see the splits.", id="K2-subtotal-emptied"),
    pytest.param(None, lambda page: None, "Enter the subtotal to see the splits.", id="cold-boot"),
    pytest.param(None, lambda page: switch_to(page, "By item"), "Add each item and tap who had it to see the splits.", id="by-item"),
    pytest.param(None, lambda page: (switch_to(page, "By item"), page.get_by_role("button", name="Add item", exact=True).click()),
                 "Add each item and tap who had it to see the splits.", id="by-item-add-item"),
    pytest.param(seeds.S1, lambda page: support.replace_text(page, item_price(page, 1), "abc"),
                 "Give every item a price to see the splits.", id="K1-one-price-abc"),
    pytest.param(seeds.S1, lambda page: [support.replace_text(page, item_price(page, n), "abc") for n in range(1, 5)],
                 "Add each item and tap who had it to see the splits.", id="K1-every-price-abc"),
]


@pytest.mark.parametrize("seed, setup, message", BLOCKED_CASES)
def test_R17_when_the_splits_cannot_be_worked_out(open_app, seed, setup, message):
    # [v1.1.0] The card's lines of the qa.md outline. The strip's and the sheet's are the next test's (tasks A11, A12).
    page = open_app(seed=seed).page
    setup(page)
    found = receipt(page)
    assert {key: found[key] for key in ("blocks", "total", "note")} == blocked_card(message)


@pytest.mark.parametrize("seed, setup, message", BLOCKED_CASES)
def test_R17_the_strip_and_the_sheet_say_why_too(open_app, seed, setup, message):
    # The strip's and the sheet's lines of qa.md "When the splits cannot be worked out" (R49 task A11, R50 task A12).
    page = open_app(seed=seed).page
    setup(page)
    assert page.evaluate(STRIP_MESSAGE_JS) == {"message": [message, []], "copy": [True, True]}
    page.locator("#splitsBtn").click()
    found = receipt(page, "#splitsDlg .rbody")
    assert found is not None, "the sheet holds no div.rbody"
    assert {key: found[key] for key in ("blocks", "total", "note")} == blocked_card(message)


def test_R18_items_that_still_need_a_person(open_app):
    # [v1.1.0] qa.md on K1, the card's lines. The needs marker is test_R18_every_item_with_nobody_carries_the_needs_marker
    # (task A8) and the strip's line the next test's (task A11).
    page = open_app(seed=seeds.S1).page
    toggle(page, "Mee goreng mamak", "Chen").click()
    found = receipt(page)
    assert found["blocks"] == ["div.r-total", "dl.r-lines", "div.r-rule", "div.r-msg"]
    assert found["total"] == [["span.r-label", "", "Total"], ["p.r-amount", "rTotal", "RM 69.26"]] and found["lines"] == S1_LINES
    assert found["note"] == ["div.r-msg", ["svg.ic", "#i-warning-circle"], ["p", ONE_NEEDS]]
    toggle(page, "Char kuey teow", "Ben").click()
    assert receipt(page)["note"] == ["div.r-msg", ["svg.ic", "#i-warning-circle"], ["p", TWO_NEED]]
    toggle(page, "Mee goreng mamak", "Chen").click()
    toggle(page, "Char kuey teow", "Ben").click()
    assert card_rows(page) == [S1_SPLITS, S1_PROOF] and receipt(page)["copy"] == CARD_COPY


def test_R18_the_strip_says_items_still_need_a_person(open_app):
    # The strip's line of qa.md "Items that still need a person". The strip is task A11's (R49).
    page = open_app(seed=seeds.S1).page
    toggle(page, "Mee goreng mamak", "Chen").click()
    assert page.evaluate(STRIP_MESSAGE_JS) == {"message": [ONE_NEEDS, ["#i-warning-circle"]], "copy": [True, True]}


def test_R7_the_item_left_with_nobody_needs_a_person_on_the_card(open_app):
    # [v1.1.0] The card's line of qa.md "Remove a person and they leave every item". The strip's line is
    # test_R7_the_item_left_with_nobody_needs_a_person_on_the_card_and_the_strip (task A11).
    page = open_app(seed=seeds.S1).page
    open_people_first(page)
    remove_button(page, "Chen").click()
    assert receipt(page)["note"] == ["div.r-msg", ["svg.ic", "#i-warning-circle"], ["p", ONE_NEEDS]]


@pytest.mark.parametrize("seed, figure, lines", [(seeds.S2, "116.60", S2_LINES), (seeds.S1, "69.26", S1_LINES)],
                         ids=["K2", "K1"])
def test_R19_total_and_bill_lines(open_app, seed, figure, lines):
    # [v1.1.0] qa.md "Total and bill lines" at 1280 x 800. The Total figure has its span.cur and the lines no working.
    found = receipt(open_app(seed=seed, viewport=VIEWPORTS[1280]).page)
    assert found["total"] == [["span.r-label", "", "Total"], ["p.r-amount", "rTotal", f"RM {figure}"]]
    assert found["amount"] == ["span.cur RM ", figure]
    assert found["blocks"][1:3] == ["dl.r-lines", "div.r-rule"] and found["lines"] == lines and found["rule"] == "true"


def test_R19_a_charge_of_zero_is_allowed_and_still_shown(open_app):
    # [v1.1.0] qa.md "A charge of 0 is allowed and still shown" (R15, R19) on K2 at 1280 x 800, with the spare line (task A13).
    page = open_app(seed=seeds.S2, viewport=VIEWPORTS[1280]).page
    support.replace_text(page, rate_field(page, "Service charge"), "0")
    assert shown_errors(page) == []
    assert receipt(page)["lines"][1:] == [["Service 0%", "RM 0.00"], ["SST 6%", "RM 6.00"]]
    assert card_figures(page)[1] == ["RM 35.34", "RM 35.33", "RM 35.33"]
    assert support.reads(page, "#spareLine") == "1 sen left over"


def test_R20_the_even_split_from_a_cold_boot(open_app):
    # [v1.1.0] qa.md key flow 1, the card's and the strip's lines with the spare line and chip (task A13). The sheet's
    # line is test_R20_the_sheet_lists_the_splits_as_the_card_does (task A12).
    page = open_app().page
    support.replace_text(page, person_field(page, 1), "Aisyah")
    support.replace_text(page, person_field(page, 2), "Ben")
    page.get_by_role("button", name="Add person").click()
    type_into(page, person_field(page, 3), "Chen")
    type_into(page, subtotal_field(page), "100.00")
    found = receipt(page)
    assert found["head"] == [["h2", "splitsH", None, "Splits"]]
    assert found["list"] == {"id": "splits", "cls": "r-splits", "labelledBy": "splitsH", "rowsVar": "", "rows": S2_SPLITS}
    assert found["proof"] == {"parts": ["svg.seal", "span.lbl-proof", "span.amt"], "seal": ["svg.seal", "#i-seal-check"],
                              "id": "addsUp", "amount": "RM 116.60", "working": None}
    assert support.reads(page, "#rbody > div.r-check") == "Adds up to RM 116.60"
    assert [support.reads(page, "#spareLine"), support.reads(page, "#spareBtn")] == ["2 sen left over", "Top of the list"]
    assert visible_text(page, "#stripInfo") == "Total RM 116.60"  # the strip reads (task A11, R49)


def test_R20_the_sheet_lists_the_splits_as_the_card_does(open_app):
    # The sheet's lines of qa.md key flow 1 (its bill is K2) and of "More than six people list in two columns on the
    # desktop" (R50, task A12). In the sheet only the heading carries an id (PD-20).
    page = open_app(seed=seeds.S2).page
    page.locator("#splitsBtn").click()
    found = receipt(page, "#splitsDlg .rbody")
    assert found is not None, "the sheet holds no div.rbody"
    assert found["head"] == [["h2", "sheetSplitsH", None, "Splits"]]
    assert found["list"] == {"id": "", "cls": "r-splits", "labelledBy": "sheetSplitsH", "rowsVar": "", "rows": S2_SPLITS}
    twelve = open_app(seed=seeds.T12).page
    twelve.locator("#splitsBtn").click()
    lefts = [left for left, _ in twelve.evaluate(ROW_EDGES_JS, "#splitsDlg .rbody")]
    assert len(lefts) == 12 and max(lefts) - min(lefts) <= 0.5, lefts


# The left and top edge of each splits row under `root`, in list order.
ROW_EDGES_JS = """(root) => [...document.querySelectorAll(root + ' > ul.r-splits > li')].map((li) => {
  const box = li.getBoundingClientRect(); return [box.left, box.top]; })"""


def in_two_columns(edges, rows):
    """Whether the splits rows at `edges` (ROW_EDGES_JS) stand in two columns with `rows` in the first: those share one
    left edge, the rest share another further right, and the first of the second column is level with row 1 (PD-17)."""
    def level(a, b):
        return abs(a - b) <= 0.5

    first, second = edges[:rows], edges[rows:]
    return (all(level(left, first[0][0]) for left, _ in first) and all(level(left, second[0][0]) for left, _ in second)
            and second[0][0] > first[0][0] + 0.5 and level(second[0][1], first[0][1]))


def test_R20_more_than_six_people_list_in_two_columns_on_the_desktop(open_app):
    # [v1.1.0] qa.md on T12 at 1280 x 800 (PD-17). The sheet's line is test_R20_the_sheet_lists_the_splits_as_the_card_does.
    page = open_app(seed=seeds.T12, viewport=VIEWPORTS[1280]).page
    found = receipt(page)["list"]
    assert found and [found["cls"], found["rowsVar"], len(found["rows"])] == ["r-splits many", "6", 12], found
    edges = page.evaluate(ROW_EDGES_JS, "#rbody")
    assert in_two_columns(edges, 6), edges
    for seed in (seeds.S2, seeds.T12I):
        assert receipt(open_app(seed=seed, viewport=VIEWPORTS[1280]).page)["list"]["cls"] == "r-splits"


@pytest.mark.parametrize("count", [7, 8, 9, 10, 11], ids=lambda count: f"{count}-people")
def test_R20_seven_to_eleven_people_list_in_two_columns_on_the_desktop(open_app, count):
    # R20 sets --rows to ceil(people / 2). Only an odd count tells that from a floor, which makes the grid open a third
    # column (code review CR-S5-7). T12 is the test above. The bill is T12 cut to its first `count` people.
    seed = seeds.changed(seeds.T12, lambda d: d["bill"].update(people=d["bill"]["people"][:count], nextId=count + 1))
    page = open_app(seed=seed, viewport=VIEWPORTS[1280]).page
    found, rows = receipt(page)["list"], (count + 1) // 2
    assert found and [found["cls"], found["rowsVar"], len(found["rows"])] == ["r-splits many", str(rows), count], found
    edges = page.evaluate(ROW_EDGES_JS, "#rbody")
    assert in_two_columns(edges, rows), edges


def test_R21_the_by_item_split_from_gestures(open_app):
    # [v1.1.0] qa.md key flow 2, the card's lines with the spare line (task A13).
    page = open_app().page
    build_s2(page)
    build_items_after_switch(page)
    assert receipt(page)["head"] == [["h2", "splitsH", None, "Splits"], ["span", "", "true", "items + charges"]]
    assert card_rows(page) == [S1_SPLITS, S1_PROOF]
    assert support.reads(page, "#spareLine") == "1 sen left over"
    working = page.evaluate("() => [...document.querySelectorAll('#splits > li > span.wk')].map((wk) => wk.textContent)")
    assert working == ["Items 24.90 + charges 4.14", "Items 13.50 + charges 2.24", "Items 21.00 + charges 3.48"]


def build_items_after_switch(page):
    switch_to(page, "By item")
    for name, price, people in S1_ITEMS:
        add_item_named(page, name, price, people)


def test_R21_someone_who_had_nothing_is_still_listed(open_app):
    # [v1.1.0] qa.md on the I2 seed at 1280 x 800, with the spare line (task A13).
    page = open_app(seed=seeds.I2, viewport=VIEWPORTS[1280]).page
    assert card_rows(page) == [[["Aisyah", "RM 0.00", "0.00 + 0.00"], ["Ben", "RM 14.59", "12.51 + 2.08"],
                                ["Chen", "RM 2.91", "2.50 + 0.41"]], ["RM 17.50", "15.01 + 2.49"]]
    assert support.reads(page, "#spareLine") == "2 sen left over"


def test_R8_the_receipt_follows_each_mode(open_app):
    page = open_app().page
    support.replace_text(page, subtotal_field(page), "100.00")
    switch_to(page, "By item")
    add_item_named(page, "Tea", "5.00", ["Person 1"])
    assert card_figures(page)[0] == "RM 5.83"
    switch_to(page, "Even")
    assert card_figures(page)[0] == "RM 116.60"


# ---------------------------------------------------------------- v1.1.0 task A10: copy summary and the status (R22 to R24, R5, R42)
FAILED_COPY = "Could not copy. Your browser blocked the clipboard."
# Every status paragraph the page holds (spec R24), the card's #cardStatus, the strip's #stripStatus and the sheet's
# p.status (task A12), each as whether it is displayed and its line, the class list, the role and the child nodes in
# order (an element as its tag and classes with the href of its use, a text node as its text). Null where the page
# holds none, so a paragraph that is not built fails on the assertion that names it, never on a wait.
STATUS_JS = """() => {
  const read = (el) => el && { shown: el.checkVisibility(), line: [el.className, el.getAttribute('role'),
    [...el.childNodes].map((node) => node instanceof Element
      ? [node.localName + [...node.classList].map((name) => '.' + name).join(''), node.querySelector('use')?.getAttribute('href') ?? null]
      : node.textContent)] };
  return { card: read(document.querySelector('#cardStatus')), strip: read(document.querySelector('#stripStatus')),
           sheet: read(document.querySelector('#splitsDlg p.status')) };
}"""
COPIED = ["status", "status", [["svg.ic", "#i-check"], "Summary copied"]]
COPY_REFUSED = ["status is-fail", "status", [["svg.ic", "#i-warning-circle"], FAILED_COPY]]
NO_STATUS = ["status", "status", []]


def status_lines(page):
    """The line of each status paragraph (STATUS_JS) by place, card, strip and sheet, None where the page holds none."""
    return {place: found and found["line"] for place, found in page.evaluate(STATUS_JS).items()}


def statuses_shown(page):
    """Whether each status paragraph is displayed (STATUS_JS) by place, None where the page holds none."""
    return {place: found and found["shown"] for place, found in page.evaluate(STATUS_JS).items()}


def click_copy(page, selector):
    """Click the Copy summary at `selector` and wait two frames, so the clipboard's answer is on screen. A button the
    page does not hold fails here on its count, never on a wait."""
    button = page.locator(selector)
    assert button.count() == 1, f"no {selector}"
    button.click()
    settle(page)


def copy_summary(page):
    """The one Copy summary shown at this width (the card's from 1024 px, the strip's below), as a 1.0 test pressed it."""
    page.get_by_role("button", name="Copy summary").click()
    settle(page)


COPY_BUTTON = {"card": "#copyBtn", "strip": "#stripCopy", "sheet": "#splitsDlg .r-copy"}
COPY_CASES = [  # qa.md "Copy summary puts the exact text on the clipboard": seed, width, the Copy summary clicked, the text
    pytest.param(seeds.S2, 1280, "card", S2_COPY, id="K2-1280-card"),
    pytest.param(seeds.S2, 390, "sheet", S2_COPY, id="K2-390-sheet"),
    pytest.param(seeds.S2, 390, "strip", S2_COPY, id="K2-390-strip"),
    pytest.param(seeds.S1, 1280, "card", S1_COPY, id="K1-1280-card"),
    pytest.param(seeds.S1, 390, "sheet", S1_COPY, id="K1-390-sheet"),
    pytest.param(seeds.S1, 390, "strip", S1_COPY, id="K1-390-strip"),
]


@pytest.mark.parametrize("seed, width, place, text", COPY_CASES)
def test_R22_copy_summary_puts_the_exact_text_on_the_clipboard(open_app, seed, width, place, text):
    # [v1.1.0] Every status paragraph present shows it, the card's at any width (it is in the DOM below 1024 px), the
    # strip's at any width, and the sheet's while the sheet is open.
    page = open_app(seed=seed, viewport=VIEWPORTS[width]).page
    if place == "sheet":
        page.locator("#splitsBtn").click()
    click_copy(page, COPY_BUTTON[place])
    assert page.evaluate("[window.testClipboardText, window.testClipboardWrites]") == [text, 1]
    assert status_lines(page) == {"card": COPIED, "strip": COPIED, "sheet": COPIED if place == "sheet" else None}


def test_R22_a_bill_from_rm_1000_copies_with_thousands_commas(open_app):
    # [v1.1.0] qa.md on W1 at 1280 x 800. CG-P1 ruled by the owner, the comma is in the copied summary too (core R24).
    page = open_app(seed=seeds.W1, viewport=VIEWPORTS[1280]).page
    click_copy(page, "#copyBtn")
    assert page.evaluate("window.testClipboardText") == "\n".join([
        "Bill split", "Total RM 1,193.87 (subtotal RM 1,023.90, service 10% RM 102.39, SST 6% RM 67.58)",
        "Aisyah RM 1,153.65", "Ben RM 15.74", "Chen RM 24.48", "Adds up to RM 1,193.87"])


def test_R23_the_browser_blocks_the_clipboard(open_app):
    # [v1.1.0] qa.md on K2 with reject.js. Its strip height line is test_R23_a_blocked_copy_grows_the_strip (task A11).
    session = open_app(seed=seeds.S2, clipboard="reject")
    page = session.page
    click_copy(page, "#stripCopy")
    assert status_lines(page) == {"card": COPY_REFUSED, "strip": COPY_REFUSED, "sheet": None}
    assert session.problems() == [] and stored_text(page) == seeds.S2


def test_R23_a_blocked_copy_grows_the_strip(open_app):
    # The strip line of qa.md "The browser blocks the clipboard". The strip's height and --strip-h are task A11's (R49).
    page = open_app(seed=seeds.S2, clipboard="reject").page
    click_copy(page, "#stripCopy")
    height, strip_h = page.evaluate("() => [document.querySelector('#strip').getBoundingClientRect().height, "
                                    "getComputedStyle(document.documentElement).getPropertyValue('--strip-h').trim()]")
    assert abs(height - 153) <= 0.5 and strip_h == "153px", (height, strip_h)


def test_R23_the_clipboard_api_is_missing(open_app):
    # [v1.1.0] qa.md on K2 with missing.js.
    session = open_app(seed=seeds.S2, clipboard="missing")
    page = session.page
    click_copy(page, "#stripCopy")
    assert status_lines(page)["strip"] == COPY_REFUSED and session.problems() == []


# A point of the top bar where only the bar itself or the empty #notes lies, for qa.md "click empty space in the top bar".
EMPTY_TOP_BAR_POINT_JS = """() => { const bar = document.querySelector('header.top'), box = bar.getBoundingClientRect();
  const y = box.top + box.height / 2;
  for (let x = Math.ceil(box.left) + 1; x < box.right - 1; x += 1) {
    const hit = document.elementFromPoint(x, y);
    if (hit === bar || hit?.id === 'notes') return [x, y];
  }
  return null; }"""
# qa.md "Press Escape" while a dialog is open: a close listener goes on the open dialog before the key press. With P1
# over the Splits sheet both are open, and Escape closes the one on top, the last open one in tree order (task A13).
WATCH_DIALOG_CLOSE_JS = """() => { const open = [...document.querySelectorAll('dialog[open]')].pop(); if (!open) return false;
  window.testDialogClosed = false; open.addEventListener('close', () => { window.testDialogClosed = true; }, { once: true });
  return true; }"""


def closing(page, gesture):
    """Run `gesture`, a callable that should close the open dialog, and wait for that dialog's close event, at most 2 s.
    With none open, only the gesture. M1 gives focus back to New bill in its close event, which the HTML close steps
    queue a task after the close, so every M1 close a test reads focus after waits here (spec R59 (2) for Escape, the
    same race for Cancel, Start new bill and the backdrop, F-A3-1, task A16)."""
    watching = page.evaluate(WATCH_DIALOG_CLOSE_JS)
    gesture()
    if watching:
        try:
            page.wait_for_function("() => window.testDialogClosed", timeout=2000)
        except PlaywrightTimeoutError:
            pytest.fail("dialog still open after 2 s")


def press_escape(page):
    """qa.md "Press Escape": with a dialog open, press Escape and wait for its close event, at most 2 s. With none
    open (the Splits sheet before task A12), only the key press."""
    closing(page, lambda: page.keyboard.press("Escape"))


def test_R24_the_status_lasts_until_the_next_change_to_the_bill(open_app):
    # [v1.1.0] qa.md on K2 at 390 x 844. Rule 10 replaces 1.0's PD-5. The sheet's line ("the sheet's p.status read it too
    # while the sheet was open") is test_R24_the_sheet_shows_the_status_while_it_is_open (task A12).
    page = open_app(seed=seeds.S2).page
    assert status_lines(page) == {"card": NO_STATUS, "strip": NO_STATUS, "sheet": None}
    assert statuses_shown(page) == {"card": False, "strip": False, "sheet": None}
    click_copy(page, "#stripCopy")
    assert status_lines(page) == {"card": COPIED, "strip": COPIED, "sheet": None}
    point = page.evaluate(EMPTY_TOP_BAR_POINT_JS)
    assert point, "no empty point in the top bar"
    page.mouse.click(*point)
    page.locator("#peopleBtn").click()
    page.locator("#peopleBtn").click()
    page.locator("#splitsBtn").click()
    press_escape(page)
    open_dialog(page)
    page.get_by_role("button", name="Cancel").click()
    page.set_viewport_size({"width": 400, "height": 844})
    assert status_lines(page) == {"card": COPIED, "strip": COPIED, "sheet": None}
    open_people_first(page)
    type_at_end(page, person_field(page, 1), "x")
    assert status_lines(page) == {"card": NO_STATUS, "strip": NO_STATUS, "sheet": None}
    assert statuses_shown(page) == {"card": False, "strip": False, "sheet": None}
    click_copy(page, "#stripCopy")
    assert status_lines(page)["strip"] == COPIED
    page.reload()
    assert status_lines(page) == {"card": NO_STATUS, "strip": NO_STATUS, "sheet": None}


def test_R24_the_sheet_shows_the_status_while_it_is_open(open_app):
    # The sheet's line of qa.md "The status lasts until the next change to the bill" (R50, task A12).
    page = open_app(seed=seeds.S2).page
    click_copy(page, "#stripCopy")
    page.locator("#splitsBtn").click()
    assert status_lines(page) == {"card": COPIED, "strip": COPIED, "sheet": COPIED}
    press_escape(page)
    assert status_lines(page) == {"card": COPIED, "strip": COPIED, "sheet": None}


def test_R22_a_failed_copy_is_replaced_by_the_next_attempt(open_app):
    # [v1.1.0] Spec R24, each attempt replaces the previous text and class.
    page = open_app(seed=seeds.S2, clipboard="reject").page
    click_copy(page, "#stripCopy")
    assert status_lines(page)["strip"] == COPY_REFUSED
    page.evaluate("() => { Clipboard.prototype.writeText = () => Promise.resolve(); }")
    click_copy(page, "#stripCopy")
    assert status_lines(page) == {"card": COPIED, "strip": COPIED, "sheet": None}


# The clipboard's answer waits until the test calls window.finishCopy, as a permission prompt would make it wait.
WAITING_CLIPBOARD_JS = "() => { Clipboard.prototype.writeText = () => new Promise((resolve) => { window.finishCopy = resolve; }); }"
WHILE_THE_COPY_WAITS = [  # a change to the bill made while the copy waits, and the card's status line after the answer
    pytest.param(lambda page: support.replace_text(page, subtotal_field(page), ""), None, id="splits-left"),
    pytest.param(lambda page: (open_people_first(page), type_at_end(page, person_field(page, 1), "x")), NO_STATUS,
                 id="name-typed"),
]


@pytest.mark.parametrize("change, card", WHILE_THE_COPY_WAITS)
def test_R24_an_answer_that_comes_after_a_change_sets_no_status(open_app, change, card):
    # [v1.1.0] The 1.0 test of a late answer, with rule 10. The change cleared the status, and the summary the browser
    # copied is not the one on screen any more, so the late answer shows nothing (BUILD.md, task A10, judgment call 2).
    page = open_app(seed=seeds.S2).page
    page.evaluate(WAITING_CLIPBOARD_JS)
    click_copy(page, "#stripCopy")
    assert page.evaluate("typeof window.finishCopy") == "function", "the copy is not waiting for its answer"
    change(page)
    page.evaluate("() => window.finishCopy()")
    settle(page)
    assert status_lines(page) == {"card": card, "strip": NO_STATUS, "sheet": None}


def test_R5_a_new_name_reaches_the_copied_text(open_app):
    page = open_app().page
    build_s1(page)
    person_field(page, 3).click()
    page.keyboard.press("End")
    page.keyboard.type(" Wei")
    copy_summary(page)
    assert (page.evaluate("window.testClipboardText") or "").splitlines()[4:5] == ["Chen Wei RM 24.48"]


def test_R42_duplicate_names_through_the_whole_flow(open_app):
    # [v1.1.0] qa.md "Two people may have the same name", from a cold boot at 390 x 844, where People is open.
    page = open_app().page
    support.replace_text(page, person_field(page, 1), "Ben")
    support.replace_text(page, person_field(page, 2), "Ben")
    page.get_by_role("button", name="Add person").click()
    type_into(page, person_field(page, 3), "Chen")
    type_into(page, subtotal_field(page), "100.00")
    shown = "() => [document.querySelectorAll('p.err:not([hidden])').length, document.querySelectorAll('#notes div.note').length]"
    assert page.evaluate(shown) == [0, 0]
    assert [person_field(page, number).input_value() for number in (1, 2)] == ["Ben", "Ben"]
    assert card_rows(page) == [[["Ben", "RM 38.87", None], ["Ben", "RM 38.87", None], ["Chen", "RM 38.86", None]],
                               ["RM 116.60", None]]
    assert remove_button(page, "Ben").count() == 2
    click_copy(page, "#stripCopy")
    assert (page.evaluate("window.testClipboardText") or "").splitlines()[2:4] == ["Ben RM 38.87", "Ben RM 38.87"]
    switch_to(page, "By item")
    page.get_by_role("button", name="Add item", exact=True).click()
    type_into(page, item_name(page, 1), "Tea")
    type_into(page, page.get_by_label("Tea price in RM", exact=True), "10.00")
    who_group(page, "Tea").get_by_role("button", name="Ben", exact=True).nth(1).click()
    assert [b.get_attribute("aria-pressed") for b in who_group(page, "Tea").get_by_role("button").all()] == ["false", "true", "false"]
    assert card_rows(page) == [[["Ben", "RM 0.00", "0.00 + 0.00"], ["Ben", "RM 11.66", "10.00 + 1.66"],
                                ["Chen", "RM 0.00", "0.00 + 0.00"]], ["RM 11.66", "10.00 + 1.66"]]
    remove_button(page, "Ben").nth(1).click()
    assert [field.input_value() for field in page.locator("li.person input").all()] == ["Ben", "Chen"]
    assert receipt(page)["note"] == ["div.r-msg", ["svg.ic", "#i-warning-circle"], ["p", ONE_NEEDS]]
    assert [(person["id"], person["name"]) for person in stored(page)["bill"]["people"]] == [("p1", "Ben"), ("p3", "Chen")]


# ---------------------------------------------------------------- v1.1.0 task A11: the strip (R49)
# The strip in one evaluate, so a part that is not built fails on the assertion that names it, never on a wait. A node is
# a text as its text, an svg as its class and the href of its use, and any other element as its tag and classes, its id
# and its child nodes. The strip's place is whether it is displayed, its position, the gap from its bottom edge to the
# viewport's and its height, both rounded to whole px (a measured number matches within 0.5 px, qa.md Phrases), and the
# root's --strip-h. The status's place is "beside" the Total (to its right on the same line) or "under" it, with its
# number of text lines, or null and 0 while it is not displayed.
STRIP_JS = """() => {
  const one = (selector) => document.querySelector(selector);
  const strip = one('#strip'), info = one('#stripInfo'), status = one('#stripStatus'), copy = one('#stripCopy'), splits = one('#splitsBtn');
  const part = (node) => node.nodeType === 3 ? node.textContent
    : node.localName === 'svg' ? ['svg.' + node.getAttribute('class'), node.querySelector('use')?.getAttribute('href') ?? null]
    : [node.localName + [...node.classList].map((name) => '.' + name).join(''), node.id || null, [...node.childNodes].map(part)];
  const box = strip.getBoundingClientRect();
  let place = null, lines = 0;
  if (status.checkVisibility()) {
    const s = status.getBoundingClientRect(), i = info.getBoundingClientRect();
    place = s.left >= i.right - 0.5 && s.top < i.bottom && s.bottom > i.top ? 'beside' : s.top >= i.bottom - 0.5 ? 'under' : 'overlapping';
    const range = document.createRange();
    range.selectNode([...status.childNodes].find((node) => node.nodeType === 3));
    lines = new Set([...range.getClientRects()].filter((r) => r.width > 0).map((r) => Math.round(r.top))).size;
  }
  return {
    strip: [strip.checkVisibility(), getComputedStyle(strip).position, Math.round(innerHeight - box.bottom), Math.round(box.height),
            getComputedStyle(document.documentElement).getPropertyValue('--strip-h').trim()],
    info: [...info.childNodes].map(part),
    status: [status.className, [...status.childNodes].map(part), place, lines],
    copy: [copy.checkVisibility(), copy.disabled],
    splits: [splits.disabled, splits.getAttribute('aria-haspopup'), splits.getAttribute('aria-controls'), splits.getAttribute('aria-expanded')],
  };
}"""


def strip_total(figure):
    """#stripInfo of an even or by-item result (spec R49), the label "Total", then the figure with its span.cur."""
    return [["span.s-label", None, ["Total"]], ["span.s-fig", "stripTotal", [["span.cur", None, ["RM "]], figure]]]


def strip_message(text, icon=None):
    """#stripInfo of a blocked or unassigned result (spec R17, R18), p.s-msg#stripMsg with the icon first if it has one."""
    return [["p.s-msg", "stripMsg", ([["svg.ic", icon]] if icon else []) + [text]]]


STRIP_NO_STATUS = ["status", [], None, 0]
STRIP_CASES = [  # qa.md "The strip for each result": seed, clipboard script, click #stripCopy first, height, info, status, disabled
    pytest.param(seeds.S1, "recorder", False, 111, strip_total("69.26"), STRIP_NO_STATUS, False, id="K1"),
    pytest.param(seeds.S2, "recorder", False, 111, strip_total("116.60"), STRIP_NO_STATUS, False, id="K2"),
    pytest.param(None, "recorder", False, 108, strip_message("Enter the subtotal to see the splits."), STRIP_NO_STATUS, True,
                 id="cold-boot"),
    pytest.param(seeds.RE, "recorder", False, 108, strip_message("Check the charges to see the splits."), STRIP_NO_STATUS, True,
                 id="RE"),
    pytest.param(seeds.S5, "recorder", False, 128, strip_message(ONE_NEEDS, "#i-warning-circle"), STRIP_NO_STATUS, True, id="BU"),
    pytest.param(seeds.S2, "recorder", True, 111, strip_total("116.60"), ["status", COPIED[2], "beside", 1], False,
                 id="K2-copied"),
    pytest.param(seeds.S2, "reject", True, 153, strip_total("116.60"), ["status is-fail", COPY_REFUSED[2], "under", 2], False,
                 id="K2-refused"),
]


@pytest.mark.parametrize("seed, clipboard, copy_first, height, info, status, disabled", STRIP_CASES)
def test_R49_the_strip_for_each_result(open_app, seed, clipboard, copy_first, height, info, status, disabled):
    # qa.md at 390 x 844. "Fixed at the bottom of the viewport" is position fixed with no gap under the strip.
    page = open_app(seed=seed, clipboard=clipboard).page
    if copy_first:
        click_copy(page, "#stripCopy")
    assert page.evaluate(STRIP_JS) == {"strip": [True, "fixed", 0, height, f"{height}px"], "info": info, "status": status,
                                       "copy": [True, disabled], "splits": [False, "dialog", "splitsDlg", "false"]}


# The focused control (its id, its name or its text, and whether it is a toggle), its bottom edge and the strip's top edge.
FOCUS_OVER_STRIP_JS = """() => { const focused = document.activeElement, strip = document.querySelector('#strip');
  return [focused.id || focused.getAttribute('aria-label') || focused.textContent.trim(), focused.matches('button.tap'),
          focused.getBoundingClientRect().bottom, strip.getBoundingClientRect().top]; }"""
LAST_TOGGLE_OVER_STRIP_JS = """() => { scrollTo(0, document.documentElement.scrollHeight);
  return [[...document.querySelectorAll('button.tap')].at(-1).getBoundingClientRect().bottom,
          document.querySelector('#strip').getBoundingClientRect().top]; }"""


def test_R49_no_control_the_user_tabs_to_is_left_under_the_strip(open_app):
    # qa.md on K1 at 390 x 844 with both sections opened first. Tab starts after New bill, the first control of the page,
    # and stops at Splits, the strip's own first control. All 12 toggles must be among the stops, so a walk that skipped
    # the bottom of the page cannot pass. WebKit's own focus scroll leaves a control that is inside the viewport where it
    # is, under the strip, and does not read scroll-padding-bottom, so in WebKit it holds through the app's focus scroll
    # (spec R49, task A21, F-A11-1).
    page = open_app(seed=seeds.S1).page
    open_people_first(page)
    open_charges_first(page)
    new_bill_button(page).focus()
    stops, under = [], []
    for _ in range(80):
        page.keyboard.press("Tab")
        name, is_toggle, bottom, strip_top = page.evaluate(FOCUS_OVER_STRIP_JS)
        if name == "splitsBtn":
            break
        stops.append([name, is_toggle])
        if bottom > strip_top + 0.5:
            under.append([name, bottom, strip_top])
    else:
        pytest.fail(f"Tab gave up after 80 presses without reaching Splits, the last stops were {stops[-3:]}")
    assert under == [] and sum(is_toggle for _, is_toggle in stops) == 12, (under, stops)
    toggle_bottom, strip_top = page.evaluate(LAST_TOGGLE_OVER_STRIP_JS)
    assert toggle_bottom < strip_top, (toggle_bottom, strip_top)


# The app's scrollIntoView calls (R49, the focus scroll), counted by a wrapper the test adds before any gesture. The
# browser's own focus scroll never calls the script method, so the count is the app's alone.
COUNT_SCROLL_INTO_VIEW_JS = """() => { window.testScrollIntoViewCalls = 0; const original = Element.prototype.scrollIntoView;
  Element.prototype.scrollIntoView = function (...options) { window.testScrollIntoViewCalls += 1; return original.apply(this, options); }; }"""
# Whether the focused element is the one `selector` names, its bottom edge, the strip's top edge and the app's calls so far.
FOCUSED_AGAINST_STRIP_JS = """(selector) => { const focused = document.activeElement;
  return [focused === document.querySelector(selector), focused.getBoundingClientRect().bottom,
          document.querySelector('#strip').getBoundingClientRect().top, window.testScrollIntoViewCalls]; }"""


def test_R49_the_app_scrolls_a_focused_control_only_below_1024_px_and_only_when_the_strip_covers_it(open_app):
    # qa.md, spec R49 "The focus scroll". It passes before task A21, so its teeth come from stubs of the handler
    # (BUILD.md, A21). The control clear of the strip and the sheet are first checked to be where the scenario puts them.
    page = open_app(seed=seeds.RND, viewport=(1280, 800)).page
    page.evaluate(COUNT_SCROLL_INTO_VIEW_JS)
    new_bill_button(page).focus()
    tab_until(page, subtotal_field(page))
    assert page.evaluate("window.testScrollIntoViewCalls") == 0, "the app scrolled from 1024 px"
    page.set_viewport_size({"width": 390, "height": 844})
    new_bill_button(page).focus()
    page.keyboard.press("Tab")
    focused, bottom, strip_top, calls = page.evaluate(FOCUSED_AGAINST_STRIP_JS, "#peopleBtn")
    assert focused and bottom < strip_top, (focused, bottom, strip_top)
    assert calls == 0, "the app scrolled a control the strip does not cover"
    for control in ("#splitsBtn", "#stripCopy"):
        page.locator(control).focus()
        focused, _, _, calls = page.evaluate(FOCUSED_AGAINST_STRIP_JS, control)
        assert focused and calls == 0, f"{control} focused {focused}, the app's calls {calls}"
    page.locator("#splitsBtn").click()
    focused, bottom, strip_top, calls = page.evaluate(FOCUSED_AGAINST_STRIP_JS, "#splitsDlg > div.sheet")
    assert focused, "div.sheet does not have focus"
    assert bottom > strip_top, f"the sheet's bottom edge {bottom} is not below the strip's top edge {strip_top}"
    assert calls == 0, "the app scrolled the sheet, which sits above the strip"


# ---------------------------------------------------------------- v1.1.0 task A12: the Splits sheet (R50)
# The Splits sheet in one evaluate (spec R50): the dialog, its sheet with the parts R50 names in order, where focus is,
# Splits' aria-expanded and every id inside the dialog. A part the dialog does not hold reads as null, so a sheet that is
# not built fails on the assertion that names it, never on a wait.
SHEET_JS = """() => {
  const dialog = document.querySelector('#splitsDlg'), sheet = dialog.querySelector(':scope > div.sheet');
  const label = (el) => el.localName + [...el.classList].map((name) => '.' + name).join('');
  const kids = (el) => el ? [...el.children].map(label) : null;
  const top = sheet?.querySelector(':scope > div.sheet-top'), close = top?.querySelector(':scope > button') ?? null;
  const active = document.activeElement;
  return {
    open: dialog.open, modal: dialog.matches(':modal'), name: dialog.getAttribute('aria-label'), children: kids(dialog),
    sheet: sheet && { tabindex: sheet.getAttribute('tabindex'), children: kids(sheet),
      foil: sheet.querySelector(':scope > div.foil')?.getAttribute('aria-hidden') ?? null,
      top: kids(top), grab: top?.querySelector(':scope > span.grab')?.getAttribute('aria-hidden') ?? null,
      close: close && [close.getAttribute('type'), close.getAttribute('aria-label'), close.querySelector('use')?.getAttribute('href') ?? null],
      scroll: kids(sheet.querySelector(':scope > div.sheet-scroll#sheetScroll')) },
    focus: active === sheet ? 'the sheet' : active.id || active.localName,
    expanded: document.querySelector('#splitsBtn').getAttribute('aria-expanded'),
    ids: [...dialog.querySelectorAll('[id]')].map((el) => el.id),
  };
}"""
SHEET_OPEN = {
    "open": True, "modal": True, "name": "Splits", "children": ["div.glass.dense.sheet"],
    "sheet": {"tabindex": "-1", "children": ["div.foil", "div.sheet-top", "div.sheet-scroll"], "foil": "true",
              "top": ["span.grab", "button.icon-btn"], "grab": "true", "close": ["button", "Close", "#i-x"], "scroll": ["div.rbody"]},
    "focus": "the sheet", "expanded": "true", "ids": ["sheetScroll", "sheetSplitsH"],
}
# qa.md "#splitsDlg is closed and has no child element, and #splitsBtn has aria-expanded 'false' and focus".
SHEET_CLOSED = {"open": False, "children": [], "expanded": "false", "focus": "splitsBtn"}


def sheet_state(page, keys=None):
    """SHEET_JS, or only its `keys`."""
    found = page.evaluate(SHEET_JS)
    return found if keys is None else {key: found[key] for key in keys}


def open_sheet(page):
    """Click Splits and check that the sheet opened, so a later step fails on this assertion and never waits for a part."""
    page.locator("#splitsBtn").click()
    assert page.evaluate("() => document.querySelector('#splitsDlg').open"), "the sheet did not open"


def test_R50_the_splits_sheet_opens_with_the_cards_receipt(open_app):
    # qa.md on K1 at 390 x 844. "Is named" is read as the role and name a screen reader gets, and the receipt by "reads".
    page = open_app(seed=seeds.S1).page
    assert sheet_state(page, ("open", "children")) == {"open": False, "children": []}
    page.locator("#splitsBtn").click()
    assert sheet_state(page) == SHEET_OPEN
    assert page.get_by_role("dialog", name="Splits", exact=True).count() == 1
    assert support.reads(page, "#splitsDlg .rbody") == card_text(page)


@pytest.mark.parametrize("size, close", [((390, 844), "close"), ((390, 844), "escape"), ((390, 844), (195, 80)),
                                         ((360, 780), (180, 80))],
                         ids=["390-close", "390-escape", "390-backdrop", "360-backdrop"])
def test_R50_closing_the_sheet_returns_focus_to_splits(open_app, size, close):
    # qa.md on K1. The backdrop points are docs/design/LINKS.json's, above the sheet, on its ::backdrop.
    page = open_app(seed=seeds.S1, viewport=size).page
    open_sheet(page)
    if close == "close":
        button = page.locator("#splitsDlg button[aria-label=Close]")
        assert button.count() == 1, "the sheet holds no Close"
        button.click()
    elif close == "escape":
        press_escape(page)
    else:
        page.mouse.click(*close)
    assert sheet_state(page, SHEET_CLOSED) == SHEET_CLOSED


def test_R50_a_press_that_starts_in_the_sheet_and_ends_on_the_backdrop_does_not_close_it(open_app):
    # qa.md on K1 at 390 x 844. The click goes to the dialog, the common ancestor, at a point on the backdrop (R30 (1)).
    page = open_app(seed=seeds.S1).page
    open_sheet(page)
    drag(page, centre_of(page.locator("#splitsDlg .r-amount")), (195, 80))
    assert sheet_state(page, ("open", "children")) == {"open": True, "children": ["div.glass.dense.sheet"]}


@pytest.mark.parametrize("gesture", ["touch-double", "mouse-double"])
@pytest.mark.parametrize("size", [(390, 844), (360, 780)], ids=["390x844", "360x780"])
def test_R50_a_repeat_press_on_splits_leaves_the_sheet_open_and_copies_nothing(open_app, size, gesture):
    # qa.md (PD-21). The sheet rises under the second press, and its Copy summary is there.
    page = open_app(seed=seeds.S1, viewport=size, touch=gesture == "touch-double").page
    page.evaluate(RECORD_BODY_CLICKS_JS)
    gesture_at(page, gesture, centre_of(page.locator("#splitsBtn")))
    assert sheet_state(page, ("open",)) == {"open": True} and page.evaluate("window.testClipboardWrites") == 0
    assert_only_press_1_and_click_1_reached_the_page(page, 2, tapped=gesture == "touch-double")


@pytest.mark.parametrize("gesture", ["mouse-double", "touch-double"])
@pytest.mark.parametrize("point", ["close", (195, 80)], ids=["close", "backdrop"])
def test_R50_the_second_press_of_a_double_activation_that_closed_the_sheet_never_reaches_the_page(open_app, point, gesture):
    # qa.md on K1 at 390 x 844 (PD-21, F-A12-1, task A18). The backdrop point is LINKS.json's. The body recorder proves
    # the cancel whatever lies under the second press. It passes on the tree before A18, so its teeth come from a stub of
    # the sheet's click close (BUILD.md, A18).
    page = open_app(seed=seeds.S1, touch=gesture == "touch-double").page
    noted = stored_text(page)
    open_sheet(page)
    page.evaluate(RECORD_BODY_CLICKS_JS)
    gesture_at(page, gesture, centre_of(page.locator("#splitsDlg button[aria-label=Close]")) if point == "close" else point)
    assert sheet_state(page, SHEET_CLOSED) == SHEET_CLOSED
    assert_only_press_1_and_click_1_reached_the_page(page, 2, tapped=gesture == "touch-double")
    assert page.evaluate("window.testClipboardWrites") == 0 and stored_text(page) == noted


FOCUSIN_RECORDER_JS = """() => { window.testFocusins = [];
  document.addEventListener('focusin', (event) => window.testFocusins.push(event.target.id || event.target.localName), true); }"""


def test_R50_the_sheet_closes_itself_when_the_window_reaches_1024_px(open_app, request):
    # qa.md on K1 (PD-18, the app moves no focus). The browser's own dialog close step may return focus to Splits, so a
    # focusin there is allowed, and where focus ends is recorded per engine in the run's evidence folder.
    page = open_app(seed=seeds.S1).page
    open_sheet(page)
    page.evaluate(FOCUSIN_RECORDER_JS)
    page.set_viewport_size({"width": 1024, "height": 768})
    try:
        page.wait_for_function("() => !document.querySelector('#splitsDlg').open", timeout=2000)
    except PlaywrightTimeoutError:
        pass  # gave up after 2 s, and the assertion below names the sheet that is still open
    settle(page)  # a focus that the close event would move comes a task later
    found, focusins = sheet_state(page, ("open", "children", "expanded", "focus")), page.evaluate("window.testFocusins")
    record = request.getfixturevalue("evidence_folder") / "R50-sheet-closed-at-1024.txt"
    record.write_text(json.dumps({"focusins": focusins, "focused afterwards": found["focus"]}) + "\n", encoding="utf-8")
    assert {key: found[key] for key in ("open", "children", "expanded")} == {"open": False, "children": [], "expanded": "false"}
    assert [target for target in focusins if target != "splitsBtn"] == [], focusins


def test_R50_the_sheet_follows_the_bill_while_it_is_open(open_app):
    # qa.md on K2 at 390 x 844. The chip's count is asserted before its click, so a sheet with no chip fails at once.
    page = open_app(seed=seeds.S2).page
    open_sheet(page)
    chip = page.locator(SHEET_SPARE_CHIP)
    assert chip.count() == 1, "the sheet holds no spare chip"
    chip.click()
    page.locator("#spareDlg label.choice", has_text="One person").click()
    assert page.evaluate("() => document.querySelector('#spareDlg').open") is True
    assert [row[1] for row in receipt(page, "#splitsDlg .rbody")["list"]["rows"]] == ["RM 38.88", "RM 38.86", "RM 38.86"]


# ---------------------------------------------------------------- v1.1.0 task A13: the spare line, the chips and P1 (R51, R52)
# The spare line of the div.rbody at `root` in one evaluate (spec R51), null when it has none: the block before it, its
# children, its p, and each chip of div.r-spare-acts with its own text and icons in order.
SPARE_LINE_JS = """(root) => {
  const spare = document.querySelector(root)?.querySelector(':scope > div.r-spare');
  if (!spare) return null;
  const line = spare.querySelector(':scope > p'), acts = spare.querySelector(':scope > div.r-spare-acts');
  const parts = (el) => [...el.childNodes].map((node) => node instanceof Element
    ? `${node.localName}.${node.getAttribute('class')} ${node.querySelector('use')?.getAttribute('href')}` : node.textContent);
  return { after: spare.previousElementSibling?.className ?? null, children: [...spare.children].map((el) => el.localName),
    line: line && [line.id, line.textContent],
    chips: acts && [...acts.children].map((el) => [el.localName, el.id, el.className, el.getAttribute('type'),
      el.getAttribute('aria-haspopup'), el.getAttribute('aria-label'), parts(el)]) };
}"""
PICK_AGAIN_CHIP = ["button", "pickAgain", "chip-btn", "button", None, None, ["svg.ic #i-shuffle", "Pick again"]]


def spare_line(page, root="#rbody"):
    return page.evaluate(SPARE_LINE_JS, root)


def spare_chip(text, element_id="spareBtn"):
    """The spare chip as SPARE_LINE_JS reads it (spec R51), the chip text and then the caret."""
    return ["button", element_id, "chip-btn", "button", "dialog", f"Spare sen: {text}. Change", [text, "svg.ic #i-caret"]]


def card_spare(count, *chips):
    return {"after": "r-check", "children": ["p", "div"], "line": ["spareLine", f"{count} sen left over"], "chips": list(chips)}


def spare_chips(page):
    """The ids of the card's spare chips in order, or None when the card has no spare line."""
    found = spare_line(page)
    return found and [chip[1] for chip in found["chips"] or []]


@pytest.mark.parametrize("seed, count, chips", [
    (seeds.S2, 2, [spare_chip("Top of the list")]),
    (seeds.ONE, 2, [spare_chip("One person, Ben")]),
    (seeds.RND, 2, [PICK_AGAIN_CHIP, spare_chip("At random")]),
    (seeds.S1, 1, [spare_chip("Top of the list")]),
    (seeds.T12, 8, [spare_chip("Top of the list")]),
], ids=["K2", "ONE", "RND", "K1", "T12"])
def test_R51_the_spare_sen_line_and_chip(open_app, seed, count, chips):
    # qa.md at 1280 x 800. The chip names the rule in effect (CG-P7). A click on Pick again is R54's (task A15).
    page = open_app(seed=seed, viewport=VIEWPORTS[1280]).page
    assert spare_line(page) == card_spare(count, *chips)


def test_R51_no_spare_sen_no_line(open_app):
    # qa.md from a cold boot at 390 x 844. RM 30.00 shared by three with no charges leaves no spare sen.
    page = open_app().page
    page.get_by_role("button", name="Add person").click()
    type_into(page, subtotal_field(page), "30.00")
    open_charges_first(page)
    support.replace_text(page, rate_field(page, "Service charge"), "0")
    support.replace_text(page, rate_field(page, "SST"), "0")
    assert card_figures(page)[1] == ["RM 10.00"] * 3 and spare_line(page) is None
    open_sheet(page)
    assert receipt(page, "#splitsDlg .rbody") is not None and spare_line(page, "#splitsDlg .rbody") is None


# P1 in one evaluate (spec R52), a part it does not hold reading as null: open and modal, its name and description by
# the ids it points at, the parts of div.in, the head, the count, each choice, the checked rule, the pickers of R53 and
# R54, where focus is, the CSSOM left and bottom, and its box [left, top, right, bottom, width, height].
P1_JS = """() => {
  const dialog = document.querySelector('#spareDlg'), inner = dialog.querySelector(':scope > div.in');
  const label = (el) => el.localName + [...el.classList].map((name) => '.' + name).join('');
  const kids = (el) => el ? [...el.children].map(label) : null;
  const head = inner?.querySelector(':scope > div.pop-head'), sub = inner?.querySelector(':scope > p.pop-sub');
  const active = document.activeElement, box = dialog.getBoundingClientRect();
  return {
    open: dialog.open, modal: dialog.matches(':modal'),
    named: document.getElementById(dialog.getAttribute('aria-labelledby'))?.textContent ?? null,
    described: document.getElementById(dialog.getAttribute('aria-describedby'))?.textContent ?? null,
    parts: kids(inner),
    head: head && [...head.children].map((el) => [label(el), el.id, el.getAttribute('type'), el.getAttribute('aria-label'),
      el.textContent, el.querySelector('use')?.getAttribute('href') ?? null]),
    sub: sub && [sub.id, sub.textContent],
    choices: [...(inner?.querySelectorAll(':scope > div.choices > label.choice') ?? [])].map((choice) => {
      const input = choice.querySelector(':scope > input');
      return [kids(choice), input?.type, input?.name, input?.value,
        choice.querySelector(':scope > span.dot')?.getAttribute('aria-hidden') ?? null, choice.textContent];
    }),
    checked: dialog.querySelector('input[name=spareRule]:checked')?.value ?? null,
    pickers: [...dialog.querySelectorAll('#pickWrap, #randWrap')].map((el) => el.id),
    focus: dialog.contains(active) && active.name === 'spareRule' ? 'radio ' + active.value
      : active.matches('#splitsDlg .r-spare-acts button[aria-haspopup]') ? "the sheet's spare chip" : active.id || active.localName,
    style: [dialog.style.getPropertyValue('left'), dialog.style.getPropertyValue('bottom')],
    box: [box.left, box.top, box.right, box.bottom, box.width, box.height],
  };
}"""


def p1_choice(value, text):
    return [["input", "span.dot", "span"], "radio", "spareRule", value, "true", text]


P1_K1 = {
    "open": True, "modal": True, "named": "Spare sen", "described": "1 sen left over",
    "parts": ["div.pop-head", "p.pop-sub", "div.choices"],
    "head": [["h2", "spareTitle", None, None, "Spare sen", None], ["button.icon-btn", "", "button", "Close", "", "#i-x"]],
    "sub": ["spareSub", "1 sen left over"],
    "choices": [p1_choice("top", "Top of the list"), p1_choice("one", "One person"), p1_choice("random", "At random")],
    "checked": "top", "pickers": [], "focus": "radio top",
}


def p1_state(page, keys=None):
    """P1_JS, or only its `keys`."""
    found = page.evaluate(P1_JS)
    return found if keys is None else {key: found[key] for key in keys}


def open_p1(page, opener):
    """Open P1 from the card's chip ("desktop") or from Splits and the sheet's chip ("phone"), and check that it opened,
    so a later step fails on this assertion and never waits for a part."""
    click_after_load(page, SPARE_OPENERS[opener])
    assert page.evaluate("() => document.querySelector('#spareDlg').open"), "P1 did not open"


def choose(page, text):
    page.locator("#spareDlg label.choice", has_text=text).click()


def near(found, expected):
    return abs(found - expected) <= 0.5


SHEET_PADDING_JS = "() => document.querySelector('#sheetScroll')?.style.getPropertyValue('padding-bottom') ?? null"


@pytest.mark.parametrize("size, opener", [((1280, 800), "desktop"), ((390, 844), "phone")], ids=["1280-card-chip", "390-sheet-chip"])
def test_R52_p1_opens_from_either_chip_with_focus_on_the_chosen_rule(open_app, size, opener):
    # qa.md on K1. Closed, P1 is the empty dialog of index.html. "Is named" and "described by" are read through the ids
    # its aria-labelledby and aria-describedby point at.
    page = open_app(seed=seeds.S1, viewport=size).page
    assert p1_state(page, ("open", "parts")) == {"open": False, "parts": None}
    open_p1(page, opener)
    assert p1_state(page, P1_K1) == P1_K1
    assert page.get_by_role("dialog", name="Spare sen", exact=True).count() == 1


def test_R52_a_choice_applies_at_once_and_p1_stays_open(open_app):
    # qa.md on K2 at 1280 x 800. Its #pickWrap lines are R53's (task A14).
    page = open_app(seed=seeds.S2, viewport=VIEWPORTS[1280]).page
    open_p1(page, "desktop")
    choose(page, "One person")
    assert p1_state(page, ("open", "checked", "pickers")) == {"open": True, "checked": "one", "pickers": ["pickWrap"]}
    assert card_figures(page)[1] == ["RM 38.88", "RM 38.86", "RM 38.86"]
    assert spare_line(page)["chips"] == [spare_chip("One person, Aisyah")]
    assert stored(page)["bill"]["spare"] == {"rule": "one", "personId": "p1"}
    choose(page, "Top of the list")
    assert p1_state(page, ("open", "checked", "pickers")) == {"open": True, "checked": "top", "pickers": []}
    assert card_figures(page)[1] == ["RM 38.87", "RM 38.87", "RM 38.86"]


def test_R52_arrow_keys_move_between_the_three_choices_and_focus_stays_on_the_radio(open_app):
    # qa.md on K2 at 1280 x 800. An arrow key fires change, which applies the rule and renders P1 again, so the render
    # must keep the focused radio. Its #pickWrap lines are R53's (task A14), its #randWrap line R54's (task A15).
    page = open_app(seed=seeds.S2, viewport=VIEWPORTS[1280]).page
    open_p1(page, "desktop")
    assert p1_state(page, ("focus",)) == {"focus": "radio top"}
    page.keyboard.press("ArrowDown")
    assert p1_state(page, ("checked", "focus", "pickers")) == {"checked": "one", "focus": "radio one", "pickers": ["pickWrap"]}
    assert picker(page, ("pills",)) == {"pills": k2_pills("Aisyah")}
    assert card_figures(page)[1] == ["RM 38.88", "RM 38.86", "RM 38.86"]
    assert spare_line(page)["chips"] == [spare_chip("One person, Aisyah")]
    page.keyboard.press("ArrowDown")
    assert p1_state(page, ("checked", "focus", "pickers")) == {"checked": "random", "focus": "radio random", "pickers": ["randWrap"]}
    assert sorted(card_figures(page)[1]) == ["RM 38.86", "RM 38.87", "RM 38.87"]
    assert spare_line(page)["chips"] == [PICK_AGAIN_CHIP, spare_chip("At random")]
    spare = stored(page)["bill"]["spare"]
    assert spare["rule"] == "random" and sorted(spare["order"]) == ["p1", "p2", "p3"], spare
    page.keyboard.press("ArrowUp")
    page.keyboard.press("ArrowUp")
    assert p1_state(page, ("checked", "focus")) == {"checked": "top", "focus": "radio top"}
    assert card_figures(page)[1] == ["RM 38.87", "RM 38.87", "RM 38.86"]
    assert spare_line(page)["chips"] == [spare_chip("Top of the list")]


# The card, the card's chip and the viewport, for P1's desktop place (spec R52).
PLACE_JS = """() => { const card = document.querySelector('#card').getBoundingClientRect();
  const chip = document.querySelector('#spareBtn')?.getBoundingClientRect();
  return { cardRight: card.right, chipBottom: chip ? chip.bottom : null, width: innerWidth,
    height: document.documentElement.clientHeight }; }"""


@pytest.mark.parametrize("seed, size, place", [
    pytest.param(seeds.S1, (1280, 800), {"left": 574, "bottom": 632.8, "width": 340}, id="K1-1280"),
    pytest.param(seeds.S2, (1280, 800), {"left": 574, "bottom": 560.8}, id="K2-1280"),
    pytest.param(seeds.ONE, (1280, 800), {"bottom": 560.8, "height": 310}, id="ONE-1280"),
    pytest.param(seeds.S1, (1024, 768), {}, id="K1-1024x768"),
])
def test_R52_p1_sits_beside_the_card_on_the_desktop(open_app, seed, size, place):
    # qa.md. Its left is the card's right edge plus 16 and its bottom is level with #spareBtn's bottom, set through the
    # CSSOM (R38). The ONE row is 310 px tall with the picker of R53 (task A14).
    page = open_app(seed=seed, viewport=size).page
    open_p1(page, "desktop")
    left, top, right, bottom, width, height = p1_state(page, ("box",))["box"]
    around = page.evaluate(PLACE_JS)
    assert near(left, around["cardRight"] + 16) and near(bottom, around["chipBottom"]), (left, bottom, around)
    assert left >= 0 and top >= 0 and right <= around["width"] and bottom <= around["height"], (left, top, right, bottom)
    for key, value in {"left": left, "bottom": bottom, "width": width, "height": height}.items():
        assert key not in place or near(value, place[key]), (key, value)
    style = p1_state(page, ("style",))["style"]
    assert all(value.endswith("px") for value in style), style
    assert near(float(style[0][:-2]), left) and near(around["height"] - float(style[1][:-2]), bottom), style


@pytest.mark.parametrize("seed, size, height, pad", [
    pytest.param(seeds.S1, (390, 844), 255, "271px", id="K1-390"),
    pytest.param(seeds.S1, (360, 780), 255, "271px", id="K1-360"),
    pytest.param(seeds.ONE, (390, 844), 309, "325px", id="ONE-390"),
    pytest.param(seeds.RND, (390, 844), 309, "325px", id="RND-390"),
])
def test_R52_on_a_phone_p1_is_a_bottom_sheet_over_the_splits_sheet_and_the_sheet_makes_room(open_app, seed, size, height, pad):
    # qa.md. The ONE and RND rows are 309 px tall with the picker of R53 and Pick again of R54 (tasks A14, A15).
    page = open_app(seed=seed, viewport=size).page
    open_p1(page, "phone")
    found = p1_state(page, ("box", "style"))
    assert near(found["box"][3], size[1]) and near(found["box"][5], height) and found["style"] == ["", ""], found
    assert page.evaluate(SHEET_PADDING_JS) == pad
    press_escape(page)
    assert page.evaluate(SHEET_PADDING_JS) == "" and sheet_state(page, ("open",)) == {"open": True}


# The sheet's scroll area, its Splits heading, its last splits row and P1's top edge (spec R52, g2's rule).
SPLITS_IN_VIEW_JS = """() => { const scroll = document.querySelector('#sheetScroll');
  const rows = scroll.querySelectorAll('ul.r-splits > li');
  return { scrollTop: scroll.scrollTop, areaTop: scroll.getBoundingClientRect().top,
    headTop: scroll.querySelector('#sheetSplitsH').getBoundingClientRect().top,
    lastRowBottom: rows[rows.length - 1].getBoundingClientRect().bottom,
    p1Top: document.querySelector('#spareDlg').getBoundingClientRect().top }; }"""


def test_R52_the_sheet_scrolls_so_the_splits_stay_in_view_above_p1(open_app):
    # qa.md on T12 at 390 x 844.
    page = open_app(seed=seeds.T12).page
    open_p1(page, "phone")
    choose(page, "One person")
    found = page.evaluate(SPLITS_IN_VIEW_JS)
    assert found["scrollTop"] > 0, found
    head_at_top = near(found["headTop"], found["areaTop"])
    assert found["lastRowBottom"] <= found["p1Top"] + 0.5 or head_at_top, found
    assert found["headTop"] >= found["areaTop"] - 0.5, found  # it never scrolls further than the heading


@pytest.mark.parametrize("size, opener, close", [
    ((1280, 800), "desktop", "close"), ((1280, 800), "desktop", "escape"), ((1280, 800), "desktop", (200, 60)),
    ((390, 844), "phone", (359, 622)), ((390, 844), "phone", (195, 30)),
    ((360, 780), "phone", (329, 558)), ((360, 780), "phone", (180, 30)),
], ids=["1280-close", "1280-escape", "1280-backdrop", "390-close", "390-backdrop", "360-close", "360-backdrop"])
def test_R52_closing_p1_returns_focus_to_the_chip_shown_at_that_moment(open_app, size, opener, close):
    # qa.md on K1. The points are docs/design/LINKS.json's, Close in P1's corner and the backdrop above it. Below 1024 px
    # the Splits sheet stays open after P1 closes.
    page = open_app(seed=seeds.S1, viewport=size).page
    open_p1(page, opener)
    if close == "close":
        button = page.locator("#spareDlg button[aria-label=Close]")
        assert button.count() == 1, "P1 holds no Close"
        button.click()
    elif close == "escape":
        press_escape(page)
    else:
        page.mouse.click(*close)
    shown_chip = "spareBtn" if opener == "desktop" else "the sheet's spare chip"
    assert p1_state(page, ("open", "focus")) == {"open": False, "focus": shown_chip}
    assert sheet_state(page, ("open",)) == {"open": opener == "phone"}


def test_R52_a_repeat_click_on_the_desktop_chip_leaves_p1_open(open_app):
    # qa.md on K1 at 1280 x 800 with a body recorder (PD-21). P1's light backdrop lies under the second click.
    page = open_app(seed=seeds.S1, viewport=VIEWPORTS[1280]).page
    chip = page.locator("#spareBtn")
    assert chip.count() == 1, "the card holds no spare chip"
    page.evaluate(RECORD_BODY_CLICKS_JS)
    gesture_at(page, "mouse-double", centre_of(chip))
    assert p1_state(page, ("open", "focus")) == {"open": True, "focus": "radio top"}
    assert_only_press_1_and_click_1_reached_the_page(page, 2)


@pytest.mark.parametrize("gesture", ["mouse-double", "touch-double"])
@pytest.mark.parametrize("size, opener, point, focus", [
    ((1280, 800), "desktop", "close", "spareBtn"), ((1280, 800), "desktop", (200, 60), "spareBtn"),
    ((390, 844), "phone", (359, 622), "the sheet's spare chip"), ((390, 844), "phone", (195, 30), "the sheet's spare chip"),
], ids=["1280-close", "1280-backdrop", "390-close", "390-backdrop"])
def test_R52_the_second_press_of_a_double_activation_that_closed_p1_never_reaches_the_page(open_app, size, opener, point, focus,
                                                                                           gesture):
    # qa.md on K1 (PD-21, F-A13-1, task A18). The points are LINKS.json's. Below 1024 px the second press would land on
    # the Splits sheet, which stays open. It passes on the tree before A18, so its teeth come from a stub of P1's click
    # close (BUILD.md, A18).
    page = open_app(seed=seeds.S1, viewport=size, touch=gesture == "touch-double").page
    noted, before = stored_text(page), snapshot(page)
    open_p1(page, opener)
    page.evaluate(RECORD_BODY_CLICKS_JS)
    gesture_at(page, gesture, centre_of(page.locator("#spareDlg button[aria-label=Close]")) if point == "close" else point)
    assert p1_state(page, ("open", "focus")) == {"open": False, "focus": focus}
    assert_only_press_1_and_click_1_reached_the_page(page, 2, tapped=gesture == "touch-double")
    assert sheet_state(page, ("open",)) == {"open": opener == "phone"} and snapshot(page) == before
    assert page.evaluate("window.testClipboardWrites") == 0 and stored_text(page) == noted


def wait_for_the_sheet_to_close(page):
    """The sheet closes itself in the media query's change event once the width reaches 1024 px (R50). At most 2 s."""
    try:
        page.wait_for_function("() => !document.querySelector('#splitsDlg').open", timeout=2000)
    except PlaywrightTimeoutError:
        pass  # gave up after 2 s, and the assertion after it names the sheet that is still open
    settle(page)


def test_R52_p1_follows_the_width_when_it_crosses_1024_px(open_app):
    # qa.md on K1 (PD-23).
    page = open_app(seed=seeds.S1).page
    open_p1(page, "phone")
    page.set_viewport_size({"width": 1280, "height": 800})
    wait_for_the_sheet_to_close(page)
    found = p1_state(page, ("open", "box"))
    assert sheet_state(page, ("open",)) == {"open": False} and found["open"] is True
    assert near(found["box"][0], 574) and near(found["box"][3], 632.8), found
    press_escape(page)
    assert p1_state(page, ("focus",)) == {"focus": "spareBtn"}


def test_R52_p1_opened_on_the_desktop_and_closed_below_1024_px(open_app):
    # qa.md on K1, CG-P8 (ruled by the owner, focus to Splits). No spare chip is shown below 1024 px while the Splits
    # sheet is closed. The style is read once a change of the media query can have run, at most 2 s.
    page = open_app(seed=seeds.S1, viewport=VIEWPORTS[1280]).page
    open_p1(page, "desktop")
    page.set_viewport_size({"width": 900, "height": 800})
    try:
        page.wait_for_function("() => document.querySelector('#spareDlg').style.getPropertyValue('left') === ''", timeout=2000)
    except PlaywrightTimeoutError:
        pass  # gave up after 2 s, and the assertion below names the style that is still there
    found = p1_state(page, ("open", "style", "box"))
    assert found["open"] is True and found["style"] == ["", ""], found
    assert near(found["box"][3], 800) and near(found["box"][4], 560), found  # a bottom sheet, 560 px wide at most
    press_escape(page)
    assert p1_state(page, ("focus",)) == {"focus": "splitsBtn"}


# The picker of R53 in one evaluate, null while P1 holds no #pickWrap. Where it sits (its tag and classes, its parent's
# class and the value of the choice before it), its parts, its legend, each pill as [tag and classes, the radio's type,
# name, value and checked, the face's nodes with an icon as "classes href"], and the text of the pill that has focus.
PICKER_JS = """() => {
  const wrap = document.querySelector('#spareDlg #pickWrap');
  if (!wrap) return null;
  const label = (el) => el.localName + [...el.classList].map((name) => '.' + name).join('');
  const legend = wrap.querySelector(':scope > legend'), list = wrap.querySelector(':scope > div.pick-list#pickList');
  const focused = wrap.contains(document.activeElement) ? document.activeElement.closest('label.pill') : null;
  return {
    place: [label(wrap), wrap.parentElement.className, wrap.previousElementSibling?.querySelector(':scope > input')?.value ?? null],
    parts: [...wrap.children].map(label),
    legend: legend && [label(legend), legend.textContent],
    pills: list && [...list.children].map((pill) => {
      const input = pill.querySelector(':scope > input'), face = pill.querySelector(':scope > span.pill-face');
      return [label(pill), input && [input.type, input.name, input.value, input.checked],
        face && [...face.childNodes].map((node) => node instanceof Element
          ? `${label(node)} ${node.querySelector('use')?.getAttribute('href')}` : node.textContent)];
    }),
    focus: focused && focused.textContent,
  };
}"""
PICKER_PARTS = ("place", "parts", "legend", "pills")


def picker(page, keys):
    """PICKER_JS with only its `keys`, or None when P1 holds no picker."""
    found = page.evaluate(PICKER_JS)
    return found and {key: found[key] for key in keys}


def pill(value, name, checked=False):
    """A pill as PICKER_JS reads it (spec R53), its radio, then the check icon and the name as a text node."""
    return ["label.pill", ["radio", "spareWho", value, checked], ["svg.ic #i-check", name]]


def picker_with(*pills):
    """PICKER_PARTS of a picker after the One person choice inside div.choices, holding `pills` (spec R53)."""
    return {"place": ["fieldset.pick", "choices", "one"], "parts": ["legend.sr", "div.pick-list"],
            "legend": ["legend.sr", "Who pays the spare sen"], "pills": list(pills)}


def k2_pills(checked=None):
    """The three pills of K2, Aisyah, Ben and Chen with values 1 to 3, the one named `checked` checked."""
    return [pill(str(value), name, name == checked) for value, name in enumerate(["Aisyah", "Ben", "Chen"], start=1)]


def click_pill(page, name):
    """Click the pill that reads `name`, counted first, so a missing pill fails here and never waits."""
    found = page.locator("#pickList label.pill", has_text=name)
    assert found.count() == 1, f"no pill reads {name}"
    found.click()


def test_R53_one_person_picks_the_first_eligible_person_at_once_and_a_pill_changes_it(open_app):
    # qa.md on K2 at 1280 x 800. The arrow key fires change on the pill, which applies the choice and renders P1 again,
    # so the render must keep the focused pill (native radios, R33).
    page = open_app(seed=seeds.S2, viewport=VIEWPORTS[1280]).page
    open_p1(page, "desktop")
    choose(page, "One person")
    assert picker(page, PICKER_PARTS) == picker_with(*k2_pills("Aisyah"))
    assert card_figures(page)[1] == ["RM 38.88", "RM 38.86", "RM 38.86"]
    assert spare_line(page)["chips"] == [spare_chip("One person, Aisyah")]
    click_pill(page, "Ben")
    assert picker(page, ("pills",)) == {"pills": k2_pills("Ben")}
    assert card_figures(page)[1] == ["RM 38.86", "RM 38.88", "RM 38.86"]
    assert spare_line(page)["chips"] == [spare_chip("One person, Ben")]
    assert stored(page)["bill"]["spare"] == {"rule": "one", "personId": "p2"}
    press_escape(page)
    page.locator("#spareBtn").click()
    assert p1_state(page, ("checked", "focus")) == {"checked": "one", "focus": "radio one"}
    page.keyboard.press("Tab")
    assert picker(page, ("focus",)) == {"focus": "Ben"}
    page.keyboard.press("ArrowRight")
    assert picker(page, ("pills", "focus")) == {"pills": k2_pills("Chen"), "focus": "Chen"}
    assert card_figures(page)[1] == ["RM 38.86", "RM 38.86", "RM 38.88"]


def test_R53_only_people_on_an_item_can_be_chosen_in_by_item(open_app):
    # qa.md on I2 at 1280 x 800 (CG-P2, ruled by the owner). A pill's value is its person's place in the people list, so
    # Ben and Chen keep 2 and 3 while Aisyah, who had nothing, has no pill.
    page = open_app(seed=seeds.I2, viewport=VIEWPORTS[1280]).page
    open_p1(page, "desktop")
    choose(page, "One person")
    assert picker(page, ("pills",)) == {"pills": [pill("2", "Ben", True), pill("3", "Chen")]}
    assert [row[:2] for row in card_rows(page)[0]] == [["Aisyah", "RM 0.00"], ["Ben", "RM 14.59"], ["Chen", "RM 2.91"]]
    click_pill(page, "Chen")
    assert card_rows(page) == [[["Aisyah", "RM 0.00", "0.00 + 0.00"], ["Ben", "RM 14.57", "12.50 + 2.07"],
                                ["Chen", "RM 2.93", "2.51 + 0.42"]], ["RM 17.50", "15.01 + 2.49"]]


def test_R53_a_chosen_person_who_has_nothing_falls_back_to_top_of_the_list_and_stays_chosen(open_app):
    # qa.md on G4 at 1280 x 800 (CG-P7 and CG-P2, ruled by the owner). The chip names the rule in effect and P1 the
    # stored choice with no pill checked, so a click on a pill applies at once.
    page = open_app(seed=seeds.ODD_READABLE["G4"], viewport=VIEWPORTS[1280]).page
    assert card_figures(page)[1] == ["RM 44.78", "RM 0.00", "RM 24.48"]
    assert spare_line(page)["chips"] == [spare_chip("Top of the list")]
    open_p1(page, "desktop")
    assert p1_state(page, ("checked", "focus")) == {"checked": "one", "focus": "radio one"}
    assert picker(page, ("pills",)) == {"pills": [pill("1", "Aisyah"), pill("3", "Chen")]}
    click_pill(page, "Chen")
    assert card_figures(page)[1] == ["RM 44.77", "RM 0.00", "RM 24.49"]
    assert spare_line(page)["chips"] == [spare_chip("One person, Chen")]
    assert stored(page)["bill"]["spare"] == {"rule": "one", "personId": "p3"}


ONE_WITH_DEVI = seeds.changed(seeds.ONE, lambda d: (d["bill"]["people"].append({"id": "p4", "name": "Devi"}),
                                                     d["bill"].update(nextId=5)))


def test_R53_removing_the_chosen_person_sets_the_rule_back_to_top_of_the_list(open_app):
    # qa.md on the ONE seed with a fourth person, Devi, at 1280 x 800 (core R12, interaction rule 8).
    page = open_app(seed=ONE_WITH_DEVI, viewport=VIEWPORTS[1280]).page
    remove = remove_button(page, "Ben")
    assert remove.count() == 1, "no Remove Ben"
    remove.click()
    assert stored(page)["bill"]["spare"] == {"rule": "top"}
    assert [row[:2] for row in card_rows(page)[0]] == [["Aisyah", "RM 38.87"], ["Chen", "RM 38.87"], ["Devi", "RM 38.86"]]
    assert spare_line(page)["chips"] == [spare_chip("Top of the list")]


# ---------------------------------------------------------------- v1.1.0 task A15: At random and Pick again (R54)
# #randWrap in one evaluate, null while P1 holds none. Where it sits (its tag and classes, its parent's class and the value
# of the choice before it), its children as [tag and classes, id, type, nodes with an icon as "classes href"], and the
# id of the control in it that has focus.
RAND_WRAP_JS = """() => {
  const wrap = document.querySelector('#spareDlg #randWrap');
  if (!wrap) return null;
  const label = (el) => el.localName + [...el.classList].map((name) => '.' + name).join('');
  return {
    place: [label(wrap), wrap.parentElement.className, wrap.previousElementSibling?.querySelector(':scope > input')?.value ?? null],
    parts: [...wrap.children].map((el) => [label(el), el.id, el.getAttribute('type'), [...el.childNodes].map((node) =>
      node instanceof Element ? `${label(node)} ${node.querySelector('use')?.getAttribute('href')}` : node.textContent)]),
    focus: wrap.contains(document.activeElement) ? document.activeElement.id : null,
  };
}"""
RAND_WRAP = {"place": ["div.pick", "choices", "random"],
             "parts": [["button.btn.btn-ghost", "pickAgainSheet", "button", ["svg.ic #i-shuffle", "Pick again"]]]}


def rand_wrap(page, keys):
    """RAND_WRAP_JS with only its `keys`, or None when P1 holds no #randWrap."""
    found = page.evaluate(RAND_WRAP_JS)
    return found and {key: found[key] for key in keys}


def cents(amount):
    """A receipt figure in sen, "RM 38.87" -> 3887."""
    return int(amount.removeprefix("RM ").replace(",", "").replace(".", ""))


def k2_draw(page):
    """The card's splits after a draw (spec R54) as [name, amount] rows, who is on RM 38.86, and their sum in sen."""
    rows = [row[:2] for row in card_rows(page)[0]]
    return {"rows": rows, "low": [name for name, amount in rows if amount == "RM 38.86"], "sum": sum(cents(amount) for _, amount in rows)}


def test_R54_at_random_gives_the_spare_sen_to_different_people_and_pick_again_draws_again(open_app):
    # qa.md on K2 at 1280 x 800. Every draw is a real one (Math.random), so the test reads who is on RM 38.86 and never
    # names them. Enter on #pickAgainSheet renders P1 again, so the render must keep the focused button (R54, R33).
    page = open_app(seed=seeds.S2, viewport=VIEWPORTS[1280]).page
    open_p1(page, "desktop")
    choose(page, "At random")
    assert rand_wrap(page, ("place", "parts")) == RAND_WRAP
    assert p1_state(page, ("pickers",)) == {"pickers": ["randWrap"]}
    first = k2_draw(page)
    assert sorted(amount for _, amount in first["rows"]) == ["RM 38.86", "RM 38.87", "RM 38.87"] and first["sum"] == 11660, first
    assert spare_line(page)["chips"] == [PICK_AGAIN_CHIP, spare_chip("At random")]
    spare = stored(page)["bill"]["spare"]
    assert set(spare) == {"rule", "order"} and spare["rule"] == "random" and sorted(spare["order"]) == ["p1", "p2", "p3"], spare
    press_escape(page)
    page.locator("#spareBtn").click()
    assert p1_state(page, ("checked", "focus")) == {"checked": "random", "focus": "radio random"}
    page.keyboard.press("Tab")
    assert rand_wrap(page, ("focus",)) == {"focus": "pickAgainSheet"}
    page.keyboard.press("Enter")
    second = k2_draw(page)
    assert len(second["low"]) == 1 and second["low"] != first["low"] and second["sum"] == 11660, (first, second)
    assert stored(page)["bill"]["spare"]["order"] != spare["order"]
    assert rand_wrap(page, ("focus",)) == {"focus": "pickAgainSheet"}
    press_escape(page)
    pick_again = page.locator("#pickAgain")
    assert pick_again.count() == 1, "the card holds no Pick again"
    pick_again.click()
    third = k2_draw(page)
    assert len(third["low"]) == 1 and third["low"] != second["low"] and third["sum"] == 11660, (second, third)
    page.reload()
    assert k2_draw(page) == third
    click_copy(page, "#copyBtn")
    lines = (page.evaluate("window.testClipboardText") or "").splitlines()
    assert lines[2:5] == [f"{name} {amount}" for name, amount in third["rows"]], lines


def test_R54_pick_again_that_can_change_nothing_does_nothing(open_app):
    # qa.md on PA0 at 1280 x 800 with the write counter (CG-P3, ruled by the owner, at most 64 draws and then no change).
    # From 1024 px the card's Pick again is the second Tab stop (R32), so the Tabs stop at 10.
    session = open_app(seed=seeds.PA0, viewport=VIEWPORTS[1280], init_scripts=[support.storage_driver("count-set")])
    page = session.page
    noted = stored_text(page)
    for _ in range(10):
        if page.evaluate("document.activeElement.id") == "pickAgain":
            break
        page.keyboard.press("Tab")
    assert page.evaluate("document.activeElement.id") == "pickAgain"  # otherwise gave up after 10 Tabs
    page.keyboard.press("Enter")
    assert [row[:2] for row in card_rows(page)[0]] == [["Aisyah", "RM 0.01"], ["Ben", "RM 0.01"], ["Chen", "RM 0.00"]]
    assert page.evaluate("window.testSetItemCalls") == 0 and stored_text(page) == noted
    assert page.evaluate("document.activeElement.id") == "pickAgain"
    assert session.problems() == []


SHEET_PICK_AGAIN = "#splitsDlg div.r-spare-acts > button.chip-btn:has(+ button.chip-btn[aria-haspopup=dialog])"


def sheet_draw(page):
    """Who is on RM 38.86 in the sheet after a draw of K2 (spec R54), and the sheet's proof figure."""
    found = receipt(page, "#splitsDlg .rbody")
    return {"low": [row[0] for row in found["list"]["rows"] if row[1] == "RM 38.86"], "proof": found["proof"]["amount"]}


def test_R54_pick_again_in_the_splits_sheet_draws_again(open_app):
    # qa.md on RND at 390 x 844 (F-A15-1, task A18). The sheet's chip comes from the card's renderer (PD-20). Focus after
    # a mouse click is each engine's own (R59), so the keyboard step Tabs until the chip has focus. It passes on the tree
    # before A18, so its teeth come from a stub that leaves the sheet's chip without its click handler (BUILD.md, A18).
    page = open_app(seed=seeds.RND).page
    open_sheet(page)
    chip = page.locator(SHEET_PICK_AGAIN)
    assert chip.count() == 1, "the sheet holds no Pick again chip before its spare chip"
    first, order = sheet_draw(page), stored(page)["bill"]["spare"]["order"]
    chip.click()
    second = sheet_draw(page)
    assert len(second["low"]) == 1 and second["low"] != first["low"] and second["proof"] == "RM 116.60", (first, second)
    assert stored(page)["bill"]["spare"]["order"] != order and sheet_state(page, ("open",)) == {"open": True}
    tab_until(page, chip, limit=10)
    page.keyboard.press("Enter")
    third = sheet_draw(page)
    assert len(third["low"]) == 1 and third["low"] != second["low"] and third["proof"] == "RM 116.60", (second, third)
    assert has_focus(chip)


# PD-19. A draw is a call of chooseSpareRule or pickAgain with no parentheses inside its argument list.
DRAW_CALL = re.compile(r"\b(chooseSpareRule|pickAgain)\(([^()]*)\)")


def draws_given_math_random(text):
    """The name of every draw call in `text` that has Math.random as one of its arguments."""
    return [call.group(1) for call in DRAW_CALL.finditer(text)
            if "Math.random" in [argument.strip() for argument in call.group(2).split(",")]]


def random_problems(sources):
    """What the R54 scan finds in {name: text}. A Math.random anywhere but as an argument of a draw call, a comment
    included, and any crypto.getRandomValues."""
    found = []
    for name, text in sources.items():
        outside = text.count("Math.random") - len(draws_given_math_random(text))
        if outside:
            found.append(f"{name}: Math.random {outside} times outside a draw")
        if "crypto.getRandomValues" in text:
            found.append(f"{name}: crypto.getRandomValues")
    return found


def test_R54_math_random_goes_only_to_the_two_draws(tmp_path):
    # qa.md (PD-19). The scan is not blind, it finds Math.random given to both draws.
    sources = {name: text for name, text in support.shipped_text().items() if name.startswith("src/")}
    assert random_problems(sources) == []
    assert sorted(name for text in sources.values() for name in draws_given_math_random(text)) == ["chooseSpareRule", "pickAgain"]
    main = sources["src/main.js"]
    planted = {"math-random": main + "\nconst r = Math.random();\n",
               "crypto": main + "\nconst bytes = crypto.getRandomValues(new Uint32Array(1));\n"}
    for name, text in planted.items():
        copy = tmp_path / f"{name}-main.js"
        copy.write_text(text, encoding="utf-8")
        assert random_problems(dict(sources, **{"src/main.js": copy.read_text(encoding="utf-8")})) != [], name


# ---------------------------------------------------------------- Task 9: the draft (R25 to R28, with R3, R8, R10, R24, R26, R42)
NEW_BILL_DRAFT = ('{"version":2,"bill":{"mode":"even","people":[{"id":"p1","name":"Person 1"},{"id":"p2","name":"Person 2"}],'
                  '"subtotalText":"","items":[],"serviceText":"10","sstText":"6","spare":{"rule":"top"},"nextId":3}}')
SNAPSHOT_JS = """() => ({
  people: [...document.querySelectorAll('li.person input')].map((i) => i.value),
  mode: document.querySelector('input[name=mode]:checked').value,
  subtotal: document.querySelector('#evenSub')?.value ?? null,
  items: [...document.querySelectorAll('li.item')].map((li) => [...li.querySelectorAll('input')].map((i) => i.value)
    .concat([...li.querySelectorAll('.tap')].map((b) => b.getAttribute('aria-pressed')))),
  rates: [document.querySelector('#svc').value, document.querySelector('#sst').value],
})"""


def stored(page):
    text = page.evaluate("localStorage.getItem('split.draft')")
    return text if text is None else json.loads(text)


def stored_text(page):
    return page.evaluate("localStorage.getItem('split.draft')")


def snapshot(page):
    return page.evaluate(SNAPSHOT_JS)


@pytest.mark.parametrize("change, check", [
    (lambda page: person_field(page, 1).fill("A"), lambda bill: bill["people"][0]["name"] == "A" and bill["spare"] == {"rule": "top"}),
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
    # [v1.1.0] A spare choice is a change too (task A13, R52).
    (lambda page: (page.get_by_role("button", name="Add person").click(), subtotal_field(page).fill("100.00"),
                   click_after_load(page, ("#splitsBtn", SHEET_SPARE_CHIP)), choose(page, "One person")),
     lambda bill: bill["spare"] == {"rule": "one", "personId": "p1"}),
], ids=["name", "add-person", "subtotal", "mode", "add-item", "sst", "remove-person", "remove-item", "spare"])
def test_R25_every_change_is_saved(open_app, change, check):
    page = open_app().page
    assert stored(page) is None
    change(page)
    draft = stored(page)
    assert list(draft) == ["version", "bill"] and draft["version"] == 2 and check(draft["bill"])


def test_R25_leaving_a_field_copying_folding_and_the_sheet_do_not_save(open_app):
    # [v1.1.0] qa.md on K2 at 390 x 844 with the write counter, which proves that nothing was written at all (task A13).
    page = open_app(seed=seeds.S2, init_scripts=[support.storage_driver("count-set")]).page
    noted = stored_text(page)
    assert noted == seeds.S2
    subtotal_field(page).click()
    page.keyboard.press("Tab")
    click_copy(page, "#stripCopy")
    page.locator("#peopleBtn").click()
    page.locator("#peopleBtn").click()
    open_sheet(page)
    press_escape(page)
    assert page.evaluate("window.testSetItemCalls") == 0 and stored_text(page) == noted


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
    assert snapshot(again) == before and split_state(again) == ITEM_SHOWN
    assert section_state(again) == [FOLDED, FOLDED]  # R26, sections fold by R48 on a reload (task A4)
    assert card_rows(again) == [S1_SPLITS, S1_PROOF]  # the card's rows since task A9
    assert [support.reads(again, "#spareLine"), support.reads(again, "#spareBtn")] == ["1 sen left over", "Top of the list"]
    switch_to(again, "Even")
    assert subtotal_field(again).input_value() == "100.00"
    assert card_figures(again)[0] == "RM 116.60"


def test_R8_both_sets_of_input_survive_a_reload(open_app):
    page = open_app().page
    subtotal_field(page).fill("100.00")
    switch_to(page, "By item")
    add_item_named(page, "Tea", "5.00", ["Person 1"])
    page.reload()
    assert split_state(page) == ITEM_SHOWN and item_name(page, 1).input_value() == "Tea"
    assert toggle(page, "Tea", "Person 1").get_attribute("aria-pressed") == "true" and card_figures(page)[0] == "RM 5.83"
    switch_to(page, "Even")
    assert subtotal_field(page).input_value() == "100.00" and card_figures(page)[0] == "RM 116.60"


def test_R26_a_drawn_order_comes_back_after_a_reload(open_app):
    # [v1.1.0] qa.md on RND (task A13).
    page = open_app(seed=seeds.RND).page
    for _ in ("load", "reload"):
        assert [row[:2] for row in receipt(page)["list"]["rows"]] == [["Aisyah", "RM 38.86"], ["Ben", "RM 38.87"], ["Chen", "RM 38.87"]]
        assert spare_chips(page) == ["pickAgain", "spareBtn"] and support.reads(page, "#spareBtn") == "At random"
        page.reload()
    assert stored(page)["bill"]["spare"] == {"rule": "random", "order": ["p2", "p3", "p1"]}


@pytest.mark.parametrize("name", ["G1", "G2", "G3", "G4", "G5", "G6", "G7"])
def test_R26_odd_but_readable_drafts_load(open_app, name):
    # [v1.1.0] G4 to G7 carry the spare choice and drafts saved by 1.0 (task A13). The chip names the rule in effect
    # (CG-P7), and one edit is enough for the next save to write version 2 (R61).
    seed = seeds.ODD_READABLE[name]
    page = open_app(seed=seed).page
    assert page.locator("div.note").count() == 0
    if name == "G2":
        assert person_field(page, 1).input_value() == seeds.FLAGS_20
    elif name == "G4":
        assert card_figures(page)[1] == ["RM 44.78", "RM 0.00", "RM 24.48"]
    else:
        assert snapshot(page) == snapshot(open_app(seed=seeds.S1 if name == "G7" else seeds.S2).page)
    if name in ("G4", "G5", "G7"):
        assert support.reads(page, "#spareBtn") == "Top of the list"
    if name == "G7":
        assert section_state(page) == [FOLDED, FOLDED]
    if name == "G3":
        assert page.evaluate("({}).polluted") is None
    if name == "G1":
        subtotal_field(page).fill("100.0")
        text = stored_text(page)
        assert "extra" not in text and "colour" not in text and json.loads(text)["bill"]["subtotalText"] == "100.0"
    if name in ("G5", "G6"):
        subtotal_field(page).fill("100.0")
        assert stored(page)["version"] == 2 and stored(page)["bill"]["spare"] == {"rule": "top"}
    if name == "G7":
        toggle(page, "Satay, 10 sticks", "Ben").click()
        assert stored(page)["version"] == 2


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
    # 1.0's "no message about storage shows" is retired by R46 and R47. No page error, console error or CSP violation is
    # checked at teardown.
    page = open_app(init_scripts=[driver]).page
    add_a_person_after_a_subtotal(page)
    total, splits = card_figures(page)
    assert total == "RM 116.60" and len(splits or []) == 3  # the card holds three splits rows (task A9)


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


def test_R47_a_change_that_writes_nothing_leaves_the_warning(open_app):
    # qa.md SW4. Pick again on PA0 can change nothing (CG-P3), so it makes no save attempt and the warning stays. A stub
    # that saves an unchanged bill fails it in both engines (BUILD.md, task A15).
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
    # The engine throws its own error through the app's own save. The card's third splits row reads "Chen Wei" (task A9).
    rows, _ = card_rows(page)
    assert notes(page) == [WARNING] and rows and rows[2][0] == "Chen Wei"
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
    assert field_error(subtotal_field(page), "evenErr") == error_state(AMOUNT_MESSAGE, "evenErr", shown=True)
    assert field_error(page.locator("#svc"), "svcErr") == error_state(SERVICE_MESSAGE, "chargeHint svcErr", shown=True)
    assert field_error(page.locator("#sst"), "sstErr") == error_state(SST_MESSAGE, "chargeHint", shown=False)


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


# dialog.modal#newDlg as R29 names it, null when the page holds none: whether it is modal, the text of the elements its
# aria-labelledby and aria-describedby point at, and each button as its id, classes and text.
NEW_DIALOG_JS = """() => { const d = document.querySelector('dialog.modal#newDlg'); if (!d) return null;
  const text = (ids) => (ids || '').split(' ').map((id) => document.getElementById(id)?.textContent ?? null).join(' ');
  return { modal: d.matches(':modal'), name: text(d.getAttribute('aria-labelledby')), description: text(d.getAttribute('aria-describedby')),
           buttons: [...d.querySelectorAll('button')].map((b) => [b.id, b.className, b.textContent]) }; }"""
NEW_DIALOG = {"modal": True, "name": "Start a new bill?", "description": "This clears the people, items and amounts.",
              "buttons": [["startNew", "btn btn-danger btn-lg", "Start new bill"], ["", "btn btn-ghost btn-lg", "Cancel"]]}


def scrolled_by_wheel(page, point, pixels):
    """How far window.scrollY moved after a mouse wheel of `pixels` at `point`, waiting at most 500 ms for a move."""
    before = page.evaluate("window.scrollY")
    page.mouse.move(*point)
    page.mouse.wheel(0, pixels)
    try:
        page.wait_for_function("(y) => window.scrollY !== y", arg=before, timeout=500)
    except PlaywrightTimeoutError:
        pass
    return page.evaluate("window.scrollY") - before


def test_R29_the_dialog_opens_with_the_safe_choice_focused(open_app):
    # [v1.1.0] qa.md over K1. The 1.0 test also read the .app height as exactly 844, which WebKit lays out at 843.984375
    # (spec R59 (1)). The scenario reads no height, so that line went with the rewrite (task A16).
    page = open_app(seed=seeds.S1).page
    # The page itself can scroll, so a wheel that leaves window.scrollY where it was shows the scroll was held.
    assert page.evaluate("document.scrollingElement.scrollHeight - innerHeight") > 0
    new_bill_button(page).click()
    assert page.evaluate(NEW_DIALOG_JS) == NEW_DIALOG
    assert page.get_by_role("dialog", name="Start a new bill?").count() == 1
    assert focused(page) == "Cancel"
    page.keyboard.press("Tab")
    assert focused(page) == "Start new bill"
    page.keyboard.press("Tab")
    assert focused(page) == "Cancel"
    page.keyboard.press("Shift+Tab")
    page.keyboard.press("Shift+Tab")
    assert focused(page) == "Cancel"
    box = page.locator("dialog#newDlg").bounding_box()
    over_the_scrim = (box["x"] + box["width"] / 2, box["y"] / 2)  # above the dialog's box
    assert scrolled_by_wheel(page, over_the_scrim, 400) == 0


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


def outside(box, point):
    """Whether `point` falls outside the bounding `box`, so a click there lands on the backdrop."""
    x, y = point
    return not (box["x"] <= x <= box["x"] + box["width"] and box["y"] <= y <= box["y"] + box["height"])


def m1_closer(page, close, by_item=None):
    """The gesture of one way out of M1 by its id, as a callable for `closing`. The backdrop is clicked at (20, 20), the
    point of LINKS.json, or at `by_item`, the centre of the By item label measured before the dialog opened."""
    return {"cancel": lambda: page.get_by_role("button", name="Cancel", exact=True).click(),
            "escape": lambda: page.keyboard.press("Escape"),
            "backdrop": lambda: page.mouse.click(20, 20),
            "backdrop-over-by-item": lambda: page.mouse.click(*by_item)}[close]


MODE_STATE_JS = "() => [document.querySelector('#modeEven')?.checked ?? null, document.activeElement?.id === 'modeItem']"


@pytest.mark.parametrize("close", ["cancel", "escape", "backdrop", "backdrop-over-by-item"])
def test_R30_leaving_the_dialog_without_starting_over(open_app, close):
    # [v1.1.0] qa.md over K2. The backdrop point is (20, 20) and the control under the backdrop is the By item half of the
    # Split switch. Each close waits for the dialog's close event before focus is read (`closing`, spec R59 (2), F-A3-1).
    page = open_app(seed=seeds.S2).page
    by_item = centre_of(page.locator("label[for=modeItem]"))
    open_dialog(page)
    box = page.locator("dialog#newDlg").bounding_box()
    assert outside(box, (20, 20)) and outside(box, by_item), "a backdrop point lies on the dialog"
    closing(page, m1_closer(page, close, by_item))
    assert dialog_is_open(page) is False
    assert focused(page) == "New bill" and stored_text(page) == seeds.S2
    assert snapshot(page) == snapshot(open_app(seed=seeds.S2).page)
    assert receipt(page)["lines"] == S2_LINES and card_rows(page) == [S2_SPLITS, S2_PROOF]  # the card since task A9
    assert page.evaluate(MODE_STATE_JS) == [True, False]  # "Even" still checked and #modeItem without focus


# The bill-empty screen of qa.md "Start over (key flow 4)", read in one evaluate, null for a part the page does not hold:
# [data-open, aria-expanded] of People and of Charges, the person names, the Split radios and blocks, the Subtotal and
# the two rates (their value property, so a folded Charges need not open), and what the card reads.
BILL_EMPTY_JS = """() => ({ people: [...document.querySelectorAll('li.person input')].map((input) => input.value),
  subtotal: document.querySelector('#evenSub')?.value ?? null,
  rates: ['#svc', '#sst'].map((s) => document.querySelector(s)?.value ?? null) })"""
BILL_EMPTY = {"sections": [["true", "true"], ["false", "false"]],  # People open, Charges folded (section_state)
              "split": EVEN_SHOWN, "people": ["Person 1", "Person 2"], "subtotal": "", "rates": ["10", "6"],
              "card": BLOCKED_CARD["subtotal"]}


def bill_empty_screen(page):
    """What the screen shows of a new bill, in the shape of BILL_EMPTY. People open and Charges folded below 1024 px."""
    return {"sections": section_state(page), "split": split_state(page), **page.evaluate(BILL_EMPTY_JS),
            "card": card_text(page)}


def test_R31_start_over(open_app):
    # [v1.1.0] qa.md "Start over (key flow 4)" from K1. The open state is reset as at load (CG-P4), the draft is version 2.
    page = open_app(seed=seeds.S1).page
    start_over(page)
    assert dialog_is_open(page) is False and focused(page) == "New bill"
    assert bill_empty_screen(page) == BILL_EMPTY
    assert stored_text(page) == NEW_BILL_DRAFT and stored(page)["bill"]["spare"] == {"rule": "top"}
    page.reload()
    assert bill_empty_screen(page) == BILL_EMPTY  # an untouched new bill opens People again (CG-P4)


def test_R31_start_over_clears_the_copy_status_and_the_spare_choice(open_app):
    # [v1.1.0] qa.md on the RND seed, whose drawn order shows the spare choice going back to Top of the list. The card of a
    # blocked bill holds no p.status (R17), the strip always holds #stripStatus (R49). "The card reads" is the whole card,
    # its bare Total and then the message (qa.md, Phrases).
    page = open_app(seed=seeds.RND).page
    click_copy(page, "#stripCopy")
    assert support.reads(page, "#stripStatus") == "Summary copied"
    start_over(page)
    assert status_lines(page)["strip"] == NO_STATUS and statuses_shown(page)["strip"] is False
    assert page.locator("#rbody p.status").count() == 0
    assert card_text(page) == BLOCKED_CARD["subtotal"] and visible_text(page, "#stripInfo") == "Enter the subtotal to see the splits."
    assert stored(page)["bill"]["spare"] == {"rule": "top"}
    subtotal_field(page).click()
    page.keyboard.type("100.00")
    assert status_lines(page)["card"] == NO_STATUS and status_lines(page)["strip"] == NO_STATUS


# Every inline error mark the page shows (R10): the ids of the p.err without hidden, how many inputs have aria-invalid
# "true" and how many div.field have is-bad.
ERROR_MARKS_JS = """() => ({ shown: [...document.querySelectorAll('p.err:not([hidden])')].map((p) => p.id),
  invalid: document.querySelectorAll('input[aria-invalid=true]').length, bad: document.querySelectorAll('div.field.is-bad').length })"""
NO_ERROR_MARKS = {"shown": [], "invalid": 0, "bad": 0}


def error_marks(page):
    return page.evaluate(ERROR_MARKS_JS)


def error_shown(error_id):
    """The error marks of one field whose error shows, with the id of its p.err."""
    return {"shown": [error_id], "invalid": 1, "bad": 1}


def add_three_items(page):
    """qa.md: click "By item" and click "Add item" 3 times. The new items get the ids i3, i4 and i5."""
    switch_to(page, "By item")
    for _ in range(3):
        page.get_by_role("button", name="Add item", exact=True).click()


START_OVER_CASES = [  # qa.md "Start over clears the error flags": seed (None for a cold boot), the field made bad, its text
    # and its error id, what is done after the start over, the field typed into then and its error id
    pytest.param(seeds.S2, subtotal_field, "0", "evenErr", None, subtotal_field, "evenErr", id="subtotal"),
    # Item 2 of K1 is i5. After the start over the third new item is i5 again, which a stale flag would mark at once.
    pytest.param(seeds.S1, lambda page: item_price(page, 2), "13.505", "ie2", add_three_items, lambda page: item_price(page, 3),
                 "ie3", id="item-price"),
    # A cold boot and Start new bill both fold Charges below 1024 px, so it is opened first each time.
    pytest.param(None, opened_rate_field("Service charge"), "31", "svcErr", open_charges_first,
                 opened_rate_field("Service charge"), "svcErr", id="service"),
    pytest.param(None, opened_rate_field("SST"), "25", "sstErr", open_charges_first, opened_rate_field("SST"), "sstErr", id="sst"),
]


@pytest.mark.parametrize("seed, bad_field, bad_text, bad_id, prepare, field_of, error_id", START_OVER_CASES)
def test_R31_start_over_clears_the_error_flags(open_app, seed, bad_field, bad_text, bad_id, prepare, field_of, error_id):
    # [v1.1.0] qa.md: the error is made on screen by typing and leaving the field, then Start new bill, then the rule is
    # seen to start again (R10 a): typing "abc" shows nothing until the field is left.
    page = open_app(seed=seed).page
    support.replace_text(page, bad_field(page), bad_text)
    page.keyboard.press("Tab")
    assert error_marks(page) == error_shown(bad_id)
    start_over(page)
    if prepare:
        prepare(page)
    assert error_marks(page) == NO_ERROR_MARKS
    field = field_of(page)
    support.replace_text(page, field, "abc")
    assert error_marks(page) == NO_ERROR_MARKS
    page.keyboard.press("Tab")
    assert error_marks(page) == error_shown(error_id) and field.get_attribute("aria-invalid") == "true"


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
# The rows of qa.md "A press below an invalid field lands on the control it started on". Since task A4 nothing sits under
# the Subtotal, and its target is the Charges header row above it, which the error does not move. It runs below 1024 px,
# where that row shows, with the mouse and with a touch tap (task A7). The price's target is a toggle of its own item,
# which its error moves down a line (task A8). The rows on p.hint#chargeHint are pressed with the mouse only. Their touch
# tap is the @per_engine scenario (test_R10_a_touch_tap_on_the_charges_hint_below_an_invalid_rate), since WebKit sends no
# mouse event and no click to text that is not a control (spec R59 (3), task A6).
AISYAH_ON_CHAR_KUEY_TEOW = lambda page: toggle(page, "Char kuey teow", "Aisyah")  # noqa: E731
RATE_PRESS_CASES = [  # (seed, field, bad text, error id, the error's text, aria-describedby hidden and shown, the target and
    # what RECORD_CLICKS_JS records of its click, how)
    pytest.param(None, subtotal_field, "0", "evenErr", AMOUNT_MESSAGE, "evenErr", "evenErr",
                 lambda page: page.locator("#chargesBtn"), "chargesBtn", "mouse", id="subtotal-mouse"),
    pytest.param(None, subtotal_field, "0", "evenErr", AMOUNT_MESSAGE, "evenErr", "evenErr",
                 lambda page: page.locator("#chargesBtn"), "chargesBtn", "touch", id="subtotal-touch"),
    pytest.param(seeds.S1, lambda page: item_price(page, 2), "13.505", "ie2", AMOUNT_MESSAGE, "ie2", "ie2",
                 AISYAH_ON_CHAR_KUEY_TEOW, "button", "mouse", id="item-price-mouse"),
    pytest.param(seeds.S1, lambda page: item_price(page, 2), "13.505", "ie2", AMOUNT_MESSAGE, "ie2", "ie2",
                 AISYAH_ON_CHAR_KUEY_TEOW, "button", "touch", id="item-price-touch"),
    pytest.param(None, opened_rate_field("Service charge"), "31", "svcErr", SERVICE_MESSAGE, "chargeHint", "chargeHint svcErr",
                 lambda page: page.locator("#chargeHint"), "chargeHint", "mouse", id="service-mouse"),
    pytest.param(None, opened_rate_field("SST"), "25", "sstErr", SST_MESSAGE, "chargeHint", "chargeHint sstErr",
                 lambda page: page.locator("#chargeHint"), "chargeHint", "mouse", id="sst-mouse"),
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


@pytest.mark.parametrize("seed, field_of, bad, error_id, message, described, shown_described, target_of, recorded, how",
                         RATE_PRESS_CASES)
def test_R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on(
        open_app, seed, field_of, bad, error_id, message, described, shown_described, target_of, recorded, how):
    page = open_app(seed=seed, touch=how == "touch").page
    field = field_of(page)
    support.replace_text(page, field, bad)
    assert field_error(field, error_id) == error_state(message, described, shown=False)  # not showing yet (CG-3)
    page.evaluate(RECORD_CLICKS_JS)
    press(page, how, centre_of(target_of(page)))
    assert page.evaluate("window.testClicks") == [recorded]
    assert field_error(field, error_id) == error_state(message, shown_described, shown=True)


# qa.md "A touch tap on the charges hint below an invalid rate" (@per_engine, spec R59 (3), the A0 measurement tap_on_hint).
# The recorder listens on window in the capture phase, the half of qa.md's "A body recorder" that sees every event first.
# Listeners on body make WebKit send a tap's mouse events to the plain text under it (BUILD.md, A17 judgment call 6, and A6),
# so the body half would change what this scenario measures.
HINT_TAP_JS = """() => { window.testHintTap = [];
  for (const type of ['mousedown', 'click']) {
    window.addEventListener(type, (event) => window.testHintTap.push(`${type}:${event.target.id || event.target.localName}`), true);
  } }"""
TAP_SETTLE_MS = 300  # the A0 measurement's own wait after the tap, so "no click came" is read after the same time


@pytest.mark.parametrize("label, bad, input_id, error_id, message, shown_described", [
    pytest.param("Service charge", "31", "svc", "svcErr", SERVICE_MESSAGE, "chargeHint svcErr", id="service"),
    pytest.param("SST", "25", "sst", "sstErr", SST_MESSAGE, "chargeHint sstErr", id="sst"),
])
def test_R10_a_touch_tap_on_the_charges_hint_below_an_invalid_rate(open_app, engine, label, bad, input_id, error_id,
                                                                   message, shown_described):
    page = open_app(touch=True).page
    field = opened_rate_field(label)(page)
    support.replace_text(page, field, bad)
    assert field_error(field, error_id) == error_state(message, "chargeHint", shown=False)  # not showing yet
    page.evaluate(HINT_TAP_JS)
    page.touchscreen.tap(*centre_of(page.locator("#chargeHint")))
    page.wait_for_timeout(TAP_SETTLE_MS)
    seen = page.evaluate("window.testHintTap")
    has_focus = page.evaluate("document.activeElement.id") == input_id
    if engine == "chromium":  # the hint gets the mouse events and a click, the field is left (R10 (a))
        assert ([event for event in seen if event.startswith("click:")], has_focus) == (["click:chargeHint"], False)
        assert field_error(field, error_id) == error_state(message, shown_described, shown=True)
    else:  # WebKit sends pointer and touch events only, the field keeps focus and is not left
        assert (seen, has_focus) == ([], True)
        assert field_error(field, error_id) == error_state(message, "chargeHint", shown=False)


@pytest.mark.parametrize("how", ["mouse", "touch"])
def test_R13_a_tap_below_an_invalid_price_toggles_that_person_and_then_shows_the_error(open_app, how):
    # [v1.1.0] The price named by its item and its error p.err#ie2 (task A8).
    page = open_app(seed=seeds.S1, touch=how == "touch").page
    price = item_price(page, 2)
    support.replace_text(page, price, "13.505")  # invalid, and its error is not flagged yet
    aisyah = AISYAH_ON_CHAR_KUEY_TEOW(page)
    assert field_error(price, "ie2") == PRICE_HIDDEN and aisyah.get_attribute("aria-pressed") == "false"
    press(page, how, centre_of(aisyah))
    assert aisyah.get_attribute("aria-pressed") == "true"
    assert sorted(stored(page)["bill"]["items"][1]["who"]) == ["p1", "p2"]
    assert field_error(price, "ie2") == PRICE_SHOWN


PRICE_HIDDEN, PRICE_SHOWN = error_state(AMOUNT_MESSAGE, "ie2", shown=False), error_state(AMOUNT_MESSAGE, "ie2", shown=True)


def test_R10_the_error_waits_for_the_mouse_button_to_come_up(open_app):
    # [v1.1.0] qa.md "The error waits for the release, and only a press holds it back", the price lines (task A8).
    page = open_app(seed=seeds.S1).page
    price = item_price(page, 2)
    support.replace_text(page, price, "13.505")
    x, y = centre_of(AISYAH_ON_CHAR_KUEY_TEOW(page))
    page.mouse.move(x, y)
    page.mouse.down()
    assert not has_focus(price)  # the field has been left ...
    assert field_error(price, "ie2") == PRICE_HIDDEN  # ... and its error waits for the release
    page.mouse.up()
    assert field_error(price, "ie2") == PRICE_SHOWN
    assert AISYAH_ON_CHAR_KUEY_TEOW(page).get_attribute("aria-pressed") == "true"


@pytest.mark.parametrize("how", ["mouse", "touch", "held"])
def test_R10_a_keyboard_blur_shows_the_error_at_once_even_after_a_press(open_app, how):
    page = open_app(seed=seeds.S1, touch=how == "touch").page
    price = item_price(page, 2)
    if how == "held":
        # A press that has not reported its end (the button is still down, as when its mouseup went to another window).
        # The key press that moves focus ends it, so the error must not wait for a release that may never come (WR-03).
        support.replace_text(page, price, "13.505")
        x, y = centre_of(price)
        page.mouse.move(x, y)
        page.mouse.down()
    else:
        press(page, how, centre_of(price))  # a finished press must not hold the next blur back
        assert has_focus(price)
        page.keyboard.press("Control+A")
        page.keyboard.type("13.505")
    page.keyboard.press("Tab")
    assert field_error(price, "ie2") == PRICE_SHOWN  # for "held", before the button comes up
    if how == "held":
        page.mouse.up()
        assert field_error(price, "ie2") == PRICE_SHOWN


SST_HIDDEN, SST_SHOWN = error_state(SST_MESSAGE, "chargeHint", shown=False), error_state(SST_MESSAGE, "chargeHint sstErr", shown=True)


def sst_holding_25(page):
    """qa.md: "SST" holding "25", with Charges opened first, the field still focused. Returns the field."""
    sst = opened_rate_field("SST")(page)
    support.replace_text(page, sst, "25")
    return sst


def test_R10_pressing_empty_space_also_waits_for_the_release(open_app):
    page = open_app().page
    sst = sst_holding_25(page)
    box = page.locator("h1.word").bounding_box()
    page.mouse.move(box["x"] + box["width"] + 40, box["y"] + box["height"] / 2)  # blank header space
    page.mouse.down()
    assert field_error(sst, "sstErr") == SST_HIDDEN
    page.mouse.up()
    assert field_error(sst, "sstErr") == SST_SHOWN


def test_R10_a_press_that_ends_runs_each_waiting_handler_once(open_app):
    # WR-03 (mutant P1: the waiting handlers are never dropped, so every later release re-runs the old ones).
    page = open_app().page
    sub = subtotal_field(page)
    sub.click()
    page.keyboard.type("abc")
    box = page.locator("h1.word").bounding_box()
    page.mouse.move(box["x"] + box["width"] + 40, box["y"] + box["height"] / 2)  # blank header space
    page.mouse.down()
    assert shown_errors(page) == []
    page.mouse.up()
    assert shown_errors(page) == ["evenErr"]  # the held-back blur ran once
    sub.click()
    page.keyboard.press("Control+A")
    page.keyboard.type("5")  # valid: the error goes
    page.keyboard.type("x")  # bad again, and the field still has focus, so no error until it is left
    assert shown_errors(page) == []
    page.mouse.click(*centre_of(sub))  # a press inside the focused field blurs nothing, so nothing may run
    assert shown_errors(page) == []


def test_R10_a_secondary_button_press_does_not_hold_the_error_back(open_app):
    # WR-03: a right click opens the context menu and on macOS and Linux the page gets no mouseup, so only the
    # primary button, the one that can produce a click, may hold a blur back.
    page = open_app().page
    sst = sst_holding_25(page)
    box = page.locator("h1.word").bounding_box()
    page.mouse.move(box["x"] + box["width"] + 40, box["y"] + box["height"] / 2)
    page.mouse.down(button="right")
    assert field_error(sst, "sstErr") == SST_SHOWN  # before any release
    page.mouse.up(button="right")


def test_R10_a_cancelled_press_releases_the_waiting_error(open_app):
    # A drag that the browser turns into a native drag ends with pointercancel and no mouseup. Playwright cannot start
    # one, so the event is dispatched on the document as the browser would (a read-only stand-in, no app hook).
    page = open_app().page
    sst = sst_holding_25(page)
    box = page.locator("h1.word").bounding_box()
    page.mouse.move(box["x"] + box["width"] + 40, box["y"] + box["height"] / 2)
    page.mouse.down()
    assert field_error(sst, "sstErr") == SST_HIDDEN
    page.evaluate("() => document.dispatchEvent(new PointerEvent('pointercancel', { bubbles: true }))")
    assert field_error(sst, "sstErr") == SST_SHOWN  # before the button comes up
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


# qa.md "The second press of a double activation that closed the dialog never reaches the page", the v1.1.0 form of the 1.0
# CR-01 tests (a double click or double tap on Cancel, the second click of a double activation, a triple click on Cancel).
# Rows: the point pressed, the size and the gesture. Cancel at four phone sizes, where the control under it is often a
# person's toggle, Start new bill, and the backdrop at (20, 20), each with a mouse double click and a touch double tap, and
# a mouse triple click on Cancel at 360 x 640.
DOUBLE_CLOSE_CASES = [
    *(pytest.param("Cancel", size, gesture, id=f"cancel-{size[0]}x{size[1]}-{gesture}")
      for size in [(360, 640), (375, 667), (412, 732), (390, 844)] for gesture in ["mouse-double", "touch-double"]),
    pytest.param("Cancel", (360, 640), "mouse-triple", id="cancel-360x640-mouse-triple"),
    *(pytest.param(target, (390, 844), gesture, id=f"{name}-390x844-{gesture}")
      for target, name in [("Start new bill", "start-new-bill"), ("backdrop", "backdrop")]
      for gesture in ["mouse-double", "touch-double"]),
]


@pytest.mark.parametrize("target, viewport, gesture", DOUBLE_CLOSE_CASES)
def test_R30_the_second_press_of_a_double_activation_that_closed_the_dialog_never_reaches_the_page(
        open_app, target, viewport, gesture):
    # The body recorder proves the cancel, so no row passes only because the layout put something harmless under the
    # second press (spec R57 (b)). For a touch row it also checks that the two taps were one double tap.
    page = open_app(seed=seeds.S1, viewport=viewport, touch=gesture == "touch-double").page
    before = snapshot(page)
    open_dialog(page)
    page.evaluate(RECORD_BODY_CLICKS_JS)
    point = (20, 20) if target == "backdrop" else centre_of(page.get_by_role("button", name=target, exact=True))
    closing(page, lambda: gesture_at(page, gesture, point))
    assert dialog_is_open(page) is False and focused(page) == "New bill"
    assert_only_press_1_and_click_1_reached_the_page(page, GESTURE_PRESSES[gesture], tapped=gesture == "touch-double")
    if target == "Start new bill":
        assert bill_empty_screen(page) == BILL_EMPTY and stored(page) == json.loads(NEW_BILL_DRAFT)
    else:
        assert snapshot(page) == before and stored_text(page) == seeds.S1


def test_R30_a_single_click_closes_as_before_and_the_next_double_click_is_not_held_back(open_app):
    page = open_app(seed=seeds.S1, viewport=PHONES[0]).page
    open_dialog(page)
    closing(page, m1_closer(page, "cancel"))  # focus comes back in the close event (F-A3-1, task A16)
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
    closing(page, lambda: page.touchscreen.tap(10, 10))  # focus comes back in the close event (F-A3-1, task A16)
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
# The v1.1.0 sizes of these outlines (qa.md). The R6 and R7 rows use them since task A5, R12 since task A8 and R29 since
# task A16, which retired the 1.0 sizes (360 x 640 in place of 360 x 780).
V11_SIZES = [(360, 780), (390, 844), (1280, 800)]
V11_SIZE_IDS = [f"{w}x{h}" for w, h in V11_SIZES]
GESTURES = ["single", "mouse-double", "mouse-triple", "touch-double"]  # "single" is the control: what one click does
ONE_ITEM = seeds.changed(seeds.S1, lambda d: d["bill"].update(items=d["bill"]["items"][3:]))
LAST_ROW_CASES = [  # (seed, the remove button, the row selector, where focus goes by R34 afterwards)
    pytest.param(seeds.S2, "Remove Chen", "li.person", "Person 2 name", id="S2-person-3-of-3"),
    pytest.param(seeds.S8, "Remove Mei Ling", "li.person", "Person 11 name", id="S8-person-12-of-12"),
    pytest.param(seeds.S1, "Remove Satay, 10 sticks", "li.item", "Item 3 name", id="S1-item-4-of-4"),
    pytest.param(ONE_ITEM, "Remove Satay, 10 sticks", "li.item", "addItem", id="S1-only-item"),  # #addItem since task A8
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
@pytest.mark.parametrize("viewport", V11_SIZES, ids=V11_SIZE_IDS)
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
# An amount that is not a number shows its error when its field is left. A blur caused by a press waits for the mouseup
# (RD-3), so the click on the toggle that was pressed is not lost, and the repeat press of a double click, triple click or
# double tap lands where the error has moved things. In 1.0 the error line pushed the chips up under their own item's
# Remove. In v1.1.0 the error is the last child of the item row (R14), so the toggles move down and no Remove moves
# (qa.md, task A8). The scout proves it: it makes the price bad, leaves the field by Tab (the error shows at once) and
# asks, for every 4 px point of every toggle of item 1 as laid out before the error, what is under it afterwards. A later
# layout that puts a Remove under such a point fails here and names it. The press goes to a point of "Aisyah" that stays
# on her toggle, on a second page whose price field still has focus, so the press itself causes the blur.
# Before the error, every 4 px point of the box of each toggle of item 1, with whether it hits that toggle (a pill's
# rounded corners do not). The toggles are kept in window.testToggles for the reading after the error.
TOGGLE_POINTS_JS = """() => {
  window.testToggles = [...document.querySelectorAll('li.item:first-child div.taps > button.tap')];
  return window.testToggles.flatMap((node, index) => { const r = node.getBoundingClientRect(), points = [];
    for (let x = r.x + 2; x < r.right - 1; x += 4) for (let y = r.y + 2; y < r.bottom - 1; y += 4) {
      points.push({ index, name: node.textContent.trim(), x, y, on: document.elementFromPoint(x, y)?.closest('button') === node });
    }
    return points; });
}"""
# The same points once the error shows: those over any Remove, and those of "Aisyah" on her toggle before and after.
UNDER_TOGGLES_JS = """(points) => {
  const overRemove = [], stillAisyah = [];
  for (const p of points) {
    const button = document.elementFromPoint(p.x, p.y)?.closest('button');
    if (button && /^Remove /.test(button.getAttribute('aria-label') || '')) overRemove.push([p.x, p.y]);
    if (p.name === 'Aisyah' && p.on && button === window.testToggles[p.index]) stillAisyah.push([p.x, p.y]);
  }
  return { overRemove, stillAisyah };
}"""


@pytest.mark.parametrize("gesture", REPEAT_GESTURES)
@pytest.mark.parametrize("width", [375, 390])
def test_R7_a_repeat_press_on_a_chip_under_a_pending_price_error_never_removes_the_item(open_app, width, gesture):
    # [v1.1.0] qa.md on K1-8 (task A8). Aisyah starts on i4, so an even number of toggles leaves her on.
    scout = open_app(seed=seeds.K1_8, viewport=(width, 3000)).page  # tall: the whole bill is in view, so the scout's points are the second page's
    points = scout.evaluate(TOGGLE_POINTS_JS)
    support.replace_text(scout, item_price(scout, 1), "abc")
    scout.keyboard.press("Tab")
    settle(scout)
    under = scout.evaluate(UNDER_TOGGLES_JS, points)
    assert under["overRemove"] == [], f"toggle points over a Remove once the error shows: {under['overRemove'][:3]}"
    assert under["stillAisyah"], "no point of the Aisyah toggle stays on it once the error shows"
    page = open_app(seed=seeds.K1_8, viewport=(width, 3000), touch=gesture == "touch-double").page
    item_price(page, 1).fill("abc")  # focus stays: the press below leaves the field
    page.evaluate(RECORD_BODY_CLICKS_JS)
    gesture_at(page, gesture, under["stillAisyah"][0])
    presses = GESTURE_PRESSES[gesture]
    assert len(seen_by_the_page(page)["clicks"]) == presses  # one click per press reached the page
    items = stored(page)["bill"]["items"]
    assert ("p1" in items[0]["who"]) == (presses % 2 == 0)  # and each one toggled Aisyah
    assert [item["id"] for item in items] == ["i4", "i5", "i6", "i7"] and shown_errors(page) == ["ie1"]


# ---------------------------------------------------------------- Security I-1: the repeat press on New bill (R29, R30)
# Opening the dialog puts its backdrop under the pointer, so the second click of a double click, triple click or double tap
# on "New bill" closed it again: the dialog flashed open and shut. Opening arms the same guard as closing does.
@pytest.mark.parametrize("gesture", ["mouse-double", "mouse-triple", "touch-double"])
@pytest.mark.parametrize("viewport", V11_SIZES, ids=V11_SIZE_IDS)
def test_R29_a_repeat_press_on_new_bill_leaves_the_dialog_open(open_app, viewport, gesture):
    # [v1.1.0] qa.md over K1 at 360 x 780, 390 x 844 and 1280 x 800, proven with the body recorder (task A16).
    page = open_app(seed=seeds.S1, viewport=viewport, touch=gesture == "touch-double").page
    page.evaluate(RECORD_BODY_CLICKS_JS)
    gesture_at(page, gesture, centre_of(new_bill_button(page)))
    assert dialog_is_open(page) is True and focused(page) == "Cancel" and stored_text(page) == seeds.S1
    assert_only_press_1_and_click_1_reached_the_page(page, GESTURE_PRESSES[gesture], tapped=gesture == "touch-double")


@pytest.mark.parametrize("close", ["cancel", "backdrop", "escape"])
def test_R30_after_a_double_click_on_new_bill_one_deliberate_click_still_closes_it(open_app, close):
    # [v1.1.0] The backdrop point is (20, 20). Each close waits for the dialog's close event before focus is read
    # (`closing`, spec R59 (2) for Escape, F-A5-1, and F-A3-1 for the clicks).
    page = open_app(seed=seeds.S1).page
    gesture_at(page, "mouse-double", centre_of(new_bill_button(page)))
    assert dialog_is_open(page) is True
    closing(page, m1_closer(page, close))
    assert dialog_is_open(page) is False and focused(page) == "New bill" and stored_text(page) == seeds.S1


def test_R29_the_keyboard_and_the_next_press_are_not_held_back(open_app):
    # [v1.1.0] qa.md over K1 with the body recorder, the v1.1.0 form of the 1.0 tests
    # test_R29_opening_by_keyboard_and_opening_again_straight_away_is_not_held_back and
    # test_R29_the_guard_of_opening_ends_at_the_next_press. A key press activates with click count 0, which no guard holds
    # back, and the guard that a click on New bill arms is gone by the next press.
    page = open_app(seed=seeds.S1).page
    page.evaluate(RECORD_BODY_CLICKS_JS)
    tab_until(page, new_bill_button(page))
    page.keyboard.press("Enter")
    assert dialog_is_open(page) is True and focused(page) == "Cancel"
    closing(page, lambda: page.keyboard.press("Enter"))
    assert dialog_is_open(page) is False and focused(page) == "New bill"
    page.keyboard.press("Enter")
    assert dialog_is_open(page) is True and focused(page) == "Cancel"
    assert seen_by_the_page(page) == {"presses": [], "clicks": [0, 0, 0]}  # the three key clicks, each count 0
    press_escape(page)
    open_dialog(page)
    press_escape(page)
    ben = toggle(page, "Nasi lemak ayam", "Ben")
    assert ben.get_attribute("aria-pressed") == "false"
    page.evaluate(RESET_RECORDER_JS)
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


# ---------------------------------------------------------------- v1.1.0 task A18: cross-cutting checks in both engines
# R32, R35, R36, R37, R55 and R60 in the v1.1.0 forms of qa.md. The 1.0 forms read the 1.0 markup and were marked for A18.
# Tests that check several lines of one scenario gather what is wrong into one list and assert it empty, so one failing
# run names every line that broke.

# The accessible name of a control from the four sources the app's controls use, in accname's order, aria-labelledby,
# aria-label, the input's own label, then its text. qa.md names every Tab stop by it (R32).
ACCESSIBLE_NAME_JS = """(el) => { const text = (node) => (node ? node.textContent : '').replace(/\\s+/g, ' ').trim();
  const by = el.getAttribute('aria-labelledby');
  if (by) return by.split(/\\s+/).map((id) => text(document.getElementById(id))).join(' ');
  if (el.hasAttribute('aria-label')) return el.getAttribute('aria-label');
  if (el.labels && el.labels.length) return text(el.labels[0]);
  return text(el); }"""
FOCUSED_NAME_JS = "() => (" + ACCESSIBLE_NAME_JS + ")(document.activeElement)"
# How many controls Tab can reach in `scope`, a dialog's selector, or in the page outside the dialogs when it is null.
# Enabled, displayed, not taken out by a negative tabindex, and of a radio group the checked radio only.
TABBABLE_COUNT_JS = """(scope) => [...(scope ? document.querySelector(scope) : document).querySelectorAll('button, input, [tabindex]')]
  .filter((el) => el.tabIndex >= 0 && !el.disabled && el.checkVisibility() && (el.type !== 'radio' || el.checked)
    && (scope || !el.closest('dialog'))).length"""
K1_ITEM_STOPS = [stop for number, (name, _, _) in enumerate(S1_ITEMS, start=1)
                 for stop in (f"Item {number} name", f"{name} price in RM", f"Remove {name}", "Aisyah", "Ben", "Chen")]
EMPTY_STOPS = ["New bill", "People", "Add person", "Person 1 name", "Person 2 name", "Charges", "Even", "Subtotal in RM", "Splits"]
TAB_SCOPES = {"page": None, "sheet": "#splitsDlg", "p1": "#spareDlg"}
TAB_ORDER_CASES = [  # qa.md "Tab order follows the golden", the seed, the width, where Tab starts, the order of the names
    pytest.param(seeds.S1, 390, "page", ["New bill", "People", "Charges", "By item", "Add item", *K1_ITEM_STOPS, "Splits",
                                         "Copy summary"], id="K1-390"),
    pytest.param(None, 390, "page", EMPTY_STOPS, id="bill-empty-390"),
    pytest.param(seeds.UNREADABLE["B1"], 390, "page", ["Dismiss note", *EMPTY_STOPS], id="B1-390"),
    pytest.param(seeds.S1, 1280, "page", ["New bill", "Spare sen: Top of the list. Change", "Copy summary", "Add person",
                                          "Person 1 name", "Remove Aisyah", "Person 2 name", "Remove Ben", "Person 3 name",
                                          "Remove Chen", "Service charge", "SST", "By item", "Add item", *K1_ITEM_STOPS],
                 id="K1-1280"),
    pytest.param(seeds.S1, 390, "sheet", ["Close", "Spare sen: Top of the list. Change", "Copy summary"], id="K1-sheet-390"),
    pytest.param(seeds.RND, 390, "sheet", ["Close", "Pick again", "Spare sen: At random. Change", "Copy summary"],
                 id="RND-sheet-390"),
    pytest.param(seeds.S1, 1280, "p1", ["Close", "Top of the list"], id="K1-P1-1280"),
    pytest.param(seeds.ONE, 1280, "p1", ["Close", "One person", "Ben"], id="ONE-P1-1280"),
    pytest.param(seeds.RND, 1280, "p1", ["Close", "At random", "Pick again"], id="RND-P1-1280"),
]


@pytest.mark.parametrize("seed, width, start, order", TAB_ORDER_CASES)
def test_R32_tab_order_follows_the_golden(open_app, seed, width, start, order):
    # qa.md. From the top of the page the first Tab leaves body. The sheet has focus on open, and P1 opens with focus on
    # the checked choice, so its Close is reached by Shift+Tab. Neither wraps Tab (Non-goals), so the walk stops at the
    # last name, and the count of controls Tab can reach in the same scope shows that none is left out.
    page = open_app(seed=seed, viewport=VIEWPORTS[width]).page
    if start == "sheet":
        open_sheet(page)
    elif start == "p1":
        open_p1(page, "desktop")
        page.keyboard.press("Shift+Tab")
    stops = [page.evaluate(FOCUSED_NAME_JS)] if start == "p1" else []
    while len(stops) < len(order):
        page.keyboard.press("Tab")
        stops.append(page.evaluate(FOCUSED_NAME_JS))
    assert stops == order
    assert page.evaluate(TABBABLE_COUNT_JS, TAB_SCOPES[start]) == len(order)


FOCUS_RING = "rgb(163, 170, 255)"  # --focus, system.md Focus
# Where a focused control draws its ring (system.md Focus). An input on its div.field or li.field wrapper, a half of the
# Split switch on its label, a header row as the border of its ::after (left and right -8px, 8 px wider than the row on
# each side), anything else on itself. `edge` is the holder's box-shadow, the red edge of an error field.
RING_JS = """(el) => {
  const visible = el.matches(':focus-visible');
  if (el.matches('.sec-btn')) {
    const after = getComputedStyle(el, '::after');
    return { on: 'button.sec-btn::after', visible, ring: [after.borderTopStyle, after.borderTopWidth, after.borderTopColor, after.left, after.right] };
  }
  const holder = el.localName === 'input' && el.closest('.field') ? el.closest('.field') : el.matches('.mode-sw input') ? el.nextElementSibling : el;
  const s = getComputedStyle(holder);
  return { on: holder.localName + [...holder.classList].map((name) => '.' + name).join(''), visible,
           ring: [s.outlineStyle, s.outlineWidth, s.outlineColor, s.outlineOffset], edge: s.boxShadow };
}"""


def ring(offset, *more):
    return ["solid", "2px", FOCUS_RING, offset, *more]


# qa.md "Every focused control shows the one ring", each control, its selector in the app and in the golden, and its ring.
# The header row and Splits are not displayed from 1024 px, and Copy summary is the card's there.
RING_TARGETS = {
    "a name field": ("input[aria-label='Person 1 name']", ring("2px")),
    "a person's Remove": ("button[aria-label='Remove Aisyah']", ring("-3px")),
    "the checked half of the Split switch": ("#modeItem", ring("-5px")),
    "a header row": ("#peopleBtn", ["solid", "2px", FOCUS_RING, "-8px", "-8px"]),
    "a toggle": ("div[aria-label='Who had Nasi lemak ayam'] button.tap", ring("2px")),
    "an item's Remove": ("button[aria-label='Remove Nasi lemak ayam']", ring("2px")),
    "Splits": ("#splitsBtn", ring("2px")),
    "Copy summary": ("#stripCopy", ring("2px")),
}
DESKTOP_RING_TARGETS = {**{what: target for what, target in RING_TARGETS.items() if what not in ("a header row", "Splits")},
                        "Copy summary": ("#copyBtn", ring("2px"))}


def ring_by_tab(page, selector):
    """RING_JS on the first match of `selector`, focused by Tab from New bill (so it is :focus-visible), at most 80 presses."""
    control = page.locator(selector).first
    page.locator("#newBill").focus()
    tab_until(page, control, limit=80)
    return control.evaluate(RING_JS)


@pytest.mark.parametrize("width, golden", [(390, "bill-items-open"), (1280, "bill-items")], ids=["390", "1280"])
def test_R32_every_focused_control_shows_the_one_ring(open_app, plain_context, width, golden):
    # qa.md on K1, below 1024 px with People and Charges opened by keyboard (Enter on each header row). Each ring is
    # compared with the golden's on the same control focused by Tab, and with the numbers of system.md Focus.
    page = open_app(seed=seeds.S1, viewport=VIEWPORTS[width]).page
    if width < 1024:
        for header in ("#peopleBtn", "#chargesBtn"):
            page.locator(header).focus()
            page.keyboard.press("Enter")
    golden_page = support.open_golden(plain_context, golden, VIEWPORTS[width])
    problems = []
    for what, (selector, expected) in (RING_TARGETS if width < 1024 else DESKTOP_RING_TARGETS).items():
        found, drawn = ring_by_tab(page, selector), ring_by_tab(golden_page, selector)
        if not found["visible"] or found["ring"] != expected or [found["on"], found["ring"]] != [drawn["on"], drawn["ring"]]:
            problems.append(f"{what}: app {found}, golden {drawn}")
    assert not problems, " | ".join(problems)


def test_R32_an_error_field_keeps_its_red_edge_and_gains_the_ring(open_app, plain_context):
    # qa.md, the RE line of "Every focused control shows the one ring", at 390 x 844, where Charges is open on load.
    page = open_app(seed=seeds.RE).page
    edge = page.locator("#svc").evaluate("(el) => getComputedStyle(el.closest('.field')).boxShadow")
    found = ring_by_tab(page, "#svc")
    drawn = ring_by_tab(support.open_golden(plain_context, "rate-error"), "#svc")
    assert edge != "none" and found["edge"] == edge, (edge, found)
    assert found["visible"] and found["ring"] == ring("2px") and found == drawn, (found, drawn)


@pytest.mark.parametrize("seed, field_of, text", [
    (seeds.S2, subtotal_field, "100.00"),
    (seeds.S1, opened_rate_field("Service charge"), "12.5"),
], ids=["subtotal", "service-charge"])
def test_R33_typing_in_an_amount_or_a_rate_keeps_focus_and_caret(open_app, seed, field_of, text):
    page = open_app(seed=seed).page
    type_and_watch(page, field_of(page), text)


# qa.md "No horizontal overflow in any golden state", the page's overflow, every displayed element whose right edge is past
# the viewport's (the first 8 named), the People grid's columns where it is displayed, the tops of the blocks top bar,
# People, Charges, Split, then Items or Subtotal (null when not displayed), and the strip's position with the gap under it.
LAYOUT_JS = """() => {
  const shown = (el) => !!el && el.checkVisibility();
  const name = (el) => el.localName + (el.id ? '#' + el.id : '') + [...el.classList].map((c) => '.' + c).join('');
  const wide = [...document.body.querySelectorAll('*')].filter((el) => shown(el) && el.getBoundingClientRect().right > innerWidth + 0.5)
    .map((el) => name(el) + ' ' + el.getBoundingClientRect().right);
  const list = document.querySelector('#peopleList'), strip = document.querySelector('#strip');
  return {
    overflow: document.documentElement.scrollWidth - innerWidth, wide: wide.slice(0, 8), wideCount: wide.length,
    columns: shown(list) ? getComputedStyle(list).gridTemplateColumns.split(' ').length : null,
    tops: ['header.top', '#peopleBlk', '#chargesBlk', '#splitBlk', '#itemsBlock, #evenBlock'].map((selector) => {
      const el = document.querySelector(selector); return shown(el) ? el.getBoundingClientRect().top : null; }),
    strip: shown(strip) ? [getComputedStyle(strip).position, innerHeight - strip.getBoundingClientRect().bottom] : null,
  };
}"""
R35_PAIRS = [pytest.param(golden, width, id=f"{golden}-{width}") for golden, (_, _, widths) in R3_STATES.items() for width in widths]


def layout_problems(found, width):
    """What breaks qa.md's lines of R35 in LAYOUT_JS's `found` at `width`, as one list of sentences."""
    problems = [f"the page is {found['overflow']} px wider than the viewport"] if found["overflow"] > 0 else []
    if found["wideCount"]:
        problems.append(f"{found['wideCount']} displayed elements end past the viewport's right edge, {found['wide']}")
    if found["columns"] is not None and found["columns"] != (3 if width >= 1024 else 2):
        problems.append(f"People's list has {found['columns']} columns")
    if width < 1024:
        tops = found["tops"]
        if None in tops or any(upper >= lower for upper, lower in zip(tops, tops[1:])):
            problems.append(f"the tops of the top bar, People, Charges, Split and Items or Subtotal are {tops}")
        if found["strip"] is None or found["strip"][0] != "fixed" or abs(found["strip"][1]) > 0.5:
            problems.append(f"the strip is {found['strip']}, not fixed at the bottom of the viewport")
    return problems


@pytest.mark.parametrize("golden, width", R35_PAIRS)
def test_R35_no_horizontal_overflow_in_any_golden_state(open_app, golden, width):
    # qa.md, each golden's state reached as in the R3 outline (R3_STATES) at each width of its row.
    seed, after_load, _ = R3_STATES[golden]
    page = open_app(seed=seed, viewport=VIEWPORTS[width]).page
    click_after_load(page, after_load.get("desktop" if width >= 1024 else "phone", ()))
    problems = layout_problems(page.evaluate(LAYOUT_JS), width)
    assert not problems, " | ".join(problems)


def test_R35_layout_problems_has_teeth():
    good = {"overflow": 0, "wide": [], "wideCount": 0, "columns": 2, "tops": [0, 60, 120, 180, 240], "strip": ["fixed", 0]}
    assert layout_problems(good, 390) == [] and layout_problems(dict(good, columns=3, strip=None, tops=[0, 64, 64, 64, None]), 1280) == []
    for broken in ({"overflow": 1}, {"wideCount": 1, "wide": ["div 391"]}, {"columns": 1}, {"tops": [0, 120, 60, 180, 240]},
                   {"tops": [0, 60, 120, 180, None]}, {"strip": ["static", 0]}, {"strip": ["fixed", 12]}):
        assert layout_problems({**good, **broken}, 390), broken


def box_of(page, selector):
    return page.locator(selector).evaluate("(el) => { const b = el.getBoundingClientRect(); return [b.x, b.y, b.width, b.height]; }")


def close_to(found, expected):
    """Every number of `found` within 0.5 px of `expected`'s (qa.md, a measured number matches within 0.5 px)."""
    return len(found) == len(expected) and all(abs(a - b) <= 0.5 for a, b in zip(found, expected))


def test_R35_sizes_the_design_gives_at_360_by_780(open_app, plain_context):
    # The 1.0 sizes at 360 x 780 are FE element checklist rows since v1.1.0 (qa.md, the R35 outline's note). K2-06, the
    # Subtotal field at most 240 px wide, as wide as the golden's. The refused copy status on the strip stays inside the
    # viewport with nothing cut (the ST-08 line, whose 153 px strip is the R49 strip test's at 390). M1-02, the dialog
    # 328 px wide with its top at 261.
    page = open_app(seed=seeds.S2, clipboard="reject", viewport=VIEWPORTS[360]).page
    golden = support.open_golden(plain_context, "bill-even", VIEWPORTS[360])
    problems = []
    field, drawn = box_of(page, "#evenField"), box_of(golden, "#evenField")
    if not page.locator("#evenField").evaluate("(el) => el.matches('div.field.money.sub-field')") or field[2] > 240.5 \
            or not close_to(field, drawn):
        problems.append(f"the Subtotal field is {field}, the golden's {drawn}")
    click_copy(page, "#stripCopy")
    shape = page.locator("#stripStatus").evaluate("(el) => [el.className, el.textContent.trim().length > 0, el.scrollWidth <= el.clientWidth]")
    x, _, width, _ = box_of(page, "#stripStatus")
    overflow = page.evaluate(LAYOUT_JS)["overflow"]
    if shape != ["status is-fail", True, True] or x < 0 or x + width > 360.5 or overflow > 0:
        problems.append(f"the refused status is {shape} from x {x} to {x + width}, the page overflows by {overflow} px")
    open_dialog(page)
    dialog, overflow = box_of(page, "#newDlg"), page.evaluate(LAYOUT_JS)["overflow"]
    if not close_to([dialog[2], dialog[1]], [328, 261]) or overflow > 0:
        problems.append(f"the dialog is {dialog}, the page overflows by {overflow} px")
    assert not problems, " | ".join(problems)


def test_R35_content_width_of_the_header_and_the_note_at_1280_by_800(open_app, plain_context):
    # The 1.0 widths of the header and the note at 1280 x 800 are FE element checklist rows since v1.1.0. K1-01, the top
    # bar 64 px tall with 48 px sides. BR-02, the note centred in the top bar between the brand and New bill, 44 px tall
    # with no padding at the top or the bottom, where the golden draws it. Its 44 px is the height inside its 1 px
    # border (clientHeight), the golden's border box being 46.
    page = open_app(seed=seeds.UNREADABLE["B1"], viewport=VIEWPORTS[1280]).page
    golden = support.open_golden(plain_context, "bill-unreadable", VIEWPORTS[1280])
    problems = []
    bar = page.locator("header.top").evaluate("""(el) => { const s = getComputedStyle(el);
      return [el.getBoundingClientRect().height, parseFloat(s.paddingLeft), parseFloat(s.paddingRight)]; }""")
    if not close_to(bar, [64, 48, 48]):  # WebKit computes the sides as 48.000008px (spec R59 (1))
        problems.append(f"the top bar's height and sides are {bar}")
    note, brand, new_bill = box_of(page, "div.note"), box_of(page, "div.brand"), box_of(page, "#newBill")
    inside = page.locator("div.note").evaluate("""(el) => { const s = getComputedStyle(el);
      return [el.clientHeight, s.paddingTop, s.paddingBottom]; }""")
    if not close_to(note, box_of(golden, "div.note")) or inside != [44, "0px", "0px"]:
        problems.append(f"the note is {note} with {inside}, the golden's {box_of(golden, 'div.note')}")
    if not brand[0] + brand[2] <= note[0] or not note[0] + note[2] <= new_bill[0]:
        problems.append(f"the note {note} is not between the brand {brand} and New bill {new_bill}")
    assert not problems, " | ".join(problems)


TRANSITION_CLASSES = [".btn", ".chip-btn", ".tap", ".icon-btn", ".mode-sw label"]
# Every value of the computed transition-duration of every element each selector matches, as [selector, values].
DURATIONS_JS = """(selectors) => selectors.map((selector) => [selector, [...document.querySelectorAll(selector)]
  .flatMap((el) => getComputedStyle(el).transitionDuration.split(', '))])"""
# document.getAnimations() as [kind, playState, target as tag#id.classes, duration in ms].
ANIMATIONS_JS = """() => document.getAnimations().map((a) => { const t = a.effect && a.effect.target;
  return [a.constructor.name, a.playState, t ? t.localName + '#' + t.id + [...t.classList].map((c) => '.' + c).join('') : null,
          a.effect ? a.effect.getTiming().duration : null]; })"""


def test_R36_reduced_motion_moves_nothing(open_app):
    # qa.md on K1 at 390 x 844 under "reduce", the default context. "Right after" is read as soon as the click returns.
    page = open_app(seed=seeds.S1).page
    problems = []

    def no_durations(target, selectors):
        problems.extend(f"{selector} transition-duration {sorted(set(values))}"
                        for selector, values in target.evaluate(DURATIONS_JS, selectors) if not values or set(values) != {"0s"})

    def no_animations(when):
        found = page.evaluate(ANIMATIONS_JS)
        if found:
            problems.append(f"getAnimations() {when}: {found}")

    no_durations(page, TRANSITION_CLASSES)
    no_animations("right after load")
    toggle(page, "Mee goreng mamak", "Ben").click()
    no_animations("right after a toggle click")
    page.locator("#peopleBtn").click()
    no_animations("right after #peopleBtn opened People")
    open_sheet(page)
    no_animations("right after Splits opened the sheet")
    page.locator(SHEET_SPARE_CHIP).click()
    no_animations("right after the chip opened P1")
    over_one = open_app(seed=seeds.ONE).page
    open_p1(over_one, "phone")
    no_durations(over_one, [".choice", ".pill-face"])
    assert not problems, " | ".join(problems)


def test_R36_with_motion_allowed_nothing_loops(open_app):
    # qa.md on K1 under "no-preference" (spec R36 as worded 2026-10-15, F-A4-1, no animation is running). The resize to
    # 390 shows the strip, which starts its foil sweep, so 3 s pass before the click on #peopleBtn.
    page = open_app(seed=seeds.S1, viewport=VIEWPORTS[1280], reduced_motion="no-preference").page
    problems = []

    def nothing_running(when):
        found = [animation for animation in page.evaluate(ANIMATIONS_JS) if animation[1] == "running"]
        if found:
            problems.append(f"running {when}: {found}")

    at_load = page.evaluate(ANIMATIONS_JS)
    if not any(kind == "CSSAnimation" for kind, *_ in at_load):
        problems.append(f"no CSSAnimation right after load: {at_load}")
    page.wait_for_timeout(3000)
    nothing_running("3 s after load")
    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_timeout(3000)
    page.locator("#peopleBtn").click()
    reveal = [animation for animation in page.evaluate(ANIMATIONS_JS) if animation[0] not in ("CSSAnimation", "CSSTransition")]
    if [animation[2:] for animation in reveal] != [["div#peopleBody.sec-body", 200]]:
        problems.append(f"right after the click on #peopleBtn the animations besides CSS ones are {reveal}")
    if page.locator("#peopleBody").get_attribute("style") is not None:
        problems.append("#peopleBody has a style attribute")
    page.wait_for_timeout(1000)
    nothing_running("1 s after the click on #peopleBtn")
    if any(animation[0] not in ("CSSAnimation", "CSSTransition") for animation in page.evaluate(ANIMATIONS_JS)):
        problems.append("the reveal is still in getAnimations() 1 s after the click")
    for name, gesture in [("a toggle click", lambda: toggle(page, "Mee goreng mamak", "Ben").click()),
                          ("the click on Splits", lambda: open_sheet(page)),
                          ("the click on the sheet's spare chip", lambda: page.locator(SHEET_SPARE_CHIP).click()),
                          ("Escape", lambda: press_escape(page)), ("Escape again", lambda: press_escape(page))]:
        gesture()
        page.wait_for_timeout(1000)
        nothing_running(f"1 s after {name}")
    assert not problems, " | ".join(problems)


PERSON_PAYLOAD, ITEM_PAYLOAD, SCRIPT_PAYLOAD = "<svg onload=f()>", "<img src=x onerror=alert(1)>", '"><script>alert(2)</script>'
# What markup a payload could have made, img and script elements under body, elements with an onload or onerror
# attribute, and every svg under body, as its class, or as "other" when it is none of svg.sprite, .mark, .ic or .seal.
MARKUP_JS = """() => ({ markup: document.body.querySelectorAll('img, script').length,
  handlers: document.querySelectorAll('[onload], [onerror]').length,
  svgs: [...document.body.querySelectorAll('svg')].map((svg) =>
    svg.matches('svg.sprite, svg.mark, svg.ic, svg.seal') ? svg.getAttribute('class') : 'other') })"""


def test_R37_names_are_shown_as_text_and_never_as_markup(open_app):
    # qa.md on K1 at 390 x 844 with People opened first. The card is not displayed below 1024 px but is in the DOM, so its
    # first splits row is read there. CG-9 of 1.0 stands.
    session = open_app(seed=seeds.S1)
    page = session.page
    dialogs = []
    page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.dismiss()))
    open_people_first(page)
    svgs_before = len(page.evaluate(MARKUP_JS)["svgs"])
    support.replace_text(page, person_field(page, 1), PERSON_PAYLOAD)
    support.replace_text(page, item_name(page, 1), ITEM_PAYLOAD)
    support.replace_text(page, item_name(page, 2), SCRIPT_PAYLOAD)
    problems = []

    def expect(what, found, wanted):
        if found != wanted:
            problems.append(f"{what}: {found!r}, not {wanted!r}")

    expect("Person 1 name", person_field(page, 1).input_value(), PERSON_PAYLOAD)
    expect("Item 1 name", item_name(page, 1).input_value(), ITEM_PAYLOAD)
    expect("the payload lengths", [len(PERSON_PAYLOAD), len(ITEM_PAYLOAD)], [16, 28])
    expect("that person's toggles", page.locator("button.tap").evaluate_all(
        f"(taps) => taps.filter((tap) => tap.textContent === {json.dumps(PERSON_PAYLOAD)}).length"), 4)
    expect("the card's first splits row", page.evaluate("document.querySelector('#splits li .nm')?.textContent ?? null"), PERSON_PAYLOAD)
    expect("that person's Remove", remove_button(page, PERSON_PAYLOAD).count(), 1)
    expect("item 1's Remove", page.get_by_role("button", name=f"Remove {ITEM_PAYLOAD}", exact=True).count(), 1)
    expect("item 1's price", page.get_by_label(f"{ITEM_PAYLOAD} price in RM", exact=True).count(), 1)
    expect("item 1's group", who_group(page, ITEM_PAYLOAD).count(), 1)
    page.locator("#peopleBtn").click()  # folds People
    summary = page.evaluate("document.querySelector('#peopleBlk span.sec-txt')?.textContent ?? ''")
    if not summary.startswith(PERSON_PAYLOAD):
        problems.append(f"the People summary reads {summary!r}")
    found = page.evaluate(MARKUP_JS)
    expect("img and script elements, onload and onerror attributes", [found["markup"], found["handlers"]], [0, 0])
    expect("the number of svg elements", len(found["svgs"]), svgs_before)
    expect("svg elements that are none of svg.sprite, .mark, .ic or .seal", found["svgs"].count("other"), 0)
    expect("dialog events and page errors", [dialogs, session.page_errors], [[], []])
    open_sheet(page)
    page.locator(SHEET_SPARE_CHIP).click()
    choose(page, "One person")
    face = page.evaluate("""() => { const face = document.querySelector('#pickList label.pill span.pill-face');
      return face && [face.querySelectorAll(':scope > svg.ic').length, face.children.length,
                      [...face.childNodes].filter((node) => node.nodeType === Node.TEXT_NODE).map((node) => node.data)]; }""")
    expect("the first pill's face (svg.ic, children, text nodes)", face, [1, 1, [PERSON_PAYLOAD]])
    press_escape(page)
    press_escape(page)
    click_copy(page, "#stripCopy")
    expect("line 3 of the clipboard text", (page.evaluate("window.testClipboardText") or "").split("\n")[2:3], [f"{PERSON_PAYLOAD} RM 29.04"])
    assert not problems, " | ".join(problems)


# qa.md "The desktop layout at 1280 and at 1024", the top bar's height, the two regions with their names and boxes, the
# card and the chip, and whether the strip, the header rows, the bodies and the desktop headings are displayed.
DESKTOP_JS = """() => {
  const box = (selector) => { const el = document.querySelector(selector); if (!el) return null;
    const b = el.getBoundingClientRect(); return [b.x, b.y, b.width, b.height]; };
  const shown = (selector) => { const el = document.querySelector(selector); return !!el && el.checkVisibility(); };
  return {
    top: document.querySelector('header.top').getBoundingClientRect().height,
    names: [document.querySelector('section.stage#stage')?.getAttribute('aria-label') ?? null,
            document.querySelector('section.work#work')?.getAttribute('aria-label') ?? null],
    stage: box('#stage'), work: box('#work'), card: box('#card'), chip: box('#spareBtn'),
    shown: Object.fromEntries(['#stage', '#work', '#strip', '#peopleBtn', '#chargesBtn', '#peopleBody', '#chargesBody',
                               'h2#peopleH', 'h2#chargesH'].map((selector) => [selector, shown(selector)])),
  };
}"""


def test_R55_the_desktop_layout_at_1280_and_at_1024(open_app):
    # qa.md on K1. "Side by side" is the stage's right edge at or left of the working's left edge, with their boxes
    # sharing rows of the page.
    page = open_app(seed=seeds.S1, viewport=VIEWPORTS[1280]).page
    found = page.evaluate(DESKTOP_JS)
    problems = []
    stage, work = found["stage"], found["work"]
    if abs(found["top"] - 64) > 0.5:
        problems.append(f"header.top is {found['top']} px tall")
    if found["names"] != ["Bill and splits", "Edit the bill"]:
        problems.append(f"the regions are named {found['names']}")
    if not (stage[0] + stage[2] <= work[0] + 0.5 and stage[1] < work[1] + work[3] and work[1] < stage[1] + stage[3]):
        problems.append(f"the stage {stage} and the working {work} are not side by side")
    if not close_to(found["card"], [98, 84, 460, 642]) or not close_to(found["chip"], [392, 589, 141, 44]):
        problems.append(f"the card is {found['card']} and #spareBtn {found['chip']}")
    shown = found["shown"]
    wanted = {"#stage": True, "#work": True, "#strip": False, "#peopleBtn": False, "#chargesBtn": False, "#peopleBody": True,
              "#chargesBody": True, "h2#peopleH": True, "h2#chargesH": True}
    if shown != wanted:
        problems.append(f"displayed {[s for s in wanted if shown[s] != wanted[s]]} the other way round, at 1280 x 800")
    page.set_viewport_size({"width": 1024, "height": 768})
    found = page.evaluate(DESKTOP_JS)
    if not found["card"][0] + found["card"][2] < found["work"][0] or found["shown"]["#strip"]:
        problems.append(f"at 1024 x 768 the card is {found['card']}, the working {found['work']}, the strip shown {found['shown']['#strip']}")
    assert not problems, " | ".join(problems)


R55_GOLDENS = [golden for golden, (_, _, widths) in R3_STATES.items() if 1280 in widths]


@pytest.mark.parametrize("golden", R55_GOLDENS)
def test_R55_the_page_never_scrolls_at_1280_by_800(open_app, golden):
    # qa.md, each golden's state reached as in the R3 outline at 1280 x 800.
    seed, after_load, _ = R3_STATES[golden]
    page = open_app(seed=seed, viewport=VIEWPORTS[1280]).page
    click_after_load(page, after_load.get("desktop", ()))
    height = page.evaluate("[document.documentElement.scrollHeight, innerHeight]")
    assert height[0] <= height[1], f"the page is {height[0]} px tall in a {height[1]} px viewport"


# The money figures R60 names that are wider than their box, among those in `root`, and how many of each it holds.
FIGURES_JS = """(root) => { const scope = document.querySelector(root), found = {}, wide = [];
  for (const selector of ['.r-amount', '.amt', '.r-lines dd', '.wk']) {
    const figures = [...scope.querySelectorAll(selector)];
    found[selector] = figures.length;
    wide.push(...figures.filter((el) => el.scrollWidth > el.clientWidth).map((el) => `${selector} ${el.textContent} ${el.scrollWidth} > ${el.clientWidth}`));
  }
  return { found, wide }; }"""
# #stripTotal as [scrollWidth, clientWidth, whether its text sits on one line]. One line means every box of its text
# shares one band across the strip (the "RM" at 14 px makes the line box 33 px, not the 30 px of its line-height).
STRIP_TOTAL_JS = """() => { const fig = document.querySelector('#stripTotal'); if (!fig) return null;
  const range = document.createRange(); range.selectNodeContents(fig);
  const rects = [...range.getClientRects()].filter((rect) => rect.width > 0);
  return [fig.scrollWidth, fig.clientWidth, rects.length > 0 && Math.max(...rects.map((r) => r.top)) < Math.min(...rects.map((r) => r.bottom))]; }"""


@pytest.mark.parametrize("seed", [seeds.W1, seeds.MAX_E, seeds.MAX_I], ids=["W1", "MAX-E", "MAX-I"])
def test_R60_large_bills_fit_a_360_px_phone(open_app, seed):
    # qa.md at 360 x 780. The card is not displayed below 1024 px, so the figures are read on the strip and in the sheet.
    # Even rows carry no .wk (K2-11), so a MAX-E sheet holds none. A failure on a MAX bill is a design finding for the
    # owner, the CSS stays a byte copy (spec R60).
    page = open_app(seed=seed, viewport=VIEWPORTS[360]).page
    problems = []
    overflow = page.evaluate("document.documentElement.scrollWidth - innerWidth")
    strip = page.evaluate(STRIP_TOTAL_JS)
    if overflow > 0 or strip is None or strip[0] > strip[1]:
        problems.append(f"before Splits the page overflows by {overflow} px and #stripTotal is {strip}")
    open_sheet(page)
    figures = page.evaluate(FIGURES_JS, "#splitsDlg .rbody")
    if figures["wide"] or not all(figures["found"][selector] for selector in (".r-amount", ".amt", ".r-lines dd")):
        problems.append(f"in the sheet {figures}")
    overflow = page.evaluate("document.documentElement.scrollWidth - innerWidth")
    if overflow > 0:
        problems.append(f"with the sheet open the page overflows by {overflow} px")
    assert not problems, " | ".join(problems)


def test_R60_the_large_price_shows_whole(open_app):
    # qa.md on W1 at 360 x 780. "One line box tall" is read from the boxes of #stripTotal's text (STRIP_TOTAL_JS).
    page = open_app(seed=seeds.W1, viewport=VIEWPORTS[360]).page
    price = page.get_by_label("Item 5 price in RM", exact=True)
    found = [price.input_value(), price.evaluate("(el) => [el.scrollWidth, el.clientWidth]")]
    strip, reads = page.evaluate(STRIP_TOTAL_JS), " ".join(page.locator("#stripInfo").inner_text().split())
    problems = [] if found[0] == "964.50" and found[1][0] <= found[1][1] else [f"the price field holds {found}"]
    if reads != "Total RM 1,193.87" or strip[2] is not True:
        problems.append(f"the strip reads {reads!r}, #stripTotal {strip}")
    assert not problems, " | ".join(problems)


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
    assert not problems, " | ".join(problems)


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


# ---------------------------------------------------------------- v1.1.0 task A19: the fidelity gate (R40)
# The gate itself is `python tests/browser/fidelity/run.py` (two controls and 40 pairs, several minutes, writes its
# evidence). These tests keep its inputs honest. The seed scripts carry the clipboard stand-in and equal the seeds, they
# boot the app through its own load path, the after-load scripts press nothing without the stand-in, and the runner
# follows CG-11 and the table, the command and the controls of qa.md "Fidelity gate".
FIDELITY_DIR = ROOT / "tests" / "browser" / "fidelity"
RECORDER_JS = lf_bytes(ROOT / "tests" / "browser" / "clipboard" / "recorder.js").decode("utf-8")
SEED_STATEMENT = re.compile(r"""\AlocalStorage\.setItem\("split\.draft", '([^'\\]*)'\);\n\Z""")
FIDELITY_SEEDS = {  # qa.md "Seed scripts", each file and the seed of seeds.py it repeats
    "seed-s1.js": seeds.S1, "seed-s2.js": seeds.S2, "seed-s5.js": seeds.S5, "seed-re.js": seeds.RE, "seed-w1.js": seeds.W1,
    "seed-t12.js": seeds.T12, "seed-one.js": seeds.ONE, "seed-rnd.js": seeds.RND, "seed-b1.js": seeds.UNREADABLE["B1"],
}


def load_runner():
    import importlib.util
    spec = importlib.util.spec_from_file_location("fidelity_run", FIDELITY_DIR / "run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def seed_script_problems(path, seed):
    """What keeps the file at `path` from being recorder.js and then one setItem of `seed`, [] when nothing does.
    Line ends are compared as LF on both sides, as R1 compares the stylesheet, so any checkout gives the same answer."""
    text = lf_bytes(path).decode("utf-8")
    if not text.startswith(RECORDER_JS):
        return [f"{path.name} does not start with recorder.js"]
    match = SEED_STATEMENT.match(text[len(RECORDER_JS):])
    if not match:
        return [f"{path.name} holds more than one localStorage.setItem statement after the stand-in, or something else"]
    return [] if match.group(1) == seed else [f"{path.name} seeds {match.group(1)[:80]}, not its seed"]


@pytest.mark.parametrize("name, seed", list(FIDELITY_SEEDS.items()))
def test_R40_fidelity_seeds_match(name, seed):
    assert seed_script_problems(FIDELITY_DIR / name, seed) == []


def test_R40_there_is_one_seed_script_per_seed_and_a_planted_fault_is_reported(tmp_path):
    assert sorted(path.name for path in FIDELITY_DIR.glob("seed-*.js")) == sorted(FIDELITY_SEEDS)
    statement = lf_bytes(FIDELITY_DIR / "seed-s1.js").decode("utf-8").removeprefix(RECORDER_JS)
    planted = {"seed-s1-cut.js": statement, "seed-s1-twice.js": RECORDER_JS + statement + statement}
    for name, text in planted.items():
        (tmp_path / name).write_bytes(text.encode("utf-8"))
    assert seed_script_problems(tmp_path / "seed-s1-cut.js", seeds.S1) == ["seed-s1-cut.js does not start with recorder.js"]
    assert seed_script_problems(tmp_path / "seed-s1-twice.js", seeds.S1) == [
        "seed-s1-twice.js holds more than one localStorage.setItem statement after the stand-in, or something else"]


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


AFTER_LOAD_SCRIPTS = ("open-sections.js", "open-splits.js", "open-spare.js", "open-new-bill.js")
OPENED_JS = """() => ({ open: [...document.querySelectorAll('#peopleBlk, #chargesBlk')].map((block) => block.dataset.open),
  dialogs: [...document.querySelectorAll('dialog')].filter((dialog) => dialog.open).map((dialog) => dialog.id) })"""


def run_after_load(page, name):
    """Runs a fidelity after-load script inside an async function, as the harness runs it. Gives "resolved", or what it
    rejected with as [whether it is an Error, its message]."""
    source = (FIDELITY_DIR / name).read_text(encoding="utf-8")
    return page.evaluate(f"""() => (async () => {{ {source}\n }})().then(
      () => "resolved", (reason) => [reason instanceof Error, String(reason?.message ?? reason)])""")


@pytest.mark.chromium_only(reason="The after-load scripts serve the fidelity gate, which runs in Chromium only (ledger S5 row 2).")
def test_R40_an_after_load_script_presses_nothing_without_the_clipboard_stand_in(open_app):
    page = open_app(seed=seeds.S1, clipboard="missing").page
    folded = page.evaluate(OPENED_JS)
    assert folded == {"open": ["false", "false"], "dialogs": []}
    page.evaluate(RECORD_BODY_CLICKS_JS)
    for name in AFTER_LOAD_SCRIPTS:
        assert run_after_load(page, name) == [True, "clipboard stand-in missing"], name
        assert seen_by_the_page(page) == {"presses": [], "clicks": []} and presses_and_clicks(page) == ([], []), name
        assert page.evaluate(OPENED_JS) == folded, name
    page = open_app(seed=seeds.S1).page
    assert run_after_load(page, "open-splits.js") == "resolved"
    assert page.locator("#splitsDlg").evaluate("(dialog) => dialog.matches(':modal')")
    assert page.evaluate("window.testClipboardWrites") == 0
    assert page.evaluate("document.activeElement === document.body && document.querySelectorAll(':focus-visible').length === 0")


# qa.md "Fidelity gate", the table, in its order: golden, seed script, after-load script, viewports. 40 pairs.
WIDE, PHONE = ("390x844", "360x780", "1280x800"), ("390x844", "360x780")
FIDELITY_TABLE = [
    ("bill-items", "seed-s1.js", None, WIDE), ("bill-items-open", "seed-s1.js", "open-sections.js", PHONE),
    ("bill-even", "seed-s2.js", None, WIDE), ("spare-sen", "seed-s1.js", "open-spare.js", WIDE),
    ("spare-sen-one", "seed-one.js", "open-spare.js", WIDE), ("spare-sen-random", "seed-rnd.js", "open-spare.js", WIDE),
    ("splits-sheet", "seed-s1.js", "open-splits.js", PHONE), ("new-bill-dialog", "seed-s1.js", "open-new-bill.js", WIDE),
    ("bill-empty", None, None, WIDE), ("rate-error", "seed-re.js", None, WIDE), ("bill-unassigned", "seed-s5.js", None, WIDE),
    ("bill-unreadable", "seed-b1.js", None, WIDE), ("bill-twelve", "seed-t12.js", None, WIDE),
    ("bill-large", "seed-w1.js", None, WIDE),
]
FIDELITY_PAIRS = [(golden, seed, after_load, viewport) for golden, seed, after_load, viewports in FIDELITY_TABLE
                  for viewport in viewports]


def test_R40_the_runner_uses_the_python_that_runs_pytest():
    source = (FIDELITY_DIR / "run.py").read_text(encoding="utf-8")
    assert "[sys.executable, str(HARNESS)" in source
    assert not re.search(r"\bpip\b|ensurepip|\bvenv\b|\.sdlc-harness|virtualenv", source)  # no environment, no installer
    assert "--engine" not in source  # Chromium only (R58)
    assert len(FIDELITY_PAIRS) == 40 and list(load_runner().PAIRS) == FIDELITY_PAIRS
    import importlib
    for module in ("playwright", "PIL", "numpy"):  # the harness needs these, and the Python that runs this test has them
        importlib.import_module(module)


def test_R40_the_runner_takes_the_harness_from_the_environment_and_has_a_default():
    runner = load_runner()
    assert runner.harness_path({}) == runner.DEFAULT_HARNESS
    assert runner.harness_path({"SDLC_HARNESS": ""}) == runner.DEFAULT_HARNESS  # a blank variable is not a path
    assert runner.harness_path({"SDLC_HARNESS": "elsewhere/fidelity.py"}) == Path("elsewhere/fidelity.py")
    assert runner.HARNESS == runner.harness_path(os.environ)  # what the module picked at import


def documented_command(harness, golden, candidate, viewport, seed, after_load, out):
    """qa.md "Fidelity gate", Command, for one render pair, with sys.executable for `python`."""
    cmd = [sys.executable, str(harness), "--golden", f"./docs/design/{golden}.html", "--candidate", candidate,
           "--viewport", viewport, "--dpr", "1", "--color-scheme", "dark", "--browser-arg=--disable-lcd-text",
           "--fixed-time", "2026-10-13T09:00:00", "--threshold", "0.01"]
    cmd += ["--candidate-init-script", f"./tests/browser/fidelity/{seed}"] if seed else []
    cmd += ["--candidate-after-load", f"./tests/browser/fidelity/{after_load}"] if after_load else []
    return cmd + ["--out", str(out)]


def test_R40_the_runner_builds_the_documented_command():
    runner = load_runner()
    wrong = [pair for pair in FIDELITY_PAIRS if runner.command("http://127.0.0.1:1", *pair, Path("out"))
             != documented_command(runner.HARNESS, pair[0], "http://127.0.0.1:1/", pair[3], pair[1], pair[2], "out")]
    assert wrong == []
    named = {name for _, seed, after_load, _ in FIDELITY_PAIRS for name in (seed, after_load) if name}
    assert sorted(name for name in named if not (FIDELITY_DIR / name).is_file()) == []


class FakeServer:
    """Stands in for rig.StaticServer in the runner's own test. No process is started."""
    base = "http://127.0.0.1:1"

    def __init__(self, root, say=print):
        self.say = say

    def start(self):
        self.say("server STARTED (fake)")
        return self

    def stop(self):
        self.say("server STOPPED (fake)")


def fake_harness(report_for, commands):
    """Stands in for subprocess.run of the harness. Records each command, writes report_for(its --out folder name) as
    report.json there and exits 0, or exits 1 and writes nothing when that gives None."""
    def run(cmd, **_):
        commands.append(cmd)
        out = Path(cmd[cmd.index("--out") + 1])
        report = report_for(out.name)
        if report is not None:
            out.mkdir(parents=True)
            (out / "report.json").write_text(json.dumps(report), encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0 if report is not None else 1, stdout="", stderr="")
    return run


def harness_report(pixels, dimensions_match=True):
    return {"mismatch_pixels": pixels, "mismatch_pct": round(100 * pixels / (390 * 844), 4), "dimensions_match": dimensions_match,
            "golden_size": [390, 844], "candidate_size": [390, 844] if dimensions_match else [390, 900]}


# Each case: reports that differ from a clean run (by --out folder name, None for a harness that wrote none), the
# CONTROL lines of run.log, the pairs that FAIL (None when a control stops the run before any pair) and the exit status.
RUNNER_CASES = {
    "clean": ({}, ["CONTROL PASS control-self", "CONTROL PASS control-noseed"], [], 0),
    "self-compare-noisy": ({"control-self-390x844": harness_report(3)}, ["CONTROL FAIL control-self"], None, 1),
    "no-seed-blind": ({"control-noseed-390x844": harness_report(0)},
                      ["CONTROL PASS control-self", "CONTROL FAIL control-noseed"], None, 1),
    "pairs-at-fault": ({"bill-large-360x780": harness_report(12), "bill-twelve-1280x800": harness_report(0, False),
                        "splits-sheet-390x844": None},
                       ["CONTROL PASS control-self", "CONTROL PASS control-noseed"],
                       ["splits-sheet 390x844", "bill-twelve 1280x800", "bill-large 360x780"], 1),
}


@pytest.mark.parametrize("case", list(RUNNER_CASES))
def test_R40_the_runner_runs_its_controls_first_and_passes_only_a_clean_pair(monkeypatch, tmp_path, case):
    changed, control_lines, failing, status = RUNNER_CASES[case]
    clean = lambda name: harness_report(5000 if name == "control-noseed-390x844" else 0)  # the cold app is not bill-items
    runner, commands = load_runner(), []
    harness = tmp_path / "fidelity.py"
    harness.write_bytes(b"")
    monkeypatch.setattr(runner, "HARNESS", harness)
    monkeypatch.setattr(runner, "EVIDENCE_ROOT", tmp_path / "evidence")
    monkeypatch.setattr(runner, "rig", types.SimpleNamespace(ROOT=ROOT, StaticServer=FakeServer))
    monkeypatch.setattr(runner, "subprocess", types.SimpleNamespace(
        run=fake_harness(lambda name: changed[name] if name in changed else clean(name), commands),
        TimeoutExpired=subprocess.TimeoutExpired))
    assert runner.main() == status
    [run_folder] = (tmp_path / "evidence").iterdir()
    log = (run_folder / "run.log").read_text(encoding="utf-8").splitlines()
    assert [" ".join(line.split()[:3]) for line in log if line.startswith("CONTROL ")] == control_lines
    base = FakeServer.base
    controls = [documented_command(harness, "bill-items", base + path, "390x844", None, None, run_folder / f"{name}-390x844")
                for name, path in (("control-self", "/docs/design/bill-items.html"), ("control-noseed", "/"))]
    pairs = [documented_command(harness, golden, base + "/", viewport, seed, after_load, run_folder / f"{golden}-{viewport}")
             for golden, seed, after_load, viewport in FIDELITY_PAIRS]
    verdicts = [line.split()[:3] for line in log if line.startswith(("PASS ", "FAIL "))]
    if failing is None:
        assert commands == controls[:len(control_lines)] and verdicts == [] and any(line.startswith("NOT RUN") for line in log)
    else:
        assert commands == controls + pairs
        assert [" ".join(verdict[1:]) for verdict in verdicts if verdict[0] == "FAIL"] == failing
        assert sum(verdict[0] == "PASS" for verdict in verdicts) == 40 - len(failing)
        assert f"{40 - len(failing)} of 40 pairs pass" in log[-1]


# ---------------------------------------------------------------- v1.1.0 task A20: the cold-boot live gate (R41)
# The gate itself is `python tests/browser/live_e2e.py` (writes qa/live-e2e/<stamp>-<engine>/, or -<engine>-control/ for
# its control). These tests keep its script honest without running a second browser inside this one, as the @R41 @static
# scenario "The gate script makes a cold context except on its control path" says: what it expects, how it labels its
# steps, that it uses real gestures and reads only, and that only its control path gets a stored bill.
LIVE_SCRIPT = ROOT / "tests" / "browser" / "live_e2e.py"
SUPPORT_SCRIPT = ROOT / "tests" / "browser" / "support.py"  # the helpers the gate reads and types through
ACTION_WORDS = {"open", "replace", "click", "close", "type", "press", "tap", "reload", "no"}
BANNED_KEYWORDS = ("bypass_csp", "permissions")  # the strict policy stays live and no permission is granted
# No shortcut that is not a gesture, and no screenshot, which adds a stylesheet that WebKit's policy refuses (R59 (4)).
BANNED_ATTRIBUTES = ("fill", "dispatch_event", "check", "set_checked", "select_option", "route", "add_init_script",
                     "launch_persistent" + "_context", "screenshot")
# The read-only list. Every page.evaluate and wait_for_function argument of the script and of the support.py helpers it
# runs is one of these, and each only reads. TWO_FRAMES_JS waits two animation frames and FOCUS_ON_NEW_BILL_JS is a
# condition, so neither changes anything. page_script_writes checks that each text still only reads.
READS_ONLY = {"STAND_IN_JS", "TWO_FRAMES_JS", "OPEN_DIALOGS_JS", "PICKED_JS", "SECTIONS_JS", "ITEMS_JS", "FOCUS_ON_NEW_BILL_JS",
              "COLD_BOOT_JS", "RECEIPT_JS", "READS_AT_JS", "ACTIVE_LABEL_JS"}
READ_EXPRESSIONS = {"window.testClipboardText", "window.testClipboardWrites", "window.testCspViolations",
                    "Array.isArray(window.testCspViolations)", "localStorage.getItem('split.draft')"}
# What a page script of the gate may call: reads of the page, of the stand-in's records and of the draft's text, the
# methods that shape what was read, and the helpers the script declares itself (const name = (...) =>). The scan reads
# the text, it does not parse it, so it catches a plain write (localStorage.clear(), an assignment, ++ or --) and not
# one hidden on purpose.
READ_CALLS = {"querySelector", "querySelectorAll", "getAttribute", "matches", "checkVisibility", "getPropertyValue",
              "createTreeWalker", "nextNode", "getItem", "isArray", "call", "includes", "map", "filter", "slice", "concat",
              "join", "push", "replace", "trim", "requestAnimationFrame", "Promise"}
JS_STRING = re.compile(r"'(?:\\.|[^'\\])*'" + r'|"(?:\\.|[^"\\])*"')  # blanked first, so '--rows' is no step
JS_CALL = re.compile(r"([A-Za-z_$][\w$]*)\s*\(")
JS_NOT_CALLS = {"if", "for", "while", "switch", "catch", "return", "typeof", "function"}
JS_HELPER = re.compile(r"(?:\bconst|,)\s*([A-Za-z_$][\w$]*)\s*=\s*\(")
JS_WRITE = re.compile(r"(?<![=!<>])=(?![=>])|\+\+|--")
JS_DECLARED = re.compile(r"(?:\bconst|,)\s*[A-Za-z_$][\w$]*\s*$")  # what comes before the = of a const declaration


def gate_script(path=LIVE_SCRIPT):
    """The text and the syntax tree of the gate script at `path`, the one way these tests read it, so a planted copy in a
    temporary folder goes through the same code as the real script (task A20 item 1)."""
    source = path.read_text(encoding="utf-8")
    return source, ast.parse(source)


def method_calls(tree, name):
    return [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == name]


def is_name(node, *parts):
    """Whether `node` spells the dotted name `parts`, as is_name(node, "rig", "storage_state") for rig.storage_state."""
    for part in reversed(parts[1:]):
        if not (isinstance(node, ast.Attribute) and node.attr == part):
            return False
        node = node.value
    return isinstance(node, ast.Name) and node.id == parts[0]


def keyword_of(call, name):
    return next((keyword.value for keyword in call.keywords if keyword.arg == name), None)


def is_control(node):
    """The parsed --control value, the namespace's attribute (args.control) or a name bound to it."""
    return (isinstance(node, ast.Attribute) and node.attr == "control") or (isinstance(node, ast.Name) and node.id == "control")


def live_gate_steps(path=LIVE_SCRIPT):
    _, tree = gate_script(path)
    return [call for call in method_calls(tree, "step") if is_name(call.func.value, "gate")]


def rig_contexts(tree):
    return [call for call in method_calls(tree, "new" + "_context") if is_name(call.func.value, "rig")]


def storage_state_problems(tree, context):
    """storage_state is a keyword exactly once, on the one rig.new_context call, and reads
    `rig.storage_state(..., seeds.S2) if <the parsed --control value> == "seeded" else None` (qa.md, Control mode)."""
    given = [node for node in ast.walk(tree) if isinstance(node, ast.keyword) and node.arg == "storage_state"]
    value = keyword_of(context, "storage_state")
    if len(given) != 1 or value is None:
        return ["storage_state is not a keyword exactly once, on the rig.new_context call"]
    if not isinstance(value, ast.IfExp):
        return ["storage_state is not a conditional expression"]
    test, problems = value.test, []
    sides = [test.left, *test.comparators] if isinstance(test, ast.Compare) else []
    if not (sides and [type(op) for op in test.ops] == [ast.Eq] and any(is_control(side) for side in sides)
            and any(isinstance(side, ast.Constant) and side.value == "seeded" for side in sides)):
        problems.append('the test of storage_state is not the parsed --control value == "seeded"')
    if not (isinstance(value.body, ast.Call) and is_name(value.body.func, "rig", "storage_state")
            and any(is_name(argument, "seeds", "S2") for argument in value.body.args)):
        problems.append("storage_state does not give the K2 state when its test holds")
    if not (isinstance(value.orelse, ast.Constant) and value.orelse.value is None):
        problems.append("the else branch of storage_state is not None")
    return problems


def control_option_problems(tree):
    """The one add_argument("--control", ...) call has the choices ["seeded"] and the default None (qa.md, Control mode)."""
    options = [call for call in method_calls(tree, "add_argument")
               if call.args and isinstance(call.args[0], ast.Constant) and call.args[0].value == "--control"]
    if len(options) != 1:
        return ["there is not exactly one --control option"]
    choices, default = keyword_of(options[0], "choices"), keyword_of(options[0], "default")
    problems = [] if isinstance(choices, ast.List) and ast.literal_eval(choices) == ["seeded"] else [
        'the choices of --control are not ["seeded"]']
    if not (isinstance(default, ast.Constant) and default.value is None):
        problems.append("the default of --control is not None")
    return problems


def screencast_problems(tree, context):
    """page.screencast.start is called exactly once, with on_frame and a size equal to the context's viewport (R41)."""
    starts = [call for call in method_calls(tree, "start")
              if isinstance(call.func.value, ast.Attribute) and call.func.value.attr == "screencast"]
    if len(starts) != 1:
        return ["page.screencast.start is not called exactly once"]
    size, viewport = keyword_of(starts[0], "size"), keyword_of(context, "viewport")
    problems = [] if keyword_of(starts[0], "on_frame") is not None else ["page.screencast.start has no on_frame"]
    if size is None or viewport is None or ast.dump(size) != ast.dump(viewport):
        problems.append("the size of page.screencast.start is not the context's viewport")
    return problems


def read_argument(call):
    """The first argument of an evaluate or wait_for_function call, as its name, its text or its source."""
    first = call.args[0] if call.args else None
    if isinstance(first, ast.Name):
        return first.id
    return first.value if isinstance(first, ast.Constant) else ast.unparse(first) if first is not None else "no argument"


def string_value(node, strings):
    """The text of a string expression: a literal, a name in `strings`, or an f-string of those. None for anything else."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return strings.get(node.id)
    if isinstance(node, ast.JoinedStr):
        parts = [string_value(part.value if isinstance(part, ast.FormattedValue) else part, strings) for part in node.values]
        return None if None in parts else "".join(parts)
    return None


def module_strings(tree):
    """The module-level string constants of `tree` by name, so an evaluate argument such as COLD_BOOT_JS has a text."""
    strings = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            text = string_value(node.value, strings)
            if text is not None:
                strings[node.targets[0].id] = text
    return strings


def gate_helpers(tree, helper_tree):
    """The functions of support.py the gate runs: those it calls as support.<name>, and those these call in turn."""
    functions = {node.name: node for node in helper_tree.body if isinstance(node, ast.FunctionDef)}
    names = [call.func.attr for call in ast.walk(tree) if isinstance(call, ast.Call)
             and isinstance(call.func, ast.Attribute) and is_name(call.func.value, "support")]
    found = {}
    while names:
        name = names.pop()
        if name in functions and name not in found:
            found[name] = functions[name]
            names += [call.func.id for call in ast.walk(found[name]) if isinstance(call, ast.Call) and isinstance(call.func, ast.Name)]
    return list(found.values())


def page_script_writes(name, script):
    """What makes the page script `script` (named `name`) more than a read, one line each, [] for a read."""
    code = JS_STRING.sub("''", script)
    own = set(JS_HELPER.findall(code))
    found = [f"{name} calls {call}(), which is not a read" for call in dict.fromkeys(JS_CALL.findall(code))
             if call not in READ_CALLS | JS_NOT_CALLS | own]
    if any(write.group() != "=" or not JS_DECLARED.search(code[:write.start()]) for write in JS_WRITE.finditer(code)):
        found.append(f"{name} assigns or steps a value")
    return found


def live_gate_problems(path, helpers=SUPPORT_SCRIPT):
    """What keeps the gate script at `path` from qa.md "Cold-boot live-e2e gate" (Rules, Control mode) and from R41's
    capture, one line each, [] when nothing does. The real script and every planted copy go through it (task A20). The
    Rules on gestures and reads also cover the functions of `helpers` (support.py) that the gate runs (CR-S5-6)."""
    source, tree = gate_script(path)
    _, helper_tree = gate_script(helpers)
    helper_strings = module_strings(helper_tree)
    run = [(tree, module_strings(tree)), *((function, helper_strings) for function in gate_helpers(tree, helper_tree))]
    nodes = [node for part, _ in run for node in ast.walk(part)]
    problems = [f"{node.arg} is a keyword argument" for node in nodes
                if isinstance(node, ast.keyword) and node.arg in BANNED_KEYWORDS]
    used = {node.attr for node in nodes if isinstance(node, ast.Attribute)}
    problems += [f".{name} is used" for name in BANNED_ATTRIBUTES if name in used]
    made = "new" + "_context("  # spelled in two parts so test_R39_only_the_rig_makes_browser_contexts does not flag this file
    contexts = rig_contexts(tree)
    if source.count("rig." + made) != 1 or source.count(made) != 1 or len(contexts) != 1:
        return problems + ["the one context does not come from one rig.new_context call"]
    problems += storage_state_problems(tree, contexts[0])
    problems += control_option_problems(tree)
    problems += screencast_problems(tree, contexts[0])
    reads = [(call, strings) for part, strings in run
             for call in method_calls(part, "evaluate") + method_calls(part, "wait_for_function")]
    seen = [read_argument(call) for call, _ in reads]
    problems += [f"{item} is not on the read-only list" for item in seen if item not in READS_ONLY | READ_EXPRESSIONS]
    texts = dict.fromkeys((read_argument(call), string_value(call.args[0], strings) if call.args else None)
                          for call, strings in reads)
    for item, script in texts:
        problems += [f"{item} has no text this test can read"] if script is None else page_script_writes(item, script)
    return problems if seen else problems + ["the script reads nothing with page.evaluate"]


def test_R41_the_step_log_puts_gesture_and_assertion_in_their_own_fields():
    # [v1.1.0] The steps 1 to 9 of qa.md's flow, with the 1.0 action words unchanged (task A20 item 2).
    import live_e2e
    assert live_e2e.format_step(3, "click it", "it is open", "PASS") == "03 | gesture: click it | assertion: it is open | PASS"
    steps = live_gate_steps()
    assert [call.args[0].value for call in steps] == list(range(1, 10))  # one call per numbered step of qa.md
    for call in steps:
        fields = {keyword.arg: keyword.value.value if isinstance(keyword.value, ast.Constant) else None for keyword in call.keywords}
        gesture, assertion = fields["gesture"], fields["assertion"]
        assert gesture and assertion, call.args[1].value
        assert gesture.split()[0] in ACTION_WORDS, f"step {call.args[0].value}: the gesture field holds {gesture!r}"
        assert assertion.split()[0] not in ACTION_WORDS, f"step {call.args[0].value}: the assertion field holds {assertion!r}"


def test_R41_the_gate_installs_the_clipboard_recorder_and_the_csp_listener_and_nothing_else():
    # [v1.1.0] qa.md, Rules. The recorder (CG-7 of 1.0), then the engine-neutral CSP detector (task A20 item 3).
    import live_e2e
    assert live_e2e.INIT_SCRIPTS == ["tests/browser/clipboard/recorder.js", "tests/browser/csp/listener.js"]


def test_R41_the_gate_uses_real_gestures_and_reads_only():
    # [v1.1.0] The @R41 @static scenario up to its INIT_SCRIPTS line, and its capture lines (task A20 items 1 and 4).
    assert live_gate_problems(LIVE_SCRIPT) == []


# Each planted copy is the real script with one fault (the @R41 @static scenario), and the one line the guard reports.
PLANTED_GATE_FAULTS = {
    "storage-state-without-a-condition": ["storage_state is not a conditional expression"],
    "else-branch-is-the-k2-state": ["the else branch of storage_state is not None"],
    "bypass-csp-false": ["bypass_csp is a keyword argument"],
    "page-screenshot-in-the-step-helper": [".screenshot is used"],
}


def planted_gate_copy(source, tree, fault):
    """The text of the gate script with `fault` planted, cut from the script's own syntax tree so it follows its edits."""
    [context] = rig_contexts(tree)
    value, segment = keyword_of(context, "storage_state"), lambda node: ast.get_source_segment(source, node)
    if fault == "storage-state-without-a-condition":
        return source.replace(segment(value), segment(value.body), 1)
    if fault == "else-branch-is-the-k2-state":
        return source.replace(segment(value), f"{segment(value.body)} if {segment(value.test)} else {segment(value.body)}", 1)
    if fault == "bypass-csp-false":
        call = segment(context)
        return source.replace(call, call[:-1].rstrip().rstrip(",") + ", bypass_csp=False)", 1)
    step = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "step")
    lines = source.splitlines(keepends=True)
    lines.insert(step.body[-1].lineno - 1, " " * step.body[-1].col_offset + 'self.page.screenshot(path="planted.png")\n')
    return "".join(lines)


@pytest.mark.parametrize("fault", list(PLANTED_GATE_FAULTS))
def test_R41_a_planted_copy_of_the_gate_script_is_reported(tmp_path, fault):
    source, tree = gate_script()
    planted = tmp_path / "live_e2e.py"
    planted.write_text(planted_gate_copy(source, tree, fault), encoding="utf-8")
    assert planted.read_text(encoding="utf-8") != source
    assert live_gate_problems(planted) == PLANTED_GATE_FAULTS[fault]


# Each planted copy is the real support.py with one write in a helper the gate runs, and the one line the guard
# reports (code review CR-S5-6: the gate reads the cold boot through COLD_BOOT_JS and types through replace_text).
PLANTED_HELPER_FAULTS = {
    "cold-boot-js-clears-the-storage": ["COLD_BOOT_JS calls clear(), which is not a read"],
    "replace-text-fills-the-field": [".fill is used"],
}


def planted_helper_copy(source, tree, fault):
    """The text of support.py with `fault` planted, cut from its own syntax tree so it follows its edits."""
    if fault == "cold-boot-js-clears-the-storage":
        [script] = [node.value for node in tree.body if isinstance(node, ast.Assign) and is_name(node.targets[0], "COLD_BOOT_JS")]
        text = ast.get_source_segment(source, script)
        return source.replace(text, text.replace("{", "{ localStorage.clear();", 1), 1)
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "replace_text")
    first = function.body[1]  # the first statement after the docstring
    lines = source.splitlines(keepends=True)
    lines.insert(first.lineno - 1, " " * first.col_offset + 'locator.fill("")\n')
    return "".join(lines)


@pytest.mark.parametrize("fault", list(PLANTED_HELPER_FAULTS))
def test_R41_a_planted_copy_of_a_helper_the_gate_runs_is_reported(tmp_path, fault):
    # The gate's Rules ("page.evaluate only reads", "Only real gestures change the app") hold for what it runs from
    # support.py too, so the guard follows the helpers the gate calls (code review CR-S5-6).
    source, tree = gate_script(SUPPORT_SCRIPT)
    planted = tmp_path / "support.py"
    planted.write_text(planted_helper_copy(source, tree, fault), encoding="utf-8")
    assert planted.read_text(encoding="utf-8") != source
    assert live_gate_problems(LIVE_SCRIPT, helpers=planted) == PLANTED_HELPER_FAULTS[fault]


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


def test_R58_a_run_never_writes_into_an_evidence_folder_it_did_not_make(tmp_path, monkeypatch):
    # Two runs of one engine in the same second get the same <stamp>-<engine> name. The second must not write into the
    # first one's folder (constitution, Gates and evidence, each run writes its own capture; code review CR-S5-14).
    import conftest
    moment = types.SimpleNamespace(strftime=lambda pattern: "20261015-235959")
    monkeypatch.setattr(conftest, "datetime", types.SimpleNamespace(datetime=types.SimpleNamespace(now=lambda: moment)))
    monkeypatch.setattr(conftest, "EVIDENCE_ROOT", tmp_path)
    monkeypatch.setitem(conftest._evidence, "dir", None)
    first = conftest.evidence_dir()
    monkeypatch.setitem(conftest._evidence, "dir", None)  # the second run's first call, in the same second
    try:
        second = conftest.evidence_dir()
    except FileExistsError:
        second = None
    assert first.is_dir() and first.parent == tmp_path and second != first


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
    """New bill, then Start new bill (R31), and wait for the dialog's close event (`closing`), which is where focus goes
    back to New bill (task A16)."""
    open_dialog(page)
    closing(page, lambda: page.get_by_role("button", name="Start new bill", exact=True).click())


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
    type_into(page, item_price(page, 1), "abc")  # "Nasi lemak ayam price in RM" (R11)
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


# ---------------------------------------------------------------- Task A22: names stay plain (R62, R4, R5, R11, R26, R33)
# The class of core R35 written out, because Python's re has no \p{...}: the C0 and C1 controls (Cc, 65), LS, PS and
# the 12 bidi controls (qa.md, Plain names, "Python's equivalent list of the 79 code points").
NAME_CLASS = frozenset([*range(0x00, 0x20), *range(0x7F, 0xA0), 0x2028, 0x2029, 0x061C, 0x200E, 0x200F,
                        *range(0x202A, 0x202F), *range(0x2066, 0x206A)])
assert len(NAME_CLASS) == 79


def class_free(text):
    return not any(ord(char) in NAME_CLASS for char in text)


def spelled(text):
    """`text` with every code point outside printable ASCII written U+XXXX, for ids and messages."""
    return "".join(char if 0x20 <= ord(char) <= 0x7E else f"U+{ord(char):04X}" for char in text)


# A test-side recorder of what each input event left in its field before the app's listener ran (window, capture
# phase), so a character the tool cannot insert fails its case with its code point instead of passing unseen.
RECORD_INPUT_JS = """() => { window.testInputValues = [];
  window.addEventListener('input', (event) => window.testInputValues.push(event.target.value), true); }"""
FIELD_STATE_JS = "(el) => [el === document.activeElement, el.value, el.selectionStart, el.selectionEnd]"
PEOPLE_SUMMARY_JS = "() => document.querySelector('#peopleSum .sec-txt')?.textContent ?? null"


def insert(page, text):
    """qa.md "insert T": page.keyboard.insert_text(T) on the focused field, one input event with the text, which is how
    a paste or a drop arrives. Returns the characters of T the tool did not put into the field, spelled (RECORD_INPUT_JS
    must be on the page)."""
    page.evaluate("() => { window.testInputValues = []; }")
    page.keyboard.insert_text(text)
    seen = page.evaluate("() => window.testInputValues")
    return [spelled(char) for char in text if not seen or char not in seen[-1]]


def people_names(page):
    return [person["name"] for person in stored(page)["bill"]["people"]]


PLAIN_INSERTS = [("‮", "Ben", 3), ("‮x", "Benx", 4), ("a b", "Benab", 5), ("\u0000", "Ben", 3),
                 ("\u0009Lee", "BenLee", 6)]


@pytest.mark.parametrize("text, value, caret", PLAIN_INSERTS, ids=[spelled(text) for text, _, _ in PLAIN_INSERTS])
def test_R62_a_control_or_bidi_character_put_into_a_persons_name_is_removed_at_once(open_app, text, value, caret):
    # qa.md "Copy summary on the card" at 390 x 844: the card is not displayed below 1024 px, so the one Copy summary
    # shown there (the strip's) is pressed, whose text R22 proves equal to the card's (BUILD.md, task A22).
    page = open_app(seed=seeds.S2).page
    open_people_first(page)
    page.evaluate(RECORD_INPUT_JS)
    field = person_field(page, 2)
    handle = field.element_handle()
    field.click()
    page.keyboard.press("End")
    assert insert(page, text) == []
    assert page.evaluate(FIELD_STATE_JS, handle) == [True, value, caret, caret]
    names = people_names(page)
    assert names[1] == value and all(class_free(name) for name in names)
    rows, _ = card_rows(page)
    summary = page.evaluate(PEOPLE_SUMMARY_JS)
    assert [rows[1][0], person_rows(page)[1]["remove"][1]] == [value, f"Remove {value}"]
    assert value in summary and class_free(summary)
    copy_summary(page)
    assert page.evaluate("window.testClipboardText").split("\n")[3] == f"{value} RM 38.87"


def test_R62_a_removal_in_the_middle_of_a_name_keeps_the_caret_where_the_text_went_in(open_app):
    page = open_app(seed=seeds.S2).page
    open_people_first(page)
    page.evaluate(RECORD_INPUT_JS)
    field = person_field(page, 2)
    handle = field.element_handle()
    field.click()
    page.keyboard.press("End")
    page.keyboard.press("ArrowLeft")  # the caret after "Be"
    assert insert(page, "‮x⁧") == []
    assert page.evaluate(FIELD_STATE_JS, handle) == [True, "Bexn", 3, 3]
    page.keyboard.type("y")
    assert page.evaluate(FIELD_STATE_JS, handle)[:2] == [True, "Bexyn"] and people_names(page)[1] == "Bexyn"


EVERY_KIND = [0x0001, 0x0009, 0x001B, 0x001F, 0x007F, 0x0080, 0x0085, 0x009F, 0x2028, 0x2029, 0x061C, 0x200E, 0x200F,
              0x202A, 0x202B, 0x202C, 0x202D, 0x202E, 0x2066, 0x2067, 0x2068, 0x2069]


def test_R62_each_kind_of_character_in_the_class_is_removed_from_a_name_field(open_app):
    # The ends of each range through the real field. The whole class is proved once in Node (split-core, R35).
    page = open_app(seed=seeds.S2).page
    open_people_first(page)
    page.evaluate(RECORD_INPUT_JS)
    field = person_field(page, 1)
    handle = field.element_handle()
    wrong = []
    for code_point in EVERY_KIND:
        field.click()
        page.keyboard.press("Control+A")
        page.keyboard.type("A")
        missing = insert(page, f"B{chr(code_point)}C")
        found = [*page.evaluate(FIELD_STATE_JS, handle)[1:], people_names(page)[0]]
        if missing or found != ["ABC", 3, 3, "ABC"]:
            wrong.append(f"U+{code_point:04X}: not inserted {missing}" if missing else f"U+{code_point:04X}: {spelled(str(found))}")
    assert wrong == []


def test_R62_characters_outside_the_class_stay_in_a_name(open_app):
    page = open_app(seed=seeds.S2).page
    open_people_first(page)
    page.evaluate(RECORD_INPUT_JS)
    kept, emoji = "A​B C﻿", "\U0001F468‍\U0001F469‍\U0001F467"
    for number, text in ((2, kept), (3, emoji)):
        person_field(page, number).click()
        page.keyboard.press("End")
        assert insert(page, text) == []
    values = [person_field(page, number).input_value() for number in (2, 3)]
    assert values == people_names(page)[1:3] == ["Ben" + kept, "Chen" + emoji]


# A test-side spy on "Person 2 name" alone: every call of the value setter of HTMLInputElement.prototype and of
# setSelectionRange on that element adds 1 (qa.md, "Typing that brings no character of the class writes nothing").
FIELD_WRITES_SPY_JS = """(el) => { window.testFieldWrites = 0; const proto = HTMLInputElement.prototype;
  const value = Object.getOwnPropertyDescriptor(proto, 'value'), select = proto.setSelectionRange;
  Object.defineProperty(proto, 'value', { ...value,
    set(text) { if (this === el) window.testFieldWrites += 1; value.set.call(this, text); } });
  proto.setSelectionRange = function (...args) { if (this === el) window.testFieldWrites += 1; return select.apply(this, args); }; }"""


def test_R62_typing_that_brings_no_character_of_the_class_writes_nothing_into_the_field(open_app):
    page = open_app(seed=seeds.S2).page
    field = person_field(page, 2)
    handle = field.element_handle()
    page.evaluate(FIELD_WRITES_SPY_JS, handle)
    open_people_first(page)
    field.click()
    page.keyboard.press("End")
    page.keyboard.type("abc")
    page.keyboard.press("Home")
    page.keyboard.type("X")
    page.keyboard.press("Backspace")
    assert page.evaluate("window.testFieldWrites") == 0
    assert page.evaluate(FIELD_STATE_JS, handle) == [True, "Benabc", 0, 0]


ITEM_NAMES_JS = """(index) => { const li = document.querySelectorAll('li.item')[index];
  return li && [li.querySelector('.field.money input').getAttribute('aria-label'),
    li.querySelector('button.icon-btn').getAttribute('aria-label'), li.querySelector('div.taps').getAttribute('aria-label')]; }"""


def test_R62_an_item_name_loses_the_class_too(open_app):
    page = open_app(seed=seeds.S1).page
    page.evaluate(RECORD_INPUT_JS)
    field = item_name(page, 2)
    handle = field.element_handle()
    field.click()
    page.keyboard.press("End")
    assert insert(page, "‮x") == []
    value = "Char kuey teowx"
    assert page.evaluate(FIELD_STATE_JS, handle) == [True, value, 15, 15]
    assert stored(page)["bill"]["items"][1]["name"] == value
    assert page.evaluate(ITEM_NAMES_JS, 1) == [f"{value} price in RM", f"Remove {value}", f"Who had {value}"]


def test_R62_a_name_made_only_of_removed_characters_falls_back_to_its_position(open_app):
    page = open_app(seed=seeds.S2).page
    open_people_first(page)
    page.evaluate(RECORD_INPUT_JS)
    field = person_field(page, 2)
    field.click()
    page.keyboard.press("Control+A")
    assert insert(page, "‮") == []
    assert [field.input_value(), field.get_attribute("placeholder"), people_names(page)[1]] == ["", "Person 2", ""]
    rows, _ = card_rows(page)
    assert [rows[1][0], person_rows(page)[1]["remove"][1]] == ["Person 2", "Remove Person 2"]
    assert "Person 2" in page.evaluate(PEOPLE_SUMMARY_JS)


# One box per character of the People summary's text node (a Range over each code point), the zero-width ones left
# out, as [left, top, bottom], so the order they are drawn in can be read (SEC-S5-1, SEC-S5-3).
CHARACTER_BOXES_JS = """(selector) => { const node = document.querySelector(selector)?.firstChild; if (!node) return null;
  const boxes = []; let at = 0;
  for (const char of node.data) { const range = document.createRange(); range.setStart(node, at); range.setEnd(node, at + char.length);
    const box = range.getBoundingClientRect(); if (box.width > 0) boxes.push([box.left, box.top, box.bottom]); at += char.length; }
  return boxes; }"""


def people_summaries(labels):
    """Every summary R48 (2) lets the People row show for `labels`, longest first, as peopleSummaries writes them."""
    fewer = [f"{', '.join(labels[:shown])} and {len(labels) - shown} more" for shown in range(len(labels) - 1, 0, -1)]
    return [", ".join(labels), *fewer, f"{len(labels)} people"]


def test_R62_a_saved_name_with_bidi_controls_loads_plain_and_the_people_line_reads_left_to_right(open_app):
    page = open_app(seed=seeds.G8, init_scripts=[support.storage_driver("count-set")]).page
    fields = page.locator("li.person input")
    summary = page.evaluate(PEOPLE_SUMMARY_JS)
    boxes = page.evaluate(CHARACTER_BOXES_JS, "#peopleSum .sec-txt") or []
    lefts = [box[0] for box in boxes]
    found = {  # every property of the load at once, so one run shows each that fails
        "notes": notes(page), "people": section_state(page)[0],
        "fields": [fields.nth(index).input_value() for index in range(5)], "placeholder": fields.nth(4).get_attribute("placeholder"),
        "summary": [class_free(summary), summary in people_summaries(["Aisyah", "Ben", "Chen", "AB", "Person 5"])],
        "left to right": bool(boxes) and all(right > left for left, right in zip(lefts, lefts[1:])),
        "one band": bool(boxes) and max(box[1] for box in boxes) < min(box[2] for box in boxes),
        "stored": [stored_text(page) == seeds.G8, page.evaluate("window.testSetItemCalls")],
    }
    assert found == {"notes": [], "people": FOLDED, "fields": ["Aisyah", "Ben", "Chen", "AB", ""], "placeholder": "Person 5",
                     "summary": [True, True], "left to right": True, "one band": True, "stored": [True, 0]}, spelled(summary)
    open_people_first(page)
    type_at_end(page, person_field(page, 1), "x")
    assert people_names(page) == ["Aisyahx", "Ben", "Chen", "AB", ""]
    copy_summary(page)  # the strip's at 390 x 844, as in the outline above
    rows, _ = card_rows(page)
    assert page.evaluate("window.testClipboardText").split("\n")[2:-1] == [f"{name} {amount}" for name, amount, _ in rows]


# ===== END OF TESTS (new tests go above this line) =====
