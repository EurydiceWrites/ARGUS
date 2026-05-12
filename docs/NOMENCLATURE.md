# NOMENCLATURE — Argus

Project-specific vocabulary. Use these terms consistently across handoffs, code, schema, and documentation. Adding a new term requires a handoff entry; redefining an existing term requires Eurydice approval.

**Last updated:** 2026-05-12 (initial document, H-001)

---

## Core terms

### Tranche

A single PURSUE release batch. Identified by date.

- **Tranche 1:** 2026-05-08 release at war.gov/UFO.
- Future tranches numbered sequentially, dated.

Every archived item belongs to exactly one tranche. If material appears in a later tranche that we already have from an earlier one, the later capture is a separate manifest row (same item, new tranche, new retrieval).

### Item

A single archived artifact. One file, one item.

- A 200-page PDF mission report is **one item.**
- A 12-minute FLIR video is **one item.**
- A page-of-photographs scan is **one item** even if it depicts multiple distinct objects.
- An accompanying transcript published alongside a video is a **separate item** linked to the video by manifest reference, not the same item.

Items get a stable `item_id` once ingested into the database (Phase 4). Until then, they're referenced by their relative path under `data/raw/`.

### Manifest

The catalog of all archived items. First version is a JSON-Lines or CSV file produced by the Phase 1 archiver. Promoted to a database table in Phase 4.

Every manifest row carries: `item_id`, `tranche`, `media_type`, `source_url`, `agency`, `file_hash` (SHA-256), `retrieval_timestamp`, `archiver_version`, `local_path`, plus whatever metadata the source page provided.

### Provenance

The full chain of where an item came from. For Argus, provenance is:

1. **Source URL** — the war.gov page (or archive.org mirror, or agency-direct URL) the item was fetched from.
2. **Agency** — the originating government body that released the item (DoW, ODNI, FBI, NASA, DOE, AARO, etc.).
3. **Tranche** — which release batch.
4. **Retrieval timestamp** — when our archiver pulled it.
5. **File hash** — SHA-256 of the bytes as retrieved.

If we can't answer "where did this come from?" from the manifest in thirty seconds, the manifest is broken.

### Media type

The three storage buckets in `data/raw/`:

- **video** — `.mp4`, `.mov`, `.avi`, etc. FLIR footage, sensor recordings, declassified video.
- **images** — `.jpg`, `.png`, `.tiff`, etc. Photographs (Apollo, aerial, etc.), still frames pulled from video.
- **text** — `.pdf`, `.txt`, `.docx`, transcripts, mission reports, source documents.

If a future tranche introduces a new media type (e.g., raw radar sensor data, 3D scan files), add a bucket and a row in this document.

### Agency

The originating government body credited with the release. Known agencies for Tranche 1:

- **DoW** — Department of War
- **ODNI** — Office of the Director of National Intelligence
- **FBI** — Federal Bureau of Investigation
- **NASA** — National Aeronautics and Space Administration
- **DOE** — Department of Energy
- **AARO** — All-domain Anomaly Resolution Office

Spell out the abbreviation on first use in any document. Use the abbreviation thereafter.

### Tranche-dated capture

Argus assumes war.gov may change between tranches. A "tranche-dated capture" is the snapshot of a source page at the time of one specific archiver run, preserved alongside the items it produced. If a war.gov page is restructured between Tranche 2 and Tranche 3, we have the Tranche-2 capture to consult.

---

## Phase-specific terms

### Phase 3: classification dimensions (provisional)

These are starting candidates from the project handoff document. They are **not committed** until Phase 3 has been run.

- **Morphology** — shape, size, structure of the depicted phenomenon.
- **Behavior** — movement, interaction, state changes.
- **Environment** — setting, conditions, context.
- **Sensor type** — what captured the item (FLIR, optical, radar, eyewitness photograph, declassified document scan).
- **Quality / confidence** — resolution, clarity, completeness.

When Phase 3 freezes v1 of the taxonomy, those terms move from "provisional" to "canonical" in this document.

### Phase 5: classification

A **classification** is a (dimension, category, item, classifier_id, confidence, timestamp) tuple. The same item can carry multiple classifications across dimensions. Classifications are versioned with the taxonomy version they were produced under.

---

## What this document is *not*

This is the vocabulary of the project's infrastructure (tranche, item, manifest, provenance). It is **not** the substantive UAP-domain vocabulary (morphology categories, sensor signatures, encounter typologies). That vocabulary is the output of Phase 3 and lives in `taxonomy/`.

---

## How to add a term

1. Open a handoff (any active handoff is fine; or open a small dedicated one).
2. Propose the term, its operational definition, and where it applies.
3. Eurydice confirms.
4. Add the term to this file under the appropriate section.
5. Note the addition in the handoff's report-back.

Do not silently introduce vocabulary in code or other docs. Naming drift is how systems become unmaintainable.
