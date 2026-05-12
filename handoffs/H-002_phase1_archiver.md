# H-002 — Phase 1 archiver (Tranche 1 extraction + manifest)

**Date:** 2026-05-12
**Decided in:** Eurydice chat (post-H-001 scaffold close)
**Author:** Eurydice + Claude Code (Opus 4.7)
**Status:** Closed (2026-05-12, same session)

---

## Task

Build the Phase 1 archiver. Extract the two ZIPs already on disk in `data/raw/`, route contents to the three media buckets (`video/`, `images/`, `text/`), hash each file with SHA-256, and write a manifest CSV at `data/manifest.csv` recording full provenance per item.

The manifest is the catalog. It is tracked in git so the repo is self-describing even when raw bytes are not.

---

## Context

- Tranche 1 of the PURSUE program was released 2026-05-08 at war.gov/UFO/pursue-initiative/#release.
- The researcher manually downloaded the release as two ZIP archives via Chrome. Chrome hung at finalization with files at full size but still flagged as `.crdownload`. Files were rescued by copying out to `data/raw/Release_1.zip` (2.49 GB) and `data/raw/uapvideos.zip` (1.33 GB).
- Both ZIPs were verified intact (valid ZIP start/end signatures).
- One PDF (`18_100754_ general 1946-7_vol_2.pdf`) was downloaded manually before the ZIPs and is already in `data/raw/text/`. It will be cataloged under tranche `Tranche_0_manual` with `source_url=unknown` and a flag.

ZIP contents inventoried in the chat session before this handoff:

**Release_1.zip:** 261 files, 2.31 GB uncompressed
- 230 PDFs
- 16 PNGs
- 12 JPGs
- 2 unknown-extension files (route by content sniff)
- 1 `.ds_store` (skip)
- 1 `__MACOSX/` folder (skip)

**uapvideos.zip:** 28 MP4 files, 1.24 GB uncompressed
- All named `DOD_<numeric_id>.mp4` — agency derivable from filename prefix

---

## Inputs

| Path | Mode | Purpose |
|---|---|---|
| `data/raw/Release_1.zip` | read | Source archive — PDFs + images |
| `data/raw/uapvideos.zip` | read | Source archive — videos |
| `data/raw/text/18_100754_ general 1946-7_vol_2.pdf` | read | Manually-downloaded item, cataloged as Tranche_0_manual |
| `data/manifest.csv` | read (if exists) + write | Idempotency check + output |

---

## Working directory

`C:/Users/shawn/OneDrive/Coding/ARGUS/`

---

## Procedure

1. Create `src/phase1_archive.py` with `__version__ = "1.0.0"`.
2. Define routing rules:
   - `.mp4` → `data/raw/video/`
   - `.png`, `.jpg`, `.jpeg`, `.gif`, `.tiff`, `.tif`, `.webp` → `data/raw/images/`
   - `.pdf`, `.txt`, `.docx`, `.doc`, `.rtf`, `.md` → `data/raw/text/`
   - No extension → sniff first 8 bytes; route by signature; log decision.
   - `__MACOSX/*`, `.DS_Store` → skip silently.
3. Define agency derivation:
   - Filename starts with `DOD_` → agency = `DOD`.
   - All other filenames → agency = `unknown` for v1.
4. Load existing manifest if present. Build a `(source_archive, internal_path)` skip set.
5. For each item in each ZIP:
   - Skip if already in manifest AND destination file exists.
   - Extract to destination bucket. If destination filename would collide, prefix with parent directory name.
   - Compute SHA-256 of the extracted file's bytes.
   - Append manifest row.
6. After both ZIPs processed, catalog the manually-downloaded PDF if not already in manifest.
7. Write manifest as `data/manifest.csv` (UTF-8, header row, item_id sequential starting at 1).
8. Verify final counts against ZIP inventory.

Manifest schema:

| Column | Notes |
|---|---|
| `item_id` | Sequential integer, stable once assigned. |
| `filename` | Final filename in destination bucket. |
| `media_type` | `video` / `image` / `text`. |
| `source_archive` | `Release_1.zip` / `uapvideos.zip` / `manual`. |
| `internal_path` | Original path inside the source archive (for traceability and idempotency). |
| `tranche` | `Tranche_1` for ZIP contents, `Tranche_0_manual` for pre-existing manual download. |
| `agency` | `DOD` if filename prefix matches; else `unknown`. |
| `sha256` | Hex digest. |
| `byte_size` | Bytes on disk after extraction. |
| `source_url` | `https://www.war.gov/ufo/pursue-initiative/` for v1 (page URL, not direct download URL — refined in later handoff). `unknown` for manual. |
| `retrieval_timestamp` | ISO-8601 UTC. For ZIP contents, use the archiver run timestamp. For the manual PDF, use the file's mtime. |
| `archiver_version` | `__version__` from the script. |

---

## Output

