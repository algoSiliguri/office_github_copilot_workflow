# Design Spec: Language-Agnostic Superpowers Workflow for GitHub Copilot in IntelliJ

**Date:** 2026-04-02
**Context:** Personal use across multiple repos in IntelliJ IDEA 2025.3.4 with GitHub Copilot plugin. Implements the core superpowers design principle (skills as single source of truth) using the native GitHub Copilot plugin feature set confirmed available in this environment.

---

## 1. Problem Statement

The current `.github/` folder implements the superpowers workflow cycle but inverts the core design principle: process knowledge lives inside prompt files rather than in skills. This means:

- Improving a process (e.g. brainstorming) requires editing a prompt file, not a skill
- No single source of truth — the same logic is duplicated or scattered
- All content is AIB/Java/Maven specific — not portable across tech stacks
- Brainstorming is a rigid 4-question form, not an intelligent conversation

The goal is a clean, language-agnostic `.github/` folder that correctly implements the superpowers model, copies unchanged to any repo, and requires editing only one file (`conventions/SKILL.md`) to adapt to a new tech stack.

---

## 2. Confirmed Environment

**IDE:** IntelliJ IDEA 2025.3.4
**Plugin:** GitHub Copilot (with agent mode enabled)

**Confirmed supported features (verified via Settings screenshots):**

| Feature | Setting location | Status |
|---|---|---|
| `copilot-instructions.md` | Tools → Copilot → Customizations → Copilot Instructions (Workspace) | ✅ |
| `.github/instructions/*.instructions.md` | Customizations → Instruction Files (Workspace) | ✅ |
| `.github/prompts/*.prompt.md` | Customizations → Prompt Files (Workspace) | ✅ |
| `.github/agents/*.agent.md` | Customizations → Chat Agents (Workspace) | ✅ |
| `.github/skills/<name>/SKILL.md` | Tools → Copilot → Chat → Enable Skills | ✅ |
| Agent mode | Tools → Copilot → Chat → Enable Agent Mode | ✅ |
| Custom agents | Tools → Copilot → Chat → Enable Custom Agent | ✅ |
| Subagents | Tools → Copilot → Chat → Enable Subagent | ✅ |

**Available built-in tools (from Configure Tools dialog):**
`insert_edit_into_file` · `replace_string_in_file` · `create_file` · `apply_patch` ·
`get_terminal_output` · `show_content` · `open_file` · `run_in_terminal` · `get_errors` ·
`list_dir` · `read_file` · `file_search` · `grep_search` · `validate_cves` ·
`run_subagent` · `semantic_search`

---

## 3. Core Design Principle

**Skills are the single source of truth for process knowledge.**

```
copilot-instructions.md   ← routing + hard rules only (no process logic)
skills/<name>/SKILL.md    ← all process knowledge lives here
prompts/*.prompt.md       ← thin entry points: declare phase + point to skill
agents/*.agent.md         ← persona + tool set only (no process logic)
```

When you improve a skill, every agent and prompt that uses it improves automatically. No duplication.

**Layer interaction flow:**
```
User types /brainstorm
  → brainstorm.prompt.md activates
  → declares phase, activates @Design Agent, points to brainstorming/SKILL.md
  → Design Agent persona + brainstorming skill drive the conversation
  → skill reads repo context if present, asks intelligent questions
  → conversation continues until alignment
  → skill outputs summary → user invokes /write-spec next
```

---

## 4. Folder Structure

```
.github/
├── copilot-instructions.md
│
├── skills/
│   ├── brainstorming/
│   │   └── SKILL.md
│   ├── spec-writing/
│   │   └── SKILL.md
│   ├── planning/
│   │   └── SKILL.md
│   ├── execution/
│   │   └── SKILL.md
│   ├── tdd/
│   │   └── SKILL.md
│   ├── debugging/
│   │   └── SKILL.md
│   ├── verification/
│   │   └── SKILL.md
│   ├── review/
│   │   └── SKILL.md
│   └── conventions/
│       └── SKILL.md          ← ONLY file edited when copying to a new repo
│
├── prompts/
│   ├── brainstorm.prompt.md
│   ├── write-spec.prompt.md
│   ├── write-plan.prompt.md
│   ├── execute-plan.prompt.md
│   ├── tdd.prompt.md
│   ├── debug.prompt.md
│   ├── verify.prompt.md
│   └── review.prompt.md
│
└── agents/
    ├── design.agent.md
    ├── implementation.agent.md
    └── review.agent.md
```

**To adapt to a new repo:** copy the entire `.github/` folder, then edit only `skills/conventions/SKILL.md`.

---

## 5. Workflow Cycle

| Phase | Agent | Prompt | Skill |
|---|---|---|---|
| Brainstorm | Design Agent | `/brainstorm` | `brainstorming/` |
| Spec | Design Agent | `/write-spec` | `spec-writing/` |
| Plan | Design Agent | `/write-plan` | `planning/` |
| Execute | Implementation Agent | `/execute-plan` | `execution/` |
| Execute (new code) | Implementation Agent | `/tdd` | `tdd/` |
| Debug | Implementation Agent | `/debug` | `debugging/` |
| Verify | Review Agent | `/verify` | `verification/` |
| Review | Review Agent | `/review` | `review/` |

