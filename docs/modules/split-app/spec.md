# Module: split-app

> Build contract. Read by the builder. Build ONLY what is here.
> Stack is LOCKED to the project stack (static page, vanilla JavaScript ES modules, plain CSS, zero dependencies, `localStorage` only).
> Depends on `split-core` through its exported functions only (see Contracts).
> Nature is FE. This is the **live-composition module**. It owns the shipped entry point `index.html`, the whole UI, the draft in `localStorage`, the clipboard, the New bill dialog, the fidelity gate and the **cold-boot live-e2e gate**.
> Sources are `docs/brainstorm/brainstorm.md`, `docs/design/RULINGS.md`, `docs/design/system.md`, `docs/design/system.css`, the five screen goldens with their `.md` files, and `docs/design/states.html` with `states.md`.

## Module roadmap
- **Build order.** Second, after `split-core` is green. Inside the module, follow the task order below (shell, people, mode and subtotal, items, charges, panel, copy, draft, dialog, cross-cutting checks, fidelity, live gate).
- **Done when.** Functional QA is green against the running app, the fidelity gate passes on all five screens at both viewports, the element checklist passes, the cold-boot live-e2e gate has its evidence artifact, and the code-review and security finders pass.
- **Clarify gate.** Ruled 2026-10-08 by the orchestrator under the owner's delegation (ORCH). CG-1 to CG-6 were accepted as recommended, and CG-7 (tests never touch the operating system clipboard) was added. CG-8 (a backdrop click acts as Cancel) was added too. **Added 2026-10-08 (re-plan after the plan check).** CG-9 (the R37 payloads), CG-10 (the SVG namespace string in R39, and how the icons are built) and CG-11 (the harness interpreter) were ruled by ORCH. The rulings are recorded in `docs/modules/ROADMAP.md` and marked inline below. Nothing blocks the build.

## Invariants & assumptions
- `split-core` is the only place where money is parsed, computed, allocated or formatted, and the only place that edits a `Bill`. This module never does arithmetic on money and never edits `people` or `items` arrays itself.
- The goldens in `docs/design/` are the truth for markup, classes, copy and look. `src/system.css` is a byte copy of `docs/design/system.css`. No CSS rule is added, removed or changed.
- The page is served as static files from any folder (the target is a GitHub Pages project path such as `/split/`), so every URL in the page is relative.
- Headless Chromium through Python Playwright is the only test browser (CLAUDE.md). Behaviour that differs in other engines is out of scope unless it is named below (the draft name length rule in D8 is the one engine-specific rule).
- Native `<dialog>` with `showModal()` is available in the target browsers (Chromium, WebKit and Gecko since 2022).
- `navigator.clipboard.writeText` exists only in secure contexts. `http://127.0.0.1` and GitHub Pages (https) are secure contexts.

## Requirements

### Shell and boot
- **R1. Entry point.** `index.html` sits at the project root and holds, in this order inside `<head>`, `<meta charset="utf-8">`, `<meta name="viewport" content="width=device-width, initial-scale=1">`, the CSP meta of R38, `<title>Split</title>`, `<link rel="stylesheet" href="src/system.css">` and `<script type="module" src="src/main.js"></script>`. `<html lang="en">`. `src/system.css` is byte-identical to `docs/design/system.css` (equal SHA-256). Every URL in `index.html` and every `import` in `src/` is relative (no leading `/`, no scheme). Loading the page raises no console error and no page error.
- **R2. Cold boot is a new bill, never a seed.** With empty storage the first render is S3 (`bill-empty.html`). Two people with the field values `Person 1` and `Person 2`, both remove buttons disabled, Even checked, an empty Subtotal with no error, Service charge `10`, SST `6`, and a bill panel holding only the Shares heading and "Enter the subtotal to see the shares.". Nothing is written to storage until the first change. `index.html` and every file under `src/` contain none of the golden sample names as whole words (Aisyah, Ben, Chen, Devi, Farid, Grace, Hafiz, Indra, Jia Hui, Kumar, Lina, Mei Ling, Nasi lemak, Char kuey teow, Mee goreng, Satay). There is no demo mode, no fixture, no URL parameter and no global hook (`window.__*`) that fills or exposes the bill.
- **R3. Markup mirrors the goldens.** After every render the DOM follows the DOM contract below. Elements, nesting, class lists, ids, ARIA attributes and copy equal the goldens for the same state. Only the differences listed under "Allowed differences" exist. The test's DOM walk compares rendered markup, so it skips a closed `dialog.dialog` and every element that carries the `hidden` attribute, with everything inside it (allowed difference 7). [Added 2026-10-08, plan check FLAG. The contract keeps the dialog in `body` in every state and lets a block that is not rendered carry `hidden`, while the S1, S2, S3 and S5 goldens have neither.] [Changed 2026-10-09, ORCH: the walk skips by computed `display: none`, see allowed difference 7.]

### People (C1)
- **R4. Person rows.** One `li.field.person` per person in list order. Its input has `type="text"`, `maxlength="20"` (`LIMITS.personNameMax`), `autocomplete="off"`, `aria-label="Person {i} name"` and `placeholder="Person {i}"` ({i} is the 1-based position), and its `value` is the stored name. Its remove button is `button.icon-btn` with `aria-label="Remove {personLabel}"` and the X icon. A blank name shows the placeholder in the field and `Person {i}` everywhere else (ruling 4).
- **R5. Names update live.** On every `input` event in a person's name field, `setPersonName` is applied and, in the same render, the new label shows on that person's toggle in every item, in their shares-table row, and in their remove button's accessible name. The next Copy summary uses it. The same holds for item names, which update their remove button (`Remove {itemLabel}`) and their group name (`Who had {itemLabel}`).
- **R6. Add person.** "Add person" appends a person through `addPerson`. The new field is **empty** and shows the placeholder `Person {i}`. [CG-1 ruled 2026-10-08, ORCH. Accepted as written.] At 12 people the button has the `disabled` attribute and the S8 disabled look (transparent fill, `--line` border, `--ink-disabled` text and plus icon, `not-allowed` cursor, skipped by Tab).
- **R7. Remove person.** A remove button calls `removePerson`, which also takes that person off every item. At 2 people both remove buttons have the `disabled` attribute (borders kept, X in `--ink-disabled`, skipped by Tab).

