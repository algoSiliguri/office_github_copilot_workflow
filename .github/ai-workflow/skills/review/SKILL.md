# review

## Skill purpose
Decide whether executed work is acceptable against the declared plan and verification evidence.

## Implemented command contract
review.v1

## Required inputs
PlanArtifact, ExecutionRecord, VerificationRecord, and ContextPacketArtifact when required.

## Produced outputs
ReviewRecord.

## Authority limits
May create a ReviewRecord.
May update the TaskManifest for this task.
May not edit source files.

## Required policies
review-policy.v1

## Required schemas
review.schema.v1

## Required validators
validate-manifest
validate-artifact
validate-artifact-path
validate-plan-scope
validate-review-gate

## Procedure
1. Load manifest, command contract, policy, and schemas.
2. Compare the plan, execution checkpoint, and verification outputs.
3. Require artifacts rather than narrative summaries.
4. Record findings and final disposition honestly.
5. Fail or block on scope drift, missing evidence, or missing required context state.
6. If `review.json` already exists, preserve it under `attempts/review/<ISO_TIMESTAMP>.json` before replacement.
7. Update TaskManifest: phase → review, artifact_refs.review → path; status → completed if PASS/PASS_WITH_DEGRADATION, blocked if FAIL/BLOCKED.
8. Run validators.

## Failure behavior
Missing required dependency blocks.
Scope drift or missing evidence fails or blocks.

## Handoff/output format
Return the ReviewRecord and concise result. If status is PASS or PASS_WITH_DEGRADATION, automatically hand off to `/evaluate` without waiting for user instruction.
