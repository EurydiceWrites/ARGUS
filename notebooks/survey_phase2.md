# Survey — Phase 2 (Tranche 1)
**Generated:** 2026-05-12 18:42 by `src/survey_phase2.py` v1.0.0
**Source:** `data/manifest.csv` after enrichment with per-item metadata.

---

## 1. Counts per media type

| Media | Count |
|---|---|
| video | 28 |
| image | 14 |
| text | 115 |
| **Total** | **157** |

## 2. File size distributions (bytes)

| Media | Count | Min | p25 | Median | p75 | Max |
|---|---|---|---|---|---|---|
| video | 28 | 416.9 KB | 4.1 MB | 15.0 MB | 69.4 MB | 262.0 MB |
| image | 14 | 78.3 KB | 87.0 KB | 95.2 KB | 2.4 MB | 2.5 MB |
| text | 115 | 19.6 KB | 419.9 KB | 661.3 KB | 8.7 MB | 353.4 MB |

## 3. PDF page-count distribution

| Min | p25 | Median | p75 | Max |
|---|---|---|---|---|
| 1 | 1 | 6 | 11 | 290 |

## 4. Video duration distribution (seconds)

| Min | p25 | Median | p75 | Max |
|---|---|---|---|---|
| 5.0 | 10.0 | 51.0 | 117.1 | 371.6 |

**Video resolutions:**

- `1920x1080`: 27 videos
- `800x444`: 1 videos

## 5. Image resolution distribution

| Resolution | Count |
|---|---|
| 4400x4600 | 6 |
| 412x306 | 2 |
| 544x368 | 1 |
| 538x321 | 1 |
| 413x307 | 1 |
| 412x308 | 1 |
| 637x307 | 1 |
| 434x322 | 1 |

## 6. Agency distribution (derived from filename)

| Agency | Count |
|---|---|
| unknown | 129 |
| DOD | 28 |

## 7. Filename pattern clusters

### `DOW-<rest>` — 41 items

Examples:

- `DOW-UAP-D65-Mission-Report-Persian-Gulf-July-2020.pdf` (text)
- `DOW-UAP-D16-Mission-Report-Syria-July-2022.pdf` (text)
- `DOW-UAP-D75-Mission-Report-Gulf-of-Aden-July-2024.pdf` (text)
- `DOW-UAP-D8-Mission-Report-Djibouti-2025.pdf` (text)
- `DOW-UAP-D50-Email-Correspondence-INDOPACOM-April-2025.pdf` (text)

### `<numeric_prefix>_<rest>` — 33 items

Examples:

- `65_HS1-834228961_62-HQ-83894_Section_2.pdf` (text)
- `18_100754_ General 1946-7_Vol_2.pdf` (text)
- `65_HS1-834228961_62-HQ-83894_Section_3.pdf` (text)
- `65_HS1-834228961_62-HQ-83894_Section_1.pdf` (text)
- `65_HS1-101634279_100-DE-18221_Serial_844.pdf` (text)

### `FBI-<rest>` — 32 items

Examples:

- `FBI-Photo-B15.pdf` (text)
- `FBI-Photo-B14.pdf` (text)
- `FBI-Photo-B16.pdf` (text)
- `FBI-Photo-B17.pdf` (text)
- `FBI-Photo-B13.pdf` (text)

### `DOD_<numeric_id>` — 28 items

Examples:

- `DOD_111688723.mp4` (video)
- `DOD_111688762.mp4` (video)
- `DOD_111688775.mp4` (video)
- `DOD_111688809.mp4` (video)
- `DOD_111688816.mp4` (video)

### `NASA-<rest>` — 12 items

Examples:

- `NASA-UAP-VM3-Apollo-12-1969.jpg` (image)
- `NASA-UAP-VM6-Apollo-17-1972.jpg` (image)
- `NASA-UAP-VM5-Apollo-12-1969.jpg` (image)
- `NASA-UAP-D7-Skylab-Technical-Crew-Debriefing-1973.pdf` (text)
- `NASA-UAP-D4-Apollo-11-Technical-Crew-Debriefing-1969.pdf` (text)

### `<other>` — 4 items

Examples:

- `059UAP00011.pdf` (text)
- `059UAP00012.pdf` (text)
- `059UAP00013.pdf` (text)
- `2024-04-30-Composite-Sketch.pdf` (text)

### `<Serial_prefix>` — 3 items

Examples:

- `Serial-4-Redacted_Redacted.pdf` (text)
- `Serial 5 Redacted_Redacted.pdf` (text)
- `Serial-3_Redacted.pdf` (text)

### `DOS-<rest>` — 2 items

Examples:

