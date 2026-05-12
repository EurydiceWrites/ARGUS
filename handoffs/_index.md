# Handoffs Index

**Newest first. The active handoff is at the top.** Each row links to the full handoff doc and gives a one-line summary so an agent or human can scan the chronology in 30 seconds.

This index is required reading at session start (per [CLAUDE.md](../CLAUDE.md)) and required maintenance at session close (per [docs/WORKFLOW_PROTOCOL.md](../docs/WORKFLOW_PROTOCOL.md) Rule 1).

---

## Active

| ID | Date | One-line summary |
|---|---|---|
| **[H-003](H-003_phase2_survey.md)** | **2026-05-12** | **Phase 2 technical survey. Enrich data/manifest.csv with per-item metadata (PDF page counts, image dimensions, video duration/resolution). Analyze filename patterns. Write structured survey notes to notebooks/survey_phase2.md. No taxonomy design. External-literature survey deferred to H-004.** |

## Closed

| ID | Date | One-line summary |
|---|---|---|
| [H-002](H-002_phase1_archiver.md) | 2026-05-12 | Phase 1 archiver. `src/phase1_archive.py` v1.0.0 extracts Release_1.zip + uapvideos.zip, routes to video/images/text buckets, SHA-256s each item, writes tracked manifest at `data/manifest.csv`. Idempotent (idempotency bug in manual-catalog pass caught and fixed during close). Final Tranche_1 inventory: **157 items** (115 PDFs + 14 images + 28 videos). Pre-extraction count was inflated by __MACOSX AppleDouble mirrors; real release is much smaller. Manually-downloaded PDF subsumed into Tranche_1 (byte-identical to a ZIP entry). |
| [H-001](H-001_project_scaffold.md) | 2026-05-12 | Project scaffold. README, CLAUDE.md, CURRENT.md, PROJECT_OVERVIEW.md, FUTURE_WORK.md, WORKFLOW_PROTOCOL.md, NOMENCLATURE.md, handoffs/_index.md, H-001 itself. Directory structure (src/taxonomy/db/notebooks/docs/handoffs/) created. Data folder split into video/images/text buckets, gitignored. Working protocol imported from Anomaly Taxonomy and adapted for media-archival domain. |

---

## Maintenance rules

Per [docs/WORKFLOW_PROTOCOL.md](../docs/WORKFLOW_PROTOCOL.md) Rule 1:

- Every handoff closure adds a row to this index. The new row goes at the **top** (under the appropriate section).
- When a handoff transitions from Active to Closed, move its row from the Active table to the top of the Closed table.
- The closing commit must include both this index update and the corresponding `CURRENT.md` update.

If a session reads this index and finds a row that contradicts `CURRENT.md`, this index is the source of truth — `CURRENT.md` is stale and must be reconciled before further work.
