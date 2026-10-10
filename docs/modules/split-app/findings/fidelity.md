---
module: split-app
kind: fidelity
status: clean
counts: { critical: 0, high: 0, medium: 0, low: 0 }
mismatch_pct: 0
mismatch_pixels: { bill-empty_390: 0, bill-empty_1280: 0, bill-even_390: 0, bill-even_1280: 0, bill-items_390: 0, bill-items_1280: 0, bill-unassigned_390: 0, bill-unassigned_1280: 0, new-bill-dialog_390: 0, new-bill-dialog_1280: 0 }
artifacts: ./docs/modules/split-app/qa/fidelity/20261010-133017/ (the ten gate pairs) and ./docs/modules/split-app/qa/fidelity-checklist/20261010-133500/ (checklist, whole-page, interaction and control evidence)
---
# Fidelity gate, split-app

> Written by the fidelity finder (read-only on the product), 2026-10-10, against `4a3c5bf` on `main`. Goldens: `docs/design/bill-empty.html` (S3), `bill-even.html` (S2), `bill-items.html` (S1), `bill-unassigned.html` (S5), `new-bill-dialog.html` (M1) and the specimen sheet `states.html` with `states.md`. The working tree was clean before the run, and `git status --short` afterwards lists only my two new evidence folders.

## Verdict

**1-to-1. status: clean. 0 findings (0 critical, 0 high, 0 medium, 0 low), 12 observations.**

- **Pixel half of R40.** All ten pairs give **0 mismatching pixels and `dimensions_match` true** at threshold 0.01, on harness 2.1.3. Eight of the ten candidate screenshots are **byte-identical** to their golden screenshots, so for those not one pixel differs at any level. The two M1 pairs differ at 141 pixels (390) and 103 pixels (1280) by at most 2 of 255 on a channel, every one of them on a rounded corner, the same pixels in all six gate runs of 2026-10-09 and 10 (O-02).
- **Element half of R40.** All **131 rows of the FE element checklist pass** (S1 53 of 53, S2 28 of 28, S3 14 of 14, S5 12 of 12, M1 9 of 9, states sheet 15 of 15), each measured on the running app against the golden or the specimen, at 390 x 844 and 1280 x 800 (and 360 x 780 where a row names it). I added **26 finder rows** the checklist does not have (hover, pressed, focus rings, Tab order, disabled, placeholder, motion, layouts at seven widths, CSS bytes, document properties, icons), all 26 pass. 157 of 157 rows in all.
- **Whole-page comparison.** The golden's DOM and the app's DOM were compared element by element for the five screens at seven widths (360, 390, 599, 600, 1023, 1024, 1280), 35 pairs, 4,123 paired elements, 2,242,912 property comparisons. The 28 pairs of S1, S2, S3 and S5 give **0 differences** in structure, attributes, own text, input values, rectangles, computed styles and pseudo elements. The 7 M1 pairs differ only in the native modal's own properties (O-03).
- **The gate is honest, and I tested that it can fail.** Same page states, equal dimensions, nothing masked. I also made 13 one-thing mutants of the running page. My rows and the whole-page comparison caught 13 of 13. The harness rule alone (threshold 0.01) misses 5 of them, the one-colour-level changes, which is why this report also counts pixels that differ at any level.
- The 0-pixel baseline measured on 2.1.1 **holds on 2.1.3**, and at 360, 600 and 1024 as well (15 extra harness runs, 15 of 15 at 0, O-04).
- One documented deviation is **not counted**: the golden note `new-bill-dialog.md` says a backdrop click does nothing, the app closes the dialog as Cancel, by the orchestrator's ruling CG-8 (O-01). Say so if you want it counted as one low finding.

Functional QA was taken as green from `findings/regression-qa.md` (340 of 341, R40 the one untested item, which this report now covers). I did not re-run the full suites. I ran the 14 `R40` tests that guard the gate's own scaffolding (`python -m pytest tests/browser -q -k R40 -p no:cacheprovider`, 14 passed).

## Gate conditions
| Item | Value |
|---|---|
| Harness | `{sdlc}/harness/fidelity.py`, plugin version **2.1.3** (`.claude-plugin/plugin.json`), frozen mode, unmodified. `bypass_csp` and `reduced_motion=reduce` are the harness's own. Started by the project's runner `python tests/browser/fidelity/run.py` with `sys.executable` |
| Runtime | headless Chromium 149.0.7827.55, Playwright 1.61.0, Pillow 12.3.0, numpy 2.4.6, Python 3.14.0, Windows 11 (10.0.26200) |
| Flags (every pair) | `--dpr 1 --color-scheme light --browser-arg=--disable-lcd-text --fixed-time 2026-10-08T09:00:00 --threshold 0.01`, full page |
| State flags | S3 none (a fresh browser per render, empty storage). S2 `--candidate-init-script seed-s2.js`. S1 `seed-s1.js`. S5 `seed-s5.js`. M1 `seed-s2.js` plus `--candidate-after-load open-new-bill.js`. Each seed file is one statement that stores exactly the seed qa.md gives (checked, DC-04) |
| Server | `python -m http.server 61288 --bind 127.0.0.1` from the project root (pid 13580), stopped, "port free again True" printed by the runner |
| Budget | A pair passes only with `dimensions_match` true and 0 mismatching pixels (qa.md). All ten pass |
| Run folder | `docs/modules/split-app/qa/fidelity/20261010-133017/`, with `run.log` (the commands, the server PID and port, a PASS line per pair, "10 of 10 pairs pass") |
| My own measurements | Playwright Chromium with the shipped CSP live (no `bypass_csp` except where a script reproduces the harness and says so), reduced motion unless a row tests motion, `--force-color-profile=srgb --hide-scrollbars --disable-lcd-text`, 1x scale. Every app context carried the clipboard recorder or the reject script, so no run touched the operating system clipboard. The scripts that record the console (`dom_diff`, `rows_screens`, `rows_states`, `interactions`) logged 0 console errors, 0 warnings and 0 page errors |

