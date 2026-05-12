# Argus — Working Protocol for Claude Code

This file is read automatically at the start of every Claude Code session in this project. The protocol below is **mandatory** and takes precedence over any default Claude Code behavior.

---

## Session Start: Read these files in order, BEFORE responding

Before responding to any user message — even a casual greeting like "hi" or "ready to keep going" — read these files in this order. This applies to every Claude Code session, every Cowork session, every chat session in this project. **If you skip this step, you will misroute work.**

### The reading order

1. **`CURRENT.md`** at project root — the lean entry point. Tells you the active handoff, where work is paused, and the immediate next step. *Don't try to absorb everything; just locate the active handoff and the resume path.*

2. **The active handoff** that `CURRENT.md` points to (e.g. `handoffs/H-001_*.md`). This has the full context for the current task — much more detail than CURRENT.md.

3. **`handoffs/_index.md`** — newest-first index of every handoff. **Cross-check against `CURRENT.md`'s "Last updated" date.** If the index has handoffs newer than CURRENT.md says was the last update, then **CURRENT.md is stale. Notify the user immediately** — staleness is a workflow failure, not something to route around. Read the most recent handoff in the index as the source of truth.

4. **`docs/WORKFLOW_PROTOCOL.md`** — read Rule 1 (the session-close checklist) **only if** the work you're about to do will create or close a handoff. The checklist is what prevents future stale-CURRENT.md failures.

### Why the three files

The discoverability layer is intentionally three files:

- `CURRENT.md` = lean, "what's now"
- `handoffs/_index.md` = scannable chronology
- `handoffs/H-###_*.md` = full source of truth per handoff

This separation prevents a single sprawling state document from accumulating stale claims hidden in it. (Lesson imported from the Anomaly Taxonomy project, where a 27KB single CURRENT.md hid stale state for weeks before it was caught.)

---

## Goal Grounding Protocol (mandatory)

Before starting any non-trivial planning or execution in this project — designing scrapers, building taxonomy categories, modifying the database, generating reports, proposing approaches — Claude **must**:

1. State the **immediate goal** (what we're doing right now, in one sentence)
2. State the **underlying purpose** (the bigger problem this work serves)
3. State **what success looks like** (the concrete criterion that tells us we're done)

**Then wait for the user's confirmation before proceeding to any execution.** If the user corrects any of the three, re-state with the correction and confirm again.

### Re-trigger condition

When the user pushes back on a specific case — *"I wouldn't classify that as X,"* *"this isn't right,"* *"wait, is that what we're after?"* — treat the pushback as a possible **goal-clarification moment**, not just an implementation issue.

**Action:** Stop work. Re-state the three items above. Reconfirm before continuing.

(Imported from Anomaly Taxonomy where a specific-case pushback was misread as a methodology problem and escalated into a four-hour rabbit hole. The user was actually naming the goal in concrete terms.)

### Trivial work exemption

Single-file edits with self-evident purpose (typo fixes, renaming a variable the user explicitly named, fixing an obvious bug) do not require the full protocol. Anything that involves:

- Writing or running a script
- Building a report or analysis
- Modifying data, schema, or taxonomy categories
- Making decisions that would be hard to reverse
- Proposing an approach to a multi-step task

…requires the protocol.

---

## Build-order discipline

This project has a fixed phase order (see `FUTURE_WORK.md`):

1. Archive
2. Survey
3. Design the taxonomy
4. Schema
5. Index and classify

**Don't skip phases.** No taxonomy design before survey. No schema before taxonomy. The phase order is sacred because the classification system is supposed to emerge from observed patterns, not be imposed in advance.

If a session is tempted to jump ahead ("we could design the schema now while archiving runs"), stop and check with the user. The temptation usually means the work is being shaped by an assumption that hasn't been tested against the data.

---

## Methodological principles

These carry forward from the Anomaly Taxonomy project's hard-won discipline:

- **No batch decisions without verification.** Every classification reviewed by the researcher.
- **Provenance tracking.** Every item traced to source URL, agency, tranche, and retrieval date.
- **Epistemic honesty.** Tier confidence. Label what's certain vs. interpreted. Don't claim ground-truth status for AI output.
- **Researcher is the human in the loop.** AI assists; researcher decides.
- **Document everything.** Decisions logged with rationale in the handoff chain.

---

## Project-specific context (will grow)

This is a new project. As feedback memories and conventions accumulate, they'll be linked from here.
