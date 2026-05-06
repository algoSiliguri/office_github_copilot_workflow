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
validate-quick-task-preclassify
validate-artifact
validate-plan-scope

## Procedure
1. Load manifest.
2. Load command contract and policy.
3. Run the preclassify validator before the first file edit.
4. Classify the task against quick-task-policy.v1.
5. List exact files before editing.
6. Record `bypass_justification` explaining why retrieval, TDD, and full EvaluationRecord are safely bypassed.
7. If any bypass cannot be justified concretely, create QuickTaskRecord with ESCALATED_TO_FULL_WORKFLOW.
8. If allowed, make only declared edits.
9. Run available verification.
10. Create QuickTaskRecord.
11. Run artifact and scope validation.

## Failure behavior
Missing required dependency blocks.
Forbidden change class escalates.
Unplanned file change fails.
Missing verification fails.
Missing bypass justification escalates.

## Handoff/output format
Return the QuickTaskRecord and concise result.
