"""Threat row 2 (R27, D1 to D12): hostile `split.draft` values in localStorage.

Each case boots the app cold, writes the hostile text under `split.draft` from the page, reloads, and records:
  - what the app did: the S7 note, the people and items it shows, the mode, the draft it saved at boot,
  - console errors, page errors, CSP violations, requests,
  - prototype pollution (Object.prototype and Array.prototype names, stray properties on {}),
  - how long the first render took,
  - after one real keystroke in Person 1 name: the saved draft keeps only the known keys (D11, D12).
Expectation per case is stated in the table: "ok" (loads as that bill), "note" (unreadable, S7 note, new bill saved).
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import seeds  # noqa: E402

S2 = json.loads(seeds.S2)
S1 = json.loads(seeds.S1)
STANDARD_OBJECT_KEYS = ("__defineGetter__,__defineSetter__,__lookupGetter__,__lookupSetter__,__proto__,constructor,"
                        "hasOwnProperty,isPrototypeOf,propertyIsEnumerable,toLocaleString,toString,valueOf")
KNOWN = {"": {"version", "bill"}, "bill": {"mode", "people", "subtotalText", "items", "serviceText", "sstText", "nextId"},
         "person": {"id", "name"}, "item": {"id", "name", "priceText", "who"}}


def dump(value):
    return json.dumps(value, separators=(",", ":"), ensure_ascii=True)


def mutated(base, edit):
    draft = json.loads(json.dumps(base))
    edit(draft)
    return dump(draft)


def raw_proto(prefix_json, extra):
    """JSON text with a literal __proto__ member (json.dumps would also write it, but this keeps the order explicit)."""
    return prefix_json[:-1] + "," + extra + "}"


DEEP = 200_000
CASES = [  # (id, text, expectation, note)
    ("H01 empty string", "", "note", "getItem returns '' (not null)"),
    ("H02 whitespace", "   ", "note", ""),
    ("H03 truncated JSON", "{", "note", ""),
    ("H04 null", "null", "note", ""),
    ("H05 array", "[]", "note", ""),
    ("H06 number", "1", "note", ""),
    ("H07 string", '"x"', "note", ""),
    ("H08 true", "true", "note", ""),
    ("H09 empty object", "{}", "note", ""),
    ("H10 BOM before valid JSON", "﻿" + seeds.S2, "note", "JSON.parse refuses a BOM"),
    ("H11 valid JSON then garbage", seeds.S2 + "x", "note", ""),
    ("H12 __proto__ at the top, valid bill", raw_proto(seeds.S2, '"__proto__":{"polluted":1}'), "ok", "D11: unknown key ignored"),
    ("H13 __proto__ and constructor inside bill", raw_proto(seeds.S2[:-1], '"__proto__":{"polluted":1},"constructor":{"prototype":{"polluted":1}}') + "}", "ok", ""),
    ("H14 __proto__ and constructor inside a person",
     seeds.S2.replace('"name":"Aisyah"', '"name":"Aisyah","__proto__":{"polluted":1},"constructor":{"prototype":{"polluted":1}}'), "ok", ""),
    ("H15 who holds __proto__", mutated(S1, lambda d: d["bill"]["items"][0].update(who=["__proto__"])), "note", ""),
    ("H16 who holds constructor", mutated(S1, lambda d: d["bill"]["items"][0].update(who=["constructor"])), "note", ""),
    ("H17 who holds toString", mutated(S1, lambda d: d["bill"]["items"][0].update(who=["toString"])), "note", ""),
    ("H18 who holds a stale id p9", mutated(S1, lambda d: d["bill"]["items"][0].update(who=["p9"])), "note", ""),
    ("H19 person id __proto__", mutated(S2, lambda d: d["bill"]["people"][0].update(id="__proto__")), "note", ""),
    ("H20 people as an object with length", mutated(S2, lambda d: d["bill"].update(people={"length": 2, "0": d["bill"]["people"][0], "1": d["bill"]["people"][1]})), "note", ""),
    ("H21 version 1.0 and 1e0 (same number)", seeds.S2.replace('"version":1', '"version":1.0'), "ok", "JSON.parse('1.0') is 1"),
    ("H22 version string", mutated(S2, lambda d: d.update(version="1")), "note", ""),
    ("H23 mode toString", mutated(S2, lambda d: d["bill"].update(mode="toString")), "note", ""),
    ("H24 mode array", mutated(S2, lambda d: d["bill"].update(mode=["even"])), "note", ""),
    ("H25 nextId string", mutated(S2, lambda d: d["bill"].update(nextId="4")), "note", ""),
    ("H26 nextId 1e300", seeds.S2.replace('"nextId":4', '"nextId":1e300'), "note", ""),
    ("H27 nextId 1000000000 (the maximum)", mutated(S2, lambda d: d["bill"].update(nextId=1_000_000_000)), "ok", ""),
    ("H28 nextId 1000000001", mutated(S2, lambda d: d["bill"].update(nextId=1_000_000_001)), "note", ""),
    ("H29 name null", mutated(S2, lambda d: d["bill"]["people"][0].update(name=None)), "note", ""),
    ("H30 name array", mutated(S2, lambda d: d["bill"]["people"][0].update(name=["a"])), "note", ""),
    ("H31 name with U+2028 (accepted residual)", mutated(S2, lambda d: d["bill"]["people"][0].update(name="A B")), "ok", ""),
    ("H32 name with a lone surrogate", seeds.S2.replace('"name":"Aisyah"', '"name":"\\ud800"'), "ok", ""),
    ("H33 name with CR", mutated(S2, lambda d: d["bill"]["people"][0].update(name="A\rB")), "note", ""),
    ("H34 unknown keys at every level", mutated(S1, lambda d: (d.update(extra=1), d["bill"].update(extra=2), d["bill"]["people"][0].update(extra=3), d["bill"]["items"][0].update(extra=4))), "ok", "D11"),
    ("H35 ids with leading zeros p01 and p1", mutated(S2, lambda d: d["bill"].update(people=[{"id": "p01", "name": "A"}, {"id": "p1", "name": "B"}], nextId=4)), "ok", "distinct strings, both accepted"),
    ("H36 priceText with a line feed", mutated(S1, lambda d: d["bill"]["items"][0].update(priceText="1\n2")), "ok", "D9 checks only the type"),
    ("H37 subtotalText holding markup", mutated(S2, lambda d: d["bill"].update(subtotalText="<img src=x onerror=f()>")), "ok", "shows the amount error"),
    ("H38 nesting 200000 deep in an unknown key", seeds.S2[:-1] + ',"x":' + "[" * DEEP + "]" * DEEP + "}", "any", "JSON.parse may throw RangeError, which is caught"),
    ("H39 4.5 MB subtotalText", mutated(S2, lambda d: d["bill"].update(subtotalText="9" * 4_500_000)), "ok", "self-DoS size"),
    ("H40 3 MB person name", mutated(S2, lambda d: d["bill"]["people"][0].update(name="a" * 3_000_000)), "note", "D8"),
    ("H41 50 items, each tapped by 3", mutated(S1, lambda d: d["bill"].update(
        items=[{"id": f"i{n}", "name": f"Dish {n}", "priceText": "12.00", "who": ["p1", "p2", "p3"]} for n in range(4, 54)], nextId=54)), "ok", "the maximum"),
    ("H42 51 items", mutated(S1, lambda d: d["bill"].update(
        items=[{"id": f"i{n}", "name": f"Dish {n}", "priceText": "12.00", "who": ["p1"]} for n in range(4, 55)], nextId=55)), "note", ""),
]

PROTO_JS = """() => ({
  objectKeys: Object.getOwnPropertyNames(Object.prototype).sort().join(','),
  arrayExtra: Object.keys(Array.prototype).join(','),
  stray: ['polluted', 'extra'].filter((k) => ({})[k] !== undefined || [][k] !== undefined).length,
})"""
STATE_JS = """() => ({
  note: !!document.querySelector('.note'),
  mode: (document.querySelector('input[name=mode]:checked') || {}).value || null,
  people: [...document.querySelectorAll('li.person input')].map((i) => i.value.slice(0, 40)),
  items: document.querySelectorAll('li.item').length,
  subtotalLen: (document.querySelector('#subtotal') || { value: '' }).value.length,
  errors: [...document.querySelectorAll('p.error')].map((p) => p.textContent),
})"""


def keys_ok(saved_text):
    saved = json.loads(saved_text)
    problems = []
    if set(saved) != KNOWN[""]:
        problems.append(f"top keys {sorted(saved)}")
    bill = saved["bill"]
    if set(bill) != KNOWN["bill"]:
        problems.append(f"bill keys {sorted(bill)}")
    for person in bill["people"]:
        if set(person) != KNOWN["person"]:
            problems.append(f"person keys {sorted(person)}")
    for item in bill["items"]:
        if set(item) != KNOWN["item"]:
            problems.append(f"item keys {sorted(item)}")
    return problems


def run_case(browser, base, text):
    ctx, page, cap = common.open_page(browser, base, viewport=(390, 844))
    try:
        page.evaluate("(t) => localStorage.setItem('split.draft', t)", text)
        started = time.perf_counter()
        page.reload()
        page.wait_for_selector("li.person")
        boot_ms = round((time.perf_counter() - started) * 1000)
        state = page.evaluate(STATE_JS)
        proto = page.evaluate(PROTO_JS)
        saved_at_boot = page.evaluate("() => localStorage.getItem('split.draft')")
        unchanged_at_boot = saved_at_boot == text
        key_problems = []
        key_ms = None
        if state["people"]:
            field = page.get_by_label("Person 1 name")
            field.click()
            key_started = time.perf_counter()
            page.keyboard.type("Z")
            common.settle(page, 20)
            key_ms = round((time.perf_counter() - key_started) * 1000)
            key_problems = keys_ok(page.evaluate("() => localStorage.getItem('split.draft')"))
        return {
            "state": state, "proto_ok": proto["objectKeys"] == STANDARD_OBJECT_KEYS and proto["arrayExtra"] == "" and proto["stray"] == 0,
            "boot_ms": boot_ms, "key_ms": key_ms, "draft_untouched_at_boot": unchanged_at_boot, "key_problems_after_edit": key_problems,
            "problems": cap.problems(base), "pwned": page.evaluate("window.pwned"), "csp": page.evaluate("window.csp"),
        }
    finally:
        ctx.close()


def body(browser, server, results):
    for case_id, text, expect, note in CASES:
        got = run_case(browser, server.base, text)
        noted = got["state"]["note"]
        verdict_expect = {"ok": not noted, "note": noted, "any": True}[expect]
        # a note means a new bill was saved at boot; a loaded draft is left as it was until the first change
        shape_ok = (got["state"]["people"] == ["Person 1", "Person 2"]) if noted else True
        clean = got["proto_ok"] and not got["problems"] and got["pwned"] == 0 and not got["csp"] and not got["key_problems_after_edit"]
        ok = verdict_expect and shape_ok and clean and (got["draft_untouched_at_boot"] if expect == "ok" else True)
        row = {"case": case_id, "expect": expect, "ok": ok, "note_shown": noted, "note": note, **got}
        results["cases"].append(row)
        print(f"{'PASS' if ok else 'FAIL'} {case_id:46} expect {expect:5} note shown {noted!s:5} people {len(got['state']['people'])} items {got['state']['items']} "
              f"boot {got['boot_ms']:5} ms key {got['key_ms']} ms proto ok {got['proto_ok']} problems {got['problems']} keys {got['key_problems_after_edit']}")


if __name__ == "__main__":
    common.run_probe("p3-hostile-draft", body)
