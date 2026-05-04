# Quick-Task Proof Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the new `.github/ai-workflow/` runtime skeleton and prove the new authority stack with `/quick-task` end-to-end.

**Architecture:** Build the proof slice in dependency order. First create the runtime shell and bootstrap manifest so the new surface can discover itself. Then add the `/quick-task` command contract, policies, and schema as the first real authority chain. After that, add the skill, prompt, and validators, and finish with one concrete `QuickTaskRecord` example plus verification that the slice escalates and validates correctly without touching the legacy `github/` runtime.

**Tech Stack:** Markdown, YAML, JSON Schema, and small repo-local validator scripts under `.github/ai-workflow/`. Verification via `find`, `rg`, `python3`, and direct validator execution.

---

## All Files Changed

**Task 1 — Runtime skeleton and bootstrap surface:**
- Create: `.github/copilot-instructions.md`
- Create: `.github/prompts/quick-task.prompt.md`
- Create: `.github/ai-workflow/manifest.yaml`
- Create: `.github/ai-workflow/schemas/manifest.schema.json`
- Create: `.github/ai-workflow/schemas/command-contract.schema.json`
- Create: `.github/ai-workflow/artifacts/.gitkeep`
- Create: `.github/ai-workflow/logs/.gitkeep`

**Task 2 — `/quick-task` contract, policy, and artifact schema:**
- Create: `.github/ai-workflow/contracts/commands/quick-task.v1.yaml`
- Create: `.github/ai-workflow/policies/quick-task-policy.v1.yaml`
- Create: `.github/ai-workflow/policies/review-policy.v1.yaml`
- Create: `.github/ai-workflow/schemas/quick-task.schema.json`

**Task 3 — Skill, protocol, and validator implementations:**
- Create: `.github/ai-workflow/skills/quick-task/SKILL.md`
- Create: `.github/ai-workflow/protocols/verification-gate.md`
- Create: `.github/ai-workflow/validators/bootstrap`
- Create: `.github/ai-workflow/validators/validate-manifest`
- Create: `.github/ai-workflow/validators/validate-artifact`
- Create: `.github/ai-workflow/validators/validate-plan-scope`
- Create: `.github/ai-workflow/validators/validate-review-gate`

**Task 4 — Proof artifact and acceptance verification:**
- Create: `.github/ai-workflow/artifacts/examples/quick-task-escalation.yaml`
- Modify as needed: any file above to resolve validator or contract drift discovered during verification

---

## Task 1: Runtime Skeleton and Bootstrap Surface

**Files:**
- Create: `.github/copilot-instructions.md`
- Create: `.github/prompts/quick-task.prompt.md`
- Create: `.github/ai-workflow/manifest.yaml`
- Create: `.github/ai-workflow/schemas/manifest.schema.json`
- Create: `.github/ai-workflow/schemas/command-contract.schema.json`
- Create: `.github/ai-workflow/artifacts/.gitkeep`
- Create: `.github/ai-workflow/logs/.gitkeep`

- [ ] **Step 1: Create the `.github/` runtime shell**

Create the exact directory layout below and do not move or delete the existing `github/`
tree in this task:

```text
.github/
  prompts/
  ai-workflow/
    schemas/
    contracts/commands/
    policies/
    skills/quick-task/
    protocols/
    validators/
    artifacts/
    logs/
```

The old `github/` directory remains untouched so the proof slice can be added without
breaking the current repo state.

- [ ] **Step 2: Write `.github/copilot-instructions.md` as a thin authority pointer**

Write only the runtime rules that are still allowed to be normative:

```md
# Copilot Instructions

This repository uses `.github/ai-workflow/manifest.yaml` as the workflow bootstrap authority.

Before following any workflow command:
1. Load `.github/ai-workflow/manifest.yaml`.
2. Resolve command contracts, policies, schemas, and validators from the manifest.
3. Treat prompts as UX wrappers only.

Authority order:
1. Artifact schema
2. Verification/review gates
3. Phase semantics
4. Runtime layout contract
5. Skill text
6. Command UX

If this file conflicts with the manifest, contracts, policies, schemas, or validators, this file loses.

Do not claim completion without verification evidence.
Do not edit files outside declared task scope.
```

