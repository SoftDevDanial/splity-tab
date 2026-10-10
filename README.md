# Split

Split shares one restaurant bill between friends. Type who was there and either the subtotal or each item,
and it adds the service charge and SST, shares the total to the sen and copies a plain text summary for the
group chat. Everything stays in this browser. There is no account, no server and no network call.

Built end to end with the sdlc pipeline. The run's state is in `docs/progress/STATE.md` and every decision,
finding and fix of this version is in `docs/v1.0.0/CHANGE-LEDGER.md`.

## Status, v1.0.0

| Module | What it is | State |
|---|---|---|
| `split-core` | the money rules, pure functions, no DOM | closed 2026-10-09 |
| `split-app` | the page, the saved draft, the copy summary | closed 2026-10-09 |

- At v1.0.0, 427 browser tests and 275 unit tests pass.
- The page matches its five approved design screens to the pixel at 390 x 844 and 1280 x 800 (10 of 10 pairs, 0 mismatched pixels).
- The cold-boot live gate passes 7 of 7 steps with real gestures on the shipped page.
- QA, code review and security reviews are done, with their findings fixed or accepted below.

## Run it

```
python -m http.server 8000 --bind 127.0.0.1
```

Run that from the project root, then open `http://127.0.0.1:8000/`. Stop the server when you are done.
Any static host works. There is no build step and nothing to install.

## Test it

| What | Command | Evidence |
|---|---|---|
| Unit tests | `node --test "tests/**/*.test.js"` | none |
| Browser tests | `python -m pytest tests/browser -q` | a failure screenshot in `docs/modules/split-app/qa/functional/<ts>/` |
| Looks right (fidelity gate) | `python tests/browser/fidelity/run.py` | `docs/modules/split-app/qa/fidelity/<ts>/` |
| Works right (live gate) | `python tests/browser/live_e2e.py` | `docs/modules/split-app/qa/live-e2e/<ts>/` |

Node 24, Python with pytest and Playwright, headless Chromium. Each browser command starts and stops its own
local server and prints its PID and port. A bare `node --test tests/` fails on Node 24, so keep the quoted
glob. The fidelity gate uses the sdlc harness. `SDLC_HARNESS` points it at another copy.

The tests never touch the system clipboard. Every browser context gets a stand-in for
`navigator.clipboard.writeText` (a recorder by default, a rejecting or missing one for the failure tests),
and no clipboard permission is ever granted.

## How it is built

Vanilla JavaScript ES modules and plain CSS. Zero dependencies, no framework, no web fonts.

**`split-core`** (`src/core/`) holds every money rule. Amounts are integer sen.
- `parseAmount`, `parseRate`, `formatMoney`, `formatRate` read and write ringgit text.
- `allocateEvenly` and `allocateByWeight` share an amount so the parts always add up to the whole. `allocateByWeight` is the one place that uses `BigInt`.
- `billCharges` applies service charge and then SST on top, each with half-up rounding. `computeResult` builds the even split or the by-item split from the typed bill.
- `newBill`, `addPerson`, `removePerson`, `addItem`, `toggleItemPerson` and the other actions return a new bill and never change the old one.
- `summaryText` writes the copy summary, one line per row, with control and direction characters in names turned into spaces.

