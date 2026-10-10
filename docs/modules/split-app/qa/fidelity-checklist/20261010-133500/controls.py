"""Negative controls: proof that the checks in this folder can fail.

Each mutant changes ONE thing in the running app's page (in my own browser context, through the page's CSSOM or DOM, never in a
file of the product) and is then judged three ways:
  1. the S1 checklist rows (rows_screens.screen_s1) at 390 x 844: which row ids flip to FAIL,
  2. the whole-page comparison (dom_diff.compare): how many elements differ,
  3. the pixel gate's own rule (threshold 0.01) and the any-level count, on full-page screenshots of the golden and the mutant.
A check that stays green under a mutant it should catch would be a blind spot in the evidence.

The golden screenshot is taken on a second golden page, because Playwright's screenshot leaves an empty style attribute on the inputs
of the page it photographs, and the rows and the walk must see the golden untouched.

usage: python controls.py
"""
import sys

sys.dont_write_bytecode = True
import io

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

import common as C
from dom_diff import compare
from rows_lib import Ctx, Rows
from rows_screens import screen_s1

MUTANTS = [
    ("wordmark letter-spacing 0", "document.querySelector('h1.wordmark').style.letterSpacing = '0px'", {"S1-01"}),
    ("header button border colour (1 level)", "document.querySelector('header .btn').style.borderColor = '#78807D'", {"S1-02"}),
    ("person 1 remove icon colour (1 level)", "document.querySelector('li.field.person .icon-btn svg').style.fill = '#4A524F'", {"S1-05"}),
    ("Ben toggle on item 1 flipped to pressed", "document.querySelector('li.item .who .tap:nth-child(2)').setAttribute('aria-pressed', 'true')", {"S1-19"}),
    ("Total double rule made single", "document.querySelector('.final').style.borderBottomStyle = 'solid'", {"S1-45"}),
    ("check row copy 'Adds up to' -> 'Adds up'", "const th = document.querySelector('table.shares tfoot th'); th.lastChild.textContent = 'Adds up'", {"S1-51"}),
    ("hint 14px -> 13px", "document.querySelector('#charges-hint').style.fontSize = '13px'", {"S1-39"}),
    ("Copy summary min-height 48 -> 47", "document.querySelector('button.copy').style.minHeight = '47px'", {"S1-52"}),
    ("item 2 separator colour (1 level)", "document.querySelector('li.item:nth-child(2)').style.borderTopColor = '#C9CECC'", {"S1-32"}),
    ("--ink one level lighter (#141917 -> #151917)", "document.documentElement.style.setProperty('--ink', '#151917')", None),
    ("--line-strong one level (#78807C -> #78807D)", "document.documentElement.style.setProperty('--line-strong', '#78807D')", None),
    ("panel padding-top 20 -> 19", "document.querySelector('div.tape').style.paddingTop = '19px'", None),
    ("Add person button text -> Add people", "const b = document.querySelector('ul.cells > li:last-child .btn'); b.lastChild.textContent = 'Add people'", {"S1-10"}),
]


def shot(page):
    return np.asarray(Image.open(io.BytesIO(page.screenshot(full_page=True, animations="disabled"))).convert("RGB"), dtype=np.int32)


def pixel_counts(g, c):
    if g.shape != c.shape:
        return {"size_differs": [list(g.shape[:2]), list(c.shape[:2])], "above_0.01": "dimensions differ", "any_level": "dimensions differ"}
    dist = np.sqrt(((g - c) ** 2).sum(axis=2)) / 441.6729559300637
    return {"size_differs": None, "above_0.01": int((dist > 0.01).sum()), "any_level": int((np.abs(g - c).max(axis=2) > 0).sum())}


def main():
    server = C.rig.StaticServer(C.ROOT, say=print)
    results = []
    try:
        server.start()
        with sync_playwright() as pw:
            browser = C.launch(pw)
            vp = (390, 844)
            golden, seed = C.SCREENS["bill-items"]
            gctx = C.gold_ctx(browser, vp)
            g = C.open_golden(gctx, golden)
            gctx2 = C.gold_ctx(browser, vp)
            g_img = shot(C.open_golden(gctx2, golden).page)
            g_walk = g.walk()
            for label, js, expect in [("(no mutation, control)", "0", set())] + MUTANTS:
                actx = C.app_ctx(browser, server.base, vp, seed=seed)
                a = C.open_app(actx, server.base)
                a.page.evaluate("() => { " + js + " }")
                a.page.wait_for_timeout(120)
                R = Rows()
                screen_s1(Ctx(R, a, g, 390, "bill-items"))
                failing = sorted(rid for rid, by in R.d.items() if any(not ok for v in by.values() for ok, _ in v))
                r = compare(g_walk, a.walk())
                px = pixel_counts(g_img, shot(a.page))
                res = {"mutant": label, "rows_failing": failing, "rows_failing_count": len(failing),
                       "expected_rows_among_failing": (expect is None) or expect.issubset(set(failing)),
                       "dom_style_diff_elements": len(r["style_diffs"]), "dom_rect_diff_elements": len(r["rect_diffs"]), "dom_text_diffs": len(r["text_diffs"]),
                       "dom_attr_diffs": len(r["attr_diffs"]), "pixels": px}
                results.append(res)
                print(f"{label:46} rows failing {len(failing):3} {failing[:5]}  dom style {len(r['style_diffs']):3} rect {len(r['rect_diffs']):3} text {len(r['text_diffs'])} attr {len(r['attr_diffs'])}  pixels>0.01 {px['above_0.01']}  any-level {px['any_level']}")
                actx.close()
            gctx.close()
            gctx2.close()
            browser.close()
    finally:
        server.stop()
    C.dump("controls.json", results)
    caught = [r for r in results[1:] if r["rows_failing_count"] or r["dom_style_diff_elements"] or r["dom_rect_diff_elements"] or r["dom_text_diffs"] or r["dom_attr_diffs"]]
    expected_ok = [r for r in results[1:] if r["expected_rows_among_failing"]]
    harness_blind = [r["mutant"] for r in results[1:] if r["pixels"]["above_0.01"] == 0]
    print(f"mutants caught by rows or the whole-page comparison: {len(caught)} of {len(results) - 1}; the row the mutant targets failed in {len(expected_ok)} of {len(results) - 1}")
    print("mutants the harness rule (0.01) does not see:", harness_blind)
    print("unmutated control: rows failing", results[0]["rows_failing_count"], "dom diffs", results[0]["dom_style_diff_elements"], results[0]["dom_attr_diffs"], "pixels", results[0]["pixels"])


if __name__ == "__main__":
    main()
