---
question: Can each app's existing browser suites and gates also run headless in Playwright WebKit on this Windows machine, and what must the plan specify to make that real?
verdict: feasible-with-caveats
---
# WebKit for the browser suites and gates (v1.1.0 scope S5, Split and Streaks)

sdlc researcher, plan phase. Written 2026-10-13. The same file sits in both projects.

**Recommendation:** Run both functional pytest suites and both cold-boot live gates a second time in headless WebKit, chosen by one `--engine` option. Keep the fidelity pixel gate in Chromium only.
**How:** `python -m playwright install webkit` (Playwright 1.61.0, WebKit 26.5, build 2311). Then `getattr(playwright, engine).launch(headless=True, args=...)` behind a pytest option and a live gate flag, with launch arguments per engine and a `chromium_only` marker for the one CDP test.
**Pitfalls:** A button does not take focus on a mouse click in WebKit. Chromium launch switches must not reach WebKit. `is_mobile` breaks `mouse.wheel`. The click `detail` of a double tap is unproven. Console message texts differ between engines.
**Feasibility:** FEASIBLE WITH CAVEATS, see Verdict.
**Sources:** at the end.

## Question

Can each app's existing browser suites and gates also run headless in Playwright WebKit on this Windows machine, and what must the plan specify to make that real? Scope S5 in both v1.1.0 change ledgers says "The browser tests and the gates also run in WebKit, the engine of Safari on iPhone".

## Verdict

**FEASIBLE WITH CAVEATS.**

Playwright 1.61.0 has a WebKit 26.5 build for Windows and drives it headless with every Playwright API the two suites use. Nothing in either app or either suite rules it out. Four caveats remain.

1. **WebKit is not installed.** The install downloads about 62 MB and is the owner's call.
2. **Some tests need a WebKit expectation or a Chromium-only skip.** Two are certain today and about a dozen are probable. The full list only comes from a first WebKit run, which this research did not do (nothing installed, no browser started).
3. **The fidelity gate has no meaningful WebKit form.** It is a 0-pixel compare against goldens rendered in Chromium, run by the sdlc plugin harness, which is Chromium only and sits outside both projects.
4. **WebKit on Windows is Safari's engine, not Safari on an iPhone.** Touch gestures, the on-screen keyboard, iPhone fonts and Safari's 7-day storage expiry stay unproven without a real phone.

## Evidence

### 1. Install

- **Command.** `python -m playwright install webkit`, run with the Python that runs pytest (Playwright 1.61.0 per `python -m playwright --version`, package in `{home}\AppData\Roaming\Python\Python314\site-packages\playwright`).
- **Dry run.** `--dry-run` exists in 1.61 (`python -m playwright install --help`). `python -m playwright install --dry-run webkit` printed the block below on 2026-10-13 and downloaded nothing.

```
WebKit 26.5 (playwright webkit v2311)
  Install location:    {home}\AppData\Local\ms-playwright\webkit-2311
  Download url:        https://cdn.playwright.dev/dbazure/download/playwright/builds/webkit/2311/webkit-win64.zip
  Download fallback 1: https://playwright.download.prss.microsoft.com/dbazure/download/playwright/builds/webkit/2311/webkit-win64.zip
  Download fallback 2: https://cdn.playwright.dev/builds/webkit/2311/webkit-win64.zip
FFmpeg (playwright ffmpeg v1011)   {home}\AppData\Local\ms-playwright\ffmpeg-1011
Winldd (playwright winldd v1007)   {home}\AppData\Local\ms-playwright\winldd-1007
```

