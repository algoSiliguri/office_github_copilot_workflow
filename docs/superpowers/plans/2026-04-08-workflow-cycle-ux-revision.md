# Workflow Cycle UX Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix bugs and UX gaps across the Copilot workflow system — Setup agent reassignment, tools syntax, phase visibility, context hygiene, model hints, and multi-source ticket format.

**Architecture:** Surgical Markdown edits across 25 files in `github/`. No skill logic changes. Context Hygiene is defined once in `copilot-instructions.md` and referenced by a one-liner in each skill's Handoff. Model routing stays in WORKFLOW.md as single source of truth; skills get lightweight hints only.

**Tech Stack:** Markdown (GitHub Copilot agent/prompt/skill system). No build, no tests — verification is manual diff review.

**Base path:** All file paths are relative to the project root (`Claude Projects/Office/`).

---

### Task 1: Context Hygiene Rule in copilot-instructions.md

**Files:**
- Modify: `github/copilot-instructions.md`

- [ ] **Step 1: Add Context Hygiene (MANDATORY) section**

Append after the `## Conscious Skip Protocol` section (after the "Never skip silently." line):

```markdown

## Context Hygiene (MANDATORY)

After completing every phase — before any handoff — produce a context hygiene summary:

1. **Summary:** ≤5 bullet points capturing the key decisions and outcomes of this phase
2. **Artifacts:** List every file created or modified during this phase (full paths)
3. **Continuation:** State the next `/command` to use, with any required inputs

This pattern resets context for the next phase. Follow it even when staying in the same chat.
```

- [ ] **Step 2: Verify**

Open `github/copilot-instructions.md`. Confirm:
- The new section appears after Conscious Skip Protocol
- No other content was changed
- The section title is exactly `## Context Hygiene (MANDATORY)`

- [ ] **Step 3: Commit**

```bash
git add github/copilot-instructions.md
git commit -m "feat: add Context Hygiene (MANDATORY) section to copilot-instructions"
```

---

### Task 2: Agent Files — Tools Syntax, Skill Usage Mapping, Setup Reassignment

**Files:**
- Modify: `github/agents/design.agent.md`
- Modify: `github/agents/implementation.agent.md`
- Modify: `github/agents/review.agent.md`

- [ ] **Step 1: Edit design.agent.md — tools syntax**

Replace the frontmatter `tools:` block:

Old:
```yaml
tools:
  - read_file
  - list_dir
  - file_search
  - grep_search
  - semantic_search
  - show_content
```

New:
```yaml
tools: ['read_file', 'list_dir', 'file_search', 'grep_search', 'semantic_search', 'show_content']
```

- [ ] **Step 2: Edit design.agent.md — remove Setup ownership**

Replace the frontmatter `description:` line:

Old:
```yaml
description: Senior architect for exploring problems and designing solutions before any code is written. Use during setup, brainstorm, spec, and plan phases.
```

New:
```yaml
description: Senior architect for exploring problems and designing solutions before any code is written. Use during brainstorm, spec, and plan phases.
```

Replace the Metadata Phases line:

Old:
```
- **Phases:** 1 — Setup, 2 — Brainstorm, 3 — Spec, 4 — Plan
```

New:
```
- **Phases:** 2 — Brainstorm, 3 — Spec, 4 — Plan
```

Replace in Role section:

Old:
```
You are active during setup, brainstorm, spec, and plan phases. You explore the problem, surface risks, and produce artefacts (conventions, brainstorm summaries, specs, plans) that guide implementation.
```

New:
```
You are active during brainstorm, spec, and plan phases. You explore the problem, surface risks, and produce artefacts (brainstorm summaries, specs, plans) that guide implementation.
```

Replace in Responsibilities:

Old:
```
- Produce phase artefacts: populated conventions file, brainstorm summary, spec file, plan file
```

New:
```
- Produce phase artefacts: brainstorm summary, spec file, plan file
```

