# Workflow Cheat Sheet

Quick reference for day-to-day use. For full explanations see WORKFLOW.md; for system mechanics see ARCHITECTURE.md.

---

## Commands

| Command | When |
|---|---|
| `/setup` | Once per repo — auto-detects stack, writes `conventions/SKILL.md` |
| `/brainstorm` | Start every feature ticket |
| `/write-spec [brainstorm-path]` | After brainstorm approved |
| `/write-plan [spec-path]` | After spec approved |
| `/context-packet [ticket] [phase-N]` | V1 only: after plan, before execution — phased + ≥4 files. Auto-triggered in v2. |
| `/execute-plan [plan-path]` | After plan approved |
| `/tdd` | Inside execute, when writing new logic |
| `/debug` | Inside execute, when a test fails |
| `/verify [spec-path]` | After all phases complete |
| `/review [verification-path]` | After verification |
| `/quick-task` | Trivial bugfix or config change — skips brainstorm + spec |
| `/index codebase` | After setup, or when code structure changes significantly |
| `/index knowledge` | Before a large ticket (full run) |
| `/index knowledge --incremental` | After every ticket closes; when stale warning appears in packet; when execution ends with ≥3 knowledge candidates |
| `/validate-artifact [path]` | Debug v2 artifacts — checks schema, integrity, invariants (runs silently inside each skill) |

---

## Execution Modes

| Mode | When | Checkpoints |
|---|---|---|
| `inline` | ≤5 files, low risk | 1 hard gate at end |
| `phased-inline` | 6–12 files or high risk (default) | Hard gate after each phase |
| `phased-subagent` | >12 files | Hard gate after each phase, fresh sub-session per phase |

Mode is set by the planner, not chosen by the engineer. Justification is required on the execution mode line.

---

## Knowledge Topic Page Schema

```
_Type: [system|empirical|external|operational|meta] | Modules: [...] | Weight: HIGH|MEDIUM|LOW | Recurrence: N | Status: [flags]_
_Validity: [valid|stale|questionable|superseded] | Last validated: [YYYY-MM-DD|—]_

## Summary
## Provenance
  - Source: `artifact path`
  - Evidence: data or observations
  - Validated by: ticket or artifact — or "—"
## Relationships        ← omit if none
  - contradicts: [[topic]] — specific conflict description
  - supersedes: [[topic]] — what changed
  - supports: [[topic]] — how it reinforces (manual only)
  - derived_from: [[topic or artifact]] — derivation context (manual only)
## Pattern             ← omit until confirmed by engineer
## Entries
  - YYYY-MM-DD TICKET-ID | source-type | Weight | description
## Related Modules
  - [`Module`](../codebase/module.md) — one sentence
```

---

## Knowledge Layer: Who Owns What

| Component | Owns |
|---|---|
| `index-knowledge` | Type inference · contradiction detection · validity transitions · relationship writing |
| `retrieval-protocol` | Filtering · ranking · exclusion · budget |
| `context-packet` | Assembly and display only — reads, never writes |

---

## Validity States

| State | Meaning | How set | How cleared |
|---|---|---|---|
| `valid` | Trustworthy | Default on creation; manual reset after re-validation | — |
| `stale` | Decay trigger met — revalidate before relying | Auto by index-knowledge incremental | Manual: update Last validated, set valid |
| `questionable` | Conflicting evidence detected | Auto when contradiction stub written | Manual: resolve conflict, set valid |
| `superseded` | Replaced by a newer topic | Manual (+ write supersedes ref on new topic) | Never — excluded from retrieval permanently |

---

## Relationship Rules

| Type | Written by | Effect in retrieval |
|---|---|---|
| `contradicts` | index-knowledge (auto) | Conflict section in packet; one-hop expansion |
| `supersedes` | index-knowledge (auto) | Old topic excluded from retrieval |
| `supports` | Engineer only | Informational only |
| `derived_from` | Engineer only | Cluster logic; lineage label in packet |

`## Relationships` section is **omitted** from topic pages when no relationships exist.

---

## Retrieval Exclusion Rules (applied before ranking)

1. `validity=superseded` → always excluded
2. `type=empirical or operational` + `Recurrence=1` + `validity=stale` + no BLOCKER → excluded (`system`/`external`: load with ⚠️ STALE instead)
3. Stale side of a contradiction where the other side is valid → load only the valid side