### Mode and subtotal (C2, C3)
- **R8. Mode switch.** `fieldset.mode` holds two radios, `#mode-even` ("Even") and `#mode-item` ("By item"), with the hidden legend "Split mode". Clicking a label, or an arrow key on the focused radio, calls `setMode`. Even mode renders the Subtotal block and no Items block. By-item mode renders the Items block and no Subtotal block. Both inputs survive any number of switches (the subtotal text, every item, every tap), including after a reload.
- **R9. Subtotal field.** In even mode the Subtotal block holds `input#subtotal` (`type="text"`, `inputmode="decimal"`, `autocomplete="off"`) inside `span.field.money` with the `RM` unit, labelled by `<label for="subtotal">Subtotal<span class="sr-only"> in RM</span></label>` inside `h2#h-subtotal`. Every `input` event calls `setSubtotalText` with the exact text.
- **R10. When an inline error shows.** This rule applies to the subtotal, every item price, Service charge and SST. An error shows only for text that is not empty and fails its parser (`parseAmount`, `parseRate(_, 30)`, `parseRate(_, 20)`). An empty field never shows one (ruling 1). [CG-3 ruled 2026-10-08, ORCH. Accepted as written.] (a) The error appears when the field loses focus holding such text. (b) At boot, a restored field holding such text shows its error at once. (c) While the user types, a shown error disappears as soon as the text becomes valid or empty, and does not come back until the field next loses focus. (d) A field's error state survives a mode switch (it shows again when its block is shown again). When an error shows, the input has `aria-invalid="true"` and its `aria-describedby` starts with the error's id. When no error shows, the input has no `aria-invalid` attribute and the error paragraph is not in the DOM. The bill panel is not affected by this timing. It always follows the current text (R16, R17).

### Items (C3)
- **R11. Item rows.** In by-item mode, one `li.item` per item in list order inside `ol.items`. The name input has `type="text"`, `maxlength="40"` (`LIMITS.itemNameMax`), `autocomplete="off"`, `aria-label="Item {j} name"` and `placeholder="Item {j}"`. The price input sits in `span.field.money` with the `RM` unit and has `type="text"`, `inputmode="decimal"`, `autocomplete="off"` and `aria-label="Item {j} price in RM"`. The remove button is `button.icon-btn` with `aria-label="Remove {itemLabel}"`. `input` events call `setItemName` and `setItemPriceText` with the exact text.
- **R12. Add and remove items.** "Add item" (outline button with the plus icon, after the list) calls `addItem`. The new item has an empty name (placeholder `Item {j}`), an empty price and nobody tapped. At 50 items the button has the `disabled` attribute and the same disabled look as Add person at 12. Any item's remove button calls `removeItem` at any time.
- **R13. Who had it.** Under each item, `div.who` with `role="group"` and `aria-label="Who had {itemLabel}"` holds one `button.tap` per person in people-list order. Its text is the person's label and `aria-pressed` is `"true"` when that person is in the item's `who`, otherwise `"false"`. A click calls `toggleItemPerson`.
- **R14. Price error.** When a price shows its error (R10), `p.error#price-error-{itemId}` with "Enter an amount like 12.50" is the last child of that item's `div.item-line` (after the remove button), so it spans the name and price columns and is right aligned, as in `states.html` S4. The price input has `aria-invalid="true"` and `aria-describedby="price-error-{itemId}"`.

### Charges (C4)
- **R15. Charges block.** `section` with `h2#h-charges` "Charges" holds a `div.cells` with two cells. Each cell has `label.label` and `span.field.percent` with the input and the `%` unit. Service charge is `input#rate-service` labelled "Service charge" + hidden " in percent". SST is `input#rate-sst` labelled "SST" + hidden " in percent". Both inputs have `inputmode="decimal"`, `autocomplete="off"` and `aria-describedby="charges-hint"`, and their values are `serviceText` and `sstText` (`10` and `6` on a new bill). `p.hint#charges-hint` reads "Set a charge to 0 if your bill already includes it.". When a rate shows its error (R10), `p.error` is the last child of its cell, with id `rate-service-error` and "Enter a rate from 0 to 30", or id `rate-sst-error` and "Enter a rate from 0 to 20" (ruling 2). The input then has `aria-invalid="true"` and `aria-describedby="{error id} charges-hint"`. `input` events call `setServiceText` and `setSstText`.

### The bill panel (C2, C3, C5, RULINGS 3)
- **R16. Live, quiet panel.** The panel shows `computeResult(bill)` for the current bill after every change, with no submit button. `div.tape` and its sections carry no `aria-live` and no live-region role. The only live regions on the page are the copy status (R24) and the note (R27).
- **R17. Blocked messages.** For a `blocked` result the panel holds only the Shares section (`h2#h-shares` "Shares" and `p.result-msg`). No Bill summary, no table, no Copy summary, no status. The message is exactly, by reason, `rates` "Check the charges to see the shares.", `subtotal` "Enter the subtotal to see the shares.", `no-items` "Add an item to see the shares.", `prices` "Give every item a price to see the shares.".
- **R18. Items still need a person.** For an `unassigned` result the panel holds the full Bill summary (R19) and then the Shares section with `p.result-msg` and no table, Copy summary or status. The message is "1 item still needs a person. Tap who had it to see the shares." for a count of 1, and "{count} items still need a person. Tap who had each one to see the shares." for 2 or more. No error styling appears on the items or their toggles.
- **R19. Bill summary.** For `unassigned`, `even` and `item` results the first panel section is `h2#h-summary` "Bill summary" then `dl.sum` with four `div.row` in this order. Subtotal (empty `span.op`) with `formatMoney(subtotal)`. Service charge (`span.op` "+") with `formatMoney(service)` and `dd.work` "{formatRate(serviceBp)} of {formatMoney(subtotal)}". SST ("+") with `formatMoney(sst)` and `dd.work` "{formatRate(sstBp)} of {formatMoney(sstBase)}". `div.row.total` Total ("=") with `span.final` holding `formatMoney(total)`. The rows show at 0% too (`0% of RM 100.00`, `RM 0.00`).
- **R20. Shares, even mode.** For an `even` result, the Shares section holds `table.shares` with `thead.sr-only` (Person, Share), one `tbody` row per person (`th[scope=row]` label, `td.share` share) and a `tfoot` row (`th[scope=row]` with the check icon and "Adds up to", `td.share` with `check.share`), then the Copy summary button and `p.status`. With the S2 input the shares are RM 38.87, RM 38.87, RM 38.86 and the check row RM 116.60.
- **R21. Shares, by item.** For an `item` result, the table has a visible `thead` (hidden "Person", "Items", "+ Charges" and "= Share" with `span.op` operators), one row per person with `td` items, `td` charges and `td.share` share, and a `tfoot` row with the check icon, "Adds up to", `check.items`, `check.charges` and `check.share`. People with nothing tapped are listed with RM 0.00 in all three cells. With the S1 input the rows are Aisyah 24.90 / 4.14 / 29.04, Ben 13.50 / 2.24 / 15.74, Chen 21.00 / 3.48 / 24.48 and the check row 59.40 / 9.86 / 69.26.

