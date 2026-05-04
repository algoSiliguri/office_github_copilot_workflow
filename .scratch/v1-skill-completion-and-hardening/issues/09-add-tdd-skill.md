## Parent

[PRD: v1 Skill Completion and Hardening](../PRD.md)

Status: needs-triage
Type: AFK

## What to build

Add `/tdd` as a red-green-refactor loop skill (1-layer: `.agent.md` + thin `.prompt.md`). This skill runs test-first development cycles grounded in the repo's actual test runner command from `config.yaml`.

Agent behavior (four phases, repeating):
1. **Plan** — confirm the interface under test; identify one behavior to verify first; agree on the test seam before writing anything
2. **Tracer bullet** — write one failing test for the smallest meaningful behavior; run it; confirm it is red for the right reason
3. **Incremental loop** — write minimal code to make the test pass; run it; confirm green; repeat for next behavior
4. **Refactor** — once behaviors are covered, clean up without breaking tests; re-run after each refactor step

Philosophy: tests verify observable behavior through public interfaces, not implementation details. No testing private methods. No mocking unless isolation is genuinely required.

Tools: `[read, edit, search, execute]` — must read existing tests for prior art, write test and implementation files, run the test command.

Test runner: read `verify` or `test` command from `.github/workflow/config.yaml`. If `none`, ask the user for the test command before proceeding.

Handoff: `/tdd` is a self-contained loop. When the feature is complete and tests are green, output a summary. No artifact produced. User decides whether to proceed to `/review`.

## Acceptance criteria

- [ ] `.github/agents/tdd.agent.md` exists with `tools: [read, edit, search, execute]` and four-phase loop
- [ ] `.github/prompts/tdd.prompt.md` exists as thin wrapper referencing agent via `#file:`
- [ ] Agent reads test runner command from `config.yaml` before starting
- [ ] Agent runs the test command after each write step (does not assume green)
- [ ] Agent enforces behavior-through-interface testing philosophy (stated in instructions)
- [ ] Agent does not produce a saved task artifact
- [ ] Agent outputs a session summary when the loop completes

## Blocked by

[01 — Fix agent tool declarations](01-fix-agent-tool-declarations.md)
