# Copilot Workflow Evolution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evolve the GitHub Copilot workflow system with adaptive execution routing, phased-inline mode, lean sub-agent conventions, coverage confidence enforcement, mandatory retrieval, vestigial cleanup, and documentation restructure.

**Architecture:** Changes are distributed across five phases aligned to file boundaries — peripheral skill cleanup first, then planning, then execution (the core rewrite), then retrieval enforcement, then documentation. The execution skill receives the most substantial changes because it implements routing, mode dispatch, coverage enforcement, and checkpoint discipline.

**Tech Stack:** Markdown skill files. No build system. Verification = grep/read checks against landed file content.

---

## All Files Changed

- `github/skills/review/SKILL.md` — Phase 1: remove allowed-tools frontmatter, simplify handoff (R7, R8)
- `github/skills/verification/SKILL.md` — Phase 1: remove allowed-tools frontmatter, simplify handoff (R7, R8)
- `github/skills/spec-writing/SKILL.md` — Phase 1: simplify handoff (R7, R8)
- `github/skills/setup/SKILL.md` — Phase 1: remove allowed-tools frontmatter, simplify handoff (R7, R8)
- `github/skills/debugging/SKILL.md` — Phase 1: simplify handoff (R7, R8)
- `github/skills/brainstorming/SKILL.md` — Phase 2: remove allowed-tools frontmatter, simplify handoff, retrieval visibility (R6, R7, R8)
- `github/skills/planning/SKILL.md` — Phase 3: remove allowed-tools frontmatter, 3-tier mode selection, mandatory retrieval annotation, simplify handoff (R1, R6, R7, R8)
- `github/skills/execution/SKILL.md` — Phase 4: 3-mode routing, phased-inline, inline soft checkpoints, lean sub-agent conventions, coverage confidence enforcement, simplify handoff (R2, R3, R4, R5, R7, R8)
- `github/WORKFLOW.md` — Phase 5: rewrite as usage guide, remove model routing section (R7, R9)
- `github/ARCHITECTURE.md` — Phase 5: create new system design reference (R9)

---

## Phase 1: Peripheral skill cleanup (R7, R8)

**Files:**
- Modify: `github/skills/review/SKILL.md`
- Modify: `github/skills/verification/SKILL.md`
- Modify: `github/skills/spec-writing/SKILL.md`
- Modify: `github/skills/setup/SKILL.md`
- Modify: `github/skills/debugging/SKILL.md`

**Context:** The spec confirmed (via audit before writing this plan) that `Recommended:` hints appear only in skill Handoff sections — no agent file (design.agent.md, implementation.agent.md, review.agent.md) or prompt file parses this line as a routing signal. Safe to remove without pre-update.

---

- [ ] **Step 1: Remove `allowed-tools:` line from review/SKILL.md frontmatter**

  In `github/skills/review/SKILL.md`, the frontmatter currently is:
  ```
  ---
  name: review
  description: Critical peer review of code and evidence before raising a PR. Reads spec, verification file, and all changed files with fresh eyes. Flags BLOCKERs and SUGGESTIONs. Use after the verification file is complete.
  allowed-tools: read_file, list_dir, file_search, grep_search, semantic_search, get_errors, run_in_terminal, get_terminal_output, validate_cves
  ---
  ```
  
  Replace with:
  ```
  ---
  name: review
  description: Critical peer review of code and evidence before raising a PR. Reads spec, verification file, and all changed files with fresh eyes. Flags BLOCKERs and SUGGESTIONs. Use after the verification file is complete.
  ---
  ```

- [ ] **Step 2: Verify allowed-tools removed from review/SKILL.md**

  Run: `grep -n "allowed-tools" "github/skills/review/SKILL.md"`
  Expected: no output (zero matches)

- [ ] **Step 3: Simplify review/SKILL.md handoff section**

  Find the Handoff section in `github/skills/review/SKILL.md`:
  ```
  ## Handoff
  
  If no blockers: raise your PR.
  
  If blockers found: fix each blocker, then re-invoke `/review` for the affected area only. Do not re-review the entire diff for a single fix.
  
  Apply context hygiene summary, then proceed.
  ```
  
  Replace with:
  ```
  ## Handoff
  
  If no blockers: raise your PR.
  
  If blockers found: fix each blocker, then re-invoke `/review` for the affected area only. Do not re-review the entire diff for a single fix.
  
  Apply context hygiene before closing this chat.
  ```

- [ ] **Step 4: Verify handoff updated in review/SKILL.md**

  Run: `grep -n "Apply context hygiene" "github/skills/review/SKILL.md"`
  Expected: one line containing `Apply context hygiene before closing this chat.`

  Run: `grep -n "Recommended:" "github/skills/review/SKILL.md"`
  Expected: no output

- [ ] **Step 5: Remove `allowed-tools:` line from verification/SKILL.md frontmatter**

  In `github/skills/verification/SKILL.md`, replace:
  ```
  ---
  name: verification
  description: Proves every spec requirement is met with actual test evidence before raising a PR. Reads the spec and auto-generates a pre-populated verification document. Use after all plan steps are complete and the full test suite is green.
  allowed-tools: read_file, run_in_terminal, get_terminal_output
  ---
  ```
  
  With:
  ```
  ---
  name: verification
  description: Proves every spec requirement is met with actual test evidence before raising a PR. Reads the spec and auto-generates a pre-populated verification document. Use after all plan steps are complete and the full test suite is green.
  ---
  ```

- [ ] **Step 6: Simplify verification/SKILL.md handoff section**

  Find in `github/skills/verification/SKILL.md`:
  ```
  ## Handoff
  
  Next phase: `/review`
  
  Start a new chat. Recommended: **Premium**. Use `/review` with the verification file path and the list of changed files.
  
  Apply context hygiene summary, then proceed.
  ```
  
  Replace with:
  ```
  ## Handoff
  
  Next: `/review [verification-file-path]` in a new chat.
  Note: also provide the list of changed files (`git diff --name-only main`).
  
  Apply context hygiene before closing this chat.
  ```

- [ ] **Step 7: Verify verification/SKILL.md changes**

  Run: `grep -n "allowed-tools\|Recommended:\|hygiene summary" "github/skills/verification/SKILL.md"`
  Expected: no output

