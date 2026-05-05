# /review

Compare changed files against plan scope. Catch scope creep before merge.

## Pre-conditions

1. Read the PlanArtifact at `.github/tasks/TASK-{NNN}/plan.yaml`.
2. Read the VerificationRecord at `.github/tasks/TASK-{NNN}/verification.yaml`.
3. Confirm `verification.status` is `VERIFIED` or `VERIFIED_WITH_DEGRADATION`. If not, stop and tell the user to fix verification first.

## Stage review rules

Scope violations, degraded states, and blocked work must be recorded as FAIL or BLOCKED — do not smooth them over in prose. See full required checks:

#file:.github/ai-workflow/protocols/stage-review.md

## Review steps

1. List all files changed during execution (from `execution.actual_changes.files_touched`).
2. Compare against `plan.files_in_scope` paths.
3. Any file touched that is NOT in `plan.files_in_scope` is a scope violation — record it in `scope_violations[]`.
4. If `scope_violations` is non-empty, status is FAIL.
5. If all changed files are in scope, status is PASS or PASS_WITH_DEGRADATION depending on verification state — but a human must approve before merge.

## Human authorization

PASS and PASS_WITH_DEGRADATION require explicit human approval. Produce this block and wait:

```
--- REVIEW APPROVAL REQUEST ---
Task: TASK-{NNN}
Changed files: [list]
Scope violations: none | [list]
Status: PASS | PASS_WITH_DEGRADATION | FAIL
Human approval required to merge. Type "approved by <your name>" to confirm.
---
```

Record the reviewer name in `human_authorization.reviewer`.

## Output

Save a ReviewRecord to `.github/tasks/TASK-{NNN}/review.yaml`.

Required fields:
- `artifact_type: ReviewRecord`
- `schema_version: review.schema.v1`
- `task_id`
- `primary_surface: copilot_plugin`
- `secondary_surfaces_allowed: [copilot_cli]`
- `plan_ref`, `execution_ref`, `verification_ref`
- `actual_changed_files` — from execution record
- `scope_violations` — list of files touched but not in plan scope (empty if clean)
- `scope_match: true | false`
- `status: PASS | PASS_WITH_DEGRADATION | FAIL | BLOCKED`
- `created_at` — ISO 8601 datetime, populate at artifact write time
- `human_authorization` — required for PASS/PASS_WITH_DEGRADATION. When status is `rejected`, must include `reason: { category: enum, details: string }` — present this block to the human reviewer and capture their structured reason. Category enum: `scope_violation | incorrect_implementation | criteria_not_met | verification_incomplete | quality_issue | other`.
- `degraded_reason` — required for PASS_WITH_DEGRADATION
- `validated_under` — exact workflow/command/schema/config tuple

After saving the ReviewRecord, update the TaskManifest at `.github/ai-workflow/artifacts/task-manifest/TASK-{NNN}.task-manifest.json`:
- Set `phase: review`
- Set `updated_at: <ISO 8601 timestamp>`
- Set `artifact_refs.review: .github/tasks/TASK-{NNN}/review.yaml`
- If status is `PASS` or `PASS_WITH_DEGRADATION`, set `status: completed`
- If status is `FAIL` or `BLOCKED`, set `status: blocked`

After saving, output:

```
STATUS: review complete
TASK: TASK-{NNN}
SCOPE_VIOLATIONS: none | [N violations]
RESULT: PASS | FAIL
ARTIFACT: .github/tasks/TASK-{NNN}/review.yaml
NEXT: /evaluate
```

If status is `PASS` or `PASS_WITH_DEGRADATION`, automatically proceed to `/evaluate` — do not wait for user instruction. Evaluation is mandatory after every completed review.
