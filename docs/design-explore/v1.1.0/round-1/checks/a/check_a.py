"""Render checks for direction A, Night Console (round 1, v1.1.0).

Opens a.html by its file:/// URL in headless Chromium at 390x844, 360x780 and 1280x800.
Saves screenshots next to this script, asserts the inventory figures, drives every popup
through the design's own controls, and records console errors, sideways scroll, touch
targets and contrast ratios in results.json. Every wait is bounded; the browser is closed
in a finally block.
"""
import json
import pathlib
import re
import sys
import urllib.request

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
HTML = HERE.parent.parent / "a.html"
URL = HTML.as_uri()
ICONS_JS = HERE.parents[5] / "src" / "ui" / "icons.js"

results = {"url": URL, "console_errors": {}, "hscroll": {}, "asserts": [], "small_targets": {},
           "contrast": {}, "icons": {}, "screens": []}
failures = []


def check(name, got, want):
    ok = got == want
    results["asserts"].append({"name": name, "ok": ok, "got": got, "want": want})
    if not ok:
        failures.append(f"{name}: got {got!r}, want {want!r}")


# ---------- contrast maths (WCAG 2.x relative luminance) ----------
def parse_color(s):
    s = s.strip()
    if s.startswith("#"):
        h = s[1:]
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (1.0,)
    m = re.match(r"rgba?\(([^)]+)\)", s)
    parts = [p.strip() for p in m.group(1).split(",")]
    a = float(parts[3]) if len(parts) > 3 else 1.0
    return (int(float(parts[0])), int(float(parts[1])), int(float(parts[2])), a)


def over(fg, bg):
    a = fg[3]
    return tuple(round(fg[i] * a + bg[i] * (1 - a)) for i in range(3)) + (1.0,)


def lum(c):
    def ch(v):
        v = v / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


# ---------- icon paths must equal Phosphor's ----------
def icon_check():
    html = HTML.read_text(encoding="utf-8")
    syms = dict(re.findall(r'<symbol id="i-([a-z-]+)" viewBox="0 0 256 256"><path d="([^"]+)"/></symbol>', html))
    ref = {}
    if ICONS_JS.exists():
        js = ICONS_JS.read_text(encoding="utf-8")
        for k, v in re.findall(r'(\w+): "([^"]+)"', js):
            ref[k] = v
    remote = {"caret": "caret-down", "shuffle": "shuffle", "warning": "warning", "warning-circle": "warning-circle",
              "receipt": "receipt", "seal-check": "seal-check"}
    for local, name in remote.items():
        try:
            with urllib.request.urlopen(f"https://unpkg.com/@phosphor-icons/core@2.1.1/assets/regular/{name}.svg", timeout=15) as r:
                svg = r.read().decode("utf-8")
            ref[local] = re.search(r'd="([^"]+)"', svg).group(1)
        except Exception as e:  # offline: record, do not fail the render checks
            results["icons"][local] = f"reference not fetched ({e.__class__.__name__})"
    for k, d in syms.items():
        if k in ref:
            results["icons"][k] = "exact" if ref[k] == d else "MISMATCH"
            if ref[k] != d:
                failures.append(f"icon {k} path differs from Phosphor")


# ---------- page helpers ----------
def shot(page, name, full=False, el=None):
    path = HERE / f"{name}.png"
    if el is not None:
        page.locator(el).screenshot(path=str(path))
    else:
        page.screenshot(path=str(path), full_page=full)
    results["screens"].append(path.name)


def hscroll(page, label):
    sw, cw = page.evaluate("[document.documentElement.scrollWidth, document.documentElement.clientWidth]")
    results["hscroll"][label] = {"scrollWidth": sw, "clientWidth": cw, "sideways": sw > cw}
    if sw > cw:
        failures.append(f"sideways scroll at {label}: {sw} > {cw}")


def texts(page, sel):
    return page.eval_on_selector_all(sel, "els => els.filter(e => e.offsetParent !== null).map(e => e.textContent.trim().replace(/\\s+/g, ' '))")


