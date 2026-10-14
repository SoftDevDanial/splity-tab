"""Helpers shared by the browser tests: the R3 DOM walk, static scans of the shipped files, page shortcuts."""
import re

import rig

ROOT = rig.ROOT
GOLDEN_DIR = ROOT / "docs" / "design"
# The 1.0 goldens that 1.0 tests still read, byte copies from tag v1.0.0, because the v1.1.0 finalize replaced
# them in GOLDEN_DIR. Test data only. Gone after task A8 rewrites the last reader (spec, "The 1.0 golden fixtures").
GOLDEN_V1_DIR = ROOT / "tests" / "fixtures" / "design-v1.0.0"

CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; "
       "base-uri 'none'; form-action 'none'")
STORAGE_DIR = ROOT / "tests" / "browser" / "storage"


def storage_driver(name):
    """The init script of one storage driver in STORAGE_DIR (qa.md How to run), "fail-set" (D-a), "fail-get" (D-b),
    "fail-getitem" (D-c) or "count-set" (the write counter). A test passes it to open_app in init_scripts."""
    return (STORAGE_DIR / f"{name}.js").read_text(encoding="utf-8")

# The R3 walk (spec R3 and its allowed differences). Compares tag, class list, own text, every aria-* attribute,
# the attributes in KEEP, the href of every use, and an input's value and checked properties (the property, so the
# golden's value attribute and the app's value property meet, difference 1). It skips every element whose computed
# display is none with what is inside it, which takes in a closed dialog (difference 6), and the golden's div.backdrop
# stand-ins for ::backdrop (difference 3). span.sec-txt is compared by its visible text, because bill-twelve draws the
# app's one fitted text as two spans that a media query picks between (difference 9). style, data-up and data-down
# are never compared (differences 7 and 8).
DOM_WALK_JS = """(selector) => {
  const KEEP = new Set(["id", "role", "type", "name", "for", "tabindex", "data-open", "disabled", "maxlength",
    "inputmode", "autocomplete", "placeholder"]);
  const squash = (text) => text.replace(/\\s+/g, " ").trim();
  function walk(node) {
    if (getComputedStyle(node).display === "none" || node.matches("div.backdrop")) return null;
    const attrs = {};
    for (const attr of node.attributes) {
      if (attr.name.startsWith("aria-") || KEEP.has(attr.name) || (attr.name === "href" && node.localName === "use")) {
        attrs[attr.name] = attr.value;
      }
    }
    const entry = { tag: node.tagName.toLowerCase(), cls: [...node.classList].sort().join(" "), attrs };
    if (node.matches("span.sec-txt")) return { ...entry, text: squash(node.innerText), children: [] };
    entry.text = squash([...node.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join(" "));
    if (node instanceof HTMLInputElement) { entry.value = node.value; entry.checked = node.checked; }
    entry.children = [...node.children].map(walk).filter(Boolean);
    return entry;
  }
  return walk(selector ? document.querySelector(selector) : document.body);
}"""


def dom_walk(page, selector=None):
    """The walk of `document.body`, or of the first element matching `selector` (a part of the page)."""
    return page.evaluate(DOM_WALK_JS, selector)


def walk_label(entry):
    return entry["tag"] + "".join(f".{name}" for name in entry["cls"].split())


def first_diff(app, golden, path=None):
    """The first difference between two walks as a readable line that ends at the element, or None when equal."""
    path = path or walk_label(app)
    for key in ("tag", "cls", "attrs", "text", "value", "checked"):
        if app.get(key) == golden.get(key):
            continue
        if key == "attrs":
            name = next(n for n in sorted({*app["attrs"], *golden["attrs"]}) if app["attrs"].get(n) != golden["attrs"].get(n))
            return f"{path}: attr {name} app={app['attrs'].get(name)!r} golden={golden['attrs'].get(name)!r}"
        return f"{path}: {key} app={app.get(key)!r} golden={golden.get(key)!r}"
    if len(app["children"]) != len(golden["children"]):
        return (f"{path}: children app={[walk_label(child) for child in app['children']]} "
                f"golden={[walk_label(child) for child in golden['children']]}")
    for index, (a, g) in enumerate(zip(app["children"], golden["children"])):
        found = first_diff(a, g, f"{path}>{walk_label(a)}[{index}]")
        if found:
            return found
    return None


def walk_entries(walk):
    """Every entry of a walk, in document order."""
    yield walk
    for child in walk["children"]:
        yield from walk_entries(child)


# "Reads" (qa.md, phrases): every text node under an element joined with a space, then every run of white space made
# one space. The phrase says textContent, which runs two blocks together when the DOM is built by script with no
# white-space node between them (allowed difference 4), so it is read this way (BUILD.md, task A2, judgment call).
READS_JS = """(el) => { const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT), parts = [];
  while (walker.nextNode()) parts.push(walker.currentNode.textContent);
  return parts.join(' ').replace(/\\s+/g, ' ').trim(); }"""


def reads(page, selector):
    """What the element at `selector` reads, or None when the page has no such element."""
    return page.evaluate(f"(selector) => {{ const el = document.querySelector(selector); return el ? ({READS_JS})(el) : null; }}", selector)


def card_text(page):
    """"The card reads" (qa.md, phrases)."""
    return reads(page, "#rbody")


def open_golden(plain_context, name, viewport=(390, 844), folder=GOLDEN_DIR):
    """A page on one golden, opened read-only as a file from `folder` (GOLDEN_V1_DIR for a 1.0 golden), in the
    default context of qa.md How to run, so the app and the golden it is compared with share one context (task A3)."""
    context = plain_context(viewport={"width": viewport[0], "height": viewport[1]}, color_scheme="dark",
                            reduced_motion="reduce")
    page = context.new_page()
    page.goto((folder / f"{name}.html").as_uri())
    return page


def golden_walk(plain_context, name, viewport=(390, 844), selector=None, folder=GOLDEN_DIR):
    return dom_walk(open_golden(plain_context, name, viewport, folder), selector)


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
    """The visible text of the bill panel, one line per block, without the blank lines paragraphs add. The panel
    sits in the card's #rbody since the v1.1.0 shell (task A2)."""
    lines = page.locator("#rbody").inner_text().splitlines()
    return "\n".join(line.strip() for line in lines if line.strip())
