## Parent

[PRD: v1 Skill Completion and Hardening](../PRD.md)

Status: needs-triage
Type: AFK

## What to build

Add `/grill-with-docs` as a doc-grounded grill variant skill (1-layer: `.agent.md` + thin `.prompt.md`). This skill challenges a proposed task or plan against existing local repository documentation before implementation begins. It must degrade cleanly to normal `/grill` when no documentation exists.

Agent behavior:
1. **Doc discovery** — search for local documentation in this order: `CONTEXT.md`, `docs/adr/`, architecture notes, `README.md`, `docs/`, runbooks, domain glossaries, existing specs. Record what was found.
2. **Degradation check** — if no useful documentation is found, emit a documentation gap note (list what was searched, state that none was found) and continue as normal `/grill` from this point. Do not fabricate project context.
3. **Doc-grounded grilling** — for each found document relevant to the task, extract: key terminology, stated constraints, prior decisions, known risks. Use these to sharpen grilling questions.
4. **Grilling session** — run the standard grill protocol (goal, assumptions, constraints, risks, decisions, success criteria) but ground each question in found documentation. Call out terminology mismatches, stale assumptions, and prior decisions that constrain the approach.
5. **Optional recommendation** — after shared understanding is reached, offer to create a lightweight `CONTEXT.md` or ADR entry if key decisions were surfaced that are not yet documented. Do not create these automatically.

Tools: `[read, search]` — no writes. Doc creation is a suggestion, not an action.

This skill is not a mandatory gate. It is an optional doc-grounded variant of `/grill`. It does not produce a `GrillRecord` — if a `GrillRecord` is needed for downstream phases, the user must run `/grill` after this session.

## Acceptance criteria

- [ ] `.github/agents/grill-with-docs.agent.md` exists with `tools: [read, search]`
- [ ] `.github/prompts/grill-with-docs.prompt.md` exists as thin wrapper referencing agent via `#file:`
- [ ] Agent searches all documented locations before declaring docs absent
- [ ] Agent emits explicit documentation gap note when no docs found, listing what was searched
- [ ] Agent degrades to normal grill protocol when no docs exist (no crash, no fabrication)
- [ ] Agent grounds at least one grilling question per found relevant document
- [ ] Agent identifies terminology mismatches and stale assumptions when docs exist
- [ ] Agent does not auto-create `CONTEXT.md` or ADRs — only recommends them

## Blocked by

[01 — Fix agent tool declarations](01-fix-agent-tool-declarations.md)
