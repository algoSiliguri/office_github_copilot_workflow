# Artifact Examples

These fixtures exercise the shipped v1 governance bundle. They are not runtime task artifacts for active work. They exist so maintainers can validate the bundle against known-good and known-bad examples.

## Layout

- `valid/TASK-001/` contains a complete valid full-workflow artifact chain.
- `valid/TASK-002/context-packet.json` contains a standalone valid context-packet example.
- `invalid/` contains focused failure fixtures for critical gates.

## Recommended checks

```bash
python3 .github/ai-workflow/validators/validate-artifact .github/ai-workflow/artifacts/examples/valid/TASK-001/grill.json
python3 .github/ai-workflow/validators/validate-artifact .github/ai-workflow/artifacts/examples/valid/TASK-001/task-manifest.json
python3 .github/ai-workflow/validators/validate-artifact .github/ai-workflow/artifacts/examples/valid/TASK-001/plan.json
python3 .github/ai-workflow/validators/validate-artifact .github/ai-workflow/artifacts/examples/valid/TASK-001/execution.json
python3 .github/ai-workflow/validators/validate-artifact .github/ai-workflow/artifacts/examples/valid/TASK-001/verification.json
python3 .github/ai-workflow/validators/validate-artifact .github/ai-workflow/artifacts/examples/valid/TASK-001/review.json
python3 .github/ai-workflow/validators/validate-artifact .github/ai-workflow/artifacts/examples/valid/TASK-001/evaluation.json
python3 .github/ai-workflow/validators/validate-artifact .github/ai-workflow/artifacts/examples/valid/TASK-002/context-packet.json
python3 .github/ai-workflow/validators/validate-criteria-coverage .github/ai-workflow/artifacts/examples/valid/TASK-001/verification.json .github/ai-workflow/artifacts/examples/valid/TASK-001/grill.json
python3 .github/ai-workflow/validators/validate-review-gate .github/ai-workflow/artifacts/examples/valid/TASK-001/review.json
python3 .github/ai-workflow/validators/validate-evaluation-gate .github/ai-workflow/artifacts/examples/valid/TASK-001/evaluation.json
python3 .github/ai-workflow/validators/validate-context-packet .github/ai-workflow/artifacts/examples/valid/TASK-002/context-packet.json
```

## Invalid fixture intent

- `invalid/review-scope-violation.json` with `invalid/execution-scope-violation.json`: must fail because out-of-scope files cannot pass review.
- `invalid/verification-criteria-coverage.json` with `invalid/grill-criteria.json`: must fail criteria coverage because the declared criteria and verification outcomes do not match 1:1.
- `invalid/evaluation-confirmed-missing-reviewer.json`: must fail because a confirmed evaluation cannot omit the human reviewer.
