# Lifecycle, Split (Danial's Splity Tab)

How each version went from an idea to a reviewed build, phase by phase. The v1.0.0 part was written at its review on
2026-10-10 and is kept as it was. The v1.1.0 part was written at its review on 2026-10-16 from
`docs/progress/STATE-LOG.md`, `docs/v1.1.0/CHANGE-LEDGER.md`, the handoffs in `docs/progress/handoff/` and the
findings files. The human test column and the seal are the owner's.

## v1.0.0 (sealed 2026-10-10, tag `v1.0.0`)

The owner delegated the run on 2026-10-08 ("Auto create with lifecycles for 2 projects"), so decisions inside it are
tagged ORCH and stay reversible.

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
| Review | 2026-10-10 | Drove every brainstorm flow and rule on a cold boot with real gestures: 80 of 80 checks pass, and the accepted 360 px limit measured again. Verdict below | Shippable for the owner's test |
| UAT | 2026-10-10 15:02 to 15:58 | One sitting, 8 cases, the tester's pre-run and the owner's verdicts 8 of 8 PASS. His requests became v1.1.0 (the spare sen chosen by the user, UAT-F1). UAT-F3 investigated, not a bug | Script rule from UAT-F2, every expected line lists every figure on screen (USER) |
| Seal | 2026-10-10 16:35 | `docs/v1.0.0/SEAL.md`, tag `v1.0.0`, residuals listed as ruled | "1. Seal both apps" (USER) |

### v1.0.0 review verdict (stakeholder seat, 2026-10-10)

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

## v1.1.0 (in review, not sealed)

Not delegated. The owner ran the design round with the orchestrator and ruled every product question himself
(USER). Decisions the orchestrator took in between are ORCH and reversible. The ledger is the record of each one.

