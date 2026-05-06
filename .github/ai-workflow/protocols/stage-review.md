> **Layer 3 — Protocol.** Invoked by: `/review` (review skill). Governs stage-level review decision logic.


# Stage Review

Use this protocol during `/review`.

Required checks:
- actual changed files are within declared plan scope
- verification evidence exists and matches the work performed
- degraded work does not receive normal `PASS`
- blocked work does not receive acceptance

If any required check fails, do not smooth it over in prose. Record `FAIL` or `BLOCKED`.