# Copilot Context Hygiene & Premium Usage Balance — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce per-session premium quota consumption in IntelliJ Copilot by adding model routing guidance, new-chat-per-phase hygiene, Active Context short-circuit in brainstorming, automated conventions setup, and a quick-task bypass.

**Architecture:** Three interlocking levers — (1) a model routing table visible at every chat start, (2) explicit "Start a new chat" instructions at every phase-end handoff, and (3) a one-sentence Active Context block in conventions that eliminates cold-start file exploration in brainstorming. Supplemented by a new `/setup` prompt that auto-populates conventions and a `/quick-task` prompt that bypasses brainstorm/spec for simple work.

**Tech Stack:** Markdown only. No build system. No test runner. Verification is reading the output files and confirming content matches the spec.

---

## All Files Changed

- `github/copilot-instructions.md` — Task 1: add Model Routing table + Session Hygiene hard rule
- `github/skills/conventions/SKILL.md` — Task 2: add `## Active Context` section at bottom
- `github/skills/brainstorming/SKILL.md` — Task 2: replace "Before Asking Anything" with Active Context check/write-back
- `github/skills/planning/SKILL.md` — Task 3: update phase-end handoff with new-chat + model-switch instructions
- `github/skills/spec-writing/SKILL.md` — Task 3: update phase-end handoff
- `github/skills/tdd/SKILL.md` — Task 3: update phase-end handoff
- `github/skills/debugging/SKILL.md` — Task 3: update phase-end handoff
- `github/skills/execution/SKILL.md` — Task 4: update both inline and phased phase-end handoffs
- `github/skills/verification/SKILL.md` — Task 4: update phase-end handoff
- `github/skills/review/SKILL.md` — Task 4: update phase-end handoff
- `github/skills/setup/SKILL.md` — Task 5: **NEW** — auto-detects stack and writes conventions
- `github/prompts/setup.prompt.md` — Task 5: **NEW** — triggers setup skill
- `github/prompts/quick-task.prompt.md` — Task 6: **NEW** — direct-to-plan bypass
- `github/WORKFLOW.md` — Task 7: add Setup, Model Routing, and Session Hygiene sections; update cheat sheet

---

## Task 1: copilot-instructions.md — Model Routing + Session Hygiene

**Files:**
- Modify: `github/copilot-instructions.md`

- [ ] **Step 1: Add Model Routing table and Session Hygiene rule**

  Open `github/copilot-instructions.md`. Append the following two sections after the existing `## Hard Rules` block:

  ```markdown
  ## Model Routing

  Switch models at every phase boundary. Premium quota compounds within a session.

  | Phase | Model | Reason |
  |---|---|---|
  | Brainstorm | Premium | Ambiguity resolution, architectural judgment |
  | Plan | Premium | Codebase reading + architectural decisions |
  | Debug | Premium | Root cause reasoning |
  | Review | Premium | Critical judgment, spec deviation detection |
  | Spec-writing | Standard | Transcribing agreed design — template work |
  | Execute | Standard | Mechanical — plan tells it exactly what to do |
  | TDD | Standard | Pattern-following (red → green → refactor) |
  | Verify | Standard | Checklist against known requirements |

  ## Session Hygiene

  **Start a new chat at every phase boundary.**

  Premium quota compounds within a session — each turn re-processes the full conversation
  history. A new chat resets the cost counter to zero.

  The skill handoff message at the end of each phase will remind you. Do not skip it.
  ```

- [ ] **Step 2: Verify**

  Read `github/copilot-instructions.md` and confirm:
  - `## Model Routing` table is present with 8 rows
  - `## Session Hygiene` section is present with the new-chat instruction
  - Existing content (`## The Cycle`, `## Phase Routing`, `## Hard Rules`, etc.) is unchanged

- [ ] **Step 3: Commit**

  ```bash
  git add github/copilot-instructions.md
  git commit -m "feat: add model routing table and session hygiene rule to copilot-instructions"
  ```

---

## Task 2: Active Context — conventions/SKILL.md + brainstorming/SKILL.md

**Files:**
- Modify: `github/skills/conventions/SKILL.md`
- Modify: `github/skills/brainstorming/SKILL.md`

