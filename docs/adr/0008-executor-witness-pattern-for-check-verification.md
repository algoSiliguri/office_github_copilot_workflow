# Executor-Witness Pattern for check-verification

`check-verification` spawns the locked verification commands from the PlanRecord via `subprocess.run(cmd, shell=False)` and reads `result.returncode` directly from the OS. It does not parse log files, read a model-written exit code field, or delegate execution to a separate shell step whose output is written to disk first.

**Considered Options**

- Parse a `test_run.log` written by a prior shell step — rejected because the log file is writable by any process, including the AI, making it equivalent to trusting a model-written field.
- Trust a `command_exit_code` field in the VerificationDraft — rejected because the AI that wrote the draft also wrote the exit code; this lets the agent grade its own exam.
- Have `check-verification` spawn the command and capture `returncode` directly — chosen.

**Consequences**

- `check-verification` is no longer a pure reader; it has an execution side effect. This is a deliberate SRP trade-off: the script's single responsibility is **attestation**, and witnessing execution is the attestation mechanism.
- Validators must be invoked with a live working tree, not in a read-only fixture environment, when running as the Executor-Witness.
- Text output (stdout/stderr) streams to the developer's terminal and a log file but is ignored by the script's logic. The integer returncode is the only signal.
- `shell=False` with array-form commands (not string commands) is required to prevent injection via AI-controlled command strings.
- The VerificationDraft is deleted after a successful receipt write; the VerificationReceipt is the only artifact that survives the phase.