### Copy summary (C6)
- **R22. Copy works.** Clicking Copy summary calls `navigator.clipboard.writeText(summaryText(computeResult(bill)))`. When the promise resolves, `p.status` reads "Summary copied" with the class list `status` only (ink colour).
- **R23. Copy fails politely.** When `navigator.clipboard` or `writeText` is missing, or the promise rejects, `p.status` reads "Could not copy. Your browser blocked the clipboard." with the class list `status status-failure` (error red). No exception escapes and nothing else changes. There is no fallback copy method.
- **R24. Status lifecycle.** `p.status[role=status]` is empty (and so hidden by `.status:empty`) until a copy is tried. Each attempt replaces the previous text and class. The text stays through later edits while the table stays. When the Shares section switches to a message, the status goes with it, and when the table comes back the status is empty again. The status is not saved in the draft.

### Draft (C7)
- **R25. Save after every change.** After every change to the bill (each `input` event on any field, each click that changes the bill, each mode change, Start new bill), `localStorage` key `split.draft` holds `encodeDraft(bill)`, a JSON text whose parsed value deep-equals `{ "version": 1, "bill": <the Bill> }`. A failed write is ignored (R28). Nothing is saved on unload, and nothing is saved at cold boot.
- **R26. Restore on load.** When the page loads with a readable draft (the decoder accepts it), the screen shows that bill exactly. Every name, the mode, the subtotal text, every item with its name, price text and taps, and both rate texts are as they were, and switching mode shows the other mode's input as it was. Inline errors follow R10 (b).
- **R27. Unreadable draft.** When `split.draft` exists but the decoder rejects it (rules D1 to D12), the app starts `newBill()`, saves it at once (so a reload does not show the note again), and shows the S7 note under the header. `div.note-wrap > div.note[role=status]` holds `<p>Your saved bill could not be read, so a new one was started.</p>` and `button.icon-btn` with `aria-label="Dismiss note"` and the X icon. Dismiss removes the note from the DOM and moves focus to the `Person 1 name` input ("the next control in order", `states.md`). Start new bill does not show, hide or move the note.
- **R28. Storage unavailable.** When reading `window.localStorage` throws, `getItem` throws, or `setItem` throws (for example a quota or security error), the app starts or continues with the bill in memory, works normally for the rest of the session and shows no message. No exception reaches the console.

### New bill (C8)
- **R29. Confirmation dialog opens.** "New bill" in the header opens `dialog.dialog` with `showModal()`. The dialog is the M1 golden: `h2.dialog-title#dialog-title` "Start a new bill?", `p.dialog-text#dialog-text` "This clears the people, items and amounts.", then `div.dialog-actions` with `button.btn.btn-primary.btn-large` "Start new bill" and `button.btn.btn-outline.btn-large` "Cancel", and `aria-labelledby="dialog-title"` and `aria-describedby="dialog-text"`. On open, focus goes to Cancel. Tab from Cancel moves to Start new bill and Shift+Tab from Start new bill moves to Cancel, so focus never leaves the two buttons. (Native `showModal()` alone lets Tab leave to the document. Measured during planning in headless Chromium the order was Cancel, body, Start new bill. So the app wraps Tab itself.) The page behind is inert and does not scroll (`showModal()` plus the `.app` clip rule already in `system.css`).
- **R30. Cancel changes nothing.** Cancel, Esc and a click on the backdrop close the dialog and leave the bill, the draft and the screen unchanged. A backdrop click acts exactly as Cancel, including where focus returns, and the click does not reach the control drawn under it. [Backdrop ruled 2026-10-08, ORCH, CG-8 in `ROADMAP.md`. It follows the design flow check, `docs/design-explore/FLOW-CHECK.md`, where a click at (10, 10) on the backdrop returns to S2.] Native `showModal()` ignores a backdrop click (measured during planning), so the app handles it. A click whose target is the `dialog` element itself and whose point falls outside the dialog's box is a backdrop click. After any close, focus is on "New bill".
- **R31. Start new bill.** Start new bill sets the bill to `newBill()`, saves it, closes the dialog and renders S3 (people `Person 1` and `Person 2`, Even, empty subtotal, 10 and 6, no items). Focus returns to "New bill". All inline errors and the copy status are cleared. [Added 2026-10-08, plan check FLAG. "Cleared" means the view state is reset (`errorShown` and `status`), so a stale flag cannot show an error early on the next bill, and a stale copy status cannot come back when the table returns. Item ids restart at `i3` on a new bill, so a price flag kept by item id would hit a new item.]

