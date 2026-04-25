# LLM-Native Artifact Evolution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evolve the `.github/` workflow system from prose-based v1 artifacts to typed, schema-defined v2 artifacts, eliminating parsing variance at all six phase boundaries.

**Architecture:** Consumer-first upgrade sequence (spec Rule 1): Foundation (SCHEMA.md + validate-artifact + conventions) → Consumer upgrades (review, context-packet, execution) → Producer upgrades (planning, spec-writing, brainstorming). Version gates ensure no v2 artifact arrives at an unprepared skill. V1 artifacts remain valid indefinitely with no behavior change.

**Tech Stack:** Markdown, YAML frontmatter, TypeScript interface notation (documentation only — not compiled), `grep`/`git` for verification.

---

## File Structure

| File | Status | Task |
|---|---|---|
| `.github/skills/SCHEMA.md` | Create | Task 1 |
| `.github/skills/validate-artifact/SKILL.md` | Create | Task 2 |
| `.github/skills/conventions/SKILL.md` | Modify | Task 3 |
| `.github/skills/review/SKILL.md` | Modify | Task 4 |
| `.github/skills/context-packet/SKILL.md` | Modify | Task 5 |
| `.github/skills/execution/SKILL.md` | Modify | Task 6 |
| `.github/skills/planning/SKILL.md` | Modify | Task 7 |
| `.github/skills/spec-writing/SKILL.md` | Modify | Task 8 |
| `.github/skills/brainstorming/SKILL.md` | Modify | Task 9 |

**Out of scope:** `exports.md` and `imports.md` per-repo files. The context-packet skill (Task 5) reads `imports.md` if it exists. Creating and populating those files is migration Phase 3 (after ≥5 tickets on v2) and is a team adoption activity, not a system change.

---

## Phase 1: Foundation

**Files:**
- Create: `.github/skills/SCHEMA.md`
- Create: `.github/skills/validate-artifact/SKILL.md`
- Modify: `.github/skills/conventions/SKILL.md`

---

### Task 1: Create SCHEMA.md

**Files:**
- Create: `.github/skills/SCHEMA.md`

- [ ] **Step 1: Write SCHEMA.md**

Write `.github/skills/SCHEMA.md` with this exact content:

````
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
````

- [ ] **Step 2: Verify SCHEMA.md**

Run: `grep -c 'ProblemRecord\|DecisionRecord\|interface Requirement\|StepNode\|Amendment' .github/skills/SCHEMA.md`
Expected: at least 5 matches (one heading or interface declaration per type)

- [ ] **Step 3: Commit SCHEMA.md**

```bash
git add .github/skills/SCHEMA.md
git commit -m "feat: add SCHEMA.md with v2 primitive definitions, invariants, and evolution policy"
```

---

### Task 2: Create validate-artifact skill

**Files:**
- Create: `.github/skills/validate-artifact/SKILL.md`

- [ ] **Step 1: Write validate-artifact/SKILL.md**

Write `.github/skills/validate-artifact/SKILL.md` with this exact content:

````
---
name: validate-artifact
description: Validates a v2 artifact against schema invariants, referential integrity, and immutability rules. Runs silently at the start of each consuming skill before any work begins. Also user-invokable as /validate-artifact [artifact-path] for debugging.
---

## Metadata

- **Name:** validate-artifact
- **Phase:** Pre-phase validation — runs silently inside consuming skills; also user-invokable
- **Inputs:** Artifact file path. Optionally a source artifact file path (enables Check 5: immutability).
- **Outputs:** `PASS` (silent when invoked internally) or itemized `FAIL` list with field paths.

---

You are validating a v2 artifact. All checks are exact comparisons — no semantic judgments.

## Silent vs. Direct Invocation

**When invoked silently (inside a consuming skill at phase start):**
On `PASS`: proceed — do not surface validation to the engineer.
On any `FAIL`: stop immediately with:

```
BLOCK — artifact validation failed:
1. [field.path]: [specific violation]
2. [field.path]: [specific violation]
```

Do not proceed with the consuming skill while any check fails.

**When invoked directly (`/validate-artifact [path]`):**
Report either:
- `Artifact at [path]: PASS — all checks passed.`
- `Artifact at [path]: FAIL — [N] violation(s) found:` followed by numbered list.

---

## Check 1: Schema Version Gate (Rule 1)

Read the artifact's YAML frontmatter. Look for `schema_version:`.

- **Absent:** artifact is v1. Output `PASS — v1 artifact, skip.` Stop all checks.
- **`schema_version: 2`:** proceed to Check 2.
- **Any other value:** FAIL — `schema_version: unsupported value '[value]'. Expected: 2`.

---

## Check 2: ID Uniqueness

Collect IDs from these arrays:
- `decisions[*].id` — must be unique within the decisions array
- `requirements[*].id` — must be unique within the requirements array
- All `phases[*].steps[*].id` values across all phases — must be globally unique

For each array where any ID appears more than once: FAIL — `[array path][index].id: duplicate id '[id]'`

---

## Check 3: Referential Integrity

For each reference, verify the target ID exists:

| Source field | Target field |
|---|---|
| `requirements[*].source_decision` (non-null) | `decisions[*].id` |
| `phases[*].steps[*].requirement_ids[*]` | `requirements[*].id` |
| `phases[*].steps[*].depends_on[*]` | any `phases[*].steps[*].id` (globally) |

For each broken reference: FAIL — `[source.field.path]: '[value]' not found in [target field path]`

---

## Check 4: Cross-Field Invariants

Check all invariants from `.github/skills/SCHEMA.md`:

1. `problem.scope[*].module` values unique within scope array
2. `problem.acceptance_signals` array non-empty
3. Each `DecisionRecord`: `chosen` value not present in any `rejected[*].option`
4. Each `DecisionRecord`: if `reversibility = 'low'` then `constraints.length >= 1`
5. Each `StepNode.id`: the phase number extracted from the pattern `P{N}.S{M}` matches the `phase` field value `N`
6. Each `StepNode.files[*].path` unique within the step
7. Each `StepNode.files[*].path` unique across all steps within the same phase (same `phase` field value)

For each violation: FAIL — `[field path]: [invariant description]`

