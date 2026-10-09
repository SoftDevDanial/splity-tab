# QA: split-app

> Test contract. Every functional scenario runs against the **running** app, served by
> `python -m http.server <port> --bind 127.0.0.1` from the project root and driven by headless Python
> Playwright (Chromium) with real gestures (clicks, typing, key presses). Gherkin tags map each scenario to
> an R# in `spec.md`, and every R# has at least one scenario. The fidelity gate and the cold-boot live-e2e
> gate run after the functional suite is green.

## How to run
- **Functional suite.** `python -m pytest tests/browser -q` from the project root. Test functions are named `test_R<n>_<what>` so a grep maps each one to its tag. This is the browser test command in `CLAUDE.md` (CG-6 ruled 2026-10-08, ORCH). `split-core`'s unit tests run with `node --test "tests/**/*.test.js"`.
- **Fidelity gate.** `python tests/browser/fidelity/run.py`, which serves the app and runs the sdlc plugin harness `{sdlc}/harness/fidelity.py` once per screen and width (see the Fidelity gate section). **Changed 2026-10-08 (CG-11):** `run.py` starts the harness with `sys.executable`, the Python that runs pytest, so the README venv is not needed.
- **Live gate.** `python tests/browser/live_e2e.py`.
- **Server lifecycle (every run).** The harness picks a free port by binding port 0, starts `python -m http.server <port> --bind 127.0.0.1` with the project root as working directory, waits for `GET /` to answer (at most 50 tries 100 ms apart, then it gives up and fails the run with "server gave up after 50 tries"), and in a `finally` block kills the server by PID, waits for it to exit (10 s cap) and re-checks that the port binds again. It prints the PID and port at start and STOPPED with the port re-check at the end, so the orchestrator can ledger it.
- **Browser.** `chromium.launch(headless=True)`. Never headed. A new context per scenario unless the scenario says "the same context". Viewport 390 x 844, device scale factor 1, colour scheme light, unless stated. No context is ever created with `bypass_csp`, so the shipped Content Security Policy is live in every scenario.
- **Seeding.** A scenario that starts from a stored bill passes it through Playwright `storage_state` when it creates the context (`origins[0].localStorage = [{ name: "split.draft", value: <seed> }]`). Nothing is ever injected into the app. No `window.__*` hook exists or is used. An init script that controls the **browser platform** (the clipboard scripts below, making `localStorage` throw) is allowed, because it emulates the browser, not the app, in the same way `page.clock` does.
- **Clipboard (CG-7, ruled 2026-10-08, ORCH).** No test ever touches the operating system clipboard, not even to read it, because it holds the owner's data. No clipboard permission is ever granted. Every browser context gets exactly one test-side init script from `tests/browser/clipboard/`.
  - `recorder.js` is the default for every context. It replaces `Clipboard.prototype.writeText` with a function that stores `String(text)` in `window.testClipboardText`, adds 1 to `window.testClipboardWrites`, and returns a resolved promise. Tests read `window.testClipboardText` and compare it exactly, `\n` line ends included.
  - `reject.js` (the failure path) replaces `writeText` with a function that returns `Promise.reject(new DOMException("Write permission denied.", "NotAllowedError"))`.
  - `missing.js` (the missing API) makes `navigator.clipboard` read as `undefined`.
  - A scenario that names `reject.js` or `missing.js` uses it instead of `recorder.js`. The app gets no hook. It calls the real `navigator.clipboard.writeText`, which is what these scripts replace.
- **Console and network.** Every scenario records console messages, page errors and requests. A console error, a page error, a CSP violation (Chromium logs every violation as a console error whose text contains "Content Security Policy") or a request that is not a same-origin GET (for `/`, `/src/system.css`, a file under `/src/` or `/favicon.ico`) fails the scenario, except where a scenario expects otherwise.
- **Evidence.** `docs/modules/split-app/qa/functional/<YYYYMMDD-HHMMSS>/` holds the pytest output (`pytest.txt`, `junit.xml`) and a screenshot for every failed scenario. Nothing is written to the project root or `docs/design/`.

## Seed drafts (test fixtures in `tests/browser/seeds.py`, the one source. The fidelity files `tests/browser/fidelity/seed-*.js` repeat them, and a functional test keeps them equal)
```text
S2  {"version":1,"bill":{"mode":"even","people":[{"id":"p1","name":"Aisyah"},{"id":"p2","name":"Ben"},{"id":"p3","name":"Chen"}],"subtotalText":"100.00","items":[],"serviceText":"10","sstText":"6","nextId":4}}
S1  {"version":1,"bill":{"mode":"item","people":[{"id":"p1","name":"Aisyah"},{"id":"p2","name":"Ben"},{"id":"p3","name":"Chen"}],"subtotalText":"","items":[{"id":"i4","name":"Nasi lemak ayam","priceText":"15.90","who":["p1"]},{"id":"i5","name":"Char kuey teow","priceText":"13.50","who":["p2"]},{"id":"i6","name":"Mee goreng mamak","priceText":"12.00","who":["p3"]},{"id":"i7","name":"Satay, 10 sticks","priceText":"18.00","who":["p1","p3"]}],"serviceText":"10","sstText":"6","nextId":8}}
S5  S1 with i6 "who":[]
S8  even, twelve people p1 to p12 named Aisyah, Ben, Chen, Devi, Farid, Grace, Hafiz, Indra, Jia Hui, Kumar, Lina, Mei Ling, subtotalText "", rates "10" and "6", nextId 13
```

### Unreadable drafts (each must give the S7 note, R27)
| Id | Stored value | Rule |
|---|---|---|
| B1 | `not json` | D1 |
| B2 | `[]` | D2 |
| B3 | `null` | D2 |
| B4 | S2 with `"version":2` | D3 |
| B5 | S2 with `"version":"1"` | D3 |
| B6 | `{"version":1,"bill":[]}` | D4 |
| B7 | S2 with `"mode":"split"` | D5 |
| B8 | S2 with only p1 | D6 |
| B9 | S2 with 13 people | D6 |
| B10 | S2 with person id `"x1"` | D6 |
| B11 | S2 with two people both id `"p1"` | D6 |
| B12 | S2 with `"name":5` | D6 |
| B13 | S1 with i4 `"who":["p9"]` | D7 |
| B14 | S1 with i4 `"who":["p1","p1"]` | D7 |
| B15 | S1 with 51 items | D7 |
| B16 | S1 with two items both id `"i4"` | D7 |
| B17 | S1 with i4 `"priceText":15.9` (a number) | D7 |
| B18 | S2 with Aisyah renamed `ABCDEFGHIJKLMNOPQRSTU` (21 characters) | D8 |
| B19 | S2 with Aisyah renamed `"Ai\nsyah"` | D8 |
| B20 | S1 with i4 named 41 characters | D8 |
| B21 | S2 with `"subtotalText":100` | D9 |
| B22 | S2 with `"nextId":3` (not above p3) | D10 |
| B23 | S2 with `"nextId":1.5` | D10 |
| B24 | S2 with `"nextId":2000000000` | D10 |

### Readable drafts that look odd (must load, R26 and D8, D11, D12)
| Id | Stored value | Expected |
|---|---|---|
| G1 | S2 plus a top-level `"extra":1` and a person key `"colour":"red"` | loads as S2. After one change the stored draft has neither key |
| G2 | S2 with Aisyah renamed to 20 copies of the Malaysian flag emoji (U+1F1F2 U+1F1FE, 20 grapheme clusters, 80 UTF-16 code units) | loads, the name shows in full |
| G3 | S2 with `"__proto__":{"polluted":true}` inside `bill` | loads as S2, and `({}).polluted` is `undefined` in the page |

## Functional test cases (Gherkin)
Phrases used below. "Replace the text of X with Y" means click X, press Control+A, then type Y key by key. "Leave the field" means press Tab. "The panel shows" reads the visible text of `div.tape`. "Equal to the specimen" (added 2026-10-08, plan check FLAG) means that these computed properties, read with `getComputedStyle`, are equal on the app element and on the named element of `states.html`: `color`, `background-color`, `font-size`, `font-weight`, the width, style and colour of each border side, `box-shadow`, the four `padding-*` values and the four corner radii. A row that needs one more property names it (for example `cursor`, `text-align` or `margin-top`). Width, height, position and anything that follows from them are never compared, because at 390 the specimen frames are narrower than the app (324 px of content in a frame against 358 px in a screen). **Changed 2026-10-08.** Before this date the rows said only that the computed styles "equal" the specimen's, with no property list, which a reader could take to include width. "Specimen properties" is short for that list.

