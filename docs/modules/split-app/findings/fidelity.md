---
module: split-app
kind: fidelity
status: one-to-one
date: 2026-10-15
head: 82e2285 (code as d58f4ce, no change under src/, index.html, tests/ or docs/design/ since af782d0)
scope: R40 both halves (the A19 pixel gate read back from its own files, the FE element checklist of qa.md run on the running app), the three sub-threshold pairs, QA-S5-4
counts: { findings: 0, observations: 9 }
mismatch_pct: 0
artifacts: ./docs/modules/split-app/qa/fidelity/20261015-193738/ (A19 gate) and ./docs/modules/split-app/qa/fidelity-checklist/20261015-225153/ (this run)
---
# Fidelity gate, split-app (v1.1.0, step 5)

Written by the fidelity finder (read-only) on 2026-10-15 at HEAD `82e2285`, whose code is `d58f4ce`. `git diff --stat af782d0 HEAD -- src index.html docs/design` and `git diff --stat d58f4ce HEAD -- src index.html tests docs/design` are empty, and `git status` shows no change there. `git hash-object --no-filters src/system.css` is `bf30ddadb8c756dc5d462243c642c218597ae0ac`. Goldens were opened as files and read only. Nothing under `src/`, `tests/`, `docs/design/`, any spec, qa.md, README or ledger was written.

## Verdict
**1-to-1. status one-to-one. 0 findings (FID-S5 has no entry). 9 observations.**

