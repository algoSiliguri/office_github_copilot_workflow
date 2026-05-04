## Parent

[2026-05-03-copilot-plugin-first-v1-prd.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/docs/superpowers/specs/2026-05-03-copilot-plugin-first-v1-prd.md)

Status: needs-triage
Type: AFK

# Enforce evidence-backed verification and scope-based review

## What to build

Separate verification intent from verification evidence. The workflow should treat verification as CLI-evidenced and review as a deterministic comparison between declared scope and actual changes, with degraded states surfaced explicitly.

## Acceptance criteria

- [ ] Verification success requires evidence artifacts derived from real command output.
- [ ] Plans declare verification intent, while verification artifacts capture executed commands and results.
- [ ] Review compares actual changed scope against declared plan scope and fails deterministically on mismatches.
- [ ] Partial or degraded verification states are explicitly marked and require human acknowledgment.

## Blocked by

- [.scratch/copilot-plugin-first-v1/issues/06-formalize-scoped-execution-and-cli-handoff-contracts.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/.scratch/copilot-plugin-first-v1/issues/06-formalize-scoped-execution-and-cli-handoff-contracts.md)
