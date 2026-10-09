"""Ghost-click sweep (audit item 2): real mouse double and triple clicks and touchscreen double taps on every control.

For each control, viewport and gesture it opens a fresh context on a known bill, records the page state, does
one gesture at the centre of the control, and records the state again. A single click on the same control in
a fresh context is the baseline. The event log (every mousedown, mouseup, click, dblclick: detail, target,
whether it reached the page) says which control each click of the gesture hit.

Read the verdict columns: data_equal_single (draft, people, items, mode, texts), data_equal_initial (the
gesture changed nothing) and ui_equal_single (dialog open, note, status line, focused control).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import seeds  # noqa: E402

VP = {"360x640": (360, 640), "390x844": (390, 844), "1280x800": (1280, 800)}


def people(count):
    return seeds.changed(seeds.S2, lambda d: d["bill"].update(
        people=[{"id": f"p{n}", "name": f"P{n}"} for n in range(1, count + 1)], nextId=count + 1))


FOUR, FIVE = people(4), people(5)
ONE_ITEM = seeds.changed(seeds.S1, lambda d: d["bill"].update(items=d["bill"]["items"][:1]))
NO_ITEMS_BY_ITEM = seeds.with_bill(seeds.S1, items=[], nextId=4)
NOTE_SEED = seeds.UNREADABLE["B1"]


def by_name(name):
    return lambda page: page.get_by_role("button", name=name, exact=True)


def open_dialog(page):
    page.get_by_role("button", name="New bill", exact=True).click()
    common.settle(page)


def no_setup(page):
    pass


def toggle_ben_on_item1(page):
    return page.get_by_role("group", name="Who had Nasi lemak ayam").get_by_role("button", name="Ben", exact=True)


# name, seed, setup, locator (or None), fixed point (or callable), listed (the 13 controls the owner named)
CONTROLS = [
    dict(name="new-bill", seed=seeds.S1, setup=no_setup, loc=by_name("New bill"), listed=True),
    dict(name="start-new-bill", seed=seeds.S1, setup=open_dialog, loc=by_name("Start new bill"), listed=True),
    dict(name="cancel", seed=seeds.S1, setup=open_dialog, loc=by_name("Cancel"), listed=True),
    dict(name="backdrop-corner", seed=seeds.S1, setup=open_dialog, point=lambda page: (10, 10), listed=True),
    dict(name="remove-person-middle", seed=FIVE, setup=no_setup, loc=by_name("Remove P2"), listed=True),
    dict(name="remove-item-middle", seed=seeds.S1, setup=no_setup, loc=by_name("Remove Char kuey teow"), listed=True),
    dict(name="add-person-from-2", seed=None, setup=no_setup, loc=by_name("Add person"), listed=True),
    dict(name="add-item-from-4", seed=seeds.S1, setup=no_setup, loc=by_name("Add item"), listed=True),
    dict(name="toggle", seed=seeds.S1, setup=no_setup, loc=toggle_ben_on_item1, listed=True),
    dict(name="mode-by-item", seed=seeds.S2, setup=no_setup, loc=lambda page: page.locator("label[for=mode-item]"), listed=True),
    dict(name="mode-even", seed=seeds.S1, setup=no_setup, loc=lambda page: page.locator("label[for=mode-even]"), listed=True),
    dict(name="copy-summary", seed=seeds.S2, setup=no_setup, loc=by_name("Copy summary"), listed=True),
    dict(name="dismiss-note", seed=NOTE_SEED, setup=no_setup, loc=by_name("Dismiss note"), listed=True),
    # variants where the layout under the pointer differs
    dict(name="backdrop-over-add-person", seed=seeds.S1, setup=no_setup, loc=by_name("Add person"), over_backdrop=True, listed=False),
    dict(name="remove-person-last-of-4", seed=FOUR, setup=no_setup, loc=by_name("Remove P4"), listed=False),
    dict(name="remove-person-last-of-5", seed=FIVE, setup=no_setup, loc=by_name("Remove P5"), listed=False),
    dict(name="remove-item-last-of-4", seed=seeds.S1, setup=no_setup, loc=by_name("Remove Satay, 10 sticks"), listed=False),
    dict(name="remove-item-only", seed=ONE_ITEM, setup=no_setup, loc=by_name("Remove Nasi lemak ayam"), listed=False),
    dict(name="add-person-from-3", seed=seeds.S2, setup=no_setup, loc=by_name("Add person"), listed=False),
    dict(name="add-person-from-5", seed=FIVE, setup=no_setup, loc=by_name("Add person"), listed=False),
    dict(name="add-item-from-0", seed=NO_ITEMS_BY_ITEM, setup=no_setup, loc=by_name("Add item"), listed=False),
]

LISTED_GESTURES = [("360x640", "dbl"), ("390x844", "dbl"), ("1280x800", "dbl"), ("360x640", "triple"), ("1280x800", "triple"),
                   ("360x640", "tap2"), ("390x844", "tap2")]
VARIANT_GESTURES = [("360x640", "dbl"), ("390x844", "dbl"), ("1280x800", "dbl"), ("360x640", "tap2")]

DATA_KEYS = ["draft", "mode", "people", "items", "subtotal", "service", "sst"]
UI_KEYS = ["dialogOpen", "note", "status", "focus"]


def point_for(page, control):
    if "point" in control:
        return control["point"](page)
    loc = control["loc"](page)
    if control.get("over_backdrop"):
        box = loc.bounding_box()
        return (box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    return common.centre(loc)


def run_once(browser, base, control, vp_name, gesture):
    """One fresh context. gesture: 'single', 'dbl', 'triple' or 'tap2'. Returns (before, after, events, problems)."""
    touch = gesture == "tap2"
    ctx, page, cap = common.open_page(browser, base, seed=control["seed"], viewport=VP[vp_name], touch=touch)
    try:
        common.settle(page)
        point = None
        if control.get("over_backdrop"):
            point = point_for(page, control)  # measured before the dialog hides the page
        control["setup"](page)
        if control.get("over_backdrop"):
            open_dialog(page)
        else:
            point = point_for(page, control)
        before = common.snap(page)
        page.evaluate("() => { window.evlog = []; }")
        x, y = point
        if gesture == "single":
            page.mouse.click(x, y)
        elif gesture == "dbl":
            page.mouse.dblclick(x, y)
        elif gesture == "triple":
            page.mouse.click(x, y, click_count=3)
        elif gesture == "tap2":
            page.touchscreen.tap(x, y)
            page.touchscreen.tap(x, y)
        common.settle(page, 200)
        after = common.snap(page)
        events = page.evaluate("() => window.evlog")
        problems = cap.problems(base) + ([f"cg7 violations {n}"] if (n := page.evaluate("window.cg7Violations")) else [])
        return before, after, events, problems, (round(x), round(y))
    finally:
        ctx.close()


def pick(snapshot, keys):
    return {k: snapshot[k] for k in keys}


def summarise_events(events):
    return [f"{e['type']}:{e['detail']}:{e['target']}:{'reached' if e['reached'] else 'SWALLOWED'}" for e in events if e["type"] in ("mousedown", "click")]


def body(browser, server, results):
    base = server.base
    baselines = {}
    for control in CONTROLS:
        gestures = LISTED_GESTURES if control["listed"] else VARIANT_GESTURES
        for vp_name in dict.fromkeys(v for v, _ in gestures):
            before, after, events, problems, point = run_once(browser, base, control, vp_name, "single")
            baselines[(control["name"], vp_name)] = (before, after)
        for vp_name, gesture in gestures:
            before, after, events, problems, point = run_once(browser, base, control, vp_name, gesture)
            single_before, single = baselines[(control["name"], vp_name)]
            row = {
                "control": control["name"], "viewport": vp_name, "gesture": gesture, "point": point,
                "data_equal_initial": pick(after, DATA_KEYS) == pick(before, DATA_KEYS),
                "data_equal_single": pick(after, DATA_KEYS) == pick(single, DATA_KEYS),
                "ui_equal_single": pick(after, UI_KEYS) == pick(single, UI_KEYS),
                "events": summarise_events(events), "problems": problems,
                "after": {k: after[k] for k in ("mode", "people", "items", "dialogOpen", "note", "status", "focus")},
                "single": {k: single[k] for k in ("mode", "people", "items", "dialogOpen", "note", "status", "focus")},
                "before_draft": before["draft"], "after_draft": after["draft"],
            }
            results["cases"].append(row)
            flag = "" if row["data_equal_single"] and row["ui_equal_single"] else "  <-- differs from a single click"
            print(f"{control['name']:28} {vp_name:9} {gesture:6} data==single {row['data_equal_single']!s:5} "
                  f"data==initial {row['data_equal_initial']!s:5} ui==single {row['ui_equal_single']!s:5}{flag}")
            for line in row["events"]:
                if flag:
                    print("      ", line)
            if problems:
                print("      PROBLEMS", problems)


if __name__ == "__main__":
    common.run_probe("p6-ghost-sweep", body)
