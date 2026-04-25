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
- **Non-goals:** Does not write code; does not modify plans or specs; does not build the codebase or knowledge index

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

**Version gate:** After reading the plan file, check its `schema_version` frontmatter. Store as PLAN_VERSION.

### V2 (PLAN_VERSION = 2)
PLAN_VERSION = 2. Use v2 typed-field paths in Steps 2, 3, 6.5, and 7.

### V1 (PLAN_VERSION = 1)
PLAN_VERSION = 1. Use existing prose extraction paths.

## Step 2: Check Trigger Conditions

Evaluate all three conditions. All must be true to proceed:

1. **Repo maturity:** Read `[CODEBASE_PATH]/index.md` header. Is `maturity: medium` or `maturity: mature`? If `maturity: low` → stop: "Maturity is low. Context packets are not generated for low-maturity repos. Use codebase search protocol (Plan 3) instead."

2. **Execution mode:** Does the plan file contain `> **Execution mode:** phased`? If `inline` or absent → stop: "Plan is inline execution mode. Context packets are for phased plans only."

3. **Phase file count:**

### V2 (PLAN_VERSION = 2)
Locate the phase entry where `phases[*].id = N`. Count total `FileRef` entries across `phases[N-1].steps[*].files` (all steps in that phase).
Are there ≥ 4 files? If < 4 → stop: "Phase [N] has [count] files. Context packets are generated for phases with ≥ 4 files only."

### V1 (PLAN_VERSION = 1)
Find the section `## Phase [N]:` and count files listed in its `**Files in this phase:**` block.
Are there ≥ 4 files? If < 4 → stop: "Phase [N] has [count] files. Context packets are generated for phases with ≥ 4 files only."

If all three conditions pass, continue.

## Step 3: Extract Phase File Manifest

### V2 (PLAN_VERSION = 2)
Read `phases[*].id = N` entry. Collect all `steps[*].files[*].path` values across every step in that phase. Exclude paths where `operation: 'delete'` (deleted files have no module context to load). Store as PHASE_FILES. No text parsing required.

### V1 (PLAN_VERSION = 1)
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

For each selected topic, read `[KNOWLEDGE_PATH]/[topic].md`. Extract:
- Header line 1: **Type** (the `Type:` value)
- Header line 2: **Validity** (the `Validity:` value)
- `## Summary` — full content
- `## Relationships` — `contradicts:` lines only; record the referenced topic names as a list
- `## Relationships` — `derived_from:` lines only; record the full line text
- `## Pattern` — if present

Do NOT include the full `## Entries` list in the packet — summary and pattern only.

Store as KNOWLEDGE_CONDENSED: a list of `{topic, modules, weight, type, validity, summary, contradicts_refs (list of topic names), derived_from_line (or null), pattern (or null)}`.

## Step 6.5: Select Decisions for Context Packet

### V2 (PLAN_VERSION = 2)
Compute the set of decisions to include in `## Relevant Decisions`:

```
phase_req_ids  = union of step.requirement_ids for all steps where phases[*].id = N
decision_ids_A = { req.source_decision
                   for req in requirements
                   where req.id ∈ phase_req_ids AND req.source_decision != null }
decision_ids_B = { d.id for d in decisions where d.reversibility = 'low' }
included       = decisions where id ∈ (decision_ids_A ∪ decision_ids_B)
```

Store as SELECTED_DECISIONS.

### V1 (PLAN_VERSION = 1)
Not applicable — skip this step. All decisions from loaded module pages apply (existing behavior).

## Step 7: Compute Coverage Confidence

### V2 (PLAN_VERSION = 2)
Apply the typed formula:

```
all_files  = all FileRef entries in phases[*].id=N steps
none_count = count of f in all_files where file-to-module mapping = UNKNOWN
total      = count of all_files

if none_count / total > 0.5  → CONFIDENCE = 'low'
if none_count > 0            → CONFIDENCE = 'medium'
else                         → CONFIDENCE = 'high'
```