- **What is new on disk.** `ffmpeg-1011` and `winldd-1007` already exist in `{home}/AppData/Local/ms-playwright/`, next to `chromium-1228` and `chromium_headless_shell-1228`. Only `webkit-2311` is missing. `install --help` offers `--force` to reinstall, so revisions already present are skipped.
- **Size.** A header-only request to the download URL (no body fetched) returned `Content-Length: 61623802`, about 62 MB, and `Last-Modified: Wed, 10 Jun 2026`. The unpacked size on Windows is UNVERIFIED. Playwright's browsers page shows about 180 MB for a WebKit folder (its macOS example). Drive C has 99 GB free.
- **From where.** Playwright's CDN `cdn.playwright.dev`, which answered with a 307 redirect to `playwright.download.prss.microsoft.com`, a Microsoft download host.
- **Prerequisites.** On Windows Playwright checks the browser's DLL imports with winldd. It asks for the Visual C++ runtime when `vcruntime140.dll`, `vcruntime140_1.dll` or `msvcp140.dll` is missing, and for Media Foundation when `mf.dll` or `mfplat.dll` is missing (driver `coreBundle.js`). All five are present in `C:\Windows\System32`. `--with-deps` is not needed. On Windows it only runs `install_media_pack.ps1`, and only for Chromium (driver `installDependenciesWindows`).
- **What runs.** `webkit-2311\Playwright.exe` (driver executable table, `"win-x64": ["Playwright.exe"]`). Playwright passes `--headless` for a headless launch and on Windows always adds `--disable-accelerated-compositing` (driver `defaultArgs` for WebKit). Headless keeps the constitution rule "Headless by default".
- **Rejected option.** The driver also has a `webkit-wsl` channel. Its installer `bin/install_webkit_wsl.ps1` creates a WSL distribution named "playwright" (Ubuntu 24.04, 10 GB virtual disk), downloads Node 22.17.0 into it and installs Linux WebKit there. It is much heavier, a web search found no public Playwright docs for it, and Linux WebKit focuses a button on click, which Safari does not (see the focus row below). Not recommended.

### 2. Parity

What the suites and the apps rely on, read from `tests/browser/`, `src/` and `index.html` of both projects. Neither project's `harness/` holds a gate, both hold only `_scratch/`. The gates are `tests/browser/live_e2e.py` (both) and `tests/browser/fidelity/run.py` (Split). Streaks runs the plugin fidelity harness directly (Streaks `docs/modules/app/qa.md`, Fidelity gate).

