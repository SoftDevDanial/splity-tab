"""Stakeholder review drive of Split: the brainstorm's four key flows and its rules, real gestures, cold boot, no seed.

usage: python -B review_split.py <base url> <out dir>      (run with the project root as the working directory)
Writes results.json and one screenshot per check group into <out dir>. Never touches the OS clipboard: every context
loads the project's clipboard recorder (CG-7), or its rejecter for the blocked-clipboard check.
Expected money figures are worked out here from the brainstorm's rules in whole cents, not copied from the app.
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE, OUT = sys.argv[1].rstrip("/"), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
CLIP = Path.cwd() / "tests" / "browser" / "clipboard"
results, requests, console = [], [], []

SUMMARY_JS = """() => [...document.querySelectorAll('dl.sum .row')].map((r) => [r.querySelector('dt').textContent.trim(),
  r.querySelector('.amt').textContent.trim(), (r.querySelector('.work') || { textContent: '' }).textContent.trim()])"""
TABLE_JS = """(part) => [...document.querySelectorAll(`table.shares ${part} tr`)].map((tr) => [...tr.children].map((c) => c.textContent.trim()))"""
ACTIVE_JS = "() => document.activeElement.getAttribute('aria-label') || document.activeElement.id || document.activeElement.textContent.trim()"
WIDTH_JS = "() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]"


# --- the brainstorm's rules, in whole cents --------------------------------------------------------------------
def half_up(num, den):
    return (2 * num + den) // (2 * den)


def bill(sub, service_pct=10, sst_pct=6):
    service = half_up(sub * service_pct, 100)
    sst = half_up((sub + service) * sst_pct, 100)
    return service, sst, sub + service + sst


def even(total, n):
    base, left = divmod(total, n)
    return [base + (1 if i < left else 0) for i in range(n)]


def rm(cents):
    return f"RM {cents // 100}.{cents % 100:02d}"


# --- checks and page helpers ------------------------------------------------------------------------------------
def check(group, name, ok, seen):
    results.append({"group": group, "check": name, "result": "PASS" if ok else "FAIL", "seen": seen})
    print(("PASS " if ok else "FAIL ") + group + " :: " + name + " :: " + str(seen)[:170], flush=True)


def known(group, name, seen, ref):
    results.append({"group": group, "check": name, "result": f"KNOWN ({ref})", "seen": seen})
    print(f"KNOWN {group} :: {name} :: {str(seen)[:170]}", flush=True)


def new_page(browser, width=390, height=844, clip="recorder.js", **extra):
    ctx = browser.new_context(viewport={"width": width, "height": height}, locale="en-GB", **extra)
    ctx.add_init_script(path=str(CLIP / clip))
    page = ctx.new_page()
    page.on("request", lambda r: requests.append(r.url))
    page.on("console", lambda m: console.append(f"{m.type}: {m.text}"))
    page.on("pageerror", lambda e: console.append(f"pageerror: {e}"))
    return ctx, page


def replace(page, locator, text):
    locator.click()
    page.keyboard.press("Control+A")
    if text:
        page.keyboard.type(text)
    else:
        page.keyboard.press("Backspace")


def person(page, n):
    return page.get_by_label(f"Person {n} name", exact=True)


def subtotal(page):
    return page.get_by_role("textbox", name="Subtotal in RM", exact=True)


def button(page, name):
    return page.get_by_role("button", name=name, exact=True)


def message(page):
    m = page.locator("p.result-msg")
    return m.inner_text().strip() if m.count() else ""


def errors(page):
    return [t.strip() for t in page.locator("p.error").all_inner_texts()]


def people_values(page):
    return page.evaluate("() => [...document.querySelectorAll('li.person input')].map((i) => i.value)")


def add_item(page, name, price, who=()):
    button(page, "Add item").click()
    page.keyboard.type(name)
    page.keyboard.press("Tab")
    page.keyboard.type(price)
    label = name or f"Item {page.locator('li.item').count()}"
    for p in who:
        page.get_by_role("group", name=f"Who had {label}", exact=True).get_by_role("button", name=p, exact=True).click()


def settle(page):
    page.wait_for_function("() => document.getAnimations().length === 0")


def shot(page, name):
    settle(page)
    page.screenshot(path=str(OUT / name), full_page=True)


S1_ITEMS = [("Nasi lemak ayam", "15.90", ["Aisyah"]), ("Char kuey teow", "13.50", ["Ben"]),
            ("Mee goreng mamak", "12.00", ["Chen"]), ("Satay, 10 sticks", "18.00", ["Aisyah", "Chen"])]
# The brainstorm's own summary example (C6), word for word.
BRAINSTORM_COPY = ("Bill split\nTotal RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)\n"
                   "Aisyah RM 38.87\nBen RM 38.87\nChen RM 38.86\nAdds up to RM 116.60")


def s1_expected():
    """By-item rule from the brainstorm: shared prices split down with leftovers to the top of the list, then the
    charges shared in proportion to each items subtotal, rounded down, leftovers to the top with items above zero."""
    names = ["Aisyah", "Ben", "Chen"]
    items = {n: 0 for n in names}
    for _, price, who in S1_ITEMS:
        cents = round(float(price) * 100)
        order = [n for n in names if n in who]
        for n, part in zip(order, even(cents, len(order))):
            items[n] += part
    sub = sum(items.values())
    service, sst, total = bill(sub)
    charges = service + sst
    shares = {n: charges * items[n] // sub for n in names}
    left = charges - sum(shares.values())
    for n in names:
        if left and items[n] > 0:
            shares[n] += 1
            left -= 1
    rows = [[n, rm(items[n]), rm(shares[n]), rm(items[n] + shares[n])] for n in names]
    return rows, [["Adds up to", rm(sub), rm(charges), rm(total)]], total


with sync_playwright() as p:
    browser = p.chromium.launch()
    try:
        # ---------------- Flow 1, even split, cold boot ----------------
        g = "flow 1 even split"
        ctx, page = new_page(browser)
        page.goto(BASE + "/")
        check(g, "cold boot: two people, Person 1 and Person 2", people_values(page) == ["Person 1", "Person 2"], people_values(page))
        check(g, "cold boot: Even is chosen, 10% and 6% filled, Subtotal empty",
              page.locator("#mode-even").is_checked() and page.locator("#rate-service").input_value() == "10"
              and page.locator("#rate-sst").input_value() == "6" and subtotal(page).input_value() == "",
              [page.locator("#rate-service").input_value(), page.locator("#rate-sst").input_value()])
        check(g, "cold boot: the shares area says what to do", message(page) == "Enter the subtotal to see the shares.", message(page))
        check(g, "cold boot: nothing saved before the first change", page.evaluate("localStorage.getItem('split.draft')") is None, None)
        check(g, "Remove is disabled at 2 people", all(b.is_disabled() for b in page.locator("li.person button").all()), None)
        hint = page.locator("#charges-hint").inner_text().strip()
        check(g, "the charge hint is on screen", hint == "Set a charge to 0 if your bill already includes it.", hint)
        shot(page, "01-cold-boot.png")
        replace(page, person(page, 1), "Aisyah")
        replace(page, person(page, 2), "Ben")
        check(g, "the draft is saved after a change", "Aisyah" in (page.evaluate("localStorage.getItem('split.draft')") or ""), None)
        button(page, "Add person").click()
        check(g, "Add person puts the cursor in the new name field", page.evaluate(ACTIVE_JS) == "Person 3 name", page.evaluate(ACTIVE_JS))
        page.keyboard.type("Chen")
        replace(page, subtotal(page), "100.00")
        service, sst, total = bill(10000)
        summary = page.evaluate(SUMMARY_JS)
        check(g, "bill summary: subtotal, service on subtotal, SST on subtotal plus service, total",
              summary == [["Subtotal", "RM 100.00", ""], ["+Service charge", rm(service), "10% of RM 100.00"],
                          ["+SST", rm(sst), f"6% of {rm(10000 + service)}"], ["=Total", rm(total), ""]], summary)
        want = [[n, rm(c)] for n, c in zip(["Aisyah", "Ben", "Chen"], even(total, 3))]
        rows = page.evaluate(TABLE_JS, "tbody")
        check(g, "even shares to the cent, leftover cents to the top of the list", rows == want, rows)
        cents = [int(r[1][3:].replace(".", "")) for r in rows]
        check(g, "shares differ by at most 1 sen", max(cents) - min(cents) <= 1, cents)
        check(g, "Adds up to RM X under the shares", page.evaluate(TABLE_JS, "tfoot") == [["Adds up to", rm(total)]], page.evaluate(TABLE_JS, "tfoot"))
        heads = page.locator("div.tape h2").all_inner_texts()
        check(g, "bill summary sits above the shares", heads == ["Bill summary", "Shares"], heads)
        button(page, "Copy summary").click()
        status = page.locator("p.status").inner_text().strip()
        copied = page.evaluate("window.testClipboardText")
        check(g, "Copy summary copies the brainstorm's text exactly", copied == BRAINSTORM_COPY, copied)
        check(g, "Copy summary says Summary copied", status == "Summary copied", status)
        shot(page, "02-even-split.png")

        # ---------------- Flow 2, by item ----------------
        g = "flow 2 by item"
        page.locator("fieldset.mode label", has_text="By item").click()
        check(g, "By item with no items says what to do", message(page) == "Add an item to see the shares.", message(page))
        for name, price, _ in S1_ITEMS:
            add_item(page, name, price)
        check(g, "unassigned items block the result and are counted",
              message(page) == "4 items still need a person. Tap who had each one to see the shares."
              and page.locator("table.shares").count() == 0, message(page))
        for name, _, who in S1_ITEMS[:3]:
            for n in who:
                page.get_by_role("group", name=f"Who had {name}", exact=True).get_by_role("button", name=n, exact=True).click()
        check(g, "one item left says 1 item still needs a person", message(page) == "1 item still needs a person. Tap who had it to see the shares.", message(page))
        for n in S1_ITEMS[3][2]:
            page.get_by_role("group", name=f"Who had {S1_ITEMS[3][0]}", exact=True).get_by_role("button", name=n, exact=True).click()
        want_rows, want_check, s1_total = s1_expected()
        head = page.evaluate(TABLE_JS, "thead")
        check(g, "each person shows items, charges and share", head == [["Person", "+Charges", "=Share"]] or head == [["Person", "Items", "+Charges", "=Share"]], head)
        rows = page.evaluate(TABLE_JS, "tbody")
        check(g, "shared satay split between Aisyah and Chen, charges in proportion, to the cent", rows == want_rows, rows)
        check(g, "the check row adds up to the total", page.evaluate(TABLE_JS, "tfoot") == want_check, page.evaluate(TABLE_JS, "tfoot"))
        button(page, "Copy summary").click()
        copied = page.evaluate("window.testClipboardText")
        check(g, "Copy summary in by item lists each person's share and the total",
              copied.splitlines()[0] == "Bill split" and copied.splitlines()[-1] == f"Adds up to {rm(s1_total)}"
              and [l.rsplit(" RM ", 1)[0] for l in copied.splitlines()[2:5]] == ["Aisyah", "Ben", "Chen"], copied)
        shot(page, "03-by-item.png")
        add_item(page, "", "")
        check(g, "an item with no name shows as Item N", page.get_by_role("group", name="Who had Item 5", exact=True).count() == 1, None)
        check(g, "an item with no price blocks the shares", message(page) == "Give every item a price to see the shares.", message(page))
        button(page, "Remove Item 5").click()
        check(g, "Remove takes the item away at any time", page.locator("li.item").count() == 4 and page.locator("table.shares").count() == 1, page.locator("li.item").count())
        page.locator("fieldset.mode label", has_text="Even").click()
        kept_even = subtotal(page).input_value()
        page.locator("fieldset.mode label", has_text="By item").click()
        check(g, "switching modes keeps both the subtotal and the items", kept_even == "100.00" and page.locator("li.item").count() == 4, [kept_even, page.locator("li.item").count()])

        # ---------------- Flow 3, come back later ----------------
        g = "flow 3 come back"
        page.close()
        page = ctx.new_page()
        page.on("request", lambda r: requests.append(r.url))
        page.on("console", lambda m: console.append(f"{m.type}: {m.text}"))
        page.goto(BASE + "/")
        check(g, "a closed tab reopens on the same bill, By item", page.locator("#mode-item").is_checked() and page.evaluate(TABLE_JS, "tbody") == want_rows, page.evaluate(TABLE_JS, "tbody"))
        page.locator("fieldset.mode label", has_text="Even").click()
        check(g, "the even subtotal and shares are kept too", subtotal(page).input_value() == "100.00" and page.evaluate(TABLE_JS, "tbody") == want, page.evaluate(TABLE_JS, "tbody"))
        shot(page, "04-come-back.png")

        # ---------------- Flow 4, start over ----------------
        g = "flow 4 start over"
        button(page, "New bill").click()
        dlg = page.get_by_role("dialog", name="Start a new bill?")
        text = page.locator("#dialog-text").inner_text().strip()
        check(g, "New bill asks the brainstorm's question",
              dlg.count() == 1 and text == "This clears the people, items and amounts."
              and button(page, "Start new bill").is_visible() and button(page, "Cancel").is_visible(), text)
        shot(page, "05-dialog.png")
        button(page, "Cancel").click()
        check(g, "Cancel keeps the bill", people_values(page) == ["Aisyah", "Ben", "Chen"] and subtotal(page).input_value() == "100.00", people_values(page))
        button(page, "New bill").click()
        page.keyboard.press("Escape")
        check(g, "Esc also cancels and keeps the bill", people_values(page) == ["Aisyah", "Ben", "Chen"], people_values(page))
        button(page, "New bill").click()
        page.mouse.click(6, 6)
        check(g, "a click on the backdrop cancels (delegated ruling CG-8)", not page.locator("dialog.dialog").evaluate("(d) => d.open")
              and people_values(page) == ["Aisyah", "Ben", "Chen"], None)
        button(page, "New bill").click()
        button(page, "Start new bill").click()
        back = [people_values(page), page.locator("#mode-even").is_checked(), page.locator("#rate-service").input_value(),
                page.locator("#rate-sst").input_value(), subtotal(page).input_value(), message(page)]
        check(g, "Start new bill returns to two people, even split, 10% and 6%",
              back == [["Person 1", "Person 2"], True, "10", "6", "", "Enter the subtotal to see the shares."], back)
        page.reload()
        check(g, "the new bill is what a reload shows", people_values(page) == ["Person 1", "Person 2"] and subtotal(page).input_value() == "", people_values(page))
        page.locator("fieldset.mode label", has_text="By item").click()
        check(g, "the items are cleared too", page.locator("li.item").count() == 0, page.locator("li.item").count())
        shot(page, "06-new-bill.png")
        ctx.close()

        # ---------------- Rules: amounts and bill maths ----------------
        g = "rules amounts"
        ctx, page = new_page(browser)
        page.goto(BASE + "/")
        for good in ("12", "12.5", "12.50", "99999.99"):
            replace(page, subtotal(page), good)
            page.keyboard.press("Tab")
            check(g, f"amount {good!r} is accepted", errors(page) == [] and page.locator("table.shares").count() == 1, errors(page))
        for bad in ("abc", "0", "12.345", "100000", "-5", "1,000"):
            replace(page, subtotal(page), bad)
            page.keyboard.press("Tab")
            check(g, f"amount {bad!r} shows the inline error when the field is left", errors(page) == ["Enter an amount like 12.50"], errors(page))
        shot(page, "07-amount-error.png")
        replace(page, subtotal(page), "10.05")
        page.keyboard.press("Tab")
        service, sst, total = bill(1005)
        summary = page.evaluate(SUMMARY_JS)
        check(g, "service rounds half up to the cent (10% of RM 10.05 is RM 1.01)", summary[1][1] == rm(service) == "RM 1.01", summary)
        check(g, "SST on subtotal plus service, half up", summary[2][1] == rm(sst) and summary[3][1] == rm(total), summary)
        button(page, "Add person").click()
        rows = page.evaluate(TABLE_JS, "tbody")
        check(g, "three people: leftover cents go to the top of the list", [r[1] for r in rows] == [rm(c) for c in even(total, 3)], rows)

        g = "rules charges"
        replace(page, subtotal(page), "100")
        for field, bad, msg in (("#rate-service", "31", "Enter a rate from 0 to 30"), ("#rate-sst", "21", "Enter a rate from 0 to 20"),
                                ("#rate-service", "12.555", "Enter a rate from 0 to 30")):
            replace(page, page.locator(field), bad)
            page.keyboard.press("Tab")
            check(g, f"{field[6:]} {bad} shows its range", msg in errors(page), errors(page))
            check(g, f"{field[6:]} {bad} holds back the shares with a reason", message(page) == "Check the charges to see the shares.", message(page))
            replace(page, page.locator(field), "10" if "service" in field else "6")
        for field, edge in (("#rate-service", "30"), ("#rate-sst", "20"), ("#rate-service", "12.5")):
            replace(page, page.locator(field), edge)
            page.keyboard.press("Tab")
            check(g, f"{field[6:]} {edge} is accepted", errors(page) == [] and page.locator("table.shares").count() == 1, errors(page))
        replace(page, page.locator("#rate-service"), "0")
        replace(page, page.locator("#rate-sst"), "0")
        page.keyboard.press("Tab")
        summary = page.evaluate(SUMMARY_JS)
        check(g, "0 turns both charges off: total equals the subtotal", summary[1][1] == "RM 0.00" and summary[2][1] == "RM 0.00" and summary[3][1] == "RM 100.00", summary)
        shot(page, "08-charges.png")
        ctx.close()

        # ---------------- Rules: people ----------------
        g = "rules people"
        ctx, page = new_page(browser)
        page.goto(BASE + "/")
        replace(page, person(page, 1), "A" * 25)
        check(g, "a name stops at 20 characters", len(person(page, 1).input_value()) == 20, len(person(page, 1).input_value()))
        replace(page, person(page, 1), "Ali")
        replace(page, person(page, 2), "Ali")
        replace(page, subtotal(page), "10")
        rows = page.evaluate(TABLE_JS, "tbody")
        check(g, "duplicate names are allowed", [r[0] for r in rows] == ["Ali", "Ali"] and errors(page) == [], rows)
        replace(page, person(page, 2), "")
        rows = page.evaluate(TABLE_JS, "tbody")
        check(g, "a blank name shows as Person N", [r[0] for r in rows] == ["Ali", "Person 2"], rows)
        while page.locator("li.person").count() < 12:
            button(page, "Add person").click()
        check(g, "Add person is disabled at 12", button(page, "Add person").is_disabled() and page.locator("li.person").count() == 12, page.locator("li.person").count())
        shot(page, "09-twelve-people.png")
        button(page, "Remove Person 12").click()
        check(g, "Add person comes back at 11", not button(page, "Add person").is_disabled(), None)
        ctx.close()

        ctx, page = new_page(browser)
        page.goto(BASE + "/")
        replace(page, person(page, 1), "Aisyah")
        replace(page, person(page, 2), "Ben")
        button(page, "Add person").click()
        page.keyboard.type("Chen")
        page.locator("fieldset.mode label", has_text="By item").click()
        add_item(page, "Teh tarik", "3.00", ["Chen"])
        add_item(page, "Roti canai", "2.40", ["Ben", "Chen"])
        button(page, "Remove Chen").click()
        who = page.get_by_role("group", name="Who had Roti canai", exact=True).get_by_role("button").all_inner_texts()
        check(g, "removing a person takes them off every item",
              message(page) == "1 item still needs a person. Tap who had it to see the shares." and [w.strip() for w in who] == ["Aisyah", "Ben"], [message(page), who])
        shot(page, "10-remove-person.png")
        ctx.close()

        # ---------------- Rules: items ----------------
        g = "rules items"
        ctx, page = new_page(browser)
        page.goto(BASE + "/")
        page.locator("fieldset.mode label", has_text="By item").click()
        button(page, "Add item").click()
        page.keyboard.type("x" * 45)
        check(g, "an item name stops at 40 characters", len(page.get_by_label("Item 1 name", exact=True).input_value()) == 40, None)
        while page.locator("li.item").count() < 50:
            button(page, "Add item").click()
        check(g, "Add item is disabled at 50 items", button(page, "Add item").is_disabled(), page.locator("li.item").count())
        ctx.close()

        # ---------------- Rules: copy blocked, unreadable draft ----------------
        g = "rules copy and draft"
        ctx, page = new_page(browser, clip="reject.js")
        page.goto(BASE + "/")
        replace(page, subtotal(page), "50")
        button(page, "Copy summary").click()
        page.wait_for_function("() => document.querySelector('p.status').textContent.length > 0")
        status = page.locator("p.status").inner_text().strip()
        check(g, "a blocked clipboard says so", status == "Could not copy. Your browser blocked the clipboard.", status)
        shot(page, "11-copy-blocked.png")
        ctx.close()

        ctx, page = new_page(browser)
        page.goto(BASE + "/")
        page.evaluate("localStorage.setItem('split.draft', '{not json')")
        page.reload()
        note = page.locator("div.note")
        text = note.inner_text().strip() if note.count() else ""
        check(g, "an unreadable draft starts a new bill with the note", text == "Your saved bill could not be read, so a new one was started."
              and people_values(page) == ["Person 1", "Person 2"], text)
        shot(page, "12-unreadable-draft.png")
        button(page, "Dismiss note").click()
        check(g, "the note can be dismissed", page.locator("div.note").count() == 0, page.locator("div.note").count())
        ctx.close()

        # ---------------- Platform: 360 px phone, keyboard, reduced motion, desktop ----------------
        g = "platform"
        ctx, page = new_page(browser, width=360, height=780)
        page.goto(BASE + "/")
        replace(page, person(page, 1), "Aisyah")
        replace(page, person(page, 2), "Ben")
        button(page, "Add person").click()
        page.keyboard.type("Chen")
        replace(page, subtotal(page), "100.00")
        w = page.evaluate(WIDTH_JS)
        check(g, "360 px phone, even split, no sideways scroll", w[0] <= w[1], w)
        page.locator("fieldset.mode label", has_text="By item").click()
        for name, price, who in S1_ITEMS:
            add_item(page, name, price, who)
        w = page.evaluate(WIDTH_JS)
        check(g, "360 px phone, the brainstorm-sized by-item bill fits", w[0] <= w[1], w)
        shot(page, "13-phone-360-by-item.png")
        add_item(page, "Seafood platter", "999.00", ["Aisyah"])
        w = page.evaluate(WIDTH_JS)
        known(g, "360 px phone, a by-item bill over RM 653.40 scrolls sideways", w, "H-02, accepted for v1.0, fixed in v1.1.0")
        shot(page, "14-phone-360-big-bill.png")
        ctx.close()

        ctx, page = new_page(browser)
        page.goto(BASE + "/")
        page.keyboard.press("Tab")
        first = page.evaluate(ACTIVE_JS)
        page.keyboard.press("Tab")
        second = page.evaluate(ACTIVE_JS)
        ring = page.evaluate("() => getComputedStyle(document.activeElement.closest('.field')).outlineStyle")
        check(g, "keyboard: Tab goes New bill, then Person 1 name, with a visible focus ring", first == "New bill" and second == "Person 1 name" and ring == "solid", [first, second, ring])
        page.keyboard.type("Aisyah")
        for _ in range(6):
            if page.evaluate(ACTIVE_JS) == "Add person":
                break
            page.keyboard.press("Tab")
        page.keyboard.press("Enter")
        check(g, "keyboard: Enter on Add person adds one and moves to its name", page.evaluate(ACTIVE_JS) == "Person 3 name", page.evaluate(ACTIVE_JS))
        for _ in range(8):
            if page.evaluate(ACTIVE_JS) == "mode-even":
                break
            page.keyboard.press("Tab")
        page.keyboard.press("ArrowRight")
        check(g, "keyboard: the arrow key switches to By item", page.locator("#mode-item").is_checked(), page.evaluate(ACTIVE_JS))
        ctx.close()

        ctx, page = new_page(browser, reduced_motion="reduce")
        page.goto(BASE + "/")
        dur = page.evaluate("getComputedStyle(document.querySelector('.btn')).transitionDuration")
        check(g, "reduced motion switches transitions off", all(float(d.rstrip("s")) == 0 for d in dur.split(",")), dur)
        ctx.close()

        ctx, page = new_page(browser, width=1280, height=800)
        page.goto(BASE + "/")
        replace(page, subtotal(page), "100.00")
        w = page.evaluate(WIDTH_JS)
        check(g, "desktop 1280 px, no sideways scroll", w[0] <= w[1], w)
        shot(page, "15-desktop.png")

        # ---------------- Non-goals ----------------
        g = "non-goals"
        page.locator("fieldset.mode label", has_text="By item").click()
        words = " ".join(page.locator("button, label, a, h1, h2, h3, legend").all_inner_texts()
                         + page.evaluate("() => [...document.querySelectorAll('[aria-label]')].map((e) => e.getAttribute('aria-label'))")).lower()
        banned = [w for w in ("pay", "duitnow", "qr", "login", "sign in", "account", "sync", "share link", "currency", "usd", "history",
                              "photo", "scan", "camera", "tip", "discount", "voucher", "theme", "dark mode", "language", "cash rounding")
                  if w in words.replace("people", "")]
        check(g, "no payments, accounts, sync, currencies, history, OCR, tips, discounts, theme or language control", banned == [], banned)
        check(g, "no file upload, no dropdown, no links out", page.locator("input[type=file], select, a[href]").count() == 0, page.locator("input[type=file], select, a[href]").count())
        ctx.close()
    finally:
        browser.close()

g = "privacy and health"
origin = BASE
outside = sorted({u for u in requests if not u.startswith(origin)})
check(g, "every request went to the app's own address", not outside, outside)
bad = [line for line in console if line.startswith(("error:", "pageerror:")) or "Content Security Policy" in line]
check(g, "no console errors, page errors or CSP violations in any session", not bad, bad)
fails = [r for r in results if r["result"] == "FAIL"]
known_rows = [r for r in results if r["result"].startswith("KNOWN")]
(OUT / "results.json").write_text(json.dumps({"base": BASE, "checks": results, "requests": len(requests),
                                              "fails": len(fails), "known": len(known_rows)}, indent=1), encoding="utf-8")
print(f"{len(results) - len(fails) - len(known_rows)} of {len(results) - len(known_rows)} checks PASS, {len(known_rows)} known limit measured")
