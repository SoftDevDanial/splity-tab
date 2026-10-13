# Module: split-app

> Build contract. Read by the builder. Build ONLY what is here.
> Stack is LOCKED to the project stack (static page, vanilla JavaScript ES modules, plain CSS, zero dependencies, `localStorage` only).
> Depends on `split-core` through its exported functions only (see Contracts).
> Nature is FE. This is the **live-composition module**. It owns the shipped entry point `index.html`, the whole UI, the draft in `localStorage`, the save warning, the clipboard, the dialogs, the fidelity gate and the **cold-boot live-e2e gate**.
> Sources are `docs/brainstorm/brainstorm.md` (with its v1.1.0 delta), `docs/design/RULINGS.md`, `docs/design/RULINGS-v1.1.0.md`, `docs/design-explore/v1.1.0/final/SELF-CRITIQUE.md` (the approved copy list and interaction rules 1 to 13), `docs/design/system.md`, `docs/design/system.css`, the fifteen goldens in `docs/design/` with their `.md` files, `docs/design/LINKS.json`, `docs/v1.1.0/CHANGE-LEDGER.md` (scopes S1 to S9 and the clarify rulings in S4, S5 and S6) and the research in `docs/brainstorm/research/`.

## v1.1.0 delta
Written 2026-10-13 by the planner (solutions architect role). The 1.0 text of every changed requirement is in git tag `v1.0.0`. Scopes are the ones in `docs/v1.1.0/CHANGE-LEDGER.md`. Clarify items CG-P1 to CG-P7 and planner decisions PD-17 to PD-23 are in `docs/modules/ROADMAP.md`, section v1.1.0. A requirement written to a recommended answer names its item, so a different ruling changes that one line.

| R# | Status | Scope | What changed |
|---|---|---|---|
| R1 | Changed | S6, S7, S8 | Head order and content (color scheme, viewport-fit, title, tab icon link). `src/system.css` is again a byte copy of the golden CSS |
| R2 | Changed | S7, S8 | Cold boot is `bill-empty` with People open on a phone |
| R3 | Changed | S7 | DOM walk against the fifteen goldens at the 40 fidelity pairs, new allowed differences |
| R4 | Changed | S7 | Person rows in `ul.people#peopleList`, X icon through the sprite |
| R5 | Changed | S7 | A name also updates the receipt rows (card and sheet), the People summary and the picker pills |
| R6 | Changed | S7 | Add person in the heading row, the v1.1.0 disabled look |
| R7 | Changed | S7 | The v1.1.0 disabled look for Remove at two people |
| R8 | Changed | S7 | The Split block and switch markup, no legend |
| R9 | Changed | S7 | The Subtotal block markup, error paragraph always present |
| R10 | Changed | S7 | Error markup (`is-bad`, `hidden`, `aria-invalid`), rate `aria-describedby` order (rule 13) |
| R11 | Changed | S7 | Price name `{itemLabel} price in RM`, placeholder `0.00`, `aria-describedby="ie{j}"` |
| R12 | Changed | S7 | Add item in the heading row |
| R13 | Changed | S7 | Toggle group and toggle markup |
| R14 | Changed | S7 | Price error markup |
| R15 | Changed | S7 | Charges markup and copy |
| R16 | Changed | S7 | Quiet card, sheet and strip |
| R17 | Changed | S7 | Blocked receipt and strip, the four messages with "splits" |
| R18 | Changed | S7 | Unassigned receipt and strip, the amber item marker |
| R19 | Changed | S7 | Total and bill lines markup |
| R20 | Changed | S1, S7 | Even splits list, the proof row, two columns above six people (PD-17) |
| R21 | Changed | S1, S7 | By-item working under each split |
| R22 | Changed | S7 | Copy from the card, the sheet or the strip, status with icon |
| R23 | Changed | S7 | Failure status `status is-fail` with icon |
| R24 | Changed | S7 | Status on every status line, cleared by the next change (rule 10) |
| R25 | Changed | S1, S4 | Envelope version 2, a failed save shows the warning |
| R26 | Changed | S1, S7 | Restores the spare choice, sections fold per R48 |
| R27 | Changed | S7 | Note in the top bar, focus to New bill on dismiss (rule 12) |
| R28 | Changed | S4 | Keeps working in memory, the message part moves to R46 and R47 |
| R29 | Changed | S7 | M1 markup, danger and ghost buttons |
| R31 | Changed | S7 | Start new bill gives `bill-empty` with People open on a phone, resets the open state |
| R32 | Changed | S7 | Tab order per golden DOM on phone and desktop, the one focus ring |
| R35 | Changed | S2, S7 | No sideways overflow in every golden state at 360, 390 and 1280 |
| R36 | Changed | S7 | The motion list of `system.md` |
| R37 | Changed | S7 | Same sinks, icon counts by the new classes |
| R38 | Changed | S6, S7 | CSP unchanged, a narrow CSSOM allowance, the icon loads under the policy |
| R39 | Changed | S6 | One more namespace exemption (the root of `src/icon.svg`), `/src/icon.svg` allowed |
| R40 | Changed | S5, S7 | Fidelity at 40 pairs, Chromium only |
| R41 | Changed | S5, S7 | Live gate in Chromium and WebKit, the v1.1.0 headline flow |
| R42 | Changed | S7 | Wording only, "splits list" for "shares table" |
| R43 | New | S8 | The name in the title and the top bar |
| R44 | New | S6 | The header mark and the icon sprite |
| R45 | New | S6 | The tab icon file `src/icon.svg` |
| R46 | New | S4 | The save warning shows |
| R47 | New | S4 | The save warning clears |
| R48 | New | S7 | People and Charges fold below 1024 px |
| R49 | New | S7 | The strip below 1024 px |
| R50 | New | S7 | The Splits sheet |
| R51 | New | S1, S7 | The spare sen line and chip |
| R52 | New | S1, S7 | P1, the spare sen choice |
| R53 | New | S1 | One person and its picker |
| R54 | New | S1 | At random and Pick again |
| R55 | New | S7 | The desktop layout |
| R56 | New | S7 | The item frame |
| R57 | New | S3 | A held Enter adds no blank item |
| R58 | New | S5 | The engine switch for the browser suite and the live gate |
| R59 | New | S5 | Behaviour stated per engine |
| R60 | New | S2 | Large bills fit 360 px |
| R61 | New | S1 | Draft version 2 |

No requirement is retired. R30, R33 and R34 are unchanged. Counts are new 19 (R43 to R61), changed 39, unchanged 3, retired 0, total 61.

## Module roadmap
- **Build order.** Second, after `split-core`, apart from one interleave. Task A1 (draft version 2) lands right after core task C2, because from C2 on a `Bill` carries `spare` and the 1.0 decoder drops unknown keys, so a reload would hand core a bill without `spare`. Task A0 (the engine switch and the WebKit baseline) comes before everything else. The full order is in `docs/modules/ROADMAP.md`, section v1.1.0.
- **Done when.** Functional QA is green against the running app in Chromium and in WebKit (only listed `chromium_only` skips), the fidelity gate passes all 40 pairs in Chromium, every row of the FE element checklist passes, the cold-boot live gate has its evidence artifact in both engines, and the code-review and security finders pass. A WebKit failure in the suite or the live gate blocks the seal (ledger S5 row 2).
- **Phase skills.** Every UI task (A2 and later) loads the design row of `docs/phase-skills.md` (`taste-skill`, `frontend-design`) before it writes anything, and its build record says what transferred. Plan has none.
- **Clarify gate.** CG-P1 to CG-P7 are open for the owner (clarify gate part 2). Each requirement below is written to the recommended answer.

## Invariants & assumptions
- `split-core` is the only place where money is parsed, computed, allocated or formatted, the only place that edits a `Bill`, and the only place that draws a spare sen order. This module never does arithmetic on money, never edits `people`, `items` or `spare` itself, and passes `Math.random` into the two core functions that draw (PD-19).
- The goldens in `docs/design/` are the truth for markup, classes, copy and look. `src/system.css` is a byte copy of `docs/design/system.css` (equal SHA-256, `eaa6a3b2753abf7848afb81b848aa411fbf3fa16b87b961a6170e042e1bdb7b0` at planning time). No CSS rule is added, removed or changed. [Changed 2026-10-13, v1.1.0, S7. 1.0's one trailing rule of RC-5 is gone, because the v1.1.0 golden CSS already holds `[hidden] { display: none !important; }`.]
- The page is served as static files from any folder (the target is a GitHub Pages project path such as `/split/`), so every URL in the page is relative. The public deployment serves only `index.html` and `src/`, plus a `.nojekyll` file, made by the orchestrator at release (`CLAUDE.md`, Publish, security SEC-02 of 1.0).
- [Changed 2026-10-13, v1.1.0, S5.] The browser suite and the cold-boot live gate run headless in Chromium and in WebKit through Python Playwright, one engine per run, chosen by `--engine` (R58). The fidelity gate runs in Chromium only, because the goldens are Chromium renders and the sdlc harness is Chromium only (ledger S5 row 2). Playwright's WebKit on Windows is Safari's engine, not Safari on an iPhone, so touch gestures, the on-screen keyboard and Safari's storage clean-up stay with the owner's UAT. Behaviour that differs by engine is stated per engine (R59). The draft name length rule D8 is the one product rule written for WebKit.
- Native `<dialog>` with `showModal()` is available in the target browsers (Chromium, WebKit and Gecko since 2022).
- `navigator.clipboard.writeText` exists only in secure contexts. `http://127.0.0.1` and GitHub Pages (https) are secure contexts in Chromium. WebKit's answer on `http://127.0.0.1` is probed in task A0 (R59).
- One theme. The design is dark (`<meta name="color-scheme" content="dark">`, `system.md`). There is no light theme and no theme switcher.

## Requirements

### Shell and boot
- **R1. Entry point.** (v1.1.0 changed) `index.html` sits at the project root with `<html lang="en">` and holds, in this order inside `<head>`, `<meta charset="utf-8">`, `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">`, `<meta name="color-scheme" content="dark">`, the CSP meta of R38, `<title>Danial's Splity Tab</title>`, `<link rel="icon" type="image/svg+xml" href="src/icon.svg">`, `<link rel="stylesheet" href="src/system.css">` and `<script type="module" src="src/main.js"></script>`. `src/system.css` is byte-identical to `docs/design/system.css` (equal SHA-256). Every URL in `index.html` and every `import` in `src/` is relative (no leading `/`, no scheme). Loading the page raises no console error and no page error in either engine. [Changed 2026-10-13, v1.1.0, S6, S7, S8. The head follows the goldens' head, with the CSP meta and linked files in place of the inline styles (allowed difference 3). The icon link sits after the CSP meta, because a meta policy does not cover what comes before it (research B6).]
- **R2. Cold boot is a new bill, never a seed.** (v1.1.0 changed) With empty storage the first render is the `bill-empty` state. Two people with the field values `Person 1` and `Person 2`, both Remove buttons disabled, Even checked, an empty Subtotal with no error, Service charge `10`, SST `6`. Below 1024 px People is open and Charges folded (R48, CG-P4). The receipt shows "Total" and "Enter the subtotal to see the splits." (R17), and the strip shows the same message with Copy summary disabled (R49). Nothing is written to storage until the first change. `index.html` and every file under `src/` contain none of the golden sample names as whole words (Aisyah, Ben, Chen, Devi, Farid, Grace, Hafiz, Indra, Jia Hui, Kumar, Lina, Mei Ling, Nasi lemak, Char kuey teow, Mee goreng, Satay). There is no demo mode, no fixture, no URL parameter and no global hook (`window.__*`) that fills or exposes the bill.
- **R3. Markup mirrors the goldens.** (v1.1.0 changed) After every render the DOM follows the DOM contract below. At each of the 40 state and width pairs of the fidelity gate (R40), a DOM walk compares the page's body with the golden's body and finds equal tags, nesting, class lists, ids, own text, and these attributes. `role`, every `aria-*`, `type`, `name`, `value` of a radio, `for`, `tabindex`, `data-open`, `disabled`, `maxlength`, `inputmode`, `autocomplete`, `placeholder`, the `href` of every `use`, the `checked` state, and an input's `value` property against the golden's `value` attribute. The walk skips every element whose computed `display` is `none` (with everything inside it) on both sides, and a closed dialog. Only the allowed differences listed in the contracts exist.

### The name and the logo (S6, S8)
- **R43. The name.** (v1.1.0 new) The document title is `Danial's Splity Tab`. The top bar's `div.brand` holds the mark (R44) and then `h1.word` with the text `Splity Tab`. No other text in the page names the app. [Brainstorm v1.1.0, Name (USER).]
- **R44. The mark and the sprite.** (v1.1.0 new) The first child of `body` is the golden's `svg.sprite` block (`aria-hidden="true" focusable="false"`, the `seal-grad` gradient and the ten symbols `i-x`, `i-plus`, `i-copy`, `i-check`, `i-caret`, `i-shuffle`, `i-warning`, `i-warning-circle`, `i-mark`, `i-seal-check`), byte for byte as in `bill-items.html`, written in `index.html`. The header mark is the golden's inline `<svg class="mark" viewBox="0 0 28 28" aria-hidden="true" focusable="false">` with one `path` whose `fill-rule` and `d` are byte-equal to the golden's, written in `index.html`. Neither carries an `xmlns` attribute. The empty receipt (R17) uses `#i-mark` through `<use>`. Every other icon in the page is `<svg class="ic" aria-hidden="true" focusable="false"><use href="#i-{name}"/></svg>` (the seal is `svg.seal`), built at run time with `createElementNS` (R37). [Ledger S6 row 1, S7 row 13 (the mark S12, the empty state uses `i-mark` by the owner's ruling).]
- **R45. The tab icon.** (v1.1.0 new) `src/icon.svg` holds exactly the bytes of `urllib.parse.unquote` of the golden icon link's `href` after its first comma (470 bytes, SHA-256 `7b5e4176a6182d23f06073ff181f01bbb73e2ac562f78d58a930ffb80fe7fef2` at planning time, one identical `href` in all fifteen goldens). It parses as XML with the root `{http://www.w3.org/2000/svg}svg`, `viewBox="0 0 16 16"`, a default fill `#A3AAFF` and `#1E2140` under `prefers-color-scheme: light`. `index.html` links it as R1 says. The CSP is unchanged (R38). Safari 26 showing one icon colour in both themes is accepted as Safari's bug and checked in UAT. There is no home-screen icon and no manifest. `docs/brand/favicon.svg` is never copied (it is the 1.0 mark on a tile). [Ledger S6 row 2, USER "Yes, a file" and "Header and tab only". Research B6 option B.]

