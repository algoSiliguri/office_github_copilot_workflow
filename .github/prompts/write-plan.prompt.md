# /write-plan

Produce a scope-locked plan grounded in the GrillRecord for this task.

#file:.github/agents/write-plan.md

## Mandatory v1 planning decisions

Every PlanArtifact must include:

- `diagnosis_confidence_gate`: for diagnosis-backed bugfixes, record confidence and whether the plan is a production fix, reproduction test, instrumentation, or test-surface improvement. Low confidence blocks production fixes.
- `retrieval_decision`: `used | skipped | unavailable`, with concrete reasons and files considered. Do not auto-explore the whole codebase; make bounded retrieval explicit.
- `tdd_decision`: whether TDD is required, why, and the test-first plan when required.

TDD is required for behavior changes, bugfixes, shared logic, public APIs, persistence/data shape, permissions/security, and cross-module behavior.

TDD is not required for docs-only, comments-only, formatting-only, or pure workflow metadata changes. If TDD is not required, record the concrete reason.
