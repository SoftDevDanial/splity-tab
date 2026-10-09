# Fix proposals, tried in throwaway copies (not applied to the repo)

The Dev Solver owns the patch. These two were tried so that the finder can say the suggested fix works and
breaks nothing. Both ran against the full suite in a scratch copy: **205 passed** each. Results:
`probe-fix-base-dialog.json`, `probe-fix-FIX-dialog.json`, `probe-fix-base-remove.json`, `probe-fix-FIX2-remove.json`.
Script: `scripts/probe_fix.py`.

## FIX for CR-01: swallow the second click of a double click once, after any click-driven close

`UIEvent.detail` is the click count. Measured (`probe-detail.json`, `probe-detail-dblclick.json`): `mouse.dblclick` sends
detail 1 then 2, a double tap within 200 ms sends 1 then 2, two taps 400 ms apart send 1 and 1. The guard installs itself
when the dialog is closed by a click, cancels a click whose detail is above 1, and removes itself on the next click of any
kind. No timer.

```js
function swallowSecondClick() {
  document.addEventListener("click", (event) => {
    if (event.detail > 1) {
      event.stopPropagation();
      event.preventDefault();
    }
  }, { capture: true, once: true });
}

const closeByClick = () => {
  swallowSecondClick();
  dialog.close();
};
// cancel click, start click (before onConfirm) and the backdrop click all call closeByClick()
```

| Check | base (shipped) | with FIX |
|---|---|---|
| Double mouse click and double tap on Cancel, 3 viewports (6 checks) | 6 FAIL, the draft changed | 6 PASS |
| Double click and double tap on the backdrop (12, 12), and on Start new bill, 3 viewports (12 checks) | 12 PASS | 12 PASS |
| A single click on Cancel still closes with focus on New bill | PASS | PASS |
| A later double click on a toggle still flips it twice (the guard does not linger) | PASS | PASS |

## FIX2 for WR-01: a Remove button ignores the second click of a double click

```js
remove.addEventListener("click", (event) => { if (event.detail <= 1) onRemove(id); });
```
(in `createRow` of `src/ui/people.js` and `src/ui/items.js`). A keyboard activation has detail 0, so Enter and Space still work.

| Check | base (shipped) | with FIX2 |
|---|---|---|
| Double click and double tap on Remove, item 2 of 4 and person 2 of 5 (4 checks) | 4 FAIL, two rows removed | 4 PASS, one row removed |
| A single click removes one row; a second click 700 ms later removes another | 2 PASS | 2 PASS |

## Tests that go with them
- Double click and double tap (`page.mouse.dblclick`, `page.touchscreen.tap` twice in a `has_touch` context) on **Cancel**
  with the S1 seed at 375 x 667. Assert the stored draft equals the seed text, the dialog is closed and focus is on New bill.
  Red on the shipped code (6 of 6 sizes and gestures).
- The same on **Remove {item}** with S1 and **Remove {person}** with a five person bill. Assert one row is gone.
