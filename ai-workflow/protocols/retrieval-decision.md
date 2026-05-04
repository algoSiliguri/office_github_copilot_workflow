# Retrieval Decision

Use this protocol during `/write-plan`.

Required fields:
- whether retrieval was required
- decision: `used | skipped | unavailable`
- short justification
- note any degraded or blocked reason caused by missing or conflicting context

Do not treat index presence alone as a retrieval trigger.
