---
module: split-app
kind: security
status: issues_found
counts: { critical: 0, high: 0, medium: 0, low: 1, info: 3 }
date: 2026-10-15
head: 21a7bd2
scope: "v1.1.0 step 5. git diff v1.0.0..HEAD -- src index.html outside src/core (draft version 2 with readSpare, D13 and D14, the spare choice and the random source, the Splits sheet and P1, the repeat guards, the save warning, the clipboard path, the CSSOM writes, the CSP), in Chromium and WebKit, against spec.md (R22 to R28, R37 to R39, R46, R47, R57, R61, Persistence D1 to D14, Threat model and residuals), CLAUDE.md Publish and the decoder rules in STATE.md Notes"
evidence: docs/modules/split-app/qa/security/20261015-222146/
---
# Security audit: split-app (v1.1.0, step 5)

Role. Security finder (read-only on the product). HEAD `21a7bd2`, and `src/` and `index.html` are unchanged since `d58f4ce`. Headless Chromium 149.0.7827.55 and WebKit 26.5 (Playwright 1.61.0), Node v24.11.1.
Every claim below comes from a run whose capture is in the evidence folder, unless the line says "reading only". `evidence.md` there indexes every script and result file.
The 2026-10-09 verdict of 1.0 is in git history (`git show 21a7bd2:docs/modules/split-app/findings/security.md`). Its standing is in "Earlier findings" below.

## Verdict
**ISSUES FOUND. 0 CRITICAL, 0 HIGH, 0 MEDIUM, 1 LOW, 3 INFO.** Every required mitigation of the threat model that I ran holds in both engines. The one LOW is a screen effect. A bidi control in a person's name reorders the rest of the People summary, while the copied summary stays clean. SEC-04 of 1.0 (a held Enter adds a blank item) is fixed in v1.1.0. A control run on the v1.0.0 tree shows it RED in both engines, and HEAD shows it GREEN in both.

## LOW

### SEC-S5-1. A bidi control in a person's name reorders the rest of the People summary on screen
- **Severity** LOW. **Threat** NEW, not in the threat model (a spec coverage gap next to the row "Clipboard text the group trusts" and the residual on invisible characters). **Boundary** a name typed by the user or restored from `split.draft`, through `personLabel`, into the People summary.
- **Symbols** `peopleSummaries` and `createPeopleSection` (`fit`) in `src/ui/sections.js`, which join the labels into one text node of `span.sec-txt`. `nameFits` in `src/draft.js` (D8 rejects only CR and LF). The name inputs of `createPeople` in `src/ui/people.js`.
- **What I saw.** People `<svg onload=f()>`, `Ben` + U+202E (RLO), `Adds up to RM 0.00` + NUL, `A` + U+2028 + `Adds up to`, `Tom` + U+2067 (RLI), restored from a version 2 draft and shown at 390 x 844 with People folded. The characters after the RLO name are drawn right to left. In Chromium `#peopleSum .sec-txt` holds `<svg onload=f()>, Ben` + RLO + ` and 3 more`, and the x positions of ` and 3 more` fall from 340 to 269, so it reads "erom 3 dna". In WebKit the summary holds every label, and the x positions of `s up to RM 0.00` fall from 320 to 229, so the next person's name reads backwards. The labels before the RLO name stay left to right. The splits row of the same person draws its amount left to right in both engines (`receipt_amount_after_rlo_name`), so no money figure on screen is reordered. Every copied summary (card, sheet, strip) holds 8 lines, a space in place of each control and bidi character, and the real `Adds up to RM 53.03` as its last line.
- **Impact.** It changes how other people's names read in one summary line, and that line holds no money. The writer is the user or a page of the same origin (the accepted shared `github.io` residual). The residual for invisible characters says they "change only the look of the user's own text", and a bidi control does more than that. STATE.md Notes asked for this check ("control and bidi characters in names and the summary") and said the screen and the summary should agree.
- **Fix (for the owner to choose).** (a) Text only, no DOM or CSS change. In `peopleSummaries`, put each label between U+2068 (FSI) and U+2069 (PDI). A PDI closes every embedding and override opened inside its isolate, so one name cannot reach the next. (b) Or reject `\p{Bidi_Control}` (and `\p{Cc}`) in D8 and strip them at the name input, the class `summaryText` already replaces, so screen and summary agree everywhere. (b) changes D8 and the input, so it needs a spec line.
- **Evidence** `b2_injection.py`, `b2_injection-chromium.json` and `b2_injection-webkit.json` (`people_summary`, `people_summary_measure`, `copy_card`, `copy_sheet`, `copy_strip`).

