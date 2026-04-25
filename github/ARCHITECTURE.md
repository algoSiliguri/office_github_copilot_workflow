# Architecture Reference: GitHub Copilot Workflow

updated: 2026-04-17

Internal mechanics of the workflow system. Written for skill maintainers and system designers — not for day-to-day use. For usage guidance, see WORKFLOW.md.

**Sync policy:** Updated in the same commit as any skill that changes its decision logic.

---

## Why This System Exists: LLM Stateless Constraints

Five constraints apply to any multi-phase workflow built on stateless LLM agents. These are platform constraints, not design choices — they apply regardless of agent framework, IDE, or prompt strategy.

**C1 — Stateless execution:** No information persists across phase boundaries unless explicitly written to a file and reloaded. Every session and sub-agent is a cold start. Context is carried forward through artifacts, not memory.

**C2 — Weak artifact contracts:** Phase outputs are human-readable but not deterministically consumable by the next phase. Without defined schemas, the next agent reinterprets instead of executes — introducing variance at every boundary.

**C3 — No native retrieval:** Agents cannot discover relevant knowledge autonomously. Only explicitly referenced files enter context. Prior work, indexed knowledge, and accumulated patterns are invisible unless surfaced.

**C4 — Context loading inefficiency:** Each phase rebuilds understanding by re-reading files from scratch. No caching, no incremental reuse, no scoping. Cost scales with repo size and phase count.

**C5 — Limited execution control:** Agents can only guide behavior through prompts. Any discipline that cannot be expressed as an artifact or file-based check is convention, not structure.

Every mechanism in this system addresses one or more of these constraints directly.

---

## Invocation Model

The system separates capabilities into two categories: automatic and explicit.

### Automatic Capabilities

These are embedded inside phase execution and cannot be invoked directly:

- **Retrieval protocol** — triggered during planning when index maturity is `medium` or `mature`
- **Decision conflict check** — runs inside spec-writing and planning; blocks progress on unresolved conflicts
- **TDD** — triggered during execution when writing new logic
- **Debugging** — triggered when execution encounters test failures

These operate as internal mechanisms, not user-facing commands. They enforce discipline without requiring the user to remember to call them.

### Explicit Capabilities

These must be invoked manually:

- **Phase commands** — brainstorm, spec-writing, planning, execution, verification, review
- **Indexing** — `/index codebase` and `/index knowledge` build the retrieval layer; they are preconditions for retrieval quality, not optional utilities
- **Context preparation** — `/context-packet` must be invoked between planning and execution when conditions are met

### Design Principle

Automatic capabilities enforce system discipline.
Explicit capabilities give the user control over state and context.

Confusion arises when explicit steps are not surfaced clearly — especially `/context-packet` and indexing. These are not passive; they determine retrieval quality and execution discipline for everything that follows.

---

## Execution Mode Decision

The planner sets execution mode when writing the plan. The executor reads the annotated mode and runs it. Routing intelligence lives at planning time — execution is mechanical.

### Three-Tier Model

| Mode | File count baseline | Typical use |
|---|---|---|
| `inline` | ≤5 files, low risk | Small changes, well-understood modules |
| `phased-inline` | 6–12 files OR high risk | Most feature plans — checkpoint discipline without sub-agent cost |
| `phased-subagent` | >12 files | Large plans where fresh context per phase is needed |

File count defines the default baseline. Final execution mode is determined after evaluating complexity, coupling, and risk signals — file count alone is never sufficient justification. This is not a user choice. The mode is set by the planner, annotated in the plan, and announced by the executor.

### Override Rules (applied after baseline)

- ≤5 files + high risk/uncertain steps → escalate to `phased-inline`
- 6–12 tightly coupled, well-understood files → may downgrade to `inline`
- >12 files of trivial changes (e.g. mass rename) → may use `phased-inline`

### Risk Signals (escalate one tier if any are true)

- A step touches a module flagged `active` or `high-risk` in the codebase index
- A step requires resolving a decision conflict flagged during planning
- More than 3 steps in a phase are marked "or equivalent" / "depending on current state"

### Justification Requirement

Every plan must include a one-sentence justification on the execution mode line:

`> **Execution mode:** phased-inline — 8 files, auth module has high iteration risk`

The justification must be meaningful — it should state the actual risk or complexity signal, not just echo the file count. "8 files" is not a justification. "8 files, auth module flagged active-risk" is. This makes routing auditable before execution begins.

