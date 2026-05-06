# Architecture

## What this system is

This bundle is a **Copilot/JetBrains-native workflow bundle**. It gives Copilot a bounded command system instead of leaving it to operate as a free-form assistant. Other LLM runtimes (e.g. Claude Code) may use the same governance files but require their own entrypoint setup. `CLAUDE.md` at the repo root provides the Claude Code entrypoint.

**Enforcement model (v1):** v1 is a *governed convention system with deterministic validators and human-enforced gates*. Hard enforcement via CLI wrappers, Git hooks, or CI gates is deferred to v2.

## Main layers

Precedence chain: `copilot-instructions.md` > governance > protocols > prompts > skills > docs > agents (non-canonical)

- `copilot-instructions.md`
  Top-level workflow rules, command order, CLI handoff rules, and hard constraints.

- `prompts/`
  **Invocation layer.** User-invoked slash commands. Each prompt declares intent and entry contract. They are the binding entry point, not a guaranteed slash-command runtime.

- `ai-workflow/skills/`
  **Procedure layer.** Executable step definitions invoked by prompts. Skills own the authority and procedure for each phase.

- `ai-workflow/protocols/`
  Decision protocols for edge cases that cut across phases. Sits between governance and prompts/skills. Every protocol must be referenced by at least one prompt or skill.

- `agents/`
  **Non-canonical / advisory.** Optional custom agent profiles. Not authoritative for behavior — `prompts/` and `skills/` are.

### Two-layer behavior spec

| Layer | Location | Role | Canonical? |
|-------|----------|------|------------|
| Invocation | `prompts/` | Intent + entry contract + what artifact is produced | Yes |
| Procedure | `ai-workflow/skills/` | Executable steps, authority limits, edge-case rules | Yes |
| Advisory | `agents/` | Extended guidance, examples, heuristics | No (non-canonical) |

- `ai-workflow/manifest.yaml`
  The authoritative workflow graph. It defines which commands exist, their allowed predecessors, required inputs, outputs, and handoffs.

- `ai-workflow/contracts/commands/`
  Versioned command contracts. These define authority limits, required validators, and non-negotiable semantics.

- `ai-workflow/policies/`
  Cross-cutting rules such as quick-task eligibility, context thresholds, verification status, and review dispositions.

- `ai-workflow/schemas/`
  Artifact formats for grill, plan, execution, verification, review, and related records.

- `ai-workflow/validators/`
  Deterministic checks that enforce manifest integrity, config correctness, plan scope, artifact compatibility, and review gating.

- `workflow/config.yaml`
  Repo-local wiring only. This is the generated file that stores detected commands and project metadata for the target repo.

## Workflow model

The governed path is:

`setup-workflow -> grill -> legacy-explore if needed -> write-plan -> context-packet if needed -> execute-plan -> verify -> review -> evaluate`

There is also a narrow escape hatch:

`quick-task`

This path is only for small, low-risk, tightly scoped work. If scope or risk grows, it escalates back to the full workflow.

## Key architectural constraints

- Planning must happen before implementation.
- Implementation must stay within declared file scope.
- Verification must use real command output.
- Review must compare actual changed files against plan scope.
- Evaluation is mandatory after any accepted full-workflow review and is not terminal until a human confirms or overrides the draft.
- CLI execution requires explicit human approval when the workflow says so.

## What is canonical

For behavior, trust `.github/` over any external notes.

- Human guidance: `copilot-instructions.md`, `docs/`
- Command behavior: `prompts/` (invocation layer), `ai-workflow/skills/` (procedure layer)
- Advisory (non-canonical): `agents/`
- Enforcement and machine authority: `manifest.yaml`, contracts, policies, schemas, validators

## Runtime artifacts

Full-workflow runtime artifacts are canonical **only** under `.github/tasks/TASK-{NNN}/` — this is the single artifact root. Use strict JSON filenames: `task-manifest.json`, `grill.json`, `plan.json`, `execution.json`, `verification.json`, `review.json`, and `evaluation.json`.

`ai-workflow/artifacts/examples/` is for test fixtures and validator regression cases only. Nothing runtime belongs there.

## Architecture tree (key additions)

```
.github/
├── CLAUDE.md                        ← Claude Code entrypoint
├── copilot-instructions.md
├── prompts/                         ← invocation layer (canonical)
├── ai-workflow/
│   ├── skills/                      ← procedure layer (canonical)
│   ├── protocols/                   ← layer 3: decision protocols
│   ├── artifacts/
│   │   └── examples/                ← test fixtures only (NOT runtime)
│   └── ...
└── tasks/                           ← ONLY runtime artifact location (TASK-NNN/)
```
