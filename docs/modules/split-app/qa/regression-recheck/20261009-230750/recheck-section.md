## Re-check (2026-10-09)

**FAIL. 1 BLOCKER, 0 WARNING, 0 INFO.** RG-CR-01, RG-CR-02, RG-CR-04 and the README hold as fixed. The hunt for a second unarmed path
found one: a double press on a "who had it" chip under a pending price error removes the item (RG-CR-08), the same regression class
as RG-CR-01, so RG-CR-01's fix does not close the class.

Role: code-review finder, scoped re-check (read-only). Start HEAD `a6cbbf8`. Scope as ordered: RG-CR-01 as fixed (`e30b015`) and a hunt
for the fix's own defects, RG-CR-02 (`17ac1ed`), RG-CR-04 and the RG-CR-03 wording (`38686c0`, `f0ca022`), README after `a6cbbf8`.
Accepted and not re-filed: RG-CR-05, RG-CR-07, H-02, SEC-03, SEC-04, two tabs, same-origin read and framing. Evidence:
`docs/modules/split-app/qa/regression-recheck/20261009-230750/` (`evidence.md` indexes every script and output). Project `src/` and
`tests/browser/` were not written (SHA-256 of every file before and after each batch: equal).

### BLOCKER

#### RG-CR-08: A double press on a "who had it" chip under a pending price error removes that item   (bug, regression of 071577a, contract-drift against R7 WR-01)
- **File and symbol:** `src/ui/items.js` `createItems` > `createRow`: `remove.addEventListener("click", () => { swallowRepeatClicks(); onRemove(id); })`.
  Same shape in `src/ui/people.js` `createPeople` > `createRow` (not reachable by this path today, see Reach). The guard's input is
  `src/ui/dom.js` `isRepeatClick`, file-private since `071577a`. The layout move comes from `src/ui/field-error.js` `createErrorSlot`
  (`host.append(paragraph)` inside `div.item-line`), timed by `src/ui/field-leave.js` `onFieldLeave` (RD-3, a blur caused by a press waits for `mouseup`).
- **Issue:** Before `071577a` each Remove handler ignored any click with a count above 1, armed or not (`if (!isRepeatClick(event)) onRemove(id)`).
  Since it, a Remove acts on every click that reaches it and relies on an earlier Remove, Add or dialog click having armed `swallowRepeatClicks`.
  RG-CR-01 closed one unarmed path (Add person). A price error is a second one, and no click can arm for it. With focus in a price field that holds
  invalid text, the first press of a double click, triple click or double tap on a chip blurs the field. RD-3 holds the blur until `mouseup`, the error line
  appears in the item's own `item-line` and pushes the item's chips (and every later item) down by one line, and the click on the chip toggles the person.
  The repeat press then lands on what was a line higher. For a chip in the first chip row whose x range meets the Remove button's, that is the item's own
  Remove, whose handler arms a guard and removes the row. The pressed control was a chip, which arms nothing, so no guard was outstanding. The whole item
  goes (name, price, who), silently, with no undo. R7's WR-01 note says "the second click of a double click or double tap on a remove button is ignored ... One row goes,
  not two" and adds "The same holds for R12". That holds only when something armed the guard.
- **Proof (run, not read):** `probe_toggle_remove.py`, 240 configurations (3 name sets x people 3 to 12 x widths 360, 375, 390, 412, 600, 768, 1024, 1280), by-item
  S1 bill, Item 1 price holds `abc` with focus. Scan of every 4 px point of every chip for what lies under it once the error shows, then the real
  `mouse.dblclick` at the first point that lands on a Remove, and a single click at the same point as control:

  | Tree | Layouts where a chip point lands on its own item's Remove | Real double click removed an item | Single click removed an item |
  |---|---|---|---|
  | `61c3cd3` (before the delta) | 96 of 240 | **0 of 96** | 0 of 96 |
  | `a6cbbf8` (HEAD) | 96 of 240 | **96 of 96** | 0 of 96 |
  | HEAD plus the fix below | 96 of 240 | 0 of 96 | 0 of 96 |

  Concrete repro: viewport 390 x 3000, by-item bill with Aisyah, Ben, Chen, Devi, Farid and the four S1 items, type `abc` in "Item 1 price in RM" and leave focus there,
  `mouse.dblclick(329.5, 577)` (the Farid chip of item 2). Result: "Remove Char kuey teow" gone, 4 items become 3. One click at the same point toggles Farid on item 2 and removes nothing.
  The candidate test `test_rg_cr_08_candidate.py` (6 rows: 375 and 390 px x mouse double, mouse triple, touch double) is **red 6 of 6 on HEAD** and green on the fix.
