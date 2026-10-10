"""Render check for round-1 direction B (Glass Receipt).

Opens b.html by its file:/// URL in headless Chromium (no server, no network), at 390x844, 360x780 and 1280x800.
Saves screenshots beside this script, checks every inventory figure, console errors, sideways scroll at 360,
dialog close paths (Esc and backdrop), icon paths against the Phosphor copies, and contrast ratios.
Every wait is bounded. The browser is closed in a finally block.
"""
import json
import pathlib
import re
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
ROUND = HERE.parent.parent
PAGE = ROUND / "b.html"
A_PAGE = ROUND / "a.html"
ICONS_JS = ROUND.parent.parent.parent.parent / "src" / "ui" / "icons.js"
URL = PAGE.as_uri()
T = 5000  # ms, every wait is bounded by this

console_errors = []
failures = []
notes = []
hscroll = {}


def check(cond, msg):
    (notes if cond else failures).append(("ok  " if cond else "FAIL ") + msg)


# ---------- contrast ----------
def hex_rgb(h):
    h = h.strip().lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def parse_css_color(s):
    m = re.match(r"rgba?\(([^)]+)\)", s.strip())
    if m:
        parts = [float(x) for x in m.group(1).replace("/", ",").split(",")]
        return tuple(int(round(p)) for p in parts[:3]), (parts[3] if len(parts) > 3 else 1.0)
    return hex_rgb(s), 1.0