| Feature | Where it is used | Playwright WebKit on Windows | Evidence |
|---|---|---|---|
| `page.clock`, `context.clock` (`install`, `set_fixed_time`, `pause_at`, `run_for`, `set_system_time`) | Streaks `conftest.py` (`open_app`, `let_guard_pass`), `test_delete.py`, `test_rollover.py` | Works the same as in Chromium | The clock is a page script that Playwright adds with `addInitScript` (driver `clockSource.ts`, `globalThis.__pwClock`). It redefines `Event.prototype.timeStamp` from the fake `performance`. The clock docs list `Event.timeStamp` among the overridden globals and name no browser limit. Streaks' guard window reads `event.timeStamp` (`src/app.js`), so it follows the clock in both engines |
| Key auto-repeat and `event.repeat` | Split S3 fix (a capture `keydown` listener that cancels `event.repeat`, SEC-04 in `docs/modules/split-app/findings/security.md`), probed with repeated `keyboard.down("Enter")` | Works | The WebKit keyboard backend sends `autoRepeat` on the second `keyboard.down` of a held key (driver `wkInput.ts`). Playwright's test "should specify repeat property" in `page-keyboard.spec.ts` has no skip, and Playwright's "Windows" CI job runs WebKit. WebKit clicks a button on the Enter keypress (`HTMLButtonElement.cpp`), so cancelling the repeated keydown stops that click as it does in Chromium |
| `<dialog>`, `showModal()`, `:modal`, `close`, `returnValue`, `form method="dialog"` | Split `src/ui/dialog.js`, Streaks `src/view.js` and `src/app.js`, both `index.html` | Works | Both specs set Safari 15.4 as the floor for native dialogs (Split `spec.md` line 19, Streaks `spec.md` line 30). WebKit 26.5 is far past it. Streaks relies on the dialog focusing steps to put focus on Cancel. Split calls `cancel.focus()` itself |
| Focus after a mouse click on a `<button>` | Streaks `test_add.py`, the R10 test | DIFFERS from Chromium and MATCHES Safari | `HTMLFormControlElement::isMouseFocusable()` returns false for form controls on every WebKit port except GTK and WPE, unless `tabindex` is set. The mouse-down code in `EventHandler.cpp` walks up for a mouse-focusable element and, finding none, sets focus to no element. Neither app sets `tabindex` on a button today (grep of `index.html` and `src/`). So after a click on a button `document.activeElement` is `body` in WebKit. Both apps already restore focus by hand after their dialog for this reason (Split `src/ui/dialog.js` comment, Streaks `src/app.js` `onDialogClose` comment) |
| Tab reaching buttons | Streaks `tab_until`, `test_R22_tab_order`, Split dialog Tab tests | Works like Chromium | `EventHandler::tabsToAllFormControls` returns true outside Cocoa platforms ("We always allow tabs to all controls"). Safari on a Mac or iPad follows its keyboard setting instead, so this is easier on Windows than on Apple hardware |
| `localStorage` and seeding | Split `rig.storage_state` (Playwright `storage_state`), Streaks `open_app` (a `/__seed__` page), the throwing-storage init scripts of both | Works | Playwright API and plain page JavaScript. The scripts redefine `window.localStorage` and `Storage.prototype.setItem` |
| Init scripts | Split `rig.new_context` (a clipboard script in every context), the fidelity seed scripts, Streaks `init_script` and the write counter | Works | `add_init_script` runs "after the document was created but before any of its scripts were run" (BrowserContext API) |
| Clipboard stand-in | Split `tests/browser/clipboard/recorder.js`, `reject.js`, `missing.js`, live gate step 1 | Works. Secure context on `http://127.0.0.1` in WebKit is UNVERIFIED | WebKit turns the Async Clipboard API on for `PLATFORM(WIN)` (`UnifiedWebPreferences.yaml`, `AsyncClipboardAPIEnabled`), so `Clipboard.prototype.writeText` exists for the recorder to replace. The constitution rule "Never touch the system clipboard" holds because the rig puts a stand-in in every context and grants no permission. If `Clipboard` were absent, the app could not reach the OS clipboard either, and the recorder tests would fail loudly |
| Touch (`has_touch`, `touchscreen.tap`) | Split `open_app(touch=True)`, Streaks `open_app(touch=True)`, `press_twice` | Works. The click `detail` of two quick taps is UNVERIFIED | The driver turns touch on with `Page.setTouchEmulationEnabled` and taps with `Input.dispatchTapEvent`. Playwright's `tap.spec.ts` (with `hasTouch`) has no WebKit or Windows skip |
| `is_mobile` | Not used | Leave it unset | With `is_mobile` the driver throws "Mouse wheel is not supported in mobile WebKit". Split `test_R29_the_dialog_opens_with_the_safe_choice_focused` and Streaks `test_R13_the_confirmation_opens_as_a_modal_with_focus_on_cancel` call `mouse.wheel` |
| Viewport, `device_scale_factor`, `color_scheme`, `reduced_motion`, `timezone_id`, `locale` | both `conftest.py` | Works | Playwright's emulate-media and timezone test files have no WebKit skip. Neither app formats with locale data (grep of `src/`, only `Intl.Segmenter` in Split `src/draft.js`) |
| CDP session | Split `test_R33_ime_composition_survives_a_render` | NOT available | "CDP sessions are only supported on Chromium-based browsers" (BrowserContext API) |
| Chromium launch switches | Streaks `conftest.py` `browser` and `live_e2e.py` pass `--force-color-profile=srgb`. Split fidelity passes `--browser-arg=--disable-lcd-text` to the harness | Must not reach WebKit | They are Chromium switches |
| Console and CSP checks | Split `Session.problems` (any console error, any "Content Security Policy" text), Streaks `test_R25_the_csp_is_in_force` (looks for "connect-src") | Works. Message wording UNVERIFIED | WebKit words its console messages differently from Chromium. Streaks sets `connect-src 'none'` explicitly in `index.html`, so the directive name should still appear |
| Locator stability wait | every locator action | Slower | On Windows the driver waits 5 animation frames for a stable position, 1 elsewhere (`rafCountForStablePosition`). The Chromium runs took 109.87 s for 427 Split tests and 42.32 s for 179 Streaks tests (each `docs/regression/REGRESSION.md`). The WebKit time is UNVERIFIED |

CSS in the v1.1.0 `docs/design/system.css` of both projects (the build copies it).

