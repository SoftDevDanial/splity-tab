# Security audit evidence: split-app

Role: security finder (read-only on the product). Date: 2026-10-09. Repository head `5ef85cf`, code under audit `61c3cd3`
(`git diff` of `src/` and `index.html` against HEAD is empty). Browser: headless Chromium 149.0.7827.55 through Python Playwright.
Verdict file: `docs/modules/split-app/findings/security.md`.

## Baseline (run once at the start)
| Command | Result |
|---|---|
| `python -m pytest tests/browser -q` | 244 passed in 92.25 s (server pid 17892 port 45423, stopped, port free again) |
| `node --test "tests/**/*.test.js"` | 275 tests, 275 pass, 0 fail, 0 skipped |

## How every probe is built
- `common.py` is the shared helper. Every browser context comes from `rig.new_context` (the clipboard recorder from
  `tests/browser/clipboard/recorder.js` is installed, `permissions` and `bypass_csp` are refused, and p5 proves the refusal).
  On top of that `PROBE_JS` rejects `Clipboard.readText`, `read` and `write` (CG-7), records every mouse event with its `detail`,
  its target and whether it reached the page, records every `securitypolicyviolation`, and counts hostile payloads that run
  (`window.f` and `window.alert` add to `window.pwned`). The operating system clipboard was never read, written or granted.
- Every script starts its own server with `rig.StaticServer` (`python -m http.server <free port> --bind 127.0.0.1` from the project root), prints
  `server STARTED pid .. port ..` and `server STOPPED pid .. port .., exited True, port free again True`, and closes its browser in a `finally`.
- Results are written next to the scripts as `results-<probe>.json` by the scripts themselves (ASCII JSON). Re-running a script overwrites its file,
  so the scripts that were corrected after a first run hold the corrected run (see "Corrections").
- Nothing was written outside this folder and `docs/modules/split-app/findings/security.md`. No file of the product was edited. `git status` shows only
  those two paths as untracked.

