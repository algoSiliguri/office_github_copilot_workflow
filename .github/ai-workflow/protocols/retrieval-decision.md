> **Layer 3 — Protocol.** Invoked by: `/write-plan` (planning skill). Governs when the AI reads prior artifacts or fetches retrieval context during planning. Key behavioral rules are also reflected in `copilot-instructions.md` as always-on behavior.


# Retrieval Decision

Use this protocol during `/write-plan`.

Required fields:
- whether retrieval was required
- decision: `used | skipped | unavailable`
- short justification
- note any degraded or blocked reason caused by missing or conflicting context

Do not treat index presence alone as a retrieval trigger.