| CSS | Where | WebKit | Effect |
|---|---|---|---|
| `backdrop-filter` | Split line 180, with `-webkit-backdrop-filter` beside it and an `@supports` fallback at line 508 | Parsed. Probably not painted in Playwright WebKit on Windows, because the launcher disables accelerated compositing and WebKit draws backdrop filters through a compositing layer (WebKit bug 271340). UNVERIFIED | Visual only. One more reason not to pixel-compare in WebKit |
| `:has()`, `dvh`, `inset`, `overflow-x: clip`, `text-wrap: balance`, `env(safe-area-inset-bottom)` | both | Supported by WebKit 26.5 | `env()` is 0 in a desktop window |
| `scrollbar-width`, `scrollbar-color`, `::-webkit-scrollbar` | both | `scrollbar-width` from Safari 18.2. `scrollbar-color` later, sources disagree, 26.2 is likely | Cosmetic. iPhone scrollbars are overlays |
| `user-select: none` without a `-webkit-` twin | Split line 319 | Unprefixed support in Safari is UNVERIFIED | Cosmetic. The goldens are immutable, so a change would be a design ruling |
| `-webkit-text-size-adjust`, `-webkit-tap-highlight-color`, `-webkit-font-smoothing` | both | Apple platforms only | No effect on Windows |
| `color-mix`, `aspect-ratio`, `accent-color` | none | Not used | Grep found none |
| System font stacks (`ui-sans-serif, system-ui, ... "Segoe UI"` and `ui-monospace, "Cascadia Mono", ...`) | both | WebKit on Windows draws text with its own rasteriser. Which face `ui-sans-serif` and `system-ui` resolve to there is UNVERIFIED | Any test that measures a wrapped text height can differ by engine |

### 3. How far Playwright's WebKit on Windows stands from Safari on iPhone

What a WebKit run proves.

- The apps' JavaScript runs in JavaScriptCore, and their DOM, events, dialogs, button focus rules, storage use and CSP run in WebCore, the engine of Safari.
- On focus after a click, the Windows port behaves like Safari (the `#else` branch of `isMouseFocusable`). The Linux ports do not.

What it does not prove.

- **Branded Safari.** Playwright's docs say "Playwright doesn't work with the branded version of Safari since it relies on patches" and that its WebKit is derived from the latest WebKit main branch sources. So it is newer than any Safari in use and says nothing about the Safari 15.4 floor in both specs.
- **An iPhone.** The same docs say "for the closest-to-Safari experience you should run WebKit on mac". The Windows port has none of the iOS layer. Not covered are the tap and double-tap gesture recogniser (Playwright synthesises a tap), the on-screen keyboard and the visual viewport it shrinks, Safari's collapsing toolbars that change `dvh`, momentum scrolling, safe areas, `(hover: hover)` (a desktop context reports hover), and San Francisco fonts with their line wraps. Playwright's emulation guide describes device emulation as simulated browser behaviour.
- **Storage expiry.** Safari deletes all script-writable storage, `localStorage` included, after seven days of Safari use without interaction on the site. Web apps added to the Home Screen keep their own counter (webkit.org, "Full Third-Party Cookie Blocking and More"). Playwright does not emulate this. Both apps keep everything in `localStorage`, Streaks a whole habit history.
- **Keyboard on Apple hardware.** Safari on Cocoa follows its keyboard setting for Tab. The Windows port always tabs to every control.

### 4. Which gates should run in WebKit

**Recommendation.** WebKit runs both functional pytest suites and both cold-boot live gates. The fidelity gate stays Chromium only.

**Reasons.**

1. The goldens are Chromium renders, and the 0-pixel budget rests on the same engine. Streaks `qa.md` says "The candidate uses the same CSS, the same DOM and the same system fonts on the same engine, so any pixel over 0.1 is a real difference". Split `qa.md` sets threshold 0.01 and 0 pixels. WebKit's text rasteriser and the likely missing blur would fail every pair for reasons that are not defects.
2. The harness is Chromium only and belongs to the plugin. Split `qa.md` says it "renders each side in its own headless Chromium" with `--force-color-profile=srgb` and `--hide-scrollbars`. A WebKit mode would be a plugin change, outside both projects and the owner's call. Even then a WebKit against WebKit compare would mostly re-prove that the app's DOM equals the golden's, which the Chromium run and Split's R3 DOM walk and Streaks' `canonical_pair` already prove.
3. WebKit pictures still come for free. Each live gate saves a full-page screenshot per step (Split `live_e2e.py` `Gate.step`, Streaks `live_e2e.py` `Gate.step`), so the WebKit live gate leaves a WebKit picture of every step for the owner to look at.

### 5. How the suites should select the engine

One suite, one option, two commands. Today Split launches in `conftest.py` (`browser` fixture) and `live_e2e.py`, Streaks in `conftest.py` (`browser` fixture) and `live_e2e.py`, all with `playwright.chromium`.

- **Pytest option.** `--engine` with the choices `chromium` and `webkit`, default `chromium`, added by `pytest_addoption` in each `tests/browser/conftest.py`. That conftest is loaded as an initial conftest for `python -m pytest tests/browser`, so the hook runs there. The plain command keeps running Chromium as now.
- **Launch in one place.** Split puts it in `rig.py`, already "the one place a browser context is made", so `rig.launch(playwright, engine)` sits beside `rig.new_context`. Streaks puts the same helper in `conftest.py`, which `live_e2e.py` already imports from. Launch arguments are kept per engine, so Streaks' `--force-color-profile=srgb` stays Chromium only.

