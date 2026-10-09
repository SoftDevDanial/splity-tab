"""Shared helpers of the split-app security re-check probes (security finder, read-only on the product).

It imports the audit's own helper (qa/security/20261009-201702/common.py) read only and points its output folder at this
folder, so every browser context still comes from rig.new_context (clipboard recorder on, `permissions` and `bypass_csp`
refused, a second CG-7 guard rejecting readText, read and write). Nothing here touches the operating system clipboard.

Added on top of the audit helper:
- Cap.problems also reads window.csp (every securitypolicyviolation the page saw), so a CSP violation is a problem row.
- gesture() runs one named gesture at a point (single, dbl, triple, tap1, tap2).
- draft(), clicks(), legacy sources served from memory for the control rows.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
AUDIT = HERE.parents[1] / "security" / "20261009-201702"
sys.path.insert(0, str(AUDIT))

import common  # noqa: E402  (the audit's helper, read only)

common.HERE = HERE  # results-*.json land in this folder, not in the audit's

_orig_attach = common.Cap.attach
_orig_problems = common.Cap.problems


def _attach(self, page):
    self._page = page
    return _orig_attach(self, page)


def _problems(self, base):
    found = _orig_problems(self, base)
    try:
        csp = self._page.evaluate("() => window.csp")
    except Exception as exc:  # a closed page
        csp = []
        found.append(f"csp read failed: {exc}")
    found += [f"csp violation: {c}" for c in (csp or [])]
    return found


common.Cap.attach = _attach
common.Cap.problems = _problems

seeds = common.seeds
rig = common.rig
open_page = common.open_page
settle = common.settle
centre = common.centre
snap = common.snap
run_probe = common.run_probe

ROOT = common.ROOT


def draft(page):
    raw = page.evaluate("() => localStorage.getItem('split.draft')")
    return json.loads(raw) if raw else None


def bill(page):
    d = draft(page)
    return d["bill"] if d else None


def btn(page, name):
    return page.get_by_role("button", name=name, exact=True)


def gesture(page, kind, x, y):
    if kind == "single":
        page.mouse.click(x, y)
    elif kind == "dbl":
        page.mouse.dblclick(x, y)
    elif kind == "triple":
        page.mouse.click(x, y, click_count=3)
    elif kind == "tap1":
        page.touchscreen.tap(x, y)
    elif kind == "tap2":
        page.touchscreen.tap(x, y)
        page.touchscreen.tap(x, y)
    else:
        raise ValueError(kind)


def clicks(page, kinds=("click",)):
    """The page's event log as 'type:detail:target:reached|SWALLOWED' strings (see common.PROBE_JS)."""
    return [f"{e['type']}:{e['detail']}:{e['target']}:{'reached' if e['reached'] else 'SWALLOWED'}"
            for e in page.evaluate("() => window.evlog") if e["type"] in kinds]


def reset_log(page):
    page.evaluate("() => { window.evlog = []; }")


def dialog_open(page):
    return page.evaluate("() => document.querySelector('dialog').open")


def press(page, x, y, count, button="left"):
    """One press and release carrying click count `count` (what the operating system would report for a repeat)."""
    page.mouse.move(x, y)
    page.mouse.down(button=button, click_count=count)
    page.mouse.up(button=button, click_count=count)


# --- the tree before the fixes, served from memory (no project file written) --------------------------------------
LEGACY_REV = "06fa151"  # the audited tree's last src commit; src/ui differs from HEAD in these four files only
LEGACY_FILES = ["src/ui/dom.js", "src/ui/dialog.js", "src/ui/people.js", "src/ui/items.js"]


def legacy_sources():
    out = {}
    for rel in LEGACY_FILES:
        out[rel] = subprocess.run(["git", "show", f"{LEGACY_REV}:{rel}"], cwd=ROOT, capture_output=True, check=True).stdout.decode("utf-8")
    return out


def install_legacy(context, base, sources):
    def handler_for(body):
        def handler(route):  # one parameter only: Playwright passes (route, request) to a two-parameter handler
            route.fulfill(status=200, content_type="text/javascript", body=body)
        return handler

    for rel, body in sources.items():
        context.route(f"{base}/{rel}", handler_for(body))


def open_legacy_page(browser, base, sources, **kwargs):
    context, page, cap = open_page(browser, base, goto=False, **kwargs)
    install_legacy(context, base, sources)
    page.goto(base + "/")
    return context, page, cap
