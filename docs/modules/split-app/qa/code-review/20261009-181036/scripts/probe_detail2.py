"""Click detail for Playwright's mouse.dblclick (clickCount 1 then 2), the closest thing to a real double click.
Result: [['New bill', 1], ['Cancel', 1], ['Chen', 2]]. The second click has detail 2 and lands on the Chen toggle.
(Record copy, see cr.py.)"""
import sys
sys.path.insert(0, "{temp}/claude/{project-id}/0fc4b490-9bf0-46ec-8ac8-08b33bc21485/scratchpad")
import cr

run = cr.Run().start()
try:
    seeds = run.seeds
    s = run.session(seed=seeds.S1, viewport=(375, 667))
    page = s.open()
    page.evaluate("""() => { window.testDetails = [];
      document.addEventListener('click', (e) => window.testDetails.push([e.target.textContent.trim().slice(0, 12), e.detail]), true); }""")
    page.get_by_role("button", name="New bill", exact=True).click()
    box = page.get_by_role("button", name="Cancel").bounding_box()
    page.mouse.dblclick(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.wait_for_timeout(100)
    run.note("mouse.dblclick on Cancel: click details (target text, detail)", page.evaluate("window.testDetails"))
    s.close()
finally:
    run.stop()
    run.save("probe-detail-dblclick.json")