- [ ] **Step 3: Edit design.agent.md — remove Skill Usage Mapping**

Delete the entire `## Skill Usage Mapping` section (the heading and the table below it):

```markdown
## Skill Usage Mapping

| Phase | Skill | Model Tier | Trigger |
|-------|-------|------------|---------|
| 1 — Setup | `.github/skills/setup/SKILL.md` | Standard | `/setup` or "set up this repo" |
| 2 — Brainstorm | `.github/skills/brainstorming/SKILL.md` | Premium | `/brainstorm` or "let's brainstorm" or "I want to work on" |
| 3 — Spec | `.github/skills/spec-writing/SKILL.md` | Standard | `/write-spec` |
| 4 — Plan | `.github/skills/planning/SKILL.md` | Premium | `/write-plan` |
```

Remove this block entirely. The file should end after the `## Tools` table.

- [ ] **Step 4: Edit implementation.agent.md — tools syntax**

Replace the frontmatter `tools:` block:

Old:
```yaml
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

New:
```yaml
tools: ['read_file', 'list_dir', 'file_search', 'grep_search', 'semantic_search', 'insert_edit_into_file', 'replace_string_in_file', 'create_file', 'apply_patch', 'run_in_terminal', 'get_terminal_output', 'get_errors', 'open_file', 'run_subagent']
```

- [ ] **Step 5: Edit implementation.agent.md — add Setup ownership**

Replace the frontmatter `description:` line:

Old:
```yaml
description: Disciplined engineer who implements exactly what the plan says. Use during execute, TDD, and debug phases. Always reads the plan before writing any code.
```

New:
```yaml
description: Disciplined engineer who implements exactly what the plan says. Use during setup, execute, TDD, and debug phases. Always reads the plan before writing any code.
```

Replace the Metadata Phases line:

Old:
```
- **Phases:** 5 — Execute, 6 — TDD, 7 — Debug, 10 — Quick Task
```

New:
```
- **Phases:** 1 — Setup, 5 — Execute, 6 — TDD, 7 — Debug, 10 — Quick Task
```

Replace in Metadata Description:

Old:
```
- **Description:** Disciplined engineer who implements exactly what the plan says — no improvisation, no scope creep.
```

New:
```
- **Description:** Disciplined engineer who implements exactly what the plan says — no improvisation, no scope creep. Also runs one-time repo setup.
```

Replace in Role section:

Old:
```
You are active during execute, TDD, and debug phases.
```

New:
```
You are active during setup, execute, TDD, and debug phases.
```

- [ ] **Step 6: Edit implementation.agent.md — remove Skill Usage Mapping**

Delete the entire `## Skill Usage Mapping` section:

```markdown
## Skill Usage Mapping

| Phase | Skill | Model Tier | Trigger |
|-------|-------|------------|---------|
| 5 — Execute | `.github/skills/execution/SKILL.md` | Standard | `/execute-plan` |
| 6 — TDD | `.github/skills/tdd/SKILL.md` | Standard | `/tdd` or "write a test for" |
| 7 — Debug | `.github/skills/debugging/SKILL.md` | Premium | `/debug` or "this test is failing" |
| 10 — Quick Task | `.github/skills/execution/SKILL.md` | Standard | `/quick-task` |
```

Remove this block entirely.

- [ ] **Step 7: Edit review.agent.md — tools syntax**

Replace the frontmatter `tools:` block:

Old:
```yaml
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

New:
```yaml
tools: ['read_file', 'list_dir', 'file_search', 'grep_search', 'semantic_search', 'show_content', 'get_errors', 'run_in_terminal', 'get_terminal_output', 'validate_cves']
```

- [ ] **Step 8: Edit review.agent.md — remove Skill Usage Mapping**

Delete the entire `## Skill Usage Mapping` section:

```markdown
## Skill Usage Mapping

| Phase | Skill | Model Tier | Trigger |
|-------|-------|------------|---------|
| 8 — Verify | `.github/skills/verification/SKILL.md` | Standard | `/verify` |
| 9 — Review | `.github/skills/review/SKILL.md` | Premium | `/review` |
```

