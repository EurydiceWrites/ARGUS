# CURRENT — Argus

**Last updated:** 2026-05-12 (project scaffold complete)
**Active handoff:** [handoffs/H-001_project_scaffold.md](handoffs/H-001_project_scaffold.md) — closed; next handoff opens with Phase 1

---

## ACTIVE WORK — Read this section first

**Where we are:** Project initialized. Repo connected to GitHub (`EurydiceWrites/ARGUS`). Directory structure built. Working protocol, project overview, workflow rules, nomenclature, and forward roadmap all on disk. One manually-downloaded PURSUE PDF sits in `data/raw/text/` awaiting the proper archiver. The researcher is currently bulk-loading the rest of the manual downloads into `data/raw/video/`, `data/raw/images/`, `data/raw/text/`.

**Phase status:** Phase 0 (scaffold) complete. Phase 1 (archive) not yet started.

**Concrete resume path (next session):**

1. Confirm the researcher has finished bulk-loading manual downloads into `data/raw/`.
2. Run an inventory script: count files per media-type bucket, size, formats. Surface what's there before designing anything.
3. Fetch `war.gov/UFO` and inspect what's published — URL structure, file types, tranche organization, whether there's a manifest.
4. Open H-002 for the Phase 1 archiver design. Apply the Goal Grounding Protocol before writing code.

**Do not jump ahead** to taxonomy design (Phase 3) or schema (Phase 4). The build order is sacred — see `CLAUDE.md` and `FUTURE_WORK.md`.

---

## Working protocol (mandatory)

The **Goal Grounding Protocol** is active for this project. Before any non-trivial work, state (1) immediate goal, (2) underlying purpose, (3) success criterion, then wait for user confirmation. See [CLAUDE.md](CLAUDE.md).

**Session-close discipline:** Closing a handoff means updating CURRENT.md (this file), `handoffs/_index.md`, and committing all three (the new handoff doc + both updates) in a single commit. See [docs/WORKFLOW_PROTOCOL.md](docs/WORKFLOW_PROTOCOL.md) Rule 1.

---

## Recent handoffs (most recent first — full list at [handoffs/_index.md](handoffs/_index.md))

| ID | Date | Status | Summary |
|---|---|---|---|
| **[H-001](handoffs/H-001_project_scaffold.md)** | **2026-05-12** | **Closed — Project scaffold built. README, CLAUDE.md, CURRENT.md, PROJECT_OVERVIEW.md, FUTURE_WORK.md, WORKFLOW_PROTOCOL.md, NOMENCLATURE.md, handoffs/_index.md, H-001 itself. Directory structure (src/taxonomy/db/notebooks/docs/handoffs/) created. Data folder split into video/images/text buckets, gitignored.** |

---

## Where to find more

| If you want... | Read this |
|---|---|
| The big-picture project framing | [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) |
| The phase-by-phase build plan | [FUTURE_WORK.md](FUTURE_WORK.md) |
| Standing operational rules | [docs/WORKFLOW_PROTOCOL.md](docs/WORKFLOW_PROTOCOL.md) |
| Vocabulary (tranche, item, manifest, etc.) | [docs/NOMENCLATURE.md](docs/NOMENCLATURE.md) |
| Working protocol for Claude sessions | [CLAUDE.md](CLAUDE.md) |
| Newest-first index of all handoffs | [handoffs/_index.md](handoffs/_index.md) |
