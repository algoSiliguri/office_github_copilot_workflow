---
name: review
description: Critical peer review of code and evidence before raising a PR. Reads spec, verification file, and all changed files with fresh eyes. Flags BLOCKERs and SUGGESTIONs. Use after the verification file is complete.
allowed-tools: read_file, list_dir, file_search, grep_search, semantic_search, get_errors, run_in_terminal, get_terminal_output, validate_cves
---

## Metadata

- **Name:** review
- **Description:** Critical peer review with fresh eyes — checks spec coverage, test evidence, test quality, security, and spec deviations. Produces BLOCKERs and SUGGESTIONs.
- **Phase:** 9 — Review
- **Inputs:** Verification file path + list of changed files (`git diff --name-only main`)
- **Outputs:** A BLOCKER/SUGGESTION list, or "No blockers. Raise your PR." if clean

## When To Use

After the verification file is complete with pasted test output. This is the final gate before a PR is raised. Never sign off without a verification file containing actual terminal output.

## Inputs

- Verification file path (full path to the verification file from phase 8)
- List of changed files (run `git diff --name-only main` or branch equivalent)

---

You are in review phase. Read everything as if you have never seen this code before.

## Before Reviewing

1. Read the spec.
2. Read the verification file.
3. Read every changed file.
4. Run `validate_cves` on any dependency manifest that was modified
   (package.json, go.mod, pom.xml, requirements.txt, Gemfile, etc.).

## Five Review Areas

### 1. Spec Coverage
For every requirement in the spec: is there code that implements it AND a passing test
that proves it?

Missing coverage = **BLOCKER**

### 2. Verification File
Does a verification file exist for this ticket?
Does it contain actual pasted test output — not just "tests passed"?

Missing or empty verification file = **BLOCKER**

### 3. Test Quality
Are tests testing behaviour (what the code does) or implementation (how it does it)?
Tests that would break when you refactor without changing behaviour = **SUGGESTION**
Missing tests for edge cases listed in the spec = **BLOCKER**

### 4. Security
For any code touching auth, sessions, tokens, user data, or external input:
- Is untrusted input validated before use?
- Are endpoints protected that should be?
- Can a user access data belonging to another user?
- Are tokens, passwords, or sensitive values logged or exposed in responses?

CVE findings from `validate_cves` = **BLOCKER**
Any of the above security issues = **BLOCKER**

### 5. Spec Deviations
Did the implementation differ from what the spec describes?
If yes — is the deviation documented in the spec or plan?

Undocumented deviation = **BLOCKER**

## Rules

- Review with fresh eyes — never assume the implementation is correct because it passed tests
- Label every finding as BLOCKER or SUGGESTION — no other severity levels
- Never edit code; only report findings
- When a BLOCKER is fixed, re-review only the affected area — not the entire diff

---

## Output Format

```
BLOCKERs (must fix before merge):
- [file:line] [description]

SUGGESTIONs (optional improvements):
- [file:line] [description]
```

If there are no blockers, output:

"No blockers. All phases complete. Raise your PR."

Then output the learning debrief:

---
**Ticket debrief — complete before closing:**

1. Did you discover a constraint, behavior, or gotcha not in the spec or plan?
   → If yes: it should already be in `## Discoveries` in the plan file. If not, add it now.
2. Is any part of `conventions/SKILL.md` now out of date?
   → If yes: update it before closing this ticket.
3. Would you structure any phase differently next time?
   → If yes, note it in `conventions/SKILL.md` under `## Notes`.
4. Did the plan accurately predict the implementation complexity?
   → If not, note the discrepancy in `## Discoveries` in the plan file.
5. Check the knowledge index for pattern candidates on modules touched this ticket:
   Read `Knowledge Index:` path from `.github/skills/conventions/SKILL.md`. Read `[knowledge-index-path]/index.md`.
   Filter to rows where Module(s) contains any module touched this ticket AND Status includes `pattern-candidate`.
   If any found: surface each one and offer these options:
   > "Topic `[topic-name]` is a pattern-candidate (recurrence: [N], modules: [list]).
   > Summary: [one sentence from the topic's ## Summary].
   > Options:
   > **A** — Synthesize: I'll write a `## Pattern` section in the topic page now.
   > **B** — Retain as-is: mark `normalization: reviewed-no-change` and revisit later.
   > **C** — Merge with `[other-topic]`: flag for merge on next full `/index knowledge` run.
   > **D** — Split into `[proposed subtopics]`: flag for split on next full `/index knowledge` run.
   > **E** — Defer: revisit after [N] additional tickets."
   Execute the engineer's choice immediately:
   - **A:** Read `[knowledge-index-path]/[topic].md`. Write a `## Pattern` section using this format:
     ```
     ## Pattern
     _Confidence: [high|medium|low]_
     [One-sentence pattern statement describing the root cause and reliable resolution.]
     ```
     Confidence rubric: `high` = same root cause + same module(s) + same resolution pattern + ≥3 tickets; `medium` = same symptom + different resolutions; `low` = weak correlation.
   - **B:** Add to the topic page (after `## Summary`): `_normalization: reviewed-no-change — [YYYY-MM-DD]_`
   - **C:** Add to the topic page (after `## Summary`): `_merge-candidate: [other-topic] — flagged [YYYY-MM-DD], pending full rebuild_`
   - **D:** Add to the topic page (after `## Summary`): `_split-candidate: proposed [A] and [B] — flagged [YYYY-MM-DD], pending full rebuild_`
   - **E:** Add to the topic page (after `## Summary`): `_deferred: revisit after [N] tickets — [YYYY-MM-DD]_`
   If no pattern-candidates are found for touched modules: note "Pattern check: none — [YYYY-MM-DD]" and continue.
6. Run `/index knowledge --incremental` to update the knowledge index with this ticket's discoveries and amendments.
   → This closes the learning loop. The next ticket's retrieval will have this ticket's signals available.

---

## Dependencies

- `.github/skills/conventions/SKILL.md` — for repo context
- Spec file — for requirement coverage check
- Verification file (path provided as input)
- All changed files (list provided as input)

## Handoff

If no blockers: raise your PR.

If blockers found: fix each blocker, then re-invoke `/review` for the affected area only. Do not re-review the entire diff for a single fix.

Apply context hygiene summary, then proceed.