- **Reach (honest):** it needs a by-item bill, an invalid amount still typed in a price field that has focus, and a repeat press on a chip at the right end of the first
  chip row of an item. In an affected layout the points that land on a Remove are a median 1.4 percent (at most 4.8 percent) of all chip points. Whether a layout is
  affected depends on how wide the chips are:

  | Names | People counts that lay a chip over the Remove, by width |
  |---|---|
  | `P1` to `P12` | 360, 375: 6 or more. 390, 412: 7 or more. 600, 768: 10 or more. 1024: 9 or more. 1280: 10 or more |
  | Aisyah, Ben, Chen, Devi, Farid, Grace, Hafiz, Indra, Jia Hui, Kumar, Lina, Mei Ling | 375, 390: 5 or more. 1024: 7 or more. 1280: 8 or more. None at 360, 412, 600, 768 |
  | 12 longer names (Muhammad Aiman, Nur Aisyah Binti, ...) | 360, 375, 1024: every count from 3. None at 390, 412, 600, 768, 1280 |

  Person Remove buttons are above every price field, so no price error moves them. Dismiss note, the other mover the solver measured, puts no control
  under the pointer (see What held, item 1). The same shift can also put a neighbouring chip under a repeat press (a visible, reversible toggle). That was not
  measured and the fix below does not change it.
- **Fix (verified in a scratch copy, `FIXA` in `run_mutants.py`):** restore the old count test as a backstop at the sink, next to the guard. The guard still cancels the
  repeat press for the armed paths (it also protects Add person, which has no count test).
  ```js
  // src/ui/dom.js
  export const isRepeatClick = (event) => event.detail > 1;   // was file-private
  // src/ui/items.js and src/ui/people.js (createRow), and add isRepeatClick to the import from "./dom.js"
  remove.addEventListener("click", (event) => { swallowRepeatClicks(); if (!isRepeatClick(event)) onRemove(id); });
  ```
  With it: real double click removes 0 of 96, single click 0 of 96, full suite 427 passed (421 plus the 6 candidate rows) in 121.73 s, and the 218-test repeat-press
  selection (R6, R7, R12, R29, R30, R34) is still 218 of 218. The people handler gets the same line for one rule, though no known path reaches it.
  Add the candidate test (it finds the point on a scout page where the price is bad, then presses on a second page) next to the SEC-01 block.
- **Docs this refutes (update with the fix):** BUILD.md judgment call 18 ("The one candidate is a double click on 'Dismiss note'", "'Dismiss note' is the measured exception"),
  spec R7 (the RG-CR-01 correction names "Dismiss note" as the one control that moves rows and does not arm), the spec Threat model row "The bill, as the user left it"
  (same sentence), `swallowRepeatClicks` JSDoc in `src/ui/dom.js` ("a new one must" arm it, which cannot be done for a layout move that is not a click), and the BUILD.md code map
  and call 18 (`isRepeatClick` file-private). Say that a Remove ignores a repeat press itself and that the guard covers everything else.
- **Severity:** BLOCKER by the rule the orchestrator applied to RG-CR-01 (a regression of verified behaviour, `61c3cd3` was safe) and because it destroys typed data.
  It is narrower than RG-CR-01 (the reach table). Under the stop rule the orchestrator may rule it an accepted limit instead. Then the README "Known limits" table, the
  spec Residual risks and the ledger need a row, and the candidate test is not added. I do not recommend it, the fix is two lines and verified.