```python
ENGINES = ("chromium", "webkit")
LAUNCH_ARGS = {"chromium": [], "webkit": []}  # Streaks: {"chromium": ["--force-color-profile=srgb"], "webkit": []}

def launch(playwright, engine):
    if engine not in ENGINES:
        raise ValueError(f"unknown engine {engine!r}")
    return getattr(playwright, engine).launch(headless=True, args=LAUNCH_ARGS[engine])
```

- **Fixtures.** A session `engine` fixture returns the option. The session `browser` fixture calls `launch`. A test that needs an engine-specific expectation asks for `engine`.
- **Chromium-only tests.** A registered marker `chromium_only(reason=...)`. `pytest_collection_modifyitems` turns it into a skip when the engine is not Chromium. Every skip is listed in the run's evidence and counted, never reported as a pass.
- **Live gates.** Each `live_e2e.py` gets `--engine` (Split has no arguments today, Streaks already uses `argparse`). The summary records the engine and `browser.version`. Split's `facts["chromium"]` and Streaks' `"browser": f"Chromium {browser_version}"` become engine-neutral.
- **Evidence.** Folder names carry the engine, for example Split `qa/functional/<stamp>-webkit/` and `qa/live-e2e/<stamp>-webkit/`, and the Streaks caller passes `--out` and `STREAKS_EVIDENCE_DIR` with `-webkit` in the name.
- **Commands.** `python -m pytest tests/browser -q` (Chromium) and `python -m pytest tests/browser -q --engine webkit`. Split `python tests/browser/live_e2e.py --engine webkit`. Streaks `python tests/browser/live_e2e.py --engine webkit --base-url <url> --out <folder>`.
- **Why not a parametrised `browser` fixture.** It would make every default run need WebKit installed, double every run, and mix both engines in one evidence folder. Two commands keep the Chromium run as it is and give WebKit its own record.

### 6. Tests that need a WebKit-specific expectation

Measured against the v1.0 suites on disk today. v1.1.0 rewrites much of both suites for the new look (S7), so the probe in the plan decides the final list.

**Certain.**

| Project | File and test | Why | WebKit handling |
|---|---|---|---|
| Streaks | `tests/browser/test_add.py::test_R10_the_first_habit_on_a_fresh_day` | Asserts that Add has focus after a mouse click ("a click on Add had put it there") | In WebKit a clicked button takes no focus, so focus is on `body`. R10 ("the app does not move focus") still holds. Assert `body` in WebKit |
| Split | `tests/browser/test_app.py::test_R33_ime_composition_survives_a_render` | Uses `page.context.new_cdp_session`, Chromium only | `chromium_only`. Playwright has no cross-engine IME API |

Not tests but code that must change for WebKit. Streaks `tests/browser/conftest.py` `browser` and `tests/browser/live_e2e.py` (the Chromium switch and the hard-coded "Chromium" in `summary.json`). Split `tests/browser/conftest.py` `browser` and `tests/browser/live_e2e.py` (`playwright.chromium.launch`, `facts["chromium"]`).

**Probable, settled by the probe.**

