"""Double click / double tap on a Remove button and on Add person: how many rows change? (Record copy, see cr.py.)"""
import sys
sys.path.insert(0, "{temp}/claude/{project-id}/0fc4b490-9bf0-46ec-8ac8-08b33bc21485/scratchpad")
import cr

run = cr.Run().start()
try:
    seeds = run.seeds

    def centre(locator):
        box = locator.bounding_box()
        return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2

    def count_items(page):
        return page.locator("li.item").count()

    for how in ["mouse", "touch"]:
        # items: S1 has four items
        s = run.session(seed=seeds.S1, viewport=(390, 844), touch=(how == "touch"))
        page = s.open()
        x, y = centre(page.get_by_role("button", name="Remove Char kuey teow", exact=True))
        before = count_items(page)
        if how == "mouse":
            page.mouse.dblclick(x, y)
        else:
            page.touchscreen.tap(x, y)
            page.touchscreen.tap(x, y)
        page.wait_for_timeout(150)
        run.note(f"{how}: double activation of 'Remove Char kuey teow' (item 2 of {before}) leaves items", count_items(page))
        s.close()

        # people: five people, even mode
        five = seeds.changed(seeds.S2, lambda d: d["bill"].update(
            people=[{"id": f"p{n}", "name": f"P{n}"} for n in range(1, 6)], nextId=6))
        s = run.session(seed=five, viewport=(390, 844), touch=(how == "touch"))
        page = s.open()
        x, y = centre(page.get_by_role("button", name="Remove P2", exact=True))
        before = page.locator("li.person").count()
        if how == "mouse":
            page.mouse.dblclick(x, y)
        else:
            page.touchscreen.tap(x, y)
            page.touchscreen.tap(x, y)
        page.wait_for_timeout(150)
        run.note(f"{how}: double activation of 'Remove P2' (person 2 of {before}) leaves people", page.locator("li.person").count())
        s.close()

        # Add person: one double activation
        s = run.session(seed=seeds.S2, viewport=(390, 844), touch=(how == "touch"))
        page = s.open()
        x, y = centre(page.get_by_role("button", name="Add person"))
        before = page.locator("li.person").count()
        if how == "mouse":
            page.mouse.dblclick(x, y)
        else:
            page.touchscreen.tap(x, y)
            page.touchscreen.tap(x, y)
        page.wait_for_timeout(150)
        run.note(f"{how}: double activation of 'Add person' from {before} people leaves", page.locator("li.person").count())
        s.close()
finally:
    run.stop()
    run.save("probe-double.json")
