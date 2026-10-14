# A0 WebKit baseline, the sorting record

Written 2026-10-14 by the frontend developer role (task A0, R58, R59), on the tree of A0 with `src/` unchanged since `853afe1`.

**Status. NOT COMPLETE.** The WebKit run of the suite has 48 failed tests. 5 are sorted below. 43 cannot be sorted on this machine and wait for a ruling (blocker B-A0-1). The WebKit run of the 1.0 live gate fails at step 7 for a reason in the test tool, which also needs a ruling (Q-A0-3).

**Status, corrected 2026-10-14 after the rulings. COMPLETE.** All 48 are sorted. The 43 are class (a), fixed at task A17 (H-04). The 5 class (b) wait for spec lines. The live gate question is decided for A20 (H-05). See "Rulings, 2026-10-14" at the end. The status line above is kept as written.

## The runs behind this record
Every folder below was listed on disk after its run.

| Run | Folder | Result |
|---|---|---|
| Chromium suite, same tree | `docs/modules/split-app/qa/functional/20261014-125352-chromium/` | 430 passed, 0 failed, 0 skipped. The 427 sealed 1.0 cases all pass (every test function of the `v1.0.0` `test_app.py` ran), and the 3 A0 cases are counted apart (`test_R58_the_engine_option_and_the_one_launch_place`, `test_R58_only_the_rig_launches_a_browser`, `test_R58_the_rig_launches_headless_with_the_arguments_of_its_engine`). The `chromium_only` IME test ran and passed |
| WebKit suite, same tree | `docs/modules/split-app/qa/functional/20261014-125604-webkit/` | 381 passed, 48 failed, 1 skipped, 430 in all, 239 s. `skips.txt` lists the one skip (the R33 IME test, reason "Needs a CDP session ...") with count 1, equal to `junit.xml`'s `skipped="1"`. 50 failure screenshots |
| Live gate 1.0, Chromium | `docs/modules/split-app/qa/live-e2e/20261014-130326-chromium/` | PASS, 7 of 7 steps, `summary.json` engine `chromium`, browser 149.0.7827.55 |
| Live gate 1.0, WebKit | `docs/modules/split-app/qa/live-e2e/20261014-130333-webkit/` | FAIL at step 7, steps 1 to 6 PASS, `summary.json` engine `webkit`, browser 26.5 (Q-A0-3) |
| R59 probes | `probes.json` in this folder, by `python tests/browser/probe_webkit.py --engine webkit` | All probes ran. Launched by `rig.launch`, every context by `rig.new_context`, the stand-in checked before each gesture |
| Sorting diagnostics | `diagnostics/sorting_diagnostics.json` in this folder, by the script beside it | Three measurements in both engines, cited below |

The qa scenario "The A0 baseline record is complete" asks this folder to hold the WebKit run's `pytest.txt`, `junit.xml` and `skips.txt`. They sit in the WebKit run's own folder above, which R58 names `<stamp>-webkit`. A copy here needs a shell copy or a 150 KB hand copy, neither of which this lane may make (Q-A0-2).

## Probe results (R59), WebKit 26.5 on this machine
| Probe | Measured |
|---|---|
| Click count of a quick touch double tap | `detail` 1 on both clicks (`quick_double_tap_click_details` [1, 1]) |
| Order of one tap's events | pointerdown, touchstart, pointerup, touchend, mousedown, mouseup, click. The pointer events come before the mouse events, as `src/ui/field-leave.js` assumes |
| `isSecureContext` and `typeof Clipboard` on `http://127.0.0.1` | true and "function". `navigator.clipboard` is an object, so `recorder.js` takes the same path as in Chromium (it replaces `Clipboard.prototype.writeText`) |
| An init script redefines `window.localStorage` | Yes. With the driver the getter throws `SecurityError`, without it the read works. The D-b scenarios can run in both engines |
| Console text of a CSP violation | type error, "Refused to execute a script because its hash, its nonce, or 'unsafe-inline' does not appear in the script-src directive of the Content Security Policy." The `securitypolicyviolation` event fired with `script-src-elem` and `inline` |
| Console text of a denied `localStorage` | None. An init script that calls `localStorage.setItem` gives no console message and no page error in WebKit, and the key lands on the served page |
| Focus after a mouse click on the label of a radio | `body` (the radio becomes checked) |
| Focus after a mouse click on a visible radio | `body` (the radio becomes checked) |
| `Content-Type` of `/docs/brand/mark.svg` from the test server | `image/svg+xml` |

