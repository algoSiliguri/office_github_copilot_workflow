# Retrieval + Intelligence Layer — Retrieval Layer Implementation Plan (Plan 4b)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire the retrieval protocol into the workflow — a shared retrieval-protocol skill plus targeted integrations in all five phase skills (brainstorming, spec-writing, planning, execution, review) — so that index knowledge surfaces at the right moment in every workflow phase.

**Architecture:** One new shared reference skill (`retrieval-protocol/SKILL.md`) contains the full navigation decision tree, loading budgets, ticket-type classification, expansion rules, and retrieval summary format. Planning reads this skill and runs the full protocol. Brainstorming inlines a simplified index-only scan. Spec-writing inlines a decision conflict check. Execution reads context packets. Review adds knowledge maintenance to its debrief. All integrations are additive — no existing skill logic is removed.

**Tech Stack:** Markdown only — no code, no build system. Verification is scenario trace.

**Spec:** `docs/superpowers/specs/2026-04-16-retrieval-intelligence-design.md`

**Prerequisite:** Plan 4a must be complete. The index files these skills read are produced by the generation skills in Plan 4a.

---

## All Files Changed

- `github/skills/retrieval-protocol/SKILL.md` — Phase 1: new shared reference skill; full retrieval protocol
- `github/skills/brainstorming/SKILL.md` — Phase 2: add Intelligence Scan section before Entry Logic
- `github/skills/spec-writing/SKILL.md` — Phase 2: add Decision Conflict Check before Self-Review
- `github/skills/planning/SKILL.md` — Phase 3: add Intelligence Retrieval section; update plan template with two new preamble sections
- `github/skills/execution/SKILL.md` — Phase 4: add context packet check to inline and phased execution modes
- `github/skills/review/SKILL.md` — Phase 4: add items 5–6 to ticket debrief

---

## Phase 1: Retrieval Protocol Shared Skill

**Files in this phase:**
- Create: `github/skills/retrieval-protocol/SKILL.md`

- [ ] **Step 1: Create the retrieval-protocol skill file**

Create `github/skills/retrieval-protocol/SKILL.md` with this exact content:

```markdown
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
```

- [ ] **Step 2: Trace Scenario 2 — Retrieval protocol for a bug-fix ticket**

Mental trace: Brainstorm artifact `## Problem` says "fix token validation failure in authentication flow."

Confirm:
1. Activation gate: `codebase/index.md` exists, header shows `maturity: mature`. Protocol runs.
2. Ticket type classification: text contains "fix" and "failure" → `bug-fix`. LOADING_SPLIT = 1 module page, 2 knowledge pages.
3. Step 1 extracts: named modules = none explicit; feature area keywords = ["token", "validation", "authentication"]. File paths = none.
4. Step 2: Priority 2 search — modules with `active` risk status whose Responsibility mentions "auth" or "token". Suppose `AuthService` matches.
5. Step 3: module budget = 1, knowledge budget = 2.
6. Step 4: Load `codebase/auth-service.md`. LOADED_MODULES = [`AuthService`]. Budget exhausted.
7. Step 5: Filter knowledge index to entries for AuthService. Sort HIGH first. Suppose 2 HIGH entries exist for AuthService.
8. Step 6: Load both HIGH-weight topic pages. LOADED_KNOWLEDGE = [`token-invalidation-lag`, `session-timeout-mismatch`]. Budget exhausted.
9. Step 7: Expansion check. Suppose AuthService's `## Dependencies` lists `TokenStore` as `critical-core`. The loaded module page mentions token validation logic — it IS relevant to the feature area. No mismatch trigger fires. Expansion = none.
10. Step 8: Retrieval summary produced. Coverage confidence: `high` (named keyword matched, index 2 days old, not stale).

This satisfies **R3** (terminated within budget) and **R8** (retrieval summary deterministic).

- [ ] **Step 3: Commit Phase 1**

```bash
git add github/skills/retrieval-protocol/SKILL.md
git commit -m "feat: add retrieval-protocol shared skill — navigation decision tree, loading budget, one-hop expansion"
```

