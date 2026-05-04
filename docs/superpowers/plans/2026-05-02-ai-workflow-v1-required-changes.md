# AI Workflow V1 Required Changes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the current `.github/ai-workflow` proto-v1 into the agreed v1 architecture: manifest-owned workflow graph, repo-local setup/config, first-class context packets, durable execution checkpoints, and strict artifact-driven verify/review behavior.

**Architecture:** Keep the existing split between manifest, contracts, policies, schemas, validators, prompts, and skills. Extend that runtime rather than rewriting it. Add `/setup-workflow` and `/context-packet` as first-class commands, make `PlanArtifact` rich enough to drive deterministic context gating, and require durable `ExecutionCheckpointArtifact` state for every `/execute-plan` run.

**Tech Stack:** YAML manifests/contracts/policies, JSON schemas, Python validators, Markdown prompts/skills/docs

---

## File Map

**Create:**
- `.github/ai-workflow/contracts/commands/setup-workflow.v1.yaml`
- `.github/ai-workflow/contracts/commands/context-packet.v1.yaml`
- `.github/ai-workflow/skills/setup-workflow/SKILL.md`
- `.github/ai-workflow/skills/context-packet/SKILL.md`
- `.github/ai-workflow/schemas/config.schema.json`
- `.github/ai-workflow/schemas/context-packet.schema.json`
- `.github/ai-workflow/schemas/execution-checkpoint.schema.json`
- `.github/ai-workflow/policies/context-policy.v1.yaml`
- `.github/ai-workflow/validators/validate-context-packet`
- `.github/ai-workflow/validators/validate-compatibility`
- `.github/prompts/setup-workflow.prompt.md`
- `.github/prompts/context-packet.prompt.md`
- `.github/workflow/config.yaml`
- `.github/ai-workflow/artifacts/context/.gitkeep`
- `.github/ai-workflow/artifacts/execution/.gitkeep`
- `.github/ai-workflow/artifacts/evidence/.gitkeep`

**Modify:**
- `.github/ai-workflow/manifest.yaml`
- `.github/ai-workflow/schemas/manifest.schema.json`
- `.github/ai-workflow/schemas/plan.schema.json`
- `.github/ai-workflow/schemas/brainstorm.schema.json`
- `.github/ai-workflow/schemas/quick-task.schema.json`
- `.github/ai-workflow/schemas/spec.schema.json`
- `.github/ai-workflow/schemas/verification.schema.json`
- `.github/ai-workflow/schemas/review.schema.json`
- `.github/ai-workflow/contracts/commands/write-plan.v1.yaml`
- `.github/ai-workflow/contracts/commands/execute-plan.v1.yaml`
- `.github/ai-workflow/contracts/commands/verify.v1.yaml`
- `.github/ai-workflow/contracts/commands/review.v1.yaml`
- `.github/ai-workflow/contracts/commands/quick-task.v1.yaml`
- `.github/ai-workflow/policies/workflow-policy.v1.yaml`
- `.github/ai-workflow/policies/retrieval-policy.v1.yaml`
- `.github/ai-workflow/validators/bootstrap`
- `.github/ai-workflow/validators/validate-manifest`
- `.github/ai-workflow/validators/validate-artifact`
- `.github/ai-workflow/validators/validate-plan-scope`
- `.github/ai-workflow/validators/validate-review-gate`
- `.github/ai-workflow/validators/validate-quick-task-preclassify`
- `.github/ai-workflow/skills/planning/SKILL.md`
- `.github/ai-workflow/skills/execution/SKILL.md`
- `.github/ai-workflow/skills/verification/SKILL.md`
- `.github/ai-workflow/skills/review/SKILL.md`
- `.github/ai-workflow/skills/quick-task/SKILL.md`
- `.github/prompts/write-plan.prompt.md`
- `.github/prompts/execute-plan.prompt.md`
- `.github/prompts/verify.prompt.md`
- `.github/prompts/review.prompt.md`
- `.github/ai-workflow/artifacts/examples/write-plan-from-spec.yaml`
- `.github/ai-workflow/artifacts/examples/verify-from-plan.yaml`
- `.github/ai-workflow/artifacts/examples/review-from-verification.yaml`
- `CLAUDE.md`

---

### Task 1: Expand the manifest into the central workflow graph

**Files:**
- Modify: `.github/ai-workflow/manifest.yaml`
- Modify: `.github/ai-workflow/schemas/manifest.schema.json`
- Modify: `.github/ai-workflow/validators/bootstrap`
- Modify: `.github/ai-workflow/validators/validate-manifest`