---

## Execution Mechanics

### Inline Mode

All steps run sequentially in the current session. Tests run after each step. No sub-agents.

**Soft checkpoints** (only if total steps ≥6): after each file-group, informational — no gate, proceeds automatically. Soft checkpoints are informational only and must not introduce execution pauses:

```
— [group name] — [N steps complete]
Tests: [PASS / FAIL — one-line summary]
```

**Hard checkpoint**: one gate at the end of all steps. Same format as phased checkpoints. Engineer must confirm or raise a concern before finishing options are presented.

For plans with <6 steps: no soft checkpoints. Hard checkpoint at the end only.

### Phased-Inline Mode

Phases execute sequentially in the current session. No sub-agents. UX is identical to phased-subagent — same phase start format, same checkpoint format, same gate discipline. The engineer cannot distinguish the modes from the output.

**Phased-inline is the default execution strategy for most real-world feature development.** Inline is an optimization for small, well-scoped tasks; phased-subagent is an isolation mechanism for large plans. When in doubt, the planner should default to phased-inline.

**Why phased-inline exists:** Sub-agent overhead requires packaging everything a sub-agent needs into a self-contained prompt — conventions summary, context packet, step list, rules. For 6–12 file plans, this overhead exceeds the benefit of fresh context. Phased-inline gives checkpoint discipline and review gates at lower cost. Context accumulates across phases in the session. To mitigate this, a context reset block is emitted between phases when the engineer types `continue` — a brief inline summary that explicitly scopes what to carry forward and what to discard, directing the executor to treat prior phase details as non-authoritative.

### Phased-Subagent Mode

Each phase dispatches a fresh `@Implementation Agent` sub-session with a fully self-contained prompt. The sub-session has no access to the parent session.

**Lean conventions summary** (not the full `conventions/SKILL.md`):

```
--- CONVENTIONS ---
Test: [command]
Commit: [format]
Lint: [command or "none"]
Ticket: [format]
--- END CONVENTIONS ---
```

**Dynamic injection:** Relevant sections from `conventions/SKILL.md` are dynamically injected based on step requirements (e.g. error handling, API conventions, data conventions). The parent session scans step text before dispatch and appends matching sections — pull-based, not push-based. If a matching section does not exist in conventions: no injection, no warning.

**Fallback:** If sub-agents are unavailable, the system falls back to `phased-inline` automatically.

### Codebase Search Protocol

Before any module exploration during execution, the executor runs a knowledge state check (Step 0). Three-tier logic, first match wins:

1. **Context packet covers module** (exact name match in `## Module Context`) → no signal; proceed to search
2. **`[KNOWLEDGE_PATH]/[module].md` exists** → emit reuse signal with 1-line summary from `## Summary`
3. **Neither** → emit gap signal noting the module has no prior structured knowledge

Signal is informational only — never blocks execution. One signal (or none) per module. Classifies knowledge state, not behavior: surfaces what is known, what is being re-derived, and what is not yet captured.

### Execution-End Reflection Blocks

After the full test suite passes in all three modes, three reflection blocks appear before finishing options:

**Context Quality Review** — retrospective on context sufficiency: coverage level (High/Medium/Low), issues encountered (missing context, irrelevant context, misleading assumptions), and whether a context packet would have helped.

**Knowledge Candidates** — high-signal learnings from execution: new patterns, undocumented constraints, repeated ambiguity, workarounds that required reasoning. Max 5 items. Not auto-saved — candidates for future `/index knowledge` runs. If ≥3 strong candidates are listed, the system recommends running `/index knowledge --incremental`.

**Plan Stability** — single-line signal: `Stable` (no amendments) / `Minor drift` (1–2 amendments, no core logic change) / `Major drift` (core approach changed or multiple phases amended). Surfaces planning quality issues for upstream improvement.

Order: Context Quality Review → Knowledge Candidates → Plan Stability → finishing options. Present in all modes (inline, phased-inline, phased-subagent). In phased-subagent mode, these blocks run in the parent session after all phases complete — not inside sub-agent prompts.

---

## Review Checkpoint Anatomy

### Phase Start Announcement (phased modes only)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Phase [N] of [M] — [Phase name] — [N files] / [N steps]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Two-Stage Review

**Stage 1: Spec Compliance** — Does the diff match the plan? All listed files changed; no unlisted files changed. If Stage 1 fails: agent fixes before showing the checkpoint.