| Project | File and test | Risk |
|---|---|---|
| Split | `test_app.py::test_R40_a_seed_script_boots_the_app_through_its_own_load_path` | Filters the Chromium error text "Failed to read the 'localStorage' property". WebKit words a denied `localStorage` differently, if it raises one at all in the first blank document |
| Split | `test_R30_a_double_click_or_double_tap_on_cancel_changes_nothing`, `test_R30_the_second_click_of_a_double_activation_never_reaches_the_page`, `test_R7_a_double_click_or_double_tap_on_remove_removes_one_row`, `test_R34_after_a_double_click_on_remove_focus_is_where_one_click_puts_it`, `test_R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing`, `test_R6_a_repeat_press_on_add_person_adds_one_person_and_keeps_it`, `test_R12_a_repeat_press_on_add_item_adds_one_item_and_never_reaches_the_page`, `test_R7_a_repeat_press_on_a_chip_under_a_pending_price_error_never_removes_the_item`, `test_R29_a_repeat_press_on_new_bill_leaves_the_dialog_open`, each in its touch variant (`how="touch"` or `gesture="touch-double"`) | Split's guard treats a press as a repeat when `event.detail > 1` (`src/ui/dom.js` `isRepeatClick`). Whether WebKit's synthetic second tap carries `detail` 2 is UNVERIFIED. If it carries 1, WebKit on Windows cannot tell an artefact of Playwright's tap from a real Safari gap, and only an iPhone can |
| Split | `test_R10_*` touch variants (`press(page, "touch", ...)`) | The comment in `src/ui/field-leave.js` relies on the order "pointerup first and the mouse events after it" for a tap. WebKit's tap event order is UNVERIFIED |
| Streaks | `test_delete.py` touch rows (`press_twice`, `open_by_press` with `touch=True`) | The guard uses `event.timeStamp` (clock driven, engine neutral) and `event.detail > 0` for a tap. Lower risk, UNVERIFIED |
| Streaks | `test_platform.py::test_R23_motion_without_reduced_motion`, `test_R23_everything_appears_at_once_under_reduced_motion` | Read `getComputedStyle(dialog, '::backdrop')`. WebKit support for that pseudo-element in `getComputedStyle` is UNVERIFIED |
| Streaks | `test_platform.py::test_R22_focus_rings_on_keyboard_focus` | Compares the computed `outline` shorthand string. Serialisation in WebKit is UNVERIFIED |
| Streaks | `test_platform.py::test_R26_no_globals_and_no_hooks` | Compares `Object.getOwnPropertyNames(window)` between two pages. WebKit's list may differ, UNVERIFIED |
| Streaks | `test_platform.py::test_R25_the_csp_is_in_force` | Matches CSP console text. Wording UNVERIFIED |
| Both | any assertion on the size of wrapped text | Different rasteriser and possibly a different face |
| Split | `test_R39_*` clipboard tests | Pass if `http://127.0.0.1` is a secure context in WebKit, UNVERIFIED |

## Per-app notes

### Split

- **Files the plan touches.** `tests/browser/rig.py` (`ENGINES`, `launch`), `tests/browser/conftest.py` (option, `engine` fixture, marker, evidence folder suffix, merged into its existing `pytest_configure`), `tests/browser/live_e2e.py` (flag, `rig.launch`, summary), `tests/browser/test_app.py` (the marker on the CDP test, the WebKit branch of `test_R40_a_seed_script_boots_the_app_through_its_own_load_path`, and what the probe finds). `tests/browser/fidelity/run.py` stays as it is.
- **Meta tests.** `test_R39_only_the_rig_makes_browser_contexts` and `test_R41_the_gate_uses_real_gestures_and_reads_only` must keep passing (the live gate must still make exactly one context through the rig). Add a twin that only `rig.py` launches a browser.
- **S3 (SEC-04).** The fix uses `event.repeat` and a cancelled keydown. The same mechanism works in WebKit (section 2), so the S3 tests run in both engines.
- **Clipboard.** Keep the live gate's step 1 check that `Clipboard.prototype.writeText` is not native before any gesture. It is the proof that the stand-in, not the OS clipboard, is in use in WebKit too.
- **Spec text.** `docs/modules/split-app/spec.md` line 18 says "Headless Chromium through Python Playwright is the only test browser". It needs the S5 amendment. Line 19 already names WebKit for native dialogs, and D8 and PD-10 already count names in grapheme clusters because WebKit counts `maxlength` that way.
- **Look.** The new goldens use `backdrop-filter` glass. WebKit screenshots on Windows probably show the card without blur (UNVERIFIED). That is a property of the test browser, not of Safari on an iPhone.

### Streaks

- **Files the plan touches.** `tests/browser/conftest.py` (option, `engine` fixture, `launch` with `--force-color-profile=srgb` for Chromium only, marker), `tests/browser/live_e2e.py` (flag, launch, summary `"browser"`), `tests/browser/test_add.py` (the R10 WebKit expectation), and what the probe finds. `harness/_scratch/run_browser_tests.py` already forwards pytest arguments, so `--engine webkit` passes through.
- **Clock.** Fully supported, because Playwright's clock is a page script (section 2). The guard window tests in `test_delete.py` and the rollover tests in `test_rollover.py` need no change for the clock itself.
- **Spec text.** `docs/modules/app/spec.md` line 30 says "Tests run on headless Chromium only (CLAUDE.md), so Safari and Firefox behaviour is not verified by this plan", and R27 (line 147) says "In a fresh headless Chromium context". Both need the S5 amendment.
- **Storage expiry.** Safari's 7-day rule (section 3) matters most here, since the whole habit history lives in `localStorage`. No test can show it.

