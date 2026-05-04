# Protocol: Stage Review

**Purpose:** Validate a completed phase for spec compliance (Stage 1) and code quality (Stage 2) before it is presented to the engineer.

**Inputs:**
- Plan listed files — V2: from `phases[N].steps[*].files`; V1: from `**Files in this phase:**` prose section
- Actually changed files — from `git diff --name-status HEAD~1`
- Incidental file patterns — from `conventions/SKILL.md`

**Outputs:**
- Stage 1 result: PASS or FAIL, with plan-listed list, actually-changed list, and (on FAIL) unlisted list
- Stage 2 result: PASS or FAIL, with finding on FAIL (one line: what + where)

**Non-goals:** Does not present the checkpoint (phase-checkpoint protocol responsibility). Does not gate execution (orchestrator responsibility). Does not fix Stage 1 or Stage 2 failures.

**Internal v1/v2:** Stage 1 has isolated `### V2` / `### V1` subsections for plan-listed file resolution. The caller does not need to prepare version-specific inputs — version is read from the plan file's `schema_version` frontmatter within the protocol.

---

## Stage 1: Spec Compliance

### V2 (PLAN_VERSION = 2)

- `plan_listed` = all `files[*].path` values from `phases[*].id=N .steps[*].files` (typed array, no text parsing)
- `actually_changed` = paths in `git diff --name-status HEAD~1` with status `A` (added), `M` (modified), or `R` (renamed). Paths with status `D` (deleted): check these against plan_listed separately — a `D` path not in plan_listed and not covered by a `step-removed` amendment = Stage 1 FAIL.
- Classify each path in `actually_changed`:
  - Present in `plan_listed` → expected
  - Absent from `plan_listed` AND status is NOT `D` AND path matches a pattern in `conventions/SKILL.md: Incidental file patterns` AND path is not in any StepNode across any phase → `incidental` (logged in checkpoint under `Incidental files:`, NOT a failure)
  - Absent from `plan_listed` AND does not meet all incidental conditions → `unlisted` → Stage 1 FAIL
- Stage 1 PASS: all `actually_changed` paths are expected or incidental.

### V1 (PLAN_VERSION = 1)

Compile two lists: **Plan listed** — all files from this phase's `**Files in this phase:**` section in the plan; **Actually changed** — all files modified during this phase's steps.

Stage 1 PASS: all actually-changed files appear in plan-listed. Any unlisted file = Stage 1 FAIL.

## Stage 2: Code Quality

Stage 2 runs only after Stage 1 passes (same for both V2 and V1). Check:
- Code follows conventions from `.github/skills/conventions/SKILL.md`
- Tests test behaviour, not implementation details
- No obvious issues (missing error handling the spec required, wrong return types, etc.)

Stage 2 result is one line: PASS or FAIL with finding (what + where). No explanation, no suggestion.

**On failure (phased-subagent mode):** send the subagent back to fix. Re-run only Stage 2.
**On failure (phased-inline mode):** stop for engineer review before proceeding.

Stage 1 always shows Plan listed and Actually changed. On PASS, the lists match. On FAIL, include the Unlisted section. Stage 2 remains one line. No explanation, no suggestion in either.
