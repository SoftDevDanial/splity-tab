# Roadmap: Split v0.1.0

**Phase.** plan · **Date.** 2026-10-08 · **Written by.** the planner (solutions architect role)
**Inputs.** `docs/brainstorm/brainstorm.md`, `docs/design/` (goldens, screen docs, `system.md`, `system.css`, `RULINGS.md`), `docs/design-explore/FLOW-CHECK.md`, `CLAUDE.md`, `docs/constitution.md`. No research folder and no repo summary (greenfield).
**Phase skills.** The registry (`docs/phase-skills.md`) assigns none to plan. The design row (taste-skill, frontend-design) applies to the UI work in `split-app` during execute.
**Clarify gate.** Ruled on 2026-10-08 by the orchestrator under the owner's delegation (ORCH, reversible). Nothing blocks execute.
**Re-plan 2026-10-08.** A second planner pass after the plan check (3 BLOCK, 9 FLAG) fixed every item as ruled by ORCH. Changes are marked "Changed 2026-10-08" or "Added 2026-10-08", and the old wording stays visible where it was wrong. CG-9 to CG-11 below record the three rulings. The plan checker sets the new verdict.

## Modules
| Order | Module | Nature | Depends on | R# count | Contract |
|---|---|---|---|---|---|
| 1 | `split-core` | Pure logic. Money parsing and formatting, bill maths, cent allocation, bill state rules, summary text. No DOM, no I/O | none | 26 | `split-core/spec.md`, `split-core/qa.md` |
| 2 | `split-app` | FE and the **live-composition module**. `index.html`, the UI, the `localStorage` draft, the clipboard, the dialog, the fidelity gate and the cold-boot live-e2e gate | `split-core` (exported functions only) | 42 | `split-app/spec.md`, `split-app/qa.md` |

**R# counts.** Changed 2026-10-08, from 25 and 41 to 26 and 42 (68 in all), by the duplicate-names requirements (core R26, app R42).

**Why two modules.** There are two reasons to change in this product (how the money works, and how the page looks and behaves) and only one real seam between them. The core is pure and fully unit-testable under `node --test`. The app is the browser shell. A third module (for example the draft on its own) would add a cross-module contract for about 60 lines of code with no variation point behind it.

**One change from the expected shape.** `split-core` also owns the bill state rules (the `Bill` shape, new-bill defaults, limits, "remove a person from every item", display-name fallback, the blocking order of RULINGS 3). They are DOM-free brainstorm rules, so exact unit tests can cover them, and the app never edits arrays itself.

## Build order
1. **`split-core`.** Independent, no UI. Green when `node --test "tests/**/*.test.js"` passes every `@R` case.
2. **`split-app`.** Starts when `split-core` is green. Its own task order is shell, people, mode and subtotal, items, charges, panel, copy, draft, dialog, cross-cutting checks, fidelity gate, live gate.

There is no dependency cycle and no deadlock.

## Commands the plan relies on
| What | Command | Status |
|---|---|---|
| Serve | `python -m http.server <port> --bind 127.0.0.1` from the project root | as in `CLAUDE.md` |
| Unit tests | `node --test "tests/**/*.test.js"` | as in `CLAUDE.md` (CG-6) |
| Browser tests | `python -m pytest tests/browser -q` | as in `CLAUDE.md` (CG-6). pytest 9.1 and Playwright 1.61.0, both test-only |
| Fidelity gate | `python tests/browser/fidelity/run.py`, which serves the app and runs the sdlc plugin harness `{sdlc}/harness/fidelity.py` (sdlc 2.1.2) 10 times. Changed 2026-10-08 (CG-11): the runner starts the harness with `sys.executable`, the Python that runs pytest, not with the README venv | test-only, see `split-app/qa.md` |
| Live gate | `python tests/browser/live_e2e.py` | test-only |

