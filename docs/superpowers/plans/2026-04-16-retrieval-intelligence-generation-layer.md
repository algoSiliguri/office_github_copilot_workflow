# Retrieval + Intelligence Layer — Generation Layer Implementation Plan (Plan 4a)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the generation layer — conventions extensions and three generation skills (Job A: codebase indexing, Job B: knowledge extraction, Job C: context packet assembly) — that produce the Markdown index files consumed by the retrieval protocol.

**Architecture:** Three new skills created as Copilot slash commands. Conventions and setup skills extended with three new artifact paths (`codebase/`, `knowledge/`, `context/`) and a maturity threshold field. Each generation skill contains the full algorithm as step-by-step Copilot instructions and writes structured Markdown index files on demand. No infrastructure, no continuous processes — engineer-triggered only.

**Tech Stack:** Markdown only — no code, no build system, no test runner. Verification for each phase is a concrete scenario trace through the written skill text.

**Spec:** `docs/superpowers/specs/2026-04-16-retrieval-intelligence-design.md`

**Follow-up:** Plan 4b covers the retrieval protocol skill and per-skill integrations (brainstorming, spec-writing, planning, execution, review). Plan 4a must be complete before Plan 4b.

**Dependencies:** Plans 1–3 must be implemented first. Job B (Phase 3) reads `artifact-index.md`, `## Discoveries`, `## Amendments`, and `## Design Rationale` sections added by Plans 1–3.

---

## All Files Changed

- `github/skills/conventions/SKILL.md` — Phase 1: add three new artifact path fields + maturity threshold
- `github/skills/setup/SKILL.md` — Phase 1: detect three new directories; populate new fields in output template; add Step 5b to create `module-map.md` starter
- `github/prompts/index.prompt.md` — Phase 1: new prompt routing `/index` sub-commands to Job A and Job B skills
- `github/prompts/context-packet.prompt.md` — Phase 1: new prompt for context packet assembly
- `github/skills/index-codebase/SKILL.md` — Phase 2: new skill implementing Job A (codebase parsing and indexing)
- `github/skills/index-knowledge/SKILL.md` — Phase 3: new skill implementing Job B (knowledge extraction and indexing)
- `github/skills/context-packet/SKILL.md` — Phase 4: new skill implementing Job C (context packet assembly)

---

## Phase 1: Conventions + Setup Extensions

**Files in this phase:**
- Modify: `github/skills/conventions/SKILL.md`
- Modify: `github/skills/setup/SKILL.md`
- Create: `github/prompts/index.prompt.md`
- Create: `github/prompts/context-packet.prompt.md`

- [ ] **Step 1: Add three new artifact path fields to conventions/SKILL.md**

In `github/skills/conventions/SKILL.md`, find the `## Artifact Paths` section (current content):

```
## Artifact Paths (relative to project root)

Specs:          <e.g. docs/workflow/specs/>
Plans:          <e.g. docs/workflow/plans/>
Verifications:  <e.g. docs/workflow/verifications/>
Brainstorms:    <e.g. docs/workflow/brainstorms/>
Handoffs:       <e.g. docs/workflow/handoffs/>
```

Replace with:

```markdown
## Artifact Paths (relative to project root)

Specs:          <e.g. docs/workflow/specs/>
Plans:          <e.g. docs/workflow/plans/>
Verifications:  <e.g. docs/workflow/verifications/>
Brainstorms:    <e.g. docs/workflow/brainstorms/>
Handoffs:       <e.g. docs/workflow/handoffs/>
Codebase Index: <e.g. codebase/>
Knowledge Index: <e.g. knowledge/>
Context Packets: <e.g. context/>
```

- [ ] **Step 2: Add maturity threshold field to conventions/SKILL.md Codebase section**

In `github/skills/conventions/SKILL.md`, find the `## Codebase` section (current content):

```
## Codebase

Language:       <e.g. Java / Python / Go / TypeScript>
Framework:      <e.g. Spring Boot / FastAPI / Gin / Next.js>
Entry points:   <e.g. src/main/java/App.java / cmd/main.go / app/__init__.py>
Key modules:    <e.g. auth, billing, api — names of the main packages or modules>
```

Replace with:

```markdown
## Codebase

Language:       <e.g. Java / Python / Go / TypeScript>
Framework:      <e.g. Spring Boot / FastAPI / Gin / Next.js>
Entry points:   <e.g. src/main/java/App.java / cmd/main.go / app/__init__.py>
Key modules:    <e.g. auth, billing, api — names of the main packages or modules>
Maturity threshold: <default | N — module count above which maturity becomes "mature"; default thresholds: <10=low, 10–30=medium, >30=mature>
```

- [ ] **Step 3: Trace scenario for conventions changes**

Mental trace — team member opens `conventions/SKILL.md` after setup. Confirm:
1. `Codebase Index:`, `Knowledge Index:`, `Context Packets:` fields are present in `## Artifact Paths` with placeholder text matching the format of existing path fields.
2. `Maturity threshold:` is present in `## Codebase` with default explanation in the placeholder.
3. No other lines changed.

- [ ] **Step 4: Update setup/SKILL.md Step 5 to detect three new directories**

In `github/skills/setup/SKILL.md`, find the `## Step 5: Detect Artifact Paths` section (current content):

```
Check if any of these directories exist:
- `docs/specs/` or `docs/workflow/specs/` → use as specs path
- `docs/plans/` or `docs/workflow/plans/` → use as plans path
- `docs/verifications/` or `docs/workflow/verifications/` → use as verifications path
- `docs/brainstorms/` or `docs/workflow/brainstorms/` → use as brainstorms path
- `docs/handoffs/` or `docs/workflow/handoffs/` → use as handoffs path

If none exist, default to:
- Specs: `docs/specs/`
- Plans: `docs/plans/`
- Verifications: `docs/verifications/`
- Brainstorms: `docs/brainstorms/`
- Handoffs: `docs/handoffs/`
```

Replace with:

```markdown
Check if any of these directories exist:
- `docs/specs/` or `docs/workflow/specs/` → use as specs path
- `docs/plans/` or `docs/workflow/plans/` → use as plans path
- `docs/verifications/` or `docs/workflow/verifications/` → use as verifications path
- `docs/brainstorms/` or `docs/workflow/brainstorms/` → use as brainstorms path
- `docs/handoffs/` or `docs/workflow/handoffs/` → use as handoffs path
- `codebase/` → use as codebase index path
- `knowledge/` → use as knowledge index path
- `context/` → use as context packets path

If none exist for the first five, default to:
- Specs: `docs/specs/`
- Plans: `docs/plans/`
- Verifications: `docs/verifications/`
- Brainstorms: `docs/brainstorms/`
- Handoffs: `docs/handoffs/`

For the last three (intelligence layer), always default to these if not found:
- Codebase Index: `codebase/`
- Knowledge Index: `knowledge/`
- Context Packets: `context/`
```

- [ ] **Step 5: Update setup/SKILL.md Step 6 output template to include new fields**

In `github/skills/setup/SKILL.md`, in the Step 6 template block, find the `## Artifact Paths` subsection inside the markdown code fence:

```
## Artifact Paths (relative to project root)

Specs:          [detected value]
Plans:          [detected value]
Verifications:  [detected value]
Brainstorms:    [detected value]
Handoffs:       [detected value]
```

Replace with:

```markdown
## Artifact Paths (relative to project root)

Specs:          [detected value]
Plans:          [detected value]
Verifications:  [detected value]
Brainstorms:    [detected value]
Handoffs:       [detected value]
Codebase Index: [detected value]
Knowledge Index: [detected value]
Context Packets: [detected value]
```

- [ ] **Step 6: Update setup/SKILL.md Step 6 output template Codebase section**

In `github/skills/setup/SKILL.md`, in the Step 6 template block, find the `## Codebase` subsection:

