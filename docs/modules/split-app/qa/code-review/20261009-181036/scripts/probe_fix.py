"""Does a proposed fix work? Usage: python probe_fix.py <tree> <label> <dialog|remove>  (Record copy, see cr.py.)
dialog: double click / double tap on Cancel, on the backdrop and on Start new bill must change nothing under the dialog;
        a single click must still close it with focus on New bill.
remove: a double click / double tap on a Remove button removes one row; a slow second click (700 ms) removes a second one."""
import sys
sys.path.insert(0, "{temp}/claude/{project-id}/0fc4b490-9bf0-46ec-8ac8-08b33bc21485/scratchpad")
import cr

tree, label, part = sys.argv[1], sys.argv[2], sys.argv[3]
run = cr.Run(tree).start()
try:
    seeds = run.seeds

    def centre(locator):
        box = locator.bounding_box()
        return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2

    def twice(page, how, x, y, gap=0):
        if how == "mouse" and gap == 0:
            page.mouse.dblclick(x, y)
        elif how == "mouse":
            page.mouse.click(x, y)
            page.wait_for_timeout(gap)
            page.mouse.click(x, y)
        else:
            page.touchscreen.tap(x, y)
            page.wait_for_timeout(gap)
            page.touchscreen.tap(x, y)

    if part == "dialog":
        for viewport in [(375, 667), (360, 640), (412, 732)]:
            for how in ["mouse", "touch"]:
                for target in ["Cancel", "backdrop", "Start new bill"]:
                    s = run.session(seed=seeds.S1, viewport=viewport, touch=(how == "touch"))
                    page = s.open()
                    before = s.stored()
                    page.get_by_role("button", name="New bill", exact=True).click()
                    if target == "backdrop":
                        x, y = 12, 12
                    else:
                        x, y = centre(page.get_by_role("button", name=target, exact=True))
                    twice(page, how, x, y)
                    page.wait_for_timeout(120)
                    after = s.stored()
                    closed = page.locator("dialog.dialog").evaluate("(d) => !d.open")
                    if target == "Start new bill":
                        fresh = seeds.dump({"version": 1, "bill": {"mode": "even", "people": [{"id": "p1", "name": "Person 1"}, {"id": "p2", "name": "Person 2"}],
                                                                   "subtotalText": "", "items": [], "serviceText": "10", "sstText": "6", "nextId": 3}})
                        ok = after == fresh and closed
                    else:
                        ok = after == before and closed
                    run.check(f"[{label}] double {how} on {target} at {viewport}: nothing under the dialog changes", ok,
                              f"closed={closed} draft_same={after == before}")
                    s.close()
        s = run.session(seed=seeds.S1, viewport=(375, 667))
        page = s.open()
        page.get_by_role("button", name="New bill", exact=True).click()
        page.get_by_role("button", name="Cancel", exact=True).click()
        page.wait_for_timeout(100)
        focus = page.evaluate("document.activeElement.textContent.trim()")
        run.check(f"[{label}] single click on Cancel still closes with focus on New bill", focus == "New bill", f"focus={focus}")
        # a later, unrelated double click must behave as before (the one-shot guard must not linger):
        # a double click on a toggle flips it twice, so it ends as it started
        toggle = page.get_by_role("group", name="Who had Char kuey teow", exact=True).get_by_role("button", name="Aisyah", exact=True)
        was = toggle.get_attribute("aria-pressed")
        page.wait_for_timeout(50)
        toggle.dblclick()
        now = toggle.get_attribute("aria-pressed")
        run.check(f"[{label}] a later double click on a toggle still flips it twice", now == was, f"before={was} after={now}")
        s.close()

    if part == "remove":
        for how in ["mouse", "touch"]:
            s = run.session(seed=seeds.S1, viewport=(390, 844), touch=(how == "touch"))
            page = s.open()
            x, y = centre(page.get_by_role("button", name="Remove Char kuey teow", exact=True))
            twice(page, how, x, y)
            page.wait_for_timeout(120)
            left = page.locator("li.item").count()
            run.check(f"[{label}] double {how} on Remove (item 2 of 4) removes one row", left == 3, f"items left={left}")
            s.close()
            five = seeds.changed(seeds.S2, lambda d: d["bill"].update(
                people=[{"id": f"p{n}", "name": f"P{n}"} for n in range(1, 6)], nextId=6))
            s = run.session(seed=five, viewport=(390, 844), touch=(how == "touch"))
            page = s.open()
            x, y = centre(page.get_by_role("button", name="Remove P2", exact=True))
            twice(page, how, x, y)
            page.wait_for_timeout(120)
            left = page.locator("li.person").count()
            run.check(f"[{label}] double {how} on Remove (person 2 of 5) removes one row", left == 4, f"people left={left}")
            s.close()
        s = run.session(seed=seeds.S1, viewport=(390, 844))
        page = s.open()
        x, y = centre(page.get_by_role("button", name="Remove Char kuey teow", exact=True))
        page.mouse.click(x, y)
        run.check(f"[{label}] single click on Remove removes one row", page.locator("li.item").count() == 3)
        page.wait_for_timeout(700)
        page.mouse.click(x, y)
        left = page.locator("li.item").count()
        run.check(f"[{label}] a second, slow click (700 ms later) removes another row", left == 2, f"items left={left}")
        s.close()
finally:
    run.stop()
    run.save(f"probe-fix-{label}.json")
