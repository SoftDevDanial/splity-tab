# Finalize, Splity Tab v1.1.0

**Date.** 2026-10-13 · **Approved by.** the owner, 2026-10-11 23:45 (`../RULINGS.md`, Finalize gate)

## What moved
`../final/` was copied into `docs/design/` by `finalize_copy.py`. 34 files, the fifteen goldens with their `.md`, `system.css`, `system.md`, `LINKS.json` and `MANIFEST.md`. 20 are new and 14 replace 1.0's goldens, which stay in tag `v1.0.0`. Every copy has the SHA-256 of its source. `../RULINGS.md` sits beside 1.0's rulings as `docs/design/RULINGS-v1.1.0.md`, as 1.0's finalize copied its rulings.

`../final/checks/` and `../final/SELF-CRITIQUE.md` stay here. The checks reach `round-2/g2.html` and `logo/round-2/s12.html`, so they only run from the explore folder.

## The checks from the new place
`rehome_checks.py` copies `../final/checks/*.py` to a scratch folder with the golden folder set to `docs/design/` and every `round-2/` and `logo/` lookup kept on this folder. Then `check_final.py` ran from there.

| Run | Asserts | Results |
|---|---|---|
| `../final/checks/results.json` (2026-10-11) | 748 of 748 | |
| `check-results.json` (2026-10-13, goldens read from `docs/design/`) | 747 of 748 | pages, static, contrast, tokens, clipboard, the 48 links, console, page errors and network all equal to the 2026-10-11 run |

The one fail is not a golden. The markdown lint globs every `.md` in its folder. In `final/` that took in `SELF-CRITIQUE.md`, in `docs/design/` it takes in 1.0's `RULINGS.md` instead (there since 2026-10-08, in tag `v1.0.0`), whose header has prose colons (`**Date:**`). That sealed record is left as it is. `RULINGS-v1.1.0.md` was copied in after this run globbed the folder. Its only colons are clock times.

## Run again
```
python -B finalize_copy.py <app root> --dry
python -B rehome_checks.py <app root> <scratch folder>
python -B <scratch folder>/check_final.py
```
