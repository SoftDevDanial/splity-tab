"""Render checks for round-1 direction C, Daylight Instrument.

Opens c.html by file URL in headless Chromium at 390x844, 360x780 and 1280x800, drives every popup, dialog and
prototype state, saves screenshots beside this script, and writes results.json. Every wait is bounded and the
browser is closed in a finally block. Never touches the clipboard, makes no network calls.
"""
import json
import pathlib
import re

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
ROUND = HERE.parent.parent
PAGE = ROUND / "c.html"
URL = PAGE.as_uri()
ICONS_JS = ROUND.parents[3] / "src" / "ui" / "icons.js"
B_HTML = ROUND / "b.html"

VIEWPORTS = [(390, 844), (360, 780), (1280, 800)]
results = {"url": URL, "console_errors": [], "requests": [], "checks": [], "overflow": {}, "contrast": {}, "targets": {}}


def check(name, ok, detail=""):
    results["checks"].append({"name": name, "ok": bool(ok), "detail": detail})


# ---------- contrast ----------
def _lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def lum(hx):
    hx = hx.strip().lstrip("#")
    r, g, b = int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


# ---------- static file checks ----------
def static_checks():
    src = PAGE.read_text(encoding="utf-8")
    check("no em or en dash in the page", "—" not in src and "–" not in src)
    ext = [m for m in re.findall(r'(?:src|href)\s*=\s*"([^"]+)"', src) if m.startswith(("http:", "https:", "//"))]
    check("no external src or href", not ext, ext)
    check("no @import or url(http", "@import" not in src and "url(http" not in src)
    mine = dict(re.findall(r'<symbol id="i-([\w-]+)" viewBox="0 0 256 256"><path d="([^"]+)"', src))
    known = set(re.findall(r'"(M[^"]+Z)"', ICONS_JS.read_text(encoding="utf-8")))
    known |= set(re.findall(r'<path d="([^"]+)"', B_HTML.read_text(encoding="utf-8")))
    bad = [k for k, d in mine.items() if d not in known]
    check("every icon path is an exact copy (icons.js or b.html)", not bad, {"icons": sorted(mine), "not_exact": bad})
    check("mark path is the brand geometry", 'd="M3 6h24v9H3zM33 6h12v9H33zM3 30h42v9H3z"' in src)


OVERFLOW_JS = """
() => {
  const vw = document.documentElement.clientWidth;
  const bad = [];
  for (const el of document.querySelectorAll('body *')) {
    if (el.closest('.sr-only') || el.closest('svg[width="0"]') || el.closest('dialog:not([open])') || el.closest('[hidden]')) continue;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    if (r.right > vw + 0.5 || r.left < -0.5) bad.push({ tag: el.tagName, cls: typeof el.className === 'string' ? el.className : '', id: el.id, left: Math.round(r.left), right: Math.round(r.right) });
  }
  const clipped = [];
  for (const el of document.querySelectorAll('.brk dd, .brk dt, .sh td, .sh th, .tot, .tot-l, .param-l, .spare-t, .btn, .tog, .opt-t, .word')) {
    if (el.closest('.sr-only')) continue;
    if (el.scrollWidth > el.clientWidth + 1) clipped.push({ cls: el.className, text: el.textContent.trim().slice(0, 40), sw: el.scrollWidth, cw: el.clientWidth });
  }
  return { scrollWidth: document.documentElement.scrollWidth, bodyScrollWidth: document.body.scrollWidth, clientWidth: vw, poking: bad.slice(0, 20), clipped };
}
"""

TARGETS_JS = """
() => {
  const small = [];
  const els = document.querySelectorAll('.app button, .app .fld, .app .pcell, .app .param, .mode span, dialog[open] button');
  for (const el of els) {
    if (el.closest('.sr-only') || el.closest('[hidden]')) continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0) continue;
    if (r.height < 43.5 || r.width < 43.5) small.push({ tag: el.tagName, cls: typeof el.className === 'string' ? el.className : '', text: el.textContent.trim().slice(0, 30), w: Math.round(r.width), h: Math.round(r.height) });
  }
  return small;
}
"""


def figs(page):
    return page.evaluate("() => Object.fromEntries([...document.querySelectorAll('#face [data-k]')].map(e => [e.dataset.k, e.textContent]))")


def shares(page):
    f = figs(page)
    return [f[k] for k in sorted((k for k in f if re.fullmatch(r"s\d+", k)), key=lambda k: int(k[1:]))]


def via_bar(page, key):
    if page.locator("#protoList").is_hidden():
        page.click("#protoTab")
    page.click(f'[data-state="{key}"]')
    page.click("#protoTab")


