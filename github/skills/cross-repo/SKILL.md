---
name: cross-repo
description: Canonical format reference for exports.md and imports.md. Defines YAML schemas, naming rules, guardrails, and operational guide for cross-repo context sharing. Read this before writing either file in any repo.
---

## Metadata

- **Name:** cross-repo
- **Phase:** Reference — consulted before writing exports.md or imports.md; not an executable phase skill
- **Inputs:** None
- **Outputs:** N/A

---

## When to Use Cross-Repo Context

Use when:
- Service A will call Service B's API for the first time and no prior integration exists in Service A's codebase
- A shared library in Service B will be consumed by Service A
- Service A's engineers need Service B's API surface, DTOs, or constraints during implementation

Set up after ≥5 tickets complete on v2 artifacts (Phase 3 of the v2 migration).

---

## Two Files Required

| File | Location | Written by | Purpose |
|---|---|---|---|
| `exports.md` | `[knowledge-path]/exports.md` in the **exporting** repo | Service B engineers | Declares what Service B makes available |
| `imports.md` | `[knowledge-path]/imports.md` in the **importing** repo | Service A engineers | Declares what Service A wants to consume |

Both files are hand-authored. The system never auto-generates or auto-updates them during execution. Tooling may pre-populate `code_exports` (e.g., scanning for controller annotations), but the final selection of roots and patterns is always human-controlled.

---

## exports.md — Full Schema

```yaml
# [knowledge-path]/exports.md
# Written by: engineers of the exporting repo
# Updated when: new API surfaces added or topics become stale

exported_topics:                            # OPTIONAL — omit if no knowledge signals to share
  - topic_id: T1                            # REQUIRED  unique string  /^T[0-9]+$/
    title: "Short descriptive title"        # REQUIRED  non-empty
    modules: [module-name]                  # REQUIRED  min:1  exact names from THIS repo's codebase index
    weight: HIGH                            # REQUIRED  HIGH | MEDIUM | LOW
    type: empirical                         # REQUIRED  system | empirical | external | operational
    summary: "One-sentence key constraint"  # REQUIRED  non-empty
    last_updated: YYYY-MM-DD                # REQUIRED  ISO date — topics older than 90 days are not loaded

code_exports:                               # OPTIONAL — omit if no code to share
  - module: module-name                     # REQUIRED  exact name from THIS repo's codebase index
    type: api-surface                       # REQUIRED  "api-surface" | "shared-library"
    roots:                                  # REQUIRED  min:1
      - path: src/payments/controllers      # REQUIRED  relative to THIS repo root
        include: ["*.java"]                 # REQUIRED  min:1 glob pattern
        exclude: ["*Internal*.java"]        # OPTIONAL  default: []
```

**Type semantics:**
- `api-surface`: externally callable interfaces — controllers, REST endpoints, gRPC service definitions
- `shared-library`: reusable internal utilities explicitly safe for cross-repo use

**Root path guardrails — these paths are prohibited as roots:**
- `src/`
- `src/main/`
- `src/main/java/`
- Any directory resolving to >20 files after include/exclude filtering

Roots must point to a specific package or feature-level directory. If a root exceeds 20 files after filtering: that root is skipped with a warning in the context packet. Split into more specific roots.

---

## imports.md — Full Schema

```yaml
# [knowledge-path]/imports.md
# Written by: engineers of the importing repo
# Updated when: a new cross-repo dependency is introduced

import_sources:
  - repo: service-b                                   # REQUIRED  human-readable repo identifier
    exports_path: ../service-b/knowledge/exports.md   # REQUIRED  path to exports.md relative to THIS repo root
    scope: [payment-integration]                      # REQUIRED  min:1  module names in THIS repo's codebase index
    include_code:                                     # OPTIONAL  omit = load knowledge signals only, no code
      - api-surface                                   # values: "api-surface" | "shared-library"
```

---

## The Naming Alignment Rule

**This is the most common failure mode.**

`exports.md:modules[]` in the exporting repo must **exactly match** `imports.md:scope[]` in the importing repo. Case-sensitive string equality. No fuzzy matching. A single character difference produces no signal and no error.

```yaml
# BROKEN — one character difference, produces no match, no error
# service-b/exports.md
modules: [payment-api]      # "payment-api"

# service-a/imports.md
scope: [payments-api]       # "payments-api" — no match
```

Convention: use lowercase hyphenated names matching your codebase index format (`payment-api`, `auth-service`) consistently across all repos.

---

## What Fires at Each Phase

| Phase | What activates | What is loaded |
|---|---|---|
| Brainstorming | Silent scan when problem scope matches `imports.md:scope` | HIGH/MEDIUM `exported_topics` only — as framing context before opening question |
| Planning | Auto-injection when StepNode files resolve to a scoped module | `risk_signals: ["API Conventions"]` appended to matching StepNodes |
| Context Packet | Full cross-repo resolution | `exported_topics` signals + `code_exports` files (when `include_code:` declared) |

Code files from `code_exports` are only loaded at context packet time. They do not appear during brainstorming or planning.

---

## File Cap Summary

| Cap | Value | Behavior when exceeded |
|---|---|---|
| Per-root file cap | 20 files | Root skipped; warning in context packet |
| Global per-import-source per-phase cap | 50 files | First 50 lexicographically; warning logged |
| Per-file line cap | 500 lines | File truncated; `... (truncated)` appended |
