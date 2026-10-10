"""Reproduce Split UAT-01 to UAT-06 as the owner did them, in several browsers, and print the by-item table.
Also a variant with Ben above Aisyah in the people list. Clipboard recorder only (CG-7). Reads only.
usage: python -B split_uat06_repro.py <base url> <project root>
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE, ROOT = sys.argv[1].rstrip("/"), Path(sys.argv[2])
TABLE_JS = """(part) => [...document.querySelectorAll(`table.shares ${part} tr`)].map((tr) => [...tr.children].map((c) => c.textContent.trim()))"""
ITEMS = [("Nasi lemak ayam", "15.90", ["Aisyah"]), ("Char kuey teow", "13.50", ["Ben"]),
         ("Mee goreng mamak", "12.00", ["Chen"]), ("Satay, 10 sticks", "18.00", ["Aisyah", "Chen"])]


def replace(page, locator, text):
    locator.click()
    page.keyboard.press("Control+A")
    page.keyboard.type(text)


def run(browser, names):
    ctx = browser.new_context(viewport={"width": 1280, "height": 800})
    ctx.add_init_script(path=str(ROOT / "tests" / "browser" / "clipboard" / "recorder.js"))
    page = ctx.new_page()
    page.goto(BASE + "/")
    replace(page, page.get_by_label("Person 1 name", exact=True), names[0])
    replace(page, page.get_by_label("Person 2 name", exact=True), names[1])
    page.get_by_role("button", name="Add person", exact=True).click()
    page.keyboard.type(names[2])
    replace(page, page.get_by_role("textbox", name="Subtotal in RM", exact=True), "100.00")
    page.get_by_role("button", name="Copy summary", exact=True).click()
    page.locator("fieldset.mode label", has_text="By item").click()
    for name, price, who in ITEMS:
        page.get_by_role("button", name="Add item", exact=True).click()
        page.keyboard.type(name)
        page.keyboard.press("Tab")
        page.keyboard.type(price)
        for person in who:
            page.get_by_role("group", name=f"Who had {name}", exact=True).get_by_role("button", name=person, exact=True).click()
    rows = page.evaluate(TABLE_JS, "tbody") + page.evaluate(TABLE_JS, "tfoot")
    ctx.close()
    return rows


with sync_playwright() as p:
    for label, kwargs in (("chromium", {}), ("chrome", {"channel": "chrome"}), ("msedge", {"channel": "msedge"})):
        try:
            browser = p.chromium.launch(**kwargs)
        except Exception as error:
            print(label, "not available:", str(error).splitlines()[0])
            continue
        try:
            print(label, browser.version, "Aisyah, Ben, Chen:", run(browser, ["Aisyah", "Ben", "Chen"]))
            if label == "chromium":
                print(label, "variant Ben, Aisyah, Chen:", run(browser, ["Ben", "Aisyah", "Chen"]))
        finally:
            browser.close()
