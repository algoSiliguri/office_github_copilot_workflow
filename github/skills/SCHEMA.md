---
schema_definition: "v2.0"
---

# Artifact Schema

All six skills reference this file as the canonical source for type definitions,
invariants, and evolution policy. No primitive is defined in two places.

---

## Schema Definition Version

`Schema definition: v2.0`

Incremented on non-breaking changes. Bumped to v3.0 on any breaking change (see Evolution Policy).

---

## Primitive 1: ProblemRecord

```typescript
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
```

**Invariants:**
- `scope[*].module` unique within array
- `acceptance_signals` non-empty even when all `scope[*].known = false`

---

## Primitive 2: DecisionRecord

```typescript
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
```

**Invariants:**
- `chosen ∉ rejected[*].option`
- `reversibility = 'low'` → `constraints.length >= 1`
- `id` unique across all `DecisionRecord[]` in the artifact

---

## Primitive 3: Requirement

```typescript
interface Requirement {
  id:               string;                                    // REQUIRED  /^R[0-9]+$/  unique
  text:             string;                                    // REQUIRED  non-empty
  acceptance:       string;                                    // REQUIRED  non-empty  runnable command
  classification:   'functional' | 'constraint' | 'non-functional';  // REQUIRED
  source_decision?: string | null;                             // OPTIONAL  default: null
}
```

**Invariants:**
- `source_decision != null` → `source_decision ∈ decisions[*].id` (same artifact)
- `id` unique across all `Requirement[]` in the artifact

---

## Primitive 4: StepNode

```typescript
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
```

**Invariants:**
- `id` phase segment matches `phase` field: `id = "P{phase}.S{n}"`
- `depends_on[*] ∈ StepNode[*].id`; referenced step's `phase <= this step.phase`
- `files[*].path` unique within a StepNode
- `files[*].path` unique across ALL steps within the same phase
- `requirement_ids[*] ∈ requirements[*].id` (same artifact)
- `id` unique across all `StepNode[]` in the artifact

---

## Amendment Envelope

Not a primitive. Does not flow between phases. Lives on PlanArtifact only.

```typescript
interface Amendment {
  id:          string;    // /^A[0-9]+$/  append-only; A1, A2, A3 ... never reused
  step_id?:    string;    // null = phase-level or plan-level amendment
  phase:       number;
  type:        'step-added' | 'step-removed' | 'verify-override'
             | 'decision-conflict' | 'scope-change'
             | 'step-completed';    // added by execution after each passing verify
  description: string;   // non-empty
  added_by:    'engineer' | 'execution';
}
```

`step-completed` amendments are the only per-step execution records. They enable
deterministic context reset block generation without modifying immutable StepNode fields.

---

## Artifact Inheritance Chain

```
BrainstormArtifact       owns: [problem, open_decisions]
SpecArtifact             owns: [decisions, requirements, spec_constraints, out_of_scope]
  inherits (read-only):  [problem, open_decisions]
PlanArtifact             owns: [execution, phases, retrieval_constraints, amendments]
  inherits (read-only):  [problem, open_decisions, decisions, requirements,
                          spec_constraints, out_of_scope]
```

Downstream phases inherit upstream fields verbatim and write only to new owned fields.

---

## Referential Integrity

| Violation | Detection | Mode |
|---|---|---|
| `step.requirement_ids[i]` not in `requirements[*].id` | Plan validation | BLOCK |
| `requirement.source_decision` not in `decisions[*].id` | Spec validation | BLOCK |
| Duplicate `DecisionRecord.id` | Plan validation | BLOCK |
| Duplicate `Requirement.id` | Spec validation | BLOCK |
| Duplicate `StepNode.id` | Plan validation | BLOCK |
| `step.depends_on[i]` not in `StepNode[*].id` | Plan validation | BLOCK |

---

## Evolution Policy (Rule 4)

**Non-breaking (no `schema_version` increment; update `Schema definition` patch only):**
- Adding optional fields to any primitive
- Adding new enum values to non-invariant fields
- Relaxing a constraint

**Breaking (must increment artifact `schema_version` to `3`):**
- Adding required fields
- Removing fields
- Changing a field's type
- Tightening a constraint or adding a new invariant
- Removing an enum value

`SCHEMA.md` version header is incremented on non-breaking changes and bumped on breaking
changes. Artifact `schema_version` tracks major only.
