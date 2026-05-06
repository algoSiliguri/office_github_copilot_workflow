> **Layer 3 — Protocol.** Invoked by: `/verify` (verification skill), `/quick-task`. Governs pass/fail gate logic for verification evidence.


# Verification Gate

Verification evidence is required before a quick-task may pass.

Allowed evidence:
- automated test output
- typecheck/build/lint output
- manual inspection note
- local run output
- before/after behavior note

If no credible evidence exists, the quick-task result must be FAIL.