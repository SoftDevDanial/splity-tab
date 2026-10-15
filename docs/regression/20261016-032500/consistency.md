---
kind: consistency-sweep
mode: sweep
run: sdlc:regression --full, v1.1.0
date: 2026-10-16
head: 64b882c
code: b0992b4 (git diff --stat b0992b4..HEAD -- src tests index.html is empty)
status: issues_found
counts: { blocker: 0, warning: 1, info: 7 }
evidence: docs/regression/20261016-032500/code-review-sweep/
---
# Consistency sweep

Role. Code-review finder (read-only), deliverable 2 of the v1.1.0 `sdlc:regression --full` code review. The whole codebase (`src/`, `index.html`, `tests/`) and its living docs (`README.md`, `CLAUDE.md`, both `spec.md`, both `qa.md`, both `BUILD.md`, the code comments), read for what a per-module review cannot see. The delta of the fix pass is reviewed in each module's `findings/code-review.md`, section "v1.1.0 regression --full, 2026-10-16", and is not repeated here. Severity as in those files. A claim from reading is labelled read, and a measured one names its capture.

**Verdict. 0 BLOCKER, 1 WARNING, 7 INFO.** One cross-module seam is measured wrong in both engines (CS-1). The rest are dead test code, stale doc lists, a contract stated two ways, small repeated derivations, a README hero that is 1.0's, and leftovers on disk.