## Index of probe scripts and outputs
| Script | Audit item | Output | What it ran | Key result |
|---|---|---|---|---|
| `p1_injection.py` | 1, threat row 1 (R37) | `results-p1-injection.json` (21 rows) | 10 pairs of hostile person and item names (markup, `__proto__`, `constructor`, `toString`, `hasOwnProperty`, template syntax, entities), each typed with the keyboard and each restored from a draft; markup typed into price, both rates and the subtotal | 20 of 20 pair runs: element signature equals a benign pair of the same lengths, `pwned` 0, no dialog, no CSP violation, the text is literal in the field, the toggle, the shares row, `Remove ..`, `Who had ..` and the copied row, 6 clipboard lines, Object.prototype holds its 12 standard names. Money fields: only the three fixed error texts, 0 unsafe nodes |
| `p2_clipboard_text.py` | 1, threat row 4 | `results-p2-clipboard-text.json` (36 rows) | Line breaks inserted into name, item and price fields five ways; 15 control, separator and bidi characters in a name, typed and restored | 5 of 5 break insertions leave no LF or CR in the field or in storage (Chromium turns an inserted break into a space or drops it). 30 of 30 character runs: 6 clipboard lines, one `Adds up to`, no control, separator or bidi character in the text. ZWSP, BOM and NBSP stay (accepted) |
| `p3_hostile_draft.py` | 1, threat row 2 (D1 to D12) | `results-p3-hostile-draft.json` (42 rows) | 42 hostile `split.draft` values written from the page, then a reload and one real keystroke | 28 unreadable ones give the S7 note and a new bill, 14 readable ones load. 0 console or page errors, 0 prototype pollution, after the first edit only the known keys are saved (42 of 42). Boot at most 84 ms, except a 4.5 MB `subtotalText` (410 ms, 78 ms per key) and a 3 MB name (374 ms, rejected) |
| `p4_storage.py` | 1, threat row 3 (R28) | `results-p4-storage.json` (7 rows) | 7 storage failures installed by an init script, then a flow of real gestures and a reload | 6 of 7 clean: shares RM 38.87, 38.87, 38.86, "Summary copied", no note, 0 errors. E6 (`getItem` returns undefined, a Storage contract violation) shows the S7 note and still works |
| `p5_csp_network.py` | 1, R38 and R39 | `results-p5-csp-network.json` (30 rows) | 6 real flows with the shipped policy live; 20 positive controls from inside the page; a negative control; the rig refuses `bypass_csp` and `permissions` | 6 of 6 flows: 0 CSP violations, 0 console errors or warnings, only same-origin GETs (22 distinct URLs, all 200), no websocket, worker, popup, dialog; only `split.draft` in localStorage, no cookie, IndexedDB, cache or service worker. 20 of 20 controls blocked (eval in a page timer task, inline script, inline handler, cross-origin image, fetch, XHR, WebSocket, EventSource, sendBeacon, iframe, form, base, style element and attribute, stylesheet, script, dynamic import) |
| `p5b_blocked_requests.py` | 1, R39 | `results-p5b-blocked-requests.json` (17 rows) | The 17 request-bearing controls again, listing failed requests | every request the page tried failed with reason `csp` (5 foreign-origin requests and 2 same-origin requests for `/`); 0 reached the network |
| `p6_ghost_sweep.py` | 2 | `results-p6-ghost-sweep.json` (123 rows) | 21 controls: mouse double click at 360x640, 390x844, 1280x800; triple click at 360x640 and 1280x800; double tap at 360x640 and 390x844 (the 8 variant controls: double click at three sizes and a double tap at 360x640). A single click on a fresh context is the baseline of each control and size | 64 rows equal a single click, 46 differ in UI only (focus or the dialog flash), 13 differ in data: 5 are toggles (two flips, by design), 8 are SEC-01 (Remove of the last person). 0 console, page or request problems |
| `analyse_ghost.py`, `analyse_ui.py`, `analyse_counts.py` | 2 | printed only | Read the sweep file: per-control table, which UI keys differ, the counts above | see the verdict file |
| `p6b_layout_scan.py` | 2 | `results-p6b-layout-scan.json` (46 rows) | A: Add item, Remove of the last item and of a middle item with the control scrolled to six heights (50 to 550 px) of a 360x640 viewport, double click and double tap. B: an invalid price left by the first press, then a double click or double tap on a control below it | A: 36 of 36 rows have the data of a single click, the second press lands on the new name input or inert space. B: 10 rows, data as a single click except the last-person Remove (SEC-01 again, 3 people) |
| `p6c_every_toggle.py` | 2 | `results-p6c-every-toggle.json` (36 rows) | All 12 toggles of the S1 bill, double click, triple click and double tap at 360x640 | 36 of 36 as designed: both clicks on the same toggle, double click and tap flip twice, triple flips once, nothing else changes |
| `p7_swallow_scope.py` | 3 | `results-p7-swallow-scope.json` (36 rows) | Enter and Space on New bill, Cancel and Start new bill; a held Enter; right and middle button; presses that start and end in different places; one press with click count 1, 2 and 3 after Cancel; touch taps at 0 to 220 px and 60 or 450 ms after a tap on Cancel; the guard's life after a keyboard close and after Esc | nothing deliberate is swallowed. Details in the verdict file, audit item 3 |
| `p8_publish_scope.py` | 4 | `results-p8-publish-scope.json` (2 rows) | Read-only `git ls-files` and file reads; GET requests for 20 URLs on a loopback server rooted at the project | 3,108 tracked files, 22 are the app; 3,086 would be served; 875 copies of `src/` files in 178 folders; 143 text files with a local path; the sample URLs all return 200 |
| `p9_sec01_repro.py` | 2, SEC-01 | `results-p9-sec01-repro.json` (24 rows) | Remove of the last person (S2 with 3 people, S8 with 12) and of the last item (S1), double click, triple click, double tap, 3 sizes | 16 of 16 person rows add a blank person, 8 of 8 item rows do not |
| `p10_fix_check.py` | 2, SEC-01 fix | `results-p10-fix-check.json` (62 rows) | The shipped code, then fix B (Add person ignores a repeat click) and fix A (Remove arms the shared document guard), each served from memory with `route.fulfill`; no project file written | shipped: 16 of 16 repro rows fail. Fix B: 16 of 16 pass, 7 of 7 regression checks pass. Fix A: 16 of 16 pass, 7 of 7 pass, and focus ends on the name field after a double click on a middle Remove |
| `p11_boundaries.py` | 1, SEC-03 | `results-p11-boundaries.json` (2 rows) | nextId at the decoder maximum then one Add person then a reload; a second page of the same origin writing a hostile draft while the app is open | SEC-03 reproduced. The second page's write is ignored by the open app and overwritten by its next save |

