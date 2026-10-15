"""Read-only probe for the README Known limits row "A double click on Dismiss note or a mode label moves keyboard focus
to the page. No data changes" (1.0). Runs inside a scratch copy of the project through its own conftest (open_app,
headless, clipboard stand-in loaded). Asserts nothing about the app, it prints one line per case for the reviewer."""
import json

import seeds

SIZES = [(390, 844), (360, 780), (1280, 800)]
DESCRIBE_JS = """(el) => el ? (el.id ? '#' + el.id : (el.getAttribute('aria-label') || el.localName + (el.className ? '.' + el.className : ''))) : null"""
ACTIVE_JS = f"() => ({DESCRIBE_JS})(document.activeElement)"
UNDER_JS = f"([x, y]) => ({DESCRIBE_JS})(document.elementFromPoint(x, y))"
SECTIONS_JS = """() => ['#peopleBtn', '#chargesBtn'].map((s) => { const b = document.querySelector(s);
  return b ? (b.checkVisibility() ? b.getAttribute('aria-expanded') : 'hidden') : 'absent'; })"""
STORED_JS = "() => localStorage.getItem('split.draft')"
NOTE_JS = "() => !!document.querySelector('#dismissNote')"


def centre(page, selector):
    box = page.locator(selector).bounding_box()
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def snapshot(page, point):
    return {"active": page.evaluate(ACTIVE_JS), "under": page.evaluate(UNDER_JS, list(point)),
            "sections": page.evaluate(SECTIONS_JS), "note": page.evaluate(NOTE_JS)}


def test_probe_known_limit(open_app):
    lines = []
    for width, height in SIZES:
        for gesture in ("click", "dblclick"):
            page = open_app(seed=seeds.UNREADABLE["B1"], viewport=(width, height)).page
            point = centre(page, "#dismissNote")
            before = {**snapshot(page, point), "stored": page.evaluate(STORED_JS)}
            getattr(page.mouse, gesture)(*point)
            page.wait_for_timeout(50)
            after = snapshot(page, point)
            same = page.evaluate(STORED_JS) == before["stored"]
            lines.append(f"dismiss-note {width}x{height} {gesture}: before {json.dumps({k: v for k, v in before.items() if k != 'stored'})} "
                         f"after {json.dumps(after)} stored-unchanged {same}")
        for label in ("modeEven", "modeItem"):
            for gesture in ("click", "dblclick"):
                page = open_app(seed=seeds.S1, viewport=(width, height)).page
                selector = f"label[for={label}]"
                page.locator(selector).scroll_into_view_if_needed()
                point = centre(page, selector)
                stored = page.evaluate(STORED_JS)
                getattr(page.mouse, gesture)(*point)
                page.wait_for_timeout(50)
                mode = json.loads(page.evaluate(STORED_JS) or "{}").get("bill", {}).get("mode")
                lines.append(f"mode-label {label} {width}x{height} {gesture}: active {page.evaluate(ACTIVE_JS)} "
                             f"under {page.evaluate(UNDER_JS, list(point))} mode {mode} stored-unchanged {page.evaluate(STORED_JS) == stored}")
    print("\nPROBE-BEGIN\n" + "\n".join(lines) + "\nPROBE-END")
