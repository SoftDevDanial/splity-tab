# Handoff 2026-10-14, execute v1.1.0 orchestrator (Split and Streaks)

Written by the orchestrator session that ran `sdlc:continue` then `sdlc:execute` for both apps on 2026-10-14. The Streaks copy is `examples/streaks/docs/progress/handoff/handoff-2026-10-14-execute-orchestrator.md` (same text). Resume with `/sdlc:continue` at `{workspace}`.

## Standing rules this run (from the owner and the briefs)
- Owner said 2026-10-14 "Start now, both apps". At most 2 agents at a time across both apps, one lane per app. Usage check before every launch and hand-back (5h stop at 75%, weekly does not stop agents, at 90% tell agents to write files).
- Briefs forbid every shell write (Write and Edit only, `git commit -m`, no heredoc), name exact paths to stage, the credential gate before each commit, no Co-Authored-By or vendor line, never push, headless only, clipboard stand-in, bounded waits, PROCESSES block on return.
- UI tasks read the design row on disk (no Skill tool in builders). `taste-skill/1.0.0/skills/taste-skill/SKILL.md`, `claude-plugins-official/frontend-design/8d392c816966/skills/frontend-design/SKILL.md`.
- Before any run that drives the sealed 1.0 app, tell the owner the old green and white look may show in the browser pane (memory `warn-before-old-app-baselines`).

## Split (`examples/split`)
- Done. Step 0 WebKit 26.5. C1 `d9be159`. A0 `4b67e96`. C2 `ad0436b`. A1 `4231563` (seeds version 2 under B-A1-1, two R40 tests xfail strict "task A19"). Node 313, Chromium 424 plus 6 xfail, WebKit 48 failures equal to the A0 baseline (43 are H-04 class (a) for A17, 5 class (b) await spec lines). Verified by the orchestrator 14:30.
- Done 14:50. Core C3 `bf62046`, C4 `13d74e3`, C5 `08f7faa`, C6 `67c1c15`. split-core fully built, Node 369, Chromium 424 plus 6 xfail. Nothing in flight for Split.
- Next. A2 to A18 (UI, design row, about 3 tasks per builder), A19 fidelity (Chromium), A20 live gate (both engines). Then finders on both modules. Split's README reconcile facts per task are in each BUILD.md "For the README reconcile".
- Owed. A planner pass (sdlc-planner, Edit only) before A17 and A20. (1) H-04 tap-safe repeat rule for the owner's ruling (ledger Needs the human H-04, ruled "Fix it in v1.1.0"). (2) H-05 a WebKit capture that adds no stylesheet, an exact-line allowance only if none exists (ORCH). (3) Spec and qa lines for the five class (b) WebKit cases (R29 height, two R30 Escape, two R10 hint taps), see `docs/modules/split-app/qa/webkit-baseline/20261014-130011/sorting.md`.
- Owed. Rule on the untracked red and probe run folders under `docs/modules/split-app/qa/functional/` (131624, 131753, 131836, 132019, 140338, 141448, 141810). Recommendation, keep untracked, they are recorded in the ledger.
- Orchestrator action 2. Add the WebKit commands (`python -m pytest tests/browser -q --engine webkit`, `python tests/browser/live_e2e.py --engine webkit`) to Split's `CLAUDE.md` (the engine option exists since A0). Not done yet.

## Streaks (`examples/streaks`)
- Done. habit-logic 6 `6188e66`, 7 `964678b`, 8 `9a79991`, 9 `3676fe5` (module fully built, Node 137). App 11 `42b64c3`, 12 `3e1db38`, 13 `d05297a`, 14 `6df2bd6`. WebKit commands added to `CLAUDE.md` (uncommitted orchestrator edit).
- Done 15:05. App 15 `b5a2d0d`, 16 `01dcde9`, 17 `6a7789b`. Chromium 54 passed and 33 xfail strict, WebKit 53, 1 skip, 33 xfail. Nothing in flight for Streaks.
- Owed. qa.md wording Q1 (twelve habit composer, check the field's box) and Q2 (Overview button computes flex), ruled ORCH to the golden (ledger S7 row 15). Fold into a Streaks planner touch-up before the QA finder runs.
- Next. App 18 to 20 (P1, P2, P4), 21 to 25, then 26 and 27, then the finders on both modules (QA both engines, code review, security), then task 28 gates.

## Owner events today
- 13:50 HOLD over the design (he saw the 1.0 page in the browser pane during baselines). Checked, goldens equal the approved final set and the archive, renders shown, he said continue at 14:00 (ledger off-scope rows, Split 14, Streaks 16).

## Process state
- Every agent return declared its processes STOPPED. Process ledgers current (Split rows 41 to 44, Streaks rows 38 to 45). Sweep by name, age, port and command line at resume, shells included.
- Uncommitted orchestrator files in both repos. `docs/progress/*`, `docs/v1.1.0/CHANGE-LEDGER.md`, Streaks `CLAUDE.md`. Streaks `docs/explain/` (2026-10-11 explain run) is untracked and never committed.