## The ten captures
| Capture | Mismatching pixels (threshold 0.01) | `dimensions_match` | Golden / candidate size | Pixels that differ at any level | Evidence (under `docs/modules/split-app/qa/fidelity/20261010-133017/`) |
|---|---|---|---|---|---|
| bill-empty (S3) 390x844 | **0** | true | 390x844 / 390x844 | 0 (files byte-identical) | `bill-empty-390x844/` |
| bill-empty (S3) 1280x800 | **0** | true | 1280x800 / 1280x800 | 0 (byte-identical) | `bill-empty-1280x800/` |
| bill-even (S2) 390x844 | **0** | true | 390x1189 / 390x1189 | 0 (byte-identical) | `bill-even-390x844/` |
| bill-even (S2) 1280x800 | **0** | true | 1280x800 / 1280x800 | 0 (byte-identical) | `bill-even-1280x800/` |
| bill-items (S1) 390x844 | **0** | true | 390x1711 / 390x1711 | 0 (byte-identical) | `bill-items-390x844/` |
| bill-items (S1) 1280x800 | **0** | true | 1280x1129 / 1280x1129 | 0 (byte-identical) | `bill-items-1280x800/` |
| bill-unassigned (S5) 390x844 | **0** | true | 390x1506 / 390x1506 | 0 (byte-identical) | `bill-unassigned-390x844/` |
| bill-unassigned (S5) 1280x800 | **0** | true | 1280x1129 / 1280x1129 | 0 (byte-identical) | `bill-unassigned-1280x800/` |
| new-bill-dialog (M1) 390x844 | **0** | true | 390x844 / 390x844 | 141, at most 2 of 255, all 141 on rounded corners, box x 16 to 373, y 305 to 538 | `new-bill-dialog-390x844/` |
| new-bill-dialog (M1) 1280x800 | **0** | true | 1280x800 / 1280x800 | 103, at most 2 of 255, all 103 on rounded corners, box x 120 to 1159, y 32 to 499 | `new-bill-dialog-1280x800/` |

Each folder holds `golden.png`, `candidate.png`, `diff.png`, `styles.json`, `report.json`. I opened `candidate.png` of M1 at 390 (the S2 page dimmed by the scrim with the dialog centred, "Start a new bill?", the stacked Start new bill and Cancel) and of S1 at 1280 (two columns, the panel card at the right, the check row in green). Both show the intended state. The expected sizes agree with the heights the earlier runs recorded.

### Is the pixel run honest
- **Same page states.** The seed scripts hold exactly the S1, S2 and S5 drafts qa.md gives (DC-04), and the app boots into them through its own load path. S3 is a cold boot. M1 is S2 with the dialog opened. The screenshots and the byte-identical results show each side in the state the golden draws.
- **Dimensions equal in all ten pairs**, so the diff compares whole pages, not a cropped overlap.
- **Nothing masked.** The harness has no mask option. It screenshots the full page and counts every pixel whose RGB distance exceeds 0.01 of the maximum. Because 8 of 10 pairs are byte-identical, no tolerance is used in them at all. The runs are deterministic: the candidate and golden screenshots of M1 have the same hashes in all six gate runs (2026-10-09 17:27 to 2026-10-10 13:30).
- **The M1 blur hides nothing real.** `open-new-bill.js` makes a synthetic click and then blurs, to remove the focus ring a synthetic click would show on Cancel. I opened the same dialog with a real mouse click and no blur: Cancel holds focus with `:focus-visible` false and outline style none (M1-07), and in my own captures the render equals the golden turned into a native modal with **0 differing pixels at 360, 390 and 600** (O-02).
- **The harness's own `styles.json`** compared golden against candidate: all 10 pairs have 0 rectangle differences and 0 style differences among the 27 properties it dumps, apart from M1's `dialog.dialog` `overflow` and the golden's `div.backdrop` (native modal, O-03). Its `text` field differs on some containers only because it cuts textContent at 80 characters and the goldens keep white space between elements (allowed difference 5) and the app keeps the hidden mode block in the DOM (allowed difference 7). No leaf text differs (O-08).
- **What the harness cannot see**, and what covers it. It forces reduced motion, bypasses the CSP, uses 2 viewports, and photographs no hover, focus, pressed, disabled or error state. The IX rows, the ST rows, the layout rows and the CSP-live measurements cover those (O-04, O-05).

