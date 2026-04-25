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
- **Non-goals:** Does not modify source files or workflow artifacts; does not extract knowledge signals (index-knowledge's job)

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
