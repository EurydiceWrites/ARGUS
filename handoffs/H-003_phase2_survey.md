# H-003 — Phase 2 technical survey (manifest enrichment + structural notes)

**Date:** 2026-05-12
**Decided in:** Eurydice chat (post-H-002 close, same session)
**Author:** Eurydice + Claude Code (Opus 4.7)
**Status:** Closed (2026-05-12, same session)

---

## Task

Run the technical survey of Tranche 1. Enrich `data/manifest.csv` with per-item metadata (PDF page counts, image dimensions, video duration / resolution), analyze filename patterns, and write a structured survey notes document in `notebooks/survey_phase2.md` summarizing the shape of the archive and surfacing open questions for the researcher.

Out of scope: external-taxonomy literature survey (Hynek, Vallée, AARO, GEIPAN, SCU) — deferred to H-004.

---

## Context

H-002 closed with 157 items archived to `data/raw/{video,images,text}/` and the manifest carrying source-level provenance (filename, media type, archive, hash, byte size). Phase 3 (taxonomy design) cannot proceed responsibly until we know what's actually in the archive at item level: how big, how many pages, what resolution, what naming conventions, what the agency-released filenames implicitly tell us, what metadata is conspicuously absent.

---

## Inputs

| Path | Mode | Purpose |
|---|---|---|
| `data/manifest.csv` | read + write (in place enrichment) | Manifest to enrich with metadata columns |
| `data/raw/video/*.mp4` | read | Video metadata extraction |
| `data/raw/images/*.{png,jpg}` | read | Image dimensions |
| `data/raw/text/*.pdf` | read | PDF page counts + basic structural inspection |

---

## Working directory

`C:/Users/shawn/OneDrive/Coding/ARGUS/`

---

## Procedure

1. Create `src/survey_phase2.py` with `__version__ = "1.0.0"`.
2. Install required Python packages: `pypdf`, `pillow`. Check for `ffprobe` (ffmpeg); if absent, fall back to `cv2` (opencv-python) or empty values.
3. For each manifest row, enrich:
   - **text/PDF:** `pdf_page_count` (via `pypdf.PdfReader`)
   - **image:** `image_width`, `image_height` (via `PIL.Image`)
   - **video:** `video_duration_sec`, `video_resolution` (via `ffprobe` first, else cv2)
4. Re-write `data/manifest.csv` in place, preserving existing columns + adding new ones.
5. Run filename pattern analysis:
   - Cluster filenames by leading token (e.g., `DOD_*`, `FBI-*`, numeric-prefix, etc.)
   - For each cluster, report count and representative samples.
6. Compute size / page-count / duration distributions per media type (min, p25, median, p75, max).
7. Write `notebooks/survey_phase2.md` with:
   - Counts and size distributions per media type
   - Page-count distribution for PDFs
   - Filename pattern clusters with examples
   - Observations on what filenames implicitly encode (agency tags, ID numbers, version markers)
   - Observations on what's conspicuously absent (no incident date in filename, no location, no sensor type)
   - Open questions for the researcher to consider before Phase 3

---

## Output

- `src/survey_phase2.py` — the survey script. Re-runnable; idempotent (re-running on enriched manifest is a no-op or refreshes values).
- `data/manifest.csv` — same row count, new columns: `pdf_page_count`, `image_width`, `image_height`, `video_duration_sec`, `video_resolution`.
- `notebooks/survey_phase2.md` — the structured findings document.
- `logs/survey_phase2_<timestamp>.log` — run log.

---

## Acceptance criteria

- [ ] All 115 PDFs have non-blank `pdf_page_count`.
- [ ] All 14 images have non-blank `image_width` and `image_height`.
- [ ] All 28 videos have non-blank `video_duration_sec` and `video_resolution` (or a clearly flagged blank with reason).
- [ ] `notebooks/survey_phase2.md` exists and is at least minimally complete (counts, filename clusters, observations, open questions).
- [ ] Manifest row count unchanged (still 157).
- [ ] All existing manifest columns preserved.

---

## Do NOT

- Do not invoke any LLM.
- Do not propose taxonomy categories (Phase 3 work — survey is observation, not classification).
- Do not fetch war.gov in this handoff.
- Do not load to a database.

---

## Report back to Eurydice chat with

