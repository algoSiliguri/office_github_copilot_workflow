---
name: debugging
description: Systematic debugging — reproduce, isolate, hypothesise, verify hypothesis, fix, confirm. Use when a test is failing or behaviour is unexpected. Always diagnose before fixing.
---

> **IRON LAW:** No fixes without root cause investigation first. No exceptions.

## Metadata

- **Name:** debugging
- **Description:** Systematic diagnosis before fixing — reproduce → isolate → hypothesise → verify → fix → confirm. Never jump to a solution.
- **Phase:** 7 — Debug (within Execute)
- **Inputs:** Full test failure output including stack trace, or a description of unexpected behaviour
- **Outputs:** Root cause identified + minimal fix applied + failing test now passing + no new regressions

## When To Use

When a test fails or behaviour is unexpected during `/execute-plan` or `/tdd`. Always diagnose before writing any fix. Do not skip to Step 5 without completing Steps 1–4.

## Inputs

- Full test output including stack trace (paste, do not summarise)
- Or: exact steps to reproduce unexpected behaviour

---

You are in debug phase. Diagnose before fixing. Never jump to a solution.

## Step 1: Reproduce

What exact input, action, or test triggers the problem?

- If a test is failing: paste the full test output including the stack trace.
- If behaviour is wrong: describe the exact steps to reproduce it.

Do not proceed to Step 2 until reproduction is confirmed.

## Step 2: Isolate

Which specific file, method, or line is responsible?

Read the stack trace top-to-bottom. The first line in your own code (not framework or library
code) is the suspect.

State: "The failure originates in `[file]` at `[method]` line [N]."

If the stack trace does not point clearly to your code (e.g. the failure is in a framework callback and the root cause is not visible), use the **Codebase Search Protocol** to locate the relevant code:

## Codebase Search Protocol (use only when stack trace is insufficient)

1. **Formulate a specific query**: name the class, method, or behavior you're trying to find. Bad: "find where it breaks". Good: "OrderProcessor.processPayment method".
2. **Run `semantic_search`** with the specific query.
3. **If a relevant result appears**: read it and use it to complete Step 2 (the isolation statement).
4. **If zero results or irrelevant**: try once more with the exact method or class name.
5. **Fallback after 2 failed searches**: use `grep_search` with an exact string from the stack trace.
6. **Stop when isolated**: once you can state "The failure originates in [file] at [method] line [N]", return to Step 3.

## Step 3: Hypothesise

State one specific hypothesis: "I think this fails because [specific reason]."

One hypothesis only — the most likely one. Do not list alternatives yet.

## Step 4: Verify the Hypothesis

Before writing any fix: how can you confirm the hypothesis is correct?

Options: read the code carefully, add a log statement, write a targeted assertion,
inspect a variable value.

Perform the verification. State: "Hypothesis confirmed / not confirmed."

If not confirmed: return to Step 3 with a new hypothesis.

## Escalation

Track hypothesis count silently during this debugging session.

- **< 3 hypotheses tested:** Return to Step 3 with a new hypothesis.
- **>= 3 hypotheses tested:** STOP. Do not attempt a 4th hypothesis without engineer input.

Present to the engineer:

> **Escalation — 3 hypotheses exhausted**
>
> **Ruled out:**
> 1. [Hypothesis 1] — [why it was ruled out]
> 2. [Hypothesis 2] — [why it was ruled out]
> 3. [Hypothesis 3] — [why it was ruled out]
>
> **Current suspicion:** [what the evidence points to]
>
> This may be an architectural issue, not a local bug.
>
> How would you like to proceed?

Wait for engineer input before continuing.

## Step 5: Fix

**REQUIRED:** Write a failing test that reproduces the bug BEFORE implementing the fix. Follow `.github/skills/tdd/SKILL.md` RED phase for this test.

Apply the minimal change that addresses the root cause.

Do not fix unrelated issues. Do not refactor while fixing.

## Step 6: Confirm

Run the failing test. Expected: PASS.
Run the full test suite. Expected: no new failures.

---

## Output Format

- Reproduction confirmed (pasted failure output)
- Isolation statement: file + method + line
- Hypothesis: one specific statement
- Hypothesis verification: confirmed or not confirmed
- Fix: minimal code change
- Confirmation: failing test PASS + full suite green

## Dependencies

- `.github/skills/conventions/SKILL.md` — for test command

## Handoff

Return to `/execute-plan` after confirming the fix.

If the bug requires a non-trivial fix not covered by the current plan: Next: `/write-plan` in a new chat.

Apply context hygiene before closing this chat.