- [ ] **Step 1: Rewrite manifest command entries to own graph semantics**

Add graph-owned fields to every command entry in `.github/ai-workflow/manifest.yaml`:

```yaml
commands:
  /write-plan:
    contract: write-plan.v1
    file: .github/ai-workflow/contracts/commands/write-plan.v1.yaml
    allowed_predecessors:
      - /write-spec
    required_inputs:
      - spec_artifact
    conditional_inputs: []
    produces:
      - plan_artifact
    may_edit_source: false
    may_search_outside_plan_files: true
    allowed_handoffs:
      - /context-packet
      - /execute-plan
```

Repeat that structure for all existing commands and add `/setup-workflow` and `/context-packet`.

- [ ] **Step 2: Register new schemas, policies, validators, and config path**

Extend manifest sections so these paths are first-class:

```yaml
schemas:
  config: .github/ai-workflow/schemas/config.schema.json
  context_packet: .github/ai-workflow/schemas/context-packet.schema.json
  execution_checkpoint: .github/ai-workflow/schemas/execution-checkpoint.schema.json

policies:
  context: .github/ai-workflow/policies/context-policy.v1.yaml

validators:
  context_packet: .github/ai-workflow/validators/validate-context-packet
  compatibility: .github/ai-workflow/validators/validate-compatibility

runtime:
  root: .github/ai-workflow
  bootstrap_validator: .github/ai-workflow/validators/bootstrap
  config: .github/workflow/config.yaml
```

- [ ] **Step 3: Update the manifest schema**

Modify `.github/ai-workflow/schemas/manifest.schema.json` so the new graph fields are required for every command:

```json
"allowed_predecessors": { "type": "array", "items": { "type": "string", "minLength": 1 } },
"required_inputs": { "type": "array", "items": { "type": "string", "minLength": 1 } },
"conditional_inputs": { "type": "array", "items": { "type": "string", "minLength": 1 } },
"produces": { "type": "array", "items": { "type": "string", "minLength": 1 } },
"may_edit_source": { "type": "boolean" },
"may_search_outside_plan_files": { "type": "boolean" },
"allowed_handoffs": { "type": "array", "items": { "type": "string", "minLength": 1 } }
```

- [ ] **Step 4: Tighten bootstrap and manifest validation**

Update `bootstrap` and `validate-manifest` so they fail when:
- new required command keys are missing
- `/setup-workflow` or `/context-packet` are missing
- new schemas/policies/validators are unregistered

Run:

```bash
./.github/ai-workflow/validators/bootstrap
./.github/ai-workflow/validators/validate-manifest
```

Expected: both print `PASS`

---

### Task 2: Add repo-local setup and config wiring

**Files:**
- Create: `.github/ai-workflow/contracts/commands/setup-workflow.v1.yaml`
- Create: `.github/ai-workflow/skills/setup-workflow/SKILL.md`
- Create: `.github/prompts/setup-workflow.prompt.md`
- Create: `.github/ai-workflow/schemas/config.schema.json`
- Create: `.github/workflow/config.yaml`

- [ ] **Step 1: Create the config schema**

Create `.github/ai-workflow/schemas/config.schema.json` with local wiring only:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Workflow Config",
  "type": "object",
  "additionalProperties": false,
  "required": ["workflow_version", "paths", "thresholds", "module_vocabulary", "retrieval"],
  "properties": {
    "workflow_version": { "type": "integer", "const": 1 }
  }
}
```
```

Fill out the remaining properties for `paths`, `thresholds`, `module_vocabulary`, and `retrieval`.

- [ ] **Step 2: Create the initial repo-local config**

Seed `.github/workflow/config.yaml` with the agreed defaults:

```yaml
workflow_version: 1

paths:
  artifacts: .github/ai-workflow/artifacts
  manifest: .github/ai-workflow/manifest.yaml
  schemas: .github/ai-workflow/schemas
  evidence: .github/ai-workflow/artifacts/evidence
  knowledge: .github/knowledge
  indexes: .github/indexes

thresholds:
  max_inline_files_without_packet: 3
  max_inline_modules_without_packet: 1
  max_out_of_plan_reads_without_packet: 0
```

Complete the `module_vocabulary` and `retrieval` sections with repo-appropriate placeholder-but-valid defaults.

- [ ] **Step 3: Add the `/setup-workflow` contract**

Create `.github/ai-workflow/contracts/commands/setup-workflow.v1.yaml`:

