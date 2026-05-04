---
name: planning
description: Creates a phased implementation plan from a spec file by reading the actual codebase first. Generates concrete file-level steps with real paths — not placeholders. Use when ready to plan implementation after a spec is written and approved.
---

## Metadata

- **Name:** planning
- **Description:** Creates a grounded, phased implementation plan with real file paths and concrete steps — no placeholders allowed.
- **Phase:** 4 — Plan
- **Inputs:** Spec file path
- **Outputs:** Plan file at `[plans-path]/YYYY-MM-DD-[ticket-id]-[feature-name].md`
- **Non-goals:** Does not write code; does not execute steps; does not validate spec against test evidence

## When To Use

After a spec is written and reviewed. Do not plan without a spec. If a spec is missing, run `/write-spec` first. For `/quick-task` paths where a spec is consciously skipped, note this in the plan header.

## Inputs

- Spec file path (full path to the spec created in phase 3)

---

You are in plan phase. Create a phased implementation plan grounded in the actual code.

## Intelligence Retrieval (run before exploring the codebase)

1. Read `.github/skills/retrieval-protocol/SKILL.md`. Run the full retrieval protocol exactly as described — activation gate through retrieval summary (Steps 1–9 in the protocol).
2. **If index absent or maturity = low:** Skip retrieval. Proceed directly to "Before Writing a Single Step" below, using the full codebase search (step 2 in that section).
   **If index exists at any maturity above low:** Retrieval is mandatory. A skip without documented justification blocks the plan from being written.
3. **After retrieval completes:**
   a. Assemble the `## Intelligence Context` block from the retrieval summary. This block goes in the plan preamble (added in Step 2 of the plan structure update below).
   b. Collect all `## Known Constraints` lines from every loaded module page. These go in the `## Constraints` section of the plan preamble (also in Step 2 below). Label each: `[source: module-page]`. Treat them as non-negotiable — equivalent to spec requirements.
   c. Note which loaded knowledge entries have HIGH weight — use them to order phases (put riskier, higher-signal areas first) and to add risk notes to the relevant phase's `**Engineer review prompt:**`.
   d. **Populate `retrieval_modules`** (v2 only): Set `execution.retrieval_modules` in the plan artifact to the list of module names in LOADED_MODULES (from retrieval-protocol Step 7). If retrieval was skipped or LOADED_MODULES is empty, write `retrieval_modules: []`. This field is consumed by context-packet to surface planning overlap — it does not affect retrieval logic.
3. **Spec classification:**

### V2 (SPEC_VERSION = 2)
Read `problem.classification` from the spec artifact as a typed field. Pass it directly to the retrieval protocol's classification parameter — no prose inference:
- `new-feature` → retrieval priority: system › empirical › external
- `modification` or `bug-fix` → retrieval priority: empirical › system › external

### V1 (SPEC_VERSION = 1)
Not applicable — skip this step. Retrieval priority uses default ordering.

   d. **Decision Conflict Check:**

### V2 (SPEC_VERSION = 2)
Read `decisions[*].constraints[]` typed array from the spec artifact. Compare each constraint against `## Known Constraints` sections in loaded module pages. Flag where a spec constraint directly contradicts a module constraint.

Note: module pages are v1 prose. This check remains partially deterministic (typed spec input vs. prose module pages) until module pages adopt v2 typed decisions — acknowledged limitation in the design spec.

### V1 (SPEC_VERSION = 1)
Read `## Decisions` from every loaded module page; compare against the spec's `## Architecture / Design Decisions` prose.

Note: module pages are v1 prose. This check remains partially deterministic (typed spec input vs. prose module pages) until module pages adopt v2 typed decisions — acknowledged limitation in the design spec.

## Version Gate (run before any other step)

Read the spec file's `schema_version` frontmatter. Store as SPEC_VERSION.

### V2 (SPEC_VERSION = 2)
Run `/validate-artifact [spec-path] [brainstorm-path]` silently (includes immutability check against brainstorm source). BLOCK if validation fails. Use v2 typed-field paths throughout this skill.

### V1 (SPEC_VERSION = 1 or absent)
SPEC_VERSION = 1. Use existing prose extraction throughout. Version gates do not apply.

## Before Writing a Single Step