def proto(page, key):
    if page.locator("#proto-panel").is_hidden():
        page.click("#proto-toggle")
    page.click(f'#proto-panel [data-state="{key}"]')
    page.click("#proto-toggle")
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(150)


def picker_open(page):
    page.wait_for_selector("#picker:not([hidden])", timeout=3000)


def picker_closed(page):
    page.wait_for_selector("#picker", state="hidden", timeout=3000)


def small_targets(page, label):
    found = page.evaluate("""() => {
      const out = [];
      const els = document.querySelectorAll('button, input:not([type=radio]), .seg-opt');
      for (const el of els) {
        if (el.closest('.proto') || el.closest('[hidden]')) continue;
        const r = el.getBoundingClientRect();
        if (!r.width || !r.height) continue;
        if (r.height < 43.5 || r.width < 43.5) out.push((el.getAttribute('aria-label') || el.textContent.trim()).slice(0, 40) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
      }
      return out;
    }""")
    results["small_targets"][label] = found
    if found:
        failures.append(f"targets under 44 px at {label}: {found}")


def new_page(browser, w, h, label):
    ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
    page = ctx.new_page()
    page.set_default_timeout(5000)
    errs = []
    page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errs.append(str(e)))
    results["console_errors"][label] = errs
    page.goto(URL, wait_until="load", timeout=10000)
    page.wait_for_timeout(700)
    return ctx, page


