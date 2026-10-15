"""B6b. The real-quota row of B6 again, with a tight fill (B6 left about 1 KB free, so the draft still fitted).

python docs/modules/split-app/qa/security/20261015-222146/b6b_real_quota.py --engine chromium|webkit
A same-origin key fills localStorage in shrinking chunks down to one character before the app loads (the shared
github.io origin residual). The app then boots, a character is typed (the draft write must fail and the warning show),
the filler is removed by the same-origin code, a second character is typed (the warning must clear, R47).
Writes b6b_real_quota-<engine>.json.
"""
import argparse
import json

from common import Probe, say

WARN = "() => !!document.querySelector('#notes .note.is-warn')"
FILL = """() => { let keys = 0;
  for (let size = 1 << 20; size >= 1; size = size >> 1) {
    const block = 'x'.repeat(size);
    for (;;) { try { localStorage.setItem('hub.f' + keys, block); keys += 1; } catch (e) { break; } }
  }
  return keys; }"""
FREE = "() => { for (const k of Object.keys(localStorage)) if (k.startsWith('hub.')) localStorage.removeItem(k); return true; }"


def typed(page, text):
    page.locator("#svc").click()
    page.keyboard.press("End")
    page.keyboard.type(text)


def run(engine):
    with Probe("b6b_real_quota", engine) as probe:
        row = {"driver": "real quota, tight fill"}
        ctx = probe.context(viewport={"width": 1280, "height": 800})
        try:
            page, rec = probe.page(ctx)
            page.goto(probe.base + "/src/system.css")
            row["filler_keys"] = page.evaluate(FILL)
            rec["requests"].clear()
            probe.open_app(page)
            probe.stand_in(page)
            row["warning_at_boot"] = page.evaluate(WARN)
            typed(page, "1")
            row["warning_after_typing"] = page.evaluate(WARN)
            row["stored_draft_after_failed_write"] = page.evaluate("() => localStorage.getItem('split.draft')")
            page.evaluate(FREE)
            typed(page, "2")
            row["warning_after_storage_back"] = page.evaluate(WARN)
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