def shot(page, name, full=False):
    page.screenshot(path=str(HERE / f"{name}.png"), full_page=full)
    return f"{name}.png"


def dialog_open(page, sel):
    return page.evaluate("s => document.querySelector(s).open", sel)


def run_viewport(browser, w, h):
    tag = str(w)
    ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, reduced_motion="reduce")
    page = ctx.new_page()
    page.set_default_timeout(5000)
    page.on("console", lambda m: m.type == "error" and results["console_errors"].append(f"{tag}: {m.text}"))
    page.on("pageerror", lambda e: results["console_errors"].append(f"{tag}: pageerror {e}"))
    page.on("request", lambda r: (not r.url.startswith(("file:", "data:"))) and results["requests"].append(r.url))
    page.goto(URL, wait_until="load", timeout=10000)

    # ---- K1 ----
    check(f"{tag} page title", page.title() == "Danial's Splity Tab", page.title())
    brand = page.inner_text(".brand")
    check(f"{tag} header wordmark is Splity Tab only", brand.strip() == "Splity Tab", brand)
    f = figs(page)
    k1 = {"total": "69.26", "sub": "RM 59.40", "svc": "RM 5.94", "sst": "RM 3.92", "s0": "29.04", "s1": "15.74", "s2": "24.48",
          "i0": "RM 24.90", "c0": "RM 4.14", "i1": "RM 13.50", "c1": "RM 2.24", "i2": "RM 21.00", "c2": "RM 3.48", "sum": "69.26", "sp": "1 sen"}
    check(f"{tag} K1 figures", all(f.get(k) == v for k, v in k1.items()), f)
    check(f"{tag} K1 proof row working", "RM 59.40 + RM 9.86" in page.inner_text("#shares tfoot"), page.inner_text("#shares tfoot"))
    check(f"{tag} K1 spare choice shows Top of the list", "Top of the list" in page.inner_text("#spareBtn"))
    shot(page, f"k1-{tag}")
    shot(page, f"k1-{tag}-full", full=True)
    results["overflow"][f"k1-{tag}"] = page.evaluate(OVERFLOW_JS)
    results["targets"][f"k1-{tag}"] = page.evaluate(TARGETS_JS)

    # ---- P1 on K1 ----
    page.click("#spareBtn")
    page.wait_for_function("() => document.querySelector('#spareDlg').open", timeout=3000)
    shot(page, f"p1-k1-{tag}")
    page.keyboard.press("Escape")
    check(f"{tag} P1 closes on Esc", not dialog_open(page, "#spareDlg"))
    page.click("#spareBtn")
    page.click('.opt[data-rule="one"]')
    shot(page, f"p1-picker-k1-{tag}")
    page.click('[data-pick="2"]')
    check(f"{tag} K1 one person Ben gives 29.03 and 15.75", shares(page) == ["29.03", "15.75", "24.48"], shares(page))
    check(f"{tag} K1 choice label shows Ben", "One person, Ben" in page.inner_text("#spareBtn"))
    shot(page, f"p1-one-ben-k1-{tag}")
    page.click("#spareBtn")
    page.click('.opt[data-rule="random"]')
    r1 = shares(page)
    k1_random = [["29.04", "15.74", "24.48"], ["29.03", "15.75", "24.48"], ["29.03", "15.74", "24.49"]]
    check(f"{tag} K1 random gives the 1 sen to one person", r1 in k1_random, r1)
    check(f"{tag} K1 random shows Pick again", page.locator("#pickAgain").count() == 1)
    shot(page, f"p1-random-k1-{tag}")
    page.click("#pickAgain")
    r2 = shares(page)
    check(f"{tag} K1 Pick again draws again", r2 != r1 and r2 in k1_random, {"before": r1, "after": r2})
    shot(page, f"p1-pick-again-k1-{tag}")
    page.click("#spareBtn")
    page.mouse.click(4, 4)
    check(f"{tag} P1 closes on backdrop", not dialog_open(page, "#spareDlg"))

    # ---- K2 ----
    via_bar(page, "K2")
    f = figs(page)
    check(f"{tag} K2 figures", [f.get("total"), f.get("sub"), f.get("svc"), f.get("sst")] == ["116.60", "RM 100.00", "RM 10.00", "RM 6.60"]
          and shares(page) == ["38.87", "38.87", "38.86"] and f.get("sp") == "2 sen", f)
    shot(page, f"k2-{tag}")
    page.click("#spareBtn")
    shot(page, f"p1-k2-{tag}")
    page.click('.opt[data-rule="one"]')
    page.click('[data-pick="2"]')
    check(f"{tag} K2 one person Ben gives 38.86 38.88 38.86", shares(page) == ["38.86", "38.88", "38.86"], shares(page))
    shot(page, f"p1-one-ben-k2-{tag}")
    page.click("#spareBtn")
    page.click('.opt[data-rule="random"]')
    rk = shares(page)
    check(f"{tag} K2 random gives two different people one sen each", sorted(rk) == ["38.86", "38.87", "38.87"], rk)
    shot(page, f"p1-random-k2-{tag}")

    # ---- M1 ----
    via_bar(page, "K1")
    page.click("#newBill")
    page.wait_for_function("() => document.querySelector('#newDlg').open", timeout=3000)
    shot(page, f"m1-{tag}")
    tab = page.locator("#protoTab").bounding_box()
    under = page.evaluate("([x, y]) => document.elementFromPoint(x, y).id", [tab["x"] + 6, tab["y"] + 6])
    check(f"{tag} proto bar sits under the M1 backdrop", under == "newDlg", under)
    page.keyboard.press("Escape")
    check(f"{tag} M1 closes on Esc", not dialog_open(page, "#newDlg"))
    page.click("#newBill")
    page.mouse.click(4, 4)
    check(f"{tag} M1 closes on backdrop", not dialog_open(page, "#newDlg"))
    page.click("#newBill")
    page.click("#newCancel")
    check(f"{tag} M1 Cancel keeps the bill", figs(page).get("total") == "69.26")
    page.click("#newBill")
    page.click("#newGo")
    names = page.eval_on_selector_all("[data-pname]", "els => els.map(e => e.value)")
    s1ok = (names == ["Person 1", "Person 2"] and page.input_value("#subtotal") == "" and page.input_value("#r-service") == "10"
            and page.input_value("#r-sst") == "6" and page.is_checked('input[value="even"]')
            and "Enter the subtotal to see the shares." in page.inner_text("#readB"))
    check(f"{tag} Start new bill gives S1", s1ok, names)
    shot(page, f"s1-after-start-new-bill-{tag}")

    # ---- S4 via the design's own button ----
    via_bar(page, "K1")
    page.click("#copyBtn")
    check(f"{tag} Copy summary shows Summary copied", page.inner_text("#status").strip() == "Summary copied")
    page.locator("#status").scroll_into_view_if_needed()
    shot(page, f"s4-copied-via-button-{tag}")

    # ---- prototype bar ----
    page.evaluate("() => window.scrollTo(0, 0)")
    page.click("#protoTab")
    shot(page, f"proto-panel-{tag}")
    page.click("#protoTab")

    expect = {
        "S1": "Enter the subtotal to see the shares.",
        "S2": "Enter an amount like 12.50",
        "S3": "1 item still needs a person. Tap who had it to see the shares.",
        "S4ok": "Summary copied",
        "S4fail": "Could not copy. Your browser blocked the clipboard.",
        "S5": "This bill is not being saved on this device. It will be lost when you close this tab.",
        "S6": "Your saved bill could not be read, so a new one was started.",
    }
    for key in ["S1", "S2", "S3", "S4ok", "S4fail", "S5", "S6", "S7", "W1"]:
        via_bar(page, key)
        page.evaluate("() => window.scrollTo(0, 0)")
        body = page.inner_text("body")
        if key in expect:
            check(f"{tag} {key} copy", expect[key] in body, key)
        if key == "S7":
            check(f"{tag} S7 Add person disabled at 12", page.is_disabled("#addPerson") and page.locator("[data-pname]").count() == 12)
        if key == "W1":
            check(f"{tag} W1 adds up to RM 1,193.87", figs(page).get("sum") == "1,193.87" and figs(page).get("total") == "1,193.87", figs(page))
            page.locator("#face").screenshot(path=str(HERE / f"state-w1-face-{tag}.png"))
        if key in ("S4ok", "S4fail"):
            page.locator("#status").scroll_into_view_if_needed()
            shot(page, f"state-{key.lower()}-{tag}")
            page.evaluate("() => window.scrollTo(0, 0)")
        shot(page, f"state-{key.lower()}-{tag}-full", full=True)
        if key in ("S5", "S6"):
            shot(page, f"state-{key.lower()}-{tag}")
        results["overflow"][f"{key}-{tag}"] = page.evaluate(OVERFLOW_JS)
        if key == "S6":
            page.click("#dismissNote")
            check(f"{tag} S6 note dismisses", page.locator(".note").count() == 0)

    # ---- focus ring ----
    if w == 1280:
        via_bar(page, "K1")
        page.evaluate("() => { window.scrollTo(0, 0); document.activeElement && document.activeElement.blur(); }")
        page.focus("#spareBtn")
        page.keyboard.press("Shift+Tab")
        page.keyboard.press("Tab")
        shot(page, f"focus-ring-{tag}")
    ctx.close()