**Stage 2: Code Quality** — Only runs after Stage 1 passes. Tests test behaviour; conventions followed; no obvious issues the spec required.

Both stages run internally. The engineer always sees the outcome of both stages in the checkpoint — internal execution ensures correctness before surfacing; surfaced output ensures visibility and auditability.

### Checkpoint Format

```
Phase [N] complete — [Phase name]

Files changed:
  + [file] (created)
  ~ [file] (modified)

[Stage 1] Spec compliance: PASS

Plan listed:
- <file1>

Actually changed:
- <file1>

[Stage 2] Code quality: PASS

Test output:
[pasted terminal output — not a summary]

Plan changes this phase:
- none OR [1-line summary of any ## Amendments entry written during this phase]

Decisions & Assumptions: [subagent mode only — omit in phased-inline]
[bullets from sub-agent, or "None"]

Review:
[exact questions from the plan's Engineer review prompt for this phase]

Type `continue` for Phase [N+1], or describe a concern.
```

Stage 1 always shows Plan listed and Actually changed — the engineer can verify compliance directly against their git diff without relying on the agent's verdict. On FAIL, an Unlisted section is added. Stage 2 remains one line (PASS or FAIL with finding). No explanation, no suggestion in either.

**Plan changes this phase:** Surface any `## Amendments` entries tagged with the current phase. Omit the field when empty is not an option — write "none". This makes plan mutations visible at checkpoint time without requiring the engineer to re-read the plan file.

**Decisions & Assumptions (phased-subagent only):** Sub-agents are required to return a `Decisions & Assumptions` field listing only cases where multiple valid implementations existed, ambiguity required a judgment call, or behavior was inferred rather than specified. Max 5 bullets. Omitted when execution was mechanical. This surfaces hidden reasoning that would otherwise be invisible to Stage 1, Stage 2, and the engineer.

**Gate:** Hard. No auto-continue. On test failure or Stage 1 failure: "Phase [N] failed — use `/debug`. Type `retry phase [N]` when fixed." Retry counter per phase capped at 2 retries; on third failure the phase transitions to EXECUTION BLOCKED state requiring plan amendment or abort. No auto-retry.

---

## Verification Gate

The iron law: no claim of "tests pass" without pasted terminal output as evidence.

Before claiming any of the following — "step complete", "phase complete", "all tests pass", "full suite green":

1. **Identify** the exact command that proves the claim.
2. **Run** it — fresh execution, not cached output.
3. **Read** the full output including exit code.
4. **Claim** with the pasted evidence.

Rejected: "should pass", "probably works", "tests passed" (without output). Evidence is pasted terminal output — nothing else counts.

---

## Retrieval Integration

The retrieval intelligence layer addresses C3 (no native discovery) through structured Markdown indexes that agents explicitly load.

### Maturity Gate

| Module count | Maturity | Effect |
|---|---|---|
| < 10 | `low` | Retrieval skipped; fall back to codebase search protocol |
| 10–30 | `medium` | Retrieval activates |
| > 30 | `mature` | Retrieval activates |

Thresholds are configurable per repo in `conventions/SKILL.md` (`Maturity threshold:`). The defaults above apply when set to `default`.

### Per-Phase Integration

| Phase | What happens |
|---|---|
| **Brainstorm** | Silent intelligence scan: read codebase index, identify candidate modules and HIGH-weight knowledge signals, frame opening question around findings. When no candidates found: state "Index has no match for this area — starting without codebase context." Absence is always stated, never silent. No module pages loaded — index only. |
| **Spec-writing** | Decisions-only check: read `## Decisions` sections from relevant module pages; compare against the spec's architectural choices; flag conflicts. A conflict must be resolved before the spec is completed. No full page loads beyond the Decisions section. |
| **Planning** | Full retrieval: load module pages + knowledge pages within budget; run decision conflict check; order phases by signal weight. Mandatory when index maturity > `low`. A skip without documented justification blocks the plan from being written. |
| **Execution** | Context packet only. No additional index access during execution. All module and knowledge context was pre-assembled in the packet. |

### Loading Budget (hard limits — never exceeded)

| Phase | Module pages | Knowledge pages | Expansion allowed |
|---|---|---|---|
| Planning | 3 | 2 | +1 module, +1 knowledge |
| Brainstorming | 0 (index-only scan) | 0 | None |
| Spec-writing | 0 (Decisions section only) | 0 | None |
| Execution | Via context packet only | Via context packet only | None |