### Keyboard, focus, layout, motion (platform rules)
- **R32. Keyboard order and visible focus.** Tab reaches every enabled control in the order the goldens give: New bill, (Dismiss note when shown), each person's name then remove, Add person, the checked mode radio, then in by-item mode each item's name, price, remove and toggles in order, then Add item, or in even mode the Subtotal, then Service charge, SST and Copy summary (when shown). Disabled controls are skipped. Every focused control shows the system ring (2 px ink outline at 2 px offset, drawn on the field wrapper for inputs, inset on the person remove button, the double ring on the mode switch).
- **R33. Typing never loses its place.** The app never replaces, re-creates or moves an input element while it has focus, and never writes the `value` or caret of the input the user is typing in. After every keystroke in any field, the same element still has focus and the caret is where the user put it, including when typing in the middle of the text and during IME composition.
- **R34. Focus after add and remove.** [CG-2 ruled 2026-10-08, ORCH. Accepted as written.] After Add person, focus is on the new person's name input. After Add item, focus is on the new item's name input. After removing the person or item at position k, focus is on the name input now at position k, or at k - 1 when the removed one was last. After removing the last remaining item, focus is on "Add item".
- **R35. Phone first.** At 360 x 780, 390 x 844 and 1280 x 800, for the S1, S2, S3 and S5 states, the page has no horizontal overflow (`document.documentElement.scrollWidth <= window.innerWidth`). The people grid shows 2 columns at 360 and 390 and 3 at 1280. The bill panel sits after the Charges block under 1024 px and in the right column, sticky, at 1024 px and up. **Added 2026-10-08 (plan check FLAG, sizes taken from the design docs).** At 360 x 780 the S2 Subtotal field (`span.field.money`) is 160 px wide (`bill-even.md`), the New bill dialog is 328 px wide with its body (`p.dialog-text`) on two lines (`new-bill-dialog.md`), and the copy failure status (`p.status.status-failure`) wraps onto two centred lines with no horizontal overflow (`states.md`). With the dialog open at 360 x 780 the page still has no horizontal overflow. At 1280 x 800 the content width of the header and of the S7 note is 1040 px (`states.md`: the 1104 px page maximum less two 32 px gutters).
- **R36. Reduced motion.** With `prefers-reduced-motion: reduce`, buttons, toggles, icon buttons and mode labels have a computed `transition-duration` of `0s`. With `no-preference` it is `0.12s, 0.12s` (background-color and color). ~~Nothing on the page animates by itself (`document.getAnimations()` is empty after load and after every interaction).~~ [Changed 2026-10-08, plan check FLAG. That sentence is not true under `no-preference`, because the 120 ms colour transitions of the system are running right after a click. Measured: two CSSTransitions, `background-color` and `color`, and none 400 ms later.] Nothing on the page animates by itself, so `document.getAnimations()` is empty after load in both settings. With `reduce` it is also empty right after every interaction. With `no-preference` every animation present right after a click is a CSSTransition of `background-color` or `color`, and `document.getAnimations()` is empty 500 ms after the click.

### Security
- **R37. Text stays text.** Every name, price text and rate text reaches the DOM only through `textContent`, the `value` property or `setAttribute` on `aria-label` and `placeholder`. Files under `src/` contain none of `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval(`, `new Function(` or `setAttribute("on`. ~~A name such as `<img src=x onerror=alert(1)>` shows as those literal characters in toggles, the table and the clipboard text, and creates no element.~~ [Changed 2026-10-08, plan check BLOCK, CG-9. That payload is 28 characters, and a person name holds at most 20 (R4, D8), so no conformant build can hold it as a person name.] A person name such as `<svg onload=f()>` (16 characters) shows as those literal characters in the field, in every toggle, in the shares row, in the remove button's accessible name (`Remove <svg onload=f()>`) and in the clipboard text. An item name such as `<img src=x onerror=alert(1)>` (28 characters, within the 40 limit) shows as those literal characters in the field, in `Remove {itemLabel}` and in `Who had {itemLabel}`. Neither creates an element. **Added 2026-10-08 (CG-10).** The scan also finds none of `createContextualFragment` or `DOMParser` in `src/`, and no `<template` in `index.html` or `src/`. The icons are built with `createElementNS` (see the DOM contract and R39), never by cloning a `<template>`.
- **R38. Content Security Policy.** `index.html` carries exactly `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; base-uri 'none'; form-action 'none'">`. No inline script, inline style attribute or `<style>` element exists in `index.html` or is created by `src/`. No CSP violation is logged during any functional scenario or the live gate, and neither of them uses `bypass_csp`, so the shipped policy is live in both. [Changed twice on 2026-10-08, ORCH. The plan first had `style-src 'self'`. It was relaxed to `style-src 'self' 'unsafe-inline'` because harness 2.1.1 injected its freeze stylesheet into the candidate and exited with a CSP error under the strict policy (measured). Harness 2.1.2 renders with Playwright `bypass_csp`, so the strict policy is restored. The fidelity gate therefore never sees the policy, and the functional suite and the live gate are what catch policy breakage.]
- **R39. Nothing leaves the device.** Files under `src/` contain none of `fetch(`, `XMLHttpRequest`, `WebSocket`, `EventSource`, `sendBeacon`, `serviceWorker` or a URL with a scheme. **One exemption, ruled 2026-10-08 (CG-10, plan check BLOCK).** The exact namespace string `http://www.w3.org/2000/svg` is allowed when it is the first argument of a `createElementNS` call, because that is how the icons are built (see the DOM contract). The scan allows only that. No other string with a scheme is allowed, not even another namespace, and the namespace string is allowed nowhere else. It is a name that is never requested, not a URL. There is no `<template>` cloning and no `innerHTML` (R37). During every browser test run the only requests are same-origin GETs for the page, `src/system.css`, files under `src/` and the browser's own `/favicon.ico`.

### Gates
- **R40. Looks right.** The fidelity gate in `qa.md` passes for `bill-empty`, `bill-even`, `bill-items`, `bill-unassigned` and `new-bill-dialog` at 390 x 844 and 1280 x 800, and every row of the FE element checklist passes.
- **R41. Works right.** The cold-boot live-e2e gate in `qa.md` passes and leaves its evidence artifact. No artifact means not done.

### Names (C1, added 2026-10-08 after the plan check)
- **R42. Duplicate names are allowed.** The brainstorm rule "Duplicate names are allowed" had no requirement. Typing a name equal to another person's (exactly, after trimming, or differing only in letter case) is accepted. There is no error, no note, no merge and no warning, and the draft saves both people. Each row keeps its own toggles, shares row and remove button. Two people called "Ben" give two `Remove Ben` buttons with the same accessible name, and each acts on its own row only. The shares table and the copied text hold one line per person, so "Ben" appears twice.

