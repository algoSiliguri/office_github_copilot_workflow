# Protocol: Phase Checkpoint

**Purpose:** The standard output format for presenting a completed phase to the engineer for review.

**Inputs:**
- Phase N, phase name
- Stage 1 result (from stage-review): PASS/FAIL + plan-listed + actually-changed + unlisted (if FAIL)
- Stage 2 result (from stage-review): PASS/FAIL + finding (if FAIL)
- Test output (pasted)
- Plan review prompt text (from the plan's engineer review prompt for this phase)
- Amendments (if any written during this phase)
- Decisions & assumptions (optional — subagent mode only; omit if not provided)

**Outputs:** The formatted checkpoint block, ready to present to the engineer.

**Non-goals:** Does not run Stage 1 or Stage 2 review. Does not run tests. Does not wait for or handle the engineer's response (orchestrator responsibility).

---

Output this block exactly:

```
Phase [N] complete — [Phase name]

Files changed:
  + [file] (created)
  ~ [file] (modified)

[Stage 1] Spec compliance: PASS

Plan listed:
- <file1>
- <file2>

Actually changed:
- <file1>
- <file2>
OR
[Stage 1] Spec compliance: FAIL

Plan listed:
- <file1>

Actually changed:
- <file1>
- <fileX>

Unlisted:
- <fileX>

[Stage 2] Code quality: PASS
OR
[Stage 2] Code quality: FAIL — [finding: what + where]

Test output:
[pasted output]

Plan changes this phase:
- none OR
- [1-line summary of any ## Amendments entry tagged Phase [N] written during this phase]

[Decisions & Assumptions:
[bullets from sub-agent — or "None" if the sub-agent omitted the field]
(present in phased-subagent mode only — omit this block entirely in phased-inline mode)]

Review:
[exact questions from plan's Engineer review prompt for this phase]

Type `continue` for Phase [N+1], or describe a concern.
```

Rules:
- Stage 1 always shows Plan listed and Actually changed. On PASS, the lists match. On FAIL, include the Unlisted section.
- Stage 2 remains one line (PASS or FAIL with finding). No explanation, no suggestion in either.
- The `Decisions & Assumptions:` block is present only when the orchestrator is in phased-subagent mode and the subagent provided the field. Omit entirely in phased-inline mode or when the subagent omitted the field.