```gherkin
Feature: Split app, served and driven like a person would

  # ---------- Shell and boot ----------
  @R1
  Scenario: The entry point loads only its own files
    Given a fresh context with empty storage
    When I open "/"
    Then the head holds, in order, charset utf-8, the viewport meta, the CSP meta, title "Split", a stylesheet link "src/system.css" and a module script "src/main.js"
    And html has lang "en"
    ~~And the SHA-256 of src/system.css equals that of docs/design/system.css~~
    # Changed 2026-10-09, ORCH, RD-1 (RC-5 wins). The file is the golden's bytes plus exactly one trailing rule,
    # "[hidden] { display: none !important; }" on its own line, so the two SHA-256 values differ by design.
    And the bytes of src/system.css equal the bytes of docs/design/system.css followed by "\n[hidden] { display: none !important; }\n"
    And no console error and no page error was logged
    And every request was a same-origin GET for "/", "/src/system.css", a file under "/src/" or "/favicon.ico"

  @R1
  Scenario: The page works from a sub-path, as on GitHub Pages
    Given a second server started with the project's parent folder as its root
    When I open "/split/"
    Then the S3 screen renders with no failed request and no console error
    And the static scan of index.html and src/ finds no src, href or import that starts with "/" or contains "://" (the SVG namespace string that R39 allows inside createElementNS is not a src, href or import)

  @R2
  Scenario: Cold boot is a new bill with no seed
    Given a fresh context with empty storage
    When I open "/"
    Then the people fields hold "Person 1" and "Person 2" and both remove buttons are disabled
    And "Even" is checked, Subtotal is empty with no error, Service charge is "10" and SST is "6"
    And the panel holds only the heading "Shares" and "Enter the subtotal to see the shares."
    And localStorage has no "split.draft" key
    And no own property of window starts with "__"

  @R2
  Scenario: No sample data ships
    Given the text of index.html and every file under src/
    Then none of these whole words appears: Aisyah, Ben, Chen, Devi, Farid, Grace, Hafiz, Indra, Jia Hui, Kumar, Lina, Mei Ling, Nasi lemak, Char kuey teow, Mee goreng, Satay

  @R3
  Scenario Outline: The rendered markup matches its golden
    Given the <state> state (cold boot, or seeded with <seed>)
    When the DOM walk in test_app.py compares the page's body with that of docs/design/<golden>.html (tag, class list, id, own text, role, every aria-* attribute, disabled, checked, maxlength, inputmode, placeholder, the input value property) and skips a closed dialog.dialog and every element that has the hidden attribute, with what is inside them
    Then every element, class list, id, ARIA attribute and text matches, apart from the allowed differences in spec.md
    Examples:
      | state | seed | golden          |
      | S3    | none | bill-empty      |
      | S2    | S2   | bill-even       |
      | S1    | S1   | bill-items      |
      | S5    | S5   | bill-unassigned |

  # ---------- People ----------
  @R4
  Scenario: Person rows carry their names and labels
    Given the S1 seed
    Then the three person inputs have aria-labels "Person 1 name", "Person 2 name", "Person 3 name", placeholders "Person 1", "Person 2", "Person 3", maxlength 20 and autocomplete off
    And their remove buttons are named "Remove Aisyah", "Remove Ben", "Remove Chen" and are enabled

  @R4 @R5
  Scenario: A blank name falls back to its position everywhere but the field
    Given the S1 seed
    When I replace the text of "Person 2 name" with nothing (Control+A, Backspace)
    Then that field shows the placeholder "Person 2"
    And its remove button is named "Remove Person 2"
    And every item's toggle for that person reads "Person 2"
    And the shares row reads "Person 2"

  @R5
  Scenario: Renaming a person updates every place on each keystroke
    Given the S1 seed (with the clipboard recorder, as every context)
    When I click the end of "Person 3 name" and type " Wei"
    Then after each key the toggles, the shares row and the remove name show the text typed so far
    And the toggles in all four items read "Chen Wei", the remove button is "Remove Chen Wei"
    When I click "Copy summary"
    Then line 5 of window.testClipboardText is "Chen Wei RM 24.48"

  @R5
  Scenario: Renaming an item updates its accessible names
    Given the S1 seed
    When I replace the text of "Item 4 name" with "Satay"
    Then the item's remove button is named "Remove Satay" and its group "Who had Satay"

  @R6
  Scenario: Add person until the limit
    Given a cold boot
    When I click "Add person"
    Then there are 3 person rows, the third input is empty with placeholder "Person 3"
    And all three remove buttons are enabled
    When I click "Add person" 9 more times
    Then there are 12 person rows and "Add person" has the disabled attribute
    And its specimen properties and its cursor (not-allowed) equal those of the "S8 12 people" button in states.html
    When I click "Add person" again
    Then there are still 12 person rows

  @R7
  Scenario: Remove a person and they leave every item
    Given the S1 seed
    When I click "Remove Chen"
    Then two person rows remain, Aisyah and Ben, and both remove buttons are disabled
    And every "Who had" group holds exactly the toggles "Aisyah" and "Ben"
    And the panel shows "1 item still needs a person. Tap who had it to see the shares."

  # Added 2026-10-09, ORCH, security audit SEC-01. A double click, a triple click and a double tap are two or three presses, and the
  # first one moves a different control under the pointer. Removing the last person slides "Add person" into the cell the row filled,
  # so the second click used to add a blank person. The tests are `test_R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing`
  # and the tests after it in the same section of `test_app.py`, up to the RG-CR-01 header. The code-review rows for a middle Remove (WR-01) are `test_R7_a_double_click_or_double_tap_on_remove_removes_one_row`
  # and `test_R7_two_separate_clicks_and_a_key_press_still_remove_a_row_each`.
  @R7
  Scenario Outline: A repeat press on the last Remove removes that row and adds nothing
    Given <bill> is the stored draft
    And the viewport is <size>
    When I <gesture> at the centre of <button>
    Then one row fewer shows and the stored draft is the bill that one click on <button> leaves (the last person or item gone, no blank row, "nextId" unchanged)
    And focus is on <focus>
    Examples:
      | bill                          | button                    | focus         |
      | S2                            | Remove Chen               | Person 2 name |
      | S8                            | Remove Mei Ling           | Person 11 name |
      | S1                            | Remove Satay, 10 sticks   | Item 3 name   |
      | S1 with only its last item    | Remove Satay, 10 sticks   | Add item      |
    # Sizes: 360 x 640, 390 x 844, 1280 x 800. Gestures: single click (the control), mouse double click, mouse triple click, touch double tap.

  @R34
  Scenario Outline: After a double click or double tap on a middle Remove, focus is where one click puts it
    Given <bill> is the stored draft
    When I double click, or double tap, <button>
    Then one row is gone and focus is on <focus>, not on the next Remove button or the page body
    Examples:
      | bill                        | button                | focus         |
      | the S1 bill                 | Remove Char kuey teow | Item 2 name   |
      | S2 with five people P1 to P5 | Remove P2             | Person 2 name |

  @R7
  Scenario: A press of its own is never held back
    Given the S2 seed
    When I click the centre of "Remove Chen" and then, as a separate click, the same point
    Then "Add person" was under the pointer for the second click, and it adds one person (the guard goes by click count 2 or more, not by time or place)
    When I click "Remove Nasi lemak ayam" in the S1 bill and then double click a toggle
    Then both presses and both clicks reach the page, so the toggle ends where it began (the guard is gone at the first press that is not a repeat; watching the clicks alone cannot see a guard that kept its press listener, RG-CR-02)
    When I click "Remove Chen" in the S2 bill and then double click "Person 1 name"
    Then the word "Aisyah" is selected (the user-visible side of the same lifetime)

  # Added 2026-10-09, ORCH, regression RG-CR-01. The new person's row takes the grid cell of the button that was pressed, so its Remove
  # button sits under the right 44 px of "Add person". Since SEC-01 a Remove acts on every click that reaches it, so the repeat press of a
  # double click used to remove the blank row it had just added (nothing added, one id spent, focus on the previous name). "Add person"
  # and "Add item" arm the guard now. The tests are `test_R6_a_repeat_press_on_add_person_adds_one_person_and_keeps_it` and
  # `test_R12_a_repeat_press_on_add_item_adds_one_item_and_never_reaches_the_page` in `test_app.py`, one row for each combination below.
  @R6
  Scenario Outline: A repeat press on Add person adds one person and keeps it
    Given the S2 bill with <people> people, P1 to P<people>, is the stored draft
    And the viewport is <size>
    When I <gesture> at <place> of "Add person"
    Then one person row more shows and the stored draft is that bill with one blank person added (the id counter moved once)
    And focus is on the name field of the new person
    Examples:
      | people     | place                                                         |
      | 2, 3, 4, 5 | the middle of the button (the control: it misses the new Remove) |
      | 2, 3, 4, 5 | 22 px in from its right edge (the middle of the new Remove)   |
    # Sizes: 360 x 640, 390 x 844, 1280 x 800. Gestures: mouse double click, mouse triple click, touch double tap.

  @R12
  Scenario Outline: A repeat press on Add item adds one item and never reaches the page
    Given the S1 bill cut to its first <items> items is the stored draft
    And a recorder on the page body for the mouse presses and clicks that reach it
    When I <gesture> at <place> of "Add item"
    Then one item row more shows and the stored draft is that bill with one blank item added
    And focus is on the name field of the new item
    And the body saw press 1 and click 1 only (the guard cancelled the rest; no Remove button is under "Add item", so the bill alone cannot show it)
    Examples:
      | items | place                                |
      | 1, 4  | the middle of the button             |
      | 1, 4  | 22 px in from its right edge         |
    # Sizes and gestures as above.

  @R42
  Scenario: Two people may have the same name (added 2026-10-08)
    Given a cold boot with the clipboard recorder
    When I replace "Person 1 name" with "Ben" and "Person 2 name" with "Ben", click "Add person" and type "Chen" into "Person 3 name"
    And I type "100.00" into Subtotal
    Then no p.error and no note exists and the first two person fields both hold "Ben"
    And the shares rows read Ben RM 38.87, Ben RM 38.87 and Chen RM 38.86 and the check row reads RM 116.60
    And two remove buttons are named "Remove Ben"
    When I click "Copy summary"
    Then lines 3 and 4 of window.testClipboardText are both "Ben RM 38.87"
    When I click "By item", click "Add item", type "Tea" in "Item 1 name", type "10.00" in "Item 1 price in RM" and click the second "Ben" toggle in "Who had Tea"
    Then only the second "Ben" toggle has aria-pressed "true"
    And the shares rows read Ben RM 0.00, RM 0.00, RM 0.00 and Ben RM 10.00, RM 1.66, RM 11.66 and Chen RM 0.00, RM 0.00, RM 0.00
    And the check row reads RM 10.00, RM 1.66, RM 11.66
    When I click the second "Remove Ben"
    Then two person rows remain, "Ben" and "Chen", and the panel shows "1 item still needs a person. Tap who had it to see the shares."
    And localStorage "split.draft" holds two people, p1 "Ben" and p3 "Chen"

  # ---------- Mode and subtotal ----------
  @R8
  Scenario: Switching modes keeps both sets of input
    Given a cold boot
    When I replace the text of Subtotal with "100.00"
    And I click "By item", click "Add item", type "Tea" in "Item 1 name", type "5.00" in "Item 1 price in RM" and click the "Person 1" toggle
    Then the Subtotal block is not rendered and the Items block is
    When I click "Even"
    Then Subtotal holds "100.00", the Items block is not rendered and the panel total is "RM 116.60"
    When I click "By item"
    Then item 1 is "Tea", "5.00", with "Person 1" pressed, and the panel total is "RM 5.83"
    When I reload the page
    Then the same by-item screen shows, and "Even" again shows "100.00"

  @R8
  Scenario: Arrow keys move between the modes
    Given a cold boot
    When I press Tab until the "Even" radio has focus and press ArrowRight
    Then "By item" is checked and the Items block is rendered

  @R9
  Scenario: The subtotal field drives the even split
    Given a cold boot
    Then the Subtotal input has id "subtotal", inputmode "decimal", autocomplete off, sits in span.field.money after the "RM" unit and is labelled "Subtotal in RM"
    When I type "100.00" into Subtotal
    Then the panel shows the S2 bill summary for two people with shares "RM 58.30" and "RM 58.30"

  @R10
  Scenario Outline: An inline error waits for the field to be left
    Given <setup>
    When I replace the text of <field> with "<bad>"
    Then no error paragraph exists for that field yet
    When I leave the field
    Then "<message>" shows in p.error with id "<error id>" and the input has aria-invalid "true" and an aria-describedby that starts with "<error id>"
    When I click back into <field>, press Control+A and type "<good>" key by key
    Then the error is gone after the first key that makes the text valid, before I leave the field
    Examples:
      | setup      | field                | bad    | message                     | error id           | good  |
      | a cold boot | Subtotal            | 0      | Enter an amount like 12.50  | subtotal-error     | 12.50 |
      | the S1 seed | "Item 2 price in RM" | 13.505 | Enter an amount like 12.50  | price-error-i5     | 13.50 |
      | a cold boot | "Service charge"     | 31     | Enter a rate from 0 to 30   | rate-service-error | 10    |
      | a cold boot | "SST"                | 20.01  | Enter a rate from 0 to 20   | rate-sst-error     | 6     |

  @R10
  Scenario: An empty field never shows an error
    Given a cold boot
    When I click Subtotal and leave the field
    And I replace the text of "Service charge" with nothing and leave the field
    Then no p.error exists on the page and no input has aria-invalid
    And the panel shows "Check the charges to see the shares."

  @R10
  Scenario: Typing invalid text in a focused field does not show the error early
    Given a cold boot
    When I type "abc" into Subtotal without leaving it
    Then no error shows and the panel shows "Enter the subtotal to see the shares."

  @R10
  Scenario: A restored invalid field shows its error at once
    Given the S2 seed with "subtotalText":"0"
    When the page loads
    Then the Subtotal error "Enter an amount like 12.50" shows without any interaction

  @R10
  Scenario: An error survives a mode switch
    Given a cold boot with "0" typed in Subtotal and the field left
    When I click "By item" and then "Even"
    Then the Subtotal error still shows

  # Added 2026-10-09, ORCH, RD-3. A press that ends the edit of an invalid field must still land on the control it started on.
  # The tests use a mouse and a touch tap (a context with has_touch, page.touchscreen.tap) and were shown red without the fix.
  @R10 @R13
  Scenario Outline: A press below an invalid field lands on the control it started on
    Given <setup>
    When I replace the text of <field> with "<bad>" and the error is not showing yet
    And I press once, with the mouse and again with a touch tap, on <target> (the middle of the control, found before the press)
    Then the click event reached <target> exactly once
    And the error "<error id>" shows after the press and the input has aria-invalid "true"
    Examples:
      | setup       | field                | bad    | target                                   | error id           |
      | a cold boot | Subtotal             | 0      | the "Service charge" input               | subtotal-error     |
      | the S1 seed | "Item 2 price in RM" | 13.505 | the "Aisyah" toggle in "Who had Char kuey teow" | price-error-i5 |
      | a cold boot | "Service charge"     | 31     | p.hint#charges-hint                      | rate-service-error |
      | a cold boot | "SST"                | 25     | p.hint#charges-hint                      | rate-sst-error     |

  @R13
  Scenario: A tap on a person below an invalid, unflagged price toggles them and then shows the error
    Given the S1 seed
    When I replace the text of "Item 2 price in RM" with "13.505"
    And I press the "Aisyah" toggle of "Who had Char kuey teow" (mouse, then touch)
    Then that toggle has aria-pressed "true", the item holds p1 and p2 in the stored draft, and p.error#price-error-i5 shows

  @R10
  Scenario: The error waits for the release, and only a press holds it back
    Given the S1 seed and "13.505" typed in "Item 2 price in RM"
    When the mouse button goes down on a toggle
    Then the field has lost focus and still no p.error exists
    When the button comes up
    Then p.error#price-error-i5 exists
    And pressing empty space beside the wordmark behaves the same for "SST" with "25"
    And a Tab from the field shows its error at once, even after an earlier press

  # ---------- Items ----------
  @R11
  Scenario: Item rows carry their names and labels
    Given the S1 seed
    Then item j (1 to 4) has a name input labelled "Item j name" with placeholder "Item j", maxlength 40, autocomplete off
    And a price input labelled "Item j price in RM" with inputmode "decimal" in span.field.money after the "RM" unit
    And remove buttons named "Remove Nasi lemak ayam", "Remove Char kuey teow", "Remove Mee goreng mamak", "Remove Satay, 10 sticks"

  @R12
  Scenario: Add an item, remove one, and reach the limit
    Given a cold boot and I click "By item"
    When I click "Add item"
    Then one item row exists with an empty name (placeholder "Item 1"), an empty price and no toggle pressed
    And the panel shows "Give every item a price to see the shares."
    When I click "Add item" 49 more times
    Then 50 item rows exist and "Add item" has the disabled attribute, and its specimen properties and cursor equal those of the "S8 12 people" button in states.html (not its width, because "Add item" has its natural width and the specimen button fills a cell)
    When I click the remove button of item 2
    Then 49 item rows exist and "Add item" is enabled

  @R13
  Scenario: Tapping a person on an item
    Given the S1 seed
    When I click the "Ben" toggle in "Who had Satay, 10 sticks"
    Then that toggle has aria-pressed "true"
    And the shares rows read Aisyah RM 21.90, RM 3.64, RM 25.54 and Ben RM 19.50, RM 3.24, RM 22.74 and Chen RM 18.00, RM 2.98, RM 20.98
    And the check row reads RM 59.40, RM 9.86, RM 69.26
    When I click the same toggle again
    Then it has aria-pressed "false" and the S1 shares return

  @R14
  Scenario: A price error sits in the item line
    Given the S1 seed
    When I replace the text of "Item 2 price in RM" with "13.505" and leave the field
    Then p.error#price-error-i5 is the last child of that item's div.item-line
    And its specimen properties, its text-align (right) and its margin-top (0) equal those of #s4-price-error in states.html
    And the price input has aria-describedby "price-error-i5"

  # ---------- Charges ----------
  @R15
  Scenario: The Charges block and its defaults
    Given a cold boot
    Then "Service charge in percent" holds "10" and "SST in percent" holds "6", each followed by a "%" unit
    And both inputs have aria-describedby "charges-hint"
    And the hint reads "Set a charge to 0 if your bill already includes it."

  @R15
  Scenario: A rate error names both ids and its range
    Given a cold boot
    When I replace the text of "Service charge" with "31" and leave the field
    Then p.error#rate-service-error "Enter a rate from 0 to 30" is the last child of the Service charge cell
    And the input's aria-describedby is "rate-service-error charges-hint"

  @R15 @R19
  Scenario: A charge of 0 is allowed and still shown
    Given the S2 seed
    When I replace the text of "Service charge" with "0"
    Then no error shows, the Service charge row reads "RM 0.00" with "0% of RM 100.00"
    And the SST row reads "RM 6.00" with "6% of RM 100.00" and the shares are RM 35.34, RM 35.33, RM 35.33

  # ---------- Panel ----------
  @R16
  Scenario: The panel follows every keystroke and stays quiet
    Given the S2 seed
    When I replace the text of Subtotal with "5"
    Then the panel total is "RM 5.83" and the shares are RM 1.95, RM 1.94, RM 1.94
    When I type "0"
    Then the panel total is "RM 58.30" and the shares are RM 19.44, RM 19.43, RM 19.43
    ~~And no element inside div.tape has aria-live or role status, alert or log~~
    # Changed 2026-10-09, ORCH, RD-2. The old line contradicts the DOM contract, where p.status[role=status] is inside div.tape (R24).
    # The rule is: p.status[role=status] is the only live element in the tape. The tape and its sections carry no aria-live and no role.
    And p.status[role=status] is the only element inside div.tape with aria-live or a role of status, alert or log, and div.tape and its sections carry none

  @R17
  Scenario Outline: When the shares cannot be worked out
    Given <setup>
    Then the panel holds only the "Shares" heading and the message "<message>"
    And there is no Bill summary, no table, no "Copy summary" and no status element
    Examples:
      | setup                                                         | message                                    |
      | the S2 seed with Service charge emptied                        | Check the charges to see the shares.       |
      | the S1 seed with SST replaced by "25"                          | Check the charges to see the shares.       |
      | the S2 seed with Subtotal emptied                              | Enter the subtotal to see the shares.      |
      | a cold boot, then a click on "By item"                         | Add an item to see the shares.             |
      | a cold boot, "By item", then "Add item"                        | Give every item a price to see the shares. |
      | the S1 seed with "Item 1 price in RM" replaced by "abc"        | Give every item a price to see the shares. |

  @R18
  Scenario: Items that still need a person
    Given the S1 seed
    When I click the "Chen" toggle in "Who had Mee goreng mamak"
    Then the Bill summary still shows RM 59.40, RM 5.94, RM 3.92 and RM 69.26
    And the Shares section holds "1 item still needs a person. Tap who had it to see the shares." and no table, "Copy summary" or status
    When I click the "Ben" toggle in "Who had Char kuey teow"
    Then the message is "2 items still need a person. Tap who had each one to see the shares."
    When I press both toggles again
    Then the table, the check row and "Copy summary" return with the S1 numbers

  @R19
  Scenario Outline: The bill summary shows its working
    Given the <seed> seed
    Then the rows read "Subtotal" <sub>, "+ Service charge" <svc> with "<w1>", "+ SST" <sst> with "<w2>", "= Total" <total>
    And the Total amount sits in span.final
    Examples:
      | seed | sub       | svc      | w1               | sst     | w2              | total     |
      | S2   | RM 100.00 | RM 10.00 | 10% of RM 100.00 | RM 6.60 | 6% of RM 110.00 | RM 116.60 |
      | S1   | RM 59.40  | RM 5.94  | 10% of RM 59.40  | RM 3.92 | 6% of RM 65.34  | RM 69.26  |

  @R20
  Scenario: The even split from a cold boot (key flow 1)
    Given a cold boot
    When I replace "Person 1 name" with "Aisyah" and "Person 2 name" with "Ben", click "Add person" and type "Chen" into "Person 3 name"
    And I type "100.00" into Subtotal
    Then the shares table has hidden heads "Person" and "Share" and rows Aisyah RM 38.87, Ben RM 38.87, Chen RM 38.86
    And the check row reads "Adds up to" RM 116.60

  @R21
  Scenario: The by-item split from gestures (key flow 2)
    Given the even bill of the previous scenario
    When I click "By item" and, for each S1 item in order, click "Add item", type its name and price and click its people's toggles
    Then the table heads are "Items", "+ Charges", "= Share"
    And the rows read Aisyah RM 24.90, RM 4.14, RM 29.04 and Ben RM 13.50, RM 2.24, RM 15.74 and Chen RM 21.00, RM 3.48, RM 24.48
    And the check row reads RM 59.40, RM 9.86, RM 69.26

  @R21
  Scenario: Someone who had nothing is still listed
    Given the S1 seed changed by gestures into split-core's I2 bill (items "10.00" for Ben and "5.01" for Ben and Chen)
    Then the rows read Aisyah RM 0.00, RM 0.00, RM 0.00 and Ben RM 12.51, RM 2.08, RM 14.59 and Chen RM 2.50, RM 0.41, RM 2.91
    And the check row reads RM 15.01, RM 2.49, RM 17.50

  # ---------- Copy summary ----------
  @R22
  Scenario Outline: Copy summary puts the exact text on the clipboard
    Given the <seed> seed with the clipboard recorder
    When I click "Copy summary"
    Then p.status reads "Summary copied" and its class list is exactly "status"
    And window.testClipboardText equals the <seed> block of split-core spec R24 exactly, joined with "\n"
    And window.testClipboardWrites is 1
    Examples:
      | seed |
      | S2   |
      | S1   |

  @R23
  Scenario: The browser blocks the clipboard
    Given the S2 seed with the clipboard script reject.js
    When I click "Copy summary"
    Then p.status reads "Could not copy. Your browser blocked the clipboard." and its class list is "status status-failure"
    And no page error was logged and the bill is unchanged

  @R23
  Scenario: The clipboard API is missing
    Given the S2 seed with the clipboard script missing.js
    When I click "Copy summary"
    Then p.status reads "Could not copy. Your browser blocked the clipboard." and no page error was logged

  @R24
  Scenario: The status lives as long as the table
    Given the S2 seed
    Then p.status exists, is empty and is not displayed
    When I click "Copy summary" (clipboard recorder)
    Then the status reads "Summary copied"
    When I type "x" at the end of "Person 1 name"
    Then the status still reads "Summary copied"
    When I empty Subtotal
    Then no status element exists
    When I type "100.00" into Subtotal
    Then p.status exists and is empty
    When I click "Copy summary" and reload
    Then p.status is empty

  # ---------- Draft ----------
  @R25
  Scenario Outline: Every change is saved
    Given a cold boot
    When I <change>
    Then localStorage "split.draft" parses to { "version": 1, "bill": ... } whose bill <expectation>
    Examples:
      | change                                   | expectation                                   |
      | type "A" into "Person 1 name"            | has people[0].name "A"                        |
      | click "Add person"                       | has 3 people and nextId 4                     |
      | type "1" into Subtotal                   | has subtotalText "1"                          |
      | click "By item"                          | has mode "item"                               |
      | click "By item", then "Add item"         | has one item { id "i3", name "", priceText "", who [] } |
      | replace "SST" with "8"                   | has sstText "8"                               |

  @R25
  Scenario: Leaving a field or copying does not save
    Given the S2 seed loaded and the stored text noted
    When I click Subtotal and leave it, and click "Copy summary"
    Then the stored text is unchanged

  @R26
  Scenario: Come back later (key flow 3)
    Given the S1 bill built by gestures in one page, with Subtotal "100.00" typed earlier in even mode
    When I close the page and open "/" in a new page of the same context
    Then every person, item, price, toggle and rate is as before and "By item" is checked
    And the shares match S1
    When I click "Even"
    Then Subtotal holds "100.00"

  @R26
  Scenario Outline: Odd but readable drafts load
    Given the <id> seed
    When the page loads
    Then no note shows and <expected>
    Examples:
      | id | expected                                                              |
      | G1 | the S2 screen shows, and after one edit the stored draft has no "extra" or "colour" key |
      | G2 | Person 1 shows the 20 flags in full                                    |
      | G3 | the S2 screen shows and ({}).polluted is undefined                    |

  @R27
  Scenario Outline: An unreadable draft starts a new bill with a note
    Given the <id> seed
    When the page loads
    Then the S7 note reads "Your saved bill could not be read, so a new one was started." in div.note[role=status] with a "Dismiss note" button
    And the S3 screen shows under it
    And localStorage "split.draft" now parses to the new bill
    When I reload
    Then no note shows
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

  @R27
  Scenario: Dismissing the note
    Given the B1 seed
    When I click "Dismiss note"
    Then the note is no longer in the DOM and "Person 1 name" has focus
    And opening the New bill dialog and pressing Start new bill never brings a note back

  @R28
  Scenario Outline: The app works without storage
    Given a cold boot with an init script that <breaks storage>
    When I type "100.00" into Subtotal and click "Add person"
    Then the panel shows a total of "RM 116.60" with three shares
    And no message about storage shows and no page error or console error was logged
    Examples:
      | breaks storage                                                  |
      | makes reading window.localStorage throw a SecurityError          |
      | makes Storage.prototype.getItem throw                            |
      | makes Storage.prototype.setItem throw a QuotaExceededError       |

  # ---------- New bill ----------
  @R29
  Scenario: The dialog opens with the safe choice focused
    Given the S2 seed
    When I click "New bill" with the mouse
    Then dialog.dialog matches ":modal", is named "Start a new bill?" and described by "This clears the people, items and amounts."
    And "Cancel" has focus
    When I press Tab
    Then "Start new bill" has focus
    When I press Tab
    Then "Cancel" has focus
    When I press Shift+Tab twice
    Then "Cancel" has focus
    And .app is as tall as the viewport and a mouse wheel over the page leaves window.scrollY at 0

  @R30
  Scenario Outline: Leaving the dialog without starting over
    Given the S2 seed and the stored draft text noted
    When I click "New bill" and then <close>
    Then <open state>
    And the screen still shows the S2 bill and the stored draft text is unchanged
    And "New bill" has focus once the dialog is closed
    Examples:
      | close                                        | open state                                                     |
      | click "Cancel"                               | the dialog is closed                                           |
      | press Escape                                 | the dialog is closed                                           |
      | click the backdrop at (10, 10)               | the dialog is closed                                           |
      | click the backdrop over "Person 1 name"      | the dialog is closed and "Person 1 name" does not have focus   |

  # Added 2026-10-09, ORCH, security audit I-1. A double click on "New bill" used to flash the dialog open and shut: the second
  # click landed on the backdrop of the dialog the first had opened. Opening now arms the guard that closing already armed (R30, CR-01).
  # The tests are `test_R29_a_repeat_press_on_new_bill_leaves_the_dialog_open` (9 rows) and the three after it in `test_app.py`.
  @R29
  Scenario Outline: A repeat press on New bill leaves the dialog open
    Given the S1 seed at <size>
    When I <gesture> at the centre of "New bill"
    Then the dialog is open, "Cancel" has focus, only the first click reached the page and the stored draft is unchanged
    Examples:
      | size                              | gesture                                   |
      | 360 x 640, 390 x 844, 1280 x 800  | mouse double click, mouse triple click, touch double tap |

  @R30
  Scenario Outline: After a double click on New bill one deliberate click still closes it
    Given the S1 seed and a double click on "New bill" has opened the dialog
    When I <close>
    Then the dialog is closed, "New bill" has focus and the stored draft is unchanged
    Examples:
      | close                  |
      | click "Cancel"         |
      | click the backdrop at (10, 10) |
      | press Escape           |

  @R29
  Scenario: The keyboard and the next press are not held back
    Given the S2 seed
    When I focus "New bill", press Enter, Enter on "Cancel" and Enter on "New bill" again
    Then the dialog opens, closes and opens again, with "Cancel" focused each time it is open (a key press has click count 0)
    When I open the dialog by click, press Escape and double click a toggle on the S1 bill
    Then both presses and both clicks reach the page (the guard of the opening click is gone at the first press that is not a repeat)

  # Changed 2026-10-08, plan check FLAG. The scenario was: Given the S1 seed with a copy already made (status "Summary copied") and an error showing
  # on "Item 2 price in RM", When I click "New bill" and then "Start new bill", Then ... no error and no status shows.
  # That Given cannot happen, because a price error blocks the panel (R17) and the status lives only while the table does (R24).
  # The Then also passed when the view state was never reset, because the new bill is blocked and every field is empty or valid.
  # It is now three scenarios. Each Given can happen, and each check fails when the reset is missing.
  @R31
  Scenario: Start over (key flow 4)
    Given the S1 seed
    When I click "New bill" and then "Start new bill"
    Then the dialog is closed, "New bill" has focus and the S3 screen shows
    And "Person 1 name" and "Person 2 name" hold "Person 1" and "Person 2", "Even" is checked, Subtotal is empty, and Service charge and SST hold "10" and "6"
    And localStorage "split.draft" parses to { "version": 1, "bill": <the newBill() value of split-core R10> }
    When I reload
    Then the S3 screen shows

  @R31
  Scenario: Start over clears the copy status
    Given the S2 seed (with the clipboard recorder)
    When I click "Copy summary"
    Then p.status reads "Summary copied"
    When I click "New bill" and then "Start new bill"
    Then no p.status element exists and the panel holds only "Enter the subtotal to see the shares."
    When I type "100.00" into Subtotal
    Then the table is back and p.status exists and is empty

  @R31
  Scenario Outline: Start over clears the error flags
    Given <setup>
    And the error of that field shows
    When I click "New bill" and then "Start new bill"
    And <prepare>
    Then no p.error exists and no input has aria-invalid
    When I replace the text of <field> with "abc" without leaving the field
    Then still no p.error exists and no input has aria-invalid (R10 a: a stale flag would show the error at once)
    When I leave the field
    Then the error of <field> shows, so the rule still works after a start over
    Examples:
      | setup                                                                          | prepare                                                                         | field                |
      | the S2 seed, "Subtotal" replaced with "0" and the field left                    | nothing                                                                         | Subtotal             |
      | the S1 seed, "Item 2 price in RM" replaced with "13.505" and the field left (item id i5) | click "By item" and click "Add item" 3 times (the new items get ids i3, i4 and i5) | "Item 3 price in RM" |
      | a cold boot, "Service charge" replaced with "31" and the field left             | nothing                                                                         | "Service charge"     |
      | a cold boot, "SST" replaced with "25" and the field left                        | nothing                                                                         | "SST"                |

  # ---------- Keyboard, focus, layout, motion ----------
  @R32
  Scenario Outline: Tab order follows the golden
    Given the <state> state
    When I press Tab repeatedly from the top of the page
    Then the focused controls' accessible names come in exactly this order: <order>
    And each focused control shows a 2px solid ink outline at 2px offset (on span.field for inputs, at -3px on the person remove button, on fieldset.mode for the radios)
    Examples:
      | state | order |
      | S3    | New bill, Person 1 name, Person 2 name, Add person, Even, Subtotal in RM, Service charge in percent, SST in percent |
      | S1    | New bill, Person 1 name, Remove Aisyah, Person 2 name, Remove Ben, Person 3 name, Remove Chen, Add person, By item, then for each item j: Item j name, Item j price in RM, Remove <item>, Aisyah, Ben, Chen, then Add item, Service charge in percent, SST in percent, Copy summary |
      | S7    | New bill, Dismiss note, Person 1 name, Person 2 name, Add person, Even, Subtotal in RM, Service charge in percent, SST in percent |

  @R33
  Scenario Outline: Typing never loses its place
    Given the S1 seed (the S2 seed for Subtotal)
    When I take a handle to <field>, click it, press Control+A and type "<text>" key by key
    Then after every key the same element is document.activeElement and its selectionStart equals the number of characters typed so far
    When I press Home and type "X"
    Then the value starts with "X" and selectionStart is 1
    Examples:
      | field                 | text   |
      | "Person 1 name"       | Aisyah |
      | "Item 1 name"         | Nasi   |
      | "Item 1 price in RM"  | 15.90  |
      | Subtotal              | 100.00 |
      | "Service charge"      | 12.5   |

  @R33
  Scenario: IME composition survives a render
    Given the S1 seed and a CDP session on the page
    When I focus "Person 1 name", send Input.imeSetComposition for "jia" and then Input.insertText "家"
    Then the field value ends with "家", the same element has focus and no composed text was lost

  @R34
  Scenario Outline: Focus after adding or removing
    Given <setup>
    When I <action>
    Then <target> has focus
    Examples:
      | setup                         | action                                   | target                    |
      | a cold boot                   | click "Add person"                       | "Person 3 name"           |
      | the S1 seed                   | click "Remove Ben"                       | "Person 2 name" (Chen)    |
      | the S1 seed                   | click "Remove Chen"                      | "Person 2 name" (Ben)     |
      | the S1 seed                   | click "Add item"                         | "Item 5 name"             |
      | the S1 seed                   | click "Remove Char kuey teow"            | "Item 2 name" (Mee goreng mamak) |
      | the S1 seed                   | click "Remove Satay, 10 sticks"          | "Item 3 name"             |
      | a cold boot, "By item", one item added | click "Remove Item 1"           | "Add item"                |

  @R35
  Scenario Outline: No horizontal overflow at phone and desktop sizes
    Given the <state> state at <viewport>
    Then document.documentElement.scrollWidth is at most window.innerWidth
    And the people grid has <columns> columns
    And the bill panel is <panel>
    Examples:
      | state | viewport  | columns | panel                                   |
      | S1    | 360 x 780 | 2       | after the Charges block                 |
      | S2    | 360 x 780 | 2       | after the Charges block                 |
      | S3    | 360 x 780 | 2       | after the Charges block                 |
      | S5    | 360 x 780 | 2       | after the Charges block                 |
      | S1    | 390 x 844 | 2       | after the Charges block                 |
      | S1    | 1280 x 800 | 3      | in the right column with position sticky |
      | S3    | 1280 x 800 | 3      | in the right column with position sticky |
      | M1 (S2 seed, dialog open) | 360 x 780 | 2 | after the Charges block |

  @R35
  Scenario: Sizes the design gives at 360 x 780 (added 2026-10-08, plan check FLAG)
    Given the S2 seed at 360 x 780 with the clipboard script reject.js
    Then the span.field.money of Subtotal is 160 px wide
    When I click "Copy summary"
    Then p.status.status-failure has text-align center and is 40 px tall (two 20 px lines)
    And p.status has no overflow of its own (scrollWidth at most clientWidth) and its right edge is at most 360
    And document.documentElement.scrollWidth is at most window.innerWidth
    When I click "New bill"
    Then dialog.dialog is 328 px wide and p.dialog-text is 48 px tall (two 24 px lines)
    And document.documentElement.scrollWidth is at most window.innerWidth

  @R35
  Scenario: Content width at 1280 x 800 (added 2026-10-08, plan check FLAG)
    Given the B1 seed at 1280 x 800
    Then div.note is 1040 px wide
    And header.bar is 1104 px wide with 32 px of padding on each side, so its content is 1040 px wide

  # Changed 2026-10-08, plan check FLAG. The step was: And after load and after clicking a toggle, document.getAnimations() is empty.
  # Under no-preference that is a race with the 120 ms colour transitions (measured: two CSSTransitions, background-color and color,
  # right after a click, and none 400 ms later). The count now waits 500 ms. The reduce row keeps "empty right after the click".
  @R36
  Scenario Outline: Motion follows the user's setting
    Given the S1 seed with reduced motion "<setting>"
    Then the computed transition-duration of ".btn", ".tap", ".icon-btn" and ".mode label" is "<duration>"
    And right after load document.getAnimations() is empty
    When I click a toggle
    Then <right after the click>
    When I wait 500 ms
    Then document.getAnimations() is empty, so no transition is still running
    Examples:
      | setting        | duration     | right after the click                                                            |
      | reduce         | 0s           | document.getAnimations() is empty                                                |
      | no-preference  | 0.12s, 0.12s | every animation listed is a CSSTransition of background-color or color           |

  # ---------- Security ----------
  # Changed 2026-10-08, plan check BLOCK, CG-9. The scenario typed "<img src=x onerror=alert(1)>" (28 characters) into "Person 1 name",
  # whose maxlength is 20 (R4, D8), and expected line 3 of window.testClipboardText to be "<img src=x onerror=alert(1)> RM 29.04".
  # No conformant build can hold that name (typing it leaves "<img src=x onerror=a"), so the test always failed.
  # The person payload is now "<svg onload=f()>" (16 characters). The img payload went to an item name (maxlength 40).
  @R37
  Scenario: Names are shown as text, never as markup
    Given the S1 seed (with the clipboard recorder), and the number of svg elements under body noted
    When I replace "Person 1 name" with "<svg onload=f()>", "Item 1 name" with "<img src=x onerror=alert(1)>" and "Item 2 name" with "\"><script>alert(2)</script>"
    Then "Person 1 name" holds exactly "<svg onload=f()>" (16 characters, nothing cut by maxlength 20) and "Item 1 name" holds exactly "<img src=x onerror=alert(1)>" (28 characters)
    And that person's toggle in every item, the first shares row and the person's remove button ("Remove <svg onload=f()>") show those exact characters
    And item 1's remove button is named "Remove <img src=x onerror=alert(1)>" and its group is named "Who had <img src=x onerror=alert(1)>"
    And no img or script element exists under body apart from the module script in head
    And the number of svg elements under body is the number noted, every one is an icon with class "ph", and no element has an onload or onerror attribute
    And no dialog event fired and no page error was logged
    When I click "Copy summary"
    Then line 3 of window.testClipboardText is "<svg onload=f()> RM 29.04"
    And the static scan of src/ finds none of innerHTML, outerHTML, insertAdjacentHTML, document.write, eval(, new Function(, setAttribute("on, createContextualFragment or DOMParser
    And the static scan of index.html and src/ finds no "<template" tag

  @R38
  Scenario: The Content Security Policy is exact and never violated
    Given index.html
    Then it carries exactly the CSP meta of spec R38 and no inline script, style attribute or style element
    And across the whole functional suite no console message mentions "Content Security Policy"

  @R38
  Scenario Outline: The strict policy blocks nothing the app needs
    Given the <state> state in a context without bypass_csp
    Then the stylesheet applies (the computed background colour of body is "rgb(238, 240, 238)", the --page token)
    And the module ran (the people rows and the Charges inputs exist and the panel shows <panel>)
    And no element under body carries a style attribute
    And no console message mentions "Content Security Policy" and no page error was logged
    Examples:
      | state                                  | panel                                      |
      | S3, a cold boot                        | "Enter the subtotal to see the shares."    |
      | S1 seed                                | the S1 table and check row                 |
      | S2 seed with the New bill dialog open  | the S2 table, under the open dialog        |

  # Changed 2026-10-08, plan check BLOCK, CG-10. The scan was: none of fetch(, XMLHttpRequest, WebSocket, EventSource, sendBeacon,
  # serviceWorker or a "scheme://" URL appears. The icons need createElementNS, which takes the SVG namespace string, so that scan
  # failed on any build that follows the DOM contract. Exactly that one string is now exempt, in exactly one position.
  @R39
  Scenario: Nothing leaves the device
    Given the static scan of src/
    Then none of fetch(, XMLHttpRequest, WebSocket, EventSource, sendBeacon or serviceWorker appears
    And after removing every occurrence of createElementNS( followed by the exact string "http://www.w3.org/2000/svg" as its first argument (in single, double or backtick quotes), no "scheme://" string remains in any file under src/
    And the namespace string "http://www.w3.org/2000/svg" appears nowhere else (not as a second argument, not in a comment, not in another call), and no other namespace or URL appears
    And index.html holds no "scheme://" string at all
    And the request logs of every scenario in the suite hold only same-origin GETs for "/", "/src/system.css", files under "/src/" and "/favicon.ico"

  @R39
  Scenario: The SVG icons come from createElementNS (added 2026-10-08)
    Given the static scan of src/ and the S1 seed page
    Then at least one call createElementNS("http://www.w3.org/2000/svg", ...) exists in src/
    And none of innerHTML, insertAdjacentHTML, createContextualFragment or DOMParser appears in src/, and neither index.html nor src/ holds a "<template" tag
    And the page holds 11 svg.ph icons (7 X, 2 plus, 1 check, 1 copy), each with viewBox "0 0 256 256", aria-hidden "true", focusable "false" and one path

  # ---------- Gates ----------
  @R40
  Scenario: Looks right
    When the fidelity gate below runs
    Then all ten screen and viewport pairs pass and every FE element checklist row passes

  @R40
  Scenario: The runner uses the Python that runs pytest (added 2026-10-08, CG-11)
    Given the source of tests/browser/fidelity/run.py
    Then it starts the harness as [sys.executable, <path to fidelity.py>, ...]
    And it holds no path to a virtual environment (no ".sdlc-harness") and never runs pip or any installer
    And importing playwright, PIL and numpy in the Python that runs the test succeeds, so the harness requirements are met by that same Python

  @R41
  Scenario: Works right
    When the cold-boot live-e2e gate below runs
    Then it passes and its evidence artifact exists
```

