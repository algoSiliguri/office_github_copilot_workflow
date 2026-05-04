# Planning Context Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persist planning-phase retrieval outputs in the plan artifact and surface module overlap in context packets, creating the observability foundation for future FT2/FT3 optimizations.

**Architecture:** Add an optional `execution.retrieval_modules` field to v2 PlanArtifact (non-breaking). Context-packet reads this field (v2) or parses the `## Intelligence Context` prose block (v1) to identify which modules were already loaded at planning time, then notes overlap in the packet header. No behavioral change to loading — pure observability. FT3 (secondary knowledge map) and FT2 (abbreviated loading) are explicitly deferred: FT3 until knowledge topics reach ~30; FT2 until a safe solution for blast-radius context is designed.

**Tech Stack:** Markdown skill files, GitHub Copilot Workflow System (`.github/skills/`)

**Deferred explicitly:**
- FT3 (secondary module-topic map) — knowledge base is near-empty; implement when topics ≥ 30
- FT2 (abbreviated module loading) — correctness risk: execution agents require full module context; no safe solution identified

---

### Task 1: Add `retrieval_modules` to v2 PlanArtifact template

**Files:**
- Modify: `github/skills/planning/SKILL.md`

**What and why:** The v2 PlanArtifact currently captures execution mode, retrieval status, and retrieval constraints — but not which modules were actually loaded during planning retrieval. Adding `retrieval_modules: []` as an optional field under `execution:` closes this gap without breaking any existing consumer (optional field, non-breaking per Rule 4 of the v2 artifact model).

- [ ] **Step 1: Locate the v2 PlanArtifact template in planning/SKILL.md**

Find the `### V2 (SPEC_VERSION = 2)` section. The `execution:` block currently reads:

```yaml
execution:
  mode: "[inline|phased-inline|phased-subagent]"
  justification: "[one sentence justifying mode choice]"
  retrieval: "[ran|skipped]"
  retrieval_justification: "[reason if skipped; empty string if retrieval ran]"
```

- [ ] **Step 2: Add `retrieval_modules` field to the execution block**

Replace the execution block above with:

```yaml
execution:
  mode: "[inline|phased-inline|phased-subagent]"
  justification: "[one sentence justifying mode choice]"
  retrieval: "[ran|skipped]"
  retrieval_justification: "[reason if skipped; empty string if retrieval ran]"
  retrieval_modules: []
```

`retrieval_modules` is a list of module names loaded during retrieval (from LOADED_MODULES after retrieval-protocol Step 7 completes). Empty list `[]` when retrieval was skipped or no modules were loaded. Optional field — consuming skills treat its absence identically to an empty list.

- [ ] **Step 3: Add population instruction to the Intelligence Retrieval section**

In the `## Intelligence Retrieval` section of planning/SKILL.md, after Step 3 which says "After retrieval completes... Assemble the `## Intelligence Context` block", add:

```
   d. **Populate `retrieval_modules`** (v2 only):
      Set `execution.retrieval_modules` in the plan artifact to the list of module names
      in LOADED_MODULES (from retrieval-protocol Step 7). If retrieval was skipped or
      LOADED_MODULES is empty, write `retrieval_modules: []`.
      This field is consumed by context-packet to surface planning overlap.
```

Add this as step `d` after the existing step `c` (High-weight knowledge entries for risk ordering) and before the existing step `d` (Decision Conflict Check — which will become step `e`).

- [ ] **Step 4: Verify the template reads correctly**

Re-read the modified section of `github/skills/planning/SKILL.md` and confirm:
- `retrieval_modules: []` appears in the v2 execution block
- The population instruction is present in the Intelligence Retrieval section
- The step lettering is sequential (a, b, c, d, e) with no gaps or duplicates
- No other section of the file was inadvertently altered

- [ ] **Step 5: Commit**

```bash
git add "github/skills/planning/SKILL.md"
git commit -m "planning: add retrieval_modules to v2 PlanArtifact execution block"
```

---

### Task 2: Surface planning overlap in context-packet

**Files:**
- Modify: `github/skills/context-packet/SKILL.md`

