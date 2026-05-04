---
name: verification
description: Proves every spec requirement is met with actual test evidence before raising a PR. Reads the spec and auto-generates a pre-populated verification document. Use after all plan steps are complete and the full test suite is green.
---

> **IRON LAW:** No sign-off without pasted terminal output as evidence. No exceptions.

## Metadata

- **Name:** verification
- **Description:** Proves every spec requirement is met with actual pasted test evidence — not claims. Generates a verification file that becomes the input for code review.
- **Phase:** 8 — Verify
- **Inputs:** Spec file path — recorded as `source` in the verification frontmatter
- **Outputs:** Verification file at `[verifications-path]/YYYY-MM-DD-[ticket-id]-[feature-name].md`
- **Non-goals:** Does not fix failures; does not write new tests; does not raise a PR

## When To Use

After all plan steps are complete and the full test suite is green. Do not run verification before execution is done. The verification file is required input for `/review` — no PR without it.

## Inputs

- Spec file path (full path to the spec from phase 3)

---

You are in verify phase. Prove every requirement is met — with evidence, not claims.

## Before Generating Anything

1. Read the spec file in full.
2. Extract every requirement, edge case, and constraint — list them.
3. Read `.github/skills/conventions/SKILL.md` for the test command and verifications path.

## Auto-Generate the Verification Skeleton

Create the verification file at:
`[verifications-path]/YYYY-MM-DD-[ticket-id]-[feature-name].md`

Pre-populate it with the actual requirement text copied from the spec:

```markdown
---
ticket: [TICKET-ID]
phase: verify
created: [YYYY-MM-DD]
status: pending
source: [spec-file-path]
---

# Verification: [TICKET-ID] — [Feature Name]

## Requirement Coverage

- [ ] [Exact requirement text copied from spec]
  - Test: `[test file and method name that proves this requirement]`
  - Result: [run the test — paste actual output line here]

- [ ] [Next exact requirement text]
  - Test: `[test file and method name]`
  - Result: [paste actual output]

(repeat for every requirement and edge case in the spec)

## Test Output

### Targeted Tests
[Run each specific test — paste full output]

### Full Suite (No Regressions)
[Run full test suite — paste full output]

### Manual Testing
[For each manual scenario in the spec's Testing Strategy:
  Scenario: [name]
  Steps: [exact steps taken]
  Result: [what you observed]]

## Sign-Off
- All requirements met: [YES / NO — list any NO with reason]
- Tests passing: [YES / NO]
- No regressions: [YES / NO]
- Ready for review: [YES / NO]
```

## Hard Stop

If any requirement has no test — do not sign off. Add the test first, then return here.

"Tests passed" is not evidence. Pasted terminal output is evidence.

---

## Output Format

Verification file containing:
- YAML frontmatter (`ticket`, `phase`, `created`, `status`, `source`)
- Requirement coverage table (each requirement mapped to a test + pasted output)
- Targeted test output (pasted)
- Full suite output (pasted)
- Manual testing results
- Sign-off checklist

## Dependencies

- `.github/skills/conventions/SKILL.md` — for test command and verifications path
- Spec file (path provided as input)

## Handoff

Next: `/review [verification-file-path]` in a new chat.
Note: also provide the list of changed files (`git diff --name-only main`).

Apply context hygiene before closing this chat.