```
## Codebase

Language:       [detected value]
Framework:      [detected value or "none"]
Entry points:   [detected value or "# inferred — verify this"]
Key modules:    [detected value or "# inferred — verify this"]
```

Replace with:

```markdown
## Codebase

Language:       [detected value]
Framework:      [detected value or "none"]
Entry points:   [detected value or "# inferred — verify this"]
Key modules:    [detected value or "# inferred — verify this"]
Maturity threshold: default
```

Note: setup always writes `default` for maturity threshold. Engineers override it manually after setup if needed.

- [ ] **Step 7: Add Step 5b to setup/SKILL.md — create module-map.md starter**

In `github/skills/setup/SKILL.md`, find the line `## Step 6: Write conventions/SKILL.md` and insert this new section immediately before it:

```markdown
## Step 5b: Create module-map.md starter

Check if `[codebase-index-path]/module-map.md` exists (use the detected codebase index path from Step 5).

If it does NOT exist, create it with this exact content:

    # Module Map

    Manual boundary overrides for the codebase index. One row per module.
    Format: `[module-name] | [path(s), comma-separated] | [responsibility]`

    Rows here take precedence over auto-discovery by `/index codebase`.
    Add rows when auto-discovery produces wrong module boundaries.
    Run `/index codebase` after editing this file to regenerate the index.

    <!-- Examples:
    auth | src/auth/, src/session/ | Handles authentication, session tokens, and user identity
    billing | src/billing/service.py, src/billing/models.py | Processes payments and invoices
    -->

If it already exists, do not overwrite it.
```

- [ ] **Step 8: Trace scenario for setup changes**

Mental trace — engineer runs `/setup` on a fresh repo. No `codebase/`, `knowledge/`, or `context/` directories exist.