## Contracts

### Files
| File | Owns |
|---|---|
| `index.html` (project root) | The shipped entry point (R1, R38). The static shell may hold the parts that never change (header, the fixed headings, the mode fieldset, the Charges block, the dialog), or `src/main.js` may build them. Either way the result is the DOM contract. |
| `src/system.css` | Byte copy of `docs/design/system.css`. Never edited. |
| `src/main.js` | Boot (storage, draft load, note, first render) and event wiring. Holds the one `bill` value and the view state, and calls `split-core` actions. |
| `src/draft.js` | `DRAFT_KEY`, `encodeDraft`, `decodeDraft`, `getStorage`, `loadDraft`, `saveDraft` (R25 to R28). Pure apart from the storage object passed in. |
| `src/ui/*.js` | Rendering, one file per block where that keeps each file single-purpose (people, mode and subtotal, items, charges, panel, copy, note, dialog, icons, where icons builds the four SVGs with `createElementNS`, CG-10). Names are the builder's choice. |
| `tests/browser/` | Python Playwright tests (`conftest.py`, `seeds.py`, `test_app.py`), the clipboard init scripts (`clipboard/`), the fidelity setup scripts and runner (`fidelity/`) and the live gate (`live_e2e.py`). Test-side only, never loaded by `index.html`. Seed drafts live here and nowhere under `src/`. |

### Imports from split-core (the only cross-module surface)
`LIMITS`, `newBill`, `addPerson`, `removePerson`, `setPersonName`, `setMode`, `setSubtotalText`, `setServiceText`, `setSstText`, `addItem`, `removeItem`, `setItemName`, `setItemPriceText`, `toggleItemPerson`, `personLabel`, `itemLabel` from `src/core/bill.js`. `parseAmount`, `parseRate`, `formatMoney`, `formatRate` from `src/core/money.js`. `computeResult` from `src/core/result.js`. `summaryText` from `src/core/summary.js`. Types are as declared in `split-core/spec.md`.

### Gesture to action
| Gesture | Effect |
|---|---|
| `input` on Person {i} name | `setPersonName`, save, render (R5) |
| click Remove {personLabel} | `removePerson`, save, render, focus (R7, R34) |
| click Add person | `addPerson`, save, render, focus (R6, R34) |
| `change` on a mode radio | `setMode`, save, render (R8) |
| `input` on Subtotal | `setSubtotalText`, save, render, error rule (R9, R10) |
| `input` on Item {j} name or price | `setItemName` or `setItemPriceText`, save, render (R11, R10) |
| click Remove {itemLabel} | `removeItem`, save, render, focus (R12, R34) |
| click a toggle | `toggleItemPerson`, save, render (R13) |
| click Add item | `addItem`, save, render, focus (R12, R34) |
| `input` on Service charge or SST | `setServiceText` or `setSstText`, save, render, error rule (R15, R10) |
| focus leaves an amount or rate field | error rule (a) of R10, no save (the bill did not change) |
| click Copy summary | clipboard and status (R22 to R24), no save |
| click New bill | open the dialog (R29) |
| click Start new bill | `newBill()`, save, close, render (R31) |
| click Cancel, Esc, click the backdrop | close, nothing else changes (R30) |
| click Dismiss note | remove the note, focus Person 1 name (R27) |

### View state (in memory only, never saved)
`{ errorShown: { subtotal: boolean, service: boolean, sst: boolean, price: { [itemId]: boolean } }, noteShown: boolean, status: null | "ok" | "fail" }`. At boot `errorShown` is set from the restored texts (R10 b). Start new bill resets `errorShown` and `status` (R31).

### DOM contract
Braces are filled at render time. `{i}` and `{j}` are 1-based positions. `{personLabel}` and `{itemLabel}` come from `personLabel` and `itemLabel`. `[...]` marks a conditional attribute or element. Icons are the four Phosphor SVGs copied byte for byte from the goldens (X from any remove button, Plus from Add person, Copy from Copy summary, Check from the check row), each `<svg class="ph" viewBox="0 0 256 256" aria-hidden="true" focusable="false"><path d="..."/></svg>`. **Added 2026-10-08 (CG-10).** The icons are built at run time with `document.createElementNS("http://www.w3.org/2000/svg", "svg")` and `"path"`, then `setAttribute` for `class`, `viewBox`, `aria-hidden`, `focusable` and `d`. The `d` strings are constants copied from the goldens, so these attributes hold no user text and R37 is not touched. The result is the same DOM as the golden's parsed SVG, so it needs no allowed difference. Not allowed: cloning a `<template>` or a hidden static icon from `index.html`, `innerHTML`, `insertAdjacentHTML`, `createContextualFragment` and `DOMParser`.

