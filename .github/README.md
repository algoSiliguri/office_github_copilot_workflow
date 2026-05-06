# GitHub Copilot Workflow Bundle

Portable `.github` workflow bundle for GitHub Copilot Chat, Copilot CLI, and Claude Code style agent workflows.

This repository is not a standalone application. It contains the contents you copy into a target repository's `.github/` directory.

## What this gives you

- A structured command flow from discovery to review
- Portable prompts, agents, contracts, schemas, and validators
- Scope control so implementation stays bounded to an approved plan
- Verification and review gates that require explicit evidence
- A lightweight `/quick-task` path for small changes

## Workflow commands

| Command | Purpose |
|---|---|
| `/setup-workflow` | Detect repo stack and write workflow config |
| `/diagnose` | Reproduce and isolate bugs/regressions before fixing |
| `/grill` | Clarify goal, risks, constraints, and decisions |
| `/legacy-explore` | Optional bounded exploration for ambiguous codebases |
| `/write-plan` | Produce a scope-locked implementation plan |
| `/context-packet` | Optional retrieval artifact for broader tasks |
| `/execute-plan` | Implement only the declared plan scope |
| `/verify` | Run the declared verification command and capture evidence |
| `/review` | Final scope and quality review |
| `/evaluate` | Mandatory post-review evaluation draft plus human confirmation |
| `/evaluate-system` | Periodic retrospective over completed task artifacts |
| `/evaluate-fleet` | Cross-developer retrospective over exported system evaluations |
| `/quick-task` | Small-task fast path without full workflow overhead |

## Recommended flow

For non-trivial work:

`/setup-workflow -> [/diagnose for bugs] -> /grill -> [/legacy-explore] -> /write-plan -> [/context-packet] -> /execute-plan -> /verify -> /review -> /evaluate`

Periodically run `/evaluate-system` after 5 evaluated tasks, after any human override/rejection, before workflow governance changes, or when you explicitly want to inspect system quality. It reads structured artifacts first and uses raw logs only as cited evidence for a specific pattern.

For the shared bundle, maintainers can run `/evaluate-fleet` over opt-in exported `SystemEvaluationReport`s from multiple developers. One-off local findings stay local; main `.github` changes require repeated patterns across at least 2 independent sources and still go through `/grill`. Fleet reports use evidence refs plus paraphrased pattern summaries only; they do not copy raw developer excerpts. Raw source-report drilldown requires controlled review with a reason code: `validate-pattern`, `resolve-ambiguity`, or `audit-safety`. If raw detail is reviewed, create a `RawSourceReviewRecord` with evidence refs and a paraphrased outcome summary only. This V1 threshold can be raised later as adoption grows.

Fleet reports require stable pseudonymous source IDs such as `SRC-teamA-devbox7`. Do not use real names or email addresses. Optional `repository_hint` values must be coarse and non-identifying, such as `swift-ios-app` or `spring-boot-monolith`.

Source IDs are used only to prove independent observations and avoid double-counting. Fleet evaluation compares workflow/system patterns, not developers; it must not rank, score, or blame people.

Fleet candidates are classified as `universal` or `stack_specific`. Universal candidates may be considered for the default workflow. Stack-specific candidates become optional profile guidance, such as `swift-upgrade-profile` or `legacy-java-profile`, so one ecosystem does not distort the shared default.

V1 profiles are passive guidance only. They can adjust prompts, checklist wording, retrieval hints, examples, and risk reminders, but they cannot override diagnosis, TDD decisions, scope locks, verification, evaluation, human approval, artifact schemas, or command phase order.

Profiles may add diagnostic signals, such as whether Swift API churn was surfaced before editing, but they cannot introduce new core success metrics. Global evaluation stays comparable across stacks.

Profile diagnostic signals use a controlled kebab-case ID plus a free-text explanation. Example: `swift-upgrade-api-churn-surfaced-before-edit`.

Signal IDs can be renamed or merged during V1 learning, but only through explicit proposed `diagnostic_signal_aliases` records in fleet reports so historical trends remain traceable. Canonical alias adoption requires `/grill task_type=system_improvement`.

Fleet grouping is semantic, not exact-text matching: repeated observations are normalized by problem, implicated component, target surface, and expected metric movement.

For small bounded changes:

`/setup-workflow -> /quick-task`

## Repository layout

This repo mirrors a target `.github/` folder:

- `agents/` contains custom agent profiles and command-specific guidance
- `ai-workflow/` contains manifest, contracts, policies, schemas, validators, and examples
- `instructions/` contains editing rules for workflow files
- `prompts/` contains command prompt files
- `tasks/` stores generated task artifacts
- `workflow/` stores repo-specific generated config
- `copilot-instructions.md` is the primary human-facing instruction entrypoint

## Start here

1. Read [docs/INSTALL.md](docs/INSTALL.md).
2. Read [docs/USAGE.md](docs/USAGE.md).
3. Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
4. Read [docs/CHEAT-SHEET.md](docs/CHEAT-SHEET.md).
5. Copy these files into the target repository's `.github/` directory.
6. In the target repo, run `/setup-workflow` first.

To brief an AI on the full system in one paste, use [docs/MASTER_CONTEXT.md](docs/MASTER_CONTEXT.md).

## Validation

From the target repository root after installing into `.github/`:

```bash
python3 .github/ai-workflow/validators/bootstrap
python3 .github/ai-workflow/validators/validate-manifest
python3 .github/ai-workflow/validators/validate-config .github/workflow/config.yaml
python3 .github/ai-workflow/validators/validate-release-readiness
```

## V1 release readiness

This bundle is ready for V1 local/plugin use when `validate-release-readiness` passes. V1 means the workflow is stable for GitHub Copilot Chat in JetBrains with explicit CLI handoff support, deterministic artifact validators, observable evaluation records, and governed fleet-learning artifacts.

V1 is not self-modifying. `/evaluate-system` and `/evaluate-fleet` can produce candidate improvements, but shared `.github` changes still require human-approved `/grill task_type=system_improvement`.

The V1 release bar is:

- Manifest, config, schemas, and valid example artifacts pass validation.
- Negative safety tests fail correctly.
- Command authority boundaries are documented.
- Raw fleet evidence cannot leak into aggregate reports.
- The system is usable locally without a central service.

## Important constraints

- `manifest.yaml`, schemas, and validators are governance files
- Repo-specific values belong in `.github/workflow/config.yaml`
- Workflow edits should preserve portability across repositories
- `/verify` must run a real command and capture real output before claiming success
- Full-workflow task artifacts live only under `.github/tasks/TASK-{NNN}/` as JSON files

## Docs

- [Installation](docs/INSTALL.md)
- [Effective usage](docs/USAGE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Cheat sheet](docs/CHEAT-SHEET.md)
- [Master context prompt](docs/MASTER_CONTEXT.md)