## FE element checklist
Each row passes or fails on its own. "Matches" means the same element, classes, text, ARIA and computed styles as the golden at 390 x 844 and at 1280 x 800, with the state reached as in the fidelity gate. Rows marked "as" repeat an earlier row's check on this golden's render. Rows added 2026-10-08 that name another viewport (S2-28, M1-09, ST-14, ST-15) are checked at that viewport by the R35 scenarios.

### S1 `docs/design/bill-items.html`
| Id | Element | Expected |
|---|---|---|
| S1-01 | Wordmark `h1.wordmark` | "Split", 22/28 700, ink, letter-spacing -0.01em |
| S1-02 | Header button | `.btn.btn-outline` "New bill", field fill, line-strong border, 15/20 600, right end of `.bar` |
| S1-03 | People heading | `h2.block-title#h-people` "People", 18/24 700 |
| S1-04 | Person 1 field | `li.field.person`, input value "Aisyah", aria-label "Person 1 name", maxlength 20 |
| S1-05 | Person 1 remove | `.icon-btn` "Remove Aisyah", enabled, X icon 20 px ink muted, `--line` left divider, 44 x 44 |
| S1-06 | Person 2 field | value "Ben", aria-label "Person 2 name" |
| S1-07 | Person 2 remove | "Remove Ben", enabled, X icon |
| S1-08 | Person 3 field | value "Chen", aria-label "Person 3 name" |
| S1-09 | Person 3 remove | "Remove Chen", enabled, X icon |
| S1-10 | Add person | `.btn.btn-outline` in the next cell, full cell width, plus icon 18 px ink muted, "Add person", enabled |
| S1-11 | People grid | `ul.cells`, 2 columns at 390, 3 at 1280, 8 px gaps |
| S1-12 | Mode switch | `fieldset.mode`, hidden legend "Split mode", two equal 44 px halves, line-strong outline and divider |
| S1-13 | Even label | unchecked, field fill, ink text |
| S1-14 | By item label | checked, ink fill, on-ink text |
| S1-15 | Items heading | `h2.block-title#h-items` "Items" |
| S1-16 | Item 1 name | value "Nasi lemak ayam", aria-label "Item 1 name", maxlength 40 |
| S1-17 | Item 1 price | `span.field.money` with "RM" unit (ink muted, aria-hidden), value "15.90" right aligned, aria-label "Item 1 price in RM", 96 px wide at 390 and 120 px at 1280 |
| S1-18 | Item 1 remove | "Remove Nasi lemak ayam", X icon |
| S1-19 | Item 1 toggles | group "Who had Nasi lemak ayam". Aisyah pressed (ink fill), Ben and Chen not pressed (field fill) |
| S1-20 | Item 2 name | "Char kuey teow", "Item 2 name" |
| S1-21 | Item 2 price | "13.50", "Item 2 price in RM" |
| S1-22 | Item 2 remove | "Remove Char kuey teow" |
| S1-23 | Item 2 toggles | "Who had Char kuey teow", Ben pressed only |
| S1-24 | Item 3 name | "Mee goreng mamak", "Item 3 name" |
| S1-25 | Item 3 price | "12.00", "Item 3 price in RM" |
| S1-26 | Item 3 remove | "Remove Mee goreng mamak" |
| S1-27 | Item 3 toggles | "Who had Mee goreng mamak", Chen pressed only |
| S1-28 | Item 4 name | "Satay, 10 sticks", "Item 4 name" |
| S1-29 | Item 4 price | "18.00", "Item 4 price in RM" |
| S1-30 | Item 4 remove | "Remove Satay, 10 sticks" |
| S1-31 | Item 4 toggles | "Who had Satay, 10 sticks", Aisyah and Chen pressed, Ben not |
| S1-32 | Item separators | 1 px `--line` above items 2 to 4, none above item 1, 16 px item padding |
| S1-33 | Add item | outline button, plus icon, "Add item", natural width, left aligned after the list |
| S1-34 | Charges heading | `h2.block-title#h-charges` "Charges" |
| S1-35 | Service label | `label.label` "Service charge" + hidden " in percent", 15/20 600 |
| S1-36 | Service input | value "10" right aligned, "%" unit after it, aria-describedby "charges-hint" |
| S1-37 | SST label | "SST" + hidden " in percent" |
| S1-38 | SST input | value "6", "%" unit, aria-describedby "charges-hint" |
| S1-39 | Hint | `p.hint#charges-hint` "Set a charge to 0 if your bill already includes it.", 14/20 ink muted |
| S1-40 | Panel frame | `div.tape`. At 390 full bleed, 2 px ink top rule, 1 px line bottom. At 1280 420 px wide, 1 px ink border, 6 px radius, sticky, top level with the People block |
| S1-41 | Summary heading | `h2.tape-title#h-summary` "Bill summary" |
| S1-42 | Subtotal row | empty operator, "Subtotal", "RM 59.40" |
| S1-43 | Service row | "+", "Service charge", "RM 5.94", working "10% of RM 59.40" (15/20 ink muted) |
| S1-44 | SST row | "+", "SST", "RM 3.92", working "6% of RM 65.34" |
| S1-45 | Total row | "=", "Total" 18 px 700, "RM 69.26" 26/32 700 on the 3 px double rule, 1 px ink rule above from 28 px |
| S1-46 | Shares heading | `h2.tape-title#h-shares` "Shares", 32 px under the Total |
| S1-47 | Table heads | hidden "Person", "Items", "+ Charges", "= Share", 13/18 600 ink muted, right aligned |
| S1-48 | Row Aisyah | name 15 px 600 ink. "RM 24.90", "RM 4.14" (14 px ink muted). "RM 29.04" 18 px 700 ink |
| S1-49 | Row Ben | "RM 13.50", "RM 2.24", "RM 15.74" |
| S1-50 | Row Chen | "RM 21.00", "RM 3.48", "RM 24.48" |
| S1-51 | Check row | check icon 18 px accent in the gutter, "Adds up to" accent, "RM 59.40", "RM 9.86", "RM 69.26" accent 18 px 700, 1 px ink rule above |
| S1-52 | Copy summary | `.btn.btn-primary.btn-large.btn-block.copy`, ink fill, copy icon 20 px, "Copy summary", full width, 48 px, 24 px under the table |
| S1-53 | Status | `p.status[role=status]` present, empty, not displayed |

