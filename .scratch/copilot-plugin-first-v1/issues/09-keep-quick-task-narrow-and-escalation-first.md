## Parent

[2026-05-03-copilot-plugin-first-v1-prd.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/docs/superpowers/specs/2026-05-03-copilot-plugin-first-v1-prd.md)

Status: needs-triage
Type: AFK

# Keep `/quick-task` narrow and escalation-first

## What to build

Constrain `/quick-task` to strictly local, low-risk work with no public behavior change. If scope, ambiguity, or risk expands, the workflow should escalate into the main flow instead of using quick-task as a loophole.

## Acceptance criteria

- [ ] Quick-task policy limits work to low-risk, local edits with no public behavior change.
- [ ] Quick-task rejects or escalates ambiguous, multi-file, multi-module, or behavior-changing work.
- [ ] Escalation from quick-task into the main workflow is explicitly defined and easy to follow.
- [ ] Tests or validation rules prove that quick-task cannot bypass the main safety gates.

## Blocked by

- [.scratch/copilot-plugin-first-v1/issues/02-collapse-v1-onto-one-authoritative-workflow-graph.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/.scratch/copilot-plugin-first-v1/issues/02-collapse-v1-onto-one-authoritative-workflow-graph.md)
- [.scratch/copilot-plugin-first-v1/issues/05-add-risk-classed-planning-and-degraded-state-approval-gates.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/.scratch/copilot-plugin-first-v1/issues/05-add-risk-classed-planning-and-degraded-state-approval-gates.md)
