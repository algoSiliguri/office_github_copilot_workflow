# /evaluate

Score a completed task against its declared success criteria and produce an EvaluationRecord for human confirmation.

## Pre-conditions

1. Read the TaskManifest at `.github/ai-workflow/artifacts/task-manifest/TASK-{NNN}.task-manifest.json`.
2. If `status` is not `completed`, stop and tell the user the task is not in a completed state — evaluation requires a completed task chain.
3. Read all upstream artifacts via `artifact_refs` in the TaskManifest.

## Scoring steps

1. From `VerificationRecord.criteria_outcomes`, compute:
   - `criteria_satisfaction_rate` = (criteria where met=true) / (total criteria). Express as decimal 0.0–1.0.
   - `criteria_outcomes_summary` = list of {criterion, met} for each entry.
2. From `ExecutionRecord.actual_changes.unplanned_files_touched`, count entries → `unplanned_files_count`.
3. From `ReviewRecord`: read `scope_match` → `scope_adherence`, `status` → `review_status`, `human_authorization.status` → `human_approval_first_pass`.
4. From `VerificationRecord`: read `status` → `verification_status`.

## Outcome classification

Apply these rules in order — first match wins:

**success**: criteria_satisfaction_rate = 1.0 AND scope_adherence = true AND review_status in [PASS, PASS_WITH_DEGRADATION] AND human_approval_first_pass = approved

**failure**: criteria_satisfaction_rate < 0.5 OR review_status in [FAIL, BLOCKED] OR human_approval_first_pass = rejected

**partial_success**: everything else (rate >= 0.5, degraded states, approved after revision)

## Output

Save EvaluationRecord to `.github/ai-workflow/artifacts/evaluation/TASK-{NNN}.evaluation.json` with `evaluation_status: draft`.

Required fields:
- `artifact_type: EvaluationRecord`
- `schema_version: evaluation.schema.v1`
- `task_id`
- `created_at` — ISO 8601 timestamp
- `source_refs` — paths to all 6 artifacts from TaskManifest
- `scores` — all 7 score fields populated
- `outcome` — classified result
- `evaluation_status: draft`
- `human_evaluation.status: draft`, `reviewer: null`, `confirmed_at: null`

After saving, present this block to the human reviewer:

```
--- EVALUATION CONFIRMATION REQUEST ---
Task: TASK-{NNN}
Outcome: success | partial_success | failure
Criteria met: X/Y (rate: Z)
Scope adherence: true | false
Unplanned files: N
Verification: VERIFIED | ...
Review: PASS | ...
Human approval (first pass): approved | rejected | pending

To confirm: type "confirm evaluation by <your name>"
To override: type "override evaluation: <category> — <details>"

Override categories: scope_violation | incorrect_implementation | criteria_not_met | verification_incomplete | quality_issue | other
---
```

When human confirms: set `evaluation_status: confirmed`, `human_evaluation.status: confirmed`, `human_evaluation.reviewer: <name>`, `human_evaluation.confirmed_at: <ISO 8601>`.

When human overrides: set `evaluation_status: overridden`, `human_evaluation.status: overridden`, `human_evaluation.reviewer: <name>`, `human_evaluation.override_reason: { category: <category>, details: <details> }`.

After human responds, update the saved EvaluationRecord, then update the TaskManifest:
- Set `phase: evaluated`
- Set `updated_at: <ISO 8601>`
- Set `artifact_refs.evaluation: .github/ai-workflow/artifacts/evaluation/TASK-{NNN}.evaluation.json`

After completing, output:

```
STATUS: evaluate complete
TASK: TASK-{NNN}
OUTCOME: success | partial_success | failure
CRITERIA_RATE: X/Y
EVALUATION_STATUS: confirmed | overridden
ARTIFACT: .github/ai-workflow/artifacts/evaluation/TASK-{NNN}.evaluation.json
```
