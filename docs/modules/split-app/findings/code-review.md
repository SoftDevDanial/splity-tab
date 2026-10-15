---
module: split-app
kind: code-review
status: issues_found
counts: { blocker: 0, warning: 4, info: 6 }
date: 2026-10-15
head: d58f4ce
scope: "git diff v1.0.0..HEAD -- index.html src (outside src/core, 24 files, src/ui/panel.js deleted) and -- tests (A0 to A21 test side, with A20's live_e2e.py rewrite, the COLD_BOOT_JS, cold_boot_state, RECEIPT_JS and receipt move into support.py, COLD_BOOT into expected.py, and the A20 guard helpers in test_app.py), judged against spec.md v1.1.0 (R1 to R61, D1 to D14, Contracts, Gesture to action, Non-goals, threat model), qa.md, BUILD.md, constitution.md, CLAUDE.md and README.md"
evidence: docs/modules/split-app/qa/code-review/20261015-212541/
recheck: { date: 2026-10-16, head: 6cddc66, status: issues_found, counts: { blocker: 0, warning: 5, info: 1 }, evidence: docs/modules/split-app/qa/code-review/20261016-020001/ }
---
# Code review: split-app (v1.1.0, step 5)

Role. Code-review finder (read-only). Date 2026-10-15, HEAD `d58f4ce`, working tree clean for `src/`, `tests/`, `index.html` and `docs/design/` (`git diff --stat HEAD` on those paths empty, `src/system.css` is the golden blob `bf30dda`).

**Verdict. 0 BLOCKER, 4 WARNING, 6 INFO.** No defect in the shipped behaviour found, no hallucinated code, no non-goal built. The four warnings are two tests that cannot see what they guard (the live gate's reads-only guard stops at `live_e2e.py`, and R20's `--rows` has no odd-count case), one comment that lists the guard's armers and has lost P1, and the README, which is stale well beyond the header that STATE already names.

QA's verdict for this module today is ISSUES with QA-S5-1 (no test for the `@R9 @R11` accessible description scenario) and the observations QA-S5-2 to QA-S5-5. None is repeated here.

## Method
- Read every changed line of `index.html`, `src/main.js`, `src/draft.js`, `src/errors.js` and `src/ui/*.js` and the functions they call, the BUILD.md records of A0 to A21 where a judgment call touched the code, and the A20 test side named in the handoff (`live_e2e.py` whole, `support.py`, `expected.py`, `conftest.py`, the A20 block of `test_app.py`). The rest of `test_app.py` (5,631 lines in all) was read by grep and by the tests the mutants select, not line by line.
- Reverse audit by symbol. `watchPointerClicks`, `isRepeatClick`, `isRepeatPress` (R57 (b), R7), `swallowRepeatClicks` with `keydown` (R57 (a)), `closeOnBackdropClick` (R30, R50, R52), `DESKTOP` (R50, R52, R49), `createReceipt`, `createSpareLine`, `CARD_IDS`, `SHEET_IDS`, `BLOCKED_MESSAGE`, `unassignedMessage`, `hasSplits` (R16 to R21, R51), `showCopyStatus` (R22 to R24), `createStrip`, `fit`, `focusScroll` (R49), `createSheet`, `makeRoom` (R50, R52), `createSpareChoice`, `createPicker`, `createPill`, `drawPills`, `createRandWrap`, `choicesFor`, `place`, `RULE_NAMES` (R52 to R54), `createPeopleSection`, `createChargesSection`, `peopleSummaries`, `chargesSummary`, `reveal` (R48), `createNotes` (R27, R46), `createFieldError` (R10, R14, R15), `markFrame` (R56), `readSpare`, the version 2 envelope and `loadDraft`'s `failed` (R61, R46), `openAsAtLoad`, `save`, `copySummary`, `personName`, `onPickAgain` (R48, R46, R47, R22, R51, R54). Nothing maps to no R#. Not built, as the Non-goals require. No timer, no scroll call besides `focusScroll` and `makeRoom`, no Tab wrap in the sheet or P1, no `autofocus`, no `innerHTML`, no `Math.random` outside the two draws, no hook for an engine.
- Comment rule. No `file:line` citation, no TODO, no commented-out code in `src/` (grep). One stale comment (CR-S5-8).
- Runs, all on scratch copies (`app-mutation-run.txt`). Four app mutants in headless Chromium through the copy's own conftest, 2 killed and 2 survived. The draft and repeat-rule mutants D01 to D04, R01 and R02 ran with the core set and were all killed (split-core's `mutation-run.txt`). Two read-only probes (`probe-rows-output.txt`, `probe-sheet-scroll-output.txt`) and one planted copy of `support.py` (`planted-support-guard-run.txt`).

## BLOCKER
None.

## WARNING

