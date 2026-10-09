---
module: split-app
kind: security
status: clean
counts: { critical: 0, high: 0, medium: 0, low: 0 }
---
# Security audit: split-app

Role: security finder (read-only on the product). Date: 2026-10-09. Repository head `5ef85cf`, code under audit `61c3cd3` (`src/` and `index.html` are identical at both).
Judged against `spec.md` (R37 to R39, R25 to R30, the DOM contract, Persistence D1 to D12, the Threat model and its accepted residuals), `CLAUDE.md`, the constitution, `findings/qa.md` and `findings/code-review.md`. `split-core` internals were not re-audited.
Evidence: `docs/modules/split-app/qa/security/20261009-201702/` (`evidence.md` indexes 18 scripts, 14 result files with 484 rows, and the printed outputs).
Baseline run first: `python -m pytest tests/browser -q` gave 244 passed (92 s), `node --test "tests/**/*.test.js"` gave 275 pass, 0 fail.

## Verdict
**ISSUES FOUND. 0 CRITICAL, 0 HIGH, 1 MEDIUM, 2 LOW.** No exploitable vulnerability. All seven threat-model rows and R37 to R39 held under hostile input in the running app, with the shipped policy live and no `bypass_csp`.
The one MEDIUM is the ghost-click class again, on a control the two earlier fixes did not reach: a double click or double tap on the Remove button of the **last person** removes that person and then presses **Add person**, which has slid under the pointer, so a blank person is added and saved (SEC-01). Every other control in the sweep behaves as a single click does, and the `swallowRepeatClicks` guard swallowed nothing deliberate (audit item 3). The two LOWs are the publish scope (SEC-02) and a boundary in D10 where the app saves a draft its own decoder rejects (SEC-03).

## CRITICAL
None.

## HIGH
None.

## MEDIUM

### SEC-01: A double click or double tap on Remove of the last person adds a blank person   (ghost click, same class as CR-01 and WR-01)
- **Severity:** MEDIUM. **File:** `src/ui/people.js:17` (the Remove handler ignores a repeat click only when it lands on a Remove button) and `src/ui/people.js:22` (`add.addEventListener("click", onAdd)` has no such test); `src/main.js:65` (`onRemove`). **Boundary:** pointer gesture, entry `button.icon-btn[aria-label="Remove {name}"]` of the last row, sink `addPerson` through the Add person button and then `saveDraft`.
- **Maps to spec threat:** NEW, not in the threat model. R7 (WR-01 note) guards a repeat click on a Remove button and R30 (CR-01 note) guards the dialog close. Neither covers a repeat click that lands on a different control.
- **Repro (all three viewports, mouse and touch):**
  1. Serve the project root. Open a context at 390 x 844 (also 360 x 640 and 1280 x 800) with the S2 draft in `split.draft`: `{"version":1,"bill":{"mode":"even","people":[{"id":"p1","name":"Aisyah"},{"id":"p2","name":"Ben"},{"id":"p3","name":"Chen"}],"subtotalText":"100.00","items":[],"serviceText":"10","sstText":"6","nextId":4}}`. A cold boot with one Add person click gives the same layout.
  2. Double click (`page.mouse.dblclick`) the centre of `Remove Chen`, the last person's remove button. Touch: two `page.touchscreen.tap` at the same point (360 x 640 and 390 x 844). A triple click gives the same result.
  3. A single click leaves `[Aisyah, Ben]` and shares RM 58.30, RM 58.30. The double click leaves `[Aisyah (p1), Ben (p2), "" (p4)]` with `nextId` 5 and shares Aisyah RM 38.87, Ben RM 38.87, **Person 3** RM 38.86. The removal looks undone, Chen's name is gone, and the new row is saved.
