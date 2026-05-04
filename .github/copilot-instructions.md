# GitHub Copilot Enterprise — Workflow Instructions

This repo ships a portable AI workflow for IntelliJ Copilot Chat and Copilot CLI.
Project-specific config: `.github/workflow/config.yaml` — written by `/setup-workflow`, never edit manually.

## Available commands

| Command | Phase | Primary surface |
|---|---|---|
| `/setup-workflow` | Bootstrap | Plugin |
| `/grill` | Problem exploration + decisions | Plugin |
| `/legacy-explore` | Legacy/ambiguity gate (advanced) | Plugin |
| `/write-plan` | Scope lock | Plugin |
| `/context-packet` | Retrieval prep (optional) | Plugin |
| `/execute-plan` | Implementation | Plugin + CLI |
| `/verify` | Evidence-backed verification | CLI |
| `/review` | Scope-check before merge | Plugin |
| `/quick-task` | Lightweight path | Plugin |

## Workflow phase order

```
setup-workflow → grill → [legacy-explore if required] → write-plan → [context-packet] → execute-plan → verify → review
                                              ↑
                                         quick-task (parallel escape hatch)
```

## Permission ladder

| Tier | Actions | Approval required |
|---|---|---|
| 1 | Read, search, explain | None |
| 2 | Edit declared in-scope files | Plan scope |
| 3 | CLI handoff, run commands | Human-approved handoff block |
| 4 | Schema, contract, manifest changes | Explicit human instruction |

## Output contract

All phase state via status blocks — never prose paragraphs.

```
STATUS: [phase] | SURFACE: [plugin|cli] | SCOPE: [N files] | NEXT: [command]
```

## CLI handoff rules

Triggers:
1. Plan step declares `preferred_surface: copilot_cli`
2. Verification requires running commands
3. Scope spans >5 files with non-trivial changes

Always show CLI handoff block and wait for human approval before switching surfaces.

## Hard rules

- No task done without `VerificationRecord` containing command output
- No edits outside declared plan scope
- No CLI handoff without human approval
- No plan creation until GrillRecord has `decision: proceed`
- No plan creation when GrillRecord says exploration is required and no LegacyExplorationRecord exists
- All artifacts saved to `.github/tasks/TASK-{NNN}/`

## Instruction hierarchy

`.github/instructions/` > `.github/agents/` > `.github/prompts/`

Manifest at `.github/ai-workflow/manifest.yaml` is a machine-readable registry for CLI validators only — do not load it as an instruction source.
