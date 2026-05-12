# CURRENT — Argus

**Last updated:** 2026-05-12 (H-004 opened; Phase 3 unit-of-classification question settled; Path B committed)
**Active handoff:** H-004 — Filename Metadata Extractor (open; Claude Code to execute)

---

## ACTIVE WORK — Read this section first

**Where we are:** Phase 3 preparation has begun under the **Path B sequenced-hybrid strategy**. The open question from H-003 close — *"What's the right unit of classification: file, incident, or scene?"* — is **settled**:

- **File** = unit of ingest and provenance. 1:1 with manifest rows.
- **Incident** = unit of classification. A real-world UAP event. One file may document 0, 1, or N incidents; one incident may be documented by 1 or N files.
- **Scene** = deferred to Phase 5+ as optional refinement.

The Phase 4 schema will be **two-tier**: `files` and `incidents` joined by `file_incidents`, with `taxonomy_codes` joined to incidents via `incident_codes`. Two many-to-many joins, not one. The Mack-Bullard analog of *case ↔ motif* in Argus is **incident ↔ code**, not file ↔ code. Files don't get classified directly; incidents do.

H-004 (filename metadata extractor) is open and waiting on Claude Code to execute. It parses the DOW, DOS, and NASA filename conventions surfaced in H-003 into five new manifest columns (`agency`, `country`, `date`, `date_precision`, `item_type`), enriching ~55 PDFs + ~12 NASA images deterministically without opening any file. FBI case files and DOD videos remain out of scope until later sub-phases that authorize LLM-assisted content extraction.

**Phase status:** Phase 0 ✓. Phase 1 ✓. Phase 2 ✓. Phase 3 prep in progress (unit decision settled; H-004 active). Phase 3 design (taxonomy itself) still gated by H-005 (external-taxonomy survey, to run in Eurydice chat in parallel with H-004) and the Phase 3 reading-as-cases pass.

**Concrete resume path:**

1. **H-004 — Filename metadata extractor.** Claude Code executes per the handoff spec at `handoffs/H-004_filename_extractor.md`. Closes per session-close checklist (Rule 1).
2. **H-005 — External-taxonomy survey** (parallel). Hynek / Vallée / AARO / GEIPAN / SCU, in Eurydice chat. Output: `notebooks/existing_taxonomies.md`. Desk research, not script work — shapes the vocabulary Phase 3 design will draw from.
3. **Phase 3 — Taxonomy design.** Once H-004 and H-005 close, read the clean ~55 DOW/DOS/NASA cases, extract incidents, observe patterns, draft taxonomy v1 grounded in the actual archive.
4. **Phase 4 — Schema.** Implement the two-tier model in SQLite.
5. **Phase 5 v1 — Index and classify the clean subset.** End of Path B v1.
6. **Later (post-v1):** war.gov page parse (refines `source_url`); FBI case-file extraction with LLM assistance + researcher review; DOD video segmentation. Taxonomy versions to v2 and beyond as messier data lands.

**Do not jump ahead** to taxonomy design (Phase 3) or schema (Phase 4) until H-004 closes and H-005 produces the external-taxonomy reference.

---

## Working protocol (mandatory)

The **Goal Grounding Protocol** is active for this project. Before any non-trivial work, state (1) immediate goal, (2) underlying purpose, (3) success criterion, then wait for user confirmation. See [CLAUDE.md](CLAUDE.md).

**Session-close discipline:** Closing a handoff means updating CURRENT.md (this file), `handoffs/_index.md`, and committing all three (the new handoff doc + both updates) in a single commit. See [docs/WORKFLOW_PROTOCOL.md](docs/WORKFLOW_PROTOCOL.md) Rule 1.

---

## Recent handoffs (most recent first — full list at [handoffs/_index.md](handoffs/_index.md))

| ID | Date | Status | Summary |
|---|---|---|---|
| **[H-004](handoffs/H-004_filename_extractor.md)** | **2026-05-12** | **Open — Filename metadata extractor. Parses DOW/DOS/NASA filename conventions into five new manifest columns (`agency`, `country`, `date`, `date_precision`, `item_type`). Path B v1 preparation. Claude Code to execute.** |
| [H-003](handoffs/H-003_phase2_survey.md) | 2026-05-12 | Closed — Phase 2 technical survey. Manifest enriched (page counts / dimensions / durations) for all 157 items. Filename analysis revealed 6+ agency conventions; ~80 PDFs have machine-extractable date+location+item-type from filenames. |
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
