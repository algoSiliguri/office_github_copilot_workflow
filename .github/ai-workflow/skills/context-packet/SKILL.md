# context-packet

## Skill purpose
Generate a bounded context packet that supports execution without silently expanding scope.

## Implemented command contract
context-packet.v1

## Required inputs
PlanArtifact.

## Produced outputs
ContextPacketArtifact.

## Authority limits
May create only a ContextPacketArtifact.
May update the TaskManifest for this task.
May not edit source files.

## Required policies
workflow-policy.v1
retrieval-policy.v1
context-policy.v1

## Required schemas
context-packet.schema.v1

## Required validators
validate-manifest
validate-artifact
validate-artifact-path
validate-context-packet

## Procedure
1. Load manifest, command contract, policies, and schema.
2. Read the plan and decide whether the packet covers the declared phase scope.
3. Retrieve only bounded context required by the plan and config budget.
4. Record included context, gaps, and execution decision.
5. Update TaskManifest: phase → context_packet, artifact_refs.context_packet → path.
6. Run validators.