---

## Check 5: Immutability (only when source artifact path is provided)

Compare each inherited field in the artifact being validated against the corresponding field
in the source file. Fields must match byte-for-byte.

**SpecArtifact (source = BrainstormArtifact):** compare `problem`, `open_decisions`
**PlanArtifact (source = SpecArtifact):** compare `problem`, `open_decisions`, `decisions`, `requirements`, `spec_constraints`, `out_of_scope`

If any inherited field differs: FAIL — `[field path]: inherited field modified. Auto-fix: prohibited. Return to the phase that owns this field.`

---

## Output Format

**PASS (direct invocation):**
```
Artifact at [path]: PASS — all checks passed.
```
(Silent when invoked internally.)

**FAIL:**
```
BLOCK — artifact validation failed:
1. decisions[1].id: duplicate id 'D2'
2. phases[0].steps[2].requirement_ids[0]: 'R9' not found in requirements[*].id
3. phases[1].steps[0].id: 'P2.S1' — phase segment '2' does not match phase field '1'
```

---

## Dependencies

- `.github/skills/SCHEMA.md` — canonical invariant definitions

## Notes

This skill is read-only. It never modifies any artifact file.
````

- [ ] **Step 2: Verify validate-artifact/SKILL.md has all 5 checks**

Run: `grep -c '## Check [1-5]' .github/skills/validate-artifact/SKILL.md`
Expected: 5

- [ ] **Step 3: Commit validate-artifact skill**

```bash
git add .github/skills/validate-artifact/SKILL.md
git commit -m "feat: add validate-artifact skill with 5-check v2 validation sequence"
```

---

### Task 3: Add incidental file patterns field to conventions

**Files:**
- Modify: `.github/skills/conventions/SKILL.md`

- [ ] **Step 1: Confirm Notes section location**

Run: `grep -n '## Notes\|Incidental' .github/skills/conventions/SKILL.md`
Expected: line with `## Notes` present; no line with `Incidental` (field not yet added).

- [ ] **Step 2: Add Incidental file patterns field**

In `.github/skills/conventions/SKILL.md`, find the `## Notes` section. The current content is:

```
## Notes

<Any other repo-specific conventions: file naming, package structure, coding standards, deployment notes>
```

Replace with:

```
## Notes

<Any other repo-specific conventions: file naming, package structure, coding standards, deployment notes>

Incidental file patterns: <comma-separated glob patterns for files that change alongside any step but are never plan targets — e.g. *.lock, package-lock.json, .DS_Store. Leave blank initially; add patterns after Stage 1 false positives appear. Used by the v2 execution skill Rule 2 incidental grace category.>
```

- [ ] **Step 3: Verify field is present**

Run: `grep -n 'Incidental file patterns' .github/skills/conventions/SKILL.md`
Expected: one line containing the field

- [ ] **Step 4: Commit conventions change**

```bash
git add .github/skills/conventions/SKILL.md
git commit -m "feat: add Incidental file patterns field to conventions (v2 Rule 2 Stage 1 grace)"
```

---

## Phase 2: Consumer Upgrades

**Files:**
- Modify: `.github/skills/review/SKILL.md`
- Modify: `.github/skills/context-packet/SKILL.md`

---

### Task 4: Upgrade review skill to v2

**Files:**
- Modify: `.github/skills/review/SKILL.md`

Changes: version gate, v2 spec-coverage path using typed `requirements[*]` + `requirement_ids`, v2 spec-deviations path using amendment records.

- [ ] **Step 1: Add version gate before "## Before Reviewing"**

In `.github/skills/review/SKILL.md`, find `## Before Reviewing`. Insert this block immediately after the heading (before step 1):

```
**Version gate:** Before reading any artifact, check the plan file's `schema_version` frontmatter.
- `schema_version: 2` → PLAN_VERSION = 2. Use v2 typed paths in sections below. Run `/validate-artifact [plan-path]` silently. BLOCK if validation fails.
- Absent or other → PLAN_VERSION = 1. Use existing prose extraction throughout. No change in behavior.

```

- [ ] **Step 2: Add v2 spec coverage path to Section 1**

In `.github/skills/review/SKILL.md`, find `### 1. Spec Coverage`. The section ends with:

```
Missing coverage = **BLOCKER**
```

Append immediately after (before the next `###`):

```

**V2 path (PLAN_VERSION = 2):** Read `requirements[*]` directly from the plan artifact. For each requirement: (a) confirm at least one StepNode in `phases[*].steps[]` lists `requirement.id` in its `requirement_ids[]`; (b) confirm at least one `step-completed` amendment exists in `amendments[]` for each such StepNode. A requirement with no linked StepNode OR a linked StepNode with no `step-completed` amendment = BLOCKER.
```

- [ ] **Step 3: Add v2 spec deviations path to Section 5**

In `.github/skills/review/SKILL.md`, find `### 5. Spec Deviations`. The section ends with:

```
Undocumented deviation = **BLOCKER**
```

Append immediately after:

```

**V2 path (PLAN_VERSION = 2):** Run `git diff --name-status main`. For each file with status `A` (added), `M` (modified), or `R` (renamed) in the diff: check if the path appears in any `phases[*].steps[*].files[*].path` in the plan. If it does not appear in any StepNode AND there is no `step-added` or `scope-change` amendment in `amendments[]` documenting it: BLOCKER. Files with status `D` (deleted) that are absent from StepNodes: check for a `step-removed` amendment. `step-completed` amendments are compliance records, not deviations.
```

- [ ] **Step 4: Verify all three additions are present**

Run: `grep -c 'Version gate\|V2 path' .github/skills/review/SKILL.md`
Expected: 3 (one version gate + two V2 path labels)

- [ ] **Step 5: Commit review upgrade**

```bash
git add .github/skills/review/SKILL.md
git commit -m "feat: upgrade review skill with v2 version gate, typed requirement traceability, amendment-based deviation check"
```

---

### Task 5: Upgrade context-packet skill to v2

**Files:**
- Modify: `.github/skills/context-packet/SKILL.md`

