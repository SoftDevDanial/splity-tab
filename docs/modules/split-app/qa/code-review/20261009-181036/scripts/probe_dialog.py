"""Dialog probes: F-1 repro, drag from the dialog text to the backdrop, click on the dialog padding,
focus after a click on non-focusable dialog text, key repeat on New bill. (Record copy, see cr.py.)"""
import sys
sys.path.insert(0, "{temp}/claude/{project-id}/0fc4b490-9bf0-46ec-8ac8-08b33bc21485/scratchpad")
import cr

run = cr.Run().start()
try:
    seeds = run.seeds

    def new_bill(page):
        page.get_by_role("button", name="New bill", exact=True).click()

    def center(locator):
        box = locator.bounding_box()
        return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2

    # a. F-1 repro (double click on Cancel) at the sizes QA measured, mouse and touch
    for viewport in [(375, 667), (360, 640), (412, 732)]:
        for how in ["mouse", "touch"]:
            s = run.session(seed=seeds.S1, viewport=viewport, touch=(how == "touch"))
            page = s.open()
            before = s.stored()
            new_bill(page)
            x, y = center(page.get_by_role("button", name="Cancel"))
            if how == "mouse":
                page.mouse.dblclick(x, y)
            else:
                page.touchscreen.tap(x, y)
                page.touchscreen.tap(x, y)
            page.wait_for_timeout(150)
            after = s.stored()
            run.check(f"F-1 {how} {viewport}: a double click/tap on Cancel leaves the draft unchanged", before == after,
                      "draft changed" if before != after else "")
            s.close()

    # b. drag from the dialog text to the backdrop, release outside the box
    s = run.session(seed=seeds.S2)
    page = s.open()
    new_bill(page)
    x, y = center(page.locator("#dialog-text"))
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(10, 10, steps=5)
    page.mouse.up()
    page.wait_for_timeout(100)
    still_open = page.locator("dialog.dialog").evaluate("(d) => d.open")
    run.check("drag from the dialog text to the backdrop does not close the dialog", still_open is True, f"open={still_open}")
    s.close()

    # c. a click on the dialog's own padding keeps it open
    s = run.session(seed=seeds.S2)
    page = s.open()
    new_bill(page)
    box = page.locator("dialog.dialog").bounding_box()
    page.mouse.click(box["x"] + 3, box["y"] + 3)
    page.wait_for_timeout(100)
    open_after_padding = page.locator("dialog.dialog").evaluate("(d) => d.open")
    run.check("a click on the dialog padding (inside the box) keeps it open", open_after_padding is True, f"open={open_after_padding}")
    s.close()

    # d. focus after a click on the non-focusable text, then Tab and Shift+Tab
    s = run.session(seed=seeds.S2)
    page = s.open()
    new_bill(page)
    x, y = center(page.locator("#dialog-title"))
    page.mouse.click(x, y)
    active_after_click = page.evaluate("document.activeElement.tagName + ':' + (document.activeElement.textContent || '').trim().slice(0, 20)")
    run.note("active element after a click on the dialog title", active_after_click)
    seen = []
    for key in ["Tab", "Tab", "Tab", "Shift+Tab", "Shift+Tab", "Shift+Tab"]:
        page.keyboard.press(key)
        seen.append(page.evaluate("document.activeElement.tagName + ':' + (document.activeElement.textContent || '').trim().slice(0, 20)"))
    run.note("focus path after the title click and Tab x3, Shift+Tab x3", seen)
    inside = all(item.startswith("BUTTON:") for item in seen)
    run.check("after a click on the dialog title, Tab and Shift+Tab stay on the two buttons", inside, str(seen))
    s.close()

    # e. a held Enter on New bill (auto repeat)
    s = run.session(seed=seeds.S2)
    page = s.open()
    page.get_by_role("button", name="New bill", exact=True).focus()
    page.keyboard.down("Enter")
    page.keyboard.down("Enter")
    page.keyboard.down("Enter")
    page.keyboard.up("Enter")
    page.wait_for_timeout(100)
    open_now = page.locator("dialog.dialog").evaluate("(d) => d.open")
    run.note("held Enter on New bill (three keydowns, the 2nd and 3rd are repeats): dialog open afterwards", open_now)
    s.close()
finally:
    run.stop()
    run.save("probe-dialog.json")