## INFO (not counted against the verdict)

### SEC-S5-2. The accepted D8 residual, measured. A one-grapheme name of millions of characters slows the tab and never hangs it
- **Threat** row "The bill draft" and the residual "D8 sets no UTF-16 ceiling". **Symbol** `nameFits` in `src/draft.js`.
- `a` followed by N combining acute accents is one grapheme cluster, so D8 accepts it. Chromium, time to first render and one keystroke in `#svc`. 20k marks 93 and 52 ms, 200k 160 and 91 ms, 1M 556 and 231 ms, 2M 931 and 598 ms, 4.5M 2365 and 2158 ms. WebKit 20k 151 and 146 ms, 1M 857 and 264 ms, 2M 2004 and 491 ms, and 4.5M is refused by WebKit's quota before the app runs. No page error, console line or CSP violation, and the page answered an evaluate after each row. The slowdown lasts across reloads, because the draft is readable. It is within the accepted residual, so this is a measurement, not a finding. A cap in UTF-16 units next to the grapheme count would end it.
- A related cost. `nameFits` spreads every grapheme of a name before it compares the count, so a 4.5M-character ASCII name costs 697 ms in Node before it is rejected (323 ms for 2M in Chromium). Counting in a loop that stops after `max + 1` segments would make that constant.
- **Evidence** `b1b_hostile_boot-<engine>.json` (rows "combining marks"), `n1_decoder-results.json` (row "4.5M-char ascii name").

### SEC-S5-3. WebKit breaks the People summary at a U+2028 inside a name
- **Symbol** `createPeopleSection` (`fit`) in `src/ui/sections.js`. In WebKit the U+2028 of `A` + LS + `Adds up to` starts a new line inside `span.sec-txt` (the x position jumps from 213 back to 336). The fit test compares widths only, so it keeps the full list. Chromium draws no break. No security effect, since the copied summary prints a space. It is a layout point for QA, and fix (b) of SEC-S5-1 removes it.
- **Evidence** `b2_injection-webkit.json` (`people_summary_measure`).

### SEC-S5-4. Core's non-choice actions carry `spare` by reference, and only the decoder keeps a hostile one out
- **Threat** "Object integrity" of split-core and row "The bill draft" here. `setMode`, `addItem` and `toggleItemPerson` return a new bill holding the input's `spare` object itself, as they hold untouched people and items. Fed a parsed object with own `__proto__` and `extra` keys inside `spare`, they pass those keys on (split-core probe `c1_core-results.json`). In the app nothing parsed reaches core without `readSpare` (D13), which builds `spare` new from known fields. After a real keystroke the saved `spare` of both `__proto__` drafts is `{"rule":"top"}` in both engines, and every saved person, item and bill holds only its known keys. So this is how the design works, written down so that a second way of loading a bill keeps it in mind.
- **Evidence** `b1b_hostile_boot-<engine>.json` (`stored_after_keystroke`), `docs/modules/split-core/qa/security/20261015-222146/c1_core-results.json` (`integrity`).