Remove this block entirely.

- [ ] **Step 9: Verify all 3 agent files**

For each agent file, confirm:
- Frontmatter `tools:` uses inline array syntax `['tool1', 'tool2']`
- No `## Skill Usage Mapping` section exists
- `design.agent.md` does NOT mention Setup in Phases, Role, or description
- `implementation.agent.md` DOES mention Setup in Phases, Role, and description
- No other content was changed

- [ ] **Step 10: Commit**

```bash
git add github/agents/design.agent.md github/agents/implementation.agent.md github/agents/review.agent.md
git commit -m "fix: agent tools syntax, remove Skill Usage Mapping, reassign Setup to Implementation Agent"
```

---

### Task 3: WORKFLOW.md Consistency Updates

**Files:**
- Modify: `github/WORKFLOW.md`

- [ ] **Step 1: Update Quick Reference table — Setup row**

Replace:

Old:
```
| Setup | First time in a repo | @Design Agent | `/setup` | Populated `conventions/SKILL.md` |
```

New:
```
| Setup | First time in a repo | @Implementation Agent | `/setup` | Populated `conventions/SKILL.md` |
```

- [ ] **Step 2: Update folder structure comment — Design Agent phases**

Replace:

Old:
```
│   ├── design.agent.md         # Phases 1–4: Setup, Brainstorm, Spec, Plan
```

New:
```
│   ├── design.agent.md         # Phases 2–4: Brainstorm, Spec, Plan
```

- [ ] **Step 3: Update Model Routing — remove Skill Usage Mapping reference**

Replace the paragraph after the Model Routing table:

Old:
```
Switch models when you start a new chat at each phase boundary. The authoritative model
routing table lives in each agent's **Skill Usage Mapping** section:
- Design Agent (`agents/design.agent.md`) — phases 1–4
- Implementation Agent (`agents/implementation.agent.md`) — phases 5–7, 10
- Review Agent (`agents/review.agent.md`) — phases 8–9
```

New:
```
Switch models when you start a new chat at each phase boundary. This table is the
single source of truth for model routing. Each skill's Handoff section includes a
lightweight model hint that matches this table.
```

- [ ] **Step 4: Update Session Hygiene — add Context Hygiene cross-reference**

At the end of the `## Session Hygiene` section, after the paragraph about cost ("Phases are natural resets — use them."), append:

```markdown

See also: **Context Hygiene (MANDATORY)** in `copilot-instructions.md` for the required
3-step post-phase summary pattern.
```

- [ ] **Step 5: Verify**

Open `github/WORKFLOW.md`. Confirm:
- Quick Reference table shows `@Implementation Agent` for Setup
- Folder structure shows Design Agent as Phases 2-4
- Model Routing no longer mentions Skill Usage Mapping or agent phase ranges
- Session Hygiene cross-references Context Hygiene in copilot-instructions.md
- No other content was changed

- [ ] **Step 6: Commit**

```bash
git add github/WORKFLOW.md
git commit -m "fix: WORKFLOW.md — Setup agent, Design Agent phases, model routing source of truth, context hygiene xref"
```

---

### Task 4: Multi-Source Ticket Format in conventions/SKILL.md

**Files:**
- Modify: `github/skills/conventions/SKILL.md`

- [ ] **Step 1: Replace the Ticket & Branch section**

Replace:

Old:
```markdown
## Ticket & Branch

Ticket format:  <e.g. AIB-1234 / PROJ-567 / GH-123>
Branch naming:  <e.g. TICKET-1234-short-description>
```

New:
```markdown
## Ticket & Branch

### Ticket Sources

| Source | Format | Example |
|--------|--------|---------|
| Jira | <e.g. PROJ-1234> | PROJ-567 |
| GitHub Issues | <e.g. #123 or GH-123> | GH-123 |
| Other | <format if applicable> | — |

Active ticket format: <e.g. Jira: PROJ-1234>
Branch naming:        <e.g. TICKET-1234-short-description>
```

