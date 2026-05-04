# Copilot Workflow: Knowledge Accumulation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a post-ticket learning prompt, an append-only workflow log, an artifact index, structured conventions sections, and a semantic search protocol — so knowledge and discovery compound across tickets instead of evaporating at chat close.

**Architecture:** The review skill gains a structured debrief prompt at ticket close. The context hygiene persistence rule (from Plan 2) is extended with two append rules: one line to `log.md` per phase completion, one line to `artifact-index.md` per created artifact. The conventions template gains domain sections (Codebase, Testing, Development) replacing the flat Tech Stack block, giving skills a finer-grained load target. The execution and debugging skills each gain a Codebase Search Protocol that bounds semantic search to two tries before falling back to grep.

**Tech Stack:** Markdown only — no code, no build system, no test runner. Verification for each phase is a concrete scenario trace.

**Spec:** `docs/superpowers/specs/2026-04-16-copilot-workflow-gap-analysis-design.md`

**Depends on:** Plan 2 (`2026-04-16-copilot-workflow-handoff-persistence.md`) must be implemented first — Phase 2 of this plan extends the persistence rule added in Plan 2.

---

> **Execution mode:** phased

## All Files Changed

- `github/skills/review/SKILL.md` — Phase 1: add post-ticket learning debrief after sign-off
- `github/copilot-instructions.md` — Phase 2: extend context hygiene persistence with log and artifact index rules
- `github/skills/conventions/SKILL.md` — Phase 3: replace Tech Stack with Codebase, Testing, Development sections
- `github/skills/setup/SKILL.md` — Phase 3: update Step 3 detection and Step 6 output template to match new sections
- `github/skills/execution/SKILL.md` — Phase 4: add Codebase Search Protocol section
- `github/skills/debugging/SKILL.md` — Phase 4: add Codebase Search Protocol section

---

## Phase 1: Post-Ticket Learning Debrief in Review Skill

**Files in this phase:**
- Modify: `github/skills/review/SKILL.md`

- [ ] **Step 1: Locate the no-blockers sign-off in the Output Format section**

In `github/skills/review/SKILL.md`, find the Output Format section:

```
If there are no blockers: "No blockers. All phases complete. Raise your PR."
```

- [ ] **Step 2: Add learning debrief after the sign-off line**

Replace:

```
If there are no blockers: "No blockers. All phases complete. Raise your PR."
```

With:

```markdown
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

---
```

- [ ] **Step 3: Trace scenario to verify**

Mental trace — review phase completes for PROJ-123 with no blockers.

Confirm:
1. Agent outputs "No blockers. All phases complete. Raise your PR."
2. Immediately below, the four-question debrief block is output.
3. If the engineer found a gotcha not already in `## Discoveries`, they add it to the plan file now.
4. If conventions is out of date (e.g. a library version changed), the engineer updates it before marking the ticket done.
5. The debrief is not automated — it requires engineer responses. No automated action is required from the agent.

Mental trace — review phase has blockers:
1. Agent outputs the BLOCKER list only. No debrief is shown.
2. Debrief is shown only after all blockers are resolved and "No blockers." is reached.

- [ ] **Step 4: Commit**

```bash
git add github/skills/review/SKILL.md
git commit -m "feat: add post-ticket learning debrief to review sign-off"
```

**Engineer review prompt:**
- The debrief references `## Discoveries` in the plan file — a section introduced in Plan 2. Confirm that if Plan 2 is not yet implemented (i.e., there is no `## Discoveries` section), the debrief question 1 still makes sense (the answer is just "no, there is nothing to add").
- Is the debrief phrasing clear enough that an engineer reading it under time pressure will engage with it, rather than skipping it? If questions 3 and 4 feel too abstract, they can be merged into "Was anything about this ticket harder or easier than the plan predicted? If yes, note it."

---

## Phase 2: Workflow Log and Artifact Index

**Files in this phase:**
- Modify: `github/copilot-instructions.md`

- [ ] **Step 1: Locate the context hygiene persistence block from Plan 2**

In `github/copilot-instructions.md`, find the persistence rule added in Plan 2 (the last rule in the `## Context Hygiene (MANDATORY)` section):

