---
ticket: QUICK-TASK-PROOF-001
phase: spec
created: 2026-05-02
status: draft
schema_version: 1
---

# Spec: `/quick-task` Proof Slice

## Problem Statement

The current repository contains a large amount of workflow design intent, but it does not
yet embody a clean, enforceable v1 authority stack. Paths, thresholds, command behavior,
and review rules are still scattered across prompts, skills, protocols, and docs. That
makes the system hard to trust and hard to evolve.

The first irreversible implementation cut should prove the new architecture with the
smallest end-to-end slice possible: `/quick-task`.

`/quick-task` is the right proof slice because it is small enough to implement without
rebuilding the whole workflow, but still exercises the core question the system must answer
honestly:

> Can the agent perform a small change within an explicitly declared scope, or must it
> escalate before it drifts into unreviewable work?

## Objective

Create the new `.github/ai-workflow/` runtime skeleton and implement `/quick-task` end to
end through the new authority chain:

`manifest -> command contract -> policy -> schema -> skill -> validators -> QuickTaskRecord`

The slice succeeds only if:
- the runtime can discover itself from the new manifest
- `/quick-task` can classify a task against explicit policy
- scope is declared before editing
- scope and classification lock on first write
- forbidden or misclassified work escalates cleanly
- the result is recorded in a small, reviewable artifact

## Design Goals

- Prove the new runtime authority stack with the smallest realistic command
- Keep the implementation narrow enough that old design residue is not dragged into v1
- Make escalation honest without turning `/quick-task` into hidden planning
- Enforce the primary v1 safety goal: no unreviewable out-of-scope agent changes

## Non-Goals

- Do not migrate the full workflow command set
- Do not build indexing, knowledge, cross-repo, context-packet, override, or sub-agent layers
- Do not define the final v1 runtime for every command
- Do not delete/archive existing design residue as part of this slice
- Do not convert `/quick-task` into a brainstorm/spec/plan generator

## Required Runtime Surface

This slice creates only the minimum runtime structure needed for `/quick-task`:

```text
.github/
  copilot-instructions.md
  prompts/
    quick-task.prompt.md
  ai-workflow/
    manifest.yaml
    contracts/
      commands/
        quick-task.v1.yaml
    schemas/
      manifest.schema.json
      command-contract.schema.json
      quick-task.schema.json
    policies/
      quick-task-policy.v1.yaml
      review-policy.v1.yaml
    skills/
      quick-task/SKILL.md
    protocols/
      verification-gate.md
    validators/
      bootstrap
      validate-manifest
      validate-artifact
      validate-plan-scope
      validate-review-gate
    artifacts/
      .gitkeep
    logs/
      .gitkeep
```

## `/quick-task.v1` Command Contract

The command contract must define only:
- stable alias: `/quick-task`
- contract ID/version
- produced artifact: `QuickTaskRecord`
- required policies
- required validators
- authority limits
- required semantics

The command contract must not define:
- prompt bodies
- policy thresholds
- validator logic
- hidden fallback behavior
- architecture rationale

## `quick-task-policy.v1`

The policy must define only:
- `max_files`
- allowed change classes
- forbidden change classes
- required checks
- policy outcomes for forbidden class, file-limit overflow, and missing verification

The policy must not define:
- prompt text
- schema content
- command aliases
- broader full-workflow rules unrelated to quick-task eligibility

## `QuickTaskRecord`

The proof slice artifact is `QuickTaskRecord`. It must be small and reviewable.

Required fields:
- schema version
- command
- status
- task summary
- `change_class`
- planned and actual files
- escalation state/reasons
- verification evidence
- review disposition

Optional only when escalation occurs:
- `escalation_seed`

`QuickTaskRecord` is the only day-one artifact for this slice. Escalation may preserve
context inside `escalation_seed`, but it must not emit `BrainstormArtifact`, `SpecArtifact`,
or `PlanArtifact`.

## Classification and Scope Lock

`change_class` is proposed by the skill and checked by deterministic policy rules.

Rules:
- classification may be refined during read-only inspection
- classification and planned file scope lock at the first attempted workspace write
- after lock, no silent reclassification or scope expansion is allowed
- if reality contradicts the locked classification or scope, `/quick-task` must fail or
  escalate

The first attempted workspace write is any create, modify, delete, apply-patch, diff
application, or persistent IDE buffer write.

## Escalation Rules

Escalation happens when:
- the task falls into a forbidden change class
- the file count exceeds policy
- inspection reveals risky/public behavior change
- post-lock review shows the quick-task classification was wrong in a way that invalidates
  the quick-task path

Escalation produces:
- `status: ESCALATED_TO_FULL_WORKFLOW`
- a populated `QuickTaskRecord`
- an `escalation_seed` block
- default next command: `/write-spec`

Escalation preserves context, not authority.

## Validator Responsibilities

### `bootstrap`

Structural only:
- manifest exists
- manifest version supported
- required paths/contracts/schemas/policies/validators resolve

### `validate-manifest`

Structural only:
- manifest shape is valid
- required sections present
- forbidden sections absent

### `validate-artifact`

Structural only:
- `QuickTaskRecord` matches `quick-task.schema.v1`
- required fields present
- enum values valid

### `validate-plan-scope`

Limited semantics for quick-task only:
- planned file count `<= max_files`
- exact planned file paths present
- declared change class is policy-allowed
- forbidden class forces escalation

### `validate-review-gate`

Limited semantics for quick-task only:
- actual files are a subset of planned files
- verification evidence exists
- artifact status matches policy outcome
- forbidden class results in escalation, not pass
- missing evidence results in fail

## Verification Expectations

Tests are optional. Verification is not.

For this slice, verification may be:
- automated test output
- typecheck/build/lint output
- manual inspection evidence
- local run output
- before/after behavior note

If no credible evidence exists, quick-task must fail.

## Acceptance Criteria

1. The repository contains the new `.github/ai-workflow/` skeleton for the `/quick-task`
   slice.
2. `/quick-task` is defined by a command contract, not only by prompt or skill prose.
3. `quick-task-policy.v1` owns file-count and change-class thresholds.
4. `quick-task.schema.v1` validates a minimal `QuickTaskRecord`.
5. A forbidden change class produces `ESCALATED_TO_FULL_WORKFLOW` before editing begins.
6. An allowed quick-task cannot edit files outside the declared planned set.
7. The first attempted write locks classification and planned scope.
8. Post-edit misclassification cannot self-correct silently; it must fail or escalate.
9. Review-gate validation distinguishes `PASS_QUICK`, `FAIL`, and `ESCALATED_TO_FULL_WORKFLOW`.
10. No indexing, knowledge, cross-repo, context-packet, sub-agent, or override machinery is
    required for the slice to function.

## Out of Scope Follow-Up

If this slice works cleanly, later work may migrate:
- `/brainstorm`
- `/write-spec`
- `/write-plan`
- `/execute-plan`
- `/verify`
- `/review`

Those commands are explicitly not part of this spec.