**Phase transitions:** Each skill ends with a handoff line:
> "Phase complete. Use `/write-spec` next."

---

## 6. Skills Design

### 6.1 Skills Classification

| Dynamic / Conversational | Procedural / Structured |
|---|---|
| `brainstorming` | `spec-writing` |
| `planning` | `execution` |
| `verification` | `tdd` |
| `review` | `debugging` |

Dynamic skills instruct Copilot to read context first and exercise judgment. Procedural skills define a sequence to follow exactly.

---

### 6.2 Brainstorming Skill

**Design:** Senior architect persona. Dynamic, conversational, context-grounded. Not a fixed questionnaire.

**Two modes detected automatically:**

**Existing repo mode:**
1. Read relevant files, entry points, existing patterns using `read_file`, `semantic_search`, `grep_search`
2. Ask questions informed by what was found — never ask what can be read
3. Raise concerns spotted in the code: "I see no auth middleware — is that in scope?"
4. Questions are specific to the actual codebase, not generic

**Greenfield mode (no repo or new feature area):**
1. Start with problem domain: what problem, for whom, why now
2. Explore constraints before solutions
3. Ask about integration points, scale expectations, team context
4. Only discuss technical decisions after the problem is clearly understood

**Architect persona throughout:**
- One intelligent question at a time, building on the previous answer
- Challenges vague answers: "I can't write a test for that — can you be more specific?"
- Proactively surfaces concerns the engineer hasn't raised
- Proposes alternative framings when the first framing seems off
- Drives toward convergence itself — not after N questions but when enough is known

**Convergence:** The architect decides when problem, success criteria, constraints, and key risks are all clear enough to write a spec without assumptions. Ends with:
> "I think I understand enough. Here's what we've aligned on: [summary]. Ready to write the spec?"

---

### 6.3 Planning Skill

**Design:** Dynamic — reads the actual codebase before generating any steps.

1. Read spec file to understand what needs to be built
2. Explore the codebase: find relevant files, understand existing patterns, identify integration points
3. Generate steps that reference **real file paths** found in the codebase, not placeholders
4. Each step is one concrete change: file path + line range + what changes + why
5. Includes testing checklist using the actual test command from `conventions/SKILL.md`
6. Includes rollback plan

A plan step that says `[ClassName].[ext]` is rejected. A plan step that says `src/auth/TokenService.go:45` (or whatever the actual path is) is accepted.

---

### 6.4 Verification Skill

**Design:** Dynamic — reads the spec's actual requirements and auto-generates the verification skeleton.

1. Read spec file
2. Extract every requirement and edge case
3. Auto-generate verification document pre-populated with requirement text
4. For each requirement: identify the test that proves it, run it, paste actual output
5. Never sign off without pasted test output — "tests passed" is not evidence

---

### 6.5 Review Skill

**Design:** Dynamic — fresh eyes, skeptical, evidence-driven.

Persona: a peer reviewer who has never seen this code. Reads with genuine critical eyes, not ticking boxes.

Five review areas:
1. **Spec coverage** — does every requirement have corresponding code and a passing test?
2. **Verification file** — does it exist with actual (not claimed) test output?
3. **Test quality** — are tests testing behaviour or implementation?
4. **Security** — use `validate_cves` for dependency CVEs + manual OWASP top 10 check for auth/data handling code
5. **Spec deviations** — did the implementation differ from the spec? Is it documented?

Each finding labelled: **BLOCKER** (must fix before merge) or **SUGGESTION** (optional).
No blockers → "Ready to merge."

---

### 6.6 Remaining Skills (Procedural)

**Spec-writing:** Template-driven. Problem statement, solution approach, testable requirements, architecture decisions, risks, testing strategy. Each requirement must pass the test: "can I write a failing test for this?"

**Execution:** Hard checklist. Read plan before writing any code. Work steps in order. Run tests after every step. Stop and ask before doing anything not in the plan. Document deviations explicitly.

**TDD:** Iron law — no production code without a failing test first. Red → Green → Refactor → confirm no regressions. One behaviour at a time. Paste failure output before proceeding.

**Debugging:** Reproduce → Isolate → Hypothesise → Verify hypothesis → Fix → Confirm. Never jump to a fix. One hypothesis at a time. Fix the root cause, not the symptom.

---

## 7. Agents Design

### 7.1 Design Agent

```yaml
name: Design Agent
description: Senior architect for exploring problems and designing solutions. Active during brainstorm, spec, and plan phases. Never writes implementation code.
tools:
  - read_file
  - list_dir
  - file_search
  - grep_search
  - semantic_search
  - show_content
```

Persona: challenges vague thinking, proposes 2–3 alternatives before recommending, asks "why" before "what", never writes implementation code or business logic.

---

### 7.2 Implementation Agent

