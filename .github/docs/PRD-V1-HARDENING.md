# PRD: V1 Workflow Hardening

## Problem Statement

The repository already contains a substantial portable `.github` workflow bundle for GitHub Copilot and JetBrains-first development, but the current implementation is not yet coherent enough for a trustworthy v1 release. The core issue is not lack of concepts. The issue is drift between the human-facing instructions, prompt files, agent files, manifest, contracts, schemas, policies, and validators.

Today, the system claims deterministic governance, artifact authority, and evaluation-driven improvement, but the current bundle still contains conflicting artifact roots, mixed assumptions about YAML versus JSON artifacts, incomplete validator coverage for `TaskManifest` and `EvaluationRecord`, inconsistent command authority around `TaskManifest` updates, and Copilot surface assumptions that do not cleanly match current GitHub Copilot JetBrains behavior.

As a result, the bundle cannot yet deliver a minimal, portable, governed v1 artifact chain that is both human-debuggable and machine-enforceable.

## Solution

Harden the current repository to a smallest polished v1 without redesigning the system. Keep the existing workflow model and governance intent, but align every layer to one locked runtime contract:

- full-workflow runtime artifacts live only under `.github/tasks/TASK-{NNN}/`
- all runtime task artifacts are JSON only
- `task-manifest.json` is the lifecycle authority from `/grill` onward
- `/evaluate` is mandatory after every accepted full-workflow task
- draft evaluation is non-terminal until human confirmation or override
- `/quick-task` remains a lighter path outside evaluation metrics
- retries stay inside the same `task_id` only when the declared task contract is unchanged
- scope drift is a hard review failure

The product outcome is not a new framework. The outcome is a coherent v1 workflow bundle whose docs, prompts, agents, manifest, schemas, contracts, policies, validators, and examples all agree on the same governed runtime behavior.

## User Stories

1. As a developer using GitHub Copilot in JetBrains, I want one always-on instruction entrypoint and a clear prompt surface, so that I do not depend on hidden or unsupported routing behavior.
2. As a developer running the full workflow, I want every task artifact colocated in one task folder, so that I can inspect the entire artifact chain without searching across the repository.
3. As a developer diagnosing a failed task, I want `task-manifest.json` to exist from task birth, so that blocked and stopped tasks are visible even when they never reached planning or execution.
4. As a reviewer, I want the plan, execution, verification, review, and evaluation artifacts to use one file format, so that validation and diagnosis are deterministic.
5. As a workflow maintainer, I want all runtime artifacts to be JSON and all schemas to be JSON Schema, so that validation logic remains strict and format-aligned.
6. As a workflow maintainer, I want validators to reject any artifact placed outside the canonical task folder structure, so that evaluation and diagnosis never rely on arbitrary file discovery.
7. As a reviewer, I want any file edited outside approved scope to hard-fail review, so that plan scope remains the primary governance boundary.
8. As a developer reworking a failed task, I want retry attempts to stay under the same `task_id` when the declared contract is unchanged, so that normal rework does not explode task identifiers.
9. As a governance auditor, I want previous attempts preserved under append-only history, so that no failure signal is silently overwritten.
10. As a metrics consumer, I want `human_approval_first_pass` derived from an immutable first review decision, so that human approval quality is comparable across tasks.
11. As a reviewer, I want review rejection reasons to remain structured, so that future evaluation and improvement tasks can aggregate recurring failure categories.
12. As a workflow user, I want `/evaluate` to run after every accepted full-workflow task, so that every completed task has a terminal governed assessment.
13. As a human reviewer, I want draft evaluation to remain non-authoritative until I confirm or override it, so that the workflow never self-certifies its own success.
14. As a system improver, I want failing evaluations to feed traceable `system_improvement` tasks, so that workflow changes can be tied back to evidence.
15. As a user taking the fast path, I want `/quick-task` to stay lightweight, so that low-risk work does not incur hidden full-workflow overhead.
16. As a workflow maintainer, I want `/quick-task` to escalate immediately on risk, ambiguity, scope drift, or verification uncertainty, so that unsupported work enters the governed path early.
17. As a workflow maintainer, I want the manifest, schema, and validator layers to validate the system as it actually ships, so that governance is executable rather than aspirational.
18. As a workflow upgrader, I want compatibility checks to understand every v1 artifact type, so that older task artifacts can be revalidated or marked for migration deterministically.
19. As a docs reader, I want README, architecture docs, usage docs, and prompts to agree on the same command graph and artifact model, so that the bundle teaches one behavior rather than several.
20. As a team adopting this bundle, I want a smallest polished v1 with explicit out-of-scope boundaries, so that future enhancements can be added without destabilizing the base workflow.

## Implementation Decisions

