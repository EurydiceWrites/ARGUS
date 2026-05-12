# CURRENT — Argus

**Last updated:** 2026-05-12 (H-002 opened; Phase 1 archiver in progress)
**Active handoff:** [handoffs/H-002_phase1_archiver.md](handoffs/H-002_phase1_archiver.md)

---

## ACTIVE WORK — Read this section first

**Where we are:** Phase 0 scaffold closed. Tranche 1 of the PURSUE release (war.gov 2026-05-08) is on disk as two ZIPs in `data/raw/`: `Release_1.zip` (2.49 GB, 261 entries — 230 PDFs + 28 images + Mac junk) and `uapvideos.zip` (1.33 GB, 28 MP4s). H-002 is the archiver that extracts these to media buckets, hashes everything, and writes a tracked manifest at `data/manifest.csv`.

**Phase status:** Phase 1 (archive) in progress.

**Concrete resume path:**

1. H-002 is mid-execution. Goal grounding confirmed; handoff doc committed; archiver code to be written next.
2. Run `src/phase1_archive.py` against `data/raw/Release_1.zip` and `data/raw/uapvideos.zip`.
3. Verify against H-002 acceptance criteria. Re-run for idempotency check.
4. Close H-002 with report-back per Rule 5.

**Do not jump ahead** to taxonomy design (Phase 3) or schema (Phase 4). The build order is sacred — see `CLAUDE.md` and `FUTURE_WORK.md`.

---

## Working protocol (mandatory)

The **Goal Grounding Protocol** is active for this project. Before any non-trivial work, state (1) immediate goal, (2) underlying purpose, (3) success criterion, then wait for user confirmation. See [CLAUDE.md](CLAUDE.md).

**Session-close discipline:** Closing a handoff means updating CURRENT.md (this file), `handoffs/_index.md`, and committing all three (the new handoff doc + both updates) in a single commit. See [docs/WORKFLOW_PROTOCOL.md](docs/WORKFLOW_PROTOCOL.md) Rule 1.

---

## Recent handoffs (most recent first — full list at [handoffs/_index.md](handoffs/_index.md))

| ID | Date | Status | Summary |
|---|---|---|---|
| **[H-002](handoffs/H-002_phase1_archiver.md)** | **2026-05-12** | **Active — Phase 1 archiver. Extract Release_1.zip + uapvideos.zip, route to media buckets, SHA-256 each item, write tracked manifest at data/manifest.csv. Idempotent.** |
| [H-001](handoffs/H-001_project_scaffold.md) | 2026-05-12 | Closed — Project scaffold built. README, CLAUDE.md, CURRENT.md, PROJECT_OVERVIEW.md, FUTURE_WORK.md, WORKFLOW_PROTOCOL.md, NOMENCLATURE.md, handoffs/_index.md, H-001 itself. Directory structure (src/taxonomy/db/notebooks/docs/handoffs/) created. Data folder split into video/images/text buckets, gitignored. |

---

## Where to find more

| If you want... | Read this |
|---|---|
| The big-picture project framing | [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) |
| The phase-by-phase build plan | [FUTURE_WORK.md](FUTURE_WORK.md) |
| Standing operational rules | [docs/WORKFLOW_PROTOCOL.md](docs/WORKFLOW_PROTOCOL.md) |
| Vocabulary (tranche, item, manifest, etc.) | [docs/NOMENCLATURE.md](docs/NOMENCLATURE.md) |
| Working protocol for Claude sessions | [CLAUDE.md](CLAUDE.md) |
| Newest-first index of all handoffs | [handoffs/_index.md](handoffs/_index.md) |
