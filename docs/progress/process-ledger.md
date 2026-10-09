# Process ledger

One row per process spawned under this project (constitution, Process and resource accounting).
Every row ends STOPPED and verified free, or deliberately running and named in the handoff.

| # | phase | owner | what | PID | port | started | purpose | stopped at | verified free |
|---|---|---|---|---|---|---|---|---|---|
| 1 | plan | sdlc-planner | python -m http.server (golden render and clipboard probe) | 36080 | 64991 | 2026-10-08 ~22:25 | feasibility probe | in the agent's finally block | yes, port re-bound and netstat free (agent sweep) |
| 2 | plan | sdlc-planner | python -m http.server (CSP probe) | 25348 | 26576 | 2026-10-08 ~22:25 | feasibility probe | in the agent's finally block | yes, port re-bound and netstat free (agent sweep) |
| 3 | plan | sdlc-planner | headless Chromium, 5 probe runs | not recorded | none | 2026-10-08 ~22:25 | feasibility probes | closed in script | yes, agent sweep by name and command line found none |
| 4 | plan | sdlc-planner | python -m http.server and headless Chromium (CSP and dialog harness probes, 5 servers) | 22700, 41640, 37588, 40496, one not printed | 1277, 17581, 9525, 51225, 49066 | 2026-10-08 ~22:40 | harness probes | in the agent's finally blocks | yes, ports re-bound and netstat free (agent sweep) |
| 5 | plan | sdlc-plan-checker | python -m http.server (maxlength, animation and favicon probe) and headless Chromium | 40424 | 22849 | 2026-10-08 ~22:55 | coverage-gate probe | in the agent's finally block | yes, tasklist and netstat checked (agent sweep) |