Total result rows: 484 in 14 files. The sweeps are loops over the cross product of controls, sizes and gestures that the brief named (p6 123, p6b 46, p6c 36, p9 24, p10 62), so the aim of 150 cases was exceeded on purpose. Run time of all probes together: about ten minutes of machine time.

## Printed output of the runs that decide the findings
SEC-01 (`p9_sec01_repro.py`, 390x844, double click, S2 remove Chen):
```
after single: ["p1='Aisyah'", "p2='Ben'"] shares ['Aisyah RM 58.30', 'Ben RM 58.30']
after double: ["p1='Aisyah'", "p2='Ben'", "p4=''"] shares ['Aisyah RM 38.87', 'Ben RM 38.87', 'Person 3 RM 38.86']
click log: click:1 button.icon-btn [Remove Chen] -> click:2 button.btn.btn-outline (Add person), reached the page
```
SEC-01 (`p9`, S8, 390x844, double click, remove the twelfth person): 11 people after a single click, 12 after the double click, the twelfth is `p13=''`.
SEC-01 with a triple click: click 3 lands on `Remove Person 3` (the new blank row) and is ignored by the WR-01 guard, so the blank row stays.
SEC-01 fix check (`p10`): `PASS fix A: S2 remove Chen 360x640 dbl people 3 -> 2` for all 16 rows; the same rows read `FAIL fix none: ... people 3 -> 3` on the shipped code.
SEC-03 (`p11`): `B1 loaded ['Aisyah','Ben','Chen'] -> after Add person the saved nextId is 1000000001 -> after reload {'note': True, 'people': ['Person 1','Person 2']}`.
Publish scope (`p8`): `tracked files 3108; served by design (index.html and src/) 22; everything else 3086`, `copies of src files outside src/: 875 in 178 folders`, `text files containing a local path ...: 143`.
Touch tap count (`p7` T5): the second tap gets `detail` 2 and is swallowed at 0, 8 and 16 px from the first tap when it comes 60 ms later, and gets `detail` 1 at 24 px or more, and at every distance 450 ms later (the window lies between 60 and 450 ms; it was not narrowed further).

## Corrections made during the audit (the files hold the corrected runs)
- `p1_injection.py`: the first version counted the page's own head `script` and `link` as unsafe nodes, so every row failed. The count is now taken inside `document.body`.
- `p5_csp_network.py`: the first version tried `new Function` inside `page.evaluate`, which the inspector allows even under a CSP without `unsafe-eval` (CDP `allowUnsafeEvalBlockedByCSP` defaults to true). The eval controls now run in a page timer task and are blocked (`script-src | eval`).
- `p5b_blocked_requests.py` and `p7_swallow_scope.py`: the first versions tested the wrong predicate (the failure text is `csp`, not `ERR_BLOCKED_BY_CSP`) and sent a count-2 press as a count-1 press followed by a count-2 press. Fixed and re-run.
- `p10_fix_check.py`: the first run died on a wrong route handler signature before the fixes were exercised. Re-run after the fix.

## Processes
Started by this audit and stopped by the same script, each printing `STOPPED ... exited True, port free again True` (pid, port): pytest 17892 (45423); p6 2748 (22798); p6b 48284 (10858);
p7 51952 (2176, first run) and 27440 (18570); p1 33552 (29826, first run) and 32680 (31472); p2 39392 (4723); p3 43660 (59446); p4 52424 (8099);
p5 47968 (47298, first run) and 40052 (49180); p5b 50400 (20405, first run) and 19064 (3806); p8 52132 (54184); p9 41396 (50261); p10 35084 (37564, first run) and 7012 (37026);
p6c 48728 (56750); p11 47220 (17065). That is 20 servers on 20 ports. Each script's headless Chromium and Playwright driver were closed by the script (`browser.close()` in a `finally`, then the
`sync_playwright` context). One run (p10, first) raised inside `browser.close()` after its server had been stopped. No background shell, watcher or poll loop was started.
Final sweep at 20:51:15, after the last probe, by Win32_Process on name (python, node, chrome, headless, playwright, sh, cmd) and on command line (`http.server`,
`playwright`, `ms-playwright`, this folder's name, the probe file names): 4 matches, all `bash.exe` and `powershell.exe` of this session's own shell and of the sweep command.
Netstat on the 20 server ports above: none listening. Windows reuses pids: pid 52132 (the `p8` server, stopped) was later seen as a `bash.exe` of this session.