## Clarify gate (ruled 2026-10-08, ORCH)
| Id | Question | Why it was open | Resolution | Ruling | Affects |
|---|---|---|---|---|---|
| CG-1 | What is a newly added person called? | The brainstorm names the first two "Person 1" and "Person 2" and the S3 golden shows them as field values. It says nothing about the third and later ones. | The new field is **empty** and shows the placeholder "Person N", and "Person N" is used everywhere else (ruling 4). | Ruled 2026-10-08, ORCH. Accepted as recommended. | core R11, app R6 |
| CG-2 | Where does keyboard focus go after Add person, Add item and a Remove? | Not designed. Without a rule, a removed button takes focus with it and a keyboard user starts again from the top. | After an add, the new row's name field. After a remove at position k, the name field now at k (or k - 1 if it was the last). After the last item is removed, "Add item". | Ruled 2026-10-08, ORCH. Accepted as recommended. | app R34 |
| CG-3 | When does an inline error appear? | Ruling 1 says which text shows an error, not when. A live check flashes "Enter an amount like 12.50" on almost every price typed. | Show the error when the field is left holding bad text, and at load for restored bad text. Remove it as soon as the text becomes valid or empty while typing. The bill panel always follows the current text. | Ruled 2026-10-08, ORCH. Accepted as recommended. | app R10 |
| CG-4 | Exactly which text counts as "a number with up to 2 decimals"? | The brainstorm gives "12", "12.5", "12.50" and the limits, but not white space, a trailing dot, a leading dot, leading zeros or commas. | Trim surrounding white space. ASCII digits, optionally a dot and 0 to 2 decimals. "12." is 12.00, "007" is 7.00, and ".5", "1,000", signs and exponents are errors. Same grammar for rates. | Ruled 2026-10-08, ORCH. Accepted as recommended. | core R1, R3 |
| CG-5 | Do large amounts get a thousands separator? | The brief fixes "RM 38.87" but no amount above 999. A by-item total can reach RM 7799999.22. | No separator ("RM 1234.56"). | Ruled 2026-10-08, ORCH. Accepted as recommended. | core R4 |
| CG-6 | The `CLAUDE.md` unit test command was broken | `node --test tests/` exits 1 with `MODULE_NOT_FOUND` on Node 24.11.1 (measured). `CLAUDE.md` had no browser test command. | Unit tests `node --test "tests/**/*.test.js"`, browser tests `python -m pytest tests/browser -q`. | Ruled 2026-10-08, ORCH. Accepted. The orchestrator changed `CLAUDE.md`, and both `qa.md` files use these exact commands. | both `qa.md` files |
| CG-7 | May tests touch the operating system clipboard? | Headless Chromium on Windows writes the real system clipboard (measured). The first plan saved and restored it, which still reads the owner's data. | No test ever touches it, not even to read it. A test-side init script replaces `navigator.clipboard.writeText` with a recorder that resolves and stores the text on `window` (`recorder.js`), or makes it reject with a `NotAllowedError` DOMException (`reject.js`). This is platform control in the same category as `page.clock`. The app gets no hook. | Ruled 2026-10-08, ORCH (added by the orchestrator). | app threat model, `split-app/qa.md` How to run, R5, R22, R23, R24, R37 and the live gate |
| CG-8 | What does a click on the New bill dialog's backdrop do? | `docs/design/new-bill-dialog.md` says it does nothing, while `docs/design-explore/FLOW-CHECK.md` expects a backdrop click at (10, 10) to return to S2. | A backdrop click acts as Cancel, with the same result and the same focus return ("New bill"). Native `showModal()` ignores it (measured), so the app handles it. The golden `.md` is immutable and stays as written. This ruling overrides that one sentence. | Ruled 2026-10-08, ORCH (added by the orchestrator). | app R30 and its scenario |
| CG-9 | Which person name can the R37 injection test type? | The plan check showed that the old person payload `<img src=x onerror=alert(1)>` is 28 characters, and every person input has `maxlength="20"` (R4, D8), so no conformant build can hold it. | The person name is `<svg onload=f()>` (16 characters). The long `<img src=x onerror=alert(1)>` payload moves to an item name (maxlength 40), where it reaches the field, `Remove {itemLabel}` and `Who had {itemLabel}`. The `"><script>alert(2)</script>` payload stays, on a second item name. | Ruled 2026-10-08, ORCH. | app R37 and its scenario |
| CG-10 | How are the four SVG icons built, when R39 bans every `scheme://` string and R37 bans `innerHTML`? | The icons are made at run time. `createElementNS` needs the namespace string `http://www.w3.org/2000/svg`, which the R39 scan would flag. Cloning a `<template>` or a hidden icon would add an element and an HTML-parsing sink that no rule covers. | Exempt exactly the string `http://www.w3.org/2000/svg` when it is the first argument of `createElementNS`, in R39 and in its scan, and nothing else. No `<template>` cloning, no `innerHTML`. | Ruled 2026-10-08, ORCH. | app R37, R39, DOM contract |
| CG-11 | Which Python runs the fidelity harness? | `harness/README.md` asks for a venv in `%USERPROFILE%\.sdlc-harness\.venv`, which still does not exist (checked 2026-10-08). The system Python has the harness requirements. | `run.py` runs the harness with `sys.executable`, the same Python that runs pytest. The README venv is optional here. Nothing creates it and nothing installs packages. | Ruled 2026-10-08, ORCH. | app Fidelity gate section, task 12 |