```html
<body>
<div class="app">
  <header class="bar">
    <h1 class="wordmark">Split</h1>
    <button class="btn btn-outline" type="button">New bill</button>
  </header>
  [R27 only]
  <div class="note-wrap">
    <div class="note" role="status">
      <p>Your saved bill could not be read, so a new one was started.</p>
      <button class="icon-btn" type="button" aria-label="Dismiss note">{X}</button>
    </div>
  </div>
  <main class="layout">
    <div class="inputs">
      <section class="block" aria-labelledby="h-people">
        <h2 class="block-title" id="h-people">People</h2>
        <ul class="cells">
          [one per person]
          <li class="field person">
            <input type="text" maxlength="20" autocomplete="off" aria-label="Person {i} name" placeholder="Person {i}">   value = person.name
            <button class="icon-btn" type="button" aria-label="Remove {personLabel}" [disabled at 2 people]>{X}</button>
          </li>
          <li><button class="btn btn-outline" type="button" [disabled at 12 people]>{Plus}Add person</button></li>
        </ul>
      </section>
      <fieldset class="mode">
        <legend class="sr-only">Split mode</legend>
        <input type="radio" name="mode" id="mode-even" value="even" [checked in even mode]>
        <label for="mode-even">Even</label>
        <input type="radio" name="mode" id="mode-item" value="item" [checked in by-item mode]>
        <label for="mode-item">By item</label>
      </fieldset>
      [even mode only]
      <section class="block" aria-labelledby="h-subtotal">
        <h2 class="block-title" id="h-subtotal"><label for="subtotal">Subtotal<span class="sr-only"> in RM</span></label></h2>
        <div class="cells">
          <span class="field money"><span class="unit" aria-hidden="true">RM</span><input id="subtotal" type="text" inputmode="decimal" autocomplete="off" [aria-invalid="true" aria-describedby="subtotal-error"]></span>
        </div>
        [error shown] <p class="error" id="subtotal-error">Enter an amount like 12.50</p>
      </section>
      [by-item mode only]
      <section class="block" aria-labelledby="h-items">
        <h2 class="block-title" id="h-items">Items</h2>
        <ol class="items">
          [one per item]
          <li class="item">
            <div class="item-line">
              <span class="field"><input type="text" maxlength="40" autocomplete="off" aria-label="Item {j} name" placeholder="Item {j}"></span>
              <span class="field money"><span class="unit" aria-hidden="true">RM</span><input type="text" inputmode="decimal" autocomplete="off" aria-label="Item {j} price in RM" [aria-invalid="true" aria-describedby="price-error-{itemId}"]></span>
              <button class="icon-btn" type="button" aria-label="Remove {itemLabel}">{X}</button>
              [error shown] <p class="error" id="price-error-{itemId}">Enter an amount like 12.50</p>
            </div>
            <div class="who" role="group" aria-label="Who had {itemLabel}">
              [one per person] <button class="tap" type="button" aria-pressed="{true|false}">{personLabel}</button>
            </div>
          </li>
        </ol>
        <button class="btn btn-outline" type="button" [disabled at 50 items]>{Plus}Add item</button>
      </section>
      <section class="block" aria-labelledby="h-charges">
        <h2 class="block-title" id="h-charges">Charges</h2>
        <div class="cells">
          <div>
            <label class="label" for="rate-service">Service charge<span class="sr-only"> in percent</span></label>
            <span class="field percent"><input id="rate-service" type="text" inputmode="decimal" autocomplete="off" aria-describedby="charges-hint" [error: aria-invalid="true" aria-describedby="rate-service-error charges-hint"]><span class="unit" aria-hidden="true">%</span></span>
            [error shown] <p class="error" id="rate-service-error">Enter a rate from 0 to 30</p>
          </div>
          <div>
            <label class="label" for="rate-sst">SST<span class="sr-only"> in percent</span></label>
            <span class="field percent"><input id="rate-sst" type="text" inputmode="decimal" autocomplete="off" aria-describedby="charges-hint" [error: aria-invalid="true" aria-describedby="rate-sst-error charges-hint"]><span class="unit" aria-hidden="true">%</span></span>
            [error shown] <p class="error" id="rate-sst-error">Enter a rate from 0 to 20</p>
          </div>
        </div>
        <p class="hint" id="charges-hint">Set a charge to 0 if your bill already includes it.</p>
      </section>
    </div>
    <div class="tape">
      [unassigned, even, item]
      <section class="tape-section" aria-labelledby="h-summary">
        <h2 class="tape-title" id="h-summary">Bill summary</h2>
        <dl class="sum">
          <div class="row"><dt><span class="op" aria-hidden="true"></span>Subtotal</dt><dd class="amt">{subtotal}</dd></div>
          <div class="row"><dt><span class="op" aria-hidden="true">+</span>Service charge</dt><dd class="amt">{service}</dd><dd class="work">{serviceRate} of {subtotal}</dd></div>
          <div class="row"><dt><span class="op" aria-hidden="true">+</span>SST</dt><dd class="amt">{sst}</dd><dd class="work">{sstRate} of {sstBase}</dd></div>
          <div class="row total"><dt><span class="op" aria-hidden="true">=</span>Total</dt><dd class="amt"><span class="final">{total}</span></dd></div>
        </dl>
      </section>
      <section class="tape-section" aria-labelledby="h-shares">
        <h2 class="tape-title" id="h-shares">Shares</h2>
        [blocked, unassigned] <p class="result-msg">{message}</p>
        [even]
        <table class="shares" aria-labelledby="h-shares">
          <thead class="sr-only"><tr><th scope="col">Person</th><th scope="col">Share</th></tr></thead>
          <tbody>[per person] <tr><th scope="row">{personLabel}</th><td class="share">{share}</td></tr></tbody>
          <tfoot><tr><th scope="row">{Check}Adds up to</th><td class="share">{check.share}</td></tr></tfoot>
        </table>
        [item]
        <table class="shares" aria-labelledby="h-shares">
          <thead><tr>
            <th scope="col"><span class="sr-only">Person</span></th>
            <th scope="col">Items</th>
            <th scope="col"><span class="op" aria-hidden="true">+</span>Charges</th>
            <th scope="col"><span class="op" aria-hidden="true">=</span>Share</th>
          </tr></thead>
          <tbody>[per person] <tr><th scope="row">{personLabel}</th><td>{items}</td><td>{charges}</td><td class="share">{share}</td></tr></tbody>
          <tfoot><tr><th scope="row">{Check}Adds up to</th><td>{check.items}</td><td>{check.charges}</td><td class="share">{check.share}</td></tr></tfoot>
        </table>
        [even, item]
        <button class="btn btn-primary btn-large btn-block copy" type="button">{Copy}Copy summary</button>
        <p class="status [status-failure]" role="status">{status text or empty}</p>
      </section>
    </div>
  </main>
</div>
<dialog class="dialog" aria-labelledby="dialog-title" aria-describedby="dialog-text">
  <h2 class="dialog-title" id="dialog-title">Start a new bill?</h2>
  <p class="dialog-text" id="dialog-text">This clears the people, items and amounts.</p>
  <div class="dialog-actions">
    <button class="btn btn-primary btn-large" type="button">Start new bill</button>
    <button class="btn btn-outline btn-large" type="button">Cancel</button>
  </div>
</dialog>
</body>
```

All money in the panel is `formatMoney`, all rates `formatRate`. A block that is not rendered is either absent or carries the `hidden` attribute.