**`split-app`** (`src/main.js`, `src/draft.js`, `src/errors.js`, `src/ui/`) is the page.
- `src/main.js` boots the page, keeps the one bill, and routes every change to the bill through `commit`. The caller runs a core action (for example `commit(addPerson(bill))`), and `commit` takes the bill it returned, saves the draft and calls `render`. `render` reads the view state and never writes it. `setStatus` is the only writer of the copy status.
- `src/draft.js` saves and loads the draft (`getStorage`, `loadDraft`, `saveDraft`, `encodeDraft`, `decodeDraft`).
- `src/errors.js` holds the rules for when a field error shows, with their own unit tests. `newErrorFlags`, `flagsFor` and `visibleErrors` build or read the flags, and `typedInto`, `leftField` and `forgetPrice` update the flags they are given.
- `src/ui/` builds one block per section (`createX(handlers)` returns `{ el, update }`). Blocks write the DOM and report gestures. They never change the bill.
- `reconcileChildren` updates lists without re-inserting a node that is already in place, so typing never loses focus.
- `onFieldLeave` holds a field's error back until a press ends, so a tap on the button below an invalid field is never lost.
- `swallowRepeatClicks` cancels the repeat press of a double click, triple click or double tap, so it never lands on a control that moved under the pointer. It protects only the controls that arm it. Every Remove button, Add person, Add item, and the New bill dialog on open and close arm it. A Remove button also ignores a repeat press itself (`isRepeatClick`), so when a price error moves the rows and the second press of a double click lands on a Remove, nothing is removed.
- `createDialog` runs the New bill dialog. Cancel, Esc and Start new bill close it. A click on the backdrop closes it only if the press began on the backdrop too.

**The look.** `src/system.css` is a byte copy of the approved design's `system.css` plus one rule at the end,
`[hidden] { display: none !important; }`. No other CSS is added or changed.

## The saved draft

One key, `split.draft` in `localStorage`, holding `{ "version": 1, "bill": ... }`. It is saved after every
change and read once at boot.

`decodeDraft` treats the stored text as untrusted. It accepts a draft only when every rule D1 to D12 in
`docs/modules/split-app/spec.md` (Persistence) holds. Those rules cover the JSON shape, the mode, 2 to 12
people, 0 to 50 items, unique ids, names within their length, and the id counter. It builds the bill from
known fields only and never throws. A draft it cannot read gives a new bill and a short note saying so. If
storage is blocked or full, the page keeps working in memory.

## Security

- Names, prices and rates reach the page only as text (`textContent`, `value`, `setAttribute` on labels). `src/` contains no `innerHTML`, `eval` or similar.
- The page carries a strict Content Security Policy.
  ```
  default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; base-uri 'none'; form-action 'none'
  ```
- Nothing leaves the device. `src/` has no network API, and every test run checks that the only requests are same-origin GETs for the page's own files.
- **Publish only `index.html`, `src/` and a `.nojekyll` file.** Never serve the repository root. It holds build records, screenshots, local paths and deliberate mutant copies of `src/` used to prove the tests can fail.

## Known limits in v1.0.0

Each was found during this version and accepted on purpose. The reasoning is in the ledger,
`docs/modules/split-app/spec.md` (Residual risks) and `docs/modules/split-app/findings/security.md`.

| Limit | Planned |
|---|---|
| On a big bill (from about RM 650 of items) the by-item table is wider than a 360 px phone, so the page scrolls sideways (H-02) | fixed in v1.1.0 |
| Holding Enter on Remove of the only item adds one blank item, which one click removes (SEC-04) | fixed in v1.1.0 |
| A double click on Dismiss note or a mode label moves keyboard focus to the page. No data changes | kept |
| Another page on the same `github.io` origin can read the draft, and the page can be framed | kept, no way to isolate it on that host |
| Two tabs of one browser editing the bill overwrite each other, last save wins | kept, one draft per browser by design |
| A hand-edited draft can push the id counter to its ceiling, and the next save is unreadable | kept, only a page that can already overwrite the draft can do it |

## Where the record lives

- `docs/v1.0.0/CHANGE-LEDGER.md` lists every scope, decision, finding and fix, dated, with who decided.
- `docs/modules/<module>/spec.md` and `qa.md` hold the requirements and the test contract.
- `docs/modules/<module>/findings/` holds each review's verdict (QA, code review, security, fidelity).
- `docs/modules/<module>/qa/` holds the evidence of every run.
- `docs/design/` holds the approved design screens. They do not change outside the design phase.
