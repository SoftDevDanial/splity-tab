# Lifecycle: Split v1.0.0

How this version went from an idea to a reviewed build, phase by phase. Written at review on 2026-10-10 from
`docs/progress/STATE-LOG.md`, the CHANGE-LEDGER and the findings files. The owner delegated the run on
2026-10-08 ("Auto create with lifecycles for 2 projects"), so decisions inside it are tagged ORCH and stay
reversible. The human test column and the seal are the owner's.

| Phase | When | What happened | Key decisions |
|---|---|---|---|
| Init | 2026-10-08 10:45 | Greenfield project, track `sdlc`, working version 0.1.0. Constitution, phase-skills registry, context hooks and `.gitignore` installed | One of two showcase examples |
| Brainstorm | 2026-10-08 10:50 | 13 questions walked, 8 capabilities (C1 to C8), 4 key flows, the money rules and 8 non-goals written down | Malaysian receipts: SST on subtotal plus service, whole cents, leftover cents to the top of the list, an unassigned item blocks the result (ORCH) |
| Design | 2026-10-08 10:50 to 15:52 | Three directions (Receipt tape, Colour per person, Working shown), each checked at 360, 390 and 1280 px. "Working shown" chosen with two changes folded in. A composer agent built the system, 5 screens and a states sheet. Flow check 12 of 12 links | "Working shown" is the only direction that puts the proof on the screen: each charge shows its base ("10% of RM 59.40") and the shares table sums across and down to the total (ORCH). A mid-run plugin upgrade changed two constitution lines, none this run relies on |
| Plan | 2026-10-08 15:53 to 2026-10-09 11:41 | Two modules: `split-core` (money and rules, 26 requirements) and `split-app` (42). Clarify gate CG-1 to CG-11 ruled. Plan check BLOCK (3 block, 9 flag), fixed by a fresh planner, re-check PASS. The change ledger opened with 8 scopes | Tests never touch the system clipboard (CG-7) after a planning probe overwrote the owner's. A backdrop click acts as Cancel (CG-8). Three harness gaps fixed in the plugin, so the strict Content Security Policy stayed |
| Execute, split-core | 2026-10-09 11:48 to 14:38 | Built (185 tests). Code review: 10 warnings fixed, including names that could fake an extra line in the copied summary. Security: 1 medium and 3 low fixed, a re-check found 2 more low, fixed. QA PASS, 54 scenarios. Closed at `329679e` with 254 tests, 600,000 random bills matching an independent reference | The owner set the target to a stable 1.0, so the version label moved from 0.1.0 to 1.0.0 (USER) |
| Execute, split-app | 2026-10-09 15:10 to 21:56 | Built in two parts (the owner stopped the second builder once and resumed it). QA PASS 145 of 145. Code review: a double click on Cancel could change the bill (BLOCKER), fixed with 12 warnings. Security: a double click on the last Remove saved a blank person, fixed; publish scope written down. Pixel gate 10 of 10 at 0 px, live gate 7 of 7. Closed at `22ac9af` | One repeat-press guard for every control that moves the layout under the pointer (ORCH, from QA, code review and security). The 360 px overflow on big bills (H-02) and a held Enter on the only item's Remove (SEC-04) accepted for v1.0, the owner chose to fix both in v1.1.0 (USER) |
| Regression | 2026-10-09 21:57 to 2026-10-10 14:30 | `--full` under an economy ruling. The code review of the delta caught two regressions the guard itself had caused (RG-CR-01 a double click on Add person added then removed a person, RG-CR-08 a double press on a chip under a price error removed the item), both fixed in two solver rounds. The orchestrator found the fidelity finder had never run on split-app and ran it: 157 of 157 element checks. QA 340 of 341. Cold boot 7 of 7. 427 browser and 275 unit tests | Verdicts on byte-identical code stand (ORCH). A regression of verified behaviour stays a BLOCKER, never accepted. The owner chose a second version per app to show versioning (USER) |
| Brand | 2026-10-10 | Logo, README redesign, static badges, a showcase image from real pixel-gate captures. Docs only, no app change | Logo in the repo now, the favicon in v1.1.0 through the design phase (USER) |
| Review | 2026-10-10 | Drove every brainstorm flow and rule on a cold boot with real gestures: 80 of 80 checks pass, and the accepted 360 px limit measured again. See the verdict below | Shippable for the owner's test |