def run_390(browser):
    ctx, page = new_page(browser, 390, 844, "390")
    try:
        # K1, the key screen
        shot(page, "k1-390")
        shot(page, "k1-390-full", full=True)
        check("K1 summary", texts(page, ".sum dd"), ["RM 59.40", "RM 5.94", "RM 3.92", "RM 69.26"])
        check("K1 working", texts(page, ".sum dt .work"), ["10% of RM 59.40", "6% of RM 65.34"])
        check("K1 names", texts(page, ".share .mention"), ["Aisyah", "Ben", "Chen"])
        check("K1 shares", texts(page, ".share .amt"), ["RM 29.04", "RM 15.74", "RM 24.48"])
        check("K1 share working", texts(page, ".share .work"),
              ["Items RM 24.90 + Charges RM 4.14", "Items RM 13.50 + Charges RM 2.24", "Items RM 21.00 + Charges RM 3.48"])
        check("K1 adds up", texts(page, ".proof .amt") + texts(page, ".proof .work"), ["RM 69.26", "Items RM 59.40 + Charges RM 9.86"])
        check("K1 spare line", texts(page, "#spare-count"), ["1 sen left over"])
        check("K1 spare choice", texts(page, '.seg-btn[aria-pressed="true"]'), ["Top of the list"])
        check("K1 item prices", page.eval_on_selector_all("[data-item-price]", "e => e.map(x => x.value)"), ["15.90", "13.50", "12.00", "18.00"])
        small_targets(page, "390 K1")

        # P1 on K1: One person opens the picker; Esc, the backdrop and Close all close it
        page.click('[data-spare="one"]')
        picker_open(page)
        page.wait_for_timeout(250)
        shot(page, "p1-picker-k1-390")
        page.keyboard.press("Escape")
        picker_closed(page)
        check("P1 Esc keeps Top of the list", texts(page, '.seg-btn[aria-pressed="true"]'), ["Top of the list"])
        page.click('[data-spare="one"]')
        picker_open(page)
        page.mouse.click(195, 60)
        picker_closed(page)
        page.click('[data-spare="one"]')
        picker_open(page)
        page.click("#picker-x")
        picker_closed(page)
        page.click('[data-spare="one"]')
        picker_open(page)
        page.click('[data-pick="2"]')
        picker_closed(page)
        page.wait_for_timeout(1000)
        check("K1 one person Ben", texts(page, ".share .amt"), ["RM 29.03", "RM 15.75", "RM 24.48"])
        shot(page, "p1-one-person-k1-390", el="#msg")
        page.click("[data-open-picker]")
        picker_open(page)
        page.keyboard.press("Escape")
        picker_closed(page)

        page.click('[data-spare="random"]')
        page.wait_for_timeout(1000)
        r1 = texts(page, ".share .amt")
        shot(page, "p1-random-k1-390", el="#msg")
        page.click("[data-again]")
        page.wait_for_timeout(1000)
        r2 = texts(page, ".share .amt")
        shot(page, "p1-pick-again-k1-390", el="#msg")
        cents = lambda xs: sum(int(x.replace("RM ", "").replace(",", "").replace(".", "")) for x in xs)
        check("K1 random adds up", cents(r1), 6926)
        check("K1 pick again adds up", cents(r2), 6926)
        check("K1 pick again changes the draw", r1 != r2, True)
        results["k1_random_draws"] = [r1, r2]

        # K2 through the design's own mode switch
        proto(page, "K1")
        page.click('label.seg-opt:has(input[value="even"])')
        page.wait_for_timeout(1000)
        check("K2 summary", texts(page, ".sum dd"), ["RM 100.00", "RM 10.00", "RM 6.60", "RM 116.60"])
        check("K2 working", texts(page, ".sum dt .work"), ["10% of RM 100.00", "6% of RM 110.00"])
        check("K2 shares", texts(page, ".share .amt"), ["RM 38.87", "RM 38.87", "RM 38.86"])
        check("K2 adds up", texts(page, ".proof .amt"), ["RM 116.60"])
        check("K2 spare line", texts(page, "#spare-count"), ["2 sen left over"])
        check("K2 subtotal field", page.input_value("#subtotal"), "100.00")
        shot(page, "k2-390")
        shot(page, "k2-390-full", full=True)
        page.click('[data-spare="one"]')
        picker_open(page)
        page.wait_for_timeout(250)
        shot(page, "p1-picker-k2-390")
        page.click('[data-pick="2"]')
        picker_closed(page)
        page.wait_for_timeout(1000)
        check("K2 one person Ben", texts(page, ".share .amt"), ["RM 38.86", "RM 38.88", "RM 38.86"])
        page.click('[data-spare="random"]')
        page.wait_for_timeout(1000)
        k2r = texts(page, ".share .amt")
        check("K2 random gives two different people one sen", sorted(k2r), ["RM 38.86", "RM 38.87", "RM 38.87"])
        shot(page, "p1-random-k2-390", el="#msg")
        page.click("[data-again]")
        page.wait_for_timeout(1000)
        k2r2 = texts(page, ".share .amt")
        check("K2 pick again still two different people", sorted(k2r2), ["RM 38.86", "RM 38.87", "RM 38.87"])
        check("K2 pick again changes the draw", k2r != k2r2, True)
        results["k2_random_draws"] = [k2r, k2r2]

        # M1 through New bill; Esc, backdrop and Cancel close it; Start new bill resets
        proto(page, "K1")
        page.click("#new-bill")
        page.wait_for_selector("#m1[open]", timeout=3000)
        page.wait_for_timeout(250)
        shot(page, "m1-390")
        check("M1 copy", texts(page, "#m1 .modal-title, #m1 .modal-text, #m1 button"),
              ["Start a new bill?", "This clears the people, items and amounts.", "Cancel", "Start new bill"])
        page.keyboard.press("Escape")
        page.wait_for_selector("#m1:not([open])", state="attached", timeout=3000)
        page.click("#new-bill")
        page.wait_for_selector("#m1[open]", timeout=3000)
        page.mouse.click(8, 8)
        page.wait_for_selector("#m1:not([open])", state="attached", timeout=3000)
        page.click("#new-bill")
        page.wait_for_selector("#m1[open]", timeout=3000)
        page.click("#m1-cancel")
        page.wait_for_selector("#m1:not([open])", state="attached", timeout=3000)
        check("M1 Cancel keeps the bill", texts(page, ".share .amt"), ["RM 29.04", "RM 15.74", "RM 24.48"])
        page.click("#new-bill")
        page.wait_for_selector("#m1[open]", timeout=3000)
        page.click("#m1-start")
        page.wait_for_selector("#m1:not([open])", state="attached", timeout=3000)
        page.wait_for_timeout(300)
        check("Start new bill gives S1 people", page.eval_on_selector_all("[data-person]", "e => e.map(x => x.value)"), ["Person 1", "Person 2"])
        check("Start new bill gives S1 message", texts(page, ".bot-line"), ["Enter the subtotal to see the shares."])
        shot(page, "s1-after-start-new-bill-390", full=True)

        # Copy summary through the design's own button
        proto(page, "K1")
        page.click("#copy")
        page.wait_for_timeout(200)
        check("S4 copied", texts(page, "#status"), ["Summary copied"])
        shot(page, "s4-copied-390", el="#msg")

        # The prototype bar itself
        page.click("#proto-toggle")
        page.wait_for_timeout(150)
        shot(page, "proto-panel-390")
        page.click("#proto-toggle")

        # States with no natural trigger
        proto(page, "S1")
        check("S1 people", page.eval_on_selector_all("[data-person]", "e => e.map(x => x.value)"), ["Person 1", "Person 2"])
        check("S1 removes disabled", page.eval_on_selector_all("[data-remove-person]", "e => e.map(x => x.disabled)"), [True, True])
        check("S1 mode Even", page.is_checked('input[name="mode"][value="even"]'), True)
        check("S1 subtotal empty", page.input_value("#subtotal"), "")
        check("S1 rates", [page.input_value("#svc"), page.input_value("#sst")], ["10", "6"])
        check("S1 message", texts(page, ".bot-line"), ["Enter the subtotal to see the shares."])
        shot(page, "state-s1-390", full=True)

        proto(page, "S2")
        check("S2 error", texts(page, "#subtotal-err"), ["Enter an amount like 12.50"])
        check("S2 aria-invalid", page.get_attribute("#subtotal", "aria-invalid"), "true")
        shot(page, "state-s2-390", full=True)

        proto(page, "S3")
        check("S3 message", texts(page, ".bot-line"), ["1 item still needs a person. Tap who had it to see the shares."])
        check("S3 summary still shows", texts(page, ".sum-total dd"), ["RM 69.26"])
        shot(page, "state-s3-390", full=True)

        proto(page, "S4ok")
        check("S4 ok", texts(page, "#status"), ["Summary copied"])
        shot(page, "state-s4-copied-390", el="#msg")
        proto(page, "S4fail")
        check("S4 fail", texts(page, "#status"), ["Could not copy. Your browser blocked the clipboard."])
        shot(page, "state-s4-failed-390", el="#msg")

        proto(page, "S5")
        check("S5 note", texts(page, "#n-save p"), ["This bill is not being saved on this device. It will be lost when you close this tab."])
        check("S5 has no dismiss", page.locator("#n-save button").count(), 0)
        shot(page, "state-s5-390")

        proto(page, "S6")
        check("S6 note", texts(page, "#n-unread p"), ["Your saved bill could not be read, so a new one was started."])
        shot(page, "state-s6-390")
        page.click("#n-unread-x")
        check("S6 dismiss hides the note", page.locator("#n-unread").is_hidden(), True)

        proto(page, "S7")
        check("S7 twelve people", page.locator("[data-person]").count(), 12)
        check("S7 Add person disabled", page.is_disabled("#add-person"), True)
        shot(page, "state-s7-390", full=True)

        proto(page, "W1")
        check("W1 total", texts(page, ".sum-total dd"), ["RM 1,193.87"])
        check("W1 shares", texts(page, ".share .amt"), ["RM 29.04", "RM 1,140.35", "RM 24.48"])
        check("W1 adds up", texts(page, ".proof .work"), ["Items RM 1,023.90 + Charges RM 169.97"])
        shot(page, "state-w1-390", full=True)
        hscroll(page, "390 W1")
    finally:
        ctx.close()


