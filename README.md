# Argus

Visual taxonomy system for the **Presidential Unsealing and Reporting System for UAP Encounters (PURSUE)** declassified releases hosted at war.gov/UFO.

Named for Argus Panoptes, the hundred-eyed giant of Greek myth whose purpose was total observation. After his death, his eyes became the peacock's tail — surveillance transformed into a colorful visual pattern.

## What this is

A complete archival, indexing, and classification pipeline for the PURSUE tranches. Designed for rolling releases — new tranches drop, the same pipeline runs again.

## What this is not

This is not the Anomaly Taxonomy / Mack-Bullard UFO Matrix. That project processes text narratives through Bullard's 550-code taxonomy. Argus processes visual and documentary material through a classification system designed from observed patterns in the data.

Separate repos. Separate databases. Separate pipelines. May eventually cross-reference.

## Build order

1. **Archive** — systematically download and preserve everything at war.gov/UFO. Re-runnable for future tranches.
2. **Survey** — catalog what's in the tranche. Note material types, metadata, patterns.
3. **Design the taxonomy** — classification categories emerge from the data, not imposed in advance.
4. **Schema** — SQLite database designed around the taxonomy.
5. **Index and classify** — apply the taxonomy. Color-coded visualization layer for analysis.

## Repo layout

```
argus/
├── data/
│   └── raw/                 # Downloaded files (gitignored; tracked via manifest)
│       ├── video/           # FLIR footage, sensor video, declassified video
│       ├── images/          # Photographs (Apollo, aerial, etc.), still frames
│       └── text/            # PDFs, transcripts, reports, mission documents
├── src/                     # Pipeline code (archiver, indexer, classifier)
├── taxonomy/                # Classification system (designed in Phase 3)
├── db/                      # Schema + migrations
└── notebooks/               # Survey and exploration work
```

## Methodological principles

- No batch decisions without verification. Every classification reviewed.
- Provenance tracking. Every item traced to its source release.
- Epistemic honesty. Tier confidence. Label what's certain vs. interpreted.
- Researcher is the human in the loop. AI assists; researcher decides.
- Build order is sacred. Don't skip phases.