| Phase | When | What happened | Key decisions |
|---|---|---|---|
| Opened | 2026-10-10 16:37 | The v1.1.0 ledger opened at the seal with nine scopes, S1 the spare sen chosen by the user (UAT-F1), S2 the by-item table at 360 px (H-02), S3 a held Enter on Remove (SEC-04), S4 the save warning, S5 tests in WebKit, S6 the logo in the app, S7 a livelier look, S8 a free name, S9 several bills as a document only | Scopes from his UAT words and his D-01 answers ("i agree with all") (USER) |
| Brainstorm delta | 2026-10-10 16:42 | His answers turned into the v1.1.0 delta of `docs/brainstorm/brainstorm.md`, C9 spare sen choice, C10 save warning, C3 changed (fits 360 px), C0 a new look, the name, and `docs/future/several-bills.md` | Name "Danial's Splity Tab", the logo and header show "Splity Tab" (USER). One spare sen rule for the whole bill, a random draw kept in the draft, the save warning copy, one dark theme, still no web fonts (ORCH) |
| Design | 2026-10-10 16:46 to 2026-10-13 | Round 1, five clickable directions by five designer agents. He asked for a mix. Direction F was built on D from the orchestrator's reading, then withdrawn when he corrected the base to B Glass Receipt (the orchestrator's misread, ledger S7 row 4). G Glass Console, then G2 after his phone note (People and Charges fold, "Shares" becomes "Splits"). Composer agent, 15 goldens, the locked system. Flow check found one golden defect in the accessible names, fixed. Logo rounds, ten marks drawn and reviewed, he kept the 1.0 mark with his own tweak (S12). The UAT sheet layout was designed in the same round. Finalize copy into `docs/design/` on 2026-10-13 after his "Yes, but later" | G2 and S12 (USER). A bad rate or price blocks the receipt as in 1.0 (ORCH, told to him). Copy list and thirteen interaction rules approved (USER, `docs/design/RULINGS-v1.1.0.md`) |
| Plan | 2026-10-13 18:20 to 23:05 | Constitution updated to the sdlc 2.6.0 copy. Two researchers (WebKit testing, the save warning and the tab icon). Clarify gate part 1 (show the warning at boot, the icon as a file, header and tab only, install WebKit, suites and live gates in WebKit, pixel gate Chromium only) and part 2 (CG-P1 to CG-P8). Delta contracts, split-core 34 R# and split-app 61 R#. Plan check BLOCK (4 block), one fix pass, re-check PASS, a touch-up. Done at `853afe1` | Every clarify item ruled as recommended (USER). The 1.0 test files go by `git rm`, kept in the tag (USER) |
| Execute | 2026-10-14 11:54 to 2026-10-16 03:20 | WebKit 26.5 installed. A0 ran the 1.0 suite in WebKit, 48 failures. Core C1 to C6, then app A1 to A21 one task per builder, each seen failing first and committed with its proof runs. The owner stopped the build once ("HOLD EVERYTHING") when the A0 baseline showed the 1.0 page in his pane, resolved by a check of the goldens. Step 5 finders on both modules, QA (one missing test), code review (14 items), security (SEC-S5-1, a bidi character in a name flips the People line), fidelity (one-to-one, 0 findings). One solver round. The H-10 build (C7, A22). The step 5 re-check found a double click on Dismiss note folding People (CR-R1), built as A23 with a fix pass. Both modules closed at `b0992b4`, Node 406, Chromium 742 and WebKit 742 with 0 failures | H-04, a double tap in WebKit counts as one press by time and place, 500 ms and 22 px (USER). H-05, the WebKit live gate captures by screencast frames (ORCH, his no preference). H-06 the amber bar on a new item, H-07 no status for a late clipboard answer (USER, keep). H-08, the focus scroll that keeps a Tab stop clear of the strip in WebKit (USER). H-09, keep the amount hint as built, a VoiceOver case at UAT (USER). H-10, remove control and bidi characters from names (USER). A23 and the minor calls of the night under his word on minor calls (ORCH) |
| Regression | 2026-10-16 03:25 to 04:25 | `--full`, the step 5 re-check's QA and security folded in. QA PASS both modules (73 and 181 scenarios), pixel gate 40 of 40 at 0 px with both controls, cold boot 9 of 9 in Chromium and WebKit with red controls, security PASS both, code review 0 BLOCKER with the consistency sweep. No solver round | CS-1 (a name input of only removed characters saves the same text and clears the copy status) and SEC-R1 (an IME composition holding a bidi control is cut short) accepted as residuals, both to the v1.2.0 plan (ORCH). README fixes RG-CR-1, RG-CR-2, CS-7 |
| Review | 2026-10-16 04:27 to 05:00 | The stakeholder drive on a cold boot with real gestures, Chromium at 1280 x 800, 390 x 844 and 360 x 780, WebKit at 390 x 844 and 360 x 780. 303 checks pass, 0 fail, 44 recorded as information. Every money figure worked out by the script from the brainstorm's rules. The app equals its golden to 0 px in WebKit at the first visit, K1 and W1 | Shippable to UAT. D1 (WebKit draws a focus ring after a tap that opens a popup or closes the sheet, an engine difference recorded in part), D2 (README header at 1.0 until the seal, ORCH) and O1 (a 99,999.99 price does not show whole at 360 px) go to the owner. Next `sdlc:uat` |

### v1.1.0 review verdict (stakeholder seat, 2026-10-16)

**Shippable to UAT.** Every capability of the brainstorm and its v1.1.0 delta works on a cold boot with no seed in
both engines, the four key flows hold, and the copied summary of the even split is the brainstorm's own example word
for word. No requirement was dropped and nothing was built that no spec or ruling asked for. The full record, the
deviations with their causes, the behaviour ruled beyond the brainstorm's words and the candidate UAT cases are in
`docs/review/20261016-042713/review.md`. Compliance review is skipped (personal direction). No out-of-project
artifacts are logged (`docs/progress/out-of-project-artifacts.md` does not exist), and one stray named in the state
log is listed there for the owner.