- [ ] **Step 2: Verify**

Open `github/skills/conventions/SKILL.md`. Confirm:
- The Ticket Sources table has 3 rows: Jira, GitHub Issues, Other
- There is an `Active ticket format:` field
- Branch naming is preserved
- No other content was changed

- [ ] **Step 3: Commit**

```bash
git add github/skills/conventions/SKILL.md
git commit -m "feat: conventions template supports multiple ticket sources with active format field"
```

---

### Task 5: Multi-Source Ticket Detection in setup/SKILL.md

**Files:**
- Modify: `github/skills/setup/SKILL.md`

- [ ] **Step 1: Update allowed-tools to include write tools**

Replace:

Old:
```yaml
allowed-tools: read_file, list_dir, file_search, grep_search
```

New:
```yaml
allowed-tools: read_file, list_dir, file_search, grep_search, create_file, insert_edit_into_file, replace_string_in_file
```

- [ ] **Step 2: Update Step 4 — detect multiple ticket sources**

Replace the ticket detection bullet in Step 4:

Old:
```markdown
- Any mention of ticket format (e.g. `PROJ-1234`, `GH-123`, `#123`)
```

New:
```markdown
- Ticket sources — check for multiple formats:
  - Jira-style: `PROJ-1234`, `AIB-567` (uppercase letters + dash + digits)
  - GitHub Issues: `#123`, `GH-123`
  - Other: any other ticket ID patterns mentioned
```

- [ ] **Step 3: Update Step 6 — write multi-source ticket format**

Replace the Ticket & Branch block in the Step 6 template:

Old:
```markdown
## Ticket & Branch

Ticket format:  [detected or inferred value]
Branch naming:  [detected or inferred value]
```

New:
```markdown
## Ticket & Branch

### Ticket Sources

| Source | Format | Example |
|--------|--------|---------|
| Jira | [detected or "not detected"] | [example] |
| GitHub Issues | [detected or "not detected"] | [example] |
| Other | [detected or "not detected"] | [example] |

Active ticket format: [primary detected format — e.g. "Jira: PROJ-1234"]
Branch naming:        [detected or inferred value]
```

- [ ] **Step 4: Update Handoff — add context hygiene + model hint**

Replace the entire `## Handoff` section:

Old:
```markdown
## Handoff

Next phase: `/brainstorm`

Once the engineer has reviewed and corrected the conventions file, start the first feature with `/brainstorm`.
```

New:
```markdown
## Handoff

Next phase: `/brainstorm`

Once the engineer has reviewed and corrected the conventions file, start the first feature with `/brainstorm`.

Start a new chat. Recommended: **Premium**. Use `/brainstorm`.

Apply context hygiene summary, then proceed.
```

- [ ] **Step 5: Verify**

Open `github/skills/setup/SKILL.md`. Confirm:
- `allowed-tools` includes write tools
- Step 4 detects Jira, GitHub Issues, and Other formats
- Step 6 template writes the multi-source Ticket Sources table + Active ticket format
- Handoff includes model hint and context hygiene one-liner
- No other content was changed (skill logic, steps structure unchanged)

- [ ] **Step 6: Commit**

```bash
git add github/skills/setup/SKILL.md
git commit -m "feat: setup detects multi-source ticket formats, add write tools, handoff updates"
```

---

### Task 6: Prompt Files — Phase Announcements + Setup Agent Switch

**Files:**
- Modify: `github/prompts/setup.prompt.md`
- Modify: `github/prompts/brainstorm.prompt.md`
- Modify: `github/prompts/write-spec.prompt.md`
- Modify: `github/prompts/write-plan.prompt.md`
- Modify: `github/prompts/execute-plan.prompt.md`
- Modify: `github/prompts/quick-task.prompt.md`
- Modify: `github/prompts/tdd.prompt.md`
- Modify: `github/prompts/debug.prompt.md`
- Modify: `github/prompts/verify.prompt.md`
- Modify: `github/prompts/review.prompt.md`