def chan(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(rgb):
    r, g, b = (chan(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


def blend(fg, alpha, bg):
    return tuple(int(round(fg[i] * alpha + bg[i] * (1 - alpha))) for i in range(3))


def tokens():
    css = PAGE.read_text(encoding="utf-8")
    root = css[css.index(":root{"):css.index("}", css.index(":root{"))]
    out = {}
    for name, val in re.findall(r"--([a-z0-9-]+):([^;]+);", root):
        out[name] = val.strip()
    return out


# ---------- page helpers ----------
def wait_settled(page, ms=250):
    page.wait_for_timeout(ms)


def proto(page, sid):
    if page.is_hidden("#protoList"):
        page.click("#protoToggle", timeout=T)
    page.click(f"[data-state='{sid}']", timeout=T)
    if page.is_visible("#protoList"):
        page.click("#protoToggle", timeout=T)
    wait_settled(page)


def shares(page):
    return page.eval_on_selector_all(
        "#shares li",
        "els => els.map(e => [e.querySelector('.nm').textContent, e.querySelector('.amt').textContent,"
        " ((e.querySelector('.wk') || {}).textContent || '').replace('Items ', '').replace('charges ', '')])",
    )


def text(page, sel):
    return page.inner_text(sel, timeout=T).strip()


def scroll_x(page):
    """Sideways scroll, plus any element poking past the viewport (the app clips overflow, so scrollWidth alone hides it)."""
    sw = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    out = page.evaluate("""(() => {
      const W = document.documentElement.clientWidth;
      return [...document.querySelectorAll('.bar *, .notes *, .work *, #rbody *')]
        .filter(e => !e.closest('.sr') && !e.closest('[hidden]') && e.getClientRects().length)
        .filter(e => { const r = e.getBoundingClientRect(); return r.right > W + 0.5 || r.left < -0.5; })
        .map(e => (e.id || e.className || e.tagName) + '').slice(0, 5);
    })()""")
    return max(sw, 0) + len(out), out


def no_overlap(page, a, b):
    return page.evaluate(f"""(() => {{
      const x = document.querySelector('{a}').getBoundingClientRect(), y = document.querySelector('{b}').getBoundingClientRect();
      return x.right <= y.left || y.right <= x.left || x.bottom <= y.top || y.bottom <= x.top;
    }})()""")


def dlg_open(page, id_):
    return page.evaluate(f"document.getElementById('{id_}').open")


def shot(page, name, full=False):
    page.screenshot(path=str(HERE / name), full_page=full, timeout=T)


def check_k1(page, tag):
    check(text(page, ".r-amount") == "RM 69.26", f"{tag} total RM 69.26")
    lines = page.eval_on_selector_all(".r-lines div", "els => els.map(e => e.innerText.replace(/\\s+/g, ' ').trim())")
    check(lines == ["Subtotal RM 59.40", "Service 10% RM 5.94", "SST 6% RM 3.92"], f"{tag} bill lines {lines}")
    s = shares(page)
    want = [["Aisyah", "RM 29.04", "24.90 + 4.14"], ["Ben", "RM 15.74", "13.50 + 2.24"], ["Chen", "RM 24.48", "21.00 + 3.48"]]
    check(s == want, f"{tag} shares {s}")
    check(text(page, ".r-check .amt") == "RM 69.26" and text(page, ".r-check .wk") == "59.40 + 9.86", f"{tag} adds up to RM 59.40 + RM 9.86 = RM 69.26")
    check(text(page, ".r-spare p") == "1 sen left over", f"{tag} 1 sen left over")
    check(text(page, "#spareBtn") == "Top of the list", f"{tag} Top of the list chosen")


def check_k2(page, tag):
    check(text(page, ".r-amount") == "RM 116.60", f"{tag} total RM 116.60")
    lines = page.eval_on_selector_all(".r-lines div", "els => els.map(e => e.innerText.replace(/\\s+/g, ' ').trim())")
    check(lines == ["Subtotal RM 100.00", "Service 10% RM 10.00", "SST 6% RM 6.60"], f"{tag} bill lines {lines}")
    s = [x[1] for x in shares(page)]
    check(s == ["RM 38.87", "RM 38.87", "RM 38.86"], f"{tag} shares {s}")
    check(text(page, ".r-spare p") == "2 sen left over", f"{tag} 2 sen left over")
    check(text(page, "#spareBtn") == "Top of the list", f"{tag} Top of the list chosen")


def open_spare(page):
    page.click("#spareBtn", timeout=T)
    page.wait_for_function("document.getElementById('spareDlg').open", timeout=T)
    wait_settled(page, 300)


def choose(page, rule):
    page.click(f"#spareDlg label.choice:has(input[value='{rule}'])", timeout=T)
    wait_settled(page, 200)


def pick_person(page, name):
    page.click(f"#pickList label.pill:has-text('{name}')", timeout=T)
    wait_settled(page, 200)


def load(page, w, h):
    page.set_viewport_size({"width": w, "height": h})
    page.goto(URL, timeout=15000)
    page.wait_for_selector("#shares", timeout=T)
    page.wait_for_timeout(2200)  # the one load sweep is 1.7 s


def run_390(page):
    load(page, 390, 844)
    check_k1(page, "K1@390")
    shot(page, "k1-390.png")
    shot(page, "k1-390-full.png", full=True)

    # P1 on K1: open, one person (Ben), at random, pick again, Esc
    open_spare(page)
    shot(page, "p1-k1-open-390.png")
    choose(page, "one")
    shot(page, "p1-k1-one-person-picker-390.png")
    pick_person(page, "Ben")
    s = [x[1] for x in shares(page)]
    check(s == ["RM 29.03", "RM 15.75", "RM 24.48"], f"P1 K1 one person Ben {s}")
    shot(page, "p1-k1-one-ben-390.png")
    choose(page, "random")
    s_rand = [x[1] for x in shares(page)]
    check(sum(int(x[3:].replace('.', '').replace(',', '')) for x in s_rand) == 6926, f"P1 K1 random still adds up {s_rand}")
    check(page.is_visible("#randWrap button"), "P1 K1 random shows Pick again in the sheet")
    shot(page, "p1-k1-random-390.png")
    page.keyboard.press("Escape")
    wait_settled(page)
    check(not dlg_open(page, "spareDlg"), "P1 closes on Esc")
    check(page.is_visible("#pickAgain"), "At random shows Pick again on the receipt")
    check(text(page, "#spareBtn") == "At random", "chip reads At random")
    before = [x[1] for x in shares(page)]
    page.click("#pickAgain", timeout=T)
    wait_settled(page)
    after = [x[1] for x in shares(page)]
    check(before != after, f"Pick again draws again {before} -> {after}")
    shot(page, "p1-k1-pick-again-390.png")

    # K2 through the design's own mode switch
    proto(page, "k1")
    page.click("label[for='modeEven']", timeout=T)
    wait_settled(page)
    check_k2(page, "K2@390 via mode switch")
    page.evaluate("scrollTo(0,0)")
    shot(page, "k2-390.png")
    open_spare(page)
    choose(page, "one")
    pick_person(page, "Ben")
    s = [x[1] for x in shares(page)]
    check(s == ["RM 38.86", "RM 38.88", "RM 38.86"], f"P1 K2 one person Ben {s}")
    shot(page, "p1-k2-one-ben-390.png")
    choose(page, "random")
    s = [int(x[1][3:].replace('.', '')) for x in shares(page)]
    plus_one = [v for v in s if v == 3887]
    check(sum(s) == 11660 and len(plus_one) == 2 and s != [3887, 3887, 3886], f"P1 K2 random gives two different people one sen each {s}")
    shot(page, "p1-k2-random-390.png")
    page.mouse.click(195, 30)  # the backdrop above the sheet
    wait_settled(page)
    check(not dlg_open(page, "spareDlg"), "P1 closes on a backdrop click")

    # M1: Esc, backdrop, Cancel, then Start new bill
    proto(page, "k1")
    page.click("#newBill", timeout=T)
    page.wait_for_function("document.getElementById('newDlg').open", timeout=T)
    wait_settled(page, 300)
    check(text(page, "#newTitle") == "Start a new bill?" and text(page, "#newBody") == "This clears the people, items and amounts.", "M1 copy")
    shot(page, "m1-390.png")
    page.keyboard.press("Escape")
    wait_settled(page)
    check(not dlg_open(page, "newDlg"), "M1 closes on Esc")
    page.click("#newBill", timeout=T)
    wait_settled(page, 300)
    page.mouse.click(8, 8)
    wait_settled(page)
    check(not dlg_open(page, "newDlg"), "M1 closes on a backdrop click")
    page.click("#newBill", timeout=T)
    wait_settled(page, 300)
    page.click("#newDlg [data-close]", timeout=T)
    wait_settled(page)
    check(not dlg_open(page, "newDlg"), "M1 closes on Cancel")
    page.click("#newBill", timeout=T)
    wait_settled(page, 300)
    page.click("#startNew", timeout=T)
    wait_settled(page)
    check(text(page, ".r-empty p") == "Enter the subtotal to see the shares.", "Start new bill gives S1")
    shot(page, "s1-after-start-new-bill-390.png")

    # Copy summary, the design's own control
    proto(page, "k1")
    page.click("#copyBtn", timeout=T)
    wait_settled(page)
    check(text(page, ".status") == "Summary copied", "Copy summary shows Summary copied")
    shot(page, "s4-copied-via-button-390.png")

    # Prototype states panel, over the page and under a dialog
    page.evaluate("scrollTo(0,0)")
    page.click("#protoToggle", timeout=T)
    wait_settled(page)
    shot(page, "proto-panel-390.png")
    page.click("#protoToggle", timeout=T)
    page.click("#newBill", timeout=T)
    wait_settled(page, 300)
    page.click("#protoToggle", force=True, timeout=T)  # lands on the backdrop, which closes the dialog
    wait_settled(page)
    check(page.is_hidden("#protoList") and not dlg_open(page, "newDlg"), "Prototype bar sits under the dialog backdrop")

    # every state
    for sid in ["s1", "s2", "s3", "s4fail", "s5", "s6", "s7", "w1"]:
        proto(page, sid)
        page.evaluate("scrollTo(0,0)")
        if sid == "s2":
            page.locator("#evenErr").scroll_into_view_if_needed(timeout=T)
            check(text(page, "#evenErr") == "Enter an amount like 12.50", "S2 error copy under the field")
            check(page.get_attribute("#evenSub", "aria-invalid") == "true", "S2 field marked invalid")
            page.evaluate("scrollBy(0, 120)")
        if sid == "s1":
            names = page.eval_on_selector_all("#peopleList input", "els => els.map(e => e.value)")
            check(names == ["Person 1", "Person 2"], f"S1 people {names}")
            check(page.is_checked("#modeEven") and page.input_value("#evenSub") == "" and page.input_value("#svc") == "10" and page.input_value("#sst") == "6", "S1 Even, empty subtotal, 10% and 6%")
            check(text(page, ".r-empty p") == "Enter the subtotal to see the shares.", "S1 message")
            check(page.is_disabled("[data-remove-person]"), "S1 remove disabled at 2 people")
        if sid == "s3":
            check(text(page, ".r-msg p") == "1 item still needs a person. Tap who had it to see the shares.", "S3 message")
        if sid == "s4fail":
            check(text(page, ".status") == "Could not copy. Your browser blocked the clipboard.", "S4 failure copy")
            page.locator(".status").scroll_into_view_if_needed(timeout=T)
        if sid == "s5":
            check(text(page, ".note p") == "This bill is not being saved on this device. It will be lost when you close this tab.", "S5 copy")
            check(page.query_selector(".note button") is None, "S5 cannot be dismissed")
        if sid == "s6":
            check(text(page, ".note p") == "Your saved bill could not be read, so a new one was started.", "S6 copy")
            shot(page, f"state-{sid}-390.png")
            page.click("#dismissNote", timeout=T)
            wait_settled(page)
            check(page.query_selector(".note") is None, "S6 dismiss works")
            continue
        if sid == "s7":
            check(page.locator("#peopleList input").count() == 12 and page.is_disabled("#addPerson"), "S7 12 people, Add person disabled")
            shot(page, f"state-{sid}-390-full.png", full=True)
            page.locator("#addPerson").scroll_into_view_if_needed(timeout=T)
        if sid == "w1":
            check(text(page, ".r-amount") == "RM 1,193.87" and text(page, ".r-check .amt") == "RM 1,193.87", "W1 reaches RM 1,193.87")
        shot(page, f"state-{sid}-390.png")


def run_360(page):
    load(page, 360, 780)
    check_k1(page, "K1@360")
    shot(page, "k1-360.png")
    shot(page, "k1-360-full.png", full=True)
    hscroll["k1"] = scroll_x(page)
    for sid in ["k2", "s1", "s2", "s3", "s4ok", "s4fail", "s5", "s6", "s7", "w1"]:
        proto(page, sid)
        hscroll[sid] = scroll_x(page)
    proto(page, "w1")
    page.evaluate("scrollTo(0,0)")
    shot(page, "state-w1-360.png")
    shot(page, "state-w1-360-full.png", full=True)
    widths = page.evaluate("[...document.querySelectorAll('#rbody *')].filter(e => !e.closest('.sr') && e.scrollWidth > e.clientWidth + 1 && getComputedStyle(e).overflow !== 'visible').length")
    check(widths == 0, "W1 nothing clipped inside the receipt at 360")
    over = page.evaluate("(() => { const r = document.getElementById('receipt').getBoundingClientRect(); return [...document.querySelectorAll('#rbody .amt, #rbody .r-amount, #rbody .wk')].filter(e => e.getBoundingClientRect().right > r.right - 1).length; })()")
    check(over == 0, "W1 every figure inside the card at 360")
    proto(page, "w1")
    page.click("#spareBtn", timeout=T)
    wait_settled(page, 300)
    hscroll["p1-open"] = scroll_x(page)
    shot(page, "p1-w1-360.png")
    page.keyboard.press("Escape")
    proto(page, "k1")
    page.click("#newBill", timeout=T)
    wait_settled(page, 300)
    shot(page, "m1-360.png")
    page.keyboard.press("Escape")
    check(all(v[0] <= 0 for v in hscroll.values()), f"no sideways scroll and nothing past the edge at 360 {hscroll}")
    page.set_viewport_size({"width": 390, "height": 844})
    for sid in ["k1", "k2", "s1", "s2", "s5", "s7", "w1"]:
        proto(page, sid)
        v = scroll_x(page)
        check(v[0] <= 0, f"nothing past the edge at 390 in {sid} {v}")


def run_768(page):
    load(page, 768, 1024)
    shot(page, "k1-768.png")
    open_spare(page)
    check(no_overlap(page, "#spareDlg", "#shares"), "P1 at 768 does not cover the shares")
    shot(page, "p1-k1-768.png")
    page.keyboard.press("Escape")


def run_1280(page):
    load(page, 1280, 800)
    check_k1(page, "K1@1280")
    shot(page, "k1-1280.png")
    shot(page, "k1-1280-full.png", full=True)
    open_spare(page)
    check(no_overlap(page, "#spareDlg", "#shares"), "P1 at 1280 does not cover the shares")
    choose(page, "one")
    pick_person(page, "Ben")
    check(no_overlap(page, "#spareDlg", "#shares"), "P1 at 1280 still clear of the shares after the picker opens")
    shot(page, "p1-k1-one-person-1280.png")
    choose(page, "random")
    shot(page, "p1-k1-random-1280.png")
    page.mouse.click(1200, 60)
    wait_settled(page)
    check(not dlg_open(page, "spareDlg"), "P1 closes on a backdrop click at 1280")
    proto(page, "k1")
    page.click("#newBill", timeout=T)
    wait_settled(page, 300)
    shot(page, "m1-1280.png")
    page.keyboard.press("Escape")
    wait_settled(page)
    for sid in ["k2", "s1", "s3", "s5", "s6", "s7", "w1", "s4fail"]:
        proto(page, sid)
        page.evaluate("scrollTo(0,0)")
        shot(page, f"state-{sid}-1280.png")
    # keyboard focus ring
    proto(page, "k1")
    page.evaluate("scrollTo(0,0)")
    page.mouse.click(5, 300)
    for _ in range(3):
        page.keyboard.press("Tab")
    shot(page, "focus-ring-1280.png")
    focused = page.evaluate("document.activeElement.id || document.activeElement.className")
    notes.append(f"info focus after 3 tabs: {focused}")


def run_reduced(browser):
    ctx = browser.new_context(viewport={"width": 1280, "height": 800}, reduced_motion="reduce")
    try:
        page = ctx.new_page()
        page.on("pageerror", lambda e: console_errors.append(str(e)))
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        cdp = ctx.new_cdp_session(page)
        cdp.send("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-reduced-transparency", "value": "reduce"}, {"name": "prefers-reduced-motion", "value": "reduce"}]})
        page.goto(URL, timeout=15000)
        page.wait_for_selector("#shares", timeout=T)
        page.wait_for_timeout(200)
        bf = page.evaluate("getComputedStyle(document.getElementById('receipt')).backdropFilter")
        anim = page.evaluate("getComputedStyle(document.querySelector('.foil')).animationName")
        check(bf == "none", f"reduced transparency gives a solid card (backdrop-filter {bf})")
        check(anim == "none", f"reduced motion stops the load sweep (animation {anim})")
        shot(page, "k1-1280-reduced-transparency-and-motion.png")
    finally:
        ctx.close()


