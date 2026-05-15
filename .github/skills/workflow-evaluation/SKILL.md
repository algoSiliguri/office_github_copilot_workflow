---
name: workflow-evaluation
description: Use only when a maintainer explicitly invokes /evaluate to assess completed workflow artifacts.
---

# workflow-evaluation

Use this skill only for maintainer `/evaluate`.

## Purpose

Evaluate workflow failures and improvement candidates from structured artifacts and redacted event summaries.

## Use When

- A maintainer explicitly invokes `/evaluate`.
- Completed task artifacts exist.

## Instructions

- Read GraphRecord, PlanRecord, ExecutionRecord, VerificationRecord, ReviewRecord, and redacted event summaries before raw session data.
- Produce evaluation reports outside the normal task artifact path.
- Produce improvement candidates with evidence refs, proposed governance-file changes, risk, rollback, and required maintainer approval.
- Keep evaluation outside the normal task path.
- Require maintainer approval before changing instructions, skills, hooks, schemas, validators, policies, command definitions, or other governance files.

## Must Not

- Self-modify instructions, skills, hooks, schemas, validators, policies, or command definitions.
- Approve its own recommendations.
- Depend on raw transcripts by default.