Each prompt gets a phase announcement instruction added as the first line of the body (after the `---` closing the frontmatter). The setup prompt also switches from Design Agent to Implementation Agent.

- [ ] **Step 1: Edit setup.prompt.md**

Replace the entire body (after frontmatter):

Old:
```markdown
You are in **setup phase**.

Switch to @Design Agent.
Read and follow `.github/skills/setup/SKILL.md`.
```

New:
```markdown
> **Phase: Setup** | Skill: setup

You are in **setup phase**.

Switch to @Implementation Agent.
Read and follow `.github/skills/setup/SKILL.md`.
```

- [ ] **Step 2: Edit brainstorm.prompt.md**

Replace the entire body:

Old:
```markdown
You are in **brainstorm phase**.

Switch to @Design Agent.
Read and follow `.github/skills/brainstorming/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for repo context.
```

New:
```markdown
> **Phase: Brainstorm** | Skill: brainstorming

You are in **brainstorm phase**.

Switch to @Design Agent.
Read and follow `.github/skills/brainstorming/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for repo context.
```

- [ ] **Step 3: Edit write-spec.prompt.md**

Replace the entire body:

Old:
```markdown
You are in **spec phase**.

Switch to @Design Agent.
Read and follow `.github/skills/spec-writing/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for artifact paths and ticket format.

Input: paste the brainstorm summary and the ticket ID.
```

New:
```markdown
> **Phase: Spec** | Skill: spec-writing

You are in **spec phase**.

Switch to @Design Agent.
Read and follow `.github/skills/spec-writing/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for artifact paths and ticket format.

Input: paste the brainstorm summary and the ticket ID.
```

- [ ] **Step 4: Edit write-plan.prompt.md**

Replace the entire body:

Old:
```markdown
You are in **plan phase**.

Switch to @Design Agent.
Read and follow `.github/skills/planning/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for paths and commands.

Input: paste the spec file path.
```

New:
```markdown
> **Phase: Plan** | Skill: planning

You are in **plan phase**.

Switch to @Design Agent.
Read and follow `.github/skills/planning/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for paths and commands.

Input: paste the spec file path.
```

- [ ] **Step 5: Edit execute-plan.prompt.md**

Replace the entire body:

Old:
```markdown
You are in **execute phase**.

Switch to @Implementation Agent.
Read and follow `.github/skills/execution/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for the test command.

Input: paste the plan file path.
```

New:
```markdown
> **Phase: Execute** | Skill: execution

You are in **execute phase**.

Switch to @Implementation Agent.
Read and follow `.github/skills/execution/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for the test command.

Input: paste the plan file path.
```

- [ ] **Step 6: Edit quick-task.prompt.md**

Replace the entire body:

Old:
```markdown
You are in **plan phase** for a quick task.

Switch to @Design Agent.
Read and follow `.github/skills/planning/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for repo context.

**Conscious skip:** Brainstorm and spec phases bypassed — this is a quick task (bugfix,
config change, or trivial change with no design decisions). Note in the plan header:
"No spec — quick task."
```

New:
```markdown
> **Phase: Plan (Quick Task)** | Skill: planning

You are in **plan phase** for a quick task.

Switch to @Design Agent.
Read and follow `.github/skills/planning/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for repo context.

**Conscious skip:** Brainstorm and spec phases bypassed — this is a quick task (bugfix,
config change, or trivial change with no design decisions). Note in the plan header:
"No spec — quick task."
```

- [ ] **Step 7: Edit tdd.prompt.md**

Replace the entire body:

Old:
```markdown
You are in **TDD mode**.

Switch to @Implementation Agent.
Read and follow `.github/skills/tdd/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for the test command.
```

New:
```markdown
> **Phase: TDD** | Skill: tdd

