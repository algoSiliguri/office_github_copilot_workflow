## Parent

[2026-05-03-copilot-plugin-first-v1-prd.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/docs/superpowers/specs/2026-05-03-copilot-plugin-first-v1-prd.md)

Status: needs-triage
Type: AFK

# Add bounded exploration as the required legacy/ambiguity gate

## What to build

Introduce a first-class bounded exploration capability for legacy or unclear repositories. Planning must not silently expand into repo archaeology; instead, the workflow should trigger a dedicated exploration phase when ambiguity or risk signals are present, and produce a compact artifact that planning can consume.

## Acceptance criteria

- [ ] The workflow defines explicit triggers for required exploration, including unknown target files, unclear ownership, weak tests, or likely multi-module impact.
- [ ] A bounded exploration phase exists as a distinct capability with scoped search rules and a compact output artifact.
- [ ] `/grill` and `/write-plan` do not implicitly replace or absorb broad exploration behavior.
- [ ] Legacy-monolith support in docs and workflow rules is conditioned on this exploration gate.

## Blocked by

- [.scratch/copilot-plugin-first-v1/issues/02-collapse-v1-onto-one-authoritative-workflow-graph.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/.scratch/copilot-plugin-first-v1/issues/02-collapse-v1-onto-one-authoritative-workflow-graph.md)
- [.scratch/copilot-plugin-first-v1/issues/03-make-setup-workflow-produce-a-small-valid-runtime-config.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/.scratch/copilot-plugin-first-v1/issues/03-make-setup-workflow-produce-a-small-valid-runtime-config.md)
