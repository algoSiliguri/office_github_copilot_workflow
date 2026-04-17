# Architecture Reference: GitHub Copilot Workflow

updated: 2026-04-17

This document describes the internal mechanics of the workflow system. It is the reference for system designers and skill maintainers — not for day-to-day use. For usage guidance, see WORKFLOW.md.

**Sync policy:** Updated in the same commit as any skill that changes its decision logic. WORKFLOW.md is not updated for internal mechanism changes.

---

## Execution Mode Decision Logic

The planner (`planning/SKILL.md`) sets execution mode when writing the plan. The executor reads the annotated mode and runs it. This separation keeps the execution skill simple; routing intelligence lives where the plan is made.

### Three-Tier Model

| Mode | File count baseline | Typical use |
|---|---|---|
| `inline` | ≤5 files, low risk | Small changes, well-understood modules |
| `phased-inline` | 6–12 files OR high risk | Most feature plans — checkpoint discipline without sub-agent cost |
| `phased-subagent` | >12 files | Large or context-heavy plans where fresh context per phase is required |

### Override Rules

Applied after the baseline, before writing the `> **Execution mode:**` line:
- ≤5 files + high risk/uncertain steps → escalate to `phased-inline`
- 6–12 tightly coupled, well-understood files, low complexity → downgrade to `inline`
- >12 files of trivial changes (e.g. rename across files) → may use `phased-inline`

### Risk Signals (escalate one tier if any are true)

- A step touches a module flagged `active` or `high-risk` in the codebase index
- A step requires resolving a decision conflict flagged during planning
- More than 3 steps in a phase are marked with "or equivalent" / "depending on current state"

### Justification Requirement

Every plan must include a one-sentence mode justification on the `> **Execution mode:**` line:
`> **Execution mode:** phased-inline — 8 files, auth module has high iteration risk`

---

## Phased-Inline Mechanism

`phased-inline` executes phases sequentially in the current session with no sub-agents. It is UX-identical to `phased-subagent` — same phase start format, same checkpoint format, same gate discipline. The engineer cannot distinguish the modes from the output.

**Phase start announcement (both phased-inline and phased-subagent):**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Phase [N] of [M] — [Phase name] — [N files] / [N steps]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Phase checkpoint format (both modes):**
```
Phase [N] complete — [Phase name]

Files changed:
  + [file] (created)
  ~ [file] (modified)

[Stage 1] Spec compliance: PASS | FAIL — [finding]
[Stage 2] Code quality: PASS | FAIL — [finding]

Test output:
[pasted output]

Review:
[exact questions from plan's Engineer review prompt]

Type `continue` for Phase [N+1], or describe a concern.
```

**Gate:** Hard. No auto-continue. On failure: "Phase [N] failed — use `/debug`. Type `retry phase [N]` when fixed."

**Trade-off vs phased-subagent:** phased-inline accumulates tool call history across phases. For plans near the 12-file upper boundary, late phases may have reduced context focus. At current plan sizes (≤40 steps) this is not a concern at 200k context; revisit if plans regularly exceed that.

---

## Sub-Agent Dispatch Protocol

Used only in `phased-subagent` mode. Each phase dispatches a fresh `@Implementation Agent` sub-session.

### Minimal Conventions Summary

Sub-agent prompts do not embed the full `conventions/SKILL.md`. Instead, a minimal summary is extracted at dispatch time:
```
--- CONVENTIONS ---
Test: [command]
Commit: [format]
Lint: [command or "none"]
Ticket: [format]
--- END CONVENTIONS ---
```

### Dynamic Injection Rules

Additional convention sections are injected only when phase steps match keyword patterns. The parent session scans step text before dispatch and appends matching sections after `--- END CONVENTIONS ---`:

| Keywords in step text | Section injected |
|---|---|
| error, exception, throws, catch, validate, validation | `## Error Handling` |
| endpoint, request, response, API, contract, status code | `## API Conventions` |
| migration, schema, table, query, database, model | `## Data Conventions` |
| Framework name matching a section header in conventions | That section |