You are in **TDD mode**.

Switch to @Implementation Agent.
Read and follow `.github/skills/tdd/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for the test command.
```

- [ ] **Step 8: Edit debug.prompt.md**

Replace the entire body:

Old:
```markdown
You are in **debug phase**.

Switch to @Implementation Agent.
Read and follow `.github/skills/debugging/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for the test command.

Input: paste the failing test output or describe the unexpected behaviour.
```

New:
```markdown
> **Phase: Debug** | Skill: debugging

You are in **debug phase**.

Switch to @Implementation Agent.
Read and follow `.github/skills/debugging/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for the test command.

Input: paste the failing test output or describe the unexpected behaviour.
```

- [ ] **Step 9: Edit verify.prompt.md**

Replace the entire body:

Old:
```markdown
You are in **verify phase**.

Switch to @Review Agent.
Read and follow `.github/skills/verification/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for paths and test command.

Input: paste the spec file path.
```

New:
```markdown
> **Phase: Verify** | Skill: verification

You are in **verify phase**.

Switch to @Review Agent.
Read and follow `.github/skills/verification/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for paths and test command.

Input: paste the spec file path.
```

- [ ] **Step 10: Edit review.prompt.md**

Replace the entire body:

Old:
```markdown
You are in **review phase**.

Switch to @Review Agent.
Read and follow `.github/skills/review/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for context.

Input: paste the verification file path and run `git diff --name-only main` for the changed files list.
```

New:
```markdown
> **Phase: Review** | Skill: review

You are in **review phase**.

Switch to @Review Agent.
Read and follow `.github/skills/review/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for context.

Input: paste the verification file path and run `git diff --name-only main` for the changed files list.
```

- [ ] **Step 11: Verify all 10 prompt files**

For each prompt file, confirm:
- First line after frontmatter is `> **Phase: [Name]** | Skill: [name]`
- `setup.prompt.md` says `@Implementation Agent` (not `@Design Agent`)
- No other content was changed

- [ ] **Step 12: Commit**

```bash
git add github/prompts/*.prompt.md
git commit -m "feat: add phase announcement to all prompts, switch /setup to Implementation Agent"
```

---

### Task 7: Skill Handoff Updates — Context Hygiene + Model Hints

**Files:**
- Modify: `github/skills/brainstorming/SKILL.md`
- Modify: `github/skills/spec-writing/SKILL.md`
- Modify: `github/skills/planning/SKILL.md`
- Modify: `github/skills/execution/SKILL.md`
- Modify: `github/skills/tdd/SKILL.md`
- Modify: `github/skills/debugging/SKILL.md`
- Modify: `github/skills/verification/SKILL.md`
- Modify: `github/skills/review/SKILL.md`

(setup/SKILL.md and conventions/SKILL.md were already updated in Tasks 4-5.)

For each skill: add the context hygiene one-liner at the end of the Handoff section, and add a model recommendation to skills whose handoff crosses a phase boundary (new chat).

**Model routing reference (from WORKFLOW.md):**

| Next Phase | Model |
|---|---|
| Brainstorm | Premium |
| Spec | Standard |
| Plan | Premium |
| Execute | Standard |
| TDD | Standard (no new chat) |
| Debug | Premium (no new chat) |
| Verify | Standard |
| Review | Premium |

- [ ] **Step 1: Edit brainstorming/SKILL.md Handoff**

Replace:

Old:
```markdown
## Handoff

Next phase: `/write-spec`

Paste the brainstorm summary as input to `/write-spec` along with the ticket ID.
```

New:
```markdown
## Handoff

Next phase: `/write-spec`

Paste the brainstorm summary as input to `/write-spec` along with the ticket ID.

Start a new chat. Recommended: **Standard**. Use `/write-spec`.

Apply context hygiene summary, then proceed.
```

- [ ] **Step 2: Edit spec-writing/SKILL.md Handoff**

