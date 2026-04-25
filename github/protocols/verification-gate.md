# Protocol: Verification Gate

**Purpose:** Ensure no success claim is made without a fresh command execution and pasted terminal output as evidence.

**Inputs:** The claim being made (e.g., "tests pass"). The exact command that proves it.

**Outputs:** A verified assertion with pasted terminal output, or a blocked claim if evidence is absent.

**Non-goals:** Does not determine which command to run (orchestrator responsibility). Does not retry on failure. Does not interpret what the output means.

---

Before claiming any of these: "step complete", "phase complete", "all tests pass", "full suite green" — run this gate:

1. **IDENTIFY:** What exact command proves the claim?
2. **RUN:** Execute it now — fresh execution, not cached output.
3. **READ:** Read the full output including exit code.
4. **CLAIM:** State the claim with the pasted evidence.

Reject these: "should pass", "probably works", "tests passed" (without output). Evidence is pasted terminal output — nothing else counts.
