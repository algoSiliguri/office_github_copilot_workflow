# evaluate

## Skill purpose
Score a completed task against its declared success criteria and produce a human-confirmable EvaluationRecord.

## Implemented command contract
evaluate.v1

## Required inputs
TaskManifest, GrillRecord, PlanArtifact, ExecutionRecord, VerificationRecord, ReviewRecord.

## Produced outputs
EvaluationRecord (evaluation_status: draft).

## Authority limits
May create an EvaluationRecord.
May update the TaskManifest for this task.
May not edit source files.
May not self-confirm the EvaluationRecord — human confirmation is required.

## Required policies
evaluation-policy.v1

## Required schemas
evaluation.schema.v1

## Required validators
validate-manifest
validate-artifact
validate-artifact-path
validate-evaluation-gate

## Procedure
1. Load manifest, command contract, policy, and schema.
2. Read TaskManifest. If status is not `completed`, stop — do not evaluate incomplete or abandoned tasks.
3. Read all 5 upstream workflow artifacts referenced by TaskManifest: GrillRecord, PlanArtifact, ExecutionRecord, VerificationRecord, ReviewRecord.
4. Compute scores:
   - criteria_satisfaction_rate = (count of criteria_outcomes where met=true) / (total criteria_outcomes)
   - criteria_outcomes_summary = [{criterion, met}] from VerificationRecord.criteria_outcomes
   - scope_adherence = ReviewRecord.scope_match
   - unplanned_files_count = len(ExecutionRecord.actual_changes.unplanned_files_touched)
   - verification_status = VerificationRecord.status
   - review_status = ReviewRecord.status
   - human_approval_first_pass = ReviewRecord.human_authorization.status
5. Classify outcome using declared rules from evaluation-policy.v1.
6. Write EvaluationRecord with evaluation_status: draft. Do not set confirmed_at.
7. Update TaskManifest: keep phase → review, keep status → completed, and set artifact_refs.evaluation → path.
8. Present human_evaluation block to the human reviewer for confirmation or override.
9. Only after human confirmation or override, update TaskManifest: phase → evaluated.
10. Run validators.

## Failure behavior
TaskManifest status not completed blocks evaluation.
Missing any upstream artifact blocks evaluation.
Missing criteria_outcomes blocks scoring.

## Handoff/output format
Return EvaluationRecord (draft) and present confirmation block to human. After human confirms or overrides, update evaluation_status and confirmed_at accordingly.