- [ ] **Step 8: Simplify spec-writing/SKILL.md handoff section**

  In `github/skills/spec-writing/SKILL.md`, find:
  ```
  ## Handoff
  
  Next phase: `/write-plan`
  
  After spec is reviewed and approved, use `/write-plan` with the spec file path as input.
  
  Start a new chat. Recommended: **Premium**. Use `/write-plan`.
  
  Apply context hygiene summary, then proceed.
  ```
  
  Replace with:
  ```
  ## Handoff
  
  Next: `/write-plan [spec-file-path]` in a new chat.
  
  Apply context hygiene before closing this chat.
  ```

- [ ] **Step 9: Verify spec-writing/SKILL.md changes**

  Run: `grep -n "Recommended:\|hygiene summary" "github/skills/spec-writing/SKILL.md"`
  Expected: no output

- [ ] **Step 10: Remove `allowed-tools:` line from setup/SKILL.md frontmatter**

  In `github/skills/setup/SKILL.md`, replace:
  ```
  ---
  name: setup
  description: One-time repo initialisation. Auto-detects tech stack, test commands, and artifact paths, then writes a fully populated conventions/SKILL.md. Run once per repo before the first brainstorm session.
  allowed-tools: read_file, list_dir, file_search, grep_search, create_file, insert_edit_into_file, replace_string_in_file
  ---
  ```
  
  With:
  ```
  ---
  name: setup
  description: One-time repo initialisation. Auto-detects tech stack, test commands, and artifact paths, then writes a fully populated conventions/SKILL.md. Run once per repo before the first brainstorm session.
  ---
  ```

- [ ] **Step 11: Simplify setup/SKILL.md handoff section**

  In `github/skills/setup/SKILL.md`, find:
  ```
  ## Handoff
  
  Next phase: `/brainstorm`
  
  Once the engineer has reviewed and corrected the conventions file, start the first feature with `/brainstorm`.
  
  Start a new chat. Recommended: **Premium**. Use `/brainstorm`.
  
  Apply context hygiene summary, then proceed.
  ```
  
  Replace with:
  ```
  ## Handoff
  
  Next: `/brainstorm` in a new chat.
  Note: review and correct conventions/SKILL.md first — especially ticket format and commit style.
  
  Apply context hygiene before closing this chat.
  ```

- [ ] **Step 12: Verify setup/SKILL.md changes**

  Run: `grep -n "allowed-tools\|Recommended:\|hygiene summary" "github/skills/setup/SKILL.md"`
  Expected: no output

- [ ] **Step 13: Simplify debugging/SKILL.md handoff section**

  In `github/skills/debugging/SKILL.md`, find:
  ```
  ## Handoff
  
  Return to `/execute-plan` after confirming the fix.
  
  If the bug requires a non-trivial fix not covered by the current plan, start a new chat. Recommended: **Premium**. Use `/write-plan` for the fix before implementing.
  
  Apply context hygiene summary, then proceed.
  ```
  
  Replace with:
  ```
  ## Handoff
  
  Return to `/execute-plan` after confirming the fix.
  
  If the bug requires a non-trivial fix not covered by the current plan: Next: `/write-plan` in a new chat.
  
  Apply context hygiene before closing this chat.
  ```

- [ ] **Step 14: Verify debugging/SKILL.md changes**

  Run: `grep -n "Recommended:\|hygiene summary" "github/skills/debugging/SKILL.md"`
  Expected: no output

- [ ] **Step 15: Commit**

  ```bash
  git add "github/skills/review/SKILL.md" "github/skills/verification/SKILL.md" "github/skills/spec-writing/SKILL.md" "github/skills/setup/SKILL.md" "github/skills/debugging/SKILL.md"
  git commit -m "chore: remove vestigial allowed-tools, Recommended:, and hygiene summary from peripheral skills (R7, R8)"
  ```

**Test after this phase:**
`grep -rn "allowed-tools\|Recommended:\|hygiene summary" github/skills/review/ github/skills/verification/ github/skills/spec-writing/ github/skills/setup/ github/skills/debugging/`
Expected: no output

**Engineer review prompt:**
- Do all five files still have complete Handoff sections (just shorter)? Open each and confirm the `## Handoff` heading and body exist.
- Does debugging/SKILL.md still distinguish between "return to execute-plan" and "start new chat for non-trivial fix"?

---

## Phase 2: brainstorming/SKILL.md (R6, R7, R8)

**Files:**
- Modify: `github/skills/brainstorming/SKILL.md`

---

- [ ] **Step 1: Remove `allowed-tools:` from brainstorming/SKILL.md frontmatter**

  In `github/skills/brainstorming/SKILL.md`, replace:
  ```
  ---
  name: brainstorming
  description: Guides collaborative problem exploration with a senior architect persona before any spec is written. Activate when the user wants to explore requirements, understand a problem, discuss a new feature, or start work on a story or ticket.
  allowed-tools: read_file, list_dir, file_search, grep_search, semantic_search
  ---
  ```
  
  With:
  ```
  ---
  name: brainstorming
  description: Guides collaborative problem exploration with a senior architect persona before any spec is written. Activate when the user wants to explore requirements, understand a problem, discuss a new feature, or start work on a story or ticket.
  ---
  ```

- [ ] **Step 2: Update Intelligence Scan step 4 to make retrieval absence visible (R6)**

  In `github/skills/brainstorming/SKILL.md`, find the Intelligence Scan section step 4:
  ```
  4. Open the conversation with one of these framings:
     - **Candidates found (step 2 matched at least one module):**
       "Based on the index, `[module-name]` appears to be the primary area for this work.
       It is flagged as `[quadrant]` with `[N]` recent signals.
       Known signals: [one-line summaries from step 3, or "none yet"]. Does this match your understanding?"
     - **No candidates (step 2 found nothing, or index absent/low):**
       Proceed directly to the Active Context check and seed question in Entry Logic below.
       Open without any codebase framing.
  ```
  
  Replace with:
  ```
  4. Open the conversation with one of these framings:
     - **Candidates found (step 2 matched at least one module):**
       "Based on the index, `[module-name]` appears to be the primary area for this work.
       It is flagged as `[quadrant]` with `[N]` recent signals.
       Known signals: [one-line summaries from step 3, or "none yet"]. Does this match your understanding?"
     - **No candidates (step 2 found nothing, or index absent/low):**
       Say: "Index has no match for this ticket area — starting without codebase context."
       Then proceed directly to the Active Context check and seed question in Entry Logic below.
  ```