Budget exhaustion stops loading. No additional reads are taken under uncertainty — remaining uncertainty is resolved during execution via codebase search.

### Ticket-Type Loading Split (within planning budget)

The brainstorm artifact's Problem section is classified by first-match keyword:

| Ticket type | Module pages | Knowledge pages |
|---|---|---|
| `new-feature` | 3 | 1 |
| `modification` | 2 | 2 |
| `bug-fix` | 1 | 2 |

Unused slots are not filled speculatively.

### Retrieval Annotation in Plans

Every plan notes retrieval outcome:

`> **Retrieval:** ran | skipped — [reason]`

Retrieval is mandatory when index maturity is `medium` or `mature`. A skip must be explicitly justified — it is treated as a failure condition, not a soft warning. A plan that skips required retrieval without documented justification is considered incomplete and must not proceed to execution.

---

## Context Packet Behavior

Context packets pre-assemble execution context for a specific ticket phase, written after the plan is finalized and before execution begins.

### Trigger Conditions (default — all three should be true)

1. Codebase index maturity is `medium` or `mature`
2. Plan execution mode is `phased` (not `inline`)
3. Phase has ≥ 4 files

These are the default trigger conditions, not a hard gate. The planner or executor may still generate or use a context packet for phases with fewer files when complexity is high or retrieval signals are strong. If default conditions are not met and no packet is generated, the phase uses the codebase search protocol.

### Content

- Index state (generated date, age, hash drift, maturity)
- Recorded decisions from module pages in scope (appear first — before module code)
- Condensed module pages: responsibility, entry points, public interface, dependencies, known constraints
- High/medium-weight knowledge signals: summary and pattern only (not full entry lists)
- Coverage confidence level

Decisions appear before module context — constraints must be seen before implementation begins.

### Coverage Confidence — Behavioral Constraint

Coverage confidence is not metadata. It is a behavioral constraint that governs how the executor reads files during a phase.

| Level | Constraint |
|---|---|
| `high` | Strictly prohibited from reading files outside the context packet. Any attempt must halt execution and require explicit engineer approval before proceeding. |
| `medium` | Controlled one-hop expansion — may read files referenced by packet modules; no broad scanning. |
| `low` | Full codebase search available without restriction. Agent must acknowledge low confidence at phase start before proceeding. |

Confidence is announced at session or phase start. Absence of a context packet = `low`, always announced explicitly, never silent.

Coverage enforcement is identical across all three execution modes.

### User Responsibility

Context packets are not automatically generated.

The user decides whether to invoke `/context-packet` between planning and execution. They are most effective when:
- Retrieval has already run (via planning)
- Indexes are up to date
- Execution is phased and the phase is non-trivial (≥4 files)

They act as a bridge between retrieval and execution — not a replacement for either. If skipped, execution falls back to live codebase search and announces `low` coverage confidence at phase start.

---

## Session Hygiene Protocol

Start a new chat at every phase boundary. Each phase builds its prompt context from scratch — a fresh session prevents stale assumptions from accumulating.

**Why this matters (C1):** LLM sessions accumulate tool call history, intermediate reasoning, and exploratory reads that are irrelevant to the next phase. Without a reset, later phases are biased by earlier context that may no longer be accurate. The session boundary is an enforcement mechanism, not a convention.

Skills reference this protocol via their Handoff sections. The canonical definition lives here; skills do not duplicate it.

---

## Decision Conflict Check

The conflict check runs in two phases with different stakes:

**Spec-writing:** After the Architecture section is drafted, the spec-writer reads `## Decisions` from relevant module pages and compares against the spec's architectural choices. A conflict — spec contradicts a recorded decision, weakens a load-bearing assumption, or re-proposes a rejected alternative — must be resolved before the spec is completed. Resolution options: revise the spec to align (Option A), or add an explicit `## Design Override` section documenting the override and reason (Option B).

**Planning:** After retrieval runs, the planner compares all loaded module decisions against the spec. Conflicts at this stage are riskier because the spec is already locked — surfaced as flags that require engineer resolution before any steps are written.

**Why it exists:** Recorded decisions represent constraints established by prior tickets. Silently overriding them produces accumulated debt that is difficult to detect at review time.

---

## Knowledge Loop