```yaml
command_contract_id: setup-workflow.v1
stable_alias: /setup-workflow
contract_version: 1

input_artifacts: []

output_artifacts:
  - type: workflow_config
    schema: config.schema.v1
    required: true
```

Add authority and semantics so the command may update only `.github/workflow/config.yaml` and may not edit source files.

- [ ] **Step 4: Add setup prompt and skill**

Create a prompt and skill that say:
- read the manifest first
- produce or update config
- never redefine workflow semantics
- only wire local paths, thresholds, module vocabulary, retrieval locations

Run:

```bash
./.github/ai-workflow/validators/validate-manifest
python3 - <<'PY'
import json, yaml
json.load(open('.github/ai-workflow/schemas/config.schema.json'))
yaml.safe_load(open('.github/workflow/config.yaml'))
print('PASS')
PY
```

Expected: all commands print `PASS`

---

### Task 3: Introduce ContextPacketArtifact and `/context-packet`

**Files:**
- Create: `.github/ai-workflow/contracts/commands/context-packet.v1.yaml`
- Create: `.github/ai-workflow/skills/context-packet/SKILL.md`
- Create: `.github/prompts/context-packet.prompt.md`
- Create: `.github/ai-workflow/schemas/context-packet.schema.json`
- Create: `.github/ai-workflow/policies/context-policy.v1.yaml`
- Create: `.github/ai-workflow/validators/validate-context-packet`
- Create: `.github/ai-workflow/artifacts/context/.gitkeep`

- [ ] **Step 1: Create the context packet schema**

Create `.github/ai-workflow/schemas/context-packet.schema.json` with these required fields:

```json
[
  "artifact_type",
  "schema_version",
  "task_id",
  "phase_id",
  "source_plan",
  "generated_at",
  "scope",
  "retrieval_policy",
  "coverage",
  "included_context",
  "execution_decision",
  "validated_under"
]
```

Constrain `execution_decision.status` to `proceed`, `refresh_required`, or `escalate`.

- [ ] **Step 2: Encode strict packet trigger rules as policy**

Create `.github/ai-workflow/policies/context-policy.v1.yaml`:

```yaml
policy_id: context-policy.v1

required_triggers:
  - execution_mode_is_phased
  - retrieval_required
  - phase_file_count_exceeds_threshold
  - phase_spans_multiple_modules
  - module_mapping_uncertain
  - out_of_plan_read_needed

not_required_only_when:
  execution_mode: inline
  retrieval_required: false
  max_inline_files_without_packet: 3
  max_inline_modules_without_packet: 1
  max_out_of_plan_reads_without_packet: 0
```

- [ ] **Step 3: Add the `/context-packet` command contract**

Create `.github/ai-workflow/contracts/commands/context-packet.v1.yaml` so it:
- requires `plan_artifact`
- produces `context_packet_artifact`
- may search outside plan files
- may not edit source
- may hand off only to `/execute-plan` or `/write-plan`

- [ ] **Step 4: Add the packet validator**

Create `.github/ai-workflow/validators/validate-context-packet` to verify:
- packet references a real plan path
- `task_id` and `phase_id` are non-empty
- `execution_decision.status` is one of the allowed values
- `included_context[]` entries are justified
- packet does not declare implementation steps or new scope

Run:

```bash
python3 - <<'PY'
import json
json.load(open('.github/ai-workflow/schemas/context-packet.schema.json'))
print('PASS')
PY
./.github/ai-workflow/validators/validate-manifest
```

Expected: both print `PASS`

---

### Task 4: Expand PlanArtifact to drive deterministic context gating

**Files:**
- Modify: `.github/ai-workflow/schemas/plan.schema.json`
- Modify: `.github/ai-workflow/contracts/commands/write-plan.v1.yaml`
- Modify: `.github/ai-workflow/policies/workflow-policy.v1.yaml`
- Modify: `.github/ai-workflow/policies/retrieval-policy.v1.yaml`
- Modify: `.github/ai-workflow/skills/planning/SKILL.md`
- Modify: `.github/prompts/write-plan.prompt.md`
- Modify: `.github/ai-workflow/validators/validate-artifact`
- Modify: `.github/ai-workflow/validators/validate-plan-scope`

- [ ] **Step 1: Replace loose step-only planning with phase-aware structure**

Extend `plan.schema.json` so a plan can declare:

```json
"execution": {
  "type": "object",
  "required": ["mode"],
  "properties": {
    "mode": { "enum": ["inline", "phased-inline", "phased-subagent"] }
  }
}
```