```
- After outputting this block, save it to `[Handoffs path]/[ticket-id].md`:
  - If the file doesn't exist: create it with the header `# Handoff Log: [ticket-id]` on line 1, then append the block below the header.
  - If the file exists: append two blank lines, then the block.
  - `[Handoffs path]` comes from the `Handoffs:` line in `conventions/SKILL.md`. If that line is missing or empty, use `docs/handoffs/`.
  - `[ticket-id]` comes from the `ticket:` frontmatter field of any artifact created this phase. If no artifact was created, read the `Active Context` block in `conventions/SKILL.md`.
```

- [ ] **Step 2: Extend persistence rule with log and artifact index append rules**

Replace the block above with:

```markdown
- After outputting this block, save it to `[Handoffs path]/[ticket-id].md`:
  - If the file doesn't exist: create it with the header `# Handoff Log: [ticket-id]` on line 1, then append the block below the header.
  - If the file exists: append two blank lines, then the block.
  - `[Handoffs path]` comes from the `Handoffs:` line in `conventions/SKILL.md`. If that line is missing or empty, use `docs/handoffs/`.
  - `[ticket-id]` comes from the `ticket:` frontmatter field of any artifact created this phase. If no artifact was created, read the `Active Context` block in `conventions/SKILL.md`.
- Append one line to `[Handoffs parent]/log.md` (the parent directory of the Handoffs path — e.g. if Handoffs is `docs/workflow/handoffs/`, the log is `docs/workflow/log.md`; create with header `# Workflow Log` if missing):
  `[YYYY-MM-DD] | [ticket-id] | [phase-name] | complete`
- For each file listed under a "Created:" line in the Artifacts section of this block, append one line to `[Handoffs parent]/artifact-index.md` (create with header `# Artifact Index` if missing):
  `[YYYY-MM-DD] | [ticket-id] | [phase-name] | [full-artifact-path] — [description from the Artifacts line]`
```

- [ ] **Step 3: Trace scenario to verify**

Conventions has `Handoffs: docs/workflow/handoffs/`. Engineer completes the brainstorm phase for PROJ-456. Context hygiene block lists:

```
**Artifacts:**
- Created: `docs/workflow/brainstorms/2026-04-16-PROJ-456-brainstorm.md` — brainstorm artifact with aligned problem and success criteria
```

Confirm after the context hygiene block is output:
1. `docs/workflow/handoffs/PROJ-456.md` is created (or appended to) with the block.
2. `docs/workflow/log.md` gets one new line: `2026-04-16 | PROJ-456 | brainstorm | complete`
3. `docs/workflow/artifact-index.md` gets one new line: `2026-04-16 | PROJ-456 | brainstorm | docs/workflow/brainstorms/2026-04-16-PROJ-456-brainstorm.md — brainstorm artifact with aligned problem and success criteria`

Mental trace — context hygiene block has no Created lines (only Modified):
1. Handoff file is still appended to.
2. Log line is still written.
3. Artifact index gets no new lines (only "Created:" lines trigger entries — "Modified:" lines do not).

Mental trace — Handoffs path is `docs/handoffs/` (default, no parent workflow dir):
1. Log file path is `docs/log.md`.
2. Artifact index path is `docs/artifact-index.md`.

- [ ] **Step 4: Commit**

```bash
git add github/copilot-instructions.md
git commit -m "feat: extend context hygiene persistence with workflow log and artifact index append"
```

**Engineer review prompt:**
- The parent directory derivation (strip the last path segment from the Handoffs path) is ambiguous if the Handoffs path has a trailing slash vs. not. Confirm the rule instruction is clear enough: `docs/workflow/handoffs/` → parent is `docs/workflow/`; `docs/handoffs/` → parent is `docs/`. Add an explicit example to the rule if needed.
- Is `docs/log.md` a good default location when the user has `docs/handoffs/` (not under a `workflow/` subdirectory)? Alternatively, define the log path as `[Handoffs path]/../log.md` explicitly using relative path notation.

---

## Phase 3: Conventions Domain Segmentation

**Files in this phase:**
- Modify: `github/skills/conventions/SKILL.md`
- Modify: `github/skills/setup/SKILL.md`

**Note:** This change restructures the conventions template from one flat "Tech Stack" section to three domain sections (Codebase, Testing, Development). Existing conventions files populated by `/setup` before this plan are not affected — they keep their current structure. The new structure applies when `/setup` is re-run. Skills that read conventions search by content (e.g. "find the test command"), not by section name, so they will continue to work with both old and new formats.

- [ ] **Step 1: Replace Tech Stack section in conventions/SKILL.md template**

In `github/skills/conventions/SKILL.md`, find the `## Tech Stack` section:

```
## Tech Stack

Language:       <e.g. Java / Python / Go / TypeScript>
Framework:      <e.g. Spring Boot / FastAPI / Gin / Next.js>
Test command:   <e.g. mvn test / pytest / go test ./... / npm test>
Build command:  <e.g. mvn package / pip install / go build / npm run build>
Lint command:   <e.g. checkstyle / flake8 / golint / eslint>
```

Replace with:

```markdown
## Codebase

Language:       <e.g. Java / Python / Go / TypeScript>
Framework:      <e.g. Spring Boot / FastAPI / Gin / Next.js>
Entry points:   <e.g. src/main/java/App.java / cmd/main.go / app/__init__.py>
Key modules:    <e.g. auth, billing, api — names of the main packages or modules>

## Testing

Test command:   <e.g. mvn test / pytest / go test ./... / npm test>
Test location:  <e.g. src/test/java/ / tests/ / __tests__/>
Test patterns:  <e.g. unit tests use mocks; integration tests use @SpringBootTest>

## Development

Build command:  <e.g. mvn package / pip install / go build / npm run build>
Lint command:   <e.g. checkstyle / flake8 / golint / eslint>
Local dev:      <e.g. mvn spring-boot:run / flask run / go run ./cmd/ / npm run dev>
```

- [ ] **Step 2: Trace scenario to verify conventions change**

Mental trace — a new engineer opens `conventions/SKILL.md` after running `/setup`. Confirm:
1. The file has three sections: `## Codebase`, `## Testing`, `## Development` where `## Tech Stack` was.
2. `## Artifact Paths`, `## Commit Message Format`, `## PR Convention`, `## Notes`, `## Active Context` are unchanged.
3. Skills that look for "Test command:" still find it under `## Testing`.

- [ ] **Step 3: Extend setup/SKILL.md Step 3 to detect new fields**

In `github/skills/setup/SKILL.md`, find Step 3 (Find Commands). The step currently detects test, build, and lint commands. After the block that reads CI config, add the following detection instructions:

Find the end of Step 3 (the line ending the CI config detection):

```
If found, use those as the commands.

Check `.github/workflows/` for CI config. Read the first `.yml` file found. Extract the
exact test and build commands used in CI — these are the authoritative commands.
```

Replace with:

```markdown
If found, use those as the commands.

Check `.github/workflows/` for CI config. Read the first `.yml` file found. Extract the
exact test and build commands used in CI — these are the authoritative commands.

Also detect:
- **Entry points**: look for `main` files at common paths: `src/main/java/` (Java), `cmd/` or `main.go` (Go), `app.py` or `app/__init__.py` (Python), `src/index.ts` or `src/main.ts` (TypeScript). Use the first match found, or write `# inferred — verify this` if none found.
- **Test location**: check for `src/test/`, `tests/`, `__tests__/`, `spec/`. Use the first that exists.
- **Test patterns**: read one test file from the test location. Note whether it uses mocks, integration setup (e.g. `@SpringBootTest`, `pytest fixtures`), or in-memory DBs. Summarise in one sentence.
- **Key modules**: list the top-level package or directory names under the main source root (e.g. `src/main/java/com/example/` sub-packages; `src/` top-level directories). List at most 5 names.
- **Local dev command**: check `package.json` scripts for `"start"` or `"dev"`; check for Spring Boot Maven plugin in `pom.xml`; check `Makefile` for a `run:` or `serve:` target. If none found, write `# inferred — verify this`.
```

- [ ] **Step 4: Update setup/SKILL.md Step 6 output template to use domain sections**

In `github/skills/setup/SKILL.md`, find the `## Tech Stack` block inside the Step 6 output template:

```
## Tech Stack

Language:       [detected value]
Framework:      [detected value or "none"]
Test command:   [detected value]
Build command:  [detected value]
Lint command:   [detected value or "none"]
```

Replace with:

```markdown
## Codebase

Language:       [detected value]
Framework:      [detected value or "none"]
Entry points:   [detected value or "# inferred — verify this"]
Key modules:    [detected value or "# inferred — verify this"]

## Testing

Test command:   [detected value]
Test location:  [detected value or "# inferred — verify this"]
Test patterns:  [detected value or "# inferred — verify this"]

## Development

Build command:  [detected value]
Lint command:   [detected value or "none"]
Local dev:      [detected value or "# inferred — verify this"]
```