If `conventions/SKILL.md` does not contain a matching section: no injection. No failure or warning.

**Design principle:** pull-based, not push-based. The parent scans and pushes only relevant sections. Sub-agents don't decide what they need — they receive what was determined relevant.

---

## Coverage Confidence Constraint Table

Coverage confidence is set by the context packet's `Coverage confidence:` field, or by the plan's `## Intelligence Context` block. It is a behavioral constraint, not metadata.

| Level | Behavior |
|---|---|
| `high` | **Prohibited** from reading files outside the context packet. Any step requiring an out-of-packet file read must stop and ask. |
| `medium` | Controlled one-hop expansion — may read files referenced by packet modules; no broad scanning. |
| `low` | **Required** to acknowledge the gap. Full codebase search available without restriction. |

Coverage level is surfaced at phase/session start: `Context: [high|medium|low] coverage — [behavior description]`

If no context packet exists for a phase: treat as `low`. The absence is always announced explicitly — never silent.

Coverage enforcement is identical across inline, phased-inline, and phased-subagent modes.

---

## Retrieval Integration Points

Retrieval is enforced at three entry points:

| Phase | Behavior |
|---|---|
| **Planning** (`planning/SKILL.md`) | Mandatory when index exists at any maturity above `low`. Skip requires documented justification. Plan must note: `Retrieval: ran | skipped — [reason]` |
| **Execution** (`execution/SKILL.md`) | Context packet check is mandatory. If not found: explicitly noted — "No context packet for phase [N]. Proceeding with full codebase search." Never silent. |
| **Brainstorming** (`brainstorming/SKILL.md`) | Intelligence scan always runs. When candidates found: surface before first question. When no candidates found: "Index has no match for this ticket area — starting without codebase context." Absence is visible. |

Retrieval enforcement does not apply to spec-writing, TDD, debugging, or verification — these operate on artifacts already produced.

---

## Review Checkpoint Anatomy

### Two-Stage Review

**Stage 1: Spec Compliance** — Does the diff match the plan? All listed files changed, no unlisted changes. If Stage 1 fails: agent fixes before showing checkpoint.

**Stage 2: Code Quality** — Only runs after Stage 1 passes. Tests test behaviour, conventions followed, no obvious issues the spec required.

### Stage Detail Rules

PASS is one line. FAIL is one line including the finding (what + where). No explanation, no suggestion — the engineer decides what to do with it.

Show exactly one Stage 1 line and one Stage 2 line — the applicable variant only.

### Gate Protocol

Hard gate: the agent does not proceed to the next phase without explicit `continue` from the engineer. No auto-retry on failure — engineer must invoke `/debug` and return with `retry phase [N]`.

---

## Inline Soft Checkpoints

Applied only in `inline` mode with ≥6 total steps.

Steps are grouped by file (all steps on one file = one group) or by natural dependency boundary. After each group:
```
— [group name] — [N steps complete]
Tests: [PASS / FAIL — summary line]
```

Soft checkpoints are informational. No gate. Agent proceeds automatically.

After all steps: one hard checkpoint (same format as phased checkpoint). This is the only gate in inline mode.

For inline plans with <6 steps: no soft checkpoints. Hard checkpoint at the end only.

---

## Session Hygiene Protocol

Start a new chat at every phase boundary. Each phase builds its context from scratch — a fresh session prevents stale assumptions from accumulating across phases.

Skills reference this protocol via their Handoff sections. The canonical definition lives here; skills do not duplicate it.

---

## Evolution Principles

- **Mechanisms replace rules.** A behavioral constraint enforced by artifact or file-based check is stronger than a convention in a document.
- **Simpler systems that scale.** Every addition must justify its complexity against the maintenance cost.
- **Every constraint must be enforceable** as an artifact or a file-based check — not a convention.
- **ARCHITECTURE.md is not aspirational.** It describes how the system actually behaves. If a skill implementation diverges, update one of them — not both to stay in sync with a future state.
