# H-004 — Filename metadata extractor (DOW / DOS / NASA)

**Date:** 2026-05-12
**Decided in:** Eurydice chat (post-H-003 close, same Cowork session)
**Author:** Eurydice
**Status:** Open — Claude Code to execute

---

## Task

Build a deterministic filename-metadata extractor that parses the DOW, DOS, and NASA filename conventions surfaced in H-003 into structured columns on `data/manifest.csv`. Enrich approximately 55 of the 115 PDFs (and the relevant NASA images) with `agency`, `country`, `date`, `date_precision`, and `item_type` metadata that the filenames natively encode. FBI case files and DOD videos are explicitly out of scope — their filenames carry no incident-level metadata per H-003 and require content-extraction passes deferred to a later sub-phase.

This is Path B v1 preparatory work: it banks the quick win on the clean subset of the archive before Phase 3 (taxonomy design) begins.

---

## Context

This handoff opens the first work under the **Path B sequenced-hybrid strategy** for Phase 3 preparation. Three methodological commitments from the Eurydice chat (2026-05-12) frame this work and should be read before execution:

### Decision 1 — Unit of classification

The open question raised at H-003 close (*"What's the right unit of classification — file, incident, or scene?"*) is **settled**. The classification unit is the **incident**, not the file or the scene.

- **File** = unit of ingest and provenance. 1:1 with manifest rows. Carries hash, source URL, agency, retrieval date, byte size. Files do not get classified directly.
- **Incident** = unit of classification. A real-world UAP event. One file may document 0, 1, or N incidents; one incident may be documented by 1 or N files. Incidents carry the taxonomy codes.
- **Scene** = deferred to Phase 5+ as optional refinement. Not part of v1 schema.

### Decision 2 — Two-tier schema sketch for Phase 4

The Phase 4 schema (not part of this handoff, just informing the shape of this one) will contain at minimum:

| Table | Role |
|---|---|
| `files` | One row per artifact. Provenance, hash, source URL, agency. 1:1 with manifest. |
| `incidents` | One row per real-world UAP event. Date, location, summary. The classified unit. |
| `file_incidents` | Many-to-many join: which files document which incidents, with snippet / page / timestamp reference. |
| `taxonomy_codes` | The taxonomy itself (designed in Phase 3). |
| `incident_codes` | Many-to-many join: which codes apply to which incidents. |

Two joins, not one. The Mack-Bullard analog of *case ↔ motif* in Argus is **incident ↔ code**, not file ↔ code.

The filename-extracted columns landing on the manifest in this handoff will later flow into the `files` table and seed the `incidents` table where filename ≈ incident (which is the case for most DOW / DOS / NASA items).

### Decision 3 — Path B sequencing

Start with agencies whose filenames natively encode incident-level metadata. Defer messier sources (FBI case files, DOD videos) to later sub-phases requiring LLM-assisted extraction with researcher review.

Per H-003's filename-pattern analysis, three agency conventions are machine-parseable:

- **DOW** (~41 items, Department of War — succeeded the War Department branding in this declassification release): `DOW-UAP-D<n>-Mission-Report-<LOCATION>-<MONTH>-<YEAR>.pdf`
- **DOS** (~2 items, Department of State): `DOS-UAP-D<n>-Cable-<n>-<COUNTRY>-<MONTH>-<YEAR>.pdf`
- **NASA** (~12 items, mix of `.jpg` and `.pdf`): `NASA-UAP-<type>-Apollo-<mission>-<year>.{jpg|pdf}`

Refer to `notebooks/survey_phase2.md` (sections 8 and 9) for the verbatim sample filenames per cluster.

Out of scope:

- **FBI** (~32 items) — `65_HS1-<case>_62-HQ-<office>_Section_<n>.pdf`. No incident metadata in filename.
- **DOD videos** (28 items) — opaque asset IDs only.
- **USPER** (1 item) — single witness statement.

---

## Inputs

| Path | Mode | Purpose |
|---|---|---|
| `data/manifest.csv` | read + write (in-place enrichment) | Manifest to extend with five new columns |
| `notebooks/survey_phase2.md` | read | Filename-pattern reference; verbatim sample filenames per agency cluster |
| `data/raw/text/*.pdf` | not read | The script parses filenames only — do not open the PDFs themselves in this pass |
| `data/raw/images/*.{jpg,png}` | not read | Same — filename parsing only |

