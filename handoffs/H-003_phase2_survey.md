# H-003 — Phase 2 technical survey (manifest enrichment + structural notes)

**Date:** 2026-05-12
**Decided in:** Eurydice chat (post-H-002 close, same session)
**Author:** Eurydice + Claude Code (Opus 4.7)
**Status:** Active

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
