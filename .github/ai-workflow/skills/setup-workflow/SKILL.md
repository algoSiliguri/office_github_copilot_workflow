# setup-workflow

## Skill purpose
Produce or update repo-local workflow wiring without changing workflow semantics.

## Implemented command contract
setup-workflow.v1

## Required inputs
None.

## Produced outputs
Workflow config artifact.

## Authority limits
May update only `.github/workflow/config.yaml`.
May not edit source files.

## Required policies
workflow-policy.v1

## Required schemas
config.schema.v1

## Required validators
validate-manifest
validate-config

## Procedure
1. Load manifest, command contract, policy, and config schema.
2. Inspect current repo layout, project description sources, and likely build/test/lint/verify commands.
3. Produce or update `.github/workflow/config.yaml`.
4. Preserve manifest authority over workflow semantics.
5. Run validation.
