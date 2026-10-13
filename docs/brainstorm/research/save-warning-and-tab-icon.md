---
question: S4 save warning and S6 tab icon in Split and Streaks v1.1.0. How localStorage fails in Chromium and WebKit, what "saving fails" means, how tests drive it with no app hook, what the same-origin hub iframe changes, and how the golden's SVG data URI tab icon fares with browsers, the shipped CSP and the tests
verdict: feasible-with-caveats
---
# Save warning (S4) and tab icon (S6), Split and Streaks v1.1.0

Shared by both apps. The same text sits at `split/docs/brainstorm/research/save-warning-and-tab-icon.md` and `streaks/docs/brainstorm/research/save-warning-and-tab-icon.md`. Written 2026-10-13 by the sdlc researcher, plan phase. Nothing was run in a browser. Every claim cites a source or a file read, and anything not verified is marked UNVERIFIED.

## Question
**Part A, the save warning (ledger S4).** (1) Every way `localStorage` fails in current Chromium and Safari or WebKit, which failures throw on read and which on write, and the exception names. (2) A precise, testable meaning of "saving fails" and when the warning clears. (3) How a Playwright test drives each failure in Chromium and WebKit with no hook in the app, and which drivers are faithful. (4) Whether storage works inside the hub's same-origin iframe and whether the keys clash.

**Part B, the tab icon (ledger S6).** (5) Browser support for an SVG data URI favicon and for `prefers-color-scheme` inside it. (6) Whether the shipped CSP allows it and what must change. (7) What a home-screen icon would need. (8) How a test proves the tab icon is wired.

