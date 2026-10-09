"""Does UIEvent.detail (the click count) mark the second click of a double click / double tap?
Used only to give the solver a fix that is known to work in Chromium. (Record copy, see cr.py.)
Note: Playwright's mouse.click() sends clickCount 1 each time, so the mouse rows here show detail 1.
A real double click (or Playwright's mouse.dblclick) sends 1 then 2."""
import sys
sys.path.insert(0, "{temp}/claude/{project-id}/0fc4b490-9bf0-46ec-8ac8-08b33bc21485/scratchpad")
import cr

run = cr.Run().start()
try:
    seeds = run.seeds
    for how, gap in [("mouse", 0), ("mouse", 80), ("mouse", 250), ("touch", 0), ("touch", 60), ("touch", 200), ("touch", 400)]:
        s = run.session(seed=seeds.S1, viewport=(375, 667), touch=(how == "touch"))
        page = s.open()
        page.evaluate("""() => { window.testDetails = [];
          document.addEventListener('click', (e) => window.testDetails.push([e.target.textContent.trim().slice(0, 12), e.detail]), true); }""")
        page.get_by_role("button", name="New bill", exact=True).click()
        box = page.get_by_role("button", name="Cancel").bounding_box()
        x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        if how == "mouse":
            page.mouse.click(x, y)
            page.wait_for_timeout(gap)
            page.mouse.click(x, y)
        else:
            page.touchscreen.tap(x, y)
            page.wait_for_timeout(gap)
            page.touchscreen.tap(x, y)
        page.wait_for_timeout(100)
        run.note(f"click details, {how}, gap {gap} ms (target text, detail)", page.evaluate("window.testDetails"))
        s.close()
finally:
    run.stop()
    run.save("probe-detail.json")
