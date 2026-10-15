"""B6. Threat rows "the user's belief that the bill is kept" and "availability" (R28, R46, R47), with the suite's drivers.

python docs/modules/split-app/qa/security/20261015-222146/b6_save_warning.py --engine chromium|webkit
Four contexts. D-b (the localStorage getter throws until released), D-a (setItem throws until released), D-c (getItem
throws, setItem works) and a real full quota (a same-origin key fills the storage before the app loads, the shared
github.io origin case). Each records whether the warning shows at boot, after a typed character, and after the storage
comes back, what is stored, and every console line, page error and CSP violation. Writes b6_save_warning-<engine>.json.
"""
import argparse
import json

from common import Probe, ROOT, say

DRIVERS = {name: (ROOT / "tests" / "browser" / "storage" / f"{name}.js").read_text(encoding="utf-8")
           for name in ("fail-get", "fail-set", "fail-getitem")}
WARN = "() => !!document.querySelector('#notes .note.is-warn')"
FILL = """() => { let n = 0; const block = 'x'.repeat(1 << 20);
  try { for (; n < 64; n += 1) localStorage.setItem('hub.filler.' + n, block); return 'never full'; }
  catch (e) { try { for (let k = 0; k < 4096; k += 1) localStorage.setItem('hub.small.' + n + '.' + k, 'x'.repeat(1024)); } catch (e2) {}
    return 'full after ' + n + ' MiB-sized keys'; } }"""
FREE = "() => { for (const k of Object.keys(localStorage)) if (k.startsWith('hub.')) localStorage.removeItem(k); return true; }"


def typed(page, text):
    page.locator("#svc").click()
    page.keyboard.press("End")
    page.keyboard.type(text)


def run(engine):
    with Probe("b6_save_warning", engine) as probe:
        for name in ("fail-get", "fail-set", "fail-getitem", "real-quota"):
            row = {"driver": name}
            scripts = [DRIVERS[name]] if name in DRIVERS else []
            ctx = probe.context(extra_scripts=scripts, viewport={"width": 1280, "height": 800})
            try:
                page, rec = probe.page(ctx)
                if name == "real-quota":
                    page.goto(probe.base + "/src/system.css")
                    row["fill"] = page.evaluate(FILL)
                    rec["requests"].clear()
                probe.open_app(page)
                probe.stand_in(page)
                row["warning_at_boot"] = page.evaluate(WARN)
                typed(page, "1")
                row["warning_after_typing"] = page.evaluate(WARN)
                if name in ("fail-get", "fail-set"):
                    page.evaluate("() => window.dispatchEvent(new CustomEvent('test:storage', { detail: false }))")
                elif name == "real-quota":
                    page.evaluate(FREE)
                typed(page, "2")
                row["warning_after_storage_back"] = page.evaluate(WARN)
                if name != "fail-getitem":
                    stored = page.evaluate("() => localStorage.getItem('split.draft')")
                    row["stored_service_text"] = json.loads(stored)["bill"]["serviceText"] if stored else None
                row["service_on_screen"] = page.locator("#svc").input_value()
                row["csp"] = probe.violations(page)
                row.update(console=rec["console"], page_errors=rec["page_errors"], off_rule_requests=probe.off_rule_requests(rec))
            except Exception as error:  # noqa: BLE001
                row["error"] = f"{type(error).__name__}: {str(error)[:300]}"
            finally:
                ctx.close()
            probe.rows.append(row)
            say(json.dumps(row, ensure_ascii=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", choices=["chromium", "webkit"], default="chromium")
    run(parser.parse_args().engine)
