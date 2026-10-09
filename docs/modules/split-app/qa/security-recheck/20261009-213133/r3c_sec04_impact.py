"""SEC-04 impact: what the user sees after a held Enter on Remove of the only item, against an ordinary press.

Same seed (S1 reduced to its first item), 390x844. Records the saved bill, the Items block and the shares panel text after
(a) an ordinary 90 ms Enter press and (b) an Enter held for ~700 ms (first auto-repeat at 520 ms). Then one single click on the
blank row's Remove, to show the extra row is undone with one action.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rc  # noqa: E402
from rc import seeds, btn  # noqa: E402

ONE_ITEM = seeds.changed(seeds.S1, lambda d: d["bill"].update(items=d["bill"]["items"][:1]))
PANEL = "() => ({ tape: document.querySelector('.tape').innerText.replace(/\\s+/g, ' ').trim(), items: [...document.querySelectorAll('li.item')].map((li) => [li.querySelector('input').value, li.querySelectorAll('input')[1].value, li.querySelector('.field.money') ? li.innerText.replace(/\\s+/g, ' ').trim() : '']) })"


def body(browser, server, results):
    base = server.base
    for label, held in (("ordinary 90 ms Enter press", False), ("Enter held ~700 ms", True)):
        ctx, page, cap = rc.open_page(browser, base, seed=ONE_ITEM, viewport=(390, 844))
        try:
            rc.settle(page)
            before = page.evaluate(PANEL)
            btn(page, "Remove Nasi lemak ayam").focus()
            if held:
                page.keyboard.down("Enter")
                page.wait_for_timeout(520)
                for _ in range(4):
                    page.keyboard.down("Enter")
                    page.wait_for_timeout(35)
                page.keyboard.up("Enter")
            else:
                page.keyboard.press("Enter", delay=90)
            rc.settle(page, 150)
            after = page.evaluate(PANEL)
            saved = rc.bill(page)
            row = {"case": label, "before": before, "after": after, "saved_items": saved["items"], "nextId": saved["nextId"], "problems": cap.problems(base)}
            if held:
                x, y = rc.centre(page.get_by_role("button", name="Remove Item 1", exact=True))
                page.mouse.click(x, y)
                rc.settle(page, 120)
                row["after_one_click_on_blank_row_remove"] = rc.bill(page)["items"]
            results["cases"].append(row)
            print(label, "->", {k: v for k, v in row.items() if k != "before"})
        finally:
            ctx.close()


if __name__ == "__main__":
    rc.run_probe("r3c-sec04-impact", body)