def run_360(browser):
    ctx, page = new_page(browser, 360, 780, "360")
    try:
        shot(page, "k1-360")
        shot(page, "k1-360-full", full=True)
        hscroll(page, "360 K1")
        small_targets(page, "360 K1")
        for key in ["K2", "S1", "S2", "S3", "S4fail", "S5", "S6", "S7", "W1"]:
            proto(page, key)
            hscroll(page, f"360 {key}")
        shot(page, "state-w1-360-full", full=True)
        shot(page, "state-w1-360-shares", el="#msg")
        # rows must stay inside the embed at 360 even with RM 1,193.87
        over = page.evaluate("""() => {
          const out = [];
          for (const el of document.querySelectorAll('.embed *, .msg-comp *, .msg-actions *')) {
            const r = el.getBoundingClientRect();
            if (r.width && (r.right > document.documentElement.clientWidth + 0.5 || r.left < -0.5)) out.push(el.className || el.tagName);
          }
          return out;
        }""")
        results["w1_360_out_of_view"] = over
        if over:
            failures.append(f"W1 at 360: elements outside the viewport {over[:5]}")
        proto(page, "K1")
        page.click('[data-spare="one"]')
        picker_open(page)
        page.wait_for_timeout(250)
        hscroll(page, "360 P1 open")
        shot(page, "p1-picker-360")
        page.keyboard.press("Escape")
        picker_closed(page)
        page.click("#new-bill")
        page.wait_for_selector("#m1[open]", timeout=3000)
        page.wait_for_timeout(250)
        hscroll(page, "360 M1 open")
        shot(page, "m1-360")
        page.keyboard.press("Escape")
        page.click("#proto-toggle")
        hscroll(page, "360 prototype panel open")
        page.click("#proto-toggle")
    finally:
        ctx.close()