**Engineer review prompt:**
- The activation gate stops retrieval for `maturity: low` repos. After this stop, the planning skill falls back to its existing codebase search ("Before Writing a Single Step" step 2). Confirm this fallback path is clearly described in Phase 3 of this plan where planning/SKILL.md is modified — the retrieval skill itself only stops, it doesn't describe the fallback.
- The loading budget table includes a Brainstorming row (0/0/None) and Spec-writing row (0/0/None) even though those phases don't call this skill. This is intentional — the table is a reference so engineers understand the full per-phase budget at a glance. Would it be clearer to add a note saying "Brainstorming and Spec-writing inline their own lighter protocols; they do not call this skill"?

---

## Phase 2: Brainstorming + Spec-writing Integrations

**Files in this phase:**
- Modify: `github/skills/brainstorming/SKILL.md`
- Modify: `github/skills/spec-writing/SKILL.md`

- [ ] **Step 1: Add Intelligence Scan to brainstorming/SKILL.md**

In `github/skills/brainstorming/SKILL.md`, find this block (the separator + persona paragraph before `## Entry Logic`):

```
---

You are a senior software architect in a real conversation with an engineer. Your job is to
understand the problem deeply before any solution is discussed. You do not run through a
checklist. You do not ask a predetermined set of questions. You think, probe, and explore.

## Entry Logic
```

Replace with:

```markdown
---

You are a senior software architect in a real conversation with an engineer. Your job is to
understand the problem deeply before any solution is discussed. You do not run through a
checklist. You do not ask a predetermined set of questions. You think, probe, and explore.

## Intelligence Scan (run silently before the first question)

Before engaging with the engineer, silently check whether a codebase index exists:

1. Read `Codebase Index:` path from `.github/skills/conventions/SKILL.md`.
   Attempt to read `[codebase-index-path]/index.md`.
   If the file does not exist, or the header shows `maturity: low`: skip to step 4 (open without codebase framing).

2. Read the index table. Identify candidate modules by matching Module name or Responsibility column text against:
   - Any content in the `## Active Context` block in conventions
   - The ticket ID or description provided by the engineer (if already given)
   Priority: modules with `active` Risk Status first, then by Reach (direct) descending. Select up to 3 candidates.

3. Read `Knowledge Index:` path from conventions. Read `[knowledge-index-path]/index.md`.
   Filter rows: topics where Module(s) contains a candidate from step 2 AND Weight = `HIGH`.
   Collect topic name and one-line summary for each match.

4. Open the conversation with one of these framings:
   - **Candidates found (step 2 matched at least one module):**
     "Based on the index, `[module-name]` appears to be the primary area for this work.
     It is flagged as `[quadrant]` with `[N]` recent signals.
     Known signals: [one-line summaries from step 3, or "none yet"]. Does this match your understanding?"
   - **No candidates (step 2 found nothing, or index absent/low):**
     Proceed directly to the Active Context check and seed question in Entry Logic below.
     Open without any codebase framing.

Do not announce the scan. Do not mention index files or retrieval protocol to the engineer.

## Entry Logic
```

- [ ] **Step 2: Trace scenario — brainstorm with a medium-maturity repo**

Mental trace: Engineer opens `/brainstorm` for a ticket about "adding rate limiting to the login endpoint." Active Context in conventions is empty. Codebase index exists, maturity = medium.

Confirm:
1. Intelligence Scan step 1: index exists, maturity = medium. Proceed.
2. Step 2: scan Responsibility column for terms related to login. `AuthController` has Responsibility containing "login" — selected as candidate. Risk Status = active. Reach = 5 (highest in the auth area).
3. Step 3: knowledge index filtered to AuthController. One HIGH-weight entry found: `auth-rate-limit-bypass` — "Repeated login attempts can bypass the 5-request limit due to session ID regeneration."
4. Step 4: framing chosen: "Based on the index, `AuthController` appears to be the primary area for this work. It is flagged as `critical-core` with 3 recent signals. Known signals: auth-rate-limit-bypass — 'repeated login attempts can bypass the 5-request limit due to session ID regeneration'. Does this match your understanding?"
5. Engineer responds. Brainstorming continues normally from there.

Confirm: the framing surfaces a directly relevant prior discovery before the engineer has said anything. The scan is not announced.

- [ ] **Step 3: Add Decision Conflict Check to spec-writing/SKILL.md**

In `github/skills/spec-writing/SKILL.md`, find this block (the paragraph before the horizontal rule and Self-Review):

```
For every requirement: if you cannot describe a failing test for it, push back and make it
more specific before accepting it.

