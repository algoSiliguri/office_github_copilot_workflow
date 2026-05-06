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
  **Conditionally mandatory.** Controlled by `context_packet_required` in `PlanArtifact`. If `true`, `/execute-plan` preflight halts when `context-packet.json` is absent. Builds bounded execution context for the plan.

- `/execute-plan`
  Implements only the files and steps declared in the plan.

- `/verify`
  Runs the plan's verification command exactly as written and captures evidence.

- `/review`
  Checks scope match and verification status before merge. On PASS or PASS_WITH_DEGRADATION, automatically hands off to `/evaluate`.

- `/evaluate`
  Mandatory after every accepted full-workflow review. AI computes scores from all upstream artifacts, presents draft to human, then writes **once** on confirmation/override: `TaskManifest` (phase: evaluated, status: completed) and `EvaluationRecord`. Terminal artifact of every completed task.

  **Outcome bands:**

  | Band | Condition |
  |------|-----------|
  | `success` | rate == 1.0 |
  | `partial_success_high` | rate >= 0.8 |
  | `partial_success_low` | rate >= 0.5 |
  | `failure` | rate < 0.5, or review FAIL/BLOCKED, or human rejected |

  After confirmation, a completion block shows `improvement_signal`, unmet criteria IDs, and a pre-filled `/grill` suggestion. No automatic task creation.

- `/quick-task`
  Fast path for very small, low-risk work. Always produces a `QuickTaskRecord` with `eligibility_check`. Escalation is a hard stop.

  **Eligibility rules (all must pass):**

  | # | Rule |
  |---|------|
  | 1 | Maximum 2 files touched |
  | 2 | No protected file types (schemas, validators, contracts, manifest, policies) |
  | 3 | No new file creation |
  | 4 | Change is self-contained within declared files |
  | 5 | No architectural decisions required |
  | 6 | Verification is trivial (syntax, linting, or manual visual check) |
  | 7 | No CLI handoff required |
  | 8 | No ambiguity about target files or intended change |

## Not in v1

- `/diagnose` — future v2 diagnostic command for health-checking workflow files. Not available in v1.

## Typical flows

Small change:

`/setup-workflow -> /quick-task`

Normal change:

`/setup-workflow -> /grill -> /write-plan -> /execute-plan -> /verify -> /review -> /evaluate`

Ambiguous or legacy change:

`/setup-workflow -> /grill -> /legacy-explore -> /write-plan -> /execute-plan -> /verify -> /review -> /evaluate`

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
