---
module: split-core
kind: code-review
status: issues_found
counts: { blocker: 0, warning: 3, info: 1 }
date: 2026-10-15
head: d58f4ce
scope: "git diff v1.0.0..HEAD -- src/core (bill.js, money.js, result.js, spare.js new) and the Node tests of v1.1.0 tasks C1 to C6 (bill, money, result, spare, invariants, hygiene, summary, support/bills.js, support/rng.js), judged against spec.md v1.1.0 (R1 to R34, Contracts, Non-goals, threat model), qa.md, constitution.md and README.md"
evidence: docs/modules/split-core/qa/code-review/20261015-212541/
recheck: { date: 2026-10-16, head: 6cddc66, status: issues_found, counts: { blocker: 0, warning: 1, info: 3 }, evidence: docs/modules/split-core/qa/code-review/20261016-020001/ }
---
# Code review: split-core (v1.1.0, step 5)

Role. Code-review finder (read-only). Date 2026-10-15, HEAD `d58f4ce`, working tree clean for `src/`, `tests/`, `index.html` and `docs/design/` (`git diff --stat HEAD` on those paths empty, `git hash-object --no-filters src/system.css` is the golden blob `bf30dda`).

**Verdict. 0 BLOCKER, 3 WARNING, 1 INFO.** No wrong money result found, no hallucinated code, no non-goal built, no contract drift. The spare sen rules (R27 to R33) are correct on every path I traced and on every mutant I tried but one, and that one is a test gap, not a defect. The warnings are a lost BigInt guard on the result path (a test gap that a real probe shows can hide a wrong sen), a Bill field list now written twice with a comment that says "one place", and a README section that predates v1.1.0.

The previous review of this module was 2026-10-09 (v1.0, WR-01 to WR-10, all solved before the 1.0 seal). QA's verdict for this module today is PASS with no finding (`findings/qa.md`), so nothing here repeats it. QA-S5-1 (the missing `@R9 @R11` accessible description test) is split-app's and is not repeated either.

## Method
- Read every changed line of `src/core/` and the functions they call (`allocateByWeight`, `billWith`, `sparePeople`, `parseAmount`), the C1 to C6 records in `BUILD.md`, and the v1.1.0 Node test files.
- Reverse audit by symbol. Every new or changed symbol maps to an R#. `formatAmount` (R34), the `THOUSANDS_GAP` comma in `formatMoney` (R4), `spare` in `billWith` and `newBill` (R10, R27), `spareWith` and `spareWithout` (R11, R12, R27), `sparePeople` (R28), `chooseSpareRule` and `drawOrder` (R29), `chooseSparePerson` (R30), `pickAgain`, `MAX_DRAWS`, `rowsDiffer` (R31), `floorParts`, `divide`, `TOP`, `onePerson`, `atRandom`, `spareRule`, `nobody` (R20, R21, R32), `spareResult` (R33), the `no-prices` row (R18). The Contracts table lists exactly the exports found. Nothing maps to no R#, and nothing on the Non-goals list exists (no random source in core, no seeded generator, no record of draws, no fourth rule, no spare line in `summaryText`).
- Comment rule. No `file:line` citation and no TODO in `src/` (grep). Comments in the changed code say why, apart from the one false claim in CR-S5-2.
- 24 single-edit mutants on scratch copies of `src/` and the Node tests, 23 killed and 1 survived (`mutation-run.txt`, `mutation-summary.json`). The unmutated copy ran 379 of 379. One Node probe (`probe_trap.mjs`, `probe-trap-output.txt`).

## BLOCKER
None.

## WARNING

