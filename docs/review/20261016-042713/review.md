# Stakeholder review, Danial's Splity Tab v1.1.0

**Role.** Stakeholder reviewer (agent), `sdlc:review`. This is an agent's verdict. UAT is the owner's, and only he seals the version.
**When.** 2026-10-16, 04:27 to 05:00 local (UTC+8). **Code.** HEAD `22e388b`, whose `src/`, `tests/` and `index.html` are the code `sdlc:regression --full` judged (`b0992b4`, PASS 2026-10-16 04:25, `docs/regression/REGRESSION.md`). `git diff --stat 22e388b -- src tests index.html` is empty, and the only change in the working tree is the orchestrator's `docs/progress/STATE.md`.
**Direction.** Personal, so the compliance audit is skipped.
**The question.** Review asks whether the built thing deviates from the brainstorm and the specs. UAT asks whether it is what the owner asked for and whether he can live with it. Same app, different seat, so both drive it.

## Verdict

**Shippable to UAT.** Every capability of the brainstorm and its v1.1.0 delta works on a cold boot with no seed, with real taps, clicks and keys, in Chromium 149 (1280 x 800 with the mouse and keyboard, 390 x 844 and 360 x 780 with taps) and in WebKit 26.5, the engine of Safari on iPhone (390 x 844 and 360 x 780 with taps). 303 checks pass, 0 fail, 44 are recorded as information (Chromium 193 pass and 26 information, WebKit 110 pass and 18 information). Every money figure the drive compares was worked out by the drive script from the brainstorm's rules in whole sen, not read from the app. The app equals its golden to 0 pixels in WebKit at the first visit, at the key screen K1 and at the large bill W1, each rendered by the same engine.

Nothing found blocks UAT. Three items need the owner's eye, none of them new code.
- D1. In WebKit a tap that opens a popup or closes the Splits sheet leaves a focus ring on the control the app focuses (Cancel in New bill, the checked choice in Spare sen, Splits after the sheet closes). The fidelity finder recorded it as an engine difference. The ledger names only the ring on Splits.
- O1. A price of 99,999.99 does not show whole in its field at 360 px (it shows "99999.9" until the field is focused). The splits table fits, as promised. No record names this.
- D2. The README header still shows the 1.0 name and look, by the orchestrator's ruling until the seal.

## How it was driven

- The drive script serves the project root itself with `python -m http.server` on a free `127.0.0.1` port, one server per engine run, and stops it by PID at the end with its port checked refusing. Final runs, Chromium PID 26096 on port 8678, WebKit PID 20884 on port 8680 (`run-log-chromium.txt`, `run-log-webkit.txt`).
- Every context fresh, empty `localStorage`, dark colour scheme, headless. The project's clipboard stand-in (`tests/browser/clipboard/recorder.js`, or `reject.js` for the blocked case) and CSP listener load before any page in every context, and the drive checks the stand-in is in place before its first gesture. The system clipboard was never reached.
- Real gestures only. Taps at a person's pace on the phone sizes (never two taps within 600 ms and 30 px unless the case is a double tap), mouse clicks at 1280 x 800, keyboard typing everywhere. A held key is `keyboard.down`, 520 ms, four more `keyboard.down`, then `keyboard.up`, as the suite holds it.
- Storage failure was made only inside a throwaway context, with the project's test drivers `tests/browser/storage/fail-set.js` (writes throw) and `fail-get.js` (the storage getter throws from boot). An unreadable draft was made by writing broken text into that context's storage and reloading.
- Look checks load the golden from `docs/design/` (read only) into a second page of the same context at the same size, compare pixels, then compare by eye.
- The script is `review_v110.py` in this folder. Results per check are in `results-chromium.json` and `results-webkit.json`. Four trial runs while the script was written sit in `trial-1/` to `trial-4/`. Their failures were the script's own (it read the strip's label and figure as one text, measured P1 while it was still rising, and read focus before a dialog's close event), each fixed before the final runs.

## What was driven, per capability

Captures are in this folder with a `chromium-` or `webkit-` prefix. Every row ran in both engines except the desktop rows, which ran in Chromium.