## Planner decisions (reversible, no human input needed unless overturned)
| Id | Decision | Reason |
|---|---|---|
| PD-1 | "Add item" is disabled at 50 items with the S8 disabled look. | The brainstorm sets the 50 limit and the system has exactly one way to show an unavailable add (Add person at 12). |
| PD-2 | A name of only spaces counts as blank, and labels show the trimmed name. The field keeps what was typed. | "Blank" in the brainstorm. Trimming only the label keeps typing undisturbed. |
| PD-3 | People who had nothing are listed with RM 0.00 in the table and in the copied text. Charge rows show at 0% too. | "Each person shows their items total" and "one person per line". Hiding rows would be a new rule. |
| PD-4 | Summary lines are joined with "\n" and have no trailing newline. | The brainstorm's block shows six lines and nothing after them. |
| PD-5 | The copy status stays until the next attempt or until the Shares table is replaced, and is never saved. | "Replaced by the next attempt" (`states.md`). Nothing says an edit clears it. |
| PD-6 | An unreadable draft is overwritten with the new bill at once, so the note does not return on reload. New bill does not touch the note. | "The app starts a new bill." A note that came back on every reload would contradict it. |
| PD-7 | Storage failures are silent, and the app keeps working in memory. | No copy exists for it and the brainstorm adds none. Crashing is worse. |
| PD-8 | A CSP meta `default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; base-uri 'none'; form-action 'none'`. **Changed twice on 2026-10-08.** It first read `style-src 'self'`, was relaxed to `style-src 'self' 'unsafe-inline'`, and was restored to `style-src 'self'` by ORCH ruling. | Backstop for name injection and a hard stop on network calls. Invisible. The relaxation was because harness 2.1.1 injected its freeze stylesheet with Playwright `add_style_tag` and exited with a CSP error under the strict policy (measured). Harness 2.1.2 renders with `bypass_csp`, so the strict policy came back. The functional suite and the live gate run without bypass and fail on any CSP console error, so they catch policy breakage. See N-1. |
| PD-9 | Name inputs always carry `placeholder="Person N"` or `"Item N"`. | Ruling 4. It renders nothing while the field holds text, so the goldens still match. |
| PD-10 | The draft decoder counts name length in grapheme clusters. | WebKit counts `maxlength` in grapheme clusters and Chromium in UTF-16 units. A name an iPhone let the user type must reload. |
| PD-11 | Rates print without trailing zeros ("10.00" shows as "10%", 6.5 as "6.5%"). | The goldens show "10%" and "6%" from the input "10" and "6". |
| PD-12 | `index.html` links `src/system.css` (a byte copy) instead of inlining it. | `system.md` says the build copies one stylesheet. Rendering is identical. |
| PD-13 | The fidelity gate runs the sdlc plugin harness with `--browser-arg=--disable-lcd-text`, `--color-scheme light`, `--dpr 1`, `--fixed-time 2026-10-08T09:00:00` and `--threshold 0.01`, and a pair passes only at 0 mismatching pixels with matching sizes. **Changed 2026-10-08.** It first described an own harness with a per-channel tolerance of 16. | Measured with the harness (2.1.0, then 2.1.1, same counts, 2.1.2 adds only the CSP bypass) on a scratch candidate built like the app. `bill-items` matched at threshold 0. The dialog's largest per-pixel distance was 0.0068 (390) and 0.0051 (1280), all glyph-edge anti-aliasing. Without the LCD flag the dialog differed by 2591 pixels at 390. |
| PD-14 | The dialog wraps Tab itself between its two buttons. | `new-bill-dialog.md` says Tab cycles between them. Measured that native `showModal()` lets Tab leave to the document (Cancel, body, Start new bill). |
| PD-15 | ~~Clipboard tests save and restore the human's clipboard text.~~ **WITHDRAWN 2026-10-08**, replaced by CG-7. | Reading the clipboard reads the owner's data. |
| PD-16 | The fidelity after-load script for the dialog blurs the focused button after opening it. | The harness's click is synthetic, so Chromium draws the keyboard focus ring on Cancel (0.48% of the 390 render, measured), which a real mouse open does not. The golden shows no ring. Focus on Cancel is checked with real gestures by R29. |