### S2 `docs/design/bill-even.html`
| Id | Element | Expected |
|---|---|---|
| S2-01 | Wordmark | as S1-01 |
| S2-02 | New bill | as S1-02 |
| S2-03 | People heading | as S1-03 |
| S2-04 | Person rows 1 to 3 (fields and removes) | as S1-04 to S1-09 |
| S2-05 | Add person | as S1-10 |
| S2-06 | People grid | as S1-11 |
| S2-07 | Mode switch | as S1-12 |
| S2-08 | Even label | checked, ink fill, on-ink text |
| S2-09 | By item label | unchecked, field fill |
| S2-10 | Subtotal heading | `h2.block-title#h-subtotal` holding `label[for=subtotal]` "Subtotal" + hidden " in RM" |
| S2-11 | Subtotal field | `span.field.money` in one grid cell (175 px at 390, 180 px at 1280), "RM" unit, `input#subtotal` value "100.00", no aria-invalid, no error paragraph |
| S2-12 | Items block | not rendered |
| S2-13 | Charges block (heading, two labels, two inputs, hint) | as S1-34 to S1-39 |
| S2-14 | Panel frame | as S1-40 |
| S2-15 | Summary heading | as S1-41 |
| S2-16 | Subtotal row | "RM 100.00" |
| S2-17 | Service row | "RM 10.00", "10% of RM 100.00" |
| S2-18 | SST row | "RM 6.60", "6% of RM 110.00" |
| S2-19 | Total row | "RM 116.60" on the double rule |
| S2-20 | Shares heading | as S1-46 |
| S2-21 | Table heads | `thead.sr-only` with "Person" and "Share" |
| S2-22 | Row Aisyah | `th` "Aisyah", `td.share` "RM 38.87", no Items or Charges cell |
| S2-23 | Row Ben | "RM 38.87" |
| S2-24 | Row Chen | "RM 38.86" |
| S2-25 | Check row | check icon, "Adds up to", "RM 116.60" in accent |
| S2-26 | Copy summary | as S1-52 |
| S2-27 | Status | as S1-53 |
| S2-28 | Subtotal field at 360 x 780 (added 2026-10-08) | `span.field.money` is 160 px wide, one grid cell (`bill-even.md`) |