## Whole-page comparison behind the pixel counts
Every rendered element (display other than none) of the golden and the app, paired in document order: tag, id, class list, every attribute, own text, input value, checked and disabled, rectangle, every computed property (544 per element: Chromium's longhands, the shorthands it does not list, and the custom properties), and `::before` and `::after` computed style. Script `dom_diff.py`, output `dom_diff_all.json`.

| Screen | Elements (golden / app) | Pairs (widths) | Structure, attribute, text, value, rectangle, style, pseudo differences |
|---|---|---|---|
| S3 bill-empty | 57 / 57 | 7 | **0** |
| S2 bill-even | 107 / 107 | 7 | **0** |
| S1 bill-items | 174 / 174 | 7 | **0** |
| S5 bill-unassigned | 138 / 138 | 7 | **0** |
| M1 new-bill-dialog | 114 / 113 | 7 | the golden's stand-in `div.backdrop` (1), `interactivity` inert against auto on the 107 elements inside `.app` and on `.total::before`, and on `dialog.dialog` and its children the UA modal rules `overflow` (auto), `max-height` (calc(100% - 38px)), `overlay` (auto) and `user-select` (text). All are the native modal (allowed difference 4, O-03) |

Widths: 360, 390, 599, 600, 1023, 1024, 1280. 497 attribute differences were classed allowed: 301 `value` attributes (compared as properties), 35 `checked`, 154 `placeholder` on name inputs (ruling 4), 7 `inert` on the golden's `.app`. No other attribute differs. The rectangle comparison is exact (0.01 px), so every spacing, size and position in the five screens is equal to the golden at every width.

## FE element checklist
Every PASS below includes this half: **the app's element equals the golden's element** (or the specimen's, for the ST rows) in rectangle, text, attributes less the allowed differences, and all computed properties (544 per element for the screen rows, 471 for the specimen rows after dropping the ones that follow only from box size, custom properties and `list-style`). The measured column gives the literal values qa.md and `system.css` call for, read from the running app. Values read "390 / 1280" where the viewport changes them, otherwise one value for both. Every measured string is in `docs/modules/split-app/qa/fidelity-checklist/20261010-133500/checklist_full.md` (1,065 entries). Row scripts: `rows_screens.py`, `rows_states.py`, `interactions.py`, `static_checks.py`, `misc_checks.py`.

### S1 `bill-items.html` (53 rows, all PASS)
| Id | Element | Result | Measured |
|---|---|---|---|
| S1-01 | Wordmark | PASS | `h1.wordmark` "Split", 22/28, 700, ink, letter-spacing -0.22px (-0.01em) |
| S1-02 | Header button | PASS | `.btn.btn-outline` "New bill", field fill, 1px line-strong, radius 6, 15/20 600 ink. Right edge 374 / 1160, the content edge of `.bar` |
| S1-03 | People heading | PASS | `h2#h-people` "People", 18/24 700, 12px above its grid |
| S1-04 | Person 1 field | PASS | `li.field.person` 44 high, field fill, 1px line-strong, radius 6. Input "Aisyah", aria-label "Person 1 name", maxlength 20, 16/24 ink, padding 0 12, 42 high |
| S1-05 | Person 1 remove | PASS | "Remove Aisyah", enabled, 44x44, borders 1px line-strong top, right, bottom and 1px line (lighter) left, radii 0 6 6 0, ink-muted. X svg 20x20, fill ink-muted |
| S1-06 | Person 2 field | PASS | Value "Ben", aria-label "Person 2 name", maxlength 20, same box as S1-04 |
| S1-07 | Person 2 remove | PASS | "Remove Ben", enabled, as S1-05 |
| S1-08 | Person 3 field | PASS | Value "Chen", aria-label "Person 3 name", maxlength 20 |
| S1-09 | Person 3 remove | PASS | "Remove Chen", enabled, as S1-05 |
| S1-10 | Add person | PASS | `.btn.btn-outline` "Add person", enabled, field fill, 1px line-strong, 15/20 600 ink, one grid cell wide: 175 at x199 y168 / 180 at x120 y188. Plus svg 18x18 ink-muted |
| S1-11 | People grid | PASS | `ul.cells` grid, 2 columns "175px 175px" / 3 columns "180px 180px 180px", gaps 8 and 8 |
| S1-12 | Mode switch | PASS | `fieldset.mode` grid, field fill, 1px line-strong, radius 6, overflow hidden, 24 above. Legend "Split mode" sr-only 1x1. Halves 178x44 and 178x44 / 277x44 and 277x44, divider 1px line-strong on the By item half |
| S1-13 | Even label | PASS | Unchecked: transparent over the field fill, ink, 15/20 600. Radio `checked` false |
| S1-14 | By item label | PASS | Checked: ink fill, on-ink text, 15/20 600. Radio `checked` true |
| S1-15 | Items heading | PASS | `h2#h-items` "Items", 18/24 700. The Subtotal block is not rendered (0 shown, 0 in the golden) |
| S1-16 | Item 1 name | PASS | Input "Nasi lemak ayam", aria-label "Item 1 name", maxlength 40, 16/24. Wrapper 44 high, field fill, 1px line-strong, radius 6 |
| S1-17 | Item 1 price | PASS | `span.field.money` 96x44 / 120x44. Unit "RM" ink-muted, aria-hidden. Input "15.90" right aligned, aria-label "Item 1 price in RM" |
| S1-18 | Item 1 remove | PASS | "Remove Nasi lemak ayam", 44x44, ink-muted, radius 6, transparent. X svg 20x20 |
| S1-19 | Item 1 toggles | PASS | `div.who` role group "Who had Nasi lemak ayam", gap 8, 8 under the line. Aisyah `aria-pressed` true (ink fill, on-ink, ink border), Ben and Chen false (field fill, ink, 1px line-strong). Each 44 high, 15/20 600, radius 6, padding 0 12 |
| S1-20 | Item 2 name | PASS | "Char kuey teow", "Item 2 name", maxlength 40 |
| S1-21 | Item 2 price | PASS | "13.50", "Item 2 price in RM", 96 / 120 wide |
| S1-22 | Item 2 remove | PASS | "Remove Char kuey teow", 44x44 |
| S1-23 | Item 2 toggles | PASS | "Who had Char kuey teow". Ben pressed only |
| S1-24 | Item 3 name | PASS | "Mee goreng mamak", "Item 3 name" |
| S1-25 | Item 3 price | PASS | "12.00", "Item 3 price in RM" |
| S1-26 | Item 3 remove | PASS | "Remove Mee goreng mamak", 44x44 |
| S1-27 | Item 3 toggles | PASS | "Who had Mee goreng mamak". Chen pressed only |
| S1-28 | Item 4 name | PASS | "Satay, 10 sticks", "Item 4 name" |
| S1-29 | Item 4 price | PASS | "18.00", "Item 4 price in RM" |
| S1-30 | Item 4 remove | PASS | "Remove Satay, 10 sticks", 44x44 |
| S1-31 | Item 4 toggles | PASS | "Who had Satay, 10 sticks". Aisyah and Chen pressed, Ben not |
| S1-32 | Item separators | PASS | Item 1 border-top 0, padding 0 16. Items 2 to 4 border-top 1px solid line, padding 16 above and below |
| S1-33 | Add item | PASS | `.btn.btn-outline` "Add item", 44 high, natural width 122.78 (not the 358 / 1040 line), left edge on the list edge (x16 / x120), directly after the list (y841 / y861), plus svg 18x18 ink-muted |
| S1-34 | Charges heading | PASS | `h2#h-charges` "Charges", 18/24 700 |
| S1-35 | Service label | PASS | `label.label` "Service charge" plus hidden " in percent" (sr-only 1x1), 15/20 600, block, 8 above the field, ink |
| S1-36 | Service input | PASS | Value "10", right aligned, padding 0 2 0 12, aria-describedby "charges-hint". Field 175 at x16 / 180 at x120. "%" unit ink-muted, aria-hidden, padding-right 12 |
| S1-37 | SST label | PASS | "SST" plus hidden " in percent", as S1-35 |
| S1-38 | SST input | PASS | Value "6", aria-describedby "charges-hint". Field 175 at x199 / 180 at x308, "%" unit |
| S1-39 | Hint | PASS | `p.hint#charges-hint` "Set a charge to 0 if your bill already includes it.", 14/20 400 ink-muted, 8 above |
| S1-40 | Panel frame | PASS | 390: full bleed, 390 wide at x0, top rule 2px ink, bottom 1px line, no side borders, radius 0, padding 20 16 24, 32 above. 1280: 420 wide at x740, 1px ink border, radius 6, sticky top 24, padding 24, top 100 equals the People block's top 100. Scrolled 120 px the panel sits at 24 in the app and in the golden |
| S1-41 | Summary heading | PASS | `h2#h-summary` "Bill summary", 18/24 700 |
| S1-42 | Subtotal row | PASS | Empty operator, "Subtotal", "RM 59.40" right aligned, no wrap, no working line |
| S1-43 | Service row | PASS | Operator "+" (20 wide, 600, ink-muted, 8 right), "Service charge", "RM 5.94", working "10% of RM 59.40" 15/20 ink-muted indented 28 |
| S1-44 | SST row | PASS | "+", "SST", "RM 3.92", working "6% of RM 65.34" |
| S1-45 | Total row | PASS | Margin-top 12, padding-top 12. `::before` rule absolute top 0, left 28, right 0, 1px solid ink. "=" operator, label 18 700 ink, amount cell 26/32 700, `span.final` "RM 69.26" with border-bottom 3px double ink, line-height 29.9 |
| S1-46 | Shares heading | PASS | `h2#h-shares` "Shares", 18/24 700. Section starts 32 under the Bill summary section (gap measured 32) |
| S1-47 | Table heads | PASS | Hidden "Person" (sr-only 1x1), "Items", "+Charges", "=Share", 13/18 600 ink-muted, right aligned, bottom aligned, padding 0 0 4. Operators inline, 4 right margin. Table 358 / 370 wide, 8 under the heading |
| S1-48 | Row Aisyah | PASS | Name 15 600 ink, left, padding-left 28. "RM 24.90" and "RM 4.14" 14 400 ink-muted right. "RM 29.04" 18 700 ink |
| S1-49 | Row Ben | PASS | "RM 13.50", "RM 2.24", "RM 15.74", same styles |
| S1-50 | Row Chen | PASS | "RM 21.00", "RM 3.48", "RM 24.48", same styles |
| S1-51 | Check row | PASS | Check svg 18x18 accent, absolute left 0 top 14 (x16 / x765, in the gutter). "Adds up to" accent 15 600, padding-left 28, with the 1px ink rule from 28 (background 100% 1px at 28px 0). "RM 59.40" and "RM 9.86" 14/400 ink-muted, "RM 69.26" 18/700 accent. Each cell 1px ink top border, padding-top 12 (O-06) |
| S1-52 | Copy summary | PASS | `button.btn.btn-primary.btn-large.btn-block.copy` "Copy summary", ink fill, on-ink, 1px ink, 48 high, 358 / 370 wide (full), 16/24 600, 24 under the table, copy svg 20x20 |
| S1-53 | Status | PASS | `p.status[role=status]` present, empty, class "status", display none. The golden's is the same |

### S2 `bill-even.html` (28 rows, all PASS)
| Id | Element | Result | Measured |
|---|---|---|---|
| S2-01 | Wordmark | PASS | As S1-01, re-measured on S2 |
| S2-02 | New bill | PASS | As S1-02 (right edge 374 / 1160) |
| S2-03 | People heading | PASS | As S1-03 |
| S2-04 | Person rows 1 to 3 | PASS | As S1-04 to S1-09: three inputs "Aisyah", "Ben", "Chen" and three enabled removes, all equal to the golden |
| S2-05 | Add person | PASS | As S1-10 (175 at x199 y168 / 180 at x120 y188) |
| S2-06 | People grid | PASS | As S1-11 (2 columns / 3, gaps 8) |
| S2-07 | Mode switch | PASS | As S1-12 (halves 178 and 178 / 277 and 277, 44 high) |
| S2-08 | Even label | PASS | Checked: ink fill, on-ink, 15/20 600. Radio `checked` true |
| S2-09 | By item label | PASS | Unchecked: transparent over the field fill, ink. Radio `checked` false |
| S2-10 | Subtotal heading | PASS | `h2#h-subtotal` 18/24 700 holding `label[for=subtotal]`, text "Subtotal" plus hidden " in RM" (reads "Subtotal in RM") |
| S2-11 | Subtotal field | PASS | `span.field.money` 175x44 / 180x44 at the first grid column (x16 / x120). "RM" unit ink-muted, padding-left 8. `input#subtotal` "100.00", right aligned, padding 0 8 0 4, no aria-invalid, no aria-describedby, 0 `p.error` in the DOM |
| S2-12 | Items block | PASS | Not rendered (0 shown, 0 in the golden) |
| S2-13 | Charges block | PASS | As S1-34 to S1-39: fields 175 / 180 wide at x16 and x199 / x120 and x308, "10" and "6", hint 14/20 ink-muted |
| S2-14 | Panel frame | PASS | As S1-40. The S2 page does not scroll at 1280, so sticky is exercised on S1 and S5 instead (O-10). Top 100 equals the People top |
| S2-15 | Summary heading | PASS | As S1-41 |
| S2-16 | Subtotal row | PASS | "RM 100.00" |
| S2-17 | Service row | PASS | "RM 10.00", working "10% of RM 100.00" |
| S2-18 | SST row | PASS | "RM 6.60", working "6% of RM 110.00" |
| S2-19 | Total row | PASS | "RM 116.60" in `span.final` on the 3px double rule, rule above from 28 |
| S2-20 | Shares heading | PASS | As S1-46 (32 under the Bill summary section) |
| S2-21 | Table heads | PASS | `thead.sr-only` (1x1, absolute) holding `th[scope=col]` "Person" and "Share" |
| S2-22 | Row Aisyah | PASS | `th[scope=row]` "Aisyah" 15 600, `td.share` "RM 38.87" 18 700. Two cells only, no Items or Charges cell |
| S2-23 | Row Ben | PASS | "RM 38.87", two cells |
| S2-24 | Row Chen | PASS | "RM 38.86", two cells |
| S2-25 | Check row | PASS | Check svg 18x18 accent (left 0, top 14), "Adds up to" accent, `td.share` "RM 116.60" accent 18/700, 1px ink top border, rule from 28 |
| S2-26 | Copy summary | PASS | As S1-52 (358 / 370 wide, 48 high, 24 under the table) |
| S2-27 | Status | PASS | As S1-53 |
| S2-28 | Subtotal field at 360 x 780 | PASS | `span.field.money` 160x44, one grid cell. scrollWidth 360, innerWidth 360 |

### S3 `bill-empty.html` (14 rows, all PASS)
| Id | Element | Result | Measured |
|---|---|---|---|
| S3-01 | Wordmark, New bill, People heading | PASS | As S1-01 to S1-03, re-measured |
| S3-02 | Person 1 field | PASS | Value "Person 1", aria-label "Person 1 name", maxlength 20, placeholder "Person 1" (allowed difference 2) |
| S3-03 | Person 1 remove | PASS | "Remove Person 1", `disabled`, X svg fill ink-disabled (154, 161, 157), borders kept (1px line-strong, lighter left divider), transparent, cursor not-allowed. Skipped by Tab (IX-11) |
| S3-04 | Person 2 field | PASS | Value "Person 2", aria-label "Person 2 name" |
| S3-05 | Person 2 remove | PASS | "Remove Person 2", disabled as S3-03 |
| S3-06 | Add person | PASS | Enabled, in the third grid cell: second row first column at 390 (x16 y168), first row third column at 1280 (x496 y136), 175 / 180 wide |
| S3-07 | Mode switch | PASS | Even checked (ink fill), By item unchecked, halves 178 / 277 |
| S3-08 | Subtotal heading and field | PASS | As S2-10 and S2-11 but `value` empty, "RM" unit shown, 0 `p.error`, no aria-invalid |
| S3-09 | Charges block | PASS | As S1-34 to S1-39 |
| S3-10 | Panel frame | PASS | As S1-40 (full bleed with the 2px rule at 390, a short card 420 wide at x740 at 1280, top 100 equals the People top) |
| S3-11 | Bill summary | PASS | Not rendered: 0 `#h-summary`, 0 `dl.sum` in the DOM, golden the same |
| S3-12 | Shares heading | PASS | `h2#h-shares` 18/24 700 |
| S3-13 | Result message | PASS | `p.result-msg` "Enter the subtotal to see the shares.", 16/24 400 ink, 8 under the heading, same x as the heading (no indent), 24 high (one line) |
| S3-14 | Table, Copy summary, status | PASS | 0 `table.shares`, 0 `button.copy`, 0 `p.status` in the DOM |

### S5 `bill-unassigned.html` (12 rows, all PASS)
| Id | Element | Result | Measured |
|---|---|---|---|
| S5-01 | Header, People, mode switch | PASS | As S1-01 to S1-14, re-measured on S5 |
| S5-02 | Items 1, 2 and 4 | PASS | As S1-16 to S1-23 and S1-28 to S1-31 (names, prices, removes, toggles Aisyah / Ben / Aisyah and Chen) |
| S5-03 | Item 3 fields and remove | PASS | As S1-24 to S1-26 ("Mee goreng mamak", "12.00", "Remove Mee goreng mamak") |
| S5-04 | Item 3 toggles | PASS | "Who had Mee goreng mamak": Aisyah, Ben and Chen all `aria-pressed` false, field fill, ink, 1px line-strong. 0 `p.error` and 0 `aria-invalid` on the page, no error styling |
| S5-05 | Add item, Charges block | PASS | As S1-33 to S1-39 |
| S5-06 | Bill summary | PASS | As S1-41 to S1-45: "RM 59.40", "RM 5.94" (10% of RM 59.40), "RM 3.92" (6% of RM 65.34), "RM 69.26" |
| S5-07 | Shares heading | PASS | As S1-46 (32 under the Bill summary section) |
| S5-08 | Result message | PASS | "1 item still needs a person. Tap who had it to see the shares.", 16/24 ink, 8 under the heading, no indent, 48 high = two lines at 390 and at 1280 |
| S5-09 | Table, Copy summary, status | PASS | 0 `table.shares`, 0 `button.copy`, 0 `p.status` |
| S5-10 | Items heading | PASS | As S1-15 |
| S5-11 | Item separators | PASS | As S1-32 |
| S5-12 | Panel frame | PASS | 390: full bleed with the 2px rule, ends 24 padding plus 1 rule under the message. 1280: card 420 wide, sticky, top 100 equals the People top, bottom 491.89 against message bottom 466.89 (24 padding plus 1 border). Scrolled 120 px: panel top 24 in app and golden |

### M1 `new-bill-dialog.html` (9 rows, all PASS), app opened by a real mouse click on "New bill"
| Id | Element | Result | Measured |
|---|---|---|---|
| M1-01 | Page behind | PASS | The S2 render under the scrim. `.app` 844 / 800 high = the viewport, overflow hidden, position relative. A mouse wheel leaves `scrollY` at 0. A hit on the header button lands on the dialog (page inert). Golden `.app` same height and overflow, `inert` |
| M1-02 | Scrim | PASS | App `dialog::backdrop` rgba(20, 25, 23, 0.48), fixed, inset 0. Golden `.backdrop` the same colour, fixed, 390x844 / 1280x800 |
| M1-03 | Dialog box | PASS | 358 wide / 400 wide, centre (195, 422) / (640, 400) = the viewport centre, padding 24, surface fill, 1px ink border, radius 6, box-shadow none |
| M1-04 | Title | PASS | `h2.dialog-title#dialog-title` "Start a new bill?", 18/24 700. Dialog aria-labelledby "dialog-title", aria-describedby "dialog-text", `open` and `:modal` true |
| M1-05 | Body | PASS | `p.dialog-text#dialog-text` "This clears the people, items and amounts.", 16/24 ink-muted, 8 under the title |
| M1-06 | Start new bill | PASS | `.btn.btn-primary.btn-large` first, ink fill, 48 high, 16/24 600. Full width 308 of 308 at 390. At 1280 natural width 129.47 in a right aligned row (Cancel right edge 815 = actions right edge) |
| M1-07 | Cancel | PASS | `.btn.btn-outline.btn-large` second, field fill, 1px line-strong, 48 high. Focused on open, `:focus-visible` false, outline style none |
| M1-08 | Actions | PASS | 390: column, Start above Cancel, 8 apart. 1280: row, 8 apart. 24 under the body |
| M1-09 | Dialog at 360 x 780 | PASS | 328 wide, centre (180, 390), `p.dialog-text` 48 high (two lines), scrollWidth 360, innerWidth 360 with the dialog open |

### States sheet `states.html` (15 rows, all PASS)
Each state is reached on the app with real gestures (clicks, typing, Tab, Remove, a mouse click on Copy summary under the clipboard recorder or the reject script) and compared with the specimen's own element on 471 computed properties. Values 390 / 1280, one value where equal.
| Id | State | Result | Measured |
|---|---|---|---|
| ST-01 | S4 subtotal error | PASS | "0" typed: no `p.error` while typing, after Tab `input#subtotal` `aria-invalid` true, `aria-describedby` "subtotal-error". `p.error#subtotal-error` "Enter an amount like 12.50" right after `div.cells`, margin-top 8, left aligned. Paragraph and `span.field.money` (border rgb(180, 35, 24), box-shadow rgb(180, 35, 24) 0 0 0 1px inset) equal to `#s4-subtotal-error` and its field |
| ST-02 | S4 price error | PASS | "13.505" in Item 2 and Tab: `p.error#price-error-i5` last child of `div.item-line`, text-align right, margin-top 0, grid-column 1 / 3. Price input `aria-invalid` true, `aria-describedby` "price-error-i5". Paragraph and price field equal to `#s4-price-error` and the specimen's price field. Toggles keep 8px gap (app [8, 8px, 8px], specimen the same) |
| ST-03 | S4 error with focus | PASS | Clicked back into the error field: border stays error red with the inset shadow, outline 2px solid ink offset 2px. Equal to the specimen's field focused the same way |
| ST-04 | S6 copy success | PASS | "Summary copied", class "status", role status, 14/20 600 ink, centred, 8 under Copy summary. Equal to the S6 success specimen. The recorder logged 1 write |
| ST-05 | S6 copy failure | PASS | "Could not copy. Your browser blocked the clipboard.", class "status status-failure", error red (180, 35, 24), 14/20 600, centred, 8 under the button. Equal to the S6 failure specimen |
| ST-06 | S7 note | PASS | `div.note-wrap > div.note[role=status]` between `header.bar` and `main.layout`. Text "Your saved bill could not be read, so a new one was started.". Dismiss button aria-label "Dismiss note", 44x44, X path data equal to the specimen's (184 characters). `div.note`, its `p`, the button and the X svg equal to the specimen's. Wordmark `h1` equals the specimen's `p.wordmark` (allowed difference 6) |
| ST-07 | S7 screen under the note | PASS | Person 1 and Person 2 (aria-labels "Person 1 name", "Person 2 name"), both removes disabled, Even checked, "10" and "6", empty subtotal, message "Enter the subtotal to see the shares.". Disabled remove equals the S7 frame's |
| ST-08 | S8 12 people | PASS | Add person `disabled`, transparent fill, border line (201, 206, 203), text and plus ink-disabled (154, 161, 157), cursor not-allowed, equal to the S8 specimen button (not its width). 6 rows of 2 at 390 and Add person in the next cell (top 428 after the last row top 376). At 1280, 4 rows of 3 and Add person in the next cell |
| ST-09 | S8 2 people | PASS | After a real click on "Remove Chen": both removes `disabled`, X ink-disabled, cursor not-allowed, borders kept (line-strong, left divider line), each equal to the S8 2-people specimen's, X svgs equal |
| ST-10 | Rate errors | PASS | "31" in Service charge: `p.error#rate-service-error` "Enter a rate from 0 to 30", last child of its cell, input `aria-invalid` true, `aria-describedby` "rate-service-error charges-hint". "20.01" in SST: "Enter a rate from 0 to 20", id "rate-sst-error". Both paragraphs equal `#s4-subtotal-error`, both fields have the error border and inset shadow |
| ST-11 | Other panel messages | PASS | "Check the charges to see the shares.", "Add an item to see the shares.", "Give every item a price to see the shares.", each `p.result-msg` equal to S3's |
| ST-12 | Plural S5 message | PASS | "2 items still need a person. Tap who had each one to see the shares.", equal to S5's `p.result-msg`, two lines (48 high, as the singular) |
| ST-13 | Add item at 50 | PASS | 50 item rows, Add item `disabled`, cursor not-allowed, natural width 122.78, equal to the S8 specimen button (not its width), plus svg equal |
| ST-14 | S6 copy failure at 360 x 780 | PASS | `p.status` 328x40, two centred lines, class "status status-failure", scrollWidth 360 <= innerWidth 360, equal to the specimen (also 40 high at 360) |
| ST-15 | S7 note at 1280 x 800 | PASS | `div.note` 1040 wide, `header.bar` content 1040, `.note-wrap` content 1040 |

### Finder rows, not in qa.md (26 rows, all PASS)
The checklist has no rows for hover, focus, pressed and disabled, for the other widths, or for the stylesheet itself. These rows come from `system.md` (component inventory, focus ring, motion, layout) and the screen notes. IX rows (`interactions.py`) make the same gesture on the golden and the app with a real mouse or key press and compare the **whole page** (every element, every property) after each one.
| Id | What | Result | Measured |
|---|---|---|---|
| IX-01 | Hover on outline buttons (New bill, Add person, Add item) | PASS | Fill hover (227, 231, 228), text ink. Whole page equal to the golden under the same hover (174 elements, 0 differences), 390 and 1280 |
| IX-02 | Hover on Copy summary | PASS | Fill ink-hover (42, 48, 45), text on-ink, whole page equal |
| IX-03 | Hover on icon buttons (person remove, item remove) | PASS | Fill hover, the X turns ink (20, 25, 23), whole page equal |
| IX-04 | Hover on toggles | PASS | Off toggle fill hover. On toggle keeps ink fill and on-ink text. Whole page equal |
| IX-05 | Hover on mode labels | PASS | Unchecked label fill hover. Checked label keeps ink fill. Whole page equal |
| IX-06 | Hover on disabled removes (S3) | PASS | Fill stays transparent, X stays ink-disabled, whole page equal (57 elements) |
| IX-07 | Pressed: New bill, Add person, Copy summary, person remove, toggle | PASS | `transform` matrix(1, 0, 0, 1, 0, 1), a 1px drop. Whole page equal under the same press. Releasing away from the control left the stored draft unchanged |
| IX-08 | Pressed on a disabled remove | PASS | `transform` none, no shift, whole page equal |
| IX-09 | Tab walk on S1 | PASS | 37 stops, whole page equal after every stop. Order: New bill, each person name then remove, Add person, the checked mode radio, each item name, price, remove and three toggles, Add item, Service charge, SST, Copy summary. Rings correct at every stop: 2px solid ink offset 2px, on the field wrapper for inputs, offset -3px inset on person removes, outer ring plus the 3px field and 2px ink double ring on the mode switch |
| IX-10 | Tab walk on S2 | PASS | 13 stops, equal. Subtotal then Service charge, SST, Copy summary after the Even radio |
| IX-11 | Tab walk on S3 | PASS | 8 stops, the two disabled removes are skipped, equal |
| IX-12 | Placeholder | PASS | Blank "Person 2": placeholder "Person 2" in ink-muted (74, 82, 78) at opacity 1, remove named "Remove Person 2" |
| IX-13 | Motion | PASS | no-preference: `transition-duration` 0.12s, 0.12s on `.btn`, Copy summary, `.icon-btn`, `.tap` and the mode label (background-color, color). reduce: 0s. Equal to the golden |
| IX-14 | Colour scheme dark | PASS | Body stays (238, 240, 238), one light theme, whole page equal to the golden |
| IX-15 | Dialog focus by keyboard | PASS | Enter on New bill: Cancel focused, `:focus-visible` true, outline 2px solid ink offset 2px. Tab: Start new bill focused with the same ring |
| IX-16 | Dialog hover | PASS | Start new bill fill ink-hover with border ink-hover, Cancel fill hover. The golden gives the same fills |
| LY-01 | Horizontal overflow | PASS | 0 of 35 captures overflow (5 screens at 360, 390, 599, 600, 1023, 1024, 1280). The accepted H-02 case (by-item table above about RM 650 at 360) is not reached by these bills |
| LY-02 | Layout numbers at seven widths | PASS | 35 of 35 measurement sets equal the golden's. People columns 2, 2, 3, 3, 3, 3, 3. Panel full bleed with the 2px rule under 600 (599 wide at 599), a 528 wide bordered card at 600 and 1023 (x36 and x247.5), the right column 420 wide sticky at 1024 and up (x572 and x740) with its top at the People top. S2 subtotal field 160, 175, 183.66, 170.66, 170.66, 153.33, 180. Item price field 96 under 600 and 120 from 600. Dialog 328 at 360, 358 at 390 and 400 from 432 up, stacked under 600 and a row from 600 |
| LY-03 | Whole-page comparison at seven widths | PASS | 35 of 35 pairs, S1, S2, S3, S5: 0 differences (table above). M1: only native modal properties |
| LY-04 | Extra pixel runs at 360x780, 600x900, 1024x768 | PASS | 15 of 15 harness runs at 0 mismatching pixels, dimensions equal. 12 byte-identical. The 3 M1 pairs differ by at most 2 of 255 on 127, 101 and 113 pixels |
| DC-01 | Stylesheet | PASS | `src/system.css` is `docs/design/system.css` followed by exactly `\n[hidden] { display: none !important; }\n` (18,142 against 18,102 bytes). The first `<style>` block of all six goldens equals `system.css` exactly. `index.html` has no inline style, style attribute or inline script |
| DC-02 | Document | PASS | Title "Split", `lang` "en", standards mode, viewport meta, charset equal in 10 captures. `html` and `body` computed style equal on every property, `:root` custom properties equal |
| DC-03 | Icons | PASS | 10 of 10 captures give the same `svg.ph` count, attributes and path data. The four distinct paths (X, plus, copy, check) are the goldens' |
| DC-04 | Gate setup scripts | PASS | `seed-s1.js`, `seed-s2.js`, `seed-s5.js` are one statement each, set only `split.draft`, and store exactly the seeds written in qa.md and `seeds.py`. `open-new-bill.js` clicks "New bill", waits two frames, blurs, waits two frames |
| DC-05 | S7 note geometry at five widths | PASS | 16 under the header, button top-right (1px inset), text on two lines at 360 and 390 (note 66 high) and on one line from 600 (46 high), text centred, note width equals the note-wrap content width (328, 358, 528, 960, 1040) |
| DC-06 | Product source | PASS | `src/` has no `.style`, `classList`, `cssText`, `insertRule` or inline style. Every class the code writes is a class of `system.css`, and the class lists equal the goldens' (the whole-page comparison finds no class difference) |

## Findings
None. No addition, subtraction or modification of the design was found. Every PASS above is the app equal to the golden, or to the specimen, on the full set of computed properties, not on a sample.

Candidates I considered and did not raise. The native modal's UA rules (O-03), the backdrop-click ruling (O-01), the loose wording of qa.md S1-51 (O-06), and the stale harness version in qa.md (O-07). Each is ruled, specified or a documentation matter, and none changes what the user sees against the golden.

## Observations
- **O-01 A recorded ruling differs from one sentence of a golden note.** `docs/design/new-bill-dialog.md` says "A click on the backdrop does nothing (native modal behaviour)". The app closes the dialog as Cancel on a backdrop click (R30). That is the orchestrator's ruling CG-8 in `docs/modules/ROADMAP.md`, which names the golden sentence and says it overrides it, citing `docs/design-explore/FLOW-CHECK.md` where a click at (10, 10) on the backdrop expects the S2 screen. The golden HTML cannot show behaviour, so no pixel or style is affected. I did not count it. If you want a strict reading, it is one low finding, "modification of a golden note, ruled", and the fix is either an edit of the golden note (which is immutable) or removing the backdrop handler.
- **O-02 The M1 pairs differ at a level below the threshold, and the app is not the cause.** At any level 141 pixels (390) and 103 pixels (1280) differ from the golden, at most 2 of 255 on a channel. All 244 sit on rounded corners, within 7 px of a corner of an element with a border-radius (`m1_pixel_locations.json`). At 390, 46 are on the dialog box's own corners and 95 on the corners of buttons. At 1280, 79 are on the corners of buttons (the dialog's two and those behind the scrim), 9 on money fields, 6 on person fields, 6 on the mode switch and 3 on the panel. qa.md attributes them to glyph edges, and the data says corners. The counts are byte-stable, the same candidate and golden hashes in all six gate runs. The cause is the engine's anti-aliasing of rounded borders drawn in the top layer against in flow. The control: the golden turned into a native modal in memory differs from the static golden by 95 and 54 pixels in my captures, and from the app opened by a real mouse click by **0 pixels at 360, 390 and 600** and 27 pixels of 1 level at 1024 and 1280 (`m1_native.json`). Under the harness's own conditions the same control leaves 46 and 49 pixels (`m1_native_harness.json`), and a probe (`m1_native_probe.json`) shows the harness's freeze stylesheet is what adds them at 390 (0 without it, and the 46 are the dialog's own corners). The qa.md budget (largest delta 0.0068 against 0.01 allowed) holds.
- **O-03 Native modal against the golden's static dialog.** The M1 differences are `interactivity` (the golden's `inert` page against the modal-made inertness, 107 elements and `.total::before`), and on `dialog.dialog` the UA modal rules `overflow` auto, `max-height` calc(100% - 38px), `overlay` auto and `user-select` text, plus the golden's stand-in `div.backdrop`. None changes a pixel at any viewport the spec names. `max-height` would clip or scroll the dialog only below a viewport height of about 272 px (the dialog is 234 high at 390), which is no specified size.
- **O-04 What the harness gate cannot see.** It forces `reduced_motion=reduce`, bypasses the CSP, uses two viewports and photographs no hover, focus, pressed, disabled or error state. My measurements ran with the shipped CSP live and the scripts that record the console logged nothing, so the policy does not change what is drawn here. The extra runs at 360, 600 and 1024 stay at 0. The motion, hover, focus and pressed rows are in IX-01 to IX-16.
- **O-05 The pixel rule has a floor.** The harness counts a pixel only above 0.01 of the maximum RGB distance, about 4.4 levels. Negative controls (`controls.py`): of 13 one-thing mutants, 5 are one-colour-level changes (a border colour, an icon fill, a separator, `--ink`, `--line-strong`) and the harness rule reports 0 pixels for every one of them, while the any-level count reports 253, 38, 358, 47,495 and 8,267. My rows and the whole-page comparison caught all 13, and the unmutated control gave 0 failing rows, 0 differences and 0 pixels. That is why 8 of 10 pairs being byte-identical matters here: it rules out a hidden one-level drift in the gate's own result.
- **O-06 qa.md S1-51 reads looser than the golden.** It lists "RM 59.40, RM 9.86, RM 69.26 accent 18 px 700". In the golden only the share cell (`td.share`) is accent 18/700. The Items and Charges cells of the check row are 14/400 ink-muted, as `bill-items.md` says ("label and final share in accent"). The app equals the golden. The wording is the thing to tidy.
- **O-07 qa.md names harness 2.1.2.** The Fidelity gate section says "sdlc 2.1.2". The installed harness is 2.1.3 (`.claude-plugin/plugin.json`). The 0-pixel baseline measured on 2.1.1 holds on 2.1.3, which is the confirmation qa.md asks for on a later harness. Owner's edit, not mine. My agent definition names a cached 1.0.0 harness, and I used the project's 2.1.3 one, as the task and `run.py` say.
- **O-08 The harness's `text` field is a window.** It is textContent cut at 80 characters, so white space between elements in the goldens (allowed difference 5) and the text of the app's `hidden` mode block (allowed difference 7) move the cut. 78 container text differences across the ten pairs are of that kind (30 on the three containers that hold the hidden block, 48 window shifts), none on a leaf (`styles_json_diff_gate.json`).
- **O-09 The `[hidden]` rule changes nothing visible.** The one rule the app adds (accepted, RD-1) only affects the other mode's block, which no golden contains. In S1 and S5 the Subtotal block is display none (no client rects), in S2 and S3 the Items block is. The whole-page comparison finds no rendered element it changes.
- **O-10 The sticky panel is exercised where the page scrolls.** At 1280 the S1 and S5 pages scroll (329 px), so the scroll test there shows the panel stuck at 24 in both the app and the golden. S2 and S3 fit the viewport and cannot scroll, so only the resting position (top 100, equal to the People top) is measured for them.
- **O-11 Method note on the specimen rows.** The specimen frames set `--gutter` and `--price-width` on purpose and sit inside `ul.cells` or not, so custom properties and the inherited `list-style` were left out of the specimen comparison. Everything else Chromium lists was compared. Nothing else was excluded.
- **O-12 Process slips of mine.** See Processes. None touched the product and none affects the evidence.

