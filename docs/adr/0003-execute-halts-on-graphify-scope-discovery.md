# Execute Halts and Returns to Plan When Graphify Reveals Missing Scope

When `/execute` follows approved `graph_refs[]` and discovers that the plan's `intended_files` is structurally incomplete — files the plan should have included but did not — execution halts with `status: blocked` and requires a plan amendment via `/plan` before continuing. Scope-drift approval is not used for this case.

**Considered Options**

- Request scope-drift approval inline and continue execution with the additional files.
- Halt execution, surface the scope gap, require the user to amend the plan via `/plan`, re-approve, and re-run `/execute`.

**Consequences**

Scope-drift approval exists for opportunistic small additions discovered during execution — files adjacent to planned work that are safe to include. It is not an escape valve for plans whose scope was wrong at the root. A plan with a structural scope error needs a corrected `intended_files` list, a revised risk assessment, and fresh human approval. Using scope-drift approval for structural errors would bypass the plan approval gate and make the approved plan an unreliable record of intent. The cost is one extra `/plan` cycle; the benefit is that every approved plan remains an honest description of what was actually intended.