## Notes for the human (not blocking)
- **N-1. Harness and a strict style policy. Resolved 2026-10-08, ORCH.** The note said the strict policy needed a harness option to bypass the candidate's CSP (Playwright `bypass_csp`), a plugin change outside this project, so the plan had relaxed `style-src`. Harness 2.1.2 now renders with `bypass_csp` (control-tested by the orchestrator, 2.1.1 crashed on a `style-src 'self'` page and 2.1.2 scored it 0.0%), and the strict policy is restored (PD-8, R38).
- **N-2. Harness venv.** `harness/README.md` asks for a venv in `%USERPROFILE%\.sdlc-harness\.venv`. It did not exist at planning time. The system Python had the harness requirements (Playwright 1.61.0, Pillow 12.3.0, numpy 2.4.6) and ran the harness during planning. **Changed 2026-10-08, ORCH (CG-11).** `run.py` runs the harness with `sys.executable`, the same Python that runs pytest, and that Python has the harness requirements. The README venv is optional here, so the fidelity tester neither stops on a missing venv nor installs packages.
- **N-3. Harness 2.1.1 and later pin time through Playwright's clock** (default 2023-11-14T22:13:20Z, or `--fixed-time`). Split reads no clock, so nothing in a fidelity render relies on a live `Date.now`.

## Traceability
| Source | Requirements |
|---|---|
| C1 People | core R10, R11, R12, R17 · app R4, R5, R6, R7, R34 |
| C2 Even split | core R1, R7, R18, R20 · app R8, R9, R20 |
| C3 Split by item | core R13, R14, R19, R21 · app R11, R12, R13, R14, R18, R21 |
| C4 Charges | core R3, R5, R6 · app R15, R19 |
| C5 Shares that add up | core R7, R8, R9, R22, R23 · app R20, R21 |
| C6 Copy summary | core R24 · app R22, R23, R24 |
| C7 Draft kept | app R2, R25, R26, R27, R28 |
| C8 New bill | core R10 · app R29, R30, R31 |
| Money in whole cents, no floating point | core R1, R6, R8, R23, R25 |
| Platform (phone, keyboard, focus, reduced motion, static, offline) | app R1, R32, R33, R35, R36, R39 |
| Money written as in the brief ("RM 38.87": whole ringgit, a dot, two sen digits) and CG-5 | core R4 |
| Brainstorm rule "Switching modes keeps both sets of input" (decision 13) | core R15 · app R8 |
| Purity invariant (functions are pure, no input is mutated) | core R16 |
| Brainstorm rule "Duplicate names are allowed" | core R26 · app R42 |
| `bill-items.md`: the panel "is not a live region" | app R16 |
| Threat model (script injection through names, Content Security Policy) | app R37, R38 |
| RULINGS 1 to 4 | core R2 and app R10 (1) · app R15 (2) · core R18, R19 and app R17, R18 (3) · core R17 and app R4, R5 (4) |
| Clarify gate CG-1 to CG-11 (CG-9 to CG-11 added 2026-10-08) | see the Affects column above |
| Goldens S1, S2, S3, S5, M1 | app R3 (markup and copy) · app R40 (fidelity) and the element checklist |
| States S4, S6, S7, S8 | app R10, R14, R22, R23, R27, R6, R7 and checklist rows ST-01 to ST-13 |
| Definition of done (live gate) | app R41 |

Added 2026-10-08 (plan check FLAG): the entries for core R2, R4, R15, R16, R26 and app R3, R16, R37, R38, R42, each with its source above.

## Global non-goals (from the brainstorm)
Payments, transfer links or DuitNow QR. Accounts, login, sync, sharing links. Other currencies, conversion, other languages. OCR. A history of bills. 5-sen cash rounding. Tips, discounts, vouchers, per-item tax exemptions. A theme switcher. Each module's spec lists its own non-goals on top of these.