- **Why:** removing the last row of the 2-column (3-column at 1280) people grid moves the Add person cell into the cell the removed row filled, and the Add person button spans that cell, so the pointer is over it for the second click. The click log of the sweep: `click:1 button.icon-btn [Remove P4]`, then `click:2 button.btn.btn-outline` (Add person), `reached` the page. With a triple click the third click lands on the new row's Remove button and is ignored by the WR-01 test, so the blank row stays.
- **Storage and measurement:** the saved draft gains a person with an empty name and `nextId` + 1. 16 of 16 rows add a blank person (S2 with 3 people and S8 with 12 people, each at 3 sizes, double click and triple click, and a double tap at the two phone sizes; `p9_sec01_repro.py`). The sweep gives 8 of 8 for the last of 4 and the last of 5 people (`p6_ghost_sweep.py`), and an invalid-price variant gives the same for 3 people (`p6b_layout_scan.py`, part B, 2 of 2). Removing a **middle** person, a middle item, the last item or the only item shows no data change: the second press lands on the next row's Remove button (ignored) or on inert space. At 12 people the Add person button is disabled before the removal and enabled after it, and the double click still adds (S8, 8 of 8).
- **Impact:** an unrequested change that is saved at once, with no undo (a non-goal). In Even mode the split silently runs over one more person. In By item mode a blank person is listed with RM 0.00. No money is lost beyond the row the user meant to remove, and one single click on the blank row's Remove undoes it, so MEDIUM and not HIGH.
- **Fix (preferred, verified in memory):** move `swallowRepeatClicks` from `src/ui/dialog.js` into `src/ui/dom.js`, export it, and call it from the Remove click handlers in `people.js` and `items.js` in place of the `isRepeatClick(event)` test: `remove.addEventListener("click", () => { swallowRepeatClicks(); onRemove(id); })`. The repeat press is then cancelled at the document whatever slid under it. `p10_fix_check.py` served that change from memory (no project file written): 16 of 16 repro rows give one removal, a double click on a middle Remove still removes one row, two separate clicks remove two, Enter removes one, Add person adds one on a single and on a double click, a double click on Cancel changes nothing, and focus ends on the name field after a double click on a middle Remove (today it ends on the next Remove button or on the body). Narrow alternative: `add.addEventListener("click", (event) => { if (!isRepeatClick(event)) onAdd(); })` in `people.js:22` (and `items.js:40` for symmetry): 16 of 16 and the same 7 regression checks pass, the focus drift stays.
- **Tests to add:** S2 and S8 at 360 x 640, 390 x 844 and 1280 x 800, double click, triple click and (phones) double tap on the last person's Remove, expecting one person fewer and no blank row. The existing `REMOVE_CASES` use P2 of 5 and item 2 of 4 only.

## LOW

### SEC-02: The publish scope is undefined, and "serves the folder as is" would publish the whole repository
- **Severity:** LOW. **File:** `CLAUDE.md` (Stack: "the target host is GitHub Pages, which serves the folder as is", no Publish section) and `spec.md` Invariants. **Boundary:** the repository root served as a static site.
- **Maps to spec threat:** NEW. The trust boundary "what is published" has no row. The Streaks example filed the same gap as SEC-04 (LOW) and fixed it with a Publish section.
- **Measurement (`p8_publish_scope.py`):** 3,108 tracked files, 22 of them the app (`index.html` and 21 files under `src/`). The other 3,086 would be public from the same origin: `docs/` (36 MB, 142 PNG screenshots, run logs), `tests/`, `CLAUDE.md`, `.claude/settings.json` (hook commands), `.gitignore`. Of these, **875 are copies of `src/` modules in 178 folders** under `docs/modules/split-core/qa/` (deliberate mutants `M..` and `S..`, and `commits/*`), each served as `text/javascript`; **143 text files hold an absolute local path** (`{home}/...` scratch paths in the code-review scripts, `{workspace}/...`, `{plugins}/...`); 7 exploration pages (`docs/design-explore/prototype/*.html`, `round-1/a.html`, `round-1/compare.html`) carry inline scripts. A loopback server on the root returned 200 for `/CLAUDE.md`, `/docs/constitution.md`, `/docs/modules/split-app/spec.md`, `/.claude/settings.json`, `/tests/browser/rig.py`, a mutant `money.js` and a `run.log`. The dev command in `CLAUDE.md` (`python -m http.server`) also lists directories and serves `.git/` on loopback; Pages does not serve `.git/`.
- **Threat:** information disclosure (user name, directory layout, build records) and a weaker CSP backstop: R38 relies on `script-src 'self'`, and with a root deployment `'self'` includes 875 stale or mutated copies of the app's own modules. Without `.nojekyll`, Pages also runs Jekyll over the markdown files that carry front matter (the findings files), and a double opening brace or a brace and percent pair in one of them breaks the publish build (none today).
- **Fix:** a Publish section in `CLAUDE.md` and a note on the Invariants line of `spec.md`: the public deployment serves only `index.html`, `src/` and a `.nojekyll` file, made at release by the orchestrator; never point Pages at the repository root. No code change.

