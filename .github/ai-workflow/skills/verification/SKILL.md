# verify

## Skill purpose
Turn executed work into a verification artifact with explicit evidence.

## Implemented command contract
verify.v1

## Required inputs
PlanArtifact plus ExecutionRecord, and ContextPacketArtifact when required.

## Produced outputs
VerificationRecord.

## Authority limits
May create a VerificationRecord.
May update the TaskManifest for this task.
May not edit source files.

## Required policies
verification-policy.v1
review-policy.v1

## Required schemas
verification.schema.v1

## Required validators
validate-manifest
validate-artifact
validate-plan-scope
validate-review-gate
validate-criteria-coverage

## Procedure
1. Load manifest, command contract, policies, and schema.
2. Compare execution checkpoint changes against the plan scope.
3. Verify required context-packet state when one was required.
4. Read GrillRecord success_criteria — produce one criteria_outcomes entry per criterion (1:1). criteria_outcomes is the authoritative pass/fail record per declared success criterion. Multiple criteria may share one verification_command_ref.
5. Record exact verification evidence.
6. Preserve degraded status honestly when applicable.
7. Produce the VerificationRecord.
8. Update TaskManifest: phase → verification, artifact_refs.verification → path; status → blocked if BLOCKED.
9. Run validators including validate-criteria-coverage.

## Failure behavior
Missing required dependency blocks.
Missing evidence fails or blocks.

## Handoff/output format
Return the VerificationRecord and concise result.