Changes: version detection in Step 1, v2 file count + manifest extraction from typed fields in Steps 2–3, decision selection rule as Step 6.5, coverage formula replacement in Step 7, cross-repo signals as Step 7.5, `## Cross-Repo Signals` section in Step 8 template.

- [ ] **Step 1: Add version detection to Step 1**

In `.github/skills/context-packet/SKILL.md`, find `## Step 1: Read Conventions and Locate the Plan`. The section ends with:

```
If no plan file is found for the ticket ID, stop and say: "No plan file found for [ticket-id] in [PLANS_PATH]. Ensure the plan exists before generating a context packet."
```

Append immediately after:

```

**Version detection:** After reading the plan file, check its `schema_version` frontmatter. Store as PLAN_VERSION.
- `schema_version: 2` → PLAN_VERSION = 2. Use v2 typed-field paths in Steps 2, 3, 6.5, and 7.
- Absent → PLAN_VERSION = 1. Use existing prose extraction paths.
```

- [ ] **Step 2: Add v2 file count path to Step 2 trigger condition 3**

In `.github/skills/context-packet/SKILL.md`, find condition 3 in Step 2:

```
3. **Phase file count:** Find the section for the requested phase (e.g. `## Phase 2:`) in the plan. Count the files listed in its `**Files in this phase:**` block. Are there ≥ 4 files? If < 4 → stop: "Phase [N] has [count] files. Context packets are generated for phases with ≥ 4 files only."
```

Replace with:

```
3. **Phase file count:**
   - **V2 (PLAN_VERSION = 2):** Locate the phase entry where `phases[*].id = N`. Count total `FileRef` entries across `phases[N-1].steps[*].files` (all steps in that phase).
   - **V1 (PLAN_VERSION = 1):** Find the section `## Phase [N]:` and count files listed in its `**Files in this phase:**` block.
   Are there ≥ 4 files? If < 4 → stop: "Phase [N] has [count] files. Context packets are generated for phases with ≥ 4 files only."
```

- [ ] **Step 3: Add v2 file manifest extraction to Step 3**

In `.github/skills/context-packet/SKILL.md`, find `## Step 3: Extract Phase File Manifest`. The section currently starts with:

```
From the plan's phase section, extract the exact list of files listed under `**Files in this phase:**`. Store as PHASE_FILES.
```

Replace that opening sentence with:

```
**V2 (PLAN_VERSION = 2):** Read `phases[*].id = N` entry. Collect all `steps[*].files[*].path` values across every step in that phase. Exclude paths where `operation: 'delete'` (deleted files have no module context to load). Store as PHASE_FILES. No text parsing required.

**V1 (PLAN_VERSION = 1):** From the plan's phase section, extract the exact list of files listed under `**Files in this phase:**`. Store as PHASE_FILES.
```

- [ ] **Step 4: Insert decision selection rule as Step 6.5**

In `.github/skills/context-packet/SKILL.md`, find `## Step 7: Compute Coverage Confidence`. Insert this new section immediately before it:

```
## Step 6.5: Select Decisions for Context Packet (PLAN_VERSION = 2 only)

Compute the set of decisions to include in `## Relevant Decisions`:

```
phase_req_ids  = union of step.requirement_ids for all steps where phases[*].id = N
decision_ids_A = { req.source_decision
                   for req in requirements
                   where req.id ∈ phase_req_ids AND req.source_decision != null }
decision_ids_B = { d.id for d in decisions where d.reversibility = 'low' }
included       = decisions where id ∈ (decision_ids_A ∪ decision_ids_B)
```

Store as SELECTED_DECISIONS. Skip entirely for PLAN_VERSION = 1 (all decisions from loaded module pages apply, existing behavior).

```

- [ ] **Step 5: Replace Step 7 coverage confidence with typed formula**

In `.github/skills/context-packet/SKILL.md`, replace the entire `## Step 7: Compute Coverage Confidence` section (from the `## Step 7` heading through the final `prepend` block, stopping before `## Step 8`) with:

```
## Step 7: Compute Coverage Confidence

**V2 (PLAN_VERSION = 2):** Apply the typed formula:

```
all_files  = all FileRef entries in phases[*].id=N steps
none_count = count of f in all_files where file-to-module mapping = UNKNOWN
total      = count of all_files

if none_count / total > 0.5  → CONFIDENCE = 'low'
if none_count > 0            → CONFIDENCE = 'medium'
else                         → CONFIDENCE = 'high'
```

**File path → module mapping rule (v2 only):**
```
candidates(path) = { m for m in codebase_index.modules
                       where any source_path ∈ m.source_paths is a prefix of path }

resolve(path):
  |candidates| = 1  → use that module
  |candidates| = 0  → UNKNOWN
  |candidates| > 1  → longest matching prefix wins;
                      tie → higher Reach score wins;
                      tie → alphabetically first module name (deterministic)
```

**V1 (PLAN_VERSION = 1):** Use existing rules (first match wins: unresolved majority → low, stale index → low, index age > 30 days → low, one or more unresolved → medium, all resolved + index ≤ 7 days + not stale → high).

If CONFIDENCE = `low`, prepend to the packet:
```
> ⚠️ **Low coverage confidence** — index may be stale or missing modules. Run `/index codebase` and `/index knowledge` before relying on this packet.
```

If CONFIDENCE = `medium`, prepend:
```
> ℹ️ **Medium coverage confidence** — [reason]. Verify unresolved files manually if they contain constraints relevant to this phase.
```

```

- [ ] **Step 6: Insert cross-repo signals as Step 7.5**

In `.github/skills/context-packet/SKILL.md`, find `## Step 8: Write context/[ticket-id]/phase-[N]-context.md`. Insert this new section immediately before it:

```
## Step 7.5: Load Cross-Repo Signals (if imports.md exists)

Read `[KNOWLEDGE_PATH]/../imports.md`. If this file does not exist: skip this step entirely — set CROSS_REPO_SIGNALS = [].

If the file exists, run this resolution for each `import_source` in the file:

```
For each phase_module in PHASE_MODULES:
  If phase_module ∈ import_source.scope (exact string match):
    Read import_source.exports_path
    For each exported_topic where phase_module ∈ exported_topic.modules (exact string match):
      If exported_topic.weight ∈ {HIGH, MEDIUM}
      AND days_since(exported_topic.last_updated) <= 90:
        → add to CROSS_REPO_SIGNALS