Do not copy behavioral thresholds, quick-task rules, or validator logic into this file.

- [ ] **Step 3: Write `.github/prompts/quick-task.prompt.md` as a non-authoritative wrapper**

Keep the prompt short and pointer-only:

```md
# /quick-task

Use the `/quick-task` workflow for small, local, low-risk edits only.

Load:
- `.github/ai-workflow/manifest.yaml`
- the command contract bound to `/quick-task`
- the required policies, schemas, and validators referenced by that contract

If the task exceeds quick-task authority, escalate to the full workflow instead of stretching this command.
```

Do not place file-count thresholds, forbidden classes, or review rules in the prompt.

- [ ] **Step 4: Write `.github/ai-workflow/manifest.yaml`**

Create a minimal manifest for this proof slice with exactly one stable command binding and
only the wiring needed for `/quick-task`:

```yaml
manifest_version: 1
workflow_contract_version: 1
supported_manifest_versions:
  - 1

runtime:
  root: .github/ai-workflow
  bootstrap_validator: .github/ai-workflow/validators/bootstrap

paths:
  contracts_root: .github/ai-workflow/contracts
  schemas_root: .github/ai-workflow/schemas
  policies_root: .github/ai-workflow/policies
  skills_root: .github/ai-workflow/skills
  protocols_root: .github/ai-workflow/protocols
  validators_root: .github/ai-workflow/validators
  artifacts_root: .github/ai-workflow/artifacts
  logs_root: .github/ai-workflow/logs

commands:
  /quick-task:
    contract: quick-task.v1
    file: .github/ai-workflow/contracts/commands/quick-task.v1.yaml

schemas:
  manifest: .github/ai-workflow/schemas/manifest.schema.json
  command_contract: .github/ai-workflow/schemas/command-contract.schema.json
  quick_task: .github/ai-workflow/schemas/quick-task.schema.json

policies:
  quick_task: .github/ai-workflow/policies/quick-task-policy.v1.yaml
  review: .github/ai-workflow/policies/review-policy.v1.yaml

validators:
  bootstrap: .github/ai-workflow/validators/bootstrap
  manifest: .github/ai-workflow/validators/validate-manifest
  artifact: .github/ai-workflow/validators/validate-artifact
  plan_scope: .github/ai-workflow/validators/validate-plan-scope
  review_gate: .github/ai-workflow/validators/validate-review-gate
```

- [ ] **Step 5: Create `manifest.schema.json` and `command-contract.schema.json`**

Keep both schemas minimal.

`manifest.schema.json` must validate:
- integer `manifest_version`
- integer `workflow_contract_version`
- `supported_manifest_versions[]`
- `runtime.bootstrap_validator`
- the `paths`, `commands`, `schemas`, `policies`, and `validators` maps used above

`command-contract.schema.json` must validate:
- `command_contract_id`
- `stable_alias`
- `contract_version`
- `output_artifacts`
- `required_policies`
- `required_validators`
- `authority`
- `semantics.required`

Do not add future command surface or unused keys in this first slice.

- [ ] **Step 6: Create `.gitkeep` placeholders**

Create:

```text
.github/ai-workflow/artifacts/.gitkeep
.github/ai-workflow/logs/.gitkeep
```

No artifact examples yet in this task.

- [ ] **Step 7: Verify Task 1**

Run:

```bash
find .github -maxdepth 4 | sort
rg -n "manifest.yaml|quick-task|Authority order" .github/copilot-instructions.md .github/prompts/quick-task.prompt.md .github/ai-workflow/manifest.yaml
python3 - <<'PY'
import json, pathlib, yaml
root = pathlib.Path(".github/ai-workflow")
yaml.safe_load((root / "manifest.yaml").read_text())
json.loads((root / "schemas/manifest.schema.json").read_text())
json.loads((root / "schemas/command-contract.schema.json").read_text())
print("PASS")
PY
```