After each ticket closes, the review skill runs a structured debrief:

1. Were discoveries and amendments written to the plan file? If not, add them now.
2. Is `conventions/SKILL.md` out of date? Update it before closing.
3. Would any phase be structured differently next time? Note it in conventions under `## Notes`.
4. Did the plan accurately predict implementation complexity? If not, note the discrepancy in plan `## Discoveries`.
5. Check the knowledge index for pattern-candidate topics on modules touched this ticket.

**Pattern-candidate resolution:** When found, the engineer chooses from: synthesize (write a `## Pattern` section now), retain as-is, merge with another topic, split into subtopics, or defer. Synthesizing a pattern writes a confidence-rated statement (high = same root cause, same modules, same resolution, ≥3 tickets; medium = same symptom, varied resolutions; low = weak correlation).

The debrief closes with `/index knowledge --incremental` — this ticket's signals are available for the next ticket's retrieval.

---

## Knowledge Layer

The knowledge layer adds structured, evolution-aware signals to the retrieval system. Knowledge is stored as topic pages in `[knowledge-index-path]/`, maintained exclusively by `index-knowledge`, and consumed by retrieval-protocol and context-packet.

### Schema

Each topic page uses two header lines followed by fixed sections:

```
_Type: [system|empirical|external|operational|meta] | Modules: [...] | Weight: HIGH|MEDIUM|LOW | Recurrence: N | Status: [flags]_
_Validity: [valid|stale|questionable|superseded] | Last validated: [YYYY-MM-DD|—]_

## Summary
## Provenance
## Relationships   ← omit if none
## Pattern         ← omit until confirmed
## Entries
## Related Modules
```

**Type** — nature of the claim. Drives retrieval sort priority and staleness rules.
**Validity** — trustworthiness of the claim. Transitions: valid → stale (type-specific decay trigger), valid → questionable (contradiction detected). Never auto-recovers — engineer resets manually after re-validation.
**Provenance** — Source, Evidence, Validated by. Human-facing only; not used in retrieval ranking.
**Relationships** — optional typed links. Section omitted entirely when no relationships exist.

### Component Boundaries

These boundaries are strict. No component may perform logic owned by another.

| Component | Owns |
|---|---|
| `index-knowledge` | Type inference · contradiction detection · validity transitions · relationship stub writing |
| `retrieval-protocol` | Filtering · ranking · exclusion rules · budget handling |
| `context-packet` | Assembly and display only — reads fields written by index-knowledge, renders them |

`retrieval-protocol` reads validity and type; it does not recompute staleness.
`context-packet` reads all fields; it does not write to knowledge files.

### Retrieval Behavior

**Exclusion rules** (applied before ranking, in order):
1. `validity=superseded` — always excluded
2. `type=empirical or operational` + `Recurrence=1` + `validity=stale` + no BLOCKER entry — excluded (system and external types: load with ⚠️ STALE instead)
3. Stale side of a contradiction where the other side is valid — load only the valid side; no conflict section triggered

**Type priority within same weight tier:**
- `bug-fix / modification` tickets: empirical → system → external
- `new-feature` tickets: system → empirical → external

**Clustering:**
When 3+ topics share `derived_from: [[same-source]]`: load at most 2 (highest weight); note count for remainder. Prefer source topic over derivatives when source is in scope.

**Contradiction pairs:**
When both sides of a `contradicts` relationship are in scope, the pair counts as 1 budget slot. For 3+ mutually contradicting topics: load the 2 highest-weight as a pair; surface a cluster notice for the rest.

### Runtime Signals (context-packet only)

Exactly two proactive signals are defined. No others.

**Stale signal warning** — appears at the top of `## Knowledge Signals` when ≥2 loaded topics have `validity=stale`:
> ⚠️ N stale signals in scope — run `/index knowledge --incremental` to refresh before relying on this packet.
Actionable: maps to a specific command. Omitted when condition not met.

**Conflicting signals section** (`## Conflicting Signals`) — appears before `## Knowledge Signals` when both sides of a `contradicts` pair are loaded. Shows topic summaries, types, validity, and the specific conflict description. Omitted when no active conflicts are in scope.

No conflict count warning. No provenance warning. Both were evaluated and rejected: no actionable response available at context-packet time.

### Relationship Rules

