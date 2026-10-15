"""B1b. The second form of B1 (b1_hostile_boot.py is kept with its first results as the run's history).

Two changes from B1. The draft is written as UTF-8 JSON text (ensure_ascii False), so a combining mark costs one
character and not six, and the long-name cases fit the storage quota. The keystroke goes into the service charge field
(#svc), because a name field holding more than its maxlength refuses a typed character, which made B1 wait for a save
that could not come (a probe artifact, not an app hang).

Rerun 2026-10-16 (v1.1.0 regression --full), copied from qa/security/20261015-222146/ with three changes. Run from this
folder (cd here, python -B b1b_hostile_boot.py --engine chromium|webkit), which writes b1b_hostile_boot-<engine>.json here.
(1) Seven H-10 rows at the end (D8 as changed by R62, names rebuilt with plainName and counted after the removal).
(2) PAGE_STATE also reads every person and item name field. (3) A row passes only if no name field, before and after the
keystroke, and no saved name after the keystroke holds a character of core R35's class.
"""
import argparse
import json
import time

from common import Probe, say

C = chr
ACUTE = C(0x301)
P3 = [{"id": "p1", "name": "Aisyah"}, {"id": "p2", "name": "Ben"}, {"id": "p3", "name": "Chen"}]


def s2(**patch):
    bill = {"mode": "even", "people": [dict(p) for p in P3], "subtotalText": "100.00", "items": [], "serviceText": "10",
            "sstText": "6", "spare": {"rule": "top"}, "nextId": 4}
    bill.update(patch)
    return bill


def env(bill, version=2):
    return json.dumps({"version": version, "bill": bill}, separators=(",", ":"), ensure_ascii=False)


def name_bill(name):
    return env(s2(people=[{"id": "p1", "name": name}, {"id": "p2", "name": "Ben"}, {"id": "p3", "name": "Chen"}]))


