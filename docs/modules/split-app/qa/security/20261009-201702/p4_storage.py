"""Threat row 3 (R28): localStorage disabled, full or throwing.

Each case installs a storage failure through an init script (before any page script runs), boots the app cold and
drives a short flow with real gestures: type a subtotal of 100, add a person and type her name, switch to By item,
add an item, switch back, copy the summary. It records console errors, page errors, whether the S7 note appeared,
whether the shares came out right (RM 38.87, 38.87, 38.86, sum RM 116.60), and what a reload does.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

FAILURES = {
    "E1 window.localStorage getter throws SecurityError": """
      Object.defineProperty(window, "localStorage", { configurable: true, get() { throw new DOMException("The operation is insecure.", "SecurityError"); } });""",
    "E2 localStorage is null": """
      Object.defineProperty(window, "localStorage", { configurable: true, value: null });""",
    "E3 getItem throws": """
      Storage.prototype.getItem = function () { throw new DOMException("denied", "SecurityError"); };""",
    "E4 setItem throws QuotaExceededError every time": """
      Storage.prototype.setItem = function () { throw new DOMException("full", "QuotaExceededError"); };""",
    "E5 setItem works twice, then throws": """
      (() => { const real = Storage.prototype.setItem; let n = 0;
        Storage.prototype.setItem = function (k, v) { n += 1; if (n > 2) throw new DOMException("full", "QuotaExceededError"); return real.call(this, k, v); }; })();""",
    "E6 getItem returns undefined": """
      Storage.prototype.getItem = function () { return undefined; };""",
    "E7 the real quota is used up before the app boots": """
      (() => { try { const block = "x".repeat(1 << 20); let i = 0; for (;;) { localStorage.setItem("fill" + i, block); i += 1; }
        } catch (e) { try { const rest = "y".repeat(1024); let j = 0; for (;;) { localStorage.setItem("pad" + j, rest); j += 1; } } catch (e2) {} } })();""",
}
EXPECTED_SHARES = {"Person 1": "RM 38.87", "Person 2": "RM 38.87", "Dina": "RM 38.86"}
SHARES_JS = "() => Object.fromEntries([...document.querySelectorAll('table.shares tbody tr')].map((tr) => [tr.cells[0].textContent, tr.cells[tr.cells.length - 1].textContent]))"
AFTER_JS = "() => ({ note: !!document.querySelector('.note'), people: [...document.querySelectorAll('li.person input')].map((i) => i.value), subtotal: document.querySelector('#subtotal').value })"


def drive(page):
    page.locator("#subtotal").click()
    page.keyboard.type("100")
    page.get_by_role("button", name="Add person").click()
    page.keyboard.type("Dina")  # focus is on the new name field (R34)
    page.locator("label[for=mode-item]").click()
    page.get_by_role("button", name="Add item").click()
    page.locator("label[for=mode-even]").click()
    common.settle(page, 80)


def run_case(browser, base, script):
    ctx, page, cap = common.open_page(browser, base, viewport=(390, 844), extra_scripts=[script], goto=False)
    try:
        page.goto(base + "/")
        common.settle(page, 80)
        drive(page)
        shares = page.evaluate(SHARES_JS)
        page.get_by_role("button", name="Copy summary").click()
        common.settle(page, 60)
        status = page.evaluate("() => document.querySelector('p.status').textContent")
        note_before_reload = page.evaluate("() => !!document.querySelector('.note')")
        page.reload()
        common.settle(page, 80)
        return {"shares": shares, "status": status, "note_before_reload": note_before_reload,
                "after_reload": page.evaluate(AFTER_JS), "problems": cap.problems(base)}
    finally:
        ctx.close()


def body(browser, server, results):
    for name, script in FAILURES.items():
        got = run_case(browser, server.base, script)
        usable = got["shares"] == EXPECTED_SHARES and got["status"] == "Summary copied"
        clean = not got["problems"] and not got["note_before_reload"] and not got["after_reload"]["note"]
        row = {"case": name, "ok": usable and clean, "usable": usable, "clean": clean, **got}
        results["cases"].append(row)
        print(f"{'PASS' if row['ok'] else 'FAIL'} {name:52} shares ok {got['shares'] == EXPECTED_SHARES} status {got['status']!r} "
              f"note {got['note_before_reload']} after reload people {got['after_reload']['people']} subtotal {got['after_reload']['subtotal']!r} "
              f"problems {got['problems']}")


if __name__ == "__main__":
    common.run_probe("p4-storage", body)