**File path → module mapping rule (v2 only):**
```
candidates(path) = { m for m in codebase_index.modules
                       where any source_path ∈ m.source_paths is a prefix of path }

resolve(path):
  |candidates| = 1  → use that module
  |candidates| = 0  → UNKNOWN
  |candidates| > 1  → longest matching prefix wins;
                      tie → higher Reach score wins;
                      tie → alphabetically first module name (deterministic)
```

### V1 (PLAN_VERSION = 1)
Use existing rules (first match wins: unresolved majority → low, stale index → low, index age > 30 days → low, one or more unresolved → medium, all resolved + index ≤ 7 days + not stale → high).

If CONFIDENCE = `low`, prepend to the packet:
```
> ⚠️ **Low coverage confidence** — index may be stale or missing modules. Run `/index codebase` and `/index knowledge` before relying on this packet.
```

If CONFIDENCE = `medium`, prepend:
```
> ℹ️ **Medium coverage confidence** — [reason]. Verify unresolved files manually if they contain constraints relevant to this phase.
```

**Pre-assembly computations (before writing the packet):**

- **STALE_COUNT** = count of topics in KNOWLEDGE_CONDENSED where `validity = stale`
- **CONFLICT_PAIRS** = pairs of topics in KNOWLEDGE_CONDENSED where topic A's `contradicts_refs` contains topic B's name AND topic B is present in KNOWLEDGE_CONDENSED. For 3+ mutually contradicting topics: include only the 2 highest-weight topics as one pair; record `+N additional topics in conflict cluster` for the rest.

## Step 7.5: Load Cross-Repo Signals (if imports.md exists)

Read `[KNOWLEDGE_PATH]/../imports.md`. If this file does not exist: skip this step entirely — set CROSS_REPO_SIGNALS = [].

If the file exists, run this resolution for each `import_source` in the file:

```
For each phase_module in PHASE_MODULES:
  If phase_module ∈ import_source.scope (exact string match):
    Read import_source.exports_path
    For each exported_topic where phase_module ∈ exported_topic.modules (exact string match):
      If exported_topic.weight ∈ {HIGH, MEDIUM}
      AND days_since(exported_topic.last_updated) <= 90:
        → add to CROSS_REPO_SIGNALS
```

Match is exact string equality only. Naming divergence between repos produces no match.
CROSS_REPO_SIGNALS do NOT affect CONFIDENCE calculation.
CROSS_REPO_SIGNALS do NOT count against the knowledge loading budget.

**Code loading (runs after topic signal resolution, same step):**

Initialize CROSS_REPO_CODE = [] and CROSS_REPO_CODE_WARNINGS = [].

For each import_source where `include_code` is present and non-empty:
  For each phase_module in PHASE_MODULES:
    If phase_module ∈ import_source.scope (exact string match):
      (exports already read above — reuse parsed content)
      If exports.code_exports is absent: skip code loading for this source

      For each code_export where:
        code_export.module == phase_module (exact string)
        AND code_export.type ∈ import_source.include_code:

          Accumulate files across all roots for this code_export:
            For each root in code_export.roots:
              If root.path does not exist: skip silently
              List files under root.path
              Apply root.include patterns (keep matches only)
              Apply root.exclude patterns (remove matches)
              Skip binary / non-text files silently
              If result > 20 files:
                Add to CROSS_REPO_CODE_WARNINGS: "Root [root.path] skipped — exceeds 20-file limit"
                Skip root; continue to next root
              Else: add files to candidate set

            Deduplicate candidate set by full path (keep first lexicographic occurrence)
            Sort candidate set lexicographically by full path
            Apply global cap: if candidate set > 50 files, keep first 50
              and add to CROSS_REPO_CODE_WARNINGS: "import_source [repo] capped at 50 files"
            For each file in candidate set:
              Read content; truncate at 500 lines with "... (truncated)" if needed
            Add group {repo, module, type, root_summary, files, warnings} to CROSS_REPO_CODE

