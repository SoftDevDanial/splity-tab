"""Render checks for round-1 direction E (Command Line).

Opens e.html by its file:/// URL in headless Chromium at 390x844, 360x780 and 1280x800.
Saves screenshots into this folder, prints console errors, sideways scroll at 360, keyboard reach of
P1 and M1, the inventory figures and the contrast ratios. Every wait is bounded and the browser is
closed in a finally block. Writes nothing but the screenshots.
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
PAGE = (HERE.parent.parent / "e.html").resolve()
URL = PAGE.as_uri()
T = 5000  # default bounded timeout, ms

errors, foreign = [], []
fails = []


def check(cond, label):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        fails.append(label)


def lum(hexv):
    hexv = hexv.strip().lstrip("#")
    c = [int(hexv[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return round((la + 0.05) / (lb + 0.05), 2)


def open_page(browser, w, h, motion="no-preference"):
    ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, reduced_motion=motion)
    page = ctx.new_page()
    page.set_default_timeout(T)
    page.on("console", lambda m: errors.append(f"{w}px console.{m.type}: {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(f"{w}px pageerror: {e}"))
    page.on("request", lambda r: None if r.url.startswith(("file:", "data:")) else foreign.append(r.url))
    page.goto(URL, wait_until="load", timeout=10000)
    page.wait_for_selector("#out-in table.shares", timeout=T)
    return ctx, page


def set_state(page, key):
    page.click("#proto-tab")
    page.click(f'.st[data-state="{key}"]')
    page.wait_for_timeout(120)


def shot(page, name, full=True):
    page.wait_for_timeout(260)
    page.screenshot(path=str(HERE / name), full_page=full, animations="disabled")
    print("  shot", name)


def rows(page):
    return page.eval_on_selector_all(
        "#out-in table.shares tbody tr",
        "trs => trs.map(tr => [...tr.children].map(c => c.textContent.trim()))")


def foot(page):
    return page.eval_on_selector_all(
        "#out-in table.shares tfoot td", "tds => tds.map(td => td.textContent.trim())")


def out_text(page):
    return page.inner_text("#out-in")


OVERFLOW_JS = """(w) => {
  const off = [];
  for (const el of document.querySelectorAll('body *')) {
    if (el.closest('dialog:not([open])') || el.closest('[hidden]') || el.closest('.sr-only')) continue;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || cs.position === 'fixed') continue;
    const r = el.getBoundingClientRect();
    if (!r.width && !r.height) continue;
    if (r.right > w + 0.5 || r.left < -0.5) off.push(el.tagName + '#' + el.id + '.' + (typeof el.className === 'string' ? el.className : '') + ' right=' + Math.round(r.right));
  }
  const clipped = [];
  for (const el of document.querySelectorAll('#out-in td, #out-in tfoot th, .sum dd, .sum dt, .spare-n')) {
    if (el.scrollWidth > el.clientWidth + 1) clipped.push(el.textContent.trim());
  }
  return {scrollWidth: document.documentElement.scrollWidth, bodyScroll: document.body.scrollWidth, offenders: off.slice(0, 15), clipped};
}"""


def overflow_ok(page, w, label):
    r = page.evaluate(OVERFLOW_JS, w)
    ok = r["scrollWidth"] <= w and not r["offenders"] and not r["clipped"]
    check(ok, f"{label} at {w}px: scrollWidth {r['scrollWidth']}, offenders {r['offenders']}, clipped cells {r['clipped']}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            # ---------------- 390 x 844 ----------------
            ctx, page = open_page(browser, 390, 844)
            print("== 390 x 844")
            shot(page, "k1_390.png")
            shot(page, "k1_390_viewport.png", full=False)
            r = rows(page)
            check(r == [["Aisyah", "24.90", "4.14", "RM 29.04"], ["Ben", "13.50", "2.24", "RM 15.74"], ["Chen", "21.00", "3.48", "RM 24.48"]], f"K1 rows {r}")
            check(foot(page) == ["59.40", "9.86", "RM 69.26"], f"K1 adds up {foot(page)}")
            t = out_text(page)
            for s in ["RM 59.40", "10% of RM 59.40", "RM 5.94", "6% of RM 65.34", "RM 3.92", "RM 69.26", "1 sen left over", "Top of the list"]:
                check(s in t, f"K1 shows '{s}'")
            check(page.inner_text(".brand").strip() == "Splity Tab", "header wordmark is 'Splity Tab' only")
            check(page.title() == "Danial's Splity Tab", f"title '{page.title()}'")

            # P1 by click: menu, then one person -> Ben
            page.click("#btn-spare")
            page.wait_for_selector("#dlg-spare[open]", timeout=T)
            shot(page, "p1_menu_390.png", full=False)
            page.click('#sp-list .opt[data-key="2"]')
            page.wait_for_timeout(100)
            shot(page, "p1_person_390.png", full=False)
            page.click('#sp-list .opt[data-key="2"]')
            page.wait_for_timeout(100)
            check(not page.is_visible("#dlg-spare"), "P1 closes after choosing Ben")
            r = rows(page)
            check([x[3] for x in r] == ["RM 29.03", "RM 15.75", "RM 24.48"], f"K1 one person Ben {[x[3] for x in r]}")
            check(foot(page)[-1] == "RM 69.26", "K1 one person still adds up to RM 69.26")
            shot(page, "p1_one_person_390.png")

            # backdrop closes P1
            page.click("#btn-spare")
            page.wait_for_selector("#dlg-spare[open]", timeout=T)
            page.mouse.click(195, 40)
            page.wait_for_timeout(150)
            check(not page.is_visible("#dlg-spare"), "P1 closes on backdrop tap")

            # K2 and its spare sen choices
            set_state(page, "K2")
            shot(page, "k2_390.png")
            r = rows(page)
            check([x[-1] for x in r] == ["RM 38.87", "RM 38.87", "RM 38.86"], f"K2 shares {[x[-1] for x in r]}")
            t = out_text(page)
            for s in ["RM 100.00", "RM 10.00", "RM 6.60", "RM 116.60", "2 sen left over", "Top of the list"]:
                check(s in t, f"K2 shows '{s}'")
            page.click("#btn-spare"); page.wait_for_selector("#dlg-spare[open]", timeout=T)
            page.click('#sp-list .opt[data-key="2"]'); page.wait_for_timeout(80)
            page.click('#sp-list .opt[data-key="2"]'); page.wait_for_timeout(120)
            r = [x[-1] for x in rows(page)]
            check(r == ["RM 38.86", "RM 38.88", "RM 38.86"], f"K2 one person Ben {r}")
            page.click("#btn-spare"); page.wait_for_selector("#dlg-spare[open]", timeout=T)
            page.click('#sp-list .opt[data-key="3"]'); page.wait_for_timeout(120)
            check(page.is_visible("#btn-again"), "At random shows Pick again")
            shot(page, "p1_random_390.png")
            outcomes = set()
            for _ in range(30):
                r = [x[-1] for x in rows(page)]
                check_ok = sorted(r) == ["RM 38.86", "RM 38.87", "RM 38.87"]
                if not check_ok:
                    check(False, f"random shares wrong {r}")
                    break
                outcomes.add(tuple(r))
                page.click("#btn-again")
            check(len(outcomes) >= 2, f"Pick again draws really vary: {len(outcomes)} distinct outcomes in 30 draws {sorted(outcomes)}")

            # M1 by click, Cancel, Esc, backdrop
            page.click("#btn-new"); page.wait_for_selector("#dlg-new[open]", timeout=T)
            shot(page, "m1_390.png", full=False)
            t = page.inner_text("#dlg-new")
            for s in ["Start a new bill?", "This clears the people, items and amounts.", "Start new bill", "Cancel"]:
                check(s in t, f"M1 shows '{s}'")
            page.keyboard.press("Escape"); page.wait_for_timeout(120)
            check(not page.is_visible("#dlg-new"), "M1 closes on Esc")
            page.click("#btn-new"); page.wait_for_selector("#dlg-new[open]", timeout=T)
            page.mouse.click(10, 10); page.wait_for_timeout(120)
            check(not page.is_visible("#dlg-new"), "M1 closes on backdrop tap")
            page.click("#btn-new"); page.wait_for_selector("#dlg-new[open]", timeout=T)
            page.click("#new-start"); page.wait_for_timeout(120)
            t = out_text(page)
            check("Enter the subtotal to see the shares." in t, "Start new bill gives S1 message")

            # States
            set_state(page, "S1"); shot(page, "s1_390.png")
            vals = page.eval_on_selector_all(".person input", "els => els.map(e => e.value)")
            check(vals == ["Person 1", "Person 2"], f"S1 people {vals}")
            check(page.is_checked("#mode-even") and page.input_value("#subtotal") == "" and page.input_value("#rate-service") == "10" and page.input_value("#rate-sst") == "6", "S1 even, empty subtotal, 10 and 6")
            check(page.eval_on_selector_all(".person .icon-btn", "b => b.every(x => x.disabled)"), "S1 remove disabled at 2 people")
            set_state(page, "S2"); shot(page, "s2_390.png")
            check("Enter an amount like 12.50" in page.inner_text("#block-subtotal"), "S2 error under the subtotal")
            set_state(page, "S3"); shot(page, "s3_390.png")
            check("1 item still needs a person. Tap who had it to see the shares." in out_text(page), "S3 message")
            set_state(page, "S4"); shot(page, "s4_copied_390.png")
            check("Summary copied" in out_text(page), "S4 Summary copied")
            set_state(page, "S4b"); shot(page, "s4_failed_390.png")
            check("Could not copy. Your browser blocked the clipboard." in out_text(page), "S4 could not copy")
            set_state(page, "S5"); shot(page, "s5_390.png")
            check("This bill is not being saved on this device. It will be lost when you close this tab." in page.inner_text("#note-wrap"), "S5 note")
            check(page.query_selector("#note-wrap button") is None, "S5 cannot be dismissed")
            set_state(page, "S6"); shot(page, "s6_390.png")
            check("Your saved bill could not be read, so a new one was started." in page.inner_text("#note-wrap"), "S6 note")
            page.click("#note-dismiss"); page.wait_for_timeout(80)
            check(page.inner_text("#note-wrap").strip() == "", "S6 dismiss works")
            set_state(page, "S7"); shot(page, "s7_390.png")
            check(page.is_disabled("#btn-add-person") and page.eval_on_selector_all(".person", "e => e.length") == 12, "S7 12 people, Add person disabled")
            # Copy summary click shows the status (no clipboard call)
            set_state(page, "K1")
            page.click("#btn-copy"); page.wait_for_timeout(80)
            check("Summary copied" in out_text(page), "Copy summary click shows status")
            # proto panel open over the page
            page.click("#proto-tab"); page.wait_for_timeout(80)
            shot(page, "proto_panel_390.png", full=False)
            page.keyboard.press("Escape"); page.wait_for_timeout(80)
            check(page.is_hidden("#proto-panel"), "Prototype states panel closes on Esc")
            # palette add item natural S2 and S3
            page.fill("#new-name", "Teh tarik")
            page.fill("#new-price", "3.205")
            page.click("#btn-add-item"); page.wait_for_timeout(80)
            check("Enter an amount like 12.50" in page.inner_text("#palette"), "palette shows amount error on Add")
            shot(page, "palette_error_390.png")
            page.fill("#new-price", "3.20")
            page.keyboard.press("Enter"); page.wait_for_timeout(120)
            check("1 item still needs a person." in out_text(page), "added item without a person shows S3 naturally")
            ctx.close()

            # ---------------- 360 x 780 ----------------
            ctx, page = open_page(browser, 360, 780)
            print("== 360 x 780")
            shot(page, "k1_360.png")
            overflow_ok(page, 360, "K1")
            set_state(page, "W1"); shot(page, "w1_360.png")
            check("RM 1,193.87" in out_text(page), "W1 shows RM 1,193.87")
            overflow_ok(page, 360, "W1")
            set_state(page, "S7"); overflow_ok(page, 360, "S7")
            set_state(page, "K2"); overflow_ok(page, 360, "K2")
            page.click("#btn-spare"); page.wait_for_selector("#dlg-spare[open]", timeout=T)
            page.click('#sp-list .opt[data-key="3"]'); page.wait_for_timeout(120)
            overflow_ok(page, 360, "K2 at random")
            shot(page, "k2_random_360.png")
            set_state(page, "S5"); overflow_ok(page, 360, "S5")
            set_state(page, "S2"); overflow_ok(page, 360, "S2")
            ctx.close()

            # ---------------- 1280 x 800 ----------------
            ctx, page = open_page(browser, 1280, 800)
            print("== 1280 x 800")
            shot(page, "k1_1280.png")
            shot(page, "k1_1280_viewport.png", full=False)
            overflow_ok(page, 1280, "K1")
            # keyboard reach by Tab
            order = []
            page.click(".brand span")
            for _ in range(120):
                page.keyboard.press("Tab")
                fid = page.evaluate("document.activeElement && (document.activeElement.id || document.activeElement.tagName)")
                order.append(fid)
                if fid == "btn-spare":
                    break
            check("btn-new" in order, f"Tab reaches New bill (step {order.index('btn-new') + 1 if 'btn-new' in order else '-'})")
            check("btn-spare" in order, f"Tab reaches the spare sen control (step {len(order)})")
            ring = page.evaluate("(() => { const s = getComputedStyle(document.activeElement); return [s.outlineStyle, s.outlineWidth, s.outlineColor]; })()")
            check(ring[0] == "solid" and ring[1] == "2px", f"visible focus ring on the focused control {ring}")
            page.keyboard.press("Enter"); page.wait_for_selector("#dlg-spare[open]", timeout=T)
            check(True, "Enter on the spare sen control opens P1")
            shot(page, "p1_menu_1280.png", full=False)
            page.keyboard.press("ArrowDown"); page.keyboard.press("Enter"); page.wait_for_timeout(80)
            shot(page, "p1_person_1280.png", full=False)
            page.keyboard.press("2"); page.wait_for_timeout(120)
            r = [x[3] for x in rows(page)]
            check(r == ["RM 29.03", "RM 15.75", "RM 24.48"], f"keyboard only: one person Ben {r}")
            page.keyboard.press("s"); page.wait_for_selector("#dlg-spare[open]", timeout=T)
            check(True, "key S opens P1")
            page.keyboard.press("Escape"); page.wait_for_timeout(100)
            check(not page.is_visible("#dlg-spare"), "Esc closes P1")
            page.keyboard.press("n"); page.wait_for_selector("#dlg-new[open]", timeout=T)
            check(page.evaluate("document.activeElement.id") == "new-cancel", "key N opens M1 with focus on Cancel")
            shot(page, "m1_1280.png", full=False)
            page.keyboard.press("Escape"); page.wait_for_timeout(100)
            check(not page.is_visible("#dlg-new"), "Esc closes M1")
            # Tab to New bill and Enter (click the plain wordmark first so Tab starts at the top)
            page.click(".brand span"); page.keyboard.press("Tab")
            check(page.evaluate("document.activeElement.id") == "btn-new", "first Tab stop is New bill")
            page.keyboard.press("Enter"); page.wait_for_selector("#dlg-new[open]", timeout=T)
            page.keyboard.press("Tab"); page.keyboard.press("Shift+Tab")
            page.keyboard.press("Escape"); page.wait_for_timeout(80)
            # keys E, I, /
            page.keyboard.press("e"); page.wait_for_timeout(60)
            check(page.is_checked("#mode-even"), "key E switches to Even")
            shot(page, "k2_1280.png")
            page.keyboard.press("i"); page.wait_for_timeout(60)
            check(page.is_checked("#mode-item"), "key I switches to By item")
            page.focus("#btn-new"); page.keyboard.press("/")
            check(page.evaluate("document.activeElement.id") == "new-name", "key / focuses the add-item palette")
            shot(page, "palette_focus_1280.png", full=False)
            set_state(page, "W1"); shot(page, "w1_1280.png")
            set_state(page, "S5"); shot(page, "s5_1280.png", full=False)

            # touch targets
            small = page.evaluate("""() => [...document.querySelectorAll('main button, main input:not([type=radio]), main label[for^=mode], #btn-new')]
              .filter(e => e.offsetParent !== null && !e.classList.contains('tap'))
              .map(e => { const r = e.getBoundingClientRect(); return [e.id || e.textContent.trim().slice(0, 20), Math.round(r.width), Math.round(r.height)]; })
              .filter(x => x[2] < 44 || (x[1] < 44))""")
            check(not small, f"touch targets 44 px (chips are 36 px drawn with a 46 px hit area) {small}")

            # contrast from the live tokens
            tok = page.evaluate("""() => { const s = getComputedStyle(document.documentElement); const o = {};
              for (const k of ['bg','surface','field','hover','ink','ink-2','on-ink','line-strong','signal','signal-ink','error']) o[k] = s.getPropertyValue('--' + k).trim();
              return o; }""")
            pairs = [
                ("body text ink on page bg", "ink", "bg", 4.5), ("body text ink on output surface", "ink", "surface", 4.5),
                ("muted ink-2 on page bg", "ink-2", "bg", 4.5), ("muted ink-2 on output surface", "ink-2", "surface", 4.5),
                ("muted ink-2 on palette field", "ink-2", "field", 4.5), ("muted ink-2 on hover", "ink-2", "hover", 4.5),
                ("accent signal-ink (prompt, check, focus) on page bg", "signal-ink", "bg", 4.5),
                ("accent signal-ink on output surface", "signal-ink", "surface", 4.5),
                ("accent signal-ink on palette field", "signal-ink", "field", 4.5),
                ("ink text on the signal orange key (Add item)", "ink", "signal", 4.5),
                ("on-ink on ink (Total bar, Copy summary, chosen chip)", "on-ink", "ink", 4.5),
                ("error on page bg", "error", "bg", 4.5), ("error on palette field", "error", "field", 4.5),
                ("control underline line-strong on page bg (3:1)", "line-strong", "bg", 3.0),
                ("control border line-strong on field (3:1)", "line-strong", "field", 3.0),
                ("focus ring signal-ink on hover (3:1)", "signal-ink", "hover", 3.0),
            ]
            print("== contrast (tokens " + ", ".join(f"{k} {v}" for k, v in tok.items()) + ")")
            for label, a, b, need in pairs:
                rr = ratio(tok[a], tok[b])
                check(rr >= need, f"{label}: {rr}:1 (need {need})")
            ctx.close()

            # ---------------- reduced motion ----------------
            ctx, page = open_page(browser, 390, 844, motion="reduce")
            page.click("#btn-spare"); page.wait_for_selector("#dlg-spare[open]", timeout=T)
            anim = page.evaluate("getComputedStyle(document.querySelector('#dlg-spare .card')).animationName")
            check(anim == "none", f"reduced motion: dialog has no animation ({anim})")
            page.keyboard.press("Escape")
            ctx.close()
        finally:
            browser.close()

    print("== console and page errors:", len(errors))
    for e in errors:
        print("  ", e)
    print("== requests that are not file: or data:", len(foreign), foreign[:5])
    check(not errors, "zero console errors")
    check(not foreign, "no network requests")
    print("== RESULT:", "ALL PASS" if not fails else f"{len(fails)} FAIL")


if __name__ == "__main__":
    main()