### People (C1)
- **R4. Person rows.** (v1.1.0 changed) `ul.people#peopleList[aria-labelledby=peopleH]` holds one `li.field.person` per person in list order. Its input has `type="text"`, `maxlength="20"` (`LIMITS.personNameMax`), `autocomplete="off"`, `aria-label="Person {i} name"` and `placeholder="Person {i}"` ({i} is the 1-based position), and its `value` is the stored name. Its Remove button is `button.icon-btn` with `aria-label="Remove {personLabel}"` and the X icon. A blank name shows the placeholder in the field and `Person {i}` everywhere else (ruling 4).
- **R5. Names update live.** (v1.1.0 changed) On every `input` event in a person's name field, `setPersonName` is applied and, in the same render, the new label shows on that person's toggle in every item, in their row of the splits list (card, and sheet when open), in their Remove button's accessible name, in the People summary (R48) and on their pill in P1 when it is open (R53). The next Copy summary uses it. The same holds for item names, which update their Remove button (`Remove {itemLabel}`), their price field's name (`{itemLabel} price in RM`) and their group name (`Who had {itemLabel}`).
- **R6. Add person.** (v1.1.0 changed) `button.btn.btn-ghost#addPerson` (plus icon, "Add person") in the People heading row appends a person through `addPerson`. The new field is **empty** and shows the placeholder `Person {i}` (CG-1 of 1.0). At 12 people the button has the `disabled` attribute and the system's disabled look (faint label and icon, `--l5` border, no fill, `not-allowed` cursor), and Tab skips it. The repeat-press guard of 1.0 stays in force. The click arms `swallowRepeatClicks` before it adds, so a double click, a triple click or a double tap adds one person, focus ends on the new name (R34) and the id counter moves once (RG-CR-01).
- **R7. Remove person.** (v1.1.0 changed) A Remove button calls `removePerson`, which also takes that person off every item (and, by core R12, off the drawn order, and resets a One person choice that named them). At 2 people both Remove buttons have the `disabled` attribute and the disabled look (faint X, no hover), and Tab skips them. The 1.0 guard rules stay in force. A Remove click arms `swallowRepeatClicks` (`src/ui/dom.js`), which cancels the repeat `mousedown` and `click` (click count above 1) at the document and ends at the first press that is not a repeat. A Remove also ignores a repeat press itself (`isRepeatClick`, click count above 1) whether or not the guard is armed (RG-CR-08). The clicks that arm the guard are every Remove, Add person, Add item and every click that opens or closes a dialog (R29, R30, R50, R52). Dismiss note arms nothing (1.0 BUILD.md judgment call 18). The same holds for the Remove of an item (R12). [Sources SEC-01, I-1, RG-CR-01, RG-CR-08, full history in tag `v1.0.0`.]
- **R42. Duplicate names are allowed.** (v1.1.0 changed) Typing a name equal to another person's (exactly, after trimming, or differing only in letter case) is accepted. There is no error, no note, no merge and no warning, and the draft saves both people. Each row keeps its own toggles, splits row and Remove button. Two people called "Ben" give two `Remove Ben` buttons with the same accessible name, and each acts on its own row only. The splits list and the copied text hold one line per person, so "Ben" appears twice. [Changed 2026-10-13, v1.1.0, S7. Wording only, the receipt has a splits list, not a shares table.]

### Split and Subtotal (C2, C3)
- **R8. Split switch.** (v1.1.0 changed) `div.blk.split#splitBlk[role=group][aria-labelledby=splitH]` holds `h2.blk-h#splitH` "Split" and `div.mode-sw` with two radios, `#modeEven` (label "Even") and `#modeItem` (label "By item"), `name="mode"`, each followed by its `label[for]`. There is no legend. Clicking a label, or an arrow key on the focused radio, calls `setMode`. Even mode renders the Subtotal block (`#evenBlock`) and no Items block. By-item mode renders the Items block (`#itemsBlock`) and no Subtotal block. The block of the other mode is absent from the DOM. Both inputs survive any number of switches (the subtotal text, every item, every tap, the spare choice), including after a reload.
- **R9. Subtotal field.** (v1.1.0 changed) In even mode `div.blk#evenBlock` holds `label.blk-h.solo[for=evenSub]` "Subtotal", then `div.field.money.sub-field#evenField` with `span.unit[aria-hidden=true]` "RM" and `input#evenSub` (`type="text"`, `inputmode="decimal"`, `autocomplete="off"`, `placeholder="0.00"`, `aria-label="Subtotal in RM"`, `aria-describedby="evenErr"` at all times, `aria-invalid` "false" or "true"), then `p.err#evenErr` with the warning-circle icon and "Enter an amount like 12.50", which carries `hidden` while its error is not shown. Every `input` event calls `setSubtotalText` with the exact text. [The constant `aria-describedby` follows the golden, clarify item CG-P6.]
- **R10. When an inline error shows.** (v1.1.0 changed) The rule applies to the Subtotal, every item price, Service charge and SST. An error shows only for text that is not empty and fails its parser (`parseAmount`, `parseRate(_, 30)`, `parseRate(_, 20)`). An empty field never shows one (ruling 1). The timing is 1.0's (CG-3, RD-3). (a) The error appears when the field loses focus holding such text. (b) At boot, a restored field holding such text shows its error at once. (c) While the user types, a shown error disappears as soon as the text becomes valid or empty, and does not come back until the field next loses focus. (d) A field's error state survives a mode switch. When focus leaves because a pointer is pressed inside the page, the error is rendered once that press ends (`mousedown` to `mouseup`, `pointercancel` or a `keydown`, on the document in the capture phase), so the click on the control the press started on is kept. A blur from the keyboard renders at once. One shared helper (`onFieldLeave` in `src/ui/field-leave.js`) serves every field, and its top comment is the one home of the measurement. The markup per state follows the goldens. While an error shows, the field wrapper (`div.field`) carries class `is-bad`, the input has `aria-invalid="true"` and the error paragraph has no `hidden`. While none shows, the input has `aria-invalid="false"`, the wrapper has no `is-bad` and the paragraph carries `hidden`. The paragraph is always in the DOM. A rate names its error in `aria-describedby` only while it shows, hint first (`chargeHint`, then `chargeHint svcErr` or `chargeHint sstErr`, rule 13). The Subtotal and every price name their error paragraph at all times (`evenErr`, `ie{j}`), as the goldens do (CG-P6). The receipt is not affected by this timing. It always follows the current text (R16, R17).

### Items (C3)
- **R11. Item rows.** (v1.1.0 changed) In by-item mode `ul.frame#itemList[aria-labelledby=itemsH]` (inside the frame of R56) holds one `li.item` per item in list order. Its `div.item-row` holds the name field (`div.field` with an input of `type="text"`, `maxlength="40"` (`LIMITS.itemNameMax`), `autocomplete="off"`, `aria-label="Item {j} name"`, `placeholder="Item {j}"`), the price field (`div.field.money` with `span.unit[aria-hidden=true]` "RM" and an input of `type="text"`, `inputmode="decimal"`, `autocomplete="off"`, `placeholder="0.00"`, `aria-label="{itemLabel} price in RM"`, `aria-invalid` "false" or "true", `aria-describedby="ie{j}"`), the Remove button (`button.icon-btn`, `aria-label="Remove {itemLabel}"`, X icon) and `p.err#ie{j}` (R14). {j} is the 1-based position. `input` events call `setItemName` and `setItemPriceText` with the exact text.
- **R12. Add and remove items.** (v1.1.0 changed) `button.btn.btn-ghost#addItem` (plus icon, "Add item") in the Items heading row calls `addItem`. The new item has an empty name (placeholder `Item {j}`), an empty price and nobody tapped. At 50 items the button has the `disabled` attribute and the disabled look of R6. Any item's Remove calls `removeItem` at any time. The Add item click arms `swallowRepeatClicks` like Add person (RG-CR-01). Focus moves as R34 says.
- **R13. Who had it.** (v1.1.0 changed) After the item row, `div.taps[role=group][aria-label="Who had {itemLabel}"]` holds one `button.tap` per person in people-list order, each holding the check icon and then `<span>{personLabel}</span>`, with `aria-pressed` "true" when that person is in the item's `who`, otherwise "false". A click calls `toggleItemPerson`.
- **R14. Price error.** (v1.1.0 changed) `p.err#ie{j}` (warning-circle icon, "Enter an amount like 12.50") is the last child of its `div.item-row`, so it spans the name and price columns and is right aligned (`states.html`, S2 on a price). While it shows, the price wrapper is `div.field.money.is-bad` (R10).

### Charges (C4)
- **R15. Charges block.** (v1.1.0 changed) The Charges section body (R48) holds `h2.blk-h.solo#chargesH` "Charges" and `div.charges` with two cells and the hint. Each cell holds `label.lbl[for]`, a `div.field.pct` with the input and `span.unit[aria-hidden=true]` "%", and its error paragraph. Service charge is `label.lbl[for=svc]` "Service charge", `input#svc`, `p.err#svcErr` "Enter a rate from 0 to 30". SST is `label.lbl[for=sst]` "SST", `input#sst`, `p.err#sstErr` "Enter a rate from 0 to 20" (ruling 2). Each error paragraph starts with the warning-circle icon. Both inputs have `type="text"`, `inputmode="decimal"`, `autocomplete="off"`, `aria-invalid` and `aria-describedby` as R10 says, and their values are `serviceText` and `sstText` (`10` and `6` on a new bill). `p.hint#chargeHint` reads "Set a charge to 0 if your bill already includes it.". There is no hidden " in percent" ending. `input` events call `setServiceText` and `setSstText`.

