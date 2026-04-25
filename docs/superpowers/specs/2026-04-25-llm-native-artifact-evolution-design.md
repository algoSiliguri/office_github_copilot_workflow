---
ticket: SYSTEM-EVOLUTION-001
phase: spec
created: 2026-04-25
status: approved
schema_version: 1
---

# Spec: LLM-Native Artifact Evolution

## Problem Statement

The workflow system enforces discipline through artifacts, but every phase boundary is a parsing boundary. Specs, plans, and brainstorm outputs are human-readable Markdown. Consuming phases re-extract structure from prose, introducing variance at each boundary (C2). Context packet triggering is manual, creating a known failure mode. Stage 1 compliance is LLM-inferred rather than exact. These are structural problems, not configuration problems.

## Design Goals

Three axes, ordered by dependency:

1. **LLM-native artifacts (foundation)** — replace prose-heavy artifacts with typed, schema-defined representations that downstream phases read without interpretation
2. **Execution efficiency (derived from 1)** — eliminate context rebuilding overhead, make Stage 1 exact, auto-trigger context packets
3. **Cross-repo context (reuses model from 1)** — federated knowledge retrieval across repos using the same artifact model primitives

## Non-Negotiable Constraints

Preserved without exception:
- Phase boundaries and session resets
- Execution modes (inline, phased-inline, phased-subagent) and their trigger logic
- Checkpoint format and gate discipline (engineer must confirm, no auto-continue)
- Verification iron law (no claim without pasted terminal output)
- Artifact-based state transfer (no hidden memory)
- Knowledge indexing loop and retrieval constraints

Not allowed:
- Collapsing phases
- Implicit memory between sessions
- Removing verification or checkpoints
- Opaque artifact formats

---

## Core Artifact Model (Area 2)

### The Four Primitives

All four are expressed in TypeScript interface notation. These are the canonical types; all consuming skills reference `SCHEMA.md` for definitions.

```typescript
// ─── PRIMITIVE 1: ProblemRecord ───────────────────────────────────────────────
interface ScopeModule {
  module: string;       // REQUIRED  /^[a-z][a-z0-9-]*$/
  known: boolean;       // REQUIRED  true = exists in codebase index
}

interface ProblemRecord {
  id:                 string;         // REQUIRED  /^[A-Z]+-[0-9]+$/
  classification:     'new-feature' | 'modification' | 'bug-fix';  // REQUIRED
  summary:            string;         // REQUIRED  non-empty  max:200 chars
  scope:              ScopeModule[];  // REQUIRED  min:1
  acceptance_signals: string[];       // REQUIRED  min:1
}
// Invariants:
//   scope[*].module unique within array
//   acceptance_signals non-empty even when all scope.known=false


// ─── PRIMITIVE 2: DecisionRecord ─────────────────────────────────────────────
interface RejectedOption {
  option: string;  // REQUIRED  non-empty
  reason: string;  // REQUIRED  non-empty
}

interface DecisionRecord {
  id:             string;             // REQUIRED  /^D[0-9]+$/  unique across decisions[]
  question:       string;             // REQUIRED  non-empty
  chosen:         string;             // REQUIRED  non-empty
  rejected:       RejectedOption[];   // REQUIRED  min:1
  constraints:    string[];           // REQUIRED when reversibility='low', else min:0
  reversibility:  'low' | 'medium' | 'high';          // REQUIRED
  phase_resolved: 'spec' | 'planning';                 // REQUIRED
}
// Invariants:
//   chosen ∉ rejected[*].option
//   reversibility='low' → constraints.length >= 1
//   id unique across all DecisionRecord[] in artifact


// ─── PRIMITIVE 3: Requirement ────────────────────────────────────────────────
interface Requirement {
  id:               string;                                    // REQUIRED  /^R[0-9]+$/  unique
  text:             string;                                    // REQUIRED  non-empty
  acceptance:       string;                                    // REQUIRED  non-empty  runnable command
  classification:   'functional' | 'constraint' | 'non-functional';  // REQUIRED
  source_decision?: string | null;                             // OPTIONAL  default: null
}
// Invariants:
//   source_decision != null → source_decision ∈ decisions[*].id (same artifact)
//   id unique across all Requirement[] in artifact


// ─── PRIMITIVE 4: StepNode ───────────────────────────────────────────────────
interface FileRef {
  path:      string;                              // REQUIRED  non-empty
  operation: 'create' | 'modify' | 'delete';     // REQUIRED
}

interface StepNode {
  id:              string;     // REQUIRED  /^P[0-9]+\.S[0-9]+$/  unique
  phase:           number;     // REQUIRED  integer >= 1
  description:     string;     // REQUIRED  non-empty  max:300 chars
  files:           FileRef[];  // REQUIRED  min:1
  depends_on:      string[];   // OPTIONAL  default:[]
  verify:          string;     // REQUIRED  non-empty  runnable command
  risk_signals:    string[];   // OPTIONAL  default:[]
  review_prompt:   string;     // REQUIRED  non-empty
  requirement_ids: string[];   // OPTIONAL  default:[]
}
// Invariants:
//   id phase segment matches phase field: id = "P{phase}.S{n}"
//   depends_on[*] ∈ StepNode[*].id; referenced step.phase <= this step.phase
//   files[*].path unique within a StepNode
//   files[*].path unique across ALL steps within the same phase
//   requirement_ids[*] ∈ requirements[*].id (same artifact)
//   id unique across all StepNode[] in artifact
```