### Allowed differences from the goldens
These are invisible and are the only ones allowed. Anything else is a fidelity finding.
1. Inputs carry their value as the `value` property, not a `value` attribute.
2. Person and item name inputs always carry `placeholder` (ruling 4). It renders nothing while the field holds text.
3. `<head>` links `src/system.css` and `src/main.js` and carries the CSP meta, instead of the golden's inline `<style>`.
4. The dialog is opened with `showModal()` and its scrim is `dialog::backdrop`. The golden's static `div.backdrop`, its `open` attribute in the markup and `inert` on `.app` are stand-ins for a static file and do not exist in the app.
5. White-space text nodes between elements may differ where they do not render (flex and grid containers, before an absolutely positioned icon).
6. The specimen-only markup of `states.html` (frames, captions, `h3` headings, the `s4-` and `s7-` id prefixes, the `p.wordmark` in S7) is not app markup. The app uses the screen goldens' `h1` and `h2`.
7. **Added 2026-10-08.** A closed `dialog.dialog` and any element with the `hidden` attribute are not rendered, so the R3 DOM walk skips them and what is inside them. It still compares every rendered element.
   **Changed 2026-10-09 (plan re-check FLAG 5, ORCH).** The sentence above is false where `system.css` gives a class a `display` value, which overrides the browser's own `[hidden]` rule (measured: `button.copy`, `ul.cells` and `span.field` stay visible with `hidden`). Ruling: `src/system.css` ends with `[hidden] { display: none !important; }` (invisible in every golden state, since no golden element carries `hidden`), and the R3 walk skips every element whose computed `display` is `none`, plus a closed `dialog.dialog`.

### Copy (every UI string, exact)
| Where | Copy |
|---|---|
| Document title, wordmark | Split |
| Header button | New bill |
| Headings | People, Items, Subtotal, Charges, Bill summary, Shares |
| Hidden label endings | " in RM" (Subtotal), " in percent" (both rates) |
| Mode switch | Even, By item, hidden legend "Split mode" |
| Buttons | Add person, Add item, Copy summary |
| Person field | aria-label "Person {i} name", placeholder "Person {i}", remove "Remove {personLabel}" |
| Item fields | aria-label "Item {j} name" and "Item {j} price in RM", placeholder "Item {j}", remove "Remove {itemLabel}", group "Who had {itemLabel}" |
| Rate labels | Service charge, SST |
| Hint | Set a charge to 0 if your bill already includes it. |
| Amount error | Enter an amount like 12.50 |
| Rate errors | Enter a rate from 0 to 30 (service), Enter a rate from 0 to 20 (SST) |
| Summary labels | Subtotal, Service charge, SST, Total |
| Working lines | {rate} of {money}, for example "10% of RM 59.40" |
| Table heads | by item "Person" (hidden), "Items", "Charges" after "+", "Share" after "=". Even "Person" and "Share", both hidden |
| Check row | Adds up to |
| Panel messages | Check the charges to see the shares. · Enter the subtotal to see the shares. · Add an item to see the shares. · Give every item a price to see the shares. · 1 item still needs a person. Tap who had it to see the shares. · {count} items still need a person. Tap who had each one to see the shares. |
| Copy status | Summary copied · Could not copy. Your browser blocked the clipboard. |
| Note | Your saved bill could not be read, so a new one was started. Dismiss button "Dismiss note" |
| Dialog | Start a new bill? · This clears the people, items and amounts. · Start new bill · Cancel |

### Persistence
- **Key.** `split.draft` in `window.localStorage`. Nothing else is stored anywhere.
- **Envelope (version 1).** `{ "version": 1, "bill": Bill }` with `Bill` exactly as typed in `split-core/spec.md`. Example (the S2 bill):

  ```json
  {"version":1,"bill":{"mode":"even","people":[{"id":"p1","name":"Aisyah"},{"id":"p2","name":"Ben"},{"id":"p3","name":"Chen"}],"subtotalText":"100.00","items":[],"serviceText":"10","sstText":"6","nextId":4}}
  ```
- **`src/draft.js` functions.**

  | Signature | Behaviour |
  |---|---|
  | `DRAFT_KEY = "split.draft"` | the key |
  | `encodeDraft(bill: Bill): string` | `JSON.stringify({ version: 1, bill })` |
  | `decodeDraft(text: string): { ok: true, bill: Bill } \| { ok: false }` | applies D1 to D12, never throws |
  | `getStorage(): Storage \| null` | `window.localStorage`, or `null` when reading it throws |
  | `loadDraft(storage: Storage \| null): { state: "none" } \| { state: "ok", bill: Bill } \| { state: "unreadable" }` | `none` when storage is null, `getItem` throws or returns null. Otherwise the decoder decides |
  | `saveDraft(storage: Storage \| null, bill: Bill): boolean` | `setItem(DRAFT_KEY, encodeDraft(bill))`, `false` on null storage or any exception |
- **Decoder rules.** A draft is readable only when all of these hold. Any failure gives `{ ok: false }`.
  - **D1.** The text parses with `JSON.parse` (no reviver).
  - **D2.** The parsed value is a plain object (not `null`, not an array).
  - **D3.** `version` is exactly the number `1`.
  - **D4.** `bill` is a plain object.
  - **D5.** `bill.mode` is `"even"` or `"item"`.
  - **D6.** `bill.people` is an array of 2 to 12 plain objects. Each has `id`, a string matching `^p[0-9]{1,10}$`, and `name`, a string. Person ids are unique.
  - **D7.** `bill.items` is an array of 0 to 50 plain objects. Each has `id` matching `^i[0-9]{1,10}$`, `name` a string, `priceText` a string and `who` an array of strings. Item ids are unique. Every `who` entry is the id of a person in this bill, with no repeats inside one `who`.
  - **D8.** A person name has at most 20 and an item name at most 40 grapheme clusters, counted with `Intl.Segmenter` (granularity `grapheme`). No name contains U+000A or U+000D. (Grapheme clusters, because WebKit counts `maxlength` in grapheme clusters and Chromium in UTF-16 code units, and a name either engine let the user type must reload.)
  - **D9.** `subtotalText`, `serviceText` and `sstText` are strings.
  - **D10.** `nextId` is an integer from 1 to 1,000,000,000 and greater than the number in every person and item id.
  - **D11.** Unknown keys anywhere are ignored and are not carried into the decoded bill.
  - **D12.** The decoded `Bill` is built as new objects from the known fields only. Parsed objects are never copied wholesale (no spread, no `Object.assign`).

