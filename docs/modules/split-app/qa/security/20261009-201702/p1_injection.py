"""Threat row 1 (R37, R38): hostile names, prices and rates, typed and restored.

For every (person name, item name) pair it measures, once by real typing and once by a restored draft:
  - the element signature of the whole document equals the one of a benign pair of the same lengths (no element created),
  - window.pwned stays 0 (window.f and window.alert count themselves), no dialog opened, no CSP violation,
  - the text shows literally in the field, in an item's toggle, in the shares row, in the remove button's
    accessible name, in `Who had ...`, and in the copied text, which keeps its line count,
  - Object.prototype and Array.prototype hold no new key, and the saved draft parses back to the same names.
Then the money fields get markup: only the fixed error text appears, no element is created.
(An earlier version of this script counted the page's own head script and link as unsafe nodes; the count is now
taken inside document.body, where the app has no script, style, link or iframe.)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import seeds  # noqa: E402

PAIRS = [
    ("<svg onload=f()>", "<img src=x onerror=alert(1)>"),
    ("<script>f()</script>", "\"><script>alert(2)</script>"),
    ("</li><li>x", "<iframe srcdoc=\"<script>f()</script>\">"),
    ("</button><button>", "</li></ol><h1>owned</h1>"),
    ("<b onmouseover=f()>", "<style>*{display:none}</style>"),
    ("&lt;b&gt;&amp;x", "<a href=\"javascript:f()\">x</a>"),
    ("__proto__", "__proto__"),
    ("constructor", "constructor"),
    ("toString", "hasOwnProperty"),
    ("{{7*7}} ${f()}", "{{constructor.constructor('f()')()}}"),
]
FIXED_ERRORS = {"Enter an amount like 12.50", "Enter a rate from 0 to 30", "Enter a rate from 0 to 20"}
STANDARD_OBJECT_KEYS = ("__defineGetter__,__defineSetter__,__lookupGetter__,__lookupSetter__,__proto__,constructor,"
                        "hasOwnProperty,isPrototypeOf,propertyIsEnumerable,toLocaleString,toString,valueOf")

SIGNATURE_JS = """() => {
  const counts = {};
  for (const el of document.querySelectorAll('*')) counts[el.tagName] = (counts[el.tagName] || 0) + 1;
  return JSON.stringify(Object.entries(counts).sort());
}"""
PROTO_JS = """() => ({
  objectKeys: Object.getOwnPropertyNames(Object.prototype).sort().join(','),
  arrayExtra: Object.keys(Array.prototype).join(','),
  stray: [({}).polluted, ({}).name, ({}).id, ({}).who].filter((v) => v !== undefined).length,
})"""
UNSAFE_JS = "() => document.body.querySelectorAll('script, iframe, object, embed, style, link, img, h1:not(.wordmark), [onload], [onerror], [onclick], [onmouseover]').length"
READ_JS = """() => {
  const first = document.querySelector('li.person');
  const item = document.querySelector('li.item');
  const rows = [...document.querySelectorAll('table.shares tbody th')].map((th) => th.textContent);
  return {
    personField: first.querySelector('input').value,
    removeLabel: first.querySelector('button').getAttribute('aria-label'),
    itemField: item.querySelector('input').value,
    itemRemove: item.querySelector('button.icon-btn').getAttribute('aria-label'),
    whoLabel: item.querySelector('.who').getAttribute('aria-label'),
    toggle: item.querySelector('.who .tap').textContent,
    sharesFirstRow: rows[0],
  };
}"""
ERRORS_JS = "() => [...document.querySelectorAll('p.error')].map((p) => p.textContent)"


def seed_with(person, item):
    return seeds.changed(seeds.S1, lambda d: (d["bill"]["people"][0].update(name=person), d["bill"]["items"][0].update(name=item)))


def type_into(page, locator, text):
    locator.click()
    page.keyboard.press("Control+A")
    page.keyboard.type(text)


def measure(page, cap, base, dialogs):
    common.settle(page, 100)
    read = page.evaluate(READ_JS)
    sig = page.evaluate(SIGNATURE_JS)
    proto = page.evaluate(PROTO_JS)
    unsafe = page.evaluate(UNSAFE_JS)
    page.get_by_role("button", name="Copy summary").click()
    common.settle(page, 60)
    lines = page.evaluate("() => window.testClipboardText").split("\n")
    saved = page.evaluate("() => localStorage.getItem('split.draft')")
    return {
        "read": read, "signature": sig, "proto": proto, "unsafe_nodes": unsafe, "pwned": page.evaluate("window.pwned"),
        "csp": page.evaluate("window.csp"), "dialogs": len(dialogs), "clip_lines": len(lines),
        "clip_first_row": lines[2] if len(lines) > 2 else None,
        "saved_names": json.loads(saved)["bill"]["people"][0]["name"] if saved else None, "problems": cap.problems(base),
    }


def run_pair(browser, base, person, item, how):
    ctx, page, cap = common.open_page(browser, base, seed=seeds.S1 if how == "typed" else seed_with(person, item), viewport=(390, 844))
    dialogs = []
    page.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))
    try:
        if how == "typed":
            type_into(page, page.get_by_label("Person 1 name"), person)
            type_into(page, page.get_by_label("Item 1 name"), item)
        return measure(page, cap, base, dialogs)
    finally:
        ctx.close()


def benign_signature(browser, base, person, item):
    ctx, page, cap = common.open_page(browser, base, seed=seed_with("A" * len(person), "B" * len(item)), viewport=(390, 844))
    try:
        common.settle(page, 100)
        page.get_by_role("button", name="Copy summary").click()
        common.settle(page, 60)
        return page.evaluate(SIGNATURE_JS)
    finally:
        ctx.close()


def literal_checks(read, person, item):
    return {
        "personField": read["personField"] == person, "removeLabel": read["removeLabel"] == f"Remove {person}",
        "itemField": read["itemField"] == item, "itemRemove": read["itemRemove"] == f"Remove {item}",
        "whoLabel": read["whoLabel"] == f"Who had {item}", "toggle": read["toggle"] == person,
        "sharesFirstRow": read["sharesFirstRow"] == person,
    }


def money_markup(browser, base, results):
    markup = "<img src=x onerror=f()>"
    ctx, page, cap = common.open_page(browser, base, seed=seeds.S1, viewport=(390, 844))
    try:
        common.settle(page)
        out = {}
        for label, text in (("price-markup", markup), ("price-plain", "abc")):
            price = page.get_by_label("Item 1 price in RM")
            type_into(page, price, text)
            page.keyboard.press("Tab")
            common.settle(page, 80)
            out[label] = {"signature": page.evaluate(SIGNATURE_JS), "errors": page.evaluate(ERRORS_JS), "value": price.input_value()}
        for field in ("Service charge in percent", "SST in percent"):
            type_into(page, page.get_by_label(field), markup)
            page.keyboard.press("Tab")
            common.settle(page, 80)
        page.locator("label[for=mode-even]").click()
        type_into(page, page.locator("#subtotal"), markup)
        page.keyboard.press("Tab")
        common.settle(page, 80)
        errors = page.evaluate(ERRORS_JS)
        out["all_errors_after_all_four_fields"] = errors
        out["only_fixed_error_texts"] = set(errors) <= FIXED_ERRORS and len(errors) >= 4
        out["unsafe_nodes_in_body"] = page.evaluate(UNSAFE_JS)
        out["pwned"] = page.evaluate("window.pwned")
        out["csp"] = page.evaluate("window.csp")
        out["problems"] = cap.problems(base)
        out["same_signature_markup_vs_plain_price"] = out["price-markup"]["signature"] == out["price-plain"]["signature"]
        ok = out["only_fixed_error_texts"] and out["unsafe_nodes_in_body"] == 0 and out["pwned"] == 0 and not out["csp"] and not out["problems"]
        results["cases"].append({"case": "money fields with markup (price, service, SST, subtotal)", "ok": ok, **out})
        print(f"{'PASS' if ok else 'FAIL'} money fields with markup: errors {sorted(set(errors))} unsafe nodes {out['unsafe_nodes_in_body']} "
              f"pwned {out['pwned']} csp {out['csp']} same signature as plain text {out['same_signature_markup_vs_plain_price']}")
    finally:
        ctx.close()


def body(browser, server, results):
    base = server.base
    for person, item in PAIRS:
        expected_sig = benign_signature(browser, base, person, item)
        for how in ("typed", "restored"):
            got = run_pair(browser, base, person, item, how)
            checks = literal_checks(got["read"], person.strip(), item.strip())
            ok = (got["signature"] == expected_sig and got["pwned"] == 0 and not got["csp"] and got["dialogs"] == 0
                  and all(checks.values()) and got["clip_lines"] == 6 and got["unsafe_nodes"] == 0
                  and got["proto"]["stray"] == 0 and got["proto"]["objectKeys"] == STANDARD_OBJECT_KEYS and got["proto"]["arrayExtra"] == ""
                  and not got["problems"] and got["saved_names"] in (None, person))
            row = {"case": f"{how}: person={person!r} item={item!r}", "ok": ok, "signature_equals_benign": got["signature"] == expected_sig,
                   "checks": checks, **{k: got[k] for k in ("pwned", "csp", "dialogs", "clip_lines", "clip_first_row", "proto", "saved_names", "problems", "unsafe_nodes")}}
            results["cases"].append(row)
            print(f"{'PASS' if ok else 'FAIL'} {how:8} person={person!r:24} item={item!r:46} sig==benign {row['signature_equals_benign']} "
                  f"clip lines {got['clip_lines']} first row {got['clip_first_row']!r}")
    money_markup(browser, base, results)


if __name__ == "__main__":
    common.run_probe("p1-injection", body)
