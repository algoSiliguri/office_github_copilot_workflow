#!/usr/bin/env bash
set -euo pipefail

python3 .github/workflow/validators/check-setup
python3 .github/workflow/validators/check-plan .github/examples/tasks/TASK-001/plan.json
python3 .github/workflow/validators/check-execution .github/examples/tasks/TASK-001/execution.json
python3 .github/workflow/validators/check-verification .github/examples/tasks/TASK-001/verification.json .github/examples/tasks/TASK-001/review.json
python3 .github/workflow/validators/check-state
python3 .github/workflow/validators/check-memory
python3 .github/workflow/validators/check-state .github/examples/state/good-full-lifecycle/state.json .github/examples/tasks
python3 .github/workflow/validators/check-graph .github/workflow/graph-record.json
python3 .github/workflow/validators/check-graphify-copilot --repo-root .github/examples/graphify-copilot/good-repo --home .github/examples/graphify-copilot/good-home --graphify-bin .github/examples/graphify-copilot/fake-bin/graphify
python3 .github/workflow/validators/check-plan .github/examples/graph/fresh.plan.json
python3 .github/workflow/validators/check-graph .github/examples/graph/fresh.graph-record.json .github/examples/graph/fresh.plan.json
python3 .github/workflow/validators/check-plan .github/examples/graph/degraded.plan.json
python3 .github/workflow/validators/check-graph .github/examples/graph/degraded-approved.graph-record.json .github/examples/graph/degraded.plan.json
python3 .github/workflow/validators/check-plan .github/examples/graph/missing-quick.plan.json
python3 .github/workflow/validators/check-graph .github/examples/graph/missing.graph-record.json .github/examples/graph/missing-quick.plan.json
python3 .github/workflow/validators/check-execution .github/examples/approvals/scope-drift-approved.execution.json
python3 .github/workflow/validators/check-execution .github/examples/approvals/governance-approved.execution.json
python3 .github/workflow/validators/check-execution .github/examples/approvals/memory-approved.execution.json
python3 .github/workflow/validators/check-memory .github/examples/memory/good-notebook
python3 .github/workflow/validators/check-memory .github/examples/evaluations/local-memory

expect_fail() {
  label="$1"
  shift
  if "$@" >/tmp/office-copilot-workflow-negative.out 2>/tmp/office-copilot-workflow-negative.err; then
    echo "release-check: expected failure did not occur: $label" >&2
    exit 1
  fi
}

expect_fail_contains() {
  label="$1"
  expected="$2"
  shift 2
  if "$@" >/tmp/office-copilot-workflow-negative.out 2>/tmp/office-copilot-workflow-negative.err; then
    echo "release-check: expected failure did not occur: $label" >&2
    exit 1
  fi
  if ! grep -q "$expected" /tmp/office-copilot-workflow-negative.err; then
    echo "release-check: expected failure text did not occur: $label" >&2
    cat /tmp/office-copilot-workflow-negative.err >&2
    exit 1
  fi
}

expect_fail "stale graph without degraded approval" \
  python3 .github/workflow/validators/check-plan .github/examples/negative/stale-graph-without-approval.plan.json
expect_fail_contains "missing Graphify command reports fix" "Install Graphify" \
  python3 .github/workflow/validators/check-graphify-copilot --repo-root .github/examples/graphify-copilot/good-repo --home .github/examples/graphify-copilot/good-home --graphify-bin .github/examples/graphify-copilot/missing-bin/graphify
expect_fail_contains "missing Copilot Graphify skill reports fix" "graphify copilot install" \
  python3 .github/workflow/validators/check-graphify-copilot --repo-root .github/examples/graphify-copilot/good-repo --home .github/examples/graphify-copilot/missing-skill-home --graphify-bin .github/examples/graphify-copilot/fake-bin/graphify
expect_fail_contains "missing Graphify output reports fix" "Run: graphify" \
  python3 .github/workflow/validators/check-graphify-copilot --repo-root .github/examples/graphify-copilot/missing-output-repo --home .github/examples/graphify-copilot/good-home --graphify-bin .github/examples/graphify-copilot/fake-bin/graphify
expect_fail "plan missing graph usage declaration" \
  python3 .github/workflow/validators/check-plan .github/examples/negative/missing-graph-usage.plan.json