Evidence `docs/regression/20261016-032500/code-review-sweep/`. `test_zz_probe_cs.py` is the probe of CS-1 (run on a scratch copy of the tree, never under the project's `tests/`), `junit-PROBE-CS-chromium-run2.xml` and `junit-PROBE-CS-webkit-run2.xml` hold its PROBE lines (the first pair, without `-run2`, is the same probe run with `-s`, whose lines went to the console only). `exports_census.py`, `test_side_census.py` and `unused_imports.py` are the read-only censuses, each run with `python -I` from the project root on HEAD.

## BLOCKER
None.

## WARNING

### CS-1. A name input that brings only characters of the class saves an unchanged bill and clears the copy status   (cross-module seam, app R25, R24 rule 10, R62 (1), core R15)
- **Symbols.** `commit` in `src/main.js` (it skips only when `next === bill`, and its comment says "the next change to the bill clears the copy status, and nothing else does"). `setPersonName` and `setItemName` in `src/core/bill.js`, which return a new Bill for a name equal to the stored one (only an unknown id returns the same bill). `plainNameField` in `src/ui/dom.js`, called from the `input` listeners of `createPeople` and `createItems`. Against them, `chooseSpareRule`, `chooseSparePerson` and `pickAgain` in `src/core/spare.js`, which return the same bill when nothing changes, so `commit` skips them.
- **What is wrong.** Measured in Chromium 149.0.7827.55 and WebKit 26.5. On S2 at 390 x 844 with the write counter (`count-set`), Copy summary on the strip shows "Summary copied". Then `insert_text("‮")` at the end of Person 2 name. `plainNameField` gives back "Ben", the stored name, `setPersonName` returns a new but equal bill, and `commit` saves it. One `setItem` call, the stored text unchanged, and the strip's status empty. The same for U+2028 put into an item name on S1. The control row (an "x" put in the same way) saves and clears too, as it should.
- **Why it matters.** App R25 ends "A commit that leaves the bill unchanged writes nothing", and R24 keeps the copy status until the next change to the bill. Before task A22 every `input` event changed a name, so the identity check in `commit` was enough. Since A22 an input can map back to the stored name, and the two modules' conventions disagree. Core returns the same bill for a no-op only in some actions, and the app treats a new object as a change. No per-module review can see it (the core setters and the app commit each read right on their own). Rated WARNING, not BLOCKER, because R25 also lists "each `input` event on any field" as a change, so one reading of the spec allows the save, and no data changes (the text written is the text stored). The visible part is the copy status vanishing after a paste that changed nothing.
- **Evidence.** Run. `test_zz_probe_cs.py`, three rows per engine, the PROBE lines in `junit-PROBE-CS-chromium-run2.xml` and `junit-PROBE-CS-webkit-run2.xml` ("setItem calls 1, stored text unchanged True, strip status before copied True, after copied False" for both class-only rows). Read, `commit`, `setPersonName`, `changeItem` and the three spare actions.
- **Fix.** For the planner first, one sentence in R25 or R62 (1) on whether an input that leaves every name as stored is a change. The recommended reading is that it is not (R25's last sentence). Then either (a) core, `setPersonName` and `setItemName` return the same bill when the name is unchanged, as the spare actions do, with a line in core R15 and Node cases, or (b) app, the `onName` handlers in `main.js` skip the commit when the plain text equals the stored name. Then a browser case in both engines with the write counter, a class-only insert into a person name and into an item name, asserting 0 `setItem` calls and the copy status kept, seen failing first on today's tree (the probe above is that RED).
- **Route.** Planner (the R25 or R62 sentence and the choice of a or b), then Dev Solver.

## INFO

### CS-2. Dead test code, two helpers and an import   (dead code, a false docstring)
- **Symbols.** `toggle_states` and `table_cells` in `tests/browser/test_app.py`, and the import of `I3` from `./support/bills.js` in `tests/spare.test.js`.
- **What.** Measured by `test_side_census.py` (each name appears once, at its definition, in all 44 tracked test files) and `unused_imports.py` (the one unused import under `src/` and `tests/` is `I3`). `table_cells` reads `table.shares`, the 1.0 table that v1.1.0 removed, and its docstring says "Read only by a test marked for a later task (A18), which rewrites it to the receipt". A18 removed that reader (`git log -S "table_cells("`, last in `101e842`), so no test reads it and the page never renders what it reads. `toggle_states` lost its last callers in task A8 (`e1969da`, found with `git log -G`). `I3` has been imported unused since C5 (`08f7faa`).
- **Why.** Dead code is a smell the constitution names, and a docstring that names a reader that does not exist is doc rot. The step 5 dead-code items (CR-S5-11, CR-S5-12) did not reach them, since they predate those ranges.
- **Fix.** Remove the two helpers and `I3` from the import list. The collected test ids stay the same (742 per engine, 406 Node).
- **Route.** Dev Solver (test side only).

### CS-3. The test side's file lists in the app spec and `qa.md` are stale   (doc rot, planner)
- **Symbols.** `docs/modules/split-app/spec.md`, Contracts, Files, the row `tests/browser/` ("Python Playwright tests (`conftest.py`, `rig.py`, `seeds.py`, `test_app.py`)"). `docs/modules/split-app/qa.md`, How to run, "this module's Node tests (`tests/draft.test.js`, `tests/errors.test.js`)" and the Evidence bullet.
- **What.** Read and listed (`git ls-files tests`). The Files row leaves out `support.py`, `expected.py` and `probe_webkit.py`, which hold the shared helpers (the live gate's among them, R41), the expected values and the A0 probes of R59. The How to run line leaves out `tests/repeat.test.js` (A17, the `@R57 @node` table) and `tests/dom.test.js` (A23, the `@R62 @node` outline), though the spec's own Files row for the Node tests admits both. The Evidence bullet names `pytest.txt`, `junit.xml`, `skips.txt` and the failure screenshots, while the R9, R45 and R50 records also land there and the three files appear only with `SPLIT_EVIDENCE=1` (the conftest module docstring).
- **Why.** The spec and `qa.md` are documentation held to the same standard as code, and a list that is short by three files reads as complete.
- **Fix.** Add the three Python files to the Files row, the two Node files to the How to run line, and the records and the `SPLIT_EVIDENCE=1` condition to the Evidence bullet, each with a dated note.
- **Route.** Planner.

### CS-4. The RED method is stated two ways, `xfail` commits in `qa.md` and a RED run on the tree before in the tasks   (docs contradict each other)
- **Symbols.** `docs/modules/split-app/qa.md`, How to run, the "Controls" bullet ("Every new or changed scenario is committed before its task as `xfail(strict=True, reason="task An")` ... The task that builds the requirement removes the mark"). `spec.md` tasks A22 and A23, step 1 RED. `skip_reason` in `tests/browser/conftest.py`, which still reads `wasxfail`.
- **What.** Read. A22 and A23 wrote their scenarios, ran them on the tree before the change in their own `qa/functional/<stamp>-<engine>/` folders, and committed the tests with the change (`4a19b4d`, `1f1eb97`), as their task text says. No scenario was committed as `xfail`, and the suite has none since CR-S5-12 (`grep xfail tests`, only the conftest branch). Both methods meet the constitution's rule (a control watched failing first), but the contract names one and the tasks follow the other.
- **Why.** The next builder who reads `qa.md` first will commit an `xfail` the newer tasks never used, or think the A22 and A23 REDs broke the contract.
- **Fix.** One dated line in the Controls bullet that a task may instead run the new scenarios RED on the tree before it and commit them with the change, keeping the RED folder, as A22 and A23 did. `skip_reason`'s `xfail` branch then stays, since it keeps an `xfail` counted if one is ever used.
- **Route.** Planner.

### CS-5. Three small derivations are written in both modules   (DRY candidates, no merge recommended now)
- **Symbols and the call on each.**
  1. "A result with splits". `hasSplits` in `src/ui/receipt.js`, the first guard of `summaryText` in `src/core/summary.js` and the guard after `computeResult` in `pickAgain` in `src/core/spare.js`, each `kind` "even" or "item". True DRY, they change for one reason (a new result kind with splits). A shared helper needs a core export that the Contracts forbid ("No other exports"), so the merge costs a contract line. Leave it, and the planner adds it if a result kind is ever added.
  2. "A rate text and its cap". `parseRate(bill.serviceText, LIMITS.serviceMaxPercent)` and the SST pair in `computeResult` (`src/core/result.js`), in the parser table of `src/errors.js` and in `chargesSummary` (`src/ui/sections.js`). True DRY. `chargesSummary` could read the `errors.js` table without touching core, which is the cheap half.
  3. "The fallback label of a blank name". The placeholders `Person {i}` and `Item {j}` built in `createPeople` and `createItems`, and the fallbacks of `personLabel` and `itemLabel` (`labelOf` in `src/core/bill.js`). They change together by ruling 4, but app R4 and core R17 each state their own, so they are tied by the specs rather than by code. Leave it.
- **What.** Read and grep (`kind ===`, `kind !==`, `parseRate(`, `` `Person ``).
- **Why.** Recorded so the next change to any of them changes all, as the constitution's DRY rule asks, and so no one merges them on looks alone.
- **Fix.** None now. Item 2's app half is optional (Dev Solver, behaviour verified before and after).
- **Route.** Planner (items 1 and 3), Dev Solver optional (item 2).

### CS-6. Test helpers and the name class are written twice across the module boundary, under two names   (DRY, one concept two names)
- **Symbols.** `spelled` in `tests/bill.test.js` (core) and in `tests/dom.test.js` (app). `NAME_CLASS` in `tests/draft.test.js` and in `tests/browser/test_app.py`, against `NAME_CONTROLS` in `src/core/bill.js`. The `src/draft.js` header ("app R62's class").
- **What.** Read. The two `spelled` helpers give the same text in two forms, and `tests/support/` already holds the shared Node test helpers (`bills.js`, `rng.js`). True DRY. `tests/draft.test.js` writes the class regex again without the `g` flag, because it calls `.test` on it, which on the shared `g` object would alternate (split-core CR-R3). That copy is false DRY and stays. The Python copy has to exist (no `\p{...}` in Python's `re`). But the one class has two names, `NAME_CONTROLS` in `src/` and `NAME_CLASS` in both test copies, so a grep for `NAME_CONTROLS` before a change to the class finds neither copy. The Node copy would then miss new members silently, and the 79 count in `tests/bill.test.js` is the only guard that would go red.
- **Fix.** Move `spelled` to `tests/support/` and import it in both Node files. In both `NAME_CLASS` copies add "a copy of NAME_CONTROLS (src/core/bill.js)" to the comment, so a grep of the name finds them. Test side only.
- **Route.** Dev Solver.

### CS-7. The README's hero, name and badges are 1.0's, and its caption calls them the built app   (README reconcile, fallback owner)
- **Symbols.** `README.md`, the top block (the lockup with alt "Split", the badges `version.svg` "version 1.0.0" and `tests.svg` "702 tests passing at 1.0.0", `docs/brand/screens/showcase.png` and the caption "Real captures of the built app, taken by the pixel gate ... Each one matches its approved design screen with 0 mismatched pixels"). Against app R43, `index.html`'s title "Danial's Splity Tab" and `h1.word` "Splity Tab".
- **What.** Read and `git log`. `showcase.png` and the badges date from `4a3c5bf` (2026-10-10, v1.0.0). HEAD's app has the v1.1.0 look, logo and name, which the README's own Versions row lists. The badges say "at 1.0.0", so they are true, but the caption says the captures are the built app.
- **Why.** The repository is public, and the first thing the README shows is not the app at HEAD. Version 1.1.0 is not sealed, so the 1.0 hero may be meant to stay until the seal, which the README does not say.
- **Fix.** Now, "Real captures of the app at v1.0.0". At the 1.1.0 seal (publish prep), new captures, lockup and badges. Docs only.
- **Route.** Orchestrator (README reconcile, at the seal).

### CS-8. Leftovers on disk   (leftovers, never delete)
- **Paths.** `harness/_scratch/design-final/` (3.7 MB), `design-r1-a/`, `design-r1-b/` and `design-r1-c/` (about 400 KB each), all from 2026-10-08, the 1.0 design phase's scratch, ignored by `.gitignore`. The empty folders `docs/compliance/` and `docs/qa/`, not tracked. The aborted fidelity capture `docs/modules/split-app/qa/fidelity/20261016-031935/` of today's QA finder (14 state folders), noted only, as the brief says.
- **What.** Listed (`ls -la`, `du -sh`, `find docs -type d -empty`). Nothing under `src/`, `tests/` or the project root is stray (`git ls-files` against `ls -la`), and no evidence folder of v1.1.0 is cited nowhere (the four functional folders without a `pytest.txt` are each cited in `BUILD.md`).
- **Fix.** Archive the design scratch by the house rule (`scripts/safe_move.py`, never a delete) if the owner no longer needs it. The empty folders can stay, they are the constitution's homes for compliance and ad hoc test output.
- **Route.** Orchestrator (the owner empties the archive).

## Checked and found sound (no finding)
- Exports. Every export under `src/` has a reader under `src/` except `allocateEvenly` (kept by PD-25), `AMOUNT_MIN_CENTS`, `AMOUNT_MAX_CENTS`, `billCharges`, `DRAFT_KEY`, `encodeDraft` and `decodeDraft`, each used in its own file, named in its module's Contracts and read by the tests (`exports_census.py`). The core Contracts Files table equals the exports, and the app's "Imports from split-core" list covers every core import under `src/` outside `src/core/` (grep). Every `LIMITS` key has a reader.
- The Bill field list. `BILL_FIELDS`, the Bill typedef and the decoder's own list are guarded together by the decoder round trip of `newBill()` and the key order test in `tests/draft.test.js` (read), so a field added only to `newBill` goes red.
- Cross-module security. Every name reaches the bill only through `plainNameField` or `readName`, and the summary replaces the class again (grep of `setPersonName(` and `setItemName(` callers). `src/` holds no network, other storage, timer, `innerHTML` or `eval` (grep). `Math.random` goes only to `chooseSpareRule` and `pickAgain`, `BigInt` is only in `allocate.js`, and `focusScroll` is the only `focusin` listener (grep), as the README says.
- No `file:line` citation in a comment under `src/` or `tests/`, no comment that asserts a test count that has gone stale, no commented-out code, no TODO, FIXME or stub (grep). No literal character of the class or of Cf in any tracked text file under `src/` or `tests/` (split-app evidence of this run, `check_escapes.py`). No `xfail` and no skip but the three `chromium_only` marks.
- The R# counts. App new 20, changed 40, unchanged 2, total 62, and core new 9, changed 9, unchanged 17, total 35, as both delta headers say (grep of the tags).
- `CLAUDE.md`'s commands match the scripts (`--engine`, `--control seeded` and `--base-url` in `live_e2e.py`'s parser, read without running it, and `SDLC_HARNESS` in `fidelity/run.py`). The server lifecycle of `qa.md` (50 tries 100 ms apart, the 10 s stop, the port re-check) is `rig.StaticServer` (read).
- `src/system.css` is blob `bf30dda`, equal to `HEAD:docs/design/system.css` (run).

## Known, not raised
- The older prose colons outside the step 5 lists (ledger S7 row 48, ruled to this doc pass or the v1.2.0 plan). For sizing, a heuristic grep of comment lines under `src/` for a prose colon or semicolon gives 46 hits in 17 files (a few are JSDoc types or a signature), from `grep -rnE "^\s*(//|\*)" src --include=*.js` filtered for a word, a colon and a space.
- The two `qa.md` notes the solver flagged (the held Enter "four repeats", the CR-R6 RED written as stubs by Edit). Two more stale notes of the same A23 section are split-app RG-CR-5.
- The README's Test it evidence column and its factories sentence are split-app RG-CR-1 and RG-CR-2.
