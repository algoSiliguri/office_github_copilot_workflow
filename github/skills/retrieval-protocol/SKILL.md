---
name: retrieval-protocol
description: Shared reference skill — the full retrieval protocol for the planning phase. Read this skill when the planning skill runs Intelligence Retrieval. Contains the activation gate, loading budgets, ticket-type classification, navigation decision tree, one-hop expansion rules, retrieval summary format, and staleness handling.
allowed-tools: read_file
---

## Metadata

- **Name:** retrieval-protocol
- **Description:** The retrieval protocol consumed by the planning phase. Governs how the planner navigates the codebase and knowledge indexes to load the minimum relevant context before drafting a plan.
- **Phase:** Shared reference — read by the planning skill during Intelligence Retrieval
- **Inputs:** Brainstorm artifact (already read by the planning skill), codebase index, knowledge index
- **Outputs:** A retrieval summary block (`## Intelligence Context`) and a set of loaded module/knowledge pages for use during planning

## When To Use

Read this skill only when the planning skill's Intelligence Retrieval section instructs you to. Do not invoke this skill during brainstorming, spec-writing, execution, or review — those phases have their own inline integrations.

---

## Activation Gate

Before loading any index files, run this gate:

```
1. Read [Codebase Index:] path from .github/skills/conventions/SKILL.md.
   Attempt to read [codebase-index-path]/index.md.
   If the file does not exist → SKIP. Fall back to codebase search protocol
   (semantic_search / grep_search on demand). Stop here.

2. Read the index header line:
   <!-- generated: YYYY-MM-DD | modules: N | source-hash: ... | maturity: low|medium|mature | stale: true|false -->
   If maturity = low → SKIP. Fall back to codebase search protocol. Stop here.
   If maturity = medium or mature → PROCEED with the full protocol below.
```

## Loading Budget (hard limits — never exceed)