| Brainstorm capability, ledger scope | What was done with real gestures | Result | Captures |
|---|---|---|---|
| Cold boot, R2 | Empty storage gives two people "Person 1" and "Person 2", both Remove disabled, Even, an empty Subtotal, 10 and 6, "Enter the subtotal to see the splits." on the card and the strip, Copy summary disabled, nothing stored. On a phone People open and Charges folded | PASS | `*-m01-cold-boot.png` beside `*-m01-cold-boot-golden.png` |
| C1 People | Rename, Add person (focus on the new empty field), a double press on Add person adds one, 12 is the limit, 2 the floor, duplicate names, a blank name shows its place, removing a person takes them off every item, focus after removing the last person | PASS | `*-m11-twelve.png`, `*-m13-twelve-folded.png` |
| C2 Even split, key flow 1 | Aisyah, Ben, Chen, Subtotal 100 gives Total RM 116.60, splits RM 38.87, 38.87, 38.86, the bill lines and "Adds up to RM 116.60". Copy summary puts the brainstorm's own example text on the stand-in, word for word | PASS | `*-m02-even*.png` |
| Amount rules | "100,00", "0", "100000" and "1.234" show "Enter an amount like 12.50" on leaving and block the receipt. "12", "12.5", "12.50" and "99999.99" are accepted | PASS | `*-m03-amount-error.png` |
| C3 By item, key flow 2 | No item blocks with its message, a price with nobody tapped gives "1 item still needs a person..." and the amber marker, a blank price gives "Give every item a price...", two untapped items give the plural. The four K1 items give RM 69.26, Aisyah RM 29.04 (24.90 + 4.14), Ben RM 15.74 (13.50 + 2.24), Chen RM 24.48 (21.00 + 3.48), "1 sen left over", and the 1.0 summary text. Switching to Even and back keeps both sets of input | PASS | `*-m06-k1.png` beside `*-m06-k1-golden.png` |
| C3 changed, fits 360 px (S2, H-02) | W1 (a fifth item RM 964.50) at 360 x 780, no sideways scroll, "964.50" whole in its field, strip "Total RM 1,193.87", sheet Aisyah RM 1,153.65, every figure inside its box. Then five items at RM 99,999.99 (Total RM 582,999.95), no sideways scroll and no clipped figure in the page, the strip or the sheet | PASS, O1 below | `*-w01-w1.png`, `*-w02-w1-sheet.png`, `*-w03-max-sheet.png` |
| C4 Charges | Service 35 shows "Enter a rate from 0 to 30" and blocks with "Check the charges to see the splits.", folded Charges reads "Check service charge" with its marker, 0 turns service off (Service 0%, RM 0.00, Total RM 62.96), SST 25 shows "Enter a rate from 0 to 20" and "Check SST", a blank rate shows no inline error but blocks and reads "Check both rates", the hint text | PASS | `*-m07-rate-error*.png` |
| C5 Splits that add up | The proof line and its working on every split shown, by item "59.40 + 9.86" | PASS | |
| C6 Copy summary | From the card, the strip and the sheet. "Summary copied". A blocked clipboard says "Could not copy. Your browser blocked the clipboard.", and the next change clears the status | PASS | `*-b01-copy-blocked.png` |
| C7 Draft kept, key flow 3 | Saved as version 2 after each change, nothing written at boot, a reload and a closed tab opened again show the bill as it was, on a phone a saved bill opens with both sections folded | PASS | |
| C8 New bill, key flow 4 | The dialog's words, focus on Cancel, Cancel changes nothing, Start new bill returns to two people, Even, 10% and 6%, Top of the list, focus on New bill, People open on a phone | PASS | `*-m09-new-bill-dialog.png`, `*-m11-new-bill-dialog.png`, `*-after-new-bill.png` |
| C9 Spare sen (S1) | P1 opens with "Spare sen", "2 sen left over" and three choices, Top checked and focused. One person picks the first person at once, Ben gives 38.86, 38.88, 38.86 and the copied text follows. At random gives two different people one sen each, Pick again (by key in P1, by tap or click on the receipt) draws a different split, a reload keeps the draw, Top of the list brings back the 1.0 split. By item, the picker lists only people on an item (Dan, on no item, is left out and listed at RM 0.00), Ben gives 15.75 and Aisyah 29.03. Escape and a click on the backdrop close P1 with focus on the chip. On the desktop P1 sits 16 px right of the card with its bottom level with the chip | PASS | `*-m04-p1-one-person-ben.png` beside its golden, `*-m05-p1-at-random.png` |
| C10 Save warning (S4) | Storage that cannot write shows "This bill is not being saved on this device. It will be lost when you close this tab." at the first failed save, no dismiss control, the app keeps working, the warning goes after the next save works and the store holds the bill on screen. Storage refused from boot shows it in the first render and clears without a reload when storage comes back | PASS | `*-s01-save-warning.png` |
| Unreadable draft, A23 | The note with Dismiss, a new bill saved, People open on a phone. A double click or double tap on Dismiss note acts once (note gone, focus on New bill, People still open, the store unchanged). Dismiss note is the first Tab stop and a held Enter on it opens no dialog | PASS | `*-u01-unreadable-note.png` |
| Held Enter on Remove (S3, SEC-04) | Enter held on the only item's Remove removes it, adds no blank item, the id counter is unchanged and focus is on Add item | PASS | |
| Names stay plain (H-10) | A pasted U+202E and U+2028 leave "Ben", "Aisyah" and "Tehtarik" in the fields and the store, the People line holds no such character, the copied summary reads the same names | PASS | |
| C0 Look (S7) | First visit, K1, the One person popup, the Splits sheet, the New bill dialog and W1 against their goldens. WebKit 0 px at the first visit, K1 and W1. Chromium 0 to 116 px at those states. The popups and sheets differ by 3,296 to 45,779 px in either engine, eye-checked as the page behind (scrolled by the drive) under the glass and the scrim, plus D1's ring in WebKit. The pixel gate (seeded, fixed time) is the authority, 40 of 40 pairs at 0 px in the regression | PASS by eye, D1 below | each `*-golden.png` beside its app capture |
| Folding sections (G2) | Folded summaries "Aisyah, Ben, Chen" and "Service 10%, SST 6%", a header row opens on Enter and folds on Space, twelve blank names read "Person 1, Person 2, Person 3 and 9 more" | PASS | `*-m06-k1.png` |
| Strip and Splits sheet | Open by a tap (focus on the sheet, no ring drawn, aria-expanded true), Close, Escape and a tap on the backdrop close it with focus back on Splits, a double tap on Splits opens it once and its second tap reaches nothing under it (nothing copied) | PASS, D1 | `*-m09-splits-sheet-k1.png`, `*-m10-after-sheet-close-strip.png` |
| Logo (S6) | Header mark path equals the golden's S12, `src/icon.svg` equals the golden's tab icon byte for byte (470 bytes), linked as SVG, drawn in #A3AAFF under dark and #1E2140 under light | PASS | `*-16x16-tab-icon-dark.png`, `*-16x16-tab-icon-light.png` |
| Name (S8) | Tab title "Danial's Splity Tab", header "Splity Tab" only, no "Danial" and no "D" in the page | PASS, D2 for the README | |
| Keyboard (R32) | Phone K1, 31 Tab stops from New bill to Copy summary in both engines. Desktop K1 starts New bill, the chip, Copy summary, Add person | PASS | |
| Desktop layout (R55, R56) | 1280 x 800 never scrolls, the card at 98, 84, 460 x 642, header rows hidden and both bodies shown, the item frame scrolls inside itself | PASS | `chromium-1280x800-m06-k1.png` |
| Nothing leaves the device | Every request of the app pages is a same-origin GET for the page, `src/` or `favicon.ico` (570 in Chromium, 330 in WebKit). No console error and no page error from the app. No CSP violation from the app | PASS | |
| S5 WebKit, S9 several bills | WebKit drove every phone flow above. `docs/future/several-bills.md` exists as a document and nothing of it is built | PASS | |

