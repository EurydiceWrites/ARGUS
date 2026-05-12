# FUTURE_WORK — Argus

**Last updated:** 2026-05-12

The phase-by-phase build plan for Argus, plus the open questions each phase needs to answer before it can close.

The phase order is fixed. Don't skip phases. See [CLAUDE.md](CLAUDE.md) build-order discipline.

---

## Phase 1 — Archive

**Goal:** Systematically download and preserve everything currently at war.gov/UFO, in a way that re-runs cleanly when new tranches drop.

### Steps

1. **Inventory what's currently in `data/raw/` from manual downloads.** Count files per media-type bucket, size, formats, naming patterns. Establishes baseline.
2. **Fetch and inspect war.gov/UFO.** Understand the URL structure, file types hosted, how tranches are organized, whether there's a manifest or just HTML.
3. **Design the archiver.** Re-runnable, idempotent, tracks tranches. Records provenance (source URL, agency, tranche date, retrieval date, file hash) per item.
4. **Run the archiver on Tranche 1 (May 8, 2026 release).** Verify completeness against the war.gov page.
5. **Build the manifest.** First version of the archive's index — what's archived, when, where it came from. Likely a CSV or JSON-Lines file initially; promoted to the database in Phase 4.

### Open questions

- Is there a machine-readable manifest at war.gov/UFO, or must structure be inferred from HTML?
- Are individual files identified by stable URLs across re-runs, or do they get re-uploaded with new IDs?
- Do we need to mirror the war.gov organizational structure (by agency, by date, etc.) or impose our own?
- Should we capture screenshots of the war.gov pages themselves as part of the provenance record, in case the page changes between tranches?

### Acceptance criteria

- Re-running the archiver does not re-download files already on disk (idempotent).
- Every file in `data/raw/` has a manifest row with its provenance.
- File hashes match war.gov source on first download.

---

## Phase 2 — Survey

**Goal:** Examine what's actually in the archive before designing anything.

### Steps

1. **Catalog by material type.** Counts of video, image, document, transcript, sensor data, other.
2. **Note metadata the government provides.** Filename conventions, captions, accompanying text, agency tags.
3. **Note metadata the government does NOT provide.** Missing dates, missing locations, missing camera info, missing context.
4. **Document first impressions, patterns, and questions.** This is the researcher looking at the data before designing the taxonomy. Notes go in `notebooks/survey_phase2.md`.
5. **Survey existing UAP classification systems** for comparison: Hynek (CE1-3, nocturnal lights, daylight discs), Vallée (Type I-V), AARO's categorical scheme, GEIPAN's system, SCU's case methodology. Notes go in `notebooks/existing_taxonomies.md`.

### Open questions

- Are video and image material classifiable on the same dimensions, or do they need separate tracks?
- Are documents and transcripts a separate analytical layer (context for visual items) or a primary classification target?
- What metadata gaps would change Phase 3 categories if filled?

### Acceptance criteria

- Researcher has examined every distinct file type at least once.
- Existing-taxonomies notes summarize what other systems classify on and what they ignore.
- A list of candidate classification dimensions exists, even if provisional.

---

## Phase 3 — Design the taxonomy

**Goal:** Build the classification system from observed patterns. This is the intellectual core of the project.

### Possible dimensions (starting questions, not pre-committed)

- **Morphology** — shape, size, structure of observed phenomena
- **Behavior** — movement patterns, interactions, state changes
- **Environment** — setting, conditions, context of observation
- **Sensor type** — what captured this (FLIR, optical, radar, eyewitness photograph, declassified document scan)
- **Provenance** — originating agency, classification level prior to release, date range
- **Confidence / quality** — resolution, clarity, completeness of the record

### Steps

1. **Write the pre-registration.** What dimensions do we expect to matter, based on Phase 2's survey? What would falsify each? What have we been exposed to that might bias us?
2. **Draft v1 of the taxonomy.** Per-dimension category lists with operational definitions.
3. **Apply v1 to a small sample (10–20 items per media type)** and see what breaks. Categories that can't be applied consistently get sharpened or dropped.
4. **Iterate until inter-rater reliability is acceptable** (researcher classifies twice on the same sample, separated by time; agreement above a defined threshold).
5. **Freeze v1.** Versioned because the taxonomy will evolve.

