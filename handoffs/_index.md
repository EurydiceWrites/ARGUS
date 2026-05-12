# Handoffs Index

**Newest first. The active handoff is at the top.** Each row links to the full handoff doc and gives a one-line summary so an agent or human can scan the chronology in 30 seconds.

This index is required reading at session start (per [CLAUDE.md](../CLAUDE.md)) and required maintenance at session close (per [docs/WORKFLOW_PROTOCOL.md](../docs/WORKFLOW_PROTOCOL.md) Rule 1).

---

## Active

| ID | Date | One-line summary |
|---|---|---|
| *(none — H-001 closed; next handoff opens with Phase 1 archiver)* | | |

## Closed

| ID | Date | One-line summary |
|---|---|---|
| [H-001](H-001_project_scaffold.md) | 2026-05-12 | Project scaffold. README, CLAUDE.md, CURRENT.md, PROJECT_OVERVIEW.md, FUTURE_WORK.md, WORKFLOW_PROTOCOL.md, NOMENCLATURE.md, handoffs/_index.md, H-001 itself. Directory structure (src/taxonomy/db/notebooks/docs/handoffs/) created. Data folder split into video/images/text buckets, gitignored. Working protocol imported from Anomaly Taxonomy and adapted for media-archival domain. |

---

## Maintenance rules

Per [docs/WORKFLOW_PROTOCOL.md](../docs/WORKFLOW_PROTOCOL.md) Rule 1:

- Every handoff closure adds a row to this index. The new row goes at the **top** (under the appropriate section).
- When a handoff transitions from Active to Closed, move its row from the Active table to the top of the Closed table.
- The closing commit must include both this index update and the corresponding `CURRENT.md` update.

If a session reads this index and finds a row that contradicts `CURRENT.md`, this index is the source of truth — `CURRENT.md` is stale and must be reconciled before further work.
