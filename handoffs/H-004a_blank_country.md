# H-004a — Allow blank DOW country for filenames lacking location

**Date:** 2026-05-12
**Decided in:** Eurydice chat (same session as H-004 close)
**Author:** Eurydice
**Status:** Closed (single atomic commit — Open and Close merged because the change is ~5 lines and the spec is one sentence)

---

## Task

Refine [`src/extract_filename_metadata.py`](../src/extract_filename_metadata.py) so that DOW filenames carrying a known `item_type` and a parseable date but **no location token** between them parse successfully with a blank `country` field, rather than failing the parse entirely.

## Context

H-004 closed with two unparsed DOW candidates:

- `DOW-UAP-D48-Report-September-1996.pdf`
- `DOW-UAP-D49-Launch-Summary-February-2000.pdf`

Both have a known DOW item_type (`Report`, `Launch-Summary`) and a parseable date (`1996-09`, `2000-02`), but the source filename omits the location token that DOW filenames usually carry between the item_type and the date. The H-004 parser was strict (required non-empty location) so the acceptance criterion *"DOW rows have non-blank `country`"* held for everything it claimed.

Eurydice decision in this chat: blank country is fine — it's a non-fabrication signal that the source filename simply does not encode location for these items. Preferable to losing the date and item_type entirely.

## Procedure (executed)

1. **`_strip_dow_item_type`** accepts an exact match (remainder == item_type) and returns `(item_type, "")` — empty location rather than parse failure.
2. **`parse_dow`** no longer treats empty location as a parse failure; documentation comment added.
3. **Tests renamed and rewritten:** `test_dow_bare_report` → `test_dow_bare_report_blank_country`, `test_dow_launch_summary` → `test_dow_launch_summary_blank_country`. Both now assert the full expected dict (blank country, populated date and item_type) rather than `None`.
4. **Manifest re-run** against a freshly-restored H-003 manifest. New result: 41 DOW + 2 DOS + 12 NASA = **55 of 157** enriched. **0** unparsed DOW/DOS/NASA-like filenames.

## Acceptance criteria (final)

- [x] D48 parses with `agency=DOW, country="", date=1996-09-01, date_precision=month, item_type=Report`
- [x] D49 parses with `agency=DOW, country="", date=2000-02-01, date_precision=month, item_type=Launch-Summary`
- [x] D54's literal-`NA` date sentinel still preserved (`country=Mediterranean-Sea, date="", date_precision=""`)
- [x] All 24 unit tests pass
- [x] Idempotency byte-identical (internal second-run hash `104834132a268f0795ecd246e1f40f70a0c2fb9d731a54fdfecf1969b5a5ea8e`)
- [x] Row count unchanged (157)
- [x] FBI / DOD / USPER rows unchanged
- [x] H-004 acceptance criteria **revised in spirit**: "All ~41 DOW items have non-blank `agency`, `date`, `date_precision`, `item_type`; `country` may be blank when the source filename omits the location token." The 3 design-preserving blanks (D48 country, D49 country, D54 date) are documented features, not gaps.

## Final per-agency state

| Agency | Enriched | Blank fields (by design) |
|---|---|---|
| DOW | 41 / 41 | 2 with blank `country` (D48, D49); 1 with blank `date` + `date_precision` (D54 NA sentinel) |
| DOS | 2 / 2 | none |
| NASA | 12 / 12 | all 12 with blank `country` (NASA filenames don't encode country) |
| **Total** | **55 / 157** | — |

## Do NOT

- Do not retroactively edit the H-004 closure section — it's a historical record. H-004a is the formal record of the refinement.
- Do not loosen the parser further (e.g., to accept unknown item_types) — that would weaken the deterministic guarantee.

## Next step

Unchanged from H-004 close: **H-005 — external-taxonomy survey** in the Eurydice chat. No further parser refinement is on the table; the clean-subset enrichment is complete.