## Verdict per part
- **Part A, save warning. FEASIBLE WITH CAVEATS.** Every failure that throws is already caught in both apps, so the warning only needs the result to be passed up. Two kinds of loss can never show it, because nothing fails while the tab is open (private browsing, Safari's 7-day deletion). The sealed 1.0 rules Split R28 and Streaks R18 (CG-5) say "no message" and must be replaced. Proxy tests run in both engines, and a real quota fill gives one faithful test per engine.
- **Part B, tab icon. FEASIBLE WITH CAVEATS.** The golden's `data:` icon breaks the shipped rules of both apps as they stand. The CSP blocks it (Split `img-src 'self'`, Streaks `default-src 'self'` with no `img-src`), R1 in both apps forbids a URL with a scheme in `index.html`, and Split's R39 scan forbids `://` in shipped files. Shipping the same SVG bytes as `src/icon.svg` keeps both CSPs unchanged. Safari 26 shows SVG and `data:` icons but ignores the light and dark switch inside them (WebKit bug 309949, open). Safari before 26 shows no SVG icon at all.

**Recommendation:** Show the warning from the result of the latest save attempt (any throw, or no storage object, means failed), plus at boot when the boot read fails. Ship the tab icon as `src/icon.svg` holding the golden's decoded SVG, with no CSP change.

**How:** Split already returns a boolean from `saveDraft`. Streaks' `saveHabits` must return one and `loadHabits` must report a failed read. Tests use test-side init scripts that replace `Storage.prototype.setItem` or the `window.localStorage` getter, switched off through a `CustomEvent`, plus one real quota fill per engine. The icon is `<link rel="icon" type="image/svg+xml" href="src/icon.svg">` after the CSP meta, its bytes compared to the decoded golden href.

**Pitfalls:** The app must never read the error's name or code (it differs by engine and version). Private browsing cannot trigger the warning, so UAT must use a blocked-storage setting. A quota test must make a change that grows the stored text. Split's R39 scan needs one narrow exemption for the SVG namespace inside `src/icon.svg`. Safari shows one icon colour in both themes. Do not copy `docs/brand/favicon.svg`, which is the 1.0 mark on a tile.

**Feasibility:** feasible-with-caveats. Evidence below. Nothing blocks either scope. The caveats are a few spec deltas per app, one residual the warning cannot cover, and one Safari bug the apps cannot fix.

---

## Evidence, Part A

### A1. How `localStorage` fails today

| # | Case | What fails | Chromium | WebKit and Safari | Source |
|---|---|---|---|---|---|
| 1 | Storage blocked by a user setting. Chrome "Don't allow sites to save data on your device" (Site settings, On-device site data) or a per-site block. Safari "Block All Cookies" on macOS and iPhone | Reading the `window.localStorage` property throws, so every read and every write fails | `SecurityError` DOMException, legacy code 18. Message `Failed to read the 'localStorage' property from 'Window': Access is denied for this document.` | `SecurityError`, message `SecurityError (DOM Exception 18): The operation is insecure.` (forum reports, secondary) | HTML spec getter ("if the request violates a policy decision"), MDN localStorage, chromium.org page, Google Chrome Help, DRACOON and Apple forum (secondary). Split `tests/browser/test_app.py` lines 2231 to 2233 records the Chromium message from the blank first document |
| 2 | Opaque origin. An `<iframe sandbox>` without `allow-same-origin`, or a `data:` document | The getter throws | `SecurityError` | `SecurityError` | HTML spec ("if the Document's origin is an opaque origin"), MDN localStorage |
| 3 | Quota full. About 5 MiB of localStorage per origin, shared by every page on the origin | `setItem` throws. Reads keep working | Name `QuotaExceededError`. Chrome and Edge 138 and later have a `QuotaExceededError` interface that extends DOMException (MDN compat data). Older engines throw a plain DOMException with that name, legacy code 22. Which class Chromium's `setItem` throws in a given version is UNVERIFIED | DOMException named `QuotaExceededError`, code 22. Safari is not listed as having the new interface | HTML spec setItem step 4, MDN setItem, MDN quotas, MDN QuotaExceededError, Web IDL discussion (search summary) |
| 4 | Private browsing today. Safari Private, Chrome Incognito | Nothing throws. Writes succeed and the data is deleted when the last private tab closes | no error | no error | MDN localStorage, MDN quotas |
| 5 | A cross-site iframe (not the hub case) | Nothing throws. The frame gets its own partitioned store | no error, partitioned since Chrome 115 | no error, a separate partition with 10% of the main frame's quota | Privacy Sandbox storage partitioning, WebKit storage policy (Safari 17) |
| 6 | A same-site iframe (the hub case) | Nothing. The frame shares the app's own store | no error | no error | Privacy Sandbox ("their storage remains shared"), WebKit storage policy (only cross-origin frames are partitioned) |
| 7 | `window.localStorage` is `null` | `getItem` on null is a TypeError | not seen | not seen | Old reports for Firefox with `dom.storage.enabled=false`, others say it throws. UNVERIFIED |
| 8 | Safari's 7-day deletion with cross-site tracking prevention on | Nothing at the time. Script-written data is deleted after 7 days of Safari use with no interaction on the site. Home Screen web apps keep their own day count | not applicable | silent | WebKit "Full Third-Party Cookie Blocking and More" (2020), MDN quotas |
| 9 | `getItem` throws while the getter works | No documented trigger found | UNVERIFIED | UNVERIFIED | test proxy only |

Read or write, in short. Cases 1 and 2 fail on read (the getter), so both reads and writes fail. Case 3 fails on write only. Cases 4, 5, 6 and 8 never throw.

One spec detail matters for tests. `setItem` with the value already stored returns before the quota check (HTML spec setItem step 3, "If oldValue is value, then return"). Whether every engine does this is UNVERIFIED.

Both apps already catch every one of these. Split `src/draft.js` guards the getter (`getStorage`, lines 82 to 89), `getItem` (lines 92 to 103) and `setItem` (lines 106 to 114), and `saveDraft` already returns `false` on any failure. Streaks `src/storage.js` guards `getItem` (lines 75 to 80) and `setItem` (lines 89 to 95), and a null store becomes a caught TypeError. Neither app listens to the `storage` event (grep of both `src/` folders, no match).

### A2. What "saving fails" should mean

The owner's copy says the warning "shows while saving fails and goes away after the next save works. It cannot be dismissed" (both `docs/brainstorm/brainstorm.md`, v1.1.0 delta). The sealed 1.0 specs say the opposite. Split R28 "shows no message" (`docs/modules/split-app/spec.md` line 65) and Streaks R18, "no message shows" (`docs/modules/app/spec.md` line 122, CG-5). Both 1.0 specs also forbid a write at boot (Split R2 "Nothing is written to storage until the first change", Streaks R3 and R16 "Loading writes nothing"), which rules out a probe write.

Recommended definition, numbered SW so it does not clash with Split's decoder rules D1 to D12.

- **SW1. A save attempt** is every call that writes the app's key. Split `saveDraft`, called by each `commit` that changes the bill, the R27 reset save at boot and Start new bill (`src/main.js` lines 26 and 54). Streaks `saveHabits`, called by add, tick, delete and the R17 reset (`src/app.js` lines 50, 63 and 144, `src/storage.js` line 84), and in 1.1.0 by Done today, both year views and the day editor.
- **SW2. A save attempt fails** when the storage object cannot be obtained (the getter throws or returns null) or `setItem` throws. Any exception counts. The app never reads the error's name or code, because the class and the code differ by engine and version (A1 row 3).
- **SW3. A save attempt succeeds** when `setItem` returns.
- **SW4. The latest attempt decides.** After every attempt the warning shows if it failed and is removed if it succeeded. No timer, no probe write, no read back. A change that writes nothing (Split skips a commit when the bill is unchanged) leaves the warning as it is.
- **SW5. Boot.** If the boot read fails (the getter throws or is null, or `getItem` throws), the warning shows from the first render, because no change can be kept. A readable or empty store shows no warning at boot, since a cold boot makes no attempt. This is a reading of the owner's rule and goes to the clarify gate (CG-1).
- **SW6. Retry the getter.** While the storage object could not be obtained, each later save attempt reads `window.localStorage` again, so the warning can clear without a reload. Split today reads the getter once at boot (`src/main.js` line 22).
- **SW7. Quiet live region.** The warning's DOM changes only when the state flips, so the `role="status"` region is not touched on every keystroke near the quota edge.
- **SW8. Out of scope, stated as a known limit.** Private browsing, Safari's 7-day deletion and the user clearing site data lose data with no failure the page can see (A1 rows 4 and 8). A write that silently does nothing is not documented for any current engine, so a read back would add cost for no known case.

Testable statements that follow. (a) A cold boot with working storage shows no warning. (b) The first change whose save throws shows the exact approved copy, `role="status"`, and no dismiss control. (c) While saves keep failing the warning stays, and after a reload it shows again only per SW5 or on the next failed save. (d) The first change whose save works removes it, and the stored text then equals the encoded state on screen. (e) With the getter throwing at boot, the warning is in the first render (if CG-1 is ruled yes). (f) An unreadable saved value plus a failing reset save shows both the unreadable note and the warning.

### A3. Driving each failure in Playwright with no app hook

Playwright's `add_init_script` runs "after the document was created but before any of its scripts were run", in every page and every child frame, and the order between several init scripts "is not defined" (Playwright BrowserContext docs). No documented `new_context` option blocks storage. Playwright's WebKit is built from WebKit main with Playwright patches and "doesn't work with the branded version of Safari", and features vary by platform (Playwright browsers page). So a WebKit run on this Windows machine proves WebKit's storage code, not Safari's settings or tracking prevention.

| Driver | Engines | Faithful or proxy | Notes |
|---|---|---|---|
| D-a. Init script replaces `Storage.prototype.setItem` with a function that throws `new DOMException('...', 'QuotaExceededError')`, keeps the original in a closure and is switched off by a `CustomEvent` from the test | Chromium and WebKit | Proxy | Covers SW2 to SW4 and the recovery. The error object is test-made, so its class and code may differ from the engine's own. Harmless because the app must not read them (SW2). Adds no property to `window`, so Streaks' R26 "no globals" check keeps its meaning |
| D-b. Init script redefines `window.localStorage` with a getter that throws `SecurityError` | Chromium (in use today). WebKit UNVERIFIED | Proxy | Split `test_app.py` lines 1178 to 1182 and Streaks `test_storage.py` lines 173 to 181 already use it. Whether WebKit lets the property be redefined is UNVERIFIED (probe P1). Covers SW5 and, with the switch, SW6 |
| D-c. Init script makes `Storage.prototype.getItem` throw | Both | Proxy | No real trigger is known (A1 row 9). Keeps the boot path honest |
| D-d. Real quota fill. A test-side `page.evaluate` on the app's origin writes filler keys until even one more character is refused, then a real gesture makes a change that grows the stored text. Removing the filler and making one more change proves the clear | Chromium and WebKit | **Faithful** | The engine throws its own `QuotaExceededError` through the app's own `setItem` call. It is the same thing a sibling page on the shared origin can cause (A4). Each Playwright context has its own storage, so filler never leaks between tests |
| D-e. A test-only host page embeds the app in `<iframe sandbox="allow-scripts">` | Both | Faithful (real `SecurityError`) | Heavy. Module scripts are fetched in CORS mode (HTML spec, not re-checked here), so in an opaque-origin frame served by `python -m http.server` (no CORS headers) the app would not boot at all. UNVERIFIED end to end. Optional |
| D-f. Chromium persistent context whose `Default/Preferences` blocks site data (`profile.default_content_setting_values.cookies = 2`) | Chromium only | Faithful | UNVERIFIED with Playwright's bundled Chromium. Needs `launch_persistent_context`, which Split's rule that only the rig makes contexts (`test_app.py` line 98) would have to allow. Optional |
| D-g. Private browsing | none | not drivable | Nothing fails, nothing to assert (SW8) |
| D-h. Owner UAT on real devices. Safari "Block All Cookies" on iPhone and Mac, Chrome "Don't allow sites to save data on your device" | Safari, Chrome | Faithful | The only check of the real settings. Private mode must not be used to look for the warning |

The init-script switch for D-a, test-side only and never shipped.

```js
(() => {
  const realSetItem = Storage.prototype.setItem;
  let failing = true;
  addEventListener("test:storage", (event) => { failing = event.detail; });
  Storage.prototype.setItem = function (key, value) {
    if (failing) throw new DOMException("test quota", "QuotaExceededError");
    return realSetItem.call(this, key, value);
  };
})();
```

The test turns it off with `page.evaluate("dispatchEvent(new CustomEvent('test:storage', { detail: false }))")`. The script must not touch `localStorage` at its top level, because it also runs in the blank first document where storage access is denied (Split `test_app.py` lines 2231 to 2233).

The filler for D-d, run with `page.evaluate` on the app's page before the change.

```js
() => {
  let size = 1 << 20, n = 0;
  while (size >= 1) {
    try { localStorage.setItem("test.fill." + n++, "x".repeat(size)); }
    catch { size = Math.floor(size / 2); }
  }
}
```

Pitfalls for D-d. The change after the fill must grow the stored text (a write of the same or a shorter value can succeed, see the spec detail under A1). The boot read still works in this state, so per SW5 there is no warning until that change. How long the fill takes in each engine is UNVERIFIED (probe P2).

Recommended matrix. In both engines, the proxies D-a to D-c for statements (a) to (f) in A2, and D-d once per app for the real failure and the clear. D-h as a UAT case. D-e and D-f only if the plan wants a faithful blocked-getter test in the suite.

### A4. The hub's same-origin iframe

- GitHub serves every project site of one account at `https://<owner>.github.io/<repositoryname>` (GitHub Pages docs), so the hub at `/sdlc-showcase/` and the apps at `/split/` and `/streaks/` share one origin. `github.io` is on the Public Suffix List, so `<owner>.github.io` is its own site (jefftk history of the list, secondary).
- **Storage works in the iframe in both engines and is not partitioned.** Chrome keys storage by origin and top-level site plus an ancestor bit, and in a chain of only same-site contexts "their storage remains shared" (Privacy Sandbox, Chrome 115). WebKit gives a separate partition only to a cross-origin frame (WebKit storage policy). Firefox is expected to behave the same, UNVERIFIED.
- **So the framed app and the app opened on its own use the same key.** A bill or habit list made in the hub is there when the app is opened directly, and the reverse.
- **The keys do not clash.** `split.draft` (`src/draft.js` line 9) and `streaks.state` (`src/storage.js` line 11) are different. The plan must state that the hub never writes either key, never calls `localStorage.clear()`, and prefixes any key of its own (for example `showcase.`).
- **One quota for the whole origin.** About 5 MiB (MDN) is shared by the hub, both apps and every other project site of the account. If any of them fills it, the apps' saves fail and the warning shows, which is the intended behaviour.
- **Two live copies overwrite each other.** With no `storage` listener, the app in the hub frame and the same app in its own tab each keep their own state in memory and the last write wins. A 1.0 residual, unchanged, but the hub makes it more likely. The plan should state it.
- **No `sandbox` on the hub's frames.** Without `allow-same-origin` the frame has an opaque origin and the getter throws `SecurityError` (HTML spec), so every visitor would see the warning, and the module scripts would need CORS headers to load. The frames are the owner's own pages on the same origin, so the hub plan should use no `sandbox` attribute.
- Streaks threat T10 says "a framed copy sees an empty, separate store" (`docs/modules/app/spec.md` line 334). That holds for a cross-site framer only and does not describe the hub.

---

## Evidence, Part B

### B5. Browser support for the SVG data URI icon

The goldens deliver the icon as `<link rel="icon" ... href="data:image/svg+xml,...">`. Decoded here (read-only script), each is a 16 x 16 SVG with a `<style>` that sets the default fill and switches it under `@media (prefers-color-scheme:light)`, plus the same default as a `fill` attribute, which is the fallback if the style is not applied.

| | Split | Streaks |
|---|---|---|
| Default fill (dark browser theme) | `#A3AAFF` | `#FFB020` |
| Under `prefers-color-scheme: light` | `#1E2140` | `#9A5B00` |
| `type` attribute on the golden link | `image/svg+xml` | none |
| Goldens carrying the link | 15 of 15, one identical href | 8 of 9, one identical href, `states.html` has none |
| Decoded SVG | 470 bytes, root in the SVG namespace, viewBox `0 0 16 16` | 458 bytes, same |

| Browser | SVG icon | `data:` URL icon | `prefers-color-scheme` inside |
|---|---|---|---|
| Chrome and Edge | Yes since 80 (caniuse) | Widely used (secondary), not checked against a primary source, UNVERIFIED | Yes (web.dev adaptive favicon, 2022). The Streaks ruling records Chromium giving 255 176 32 in dark and 154 91 0 in light (`docs/design/RULINGS-v1.1.0.md` line 29) |
| Firefox | Yes since 41 (caniuse) | Widely used (secondary), UNVERIFIED | Yes (web.dev) |
| Safari 26 on macOS | Yes. Safari 26.0 notes "Added support for SVG icons" | Yes. Safari 26.0 notes "Added support for `data:` URL icons" | **No.** WebKit bug 309949 "SVG favicons don't respect media query overrides, notably for dark mode", status NEW, tested on Safari 26.3, confirmed by a WebKit engineer, who adds "we need to do something different for favicons" |
| Safari 26 on iPhone | Yes (caniuse 26.0, WebKit WWDC25 post "everyplace there are icons in the interface, including favicons") | Yes (same) | No, same bug. UNVERIFIED on a device |
| Safari before 26 (macOS 15 and older, iOS 18 and older) | No | No | Not applicable |

**What Safari 26 shows instead.** One colour in both themes. In bug 309949 Safari kept the icon's default in dark mode. Comments on the older bug 199134 say Safari applied the light styles to SVG images in dark mode. Since both goldens put the override on the light side, the likely result is the light colour (`#1E2140`, `#9A5B00`) in both themes, which on a near-black tab bar is about 1.1 to 1 for Split and 3.1 to 1 for Streaks (computed here against `#1E1E1E`, the real Safari bar colour is UNVERIFIED). If Safari instead keeps the default, the pale colours sit on a light bar at about 2.2 to 1 for Split and 1.8 to 1 for Streaks (computed against white). Which one appears is UNVERIFIED (probe P4). WebKit's 2026 fixes make SVG images follow the system theme in Safari Technology Preview (bug 199134, comment of 2026-06-10), but the favicon case is tracked separately and was still open.

**What Safari before 26 shows.** No icon from the link. The HTML spec allows a fallback to `/favicon.ico` resolved against the document URL only "in the absence of a link with the icon keyword", and that path is the origin root `https://<owner>.github.io/favicon.ico`, outside both apps. What Safari draws when it has no icon (a letter tile or a blank) is UNVERIFIED.

### B6. The shipped CSP and the other 1.0 rules

| Rule | Split today | Streaks today | Effect on the golden's `data:` icon |
|---|---|---|---|
| CSP meta | `default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; base-uri 'none'; form-action 'none'` (`index.html` line 6, spec R38 "exactly") | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'` (`index.html` line 5, spec R1) | **Blocked in both.** The icon fetch has destination "image" (HTML spec), `img-src` governs "images and favicons" and falls back to `default-src` (MDN img-src). `'self'` never matches `data:`, because CSP3 requires a non-HTTP(S) scheme to be listed explicitly. The WPT test `img-src/icon-blocked.sub.html` passes in Chrome, Edge and Firefox (icon blocked and a violation for `img-src` fired), Safari has no recorded result (wpt.fyi). Chromium logs each violation as a console error (Split `qa.md` line 21), which fails both suites' clean-console rules |
| Relative URLs only | R1 "Every URL in `index.html` ... is relative (no leading `/`, no scheme)" | R1 same, and `test_entry.py` asserts `"://" not in url` for every URL in `index.html` | A `data:` href is a URL with a scheme, and its SVG holds the literal `http://www.w3.org/2000/svg` (measured) |
| Split R39 static scan | `test_R39_nothing_leaves_the_device_by_the_static_scan` asserts `"://" not in index.html` and scans every shipped file for scheme strings, exempting only `createElementNS("http://www.w3.org/2000/svg", ...)` | not applicable | Fails on the `xmlns` inside the data URI, and would fail the same way on a separate SVG file |
| Split out-of-scope list | spec line 374 lists "a favicon" among things not built | not applicable | Must drop it |

The SVG cannot drop its `xmlns`, because an SVG image is parsed as XML and needs the namespace on its root. The inline header mark is different. In HTML markup an inline `<svg>` needs no `xmlns` (the goldens' header marks have none), so it keeps `index.html` free of `://`.

**Option B, recommended.** Ship the decoded golden SVG as `src/icon.svg` and link it with `<link rel="icon" type="image/svg+xml" href="src/icon.svg">`, placed after the CSP meta (CSP3 says a meta policy does not apply to content before it).
- Split. CSP unchanged (`img-src 'self'` allows it). R1 relative-URL rule holds. R39's request list already allows "files under `/src/`". R39's static scan needs one exemption, the SVG namespace as the `xmlns` of the root element of `src/icon.svg`, a name that is never requested, like the CG-10 exemption. R1's head order gains the link.
- Streaks. CSP unchanged (`default-src 'self'` allows it). R1 relative-URL test passes. R25's request list (`/`, `/index.html`, `/favicon.ico`, `/src/styles.css`, `/src/<name>.js`) gains `/src/icon.svg`. R1's head order gains the link. No scan exemption is needed.
- It also sidesteps an open Firefox report that `data:` SVGs may inherit the page's CSP and lose their inline styles (Mozilla bug 1358106, UNCONFIRMED), which would hit Split's strict `style-src 'self'`. A same-origin SVG file is its own document, and Firefox ignores a CSP on SVG images since Firefox 77 (Mozilla bug 1262842).
- The cost is one same-origin GET for a static file, like the existing CSS and JS. The host must serve it as `image/svg+xml`. GitHub Pages is expected to, and `python -m http.server` on Windows takes its types from Python's `mimetypes`, which can read the registry, UNVERIFIED (probe P3).
- `docs/brand/BRAND.md` (Split) already planned this ("copy it into `src/` when it ships, the CSP already allows `img-src 'self'`"). But both `docs/brand/favicon.svg` files are the 1.0 marks on a solid tile (read here). The source of truth is the golden's href, decoded.

**Option A, the alternative.** Keep the golden's link byte for byte. Change Split to `img-src 'self' data:` and add `img-src 'self' data:` to Streaks, amend R1 in both apps to allow exactly one `data:image/svg+xml` URL, and amend Split R39 so the namespace inside that URL is allowed. No extra request. More rule changes per app, the CSP widens (to images only, and neither app writes markup from data, Split R37 and Streaks R24), and the Firefox report above stays open for Split.

### B7. A home-screen icon (not in S6, for the clarify gate)

The roadmap once said "the favicon (the browser tab and the home-screen icon)" (`OWNER-ROADMAP.md` line 80). Ledger S6 in both apps says only "The logo shows in the app's header and as the browser tab icon".

- **iPhone.** A PNG of 180 x 180 (60 pt at 3x, realfavicongenerator 2026) linked with `<link rel="apple-touch-icon" href="src/apple-touch-icon.png">`. Without a link, iOS looks for `apple-touch-icon.png` in the site root (Apple Safari Web Content Guide, archived), which for a project site is `<owner>.github.io/apple-touch-icon.png`, outside the app and outside its publish copy, so the link is required. iOS does not keep transparency and paints clear pixels black (Apple Developer Forums, community answer), so the PNG needs an opaque square ground, and iOS rounds the corners itself.
- **iOS 26 may already make one.** Safari 26 uses SVG and `data:` icons "everyplace there are icons in the interface", including Home Screen web apps, and uses manifest icons when defined (WebKit WWDC25 post). Every site added to the Home Screen now opens as a web app by default (same post, Safari 26.0 notes). What iOS 26 draws from a transparent SVG tab icon is UNVERIFIED and needs an iPhone check.
- **Android.** Chrome uses a web app manifest's icons, 512 x 512 at least and 192 x 192 recommended, with `purpose: maskable` for adaptive icons (web.dev Learn PWA). Without a manifest, older Chrome used the largest favicon or the apple-touch-icon (firt.dev, 2013, dated, UNVERIFIED today). A manifest is linked with `<link rel="manifest" href="src/app.webmanifest">` and served as `application/manifest+json` or another JSON type (web.dev). In Split it would also need `manifest-src 'self'`, because `manifest-src` falls back to `default-src` (MDN) and Split's is `'none'`. Streaks' `default-src 'self'` allows it. A manifest also brings `display`, `start_url` and install choices, which is new product scope.
- **Where the files live.** Under `src/`, since only `index.html`, `src/` and `.nojekyll` are published (both `CLAUDE.md`, Publish).
- **Zero network.** Static same-origin files fetched by the browser for its own interface, with nothing sent by the app's code and no third party. It fits the rule. Two frictions remain. A PNG is a binary made outside the no-build stack (rendered once and committed), and an opaque ground contradicts the ruling "no background, no tile" (`docs/design/RULINGS-v1.1.0.md`, both apps), so it needs a design ruling first.

### B8. Testing the tab icon with no visible tab

1. **Static, Node or pytest.** `index.html` has exactly one `link[rel~="icon"]`, after the CSP meta, with `type="image/svg+xml"` and the relative href `src/icon.svg`. The bytes of `src/icon.svg` equal `urllib.parse.unquote` of the payload after the first comma of the golden's href, checked against every golden that carries it. The file parses as XML with root `{http://www.w3.org/2000/svg}svg` and viewBox `0 0 16 16`.
2. **Live wiring, both engines.** In the running app the link's resolved `href` is the app's own `src/icon.svg`, including under Streaks' sub-path test.
3. **Policy, both engines.** On the app's page, under its live CSP, a test-side `page.evaluate` loads the link's `href` into `new Image()` and waits for `load`, with a `securitypolicyviolation` listener that must stay silent. The same `img-src` rule governs an `<img>` and the icon fetch (B6), so this proves the policy allows the icon in Chromium and WebKit. The existing clean-console rule then also catches a blocked icon in Chromium.
4. **Colours, Chromium.** Render `src/icon.svg` in an `<img>` on a blank test page under `page.emulate_media(color_scheme="dark")` and then `"light"` (Playwright Page docs) and read a pixel inside the path. Expect the B5 colours. In WebKit the colour scheme of SVG images is the subject of open bugs 199134 and 316640, so record WebKit's result as information only.
5. **Requests.** Option B may add a GET for `/src/icon.svg`. Whether headless Chromium or WebKit fetch the icon at all is UNVERIFIED, so allow the request and do not require it. Keep the 1.0 allowance for `/favicon.ico`, which the spec only uses when no icon link exists.
6. **People.** The tab is only visible in a headed browser, so the 1.1.0 UAT carries one case for Chrome, Firefox, Safari on macOS and Safari on iPhone, each in light and dark.

---

## Per-app notes

| Topic | Split (Danial's Splity Tab) | Streaks (Danial's Streaky Habit) |
|---|---|---|
| Ledger S4 tag | USER | ORCH, applied by analogy to Split's ruling |
| Save result today | `saveDraft` returns a boolean (`src/draft.js` line 106), ignored by `commit` and the boot reset (`src/main.js` lines 26 and 54) | `saveHabits` returns nothing (`src/storage.js` line 89). `loadHabits` folds "storage unusable" into `{ habits: [], reset: false }` (line 79) and ignores the reset save's result (line 84). Its header comment says "Storage failures never reach the user (CG-5)" |
| Getter read | Once at boot, cached in `storage` (`src/main.js` line 22). SW6 needs a re-read while it is null | Read on every call through the bare `localStorage` global, so recovery already works |
| 1.0 rules to replace | R28, R25 "A failed write is ignored (R28)", the threat row "Availability" | R18 (CG-5), threat T6, the storage contract row for `loadHabits` |
| Warning in the golden | Inventory S5 in `states.md` (the ledger calls the scope S4). In the top bar, `div.notes > div.note.is-warn[role=status]` with a 20 px amber warning icon (`#i-warning`, new to the app's icon set) and the text. A second row of the bar on a phone, centred between the brand and New bill on a desktop at 44 px. Drawn at 390 only (MANIFEST) | Inventory S4 in `states.md`. `div.banners > div.banner.warn[role=status]` with text only, between the overview band (desktop) or header (phone) and the list |
| Warning plus unreadable note | Different places (top bar and under the header), no order question | Both live in `.banners` and no golden draws them together. The plan states the order (ORCH reading, warning first, as in Split where the bar sits above the note) |
| CSP | `img-src 'self'`, `default-src 'none'` (a manifest would need `manifest-src`) | No `img-src`, `default-src 'self'` |
| Golden icon link | Has `type="image/svg+xml"` | No `type`. The plan adds it, which only helps engines skip an SVG they cannot use |
| Scan rules hit by the icon | R1 relative URLs, R39 static scan and `"://" not in index.html` | R1 relative URLs (`test_entry.py`), R25 request list |
| Header mark | `index.html` has a text wordmark only. Icons are built with `createElementNS` (CG-10). An inline `<svg>` in `index.html` without `xmlns` passes R39 | `index.html` already holds an inline sprite without `xmlns` |

---

## Recommendation for the plan

1. **Spec delta, both apps.** Replace Split R28 and Streaks R18 with SW1 to SW8, amend the rows listed in Per-app notes, and quote the approved copy exactly.
2. **Code shape.** Split passes `saveDraft`'s boolean to the view and re-reads the getter while it is null. Streaks makes `saveHabits` return a boolean and `loadHabits` report a failed read and the reset save's result. The app never inspects the exception.
3. **Markup.** As the goldens draw it, `role="status"`, no dismiss. The DOM changes only when the state flips (SW7). A live region announces most reliably when its container exists before its text changes, so the plan should say whether the container is present from boot (UNVERIFIED across screen readers, an accessibility review point).
4. **Tests.** The matrix in A3, in both engines. One faithful quota test per app. A UAT case with real blocked storage on iPhone Safari and desktop Chrome, and a note in the UAT sheet that private mode cannot show the warning.
5. **Hub contract** (for the hub project and stated in both apps' plans). Same origin and one store, keys `split.draft` and `streaks.state` reserved, no `clear()`, a prefix for hub keys, no `sandbox` on the frames, shared quota, last write wins between two live copies.
6. **Tab icon, Option B.** `src/icon.svg` equal to the decoded golden href, `<link rel="icon" type="image/svg+xml" href="src/icon.svg">` after the CSP meta, CSP unchanged in both apps. Deltas, Split R1 head order and one R39 namespace exemption with a teeth test, drop "a favicon" from the out-of-scope list. Streaks R1 head order and `/src/icon.svg` in the R25 request list. ORCH and reversible, Option A is the fallback.
7. **Never use `docs/brand/favicon.svg`** in the app. It is the 1.0 mark on a tile.
8. **Probes for the build, not run here.** P1, WebKit honours `Object.defineProperty(window, 'localStorage', ...)` in an init script. P2, the quota fill's time and result in Playwright Chromium and WebKit on this machine. P3, `python -m http.server` here serves `.svg` as `image/svg+xml`. P4, on a real Mac and iPhone with Safari 26 or later, which icon colour shows in light and in dark. P5, Firefox switches the icon colour with its theme.

## Clarify-gate items for the owner

- **CG-1, both apps. Does the warning show as soon as the app opens when the browser refuses storage outright?** Today nothing is saved until the first change, so without this the warning would first appear on the first tap or keystroke. **Recommended answer, yes.** If the browser refuses storage at load, nothing can be kept, and showing the warning at once is truthful and avoids the bar jumping in mid-typing.
- **CG-2, both apps. Private browsing and Safari's 7-day clean-up cannot trigger the warning.** In both cases every save works while the tab is open and the browser deletes the data later, which no page can detect. **Recommended answer, accept as a known limit** and say so in the README limits. For UAT, trigger the warning with Safari "Block All Cookies" on the iPhone or Chrome's "Don't allow sites to save data on your device", not with a private window.
- **CG-3, both apps. Safari keeps one tab icon colour in both themes** (WebKit bug 309949, open). The likely result is Splity Tab's navy mark close to invisible on Safari's dark tab bar, and Streaky Habit's dark amber faint there. Chrome and Firefox switch correctly. **Recommended answer, accept for 1.1.0** as Safari's bug, record it as a known limit, and check it in UAT on a Mac and an iPhone in both themes. The other option is one mid-tone colour that reads on both grounds, which is a logo change for a new round.
- **CG-4, both apps. A home-screen icon for iPhone and Android.** Not in S6. It needs an opaque square PNG (iOS paints transparency black), which conflicts with "no background, no tile", plus for Android a manifest and in Split a CSP change. **Recommended answer, keep 1.1.0 to S6 as written** (header and tab icon), look at what iOS 26 makes from the tab icon during UAT on the iPhone, and decide a home-screen icon in a later version with its own logo round for the tile.

## Sources

Project files read (absolute root `{workspace}/`)
- `examples/split/CLAUDE.md`, `examples/streaks/CLAUDE.md`, `examples/split/docs/constitution.md` (identical in both apps, compared)
- `examples/*/docs/brainstorm/brainstorm.md`, `examples/*/docs/v1.1.0/CHANGE-LEDGER.md`, `OWNER-ROADMAP.md` lines 60 to 94
- `examples/split/src/draft.js`, `examples/split/src/main.js`, `examples/split/index.html`
- `examples/streaks/src/storage.js`, `examples/streaks/src/app.js`, `examples/streaks/index.html`
- `examples/split/docs/modules/split-app/spec.md` (R1, R2, R25 to R28, R38, R39, line 374), `examples/split/docs/modules/split-app/qa.md` line 21
- `examples/streaks/docs/modules/app/spec.md` (R1, R3, R16 to R18, R24 to R26, T6, T9, T10)
- `examples/*/docs/design/states.md`, `states.html`, `MANIFEST.md`, `RULINGS-v1.1.0.md`, every golden's `<link rel="icon">` (decoded with a read-only script)
- `examples/*/docs/brand/BRAND.md` and `favicon.svg`
- `examples/split/tests/browser/test_app.py` (lines 98, 1178 to 1191, 2119 to 2200, 2231 to 2233), `examples/streaks/tests/browser/test_storage.py` (lines 173 to 209), `examples/streaks/tests/browser/test_entry.py` (R1 URL test), `examples/streaks/tests/browser/test_platform.py` (src scan)

Web, storage
- HTML spec, Web storage. https://html.spec.whatwg.org/multipage/webstorage.html
- MDN, Window.localStorage. https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage
- MDN, Storage.setItem. https://developer.mozilla.org/en-US/docs/Web/API/Storage/setItem
- MDN, Storage quotas and eviction criteria. https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria
- MDN, QuotaExceededError. https://developer.mozilla.org/en-US/docs/Web/API/QuotaExceededError
- Web IDL QuotaExceededError discussion (search summary). https://lists.w3.org/Archives/Public/public-webapps-github/2025Jan/0574.html
- Chromium, the localStorage SecurityError. https://www.chromium.org/for-testers/bug-reporting-guidelines/uncaught-securityerror-failed-to-read-the-localstorage-property-from-window-access-is-denied-for-this-document
- Google Chrome Help, on-device site data (search summary). https://support.google.com/chrome/answer/14114868
- Safari "Block all cookies" and SecurityError (secondary). https://cloud.support.dracoon.com/hc/en-us/articles/360017690740 and https://developer.apple.com/forums/thread/87778
- Firefox `dom.storage.enabled` reports (secondary, dated). https://bugzilla.mozilla.org/show_bug.cgi?id=539176
- WebKit, Updates to Storage Policy. https://webkit.org/blog/14403/updates-to-storage-policy/
- WebKit, Full Third-Party Cookie Blocking and More. https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/
- Privacy Sandbox, Storage partitioning. https://privacysandbox.google.com/cookies/storage-partitioning
- GitHub Docs, About GitHub Pages. https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages
- History of the Public Suffix List (secondary). https://jefftk.com/p/history-of-the-public-suffix-list
- Playwright, Browsers. https://playwright.dev/python/docs/browsers
- Playwright, BrowserContext.add_init_script. https://playwright.dev/python/docs/api/class-browsercontext#browser-context-add-init-script
- Playwright, Page.emulate_media. https://playwright.dev/python/docs/api/class-page#page-emulate-media

Web, icons and CSP
- caniuse, SVG favicons. https://caniuse.com/link-icon-svg
- Safari 26.0 release notes. https://developer.apple.com/documentation/safari-release-notes/safari-26-release-notes
- WebKit, News from WWDC25, Safari 26 beta. https://webkit.org/blog/16993/news-from-wwdc25-web-technology-coming-this-fall-in-safari-26-beta/
- WebKit bug 309949. https://bugs.webkit.org/show_bug.cgi?id=309949
- WebKit bug 199134. https://bugs.webkit.org/show_bug.cgi?id=199134
- WebKit bug 316640. https://bugs.webkit.org/show_bug.cgi?id=316640
- web.dev, Building an adaptive favicon. https://web.dev/articles/building/an-adaptive-favicon
- HTML spec, link type icon. https://html.spec.whatwg.org/multipage/links.html
- MDN, CSP img-src. https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/img-src
- MDN, CSP manifest-src. https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/manifest-src
- W3C, CSP Level 3. https://www.w3.org/TR/CSP3/
- WPT, img-src icon-blocked test. https://github.com/web-platform-tests/wpt/blob/master/content-security-policy/img-src/icon-blocked.sub.html and results https://wpt.fyi/api/search?label=master&label=stable&q=icon-blocked
- Mozilla bug 1262842 (CSP on SVG images ignored since Firefox 77). https://bugzilla.mozilla.org/show_bug.cgi?id=1262842
- Mozilla bug 1358106 (data or blob SVG styles under CSP, unconfirmed). https://bugzilla.mozilla.org/show_bug.cgi?id=1358106
- Apple, Configuring Web Applications (archived). https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/SafariWebContent/ConfiguringWebApplications/ConfiguringWebApplications.html
- Apple Developer Forums, transparent web clip icon turns black. https://developer.apple.com/forums/thread/713895
- realfavicongenerator, the touch icon is 180 x 180. https://realfavicongenerator.net/blog/apple-touch-icon-is-180x180-pixels-but-is-that-still-true
- web.dev, Learn PWA, Web app manifest. https://web.dev/learn/pwa/web-app-manifest
- firt.dev, home screen web apps on Android (2013). https://firt.dev/home-screen-web-apps-android/
- WebKit bug 235877, manifest icons in iOS 15.4 (search summary). https://bugs.webkit.org/show_bug.cgi?id=235877

sdlc researcher, plan phase, 2026-10-13