### SEC-03: A draft the decoder accepts leads the app to save a draft the decoder rejects (D10 at its maximum)
- **Severity:** LOW. **File:** `src/draft.js:13` and `:58` (`MAX_NEXT_ID`, D10) with `src/core/bill.js:69` and `:93` (`nextId + 1` on every add). **Boundary:** `localStorage` read, then `saveDraft`, then the next load.
- **Maps to spec threat:** threat row 2 ("a hostile draft ... loads a partial bill"), in part: it loads fully, then destroys itself.
- **Repro:** store the S2 draft with `"nextId":1000000000` (the maximum D10 allows). It boots as Aisyah, Ben, Chen. Click Add person: the saved `nextId` is 1000000001. Reload: the S7 note appears and the bill is a new one (`p11_boundaries.py`, B1).
- **Impact:** an honest bill never gets near 10^9 ids. Only a hand-edited draft or a page of the same origin can set it, and that writer could delete the draft directly, so this adds no power. It is a round-trip inconsistency in the spec's own range: D10 allows a value from which the app's next step leaves the range.
- **Fix:** either make `addPerson` and `addItem` return the bill unchanged at the cap (the same shape as the 12 and 50 limits; that is a `split-core` change), or lower D10's upper bound by the headroom the app can spend, or record it as an accepted residual with the sentence above.

## What held up
Control and measurement per threat row. Entry points: `index.html`, `src/main.js`, `src/draft.js`, `src/ui/*.js`.