def contrast(page):
    tk = tokens()
    nav1, nav2, nav3 = hex_rgb(tk["navy-1"]), hex_rgb(tk["navy-2"]), hex_rgb(tk["navy-3"])
    ink, muted, cyan = hex_rgb(tk["ink"]), hex_rgb(tk["ink-muted"]), hex_rgb(tk["cyan"])
    tint = blend((98, 214, 232), 0.14, nav1)
    out = {
        "ink on navy (body text)": ratio(ink, nav1),
        "ink-muted on navy": ratio(muted, nav1),
        "cyan accent on navy": ratio(cyan, nav1),
        "on-cyan text on cyan button": ratio(hex_rgb(tk["on-cyan"]), cyan),
        "ink on dialog navy-2": ratio(ink, nav2),
        "ink-muted on dialog navy-2": ratio(muted, nav2),
        "ink-muted on hover navy-3": ratio(muted, nav3),
        "error on navy": ratio(hex_rgb(tk["error"]), nav1),
        "error on navy-2": ratio(hex_rgb(tk["error"]), nav2),
        "ink on toggle-on tint": ratio(ink, tint),
        "control border (line) on navy, 3:1": ratio(hex_rgb(tk["line"]), nav1),
        "focus ring on navy, 3:1": ratio(hex_rgb(tk["focus"]), nav1),
        "warn icon on navy-2, 3:1": ratio(hex_rgb(tk["warn"]), nav2),
    }
    # The glass. Hide the card's text, screenshot, then for every text element read the BRIGHTEST pixel inside its
    # own box (the worst case for light text) and compare it with that element's computed colour.
    worst = {}
    for vw, vh, sid in [(390, 844, "k1"), (360, 780, "w1"), (1280, 800, "k1"), (390, 844, "s3"), (390, 844, "s1"), (390, 844, "s4fail")]:
        page.set_viewport_size({"width": vw, "height": vh})
        proto(page, sid)
        page.evaluate("scrollTo(0,0)")
        page.wait_for_timeout(300)
        boxes = page.evaluate("""(() => {
          const sel = '#rbody .r-label, #rbody .cur, #rbody .r-amount, #rbody dt, #rbody dd, #rbody .nm, #rbody .amt, #rbody .wk,'
            + ' #rbody .r-head h2, #rbody .r-head span, #rbody .r-check .lbl, #rbody .r-spare p, #rbody .r-msg p, #rbody .r-empty p, #rbody .status';
          return [...document.querySelectorAll(sel)].map(e => {
            const r = e.getBoundingClientRect();
            const cls = e.matches('.r-amount') ? 'total' : (e.className || e.tagName.toLowerCase());
            return { cls: String(cls), color: getComputedStyle(e).color, box: [r.left, r.top, r.right, r.bottom] };
          });
        })()""")
        page.add_style_tag(content="#rbody, #rbody * { color: transparent !important; text-shadow: none !important; } #rbody svg { visibility: hidden !important; }")
        page.wait_for_timeout(100)
        path = HERE / "_sample.png"
        page.screenshot(path=str(path), timeout=T)
        img = Image.open(path).convert("RGB")
        for bx in boxes:
            x0, y0, x1, y1 = (int(round(v)) for v in bx["box"])
            best = None
            for x in range(max(x0, 0), min(x1, img.width), 2):
                for y in range(max(y0, 0), min(y1, img.height), 2):
                    px = img.getpixel((x, y))
                    if best is None or lum(px) > lum(best):
                        best = px
            if best is None:
                continue
            fg, _ = parse_css_color(bx["color"])
            r = ratio(fg, best)
            key = f"{bx['cls']} on glass"
            if key not in worst or r < worst[key][0]:
                worst[key] = (r, "#%02X%02X%02X" % best, f"{sid}@{vw}")
        path.unlink()
        page.reload(timeout=15000)
        page.wait_for_selector("#rbody", timeout=T)
        page.wait_for_timeout(2000)
    for k, (r, bg, where) in sorted(worst.items(), key=lambda kv: kv[1][0]):
        out[f"{k} (worst {bg}, {where})"] = r
    solid = hex_rgb(tk["glass-solid"])
    out["ink-soft on solid fallback card"] = ratio(hex_rgb(tk["ink-soft"]), solid)
    out["cyan on solid fallback card"] = ratio(cyan, solid)
    for k, v in out.items():
        if isinstance(v, float):
            need = 3.0 if "3:1" in k else 4.5
            check(v >= need, f"contrast {k} {v} (need {need})")
    return out