```

Match is exact string equality only. Naming divergence between repos produces no match.
CROSS_REPO_SIGNALS do NOT affect CONFIDENCE calculation.
CROSS_REPO_SIGNALS do NOT count against the knowledge loading budget.

```

- [ ] **Step 7: Add ## Cross-Repo Signals section to Step 8 template**

In `.github/skills/context-packet/SKILL.md`, find the Step 8 template. Locate this block:

```
    ## Knowledge Signals

    _(High-weight historical signals for modules in scope. Summary and pattern only —
    full entry list at [KNOWLEDGE_PATH]/[topic].md.)_
```

Insert this block IMMEDIATELY BEFORE `## Knowledge Signals`:

```
    [If CROSS_REPO_SIGNALS is non-empty:]
    ## Cross-Repo Signals

    _(Advisory only — signals from external repos whose exported module names match this phase scope. Cannot block execution, modify artifact fields, create contradicts relationships, or affect coverage confidence. Exact module name match only.)_

    [For each signal in CROSS_REPO_SIGNALS:]
    ### [topic_id] — [title] | [weight] | [type]
    _Source repo: [repo name] | Modules: [modules list] | Last updated: [last_updated]_

    [summary]

    ---

```

Also append to the Rules block at the bottom of Step 8:
```
- `## Cross-Repo Signals` appears only when CROSS_REPO_SIGNALS is non-empty. Omit entirely when empty — no placeholder.
- Cross-repo signals are advisory only. They cannot create `contradicts` relationships with local topics and do not affect coverage confidence.
```

- [ ] **Step 8: Verify all context-packet changes**

Run: `grep -c 'PLAN_VERSION\|decision_ids_A\|CROSS_REPO_SIGNAL\|none_count\|Step 6.5\|Step 7.5' .github/skills/context-packet/SKILL.md`
Expected: 6 matches (one per key variable/heading)

- [ ] **Step 9: Commit context-packet upgrade**

```bash
git add .github/skills/context-packet/SKILL.md
git commit -m "feat: upgrade context-packet skill to v2 typed fields, coverage formula, decision selection rule, cross-repo signals"
```

---

## Phase 3: Execution Upgrade

**Files:**
- Modify: `.github/skills/execution/SKILL.md`

---

### Task 6: Upgrade execution skill to v2

**Files:**
- Modify: `.github/skills/execution/SKILL.md`

Changes: version gate in Step 1, context packet auto-trigger as Step 1.5, Stage 1 exact comparison + Rule 2 incidental grace in Step 2b/2c, context reset block from amendments (Rule 3) in Step 2b, `step-completed` amendment write after each verify, lean conventions injection from `risk_signals[]` in Step 2c.

- [ ] **Step 1: Add version detection as step 5 in Step 1**

In `.github/skills/execution/SKILL.md`, find `## Step 1: Read the Plan and Decide Mode`. The section has 4 numbered steps ending with announcing the mode. After the announcement text (after step 4 ending with `"14 files across 4 phases. Using **sub-agent mode**..."`), add:

```
5. **Version detection:** Read the plan file's `schema_version` frontmatter. Store as PLAN_VERSION.
   - `schema_version: 2` → PLAN_VERSION = 2. Use v2 typed paths throughout this skill.
   - Absent → PLAN_VERSION = 1. All existing paths apply unchanged.
   If PLAN_VERSION = 2: run `/validate-artifact [plan-path]` silently. BLOCK if validation fails.
```

- [ ] **Step 2: Add context packet auto-trigger as Step 1.5**

In `.github/skills/execution/SKILL.md`, find `## Step 1b: Coverage Confidence Announcement`. Insert this new section IMMEDIATELY BEFORE Step 1b:

```
## Step 1.5: Context Packet Auto-Trigger (PLAN_VERSION = 2 only)

For each phase about to execute, before any step runs, check both conditions:
1. `plan.execution.mode` = `'phased-inline'` or `'phased-subagent'`
2. Total FileRef count across `phases[*].id=N .steps[*].files` ≥ 4

If both hold: silently invoke the context-packet skill for this phase (do not ask the engineer — run it as an internal step). Announce the result: "Context packet auto-triggered for Phase [N]: [N] files across [N] modules. Coverage: [level]."

If conditions are not met (inline mode, or < 4 files): announce: "Phase [N]: [N] file(s) — below auto-trigger threshold. Proceeding with codebase search protocol."

For PLAN_VERSION = 1: no change — context packet is triggered manually via `/context-packet` command.

```

- [ ] **Step 3: Replace Stage 1 check instructions in Step 2b**

In `.github/skills/execution/SKILL.md`, find Step 2b. The current Stage 1 instruction is:

```
Before showing the checkpoint, compile two lists for Stage 1: **Plan listed** — all files from this phase's **Files in this phase:** section in the plan; **Actually changed** — all files you modified during this phase's steps.
```

Replace with:

```
**Stage 1 — Spec compliance:**

**V2 (PLAN_VERSION = 2):**
- `plan_listed` = all `files[*].path` values from `phases[*].id=N .steps[*].files` (typed array, no text parsing)
- `actually_changed` = paths in `git diff --name-status HEAD~1` with status `A` (added), `M` (modified), or `R` (renamed). Paths with status `D` (deleted): check these against plan_listed separately — a `D` path not in plan_listed and not covered by a `step-removed` amendment = Stage 1 FAIL.
- Classify each path in `actually_changed`:
  - Present in `plan_listed` → expected
  - Absent from `plan_listed` AND status is NOT `D` AND path matches a pattern in `conventions/SKILL.md: Incidental file patterns` AND path is not in any StepNode across any phase → `incidental` (logged in checkpoint under `Incidental files:`, NOT a failure)
  - Absent from `plan_listed` AND does not meet all incidental conditions → `unlisted` → Stage 1 FAIL
- Stage 1 PASS: all `actually_changed` paths are expected or incidental.

**V1 (PLAN_VERSION = 1):** Compile two lists: **Plan listed** — all files from this phase's `**Files in this phase:**` section in the plan; **Actually changed** — all files modified during this phase's steps.
```

