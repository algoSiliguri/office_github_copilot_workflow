# Live Task Artifacts

Live task artifacts are written under `.github/tasks/TASK-{NNN}/`.

Required task files:

- `plan.json`
- `execution.json`
- `verification.json`
- `review.json`
- `logs/events.jsonl` local-only and gitignored by default

Committed examples live under `.github/examples/tasks/`.

Do not commit real task logs. Commit only deliberate, redacted examples under
`.github/examples/tasks/`.