- **Pixel half (A19's run), confirmed from its files.** Both controls behaved as written (self-compare 0 pixels with equal sizes, no-seed 184588 pixels and unequal sizes). All 40 pairs report `"mismatch_pixels": 0` and `"dimensions_match": true` at threshold 0.01. Each pair's `report.json` names the golden, seed and after-load script of qa.md's table, and each `PASS` line of `run.log` carries the same count as its report. 38 of the 42 PNG pairs are byte-identical. The other four are the no-seed control (by design) and the three sub-threshold pairs below. The read-back is `qa/fidelity-checklist/20261015-225153/a19-gate-readback.json`.
- **Checklist half, this run, Chromium 149.0.7827.55.** Every row of qa.md "FE element checklist" (K1, KO, K2, P1, PO, PR, P2, M1, BE, RE, BU, BR, BT, W1, ST) was checked at every width its section names, on the app in the golden's state reached by the gate's own seeds and after-load scripts (`tests/browser/fidelity/`), and by real gestures for the ST, focus and motion rows. 715 row and width checks on the 40 states (3572 measurements) plus 38 gesture rows (185 measurements). All pass except two rows whose figure the golden itself does not show (O-1, O-2). The app equals the golden there.
- **Element by element.** In all 40 states, 5578 rendered elements were paired between golden and app in document order, with 0 unpaired apart from the allowed differences, and equal tag, id, classes, own text, ARIA and the R3 attributes, input value and checked state, `::before`, `::after` and `::placeholder`, about 150 computed properties each, and the rect. The largest rect difference is 1/64 px (P1 at 1280, the bottom edge 632.797 against 632.8125). Every other rect is equal to the last bit. What differs is allowed. It is the `checked` content attribute (the state is equal, O-3), `user-select: text` and the modal UA rules inside an open modal dialog and the stand-in z-index (difference 3), `data-down` (difference 8), and the `fit-wide` and `fit-narrow` spans of `bill-twelve` (difference 9).

## Findings
None. No element, text, order, state, focus ring or motion of the app differs from its golden in Chromium.

## The pixel half, A19's run
| pair | report.json | PNGs | my reading |
|---|---|---|---|
| control-self-390x844 | 0 px, sizes equal | byte-identical | as written |
| control-noseed-390x844 | 184588 px (56.08%), 390x950 against 390x844 | differ | as written, the gate can fail |
| 37 pairs | 0 px, sizes equal | byte-identical | 1-to-1 |
| bill-unreadable-390x844 | 0 px | 19 px differ, at most 1 level | engine raster, below |
| new-bill-dialog-390x844 | 0 px | 77 px differ, at most 2 levels | engine raster, below |
| new-bill-dialog-1280x800 | 0 px | 84 px differ, at most 2 levels | engine raster, below |

## The three sub-threshold pairs (judged)
The captures are `chromium/raster/raster.json` and `chromium/raster-2/raster-2.json` with their PNGs, rendered with the gate's flags (`--force-color-profile=srgb --hide-scrollbars --disable-lcd-text`). My renders reproduce the gate's counts exactly (19, 77, 84 pixels, same boxes). A re-render of each golden gives 0 pixels, and the control pair `bill-items-390x844` gives 0.

- **bill-unreadable-390x844, recorded engine difference (raster), not a finding.** The 19 pixels are the bottom corners of the two person fields (`li.field.person` at y 199 to 245), 1 level each. Computed styles and rects of every element are equal (`chromium/compare.json`). The cause is paint history. The app puts the note in by script after first paint. When the note is taken out and put back by script on both pages (in memory only), golden and app are pixel-identical (0 pixels, `raster-2.json`), and putting the golden's own note back moves 24 of its pixels by 1 level.
- **new-bill-dialog-390x844 and -1280x800, recorded engine difference (top layer against the golden's stand-in, allowed difference 3), not a finding.** The pixels are the four rounded corners of Cancel (`button.btn.btn-ghost.btn-lg`, 41,466 308x48 at 390 and 725.172,416 89.828x48 at 1280), at most 2 levels. Styles and rects are equal. The golden page with its stand-ins removed and its dialog opened by `showModal()` in memory equals the app at 1280 to 0 pixels. At 390 the Cancel corners become equal too. The 7 pixels left sit in the strip's top edge, the same 7 pixels the app's own page shows between two consecutive full-page captures.

## QA-S5-4 (judged against the goldens, in WebKit 26.5 with Chromium as control)
The captures are `webkit/qa-s5-4/probe.json` and `chromium/qa-s5-4/probe.json` with their PNGs, `webkit/qa-s5-4-focus/probe.json` and `chromium/qa-s5-4-focus/probe.json`.

- **The page faintly through the Splits sheet. Recorded engine difference, not a finding.** The golden `splits-sheet.html` shows the same. Measured as the change inside the sheet when `div.app` is hidden in memory, at 390x844. In WebKit golden and app give the same figures (mean 0.236 levels, max 4.3, 2.12% of pixels over 2 levels, mean edge 0.1139). In Chromium both give 0.099, 1.3, 0%, 0.0098. The glass computes the same on both sides in both engines (`rgba(27, 33, 43, 0.92)`, the 155 degree gradient, `blur(24px) saturate(1.4)`). WebKit supports `backdrop-filter`, so the solid fallback of system.md does not apply. The direct golden against app pixel difference inside the sheet (16452 pixels in WebKit, 16550 in Chromium, at most 20 levels) is the hover state of the sheet's Copy summary under the pointer that clicked Splits, the same in both engines.
- **The ring on Splits after the sheet closes. Recorded engine difference, not a finding.** After a mouse click on the sheet's Close, Splits has focus in both engines. In WebKit it matches `:focus-visible` and draws the ring (`solid 2px rgb(163, 170, 255) 2px`), in Chromium it does not. WebKit does the same for Cancel after a mouse click on New bill (M1-08 holds in Chromium only, the checklist's engine). The golden's own mechanism gives the same result in WebKit. On the golden `new-bill-dialog.html` in memory, after a mouse click on New bill, Cancel with `autofocus` and `showModal()` matches `:focus-visible` with the ring, the same as focus by script, so allowed difference 10's "same result" holds in WebKit as well. WebKit leaves focus on `body` after a mouse click on a button (spec R59), so a later script focus counts as visible. One measured fact for the planner. In WebKit 26.5, `focus({ focusVisible: false })` gives no `:focus-visible` and no ring. The sheet itself after a mouse open matches `:focus-visible` in WebKit but draws no ring (its outline is none), so P2-09 looks the same in both engines.

## Checklist half, by section (Chromium)
Row results are in `chromium/rows.json` (every check with the app's value and the golden's value beside it), `chromium/rows-summary.json` and `chromium/states-2/states.json`.

| section | golden, widths | row and width checks | result |
|---|---|---|---|
| K1 | bill-items, 390 360 1280 | 165 (64 rows, K1-64 in `chromium/inventory/inventory.json`) | 164 pass, K1-44 at 1280 see O-1 |
| KO | bill-items-open, 390 360 | 71 | pass |
| K2 | bill-even, 390 360 1280 | 80 | pass |
| P1, PO, PR | spare-sen, spare-sen-one, spare-sen-random, 390 360 1280 | 93 | pass |
| P2 | splits-sheet, 390 360 | 18 plus P2-09 | pass |
| M1 | new-bill-dialog, 390 360 1280 | 21 plus M1-08 | pass |
| BE, RE, BU, BR | bill-empty, rate-error, bill-unassigned, bill-unreadable | 172 | pass |
| BT | bill-twelve, 390 360 1280 | 38 plus BT-07 | pass |
| W1 | bill-large, 390 360 1280 | 57 | 56 pass, W1-02 at 1280 see O-2 |
| ST | states.html pieces, real gestures | ST-01 to ST-17 (21 row and width checks) | pass |
| Focus | Tab from the top in K1 (390, 1280), KO (390, 360), BE, RE, BR (390), app against golden | 7 walks, the ring at every stop equal to the golden's, every stop `:focus-visible`, KO-08 37 controls none under the strip while focused, ST-15 red edge kept with the ring | pass |
| Motion | K1 at 390 and 1280, reduce and no-preference | Under reduce no animation at load or after any gesture, and every listed transition 0s. Under no-preference the foil 1.8 s and the card light 1.4 s run once, the section reveal and caret 200 ms, the sheet lift 240 ms, P1's rise 200 ms, M1's fade 160 ms, hover 120 ms, nothing running 3 s after load or 1 s after a gesture, transitions equal to the golden's (`chromium/states-2/motion.json`) | pass |

K1-64. `src/icon.svg` is served as `image/svg+xml`, 470 bytes, SHA-256 `7b5e4176a6182d23f06073ff181f01bbb73e2ac562f78d58a930ffb80fe7fef2`, byte-equal to the golden href after its comma, one distinct href in all fifteen goldens.

## Observations (no finding, the app equals the golden in each)
- **O-1. K1-44 at 1280.** qa.md says the Items heading row is 20 px under the hairline. The golden has 16 px at 1280 (margin 16, border 1, padding 16), the app the same. 20 px holds at 390 and 360. A checklist wording point for the planner.
- **O-2. W1-02 at 1280.** qa.md says "the 412 px card body". The golden's `#rbody` is 410 px (460 less 2 px of edge and 48 px of padding), the app the same. A wording point.
- **O-3.** The app sets the radio's `checked` property, the golden the `checked` attribute. The checked state is equal everywhere, and R3 compares the state. Not rendered.
- **O-4. Readings that hold only one way.** K1-01 "60 px" is the phone top bar less its 1 px hairline (border box 61), "64 px at 1280" is the border box (63 plus 1). K1-40 "Split starts at 229" is where the Split block ends (it starts at 170), as BE-14 and KO-07 use "ends". K1-02 "computed color and fill equal" holds as equal to the golden's (`fill` is `--accent-ink`, `color` is `--text`, on both sides). K1-10 "RM in body text" holds for the colour (`--text`, the figure `--total-ink`), the family is monospace on both sides. K1-54's "104px" column is 128 px at 1280 on both sides, as K1-47 says. BR-02 "44 px tall" is the content box (border box 46 with the 44 px Dismiss note), ST-10's 44 px at 1280 is the border box (no dismiss), system.md Banner says 44 on desktop.
- **O-5. ST-09.** "Two lines where the strip is narrower than the sentence". At 390 and 360 the sentence is 313.3 px in 356 and 326 px of room, one line, no overflow (`chromium/states-2/ST-09-*.app.json.gz`). The canvas width printed in `states-2/states.json` for this row used the default canvas font and is wrong. The verdict uses the dump.
- **O-6. P1 at 1280.** Its top is 1/64 px off the golden's (376.797 against 376.8125). The PNGs are byte-identical.
- **O-7. First gesture pass.** `chromium/states/` is the first pass of the gesture rows. Four of its checks were my own measuring errors (a width compare qa.md excludes for ST-03, the ST-09 line rule, ST-10's 44 px reading, and Tab walks that did not start at the top). `chromium/states-2/` is the corrected pass the verdict uses. Kept, never overwritten.
- **O-8. WebKit screenshots.** The five WebKit `page.screenshot` calls of the app each logged "Refused to apply a stylesheet" and one `style-src-elem` violation (`webkit/qa-s5-4/probe.json`), the known effect of the tool (spec R59 (4)), not of the app.
- **O-9. Repeated full-page captures.** Two consecutive full-page captures of the same app page differ in the strip's top edge (7 to 9 pixels, `raster/raster.json`). No animation is listed (`getAnimations()` empty under reduce). Pixel gate pairs take one capture per side and are unaffected.

## NOT RUN and Not done
- **Not done. The element-by-element compare in WebKit for the 40 states.** R40 and the checklist scope fidelity to Chromium (ledger S5 row 2), so it is no gate. Left out to stay within this finder's context budget. QA-S5-4's two points were measured in WebKit above.
- **NOT RUN. Hover and pressed states.** The checklist has no row for them and no golden draws them.

## Evidence (listed on disk)
`docs/modules/split-app/qa/fidelity-checklist/20261015-225153/`
- `a19-gate-readback.json`
- `chromium/compare.json`, `chromium/run.log`, 80 `chromium/<pair>.golden.json.gz` and `.app.json.gz` dumps
- `chromium/inventory/inventory.json`, `run.log`, 80 inventories
- `chromium/rows.json`, `chromium/rows-summary.json`
- `chromium/states/` (first pass) and `chromium/states-2/` (`states.json`, `tab-rings.json`, `motion.json`, `run.log`, 38 dumps, 9 PNGs)
- `chromium/raster/` (`raster.json`, `run.log`, 22 PNGs), `chromium/raster-2/` (`raster-2.json`, `run.log`, 4 PNGs)
- `chromium/qa-s5-4/` and `webkit/qa-s5-4/` (`probe.json`, `run.log`, 7 PNGs each), `chromium/qa-s5-4-focus/probe.json`, `webkit/qa-s5-4-focus/probe.json`

The scripts that made them are in this finder's scratchpad (`split-fid-step5/`), outside the project.