And add either `phases[]` or enrich `steps[]` so each unit declares:
- `files[]`
- `modules[]`
- `subsystem`
- `verification_command`
- `module_mapping_confidence`
- `context_state`

- [ ] **Step 2: Make verification command mandatory**

Move `verification_command` out of optional status and make it required for non-blocked plans.

- [ ] **Step 3: Make retrieval reasoning deterministic**

Update `retrieval-policy.v1.yaml` and `write-plan.v1.yaml` so planning must declare:

```yaml
retrieval_decision:
  required: true
  reason: phase_spans_multiple_modules
```

Use `reason`, not only freeform `justification`, so packet triggers are machine-checkable.

- [ ] **Step 4: Update plan validation and planning skill**

Update validators and `planning/SKILL.md` to fail when:
- module mapping is missing
- subsystem is missing
- verification command is missing
- packet trigger state cannot be computed

Run:

```bash
python3 - <<'PY'
import json
json.load(open('.github/ai-workflow/schemas/plan.schema.json'))
print('PASS')
PY
```

Expected: `PASS`

---

### Task 5: Add ExecutionCheckpointArtifact and make `/execute-plan` always produce it

**Files:**
- Create: `.github/ai-workflow/schemas/execution-checkpoint.schema.json`
- Create: `.github/ai-workflow/artifacts/execution/.gitkeep`
- Modify: `.github/ai-workflow/contracts/commands/execute-plan.v1.yaml`
- Modify: `.github/ai-workflow/skills/execution/SKILL.md`
- Modify: `.github/prompts/execute-plan.prompt.md`
- Modify: `.github/ai-workflow/validators/validate-artifact`

- [ ] **Step 1: Create the execution checkpoint schema**

Create `.github/ai-workflow/schemas/execution-checkpoint.schema.json` with required fields:

```json
[
  "artifact_type",
  "schema_version",
  "task_id",
  "source_plan",
  "execution_mode",
  "status",
  "context_state",
  "plan_scope",
  "actual_changes",
  "evidence",
  "decision",
  "validated_under"
]
```

Allow `status` values `in_progress`, `completed`, `blocked`, `escalated`.

- [ ] **Step 2: Make `/execute-plan` produce checkpoint output**

Update `execute-plan.v1.yaml`:

```yaml
output_artifacts:
  - type: execution_checkpoint_artifact
    schema: execution-checkpoint.schema.v1
    required: true
```

Add conditional input for `context_packet_artifact` when required by plan state.

- [ ] **Step 3: Make execution packet-aware but never packet-generating**

Update the execution skill and prompt so `/execute-plan` does this before edits:
- if packet not required: continue
- if packet required and missing: stop
- if packet says `refresh_required`: stop
- if packet says `escalate`: stop
- if packet says `proceed`: continue

- [ ] **Step 4: Record actual execution evidence in checkpoint**

The skill must populate:
- files touched
- unplanned files touched
- commands run
- output refs
- continue/stop/escalate decision

Run:

```bash
python3 - <<'PY'
import json
json.load(open('.github/ai-workflow/schemas/execution-checkpoint.schema.json'))
print('PASS')
PY
```

Expected: `PASS`

---

### Task 6: Make artifact pinning mandatory and add compatibility checks

**Files:**
- Modify: `.github/ai-workflow/schemas/brainstorm.schema.json`
- Modify: `.github/ai-workflow/schemas/quick-task.schema.json`
- Modify: `.github/ai-workflow/schemas/spec.schema.json`
- Modify: `.github/ai-workflow/schemas/plan.schema.json`
- Modify: `.github/ai-workflow/schemas/verification.schema.json`
- Modify: `.github/ai-workflow/schemas/review.schema.json`
- Modify: `.github/ai-workflow/schemas/context-packet.schema.json`
- Modify: `.github/ai-workflow/schemas/execution-checkpoint.schema.json`
- Create: `.github/ai-workflow/validators/validate-compatibility`
- Modify: `.github/ai-workflow/validators/validate-artifact`

- [ ] **Step 1: Make `task_id` and `validated_under` required everywhere**

Update every artifact schema so these fields are required:

```json
"task_id": { "type": "string", "minLength": 1 },
"validated_under": {
  "type": "object",
  "required": [
    "workflow_manifest_version",
    "schema_version",
    "command_version",
    "config_version"
  ]
}
```

- [ ] **Step 2: Upgrade `validate-artifact` to enforce pinning**

