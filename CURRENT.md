# CURRENT — Argus

**Last updated:** 2026-05-12 (H-003 closed; Phase 2 technical survey complete)
**Active handoff:** none — Phase 2 technical survey done; choose H-004 (external-taxonomy survey) or H-005 (war.gov page parse) next

---

## ACTIVE WORK — Read this section first

**Where we are:** Phase 2 (technical survey) is complete. The manifest carries per-item metadata for all 157 Tranche 1 items: PDF page counts, image dimensions, video duration/resolution. Filename-pattern analysis surfaced a major finding — **DOW (Dept. of War), DOS (Dept. of State), and NASA filenames natively encode date + location + item-type** for ~80 of the 115 PDFs. The first-pass archiver only caught the 28 `DOD_` videos; the rest of the agency tagging was hidden in plain sight. FBI case files and DOD videos carry no such encoding — only IDs.

Full survey notes at `notebooks/survey_phase2.md`. Distributions, clusters, observations, open questions for the researcher.

**Phase status:** Phase 0 ✓. Phase 1 ✓. Phase 2 ✓ (technical only — external-literature survey deferred). Phase 3 (taxonomy design) requires the open questions resolved first.

**Concrete resume path (multiple paths, pick one):**

1. **H-004 — External-taxonomy survey.** Hynek, Vallée, AARO, GEIPAN, SCU. Compare what other systems classify on. Output: `notebooks/existing_taxonomies.md`.
2. **H-005 — War.gov page parse.** Fetch and parse `https://www.war.gov/ufo/pursue-initiative/` for source-page metadata (captions, agency attribution, direct download URLs). Refines `source_url` in the manifest and surfaces metadata not present in filenames.
3. **H-006 — Filename-metadata extractor.** Lightweight script that regexes DOW / DOS / NASA filename patterns into structured columns on the manifest (agency, country, date, item_type). Quick win that immediately enriches ~80 PDFs.

The open question raised in the H-003 close — *"What's the right unit of classification: file, incident, or scene?"* — should be settled before Phase 3 starts.

**Do not jump ahead** to taxonomy design (Phase 3) or schema (Phase 4) until the open question is settled.

---

## Working protocol (mandatory)

The **Goal Grounding Protocol** is active for this project. Before any non-trivial work, state (1) immediate goal, (2) underlying purpose, (3) success criterion, then wait for user confirmation. See [CLAUDE.md](CLAUDE.md).

**Session-close discipline:** Closing a handoff means updating CURRENT.md (this file), `handoffs/_index.md`, and committing all three (the new handoff doc + both updates) in a single commit. See [docs/WORKFLOW_PROTOCOL.md](docs/WORKFLOW_PROTOCOL.md) Rule 1.

---

## Recent handoffs (most recent first — full list at [handoffs/_index.md](handoffs/_index.md))

| ID | Date | Status | Summary |
|---|---|---|---|
| **[H-003](handoffs/H-003_phase2_survey.md)** | **2026-05-12** | **Closed — Phase 2 technical survey. Manifest enriched (page counts / dimensions / durations) for all 157 items. Filename analysis revealed 6+ agency conventions; ~80 PDFs have machine-extractable date+location+item-type from filenames.** |
| [H-002](handoffs/H-002_phase1_archiver.md) | 2026-05-12 | Closed — Phase 1 archiver. 157 items archived from Tranche 1 (115 PDFs + 14 images + 28 videos). Idempotent. Manifest at `data/manifest.csv`. |
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