expect_fail "used graph without refs" \
  python3 .github/workflow/validators/check-plan .github/examples/negative/used-graph-without-refs.plan.json
expect_fail "skipped graph without approval" \
  python3 .github/workflow/validators/check-plan .github/examples/negative/skipped-graph-without-approval.plan.json
expect_fail "quick graph-light task without explicit policy" \
  python3 .github/workflow/validators/check-plan .github/examples/negative/quick-graph-light-without-policy.plan.json
expect_fail "plan missing graph scope" \
  python3 .github/workflow/validators/check-plan .github/examples/negative/missing-graph-scope.plan.json
expect_fail "vague graph scope decision" \
  python3 .github/workflow/validators/check-plan .github/examples/negative/vague-graph-scope.plan.json
expect_fail "nearby graph scope overlaps intended files" \
  python3 .github/workflow/validators/check-plan .github/examples/negative/graph-scope-overlap.plan.json
expect_fail "missing verification command" \
  python3 .github/workflow/validators/check-plan .github/examples/negative/missing-verification-command.plan.json
expect_fail "unapproved quick task" \
  python3 .github/workflow/validators/check-plan .github/examples/negative/unapproved-quick-task.plan.json
expect_fail "out-of-scope modification without approved deviation" \
  python3 .github/workflow/validators/check-execution .github/examples/negative/out-of-scope.execution.json
expect_fail "governance edit without approval" \
  python3 .github/workflow/validators/check-execution .github/examples/negative/governance-without-approval.execution.json
expect_fail "memory write without approval" \
  python3 .github/workflow/validators/check-execution .github/examples/negative/memory-without-approval.execution.json
expect_fail "memory candidate without evidence" \
  python3 .github/workflow/validators/check-memory .github/examples/memory/bad-missing-evidence
expect_fail "accepted memory without approval" \
  python3 .github/workflow/validators/check-memory .github/examples/memory/bad-accepted-without-approval
expect_fail "rejected memory without audit" \
  python3 .github/workflow/validators/check-memory .github/examples/memory/bad-rejected-without-audit
expect_fail "degraded verification without acknowledgement" \
  python3 .github/workflow/validators/check-verification .github/examples/negative/degraded-verification.verification.json .github/examples/negative/degraded-verification.review.json
expect_fail "failed verification cannot be approved vaguely" \
  python3 .github/workflow/validators/check-verification .github/examples/negative/failed-verification-vague-approval.verification.json .github/examples/negative/failed-verification-vague-approval.review.json
expect_fail "graphify cannot be verification proof" \
  python3 .github/workflow/validators/check-verification .github/examples/negative/graph-only-verification.verification.json .github/examples/negative/graph-only-verification.review.json
expect_fail "graph-near scope drift requires approval" \
  python3 .github/workflow/validators/check-verification .github/examples/negative/graph-near-drift-without-approval.verification.json .github/examples/negative/graph-near-drift-without-approval.review.json
expect_fail "graph-unrelated drift must be noted as higher risk" \
  python3 .github/workflow/validators/check-verification .github/examples/negative/graph-unrelated-drift-without-risk-note.verification.json .github/examples/negative/graph-unrelated-drift-without-risk-note.review.json
expect_fail "missing created_at timestamp" \
  python3 .github/workflow/validators/check-plan .github/examples/negative/missing-created-at.plan.json
expect_fail "rejected verification without structured reason" \
  python3 .github/workflow/validators/check-verification .github/examples/negative/rejected-verification-without-reason.verification.json .github/examples/negative/rejected-verification-without-reason.review.json
expect_fail "rejected review without structured reason" \
  python3 .github/workflow/validators/check-verification .github/examples/negative/rejected-review-without-reason.verification.json .github/examples/negative/rejected-review-without-reason.review.json
expect_fail "active task points to missing folder" \
  python3 .github/workflow/validators/check-state .github/examples/state/missing-active-folder/state.json .github/examples/tasks
expect_fail "two active task folders" \
  python3 .github/workflow/validators/check-state .github/examples/state/two-active-tasks/state.json .github/examples/state/two-active-tasks/tasks
