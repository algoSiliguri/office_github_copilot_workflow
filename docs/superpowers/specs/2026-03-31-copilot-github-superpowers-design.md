# Design Spec: Replicating Superpowers Workflow via `.github/` for GitHub Copilot (IntelliJ)

**Date:** 2026-03-31
**Context:** AIB microservices (Java/Spring Boot, 10+ repos). IntelliJ IDE with GitHub Copilot plugin (no additional plugins or MCP servers can be installed). Jira for tracking, Bitbucket for code.

---

## 1. Problem Statement

The Superpowers plugin for Claude Code provides structured workflow enforcement (brainstorm → spec → plan → execute → verify), individual skill prompts, agent specialization, and hard gates that prevent skipping phases. This system needs to be replicated using only the `.github/` folder components natively supported by GitHub Copilot's IntelliJ plugin — no MCP servers, no additional plugins.

**Goal:** A portable `.github/` folder that can be copied to any AIB repo and immediately provides Superpowers-equivalent workflow discipline through Copilot Chat.

---

## 2. Architecture

### Mapping: Superpowers → `.github/`

| Superpowers Component | `.github/` Equivalent |
|---|---|
| `using-superpowers` base skill | `copilot-instructions.md` |
| Individual skills | `.github/prompts/*.prompt.md` |
| Agent specialization | `.github/agents/*.md` |
| Skill reference docs | `.github/skills/*.md` |
| Setup guide | `.github/instructions/getting-started.md` |

### Folder Structure

```
.github/
├── copilot-instructions.md          ← always-on spine
├── prompts/
│   ├── brainstorm.prompt.md         ← /brainstorm
│   ├── write-spec.prompt.md         ← /write-spec
│   ├── write-plan.prompt.md         ← /write-plan
│   ├── execute-plan.prompt.md       ← /execute-plan
│   ├── debug.prompt.md              ← /debug
│   ├── verify.prompt.md             ← /verify
│   └── review.prompt.md             ← /review
├── agents/
│   ├── design.md                    ← design-mode persona
│   ├── implementation.md            ← coding-mode persona
│   └── review.md                    ← review-mode persona
├── skills/
│   ├── workflow.md                  ← full cycle reference
│   └── aib-conventions.md          ← AIB/Jira/Spring Boot context
└── instructions/
    └── getting-started.md           ← day-to-day usage guide
```

**Key principle:** 3 agents represent modes of thinking (design, build, review), not individual phases. 7 prompts represent individual skill invocations. Skills are reference docs that keep guidance DRY.

---

## 3. Component Specifications

### 3.1 `copilot-instructions.md` — The Spine

Always loaded into every Copilot interaction. Replaces the `using-superpowers` base skill.

**Contents:**
- **Workflow declaration:** 5-phase cycle (brainstorm → spec → plan → execute → verify) with hard rule: never write implementation code without a plan file existing for the Jira ticket
- **Phase gate:** Copilot asks "which phase are you in?" at the start of every new conversation and surfaces the right prompt/agent
- **AIB context:** Branch naming (`AIB-1234-description`), Jira ticket format, Bitbucket PR conventions, Java/Spring Boot stack
- **Agent routing table:** design phase → design agent, coding phase → implementation agent, PR/post-code → review agent
- **Hard rules:**
  - Don't generate code before spec and plan exist
  - Don't claim work is done without running tests
  - Don't skip verification even for small fixes
  - Always link changes back to Jira ticket
- **Escape hatch:** "If you need to skip a phase, say so explicitly and I'll note it" — conscious override, not accidental skip

**Target length:** ~50-80 lines. Short and scannable. Detailed guidance lives in prompts and skills.

---

### 3.2 Prompts (`.github/prompts/`)

Each is a `.prompt.md` file invoked as a slash command in Copilot Chat. Each ends with an explicit "next step" pointer to the following prompt.

#### `/brainstorm` (`brainstorm.prompt.md`)
- Mirrors Superpowers `brainstorming` skill
- Asks one question at a time to explore: problem, constraints, success criteria, edge cases
- Refuses to move to spec until 4 key questions are answered
- Output: structured answers ready to feed into `/write-spec`
- Next step: `/write-spec`