Information recorded (not pass or fail).
- In WebKit every screenshot of the app adds one console line "Refused to apply a stylesheet..." and one `style-src` violation (spec R59 (4), the tool, not the app). The drive counted 19 of each against 19 screenshots. So in WebKit the app's own console cleanliness rests on the live gate, which captures by screencast frames and found 0 in the regression.
- Right after Escape, the browser's own close step runs before the app's `close` handler. In both engines Splits still reads `aria-expanded="true"` for that moment after the sheet closes, and in WebKit focus sits on the sheet for that moment after P1 closes. Both settle within the bounded wait (R59 (2)).
- The W1 frame shows `data-up` after the fifth item is added and scrolled into view, and `data-down` once scrolled back to its top, as R56 says.

## The hard questions

**Every brainstorm capability delivered.** Yes. C1 to C8 of 1.0, C9 and C10, the changed C3 and C0, the name and the logo. The four key flows hold. S9 is a document, as ruled.

**Every R# working.** Every requirement this drive touched works in both engines. Not driven here and standing on the regression (Node 406, Chromium 742, WebKit 742 with 3 counted skips, pixel gate 40 of 40 at 0 px, cold boot 9 of 9 in both engines, security and code review PASS) are reduced motion (R36), injection-shaped names (R37), the CSSOM allowance and the scans (R38, R39), the pixel gate itself (R40), the DOM walk (R3), the 50 item limit, the edges of the 500 ms and 22 px tap rule (R57 (b)), the engine switch (R58) and hover states.