### CR-S5-1. The BigInt guard no longer covers `computeResult`'s charges split, and a float floor passes all 379 tests   (test gap, R21 (4), R8)
- **Symbol.** `floorParts` and `divide` in `src/core/result.js`. The tests that should catch it are the `@R21` and `@R32` cases of `tests/result.test.js` and the R22 sweep in `tests/invariants.test.js`.
- **What is wrong.** In 1.0, `computeResult` called `allocateByWeight` for the charges directly, so the R8 "BigInt trap" rows of `tests/allocate.test.js` guarded the result path too. Since C4 the result path has its own floor step. `floorParts` asks `allocateByWeight(amount, [total - weight, weight])[1]` for each floor, which is exact (I checked the argument and the probe agrees). But no test drives `computeResult` through a trap input, so the step's exactness rests on nobody's assertion. Mutant K02 replaces the body of `floorParts` with `Math.floor((amount * weight) / total)` and all 379 Node tests stay green.
- **Why it matters.** R21 (4) says the charges are "computed exactly as in R8". On a by-item bill where amount x weight passes 2^53, a float floor moves one sen between two people and every sum still adds up, so neither R22's sweep nor a user can see it. This is the 1.0 WR-01 lesson coming back through a new code path.
- **Evidence (run).** `probe_trap.mjs` builds a 38-item by-item bill through the real actions, p1 on 5 items worth 496,760.84 and p2 on 33 items worth 3,228,945.46, rates 10 and 6, so the charges division is the R8 trap row 61846725 over [49676084, 322894546]. The project's code gives charges [8246230, 53600495], equal to `allocateByWeight`. The K02 copy gives [8246231, 53600494] with `check.share` still equal to the total (`probe-trap-output.txt`). K02 survived 379 of 379 (`mutation-summary.json`).
- **Fix.** Add one `@R21 @R8` case to `tests/result.test.js` that builds the probe's bill (or any by-item bill whose charges division is an R8 trap row) and asserts the exact charges column, and add its row to qa.md beside the R8 trap rows. Seen failing first against the K02 edit as a stub.
- **Route.** Dev Solver (the test), planner (the qa.md row).
- **Solver, 2026-10-15 (dev solver, step 5 round). RESOLVED in `042c359`, the qa.md row is still the planner's.** `tests/result.test.js` gains "@R21 @R8 a by-item bill whose charges division is an R8 trap row gets the exact charges", the probe's 38 item bill through `buildBill`, asserting the charges column [8246230, 53600495] (equal to `allocateByWeight` on the trap row) and that a float floor misses the bill. RED on K02 by the reviewer's `mutate.mjs` in scratch: `docs/modules/split-core/qa/unit/20261015-233338-red-CR-S5-1/` (379 pass, 1 fail, the new test, [8246231, 53600494]). Proof on `4462b4c`: Node `docs/modules/split-core/qa/unit/20261015-234943/node-test.txt`, 380 of 380.

### CR-S5-2. The Bill field list is written twice, and `billWith`'s comment says it is written once   (DRY, doc rot, threat model "object integrity")
- **Symbol.** `withSpare` in `src/core/spare.js` and `billWith` in `src/core/bill.js`.
- **What is wrong.** `withSpare` lists the eight Bill fields by hand because `billWith` is private and the Contracts allow `bill.js` no new export. The builder named this as C5 "Deviation 2" and the ledger (S1 row 8) accepted it "for the code review to judge". Meanwhile `billWith` still carries the comment "One place that lists the Bill fields, so no action can forget one when copying." That sentence is now false, and it is the sentence a later builder reads before adding a ninth field.
- **Why it matters.** Adding a Bill field means editing two lists in two files (shotgun surgery). The tests catch a dropped field today (mutants K01 and K16 killed, 7 and 5 failures), so this is a maintenance and doc-rot risk, not a live defect.
- **Evidence.** From reading, and mutants K01 (drop `nextId` from `withSpare`) and K16 (spread the bill in `withSpare`) killed.
- **Fix.** Preferred, one list. The planner adds one export to the Contracts, for example `setSpare(bill, spare)` in `bill.js` (R27, built through `billWith`, the spare object rebuilt by the caller from known fields), and `spare.js` calls it in place of `withSpare`. If the contract stays, at least change the `billWith` comment so it names both lists, for example "Lists the Bill fields. `withSpare` in spare.js repeats this list (spare.js cannot import a private helper), so a new field goes in both."
- **Route.** Planner (contract choice), Dev Solver (the code or the comment).
- **Solver, 2026-10-15 (dev solver, step 5 round). RESOLVED in `9277412`, with no Contracts change.** One list without a new export: `newBill` (already exported, and a full Bill by definition) is the one place that lists the fields. `bill.js` keeps the private `BILL_FIELDS = Object.keys(newBill())` and `billWith` builds from it, and `spare.js` imports `newBill` and `withSpare` builds from the same keys. Never a spread. Both comments rewritten and now true. DRY safety: `docs/modules/split-core/qa/unit/20261015-233527-dry-CR-S5-2/`, Node 380 of 380 on `042c359` before and 380 of 380 after with the same names, and three mutants of the new form killed by the existing tests (a spread `withSpare` 5 like K16, a dropped `nextId` 7 like K01, a spread `billWith` 13). The planner may still prefer the export of the finding's first fix, which would replace this one.

