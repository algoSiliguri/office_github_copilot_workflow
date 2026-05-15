#!/usr/bin/env bash
set -euo pipefail

python3 .github/workflow/validators/check-setup
python3 .github/workflow/validators/check-plan .github/examples/tasks/TASK-001/plan.json
python3 .github/workflow/validators/check-execution .github/examples/tasks/TASK-001/execution.json
python3 .github/workflow/validators/check-verification .github/examples/tasks/TASK-001/verification.json .github/examples/tasks/TASK-001/review.json

expect_fail() {
  label="$1"
  shift
  if "$@" >/tmp/office-copilot-workflow-negative.out 2>/tmp/office-copilot-workflow-negative.err; then
    echo "release-check: expected failure did not occur: $label" >&2
    exit 1
  fi
}

expect_fail "stale graph without degraded approval" \
  python3 .github/workflow/validators/check-plan .github/examples/negative/stale-graph-without-approval.plan.json
expect_fail "missing verification command" \
  python3 .github/workflow/validators/check-plan .github/examples/negative/missing-verification-command.plan.json
expect_fail "unapproved quick task" \
  python3 .github/workflow/validators/check-plan .github/examples/negative/unapproved-quick-task.plan.json
expect_fail "out-of-scope modification without approved deviation" \
  python3 .github/workflow/validators/check-execution .github/examples/negative/out-of-scope.execution.json
expect_fail "degraded verification without acknowledgement" \
  python3 .github/workflow/validators/check-verification .github/examples/negative/degraded-verification.verification.json .github/examples/negative/degraded-verification.review.json

python3 .github/hooks/scripts/log-event.py < .github/examples/hooks/log-event.json | python3 -m json.tool >/dev/null
python3 .github/hooks/scripts/agent-stop.py < .github/examples/hooks/agent-stop.json | python3 -m json.tool >/dev/null
python3 .github/hooks/scripts/post-tool-use.py < .github/examples/hooks/log-event.json | python3 -m json.tool >/dev/null

forbidden_decision="$(python3 .github/hooks/scripts/pre-tool-use.py < .github/examples/hooks/pre-tool-use-forbidden.json)"
approved_decision="$(python3 .github/hooks/scripts/pre-tool-use.py < .github/examples/hooks/pre-tool-use-approved.json)"
python3 -c 'import json,sys; data=json.loads(sys.argv[1]); sys.exit(0 if data["decision"] == "deny" and "workflow_governance_edits" in data["risk_categories"] else 1)' "$forbidden_decision"
python3 -c 'import json,sys; data=json.loads(sys.argv[1]); sys.exit(0 if data["decision"] == "allow" and "graph_regeneration" in data["risk_categories"] else 1)' "$approved_decision"

if find .github -name '*.yaml' -o -name '*.yml' | grep -q .; then
  echo "release-check: required v1 path must not contain YAML" >&2
  exit 1
fi
if grep -R -E '^[[:space:]]*(import yaml|from yaml|import jsonschema|from jsonschema)' .github/workflow/validators; then
  echo "release-check: validators must use only Python standard-library dependencies" >&2
  exit 1
fi

echo "release-check: ok"
