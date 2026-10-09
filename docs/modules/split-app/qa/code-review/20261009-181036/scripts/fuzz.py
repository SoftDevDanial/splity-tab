"""Random real-gesture sessions against the shipped app (scratch copy), with invariants after each step.
Usage: python fuzz.py <seed> <steps>. Gestures only (clicks, keys). Reads state with evaluate. (Record copy, see cr.py.)
Invariants: no page error, no console error; draft ids/counts equal the DOM; focus rules R34; error/aria-invalid pairing;
dialog closes with focus on New bill; draft always readable by JSON.parse and keeps ids unique.
Run: seeds 1 (120 steps), 2, 3 and 4 (200 steps each). 0 failures."""
import json
import random
import sys
sys.path.insert(0, "{temp}/claude/{project-id}/0fc4b490-9bf0-46ec-8ac8-08b33bc21485/scratchpad")
import cr

seed, steps = int(sys.argv[1]), int(sys.argv[2])
rng = random.Random(seed)
run = cr.Run().start()
TOKENS = ["1", "5.", "abc", "12.50", "0", "31", "x", "100", "7.255", " ", "9999999", "Ben", "Aisyah Binti", "<b>", "é", "00.10"]


def state(page):
    return page.evaluate("""() => ({
      people: [...document.querySelectorAll('li.person input')].map((i) => i.value),
      items: document.querySelectorAll('li.item').length,
      mode: document.querySelector('input[name=mode]:checked').value,
      active: document.activeElement.getAttribute('aria-label') || document.activeElement.id || document.activeElement.textContent.trim(),
      errors: document.querySelectorAll('p.error').length,
      invalid: document.querySelectorAll('[aria-invalid=true]').length,
      dialogOpen: document.querySelector('dialog').open,
      removeEnabled: [...document.querySelectorAll('li.person button')].filter((b) => !b.disabled).length,
      stored: localStorage.getItem('split.draft'),
    })""")


failures = []
try:
    s = run.session(viewport=(390, 844))
    page = s.open()

    def fail(step, what):
        failures.append(f"seed {seed} step {step}: {what}")
        print("FAIL", failures[-1], flush=True)

    def visible_inputs():
        return page.locator("input[type=text]:visible").all()

    for step in range(steps):
        st = state(page)
        action = rng.choice(["type", "type", "type", "blur-key", "blur-mouse", "addp", "rmp", "additem", "rmitem", "toggle",
                             "toggle", "mode", "copy", "dialog", "reload", "clickfield"])
        expected_active = None
        try:
            if action == "type":
                fields = visible_inputs()
                f = rng.choice(fields)
                f.click()
                if rng.random() < 0.5:
                    page.keyboard.press("Control+A")
                if rng.random() < 0.2:
                    page.keyboard.press("Backspace")
                else:
                    page.keyboard.type(rng.choice(TOKENS))
            elif action == "blur-key":
                page.keyboard.press(rng.choice(["Tab", "Shift+Tab"]))
            elif action == "blur-mouse":
                box = page.locator("h1.wordmark").bounding_box()
                page.mouse.click(box["x"] + box["width"] + 30, box["y"] + 5)
            elif action == "clickfield":
                f = rng.choice(visible_inputs())
                f.click()
            elif action == "addp":
                b = page.get_by_role("button", name="Add person")
                if b.is_enabled():
                    n = len(st["people"])
                    b.click()
                    expected_active = f"Person {n + 1} name"
            elif action == "rmp":
                buttons = [b for b in page.locator("li.person button").all() if b.is_enabled()]
                if buttons:
                    k = rng.randrange(len(buttons))
                    n = len(st["people"])
                    buttons[k].click()
                    expected_active = f"Person {min(k, n - 2) + 1} name"
            elif action == "additem" and st["mode"] == "item":
                b = page.get_by_role("button", name="Add item")
                if b.is_enabled():
                    m = st["items"]
                    b.click()
                    expected_active = f"Item {m + 1} name"
            elif action == "rmitem" and st["mode"] == "item" and st["items"] > 0:
                m = st["items"]
                k = rng.randrange(m)
                page.locator("li.item").nth(k).locator("button.icon-btn").click()
                expected_active = "Add item" if m == 1 else f"Item {min(k, m - 2) + 1} name"
            elif action == "toggle" and st["mode"] == "item" and st["items"] > 0:
                taps = page.locator("li.item button.tap").all()
                rng.choice(taps).click()
            elif action == "mode":
                page.get_by_text(rng.choice(["Even", "By item"]), exact=True).click()
            elif action == "copy":
                b = page.locator("button.copy")
                if b.count():
                    b.click()
            elif action == "dialog":
                page.get_by_role("button", name="New bill", exact=True).click()
                how = rng.choice(["cancel", "esc", "backdrop", "start"])
                if how == "cancel":
                    page.get_by_role("button", name="Cancel").click()
                elif how == "esc":
                    page.keyboard.press("Escape")
                elif how == "backdrop":
                    page.mouse.click(8, 8)
                else:
                    page.get_by_role("button", name="Start new bill").click()
                page.wait_for_timeout(30)
                after = state(page)
                if after["dialogOpen"]:
                    fail(step, f"dialog still open after {how}")
                if after["active"] != "New bill":
                    fail(step, f"focus after {how} is {after['active']!r}")
            elif action == "reload":
                page.reload()
        except Exception as error:  # a gesture that cannot be made (covered, detached) is itself worth a look
            fail(step, f"{action} raised {type(error).__name__}: {str(error)[:150]}")
            continue

        after = state(page)
        if expected_active is not None and after["active"] != expected_active:
            fail(step, f"{action}: focus is {after['active']!r}, expected {expected_active!r}")
        stored = after["stored"]
        if stored is not None:
            try:
                bill = json.loads(stored)["bill"]
                ids = [p["id"] for p in bill["people"]] + [i["id"] for i in bill["items"]]
                if len(ids) != len(set(ids)):
                    fail(step, "duplicate ids in the draft")
                if [p["name"] for p in bill["people"]] != after["people"]:
                    fail(step, f"draft names {[p['name'] for p in bill['people']]} differ from the screen {after['people']}")
                if len(bill["items"]) != after["items"]:
                    fail(step, "draft item count differs from the screen")
                if bill["mode"] != after["mode"]:
                    fail(step, "draft mode differs from the screen")
                for item in bill["items"]:
                    if not set(item["who"]) <= {p["id"] for p in bill["people"]}:
                        fail(step, "an item names a person who is gone")
            except Exception as error:
                fail(step, f"draft unreadable: {error}")
        if after["errors"] != after["invalid"]:
            fail(step, f"errors on screen {after['errors']} but aria-invalid {after['invalid']}")
        if s.errors:
            fail(step, f"page errors {s.errors}")
            s.errors.clear()
        bad = [t for k, t in s.console if k == "error" or "Content Security Policy" in t]
        if bad:
            fail(step, f"console {bad[:2]}")
            s.console.clear()
    run.note(f"seed {seed}: {steps} steps", {"failures": len(failures)})
    s.close()
finally:
    run.stop()
    run.results.append({"failures": failures})
    run.save(f"fuzz-seed-{seed}.json")
print("DONE seed", seed, "failures", len(failures))
