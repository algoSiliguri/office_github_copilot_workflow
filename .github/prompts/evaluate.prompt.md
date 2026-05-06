# /evaluate

Score a completed task against its declared success criteria and produce an EvaluationRecord for human confirmation.

## Pre-conditions

1. Read the TaskManifest at `.github/tasks/TASK-{NNN}/task-manifest.json`.
2. If `status` is not `completed`, stop and tell the user the task is not in a completed state — evaluation requires a completed task chain.
3. Read all upstream artifacts via `artifact_refs` in the TaskManifest.

## Scoring steps

1. From `VerificationRecord.criteria_outcomes`, compute:
   - `criteria_count` = total criteria count
   - `criteria_met_count` = count where met=true
   - `criteria_unmet_count` = count where met=false
   - `criteria_satisfaction_rate` = criteria_met_count / criteria_count. Express as decimal 0.0–1.0.
   - `criteria_outcomes_summary` = list of {criterion, criterion_id, met} for each entry.
2. From `ExecutionRecord.actual_changes.unplanned_files_touched`, count entries → `unplanned_files_count`.
3. From `ReviewRecord`: read `scope_match` → `scope_adherence`, `status` → `review_status`, `human_authorization.status` → `human_approval_first_pass`.
4. From `VerificationRecord`: read `status` → `verification_status`.

## Outcome classification

Apply these rules in order — first match wins:

**success**: criteria_satisfaction_rate == 1.0 AND scope_adherence == true AND review_status in [PASS, PASS_WITH_DEGRADATION] AND human_approval_first_pass == approved

**failure**: criteria_satisfaction_rate < 0.5 OR review_status in [FAIL, BLOCKED] OR human_approval_first_pass == rejected

**partial_success_high**: criteria_satisfaction_rate >= 0.8 (and does not meet success conditions)

**partial_success_low**: criteria_satisfaction_rate >= 0.5 (and does not meet partial_success_high conditions)

Set `outcome_band` = same value as `outcome`.

## Improvement signal

Derive `improvement_signal` from the primary failure reason:

| Condition | Signal |
|-----------|--------|
| Unmet criteria exist | `criteria_not_met` |
| scope_adherence == false | `scope_violation` |
| verification_status in [FAILED, BLOCKED] | `verification_incomplete` |
| human_approval_first_pass == rejected | `quality_issue` |
| outcome == success | `none` |
| other | `other` |

Apply in order — first match wins.

## Output

Save EvaluationRecord to `.github/tasks/TASK-{NNN}/evaluation.json` with `evaluation_status: draft`.

Required fields:
- `artifact_type: EvaluationRecord`
- `schema_version: evaluation.schema.v1`
- `task_id`
- `created_at` — ISO 8601 timestamp
- `source_refs` — paths to all 6 artifacts from TaskManifest
- `scores` — all required score fields: `criteria_satisfaction_rate`, `criteria_count`, `criteria_met_count`, `criteria_unmet_count`, `outcome_band`, `criteria_outcomes_summary`, `scope_adherence`, `unplanned_files_count`, `verification_status`, `review_status`, `human_approval_first_pass`
- `outcome` — classified result
- `improvement_signal` — derived signal
- `evaluation_status: draft`
- `human_evaluation.status: draft`, `reviewer: null`, `confirmed_at: null`
- `validated_under` — exact workflow/command/schema/config tuple

After saving the draft, present this block to the human reviewer:

```
--- EVALUATION CONFIRMATION REQUEST ---
Task: TASK-{NNN}
Outcome: <outcome>
Outcome band: <outcome_band>
Criteria met: <criteria_met_count>/<criteria_count> (rate: <criteria_satisfaction_rate>)
Unmet criteria: <list of unmet criterion IDs or "none">
Scope adherence: true | false
Unplanned files: N
Verification: VERIFIED | ...
Review: PASS | ...
Human approval (first pass): approved | rejected | pending
Improvement signal: <improvement_signal>

To confirm: type "confirm evaluation by <your name>"
To override: type "override evaluation: <category> — <details>"

Override categories: scope_violation | incorrect_implementation | criteria_not_met | verification_incomplete | quality_issue | other
---
```

When human confirms: set `evaluation_status: confirmed`, `human_evaluation.status: confirmed`, `human_evaluation.reviewer: <name>`, `human_evaluation.confirmed_at: <ISO 8601>`.

When human overrides: set `evaluation_status: overridden`, `human_evaluation.status: overridden`, `human_evaluation.reviewer: <name>`, `human_evaluation.override_reason: { category: <category>, details: <details> }`.

After human confirms or overrides, update the saved EvaluationRecord, then make the single terminal TaskManifest update:
- Set `phase: evaluated`
- Set `status: completed`
- Set `artifact_refs.evaluation: .github/tasks/TASK-{NNN}/evaluation.json`
- Set `evaluated_at: <ISO 8601>`
- Set `updated_at: <ISO 8601>`

Do NOT update the TaskManifest before human confirmation. The draft EvaluationRecord is not authoritative.

After completing, output:

```
--- EVALUATION COMPLETE ---
TASK: TASK-{NNN}
OUTCOME: <outcome_band>
CRITERIA: <criteria_met_count>/<criteria_count> (rate: <criteria_satisfaction_rate>)
UNMET_CRITERIA: <list of unmet criterion IDs, or "none">
SCOPE_ADHERENCE: true | false
VERIFICATION: <verification_status>
REVIEW: <review_status>
EVALUATION_STATUS: confirmed | overridden
IMPROVEMENT_SIGNAL: <improvement_signal>
SUGGESTED_NEXT_ACTION: <if improvement_signal != none: "Consider: /grill task_type=system_improvement triggered_by=.github/tasks/TASK-{NNN}/evaluation.json failure_category=<improvement_signal>". If none: "No improvement action required.">
VALIDATORS_REQUIRED: validate-evaluation-gate, validate-artifact
VALIDATORS_RUN: <list with pasted output>
ARTIFACTS_WRITTEN: .github/tasks/TASK-{NNN}/evaluation.json, .github/tasks/TASK-{NNN}/task-manifest.json
NEXT_ALLOWED: task complete
---
```
