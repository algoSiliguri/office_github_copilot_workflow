# Spec: Workflow Cycle UX Revision

## Problem Statement

The GitHub Copilot workflow system has several bugs and UX gaps that degrade the cycle experience: `/setup` fails because the Design Agent lacks write tools, skill names are invisible in chat output, agents carry dead-weight Skill Usage Mapping sections, agent tools use wrong YAML syntax, there's no context hygiene discipline between phases, model recommendations are inconsistent across handoffs, and the ticket format is over-constrained for repos with mixed ticket sources.

## Solution Approach

Surgical edits across agents, prompts, skills, and shared files to fix bugs and add lightweight UX patterns. No changes to skill logic, execution modes, plan/spec structure, or review/verification content. Each touched file gets a consistency check against the new rules.

## Requirements

- [ ] `/setup` executes successfully via Implementation Agent (which has write tools)
- [ ] Design Agent no longer owns Setup phase; Implementation Agent does
- [ ] All 3 agent files use `tools: ['tool_name']` inline array syntax in frontmatter
- [ ] Skill Usage Mapping section removed from all 3 agent files
- [ ] Every prompt body includes a phase announcement instruction: `> **Phase: [Name]** | Skill: [name]`
- [ ] `copilot-instructions.md` contains a Context Hygiene (MANDATORY) section defining the 3-step post-phase pattern
- [ ] Every skill's Handoff section ends with "Apply context hygiene summary, then proceed."
- [ ] Skills with new-chat handoffs include a model recommendation: "Start a new chat. Recommended: [Model]. Use /[command]."
- [ ] Model hints in skills match the Model Routing table in WORKFLOW.md
- [ ] `conventions/SKILL.md` template supports multiple ticket sources (Jira, GitHub Issues, Other) plus an Active ticket format field
- [ ] `setup/SKILL.md` detects and populates multiple ticket formats during auto-detection
- [ ] WORKFLOW.md Quick Reference table shows `@Implementation Agent` for Setup
- [ ] WORKFLOW.md folder structure comment reflects Design Agent owns Phases 2-4 (not 1-4)
- [ ] WORKFLOW.md Model Routing section no longer references Skill Usage Mapping in agents
- [ ] WORKFLOW.md Session Hygiene cross-references Context Hygiene rule in copilot-instructions.md
- [ ] No skill logic, execution mode, plan structure, spec structure, or review/verification content is changed

## Architecture / Design Decisions

**Files changed (25 total):**

| Category | Files | What changes |
|----------|-------|-------------|
| Agents (3) | `design.agent.md`, `implementation.agent.md`, `review.agent.md` | Tools syntax fix, remove Skill Usage Mapping, reassign Setup ownership |
| Prompts (10) | All prompt files | Add phase announcement instruction |
| Skills (10) | All skill files | Add context hygiene one-liner to Handoff; model hints where applicable |
| Shared (2) | `copilot-instructions.md`, `WORKFLOW.md` | Context Hygiene rule, consistency updates |

**Key decisions:**
- `/setup` moves to Implementation Agent (preserves Design Agent's read-only purity)
- Model routing stays in WORKFLOW.md as single source of truth; skills get hints only
- Context hygiene pattern defined once in copilot-instructions.md; skills reference with one line
- Ticket format becomes multi-source with one "active" field for automation
- Phase visibility is a response-content problem, solved in prompt bodies not frontmatter

## Risks & Dependencies

- **Copilot agent frontmatter behavior:** The `tools:` inline array syntax is based on user's confirmed working format. If Copilot changes its parsing, tools may break.
- **Context hygiene compliance:** Copilot may not reliably follow the context hygiene instruction from copilot-instructions.md if the conversation is long. The one-liner in each skill's Handoff acts as a reinforcement signal.
- **Phase announcement drift:** Copilot may stop announcing the phase after the first response in a session. This is mitigated by the prompt instruction but can't be fully guaranteed.
- **No existing tests:** This is a Markdown-only workflow system with no automated tests. Verification is manual: run each `/command` and confirm the output matches expectations.

## Testing Strategy

- **Manual: `/setup`** — run in a test repo, confirm `conventions/SKILL.md` is written with multi-source ticket format populated
- **Manual: Phase announcement** — run `/brainstorm`, `/write-spec`, `/write-plan`, `/execute-plan`, `/verify`, `/review` and confirm first response line shows `> **Phase: X** | Skill: Y`
- **Manual: Context hygiene** — complete a brainstorm session, confirm the agent produces a <=5 bullet summary + artifact list + continuation prompt before handoff
- **Manual: Model hints** — confirm each skill's handoff message includes the correct model recommendation matching WORKFLOW.md
- **Manual: Agent tools** — confirm agent files parse correctly in Copilot (agents appear in @ menu, tools are available)
- **Diff review:** For every changed file, verify no unintended content was altered outside the scoped changes
