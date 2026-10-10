# Evidence index, split-app fidelity checklist

Written by the fidelity finder on 2026-10-10 against `4a3c5bf`. Read-only on the product: every script opens the app and the goldens, none writes under
`src/`, `tests/`, `index.html` or `docs/design/`. Findings are in `docs/modules/split-app/findings/fidelity.md`. The gate run that `run.py` wrote is
`docs/modules/split-app/qa/fidelity/20261010-133017/` (ten pairs, each with `golden.png`, `candidate.png`, `diff.png`, `styles.json`, `report.json`, and `run.log`).

How the scripts are run, from this folder, with `PYTHONDONTWRITEBYTECODE=1`: `python <script>.py`. Each one that needs the app starts its own
`python -m http.server <free port> --bind 127.0.0.1` through `tests/browser/rig.py` (the project's own server rig), kills it by PID in a `finally` block
and prints "port free again True". Every context that opens the app is made with `rig.new_context`, so it carries the clipboard recorder (or the reject script)
and none sets `bypass_csp` (the two scripts that reproduce the harness's rendering set it on purpose, and say so): the shipped CSP is live in the measurements,
and no run touched the operating system clipboard. Golden pages are plain contexts on `file://` URLs, the goldens carry no CSP and are never written.

| File | What it does | Output |
|---|---|---|
| `common.py`, `rows_lib.py` | Shared helpers. `rows_lib` holds the row framework (golden equality plus literal expectations) | none |
| `exact_diff.py` | Pixels that differ at ANY level (not only above the harness threshold 0.01) for each pair of a gate run | `exact_diff_gate.json` |
| `styles_json_diff.py` | The harness's own `styles.json`, golden side against candidate side, per pair | `styles_json_diff_gate.json` |
| `m1_pixel_locations.py` | Where the differing pixels of the two M1 gate pairs are (every one is on a rounded corner) | `m1_pixel_locations.json` |
| `m1_native.py` | What those few pixels are, with my own screenshots: the golden turned into a native modal in memory against the app opened by a real mouse click | `m1_native.json` |
| `m1_native_harness.py` | The same control rendered by the harness's own `render()` function (unmodified `fidelity.py`) against the gate's `candidate.png` | `m1_native_harness.json`, `m1_native_harness/` |
| `m1_native_probe.py` | Switches the harness's rendering ingredients on one at a time to find which one leaves the residual (its freeze stylesheet) | `m1_native_probe.json` |
| `extra_pixel.py` | The same harness, flags and setup scripts at 360x780, 600x900 and 1024x768 (the gate runs only 390 and 1280) | `extra-360x780/`, `extra-600x900/`, `extra-1024x768/` (five pairs each), `extra_pixel.json` |
| `dom_diff.py` | Whole-page comparison, golden against app, for 5 screens at 360, 390, 599, 600, 1023, 1024, 1280: every rendered element, attribute, own text, input value, rectangle, every computed property (544 per element: Chromium's longhands, the shorthands it does not list, and the custom properties), `::before` and `::after` | `dom_diff_all.json` |
| `rows_screens.py` | Checklist rows S1, S2, S3, S5, M1 (116 rows) at 390x844 and 1280x800, with S2-28 and M1-09 at 360x780 | `rows_screens.json` |
| `rows_states.py` | Checklist rows ST-01 to ST-15, states reached on the app with real gestures and compared with `states.html` | `rows_states.json` |
| `interactions.py` | Hover, pressed, disabled, Tab order and focus rings, placeholder, motion, colour scheme, dialog focus: the same gesture on golden and app, whole page compared after each (16 finder rows IX-01 to IX-16) | `interactions.json` |
| `static_checks.py` | CSS bytes, document properties, `html` and `body` computed style, `:root` custom properties, icons, layout numbers at seven widths | `static_checks.json` |
| `misc_checks.py` | The gate's state scripts against the seeds written in qa.md, and the S7 note geometry at five widths | `misc_checks.json` |
| `controls.py` | Negative controls: 13 one-thing mutants of the running page, judged by the rows, the whole-page comparison and the pixel rule | `controls.json` |
| `build_tables.py`, `build_short.py` | Turn the row JSON into tables | `checklist_table.md`, `checklist_short.md`, `checklist_full.md` (every measured string of every row, 1,065 entries) |

Reading the row files. Each row id maps to one entry list per viewport (`"390"`, `"1280"`, or `"360"`), each entry is `[passed, text]`. A row passes only when every entry passes.
Every element entry ends with "= golden" (the app's element equals the golden's on rectangle, text, attributes less the allowed differences, and all computed
properties) and shows the literal values taken from qa.md and system.css. `checklist_full.md` has them all. The finder rows LY-01 to LY-04 and DC-01 to DC-06 of the report come from
`dom_diff_all.json`, `extra_pixel.json`, `static_checks.json`, `misc_checks.json` and a search of `src/`, and are not in the row files.

Notes on method that a reader needs.
- Allowed differences of spec.md were applied exactly: `value` and `checked` attributes (compared as properties), `placeholder` on name inputs, the golden's `inert` on `.app` and its `.backdrop`, and display none elements (the other mode's hidden block). 497 attribute differences were classed allowed in `dom_diff_all.json`, none other exists.
- In `rows_states.py` "equal to the specimen" ignores box-size properties, custom properties (`--gutter` and `--price-width` are set by the specimen frame on purpose) and `list-style` (inherited from whichever `ul.cells` an element sits in, drawn only on a list item). Everything else Chromium lists is compared.
- Playwright's screenshot leaves an empty `style=""` on the inputs of the page it photographs. `controls.py` therefore photographs a separate golden page. No script measures a page it has photographed.
- The harness's freeze stylesheet cannot be added to the app under its CSP (`style-src 'self'`), which is why the harness bypasses the policy. `m1_native_probe.py` bypasses it only for the variants that need the freeze stylesheet.
- Two scratch debugging scripts were written in the session scratchpad, outside the project, and are not evidence.

Result in one line. 131 of 131 checklist rows pass, 26 of 26 finder rows pass, 10 of 10 harness pairs at 0 mismatching pixels, 8 of those 10 byte-identical to the golden screenshot and the other 2 within 2 of 255 on 141 and 103 pixels (all on rounded corners), 15 of 15 extra harness runs at 0, 35 of 35 whole-page comparisons clean apart from native-modal properties, 13 of 13 mutants caught.