### S3 `docs/design/bill-empty.html`
| Id | Element | Expected |
|---|---|---|
| S3-01 | Wordmark, New bill, People heading | as S1-01 to S1-03 |
| S3-02 | Person 1 field | value "Person 1", aria-label "Person 1 name", placeholder "Person 1" |
| S3-03 | Person 1 remove | "Remove Person 1", `disabled`, X in `--ink-disabled`, borders kept, `not-allowed` cursor, skipped by Tab |
| S3-04 | Person 2 field | value "Person 2", aria-label "Person 2 name" |
| S3-05 | Person 2 remove | "Remove Person 2", disabled as S3-03 |
| S3-06 | Add person | enabled, third grid cell (second row at 390) |
| S3-07 | Mode switch | Even checked, By item unchecked |
| S3-08 | Subtotal heading and field | as S2-10 and S2-11 but empty, "RM" unit visible, no error |
| S3-09 | Charges block | as S1-34 to S1-39 |
| S3-10 | Panel frame | as S1-40 (short card at 1280) |
| S3-11 | Bill summary | not rendered |
| S3-12 | Shares heading | as S1-46 |
| S3-13 | Result message | `p.result-msg` "Enter the subtotal to see the shares.", 16/24 ink, 8 px under the heading, no indent |
| S3-14 | Table, Copy summary, status | not rendered |