Type priority within same weight tier: `bug-fix/modification` → empirical › system › external. `new-feature` → system › empirical › external.

---

## Context Packet Signals

**Stale signal warning** — appears in `## Knowledge Signals` when ≥2 loaded topics are stale:
> ⚠️ N stale signals in scope — run `/index knowledge --incremental` to refresh before relying on this packet.

**Conflicting signals section** (`## Conflicting Signals`) — appears before `## Knowledge Signals` when both sides of a `contradicts` pair are loaded. Shows summaries, types, validity side by side. Includes escalation label when types conflict:
- empirical (valid) ↔ system (valid) → ⚠️ ENGINEER DECISION REQUIRED
- empirical (valid) ↔ empirical (valid) → ⚠️ CONFLICTING EVIDENCE

No conflict count warning. No provenance warning.

---

## Contradiction Detection Guard (index-knowledge Step 6)

Auto-writes `contradicts` stubs only when ALL gates pass:

1. **Specificity** — description names a concrete parameter, value, or contract (not a general tension)
2. **Signal strength** — at least one topic HIGH, or both MEDIUM+
3. **Per-run cap** — max 3 new stubs per run; excess logged, not written

Self-review pass: each description re-read once before writing. Stubs that can't answer "what specific thing conflicts?" are removed.

---

## Execution Signals (Automatic)

These appear during and at the end of every execution session without any command.

**During execution — Codebase Search Protocol (Step 0):**
Before any module is explored, one of three signals fires:
- *Context packet covers this module* → no signal (suppressed)
- *Knowledge file exists* → `Context reuse signal: This module has prior structured knowledge: [1-line summary]`
- *Neither* → `Context reuse signal: No prior structured knowledge available for this module.`

**Between phases (phased-inline) — Context Reset Block:**
Appears after you type `continue`. Summarizes completed phase outcomes and forward state. Directs the executor to treat prior phase details as non-authoritative.

**At session end — Reflection blocks (all modes):**
Appear before finishing options in this order:
1. `--- Context Quality Review ---` — coverage, issues, whether a packet would have helped
2. `--- Knowledge Candidates ---` — up to 5 high-signal learnings; if ≥3 strong candidates → run `/index knowledge --incremental`
3. `Plan stability:` — Stable / Minor drift / Major drift

---

## Hard Rules (cannot be skipped)

1. No implementation before a plan exists
2. No "done" without running tests — paste actual output, never claim
3. No PR without a verification file
4. Retrieval is mandatory at planning when index maturity is `medium` or `mature` — skip requires explicit documented justification
5. New chat at every phase boundary

---

## V2 Artifact Primitives (schema_version: 2)

_New tickets only, after all six skills are upgraded. Full types in `.github/skills/SCHEMA.md`._

| Primitive | Produced by | Key fields |
|---|---|---|
| `ProblemRecord` | brainstorming | `id`, `classification` (new-feature/modification/bug-fix), `scope[]`, `acceptance_signals[]` |
| `DecisionRecord` | spec-writing | `id` (D1...), `chosen`, `rejected[min:1]`, `constraints[]`, `reversibility` (low/medium/high) |
| `Requirement` | spec-writing | `id` (R1...), `text`, `acceptance` (runnable command), `classification`, `source_decision?` |
| `StepNode` | planning | `id` (P1.S1...), `files[]` (path+operation), `verify` (command), `review_prompt`, `requirement_ids[]` |

**Inheritance:** each artifact carries all upstream fields verbatim + adds its own. No re-parsing at phase boundaries.

**Stage 1 (v2):** exact `StepNode.files` vs `git diff`. Grace: files matching `conventions: Incidental file patterns` that are not in any StepNode and are not deletions → logged, not a failure.

**Schema evolution:** adding optional fields = non-breaking. Adding required fields, removing fields, changing types = bump to `schema_version: 3`.

---

## System Philosophy

- **File-native** — no runtime dependencies, no external services; all intelligence is Markdown
- **Relationships enable reasoning, not storage** — a topic without relationships is valid; relationships exist to surface contradictions and lineage, not to build an ontology
- **Minimal schema, high signal** — every schema field is read by retrieval or displayed in packets; unused fields are not added
- **Mechanisms replace rules** — discipline enforced by artifacts and file-based checks is stronger than conventions in documents