| Threat row / rule | Control (cited) | Measurement |
|---|---|---|
| 1. Script integrity, R37 | Every user string reaches the DOM through `el()` (`src/ui/dom.js:13-18`: `setAttribute` and text nodes), `setText` and `setValue` (`dom.js:41-47`) and `aria-label` and `placeholder`; icons by `createElementNS` (`src/ui/icons.js:13-17`); ids come from the validated `^p[0-9]{1,10}$` and `^i[0-9]{1,10}$` (`src/draft.js:11-12`). Static scan of `src/`: 0 hits for `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval(`, `new Function`, `setAttribute("on`, `createContextualFragment`, `DOMParser`, `<template`, `fetch(`, `XMLHttpRequest`, `WebSocket`, `EventSource`, `sendBeacon`, `serviceWorker`; the only scheme string is `src/ui/icons.js:14`. No `.style`, timer, `location`, `postMessage`, `window.open`, `document.cookie` or `storage` listener in `src/`, and no dynamic `import(` (the only `import(` text is JSDoc types in `src/core` comments) | `p1`: 10 hostile pairs (`<svg onload=f()>`, `<img src=x onerror=alert(1)>`, `</li><li>`, `</button><button>`, `<script>`, `<iframe srcdoc>`, `<style>`, entities, `__proto__`, `constructor`, `toString`, `hasOwnProperty`, template syntax), each typed and each restored: 20 of 20 keep the element signature of a benign pair, `pwned` 0, no dialog, no CSP violation, text literal in the field, the toggle, the shares row, `Remove ..`, `Who had ..` and the copied row, Object.prototype unchanged. Markup in price, both rates and the subtotal: only the three fixed error texts |
| 1. CSP, R38 | `index.html:6` is the spec's string character for character, third in `<head>`, before the stylesheet and the module; no inline script, style element or style attribute in `index.html` or created by `src/` | `p5`: 6 flows (cold boot with typing, restored bill with the dialog closed three ways, copy refused, clipboard missing, unreadable draft with the note, hostile names) log 0 violations and 0 console errors or warnings. 20 of 20 positive controls from inside the page are blocked (eval and `new Function` in a page timer task, inline script, inline handler, cross-origin image, same- and cross-origin fetch, XHR, WebSocket, EventSource, sendBeacon, iframe, form, base, style element, style attribute, stylesheet, script element, dynamic import). A node added to the DOM does change the element count (the signature check has teeth). The rig refuses `bypass_csp` and `permissions` |
| 2. Hostile draft, R27, D1 to D12 | `decode` runs inside one `try` that returns `REJECTED` (`src/draft.js:43-80`); names by `nameFits` (`:22-24`, grapheme count, no CR or LF); objects rebuilt from known fields (`readPerson` `:26-29`, `readItem` `:31-38`, `decode` `:59-65`); `who` checked against a `Set` of ids; `loadDraft` and `saveDraft` guarded (`:92-114`) | `p3`: 42 values. 28 unreadable (empty, whitespace, truncated, `null`, array, number, string, BOM, trailing garbage, `who` holding `__proto__`, `constructor`, `toString` or a stale id, id `__proto__`, people as an object with `length`, version as a string, mode `toString`, nextId as a string, `1e300` and 1000000001, null and array names, a CR in a name, a 3 MB name, 51 items) give the S7 note and a saved new bill. 14 readable ones load (`__proto__` at three levels, `1.0`, nextId 1000000000, U+2028, a lone surrogate, unknown keys, ids `p01` and `p1`, a line feed in a price text, markup in a subtotal, 200,000 levels of nesting, a 4.5 MB `subtotalText`, 50 items). 0 console or page errors, Object.prototype and Array.prototype unchanged, and after one real keystroke only `version`, `bill` and the known bill, person and item keys are saved (42 of 42) |
| 3. Storage unavailable, R28 | `getStorage` (`src/draft.js:83-89`), `loadDraft` (`:92-103`), `saveDraft` (`:106-114`) catch every access | `p4`: `window.localStorage` getter throws, `localStorage` null, `getItem` throws, `setItem` throws always, `setItem` throws after two calls, the real quota used up: a full flow (type, add person, rename, switch mode, add item, copy) gives shares RM 38.87, 38.87, 38.86, "Summary copied", no note and 0 errors in 6 of 6. A fake `getItem` returning `undefined` (not a real Storage) shows the S7 note and still works |
| 4. Clipboard line forging | A text input strips CR and LF itself (HTML value sanitization), D8 rejects them in stored names (`src/draft.js:23`), and `summaryText` replaces every control, line and paragraph separator and bidi control with a space (`src/core/summary.js:8`, `:28`) | `p2`: LF, CRLF, a trailing LF, `execCommand` and a typed Enter leave no CR or LF in the field or in storage (5 of 5). 15 characters (U+2028, U+2029, U+0085, U+000B, U+000C, NUL, U+001F, U+007F, U+202E, U+2066, U+200E, U+061C, U+200B, U+FEFF, U+00A0) typed and restored: 30 of 30 copy 6 lines with one `Adds up to` and no control, separator or bidi character; ZWSP, BOM and NBSP stay |
| 5. Privacy, R39 | No network API in `src/`; CSP `default-src 'none'`; zero dependencies | `p5`: every request of the 6 flows is a same-origin GET for `/`, `/src/system.css` or a file under `/src/` (22 URLs, all 200), no websocket, worker, popup, download or dialog; storage holds only `split.draft`, no cookie, IndexedDB, Cache Storage or service worker; no link, form or frame in the body. `p5b`: every request the page tried in the 17 request-bearing controls failed with reason `csp` (5 foreign-origin requests and 2 same-origin requests for `/`); none reached the network |
| 6. Test runs and the OS clipboard, CG-7 | `rig.new_context` installs the recorder, refuses `permissions` and `bypass_csp`; the app only calls `navigator.clipboard.writeText` (`src/main.js:43`) | every context of this audit came from `rig.new_context` plus a guard rejecting `readText`, `read` and `write`; the rig's two refusals were proven in `p5`; the operating system clipboard was not read, written or granted |
| 7. Correct shares | `src/` outside `core/` does no money arithmetic (grep: only `Math.min` for focus and `Number(id.slice(1))` for ids) | static only; QA's differential run (90 bills, 0 mismatches) is the dynamic evidence and was not repeated |

### Audit item 2, the ghost-click sweep, control by control
`p6_ghost_sweep.py`: 123 rows, 21 controls, double click at 360x640, 390x844 and 1280x800, triple click at 360x640 and 1280x800, double tap at 360x640 and 390x844 (the 8 variant controls ran a double click at the three sizes and a double tap at 360x640). Baseline for each: a single click on a fresh context. 64 rows equal a single click, 46 differ in UI only, 13 differ in data (5 toggles, by design, and 8 SEC-01).