Expected:
- `.github/ai-workflow/` exists with the skeleton above
- the prompt and copilot instructions reference the manifest and stay thin
- manifest and both JSON schema files parse successfully

- [ ] **Step 8: Commit**

```bash
git add .github/copilot-instructions.md .github/prompts/quick-task.prompt.md .github/ai-workflow/manifest.yaml .github/ai-workflow/schemas/manifest.schema.json .github/ai-workflow/schemas/command-contract.schema.json .github/ai-workflow/artifacts/.gitkeep .github/ai-workflow/logs/.gitkeep
git commit -m "workflow: add ai-workflow bootstrap skeleton"
```

---

## Task 2: `/quick-task` Contract, Policy, and Artifact Schema

**Files:**
- Create: `.github/ai-workflow/contracts/commands/quick-task.v1.yaml`
- Create: `.github/ai-workflow/policies/quick-task-policy.v1.yaml`
- Create: `.github/ai-workflow/policies/review-policy.v1.yaml`
- Create: `.github/ai-workflow/schemas/quick-task.schema.json`

- [ ] **Step 1: Write `.github/ai-workflow/contracts/commands/quick-task.v1.yaml`**

Write the contract exactly with the proof-slice semantics already agreed:

```yaml
command_contract_id: quick-task.v1
stable_alias: /quick-task
contract_version: 1

input_artifacts: []

output_artifacts:
  - type: quick_task_record
    schema: quick-task.schema.v1
    required: true

required_policies:
  - quick-task-policy.v1
  - review-policy.v1

required_validators:
  before:
    - validate-manifest
  after:
    - validate-artifact
    - validate-plan-scope
    - validate-review-gate

authority:
  may_create:
    - quick_task_record
  may_modify:
    - files_declared_in_quick_task_record
  may_read:
    - manifest
    - policies
    - schemas
    - directly_affected_files
  forbidden:
    - modify_manifest
    - modify_schemas
    - modify_policies
    - change_public_contracts
    - introduce_new_abstractions
    - edit_outside_declared_scope
    - bypass_validation

semantics:
  required:
    - classify_task_against_quick_task_policy
    - list_exact_files_before_editing
    - escalate_if_policy_disallows_quick_task
    - record_verification_evidence
    - produce_reviewable_scope
```

- [ ] **Step 2: Write `.github/ai-workflow/policies/quick-task-policy.v1.yaml`**

Write the policy with only day-one quick-task thresholds and outcomes:

```yaml
policy_id: quick-task-policy.v1

max_files: 3

allowed_change_classes:
  - docs_copy
  - formatting_only
  - comments_only
  - test_only_narrow
  - isolated_internal_helper_change

forbidden_change_classes:
  - public_behavior_change
  - public_api_change
  - schema_or_data_shape_change
  - auth_or_permissions
  - persistence_or_migration
  - security_sensitive
  - concurrency
  - deployment_or_runtime_config
  - shared_core
  - cross_module_or_service_boundary
  - new_abstraction_or_dependency

required_checks:
  - exact_files_listed
  - change_class_declared
  - verification_evidence_present

on_forbidden_class: ESCALATED_TO_FULL_WORKFLOW
on_file_limit_exceeded: ESCALATED_TO_FULL_WORKFLOW
on_missing_verification: FAIL
```

- [ ] **Step 3: Write `.github/ai-workflow/policies/review-policy.v1.yaml`**

Keep the review policy equally narrow:

```yaml
policy_id: review-policy.v1

allowed_dispositions:
  - PASS_QUICK
  - FAIL
  - ESCALATED_TO_FULL_WORKFLOW

rules:
  actual_files_must_be_subset_of_planned: true
  verification_evidence_required: true
  forbidden_class_must_escalate: true
  missing_evidence_must_fail: true
```

- [ ] **Step 4: Write `.github/ai-workflow/schemas/quick-task.schema.json`**

