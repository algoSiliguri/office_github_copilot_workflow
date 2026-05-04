## Parent

[PRD: v1 Skill Completion and Hardening](../PRD.md)

Status: needs-triage
Type: AFK

## What to build

Audit the four protocol files in `.github/ai-workflow/protocols/` and make every surviving protocol visible in Copilot plugin sessions via explicit agent references. Currently no agent or instruction file references any protocol — they are dead from the plugin's perspective.

Audit decision per protocol:
- `verification-gate.md` — wire to `/verify` agent
- `stage-review.md` — wire to `/review` agent
- `phase-checkpoint.md` — wire to `/execute-plan` agent
- `retrieval-decision.md` — audit: if content is fully covered by `context-policy.v1.yaml` → delete; if it adds unique guidance not in the policy → wire to the `/context-packet` agent

Wiring pattern (hybrid — apply to each surviving protocol):
1. Add an inline rule summary to the agent (one sentence stating the key enforcement rule)
2. Add an explicit `#file:.github/ai-workflow/protocols/<name>.md` reference below the summary

Hard rule: any protocol file not referenced by at least one agent or instruction after this work is deleted. No dead abstractions ship in v1.

## Acceptance criteria

- [ ] `verification-gate.md` referenced in `execute-plan` or `verify` agent with inline summary + `#file:` reference
- [ ] `stage-review.md` referenced in `review` agent with inline summary + `#file:` reference
- [ ] `phase-checkpoint.md` referenced in `execute-plan` agent with inline summary + `#file:` reference
- [ ] `retrieval-decision.md` either deleted (if redundant with context policy) or wired to context-packet agent with documented reason
- [ ] Zero protocol files exist under `.github/ai-workflow/protocols/` without at least one referencing agent or instruction
- [ ] Each `#file:` reference uses the correct relative path resolvable from the Copilot plugin context

## Blocked by

None — can start immediately.