def icon_paths():
    """Every icon path in b.html must be a byte-exact Phosphor copy from icons.js or a.html."""
    b = PAGE.read_text(encoding="utf-8")
    ref = A_PAGE.read_text(encoding="utf-8") + ICONS_JS.read_text(encoding="utf-8")
    sym = re.findall(r'<symbol id="(i-[a-z-]+)" viewBox="0 0 256 256"><path d="([^"]+)"/>', b)
    for sid, d in sym:
        check(d in ref, f"icon {sid} is an exact Phosphor copy")
    mark = 'd="M3 6h24v9H3zM33 6h12v9H33zM3 30h42v9H3z"'
    check(mark in b, "header mark uses the mark.svg geometry unchanged")


def copy_audit():
    b = PAGE.read_text(encoding="utf-8")
    check("—" not in b and "–" not in b, "no em or en dashes in the page")
    check(re.search(r"https?://(?!www\.w3\.org/2000/svg)", b) is None, "no network URLs in the page")


def main():
    contrast_out = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            ctx = browser.new_context(viewport={"width": 390, "height": 844})
            requests = []
            ctx.on("request", lambda r: requests.append(r.url) if not r.url.startswith(("file:", "data:")) else None)
            page = ctx.new_page()
            page.on("pageerror", lambda e: console_errors.append(str(e)))
            page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
            run_390(page)
            run_360(page)
            run_768(page)
            run_1280(page)
            contrast_out = contrast(page)
            check(not requests, f"no network requests {requests}")
            ctx.close()
            run_reduced(browser)
        finally:
            browser.close()
    icon_paths()
    copy_audit()
    check(not console_errors, f"console errors {len(console_errors)} {console_errors}")
    print("\n".join(notes))
    print("\n".join(failures) if failures else "no failures")
    print("hscroll@360", json.dumps(hscroll))
    print("contrast", json.dumps(contrast_out, indent=1))
    print("console errors", len(console_errors))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