Implement a minimal JSON Schema covering:
- `schema_version`
- `command`
- `status`
- `task_summary`
- `change_class.value`
- `change_class.policy_allowed`
- `change_class.classification_status`
- `files.planned[]`
- `files.actual[]`
- `escalation.required`
- `escalation.reasons[]`
- `verification.evidence[]`
- `review.scope_match`
- `review.disposition`
- `review.notes`
- optional `escalation_seed` with:
  - `original_request`
  - `escalation_reason[]`
  - `observed_change_class`
  - `planned_files[]`
  - `actual_files_changed[]`
  - `recommended_next_command`

Use enums for:
- `status`
- `classification_status`
- file `operation`
- `review.disposition`
- `recommended_next_command` with the single allowed value `/write-spec`

- [ ] **Step 5: Verify Task 2**

Run:

```bash
python3 - <<'PY'
import json, pathlib, yaml
root = pathlib.Path(".github/ai-workflow")
yaml.safe_load((root / "contracts/commands/quick-task.v1.yaml").read_text())
yaml.safe_load((root / "policies/quick-task-policy.v1.yaml").read_text())
yaml.safe_load((root / "policies/review-policy.v1.yaml").read_text())
json.loads((root / "schemas/quick-task.schema.json").read_text())
print("PASS")
PY
rg -n "quick-task.v1|ESCALATED_TO_FULL_WORKFLOW|max_files|recommended_next_command" .github/ai-workflow/contracts/commands/quick-task.v1.yaml .github/ai-workflow/policies/quick-task-policy.v1.yaml .github/ai-workflow/policies/review-policy.v1.yaml .github/ai-workflow/schemas/quick-task.schema.json
```

Expected:
- contract, policies, and schema all parse
- the contract references only the agreed validators and policies
- the schema constrains the proof-slice fields and nothing larger

- [ ] **Step 6: Commit**

```bash
git add .github/ai-workflow/contracts/commands/quick-task.v1.yaml .github/ai-workflow/policies/quick-task-policy.v1.yaml .github/ai-workflow/policies/review-policy.v1.yaml .github/ai-workflow/schemas/quick-task.schema.json
git commit -m "workflow: define quick-task contract policy and schema"
```

---

## Task 3: Skill, Protocol, and Validator Implementations

**Files:**
- Create: `.github/ai-workflow/skills/quick-task/SKILL.md`
- Create: `.github/ai-workflow/protocols/verification-gate.md`
- Create: `.github/ai-workflow/validators/bootstrap`
- Create: `.github/ai-workflow/validators/validate-manifest`
- Create: `.github/ai-workflow/validators/validate-artifact`
- Create: `.github/ai-workflow/validators/validate-plan-scope`
- Create: `.github/ai-workflow/validators/validate-review-gate`

- [ ] **Step 1: Write `.github/ai-workflow/skills/quick-task/SKILL.md`**

Use the agreed minimal skeleton:

```md
# quick-task

## Skill purpose
Handle small, local, low-risk changes without full planning ceremony.

## Implemented command contract
quick-task.v1

## Required inputs
User task request.

## Produced outputs
QuickTaskRecord.

## Authority limits
May only edit files declared in the QuickTaskRecord.
Must escalate if quick-task-policy.v1 disallows the task.

## Required policies
quick-task-policy.v1
review-policy.v1

## Required schemas
quick-task.schema.v1

## Required validators
validate-manifest
validate-artifact
validate-plan-scope
validate-review-gate

## Procedure
1. Load manifest.
2. Load command contract and policy.
3. Classify the task against quick-task-policy.v1.
4. List exact files before editing.
5. If disallowed, create QuickTaskRecord with ESCALATED_TO_FULL_WORKFLOW.
6. If allowed, make only declared edits.
7. Run available verification.
8. Create QuickTaskRecord.
9. Run review-gate validation.

## Failure behavior
Missing required dependency blocks.
Forbidden change class escalates.
Unplanned file change fails.
Missing verification fails.

## Handoff/output format
Return the QuickTaskRecord and concise result.
```

