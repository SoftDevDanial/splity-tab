---
module: split-app
kind: code-review
status: issues_found
counts: { blocker: 0, warning: 4, info: 6 }
date: 2026-10-15
head: d58f4ce
scope: "git diff v1.0.0..HEAD -- index.html src (outside src/core, 24 files, src/ui/panel.js deleted) and -- tests (A0 to A21 test side, with A20's live_e2e.py rewrite, the COLD_BOOT_JS, cold_boot_state, RECEIPT_JS and receipt move into support.py, COLD_BOOT into expected.py, and the A20 guard helpers in test_app.py), judged against spec.md v1.1.0 (R1 to R61, D1 to D14, Contracts, Gesture to action, Non-goals, threat model), qa.md, BUILD.md, constitution.md, CLAUDE.md and README.md"
evidence: docs/modules/split-app/qa/code-review/20261015-212541/
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
