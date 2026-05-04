# Design Spec: Copilot Context Hygiene & Premium Usage Balance

**Date:** 2026-04-03
**Context:** Extends the GitHub Copilot IntelliJ workflow (2026-04-02) and phased execution workflow (2026-04-03) to solve premium quota compounding, cold-start context waste, and manual conventions setup. Applies to IntelliJ IDEA 2025.3.4 with GitHub Copilot plugin in agent mode.

---

## 1. Problem Statement

Three compounding problems observed in active Copilot usage:

| Problem | Evidence |
|---|---|
| Per-turn premium cost compounds | Each turn re-sends full conversation history; observed 0.3% → +0.5% → +0.7% per turn with Sonnet 4.6 |
| No phase-boundary session hygiene | Skills have phase-end handoffs but no instruction to start a new chat — engineers stay in the same session across phases, accumulating cost |
| Manual conventions setup | `conventions/SKILL.md` requires manual editing of 8+ fields per repo — creates friction and gets skipped |
| Cold-start file exploration in brainstorming | Brainstorming skill does silent `list_dir` + `semantic_search` reads before first question — costs premium turns on context the engineer already knows |

**Core constraint:** brainstorming and planning must remain on the strongest model. Design quality is the investment that makes execution cheap. Degrading design to save cost is the wrong trade.

---

## 2. Solution: Three Interlocking Levers

### Lever 1 — Phase-aware model routing

Premium model for phases requiring judgment. Standard model for mechanical phases.

| Phase | Model | Reason |
|---|---|---|
| Brainstorm | Premium | Ambiguity resolution, architectural judgment |
| Plan | Premium | Codebase reading + architectural decisions |
| Debug | Premium | Root cause reasoning |
| Review | Premium | Critical judgment, spec deviation detection |
| Spec-writing | Standard | Transcribing agreed design — template work |
| Execute | Standard | Mechanical — plan tells it exactly what to do |
| TDD | Standard | Pattern-following (red → green → refactor) |
| Verify | Standard | Checklist against known requirements |

Lives in `copilot-instructions.md` as a reference table. Engineers switch models at phase transitions.

---

### Lever 2 — Session hygiene: new chat per phase

Premium quota compounds within a chat session (each turn processes the full conversation history). Starting a new chat at every phase boundary resets the cost counter to zero.

All skill files gain an explicit "Start a new chat" instruction in their phase-end handoff. This is not optional — it is the cost-reset mechanism.

Phase-boundary model switch reminders are included in the handoff so the engineer knows to change model before opening the new chat.

---

### Lever 3 — Active Context in brainstorming (reduces premium turns within a session)

The brainstorming skill currently does silent file exploration before asking its first question. For a known repo, this burns premium turns on context the engineer could provide in one sentence.

Modified first action in `brainstorming/SKILL.md`:

1. Read `conventions/SKILL.md`
2. Check `## Active Context` block
   - **Present and non-empty:** use it, skip file exploration, proceed to first targeted question
   - **Absent or empty:** ask exactly: *"In 1–2 sentences, what are you working on?"* → write answer into the Active Context block → proceed with targeted questions

This compresses early turns: session starts with established context rather than from zero.

`conventions/SKILL.md` gains an `## Active Context` section at the bottom. The brainstorming skill is the only writer of this section.

---

## 3. Agentic Conventions Setup

Current problem: `conventions/SKILL.md` requires manual editing of ticket format, tech stack, commands, paths. This gets skipped or left with placeholders.

Solution: new `/setup` prompt + `skills/setup/SKILL.md`.

**Setup skill logic:**
1. `list_dir` at repo root to detect project type
2. `read_file` on whichever of `pom.xml` / `package.json` / `go.mod` / `build.gradle` / `requirements.txt` / `Cargo.toml` exists
3. `grep_search` for test/build/lint scripts; check `Makefile` and CI config if present
4. `read_file` on `README.md` for ticket format, PR conventions, project description
5. Write fully populated `skills/conventions/SKILL.md`
6. Report: "Conventions written. Review `skills/conventions/SKILL.md` and correct anything I got wrong. Then use `/brainstorm` to start your first feature."

One-time per repo. Engineer only corrects, never fills in from scratch.

---

## 4. Quick-Task Bypass

For bugfix / config-change / typo work: brainstorming is unnecessary. New `/quick-task` prompt routes directly to planning, skipping brainstorm and spec phases entirely.

Analogous to `skip_for: [bugfix, typo, config-change]` in Claude Code's `.superpowers-config.yml`.

---

## 5. Files Changed

### New files

| File | Purpose |
|---|---|
| `github/prompts/setup.prompt.md` | One-time repo init — triggers setup skill |
| `github/skills/setup/SKILL.md` | Auto-detects and writes `conventions/SKILL.md` |
| `github/prompts/quick-task.prompt.md` | Direct-to-plan bypass for simple work |

### Modified files

| File | Change |
|---|---|
| `github/copilot-instructions.md` | Model routing table + new-chat-per-phase hard rule |
| `github/skills/conventions/SKILL.md` | Add `## Active Context` block |
| `github/skills/brainstorming/SKILL.md` | Active Context check/write-back as first action |
| `github/skills/planning/SKILL.md` | Phase-end: "Start new chat. Switch to standard model. Use `/execute-plan`." |
| `github/skills/spec-writing/SKILL.md` | Phase-end: "Start new chat. Switch to premium model. Use `/write-plan`." |
| `github/skills/execution/SKILL.md` | Phase-end: "Start new chat. Use `/verify`." |
| `github/skills/debugging/SKILL.md` | Phase-end: "Start new chat. Use `/write-plan` for the fix." |
| `github/skills/verification/SKILL.md` | Phase-end: "Start new chat. Switch to premium model. Use `/review`." |
| `github/skills/review/SKILL.md` | Phase-end: "All phases complete. Raise your PR." |
| `github/skills/tdd/SKILL.md` | Phase-end: "Return to `/execute-plan` phase." |
| `github/WORKFLOW.md` | Setup section, Model Routing section, Session Hygiene section, cheat sheet, example |

---

## 6. What Is Not Changed

- The phased execution / sub-agent dispatch logic (execution/SKILL.md phase dispatch is unchanged — only the phase-end handoff message is added)
- The brainstorming convergence criteria — still architect-driven, still one-question-at-a-time
- Agent tool lists — no changes to what agents can access
- Any existing spec or plan documents

---

## 7. Success Criteria

- [ ] `/setup` on a new repo → `conventions/SKILL.md` fully populated without manual editing
- [ ] `/brainstorm` with empty Active Context → agent asks one sentence, writes it, proceeds with targeted questions
- [ ] `/brainstorm` with existing Active Context → agent skips the question, uses it immediately
- [ ] Every skill phase-end says "Start a new chat" → engineer is prompted to reset cost counter
- [ ] Model routing table in `copilot-instructions.md` → visible at every chat start
- [ ] `/quick-task` → reaches planning without a brainstorm session
- [ ] `WORKFLOW.md` setup section no longer says "fill in manually"
