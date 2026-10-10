"""Whole-page comparison: the golden's DOM against the running app's DOM, element by element.

For each of the five screens at each viewport it compares every rendered element (display other than none): tag, id,
class list, every attribute, own text, input value/checked/disabled, the rectangle, EVERY computed style property
(all ~400 that Chromium lists), and the computed style of ::before and ::after where they generate content.
Differences are listed and classified against the "Allowed differences" of spec.md. Nothing is hidden.

usage: python dom_diff.py [--sizes five|edges|all]
"""
import sys

sys.dont_write_bytecode = True
import difflib
import json
from collections import defaultdict

from playwright.sync_api import sync_playwright

import common as C

ALLOWED_ATTR = []


def attr_diffs(g, a):
    """Differences in attributes, minus the ones spec.md allows (value attribute, placeholder, checked attribute)."""
    out, allowed = [], []
    for name in sorted(set(g["attrs"]) | set(a["attrs"])):
        gv, av = g["attrs"].get(name), a["attrs"].get(name)
        if gv == av:
            continue
        rec = {"attr": name, "golden": gv, "app": av}
        if g["tag"] == "input" and name == "value" and g["attrs"].get("type", "text") == "text":
            allowed.append(dict(rec, rule="allowed 1: value is a property in the app, compared as .value below"))
        elif g["tag"] == "input" and name == "checked":
            allowed.append(dict(rec, rule="allowed 1: checked is a property in the app, compared as .checked below"))
        elif g["tag"] == "input" and name == "placeholder" and gv is None:
            allowed.append(dict(rec, rule="allowed 2: placeholder on name inputs (ruling 4)"))
        elif name == "inert" and "app" in g["cls"].split() and av is None:
            allowed.append(dict(rec, rule="allowed 4: the golden's inert stand-in, the app is made inert by showModal()"))
        else:
            out.append(rec)
    return out, allowed


def compare(gw, aw):
    gsig = [C.sig(x) for x in gw]
    asig = [C.sig(x) for x in aw]
    sm = difflib.SequenceMatcher(a=gsig, b=asig, autojunk=False)
    pairs, structural = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            pairs += [(gw[i], aw[j]) for i, j in zip(range(i1, i2), range(j1, j2))]
        else:
            for i in range(i1, i2):
                structural.append({"side": "golden only", "sig": gsig[i], "text": gw[i]["text"]})
            for j in range(j1, j2):
                structural.append({"side": "app only", "sig": asig[j], "text": aw[j]["text"]})
    res = {"golden_elements": len(gw), "app_elements": len(aw), "paired": len(pairs), "structural": structural,
           "attr_diffs": [], "attr_allowed": [], "text_diffs": [], "value_diffs": [], "rect_diffs": [], "style_diffs": [],
           "pseudo_diffs": [], "style_props_compared": 0}
    for g, a in pairs:
        where = C.sig(g)
        ad, al = attr_diffs(g, a)
        res["attr_diffs"] += [dict(d, el=where) for d in ad]
        res["attr_allowed"] += [dict(d, el=where) for d in al]
        if g["text"] != a["text"]:
            res["text_diffs"].append({"el": where, "golden": g["text"], "app": a["text"]})
        for k in ("value", "checked", "disabled"):
            if g.get(k) != a.get(k):
                res["value_diffs"].append({"el": where, "prop": k, "golden": g.get(k), "app": a.get(k)})
        if not C.rect_equal(g["rect"], a["rect"]):
            res["rect_diffs"].append({"el": where, "golden": [round(v, 2) for v in g["rect"]], "app": [round(v, 2) for v in a["rect"]]})
        res["style_props_compared"] += len(g["cs"])
        sd = C.style_diff(g["cs"], a["cs"])
        if sd:
            res["style_diffs"].append({"el": where, "n": len(sd), "props": sd})
        for pe in ("::before", "::after"):
            if (pe in g) != (pe in a):
                res["pseudo_diffs"].append({"el": where, "pseudo": pe, "golden_has": pe in g, "app_has": pe in a})
            elif pe in g:
                psd = C.style_diff(g[pe], a[pe])
                if psd:
                    res["pseudo_diffs"].append({"el": where, "pseudo": pe, "props": psd})
    return res


def main():
    which = "all"
    if "--sizes" in sys.argv:
        which = sys.argv[sys.argv.index("--sizes") + 1]
    sizes = {"five": C.FIVE, "edges": C.EDGES, "all": C.FIVE + C.EDGES}[which]
    server = rig.StaticServer(C.ROOT, say=print) if False else C.rig.StaticServer(C.ROOT, say=print)
    results = {}
    errors = []
    try:
        server.start()
        with sync_playwright() as pw:
            browser = C.launch(pw)
            for screen, (golden, seed) in C.SCREENS.items():
                for size in sizes:
                    gctx = C.gold_ctx(browser, size)
                    actx = C.app_ctx(browser, server.base, size, seed=seed)
                    g = C.open_golden(gctx, golden)
                    a = C.open_app(actx, server.base)
                    if screen == "new-bill-dialog":
                        C.new_bill_by_mouse(a)
                    gw, aw = g.walk(), a.walk()
                    key = f"{screen}@{size[0]}x{size[1]}"
                    results[key] = compare(gw, aw)
                    errors += [(key, m) for m in a.console]
                    r = results[key]
                    print(f"{key:30} elements {r['golden_elements']}/{r['app_elements']} paired {r['paired']} structural {len(r['structural'])} attr {len(r['attr_diffs'])}(+{len(r['attr_allowed'])} allowed) text {len(r['text_diffs'])} value {len(r['value_diffs'])} rect {len(r['rect_diffs'])} style-elements {len(r['style_diffs'])} pseudo {len(r['pseudo_diffs'])}")
                    gctx.close()
                    actx.close()
            browser.close()
    finally:
        server.stop()
    C.dump(f"dom_diff_{which}.json", {"results": results, "app_console_errors": errors})
    print("console errors on the app side:", errors)


if __name__ == "__main__":
    main()