### Open questions

- Do video, image, and document share one taxonomy or three?
- Is sensor-type a primary dimension or metadata?
- How do we handle items that depict multiple phenomena (e.g., a single video showing two distinct objects)?

### Acceptance criteria

- A `taxonomy/taxonomy_v1.md` document on disk with all dimensions, categories, operational definitions, and worked examples.
- Pre-registration on disk and predates the freeze.
- Researcher inter-rater agreement on the sample meets the threshold.

---

## Phase 4 — Schema

**Goal:** SQLite database designed around the Phase 3 taxonomy. Stores classifications with full provenance.

### Steps

1. **Translate taxonomy v1 into a normalized schema.** Items, classifications, dimensions, categories, sources, tranches.
2. **Write the DDL.** `db/schema.sql`.
3. **Build the loader.** Ingests the Phase 1 manifest and creates Item rows. Classifications populated separately (Phase 5).
4. **Build the migration discipline.** Version the schema; every change is a migration script with up/down logic.

### Open questions

- Are classifications versioned (so v2 of the taxonomy can re-classify without overwriting v1)?
- How do we handle multi-classification (an item that fits two categories on the same dimension)?
- Are confidence scores stored per classification or implied?

### Acceptance criteria

- `db/schema.sql` reproducibly builds an empty Argus database.
- Manifest from Phase 1 loads cleanly with no foreign-key violations.

---

## Phase 5 — Index and classify

**Goal:** Apply the taxonomy to the archived items. Build the color-coded visualization layer for analysis.

### Steps

1. **Classify every archived item.** Researcher-led; AI assists with first-pass suggestions but never makes final decisions.
2. **Build the color-coded visualization.** Source material is monochrome; the analytical layer should be visually rich. The researcher is color-dominant — make the dashboard make sense to her.
3. **Run negative controls.** Apply the apparatus to non-UAP material (conventional aviation, civilian aerial, declassified non-UAP). Verify the taxonomy discriminates.
4. **Cross-corpus analysis (eventual).** Once enough is classified, look for patterns: which morphologies cluster with which sensors? Which behaviors appear across agencies?
5. **Iterate as new tranches arrive.** The pipeline is re-runnable; the taxonomy may need v2 if new material breaks v1.

### Open questions

- When does taxonomy v1 get promoted to v2? What's the threshold?
- How do we surface "this item doesn't fit anywhere" without forcing a category?
- What does the cross-corpus analysis layer look like when partial datasets are still being classified?

### Acceptance criteria

- All Tranche-1 items classified at least at the dimension where the apparatus is confident.
- Negative controls do not produce false-positive classifications above a defined rate.
- Visualization is in use by the researcher for analytical work.

---

## Carry-forward open questions (cross-phase)

These don't belong to a single phase but need answers somewhere:

1. **Update cadence.** How automated should the daily / weekly / per-tranche re-run be? Cron? Manual? Triggered by a war.gov page change?
2. **Cross-project link.** When (if ever) do we cross-reference Argus classifications with Anomaly Taxonomy episode patterns? Separate handoff when the time comes.
3. **Public output.** Is any of this published? In what form? (Default: private research repo; no commitment to publish until Phase 5 stabilizes.)
4. **Storage scale.** PURSUE Tranche 1 is manageable on a single workstation. What's the storage / compute strategy when Tranche 6 brings a terabyte of declassified satellite imagery? Plan before it happens.

---

## Existing literature to survey (Phase 2 work)

- **Hynek, J. Allen.** *The UFO Experience: A Scientific Inquiry* (1972) — CE1/CE2/CE3 classification system.
- **Vallée, Jacques.** Classification system (Type I–V, subtypes).
- **AARO reports** (2024 debut report, subsequent releases).
- **GEIPAN (France)** — French government UAP classification system.
- **SCU (Scientific Coalition for UAP Studies)** — peer-reviewed case analyses with systematic methodology.

Nobody has done for UAP visual data what Bullard did for abduction narratives — a systematic, granular, code-level taxonomy. That's the gap this project fills.