### Artifact Inheritance Chain

Each artifact is an additive superset of the prior. Downstream phases inherit upstream fields verbatim and write only to new fields they own.

```
BrainstormArtifact
├── schema_version: 2
├── problem: ProblemRecord          ← set here, never changed
└── open_decisions:                 ← unresolved questions for spec-writing
    [{ question: string, options: string[] }]

SpecArtifact  (extends BrainstormArtifact)
├── schema_version: 2
├── problem: ProblemRecord          ← CARRIED FORWARD VERBATIM
├── open_decisions: [...]           ← CARRIED FORWARD VERBATIM (provenance)
├── decisions: DecisionRecord[]     ← open_decisions resolved
├── requirements: Requirement[]
├── spec_constraints: string[]      ← hard constraints (no source_decision)
└── out_of_scope: string[]

PlanArtifact  (extends SpecArtifact)
├── schema_version: 2
├── problem: ProblemRecord          ← CARRIED FORWARD VERBATIM
├── open_decisions: [...]           ← CARRIED FORWARD VERBATIM
├── decisions: DecisionRecord[]     ← CARRIED FORWARD VERBATIM
├── requirements: Requirement[]     ← CARRIED FORWARD VERBATIM
├── spec_constraints: string[]      ← CARRIED FORWARD VERBATIM
├── out_of_scope: string[]          ← CARRIED FORWARD VERBATIM
├── execution:
│   ├── mode: 'inline' | 'phased-inline' | 'phased-subagent'
│   ├── justification: string
│   ├── retrieval: 'ran' | 'skipped'
│   └── retrieval_justification: string
├── retrieval_constraints: string[] ← constraints discovered from module pages
├── phases: Phase[]
│   └── [{ id: number, name: string, steps: StepNode[] }]
└── amendments: Amendment[]         ← append-only during execution

ContextPacketArtifact  ← NOT in inheritance chain; a projection
├── phase_scope: StepNode[]         ← plan.phases[N].steps (direct field read)
├── decisions: DecisionRecord[]     ← filtered from plan.decisions (see selection rule)
├── coverage_confidence: 'high' | 'medium' | 'low'
├── modules: ModuleContext[]        ← loaded from codebase index
├── knowledge_signals: KnowledgeSignal[]
├── cross_repo_signals: CrossRepoSignal[]   ← area 4; separate section
├── stale_warnings: string[]
└── conflicts: ConflictPair[]
```

### Phase Consumption — Typed Field Access Only

Each phase reads defined fields. No extraction from prose.