### S5 `docs/design/bill-unassigned.html`
| Id | Element | Expected |
|---|---|---|
| S5-01 | Header, People, mode switch | as S1-01 to S1-14 |
| S5-02 | Items 1, 2 and 4 | as S1-16 to S1-23 and S1-28 to S1-31 |
| S5-03 | Item 3 fields and remove | as S1-24 to S1-26 |
| S5-04 | Item 3 toggles | "Who had Mee goreng mamak", Aisyah, Ben and Chen all not pressed, no error styling |
| S5-05 | Add item, Charges block | as S1-33 to S1-39 |
| S5-06 | Bill summary | as S1-41 to S1-45 |
| S5-07 | Shares heading | as S1-46 |
| S5-08 | Result message | "1 item still needs a person. Tap who had it to see the shares.", styled as S3-13, two lines at 390 and at 1280 |
| S5-09 | Table, Copy summary, status | not rendered |
| S5-10 | Items heading (added 2026-10-08) | as S1-15 |
| S5-11 | Item separators (added 2026-10-08) | as S1-32 |
| S5-12 | Panel frame (added 2026-10-08) | as S1-40, with the 1280 card ending 24 px under the result message (`div.tape` padding-bottom 24 px and `p.result-msg` the last thing in it, `bill-unassigned.md`). At 390 it is full bleed, as in S1-40 |

