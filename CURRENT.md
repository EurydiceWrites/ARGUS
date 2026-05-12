# CURRENT — Argus

**Last updated:** 2026-05-12 (H-002 closed; Phase 1 complete; Phase 2 next)
**Active handoff:** none — next opens with Phase 2 (survey)

---

## ACTIVE WORK — Read this section first

**Where we are:** Phase 1 (archive) is complete. Tranche 1 fully archived to media buckets with SHA-256 provenance per item in `data/manifest.csv` (157 rows: 115 PDFs + 14 images + 28 videos). Archiver script (`src/phase1_archive.py` v1.0.0) is idempotent. Pre-extraction inventory counts were inflated by `__MACOSX` Mac metadata; real Tranche 1 is 157 items, not the 287 originally estimated.

**Phase status:** Phase 0 (scaffold) ✓. Phase 1 (archive) ✓. Phase 2 (survey) not yet started.

**Concrete resume path:**

1. Open **H-003** for Phase 2 (survey). Apply Goal Grounding Protocol.
2. Inventory the archive in detail: file size distribution, PDF page-counts, image dimensions, video durations, filename patterns.
3. Note what metadata war.gov provides vs. what is absent.
4. Survey existing UAP classification systems for comparison (Hynek, Vallée, AARO, GEIPAN, SCU). Notes go in `notebooks/`.
5. **Do not** start Phase 3 (taxonomy design) until survey is complete and reviewed.

**Open items carrying forward:**

- `source_url` for every manifest row is currently the PURSUE page URL, not the direct download URL. Refine in a later handoff once we fetch and parse the war.gov page.
- Agency derivation is filename-prefix only (catches `DOD_*` videos). Most PDFs/images currently `agency=unknown`. Refinement when we have time to map filename conventions to agencies.

**Do not jump ahead** to taxonomy design (Phase 3) or schema (Phase 4). The build order is sacred — see `CLAUDE.md` and `FUTURE_WORK.md`.

---

## Working protocol (mandatory)

The **Goal Grounding Protocol** is active for this project. Before any non-trivial work, state (1) immediate goal, (2) underlying purpose, (3) success criterion, then wait for user confirmation. See [CLAUDE.md](CLAUDE.md).

**Session-close discipline:** Closing a handoff means updating CURRENT.md (this file), `handoffs/_index.md`, and committing all three (the new handoff doc + both updates) in a single commit. See [docs/WORKFLOW_PROTOCOL.md](docs/WORKFLOW_PROTOCOL.md) Rule 1.

---

## Recent handoffs (most recent first — full list at [handoffs/_index.md](handoffs/_index.md))

| ID | Date | Status | Summary |
|---|---|---|---|
| **[H-002](handoffs/H-002_phase1_archiver.md)** | **2026-05-12** | **Closed — Phase 1 archiver. `src/phase1_archive.py` v1.0.0. 157 items archived from Tranche 1 (115 PDFs + 14 images + 28 videos). Idempotent. Manifest at `data/manifest.csv`.** |
| [H-001](handoffs/H-001_project_scaffold.md) | 2026-05-12 | Closed — Project scaffold built. |

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
