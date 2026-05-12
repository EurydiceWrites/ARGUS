# CURRENT — Argus

**Last updated:** 2026-05-12 (H-004 + H-004a closed; 55 manifest rows enriched; H-005 queued as next)
**Active handoff:** None — H-005 (external-taxonomy survey) is the next recommended step, pending researcher's go-ahead

---

## ACTIVE WORK — Read this section first

**Where we are:** Phase 3 preparation continues under the **Path B sequenced-hybrid strategy**. H-004 + H-004a closed — the manifest now carries deterministic filename-derived metadata for **55 of 157 items** (41 DOW + 2 DOS + 12 NASA), four new columns appended (`country`, `date`, `date_precision`, `item_type`) joined to the pre-existing `agency` column updated in place. **0** unparsed DOW/DOS/NASA-like filenames remain. Three design-preserving blanks (D48 + D49 country, D54 date) documented in the H-004a closure.

The methodological foundation from H-004 stands:

- **File** = unit of ingest and provenance. 1:1 with manifest rows.
- **Incident** = unit of classification. A real-world UAP event. One file may document 0, 1, or N incidents; one incident may be documented by 1 or N files.
- **Scene** = deferred to Phase 5+ as optional refinement.

The Phase 4 schema will be **two-tier**: `files` and `incidents` joined by `file_incidents`, with `taxonomy_codes` joined to incidents via `incident_codes`. Two many-to-many joins, not one. The Mack-Bullard analog of *case ↔ motif* in Argus is **incident ↔ code**, not file ↔ code. Files don't get classified directly; incidents do.

**Three documented blanks** in the enriched manifest, all design-preserving rather than gaps:

1. **D48 and D49** — both have blank `country` (source filename omits the location token between item_type and date). Resolved in H-004a by relaxing the parser to allow blank `country` for known DOW item_types with parseable dates. `date`, `date_precision`, and `item_type` are populated.

2. **D54 literal-`NA` date sentinel** — `DOW-UAP-D54-Mission-Report-Mediterranean-Sea-NA.pdf` has blank `date` and `date_precision` by design (the source filename's date position is the literal token `NA`; defaulting would fabricate provenance). Downstream consumers must respect the `date_precision` column when reading dates.

3. **All NASA `country`** — NASA filenames don't encode country (`mission` is captured but `country` stays blank by design per H-004 Step 4).

**Phase status:** Phase 0 ✓. Phase 1 ✓. Phase 2 ✓. Phase 3 prep partial (unit decision settled; H-004 + H-004a closed; H-005 still owed). Phase 3 design (taxonomy itself) gated by H-005 (external-taxonomy survey, to run in Eurydice chat) and the Phase 3 reading-as-cases pass.

**Concrete resume path:**

1. **H-005 — External-taxonomy survey** (next). Hynek / Vallée / AARO / GEIPAN / SCU, in Eurydice chat. Output: `notebooks/existing_taxonomies.md`. Desk research, not script work — shapes the vocabulary Phase 3 design will draw from. **This is the recommended next step.**
2. **Phase 3 — Taxonomy design.** Once H-005 produces the external-taxonomy reference, read the clean 55 DOW/DOS/NASA cases (using the filename-derived metadata as the index), extract incidents, observe patterns, draft taxonomy v1 grounded in the actual archive.
3. **Phase 4 — Schema.** Implement the two-tier model in SQLite.
4. **Phase 5 v1 — Index and classify the clean subset.** End of Path B v1.
5. **Later (post-v1):** war.gov page parse (refines `source_url`); FBI case-file extraction with LLM assistance + researcher review; DOD video segmentation. Taxonomy versions to v2 and beyond as messier data lands.

**Do not jump ahead** to taxonomy design (Phase 3) or schema (Phase 4) until H-005 produces the external-taxonomy reference.

---

## Working protocol (mandatory)

The **Goal Grounding Protocol** is active for this project. Before any non-trivial work, state (1) immediate goal, (2) underlying purpose, (3) success criterion, then wait for user confirmation. See [CLAUDE.md](CLAUDE.md).

**Session-close discipline:** Closing a handoff means updating CURRENT.md (this file), `handoffs/_index.md`, and committing all three (the new handoff doc + both updates) in a single commit. See [docs/WORKFLOW_PROTOCOL.md](docs/WORKFLOW_PROTOCOL.md) Rule 1.

---

## Recent handoffs (most recent first — full list at [handoffs/_index.md](handoffs/_index.md))

| ID | Date | Status | Summary |
|---|---|---|---|
| [H-004a](handoffs/H-004a_blank_country.md) | 2026-05-12 | Closed — Parser relaxed to accept blank `country` for known DOW item_types with parseable dates. D48 + D49 now enriched. **0** unparsed DOW/DOS/NASA-like filenames remain; 55 of 157 rows enriched in total. |
| [H-004](handoffs/H-004_filename_extractor.md) | 2026-05-12 | Closed — Filename metadata extractor. 39 DOW + 2 DOS + 12 NASA rows enriched with `country`, `date`, `date_precision`, `item_type`. 24 unit tests pass. Idempotency byte-identical. 2 candidates surfaced for future refinement (D48, D49 lack filename location) — addressed in H-004a. 0 agency disagreements. |
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
