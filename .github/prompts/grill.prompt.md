# /grill

Run a structured problem exploration session using the grill agent.

#file:.github/agents/grill.md

## Bugfix diagnosis gate

For bugfix tasks, inspect whether reproduction, suspected root cause, and test surface are already clear.

If any are unclear, stop and require `/diagnose` first.

If a DiagnosisRecord exists, the GrillRecord must set `source_diagnosis` to that path and ground success criteria in diagnosis evidence.