---

## Self-Review (before handoff)
```

Replace with:

```markdown
For every requirement: if you cannot describe a failing test for it, push back and make it
more specific before accepting it.

## Decision Conflict Check (run after the Architecture section is written, before Self-Review)

1. Read the `## Architecture / Design Decisions` section of the spec you just drafted. List every module, service, or system named or implied by the design.

2. Read `Codebase Index:` path from `.github/skills/conventions/SKILL.md`. For each identified module, attempt to read `[codebase-index-path]/[module].md`. Extract the `## Decisions` section only.
   - If the index does not exist, or a module page does not exist: skip that module.
   - If no module pages are found at all: note `_Decision check: index not available — [YYYY-MM-DD]_` at the end of `## Architecture / Design Decisions` and proceed to Self-Review.

3. Compare each recorded decision against the spec's architectural choices. Flag a conflict when any of these are true:
   - The spec's design directly contradicts a recorded decision (proposes X where the decision chose not-X).
   - The spec weakens a load-bearing assumption that a recorded decision depends on.
   - The spec re-proposes an alternative that appears as `Rejected:` in a module's `## Decisions`.

4. **If one or more conflicts are found:** Stop. Do not proceed to Self-Review or output the spec. Present each conflict to the engineer:
   > "**Decision conflict — `[module-name]`:** A recorded decision states: '[exact decision text from the module page].'
   > Your spec [one sentence describing how the spec conflicts].
   > Options:
   > **A** — Revise the spec to align with the recorded decision.
   > **B** — Override: I'll add a `## Design Override` section and Job B will pick it up on the next `/index knowledge` run."
   Wait for the engineer to choose A or B for each conflict. Apply A (revise the spec) or B (add override section) before continuing.
   **Override section format (option B):**
   Add this section to the spec immediately before `## Risks & Dependencies`:
   ```
   ## Design Override
   **Overrides:** [module-name] decision from [YYYY-MM-DD] [TICKET-ID]
   **Reason:** [engineer's stated reason for overriding]
   ```

5. **If no conflicts:** Note at the end of `## Architecture / Design Decisions`:
   `_Decision check: no conflicts found — [YYYY-MM-DD]_`
   Proceed to Self-Review.

---

## Self-Review (before handoff)
```

- [ ] **Step 4: Trace Scenario 3 — Decision conflict detection**

Mental trace: Spec proposes in-memory cache for `AuthService`. The module page `codebase/auth-service.md` `## Decisions` contains:
```
- 2026-03-10 PROJ-89: Rejected: in-memory cache for token storage — tokens must survive pod restarts; use Redis only.
  Source: docs/specs/2026-03-10-PROJ-89-auth-redesign.md
```

Confirm:
1. Decision Conflict Check step 1: spec's `## Architecture` names `AuthService`.
2. Step 2: reads `codebase/auth-service.md`; extracts `## Decisions`.
3. Step 3: spec proposes "in-memory cache" — this appears as `Rejected:` in the module page. Conflict flagged.
4. Step 4: present conflict to engineer with exact decision text. Engineer chooses B — override.
5. `## Design Override` section added to spec before `## Risks & Dependencies`.
6. Spec can now proceed to Self-Review. This satisfies **R5** (decision conflict always surfaced before spec finalised).

- [ ] **Step 5: Commit Phase 2**

```bash
git add github/skills/brainstorming/SKILL.md github/skills/spec-writing/SKILL.md
git commit -m "feat: add intelligence scan to brainstorming; add decision conflict check to spec-writing"
```

