# Workflow File Instructions

Apply these instructions when editing this orchestration bundle.

- Keep required files JSON or JSONL.
- Keep required validators Python standard-library-only.
- Do not add user-facing commands beyond `/setup`, `/plan`, `/execute`, and `/verify`.
- Keep `/evaluate` maintainer-only.
- Keep skills compact and permission-light.
- Do not add a separate debugging skill; diagnosis belongs in `task-planning`.
- Do not make hooks required for Safe Default Mode.
- Do not add self-modifying workflow behavior.
- Do not overwrite target repository team instructions; `/setup` may only update a bounded managed `AGENTS.md` block.