- [ ] **Step 4: Replace context reset block in Step 2b with amendment-sourced Rule 3**

In `.github/skills/execution/SKILL.md`, find the context reset block template in Step 2b. The current template starts with `--- Context Reset ---` and ends with `Next phase relies ONLY on: plan file, context packet, and this summary.`

Replace the entire template (keep the surrounding instruction about when to show it and the `Treat the conversation above this block as non-authoritative` instruction, but replace the template content between them) with:

```
--- Context Reset ---

Completed Phase: [N]

Completed steps (from step-completed amendments, phase=[N]):
[For each Amendment where type='step-completed' AND phase=N, in id order:
  - [amendment.step_id]: [amendment.description]]

Changes from plan (from non-step-completed amendments, phase=[N]):
[For each Amendment where type ∈ {step-added, step-removed, verify-override, decision-conflict, scope-change} AND phase=N:
  - [amendment.type]: [amendment.description]
  OR "none" if no such amendments exist for phase N]

Next phase scope ([phases[*].id=N+1 .name]):
[One bullet per path in phases[*].id=N+1 .steps[*].files[*].path]

Discard: all prior phase execution details, test outputs, and debug/retry logs.
Next phase relies ONLY on: plan file, this block, and the auto-loaded context packet.
```

Add this note on a new line after the template:
```
_Rule 3: this block is generated exclusively from (1) step-completed amendments for phase N, (2) other amendments for phase N, and (3) next phase StepNode file paths. No open-ended session synthesis._
```

- [ ] **Step 5: Add step-completed amendment write after each step's verify**

In `.github/skills/execution/SKILL.md`, find the inline execution rules in Step 2a. After:

```
2. After each step: run the test command. Do not proceed if any test fails.
```

Add:

```
2a. **V2 only (PLAN_VERSION = 2):** When a step's verify command passes, append a `step-completed` amendment to the plan file's `amendments:` YAML array. Set `id: A{N}` where N = count of existing amendments + 1 (first amendment is A1; numbers never reused). Example:
    ```yaml
    - id: "A3"
      step_id: "P1.S2"
      phase: 1
      type: step-completed
      description: "Write TokenValidator class — verify passed: 3 tests, 0 failures"
      added_by: execution
    ```
```

Also add the same instruction in the phased-inline execution rules in Step 2b (after the step execution instruction there), and in the sub-agent dispatch return handling in Step 2c (sub-agent writes step-completed entries as part of its return output, parent session appends them to the plan file).

- [ ] **Step 6: Replace text-scan conventions injection with risk_signals[] in Step 2c**

In `.github/skills/execution/SKILL.md`, find the dynamic conventions injection block in Step 2c. It starts with:

```
**Before building the sub-agent prompt — dynamic conventions injection:**
Scan each step's text in this phase for these keyword patterns.
```

Replace the entire block (from that heading through `If \`conventions/SKILL.md\` does not contain a matching section: no injection. Do not fail or warn.`) with:

```
**Before building the sub-agent prompt — conventions injection:**

**V2 (PLAN_VERSION = 2) — lean injection from risk_signals[]:**

```
Fixed (always injected):
  test_command   ← conventions.Test command
  commit_format  ← conventions.Commit Message Format
  lint_command   ← conventions.Lint command (or "none")

Risk-signal sections (per phase):
  For each signal ∈ union of step.risk_signals[] across all steps in this phase:
    → exact header match against conventions section headers (case-insensitive)
    → include matched section; skip silently if no match found
```

No step-text scan. `StepNode.risk_signals[]` is the sole injection signal source.

**V1 (PLAN_VERSION = 1) — keyword text-scan:**
Scan each step's text for keyword patterns (error/exception/validate → `## Error Handling`; endpoint/request/API → `## API Conventions`; migration/schema/database → `## Data Conventions`; exact framework name match → that section). If `conventions/SKILL.md` does not contain a matching section: no injection.
```

- [ ] **Step 7: Verify all execution skill changes**

Run: `grep -c 'PLAN_VERSION\|step-completed\|risk_signals\|Rule 3\|auto-trigger\|plan_listed' .github/skills/execution/SKILL.md`
Expected: at least 6 matches (one per key term)

- [ ] **Step 8: Commit execution skill upgrade**

```bash
git add .github/skills/execution/SKILL.md
git commit -m "feat: upgrade execution skill to v2 version gate, typed Stage 1 + Rule 2 grace, amendment-sourced context reset, risk_signals injection, step-completed tracking"
```

---

## Phase 4: Planning Upgrade

**Files:**
- Modify: `.github/skills/planning/SKILL.md`

---

### Task 7: Upgrade planning skill to v2

**Files:**
- Modify: `.github/skills/planning/SKILL.md`

Changes: version gate + `/validate-artifact` before any work, typed `problem.classification` read for retrieval split, typed `decisions[*].constraints[]` for conflict check, v2 PlanArtifact YAML output template.

- [ ] **Step 1: Insert version gate section before "Before Writing a Single Step"**

In `.github/skills/planning/SKILL.md`, find `## Before Writing a Single Step`. Insert this new section IMMEDIATELY BEFORE it:

```
## Version Gate (run before any other step)

Read the spec file's `schema_version` frontmatter. Store as SPEC_VERSION.

- **`schema_version: 2`:** run `/validate-artifact [spec-path] [brainstorm-path]` silently (includes immutability check against brainstorm source). BLOCK if validation fails. Use v2 typed-field paths throughout this skill.
- **Absent or other:** SPEC_VERSION = 1. Use existing prose extraction throughout. Version gates do not apply.

```

- [ ] **Step 2: Add typed problem.classification read in Intelligence Retrieval**

In `.github/skills/planning/SKILL.md`, find the Intelligence Retrieval section. After step 2 (the skip/mandatory check), add:

```
3. **V2 (SPEC_VERSION = 2):** Read `problem.classification` from the spec artifact as a typed field. Pass it directly to the retrieval protocol's classification parameter — no prose inference:
   - `new-feature` → retrieval priority: system › empirical › external
   - `modification` or `bug-fix` → retrieval priority: empirical › system › external
```