1. Read the spec file in full — understand every requirement and constraint.
2. Explore the codebase:
   - **If retrieval ran:** Start from the `## Public Interface` and `## Dependencies` sections of loaded module pages. Use `read_file` on referenced files to confirm their current state. Use `file_search` and `semantic_search` only for modules or files not covered by the loaded pages.
   - **If retrieval was skipped:** Use `list_dir`, `file_search`, `semantic_search`, and `read_file` to understand the codebase from scratch.
3. Map what needs to change and where — real files, real line ranges.

Only write steps after you have seen the actual code.

## Phase Quality Rules

Group steps into phases. A phase MUST satisfy all three:
1. ≤5 files changed
2. Represents a logical unit that can be reviewed independently — ask: "If I showed only these changes to a reviewer, could they say yes or no without seeing the rest?"
3. Each individual step within the phase takes 2–5 minutes. A step is too large if it contains "and" — split it.

Typical phase boundaries: by architectural layer (repository → service → controller), by feature area (auth module, notification module), or by change type (schema migration → model update → query update).

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

## Plan Quality Bar

Reject these in any step:
- A step that references `[ClassName].[ext]` or any placeholder path
- A step that says "add validation" or "implement feature" without showing where and how
- A step that cannot be completed in 2–5 minutes

Accept these:
- `src/auth/service.go:45 — add nil check before calling user.GetProfile()`
- `tests/auth/service_test.go — add test for nil user returning 401`

### Correct Granularity

```
Phase 1, Steps:
1. Write failing test: `test_rate_limiter_returns_429_after_5_attempts`
2. Run test — expected: FAIL (RateLimiter class not found)
3. Create `src/ratelimit/RateLimiter.java` with stub `checkLimit()` method
4. Run test — expected: FAIL (assertion error, stub returns wrong value)
5. Implement `checkLimit()` with Redis counter logic
6. Run test — expected: PASS
7. Commit: "AUTH-456 phase 1: rate limiter core logic"
```

### Too Coarse

```
Phase 1, Steps:
1. Create RateLimiter class with Redis integration, add tests, and wire into LoginController
```

This is too coarse because it contains "and" — split into atomic steps.

Read `.github/skills/conventions/SKILL.md` for the test command, build command, and plans path.

Create the plan file at: `[plans-path]/YYYY-MM-DD-[ticket-id]-[feature-name].md`

## Plan Structure

### V1 (SPEC_VERSION = 1)

~~~markdown
---
ticket: [TICKET-ID]
phase: plan
created: [YYYY-MM-DD]
status: draft
source: [spec-file-path]
---

# Implementation Plan: [TICKET-ID] — [Feature Name]

> **Execution mode:** [inline | phased-inline | phased-subagent] — [one-sentence justification]
> **Retrieval:** [ran | skipped — reason]

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

---

## Phase 1: [Logical unit name — e.g. "Repository layer"]

**Files in this phase:**
- `src/auth/UserRepository.java` — new interface
- `src/auth/UserRepositoryImpl.java` — new JPA implementation
- `tests/auth/UserRepositoryTest.java` — unit tests

**Steps:**
1. Create `src/auth/UserRepository.java`: define findById(Long id), findByEmail(String email) — follow interface pattern in src/common/BaseRepository.java
2. Create `src/auth/UserRepositoryImpl.java`: implement using JPA EntityManager (see src/common/BaseRepositoryImpl.java for pattern)
3. Create `tests/auth/UserRepositoryTest.java`: test findById returns Optional.empty() for unknown id; test findByEmail returns correct user

**Test after this phase:**
`[test command from conventions] [specific test class]`

**Engineer review prompt:**
- [Question tied to a risk — e.g. "Does the impl handle the case where Redis is unavailable, or does it throw?"]
- [Question tied to an existing pattern — e.g. "Does this follow the pattern in BaseRepositoryImpl.java, or does it introduce a new approach?"]

---

## Phase 2: [Next logical unit]
[same structure]

---

## Testing Checklist (run after all phases complete)
- [ ] [test command] — full suite, no regressions
- [ ] Manual: [exact steps to verify end-to-end]

## Rollback Plan
- Revert all phase commits: `git revert HEAD~[N]` where N = number of phases
- [Any data migration to reverse, if applicable]
~~~

### V2 (SPEC_VERSION = 2)
Use this YAML PlanArtifact instead of the V1 Markdown template above. Carry all spec fields verbatim — do not re-derive.

~~~yaml
---
ticket: [TICKET-ID]
phase: plan
schema_version: 2
created: [YYYY-MM-DD]
status: draft
source: [spec-file-path]
---

