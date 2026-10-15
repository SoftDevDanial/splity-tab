# Cold-boot live gate, v1.1.0 regression --full, 2026-10-16

Run by the QA finder (read-only), HEAD `64b882c`. `live_e2e.py` takes no output folder (`--help`: `--engine`, `--control`, `--base-url`), so every run landed in its default folder under `docs/modules/split-app/qa/live-e2e/`. This file lists them. Each folder was listed on disk after its run.

Method (CLAUDE.md, Commands). One server per engine, started by this finder with `python -m http.server <port> --bind 127.0.0.1` from the project root. Control first (`--control seeded --base-url http://127.0.0.1:<port>/`), then the same command without `--control`, then the server stopped by its exact PID and the port probed with `curl` (exit 7, connection refused).

| # | engine | run | folder (under `docs/modules/split-app/qa/live-e2e/`) | verdict | server |
|---|---|---|---|---|---|
| 1 | Chromium 149.0.7827.55 | control `seeded` | `20261016-033455-chromium-control/` | RED at step 1 on its property, as required. `pass` false, `steps_run` 1, `first_failing_step` 1, 5 assertion PASS (the stand-in and CSP listener lines among them), 10 FAIL (the cold-boot lines and `split.draft is absent`), `control_red_on_its_property` true | python PID 4760, port 7237 |
| 2 | Chromium | green, `control` null | `20261016-033459-chromium/` | PASS 9 of 9 steps, 93 assertion lines PASS, 0 FAIL, 90 requests, 0 outside the rule, 0 console errors, 0 page errors, 0 CSP violations, 3 clipboard writes, `bypass_csp` false, `storage_state` null | the same server, PID 4760, port 7237 |
| 3 | WebKit 26.5 | control `seeded` | `20261016-033526-webkit-control/` | RED at step 1 on its property, as required. Same 5 PASS and 10 FAIL lines as run 1 | python PID 20580, port 15809 |
| 4 | WebKit | green, `control` null | `20261016-033527-webkit/` | PASS 9 of 9 steps, 93 assertion lines PASS, 0 FAIL, 90 requests, 0 outside the rule, 0 console, page and CSP errors, 3 clipboard writes. `clipboard-s1.txt` and `clipboard-s2.txt` equal the Chromium run's. `steps.log` differs from the Chromium run in one line, the random Pick again draw | the same server, PID 20580, port 15809 |
| 5 | Chromium, bare (extra, for qa.md "The live gate records its engine", run with no option) | `python tests/browser/live_e2e.py`, serves itself | `20261016-033656-chromium/` | PASS 9 of 9, `control` null, `engine` chromium, `server` "served by this run", 90 requests, 0 outside the rule | its own python PID 14340, port 5461, logged STOPPED and "port free again True" by the script |

Each folder holds `summary.json`, `steps.log`, `console.log`, `network.log` and the `01-*.jpg` capture, the green ones also `02-*.jpg` to `09-*.jpg`, `clipboard-s2.txt` and `clipboard-s1.txt`. `console.log` is empty in all five. Every `network.log` line is a same-origin GET (checked by script). I viewed `20261016-033455-chromium-control/01-cold-boot.jpg` (the K2 bill, People and Charges folded, strip "Total RM 116.60"), `20261016-033459-chromium/01-cold-boot.jpg` (bill-empty, People open, strip "Enter the subtotal to see the splits.") and `20261016-033527-webkit/06-by-item.jpg` (the K1 items, "Total RM 69.26", "Summary copied").

Servers stopped. PID 4760 (port 7237) and PID 20580 (port 15809) were stopped with `Stop-Process -Id <pid> -Force`, each pid then absent from the process list, and `curl http://127.0.0.1:<port>/` gave exit 7 for both ports.

Against the step 5 baseline (`20261015-205837-chromium-control/`, `-205844-chromium/`, `-205925-webkit-control/`, `-205931-webkit/`, `-205954-chromium/`). The same figures in every field I compared (steps 9 of 9, 93 assertion lines, 90 requests, 3 writes, control RED at step 1 with 5 PASS and 10 FAIL lines).
