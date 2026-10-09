"""O-1 check by the review: how large can an S1-shaped by-item bill be before the page scrolls sideways at 360 and 390?
(Record copy, see cr.py.)"""
import sys
sys.path.insert(0, "{temp}/claude/{project-id}/0fc4b490-9bf0-46ec-8ac8-08b33bc21485/scratchpad")
import cr

run = cr.Run().start()
try:
    seeds = run.seeds
    for viewport in [(360, 780), (390, 844)]:
        for factor in [1, 5, 10, 11, 12, 20, 100, 1000]:
            def scale(text):
                cents = round(float(text) * 100) * factor
                cents = min(cents, 9_999_999)
                return f"{cents // 100}.{cents % 100:02d}"

            def edit(draft):
                for item in draft["bill"]["items"]:
                    item["priceText"] = scale(item["priceText"])
            seed = seeds.changed(seeds.S1, edit)
            s = run.session(seed=seed, viewport=viewport)
            page = s.open()
            found = page.evaluate("""() => ({ overflow: document.documentElement.scrollWidth - window.innerWidth,
              total: document.querySelector('.final') ? document.querySelector('.final').textContent : null,
              table: document.querySelector('table.shares') ? document.querySelector('table.shares').getBoundingClientRect().width : null })""")
            run.note(f"{viewport[0]}px, prices x{factor}: total {found['total']}", {"overflow_px": found["overflow"], "table_width": found["table"]})
            s.close()
finally:
    run.stop()
    run.save("probe-overflow.json")
