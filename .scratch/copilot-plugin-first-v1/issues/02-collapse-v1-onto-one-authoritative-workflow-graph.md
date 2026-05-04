## Parent

[2026-05-03-copilot-plugin-first-v1-prd.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/docs/superpowers/specs/2026-05-03-copilot-plugin-first-v1-prd.md)

Status: needs-triage
Type: AFK

# Collapse v1 onto one authoritative workflow graph

## What to build

Remove the split between the legacy `brainstorm/write-spec` path and the newer `grill/write-plan` path. The repo should expose one authoritative v1 workflow graph across instructions, prompts, manifests, validators, and docs.

## Acceptance criteria

- [ ] `/grill` is the single pre-planning decision phase in the public v1 workflow.
- [ ] Retired commands such as `/brainstorm` and `/write-spec` are removed from v1 docs, manifests, validators, and policies.
- [ ] Public workflow sequencing is consistent across root instructions, prompt entrypoints, and supporting documentation.
- [ ] Validation fails if retired command references are reintroduced into authoritative v1 surfaces.

## Blocked by

- [.scratch/copilot-plugin-first-v1/issues/01-establish-plugin-first-public-contract.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/.scratch/copilot-plugin-first-v1/issues/01-establish-plugin-first-public-contract.md)