**Vision and quality held.** Yes. It reads as the G2 "Glass Console" the owner picked, the dark slate page, the indigo accent, one glass receipt with the proof in indigo, the strip and the sheet on a phone, the inputs first. The by-item table now holds a six-figure bill at 360 px.

**Any spec silently dropped.** None found. Every user-facing string literal under `src/ui/` and in `src/main.js` is in the app spec's Copy table, and every Copy row the drive reached shows where the spec says.

**Anything built that no spec or design asked for.** Nothing at the product level. Behaviour beyond the brainstorm's words exists, and each piece was ruled (table below).

**Any design not one-to-one.** In Chromium, no. In WebKit, D1.

## Deviations

| # | Where | What | Cause | Tag |
|---|---|---|---|---|
| D1 | WebKit, phone. New bill's dialog, the Spare sen popup, Splits after its sheet closes | After a tap the app's first focus matches `:focus-visible`, so the system's 2 px ring shows on Cancel (`webkit-390x844-m11-new-bill-dialog.png`, where the golden rendered in WebKit draws none, `webkit-390x844-m11-new-bill-dialog-golden.png`), on the checked choice's dot in Spare sen (measured, not captured, the drive blurs focus before that capture) and on Splits after the sheet closes by a tap on Close (`webkit-390x844-m10-after-sheet-close-strip.png`, also seen in `webkit-390x844-s01-save-warning.png`). Chromium draws none of the three after a press. The sheet itself matches `:focus-visible` in WebKit but draws nothing, its outline is none | Neither an agent's change nor the owner's mid-flight change. WebKit leaves focus on the page after a press on a button (R59), so the app's focus by script counts as keyboard-like. The fidelity finder judged it allowed difference 10, since the golden's own `autofocus` gives the ring in WebKit too (`docs/modules/split-app/findings/fidelity.md`, QA-S5-4). The ledger names only the ring on Splits (S7 rows 39, 42, 50). The ring on Cancel is in the findings file only, and the ring in Spare sen is in no record | Engine difference, recorded in part, for the owner |
| D2 | `README.md` header | The lockup's alternative text and the 1.0 lockup say "Split", the badges and the showcase image are 1.0's, and the flow chart describes the 1.0 design round, where the brainstorm delta says the READMEs use the full name. The Versions row names Danial's Splity Tab, and the caption says the image, logo and badges change at the seal | Orchestrator ruling, kept at 1.0 until the seal from sealed captures, as in Streaks (STATE Notes, ledger S7 row 52, CS-7) | ORCH, reversible |

Observations (no requirement broken, the owner decides).

| # | Where | What | Cause |
|---|---|---|---|
| O1 | A price field at 360 x 780, both engines | Holding 99999.99 its text is 91 to 92 px in a 76 px box, so it shows "99999.9" until focused (`*-360x780-w03-max-sheet.png`, the field behind the sheet). R60 promises "964.50" whole, which holds, and the brainstorm's promise is the splits table, which fits. Not measured at 390 | The golden's field width (design), not an agent's change. Any change is the design phase's |
| O2 | Right after Escape on P1 or the sheet | The interim states in the information above, for a screen reader on the iPhone | The browser's close steps run before the `close` event (R59 (2)) |