- [ ] **Step 1: Add `## Active Context` section to conventions/SKILL.md**

  Open `github/skills/conventions/SKILL.md`. Append the following at the very end of the file (after the `## Notes` section):

  ```markdown
  ## Active Context

  <Written by /brainstorm — describes the current feature or problem being worked on. Leave blank between features.>
  ```

- [ ] **Step 2: Verify conventions/SKILL.md**

  Read `github/skills/conventions/SKILL.md` and confirm:
  - `## Active Context` section is present at the bottom
  - The placeholder text reads exactly: `<Written by /brainstorm — describes the current feature or problem being worked on. Leave blank between features.>`
  - All existing sections (Ticket & Branch, Artifact Paths, Tech Stack, Commit Message Format, PR Convention, Notes) are unchanged

- [ ] **Step 3: Rewrite "Before Asking Anything" in brainstorming/SKILL.md**

  Open `github/skills/brainstorming/SKILL.md`. Replace the entire `## Before Asking Anything` section (lines 13–25, from `## Before Asking Anything` through the blank line before `## During the Conversation`) with:

  ```markdown
  ## Before Asking Anything

  1. Read `.github/skills/conventions/SKILL.md`.
  2. Check the `## Active Context` block.

  **Active Context present and non-empty:** use it as your starting point. Skip all file
  exploration. Ask your first targeted question based on the described context.

  **Active Context absent or empty:**
  1. Ask exactly: *"In 1–2 sentences, what are you working on?"*
  2. Write their answer into the `## Active Context` block in
     `.github/skills/conventions/SKILL.md`.
  3. Then proceed with targeted questions.

  **When file exploration is needed** (Active Context absent and you need codebase grounding):
  Use `list_dir`, `file_search`, and `semantic_search` to understand structure and find
  relevant areas. Do this silently — do not narrate every file you open. Summarise what you
  found in 2–3 sentences to show you have done your homework.

  **Greenfield or new area** (no relevant existing code):
  Start with the problem domain after writing Active Context.
  ```

- [ ] **Step 4: Verify brainstorming/SKILL.md**

  Read `github/skills/brainstorming/SKILL.md` and confirm:
  - The new `## Before Asking Anything` section reads conventions first, then checks Active Context
  - The two conditional branches (present/non-empty vs absent/empty) are both present
  - The "file exploration needed" and "greenfield" cases are preserved as fallbacks
  - `## During the Conversation` and `## Convergence` sections are unchanged

- [ ] **Step 5: Commit**

  ```bash
  git add github/skills/conventions/SKILL.md github/skills/brainstorming/SKILL.md
  git commit -m "feat: add Active Context to conventions and brainstorming skill"
  ```

---

## Task 3: Phase-End Handoffs — planning, spec-writing, tdd, debugging

**Files:**
- Modify: `github/skills/planning/SKILL.md`
- Modify: `github/skills/spec-writing/SKILL.md`
- Modify: `github/skills/tdd/SKILL.md`
- Modify: `github/skills/debugging/SKILL.md`

- [ ] **Step 1: Update planning/SKILL.md handoff**

  Open `github/skills/planning/SKILL.md`. Replace the last block:

  ```markdown
  When plan is complete, say:
  > "Plan written to `[path]`. Switch to @Implementation Agent, then use `/execute-plan`."
  ```

  With:

  ```markdown
  When plan is complete, say:
  > "Plan written to `[path]`.
  >
  > **Session hygiene:** Start a new chat. Switch to **standard model**. Open @Implementation Agent. Then use `/execute-plan`."
  ```

- [ ] **Step 2: Update spec-writing/SKILL.md handoff**

  Open `github/skills/spec-writing/SKILL.md`. Replace the last block:

  ```markdown
  When spec is complete, say:
  > "Spec written to `[path]`. Review it, then use `/write-plan`."
  ```

  With:

  ```markdown
  When spec is complete, say:
  > "Spec written to `[path]`. Review it.
  >
  > **Session hygiene:** Start a new chat. Keep **premium model**. Then use `/write-plan`."
  ```