#### `/write-spec` (`write-spec.prompt.md`)
- Takes brainstorm output + Jira ticket context
- Guides writing spec file to `docs/workflow/specs/YYYY-MM-DD-AIB-XXXX-name.md`
- Sections: problem statement, solution approach, requirements (testable), architecture, risks, testing strategy
- Next step: `/write-plan`

#### `/write-plan` (`write-plan.prompt.md`)
- Takes spec file as input
- Produces step-by-step implementation plan to `docs/workflow/plans/YYYY-MM-DD-AIB-XXXX-name.md`
- Forces file-level specificity (not "add JWT" but "edit `AuthService.java:45`")
- Includes: numbered steps, testing checklist, rollback plan
- Next step: `/execute-plan`

#### `/execute-plan` (`execute-plan.prompt.md`)
- Reads plan file before writing any code
- Works through steps one at a time
- After each step: run tests, confirm green before proceeding
- Flags deviations from plan explicitly and asks before proceeding
- Next step: `/verify`

#### `/debug` (`debug.prompt.md`)
- Invoked when something breaks during execution
- Forces diagnosis before fix: reproduce → isolate → hypothesize → verify hypothesis → fix → confirm fix didn't break anything else
- Never jumps to solution before root cause is identified
- Next step: return to `/execute-plan`

#### `/verify` (`verify.prompt.md`)
- Maps every spec requirement to a test
- Produces verification file at `docs/workflow/verifications/YYYY-MM-DD-AIB-XXXX-name.md`
- Requires actual test output pasted in (not "tests passed")
- Hard stop if any requirement has no test coverage
- Next step: `/review`

#### `/review` (`review.prompt.md`)
- Reviews diff against spec requirements (not just code style)
- Flags: missing tests, spec deviations, security issues (OWASP top 10 for auth/data handling code), undocumented design decisions
- Won't sign off until verification file exists
- Output: PR ready or list of blockers to resolve

---

### 3.3 Agents (`.github/agents/`)

3 agents, each representing a mode of thinking. Switched manually in Copilot Chat plugin menu.

#### `design.md` — Design Agent
- **Persona:** Senior architect who refuses to write code. Asks probing questions, challenges assumptions, proposes 2-3 approaches with trade-offs before committing.
- **Invoked during:** brainstorm, spec writing, plan writing
- **Hard constraints:**
  - Never writes implementation code
  - Always asks "why" before "what"
  - Challenges requirements that are vague or untestable
  - Explicitly flags risks and dependencies
- **Tool access:** Read files, search codebase (understand existing patterns before designing)

#### `implementation.md` — Implementation Agent
- **Persona:** Disciplined engineer who follows the plan exactly. No scope creep, no refactoring tangents, no "while I'm here" changes.
- **Invoked during:** execute-plan, debug
- **Hard constraints:**
  - Reads plan file before writing any code
  - Asks "is this in the plan?" before doing anything extra
  - Runs tests after each step, not at the end
  - Flags plan deviations explicitly before proceeding
- **Tool access:** Read/edit files, run terminal commands (`mvn test`, `mvn verify`)

#### `review.md` — Review Agent
- **Persona:** Critical peer reviewer who hasn't seen this code before. Reads with fresh eyes, questions everything.
- **Invoked during:** verify, pre-PR review
- **Hard constraints:**
  - Reviews against spec requirements, not just code quality
  - Flags missing tests as blockers, not suggestions
  - Checks OWASP top 10 for any auth/data handling code
  - Won't sign off until verification file exists