### CR-S5-3. The README's split-core section predates v1.1.0   (doc rot, fallback owner of the README)
- **Symbol.** `README.md`, the "How it is built" block, the `split-core` bullets.
- **What is wrong.** It lists `parseAmount`, `parseRate`, `formatMoney`, `formatRate`, the two allocators, `billCharges`, `computeResult`, the actions and `summaryText`. It does not name `formatAmount` (R34), `sparePeople` (R28), `src/core/spare.js` with `chooseSpareRule`, `chooseSparePerson` and `pickAgain` (R29 to R31), the spare choice in the Bill (R27) or that `computeResult` now hands out spare sen by the bill's rule and returns `spare` (R32, R33). It says "`allocateEvenly` and `allocateByWeight` share an amount", while `computeResult` no longer calls `allocateEvenly` (CR-S5-4). The STATE note that the README header is owed (Versions row, mermaid) is known and not counted here.
- **Why it matters.** The README is the handover map. A reader who greps for the spare rules from it finds nothing.
- **Evidence.** From reading `README.md` against the Contracts table of `spec.md` and the exports of `src/core/` (grep of `export function`).
- **Fix.** Add one bullet per new export by symbol (`formatAmount`, `sparePeople`, `chooseSpareRule`, `chooseSparePerson`, `pickAgain`), one line that `computeResult` splits each division in floor parts and gives the spare sen by `bill.spare` (`floorParts`, `divide`, `spareRule`), and say that `allocateEvenly` is the reference for Top of the list in the tests.
- **Route.** Orchestrator (README reconcile), this finder as fallback.

## INFO

### CR-S5-4. `allocateEvenly` has no caller in the shipped page since C4   (R7, spec consistency)
- **Symbol.** `allocateEvenly` in `src/core/allocate.js`.
- **What.** `grep -rn allocateEvenly src` finds only its definition. R7 and the Contracts keep it, R20 and R21 use it to define Top of the list, and the tests use it as the oracle (`tests/invariants.test.js`, `assertEvenRule`). The Non-goals list says "Generic helpers nobody calls". The builder flagged this in C4. It is shipped in `src/core/` for a test oracle.
- **Suggestion.** For the planner. Keep it and say in R7 that it is the Top of the list reference used by the tests, or move the reference into `tests/support/` and retire R7's export. No code change until the spec says which.

## Mutants that were killed (the tests have teeth here)
The At random cursor reset (K03) and membership (K15), One person only inside its divisions (K04) and its fallback (K05), charges members with no items (K06), Pick again comparing shares only (K07), 63 draws (K08), redrawing the rule already set (K09), `sparePeople` ignoring items (K10), the order short after `addPerson` (K11), the choice kept after its person is removed (K12), one draw too many (K13), 1.0's row (c) (K14), One person with nobody (K17), `formatMoney` without the comma (K18). The draft decoder (D01 to D04) and the repeat rule (R01, R02) mutants were run in the same copy and are reported in split-app's verdict.

## Not done
Nothing in scope was left out. No browser run was needed for this module.

## v1.1.0 step 5 re-check, 2026-10-16

Role. Code-review finder (read-only), the one step 5 re-check under the stop rule. HEAD `6cddc66`, `git status` clean for `src/`, `tests/` and `index.html`. Scope `798f17f..HEAD` for this module, the step 5 solver round (`042c359`, `9277412`), the H-10 core build (`abfbe3e`, task C7, R35, R24, R25), its records (`4b0e915`) and the README reconcile (`6cddc66`). Judged against `spec.md` (R35, R24, R25, task C7, Contracts, Non-goals), `qa.md`, `constitution.md` and `README.md`. Evidence `docs/modules/split-core/qa/code-review/20261016-020001/` (`run-notes.txt` says what each file is).

**Verdict. 0 BLOCKER, 1 WARNING, 3 INFO.** No wrong share, no hallucinated code, no non-goal built, no contract drift. Every new symbol maps to an R# (`NAME_CONTROLS` and `plainName` to R35 and R24, `BILL_FIELDS` to the threat model row "Object integrity" and CR-S5-2). No core action calls `plainName` (R15 kept, grep). `\p{Bidi_Control}` is on one line under `src/`. The Contracts table lists exactly the two new exports. The tests have teeth, 16 of 16 mutants killed (measured, below). The one WARNING is the house writing rule in comments.

