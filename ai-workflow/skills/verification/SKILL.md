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
May create only a VerificationRecord.
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

## Procedure
1. Load manifest, command contract, policies, and schema.
2. Compare execution checkpoint changes against the plan scope.
3. Verify required context-packet state when one was required.
4. Record exact verification evidence.
5. Preserve degraded status honestly when applicable.
6. Produce the VerificationRecord.
6. Run validators.

## Failure behavior
Missing required dependency blocks.
Missing evidence fails or blocks.

## Handoff/output format
Return the VerificationRecord and concise result.