**What and why:** Context-packet currently loads module pages for PHASE_MODULES with no awareness of what planning already loaded. Adding a pre-step that extracts PLANNING_LOADED (from the plan) and noting overlap in the packet header gives the executing agent — and the reviewing engineer — visibility into which modules are being re-loaded versus newly loaded. No change to what gets loaded; pure observability.

- [ ] **Step 1: Add Step 5.0 — Extract PLANNING_LOADED from the plan**

At the start of `## Step 5: Load Condensed Module Pages`, insert a new labeled sub-step before the existing loading logic:

```
**Step 5.0: Extract PLANNING_LOADED**

Before loading any module pages, identify which modules were loaded at planning time:

### V2 (PLAN_VERSION = 2)
Read `execution.retrieval_modules` from the plan file. Store as PLANNING_LOADED.
If the field is absent or empty: PLANNING_LOADED = [].

### V1 (PLAN_VERSION = 1)
Search the plan for `## Intelligence Context`. If found, read the line beginning with
`- Modules loaded:`. Parse the comma-separated list of module names that follows the
colon. Trim whitespace. Store as PLANNING_LOADED.
If `## Intelligence Context` is absent, or the line is missing, or the value is `none`:
PLANNING_LOADED = [].

PLANNING_LOADED is used only for observability — it does not alter which sections are
loaded or how module pages are processed. All modules in PHASE_MODULES receive the same
full condensed view regardless of whether they appear in PLANNING_LOADED.
```

- [ ] **Step 2: Compute OVERLAP for the packet header**

After Step 5.0 and before loading any module pages, compute:

```
OVERLAP = [m for m in PHASE_MODULES if m in PLANNING_LOADED and PLANNING_LOADED is non-empty]
OVERLAP_COUNT = len(OVERLAP)
```

Store OVERLAP and OVERLAP_COUNT for use in Step 8 (packet write) and Step 9 (report).

- [ ] **Step 3: Update Step 8 — add planning overlap line to packet header**

In Step 8, the existing packet header block reads:

```
**Generated:** YYYY-MM-DD
**Coverage confidence:** [high|medium|low]
**Phase files:** [count] files across [count] modules
**Unresolved files:** [list of unresolved file paths, or "none"]
```

Add one line after `**Coverage confidence:**`:

```
**Planning overlap:** [OVERLAP_COUNT] module(s) reloaded from planning context[: list if OVERLAP_COUNT > 0, else omit list]
```

Format rules:
- If OVERLAP_COUNT = 0: write `**Planning overlap:** 0 modules reloaded`
- If OVERLAP_COUNT > 0: write `**Planning overlap:** N module(s) reloaded from planning context: [comma-separated module names]`
- If PLANNING_LOADED = [] (no data): write `**Planning overlap:** not available (pre-retrieval plan)`

- [ ] **Step 4: Update Step 9 — add overlap to the report output**

In Step 9, the report currently reads:

```
> "Context packet written to `[CONTEXT_PATH]/[ticket-id]/phase-[N]-context.md`.
>
> - Coverage confidence: [level] — [reason if not high]
> - Modules in scope: [list]
> - Knowledge signals loaded: [N] topics (HIGH: N, MEDIUM: N)
> - Unresolved files: [list or "none"]
> - Unresolved files require direct codebase search (Plan 3) during execution."
```

Add one bullet after `Modules in scope`:

```
> - Planning overlap: [OVERLAP_COUNT] module(s) reloaded ([list or "none"])[; run /index knowledge --incremental if stale warning present]
```

- [ ] **Step 5: Verify the changes read correctly**

Re-read the modified sections of `github/skills/context-packet/SKILL.md` and confirm:
- Step 5.0 is clearly labeled and appears before the existing loading loop
- The v1/v2 version gates are present and correctly structured
- PLANNING_LOADED = [] default is stated for both paths (absent field, missing section, value "none")
- The explicit note that PLANNING_LOADED does NOT alter loading behavior is present
- Step 8 packet header has the new `**Planning overlap:**` line in the correct position
- Step 9 report has the new bullet in the correct position
- No other steps were inadvertently altered

- [ ] **Step 6: Commit**

```bash
git add "github/skills/context-packet/SKILL.md"
git commit -m "context-packet: surface planning module overlap in packet header and report"
```

---

### Task 3: Update ARCHITECTURE.md

**Files:**
- Modify: `github/ARCHITECTURE.md`

**What and why:** ARCHITECTURE.md sync policy states it must be updated in the same commit as any skill that changes decision logic. The planning overlap surfacing is a new observable behavior. The deferred optimizations need to be documented with explicit thresholds so they are not lost.

- [ ] **Step 1: Add `retrieval_modules` to the V2 Artifact Model section**

In `## V2 Artifact Model`, under `### Artifact Inheritance Chain`, find the note about `ContextPacketArtifact` being a projection. After that paragraph, or within the `PlanArtifact owns:` ownership line, add:

