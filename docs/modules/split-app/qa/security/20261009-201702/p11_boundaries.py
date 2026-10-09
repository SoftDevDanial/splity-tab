"""Round-trip boundaries between what the decoder accepts and what the app then saves, and a two-tab check.

B1 A draft with nextId 1000000000 (the decoder's maximum) is accepted. One Add person makes the app save nextId 1000000001,
   which the decoder rejects (D10). Does the next load show the note and lose the bill?
B2 Two pages of the same origin in one context: page B writes a hostile draft while page A (the app) is open. A has no
   storage listener, so it should not react; A's next save overwrites it. Then B's hostile draft, written before a load,
   goes through the decoder.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import seeds  # noqa: E402


def body(browser, server, results):
    base = server.base
    # B1
    seed = seeds.changed(seeds.S2, lambda d: d["bill"].update(nextId=1_000_000_000))
    ctx, page, cap = common.open_page(browser, base, seed=seed, viewport=(390, 844))
    try:
        common.settle(page)
        loaded = page.evaluate("() => [...document.querySelectorAll('li.person input')].map((i) => i.value)")
        page.get_by_role("button", name="Add person", exact=True).click()
        saved_next = json.loads(page.evaluate("() => localStorage.getItem('split.draft')"))["bill"]["nextId"]
        page.reload()
        common.settle(page)
        after = page.evaluate("() => ({ note: !!document.querySelector('.note'), people: [...document.querySelectorAll('li.person input')].map((i) => i.value) })")
        results["cases"].append({"case": "B1 nextId at the decoder maximum, then Add person, then reload", "loaded_people": loaded,
                                 "saved_nextId": saved_next, "after_reload": after, "problems": cap.problems(base)})
        print("B1 loaded", loaded, "-> after Add person the saved nextId is", saved_next, "-> after reload", after)
    finally:
        ctx.close()
    # B2
    ctx, page_a, cap = common.open_page(browser, base, seed=seeds.S2, viewport=(390, 844))
    try:
        common.settle(page_a)
        page_b = ctx.new_page()
        page_b.goto(base + "/")
        page_b.evaluate("(t) => localStorage.setItem('split.draft', t)", '{"version":1,"bill":{"__proto__":{"x":1}}}')
        common.settle(page_a, 200)
        a_still = page_a.evaluate("() => ({ note: !!document.querySelector('.note'), people: [...document.querySelectorAll('li.person input')].map((i) => i.value) })")
        page_a.get_by_label("Person 1 name").click()
        page_a.keyboard.type("Z")
        common.settle(page_a, 100)
        stored = json.loads(page_b.evaluate("() => localStorage.getItem('split.draft')"))["bill"]["people"][0]["name"]
        page_b.reload()
        common.settle(page_b, 100)
        b_after = page_b.evaluate("() => ({ note: !!document.querySelector('.note'), people: [...document.querySelectorAll('li.person input')].map((i) => i.value) })")
        results["cases"].append({"case": "B2 a second page writes a hostile draft while the app is open", "page_a_unchanged": a_still,
                                 "stored_person1_after_a_types": stored, "page_b_reload": b_after, "problems": cap.problems(base)})
        print("B2 page A after B wrote a hostile draft:", a_still, "| after A types, stored person 1 =", stored, "| B reload:", b_after)
    finally:
        ctx.close()


if __name__ == "__main__":
    common.run_probe("p11-boundaries", body)
