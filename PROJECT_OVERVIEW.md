# Argus — Project Overview

**Owner:** Eurydice
**Status:** Phase 0 (project scaffold) complete; Phase 1 (archive) pending
**Last updated:** 2026-05-12

---

## 1. The substantive question

On May 8, 2026, the Trump administration released the first tranche of declassified UAP files through the **Presidential Unsealing and Reporting System for UAP Encounters (PURSUE)** program. Files are hosted at **war.gov/UFO**. Additional tranches are expected on a rolling basis.

This project — **Argus** — builds a **complete visual taxonomy system** for the PURSUE releases: archived, indexed, classified, and analyzed. The taxonomy itself does not yet exist and will be designed by the researcher as patterns emerge from the data.

The name comes from Argus Panoptes, the hundred-eyed giant of Greek mythology whose purpose was total observation. After his death, his eyes were set into the peacock's tail — surveillance transformed into a colorful visual pattern. The PURSUE data itself contains eyeball imagery, because sometimes a project names itself.

The project does not claim anything about whether the phenomena depicted are real, what's causing them, or what they mean. It builds the **infrastructure** for systematic visual analysis of declassified material as it becomes public. The intellectual question — *what categories actually distinguish the contents of this archive?* — is answered in Phase 3 after the data is in hand.

---

## 2. What this project is NOT

This is **not** the Anomaly Taxonomy / Mack-Bullard UFO Matrix. That project processes text narratives through Bullard's 550-code motif taxonomy. This project processes visual and documentary material through a classification system that will be built from the ground up.

The two projects share a researcher, a methodological philosophy, and a research domain. They may eventually cross-reference (e.g., do visual morphology types correlate with narrative episode patterns?). But they are **separate repos, separate databases, separate pipelines.** Cross-referencing is future work, scoped to its own handoff.

---

## 3. The data

The PURSUE first tranche includes:

- Military sensor / FLIR video footage (e.g., Iraq 2022 mission report, Greece coastal UAP)
- Apollo 12 and Apollo 17 photographs and mission transcripts
- Declassified mission reports and source documents
- Material from multiple agencies: Department of War, ODNI, FBI, NASA, DOE, AARO

Future tranches will add more videos, imagery, investigative materials, and potentially sensor data.

**Key characteristic:** most visual material is monochrome, low-resolution, and technical (infrared, FLIR, grainy military footage). The researcher is color-dominant in visual processing — the taxonomy output layer should use color-coding to make classification visually engaging and analytically useful.

**Media types** are partitioned into three buckets at storage layer: `video/`, `images/`, `text/`. Whether they share one taxonomy or get separate classification tracks is an open question for Phase 3.

---

## 4. Build order (high level)

Detailed phase descriptions live in [FUTURE_WORK.md](FUTURE_WORK.md). The summary:

1. **Archive** — systematically download and preserve everything at war.gov/UFO. Re-runnable for future tranches.
2. **Survey** — catalog what's actually in the archive. Note material types, metadata, patterns.
3. **Design the taxonomy** — classification categories emerge from observed patterns, not imposed in advance. This is the intellectual core.
4. **Schema** — SQLite database designed around the taxonomy from Phase 3.
5. **Index and classify** — apply the taxonomy. Color-coded visualization layer for analysis. Iterate as new tranches arrive.

The order is fixed. Don't skip phases.

---

## 5. Methodological scaffolding

These principles are inherited from the Anomaly Taxonomy project, where they were earned the hard way:

### 5.1 Provenance tracking

Every archived item is traced to:

- Source URL (the war.gov page or sub-page it came from)
- Originating agency (DoW, ODNI, FBI, NASA, DOE, AARO, etc.)
- Tranche (which release batch it belongs to, dated)
- Retrieval date and tool version (which archiver run pulled it)

If we ever need to answer "where did this come from?" the answer must be findable in the manifest in under thirty seconds.

### 5.2 Pre-registration discipline