- [ ] **Step 3: Verify retrieval absence visibility in brainstorming/SKILL.md**

  Run: `grep -n "no match for this ticket" "github/skills/brainstorming/SKILL.md"`
  Expected: one line with the new text

- [ ] **Step 4: Simplify brainstorming/SKILL.md handoff section**

  In `github/skills/brainstorming/SKILL.md`, find:
  ```
  ## Handoff
  
  Next phase: `/write-spec`
  
  Pass the brainstorm artifact path: `/write-spec [brainstorms-path]/YYYY-MM-DD-[ticket-id]-brainstorm.md`
  
  The brainstorm summary is read from the file — do not paste the chat text.
  
  Start a new chat. Recommended: **Standard**. Use `/write-spec`.
  
  Apply context hygiene summary, then proceed.
  ```
  
  Replace with:
  ```
  ## Handoff
  
  Next: `/write-spec [brainstorms-path]/YYYY-MM-DD-[ticket-id]-brainstorm.md` in a new chat.
  Note: pass the file path — the summary is read from the file, not pasted from chat.
  
  Apply context hygiene before closing this chat.
  ```

- [ ] **Step 5: Verify all brainstorming/SKILL.md vestigial elements removed**

  Run: `grep -n "allowed-tools\|Recommended:\|hygiene summary" "github/skills/brainstorming/SKILL.md"`
  Expected: no output

- [ ] **Step 6: Commit**

  ```bash
  git add "github/skills/brainstorming/SKILL.md"
  git commit -m "feat: make retrieval absence visible in brainstorming; cleanup vestigial elements (R6, R7, R8)"
  ```

**Test after this phase:**
`grep -n "allowed-tools\|Recommended:\|hygiene summary" "github/skills/brainstorming/SKILL.md"`
Expected: no output

`grep -n "no match for this ticket" "github/skills/brainstorming/SKILL.md"`
Expected: one match

**Engineer review prompt:**
- Does the "no candidates" branch now say the explicit sentence before proceeding? Read steps 4 in the Intelligence Scan section.
- Is the handoff note preserved (file path, not pasted chat)?

---

## Phase 3: planning/SKILL.md (R1, R6, R7, R8)

**Files:**
- Modify: `github/skills/planning/SKILL.md`

---

- [ ] **Step 1: Remove `allowed-tools:` from planning/SKILL.md frontmatter**

  In `github/skills/planning/SKILL.md`, replace:
  ```
  ---
  name: planning
  description: Creates a phased implementation plan from a spec file by reading the actual codebase first. Generates concrete file-level steps with real paths — not placeholders. Use when ready to plan implementation after a spec is written and approved.
  allowed-tools: read_file, list_dir, file_search, grep_search, semantic_search
  ---
  ```
  
  With:
  ```
  ---
  name: planning
  description: Creates a phased implementation plan from a spec file by reading the actual codebase first. Generates concrete file-level steps with real paths — not placeholders. Use when ready to plan implementation after a spec is written and approved.
  ---
  ```

- [ ] **Step 2: Make intelligence retrieval mandatory (R6)**

  In `github/skills/planning/SKILL.md`, find the Intelligence Retrieval section steps 2–3:
  ```
  2. **If index absent or maturity = low:** Skip retrieval. Proceed directly to "Before Writing a Single Step" below, using the full codebase search (step 2 in that section).
  3. **After retrieval completes:**
  ```
  
  Replace with:
  ```
  2. **If index absent or maturity = low:** Skip retrieval. Proceed directly to "Before Writing a Single Step" below, using the full codebase search (step 2 in that section).
     **If index exists at any maturity above low:** Retrieval is mandatory. A skip without documented justification blocks the plan from being written.
  3. **After retrieval completes:**
  ```

- [ ] **Step 3: Replace 2-tier mode selection with 3-tier adaptive routing (R1)**

  In `github/skills/planning/SKILL.md`, find:
  ```
  **Set execution mode** based on total files across ALL phases:
  - ≤3 files total → `Execution mode: inline`
  - >3 files total → `Execution mode: phased`
  ```
  
  Replace with:
  ```
  **Set execution mode** based on total files across ALL phases. File count is the baseline signal; apply override rules after.
  
  **Baseline:**
  - ≤5 files AND low risk → `Execution mode: inline`
  - 6–12 files OR high risk/uncertainty → `Execution mode: phased-inline`
  - >12 files → `Execution mode: phased-subagent`
  
  **Override rules (apply after baseline):**
  - ≤5 files with high risk/uncertain steps → escalate to `phased-inline`
  - 6–12 tightly coupled, well-understood files, low complexity → downgrade to `inline`
  - >12 files of trivial changes (e.g. rename across files) → may use `phased-inline`
  
  **Risk signals — escalate one tier if any are true:**
  - Any step touches a module flagged `active` or `high-risk` in the codebase index
  - Any step requires resolving a decision conflict flagged during planning
  - More than 3 steps in a phase are marked with "or equivalent" / "depending on current state"
  
  **Required:** Include a one-sentence mode justification on the `> **Execution mode:**` line:
  `> **Execution mode:** phased-inline — 8 files, auth module has high iteration risk`
  ```

- [ ] **Step 4: Add retrieval annotation to Plan Structure (R6)**

  In `github/skills/planning/SKILL.md`, find in the Plan Structure template:
  ```
  > **Execution mode:** [inline | phased]
  ```
  
  Replace with:
  ```
  > **Execution mode:** [inline | phased-inline | phased-subagent] — [one-sentence justification]
  > **Retrieval:** [ran | skipped — reason]
  ```

- [ ] **Step 5: Verify mode selection section updated**

  Run: `grep -n "phased-inline\|phased-subagent" "github/skills/planning/SKILL.md"`
  Expected: multiple lines — baseline, override rules, risk signals, and template annotation

  Run: `grep -n "Retrieval:" "github/skills/planning/SKILL.md"`
  Expected: at least one line in the Plan Structure template

- [ ] **Step 6: Simplify planning/SKILL.md handoff section**

  In `github/skills/planning/SKILL.md`, find:
  ```
  ## Handoff
  
  Next phase: `/execute-plan`
  
  Start a new chat. Recommended: **Standard**. Use `/execute-plan` with the plan file path.
  
  Apply context hygiene summary, then proceed.
  ```
  
  Replace with:
  ```
  ## Handoff
  
  Next: `/execute-plan [plan-file-path]` in a new chat.
  
  Apply context hygiene before closing this chat.
  ```

