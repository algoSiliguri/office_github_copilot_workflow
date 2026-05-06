# /execute-plan

Execute the declared plan scope for this task. Stay bounded to plan scope.

#file:.github/agents/execute-plan.md

## Mandatory v1 execution discipline

Before editing, read `plan.tdd_decision`.

If `tdd_decision.required: true`, execute through a test-first loop and record `tdd_execution` in the ExecutionRecord:

1. failing test or reproduced failure signal
2. minimal implementation
3. verification command output
4. safe refactor if needed

If TDD was required but cannot be followed, stop and escalate to `/write-plan`. Do not silently continue.