Before any cross-cutting analysis run on the archive, write a prediction document on disk: what we expect to see, what would falsify it, what we've been exposed to that might bias the prediction. This is how the Anomaly Taxonomy project keeps results trustworthy across corpora.

For Argus, pre-registration applies to Phase 3 (taxonomy design — what dimensions do we expect to matter?) and Phase 5 (analytical runs — what patterns do we predict the classified archive will show?).

### 5.3 Negative controls

Before classifying a UAP archive, the apparatus should also be run on material that is *visually similar but not UAP* — declassified non-UAP military footage, conventional aviation, civilian aerial photography. If the taxonomy fires the same way on both, the categories don't discriminate.

This is a Phase 5 concern, but it should be designed in from Phase 3.

### 5.4 Audit trail

Every claim has a paper trail. The instrument document defines what's being measured, independent of any specific item. Per-item classifications report what the instrument finds. Raw outputs are kept alongside human-readable summaries so any number in any document can be traced back to the script that produced it.

A formal session-to-session handoff protocol (the H-### chain — see `handoffs/`) maintains continuity across the conversations that produce the work.

### 5.5 No batch decisions without verification

Every classification is reviewed. Bulk auto-classification with no human review is prohibited. Confidence-tiered automation (high-confidence auto-pass, low-confidence flagged for review) is allowed once a tier definition is calibrated and documented.

---

## 6. Where it is now

Phase 0 complete: project scaffolded, GitHub repo connected, directory structure built, working protocol in place. One manually-downloaded PURSUE PDF in `data/raw/text/`; the researcher is bulk-loading the rest of the manual downloads into the three media buckets.

Phase 1 (archive) is the immediate next step. Open question to settle in H-002: does war.gov/UFO provide a machine-readable manifest, or do we need to scrape the HTML and infer structure?

---

## 7. Where it's going next

See [FUTURE_WORK.md](FUTURE_WORK.md) for the full phase plan and open questions.

Near-term:

1. **Inventory the manually-loaded files.** Get a baseline picture of what's currently in `data/raw/`.
2. **Fetch war.gov/UFO and survey.** Understand the source structure before writing an archiver.
3. **Design and build the archiver.** Re-runnable, idempotent, tracks tranches.

Far-term:

- Survey existing UAP classification systems (Hynek, Vallée, AARO, GEIPAN, SCU) for comparison and inspiration.
- Decide whether video, image, and document material share one taxonomy or get separate classification tracks.
- Design the color-coded visualization layer for the classified archive.

---

## 8. Folder map

```
ARGUS/
├── CLAUDE.md                # Working protocol for Claude sessions
├── CURRENT.md               # Lean "where am I now" pointer
├── PROJECT_OVERVIEW.md      # This file
├── FUTURE_WORK.md           # Phase plan + open questions
├── README.md                # Public-facing description
├── LICENSE
├── data/
│   └── raw/                 # Downloaded files (gitignored; tracked via manifest)
│       ├── video/
│       ├── images/
│       └── text/
├── src/                     # Pipeline code (archiver, indexer, classifier)
├── taxonomy/                # Classification system (designed in Phase 3)
├── db/                      # Schema + migrations (designed in Phase 4)
├── notebooks/               # Survey and exploration work
├── docs/
│   ├── WORKFLOW_PROTOCOL.md # Standing rules
│   └── NOMENCLATURE.md      # Vocabulary
└── handoffs/
    ├── _index.md            # Newest-first chronology
    └── H-###_*.md           # Per-handoff source of truth
```

---

## 9. What this folder is *not*

- **Not a forum for UAP advocacy or debunking.** The taxonomy is descriptive. Causal and ontological claims are out of scope.
- **Not a finished classification system.** The taxonomy is designed in Phase 3 from observed patterns. Anything that looks like a final category in Phase 0 or Phase 1 is provisional.
- **Not a tool for re-hosting copyrighted material.** The PURSUE releases are public domain by government release. Anything that isn't, doesn't go in this archive.
