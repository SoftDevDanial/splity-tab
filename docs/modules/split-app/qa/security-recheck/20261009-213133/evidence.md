# Security re-check evidence: split-app

Role: security finder, scoped re-check (read-only on the product). Date: 2026-10-09. Started at HEAD `8012c43`, code under test `b02386b`.
HEAD moved to `a0edc90` while this ran (a docs-only ledger commit, `git diff --stat 8012c43 HEAD` lists `docs/v1.0.0/CHANGE-LEDGER.md` alone). `src/` and `index.html` are byte-identical
at `b02386b`, `8012c43` and `a0edc90` (`git diff --stat b02386b HEAD -- src index.html` is empty). Browser: headless Chromium 149.0.7827.55 through Python Playwright.
Report section: `recheck-section.md` in this folder. Nothing outside this folder was written (`git status --short` shows only `docs/modules/split-app/qa/security-recheck/` untracked).

## Baseline suites (run once, as asked)
| Command | Result |
|---|---|
| `node --test "tests/**/*.test.js"` | 275 tests, 275 pass, 0 fail, 0 cancelled, 0 skipped |
| `python -m pytest tests/browser -q -p no:cacheprovider` | 312 passed in 108.72 s (its own static server pid 47756 port 39480, `server STOPPED ... exited True, port free again True`) |

