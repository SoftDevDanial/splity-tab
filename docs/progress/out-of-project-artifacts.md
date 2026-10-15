# Out-of-project artifacts

Stray files that an agent or the orchestrator created or found outside the project root. Agents log, the owner reviews and deletes each one by hand. Nothing here is deleted by an agent.

| Path | Size | Created | By | Why it landed outside | Status |
|---|---|---|---|---|---|
| `{temp}\ref_a13` | 0 bytes | 2026-10-15 14:13 | the orchestrator (fifth session), a `touch` slip recorded in `STATE-LOG.md` 2026-10-15 14:29 | a `touch` run in the shell's temp folder, details in `STATE-LOG.md` 2026-10-15 14:29 | still present at the review 2026-10-16 05:00 (found by the stakeholder reviewer, ledger S7 row 54). Needs the owner's review and manual deletion |
