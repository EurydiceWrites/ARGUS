# H-001 — Project scaffold

**Date:** 2026-05-12
**Decided in:** Eurydice chat (session pivoting from MLT Monitor work to ARGUS kickoff)
**Author:** Eurydice + Claude Code (Opus 4.7)
**Status:** Closed

---

## Task

Bootstrap the Argus project repository with a working-protocol scaffold replicating the structure used in the Anomaly Taxonomy project, adapted to Argus's media-archival domain. Produce a discoverability layer (CURRENT / handoffs / index), a Goal Grounding Protocol entry point (CLAUDE.md), a project framing document (PROJECT_OVERVIEW.md), a forward roadmap (FUTURE_WORK.md), standing operational rules (WORKFLOW_PROTOCOL.md), and a vocabulary document (NOMENCLATURE.md).

Goal: any future session in this repo can land on the right work, with the right context, in under five minutes — by reading CURRENT.md and the active handoff alone.

---

## Context

- Argus was scoped via a handoff document (`ARGUS_PROJECT_PLAN.md`-equivalent, delivered verbatim in Eurydice chat) on 2026-05-12.
- The project's first manual file (`18_100754_ general 1946-7_vol_2.pdf`) was already in the working directory before scaffold began. Other manual downloads were being copied in during scaffold.
- The GitHub repo (`https://github.com/EurydiceWrites/ARGUS`) existed but contained only `LICENSE`.
- The Anomaly Taxonomy project (sibling repo, same researcher) provided the reference scaffold pattern, hardened across ~6 months and 23 handoffs.

Eurydice's explicit request: replicate problem-statement grounding, workflow handoffs, note-taking mechanisms, and nomenclature, sized down to Phase-0 needs.

---

## Inputs

| File | Mode | Purpose |
|---|---|---|
| `C:/Users/shawn/OneDrive/Coding/Anomaly Taxonomy/CLAUDE.md` | read | Reference pattern for session-start protocol + Goal Grounding |
| `C:/Users/shawn/OneDrive/Coding/Anomaly Taxonomy/CURRENT.md` | read | Reference pattern for lean active-work pointer |
| `C:/Users/shawn/OneDrive/Coding/Anomaly Taxonomy/PROJECT_OVERVIEW.md` | read | Reference pattern for substantive project framing |
| `C:/Users/shawn/OneDrive/Coding/Anomaly Taxonomy/READING_GUIDE.md` | read | Reference pattern for curated index (decided not to replicate yet — too small a project) |
| `C:/Users/shawn/OneDrive/Coding/Anomaly Taxonomy/docs/WORKFLOW_PROTOCOL.md` | read | Reference pattern for standing rules + handoff format |
| `C:/Users/shawn/OneDrive/Coding/Anomaly Taxonomy/handoffs/_index.md` | read | Reference pattern for chronology table |
| `C:/Users/shawn/OneDrive/Coding/Anomaly Taxonomy/handoffs/H-018_filter_goal_reframe_2026-05-02.md` | read | Reference pattern for a closed handoff document |

Read-only perimeter (Rule 3) honored: no writes to the Anomaly Taxonomy directory.

---

## Working directory

`C:/Users/shawn/OneDrive/Coding/ARGUS/`

---

## Procedure

1. **Created directory structure** at root: `src/`, `taxonomy/`, `db/`, `notebooks/`, `docs/`, `handoffs/`. (`data/raw/{video,images,text}/` was already established in a prior step.)
2. **Wrote `CLAUDE.md`** at root — session-start reading order, Goal Grounding Protocol, build-order discipline, methodological principles.
3. **Wrote `CURRENT.md`** at root — lean pointer to H-001 as the active handoff, resume path for Phase 1, links to all major docs.
4. **Wrote `PROJECT_OVERVIEW.md`** at root — substantive question, what Argus is and is NOT, the data, build order, methodological scaffolding, folder map.
5. **Wrote `FUTURE_WORK.md`** at root — five-phase build plan with steps, open questions, and acceptance criteria per phase, plus cross-phase carry-forward questions and literature-to-survey list.
6. **Wrote `docs/WORKFLOW_PROTOCOL.md`** — Rules 1 through 5 plus standing conventions. Rule 1 carries the session-close checklist. Rule 6 (data variant naming) deferred until Argus has variants worth naming.
7. **Wrote `docs/NOMENCLATURE.md`** — core terms (tranche, item, manifest, provenance, media type, agency, tranche-dated capture), phase-specific provisional terms, what-this-doc-is-not, term-addition procedure.
8. **Wrote `handoffs/_index.md`** — newest-first table with H-001 in Closed (no Active row yet; next handoff opens with Phase 1).
9. **Wrote `handoffs/H-001_project_scaffold.md`** — this document, self-describing the scaffold work.
10. **Updated `README.md`** — already exists; will be refreshed to point at the new top-level docs as part of this commit.
11. **Committed atomically** with all new files + updated README + .gitignore in one commit, pushed to GitHub.

---

## Output

Files created or updated in this handoff:

| Path | Status |
|---|---|
| `CLAUDE.md` | new |
| `CURRENT.md` | new |
| `PROJECT_OVERVIEW.md` | new |
| `FUTURE_WORK.md` | new |
| `README.md` | updated (already existed from prior commit) |
| `docs/WORKFLOW_PROTOCOL.md` | new |
| `docs/NOMENCLATURE.md` | new |
| `handoffs/_index.md` | new |
| `handoffs/H-001_project_scaffold.md` | new (this file) |
| `src/` `taxonomy/` `db/` `notebooks/` | new (empty directories) |

---

## Acceptance criteria

- [x] A session opening this repo cold can read `CURRENT.md` → active handoff → `_index.md` and orient in under five minutes.
- [x] `CLAUDE.md` carries the Goal Grounding Protocol verbatim from the Anomaly Taxonomy lesson.
- [x] `PROJECT_OVERVIEW.md` distinguishes Argus from Anomaly Taxonomy explicitly and forecloses cross-contamination of scope.
- [x] `FUTURE_WORK.md` lays out Phases 1–5 with steps, open questions, and acceptance criteria per phase.
- [x] `WORKFLOW_PROTOCOL.md` codifies the session-close checklist as a single atomic-commit requirement.
- [x] `NOMENCLATURE.md` defines tranche, item, manifest, provenance, media type, and agency unambiguously.
- [x] All files committed atomically and pushed to GitHub.

---

## Do NOT

- Do **not** import Anomaly Taxonomy's data variant naming rule (Rule 6) until Argus has variants. Premature rule import is bureaucratic overhead.
- Do **not** carry over the Anomaly Taxonomy database schema, motif key, or any Bullard-specific apparatus. Argus's taxonomy will be designed from scratch in Phase 3.
- Do **not** start Phase 1 (archiver) in this handoff. Scaffold-only scope.

---

## Report back to Eurydice chat with

- Confirmation that all files in the Output table exist and the atomic commit landed.
- The git commit hash.
- The GitHub repo URL after push.
- Any deviations from the original scope (files added, removed, or scoped differently than the original plan).
- Concrete next step for the following session.
