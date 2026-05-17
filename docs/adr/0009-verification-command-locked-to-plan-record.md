# Verification Command Locked to PlanRecord

The commands `check-verification` executes come exclusively from the human-approved `plan.json.verification_commands` array. The VerificationDraft (`verification_draft.json`) carries no command field. The AI cannot declare, modify, or override the verification command at verify time.

**Considered Options**

- Read the verification command from `verification_draft.json` — rejected. The AI writes the draft; an AI under context pressure or a malicious prompt injection can write `"verification_command": "true"` or `"echo ok"`, achieving an exit-0 receipt without running real tests.
- Read the verification command from a separate `test_run.json` written by the developer — rejected. That file is writable by the AI or any process; same forgery surface as the draft.
- Read from `plan.json`, which was human-approved at plan time — chosen.

**Consequences**

- `plan.json.verification_command` (string) must be replaced by `plan.json.verification_commands` (array of string arrays, e.g. `[["pytest", "tests/auth/"]]`). Each inner array is passed directly to `subprocess.run` with `shell=False`.
- `check-plan` must validate `verification_commands` is a non-empty array of non-empty arrays.
- If the verification strategy must change after planning, the developer must loop back through `/plan`, update the command, and re-obtain human approval. There is no in-place verification command amendment.
- `grill.json.mandatory_verification_steps` is the upstream anchor: `plan.verification_commands ⊆ grill.mandatory_verification_steps`. The grill session constrains which commands are eligible; the plan commits to a subset.