- [ ] **Step 5: Trace scenario to verify setup changes**

Mental trace — user runs `/setup` on a TypeScript/Node repo with `src/index.ts`, `tests/` directory, `package.json` scripts: `"test": "jest"`, `"build": "tsc"`, `"dev": "ts-node src/index.ts"`.

Confirm generated conventions contains:

```
## Codebase

Language:       TypeScript
Framework:      none
Entry points:   src/index.ts
Key modules:    [top-level dirs under src/ — e.g. controllers, services, models]

## Testing

Test command:   npm test
Test location:  tests/
Test patterns:  [one-sentence description from reading a test file]

## Development

Build command:  tsc
Lint command:   [detected or "none"]
Local dev:      ts-node src/index.ts
```

- [ ] **Step 6: Commit**

```bash
git add github/skills/conventions/SKILL.md github/skills/setup/SKILL.md
git commit -m "feat: replace flat Tech Stack section with Codebase, Testing, Development domain sections"
```

**Engineer review prompt:**
- The "Key modules" field lists at most 5 names. Is 5 the right cap, or should it be "all top-level packages up to 8"? The goal is enough context for a skill to know what modules exist, not an exhaustive list.
- Skills that reference "the test command" or "the test location" from conventions still work because they search by field name, not section name. Confirm by checking each skill's reference to conventions: execution, debugging, TDD, and verification all read `test command` — confirm this field name is unchanged under `## Testing`.

---

## Phase 4: Codebase Search Protocol in Execution and Debugging

**Files in this phase:**
- Modify: `github/skills/execution/SKILL.md`
- Modify: `github/skills/debugging/SKILL.md`

- [ ] **Step 1: Add Codebase Search Protocol section to execution/SKILL.md**

In `github/skills/execution/SKILL.md`, find the `## Verification Gate` section header:

```
### Verification Gate
```

Add the following new section immediately before `### Verification Gate`:

```markdown
## Codebase Search Protocol

When you need to find existing code before implementing a step — understanding a class, finding where a behavior is handled, locating a configuration value:

1. **Formulate a specific query**: name exactly what you're looking for. Bad: "find auth code". Good: "UserAuthService class" or "JWT token validation method".
2. **Run `semantic_search`** with the specific query.
3. **If a relevant result appears in the first page**: use it and stop.
4. **If zero results or all irrelevant**: try once more with a synonym or the exact class/method name as a literal string. Maximum 2 `semantic_search` calls per question.
5. **Fallback after 2 failed searches**: use `grep_search` with the exact class name, method name, or unique constant.
6. **Stop when found**: do not continue searching once you have what you need for the current step.

Apply this protocol any time a step requires understanding existing code before modifying it.

```

- [ ] **Step 2: Add a reference to the protocol in inline mode rule 1**

In `github/skills/execution/SKILL.md`, in Step 2a (Inline Execution), find rule 1:

```
1. Execute each step in order. Do not skip any.
```

Replace with:

```markdown
1. Execute each step in order. Do not skip any. When a step requires reading existing code to understand a module or class, follow the **Codebase Search Protocol** in this skill.
```

- [ ] **Step 3: Trace scenario for execution search protocol**

Mental trace — execution step says "Modify the existing UserRepository to add a `findByEmail` method." The engineer has not told the agent where `UserRepository` is.

Confirm:
1. Agent formulates query: "UserRepository class"
2. Agent runs `semantic_search "UserRepository class"`.
3. If `src/repositories/UserRepository.java` appears in results: agent reads it and proceeds.
4. If not found: agent tries `semantic_search "UserRepository"` (exact class name).
5. If still not found: agent runs `grep_search "UserRepository"` and uses the first result.
6. Agent does not run more than 2 semantic searches before falling back to grep.

- [ ] **Step 4: Add Codebase Search Protocol section to debugging/SKILL.md**

In `github/skills/debugging/SKILL.md`, find `## Step 2: Isolate`:

```
## Step 2: Isolate

Which specific file, method, or line is responsible?

Read the stack trace top-to-bottom. The first line in your own code (not framework or library
code) is the suspect.

State: "The failure originates in `[file]` at `[method]` line [N]."
```

Replace with:

