# verification-review

Use this skill for `/verify`.

## Purpose

Prove task results with real checks and review before human acceptance.

## Use When

- ExecutionRecord exists after `/execute`.
- The user asks to verify or review task completion.

## Instructions

- Run or record the approved verification command.
- Create VerificationRecord with `created_at`, command refs, result, and short safe evidence summaries.
- Create ReviewRecord with `created_at` comparing approved files to actual changed files.
- Record graph refs used, but do not use graph data as correctness evidence.
- Treat tests, checks, diff scope, and human review as authoritative.
- Require human approval for final result, scope drift, degraded verification, and remaining assumptions or deviations.
- If verification or review is rejected, record a structured reason with `category` and a specific `details` string.

## Must Not

- Accept degraded verification silently.
- Paste full shell output by default.
- Close a task without review of scope drift.
