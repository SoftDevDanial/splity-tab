# QA: split-app

> Test contract for v1.1.0. Every functional scenario runs against the **running** app, served by
> `python -m http.server <port> --bind 127.0.0.1` from the project root and driven by headless Python
> Playwright with real gestures (clicks, taps, typing, key presses). The suite runs once in Chromium and once
> in WebKit (`--engine`). A scenario tagged `@chromium_only` is skipped in WebKit with its written reason and
> counted. Gherkin tags map each scenario to an R# in `spec.md`, and every R# has at least one scenario. The
> fidelity gate (Chromium only) and the cold-boot live-e2e gate (both engines) run after the suite is green.

**v1.1.0 delta.** Written 2026-10-13 by the planner (solutions architect role). This file replaces the sealed 1.0 file, which stays in git tag `v1.0.0`. A 1.0 scenario whose expectation or setup changed keeps its tag and carries a `# [Changed 2026-10-13, v1.1.0, S#]` line saying what changed. New scenarios sit at the end of the Gherkin block under `# ---------- <topic> (v1.1.0, S#) ----------` headers. Screens are named by golden file (`bill-empty`, `bill-items`), because the v1.1.0 inventory ids (S1 first open, S3 unassigned) clash with 1.0's. Scopes S1 to S9 are those of `docs/v1.1.0/CHANGE-LEDGER.md`. Clarify items CG-P1 to CG-P8 are ruled by the owner (USER, 2026-10-13), each as recommended (ledger S1 rows 2 and 3, S4 row 3, S7 row 15), and the scenarios assert the rulings. The items are in `docs/modules/ROADMAP.md`, section v1.1.0. ~~CG-P7 and CG-P8 are open. A scenario written to their recommended answer says "pending CG-P7" or "pending CG-P8".~~ Changed 2026-10-13 after the plan check (F1, B4).

Changed 2026-10-13 after the plan check (`docs/modules/PLAN-CHECK.md`, B2, B3, B4, F1, F3, F5, F6, F9, N2, N4, N5). New scenarios are the R3 walk control, an R6 step from twelve people, Arrow keys in P1 (R52), the after-load stand-in check (R40) and the live gate's control (R41). The fidelity seeds carry the clipboard stand-in, the R47 and R54 scans have planted copies, and five checklist sections have a row for the rest. Each change carries its own dated line.

Changed 2026-10-13 after the plan re-check (`docs/modules/PLAN-CHECK.md`, F11, F12, N9). One new scenario, the live gate script's static guard (R41), which is the v1.1.0 form of three sealed 1.0 tests. "Works right" asserts `"control": null` in each green run's summary. The R1 scenario compares `src/system.css` with the golden after turning CRLF into LF. The Seed drafts paragraph states the two parts of each fidelity seed file. Each change carries its own dated line.

Changed 2026-10-14 in execute, by the planner pass the plan owed before A17 and A20 (ledger H-04, H-05, S5 rows 4, 5 and 7, S7 rows 17 to 19). "The card reads" is every text node joined with a space (Q-A2-1). "A body recorder" also proves that a repeat was cancelled, whatever lies under the second press, and checks that a double tap was one. "Press Escape" on a dialog waits for its close (R59 (2)). New scenarios are the touch tap on the charges hint (`@per_engine`, R59 (3)), the second press after a double activation closed M1 (R30), the repeat rule's Node table and two tap scenarios (R57 (b), ~~awaiting the owner's ruling~~ ruled USER 2026-10-14 20:00, "Time + place (Recommended)"). The live gate captures screencast frames (R41, H-05). Each change carries its own dated line. [Changed 2026-10-14 in execute after the owner's H-04 ruling. A17 builds right after A3 (ORCH), the A0 record scenario names the WebKit run's own folder (ORCH, Q-A0-2).]

Changed 2026-10-15 in execute, planner touch before A18 (ledger S4 row 4, S5 row 10, S7 rows 20, 22, 24, 26 and 28 to 32, H-08). Lines the build measured as untrue are corrected with the old text struck. The R47 scan bans ".removeItem(" (Q-A3-1), the held Enter on New bill also counts the dialog's close events (S5 row 10), R36 asks that no animation is running (F-A4-1), the hint tap uses the window recorder (Q-A6-1), the price error is placed by `justify-self` (F-A8-1, R14 and ST-02), ST-12 is one line on the desktop card (F-A10-1), and "Press Escape" names M1's click closes (F-A16-1). New scenarios are the second press of a double activation that closed the sheet (R50, F-A12-1) or P1 (R52, F-A13-1), Pick again in the Splits sheet (R54, F-A15-1), and where the app scrolls a focused control (R49, H-08, ruled USER 2026-10-15 16:20, option (1), task A21). The R49 Tab scenario stays `@both`. Each change carries its own dated line.

Changed 2026-10-16 in execute, planner pass for H-10 and the step 5 wording (ledger H-10, S7 rows 39 to 43). New scenarios for R62 sit at the end of the Gherkin block under "Plain names" (H-10, ruled USER 2026-10-16 00:07, option (1), task A22), with the seeds G8 to G10. Scenarios are added for three tests the step 5 solver round wrote without one (R20 seven to eleven people, CR-S5-7. R41 the guard follows `support.py`, CR-S5-6. R58 one folder per run, CR-S5-14). How to run names the live gate's one-server pair. Lines the finders measured as untrue or open to two readings are corrected with the old text struck, "The strip reads" (QA-S5-2), `browser_version` (QA-S5-3), R60's line box (A18, K1-56) and the checklist rows K1-01, K1-02, K1-10, K1-40, K1-44 (O-1), K1-54, W1-02 (O-2), BR-02 and ST-10 (fidelity O-4, A18). Each change carries its own dated line.

Changed 2026-10-16 in execute, planner touch after the step 5 re-check (ledger S7 rows 45 and 46, code review CR-R1 and CR-R6, ORCH under the owner's word on minor calls). ~~Two scenarios are added.~~ Three scenarios are added, the third by a follow-up the same day (see the last sentence). The outline "A repeat press on Dismiss note acts as one press at every width" (R27, R7, task A23) sits at the end of the Gherkin block under "Dismiss note arms the repeat guard", and the `@R62 @node` outline "plainNameField puts the caret where the text went in" (CR-R6) sits at the end of "Plain names". The first fails on today's tree on its asserted property in both engines, apart from its single click rows, which are its control. The second passes on today's tree and gets its RED from stubs of the helper. "Dismissing the note" is unchanged and carries a pointer line. Each change carries its own dated line. [Added 2026-10-16 in execute, follow-up to CR-R1, ORCH. The third is the outline "A held Enter on Dismiss note reaches nothing" (R27, R57), under the repeat press outline at 390 x 844 and 1280 x 800. Today's code is unmeasured for it and the RED run of task A23 measures it.]

## How to run
- **Functional suite.** `python -m pytest tests/browser -q` runs Chromium (the default, as in 1.0). `python -m pytest tests/browser -q --engine webkit` runs WebKit. Test functions are named `test_R<n>_<what>`, so a grep maps each one to its tag. `split-core`'s unit tests and this module's Node tests (`tests/draft.test.js`, `tests/errors.test.js`) run with `node --test "tests/**/*.test.js"`.
- **Fidelity gate.** `python tests/browser/fidelity/run.py`, Chromium only. It has no engine option (R58).
- **Live gate.** `python tests/browser/live_e2e.py` (Chromium) and `python tests/browser/live_e2e.py --engine webkit`. [Added 2026-10-16 in execute, wording as built (A20) and as `CLAUDE.md` has it.] Without `--base-url` the script serves the project root itself. A run that counts for the gate is a pair per engine against one server. Serve the project root (`python -m http.server <port> --bind 127.0.0.1`), run `python tests/browser/live_e2e.py --engine <engine> --control seeded --base-url http://127.0.0.1:<port>/`, which must stop red at step 1 (folder `<stamp>-<engine>-control`), then the same command without `--control` (the green run, folder `<stamp>-<engine>`), then stop the server by its PID ("Control and baseline" in the gate section below).
- **Before the first WebKit run.** The orchestrator installs WebKit with `python -m playwright install webkit` (ledger S5 row 2). No test, script or task in this module installs anything.
- **Server lifecycle (every run).** The harness picks a free port by binding port 0, starts `python -m http.server <port> --bind 127.0.0.1` with the project root as working directory, waits for `GET /` to answer (at most 50 tries 100 ms apart, then it gives up and fails the run with "server gave up after 50 tries"), and in a `finally` block kills the server by PID, waits for it to exit (10 s cap) and re-checks that the port binds again. It prints the PID and port at start and STOPPED with the port re-check at the end, so the orchestrator can ledger it.
- **Browser.** Every browser is launched by `rig.launch(playwright, engine)` and every context is made by `rig.new_context` (meta tests under R58). Headless always. The default context has a 390 x 844 viewport, device scale factor 1, colour scheme `dark` and reduced motion `reduce`, unless a scenario names another size or `no-preference`. No context is ever made with `is_mobile` or `bypass_csp`, so the shipped policy is live in every scenario. A scenario that taps makes its context with `has_touch` and taps with `page.touchscreen.tap`.
- **Engine tags.** Each scenario carries exactly one.
  - `@both` runs in both engines and asserts the same result in each.
  - `@per_engine` runs in both engines and asserts each engine's own result, written as "In Chromium" and "In WebKit" lines (R59).
  - `@chromium_only` runs in Chromium. WebKit skips it with the reason written in the `# reason` line under the tag, through the marker `chromium_only(reason=...)`. Every skip is listed with its reason in `skips.txt` and counted, never reported as a pass.
  - `@static` reads files only. It runs in both engine runs and gives the same result.
  - `@node` is a Node test under `node --test`, with no browser.
  - `@gate` is a gate run. The scenario names its engines.
  When the A0 baseline sorts a WebKit failure as (b), an engine difference, its scenario becomes `@per_engine` with the measurement written in. When it sorts one as (c), a Chromium-only tool, the scenario becomes `@chromium_only` with that reason (R59). The A0 record is checked by the R59 scenarios. [Changed 2026-10-14 in execute, ledger S5 rows 4 and 5. A (b) whose end state is the same in both engines keeps `@both`, and its test reads the result the way spec R59 writes it (the R29 height within 0.5 px, the R30 Escape cases waiting for the close). Only the charges hint tap becomes `@per_engine`.]
- **Seeding.** A scenario that starts from a stored bill passes it through Playwright `storage_state` when it makes the context (`origins[0].localStorage = [{ name: "split.draft", value: <seed> }]`). Nothing is ever injected into the app, and no `window.__*` hook exists or is used. Init scripts that control the **browser platform** are allowed, test-side only and kept under `tests/browser/`. They are the clipboard stand-ins, the storage drivers, the CSP listener and the write counter below.
- **Clipboard (CG-7 of 1.0).** No test ever touches the operating system clipboard, not even to read it, and no clipboard permission is ever granted. Every context in both engines gets exactly one script from `tests/browser/clipboard/`. `recorder.js` is the default. It replaces `writeText` with a function that stores `String(text)` in `window.testClipboardText`, adds 1 to `window.testClipboardWrites` and returns a resolved promise. `reject.js` makes `writeText` return `Promise.reject(new DOMException("Write permission denied.", "NotAllowedError"))`. `missing.js` makes `navigator.clipboard` read as `undefined`. The A0 probe records whether WebKit on `http://127.0.0.1` is a secure context with a `Clipboard` interface (R59). Where it has none, `recorder.js` and `reject.js` define `navigator.clipboard` with their own `writeText`, as `missing.js` redefines it, and the A0 record says which path each engine took. The app calls the real `navigator.clipboard.writeText` and gets no hook.
- **CSP listener.** Every context also gets `tests/browser/csp/listener.js`. It adds a `securitypolicyviolation` listener that pushes `{ violatedDirective, blockedURI }` to `window.testCspViolations`. It is the engine-neutral detector of a policy violation. In Chromium a console message holding "Content Security Policy" also fails a scenario, as in 1.0.
- **Console and network.** A scenario fails on any console error, any page error, any recorded CSP violation, and any request that is not a same-origin GET for `/`, `/src/system.css`, a file under `/src/` (`/src/icon.svg` allowed, not required) or `/favicon.ico`, unless the scenario expects otherwise.
- **Storage drivers (research A3, test-side init scripts in `tests/browser/storage/`).** None touches `localStorage` at its top level, because an init script also runs in the blank first document, where storage access is denied.
  - **D-a `fail-set.js`.** `Storage.prototype.setItem` throws a test-made `DOMException("test quota", "QuotaExceededError")` until a `test:storage` CustomEvent with `detail: false` is dispatched on `window`, and then calls the original.
  - **D-b `fail-get.js`.** The `window.localStorage` getter throws a test-made `DOMException(..., "SecurityError")`, with the same `test:storage` switch to let it return the real storage (SW6).
  - **D-c `fail-getitem.js`.** `Storage.prototype.getItem` throws.
  - **D-d, a real quota fill.** A `page.evaluate` on the app's page writes filler keys `test.fill.<n>`, halving the size from 1 MiB down to one character, until even one more character is refused. A gesture that grows the stored text then makes the engine throw its own error through the app's own `setItem`. Removing the filler keys and one more change prove the clear. Run once per engine.
  - **The write counter `count-set.js`.** Wraps `Storage.prototype.setItem`, adds 1 to `window.testSetItemCalls` on each call and then calls the original. It proves "writes nothing".
  If the A0 probe finds that WebKit lets no init script redefine the `window.localStorage` getter, the D-b scenarios become `@chromium_only` with that measured reason (R59 (c)).
- **Controls.** A control asserts the requirement and is watched failing first. Every new or changed scenario is committed before its task as `xfail(strict=True, reason="task An")` and is seen failing on the asserted property against the tree of that moment. That RED run keeps its own `qa/functional/<stamp>-<engine>/` folder. The task that builds the requirement removes the mark. A new test that passes before its task is a finding, because it asserts nothing or asserts the old state. The `xfail` mark is pytest's only, so a new or changed `@node` case (R61 in `tests/draft.test.js`) is seen failing on its own assertion by the stub method that `split-core/qa.md` states once (How to run, "RED first for a new or changed case"), its RED output in `docs/modules/split-app/qa/unit/<YYYYMMDD-HHMMSS>-red/` (added 2026-10-13 after the plan check, F3).
- **No hooks in shipped code.** The app gets no test hook, global or URL parameter (R2, R59). Storage failures, the clipboard and CSP observation come from the test side only.
- **Evidence.** `docs/modules/split-app/qa/functional/<YYYYMMDD-HHMMSS>-<engine>/` holds `pytest.txt`, `junit.xml`, `skips.txt` (every skip with its reason, and the count) and a screenshot of every failed scenario. Nothing is written to the project root or to `docs/design/`.

