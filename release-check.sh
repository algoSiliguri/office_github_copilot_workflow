#!/usr/bin/env bash
set -euo pipefail

python3 .github/workflow/validators/check-setup
python3 .github/workflow/validators/check-plan .github/examples/tasks/TASK-001/plan.json
python3 .github/workflow/validators/check-execution .github/examples/tasks/TASK-001/execution.json
python3 .github/workflow/validators/check-verification .github/examples/tasks/TASK-001/verification.json .github/examples/tasks/TASK-001/review.json

echo "release-check: ok"