Confirm:
1. Step 5 detection falls through to defaults: `Codebase Index: codebase/`, `Knowledge Index: knowledge/`, `Context Packets: context/`.
2. Step 5b creates `codebase/module-map.md` with the starter content (since the file doesn't exist).
3. The written `conventions/SKILL.md` contains all three new path fields and `Maturity threshold: default`.
4. The `Codebase` section in the written conventions does NOT contain `<e.g. ...>` placeholder text for the maturity threshold — it says `default`.

- [ ] **Step 9: Create github/prompts/index.prompt.md**

Create the file `github/prompts/index.prompt.md` with this exact content:

```markdown
---
name: index
description: Regenerate the codebase index (Job A), knowledge index (Job B), or both. Accepts sub-commands: codebase, knowledge, all — each optionally with --incremental.
---

Run the appropriate indexing skill based on the argument provided:

- `/index codebase` → Use the `index-codebase` skill. Full regeneration.
- `/index codebase --incremental` → Use the `index-codebase` skill. Incremental mode: only changed modules.
- `/index knowledge` → Use the `index-knowledge` skill. Full regeneration.
- `/index knowledge --incremental` → Use the `index-knowledge` skill. Incremental mode: only changed artifacts.
- `/index all` → Run `index-codebase` skill (full), then `index-knowledge` skill (full).
- `/index all --incremental` → Run `index-codebase` skill (incremental), then `index-knowledge` skill (incremental).

If no argument is provided, say: "Specify a sub-command: `/index codebase`, `/index knowledge`, or `/index all`. Add `--incremental` to update only changed items."

Read `.github/skills/conventions/SKILL.md` to get the codebase index path, knowledge index path, and entry points before starting the relevant skill.
```

- [ ] **Step 10: Create github/prompts/context-packet.prompt.md**

Create the file `github/prompts/context-packet.prompt.md` with this exact content:

```markdown
---
name: context-packet
description: Assemble a context packet for a specific ticket and phase. Usage: /context-packet [ticket-id] [phase-N]
---

Use the `context-packet` skill.

The user provides two arguments: a ticket ID (e.g. PROJ-123) and a phase number (e.g. phase-2).

If either argument is missing, say: "Usage: `/context-packet [ticket-id] [phase-N]` — for example: `/context-packet PROJ-123 phase-2`"

Read `.github/skills/conventions/SKILL.md` to get the plans path, codebase index path, knowledge index path, and context packets path before starting.
```

- [ ] **Step 11: Commit Phase 1**

```bash
git add github/skills/conventions/SKILL.md github/skills/setup/SKILL.md github/prompts/index.prompt.md github/prompts/context-packet.prompt.md
git commit -m "feat: extend conventions and setup for intelligence layer; add index and context-packet prompts"
```

**Engineer review prompt:**
- Does the `Maturity threshold: default` value in the setup output template unambiguously tell a reader that they need to manually override this if they want a custom threshold? Or should it say `Maturity threshold: default  # override: set to N if desired`?
- The `module-map.md` is created at the codebase index path (e.g. `codebase/module-map.md`). Confirm this is correct — the spec says Job A reads it from there before auto-discovery.

---

## Phase 2: Job A — Codebase Indexing Skill

**Files in this phase:**
- Create: `github/skills/index-codebase/SKILL.md`

- [ ] **Step 1: Create the index-codebase skill file**

Create `github/skills/index-codebase/SKILL.md` with this exact content:

```markdown
---
name: index-codebase
description: Parses the source tree and generates codebase/index.md plus one codebase/[module].md per module. Activated by /index codebase or /index codebase --incremental. Never modifies business logic or workflow artifact content.
allowed-tools: read_file, list_dir, file_search, grep_search, create_file, insert_edit_into_file, replace_string_in_file
---

## Metadata

- **Name:** index-codebase
- **Description:** Generates the codebase index — a two-tier Markdown structure mapping modules, responsibilities, dependencies, and entry points. Used by the retrieval protocol during planning.
- **Phase:** Index generation (engineer-triggered)
- **Inputs:** Source tree path (from conventions Entry points); codebase index path (from conventions Codebase Index); optional `--incremental` flag
- **Outputs:** `[codebase-index-path]/index.md` and `[codebase-index-path]/[module].md` per module

## When To Use

Run after initial setup, after structural changes (new modules, deletions, large renames), or on demand. Use `--incremental` after small changes to avoid full re-parse.

Never run before Plans 1–3 have been implemented in the target repo — the knowledge index (Job B) depends on artifact structures those plans add.

## Inputs

- `Entry points:` from `.github/skills/conventions/SKILL.md` — root of the source tree to walk
- `Codebase Index:` path from `.github/skills/conventions/SKILL.md` — where to write output
- `Maturity threshold:` from `.github/skills/conventions/SKILL.md` — override if not `default`
- Optional: `--incremental` flag from the `/index` prompt

---

You are generating a codebase index. Read the source tree, extract structure, and write structured Markdown files. You do NOT modify source files or workflow artifacts.

## Step 1: Read Conventions

Read `.github/skills/conventions/SKILL.md`. Extract:
- `Entry points:` — this is the root path to walk (e.g. `src/`, `cmd/`, `app/`)
- `Codebase Index:` path — where to write output (e.g. `codebase/`)
- `Maturity threshold:` — if not `default`, use the specified N for the mature threshold
- `Language:` — determines file extensions to walk

Store these as working variables: ENTRY_ROOT, INDEX_PATH, MATURITY_OVERRIDE, LANGUAGE.

## Step 2: Check module-map.md for Manual Boundaries

Read `[INDEX_PATH]/module-map.md` if it exists.

Parse each non-comment row: `[module-name] | [path(s)] | [responsibility]`

Store as MANUAL_BOUNDARIES: a list of `{name, paths[], responsibility}`.

Manual boundaries take precedence over auto-discovery in Step 4. Files in manual boundary paths are assigned to their manual module and excluded from auto-discovery.

If module-map.md does not exist, MANUAL_BOUNDARIES = [].

## Step 3: Walk the Source Tree

Use `list_dir` recursively from ENTRY_ROOT. Collect all source files matching the language extension (`.java`, `.py`, `.go`, `.ts`, `.js`, `.rs`, `.kt`, `.rb`, `.cs`).

Skip: test directories (`test/`, `tests/`, `__tests__/`, `spec/`), generated directories (`generated/`, `build/`, `dist/`, `target/`, `node_modules/`, `.gradle/`), and vendor directories (`vendor/`).

Record each file's path. Store as SOURCE_FILES.

## Step 4: Auto-Discover Module Boundaries

Skip files already assigned by MANUAL_BOUNDARIES.

For remaining files, build an import graph:
1. For each file, use `grep_search` to find import statements (pattern: `^import `, `^from `, `^require(`, `^use `).
2. Normalize import paths to file paths within the source tree.
3. Group files by co-import pattern: if files A, B, C are always imported together (every file that imports A also imports B and C, and A/B/C are never individually imported by files outside the group) → assign them to one module.
4. If a file is imported by many other files independently → it is its own module or belongs to a shared-utilities module.
5. Name the auto-discovered module after the deepest common directory in its file set. If files span multiple directories, use the primary directory (most files).

Combine MANUAL_BOUNDARIES + auto-discovered modules → MODULES list, each with `{name, paths[], responsibility: null, source: manual|auto}`.

## Step 5: Infer Responsibility for Each Module

For each module in MODULES where `responsibility = null` (auto-discovered or manual with no responsibility):

Check in this priority order — use the first one that produces a non-empty result:

1. **Module-level docstring:** Read the primary file (file with the most public exports or the `__init__.py` / `index.ts` / `mod.rs`). Look for a leading `"""..."""`, `'''...'''`, or `/* ... */` block. Extract the first sentence.
2. **README in module directory:** Check if a `README.md` exists in the module's primary directory. If yes, read the first paragraph.
3. **Module comment:** In the primary file, look for a line matching `# Module:`, `# Responsibility:`, `// Module:`, or `// Responsibility:`. Extract the text after the colon.
4. **Public interface names:** List the public class, function, and method names exported by the module. Synthesise a one-sentence responsibility from their names (e.g. classes named `UserRepository`, `UserRepositoryImpl` → "Manages user data persistence").
5. **Fallback:** Set responsibility to `# inferred — verify this` and mark the module as `pending`.

For **manual** boundaries where responsibility was specified in module-map.md, use that directly — do not run the priority check.

Set each module's `pending` flag:
- `pending = true`: responsibility came from sources 4 or 5
- `pending = false`: responsibility came from sources 1, 2, 3, or manual boundary

## Step 6: Detect Entry Points for Each Module

For each module, scan its files for entry point patterns. An entry point is a class or function that is called from outside the application (by framework, scheduler, queue consumer, or CLI).

Detection patterns (check class names AND annotations/decorators):

**Class naming patterns:**
- `*Controller`, `*Handler`, `*Job`, `*Consumer`, `*Worker`, `*CLI`, `*Server`, `*Router`, `*Listener`

**Annotation/decorator patterns:**
- Java/Kotlin: `@RestController`, `@Controller`, `@Scheduled`, `@KafkaListener`, `@EventListener`, `@RabbitListener`
- Python: `@app.route`, `@router.get`, `@router.post`, `@celery.task`, `@click.command`
- Go: `func main()`, `http.HandleFunc`, `mux.HandleFunc`
- TypeScript: `@Controller()`, `@Get()`, `@Post()`, exported `router.*` calls

For each detected entry point, record: `{class_or_function, method_or_route, file_path}`.

Store as the module's ENTRY_POINTS list.

## Step 7: Map Dependencies and Annotate Types

For each module M, find what other modules it imports (using the import graph from Step 4, resolved to module names).

For each dependency relationship (M → D), annotate the dependency type by inspecting the method or function calls from M into D:

| Method name prefix | Assigned type |
|---|---|
| `get`, `find`, `fetch`, `load`, `query` | `read` |
| `save`, `update`, `delete`, `create`, `publish`, `write` | `write` |
| Async markers: `@Async`, `async def`, goroutine call, message queue/event bus invocation | `async` |
| None of the above | `sync` |

If the type was determined from method name inspection: mark `confidence: inferred`.
If the type was declared in module-map.md: mark no confidence suffix (confirmed).

Record each dependency as: `{module: D, type: read|write|async|sync, confidence: confirmed|inferred, annotation: [one-sentence relationship description]}`.

Derive the annotation from what M does with D (e.g. "reads user records for authentication checks").

## Step 8: Compute Reach Metrics

**Reach (direct):** For each module M, count how many other modules have M in their dependency list. This is the inbound edge count.

**Downstream Reach (transitive) per Dependent:** For each module D that depends on M, run a BFS from M following outbound edges (M's dependencies, their dependencies, etc.), counting distinct reachable modules. Store this count in M's Dependents entry for D.

Record `{module: M, reach_direct: N, dependents: [{module: D, downstream_reach: N}]}`.

## Step 9: Compute Quadrant and Risk Status

For each module, compute:

**Quadrant** (derived from Reach × total signals — signals are 0/0 on first run, so use 0):
- Reach above median AND signals above median → `critical-core`
- Reach below median AND signals above median → `sleeper-risk`
- Reach above median AND signals below or equal to median → `stable-workhorse`
- Reach below or equal to median AND signals below or equal to median → `peripheral`

On first run, all modules have 0 signals, so all are `stable-workhorse` (high reach) or `peripheral` (low reach). Quadrant is updated by Job B after signal density is populated.

**Risk status:**
- `active` if module has any recent signals (0 on first run → not active)
- `historical` if recent = 0 AND total ≥ 1
- `stable` if total signals = 0

On first run, all modules start as `stable`.

## Step 10: Compute Source Hash and Maturity

**Source hash:**
1. For every file in SOURCE_FILES, get its path and modification time.
2. Sort the list of `"path:mtime"` strings alphabetically.
3. Compute MD5 or SHA-256 of the sorted, newline-joined string.
4. Truncate to first 12 characters for the header.

**Module count:** len(MODULES).

**Maturity:**
- If MATURITY_OVERRIDE is not `default`: use the override N. Modules < N = low, N to 2N = medium, > 2N = mature. (Scale: if override = 20, then <20=low, 20–40=medium, >40=mature.)
- If MATURITY_OVERRIDE = `default`: use fixed thresholds: < 10 = low, 10–30 = medium, > 30 = mature.

## Step 11: Write codebase/index.md

Write `[INDEX_PATH]/index.md` with this exact structure. Fill in every field — no placeholder text:

    <!-- generated: YYYY-MM-DD | modules: N | source-hash: [12-char hash] | maturity: low|medium|mature | stale: false -->

    # Codebase Index

    | Module | Path | Responsibility | Reach (direct) | Signals (recent/total) | Quadrant | Risk Status |
    |---|---|---|---|---|---|---|
    | [module-name] | [primary path] | [responsibility or "pending — see module page"] | N | 0/0 | [quadrant] | [risk-status] |

    _(One row per module, sorted by Reach (direct) descending.)_

Rules:
- If `pending = true`, write `pending — see module page` in the Responsibility column.
- `Signals (recent/total)` is `0/0` on first run. Job B updates this column.
- `stale: false` on first run. Updated to `true` when source hash mismatch is detected on the next run.

## Step 12: Write codebase/[module].md for Each Module

For each module, write `[INDEX_PATH]/[module-name].md` where module-name is the module's name lowercased with spaces replaced by hyphens.

Write with this exact structure:

    # [Module Name]
    _Path: `[primary path]` | Generated: YYYY-MM-DD | Reach (direct): N | Quadrant: [quadrant] ([risk-status])_

    ## Responsibility
    [What this module owns exclusively. What must not be implemented elsewhere.]
    _(Leave blank if pending = true — content is in Pending Validation below.)_

    ## Pending Validation
    _(Present only when pending = true. Empty once an engineer promotes it to ## Responsibility.)_
    [Inferred responsibility — verify and move to ## Responsibility when correct]

    ## Entry Points
    _(Classes, jobs, handlers that route calls into this module — with the specific method or route.)_
    [One line per entry point: `ClassName.methodName` or `GET /route/path` — file: `path/to/file`]
    _(If none detected: "None detected — add manually if applicable.")_

    ## Public Interface
    _(Key classes, methods, and types exposed to other modules.)_
    [One line per public export: `ClassName` / `functionName(params) → ReturnType` — [one-sentence purpose]]
    _(Populate from the top-level exports of the module's primary files.)_

    ## Dependencies
    - `[DependencyModule]` (type: [read|write|async|sync][, confidence: inferred]) — [relationship annotation]
    _(If no dependencies: "None.")_

    ## Dependents
    - `[DependentModule]` — [why it depends on this module] | Downstream Reach (transitive): N
    _(If no dependents: "None.")_

    ## Known Constraints
    _(Observed limitations — non-negotiable. Override requires architectural discussion.)_
    _(Populated by /index knowledge. Leave blank on first run.)_

    ## Decisions
    _(Chosen designs — override allowed with explicit justification recorded in spec.)_
    _(Populated by /index knowledge. Leave blank on first run.)_

## Step 13: Incremental Mode (only when --incremental flag is set)

If running in incremental mode:

1. Read the existing `[INDEX_PATH]/index.md` header. Extract `source-hash`.
2. Recompute the source hash (Step 10). If hashes match — no source files changed. Report: "No source changes detected. Index is up to date." Stop.
3. If hashes differ: identify which source files changed (by comparing stored mtime values with current mtime values for each file in the index). Recompute modules affected by those files. Regenerate only those module pages and their index rows.
4. Update the index header with the new hash, generation date, and `stale: false`.
5. Leave all other module pages and index rows unchanged.

If `[INDEX_PATH]/index.md` does not exist, run full mode (Steps 1–12) regardless of the incremental flag.

## Step 14: Report

After writing all files, say:

> "Codebase index generated at `[INDEX_PATH]/`:
>
> - `index.md` — [N] modules, maturity: [level], hash: [12-char hash]
> - [N] module pages written
> - Modules pending validation: [list module names where pending=true, or "none"]
> - Next: run `/index knowledge` to extract historical signals, or `/brainstorm` to start a ticket."

---

## Output Format

- `[codebase-index-path]/index.md` — Tier 1 index with header and table
- `[codebase-index-path]/[module].md` — one Tier 2 page per module
- No modifications to source files or workflow artifacts

## Dependencies

- `.github/skills/conventions/SKILL.md` — entry points, codebase index path, maturity threshold
- `[codebase-index-path]/module-map.md` — manual boundary overrides (optional)

## Handoff

After running this skill, run `/index knowledge` to populate Known Constraints and Decisions in module pages, and to compute signal density. Without Job B, the `Signals` column stays at `0/0` and quadrants are unreliable.
```

- [ ] **Step 2: Trace Scenario 1 — Full lifecycle on a mature repo**

Mental trace: A repo has 15 modules and 10 completed tickets. No `--incremental` flag.

Confirm:
1. Step 2 reads module-map.md. Suppose 2 manual boundaries exist (e.g. `auth`, `billing`). Their responsibilities come directly from module-map.md; `pending = false`.
2. Step 4 auto-discovers 13 additional modules from import patterns.
3. Step 5 infers responsibilities for the 13 auto-discovered modules. Suppose 4 fall through to priority 4 (interface names) or 5 (fallback) → `pending = true`.
4. Step 10 computes maturity: 15 modules → `medium` (10–30 range).
5. Step 11 writes `codebase/index.md` with 15 rows. The 4 pending modules show `pending — see module page` in the Responsibility column.
6. Step 12 writes 15 module pages. The 4 pending ones have `## Pending Validation` populated; `## Responsibility` is blank.
7. Step 14 reports: "15 modules, maturity: medium, 4 modules pending validation: [names]."

Check: `codebase/index.md` contains the `<!-- generated: ... | modules: 15 | source-hash: ... | maturity: medium | stale: false -->` header. This satisfies **R1** from the spec.

- [ ] **Step 3: Trace Scenario 5 — Greenfield behavior (low maturity)**

Mental trace: Repo with 6 modules (maturity = low after Step 10).

Confirm:
1. `maturity: low` is written in the index header.
2. The retrieval protocol (Plan 4b) reads this header and skips the codebase protocol for low maturity — it will fall through to codebase search protocol. This skill itself does not enforce that; it simply writes the correct header value.

- [ ] **Step 4: Trace Scenario 7 — Stale index detection**

Mental trace: Job A ran yesterday. Today a source file was modified. Engineer runs `/index codebase --incremental`.

Confirm:
1. Step 13 reads existing `source-hash` from the index header.
2. Recomputes hash — differs (a file's mtime changed).
3. Identifies the affected module(s) and regenerates only those pages.
4. Writes updated index with new hash, `stale: false`.

Now trace what happens if the engineer had NOT run incremental before the next planning session:
- The index header still has the old hash.
- The retrieval protocol (Plan 4b) reads the header; it does not recompute the hash.
- Hash staleness is detected on the NEXT Job A run (not by the retrieval protocol itself).
- The retrieval protocol reads `stale: false` (still from the last run) — staleness detection is the responsibility of the generation step, not the retrieval step.
- This is correct: **R1** says the skill reading the header can determine whether to run the protocol — it cannot determine staleness without running Job A first. The retrieval protocol will show an age warning if the index is old (Plan 4b).

- [ ] **Step 5: Commit Phase 2**

```bash
git add github/skills/index-codebase/SKILL.md
git commit -m "feat: add index-codebase skill (Job A) — codebase parsing and index generation"
```

**Engineer review prompt:**
- In Step 7 (dependency type annotation), the heuristic is based on method name prefixes. For a module that calls `repository.findAll()` → `find` prefix → `read`. For `eventBus.publish()` → `publish` prefix → `write`. But `publish` could be async in some systems. If this produces wrong annotations, engineers should add the corrected type to module-map.md and re-run. Is this fallback path clear from the skill text?
- The `Downstream Reach (transitive)` in Step 8 is computed per Dependent entry in M's page (how far downstream each dependent is). Confirm: if module A depends on M and A has 5 downstream dependents, then M's Dependents entry for A shows `Downstream Reach (transitive): 5`. This is what the spec says (BFS count written to each Dependents entry).

---

## Phase 3: Job B — Knowledge Indexing Skill

**Files in this phase:**
- Create: `github/skills/index-knowledge/SKILL.md`

- [ ] **Step 1: Create the index-knowledge skill file**

Create `github/skills/index-knowledge/SKILL.md` with this exact content:

```markdown
---
name: index-knowledge
description: Reads workflow artifacts (plans, specs, reviews) to extract decisions, constraints, and patterns. Writes knowledge/index.md and knowledge/[topic].md pages. Updates Known Constraints and Decisions in module pages. Activated by /index knowledge or /index knowledge --incremental.
allowed-tools: read_file, list_dir, file_search, grep_search, create_file, insert_edit_into_file, replace_string_in_file
---

## Metadata

- **Name:** index-knowledge
- **Description:** Extracts historical signals from workflow artifacts and writes a weighted knowledge index. Updates module pages with constraints and decisions. Requires the codebase index to exist.
- **Phase:** Index generation (engineer-triggered, typically after closing each ticket)
- **Inputs:** Artifact index path (from conventions); codebase index path; optional `--incremental` flag
- **Outputs:** `[knowledge-index-path]/index.md`, `[knowledge-index-path]/[topic].md` per topic, and updated `## Known Constraints` / `## Decisions` sections in module pages

## When To Use

Run after closing each ticket (use `--incremental`). Run before starting a large ticket (full run) to ensure knowledge is current. Requires the codebase index (`/index codebase`) to exist first. Do not run before Plans 1–3 are implemented — the artifact structures are not present.

## Inputs

- `Plans:` path and `Specs:` path from `.github/skills/conventions/SKILL.md`
- `Codebase Index:` path and `Knowledge Index:` path from conventions
- Optional: `--incremental` flag

---

You are extracting knowledge from workflow artifacts. You read plans, specs, and review files and write a structured knowledge index. You do NOT modify source files.

## Step 1: Read Conventions

Read `.github/skills/conventions/SKILL.md`. Extract:
- `Plans:` path (PLANS_PATH)
- `Specs:` path (SPECS_PATH)
- `Codebase Index:` path (CODEBASE_PATH)
- `Knowledge Index:` path (KNOWLEDGE_PATH)

## Step 2: Read Artifact Index

Read `[PLANS_PATH]/artifact-index.md` (created by Plan 3). This file lists all known plan, spec, and review artifacts with their paths and ticket IDs.

If artifact-index.md does not exist, fall back to scanning `[PLANS_PATH]/` and `[SPECS_PATH]/` directly using `list_dir`. Process all `.md` files found.

Store the full list of artifact paths as ARTIFACTS.

## Step 3: Build Source Routing Table

For each artifact in ARTIFACTS, classify its content type by reading its frontmatter and section headers:

| Condition | Extract | Source type |
|---|---|---|
| File has `phase: plan` in frontmatter AND contains `## Discoveries` section | Content of `## Discoveries` | discovery |
| File has `phase: plan` in frontmatter AND contains `## Amendments` section | Content of `## Amendments` | amendment |
| File has `phase: spec` in frontmatter AND contains `## Design Rationale` section | Content of `## Design Rationale` | decision |
| File has `phase: review` in frontmatter AND contains `BLOCKER` flagged items | The BLOCKER items | blocker |
| File has `phase: plan` AND contains failed mitigations or rejected fixes (look for `[failed-mitigation]` or `[rejected-fix]` tags, or language like "mitigation failed" / "fix rejected") | Those entries | discovery (tagged) |

For each extracted entry, record: `{artifact_path, ticket_id, type, content, date}`.
- `ticket_id`: from frontmatter `ticket:` field, or parsed from file name `YYYY-MM-DD-[TICKET-ID]-...`
- `date`: from frontmatter `created:` field, or file modification date

Store all entries as RAW_ENTRIES.

## Step 4: Associate Entries with Modules

For each entry in RAW_ENTRIES, determine which module it belongs to:

1. **Exact class/module name match:** Does the entry text mention a class or module name that appears in `[CODEBASE_PATH]/index.md`'s Module column? If yes, assign to that module.
2. **File path match:** Does the entry text mention a file path that maps to a module (via the Path column in the codebase index)? If yes, assign to that module.
3. **No match:** Mark as `module: unresolved`. These entries are tracked separately in `## Unresolved Entries` in the knowledge index.

Store as ROUTED_ENTRIES with each entry having a `module` field (module name or "unresolved").

## Step 5: Route to Correct Destination

Apply these routing rules to determine where each entry goes:

| Source type | Primary destination | Secondary destination |
|---|---|---|
| discovery | Knowledge index | Module page `## Known Constraints` |
| amendment (changed an observed limit) | Knowledge index | Module page `## Known Constraints` |
| amendment (changed a design choice) | Knowledge index | Module page `## Decisions` |
| decision (chosen) | Module page `## Decisions` only | — |
| decision (rejected) | Module page `## Decisions` only (prefixed "Rejected:") | — |
| blocker | Knowledge index | Module page `## Known Constraints` |
| discovery [failed-mitigation] | Knowledge index | Module page `## Known Constraints` (tagged `[failed-mitigation]`) |
| discovery [rejected-fix] | Knowledge index | Module page `## Known Constraints` (tagged `[rejected-fix]`) |

**Amendment routing rule:** Read the amendment text. If it changed a numeric limit, rate, timeout, or capacity → `## Known Constraints`. If it changed an architectural pattern or design approach → `## Decisions`.

Entries that go to the knowledge index are further grouped by topic (Step 6).
Entries that go to module pages are written directly to the relevant module's section (Step 8).

## Step 6: Normalise Topics

Group knowledge-index-bound entries into topics. A topic represents a single root cause or invariant failure mode — not a symptom.

**Initial grouping:** Group entries by co-occurring module names + overlapping keywords. Entries that mention the same module(s) and share ≥ 2 keywords (excluding common words like "the", "a", "was") → candidate for the same topic.

**Name the topic:** Use the root cause as the topic name, not the symptom (e.g., topic name: `token-invalidation-lag`, not `users-getting-logged-out`).

**Flag merge and split candidates:**
- **Merge candidate:** Two existing topics that share the same module co-occurrence AND have overlapping keywords → flag both as `merge-candidate`. Do not auto-merge.
- **Split candidate:** A topic where some entries reference modules with no dependency relationship AND the entries have non-overlapping keywords → flag as `split-candidate`. Do not auto-split.

Store as TOPICS: a list of `{name, entries[], merge_candidate: bool, split_candidate: bool}`.

## Step 7: Compute Weights for Each Topic

For each topic, compute weight from its entries using this algorithm:

**Define recent window:** The last 5 tickets by ticket ID sort order, OR entries from the last 90 days — whichever captures more entries.

**Weight computation (evaluate in order — first match wins):**
1. Any entry in this topic has `type = blocker` → **HIGH**
2. Recurrence ≥ 3 (entry count across distinct tickets) AND at least one entry is recent → **HIGH**
3. Recurrence ≥ 3 AND no recent entries → **MEDIUM** (add note: "historical")
4. Recurrence = 2 → **MEDIUM**
5. Recurrence = 1 AND type = amendment → **MEDIUM**
6. Otherwise → **LOW**

**Status flags (additive):**
- `instability`: amendments on this topic ≥ 2 → add `unstable` to status
- `pattern-candidate`: recurrence ≥ 3 AND no `## Pattern` section exists in the topic page yet → add `pattern-candidate` to status
- `stale-candidate`: weight = LOW AND no entry in the last 10 tickets → increment the knowledge index header's `stale-candidates` counter

**Base status:** `active` if any recent entry exists; `historical` if no recent entry but total > 0.

Final status is a combination, e.g., `active, pattern-candidate` or `historical, unstable`.

## Step 8: Update Module Pages with Constraints and Decisions

For each ROUTED_ENTRY destined for a module page, update the module's `[CODEBASE_PATH]/[module].md` file:

**For `## Known Constraints` entries:**
Append to the `## Known Constraints` section:
```
- [YYYY-MM-DD] [TICKET-ID]: [constraint statement from entry] [tag if applicable]
```

**For `## Decisions` entries:**
For chosen decisions, append to `## Decisions`:
```
- [YYYY-MM-DD] [TICKET-ID]: [decision statement]
  Source: `[artifact-path]`
```

For rejected alternatives (from `## Design Rationale` rejected entries), append:
```
- [YYYY-MM-DD] [TICKET-ID]: Rejected: [alternative] — [reason]
  Source: `[artifact-path]`
```

**Decision supersession:** If an existing `## Decisions` entry in a module page is about the same design choice as a new incoming decision that overrides it, add to the existing entry:
```
  Status: superseded (see [NEW-TICKET-ID])
```
Do this when the override chain length is ≥ 2 (i.e., this entry has already been superseded once before, or the new entry explicitly overrides a prior decision).

## Step 9: Write knowledge/index.md

Compute totals:
- `topics`: count of TOPICS
- `pattern-candidates`: count of topics with `pattern-candidate` in status
- `stale-candidates`: count accumulated in Step 7
- `unresolved`: count of entries in ROUTED_ENTRIES where module = "unresolved"
- `recent-window`: "last-5-tickets OR 90-days"

Write `[KNOWLEDGE_PATH]/index.md`:

    <!-- generated: YYYY-MM-DD | topics: N | recent-window: last-5-tickets OR 90-days | pattern-candidates: N | stale-candidates: N | unresolved: N -->

    # Knowledge Index

    | Topic | Module(s) | Weight | Recurrence | Recent | Impact | Last Ticket | Status |
    |---|---|---|---|---|---|---|---|
    | [topic-name] | [module list] | HIGH|MEDIUM|LOW | N | yes|no | discovery|amendment|blocker | [TICKET-ID] | [status flags] |

    _(High-weight first, then alphabetical within weight tier.)_

    ## Unresolved Entries

    _(Entries that could not be associated with a known module. Resolve by adding the module to
    the codebase index or correcting the module name reference in the source artifact.)_

    | Date | Ticket | Type | Description |
    |---|---|---|---|
    | [YYYY-MM-DD] | [TICKET] | [type] | [description] |

Rules:
- All seven header fields (`topics`, `recent-window`, `pattern-candidates`, `stale-candidates`, `unresolved` plus `generated` and the implied fields) must always be present. Never omit any field. This satisfies **R7**.
- If no unresolved entries, write "None." under `## Unresolved Entries`.

## Step 10: Write knowledge/[topic].md for Each Topic

For each topic in TOPICS, write `[KNOWLEDGE_PATH]/[topic-name].md`:

    # [Topic Name]
    _(Topic represents a single root cause or invariant failure mode — not a symptom.)_
    _Modules: [module list] | Weight: [HIGH|MEDIUM|LOW] | Recurrence: N | Status: [status flags]_

    ## Summary
    [1–2 sentence synthesis of the root cause and its observable effect, written from the entries.]

    ## Pattern
    _(Present only when status includes "pattern-candidate" AND an engineer has confirmed the pattern.
    Leave this section absent on first write — it is added by the engineer at review debrief.)_

    ## Entries
    _(High-weight entries first, then chronological within weight tier.)_
    - [YYYY-MM-DD] [TICKET-ID] | [type] | [Weight] | [description]
    _(Add [failed-mitigation] or [rejected-fix] tag on the same line where applicable.)_

    ## Related Modules
    - [`[Module]`](../codebase/[module].md) — [one sentence: how this module relates to this topic]

If the topic is flagged `merge-candidate`, add at the top (before the first heading):
```
> **Merge candidate:** This topic may overlap with [other-topic]. Review at next debrief — options: Merge, Retain as-is.
```

If the topic is flagged `split-candidate`, add at the top:
```
> **Split candidate:** This topic may cover two independent failure modes. Review at next debrief — options: Split into [A] and [B], Retain as-is.
```

## Step 11: Update Signal Density in Codebase Index

After writing all knowledge pages, update the `Signals (recent/total)` column in `[CODEBASE_PATH]/index.md` for each module:

For each module row, count:
- `total`: how many knowledge index entries (across all topics) are associated with this module
- `recent`: how many of those entries fall within the recent window

Update the cell from `0/0` to `recent/total`.

Also recompute the Quadrant for each module now that signals are available:
- For each module, determine if its `total signals` is above or below the median across all modules.
- Determine if its `Reach (direct)` is above or below the median.
- Assign quadrant per the 2×2 matrix (critical-core, sleeper-risk, stable-workhorse, peripheral).

Update the Quadrant column in `codebase/index.md`.

## Step 12: Incremental Mode (only when --incremental flag is set)

If running in incremental mode:

1. Read `[KNOWLEDGE_PATH]/index.md` header. Note the `generated:` date.
2. Check each artifact in ARTIFACTS: compare its modification time or content hash against a stored value in `[KNOWLEDGE_PATH]/.artifact-hashes.md` (a simple key-value file: `artifact-path | hash`).
3. Process only artifacts whose content has changed since the last run.
4. For changed artifacts: re-extract their entries, re-route, re-weight their topics, and update affected topic pages and module pages.
5. Recalculate header totals (topics, pattern-candidates, stale-candidates, unresolved).
6. Write updated `[KNOWLEDGE_PATH]/.artifact-hashes.md` with new hashes.

If `[KNOWLEDGE_PATH]/index.md` does not exist, run full mode (Steps 1–11) regardless of the flag.

**Important:** A full rebuild is required when topic normalizations are confirmed (merge/split at debrief) or when module associations are manually corrected. Incremental mode does not re-evaluate topic groupings.

## Step 13: Report

After writing all files, say:

> "Knowledge index generated at `[KNOWLEDGE_PATH]/`:
>
> - `index.md` — [N] topics, [N] pattern-candidates, [N] stale-candidates, [N] unresolved entries
> - [N] topic pages written
> - Signal density updated in `[CODEBASE_PATH]/index.md` for [N] modules
> - Pattern candidates: [list topic names, or "none"]
> - Unresolved entries: [N] — [list ticket/type pairs if N > 0, or "none"]
> - Next: `/context-packet [ticket-id] [phase-N]` to assemble a context packet, or `/brainstorm` to start a ticket."

---

## Output Format

- `[knowledge-index-path]/index.md` — Tier 1 knowledge index with header and table
- `[knowledge-index-path]/[topic].md` — one Tier 2 page per topic
- `[knowledge-index-path]/.artifact-hashes.md` — incremental mode hash store
- Updated `## Known Constraints` and `## Decisions` sections in affected module pages

## Dependencies

- `.github/skills/conventions/SKILL.md` — artifact paths
- `[codebase-index-path]/index.md` — module list for association; must exist before running this skill
- Plans 1–3 artifacts — `artifact-index.md`, `## Discoveries`, `## Amendments`, `## Design Rationale` sections

## Handoff

After running this skill, signal density and quadrants in the codebase index are updated, and module pages have Known Constraints and Decisions populated. The system is now ready for retrieval protocol use during planning. Run `/index knowledge --incremental` after each ticket closes.
```

- [ ] **Step 2: Trace Scenario 1 — Knowledge extraction from 10 completed tickets**

Mental trace: 10 plan files exist, each with `## Discoveries` and `## Amendments`. 3 spec files with `## Design Rationale`. 2 review files with BLOCKER flags.

Confirm:
1. Step 3 reads all 15 artifacts. Finds discoveries, amendments, design rationale, blockers.
2. Step 4 associates entries with modules via module name mentions.
3. Step 6 groups into topics. Suppose 4 topics emerge. Suppose `token-invalidation-lag` has 3 entries across 3 tickets → recurrence = 3.
4. Step 7 computes weight: `token-invalidation-lag` has recurrence ≥ 3 AND a recent entry → **HIGH**. Status: `active, pattern-candidate`.
5. Step 9 writes knowledge/index.md with `pattern-candidates: 1`.
6. Step 10 writes `knowledge/token-invalidation-lag.md` with the `> **Merge candidate:**` note if flagged, or without if clean.
7. Step 11 updates `Signals (recent/total)` in `codebase/index.md` for each module. Modules involved in the topic get counts like `3/5`.

Check: the knowledge index header contains all 7 required fields (`generated`, `topics`, `recent-window`, `pattern-candidates`, `stale-candidates`, `unresolved`). This satisfies **R7**.

- [ ] **Step 3: Trace amendment routing rule**

Mental trace: an amendment says "increased connection pool size from 10 to 50 for the database module." This changed an observed limit (connection count). Route: `## Known Constraints` in the database module page.

Another amendment says "switched from polling to event-driven for the notification module." This changed an architectural pattern. Route: `## Decisions` in the notification module page.

Confirm the routing rule in Step 5 distinguishes these correctly based on the "changed an observed limit" vs "changed a design choice" heuristic.

- [ ] **Step 4: Commit Phase 3**

```bash
git add github/skills/index-knowledge/SKILL.md
git commit -m "feat: add index-knowledge skill (Job B) — knowledge extraction and indexing"
```

**Engineer review prompt:**
- The `.artifact-hashes.md` file in the knowledge path stores hashes for incremental mode. This is an implementation detail file, not a knowledge page. Should it be listed in `codebase/index.md` or `knowledge/index.md`? It should NOT be — it is only read by the skill, not by the retrieval protocol. Confirm this is clear from the skill text.
- Step 6 groups entries by keyword overlap. For a large, mature repo with many topics, this grouping heuristic may produce false positives (merge candidates that don't actually share a root cause). The `merge-candidate` flag surfaces this for human review at the debrief. Is the path from flag → debrief → resolution clear? (It is described in the review skill update in Plan 4b.)

---

## Phase 4: Job C — Context Packet Assembly Skill

**Files in this phase:**
- Create: `github/skills/context-packet/SKILL.md`

- [ ] **Step 1: Create the context-packet skill file**

Create `github/skills/context-packet/SKILL.md` with this exact content:

```markdown
---
name: context-packet
description: Assembles a context packet for a specific ticket and phase by loading condensed module pages and high-weight knowledge entries. Writes context/[ticket-id]/phase-[N]-context.md. Triggered by /context-packet [ticket-id] [phase-N].
allowed-tools: read_file, list_dir, file_search, grep_search, create_file, insert_edit_into_file
---

## Metadata

- **Name:** context-packet
- **Description:** Pre-assembles execution context for a specific plan phase — condensed module information and high-weight knowledge signals — so the execution agent does not need to re-read the full codebase index during each phase.
- **Phase:** Pre-execution (run after plan is written, before execution begins)
- **Inputs:** Ticket ID, phase number (N), plan file path (inferred from conventions)
- **Outputs:** `[context-packets-path]/[ticket-id]/phase-[N]-context.md`

## When To Use

Run after a plan is finalised and before starting execution. Only generates packets when all three trigger conditions are met (checked in Step 2). If conditions are not met, report why and suggest running without a packet (falling back to Plan 3 codebase search protocol).

## Inputs

- Ticket ID (e.g. `PROJ-123`)
- Phase number (e.g. `phase-2`)
- Paths from `.github/skills/conventions/SKILL.md`: Plans, Codebase Index, Knowledge Index, Context Packets

---

You are assembling a context packet for a specific plan phase. You read the plan, map files to modules, load condensed knowledge, and write a structured packet file. You do NOT modify source files or workflow artifacts.

## Step 1: Read Conventions and Locate the Plan

Read `.github/skills/conventions/SKILL.md`. Extract PLANS_PATH, CODEBASE_PATH, KNOWLEDGE_PATH, CONTEXT_PATH.

Locate the plan file for the given ticket ID: search PLANS_PATH for a file whose name contains the ticket ID and whose frontmatter `ticket:` matches. Read the plan file in full.

If no plan file is found for the ticket ID, stop and say: "No plan file found for [ticket-id] in [PLANS_PATH]. Ensure the plan exists before generating a context packet."

## Step 2: Check Trigger Conditions

Evaluate all three conditions. All must be true to proceed:

1. **Repo maturity:** Read `[CODEBASE_PATH]/index.md` header. Is `maturity: medium` or `maturity: mature`? If `maturity: low` → stop: "Maturity is low. Context packets are not generated for low-maturity repos. Use codebase search protocol (Plan 3) instead."

2. **Execution mode:** Does the plan file contain `> **Execution mode:** phased`? If `inline` or absent → stop: "Plan is inline execution mode. Context packets are for phased plans only."

3. **Phase file count:** Find the section for the requested phase (e.g. `## Phase 2:`) in the plan. Count the files listed in its `**Files in this phase:**` block. Are there ≥ 4 files? If < 4 → stop: "Phase [N] has [count] files. Context packets are generated for phases with ≥ 4 files only."

If all three conditions pass, continue.

## Step 3: Extract Phase File Manifest

From the plan's phase section, extract the exact list of files listed under `**Files in this phase:**`. Store as PHASE_FILES.

Example: if Phase 2 lists:
```
- Create: `src/auth/TokenValidator.java`
- Modify: `src/auth/AuthService.java:45-78`
- Modify: `src/auth/AuthController.java`
- Test: `tests/auth/TokenValidatorTest.java`
```
PHASE_FILES = [`src/auth/TokenValidator.java`, `src/auth/AuthService.java`, `src/auth/AuthController.java`, `tests/auth/TokenValidatorTest.java`]

Strip line ranges (`:45-78`) — use only the file path.

## Step 4: Map Files to Modules

For each file in PHASE_FILES, find its module by:
1. Reading `[CODEBASE_PATH]/index.md` Path column — find the row whose Path value is a prefix of (or exact match for) the file path.
2. If matched: record `{file, module}`.
3. If not matched: record `{file, module: "unresolved"}`.

Store as FILE_MODULE_MAP. Collect the distinct resolved module names as PHASE_MODULES.

## Step 5: Load Condensed Module Pages

For each module in PHASE_MODULES (unresolved excluded), read `[CODEBASE_PATH]/[module].md`.

Extract (condensed view — do not include the full page text):
- `## Responsibility` — full content
- `## Entry Points` — full content
- `## Public Interface` — full content
- `## Dependencies` — full content (all lines)
- `## Known Constraints` — full content (all lines)
- `## Decisions` — full content (all lines)

Do NOT include `## Pending Validation` or `## Dependents` in the condensed view (too verbose for packet).

Store as MODULE_CONDENSED: a list of `{module, responsibility, entry_points, public_interface, dependencies, known_constraints, decisions}`.

## Step 6: Load High-Weight Knowledge Entries

Read `[KNOWLEDGE_PATH]/index.md`. Filter rows to topics where:
- `Module(s)` column contains at least one module from PHASE_MODULES, AND
- `Weight` column is `HIGH` or `MEDIUM`

Exclude LOW-weight entries unless no MEDIUM or HIGH entries exist for any PHASE_MODULE (in that case, include the best LOW-weight entries for those modules only).

Sort: HIGH first, then MEDIUM; within each tier: active before historical; within status: recent before stale.

Apply knowledge loading budget from the retrieval protocol:
- During execution: loading is via context packet only — no additional budget applied here. Include all HIGH and MEDIUM entries for phase modules.

For each selected topic, read `[KNOWLEDGE_PATH]/[topic].md`. Extract: `## Summary` and `## Pattern` (if present). Do NOT include the full `## Entries` list in the packet — summary and pattern only.

Store as KNOWLEDGE_CONDENSED: a list of `{topic, modules, weight, summary, pattern (or null)}`.

## Step 7: Compute Coverage Confidence

Set CONFIDENCE based on:

1. Read the index header from `[CODEBASE_PATH]/index.md`. Get the `generated:` date. Compute age in days from today.
2. Check `stale: true|false` in the index header.
3. Count unresolved files (those with `module: "unresolved"` in FILE_MODULE_MAP).

**Coverage confidence rules (first match wins):**
- Any unresolved files AND majority of PHASE_FILES is unresolved → `low`
- `stale: true` in index header → `low`
- Index age > 30 days → `low`
- One or more files unresolved (but not majority) → `medium`
- Index age 8–30 days → `medium`
- All files resolved AND index age ≤ 7 days AND stale: false → `high`

If confidence is `low`, prepend to the packet:
```
> ⚠️ **Low coverage confidence** — index may be stale or missing modules. Run `/index codebase` and `/index knowledge` before relying on this packet.
```

If confidence is `medium`, prepend:
```
> ℹ️ **Medium coverage confidence** — [reason: one or more files unresolved | index age N days]. Verify unresolved files manually if they contain constraints relevant to this phase.
```

## Step 8: Write context/[ticket-id]/phase-[N]-context.md

Write `[CONTEXT_PATH]/[ticket-id]/phase-[N]-context.md` with this exact structure:

    _Note: module content is condensed. Full pages at [CODEBASE_PATH]/[module].md.
    Load full pages if constraints or decisions require deeper context._

    ---

    # Context Packet: [TICKET-ID] Phase [N]

    **Generated:** YYYY-MM-DD
    **Coverage confidence:** [high|medium|low]
    **Phase files:** [count] files across [count] modules
    **Unresolved files:** [list of unresolved file paths, or "none"]

    ## Index State

    - Index generated: [date from index header] ([N] days ago)
    - Index hash drift: [none|detected]
    - Maturity: [level] ([N] modules)

    ## Relevant Decisions

    _(All recorded decisions from modules in scope for this phase. Non-negotiable without
    explicit override — see Known Constraints for hard limits.)_

    [For each module with decisions:]
    ### [Module Name]
    [Content of the module's ## Decisions section]

    ## Module Context

    [For each module in PHASE_MODULES:]
    ### [Module Name]
    **Responsibility:** [responsibility]

    **Entry Points:**
    [entry points content]

    **Public Interface:**
    [public interface content]

    **Dependencies:**
    [dependencies content]

    **Known Constraints:**
    [known constraints content — if empty: "None recorded."]

    ## Knowledge Signals

    _(High-weight historical signals for modules in scope. Summary and pattern only —
    full entry list at [KNOWLEDGE_PATH]/[topic].md.)_

    [For each topic in KNOWLEDGE_CONDENSED:]
    ### [Topic Name] — [Weight] | [Status]
    _Modules: [module list]_

    **Summary:** [summary]

    **Pattern:** [pattern statement if present, else "(No confirmed pattern yet.)"]

Rules:
- The `_Note:` disclosure line at the top is mandatory on every packet. This satisfies **R6**.
- `## Relevant Decisions` appears before `## Module Context` — decisions must be seen before the engineer starts coding.
- If a module has no Known Constraints, write "None recorded." — never omit the field.

## Step 9: Report

Say:

> "Context packet written to `[CONTEXT_PATH]/[ticket-id]/phase-[N]-context.md`.
>
> - Coverage confidence: [level] — [reason if not high]
> - Modules in scope: [list]
> - Knowledge signals loaded: [N] topics (HIGH: N, MEDIUM: N)
> - Unresolved files: [list or "none"]
> - Unresolved files require direct codebase search (Plan 3) during execution."

---

## Output Format

- `[context-packets-path]/[ticket-id]/phase-[N]-context.md` — assembled context packet

## Dependencies

- `.github/skills/conventions/SKILL.md` — all artifact paths
- `[codebase-index-path]/index.md` and `[codebase-index-path]/[module].md` — module data
- `[knowledge-index-path]/index.md` and `[knowledge-index-path]/[topic].md` — knowledge signals
- Plan file for the specified ticket — phase manifest

## Handoff

Pass the context packet path to the execution agent: `/execute-plan [plan-path]`
The execution skill (updated in Plan 4b) reads this packet at phase start before making any changes.
```

- [ ] **Step 2: Trace Scenario 4 — Context packet for execution**

Mental trace: Ticket PROJ-123, Plan is `phased` execution mode, Phase 2 has 5 files across 3 modules (`auth`, `billing`, `api-gateway`). Codebase index exists with maturity = `mature`, generated 3 days ago, `stale: false`.

Confirm:
1. Step 2: all 3 trigger conditions pass (mature, phased, 5 files ≥ 4).
2. Step 4: all 5 files resolve to modules — no unresolved files.
3. Step 5: condensed pages for `auth`, `billing`, `api-gateway` loaded. Each has Responsibility, Entry Points, Public Interface, Dependencies, Known Constraints, Decisions.
4. Step 6: knowledge index filtered to topics mentioning `auth`, `billing`, or `api-gateway`. Suppose 2 HIGH topics found, 1 MEDIUM topic. All 3 loaded.
5. Step 7: CONFIDENCE = `high` (all resolved, index 3 days old, not stale).
6. Step 8: packet written. Opens with `_Note: module content is condensed...` (satisfies **R6**). `## Relevant Decisions` section present before `## Module Context`.
7. Step 9 reports: "Coverage confidence: high — Modules in scope: auth, billing, api-gateway — Knowledge signals loaded: 3 topics (HIGH: 2, MEDIUM: 1)."

- [ ] **Step 3: Trace Scenario 5 — Low maturity (greenfield)**

Mental trace: Repo has 6 modules (maturity = `low`). Engineer runs `/context-packet PROJ-456 phase-1`.

Confirm:
1. Step 2: condition 1 fails — maturity is `low`.
2. Skill stops and says "Maturity is low. Context packets are not generated for low-maturity repos. Use codebase search protocol (Plan 3) instead."
3. No file is written. No error — this is the expected path for greenfield repos.

- [ ] **Step 4: Commit Phase 4**

```bash
git add github/skills/context-packet/SKILL.md
git commit -m "feat: add context-packet skill (Job C) — context packet assembly for phased execution"
```

**Engineer review prompt:**
- In Step 8, `## Relevant Decisions` is listed before `## Module Context`. This order is deliberate — decisions should be read before encountering the module context so they frame the constraints. Confirm this ordering is preserved in the written template.
- The packet's `## Knowledge Signals` section includes summary and pattern only (not the full entry list). This is intentional — full entries are at the topic page. If an execution agent sees a HIGH-weight signal and wants more detail, it should read the topic page directly. Is this instruction present in the skill text? (Check the note in Step 6 and the `_Note:` disclosure in Step 8.)

---

## Testing Checklist (run after all phases complete)

- [ ] Open `github/skills/conventions/SKILL.md` — confirm `Codebase Index:`, `Knowledge Index:`, `Context Packets:` lines are present in `## Artifact Paths`; confirm `Maturity threshold:` is present in `## Codebase`
- [ ] Open `github/skills/setup/SKILL.md` — confirm Step 5 detects `codebase/`, `knowledge/`, `context/`; confirm Step 5b creates `module-map.md` starter; confirm Step 6 template includes all 3 new path fields and `Maturity threshold: default`
- [ ] Open `github/prompts/index.prompt.md` — confirm all 6 sub-commands are routed correctly; confirm missing-argument message is present
- [ ] Open `github/prompts/context-packet.prompt.md` — confirm usage instruction is present
- [ ] Open `github/skills/index-codebase/SKILL.md` — confirm module-map.md is checked before auto-discovery (Step 2); confirm `## Pending Validation` section is written for inferred modules; confirm `stale: false` in the index header on first run; confirm incremental mode exits early when hashes match
- [ ] Open `github/skills/index-knowledge/SKILL.md` — confirm knowledge index header always contains all 7 required fields (R7); confirm amendment routing rule (limit vs. design choice); confirm `## Relevant Decisions` is populated for chosen decisions only (rejected alternatives go to "Rejected:" prefix); confirm `stale-candidates` counter is present in header
- [ ] Open `github/skills/context-packet/SKILL.md` — confirm all 3 trigger conditions are checked before proceeding; confirm `_Note:` disclosure line is at the top of the packet (R6); confirm `coverage confidence` field is always present (R6); confirm LOW maturity stops with a clear message
- [ ] Run full end-to-end scenario trace (Scenario 1 in the spec): repo with 15 modules, 10 tickets. Trace: `/index codebase` → 15 module pages written. `/index knowledge` → signal density updated, 1 pattern-candidate. `/context-packet TICKET-1 phase-2` → packet written with HIGH confidence. `/index codebase --incremental` after one file change → only affected module page regenerated.

## Rollback Plan

- Revert all phase commits: `git revert HEAD~4` (4 commits, one per phase)
- Delete generated index files from `codebase/`, `knowledge/`, `context/` if any were created during testing
- No data migration required — all changes are to skill and prompt files; existing workflow artifacts are unaffected