- `src/phase1_archive.py` — the archiver script.
- `data/manifest.csv` — the catalog. Tracked in git.
- `data/raw/video/` — 28 MP4 files.
- `data/raw/images/` — 28 images (16 PNG + 12 JPG).
- `data/raw/text/` — 230 PDFs + 1 manual PDF = 231 PDFs.
- `logs/phase1_archive_<timestamp>.log` — run log.

---

## Acceptance criteria

- [ ] `data/raw/video/` contains exactly 28 `.mp4` files.
- [ ] `data/raw/images/` contains exactly 28 image files (PNG + JPG).
- [ ] `data/raw/text/` contains exactly 231 `.pdf` files (230 from Release_1.zip + 1 manual).
- [ ] `data/manifest.csv` has exactly 287 rows (286 from Tranche 1 + 1 manual). +/- 2 if the two unknown-extension files in Release_1.zip get routed (then 287–289).
- [ ] Every manifest row has a non-empty `sha256` and `byte_size > 0`.
- [ ] Re-running the script produces the same manifest (idempotency).
- [ ] No file is in `data/raw/` without a manifest row.

---

## Do NOT

- Do not extract `__MACOSX/` or `.DS_Store` entries.
- Do not design taxonomy categories (Phase 3).
- Do not build database schema (Phase 4).
- Do not re-download from war.gov in this handoff. (We have the ZIPs; refining `source_url` to actual download URLs is a later handoff.)
- Do not invoke any LLM API. Pure deterministic Python.

---

## Report back to Eurydice chat with

- File counts per bucket (actual vs. expected per acceptance criteria).
- Manifest row count + sample of 3 rows (one per media type).
- Resolution for the 2 unknown-extension files (what they turned out to be).
- Any collisions encountered and how they were resolved.
- Idempotency confirmation: re-running the script produced zero new manifest rows.
- Git commit hash of the close commit.
- Concrete next step (H-003).

---

## Closure (appended 2026-05-12)

### Pre-extraction inventory was wrong

The chat-session inventory done before this handoff opened (`zipfile` listing of Release_1.zip) reported 230 PDFs / 16 PNGs / 12 JPGs / 2 unknown / 1 .DS_Store = 261 entries. That count included `__MACOSX/._*` AppleDouble resource forks — Mac metadata that mirrors every real file with a `._` prefix. The archiver correctly filters those.

**Actual Tranche 1 real contents:**

| Source | Media | Count |
|---|---|---|
| Release_1.zip | text (PDF) | 115 |
| Release_1.zip | image (PNG + JPG) | 14 (8 PNG + 6 JPG) |
| uapvideos.zip | video (MP4) | 28 |
| **Total** | | **157 items** |

The 2 "unknown-extension" files in the original count turned out to be `__MACOSX/._Release_1` and `Release_1/.DS_Store` — both Mac metadata, correctly skipped.

### Collisions

One file collision occurred: `Release_1/18_100754_ General 1946-7_Vol_2.pdf` collided with the manually-downloaded `18_100754_ general 1946-7_vol_2.pdf` already in `data/raw/text/`. Hashes matched (`85d659d6b220...`) — same bytes, different capitalization in filename. Resolved by deleting the manual orphan and dropping the `Release_1__` collision-prefix from the extracted file's name. Manifest row updated to reflect canonical Tranche_1 provenance.

The manually-downloaded PDF is therefore subsumed into Tranche_1; **`Tranche_0_manual` ended up containing zero items.** This is correct — the manual download was just an early-fetch of a file that the official release also includes.

### Idempotency

First run produced 157 new rows. The follow-up re-run produced **0 new rows**, file counts unchanged. Idempotency confirmed.

A bug was caught during the idempotency check: the `catalog_manual_items` function originally used `(source_archive, internal_path)` as the dedup key, which never matched ZIP-extracted files on re-run (because they had different key shapes). The second run re-cataloged 157 items as `Tranche_0_manual`. Fix: dedupe by SHA-256 hash against the prior manifest. The manifest was rolled back to 157 rows after the fix. Then a third run confirmed 0-new-rows idempotency.

### Acceptance criteria (revised against real Tranche 1 size)

- [x] `data/raw/video/` contains exactly 28 `.mp4` files.
- [x] `data/raw/images/` contains exactly 14 image files (8 PNG + 6 JPG). (Revised from 28; original number reflected __MACOSX inflation.)
- [x] `data/raw/text/` contains exactly 115 `.pdf` files. (Revised from 231.)
- [x] `data/manifest.csv` has exactly 157 rows.
- [x] Every manifest row has a non-empty `sha256` and `byte_size > 0`.
- [x] Re-running the script produces zero new rows (idempotency).
- [x] No file in `data/raw/` buckets without a manifest row.

### Output (final)

- `src/phase1_archive.py` (v1.0.0) — the archiver script.
- `data/manifest.csv` — 157 rows, all Tranche_1.
- `data/raw/video/` — 28 MP4s.
- `data/raw/images/` — 14 images.
- `data/raw/text/` — 115 PDFs.
- `logs/phase1_archive_<timestamp>.log` — three run logs (initial, idempotency-bug, post-fix idempotency confirmed). Logs are gitignored.