- [ ] **Step 7: Verify all planning/SKILL.md vestigial elements removed**

  Run: `grep -n "allowed-tools\|Recommended:\|hygiene summary" "github/skills/planning/SKILL.md"`
  Expected: no output

- [ ] **Step 8: Commit**

  ```bash
  git add "github/skills/planning/SKILL.md"
  git commit -m "feat: 3-tier adaptive routing, mandatory retrieval annotation, cleanup in planning skill (R1, R6, R7, R8)"
  ```

**Test after this phase:**
`grep -n "phased-inline\|phased-subagent" "github/skills/planning/SKILL.md"`
Expected: ≥4 matches (baseline, override, risk signal, template)

`grep -n "allowed-tools\|Recommended:\|hygiene summary" "github/skills/planning/SKILL.md"`
Expected: no output

**Engineer review prompt:**
- Does the mode justification requirement appear in both the Phase Quality Rules section and the Plan Structure template?
- Is the skip condition for low-maturity index preserved alongside the new mandatory-retrieval rule?

---

## Phase 4: execution/SKILL.md (R2, R3, R4, R5, R7, R8)

**Files:**
- Modify: `github/skills/execution/SKILL.md`

This is the largest single-file edit. Steps are ordered to: (1) update Step 1 for 3-mode routing, (2) add coverage announcement, (3) add phased-inline as a new mode section, (4) update inline with soft checkpoints, (5) update sub-agent with lean conventions, (6) cleanup handoff.

---

- [ ] **Step 1: Update execution mode announcement in Step 1 (R2)**

  In `github/skills/execution/SKILL.md`, find:
  ```
  3. Check the `> **Execution mode:**` line in the plan.
     If no `Execution mode:` annotation is found (legacy plan): count total files in the plan.
     Use inline if ≤3 files, phased if >3 files.
  4. Announce your mode:
     - **inline:** "2 files total. Using **inline mode** — executing all steps now."
     - **phased:** "11 files across 4 phases. Using **sub-agent mode** — I'll execute one phase at a time, commit, and pause for your review before each next phase."
  ```
  
  Replace with:
  ```
  3. Check the `> **Execution mode:**` line in the plan. Three valid values:
     - `inline` — execute all steps in this session
     - `phased-inline` — execute phases sequentially in this session with hard gates between phases
     - `phased-subagent` — dispatch each phase to a fresh sub-agent
     If no `Execution mode:` annotation is found (legacy plan): count total files in the plan.
     Use `inline` if ≤5 files, `phased-inline` if 6–12 files, `phased-subagent` if >12 files.
  4. Announce your mode:
     - **inline:** "2 files total. Using **inline mode** — executing all steps now."
     - **phased-inline:** "8 files across 3 phases. Using **phased-inline mode** — I'll execute phases sequentially in this session with a review gate between each."
     - **phased-subagent:** "14 files across 4 phases. Using **sub-agent mode** — I'll dispatch each phase to a fresh subagent and pause for your review before proceeding."
  ```

