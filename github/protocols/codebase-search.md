# Protocol: Codebase Search

**Purpose:** Locate a specific code element using semantic search with bounded fallback to grep, capped at 2 searches per query.

**Inputs:** A specific, formulated query (what to find — class name, method name, or constant).

**Outputs:** The location of the requested code element, or a "not found" report after exhausting the search budget.

**Non-goals:** Does not modify code. Does not perform broad module exploration. Does not set or read context packet coverage.

---

**Step 0: Knowledge state check (run before every module exploration):**
Identify the module name for the file or area you are about to explore. Then evaluate in order — first match wins:

1. Context packet is loaded AND this module appears explicitly by name in `## Module Context` → **no signal** — proceed directly to step 1. (Exact name match only — do not infer coverage.)
2. `[KNOWLEDGE_PATH]/[module].md` exists → emit, then proceed to step 1:
   ```
   Context reuse signal:
   This module has prior structured knowledge:
   - <1-line summary from the file's ## Summary section>
   ```
3. Neither condition above is met → emit, then proceed to step 1:
   ```
   Context reuse signal:
   No prior structured knowledge available for this module.
   This exploration is not reusable unless captured in the knowledge system.
   ```

Signal is informational only — never blocks execution. Emit one signal (or none) per module per exploration.

1. **Formulate a specific query**: name exactly what you're looking for. Bad: "find auth code". Good: "UserAuthService class" or "JWT token validation method".
2. **Run `semantic_search`** with the specific query.
3. **If a relevant result appears in the first page**: use it and stop.
4. **If zero results or all irrelevant**: try once more with a synonym or the exact class/method name as a literal string. Maximum 2 `semantic_search` calls per question.
5. **Fallback after 2 failed searches**: use `grep_search` with the exact class name, method name, or unique constant.
6. **Stop when found**: do not continue searching once you have what you need for the current step.