## How every probe is built
- `rc.py` imports the audit's `common.py` read only (`qa/security/20261009-201702/`) and points its output folder here. Every browser context still comes from `rig.new_context`
  (clipboard recorder on, `permissions` and `bypass_csp` refused, plus the audit's second CG-7 guard rejecting `Clipboard.readText`, `read` and `write`). The operating system
  clipboard was never read, written or granted. The only rows that press Copy summary are the 7 `copy-summary` rows of the sweep (and their single-click baselines), and their
  `problems` (which include `cg7 violations`) are empty.
- `rc.py` adds one thing to the audit helper: `Cap.problems` also reads `window.csp`, so a CSP violation is a problem row. A problem row is also any console error, any CSP console
  message, any page error and any request that is not a GET for `/`, `/src/system.css` or a file under `/src/`.
- `legacy_sources()` reads `git show 06fa151:src/ui/<file>` for the four files that differ (`dom.js`, `dialog.js`, `people.js`, `items.js`) and serves them from memory with
  `context.route(...).fulfill`. That tree is the one the audit judged. It is used only for control rows that must show the old defect, so a passing probe has teeth. No project file is written.
- Every script starts its own server with `rig.StaticServer` (`python -m http.server <free port> --bind 127.0.0.1` from the project root) and closes its browser and server in a `finally`.
  Results are written next to the scripts as `results-<probe>.json` by the scripts themselves. No script writes anywhere else. `PYTHONDONTWRITEBYTECODE=1` and `python -B` were used.

## Index of probe scripts and outputs
| Script | Brief item | Output | What it ran | Key result |
|---|---|---|---|---|
| `r1_sec01_matrix.py` | 1 | `results-r1-sec01-matrix.json` (39 rows) | Remove of the LAST person (S2 Chen, S8 the twelfth Mei Ling), of the last item (S1 Satay) and of the only item (S1 cut to its first item), each at 360x640, 390x844 and 1280x800 with a mouse double click, a mouse triple click and a touchscreen double tap (36 fresh contexts). The expectation is computed from the seed: exactly one row gone, every other field of the saved bill as seeded, no blank person or item, `nextId` unchanged. Then 3 control rows on the tree before the fixes | 36 of 36 rows pass. Each click log shows click 1 reached the Remove button and click 2 (and 3) `SWALLOWED` at the document. Controls: 3 of 3 show the old defect (S2 390x844 double click: 3 people, blank `p4`, `nextId` 4 to 5. S2 360x640 double tap: the same. S8 1280x800 triple click: 12 people, blank `p13`, `nextId` 13 to 14), so the probe has teeth |
| `r2_i1_new_bill.py` | 2 | `results-r2-i1-new-bill.json` (25 rows) | Double click and double tap on New bill at the 3 sizes, then at once one deliberate click or tap on Cancel, on Start new bill and on the backdrop at (10, 10) (18 rows). A triple click, Esc after a double click and after a double tap, a click or tap on the backdrop over the New bill spot 600 ms later (3 rows), and a control row on the old tree | 24 of 24 rows pass: after the gesture the dialog is open with focus on `Cancel` (6 of 6). Each follow-up click carries `detail` 1, reaches the page, closes the dialog and puts focus on New bill. Cancel and the backdrop leave the draft byte-equal to the seed, Start new bill resets it. Control: on the old tree a double click at 390x844 leaves the dialog closed (the I-1 flash) |
| `r3_overswallow.py` | 3 | `results-r3-overswallow.json` (27 rows) | A mouse: Remove then Add person within about 55 ms at 3 sizes (86 to 269 px away), Remove P2 then Remove P4, Remove item then Add item. B touch: Remove then Add person 60 ms later (2 sizes), the same spot at 450 ms and at 60 ms. C keyboard: Enter chain and Space chain (Remove, Tab, Remove, no pause), a held Enter on 5 kinds of Remove and a held Space on the only item (8 key repeats over about 320 ms). D right and middle button around a Remove and around Add person. E Remove right after a dialog close (mouse, touch). F guard lifetime: Remove then typing then a real double click on a name field, a state probe with lone presses of click count 2 and 1, accumulation after three Removes, no timer (3 s), a press on a disabled Remove, Esc after opening then a second tap | 22 pass, 1 FAIL, 4 measurements. The FAIL is the held Enter on Remove of the ONLY item (SEC-04). Everything else held, details in `recheck-section.md` |
| `r3b_followups.py` | 3 | `results-r3b-followups.json` (9 rows) | M: diagnosis of what happens after a middle press. K: the held Enter on the only item with a realistic hold (first repeat at 520 ms, then 35 ms apart), an ordinary 90 ms press, the same hold on the old tree, and four rows on a candidate fix served from memory (a `keydown` guard that cancels `repeat` events, added to `swallowRepeatClicks` in `dom.js`), plus a held Enter on New bill on the fixed tree for comparison | Fixed tree: held Enter leaves a blank item `i8` and `nextId` 9, the ordinary press is clean. Old tree: the same blank item (older than the fix). Candidate fix: held Enter leaves `items []` and `nextId` 8, separate Enter presses still work, a held letter key still types, a held Enter on New bill leaves the dialog open. M: the first left click after a middle press never reaches the page (only a `mouseup`), which is what ending middle-button autoscroll looks like, so the failed middle row of the first `r3` run was a harness effect and not the app |
| `r3c_sec04_impact.py` | 3 | `results-r3c-sec04-impact.json` (2 rows) | What the user sees after an ordinary Enter and after a held Enter on the only item's Remove, and one click on the blank row's Remove | ordinary: `items []`, panel text "Add an item to see the shares.". Held: one blank item, panel text "Give every item a price to see the shares.", one click on its Remove returns `items []` |
| `r4_ghost_sweep.py` | 4 | `results-r4-ghost-sweep.json` (123 rows) | The audit's `p6_ghost_sweep.py`, imported read only and run unchanged: 21 controls, double click at 3 sizes, triple click at 2, double tap at 2 (the 8 variant controls: double click at 3 sizes and a double tap at 360x640), each against a single click on a fresh context | 123 rows. 5 rows differ in data and all 5 are toggles (a double click or double tap flips twice and returns to the start, `data_equal_initial` True in 5 of 5). 17 rows differ in UI only: the two mode labels (10) and Dismiss note (7), the focus goes to the body. 0 rows with a console error, page error, CSP violation or foreign request. New bill: 7 of 7 rows equal a single click (the audit had a UI difference in each). Remove person and Remove item: 30 of 30 rows equal a single click in data and UI. No click of any non-Remove control reached a Remove button |
| `r5_csp_live.py` | 5 | `results-r5-csp-live.json` (5 rows) | Three real flows over the changed files (390x844 mouse and keyboard, 360x640 touch, cold boot and reload) with the shipped policy live, then two positive controls | 0 CSP violations, 0 console messages, 0 page errors, 0 failed requests. Every request is a same-origin GET (22 distinct URLs: `/`, `/src/system.css` and 20 files under `/src/`), all status 200. `localStorage` holds only `split.draft` (nothing after a cold boot), no cookie. Positive control: an inline script did not run and a same-origin `fetch` was blocked, 2 violations recorded (`script-src-elem \| inline`, `connect-src`). `rig.new_context` refused `bypass_csp` and `permissions` |
| `r7_partb_and_touch_near.py` | 1 and 3 | `results-r7-partb-and-touch-near.json` (14 rows) | The audit's `p6b` part B (an invalid price left by the first press, then a double click or double tap on a control below it), imported read only, 10 rows. Then a tap on Remove P2, 60 ms later a tap 30, 40 and 60 px to its left (name field) at 390x844 and 30 px at 360x640 | Part B: 8 of 10 rows equal a single click, the 2 that differ are the toggle double taps (two flips, by design). The audit's two `remove-person-3` rows (blank person added) now equal a single click. No repeat press reached a Remove button unguarded (the only repeat press that landed on one, `Remove Mee goreng mamak` in the `remove-item2` double tap, was `SWALLOWED`). Touch: 4 of 4 delivered, `mousedown:1` and `click:1` on the name field, focus on it |
| `r6_summary.py` | all | printed only | Reads the result files and prints the counts used here | 244 rows in 8 files |

Total result rows: 244. The brief aimed at under 200 with the sweep included, so this is 44 over. The sweep alone is 123 and the SEC-01 matrix is 36 by the brief's own list.
Rows beyond the brief's list: 4 control rows that give the probes teeth, 11 rows that pin SEC-04 and its candidate fix (`r3b`, `r3c`) and 14 rows of part B and touch-near (`r7`).

## Static checks (Grep tool, not a script)
- Banned APIs on the four changed files `src/ui/dom.js`, `src/ui/dialog.js`, `src/ui/people.js`, `src/ui/items.js`. Pattern: `innerHTML|outerHTML|insertAdjacentHTML|document\.write|eval\(|new Function|setAttribute\(\s*["']on|createContextualFragment|DOMParser|<template|fetch\(|XMLHttpRequest|WebSocket|EventSource|sendBeacon|serviceWorker|importScripts|postMessage|window\.open|document\.cookie|localStorage|sessionStorage|indexedDB|location\.|import\(|setTimeout|setInterval|requestAnimationFrame|\.style\b|\.cssText|addEventListener\("(storage|message)`.
  Result: 0 matches in each of the four files (the Grep count mode printed "No matches found" four times).
- The same pattern over all of `src/` (without `localStorage`, which `src/draft.js` uses by design): 3 matches, all in comments (`src/core/result.js:109` and `src/core/summary.js:14` are JSDoc `import("./...")` types, `src/core/allocate.js:1` is the word "allocation."), none in the changed files.
- Positive control of the scan: `createElement|setAttribute|addEventListener|textContent` over the same four files gives 22 matches (dom.js 7, people.js 3, dialog.js 7, items.js 5), so the Grep reaches the files.
- Imports of the four files: only relative static `import ... from` lines (`./dom.js`, `./icons.js`, `./field-error.js`, `./field-leave.js`, `../core/bill.js`), no dynamic `import(`.
- `isRepeatClick` is a file-private `const` at `dom.js:38` and used only by the guard (`dom.js:52`). `swallowRepeatClicks` is exported at `dom.js:50` and called at `people.js:18`, `items.js:27`, `dialog.js:14` and `dialog.js:21`.
- `index.html:6` holds the CSP meta tag, character for character the string of R38 in `spec.md` (count 1 in the spec), and `index.html` is unchanged since the audit.
- `git diff --stat 06fa151 HEAD -- src index.html` lists the four files above and nothing else (40 insertions, 28 deletions).

## Printed output that decides the findings
SEC-04 (`r3b_followups.py`, section K, 390x844, seed S1 cut to its first item, focus on `Remove Nasi lemak ayam`, Enter held about 700 ms):
```
FAIL [K] fixed tree: Enter held ~700 ms (first repeat at 520 ms) on Remove of the ONLY item
      items ['i8'], nextId 9, blank_items ['i8'], keys Enter:first, Enter:repeat x4, clicks Remove Nasi lemak ayam (detail 0) then Add item (detail 0), focus 'Item 1 name'
PASS [K] fixed tree: an ordinary Enter press (90 ms) on Remove of the ONLY item      items [], nextId 8, keys Enter:first, focus 'Add item'
PASS [K] CONTROL, tree before the fixes (06fa151): the same held Enter                items ['i8'], nextId 9, blank_items ['i8']
PASS [K] CANDIDATE fix from memory: the same held Enter                               items [], nextId 8, blank_items [], keys Enter:first, Enter:repeat x4, focus 'Add item'
```
The same defect in `r3_overswallow.py` (8 key repeats 40 ms apart): trail `p3/i0/Add item`, then `p3/i1/Item 1 name` from the second repeat on, saved item `i8` with empty name and price, `nextId` 9.
Middle button (`r3b` M): `mousedown:1` and `mouseup:0` on Remove P2, then the next left click on a heading produced only a `mouseup`, and the one after it a full `mousedown:1`, `mouseup:1`, `click:1`. That matches the browser using the first left click to end middle-button autoscroll.

## Corrections made while working (every run is kept in the printed record above, the files hold the last run)
1. `r1_sec01_matrix.py` first run: the 36 fixed-tree rows passed, then the control section crashed because the `route.fulfill` handler had two parameters and Playwright passed the request as the second one. The result file was not written. `rc.py` now builds a one-parameter handler. The second run wrote all 39 rows, the 36 fixed-tree rows are the same 36 passes.
2. `r3_overswallow.py` first run: the middle-button row (D) failed. Diagnosed in `r3b` section M as the browser eating the next left click after a middle press, so not an app behaviour. `r3_overswallow.py` was rewritten to end that state with a click on a heading, and rerun. Its last run is the one in the result file (22 pass, 1 fail = SEC-04, 4 measurements).
3. A stray `python - <<EOF` that only printed one line (it wrote nothing) was run once by mistake while editing a probe. No file was created or changed by it. Every file in this folder was created with the Write tool.

## Not measured
- A real mouse's operating-system click count. Playwright sets `click_count` by hand for a mouse, so the mouse rows of items 1 and 3 carry the count the gesture implies (2 for a double click, 3 for a triple, 1 for a deliberate click on another control). Chromium's own tap count was measured for touch.
- A real key-repeat device. Auto-repeat was produced by repeated `keyboard.down` with the key still down, which Playwright sends as `repeat: true` keydowns (the page recorded `Enter:first`, `Enter:repeat` x4).
- WebKit, Gecko, a real touch device, GitHub Pages itself.

## Processes
Started by me and stopped by me, each by its own script's `finally` (`server STOPPED pid .. port .., exited True, port free again True` was printed every time):
| Run | Server pid | Port |
|---|---|---|
| pytest baseline | 47756 | 39480 |
| `r1` first run (crashed in the control section, server still stopped by `finally`) | 42312 | 23562 |
| `r1` | 42440 | 18591 |
| `r2` | 39908 | 36578 |
| `r3` first run | 53632 | 55499 |
| `r3` last run | 47788 | 14053 |
| `r3b` | 48220 | 33761 |
| `r3c` (the pid was reused by Windows) | 53632 | 63464 |
| `r4` | 51472 | 44184 |
| `r5` | 52924 | 3195 |
| `r7` | 27160 | 29353 |
Each script's headless Chromium and Playwright driver were closed by the script. The two long runs (the pytest suite and `r4`) were started with `run_in_background` and ended on their own (exit code 0). No watcher, no poll loop.
Checked at 21:52 after the last probe with `Get-CimInstance Win32_Process` filtered to python, node, chrome and headless (command lines read), by `Get-Process -Id` for every pid above (all gone), and by `netstat -ano` for the ports above (no LISTENING socket).
Not mine and left alone: a `python -m http.server 52346 --bind 127.0.0.1` (pid 49448), a `python -` run by a bash command of the sibling `streaks` project (pid 46636, parent bash pid 52208), and at the start a fidelity run with its Playwright node and `chrome-headless-shell` children from that project.
