## Parent

[2026-05-03-copilot-plugin-first-v1-prd.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/docs/superpowers/specs/2026-05-03-copilot-plugin-first-v1-prd.md)

Status: needs-triage
Type: AFK

# Formalize scoped execution and CLI handoff contracts

## What to build

Make execution obey declared plan scope and make CLI handoff explicit. When command execution is required, the workflow should emit a bounded handoff contract describing why the shell is needed, which commands and files are allowed, which actions remain blocked, and what artifact must be returned.

## Acceptance criteria

- [ ] Execution behavior is defined to stay inside declared plan scope and changed-file intent.
- [ ] CLI handoff blocks include the reason, allowed commands, allowed files, blocked actions, and return artifact.
- [ ] Plugin-first orchestration and CLI-backed execution boundaries are documented consistently.
- [ ] Execution cannot silently broaden scope beyond what the plan or handoff declares.

## Blocked by

- [.scratch/copilot-plugin-first-v1/issues/05-add-risk-classed-planning-and-degraded-state-approval-gates.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/.scratch/copilot-plugin-first-v1/issues/05-add-risk-classed-planning-and-degraded-state-approval-gates.md)
