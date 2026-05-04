# Codebase Simplification Signals Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add advisory simplification signals to codebase indexing and repair two known audit defects — without changing the slash-command surface, without automatic refactoring, and without new workflow steps.

**Architecture:** Execute in strict dependency order. Phase 1 repairs must land first (ghost directory removal unblocks clean skill counts; validate-artifact.sh repairs unblock accurate artifact integrity). Phases 2–4 extend existing files only — no new skills, no new commands, no new artifact types. Phase 5 documentation is coupled to the behavior it describes. Phase 6 is mechanical verification only.

**Tech Stack:** Markdown artifacts under `github/`, shell script under `github/scripts/`, verification via `rg`, `wc`, `test`, and direct script execution.

**Spec reference:** `docs/superpowers/specs/2026-04-30-simple-capability-uplift-design.md` (audit repairs); inline analysis from 2026-04-30 simplification-signals review session.

---

## Non-Goals

- No automatic refactoring of source code
- No business logic changes
- No class, function, or feature deletion
- No package moves during indexing
- No new slash command
- No new artifact type or skill
- No changes to Stage 1, Stage 2, or Stage 3 gate logic

---

## All Files Changed

**Phase 1 — Audit repairs:**
- Delete: `github/skills/validate-artifact/` (empty ghost directory)
- Modify: `github/scripts/validate-artifact.sh`

**Phase 2 — Extend index-codebase skill:**
- Modify: `github/skills/index-codebase/SKILL.md`

**Phase 3 — Update architecture.md output format:**
- Modify: `github/skills/index-codebase/SKILL.md` (already opened in Phase 2 — single edit pass)

**Phase 4 — Thread signals into planning:**
- Modify: `github/skills/planning/SKILL.md`

**Phase 5 — Documentation:**
- Modify: `github/WORKFLOW.md`
- Modify: `github/CHEAT-SHEET.md`
- Modify: `github/ARCHITECTURE.md`

---

## Phase 1 — Audit Repairs

_Dependency: none. Execute first._

### Step 1.1 — Delete empty ghost directory

- [ ] Run: `rm -rf github/skills/validate-artifact/`
- [ ] Verify: `test ! -d github/skills/validate-artifact && echo "PASS: ghost dir removed" || echo "FAIL"`
- [ ] Verify skill count: `ls github/skills/ | wc -l` — should be 16 (was 17 with the empty dir)

**Files changed:** directory deletion only — no Markdown files touched.

---

### Step 1.2 — Add required-field checks to `validate-artifact.sh`

Current script checks: `schema_version: 2`, ID uniqueness, `source_decision` referential integrity, `depends_on` referential integrity, and inherited-field immutability. Missing: required-field presence on each primitive, and explicit id-format compliance.

**Edit `github/scripts/validate-artifact.sh`:**

After the `schema_version` check and before the duplicate-ID checks, insert required-field checks for each primitive type:

```bash
# Required fields: DecisionRecord
while IFS= read -r block_start; do
  block=$(awk "NR>=${block_start}" "$artifact" | sed -n '1,/^  - id:/{ /^  - id:/q; p}')
  printf '%s\n' "$block" | rg -q 'question:' || add_fail "decisions — missing required field: question (near line ${block_start})"
  printf '%s\n' "$block" | rg -q 'options:' || add_fail "decisions — missing required field: options (near line ${block_start})"
  printf '%s\n' "$block" | rg -q 'chosen:' || add_fail "decisions — missing required field: chosen (near line ${block_start})"
done < <(rg -n '^  - id: "D[0-9]+"' "$artifact" | cut -d: -f1)

# Required fields: Requirement
while IFS= read -r block_start; do
  block=$(awk "NR>=${block_start}" "$artifact" | sed -n '1,/^  - id:/{ /^  - id:/q; p}')
  printf '%s\n' "$block" | rg -q 'description:' || add_fail "requirements — missing required field: description (near line ${block_start})"
done < <(rg -n '^  - id: "R[0-9]+"' "$artifact" | cut -d: -f1)

# Required fields: StepNode
while IFS= read -r block_start; do
  block=$(awk "NR>=${block_start}" "$artifact" | sed -n '1,/^    - id:/{ /^    - id:/q; p}')
  printf '%s\n' "$block" | rg -q 'files:' || add_fail "steps — missing required field: files (near line ${block_start})"
  printf '%s\n' "$block" | rg -q 'verify:' || add_fail "steps — missing required field: verify (near line ${block_start})"
done < <(rg -n 'id: "P[0-9]+\.[Ss][0-9]+"' "$artifact" | cut -d: -f1)
```

