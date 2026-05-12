# WORKFLOW_PROTOCOL — Argus

Standing rules for all work in this project. Applies to Claude Code, Cowork, and any other agent or operator. Additions to this document require an Eurydice decision recorded in the handoff chain.

**Last updated:** 2026-05-12 (initial document, H-001)

---

## Rule 1 — Three files form the always-current discoverability layer

The project's discoverability layer is three files, each with a defined role:

1. **`CURRENT.md`** at project root — lean (target: ≤ 3 screens) "where am I right now?" snapshot. Contains: ACTIVE WORK block (where work is paused, what's blocking, concrete resume path), recent-handoffs pointer (last 3), and links to detail elsewhere. **Not a kitchen-sink doc.**
2. **`handoffs/_index.md`** — newest-first one-line table of every handoff. The fast-scan index for the chronology.
3. **`handoffs/H-###_<topic>.md`** — full handoff document, source of truth for the work it covers.

### Session-close checklist (mandatory)

Closing a handoff means **all of the following are true**:

- [ ] The new handoff doc is at `handoffs/H-###_<topic>.md`
- [ ] `CURRENT.md`'s ACTIVE WORK block is updated to point at the new handoff (or, if the handoff closed without a follow-up, ACTIVE WORK reflects the new state)
- [ ] `CURRENT.md`'s "Last updated" timestamp is today
- [ ] `CURRENT.md`'s "Recent handoffs" table has the new handoff at the top
- [ ] `handoffs/_index.md` has a new row at the top under either Active or Closed
- [ ] Previous Active row in `handoffs/_index.md` has been moved to Closed (if applicable)
- [ ] All updates land in the **same git commit** as the new handoff doc

If any of these are missing, the handoff is **not closed**. Closure is a single atomic commit, not a series.

### Session-start reading order (mandatory for any agent)

Before responding to any user message, even casual greetings:

1. Read `CURRENT.md` — get the active-work block.
2. Read the handoff doc that `CURRENT.md` points to — get full context.
3. Cross-check against `handoffs/_index.md` — if the index has handoffs newer than `CURRENT.md`'s "Last updated" date, **CURRENT.md is stale**. Notify the user and read the latest handoff as the source of truth.
4. If the work to be done involves creating or closing a handoff, also read this file (Rule 1's session-close checklist) so closure discipline is in mind from the start.

This reading order is what makes documentation "rigorous enough to keep on track without manual prompting" — Eurydice has stated this as a hard requirement.

---

## Rule 2 — Directory convention

| Directory | Contents |
|---|---|
| `/` (root) | Top-level operational artifacts: `README.md`, `CLAUDE.md`, `CURRENT.md`, `PROJECT_OVERVIEW.md`, `FUTURE_WORK.md`, `LICENSE`. Only stable, current operational data here. |
| `src/` | All executable code. Python, SQL DDL, shell scripts. |
| `taxonomy/` | The classification system (designed in Phase 3). Versioned (`taxonomy_v1.md`, `taxonomy_v2.md`, etc.). |
| `db/` | Schema (`schema.sql`) and migrations. The database file itself is gitignored. |
| `notebooks/` | Survey and exploration work. Phase 2 lives here; Phase 3 drafts live here before promotion to `taxonomy/`. |
| `docs/` | Persistent documentation: `WORKFLOW_PROTOCOL.md`, `NOMENCLATURE.md`, `SCHEMA_NOTES.md` (eventual). Docs here are maintained, not appended. |
| `handoffs/` | One `H-###_<topic>.md` per handoff request. Verbatim copy of the handoff as given by Eurydice. Plus `_index.md`. |
| `data/raw/` | Downloaded files from war.gov/UFO and elsewhere. **Gitignored.** Subdivided into `video/`, `images/`, `text/`. Provenance tracked via manifest, not git. |
| `logs/` | Run logs, archiver logs, classifier logs. One log per run is acceptable. |
| `audits/` | Formal audits (`AUD-###` entries). Empty until first audit. |

New folders require a protocol-doc update. Do not silently invent directories.

---

## Rule 3 — Read-only perimeter for war.gov and external sources

Argus **archives** external material. It does not modify it. Any source we fetch from (war.gov/UFO, agency mirror sites, archive.org reflections) is treated as **read + copy-out only**.

- Every fetched item is hashed on download. The hash and source URL are recorded in the manifest.
- If a source page changes between tranches, we capture the new version with a new retrieval timestamp; we do not overwrite the prior capture.
- Re-running the archiver against a previously-archived item with a different hash is a flag-and-investigate event, not a silent overwrite.

---

## Rule 4 — Handoff format

Every handoff (the spec itself, as written by Eurydice) has this structure:

- **Date** / **Decided in** / **Author**
- **Task** — one-paragraph summary
- **Context** (optional) — background findings or dependencies from prior handoffs
- **Inputs** — complete list of files / artifacts needed, with read / write designation
- **Working directory**
- **Procedure** — numbered steps, as specific as the task requires
- **Output** — exact filenames and paths
- **Acceptance criteria** — pass / fail conditions, numeric targets where applicable
- **Do NOT** — explicit exclusions
- **Report back to Eurydice chat with** — bullet list of items the closure must include

Claude Code saves the verbatim handoff text to `handoffs/H-###_<topic>.md` at the start of execution. Saved before any work begins, so the handoff record exists even if execution fails.

Handoff numbers are sequential. Sub-handoffs (revisions, fixes) use letter suffixes (`H-001a`, `H-001b`). Do not reuse numbers.

---

## Rule 5 — Report-back format

Every handoff closure ends with an explicit Eurydice-chat summary. The summary covers every item in the handoff's `Report back to Eurydice chat with` list — in order, with specific numbers, with links to the output files.

Report-back is not a freeform wrap-up. It is a structured answer keyed to the handoff's explicit questions. If a `Report back with` item can't be answered, say so explicitly and explain why.

Include at closure:

- Numerical results (counts, deltas, pass / fail flags)
- Links to output files in the conversation
- Confirmation of read-only perimeter (Rule 3) where applicable
- Any design decisions not specified in the handoff
- Any bugs or issues discovered in prior handoffs that were fixed in passing

---

## Standing conventions (not formal rules, but please)

- **Do not use emojis** in documentation unless a source artifact we're preserving uses them. Keep the tone technical. (Exception: a small set of status glyphs already used in `CLAUDE.md` / `CURRENT.md`.)
- **When editing a file someone else may be reading** (e.g., a closed handoff doc), do not delete content — only correct or append. The audit trail matters.
- **Timestamps in local time** for human-facing fields; ISO-8601 UTC for machine-read fields.
- **Do not invoke LLMs** in a handoff that doesn't explicitly authorize it. Deterministic work is the default; LLM passes are opt-in.
- **No batch decisions without verification.** Bulk classification without human review is prohibited until a confidence-tiered automation rule has been calibrated and documented.

---

## Changelog

| Date | Change |
|---|---|
| 2026-05-12 | Initial document created at close of H-001. Imports patterns established in the Anomaly Taxonomy project, adapted for Argus's media-archival domain. Rules 1, 2, 3, 4, 5 in place. Rule 6 (data variant naming) deferred until variants exist. |