| Relationship | Written by | Triggers |
|---|---|---|
| `contradicts` | index-knowledge (auto, 3-gate guard) | Conflict section in context-packet; one-hop expansion in retrieval |
| `supersedes` | index-knowledge (auto, on amendment override) | Exclusion of superseded topic from retrieval |
| `supports` | Engineer only (manual) | Informational only |
| `derived_from` | Engineer only (manual) | Cluster logic and lineage label in context-packet |

### Contradiction Detection Guard

index-knowledge Step 6 applies three gates before writing any `contradicts` stub:

1. **Specificity** — description must name a concrete, specific thing (parameter, value, contract). General tensions are rejected.
2. **Signal strength** — at least one topic HIGH, or both MEDIUM or higher. LOW-only pairs are rejected.
3. **Per-run cap** — maximum 3 new stubs per run. Excess candidates are logged in the Step 13 report but not written.

A self-review pass follows: each description is read once to confirm it answers "what specific thing conflicts?" Failing stubs are removed. This is the system's single non-deterministic step — the guard is a deliberate second check against LLM judgment drift.

### Relationship Integrity

index-knowledge runs an integrity check after all writes. Detection only — no auto-fix.

- `validity=questionable` without a `contradicts:` line in Relationships → flagged
- `validity=superseded` without any topic containing `supersedes: [[this-topic]]` → flagged

Findings are reported in the Step 13 output. Engineer resolves by correcting the validity field or writing the missing relationship.

### Philosophy

**File-native.** No runtime dependencies, no external services. All intelligence lives in Markdown files readable by Copilot and engineers alike.

**Relationships enable reasoning, not storage.** A topic page without relationships is valid. Relationships exist to surface contradictions and lineage at retrieval time — not to build a comprehensive ontology.

**Minimal schema, high signal.** Every field in the schema is read by retrieval logic or displayed in context packets. Fields without an active consumer are not added.

---

## System Evolution Principles

**Mechanisms replace rules.** A behavioral constraint enforced by an artifact or file-based check is stronger than a convention in a document. If a discipline cannot be expressed as a file-based check, it will fail under load.

**Simpler systems scale better.** Every addition must justify its complexity against the maintenance cost. Three lines of lean convention injection beat 50 lines of embedded full context.

**Better models → remove scaffolding, not add it.** As models improve at codebase understanding, context packets and loading budgets should shrink or be dropped — not supplemented with more structure. The retrieval layer exists because current models cannot discover knowledge autonomously (C3). When that changes, the layer becomes overhead.

**ARCHITECTURE.md describes how the system actually behaves.** It is not aspirational. If a skill implementation diverges from this document, update one of them — not both to describe two different states simultaneously.

---

## Documentation Philosophy

**WORKFLOW.md** answers: "How do I use this?" It is for engineers doing daily work. It must not require understanding of internal mechanics to follow.

**ARCHITECTURE.md** answers: "How does this work and how do I change it?" It is for maintainers and skill authors. It must be complete but free of usage detail that belongs in WORKFLOW.md.

When a mechanism changes:
- Update the skill that implements it.
- Update ARCHITECTURE.md to reflect the new behavior.
- Update WORKFLOW.md only if the user-visible behavior changes (e.g. a new command, a changed checkpoint format).

Invariant: WORKFLOW.md must be self-sufficient for day-to-day use. ARCHITECTURE.md must be self-sufficient for understanding or modifying any mechanism.

---

## V2 Artifact Model (design — spec: `docs/superpowers/specs/2026-04-25-llm-native-artifact-evolution-design.md`)

_Status: designed, not yet implemented. V1 behavior remains active for all current tickets._

### Motivation

Every phase boundary in the v1 system is a parsing boundary. Consuming phases re-extract structure from prose artifacts, introducing variance (C2) at each junction. This section describes the v2 artifact model that eliminates C2 by replacing prose-heavy artifacts with typed, schema-defined representations.

### The Four Primitives

Four typed records carry all information that currently flows across phase boundaries:

| Primitive | Produced by | Consumed by | Purpose |
|---|---|---|---|
| `ProblemRecord` | brainstorm | all downstream phases | Ticket identity — immutable after brainstorm |
| `DecisionRecord` | spec-writing | planning, execution, review | Resolved architectural choices with constraints |
| `Requirement` | spec-writing | planning, execution, review | Testable claims with acceptance commands |
| `StepNode` | planning | execution, context-packet, review | Atomic work units with typed file manifests |

