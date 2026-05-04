---
name: tdd
description: Guides test-driven development — write failing test first, implement minimally, refactor when green. Use when writing any new production logic or method during the execute phase.
---

> **IRON LAW:** No production code without a failing test first. No exceptions.

## Metadata

- **Name:** tdd
- **Description:** Enforces test-driven development — no production code without a failing test first. Red → Green → Refactor.
- **Phase:** 6 — TDD (within Execute)
- **Inputs:** The behaviour to implement, described in the current plan step
- **Outputs:** A passing test + minimal implementation + clean refactored code, with no regressions
- **Non-goals:** Does not apply to config or infrastructure files without testable behavior; does not write production code before a failing test

## When To Use

Any time a plan step introduces new production logic or a new method. Called from within `/execute-plan` — not as a standalone phase. Also use when fixing a bug: write a test that reproduces the bug first, then fix.

## Inputs

- Description of the behaviour to implement (from the current plan step)
- Test command (from `.github/skills/conventions/SKILL.md`)

---

You are in TDD mode. The Iron Law applies:

**No production code without a failing test first. No exceptions.**

## Step 1: RED — Write the Failing Test

1. Name the test after the behaviour, not the method:
   `should_return_empty_when_no_results` not `test_get_results`
2. Write the test using the class or method you wish existed.
   Do not create the implementation yet.
3. Run: [test command from conventions] for this specific test only.
4. Paste the failure output here. Do not proceed without it.

The failure must say the class or method does not exist, or the assertion fails for the right
reason. If the test passes without any implementation — the test is wrong. Rewrite it.

## Step 2: GREEN — Write the Minimal Implementation

Write the minimum code that makes the test pass. Not elegant code. Not complete code. The minimum.

Run the specific test again. Paste the output — it must show PASS.

If it still fails: diagnose. Use `/debug` if needed. Do not add more code blindly.

## Step 3: REFACTOR — Clean Up While Staying Green

Only now may you improve the code: remove duplication, improve naming, extract methods.

After every refactor change, run the specific test. If it turns red, revert the refactor.
Refactoring must not change behaviour.

## Step 4: Confirm No Regressions

Run the full test suite. It must be green before moving to the next behaviour.

## Rules

- One behaviour at a time. One failing test at a time.
- Never write two failing tests simultaneously.
- Never fix a bug without first writing a test that reproduces it.
- Mocks are for external dependencies only (database, HTTP client, message queue).
  Do not mock your own classes.
- If writing the test feels hard, the design is wrong. Simplify the design, not the test.

---

## Output Format

- RED: failing test with pasted failure output confirming wrong reason
- GREEN: passing test with pasted PASS output
- REFACTOR: clean code; specific test still passing
- CONFIRM: full suite green

## Dependencies

- `.github/skills/conventions/SKILL.md` — for test command

## Handoff

Return to `/execute-plan`

Complete the current plan step, then continue with the next step in the plan.

Apply context hygiene summary, then proceed.