## Recommendation for the plan

1. **Clarify gate first.** The owner approves the install (item 1 below). Nothing else in S5 can start before it.
2. **Task 0, the engine switch, before any other v1.1.0 task.** The option, the launch helper, the marker and the evidence naming of section 5, in both projects. Default stays Chromium, and the Chromium run must stay green with the same counts.
3. **Probe step in that task (a live probe for the build, not run by this research).**
   - After the install, `python -m playwright install --dry-run webkit` and a listing of `ms-playwright` show `webkit-2311`.
   - One headless WebKit launch prints `browser.version` and closes. Then `tasklist /FI "IMAGENAME eq Playwright.exe"` shows none left (constitution, process accounting).
   - `python -m pytest tests/browser -q --engine webkit -rfE` in each project on the current tree, and each live gate with `--engine webkit`. Record pass, fail and skip counts, every failure and the run time.
   - Small targeted probes for the UNVERIFIED rows. The click `detail` and event order of two quick taps with `has_touch`. `typeof Clipboard` and `isSecureContext` on `http://127.0.0.1`. `getComputedStyle(dialog, '::backdrop')`. A screenshot of the glass card. The console text of a CSP block and of a denied `localStorage`. The computed `outline` string.
   - Classify each failure as (a) an app defect Safari would show, fixed in the app, (b) an engine difference in a test expectation, written into the spec with its measurement and asserted per engine, or (c) Chromium-only tooling, marked `chromium_only` with a reason.
4. **Write the rule into the docs.** Each project's `CLAUDE.md` stack line ("headless Chromium only"), both specs (lines named in Per-app notes), each `qa.md` (functional suite, live gate, regression) and each `docs/regression/REGRESSION.md` (WebKit rows with their own counts and times).
5. **Gate definition for v1.1.0.** Chromium functional suite and live gate green. WebKit functional suite green with only listed skips, and WebKit live gate green. Fidelity green in Chromium. Every new v1.1.0 test runs in both engines from its first commit.
6. **Real iPhone cases in the v1.1.0 UAT script.** WebKit on Windows cannot prove touch gestures (item 6 below).

## Clarify-gate items for the owner

1. **May the build install WebKit with `python -m playwright install webkit`?** It downloads about 62 MB from Playwright's CDN (a Microsoft host) into `{home}\AppData\Local\ms-playwright\webkit-2311`, unpacked size about 180 MB (UNVERIFIED on Windows). No system change, no admin rights. **Recommended answer.** Yes.
2. **Should the fidelity pixel gate also run in WebKit?** **Recommended answer.** No. Keep it Chromium only. WebKit runs the functional suites and the live gates, and the WebKit live gate's per-step screenshots are kept as WebKit pictures for you to look at.
3. **Where WebKit behaves differently in a way the app does not control (a clicked button takes no focus), should each engine's own behaviour be tested and written in the spec?** **Recommended answer.** Yes. Forcing Chromium's behaviour in the app would be a product change you would have to ask for.
4. **May a test that needs a Chromium-only tool be skipped in WebKit, with a written reason and counted in the evidence?** Today that is only the Split IME test. **Recommended answer.** Yes.
5. **Is a WebKit failure blocking for the v1.1.0 seal?** **Recommended answer.** Yes, for the functional suites and the live gates, once the probe has sorted the first run's differences.
6. **Add a few cases on your own iPhone to the v1.1.0 UAT?** Split, a double tap on Remove of the last person and on Cancel in the New bill dialog. Streaks, a double tap on a trash button and then on Delete habit. A look at each screen. **Recommended answer.** Yes. WebKit on Windows cannot prove the iPhone's tap handling, and Split's double-tap guard depends on it.
7. **Change the stack line in each project's `CLAUDE.md` from "headless Chromium only" to Chromium plus WebKit for the functional suites and the live gate?** **Recommended answer.** Yes, as part of this plan, since the stack is locked in that file.
8. **Information only, Safari's 7-day storage rule.** Safari clears a site's `localStorage` after seven days of Safari use without visiting the site. A Home Screen web app keeps its data. **Recommended answer.** Note it as a known limit in each README. No code in v1.1.0.

## Sources