- [ ] **Step 3: Update tdd/SKILL.md handoff**

  Open `github/skills/tdd/SKILL.md`. Replace the last line:

  ```markdown
  Return to `/execute-plan` after each TDD cycle is complete and all tests are green.
  ```

  With:

  ```markdown
  Return to `/execute-plan` phase.
  ```

- [ ] **Step 4: Update debugging/SKILL.md handoff**

  Open `github/skills/debugging/SKILL.md`. Replace the last line in Step 6:

  ```markdown
  Say: "Bug fixed. Return to `/execute-plan` to continue at step [N]."
  ```

  With:

  ```markdown
  Say: "Bug fixed.
  > **Session hygiene:** Start a new chat. Switch to **standard model**. Use `/write-plan` for the fix."
  ```

- [ ] **Step 5: Verify all four files**

  Read each of the four files and confirm:
  - `planning/SKILL.md`: last line now contains "Start a new chat. Switch to **standard model**."
  - `spec-writing/SKILL.md`: last line now contains "Start a new chat. Keep **premium model**."
  - `tdd/SKILL.md`: last line reads "Return to `/execute-plan` phase." (no trailing content)
  - `debugging/SKILL.md`: Step 6 handoff contains "Start a new chat. Switch to **standard model**. Use `/write-plan` for the fix."

- [ ] **Step 6: Commit**

  ```bash
  git add github/skills/planning/SKILL.md github/skills/spec-writing/SKILL.md github/skills/tdd/SKILL.md github/skills/debugging/SKILL.md
  git commit -m "feat: add session hygiene handoffs to planning, spec-writing, tdd, and debugging skills"
  ```

---

## Task 4: Phase-End Handoffs — execution, verification, review

**Files:**
- Modify: `github/skills/execution/SKILL.md`
- Modify: `github/skills/verification/SKILL.md`
- Modify: `github/skills/review/SKILL.md`

- [ ] **Step 1: Update execution/SKILL.md — inline mode handoff**

  Open `github/skills/execution/SKILL.md`. In **Step 2a (Inline Execution)**, replace:

  ```markdown
  After all steps:
  1. Run the full test suite.
  2. Say: "All steps complete. Full suite green. Switch to @Review Agent, then use `/verify`."
  ```

  With:

  ```markdown
  After all steps:
  1. Run the full test suite.
  2. Say: "All steps complete. Full suite green.
  > **Session hygiene:** Start a new chat. Use `/verify`."
  ```

- [ ] **Step 2: Update execution/SKILL.md — phased mode handoff**

  In the same file, in **Step 2b (Sub-Agent Execution)**, under "After all phases complete", replace:

  ```markdown
  Then say: "Full suite green. Switch to @Review Agent, then use `/verify`."
  ```

  With:

  ```markdown
  Then say: "Full suite green.
  > **Session hygiene:** Start a new chat. Use `/verify`."
  ```

- [ ] **Step 3: Update verification/SKILL.md handoff**

  Open `github/skills/verification/SKILL.md`. Replace the last block:

  ```markdown
  When done, say:
  > "Verification file written to `[path]`. Ready for `/review`."
  ```

  With:

  ```markdown
  When done, say:
  > "Verification file written to `[path]`.
  >
  > **Session hygiene:** Start a new chat. Switch to **premium model**. Then use `/review`."
  ```

- [ ] **Step 4: Update review/SKILL.md handoff**

  Open `github/skills/review/SKILL.md`. Replace:

  ```markdown
  If there are no blockers: say "No blockers. Ready to merge."
  ```

  With:

  ```markdown
  If there are no blockers: say "No blockers. All phases complete. Raise your PR."
  ```

- [ ] **Step 5: Verify all three files**

  Read each file and confirm:
  - `execution/SKILL.md`: both inline and phased paths end with "Start a new chat. Use `/verify`."
  - `verification/SKILL.md`: last line contains "Start a new chat. Switch to **premium model**. Then use `/review`."
  - `review/SKILL.md`: no-blockers line reads "No blockers. All phases complete. Raise your PR."

