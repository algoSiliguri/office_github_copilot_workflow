# Workflow Guide: GitHub Copilot Superpowers

updated: 2026-04-17

A structured development workflow for IntelliJ + GitHub Copilot. Skills are the single source of truth — improve a skill and every phase using it improves automatically.

**To adapt to a new repo:** copy `.github/` in full, then edit only `skills/conventions/SKILL.md`.

---

## Quick Reference

| Phase | When | Prompt | Output |
|---|---|---|---|
| Setup | First time in a repo | `/setup` | Populated `conventions/SKILL.md` |
| Brainstorm | Starting a ticket | `/brainstorm` | Aligned problem + success criteria |
| Spec | After brainstorm | `/write-spec [brainstorm-path]` | Spec file |
| Plan | After spec approved | `/write-plan [spec-path]` | Phased plan file |
| Execute | After plan approved | `/execute-plan [plan-path]` | Committed code, phase by phase |
| TDD | Inside execute, new logic | `/tdd` | Red → green cycle |
| Debug | Inside execute, failing test | `/debug` | Root cause identified and fixed |
| Verify | After all phases done | `/verify [spec-path]` | Verification file with pasted test output |
| Review | After verification | `/review [verification-path]` | BLOCKER / SUGGESTION list |
| Quick Task | Bugfix / config change | `/quick-task` | Plan file, skipping brainstorm + spec |

---

## Setup (one-time per repo)

### Folder Structure

```
.github/
├── copilot-instructions.md     # Global constraints only (hard rules, priority order)
├── WORKFLOW.md                 # This guide
├── ARCHITECTURE.md             # System design reference — how the mechanics work
├── agents/
│   ├── design.agent.md         # Phases 2–4: Brainstorm, Spec, Plan
│   ├── implementation.agent.md # Phases 5–7, 10: Execute, TDD, Debug, Quick Task
│   └── review.agent.md         # Phases 8–9: Verify, Review
├── prompts/
│   └── [skill].prompt.md       # One per phase — invoked with /[skill]
└── skills/
    ├── conventions/SKILL.md    # ← ONLY file you edit when copying to a new repo
    └── [phase]/SKILL.md        # One skill per phase — single source of truth
```

### Steps

1. Copy the `.github/` folder to the root of your repo.
2. Open Copilot Chat. Type `/setup`.
   The Design Agent reads your repo and writes `skills/conventions/SKILL.md` automatically.
3. Review the generated file and correct anything wrong — especially ticket format and commit style.
4. In IntelliJ: Settings → Tools → GitHub Copilot → enable Agent Mode, Custom Agents, Subagents, and Skills.

---

## Session Hygiene

**Start a new chat at every phase boundary.** Each phase builds its prompt context from scratch — starting fresh avoids stale assumptions from the previous phase and keeps each session lean. The handoff message at the end of each skill tells you when and how to start the next chat. Follow it.

---

## Phase Sequence

The standard path: Setup → Brainstorm → Spec → Plan → Execute → Verify → Review.

**When skipping is legitimate:**
- Skip Brainstorm + Spec for a trivial bugfix or config change → use `/quick-task` instead.
- Skip Brainstorm for a well-understood change where requirements are already clear → go directly to `/write-spec` with a written summary.
- Never skip silently. State explicitly what you're skipping and why.

**Hard rules that cannot be skipped:**
- No "done" without running tests — always paste actual output.
- No PR without a verification file.

---

## End-to-End Example: "Add rate limiting to the login endpoint"

Ticket: `AUTH-456`

**Brainstorm:** `/brainstorm` → Design Agent opens: "I see your login endpoint in `LoginController.java`. What's driving this ticket?" You answer. Agent asks one question at a time — thresholds, per-IP vs per-user, Redis availability. Convergence: saves brainstorm artifact, shows aligned summary.

**Spec:** `/write-spec [brainstorm-path]` → spec file created at `docs/specs/2026-04-03-AUTH-456-login-rate-limiting.md`. Review it. Approve.

**Plan:** `/write-plan [spec-path]` → plan file created. 9 files across 3 phases. Annotated `Execution mode: phased-inline — 9 files, auth module flagged active`. Review phase boundaries. Approve.

**Execute:** `/execute-plan [plan-path]` → agent announces phased-inline mode. Phase 1 runs (Redis config + RateLimiterRepository). When done:

```
Phase 1 complete — Redis infrastructure

Files changed:
  + src/config/RedisConfig.java (created)
  + src/ratelimit/RateLimitRepository.java (created)
  + tests/ratelimit/RateLimitRepositoryTest.java (created)

[Stage 1] Spec compliance: PASS
[Stage 2] Code quality: PASS

Test output:
[BUILD SUCCESS]
Tests run: 3, Failures: 0, Errors: 0

Review:
- Does RedisConfig use the connection pool settings from application.properties?
- Does RateLimitRepository degrade gracefully when Redis is unavailable (returns false, not throws)?

Type `continue` for Phase 2, or describe a concern.
```

You check the diff, type `continue`. Phases 2 and 3 follow the same pattern.

**Verify:** `/verify [spec-path]` → maps each requirement to a test, runs them, pastes output, creates verification file.

**Review:** `/review [verification-path]` → checks spec coverage, test evidence, quality, security, deviations. No blockers → "Raise your PR."

---

## Cheat Sheet: Common Situations

**"I'm starting in a new repo"**
→ Run `/setup` first. Then `/brainstorm` for your first feature.

**"I have a simple bugfix or config change"**
→ Use `/quick-task`. Goes directly to `/write-plan`, skipping brainstorm and spec.

**"I have a new feature to build"**
→ Start with `/brainstorm`. Don't skip to `/write-plan` — the brainstorm shapes the spec.

**"I have a bug to fix"**
→ `/debug` first. Once you have a root cause, `/write-plan` for the fix, then `/execute-plan`.

**"My test is failing mid-execution"**
→ Don't push through. Use `/debug`. Return with `retry phase [N]` once fixed.

**"I got review comments on my PR"**
→ For each comment that changes code: create a mini-plan. Run `/execute-plan`. Run `/verify` again before updating the PR.

**"The plan has a step that's clearly wrong"**
→ Tell the Implementation Agent: "This isn't right — [reason]." Update the plan file first, then continue.

**"I'm in a different IDE / Copilot environment"**
→ Sub-agents may not be available. Run `/execute-plan` once per phase, telling the agent which phase to start from. Commit after each. Checkpoints still happen — manually.