Replace:

Old:
```markdown
## Handoff

Next phase: `/write-plan`

After spec is reviewed and approved, use `/write-plan` with the spec file path as input.
Start a new chat and keep the **Premium model** for plan phase.
```

New:
```markdown
## Handoff

Next phase: `/write-plan`

After spec is reviewed and approved, use `/write-plan` with the spec file path as input.

Start a new chat. Recommended: **Premium**. Use `/write-plan`.

Apply context hygiene summary, then proceed.
```

- [ ] **Step 3: Edit planning/SKILL.md Handoff**

Replace:

Old:
```markdown
## Handoff

Next phase: `/execute-plan`

Start a new chat, switch to **Standard model**, open @Implementation Agent, then use `/execute-plan` with the plan file path.
```

New:
```markdown
## Handoff

Next phase: `/execute-plan`

Start a new chat. Recommended: **Standard**. Use `/execute-plan` with the plan file path.

Apply context hygiene summary, then proceed.
```

- [ ] **Step 4: Edit execution/SKILL.md Handoff**

Replace:

Old:
```markdown
## Handoff

Next phase: `/verify`

Start a new chat. Use `/verify` with the spec file path to prove every requirement is met.
```

New:
```markdown
## Handoff

Next phase: `/verify`

Start a new chat. Recommended: **Standard**. Use `/verify` with the spec file path to prove every requirement is met.

Apply context hygiene summary, then proceed.
```

- [ ] **Step 5: Edit tdd/SKILL.md Handoff**

Replace:

Old:
```markdown
## Handoff

Return to `/execute-plan`

Complete the current plan step, then continue with the next step in the plan.
```

New:
```markdown
## Handoff

Return to `/execute-plan`

Complete the current plan step, then continue with the next step in the plan.

Apply context hygiene summary, then proceed.
```

No model hint — TDD does not cross a phase boundary (stays within Execute).

- [ ] **Step 6: Edit debugging/SKILL.md Handoff**

Replace:

Old:
```markdown
## Handoff

Return to `/execute-plan` after confirming the fix.

If the bug requires a non-trivial fix not covered by the current plan, start a new chat and use `/write-plan` for the fix before implementing.
```

New:
```markdown
## Handoff

Return to `/execute-plan` after confirming the fix.

If the bug requires a non-trivial fix not covered by the current plan, start a new chat. Recommended: **Premium**. Use `/write-plan` for the fix before implementing.

Apply context hygiene summary, then proceed.
```

- [ ] **Step 7: Edit verification/SKILL.md Handoff**

Replace:

Old:
```markdown
## Handoff

Next phase: `/review`

Start a new chat, switch to **Premium model**, then use `/review` with the verification file path and the list of changed files.
```

New:
```markdown
## Handoff

Next phase: `/review`

Start a new chat. Recommended: **Premium**. Use `/review` with the verification file path and the list of changed files.

Apply context hygiene summary, then proceed.
```

- [ ] **Step 8: Edit review/SKILL.md Handoff**

Replace:

Old:
```markdown
## Handoff

If no blockers: raise your PR.

If blockers found: fix each blocker, then re-invoke `/review` for the affected area only. Do not re-review the entire diff for a single fix.
```

New:
```markdown
## Handoff

If no blockers: raise your PR.

If blockers found: fix each blocker, then re-invoke `/review` for the affected area only. Do not re-review the entire diff for a single fix.

Apply context hygiene summary, then proceed.
```

No model hint — review is the final phase, no new-chat handoff.

- [ ] **Step 9: Verify all 8 skill files**

For each skill file, confirm:
- Handoff section ends with "Apply context hygiene summary, then proceed."
- Skills with new-chat handoffs include `Start a new chat. Recommended: **[Model]**. Use /[command].`
- Model hints match WORKFLOW.md routing table:
  - brainstorming → Standard (for /write-spec)
  - spec-writing → Premium (for /write-plan)
  - planning → Standard (for /execute-plan)
  - execution → Standard (for /verify)
  - verification → Premium (for /review)
  - debugging → Premium (for /write-plan, only on escalation path)
