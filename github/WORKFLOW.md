# Workflow Guide

updated: 2026-04-17

A structured development workflow for AI-assisted coding. Skills are the single source of truth — improve a skill and every phase using it improves automatically.

**To adapt to a new repo:** copy `.github/` in full, then edit only `skills/conventions/SKILL.md`.

---

## Quick Start

1. Copy `.github/` to your repo root.
2. Run `/setup` — the agent auto-detects your tech stack and writes `conventions/SKILL.md`.
3. Review and correct `conventions/SKILL.md` (especially ticket format and commit style).
4. Start your first feature with `/brainstorm`.

Every phase after this reads `conventions/SKILL.md` for all repo-specific values.

---

## Phase Overview

| Phase | Command | When | Output |
|---|---|---|---|
| Setup | `/setup` | Once per repo | Populated `conventions/SKILL.md` |
| Brainstorm | `/brainstorm` | Starting a ticket | Aligned problem + success criteria |
| Spec | `/write-spec [brainstorm-path]` | After brainstorm | Spec file |
| Plan | `/write-plan [spec-path]` | After spec approved | Phased plan file |
| Context Packet | `/context-packet [ticket] [phase-N]` | Optional, before execution | Pre-assembled phase context |
| Execute | `/execute-plan [plan-path]` | After plan approved | Committed code, phase by phase |
| TDD | `/tdd` | Inside execute, new logic | Red → green cycle |
| Debug | `/debug` | Inside execute, failing test | Root cause identified and fixed |
| Verify | `/verify [spec-path]` | After all phases done | Verification file with pasted test output |
| Review | `/review [verification-path]` | After verification | BLOCKER / SUGGESTION list |
| Quick Task | `/quick-task` | Trivial bugfix or config change | Plan, skipping brainstorm + spec |

---

## Session Hygiene

**Start a new chat at every phase boundary.** Each phase builds its context from scratch — starting fresh prevents stale assumptions from accumulating. The handoff note at the end of each phase tells you when and how to proceed.

---

## Artifact Format (V1 vs V2)

New tickets started after all six skills are upgraded produce **v2 artifacts** — structured YAML with typed fields (`schema_version: 2`). In-flight tickets on v1 continue to use the existing Markdown prose format unchanged.

**V1 (current default):** Artifacts are human-readable Markdown sections. Skills extract structure from prose.

**V2 (new tickets after skill upgrade):** Artifacts are YAML documents with four typed primitives — `ProblemRecord`, `DecisionRecord`, `Requirement`, `StepNode`. Each phase inherits upstream fields verbatim and adds its own. Stage 1 compliance is exact. Context packets auto-trigger for qualifying phases.

See `ARCHITECTURE.md § V2 Artifact Model` for mechanics. See `SCHEMA.md` for type definitions once written.

---

## Execution Modes (What You'll See)

The planner sets execution mode when writing the plan. You don't choose it — but you should understand what you're seeing.

**Inline:** All steps run in the current session. Progress markers appear after each file group (if the plan has ≥6 steps). One review checkpoint at the end.

**Phased-inline:** Phases run sequentially in the current session. After each phase completes, you'll see a structured checkpoint: files changed, two-stage review results (spec compliance, then code quality), pasted test output, plan changes made this phase, and review questions from the plan. Type `continue` to proceed, or describe a concern. The agent does not auto-continue.

After you type `continue`, a **context reset block** appears before the next phase starts — a brief summary of completed work, what the next phase should carry forward, and an explicit instruction to discard prior phase details. This keeps context focused as the session grows.

**Phased-subagent:** Same experience as phased-inline — same checkpoints, same gate discipline — but each phase runs in a fresh sub-session. Checkpoints also include a **Decisions & Assumptions** field when the sub-agent made judgment calls, resolved ambiguities, or inferred behavior. Used for large plans where context isolation per phase is needed.

From the engineer's perspective, phased-inline and phased-subagent are nearly indistinguishable at the checkpoint. The only visible difference is the Decisions & Assumptions field, which appears only in phased-subagent mode.

**At the end of execution (all modes):** Before the finishing options, you'll see three reflection blocks:
- **Context Quality Review** — coverage level, any context gaps or misleading assumptions, whether a context packet would have helped
- **Knowledge Candidates** — up to 5 high-signal learnings from the session (new patterns, undocumented constraints, workarounds). Not auto-saved. If ≥3 strong candidates appear, the system will recommend running `/index knowledge --incremental`.
- **Plan stability** — Stable / Minor drift / Major drift — tells you how closely execution tracked the original plan

