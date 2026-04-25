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
- **Non-goals:** Does not modify source files; does not rebuild the codebase index (index-codebase's job); does not resolve contradictions automatically

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

**Contradiction detection (same-module pairs only):**

Check for contradictions between topics that share at least one module. Only compare pairs with a shared module — do not perform full pairwise comparison across all topics.

For each candidate pair, apply three gates in order. A pair is discarded if any gate fails.

**Gate 1 — Specificity:** Draft the one-line description for the `contradicts:` stub. It must name a concrete, specific thing in conflict: a parameter name, a threshold value, a contract obligation, or a behavioral guarantee. A general tension or difference in approach does not qualify.

- Disqualified: `— different approaches to session handling`
- Qualified: `— session timeout: topic-A specifies 30 min, topic-B specifies 15 min`

**Gate 2 — Signal strength:** At least one topic in the pair must have Weight = HIGH, OR both must have Weight ≥ MEDIUM. Discard pairs where both are LOW.

**Gate 3 — Per-run cap:** If ≥4 pairs pass Gates 1 and 2, keep only the 3 with the highest combined weight (max weight per topic, summed per pair). Record discarded candidates as UNCAPPED_PAIRS.

**Self-review pass:** After formulating all stubs that passed Gates 1–3, read each description once. Each must answer: "what specific thing conflicts?" Remove any that cannot. Re-apply Gate 2 and Gate 3 to the remaining set.

Store passing pairs as CONTRADICTION_PAIRS: `{topic_a, topic_b, description}`. These are written to topic pages in Step 10.

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
- `integrity-issues`: count of INTEGRITY_ISSUES (written after Step 11 runs; use 0 as placeholder when writing the index header, update after integrity check)

Write `[KNOWLEDGE_PATH]/index.md`:

    <!-- generated: YYYY-MM-DD | topics: N | recent-window: last-5-tickets OR 90-days | pattern-candidates: N | stale-candidates: N | unresolved: N | integrity-issues: N -->

    # Knowledge Index

    | Topic | Module(s) | Type | Weight | Validity | Recurrence | Recent | Impact | Last Ticket | Status |
    |---|---|---|---|---|---|---|---|---|---|
    | [topic-name] | [module list] | [type] | HIGH|MEDIUM|LOW | [validity] | N | yes|no | discovery|amendment|blocker | [TICKET-ID] | [status flags] |

    _(High-weight first, then alphabetical within weight tier.)_

    ## Unresolved Entries

    _(Entries that could not be associated with a known module. Resolve by adding the module to
    the codebase index or correcting the module name reference in the source artifact.)_

    | Date | Ticket | Type | Description |
    |---|---|---|---|
    | [YYYY-MM-DD] | [TICKET] | [type] | [description] |

Rules:
- All eight header fields (`topics`, `recent-window`, `pattern-candidates`, `stale-candidates`, `unresolved`, `integrity-issues` plus `generated` and the implied fields) must always be present. Never omit any field. This satisfies **R7**.
- If no unresolved entries, write "None." under `## Unresolved Entries`.

## Step 10: Write knowledge/[topic].md for Each Topic

For each topic in TOPICS, write `[KNOWLEDGE_PATH]/[topic-name].md`:

    # [Topic Name]
    _Type: [knowledge_type] | Modules: [module list] | Weight: [HIGH|MEDIUM|LOW] | Recurrence: N | Status: [status flags]_
    _Validity: valid | Last validated: —_

    ## Summary
    [1–2 sentence synthesis of the root cause and its observable effect, written from the entries.]

    ## Provenance
    - Source: `[artifact path of the first entry that created this topic]`
    - Evidence: [entry count and ticket IDs, e.g., "3 observations across TICKET-A, TICKET-B, TICKET-C"]
    - Validated by: —

    ## Entries
    _(High-weight entries first, then chronological within weight tier.)_
    - [YYYY-MM-DD] [TICKET-ID] | [type] | [Weight] | [description]
    _(Add [failed-mitigation] or [rejected-fix] tag on the same line where applicable.)_

    ## Related Modules
    - [`[Module]`](../codebase/[module].md) — [one sentence: how this module relates to this topic]

Notes on field values:
- `knowledge_type`: infer from source routing (spec/Design Rationale = system; numeric discovery/amendment = empirical; manually provided external = external). Default to `system` when ambiguous.
- `Validity` initialises to `valid`. `Last validated` initialises to `—` (unvalidated). Both are updated by the engineer after formal validation, or by index-knowledge when a contradiction is detected (see Step 6).
- `## Relationships`: omit entirely on first write. Added by index-knowledge (Step 6 contradiction stubs) or manually by engineers.
- `## Pattern`: omit on first write. Added by engineer at debrief when status includes `pattern-candidate`.

If the topic is flagged `merge-candidate`, add at the top (before the first heading):
```
> **Merge candidate:** This topic may overlap with [other-topic]. Review at next debrief — options: Merge, Retain as-is.
```

If the topic is flagged `split-candidate`, add at the top:
```
> **Split candidate:** This topic may cover two independent failure modes. Review at next debrief — options: Split into [A] and [B], Retain as-is.
```

**Write contradiction stubs (from CONTRADICTION_PAIRS):**

For each pair in CONTRADICTION_PAIRS where this topic is topic_a or topic_b:
- Add or append to the `## Relationships` section: `- contradicts: [[other-topic]] — [description]`
- Set `Validity: questionable` in header line 2

Create the `## Relationships` section if absent. Place it immediately after `## Provenance` (or after `## Summary` if `## Provenance` is absent).

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

**Relationship integrity check:**

Run after all topic pages and module pages are written.

**Scope:** Full run → all topic pages in `[KNOWLEDGE_PATH]/`. Incremental run → only topics modified or created in this run.

**Check 1 — Orphaned questionable:** For each in-scope topic, if header line 2 contains `Validity: questionable`, read its `## Relationships` section. If the section is absent OR contains no `contradicts:` line → record as INTEGRITY_ISSUES: `{topic, "validity=questionable but no contradicts relationship"}`.

**Check 2 — Orphaned superseded:** For each in-scope topic, if header line 2 contains `Validity: superseded`, search all topic pages for a line matching `supersedes: [[this-topic-name]]`. If not found in any page → record as INTEGRITY_ISSUES: `{topic, "validity=superseded but no supersedes reference found"}`.

No auto-fix. Detection only. Issues are reported in Step 13.

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
> - Contradictions written: [N pairs — "topic-A ↔ topic-B" for each, or "none"]
> - Potential contradictions not written (cap): [N — or "none"]
> - Relationship integrity: [N inconsistencies — or "clean"; list each as "topic-name: reason"]
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