| Boundary | Previous artifact | Fields consumed | New fields written |
|---|---|---|---|
| Brainstorm → Spec | BrainstormArtifact | `problem` (verbatim copy), `open_decisions[]` (resolve each into DecisionRecord) | `decisions[]`, `requirements[]`, `spec_constraints[]`, `out_of_scope[]` |
| Spec → Planning | SpecArtifact | `problem.classification` (retrieval split), `decisions[*].constraints[]` (conflict check), `requirements[]` (phase ordering + risk weighting) | `execution`, `phases[]`, `retrieval_constraints[]` |
| Planning → Execution | PlanArtifact | `phases[N].steps[]` (full StepNode per step), `execution.mode` (dispatch framing) | `amendments[]` (step-completed, deviations) |
| Planning → Context Packet | PlanArtifact | `phases[N].steps[*].files[*].path` (direct array read), `decisions[]` (filtered by selection rule) | ContextPacketArtifact (separate file) |

### Allowed Transformations

| Type | Example | Permitted |
|---|---|---|
| Resolution | `open_decision{question,options}` → `DecisionRecord{chosen,rejected,constraints}` | Yes |
| Addition | Spec adds `requirements[]` to the inherited artifact | Yes |
| Projection | Context packet selects `phases[N]` from full plan | Yes |
| Annotation | Execution appends `amendments[]` to plan artifact | Yes |
| Re-derivation | Planning re-classifies `problem.classification` | No |
| Modification of owned upstream field | Spec modifies `problem.summary` | No |

---

## Amendment Envelope Type

Not a primitive. Does not flow between phases. Lives on PlanArtifact only.

```typescript
interface Amendment {
  id:          string;    // /^A[0-9]+$/  append-only numbering
  step_id?:    string;    // null = phase-level or plan-level amendment
  phase:       number;
  type:        'step-added' | 'step-removed' | 'verify-override'
             | 'decision-conflict' | 'scope-change'
             | 'step-completed';    // added by execution after each passing verify
  description: string;   // non-empty
  added_by:    'engineer' | 'execution';
}
```

`step-completed` amendments are the only per-step execution records in the model. They enable deterministic context reset block generation without modifying immutable StepNode fields.

---

## Referential Integrity

**ID generation:** IDs are assigned by the LLM writing the phase artifact, monotonically incrementing. Uniqueness is checked at validation time (phase start of the consuming skill), not at write time.

| Violation | Detection | Mode |
|---|---|---|
| `step.requirement_ids[i]` not in `requirements[*].id` | Plan validation | BLOCK |
| `requirement.source_decision` not in `decisions[*].id` | Spec validation | BLOCK |
| Duplicate `DecisionRecord.id` | Plan validation | BLOCK |
| Duplicate `Requirement.id` | Spec validation | BLOCK |
| Duplicate `StepNode.id` | Plan validation | BLOCK |
| `step.depends_on[i]` not in `StepNode[*].id` | Plan validation | BLOCK |

---

## Immutability Enforcement

**Ownership map:**

```
BrainstormArtifact owns: [problem, open_decisions]
SpecArtifact owns:       [decisions, requirements, spec_constraints, out_of_scope]
  inherits (read-only):  [problem, open_decisions]
PlanArtifact owns:       [execution, phases, retrieval_constraints, amendments]
  inherits (read-only):  [problem, open_decisions, decisions, requirements,
                          spec_constraints, out_of_scope]
```

**Validation protocol:** at the start of each consuming phase, before any work begins, compare inherited fields in the artifact being produced against their source file (byte-for-byte field comparison). Mismatch → BLOCK with field path identified.

**Violation handling:** auto-fix prohibited. Return to the phase that owns the field, amend there, re-run the downstream phase.

**Fields immutable after phase closes:**
- `problem`, `open_decisions` after brainstorm
- `decisions[]`, `requirements[]`, `spec_constraints[]` after spec approval
- `execution`, `phases[*].steps[]`, `retrieval_constraints[]` after plan approval

---

## Four System Rules