Change the validator from optional checks to required checks. Fail if `validated_under` is missing or incomplete.

- [ ] **Step 3: Add compatibility validator**

Create `validate-compatibility` with behavior:
- `PASS` if compatible
- `WARN` if older but still compatible
- `MIGRATION_REQUIRED` if incompatible

The validator must not mutate artifacts.

- [ ] **Step 4: Thread compatibility into consuming phases**

Update contract docs and skills so consuming commands run compatibility validation before normal artifact validation.

Run:

```bash
./.github/ai-workflow/validators/validate-manifest
```

Expected: `PASS`

---

### Task 7: Make `/verify` artifact-driven from plan plus checkpoint

**Files:**
- Modify: `.github/ai-workflow/contracts/commands/verify.v1.yaml`
- Modify: `.github/ai-workflow/schemas/verification.schema.json`
- Modify: `.github/ai-workflow/skills/verification/SKILL.md`
- Modify: `.github/prompts/verify.prompt.md`
- Modify: `.github/ai-workflow/validators/validate-plan-scope`
- Modify: `.github/ai-workflow/validators/validate-review-gate`

- [ ] **Step 1: Change verify inputs**

Update `verify.v1.yaml`:

```yaml
input_artifacts:
  - type: plan_artifact
    schema: plan.schema.v1
    required: true
  - type: execution_checkpoint_artifact
    schema: execution-checkpoint.schema.v1
    required: true
  - type: context_packet_artifact
    schema: context-packet.schema.v1
    required: false
```

Note in semantics that packet input becomes mandatory when the plan or checkpoint says a packet was required.

- [ ] **Step 2: Extend verification schema**

Add fields for:
- `checkpoint_ref`
- optional `context_packet_ref`
- `verification_command_run`
- packet compliance result

- [ ] **Step 3: Enforce packet and checkpoint rules in validation**

Update validators so `/verify` fails when:
- no checkpoint exists
- verification command does not match the plan
- packet was required but missing
- packet state was not `proceed`
- checkpoint shows unplanned file touches

- [ ] **Step 4: Update the verification skill and prompt**

The skill must treat the checkpoint as primary evidence and `git diff` as supporting evidence only.

Run:

```bash
./.github/ai-workflow/validators/validate-manifest
```

Expected: `PASS`

---

### Task 8: Make `/review` strictly artifact-driven

**Files:**
- Modify: `.github/ai-workflow/contracts/commands/review.v1.yaml`
- Modify: `.github/ai-workflow/schemas/review.schema.json`
- Modify: `.github/ai-workflow/skills/review/SKILL.md`
- Modify: `.github/prompts/review.prompt.md`
- Modify: `.github/ai-workflow/validators/validate-review-gate`

- [ ] **Step 1: Change review inputs**

Require:
- `plan_artifact`
- `execution_checkpoint_artifact`
- `verification_artifact`

Conditionally require `context_packet_artifact` when packet rules were active.

- [ ] **Step 2: Extend the review gate**

Update `validate-review-gate` so normal pass is forbidden when:
- required packet was absent
- checkpoint is absent or incompatible
- verification command evidence is missing
- unplanned file touches exist
- packet state ended in `refresh_required` or `escalate`

- [ ] **Step 3: Keep human approval gate intact**

Preserve the existing rule that `PASS` and `PASS_WITH_DEGRADATION` require `human_authorization`.

- [ ] **Step 4: Update review schema and skill**

Add references to:
- `checkpoint_ref`
- optional `context_packet_ref`
- packet compliance findings

Run:

```bash
./.github/ai-workflow/validators/validate-review-gate .github/ai-workflow/artifacts/examples/review-from-verification.yaml
```

Expected after example updates: `PASS`

---

### Task 9: Fix quick-task and wrapper drift

**Files:**
- Modify: `.github/ai-workflow/contracts/commands/quick-task.v1.yaml`
- Modify: `.github/ai-workflow/skills/quick-task/SKILL.md`
- Modify: `.github/prompts/quick-task.prompt.md`
- Modify: `.github/ai-workflow/validators/validate-quick-task-preclassify`
- Modify: `.github/ai-workflow/validators/validate-review-gate`

- [ ] **Step 1: Align quick-task skill with contract-required validators**

Update `quick-task/SKILL.md` to explicitly require the preclassify validator before any edit:

```md
## Required validators
validate-manifest
validate-quick-task-preclassify
validate-artifact
validate-plan-scope
validate-review-gate
```