- Preserve the existing workflow concept and command graph. This PRD hardens the current bundle rather than replacing it.
- Treat `.github/copilot-instructions.md` as the always-on repository-wide instruction entrypoint.
- Treat `.github/instructions/*.instructions.md` as scoped custom instructions, not as a command router.
- Treat `.github/prompts/*.prompt.md` as reusable user-invoked prompt files, not as guaranteed autonomous slash-command runtime hooks.
- Treat `.github/agents/*.agent.md` as optional custom agent profiles only where they follow GitHub Copilot’s supported agent profile model.
- Remove or demote assumptions that plain `.md` files under `.github/agents/` are automatically loaded as JetBrains custom agents.
- Lock the canonical full-workflow runtime artifact root to `.github/tasks/TASK-{NNN}/`.
- Keep governance assets under `.github/ai-workflow/` and keep runtime artifacts out of that governance tree.
- Standardize all runtime task artifacts to JSON only.
- Keep governance files such as manifest, contracts, policies, and generated config in YAML where already established.
- Define fixed authoritative filenames at the top level of each task folder:
  `task-manifest.json`, `grill.json`, `legacy-exploration.json`, `plan.json`, `context-packet.json`, `execution.json`, `verification.json`, `review.json`, `evaluation.json`.
- Preserve historical retries using append-only `attempts/` subdirectories for at least `plan`, `execution`, `verification`, and `review`.
- Require `TaskManifest` creation during `/grill` for every full-workflow task.
- Use `TaskManifest` as the lifecycle authority and evaluation entrypoint.
- Keep `TaskManifest.status = completed` after successful review, but do not advance `phase` to `evaluated` until the evaluation is human confirmed or overridden.
- Make `/evaluate` mandatory after every `PASS` or `PASS_WITH_DEGRADATION` full-workflow review.
- Keep `EvaluationRecord` draft state non-terminal until a human reviewer confirms or overrides it.
- Keep `/quick-task` outside the mandatory evaluation and improvement-metric system.
- End `/quick-task` at `QuickTaskRecord` only.
- Require `/quick-task` escalation into `/grill` when risk, ambiguity, scope drift, or verification uncertainty appears.
- Reserve same-task retries for implementation rework only when goal, task type, success criteria, and material approved scope remain unchanged.
- Require a new `task_id` when goal, task type, success criteria, or material scope changes.
- Treat any out-of-scope changed file as a hard `FAIL` in review.
- Allow `PASS_WITH_DEGRADATION` only for degradation within approved scope, such as verification degradation or accepted quality tradeoffs.
- Keep `ReviewRecord.human_authorization` first-decision only and immutable for that review artifact.
- Derive `human_approval_first_pass` from the first review attempt only.
- Keep verification attempts inspectable in history, but do not introduce a formal verification first-pass metric in v1.
- Expand core validator coverage so that `TaskManifest` and `EvaluationRecord` are fully supported by artifact validation and compatibility checking.
- Align manifest schema, manifest validator, and shipped manifest contents so the governance layer can validate itself.
- Add deterministic validator coverage for folder naming, fixed filenames, `task_id` consistency, and `artifact_refs` consistency.
- Restore example artifact coverage so validators can be exercised against valid and invalid v1 cases.

## Testing Decisions

- Good tests should validate external workflow behavior and invariant enforcement, not incidental implementation structure inside the validators.
- Test the manifest/contract/schema/validator system as a portable bundle, using artifact fixtures and validator results as the main external behavior.
- Test the canonical artifact path model:
  valid top-level task files, invalid misplaced files, invalid filenames, invalid folder names, and mismatched `task_id`.
- Test lifecycle behavior through `TaskManifest`:
  creation at `/grill`, blocked stop-state at grill, completed-at-review state, draft-evaluation non-terminal state, and confirmed/overridden evaluated terminal state.
- Test review scope enforcement:
  clean scope pass, degraded-within-scope pass, and any out-of-scope file hard fail.
- Test evaluation gating:
  draft evaluation written, non-terminal until human action, confirmed path, overridden path, and rejection of incomplete upstream chains.
- Test first-pass review signal preservation:
  immutable first review decision, append-only review history, and correct `human_approval_first_pass` derivation from the first review artifact.
- Test compatibility behavior for every v1 artifact type, including `TaskManifest` and `EvaluationRecord`.
- Test `/quick-task` as a separate surface with strict escalation and without inclusion in full-workflow evaluation metrics.
- Prior art should come from the repository’s existing validator-focused behavior and artifact-oriented schema enforcement, especially the current validator suite and artifact compatibility patterns already present under `.github/ai-workflow/validators/`.

## Out of Scope

- Redesigning the workflow into a different framework or orchestration model.
- Adding batch or trend evaluation in v1.
- Adding dashboards, analytics backends, or richer observability stores in v1.
- Adding automated writes to governance files based on evaluation results.
- Making `/quick-task` part of the mandatory evaluation pipeline.
- Supporting dual YAML and JSON runtime artifact formats.
- Allowing relaxed scope-drift handling.
- Introducing hidden background orchestration assumptions that are not grounded in supported GitHub Copilot behavior.
- Solving every future extensibility use case before v1 ships.

## Further Notes

- This PRD intentionally hardens what already exists. The goal is a smallest polished v1, not maximum feature coverage.
- The strongest release criterion is cross-layer agreement: docs, prompts, agents, manifest, contracts, schemas, policies, validators, and examples must all describe and enforce the same runtime contract.
- The most important governance boundary for v1 is approved scope. The most important terminal artifact is human-confirmed evaluation.
- If a future enhancement threatens determinism or comparability, it should defer to v2 rather than destabilize v1.