Do not add policy thresholds, compatibility rules, or hidden exceptions to the skill.

- [ ] **Step 2: Write `.github/ai-workflow/protocols/verification-gate.md`**

Keep this protocol short and command-agnostic:

```md
# Verification Gate

Verification evidence is required before a quick-task may pass.

Allowed evidence:
- automated test output
- typecheck/build/lint output
- manual inspection note
- local run output
- before/after behavior note

If no credible evidence exists, the quick-task result must be FAIL.
```

- [ ] **Step 3: Implement `.github/ai-workflow/validators/bootstrap`**

Write a small executable script that:
- checks `.github/ai-workflow/manifest.yaml` exists
- loads it
- checks `manifest_version` is in `supported_manifest_versions`
- verifies every referenced contract, schema, policy, validator, artifacts root, and logs root path exists

Output:
- `PASS` on success
- `BLOCKED: <exact reason>` on failure

Do not add semantic quick-task policy checks here.

- [ ] **Step 4: Implement `.github/ai-workflow/validators/validate-manifest`**

Write a small executable script that:
- loads the manifest
- validates it against `manifest.schema.json`
- rejects missing required sections
- rejects obvious junk-drawer drift in this slice by failing if unsupported top-level keys are present

Output:
- `PASS`
- `FAIL: <exact reason>`

- [ ] **Step 5: Implement `.github/ai-workflow/validators/validate-artifact`**

Write a small executable script that accepts one artifact path and:
- loads `quick-task.schema.json`
- validates the artifact JSON/YAML shape against it
- reports field-level schema failures

Output:
- `PASS`
- `FAIL: <exact reason>`

- [ ] **Step 6: Implement `.github/ai-workflow/validators/validate-plan-scope`**

For quick-task only, enforce the limited semantic rules:
- planned file count is `<= max_files`
- planned file paths are exact strings
- `change_class.value` is declared
- if `policy_allowed = false`, artifact `status` must be `ESCALATED_TO_FULL_WORKFLOW`

Input can be the path to a `QuickTaskRecord` artifact. Do not infer extra policy beyond the
declared quick-task slice.

- [ ] **Step 7: Implement `.github/ai-workflow/validators/validate-review-gate`**

For quick-task only, enforce:
- actual files are a subset of planned files
- verification evidence exists for `PASS_QUICK`
- missing evidence forces `FAIL`
- escalated tasks carry `ESCALATED_TO_FULL_WORKFLOW` as both `status` and `review.disposition`

Do not add style or architecture judgments.

- [ ] **Step 8: Verify Task 3**

Run:

```bash
chmod +x .github/ai-workflow/validators/bootstrap .github/ai-workflow/validators/validate-manifest .github/ai-workflow/validators/validate-artifact .github/ai-workflow/validators/validate-plan-scope .github/ai-workflow/validators/validate-review-gate
.github/ai-workflow/validators/bootstrap
.github/ai-workflow/validators/validate-manifest
rg -n "Implemented command contract|quick-task.v1|ESCALATED_TO_FULL_WORKFLOW|verification evidence" .github/ai-workflow/skills/quick-task/SKILL.md .github/ai-workflow/protocols/verification-gate.md .github/ai-workflow/validators/bootstrap .github/ai-workflow/validators/validate-manifest .github/ai-workflow/validators/validate-artifact .github/ai-workflow/validators/validate-plan-scope .github/ai-workflow/validators/validate-review-gate
```

Expected:
- both structural validators pass
- skill and protocol stay narrow
- validators exist and reference only the proof-slice authority chain

- [ ] **Step 9: Commit**

```bash
git add .github/ai-workflow/skills/quick-task/SKILL.md .github/ai-workflow/protocols/verification-gate.md .github/ai-workflow/validators/bootstrap .github/ai-workflow/validators/validate-manifest .github/ai-workflow/validators/validate-artifact .github/ai-workflow/validators/validate-plan-scope .github/ai-workflow/validators/validate-review-gate
git commit -m "workflow: add quick-task skill and validators"
```

---