The label and radio results are what R59 already states for WebKit, so nothing changes there.

## Sorted (5 tests)
| Test | Class | Measurement | What follows |
|---|---|---|---|
| `test_R29_the_dialog_opens_with_the_safe_choice_focused` | (b) engine difference | With the dialog open at 390 x 844 the `.app` box (`height: 100dvh`) is 843.984375 px high in WebKit and 844 in Chromium. The test asserts exactly 844 | A test change in the task that next touches R29. It compares within 0.5 px, the qa.md rule for measured numbers, which holds in both engines, so the scenario can stay `@both` |
| `test_R30_leaving_the_dialog_without_starting_over[escape]` and `test_R30_after_a_double_click_on_new_bill_one_deliberate_click_still_closes_it[escape]` | (b) engine difference | Read right after `keyboard.press("Escape")` and polled 60 times, WebKit goes open with focus on Cancel, then closed with focus on `body`, then closed with focus on New bill (the app's `close` listener). Chromium is already closed with focus on New bill when the press returns (`diagnostics/sorting_diagnostics.json`, `escape_transitions`). WebKit runs the Escape close after keyup in a later task, and the tests read focus in between. The end state is R30's in both engines | A test change. The two tests wait, bounded, for the `close` event before reading focus, and assert the same end state in both engines |
| `test_R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on[service-touch]` and `[sst-touch]` | (b) engine difference | A touch tap on the charges hint (text, not a control) in WebKit sends pointerdown, touchstart, pointerup and touchend only. There is no mouse event and no click, focus stays in the rate field, so it never blurs and no error shows. Chromium sends the mouse events and a click on the hint, the field blurs and the error shows (`diagnostics/sorting_diagnostics.json`, `tap_on_hint`). The app has nothing to fix, since R10 shows the error when the field is left and here it is not left | A spec line in R59 with this measurement, and the scenario's touch rows on the hint become `@per_engine` (In WebKit no click reaches the page and the field keeps focus). The spec and qa.md text are the planner's or orchestrator's to write. Whether an iPhone does the same is for UAT |

## Not sorted, blocker B-A0-1 (43 tests). Sorted 2026-10-14 as class (a), see Rulings
Every one is a touch double activation (two `page.touchscreen.tap` calls at one point).

| Test | Cases |
|---|---|
| `test_R6_a_repeat_press_on_add_person_adds_one_person_and_keeps_it` | 12, `touch-double-right-edge` at 2 to 5 people, 360x640, 390x844, 1280x800 |
| `test_R12_a_repeat_press_on_add_item_adds_one_item_and_never_reaches_the_page` | 12, `touch-double-centre` and `-right-edge` at 1 and 4 items, three widths |
| `test_R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing` | 6, S2 person 3 of 3 and S8 person 12 of 12, three widths |
| `test_R29_a_repeat_press_on_new_bill_leaves_the_dialog_open` | 3, `touch-double`, three widths |
| `test_R30_a_double_click_or_double_tap_on_cancel_changes_nothing` | 3, `touch` at 360x640, 375x667, 412x732 |
| `test_R30_the_second_click_of_a_double_activation_never_reaches_the_page` | 3, `touch` on Cancel, Start new bill and the backdrop |
| `test_R7_a_double_click_or_double_tap_on_remove_removes_one_row` | 2, `touch`, item 2 of 4 and person 2 of 5 |
| `test_R7_a_repeat_press_on_a_chip_under_a_pending_price_error_never_removes_the_item` | 2, `touch-double` at 375 and 390 |

**Measurement.** In WebKit each click of a quick double tap has `detail` 1 (`probes.json`, `taps`). The app treats a press as a repeat only when `event.detail > 1` (`isRepeatClick` and `swallowRepeatClicks` in `src/ui/dom.js`, no timer by design), so in WebKit the second tap is never a repeat and acts on whatever is under it. Every mouse double click and triple click case passes in WebKit (120 of 120 mouse cases in `pytest.txt`), and 25 touch cases pass where the second tap lands on something harmless.

**Why it cannot be sorted here.** If Safari on an iPhone also gives each tap of a double tap `detail` 1, the guard does not protect iPhone users. That is (a), an app defect Safari would show, and the fix is a new repeat rule, a product and spec decision since the spec says "No timer". If it is how Playwright synthesises taps on the Windows port, it is a tool artefact, and the touch rows need `@per_engine` or a WebKit skip with that reason. Research `webkit-testing.md` section 6 says only an iPhone can tell, and ROADMAP orchestrator action 4 already plans a double tap on Remove and on Cancel on the owner's iPhone. A lead, UNVERIFIED and not checked against any source in this task, is that iOS WebKit's synthetic click path may build its mouse events with a click count of 1.

## Open questions for the orchestrator
- **B-A0-1.** The class of the 43 touch double activation failures, above. A0 cannot close until it is ruled.
- **Q-A0-2.** Whether this folder must hold copies of the WebKit run's `pytest.txt`, `junit.xml` and `skips.txt`, or may name the run's own folder as it does now.
- **Q-A0-3.** The 1.0 live gate in WebKit fails only at step 7, on 7 console errors "Refused to apply a stylesheet because its hash, its nonce, or 'unsafe-inline' does not appear in the style-src directive of the Content Security Policy.", one per step screenshot. The app logs none. 0 messages before the first screenshot, 2 after two screenshots, in WebKit with both `caret="hide"` and `caret="initial"`, and 0 in Chromium (`diagnostics/sorting_diagnostics.json`, `screenshot_console`). Playwright's WebKit screenshot puts a stylesheet into the page that the shipped policy refuses. It is a tool difference, not an app defect. None of (a), (b) or (c) fits it exactly. The gate script is A20's to rewrite, so the ruling (for example, how the WebKit gate's step 9 treats exactly this text while it still counts `securitypolicyviolation` events through `csp/listener.js`) belongs there.

## Rulings, 2026-10-14 (added after the record above, which stays as written)
Relayed to the frontend developer role by the orchestrator.

| Item | Tag | Ruling | What follows here |
|---|---|---|---|
| B-A0-1, the 43 touch double activation failures | USER (H-04, "Fix it in v1.1.0") | Class (a), an app defect. `isRepeatClick` reads only `event.detail > 1` and WebKit gives each tap `detail` 1 | The planner writes a tap-safe repeat rule into the spec for the owner's ruling, and task A17 builds it. No fix in A0. The 43 stay failing in WebKit until A17 and are the known failures of this baseline |
| Q-A0-3, the WebKit live gate's screenshot CSP errors | ORCH (H-05, the owner had no preference) | The planner looks for a capture that adds no stylesheet. Only if none exists, an exact-line WebKit allowance | Decided for A20. The gate is not changed in A0 |
| The 5 class (b) failures (R29 height, two R30 Escape, two R10 taps on the charges hint) | ORCH | They wait for spec lines from the planner | Left as recorded above |
| Q-A0-2, copies of the WebKit run's files in this folder | ORCH | This record names the WebKit run's own folder, no copy | Nothing to add |
| The fixtures written with the Write tool, not a one-off Python run | ORCH | Accepted, the same blob id proof holds | Nothing to add |

The A0 WebKit baseline is therefore 381 passed, 48 failed (43 class (a) for A17, 5 class (b) waiting for spec lines), 1 skipped. Later tasks compare their WebKit runs against these 48.