| Control | Result |
|---|---|
| New bill | Opens on the first click, the second lands on the backdrop and closes it (7 of 7); the third click of a triple is swallowed. No data change. This is I-1, an observation |
| Start new bill, Cancel, backdrop at (10, 10), backdrop over Add person | 7, 7, 7 and 4 rows equal a single click. The draft is unchanged for Cancel and the backdrops, reset once for Start. Focus on New bill |
| Remove person, middle (P2 of 5) | One row. The second press lands on the next row's Remove button and is ignored. Focus ends on that Remove button, not on the name field (UI only) |
| Remove person, last | **SEC-01** |
| Remove item, middle, last, only item | One item in 7, 4 and 4 rows. The second press lands on the next Remove (ignored) or on inert space. Focus ends on that Remove button or on the body (UI only) |
| Add person (from 2, 3 and 5) | One person. The second press lands on the new Person N name field |
| Add item (from 4 and from 0 items) | One item. The second press lands on the new item's name field. `p6b` part A scrolled the button to six heights of a 360x640 viewport: 36 of 36 rows keep the data of a single click |
| Every share toggle (12 of S1) | `p6c`: double click and double tap flip twice (back to the start), triple click flips once, both clicks on the same toggle, nothing else changes, 36 of 36 |
| Mode switch (both labels) | One switch, the second click on the same label. Focus ends on the body (UI only) |
| Copy summary | Same as a single click (the status line) |
| Dismiss note | No data change; focus moves to the body. Known and accepted, not filed |

Rows with a console error, page error or foreign request: 0.

### Audit item 3, can `swallowRepeatClicks` swallow a deliberate action? No case found.
- **Keyboard** (`p7` T1): Enter and Space on New bill, Cancel and Start new bill open, close and reset as before; a keyboard click has `detail` 0, which removes the guard instead of being swallowed. Reopening New bill straight after a keyboard close works. A held Enter alternates the dialog open and closed twelve times, never reaches Start new bill (focus opens on Cancel) and leaves the draft unchanged.
- **Other buttons** (T2): a right and a middle click on Cancel and on the backdrop change nothing and the dialog stays open; a right press on the backdrop followed by a left click on the dialog's own padding does not close it (the press flag is recomputed on every mouse press); a left click on Cancel afterwards closes normally.
- **Press that starts and ends elsewhere** (T3, WR-06): dialog to backdrop, backdrop to dialog and Cancel to backdrop all leave the dialog open and the draft unchanged; backdrop to backdrop closes, as a native backdrop would.
- **A quick second click on a different control** (T4 and T5): a lone press with click count 1 right after Cancel reaches Add person and adds a person; a press carrying count 2 or 3 is swallowed, also after a 3 s pause (there is no timer), and the next count-1 press goes through. The real tap count is Chromium's, so it was measured with touch: the second tap gets `detail` 2 (swallowed) at 0, 8 and 16 px from the closing tap when it follows 60 ms later, and `detail` 1 (delivered) at 24, 30, 80 and 220 px, and at every distance 450 ms later. A control the user could aim at on purpose is at least 24 px away, so only a tap meant for the same spot is held back. Mouse clicks carry the operating system's count, which Playwright sets by hand, so a real mouse was reasoned about and not measured.
- **Guard lifetime** (T6): after a keyboard close and after Esc, a real double click on a toggle flips it twice (both clicks reached the page), so the guard does not linger.

The remaining cost of the design is that the guard has no timer. It ends at the first press that is not a repeat, which is what the spec rules (R30).

### Audit item 4, publish scope
SEC-02.

## Spec coverage gaps
1. **No threat-model row for a repeated press** (SEC-01). R7 and R30 carry dated notes for the Remove-on-Remove and dialog cases only; the class is "a gesture is two or three clicks, and the first moves the layout under the pointer". Add a row with the mitigation "a document-level guard armed by every click that removes or closes something, ending at the first non-repeat press".
2. **No row for what is published** (SEC-02). `CLAUDE.md` says "serves the folder as is" and nothing says which folder.
3. **The accepted residual about U+2028 is stale.** It says such characters "affect only the user's own clipboard text". `summaryText` now replaces U+2028, U+2029, U+0085, controls and bidi controls with a space (measured: 30 of 30 clean), and only invisible characters such as U+200B, U+FEFF and U+00A0 reach the text. The control is stronger than the residual says.
4. **"Inputs strip CR and LF" is done by the browser, not by the app.** True in Chromium (5 of 5 ways), and `summaryText` would also catch a line break in the clipboard text, but the row should say who strips them so a future `textarea` is not added unknowingly.
5. **D10's range is not closed under the app's own increments** (SEC-03).
6. **Two tabs of the same browser** are not in the model (last writer wins, no `storage` listener). With a hostile sibling page this is the accepted shared-origin residual; with two honest tabs it is silent loss of the older tab's changes. Measured: a second page's write is ignored by the open app and overwritten by its next save.

