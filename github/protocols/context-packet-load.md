# Protocol: Context Packet Load

**Purpose:** Load a pre-assembled context packet for a given ticket+phase, and declare the coverage-based access restrictions the caller must enforce.

**Inputs:** Ticket ID, phase number, context packets path (from conventions).

**Outputs:**
- Packet content (full file text, or a null signal if not found)
- Coverage confidence level: `high`, `medium`, or `low`
- Enforcement rules per level (declared in this protocol; applied by the caller)

**Non-goals:** Does not assemble the packet (context-packet skill responsibility). Does not perform code search (codebase-search protocol responsibility). Does not interpret the packet content — callers decide how to use it.

**Subagent note:** In phased-subagent mode (Step 2c), the caller embeds the packet content in the subagent prompt rather than applying enforcement in the parent session. The protocol's output (content + confidence + rules) is the same; usage differs by mode. The enforcement rules declared by this protocol apply inside the subagent.

---

1. Read `Context Packets:` path from `.github/skills/conventions/SKILL.md`.
2. Check for `[context-packets-path]/[ticket-id]/phase-[N]-context.md`. For inline plans (Step 2a), try `phase-1` first, then `phase-2` if not found.
3. If found: read the full context packet. Note the `Coverage confidence` field. Enforcement rules per level:
   - `high`: **Prohibited** from reading files outside the context packet. If a step requires a file read outside the packet, stop and say: "Step [N] requires reading [file], which is outside the context packet. Coverage is HIGH. Should I expand context or rephrase the step to work within the packet?"
   - `medium`: Controlled one-hop expansion allowed — may read files referenced by packet modules; do not scan broadly.
   - `low`: Expansion required. The Codebase Search Protocol is available without restriction.
   Use `## Relevant Decisions` and `## Module Context` to frame understanding before touching any code.
4. If not found: treat as `low` coverage. Note: "No context packet found — proceeding with full codebase search." The Codebase Search Protocol is available without restriction.