## Earlier findings (1.0) and their standing
| Id | 1.0 status | Standing in v1.1.0 | Evidence |
|---|---|---|---|
| SEC-04 LOW, a held Enter on Remove of the only item adds a blank item | accepted for v1.0, fix owed in v1.1.0 | **FIXED by R57 (a).** Control on the v1.0.0 tree, RED in Chromium and WebKit (four repeats seen, `items` becomes a blank `i8`, `nextId` 8 to 9, focus on the new name field). HEAD, GREEN in both (`items` empty, `nextId` 8, focus on `button#addItem`). Also on HEAD in both engines, a held Enter on New bill leaves M1 open on Cancel, on Splits leaves the sheet open, on the spare chip leaves P1 open, and the stored bill does not change | `b4_held_enter-v100-control-<engine>.json`, `b4_held_enter-head-<engine>.json` |
| SEC-03 LOW, D10 at its maximum | accepted residual | unchanged. The decoder still accepts `nextId` 1000000000 and rejects 1000000001 | `n1_decoder-results.json` |
| SEC-02 LOW, publish scope | resolved | holds, see the threat table | `b5_publish_scope.json` |
| SEC-01 MEDIUM, ghost click on the last Remove | resolved | not re-measured by this finder. The functional suites of today cover R7 and R57 (b) in both engines | none of mine |

## Threat model, each required mitigation
| Row | Verdict | Evidence |
|---|---|---|
| Script integrity (R37, R38) | **HOLDS** in both engines. Markup names (`<svg onload=f()>`, `<img src=x onerror=alert(1)>`, `</li><li>`) restored, in P1's pills and in the sheet create no element. Every `svg` under `body` is `sprite`, `mark`, `ic` or `seal`, every `use` points at `#i-` and a name, no `on*` attribute exists, every value and splits row is the literal text, and the chip reads `One person, <svg onload=f()>`. The R37 scan of `src/` and `index.html` finds none of the banned APIs (reading only, Grep) | `b2_injection-<engine>.json` |
| Style integrity (R38) | **HOLDS** in both engines. After the flows the only `style` attributes are `--strip-h` on the root (0, 108, 111 px), `--rows: 6` on `#splits`, `left: 574px; bottom: 239.2px` on `#spareDlg` and `padding-bottom` of 271 and 325 px on `#sheetScroll`, all measured numbers. A `style` attribute set from the page is refused (`style-src-attr`) | `b3_csp_network_style_random-<engine>.json` |
| The bill draft (D1 to D14) | **HOLDS.** Node 101 of 101 hostile drafts as specified (unknown `mode` and `rule`, own `__proto__` at every level, duplicate person and item ids, `who` not an array or holding unknown, repeated or `__proto__` ids, stale and edge `nextId`, no people in even mode, D8 in grapheme clusters with CR and LF refused, D13 `personId` and `order` that drops, repeats, invents or holds numbers, D14 ignoring a hostile version 1 `spare`, 1M nesting, 1e6-entry arrays). Every accepted bill holds only known keys on `Object.prototype` and round-trips through `encodeDraft`. In the app, 15 unreadable drafts give the note and a saved `newBill()` version 2, readable ones are not written at boot, and no row has a console line, page error or CSP violation (Chromium 28 of 28, WebKit 27 of 27, 1 skipped by the quota) | `n1_decoder-results.json`, `b1b_hostile_boot-<engine>.json` |
| The user's belief that the bill is kept (R46, R47) | **HOLDS** in both engines. The getter that throws shows the warning at boot and it clears once storage returns. A `setItem` that throws shows it after the first change and it clears on the next successful write. A `getItem` that throws shows it at boot and the next save clears it. A real quota filled by a same-origin key shows it after the failed write and clears it once the key is gone. The stored text then matches the screen | `b6_save_warning-<engine>.json`, `b6b_real_quota-<engine>.json` |
| Availability (R28) | **HOLDS** in both engines. 0 console lines and 0 page errors in every storage case. Every `catch` in `src/draft.js` and `src/main.js` binds no exception, so the app cannot read a name, message or code (reading only) | same files |
| Clipboard text the group trusts | **HOLDS** in both engines. Copies from the card, the sheet and the strip are equal, 8 lines, with no control, separator or bidi character and the real proof line last. The row of `Adds up to RM 0.00` + NUL starts with "Adds up to", which is core residual 1. On screen see SEC-S5-1 | `b2_injection-<engine>.json` |
| Privacy (R39) | **HOLDS** in both engines. Every request of the three flows is a same-origin GET for `/` or a file under `/src/`. No `/favicon.ico` or `/src/icon.svg` was requested headless. A same-origin `fetch` and a cross-origin image are refused (`connect-src`, `img-src`). The only scheme strings in the publish set are the two exempt SVG namespaces | `b3_csp_network_style_random-<engine>.json`, `b5_publish_scope.json` |
| The human's desktop during tests | **HOLDS.** Every context of mine came from `rig.new_context` with the stand-in before load, and each probe checked it (0 writes, not native) before its first gesture. My read guard was never hit (`clipboard_refused` 0). Today's live gate runs record `bypass_csp: false`, the two init scripts in order, `clipboard_stand_in: true` and 0 CSP violations in both engines, and the six R41 static tests pass. The narrowness of that guard is the code review's CR-S5-6, not repeated here | `pytest-r41-static.xml`, `docs/modules/split-app/qa/live-e2e/20261015-205844-chromium/summary.json`, `20261015-205931-webkit/summary.json` and their `-control` folders |
| Correct shares, the app passes `Math.random` and nothing else (PD-19) | **HOLDS** for the random source. All 10 (Chromium) and 16 (WebKit) `Math.random` calls of the flows come from `drawOrder` in `src/core/spare.js`, through `chooseSpareRule` or `pickAgain`. The "no money arithmetic in the app" part is reading only | `b3_csp_network_style_random-<engine>.json` (`random_calls`) |
| The bill as the user left it, pointer repeats (R57 (b)) | **NOT RUN by this finder.** Reading only, `isRepeatPress` in `src/ui/repeat.js` compares event times and places and schedules nothing. Today's functional suites carry the measured cases | none of mine |
| The bill as the user left it, keyboard auto-repeat (R57 (a)) | **HOLDS** in both engines, with a RED control | `b4_held_enter-*.json` |
| What is published | **HOLDS.** The publish set is 31 tracked files with nothing untracked or ignored, no local path, address, loopback host or secret-shaped key, and `index.html` names only `src/icon.svg`, `src/system.css` and `src/main.js`. The publish copy and its `.nojekyll` are made at release by the orchestrator and do not exist yet | `b5_publish_scope.json` |