- [ ] **Step 3: Add typed conflict check in Intelligence Retrieval section 3d**

In `.github/skills/planning/SKILL.md`, find step 3d in Intelligence Retrieval:

```
   d. Run the Decision Conflict Check (same protocol as spec-writing): read `## Decisions` from every loaded module page; compare against the spec's Architecture section; flag and resolve conflicts before writing any steps.
```

Replace with:

```
   d. **Decision Conflict Check:**
      - **V2 (SPEC_VERSION = 2):** Read `decisions[*].constraints[]` typed array from the spec artifact. Compare each constraint against `## Known Constraints` sections in loaded module pages. Flag where a spec constraint directly contradicts a module constraint.
      - **V1 (SPEC_VERSION = 1):** Read `## Decisions` from every loaded module page; compare against the spec's `## Architecture / Design Decisions` prose.
      Note (both versions): module pages are v1 prose. This check remains partially deterministic (typed spec input vs. prose module pages) until module pages adopt v2 typed decisions — acknowledged limitation in the design spec.
```

- [ ] **Step 4: Add v2 PlanArtifact output template**

In `.github/skills/planning/SKILL.md`, find `## Plan Structure`. Locate the section's v1 Markdown template (the `~~~markdown` block ending with `~~~`). After the closing `~~~`, add:

```

**V2 output template (SPEC_VERSION = 2):** Use this YAML PlanArtifact instead of the v1 Markdown template above. Carry all spec fields verbatim — do not re-derive.

~~~yaml
---
ticket: [TICKET-ID]
phase: plan
schema_version: 2
created: [YYYY-MM-DD]
status: draft
source: [spec-file-path]
---

# ── INHERITED FROM SPEC — carry verbatim, byte-for-byte ──────────────────────
problem:
  id: "[from spec]"
  classification: "[from spec]"
  summary: "[from spec]"
  scope:
    - module: "[from spec]"
      known: [from spec]
  acceptance_signals:
    - "[from spec]"

open_decisions:
  [from spec — verbatim]

decisions:
  [from spec — verbatim]

requirements:
  [from spec — verbatim]

spec_constraints:
  [from spec — verbatim]

out_of_scope:
  [from spec — verbatim]

# ── OWNED BY PLANNING — write only these fields ────────────────────────────────
execution:
  mode: "[inline|phased-inline|phased-subagent]"
  justification: "[one sentence justifying mode choice]"
  retrieval: "[ran|skipped]"
  retrieval_justification: "[reason if skipped; empty string if retrieval ran]"

retrieval_constraints:
  - "[constraint discovered from module pages — source: module-page: ModuleName]"

phases:
  - id: 1
    name: "[Phase name — logical unit description]"
    steps:
      - id: "P1.S1"
        phase: 1
        description: "[max 300 chars — what this step does]"
        files:
          - path: "[exact/file/path.ext]"
            operation: "[create|modify|delete]"
        depends_on: []
        verify: "[runnable command that proves this step complete]"
        risk_signals: []
        review_prompt: "[specific question for engineer to check after this step]"
        requirement_ids: ["R1"]

amendments: []
~~~

**Immutability rule:** All fields above the `# ── OWNED BY PLANNING` comment are inherited verbatim from the spec. Do not modify them. `/validate-artifact` at the consuming phase will byte-for-byte compare these fields against the spec source and BLOCK on any mismatch.
```

- [ ] **Step 5: Verify all planning skill changes**

Run: `grep -c 'SPEC_VERSION\|schema_version: 2\|retrieval_constraints\|risk_signals\|phase_resolved' .github/skills/planning/SKILL.md`
Expected: at least 4 distinct matches

- [ ] **Step 6: Commit planning skill upgrade**

```bash
git add .github/skills/planning/SKILL.md
git commit -m "feat: upgrade planning skill to v2 version gate, typed classification + conflict check, PlanArtifact output template"
```

---

## Phase 5: Producer Upgrades

**Files:**
- Modify: `.github/skills/spec-writing/SKILL.md`
- Modify: `.github/skills/brainstorming/SKILL.md`

---

### Task 8: Upgrade spec-writing skill to v2

**Files:**
- Modify: `.github/skills/spec-writing/SKILL.md`

Changes: version gate + `/validate-artifact` on brainstorm input, v2 typed `open_decisions[]` read path, v2 SpecArtifact YAML output template.

- [ ] **Step 1: Insert version gate before main instructions**

In `.github/skills/spec-writing/SKILL.md`, find the main instruction block. It starts with:

```
You are in spec phase. Create a design specification before any code is written.
```

Insert this new section IMMEDIATELY BEFORE that line:

```
## Version Gate (run before any other step)

Read the brainstorm artifact file's `schema_version` frontmatter. Store as BRAINSTORM_VERSION.

- **`schema_version: 2`:** run `/validate-artifact [brainstorm-path]` silently. BLOCK if validation fails. Use v2 typed-field paths in this skill.
- **Absent or other:** BRAINSTORM_VERSION = 1. Use existing prose extraction throughout.

```

- [ ] **Step 2: Add v2 open_decisions read path in Inputs section**

In `.github/skills/spec-writing/SKILL.md`, find the Inputs instruction:

```
Read the file. Extract: problem, success criteria, constraints, risks. The ticket ID is in the frontmatter.
```

Append after this line:

```
**V2 (BRAINSTORM_VERSION = 2):** Read typed fields directly — no prose extraction:
- `problem` → inherit verbatim into SpecArtifact (do not re-derive or paraphrase)
- `open_decisions[]` → each entry has `question` and `options[]`; resolve each into a `DecisionRecord` with `chosen`, `rejected[]` (one entry per unchosen option with reason), `constraints[]` (required if `reversibility='low'`), `reversibility`, `phase_resolved: 'spec'`
```

- [ ] **Step 3: Add v2 SpecArtifact output template to Spec Structure section**

In `.github/skills/spec-writing/SKILL.md`, find `## Spec Structure`. Locate the v1 Markdown template (the code block starting with ` ```markdown ` and the frontmatter). After the closing ` ``` ` of that template block, add:

```

**V2 output template (BRAINSTORM_VERSION = 2):** Use this YAML SpecArtifact instead of the v1 Markdown template above. Carry brainstorm fields verbatim.

~~~yaml
---
ticket: [TICKET-ID]
phase: spec
schema_version: 2
created: [YYYY-MM-DD]
status: draft
source: [brainstorm-file-path]
---

# ── INHERITED FROM BRAINSTORM — carry verbatim, byte-for-byte ─────────────────
problem:
  id: "[from brainstorm]"
  classification: "[from brainstorm]"
  summary: "[from brainstorm]"
  scope:
    - module: "[from brainstorm]"
      known: [from brainstorm]
  acceptance_signals:
    - "[from brainstorm]"

open_decisions:
  [from brainstorm — verbatim]

# ── OWNED BY SPEC-WRITING — write only these fields ───────────────────────────
decisions:
  - id: "D1"
    question: "[from open_decisions[0].question]"
    chosen: "[chosen option]"
    rejected:
      - option: "[unchosen option A]"
        reason: "[why this was not chosen]"
    constraints: []          # REQUIRED: min 1 entry when reversibility='low'
    reversibility: "[low|medium|high]"
    phase_resolved: "spec"

requirements:
  - id: "R1"
    text: "[specific testable requirement — X when Y]"
    acceptance: "[runnable command that proves this requirement]"
    classification: "[functional|constraint|non-functional]"
    source_decision: "D1"    # null if not derived from a decision

spec_constraints:
  - "[hard constraint not derived from any decision]"

out_of_scope:
  - "[explicitly excluded item]"
~~~

**Immutability rule:** All fields above `# ── OWNED BY SPEC-WRITING` are inherited verbatim from the brainstorm file. Do not modify them. `/validate-artifact` at the planning phase will BLOCK on any mismatch.

**Decision conflict check (V2):** After writing `decisions[]`, compare `decisions[*].constraints[]` typed values against `## Known Constraints` sections in loaded module pages (same check as V1 but uses typed input instead of prose extraction).
```

- [ ] **Step 4: Verify all spec-writing changes**

Run: `grep -c 'BRAINSTORM_VERSION\|schema_version: 2\|open_decisions\|phase_resolved\|spec_constraints' .github/skills/spec-writing/SKILL.md`
Expected: at least 4 distinct matches

- [ ] **Step 5: Commit spec-writing skill upgrade**

```bash
git add .github/skills/spec-writing/SKILL.md
git commit -m "feat: upgrade spec-writing skill to v2 version gate, typed open_decisions read, SpecArtifact output template"
```

---

### Task 9: Upgrade brainstorming skill to v2

**Files:**
- Modify: `.github/skills/brainstorming/SKILL.md`

Change: Add v2 BrainstormArtifact YAML template alongside the existing v1 Markdown template in the Convergence section.

- [ ] **Step 1: Add v2 artifact template in Convergence section**

In `.github/skills/brainstorming/SKILL.md`, find the Convergence section save instruction:

```
2. Read `Brainstorms:` path from `.github/skills/conventions/SKILL.md`.
2. Save the brainstorm artifact to `[brainstorms-path]/YYYY-MM-DD-[ticket-id]-brainstorm.md` using this exact template — fill in every field:
```

After the entire v1 template block (the indented section ending at the last indented line), add:

```
   **V2 template (use for all new brainstorms — schema_version: 2):**

        ---
        ticket: [TICKET-ID]
        phase: brainstorm
        schema_version: 2
        created: [YYYY-MM-DD]
        status: complete
        ---

        problem:
          id: "[TICKET-ID]"
          classification: "[new-feature|modification|bug-fix]"
          summary: "[one specific problem sentence, max 200 chars — specific enough to write a failing test]"
          scope:
            - module: "[module-name-from-codebase-index]"
              known: [true if module in codebase index; false if not yet indexed]
          acceptance_signals:
            - "[X happens when Y — testable, from convergence criteria]"

        open_decisions:
          - question: "[unresolved question from the conversation]"
            options:
              - "[option A]"
              - "[option B]"

   **Field rules:**
   - `problem.id`: the ticket ID
   - `problem.classification`: `new-feature` = new capability; `modification` = changes existing behavior; `bug-fix` = defect
   - `problem.summary`: max 200 chars; specific enough that you could write a failing test from it
   - `scope[*].module`: lowercase hyphenated names from the codebase index; use `known: false` for modules not yet indexed
   - `acceptance_signals`: from the conversation's convergence — each must pass the "X happens when Y" testability check
   - `open_decisions`: unresolved questions that need a decision in spec-writing. Each needs `question` and at least 2 `options`. Omit the array entirely (or leave as `[]`) if all questions were resolved during the brainstorm.
```

- [ ] **Step 2: Verify brainstorming v2 template was added**

Run: `grep -c 'schema_version: 2\|open_decisions\|acceptance_signals\|BRAINSTORM_VERSION' .github/skills/brainstorming/SKILL.md`
Expected: at least 3 matches (the v2 template fields; BRAINSTORM_VERSION is in spec-writing not here — expect 3)

- [ ] **Step 3: Commit brainstorming skill upgrade**

```bash
git add .github/skills/brainstorming/SKILL.md
git commit -m "feat: upgrade brainstorming skill to v2 BrainstormArtifact output template"
```

---

## Task 10: End-to-End Smoke Test

**Files:** none modified — verification only

This task proves the v2 chain works end-to-end. All 9 skill files must be committed before running this.

- [ ] **Step 1: Create a dummy v2 brainstorm artifact**

Write `docs/superpowers/specs/2026-04-25-v2-smoke-test-brainstorm.md` with this content:

```yaml
---
ticket: SMOKE-001
phase: brainstorm
schema_version: 2
created: 2026-04-25
status: complete
---

problem:
  id: "SMOKE-001"
  classification: "new-feature"
  summary: "Add a /health endpoint to the API that returns 200 when the service is up."
  scope:
    - module: "api"
      known: true
  acceptance_signals:
    - "GET /health returns HTTP 200 with body {status: ok} when service is running"

open_decisions:
  - question: "Should /health check downstream dependencies or be shallow?"
    options:
      - "Shallow check — always returns 200 as long as the process is up"
      - "Deep check — validates DB and cache connectivity before responding"