### The solver round, per finding (on today's tree)
- **CR-S5-1. HOLDS.** Measured. Mutant K02 (a float `floorParts`) on a fresh copy of HEAD fails exactly the new "@R21 @R8 a by-item bill whose charges division is an R8 trap row gets the exact charges", 399 pass 1 fail (`mutation-summary.json`, `node-test-K02.tap`). The qa.md row is the planner's, as the solver line says.
- **CR-S5-2. HOLDS.** Measured. One field list in code, `BILL_FIELDS = Object.keys(newBill())` in `bill.js` and `spare.js`, no spread, no new export. A spread `withSpare` (5 fail), a spread `billWith` (13 fail) and a `withSpare` that drops `nextId` (7 fail) are all killed today. The new comment overclaims a little, see CR-R2.
- **CR-S5-3 (README). CLOSED.** By grep and reading. The split-core bullets name `formatAmount`, `sparePeople`, `src/core/spare.js` with `chooseSpareRule`, `chooseSparePerson` and `pickAgain`, `floorParts`, `spareRule`, `bill.spare`, the `spare` of the result, `allocateEvenly` as the Top of the list reference of the tests, and since H-10 `NAME_CONTROLS` and `plainName`. Every symbol exists (grep of `export` and of each name in `src/core/`). "`allocateByWeight` ... is the one place that uses `BigInt`" is true (the only `BigInt(` calls are in `allocate.js`). What is still owed is in CR-R4.
- **CR-S5-4.** Planner's, PD-25 (R7 says why `allocateEvenly` stays). No code change, none expected.

### The H-10 build (C7), what was checked
- The shared `g` flag. `NAME_CONTROLS` is read only through `String.prototype.replace` (`plainName` and `summaryText`). No `.test`, `.exec` or `.match` call on it in `src/` or `tests/` (grep). Measured with a read-only probe, `plainName` gives "ABC" for "A" U+202E "B" U+2028 "C" even after `lastIndex` was set to 3, and leaves `lastIndex` at 0, five calls in a row give the same text, while `.test` on the same object alternates true and false (`run-notes.txt`, item 3). Safe today, see CR-R3.
- `summary.js` imports `NAME_CONTROLS` and keeps one code line. No import cycle (`bill.js` imports neither `summary.js` nor `result.js`).
- Mutants of C7, all killed (`mutation-summary.json`). No `g` flag (5 fail), no `\p{Bidi_Control}` (12 fail), a space in place of the deletion (13 fail), Cf deleted too (3 fail), `summary.js` keeping the import but printing only Cc as a space (7 fail, the every-code-point test among them, so a second class without the property name is caught by behaviour though the text scan misses it, as its comment says), and a first-match-only `plainName` (4 fail).
- The unmutated copy and the project tree each run 400 of 400 (`node-test-HEAD.txt`).

## BLOCKER (re-check)
None.

## WARNING (re-check)

