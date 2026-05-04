# Phase Checkpoint

Use this protocol when executing a phased or degraded plan.

Required checkpoint record:
- active step id
- files touched so far
- verification evidence collected so far
- unresolved risks
- decision to continue or stop

If scope expands or a blocked risk appears, stop and return to `/write-plan`.