These are informational. No action required unless you see ≥3 knowledge candidates or want to capture insights before closing the session.

Execution mode affects how context is handled internally — not what you need to do. Your responsibility is to review checkpoints and guide progression.

---

## How Capabilities Are Triggered

Not all system capabilities are invoked manually. Some run automatically inside phases.

### Automatic (no action required)

- Retrieval (during planning)
- Decision conflict checks (during spec-writing and planning)
- TDD and debugging (triggered during execution when needed)

These are built into the workflow and do not require explicit commands.

### Explicit (you invoke these)

| Command | When to use |
|---|---|
| `/setup` | Once per repo |
| `/index codebase` | After setup, or when code structure changes significantly |
| `/index knowledge` | Before a large ticket (full run) |
| `/index knowledge --incremental` | After every ticket closes; when stale warning appears in packet |
| `/context-packet [ticket] [phase-N]` | Before execution on v1 artifacts — phased mode + ≥4 files. Auto-triggered in v2. |
| `/brainstorm`, `/write-spec`, `/write-plan`, `/execute-plan` | Core workflow phases |
| `/verify`, `/review` | After execution completes |
| `/validate-artifact [artifact-path]` | Debug: validate a v2 artifact against schema (runs silently inside each skill) |

### Indexing Affects Retrieval Quality

Indexing is a precondition for retrieval quality — not a side utility.

If your index is missing or stale:
- Planning retrieval will have weaker context
- Context packets will have low coverage confidence, reducing execution discipline

When in doubt, re-run before starting a ticket:

```
/index codebase
/index knowledge --incremental
```

---

## Knowledge Layer

The knowledge layer stores structured signals extracted from your workflow artifacts (plans, specs, reviews). These signals appear in context packets during execution — you don't manage them directly, but you interact with them at three moments.

### Knowledge topic pages

Topic pages live in `[knowledge-index-path]/[topic].md`. Each page has a two-line header that tells you what kind of knowledge it is and whether to trust it:

```
_Type: empirical | Modules: auth-service | Weight: HIGH | Recurrence: 4 | Status: active_
_Validity: valid | Last validated: 2026-04-14_
```

**Type** tells you the nature of the claim: `system` (architectural constraint), `empirical` (observed behavior from tickets), `external` (reference material), `operational` (runtime reality), or `meta` (vault health).

**Validity** tells you its current trustworthiness: `valid`, `stale` (decay trigger met — revalidation needed), `questionable` (conflicting evidence exists), or `superseded` (replaced by a newer topic).

You do not edit these fields directly. `index-knowledge` manages them. You reset validity to `valid` manually after re-validating a claim.

### Signals you will see in context packets

**Stale signal warning** — appears at the top of `## Knowledge Signals` when ≥2 loaded topics are stale:
> ⚠️ N stale signals in scope — run `/index knowledge --incremental` to refresh before relying on this packet.

When you see this, run `/index knowledge --incremental` before executing. If the index is current and topics are genuinely stale (referenced code changed), re-validate the affected constraints and update `Last validated`.

**Conflicting signals section** (`## Conflicting Signals`) — appears when two loaded topics make conflicting assertions about the same parameter or contract. Both sides are shown. You must resolve or explicitly override before proceeding — do not suppress either side.

### When to run `/index knowledge`

- After each ticket closes: `/index knowledge --incremental` (run during the debrief in review)
- Before starting a large ticket: `/index knowledge` (full run) to ensure signals are current
- When you see the stale warning in a context packet: `/index knowledge --incremental`

### Relationships between topics

Topic pages may reference each other:
- `contradicts` and `supersedes` — written automatically by `index-knowledge`
- `supports` and `derived_from` — written manually by engineers when connections are clear

If you notice a meaningful relationship that `index-knowledge` didn't capture, add it to the topic page's `## Relationships` section manually.

---

## When to Skip Phases

Skipping is legitimate. Skipping silently is not.

**Appropriate skips:**
- Trivial bugfix or config change → use `/quick-task` (plan directly, no brainstorm or spec)
- Well-understood change with clear requirements → go directly to `/write-spec` with a written summary
- Bug to investigate first → use `/debug` to find root cause, then `/write-plan` for the fix