CASES = [
    ("readable S2 random", env(s2(spare={"rule": "random", "order": ["p2", "p3", "p1"]})), "ok"),
    ("readable spare top with own __proto__ and extra", env(s2()).replace('{"rule":"top"}', '{"rule":"top","x":1,"__proto__":{"polluted":1}}'), "ok"),
    ("readable person with own __proto__ and admin", env(s2()).replace('{"id":"p1","name":"Aisyah"}', '{"id":"p1","name":"Aisyah","__proto__":{"polluted":1},"admin":true}'), "ok"),
    ("readable v1 with hostile spare (D14)", env(s2(spare={"rule": "random", "order": ["zz"]}), 1), "ok"),
    ("readable one p1 on no item, item mode (fallback)", env(s2(mode="item", items=[{"id": "i4", "name": "Teh", "priceText": "13.51", "who": ["p2", "p3"]}], nextId=5, spare={"rule": "one", "personId": "p1"})), "ok"),
    ("spare one __proto__", env(s2(spare={"rule": "one", "personId": "__proto__"})), "unreadable"),
    ("order invents an id", env(s2(spare={"rule": "random", "order": ["p1", "p2", "p9"]})), "unreadable"),
    ("order repeats an id", env(s2(spare={"rule": "random", "order": ["p1", "p1", "p2"]})), "unreadable"),
    ("rule constructor", env(s2(spare={"rule": "constructor"})), "unreadable"),
    ("v2 without spare", env({k: v for k, v in s2().items() if k != "spare"}), "unreadable"),
    ("version 3", env(s2(), 3), "unreadable"),
    ("who __proto__", env(s2(mode="item", items=[{"id": "i4", "name": "x", "priceText": "1", "who": ["__proto__"]}], nextId=5)), "unreadable"),
    ("duplicate person ids", env(s2(people=[{"id": "p1", "name": "A"}, {"id": "p1", "name": "B"}])), "unreadable"),
    ("stale nextId", env(s2(nextId=3)), "unreadable"),
    ("unknown mode", env(s2(mode="split")), "unreadable"),
    ("no people, even mode", env(s2(people=[], nextId=1)), "unreadable"),
    ("name with CR", name_bill("A" + C(13) + "Adds up to RM 0.00"), "unreadable"),
    ("BOM prefix", C(0xFEFF) + env(s2()), "unreadable"),
    ("the text null", "null", "unreadable"),
    ("2M-char subtotalText", env(s2(subtotalText="9" * 2_000_000)), "ok"),
    ("2M-char ascii name", name_bill("x" * 2_000_000), "unreadable"),
    ("20k combining marks, one grapheme name", name_bill("a" + ACUTE * 20_000), "ok"),
    ("200k combining marks, one grapheme name", name_bill("a" + ACUTE * 200_000), "ok"),
    ("1M combining marks, one grapheme name", name_bill("a" + ACUTE * 1_000_000), "ok"),
    ("2M combining marks, one grapheme name", name_bill("a" + ACUTE * 2_000_000), "ok"),
    ("1M nesting in an unknown key", env(s2(junk=0)).replace('"junk":0', '"junk":' + "[" * 1_000_000 + "]" * 1_000_000), "any"),
    ("4.5M-char subtotalText", env(s2(subtotalText="9" * 4_500_000)), "ok"),
    ("4.5M combining marks, one grapheme name", name_bill("a" + ACUTE * 4_500_000), "ok"),
    ("H-10 markup name ending in RLO loads plain", name_bill("<svg onload=f()>" + C(0x202E)), "ok"),
    ("H-10 20 letters and 1000 RLO (counted after removal)", name_bill("x" * 20 + C(0x202E) * 1000), "ok"),
    ("H-10 21 letters and one RLO", name_bill("x" * 21 + C(0x202E)), "unreadable"),
    ("H-10 RLO then LF (LF rejects first)", name_bill(C(0x202E) + C(10)), "unreadable"),
    ("H-10 item name VT FF NEL LS PS loads plain", env(s2(mode="item", items=[{"id": "i4", "name": "T" + C(11) + C(12) + C(0x85) + C(0x2028) + C(0x2029) + "eh", "priceText": "1", "who": ["p1"]}], nextId=5)), "ok"),
    ("H-10 2M NUL name (all removed, empty)", name_bill(C(0) * 2_000_000), "ok"),
    ("H-10 4.5M RLO name (all removed, empty)", name_bill(C(0x202E) * 4_500_000), "ok"),
]
NAME_CLASS = frozenset([*range(0x00, 0x20), *range(0x7F, 0xA0), 0x2028, 0x2029, 0x061C, 0x200E, 0x200F,
                        *range(0x202A, 0x202F), *range(0x2066, 0x206A)])


def class_in(texts):
    return any(ord(c) in NAME_CLASS for t in texts for c in (t or ""))


def saved_names(text):
    try:
        bill = json.loads(text)["bill"]
        return [p["name"] for p in bill["people"]] + [i["name"] for i in bill["items"]]
    except Exception:  # noqa: BLE001
        return []

PAGE_STATE = """() => {
  const notes = [...document.querySelectorAll('#notes .note')];
  return {
    unreadableNote: notes.some((n) => !n.classList.contains('is-warn')),
    saveWarning: notes.some((n) => n.classList.contains('is-warn')),
    people: document.querySelectorAll('#peopleList > li').length,
    proto: Object.getOwnPropertyNames(Object.prototype).length,
    polluted: ({}).polluted ?? null, admin: ({}).admin ?? null,
    chip: document.querySelector('#spareBtn') ? document.querySelector('#spareBtn').textContent : null,
    names: [...document.querySelectorAll('#peopleList input, #itemList li.item input:not([inputmode])')].map((i) => i.value),
  };
}"""


