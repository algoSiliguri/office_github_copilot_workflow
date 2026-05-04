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
May create only a ReviewRecord.
May not edit source files.

## Required policies
review-policy.v1

## Required schemas
review.schema.v1

## Required validators
validate-manifest
validate-artifact
validate-plan-scope
validate-review-gate

## Procedure
1. Load manifest, command contract, policy, and schemas.
2. Compare the plan, execution checkpoint, and verification outputs.
3. Require artifacts rather than narrative summaries.
4. Record findings and final disposition honestly.
5. Fail or block on scope drift, missing evidence, or missing required context state.
6. Run validators.

## Failure behavior
Missing required dependency blocks.
Scope drift or missing evidence fails or blocks.

## Handoff/output format
Return the ReviewArtifact and concise result.
