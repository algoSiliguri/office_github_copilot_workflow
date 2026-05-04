# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- `CONTEXT.md` at the repo root, or
- `CONTEXT-MAP.md` at the repo root if it exists; it points at one `CONTEXT.md` per context. Read each one relevant to the topic.
- `docs/adr/` and, in multi-context repos, any context-specific ADR directories

If any of these files do not exist, proceed silently. Do not flag their absence and do not suggest creating them upfront.

## File structure

Single-context repo:

```text
/
|- CONTEXT.md
|- docs/adr/
`- src/
```

Multi-context repo:

```text
/
|- CONTEXT-MAP.md
|- docs/adr/
`- src/
   |- area-a/CONTEXT.md
   `- area-b/CONTEXT.md
```

This repo is currently configured as single-context.

## Use the glossary's vocabulary

When your output names a domain concept, use the term as defined in `CONTEXT.md`. Avoid drifting to synonyms the glossary explicitly avoids.

## Flag ADR conflicts

If your output contradicts an existing ADR, surface that explicitly rather than silently overriding it.
