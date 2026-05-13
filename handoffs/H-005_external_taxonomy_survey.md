# H-005 — External taxonomy survey (Hynek / Vallée / AARO / GEIPAN / SCU)

**Date:** 2026-05-12
**Decided in:** Eurydice chat (post-H-004a close, same Cowork session)
**Author:** Eurydice
**Status:** Closed — executed in Eurydice chat session (atomic open + close)

---

## Task

Produce a short reference document at `notebooks/existing_taxonomies.md` summarizing how five major UAP research systems classify cases: J. Allen Hynek (1972), Jacques Vallée (1990), GEIPAN (1977–present), AARO (2022–present), and the Scientific Coalition for UAP Studies (2017–present).

The output is **not** a recommendation for Argus's taxonomy. It is the vocabulary input that Phase 3 will draw from when designing taxonomy v1, so that the eventual Argus taxonomy either reuses existing categories deliberately or departs from them deliberately — never accidentally.

---

## Context

This handoff opens immediately after H-004 / H-004a close (filename metadata extractor for DOW/DOS/NASA; 55/157 manifest rows enriched). It is the second piece of Phase 3 preparation under the **Path B sequenced-hybrid strategy** committed to in Eurydice chat on 2026-05-12.

H-005 differs from H-001 through H-004a in one important way: **it is desk research, not script work.** It is executed in the Eurydice chat session itself rather than handed off to Claude Code. Per WORKFLOW_PROTOCOL Rule 4 the handoff doc is still written (this file) as the audit-trail record of the work, and the open spec + closure section are committed together in a single atomic commit (same pattern as H-004a, since the work happens in one sitting).

The user requested **short write-ups** ("~10-minute read"), not deep academic-paper-level depth. Five systems in scope. Mack's clinical typology (relevant via the user's parallel Anomaly Taxonomy project) was deliberately excluded on user direction and can be revisited in a follow-up if useful.

---

## Inputs

| Path | Mode | Purpose |
|---|---|---|
| (no project file) | n/a | This is desk research — no Argus file is read or modified; the output is a new notebook |

External sources used: training-knowledge primary sources for historical systems (Hynek, Vallée), and web research for current state of modern systems (AARO, GEIPAN, SCU). Full citation list in the Sources section of `notebooks/existing_taxonomies.md`.

---

## Working directory

`C:/Users/shawn/OneDrive/Coding/ARGUS/`

---

## Procedure

1. Confirm scope with the researcher: five systems (Hynek, Vallée, AARO, GEIPAN, SCU), short write-ups (~10-minute total read), no additional systems.
2. For each system, gather and write: who, when, unit of classification, the actual categories used, strengths, weaknesses. Use training knowledge for established historical systems; use web research (search retrieval 2026-05-12) for current state of modern systems.
3. Write `notebooks/existing_taxonomies.md` with: purpose statement; one section per system; a synthesis section identifying recurring axes and axes unique to one or two systems; explicit observations for Phase 3 (observations, not recommendations); open questions to carry forward into Phase 3; sources in Chicago author-date format.
4. Cite all factual claims. Where a citation is uncertain (e.g., the original publication venue of Vallée's AN / FB / MA / CE typology), state the uncertainty explicitly rather than guess.
5. Append the closure section to this handoff doc and update CURRENT.md and `handoffs/_index.md` per Rule 1.

---

## Output

- `notebooks/existing_taxonomies.md` — the survey notebook.

---

## Acceptance criteria

- [ ] All five systems covered with: who, when, unit, categories, strengths, weaknesses.
- [ ] Synthesis section identifies recurring axes and axes unique to one or two systems.
- [ ] Open questions for Phase 3 carried forward.
- [ ] Citations in Chicago author-date format; no fabricated sources.
- [ ] Uncertainty explicitly marked where present (not glossed).
- [ ] Total length suitable for ~10-minute read (target 1,500–2,500 words).

---

## Do NOT

- Do not propose Argus taxonomy categories. Phase 3 is downstream of this handoff.
- Do not fabricate citations or invent publication venues. Where a source is uncertain, mark it.
- Do not pretend AARO or SCU has a Hynek-style formal taxonomy if they don't — accurately characterize each system's actual approach, even when that approach is "no single formal framework."
- Do not import Mack's clinical typology in this pass; explicitly out of scope per user direction.

---

## Report back to Eurydice chat with

- Confirmation each of the five systems is covered.
- Any system where the survey couldn't find a clean classification framework (so the researcher knows what's a real finding vs. a literature gap).
- Any source where citation uncertainty was marked.
- Concrete next-step recommendation.

---

## Closure — 2026-05-12

**Status:** Closed.
**Executed by:** Eurydice (Cowork chat session — no Claude Code involvement).
**Output:** `notebooks/existing_taxonomies.md` (~2,000 words; readable in ~10 minutes).

### Acceptance criteria — final