```
**`execution.retrieval_modules`** (optional list, default `[]`): Module names loaded during
planning-phase retrieval. Written by planning after retrieval-protocol Step 7 completes.
Read by context-packet to compute planning overlap. Non-breaking addition — consuming
skills treat absence as empty list. Not a v2 requirement; absent in v1 plans.
```

- [ ] **Step 2: Add planning overlap note to Context Packet Behavior section**

In `## Context Packet Behavior`, under `### Content`, the current bullet list ends with "Coverage confidence level." Add:

```
- Planning overlap annotation: count and names of modules reloaded from planning context
  (sourced from `execution.retrieval_modules` in v2 plans, or `## Intelligence Context`
  prose in v1 plans). Observability only — does not alter loading behavior.
```

- [ ] **Step 3: Add deferred optimizations note to the end of Context Packet Behavior**

After the `### User Responsibility` subsection, add:

```
### Deferred Optimizations

Two optimizations were analyzed and explicitly deferred:

**FT3 — Secondary module-topic map:** When `[knowledge-index-path]/index.md` contains ≥ 30
topics, consider implementing a secondary index (`knowledge/.module-topic-map.md`) mapping
module names to topic IDs and weights. This eliminates the O(topics) full-index scan
context-packet currently performs per phase. Not yet implemented — knowledge base below threshold.
Implementing this requires: (a) index-knowledge writes the map; (b) context-packet reads it
as a fast path; (c) filtering logic remains in context-packet, not index-knowledge, to
preserve the component boundaries in the Knowledge Layer section.

**FT2 — Abbreviated module loading:** Deferred indefinitely. Execution-phase agents operate
with no memory of what planning loaded — the context packet is their sole source of module
knowledge. Skipping `## Entry Points` and `## Public Interface` for planning-overlapping
modules deprives execution of blast-radius context. No safe solution identified.
```

- [ ] **Step 4: Update the `updated:` date at the top of ARCHITECTURE.md**

Change `updated: 2026-04-17` to `updated: 2026-04-26`.

- [ ] **Step 5: Verify ARCHITECTURE.md reads consistently**

Re-read the modified sections and confirm:
- The `retrieval_modules` field description is in the V2 Artifact Model section
- The planning overlap bullet is in Context Packet Behavior → Content
- The Deferred Optimizations subsection correctly attributes FT3 threshold (30 topics) and FT2 reason
- The FT3 component boundary note matches the existing Knowledge Layer component boundaries table
- The `updated:` date is correct
- No other sections were inadvertently altered

- [ ] **Step 6: Commit**

```bash
git add "github/ARCHITECTURE.md"
git commit -m "docs: document retrieval_modules field, planning overlap, and deferred optimizations"
```

---

## Self-Review

**Spec coverage:** The implemented scope addresses FT1 partial (persist planning retrieval outputs + surface overlap). FT2 and FT3 are documented as deferred with explicit rationale and thresholds. All three Tier 1 items from the analysis are accounted for.

**Placeholder scan:** No TBD, TODO, or vague steps. Each step specifies exact file sections to locate, exact text to insert, and what correct output looks like.

**Type consistency:** No types or function signatures involved — Markdown skill files only. Field names used consistently: `retrieval_modules` (planning template + population instruction + context-packet extraction + ARCHITECTURE.md description).

**Gaps:** None. The plan does not implement behavior that wasn't analyzed and approved. Deferred items are documented in ARCHITECTURE.md so they survive future sessions.
