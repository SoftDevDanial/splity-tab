"""A draft whose person name is one grapheme cluster of many UTF-16 units passes D8. How does the page cope?
(Record copy, see cr.py.) Result: loads in 0.08, 0.12 and 0.37 s for 20,000, 200,000 and 1,000,000 marks."""
import json
import sys
import time
sys.path.insert(0, "{temp}/claude/{project-id}/0fc4b490-9bf0-46ec-8ac8-08b33bc21485/scratchpad")
import cr

run = cr.Run().start()
try:
    seeds = run.seeds
    for marks in (20_000, 200_000, 1_000_000):
        name = "a" + "\u0301" * marks
        draft = json.loads(seeds.S2)
        draft["bill"]["people"][0]["name"] = name
        text = seeds.dump(draft)
        s = run.session(seed=text)
        started = time.time()
        try:
            s.page.goto(s.base + "/", timeout=60000)
            s.page.wait_for_selector("li.person input", timeout=60000)
            loaded_at = time.time() - started
            note = s.page.locator("div.note").count()
            values = s.page.evaluate("document.querySelector('li.person input').value.length")
            t0 = time.time()
            s.page.get_by_role("textbox", name="Subtotal in RM", exact=True).fill("100.00", timeout=60000)
            reaction = time.time() - t0
            run.note(f"{marks} combining marks ({len(text) / 1e6:.2f} MB draft)",
                     {"loaded_seconds": round(loaded_at, 2), "note_shown": note, "name_units_in_field": values, "fill_subtotal_seconds": round(reaction, 2)})
        except Exception as error:  # a timeout is the finding
            run.note(f"{marks} combining marks", f"did not finish: {type(error).__name__}: {str(error)[:120]}")
        s.close()
finally:
    run.stop()
    run.save("probe-zalgo.json")