expect_fail "execution exists without approved plan" \
  python3 .github/workflow/validators/check-state .github/examples/state/execution-without-approved-plan/state.json .github/examples/state/execution-without-approved-plan/tasks
expect_fail "plan did not set active task" \
  python3 .github/workflow/validators/check-state .github/examples/state/plan-without-active-task/state.json .github/examples/state/plan-without-active-task/tasks
expect_fail "task closeout missing review" \
  python3 .github/workflow/validators/check-state .github/examples/state/close-without-review/state.json .github/examples/state/close-without-review/tasks
expect_fail "stale graph without degraded approval" \
  python3 .github/workflow/validators/check-graph .github/examples/graph/stale.graph-record.json .github/examples/graph/fresh.plan.json
expect_fail "fresh graph record without graph JSON" \
  python3 .github/workflow/validators/check-graph .github/examples/graph/fresh-missing-graph-json.graph-record.json .github/examples/graph/fresh.plan.json
expect_fail "fresh graph record without graph report" \
  python3 .github/workflow/validators/check-graph .github/examples/graph/fresh-missing-report.graph-record.json .github/examples/graph/fresh.plan.json
expect_fail "missing graph for normal task" \
  python3 .github/workflow/validators/check-graph .github/examples/graph/missing.graph-record.json .github/examples/graph/missing-normal.plan.json
expect_fail "graph refs above cap" \
  python3 .github/workflow/validators/check-plan .github/examples/graph/too-many-refs.plan.json
if git rev-parse HEAD >/dev/null 2>&1; then
  expect_fail "stale git commit in fresh graph record" \
    python3 .github/workflow/validators/check-graph .github/examples/graph/stale-commit.graph-record.json
fi

python3 -c 'from pathlib import Path; [path.unlink() for path in Path(".github/examples/hooks").glob("*/.github/tasks/*/logs/events.jsonl")]'
python3 .github/hooks/scripts/log-event.py < .github/examples/hooks/log-event.json | python3 -m json.tool >/dev/null
python3 .github/hooks/scripts/log-event.py < .github/examples/hooks/log-event-secret.json | python3 -m json.tool >/dev/null
python3 .github/hooks/scripts/agent-stop.py < .github/examples/hooks/agent-stop.json | python3 -m json.tool >/dev/null
python3 .github/hooks/scripts/post-tool-use.py < .github/examples/hooks/post-tool-use.json | python3 -m json.tool >/dev/null
session_end_out="$(COPILOT_HOOK_EVENT=sessionEnd python3 .github/hooks/scripts/log-event.py < .github/examples/hooks/session-end.json)"
python3 -c 'import json,sys; data=json.loads(sys.argv[1]); sys.exit(0 if data.get("ok") is True else 1)' "$session_end_out"

forbidden_decision="$(python3 .github/hooks/scripts/pre-tool-use.py < .github/examples/hooks/pre-tool-use-forbidden.json)"
approved_decision="$(python3 .github/hooks/scripts/pre-tool-use.py < .github/examples/hooks/pre-tool-use-approved.json)"
snake_decision="$(python3 .github/hooks/scripts/pre-tool-use.py < .github/examples/hooks/pre-tool-use-snake.json)"
memory_decision="$(python3 .github/hooks/scripts/pre-tool-use.py < .github/examples/hooks/pre-tool-use-memory.json)"
python3 -c 'import json,sys; data=json.loads(sys.argv[1]); sys.exit(0 if data["permissionDecision"] == "deny" and data.get("permissionDecisionReason") and "destructive_shell" in data["riskCategories"] else 1)' "$forbidden_decision"
python3 -c 'import json,sys; data=json.loads(sys.argv[1]); sys.exit(0 if data["permissionDecision"] == "allow" and data["riskCategories"] == [] and "permissionDecisionReason" not in data else 1)' "$approved_decision"
python3 -c 'import json,sys; data=json.loads(sys.argv[1]); sys.exit(0 if data["permissionDecision"] == "deny" and "workflow_governance_edits" in data["riskCategories"] and data["traceWrittenPath"].endswith("_orphans/logs/events.jsonl") else 1)' "$snake_decision"
python3 -c 'import json,sys; data=json.loads(sys.argv[1]); sys.exit(0 if data["permissionDecision"] == "deny" and "memory_writes" in data["riskCategories"] and data["traceWrittenPath"].endswith("_orphans/logs/events.jsonl") else 1)' "$memory_decision"
test -s .github/examples/hooks/active-workspace/.github/tasks/TASK-HOOK/logs/events.jsonl
test -s .github/examples/hooks/orphan-workspace/.github/tasks/_orphans/logs/events.jsonl
python3 -c 'import json,pathlib,sys; lines=pathlib.Path(".github/examples/hooks/active-workspace/.github/tasks/TASK-HOOK/logs/events.jsonl").read_text().splitlines(); events=[json.loads(line) for line in lines if line.strip()]; required={"event_id","task_id","phase","timestamp","event_type","tool_name","target_files","decision","reason","risk","redacted"}; sys.exit(0 if events and all(required <= set(event) and event["task_id"] == "TASK-HOOK" and event["redacted"] is True for event in events) else 1)'
python3 -c 'import json,pathlib,sys; lines=pathlib.Path(".github/examples/hooks/orphan-workspace/.github/tasks/_orphans/logs/events.jsonl").read_text().splitlines(); events=[json.loads(line) for line in lines if line.strip()]; sys.exit(0 if events and any(event["task_id"] is None and event["event_type"] == "governance_file.edit_attempt" for event in events) else 1)'
! grep -R -q "super-secret-fixture-value" .github/examples/hooks/active-workspace/.github/tasks/TASK-HOOK/logs