- tdd and review have no model hint (no new-chat handoff)
- No skill logic was changed — only Handoff sections modified

- [ ] **Step 10: Commit**

```bash
git add github/skills/brainstorming/SKILL.md github/skills/spec-writing/SKILL.md github/skills/planning/SKILL.md github/skills/execution/SKILL.md github/skills/tdd/SKILL.md github/skills/debugging/SKILL.md github/skills/verification/SKILL.md github/skills/review/SKILL.md
git commit -m "feat: add context hygiene one-liner and model hints to all skill handoffs"
```

---

### Task 8: End-to-End Manual Verification

**Files:** None modified — read-only verification pass.

- [ ] **Step 1: Verify /setup flow**

Open `setup.prompt.md` — confirm it says `@Implementation Agent`.
Open `implementation.agent.md` — confirm Setup is in Phases.
Open `setup/SKILL.md` — confirm `allowed-tools` includes write tools.
Open `design.agent.md` — confirm Setup is NOT in Phases.

- [ ] **Step 2: Verify phase announcements**

For each of the 10 prompt files, confirm the first line after frontmatter matches:
```
> **Phase: [Name]** | Skill: [name]
```

Expected values:
| Prompt | Phase | Skill |
|--------|-------|-------|
| setup | Setup | setup |
| brainstorm | Brainstorm | brainstorming |
| write-spec | Spec | spec-writing |
| write-plan | Plan | planning |
| execute-plan | Execute | execution |
| quick-task | Plan (Quick Task) | planning |
| tdd | TDD | tdd |
| debug | Debug | debugging |
| verify | Verify | verification |
| review | Review | review |

- [ ] **Step 3: Verify context hygiene chain**

Confirm `copilot-instructions.md` has `## Context Hygiene (MANDATORY)` section.
Confirm all 10 skill files (including setup and conventions N/A) have "Apply context hygiene summary, then proceed." in Handoff — except conventions which has no Handoff.

Total skills with the one-liner: 9 (setup, brainstorming, spec-writing, planning, execution, tdd, debugging, verification, review).
Conventions has `N/A` handoff — no change needed.

- [ ] **Step 4: Verify model hint consistency**

Cross-reference each skill's model hint against the WORKFLOW.md Model Routing table:

| Skill Handoff | Points to | Model Hint | WORKFLOW.md says |
|---|---|---|---|
| setup → brainstorm | /brainstorm | Premium | Premium |
| brainstorming → spec | /write-spec | Standard | Standard |
| spec-writing → plan | /write-plan | Premium | Premium |
| planning → execute | /execute-plan | Standard | Standard |
| execution → verify | /verify | Standard | Standard |
| verification → review | /review | Premium | Premium |
| debugging → plan (escalation) | /write-plan | Premium | Premium |
| tdd → execute | (no new chat) | N/A | N/A |
| review → done | (no new chat) | N/A | N/A |

All must match.

- [ ] **Step 5: Verify agent tools syntax**

Confirm all 3 agent files use `tools: ['tool1', 'tool2']` format (inline YAML array with single quotes).

- [ ] **Step 6: Verify no Skill Usage Mapping remains**

Search all files under `github/` for "Skill Usage Mapping". Expected: zero matches.

- [ ] **Step 7: Verify multi-source ticket format**

Open `conventions/SKILL.md` — confirm Ticket Sources table with Jira, GitHub Issues, Other rows + Active ticket format field.
Open `setup/SKILL.md` — confirm Step 4 detects multiple ticket sources, Step 6 template writes the table.

- [ ] **Step 8: Verify no unintended changes**

Run `git diff` on all 25 files. For each file, confirm only the scoped changes were made. No skill logic, execution mode, plan structure, spec structure, or review/verification content was changed.
