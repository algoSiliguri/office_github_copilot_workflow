---
name: validate-artifact
description: Validates a v2 artifact against schema invariants, referential integrity, and immutability rules. Runs silently at the start of each consuming skill before any work begins. Also user-invokable as /validate-artifact [artifact-path] for debugging.
---

## Metadata

- **Name:** validate-artifact
- **Phase:** Pre-phase validation — runs silently inside consuming skills; also user-invokable
- **Inputs:** Artifact file path. Optionally a source artifact file path (enables Check 5: immutability).
- **Outputs:** `PASS` (silent when invoked internally) or itemized `FAIL` list with field paths.

---

You are validating a v2 artifact. All checks are exact comparisons — no semantic judgments.

## Silent vs. Direct Invocation

**When invoked silently (inside a consuming skill at phase start):**
On `PASS`: proceed — do not surface validation to the engineer.
On any `FAIL`: stop immediately with:

```
BLOCK — artifact validation failed:
1. [field.path]: [specific violation]
2. [field.path]: [specific violation]
```

Do not proceed with the consuming skill while any check fails.

**When invoked directly (`/validate-artifact [path]`):**
Report either:
- `Artifact at [path]: PASS — all checks passed.`
- `Artifact at [path]: FAIL — [N] violation(s) found:` followed by numbered list.

---

## Check 1: Schema Version Gate (Rule 1)

Read the artifact's YAML frontmatter. Look for `schema_version:`.

- **Absent:** artifact is v1. Output `PASS — v1 artifact, skip.` Stop all checks.
- **`schema_version: 2`:** proceed to Check 2.
- **Any other value:** FAIL — `schema_version: unsupported value '[value]'. Expected: 2`.

---

## Check 2: ID Uniqueness

Collect IDs from these arrays:
- `decisions[*].id` — must be unique within the decisions array
- `requirements[*].id` — must be unique within the requirements array
- All `phases[*].steps[*].id` values across all phases — must be globally unique

For each array where any ID appears more than once: FAIL — `[array path][index].id: duplicate id '[id]'`

---

## Check 3: Referential Integrity

For each reference, verify the target ID exists:

| Source field | Target field |
|---|---|
| `requirements[*].source_decision` (non-null) | `decisions[*].id` |
| `phases[*].steps[*].requirement_ids[*]` | `requirements[*].id` |
| `phases[*].steps[*].depends_on[*]` | any `phases[*].steps[*].id` (globally) |

For each broken reference: FAIL — `[source.field.path]: '[value]' not found in [target field path]`

---

## Check 4: Cross-Field Invariants

Check all invariants from `github/skills/SCHEMA.md`:

1. `problem.scope[*].module` values unique within scope array
2. `problem.acceptance_signals` array non-empty
3. Each `DecisionRecord`: `chosen` value not present in any `rejected[*].option`
4. Each `DecisionRecord`: if `reversibility = 'low'` then `constraints.length >= 1`
5. Each `StepNode.id`: the phase number extracted from the pattern `P{N}.S{M}` matches the `phase` field value `N`
6. Each `StepNode.files[*].path` unique within the step
7. Each `StepNode.files[*].path` unique across all steps within the same phase (same `phase` field value)

For each violation: FAIL — `[field path]: [invariant description]`

---

## Check 5: Immutability (only when source artifact path is provided)

Compare each inherited field in the artifact being validated against the corresponding field
in the source file. Fields must match byte-for-byte.

**SpecArtifact (source = BrainstormArtifact):** compare `problem`, `open_decisions`
**PlanArtifact (source = SpecArtifact):** compare `problem`, `open_decisions`, `decisions`, `requirements`, `spec_constraints`, `out_of_scope`

If any inherited field differs: FAIL — `[field path]: inherited field modified. Auto-fix: prohibited. Return to the phase that owns this field.`

---

## Output Format

**PASS (direct invocation):**
```
Artifact at [path]: PASS — all checks passed.
```
(Silent when invoked internally.)

**FAIL:**
```
BLOCK — artifact validation failed:
1. decisions[1].id: duplicate id 'D2'
2. phases[0].steps[2].requirement_ids[0]: 'R9' not found in requirements[*].id
3. phases[1].steps[0].id: 'P2.S1' — phase segment '2' does not match phase field '1'
```

---

## Dependencies

- `github/skills/SCHEMA.md` — canonical invariant definitions

## Notes

This skill is read-only. It never modifies any artifact file.