Behaviour beyond the brainstorm's words, each ruled and working (not deviations).

| Where | What | Who ruled |
|---|---|---|
| Every control that moves the layout under the pointer | The second press of a double click, a double tap (500 ms, 22 px) or a held key does nothing. Dismiss note joined in A23 | USER, H-04 "Time + place". USER, S3. ORCH, A23 under the owner's word on minor calls (2026-10-16 00:19) |
| A phone, Tab | A focused control is scrolled clear of the strip | USER, H-08 |
| Names | Control, line separator and bidi characters are removed at the field and when a draft is read, item names too | USER, H-10 option 1. ORCH, PD-28 for item names |
| A new blank item | The amber marker until someone is tapped | USER, H-06 |
| A copy whose answer arrives after a change | No status shows | USER, H-07 |
| Pick again | At most 64 draws, then nothing changes | USER, CG-P3 |
| One person in By item | The chosen person takes every spare sen of the bill, only people on an item can be chosen | USER, CG-P2 |
| The copied summary | A thousands comma from RM 1,000, as on screen | USER, CG-P1 |
| The save warning | Shows at boot when the browser refuses storage outright | USER, CG-1 |
| A bad or blank rate, a bad price | The receipt blocks with one of four messages, a blank rate never counts as 0 | ORCH, told to the owner (`docs/design/RULINGS-v1.1.0.md`) |
| Even split above six people | Two columns on the desktop card | ORCH, PD-17 |

Accepted residuals a person could meet, for the UAT script. A name input that brings in only removed characters saves the same text and clears "Summary copied" (CS-1, ORCH, to v1.2.0). An IME composition holding a bidi character is cut short (SEC-R1, ORCH, to v1.2.0). No home-screen icon (off-scope row 7, DEFERRED). Safari 26 shows the tab icon in one colour in both themes (S6 row 2). Private browsing and Safari's 7-day clean-up lose the bill with no warning (S4 row 2, the README says so). Two deliberate taps on one spot within 500 ms count once (H-04).

## Follow-ups

1. D1 to the owner in UAT on his iPhone. If he keeps it, the planner adds the Cancel and Spare sen rings to the engine differences beside QA-S5-4 and the ledger gets the entry. If he wants no ring after a tap, that changes the focus rule or the focus call (the fidelity finder measured that `focus({ focusVisible: false })` draws none in WebKit), so it goes to the design or plan phase, never a patch from here.
2. O1 to the owner. If he wants the full price shown, it is a design change to the field widths, through the design phase.
3. Ledger close for the orchestrator. The At a glance table reads OPEN for S1 to S9 and no scope carries SHIPPED or a Proof line. S2, S3, S6, S8 and S9 have no execute or close rows in their own tables (their work sits under S1, S5 and S7 rows), and S8 row 1 still reads Open though H-01 ruled the name. `sdlc:uat` derives its cases from the scope sections, so each needs its close. Off-scope rows run 22, 21, 20, 19, 18, 17 out of order.
4. Staleness check, said out loud. The ledger's newest entry is S7 row 53 (2026-10-16 04:25), the newest handoff is `docs/progress/handoff/handoff-2026-10-16-execute-split-a23.md` (03:13). The ledger is newer, so it is current until this review's close, which the orchestrator writes from this return.
5. D2 at the seal and publish prep, with off-scope row 20 (long tracked paths).
6. Items already deferred to the v1.2.0 plan stay there (CS-1, SEC-R1, RG-CR-3 to RG-CR-5, CS-2 to CS-6, the older prose colons, the two qa.md notes of row 48). CS-8 and the aborted capture of row 50 go to publish prep.

## Candidate UAT cases

iPhone first, since headless WebKit on Windows is the engine but not the device.

