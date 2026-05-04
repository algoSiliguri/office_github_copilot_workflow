## Parent

[2026-05-03-copilot-plugin-first-v1-prd.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/docs/superpowers/specs/2026-05-03-copilot-plugin-first-v1-prd.md)

Status: needs-triage
Type: AFK

# Make `/setup-workflow` produce a small valid runtime config

## What to build

Bring setup, config schema, and runtime expectations back into agreement. `/setup-workflow` should produce a small, repo-local config focused on project identity and common commands, and validation should accept that contract.

## Acceptance criteria

- [ ] `.github/workflow/config.yaml` has a small v1 contract that is human-checkable and repo-local.
- [ ] Setup output, config schema, and any validators agree on the same config shape.
- [ ] The config captures project identity plus common build/test/lint/verify commands, without heavy retrieval or topology semantics.
- [ ] Validation passes for the config emitted by the setup workflow.

## Blocked by

- [.scratch/copilot-plugin-first-v1/issues/01-establish-plugin-first-public-contract.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/.scratch/copilot-plugin-first-v1/issues/01-establish-plugin-first-public-contract.md)
