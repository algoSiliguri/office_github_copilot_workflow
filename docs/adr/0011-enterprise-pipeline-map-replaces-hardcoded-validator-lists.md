# Enterprise Pipeline Map Replaces Hardcoded Validator Lists

`orchestration.json.enterprise_pipeline` is the single authority over which validators run per phase and with what arguments. A thin stdlib runner (`process_gate.py`) reads this map, interpolates `{active_task}` and `{tasks_root}` tokens from `state.json`, and invokes validators as subprocesses. No validator path, argument pattern, or phase sequence is hardcoded in runner code.

**Considered Options**

- Dynamic plugin discovery (scan a directory at runtime, auto-register any script found) — rejected. Silent failures from unexpected files, unpredictable ordering, and enterprise environment variance make this fragile at scale.
- Hardcoded invocation in `release-check.sh` or equivalent shell script — rejected. Adding a new validator requires modifying the runner, violating OCP. Shell scripts are harder to test and harder to extend safely across OS variants.
- Declarative config-driven map with a generic runner — chosen.

**Enterprise Pipeline Map shape in `orchestration.json`:**

```json
{
  "enterprise_pipeline": {
    "on_setup":        [{ "script": "...", "args": [] }],
    "on_grill":        [{ "script": "...", "args": ["{tasks_root}/{active_task}/grill.json"] }],
    "on_planning":     [{ "script": "...", "args": ["{tasks_root}/{active_task}/plan.json"] }],
    "on_execution":    [{ "script": "...", "args": ["{tasks_root}/{active_task}/execution.json"] }],
    "on_verification": [{ "script": "...", "args": ["{tasks_root}/{active_task}/verification_draft.json", "{tasks_root}/{active_task}/review.json"] }]
  }
}
```

**Consequences**

- `process_gate.py` contains zero validator knowledge. Its entire logic is: load config, load state, guard null `active_task`, interpolate args, iterate steps, fail fast on non-zero returncode.
- Adding a validator requires: (1) drop the script into `.github/workflow/validators/`, (2) add it to the appropriate `enterprise_pipeline` phase array in `orchestration.json`. No runner code changes.
- `check-setup` must validate that every script path declared in `enterprise_pipeline` exists on disk (presence check moves from `REQUIRED_PATHS` hardcode to config-driven iteration).
- `{active_task}` interpolation uses `str.format(**context)`. If `active_task` is null and any arg template contains `{active_task}`, `process_gate.py` exits 1 before spawning any subprocess.
- Commands stored in `verification_commands` and passed to subprocess are array-form (not strings) to prevent shell injection with `shell=False`.