## Observations not filed
- A double click or double tap on New bill ends with the dialog closed (I-1, QA and the code review): 7 of 7 rows, no data change.
- A double click on a mode label, on a middle or last Remove, and on Dismiss note moves focus to the body or to the next Remove button instead of the control the app chose. No data change, same class as the accepted Dismiss note case. The shared guard of the SEC-01 fix removes the Remove cases as a side effect (focus ends on the name field).
- A double click on a toggle flips it twice and a triple click once. Both clicks hit the same control, so this is not a ghost click.
- A stored `priceText` or `subtotalText` with a line feed (D9 checks only the type) shows in the field without it, and the field is flagged invalid at boot while it reads like a valid amount. No markup, clipboard or money effect, since an input strips the break and the parser refuses the stored text. Reachable only by hand-editing storage.
- No `maxlength` on the amount and rate fields (R9, R11, R15). A 4.5 MB text costs 410 ms at boot and 78 ms per key (`p3` H39); the quota stops the write beyond about 5 MB and the write failure is ignored (R28). The only tab that slows is the user's own.
- R27 overwrites an unreadable draft at boot. A draft written by a newer app version (`version` 2) would be destroyed by an older cached page. By design (R27); worth a line if a version 2 is ever planned.
- `src/draft.js:16` builds an `Intl.Segmenter` at module load. A browser without it (for example Firefox before version 125) fails at import and shows the empty shell. Out of scope for the Chromium-only gate; a feature test is one line.
- The CSP has no `require-trusted-types-for 'script'`. R38 says the policy is exactly the given string, and R37's scan covers the same ground, so it is a hardening idea only.
- Not measured: a real touch device or a real mouse's operating-system click count, WebKit and Gecko (CLAUDE.md names Chromium only), GitHub Pages itself (a loopback server stood in for a root deployment).
- Not re-filed, accepted in the spec: a page of the same `github.io` origin can read the draft, framing, U+2028 and invisible characters, the D8 UTF-16 ceiling, H-02 (the by-item table at 360 px).

## Evidence
`docs/modules/split-app/qa/security/20261009-201702/`: `evidence.md` (index, baseline, corrections, processes), `common.py`, probes `p1_injection.py`, `p2_clipboard_text.py`, `p3_hostile_draft.py`, `p4_storage.py`, `p5_csp_network.py`, `p5b_blocked_requests.py`, `p6_ghost_sweep.py`, `p6b_layout_scan.py`, `p6c_every_toggle.py`, `p7_swallow_scope.py`, `p8_publish_scope.py`, `p9_sec01_repro.py`, `p10_fix_check.py`, `p11_boundaries.py`, readers `analyse_ghost.py`, `analyse_ui.py`, `analyse_counts.py`, and one `results-*.json` per probe. 484 result rows, from loops over controls, sizes and gestures; the brief named all three sizes and all three gestures for 13 controls, so the sweep was not sampled down (the aim of 150 cases was exceeded for that reason).
Static checks were made with the Grep tool on `src/`, `index.html` and `src/system.css` (no `@import`, `url(`, `@font-face`). `src/system.css` ends with the one `[hidden]` rule. A credential-shaped scan of the tracked files found none.

