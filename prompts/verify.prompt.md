# /verify

Run the verification command from the plan and record output as evidence.

## Pre-conditions

1. Read the PlanArtifact at `.github/tasks/TASK-{NNN}/plan.yaml`.
2. Read the ExecutionRecord at `.github/tasks/TASK-{NNN}/execution.yaml`.
3. Confirm `execution.status: completed`. If blocked or escalated, stop and tell the user.

## Verification steps

1. Run the `verification_command` declared in the plan exactly as written — do not modify it.
2. Capture the full command output verbatim.
3. Record whether the command passed or failed.
4. If verification only passes with a known degradation, record the degradation explicitly and collect human acknowledgment before claiming `VERIFIED_WITH_DEGRADATION`.

## Rules

- Never claim VERIFIED without running the command and capturing real output.
- Never paraphrase the output — record it verbatim in `command_output`.
- If the command cannot be run from the plugin, issue a CLI handoff block and wait for human approval.

## Output

Save a VerificationRecord to `.github/tasks/TASK-{NNN}/verification.yaml`.

Required fields:
- `artifact_type: VerificationRecord`
- `schema_version: verification.schema.v1`
- `task_id`
- `primary_surface: copilot_cli` (verification always runs commands)
- `secondary_surfaces_allowed: [copilot_plugin]`
- `plan_ref: .github/tasks/TASK-{NNN}/plan.yaml`
- `execution_ref: .github/tasks/TASK-{NNN}/execution.yaml`
- `changed_files` — list of files from execution.actual_changes.files_touched
- `verification_command` — exact command from plan
- `verification_command_run` — exact command actually run
- `command_output` — verbatim output from running the command (required, non-empty)
- `evidence` — non-empty list of concrete evidence strings or paths derived from the command run
- `status: VERIFIED | VERIFIED_WITH_DEGRADATION | FAILED | BLOCKED`
- `degraded_reason` — required when status is VERIFIED_WITH_DEGRADATION
- `human_acknowledgment` — required and approved when status is VERIFIED_WITH_DEGRADATION
- `validated_under` — exact workflow/command/schema/config tuple

After saving, output:

```
STATUS: verify complete
TASK: TASK-{NNN}
COMMAND: <verification_command>
RESULT: VERIFIED | FAILED
ARTIFACT: .github/tasks/TASK-{NNN}/verification.yaml
NEXT: /review
```