- [ ] **Step 6: Commit**

  ```bash
  git add github/skills/execution/SKILL.md github/skills/verification/SKILL.md github/skills/review/SKILL.md
  git commit -m "feat: add session hygiene handoffs to execution, verification, and review skills"
  ```

---

## Task 5: Setup Skill — auto-populate conventions

**Files:**
- Create: `github/skills/setup/SKILL.md`
- Create: `github/prompts/setup.prompt.md`

- [ ] **Step 1: Create github/skills/setup/SKILL.md**

  ```markdown
  ---
  name: setup
  description: One-time repo initialisation. Auto-detects tech stack, test commands, and artifact paths, then writes a fully populated conventions/SKILL.md. Run once per repo before the first brainstorm session.
  allowed-tools: read_file, list_dir, file_search, grep_search
  ---

  You are setting up workflow conventions for this repo. You will read the codebase and write
  a fully populated `.github/skills/conventions/SKILL.md` without asking the engineer to fill
  anything in manually.

  ## Step 1: Detect Project Type

  Run `list_dir` at the repo root. Note all files present, especially manifest files.

  ## Step 2: Read the Build Manifest

  Read whichever manifest exists (check in this order):
  - `pom.xml` — Java/Maven
  - `build.gradle` or `build.gradle.kts` — Java/Kotlin/Gradle
  - `package.json` — JavaScript/TypeScript/Node
  - `go.mod` — Go
  - `requirements.txt` or `pyproject.toml` — Python
  - `Cargo.toml` — Rust

  Extract: language, framework (if present), project name, declared dependencies.

  ## Step 3: Find Commands

  Use `grep_search` to find test, build, and lint commands:
  - **package.json:** search `"scripts"` block for `"test"`, `"build"`, `"lint"` keys
  - **pom.xml:** standard Maven — `mvn test`, `mvn package`, `mvn checkstyle:check`
  - **build.gradle:** search for test task customisation; default is `./gradlew test`
  - **go.mod:** standard Go — `go test ./...`, `go build ./...`, `go vet ./...`
  - **pyproject.toml / setup.cfg:** look for `[tool.pytest.ini_options]`; default is `pytest`
  - **Cargo.toml:** standard Rust — `cargo test`, `cargo build`, `cargo clippy`

  Also check for a `Makefile`: run `grep_search` for lines matching `^test:`, `^build:`, `^lint:`.
  If found, use those as the commands.

  Check `.github/workflows/` for CI config. Read the first `.yml` file found. Extract the
  exact test and build commands used in CI — these are the authoritative commands.

  ## Step 4: Read Project Docs

  Run `read_file` on `README.md`. Extract:
  - Project description (1–2 sentences)
  - Any mention of ticket format (e.g. `PROJ-1234`, `GH-123`, `#123`)
  - Any PR title or commit message conventions

  If no README exists, skip this step.

  ## Step 5: Detect Artifact Paths

  Check if any of these directories exist:
  - `docs/specs/` or `docs/workflow/specs/` → use as specs path
  - `docs/plans/` or `docs/workflow/plans/` → use as plans path
  - `docs/verifications/` or `docs/workflow/verifications/` → use as verifications path

  If none exist, default to:
  - Specs: `docs/specs/`
  - Plans: `docs/plans/`
  - Verifications: `docs/verifications/`

  ## Step 6: Write conventions/SKILL.md

  Write `.github/skills/conventions/SKILL.md` with every field populated from what you
  detected. Do not leave any placeholder text such as `<e.g. ...>`.

  Where you could not detect a value, write your best inference and append `# inferred — verify this`.

  ```markdown
  ---
  name: conventions
  description: Repo-specific conventions for this project — tech stack, test commands, artifact paths, ticket format, and commit style. Always read this skill when starting any phase to ground responses in this repo's actual context.
  ---

  # Repo Conventions

  ## Ticket & Branch

  Ticket format:  [detected or inferred value]
  Branch naming:  [detected or inferred value]

  ## Artifact Paths (relative to project root)

  Specs:          [detected value]
  Plans:          [detected value]
  Verifications:  [detected value]

  ## Tech Stack

  Language:       [detected value]
  Framework:      [detected value or "none"]
  Test command:   [detected value]
  Build command:  [detected value]
  Lint command:   [detected value or "none"]

  ## Commit Message Format

  [detected or inferred value]

  ## PR Convention

  Title:  [detected or inferred value]
  Body:   [detected or inferred value]

  ## Notes

  [Any additional conventions found in README or CI config. If none, write "None detected."]

  ## Active Context

  <Written by /brainstorm — describes the current feature or problem being worked on. Leave blank between features.>
  ```

  ## Step 7: Report

  Say:
  > "Conventions written to `.github/skills/conventions/SKILL.md`. Review it and correct
  > anything I got wrong — especially ticket format and commit style.
  >
  > When ready, use `/brainstorm` to start your first feature."
  ```

- [ ] **Step 2: Create github/prompts/setup.prompt.md**

  ```markdown
  ---
  description: One-time repo initialisation — auto-detects tech stack and writes a fully populated conventions/SKILL.md
  ---

  You are in **setup phase**.

  Switch to @Design Agent.
  Read and follow `.github/skills/setup/SKILL.md`.
  ```

- [ ] **Step 3: Verify both new files**

  Read `github/skills/setup/SKILL.md` and confirm:
  - 7 steps present: Detect Project Type, Read Build Manifest, Find Commands, Read Project Docs, Detect Artifact Paths, Write conventions/SKILL.md, Report
  - Manifest check list covers: pom.xml, build.gradle, package.json, go.mod, requirements.txt/pyproject.toml, Cargo.toml
  - Step 6 shows the exact template with `## Active Context` section at bottom
  - Step 7 report message tells engineer to review and then use `/brainstorm`

  Read `github/prompts/setup.prompt.md` and confirm:
  - frontmatter description is present
  - Directs to @Design Agent and references `setup/SKILL.md`