- `DOS-UAP-D2-Cable-2-Kazakhstan-January-1994.pdf` (text)
- `DOS-UAP-D1-Cable-1-Papua-New-Guinea-January-1985.pdf` (text)

### `USPER-<rest>` — 1 items

Examples:

- `USPER-Statement-Redacted.pdf` (text)

### `<Western_prefix>` — 1 items

Examples:

- `Western_US_Event_Slides_5.08.2026.pdf` (text)

## 8. What filenames implicitly encode (the surprise)

The archiver's first-pass agency derivation (looking only for `DOD_` prefix) caught **18%** of items. The filename-pattern analysis reveals far richer agency tagging than was assumed at H-002 time:

**Agencies derivable from filename prefix:**

| Agency | Tag pattern | Count |
|---|---|---|
| Department of War | `DOW-UAP-*` | 41 |
| FBI | `FBI-*` and `65_HS1-*` (FBI case-file convention) | ~50 |
| Department of Defense | `DOD_<numeric_id>.mp4` | 28 |
| NASA | `NASA-UAP-*` | 12 |
| Department of State | `DOS-UAP-*` | 2 |
| US Person (witness statement) | `USPER-*` | 1 |
| Other / unclassifiable | mixed | ~23 |

**The DOW (Department of War) cluster carries the richest metadata.** Filenames like `DOW-UAP-D65-Mission-Report-Persian-Gulf-July-2020.pdf` and `DOW-UAP-D8-Mission-Report-Djibouti-2025.pdf` directly encode:

- Item type (`Mission-Report`, `Email-Correspondence`)
- Geographic location (Persian Gulf, Syria, Djibouti, Gulf of Aden, INDOPACOM)
- Date (year and often month)
- Internal document number (`D65`, `D8`, etc.)

**NASA filenames carry mission and year:** `NASA-UAP-VM3-Apollo-12-1969.jpg`, `NASA-UAP-D7-Skylab-Technical-Crew-Debriefing-1973.pdf`.

**DOS filenames carry country and date:** `DOS-UAP-D2-Cable-2-Kazakhstan-January-1994.pdf`.

**The `<numeric_prefix>` cluster (33 items) appears to be FBI case files** — pattern `65_HS1-<case>_62-HQ-<location>_Section_<n>.pdf` suggests file system / serial / section conventions from FBI records management.

**The `DOD_<numeric>` videos** use 9-digit IDs (`DOD_111688723.mp4` etc.) that look like DVIDS asset IDs but carry no other encoded metadata in the filename itself.

## 9. What filenames do NOT encode (true absences, narrower than originally assumed)

- **FBI case files lack date and location in the filename.** The `65_HS1-*` and `FBI-Photo-*` items show case numbers but not when or where the incident occurred. To get those, document content must be opened.
- **DOD videos carry no incident metadata at all.** Just an asset ID. To know what's in `DOD_111688723.mp4`, the video must be viewed.
- **Sensor type is never in any filename.** FLIR / optical / radar / other must be inferred from content.
- **Classification level at time of original creation** is a property of document content (cover-page markings), not filename.
- **Sequencing / pairing across items** is mostly absent. Some serialized FBI files have `Section_1`, `Section_2`, but cross-item incident grouping (video + accompanying report) is not encoded.

## 9b. What we can extract right now without human review

For ~80 of the 115 PDFs (the DOW, DOS, and NASA clusters), agency / date / location / item-type are **machine-extractable from filenames alone.** This is the first taxonomy-relevant signal the survey has surfaced. A small follow-up script (H-005 or later) could regex these out and add them as columns to the manifest.

## 10. Open questions for the researcher (pre-Phase-3)

1. **Do the 28 DOD videos belong to a small number of incidents, or are they 28 distinct incidents?** Numeric IDs are non-sequential — need to view content to know whether they cluster.
2. **Do PDFs accompany videos (paired evidence packages) or are they independent document releases?** Filename matching would not detect this; need content inspection.
3. **Is the war.gov page itself adding metadata that's not in the filenames** (captions, agency attribution, incident date)? Worth fetching the page in a later handoff.
4. **What's the right level of granularity for classification — per-file, per-incident, per-frame?** Videos in particular contain many distinct visual events; a single classification per video may be too coarse.
5. **Are documents-vs-images-vs-video three separate taxonomies or one with a media-type dimension?** (Open question carried from `FUTURE_WORK.md`.)

## 11. Next handoffs

- **H-004 (suggested):** External-taxonomy survey — Hynek, Vallée, AARO, GEIPAN, SCU. Output goes to `notebooks/existing_taxonomies.md`.
- **H-005 (suggested):** Fetch war.gov/UFO/pursue-initiative/ and parse the page for source-level metadata (captions, agency attribution per item). Refine `source_url` in the manifest from page-URL to direct-download-URL.
