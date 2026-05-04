## Parent

[PRD: v1 Skill Completion and Hardening](../PRD.md)

Status: needs-triage
Type: AFK

## What to build

Add `/safe-refactor` as a bounded refactor planning skill (1-layer: `.agent.md` + thin `.prompt.md`). This skill identifies refactor opportunities, computes blast radius and test surface, and hands off to the governed workflow before any edits happen. It maps to Matt Pocock's `improve-codebase-architecture` skill.

Agent behavior:
1. **Orient** — read the target area; identify the refactor goal (extract, rename, consolidate, simplify interface)
2. **Blast-radius scan** — search for all callers and dependents of the target; count affected files and modules
3. **Test surface check** — assess whether tests cover the target's observable behavior; flag untested behavior as refactor risk
4. **Refactor plan** — state the proposed change, affected call sites, and the safe execution order (what to change first to avoid breaking callers)
5. **Handoff decision**:
   - Single file, low caller count, good test coverage → suggest `/quick-task`
   - Multi-file or untested area → hand off to `/write-plan` with refactor plan as context; do not proceed with edits

Tools: `[read, search, edit]` — reads callers and dependents; edits only if scope is confirmed single-file and handed off via quick-task path. Does not execute commands.

Hard rule: no edits to files not in the declared refactor scope. No "while I'm here" changes.

## Acceptance criteria

- [ ] `.github/agents/safe-refactor.agent.md` exists with `tools: [read, search, edit]`
- [ ] `.github/prompts/safe-refactor.prompt.md` exists as thin wrapper referencing agent via `#file:`
- [ ] Agent performs blast-radius scan before any edit recommendation
- [ ] Agent assesses test surface quality before proceeding
- [ ] Agent routes single-file low-risk refactors to `/quick-task` and multi-file refactors to `/write-plan`
- [ ] Agent does not make edits beyond declared refactor scope
- [ ] Agent produces a refactor plan summary before any handoff

## Blocked by

[01 — Fix agent tool declarations](01-fix-agent-tool-declarations.md)