```yaml
name: Implementation Agent
description: Disciplined engineer who implements exactly what the plan says. Active during execute, tdd, and debug phases. Always reads the plan before writing any code.
tools:
  - read_file
  - list_dir
  - file_search
  - grep_search
  - semantic_search
  - insert_edit_into_file
  - replace_string_in_file
  - create_file
  - apply_patch
  - run_in_terminal
  - get_terminal_output
  - get_errors
  - open_file
  - run_subagent
```

`run_subagent` enables delegation of focused subtasks (e.g. running a TDD cycle for a specific method) while maintaining the overall execution flow.

---

### 7.3 Review Agent

```yaml
name: Review Agent
description: Critical peer reviewer who has never seen this code before. Active during verify and review phases. Flags issues, never fixes them. Requires evidence before sign-off.
tools:
  - read_file
  - list_dir
  - file_search
  - grep_search
  - semantic_search
  - show_content
  - get_errors
  - run_in_terminal
  - get_terminal_output
  - validate_cves
```

No edit tools. `validate_cves` supports the security review step. `run_in_terminal` + `get_terminal_output` enable running tests to capture actual evidence for the verification file.

---

## 8. Prompts Design

All prompts follow the same thin pattern — no process logic:

```markdown
---
description: [phase description]
---

You are in **[phase] phase**.
Switch to @[Agent Name].
Read and follow `.github/skills/[skill-name]/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for repo context.
```

The 8 prompts and their skill mappings:

| Prompt file | Agent | Skill |
|---|---|---|
| `brainstorm.prompt.md` | Design Agent | `brainstorming/SKILL.md` |
| `write-spec.prompt.md` | Design Agent | `spec-writing/SKILL.md` |
| `write-plan.prompt.md` | Design Agent | `planning/SKILL.md` |
| `execute-plan.prompt.md` | Implementation Agent | `execution/SKILL.md` |
| `tdd.prompt.md` | Implementation Agent | `tdd/SKILL.md` |
| `debug.prompt.md` | Implementation Agent | `debugging/SKILL.md` |
| `verify.prompt.md` | Review Agent | `verification/SKILL.md` |
| `review.prompt.md` | Review Agent | `review/SKILL.md` |

---

## 9. copilot-instructions.md Design

Loaded on every chat. Routing and hard rules only — no process logic.

**Contents:**
- Ask which phase at the start of every conversation
- Route to correct agent and prompt
- 4 hard rules: no code before plan, no done without passing tests, no skipping verification, always reference ticket ID in commits/PRs
- List of available `/` commands

**What it does NOT contain:** any process detail. That lives in skills.

---

## 10. Conventions Skill

The only file that changes between repos. Language-agnostic template:

```markdown
## Repo Conventions

Ticket format: <e.g. AIB-1234 / PROJ-567 / GH-123>
Branch naming: <e.g. AIB-1234-short-description>

## Artifact Paths (under project root)
Specs:          <e.g. docs/workflow/specs/>
Plans:          <e.g. docs/workflow/plans/>
Verifications:  <e.g. docs/workflow/verifications/>

## Tech Stack
Language:       <e.g. Java / Python / Go / TypeScript>
Framework:      <e.g. Spring Boot / FastAPI / Gin / Next.js>
Test command:   <e.g. mvn test / pytest / go test ./... / npm test>
Build command:  <e.g. mvn package / pip install / go build / npm run build>
Lint command:   <e.g. checkstyle / flake8 / golint / eslint>

## Commit Message Format
<e.g. TICKET-ID: short description in imperative mood>

## PR Convention
<e.g. title format, body requirements, link to ticket>
```

---

## 11. Language-Agnostic Enforcement

No skill, agent, prompt, or instruction file references any specific language, framework, build tool, or ticket system. All specifics live exclusively in `conventions/SKILL.md`.

Skills use neutral language:
- "run your test command" (not `mvn test`)
- "run your build command" (not `mvn package`)
- "the ticket ID" (not `AIB-1234`)
- "the spec file" (not a hardcoded path)

---

## 12. Success Criteria

- [ ] Copy `.github/` to a new repo → only edit `conventions/SKILL.md` → workflow works immediately
- [ ] Improve a skill → all prompts and agents using it improve without editing them
- [ ] Brainstorming feels like talking to a senior architect, not filling a form
- [ ] Planning produces steps with real file paths from the codebase, not placeholders
- [ ] Verification auto-populates from spec requirements
- [ ] Review flags BLOCKERs vs SUGGESTIONs with evidence, not assumptions
- [ ] No language, framework, or tool name appears outside `conventions/SKILL.md`
- [ ] All agent tool lists use only the confirmed available tools from the Configure Tools dialog

---

## 13. What Is Not Included

- No git hooks (enforcement is via discipline + Copilot hard rules, not automated blocking)
- No global `~/.copilot/` setup (Option A: repo-portable chosen over Option B: global)
- No CI/CD integration
- No auto-generation of specs or plans (Copilot assists, engineer decides content)