- **Tool access:** Read files only (reviewer flags, doesn't fix)

---

### 3.4 Skills (`.github/skills/`)

Reference docs that keep guidance DRY. Agents and prompts point here rather than duplicating content.

#### `workflow.md`
Full cycle reference table:

| Phase | Input needed | Output produced | Done when |
|---|---|---|---|
| Brainstorm | Jira ticket | 4 answered questions | All questions answered |
| Spec | Brainstorm answers | `docs/workflow/specs/...` | Design agent approves |
| Plan | Spec file | `docs/workflow/plans/...` | Step-by-step, file-level |
| Execute | Plan file | Working code + tests | All plan steps done |
| Verify | Spec + test output | `docs/workflow/verifications/...` | All requirements proven |
| Review | Verify file + diff | PR ready | Review agent signs off |

Also contains: when skipping a phase is acceptable and how to document the skip consciously.

#### `aib-conventions.md`
AIB-specific context referenced by all agents and prompts:
- Branch naming: `AIB-1234-short-description`
- Jira ID format: `[A-Z]+-[0-9]+` (uppercase)
- Artifact paths: `docs/workflow/{specs,plans,verifications}/YYYY-MM-DD-AIB-XXXX-name.md`
- Stack defaults: Java/Spring Boot, `mvn test`, `mvn verify`
- Bitbucket PR: link Jira ticket in PR description
- Commit message format: `AIB-1234: short description`

---

### 3.5 Usage Guide (`.github/instructions/getting-started.md`)

Practical day-to-day guide for using the system in the Copilot Chat window.

#### Part 1: One-time setup (5 minutes)
- Where to find Copilot Chat in IntelliJ
- How to switch agents (plugin menu location)
- How to invoke prompts (`/brainstorm` syntax in Chat input)
- How to verify `copilot-instructions.md` is active

#### Part 2: Daily workflow — new Jira story (step by step)
```
1.  Create branch:             git checkout -b AIB-1234-short-description
2.  Open Copilot Chat          Switch to Design Agent
3.  Run:                       /brainstorm  → answer questions
4.  Run:                       /write-spec  → review + save spec file
5.  Run:                       /write-plan  → review + save plan file
6.  Switch to:                 Implementation Agent
7.  Run:                       /execute-plan → work through steps one by one
8.  If something breaks:       /debug
9.  Switch to:                 Review Agent
10. Run:                       /verify → paste test output when asked
11. Run:                       /review → address any flagged blockers
12. Push + create Bitbucket PR linked to AIB-1234
```

#### Part 3: Common scenarios
- **Bug fix:** Same cycle, lighter `/brainstorm` (focus on reproducing bug, not requirements), same spec/plan/verify discipline
- **Small change:** `/brainstorm` can be skipped consciously — document why in the plan file header
- **Picking up someone else's code:** Start with `/review` to understand it before changing anything

#### Part 4: Troubleshooting
- "Copilot ignored my instructions" → Re-state current phase explicitly, re-invoke the prompt
- "Prompt not showing in slash commands" → Verify file extension is `.prompt.md`, not `.md`
- "Agent not behaving differently" → Verify agent file format matches Copilot plugin spec
- "Feels heavy for a small fix" → Use `--no-verify` equivalent: skip consciously and document why

---

## 4. Design Principles

| Principle | How it's applied |
|---|---|
| **No hard gates (compensated)** | `copilot-instructions.md` instructs Copilot to ask phase upfront; prompts chain with explicit "next step" |
| **DRY guidance** | AIB context and workflow reference live in `skills/`, not repeated in every prompt |
| **Portable** | Copy entire `.github/` to any AIB repo, works immediately |
| **Gradual adoption** | Existing repos: add `.github/`, start following workflow on new branches only |
| **Conscious skips** | Override is always available but requires explicit statement — mirrors `--no-verify` philosophy |
| **Language-agnostic** | `aib-conventions.md` holds Java/Spring Boot specifics; rest of system is stack-neutral |

---

## 5. Limitations vs Superpowers

| Superpowers capability | Status in this system |
|---|---|
| Hard gates (can't skip phases) | Not enforceable — relies on discipline + `copilot-instructions.md` prompting |
| Automatic task tracking | Not available — manual |
| Automatic tool invocation between skills | Not available — manual prompt invocation |
| Skill chaining (auto-transitions) | Partially replicated via "next step" pointers in each prompt |
| Always-on context | Replicated via `copilot-instructions.md` |

---

## 6. Rollout Strategy

### Phase 1: Single pilot repo
1. Create `.github/` folder with all files in one repo
2. Run through one real AIB story end-to-end
3. Refine prompts/agents based on actual Copilot behavior

### Phase 2: All repos
1. Copy `.github/` folder to remaining 9+ repos
2. No other setup required — works immediately on copy

### Phase 3: Ongoing refinement
1. Update prompts when Copilot misses intent
2. Add repo-specific customizations to `aib-conventions.md` as needed

---

## 7. Success Criteria

- `/brainstorm` through `/review` produces consistent, disciplined workflow in Copilot Chat
- Spec and plan files exist for every Jira ticket worked
- Agents behave noticeably differently (design agent refuses to write code; implementation agent asks about the plan)
- Any new AIB repo can adopt the system by copying `.github/` with zero additional setup
- Usage guide enables someone to follow the workflow on day one without asking questions
