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
| `/context-packet` | Retrieval prep (conditionally mandatory) | Plugin |
| `/execute-plan` | Implementation | Plugin + CLI |
| `/verify` | Evidence-backed verification | CLI |
| `/review` | Scope-check before merge | Plugin |
| `/evaluate` | Human-confirmed task evaluation | Plugin |
| `/quick-task` | Lightweight path | Plugin |

## Workflow phase order

```
setup-workflow → grill → [legacy-explore if required] → write-plan → [context-packet] → execute-plan → verify → review → evaluate
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

## Enforcement model

v1 is a governed convention system. Validators are deterministic gates but only run when invoked. No phase is complete unless required validators were run and output was shown in the completion block. Invalid artifacts are detectable, not impossible. Hard enforcement via CLI wrapper, Git hooks, or CI is a v2 feature.

Every command completion block must include:
- `VALIDATORS_REQUIRED:` list of required validators for this phase
- `VALIDATORS_RUN:` list actually run, with pasted output
- `ARTIFACTS_WRITTEN:` list of artifact paths written
- `NEXT_ALLOWED:` next allowed command

## Precedence chain

When rules conflict, the higher layer wins:
1. `.github/copilot-instructions.md` — always-on
2. `manifest` / `contracts` / `schemas` / `policies` / `validators` — governance authority
3. `protocols/` — reusable cross-cutting decision procedures (not governance authority)
4. `prompts/` — command invocation layer
5. `skills/` — phase procedure layer
6. `docs/` — explanation only
7. `agents/` — non-canonical / advisory

## Runtime scope

v1 primary runtime: GitHub Copilot Chat in JetBrains. `copilot-instructions.md` is the canonical always-on entrypoint. Governance files are runtime-neutral. Other LLM runtimes (Claude Code, etc.) require their own entrypoint setup — see `CLAUDE.md` at repo root.

## Hard rules

- No task done without `VerificationRecord` containing command output
- No edits outside declared plan scope
- No CLI handoff without human approval
- No plan creation until GrillRecord has `decision: proceed`
- No plan creation when GrillRecord says exploration is required and no LegacyExplorationRecord exists
- All full-workflow runtime artifacts saved as JSON under `.github/tasks/TASK-{NNN}/`

## Instruction hierarchy

`.github/copilot-instructions.md` is always-on. `.github/instructions/*.instructions.md` may add scoped instructions. `.github/prompts/*.prompt.md` are reusable user-invoked prompts. Only `.agent.md` files under `.github/agents/` should be treated as supported custom agent profiles.

Manifest at `.github/ai-workflow/manifest.yaml` is a machine-readable registry for CLI validators only — do not load it as an instruction source.