| Phase | Module pages | Knowledge pages | Expansion allowed |
|---|---|---|---|
| Planning | 3 | 2 | +1 module, +1 knowledge |
| Brainstorming | 0 (index-only) | 0 (index-only) | None |
| Spec-writing | 0 (## Decisions only) | 0 | None |
| Execution | Via context packet only | Via context packet only | None |

These limits are hard. If loading budget is exhausted, stop. Do not load additional files under uncertainty. R3 requires the protocol always terminates within budget + 1 expansion.

## Ticket Type Classification

Apply to the brainstorm artifact's `## Problem` section text. First match wins:

1. Text contains any of: `fix`, `bug`, `error`, `fail`, `failure`, `broken`, `crash` → `bug-fix`
2. Text contains any of: `modify`, `refactor`, `update`, `change`, `migrate`, `replace` → `modification`
3. Otherwise → `new-feature`

**Loading split by ticket type:**

| Ticket type | Module pages | Knowledge pages |
|---|---|---|
| new-feature | 3 | 1 |
| modification | 2 | 2 |
| bug-fix | 1 | 2 |

If the split sum is less than the budget, the remaining slots are unused — do not fill them speculatively.

## Navigation Decision Tree (Planning Phase)

Execute steps in order. Do not skip or reorder.

**Step 1 — Read the brainstorm artifact**

Extract from the brainstorm artifact:
- Named modules or classes (any proper noun that looks like a module or class name)
- File paths (any string containing `/` or `.java`, `.py`, `.go`, `.ts`, etc.)
- Feature area keywords (2–5 descriptive words from the Problem section that characterise the domain)

Classify the ticket type (see above). Set LOADING_SPLIT from the ticket-type table.

**Step 2 — Read codebase/index.md and identify candidate modules**

Read the full codebase index table. Identify candidate modules in this priority order:
- Priority 1 (directly named): modules whose name or path matches a named module or file path from Step 1
- Priority 2 (active-risk overlap): modules with `active` risk status whose Responsibility column contains a keyword from the feature area keywords
- Priority 3 (critical-core adjacent): modules with `critical-core` quadrant that are adjacent to Priority 1 modules (share a dependency edge — check this in Step 4 after loading Priority 1 module pages)

If no candidates found after Priority 1 and 2 searches:
→ Fallback: select the single module with the highest Reach (direct). Tiebreak: closest Responsibility keyword match to the feature area. Load only this one module. Set LOADING_SPLIT module count to 1.

**Step 3 — Apply ticket-type loading split**

Set the module and knowledge page budgets from LOADING_SPLIT (the ticket-type table above). These are the maximum pages to load in Steps 4 and 6. Do not exceed them.

**Step 4 — Load module pages in priority order (within module budget)**

Load module pages in this priority:
1. Priority 1 modules first (directly named)
2. Priority 2 modules next (active-risk, feature overlap)
3. Priority 3 modules last (critical-core adjacent)

Stop when the module budget is exhausted. Record loaded module names as LOADED_MODULES.

**Step 5 — Read knowledge/index.md and identify relevant entries**

Read `[Knowledge Index:]` path from conventions. Read the knowledge index table.

Filter: rows where the Module(s) column contains at least one module from LOADED_MODULES.

Sort: HIGH weight first; within HIGH: active before historical; within status: recent before stale (use the Recent column).

Exclude: LOW-weight entries unless no MEDIUM or HIGH entries exist for any loaded module (in that case, include the best LOW-weight entry for those modules only, up to budget).

If no entries exist for any loaded module: record `Knowledge loaded: none — no entries indexed for loaded modules`. Skip Step 6.

**Step 6 — Load knowledge pages (within knowledge budget)**

For each selected topic (in sorted order), load `[knowledge-index-path]/[topic].md` until the knowledge budget is exhausted. Record loaded topic names as LOADED_KNOWLEDGE.

**Step 7 — Run one-hop expansion check**

Check whether any of these mismatch triggers apply (any one activates expansion):
- A loaded module page has no class or interface name relevant to the feature area keywords
- The knowledge index has a HIGH-weight entry for an unloaded adjacent module that matches the feature area
- A loaded module's `## Dependencies` or `## Dependents` references an unloaded module with `critical-core` or `sleeper-risk` quadrant
- The loaded signals describe a different problem domain than the brainstorm feature area (loaded knowledge topic summaries do not relate to the feature area)

**If no trigger fires:** Skip expansion. Record `Expansion: none`.

**If a trigger fires — candidate selection (strict priority, first decisive criterion wins):**
1. Build pool: all modules within one dependency hop of LOADED_MODULES (check `## Dependencies` and `## Dependents` of each loaded module page)
2. Filter pool to modules with `critical-core` or `sleeper-risk` quadrant. If none remain after filtering → skip expansion entirely. Record `Expansion: none (no critical-core or sleeper-risk candidates within one hop)`.
3. From the filtered pool: prefer active-risk over historical
4. Prefer modules with outbound edges to LOADED_MODULES (they depend on modules in scope — changes likely flow into them)
5. Prefer candidates with a HIGH-weight knowledge entry matching the feature area
6. Select top 1 candidate

Load the selected module's tier-2 page (this uses the +1 expansion module slot). If a HIGH-weight knowledge entry exists for this module matching the feature area, load that topic page too (this uses the +1 expansion knowledge slot). Maximum one expansion. No second hop.

Record `Expansion: [module name] — [reason: quadrant + which trigger fired]`.

**Step 8 — Produce retrieval summary**

Assemble the retrieval summary using this exact format:

    ## Intelligence Context
    - Index maturity: [low|medium|mature] ([N] modules)
    - Index age: [N] days | Hash drift: [none|detected — "detected" if stale: true in index header]
    - Ticket type: [new-feature|modification|bug-fix]
    - Modules loaded: [list, or "none"]
    - Knowledge loaded: [list with weight in brackets, e.g. "token-lag [HIGH], db-pool [MEDIUM]"] | or "none — no entries indexed for loaded modules"
    - Expansion: [none] | [module name] — [reason]
    - Coverage confidence: [high|medium|low]
    - Warnings: [any staleness flags, missing modules, pending validation markers — or "none"]

Coverage confidence:
- `high`: all brainstorm-named modules found in index; index age ≤ 7 days; no hash drift
- `medium`: one or more named modules not in index; OR index age 8–30 days
- `low`: majority of named modules not in index; OR index age > 30 days; OR stale: true

**Step 9 — Stop**

Uncertainty remaining after retrieval is resolved during execution, not by expanding retrieval beyond the defined budget. The plan is written using what retrieval surfaced plus direct codebase exploration (the "Before Writing a Single Step" section in the planning skill).

## Staleness Handling

Apply these behaviors when staleness signals are present:

| Signal | Trigger | Behavior |
|---|---|---|
| Missing module | Module named in brainstorm not in index | Log in Warnings field of retrieval summary; fall back to codebase search for that module only (semantic_search / grep_search) |
| Hash drift | `stale: true` in index header | Prepend warning to retrieval summary: "⚠️ Index stale — run /index codebase before planning for accuracy." Still proceed with retrieval. |
| Age warning | Index age > 30 days | Set coverage confidence = low; include age in Warnings field |
| Index absent | File does not exist | Activation gate stops retrieval; fall through to codebase search protocol |

---

## Output Format

This skill does not write any files. It produces:
- A retrieval summary (`## Intelligence Context` block) for the planning skill to embed in the plan
- A set of loaded module pages and knowledge pages already in context

## Dependencies

- `.github/skills/conventions/SKILL.md` — codebase index path, knowledge index path
- `[codebase-index-path]/index.md` — Tier 1 codebase index
- `[codebase-index-path]/[module].md` — Tier 2 module pages (within budget)
- `[knowledge-index-path]/index.md` — Tier 1 knowledge index
- `[knowledge-index-path]/[topic].md` — Tier 2 topic pages (within budget)
- Brainstorm artifact (already read by the planning skill — extract named modules and feature area keywords from it)