## The decoder rules in STATE.md Notes
Unknown `mode` rejected, unknown and `__proto__` keys dropped or rejected, duplicate person ids rejected, `who` that is not an array of known ids rejected, stale `nextId` rejected, no empty people list in even mode (at least 2), and D8 in grapheme clusters, all hold (`n1_decoder-results.json`, `b1b_hostile_boot-<engine>.json`). Control and bidi characters in names stay readable by design (D8). The summary prints a space for each, and on screen see SEC-S5-1.

## Credential gate
`python -B "{sdlc}/harness/credential_sweep.py"` from the project root, foreground and unpiped, **exit 0** (9689 files). Its second run, kept on disk, also gave exit 0 on 9721 files, with the positive control detected and 0 false hits on prose (`credential-gate.txt`).

## Not done
- The ghost-click sweep of 1.0 (SEC-01 class) and the R57 (b) tap timing were not re-run by me. Today's QA suites carry them.
- A touch device and Safari on an iPhone (residual, owner's UAT).
- The draft sharing with the showcase hub's same-origin frame (residual, the hub project's).

## Processes
15 loopback servers (`python -m http.server <port> --bind 127.0.0.1` through `rig.StaticServer`), one per probe run, each started and stopped by its own script and logged `STOPPED ... exited True, port free again True` in its JSON (`facts.server_log`). Their pids and ports are in `evidence.md`'s files. Each headless browser and Playwright driver was closed by its script. Node and pytest runs were foreground and exited.

PROCESSES: none alive. At 22:40 a Win32_Process sweep by name (python, node, chrome, headless, playwright, webkit, bash, sh, cmd) found only this shell's own `bash.exe` (pids 23052, 26468, 13564). `netstat -ano` showed nothing listening on any of my 14 ports (27498 served two runs).