**Engineer review prompt:**
- The brainstorming Intelligence Scan says "Do not announce the scan." This keeps the framing natural — the architect opens with "Based on the index..." as if it's their own knowledge. Is this the right UX, or should the scan be transparent (e.g., "I checked the index and found...")?
- The Decision Conflict Check in spec-writing stops the spec from being finalised when a conflict exists. This means the engineer cannot skip it — they must choose A or B. Is this the right gate, or should there be a "C — Acknowledge and proceed without override" option for cases where the engineer has already discussed the conflict with the team?

---

## Phase 3: Planning Integration

**Files in this phase:**
- Modify: `github/skills/planning/SKILL.md`

- [ ] **Step 1: Insert Intelligence Retrieval section before "Before Writing a Single Step"**

In `github/skills/planning/SKILL.md`, find this block (the opening paragraph + Before Writing heading):

```
You are in plan phase. Create a phased implementation plan grounded in the actual code.

## Before Writing a Single Step

1. Read the spec file in full — understand every requirement and constraint.
2. Explore the codebase:
   - `list_dir` to understand the project structure
   - `file_search` to find relevant files by name pattern
   - `semantic_search` to find code related to what you're building
   - `read_file` to understand existing patterns, interfaces, and naming conventions
3. Map what needs to change and where — real files, real line ranges.

Only write steps after you have seen the actual code.
```

Replace with:

```markdown
You are in plan phase. Create a phased implementation plan grounded in the actual code.

## Intelligence Retrieval (run before exploring the codebase)

1. Read `.github/skills/retrieval-protocol/SKILL.md`. Run the full retrieval protocol exactly as described — activation gate through retrieval summary (Steps 1–9 in the protocol).
2. **If index absent or maturity = low:** Skip retrieval. Proceed directly to "Before Writing a Single Step" below, using the full codebase search (step 2 in that section).
3. **After retrieval completes:**
   a. Assemble the `## Intelligence Context` block from the retrieval summary. This block goes in the plan preamble (added in Step 2 of the plan structure update below).
   b. Collect all `## Known Constraints` lines from every loaded module page. These go in the `## Constraints` section of the plan preamble (also in Step 2 below). Label each: `[source: module-page]`. Treat them as non-negotiable — equivalent to spec requirements.
   c. Note which loaded knowledge entries have HIGH weight — use them to order phases (put riskier, higher-signal areas first) and to add risk notes to the relevant phase's `**Engineer review prompt:**`.
   d. Run the Decision Conflict Check (same protocol as spec-writing): read `## Decisions` from every loaded module page; compare against the spec's Architecture section; flag and resolve conflicts before writing any steps.

## Before Writing a Single Step

1. Read the spec file in full — understand every requirement and constraint.
2. Explore the codebase:
   - **If retrieval ran:** Start from the `## Public Interface` and `## Dependencies` sections of loaded module pages. Use `read_file` on referenced files to confirm their current state. Use `file_search` and `semantic_search` only for modules or files not covered by the loaded pages.
   - **If retrieval was skipped:** Use `list_dir`, `file_search`, `semantic_search`, and `read_file` to understand the codebase from scratch.
3. Map what needs to change and where — real files, real line ranges.

Only write steps after you have seen the actual code.
```

- [ ] **Step 2: Update the plan structure template to add Intelligence Context and Constraints preamble sections**

In `github/skills/planning/SKILL.md`, find this block inside the `~~~markdown` fence (the top of the plan template):

```
# Implementation Plan: [TICKET-ID] — [Feature Name]

> **Execution mode:** [inline | phased]

## All Files Changed
Every file created or modified across all phases:
- `[exact/path/to/file]` — Phase N: [what changes and why]
```

Replace with:

```markdown
# Implementation Plan: [TICKET-ID] — [Feature Name]

> **Execution mode:** [inline | phased]

## Intelligence Context
_(Include only when retrieval protocol ran. Omit this section entirely if index absent or maturity = low.)_
- Index maturity: [low|medium|mature] ([N] modules)
- Index age: [N] days | Hash drift: [none|detected]
- Ticket type: [new-feature|modification|bug-fix]
- Modules loaded: [list]
- Knowledge loaded: [list with weight in brackets] | or "none — no entries indexed for loaded modules"
- Expansion: [none] | [module name] — [reason]
- Coverage confidence: [high|medium|low]
- Warnings: [staleness flags, missing modules, pending validation markers — or "none"]