### The receipt (C2, C3, C5, RULINGS 3, RULINGS-v1.1.0 rows a to e)
- **R16. Live, quiet receipt.** (v1.1.0 changed) The card, the sheet (when open) and the strip show `computeResult(bill)` for the current bill after every change, with no submit button. None of them carries `aria-live` or a live-region role, apart from the `p.status[role=status]` paragraphs inside them (R24). The only other live regions on the page are the notes in `#notes` (R27, R46).
- **R17. Blocked.** (v1.1.0 changed) For a `blocked` result the receipt (card, and sheet when open) holds `div.r-total` with only `span.r-label` "Total", then `div.r-empty` with the `#i-mark` icon and `<p>{message}</p>`. There are no bill lines, no splits, no spare line, no Copy summary and no status paragraph in the receipt. The strip shows `p.s-msg#stripMsg` with the message and no icon, and its Copy summary is disabled (R49). The message by reason is `rates` "Check the charges to see the splits.", `subtotal` "Enter the subtotal to see the splits.", `no-prices` "Add each item and tap who had it to see the splits.", `prices` "Give every item a price to see the splits.". [Changed 2026-10-13, v1.1.0, S7. `RULINGS-v1.1.0.md` rows a to d, the rename "shares" to "splits", and core R18 (c) as `no-prices`.]
- **R18. Items still need a person.** (v1.1.0 changed) For an `unassigned` result the receipt holds the Total and the bill lines (R19) and the dashed rule, then `div.r-msg` with the warning-circle icon and `<p>{message}</p>`, and nothing after it (no splits, proof, spare line, Copy summary or status). The strip shows `p.s-msg#stripMsg` holding the warning-circle icon and the same message, and its Copy summary is disabled. The message is "1 item still needs a person. Tap who had it to see the splits." for a count of 1, and "{count} items still need a person. Tap who had each one to see the splits." for 2 or more. Every item with an empty `who` carries class `needs` on its `li.item` (the amber bar), and no other item does. [Changed 2026-10-13, v1.1.0, S7. `bill-unassigned.html` replaces 1.0's "no error styling on the items".]
- **R19. Total and bill lines.** (v1.1.0 changed) For `unassigned`, `even` and `item` results the receipt starts with `div.r-total` holding `span.r-label` "Total" and `p.r-amount` (`#rTotal` on the card) with `<span class="cur">RM </span>` and `formatAmount(total)`. Then `dl.r-lines` with three `div` rows, `dt` "Subtotal" with `dd` `formatMoney(subtotal)`, `dt` "Service {formatRate(serviceBp)}" with `formatMoney(service)`, `dt` "SST {formatRate(sstBp)}" with `formatMoney(sst)`. There is no working line. Rates of 0 still show (`Service 0%`, `RM 0.00`). Then `div.r-rule[aria-hidden=true]`.
- **R20. Splits, even mode.** (v1.1.0 changed) For an `even` result, after the rule comes `div.r-head` with `h2` "Splits" (`#splitsH` on the card, `#sheetSplitsH` in the sheet), then `ul.r-splits` (`#splits` on the card, `aria-labelledby` the heading's id) with one `li` per row in list order, `span.nm` with the name and `span.amt` with `formatMoney(share)`. Then `div.r-check` with the seal icon, `span.lbl-proof` "Adds up to" and `span.amt` (`#addsUp` on the card) with `formatMoney(check.share)`. Then the spare line (R51), `button.btn.btn-primary.btn-block.r-copy` (`#copyBtn` on the card) with the copy icon and "Copy summary", and `p.status[role=status]` (`#cardStatus` on the card). With more than six people the list is `ul.r-splits.many` and carries the custom property `--rows` equal to ceil(people / 2), set through the CSSOM (R38). The CSS lays it out in two columns from 1024 px (PD-17, `bill-twelve.html` shows twelve as six rows). With the S2 bill and Top of the list the splits are RM 38.87, RM 38.87, RM 38.86 and the proof RM 116.60.
- **R21. Splits, by item.** (v1.1.0 changed) For an `item` result the receipt is R20's with three additions. `div.r-head` also holds `<span aria-hidden="true">items + charges</span>` after the heading. Each `li` also holds `span.wk` with `<span class="sr">Items </span>{formatAmount(items)} + <span class="sr">charges </span>{formatAmount(charges)}`. `div.r-check` also holds `span.wk` with `{formatAmount(check.items)} + {formatAmount(check.charges)}`. People with nothing tapped are listed with RM 0.00 and `0.00 + 0.00`. The list never takes `many` in by-item mode. With the S1 bill and Top of the list the rows are Aisyah RM 29.04 (24.90 + 4.14), Ben RM 15.74 (13.50 + 2.24), Chen RM 24.48 (21.00 + 3.48) and the proof RM 69.26 (59.40 + 9.86).

### Copy summary (C6)
- **R22. Copy works.** (v1.1.0 changed) A click on Copy summary on the card (`#copyBtn`), in the sheet or on the strip (`#stripCopy`) calls `navigator.clipboard.writeText(summaryText(computeResult(bill)))`. Every Copy summary is disabled or absent unless the result is `even` or `item`. When the promise resolves, the status reads "Summary copied" with the check icon before the text, and the paragraph's class list is `status`. The text is core R24's six lines with the splits as the spare choice left them, so it matches the screen. A bill from RM 1,000 prints thousands commas (CG-P1, core R24).
- **R23. Copy fails politely.** (v1.1.0 changed) When `navigator.clipboard` or `writeText` is missing, or the promise rejects, the status reads "Could not copy. Your browser blocked the clipboard." with the warning-circle icon before the text, and the class list is `status is-fail`. No exception escapes and nothing else changes. There is no fallback copy method.
- **R24. Status lifecycle.** (v1.1.0 changed) The status is one value (none, copied or failed) shown in every status paragraph present, `#cardStatus`, the sheet's `p.status` and `#stripStatus`. Each paragraph is empty (and so not displayed, `.status:empty`) until a copy is tried. Each attempt replaces the previous text and class. The next change to the bill clears it (rule 10). A focus change, a blur, a section fold, opening or closing a dialog and a resize are not changes and leave it. It is not saved in the draft. [Changed 2026-10-13, v1.1.0, S7. Interaction rule 10 replaces 1.0's PD-5.]

### Draft (C7, C10)
- **R25. Save after every change.** (v1.1.0 changed) After every change to the bill (each `input` event on any field, each click that changes the bill, each mode change, each spare choice, pick or Pick again that changes the bill, Start new bill), a save attempt writes `localStorage` key `split.draft` with `encodeDraft(bill)`, a JSON text whose parsed value deep-equals `{ "version": 2, "bill": <the Bill> }`. A commit that leaves the bill unchanged writes nothing. A failed attempt shows the save warning (R46). Nothing is saved on unload, and nothing is saved at cold boot.
- **R26. Restore on load.** (v1.1.0 changed) When the page loads with a readable draft (R61), the screen shows that bill exactly. Every name, the mode, the subtotal text, every item with its name, price text and taps, both rate texts and the spare choice (with its drawn order) are as they were, so the splits on screen equal the ones before the reload. Switching mode shows the other mode's input as it was. Inline errors follow R10 (b). Sections open or fold by R48.
- **R27. Unreadable draft.** (v1.1.0 changed) When `split.draft` exists but the decoder rejects it, the app starts `newBill()`, saves it at once (so a reload does not show the note again), and shows the note in `div.notes#notes` in the top bar. `div.note[role=status]` holds the warning-circle icon, `<p>Your saved bill could not be read, so a new one was started.</p>` and `button.icon-btn#dismissNote` with `aria-label="Dismiss note"` and the X icon. Below 1024 px People opens (the bill is new, R48, ruling 1 of S6). Dismiss note removes the note from the DOM and moves focus to New bill (rule 12). Start new bill does not show, hide or move the note. When that reset save fails, the save warning shows as well (R46).
- **R28. Storage unavailable.** (v1.1.0 changed) When reading `window.localStorage` throws or gives null, `getItem` throws, or `setItem` throws (for example a quota or security error), the app starts or continues with the bill in memory and works normally for the rest of the session. No exception reaches the console. What the user is told is R46 and R47. [Changed 2026-10-13, v1.1.0, S4. 1.0's "shows no message" is replaced by the save warning.]
- **R61. Draft version 2.** (v1.1.0 new) `encodeDraft` always writes version 2. The decoder accepts version 1 and version 2. D3 becomes "`version` is exactly the number 1 or the number 2". D13 (version 2 only) requires `bill.spare` to be a plain object that is exactly one of `{ rule: "top" }`, `{ rule: "one", personId }` where `personId` is the id of a person in the bill, or `{ rule: "random", order }` where `order` is an array holding every person id of the bill exactly once. Other keys inside `spare` are dropped, and `spare` is built as a new object from known fields only (D12). D14 decodes a version 1 draft with `spare` set to `{ rule: "top" }`, and ignores any `spare` key it carries. A One person choice whose person is on no item is readable (core R32 falls back and keeps it). [Ledger S1, core R27.]

### The save warning (C10, ledger S4)
- **R46. The save warning shows.** (v1.1.0 new) A save attempt is every write of `split.draft` (R25, the reset save of R27, Start new bill). It fails when the storage object cannot be obtained (the `window.localStorage` getter throws or gives null) or `setItem` throws, and succeeds when `setItem` returns. After a failed attempt the warning is in `div.notes#notes`. `div.note.is-warn[role=status]` holds the `#i-warning` icon and `<p>This bill is not being saved on this device. It will be lost when you close this tab.</p>`, and no dismiss control. At boot, when the boot read fails (the getter throws or gives null, or `getItem` throws), the warning is in the first render, before any change (USER, research CG-1, ledger S4 row 2). A readable or empty store shows no warning at boot. When the warning and the unreadable note both show, the warning comes first in `#notes` (CG-P5). The DOM of the warning changes only when its state flips, so the live region is not touched on every keystroke (SW7). [Research A2, statements SW1 to SW3, SW5 and SW7.]
- **R47. The save warning clears.** (v1.1.0 new) The latest save attempt decides. After an attempt that succeeds the warning is removed, and the stored text then equals `encodeDraft` of the bill on screen (SW4). It cannot be dismissed. While the storage object could not be obtained, each later save attempt reads `window.localStorage` again, so the warning can clear without a reload (SW6). The app never reads an exception's name, message or code. There is no probe write, no read back and no timer. Private browsing and Safari's 7-day clean-up lose data with no failure the page can see. That limit is written in the README by the orchestrator (SW8, ledger S4 row 2), and nothing in the app detects it.

### Sections, strip, sheet and layout (S7)
- **R48. People and Charges fold below 1024 px.** (v1.1.0 new) People and Charges are each `div.blk.sec` with `data-open` "true" or "false", `h2.sec-h` holding `button.sec-btn` (`aria-expanded` equal to `data-open`, `aria-controls` the body id, `aria-labelledby` the `span.sec-name` id, `aria-describedby` the `span.sec-sum` id), then `div.sec-body` holding `div.sec-in` and the section's content. Below 1024 px the CSS shows the header row and hides a folded body. From 1024 px the header rows are not shown and both bodies show with their own `h2.blk-h` headings, whatever `data-open` says.
  1. **Open on load only.** At load, People is open when the loaded bill deep-equals `newBill()` (cold boot, an unreadable draft, or a reload of an untouched new bill, CG-P4), and Charges is open when a rate shows its error at load (R10 b). Every other section starts folded. After load the open state changes only by the header row (a click, Enter or Space toggles it) and by Start new bill (R31). Typing, an error, a mode switch or a resize never opens or folds a section. The open state is never saved.
  2. **The summary.** `span.sec-sum` holds `span.sec-txt`. It is hidden while open and keeps its place (CSS). The People text is the people's labels joined by ", " when all of them show whole in the row. Otherwise it is the first k labels joined by ", " and then " and {n - k} more", with k the largest count that shows whole, and "{n} people" when not even one label with its " and {n - 1} more" shows whole. The app measures it at every render of the row and whenever the row's width changes. At 390 x 844 the `bill-twelve` bill reads "Aisyah, Ben, Chen, Person 4 and 8 more" and at 360 x 780 "Aisyah, Ben, Chen and 9 more" (`bill-twelve.md`). The Charges text is "Service {formatRate(serviceBp)}, SST {formatRate(sstBp)}" when both rates pass their parsers. When a rate fails (empty or not valid, the rule of core R18 (a)), the button carries class `is-bad`, `span.sec-sum` holds the warning-circle icon before `span.sec-txt`, and the text is "Check service charge", "Check SST" or "Check both rates". It follows the current text on every input, not R10's error timing (`RULINGS-v1.1.0.md`, a blank rate shows the marker too). A Charges summary never shows a blank rate as 0.
  3. **Motion.** Opening reveals the body over 200 ms and folding is instant. The reveal is one Web Animations API animation on `div.sec-body` (height from 0 to its full height and opacity from 0 to 1), started only under `prefers-reduced-motion: no-preference`, and it writes no inline style (PD-22). The caret turn is the CSS transition of `system.css`. Under reduced motion both are instant.
- **R49. The strip.** (v1.1.0 new) Below 1024 px `div.strip.glass.dense#strip` is fixed at the bottom (CSS) and holds the foil and `div.strip-in`. The first row (`div.strip-top`) holds `div.strip-info#stripInfo` and then `p.status#stripStatus[role=status]`. For an `even` or `item` result `#stripInfo` holds `span.s-label` "Total" and `span.s-fig#stripTotal` with `<span class="cur">RM </span>` and `formatAmount(total)`. For `blocked` and `unassigned` results it holds `p.s-msg#stripMsg` as R17 and R18 say. The status sits beside the Total and takes its own line when it does not fit (CSS). The second row (`div.strip-acts`) holds `button.btn.btn-ghost#splitsBtn` ("Splits" then the caret with class `ic caret-up`, `aria-haspopup="dialog"`, `aria-controls="splitsDlg"`, `aria-expanded` "false" or "true", always enabled) and `button.btn.btn-primary#stripCopy` (copy icon, "Copy summary"), which has `disabled` unless the result is `even` or `item` and is never hidden (rule 5). The app sets the custom property `--strip-h` on the root element to the strip's measured height in px, through the CSSOM, at load and whenever the strip's size changes, so the page's bottom padding and `scroll-padding-bottom` clear it (measured in the goldens at 111, 108, 128 and 153 px). No control the user tabs to is left under the strip.
- **R50. The Splits sheet.** (v1.1.0 new) `dialog.sheet-dlg#splitsDlg[aria-label=Splits]` is empty while closed. A click on Splits fills it and opens it with `showModal()`. It then holds `div.glass.dense.sheet[tabindex=-1]` with the foil, `div.sheet-top` (`span.grab[aria-hidden=true]` and `button.icon-btn[aria-label=Close]` with the X icon) and `div.sheet-scroll#sheetScroll` holding `div.rbody` with the receipt. The receipt is made by the same renderer as the card's (one function, DRY) and carries no id but `sheetSplitsH` (PD-20). It updates live while the sheet is open. `#splitsBtn` has `aria-expanded="true"` while it is open. Focus moves to `div.sheet` on open (no ring). Escape, Close, and a click whose press and release both fall on its backdrop close it, `aria-expanded` returns to "false", the content is removed, and focus returns to Splits. A click that opens or closes it arms `swallowRepeatClicks` (PD-21). When the viewport reaches 1024 px while it is open, it closes and nothing moves focus (PD-18). Splits is not shown from 1024 px, so the sheet never opens there.
- **R55. The desktop layout.** (v1.1.0 new) From 1024 px the top bar is 64 px, and `main.layout` shows `section.stage#stage[aria-label="Bill and splits"]` (the card, R51 and R19 to R21) beside `section.work#work[aria-label="Edit the bill"]` (People, Charges, Split, then Items or Subtotal) with both sections open (R48). The strip is not shown. At 1280 x 800 the page never scrolls (`document.documentElement.scrollHeight <= innerHeight`) in every golden state, and the card and the working sit where the goldens put them (`bill-items.md`, card at 98, 84, 460 x 642).
- **R56. The item frame.** (v1.1.0 new) `div.frame-wrap#frameWrap` wraps `ul.frame#itemList` and scrolls inside itself (CSS). The app sets the attribute `data-up` (empty value) while the list is scrolled down from its top and removes it at the top, and sets `data-down` while more of the list is below its visible part and removes it at the end, at every width. It updates both on every render, on the list's `scroll` event and when the frame's size changes. At 1280 x 800 the K1 frame has `data-down` and no `data-up`. At 360 x 780 the W1 frame has `data-down`, and at 390 x 844 it has neither.
- **R35. Phone first.** (v1.1.0 changed) In every golden state at 360 x 780, 390 x 844 and 1280 x 800, the page has no horizontal overflow (`document.documentElement.scrollWidth <= window.innerWidth`) and no element sticks out past the viewport's right edge. The people grid shows 2 columns at 360 and 390 and 3 at 1280. Below 1024 px the order is the top bar, People, Charges, Split, then Items or Subtotal, with the strip fixed at the bottom. Sizes the goldens' `.md` files give are checked by the element checklist in `qa.md`.
- **R60. Large bills fit 360 px.** (v1.1.0 new) At 360 x 780, for the W1 bill (`bill-large`), core's MAX-E bill and core's MAX-I bill, the page has no horizontal overflow, and no money figure is wider than its box in the card, the sheet or the strip (`scrollWidth <= clientWidth` for every `.r-amount`, `.amt`, `.r-lines dd`, `.s-fig` and `.wk`). The price field shows "964.50" whole in W1. [Ledger S2 "at any bill size". If a MAX bill breaks this, it is a design finding for the owner. CSS stays a byte copy.]

### Spare sen (C9, ledger S1)
- **R51. The spare sen line and chip.** (v1.1.0 new) For an `even` or `item` result whose `spare.count` is above 0, the receipt holds `div.r-spare` after the proof row, with `<p>{count} sen left over</p>` (`#spareLine` on the card) and `div.r-spare-acts`. When `result.spare.rule` is "random", `div.r-spare-acts` holds first the Pick again chip (`button.chip-btn`, `#pickAgain` on the card, the shuffle icon then "Pick again"). Then the spare chip (`button.chip-btn`, `#spareBtn` on the card, `aria-haspopup="dialog"`, the chip text then the caret icon) with `aria-label="Spare sen: {chip text}. Change"`. The chip text names the rule in effect, `result.spare` (CG-P7), "Top of the list" for "top", "One person, {personLabel}" for "one", "At random" for "random". When `spare.count` is 0 there is no `div.r-spare`. A click on a chip opens P1 (R52), a click on Pick again is R54.
- **R52. P1, the spare sen choice.** (v1.1.0 new) `dialog.pop#spareDlg[aria-labelledby=spareTitle][aria-describedby=spareSub]` opens with `showModal()` from either spare chip. It holds `div.in` with `div.pop-head` (`h2#spareTitle` "Spare sen" and `button.icon-btn[aria-label=Close]` with the X icon), `p.pop-sub#spareSub` "{count} sen left over", and `div.choices` with three `label.choice` in order Top of the list, One person, At random, each holding `input[type=radio][name=spareRule]` (values `top`, `one`, `random`), `span.dot[aria-hidden=true]` and `<span>` with the label. The checked radio is the stored choice `bill.spare.rule` (CG-P7). Focus moves to the checked radio on open. A `change` on a radio applies at once through `chooseSpareRule(bill, value, Math.random)`, saves and renders, P1 stays open, and the receipt behind it, the chip text and P1's own content follow (rule 7). Arrow keys move between the choices (native radios). Escape, Close, and a click whose press and release both fall on its backdrop close it, and focus returns to the spare chip shown at that moment (`#spareBtn` from 1024 px, the sheet's chip below, PD-23). A click that opens or closes it arms `swallowRepeatClicks` (PD-21). **Place.** From 1024 px P1's `left` is the card's right edge plus 16 px and its `bottom` is the viewport height less the chip's bottom edge, so its bottom is level with the chip's bottom (`spare-sen.md`, left 574 and bottom edge at 632.8 at 1280 x 800 for K1, 560.8 for K2). Both are set through the CSSOM (R38) on open and whenever the viewport size changes while it is open. Below 1024 px the CSS makes P1 a bottom sheet over the Splits sheet, the app clears `left` and `bottom`, and while P1 is open it sets `#sheetScroll`'s `padding-bottom` to P1's height plus 16 px (271 px for K1, 325 px with the picker or Pick again), clearing it when P1 closes. When the last split row would then sit under P1, the sheet scrolls by the overlap, never further than putting the Splits heading at the top of the scroll area (g2's rule, so the splits stay in view). P1 follows the place of the current width when the width crosses 1024 px while it is open.
- **R53. One person and its picker.** (v1.1.0 new) While the stored rule is "one", `fieldset.pick#pickWrap` follows the One person choice inside `div.choices`, holding `legend.sr` "Who pays the spare sen" and `div.pick-list#pickList` with one `label.pill` per id of `sparePeople(bill)` in list order (CG-P2). Each pill holds `input[type=radio][name=spareWho]` whose `value` is that person's 1-based position in the people list, checked when the id is `bill.spare.personId`, and `span.pill-face` with the check icon and the person's label. A `change` on a pill calls `chooseSparePerson(bill, id)`, saves and renders. Choosing One person picks the first eligible person at once (core R29), so a pill is checked straight away (rule 8). Arrow keys move between the pills (native radios). While the stored rule is not "one" there is no `#pickWrap`. On K2, One person and then Ben give RM 38.86, RM 38.88, RM 38.86 (`spare-sen-one.md`).
- **R54. At random and Pick again.** (v1.1.0 new) While the stored rule is "random", `div.pick#randWrap` follows the At random choice inside `div.choices`, holding `button.btn.btn-ghost#pickAgainSheet` (shuffle icon, "Pick again"). While the rule is not "random" there is no `#randWrap`. Pick again, in P1 or on the receipt (R51), calls `pickAgain(bill, Math.random)`, and saves and renders when the bill changed (core R31 draws until the splits change, at most 64 times, CG-P3). The app passes `Math.random` to `chooseSpareRule` and `pickAgain` and to nothing else (PD-19). The drawn order is kept in the draft (R61), so a reload shows the same splits. A render keeps the focused chip or button in place, so after a keyboard press on Pick again focus stays on it. Copy summary copies the splits as drawn (R22).

### New bill (C8)
- **R29. Confirmation dialog opens.** (v1.1.0 changed) "New bill" in the top bar is `button.btn.btn-ghost#newBill[aria-haspopup=dialog]` with the plus icon. It opens `dialog.modal#newDlg[aria-labelledby=newTitle][aria-describedby=newBody]` with `showModal()`. The dialog holds `div.in` with `h2#newTitle` "Start a new bill?", `p#newBody` "This clears the people, items and amounts." and `div.acts` with `button.btn.btn-danger.btn-lg#startNew` "Start new bill" and then `button.btn.btn-ghost.btn-lg` "Cancel". On open, focus goes to Cancel (rule 11). Tab from Cancel moves to Start new bill and Shift+Tab from Start new bill moves to Cancel, so focus never leaves the two buttons (the app wraps Tab itself, PD-14, the measurement lives in the comment of `createDialog` in `src/ui/dialog.js`). The page behind is inert and does not scroll. A double click, a triple click or a double tap on New bill leaves the dialog open with focus on Cancel, because opening arms `swallowRepeatClicks` (I-1).
- **R30. Cancel changes nothing.** Cancel, Esc and a click on the backdrop close the dialog and leave the bill, the draft and the screen unchanged. A backdrop click acts exactly as Cancel, including where focus returns, and the click does not reach the control drawn under it. [Backdrop ruled 2026-10-08, ORCH, CG-8 in `ROADMAP.md`. It follows the design flow check, `docs/design-explore/FLOW-CHECK.md`, where a click at (10, 10) on the backdrop returns to S2.] Native `showModal()` ignores a backdrop click (measured during planning), so the app handles it. A click whose target is the `dialog` element itself and whose point falls outside the dialog's box is a backdrop click. After any close, focus is on "New bill". [Added 2026-10-09, ORCH, code-review CR-01 and WR-06. (1) A backdrop click is one whose press also began on the backdrop: selecting the dialog text and letting go over the backdrop does not close it. (2) The second press and click of a double click or double tap that closed the dialog (Cancel, Start new bill or the backdrop) are cancelled at the document, so they cannot reach the control drawn under the closed dialog, move focus off "New bill" or change the bill. The guard ends at the first press that is not a repeat, and it uses no timer.] [Changed 2026-10-09, ORCH, security audit SEC-01 and I-1: the guard lives in `src/ui/dom.js` (`swallowRepeatClicks`) and is shared with the Remove buttons (R7, R12) and with the click that opens the dialog (R29).] [Changed 2026-10-09, ORCH, regression RG-CR-01: it is shared with the Add person and Add item clicks too (R6, R12).]
- **R31. Start new bill.** (v1.1.0 changed) Start new bill sets the bill to `newBill()`, saves it (a save attempt, R46), closes the dialog and renders the `bill-empty` state. Below 1024 px People opens and Charges folds (the open state is reset as at load, CG-P4). Focus returns to New bill (rule 11). The view state is reset, every inline error flag, the copy status and the open state, so a stale flag cannot show an error early on the next bill (item ids restart at `i3`). The spare choice is Top of the list again (core R10).
- **R57. A held Enter adds no blank item.** (v1.1.0 new) `swallowRepeatClicks` also listens to `keydown` on the document in the capture phase while armed, and cancels (`preventDefault` and `stopPropagation`) every `keydown` whose `repeat` is true, which also stops the key click a held Enter would give the control that now has focus. The guard still ends at the first press that is not a repeat (a `mousedown` or `click` with a click count of 1 or less, or a `keydown` whose `repeat` is false). So a held Enter on the Remove of the only item removes that item only, `items` is empty, `nextId` is unchanged and focus is on Add item (R34). A held Enter on New bill leaves the dialog open with focus on Cancel. Two separate presses still act twice, and after a Remove a held letter in a name field still types. [Ledger S3, SEC-04 of 1.0 with its suggested fix.]

### Keyboard, focus, layout, motion (platform rules)
- **R32. Keyboard order and visible focus.** (v1.1.0 changed) Tab reaches every enabled control in the golden's DOM order, and skips disabled controls and everything not displayed. Below 1024 px with K1 that is New bill, the People row, the Charges row, By item, Add item, then for each item its name, price, Remove and three toggles, then Splits and Copy summary (31 stops). With `bill-empty` it is New bill, the People row, Add person, Person 1 name, Person 2 name, the Charges row, Even, Subtotal in RM, Splits. With the unreadable note, Dismiss note comes before New bill (it sits before New bill in the top bar's DOM). From 1024 px with K1 it is New bill, the spare chip, Copy summary, Add person, then each person's name and Remove, Service charge, SST, By item, Add item, then each item's name, price, Remove and toggles. Inside the sheet it is Close, the chip (Pick again first when At random), Copy summary. Inside P1 it is Close, the checked choice, then the checked pill or Pick again when shown. Every focused control shows the system's one ring (2 px `--focus` at 2 px offset, on the wrapper for fields, inset on a Remove inside a person field, inset on the focused half of the Split switch, 8 px wider than a header row, `system.md` Focus). An error field keeps its red edge and gains the ring.
- **R33. Typing never loses its place.** The app never replaces, re-creates or moves an input element while it has focus, and never writes the `value` or caret of the input the user is typing in. After every keystroke in any field, the same element still has focus and the caret is where the user put it, including when typing in the middle of the text and during IME composition.
- **R34. Focus after add and remove.** [CG-2 ruled 2026-10-08, ORCH. Accepted as written.] After Add person, focus is on the new person's name input. After Add item, focus is on the new item's name input. After removing the person or item at position k, focus is on the name input now at position k, or at k - 1 when the removed one was last. After removing the last remaining item, focus is on "Add item".
- **R36. Motion.** (v1.1.0 changed) Motion is the list of `system.md`, nothing more. Hover and press colours over 120 ms, the foil sweep and the light across the card once on load, the 200 ms section reveal (R48), the frame fades over 160 ms, the sheet's 240 ms lift, P1's 200 ms rise and M1's 160 ms fade. With `prefers-reduced-motion: reduce` every computed `transition-duration` of `.btn`, `.chip-btn`, `.tap`, `.icon-btn`, `.choice`, `.mode-sw label` and `.pill-face` is `0s`, and `document.getAnimations()` is empty at load and right after every interaction. With `no-preference` nothing loops, so `document.getAnimations()` is empty 3 s after load and 1 s after any interaction.
- **R59. Behaviour stated per engine.** (v1.1.0 new) Every requirement that names a focus target (R27, R29, R30, R31, R34, R50, R52, R53, R54, R57) moves focus by script and holds in both engines. Where focus is left to the browser after a mouse click on a button, a radio or a label, Chromium focuses the control and WebKit leaves `document.activeElement` on `body` (WebKit's `isMouseFocusable` for form controls, research section 2), and each test asserts its own engine's result. The IME test of R33 needs a CDP session and is `chromium_only`. Task A0 probes, in WebKit on this machine, the click count (`detail`) of a quick double tap and the order of a tap's pointer and mouse events (R7, R10), `isSecureContext` and `typeof Clipboard` on `http://127.0.0.1` (R22, R23), whether an init script can redefine `window.localStorage` (R46 driver D-b), and the console text of a CSP violation and of a denied `localStorage`. The first WebKit run sorts each failure as (a) an app defect Safari would show, fixed in the app, (b) an engine difference, written into this requirement with its measurement and asserted per engine, or (c) a Chromium-only tool, marked `chromium_only` with its reason. The app never gets a hook to make an engine pass.

### Security
- **R37. Text stays text.** (v1.1.0 changed) Every name, price text and rate text reaches the DOM only through `textContent`, the `value` property or `setAttribute` on `aria-label` and `placeholder`. Files under `src/` contain none of `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval(`, `new Function(`, `setAttribute("on`, `createContextualFragment` or `DOMParser`, and neither `index.html` nor `src/` holds a `<template`. A person name such as `<svg onload=f()>` (16 characters) shows as those literal characters in the field, every toggle, the splits rows, the Remove button's name, the People summary, the picker pill and the clipboard text. An item name such as `<img src=x onerror=alert(1)>` (28 characters) shows as those characters in the field, `Remove {itemLabel}`, `{itemLabel} price in RM` and `Who had {itemLabel}`. Neither creates an element. The run-time icons are built with `createElementNS` (`svg` and `use`) and `setAttribute` for `class`, `aria-hidden`, `focusable` and `href`, whose value is `#i-` plus a name from the fixed list of R44. Every `svg` under `body` is `svg.sprite`, `svg.mark`, `svg.ic` or `svg.seal`. [CG-9 and CG-10 of 1.0 stand.]
- **R38. Content Security Policy.** (v1.1.0 changed) `index.html` carries exactly `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; base-uri 'none'; form-action 'none'">`. No inline script, no `<style>` element and no `style` attribute exist in `index.html`. Code in `src/` writes style only through `style.setProperty` and `style.removeProperty` on exactly these targets. `--strip-h` on the root element (R49), `--rows` on `ul.r-splits.many` (R20), `left` and `bottom` on `#spareDlg` from 1024 px (R52), and `padding-bottom` on `#sheetScroll` while P1 is open below 1024 px (R52). The values are measured numbers in px or a count, never text from the bill. `src/` holds no `setAttribute("style"`, `cssText`, `insertRule`, `new CSSStyleSheet`, `adoptedStyleSheets`, `<style` or direct `.style.<property> =` write. The Web Animations API is used only for the section reveal (R48, PD-22). The tab icon loads under the policy in both engines (R45). No CSP violation happens during any functional scenario or the live gate in either engine, and neither uses `bypass_csp`. [Changed 2026-10-13, v1.1.0, S6 and S7. The goldens draw script-set values in their "Golden only" styles. The build sets the same four through the CSSOM, which the policy allows. The fidelity harness renders with `bypass_csp`, so the suite and the live gate are what catch policy breakage.]
- **R39. Nothing leaves the device.** (v1.1.0 changed) Files under `src/` contain none of `fetch(`, `XMLHttpRequest`, `WebSocket`, `EventSource`, `sendBeacon` or `serviceWorker`, and no string with a scheme, with exactly two exemptions. (1) The namespace string `http://www.w3.org/2000/svg` as the first argument of a `createElementNS` call (CG-10 of 1.0). (2) The same string once in `src/icon.svg`, as the `xmlns` attribute of its root element and nowhere else in that file. No other string with a scheme is allowed anywhere, not even another namespace. `index.html` holds no `://` at all (the sprite and the mark carry no `xmlns`). During every browser run in either engine the only requests are same-origin GETs for the page, `src/system.css`, files under `src/` (`/src/icon.svg` allowed, not required) and the browser's own `/favicon.ico`.

### Gates
- **R40. Looks right.** (v1.1.0 changed) The fidelity gate of `qa.md` passes all 40 state and width pairs in Chromium (twelve goldens at 390 x 844, 360 x 780 and 1280 x 800, and `bill-items-open` and `splits-sheet` at 390 and 360), and every row of the FE element checklist passes. The fidelity gate does not run in WebKit (ledger S5 row 2).
- **R41. Works right.** (v1.1.0 changed) The cold-boot live-e2e gate of `qa.md` passes in Chromium and in WebKit and leaves an evidence artifact per engine. No artifact means not done. A WebKit failure blocks the seal.
- **R58. The engine switch.** (v1.1.0 new) `tests/browser/conftest.py` adds `--engine` (`pytest_addoption`, choices `chromium` and `webkit`, default `chromium`) and a session `engine` fixture. Every browser is launched in one place, `rig.launch(playwright, engine)` in `tests/browser/rig.py`, with launch arguments kept per engine (none for either today), headless always, never with `is_mobile`. A registered marker `chromium_only(reason=...)` becomes a skip with that reason when the engine is not Chromium, and every skip is listed with its reason and counted in the run's evidence, never reported as a pass. `tests/browser/live_e2e.py` takes `--engine` with the same choices and default. Evidence folders end in the engine (`qa/functional/<stamp>-<engine>/`, `qa/live-e2e/<stamp>-<engine>/`), and each summary records the engine and `browser.version`. `tests/browser/fidelity/run.py` takes no engine option and runs Chromium only. The plain commands keep running Chromium as in 1.0. A meta test checks that only `rig.py` launches a browser, beside 1.0's test that only the rig makes contexts. [Research webkit-testing section 5, ledger S5 row 2.]

## Contracts

### Files
| File | Owns |
|---|---|
| `index.html` (project root) | The shipped entry point. The head of R1, the sprite and the inline mark of R44. It may hold the static parts of the shell (the top bar, the section frames, the Split switch, the strip frame, the three dialog elements), or `src/main.js` may build them. Either way the result is the DOM contract |
| `src/system.css` | Byte copy of `docs/design/system.css`. Never edited |
| `src/icon.svg` | The tab icon of R45, bytes fixed by the golden |
| `src/main.js` | Boot (storage, draft load, notes, the open state, first render) and event wiring. Holds the one `bill` value and the view state, and calls `split-core` actions |
| `src/draft.js` | `DRAFT_KEY`, `encodeDraft`, `decodeDraft`, `getStorage`, `loadDraft`, `saveDraft` (R25 to R28, R46, R47, R61). Pure apart from the storage object passed in and `getStorage`, which reads `window.localStorage` |
| `src/errors.js` | The R10 error flags (1.0, unchanged in shape) |
| `src/ui/*.js` | Rendering, one file per block where that keeps each file single-purpose. The top bar and notes, the sections, people, charges, the Split switch and Subtotal, items and the frame, the receipt renderer (one function for card and sheet), the strip, the sheet, P1, the New bill dialog, icons (`createElementNS`), the DOM helpers (`swallowRepeatClicks`, `isRepeatClick`), `field-leave.js` and `field-error.js`. Names are the builder's choice |
| `tests/browser/` | Python Playwright tests (`conftest.py`, `rig.py`, `seeds.py`, `test_app.py`), the clipboard stand-ins (`clipboard/`), the storage drivers (`storage/`), the CSP listener (`csp/`), the fidelity seed and after-load scripts and runner (`fidelity/`) and the live gate (`live_e2e.py`). Test-side only, never loaded by `index.html`. Seeds live here and nowhere under `src/` |
| `tests/draft.test.js`, `tests/errors.test.js` | Node unit tests of `src/draft.js` (D1 to D14) and `src/errors.js`, run with `node --test`. Test-side only |

### Imports from split-core (the only cross-module surface)
`LIMITS`, `newBill`, `addPerson`, `removePerson`, `setPersonName`, `setMode`, `setSubtotalText`, `setServiceText`, `setSstText`, `addItem`, `removeItem`, `setItemName`, `setItemPriceText`, `toggleItemPerson`, `personLabel`, `itemLabel`, `sparePeople` from `src/core/bill.js`. `parseAmount`, `parseRate`, `formatMoney`, `formatRate`, `formatAmount` from `src/core/money.js`. `computeResult` from `src/core/result.js`. `chooseSpareRule`, `chooseSparePerson`, `pickAgain` from `src/core/spare.js`. `summaryText` from `src/core/summary.js`. Types are as declared in `split-core/spec.md` (`Bill` with `spare`, results with `spare: { count, rule, personId }`, the blocked reason `no-prices`).

### Gesture to action
| Gesture | Effect |
|---|---|
| `input` on Person {i} name | `setPersonName`, save, render (R5) |
| click Remove {personLabel} | arm the guard, `removePerson`, save, render, focus (R7, R34) |
| click Add person | arm the guard, `addPerson`, save, render, focus (R6, R34) |
| `change` on a Split radio | `setMode`, save, render (R8) |
| `input` on Subtotal | `setSubtotalText`, save, render, error rule (R9, R10) |
| `input` on an item name or price | `setItemName` or `setItemPriceText`, save, render (R11, R10) |
| click Remove {itemLabel} | arm the guard, `removeItem`, save, render, focus (R12, R34) |
| click a toggle | `toggleItemPerson`, save, render (R13) |
| click Add item | arm the guard, `addItem`, save, render, focus (R12, R34) |
| `input` on Service charge or SST | `setServiceText` or `setSstText`, save, render, error rule (R15, R10) |
| focus leaves an amount or rate field | error rule (a) of R10, no save |
| click, Enter or Space on a header row | toggle the section, reveal on open (R48), no save |
| click Copy summary (card, sheet, strip) | clipboard and status (R22 to R24), no save |
| click Splits | arm the guard, fill and open the sheet, focus the sheet (R50) |
| Close, Esc or backdrop of the sheet | arm the guard, close, empty, focus Splits (R50) |
| click a spare chip | arm the guard, open P1, focus the checked choice (R52) |
| `change` on a spare choice | `chooseSpareRule(bill, value, Math.random)`, save, render (R52) |
| `change` on a pill | `chooseSparePerson`, save, render (R53) |
| click Pick again (receipt or P1) | `pickAgain(bill, Math.random)`, save and render when changed (R54) |
| Close, Esc or backdrop of P1 | arm the guard, close, clear the sheet padding, focus the shown chip (R52) |
| click New bill | arm the guard, open M1, focus Cancel (R29) |
| click Start new bill | arm the guard, `newBill()`, save, close, reset the view state, render, focus New bill (R31) |
| click Cancel, Esc, click the backdrop of M1 | arm the guard, close, focus New bill (R30) |
| click Dismiss note | remove the note, focus New bill (R27) |
| held key (`keydown` with `repeat`) while the guard is armed | cancelled (R57) |
| viewport crosses 1024 px | close an open sheet without moving focus (R50), re-place an open P1 (R52), re-measure the strip and the People summary |

### View state (in memory only, never saved)
`{ errorShown: { subtotal, service, sst, price: { [itemId]: boolean } }, noteShown: boolean, saveFailing: boolean, status: null | "ok" | "fail", open: { people: boolean, charges: boolean } }`, plus the storage handle (null while the getter failed). At boot `errorShown` is set from the restored texts (R10 b), `open` by R48 and `saveFailing` by the boot read (R46). Start new bill resets `errorShown`, `status` and `open` (R31). The dialogs' open state is the DOM's.

### DOM contract
Braces are filled at render time. `{i}` and `{j}` are 1-based positions. `{personLabel}` and `{itemLabel}` come from core `personLabel` and `itemLabel`. `[...]` marks a conditional attribute or element. `{X}`, `{Plus}`, `{Copy}`, `{Check}`, `{Caret}`, `{Shuffle}`, `{Warning}`, `{WarningCircle}` and `{Mark}` stand for `<svg class="ic" aria-hidden="true" focusable="false"><use href="#i-{name}"/></svg>` with names `x`, `plus`, `copy`, `check`, `caret`, `shuffle`, `warning`, `warning-circle`, `mark`. `{Seal}` is the same with `class="seal"` and `#i-seal-check`. The sheet's caret is `class="ic sec-caret"` in a header row and `class="ic caret-up"` on Splits. Inputs carry their value as the `value` property.

```html
<body>
<svg class="sprite" aria-hidden="true" focusable="false">...the golden's block byte for byte (R44)...</svg>
<div class="app">
  <header class="top">
    <div class="brand">
      <svg class="mark" viewBox="0 0 28 28" aria-hidden="true" focusable="false"><path fill-rule="evenodd" d="{the golden mark28 path}"/></svg>
      <h1 class="word">Splity Tab</h1>
    </div>
    <div class="notes" id="notes">
      [save failing, R46, first] <div class="note is-warn" role="status">{Warning}<p>This bill is not being saved on this device. It will be lost when you close this tab.</p></div>
      [unreadable note, R27] <div class="note" role="status">{WarningCircle}<p>Your saved bill could not be read, so a new one was started.</p><button type="button" class="icon-btn" id="dismissNote" aria-label="Dismiss note">{X}</button></div>
    </div>
    <button type="button" class="btn btn-ghost" id="newBill" aria-haspopup="dialog">{Plus}New bill</button>
  </header>
  <main class="layout">
    <section class="stage" id="stage" aria-label="Bill and splits">
      <article class="glass card" id="card">
        <div class="foil" aria-hidden="true"></div>
        <div class="rbody" id="rbody">{receipt with card ids}</div>
      </article>
    </section>
    <section class="work" id="work" aria-label="Edit the bill">
      <div class="blk sec" id="peopleBlk" data-open="{true|false}">
        <h2 class="sec-h"><button type="button" class="sec-btn" id="peopleBtn" aria-expanded="{true|false}" aria-controls="peopleBody" aria-labelledby="peopleName" aria-describedby="peopleSum"><span class="sec-name" id="peopleName">People</span><span class="sec-sum" id="peopleSum"><span class="sec-txt">{people summary}</span></span>{Caret}</button></h2>
        <div class="sec-body" id="peopleBody">
          <div class="sec-in people-in">
            <div class="blk-head">
              <h2 class="blk-h" id="peopleH">People</h2>
              <button type="button" class="btn btn-ghost" id="addPerson" [disabled at 12]>{Plus}Add person</button>
            </div>
            <ul class="people" id="peopleList" aria-labelledby="peopleH">
              [one per person] <li class="field person"><input type="text" placeholder="Person {i}" maxlength="20" autocomplete="off" aria-label="Person {i} name"><button type="button" class="icon-btn" aria-label="Remove {personLabel}" [disabled at 2]>{X}</button></li>
            </ul>
          </div>
        </div>
      </div>
      <div class="blk sec" id="chargesBlk" data-open="{true|false}">
        <h2 class="sec-h"><button type="button" class="sec-btn [is-bad]" id="chargesBtn" aria-expanded="{true|false}" aria-controls="chargesBody" aria-labelledby="chargesName" aria-describedby="chargesSum"><span class="sec-name" id="chargesName">Charges</span><span class="sec-sum" id="chargesSum">[is-bad]{WarningCircle}<span class="sec-txt">{charges summary}</span></span>{Caret}</button></h2>
        <div class="sec-body" id="chargesBody">
          <div class="sec-in">
            <h2 class="blk-h solo" id="chargesH">Charges</h2>
            <div class="charges">
              <div>
                <label class="lbl" for="svc">Service charge</label>
                <div class="field pct [is-bad]"><input type="text" id="svc" inputmode="decimal" autocomplete="off" aria-describedby="chargeHint[ svcErr]" aria-invalid="{false|true}"><span class="unit" aria-hidden="true">%</span></div>
                <p class="err" id="svcErr" [hidden]>{WarningCircle}Enter a rate from 0 to 30</p>
              </div>
              <div>
                <label class="lbl" for="sst">SST</label>
                <div class="field pct [is-bad]"><input type="text" id="sst" inputmode="decimal" autocomplete="off" aria-describedby="chargeHint[ sstErr]" aria-invalid="{false|true}"><span class="unit" aria-hidden="true">%</span></div>
                <p class="err" id="sstErr" [hidden]>{WarningCircle}Enter a rate from 0 to 20</p>
              </div>
              <p class="hint" id="chargeHint">Set a charge to 0 if your bill already includes it.</p>
            </div>
          </div>
        </div>
      </div>
      <div class="blk split" id="splitBlk" role="group" aria-labelledby="splitH">
        <h2 class="blk-h" id="splitH">Split</h2>
        <div class="mode-sw">
          <input type="radio" name="mode" id="modeEven" value="even" [checked]><label for="modeEven">Even</label>
          <input type="radio" name="mode" id="modeItem" value="item" [checked]><label for="modeItem">By item</label>
        </div>
      </div>
      [even mode only]
      <div class="blk" id="evenBlock">
        <label class="blk-h solo" for="evenSub">Subtotal</label>
        <div class="field money sub-field [is-bad]" id="evenField"><span class="unit" aria-hidden="true">RM</span><input type="text" id="evenSub" inputmode="decimal" autocomplete="off" placeholder="0.00" aria-label="Subtotal in RM" aria-describedby="evenErr" aria-invalid="{false|true}"></div>
        <p class="err" id="evenErr" [hidden]>{WarningCircle}Enter an amount like 12.50</p>
      </div>
      [by-item mode only]
      <div class="blk items-blk" id="itemsBlock">
        <div class="blk-head">
          <h2 class="blk-h" id="itemsH">Items</h2>
          <button type="button" class="btn btn-ghost" id="addItem" [disabled at 50]>{Plus}Add item</button>
        </div>
        <div class="frame-wrap" id="frameWrap" [data-up] [data-down]>
          <ul class="frame" id="itemList" aria-labelledby="itemsH">
            [one per item] <li class="item [needs]">
              <div class="item-row">
                <div class="field"><input type="text" placeholder="Item {j}" maxlength="40" autocomplete="off" aria-label="Item {j} name"></div>
                <div class="field money [is-bad]"><span class="unit" aria-hidden="true">RM</span><input type="text" placeholder="0.00" inputmode="decimal" autocomplete="off" aria-label="{itemLabel} price in RM" aria-invalid="{false|true}" aria-describedby="ie{j}"></div>
                <button type="button" class="icon-btn" aria-label="Remove {itemLabel}">{X}</button>
                <p class="err" id="ie{j}" [hidden]>{WarningCircle}Enter an amount like 12.50</p>
              </div>
              <div class="taps" role="group" aria-label="Who had {itemLabel}">[one per person]<button type="button" class="tap" aria-pressed="{true|false}">{Check}<span>{personLabel}</span></button></div>
            </li>
          </ul>
        </div>
      </div>
    </section>
  </main>
  <div class="strip glass dense" id="strip">
    <div class="foil" aria-hidden="true"></div>
    <div class="strip-in">
      <div class="strip-top">
        <div class="strip-info" id="stripInfo">
          [even, item] <span class="s-label">Total</span><span class="s-fig" id="stripTotal"><span class="cur">RM </span>{formatAmount(total)}</span>
          [blocked] <p class="s-msg" id="stripMsg">{R17 message}</p>
          [unassigned] <p class="s-msg" id="stripMsg">{WarningCircle}{R18 message}</p>
        </div>
        <p class="status [is-fail]" id="stripStatus" role="status">[status]{Check or WarningCircle}{status text}</p>
      </div>
      <div class="strip-acts">
        <button type="button" class="btn btn-ghost" id="splitsBtn" aria-haspopup="dialog" aria-controls="splitsDlg" aria-expanded="{false|true}">Splits{Caret}</button>
        <button type="button" class="btn btn-primary" id="stripCopy" [disabled unless even or item]>{Copy}Copy summary</button>
      </div>
    </div>
  </div>
</div>
<dialog class="sheet-dlg" id="splitsDlg" aria-label="Splits">
  [open only]
  <div class="glass dense sheet" tabindex="-1">
    <div class="foil" aria-hidden="true"></div>
    <div class="sheet-top"><span class="grab" aria-hidden="true"></span><button type="button" class="icon-btn" aria-label="Close">{X}</button></div>
    <div class="sheet-scroll" id="sheetScroll"><div class="rbody">{receipt with sheet ids}</div></div>
  </div>
</dialog>
<dialog class="pop" id="spareDlg" aria-labelledby="spareTitle" aria-describedby="spareSub">
  <div class="in">
    <div class="pop-head"><h2 id="spareTitle">Spare sen</h2><button type="button" class="icon-btn" aria-label="Close">{X}</button></div>
    <p class="pop-sub" id="spareSub">{count} sen left over</p>
    <div class="choices">
      <label class="choice"><input type="radio" name="spareRule" value="top" [checked]><span class="dot" aria-hidden="true"></span><span>Top of the list</span></label>
      <label class="choice"><input type="radio" name="spareRule" value="one" [checked]><span class="dot" aria-hidden="true"></span><span>One person</span></label>
      [stored rule one] <fieldset class="pick" id="pickWrap"><legend class="sr">Who pays the spare sen</legend><div class="pick-list" id="pickList">[one per eligible person]<label class="pill"><input type="radio" name="spareWho" value="{i}" [checked]><span class="pill-face">{Check}{personLabel}</span></label></div></fieldset>
      <label class="choice"><input type="radio" name="spareRule" value="random" [checked]><span class="dot" aria-hidden="true"></span><span>At random</span></label>
      [stored rule random] <div class="pick" id="randWrap"><button type="button" class="btn btn-ghost" id="pickAgainSheet">{Shuffle}Pick again</button></div>
    </div>
  </div>
</dialog>
<dialog class="modal" id="newDlg" aria-labelledby="newTitle" aria-describedby="newBody">
  <div class="in">
    <h2 id="newTitle">Start a new bill?</h2>
    <p id="newBody">This clears the people, items and amounts.</p>
    <div class="acts">
      <button type="button" class="btn btn-danger btn-lg" id="startNew">Start new bill</button>
      <button type="button" class="btn btn-ghost btn-lg">Cancel</button>
    </div>
  </div>
</dialog>
</body>
```

The receipt is written once (PD-20). Card ids are `rTotal`, `splitsH`, `splits`, `addsUp`, `spareLine`, `pickAgain`, `spareBtn`, `copyBtn`, `cardStatus`. In the sheet only the heading has an id, `sheetSplitsH`, and the list's `aria-labelledby` points at it.

```html
[even, item]
<div class="r-total"><span class="r-label">Total</span><p class="r-amount" [id="rTotal"]><span class="cur">RM </span>{formatAmount(total)}</p></div>
<dl class="r-lines">
  <div><dt>Subtotal</dt><dd>{formatMoney(subtotal)}</dd></div>
  <div><dt>Service {formatRate(serviceBp)}</dt><dd>{formatMoney(service)}</dd></div>
  <div><dt>SST {formatRate(sstBp)}</dt><dd>{formatMoney(sst)}</dd></div>
</dl>
<div class="r-rule" aria-hidden="true"></div>
<div class="r-head"><h2 id="{splitsH|sheetSplitsH}">Splits</h2>[item]<span aria-hidden="true">items + charges</span></div>
<ul class="r-splits [many]" [id="splits"] aria-labelledby="{splitsH|sheetSplitsH}">
  [one per row] <li><span class="nm">{name}</span><span class="amt">{formatMoney(share)}</span>[item]<span class="wk"><span class="sr">Items </span>{formatAmount(items)} + <span class="sr">charges </span>{formatAmount(charges)}</span></li>
</ul>
<div class="r-check">{Seal}<span class="lbl-proof">Adds up to</span><span class="amt" [id="addsUp"]>{formatMoney(check.share)}</span>[item]<span class="wk">{formatAmount(check.items)} + {formatAmount(check.charges)}</span></div>
[spare.count above 0] <div class="r-spare"><p [id="spareLine"]>{count} sen left over</p><div class="r-spare-acts">[rule random]<button type="button" class="chip-btn" [id="pickAgain"]>{Shuffle}Pick again</button><button type="button" class="chip-btn" [id="spareBtn"] aria-haspopup="dialog" aria-label="Spare sen: {chip text}. Change">{chip text}{Caret}</button></div></div>
<button type="button" class="btn btn-primary btn-block r-copy" [id="copyBtn"]>{Copy}Copy summary</button>
<p class="status [is-fail]" [id="cardStatus"] role="status">[status]{Check or WarningCircle}{status text}</p>
[unassigned] the r-total, r-lines and r-rule above, then
<div class="r-msg">{WarningCircle}<p>{R18 message}</p></div>
[blocked]
<div class="r-total"><span class="r-label">Total</span></div>
<div class="r-empty">{Mark}<p>{R17 message}</p></div>
```

### Allowed differences from the goldens
These are the only ones. Anything else is a fidelity or R3 finding.
1. Inputs carry their value as the `value` property, not a `value` attribute.
2. `<head>` links `src/system.css`, `src/icon.svg` and `src/main.js` and carries the CSP meta, instead of the golden's inline `system.css`, "Golden only" styles and `data:` icon `href`.
3. Dialogs are opened with `showModal()` and their scrims are `::backdrop`. The goldens' `div.backdrop` elements, the `open` attribute, `inert` on `.app` and on the sheet under P1, and the static stand-in rules are stand-ins for a static file and do not exist in the app.
4. White-space text nodes and comments may differ where they do not render.
5. The specimen chrome of `states.html` (the page title, captions, frames, `h3` headings, the `st1` to `st3` ids, the `span.word` of the S5 frame) is not app markup.
6. A closed dialog and every element whose computed `display` is `none` are not rendered, so the R3 walk skips them with what is inside them, on both sides.
7. The `style` attributes the CSSOM writes of R38 exist on the root element, `ul.r-splits.many`, `#spareDlg` and `#sheetScroll`, where the goldens use their "Golden only" styles (or, in `bill-twelve.html`, `style="--rows:6"`). The walk does not compare `style`.
8. `data-up` and `data-down` on `#frameWrap` are set by the app (R56). The goldens draw their effect with a "Golden only" style.
9. In `bill-twelve.html`, `span.fit-wide` and `span.fit-narrow` inside the People `span.sec-txt` stand for the app's one fitted text (R48). The walk compares the visible text of `span.sec-txt`.
10. No `autofocus` in either. The app moves focus by script (R29, R50, R52).

### Copy (every UI string, exact)
| Where | Copy |
|---|---|
| Document title | Danial's Splity Tab |
| Wordmark | Splity Tab |
| Top bar button | New bill |
| Region names | Bill and splits (card) · Edit the bill (working) |
| Section names and headings | People · Charges · Split · Items · Subtotal (label) · Splits (receipt heading) |
| People summary | the labels joined by ", " · "{labels} and {n} more" · "{n} people" |
| Charges summary | Service {rate}, SST {rate} · Check service charge · Check SST · Check both rates |
| Buttons | Add person · Add item · Copy summary · Splits · Pick again · Close · Dismiss note |
| Split switch | Even · By item |
| Person field | aria-label "Person {i} name", placeholder "Person {i}", remove "Remove {personLabel}" |
| Item fields | aria-label "Item {j} name" and "{itemLabel} price in RM", placeholders "Item {j}" and "0.00", remove "Remove {itemLabel}", group "Who had {itemLabel}" |
| Subtotal field | aria-label "Subtotal in RM", placeholder "0.00" |
| Rate labels | Service charge · SST |
| Hint | Set a charge to 0 if your bill already includes it. |
| Amount error | Enter an amount like 12.50 |
| Rate errors | Enter a rate from 0 to 30 (service) · Enter a rate from 0 to 20 (SST) |
| Receipt | Total · Subtotal · Service {rate} · SST {rate} · items + charges · Items (hidden) · charges (hidden) · Adds up to |
| Spare sen | {count} sen left over · Top of the list · One person · At random · One person, {personLabel} · chip name "Spare sen: {chip text}. Change" · P1 title "Spare sen" · hidden legend "Who pays the spare sen" |
| Blocked messages | Check the charges to see the splits. · Enter the subtotal to see the splits. · Add each item and tap who had it to see the splits. · Give every item a price to see the splits. |
| Unassigned messages | 1 item still needs a person. Tap who had it to see the splits. · {count} items still need a person. Tap who had each one to see the splits. |
| Copy status | Summary copied · Could not copy. Your browser blocked the clipboard. |
| Notes | Your saved bill could not be read, so a new one was started. · This bill is not being saved on this device. It will be lost when you close this tab. |
| Dialog | Start a new bill? · This clears the people, items and amounts. · Start new bill · Cancel |

### Persistence
- **Key.** `split.draft` in `window.localStorage`. Nothing else is stored anywhere.
- **Envelope (version 2).** `{ "version": 2, "bill": Bill }` with `Bill` exactly as typed in `split-core/spec.md`. Example (the S2 bill with At random).

  ```json
  {"version":2,"bill":{"mode":"even","people":[{"id":"p1","name":"Aisyah"},{"id":"p2","name":"Ben"},{"id":"p3","name":"Chen"}],"subtotalText":"100.00","items":[],"serviceText":"10","sstText":"6","spare":{"rule":"random","order":["p2","p3","p1"]},"nextId":4}}
  ```
- **`src/draft.js` functions.**

  | Signature | Behaviour |
  |---|---|
  | `DRAFT_KEY = "split.draft"` | the key |
  | `encodeDraft(bill: Bill): string` | `JSON.stringify({ version: 2, bill })` |
  | `decodeDraft(text: string): { ok: true, bill: Bill } \| { ok: false }` | applies D1 to D14, never throws |
  | `getStorage(): Storage \| null` | `window.localStorage`, or `null` when reading it throws or gives null |
  | `loadDraft(storage: Storage \| null): { state: "failed" } \| { state: "none" } \| { state: "ok", bill: Bill } \| { state: "unreadable" }` | `failed` when storage is null or `getItem` throws (R46 at boot). `none` when `getItem` gives null. Otherwise the decoder decides |
  | `saveDraft(storage: Storage \| null, bill: Bill): boolean` | `setItem(DRAFT_KEY, encodeDraft(bill))`, `true` when it returns, `false` on null storage or any exception (R46). The caller re-reads `getStorage()` before each save while its handle is null (R47) |
- **Decoder rules.** A draft is readable only when all of these hold. Any failure gives `{ ok: false }`.
  - **D1.** The text parses with `JSON.parse` (no reviver).
  - **D2.** The parsed value is a plain object (not `null`, not an array).
  - **D3.** (v1.1.0 changed) `version` is exactly the number `1` or the number `2`.
  - **D4.** `bill` is a plain object.
  - **D5.** `bill.mode` is `"even"` or `"item"`.
  - **D6.** `bill.people` is an array of 2 to 12 plain objects. Each has `id`, a string matching `^p[0-9]{1,10}$`, and `name`, a string. Person ids are unique.
  - **D7.** `bill.items` is an array of 0 to 50 plain objects. Each has `id` matching `^i[0-9]{1,10}$`, `name` a string, `priceText` a string and `who` an array of strings. Item ids are unique. Every `who` entry is the id of a person in this bill, with no repeats inside one `who`.
  - **D8.** A person name has at most 20 and an item name at most 40 grapheme clusters, counted with `Intl.Segmenter` (granularity `grapheme`). No name contains U+000A or U+000D. (Grapheme clusters, because WebKit counts `maxlength` in grapheme clusters and Chromium in UTF-16 code units, and a name either engine let the user type must reload.)
  - **D9.** `subtotalText`, `serviceText` and `sstText` are strings.
  - **D10.** `nextId` is an integer from 1 to 1,000,000,000 and greater than the number in every person and item id.
  - **D11.** Unknown keys anywhere are ignored and are not carried into the decoded bill.
  - **D12.** The decoded `Bill` is built as new objects from the known fields only. Parsed objects are never copied wholesale (no spread, no `Object.assign`).
  - **D13.** (v1.1.0 new, version 2 only) `bill.spare` is a plain object. `rule` is `"top"`, `"one"` or `"random"`. For `"one"`, `personId` is a string equal to the id of a person in this bill. For `"random"`, `order` is an array of strings with exactly one entry per person of this bill, every entry the id of a person in this bill, no repeats. The decoded `spare` holds only `rule` and the field its rule needs.
  - **D14.** (v1.1.0 new, version 1 only) The decoded bill gets `spare` `{ rule: "top" }`, whatever `spare` key the draft holds.

## Tasks
Each task is one commit, adds the tests for the R#s it cites (see `qa.md`) and ends with `node --test "tests/**/*.test.js"` green and the browser suite green in Chromium. From A2 on, the WebKit suite is run at the end of each task and its result recorded. A test for a requirement that a later task builds is committed as `xfail(strict=True, reason="task An")`, so it is seen failing first, and that task removes the mark. A 1.0 browser test whose expectation a v1.1.0 change retires is updated or marked the same way in the commit that retires it. 1.0 tasks 1 to 13 are done and live in tag `v1.0.0`. The ROADMAP section v1.1.0 interleaves these tasks with core tasks C1 to C6.

- A0. [ ] After the orchestrator installs WebKit. The engine switch (`--engine`, `engine` fixture, `rig.launch`, `chromium_only`, counted skips, evidence suffix, `live_e2e.py --engine`, engine and version in each summary, the launch meta test), the IME test marked `chromium_only`, the WebKit baseline run of the current suite and live gate with the R59 probes, and each WebKit failure sorted (a), (b) or (c) with its record. -> R58, R59
- A1. [ ] (right after core C2) `src/draft.js` version 2. `encodeDraft` writes version 2, D3, D13, D14, `loadDraft` reports `failed`, with `tests/draft.test.js` cases. -> R61, R25, R26
- A2. [ ] Shell and head. `index.html` head (R1), `src/system.css` byte copy, `src/icon.svg`, the sprite and the mark, the top bar, the two regions, the strip frame, the three dialog elements, the icons module through `createElementNS` and `<use>`, cold boot into the blocked `bill-empty` receipt, the static scans. -> R1, R2, R3, R37, R38, R39, R43, R44, R45
- A3. [ ] Notes and the save warning. The unreadable note with Dismiss (focus to New bill), the warning (boot read, every save attempt, re-read of the getter, order in `#notes`), storage failures in memory, the test-side storage drivers. -> R27, R28, R46, R47
- A4. [ ] Sections. Header rows, open on load (CG-P4), toggle by click, Enter and Space, the two summaries with the fitted People text and the Check marker, the reveal through the Web Animations API, restore folds. -> R48, R26
- A5. [ ] People. Rows, live names, Add person and Remove with limits, the disabled look, focus, duplicates, typing keeps focus. -> R4, R5, R6, R7, R33, R34, R42
- A6. [ ] Charges with rate errors and rule 13. -> R15, R10
- A7. [ ] Split switch and Subtotal with the error rule. -> R8, R9, R10
- A8. [ ] Items and the frame. Rows, toggles, the `needs` marker, price errors, Add item and Remove with the limit, `data-up` and `data-down`, focus. -> R11, R12, R13, R14, R56, R10, R34
- A9. [ ] The receipt renderer and the card. Blocked, unassigned, even (with `many` and `--rows`) and by-item forms, the quiet regions. -> R16, R17, R18, R19, R20, R21
- A10. [ ] Copy and status on every status line, cleared by the next change. -> R22, R23, R24
- A11. [ ] The strip with `--strip-h`. -> R49
- A12. [ ] The Splits sheet (PD-18, PD-20, PD-21). -> R50
- A13. [ ] The spare line, the chips and P1 with its placement and the sheet padding (CG-P7, PD-21, PD-23). -> R51, R52, R25, R26
- A14. [ ] One person and the picker. -> R53
- A15. [ ] At random and Pick again with `Math.random`. -> R54
- A16. [ ] The New bill dialog and Start new bill. -> R29, R30, R31
- A17. [ ] The held-key guard in `swallowRepeatClicks`. -> R57
- A18. [ ] Cross-cutting checks in both engines. Tab order and rings, overflow and sizes at 360, 390 and 1280, the desktop layout, large bills at 360, motion, injection, CSSOM targets, network log, per-engine expectations. -> R32, R35, R36, R37, R38, R39, R55, R59, R60
- A19. [ ] Fidelity gate, Chromium. Version 2 seeds, after-load scripts, `run.py` with the 40 pairs, and a passing run with evidence. -> R40, R3
- A20. [ ] Cold-boot live gate in both engines, and a passing run per engine with evidence. -> R41

## Threat model
| Asset | Trust boundary | Threat | Required mitigation |
|---|---|---|---|
| The page (script integrity) | Names, prices and rates typed by the user or read from storage enter the DOM | HTML or script injection through a name such as `<svg onload=f()>` (person) or `<img src=x onerror=alert(1)>` (item) | R37 text-only DOM writes and the banned-API scan. Icons through `createElementNS` and `<use>` with fixed fragment names, never from markup. R38 CSP `script-src 'self'` as a backstop |
| The page's style integrity (v1.1.0) | The CSSOM writes of R38 | A bill value reaching a style write, or a broad style write that a later change turns into an injection point | R38 allows four targets and measured numbers only, and the scan bans every other style write. The CSP keeps `style-src 'self'`, so no inline style element or attribute markup can apply |
| The bill draft | `localStorage` is untrusted input. On GitHub Pages every project site of the same account shares the `<user>.github.io` origin, so another page of that account can read and write `split.draft` | A malformed or hostile draft crashes the app, renders garbage, pollutes prototypes or loads a partial bill. Since v1.1.0 also a `spare` with an unknown rule, a `personId` not in the bill, or an `order` that drops, repeats or invents an id | D1 to D14 strict decoder, all or nothing, never throws. New objects from known fields only (D12), `spare` included (D13). Any failure gives a new bill and the note (R27) |
| The user's belief that the bill is kept (v1.1.0) | The browser's storage | The browser refuses or fills storage, the bill is lost on close, and the user is never told | R46 and R47 the save warning from the latest save attempt and at boot, the getter re-read. Residual SW8 below |
| Availability | `localStorage` may be disabled, full or throw on access | An exception at boot or on save leaves a blank or frozen page | R28 every storage access guarded, the app keeps working in memory. The app never reads an exception's name or code (R47) |
| Clipboard text the group trusts | The bill flows into the summary text | A name with a line break forges an extra line (for example a fake "Adds up to") | The browser's text input strips CR and LF (measured in 1.0, 4 of 4 ways), so an `<input>` must not become a `<textarea>`. D8 rejects them in stored names. Core `summaryText` (R24) replaces every control, separator and bidi control with a space and writes one line per row |
| Privacy (names and amounts stay on the device) | The page and the network | The bill leaves the device through a request, beacon or third-party script | R39 no network APIs and a request log in every browser run in both engines. R38 CSP `default-src 'none'` (so `connect-src` is none). Zero dependencies and no web fonts (`CLAUDE.md`). The tab icon is a same-origin file, never a `data:` URL and never a CSP change (R45) |
| The human's desktop and data during tests | A headless browser on Windows writes to the real system clipboard (measured in Chromium in 1.0, WebKit treated the same) | A test run replaces, or reads, whatever the human had copied | CG-7 of 1.0. No test ever touches the operating system clipboard. Every context in both engines gets a test-side stand-in for `navigator.clipboard.writeText` and no clipboard permission is granted. The live gate proves the stand-in is not native before its first gesture in each engine |
| Correct shares | UI to `split-core` | The UI recomputes or reformats money on its own and drifts from the core, or draws its own spare sen | Invariant that all money and every draw go through `split-core`. The app passes `Math.random` and nothing else. The suite compares the screen and the clipboard to the core's worked examples |
| The bill, as the user left it | Pointer gestures. A double click, a triple click or a double tap is two or three presses | The first press moves a different control under the pointer and the repeat press lands on it (SEC-01, I-1, RG-CR-01, RG-CR-08 of 1.0). Since v1.1.0 the Splits sheet and P1 open and close under the pointer the same way, so a repeat press could copy from the sheet just opened or shut P1 again | `swallowRepeatClicks` cancels the repeat press and click at the document, armed by every Remove, Add person, Add item and every click that opens or closes M1, the sheet or P1 (R7, R29, R30, R50, R52, PD-21). A Remove also ignores a repeat press itself (`isRepeatClick`). No timer |
| The bill, as the user left it (v1.1.0) | Keyboard auto-repeat | A held Enter on the Remove of the only item removes it, focus moves to Add item, and the key's repeats add a blank item (SEC-04 of 1.0) | R57 the guard also cancels `keydown` events with `repeat` while armed, and ends at the first press that is not a repeat |
| What is published | The static host serves a folder as is | Pointing GitHub Pages at the repository root publishes build records, local paths and mutant copies of `src/` | `CLAUDE.md` Publish, only `index.html`, `src/` and `.nojekyll`, from a publish copy the orchestrator makes at release. `src/icon.svg` is part of `src/` and is meant to be public |

Residual risks accepted, with the reason.
- Another project page under the same `github.io` origin can **read** the draft (names, prices and the spare choice). The data is low in sensitivity, there is no way to isolate it on that host without a custom domain, and the brainstorm keeps one draft in this browser on purpose. The same page can also fill the shared quota, which shows the save warning, the intended behaviour.
- The page can be framed (`frame-ancestors` cannot be set from a meta tag on a static host). The page has no action worth clickjacking beyond starting a new bill, which itself asks for confirmation.
- A name may hold invisible characters that are not separators (U+200B, U+FEFF, U+00A0). They change only the look of the user's own text. Core `summaryText` replaces controls, separators and bidi controls.
- D8 sets no UTF-16 ceiling and D10 allows `nextId` at its edge. Both are 1.0 residuals (code-review WR-04, security SEC-03), unchanged.
- (v1.1.0) Private browsing and Safari's 7-day clean-up lose the bill with no failure the page can see, so the save warning cannot show for them (SW8). Written in the README by the orchestrator.
- (v1.1.0) Safari 26 shows the tab icon in one colour in both themes (WebKit bug 309949). Accepted by the owner, checked in UAT.
- (v1.1.0) `Math.random` is not a secure random source. The draw decides who pays a spare sen, nothing an attacker gains from predicting.
- (v1.1.0) WebKit on Windows is not Safari on an iPhone. Touch gesture timing, the on-screen keyboard and Safari's storage clean-up are covered only by the owner's UAT cases on his iPhone.

## Non-goals
Do NOT build any of the following. Building one is a defect.
- Payments, transfer links or DuitNow QR.
- Accounts, login, sync between devices, sharing links, a share sheet (`navigator.share`), URL parameters that carry a bill.
- Other currencies, currency conversion, other languages.
- Reading the receipt from a photo (OCR).
- A history of past bills, or several bills at once (S9 is a design note only, `docs/future/several-bills.md`).
- 5-sen cash rounding.
- Tips, discounts, vouchers, per-item tax exemptions.
- A theme switcher or a light theme.
- A home-screen icon, an `apple-touch-icon`, a web app manifest or install prompts (deferred, ledger off-scope row 7). Any use of `docs/brand/favicon.svg`.
- A probe write, a read back or a timer for storage, and any detection of private browsing or Safari's 7-day clean-up.
- A spare sen rule besides the three, a split of spare sen typed by hand, a line about spare sen in the copied summary, a seeded random generator in shipped code, or a record of past draws.
- Anything the goldens do not draw and the rulings do not add. That includes a reason hint under a disabled Add person, per-item amounts inside toggles, a stacked bar of the total, undo, toasts, motion beyond `system.md`, a clipboard fallback through `document.execCommand`, a service worker or offline cache, analytics and a "saved" indicator.
- Tab wrapping inside the sheet or P1 (only M1 wraps, R29), a drag on the sheet's grab, or a swipe to close.
- A save on unload, a periodic save, or any timer.
- Any CSS change. `src/system.css` stays a byte copy.
- A WebKit fidelity gate, `is_mobile` in any context, or any hook in the app that makes a test or an engine pass.
