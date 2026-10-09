"""Scenarios that kill the surviving mutants. Run once per tree: python probe_kill.py <tree> <label>.
The shipped code (tree = base) must pass all of them. A mutant that fails one is a hole the suite does not cover.
(Record copy. It ran from the session scratchpad next to cr.py.)"""
import sys
sys.path.insert(0, "{temp}/claude/{project-id}/0fc4b490-9bf0-46ec-8ac8-08b33bc21485/scratchpad")
import cr

tree, label = sys.argv[1], sys.argv[2]
run = cr.Run(tree).start()
try:
    seeds = run.seeds

    def errors(page):
        return page.locator("p.error").count()

    def centre(locator):
        box = locator.bounding_box()
        return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2

    # K1: an error that was shown and then cleared by typing must not come back while the field keeps focus (R10 c).
    s = run.session()
    page = s.open()
    sub = page.get_by_role("textbox", name="Subtotal in RM", exact=True)
    sub.click()
    page.keyboard.type("abc")
    page.keyboard.press("Tab")
    shown = errors(page) == 1
    sub.click()
    page.keyboard.press("Control+A")
    page.keyboard.type("5")
    gone = errors(page) == 0
    page.keyboard.type("x")  # "5x" is bad again, and the field still has focus
    early = errors(page)
    run.check(f"[{label}] K1 error shown on blur, gone at valid text", shown and gone, f"shown={shown} gone={gone}")
    run.check(f"[{label}] K1 bad text typed again does NOT bring the error back before blur (R10 c)", early == 0, f"errors={early}")
    page.keyboard.press("Tab")
    run.check(f"[{label}] K1 the error returns when the field is left again", errors(page) == 1, f"errors={errors(page)}")
    s.close()

    # K2: a press that ends must not re-run an old blur handler (RD-3 helper runs each waiting handler once).
    s = run.session()
    page = s.open()
    sub = page.get_by_role("textbox", name="Subtotal in RM", exact=True)
    sub.click()
    page.keyboard.type("abc")
    bx = page.locator("h1.wordmark").bounding_box()
    page.mouse.move(bx["x"] + bx["width"] + 40, bx["y"] + bx["height"] / 2)  # blank header space
    page.mouse.down()
    held = errors(page)
    page.mouse.up()
    first = errors(page)
    run.check(f"[{label}] K2 the press on blank space waits, then shows the error", held == 0 and first == 1, f"held={held} after={first}")
    sub.click()
    page.keyboard.press("Control+A")
    page.keyboard.type("5")
    page.keyboard.type("x")
    before = errors(page)
    x, y = centre(sub)
    page.mouse.click(x, y)  # a press inside the focused field: no blur, nothing should run
    after = errors(page)
    run.check(f"[{label}] K2 a click inside the focused field does not show a stale error", before == 0 and after == 0, f"before={before} after={after}")
    s.close()

    # K3: a key press ends a press that never reported its end, so a keyboard blur shows its error at once.
    s = run.session()
    page = s.open()
    sub = page.get_by_role("textbox", name="Subtotal in RM", exact=True)
    sub.click()
    page.keyboard.type("abc")
    x, y = centre(sub)
    page.mouse.move(x, y)
    page.mouse.down()  # pressed inside the focused field, no release yet
    page.keyboard.press("Tab")
    at_once = errors(page)
    page.mouse.up()
    run.check(f"[{label}] K3 a keyboard blur during an unfinished press shows the error at once", at_once == 1, f"errors_before_release={at_once}")
    s.close()

    # K4: the draft keeps the removal of an item (R25 each click that changes the bill).
    s = run.session(seed=seeds.S1)
    page = s.open()
    page.get_by_role("button", name="Remove Char kuey teow", exact=True).click()
    stored_items = page.evaluate("JSON.parse(localStorage.getItem('split.draft')).bill.items.length")
    run.check(f"[{label}] K4 removing an item is saved", stored_items == 3, f"stored items={stored_items}")
    s.close()

    # K5: a click on the padding of the dialog keeps the dialog open (R30).
    s = run.session(seed=seeds.S2)
    page = s.open()
    page.get_by_role("button", name="New bill", exact=True).click()
    box = page.locator("dialog.dialog").bounding_box()
    page.mouse.click(box["x"] + 3, box["y"] + 3)
    open_after = page.locator("dialog.dialog").evaluate("(d) => d.open")
    run.check(f"[{label}] K5 a click inside the dialog box keeps it open", open_after is True, f"open={open_after}")
    s.close()

    # K6: S7 note markup has no stray live region or aria attribute (R27 DOM contract, R16 live regions).
    s = run.session(seed=seeds.UNREADABLE["B1"])
    page = s.open()
    stray = page.evaluate("""() => [...document.querySelectorAll('.note-wrap, .note-wrap *')].flatMap((e) =>
      [...e.attributes].filter((a) => a.name.startsWith('aria-') && !(e.tagName === 'BUTTON' && a.name === 'aria-label' && a.value === 'Dismiss note') && a.name !== 'aria-hidden').map((a) => a.name))""")
    run.check(f"[{label}] K6 the note carries no stray aria attribute", stray == [], f"stray={stray}")
    s.close()
finally:
    run.stop()
    run.save(f"probe-kill-{label}.json")