## Review verdict (stakeholder seat, 2026-10-10)

**Shippable for UAT.** Every capability C1 to C8 works on a cold boot with no seed. The four key flows hold
word for word: the even split copies the brainstorm's own example summary exactly, the by-item split shares the
satay between two people and the charges in proportion, a closed tab comes back with both modes intact, and New
bill returns to two people, even, 10% and 6%. The amount grammar, the rate ranges, half-up rounding, leftover cents
to the top of the list, the 2 to 12 people and 50 item limits, blank names, duplicate names, removing a person from
every item, the blocked clipboard message, the unreadable-draft note, keyboard use, focus rings, 360 px, 1280 px,
reduced motion, the non-goals and the no-network rule all hold (`docs/review/20261010-144746/results.json`). The
money figures in that drive are worked out from the brainstorm's rules by the script, not copied from the app.
The design matches its goldens to the pixel.

Deviations from the brainstorm and the design, with their cause:

| Deviation | Cause |
|---|---|
| The second click of a double click on Add person, Add item, any Remove, New bill or the dialog's buttons is ignored | Claude (ORCH), fixing QA F-1, code review CR-01 and WR-01, security SEC-01 and the regressions RG-CR-01 and RG-CR-08. The brainstorm did not ask for it. A single click or key press is never held back, and there is no timer |
| A click on the dialog's backdrop cancels, where `docs/design/new-bill-dialog.md` says it does nothing | Claude (ORCH), clarify ruling CG-8, so every way out of the dialog behaves the same. The visual golden is unchanged |
| Control and direction characters in a name print as a space in the copied summary, while the screen shows the name as typed | Claude (ORCH), code review WR-10 and security SEC-01 and SEC-02, so a name cannot fake an extra line or reorder a share in a chat app. A name made only of invisible characters still prints blank (accepted residual) |
| Copy the brainstorm left open: "Check the charges to see the shares.", "Add an item to see the shares.", "Give every item a price to see the shares." and "Enter a rate from 0 to 30" (or 20) | Claude (ORCH), written in the design phase and approved under delegation (`docs/design/RULINGS.md`). It fills gaps, it changes no rule |
| `src/system.css` is the golden stylesheet plus one rule that makes `hidden` win over a class's display | Claude (ORCH), plan ruling RC-5. The pixel gate shows no visible difference |
| On a 360 px phone the by-item table scrolls sideways once the items pass about RM 653.40 (measured 383 px at RM 1,058.40) | Known limit H-02, the golden CSS, accepted for v1.0. The owner chose to fix it in v1.1.0 (USER) |
| Holding Enter down on Remove of the only item adds a blank item | Known limit SEC-04, keyboard only, one click undoes it. Accepted for v1.0, scoped to v1.1.0 (ORCH, under the owner's v1.1.0 choice) |
| If storage is blocked or full, changes are not saved and no message says so | Observation from this review, accepted (ORCH). The brainstorm's note covers a draft that cannot be read, not a failed save. Listed for the owner under H-01 |
| Two tabs editing the bill, a double click on Dismiss note moving focus to the page, a hand-edited draft with a huge id | Accepted residuals (ORCH), no effect on a bill a person types. Recorded in the ledger |

No requirement was dropped and nothing was built that no spec asked for. Compliance review is skipped (personal direction).
No out-of-project artifacts are logged (`docs/progress/out-of-project-artifacts.md` does not exist).