# ── INHERITED FROM SPEC — carry verbatim, byte-for-byte ──────────────────────
problem:
  id: "[from spec]"
  classification: "[from spec]"
  summary: "[from spec]"
  scope:
    - module: "[from spec]"
      known: [from spec]
  acceptance_signals:
    - "[from spec]"

open_decisions:
  [from spec — verbatim]

decisions:
  [from spec — verbatim]

requirements:
  [from spec — verbatim]

spec_constraints:
  [from spec — verbatim]

out_of_scope:
  [from spec — verbatim]

# ── OWNED BY PLANNING — write only these fields ────────────────────────────────
execution:
  mode: "[inline|phased-inline|phased-subagent]"
  justification: "[one sentence justifying mode choice]"
  retrieval: "[ran|skipped]"
  retrieval_justification: "[reason if skipped; empty string if retrieval ran]"
  retrieval_modules: []

retrieval_constraints:
  - "[constraint discovered from module pages — source: module-page: ModuleName]"

phases:
  - id: 1
    name: "[Phase name — logical unit description]"
    steps:
      - id: "P1.S1"
        phase: 1
        description: "[max 300 chars — what this step does]"
        files:
          - path: "[exact/file/path.ext]"
            operation: "[create|modify|delete]"
        depends_on: []
        verify: "[runnable command that proves this step complete]"
        risk_signals: []
        review_prompt: "[specific question for engineer to check after this step]"
        requirement_ids: ["R1"]

amendments: []
~~~

**Immutability rule:** All fields above the `# ── OWNED BY PLANNING` comment are inherited verbatim from the spec. Do not modify them. `/validate-artifact` at the consuming phase will byte-for-byte compare these fields against the spec source and BLOCK on any mismatch.

## Cross-Repo Auto-Risk-Signal Injection

### V2 (SPEC_VERSION = 2)
If `[knowledge-path]/imports.md` exists and is readable, run once before writing the plan artifact:

```
For each StepNode S across all phases:
  For each FileRef F in S.files:
    module = resolve(F.path)   # same rule as context-packet: longest prefix → Reach score → alphabetical
    For each import_source in imports.md:
      If module ∈ import_source.scope (exact string match):
        If "API Conventions" ∉ S.risk_signals:
          Append "API Conventions" to S.risk_signals
```

Rules:
- Silent no-op when `imports.md` is absent or unreadable — no warning.
- Only injects `"API Conventions"`. Does not infer or inject other section names.
- Does not remove or replace existing `risk_signals[]` entries. Appends only.
- Injection is visible in the written plan artifact. Engineer may remove false-positive entries before approving.

### V1 (SPEC_VERSION = 1)
Not applicable — skip this step.

## No Placeholders

Every step contains either a code block showing the implementation or an exact command showing the verification. No exceptions.

Reject these patterns in any plan step:
- "TBD" / "TODO" / "implement later"
- "Add appropriate error handling" (vague — specify what error, what handling)
- "Similar to Step N" (subagents can't see other steps — repeat the content)
- "Follow existing patterns" (specify which pattern, which file)
- `[ClassName]` / `[methodName]` / `[path]` (placeholder syntax — use real names)

If you catch yourself writing any of these, stop and fill in the actual content.

---

## Output Format

Plan file at `[plans-path]/YYYY-MM-DD-[ticket-id]-[feature-name].md` containing:
- Execution mode declaration, All Files Changed table, phased steps with real paths, test commands, engineer review prompts, Testing Checklist, Rollback Plan

## Dependencies

- `.github/skills/conventions/SKILL.md` — for test command, build command, plans path
- Spec file (path provided as input)

## Self-Review (before handoff)

Before handing off to `/execute-plan`, review the plan you just wrote. Fix issues inline — no separate review cycle.

1. **Spec coverage:** Skim each section/requirement in the spec. Can you point to a task that implements it? List any gaps — add missing tasks.
2. **Placeholder scan:** Apply the No Placeholders checklist above. Fix any violations.
3. **Step independence:** Could a subagent execute each phase using only the steps in that phase, without seeing other phases? If not, add the missing context.
4. **Type consistency:** Do the types, method signatures, and property names used in later phases match what was defined in earlier phases? A function called `clearLayers()` in Phase 1 but `clearFullLayers()` in Phase 3 is a bug.

## Handoff

Next: `/execute-plan [plan-file-path]` in a new chat.

Apply context hygiene before closing this chat.