def run_motion(browser):
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, reduced_motion="no-preference")
    page = ctx.new_page()
    page.set_default_timeout(5000)
    page.on("console", lambda m: m.type == "error" and results["console_errors"].append(f"motion: {m.text}"))
    page.on("pageerror", lambda e: results["console_errors"].append(f"motion: pageerror {e}"))
    page.goto(URL, wait_until="load", timeout=10000)
    page.click("#spareBtn")
    page.click('.opt[data-rule="one"]')
    page.click('[data-pick="2"]')
    n = page.locator(".flip").count()
    anim = page.evaluate("() => { const e = document.querySelector('.flip'); return e ? getComputedStyle(e).animationName : null; }")
    check("motion: changed figures flip when motion is allowed", n >= 2 and anim == "flip", {"count": n, "anim": anim})
    ctx.close()
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
    page = ctx.new_page()
    page.set_default_timeout(5000)
    page.goto(URL, wait_until="load", timeout=10000)
    page.click("#spareBtn")
    page.click('.opt[data-rule="one"]')
    page.click('[data-pick="2"]')
    anim = page.evaluate("() => { const e = document.querySelector('.flip'); return e ? getComputedStyle(e).animationName : 'none'; }")
    trans = page.evaluate("() => getComputedStyle(document.querySelector('.btn')).transitionDuration")
    check("motion: reduced motion stops the flip and transitions", anim == "none" and trans in ("0s", ""), {"anim": anim, "transition": trans})
    ctx.close()