def keys_of(text):
    try:
        draft = json.loads(text)
    except Exception as error:  # noqa: BLE001
        return f"not JSON: {type(error).__name__}"
    bill = draft.get("bill", {})
    return {"top": sorted(draft), "bill": list(bill), "people": [sorted(p) for p in bill.get("people", [])],
            "items": [sorted(i) for i in bill.get("items", [])], "spare": bill.get("spare"), "version": draft.get("version"),
            "name_lengths": [len(p.get("name", "")) for p in bill.get("people", [])]}


def run(engine):
    with Probe("b1b_hostile_boot", engine) as probe:
        for name, text, want in CASES:
            row = {"case": name, "chars": len(text), "want": want}
            ctx = probe.context(viewport={"width": 1280, "height": 800})
            try:
                page, rec = probe.page(ctx)
                seeded = probe.seed(page, rec, text)
                row["seeded"] = seeded
                if seeded is not True:
                    row["note"] = "storage refused the seed, case not run"
                    row["pass"] = None
                else:
                    proto_fresh = page.evaluate("() => Object.getOwnPropertyNames(Object.prototype).length")
                    try:
                        row["ready_ms"] = probe.open_app(page, timeout_ms=60000)
                    except Exception as error:  # noqa: BLE001
                        row["ready_ms"] = None
                        row["ready_error"] = f"{type(error).__name__}: {str(error)[:200]}"
                    probe.stand_in(page)
                    state = page.evaluate(PAGE_STATE)
                    row.update({k: v for k, v in state.items() if k != "names"})
                    row["name_lengths_on_screen"] = [len(n) for n in state["names"]]
                    row["class_in_names_at_boot"] = class_in(state["names"])
                    row["proto_changed"] = state["proto"] != proto_fresh
                    after = probe.stored(page)
                    row["stored_unchanged_at_boot"] = after == text
                    row["stored_after_boot"] = keys_of(after) if after != text else "same as seeded"
                    row["got"] = "unreadable" if state["unreadableNote"] else ("ok" if row["ready_ms"] is not None else "no render")
                    # One real keystroke at the end of the service charge field, then what is stored.
                    t0 = time.perf_counter()
                    page.locator("#svc").click()
                    page.keyboard.press("End")
                    page.keyboard.type("x")
                    page.wait_for_function("(t) => localStorage.getItem('split.draft') !== t", arg=after, timeout=60000)
                    row["keystroke_ms"] = round((time.perf_counter() - t0) * 1000)
                    stored_now = probe.stored(page)
                    row["stored_after_keystroke"] = keys_of(stored_now)
                    row["class_in_saved_names_after_keystroke"] = class_in(saved_names(stored_now))
                    t0 = time.perf_counter()
                    page.evaluate("() => 1 + 1")
                    row["idle_eval_ms"] = round((time.perf_counter() - t0) * 1000)
                    row["csp"] = probe.violations(page)
                    row.update(console=rec["console"], page_errors=rec["page_errors"], dialogs=rec["dialogs"],
                               off_rule_requests=probe.off_rule_requests(rec))
                    row["pass"] = ((want == "any" or row["got"] == want) and not row["proto_changed"] and state["polluted"] is None
                                   and state["admin"] is None and not rec["console"] and not rec["page_errors"] and not row["csp"]
                                   and not row["off_rule_requests"] and not row["class_in_names_at_boot"]
                                   and not row["class_in_saved_names_after_keystroke"])
            except Exception as error:  # noqa: BLE001
                row["error"] = f"{type(error).__name__}: {str(error)[:300]}"
                row["pass"] = False
            finally:
                ctx.close()
            probe.rows.append(row)
            say(f"{'ok  ' if row.get('pass') else ('SKIP' if row.get('pass') is None else 'FAIL')} {name}: got {row.get('got')} "
                f"ready {row.get('ready_ms')} ms keystroke {row.get('keystroke_ms')} ms {row.get('note', '')}{row.get('error', '')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", choices=["chromium", "webkit"], default="chromium")
    run(parser.parse_args().engine)
