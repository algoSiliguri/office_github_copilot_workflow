# Cheat Sheet

## First command

Run:

`/setup-workflow`

## Core commands

- `/setup-workflow`
  Detects repo stack and writes `.github/workflow/config.yaml`.

- `/grill`
  Clarifies goals, constraints, risks, decisions, and success criteria before planning.

- `/legacy-explore`
  Use only when the target area is unclear, legacy, or risky.

- `/write-plan`
  Creates the scope-locked implementation plan.

- `/context-packet`
  Builds bounded execution context when the plan requires it.

- `/execute-plan`
  Implements only the files and steps declared in the plan.

- `/verify`
  Runs the plan's verification command exactly as written and captures evidence.

- `/review`
  Checks scope match and verification status before merge.

- `/quick-task`
  Fast path for very small, low-risk work.

## Typical flows

Small change:

`/setup-workflow -> /quick-task`

Normal change:

`/setup-workflow -> /grill -> /write-plan -> /execute-plan -> /verify -> /review`

Ambiguous or legacy change:

`/setup-workflow -> /grill -> /legacy-explore -> /write-plan -> /execute-plan -> /verify -> /review`

## When Copilot should stop

- Planning cannot continue if `/grill` says `decision: stop`.
- Planning cannot continue if exploration is required but not done.
- Execution cannot touch files outside declared scope.
- Verification cannot pass without real evidence.
- Review cannot pass if changed files exceed plan scope.

## CLI boundary

Use Copilot Chat for orchestration and planning.

Use CLI only when:

- the plan says a step prefers CLI
- commands must actually run
- the change is large enough to require CLI handoff

## Keep in mind

- `.github/` is the canonical workflow bundle.
- `workflow/config.yaml` is repo-local wiring, not workflow design.
- Governance files are `manifest.yaml`, schemas, and validators.
