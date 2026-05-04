## Parent

[2026-05-03-copilot-plugin-first-v1-prd.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/docs/superpowers/specs/2026-05-03-copilot-plugin-first-v1-prd.md)

Status: needs-triage
Type: AFK

# Lock artifact compatibility to exact version tuples

## What to build

Replace broad “workflow version 1” compatibility with exact or narrowly compatible workflow, command, and schema tuples. Artifact reuse should be rejected when semantic drift has occurred, even if the top-level manifest version remains unchanged.

## Acceptance criteria

- [ ] Compatibility checks validate exact or explicitly compatible workflow, command, and schema tuples.
- [ ] Stale artifacts are rejected when command contracts or schema contracts have changed.
- [ ] Compatibility rules are documented in a way maintainers can update deliberately during future upgrades.
- [ ] Tests cover failure cases where top-level version matches but contract tuples do not.

## Blocked by

- [.scratch/copilot-plugin-first-v1/issues/05-add-risk-classed-planning-and-degraded-state-approval-gates.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/.scratch/copilot-plugin-first-v1/issues/05-add-risk-classed-planning-and-degraded-state-approval-gates.md)
- [.scratch/copilot-plugin-first-v1/issues/06-formalize-scoped-execution-and-cli-handoff-contracts.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/.scratch/copilot-plugin-first-v1/issues/06-formalize-scoped-execution-and-cli-handoff-contracts.md)
- [.scratch/copilot-plugin-first-v1/issues/07-enforce-evidence-backed-verification-and-scope-based-review.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/.scratch/copilot-plugin-first-v1/issues/07-enforce-evidence-backed-verification-and-scope-based-review.md)