```markdown
## Step 2: Isolate

Which specific file, method, or line is responsible?

Read the stack trace top-to-bottom. The first line in your own code (not framework or library
code) is the suspect.

State: "The failure originates in `[file]` at `[method]` line [N]."

If the stack trace does not point clearly to your code (e.g. the failure is in a framework callback and the root cause is not visible), use the **Codebase Search Protocol** to locate the relevant code:

## Codebase Search Protocol (use only when stack trace is insufficient)

1. **Formulate a specific query**: name the class, method, or behavior you're trying to find. Bad: "find where it breaks". Good: "OrderProcessor.processPayment method".
2. **Run `semantic_search`** with the specific query.
3. **If a relevant result appears**: read it and use it to complete Step 2 (the isolation statement).
4. **If zero results or irrelevant**: try once more with the exact method or class name.
5. **Fallback after 2 failed searches**: use `grep_search` with an exact string from the stack trace.
6. **Stop when isolated**: once you can state "The failure originates in [file] at [method] line [N]", return to Step 3.
```

- [ ] **Step 5: Trace scenario for debugging search protocol**

Mental trace — test failure stack trace shows: `at com.framework.internal.ProxyHandler.invoke()` followed by `at com.example.OrderProcessor.processPayment()`.

Confirm:
1. Agent reads stack trace. Spots `com.example.OrderProcessor.processPayment()` as the first line in own code.
2. Agent states: "The failure originates in `OrderProcessor.java` at `processPayment` line [N]."
3. Search protocol is not needed — stack trace was sufficient.

Mental trace — test failure shows only framework internals with no own-code frame visible:
1. Agent cannot isolate from stack trace alone.
2. Agent invokes search protocol: `semantic_search "OrderProcessor processPayment"`.
3. If found: agent reads the method, identifies the failure line, states isolation.
4. If not found after 2 tries: `grep_search "processPayment"`.

- [ ] **Step 6: Commit**

```bash
git add github/skills/execution/SKILL.md github/skills/debugging/SKILL.md
git commit -m "feat: add Codebase Search Protocol to execution and debugging skills"
```

**Engineer review prompt:**
- The search protocol caps at 2 `semantic_search` calls. Is this the right limit? The cost of a third search is low, but the protocol's value is in preventing open-ended exploration. Confirm the cap is appropriate or adjust to 3 if 2 feels too restrictive.
- The debugging protocol is placed inline within `## Step 2: Isolate`, which extends that section significantly. Confirm this does not make the step feel too long. An alternative is to place it as a separate `## Codebase Search Protocol` section after Step 2 and add a one-line reference from Step 2 ("If the stack trace is insufficient, see the Codebase Search Protocol section below.").

---

## Testing Checklist (run after all phases complete)

- [ ] Open `github/skills/review/SKILL.md` — confirm Output Format section includes the four-question learning debrief after the "No blockers." sign-off
- [ ] Open `github/copilot-instructions.md` — confirm context hygiene persistence rule now has three sub-bullets: handoff file append, log.md append, artifact-index.md append
- [ ] Open `github/skills/conventions/SKILL.md` — confirm `## Tech Stack` is gone; confirm `## Codebase`, `## Testing`, `## Development` sections are present with correct fields
- [ ] Open `github/skills/setup/SKILL.md` — confirm Step 3 includes detection of entry points, test location, test patterns, key modules, local dev command; confirm Step 6 output template has the three new sections with `[detected value]` placeholders
- [ ] Open `github/skills/execution/SKILL.md` — confirm `## Codebase Search Protocol` section exists before `### Verification Gate`; confirm inline rule 1 references the protocol
- [ ] Open `github/skills/debugging/SKILL.md` — confirm `## Codebase Search Protocol` section is embedded within `## Step 2: Isolate`
- [ ] End-to-end trace for knowledge accumulation: PROJ-456 completes review with no blockers. Verify:
  - Debrief block appears after "No blockers." sign-off
  - `docs/workflow/log.md` has entries for each completed phase
  - `docs/workflow/artifact-index.md` has one entry per created artifact across all phases
  - Conventions file (if `/setup` is re-run) has Codebase/Testing/Development sections

## Rollback Plan

- Revert all phase commits: `git revert HEAD~4` (4 commits, one per phase)
- No data migration required — all changes are to template and skill files; existing artifacts and conventions files are unaffected
- `log.md` and `artifact-index.md` files created by this plan can be retained or deleted — they are append-only logs, not required by any skill
