## Parent

[PRD: v1 Skill Completion and Hardening](../PRD.md)

Status: needs-triage
Type: AFK

## What to build

Add `/zoom-out` as a lightweight orientation skill (1-layer: `.agent.md` + thin `.prompt.md`). This skill answers "what is this doing?" for any unfamiliar file, module, package, service, or flow — before any formal task exists. It produces no durable artifact and gates no downstream phase.

Agent behavior:
- Accept a target (file, module, package, service, or call flow) from the user
- Read the target and its immediate context (imports, callers, key types)
- Produce a compact orientation block: responsibility, main files, call flow summary, risks or gotchas, follow-up questions worth asking before a formal task
- Stop. Do not start planning. Do not suggest edits. Do not invoke other workflow phases unless explicitly asked.

Tools: `[read, search]` — no write operations, no execute.

No prior artifact required. No `GrillRecord` or task context needed. No output artifact produced. No phase gate.

Boundary: `/zoom-out` is orientation. `/legacy-explore` is pre-planning safety. They are distinct. `/zoom-out` must not recommend plan scope or implementation approach.

## Acceptance criteria

- [ ] `.github/agents/zoom-out.agent.md` exists with `tools: [read, search]` and correct agent instructions
- [ ] `.github/prompts/zoom-out.prompt.md` exists as a thin wrapper referencing the agent via `#file:`
- [ ] Agent produces orientation block with: responsibility, main files, call flow, risks, follow-up questions
- [ ] Agent does not produce a saved artifact
- [ ] Agent does not gate or hand off to any phase unless user explicitly asks
- [ ] Agent does not recommend implementation approaches or plan scope

## Blocked by

[01 — Fix agent tool declarations](01-fix-agent-tool-declarations.md)
