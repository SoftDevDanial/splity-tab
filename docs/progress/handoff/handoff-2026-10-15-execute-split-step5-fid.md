# Handoff. Split v1.1.0 execute, step 5, fidelity finder (read-only)

Written 2026-10-15 by the fidelity finder (read-only) at about 42 percent of its context, as its brief asks. The work the brief names is done. One optional extra is not done.

## Where it stands
- Verdict written to `docs/modules/split-app/findings/fidelity.md`. Status one-to-one, 0 findings, 9 observations. HEAD `82e2285`, code as `d58f4ce`.
- Pixel half of R40 read back from A19's own files (`docs/modules/split-app/qa/fidelity/20261015-193738/`). Both controls as written, 40 of 40 pairs at 0 mismatching pixels with equal sizes, scripts per pair as qa.md's table, 38 of 42 PNG pairs byte-identical. Not re-run, nothing in it is inconsistent.
- Checklist half run on the running app in Chromium 149. Every qa.md checklist row at every width, the ST rows, focus and motion by real gestures. 715 row and width checks plus 38 gesture rows, all pass except K1-44 at 1280 and W1-02, where the golden itself shows 16 px and 410 px (observations O-1 and O-2, wording for the planner).
- The three sub-threshold pairs and QA-S5-4 are judged as recorded engine differences with measurements (raster paint history for `bill-unreadable-390x844`, top layer against the stand-in for both `new-bill-dialog` pairs, WebKit's glass and `:focus-visible` for QA-S5-4, each shown by an in-memory experiment on the golden page).

## Not done
- The element-by-element compare of the 40 states in WebKit. It is no gate (R40 and the checklist are Chromium only, ledger S5 row 2). The script would be the scratchpad's `run_pairs.py webkit` and `run_inventory.py webkit` into a new dated folder, if the orchestrator wants it.

## For the orchestrator
- Planner wording points from the verdict, O-1, O-2, O-4 and O-5. No app change is wanted for any of them, the app equals the golden.
- One measured fact for a possible owner decision at UAT (QA-S5-4). In WebKit 26.5 a script focus after a mouse click draws the ring (Splits after the sheet closes, Cancel after New bill opens), and the golden's own autofocus does the same. `focus({ focusVisible: false })` suppresses it in WebKit 26.5. Changing it would be a spec change under R59, not a fidelity fix.

## Evidence
`docs/modules/split-app/qa/fidelity-checklist/20261015-225153/`, listed in the verdict's Evidence section. Scripts in the session scratchpad, `split-fid-step5/`, outside the project.

## Processes
None of mine alive. Every script started its own `python -m http.server` through `tests/browser/rig.py` and stopped it in a `finally` block, each logged STOPPED with "port free again True". Ports 13288, 10358, 56130, 58272, 19948, 37019, 12888 and 39457 refused a connection at the end. A sweep by command line (`split-fid-step5`, `http.server`, `playwright`, WebKit) found only another agent's `rs9a_memory.py webkit` job (PID 15168 with its server on port 15231) and its shells, left alone.