### Phrases used below
- "Replace the text of X with Y" means click X, press Control+A, then type Y key by key. "Leave the field" means press Tab.
- "Open People first" and "open Charges first" mean, below 1024 px, a click on that section's header row (`#peopleBtn`, `#chargesBtn`) when it is folded. From 1024 px both sections are always open and the step does nothing.
- "The card reads" means ~~the `textContent` of `#rbody` with every run of white space made one space~~ every text node inside `#rbody`, in document order, joined with one space, then every run of white space made one space and the ends trimmed (`support.card_text`). [Changed 2026-10-14 in execute, ledger S7 rows 17 and 19, Q-A2-1, ruled ORCH. `textContent` joins text nodes with nothing between them, so a card built by script read "TotalEnter the subtotal ..." where the golden's markup reads "Total Enter the subtotal ...", a white-space difference that allowed difference 4 permits.] It can be read at any width, because the card is in the DOM below 1024 px though not displayed. "The sheet reads" is the same for `#splitsDlg .rbody` after a click on Splits. "The strip reads" is the visible text of `#stripInfo`. [Added 2026-10-16 in execute, QA-S5-2, wording as built.] The visible text is `innerText`, which keeps a line break between the label and the figure (`'Total\nRM 116.60'`), so every run of white space, line breaks included, is made one space and the ends trimmed before it is compared. "Total RM 116.60" is that text. The live gate reads it so (`strip_reads` in `tests/browser/live_e2e.py`), and a failing line may print the raw `innerText`.
- "A body recorder" is a test-side listener, added with `page.evaluate` before the gesture, that counts the `mousedown` and `click` events reaching `document.body` in the bubble phase, with their `detail`. "Only press 1 and click 1 reached the page" means it counted one of each. [Changed 2026-10-14 in execute, ledger H-04 and S5 row 7.] It is two listeners. The second sits on `window` in the capture phase, so it runs before the app's guard, and keeps every `pointerdown`, `mousedown` and `click` of the gesture with its `pointerType`, `detail`, `timeStamp`, `clientX` and `clientY`, and the event itself. "Only press 1 and click 1 reached the page" also means that the `window` listener saw every press and click of the gesture, and that each one after the first has `defaultPrevented` true once its dispatch is over. The proof that a repeat was cancelled then does not depend on what lies under the point, because 19 WebKit cases passed at A2 only since the layout had moved. For a touch double tap it also means that the second tap's `click` came less than 500 ms after the first and within 22 px of it by those records. Otherwise the case fails and names the gap, because it did not test a double tap (spec R57 (b)).
- "Press Escape", while a dialog is open (M1, the Splits sheet or P1), means press Escape and then wait for that dialog's `close` event before anything is read, at most 2 s, failing with "dialog still open after 2 s" when it has not fired by then (a listener added before the key press catches a close that came first). [Added 2026-10-14 in execute, ledger S5 rows 4 and 5, class (b).] WebKit closes the dialog in a task after keyup, Chromium before the key press returns (spec R59 (2)). The end state is the same, so these scenarios stay `@both`. [Added 2026-10-15 in execute, planner touch before A18 (ledger S7 row 32, F-A16-1).] The same wait for M1's `close` event, at most 2 s, follows every close of M1 by a click (Cancel, Start new bill, the backdrop) before focus or the screen is read, because M1 gives focus back to New bill in its `close` event, a task after the click (spec R59 (2), "M1's click closes"). The tests do it through `closing` (A16). A click close of the Splits sheet or P1 focuses its control in the click itself.
- "Equal to the golden" (replaces 1.0's "equal to the specimen"). These computed properties are read on the app element and on the named golden element, both rendered in the engine of the run at the same width, the golden opened as a file and never written. `color`, `background-color`, `font-size`, `font-weight`, `line-height`, the width, style and colour of each border side, `box-shadow`, the four `padding-*` values and the four corner radii. A row that needs another property names it. Width, height and position are compared only where the row names them.
- "The draft" means the parsed value of `localStorage["split.draft"]`. "Stored text" means its raw string.
- Sizes are CSS px, positions are `getBoundingClientRect()` values, and a measured number matches within 0.5 px.

## Seed drafts
`tests/browser/seeds.py` is the one source. Each fidelity file `tests/browser/fidelity/seed-*.js` starts with the text of `tests/browser/clipboard/recorder.js` byte for byte, followed by exactly one `localStorage.setItem` statement that repeats one of these seeds. `test_R40_fidelity_seeds_match` keeps the first part equal to `recorder.js` and the seed part equal to `seeds.py` (Fidelity gate, Seed scripts). [Changed 2026-10-13 after the plan re-check (N9). It said the test keeps each file equal to its seed, which the B2 fix had made untrue.] Every seed is version 2 with `"spare":{"rule":"top"}` unless its row says otherwise. Names in this file map to `seeds.py` names as K1 = `S1` (the `bill-items` bill), K2 = `S2` (the `bill-even` bill), BU = `S5` (the `bill-unassigned` bill) and S8 = `S8` (twelve named people). The other names are new in `seeds.py` under the same name (`-` becomes `_`).

| Name | Value |
|---|---|
| K1 | `{"version":2,"bill":{"mode":"item","people":[{"id":"p1","name":"Aisyah"},{"id":"p2","name":"Ben"},{"id":"p3","name":"Chen"}],"subtotalText":"","items":[{"id":"i4","name":"Nasi lemak ayam","priceText":"15.90","who":["p1"]},{"id":"i5","name":"Char kuey teow","priceText":"13.50","who":["p2"]},{"id":"i6","name":"Mee goreng mamak","priceText":"12.00","who":["p3"]},{"id":"i7","name":"Satay, 10 sticks","priceText":"18.00","who":["p1","p3"]}],"serviceText":"10","sstText":"6","spare":{"rule":"top"},"nextId":8}}` |
| K2 | `{"version":2,"bill":{"mode":"even","people":[{"id":"p1","name":"Aisyah"},{"id":"p2","name":"Ben"},{"id":"p3","name":"Chen"}],"subtotalText":"100.00","items":[],"serviceText":"10","sstText":"6","spare":{"rule":"top"},"nextId":4}}` |
| BU | K1 with i6 `"who":[]` |
| RE | K1 with `"serviceText":"35"` |
| W1 | K1 plus `{"id":"i8","name":"","priceText":"964.50","who":["p1"]}` at the end of `items`, `"nextId":9` |
| T12 | even, p1 Aisyah, p2 Ben, p3 Chen, p4 to p12 with `"name":""`, `"subtotalText":"100.00"`, no items, rates `10` and `6`, `"nextId":13` |
| T12W | T12 with all twelve names `"WWWWWWWWWWWWWWWWWWWW"` (20 characters) |
| T12I | T12 with `"mode":"item"` and one item `{"id":"i13","name":"Tea","priceText":"12.00","who":[all twelve ids]}`, `"nextId":14` |
| ONE | K2 with `"spare":{"rule":"one","personId":"p2"}` |
| RND | K2 with `"spare":{"rule":"random","order":["p2","p3","p1"]}`, which gives Aisyah RM 38.86, Ben RM 38.87, Chen RM 38.87 |
| PA0 | item mode, p1 Aisyah, p2 Ben, p3 Chen, items `{"id":"i4","name":"X","priceText":"0.01","who":["p1","p2"]}` and `{"id":"i5","name":"Y","priceText":"0.01","who":["p1","p2"]}`, rates `0` and `0`, `"spare":{"rule":"random","order":["p1","p2","p3"]}`, `"nextId":6`. Two spare sen, and every order gives Aisyah RM 0.01, Ben RM 0.01, Chen RM 0.00, so Pick again can change nothing (CG-P3) |
| I2 | item mode, p1 Aisyah, p2 Ben, p3 Chen, items `{"id":"i4","name":"X","priceText":"10.00","who":["p2"]}` and `{"id":"i5","name":"Y","priceText":"5.01","who":["p2","p3"]}`, rates `10` and `6`, `"nextId":6` (core qa example I2) |
| S8 | even, twelve people p1 to p12 named Aisyah, Ben, Chen, Devi, Farid, Grace, Hafiz, Indra, Jia Hui, Kumar, Lina, Mei Ling, `"subtotalText":""`, rates `10` and `6`, `"nextId":13` |
| K1-8 | K1 with five more people p8 Devi, p9 Farid, p10 Grace, p11 Hafiz, p12 Indra, `"nextId":13` |
| MAX-E, MAX-I | core qa's named bills MAX-E and MAX-I, people named as S8, built in `seeds.py` |
| S2_V1 | the 1.0 K2 draft, `{"version":1,"bill":{"mode":"even","people":[{"id":"p1","name":"Aisyah"},{"id":"p2","name":"Ben"},{"id":"p3","name":"Chen"}],"subtotalText":"100.00","items":[],"serviceText":"10","sstText":"6","nextId":4}}` |
| S1_V1 | the 1.0 K1 draft, as K1 with `"version":1` and no `spare` key |

Helpers in `seeds.py` build the derived bills named in scenarios ("K1 cut to its first n items", "K2 with n people P1 to Pn", "K1 with only its last item") as version 2 drafts.

### Unreadable drafts (each must give the unreadable note, R27, R61)
| Id | Stored value | Rule |
|---|---|---|
| B1 | `not json` | D1 |
| B2 | `[]` | D2 |
| B3 | `null` | D2 |
| B4 | K2 with `"version":3` (changed 2026-10-13, was version 2, which is now readable) | D3 |
| B5 | K2 with `"version":"2"` | D3 |
| B6 | `{"version":1,"bill":[]}` | D4 |
| B7 | K2 with `"mode":"split"` | D5 |
| B8 | K2 with only p1 | D6 |
| B9 | K2 with 13 people | D6 |
| B10 | K2 with person id `"x1"` | D6 |
| B11 | K2 with two people both id `"p1"` | D6 |
| B12 | K2 with `"name":5` | D6 |
| B13 | K1 with i4 `"who":["p9"]` | D7 |
| B14 | K1 with i4 `"who":["p1","p1"]` | D7 |
| B15 | K1 with 51 items | D7 |
| B16 | K1 with two items both id `"i4"` | D7 |
| B17 | K1 with i4 `"priceText":15.9` (a number) | D7 |
| B18 | K2 with Aisyah renamed `ABCDEFGHIJKLMNOPQRSTU` (21 characters) | D8 |
| B19 | K2 with Aisyah renamed `"Ai\nsyah"` | D8 (still rejected after H-10, D8 (a), noted 2026-10-16) |
| B20 | K1 with i4 named 41 characters | D8 |
| B21 | K2 with `"subtotalText":100` | D9 |
| B22 | K2 with `"nextId":3` (not above p3) | D10 |
| B23 | K2 with `"nextId":1.5` | D10 |
| B24 | K2 with `"nextId":2000000000` | D10 |
| B25 | K2 without the `spare` key | D13 |
| B26 | K2 with `"spare":{"rule":"two"}` | D13 |
| B27 | K2 with `"spare":{"rule":"one","personId":"p9"}` | D13 |
| B28 | K2 with `"spare":{"rule":"one"}` | D13 |
| B29 | K2 with `"spare":{"rule":"random","order":["p1","p2"]}` (p3 missing) | D13 |
| B30 | K2 with `"spare":{"rule":"random","order":["p1","p1","p2","p3"]}` (p1 twice) | D13 |
| B31 | K2 with `"spare":{"rule":"random","order":["p1","p2","p3","p4"]}` (p4 is no person of the bill) | D13 |
| B32 | K2 with `"spare":[]` | D13 |

### Readable drafts that look odd (must load with no note, R26, R61, D8, D11 to D14)
| Id | Stored value | Expected |
|---|---|---|
| G1 | K2 plus a top-level `"extra":1` and a person key `"colour":"red"` | loads as K2. After one change the draft has neither key |
| G2 | K2 with Aisyah renamed to 20 copies of the Malaysian flag emoji (U+1F1F2 U+1F1FE, 20 grapheme clusters, 80 UTF-16 code units) | loads, and the name shows in full |
| G3 | K2 with `"__proto__":{"polluted":true}` inside `bill` | loads as K2, and `({}).polluted` is `undefined` in the page |
| G4 | K1 with `"spare":{"rule":"one","personId":"p2"}` and i5 `"who":["p1"]`, so Ben is on no item | loads. The splits are Top of the list's (Aisyah RM 44.78, Ben RM 0.00, Chen RM 24.48), the chip reads "Top of the list", and P1 shows One person checked with pills for Aisyah and Chen and none checked (CG-P7, ruled by the owner as recommended on 2026-10-13, ledger S1 row 2. It read "pending CG-P7" before the plan check, F1) |
| G5 | S2_V1 with `"spare":{"rule":"random","order":["p1"]}` inside `bill` | loads as K2 with spare Top of the list (D14). After one change the draft is version 2 with `"spare":{"rule":"top"}` |
| G6 | K2 with `"spare":{"rule":"top","extra":1}` | loads as K2. After one change the draft's `spare` is exactly `{"rule":"top"}` |
| G7 | S1_V1 unchanged (a draft saved by 1.0) | loads as K1 with spare Top of the list and both sections folded below 1024 px. After one change the draft is version 2 |
| G8 | K2 with five people, p1 `"Aisyah"`, p2 "Ben" + U+202E, p3 "Chen" + U+2067, p4 "A" + U+2028 + "B", p5 U+202E alone, and `"nextId":6`, each character written in the seed as its JSON escape (added 2026-10-16 in execute, H-10, the security finder's bill cut to its bidi and separator names) | loads with the names "Aisyah", "Ben", "Chen", "AB" and "" (labels Aisyah, Ben, Chen, AB, Person 5). The stored text is unchanged until the first change (R25), and after one change every stored name is plain (R62, D8) |
| G9 | K2 with Aisyah renamed "ABCDEFGHIJKLMNOPQRST" + U+202E (21 grapheme clusters as stored, added 2026-10-16 in execute, H-10) | loads with the name "ABCDEFGHIJKLMNOPQRST", because D8 counts the decoded name (D8 (c)) |
| G10 | K1 with i5 renamed "Char" + U+200F + " kuey teow" and S1_V1 with Ben renamed "Ben" + U+0000 (two drafts, added 2026-10-16 in execute, H-10) | each loads, the item as "Char kuey teow" and, in the version 1 draft, Ben as "Ben" |

## Functional test cases (Gherkin)
A table cell written in double quotes is literal text, spaces included. A splits row that "reads Aisyah RM 29.04 with "24.90 + 4.14"" has that `span.nm`, that `span.amt` and that `span.wk` with its `span.sr` children left out. "The proof reads RM 69.26 with "59.40 + 9.86"" is the same for the `span.amt` and `span.wk` of `div.r-check`. "The splits are" lists the `span.amt` of the rows in list order.

```gherkin
Feature: Split app, served and driven like a person would, in Chromium and in WebKit

  # ---------- Shell and boot ----------
  @R1 @both
  Scenario: The entry point loads only its own files
    # [Changed 2026-10-13, v1.1.0, S6, S7, S8] New head order with the colour scheme, viewport-fit, the new title and the icon link. src/system.css is again a byte copy, 1.0's trailing rule is gone.
    Given a fresh context with empty storage
    When I open "/"
    Then html has lang "en" and the head holds exactly, in this order, meta charset "utf-8", meta viewport "width=device-width, initial-scale=1, viewport-fit=cover", meta color-scheme "dark", the CSP meta of spec R38, title "Danial's Splity Tab", link rel "icon" type "image/svg+xml" href "src/icon.svg", link rel "stylesheet" href "src/system.css" and script type "module" src "src/main.js"
    And with every CRLF turned into LF in both files, src/system.css equals docs/design/system.css byte for byte, and both are 33070 bytes with SHA-256 "66807273b62f87e05caa931faac40a4bcac1cf7294b2cf38a9f046154b6d3c08" (the committed LF blob)
    And in a pytest temporary folder the same comparison passes for a CRLF copy of docs/design/system.css and reports an LF copy with one rule changed
    # Changed 2026-10-13 after the plan re-check (F12). It compared the raw SHA-256 of the two working files and quoted "eaa6a3b2753abf7848afb81b848aa411fbf3fa16b87b961a6170e042e1bdb7b0", the hash of this machine's CRLF working copy, so the result hung on the line-end settings. The second line is the comparison's own control.
    And no console error, page error or CSP violation was recorded
    And every request was a same-origin GET for "/", "/src/system.css", a file under "/src/" or "/favicon.ico"

  @R1 @both
  Scenario: The page works from a sub-path, as on GitHub Pages
    # [Changed 2026-10-13, v1.1.0, S6, S7] The screen expected is bill-empty, and the icon link resolves under the sub-path.
    Given a second server started with the project's parent folder as its root
    When I open "/split/"
    Then the bill-empty screen renders as the R2 cold boot scenario says, with no failed request, no console error and no CSP violation
    And the icon link's href property ends in "/split/src/icon.svg"
    And the static scan of index.html and src/ finds no src, href or import that starts with "/" or contains "://"

  @R2 @both
  Scenario: Cold boot is a new bill with no seed
    # [Changed 2026-10-13, v1.1.0, S7, S8] The first render is the bill-empty state, with People open below 1024 px, the blocked card and the strip.
    Given a fresh context with empty storage
    When I open "/"
    Then the person fields hold "Person 1" and "Person 2" and both Remove buttons have the disabled attribute
    And "Even" is checked, Subtotal is empty with placeholder "0.00" and p.err#evenErr carries hidden, Service charge holds "10" and SST holds "6"
    And #peopleBlk has data-open "true" with #peopleBtn aria-expanded "true", and #chargesBlk has data-open "false"
    And the card reads "Total Enter the subtotal to see the splits.", from div.r-total holding only span.r-label and div.r-empty holding an svg.ic that uses "#i-mark"
    And the strip reads "Enter the subtotal to see the splits." and #stripCopy is displayed and has the disabled attribute
    And localStorage has no "split.draft" key
    And no own property of window starts with "__"

  @R2 @static
  Scenario: No sample data ships
    Given the text of index.html and every file under src/
    Then none of these whole words appears: Aisyah, Ben, Chen, Devi, Farid, Grace, Hafiz, Indra, Jia Hui, Kumar, Lina, Mei Ling, Nasi lemak, Char kuey teow, Mee goreng, Satay

  @R3 @both
  Scenario Outline: The rendered markup matches its golden
    # [Changed 2026-10-13, v1.1.0, S7] Fifteen goldens less states.html, 40 state and width pairs, more attributes compared, and the v1.1.0 allowed differences.
    Given the state of <golden>, reached from the seed <seed> and then <after load> by real clicks, at each width in <widths>
    When the DOM walk in test_app.py compares the page's body with that of docs/design/<golden>.html at the same width
    Then tags, nesting, class lists, ids, own text, role, every aria-* attribute, type, name, the value of a radio, for, tabindex, data-open, disabled, maxlength, inputmode, autocomplete, placeholder, the href of every use, the checked state, and an input's value property against the golden's value attribute are equal
    And the walk skipped every element whose computed display is none, with what is inside it, on both sides, and every closed dialog
    And only the allowed differences 1 to 10 of spec.md exist
    Examples:
      | golden           | seed | after load                                                                                         | widths         |
      | bill-items       | K1   | none                                                                                               | 390, 360, 1280 |
      | bill-items-open  | K1   | a click on #peopleBtn, then on #chargesBtn                                                         | 390, 360       |
      | bill-even        | K2   | none                                                                                               | 390, 360, 1280 |
      | spare-sen        | K1   | below 1024 px a click on #splitsBtn and then on the sheet's spare chip, from 1024 px on #spareBtn   | 390, 360, 1280 |
      | spare-sen-one    | ONE  | as spare-sen                                                                                       | 390, 360, 1280 |
      | spare-sen-random | RND  | as spare-sen                                                                                       | 390, 360, 1280 |
      | splits-sheet     | K1   | a click on #splitsBtn                                                                              | 390, 360       |
      | new-bill-dialog  | K1   | a click on #newBill                                                                                | 390, 360, 1280 |
      | bill-empty       | none | none                                                                                               | 390, 360, 1280 |
      | rate-error       | RE   | none                                                                                               | 390, 360, 1280 |
      | bill-unassigned  | BU   | none                                                                                               | 390, 360, 1280 |
      | bill-unreadable  | B1   | none                                                                                               | 390, 360, 1280 |
      | bill-twelve      | T12  | none                                                                                               | 390, 360, 1280 |
      | bill-large       | W1   | none                                                                                               | 390, 360, 1280 |
    # 40 pairs. A 390 width means a 390 x 844 viewport, 360 means 360 x 780 and 1280 means 1280 x 800.

  @R3 @both
  Scenario: The walk sees every rendered element and flags each kind of change (the walk's control)
    # Added 2026-10-13 after the plan check (F6). The v1.1.0 form of 1.0's test_R3_the_walk_sees_every_rendered_element_and_flags_a_change, which neither qa listed. The walk skips by computed display on both sides and compares many attributes, so each kind of change must be seen reported.
    Given the K1 seed at 390 x 844 and the DOM walk of its body
    Then the walk holds more than 40 entries
    When a deep copy of the walk has the first toggle's aria-pressed changed from "true" to "false"
    Then first_diff of the walk and the copy names aria-pressed on that toggle, "true" on one side and "false" on the other
    When another copy has the data-open of #peopleBlk changed from "false" to "true"
    Then first_diff names data-open on that element
    When another copy drops the last li.item of ul.frame#itemList
    Then first_diff names a children difference at that list
    When I click Splits and walk the body again
    Then first_diff of the walk before and the walk after names a children difference at body that holds dialog.sheet-dlg on one side only, so an element displayed on one side only is reported and not skipped

  # ---------- People ----------
  @R4 @both
  Scenario: Person rows carry their names and labels
    # [Changed 2026-10-13, v1.1.0, S7] The list is ul.people#peopleList and the X icon comes through the sprite.
    Given the K1 seed and People opened first
    Then ul.people#peopleList has aria-labelledby "peopleH" and holds three li.field.person
    And their inputs have type "text", aria-labels "Person 1 name", "Person 2 name" and "Person 3 name", placeholders "Person 1", "Person 2" and "Person 3", maxlength 20, autocomplete "off" and the values "Aisyah", "Ben" and "Chen"
    And each li holds a button.icon-btn named "Remove Aisyah", "Remove Ben" or "Remove Chen", enabled, holding one svg.ic whose use has href "#i-x"

  @R4 @R5 @both
  Scenario: A blank name falls back to its position everywhere but the field
    # [Changed 2026-10-13, v1.1.0, S7] The splits row is on the card, and the People summary shows the fallback too.
    Given the K1 seed and People opened first
    When I replace the text of "Person 2 name" with nothing (Control+A, Backspace)
    Then that field shows the placeholder "Person 2" and its Remove button is named "Remove Person 2"
    And every item's toggle for that person reads "Person 2" and the card's second splits row reads "Person 2"
    When I click #peopleBtn to fold People
    Then the People summary reads "Aisyah, Person 2, Chen"

  @R5 @both
  Scenario: Renaming a person updates every place on each keystroke
    # [Changed 2026-10-13, v1.1.0, S7] Adds the People summary, the sheet and the picker pill, and copies from the sheet.
    Given the K1 seed and People opened first
    When I click the end of "Person 3 name" and type " Wei"
    Then after each key the toggles, the card's third splits row, the Remove name and the People summary's text show the text typed so far
    And the toggles in all four items read "Chen Wei" and the Remove button is "Remove Chen Wei"
    When I click Splits
    Then the sheet's third splits row reads "Chen Wei"
    When I click the sheet's Copy summary
    Then line 5 of window.testClipboardText is "Chen Wei RM 24.48"
    When I click the sheet's spare chip and choose "One person"
    Then the pills read "Aisyah", "Ben" and "Chen Wei"

  @R5 @both
  Scenario: Renaming an item updates its accessible names
    # [Changed 2026-10-13, v1.1.0, S7] The price field's name now follows the item name.
    Given the K1 seed
    When I replace the text of "Item 4 name" with "Satay"
    Then the item's Remove button is named "Remove Satay", its price field "Satay price in RM" and its group "Who had Satay"

  @R6 @both
  Scenario: Add person until the limit
    # [Changed 2026-10-13, v1.1.0, S7] People is open on a cold boot below 1024 px, and the disabled look is compared with bill-twelve.html.
    Given a cold boot
    When I click "Add person"
    Then there are 3 person rows, the third input is empty with placeholder "Person 3", and all three Remove buttons are enabled
    When I click "Add person" 9 more times
    Then there are 12 person rows and #addPerson has the disabled attribute
    And a Tab from #peopleBtn moves focus straight to "Person 1 name"
    When the viewport becomes 1280 x 800
    Then #addPerson is equal to the golden's #addPerson in bill-twelve.html at 1280 x 800, plus cursor "not-allowed"
    When I click "Add person" again
    Then there are still 12 person rows

  @R6 @both
  Scenario: Removing anyone from twelve turns Add person back on
    # Added 2026-10-13 after the plan check (F5). bill-twelve.md, "Removing anyone turns Add person back on". Also the v1.1.0 form of 1.0's test_R6_a_restored_twelve_person_bill_shows_the_limit_state (task A5).
    Given the S8 seed and People opened first
    Then there are 12 person rows and #addPerson has the disabled attribute, and the stored text equals the S8 seed (a restore writes nothing)
    When I click "Remove Mei Ling"
    Then there are 11 person rows, #addPerson has no disabled attribute, and "Person 11 name" has focus
    And a Tab from #peopleBtn moves focus to #addPerson
    When I click "Add person"
    Then there are 12 person rows, the new field is empty with placeholder "Person 12", and #addPerson has the disabled attribute again

  @R7 @both
  Scenario: Remove a person and they leave every item
    # [Changed 2026-10-13, v1.1.0, S7] The unassigned message reads "splits", the item gets the needs marker, and the disabled look is compared with bill-empty.html.
    Given the K1 seed and People opened first
    When I click "Remove Chen"
    Then two person rows remain, "Aisyah" and "Ben", and both Remove buttons have the disabled attribute and are equal to the golden's person Remove buttons in bill-empty.html, plus cursor
    And every "Who had" group holds exactly the toggles "Aisyah" and "Ben"
    And the li.item of "Mee goreng mamak" has class "needs" and no other li.item has it
    And the card's div.r-msg and the strip read "1 item still needs a person. Tap who had it to see the splits."

  # Added 2026-10-09, ORCH, security audit SEC-01 (1.0). A double click, a triple click and a double tap are two or three presses, and the
  # first one can move a different control under the pointer. The guard (swallowRepeatClicks) cancels the repeats at the document.
  @R7 @both
  Scenario Outline: A repeat press on the last Remove removes that row and adds nothing
    # [Changed 2026-10-13, v1.1.0, S7] The proof is the body recorder and the draft, because Add person no longer slides under the pointer. Sizes are 360 x 780, 390 x 844 and 1280 x 800.
    Given <bill> is the stored draft, the viewport is <size>, People opened first when <button> is a person's, and a body recorder
    When I <gesture> at the centre of <button>
    Then one row fewer shows and the draft is the bill that one click on <button> leaves (that person or item gone, no blank row, "nextId" unchanged)
    And only press 1 and click 1 reached the page
    And focus is on <focus>
    Examples:
      | bill                       | button                  | focus          |
      | K2                         | Remove Chen             | Person 2 name  |
      | S8                         | Remove Mei Ling         | Person 11 name |
      | K1                         | Remove Satay, 10 sticks | Item 3 name    |
      | K1 with only its last item | Remove Satay, 10 sticks | Add item       |
    # Sizes 360 x 780, 390 x 844, 1280 x 800. Gestures, a single click (the control), a mouse double click, a mouse triple click, a touch double tap.

  @R34 @both
  Scenario Outline: After a double click or double tap on a middle Remove, focus is where one click puts it
    # [Changed 2026-10-13, v1.1.0, S7] R34 is unchanged. People is opened first below 1024 px.
    Given <bill> is the stored draft and People opened first
    When I double click, or double tap, <button>
    Then one row is gone and focus is on <focus>, not on the next Remove button or the page body
    Examples:
      | bill                         | button                | focus         |
      | K1                           | Remove Char kuey teow | Item 2 name   |
      | K2 with five people P1 to P5 | Remove P2             | Person 2 name |

  @R7 @both
  Scenario: A press of its own is never held back
    # [Changed 2026-10-13, v1.1.0, S7] The second click is proven by the body recorder. Add person sits in the heading row now and is no longer under the pointer.
    # [Changed 2026-10-14 in execute, ledger H-04] Every press here is a mouse click, and for a mouse "the guard goes by click count, not by time or place" stays true under spec R57 (b). A tap goes by time and place as well, ~~awaiting the owner's ruling~~ ruled USER 2026-10-14 20:00, "Time + place (Recommended)" (scenario "A slow second tap, or a quick tap elsewhere, is never held back").
    Given the K2 seed, People opened first, and a body recorder
    When I click the centre of "Remove Chen" and then, as a separate click with click count 1, the same point
    Then the recorder counted two presses and two clicks, and the draft holds the two people Aisyah and Ben (the guard goes by click count, not by time or place)
    When I click "Remove Nasi lemak ayam" in the K1 bill and then double click a toggle
    Then both presses and both clicks of the double click reach the page and the toggle ends where it began (the guard ends at the first press that is not a repeat, RG-CR-02)
    When I click "Remove Chen" in the K2 bill with People opened first and then double click "Person 1 name"
    Then the word "Aisyah" is selected

  # Added 2026-10-09, ORCH, regression RG-CR-01 (1.0). Add person and Add item arm the guard.
  @R6 @both
  Scenario Outline: A repeat press on Add person adds one person and keeps it
    # [Changed 2026-10-13, v1.1.0, S7] Add person is in the heading row, so no new Remove lies under it. The guard is proven by the body recorder.
    Given the K2 bill with <people> people, P1 to P<people>, is the stored draft, the viewport is <size>, People opened first, and a body recorder
    When I <gesture> at <place> of "Add person"
    Then one person row more shows and the draft is that bill with one blank person added (the id counter moved once)
    And only press 1 and click 1 reached the page
    And focus is on the name field of the new person
    Examples:
      | people     | place                        |
      | 2, 3, 4, 5 | the middle of the button     |
      | 2, 3, 4, 5 | 22 px in from its right edge |
    # Sizes 360 x 780, 390 x 844, 1280 x 800. Gestures, a mouse double click, a mouse triple click, a touch double tap.

  @R12 @both
  Scenario Outline: A repeat press on Add item adds one item and never reaches the page
    # [Changed 2026-10-13, v1.1.0, S7] Sizes are 360 x 780, 390 x 844 and 1280 x 800.
    Given K1 cut to its first <items> items is the stored draft, the viewport is <size>, and a body recorder
    When I <gesture> at <place> of "Add item"
    Then one item row more shows and the draft is that bill with one blank item added
    And only press 1 and click 1 reached the page
    And focus is on the name field of the new item
    Examples:
      | items | place                        |
      | 1, 4  | the middle of the button     |
      | 1, 4  | 22 px in from its right edge |
    # Sizes and gestures as above.

  # Added 2026-10-10, ORCH, regression RG-CR-08 (1.0). A Remove also ignores a repeat press itself (isRepeatClick), for the case where
  # no click armed the guard and a layout shift puts a Remove under the second press.
  @R7 @R12 @both
  Scenario Outline: A repeat press on a chip under a pending price error never removes the item
    # [Changed 2026-10-13, v1.1.0, S7] In the v1.1.0 layout the price error sits under its item's row and the Remove does not move, so the 1.0 press point no longer exists. The scout now asserts that, and the press goes to a point that stays on the same chip.
    Given the K1-8 seed and the viewport <width> x 3000
    And "Nasi lemak ayam price in RM" holds "abc" and still has focus
    When a scout page with the same seed and width leaves the field by Tab and reads, for every 4 px point of every toggle of item 1 as laid out before the error, what lies under it once the error shows
    Then no such point lies over the Remove of item 1 or of any other item
    And at least one point of the "Aisyah" toggle lies on that same toggle before and after the error
    When a second page, with the price field still focused and a body recorder, does a <gesture> at that point
    Then the recorder counted one click per press of the gesture and each one toggled "Aisyah" (a double click leaves her on i4, a triple click takes her off)
    And the draft still holds the four items i4, i5, i6 and i7, and p.err#ie1 shows
    Examples:
      | width    |
      | 375, 390 |
    # Gestures, a mouse double click, a mouse triple click, a touch double tap. If the scout ever finds a point over a Remove, the test fails and names the point, so a later layout that brings the 1.0 hazard back is caught.

  @R42 @both
  Scenario: Two people may have the same name
    # [Changed 2026-10-13, v1.1.0, S7] The receipt says "splits", the copy is from the strip, and the working is "items + charges".
    Given a cold boot
    When I replace "Person 1 name" with "Ben" and "Person 2 name" with "Ben", click "Add person" and type "Chen" into "Person 3 name"
    And I type "100.00" into Subtotal
    Then every p.err carries hidden, #notes holds no note, and the first two person fields both hold "Ben"
    And the card's splits read Ben RM 38.87, Ben RM 38.87 and Chen RM 38.86 and #addsUp reads RM 116.60
    And two Remove buttons are named "Remove Ben"
    When I click #stripCopy
    Then lines 3 and 4 of window.testClipboardText are both "Ben RM 38.87"
    When I click "By item", click "Add item", type "Tea" in "Item 1 name", type "10.00" in "Tea price in RM" and click the second "Ben" toggle in "Who had Tea"
    Then only the second "Ben" toggle has aria-pressed "true"
    And the card's rows read Ben RM 0.00 with "0.00 + 0.00", Ben RM 11.66 with "10.00 + 1.66" and Chen RM 0.00 with "0.00 + 0.00", and the proof reads RM 11.66 with "10.00 + 1.66"
    When I click the second "Remove Ben"
    Then two person rows remain, "Ben" and "Chen", and the card's div.r-msg reads "1 item still needs a person. Tap who had it to see the splits."
    And the draft holds two people, p1 "Ben" and p3 "Chen"

  # ---------- Split and Subtotal ----------
  @R8 @both
  Scenario: Switching modes keeps both sets of input
    # [Changed 2026-10-13, v1.1.0, S7] The block ids and the strip Total.
    Given a cold boot
    When I replace the text of Subtotal with "100.00"
    And I click "By item", click "Add item", type "Tea" in "Item 1 name", type "5.00" in "Tea price in RM" and click the "Person 1" toggle
    Then #evenBlock is not in the DOM and #itemsBlock is
    When I click "Even"
    Then Subtotal holds "100.00", #itemsBlock is not in the DOM, and the strip reads "Total RM 116.60"
    When I click "By item"
    Then item 1 is "Tea", "5.00", with "Person 1" pressed, and the strip reads "Total RM 5.83"
    When I reload the page
    Then the same by-item screen shows, and "Even" again shows "100.00"

  @R8 @both
  Scenario: Arrow keys move between the modes
    # [Changed 2026-10-13, v1.1.0, S5] Focus reaches the radio by Tab, never by a label click, because WebKit does not focus a radio on a mouse click (R59).
    Given a cold boot
    When I press Tab until #modeEven has focus and press ArrowRight
    Then #modeItem is checked and has focus, and #itemsBlock is in the DOM

  @R9 @both
  Scenario: The subtotal field drives the even split
    # [Changed 2026-10-13, v1.1.0, S7] The ids evenSub, evenField and evenErr, the error paragraph always present, and no spare line for two people.
    Given a cold boot
    Then div.blk#evenBlock holds label.blk-h.solo with for "evenSub" reading "Subtotal", then div.field.money.sub-field#evenField holding span.unit "RM" with aria-hidden "true" and input#evenSub, then p.err#evenErr carrying hidden
    And input#evenSub has type "text", inputmode "decimal", autocomplete "off", placeholder "0.00", aria-label "Subtotal in RM", aria-describedby "evenErr" and aria-invalid "false"
    When I type "100.00" into Subtotal
    Then the card's splits read Person 1 RM 58.30 and Person 2 RM 58.30, #addsUp reads RM 116.60, and the card holds no div.r-spare

  @R10 @both
  Scenario Outline: An inline error waits for the field to be left
    # [Changed 2026-10-13, v1.1.0, S7] The v1.1.0 ids and markup (is-bad, hidden and aria-invalid both ways) and the rate's aria-describedby with the hint first (rule 13).
    Given <setup>
    When I replace the text of <field> with "<bad>"
    Then p.err#<error> carries hidden, the input has aria-invalid "false", its div.field has no class "is-bad", and its aria-describedby is "<described>"
    When I leave the field
    Then p.err#<error> has no hidden attribute and reads "<message>", the input has aria-invalid "true", its div.field has class "is-bad", and its aria-describedby is "<described while shown>"
    When I click back into <field>, press Control+A and type "<good>" key by key
    Then right after the first key that makes the text valid, before I leave the field, p.err#<error> carries hidden again, aria-invalid is "false", "is-bad" is gone and aria-describedby is "<described>"
    Examples:
      | setup                             | field                        | bad    | message                    | error   | described  | described while shown | good  |
      | a cold boot                       | Subtotal                     | 0      | Enter an amount like 12.50 | evenErr | evenErr    | evenErr               | 12.50 |
      | the K1 seed                       | "Char kuey teow price in RM" | 13.505 | Enter an amount like 12.50 | ie2     | ie2        | ie2                   | 13.50 |
      | a cold boot, Charges opened first | "Service charge"             | 31     | Enter a rate from 0 to 30  | svcErr  | chargeHint | chargeHint svcErr     | 10    |
      | a cold boot, Charges opened first | "SST"                        | 20.01  | Enter a rate from 0 to 20  | sstErr  | chargeHint | chargeHint sstErr     | 6     |

  @R10 @both
  Scenario: An empty field never shows an error
    # [Changed 2026-10-13, v1.1.0, S7] Error paragraphs are always present, so the check is on hidden and aria-invalid. The folded Charges row shows its marker, and the message reads "splits".
    Given a cold boot
    When I click Subtotal and leave the field
    And I open Charges first, replace the text of "Service charge" with nothing and leave the field
    Then every p.err on the page carries hidden and no input has aria-invalid "true"
    And the card and the strip read "Check the charges to see the splits."
    When I click #chargesBtn to fold Charges
    Then #chargesBtn has class "is-bad" and #chargesSum holds the warning-circle icon and "Check service charge"

  @R10 @both
  Scenario: Typing invalid text in a focused field does not show the error early
    # [Changed 2026-10-13, v1.1.0, S7] The message reads "splits".
    Given a cold boot
    When I type "abc" into Subtotal without leaving it
    Then p.err#evenErr carries hidden and the card and the strip read "Enter the subtotal to see the splits."

  @R10 @both
  Scenario: A restored invalid field shows its error at once
    # [Changed 2026-10-13, v1.1.0, S7] Version 2 seed and the v1.1.0 markup.
    Given the K2 seed with "subtotalText":"0"
    When the page loads
    Then p.err#evenErr shows "Enter an amount like 12.50" without any interaction, #evenSub has aria-invalid "true" and #evenField has class "is-bad"

  @R10 @both
  Scenario: An error survives a mode switch
    # [Changed 2026-10-13, v1.1.0, S7] The v1.1.0 ids.
    Given a cold boot with "0" typed in Subtotal and the field left
    When I click "By item" and then "Even"
    Then p.err#evenErr shows and #evenField has class "is-bad"

  # Added 2026-10-09, ORCH, RD-3 (1.0). A press that ends the edit of an invalid field must still land on the control it started on.
  @R10 @R13 @both
  Scenario Outline: A press below an invalid field lands on the control it started on
    # [Changed 2026-10-13, v1.1.0, S7] The v1.1.0 ids and targets. For the Subtotal the target is the Charges header row above it, which the error does not move, and the check is that the click reaches it once and the error shows after.
    Given <setup>
    When I replace the text of <field> with "<bad>" and the error is not showing yet
    And I press once on <target>, its middle found before the press, with the mouse and again in a has_touch context with a touch tap
    Then the click event reached <target> exactly once
    And p.err#<error> shows after the press and the input has aria-invalid "true"
    Examples:
      | setup                             | field                        | bad    | target                                          | error   |
      | a cold boot                       | Subtotal                     | 0      | the Charges header row #chargesBtn              | evenErr |
      | the K1 seed                       | "Char kuey teow price in RM" | 13.505 | the "Aisyah" toggle in "Who had Char kuey teow" | ie2     |
      | a cold boot, Charges opened first | "Service charge"             | 31     | p.hint#chargeHint                               | svcErr  |
      | a cold boot, Charges opened first | "SST"                        | 25     | p.hint#chargeHint                               | sstErr  |
    # The Subtotal row runs below 1024 px, where the header row is shown.
    # [Changed 2026-10-14 in execute, ledger S5 rows 4 and 5, class (b)] On the two p.hint#chargeHint rows the press is the mouse only. Their touch tap is the @per_engine scenario below (spec R59 (3)), because WebKit sends no mouse event and no click to text that is not a control. Task A6.

  @R10 @R59 @per_engine
  Scenario Outline: A touch tap on the charges hint below an invalid rate
    # Added 2026-10-14 in execute (ledger S5 rows 4 and 5, sorting.md, tap_on_hint in diagnostics/sorting_diagnostics.json). Both results follow R10 (a), the error shows when the field is left. Whether an iPhone does the same is a UAT case.
    Given a cold boot in a has_touch context, Charges opened first
    When I replace the text of <field> with "<bad>" and the error is not showing yet
    # Changed 2026-10-15 in execute, planner touch before A18 (ledger S7 row 22, Q-A6-1). The line read "a body recorder is added". A body listener makes WebKit send the hint mousedown and click, so the WebKit line could not hold (spec R59 (3), A6's probe qa/hint-tap/20261014-225644/probe.json). The window half sees every event first and changes nothing.
    And ~~a body recorder is added~~ a window recorder is added (the window half of "A body recorder", Phrases), and I tap p.hint#chargeHint once at its middle, found before the tap
    Then In Chromium the click event reached p.hint#chargeHint exactly once, <field> no longer has focus, p.err#<error> shows and the input has aria-invalid "true"
    And In WebKit the recorder saw no mousedown and no click, <field> still has focus, p.err#<error> carries hidden and the input has aria-invalid "false"
    Examples:
      | field            | bad | error  |
      | "Service charge" | 31  | svcErr |
      | "SST"            | 25  | sstErr |

  @R13 @both
  Scenario: A tap on a person below an invalid, unflagged price toggles them and then shows the error
    # [Changed 2026-10-13, v1.1.0, S7] The v1.1.0 price name and error id.
    Given the K1 seed
    When I replace the text of "Char kuey teow price in RM" with "13.505"
    And I press the "Aisyah" toggle of "Who had Char kuey teow" with the mouse, and in a has_touch context with a touch tap
    Then that toggle has aria-pressed "true", i5's who in the draft holds p1 and p2, and p.err#ie2 shows

  @R10 @both
  Scenario: The error waits for the release, and only a press holds it back
    # [Changed 2026-10-13, v1.1.0, S7] The v1.1.0 ids. The empty space is beside h1.word in the top bar, and SST is reached with Charges opened first.
    Given the K1 seed and "13.505" typed in "Char kuey teow price in RM"
    When the mouse button goes down on a toggle
    Then the field has lost focus and p.err#ie2 still carries hidden
    When the button comes up
    Then p.err#ie2 shows
    And pressing empty space in the top bar beside h1.word behaves the same for "SST" holding "25", with Charges opened first
    And a Tab from the field shows its error at once, even after an earlier press

  # ---------- Items ----------
  @R11 @both
  Scenario: Item rows carry their names and labels
    # [Changed 2026-10-13, v1.1.0, S7] The price name follows the item, the placeholder is "0.00", and each price points at its error paragraph.
    Given the K1 seed
    Then ul.frame#itemList has aria-labelledby "itemsH" and holds four li.item, each with a div.item-row
    And item j (1 to 4) has a name input with aria-label "Item j name", placeholder "Item j", maxlength 40 and autocomplete "off"
    And the price inputs are named "Nasi lemak ayam price in RM", "Char kuey teow price in RM", "Mee goreng mamak price in RM" and "Satay, 10 sticks price in RM", each with placeholder "0.00", inputmode "decimal", autocomplete "off", aria-invalid "false" and aria-describedby "ie1" to "ie4", inside div.field.money after span.unit "RM"
    And the Remove buttons are named "Remove Nasi lemak ayam", "Remove Char kuey teow", "Remove Mee goreng mamak" and "Remove Satay, 10 sticks"
    And p.err#ie1 to p.err#ie4 carry hidden and each is the last child of its div.item-row

  @R12 @both
  Scenario: Add an item, remove one, and reach the limit
    # [Changed 2026-10-13, v1.1.0, S7] The first item's message is the no-prices one, and the disabled look is compared with bill-twelve.html.
    Given a cold boot and I click "By item"
    When I click "Add item"
    Then one item row exists with an empty name (placeholder "Item 1"), an empty price and no toggle pressed
    And the card and the strip read "Add each item and tap who had it to see the splits."
    When I click "Add item" 49 more times
    Then 50 item rows exist and #addItem has the disabled attribute
    And at 1280 x 800 #addItem is equal to the golden's #addPerson in bill-twelve.html, plus cursor "not-allowed", not its width
    When I click the Remove button of item 2
    Then 49 item rows exist and #addItem is enabled

  @R13 @both
  Scenario: Tapping a person on an item
    # [Changed 2026-10-13, v1.1.0, S1, S7] Splits with their working on the card, and the spare line.
    Given the K1 seed at 1280 x 800
    When I click the "Ben" toggle in "Who had Satay, 10 sticks"
    Then that toggle has aria-pressed "true"
    And the card's rows read Aisyah RM 25.54 with "21.90 + 3.64", Ben RM 22.74 with "19.50 + 3.24" and Chen RM 20.98 with "18.00 + 2.98"
    And the proof reads RM 69.26 with "59.40 + 9.86", and #spareLine reads "2 sen left over"
    When I click the same toggle again
    Then it has aria-pressed "false" and the K1 splits return

  @R14 @both
  Scenario: A price error sits in the item row
    # [Changed 2026-10-13, v1.1.0, S7] Compared with the price piece of states.html.
    Given the K1 seed
    When I replace the text of "Char kuey teow price in RM" with "13.505" and leave the field
    Then p.err#ie2 is the last child of that item's div.item-row and shows
    # Changed 2026-10-15 in execute, planner touch before A18 (ledger S7 row 24, F-A8-1). The golden CSS sets no text-align on p.err, so it computes "start" in the piece and in the app, and "right aligned" is .item-row .err { justify-self: end } (spec R14).
    And p.err#ie2 is equal to the golden's p.err#ie2 in states.html (the S2 price piece), plus ~~text-align "right"~~ justify-self "end", its right edge at the price field's right edge (within 0.5 px)
    And the price's div.field.money has class "is-bad" and is equal to the golden's wrapper in the same piece
    And the price input has aria-describedby "ie2"

  # ---------- Charges ----------
  @R15 @both
  Scenario: The Charges block and its defaults
    # [Changed 2026-10-13, v1.1.0, S7] The v1.1.0 markup, no hidden " in percent", and the hint in aria-describedby.
    Given a cold boot and Charges opened first
    Then h2.blk-h.solo#chargesH reads "Charges" and is not displayed below 1024 px
    And "Service charge" (label.lbl for "svc") names input#svc holding "10", and "SST" (label.lbl for "sst") names input#sst holding "6", each in div.field.pct followed by span.unit "%" with aria-hidden "true"
    And both inputs have type "text", inputmode "decimal", autocomplete "off", aria-invalid "false" and aria-describedby "chargeHint"
    And p.err#svcErr reads "Enter a rate from 0 to 30" and p.err#sstErr reads "Enter a rate from 0 to 20", both carry hidden and both start with the warning-circle icon
    And p.hint#chargeHint reads "Set a charge to 0 if your bill already includes it."

  @R15 @both
  Scenario: A rate error names the hint first and then its error
    # [Changed 2026-10-13, v1.1.0, S7] 1.0 put the error id first. Rule 13 puts the hint first.
    Given a cold boot and Charges opened first
    When I replace the text of "Service charge" with "31" and leave the field
    Then p.err#svcErr shows "Enter a rate from 0 to 30" in the Service charge cell
    And the input's aria-describedby is "chargeHint svcErr" and its div.field.pct has class "is-bad"

  @R15 @R19 @both
  Scenario: A charge of 0 is allowed and still shown
    # [Changed 2026-10-13, v1.1.0, S1, S7] Bill lines without working, and the spare line.
    Given the K2 seed at 1280 x 800
    When I replace the text of "Service charge" with "0"
    Then no error shows, and the card's lines read "Service 0%" RM 0.00 and "SST 6%" RM 6.00
    And the splits are RM 35.34, RM 35.33, RM 35.33 and #spareLine reads "1 sen left over"

  # ---------- The receipt ----------
  @R16 @both
  Scenario: The receipt follows every keystroke and stays quiet
    # [Changed 2026-10-13, v1.1.0, S7] The card, the sheet and the strip. Only the status paragraphs and the notes are live.
    Given the K2 seed at 1280 x 800
    When I replace the text of Subtotal with "5"
    Then #rTotal reads "RM 5.83" and the splits are RM 1.95, RM 1.94, RM 1.94
    When I type "0"
    Then #rTotal reads "RM 58.30" and the splits are RM 19.44, RM 19.43, RM 19.43
    And the only elements on the page with aria-live or a role of status, alert or log are #cardStatus, #stripStatus and the div.note children of #notes, and #card, #rbody and #strip carry neither
    When the viewport becomes 390 x 844 and I click Splits
    Then the sheet's p.status with role "status" is the only such element inside #splitsDlg

  @R17 @both
  Scenario Outline: When the splits cannot be worked out
    # [Changed 2026-10-13, v1.1.0, S7] The blocked card (Total label and the mark), the strip message with Copy summary disabled, the "splits" messages, and "no-prices" for a by-item bill with no valid price (core R18).
    Given <setup>
    Then the card holds div.r-total with only span.r-label "Total", then div.r-empty holding an svg.ic that uses "#i-mark" and a p reading "<message>", and nothing else
    And the strip holds p.s-msg#stripMsg reading "<message>" with no svg, and #stripCopy is displayed and has the disabled attribute
    When I click Splits
    Then the sheet holds the same blocked receipt
    Examples:
      | setup                                                                    | message                                             |
      | the K2 seed with "Service charge" emptied, Charges opened first          | Check the charges to see the splits.                |
      | the K1 seed with "SST" replaced by "25", Charges opened first            | Check the charges to see the splits.                |
      | the K2 seed with Subtotal emptied                                        | Enter the subtotal to see the splits.               |
      | a cold boot                                                              | Enter the subtotal to see the splits.               |
      | a cold boot, then a click on "By item"                                   | Add each item and tap who had it to see the splits. |
      | a cold boot, "By item", then "Add item"                                  | Add each item and tap who had it to see the splits. |
      | the K1 seed with "Nasi lemak ayam price in RM" replaced by "abc"         | Give every item a price to see the splits.          |
      | the K1 seed with every price replaced by "abc"                           | Add each item and tap who had it to see the splits. |

  @R18 @both
  Scenario: Items that still need a person
    # [Changed 2026-10-13, v1.1.0, S7] The card keeps the Total and lines, then div.r-msg. The strip shows the message with its icon. The item gets the amber needs marker, which replaces 1.0's "no error styling on the items".
    Given the K1 seed
    When I click the "Chen" toggle in "Who had Mee goreng mamak"
    Then the card reads the Total RM 69.26 and the lines RM 59.40, RM 5.94 and RM 3.92, then holds div.r-rule and then div.r-msg with the warning-circle icon and "1 item still needs a person. Tap who had it to see the splits.", and nothing after it
    And the strip's p.s-msg#stripMsg holds the warning-circle icon and the same text, and #stripCopy has the disabled attribute
    And the li.item of "Mee goreng mamak" has class "needs" and no other li.item has it
    When I click the "Ben" toggle in "Who had Char kuey teow"
    Then the message is "2 items still need a person. Tap who had each one to see the splits." and two li.item have class "needs"
    When I press both toggles again
    Then the splits, the proof and Copy summary return with the K1 numbers and no li.item has class "needs"

  @R19 @both
  Scenario Outline: Total and bill lines
    # [Changed 2026-10-13, v1.1.0, S7] The Total figure has a span.cur, and the bill lines are a dl with no working.
    Given the <seed> seed at 1280 x 800
    Then #rTotal holds span.cur "RM " and then "<figure>"
    And dl.r-lines holds three div rows reading "Subtotal" <sub>, "<svc label>" <svc> and "<sst label>" <sst>, with no working text
    And div.r-rule with aria-hidden "true" follows it
    Examples:
      | seed | figure | sub       | svc label   | svc      | sst label | sst     |
      | K2   | 116.60 | RM 100.00 | Service 10% | RM 10.00 | SST 6%    | RM 6.60 |
      | K1   | 69.26  | RM 59.40  | Service 10% | RM 5.94  | SST 6%    | RM 3.92 |

  @R20 @both
  Scenario: The even split from a cold boot (key flow 1)
    # [Changed 2026-10-13, v1.1.0, S1, S7] The splits list, the proof, the spare line and chip, the strip, and the sheet.
    Given a cold boot
    When I replace "Person 1 name" with "Aisyah" and "Person 2 name" with "Ben", click "Add person" and type "Chen" into "Person 3 name"
    And I type "100.00" into Subtotal
    Then the card's ul.r-splits#splits has aria-labelledby "splitsH" and the splits read Aisyah RM 38.87, Ben RM 38.87, Chen RM 38.86
    And #addsUp reads RM 116.60, #spareLine reads "2 sen left over" and #spareBtn reads "Top of the list"
    And the strip reads "Total RM 116.60"
    When I click Splits
    Then the sheet holds h2#sheetSplitsH "Splits" and a list with aria-labelledby "sheetSplitsH" whose rows read as the card's

  @R20 @both
  Scenario: More than six people list in two columns on the desktop
    # [Changed 2026-10-13, v1.1.0, S7] New in R20 (PD-17).
    Given the T12 seed at 1280 x 800
    Then #splits has class "many" and its style property "--rows" reads "6"
    And rows 1 to 6 share one left edge, rows 7 to 12 share another one further right, and row 7 is level with row 1
    When the viewport becomes 390 x 844 and I click Splits
    Then the sheet's twelve rows share one left edge
    And with the K2 seed #splits has no class "many", and with the T12I seed (by item, twelve people) it has none either

  @R20 @both
  # [Added 2026-10-16 in execute, code review CR-S5-7, the test is d728076, test_R20_seven_to_eleven_people_list_in_two_columns_on_the_desktop.]
  # Only an odd count tells ceil(n / 2) from a floor, which would open a third column. Seen failing first on the
  # reviewer's mutant U4 (a floor) at 7, 9 and 11 people.
  Scenario Outline: Seven to eleven people list in two columns on the desktop
    Given the T12 seed cut to its first <n> people, with "nextId" <n> + 1, at 1280 x 800
    Then #splits has class list "r-splits many", its style property "--rows" reads "<rows>" and it holds <n> rows
    And rows 1 to <rows> share one left edge, the rest share another one further right, and the first of the second column is level with row 1
    Examples:
      | n  | rows |
      | 7  | 4    |
      | 8  | 4    |
      | 9  | 5    |
      | 10 | 5    |
      | 11 | 6    |

  @R21 @both
  Scenario: The by-item split from gestures (key flow 2)
    # [Changed 2026-10-13, v1.1.0, S1, S7] The working sits under each split with its hidden words, and the legend reads "items + charges".
    Given the even bill of key flow 1
    When I click "By item" and, for each K1 item in order, click "Add item", type its name and price and click its people's toggles
    Then div.r-head holds h2#splitsH "Splits" and a span with aria-hidden "true" reading "items + charges"
    And the card's rows read Aisyah RM 29.04 with "24.90 + 4.14", Ben RM 15.74 with "13.50 + 2.24" and Chen RM 24.48 with "21.00 + 3.48"
    And each span.wk's textContent reads "Items <items> + charges <charges>", for Aisyah "Items 24.90 + charges 4.14"
    And the proof reads RM 69.26 with "59.40 + 9.86", and #spareLine reads "1 sen left over"

  @R21 @both
  Scenario: Someone who had nothing is still listed
    # [Changed 2026-10-13, v1.1.0, S7] Starts from the I2 seed. The working reads "0.00 + 0.00".
    Given the I2 seed at 1280 x 800
    Then the card's rows read Aisyah RM 0.00 with "0.00 + 0.00", Ben RM 14.59 with "12.51 + 2.08" and Chen RM 2.91 with "2.50 + 0.41"
    And the proof reads RM 17.50 with "15.01 + 2.49" and #spareLine reads "2 sen left over"

  # ---------- Copy summary ----------
  @R22 @both
  Scenario Outline: Copy summary puts the exact text on the clipboard
    # [Changed 2026-10-13, v1.1.0, S7] Three places to copy from, and the status has the check icon.
    Given the <seed> seed at <size>
    When I click <button>
    Then window.testClipboardText equals the <block> block of split-core spec R24 exactly, joined with "\n", and window.testClipboardWrites is 1
    And every status paragraph present (#cardStatus, #stripStatus, and the sheet's p.status when the sheet is open) reads "Summary copied", holds an svg.ic whose use has href "#i-check" before the text, and has the class list "status"
    Examples:
      | seed | size       | button                                 | block |
      | K2   | 1280 x 800 | the card's #copyBtn                    | S2    |
      | K2   | 390 x 844  | the sheet's Copy summary, after Splits | S2    |
      | K2   | 390 x 844  | the strip's #stripCopy                 | S2    |
      | K1   | 1280 x 800 | the card's #copyBtn                    | S1    |
      | K1   | 390 x 844  | the sheet's Copy summary, after Splits | S1    |
      | K1   | 390 x 844  | the strip's #stripCopy                 | S1    |

  @R22 @both
  Scenario: A bill from RM 1,000 copies with thousands commas
    # [Changed 2026-10-13, v1.1.0, S7] New in R22. CG-P1 ruled by the owner (USER, 2026-10-13), the comma is in the copied summary too.
    Given the W1 seed at 1280 x 800
    When I click #copyBtn
    Then window.testClipboardText is exactly the six lines "Bill split", "Total RM 1,193.87 (subtotal RM 1,023.90, service 10% RM 102.39, SST 6% RM 67.58)", "Aisyah RM 1,153.65", "Ben RM 15.74", "Chen RM 24.48" and "Adds up to RM 1,193.87", joined with "\n"

  @R23 @both
  Scenario: The browser blocks the clipboard
    # [Changed 2026-10-13, v1.1.0, S7] Class "status is-fail" with the warning-circle icon on the strip and the card, and the strip grows.
    Given the K2 seed with the clipboard script reject.js
    When I click #stripCopy
    Then #stripStatus and #cardStatus read "Could not copy. Your browser blocked the clipboard.", hold the warning-circle icon before the text, and have the class list "status is-fail"
    And the strip is 153 px tall and the root's --strip-h reads "153px"
    And no page error was logged and the draft is unchanged

  @R23 @both
  Scenario: The clipboard API is missing
    # [Changed 2026-10-13, v1.1.0, S7] The v1.1.0 status markup.
    Given the K2 seed with the clipboard script missing.js
    When I click #stripCopy
    Then #stripStatus reads "Could not copy. Your browser blocked the clipboard." with the class list "status is-fail", and no page error was logged

  @R24 @both
  Scenario: The status lasts until the next change to the bill
    # [Changed 2026-10-13, v1.1.0, S7] Reversed. 1.0 kept the status through edits (PD-5). Rule 10 clears it at the next change, and nothing else clears it.
    Given the K2 seed
    Then #cardStatus and #stripStatus exist, are empty and are not displayed
    When I click #stripCopy
    Then #stripStatus and #cardStatus read "Summary copied"
    When I click empty space in the top bar, click #peopleBtn twice, click Splits, press Escape, open the New bill dialog, click Cancel, and resize the viewport to 400 x 844
    Then #stripStatus and #cardStatus still read "Summary copied", and the sheet's p.status read it too while the sheet was open
    When I open People first and type "x" at the end of "Person 1 name"
    Then #cardStatus and #stripStatus are empty and not displayed
    When I click #stripCopy and reload
    Then every status paragraph is empty

  # ---------- Draft ----------
  @R25 @both
  Scenario Outline: Every change is saved
    # [Changed 2026-10-13, v1.1.0, S1] Version 2, with the spare choice.
    Given a cold boot
    When I <change>
    Then the draft is { "version": 2, "bill": ... } whose bill <expectation>
    Examples:
      | change                                                                                                    | expectation                                              |
      | replace "Person 1 name" with "A"                                                                          | has people[0].name "A" and spare {"rule":"top"}          |
      | click "Add person"                                                                                        | has 3 people and nextId 4                                |
      | type "1" into Subtotal                                                                                    | has subtotalText "1"                                     |
      | click "By item"                                                                                           | has mode "item"                                          |
      | click "By item", then "Add item"                                                                          | has one item { id "i3", name "", priceText "", who [] }  |
      | open Charges first and replace "SST" with "8"                                                             | has sstText "8"                                          |
      | click "Add person", type "100.00" into Subtotal, click Splits, click the sheet's spare chip, choose "One person" | has spare {"rule":"one","personId":"p1"}           |

  @R25 @both
  Scenario: Leaving a field, copying, folding and the sheet do not save
    # [Changed 2026-10-13, v1.1.0, S7] Adds the section toggle and the sheet, and proves "no write" with the write counter.
    Given the K2 seed with the write counter count-set.js, loaded, and the stored text noted
    When I click Subtotal and leave it, click #stripCopy, click #peopleBtn twice, click Splits and press Escape
    Then window.testSetItemCalls is 0 and the stored text is unchanged

  @R26 @both
  Scenario: Come back later (key flow 3)
    # [Changed 2026-10-13, v1.1.0, S1, S7] Sections fold on a reload, and the K1 splits are read on the card with the spare line.
    Given the K1 bill built by gestures in one page from a cold boot, with Subtotal "100.00" typed earlier in even mode
    When I close the page and open "/" in a new page of the same context
    Then every person, item, price, toggle and rate is as before, "By item" is checked, and #peopleBlk and #chargesBlk have data-open "false"
    And the card's splits match K1, #spareLine reads "1 sen left over" and #spareBtn reads "Top of the list"
    When I click "Even"
    Then Subtotal holds "100.00" and the splits are RM 38.87, RM 38.87, RM 38.86

  @R26 @both
  Scenario: A drawn order comes back after a reload
    # [Changed 2026-10-13, v1.1.0, S1] New in R26.
    Given the RND seed
    When the page loads and then reloads
    Then both times the card's splits read Aisyah RM 38.86, Ben RM 38.87, Chen RM 38.87, #pickAgain comes before #spareBtn, and #spareBtn reads "At random"
    And the draft's spare is still {"rule":"random","order":["p2","p3","p1"]}

  @R26 @R61 @both
  Scenario Outline: Odd but readable drafts load
    # [Changed 2026-10-13, v1.1.0, S1] G4 to G7 added, the version 2 spare choice and drafts saved by 1.0.
    # Changed 2026-10-13 after the plan check (F1). The G4 row said "pending CG-P7". The owner ruled it as recommended.
    Given the <id> seed
    When the page loads
    Then #notes holds no note and <expected>
    Examples:
      | id | expected                                                                                                                     |
      | G1 | the K2 screen shows, and after one edit the draft has no "extra" or "colour" key                                            |
      | G2 | Person 1 shows the 20 flags in full                                                                                         |
      | G3 | the K2 screen shows and ({}).polluted is undefined                                                                          |
      | G4 | the card's splits read Aisyah RM 44.78, Ben RM 0.00, Chen RM 24.48 and #spareBtn reads "Top of the list" (CG-P7, ruled 2026-10-13, ledger S1 row 2) |
      | G5 | the K2 screen shows with #spareBtn reading "Top of the list", and after one edit the draft is version 2 with spare {"rule":"top"} |
      | G6 | the K2 screen shows, and after one edit the draft's spare is exactly {"rule":"top"}                                         |
      | G7 | the K1 screen shows with #spareBtn reading "Top of the list" and both sections folded, and after one edit the draft is version 2 |

  @R27 @R61 @both
  Scenario Outline: An unreadable draft starts a new bill with a note
    # [Changed 2026-10-13, v1.1.0, S1, S7] The note sits in #notes in the top bar, People opens below 1024 px, B4 is version 3, and B25 to B32 test the spare choice.
    Given the <id> seed
    When the page loads
    Then #notes holds div.note with role "status", holding the warning-circle icon, a p reading "Your saved bill could not be read, so a new one was started." and button.icon-btn#dismissNote named "Dismiss note" with the X icon
    And the bill-empty screen shows under it with #peopleBlk data-open "true"
    And the draft is { "version": 2, "bill": <newBill() of split-core R10, with spare {"rule":"top"}> }
    When I reload
    Then no note shows, and the bill-empty screen shows with People open (CG-P4, ruled by the owner)
    Examples:
      | id  |
      | B1  |
      | B2  |
      | B3  |
      | B4  |
      | B5  |
      | B6  |
      | B7  |
      | B8  |
      | B9  |
      | B10 |
      | B11 |
      | B12 |
      | B13 |
      | B14 |
      | B15 |
      | B16 |
      | B17 |
      | B18 |
      | B19 |
      | B20 |
      | B21 |
      | B22 |
      | B23 |
      | B24 |
      | B25 |
      | B26 |
      | B27 |
      | B28 |
      | B29 |
      | B30 |
      | B31 |
      | B32 |

  @R27 @both
  Scenario: Dismissing the note
    # [Changed 2026-10-13, v1.1.0, S7] Focus goes to New bill (rule 12). It went to Person 1 name in 1.0.
    Given the B1 seed
    When I click "New bill" and then "Start new bill"
    Then the note still shows in #notes, in the same place (Start new bill does not show, hide or move it)
    When I click "Dismiss note"
    Then the note is no longer in the DOM and #newBill has focus
    And opening the New bill dialog and pressing Start new bill never brings a note back
    # [Added 2026-10-16 in execute, code review CR-R1, ORCH, ledger S7 row 46] The repeat press of a double click on Dismiss note is the outline "A repeat press on Dismiss note acts as one press at every width" at the end of this block (task A23).

  @R28 @both
  Scenario Outline: The app works without storage
    # [Changed 2026-10-13, v1.1.0, S4] "No message about storage shows" is removed. What the user is told is R46 and R47.
    Given a cold boot with the storage driver <driver>
    When I type "100.00" into Subtotal and click "Add person"
    Then the strip reads "Total RM 116.60" and the card holds three splits rows
    And no page error, console error or CSP violation was recorded
    Examples:
      | driver                                                 |
      | D-b fail-get.js, the window.localStorage getter throws |
      | D-c fail-getitem.js, getItem throws                    |
      | D-a fail-set.js, setItem throws a QuotaExceededError   |

  # ---------- New bill ----------
  @R29 @both
  Scenario: The dialog opens with the safe choice focused
    # [Changed 2026-10-13, v1.1.0, S7] Opened over K1, the v1.1.0 ids, and the page behind does not scroll.
    Given the K1 seed
    When I click "New bill" with the mouse
    Then dialog.modal#newDlg matches ":modal", is named "Start a new bill?" and described by "This clears the people, items and amounts."
    And "Cancel" has focus
    When I press Tab
    Then "Start new bill" has focus
    When I press Tab
    Then "Cancel" has focus
    When I press Shift+Tab twice
    Then "Cancel" has focus
    And a mouse wheel of 400 px over the scrim leaves window.scrollY unchanged
    # Tab wrapping is 1.0's PD-14. The v1.1.0 new-bill-dialog.md no longer mentions it, and spec R29 keeps it. Flagged for the plan checker.
    # [Added 2026-10-14 in execute, ledger S5 rows 4 and 5, class (b)] A height read here matches within 0.5 px (Phrases). WebKit lays the .app box out at 843.984375 px at 390 x 844 and Chromium at 844 (spec R59 (1)). The 1.0 test asserts exactly 844 and fails in WebKit until A16 rewrites it to this scenario.

  @R30 @both
  Scenario Outline: Leaving the dialog without starting over
    # [Changed 2026-10-13, v1.1.0, S7] R30 is unchanged. The backdrop point is (20, 20) from LINKS.json, and the control under the backdrop is the By item half of the Split switch.
    # [Added 2026-10-14 in execute, ledger S5 rows 4 and 5, class (b)] "press Escape" waits for the dialog's close event (Phrases, spec R59 (2)). The 1.0 test's [escape] case reads focus right after the key press and fails in WebKit until A16 rewrites it.
    Given the K2 seed and the stored text noted
    When I click "New bill" and then <close>
    Then the dialog is closed and <extra>
    And the screen still shows the K2 bill and the stored text is unchanged
    And "New bill" has focus
    Examples:
      | close                                                          | extra                                                     |
      | click "Cancel"                                                 | nothing else changed                                      |
      | press Escape                                                   | nothing else changed                                      |
      | click the backdrop at (20, 20)                                 | nothing else changed                                      |
      | click the backdrop over the "By item" label of the Split switch | "Even" is still checked and #modeItem does not have focus |

  # Added 2026-10-09, ORCH, security audit I-1 (1.0). Opening arms the guard that closing already armed (R30, CR-01).
  @R29 @both
  Scenario Outline: A repeat press on New bill leaves the dialog open
    # [Changed 2026-10-13, v1.1.0, S7] Over K1, sizes 360 x 780, 390 x 844 and 1280 x 800, proven with the body recorder.
    Given the K1 seed at <size> and a body recorder
    When I <gesture> at the centre of "New bill"
    Then the dialog is open, "Cancel" has focus, only press 1 and click 1 reached the page, and the stored text is unchanged
    Examples:
      | size                             | gesture                                                  |
      | 360 x 780, 390 x 844, 1280 x 800 | mouse double click, mouse triple click, touch double tap |

  @R30 @both
  Scenario Outline: After a double click on New bill one deliberate click still closes it
    # [Changed 2026-10-13, v1.1.0, S7] The backdrop point is (20, 20).
    # [Added 2026-10-14 in execute, ledger S5 rows 4 and 5, class (b)] "press Escape" waits for the dialog's close event (Phrases, spec R59 (2)). The 1.0 test's [escape] case fails in WebKit until A16 rewrites it.
    Given the K1 seed and a double click on "New bill" has opened the dialog
    When I <close>
    Then the dialog is closed, "New bill" has focus and the stored text is unchanged
    Examples:
      | close                          |
      | click "Cancel"                 |
      | click the backdrop at (20, 20) |
      | press Escape                   |

  @R30 @both
  Scenario Outline: The second press of a double activation that closed the dialog never reaches the page
    # Added 2026-10-14 in execute (ledger H-04, S5 rows 4 and 7). The v1.1.0 form of the 1.0 CR-01 tests test_R30_a_double_click_or_double_tap_on_cancel_changes_nothing, test_R30_the_second_click_of_a_double_activation_never_reaches_the_page and test_R30_a_triple_click_on_cancel_changes_nothing_either, written by A16. ~~In WebKit the touch rows fail until A17 (H-04 class (a), spec R57 (b)).~~ [Changed 2026-10-14 in execute, ORCH. A17 builds before A16, so the touch rows pass in WebKit from the start, through spec R57 (b).] The body recorder proves the cancel, so no row passes only because the layout put something harmless under the second press.
    Given the K1 seed at <size>, the stored text noted, the dialog opened by a click on "New bill", and a body recorder
    When I <gesture> at <point>
    Then the dialog is closed, "New bill" has focus, and only press 1 and click 1 reached the page
    And <after>
    Examples:
      | point                          | size                                       | after                                                                   |
      | the centre of "Cancel"         | 360 x 640, 375 x 667, 412 x 732, 390 x 844 | the screen and the stored text are unchanged                            |
      | the centre of "Start new bill" | 390 x 844                                  | the bill-empty screen shows and the draft is { "version": 2, "bill": <newBill()> } |
      | the backdrop at (20, 20)       | 390 x 844                                  | the screen and the stored text are unchanged                            |
    # Gestures, a mouse double click and a touch double tap on every row, and a mouse triple click on "Cancel" at 360 x 640.

  @R29 @both
  Scenario: The keyboard and the next press are not held back
    # [Changed 2026-10-13, v1.1.0, S7] Over K1, proven with the body recorder.
    Given the K1 seed and a body recorder
    When I press Tab until "New bill" has focus, press Enter, Enter on "Cancel" and Enter on "New bill" again
    Then the dialog opens, closes and opens again, with "Cancel" focused each time it is open (a key press has click count 0)
    When I press Escape, open the dialog by a click, press Escape again and double click a toggle
    Then both presses and both clicks of the double click reach the page

  @R31 @both
  Scenario: Start over (key flow 4)
    # [Changed 2026-10-13, v1.1.0, S7] From K1 to bill-empty with People open below 1024 px, a version 2 draft, and a reload that still opens People (CG-P4 ruled by the owner).
    Given the K1 seed
    When I click "New bill" and then "Start new bill"
    Then the dialog is closed, "New bill" has focus, and the bill-empty screen shows with #peopleBlk data-open "true" and #chargesBlk data-open "false"
    And "Person 1 name" and "Person 2 name" hold "Person 1" and "Person 2", "Even" is checked, Subtotal is empty, and Service charge and SST hold "10" and "6"
    And the draft is { "version": 2, "bill": <newBill() of split-core R10> }, whose spare is {"rule":"top"}
    When I reload
    Then the bill-empty screen shows with People open

  @R31 @both
  Scenario: Start over clears the copy status and the spare choice
    # [Changed 2026-10-13, v1.1.0, S1, S7] The status lives on the strip and the card, and the seed has a drawn order, so the reset of the spare choice shows.
    Given the RND seed
    When I click #stripCopy
    Then #stripStatus reads "Summary copied"
    When I click "New bill" and then "Start new bill"
    Then #stripStatus is empty and not displayed, the card holds no p.status, and the card and the strip read "Enter the subtotal to see the splits."
    And the draft's spare is {"rule":"top"}
    When I type "100.00" into Subtotal
    Then #cardStatus exists and is empty, and #stripStatus is empty

  @R31 @both
  Scenario Outline: Start over clears the error flags
    # [Changed 2026-10-13, v1.1.0, S7] The v1.1.0 ids and markup, and Charges opened first below 1024 px.
    Given <setup>
    And the error of that field shows
    When I click "New bill" and then "Start new bill"
    And <prepare>
    Then every p.err carries hidden, no input has aria-invalid "true" and no div.field has class "is-bad"
    When I replace the text of <field> with "abc" without leaving the field
    Then still every p.err carries hidden and no input has aria-invalid "true" (R10 a, a stale flag would show the error at once)
    When I leave the field
    Then the error of <field> shows, so the rule still works after a start over
    Examples:
      | setup                                                                                          | prepare                                                                             | field                |
      | the K2 seed, Subtotal replaced with "0" and the field left                                     | nothing                                                                             | Subtotal             |
      | the K1 seed, "Char kuey teow price in RM" replaced with "13.505" and the field left (item i5)  | click "By item" and click "Add item" 3 times (the new items get ids i3, i4 and i5) | "Item 3 price in RM" |
      | a cold boot, Charges opened first, "Service charge" replaced with "31" and the field left      | open Charges first                                                                  | "Service charge"     |
      | a cold boot, Charges opened first, "SST" replaced with "25" and the field left                 | open Charges first                                                                  | "SST"                |

  # ---------- Keyboard, focus, layout, motion ----------
  @R32 @both
  Scenario Outline: Tab order follows the golden
    # [Changed 2026-10-13, v1.1.0, S7] The v1.1.0 DOM order on a phone and on the desktop, inside the sheet and inside P1.
    Given <state> at <size>
    When I press Tab repeatedly from <start>
    Then the focused controls' accessible names come in exactly this order, <order>
    Examples:
      | state                      | size       | start                                       | order |
      | the K1 seed                | 390 x 844  | the top of the page                         | New bill, People, Charges, By item, Add item, then for each item j "Item j name", "<item> price in RM", "Remove <item>", Aisyah, Ben, Chen, then Splits, Copy summary (31 stops) |
      | a cold boot (bill-empty)   | 390 x 844  | the top of the page                         | New bill, People, Add person, Person 1 name, Person 2 name, Charges, Even, Subtotal in RM, Splits |
      | the B1 seed                | 390 x 844  | the top of the page                         | Dismiss note, New bill, People, Add person, Person 1 name, Person 2 name, Charges, Even, Subtotal in RM, Splits |
      | the K1 seed                | 1280 x 800 | the top of the page                         | New bill, Spare sen: Top of the list. Change, Copy summary, Add person, Person 1 name, Remove Aisyah, Person 2 name, Remove Ben, Person 3 name, Remove Chen, Service charge, SST, By item, Add item, then for each item its name, price, Remove, Aisyah, Ben, Chen |
      | the K1 seed, sheet open    | 390 x 844  | the sheet, which has focus on open          | Close, Spare sen: Top of the list. Change, Copy summary |
      | the RND seed, sheet open   | 390 x 844  | the sheet                                   | Close, Pick again, Spare sen: At random. Change, Copy summary |
      | the K1 seed, P1 open       | 1280 x 800 | Close, reached by Shift+Tab from the checked choice | Close, Top of the list |
      | the ONE seed, P1 open      | 1280 x 800 | Close                                       | Close, One person, Ben |
      | the RND seed, P1 open      | 1280 x 800 | Close                                       | Close, At random, Pick again |
    # If the A0 baseline finds that WebKit's Tab skips buttons (Safari's default without "Press Tab to highlight each item"), it is sorted (b) and this outline asserts each engine's measured order (R59).

  @R32 @both
  Scenario: Every focused control shows the one ring
    # [Changed 2026-10-13, v1.1.0, S7] The v1.1.0 ring of system.md Focus.
    Given the K1 seed with People and Charges opened by keyboard (Enter on each header row)
    When I Tab to a name field, a person's Remove, the checked half of the Split switch, a header row, a toggle, an item's Remove, Splits and Copy summary
    Then each focus ring's outline-style, outline-width, outline-color and outline-offset equal the golden's on the same element focused by Tab, in bill-items-open.html at 390 x 844 and in bill-items.html at 1280 x 800
    And that is a 2 px solid rgb(163, 170, 255) outline at a 2 px offset, drawn on the div.field wrapper for an input, inset at -3 px on a person's Remove, inset at -5 px on the focused half of the Split switch, and 8 px wider than the row on each side for a header row
    And with the RE seed, "Service charge" focused by Tab keeps its red edge (the is-bad box-shadow) and gains the ring

  @R33 @both
  Scenario Outline: Typing never loses its place
    # [Changed 2026-10-13, v1.1.0, S7] R33 is unchanged. People and Charges are opened first below 1024 px, and the price is named by its item.
    Given the K1 seed (the K2 seed for Subtotal), with People and Charges opened first
    When I take a handle to <field>, click it, press Control+A and type "<text>" key by key
    Then after every key the same element is document.activeElement and its selectionStart equals the number of characters typed so far
    When I press Home and type "X"
    Then the value starts with "X" and selectionStart is 1
    Examples:
      | field                         | text   |
      | "Person 1 name"               | Aisyah |
      | "Item 1 name"                 | Nasi   |
      | "Nasi lemak ayam price in RM" | 15.90  |
      | Subtotal                      | 100.00 |
      | "Service charge"              | 12.5   |

  @R33 @chromium_only
  # reason. Needs a CDP session (Input.imeSetComposition, Input.insertText), which Playwright gives in Chromium only.
  Scenario: IME composition survives a render
    # [Changed 2026-10-13, v1.1.0, S5] Marked chromium_only (R58, R59). People is opened first.
    Given the K1 seed, People opened first, and a CDP session on the page
    When I focus "Person 1 name", send Input.imeSetComposition for "jia" and then Input.insertText "家"
    Then the field value ends with "家", the same element has focus and no composed text was lost

  @R34 @both
  Scenario Outline: Focus after adding or removing
    # [Changed 2026-10-13, v1.1.0, S7] R34 is unchanged. People is opened first below 1024 px.
    Given <setup>, with People opened first
    When I <action>
    Then <target> has focus
    Examples:
      | setup                                  | action                          | target                           |
      | a cold boot                            | click "Add person"              | "Person 3 name"                  |
      | the K1 seed                            | click "Remove Ben"              | "Person 2 name" (Chen)           |
      | the K1 seed                            | click "Remove Chen"             | "Person 2 name" (Ben)            |
      | the K1 seed                            | click "Add item"                | "Item 5 name"                    |
      | the K1 seed                            | click "Remove Char kuey teow"   | "Item 2 name" (Mee goreng mamak) |
      | the K1 seed                            | click "Remove Satay, 10 sticks" | "Item 3 name"                    |
      | a cold boot, "By item", one item added | click "Remove Item 1"           | "Add item"                       |

  @R35 @both
  Scenario Outline: No horizontal overflow in any golden state
    # [Changed 2026-10-13, v1.1.0, S2, S7] Every golden state at 360, 390 and 1280, with the v1.1.0 grid and order. The 1.0 size scenarios (Subtotal 160 px, status 40 px, dialog 328 px, note 1040 px) are replaced by FE element checklist rows.
    Given the state of <golden>, reached as in the R3 outline, at each width in <widths>
    Then document.documentElement.scrollWidth is at most window.innerWidth and no displayed element's right edge is beyond window.innerWidth
    And where People's list is displayed it has 2 columns at 360 and 390 and 3 at 1280
    And below 1024 px the displayed blocks come in the order top bar, People, Charges, Split, then Items or Subtotal, and #strip is fixed at the bottom of the viewport
    Examples:
      | golden           | widths         |
      | bill-items       | 390, 360, 1280 |
      | bill-items-open  | 390, 360       |
      | bill-even        | 390, 360, 1280 |
      | spare-sen        | 390, 360, 1280 |
      | spare-sen-one    | 390, 360, 1280 |
      | spare-sen-random | 390, 360, 1280 |
      | splits-sheet     | 390, 360       |
      | new-bill-dialog  | 390, 360, 1280 |
      | bill-empty       | 390, 360, 1280 |
      | rate-error       | 390, 360, 1280 |
      | bill-unassigned  | 390, 360, 1280 |
      | bill-unreadable  | 390, 360, 1280 |
      | bill-twelve      | 390, 360, 1280 |
      | bill-large       | 390, 360, 1280 |

  @R36 @both
  Scenario: Reduced motion moves nothing
    # [Changed 2026-10-13, v1.1.0, S7] The seven control classes of v1.1.0, and getAnimations() after the new interactions.
    Given the K1 seed with reduced motion "reduce"
    Then every value in the computed transition-duration of ".btn", ".chip-btn", ".tap", ".icon-btn" and ".mode-sw label" is "0s", and the same holds for ".choice" and ".pill-face", read with P1 open over the ONE seed
    And document.getAnimations() is empty right after load, right after a toggle click, right after a click on #peopleBtn opens People, right after Splits opens the sheet and right after the chip opens P1

  @R36 @both
  Scenario: With motion allowed nothing loops
    # [Changed 2026-10-13, v1.1.0, S7] The foil runs once, and the section reveal is one Web Animation (PD-22).
    # Changed 2026-10-15 in execute, planner touch before A18 (ledger S7 row 20, F-A4-1). "Empty" cannot hold, because the foil sweeps have fill "both" in system.css and a finished one stays in the list (A4 measured it in both engines). "No animation is running" means no animation in document.getAnimations() has playState "running". The strip is not displayed at 1280, so the resize to 390 starts its sweep (0.15 s delay, 1.8 s), hence the 3 s wait before the click.
    Given the K1 seed at 1280 x 800 with reduced motion "no-preference"
    Then right after load document.getAnimations() holds at least one CSSAnimation (the foil sweep and the light across the card), and 3 s after load ~~it is empty~~ no animation is running
    When the viewport becomes 390 x 844, 3 s pass, and I click #peopleBtn to open People
    Then document.getAnimations() holds exactly one animation that is neither a CSSAnimation nor a CSSTransition, its target is div.sec-body#peopleBody and its duration is 200 ms, and #peopleBody has no style attribute
    And 1 s after the click ~~document.getAnimations() is empty~~ no animation is running and the reveal is no longer in document.getAnimations()
    When I click a toggle, click Splits, click the sheet's spare chip, press Escape and press Escape again
    Then 1 s after each of these ~~document.getAnimations() is empty~~ no animation is running

  # ---------- Security ----------
  @R37 @both
  Scenario: Names are shown as text, never as markup
    # [Changed 2026-10-13, v1.1.0, S7] The People summary, the splits rows, the picker pill and the price name are new sinks, and svg elements are counted by the v1.1.0 classes. CG-9 of 1.0 stands.
    Given the K1 seed, People opened first, and the number of svg elements under body noted
    When I replace "Person 1 name" with "<svg onload=f()>", "Item 1 name" with "<img src=x onerror=alert(1)>" and "Item 2 name" with "\"><script>alert(2)</script>"
    Then "Person 1 name" holds exactly "<svg onload=f()>" (16 characters) and "Item 1 name" holds exactly "<img src=x onerror=alert(1)>" (28 characters)
    And that person's toggle in every item, the card's first splits row and the Remove button ("Remove <svg onload=f()>") show those exact characters
    And after a click on #peopleBtn folds People, the People summary's text starts with "<svg onload=f()>"
    And item 1's Remove is named "Remove <img src=x onerror=alert(1)>", its price "<img src=x onerror=alert(1)> price in RM" and its group "Who had <img src=x onerror=alert(1)>"
    And no img or script element exists under body, the number of svg elements under body is the number noted, every svg under body is svg.sprite, svg.mark, svg.ic or svg.seal, and no element has an onload or onerror attribute
    And no dialog event fired and no page error was logged
    When I click Splits, then the sheet's spare chip, then "One person"
    Then the first pill's span.pill-face holds one svg.ic and the text "<svg onload=f()>" as a text node
    When I press Escape twice and click #stripCopy
    Then line 3 of window.testClipboardText is "<svg onload=f()> RM 29.04"

  @R37 @static
  Scenario: No HTML sink in the source
    Given the static scan of src/ and index.html
    Then src/ holds none of innerHTML, outerHTML, insertAdjacentHTML, document.write, eval(, new Function(, setAttribute("on, createContextualFragment or DOMParser
    And neither index.html nor src/ holds a "<template" tag

  @R38 @both
  Scenario: The Content Security Policy is exact and never violated
    # [Changed 2026-10-13, v1.1.0, S5, S6] The violation listener of both engines is the suite-wide check, beside Chromium's console text.
    Given index.html and the evidence of the whole suite in this engine
    Then index.html carries exactly the CSP meta of spec R38 and no inline script, no style element and no style attribute
    And window.testCspViolations stayed empty in every scenario of the run

  @R38 @both
  Scenario Outline: The strict policy blocks nothing the app needs
    # [Changed 2026-10-13, v1.1.0, S6, S7] Dark theme, the four CSSOM targets, the tab icon, and the sheet and P1.
    Given <state> in a context without bypass_csp
    Then the stylesheet applies (body's computed background-color equals the golden's body background-color at the same width)
    And the module ran (<proof>)
    And style attributes exist only on the root element (holding only --strip-h), ul.r-splits.many (only --rows), #spareDlg (only left and bottom, from 1024 px) and #sheetScroll (only padding-bottom, while P1 and the Splits sheet are both open below 1024 px, wording changed 2026-10-13 after the plan check, N2)
    And no CSP violation was recorded and no page error was logged
    Examples:
      | state                                                     | proof                                                         |
      | a cold boot                                               | the card reads "Total Enter the subtotal to see the splits."  |
      | the K1 seed                                               | the card's splits and proof show the K1 numbers               |
      | the K1 seed with the New bill dialog open                 | the dialog is open over the K1 card                           |
      | the K1 seed at 390 x 844 with the Splits sheet and P1 open | #sheetScroll's style holds padding-bottom 271px              |
      | the K2 seed at 1280 x 800 with P1 open                    | #spareDlg's style holds left 574px and its bottom edge is at 560.8 |

  @R38 @static
  Scenario: Code writes style only to the four allowed targets
    # [Changed 2026-10-13, v1.1.0, S6, S7] New scan for the narrow CSSOM allowance and the one Web Animation (PD-22).
    Given the static scan of src/
    Then it holds none of setAttribute("style", cssText, insertRule, new CSSStyleSheet, adoptedStyleSheets, "<style" or a direct ".style.<property> =" write
    And every style.setProperty and style.removeProperty call names one of "--strip-h", "--rows", "left", "bottom" or "padding-bottom"
    And ".animate(" appears exactly once, in the section reveal of R48
    And a planted copy of a file with an extra style.setProperty("color", ...) call, scanned in a pytest temporary folder, is reported (the scan has teeth)

  # Changed 2026-10-08, plan check BLOCK, CG-10 (1.0). The namespace string is exempt in exactly one position.
  @R39 @static
  Scenario: Nothing leaves the device
    # [Changed 2026-10-13, v1.1.0, S6] A second exemption, the root xmlns of src/icon.svg, and a teeth test.
    Given the static scan of src/ and index.html
    Then none of fetch(, XMLHttpRequest, WebSocket, EventSource, sendBeacon or serviceWorker appears in src/
    And after removing every occurrence of createElementNS( followed by the exact string "http://www.w3.org/2000/svg" as its first argument (in single, double or backtick quotes), and the one xmlns attribute of the root element of src/icon.svg, no string with a scheme remains in any file under src/
    And the string "http://www.w3.org/2000/svg" appears nowhere else in src/ (not a second argument, not a comment, not another call, not a second time in src/icon.svg), and no other namespace or URL appears
    And index.html holds no "://" at all
    And a planted second xmlns in a copy of src/icon.svg, and a planted "http://www.w3.org/1999/xlink" in a copy of a JavaScript file, each scanned in a pytest temporary folder, are both reported

  @R39 @both
  Scenario: Every request stays on the device
    # [Changed 2026-10-13, v1.1.0, S5, S6] Both engines, and /src/icon.svg allowed.
    Given the request logs of every scenario of the suite in this engine
    Then every request is a same-origin GET for "/", "/src/system.css", a file under "/src/" ("/src/icon.svg" allowed, not required) or "/favicon.ico"

  @R39 @R44 @both
  Scenario: The run-time icons come from createElementNS
    # [Changed 2026-10-13, v1.1.0, S6, S7] Icons are svg.ic or svg.seal with one use into the sprite.
    Given the static scan of src/ and the K1 seed page at 1280 x 800
    Then at least one call createElementNS("http://www.w3.org/2000/svg", ...) exists in src/
    And every svg under body is svg.sprite (the first child of body), svg.mark (one, in .brand), svg.ic or svg.seal
    And every svg.ic and svg.seal has aria-hidden "true" and focusable "false" and holds exactly one use, whose href is "#i-" followed by one of x, plus, copy, check, caret, shuffle, warning, warning-circle, mark or seal-check

  # ---------- Gates ----------
  @R40 @gate
  Scenario: Looks right
    # [Changed 2026-10-13, v1.1.0, S5, S7] 40 pairs with two controls, Chromium only (ledger S5 row 2).
    When the fidelity gate below runs in Chromium
    Then both controls behave as written, all 40 state and width pairs pass, and every FE element checklist row passes

  @R40 @static
  Scenario: The runner uses the Python that runs pytest and stays Chromium only
    # [Changed 2026-10-13, v1.1.0, S5] The runner has no engine option and lists the 40 pairs.
    Given the source of tests/browser/fidelity/run.py
    Then it starts the harness as [sys.executable, <path to fidelity.py>, ...]
    And it holds no path to a virtual environment (no ".sdlc-harness"), never runs pip or any installer, and has no "--engine" option
    And it lists exactly the 40 pairs of the fidelity table with their seed and after-load scripts
    And importing playwright, PIL and numpy in the Python that runs the test succeeds

  @R40 @static
  Scenario: The fidelity seeds equal seeds.py and carry the clipboard stand-in
    # [Changed 2026-10-13, v1.1.0, S1, S7] Version 2 seeds, one file per seed the fidelity table uses.
    # Changed 2026-10-13 after the plan check (B2). The title was "The fidelity seeds equal seeds.py", and each file held only the setItem statement, so the candidate of a pair whose after-load script presses a control had no clipboard stand-in.
    Given every tests/browser/fidelity/seed-*.js and tests/browser/clipboard/recorder.js
    Then each seed file starts with the text of recorder.js byte for byte
    And the rest of the file is exactly one statement, localStorage.setItem("split.draft", '<seed>'), whose seed equals its seed in seeds.py
    And there is one file for each of K1, K2, ONE, RND, RE, BU, B1, T12 and W1
    And a planted copy of seed-s1.js with the recorder part cut, and one with a second setItem statement, each checked in a pytest temporary folder, are both reported

  @R40 @chromium_only
  # reason. The after-load scripts serve the fidelity gate, which runs in Chromium only (ledger S5 row 2).
  Scenario: An after-load script presses nothing without the clipboard stand-in
    # Added 2026-10-13 after the plan check (B2). Constitution, Browser gates. The check is the control of the stand-in rule, so it must be seen failing.
    Given the K1 seed in a context made by rig.new_context with clipboard "missing", and a body recorder
    When each of open-sections.js, open-splits.js, open-spare.js and open-new-bill.js runs inside an async function, as the harness runs it
    Then each rejects with an Error whose message is "clipboard stand-in missing", the recorder counted no mousedown and no click, and no section, sheet or dialog opened
    Given the K1 seed in a context made by rig.new_context with the default recorder.js
    When open-splits.js runs the same way
    Then #splitsDlg matches ":modal", window.testClipboardWrites is 0, and document.activeElement is body with no element matching ":focus-visible"

  @R41 @gate
  Scenario: Works right
    # [Changed 2026-10-13, v1.1.0, S5, S7] The v1.1.0 headline flow, in Chromium and in WebKit.
    When the cold-boot live-e2e gate below runs with --engine chromium and with --engine webkit
    Then it passes in each, and each run's evidence folder exists and is listed after the run
    # Added 2026-10-13 after the plan check (B3). A green run counts only beside the RED capture of its control in the same engine (next scenario).
    And each green run's summary.json records "control": null, and a run whose summary records "control": "seeded" never counts as green
    # Added 2026-10-13 after the plan re-check (F11).

  @R41 @gate
  Scenario Outline: The live gate fails when the app starts from a saved bill (control)
    # Added 2026-10-13 after the plan check (B3). Constitution, Gates and evidence. Run just before the green run of the same engine, against the same server.
    Given the app is served as for the gate, and live_e2e.py runs with --engine <engine> --control seeded
    When the script makes its one context through rig.new_context with storage_state holding the K2 seed, and runs its steps from step 1
    Then the run stops at step 1 with pass false, and steps.log names step 1's failed assertions, the screen is not bill-empty (#peopleBlk has data-open "false" and the strip reads "Total RM 116.60", not "Enter the subtotal to see the splits.") and split.draft is present
    And step 1's check that navigator.clipboard.writeText is the stand-in passed, so the RED comes from the cold-boot property and not from the clipboard check
    And summary.json records "control": "seeded", the engine, ~~browser.version~~ "browser_version" (Playwright's browser.version, wording as built, QA-S5-3, changed 2026-10-16 in execute) and pass false
    And the evidence folder name ends in "-<engine>-control", it holds no earlier run's files, and it is listed after the run and never overwritten
    Examples:
      | engine   |
      | chromium |
      | webkit   |

  @R41 @static
  Scenario: The gate script makes a cold context except on its control path
    # Added 2026-10-13 after the plan re-check (F11). The v1.1.0 form of three sealed 1.0 tests in tests/browser/test_app.py, rewritten in task A20. test_R41_the_gate_uses_real_gestures_and_reads_only, test_R41_the_step_log_puts_gesture_and_assertion_in_their_own_fields and test_R41_the_gate_installs_the_clipboard_recorder_and_nothing_else (renamed to say both scripts).
    Given the text and the syntax tree of tests/browser/live_e2e.py, read through one helper that takes a path
    Then "bypass_csp" and "permissions" are never a keyword argument in it
    And "storage_state" is a keyword argument exactly once, on the script's one rig.new_context call, and its value is a conditional expression whose test is an == comparison of the parsed --control value with "seeded" and whose else branch is None
    And the one add_argument call for "--control" has choices ["seeded"] and default None
    And no attribute in it is fill, dispatch_event, check, set_checked, select_option, route, add_init_script or launch_persistent_context, the one context comes from rig.new_context, and every page.evaluate argument is on the test's read-only list, which holds reads only (window.testCspViolations among them)
    And the gate.step calls are numbered 1 to 9, one per step of the flow below, each with a gesture field that starts with one of the 1.0 action words and an assertion field that does not
    And INIT_SCRIPTS is exactly ["tests/browser/clipboard/recorder.js", "tests/browser/csp/listener.js"]
    And three planted copies of live_e2e.py checked in a pytest temporary folder are each reported, one that passes storage_state with no condition, one whose else branch is the K2 state, and one that adds bypass_csp=False to the rig.new_context call
    # Added 2026-10-14 in execute (ledger H-05, spec R41 and R59 (4)). A WebKit screenshot adds a stylesheet the policy refuses, so the capture is a screencast frame.
    And no attribute in it is screenshot, and page.screencast.start is called exactly once, with on_frame and a size equal to the context's viewport
    And a fourth planted copy that calls page.screenshot in its step helper is reported
    # [Added 2026-10-16 in execute, code review CR-S5-6, the test is 8b7b7d4, test_R41_a_planted_copy_of_a_helper_the_gate_runs_is_reported.]
    # The gate runs functions of tests/browser/support.py, so a guard that read live_e2e.py alone could not see a write there.
    And the guard also reads every function of tests/browser/support.py that the gate calls as support.<name>, and those these call in turn, with the same keyword, attribute and page.evaluate checks as the gate's own code, and the text of every page script on the read-only list (READS_AT_JS and ACTIVE_LABEL_JS among them, named in support.py) holds no write, that is no call that is not a read, no assignment, no ++ and no --
    And two planted copies of support.py checked in a pytest temporary folder are each reported, one with localStorage.clear() in COLD_BOOT_JS and one that calls locator.fill in replace_text (seen failing first on the guard that read live_e2e.py only)
    # Watched failing first. Before A20 changes the script, the rewritten tests run against the live_e2e.py of that moment (the 1.0 flow with A0's --engine) and fail on the missing control path, the seven steps and the one init script. That RED run keeps its own qa/functional/<stamp>-<engine>/ folder (How to run, Controls). The planted copies keep the guard's own RED in every later run.

  # ---------- The name and the logo (v1.1.0, S8, S6) ----------
  @R43 @both
  Scenario: The name in the title and the top bar
    Given a cold boot
    Then document.title is "Danial's Splity Tab"
    And header.top holds div.brand, which holds svg.mark and then h1.word reading "Splity Tab"
    And the body's text holds "Splity Tab" only in h1.word and holds "Danial" nowhere

  @R44 @static
  Scenario: The sprite and the mark are the golden's bytes
    Given the text of index.html and of docs/design/bill-items.html
    Then the text from '<svg class="sprite"' to its closing tag is byte for byte the same in both, and holds the seal-grad gradient and the ten symbols i-x, i-plus, i-copy, i-check, i-caret, i-shuffle, i-warning, i-warning-circle, i-mark and i-seal-check
    And index.html's mark starts '<svg class="mark" viewBox="0 0 28 28" aria-hidden="true" focusable="false">' and holds one path whose fill-rule and d are byte for byte the golden's
    And index.html holds no "xmlns"

  @R44 @both
  Scenario: The sprite comes first and the empty receipt uses the mark
    Given a cold boot
    Then the first element child of body is svg.sprite with aria-hidden "true" and focusable "false", and it takes no space on the page
    And the card's div.r-empty holds an svg.ic whose use has href "#i-mark"
    And svg.mark in div.brand is 28 x 28 px

  @R45 @static
  Scenario: The tab icon file is the golden's icon
    Given src/icon.svg and the icon link of each of the fifteen goldens in docs/design/
    Then each golden has one link with rel "icon" whose href starts with "data:", and the fifteen hrefs are equal
    And the bytes of src/icon.svg equal urllib.parse.unquote of that href after its first comma (470 bytes, SHA-256 "7b5e4176a6182d23f06073ff181f01bbb73e2ac562f78d58a930ffb80fe7fef2" at planning time)
    And it parses as XML whose root is "{http://www.w3.org/2000/svg}svg" with viewBox "0 0 16 16", and it holds the colours "#A3AAFF" and "#1E2140", compared without case, the second inside a prefers-color-scheme light rule
    And no file under src/ has the bytes of docs/brand/favicon.svg, and neither index.html nor src/ names "favicon.svg" or "brand/"

  @R45 @both
  Scenario: The tab icon loads under the live policy
    Given a cold boot
    Then the link with rel "icon" has type "image/svg+xml" and its href property is "<origin>/src/icon.svg"
    When a test-side page.evaluate makes new Image() with src "src/icon.svg" and waits for load or error, at most 5 s
    Then load fired, naturalWidth is above 0, and no CSP violation was recorded

  @R45 @per_engine
  Scenario: The tab icon's colour follows the colour scheme
    # Research B8. The colour is asserted in Chromium. Safari 26 shows one colour in both themes (WebKit bug 309949), accepted by the owner and checked in UAT.
    Given src/icon.svg drawn by a test-side page.evaluate onto a 64 x 64 canvas, once in a context with colour scheme "dark" and once with "light"
    Then In Chromium at least 20 pixels have alpha 255, and every one of them is rgb(163, 170, 255) in the dark context and rgb(30, 33, 64) in the light one
    And In WebKit the colours read (or the error, if the canvas refuses the read) are written to icon-colour.txt in the run's evidence folder as information, and the scenario asserts only that the file holds a line for each context

  # ---------- The save warning (v1.1.0, S4) ----------
  # Statements (a) to (f) and SW4, SW6, SW7 of research save-warning-and-tab-icon.md, section A2. Drivers D-a to D-d, How to run.
  @R46 @both
  Scenario: (a) A cold boot with working storage shows no warning
    Given a fresh context with empty storage
    When I open "/"
    Then #notes holds no div.note

  @R46 @both
  Scenario: (b) The first failed save shows the warning
    Given a cold boot with the storage driver D-a
    Then #notes holds no div.note before any change
    When I replace "Person 1 name" with "A"
    Then #notes holds exactly one div.note.is-warn with role "status", holding an svg.ic whose use has href "#i-warning" and a p reading "This bill is not being saved on this device. It will be lost when you close this tab."
    And it holds no button
    And the bill on screen keeps working (the toggles and the People summary read "A", the card reads "Total Enter the subtotal to see the splits.")

  @R46 @both
  Scenario: (c) The warning stays while saves fail, and a reload starts without it
    Given a cold boot with D-a, and "Person 1 name" replaced with "A" so the warning shows
    When I type "100.00" into Subtotal and click "Add person"
    Then #notes still holds exactly one div.note.is-warn
    When I reload with D-a still failing
    Then no warning shows at boot, because the boot read works (SW5)
    And after the first change the warning shows again

  @R47 @both
  Scenario: (d) The first save that works removes the warning
    Given a cold boot with D-a, and "Person 1 name" replaced with "A" so the warning shows
    When D-a is switched off by window.dispatchEvent(new CustomEvent("test:storage", { detail: false }))
    And I type "B" at the end of "Person 1 name"
    Then #notes holds no div.note.is-warn
    And the draft equals { "version": 2, "bill": <newBill() with people[0].name "AB"> }, the bill on screen (SW4)

  @R46 @both
  Scenario Outline: (e) A failed boot read shows the warning in the first render
    # USER, research CG-1, ledger S4 row 2.
    Given a fresh context with the storage driver <driver>
    When I open "/"
    Then before any gesture #notes holds the div.note.is-warn of scenario (b) and no unreadable note
    And the bill-empty screen shows with People open
    Examples:
      | driver                              |
      | D-b fail-get.js, the getter throws  |
      | D-c fail-getitem.js, getItem throws |

  @R46 @R27 @both
  Scenario: (f) An unreadable draft whose reset save fails shows both notes, the warning first
    # CG-P5 ruled by the owner (USER, 2026-10-13), the warning comes first in #notes.
    Given the B1 seed with the storage driver D-a
    When I open "/"
    Then #notes holds two div.note, first the div.note.is-warn of scenario (b), then the unreadable note with "Dismiss note"
    When I click "Dismiss note"
    Then only the warning remains and #newBill has focus

  @R47 @both
  Scenario: SW6. A storage object that comes back clears the warning without a reload
    Given a fresh context with the storage driver D-b
    When I open "/"
    Then the warning shows at boot
    When D-b is switched off by the test:storage event and I replace "Person 1 name" with "A"
    Then the warning is gone without a reload, and the draft holds people[0].name "A"

  @R47 @both
  Scenario: SW4. Only a save attempt decides, so a change that writes nothing leaves the warning
    # Pick again on PA0 can change nothing (CG-P3, ruled), so it makes no save attempt.
    Given the PA0 seed at 1280 x 800 with D-a, and "Person 1 name" replaced with "A" so the warning shows
    When D-a is switched off and I click #pickAgain on the card
    Then the splits are unchanged (Aisyah RM 0.01, Ben RM 0.01, Chen RM 0.00) and the warning still shows
    When I type "B" at the end of "Person 1 name"
    Then the warning is gone and the draft holds people[0].name "AB"

  @R46 @both
  Scenario: SW7. The warning's live region is not touched on every keystroke
    Given a cold boot with D-a, and "Person 1 name" replaced with "A" so the warning shows
    And a test-side MutationObserver on #notes watching child lists, subtrees, character data and attributes
    When I type "bcde" at the end of "Person 1 name", key by key
    Then the observer recorded no mutation

  @R46 @R47 @both
  Scenario: D-d. A real full storage shows the warning, and room again clears it
    # Once per engine. The engine throws its own error through the app's own setItem.
    Given the K1 seed, loaded, with People opened first
    When a test-side page.evaluate fills localStorage with test.fill keys until one more character is refused
    And I click the end of "Person 3 name" and type " Wei", which grows the stored text
    Then the warning shows and the card's third splits row reads "Chen Wei"
    When a test-side page.evaluate removes every test.fill key and I type "x" at the end of "Person 3 name"
    Then the warning is gone and the draft's people[2].name is "Chen Weix"

  @R47 @static
  Scenario: The app reads no error name and probes nothing
    Given the static scan of src/
    # Changed 2026-10-15 in execute, planner touch before A18 (ledger S4 row 4, Q-A3-1, ruled ORCH). The last banned text read "removeItem(", which also matches split-core's own removeItem(bill, itemId) that the app imports (spec Contracts). The scan bans the storage method, ".removeItem(", as the test has since A3.
    Then it holds none of "QuotaExceededError", "SecurityError", "DOMException", "setTimeout", "setInterval" or ~~"removeItem("~~ ".removeItem("
    And "getItem(" appears exactly once (the boot read in loadDraft) and "setItem(" exactly once (in saveDraft)
    # Added 2026-10-13 after the plan check (F6). The scan has teeth, as R38's and R39's do.
    And a planted copy of src/draft.js with a line that reads e.name === "QuotaExceededError", one with a second getItem( call (a read back) and one with a setTimeout( call, each scanned in a pytest temporary folder, are each reported

  # ---------- Sections, strip, sheet and layout (v1.1.0, S7) ----------
  @R48 @both
  Scenario Outline: Which section is open on load
    Given <setup> at 390 x 844
    Then #peopleBlk has data-open "<people>" and #chargesBlk has data-open "<charges>", and each header row's aria-expanded equals its data-open
    Examples:
      | setup                                                                                  | people | charges |
      | a cold boot                                                                            | true   | false   |
      | the K1 seed                                                                            | false  | false   |
      | the RE seed                                                                            | false  | true    |
      | the B1 seed                                                                            | true   | false   |
      | the K1 seed, then New bill, Start new bill and a reload (an untouched new bill, CG-P4) | true   | false   |
      | a cold boot, then "Person 1 name" replaced with "A" and a reload                       | false  | false   |
      | the K2 seed with "serviceText":"" (a blank rate shows no error at load)                | false  | false   |

  @R48 @both
  Scenario: A header row toggles by click, Enter and Space
    Given the K1 seed
    Then #peopleBtn has aria-controls "peopleBody", aria-labelledby "peopleName" and aria-describedby "peopleSum", and #chargesBtn has "chargesBody", "chargesName" and "chargesSum"
    When I click #peopleBtn
    Then #peopleBlk has data-open "true", #peopleBtn has aria-expanded "true", #peopleBody is displayed, and #peopleSum keeps its box and is not visible, as the golden's #peopleSum in bill-items-open.html (compared by visibility and opacity, plus width)
    When I press Enter on #peopleBtn
    Then People is folded and #peopleBody is not displayed
    When I press Space on #peopleBtn
    Then People is open again
    And at every step aria-expanded equals data-open, and the stored text never changed

  @R48 @both
  Scenario Outline: The People summary fits its row
    Given the <seed> seed at <size>
    Then the visible text of #peopleSum is "<text>"
    Examples:
      | seed | size      | text                                   |
      | K1   | 390 x 844 | Aisyah, Ben, Chen                      |
      | T12  | 390 x 844 | Aisyah, Ben, Chen, Person 4 and 8 more |
      | T12  | 360 x 780 | Aisyah, Ben, Chen and 9 more           |
      | T12W | 360 x 780 | 12 people                              |

  @R48 @both
  Scenario: The People summary refits when its row's width changes
    Given the T12 seed at 390 x 844
    When the viewport becomes 360 x 780
    Then the visible text of #peopleSum is "Aisyah, Ben, Chen and 9 more" without a reload

  @R48 @both
  Scenario Outline: The Charges summary names a rate that blocks
    # RULINGS-v1.1.0, a blank rate shows the marker too and never reads as 0.
    Given the K1 seed and Charges opened first
    When I replace the text of "Service charge" with "<svc>" and of "SST" with "<sst>", and click #chargesBtn to fold Charges
    Then #chargesBtn <bad> class "is-bad", #chargesSum <icon> the warning-circle icon before span.sec-txt, and span.sec-txt reads "<text>"
    Examples:
      | svc     | sst     | bad    | icon     | text                     |
      | 10      | 6       | has no | holds no | Service 10%, SST 6%      |
      | (empty) | 6       | has    | holds    | Check service charge     |
      | 10      | 25      | has    | holds    | Check SST                |
      | 31      | (empty) | has    | holds    | Check both rates         |
      | 12.50   | 6.25    | has no | holds no | Service 12.5%, SST 6.25% |

  @R48 @both
  Scenario: The Charges summary follows each keystroke, not the error timing
    Given the K1 seed and Charges opened first
    When I replace the text of "SST" with "2" and then type "5", with the field still focused
    Then after the "5" key span.sec-txt of #chargesSum reads "Check SST" while p.err#sstErr still carries hidden
    When I press Backspace
    Then it reads "Service 10%, SST 2%"

  @R48 @both
  Scenario: Only the header row and Start new bill open or fold a section
    Given the K1 seed with People opened first and Charges folded
    When I type "abc" into "Nasi lemak ayam price in RM" and leave the field, click "Even" and then "By item", and resize to 1280 x 800 and back to 390 x 844
    Then People is still open and Charges still folded
    When I reload
    Then both sections are folded, because the open state is never saved

  @R48 @both
  Scenario: On the desktop both sections show with their own headings
    Given the K1 seed at 390 x 844 with both sections folded
    When the viewport becomes 1280 x 800
    Then #peopleBody, #chargesBody, h2#peopleH and h2#chargesH are displayed, #peopleBtn and #chargesBtn are not, and both data-open values are still "false"

  @R49 @both
  Scenario Outline: The strip for each result
    Given <setup> at 390 x 844
    Then #strip is displayed and fixed at the bottom of the viewport, it is <height> px tall, and the root's --strip-h reads "<height>px"
    And #stripInfo <content>
    And #stripCopy is displayed and <copy>, and #splitsBtn is enabled with aria-haspopup "dialog", aria-controls "splitsDlg" and aria-expanded "false"
    Examples:
      | setup                                              | height | content                                                                                                              | copy     |
      | the K1 seed                                        | 111    | holds span.s-label "Total" and span.s-fig#stripTotal with span.cur "RM " and "69.26"                                 | enabled  |
      | the K2 seed                                        | 111    | holds "Total" and "116.60"                                                                                           | enabled  |
      | a cold boot                                        | 108    | holds p.s-msg#stripMsg "Enter the subtotal to see the splits." with no svg                                           | disabled |
      | the RE seed                                        | 108    | holds p.s-msg#stripMsg "Check the charges to see the splits."                                                        | disabled |
      | the BU seed                                        | 128    | holds p.s-msg#stripMsg with the warning-circle icon and "1 item still needs a person. Tap who had it to see the splits." | disabled |
      | the K2 seed after a click on #stripCopy            | 111    | holds "Total" and "116.60", and #stripStatus "Summary copied" sits on the same line, right of the Total              | enabled  |
      | the K2 seed with reject.js after a click on #stripCopy | 153 | holds "Total" and "116.60", and #stripStatus.is-fail sits on its own line under them, on two lines                | enabled  |

  @R49 @both
  Scenario: No control the user tabs to is left under the strip
    # Changed 2026-10-15 in execute, planner touch before A18 (ledger H-08, ruled USER 2026-10-15 16:20, option (1), S7 row 27, F-A11-1). The scenario stays @both. In WebKit it fails on today's tree, because WebKit's own focus scroll leaves a control that is already on screen where it is and does not read scroll-padding-bottom (the A16 proof run qa/functional/20261015-163654-webkit/, its one failure). Task A21 builds the focus scroll of spec R49, which makes it pass. In Chromium the browser's own focus scroll already clears the strip, so A21 shows this test's teeth there with a stub that defeats the clearing.
    Given the K1 seed at 390 x 844 with both sections opened first
    When I press Tab through every control from the top of the page up to Splits
    Then each focused control's bottom edge is at most the strip's top edge once the browser has scrolled it into view
    And at the end of the page the last toggle's bottom edge is above the strip's top edge

  @R49 @both
  Scenario: The app scrolls a focused control only below 1024 px and only when the strip covers it
    # Added 2026-10-15 in execute, planner touch before A18 (ledger H-08, ruled USER 2026-10-15 16:20, option (1)). Spec R49, "The focus scroll". The browser's own focus scroll never calls the script method, so the counter sees only the app's calls. It passes before task A21, so A21 gets its RED from three stubs of the handler.
    Given the RND seed at 1280 x 800 and a test-side counter, added with page.evaluate before any gesture, that wraps Element.prototype.scrollIntoView, adds 1 to window.testScrollIntoViewCalls on each call and then calls the original
    When New bill is focused by script and I press Tab through every control up to Subtotal in RM
    Then window.testScrollIntoViewCalls is 0, because nothing happens from 1024 px
    When the viewport becomes 390 x 844, New bill is focused by script and I press Tab once
    Then #peopleBtn has focus, its bottom edge is above the strip's top edge, and window.testScrollIntoViewCalls is still 0, because a control clear of the strip is left alone
    When #splitsBtn and then #stripCopy are focused by script
    Then window.testScrollIntoViewCalls is still 0, because the strip's own controls are part of the strip
    When I click Splits
    Then div.sheet has focus and its bottom edge is below the strip's top edge (otherwise the case fails and names both edges), and window.testScrollIntoViewCalls is still 0, because a dialog sits above the strip

  @R50 @both
  Scenario: The Splits sheet opens with the card's receipt
    Given the K1 seed at 390 x 844
    Then #splitsDlg is closed and has no child element
    When I click Splits
    Then #splitsDlg matches ":modal", is named "Splits", and holds div.glass.dense.sheet with tabindex "-1", which holds div.foil, div.sheet-top (span.grab with aria-hidden "true" and a button.icon-btn named "Close") and div.sheet-scroll#sheetScroll holding div.rbody
    And div.sheet has focus and #splitsBtn has aria-expanded "true"
    And the sheet reads exactly what the card reads
    And the only ids inside #splitsDlg are "sheetScroll" and "sheetSplitsH"

  @R50 @both
  Scenario Outline: Closing the sheet returns focus to Splits
    Given the K1 seed at <size> and the sheet open
    When I <close>
    Then #splitsDlg is closed and has no child element, and #splitsBtn has aria-expanded "false" and focus
    Examples:
      | size      | close                           |
      | 390 x 844 | click "Close"                   |
      | 390 x 844 | press Escape                    |
      | 390 x 844 | click the backdrop at (195, 80) |
      | 360 x 780 | click the backdrop at (180, 80) |
    # Backdrop points from docs/design/LINKS.json. A click above the sheet lands on its ::backdrop, so its target is the dialog element.

  @R50 @both
  Scenario: A press that starts in the sheet and ends on the backdrop does not close it
    Given the K1 seed at 390 x 844 and the sheet open
    When the mouse goes down on the sheet's Total figure and comes up at (195, 80)
    Then the sheet is still open

  @R50 @both
  Scenario Outline: A repeat press on Splits leaves the sheet open and copies nothing
    # PD-21. The sheet rises under the second tap, and its Copy summary is there.
    Given the K1 seed at <size> and a body recorder
    When I <gesture> at the centre of Splits
    Then the sheet is open, window.testClipboardWrites is 0, and only press 1 and click 1 reached the page
    Examples:
      | size                 | gesture                               |
      | 390 x 844, 360 x 780 | touch double tap, mouse double click  |

  @R50 @both
  Scenario Outline: The second press of a double activation that closed the sheet never reaches the page
    # Added 2026-10-15 in execute, planner touch before A18 (ledger S7 row 28, F-A12-1). PD-21, the close half of the guard, which no scenario drove, shaped like the R30 outline of M1. The body recorder proves the cancel, whatever lies under the second press. It passes on today's tree, so A18 shows its teeth with a stub that leaves the guard out of the sheet's click close.
    Given the K1 seed at 390 x 844, the stored text noted, the sheet opened by a click on Splits, and a body recorder
    When I <gesture> at <point>
    Then #splitsDlg is closed and has no child element, #splitsBtn has aria-expanded "false" and focus, and only press 1 and click 1 reached the page
    And window.testClipboardWrites is 0 and the stored text is unchanged
    Examples:
      | point                     | gesture                              |
      | the centre of "Close"     | mouse double click, touch double tap |
      | the backdrop at (195, 80) | mouse double click, touch double tap |
    # The backdrop point is the one of "Closing the sheet returns focus to Splits" (docs/design/LINKS.json).

  @R50 @both
  Scenario: The sheet closes itself when the window reaches 1024 px
    # PD-18, the app moves no focus.
    Given the K1 seed at 390 x 844, the sheet open, and a test-side focusin recorder on the document
    When the viewport becomes 1024 x 768
    Then #splitsDlg is closed and has no child element, and #splitsBtn has aria-expanded "false"
    And no focusin reached any element other than #splitsBtn (the browser's own dialog close step may return focus there), and the element focused afterwards is written to the run's evidence for each engine

  @R50 @both
  Scenario: The sheet follows the bill while it is open
    Given the K2 seed at 390 x 844 and the sheet open
    When I click the sheet's spare chip and choose "One person"
    Then the sheet's splits read RM 38.88, RM 38.86, RM 38.86 while P1 is still open

  @R55 @both
  Scenario: The desktop layout at 1280 and at 1024
    Given the K1 seed at 1280 x 800
    Then header.top is 64 px tall, section.stage#stage named "Bill and splits" and section.work#work named "Edit the bill" are displayed side by side, and #strip is not displayed
    And the card's box is 460 x 642 at (98, 84) and #spareBtn's box is 141 x 44 at (392, 589)
    And #peopleBtn and #chargesBtn are not displayed while #peopleBody, #chargesBody, h2#peopleH and h2#chargesH are
    When the viewport becomes 1024 x 768
    Then the card's right edge is left of the working's left edge and #strip is not displayed

  @R55 @both
  Scenario Outline: The page never scrolls at 1280 x 800
    Given the state of <golden> at 1280 x 800, reached as in the R3 outline
    Then document.documentElement.scrollHeight is at most window.innerHeight
    Examples:
      | golden           |
      | bill-items       |
      | bill-even        |
      | spare-sen        |
      | spare-sen-one    |
      | spare-sen-random |
      | new-bill-dialog  |
      | bill-empty       |
      | rate-error       |
      | bill-unassigned  |
      | bill-unreadable  |
      | bill-twelve      |
      | bill-large       |

  @R56 @both
  Scenario Outline: The item frame marks what lies above and below
    Given the <seed> seed at <size>
    Then #frameWrap <down> data-down and <up> data-up
    Examples:
      | seed | size       | down   | up     |
      | K1   | 1280 x 800 | has    | has no |
      | K1   | 390 x 844  | has no | has no |
      | W1   | 360 x 780  | has    | has no |
      | W1   | 390 x 844  | has no | has no |

  @R56 @both
  Scenario: Scrolling the frame moves the marks
    Given the K1 seed at 1280 x 800
    When I scroll the item list to its end with the mouse wheel over the frame
    Then #frameWrap has data-up and has no data-down
    When I scroll it back to its top
    Then #frameWrap has data-down and has no data-up
    When I remove two items so the rest fits
    Then #frameWrap has neither data-up nor data-down

  # ---------- Spare sen (v1.1.0, S1) ----------
  @R51 @both
  Scenario Outline: The spare sen line and chip
    Given the <seed> seed at 1280 x 800
    Then the card's div.r-spare follows div.r-check and holds p#spareLine "<line>" and div.r-spare-acts
    And div.r-spare-acts holds <pick again>, then #spareBtn with aria-haspopup "dialog" reading "<chip>" followed by the caret icon, named "Spare sen: <chip>. Change"
    Examples:
      | seed | line            | pick again                                                                  | chip            |
      | K2   | 2 sen left over | no #pickAgain                                                               | Top of the list |
      | ONE  | 2 sen left over | no #pickAgain                                                               | One person, Ben |
      | RND  | 2 sen left over | button.chip-btn#pickAgain holding the shuffle icon and then "Pick again"    | At random       |
      | K1   | 1 sen left over | no #pickAgain                                                               | Top of the list |
      | T12  | 8 sen left over | no #pickAgain                                                               | Top of the list |

  @R51 @both
  Scenario: No spare sen, no line
    Given a cold boot
    When I click "Add person", type "30.00" into Subtotal, open Charges first and replace "Service charge" and "SST" with "0"
    Then the splits are RM 10.00 three times, and the card holds no div.r-spare
    When I click Splits
    Then the sheet holds no div.r-spare

  @R52 @both
  Scenario Outline: P1 opens from either chip with focus on the chosen rule
    Given the K1 seed at <size>
    When I click <chip>
    Then dialog.pop#spareDlg matches ":modal", is named "Spare sen" and described by "1 sen left over"
    And it holds div.pop-head (h2#spareTitle and a button.icon-btn named "Close"), p.pop-sub#spareSub and div.choices with three label.choice reading "Top of the list", "One person" and "At random", whose radios have name "spareRule" and values "top", "one" and "random"
    And the "top" radio is checked and has focus
    Examples:
      | size       | chip                                 |
      | 1280 x 800 | #spareBtn on the card                |
      | 390 x 844  | Splits, then the sheet's spare chip  |

  @R52 @both
  Scenario: A choice applies at once and P1 stays open
    Given the K2 seed at 1280 x 800 and P1 open from #spareBtn
    When I click "One person"
    Then P1 is still open, #pickWrap is shown, the card's splits read RM 38.88, RM 38.86, RM 38.86, and #spareBtn reads "One person, Aisyah"
    And the draft's spare is {"rule":"one","personId":"p1"}
    When I click "Top of the list"
    Then #pickWrap is gone and the splits read RM 38.87, RM 38.87, RM 38.86

  @R52 @both
  Scenario: Arrow keys move between the three choices and focus stays on the radio
    # Added 2026-10-13 after the plan check (F5). spare-sen.md, "Arrow keys move between the three choices (native radios)". An arrow key fires change, which applies the rule and renders P1 again, so the render must keep the focused radio.
    Given the K2 seed at 1280 x 800 and P1 open from #spareBtn, with the "top" radio focused
    When I press ArrowDown
    Then the "one" radio is checked and has focus, #pickWrap is shown with the "Aisyah" pill checked, the card's splits read RM 38.88, RM 38.86, RM 38.86, and #spareBtn reads "One person, Aisyah"
    When I press ArrowDown
    Then the "random" radio is checked and has focus, #randWrap is shown and #pickWrap is gone, two of the splits are RM 38.87 and one is RM 38.86, #spareBtn reads "At random", and the card holds #pickAgain
    And the draft's spare is {"rule":"random"} with an order holding p1, p2 and p3 once each
    When I press ArrowUp twice
    Then the "top" radio is checked and has focus, the splits read RM 38.87, RM 38.87, RM 38.86, and #spareBtn reads "Top of the list"

  @R52 @both
  Scenario Outline: P1 sits beside the card on the desktop
    Given the <seed> seed at <size> and P1 open from #spareBtn
    Then <place>
    Examples:
      | seed | size       | place                                                                                      |
      | K1   | 1280 x 800 | #spareDlg is 340 px wide, its left is 574 and its bottom edge is at 632.8, level with #spareBtn's bottom |
      | K2   | 1280 x 800 | its left is 574 and its bottom edge is at 560.8                                            |
      | ONE  | 1280 x 800 | its bottom edge is at 560.8 and it is 310 px tall                                          |
      | K1   | 1024 x 768 | its box lies inside the viewport and its left is the card's right edge plus 16             |

  @R52 @both
  Scenario Outline: On a phone P1 is a bottom sheet over the Splits sheet, and the sheet makes room
    Given the <seed> seed at <size>, Splits open and P1 open from the sheet's chip
    Then #spareDlg sits at the bottom of the viewport and is <height> px tall, and its style holds neither left nor bottom
    And #sheetScroll's style holds padding-bottom "<pad>px"
    When I press Escape
    Then #sheetScroll's style holds no padding-bottom and the sheet is still open
    Examples:
      | seed | size      | height | pad |
      | K1   | 390 x 844 | 255    | 271 |
      | K1   | 360 x 780 | 255    | 271 |
      | ONE  | 390 x 844 | 309    | 325 |
      | RND  | 390 x 844 | 309    | 325 |

  @R52 @both
  Scenario: The sheet scrolls so the splits stay in view above P1
    Given the T12 seed at 390 x 844, Splits open and P1 open from the sheet's chip
    When I choose "One person"
    Then #sheetScroll's scrollTop is above 0
    And either the last splits row's bottom edge is above P1's top edge, or h2#sheetSplitsH sits at the top of #sheetScroll's visible area (it never scrolls further)

  @R52 @both
  Scenario Outline: Closing P1 returns focus to the chip shown at that moment
    Given the K1 seed at <size> and P1 open from <chip>
    When I <close>
    Then #spareDlg is closed and <chip> has focus
    Examples:
      | size       | chip                   | close                           |
      | 1280 x 800 | #spareBtn              | click "Close"                   |
      | 1280 x 800 | #spareBtn              | press Escape                    |
      | 1280 x 800 | #spareBtn              | click the backdrop at (200, 60) |
      | 390 x 844  | the sheet's spare chip | click "Close" at (359, 622)     |
      | 390 x 844  | the sheet's spare chip | click the backdrop at (195, 30) |
      | 360 x 780  | the sheet's spare chip | click "Close" at (329, 558)     |
      | 360 x 780  | the sheet's spare chip | click the backdrop at (180, 30) |
    # Points from docs/design/LINKS.json. Below 1024 px the Splits sheet stays open after P1 closes.

  @R52 @both
  Scenario: A repeat click on the desktop chip leaves P1 open
    # PD-21. P1's light backdrop lies under the second click.
    Given the K1 seed at 1280 x 800 and a body recorder
    When I double click #spareBtn
    Then P1 is open, the "top" radio has focus, and only press 1 and click 1 reached the page

  @R52 @both
  Scenario Outline: The second press of a double activation that closed P1 never reaches the page
    # Added 2026-10-15 in execute, planner touch before A18 (ledger S7 row 29, F-A13-1). PD-21, the close half of the guard on P1, which no scenario drove, shaped like the R30 outline of M1. Points from docs/design/LINKS.json, as in "Closing P1 returns focus to the chip shown at that moment". Below 1024 px the second press would land on the Splits sheet, which stays open. It passes on today's tree, so A18 shows its teeth with a stub that leaves the guard out of P1's click close.
    Given the K1 seed at <size>, the stored text noted, P1 opened by a click on <chip>, and a body recorder
    When I <gesture> at <point>
    Then #spareDlg is closed, <focus> has focus, and only press 1 and click 1 reached the page
    And <after>, window.testClipboardWrites is 0 and the stored text is unchanged
    Examples:
      | size       | chip                                | point                     | focus                  | after                          |
      | 1280 x 800 | #spareBtn                           | the centre of "Close"     | #spareBtn              | nothing else changed           |
      | 1280 x 800 | #spareBtn                           | the backdrop at (200, 60) | #spareBtn              | nothing else changed           |
      | 390 x 844  | Splits, then the sheet's spare chip | "Close" at (359, 622)     | the sheet's spare chip | the Splits sheet is still open |
      | 390 x 844  | Splits, then the sheet's spare chip | the backdrop at (195, 30) | the sheet's spare chip | the Splits sheet is still open |
    # Gestures, a mouse double click and a touch double tap on every row.

  @R52 @both
  Scenario: P1 follows the width when it crosses 1024 px
    # PD-23.
    Given the K1 seed at 390 x 844, Splits open and P1 open from the sheet's chip
    When the viewport becomes 1280 x 800
    Then the Splits sheet has closed itself (R50), and P1 is still open with its left at 574 and its bottom edge at 632.8
    When I press Escape
    Then #spareBtn has focus

  @R52 @both
  Scenario: P1 opened on the desktop and closed below 1024 px
    # CG-P8, ruled by the owner as recommended, "The Splits button (Recommended)" (USER, 2026-10-13, ledger S1 row 3). No spare chip is shown below 1024 px while the Splits sheet is closed.
    # Changed 2026-10-13 after the plan check (B4). This line read "Pending CG-P8, written to its recommended answer".
    Given the K1 seed at 1280 x 800 and P1 open from #spareBtn
    When the viewport becomes 900 x 800
    Then P1 is still open as a bottom sheet and its style holds neither left nor bottom
    When I press Escape
    Then #splitsBtn has focus

  @R53 @both
  Scenario: One person picks the first eligible person at once, and a pill changes it
    Given the K2 seed at 1280 x 800 and P1 open from #spareBtn
    When I click "One person"
    Then fieldset.pick#pickWrap follows the One person label inside div.choices, holding legend.sr "Who pays the spare sen" and div.pick-list#pickList with three label.pill reading "Aisyah", "Ben" and "Chen"
    And each pill holds an input with type "radio", name "spareWho" and value "1", "2" or "3", then span.pill-face holding an svg.ic whose use has href "#i-check" and the name
    And the "Aisyah" pill is checked, the splits read RM 38.88, RM 38.86, RM 38.86 and #spareBtn reads "One person, Aisyah"
    When I click the "Ben" pill
    Then the splits read RM 38.86, RM 38.88, RM 38.86, #spareBtn reads "One person, Ben" and the draft's spare is {"rule":"one","personId":"p2"}
    When I press Escape, click #spareBtn (focus on the checked "One person" radio), press Tab (focus on the checked "Ben" pill) and press ArrowRight
    Then the "Chen" pill is checked and the splits read RM 38.86, RM 38.86, RM 38.88

  @R53 @both
  Scenario: Only people on an item can be chosen in By item
    # CG-P2 ruled by the owner (USER, 2026-10-13).
    Given the I2 seed at 1280 x 800 and P1 open from #spareBtn
    When I click "One person"
    Then #pickList holds two pills, "Ben" with value "2" and "Chen" with value "3", and "Ben" is checked
    And the card's rows still read Aisyah RM 0.00, Ben RM 14.59, Chen RM 2.91
    When I click the "Chen" pill
    Then the card's rows read Aisyah RM 0.00 with "0.00 + 0.00", Ben RM 14.57 with "12.50 + 2.07" and Chen RM 2.93 with "2.51 + 0.42", and the proof reads RM 17.50 with "15.01 + 2.49"

  @R53 @both
  Scenario: A chosen person who has nothing falls back to Top of the list and stays chosen
    # CG-P7, ruled by the owner as recommended, "Line says Top of the list" (USER, 2026-10-13, ledger S1 row 2). The fallback itself is CG-P2, ruled by the owner.
    # Changed 2026-10-13 after the plan check (F1). This line read "Pending CG-P7, written to its recommended answer".
    Given the G4 seed at 1280 x 800
    Then the card's splits read Aisyah RM 44.78, Ben RM 0.00, Chen RM 24.48, and #spareBtn reads "Top of the list", named "Spare sen: Top of the list. Change"
    When I click #spareBtn
    Then the "One person" radio is checked and has focus, and #pickList holds the pills "Aisyah" and "Chen" with none checked
    When I click the "Chen" pill
    Then the splits read Aisyah RM 44.77, Ben RM 0.00, Chen RM 24.49 and #spareBtn reads "One person, Chen"
    And the draft's spare is {"rule":"one","personId":"p3"}

  @R53 @both
  Scenario: Removing the chosen person sets the rule back to Top of the list
    # Core R12, interaction rule 8.
    Given the ONE seed with a fourth person {"id":"p4","name":"Devi"} and "nextId":5, at 1280 x 800
    When I click "Remove Ben"
    Then the draft's spare is {"rule":"top"}, the splits read Aisyah RM 38.87, Chen RM 38.87, Devi RM 38.86, and #spareBtn reads "Top of the list"

  @R54 @both
  Scenario: At random gives the spare sen to different people, and Pick again draws again
    Given the K2 seed at 1280 x 800 and P1 open from #spareBtn
    When I click "At random"
    Then div.pick#randWrap follows the At random label inside div.choices and holds button.btn.btn-ghost#pickAgainSheet with the shuffle icon and "Pick again", and there is no #pickWrap
    And two of the three splits are RM 38.87 and one is RM 38.86, they add up to RM 116.60, and the card holds #pickAgain before #spareBtn, which reads "At random"
    And the draft's spare is {"rule":"random"} with an order holding p1, p2 and p3 once each
    When I press Escape, click #spareBtn (focus on the checked "At random" radio), press Tab to #pickAgainSheet and press Enter
    Then the person on RM 38.86 is a different person, the splits still add up to RM 116.60, the draft's order changed, and #pickAgainSheet still has focus
    When I press Escape and click #pickAgain on the card
    Then the person on RM 38.86 changes again and the splits add up to RM 116.60
    When I reload
    Then the splits are the ones shown before the reload
    When I click #copyBtn
    Then lines 3 to 5 of window.testClipboardText equal the card's splits rows, name and amount, in order

  @R54 @both
  Scenario: Pick again that can change nothing does nothing
    # CG-P3 ruled by the owner (USER, 2026-10-13), at most 64 draws and then no change.
    Given the PA0 seed at 1280 x 800 with the write counter, and the stored text noted
    When I press Tab until #pickAgain has focus and press Enter
    Then the splits still read Aisyah RM 0.01, Ben RM 0.01, Chen RM 0.00, window.testSetItemCalls is 0, the stored text is unchanged, #pickAgain has focus, and no page error or console error was logged

  @R54 @both
  Scenario: Pick again in the Splits sheet draws again
    # Added 2026-10-15 in execute, planner touch before A18 (ledger S7 row 31, F-A15-1). The sheet's Pick again chip comes from the card's renderer (PD-20), and no scenario pressed it, so losing its listener failed no test. A15's probe drove it in both engines (qa/sheet-pick-again-probe/). It passes on today's tree, so A18 shows its teeth with a stub that leaves the sheet's chip without its click handler.
    Given the RND seed at 390 x 844, the sheet opened by a click on Splits, and the person on RM 38.86 in the sheet noted
    When I click the Pick again chip in the sheet's div.r-spare-acts (the button.chip-btn before the spare chip)
    Then the person on RM 38.86 in the sheet is a different person, the sheet's proof still reads RM 116.60, the draft's order changed, and the sheet is still open
    When I press Tab until that chip has focus and press Enter
    Then the person on RM 38.86 changes again, the proof reads RM 116.60, and the chip still has focus

  @R54 @static
  Scenario: Math.random goes only to the two draws
    # PD-19.
    Given the static scan of src/
    Then "Math.random" appears only as an argument of chooseSpareRule and pickAgain calls, and src/ holds no "crypto.getRandomValues"
    # Added 2026-10-13 after the plan check (F6). The scan has teeth, as R38's and R39's do.
    And a planted copy of a src/ file with the line "const r = Math.random();" outside those calls, and one with a "crypto.getRandomValues(" call, each scanned in a pytest temporary folder, are each reported

  # ---------- Large bills at 360 px (v1.1.0, S2) ----------
  @R60 @both
  Scenario Outline: Large bills fit a 360 px phone
    # The card is not displayed below 1024 px. A failure on a MAX bill is a design finding for the owner, because the CSS stays a byte copy (spec R60).
    Given the <seed> seed at 360 x 780
    Then document.documentElement.scrollWidth is at most 360, and #stripTotal's scrollWidth is at most its clientWidth
    When I click Splits
    Then every .r-amount, .amt, .r-lines dd and .wk in the sheet has a scrollWidth at most its clientWidth, and document.documentElement.scrollWidth is still at most 360
    Examples:
      | seed  |
      | W1    |
      | MAX-E |
      | MAX-I |

  @R60 @both
  Scenario: The large price shows whole
    Given the W1 seed at 360 x 780
    Then "Item 5 price in RM" holds "964.50" and its scrollWidth is at most its clientWidth
    And the strip reads "Total RM 1,193.87" on one line (#stripTotal is one line box tall)
    # [Added 2026-10-16 in execute, A18 Findings (K1-56), wording as built.] "One line box tall" is not a fixed height. The 14 px "RM" beside the 24/30 figure makes #stripTotal's line box 33 px, not the 30 px of its line-height. One line means every box of its text shares one band, the highest top of its text boxes above the lowest bottom (STRIP_TOTAL_JS in tests/browser/test_app.py).

  # ---------- Held keys (v1.1.0, S3) ----------
  @R57 @both
  Scenario: A held Enter on the only item's Remove removes that item only
    # The 1.0 SEC-04 repro. A keyboard.down on a key already down sends a keydown with repeat true.
    Given K1 with only its last item ("Satay, 10 sticks") is the stored draft, and its nextId noted
    When I press Tab until "Remove Satay, 10 sticks" has focus, then keyboard.down("Enter"), wait 520 ms, send four more keyboard.down("Enter") and keyboard.up("Enter")
    Then the draft's items are empty, its nextId is the noted one, and #addItem has focus
    And the card and the strip read "Add each item and tap who had it to see the splits."

  @R57 @both
  Scenario: A held Enter on New bill leaves the dialog open on Cancel
    # Changed 2026-10-15 in execute, planner touch before A18 (ledger S5 row 10). The end state alone passed on 1.0 code, where the four repeats close, open, close and open the dialog (A17 measured 2 closes in Chromium, qa/functional/20261014-205544-chromium/), so the scenario also counts the dialog's close events, as the A17 test does.
    Given the K1 seed and the stored text noted
    When I press Tab until #newBill has focus and hold Enter as above
    Then the dialog is open, "Cancel" has focus, and the stored text is unchanged
    And the dialog never closed while the key was held (a listener on #newDlg added before the key went down counted 0 close events)

  @R57 @both
  Scenario: Separate presses still act, and a held letter still types
    Given K1 with only its last item is the stored draft
    When I press Tab until "Remove Satay, 10 sticks" has focus, press Enter (down and up), and press Enter again (down and up) on #addItem, which now has focus
    Then one blank item exists, the one the second press added, and "Item 1 name" has focus
    When I hold "a" in "Item 1 name" (keyboard.down("a"), 520 ms, four more keyboard.down("a"), keyboard.up("a"))
    Then "Item 1 name" holds "aaaaa"

  # ---------- Double taps (v1.1.0, S5, H-04, ~~awaiting the owner's ruling~~ ruled USER 2026-10-14 20:00) ----------
  # Added 2026-10-14 in execute (ledger H-04, S5 rows 4, 5 and 7). Spec R57 (b), written to option 1. ~~If the owner rules another option, the planner rewrites these first.~~
  # [Changed 2026-10-14 in execute. The owner ruled option 1 at 20:00, "Time + place (Recommended)" (USER, ledger H-04). Task A17, built right after A3 (ORCH).]
  # The double tap rows of the R6, R7, R12, R29, R30 and R50 scenarios prove it in both engines through the body recorder (Phrases), and the R34 middle Remove rows through their end state, which fails without the rule. In Chromium a double tap is caught by point 1 (click count 2), as in 1.0.
  # In WebKit only point 2 catches it, since each tap has click count 1. The Node table below fixes the edges of point 2, which a browser gesture cannot hit to the millisecond.
  @R57 @node
  Scenario Outline: The repeat rule reads the click count, the pointer, the time and the place
    # Seen failing first by the stub method of split-core/qa.md (How to run, "RED first for a new or changed case").
    Given the previous pointer click <previous>
    When the press has click count <detail>, is <pointer>, comes <after> ms after that click's timeStamp and lies at (<x>, <y>)
    Then the rule says <repeat>
    Examples:
      | previous                   | detail | pointer | after | x     | y   | repeat                                          |
      | at (100, 100)              | 2      | a mouse | 5000  | 300   | 300 | repeat (point 1)                                |
      | at (100, 100)              | 3      | a tap   | 0     | 100   | 100 | repeat (point 1)                                |
      | at (100, 100)              | 1      | a mouse | 10    | 100   | 100 | not a repeat (a mouse goes by its count only)   |
      | at (100, 100)              | 0      | a tap   | 10    | 100   | 100 | not a repeat (a key press)                      |
      | at (100, 100)              | 1      | a tap   | 0     | 100   | 100 | repeat (point 2)                                |
      | at (100, 100)              | 1      | a tap   | 499.9 | 122   | 78  | repeat (point 2, every edge inside)             |
      | at (100, 100)              | 1      | a tap   | 500   | 100   | 100 | not a repeat (500 ms is not less than 500)      |
      | at (100, 100)              | 1      | a tap   | 10    | 122.5 | 100 | not a repeat (more than 22 px across)           |
      | at (100, 100)              | 1      | a tap   | 10    | 100   | 123 | not a repeat (more than 22 px down)             |
      | none yet (null)            | 1      | a tap   | 10    | 100   | 100 | not a repeat (no previous pointer click)        |

  @R57 @both
  Scenario: A slow second tap, or a quick tap elsewhere, is never held back
    # The other side of point 2, in both engines. The mouse form is the R7 scenario "A press of its own is never held back".
    Given the K2 seed in a has_touch context at 390 x 844, People opened first, and a body recorder
    When I tap the centre of "Add person", wait 600 ms, and tap the same point again
    Then the recorder's two click timeStamps are at least 500 ms apart (otherwise the case fails and names the gap), the body counted two presses and two clicks, the second tap's mousedown and click have defaultPrevented false, and the draft holds five people, the last two blank
    When I tap the centre of "Add person" and at once tap the centre of "Person 1 name", whose centre lies more than 22 px from it on at least one axis (otherwise the case fails and names both points)
    Then the second tap reached the page (counted at the body, its mousedown and click with defaultPrevented false), "Person 1 name" has focus, and the draft holds six people

  # ---------- Two engines (v1.1.0, S5) ----------
  @R58 @static
  Scenario: The engine option and the one launch place
    Given tests/browser/conftest.py, rig.py, live_e2e.py and every Python file under tests/browser/
    Then conftest.py's pytest_addoption adds "--engine" with choices "chromium" and "webkit" and default "chromium", and a session fixture "engine" returns it
    And a browser is launched only in rig.py, by rig.launch(playwright, engine), headless, with its launch arguments kept per engine
    And contexts are made only by rig.new_context, and no Playwright call outside rig.py passes is_mobile or bypass_csp
    # Changed 2026-10-13 after the plan check (N4). It read "no file under tests/ passes is_mobile or bypass_csp", which would match test_R39_a_context_never_gets_a_permission_or_bypasses_the_policy. That negative test hands bypass_csp to rig.new_context to prove the rig refuses it, and stays exempt by name.
    And a marker "chromium_only" with a "reason" argument is registered
    And live_e2e.py takes "--engine" with the same choices and default, and tests/browser/fidelity/run.py has no engine option

  @R58 @gate
  Scenario: A Chromium-only test is a counted skip in WebKit
    # Checked on the evidence of each engine's run.
    Given the evidence folder of a WebKit run and of a Chromium run of the suite at the same commit
    Then the WebKit folder's name ends in "-webkit", and its skips.txt lists every skipped test with its reason and a count equal to junit.xml's skipped count
    And the R33 IME test is listed there with a reason that starts "Needs a CDP session"
    And no skipped test is counted as passed, and the Chromium folder's name ends in "-chromium" and shows the chromium_only tests run

  @R58 @static
  # [Added 2026-10-16 in execute, code review CR-S5-14, the test is 6ffecf7, test_R58_a_run_never_writes_into_an_evidence_folder_it_did_not_make.]
  # Constitution, Gates and evidence, each run writes its own capture. Seen failing first on mkdir with exist_ok=True.
  Scenario: A suite run never writes into an evidence folder it did not make
    Given conftest.evidence_dir with its clock frozen at one second and its evidence root in a pytest temporary folder
    When a first run makes its folder <stamp>-<engine> and a second run of the same engine asks for its folder in the same second
    Then the first folder exists under that root, and the second run does not get it (evidence_dir stops with FileExistsError, as the live gate's folder does)

  @R58 @R41 @gate
  Scenario: The live gate records its engine
    When live_e2e.py runs with --engine webkit
    Then its evidence folder is docs/modules/split-app/qa/live-e2e/<stamp>-webkit/ and its summary.json records "engine" "webkit" and the browser's version (under the key "browser_version", QA-S5-3, noted 2026-10-16 in execute)
    And run with no option it uses Chromium and its folder ends in "-chromium"

  @R59 @per_engine
  Scenario Outline: Focus after a mouse click is the engine's own
    # WebKit's isMouseFocusable for form controls, research webkit-testing.md section 2.
    Given <setup>
    When I click <control> with the mouse
    Then In Chromium <focused> has focus
    And In WebKit document.activeElement is body
    Examples:
      | setup       | control                | focused   |
      | a cold boot | the "By item" label    | #modeItem |
      | the K2 seed | #stripCopy             | #stripCopy |

  @R59 @gate
  Scenario: The A0 baseline record is complete
    # Changed 2026-10-13 after the plan check (B1, B3, F9). The record names the Chromium count with the 1.0 golden fixtures, both live gate baselines, and the probe script with its launch rule, and the probe list gains the label, the radio and the .svg type.
    Given the A0 evidence folder docs/modules/split-app/qa/webkit-baseline/<stamp>/
    # [Changed 2026-10-14 in execute, ORCH, Q-A0-2 (ledger S5 row 4). The line read "Then it holds pytest.txt, junit.xml and skips.txt of the WebKit run of the suite as it stood before A1". The record names the WebKit run's own folder, and no copy is made.]
    Then it names the WebKit run's own folder, which holds them (pytest.txt, junit.xml and skips.txt of the WebKit run of the suite as it stood before A1)
    And it names the docs/modules/split-app/qa/functional/<stamp>-chromium/ folder of the Chromium run at the same commit, whose junit.xml shows the 427 sealed 1.0 tests passing, with A0's new tests counted apart
    And it names the folders of a live_e2e.py --engine chromium run and a live_e2e.py --engine webkit run of the 1.0 gate, the baseline of the A20 gate
    And probes.json was written by python tests/browser/probe_webkit.py --engine webkit, which launched through rig.launch, made every context with rig.new_context and recorded that the clipboard stand-in was in place before its first gesture
    And probes.json records, measured in WebKit on this machine, the click count (detail) of a quick touch double tap, the order of a tap's pointer and mouse events, isSecureContext and typeof Clipboard on http://127.0.0.1, whether an init script can redefine window.localStorage, and the console text of a CSP violation and of a denied localStorage
    And it records document.activeElement after a mouse click on a label of a radio and after a mouse click on a visible radio, on a page the probe writes with page.set_content so the app's styling does not decide it
    And it records the Content-Type header the test server sends for an .svg file already in the project (for example docs/brand/mark.svg), read by the probe's own GET
    And sorting.md lists every failed test of that run's junit.xml exactly once, each with one of (a) app defect, fixed in the app, (b) engine difference, with its measurement, or (c) Chromium-only tool, with its reason, and the commit or scenario change that follows

  # ---------- The accessible description of the amount fields (v1.1.0, S7, CG-P6) ----------
  @R9 @R11 @chromium_only
  # reason. Needs a CDP session (Accessibility.getPartialAXTree) to read the computed description, which Playwright gives in Chromium only.
  Scenario: The accessible description of the amount fields is measured and reported
    # CG-P6 ruled by the owner (USER, 2026-10-13). Build to the golden, measure the description in the build, report it.
    Given the K1 seed in one page and the K2 seed in another
    When the computed accessible description of "Char kuey teow price in RM" and of Subtotal is read through CDP with the error hidden, and again after "13.505" and "0" are typed and the field is left
    Then accessible-description.txt in the run's evidence folder holds the four descriptions, one line each, naming the field and the error state
    And the scenario asserts only that the four lines exist, and the orchestrator reports them to the owner

  # ---------- Draft version 2 (v1.1.0, S1) ----------
  @R61 @node
  Scenario Outline: The decoder accepts versions 1 and 2 and checks the spare choice
    Given the stored text <draft> from the seed tables above
    When decodeDraft is called in tests/draft.test.js
    Then the result is <result>
    Examples:
      | draft                 | result                                                                      |
      | K1, K2, ONE, RND, PA0 | ok, and the bill deep-equals the seed's bill                                |
      | S1_V1, S2_V1          | ok, and the bill is the 1.0 bill with spare {"rule":"top"} (D14)            |
      | G4                    | ok, with spare {"rule":"one","personId":"p2"} kept                          |
      | G5                    | ok, with spare {"rule":"top"}, because D14 ignores the spare key of a version 1 draft |
      | G6                    | ok, with spare exactly {"rule":"top"}                                       |
      | B4, B5, B25 to B32    | { ok: false }                                                               |

  @R61 @node
  Scenario: Saving writes version 2, and load and save report failures
    Given src/draft.js under node --test
    Then encodeDraft(bill) parses to { "version": 2, "bill": bill } for K1's bill
    And loadDraft(null) is { state: "failed" }, and loadDraft of a storage whose getItem throws is { state: "failed" }
    And loadDraft of a storage whose getItem returns null is { state: "none" }, of B1 is { state: "unreadable" }, and of K2 is { state: "ok", bill }
    And saveDraft(null, bill) is false, saveDraft of a storage whose setItem throws is false, and saveDraft of a working storage is true
    And neither function throws for any of these

  # ---------- Plain names (v1.1.0, H-10, added 2026-10-16 in execute) ----------
  # Ruled USER 2026-10-16 00:07, option (1) (ledger H-10, security SEC-S5-1 LOW and SEC-S5-3 INFO). Spec R62, D8, task A22.
  # "The class" is [\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}], the 79 code points of core R35. A character is written here
  # as U+XXXX and given to the page as that one character. "Insert T" means page.keyboard.insert_text(T) on the focused
  # field, one input event with the text, which is how a paste or a drop arrives. A real paste would need the system
  # clipboard, which no test touches (How to run, Clipboard). "Holds no character of the class" is checked with
  # /[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]/u in the page or in Python's equivalent list of the 79 code points.
  @R62 @R5 @both
  Scenario Outline: A control or bidi character put into a person's name is removed at once
    Given the K2 seed
    When I click "Person 2 name", press End and insert <text>
    Then "Person 2 name" is the same element and has focus, its value is "<value>" and its selection is collapsed at <caret>
    And the draft's p2 name is "<value>", and no name in the draft holds a character of the class
    And Ben's splits row on the card reads "<value>", "Remove <value>" is the second Remove's name, and the People summary text holds "<value>" and no character of the class
    And Copy summary on the card gives a text whose line 4 is "<value> RM 38.87"
    Examples:
      | text                     | value  | caret |
      | U+202E                   | Ben    | 3     |
      | U+202E "x"               | Benx   | 4     |
      | "a" U+2028 "b"           | Benab  | 5     |
      | U+0000                   | Ben    | 3     |
      | U+0009 "Lee"             | BenLee | 6     |

  @R62 @R33 @both
  Scenario: A removal in the middle of a name keeps the caret where the text went in
    Given the K2 seed
    When I click "Person 2 name", press End, press ArrowLeft once (the caret after "Be") and insert U+202E "x" U+2067
    Then "Person 2 name" is the same element and has focus, its value is "Bexn" and its selection is collapsed at 3
    When I type "y"
    Then its value is "Bexyn" and the draft's p2 name is "Bexyn"

  @R62 @both
  Scenario: Each kind of character in the class is removed from a name field
    # The full class is proved once in Node (split-core qa, "plainName and summaryText read one class"). This walks the
    # ends of each range through the real field in both engines.
    Given the K2 seed
    When, for each character c of U+0001, U+0009, U+001B, U+001F, U+007F, U+0080, U+0085, U+009F, U+2028, U+2029, U+061C, U+200E, U+200F, U+202A, U+202B, U+202C, U+202D, U+202E, U+2066, U+2067, U+2068 and U+2069 in turn, I click "Person 1 name", press Control+A, type "A" and insert "B" c "C"
    Then after each insert the value of "Person 1 name" is "ABC", its selection is collapsed at 3 and the draft's p1 name is "ABC"
    # U+0000 is in the outline above. A character the tool cannot insert fails the case with its code point, never a skip.

  @R62 @both
  Scenario: Characters outside the class stay in a name
    Given the K2 seed
    When I click "Person 2 name", press End and insert "A" U+200B "B" U+00A0 "C" U+FEFF
    And I click "Person 3 name", press End and insert U+1F468 U+200D U+1F469 U+200D U+1F467
    Then the values are "Ben" followed by exactly what was inserted, and "Chen" followed by the one emoji, and the draft holds the same two names
    # Passes before task A22. Its RED is a stub helper that also deletes \p{Cf} (spec task A22).

  @R62 @R33 @both
  Scenario: Typing that brings no character of the class writes nothing into the field
    Given the K2 seed and, added by page.evaluate before the gestures, a test-side spy that counts calls of the value setter of HTMLInputElement.prototype and of setSelectionRange on "Person 2 name"
    When I click "Person 2 name", press End, type "abc", press Home, type "X" and press Backspace
    Then the spy counted 0 calls, the value is "Benabc", and the selection is collapsed at 0
    # Passes before task A22. Its RED is a stub helper that writes the value and the caret on every input event (spec task A22).

  @R62 @R11 @both
  Scenario: An item name loses the class too
    Given the K1 seed
    When I click "Item 2 name", press End and insert U+202E "x"
    Then "Item 2 name" has focus, its value is "Char kuey teowx" and its selection is collapsed at 15
    And the draft's i5 name is "Char kuey teowx", the price field is named "Char kuey teowx price in RM", its Remove is "Remove Char kuey teowx" and its toggle group is "Who had Char kuey teowx"

  @R62 @R4 @both
  Scenario: A name made only of removed characters falls back to its position
    Given the K2 seed
    When I click "Person 2 name", press Control+A and insert U+202E
    Then "Person 2 name" is empty and shows its placeholder "Person 2", and the draft's p2 name is ""
    And the second splits row reads "Person 2", the second Remove is named "Remove Person 2", and the People summary text holds "Person 2"

  @R62 @R26 @R48 @both
  Scenario: A saved name with bidi controls loads plain and the People line reads left to right
    # SEC-S5-1 and SEC-S5-3, measured by the security finder on 2026-10-15 (qa/security/20261015-222146/, b2_injection-<engine>.json).
    Given the G8 seed at 390 x 844 with the write counter
    Then no note shows, People is folded, and the five name fields hold "Aisyah", "Ben", "Chen", "AB" and "" (placeholder "Person 5")
    And the text of #peopleSum .sec-txt holds no character of the class and is one of the R48 summaries of the labels Aisyah, Ben, Chen, AB, Person 5
    And every character box of that text (one Range rect per character, the zero-width ones left out) has a left edge greater than the one before it, and all of them share one band (the highest top above the lowest bottom), so the line runs left to right on one line
    And the stored text is still the G8 text, and window.testSetItemCalls is 0 (nothing is written at boot)
    When I open People first and type "x" at the end of "Person 1 name"
    Then the draft's names are "Aisyahx", "Ben", "Chen", "AB" and ""
    And Copy summary on the card gives one row per splits row, and the name in each row is exactly the span.nm text of that splits row on the card

  @R62 @R61 @node
  Scenario Outline: The decoder rebuilds names without the class
    Given the stored text <draft> from the seed tables above
    When decodeDraft is called in tests/draft.test.js
    Then the result is <result>
    And for every ok result, no name in the bill holds a character of the class, and encodeDraft of that bill decodes to the same bill
    Examples:
      | draft                                         | result                                                                    |
      | G8                                            | ok, names "Aisyah", "Ben", "Chen", "AB" and "", everything else as stored  |
      | G9                                            | ok, Aisyah's name is "ABCDEFGHIJKLMNOPQRST"                                |
      | G10, the K1 draft                             | ok, i5's name is "Char kuey teow"                                         |
      | G10, the S1_V1 draft                          | ok, version 1 read with spare {"rule":"top"}, Ben's name is "Ben"         |
      | K1 with i4 renamed 40 letters + U+202E        | ok, i4's name is the 40 letters                                           |
      | B19, and K2 with Aisyah renamed "Ai" U+202E U+000D "syah" | { ok: false }, LF and CR are still rejected (D8 (a))          |
      | B18, B20                                      | { ok: false }, still too long after the rebuild                           |

  @R62 @R33 @node
  Scenario Outline: plainNameField puts the caret where the text went in
    # Added 2026-10-16 in execute, code review CR-R6 (ledger S7 row 46, ORCH). The helper of spec R62 (1) in src/ui/dom.js, the one both name fields call.
    # The browser scenarios above cannot put a removed character after the caret, because a key or insert_text puts the new text before the caret and the old text is plain. A drop that selects the dropped text can. Code review CR-R6 measured mutant UC2 (the caret is selectionStart less every removed unit) passing all 12 R62 browser ids in Chromium (qa/code-review/20261016-020001/pytest-UC2-chromium.txt).
    # The test lives under tests/ (the file name is the builder's choice, in a file of its own or beside the other Node cases) and runs under node --test with the rest, no browser. Importing src/ui/dom.js touches no DOM at load.
    Given a stand-in input object { value, selectionStart, setSelectionRange } with the value <value> and the selectionStart <p>, whose setSelectionRange records its arguments
    When plainNameField is called with it
    Then it returns "<plain>", the object's value is "<plain>", and setSelectionRange was called once with (<caret>, <caret>)
    Examples:
      | value                                | p | plain   | caret | case                                                                       |
      | "Be" U+202E "n"                      | 2 | Ben     | 2     | a removed character after the caret only, none before it                   |
      | "Ben" U+202E                         | 3 | Ben     | 3     | the same at the end of the text                                            |
      | U+202E "Be" U+202E "n"               | 3 | Ben     | 2     | one removed character before the caret and one after it                    |
      | U+2028 U+2029 "Be" U+0000 "n" U+200E | 4 | Ben     | 2     | two removed characters before the caret and two after it                   |
      | "Be" U+202E "x" U+2067 "n"           | 5 | Bexn    | 3     | what an insert at the caret leaves, the caret after the "x"                |
      | U+202E U+2067                        | 1 | (empty) | 0     | a name made only of removed characters, the plain text is the empty string |
    # Passes before any change, since the shipped line is the spec's formula. Its RED is three stubs of plainNameField put in and taken out with the Edit tool, each seen failing on its asserted property. The caret of selectionStart less every removed unit (UC2, fails the first, second, third, fourth and sixth rows), the caret at the end of the plain text (UC1, fails the first, third, fourth and fifth rows) and no setSelectionRange call (UC3, fails every row). `git diff --quiet src/` after each, `grep -rn STUB src/` empty before the commit.

  # ---------- Dismiss note arms the repeat guard (v1.1.0, code review CR-R1, added 2026-10-16 in execute) ----------
  # Ruled ORCH 2026-10-16 under the owner's word on minor calls (ledger S7 row 46). Spec R27, R7 and task A23.
  # Once the note is gone, the People header row (#peopleBtn, task A4) lies under the pointer below 1024 px, so before A23 the repeat press of a double click on Dismiss note folded People. From 1024 px a header lies there and the repeat press moved focus to the page.
  # Measured on 6cddc66 by code review CR-R1 (qa/code-review/20261016-020001/, pytest-PROBE-chromium.txt and pytest-PROBE-webkit.txt, page.mouse.click and page.mouse.dblclick at the centre of #dismissNote on the B1 seed). A click left People open and focus on #newBill. A double click at 390 x 844 and 360 x 780 left People folded, the second press under #peopleBtn, and focus on #peopleBtn in Chromium and on body in WebKit. A double click at 1280 x 800 left focus on body in both engines, the second press under header.top. The stored text was unchanged in every case. The triple click and the touch double tap were not probed.
  @R27 @R7 @both
  Scenario Outline: A repeat press on Dismiss note acts as one press at every width
    Given the B1 seed at <size>, the stored text noted, and a body recorder (a has_touch context for the tap row)
    When I <gesture> at the centre of "Dismiss note"
    Then the note is no longer in the DOM and #newBill has focus
    And below 1024 px #peopleBtn has aria-expanded "true", #peopleBlk has data-open "true" and #chargesBtn has aria-expanded "false", as after one click
    And the stored text is the one noted
    And only press 1 and click 1 reached the page
    Examples:
      | size       | gesture                    |
      | 390 x 844  | single click (the control) |
      | 390 x 844  | mouse double click         |
      | 390 x 844  | mouse triple click         |
      | 390 x 844  | touch double tap           |
      | 360 x 780  | single click (the control) |
      | 360 x 780  | mouse double click         |
      | 360 x 780  | mouse triple click         |
      | 360 x 780  | touch double tap           |
      | 1280 x 800 | single click (the control) |
      | 1280 x 800 | mouse double click         |
      | 1280 x 800 | mouse triple click         |
      | 1280 x 800 | touch double tap           |
    # The single click rows pass on today's tree by design. They are the control that fixes the end state the other rows must equal. The double click rows fail on today's tree on the asserted property, People folded below 1024 px, focus not on #newBill, and a second press and click that reached the page. The triple click and touch rows are measured by the RED run of task A23, and one that passes on today's tree is reported to the orchestrator.
    # The touch double tap is proven by the recorder as "A body recorder" says (Phrases), so a second tap more than 500 ms after the first or more than 22 px from it fails the case and names the gap. A tap less than 500 ms after the Dismiss tap and within 22 px of it is its repeat by spec R57 (b), the accepted residual, so no row taps People straight after.

  @R27 @R57 @both
  Scenario Outline: A held Enter on Dismiss note reaches nothing
    # Added 2026-10-16 in execute, follow-up to code review CR-R1 (ORCH, ledger S7 row 46), task A23. The armed guard also cancels a held key's repeats (spec R57 (a)), so the repeats of Enter cannot press the control that the click moved focus to.
    # Today's code is unmeasured for this scenario, since the review probed no key. The RED run of task A23 measures it, and a row that passes on today's tree is reported to the orchestrator.
    Given the B1 seed at <size>, the stored text noted, and a click recorder on window in the capture phase (the window half of "A body recorder", Phrases, which sees every click before the guard can cancel it, the clicks that Enter makes included)
    When I press Tab until "Dismiss note" has focus, then keyboard.down("Enter"), wait 520 ms, send four more keyboard.down("Enter") and keyboard.up("Enter")
    Then the note is no longer in the DOM and #newBill has focus
    And the recorder counted one click, on #dismissNote, and none on #newBill, and dialog#newDlg does not have the open attribute
    And below 1024 px #peopleBtn has aria-expanded "true" and #chargesBtn has aria-expanded "false"
    And the stored text is the one noted
    Examples:
      | size       |
      | 390 x 844  |
      | 1280 x 800 |
    # The click count is the proof and the end state alone is not. If the four repeats reached New bill they would open, close, open and close the dialog, which leaves it closed with focus back on New bill, as the R57 scenario "A held Enter on New bill leaves the dialog open on Cancel" notes for its own count.
```

## FE element checklist
Each row passes or fails on its own. A row is checked on the app in the state the fidelity table reaches, at every width its section names unless the row names one, in Chromium. "Matches" means the same tag, classes, text and ARIA as the golden's element, and computed styles equal to the golden's by the property list of "Equal to the golden" (Phrases). A row that gives a number also asserts that number, within 0.5 px. "As K1-nn" repeats that row's check on this golden's render. A row marked "not drawn" checks a rule the goldens state but do not draw, on the app, against the piece it names. Ids are one prefix per golden. The inventory id of each golden is in its heading, because 1.0 used some of the same letters for other screens.

### K1 `docs/design/bill-items.html` (inventory K1) at 390 x 844, 360 x 780 and 1280 x 800
| Id | Element | Expected |
|---|---|---|
| K1-01 | Top bar `header.top` | 60 px tall at 390 and 360, 64 px at 1280. `--l1` fill and a hairline under it. 16 px sides on a phone, 48 px at 1280. [Added 2026-10-16 in execute, fidelity O-4, the golden is the truth.] On a phone 60 px is the bar less its 1 px hairline (border box 61), at 1280 64 px is the border box (63 and the 1 px hairline), in the golden and the app |
| K1-02 | Mark `svg.mark` in `div.brand` | 28 x 28, the colour of `--accent-ink` (computed `color` and `fill` equal), the path of R44, 10 px left of the wordmark. [Added 2026-10-16 in execute, fidelity O-4.] "Equal" means equal to the golden's, not to each other. The computed `fill` is `--accent-ink` and the computed `color` is `--text`, on both sides |
| K1-03 | Wordmark `h1.word` | "Splity Tab", 19/24 700, letter-spacing equal |
| K1-04 | Notes `div.notes#notes` | present, empty, takes no space |
| K1-05 | New bill `#newBill` | `button.btn.btn-ghost`, an 18 px plus icon then "New bill", 15/20 600, clear fill, `--line-strong` border, 10 px radius, at the right end of the top bar, `aria-haspopup` "dialog" |
| K1-06 | Stage `section.stage#stage` | named "Bill and splits". Not displayed at 390 and 360, displayed at 1280 |
| K1-07 | Card `article.glass.card#card` (1280) | 460 x 642 at (98, 84), 24 px padding, 22 px radius, the glass background, edge and `--shadow-card` (plus `background-image` and `backdrop-filter`) |
| K1-08 | Card foil `div.foil` (1280) | a 3 px indigo sheen along the card's top edge, `aria-hidden` "true" (plus `background-image`) |
| K1-09 | Total label `span.r-label` | "Total", 14/20 600 |
| K1-10 | Total figure `p.r-amount#rTotal` | `span.cur` "RM " then "69.26", 48 px at 1280, monospace, tracking -0.03em, "RM" in body text at 0.42 of the figure (plus `letter-spacing` and `font-family`). [Added 2026-10-16 in execute, fidelity O-4.] "In body text" is the colour, `--text`, where the figure is `--total-ink`. The family of "RM" is monospace on both sides |
| K1-11 | Bill lines `dl.r-lines` | three rows, "Subtotal" RM 59.40, "Service 10%" RM 5.94, "SST 6%" RM 3.92, 15/22, muted labels, monospace figures right aligned, 6 px apart |
| K1-12 | Dashed rule `div.r-rule` | dashed indigo, 20 px under the lines and 16 px above Splits, `aria-hidden` "true" |
| K1-13 | Splits heading `div.r-head` | `h2#splitsH` "Splits" 14/20 600 muted, and "items + charges" 13/18 at the right with `aria-hidden` "true" |
| K1-14 | Split row Aisyah | `span.nm` "Aisyah" 600, `span.amt` "RM 29.04" 18/24 monospace 600, `span.wk` "24.90 + 4.14" 13/18 with the hidden "Items " and "charges " |
| K1-15 | Split row Ben | as K1-14, "RM 15.74", "13.50 + 2.24" |
| K1-16 | Split row Chen | as K1-14, "RM 24.48", "21.00 + 3.48" |
| K1-17 | Splits list `ul.r-splits#splits` | rows 12 px apart, `aria-labelledby` "splitsH", no class "many" |
| K1-18 | Proof row `div.r-check` | a solid indigo hairline above it and 16 px under that, `svg.seal` 24 px filled by `url(#seal-grad)`, "Adds up to" (`span.lbl-proof`), `#addsUp` "RM 69.26" in indigo 18/24, `span.wk` "59.40 + 9.86" |
| K1-19 | Spare line `div.r-spare` | 16 px under the proof, `p#spareLine` "1 sen left over" |
| K1-20 | Spare chip `#spareBtn` | `button.chip-btn`, "Top of the list" then a 16 px muted caret, 44 px tall, full pill, 14 px sides, `--line-glass` border, dark fill at 45%, 14/20 600, named "Spare sen: Top of the list. Change". 141 x 44 at (392, 589) at 1280 |
| K1-21 | Copy summary `#copyBtn` | `button.btn.btn-primary.btn-block.r-copy`, an 18 px copy icon then "Copy summary" at 16 px, indigo fill, `--on-accent` label, full width, 48 px, 20 px under the spare line |
| K1-22 | Card status `p.status#cardStatus` | `role` "status", present, empty, not displayed |
| K1-23 | Work `section.work#work` | named "Edit the bill". From x 672 with 20 px top padding at 1280. 4 px under the top bar on a phone |
| K1-24 | People row `#peopleBtn` (390, 360) | inside `h2.sec-h`, 52 px, "People" 15/20 600 at the left, the summary "Aisyah, Ben, Chen" 14/20 400 muted right aligned, an 18 px caret, folded (`aria-expanded` "false"), a hairline under the row. Not displayed at 1280 |
| K1-25 | People body (390, 360) | `div.sec-body#peopleBody` not displayed |
| K1-26 | People heading row (1280) | `div.blk-head` 44 px with `h2.blk-h#peopleH` "People" and `#addPerson` (ghost, plus icon, "Add person") at the right |
| K1-27 | People grid (1280) | `ul.people#peopleList`, 3 columns, 148 px minimum, 8 px gaps |
| K1-28 | Person 1 field | `li.field.person`, value "Aisyah", 46 px tall, `--field` fill, `--line-strong` border, 10 px radius, 16/24 text, 12 px side padding |
| K1-29 | Person 1 Remove | `button.icon-btn` "Remove Aisyah", 44 x 44, a muted 18 px X, the right corners rounded, enabled |
| K1-30 | Person 2 field and Remove | as K1-28 and K1-29, "Ben", "Remove Ben" |
| K1-31 | Person 3 field and Remove | as K1-28 and K1-29, "Chen", "Remove Chen" |
| K1-32 | Charges row `#chargesBtn` (390, 360) | 52 px, "Charges" with "Service 10%, SST 6%" and the caret, folded, no class "is-bad". Not displayed at 1280 |
| K1-33 | Charges heading (1280) | `h2.blk-h.solo#chargesH` "Charges" |
| K1-34 | Service label | `label.lbl` for "svc", "Service charge", 14/20 600 muted, 8 px above its field |
| K1-35 | Service field | `div.field.pct` with `#svc` "10" right aligned and "%" 2 px after it and 12 px from the right edge, 150 px wide at 1280 |
| K1-36 | Service error | `p.err#svcErr` present with `hidden`, not displayed |
| K1-37 | SST label and field | as K1-34 and K1-35, "SST", `#sst` "6" |
| K1-38 | SST error | `p.err#sstErr` present with `hidden`, not displayed |
| K1-39 | Hint `p.hint#chargeHint` | "Set a charge to 0 if your bill already includes it.", 14/20 400 muted. At 1280 in a third cell 28 px down, so it lines up with the fields |
| K1-40 | Split block | `div.blk.split#splitBlk` with `role` "group" and `h2.blk-h#splitH` "Split" 15/20 600. On a phone 12 px under the Charges hairline, and ~~Split starts at 229 at 390~~ the Split block ends at 229 at 390 (it starts at 170), as BE-14 and KO-07 use "ends" [changed 2026-10-16 in execute, fidelity O-4, the golden is the truth] |
| K1-41 | Split switch `div.mode-sw` | two equal 44 px halves, `--field` track, `--line-strong` frame and divider, 10 px radius, at most 280 px wide, right of the heading |
| K1-42 | Even half | the label for "modeEven", unchecked, muted text |
| K1-43 | By item half | the label for "modeItem", checked, indigo tint with an inset indigo edge, text colour |
| K1-44 | Items heading row | `div.blk-head` 44 px with `h2.blk-h#itemsH` "Items" and `#addItem` (ghost, plus icon, "Add item") at the right, ~~20 px under a hairline~~ 20 px under a hairline at 390 and 360 and 16 px at 1280, 8 px above the frame. [Changed 2026-10-16 in execute, fidelity O-1, the golden is the truth. At 1280 the golden has 16 px (margin 16, border 1, padding 16), and the app the same.] |
| K1-45 | Item frame `div.frame-wrap#frameWrap` | `--l1` fill, 16 px radius, `--line-frame` edge, 10 px left and 8 px right padding on a phone. At 390 and 360 the four items fit with neither `data-up` nor `data-down`. At 1280 it is 291 px tall with the bottom fade and `data-down` |
| K1-46 | Item 1 name | value "Nasi lemak ayam", named "Item 1 name", maxlength 40, styled as K1-28 |
| K1-47 | Item 1 price | `div.field.money`, `span.unit` "RM" 14 px monospace muted 10 px from the left, value "15.90" monospace right aligned with 6 px left and 10 px right padding, named "Nasi lemak ayam price in RM", 104 px wide at 390 and 360, 128 px at 1280 |
| K1-48 | Item 1 Remove | `button.icon-btn` "Remove Nasi lemak ayam", 44 x 44, an 18 px X |
| K1-49 | Item 1 error | `p.err#ie1` present with `hidden` |
| K1-50 | Item 1 toggles | `div.taps` named "Who had Nasi lemak ayam", 8 px under the row, 8 px apart. Aisyah on (indigo tint, indigo edge, 14 px indigo check, 12 px left padding, text colour). Ben and Chen off (clear, `--line-strong` border, muted name). Each 44 px, full pill, 16 px sides, 14/20 600 |
| K1-51 | Item 2 | as K1-46 to K1-50, "Char kuey teow", "13.50", "Remove Char kuey teow", `#ie2` hidden, Ben on only |
| K1-52 | Item 3 | as K1-46 to K1-50, "Mee goreng mamak", "12.00", Chen on only, no class "needs" |
| K1-53 | Item 4 | as K1-46 to K1-50, "Satay, 10 sticks", "18.00", Aisyah and Chen on, Ben off |
| K1-54 | Item rows | 12 px top and bottom padding, the row `minmax(0, 1fr) 104px 44px` with 6 px gaps on a phone and 8 px at 1280, a hairline above items 2 to 4 only. [Added 2026-10-16 in execute, fidelity O-4.] The price column is 104 px on a phone and 128 px at 1280, in the golden and the app, as K1-47 says |
| K1-55 | Strip `div.strip.glass.dense#strip` (390, 360) | fixed at the bottom, 111 px, dense glass, the foil, 22 px top corners, `--shadow-up`, its top at 733 at 390 and 669 at 360. Not displayed at 1280 |
| K1-56 | Strip Total | `span.s-label` "Total" 14/20 600, `span.s-fig#stripTotal` "RM 69.26" 24/30 600 with "RM" at 14 px. [Added 2026-10-16 in execute, A18 Findings.] Its line box is 33 px tall with the 14 px "RM" on the figure's line, in the golden and the app, not the 30 px of the line-height |
| K1-57 | Strip status `#stripStatus` | `role` "status", present, empty, not displayed |
| K1-58 | Splits `#splitsBtn` | ghost on the strip (dark fill at 50%, the glass border, 12 px sides), "Splits" then the caret turned up (`ic caret-up`), `aria-expanded` "false" |
| K1-59 | Strip Copy summary `#stripCopy` | primary, copy icon, "Copy summary", enabled. Splits and Copy summary share the row 1 to 1.3 with an 8 px gap |
| K1-60 | Closed sheet `dialog#splitsDlg` | not open, no child element |
| K1-61 | Sprite `svg.sprite` | the first child of body, takes no space |
| K1-62 | Page end (390, 360) | the working's bottom padding is the strip's height plus 24 px, so the last toggle clears the strip at the end of the page |
| K1-63 | Desktop grid (1280) | 48 px sides, two 560 px columns 64 px apart, the card centred in its column 20 px below the top bar |
| K1-64 | Tab icon | the head's icon link resolves to `src/icon.svg`, whose bytes are R45's |

### KO `docs/design/bill-items-open.html` (inventory K1, sections open) at 390 x 844 and 360 x 780
| Id | Element | Expected |
|---|---|---|
| KO-01 | People row open | `aria-expanded` and `data-open` "true", the caret turned 180 degrees, the summary "Aisyah, Ben, Chen" not visible and keeping its place |
| KO-02 | People body | `#peopleBody` displayed, 4 px above and 20 px below its content, then the hairline. `h2#peopleH` not displayed |
| KO-03 | Person fields | three fields in two columns, 148 px minimum, 8 px gaps, values Aisyah, Ben, Chen, every Remove enabled, as K1-28 to K1-31 |
| KO-04 | Add person | ghost, plus icon, under the list, left aligned, 12 px below it |
| KO-05 | Charges row open | `aria-expanded` "true", the caret turned, the summary not visible |
| KO-06 | Charges body | "Service charge" 10 and "SST" 6 side by side, labels 14/20 600 muted 8 px above the fields, the hint under them 12 px below, `#svcErr` and `#sstErr` hidden |
| KO-07 | Positions at 390 | People ends at 297, Charges at 480, Split at 539, the strip's top at 733, the page 1260 px tall |
| KO-08 | Nothing under the strip | 37 controls in the working, none under the strip at the end of the page or while focused (R49 scenario) |
| KO-09 | The rest | as K1-01 to K1-05 and K1-40 to K1-62 |

### K2 `docs/design/bill-even.html` (inventory K2) at 390 x 844, 360 x 780 and 1280 x 800
| Id | Element | Expected |
|---|---|---|
| K2-01 | Top bar, People row, Charges row | as K1-01 to K1-05, K1-24, K1-25 and K1-32 |
| K2-02 | Desktop People and Charges (1280) | as K1-26 to K1-31 and K1-33 to K1-39 |
| K2-03 | Even half | checked, indigo tint with an inset indigo edge, text colour |
| K2-04 | By item half | unchecked, muted |
| K2-05 | Subtotal label | `label.blk-h.solo` for "evenSub", "Subtotal", 15/20 600, 10 px above the field |
| K2-06 | Subtotal field `#evenField` | `div.field.money.sub-field`, at most 240 px wide, the "RM" unit, `#evenSub` "100.00", placeholder "0.00", named "Subtotal in RM", `aria-invalid` "false" |
| K2-07 | Subtotal error | `p.err#evenErr` present with `hidden` |
| K2-08 | Items block | `#itemsBlock` not in the DOM |
| K2-09 | Card Total and lines | "RM 116.60", lines RM 100.00, "Service 10%" RM 10.00 and "SST 6%" RM 6.60, as K1-09 to K1-12 |
| K2-10 | Splits heading | "Splits" with no "items + charges" legend |
| K2-11 | Rows | Aisyah RM 38.87, Ben RM 38.87, Chen RM 38.86, no `span.wk` |
| K2-12 | Proof | the seal, "Adds up to", RM 116.60, no `span.wk` |
| K2-13 | Spare line and chip | "2 sen left over", "Top of the list" |
| K2-14 | Copy summary and status | as K1-21 and K1-22 |
| K2-15 | Strip | "Total RM 116.60", 111 px, Copy summary enabled |
| K2-16 | Card at 1280 | 570 px tall, the chip at (392, 517) |
| K2-17 | Phone page | fits 390 x 844 without scrolling |

### P1 `docs/design/spare-sen.html` (inventory P1) at 390 x 844, 360 x 780 and 1280 x 800
| Id | Element | Expected |
|---|---|---|
| P1-01 | Light scrim | `#spareDlg`'s `::backdrop` colour equal to the golden's `div.backdrop.light` (`--scrim-light`, 40%) |
| P1-02 | Behind on a phone (390, 360) | the Splits sheet open with K1's receipt under its 72% scrim, as P2-01 to P2-07 |
| P1-03 | Behind at 1280 | K1 with the card |
| P1-04 | Box `dialog.pop#spareDlg` | `--l3` fill, 16 px radius, 20 px padding, `--shadow-pop` |
| P1-05 | Place at 1280 | 340 px wide, left 574, the bottom edge at 632.8, over the working column and never over the splits |
| P1-06 | Place at 390 and 360 | a bottom sheet, full width up to 560 px, 16 px top corners, no bottom border, 255 px tall |
| P1-07 | Title | `h2#spareTitle` "Spare sen", 16/24 700 |
| P1-08 | Close | `button.icon-btn` "Close", 44 x 44, an 18 px X, the head pulled 10 px up and 12 px right so the X sits in the corner |
| P1-09 | Count | `p.pop-sub#spareSub` "1 sen left over", 14/20 muted |
| P1-10 | Choices | three `label.choice`, "Top of the list", "One person" and "At random", 48 px rows 2 px apart, a 20 px ring of 2 px `--line-strong`, the label 16/24 600 |
| P1-11 | Chosen | "Top of the list", its ring and a 10 px dot in indigo |
| P1-12 | No picker | neither `#pickWrap` nor `#randWrap` |
| P1-13 | Room in the sheet (390, 360) | `#sheetScroll` padding-bottom 271 px, and K1's splits stay in view above P1 with no scroll |

### PO `docs/design/spare-sen-one.html` (inventory P1, the picker) at 390 x 844, 360 x 780 and 1280 x 800
| Id | Element | Expected |
|---|---|---|
| PO-01 | Behind | K2, the sheet with K2's receipt on a phone and the card at 1280 |
| PO-02 | Count | "2 sen left over" |
| PO-03 | Chosen | "One person", indigo ring and dot |
| PO-04 | Picker `fieldset.pick#pickWrap` | after the One person label, 40 px left inset, 8 px at the bottom, `legend.sr` "Who pays the spare sen" not visible |
| PO-05 | Pill Aisyah | `label.pill`, off (clear, `--line-strong` border, muted name), value "1" |
| PO-06 | Pill Ben | on (indigo tint, indigo edge, a 14 px indigo check, 12 px left padding), value "2" |
| PO-07 | Pill Chen | off, value "3". Every pill 44 px tall, full pill, 16 px sides, 8 px apart |
| PO-08 | Height | 309 px at 390 and 360, 310 px at 1280 |
| PO-09 | Room in the sheet (390, 360) | `#sheetScroll` padding-bottom 325 px |
| PO-10 | Place at 1280 | left 574, the bottom edge at 560.8 |
| PO-11 | Splits behind | RM 38.86, RM 38.88, RM 38.86, proof RM 116.60 |
| PO-12 | Chip | "One person, Ben", named "Spare sen: One person, Ben. Change" |

### PR `docs/design/spare-sen-random.html` (inventory P1, At random) at 390 x 844, 360 x 780 and 1280 x 800
| Id | Element | Expected |
|---|---|---|
| PR-01 | Chosen | "At random", indigo ring and dot, no `#pickWrap` |
| PR-02 | Pick again in P1 | `div.pick#randWrap` with `#pickAgainSheet`, ghost, 44 px, the shuffle icon then "Pick again", 40 px left inset |
| PR-03 | Receipt chips | `#pickAgain` (shuffle icon first, "Pick again") then "At random" with its caret, 8 px apart |
| PR-04 | Chips at 360 in the sheet | the two chips wrap to a second line under the count |
| PR-05 | Splits behind | RM 38.86, RM 38.87, RM 38.87, proof RM 116.60 |
| PR-06 | Chip name | "Spare sen: At random. Change" |
| PR-07 | Count, height, room and place | "2 sen left over", 309 px (310 px at 1280), `#sheetScroll` padding-bottom 325 px, at 1280 left 574 and the bottom edge at 560.8 |

### P2 `docs/design/splits-sheet.html` (inventory P2) at 390 x 844 and 360 x 780
| Id | Element | Expected |
|---|---|---|
| P2-01 | Scrim | `#splitsDlg`'s `::backdrop` equal to the golden's `div.backdrop.under-sheet` (72%) |
| P2-02 | Sheet `div.glass.dense.sheet` | dense glass, 22 px top corners, the foil, at most 560 px wide and 92% of the viewport tall, its top at 185 at 390 and 124 at 360 |
| P2-03 | Top row `div.sheet-top` | 48 px tall |
| P2-04 | Grab `span.grab` | 36 x 4, `--l5`, centred, 10 px from the top, `aria-hidden` "true" |
| P2-05 | Close | `button.icon-btn` "Close", 44 x 44, at the right |
| P2-06 | Receipt `#sheetScroll .rbody` | 20 px sides, K1's receipt as K1-09 to K1-22, the heading `h2#sheetSplitsH`, the list's `aria-labelledby` "sheetSplitsH", no other id |
| P2-07 | Fit | the receipt is 607 px at 390 and 604 px at 360, and `#sheetScroll` does not scroll |
| P2-08 | Splits button | `aria-expanded` "true" |
| P2-09 | Focus | the sheet has focus with no ring drawn |
| P2-10 | Behind | K1 under the scrim, the strip still drawn |

### M1 `docs/design/new-bill-dialog.html` (inventory M1) at 390 x 844, 360 x 780 and 1280 x 800
| Id | Element | Expected |
|---|---|---|
| M1-01 | Behind | K1 under the 72% scrim (`::backdrop` equal to the golden's `div.backdrop`), the page not scrolling |
| M1-02 | Box `dialog.modal#newDlg` | `min(400px, 100% - 32px)` wide (358 at 390, 328 at 360, 400 at 1280), `--l3`, a 1 px white edge at 10%, 16 px radius, `--shadow-pop`, 24 px padding, centred, its top at 305 (390), 261 (360) and 311 (1280) |
| M1-03 | Title `h2#newTitle` | "Start a new bill?", 18/24 700 |
| M1-04 | Body `p#newBody` | "This clears the people, items and amounts.", 16/24 muted, 8 px below the title |
| M1-05 | Start new bill `#startNew` | `button.btn.btn-danger.btn-lg`, fill rgb(196, 49, 60), label rgb(255, 245, 245), 48 px, 20 px sides, 16 px label |
| M1-06 | Cancel | `button.btn.btn-ghost.btn-lg`, 48 px |
| M1-07 | Actions `div.acts` | 24 px below the body. At 390 and 360 stacked full width, Start new bill first, 8 px apart. At 1280 a right-aligned row |
| M1-08 | Focus | Cancel has focus after a mouse open, with no ring drawn (the fidelity script blurs it, R29 checks the focus) |

### BE `docs/design/bill-empty.html` (inventory S1, first open) at 390 x 844, 360 x 780 and 1280 x 800
| Id | Element | Expected |
|---|---|---|
| BE-01 | People row open (390, 360) | `aria-expanded` "true", the caret turned, the summary "Person 1, Person 2" not visible and keeping its place |
| BE-02 | Person 1 field | value "Person 1", named "Person 1 name", placeholder "Person 1" |
| BE-03 | Person 1 Remove | "Remove Person 1", `disabled`, a faint X, no hover change, `not-allowed` cursor |
| BE-04 | Person 2 field and Remove | as BE-02 and BE-03, "Person 2" |
| BE-05 | Add person | enabled, under the list on a phone, in the heading row at 1280 |
| BE-06 | Charges row (390, 360) | folded, "Service 10%, SST 6%" |
| BE-07 | Split | Even checked |
| BE-08 | Subtotal | empty, the muted placeholder "0.00", `aria-invalid` "false", `#evenErr` hidden |
| BE-09 | Card blocked (1280) | `div.r-total` with "Total" only, then `div.r-empty` with the 28 px muted mark (`#i-mark`) and "Enter the subtotal to see the splits." 16/24, 12 px under it. No lines, splits or Copy summary, a short card |
| BE-10 | Strip message | `p.s-msg#stripMsg` "Enter the subtotal to see the splits.", 14/20, no icon |
| BE-11 | Strip Splits | enabled, as K1-58 |
| BE-12 | Strip Copy summary | `disabled`, faint label and icon, `--l5` border, no fill |
| BE-13 | Strip height | 108 px, its top at 736 at 390 |
| BE-14 | Positions at 390 | People ends at 243, Charges at 296, Split at 355, no page scroll |
| BE-15 | The rest (added 2026-10-13 after the plan check, N5) | as K1-01 to K1-05 (the top bar), K1-33 to K1-39 at 1280 (Charges), K1-60 (the closed sheet), K1-61 (the sprite) and K1-64 (the tab icon) |

### RE `docs/design/rate-error.html` (inventory S2 on a rate) at 390 x 844, 360 x 780 and 1280 x 800
| Id | Element | Expected |
|---|---|---|
| RE-01 | Charges row (390, 360) | open on load, `#chargesBtn.is-bad` with the warning-circle icon and "Check service charge" in its summary, not visible while open |
| RE-02 | Service field | `#svc` "35", `div.field.pct.is-bad` (red edge and a 1 px inset that reads 2 px), `aria-invalid` "true", `aria-describedby` "chargeHint svcErr" |
| RE-03 | Service error `#svcErr` | shown, a 16 px warning circle then "Enter a rate from 0 to 30", 14/20 600 error red, 8 px under the field, two even lines in the half cell ("Enter a rate" over "from 0 to 30") with the icon on the first |
| RE-04 | SST | "6", no "is-bad", `#sstErr` hidden |
| RE-05 | Hint | under both fields on a phone. At 1280 the error grows its own cell downward and the SST field and the hint stay where they were |
| RE-06 | Frame at 1280 | 243 px tall with the bottom fade (`data-down`) |
| RE-07 | Card | blocked with "Check the charges to see the splits." under the mark, as BE-09, 161 px tall at 1280 |
| RE-08 | Strip | "Check the charges to see the splits.", Copy summary disabled, 108 px, its top at 736 at 390 and 672 at 360 |
| RE-09 | Positions at 390 | People ends at 117, Charges at 348, Split at 407, the page is 1125 px |
| RE-10 | The rest (added 2026-10-13 after the plan check, N5) | as K1-01 to K1-05 (the top bar), K1-24 to K1-31 (People), K1-60, K1-61 and K1-64 |

### BU `docs/design/bill-unassigned.html` (inventory S3) at 390 x 844, 360 x 780 and 1280 x 800
| Id | Element | Expected |
|---|---|---|
| BU-01 | Marked item | `li.item.needs` "Mee goreng mamak", a 3 px amber bar (`--warn-ink`) on its left edge, 12 px in from its top and bottom, 7 px left of the content on a phone and 10 px at 1280 |
| BU-02 | Its toggles | Aisyah, Ben and Chen all off, the group "Who had Mee goreng mamak" |
| BU-03 | Other items | as K1-46 to K1-53 without item 3's taps, no class "needs" |
| BU-04 | Card Total and lines | "RM 69.26", RM 59.40, RM 5.94, RM 3.92, then the dashed rule |
| BU-05 | Card message `div.r-msg` | a 22 px amber warning circle and "1 item still needs a person. Tap who had it to see the splits." |
| BU-06 | Nothing after it | no splits, proof, spare line, Copy summary or status |
| BU-07 | Strip | `#stripMsg` with an 18 px amber warning circle and the same sentence on two lines, Copy summary disabled, 128 px |
| BU-08 | The rest (added 2026-10-13 after the plan check, N5) | as K1-01 to K1-05 (the top bar), K1-24 to K1-39 (People and Charges), K1-60, K1-61 and K1-64 |

### BR `docs/design/bill-unreadable.html` (inventory S6) at 390 x 844, 360 x 780 and 1280 x 800
| Id | Element | Expected |
|---|---|---|
| BR-01 | Note on a phone (390, 360) | `div.note` with `role` "status" as a second row of the top bar, full width, 16 px radius, `--info-bg`, an indigo edge at 38%, a 20 px indigo warning circle, the text 14/20 on two lines at 390, padding 4 px top, right and bottom and 16 px left. It adds 78 px to the top bar |
| BR-02 | Note at 1280 | centred in the top bar between the brand and New bill, 44 px tall, no padding top or bottom. [Added 2026-10-16 in execute, fidelity O-4 and A18 Findings.] 44 px is the note's inner height, the 44 px Dismiss note inside it. Its border box is 46 px, in the golden and the app |
| BR-03 | Dismiss note | `button.icon-btn#dismissNote` "Dismiss note", 44 x 44, the X |
| BR-04 | Below | as BE-01 to BE-13, People open on a phone |
| BR-05 | Positions at 390 | People ends at 321, Charges at 374, Split at 433, no page scroll |

### BT `docs/design/bill-twelve.html` (inventory S7) at 390 x 844, 360 x 780 and 1280 x 800
| Id | Element | Expected |
|---|---|---|
| BT-01 | People summary (390, 360) | the visible text of `span.sec-txt` is "Aisyah, Ben, Chen, Person 4 and 8 more" at 390 and "Aisyah, Ben, Chen and 9 more" at 360, equal in text and look to the golden's visible `.fit-wide` or `.fit-narrow` |
| BT-02 | People list (1280) | twelve fields, Person 4 to Person 12 blank with their placeholders, every Remove enabled |
| BT-03 | Add person | `disabled`, faint label and icon, `--l5` border, `not-allowed` cursor |
| BT-04 | Splits at 1280 | `ul.r-splits.many`, two columns of six filled down then across, a 24 px column gap and an 8 px row gap |
| BT-05 | Figures | Aisyah, Ben, Chen and Person 4 to Person 8 RM 9.72, Person 9 to Person 12 RM 9.71, proof RM 116.60, "8 sen left over" with "Top of the list" |
| BT-06 | Card | 658 px tall at 1280 |
| BT-07 | Sheet on a phone (not drawn) | one column of twelve, checked by the R20 scenario, because the golden draws the sheet closed |
| BT-08 | The rest (added 2026-10-13 after the plan check, N5) | as K1-01 to K1-05 (the top bar), K1-32 to K1-39 (Charges), K1-60, K1-61 and K1-64 |

### W1 `docs/design/bill-large.html` (inventory W1) at 390 x 844, 360 x 780 and 1280 x 800
| Id | Element | Expected |
|---|---|---|
| W1-01 | Item 5 | a blank name with the placeholder "Item 5", the price "964.50" whole in the 104 px field at 390 and 360, Aisyah on, the names "Item 5 name", "Item 5 price in RM", "Remove Item 5" and "Who had Item 5" |
| W1-02 | Total | "RM 1,193.87", 48 px at 1280 inside the ~~412 px~~ 410 px card body (`#rbody`, the 460 px card less 2 px of edge and 48 px of padding, in the golden and the app, fidelity O-2, changed 2026-10-16 in execute), one line on the strip at 360 |
| W1-03 | Lines | RM 1,023.90, RM 102.39, RM 67.58 |
| W1-04 | Aisyah | RM 1,153.65 with "989.40 + 164.25", Ben and Chen as K1 |
| W1-05 | Proof and spare line | RM 1,193.87 with "1,023.90 + 169.97", "1 sen left over" with "Top of the list" |
| W1-06 | Frame | at 360 it holds 614 px in 581 with the bottom fade (`data-down`), at 390 it fits with no fade, at 1280 it is 291 px tall with the fade |
| W1-07 | The rest (added 2026-10-13 after the plan check, N5) | as K1-01 to K1-05 (the top bar), K1-24 to K1-39 (People and Charges), K1-60, K1-61 and K1-64 |

### ST `docs/design/states.html` (specimen sheet, no pixel diff, 1.0 precedent)
Checked on the app at 390 x 844, the card pieces at 1280 x 800. "Equal to the piece" uses the property list of "Equal to the golden", never width, because the specimen frames are narrower than the app.

| Id | State | Expected on the app |
|---|---|---|
| ST-01 | Subtotal error (S2 on an amount, Even) | K2 with Subtotal "100,00" left. `#evenField.is-bad`, `aria-invalid` "true", `#evenErr` shown 8 px below, 14/20 600 error red with a 16 px warning circle, wrapper and paragraph equal to the piece's. The card and the strip read "Enter the subtotal to see the splits." |
| ST-02 | Price error (S2 on an amount, By item) | K1 with "Char kuey teow price in RM" "13,50" left. `p.err#ie2` last in `div.item-row`, equal to the piece's plus ~~`text-align` right~~ `justify-self` end, its right edge at the price field's right edge, spanning the name and price columns, the toggles 8 px below. The card reads "Give every item a price to see the splits." Changed 2026-10-15 in execute, planner touch before A18 (ledger S7 row 24, F-A8-1). The golden CSS sets no `text-align` on `p.err`, so it computes `start` in the piece and in the app (spec R14) |
| ST-03 | Rate error, SST | K1 with Charges opened first and SST "25" left. `aria-describedby` "chargeHint sstErr", the message on two even lines with the icon on the first, the hint still under both fields |
| ST-04 | Folded "Check service charge" | the RE seed with Charges folded by a click. `button.sec-btn.is-bad`, the summary 14/20 600 error red with a 16 px warning circle 6 px before the words, right aligned beside the caret, the name still "Charges" |
| ST-05 | Folded "Check SST" | as ST-03, then Charges folded, as ST-04 |
| ST-06 | Folded "Check both rates" | K1 with Service "35" and SST "25", Charges folded, as ST-04 |
| ST-07 | Strip copied (S4) | K2 after a click on `#stripCopy`. "Summary copied" with a 16 px indigo check, 14/20 600, beside the Total on the same line, the strip 111 px |
| ST-08 | Strip blocked (S4) | K2 with reject.js after a click on `#stripCopy`. `p.status.is-fail` with a red warning circle on its own line under the Total, on two lines, the strip 153 px |
| ST-09 | By item, nothing to work out (phone) | a cold boot and "By item". The strip's `p.s-msg` "Add each item and tap who had it to see the splits." in place of the Total, on two lines where the strip is narrower than the sentence, Copy summary disabled |
| ST-10 | Save warning (S5) | a cold boot with D-a and one change. `div.note.is-warn` in the top bar, `--warn-bg`, an amber edge at 45%, a 20 px amber `#i-warning`, 14/20 text, 16 px right padding, no dismiss, two lines at 390. At 1280 centred in the top bar, 44 px tall, one line. [Added 2026-10-16 in execute, fidelity O-4.] Here 44 px is the border box, since the save warning has no Dismiss note (BR-02's 44 px is the inner height of the note with one), as `system.md` Banner gives 44 on the desktop |
| ST-11 | Card copied (S4, 1280) | K2 after a click on `#copyBtn`. `#cardStatus` centred 12 px under Copy summary with the indigo check |
| ST-12 | Card blocked (S4, 1280) | K2 with reject.js after a click on `#copyBtn`. `#cardStatus.is-fail` ~~on two lines, left aligned beside the icon~~ on one line at 1280 x 800, centred like the copied line of ST-11, with the red warning circle before the text, where the S4 piece wraps it to two lines at its 282 px card width. Changed 2026-10-15 in execute, planner touch before A18 (ledger S7 row 26, F-A10-1). The app's card at 1280 x 800 is the card of `bill-even.html`, whose body is 410 px wide, and the golden CSS fits the line on one line there, 20 px tall. The markup, the look, the icon and the place under Copy summary equal the piece. `states.md` says "On the card it wraps to two lines", true of the piece only, and stays as written (goldens are immutable) |
| ST-13 | Two items still need a person (card, 1280) | K1 with Chen untapped from Mee goreng mamak and Ben from Char kuey teow. "2 items still need a person. Tap who had each one to see the splits." styled as BU-05 |
| ST-14 | Plural on the strip (not drawn) | the same bill at 390. The strip says the same with its amber icon, styled as BU-07 |
| ST-15 | Error field with focus (not drawn, `system.md` Focus) | RE with `#svc` focused by Tab. The red edge stays and the ring is added |
| ST-16 | Card no-prices message (not drawn) | a cold boot and "By item" at 1280. "Add each item and tap who had it to see the splits." in the form of BE-09 |
| ST-17 | Card prices message (not drawn) | K1 with item 1's price "abc" at 1280. "Give every item a price to see the splits." in the form of BE-09 |

## Fidelity gate (Chromium only)
- **Harness.** The sdlc plugin harness `fidelity.py` that `run.py` resolves with `harness_path` (`SDLC_HARNESS` when set, otherwise `{sdlc}/harness/fidelity.py`), frozen mode, unmodified, started as `[sys.executable, <harness>, ...]` (CG-11 of 1.0). The runner creates no venv and installs nothing. The harness renders each side in its own headless Chromium with reduced motion, `--force-color-profile=srgb` and `--hide-scrollbars`, pins `Math.random` and the clock, injects its freeze stylesheet, renders with Playwright `bypass_csp`, and writes `golden.png`, `candidate.png`, `diff.png`, `styles.json` and `report.json`.
- **Chromium only.** The goldens are Chromium renders and the harness is Chromium only, so pixel identity in WebKit is not a requirement (ledger S5 row 2, spec R40). WebKit is covered by the suite and the live gate.
- **The policy is off inside every render.** A fidelity pass says nothing about the CSP. The suite's R38 scenarios and the live gate never bypass it.
- **Runner.** `python tests/browser/fidelity/run.py` from the project root. It manages the server with the lifecycle rules of How to run, runs the two controls and then the 40 pairs, each into its own folder, and adds no rendering or diff logic of its own.
- **Golden.** `./docs/design/<screen>.html`, opened by the harness as a file, never written. **Candidate.** `http://127.0.0.1:<port>/`, brought into the golden's state by the test-side scripts below, never by a hook in the app.
- **Seed scripts** (`--candidate-init-script`). Run before the app's own scripts so the app boots into that bill through its real load path. `seed-s1.js` (K1), `seed-s2.js` (K2), `seed-s5.js` (BU), `seed-re.js` (RE), `seed-w1.js` (W1), `seed-t12.js` (T12), `seed-one.js` (ONE), `seed-rnd.js` (RND) and `seed-b1.js` (B1). The harness takes one init script per render, so each seed file holds two parts. First the clipboard stand-in, the text of `tests/browser/clipboard/recorder.js` byte for byte. Then exactly one statement, `localStorage.setItem("split.draft", '<seed JSON>')`. `test_R40_fidelity_seeds_match` keeps the first part equal to `recorder.js` and the seed equal to `seeds.py`. The constitution (Browser gates) asks for a stand-in in every run that presses anything, and 16 of the 40 pairs press controls through their after-load script. All nine seed files carry it, so one rule covers every seeded pair. The `bill-empty` pairs and the two controls load no init script and press nothing, so they are render-only captures, which need no stand-in. [Changed 2026-10-13 after the plan check (B2). Each file held only the `setItem` statement, so no candidate had a stand-in.]
- **After-load scripts** (`--candidate-after-load`). Each first checks that the stand-in is in place and throws `new Error("clipboard stand-in missing")` before any click when `window.testClipboardWrites` is not the number 0, or when `navigator.clipboard.writeText` exists and its source text holds "[native code]" (added 2026-10-13 after the plan check, B2). A pair whose script throws cannot pass, because no click happened and the page never reaches the golden's state, and `run.py` counts a harness exit other than 0 or a missing `report.json` as FAIL, as in 1.0. The `@R40` scenario "An after-load script presses nothing without the clipboard stand-in" is this check's control. Each script then clicks with `element.click()`, waits two animation frames, calls `document.activeElement.blur()` and waits two more frames (1.0 PD-16, because a scripted click makes Chromium draw a keyboard focus ring that a real mouse click does not).
  - `open-sections.js` clicks `#peopleBtn`, then `#chargesBtn`.
  - `open-splits.js` clicks `#splitsBtn`.
  - `open-spare.js` clicks `#splitsBtn` and then the sheet's spare chip below 1024 px, and `#spareBtn` from 1024 px.
  - `open-new-bill.js` clicks `#newBill` (changed from 1.0's `header .btn`).

  | Golden | Seed | After load | Widths |
  |---|---|---|---|
  | `bill-items` | `seed-s1.js` | none | 390, 360, 1280 |
  | `bill-items-open` | `seed-s1.js` | `open-sections.js` | 390, 360 |
  | `bill-even` | `seed-s2.js` | none | 390, 360, 1280 |
  | `spare-sen` | `seed-s1.js` | `open-spare.js` | 390, 360, 1280 |
  | `spare-sen-one` | `seed-one.js` | `open-spare.js` | 390, 360, 1280 |
  | `spare-sen-random` | `seed-rnd.js` | `open-spare.js` | 390, 360, 1280 |
  | `splits-sheet` | `seed-s1.js` | `open-splits.js` | 390, 360 |
  | `new-bill-dialog` | `seed-s1.js` | `open-new-bill.js` | 390, 360, 1280 |
  | `bill-empty` | none (each render is a fresh browser) | none | 390, 360, 1280 |
  | `rate-error` | `seed-re.js` | none | 390, 360, 1280 |
  | `bill-unassigned` | `seed-s5.js` | none | 390, 360, 1280 |
  | `bill-unreadable` | `seed-b1.js` | none | 390, 360, 1280 |
  | `bill-twelve` | `seed-t12.js` | none | 390, 360, 1280 |
  | `bill-large` | `seed-w1.js` | none | 390, 360, 1280 |

  That is 40 pairs. A 390 width runs at `390x844`, 360 at `360x780` and 1280 at `1280x800`. `states.html` has no pixel pair, its pieces are the ST rows.
- **Command.** For each pair. `python` stands for `sys.executable`.

  ```bash
  python <harness>/fidelity.py \
    --golden ./docs/design/<screen>.html \
    --candidate http://127.0.0.1:<port>/ \
    --viewport <390x844|360x780|1280x800> --dpr 1 --color-scheme dark \
    --browser-arg=--disable-lcd-text \
    --fixed-time 2026-10-13T09:00:00 \
    --threshold 0.01 \
    [--candidate-init-script ./tests/browser/fidelity/<seed>.js] \
    [--candidate-after-load ./tests/browser/fidelity/<after-load>.js] \
    --out ./docs/modules/split-app/qa/fidelity/<YYYYMMDD-HHMMSS>/<screen>-<viewport>/
  ```
- **Flags and why.** `--color-scheme dark`, because the design is one dark theme (`<meta name="color-scheme" content="dark">`). `--dpr 1` and a full-page render. `--browser-arg=--disable-lcd-text`, because a native modal sits in the top layer with greyscale anti-aliasing while the golden's in-flow stand-in gets LCD anti-aliasing (1.0 PD-13, measured). It applies to both renders and hides no real difference. `--fixed-time` keeps re-runs byte-stable, and the app reads no clock.
- **Threshold.** `--threshold 0.01`. A pair passes only when `report.json` has `"dimensions_match": true` and `"mismatch_pixels": 0`. A non-zero count is a finding for the human and is never handled by raising the threshold (1.0 PD-13).
- **Controls (run first, each in its own folder).** Each asserts what the gate needs and must behave as written before any pair counts.
  - **Self-compare.** Golden `bill-items.html` against the candidate `http://127.0.0.1:<port>/docs/design/bill-items.html` (the same golden, read through the test server, never written) at `390x844` with no scripts. It must report `"dimensions_match": true` and `"mismatch_pixels": 0`, which proves the flags and the harness add no noise.
  - **No seed.** Golden `bill-items.html` against `http://127.0.0.1:<port>/` with no init script and no after-load script (the `bill-empty` state) at `390x844`. It must report `"mismatch_pixels"` above 0, which proves the gate can fail.
  - If either control misbehaves, the run stops, `run.log` gets a `CONTROL FAIL` line, and the verdict is NOT RUN.
- **Per-element check.** The fidelity finder compares the two sides of `styles.json` against the FE element checklist. Attributes the harness does not dump (ARIA, `disabled`, `checked`, `maxlength`, `inputmode`, `placeholder`, `data-open`) are checked by the R3 DOM walk. Only the allowed differences of `spec.md` may appear.
- **Evidence.** One run writes `docs/modules/split-app/qa/fidelity/<YYYYMMDD-HHMMSS>/` with `control-self-390x844/`, `control-noseed-390x844/`, one subfolder per pair (`<screen>-<viewport>/`, for example `bill-items-390x844/`) holding the harness outputs, and `run.log` (the commands, the server PID and port, the harness output, one `CONTROL` line per control and one PASS or FAIL line per pair with its mismatching pixel count). The verdict goes to `docs/modules/split-app/findings/fidelity.md`.
- **Verdict.** 1 to 1, with no additions, subtractions or modifications, for all 40 pairs.

## Cold-boot live-e2e gate (Chromium and WebKit)
- **Script.** `tests/browser/live_e2e.py`, run once with `--engine chromium` (the default) and once with `--engine webkit`, after the suite is green in both engines and the fidelity gate is green.
- **Control and baseline** (constitution, Gates and evidence, added 2026-10-13 after the plan check, B3). The gate compares the running app with the cold-boot rule (R2, R41), a first visit with empty storage that shows `bill-empty` with People open and the strip reading "Enter the subtotal to see the splits.", and it must be able to fail when the app does not start empty. Its control is the same script in the same engine against the same server, run once with `--control seeded` just before that engine's green run (the `@R41` scenario "The live gate fails when the app starts from a saved bill"). It makes its one context with `storage_state` holding the K2 seed, runs the same steps, and must stop at step 1 with pass false, failing on the cold-boot assertions while step 1's clipboard check passes. Its evidence is kept as the RED capture in `docs/modules/split-app/qa/live-e2e/<YYYYMMDD-HHMMSS>-<engine>-control/`, beside the green run and never overwritten. A control that passes step 1 means the gate cannot fail, and the gate is not met. The baseline is the gate's own prior run in the same engine, first the A0 runs of the 1.0 gate (`--engine chromium` and `--engine webkit`), then each earlier green run of the v1.1.0 gate.
- **Control mode.** `--control seeded` is the only option that changes what the script does, and it can only make the run fail. A run without it writes `"control": null` in `summary.json`, and only such a run can meet the gate. The seed is test-side data given to the context as `storage_state`, never through the app. The script passes `storage_state` in one place only, the one `rig.new_context` call, as the K2 state when the parsed `--control` value equals `"seeded"` and `None` otherwise. The `@R41 @static` scenario "The gate script makes a cold context except on its control path" checks exactly that, with planted copies, and "Works right" asserts `"control": null` in each green run's `summary.json`. [Added 2026-10-13 after the plan re-check (F11). The sealed 1.0 test `test_R41_the_gate_uses_real_gestures_and_reads_only` banned `storage_state` outright, and the plan did not give the guard its new form.]
- **Rules.** The browser is launched by `rig.launch(playwright, engine)`, headless. One new context with **no** `storage_state` (apart from the control mode) and **no** `bypass_csp`, so the shipped policy is live for the whole run. Viewport 390 x 844, device scale factor 1, colour scheme dark, reduced motion `reduce`. Its only init scripts are `tests/browser/clipboard/recorder.js` (never the operating system clipboard, CG-7 of 1.0) and `tests/browser/csp/listener.js`. No clipboard permission is granted. The entry point is the shipped `index.html` at `/`. Only real gestures change the app (mouse clicks on visible controls, keyboard typing, key presses). `page.evaluate` only **reads** (`window.testClipboardText`, `window.testCspViolations`, `document.activeElement`, `localStorage` for a check, the source text of `navigator.clipboard.writeText`), and never changes state. No seed, fixture, app hook or test-only code path in the app.
- **Flow.** Each numbered step takes a ~~screenshot~~ capture and adds a line to `steps.log` (step, gesture, assertion, PASS or FAIL). [Changed 2026-10-14 in execute, ledger H-05, ORCH. The capture is the page's newest screencast frame once the step's checks are done, never `page.screenshot` or `locator.screenshot`, because in WebKit every screenshot adds an inline stylesheet that the policy refuses, one console error and one CSP violation each (spec R59 (4)). The script starts `page.screencast.start` once after the page opens, with `on_frame` and `size` equal to the viewport, and stops it at the end. For each capture it waits two animation frames, then until no new frame has come for 400 ms, at most 5 s, and a step that gets no frame or no quiet in that time fails with "capture gave up after 5 s". The same capture runs in both engines. Measured by the planner's read-only probe on 2026-10-14, frames gave no console line and no violation in either engine, came at 390 x 844, and showed the open dialog. So step 9 needs no allowance.]
  1. Open `/`. Assert that `navigator.clipboard.writeText` is the stand-in (its source text holds no "[native code]"), that the screen is `bill-empty` with People open, and that `split.draft` is absent.
  2. In the open People section replace Person 1 with "Aisyah" and Person 2 with "Ben", click Add person, type "Chen", and type "100.00" in Subtotal. Assert that the strip reads "Total RM 116.60".
  3. Click Splits. Assert the splits RM 38.87, RM 38.87, RM 38.86, "2 sen left over" and the proof RM 116.60. Click Copy summary in the sheet. Assert "Summary copied" and that `window.testClipboardText` equals the S2 block of core R24 exactly.
  4. Click the sheet's spare chip and choose One person. Assert that the Aisyah pill is checked and the splits are RM 38.88, RM 38.86, RM 38.86. Tap the Ben pill and assert RM 38.86, RM 38.88, RM 38.86.
  5. Choose At random, then click Pick again in P1. Assert that the splits changed and still add up to RM 116.60. Close P1, click Copy summary in the sheet, and assert that lines 3 to 5 of `window.testClipboardText` equal the sheet's splits rows. Open P1 from the chip again, choose Top of the list, and assert RM 38.87, RM 38.87, RM 38.86. Close P1 and the sheet.
  6. Click By item and add the four K1 items by typing their names and prices and tapping their people. Assert that the strip reads "Total RM 69.26". Click Splits, assert the K1 rows with their working and the proof, click Copy summary in the sheet, and assert that `window.testClipboardText` equals the S1 block of core R24 exactly. Close the sheet.
  7. Reload in a new page of the same context. Assert the K1 screen with both sections folded. Click Even and assert Subtotal "100.00" and the splits RM 38.87, RM 38.87, RM 38.86.
  8. Click New bill. Assert the dialog with Cancel focused. Click Start new bill. Assert `bill-empty` with People open and focus on New bill. Reload and assert `bill-empty` with People open again (CG-P4).
  9. Throughout, assert zero console errors, zero page errors and zero recorded CSP violations (in Chromium also no console text holding "Content Security Policy"), and only same-origin GETs.
- **Evidence artifact.** `docs/modules/split-app/qa/live-e2e/<YYYYMMDD-HHMMSS>-<engine>/` with ~~`01-*.png`~~ `01-*.jpg` onwards (one per step, the viewport's screencast frame, changed 2026-10-14 in execute, H-05), `steps.log`, `console.log`, `network.log`, `clipboard-s2.txt`, `clipboard-s1.txt` and `summary.json` (start and end time, engine, ~~`browser.version`~~ `browser_version` (the value of Playwright's `browser.version`, the flat key every run writes, QA-S5-3, changed 2026-10-16 in execute), port, server PID, the init scripts used, `control` null or "seeded", result). A run stops at its first failed step and still writes the ~~screenshots~~ captures taken so far, `steps.log`, `console.log`, `network.log` and `summary.json`. After each run, list the folder to prove the files landed there. **No artifact means not done**, and a WebKit failure blocks the seal (ledger S5 row 2). A green run with no control capture of the same engine beside it does not meet the gate (B3).

## Regression
- Re-run the functional suite in Chromium and in WebKit, the fidelity gate in Chromium and the live gate in both engines in the final all-modules pass, together with `node --test "tests/**/*.test.js"`. The WebKit rows of `docs/regression/REGRESSION.md` are an orchestrator action (ROADMAP, section v1.1.0).