Playwright documentation and code
- [Playwright, Browsers](https://playwright.dev/python/docs/browsers)
- [Playwright, Clock](https://playwright.dev/python/docs/clock)
- [Playwright, Emulation](https://playwright.dev/python/docs/emulation)
- [Playwright API, Browser](https://playwright.dev/python/docs/api/class-browser)
- [Playwright API, BrowserContext](https://playwright.dev/python/docs/api/class-browsercontext)
- [Playwright test, page-keyboard.spec.ts](https://github.com/microsoft/playwright/blob/main/tests/page/page-keyboard.spec.ts)
- [Playwright test, tap.spec.ts](https://github.com/microsoft/playwright/blob/main/tests/library/tap.spec.ts)
- [Playwright test, browsercontext-timezone-id.spec.ts](https://github.com/microsoft/playwright/blob/main/tests/library/browsercontext-timezone-id.spec.ts)
- [Playwright test, page-emulate-media.spec.ts](https://github.com/microsoft/playwright/blob/main/tests/page/page-emulate-media.spec.ts)
- [Playwright CI, tests_secondary.yml (job "Windows", browsers chromium, firefox, webkit)](https://github.com/microsoft/playwright/blob/main/.github/workflows/tests_secondary.yml)
- Installed driver, read on this machine. `{home}\AppData\Roaming\Python\Python314\site-packages\playwright\driver\package\lib\coreBundle.js` (`wkInput.ts`, `wkPage.ts`, WebKit `defaultArgs`, `clockSource.ts`, `installDependenciesWindows`, executable table), `...\driver\package\browsers.json`, `...\driver\package\bin\install_webkit_wsl.ps1`
- Command output on this machine. `python -m playwright --version`, `python -m playwright install --help`, `python -m playwright install --dry-run webkit`, a header-only `curl -sIL` of the download URL

WebKit source and documentation
- [WebKit, HTMLFormControlElement.cpp (`isMouseFocusable`)](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/html/HTMLFormControlElement.cpp)
- [WebKit, EventHandler.cpp (`tabsToAllFormControls`, mouse-down focus)](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/page/EventHandler.cpp)
- [WebKit, HTMLButtonElement.cpp (Enter on keypress, Space on keyup)](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/html/HTMLButtonElement.cpp)
- [WebKit, UnifiedWebPreferences.yaml (`AsyncClipboardAPIEnabled`)](https://github.com/WebKit/WebKit/blob/main/Source/WTF/Scripts/Preferences/UnifiedWebPreferences.yaml)
- [WebKit bug 271340, backdrop-filter forces compositing](https://bugs.webkit.org/show_bug.cgi?id=271340)
- [webkit.org, Full Third-Party Cookie Blocking and More](https://webkit.org/?p=10218)

CSS support
- [caniuse, scrollbar-width](https://caniuse.com/mdn-css_properties_scrollbar-width)
- [Chrome for Developers, Scrollbar styling (Safari version for scrollbar-color)](https://developer.chrome.com/docs/css-ui/scrollbar-styling)
- [caniuse, user-select none](https://caniuse.com/user-select-none)

Project files read (both projects unless named)
- `CLAUDE.md`, `docs/constitution.md` (identical in both), `docs/v1.1.0/CHANGE-LEDGER.md` (S5), `docs/progress/STATE.md`, `docs/brainstorm/brainstorm.md`
- `tests/browser/conftest.py`, `tests/browser/live_e2e.py`, Split `tests/browser/rig.py`, `support.py`, `test_app.py`, `pytest.ini`, `clipboard/*.js`, `fidelity/run.py`, Streaks `test_add.py`, `test_delete.py`, `test_platform.py`, `test_rollover.py`, `test_storage.py`, `test_tick.py`, `harness/_scratch/run_browser_tests.py`
- `index.html`, Split `src/ui/dialog.js`, `src/ui/dom.js`, `src/ui/field-leave.js`, `src/draft.js`, `src/main.js`, Streaks `src/app.js`, `src/view.js`
- `docs/design/system.css`, Split `docs/modules/split-app/qa.md` (Fidelity gate), `spec.md`, `findings/security.md` (SEC-04), `docs/modules/ROADMAP.md` (PD-10, PD-13), Streaks `docs/modules/app/qa.md` (Fidelity gate), `spec.md`, both `docs/regression/REGRESSION.md`
- Not read, on purpose. The plugin harness `{sdlc}/harness/fidelity.py` sits outside this workspace. What it does is taken from each project's `qa.md`.