After the required-field blocks, add explicit id-format rejection for any ID that was extracted but doesn't match the expected pattern:

```bash
# ID format compliance
while IFS= read -r id; do
  [[ -z "$id" ]] && continue
  [[ "$id" =~ ^D[0-9]+$ ]] || add_fail "decisions.id — format violation: ${id} (expected D<N>)"
done < <({ rg -o '^  - id: "[^"]+"' "$artifact" || true; } | rg '"D' | sed -E 's/.*"(D[^"]+)".*/\1/')

while IFS= read -r id; do
  [[ -z "$id" ]] && continue
  [[ "$id" =~ ^R[0-9]+$ ]] || add_fail "requirements.id — format violation: ${id} (expected R<N>)"
done < <({ rg -o '^  - id: "[^"]+"' "$artifact" || true; } | rg '"R' | sed -E 's/.*"(R[^"]+)".*/\1/')
```

- [ ] Apply the edits above to `github/scripts/validate-artifact.sh`
- [ ] Verify line count: `wc -l github/scripts/validate-artifact.sh` — expect 100–130 lines

**Acceptance tests:**

- [ ] Construct `test-invalid.md` with a decision block missing `chosen:`. Run:
  `zsh github/scripts/validate-artifact.sh test-invalid.md`
  Expected: exit 1, output contains `FAIL: decisions — missing required field: chosen`

- [ ] Run against a known-good V2 artifact:
  `zsh github/scripts/validate-artifact.sh docs/superpowers/specs/2026-04-30-simple-capability-uplift-design.md`
  Expected: exit 0, no output (note: spec uses `schema_version: 1` in frontmatter — this will fail the schema check; use a plan artifact instead if available, or skip this acceptance test and note that a V2 plan artifact is the correct target)

- [ ] Confirm `run-silent.sh` behavior still intact (not touched by this phase):
  `zsh -c 'source github/scripts/run-silent.sh && run_silent true && echo "exit=$?"'`
  Expected: `✓`, `exit=0`

**Files changed:** `github/scripts/validate-artifact.sh`

---

## Phase 2 — Extend `index-codebase/SKILL.md` with Simplification Signals

_Dependency: Phase 1 complete._

**Edit `github/skills/index-codebase/SKILL.md`:**

Insert a new `## Step 12b: Compute Simplification Signals` block between Step 12 (Write module pages) and Step 13 (Write architecture.md). The new step defines detection, ranking, and the false-positive warning. Step 13's architecture.md template is updated in Phase 3.

### Step 2.1 — Insert Step 12b

- [ ] After the last line of Step 12 and before `## Step 13`, insert:

```markdown
## Step 12b: Compute Simplification Signals

Run after writing all module pages. Read the MODULES list and source files already
analysed. Do NOT read additional source files beyond what Step 3 collected.

### Detection Rules

**Signal type 1 — Utility dumping ground**
- Trigger: module whose primary path contains `utils`, `helpers`, `common`, or `shared`
  AND whose Reach (direct) is below the median across all modules.
- Confidence: HIGH if below median; MEDIUM if at median.
- Suppress if: conventions `Forbidden packages` already lists the path pattern
  (the system has already declared it forbidden — no need to re-signal).

**Signal type 2 — Responsibility mismatch**
- Trigger: module assigned to one layer (from architecture.md Layers table) whose inferred
  responsibility text contains keywords that imply a different layer
  (e.g., SQL/ORM keywords in a `controller`-layer module; HTTP/route keywords in a
  `repository`-layer module).
- Confidence: MEDIUM — always mark with `[verify]` suffix; never HIGH.
- Suppress if: module has a manual boundary entry in module-map.md with a stated responsibility
  (the human has already reviewed and named it).

**Signal type 3 — One-use abstraction**
- Trigger: module with exactly 1 dependent in the Dependents list AND fewer than 3 source
  files AND all source files are under 80 lines each.
- Confidence: HIGH if 1 dependent; MEDIUM if 2 dependents.
- Suppress if: module has any detected entry points (Step 6) — entry point modules are
  not candidates for inlining regardless of size.

**Signal type 4 — Mixed-responsibility file**
- Trigger: a single source file over 400 lines that contains class names (or function groups)
  whose name patterns imply membership in more than one distinct layer
  (e.g., `UserController` and `UserRepository` defined in the same file).
- Confidence: HIGH.
- Report: file path, line count, conflicting class/function names.
- Note: this is a file-level signal, not a module-level signal. Report the file path,
  not the module name.

**Signal type 5 — Scattered helpers**
- Trigger: a utility function name prefix (`parse_`, `format_`, `validate_`, `convert_`,
  `serialize_`) found independently defined (not imported) in 3 or more distinct modules.
- Detection: use `grep_search` for each prefix pattern across SOURCE_FILES.
- Confidence: MEDIUM — always mark with `[verify]` suffix.
- Suppress if: the function names differ in the body (false match on prefix only).

### Ranking and Cap

Score each signal:
- HIGH confidence = 3 points
- MEDIUM confidence = 1 point
- Add Reach (direct) of the affected module (or 0 for file-level signals).

Sort descending by score. Take top 5 only. Discard the rest — do not report them.
If more than 5 HIGH signals exist, suppress all MEDIUM signals from the output.

Store as SIMPLIFICATION_SIGNALS: list of `{type, target, confidence, reason}` where
`target` is the module name for types 1–3 and 5, or the file path for type 4.

⚠️ False-positive warning: simplification signals are inferred from structural patterns
only. A signal does not mean the code is wrong or must be changed. Each signal must be
evaluated by an engineer against actual behavior before any action is taken. Do NOT
convert signals into plan steps without an explicit brainstorm and spec cycle. Signals
involving shared infrastructure (e.g., a `utils` module with Reach (direct) > 5) are
likely false positives even at HIGH confidence.
```

- [ ] Verify insertion: `rg -n "Step 12b" github/skills/index-codebase/SKILL.md` — must match exactly once, between Step 12 and Step 13

**Files changed:** `github/skills/index-codebase/SKILL.md`

---

## Phase 3 — Update `architecture.md` Output Format

_Dependency: Phase 2 complete. Same file as Phase 2 — continue editing._

### Step 3.1 — Add `## Simplification Signals` section to Step 13 template

- [ ] In Step 13 of `github/skills/index-codebase/SKILL.md`, after the `## Extension Points` block in the architecture.md template, add:

```markdown
    ## Simplification Signals (advisory — requires explicit refactor ticket to act on)

    <!-- generated: YYYY-MM-DD | signals: N | cap: 5 -->

    | Signal type | Target | Confidence | Reason |
    |---|---|---|---|
    | [type name] | [module or file path] | HIGH / MEDIUM [verify] | [one-sentence reason] |

    ⚠️ Advisory only. Do not add to an existing feature ticket.
    Do not move, rename, or delete any code based solely on this table.
    Each signal requires: brainstorm → spec with behavior-preservation plan → plan → execute.
```

  Write `_No signals detected._` as the sole content under the header when
  SIMPLIFICATION_SIGNALS is empty after ranking and cap.

### Step 3.2 — Verify section ordering in template

- [ ] Confirm the generated `architecture.md` section order is:
  1. `## Layers`
  2. `## Placement Heuristics`
  3. `## Existing Anti-Patterns (frozen — do not add to)`
  4. `## Extension Points`
  5. `## Simplification Signals (advisory — requires explicit refactor ticket to act on)`

  Anti-patterns and simplification signals must remain distinct:
  - Anti-patterns = frozen bad patterns; do not copy
  - Simplification signals = existing structural opportunities; investigate before acting

- [ ] Verify: `rg -n "Simplification Signals" github/skills/index-codebase/SKILL.md` — must match at least twice (Step 12b definition + Step 13 template)

**Files changed:** `github/skills/index-codebase/SKILL.md`

---

## Phase 4 — Thread Signals into Planning (Read-Only)

_Dependency: Phase 3 complete._

### Step 4.1 — Amend planning Structural Analysis step

- [ ] In `github/skills/planning/SKILL.md`, in the `## Structural Analysis` section, after step 5 (`Choose one canonical follows_pattern path`), add step 5b:

```markdown
5b. If `architecture.md` contains a `## Simplification Signals` section with one or more
    HIGH-confidence signals: read it. If any signal targets a module touched by this plan,
    note it in `structural_constraints.packaging_rationale` as context only
    (e.g., `"auth module has a scattered-helpers signal — prefer modifying existing
    AuthUtils.parse* rather than adding new helpers"`).
    Do NOT add a simplification or cleanup step to the plan unless the ticket
    description explicitly requests structural cleanup.