- [ ] **Step 4: Commit**

  ```bash
  git add github/skills/setup/SKILL.md github/prompts/setup.prompt.md
  git commit -m "feat: add setup skill and prompt for automated conventions initialisation"
  ```

---

## Task 6: Quick-Task Prompt

**Files:**
- Create: `github/prompts/quick-task.prompt.md`

- [ ] **Step 1: Create github/prompts/quick-task.prompt.md**

  ```markdown
  ---
  description: Direct-to-plan bypass for bugfixes, config changes, and simple tasks — skips brainstorm and spec phases
  ---

  You are in **plan phase** for a quick task.

  Switch to @Design Agent.
  Read and follow `.github/skills/planning/SKILL.md`.
  Also read `.github/skills/conventions/SKILL.md` for repo context.

  **Conscious skip:** Brainstorm and spec phases bypassed — this is a quick task (bugfix,
  config change, or trivial change with no design decisions). Note in the plan header:
  "No spec — quick task."
  ```

- [ ] **Step 2: Verify**

  Read `github/prompts/quick-task.prompt.md` and confirm:
  - frontmatter description present
  - Directs to @Design Agent and references `planning/SKILL.md` and `conventions/SKILL.md`
  - "Conscious skip" note present with instruction to annotate plan header

- [ ] **Step 3: Commit**

  ```bash
  git add github/prompts/quick-task.prompt.md
  git commit -m "feat: add quick-task prompt for direct-to-plan bypass"
  ```

---

## Task 7: WORKFLOW.md — Setup, Model Routing, Session Hygiene, Cheat Sheet

**Files:**
- Modify: `github/WORKFLOW.md`

- [ ] **Step 1: Update the Quick Reference table**

  Open `github/WORKFLOW.md`. In the `## Quick Reference` table, add a row for Setup at the top (before Brainstorm):

  ```markdown
  | Setup | First time in a repo | @Design Agent | `/setup` | Populated `conventions/SKILL.md` |
  ```

  Also add a row for Quick Task (after Review):

  ```markdown
  | Quick Task | Bugfix / config change | @Design Agent | `/quick-task` | Plan file, skipping brainstorm + spec |
  ```