## Task 4: Proof Artifact and Acceptance Verification

**Files:**
- Create: `.github/ai-workflow/artifacts/examples/quick-task-escalation.yaml`
- Modify as needed: any file above to resolve validator or contract drift discovered during verification

- [ ] **Step 1: Create the escalated proof artifact**

Write `.github/ai-workflow/artifacts/examples/quick-task-escalation.yaml` exactly:

```yaml
schema_version: quick-task.schema.v1

command: /quick-task

status: ESCALATED_TO_FULL_WORKFLOW

task_summary: "Fix incorrect error message in user login flow"

change_class:
  value: public_behavior_change
  policy_allowed: false
  classification_status: revised_before_edit

files:
  planned:
    - path: src/auth/loginService.ts
      operation: modify
  actual: []

escalation:
  required: true
  reasons:
    - "public_behavior_change is forbidden for quick-task"

verification:
  evidence:
    - "Inspection shows error message string used in login response"

review:
  scope_match: true
  disposition: ESCALATED_TO_FULL_WORKFLOW
  notes: "Change affects user-visible behavior; requires full workflow"

escalation_seed:
  original_request: "Fix incorrect error message in login flow"
  escalation_reason:
    - "public_behavior_change"
  observed_change_class: public_behavior_change
  planned_files:
    - src/auth/loginService.ts
  actual_files_changed: []
  recommended_next_command: /write-spec
```

- [ ] **Step 2: Validate the example artifact end-to-end**

Run:

```bash
.github/ai-workflow/validators/validate-artifact .github/ai-workflow/artifacts/examples/quick-task-escalation.yaml
.github/ai-workflow/validators/validate-plan-scope .github/ai-workflow/artifacts/examples/quick-task-escalation.yaml
.github/ai-workflow/validators/validate-review-gate .github/ai-workflow/artifacts/examples/quick-task-escalation.yaml
```

Expected:
- all three validators return `PASS`
- the artifact remains escalated, not passed

- [ ] **Step 3: Run final slice verification**

Run:

```bash
find .github/ai-workflow -maxdepth 4 | sort
rg -n "/quick-task|quick-task.v1|quick-task-policy.v1|quick-task.schema.v1|ESCALATED_TO_FULL_WORKFLOW" .github/copilot-instructions.md .github/prompts/quick-task.prompt.md .github/ai-workflow/manifest.yaml .github/ai-workflow/contracts/commands/quick-task.v1.yaml .github/ai-workflow/policies/quick-task-policy.v1.yaml .github/ai-workflow/policies/review-policy.v1.yaml .github/ai-workflow/schemas/quick-task.schema.json .github/ai-workflow/skills/quick-task/SKILL.md .github/ai-workflow/artifacts/examples/quick-task-escalation.yaml
test -d github
```

Expected:
- the new runtime slice exists end-to-end under `.github/ai-workflow/`
- `/quick-task` appears consistently in prompt, manifest, contract, skill, and artifact
- the legacy `github/` tree still exists untouched for now

- [ ] **Step 4: Resolve any drift discovered in verification**

If any validator or verification command fails:
- fix the smallest upstream source of truth
- re-run the exact failed command
- do not patch around the failure in prompt prose

- [ ] **Step 5: Commit**

```bash
git add .github/ai-workflow/artifacts/examples/quick-task-escalation.yaml .github
git commit -m "workflow: prove quick-task authority slice"
```

---

## Self-Review

- Spec coverage: This plan covers the new runtime skeleton, thin prompt/copter shell, manifest, contract, policy, schema, skill, validators, example artifact, and end-to-end verification for `/quick-task` only.
- Placeholder scan: No `TODO`, `TBD`, or deferred implementation markers remain in task steps.
- Type consistency: The plan uses `quick-task.v1`, `quick-task-policy.v1`, `review-policy.v1`, `quick-task.schema.v1`, `QuickTaskRecord`, and `ESCALATED_TO_FULL_WORKFLOW` consistently across all tasks.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-02-quick-task-proof-slice.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