```

- [ ] Verify: `rg -n "Do NOT add a simplification" github/skills/planning/SKILL.md` — must match

**Files changed:** `github/skills/planning/SKILL.md`

---

## Phase 5 — Documentation

_Dependency: Phases 1–4 complete. All three doc files updated in this phase._

### Step 5.1 — Update `WORKFLOW.md`

- [ ] In the `## Artifact Format` section, after the `refs/schema.md` reference sentence, add:
  > Running `/index codebase` also generates a `## Simplification Signals` section in
  > `index/architecture.md` — advisory structural opportunities (capped at 5) that require
  > a dedicated refactor ticket before any action is taken.

**Files changed:** `github/WORKFLOW.md`

### Step 5.2 — Update `CHEAT-SHEET.md`

- [ ] In the `## Structural Constraints` table, add one row after the `Conscious structural override` row:
  ```
  | `index/architecture.md § Simplification Signals` | Advisory: up to 5 structural cleanup opportunities — requires refactor ticket to act on |
  ```

**Files changed:** `github/CHEAT-SHEET.md`

### Step 5.3 — Update `ARCHITECTURE.md`

- [ ] In the `## Structural Discipline` section, after the four-layer table and the Stage 3 note, add:

```markdown
### Simplification Signals

Generated by `/index codebase` and written to `index/architecture.md § Simplification Signals`.
Five signal types are detected: utility dumping grounds, responsibility mismatches,
one-use abstractions, mixed-responsibility files, and scattered helpers. Output is capped
at 5 signals, ranked by confidence and module reach.

**Signals are advisory only.** No signal may generate a plan step without an explicit
brainstorm and spec. No code is moved, renamed, or deleted during indexing.

Non-goals (prescriptive — require a new spec to change):
- No automatic refactoring
- No package moves during indexing
- No new slash command for simplification
- No new artifact type

If future signal volume warrants a dedicated file (`index/simplification.md`), that
is a schema evolution proposal, not an implementation decision.
```

**Files changed:** `github/ARCHITECTURE.md`

---

## Phase 6 — Verification

_Dependency: All phases complete._

**Structural checks:**

- [ ] `test ! -d github/skills/validate-artifact && echo "PASS" || echo "FAIL: ghost dir still exists"`
- [ ] `ls github/skills/ | wc -l` — expect 16
- [ ] `wc -l github/scripts/validate-artifact.sh` — expect 100–130 lines
- [ ] `wc -l github/skills/index-codebase/SKILL.md` — expect 310–360 lines (was 299)
- [ ] `wc -l github/skills/planning/SKILL.md` — expect 68–72 lines (was 66, +step 5b)

**Content checks:**

- [ ] `rg "required field\|missing required" github/scripts/validate-artifact.sh` — must match
- [ ] `rg "format violation" github/scripts/validate-artifact.sh` — must match
- [ ] `rg "Step 12b" github/skills/index-codebase/SKILL.md` — must match exactly once
- [ ] `rg "Simplification Signals" github/skills/index-codebase/SKILL.md | wc -l` — expect ≥ 2
- [ ] `rg "Do NOT add a simplification" github/skills/planning/SKILL.md` — must match
- [ ] `rg "Simplification Signals" github/ARCHITECTURE.md github/WORKFLOW.md github/CHEAT-SHEET.md` — all three must match

**No-new-command check:**

- [ ] `rg "simplify-codebase|/simplify" github/` — must return zero results

**Advisory-label check:**

- [ ] `rg "advisory|requires explicit refactor" github/skills/index-codebase/SKILL.md` — must match
- [ ] `rg "Advisory only" github/CHEAT-SHEET.md` — must match

**Script behavior:**

- [ ] `zsh -c 'source github/scripts/run-silent.sh && run_silent true'` — prints `✓`, exit 0
- [ ] `zsh -c 'source github/scripts/run-silent.sh && run_silent false; echo "exit=$?"'` — prints `exit=1`

**Minor cleanup note (non-blocking):**

- [ ] `rg "No prose extraction" github/skills/spec-writing/SKILL.md` — V1-era comment still present; flag for removal in Phase 3+ skill-merge work. Does not block this plan.