- [ ] **Step 2: Add coverage confidence announcement block after Step 1 (R4)**

  In `github/skills/execution/SKILL.md`, after the mode announcement step (Step 1 ends with the mode announcement), add a new step. Find:
  ```
  ## Step 2a: Inline Execution (`Execution mode: inline`)
  ```
  
  Replace with:
  ```
  ## Step 1b: Coverage Confidence Announcement (all modes)
  
  Read `Coverage confidence:` from the context packet (if loaded in Step 2a/2b/2c below) or check plan `## Intelligence Context` block.
  
  Announce at session/phase start:
  - `high`: "Context: high coverage — file reads restricted to context packet. I will not load files outside it."
  - `medium`: "Context: medium coverage — one-hop expansion allowed for files referenced by loaded modules."
  - `low`: "Context: low coverage — full codebase search available. I will note gaps as encountered."
  
  If no context packet and no `## Intelligence Context` block: treat as `low`. Announce: "No context packet found. Context: low coverage — proceeding with full codebase search."
  
  ## Step 2a: Inline Execution (`Execution mode: inline`)
  ```

- [ ] **Step 3: Verify mode routing and coverage announcement landed**

  Run: `grep -n "phased-inline\|phased-subagent\|Coverage Confidence" "github/skills/execution/SKILL.md"`
  Expected: ≥6 matches covering mode names and the new step heading

- [ ] **Step 4: Add coverage enforcement rules to inline context packet check (R4)**

  In `github/skills/execution/SKILL.md`, find the inline context packet check:
  ```
  3. If found: read the full context packet. Note the `Coverage confidence` field. Use `## Relevant Decisions` and `## Module Context` to frame your understanding before touching any code. Do not load additional module or knowledge pages from the index — the packet is the full context budget for this plan.
  4. If not found: proceed without pre-loaded context. The Codebase Search Protocol remains available on demand throughout execution.
  ```
  
  Replace with:
  ```
  3. If found: read the full context packet. Note the `Coverage confidence` field. Enforce based on level:
     - `high`: **Prohibited** from reading files outside the context packet. If a step requires a file read outside the packet, stop and say: "Step [N] requires reading [file], which is outside the context packet. Coverage is HIGH. Should I expand context or rephrase the step to work within the packet?"
     - `medium`: Controlled one-hop expansion allowed — may read files referenced by packet modules; do not scan broadly.
     - `low`: Expansion required. The Codebase Search Protocol is available without restriction.
     Use `## Relevant Decisions` and `## Module Context` to frame understanding before touching any code.
  4. If not found: treat as `low` coverage. Note: "No context packet found — proceeding with full codebase search." The Codebase Search Protocol is available without restriction.
  ```

- [ ] **Step 5: Add inline soft checkpoints and hard checkpoint (R5)**

  In `github/skills/execution/SKILL.md`, find:
  ```
  Work through all steps sequentially:
  1. Execute each step in order. Do not skip any.
  ```
  
  Replace with:
  ```
  **Inline checkpoint discipline:**
  - Count total steps in the plan. If ≥6: group steps by file (all steps on one file form one group, or by natural dependency boundary).
  - After each group completes, show a **soft checkpoint** (informational — no gate, proceed automatically):
    ```
    — [group name, e.g. "RateLimiter.java"] — [N steps complete]
    Tests: [PASS / FAIL — one-line summary]
    ```
  - After all steps complete: show a **hard checkpoint** in the same format as the phased checkpoint below (files changed, Stage 1, Stage 2, test output, finishing options). This is the only gate in inline mode.
  - For inline plans with <6 steps: no soft checkpoints. Hard checkpoint at the end only.
  
  Work through all steps sequentially:
  1. Execute each step in order. Do not skip any.
  ```

- [ ] **Step 6: Verify inline soft checkpoint section landed**

  Run: `grep -n "soft checkpoint\|hard checkpoint\|Inline checkpoint discipline" "github/skills/execution/SKILL.md"`
  Expected: ≥3 matches

- [ ] **Step 7: Add phased-inline as a new mode section (R2)**

  In `github/skills/execution/SKILL.md`, find:
  ```
  ## Step 2b: Sub-Agent Execution (`Execution mode: phased`)
  ```
  
  Replace with:
  ```
  ## Step 2b: Phased-Inline Execution (`Execution mode: phased-inline`)
  
  Execute phases sequentially in the current session. No sub-agents. UX is identical to phased-subagent — same phase start format, same checkpoint format, same gate discipline.
  
  For each phase:
  
  **Announce phase start:**
  ```
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Phase [N] of [M] — [Phase name] — [N files] / [N steps]
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ```
  
  **Context packet check (before each phase):**
  1. Read `Context Packets:` path from `.github/skills/conventions/SKILL.md`.
  2. Read `[context-packets-path]/[ticket-id]/phase-[N]-context.md` if it exists.
  3. If found: load it. Enforce coverage confidence behavior (see Step 1b).
  4. If not found: treat as `low` confidence. Note: "No context packet for phase [N]. Proceeding with full codebase search."
  
  **Execute all steps** in the phase using inline execution rules (see Step 2a).
  
  **Run two-stage review** (same as Step 2c sub-agent review below) before showing the checkpoint.
  
  **Phase checkpoint (show after both stages pass):**
  ```
  Phase [N] complete — [Phase name]
  
  Files changed:
    + [file] (created)
    ~ [file] (modified)
  
  [Stage 1] Spec compliance: PASS
  OR
  [Stage 1] Spec compliance: FAIL — [missing file or unlisted change]
  
  [Stage 2] Code quality: PASS
  OR
  [Stage 2] Code quality: FAIL — [finding: what + where]
  
  Test output:
  [pasted output]
  
  Review:
  [exact questions from plan's Engineer review prompt for this phase]
  
  Type `continue` for Phase [N+1], or describe a concern.
  ```
  
  Show exactly one Stage 1 line and one Stage 2 line — the applicable variant only (PASS or FAIL, not both).
  PASS is one line. FAIL is one line including the finding. No explanation, no suggestion.
  
  **Gate is hard:** do not proceed to the next phase without explicit `continue` from the engineer.
  
  **On test failure:** "Phase [N] failed — [test name or compliance finding]. Use `/debug`. Type `retry phase [N]` when fixed." No auto-retry.
  
  **Amendment and discovery tracking:** identical to inline mode — append to plan file under `## Amendments` or `## Discoveries`.
  
  **After all phases complete** — run the full test suite in this session and present finishing options (same as inline mode).
  
  ## Step 2c: Sub-Agent Execution (`Execution mode: phased-subagent`)
  ```

- [ ] **Step 8: Verify phased-inline section landed**

  Run: `grep -n "phased-inline\|Phased-Inline\|Phase \[N\] complete" "github/skills/execution/SKILL.md"`
  Expected: ≥5 matches including the section heading and checkpoint format

- [ ] **Step 9: Update sub-agent phase announcement to use separator format (R2)**

  In `github/skills/execution/SKILL.md` in the Step 2c section, find where phases are dispatched. Look for the subagent dispatch heading and add phase announcement. Find:
  ```
  ### Dispatch the subagent
  
  **Before dispatching — context packet check:**
  ```
  
  Replace with:
  ```
  ### Dispatch the subagent
  
  **Announce phase start before dispatching:**
  ```
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Phase [N] of [M] — [Phase name] — [N files] / [N steps]
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ```
  
  **Before dispatching — context packet check:**
  ```

- [ ] **Step 10: Replace full conventions embed with lean summary in sub-agent prompt (R3)**

  In `github/skills/execution/SKILL.md`, find the sub-agent prompt template that starts with:
  ```
  --- CONVENTIONS ---
  [Paste the full raw text content of conventions/SKILL.md here]
  --- END CONVENTIONS ---
  ```
  
  Replace with:
  ```
  --- CONVENTIONS ---
  Test: [test command from conventions/SKILL.md]
  Commit: [commit format from conventions/SKILL.md]
  Lint: [lint command from conventions/SKILL.md, or "none"]
  Ticket: [ticket format from conventions/SKILL.md]
  --- END CONVENTIONS ---
  [--- INJECTED: [section name] ---
  [section content from conventions/SKILL.md — only present when keyword-triggered; omit block entirely if no injection]
  ```
  
  And before the subagent prompt template, add these instructions for dynamic injection:
  ```
  **Before building the sub-agent prompt — dynamic conventions injection:**
  Scan each step's text in this phase for these keyword patterns. When matched, read the named section from `conventions/SKILL.md` and append it after `--- END CONVENTIONS ---` labeled `--- INJECTED: [section name] ---`:
  - Words "error", "exception", "throws", "catch", "validate", "validation" → `## Error Handling`
  - Words "endpoint", "request", "response", "API", "contract", "status code" → `## API Conventions`
  - Words "migration", "schema", "table", "query", "database", "model" → `## Data Conventions`
  - Any framework name that appears as a section header in conventions (exact match) → that section
  - Default: no injection beyond the minimal summary
  If `conventions/SKILL.md` does not contain a matching section: no injection. Do not fail or warn.
  ```

- [ ] **Step 11: Collapse sub-agent RULES block from 10 to 8 rules (R3)**

  In `github/skills/execution/SKILL.md`, find the RULES block in the sub-agent prompt:
  ```
  RULES:
  1. Execute steps in order. Do not skip any.
  2. Before making any change that affects a public interface, a dependency's behavior, or a constraint boundary: check ## Relevant Decisions in the CONTEXT PACKET (if available). If your change conflicts with a recorded decision: stop. Return the conflict to the parent session — do not proceed without acknowledgment.
  3. After each step, run the test command from CONVENTIONS.
  4. If any test fails: stop immediately and return the failure output. Do not proceed.
  5. Do not make changes not listed in the steps above. If something looks wrong, report back.
  6. **REQUIRED:** Follow TDD for any step creating new logic: write the failing test FIRST (RED), then implement (GREEN). No production code without a failing test.
  7. **REQUIRED:** If a test fails and the cause is not obvious, follow systematic debugging: reproduce -> isolate -> hypothesise -> verify -> fix. Do not guess.
  8. Commit when all steps pass: "[ticket-id] phase [N]: [phase name]"
  9. If a deviation from the plan is necessary and engineer-approved: append to the plan file — add `## Amendments` section at the end if missing, then append: `- [YYYY-MM-DD] Phase [N]: [what changed and why it was necessary]`
  10. If you discover an unexpected constraint or system behavior: append to the plan file — add `## Discoveries` section at the end if missing, then append: `- [YYYY-MM-DD] [brief description of what you discovered]`
  ```
  
  Replace with:
  ```
  RULES:
  1. Execute steps in order. Do not skip any.
  2. Before making any change that affects a public interface, a dependency's behavior, or a constraint boundary: check ## Relevant Decisions in the CONTEXT PACKET (if available). If your change conflicts with a recorded decision: stop. Return the conflict to the parent session — do not proceed without acknowledgment.
  3. After each step, run the test command from CONVENTIONS.
  4. If any test fails: stop immediately and return the failure output. Do not proceed.
  5. Do not make changes not listed in the steps above. If something looks wrong, report back.
  6. Follow TDD for new logic (RED→GREEN→REFACTOR); use systematic debugging for failures (reproduce→isolate→hypothesise→verify→fix).
  7. Commit when all steps pass: "[ticket-id] phase [N]: [phase name]"
  8. Amendments: append to `## Amendments` in plan file — `- [YYYY-MM-DD] Phase [N]: [change and reason]`. Discoveries: append to `## Discoveries` — `- [YYYY-MM-DD] [description]`.
  ```

- [ ] **Step 12: Update sub-agent checkpoint to new format (R2)**

  In `github/skills/execution/SKILL.md` in the Step 2c review section, find:
  ```
  **After both stages pass**, show the engineer:
  
  > **Phase [N] complete — [Phase name]**
  >
  > **Files changed:** `[file1]` (created), `[file2]` (modified)
  >
  > **Test output:**
  > ```
  > [Paste full output from subagent — do not summarise]
  > ```
  >
  > **Please review:**
  > [Copy the exact "Engineer review prompt" text from the plan for this phase]
  >
  > Type `continue` to proceed to Phase [N+1], or describe any concerns.
  ```
  
  Replace with:
  ```
  **After both stages pass**, show the engineer:
  
  ```
  Phase [N] complete — [Phase name]
  
  Files changed:
    + [file1] (created)
    ~ [file2] (modified)
  
  [Stage 1] Spec compliance: PASS
  OR
  [Stage 1] Spec compliance: FAIL — [missing file or unlisted change]
  
  [Stage 2] Code quality: PASS
  OR
  [Stage 2] Code quality: FAIL — [finding: what + where]
  
  Test output:
  [Paste full output from subagent — do not summarise]
  
  Review:
  [Copy the exact "Engineer review prompt" text from the plan for this phase]
  
  Type `continue` for Phase [N+1], or describe a concern.
  ```
  
  Show exactly one Stage 1 line and one Stage 2 line — the applicable variant only. PASS is one line. FAIL is one line with the finding. No explanation, no suggestion.
  ```

- [ ] **Step 13: Update execution/SKILL.md handoff section (R7, R8)**

  In `github/skills/execution/SKILL.md`, find:
  ```
  ## Handoff
  
  Next phase: `/verify`
  
  Start a new chat. Recommended: **Standard**. Use `/verify` with the spec file path to prove every requirement is met.
  
  Apply context hygiene summary, then proceed.
  ```
  
  Replace with:
  ```
  ## Handoff
  
  Next: `/verify [spec-file-path]` in a new chat.
  
  Apply context hygiene before closing this chat.
  ```

- [ ] **Step 14: Verify all execution/SKILL.md changes**

  Run: `grep -n "Recommended:\|hygiene summary\|Execution mode: phased\"" "github/skills/execution/SKILL.md"`
  Expected: no output (the quoted string `Execution mode: phased"` with closing quote should find zero matches since the new text always includes a suffix)

  Run: `grep -n "phased-inline\|phased-subagent\|lean summary\|INJECTED\|soft checkpoint\|Stage 1\|Stage 2" "github/skills/execution/SKILL.md"`
  Expected: ≥8 matches across new sections

  Run: `grep -c "RULES:" "github/skills/execution/SKILL.md"`
  Expected: 1

  Run: `grep -A 9 "RULES:" "github/skills/execution/SKILL.md" | grep -c "^[0-9]"`
  Expected: 8 (8 numbered rules)

- [ ] **Step 15: Commit**

  ```bash
  git add "github/skills/execution/SKILL.md"
  git commit -m "feat: phased-inline mode, lean sub-agent conventions, coverage confidence enforcement, inline soft checkpoints (R2, R3, R4, R5, R7, R8)"
  ```

**Test after this phase:**
`grep -n "phased-inline\|phased-subagent" "github/skills/execution/SKILL.md" | wc -l`
Expected: ≥8

`grep -n "Recommended:\|hygiene summary" "github/skills/execution/SKILL.md"`
Expected: no output

**Engineer review prompt:**
- Does phased-inline in Step 2b show UX-identical output to phased-subagent? Read both phase checkpoint blocks — they should use the same separator format and the same Stage 1 / Stage 2 line structure.
- Does the sub-agent RULES block now have exactly 8 rules with TDD and debugging merged into rule 6?
- Does the dynamic injection instruction appear before the sub-agent prompt template (not inside it)?
- Does the coverage confidence enforcement correctly distinguish HIGH (prohibited), MEDIUM (one-hop), and LOW (unrestricted)?

---

## Phase 5: WORKFLOW.md + ARCHITECTURE.md (R7, R9)

**Files:**
- Modify: `github/WORKFLOW.md`
- Create: `github/ARCHITECTURE.md`

---

- [ ] **Step 1: Rewrite WORKFLOW.md as a usage guide (R7, R9)**

  Overwrite `github/WORKFLOW.md` with the following content. This removes the Model Routing section (lines 77–112 in the original), removes sub-agent mechanics, and restructures as a practical usage guide:

  ```markdown
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
  ```

- [ ] **Step 2: Verify WORKFLOW.md rewrite**

  Run: `grep -n "Model Routing\|Recommended:\|sub-agent mode\|Sub-Agent" "github/WORKFLOW.md"`
  Expected: no matches for Model Routing or Recommended; sub-agent references in the example and cheat sheet are acceptable (they describe user-facing behavior, not internal mechanics)

  Run: `grep -n "updated:" "github/WORKFLOW.md"`
  Expected: one line with `updated: 2026-04-17`

  Run: `grep -n "phased-inline" "github/WORKFLOW.md"`
  Expected: at least one match (in the example section)

- [ ] **Step 3: Create ARCHITECTURE.md (R9)**

  Create `github/ARCHITECTURE.md` with the following content:

  ```markdown
  # Architecture Reference: GitHub Copilot Workflow
  
  updated: 2026-04-17
  
  This document describes the internal mechanics of the workflow system. It is the reference for system designers and skill maintainers — not for day-to-day use. For usage guidance, see WORKFLOW.md.
  
  **Sync policy:** Updated in the same commit as any skill that changes its decision logic. WORKFLOW.md is not updated for internal mechanism changes.
  
  ---
  
  ## Execution Mode Decision Logic
  
  The planner (`planning/SKILL.md`) sets execution mode when writing the plan. The executor reads the annotated mode and runs it. This separation keeps the execution skill simple; routing intelligence lives where the plan is made.
  
  ### Three-Tier Model
  
  | Mode | File count baseline | Typical use |
  |---|---|---|
  | `inline` | ≤5 files, low risk | Small changes, well-understood modules |
  | `phased-inline` | 6–12 files OR high risk | Most feature plans — checkpoint discipline without sub-agent cost |
  | `phased-subagent` | >12 files | Large or context-heavy plans where fresh context per phase is required |
  
  ### Override Rules
  
  Applied after the baseline, before writing the `> **Execution mode:**` line:
  - ≤5 files + high risk/uncertain steps → escalate to `phased-inline`
  - 6–12 tightly coupled, well-understood files, low complexity → downgrade to `inline`
  - >12 files of trivial changes (e.g. rename across files) → may use `phased-inline`
  
  ### Risk Signals (escalate one tier if any are true)
  
  - A step touches a module flagged `active` or `high-risk` in the codebase index
  - A step requires resolving a decision conflict flagged during planning
  - More than 3 steps in a phase are marked with "or equivalent" / "depending on current state"
  
  ### Justification Requirement
  
  Every plan must include a one-sentence mode justification on the `> **Execution mode:**` line:
  `> **Execution mode:** phased-inline — 8 files, auth module has high iteration risk`
  
  ---
  
  ## Phased-Inline Mechanism
  
  `phased-inline` executes phases sequentially in the current session with no sub-agents. It is UX-identical to `phased-subagent` — same phase start format, same checkpoint format, same gate discipline. The engineer cannot distinguish the modes from the output.
  
  **Phase start announcement (both phased-inline and phased-subagent):**
  ```
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Phase [N] of [M] — [Phase name] — [N files] / [N steps]
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ```
  
  **Phase checkpoint format (both modes):**
  ```
  Phase [N] complete — [Phase name]
  
  Files changed:
    + [file] (created)
    ~ [file] (modified)
  
  [Stage 1] Spec compliance: PASS | FAIL — [finding]
  [Stage 2] Code quality: PASS | FAIL — [finding]
  
  Test output:
  [pasted output]
  
  Review:
  [exact questions from plan's Engineer review prompt]
  
  Type `continue` for Phase [N+1], or describe a concern.
  ```
  
  **Gate:** Hard. No auto-continue. On failure: "Phase [N] failed — use `/debug`. Type `retry phase [N]` when fixed."
  
  **Trade-off vs phased-subagent:** phased-inline accumulates tool call history across phases. For plans near the 12-file upper boundary, late phases may have reduced context focus. At current plan sizes (≤40 steps) this is not a concern at 200k context; revisit if plans regularly exceed that.
  
  ---
  
  ## Sub-Agent Dispatch Protocol
  
  Used only in `phased-subagent` mode. Each phase dispatches a fresh `@Implementation Agent` sub-session.
  
  ### Minimal Conventions Summary
  
  Sub-agent prompts do not embed the full `conventions/SKILL.md`. Instead, a minimal summary is extracted at dispatch time:
  ```
  --- CONVENTIONS ---
  Test: [command]
  Commit: [format]
  Lint: [command or "none"]
  Ticket: [format]
  --- END CONVENTIONS ---
  ```
  
  ### Dynamic Injection Rules
  
  Additional convention sections are injected only when phase steps match keyword patterns. The parent session scans step text before dispatch and appends matching sections after `--- END CONVENTIONS ---`:
  
  | Keywords in step text | Section injected |
  |---|---|
  | error, exception, throws, catch, validate, validation | `## Error Handling` |
  | endpoint, request, response, API, contract, status code | `## API Conventions` |
  | migration, schema, table, query, database, model | `## Data Conventions` |
  | Framework name matching a section header in conventions | That section |
  
  If `conventions/SKILL.md` does not contain a matching section: no injection. No failure or warning.
  
  **Design principle:** pull-based, not push-based. The parent scans and pushes only relevant sections. Sub-agents don't decide what they need — they receive what was determined relevant.
  
  ---
  
  ## Coverage Confidence Constraint Table
  
  Coverage confidence is set by the context packet's `Coverage confidence:` field, or by the plan's `## Intelligence Context` block. It is a behavioral constraint, not metadata.
  
  | Level | Behavior |
  |---|---|
  | `high` | **Prohibited** from reading files outside the context packet. Any step requiring an out-of-packet file read must stop and ask. |
  | `medium` | Controlled one-hop expansion — may read files referenced by packet modules; no broad scanning. |
  | `low` | **Required** to acknowledge the gap. Full codebase search available without restriction. |
  
  Coverage level is surfaced at phase/session start: `Context: [high|medium|low] coverage — [behavior description]`
  
  If no context packet exists for a phase: treat as `low`. The absence is always announced explicitly — never silent.
  
  Coverage enforcement is identical across inline, phased-inline, and phased-subagent modes.
  
  ---
  
  ## Retrieval Integration Points
  
  Retrieval is enforced at three entry points:
  
  | Phase | Behavior |
  |---|---|
  | **Planning** (`planning/SKILL.md`) | Mandatory when index exists at any maturity above `low`. Skip requires documented justification. Plan must note: `Retrieval: ran | skipped — [reason]` |
  | **Execution** (`execution/SKILL.md`) | Context packet check is mandatory. If not found: explicitly noted — "No context packet for phase [N]. Proceeding with full codebase search." Never silent. |
  | **Brainstorming** (`brainstorming/SKILL.md`) | Intelligence scan always runs. When candidates found: surface before first question. When no candidates found: "Index has no match for this ticket area — starting without codebase context." Absence is visible. |
  
  Retrieval enforcement does not apply to spec-writing, TDD, debugging, or verification — these operate on artifacts already produced.
  
  ---
  
  ## Review Checkpoint Anatomy
  
  ### Two-Stage Review
  
  **Stage 1: Spec Compliance** — Does the diff match the plan? All listed files changed, no unlisted changes. If Stage 1 fails: agent fixes before showing checkpoint.
  
  **Stage 2: Code Quality** — Only runs after Stage 1 passes. Tests test behaviour, conventions followed, no obvious issues the spec required.
  
  ### Stage Detail Rules
  
  PASS is one line. FAIL is one line including the finding (what + where). No explanation, no suggestion — the engineer decides what to do with it.
  
  Show exactly one Stage 1 line and one Stage 2 line — the applicable variant only.
  
  ### Gate Protocol
  
  Hard gate: the agent does not proceed to the next phase without explicit `continue` from the engineer. No auto-retry on failure — engineer must invoke `/debug` and return with `retry phase [N]`.
  
  ---
  
  ## Inline Soft Checkpoints
  
  Applied only in `inline` mode with ≥6 total steps.
  
  Steps are grouped by file (all steps on one file = one group) or by natural dependency boundary. After each group:
  ```
  — [group name] — [N steps complete]
  Tests: [PASS / FAIL — summary line]
  ```
  
  Soft checkpoints are informational. No gate. Agent proceeds automatically.
  
  After all steps: one hard checkpoint (same format as phased checkpoint). This is the only gate in inline mode.
  
  For inline plans with <6 steps: no soft checkpoints. Hard checkpoint at the end only.
  
  ---
  
  ## Session Hygiene Protocol
  
  Start a new chat at every phase boundary. Each phase builds its context from scratch — a fresh session prevents stale assumptions from accumulating across phases.
  
  Skills reference this protocol via their Handoff sections. The canonical definition lives here; skills do not duplicate it.
  
  ---
  
  ## Evolution Principles
  
  - **Mechanisms replace rules.** A behavioral constraint enforced by artifact or file-based check is stronger than a convention in a document.
  - **Simpler systems that scale.** Every addition must justify its complexity against the maintenance cost.
  - **Every constraint must be enforceable** as an artifact or a file-based check — not a convention.
  - **ARCHITECTURE.md is not aspirational.** It describes how the system actually behaves. If a skill implementation diverges, update one of them — not both to stay in sync with a future state.
  ```

- [ ] **Step 4: Verify ARCHITECTURE.md created**

  Run: `ls -la "github/ARCHITECTURE.md"`
  Expected: file exists, non-zero size

  Run: `grep -n "updated:\|Execution Mode Decision\|Phased-Inline\|Sub-Agent Dispatch\|Coverage Confidence\|Retrieval Integration\|Review Checkpoint\|Inline Soft Checkpoint\|Session Hygiene Protocol\|Evolution Principles" "github/ARCHITECTURE.md" | wc -l`
  Expected: ≥9 (all major section headings present)

- [ ] **Step 5: Verify WORKFLOW.md line count is reasonable**

  Run: `wc -l "github/WORKFLOW.md"`
  Expected: ≤120 lines (the rewrite is substantially shorter than the original 293 lines)

- [ ] **Step 6: Commit**

  ```bash
  git add "github/WORKFLOW.md" "github/ARCHITECTURE.md"
  git commit -m "feat: rewrite WORKFLOW.md as usage guide; create ARCHITECTURE.md with system design reference (R7, R9)"
  ```

**Test after this phase:**
`grep -n "Model Routing" "github/WORKFLOW.md"`
Expected: no output

`grep -c "##" "github/ARCHITECTURE.md"`
Expected: ≥9 section headings

**Engineer review prompt:**
- Does WORKFLOW.md contain any sub-agent mechanics, threshold logic, or execution mode internals? If yes, those belong in ARCHITECTURE.md — move them.
- Does ARCHITECTURE.md cover all 8 sections listed in spec R9? (Execution mode decision logic, phased-inline mechanism, sub-agent dispatch protocol, coverage confidence table, retrieval integration points, review checkpoint anatomy, session hygiene protocol, evolution principles)
- Is the end-to-end example in WORKFLOW.md ≤40 lines and uses the new phased-inline terminology?

---

## Testing Checklist (run after all phases complete)

- [ ] `grep -rn "allowed-tools" github/skills/execution/ github/skills/verification/ github/skills/review/ github/skills/planning/ github/skills/brainstorming/` — expected: no output
- [ ] `grep -rn "Recommended:" github/skills/` — expected: no output
- [ ] `grep -rn "hygiene summary" github/skills/` — expected: no output
- [ ] `grep -n "Model Routing" github/WORKFLOW.md` — expected: no output
- [ ] `grep -n "phased-inline\|phased-subagent" github/skills/planning/SKILL.md` — expected: ≥4 matches
- [ ] `grep -n "phased-inline\|phased-subagent" github/skills/execution/SKILL.md` — expected: ≥8 matches
- [ ] `grep -n "no match for this ticket" github/skills/brainstorming/SKILL.md` — expected: 1 match
- [ ] `grep -n "Retrieval:" github/skills/planning/SKILL.md` — expected: ≥1 match
- [ ] `ls github/ARCHITECTURE.md` — expected: file exists
- [ ] `grep -n "tdd/SKILL.md\|verification/SKILL.md\|review/SKILL.md" github/skills/tdd/SKILL.md github/skills/verification/SKILL.md github/skills/review/SKILL.md` — confirm these files' internal logic is unchanged from the original (they were not in scope)

## Rollback Plan

- Revert all phase commits: `git revert HEAD~5` (5 commits, one per phase)
- All changes are to Markdown files only — no schema changes, no data migrations, no binaries