### What held

1. **RG-CR-01 as fixed (`e30b015`).**
   - The finder's `probe_add_double.py`, unchanged, on HEAD: 96 rows (3 sizes x 4 starting counts x 4 gestures x 2 places). All 96 add exactly one person, focus on `Person N+1 name`,
     `nextId` +1. The 36 right-edge repeat rows that were 0 of 36 on the shipped tree are 36 of 36. Centre rows and single clicks as before.
   - Hunt for a swallowed deliberate action, `probe_hunt.py`, 40 cases, 0 failed. Add person by keyboard (Enter and Space, mixed, 3 to 12 people): 9 of 9 add exactly one with
     focus on the new name. Add item by keyboard x6: 6 of 6. Tab + Enter on the new Remove while guards are outstanding: removes one person (a key click has count 0).
     After the 9 keyboard adds a mouse click on a Remove removes one and a double click on a name selects the word. A click of its own (count 1) on the new name field then typing
     keeps the text, and a click of its own on the new Remove removes that row, for Add person and Add item at the right edge and the centre (12 of 12). A click on the "By item"
     label straight after Add switches the mode. Type then double click the first and the second word after Add by mouse and by keyboard, people and items: 8 of 8 select a word
     (Windows Chromium includes the trailing space, `'Siti '`). A repeat press on the 12th person and the 50th item, three gestures x two places: 12 of 12 add one with focus on the new name.
     Remove, Add, then a double click on Add person adds exactly one (S2, S3).
   - By code: at most one guard is outstanding even for keyboard-only use. A key-activated click (count 0) is not a repeat, so the older guard removes itself in the capture phase before the
     new click arms another. A re-click at the same pixel inside the system double-click time is a repeat press by definition and is cancelled. It has no data effect, the new name field
     is already focused (R34) and empty. Clicks at another pixel have count 1 and pass.
   - Unarmed movers. **Dismiss note**, `probe_unarmed.py` part A: the whole 44 px button (9 points) at widths 320 to 1280 step 20, heights 568 and 844, with 2, 3 and 5 people: 2646 points,
     1038 `div`, 726 `h2`, 648 `section`, 234 `main`, **0 controls**. The solver measured the centre only, the claim holds for the whole button. A real double click leaves the bill as a single click
     does and focus on `BODY` (`probe_claims.py`, 3 sizes). **Mode labels**, part B: 108 repeat-gesture rows (2 bills x 3 sizes x 2 labels x 3 places x 3 gestures), 108 leave the same stored bill
     as one click, focus on `BODY`. Field-error shift: RG-CR-08.
2. **RG-CR-02 as fixed (`17ac1ed`).** Selection R6, R7, R12, R29, R30, R34 (218 tests), scratch copy per run, one in-memory replacement:

   | Mutant | Change | Result |
   |---|---|---|
   | BASE | none | 218 of 218 pass |
   | M1 | the removal pair removes `click` twice, the `mousedown` listener leaks | **4 red**: the R7, R29 and R30 "guard ends" tests and `test_R7_after_a_remove_click_a_double_click_on_a_name_still_selects_the_word` |
   | M2 | the `click` listener leaks | 3 red (the three "guard ends" tests) |
   | M9 | no `mousedown` listener registered (press side gone) | 124 red (R6 36, R7 36, R12 36, R29 9, R30 3, R34 4) |
   | M10 | no `click` listener registered (click side gone) | 116 red (R6 36, R7 22, R12 36, R29 9, R30 13) |
   | A1 | Add person arms nothing | 36 red, all of them right-edge rows of the R6 test |
   | A2 | Add item arms nothing | 36 red, every row of the R12 test |

   M1 was 106 of 106 green before and is red now. The tests pin the press side (M9) and the click side (M10) each by more than a hundred rows, and the lifetime of each listener separately (M1, M2).
