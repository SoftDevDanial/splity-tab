"""Two small checks.

 A. The state scripts the gate uses (tests/browser/fidelity/seed-s1.js, seed-s2.js, seed-s5.js, open-new-bill.js) put the app in the
    state the goldens show: the JSON each seed script stores is compared with the seeds written in qa.md (parsed from the markdown, not
    from seeds.py), and open-new-bill.js is read for what it does besides the click.
 B. The S7 note banner geometry at five widths, the app against the CSS rules and against the specimen's note.

usage: python misc_checks.py
"""
import sys

sys.dont_write_bytecode = True
import json
import re

from playwright.sync_api import sync_playwright

import common as C


def seed_script_checks():
    qa = (C.ROOT / "docs" / "modules" / "split-app" / "qa.md").read_text(encoding="utf-8")
    seeds_qa = {}
    for name in ("S2", "S1"):
        m = re.search(r"^" + name + r"  (\{.*\})\s*$", qa, re.M)
        seeds_qa[name] = json.loads(m.group(1))
    s5 = json.loads(json.dumps(seeds_qa["S1"]))
    s5["bill"]["items"][2]["who"] = []
    seeds_qa["S5"] = s5
    out = {}
    for name, fname in (("S1", "seed-s1.js"), ("S2", "seed-s2.js"), ("S5", "seed-s5.js")):
        js = (C.ROOT / "tests" / "browser" / "fidelity" / fname).read_text(encoding="utf-8")
        m = re.search(r"localStorage\.setItem\(\"split\.draft\", '(.*)'\);?\s*$", js.strip().splitlines()[-1])
        stored = json.loads(m.group(1)) if m else None
        out[fname] = {"one_statement": len([l for l in js.splitlines() if l.strip() and not l.strip().startswith("//")]) == 1,
                      "equals_qa_md_seed": stored == seeds_qa[name], "equals_seeds_py": m is not None and m.group(1) == getattr(C.seeds, name),
                      "sets_only_split_draft": js.count("localStorage.setItem") == 1}
    js = (C.ROOT / "tests" / "browser" / "fidelity" / "open-new-bill.js").read_text(encoding="utf-8")
    code = [l.strip() for l in js.splitlines() if l.strip() and not l.strip().startswith("//")]
    out["open-new-bill.js"] = {"statements": code}
    return out


NOTE_JS = """() => {
  const rect = (e) => { const b = e.getBoundingClientRect(); return [b.x, b.y + scrollY, b.width, b.height]; };
  const note = document.querySelector('.note'), p = note.querySelector('p'), btn = note.querySelector('.icon-btn');
  const hdr = document.querySelector('header.bar') || document.querySelector('.frame .bar');
  const wrap = note.parentElement;
  const range = document.createRange(); range.selectNodeContents(p);
  const lines = new Set(Array.from(range.getClientRects()).map((r) => Math.round(r.top))).size;
  const cs = getComputedStyle(wrap);
  return { note: rect(note), p: rect(p), btn: rect(btn), hdr: rect(hdr), lines, wrapContent: wrap.getBoundingClientRect().width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight) };
}"""


def note_checks(browser, base):
    rows = []
    for vp in ((360, 780), (390, 844), (600, 900), (1024, 768), (1280, 800)):
        actx = C.app_ctx(browser, base, vp, seed=C.seeds.UNREADABLE["B1"])
        a = C.open_app(actx, base)
        m = a.js(NOTE_JS)
        sctx = C.gold_ctx(browser, vp)
        spec = C.open_golden(sctx, "states")
        s = spec.js(NOTE_JS.replace("document.querySelector('.note')", "document.querySelector('section[aria-labelledby=spec-s7] .note')").replace("document.querySelector('header.bar') || document.querySelector('.frame .bar')", "document.querySelector('section[aria-labelledby=spec-s7] .bar')"))
        def geo(x):
            n, p, b, h = x["note"], x["p"], x["btn"], x["hdr"]
            return {"note_width": round(n[2], 2), "note_height": round(n[3], 2), "lines": x["lines"], "gap_under_header": round(n[1] - (h[1] + h[3]), 2),
                    "button_top_offset": round(b[1] - n[1], 2), "button_right_inset": round((n[0] + n[2]) - (b[0] + b[2]), 2), "button": [round(b[2], 2), round(b[3], 2)],
                    "p_height": round(p[3], 2), "p_centre_offset": round((p[1] + p[3] / 2) - (n[1] + n[3] / 2), 2), "content_width_of_wrap": round(x["wrapContent"], 2)}
        ga, gs = geo(m), geo(s)
        ok = (ga["gap_under_header"] == 16 and ga["button_top_offset"] == 1 and ga["button_right_inset"] == 1 and ga["button"] == [44, 44]
              and abs(ga["note_width"] - ga["content_width_of_wrap"]) < 0.01 and abs(ga["p_centre_offset"]) < 0.51 and ga["p_height"] == ga["lines"] * 24 + 16)
        rows.append({"viewport": f"{vp[0]}x{vp[1]}", "app": ga, "specimen": gs, "ok": ok, "lines_equal_to_specimen_when_widths_equal": None})
        actx.close()
        sctx.close()
    return rows


def main():
    out = {"seed_scripts": seed_script_checks()}
    server = C.rig.StaticServer(C.ROOT, say=print)
    try:
        server.start()
        with sync_playwright() as pw:
            browser = C.launch(pw)
            out["note_geometry"] = note_checks(browser, server.base)
            browser.close()
    finally:
        server.stop()
    C.dump("misc_checks.json", out)
    print(json.dumps(out["seed_scripts"], indent=1))
    for r in out["note_geometry"]:
        print(r["viewport"], "ok", r["ok"], r["app"])
        print("      specimen", r["specimen"])


if __name__ == "__main__":
    main()