- [ ] **Step 2: Replace the Setup section**

  Find the `## Setup (one-time per repo)` section. Replace its entire content (the numbered list) with:

  ```markdown
  ## Setup (one-time per repo)

  1. Copy the `.github/` folder to the root of your repo.
  2. Open Copilot Chat. Type `/setup`.
     The Design Agent reads your repo and writes `skills/conventions/SKILL.md` automatically.
  3. Review the generated file and correct anything wrong — especially ticket format and commit style.
  4. In IntelliJ: Settings → Tools → GitHub Copilot → enable Agent Mode, Custom Agents, Subagents, and Skills.

  That's it. Every other file is language-agnostic and requires no editing.
  ```

- [ ] **Step 3: Add Model Routing section**

  After the `## Setup (one-time per repo)` section and before the end-to-end example, add:

  ```markdown
  ## Model Routing

  Use the right model for each phase. Design quality is the investment that makes execution cheap.

  | Phase | Model |
  |---|---|
  | Brainstorm | Premium |
  | Plan | Premium |
  | Debug | Premium |
  | Review | Premium |
  | Spec-writing | Standard |
  | Execute | Standard |
  | TDD | Standard |
  | Verify | Standard |

  Switch models when you start a new chat at each phase boundary. The model routing table is
  also visible in `copilot-instructions.md` at the top of every chat.

  ---
  ```

- [ ] **Step 4: Add Session Hygiene section**

  After the Model Routing section, add:

  ```markdown
  ## Session Hygiene

  **Start a new chat at every phase boundary.**

  Premium quota compounds within a session — each turn re-processes the full conversation
  history. The longer a session runs, the more expensive each turn becomes.

  Starting a new chat at every phase transition resets the cost counter to zero. The skill
  handoff messages tell you when to do this — follow them.

  **Why this matters:** In a session with 20 turns of Sonnet 4.6, the last few turns can cost
  3× the first turn due to accumulated context. Phases are natural resets — use them.

  ---
  ```

- [ ] **Step 5: Update the Cheat Sheet**

  In the `## Cheat Sheet: Common Situations` section, add two entries before the existing ones:

  ```markdown
  **"I'm starting in a new repo"**
  → Run `/setup` first. The Design Agent reads your repo and fills in `conventions/SKILL.md`.
  Then `/brainstorm` for your first feature.

  **"I have a simple bugfix or config change"**
  → Use `/quick-task`. Goes directly to `/write-plan`, skipping brainstorm and spec.
  ```

- [ ] **Step 6: Verify WORKFLOW.md**

  Read `github/WORKFLOW.md` and confirm all of these are present:
  - Quick Reference table has `/setup` and `/quick-task` rows
  - `## Setup` section no longer says "fill in your repo's values" / no longer contains a numbered list that asks for manual editing
  - `## Model Routing` section is present with 8-row table
  - `## Session Hygiene` section is present explaining the compounding cost
  - Cheat sheet has "new repo" and "simple bugfix" entries
  - End-to-end example and other existing sections are unchanged

- [ ] **Step 7: Commit**

  ```bash
  git add github/WORKFLOW.md
  git commit -m "docs: update WORKFLOW.md with setup, model routing, session hygiene, and quick-task"
  ```

---

## Verification Checklist (run after all tasks complete)

- [ ] **Success criterion 1:** `/setup` flow — `skills/setup/SKILL.md` exists, contains 7 steps, Step 6 template has all fields and `## Active Context` section
- [ ] **Success criterion 2:** `/brainstorm` with empty Active Context — skill asks one question ("In 1–2 sentences, what are you working on?"), writes answer to conventions, then proceeds
- [ ] **Success criterion 3:** `/brainstorm` with existing Active Context — skill skips exploration and goes directly to first question
- [ ] **Success criterion 4:** Every skill phase-end says "Start a new chat" — confirmed in planning, spec-writing, execution (×2), debugging, verification
- [ ] **Success criterion 5:** Model routing table in `copilot-instructions.md` — 8 rows present
- [ ] **Success criterion 6:** `/quick-task` prompt exists and routes to planning skill with conscious-skip annotation
- [ ] **Success criterion 7:** `WORKFLOW.md` setup section no longer says "fill in manually"

## Rollback

- Revert all task commits: `git revert HEAD~7` (one per task, 7 commits total)
- No data migrations, no schema changes, no dependencies added