def run_1280(browser):
    ctx, page = new_page(browser, 1280, 800, "1280")
    try:
        shot(page, "k1-1280")
        hscroll(page, "1280 K1")
        small_targets(page, "1280 K1")
        page.click('[data-spare="one"]')
        picker_open(page)
        page.wait_for_timeout(250)
        shot(page, "p1-picker-1280")
        page.mouse.click(20, 780)
        picker_closed(page)
        page.click('[data-spare="random"]')
        page.wait_for_timeout(1000)
        shot(page, "p1-random-1280")
        proto(page, "K1")
        page.click("#new-bill")
        page.wait_for_selector("#m1[open]", timeout=3000)
        page.wait_for_timeout(250)
        shot(page, "m1-1280")
        page.keyboard.press("Escape")
        for key in ["K2", "S1", "S3", "S5", "S6", "S7", "W1"]:
            proto(page, key)
            hscroll(page, f"1280 {key}")
            shot(page, f"state-{key.lower()}-1280")
        proto(page, "S4fail")
        shot(page, "state-s4-failed-1280")
        proto(page, "K1")
        page.keyboard.press("Tab")
        page.keyboard.press("Tab")
        page.wait_for_timeout(150)
        shot(page, "focus-ring-1280")

        # contrast, from the live tokens
        v = page.evaluate("""() => {
          const cs = getComputedStyle(document.documentElement);
          const names = ['--l0','--l1','--l2','--l3','--l4','--l5','--field','--line-strong','--text','--text-muted','--accent','--accent-ink',
                         '--accent-line','--accent-tint','--on-accent','--danger','--on-danger','--error-ink','--warn-ink','--warn-bg','--info-bg','--focus'];
          const o = {}; for (const n of names) o[n] = cs.getPropertyValue(n).trim();
          o.bodyColor = getComputedStyle(document.body).color; o.bodyBg = getComputedStyle(document.body).backgroundColor;
          return o;
        }""")
        c = {k: parse_color(x) for k, x in v.items()}
        tint_l4 = over(c["--accent-tint"], c["--l4"])
        tint_l2 = over(c["--accent-tint"], c["--l2"])
        pairs = {
            "body text on its background (live computed)": (c["bodyColor"], c["bodyBg"], 4.5),
            "text on l1 people pane": (c["--text"], c["--l1"], 4.5),
            "text on l2 bill pane": (c["--text"], c["--l2"], 4.5),
            "text on l3 chat pane": (c["--text"], c["--l3"], 4.5),
            "text on l4 embed": (c["--text"], c["--l4"], 4.5),
            "muted on l1": (c["--text-muted"], c["--l1"], 4.5),
            "muted on l2": (c["--text-muted"], c["--l2"], 4.5),
            "muted on l3": (c["--text-muted"], c["--l3"], 4.5),
            "muted on l4 embed": (c["--text-muted"], c["--l4"], 4.5),
            "muted on accent tint (proof working)": (c["--text-muted"], tint_l4, 4.5),
            "accent ink on l3 (bot name)": (c["--accent-ink"], c["--l3"], 4.5),
            "accent ink on l4 embed": (c["--accent-ink"], c["--l4"], 4.5),
            "accent ink on accent tint (mentions, proof)": (c["--accent-ink"], tint_l4, 4.5),
            "text on accent tint (tapped chip)": (c["--text"], tint_l2, 4.5),
            "on-accent on accent (Copy summary, chosen)": (c["--on-accent"], c["--accent"], 4.5),
            "on-danger on danger (Start new bill)": (c["--on-danger"], c["--danger"], 4.5),
            "error ink on l2": (c["--error-ink"], c["--l2"], 4.5),
            "error ink on l3": (c["--error-ink"], c["--l3"], 4.5),
            "text on warn bar": (c["--text"], c["--warn-bg"], 4.5),
            "text on info bar": (c["--text"], c["--info-bg"], 4.5),
            "control border on field": (c["--line-strong"], c["--field"], 3.0),
            "control border on l1": (c["--line-strong"], c["--l1"], 3.0),
            "control border on l2": (c["--line-strong"], c["--l2"], 3.0),
            "control border on l3": (c["--line-strong"], c["--l3"], 3.0),
            "control border on l4": (c["--line-strong"], c["--l4"], 3.0),
            "chosen fill (accent) on field track": (c["--accent"], c["--field"], 3.0),
            "tapped chip border on l2": (c["--accent-line"], c["--l2"], 3.0),
            "focus ring on l0": (c["--focus"], c["--l0"], 3.0),
            "focus ring on l2": (c["--focus"], c["--l2"], 3.0),
            "focus ring on l4": (c["--focus"], c["--l4"], 3.0),
            "warn icon on warn bar": (c["--warn-ink"], c["--warn-bg"], 3.0),
        }
        for k, (fg, bg, need) in pairs.items():
            r = ratio(fg, bg)
            results["contrast"][k] = {"ratio": r, "need": need, "pass": r >= need}
            if r < need:
                failures.append(f"contrast {k}: {r} < {need}")
    finally:
        ctx.close()