def contrast(browser):
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto(URL, wait_until="load", timeout=10000)
    names = ["page", "face", "field", "hover", "ink", "ink-2", "on-ink", "cobalt", "cobalt-press", "on-cobalt", "error", "rule-strong"]
    tok = page.evaluate("ns => Object.fromEntries(ns.map(n => [n, getComputedStyle(document.documentElement).getPropertyValue('--' + n).trim()]))", names)
    ctx.close()
    pairs = [
        ("body text: ink on page", "ink", "page", 4.5), ("body text: ink on face", "ink", "face", 4.5), ("ink on field", "ink", "field", 4.5),
        ("ink on hover", "ink", "hover", 4.5), ("muted: ink-2 on page", "ink-2", "page", 4.5), ("muted: ink-2 on face", "ink-2", "face", 4.5),
        ("muted: ink-2 on field", "ink-2", "field", 4.5), ("muted: ink-2 on hover", "ink-2", "hover", 4.5),
        ("accent text: cobalt on face", "cobalt", "face", 4.5), ("accent: cobalt on page", "cobalt", "page", 4.5),
        ("button text: on-cobalt on cobalt", "on-cobalt", "cobalt", 4.5), ("button hover: on-cobalt on cobalt-press", "on-cobalt", "cobalt-press", 4.5),
        ("selected: on-ink on ink", "on-ink", "ink", 4.5), ("error on face", "error", "face", 4.5), ("error on page", "error", "page", 4.5),
        ("error on field", "error", "field", 4.5), ("control border: rule-strong on field", "rule-strong", "field", 3.0),
        ("control border: rule-strong on page", "rule-strong", "page", 3.0), ("focus ring: cobalt on page", "cobalt", "page", 3.0),
    ]
    for label, a, b, need in pairs:
        r = ratio(tok[a], tok[b])
        results["contrast"][label] = {"fg": tok[a], "bg": tok[b], "ratio": r, "need": need, "pass": r >= need}
    results["tokens"] = tok


def main():
    static_checks()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, timeout=30000)
        try:
            for w, h in VIEWPORTS:
                run_viewport(browser, w, h)
            run_motion(browser)
            contrast(browser)
        finally:
            browser.close()
    for key, o in results["overflow"].items():
        if key.endswith("-360"):
            check(f"no sideways scroll {key}", o["scrollWidth"] <= o["clientWidth"] and not o["poking"], o)
        check(f"no clipped text {key}", not o["clipped"], o["clipped"])
    for key, t in results["targets"].items():
        check(f"44 px targets {key}", not t, t)
    check("console errors are zero", not results["console_errors"], results["console_errors"])
    check("no network requests", not results["requests"], results["requests"])
    check("all contrast pairs pass", all(v["pass"] for v in results["contrast"].values()))
    (HERE / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    failed = [c for c in results["checks"] if not c["ok"]]
    print(f"checks {len(results['checks'])}, failed {len(failed)}")
    for c in failed:
        print("FAIL", c["name"], json.dumps(c["detail"])[:600])
    print("console errors", len(results["console_errors"]))
    for k, v in results["contrast"].items():
        print(f"{k}: {v['ratio']}")


if __name__ == "__main__":
    main()
