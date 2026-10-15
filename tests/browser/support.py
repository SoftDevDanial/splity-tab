"""Helpers shared by the browser tests: the R3 DOM walk, static scans of the shipped files, page shortcuts."""
import rig

ROOT = rig.ROOT
GOLDEN_DIR = ROOT / "docs" / "design"

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


# R2's first render, read in one pass so a part that is not built yet fails at once instead of waiting for it. Compared
# with expected.COLD_BOOT by test_R2_cold_boot_is_a_new_bill_with_no_seed and by the live gate's steps 1 and 8.
COLD_BOOT_JS = """() => {
  const one = (selector) => document.querySelector(selector);
  const attr = (selector, name) => one(selector)?.getAttribute(name) ?? null;
  const field = (selector) => one(selector) ? [one(selector).value, one(selector).placeholder] : null;
  const copy = one('#stripCopy');
  return {
    names: [...document.querySelectorAll('li.field.person input')].map((input) => input.value),
    removesDisabled: [...document.querySelectorAll('li.field.person button')].map((button) => button.disabled),
    evenChecked: one('#modeEven')?.checked ?? null,
    subtotal: field('#evenSub'),
    subtotalErrorHidden: one('p.err#evenErr')?.hidden ?? null,
    rates: [one('#svc')?.value ?? null, one('#sst')?.value ?? null],
    open: [attr('#peopleBlk', 'data-open'), attr('#peopleBtn', 'aria-expanded'), attr('#chargesBlk', 'data-open')],
    totalHolds: [...(one('#rbody > div.r-total')?.children ?? [])].map((el) => `${el.localName}.${el.className}`),
    emptyIcon: attr('#rbody > div.r-empty > svg.ic > use', 'href'),
    strip: one('#stripInfo')?.innerText.trim() ?? null,
    stripCopy: copy ? { shown: copy.checkVisibility(), disabled: copy.disabled } : null,
  };
}"""


def cold_boot_state(page):
    """What the page shows of R2's first render, in the shape of expected.COLD_BOOT."""
    return {**page.evaluate(COLD_BOOT_JS), "card": card_text(page)}


# The receipt of one div.rbody in one evaluate (the card's #rbody, or the sheet's from task A12), so a part the tree does
# not draw reads as null or empty and fails on its assertion at once, never on a wait. A row and the proof give their
# span.wk without its span.sr children (qa.md, before the scenarios), and null where there is none.
RECEIPT_JS = """(root) => {
  const rbody = document.querySelector(root);
  if (!rbody) return null;
  const label = (el) => el.localName + [...el.classList].map((name) => '.' + name).join('');
  const part = (selector) => rbody.querySelector(':scope > ' + selector);
  const child = (el, selector) => el.querySelector(':scope > ' + selector);
  const working = (el) => el && [...el.childNodes].filter((node) => !(node instanceof Element && node.matches('span.sr')))
    .map((node) => node.textContent).join('');
  const icon = (svg) => svg && [label(svg), svg.querySelector('use')?.getAttribute('href') ?? null];
  const total = part('div.r-total'), amount = part('div.r-total > p.r-amount'), head = part('div.r-head');
  const note = part('div.r-empty') ?? part('div.r-msg'), list = part('ul.r-splits'), check = part('div.r-check');
  const copy = part('button.r-copy'), status = part('p.status');
  return {
    blocks: [...rbody.children].map(label),
    total: total && [...total.children].map((el) => [label(el), el.id, el.textContent]),
    amount: amount && [...amount.childNodes].map((node) => node instanceof Element ? `${label(node)} ${node.textContent}` : node.textContent),
    lines: [...rbody.querySelectorAll(':scope > dl.r-lines > div')].map((row) => [...row.children].map((el) => el.textContent)),
    rule: part('div.r-rule')?.getAttribute('aria-hidden') ?? null,
    note: note && [label(note), ...[...note.children].map((el) => el.localName === 'svg' ? icon(el) : [label(el), el.textContent])],
    head: head && [...head.children].map((el) => [label(el), el.id, el.getAttribute('aria-hidden'), el.textContent]),
    list: list && { id: list.id, cls: list.className, labelledBy: list.getAttribute('aria-labelledby'),
      rowsVar: list.style.getPropertyValue('--rows'), rows: [...list.children].map((li) =>
        [child(li, 'span.nm')?.textContent ?? null, child(li, 'span.amt')?.textContent ?? null, working(child(li, 'span.wk'))]) },
    proof: check && { parts: [...check.children].map(label), seal: icon(child(check, 'svg')), id: child(check, 'span.amt')?.id ?? null,
      amount: child(check, 'span.amt')?.textContent ?? null, working: working(child(check, 'span.wk')) },
    copy: copy && [copy.id, copy.className, copy.textContent, icon(child(copy, 'svg'))],
    status: status && [status.id, status.className, status.getAttribute('role'), status.textContent],
  };
}"""


def receipt(page, root="#rbody"):
    """The receipt of the div.rbody at `root` (RECEIPT_JS), or None when the page has none."""
    return page.evaluate(RECEIPT_JS, root)


def open_golden(plain_context, name, viewport=(390, 844)):
    """A page on one golden of GOLDEN_DIR, opened read-only as a file, in the default context of qa.md How to run, so
    the app and the golden it is compared with share one context (task A3)."""
    context = plain_context(viewport={"width": viewport[0], "height": viewport[1]}, color_scheme="dark",
                            reduced_motion="reduce")
    page = context.new_page()
    page.goto((GOLDEN_DIR / f"{name}.html").as_uri())
    return page


def golden_walk(plain_context, name, viewport=(390, 844), selector=None):
    return dom_walk(open_golden(plain_context, name, viewport), selector)


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