### Rule 1: Upgrade Sequencing

Consumers must be upgraded to v2 before or simultaneously with their upstream producing skill.

When any skill encounters `schema_version: 2` and has not implemented the v2 typed-field-access path: **BLOCK** immediately with:
> `"[skill-name] does not support schema_version: 2. Upgrade the consuming skill before processing this artifact."`

Silent fallback to v1 extraction on a v2 artifact is prohibited. Two states only: route to v2 path, or BLOCK.

**Upgrade sequence per artifact type:**
```
BrainstormArtifact: upgrade spec-writing → then brainstorming
SpecArtifact:       upgrade planning → then spec-writing
PlanArtifact:       upgrade execution, context-packet, review → then planning
```

### Rule 2: Stage 1 Grace Category

Stage 1 is an exact comparison: `StepNode.files` vs `git diff --name-only`.

A file in the diff but not in any `StepNode.files[]` is exempt from Stage 1 FAIL if **all three** hold:
1. Path matches a pattern in `conventions/SKILL.md: Incidental file patterns`
2. Path is not listed in any `StepNode.files[]` across any phase
3. Git diff operation is `modify` or `create` (not `delete`)

Files meeting all three: classified `incidental`, logged in `Incidental files:` checkpoint section, not a compliance signal.

Files failing any condition: classified `unlisted`, trigger Stage 1 FAIL.

If `Incidental file patterns:` is absent from conventions: no files are incidental. All unlisted files are violations.

### Rule 3: Context Reset Block Provenance

The context reset block is generated exclusively from:
1. `phases[N].steps[].description` — completed work
2. `plan.amendments[]` filtered to `phase=N` — what changed, including `step-completed` entries
3. `phases[N+1].steps[*].files[*].path` — what the next phase will touch

No open-ended session synthesis. No information outside these three sources.

If `phases[N+1]` does not exist (last phase): the next-phase-scope section is omitted; block is omitted entirely; finishing options are shown directly.

### Rule 4: Schema Evolution Policy

`schema_version: 2` schema is stable. Governed by:

**Non-breaking (no version increment):**
- Adding optional fields to any primitive
- Adding new enum values to non-invariant fields
- Relaxing a constraint

**Breaking (must increment to `schema_version: 3`):**
- Adding required fields
- Removing fields
- Changing a field's type
- Tightening a constraint or adding a new invariant
- Removing an enum value

`SCHEMA.md` carries its own definition version header (`Schema definition: v2.0`), incremented on non-breaking changes and bumped on breaking changes. Artifact `schema_version` tracks major only.

---

## Execution Efficiency Changes (Area 1)

### Checkpoint Generation

Checkpoints are generated from typed fields, not prose inference:
- **Files changed section:** `StepNode.files[]` (typed array, not LLM summary)
- **Review section:** `StepNode.review_prompt` (exact field, not inferred question)
- **Stage 1 compliance:** exact set comparison `StepNode.files` vs `git diff --name-only` (with incidental grace per Rule 2)

### Context Packet Auto-Trigger

Context packet fires automatically inside the execution skill when:
1. `plan.execution.mode = 'phased-inline'` or `'phased-subagent'`
2. `phases[N].steps[*].files` count ≥ 4

If trigger fires but index maturity is insufficient or many files are UNKNOWN: coverage_confidence announced at phase start before execution proceeds. Engineer does not need a separate command; the quality signal is surfaced at phase start.

If trigger conditions are not met: no packet generated; codebase search protocol applies; `low` coverage confidence announced explicitly.

### Lean Conventions Injection (phased-subagent)

Sub-agent dispatch prompt built deterministically from typed fields:

```
Fixed (always injected):
  test_command   ← conventions.Test
  commit_format  ← conventions.Commit
  lint_command   ← conventions.Lint

Risk-signal sections (per step):
  For each risk_signal ∈ StepNode.risk_signals[]:
    → exact header-text match against conventions section headers
    → include matched section; skip silently if no match

Framing:
  plan.execution.mode  → sub-agent wrapper
  plan.execution.justification  → context
```