### CR-S5-5. The README describes the 1.0 app in several places, not only in its header   (doc rot, fallback owner of the README)
- **Symbol.** `README.md`, sections "How it is built", "Test it" and "The saved draft and security".
- **What is wrong.** STATE already names the header (the Versions row and the mermaid) as owed, which is known and not counted. The lines below are stale on top of it, each checked against the code by grep.
  1. `src/system.css` is "a byte copy ... plus one rule at the end, `[hidden] { display: none !important; }`". It is now an exact byte copy of the golden (blob `bf30dda`, spec R1). The extra rule is gone.
  2. The draft is "`{ "version": 1, "bill": ... }`" and the decoder applies "every rule D1 to D12". `encodeDraft` writes version 2 and `decodeDraft` applies D1 to D14 (`readSpare`). The section does not mention the save warning (R46, R47) and does not state the SW8 limit (private browsing and Safari's 7-day clean-up lose the bill with no failure the page can see), which R47 says "is written in the README by the orchestrator".
  3. `swallowRepeatClicks` is armed by "Every Remove button, Add person, Add item, and the New bill dialog on open and close". The Splits sheet (`createSheet`) and P1 (`createSpareChoice`) also arm it on open and close, it cancels a held key's repeats (R57 (a)), and a repeat is now `isRepeatPress` in `src/ui/repeat.js` fed by `watchPointerClicks` (R57 (b)). None of these is named.
  4. `closeOnBackdropClick` is "the one backdrop rule for the New bill dialog and the sheet". P1 uses it too.
  5. `showCopyStatus` draws "every status paragraph, the card's and the strip's". The sheet's is the third.
  6. "`createX(handlers)` returns `{ el, update }`". `createPeople` and `createCharges` return `content`, `createReceipt(rbody, handlers)` returns `{ update, spareChip }`, `createStrip(strip, handlers)` and `createSheet(dialog, opener, handlers)` take their element.
  7. "Test it" says "headless Chromium" and lists no WebKit command for the suite (`--engine webkit`, CLAUDE.md), and says "Each browser command starts and stops its own local server", which the live gate does not do with `--base-url` (the same table names that option).
  8. "What it does" has no spare sen choice (R51 to R54), save warning or folding sections. This may be part of the owed header pass.
- **Why it matters.** The README is the human's and the next agent's map. Point 1 tells a reader to look for a CSS rule that is not there, point 2 describes a draft format the app no longer writes, and the spec's one README duty for this module (SW8) is missing.
- **Evidence.** From reading `README.md` against `src/` and `spec.md`. `git hash-object --no-filters src/system.css` equals `git rev-parse HEAD:docs/design/system.css`. `grep -n "Private" README.md` finds nothing.
- **Fix.** Rewrite the eight points by symbol as above, and add the SW8 limit (and the other v1.1.0 residuals of the spec's threat model, if the owner wants them in "Known limits").
- **Route.** Orchestrator (README reconcile), this finder as fallback.

### CR-S5-6. The live gate's "reads only, real gestures" guard reads only `live_e2e.py`, while the gate reads and types through `support.py`   (a control narrower than its rule, R41)
- **Symbol.** `live_gate_problems`, `READS_ONLY`, `READ_EXPRESSIONS` and `BANNED_ATTRIBUTES` in `tests/browser/test_app.py`. The helpers it cannot see are `support.cold_boot_state` (`COLD_BOOT_JS`), `support.receipt` (`RECEIPT_JS`), `support.reads`, `support.active_label` and `support.replace_text`.
- **What is wrong.** qa.md's Rules say "`page.evaluate` only reads" and "Only real gestures change the app" for the gate. The guard checks the evaluate arguments and the banned attributes of the one file it parses. The gate makes 14 calls into `support.py` (`grep -oE "support\.[a-z_]+\(" tests/browser/live_e2e.py`), 9 of them through four helpers that run their own `page.evaluate` (`active_label`, `cold_boot_state`, `reads`, `receipt`) and 3 through `replace_text`, which sends the gestures of step 2. The gap is older than A20, since the 1.0 gate also read through a helper (`support.panel_text`). A20 made the gate lean on more of them, because it now reads the cold boot and the receipt through `COLD_BOOT_JS` and `RECEIPT_JS`, two of its largest page scripts, both outside the guard.
- **Why it matters.** A write added to `COLD_BOOT_JS`, or a `fill` in `replace_text`, would change what the gate proves (a cold boot, real typing) and every guard test would stay green.
- **Evidence (run).** In a scratch copy, `support.py` gained `localStorage.clear();` inside `COLD_BOOT_JS` and `locator.fill("")` inside `replace_text`, with `live_e2e.py` and `test_app.py` unchanged. `test_R41_the_gate_uses_real_gestures_and_reads_only` and the four `test_R41_a_planted_copy_of_the_gate_script_is_reported` cases all passed, 5 of 5 (`planted-support-guard-run.txt`).
- **Fix.** Make the guard follow the helpers. For each `support.<name>(` call in the gate's syntax tree, parse that function in `support.py`, check its `evaluate` arguments against the read-only list (adding `COLD_BOOT_JS`, `RECEIPT_JS`, `READS_JS` and the `active_label` expression by name) and its attributes against `BANNED_ATTRIBUTES`, and add a fifth planted copy that plants a write in a helper. qa.md's `@R41 @static` scenario names only `tests/browser/live_e2e.py`, so it needs one line for the helpers.
- **Route.** Planner (the qa.md line), Dev Solver (the guard and its planted copy).
- **Solver, 2026-10-15 (dev solver, step 5 round). RESOLVED in `8b7b7d4`, the qa.md line is still the planner's.** `live_gate_problems(path, helpers=SUPPORT_SCRIPT)` follows the support.py functions the gate runs (`gate_helpers`, today `active_label`, `card_text`, `cold_boot_state`, `person_field`, `reads`, `receipt`, `replace_text`), applies `BANNED_KEYWORDS`, `BANNED_ATTRIBUTES` and the read-only list to them too (`COLD_BOOT_JS`, `RECEIPT_JS`, `READS_AT_JS`, `ACTIVE_LABEL_JS` added), and checks the text of every page script the gate runs (`page_script_writes`: a call not on `READ_CALLS`, an assignment, `++` or `--`), so a write inside a listed script is caught too. `support.reads` and `support.active_label` now evaluate the named `READS_AT_JS` and `ACTIVE_LABEL_JS` (same text, checked). New `test_R41_a_planted_copy_of_a_helper_the_gate_runs_is_reported`, two planted copies of support.py, `localStorage.clear()` in `COLD_BOOT_JS` and `locator.fill("")` in `replace_text`. RED on the guard that read live_e2e.py only: `qa/functional/20261015-233931-chromium/` (red.txt, `[] == [...]` for both). GREEN `qa/functional/20261015-234036-chromium/`, 9 of 9 R41 tests, and the reviewer's own combined copy now reports `.fill is used` and `COLD_BOOT_JS calls clear(), which is not a read` (green.txt). Limit stated in the code: a text scan, not a parser. Full proof set in `BUILD.md`, "v1.1.0 step 5 solver round".

### CR-S5-7. R20's `--rows` is tested only at 12 people, so a floor in place of the ceiling breaks the desktop list for 7, 9 and 11 people and passes   (test gap, R20, PD-17)
- **Symbol.** `splitsAndProof` in `src/ui/receipt.js` (`list.style.setProperty("--rows", String(Math.ceil(result.rows.length / 2)))`) and the R20 and R38 tests that read `--rows`.
- **What is wrong.** Every test that reads `--rows` uses an even count (T12, "6"). With `Math.floor` the value is the same for every even count, so only an odd count above six can tell the two apart, and none is tested.
- **Why it matters.** `.r-splits.many` lays the rows out in columns with `grid-auto-flow: column` and `grid-template-rows: repeat(var(--rows), auto)`. A `--rows` one short makes the grid open a third column. The shipped code is right, but nothing would notice a regression.
- **Evidence (run).** Mutant U4 (floor in place of ceil) passed all 10 tests of `-k "R20 or R38"` (`app-mutation-run.txt`). `probe_rows.py` on a 7-person even bill at 1280 x 800 gives `--rows` "4" and 2 columns on the project and `--rows` "3" and 3 columns on the U4 copy (`probe-rows-output.txt`).
- **Fix.** Add a case with 7 people (or 9 or 11) in even mode at 1280 x 800 that asserts `--rows` "4" and two distinct column positions, and its row in qa.md beside the T12 line.
- **Route.** Dev Solver (the test), planner (the qa.md row).
- **Solver, 2026-10-15 (dev solver, step 5 round). RESOLVED in `d728076`, the qa.md row is still the planner's.** New `test_R20_seven_to_eleven_people_list_in_two_columns_on_the_desktop`, 7 to 11 people (T12 cut to its first n), even mode, 1280 x 800, asserting `--rows` ceil(n / 2) and two columns with that many rows in the first. The T12 test's column check moved into `in_two_columns`, which both call. RED on U4 by the reviewer's `mutate_app.py` in scratch: `qa/solver-step5/20261015-234515-red-CR-S5-7/red.txt` (7, 9 and 11 people fail on `--rows` 3, 4, 5 against 4, 5, 6, 8 and 10 pass). GREEN `qa/functional/20261015-234502-chromium/`, 8 of 8 R20 tests.

### CR-S5-8. `swallowRepeatClicks`' comment lists who arms the guard, and the list has lost P1   (doc rot, comment rule)
- **Symbol.** The JSDoc of `swallowRepeatClicks` in `src/ui/dom.js` ("the clicks that open and close the New bill dialog and the Splits sheet"), and the JSDoc of `isRepeatClick` in the same file.
- **What is wrong.** P1 arms the guard on open and on a click close (`open` and `closeByClick` in `src/ui/spare-choice.js`, R52, PD-21), and the comment does not say so. The comment is 16 lines and keeps a list of callers that a grep for `swallowRepeatClicks()` gives exactly (ten calls in five files), so it will rot again with the next caller. `isRepeatClick`'s JSDoc also carries a history paragraph ("In 1.0 the error line ... Since v1.1.0 ... (task A8)") that belongs in BUILD.md.
- **Why it matters.** A reader trusting the list would think P1's double click is unguarded, which is the kind of false claim the constitution's comment rule exists to stop.
- **Evidence.** From reading, and `grep -rn "swallowRepeatClicks()" src`.
- **Fix.** Replace the list of armers with the rule and the why ("every click that moves the layout under the pointer arms it, see the callers of swallowRepeatClicks"), keep the two lines on why it runs at the document in the capture phase, and move the 1.0 history out of `isRepeatClick`'s JSDoc.
- **Route.** Dev Solver.
- **Solver, 2026-10-15 (dev solver, step 5 round). RESOLVED in `4462b4c`, comments only.** The `swallowRepeatClicks` JSDoc gives the rule and the why ("Every click that moves the layout under the pointer calls it, and each caller says why"), each of the ten callers already carrying its own why, and keeps the capture-phase, held-key, first-press, RG-CR-08 and "Dismiss note" lines. 16 lines became 11. The 1.0 history paragraph of `isRepeatClick` moved to `BUILD.md`, task A8 ("Why a Remove still tests its own repeat press"), with the pointer "(BUILD.md, task A8)" left in the JSDoc. `git diff` showed only comment lines changed. Proof: the full suites of the round (BUILD.md).

## INFO

### CR-S5-9. The cancel of a running reveal on a fold is untested and has no visible effect   (R48 (3), KISS)
- **Symbol.** `if (!open) revealing?.cancel();` in `createSection`'s `setOpen` (`src/ui/sections.js`).
- **What.** Mutant U3 removes the line and all 26 R48 tests pass (`app-mutation-run.txt`). The only fold test folds after the reveal has ended. Below 1024 px the CSS hides a folded body, so a reveal that keeps running for its last few ms draws nothing either way.
- **Suggestion.** Either a test that folds within 200 ms of opening under `no-preference` and asserts no running animation on `#peopleBody`, or drop the line as speculative. Dev Solver's choice.
- **Solver, 2026-10-15 (dev solver, step 5 round). STILL-OPEN, not started.** The round stopped at its context limit before this INFO item. Nothing was changed. The resume point is in `docs/progress/handoff/handoff-2026-10-15-execute-split-step5-solver.md`.

### CR-S5-10. R52's sheet scroll goes up when the sheet is already scrolled past its Splits heading   (R52, spec silent, inherited from g2)
- **Symbol.** `makeRoom` in `src/ui/sheet.js`, `scroll.scrollTop += Math.min(overlap, headBelowTop)`.
- **What.** When P1 opens over a sheet whose heading is above the scroll area, `headBelowTop` is negative and the sheet scrolls up to put the heading at the top. On T12I at 360 x 780 the sheet went from scrollTop 424 to 199 and 5 of 12 rows ended under P1, the same as when it starts from the top. A person has to scroll that far to reach the chip, so this is the common path for a 12-person by-item bill on a small phone. The build copies g2's `keepSplitsInView` exactly, and the R52 test uses T12 at 390 x 844, where the sheet scrolls at most 135 px and the case cannot arise (`probe-sheet-scroll-output.txt`).
- **Suggestion.** For the planner. Say in R52 whether the heading cap may scroll the sheet up, or whether the scroll is downward only (`Math.max(0, Math.min(overlap, headBelowTop))`).

### CR-S5-11. `import re` in `tests/browser/support.py` is unused   (dead code)
- **Symbol.** The first import of `tests/browser/support.py`.
- **What.** No `re.` in the file. A20 noted it and left it. Delete it.
- **Solver, 2026-10-15 (dev solver, step 5 round). RESOLVED in `2ad022a`.** Removed. No name `re` in the file's syntax tree and nothing imports it from `support`. Proof: the full suites of the round.

### CR-S5-12. The xfail plumbing outlived the last xfail   (dead code, test side)
- **Symbol.** `R3_STATES` (every per-width task is `None`) with `R3_PAIRS`' conditional `xfail`, and `POLICY_STATES` (its seventh column is `None` in every row) in `tests/browser/test_app.py`.
- **What.** No xfail is left in the suite (the step 5 handoff), so the task columns and the conditional marks can go, which makes the two tables plain lists of cases.
- **Solver, 2026-10-15 (dev solver, step 5 round). RESOLVED in `c51d847`.** `R3_STATES` holds each row's widths (`EVERY_WIDTH` or 390 and 360, the same order), `R3_PAIRS` and the R38 policy parametrize carry no mark, and `POLICY_STATES` lost its always-None column. `--collect-only` gave the same ids for the R3, R35, R55 and R38 policy tests before and after (one digest), 716 collected, and no `xfail` is left in `test_app.py`. Proof: the full suites of the round.

### CR-S5-13. A second copy attempt with the same outcome is not announced again   (R24, spec silent)
- **Symbol.** `showCopyStatus` in `src/ui/copy-status.js` (`if (paragraph.textContent !== shown.text)`).
- **What.** From reading. After "Could not copy ..." a second failed attempt leaves the `role=status` paragraph untouched, so a screen reader says nothing the second time. The skip is there so that a render that is not a copy attempt stays quiet, which is right. Whether a repeat attempt must speak again is not in R24. For the planner.

### CR-S5-14. The suite's evidence folder may be shared by two runs of one engine in the same second   (constitution, Gates and evidence)
- **Symbol.** `evidence_dir` in `tests/browser/conftest.py` (`mkdir(parents=True, exist_ok=True)`).
- **What.** The live gate makes its folder without `exist_ok` so that a run can never write into another run's folder. The suite does not. Low risk, since a run takes minutes, but the rule is "each run writes its own capture". Drop `exist_ok` or add a suffix on collision.
- **Solver, 2026-10-15 (dev solver, step 5 round). RESOLVED in `6ffecf7`.** `evidence_dir` makes the folder with `mkdir(parents=True)`, so a second run of the engine in the same second stops with `FileExistsError`, as the live gate does. New `test_R58_a_run_never_writes_into_an_evidence_folder_it_did_not_make` (a frozen clock and a tmp_path root, asserting the second run does not get the first one's folder). RED on `exist_ok=True`: `qa/functional/20261015-234601-chromium/red.txt`. GREEN `qa/functional/20261015-234613-chromium/`.

## Checked and found sound (for the record, no finding)
- The repeat rule. `isRepeatPress`, `isRepeatClick` and the self-compare of a click. Mutant U1 killed by 14 touch double-tap cases. R01 and R02 killed by the `@R57 @node` table.
- P1's focus return. Mutant U2 killed, but only by the width-crossing case. In the other R52 close cases the browser's own dialog focus return already lands on the chip, so those cases pass with or without the app's line (`app-mutation-run.txt`, U2 note). Not a gap, since the crossing case covers the line, but worth knowing before trusting those cases alone.
- The decoder's D13 and D14. Mutants D01 to D04 killed.
- `openAsAtLoad` compares JSON text. It relies on `decodeDraft` building the Bill in core's key order, which its comment says and the R48 load cases exercise.
- The live gate script. The control path, the capture loop with its 5 s bound, `leave_document` across the close and the reload, and the `pass` rule in `main` read right, and the A20 control and green captures exist per engine (QA judged them).

## Not done
Nothing in scope was left out. Not run, by choice, the full browser suites, the fidelity gate and the live gate (QA ran them today on the same tree, and this review needed only targeted runs).

## v1.1.0 step 5 re-check, 2026-10-16

Role. Code-review finder (read-only), the one step 5 re-check under the stop rule. HEAD `6cddc66`, `git status` clean for `src/`, `tests/` and `index.html`. Scope `798f17f..HEAD` for this module, the step 5 solver round (`8b7b7d4`, `0094f40`, `d728076`, `6ffecf7`, `c51d847`, `4462b4c`, `2ad022a`), the H-10 app build (`4a19b4d`, task A22, R62, R33, D8), its records (`4b0e915`) and the README reconcile (`6cddc66`). Judged against `spec.md` (R62, R33, D8, R7, R27, task A22, Contracts, Non-goals, threat model), `qa.md`, `constitution.md`, `CLAUDE.md` and `README.md`. Evidence `docs/modules/split-app/qa/code-review/20261016-020001/` (`run-notes.txt` says what each file is). Every browser run was headless, on a scratch copy, through the copy's own conftest and clipboard stand-in.

**Verdict. 0 BLOCKER, 5 WARNING, 1 INFO.** No hallucinated code, no non-goal built, no contract drift. `plainNameField`, `readName` and every new test helper map to R62, R33, D8, R5, R11 or the solver round's findings. A22 adds no listener, no markup, no copy and no message (R62 Non-goals, grep and diff). The H-10 code is right on every path I traced and on 10 of 11 mutants (measured). The warnings are one 1.0 limit that 1.1.0's layout changed (a double click on Dismiss note now folds People below 1024 px, measured in both engines), a comment rule the CR-S5-8 fix stated wrongly, literal bidi controls in the Python test sources, README points left by the reconcile, and the house writing rule in comments.

### The solver round, per finding (on today's tree)
- **QA-S5-1. HOLDS.** Measured in Chromium. `test_R9_the_accessible_description_of_the_amount_fields_is_measured_and_reported` passes and writes its four lines (`accessible-description-BASE-chromium.txt`). The WebKit skip is the solver's run, read only here.
- **CR-S5-6. HOLDS.** Measured. 9 of 9 R41 tests pass. Mutant G1 (the guard follows no `support.py` helper) fails both `test_R41_a_planted_copy_of_a_helper_the_gate_runs_is_reported` cases (`pytest-G1-chromium.txt`). Read, `page_script_writes` is a text scan and says so. The planted-helper cases also catch a gate that stops calling through `support.`, since they run the real `live_e2e.py`.
- **CR-S5-7. HOLDS.** Measured. Mutant U4 (a floor for `--rows`) fails the 7, 9 and 11 people cases and passes 8 and 10 (`pytest-U4-chromium.txt`).
- **CR-S5-8. HOLDS for what it asked** (the list of armers is gone, so P1 is no longer left out, the 1.0 history is in `BUILD.md` task A8 under "Why a Remove still tests its own repeat press", with the pointer left). The new sentence that replaced the list is wrong, see CR-R2.
- **CR-S5-9.** Unchanged. `src/ui/sections.js` is not in the range. Accepted ORCH (ledger S7 row 43).
- **CR-S5-11. HOLDS.** No `import re` and no `re.` in `tests/browser/support.py` (grep), and nothing imports `re` from it.
- **CR-S5-12. HOLDS.** No `xfail` left in `tests/browser/test_app.py` (grep, 0), 728 tests collected (measured, `run-notes.txt` item 1).
- **CR-S5-14. HOLDS.** Measured. Mutant E1 (`exist_ok=True` back) fails `test_R58_a_run_never_writes_into_an_evidence_folder_it_did_not_make` (`pytest-E1-chromium.txt`).
- **CR-S5-5 (README), per point.** 1 closed (`src/system.css` is called an exact byte copy, and `git hash-object --no-filters src/system.css` equals `HEAD:docs/design/system.css`, `bf30dda`). 2 closed (version 2, D1 to D14, `readSpare`, the save warning and the private browsing limit are there). 3 closed (the sheet and P1 arm it, the held key, `isRepeatPress` in `src/ui/repeat.js` with 500 ms and 22 px, which are `REPEAT_TAP_MS` and `REPEAT_TAP_PX`, `watchPointerClicks`). 4 closed (P1 named for `closeOnBackdropClick`). 5 closed (the sheet's status paragraph named). 6 open in a narrower form, see CR-R4 (c). 7 closed (the WebKit row and the `--base-url` server sentence). 8 closed ("What it does" has the spare sen, the save warning and the folds).

### The H-10 build (A22), what was checked
- `plainNameField` caret. p minus k with k counted before p, as R62 (1) says (read). Mutants (Chromium, the 12 R62 ids). The caret at the end of the plain text (UC1) and no `setSelectionRange` (UC3) fail the middle-caret test. The item field reporting its raw value (UC4) fails the item test. Returning the typed text (UC5) fails 9 of 12. A caret of p less every removed unit (UC2) survives, see CR-R6.
- IME composition and ordinary typing. Read. The helper writes nothing unless `plainName` changed the value, and the field is plain before every event (the bill's names come only from the helper and the decoder), so a composition can be touched only when it brings a class character itself, which R33's exception allows. The solver's R33 IME and "writes nothing" runs are not repeated.
- Paste and drop. `insert_text` is one input event with the text, which is how a paste arrives (read). A drop that leaves the dropped text selected puts `selectionStart` before the removed characters, so the caret collapses at the start of the drop (read, by R62 (1)'s formula).
- D8. Measured, Node, on `src/draft.js` copies (split-core evidence, `mutation-summary.json`). The count of the stored name (D1), no LF and CR check (D2), an empty decoded name rejected (D3), no rebuild (D4) and `readPerson` or `readItem` keeping `raw.name` (D5, D6) are all killed. The count after the removal can only fall, because every class member is a grapheme cluster of its own (a Control), so no draft that loaded before H-10 is rejected now (read, UAX 29 GB4 and GB5). A name that becomes "" loads, and the G8 browser test sees the `Person 5` placeholder (BASE runs).
- Both engines on today's tree. Chromium 31 of 31 of `-k "R62 or R41 or R58_a_run or R20 or R9_the_accessible"`, WebKit 12 of 12 R62 (`pytest-BASE-chromium.txt`, `pytest-BASE62-webkit.txt`).

## BLOCKER (re-check)
None.

## WARNING (re-check)

### CR-R1. A double click on Dismiss note below 1024 px folds People, while the guard's comment, the README and spec R7 say its repeat press lands on a heading or a div   (UI state, R27, R48, R7, a 1.0 limit changed by v1.1.0's section rows)
- **Symbol.** The `dismiss` button of `createNotes` (`src/ui/note.js`, no `swallowRepeatClicks()`), `onDismiss` in `src/main.js`, the last line of the JSDoc of `swallowRepeatClicks` ("Dismiss note moves the rows and arms nothing, its repeat press lands on a heading or a div (BUILD.md, call 18)"), spec R7 ("Dismiss note arms nothing (1.0 BUILD.md judgment call 18)") and the README Known limits row "A double click on Dismiss note or a mode label moves keyboard focus to the page. No data changes".
- **What is wrong.** Measured. On the unreadable-draft bill (seed UNREADABLE B1, People open by R27), `page.mouse.dblclick` at the centre of Dismiss note at 390 x 844 and 360 x 780. The first click removes the note and focuses New bill (rule 12). The rows move up, and the second press lands on `#peopleBtn`, the People header row of v1.1.0 task A4, which folds People. Focus ends on `#peopleBtn` in Chromium and on body in WebKit. A single click leaves People open and focus on New bill. At 1280 x 800 the second press lands on `header.top` and focus goes to body in both engines, the 1.0 behaviour. The stored draft is unchanged in every case. Mode labels, the other half of the README row. In Chromium focus stays on the radio after a click and after a double click (it does not move to the page). In WebKit focus is on body after a single click as well, so a double click is no worse than a click there. Every double click leaves the same mode as a click.
- **Why it matters.** 1.0's call 18 found 0 controls under the button (2646 points), which is why Dismiss note arms nothing. v1.1.0 put a control there below 1024 px, so the spec's threat row "The first press moves a different control under the pointer and the repeat press lands on it" now applies to Dismiss note and nothing guards it. The bill is safe, but on a phone a double tap or double click undoes R27's open People and defeats rule 12's focus. Three documents state the 1.0 result as current.
- **Evidence (run).** `probe_known_limit.py`, the PROBE-BEGIN to PROBE-END lines of `pytest-PROBE-chromium.txt` and `pytest-PROBE-webkit.txt` (3 sizes x click and double click, Dismiss note and both labels). Read-only, headless, nothing pressed copies.
- **Fix.** For the planner first, R7 and the threat row. Either Dismiss note arms the guard like every other control whose click moves a control under the pointer (one `swallowRepeatClicks()` call in the `dismiss` listener of `createNotes`, a why comment, and a test that double clicks Dismiss note at 390 x 844 and asserts People open and focus on New bill), or the owner accepts the fold as the 1.1.0 form of the limit. Either way the JSDoc's last line and the README row get the measured text, for example "Below 1024 px a double click on Dismiss note folds People. No data changes. A double click on a mode label acts as one click".
- **Route.** Planner (R7, the threat row), then Dev Solver (the code, the test, the JSDoc line), orchestrator (the README row). It is a change of a 1.0 accepted residual, so the owner may want to see it (ledger "Needs the human").

### CR-R2. The new `swallowRepeatClicks` JSDoc states a rule that two of its own lines contradict   (comment rule, CR-S5-8 follow-up)
- **Symbol.** The JSDoc of `swallowRepeatClicks` in `src/ui/dom.js`, its sentence "Every click that moves the layout under the pointer calls it, and each caller says why".
- **What is wrong.** From reading, and the measurement of CR-R1. Dismiss note's click moves the layout under the pointer and does not call it (the same JSDoc's last line says so). Add item calls it although "No Remove button slides under this button" (its own comment in `createItems`, RG-CR-01). So the sentence is false in both directions. The old JSDoc said "nothing slides under that one, it arms so the rule stays one rule", which the rewrite dropped.
- **Why it matters.** CR-S5-8 was raised because the old comment made a false claim. Its fix makes a new one, the pattern the constitution's comment rule names (each round fixed the last false claim and minted a new one).
- **Fix.** Name the rule the callers follow, for example "Every control that adds, removes, opens or closes something under the pointer calls it (each caller says why), Add item included so the add controls share one rule. Dismiss note does not (R7)." The Dismiss line then follows CR-R1's ruling.
- **Route.** Dev Solver, comments only, after the planner's R7 ruling of CR-R1.

### CR-R3. The Python test sources hold literal bidi controls, separators and invisible characters, where the Node tests write escapes   (Trojan Source display risk, a control that can lose its teeth silently)
- **Symbol.** `G8` in `tests/browser/seeds.py` (U+202E twice, U+2067, U+2028 as literal characters), and in `tests/browser/test_app.py` `PLAIN_INSERTS` (U+202E twice, U+2028), `test_R62_a_removal_in_the_middle_of_a_name_keeps_the_caret_where_the_text_went_in` (U+202E, U+2067), `test_R62_characters_outside_the_class_stay_in_a_name` (U+200B, U+00A0, U+FEFF, two U+200D), `test_R62_an_item_name_loses_the_class_too` and `test_R62_a_name_made_only_of_removed_characters_falls_back_to_its_position` (U+202E each).
- **What is wrong.** Measured by a read-only scan of every changed file (`scan_invisible.py`, output in `run-notes.txt` item 4, 16 literal characters in the two Python files, none in `src/` and none in the Node tests, which write `\u{...}`). An unclosed U+202E inside a string reverses how the rest of its source line is drawn in an editor, a diff and on GitHub (CVE-2021-42574), and GitHub puts a warning banner on a file that holds one (known behaviour, not measured here). Some editors offer to remove U+2028 as an unusual line terminator on open or save (VS Code does by default, also not measured here). If one does, `("a b", "Benab", 5)` becomes `("ab", "Benab", 5)` and the `G8` name becomes "AB", and both tests still pass, so the U+2028 cases stop testing U+2028 with nothing going red.
- **Why it matters.** The repository is public, and these are the tests that prove the bidi fix. A reviewer cannot read what they assert, and the U+2028 cases can be lost to an editor's save.
- **Fix.** Write each as a Python escape (`"‮"`, `"⁧"`, `" "`, `"​"`, `" "`, `"﻿"`, `"‍"`), as `tests/draft.test.js` and `tests/bill.test.js` do, the test ids are already spelled. Optionally a one-line static test that no file under `tests/` or `src/` holds a literal character of `NAME_CLASS` or of Cf.
- **Route.** Dev Solver (test side only).

### CR-R4. README points the reconcile left or introduced   (README reconcile, fallback owner)
- **Symbol.** `README.md`, the sections "Known limits", "How it is built", "Test it", "The saved draft and security" and "How it was built". The JSDoc of `readName` (`src/draft.js`), the docstrings of `evidence_dir` and `evidence_folder` (`tests/browser/conftest.py`).
- **What is wrong.**
  - (a) The Known limits row on Dismiss note and the mode labels, see CR-R1 (measured).
  - (b) "while a line break still rejects the draft" (the security section). Measured on `decodeDraft`, only LF and CR reject. VT, FF, NEL, U+2028 LINE SEPARATOR and U+2029 PARAGRAPH SEPARATOR load with the character removed (`run-notes.txt` item 5). `readName`'s JSDoc says the same ("A line break rejects it before anything is removed").
  - (c) CR-S5-5 point 6, narrowed. "Each `create...` factory takes its handlers (and the element it fills, for `createReceipt`, `createStrip`, `createSheet`, `createSpareChoice` and `createNotes`), returns its node or `content` with an `update`, and states its exact signature in its file's header comment." `createDialog(dialog, opener, { onConfirm })` takes its element and returns nothing. `createFieldError(wrapper, input, { id, message, hint })` takes no handlers, returns `{ el, set, rename }` and `field-error.js`'s header gives no signature. `createPeopleSection(content, onToggle)` and `createChargesSection` take content, not handlers.
  - (d) "Test it", the Evidence column of both browser rows says "a failure screenshot". Since `0094f40` every Chromium run makes `docs/modules/split-app/qa/functional/<stamp>-chromium/` for `accessible-description.txt`, a passing run included (measured, the BASE run made it in its copy). The `evidence_dir` docstring ("made on first use (a failure screenshot, or SPLIT_EVIDENCE=1)") and the `evidence_folder` docstring ("R45 in WebKit") are stale the same way.
  - (e) The `plainNameField` bullet says it "keeps the caret where it was". The caret moves back by the characters removed before it (R62 (1), "where the text went in, less ..."), so "keeps the caret where the text went in" is the true form.
  - (f) "Some of what the reviews caught on the way to 1.0.0:" ends a prose sentence with a colon (house rule). It is the one README line of the range that breaks the rule (grep of the added lines).
  Every other symbol the README names exists (grep), and the behaviour claims I could check by reading hold, for example `focusScroll` is the only `focusin` listener, `Math.random` reaches only `chooseSpareRule` and `pickAgain`, `commit` skips an unchanged bill, the CSP string equals `index.html`'s, and 728 tests are collected and 400 Node tests pass (measured).
- **Why it matters.** The README is the owner's and the next agent's map, and (b) and (a) state behaviour the code refutes.
- **Fix.** (a) as CR-R1. (b) "while a line feed or carriage return still rejects it", in the README and in `readName`'s JSDoc. (c) name the exceptions or drop the claim to "each file's header comment gives its factory's signature" after adding one to `field-error.js`. (d) "a failure screenshot, and the records some scenarios write (for example `accessible-description.txt` in Chromium)" and the two docstrings to match. (e) as above. (f) a period.
- **Route.** Orchestrator (the README), Dev Solver (the JSDoc and the two docstrings, in the comment-only pass).

### CR-R5. Comment lines changed in the range break the house writing rule (colons and a semicolon in prose)   (house rule)
- **Symbol and text, as committed.** The split-core list is CR-R1 of `split-core/findings/code-review.md`. This module's lines.
  1. `src/draft.js`, JSDoc of `readName`, "D8: the name the bill gets, or null to reject the draft."
  2. `src/ui/dom.js`, JSDoc of `swallowRepeatClicks` (from `4462b4c`, not in the H-10 solver's list), "the pointer calls it, and each caller says why: the next press of that gesture would land on whatever is drawn there"
  3. `src/ui/dom.js`, JSDoc of `plainNameField`, "R62 (1), for the `input` listener of a person or item name field: the field's text without core's NAME_CONTROLS"
  4. `tests/browser/conftest.py`, docstring of `evidence_dir`, "Never exist_ok: a second run of the engine in the same second stops with FileExistsError rather than write into the"
  5. `tests/browser/test_app.py`, in `test_R9_the_accessible_description_of_the_amount_fields_is_measured_and_reported`, "CG-P6, ruled by the owner (USER, 2026-10-13): built to the golden, the description is measured and reported to the"
  6. `tests/browser/test_app.py`, docstring of `in_two_columns`, "Whether the splits rows at `edges` (ROW_EDGES_JS) stand in two columns with `rows` in the first: those share one"
  7. `tests/browser/test_app.py`, comment above `READ_CALLS`, "What a page script of the gate may call: reads of the page, of the stand-in's records and of the draft's text, the"
  8. `tests/browser/test_app.py`, docstring of `string_value`, "The text of a string expression: a literal, a name in `strings`, or an f-string of those."
  9. `tests/browser/test_app.py`, docstring of `gate_helpers`, "The functions of support.py the gate runs: those it calls as support.<name>, and those these call in turn."
  10. `tests/browser/test_app.py`, comment above `PLANTED_HELPER_FAULTS`, "reports (code review CR-S5-6: the gate reads the cold boot through COLD_BOOT_JS and types through replace_text)."
  11. `tests/browser/test_app.py`, in `test_R58_a_run_never_writes_into_an_evidence_folder_it_did_not_make` (a semicolon), "first one's folder (constitution, Gates and evidence, each run writes its own capture; code review CR-S5-14)."
  12. `tests/browser/test_app.py`, the section banner above `NAME_CLASS`, "Task A22: names stay plain (R62, R4, R5, R11, R26, R33)". A heading label in the file's banner form, which the older banners share ("Task 5: items ..."). The pass may keep it for the file's style, say so if it does.
  13. `tests/browser/test_app.py`, comment above `NAME_CLASS`, "The class of core R35 written out, because Python's re has no \p{...}: the C0 and C1 controls (Cc, 65), LS, PS and"
  14. `tests/browser/test_app.py`, docstring of `insert`, "qa.md "insert T": page.keyboard.insert_text(T) on the focused field, one input event with the text, which is how"
  15. `tests/browser/test_app.py`, in `test_R62_a_control_or_bidi_character_put_into_a_persons_name_is_removed_at_once`, "qa.md "Copy summary on the card" at 390 x 844: the card is not displayed below 1024 px, so the one Copy summary"
  16. `tests/browser/test_app.py`, comment above `FIELD_WRITES_SPY_JS`, "A test-side spy on "Person 2 name" alone: every call of the value setter of HTMLInputElement.prototype and of"
  No em dash or en dash was added in `src/` or `tests/` in the range (grep, 0 lines). Colons inside code, regular expressions (`(?:`), dict literals and the `key: value` shapes are not counted.
- **Why it matters.** As in split-core CR-R1. With both files, the range holds 21 such lines (5 in `src/`, 16 in `tests/`, one of them the banner), against the 9 the H-10 solver named.
- **Evidence.** Read and grep of the added lines of `git diff -U0 798f17f..HEAD -- src tests`.
- **Fix.** A period or a comma for each, comments only.
- **Route.** Dev Solver, the comment-only pass ruled ORCH in ledger S7 row 45.

## INFO (re-check)

### CR-R6. No test tells "p minus the removed units before p" from "p minus every removed unit"   (test gap, R62 (1), R33)
- **Symbol.** `plainNameField` in `src/ui/dom.js` (`plainName(typed.slice(0, input.selectionStart)).length`) and the R62 browser tests.
- **What.** Measured. Mutant UC2 (`input.selectionStart - (typed.length - plain.length)`) passes all 12 R62 ids in Chromium (`pytest-UC2-chromium.txt`). The two differ only when a removed character lies after `selectionStart`, which a key or `insert_text` cannot cause (the old text is plain and the new text lands before the caret) and a drop that selects the dropped text can. The shipped line is the spec's formula, so this is a gap, not a defect.
- **Suggestion.** A Node case for `plainNameField` with a stand-in input (`{ value, selectionStart, setSelectionRange }`, `dom.js` imports touch no DOM at load), for example value "Be" U+202E "n" with `selectionStart` 2, expecting value "Ben" and the caret at 2. Dev Solver, and a qa.md row by the planner.

## Not done (re-check)
- Not run, by choice, the full suites, the fidelity gate and the live gate. The solver's proof runs on `4a19b4d` (BUILD.md, task A22) cover them, read not re-run, and nothing under `src/`, `tests/` or `index.html` changed after `4a19b4d` (`git diff --stat 4a19b4d..HEAD -- src index.html tests` is empty, run).
- A touch double tap on Dismiss note was not probed (the guard is not armed there, so the repeat rule does not decide it).