- Confirmation that all three acceptance-criteria enrichment columns are filled.
- The most striking pattern from the filename analysis (whatever it is).
- The clearest absence from the metadata.
- One open question that should be in front of the researcher before Phase 3 design.
- Git commit hash of the close commit.
- Concrete next step (likely H-004 = external-taxonomy survey, or H-005 = fetch war.gov for source-page metadata).

---

## Closure (appended 2026-05-12)

### Enrichment completed

All 157 manifest rows enriched with the H-003 column set:

- **115 PDFs:** `pdf_page_count` filled. Distribution: 1 / 1 / 6 / 11 / 290 (min/p25/median/p75/max). Largest is 290 pages; one section of `65_HS1-834228961_62-HQ-83894_Section_2.pdf` weighs in at 353 MB and 194 pages.
- **14 images:** `image_width` × `image_height` filled. The 6 NASA Apollo images are 4400×4600; the other 8 are small (~412×307 range).
- **28 videos:** `video_duration_sec` and `video_resolution` filled. 27 of 28 videos are 1920×1080 (HD). One outlier at 800×444. Duration range: 5 sec → 6.2 min (median 51 sec).

`cv2` (opencv-python) was installed to enrich videos in the absence of `ffprobe`. `pypdf` was installed for PDF enrichment.

### Most striking finding: filename metadata is far richer than the H-002 archiver caught

The first-pass agency derivation in `phase1_archive.py` looks only for `DOD_` prefix and tags everything else `unknown`. That caught 18% of items. The Phase 2 filename-pattern analysis reveals **6+ distinct agency conventions** in this release:

- **DOW** (Department of War, 41 items) — `DOW-UAP-D<n>-Mission-Report-<LOCATION>-<MONTH>-<YEAR>.pdf`
- **FBI** (32+ items) — mix of `FBI-Photo-<id>.pdf` and the FBI case-file convention `65_HS1-<case>_62-HQ-<office>_Section_<n>.pdf`
- **DOD** (28 videos)
- **NASA** (12 items) — `NASA-UAP-<type>-Apollo-<mission>-<year>.{jpg|pdf}`
- **DOS** (2 items) — `DOS-UAP-D<n>-Cable-<n>-<COUNTRY>-<MONTH>-<YEAR>.pdf`
- **USPER** (1 item — witness statement)

For roughly 80 of the 115 PDFs (the DOW, DOS, and NASA clusters), **agency / date / location / item-type are machine-extractable from filenames alone.** This is a Phase 3 input the project didn't know it had.

### Clearest absence

**FBI case files (~50 items) carry no date or location in the filename** — only case and section numbers. Same for the 28 DOD videos (only an asset ID, no incident metadata). For these clusters, content inspection is required to derive any of the taxonomy dimensions that DOW filenames hand us for free.

This creates a structural asymmetry: parts of the archive are pre-tagged by their releasing agency; other parts are essentially anonymous. Phase 3 design will need to account for that — either by acknowledging that some classification dimensions will be high-confidence for some items and missing for others, or by adding a content-extraction step (OCR, video frame sampling) before classification.

### Open question for the researcher (pre-Phase-3)

**What's the right unit of classification — file, incident, or scene?** A single 6-minute FLIR video almost certainly depicts more than one distinguishable visual event. A multi-section FBI case file at 290 pages bundles many separate documents. If the unit is "file," many items will collapse heterogeneous content into a single classification. If the unit is "incident" or "scene," we need a sub-item identification step before Phase 3 categories can even be applied. This decision should be settled before drafting taxonomy v1.

### Acceptance criteria

- [x] All 115 PDFs have non-blank `pdf_page_count`.
- [x] All 14 images have non-blank `image_width` and `image_height`.
- [x] All 28 videos have non-blank `video_duration_sec` and `video_resolution`.
- [x] `notebooks/survey_phase2.md` exists, structured per the procedure section. Auto-generated observations corrected after script run to reflect what was actually in the data (the original auto-stub claimed "no date in filename" — true for FBI but wrong for DOW/DOS/NASA).
- [x] Manifest row count unchanged (157).
- [x] All existing manifest columns preserved.

### Output (final)

- `src/survey_phase2.py` (v1.0.0)
- `data/manifest.csv` — same 157 rows, now with 5 enrichment columns appended.
- `notebooks/survey_phase2.md` — the survey notes document (sections 8 + 9 + 9b hand-corrected after first auto-generation).
- `logs/survey_phase2_<timestamp>.log` — run log (gitignored).
