# Handoff. Split v1.1.0 execute, task A18 (cross-cutting checks in both engines), resume at the proof runs

Written 2026-10-15 by the frontend developer role, who stopped at about 40 percent of its context as the A18 brief asks. Read `docs/progress/handoff/handoff-2026-10-15-execute-split-A18.md` (with its section of 18:24) and the A18 brief first, then this file, then `docs/modules/split-app/BUILD.md`, section "v1.1.0 task A18".

## Done
- Every A18 scenario is a test, committed in `101e842` (`feat(split-app): the cross-cutting checks of v1.1.0 written as tests in both engines ... (task A18, R32, R35, R36, R37, R38, R39, R50, R52, R54, R55, R59, R60)`). Tests only, no file under `src/` or `index.html` changed, so the design row was not loaded (declared in BUILD.md).
- The 15 `task A18` xfails are rewritten to their v1.1.0 scenarios, and the three scenarios of 2026-10-15 (`@R50` F-A12-1, `@R52` F-A13-1, `@R54` F-A15-1) are written. 17 test functions, 88 cases, listed by name in the BUILD.md table. `MAX_E` and `MAX_I` are new in `tests/browser/seeds.py`.
- Every A18 scenario passed on the tree of `a7cfe0e` (`qa/functional/20261015-184457-chromium/`, `-184535-webkit/`, 88 of 88), so each got its RED from stubs put in and taken out with the Edit tool. 15 stubs, every one run in both engines in its own folder, recorded in the BUILD.md stub table with what each line showed. After the last removal `git diff --quiet src/` exit 0 and `grep -rn STUB src/` exit 1, and the commit holds no stub.
- The final test file passed 88 of 88 in each engine (`20261015-185856-chromium/`, `20261015-185933-webkit/`). Seven comments lost a colon after those runs, nothing else.
- BUILD.md has the A18 section (status, tests, RED record, judgment calls, two wording observations for the planner) and the missing `A21 proofs | d905f85` row of the commit table.

## Left, in this order
1. Proof on the committed tree (`101e842` or a later commit that changes no test and no app file). `git diff --quiet HEAD -- src/ tests/ index.html` exit 0 first. One job at a time, never a Chromium job while WebKit runs.
   - Node, `node --test "tests/**/*.test.js"`, expect 379 of 379 (no Node file changed).
   - Chromium full suite. Expect 695 cases, 689 passed, 6 xfailed (the two R40 tests of task A19, 3 cases each), 0 failed, 0 skipped. The suite was 624 cases with 21 xfails, A18 removed 17 cases (the 15 xfails, `test_R36_motion_follows_the_users_setting[reduce]` and `test_R32_the_ring_check_has_teeth`) and added 88.
   - WebKit full suite in the background with a bounded wait (about 7 to 8 minutes now). Expect 695 cases, 688 passed, 1 skipped (the IME test), 6 xfailed, 0 failed.
   - WebKit by id against A21's proof run `docs/modules/split-app/qa/functional/20261015-181625-webkit/`, Chromium by id against `20261015-181252-chromium/`. Expected differences, the 17 removed ids only in the old run and the 88 new ids only in the new run, every one passed. Any other change is a finding.
   - `find src index.html -newermt "<start of the first proof run>"` lists nothing, `git hash-object --no-filters src/system.css` is `bf30ddadb8c756dc5d462243c642c218597ae0ac`.
2. Fill the "Proof on the committed tree" of BUILD.md's A18 section (folders, counts from each `junit.xml`, the by-id comparisons), change its Status line, add the `A18 | 101e842` row to "v1.1.0 commits so far".
3. Tick A18 in `docs/modules/split-app/spec.md` the way A21 was ticked ("[x] ... [Ticked by the A18 proof commit, 2026-10-15 in execute. ...]"), naming the tests and that no app file changed.
4. Credential sweep `--staged`, then the docs commit `docs(split-app): the proof runs of A18 on the committed tree ... (task A18, R32, R35, R36, R37, R38, R39, R50, R52, R54, R55, R59, R60)`, staged by exact path with `git -c core.longpaths=true add`.
5. Write `docs/progress/handoff/handoff-2026-10-15-execute-split-A19.md` for A19 (fidelity gate, Chromium) with the new baselines (the proof folders of step 1, 695 cases, the 6 xfails A19 removes), and return to the orchestrator with the A18 return the brief asks for (commit hashes with `git show --stat`, per item the test id, RED folders and stubs from BUILD.md, the proof counts, PROCESSES).

## Where things are
- Runners in the earlier builder's session scratch folder, `{temp}/claude/{project-id}/34019cfb-f1a7-415f-a7eb-c47e4619e819/scratchpad/split-a18/`. `run_pytest.py <engine> [@file | node ids]` (no `-k`, writes `stdout.txt` into the run folder, prints counts and failing ids, `A18_ALL_MESSAGES=1` prints every failing case), `run_node.py`, `compare_runs.py <old> <new>`, `wait_for_run.py <engine> <after stamp>` (540 s cap), `lines.py <run folders>` (prints each line of a problem-list failure), `sweep.ps1` (read-only process sweep), `a18_all.txt` (the 17 A18 test functions as node ids). A fresh builder copies them into its own scratch folder if that one is gone.
- The A18 tests sit in `tests/browser/test_app.py` under "v1.1.0 task A18", the new R50, R52 and R54 tests beside their families (`SHEET_PICK_AGAIN`, `sheet_draw`).

## Traps
- The tests that check many lines gather problems and assert `not problems` with the list joined by " | ", so a failure names every line. `lines.py` prints them from `junit.xml`.
- WebKit computes some px values with a tail (`48.000008px`), compare numbers within 0.5 px (R59 (1)).
- All earlier traps of the A18 handoff stand (no shell redirection, no pipe after a runner or git, `core.longpaths` for `git add`, clipboard stand-in in every context, headless, never touch `src/system.css` or `docs/design/`).

## Open items carried
- Two wording observations for the planner, in BUILD.md A18 "Findings". BR-02's "44 px tall" is the note's inner height (border box 46 px in the golden and the app). K1-56's `#stripTotal` 24/30 has a 33 px line box with the 14 px "RM", so R60's "one line box tall" is not a 30 px height.
- Every open item of the A18 handoff stands.

## Processes
None of A18's alive at writing. Every pytest run was a foreground child of the runner, bounded at 1800 s, and each exited before its output printed. The probe `probe_input_width.py` ran in the foreground under `timeout 120` and exited. The sweep at return is in the A18 return to the orchestrator.