- [ ] **Step 2: Tighten prompt wording**

Ensure the prompt says quick-task must stop before editing if classification is not locked or policy disallows execution.

- [ ] **Step 3: Keep quick-task out of the context-packet path**

Do not make `/quick-task` produce packets. It should escalate into the full workflow instead.

- [ ] **Step 4: Verify contract/skill/prompt parity**

Run:

```bash
rg -n "validate-quick-task-preclassify|ESCALATED_TO_FULL_WORKFLOW|ContextPacketArtifact" .github/ai-workflow/contracts/commands/quick-task.v1.yaml .github/ai-workflow/skills/quick-task/SKILL.md .github/prompts/quick-task.prompt.md
```

Expected: preclassify appears in the skill; packet generation does not appear in quick-task docs

---

### Task 10: Refresh examples and top-level docs to match the real v1

**Files:**
- Modify: `.github/ai-workflow/artifacts/examples/write-plan-from-spec.yaml`
- Modify: `.github/ai-workflow/artifacts/examples/verify-from-plan.yaml`
- Modify: `.github/ai-workflow/artifacts/examples/review-from-verification.yaml`
- Create: `.github/ai-workflow/artifacts/examples/context-packet-from-plan.yaml`
- Create: `.github/ai-workflow/artifacts/examples/execution-checkpoint-from-plan.yaml`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update plan example to include v1-required plan fields**

Add:
- `task_id`
- `validated_under`
- phase or step module mapping
- `verification_command`
- packet trigger evaluability

- [ ] **Step 2: Add packet and checkpoint examples**

Create examples that show:
- packet `execution_decision.status: proceed`
- checkpoint `status: completed`
- no hidden scope expansion

- [ ] **Step 3: Fix the invalid review example**

Update `review-from-verification.yaml` so it includes:

```yaml
human_authorization:
  status: approved
  reviewer: engineer@example.com
```

If you do not want the example to represent approved state, change it to `FAIL` or `BLOCKED` instead of `PASS`.

- [ ] **Step 4: Rewrite `CLAUDE.md`**

Replace the stale `github/` tree description with the current `.github/ai-workflow` architecture and the new command chain:

```text
/setup-workflow
  → /brainstorm
  → /write-spec
  → /write-plan
  → /context-packet (when required)
  → /execute-plan
  → /verify
  → /review
```

Run:

```bash
for f in .github/ai-workflow/artifacts/examples/*.yaml; do
  echo "FILE:$f"
  ./.github/ai-workflow/validators/validate-artifact "$f"
done
```

Expected: every example prints `PASS`

---

### Task 11: End-to-end validator sweep

**Files:**
- Test: `.github/ai-workflow/validators/*`
- Test: `.github/ai-workflow/artifacts/examples/*`

- [ ] **Step 1: Run bootstrap and manifest validation**

```bash
./.github/ai-workflow/validators/bootstrap
./.github/ai-workflow/validators/validate-manifest
```

Expected: both print `PASS`

- [ ] **Step 2: Run artifact validation across examples**

```bash
for f in .github/ai-workflow/artifacts/examples/*.yaml; do
  echo "FILE:$f"
  ./.github/ai-workflow/validators/validate-artifact "$f"
done
```

Expected: every example prints `PASS`

- [ ] **Step 3: Run review gate on the final review example**

```bash
./.github/ai-workflow/validators/validate-review-gate .github/ai-workflow/artifacts/examples/review-from-verification.yaml
```

Expected: `PASS`

- [ ] **Step 4: Commit**

```bash
git add .github/ai-workflow .github/prompts .github/workflow/config.yaml CLAUDE.md docs/superpowers/plans/2026-05-02-ai-workflow-v1-required-changes.md
git commit -m "plan: define required v1 ai-workflow architecture changes"
```

---

## Self-Review

- **Spec coverage:** This plan covers the agreed mandatory v1 decisions: setup/config, central manifest graph, first-class context packets, deterministic packet triggers, plan-side module mapping, execution checkpoints, pinned artifacts, no in-place migration, artifact-driven verify/review, wrapper alignment, and doc/example correction.
- **Placeholder scan:** No `TODO`, `TBD`, or “implement later” placeholders remain. Open design decisions were already resolved before planning.
- **Type consistency:** Artifact names are used consistently: `PlanArtifact`, `ContextPacketArtifact`, `ExecutionCheckpointArtifact`, `VerificationArtifact`, `ReviewArtifact`, and repo-local `config.yaml`.