eval_out="$(python3 .github/workflow/evaluators/evaluate-tasks --tasks-dir .github/examples/evaluations/tasks --memory-dir .github/examples/evaluations/local-memory --output-root .github/evals/runs --run-id EVAL-20260516-0000 --created-at 2026-05-16T00:00:00Z)"
test "$eval_out" = ".github/evals/runs/EVAL-20260516-0000"
test -s .github/evals/runs/EVAL-20260516-0000/summary.json
test -s .github/evals/runs/EVAL-20260516-0000/task-metrics.json
test -s .github/evals/runs/EVAL-20260516-0000/findings.md
python3 -c 'import json,sys,pathlib; summary=json.loads(pathlib.Path(".github/evals/runs/EVAL-20260516-0000/summary.json").read_text()); sys.exit(0 if summary["task_count"] == 6 and summary["missing_event_logs_count"] == 1 and summary["scope_drift_count"] >= 1 and summary["memory_candidates"]["proposed"] == 4 and summary["memory_candidates"]["accepted"] == 1 and summary["verification"].get("failed") == 1 and summary["graph_freshness_modes"].get("stale") == 1 and isinstance(summary["repeated_failure_patterns"], list) else 1)'
python3 -c 'import json,sys,pathlib; metrics=json.loads(pathlib.Path(".github/evals/runs/EVAL-20260516-0000/task-metrics.json").read_text())["tasks"]; findings={task["task_id"]: set(task["findings"]) for task in metrics}; sys.exit(0 if "missing_event_log" in findings["TASK-EVAL-MISSING-LOGS"] and "graph_stale" in findings["TASK-EVAL-STALE-GRAPH"] and "verification_failed" in findings["TASK-EVAL-FAILED-VERIFY"] and "scope_drift" in findings["TASK-EVAL-SCOPE-DRIFT"] and "memory_spam" in findings["TASK-EVAL-MEMORY-SPAM"] else 1)'
! grep -R -i "raw prompt" .github/evals/runs/EVAL-20260516-0000/summary.json .github/evals/runs/EVAL-20260516-0000/task-metrics.json

if find .github -name '*.yaml' -o -name '*.yml' | grep -q .; then
  echo "release-check: required v1 path must not contain YAML" >&2
  exit 1
fi
if grep -R -E '^[[:space:]]*(import yaml|from yaml|import jsonschema|from jsonschema)' .github/workflow/validators; then
  echo "release-check: validators must use only Python standard-library dependencies" >&2
  exit 1
fi
if grep -R -E '^[[:space:]]*(import yaml|from yaml|import jsonschema|from jsonschema)' .github/workflow/evaluators; then
  echo "release-check: evaluators must use only Python standard-library dependencies" >&2
  exit 1
fi

echo "release-check: ok"