| # | Case | What correct looks like |
|---|---|---|
| U1 | iPhone, VoiceOver on. A price field with a valid price, then type 13.505 and move on (H-09) | VoiceOver reads the field with the hint "Enter an amount like 12.50" before the error shows, and reads it as invalid once it shows. He keeps it or asks for a change |
| U2 | iPhone. Tap Splits | The sheet rises, and the page shows faintly through the glass as in the goldens (QA-S5-4). Readable or not |
| U3 | iPhone. Tap Close on the sheet, then New bill, then the spare sen chip | Note whether a ring shows on Splits, on Cancel and on the checked choice (D1). Keep it or ask for a change |
| U4 | iPhone, VoiceOver on. New bill then Cancel, the sheet's Close, and Spare sen's Close (ledger S7 row 33, M1's interim focus, and O2) | Focus lands on New bill, Splits or the chip, and VoiceOver says nothing odd in between |
| U5 | iPhone. Double tap Add person, a Remove, Splits and Dismiss note (H-04, A23) | Each acts once. The sheet opens and nothing is copied. People stays open after the note goes |
| U6 | iPhone. A long by-item bill, move through the fields with the keyboard's next arrows (H-08) | The field being typed in is never hidden under the strip |
| U7 | iPhone. Settings, Safari, block all cookies, open the app and change something, then allow cookies and change something again (S4) | The warning shows with the exact words and cannot be dismissed, then goes |
| U8 | iPhone. Private Browsing, enter a bill, close the tab, open again | The bill is gone and no warning showed (known limit) |
| U9 | iPhone. Look at the tab icon in light and dark mode (S6) | The receipt mark. One colour in both is Safari's known bug |
| U10 | iPhone. By item, an item at RM 964.50, then a price of 99999.99 (S2, O1) | Nothing scrolls sideways and every split fits. The 99999.99 field shows "99999.9" until tapped. Can he live with it |
| U11 | Any device. A bill with spare sen, choose Top of the list, One person, At random, Pick again, reload, Copy summary (S1) | The splits change as chosen and always add up, a reload keeps the draw, the copied text matches the screen |
| U12 | Any device. By item with one person on no item, open the spare sen choice, One person (CG-P2) | The picker lists only people on an item |
| U13 | Desktop. Hold Enter on the only item's Remove (S3) | The item goes and no blank item appears |
| U14 | Desktop at 1280 x 800. The key screen with four items, then the spare sen chip | The page does not scroll, the items scroll in their frame, the popup sits beside the card |
| U15 | Any device. Paste a name copied from a right-to-left chat message, if the script can give him one (H-10) | The People line still reads left to right and the copied summary matches |

## Out-of-project artifacts

No out-of-project artifacts logged. `docs/progress/out-of-project-artifacts.md` does not exist. One stray is named in the run's records but was never logged there, `{temp}\ref_a13` (0 bytes, 2026-10-15 14:13), the orchestrator's `touch ... 2>/dev/null` slip recorded in `docs/progress/STATE-LOG.md` (2026-10-15 14:29). It still exists. This review did not touch it. It needs a ledger entry and the owner's manual delete.

## Process

- Servers, each a `python -m http.server` child of the drive script on a free `127.0.0.1` port, stopped by PID with the port checked refusing. Final runs Chromium PID 26096 port 8678, WebKit PID 20884 port 8680. Trial runs PIDs 20928 (port 6176), 22892 (24956), 5912 (25184) and 25204 (25186), each stopped the same way (the `run-log-*.txt` of each trial folder).
- Every wait bounded (5 s per action, 2 s for a dialog's close, 4 s for animations to settle, `timeout 580` on each run).
- Closing sweep by name (python, node, chrome, webkit, playwright, bash, sh) and command line (`http.server`, `playwright`, `review_v110`, `sdlc-showcase`) and by port found only the orchestrator's Streaks server, PID 11048 on 8741, left alone.
- The drive script wrote only into this folder, by relative paths from the project root, and every path above was listed on disk. Nothing under `docs/design/`, `src/`, `tests/` or `index.html` was written. Nothing was committed.

## Files in this folder

`review.md`, `review_v110.py`, `results-chromium.json`, `results-webkit.json`, `run-log-chromium.txt`, `run-log-webkit.txt`, and 71 captures, 44 from Chromium and 27 from WebKit (`<engine>-<size>-<flow><nn>-<step>.png`, a `-golden` suffix for the golden at the same state, and `<engine>-16x16-tab-icon-dark.png` and `-light.png`). The folders `trial-1/` to `trial-4/` hold the four trial runs (137 captures with their results and logs).