## Constraints
_(Include only when retrieval returned Known Constraints from module pages. Non-negotiable — treat as spec requirements.)_
- [constraint statement] `[source: module-page: ModuleName]`

## All Files Changed
Every file created or modified across all phases:
- `[exact/path/to/file]` — Phase N: [what changes and why]
```

- [ ] **Step 3: Trace Scenario 2 (continued) — Retrieval summary embedded in plan**

Mental trace: Planning phase for a bug-fix ticket ("fix token validation failure"). Retrieval protocol ran (from Scenario 2 trace in Phase 1). LOADED_MODULES = [`AuthService`], LOADED_KNOWLEDGE = [`token-invalidation-lag [HIGH]`, `session-timeout-mismatch [HIGH]`]. Index age = 2 days, not stale, coverage confidence = high.

Confirm:
1. `## Intelligence Context` block appears in the plan preamble with all 8 fields filled.
2. `AuthService`'s `## Known Constraints` section contains: "Session tokens must not be cached in-memory across requests [2026-03-10 PROJ-89]". This appears in `## Constraints` labeled `[source: module-page: AuthService]`.
3. Planner orders Phase 1 around AuthService's token validation logic (the HIGH-weight knowledge informed this ordering).
4. Decision Conflict Check: spec's Architecture names AuthService. Module page checked. Suppose no conflicts. `_Decision check: no conflicts found — 2026-04-16_` noted. Plan proceeds.
5. This satisfies **R8** (retrieval summary always appended to planning output, deterministic).

- [ ] **Step 4: Trace — Greenfield / low maturity path**

Mental trace: Repo with 6 modules (maturity = low). Planning phase runs.

Confirm:
1. Intelligence Retrieval step 1: reads retrieval-protocol skill.
2. Activation gate fires at maturity = low. Retrieval skipped.
3. Step 2 says "If retrieval was skipped: use list_dir, file_search, semantic_search." Planner falls back to full codebase search.
4. Plan template is written WITHOUT `## Intelligence Context` and `## Constraints` sections (they are omitted when retrieval was skipped).

- [ ] **Step 5: Commit Phase 3**

```bash
git add github/skills/planning/SKILL.md
git commit -m "feat: add intelligence retrieval and decision conflict check to planning skill; update plan template"
```