## Evidence
All under `{workspace}/examples/split/docs/modules/split-app/qa/`.
- Gate run, ten pairs: `fidelity/20261010-133017/<screen>-<viewport>/` (each `golden.png`, `candidate.png`, `diff.png`, `styles.json`, `report.json`) and `fidelity/20261010-133017/run.log`.
- Checklist and honesty evidence: `fidelity-checklist/20261010-133500/`. `evidence.md` is the index. It holds `exact_diff_gate.json` (any-level pixel counts and hashes), `styles_json_diff_gate.json`, `m1_pixel_locations.json`, `m1_native.json`, `m1_native_harness.json` with `m1_native_harness/`, `m1_native_probe.json`, `extra-360x780/`, `extra-600x900/`, `extra-1024x768/` with `extra_pixel.json`, `dom_diff_all.json` (the whole-page comparison), `rows_screens.json`, `rows_states.json`, `interactions.json`, `static_checks.json`, `misc_checks.json`, `controls.json`, `checklist_full.md`, `checklist_short.md`, `checklist_table.md`, and the Python scripts that produced them.

## Processes
- Started: 23 servers, each `python -m http.server <free port> --bind 127.0.0.1` from the project root. One by the project's runner `run.py` (pid 13580, port 61288), one by pytest's conftest for the 14 R40 tests (pid 6788, port 21481), and 21 by my scripts through `tests/browser/rig.py` (for example pid 11704 port 2482, pid 17452 port 37377, pid 22184 port 26901, pid 14640 port 27084, pid 13528 port 61288). Every one was stopped by PID in a `finally` block and printed "exited True, port free again True", and the three that ended in a traceback of mine were stopped by the same block. A listing at the end shows no listener on any of those ports.
- Not touched: the `python -m http.server` on port 8731 (pid 12828) serving the sibling Streaks project is still listening, as it was.
- Browsers: every script launched its own headless Chromium 149 through Playwright and closed it. A process listing after the last run shows no chrome or chromium process and no python process other than pid 12828. Nothing was started with a visible window. The operating system clipboard was never touched: every app context carried the recorder or the reject script, and no clipboard permission was granted.
- Written outside the evidence folders: only this findings file. The gate run folder `fidelity/20261010-133017/` was written by `run.py`, as the task says. Two scratch debugging scripts sit in the session scratchpad directory, outside the project. `__pycache__` was never written (`PYTHONDONTWRITEBYTECODE=1`, checked with a search of the project).
- Rule slips of mine, stated plainly. I fixed one constant of my own scratch file `common.py` once with a Python heredoc instead of the Write tool, and I used Python heredocs (stdin, not redirected into a file) for a dozen read-only inspections of my own JSON output. All other files were created with the Write tool. I never ran `sed -i`, `tee` or shell redirection into a file.
- Untouched, checked with `git status --short` (only `docs/modules/split-app/qa/fidelity/20261010-133017/` and `docs/modules/split-app/qa/fidelity-checklist/` are new, plus this file): `src/`, `tests/`, `index.html`, `docs/design/`, `spec.md`, `qa.md`, `BUILD.md`, every existing finding. Nothing was committed.
