## Parent

[PRD: v1 Skill Completion and Hardening](../PRD.md)

Status: needs-triage
Type: AFK

## What to build

Add `/diagnose` as a disciplined bug investigation skill (1-layer: `.agent.md` + thin `.prompt.md`). This skill runs a structured diagnosis loop when a developer reports a bug, regression, or unexpected behavior. It prevents freeform debugging chat from bypassing the governed workflow.

Agent behavior (six phases, in order):
1. **Build a feedback loop** — identify the fastest deterministic pass/fail signal: failing test, CLI invocation, curl script, throwaway harness. Confirm it reproduces the bug before proceeding.
2. **Reproduce** — execute the feedback loop description, confirm bug matches report.
3. **Hypothesise** — generate 3–5 ranked hypotheses, each as a falsifiable prediction: "If X is the cause, then Y will change."
4. **Instrument** — test one hypothesis at a time using targeted log reads, grep for relevant call sites, or reading stack trace context. Never blanket-log.
5. **Fix + regression test** — state the fix and where a regression test should be added. Do not write the fix — hand off to `/write-plan` or `/quick-task` depending on scope.
6. **Post-mortem** — state root cause, affected area, and whether an architectural improvement is indicated.

Tools: `[read, search]` — analysis only. No file edits. Fix handoff goes to the governed workflow.

Handoff rule: if the fix is trivial (one file, low risk) → suggest `/quick-task`. If non-trivial → suggest `/grill` or `/write-plan` with diagnosis findings as context.

## Acceptance criteria

- [ ] `.github/agents/diagnose.agent.md` exists with `tools: [read, search]` and six-phase protocol
- [ ] `.github/prompts/diagnose.prompt.md` exists as thin wrapper referencing agent via `#file:`
- [ ] Agent covers all six phases in order
- [ ] Agent does not write files or make edits
- [ ] Agent explicitly states handoff path (quick-task vs grill/write-plan) based on fix scope
- [ ] Agent produces a post-mortem summary as the final output

## Blocked by

[01 — Fix agent tool declarations](01-fix-agent-tool-declarations.md)