### CR-R1. Comment lines changed in the range break the house writing rule (colons in prose)   (house rule, `{claude-root}\CLAUDE.md` Writing, constitution Writing style)
- **Symbol.** In `src/core/bill.js`, the comment above `BILL_FIELDS` and the comment above `NAME_CONTROLS`. In `tests/bill.test.js`, the comment above the test "@R35 @R24 plainName and summaryText read one class, 79 code points, for every code point". In `tests/hygiene.test.js`, the comment above `SRC_DIR` and `oneClassProblems`, and the comment inside the test "@R35 @R25 the class is written once, in core/bill.js, and summary.js reads it from there".
- **What is wrong.** Each has a colon inside a prose sentence. The text, as committed.
  1. `BILL_FIELDS` (from `9277412`, not in the H-10 solver's list), "every copy takes it: billWith here and withSpare in spare.js, which reads the same keys because the Contracts"
  2. `NAME_CONTROLS`, "The characters no name keeps (R35) and the summary prints as a space (R24): the C0 and C1 controls, the line and"
  3. `tests/bill.test.js`, "The proof that the names on screen and the copied summary cannot drift apart (spec R35 point 2): for every code"
  4. `tests/hygiene.test.js`, above `SRC_DIR`, "R35 point 2: the class that names lose and the class the summary prints as a space are one definition, so the"
  5. `tests/hygiene.test.js`, in the test, "The scan has teeth: summary.js back on a class of its own, scanned in a temporary folder beside the real bill.js."
  No em dash or en dash was added anywhere in `src/` or `tests/` in the range (grep, 0 lines).
- **Why it matters.** The rule binds every artifact, and the ledger (S7 row 45) routes these to one comment-only pass before `sdlc:regression --full`. The solver's list named two of these five, so a pass that follows it would leave three.
- **Evidence.** Read and grep of the added lines of `git diff -U0 798f17f..HEAD -- src tests`. The split-app findings file lists the rest of the range (CR-R5 there).
- **Fix.** A period or a comma in place of each colon, for example "so a new field is added there once and every copy takes it, billWith here and withSpare in spare.js." Comments only, no code line.
- **Route.** Dev Solver, the one comment-only pass ruled ORCH in S7 row 45.
- **Solver, 2026-10-16 (dev solver, A23 pass). RESOLVED in `b0992b4`, comments only.** The five lines are written without a colon in prose (line 1 by the CR-R2 rewrite). Every changed `.js` line of the commit is a comment line, and no added line holds `Bidi_Control`. Node 406 of 406 on `b0992b4` (`qa/unit/20261016-030139/`), by id against `20261016-012221/` 0 missing, 0 changed, 6 new (the app's CR-R6 cases).

## INFO (re-check)

### CR-R2. The `BILL_FIELDS` comment says `newBill` is the one place that lists the Bill fields   (doc precision, CR-S5-2 follow-up)
- **Symbol.** The comment above `BILL_FIELDS` in `src/core/bill.js` ("newBill is the one place that lists them, so a new field is added there once and every copy takes it").
- **What.** From reading. True for core's two copies (`billWith`, `withSpare`). The Bill typedef in `bill.js` lists the fields too, and split-app's `decode` in `src/draft.js` rebuilds the Bill from its own hand list (D12), by design, because each field needs its own check. A builder who adds a ninth field only in `newBill`, as the comment invites, gets a decoder that drops it on reload.
- **Suggestion.** "newBill is the one list that core's copies read (billWith here, withSpare in spare.js). The Bill typedef above and split-app's decoder (decode in draft.js, D12) list the fields too, so a new field goes in all three." Dev Solver, in the same comment-only pass.
- **Solver, 2026-10-16 (dev solver, A23 pass). RESOLVED in `b0992b4`, comments only.** The comment says `newBill` is the one list core's copies read (`billWith` here, `withSpare` in `spare.js`), and that the Bill typedef above and split-app's decoder (`decode` in `draft.js`, D12) list the fields too, so a new field goes in all three. The `BILL_FIELDS` comment in `spare.js` said "the one list" and now says "the one list core's copies read".

### CR-R3. `NAME_CONTROLS` is a shared, stateful `g` regex, and nothing stops a future `.test` call on it   (latent defect, spec R35 point 2)
- **Symbol.** `NAME_CONTROLS` in `src/core/bill.js`, and the "class is written once" scan `oneClassProblems` in `tests/hygiene.test.js`.
- **What.** The contract asks for the exported object with flags `gu` and says it is used only through `replace`. Today that holds (grep, probe above). `NAME_CONTROLS.test(name)` by a later caller would alternate true and false on the same text (measured, `run-notes.txt` item 3), and no test would see it unless that caller's own tests did.
- **Suggestion.** For the planner and Dev Solver. One line in the existing scan that every use of `NAME_CONTROLS` under `src/` is the first argument of `.replace(`, so the comment's "Read only through String.prototype.replace" becomes a checked rule. No code change in `src/`.

### CR-R4. The README does not mention the one Bill field list, which ledger S7 row 43 names as owed   (README reconcile, fallback owner)
- **Symbol.** `README.md`, "How it is built", the `split-core` bullets.
- **What.** Row 43 says "The orchestrator owes the README (CR-S5-3, -5, `BILL_FIELDS`)", and `BUILD.md` (step 5 round) gives the line, "`billWith` and `withSpare` copy the keys of `newBill()` (one field list)". The README names neither `billWith`, `withSpare` nor `BILL_FIELDS`. Nothing in it is false. Private helpers need not be in the README, so the orchestrator may also close this by a ledger line that says so.
- **Suggestion.** Either one clause on the actions bullet ("each builds its copy from the fields of `newBill`, never a spread, so a stray key in a parsed bill is not copied"), or a ledger note that the item is dropped. Orchestrator.

### Noted, no finding
- The C7 RED stubs, the DRY run before and after and the planted `summary.js` copy are the solver's (BUILD.md, task C7). Not re-run. The 16 mutants above are this review's own runs.
- The qa.md wording item "plainName gives AB exactly when Chen's row reads A B" (C7 Deviation 2) stays with the planner, as row 45 routes it.

## Not done (re-check)
Nothing in scope was left out. No browser run was needed for this module.