**Hard rules that cannot be skipped:**
- No "done" without running tests and pasting the actual output
- No PR without a verification file
- No plan step executed without reading the plan first

---

## End-to-End Example

Ticket: `AUTH-456 — Add rate limiting to the login endpoint`

**Brainstorm** → Agent opens: "Based on the index, `auth` appears to be the primary area — flagged active with recent signals. Does this match your understanding?" You answer. Agent probes one question at a time: thresholds, per-IP vs per-user, Redis availability. Saves brainstorm artifact.

**Spec** → `/write-spec [brainstorm-path]` → spec file created. You review and approve.

**Plan** → `/write-plan [spec-path]` → plan file created. 9 files, 3 phases, annotated: `Execution mode: phased-inline — 9 files, auth module flagged active`. You review and approve.

**Context Packet** → 9 files, phased-inline mode, repo index is up to date. Run `/context-packet AUTH-456 phase-1` before starting execution. This pre-assembles module context and decisions — the executor uses it to stay within scope during each phase. If your index is stale or execution mode is inline, skip this step; execution falls back to live codebase search with low coverage confidence.

**Execute** → `/execute-plan [plan-path]` → agent announces phased-inline mode. Phase 1 runs. Checkpoint:

```
Phase 1 complete — Redis infrastructure

Files changed:
  + src/config/RedisConfig.java (created)
  + src/ratelimit/RateLimitRepository.java (created)
  + tests/ratelimit/RateLimitRepositoryTest.java (created)

[Stage 1] Spec compliance: PASS

Plan listed:
- src/config/RedisConfig.java
- src/ratelimit/RateLimitRepository.java
- tests/ratelimit/RateLimitRepositoryTest.java

Actually changed:
- src/config/RedisConfig.java
- src/ratelimit/RateLimitRepository.java
- tests/ratelimit/RateLimitRepositoryTest.java

[Stage 2] Code quality: PASS

Test output:
[BUILD SUCCESS]
Tests run: 3, Failures: 0, Errors: 0

Plan changes this phase:
- none

Review:
- Does RedisConfig use the connection pool settings from application.properties?
- Does RateLimitRepository degrade gracefully when Redis is unavailable?

Type `continue` for Phase 2, or describe a concern.
```

You check the diff. Type `continue`. A context reset block appears, then Phase 2 begins. Phases 2 and 3 follow the same pattern. This structure is consistent across all phased executions.

**Verify** → `/verify [spec-path]` → maps each requirement to a test, runs them, pastes output, creates verification file.

**Review** → `/review [verification-path]` → checks spec coverage, test evidence, quality, security, deviations. No blockers → "Raise your PR."

---

## Common Situations

**"I'm in a new repo"** → `/setup` first. Then `/brainstorm` for your first feature.

**"Trivial bugfix"** → `/quick-task`. Goes directly to planning.

**"New feature"** → Start with `/brainstorm`. Don't skip to planning — the brainstorm shapes the spec.

**"Bug to investigate"** → `/debug` first. Once you have root cause, `/write-plan` for the fix.

**"Test failing mid-execution"** → Stop. Use `/debug`. Return with `retry phase [N]` when fixed.

**"PR review comments require code changes"** → Write a mini-plan for each affected area. Execute it. Re-run `/verify` before updating the PR.

**"A plan step is clearly wrong"** → Tell the agent: "This step is wrong — [reason]." Update the plan file, then continue.

**"No sub-agents available in my environment"** → The system falls back to `phased-inline` automatically. Same checkpoint behavior, no sub-agents.

---

## File Structure

```
.github/
├── copilot-instructions.md     # Hard rules — read before any session
├── WORKFLOW.md                 # This file
├── ARCHITECTURE.md             # System design reference
├── agents/
│   ├── design.agent.md         # Brainstorm, spec, plan phases
│   ├── implementation.agent.md # Execute, TDD, debug, quick-task phases
│   └── review.agent.md         # Verify, review phases
├── prompts/
│   └── [skill].prompt.md       # One per phase — invoked with /[skill]
└── skills/
    ├── conventions/SKILL.md    # ← Only file you edit per repo
    └── [phase]/SKILL.md        # One skill per phase — source of truth
```

`conventions/SKILL.md` is the only file that changes when copying `.github/` to a new repo. All other skill files are language-agnostic templates.