CROSS_REPO_CODE does NOT affect CONFIDENCE.
CROSS_REPO_CODE does NOT count against the knowledge loading budget.
Multiple import_sources are processed independently; results concatenated.

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

    [If CONFLICT_PAIRS is non-empty:]
    ## Conflicting Signals

    _(These topics make conflicting assertions about modules in scope. Both are shown —
    do not suppress either. Resolve explicitly or flag for engineer decision.)_

    [For each pair in CONFLICT_PAIRS:]
    ### [Topic A] ↔ [Topic B] — [shared module(s)]
    - **[Topic A]** (Type: [type] | [validity indicator]): [Topic A summary]
    - **[Topic B]** (Type: [type] | [validity indicator]): [Topic B summary]
    - Conflict: [description from the `contradicts:` line]
    [If escalation applies — empirical valid ↔ system valid:]
    > ⚠️ ENGINEER DECISION REQUIRED — empirical data conflicts with designed contract
    [If escalation applies — empirical valid ↔ empirical valid:]
    > ⚠️ CONFLICTING EVIDENCE — verify data sources and sample boundaries

    [If conflict cluster has additional topics beyond the 2 loaded:]
    > +N additional topics in conflict cluster not loaded — see knowledge index for full list.

    ---

    [If CROSS_REPO_SIGNALS is non-empty:]
    ## Cross-Repo Signals

    _(Advisory only — signals from external repos whose exported module names match this phase scope. Cannot block execution, modify artifact fields, create contradicts relationships, or affect coverage confidence. Exact module name match only.)_

    [For each signal in CROSS_REPO_SIGNALS:]
    ### [topic_id] — [title] | [weight] | [type]
    _Source repo: [repo name] | Modules: [modules list] | Last updated: [last_updated]_

    [summary]

    ---

    [If CROSS_REPO_CODE is non-empty:]
    ## Cross-Repo Code

    _(Advisory only — files loaded from declared code_exports roots via exact module+type
    match. Cannot block execution, modify artifact fields, affect coverage_confidence,
    or create contradicts relationships with local topics.)_

    [For each group in CROSS_REPO_CODE:]
    ### [repo name] — [module] ([type])
    _Source roots: [root.path list] | Patterns: [include] | Excluded: [exclude]_

    [For each file in group.files:]
    **[filename]**
    [file content]

    [For each warning in group.warnings:]
    ⚠️ [warning text]

    ---

    ## Knowledge Signals

    _(High-weight historical signals for modules in scope. Summary and pattern only —
    full entry list at [KNOWLEDGE_PATH]/[topic].md.)_

    [If STALE_COUNT ≥ 2:]
    > ⚠️ [STALE_COUNT] stale signals in scope — run `/index knowledge --incremental` to refresh before relying on this packet.

    [For each topic in KNOWLEDGE_CONDENSED:]
    ### [Topic Name] — [Weight] | [Type] | [validity indicator]
    _Modules: [module list]_

    **Summary:** [summary]

    [If derived_from_line is present:]
    **Derived from:** [derived_from_line content]

    **Pattern:** [pattern statement if present, else "(No confirmed pattern yet.)"]

Rules:
- The `_Note:` disclosure line at the top is mandatory on every packet. This satisfies **R6**.
- `## Relevant Decisions` appears before `## Module Context` — decisions must be seen before the engineer starts coding.
- If a module has no Known Constraints, write "None recorded." — never omit the field.
- `## Conflicting Signals` appears only when CONFLICT_PAIRS is non-empty. Omit entirely when no conflicts are in scope — no placeholder.
- Stale signal warning appears only when STALE_COUNT ≥ 2. Omit entirely when condition is not met — no placeholder.
- Validity indicators: `valid` → no decoration; `stale` → `⚠️ STALE`; `questionable` → `⚠️ QUESTIONABLE`; `superseded` → never loaded, never displayed.
- `## Cross-Repo Signals` appears only when CROSS_REPO_SIGNALS is non-empty. Omit entirely when empty — no placeholder.
- Cross-repo signals are advisory only. They cannot create `contradicts` relationships with local topics and do not affect coverage confidence.
- `## Cross-Repo Code` appears only when CROSS_REPO_CODE is non-empty. Omit when empty — no placeholder.
- Cross-repo code is advisory only. Cannot create `contradicts` relationships or affect confidence.
- Warnings are surfaced inline under the relevant group — not in a separate section.
- Context size is bounded: 50-file global cap per import_source per phase, 500-line per-file truncation.

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