3. **RG-CR-04 and the RG-CR-03 wording.**
   - `src/errors.js` header: `newErrorFlags`, `flagsFor`, `visibleErrors` are pure, `typedInto`, `leftField`, `forgetPrice` mutate the flags they are given and return nothing. True.
   - `gesture_at` docstring: a triple click is presses 1, 2, 3. Measured (`probe_claims.py`): the document saw `mousedown [1, 2, 3]` and `click [1, 2, 3]`. True.
   - qa.md: the SEC-01 comment names a range ("the tests after it in the same section of `test_app.py`, up to the RG-CR-01 header") and the section holds the four tests the
     solver names (R34 after a double click, a separate click, guard ends, word select). The RG-CR-01 outlines match the tests (people 2 to 5, items 1 and 4, three sizes, three
     gestures, two places: 72 + 36 rows). The I-1 comment "9 rows and the three after it" is still right. True.
   - BUILD.md: Status says what happened. Test counts: 312 + 72 + 36 + 1 = 421, "about 120 s" (120.74 s measured), fidelity `qa/fidelity/20261009-225850/` 10 of 10 at 0 px (`run.log`),
     live gate `live-gate-check/` `summary.json` result PASS, 7 steps, `failure` null. Call 20: A1 reds the right-edge rows only (36), A2 reds all 36 rows of the Add item test, M1 stays killed by the
     other three. Code map: `commit` takes the bill an action returned, saves, restates the status, renders. True. **Call 18 is refuted in part by RG-CR-08** (above).
   - Spec R6 (id counter moves once, focus on the new name), R12 (Add item arms the guard, the body sees press 1 and click 1 only), R30 (the guard is shared with Add person and Add item): true against
     the code and A1, A2. R7 and the Threat model row: the list of armers is true, the statement that Dismiss note is the exception is true but incomplete (RG-CR-08).
4. **README.md after `a6cbbf8`.** Status row "closed 2026-10-09" agrees with ledger row 50 and STATE.md. "At v1.0.0, 421 browser tests and 275 unit tests pass": measured below. The `commit` sentence matches
   `commit(next)` in `src/main.js` (the caller runs `commit(addPerson(bill))`, `commit` saves and renders). The `src/errors.js` sentence matches the code. "Known limits": the reasoning sentence names
   the ledger, `spec.md` (Residual risks, the heading exists) and `findings/security.md` (lines on the mode-label focus drop), and the Dismiss note / mode label row is true (no data change, focus on the body, measured above).
   `billCharges` is the exported function (`applyRate` is private to `result.js`) and "service charge and then SST on top" matches its code. The clipboard sentence matches `rig.new_context(clipboard=...)`
   (recorder, reject, missing). The backdrop sentence matches `createDialog`. The `swallowRepeatClicks` bullet names the armers exactly as the code has them and says it protects only the controls that arm it.
   Commands run once: `node --test "tests/**/*.test.js"` **275 pass, 0 fail**. `python -m pytest tests/browser -q -p no:cacheprovider` **421 passed in 120.74 s** (rig server pid 53972, port 1143, stopped by the rig).
   If RG-CR-08 is fixed the bullet needs one clause (a Remove also ignores a repeat press itself), nothing else in the README changes.

### Processes
PROCESSES: every server was the rig's `python -m http.server` on a free loopback port with headless Chromium, started and stopped by the rig or by the script that started it, each printing `STOPPED ... exited True, port free again True`
(pids and ports are listed in `evidence.md`). My pytest batches ran as subprocesses of `run_mutants.py`, which waited for each. The only thing left running at the end was a `python -m http.server 53410` (pid 44864) that serves the
Streaks app of the sibling project. I did not start it and did not touch it. I checked with `Get-CimInstance Win32_Process` by command line (`http.server`, `chrome-headless-shell`, `pytest`, `probe_`, `run_mutants`, `playwright`), and
the title of that server's page.