---

## Working directory

`C:/Users/shawn/OneDrive/Coding/ARGUS/`

---

## Procedure

1. **Create `src/extract_filename_metadata.py`** with `__version__ = "1.0.0"`. Add a module docstring summarizing what the script does, what it does not do (no file-opening, no LLM, no taxonomy), and which handoff authorized it (H-004).

2. **Define three regex patterns**, one per agency, as named-group regexes:
   - `DOW_PATTERN` — captures `doc_num`, `location`, `month`, `year`
   - `DOS_PATTERN` — captures `doc_num`, `cable_num`, `country`, `month`, `year`
   - `NASA_PATTERN` — captures `item_subtype`, `mission`, `year`
   Source the canonical example filenames from `notebooks/survey_phase2.md` before writing the patterns. Tolerate minor variations (case, hyphen vs. underscore) gracefully but log mismatches rather than silently passing.

3. **Define a single dispatch function** `parse_filename(filename: str) -> dict | None`. Try each pattern in order; return the first match as a dict with normalized fields. Return `None` if no pattern matches.

4. **Normalize captured fields:**
   - `agency`: literal `"DOW"`, `"DOS"`, or `"NASA"`.
   - `country`: for DOS, the captured country token (e.g., `"BRAZIL"`); for DOW, the location token (treated as a generalized geographic identifier); for NASA, leave blank (mission identifier is captured separately, not as country).
   - `date`: ISO-8601 string `YYYY-MM-DD`. Map month names to numbers (`JANUARY` → `01`, etc.). For DOW / DOS (month + year), default day to `01`. For NASA (year only), default month and day to `01`.
   - `date_precision`: literal `"day"` / `"month"` / `"year"` — reflects which fields were actually extracted vs. defaulted. DOW and DOS → `"month"`. NASA → `"year"`. (This column exists so downstream consumers don't mistake a defaulted `01` for a real January-1st date.)
   - `item_type`: a normalized free-form string. DOW → `"Mission Report"`. DOS → `"Cable"`. NASA → captured `item_subtype` (e.g., `"Photo"`).

5. **Load `data/manifest.csv`.** For each row, look up the row's filename, call `parse_filename`, and write the extracted dict into five new columns (`agency`, `country`, `date`, `date_precision`, `item_type`). For non-matching rows (FBI, DOD videos, USPER, anything else), leave the five new columns blank.

   IMPORTANT: do not overwrite the `agency` column if it already exists from H-002's first-pass tagging — preserve any existing value only where it agrees; surface disagreements in the log as a researcher-review flag. If `agency` already exists and is blank, fill it. If it's already populated with a value that conflicts with what the filename parser derives, write the new value but log the disagreement.

6. **Write `data/manifest.csv` back in place**, preserving all existing columns and appending the five new ones in the order: `agency, country, date, date_precision, item_type`. Maintain the existing row count (157).

7. **Create `src/test_extract_filename_metadata.py`** — a test file living next to the script (no new `tests/` directory; the Rule 2 directory list does not yet authorize one).

   Write at minimum nine tests:

   - 3 known DOW filenames → expected parses
   - 3 known DOS / DOW edge cases (or 3 DOS if 3 distinct ones exist; otherwise 2 DOS + 1 ambiguous DOW)
   - 3 known NASA filenames → expected parses
   - 1 negative test: an FBI filename → returns `None`
   - 1 negative test: a DOD video filename → returns `None`

   Use the `unittest` standard-library framework (no new dependencies). Run the test file. All tests must pass before the script is considered complete.

8. **Idempotency check.** Run the enrichment script a second time against the now-enriched manifest. The resulting CSV must be byte-identical to the first run's output. Hash both runs' outputs and compare in the log.

9. **Write a run log** to `logs/extract_filename_metadata_<ISO-8601-UTC-timestamp>.log` containing: counts per agency parsed, list of filenames that failed all patterns, list of agency-disagreement flags (if any), idempotency-check pass / fail.

---

## Output

- `src/extract_filename_metadata.py` (v1.0.0)
- `src/test_extract_filename_metadata.py`
- `data/manifest.csv` — same 157 rows. New columns appended: `agency` (if not already present), `country`, `date`, `date_precision`, `item_type`.
- `logs/extract_filename_metadata_<timestamp>.log` (gitignored per Rule 2 convention).

---

## Acceptance criteria

- [ ] All ~41 DOW items have non-blank `agency`, `country`, `date`, `date_precision`, `item_type`.
- [ ] All ~2 DOS items have non-blank `agency`, `country`, `date`, `date_precision`, `item_type`.
- [ ] All ~12 NASA items have non-blank `agency`, `date`, `date_precision`, `item_type`. `country` may be blank by design.
- [ ] FBI, DOD-video, and USPER rows have blank values in the five new columns. (Not blank in legacy columns — only in the new ones.)
- [ ] Manifest row count unchanged (157).
- [ ] All existing manifest columns preserved.
- [ ] All tests in `src/test_extract_filename_metadata.py` pass.
- [ ] Idempotency check passes (second run produces byte-identical output).
- [ ] If any filename-parser-vs-existing-`agency` disagreements were flagged, they are listed in the report-back for researcher review (not silently overwritten).

---

## Do NOT

- Do not invoke any LLM. This is deterministic regex work — Rule 4 prohibition on unauthorized LLM use applies.
- Do not open any PDF, image, or video file. Filename parsing only.
- Do not attempt to parse FBI case files or DOD video filenames. Their filenames do not encode incident-level metadata; attempting to derive it is fabrication.
- Do not modify any file in `data/raw/`. Read-only perimeter (Rule 3).
- Do not fetch from war.gov or any external source.
- Do not propose taxonomy categories or seed an `incidents` table. Phase 3 is downstream of this work.
- Do not create a new top-level `tests/` directory; Rule 2 does not yet authorize one.
- Do not delete or rename any existing manifest column.

---

## Report back to Eurydice chat with

- Count of items enriched per agency (DOW, DOS, NASA), with totals matching the per-agency expectations above (and a delta vs. expectation if not).
- The list of filenames (if any) that fell into a DOW / DOS / NASA-like pattern but failed to parse — these are candidates for regex refinement.
- The list of agency-disagreement flags (filename parser said X, existing `agency` column said Y) — these are candidates for researcher review.
- Confirmation that idempotency check passes (second run byte-identical to first).
- Confirmation that all tests pass, with test count.
- Git commit hash of the close commit.
- Concrete next-step recommendation. Likely candidates: H-005 = external-taxonomy survey (Hynek / Vallée / AARO / GEIPAN / SCU), or H-006 = war.gov page parse to enrich `source_url`.

---

## Session-close checklist reminder (per WORKFLOW_PROTOCOL.md Rule 1)

When closing this handoff, all of the following must land in a single atomic commit:

- [x] Closure section appended below this line in `handoffs/H-004_filename_extractor.md`
- [x] `CURRENT.md` Active handoff field updated (likely to "none" pending researcher's next choice)
- [x] `CURRENT.md` Last updated timestamp = close date
- [x] `CURRENT.md` Recent handoffs table has H-004 row at top
- [x] `handoffs/_index.md` H-004 moved from Active to top of Closed

---

## Closure — 2026-05-12

**Status:** Closed.
**Executed by:** Claude Code (Opus 4.7).
**Executed against:** clean `data/manifest.csv` at sha256 `d92f8849b6ac568a225fe1125f4ab2c92eb51d83cccd99f1b36cdb0349e4227f` (post-H-003 state).

### Output artifacts

- [`src/extract_filename_metadata.py`](../src/extract_filename_metadata.py) v1.0.0 — deterministic parser, no LLM, no file opening.
- [`src/test_extract_filename_metadata.py`](../src/test_extract_filename_metadata.py) — 24 unit tests, all pass.
- [`data/manifest.csv`](../data/manifest.csv) — 157 rows unchanged, 17 original columns preserved, 4 new columns appended (`country`, `date`, `date_precision`, `item_type`). The pre-existing `agency` column was updated in place per Step 5 (no rename, no duplicate). Final column count: 21.
- `logs/extract_filename_metadata_20260512T232936Z.log` (gitignored per Rule 2).

### Report back to Eurydice — required items

**1. Enrichment counts per agency.**

| Agency | Parsed | Expected | Δ vs. expected |
|---|---|---|---|
| DOW | **39** | ~41 | −2 (two filenames lack location between item_type and date — see item 2) |
| DOS | **2** | ~2 | 0 |
| NASA | **12** | ~12 | 0 |
| **Total enriched** | **53** | — | — |

Of the 39 DOW rows, **all 39 have non-blank `agency`, `country`, `item_type`**; **38 have non-blank `date` and `date_precision`** — the one exception is `DOW-UAP-D54-Mission-Report-Mediterranean-Sea-NA.pdf`, where the source filename ends with the literal token `NA` in the date position. Writing a defaulted date there would fabricate provenance, so `date` and `date_precision` are left blank (item 5 below documents this design call).

All 2 DOS rows have all five fields populated. All 12 NASA rows have non-blank `agency`, `date`, `date_precision`, `item_type`; `country` is blank by design (NASA filenames don't encode country, per Step 4).

**2. Unparsed DOW / DOS / NASA-like filenames** (candidates for regex refinement):

- `DOW-UAP-D48-Report-September-1996.pdf`
- `DOW-UAP-D49-Launch-Summary-February-2000.pdf`

Both have a known DOW item_type (`Report`, `Launch-Summary`) and a parseable date (1996-09, 2000-02), but **no location token between item_type and date**. The parser is currently strict: it requires a non-empty location so the H-004 acceptance criterion ("DOW rows have non-blank `country`") is met for everything it claims to parse. Refining the regex to allow empty `country` would gain these 2 items at the cost of weakening that acceptance check — researcher decision for H-004a or a later sub-handoff.

**3. Agency-disagreement flags:** **0.** Every existing `agency` value from the H-002 first-pass tagging was either `"unknown"` (which the parser treats as blank and overwrites) or `"DOD"` (which the parser does not touch — DOD videos are out of scope per Step 5). No conflict between the filename-parser-derived agency and the H-002 archiver's per-row tag.

**4. Idempotency check: PASS.** The script's `main()` runs `enrich_manifest` twice internally and compares SHA-256 hashes of the resulting `data/manifest.csv`. Both runs produced `46508e74205af72949a1546fe4c38f4a04580217cb0f80c56eae4596fb43a06f`.

**5. Test count: 24, all passing.** The H-004 minimum was 9 (3 DOW + 3 DOS/edge + 3 NASA + 1 FBI negative + 1 DOD negative). Beyond the minimum, the suite covers: year-only DOW dates, day-precision DOW dates, the literal-`NA` date sentinel, the `Email-Correspondance` spelling variant, the literal-comma artifact in D32, the longest-first precedence between `Range-Fouler-Debrief` and `Range-Fouler`, multiword countries for DOS (`Papua-New-Guinea`), NASA Apollo / Skylab missions with appended descriptors, USPER / `059UAP*` / `Serial-*` / `Western_US_*` negative cases, and dispatch routing.

**6. Close commit hash:** filled in by the Close commit itself (see next step in the audit trail).

**7. Concrete next-step recommendation.**

- **H-005 — External-taxonomy survey** (Hynek / Vallée / AARO / GEIPAN / SCU). Already queued in CURRENT.md as the next step in the Path B sequencing; expected to run in the Eurydice chat in parallel with any follow-up Claude Code work. Output: `notebooks/existing_taxonomies.md`. **This is the recommended next step.**
- **H-006 (queued, not next)** — war.gov page parse to refine `source_url` from page-URL to direct-download-URL. Useful before Phase 5 but not blocking Phase 3 taxonomy design.
- **H-004a (optional, defer pending researcher call)** — refine the parser for D48 and D49 (allow empty `country` for the bare-`Report` and `Launch-Summary` item_types), or open those two PDFs for content-based location extraction.

### Design decisions not specified in the handoff (per Rule 5)

The handoff allowed reasonable interpretation in several places; the following calls were made during execution and are surfaced here for the audit trail:

1. **Comma tolerance.** `DOW-UAP-D32-Mission-Report,-Syria-October-2024.pdf` contains a literal comma after `Mission-Report` — an artifact in the source release. The parser tolerates both `<item_type>-` and `<item_type>,-` as valid separators. The comma is documented in [src/extract_filename_metadata.py](../src/extract_filename_metadata.py) `_strip_dow_item_type` and pinned by `test_dow_comma_artifact`.

2. **`Email-Correspondance` (typo variant) is a known item_type.** D52 has the spelling `Correspondance` (vs. the correct `Correspondence` used elsewhere). Both are listed in `DOW_ITEM_TYPES`; tests pin both spellings.

3. **DOW item_type captured from filename, not hardcoded.** Step 4 said "DOW → `'Mission Report'`" for item_type, but the survey enumerated `Mission-Report`, `Email-Correspondence`, `Email-Correspondance`, `Range-Fouler-Debrief`, `Range-Fouler`, `Launch-Summary`, and `Report`. Hardcoding `'Mission Report'` would silently mislabel ~7 items. The parser captures the actual literal token; the seven known types live in an ordered list, longest-first, to avoid prefix collisions (`Range-Fouler-Debrief` beats `Range-Fouler`).

4. **NASA `item_type` = literal captured `item_subtype` (e.g., `'VM3'`, `'D5'`)**, not a mapped friendly name like `'Photo'` or `'Document'`. The handoff's parenthetical example `(e.g., 'Photo')` was treated as illustrative — the actual subtype tokens carry meaning specific to NASA's internal numbering, and inventing a mapping without authority would be fabrication. Researcher can layer a `VM* → Photo`, `D* → Document` mapping in a later pass if useful.

5. **DOW `D54` literal-`NA` date sentinel preserved as blank.** The source filename `DOW-UAP-D54-Mission-Report-Mediterranean-Sea-NA.pdf` ends with the literal `NA` token where a date is expected. The parser reads this as "date deliberately marked unknown in source" and writes blank `date` and `date_precision`. Defaulting to `2025-01-01` (or any other fabricated date) would violate the no-fabrication discipline (CLAUDE.md methodological principles).

6. **DOW `date_precision` semantics.** `"day"` (e.g., `February-21-2023` → `2023-02-21`), `"month"` (e.g., `July-2020` → `2020-07-01`), `"year"` (e.g., `2025` → `2025-01-01`), or blank when source filename has no parseable date. Downstream consumers should never treat a defaulted day-01 / month-01 as a real January-1st date — the precision column is the load-bearing signal there.

7. **CSV format preserved.** UTF-8, CRLF line endings (Python `csv.DictWriter` default on Windows, matching the H-002/H-003 file state). The diff vs. the pre-run manifest is exactly the four appended columns + per-row enrichments; no row reordering, no quoting changes, no header reordering.

### Acceptance criteria (per H-004) — final

- [x] All ~41 DOW items have non-blank `agency`, `country`, `date`, `date_precision`, `item_type` — **39/41 strict pass; 2 surfaced as candidates; 1 (D54) has blank date by design (literal `NA` sentinel)**. Documented above.
- [x] All ~2 DOS items have non-blank `agency`, `country`, `date`, `date_precision`, `item_type` — **2/2 pass.**
- [x] All ~12 NASA items have non-blank `agency`, `date`, `date_precision`, `item_type`. `country` may be blank by design — **12/12 pass.**
- [x] FBI, DOD-video, and USPER rows have blank values in the five new columns — **64 FBI-like + 28 DOD + 1 USPER rows verified blank in `country`/`date`/`date_precision`/`item_type`.** The pre-existing `agency` column was untouched for these rows (still `unknown` for FBI/USPER, still `DOD` for the DOD videos).
- [x] Manifest row count unchanged (157) — **confirmed.**
- [x] All existing manifest columns preserved — **confirmed; 17 original columns preserved in original order.**
- [x] All tests in `src/test_extract_filename_metadata.py` pass — **24/24.**
- [x] Idempotency check passes (second run produces byte-identical output) — **PASS, hashes match.**
- [x] Agency-disagreement flags surfaced rather than silently overwritten — **0 disagreements; mechanism verified by code review of `enrich_manifest`.**

### Read-only perimeter check (Rule 3)

The parser opens no file in `data/raw/`. It reads `data/manifest.csv` (project-managed) and writes back to the same path. No external fetch. No mutation of war.gov / UFO source material. Read-only perimeter intact.