No step-text scan. `StepNode.risk_signals[]` is the injection signal source.

---

## Skill Changes (Area 3)

### SCHEMA.md (new file)

Lives at `.github/skills/SCHEMA.md`. Contains:
- All four primitive TypeScript interface definitions
- Amendment envelope type
- All enums
- All cross-field invariants
- Evolution policy (Rule 4)
- Schema definition version header

All six skills reference `SCHEMA.md` as the single source of type names and invariant definitions. No primitive is described in two places.

### `/validate-artifact` (new skill)

Invoked silently at the start of each consuming skill (not user-visible unless it fails). Also user-invokable as `/validate-artifact [artifact-path]` for debugging.

Checks in order:
1. `schema_version` present and supported → else BLOCK (Rule 1)
2. ID uniqueness across `decisions[]`, `requirements[]`, `StepNode[]`
3. Referential integrity: all cross-field references resolve
4. Cross-field invariants: all invariants from SCHEMA.md satisfied
5. Immutability: inherited fields byte-for-byte match source artifact file

Output: `PASS` or itemized FAIL list with field paths. All checks are exact comparisons. None are semantic.

### Per-Skill Change Summary

| Skill | What changes |
|---|---|
| `brainstorming` | Output: `BrainstormArtifact` with `schema_version: 2`. `ProblemRecord` populated from conversation. `open_decisions[]` populated from unresolved questions. |
| `spec-writing` | Gains version gate + `/validate-artifact` on input. Reads `open_decisions[]` (typed). Writes `decisions[]`, `requirements[]`, `spec_constraints[]`. Immutability check: verifies inherited fields match source brainstorm. |
| `planning` | Gains version gate + `/validate-artifact` on input. Reads `decisions[*].constraints[]` for conflict check (typed vs module page prose — partially deterministic). Reads `problem.classification` for retrieval split (direct field). Writes `execution`, `phases`, `retrieval_constraints[]`. Immutability check on inherited spec fields. |
| `execution` | Gains version gate. Checkpoint generated from StepNode fields (template fill). Stage 1: exact comparison + incidental grace (Rule 2). Writes `step-completed` amendments. Context reset block from amendments + next phase files (Rule 3). Auto-triggers context packet when conditions met. |
| `context-packet` | Gains version gate. Reads `phases[N].steps[*].files[*].path` as typed array. Decision selection uses deterministic rule. Coverage confidence computed by formula. |
| `review` | Gains version gate. Reads `requirements[]` for spec-compliance traceability via `requirement_ids` links. Stage 1 evidence: `step-completed` amendment records. |

### Limitation Acknowledged

The decision conflict check in spec-writing compares typed `DecisionRecord` fields against module page `## Decisions` prose. Module pages are not v2 artifacts. This check is only partially deterministic — one typed input, one prose input. Full determinism at this check requires module pages to adopt typed decision records, which is out of scope for this evolution.

---

## Cross-Repo Context Model (Area 4)

### Structure

Each participating repo maintains two files in its knowledge path:

**`[knowledge-path]/exports.md`** — what this repo makes available:
```yaml
exported_topics:
  - topic_id: T1
    title: "Redis connection pool exhaustion under burst load"
    modules: [redis-config, auth-service]     # module names as in THIS repo's codebase index
    weight: HIGH
    type: empirical
    summary: "Pool size must be >= 20; default of 5 causes exhaustion above 50 RPS"
    last_updated: YYYY-MM-DD
```

**`[knowledge-path]/imports.md`** — what external repos this repo monitors (engineer-maintained):
```yaml
import_sources:
  - repo: service-b
    exports_path: ../service-b/knowledge/exports.md
    scope: [auth-service, session-manager]    # module names in THIS repo to match against
```

### Import Resolution Rule (exact — no heuristics)

Runs at context packet assembly time:

