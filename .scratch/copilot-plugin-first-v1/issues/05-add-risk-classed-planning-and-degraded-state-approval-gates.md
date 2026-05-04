## Parent

[2026-05-03-copilot-plugin-first-v1-prd.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/docs/superpowers/specs/2026-05-03-copilot-plugin-first-v1-prd.md)

Status: needs-triage
Type: AFK

# Add risk-classed planning and degraded-state approval gates

## What to build

Upgrade the plan contract so each step declares files, verification intent, preferred surface, and a risk class. Degraded or high-risk work must require explicit human acknowledgment before execution or verification proceeds.

## Acceptance criteria

- [ ] Plan artifacts require per-step file scope, verification intent, preferred execution surface, and risk class.
- [ ] Risk classes at minimum distinguish safe, degraded, and high-risk work.
- [ ] Degraded execution or verification states require explicit human acknowledgment, not just narrative mention.
- [ ] Approval gates are enforced through artifact structure or validation, not only through prose guidance.

## Blocked by

- [.scratch/copilot-plugin-first-v1/issues/02-collapse-v1-onto-one-authoritative-workflow-graph.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/.scratch/copilot-plugin-first-v1/issues/02-collapse-v1-onto-one-authoritative-workflow-graph.md)
- [.scratch/copilot-plugin-first-v1/issues/03-make-setup-workflow-produce-a-small-valid-runtime-config.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/.scratch/copilot-plugin-first-v1/issues/03-make-setup-workflow-produce-a-small-valid-runtime-config.md)
- [.scratch/copilot-plugin-first-v1/issues/04-add-bounded-exploration-as-the-required-legacy-ambiguity-gate.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/.scratch/copilot-plugin-first-v1/issues/04-add-bounded-exploration-as-the-required-legacy-ambiguity-gate.md)