**Engineer review prompt:**
- The plan template now has two optional sections (`## Intelligence Context` and `## Constraints`) that are omitted when retrieval was skipped. Existing plans written before Plan 4b do not have these sections — they remain valid. Confirm: does any existing skill or agent read the `## Intelligence Context` section from a plan file? (They should not — it's for human review only. Job B reads `## Discoveries` and `## Amendments`, not `## Intelligence Context`.)
- The `## Constraints` section lists non-negotiable constraints from module pages, labeled `[source: module-page]`. These sit alongside spec requirements. Could a constraint from a module page contradict a spec requirement? If yes, what should happen? (Suggested answer: the engineer resolves the contradiction during planning review — the plan's `**Engineer review prompt**` for the affected phase should flag it.)

---

## Phase 4: Execution + Review Integrations

**Files in this phase:**
- Modify: `github/skills/execution/SKILL.md`
- Modify: `github/skills/review/SKILL.md`

- [ ] **Step 1: Add context packet check to inline execution mode in execution/SKILL.md**

In `github/skills/execution/SKILL.md`, find this block (the Step 2a heading and its opening):

```
## Step 2a: Inline Execution (`Execution mode: inline`)

Work through all steps sequentially:
1. Execute each step in order. Do not skip any. When a step requires reading existing code to understand a module or class, follow the **Codebase Search Protocol** in this skill.
```

Replace with:

```markdown
## Step 2a: Inline Execution (`Execution mode: inline`)

**Context packet check (run before any steps):**
1. Read `Context Packets:` path from `.github/skills/conventions/SKILL.md`.
2. Check for `[context-packets-path]/[ticket-id]/phase-1-context.md` (inline plans use a single phase; try `phase-1` first, then `phase-2` if not found).
3. If found: read the full context packet. Note the `Coverage confidence` field. Use `## Relevant Decisions` and `## Module Context` to frame your understanding before touching any code. Do not load additional module or knowledge pages from the index — the packet is the full context budget for this plan.
4. If not found: proceed without pre-loaded context. The Codebase Search Protocol remains available on demand throughout execution.

Work through all steps sequentially:
1. Execute each step in order. Do not skip any.
   Before making any change that affects a public interface, a dependency's behavior, or a constraint boundary (as defined in `## Relevant Decisions` in the context packet, if loaded): confirm the change does not conflict with any recorded decision. If it conflicts: stop immediately. Say: "This change conflicts with a recorded decision in the context packet: '[exact decision text]'. Should I revise the approach or proceed with an explicit override?" Do not continue without the engineer's response.
   When a step requires reading existing code to understand a module or class, follow the **Codebase Search Protocol** in this skill.
```

- [ ] **Step 2: Add context packet embed to phased subagent dispatch in execution/SKILL.md**

In `github/skills/execution/SKILL.md`, find this block (the Dispatch the subagent heading):

```
### Dispatch the subagent

Spin up a new `@Implementation Agent` sub-session with the following fully self-contained prompt.
The sub-session has NO access to the parent session — embed everything it needs.
Copy and complete the prompt below exactly, replacing bracketed placeholders with actual values from the plan:
```

Replace with:

```markdown
### Dispatch the subagent

**Before dispatching — context packet check:**
1. Read `Context Packets:` path from `.github/skills/conventions/SKILL.md`.
2. Read `[context-packets-path]/[ticket-id]/phase-[N]-context.md` if it exists.
3. If found: copy the full file content for embedding in the subagent prompt (CONTEXT_PACKET_CONTENT).
4. If not found: set CONTEXT_PACKET_CONTENT = `No context packet available. Use the Codebase Search Protocol for any module lookups during this phase.`

Spin up a new `@Implementation Agent` sub-session with the following fully self-contained prompt.
The sub-session has NO access to the parent session — embed everything it needs.
Copy and complete the prompt below exactly, replacing bracketed placeholders with actual values from the plan:
```

- [ ] **Step 3: Add context packet section and constraint-check rule to the subagent prompt in execution/SKILL.md**

In `github/skills/execution/SKILL.md`, find this block (the opening of the subagent prompt template, inside the fenced block):

```
You are implementing Phase [N]: [phase name] as part of ticket [ticket-id].

--- CONVENTIONS ---
[Paste the full raw text content of conventions/SKILL.md here]
--- END CONVENTIONS ---

FILES TO CHANGE IN THIS PHASE:
[List files from the phase block in the plan]

STEPS:
[Paste the exact numbered steps from the phase block]

RULES:
1. Execute steps in order. Do not skip any.
2. After each step, run the test command from CONVENTIONS.
```

Replace with (the `---` markers use the same convention as the existing template):

```
You are implementing Phase [N]: [phase name] as part of ticket [ticket-id].

--- CONVENTIONS ---
[Paste the full raw text content of conventions/SKILL.md here]
--- END CONVENTIONS ---

--- CONTEXT PACKET ---
[Paste CONTEXT_PACKET_CONTENT here — either the full phase-[N]-context.md content or the "No context packet available" message]
--- END CONTEXT PACKET ---

FILES TO CHANGE IN THIS PHASE:
[List files from the phase block in the plan]

STEPS:
[Paste the exact numbered steps from the phase block]

RULES:
1. Execute steps in order. Do not skip any.
2. Before making any change that affects a public interface, a dependency's behavior, or a constraint boundary: check ## Relevant Decisions in the CONTEXT PACKET (if available). If your change conflicts with a recorded decision: stop. Return the conflict to the parent session — do not proceed without acknowledgment.
3. After each step, run the test command from CONVENTIONS.
```

Note: the original rules 2–9 become rules 3–10. Renumber them accordingly in the file.

- [ ] **Step 4: Trace Scenario 4 (execution) — context packet is found**

Mental trace: Phased plan, Phase 2, ticket PROJ-123. Context packet exists at `context/PROJ-123/phase-2-context.md`. Coverage confidence = high. `## Relevant Decisions` contains: "AuthService: must use Redis for token storage — no in-memory caching (PROJ-89)."

Engineer's Phase 2 step says "Add in-memory cache for token lookup to reduce Redis latency." Subagent begins executing.

Confirm:
1. Dispatch step checks for the context packet. Found. CONTEXT_PACKET_CONTENT = full packet text.
2. Packet embedded in subagent prompt.
3. Subagent reads `## Relevant Decisions` before making changes.
4. Subagent attempts to implement in-memory token cache — conflicts with the recorded decision.
5. Subagent stops: "This change conflicts with a recorded decision in the context packet: 'AuthService: must use Redis for token storage — no in-memory caching (PROJ-89).' Should I revise the approach or proceed with an explicit override?"
6. Parent session presents conflict to engineer. Engineer decides how to proceed.

This satisfies the execution integration requirement from the spec.

- [ ] **Step 5: Add items 5–6 to the review skill's ticket debrief**

In `github/skills/review/SKILL.md`, find this block (the ticket debrief section):

```
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

Replace with:

```markdown
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
5. Check the knowledge index for pattern candidates on modules touched this ticket:
   Read `Knowledge Index:` path from `.github/skills/conventions/SKILL.md`. Read `[knowledge-index-path]/index.md`.
   Filter to rows where Module(s) contains any module touched this ticket AND Status includes `pattern-candidate`.
   If any found: surface each one and offer these options:
   > "Topic `[topic-name]` is a pattern-candidate (recurrence: [N], modules: [list]).
   > Summary: [one sentence from the topic's ## Summary].
   > Options:
   > **A** — Synthesize: I'll write a `## Pattern` section in the topic page now.
   > **B** — Retain as-is: mark `normalization: reviewed-no-change` and revisit later.
   > **C** — Merge with `[other-topic]`: flag for merge on next full `/index knowledge` run.
   > **D** — Split into `[proposed subtopics]`: flag for split on next full `/index knowledge` run.
   > **E** — Defer: revisit after [N] additional tickets."
   Execute the engineer's choice immediately:
   - **A:** Read `[knowledge-index-path]/[topic].md`. Write a `## Pattern` section using this format:
     ```
     ## Pattern
     _Confidence: [high|medium|low]_
     [One-sentence pattern statement describing the root cause and reliable resolution.]
     ```
     Confidence rubric: `high` = same root cause + same module(s) + same resolution pattern + ≥3 tickets; `medium` = same symptom + different resolutions; `low` = weak correlation.
   - **B:** Add to the topic page (after `## Summary`): `_normalization: reviewed-no-change — [YYYY-MM-DD]_`
   - **C:** Add to the topic page (after `## Summary`): `_merge-candidate: [other-topic] — flagged [YYYY-MM-DD], pending full rebuild_`
   - **D:** Add to the topic page (after `## Summary`): `_split-candidate: proposed [A] and [B] — flagged [YYYY-MM-DD], pending full rebuild_`
   - **E:** Add to the topic page (after `## Summary`): `_deferred: revisit after [N] tickets — [YYYY-MM-DD]_`
   If no pattern-candidates are found for touched modules: note "Pattern check: none — [YYYY-MM-DD]" and continue.
6. Run `/index knowledge --incremental` to update the knowledge index with this ticket's discoveries and amendments.
   → This closes the learning loop. The next ticket's retrieval will have this ticket's signals available.

---
```

- [ ] **Step 6: Trace Scenario 6 — Pattern synthesis at review**

Mental trace: Topic `token-invalidation-lag` has recurrence = 3, status = `active, pattern-candidate`. Review debrief for a ticket that touched `AuthService`.

Confirm:
1. Debrief item 5: knowledge index checked. `token-invalidation-lag` is a pattern-candidate for `AuthService` — touched this ticket.
2. Topic surfaced. Engineer chooses option A (Synthesize).
3. Reviewer reads `knowledge/token-invalidation-lag.md`. Writes `## Pattern`:
   ```
   ## Pattern
   _Confidence: high_
   When session IDs are regenerated without invalidating the prior token in Redis, the old token remains valid for up to the TTL window, allowing replay attacks.
   ```
4. File saved. Status in the knowledge index will update from `active, pattern-candidate` to `active` on the next `/index knowledge --incremental` run (item 6).
5. Debrief item 6 runs: `/index knowledge --incremental` triggered.

This satisfies Scenario 6 from the spec.

- [ ] **Step 7: Commit Phase 4**

```bash
git add github/skills/execution/SKILL.md github/skills/review/SKILL.md
git commit -m "feat: add context packet integration to execution; add knowledge maintenance to review debrief"
```

**Engineer review prompt:**
- The review debrief now ends with item 6: "Run `/index knowledge --incremental`." This is a required action before closing. Should it be inside the debrief block (making it an engineer responsibility) or should the review skill execute it automatically? The spec says "After debrief: run index knowledge --incremental" — which implies it runs as part of the review skill, not as a manual step. If the review skill should trigger it automatically, move item 6 from the debrief block to a "## Post-Debrief" step that runs after the engineer completes items 1–5.
- In Step 3 (subagent prompt renumbering), original rules 2–9 become rules 3–10. Confirm the renumbering is correct by reading the current rules list in execution/SKILL.md before editing — do not rely on the count in this plan, which may be off if the skill has been modified by another plan.

---

## Testing Checklist (run after all phases complete)

- [ ] Open `github/skills/retrieval-protocol/SKILL.md` — confirm activation gate stops at maturity=low; confirm loading budget table has hard limits for all 4 phases; confirm ticket-type classification is deterministic (first-match); confirm retrieval summary format has exactly 8 fields matching the spec's format (R8); confirm one-hop expansion stops at maximum one expansion
- [ ] Open `github/skills/brainstorming/SKILL.md` — confirm Intelligence Scan section appears before Entry Logic; confirm scan is silent (no announcement); confirm two framing variants (candidates found / not found) are both present
- [ ] Open `github/skills/spec-writing/SKILL.md` — confirm Decision Conflict Check section appears after the spec template prose and before Self-Review separator; confirm option B produces a `## Design Override` section in the spec; confirm "no conflicts" path notes the check result inline (R5)
- [ ] Open `github/skills/planning/SKILL.md` — confirm Intelligence Retrieval section appears before Before Writing a Single Step; confirm plan template has `## Intelligence Context` and `## Constraints` sections (both marked as optional); confirm low-maturity / absent-index fallback is explicit; confirm the Decision Conflict Check is referenced in the retrieval post-processing steps
- [ ] Open `github/skills/execution/SKILL.md` — confirm inline mode has context packet check before step 1; confirm phased mode has pre-dispatch context packet read; confirm CONTEXT_PACKET_CONTENT is embedded in the subagent prompt; confirm constraint-check rule is rule 2 and prior rules are renumbered; confirm the no-packet path ("not found") falls back to Codebase Search Protocol
- [ ] Open `github/skills/review/SKILL.md` — confirm debrief has items 1–6; confirm item 5 has all 5 options (A–E) with implementation instructions; confirm item 6 triggers `/index knowledge --incremental`; confirm pattern confidence rubric matches the spec (high/medium/low definitions)
- [ ] Run full end-to-end scenario trace — greenfield repo (6 modules): brainstorm intelligence scan skips; spec decision check skips (no index); planning retrieval skips; execution finds no context packet; review debrief items 5–6 still run (knowledge index may exist even for low-maturity repos). Verify no step errors out — all paths degrade gracefully.
- [ ] Run end-to-end scenario trace — mature repo (15 modules): brainstorm scan surfaces a candidate; spec check finds a conflict and blocks finalization; planning retrieval loads 2 module pages + 1 knowledge page; context packet written and embedded in execution; review debrief surfaces a pattern-candidate and synthesizes it; `/index knowledge --incremental` runs.

## Rollback Plan

- Revert all phase commits: `git revert HEAD~4` (4 commits, one per phase)
- No data migration required — all changes are to skill files; existing workflow artifacts are unaffected
- Plan 4a generation skills are unaffected by rolling back 4b — the generation layer stands independently
