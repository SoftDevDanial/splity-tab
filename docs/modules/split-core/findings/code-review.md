---
module: split-core
kind: code-review
status: issues_found
counts: { blocker: 0, warning: 3, info: 1 }
date: 2026-10-15
head: d58f4ce
scope: "git diff v1.0.0..HEAD -- src/core (bill.js, money.js, result.js, spare.js new) and the Node tests of v1.1.0 tasks C1 to C6 (bill, money, result, spare, invariants, hygiene, summary, support/bills.js, support/rng.js), judged against spec.md v1.1.0 (R1 to R34, Contracts, Non-goals, threat model), qa.md, constitution.md and README.md"
evidence: docs/modules/split-core/qa/code-review/20261015-212541/
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