```

- [ ] **Step 2: Run /validate-artifact on the brainstorm**

Invoke: `/validate-artifact docs/superpowers/specs/2026-04-25-v2-smoke-test-brainstorm.md`

Expected output:
```
Artifact at docs/superpowers/specs/2026-04-25-v2-smoke-test-brainstorm.md: PASS — all checks passed.
```

If any check fails: the relevant skill file was not updated correctly. Check that the validate-artifact skill's Check 1 correctly detects `schema_version: 2`.

- [ ] **Step 3: Create a dummy v2 spec artifact**

Write `docs/superpowers/specs/2026-04-25-v2-smoke-test-spec.md` with this content (verifies brainstorm immutability — `problem` and `open_decisions` carried verbatim):

```yaml
---
ticket: SMOKE-001
phase: spec
schema_version: 2
created: 2026-04-25
status: draft
source: docs/superpowers/specs/2026-04-25-v2-smoke-test-brainstorm.md
---

problem:
  id: "SMOKE-001"
  classification: "new-feature"
  summary: "Add a /health endpoint to the API that returns 200 when the service is up."
  scope:
    - module: "api"
      known: true
  acceptance_signals:
    - "GET /health returns HTTP 200 with body {status: ok} when service is running"

open_decisions:
  - question: "Should /health check downstream dependencies or be shallow?"
    options:
      - "Shallow check — always returns 200 as long as the process is up"
      - "Deep check — validates DB and cache connectivity before responding"

decisions:
  - id: "D1"
    question: "Should /health check downstream dependencies or be shallow?"
    chosen: "Shallow check — always returns 200 as long as the process is up"
    rejected:
      - option: "Deep check — validates DB and cache connectivity before responding"
        reason: "Adds latency and couples health endpoint to DB availability; not required by acceptance signal"
    constraints: []
    reversibility: "medium"
    phase_resolved: "spec"

requirements:
  - id: "R1"
    text: "GET /health returns HTTP 200 with body {status: ok} when service is running"
    acceptance: "curl -s http://localhost:8080/health | jq '.status' | grep ok"
    classification: "functional"
    source_decision: "D1"

spec_constraints: []

out_of_scope:
  - "Deep health checks of downstream dependencies"
```

- [ ] **Step 4: Run /validate-artifact on the spec with the brainstorm as source**

Invoke: `/validate-artifact docs/superpowers/specs/2026-04-25-v2-smoke-test-spec.md docs/superpowers/specs/2026-04-25-v2-smoke-test-brainstorm.md`

Expected: `PASS — all checks passed.`

If immutability check fails: the spec artifact has modified inherited fields. The smoke test file demonstrates what to look for when planning/spec-writing skills produce v2 artifacts.

- [ ] **Step 5: Verify referential integrity enforcement**

Create `docs/superpowers/specs/2026-04-25-v2-smoke-test-broken.md` as a copy of the spec above, but change `source_decision: "D1"` to `source_decision: "D99"`:

```yaml
requirements:
  - id: "R1"
    text: "GET /health returns HTTP 200 with body {status: ok} when service is running"
    acceptance: "curl -s http://localhost:8080/health | jq '.status' | grep ok"
    classification: "functional"
    source_decision: "D99"
```

Run: `/validate-artifact docs/superpowers/specs/2026-04-25-v2-smoke-test-broken.md`

Expected:
```
Artifact at [...]: FAIL — 1 violation(s) found:
1. requirements[0].source_decision: 'D99' not found in decisions[*].id
```

If PASS is returned: Check 3 (referential integrity) was not correctly added to validate-artifact/SKILL.md.

- [ ] **Step 6: Clean up smoke test artifacts**

```bash
rm docs/superpowers/specs/2026-04-25-v2-smoke-test-brainstorm.md
rm docs/superpowers/specs/2026-04-25-v2-smoke-test-spec.md
rm docs/superpowers/specs/2026-04-25-v2-smoke-test-broken.md
```

- [ ] **Step 7: Commit final state**

```bash
git status
git commit -m "feat: complete v2 artifact evolution — all 9 skills upgraded, smoke tests passed"
```

---

## Testing Checklist (run after all tasks complete)

- [ ] All 9 files present with expected changes:
  - `grep -rn 'schema_version' .github/skills/ | grep -v '.DS_Store'` — lines in brainstorming, spec-writing, planning, execution, review, context-packet, validate-artifact
- [ ] SCHEMA.md is the sole primitive definition source:
  - `grep -rn 'interface ProblemRecord' .github/skills/` — expected: only in SCHEMA.md
- [ ] validate-artifact has all 5 checks:
  - `grep -c '## Check [1-5]' .github/skills/validate-artifact/SKILL.md` — expected: 5
- [ ] Consumer skills committed before producers (Rule 1):
  - `git log --oneline .github/skills/review/SKILL.md .github/skills/context-packet/SKILL.md .github/skills/execution/SKILL.md .github/skills/planning/SKILL.md .github/skills/spec-writing/SKILL.md .github/skills/brainstorming/SKILL.md` — review commit appears first (most recent = last in log)
- [ ] V1 fallback paths exist in each upgraded skill:
  - `grep -c 'PLAN_VERSION = 1\|SPEC_VERSION = 1\|BRAINSTORM_VERSION = 1' .github/skills/execution/SKILL.md .github/skills/planning/SKILL.md .github/skills/spec-writing/SKILL.md` — expected: at least one line per file
- [ ] Conventions has incidental file patterns field:
  - `grep 'Incidental file patterns' .github/skills/conventions/SKILL.md` — expected: one line

## Rollback Plan

Each task is committed independently. To roll back a single skill:
```bash
git log --oneline .github/skills/[skill-name]/SKILL.md   # find pre-upgrade commit hash
git checkout [pre-upgrade-hash] -- .github/skills/[skill-name]/SKILL.md
git commit -m "revert: roll back [skill-name] to v1-only"
```

The system is valid at any partial upgrade state. Version gates route each artifact to the correct path — a partially-upgraded set of skills does not break any existing workflow. Rolling back the brainstorming skill stops new v2 BrainstormArtifacts from being created, but does not affect any in-flight tickets.
