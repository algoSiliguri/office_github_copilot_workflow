## Parent

[PRD: v1 Skill Completion and Hardening](..//PRD.md)

Status: needs-triage
Type: AFK

## What to build

Replace the invalid `tools: [codebase]` declaration in all four existing agent files with correct least-privilege tool sets. `codebase` is not a recognized tool name — it is silently ignored, leaving every agent with unrestricted tool access. This breaks the scope-lock model.

Correct mappings:
- `grill.md`: `[read, search]`
- `write-plan.md`: `[read, search]`
- `legacy-explore.md`: `[read, search]`
- `execute-plan.md`: `[read, edit, search, execute]`

Each agent file is a two-line change to the frontmatter `tools:` field. No schema, contract, or prompt changes required.

## Acceptance criteria

- [ ] `grill.md` frontmatter declares `tools: [read, search]`
- [ ] `write-plan.md` frontmatter declares `tools: [read, search]`
- [ ] `legacy-explore.md` frontmatter declares `tools: [read, search]`
- [ ] `execute-plan.md` frontmatter declares `tools: [read, edit, search, execute]`
- [ ] No agent file contains `codebase` in its `tools` field
- [ ] All tool names used are from the official recognized set: `read`, `edit`, `search`, `execute`, `agent`, `web`, `todo`

## Blocked by

None — can start immediately.