Full TypeScript interface definitions live in `.github/skills/SCHEMA.md`.

### Artifact Inheritance Chain

Each artifact is an additive superset of the previous. No phase re-derives fields set by a prior phase.

```
BrainstormArtifact  →  SpecArtifact  →  PlanArtifact  →  (execution writes amendments[])
                                              ↓
                                    ContextPacketArtifact  (projection — not in chain)
```

`ContextPacketArtifact` is a projection: it reads `plan.phases[N].steps[*].files[*].path` as a typed array and assembles module/knowledge context. It does not extend PlanArtifact.

### Immutability and Ownership

Each phase owns defined fields. Inherited fields are verified byte-for-byte against the source artifact at the start of each consuming phase (via `/validate-artifact`). Mismatch → BLOCK.

```
BrainstormArtifact owns: [problem, open_decisions]
SpecArtifact owns:       [decisions, requirements, spec_constraints, out_of_scope]
PlanArtifact owns:       [execution, phases, retrieval_constraints, amendments]
```

### Four System Rules

**Rule 1 — Upgrade sequencing:** Consumers upgraded before or simultaneously with producers. Version gate on `schema_version: 2` artifacts: BLOCK if skill has no v2 path. Silent fallback to v1 extraction prohibited.

Upgrade order per artifact type:
- `BrainstormArtifact`: upgrade spec-writing → then brainstorming
- `SpecArtifact`: upgrade planning → then spec-writing
- `PlanArtifact`: upgrade execution, context-packet, review → then planning

**Rule 2 — Stage 1 grace category:** Stage 1 is exact (`StepNode.files` vs `git diff --name-only`). Files exempt from FAIL if: matches `conventions/SKILL.md: Incidental file patterns` AND not listed in any StepNode across any phase AND operation is not `delete`. Exempted files logged as informational.

**Rule 3 — Context reset block provenance:** Block generated from typed sources only: `phases[N].steps[].description` + `amendments[]` filtered to `phase=N` + `phases[N+1].steps[*].files[*].path`. No open-ended session synthesis.

**Rule 4 — Schema evolution:** Non-breaking changes (adding optional fields, new enum values, relaxing constraints) require no version increment. Breaking changes (required fields, removals, type changes, tightening invariants) require incrementing to `schema_version: 3`.

### V2 Execution Changes

- **Checkpoint generation:** template fill from `StepNode.files` + `StepNode.review_prompt`. No inference.
- **Stage 1 compliance:** exact set comparison with incidental grace (Rule 2).
- **Context packet:** auto-triggered by execution skill when `mode=phased` AND `phases[N]` file count ≥ 4. No manual `/context-packet` command needed for qualifying phases.
- **Conventions injection (phased-subagent):** fixed sections always + `StepNode.risk_signals[]` matched against section headers by exact text. No step-text scan.
- **Context reset block:** generated from amendment records + next phase StepNode files (Rule 3). `step-completed` amendment written by execution after each passing verify.

### New Skills Required

- **`SCHEMA.md`** — canonical primitive definitions, all invariants, evolution policy. Referenced by all six skills.
- **`/validate-artifact`** — checks schema version, ID uniqueness, referential integrity, cross-field invariants, immutability. Runs silently at start of each consuming skill; also user-invokable.

### V2 Known Limitation

The decision conflict check in spec-writing compares typed `DecisionRecord.constraints[]` against module page `## Decisions` prose. Module pages are not v2 artifacts. This boundary remains partially non-deterministic until module pages adopt typed decision records (out of scope).

### Cross-Repo Context (Area 4)

Each participating repo maintains `exports.md` (what it publishes) and `imports.md` (what it monitors). Import resolution runs at context packet assembly time using exact string matching: `phase_module = exported_topic.modules[i]`. No fuzzy matching. Results appear in `## Cross-Repo Signals` in the context packet — advisory only, do not affect coverage confidence.

Operational dependency: imports work only with consistent module naming across repos.

### Migration Path

Phase 1: write `SCHEMA.md`, `/validate-artifact`, add `Incidental file patterns:` to conventions.
Phase 2: upgrade skills in consumer-first order (review → context-packet → execution → planning → spec-writing → brainstorming).
Phase 3 (after ≥5 v2 tickets): populate `exports.md`, declare `imports.md`, enable cross-repo signals.

V1 artifacts remain valid indefinitely. Version gates route them to legacy paths unchanged.
