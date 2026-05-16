# Phase 1 Artifact Contracts

These are the stable artifact contracts for v1. Each artifact is owned by exactly one workflow phase. Schema version strings are the migration gate: a v2 artifact fails all v1 validators automatically. Adding a field requires bumping the schema_version everywhere and updating all validators that check it.

---

## GraphRecord

**Path:** `.github/workflow/graph-record.json`
**Owned by:** `/setup`
**Validator:** `check-setup`, `check-graph`
**Schema version:** `graph-record.schema.v1`

Required fields: `schema_version`, `provider`, `graph_dir`, `graph_json`, `graph_report`, `manifest`, `copilot_install_expected`, `graph_status`, `last_checked_at`, `status`, `generated_at`, `repo_root`, `git_commit`, `branch`, `graphify_manifest_path`, `graph_output_exists`, `approval`, `notes`.

Extension rule: optional fields may be added without bumping schema_version. Removing or renaming required fields is a breaking change requiring `graph-record.schema.v2`.

---

## PlanRecord

**Path:** `.github/tasks/TASK-{NNN}/plan.json`
**Owned by:** `/plan`
**Validator:** `check-plan`, `check-graph` (with plan arg), `check-state`
**Schema version:** `plan-record.schema.v1`

Required fields: `schema_version`, `task_id`, `created_at`, `phase`, `status`, `summary`, `intended_files`, `risk`, `verification_command`, `graph_freshness_mode`, `graph_usage`, `graph_scope`, `graph_refs`, `context_refs`, `assumptions`, `deviations`, `planning`, `diagnosis`, `quick_task_classification`, `human_approval`, `approvals`.

Extension rule: same as GraphRecord.

---

## ExecutionRecord

**Path:** `.github/tasks/TASK-{NNN}/execution.json`
**Owned by:** `/execute`
**Validator:** `check-execution`, `check-state`
**Schema version:** `execution-record.schema.v1`

Required fields: `schema_version`, `task_id`, `created_at`, `phase`, `plan_ref`, `approved_files`, `modified_files`, `status`, `graph_refs`, `command_refs`, `checkpoints`, `risky_tool_approvals`, `deviations`, `approvals`.

Extension rule: same as GraphRecord.

---

## VerificationRecord

**Path:** `.github/tasks/TASK-{NNN}/verification.json`
**Owned by:** `/verify`
**Validator:** `check-verification`
**Schema version:** `verification-record.schema.v1`

Required fields: `schema_version`, `task_id`, `created_at`, `phase`, `plan_ref`, `execution_ref`, `verification_command`, `command_executed_at`, `command_exit_code`, `command_refs`, `result`, `evidence_summary`, `graph_context_used`, `graph_refs`, `degraded_verification`, `human_acknowledgment`.

Extension rule: same as GraphRecord.

---

## ReviewRecord

**Path:** `.github/tasks/TASK-{NNN}/review.json`
**Owned by:** `/verify`
**Validator:** `check-verification` (validates both)
**Schema version:** `review-record.schema.v1`

Required fields: `schema_version`, `task_id`, `created_at`, `phase`, `approved_files`, `actual_files`, `scope_drift`, `findings`, `assumptions`, `deviations`, `human_approval`, `human_authorization`, `approvals`, `graph_scope_review`.

Extension rule: same as GraphRecord.

---

## SessionEventLog

**Path:** `.github/tasks/TASK-{NNN}/logs/events.jsonl` (gitignored)
**Owned by:** hook scripts (`log-event.py`, `pre-tool-use.py`, `post-tool-use.py`, `agent-stop.py`)
**Validator:** `check-state` (presence check); event schema in `schemas/event.schema.json`
**Schema version:** `event.schema.v1`

Required fields per event: `schema_version`, `event_id`, `task_id`, `phase`, `timestamp`, `event_type`, `tool_name`, `target_files`, `decision`, `reason`, `risk`, `redacted`.

Extension rule: `metadata` object is the designated extension point for hook-specific fields. Adding to `metadata` is non-breaking. Top-level field additions require schema version bump.

---

## MemoryCandidate

**Path:** `.github/local-memory/inbox/MEM-CAND-{NNN}.json` (gitignored)
**Owned by:** evaluation or manual nomination
**Validator:** `check-memory`
**Schema version:** `memory-candidate.schema.json`

Extension rule: same as GraphRecord.

---

## EvalSummary

**Path:** `.github/evals/runs/EVAL-{ID}/summary.json` (gitignored)
**Owned by:** `evaluate-tasks`
**Validator:** output schema in `schemas/eval-summary.schema.json`
**Schema version:** `eval-summary.schema.v1`

Extension rule: same as GraphRecord.

---

## Version Gate

Schema version strings are the migration gate for all artifacts. Validators use exact-match checks (e.g. `schema_version == "plan-record.schema.v1"`). A v2 artifact with `schema_version: "plan-record.schema.v2"` fails all v1 validators immediately. No separate semver field is required.