def run_1024_reduced(browser):
    """In-between width (two panes) with reduced motion on: no errors, no sideways scroll."""
    ctx = browser.new_context(viewport={"width": 1024, "height": 768}, device_scale_factor=1, reduced_motion="reduce")
    page = ctx.new_page()
    errs = []
    page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errs.append(str(e)))
    results["console_errors"]["1024 reduced motion"] = errs
    try:
        page.set_default_timeout(5000)
        page.goto(URL, wait_until="load", timeout=10000)
        page.wait_for_timeout(300)
        anim = page.evaluate("getComputedStyle(document.getElementById('msg')).animationName")
        check("reduced motion: no entrance animation", anim, "none")
        shot(page, "k1-1024-reduced-motion")
        hscroll(page, "1024 K1")
    finally:
        ctx.close()


def main():
    icon_check()
    browser = None
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            run_390(browser)
            run_360(browser)
            run_1280(browser)
            run_1024_reduced(browser)
        finally:
            if browser is not None:
                browser.close()
    for label, errs in results["console_errors"].items():
        if errs:
            failures.append(f"console errors at {label}: {errs}")
    results["failures"] = failures
    (HERE / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps({"failures": failures, "console_errors": results["console_errors"], "hscroll": results["hscroll"],
                      "contrast": {k: v["ratio"] for k, v in results["contrast"].items()}, "icons": results["icons"],
                      "small_targets": results["small_targets"], "draws": [results.get("k1_random_draws"), results.get("k2_random_draws")]}, indent=1))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