### M1 `docs/design/new-bill-dialog.html`
| Id | Element | Expected |
|---|---|---|
| M1-01 | Page behind | the S2 render, under the scrim, `.app` clipped to the viewport height, not scrollable |
| M1-02 | Scrim | whole viewport, `rgba(20, 25, 23, 0.48)` |
| M1-03 | Dialog box | centred both ways, 358 px wide at 390 and 400 px at 1280, 24 px padding, surface fill, 1 px ink border, 6 px radius, no shadow |
| M1-04 | Title | `h2.dialog-title#dialog-title` "Start a new bill?", 18/24 700, names the dialog |
| M1-05 | Body | `p.dialog-text#dialog-text` "This clears the people, items and amounts.", 16/24 ink muted, 8 px under the title, describes the dialog |
| M1-06 | Start new bill | `.btn.btn-primary.btn-large`, first. Full width at 390, natural width in a right-aligned row at 1280 |
| M1-07 | Cancel | `.btn.btn-outline.btn-large`, second, focused on open with no visible ring after a mouse open |
| M1-08 | Actions | 8 px apart, 24 px under the body |
| M1-09 | Dialog at 360 x 780 (added 2026-10-08) | 328 px wide (`min(400px, 100% - 32px)`), centred, `p.dialog-text` on two lines (48 px tall), no horizontal overflow (`new-bill-dialog.md`) |

### States from `docs/design/states.html` (checked on the app at 390 x 844 unless the row names another size, no pixel diff)
"Equal" in these rows means the specimen properties defined in the phrases above, never width (Changed 2026-10-08).

| Id | State | Expected on the app |
|---|---|---|
| ST-01 | S4 subtotal error | "0" typed and left. Input aria-invalid "true", aria-describedby "subtotal-error". `p.error#subtotal-error` "Enter an amount like 12.50" right after `div.cells`. The specimen properties and `margin-top` of the paragraph equal those of `#s4-subtotal-error`, and the specimen properties of `span.field.money` (the red border colour and the 2 px inset `box-shadow` among them) equal those of its field in the specimen |
| ST-02 | S4 price error | "13.505" left in Item 2's price. `p.error` last in `div.item-line`, and its specimen properties, `text-align` (right) and `margin-top` (0) equal those of `#s4-price-error`. The price field shows the error look too: the specimen properties of its `span.field.money`, the red border colour and the 2 px inset `box-shadow` among them, equal those of the `span.field.money` around `input[aria-label="Item 1 price in RM"][aria-invalid="true"]` in the S4 frame of the specimen (added 2026-10-08). Toggles keep their 8 px gap |
| ST-03 | S4 error with focus | the error field keeps its red border and gains the ink ring |
| ST-04 | S6 copy success | `p.status` "Summary copied", ink, centred, 14/20 600, 8 px under Copy summary (`margin-top` 8 px), and its specimen properties and `text-align` (center) equal those of the S6 success specimen |
| ST-05 | S6 copy failure | `p.status.status-failure` "Could not copy. Your browser blocked the clipboard.", error red, and its specimen properties and `text-align` (center) equal those of the S6 failure specimen |
| ST-06 | S7 note | `div.note-wrap > div.note[role=status]` between the header and People, the text, and `.icon-btn` "Dismiss note" with the X icon. The specimen properties of `div.note` equal those of `.note` in the specimen |
| ST-07 | S7 screen under the note | S3 (Person 1 and Person 2, remove disabled) |
| ST-08 | S8 12 people | S8 seed. Add person disabled, transparent fill, `--line` border, `--ink-disabled` text and plus icon, and its specimen properties and `cursor` (not-allowed) equal those of the "S8 12 people" button in the specimen (not its width, the app cell is 175 px and the specimen cell 158 px). Six rows of two at 390, Add person in the next cell |
| ST-09 | S8 2 people | both removes disabled, X in `--ink-disabled`, borders kept, and the specimen properties and `cursor` of each remove button equal those of the "S8 2 people" remove buttons in the specimen |
| ST-10 | Rate errors (ruling 2, not drawn) | "Enter a rate from 0 to 30" and "Enter a rate from 0 to 20" in `p.error` under their field, styled by the `.error` rule exactly as ST-01 |
| ST-11 | Other panel messages (ruling 3, not drawn) | "Check the charges to see the shares.", "Add an item to see the shares.", "Give every item a price to see the shares." styled as S3-13 |
| ST-12 | Plural S5 message (not drawn) | "2 items still need a person. Tap who had each one to see the shares." styled as S5-08 |
| ST-13 | Add item at 50 (not drawn) | disabled, with the specimen properties and `cursor` of ST-08 (not its width, "Add item" has its natural width) |
| ST-14 | S6 copy failure at 360 x 780 (added 2026-10-08) | the failure text wraps onto two centred lines (`p.status` 40 px tall, `text-align` center) with no horizontal overflow, as `states.md` says |
| ST-15 | S7 note at 1280 x 800 (added 2026-10-08) | `div.note` is 1040 px wide, the content width of `.note-wrap` (the 1104 px page maximum less two 32 px gutters), and the content of `header.bar` is 1040 px as well |