```
For each import_source in imports.md:
  For each phase_module in context_packet.modules[*].name:
    If phase_module ∈ import_source.scope:
      Read import_source.exports_path
      For each exported_topic where phase_module ∈ exported_topic.modules (exact string):
        If exported_topic.weight ∈ {HIGH, MEDIUM}
        AND exported_topic.last_updated within 90 days:
          → include as cross-repo signal
```

Match is exact string equality: `phase_module = exported_topic.modules[i]`. Naming divergence between repos produces no match and no import. This is the explicit safety-over-recall tradeoff: no false imports, but imports require naming discipline.

### Context Packet Placement

Imported topics appear in `## Cross-Repo Signals` section — after `## Knowledge Signals`, before `## Conflicting Signals`.

Cross-repo signals:
- Do not affect `coverage_confidence` calculation
- Cannot create `contradicts` relationships with local topics
- Do not count against the local knowledge loading budget
- Are advisory only — cannot block execution or modify any artifact field

### Operational Dependency

Cross-repo imports produce useful results only when exporting repo module names in `exports.md` match the module names in the importing repo's `imports.md:scope`. The system enforces the exact-match rule but cannot enforce naming alignment across teams. This is a team naming convention requirement.

### Context Packet Decision Selection Rule

Decisions included in the context packet for phase N:

```
phase_req_ids  = ∪ step.requirement_ids  for all steps ∈ phases[N].steps
decision_ids_A = { req.source_decision
                   for req in requirements
                   where req.id ∈ phase_req_ids AND req.source_decision != null }
decision_ids_B = { d.id for d in decisions where d.reversibility = 'low' }
included       = decisions where id ∈ (decision_ids_A ∪ decision_ids_B)
```

### Coverage Confidence Formula

```
all_files = phases[N].steps[*].files[*]
none_count = |{ f ∈ all_files where module_mapping(f.path) = UNKNOWN }|
total      = |all_files|

if none_count / total > 0.5  → 'low'
if none_count > 0            → 'medium'
else                         → 'high'
```

### File Path → Module Mapping Rule

```
candidates(path) = { m for m in codebase_index.modules
                       where any p ∈ m.source_paths is a prefix of path }

resolve(path):
  |candidates| = 1  → use that module
  |candidates| = 0  → UNKNOWN
  |candidates| > 1  → use module with longest matching prefix
                      on tie: use module with higher Reach score
                      on tie: use first alphabetically (deterministic)
```

---

## Migration Strategy

**Model:** version-gated, ticket-scoped, no dual-write.

### Phase 1 — Foundation

Before any ticket migration:
1. Write `SCHEMA.md` with all primitive definitions, invariants, evolution policy
2. Write `/validate-artifact` skill
3. Add `Incidental file patterns:` to `conventions/SKILL.md` (may be empty initially)

### Phase 2 — Skill Adoption (consumer-first order)

```
Step 1: upgrade review
Step 2: upgrade context-packet
Step 3: upgrade execution
Step 4: upgrade planning
Step 5: upgrade spec-writing
Step 6: upgrade brainstorming
```

After step 6, all new tickets use v2 artifacts end-to-end.

### Phase 3 — Cross-Repo (after ≥5 tickets on v2)

1. Populate `exports.md` in exporting repos via `/index knowledge` run
2. Declare `imports.md` in importing repos
3. Context packet assembly begins including cross-repo signals

### V1 Ticket Behavior

No change. Version gates route v1 artifacts to legacy extraction paths, unchanged. V1 plans produce prose-based checkpoints and LLM-inferred Stage 1. V1 artifacts remain valid indefinitely. Legacy path removal is the team's discretion after all active tickets have closed on v1.

### Completion Signal

All six skills at v2 + `SCHEMA.md` stable at `v2.0` + at least one ticket completed end-to-end with v2 artifacts and no validation failures.

---

## Out of Scope

- Module pages adopting typed decision records (required for full determinism at spec-writing conflict check; deferred)
- Automatic `exports.md` population without a `/index knowledge` run
- Schema version negotiation between skills (version gate is binary: v2 path exists or BLOCK)
- Forcing naming alignment across repos (operational requirement, not system enforcement)
