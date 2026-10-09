---
module: split-core
kind: code-review
status: issues_found
counts: { blocker: 0, warning: 10 }
---
# Code review: split-core

Role: code-review finder (read-only). Date: 2026-10-09.
Scope: `git diff 1453dda..67e4b6e` (src/core/money.js, allocate.js, bill.js, result.js, summary.js, tests/*.test.js, tests/support/rng.js, tests/support/bills.js, docs/modules/split-core/BUILD.md).
Judged against spec.md (R1 to R26, Contracts, Non-goals, threat model), qa.md, constitution.md, CLAUDE.md and brainstorm.md.

**Verdict: PASS. 0 BLOCKER, 10 WARNING.** No wrong money result, no hallucinated code, no non-goal built, no contract drift. The warnings are vacuous or masked controls, false numeric claims (three of them in the spec and copied into BUILD.md), and two coverage gaps that mutation testing exposed. Fix WR-01 to WR-03 before the orchestrator reconciles the README, because BUILD.md's "Notes for the README reconcile" would carry those false claims into it.

## Evidence (all under `docs/modules/split-core/qa/code-review/20261009-114916/`)
- `node-test.txt`: `node --test "tests/**/*.test.js"` on Node v24.11.1. **tests 185, pass 185, fail 0**, exit 0. This matches the count in BUILD.md.
- `per-commit-summary.txt`: the task rule says every commit leaves the suite green. Each of the 8 build commits was rebuilt from `git show` and run. All were green: 51, 67, 93, 121, 161, 162, 172 and 185 tests, 0 failures.
- `probe-output.txt`: P1 to P10 behaviour probes plus a float-divergence search (`scripts/probe.mjs`, `scripts/traps.mjs`).
- `mutation-summary.json` and `mutants/M01..M16/`: 16 single-edit mutants. Test files in the copies are renamed `*.mutcase.js` so no default `node --test` glob picks them up. 10 were killed, 5 survived (M01, M07, M08, M09, M12, each tied to a finding below) and 1 is equivalent (M16).

Independent recomputation (BigInt, no core code, probe P1):
- **S2.** Subtotal 10000. Service 1000. SST on 11000 is 660. Total 11660 (RM 116.60). 11660 / 3 is 3886 rem 2, so the shares are **38.87, 38.87, 38.86**.
- **S1.** Aisyah 1590 + 900 = 2490, Ben 1350, Chen 1200 + 900 = 2100, subtotal 5940. Service 594. SST on 6534 is 392.04, rounded to 392. Total **6926 (RM 69.26)**. The 986 of charges split by weight floors to 413 / 224 / 348 (sum 985), and the 1 leftover sen goes to Aisyah. Shares are **29.04, 15.74, 24.48**.
- The core returns exactly these. E1, E2, E3, I2, I3, I4, D1, D2, MAX-E and MAX-I were also re-derived by hand and match spec and qa.

## BLOCKER
None.

## WARNING

### WR-01: The BigInt guard rests on one R8 row. The MAX-I tests and spec R23 claim a float allocator fails MAX-I, and it does not   (vacuous control, false claim in spec)
- **File:** tests/result.test.js:163-169 (title "a float product is off" and the comment at :164). tests/allocate.test.js:40-45 (title "stays exact when amount times weight passes 2^53"). spec.md:114 (R23 last sentence "A floating-point implementation gets these charges wrong"). spec.md:234 (threat row lists "R23 bound tests" as a 2^53 mitigation). qa.md:220-224. spec.md:95 (R8 row wording).
- **Issue:** Mutant M04 replaces the BigInt floors in `allocateByWeight` with `Math.floor((amount * w) / W)`. Exactly one test kills it: `@R8 allocateByWeight(236419679, [314963010,157876348])`. Both MAX-I tests stay green, because the float products there are even numbers below 2^54 and are exact (probe P4 shows float equals exact on MAX-I). The R22 sweep cannot catch it either. 30 of its 1000 by-item bills pass 2^53, but 0 of them have a float floor that differs from the exact one (P10). 2,000,000 random in-bounds two-weight inputs found no divergence at all (traps.mjs). So the comment "a float implementation drifts on exactly these weights" is false, the R23 sentence is false, and the two MAX-I titles describe a guard they do not provide. One more detail on the R8 row: `Math.floor(a * w / W)` alone gives [157481505, 78938173]. The quoted [157481506, 78938173] is the float allocator after the leftover step.
- **Fix:** Retitle both MAX-I tests to what they actually prove ("MAX-I charges are exact at the bound") and delete the comment at result.test.js:164. Tag the R8 trap row as the BigInt guard, for example `@R8 BigInt trap: ...`. In spec.md:114 replace the last sentence with "The BigInt trap case is the R8 row 236419679. A float allocator still gets MAX-I right." In spec.md:234 cite "R8 trap row" instead of "R23 bound tests". In spec.md:95 write "a float allocator (Math.floor of a x w / W, then the leftover rule) gives".

### WR-02: False numbers on the 2^53 bounds, stated in the source, in BUILD.md and in the spec   (doc rot, DRY across code and docs)
- **File:** src/core/result.js:26 (`applyRate` JSDoc). BUILD.md:68-70. spec.md:17.
- **Issue:** (a) The JSDoc says the product is "at most 649,999,935 x 2000". The largest product is actually the service step, 499,999,950 x 3000 = 1,499,999,850,000, which is bigger than 649,999,935 x 2000 = 1,299,999,870,000 (P2). BUILD.md:68 repeats the same wrong maximum. (b) spec.md:17 says `charges x weight` "can reach about 1.4e16". With one person on all 50 max items the weight is 499,999,950, so the product is 279,999,972 x 499,999,950, about 1.4e17 (P3). BUILD.md:70 copies the 1.4e16. Both conclusions still hold ("Number is enough" in `applyRate`, "BigInt is needed" in `allocateByWeight`). The stated numbers are wrong, and each derivation now lives in two or three places that will drift apart. BUILD.md's notes section also restates three more source comments: the `MAX_WHOLE_DIGITS` reasoning (money.js:16-17 vs BUILD.md:62 and :72-73), the remainder-first division (allocate.js:24 vs BUILD.md:71) and the rebuild claim of WR-03 (bill.js:5-6 vs BUILD.md:74-75).
- **Fix:** In `applyRate` state the stable effect, for example "Within the spec's bounds (spec Invariants) every product is far below 2^53, so Number is exact here", or give the correct maximum, 499,999,950 x 3000. Correct spec.md:17 to "about 1.4e17". In BUILD.md, replace the four restated derivations with symbol references (`applyRate`, `allocateByWeight`, `readHundredths`, `billWith`) so each derivation has one home.

### WR-03: "Parsed bills lose stray and `__proto__` keys on the first action" is false, and the test that claims to prove it is masked   (false comment, control that cannot fail)
- **File:** src/core/bill.js:5-6 (module header). BUILD.md:74-75. tests/bill.test.js:165-176, with the composition at :170.
- **Issue:** Only the Bill object and the one person or item an action changes are rebuilt. Untouched people and items are reused by reference. In probe P5, after `setMode` then `setPersonName("p1")` on a parsed bill, `people[1]` still has keys `["id","name","x","__proto__"]` (an own `__proto__` key), `items[0]` still has `"stray"`, and `people[1]` is still the parsed object. No prototype pollution happens (`{}.polluted` stays undefined), so this is a false claim, not a vulnerability. The guarding test also cannot catch the pattern the threat model forbids (spec.md:238, "no spread of a whole parsed object onto a target"). Mutant M12 changes `setMode` to `return { ...bill, mode }` and all 185 tests stay green, because the test passes `setMode`'s output through `setPersonName`, whose `billWith` rebuild drops the stray keys before the assertion. The R16 frozen-bill test does not catch it either, since a structured clone of S1 has no stray keys.
- **Fix:** Reword bill.js:5-6 and BUILD.md:74-75 to the true scope: "The Bill and any person or item an action changes are rebuilt from known fields. Untouched people and items are shared by reference, so cleaning a parsed bill is split-app's draft decoder's job." Then test each action's output on the parsed bill directly instead of through a composition:
  ```js
  const actions = [(b) => setMode(b, "item"), (b) => setSubtotalText(b, "1"), (b) => setServiceText(b, "1"),
    (b) => setSstText(b, "1"), (b) => addPerson(b), (b) => addItem(b), (b) => setPersonName(b, "p1", "Z")];
  for (const act of actions) {
    const next = act(parsed);
    assert.deepEqual(Object.keys(next), BILL_KEYS);
    assert.equal(Object.hasOwn(next, "__proto__"), false);
  }
  ```
  Route this to the split-app spec as well: its draft decoder must rebuild or reject people and items that carry unknown keys.

### WR-04: No test can tell R11's "p" + nextId from "p" + list length, and a regression would mint duplicate person ids   (test gap on a money-affecting rule)
- **File:** src/core/bill.js:67 (`addPerson`). tests/bill.test.js:38-51.
- **Issue:** Mutant M07 builds the id as `` `p${bill.people.length + 1}` `` and survives all 185 tests. Every `addPerson` test starts from a bill where `nextId === people.length + 1`. After add, add, remove p3, add, the correct code gives p1, p2, p4, p5 (P9). The mutant gives p1, p2, p4, p4. With two people sharing id p4, `toggleItemPerson` and `removePerson` act on both, and by-item shares come out wrong with every check still adding up. (`addItem` is covered, because S1's i8 differs from a length-based id.)
- **Fix:** Add to tests/bill.test.js:
  ```js
  test("@R11 a new person's id comes from nextId, so it never reuses a removed id", () => {
    let bill = addPerson(addPerson(newBill()));
    bill = addPerson(removePerson(bill, "p3"));
    assert.deepEqual(bill.people.map((p) => p.id), ["p1", "p2", "p4", "p5"]);
    assert.equal(bill.nextId, 6);
  });
  ```

### WR-05: R16 purity is tested for bill actions and `computeResult` only, so a `summaryText` that mutates its input passes   (test gap)
- **File:** tests/bill.test.js:141-163. tests/result.test.js:192-198. tests/support/bills.js:51-93 (fixtures are exported unfrozen). src/core/summary.js:11-24.
- **Issue:** R16 says no exported function mutates its arguments. Mutant M08 adds `result.rows.forEach((row) => { row.name = row.name.trim(); })` to `summaryText` and survives all 185 tests. `allocateByWeight` weights and the label functions are not frozen anywhere either. The shared fixtures are plain objects, so a mutating function would silently corrupt S1 and friends for every later test in the same file.
- **Fix:** Wrap each fixture export in bills.js with `deepFreeze(...)`. All current tests stay valid because the code is pure, and every `computeResult` call then also checks purity. Add `summaryText(deepFreeze(computeResult(S1)))`, `allocateByWeight(10, Object.freeze([1, 2]))` and `personLabel(Object.freeze({ id: "p1", name: " A " }), 0)` to the R16 test.

### WR-06: The digit-cap control cannot fail, and the threat model cites a test that does not exercise it   (vacuous control, overstated comment, magic number)
- **File:** src/core/money.js:13, :16-18, :31. tests/money.test.js:46-50. spec.md:236.
- **Issue:** Mutant M01 deletes `if (whole.length > MAX_WHOLE_DIGITS) return INVALID;` and all 185 tests stay green. Without the cap, `Number("1" + 400 zeros)` is `Infinity`, which fails the range check, so the 401-character case returns INVALID with no exception either way. No input gives a different output with or without the cap, so spec.md:236 ("checks the digit count before any numeric conversion (400-digit case in R1)") cites evidence that does not prove it. The comment at money.js:13, "cannot make it backtrack", is also not literally true. `[0-9]+` backtracks once per digit on a failing tail. The work stays linear (5,000,000 digits plus "x" took 10 ms, P7), so the safe claim is "no catastrophic backtracking". Finally, `MAX_WHOLE_DIGITS = 9` is not derived from `AMOUNT_MAX_CENTS` or the rate ceilings. It silently assumes every caller's ceiling has at most 9 whole digits.
- **Fix:** The orchestrator rules on one of two options. (a) Keep the cap as defence in depth, and rewrite spec.md:236 and the test title to claim only what the case proves ("401 digits are invalid and do not throw"). (b) Drop the cap as dead defensive code (KISS) together with that threat-model sentence. In both cases reword money.js:13 to "no nested quantifier, so matching stays linear in the input length".

### WR-07: The hygiene gate does not enforce two declared non-goals, so a float plus locale `formatMoney` passes every test   (gate weaker than BUILD.md claims)
- **File:** tests/hygiene.test.js:10-13. spec.md:140 (R25 list). spec.md:245 and :249 (non-goals). BUILD.md:47-48.
- **Issue:** Mutant M09 rewrites `formatMoney` as `(cents / 100).toLocaleString("en", { minimumFractionDigits: 2, maximumFractionDigits: 2, useGrouping: false })` and survives all 185 tests. That breaks the non-goal "no locale-aware number formats" and the invariant "no money calculation passes through floating point", and nothing goes red. Timer APIs (`setTimeout`, `setInterval`, `queueMicrotask`) are not scanned either. BUILD.md:47-48 says the hygiene test "enforces the purity part mechanically", which holds only for the R25 list.
- **Fix:** This needs a spec change, so it goes through the orchestrator. Add `Intl`, `toLocaleString`, `setTimeout`, `setInterval` and `queueMicrotask` to R25 and to `BANNED`, each with a negative-control line in the existing control test. If that is not adopted, narrow BUILD.md:47-48 to "enforces the R25 list".

### WR-08: `formatMoney` and `formatRate` divide in floating point, against the stated invariant and against the module's own remainder-first pattern   (unnamed deviation)
- **File:** src/core/money.js:67 (`Math.floor(cents / 100)`) and :76 (`Math.floor(bp / 100)`). spec.md:16. src/core/allocate.js:24.
- **Issue:** spec.md:16 says "No money calculation passes through floating point. Division is exact integer division." `allocateEvenly` follows this and gives the reason ("amount / count on its own is a float divide"), but both formatters use a float divide. The output is still exact for every safe integer, because a float quotient by 100 cannot round up across an integer below 2^53, so no wrong text is produced. This is an unnamed deviation and an inconsistency inside the module.
- **Fix:** Use `const whole = (cents - (cents % 100)) / 100;` (and the same for `bp`), matching `allocateEvenly`. Otherwise name the deviation in a one-line WHY comment.

### WR-09: The `changeItem` comment is stale, and `toggleItemPerson` looks up the item twice   (doc rot, minor duplication)
- **File:** src/core/bill.js:100 and :117-124.
- **Issue:** "Shared by the two item setters so unknown-id handling lives in one place" is wrong on both counts. There are three callers (`setItemName`, `setItemPriceText`, `toggleItemPerson`), and `toggleItemPerson` does its own unknown-item check (`find`, then `item === undefined`) before `changeItem` repeats it with `some`.
- **Fix:** Reword to "Shared by the item actions: an unknown item id returns the same bill." Either let `toggleItemPerson` check only the person and rely on `changeItem` for the item, or keep the `find` and build the new item directly instead of calling `changeItem`.

### WR-10: Unicode line separators other than CR and LF can forge a summary line   (security-adjacent, spec gap, route to the Security Auditor)
- **File:** src/core/summary.js:4-6 (relies on the invariant). spec.md:19 and :237.
- **Issue:** The invariant covers only U+000A and U+000D, and `<input type="text">` strips only those two. U+2028, U+2029 and U+0085 pass through `personLabel` (`trim` removes them only at the ends) into `summaryText`. In probe P8, the name "Chen" + U+2028 + "Adds up to RM 0.00" yields a summary that renders as a forged `Adds up to RM 0.00` line in any chat client that treats U+2028 as a line break. The code matches the spec. The threat model's mitigation is what is incomplete.
- **Fix:** This needs an orchestrator ruling with the Security Auditor. Either widen the invariant to every line terminator (U+000A, U+000D, U+0085, U+2028, U+2029), enforced by split-app's input handler and draft decoder, or have `summaryText` replace them with a space (which is a spec change to R24), or record the residual risk in spec.md's threat model.

## Checked and clean
- **Reverse audit.** Every export matches the Contracts table exactly (grep of `^export` in src/core). Every module-private helper serves an R#. No exported symbol lacks an R#. All test titles carry R# tags. No non-goal was built (no payments, Intl, cash rounding, extra charges, history, DOM, storage or timers).
- **Money rules.** Half-up rounding (`applyRate`, floor((n + 5000) / 10000) in exact integers). SST on subtotal plus service. Even leftover sen go to the top of the list. Item leftover sen follow people-list order, not tap order. Charges leftover sen go to the lowest index with a positive weight. MAX-E and MAX-I are exact. Mutants M02 (truncate), M03 (SST on subtotal), M05 (tap order), M06 (leftover to zero weights), M10 and M15 (larger shares last) are all killed.
- **Parsing (P7).** NBSP and trailing LF are trimmed (spec says `String.prototype.trim`). "0." is invalid as an amount and 0 bp as a rate. "." is invalid. "00.5" gives 50. A million leading zeros then "1" gives 100. Arabic-Indic and full-width digits, "1_000", "12.5 0" and "+0" are invalid. "099999.99" gives 9999999. Ten nines are invalid. Tab alone counts as empty. All of these follow the R1 grammar.
- **Input mutation.** Every bill action and `computeResult` passes on deep-frozen input (see WR-05 for the uncovered functions).
- **The five accepted judgment calls behave as BUILD.md says.** (1) `setPersonName`, `setItemName` and `setItemPriceText` return the same reference for an unknown id (tests/bill.test.js:135-139). (2) `itemResult` counts an item as unassigned when `holderIndexes` is empty (result.js:87-88), not when `who` is empty. (3) tests/support/rng.js and bills.js are not matched by the `*.test.js` glob. (4) No qa/unit evidence file exists. (5) There is no package.json, Node 24 detected ESM with no MODULE_TYPELESS warning, and no package.json exists in any parent directory up to D:/.
- **Comment rule.** No comment narrates WHAT. The two inline comments in allocate.js (:24, :43) are WHY comments for code that looks unusual. No `file:line` citations appear in source comments.

## Notes for other owners (not findings against this module)
- **split-app.** `computeResult` treats any mode other than "even" as by-item (P6: mode "bogus" returns `blocked/no-items`). The split-app draft decoder must reject an unknown `mode`, as the `Mode` type assumes.
- **Process disclosure.** The baseline run output `node-test.txt` was written with a shell `>` redirect. That breaks constitution §Filesystem safety, which says writes go through the Write tool. The file was checked afterwards: it landed at the intended path, and no stray files exist in the project root or at D:/c or D:/d. All other evidence was written with the Write tool or by Node `fs` using `D:/` forward-slash paths, and each landing was checked with `ls` and `git status`. Throwaway copies of the scripts live in the session scratchpad. `git status` shows only `docs/modules/split-core/qa/` untracked plus the orchestrator's own three modified progress files. No source file was touched.

## Solver (2026-10-09)
Role: dev solver for split-core, working to the orchestrator rulings of 2026-10-09 (ORCH). This section is appended. The verdict above is the finder's and is unchanged. Spec and qa corrections are dated, additive notes with the old wording kept visible (struck through where it was false).

**Result: 10 of 10 RESOLVED, 0 STILL-OPEN.** The suite was 185 of 185 at `67e4b6e` and is now **tests 212, pass 212, fail 0** at `46f5670` (Node v24.11.1).

Evidence is in `docs/modules/split-core/qa/solver/20261009-121000/`. The reviewer's folder was not touched.
- `node-test.txt` holds the full suite run at HEAD.
- `per-commit-summary.txt` rebuilds each of the 12 solver commits from `git show` and runs it. Every commit is green on its own: 187, 187, 199, 200, 203, 203, 204, 204, 204, 212, 212, 212 tests, 0 failures.
- `mutation-summary.json` and `mutants/S01..S28, S11c/` hold the mutation copies, with test files renamed `*.mutcase.js`. A mutant counts as KILLED only when every test it targets fails. **28 of 28 KILLED.** The S11c control survives, as designed. The scripts are in `scripts/` (`mutate.mjs`, `per-commit.mjs`, `run-suite.mjs`).

| WR | Status | Commit | What changed | How it was verified |
|---|---|---|---|---|
| WR-01 | RESOLVED | `170a293` | Retitled both MAX-I tests to what they prove and deleted the false comment. Tagged the R8 trap row `BigInt trap:`. Added two **reachable** trap rows: 61846725 over [49676084, 322894546] is the charges total of a 372570630 subtotal at 10% and 6%, and 178450942 over [111531837, 207130558] is the charges total of a 318662395 subtotal at 30% and 20%. Each trap test now also asserts that a float allocator misses its row. Corrected the `allocateByWeight` comment, spec R8 (row wording plus a dated note), R23, the threat model row, and the qa.md R8 cases. | S01 (the reviewer's M04: float product and float divide) and S02 (float product, then exact divide) each fail **all three** trap rows, so the guard is no longer one row. Search: 2,000,000 random inputs found nothing (the reviewer's traps.mjs). Solving a x w = -r (mod W) for small r found hundreds of divergences, and every one has a product above 2^53. Side finding: the original 236419679 row is a valid allocator input, but no valid rate pair produces it from its weights. The new rows are reachable bills. |
| WR-02 | RESOLVED | `16ca008` | `applyRate` JSDoc now gives the measured maximum, the service step 499,999,950 x 3000 (about 1.5e12). Spec Invariants now say charges x weight reaches about 1.4e17 (279,999,972 x 499,999,950). BUILD.md points to the `applyRate`, `allocateByWeight` and `allocateEvenly` comments instead of restating them. The `readHundredths` and `bill.js` restatements were fixed under WR-06 and WR-03. | Numbers recomputed with BigInt. 1,499,999,850,000 > 1,299,999,870,000, both below 2^53. 1.400e17 and 1.400e16. Suite green. |
| WR-03 | RESOLVED | `0a998f0` | The `bill.js` module header now states the true scope. The Bill and the changed person or item are rebuilt, untouched people and items are shared, and cleaning a parsed bill is split-app's draft decoder's job. The BUILD.md bullet was struck and points to the header. The masked composition test was replaced by 13 tests (`@R16 <action> on a parsed bill builds only known fields`). Each runs one action directly on a parsed bill with stray and own `__proto__` keys on the bill, a person and an item, and checks the rebuilt person or item. | S03 (the reviewer's M12, `setMode` spreads the bill) is KILLED. S04 (`itemWith` spreads the item) fails exactly the 4 item tests. S05 (the reviewer's M11) is KILLED. |
| WR-04 | RESOLVED | `64388f8` | Added `@R11 a new person's id comes from nextId, so it never reuses a removed id`, plus a dated qa.md scenario. | S06 (the reviewer's M07, id from list length) is KILLED. |
| WR-05 | RESOLVED | `ded51ae` | Every named fixture in `tests/support/bills.js` is deep-frozen through one `fixture` helper. New R16 tests cover `summaryText` (deep-frozen S1 and S2 results), `personLabel` and `itemLabel` (frozen person and item) and `allocateByWeight` (frozen weights). There is a dated qa.md scenario. | S07 (the reviewer's M08), S08 (weights reversed and back), S09 and S10 (labels write back) are KILLED. S11 (`computeResult` writes to a MAX-I bill and restores it) is KILLED **only** through the frozen fixture. Control S11c, the same mutant with fixtures unfrozen, survives. |
| WR-06 | RESOLVED | `858dfca` | Removed the magic `MAX_WHOLE_DIGITS`. `readHundredths(text, maxHundredths)` now takes the caller's ceiling (`AMOUNT_MAX_CENTS` or `maxPercent` x 100), derives the digit cap from it (the derivation is stated once, in its comment) and does the ceiling check itself. `parseAmount` keeps only the minimum check. The regex comment now claims linear matching, not "cannot backtrack". New test: `@R1 @R3 a whole part longer than the ceiling's is refused before any numeric conversion` spies on the global `Number`, with positive controls. The old 401-character test was retitled to what it proves. Spec threat row and qa.md got dated notes. | S12 (cap removed, the reviewer's M01), S13 (cap back to 9) and S14 (cap from the amount ceiling only) are KILLED. A differential check of the old and new parsers over 200,031 inputs with ceilings 0, 1, 20, 30, 99, 100 and 1000 (1.6M comparisons) found 0 differences. |
| WR-07 | RESOLVED | `d8cf735` | `BANNED` in `tests/hygiene.test.js` adds `Intl`, `toLocaleString`, `toLocaleDateString`, `setTimeout`, `setInterval` and `requestAnimationFrame`. The negative control flags all six in a planted line, and a positive control keeps `setTimeoutMs` and "locale-independent" green. Spec R25, qa.md and BUILD.md were narrowed to "enforces the R25 list", all dated. `queueMicrotask` was not added (not in the ruling). | S15 (the reviewer's M09, float plus `toLocaleString`) and S16 (`Intl.NumberFormat`) are KILLED. S17 to S20 plant one name each into a different core file and each is KILLED by that file's scan. |
| WR-08 | RESOLVED | `75cca79` | `formatMoney` and `formatRate` use a private `wholePart(hundredths)` that divides remainder first. No `Math.floor` is left in `src/core/`. | Output is unchanged. R4 and R5 are green, and `formatMoney` matches a BigInt reference at 0, 99, 101, 9999999, 779999922, 2^53 - 1 and other values. No test changed, so no mutant was needed. |
| WR-09 | RESOLVED | `34797ce` | `changeItem(bill, itemId, changesFor)` now takes the new fields as a function of the current item, and its comment names all item actions. `toggleItemPerson` checks only the person, and the item is looked up once, in `changeItem`. | R14 tests green. A differential random walk of the old and new `bill.js` over 120,000 action steps found 0 differences in results and in same-reference returns. |
| WR-10 | RESOLVED | `db3bd35`, `46f5670` | `summaryText` replaces each of LF, CR, VT, FF, NEL (U+0085), LS (U+2028) and PS (U+2029) in a row name with one space. These seven are the mandatory breaks of Unicode line breaking (UAX #14). One test per character plus a by-item case. Spec R24, the name invariant and the threat model row got dated notes, and qa.md got a scenario outline. Rows carry person labels only, because item labels never appear in the summary. | S21 (no replacement) fails all 8 tests. S22 to S28 each drop one character from the class and each fails exactly that character's test (LS also fails the by-item case). |

`74ab714` adds the dated test-count note to BUILD.md.

**Process notes.**
- The Edit transport turned the escape text for U+2028 and U+2029 into raw characters, which broke a regex literal for one uncommitted run. It was fixed by writing those two as `\u{2028}` and `\u{2029}` (with the `u` flag in regexes). Every touched file was then scanned for raw line terminators, and none remain.
- All writes used the Write and Edit tools or Node `fs` with `D:/` forward-slash paths. Nothing landed in the project root or at `D:/c` or `D:/d`.
- This findings file and both evidence folders are left untracked for the orchestrator to commit, like the reviewer's evidence.

**Routed, not fixed here (split-app owners).**
- The draft decoder must reject an unknown `mode`, because `computeResult` treats any mode other than "even" as by-item.
- The draft decoder must rebuild or reject people and items that carry unknown or `__proto__` keys (WR-03 scope).
- Consider rejecting VT, FF, NEL, LS and PS in names, so the screen matches the summary text.

## Re-check (2026-10-09)
Role: code-review finder (read-only). The finder verdict, WR-01 to WR-10 and the solver section above are kept as written. The front matter is unchanged on purpose (additive only), so its counts are the round 1 counts. The counts for this re-check are in this section.
Scope: `git diff 67e4b6e..HEAD -- src tests` at HEAD `c655a94`. That is the WR-01 to WR-10 solver round (`170a293` to `46f5670`), security round 1 (`b3b43fe`, `a09ce03`, `b5b448d`, `e56b396`) and security round 2 (`fedaa7a`, `5d5d02a`, `4e2740b`). By the ORCH stop rule this is also the verification of security round 2. There is no third security round.
Judged against spec.md (R1 to R26, Contracts, Non-goals, threat model), qa.md, BUILD.md, constitution.md and CLAUDE.md.

**Verdict: PASS. 0 BLOCKER, 5 WARNING (WR-11 to WR-15).**
- All ten WR items are resolved, with no spec-less code and no new defect. The three refactors that touch behaviour (WR-06, WR-08, WR-09) are identical to the old code over 1.77M parse and format comparisons and 120,000 action steps.
- Security round 1 (SEC-01 to SEC-04) and the SEC-06 and wording items of round 2 are correct and minimal. SEC-05 (the runtime trap) is correct for every access that runs, flake free, and it catches all 12 of the auditor's plants. Its limits are in WR-12 and WR-13.
- The warnings are about how firmly the new guards and docs hold the line, not about a wrong result. Three mutants of the SEC-01 regex pass all 246 tests (WR-11). Thirty-seven of 42 traps can be deleted with the suite staying green, and `globalThis` was never trapped (WR-12). Two spec claims go further than the code (WR-13, WR-14).
- No wrong money result, no hallucinated code, no non-goal built, no contract drift. The 26 exports equal the Contracts table, core imports only core, `docs/design/` is untouched, no commit carries a vendor watermark, and no source or test file holds a control character, bidi control, separator or long dash.

Evidence: `docs/modules/split-core/qa/code-review/20261009-134620/` (`INDEX.txt` lists the files and the process accounting).
- Baseline `node --test "tests/**/*.test.js"` on Node v24.11.1: **tests 246, pass 246, fail 0**, exit 0 (`node-test.txt`).
- The 19 commits from `170a293` to HEAD (17 of them change `src/` or `tests/`), rebuilt from `git archive` and run, are green with the solver's own counts (`per-commit-summary.txt`).
- 96 in-memory mutants: no file under `src/` or `tests/` was written (`mutation-summary.txt`, `probe-output.txt`, `scripts/`). The surviving ones that matter are named in the findings below.

### 1. Do the WR fixes resolve their warnings?
| WR | Result | Checked how |
|---|---|---|
| WR-01 | Resolved | The three trap rows were recomputed with BigInt and with a float allocator. The float result misses every row (236419679, 61846725, 178450942), and every product passes 2^53. The two new subtotals (372570630, 318662395) are below 499,999,950, so they are real bills. No false MAX-I claim is left in src, tests, spec or qa (grep). Old wording is struck and dated. |
| WR-02 | Resolved | 499,999,950 x 3000 = 1,499,999,850,000 is above 649,999,935 x 2000 = 1,299,999,870,000. 279,999,972 x 499,999,950 is about 1.4e17. BUILD.md points to the comments. |
| WR-03 | Resolved | The `bill.js` header is true (Bill, changed person and item rebuilt, the rest shared). The 13 per-action tests run each action on the parsed bill itself. A spread would add an own `__proto__` key and fail `Object.keys`. |
| WR-04 | Resolved | The new test fails when the id comes from the list length. |
| WR-05 | Resolved | `fixture` deep-freezes every named bill. R16 tests cover `summaryText`, both labels and `allocateByWeight`. |
| WR-06 | Resolved | W01 (cap one digit looser) and W02 (cap from the cents text) are killed by the `Number` spy test. The old and new parsers agree on 171,416 strings at 7 ceilings. No magic 9 is left. |
| WR-07 | Resolved, then widened | `BANNED` has the six names with a negative control. SEC-04 later added the code-only list. |
| WR-08 | Resolved | `wholePart` matches the old output on 0 to 200000 and six large values up to 2^53 - 1. W03 (back to `Math.floor`) is an equivalent mutant, so nothing can pin it. No `Math.floor` is left in `src/core/`. |
| WR-09 | Resolved | R1 (drop the person check) is killed by the R14 test. The old and new `bill.js` agree over 120,000 steps, values and same-reference returns. The JSDoc names all three callers. |
| WR-10 | Resolved, superseded | `summaryText` now replaces the whole class (SEC-01, SEC-02). Rows carry person labels only, which is true. |

Rows WR-03, WR-04, WR-05 and WR-10 also rest on the solver's mutants S03 to S11 and S21 to S28, which I read but did not re-run. Everything else in the table I re-ran or recomputed here.

### 2. Security rounds 1 and 2
- **SEC-01, SEC-02.** `CONTROLS` (`src/core/summary.js:8`) is exactly `[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]` and is applied at :28. The class matches 79 code points. P04 (no `Bidi_Control`), P05 (C1 range let through), P06 (`\p{Zs}`), P07 (U+1F600), P09 (`\p{Cn}`), P10 (`\p{Co}`), P11 (`\p{Cf}`), P08 and P12 (wrong replacement) are all killed. The `u` flag is needed (P13 killed).
- **SEC-03.** The two accepted residuals in spec.md match `personLabel`, which keeps NEL, U+200B, U+2800 and U+3164 as a non-blank name. Doc only.
- **SEC-04.** The code-only scan is a secondary guard. It has no false hit on the five real files, and its plants (`CODE_PLANTS`) go red in every file.
- **SEC-05, the runtime trap in `tests/hygiene.test.js`.**
  - Attribution is sound for what it claims. A hit counts when a stack line holds the core URL (`CORE_URL`, `record` at :261). The module URL is what V8 prints for a frame, so a plant in any of the 5 files is attributed (12 plant tests x 5 files). Core never receives a test callback and never calls back into test code, so a core frame cannot sit above a test-code access. The third negative-control assertion shows test code is not counted (B4, which counts everything, is killed).
  - The trap machinery fails when broken: B1 (no recorder for crypto), B2 (none for `toFixed`), B3 (no core frame ever found), B4, B5 (never armed) and B8 (hits not cleared) are all killed.
  - `//# sourceURL=` cannot hide an access silently. H05a: the clean run is fooled, but the negative control and all 12 F tests plant into the same file, see nothing, and go red.
  - A new export the workload never calls goes red by name (H06, the `unexercised` check at :394).
  - Flake: none found. The test has no timers and no order dependence beyond its own file. Ten runs alone and ten variants were green (`--test-isolation=none`, `--test-concurrency=1`, coverage, `--enable-source-maps`, `--jitless`, `--always-turbofan`, `--no-opt`, `--stack-trace-limit=2`, run directly, run from another directory). It needs `module.registerHooks` (Node 22.15, 23.5 and later), so on an older Node it fails loudly at import, never passes by accident. Only Node 24.11.1 is installed here, so no other 24.x or newer line was run.
  - False pass paths that exist are WR-12 and WR-13.
  - `codeOnly` is labelled best-effort at file level (`tests/hygiene.test.js:10-12`), and spec R25 lists its known limits. The label cites a finding id and `codeOnly` itself is silent, see WR-15.
- **SEC-06, the property tests.** They pin which code points are replaced exactly (79, up to U+2069, and "as typed" above it, surrogate halves excluded). They run in 26 ms and 105 ms, which is acceptable. They do not pin how many occurrences are replaced, see WR-11. The oracle (`R24_CLASS`, `tests/summary.test.js:128`) is the same class expression as the code, so it is not independent of a wrong class. The count 79 and the spec text are what pin it, and that is adequate.
- **Wording item.** spec.md:19 and the `summaryText` JSDoc give the exact class and say NBSP and U+3000 are kept. True.

### 3. Docs against code
- Dated notes everywhere. A word-diff of spec.md, qa.md and BUILD.md against `67e4b6e` shows removed words only where they come back inside `~~ ~~`, plus one qa.md scenario title whose old wording is quoted in the new dated comment. Nothing was rewritten silently.
- spec R24, line 19, the Clipboard threat row, the two residuals and the R8 and R23 notes match the code.
- Mismatches: R25 and qa.md over-claim (WR-12, WR-13). BUILD.md and spec Task 8 are stale (WR-14). No README exists for the module, so there is nothing to reconcile there.

## BLOCKER (re-check)
None.

## WARNING (re-check)

### WR-11: The SEC-06 property tests pin which code points are replaced, not that every one in a name is   (test gap on the SEC-01 guard)
- **File:** tests/summary.test.js:132-144 (one character per name, built at :139) and :146-155 (a name with no class member). Code under test: src/core/summary.js:8 (`CONTROLS`, flags `gu`) and :28.
- **Issue:** Three mutants of `CONTROLS`, served in memory, pass all 246 tests (the whole suite, with the mutation seen applied):
  - P01 drops the `g` flag. `A` NUL `B` NUL `C` keeps its second NUL (`probe-output.txt`). A NUL ends a C-string clipboard, which is the SEC-01 threat itself.
  - P02 adds `+`. Two adjacent NULs print as one space, against R24 "each ... one space".
  - P03 adds `\p{Cs}`. A lone surrogate becomes a space, which is outside the class.
  - Cause: no test has two replaceable characters in one name, and the second property test leaves surrogate halves out. The solver's mutants S21 to S28 and the auditor's three narrowing mutants did not try these shapes. "Pin the whole class" holds for membership only.
- **Fix:** Add two tests (written as `X00` in `scripts/mutants-fix.mjs`, served in memory):
  ```js
  test("@R24 every replaceable character in one name is replaced, one space each", () => {
    const members = [];
    for (let cp = 0; cp <= 0x2069; cp += 1) if (R24_CLASS.test(String.fromCodePoint(cp))) members.push(String.fromCodePoint(cp));
    const rowOf = (name) => summaryText(computeResult(setPersonName(S2, "p3", name))).split("\n")[4];
    assert.equal(rowOf("A" + members.join("") + "B"), "A" + " ".repeat(members.length) + "B RM 38.86");
    assert.equal(rowOf("A" + members.join("x") + "B"), "A" + members.map(() => " ").join("x") + "B RM 38.86");
  });
  test("@R24 a lone surrogate prints as typed", () => {
    const lone = [];
    for (let unit = 0xd800; unit <= 0xdfff; unit += 1) lone.push(String.fromCharCode(unit));
    const name = "A" + lone.join("x") + "B";
    assert.equal(summaryText(computeResult(setPersonName(S2, "p3", name))).split("\n")[4], name + " RM 38.86");
  });
  ```
  Proven: green on the real code (X00, 29 of 29 in the file), and red on P01, P02 and P03 (X01 to X03). Add a qa.md scenario with a dated note.

### WR-12: The runtime trap's own lists are not pinned, so a trap can be removed silently, and `globalThis` was never trapped   (control that cannot fail, spec claim false for one name)
- **File:** tests/hygiene.test.js:227-256 (`TRAPPED_GLOBALS`, `TRAPPED_METHODS`, `CONSTRUCTOR_ROUTES`), :398-409 (the negative control builds its cases from those same arrays), :16-21 and :26-37 (`BANNED`, `BANNED_IN_CODE`). spec.md:144 (SEC-05 note) and qa.md:570.
- **Issue:**
  - **(a) Silent narrowing.** Deleting one entry from the three trap lists keeps the suite green in 37 of 42 cases. The 5 that go red (`Function`, `performance`, `process`, `Date`, the Function constructor route) are the ones an F plant happens to use. The negative control iterates the same arrays, so a deleted trap takes its control with it. It matters: with the `eval` trap removed, an executed `(0, \u{65}val)("1")` passes everything (H08a), and with the trap in place the same line fails (H08b). The same holds for `fetch` (H08c, H08d).
  - **(b) `globalThis` is not trapped.** R25 bans `globalThis` and `BANNED` has it, but `TRAPPED_GLOBALS` does not. H04a: `const g = \u{67}lobalThis;` at module top level passes all 39 hygiene tests (the scan misses the escape and nothing traps it). So "It replaces every banned global" (spec.md:144) and "recorders on every banned global" (qa.md:570) are false for that name.
  - **(c) Plumbing is unpinned.** With the restore loop off (B6, :297-300), with the run id not carried onto core-to-core imports (B7, :313-318) or with one run id for every import (B9, :334-337), the suite stays green. "A fresh copy of the whole core whatever loaded it before" is claimed and never tested, because nothing loads the core earlier or twice.
  - **(d) Four copies of one list.** `BANNED`, `BANNED_IN_CODE`, the three trap lists and spec R25 describe the same set with nothing tying them together. They have already drifted (`globalThis`; `EventSource` and `indexedDB` are trapped but not banned).
- **Fix:** Add `"globalThis"` to `TRAPPED_GLOBALS`. Add a pin test that lists the names R25 bans and checks each is in a trap list (written as `Y0` in `scripts/mutants-fix.mjs`):
  ```js
  test("@R25 the runtime trap lists cover every name R25 bans", () => {
    const have = new Set([...TRAPPED_GLOBALS, ...TRAPPED_METHODS.map(([label]) => label), ...CONSTRUCTOR_ROUTES.map(([label]) => label)]);
    assert.deepEqual([...MUST_TRAP, ...MUST_TRAP_OTHER].filter((name) => !have.has(name)), []);
  });
  ```
  Proven in memory: red on the current code (the missing `globalThis`, Y0), green once `globalThis` is added (Y1), the escaped `globalThis` plant then fails (Y2), and the `eval` and `Date.now` removals fail (Y3, Y4). The pin is only as wide as its list (Y5), so list all four constructor routes and the whole `toLocale*` family. Better, keep one table of banned names that feeds `BANNED`, `BANNED_IN_CODE` and the trap lists. For (c), call `importCore()` twice and assert `notEqual(first.money, second.money)`, or delete the propagation line in the resolve hook if no test needs it (KISS).

### WR-13: The docs say the trap catches all of the scan's blind spots. It only sees code that runs   (claim in spec and qa goes further than the code)
- **File:** spec.md:144 (last sentence of the SEC-05 note, "The trap catches all of these."). qa.md:567-575. tests/hygiene.test.js:10-12 ("whatever the syntax") and :385 (the title).
- **Issue:** H02 puts the scan's first blind spot, postfix `++` then `/ process.uptime()`, inside a branch no export call takes (`formatRate`, `bp > 1e12`). The scan misreads the slash and the trap never runs the line, so all 39 tests pass. The plain-name twin (H03, `Date.now()` in the same branch) is caught by the scan only. `runEveryExport` proves each export is called (`unexercised`, :394), not each branch. So the guards complement each other: the trap sees any syntax on a path the workload runs, the scan sees every path but only plain names.
- **Fix:** Reword the last sentence of the spec.md R25 note to "The trap catches all of these on any path the workload runs. A branch the workload never takes is covered only by the name scan." Make the same change in qa.md and in the hygiene comment ("whatever the syntax, on the paths the workload runs"). No new code is needed.

### WR-14: Stale numbers and a stale task line in the docs   (doc rot)
- **File:** BUILD.md:18-20. spec.md:233.
- **Issue:** BUILD.md says "tests 185" and then, in a dated note, "tests 212". HEAD runs 246, and the rounds between ran 217, 218, 230 and 244. An absolute count rots with every added test and reads as current. spec.md:233, Task 8, still says "a static scan of `src/core/` for the banned names and foreign imports", but since SEC-05 the primary guard in that file is the runtime trap. R25 carries the dated note and the task line does not.
- **Fix:** In BUILD.md state the stable effect ("`fail 0` on `node --test "tests/**/*.test.js"`, the count is in the run output") and leave the history to the findings files. Add a dated note on the Task 8 line, without rewriting it: "[Changed date, role: the file also holds the runtime trap, the primary guard, see R25.]"

### WR-15: Small maintainability items in the new test code and the summary comments   (doc ownership, DRY, robustness)
- **File and issue:**
  - **(a) The best-effort label.** tests/hygiene.test.js:10-12 calls the scan "best-effort and secondary" (good) but cites "(security SEC-05)", a finding id, and `codeOnly` (:61-65) says nothing about its limits. Point both at "spec R25", which lists them.
  - **(b) Two file lists.** `CORE_FILES` (:225) repeats the literal at :144. A sixth core file fails :144 and then needs a second edit. Derive `CORE_FILES` from `files` (:140).
  - **(c) One class, stated three times.** src/core/summary.js:4-7 (prose), :8 (the regex) and :10-14 (the JSDoc) all give the class. When it changes, three places move. Keep the regex and one prose sentence, and let the JSDoc say "see `CONTROLS`".
  - **(d) A bare 79.** tests/summary.test.js:143 has no derivation. Write the sum beside it: 65 `Cc`, LS, PS and 12 `Bidi_Control`.
  - **(e) Hits leak after a failure.** tests/hygiene.test.js:272-303 (`trapped`): when `body` throws, `hits.splice(0)` at :302 is skipped, so the next trapped run returns the earlier run's hits and a negative control could pass on leaked evidence. Probe Z1 shows it. The same applies to :261-270, where `recording` stays true if reading `.stack` ever threw. Take the hits in the `finally` block (Z2 is green with that change) and reset `recording` there too.
- **Fix:** As listed in each bullet. All are small and none changes behaviour.

## Checked and clean (re-check)
- **Reverse audit.** Each changed function maps to an R#. `wholePart` serves R1, R3, R4, R5 (WR-06, WR-08). `CONTROLS` serves R24. The trap, the scan and the plants serve R25 (SEC-04, SEC-05). `fixture`, `floatAllocate` and `conversionsDuring` serve R16, R8 and R1/R3. No unused import, helper or constant (`scripts/unused.mjs`). No export outside the Contracts table. No non-goal built.
- **Hostile bits that were tried and held.** The `//# sourceURL=` trick is caught indirectly (above). A new unexercised export goes red. Breaking the attribution, a recorder, the arming or the clearing goes red. The commit-by-commit suite is green, so each commit leaves the tree working.
- **Process.** The sweep after the run found no `node`, `python` or `chrome` process. See `INDEX.txt`.

## Notes for other owners (re-check)
- **Routing.** WR-11 to WR-15 are test and doc changes for the Dev Solver. They touch the guards that security round 2 added, but they are code-review items, so the stop rule on a third security round is not engaged.
- **split-app.** Nothing new. The routed items from the first round and from the security audit stand (unknown `mode`, unknown or `__proto__` keys on people and items, reject controls and bidi controls in names so the screen matches the summary).
- **Process disclosure.** All evidence was written with the Write tool. No shell redirect or heredoc was used. Mutants were served in memory and the commit rebuilds ran in the session scratchpad, outside the project.

## Solver (re-check, 2026-10-09)
Role: dev solver for split-core, working to the orchestrator rulings of 2026-10-09 (ORCH, reversible). This section is appended. The finder's verdict, WR-01 to WR-15 and the earlier solver section are unchanged. Spec, qa and BUILD corrections are dated, additive notes with the old wording kept visible (struck through where it was false). By the ORCH stop rule there is no further code-review round, and the QA finder runs next.

**Result: 5 of 5 RESOLVED, 0 STILL-OPEN.** The suite was 246 of 246 at `bd7282c` and is now **tests 254, pass 254, fail 0** at `6edc1b6` (Node v24.11.1).

Evidence is in `docs/modules/split-core/qa/solver/20261009-141136/`, and `INDEX.txt` there lists every file and the process accounting. The reviewer's folder was not touched, and the mutants import its `mutants.mjs`.
- `per-commit-summary.txt` rebuilds the start HEAD and each of the 5 fix commits from `git archive` and runs the suite in each. Every tree is green: 246, 248, 252, 252, 252 and 254 tests, 0 failures.
- `mutation-final.txt` runs every mutant of the round against the final code (`scripts/mutants.mjs` reuses the reviewer's P, N, H and B mutants and adds the ones whose anchor moved or that are new). A mutant counts as KILLED only when its `MUT-APPLIED` marker was seen. 81 of 85 are killed. The 4 survivors are the identity controls H00 and P00, H02 (the documented WR-13 limit) and B7 (below).
- `flake-runs.txt`: the hygiene file 10 times alone, the full suite under `--test-isolation=none`, `--test-concurrency=1`, coverage, `--enable-source-maps`, `--stack-trace-limit=2` and `--jitless`, and the hygiene file run directly. All green.

| WR | Status | Commit | What changed | Red and green proof |
|---|---|---|---|---|
| WR-11 | RESOLVED | `28c67ed` | `tests/summary.test.js` gets two tests. One puts every member of the class in a single name, adjacent and then separated by `x`, and expects one space per member. The other puts every lone surrogate (U+D800 to U+DFFF, separated by `x`) in a name and expects it to print as typed. `R24_MEMBERS` is built once from the oracle. The comment above the property tests now says the first two pin membership and the new two pin the count of replacements. `qa.md` gets two dated scenarios. | Before (`wr11-before.txt`): P01, P02 and P03 all survive the old 27 tests. After (`wr11-after.txt`): P01 and P02 are killed by exactly `@R24 every member of the class in one name is replaced, one space each`, P03 by exactly `@R24 a lone surrogate is not in the class, so it prints as typed`. P00 (no edit) stays green with 29 of 29, and P04 to P14 are still killed. |
| WR-12 | RESOLVED | `6ec63fb` | `"globalThis"` is in `TRAPPED_GLOBALS`. A pin test names every entry of the three trap lists (compared sorted, so a reorder is not a failure). A second test derives, from `BANNED` and `BANNED_IN_CODE` themselves, that every banned name has a trap (`import(` is syntax and is the one named exception), so the lists cannot drift apart silently again. Two small tests: every trap site is put back after a run, also after a body that throws (`trapSites`, `changedSince`), and two `importCore()` calls give different namespaces. `spec.md` R25 and `qa.md` get dated notes. | Before (`wr12-before.txt`): 37 of the reviewer's 42 narrowing mutants survive, and so do H04a (the escaped `globalThis` plant), H08a and H08c (a dropped trap plus the access), B6 (no restore) and B9 (one run id). After (`wr12-after.txt`): all 42 plus N-G25 (the new `globalThis` trap dropped) are killed by the pin. H04a, H08a and H08c are killed. B6 and RS1 (restore only on success) are killed by the restore test, B9 by the fresh-copy test, D1 (a name added to `BANNED` with no trap) by the derived test and D2 (a trap added and not pinned) by the pin. |
| WR-13 | RESOLVED | `7c4e896` | `spec.md` R25: the sentence "The trap catches all of these." is struck and a dated change says what the trap sees (any syntax, on any path the workload runs; the workload is `runEveryExport`, which proves each export runs and not each branch) and what only the name scan sees. `qa.md`: the scenario title says "while every export runs", with the old title quoted in a dated comment, plus a dated note. `tests/hygiene.test.js`: the header comment and the title of the trap test say the same. | Docs and one title, no behaviour. `wr13-demo.txt`: H02 (a postfix `++` then `/ process.uptime()` in a branch the workload never takes) still passes everything, which the docs now say. H03 (a plain `Date.now()` in the same branch) is caught by the scan only. |
| WR-14 | RESOLVED | `93b9c48` | `BUILD.md`: both absolute counts (185 and 212) are struck, and a dated note states the stable effect, `fail 0` on `node --test "tests/**/*.test.js"`, with the count left to the run output and the findings files. `spec.md` Task 8 keeps its text and gets a dated note: "a static scan" is now the runtime trap plus the scan. | Docs only. A grep of `BUILD.md`, `qa.md` and `spec.md` finds no absolute test count outside a struck-through span. |
| WR-15 | RESOLVED | `6edc1b6` | (a) The header comment and `codeOnly` point at "spec R25" for the scan's limits instead of a finding id. (b) `CORE_FILES` is the one list read from `src/core/`, the literal is gone, and the "scan sees the core files" test still pins the five names. (c) `summary.js` states the class once, in `CONTROLS`. The comment above it gives the why, and the JSDoc says "each character that `CONTROLS` matches". (d) The bare 79 is `R24_CLASS_SIZE = 65 + 2 + 12` with the three terms named. (e) `trapped` takes its hits in `finally` and `record` resets `recording` and the stack trace limit in `finally`. Two new tests cover (e). `qa.md` lists them. | (e) before the fix (`wr15e-red-before-fix.txt`): both new tests red. After: green. L1 (hits taken after the try again) is killed by exactly the leak test and L2 (no `finally` in `record`) by exactly the stuck-recorder test. The machinery mutants B1 to B9 are killed except B7. The class size was recounted from Unicode: 65 `Cc`, 1 `Zl`, 1 `Zp`, 12 `Bidi_Control`, 79 in the union. P04 to P14 are still killed. |

**Left as is, for the orchestrator.**
- **B7 is an equivalent mutant.** Removing the run id from core-to-core imports in the resolve hook keeps every hygiene test green, and I found no input that tells it apart. Every core file is also imported directly with the run id, so the unversioned copy B7 creates is never the one a verdict reads. The finding gave two options for WR-12(c), a test or deletion. ORCH ruled only on the restore loop, so the propagation line stays. Deleting it (KISS) would also mean dropping the sentence in the hygiene comment that says the run id rides on every core import. Orchestrator's call.
- **One table of banned names (WR-12(d), "better") was not built.** ORCH did not rule it. The pin repeats the lists on purpose (it is a golden), and the derived test ties the scan's lists to the traps. `EventSource` and `indexedDB` are trapped and not banned, which is harmless.
- **H02 passes every guard.** It is the limit WR-13 now documents, not a regression.

**For the README reconcile (comments I own).** No README exists for the module. If one is written, these are the changes since the last round: `tests/summary.test.js` has `R24_MEMBERS`, `R24_CLASS_SIZE` and `summaryFor`. `tests/hygiene.test.js` has `CORE_FILES` (derived), `globalThis` in `TRAPPED_GLOBALS`, the pin test, the derived-coverage test, `trapSites` and `changedSince`, and `trapped` returns the hits it took in `finally`. `src/core/summary.js` changed comments only, and no export or behaviour changed.

**Process notes.**
- Every write used the Write and Edit tools. The evidence files were written by Node `fs` or by the Node test reporter's `--test-reporter-destination` option, with paths relative to the project root. No shell redirect and no heredoc was used. The added lines of every commit were scanned and hold only ASCII, with no control character and no dash. No `\u` escape was written this round.
- The commit rebuilds ran in the session scratchpad, outside the project. Nothing landed in the project root or at `D:/c` or `D:/d`.
- This findings section and the evidence folder are left uncommitted for the orchestrator, like the earlier solver round. The three modified progress and ledger files were not touched.
- `docs/design/` was not touched.
- Every process was a foreground child that exited. The final sweep (image names and command lines) found none alive. See `INDEX.txt`.