## Fidelity gate
- **Harness.** The sdlc plugin harness `{sdlc}/harness/fidelity.py` (that is `${CLAUDE_PLUGIN_ROOT}/harness/fidelity.py`, sdlc 2.1.2), frozen mode, used unmodified. ~~Run it with the harness Python described in its `README.md` (a venv in `%USERPROFILE%\.sdlc-harness\.venv`).~~ **Changed 2026-10-08 (CG-11, plan check FLAG).** `run.py` runs it with `sys.executable`, the same Python that runs pytest, and the README venv is optional here. At planning time that venv did not exist, and this Python had the harness requirements (Playwright 1.61.0, Pillow 12.3.0, numpy 2.4.6) and ran the harness. The runner creates no venv and installs no package. The harness renders each side in its own headless Chromium with reduced motion, `--force-color-profile=srgb` and `--hide-scrollbars`, pins `Math.random`, pins time through Playwright's clock (its default 2023-11-14T22:13:20Z, or `--fixed-time`, so nothing in a render may rely on a live `Date.now`), injects its freeze stylesheet, and writes `golden.png`, `candidate.png`, `diff.png`, `styles.json` and `report.json`.
- **The harness bypasses the app's Content Security Policy.** Since 2.1.2 it renders with Playwright `bypass_csp`, so its freeze stylesheet applies under the strict policy of R38. The policy is therefore off inside every fidelity render, and a fidelity pass says nothing about it. Policy breakage is caught by the functional suite (the R38 scenarios and the console rule above) and by the live gate, which never bypass it.
- **Runner.** `python tests/browser/fidelity/run.py` from the project root. It only manages the server with the lifecycle rules above (free port, `python -m http.server <port> --bind 127.0.0.1`, bounded readiness wait, kill by PID in `finally`, port re-check, PID and port printed) and calls the harness (as `[sys.executable, <path to fidelity.py>, ...]`, CG-11, added 2026-10-08) once per row and width below, each into its own evidence folder. It adds no rendering or diff logic of its own.
- **Golden.** `./docs/design/<screen>.html`, opened by the harness as a file (read-only, never written).
- **Candidate.** `http://127.0.0.1:<port>/`, brought into the golden's state by the test-side setup scripts below. Never through a hook in the app.
- **Setup scripts.** Test-side only, in `tests/browser/fidelity/`, never loaded by `index.html`.

  | File | Harness flag | What it does |
  |---|---|---|
  | `seed-s1.js`, `seed-s2.js`, `seed-s5.js` | `--candidate-init-script` | One statement, `localStorage.setItem("split.draft", '<seed JSON>')`, with the S1, S2 or S5 seed from `seeds.py`. It runs before the app's own scripts, so the app boots into that bill through its real load path. `test_R40_fidelity_seeds_match` asserts that each file holds exactly the JSON of its seed in `seeds.py`. |
  | `open-new-bill.js` | `--candidate-after-load` | Clicks the header button "New bill" (`document.querySelector("header .btn").click()`), waits two animation frames, calls `document.activeElement.blur()`, and waits two more frames. |

  Why the blur. The harness's click is synthetic, so Chromium treats the focus the app then moves to Cancel as keyboard focus and draws the focus ring, which a real mouse click does not (both measured during planning, the ring alone made 0.48% of the 390 render differ). The golden shows no ring, so the setup removes focus once the dialog is open. Focus on Cancel itself is checked with real gestures by R29.

  | Golden | Candidate state | Init script | After-load script |
  |---|---|---|---|
  | `bill-empty.html` | S3, a cold boot | none (each harness render is a fresh browser, so storage is empty) | none |
  | `bill-even.html` | S2 | `seed-s2.js` | none |
  | `bill-items.html` | S1 | `seed-s1.js` | none |
  | `bill-unassigned.html` | S5 | `seed-s5.js` | none |
  | `new-bill-dialog.html` | M1 over S2 | `seed-s2.js` | `open-new-bill.js` |
- **Command.** For each row, once at `390x844` and once at `1280x800` (10 runs). The `python` in the block below stands for `sys.executable` (CG-11, 2026-10-08).

  ```bash
  python {sdlc}/harness/fidelity.py \
    --golden ./docs/design/<screen>.html \
    --candidate http://127.0.0.1:<port>/ \
    --viewport <390x844|1280x800> --dpr 1 --color-scheme light \
    --browser-arg=--disable-lcd-text \
    --fixed-time 2026-10-08T09:00:00 \
    --threshold 0.01 \
    [--candidate-init-script ./tests/browser/fidelity/<seed>.js] \
    [--candidate-after-load ./tests/browser/fidelity/open-new-bill.js] \
    --out ./docs/modules/split-app/qa/fidelity-<screen>-<viewport>/<YYYYMMDD-HHMMSS>/
  ```
- **Flags and why.**
  - `--color-scheme light` (the harness default is dark) and `--dpr 1`. Full page (the harness default).
  - `--browser-arg=--disable-lcd-text`. In a native modal the dialog sits in the top layer and its text gets greyscale anti-aliasing, while the golden's in-flow dialog gets LCD (coloured) anti-aliasing. Measured during planning, 2591 pixels differed at 390 and 3271 at 1280 without the flag. It applies to both renders, so it hides no real difference.
  - `--fixed-time 2026-10-08T09:00:00`. The app reads no clock, so this changes nothing on screen. It keeps re-runs byte-stable.
- **Threshold.** `--threshold 0.01`. The harness divides each pixel's RGB distance by its maximum (441.67) and counts the pixel as a mismatch above this value. A pair passes only when `report.json` has `"dimensions_match": true` and `"mismatch_pixels": 0`. Justification, measured during planning with this harness (on 2.1.0 and again on 2.1.1, with the same counts, and 2.1.2 adds only the CSP bypass, which the scratch candidate did not need because its policy then allowed inline styles), these flags and a scratch candidate built like the app (CSP meta, linked `system.css`, module script, `showModal()` dialog). `bill-items` matched with 0 differing pixels even at threshold 0, at both widths. `new-bill-dialog` had 141 pixels (390) and 103 pixels (1280) that moved at all, the largest by 0.0068, all anti-aliasing at glyph edges, and 0 above 0.01. Any defect a person can see (a 1 px shift, a wrong colour or weight, a missing icon, a wrong letter) moves pixels far beyond 0.01, and a single level in a single channel is already 0.0023. A non-zero count is a finding for the human. It is never handled by raising the threshold.
- **Per-element check.** The fidelity tester compares the two sides of the harness's `styles.json` (path with tag, id and classes, text, rect and computed styles of every rendered element) against the FE element checklist. Attributes the harness does not dump (ARIA, `disabled`, `checked`, `maxlength`, `inputmode`, `placeholder`) are checked by the R3 DOM walk in the functional suite. Only the allowed differences in `spec.md` may appear.
- **Evidence.** ~~`docs/modules/split-app/qa/fidelity-<screen>-<viewport>/<YYYYMMDD-HHMMSS>/` for each of the 10 runs, holding the harness outputs.~~ **Changed 2026-10-09 (Task 12, the orchestrator's instruction named `qa/fidelity/<ts>/`).** One run of the gate writes one folder, `docs/modules/split-app/qa/fidelity/<YYYYMMDD-HHMMSS>/`, with one subfolder per pair, `<screen>-<viewport>/` (for example `bill-items-390x844/`), each holding the harness outputs, so the ten pairs of one run sit together. The `--out` in the command above is that subfolder. The runner adds `run.log` to the run folder (the commands, the server PID and port, the harness stdout and a PASS or FAIL line per pair with the mismatching pixel count). The verdict goes to `docs/modules/split-app/findings/fidelity.md`.
- **Verdict.** 1 to 1, with no additions, subtractions or modifications. The fidelity finder judges `diff.png`, `styles.json` and `report.json` per screen and width (10 pairs).

## Cold-boot live-e2e gate
- **Script.** `tests/browser/live_e2e.py`. It runs after the functional suite and the fidelity gate are green.
- **Rules.** A fresh headless Chromium and a new context with **no** `storage_state` and **no** `bypass_csp`, so the shipped strict policy is live for the whole run. Its only init script is `tests/browser/clipboard/recorder.js` (CG-7, ruled 2026-10-08, ORCH). The gate never touches the operating system clipboard, and the recorder is test-side platform control in the same category as `page.clock`, not a hook in the app. The app's real call to `navigator.clipboard.writeText` is what the recorder receives. No clipboard permission is granted. Viewport 390 x 844. The entry point is the shipped `index.html` at `/`. Only real gestures change the app (mouse clicks on visible controls, keyboard typing, key presses). `page.evaluate` is used only to **read** (`window.testClipboardText`, `document.activeElement`, `localStorage` for a final check), never to change state. No seed, fixture, app hook or test-only code path in the app.
- **Flow.** Each numbered step takes a screenshot and appends a line to `steps.log` (step, gesture, assertion, PASS or FAIL).
  1. Open `/`. Assert the S3 screen (R2) and that `split.draft` is absent.
  2. Key flow 1, even split. Replace Person 1 with "Aisyah" and Person 2 with "Ben", click Add person, type "Chen", type "100.00" in Subtotal. Assert the S2 Bill summary and shares (RM 38.87, RM 38.87, RM 38.86, Adds up to RM 116.60).
  3. Click Copy summary. Assert "Summary copied" and that `window.testClipboardText` equals the S2 block exactly.
  4. Key flow 2, by item. Click By item, add the four S1 items by typing their names and prices, tap their people. Assert the S1 table and check row, click Copy summary and assert that `window.testClipboardText` equals the S1 block exactly.
  5. Key flow 3, come back later. Close the page, open `/` in a new page of the same context. Assert the S1 screen as left, then click Even and assert Subtotal "100.00" and the S2 shares.
  6. Key flow 4, start over. Click New bill, assert the dialog and Cancel focused, click Start new bill. Assert the S3 screen. Reload and assert S3 again.
  7. Throughout, assert zero console errors, zero page errors and only same-origin GETs. Chromium logs every CSP violation as a console error, so a policy that blocks anything the app needs (its stylesheet, a module, an inline style it set) fails the gate here. `console.log` in the evidence must hold no line containing "Content Security Policy".
- **Evidence artifact.** `docs/modules/split-app/qa/live-e2e/<YYYYMMDD-HHMMSS>/` with `01-*.png` onwards (one per step), `steps.log`, `console.log`, `network.log`, `clipboard-s2.txt` and `clipboard-s1.txt` (the text the recorder captured) and `summary.json` (start and end time, Chromium version, port, server PID, the init scripts used, result). After the run, list the folder to prove the files landed there. **No artifact means not done.**

## Regression
- Re-run the functional suite, the fidelity gate and the live gate in the final all-modules pass, together with `split-core`'s `node --test "tests/**/*.test.js"`.
