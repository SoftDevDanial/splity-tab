"""Helpers shared by the browser tests: the R3 DOM walk, static scans of the shipped files, page shortcuts."""
import re

import rig

ROOT = rig.ROOT
GOLDEN_DIR = ROOT / "docs" / "design"

CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; "
       "base-uri 'none'; form-action 'none'")

# The R3 walk. Compares tag, class list, id, own text, role, every aria-* attribute, disabled, type, name,
# for, scope, maxlength, inputmode, autocomplete, the svg attributes, and the input value and checked
# properties. It skips every element whose computed display is none (a closed dialog, p.status when empty)
# and, on the name inputs, the placeholder (allowed difference 2; R4 and R11 test it on its own).
DOM_WALK_JS = """() => {
  const KEEP = new Set(["id", "role", "disabled", "type", "name", "for", "scope", "maxlength", "inputmode",
    "autocomplete", "viewBox", "focusable", "d", "placeholder"]);
  const NAME_INPUT = /^(Person|Item) \\d+ name$/;
  function walk(node) {
    if (getComputedStyle(node).display === "none") return null;
    const attrs = {};
    for (const attr of node.attributes) {
      if (!(attr.name.startsWith("aria-") || KEEP.has(attr.name))) continue;
      if (attr.name === "placeholder" && NAME_INPUT.test(node.getAttribute("aria-label") || "")) continue;
      attrs[attr.name] = attr.value;
    }
    const text = [...node.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join(" ")
      .replace(/\\s+/g, " ").trim();
    const entry = { tag: node.tagName.toLowerCase(), cls: [...node.classList].sort().join(" "), attrs, text };
    if (node instanceof HTMLInputElement) { entry.value = node.value; entry.checked = node.checked; }
    entry.children = [...node.children].map(walk).filter(Boolean);
    return entry;
  }
  return walk(document.body);
}"""


def dom_walk(page):
    return page.evaluate(DOM_WALK_JS)


def first_diff(app, golden, path="body"):
    """The first difference between two walks as a readable line, or None when they are equal."""
    for key in ("tag", "cls", "attrs", "text", "value", "checked"):
        if app.get(key) != golden.get(key):
            return f"{path}: {key} app={app.get(key)!r} golden={golden.get(key)!r}"
    here = f"{path}>{app['tag']}" + (f".{app['cls'].replace(' ', '.')}" if app["cls"] else "")
    if len(app["children"]) != len(golden["children"]):
        tags = lambda entry: [child["tag"] + ("." + child["cls"].replace(" ", ".") if child["cls"] else "") for child in entry["children"]]
        return f"{here}: children app={tags(app)} golden={tags(golden)}"
    for index, (a, g) in enumerate(zip(app["children"], golden["children"])):
        found = first_diff(a, g, f"{here}[{index}]")
        if found:
            return found
    return None


def open_golden(plain_context, name, viewport=(390, 844)):
    """A page on one golden, opened read-only as a file."""
    context = plain_context(viewport={"width": viewport[0], "height": viewport[1]}, color_scheme="light")
    page = context.new_page()
    page.goto((GOLDEN_DIR / f"{name}.html").as_uri())
    return page


def golden_walk(plain_context, name, viewport=(390, 844)):
    return dom_walk(open_golden(plain_context, name, viewport))


# "Equal to the specimen" (qa.md, phrases): these computed properties, never width, height or position.
SPECIMEN_PROPS = ["color", "backgroundColor", "fontSize", "fontWeight", "boxShadow",
                  *(f"border{side}{kind}" for side in ("Top", "Right", "Bottom", "Left") for kind in ("Width", "Style", "Color")),
                  *(f"padding{side}" for side in ("Top", "Right", "Bottom", "Left")),
                  *(f"border{corner}Radius" for corner in ("TopLeft", "TopRight", "BottomRight", "BottomLeft"))]


def specimen_props(locator, extra=()):
    """The computed properties that qa.md compares between the app and a specimen of states.html.

    Waits for the 120 ms colour transitions to end first: a control that has just changed state is
    mid-transition otherwise, and a mid-transition colour equals no specimen (R36).
    """
    locator.page.wait_for_function("() => document.getAnimations().length === 0")
    return locator.evaluate(
        "(el, names) => { const s = getComputedStyle(el); return Object.fromEntries(names.map((n) => [n, s[n]])); }",
        [*SPECIMEN_PROPS, *extra])


def replace_text(page, locator, text):
    """Click the field, select its text and type the new text key by key (qa.md, phrases)."""
    locator.click()
    page.keyboard.press("Control+A")
    if text:
        page.keyboard.type(text)
    else:
        page.keyboard.press("Backspace")


def active_label(page):
    """The aria-label (or id) of the focused element, to say where focus is."""
    return page.evaluate("document.activeElement.getAttribute('aria-label') || document.activeElement.id "
                         "|| document.activeElement.textContent.trim()")


def shipped_files():
    """index.html and every file under src/ (the files the page serves)."""
    return [ROOT / "index.html"] + sorted(path for path in (ROOT / "src").rglob("*") if path.is_file())


def shipped_text(include_core=True):
    return {path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8") for path in shipped_files()
            if include_core or "src/core/" not in path.as_posix()}


def person_field(page, number):
    return page.get_by_label(f"Person {number} name", exact=True)


def panel_text(page):
    """The visible text of the bill panel, one line per block, without the blank lines paragraphs add."""
    lines = page.locator("div.tape").inner_text().splitlines()
    return "\n".join(line.strip() for line in lines if line.strip())