- [x] All five systems covered with: who, when, unit of classification, categories, strengths, weaknesses.
- [x] Synthesis section identifies recurring axes (distance / proximity, physical evidence / sensor confirmation, occupants, anomalous flight, resolution status) and axes unique to one or two systems (reality-transformation, data-quality grading, military-specific behaviors).
- [x] Open questions for Phase 3 carried forward (four questions; see notebook).
- [x] Sources cited in Chicago author-date format.
- [x] Uncertainty explicitly marked where present.
- [x] Total length ~2,000 words (10-minute read).

### Report back — required items

**1. Coverage confirmation.** All five systems covered. Notable finding: AARO and SCU do not have a single formal classification framework comparable to Hynek's CE-1 / 2 / 3 system. Their entries accurately characterize what they *do* have — AARO's resolution-status classification plus descriptive shape labels, SCU's nine-type behavioral typology — rather than inventing a framework they don't actually use. The absence is itself a finding worth carrying into Phase 3.

**2. Literature gaps surfaced.** AARO does not publish a formal taxonomic-axes document; their categorization is operational rather than scholarly. SCU's nine activity types are derived from their research output but are not formalized in a single canonical document — different SCU publications use slightly different cuts of the data. Both gaps are flagged in the relevant system sections of the notebook.

**3. Citation uncertainty marked.** One instance: the Vallée AN / FB / MA / CE × 1–5 typology is attributed to *Confrontations* (1990) with an explicit researcher-verify caveat. The typology appears across several of Vallée's publications and the original venue is not certain from the sources I had access to. Flagged as uncertain rather than guessed.

**4. Concrete next-step recommendation.**

- **Phase 3 — Taxonomy design** is now unblocked. With H-004 / H-004a closed (clean ~55-item subset enriched with structured metadata) and H-005 closed (vocabulary in hand), Phase 3 can open. Suggested entry point: read the ~55 clean DOW / DOS / NASA cases, extract incidents, observe what categories recur, draft taxonomy v1 grounded in the actual archive. The four open questions in the notebook synthesis are design prompts, not constraints.
- **H-006 (queued, not blocking)** — war.gov page parse to refine `source_url` and surface metadata not present in filenames. Useful before Phase 5 indexing; not blocking Phase 3.

### Design decisions not specified in the handoff (per Rule 5)

1. **Synthesis is observation, not recommendation.** The synthesis section surfaces "three camps" (what-the-witness-saw, what-the-object-did, how-well-we-can-explain-it) and the axes that recur across systems, but does not recommend which Argus should adopt. Per the Eurydice operating rule: the researcher has final authority on taxonomy design.

2. **Open questions carried forward, not closed.** Four open questions are surfaced in the notebook for Phase 3 to engage with. None are answered here. Answering them now would pre-commit Phase 3 to a frame this survey is not entitled to set.

3. **Vallée citation marked uncertain rather than fabricated to confidence.** The typology itself is real and widely cited; the original publication venue I was less sure of from the sources at hand. Per project discipline, uncertainty stated clearly is more valuable than false confidence.

### Audit trail

- `notebooks/existing_taxonomies.md` — created.
- `handoffs/H-005_external_taxonomy_survey.md` — this file; open spec + closure committed atomically.
- `CURRENT.md` — updated (H-005 closed; Phase 3 unblocked; H-006 queued but not blocking).
- `handoffs/_index.md` — H-005 added to top of Closed; Active section reset to none.

All in a single atomic close commit per Rule 1.

---

## Post-close edits (audit trail, appended 2026-05-12)

After this handoff closed, the following session work touched H-005's deliverable and the surrounding Phase 3 prep work. Recorded here so the audit trail is complete; H-005's closed status is unchanged.

### Edits to `notebooks/existing_taxonomies.md`

- "Methodological note on AARO" added to section 4. AARO releases are treated as primary-source data, usable as raw material for independent analysis; AARO classifications are **not adopted as ground truth**.
- "Methodological asymmetry — AARO" subsection added to the synthesis. AARO is treated differently from the other four systems — as a data source under critical analysis, not a classification source to draw from.

### Adjacent files created in the same session (downstream of H-005, not part of its original scope)

- `notebooks/reading_list_taxonomies.md` — primary-source reading list for the five surveyed systems. Produced after the researcher elected to read primaries directly rather than rely on the survey synthesis. The H-005 notebook is explicitly framed in the reading list as "a rough starting map" rather than a vetted reference.
- `notebooks/observations.md` — working notebook for the researcher's observe-first Phase 3 prep.

### Phase 3 method committed (researcher decision)

The researcher has set Phase 3 method to **observe-first, reconcile-later**: read source material directly and record observations without pre-imposed framework; reconcile against existing classification systems only afterward. This inverts H-005's original "vocabulary before invention" framing. The existing-taxonomies notebook becomes **comparison ground, not prerequisite**. The shift is consistent with the CLAUDE.md principle that "the classification system is supposed to emerge from observed patterns, not be imposed in advance."