## Tasks
Each task is one commit and adds the browser tests for the R#s it cites (see `qa.md`). Every task ends with the functional suite green. Commit only with the human's go-ahead per the pipeline.
1. [x] `tests/browser/conftest.py` harness (free port, `python -m http.server <port> --bind 127.0.0.1` from the project root, bounded readiness wait, teardown with kill and port re-check, evidence folders, console and network capture, the clipboard init scripts `tests/browser/clipboard/recorder.js`, `reject.js` and `missing.js` with the recorder on every context by default) and `tests/browser/seeds.py` (the seed drafts). -> R1, R39
2. [x] `index.html` with the CSP meta, `src/system.css` byte copy, `src/main.js` boot that renders header, People, mode switch, Subtotal, Charges and the blocked panel from `newBill()`. -> R1, R2, R3, R38
3. [x] People block. Rows, live names, add, remove, limits, focus after add and remove, duplicate names, and the icons module (the four SVGs through `createElementNS`, CG-10). -> R4, R5, R6, R7, R33, R34, R42
4. [x] Mode switch and Subtotal block with the inline error rule. -> R8, R9, R10
5. [x] Items block. Rows, toggles, add, remove, 50 limit, price errors, focus. -> R11, R12, R13, R14, R10, R34
6. [x] Charges block with rate errors. -> R15, R10
7. [x] Bill panel. Blocked messages, unassigned message, Bill summary, both shares tables, quiet panel. -> R16, R17, R18, R19, R20, R21
8. [x] Copy summary and status. -> R22, R23, R24
9. [x] `src/draft.js` and boot wiring. Save, restore, unreadable note with dismiss, storage failures. -> R25, R26, R27, R28
10. [ ] New bill dialog. -> R29, R30, R31
11. [ ] Cross-cutting browser checks. Keyboard order and rings, typing keeps focus, layout at three viewports and the measured 360 and 1280 sizes, reduced motion, injection, static source scans, network log. -> R32, R33, R35, R36, R37, R39
12. [ ] `tests/browser/fidelity/` setup scripts (`seed-s1.js`, `seed-s2.js`, `seed-s5.js`, `open-new-bill.js`) and `run.py` (server lifecycle around the unmodified sdlc harness `fidelity.py`, started with `sys.executable`, CG-11), and a passing run with evidence. -> R40
13. [ ] `tests/browser/live_e2e.py` cold-boot gate and a passing run with evidence. -> R41

## Threat model
| Asset | Trust boundary | Threat | Required mitigation |
|---|---|---|---|
| The page (script integrity) | Names, prices and rates typed by the user or read from storage enter the DOM | HTML or script injection through a name such as `<svg onload=f()>` (person) or `<img src=x onerror=alert(1)>` (item) | R37 text-only DOM writes and the banned-API scan (the SVG icons are built with `createElementNS`, never from markup, CG-10). R38 CSP `script-src 'self'` as a backstop. |
| The bill draft | `localStorage` is untrusted input. On GitHub Pages every project site of the same account shares the `<user>.github.io` origin, so another page of that account can read and write `split.draft` | A malformed or hostile draft crashes the app, renders garbage, pollutes prototypes or loads a partial bill | D1 to D12 strict decoder, all or nothing, never throws. New objects from known fields only (D12). Any failure gives a new bill and the S7 note (R27). |
| Availability | `localStorage` may be disabled, full or throw on access | An exception at boot or on save leaves a blank or frozen page | R28 every storage access guarded. The app keeps working in memory. |
| Clipboard text the group trusts | The bill flows into the summary text | A name with a line break forges an extra line (for example a fake "Adds up to") | Inputs strip CR and LF. D8 rejects them in stored names. `summaryText` (split-core R24) writes one line per row. |
| Privacy (names and amounts stay on the device) | The page and the network | The bill leaves the device through a request, beacon or third-party script | R39 no network APIs and a request log in every browser run. R38 CSP `default-src 'none'` (so `connect-src` is none). Zero dependencies and no web fonts (CLAUDE.md). |
| The human's desktop and data during tests | Headless Chromium on Windows writes to the real system clipboard (measured during planning) | A test run replaces, or reads, whatever the human had copied | CG-7 (ruled 2026-10-08, ORCH). No test ever touches the operating system clipboard, not even to read it. Every browser context gets a test-side init script that replaces `navigator.clipboard.writeText` with a recorder (or a rejecting stub for the failure path), and no clipboard permission is ever granted. |
| Correct shares | UI to `split-core` | The UI recomputes or reformats money on its own and drifts from the core | Invariant that all money goes through `split-core`. The fidelity and functional checks compare the screen to the core's worked examples. |

Residual risks accepted, with the reason.
- Another project page under the same `github.io` origin can **read** the draft (names and restaurant prices). The data is low in sensitivity, there is no way to isolate it on that host without a custom domain, and the brainstorm keeps one draft in this browser on purpose.
- The page can be framed (`frame-ancestors` cannot be set from a meta tag on a static host). The page has no action worth clickjacking beyond starting a new bill, which itself asks for confirmation.
- A name may hold U+2028 or other invisible characters pasted by the user. Only the user can type them, and they affect only the user's own clipboard text.

## Non-goals
Do NOT build any of the following. Building one is a defect.
- Payments, transfer links or DuitNow QR.
- Accounts, login, sync between devices, sharing links, a share sheet (`navigator.share`), URL parameters that carry a bill.
- Other currencies, currency conversion, other languages.
- Reading the receipt from a photo (OCR).
- A history of past bills. One draft only.
- 5-sen cash rounding.
- Tips, discounts, vouchers, per-item tax exemptions.
- A theme switcher or a dark theme.
- Anything the goldens do not draw and the rulings do not add. That includes a reason hint under a disabled Add person, marking which item still needs a person, per-item amounts inside toggles, a stacked bar of the total, undo, toasts, animations, a clipboard fallback through `document.execCommand`, a service worker or offline cache, a favicon, analytics, and a "saved" indicator.
- A save on unload, a periodic save, or any timer.
- Any CSS change. `src/system.css` stays a byte copy.
