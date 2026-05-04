# Artifact Examples

Example artifacts were removed during the plugin-first v1 contract rewrite because the prior examples encoded obsolete workflow graphs and stale `validated_under` fields.

Regenerate examples only after the following contracts are treated as authoritative together:

- `.github/ai-workflow/manifest.yaml`
- `.github/ai-workflow/schemas/`
- `.github/ai-workflow/validators/`
- `.github/prompts/`

Do not reintroduce examples that use the retired `schema_version / command_version / config_version` tuple or the removed `brainstorm / write-spec` workflow.