## Processes
20 loopback static servers (`python -m http.server <port> --bind 127.0.0.1`, the baseline pytest run's included), pids and ports in `evidence.md`, each started and stopped by its script with `STOPPED ... exited True, port free again True`; each script's headless Chromium and Playwright driver were closed by the script. No background shell, no watcher, no poll loop.

PROCESSES: none alive. Final sweep at 20:51:15, after the last probe, by Win32_Process on name (python, node, chrome, headless, playwright, sh, cmd) and on command line (`http.server`, `playwright`, `ms-playwright`, the evidence folder name, the probe file names), and by netstat on the 20 server ports: the only matches were the `bash.exe` and `powershell.exe` of this session's own shell and of the sweep command, and no port was listening. Windows reuses pids: pid 52132 (the `p8` server, stopped) was later seen as a `bash.exe` of this session.

---

# Solver (2026-10-09)

Role: Security Solver. Start HEAD `06fa151`. Orders: the five ORCH rulings of 2026-10-09 (reversible). Evidence: `docs/modules/split-app/qa/security-solver/20261009-205629/`
(`evidence.md` has the red and green runs, the mutants, the measurements behind the doc pass and the process notes; `junit-*.xml`; `probes/`; `live-gate-check/`) and the fidelity run
`docs/modules/split-app/qa/fidelity/20261009-212142/`. Only the frontmatter was changed above this line (to `clean`, because SEC-01 and SEC-02 are resolved and SEC-03 is an accepted
residual). The finder's sections are as the finder left them, and the finder re-run decides the verdict.

## Status per finding
| Id | Status | Commit | Red | Green | Mutants |
|---|---|---|---|---|---|
| SEC-01 MEDIUM, a repeat press on the last Remove adds a blank person | RESOLVED | `071577a` | 54 new tests on the unfixed sources: the 40 that carry the defect fail (18 people rows: row count `3 == (3 - 1)` for S2 and `12 == (12 - 1)` for S8, a blank person came back; 18 item rows: focus on the page body; 4 R34 rows: focus on the next Remove), the 14 controls pass | 54 of 54; the existing WR-01 and CR-01 tests unchanged and green; the audit's own 123-row sweep re-run: no row differs from a single click in data except the 5 toggles that flip twice by design | M1 people handler without the guard: 20 red. M2 items handler without the guard: 20 red. M3 guard on `click` only: 43 red. M4 guard never disarms: 2 to 3 red. M5 guard swallows everything: 4 red |
| I-1 (observation, ruling 2) | RESOLVED | `68ab318` | 12 of 14 new tests fail on the unfixed opener (the other 2 are controls) | 14 of 14, plus the existing R29, R30, R31 tests, 43 of 43 | I1-M1 opener without the call: 12 red. M4: the new lifetime test red |
| SEC-02 LOW, publish scope | RESOLVED | `314b827` | none (documents) | `CLAUDE.md` has "## Publish" and the Stack line points to it; `spec.md` Invariants carries the dated note | |
| SEC-03 LOW, D10 at its maximum | ACCEPTED residual (ruling 4) | `314b827` | none (no code) | dated bullet under "Residual risks accepted" in `spec.md` | |
| Spec gaps 1 to 5 (ruling 5) | DONE | `314b827`, `12bc878` | none (documents) | threat-model rows for a repeated press and for what is published, the U+2028 residual and the CR and LF row rewritten from measurements, dated notes on R7, R29, R30, `qa.md` rows, `BUILD.md` code map and judgment calls | |
| Spec gap 6 (two tabs of one browser) | NOT DONE, outside the rulings | | | see Observations | |

## What changed in `src/` (for the README reconcile; symbols, not lines)
- `src/ui/dom.js`: `swallowRepeatClicks()` is exported here (moved from `dialog.js`). `isRepeatClick` stays as a file-private count test (the guard is its only user now). The doc comments were rewritten.
- `src/ui/people.js` and `src/ui/items.js`: the Remove click handler is `swallowRepeatClicks(); onRemove(id)` in place of `if (!isRepeatClick(event)) onRemove(id)`.
- `src/ui/dialog.js`: imports `swallowRepeatClicks` from `dom.js`, calls it when a click closes the dialog (as before) and when the click on New bill opens it (I-1).
- Tests: `tests/browser/test_app.py` gained 68 tests (SEC-01 54, I-1 14). No other file under `tests/` changed, `src/system.css`, `docs/design/` and `split-core` were not touched.

## Proof
- Suites: browser 244 to 312 passed, unit 275 to 275 passed (`junit-browser-final.xml`, `junit-node-final.xml`). Each commit was green on its own (298 after SEC-01, 312 after I-1).
- Fidelity: `python tests/browser/fidelity/run.py`, 10 of 10 pairs at 0 mismatching pixels, dimensions equal, evidence `docs/modules/split-app/qa/fidelity/20261009-212142/` (server pid 40216 port 12414, stopped).
- Live gate: `tests/browser/live_e2e.py` unchanged, run through `probes/p5_live_gate_scratch.py` into `live-gate-check/20261009-212227/` here: 7 of 7 steps PASS, exit 0, console.log empty (server pid 47116 port 48889, stopped). The official `qa/live-e2e/` folder was not written.
- Credential gate (`credential_sweep.py --staged`, unpiped) exit 0 before each commit.

## What the user will notice
- A double click, triple click or double tap on a Remove button removes exactly one row, at any position. Removing the last person no longer leaves a blank "Person N" row, and the shares no longer run over one more person. After a double click on a middle Remove, focus is on the name field where a single click puts it (it used to land on the next Remove button or on the page).
- A double click or double tap on New bill opens the dialog and keeps it open (it used to flash open and shut), with focus on Cancel. One click on Cancel or the backdrop, Esc, and the keyboard still close and open it as before.
- Nothing else on screen changed: the fidelity gate is at 0 pixels. The Publish section and the spec notes are documentation.

## What went beyond the letter of a ruling (reversible, for the orchestrator)
1. **`isRepeatClick` is kept, private.** Ruling 1 says to remove it if nothing else needs it. The guard needs it, so it stays as a one-line private constant in `dom.js`, no longer exported.
2. **The Remove handlers lost their own count test, and I checked that this opens no path.** The old test also ignored a repeat press that reaches a Remove button when no Remove click armed the guard first. The one way in is "Dismiss note" moving the rows. Measured: 291 viewports and the three standard sizes, three gestures, the second press lands on a heading or a `div`, never on a control (`probes/p1_dismiss_note.py`, `p2_dismiss_scan.py`). Recorded as BUILD.md judgment call 18. Revert: restore the `if (!isRepeatClick(event))` test in the two handlers (it would have to be exported again).
3. **Dated notes on R7, R29 and R30**, not named in ruling 5. R30's note said the guard serves the dialog only, and R7 and R29 describe behaviour that changed, so leaving them would have left a spec sentence the code now contradicts.
4. **The tests also assert focus (R34).** That is what makes the item rows red on the old code (their data was already safe) and the Remove-then-Remove focus drift a regression guard.

## Observations (not in the rulings, not fixed)
- The 17 UI-only differences left in the re-run sweep are a double click on the two mode labels (10 rows) and on Dismiss note (7 rows): focus ends on the page body. Known and accepted since the audit, no data effect. The same guard could cover them if the owner wants.
- Spec gap 6 (two tabs of the same browser: last writer wins, no `storage` listener) is still not in the threat model, because no ruling named it.
- CLAUDE.md's dev command (`python -m http.server` from the project root) lists directories and serves `.git/` on loopback. Loopback only, not changed.
- The guard goes by the click count the platform reports. Playwright sets it by hand for a mouse, so a real mouse's operating-system count was reasoned about and not measured (as in the audit).
- The publish copy and its `.nojekyll` do not exist yet: making them at release is the orchestrator's (the Publish section says so), and the repository holds no deploy file.

## Left for the orchestrator
- Re-run the security finder (SEC-01 and SEC-02 resolved, SEC-03 an accepted residual, I-1 resolved).
- README reconcile (WR-08): `BUILD.md` code map and judgment calls 18 and 19 are current.
- `docs/progress/`, `docs/v1.0.0/` and `docs/modules/ROADMAP.md` were not touched.

## Process note
The Write tool turned the backslash-u escapes in my first `p4_crlf_and_separators.py` into raw characters. I found it by counting them, rewrote the file with `chr()`, and wrote no escape text into any doc line. I
saw processes that are not mine during the final sweep (a `python -B -m pytest` run with its Playwright node and `chrome-headless-shell` children, and two `http.server` processes started with `--directory`) and left them alone.

PROCESSES: none alive that I started. Started and stopped by me: the pytest static servers of the baseline (pid 40612 port 47711), the I-1 green run (pid 30076 port 55164), the I-1 full suite (pid 51112 port 63662) and the final suite (pid 50360 port 47850), the probe servers (`p1` pid 35232 port 3919, `p2` pid 44504 port 8872, `p3` pid 25336 port 47292, `p4` pid 36116 port 11087), the fidelity runner (pid 40216 port 12414) and the live gate (pid 47116 port 48889), each with `STOPPED ... exited True, port free again True`; the red and mutant runs started and stopped their own servers the same way (pids not kept, output was filtered). Headless Chromium instances were closed by each script or fixture. Final sweep at 21:27 by Win32_Process (name and command line) and by netstat on the known ports found nothing of mine.
