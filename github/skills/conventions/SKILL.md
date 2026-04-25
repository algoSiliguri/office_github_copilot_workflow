---
name: conventions
description: Repo-specific conventions for this project — tech stack, test commands, artifact paths, ticket format, and commit style. Always read this skill when starting any phase to ground responses in this repo's actual context.
---

## Metadata

- **Name:** conventions
- **Description:** Shared reference document containing all repo-specific values used by every skill and agent.
- **Phase:** Shared reference — read at the start of every phase
- **Inputs:** N/A — populated once by `/setup`, updated by the team as conventions change
- **Outputs:** Context (ticket format, paths, commands, active work) that grounds all other skills

## When To Use

Read this file at the start of every phase before executing any skill. It is the single source of repo-specific values. Every skill that references "the test command", "the specs path", or "the ticket format" is referring to this file.

## Inputs

None. This file is a template populated by `/setup` and maintained by the team.

---

# Repo Conventions

## Ticket & Branch

### Ticket Sources

| Source | Format | Example |
|--------|--------|---------|
| Jira | <e.g. PROJ-1234> | PROJ-567 |
| GitHub Issues | <e.g. #123 or GH-123> | GH-123 |
| Other | <format if applicable> | — |

Active ticket format: <e.g. Jira: PROJ-1234>
Branch naming:        <e.g. TICKET-1234-short-description>

## Artifact Paths (relative to project root)

Specs:          <e.g. docs/workflow/specs/>
Plans:          <e.g. docs/workflow/plans/>
Verifications:  <e.g. docs/workflow/verifications/>
Brainstorms:    <e.g. docs/workflow/brainstorms/>
Handoffs:       <e.g. docs/workflow/handoffs/>
Codebase Index: <e.g. codebase/>
Knowledge Index: <e.g. knowledge/>
Context Packets: <e.g. context/>

## Codebase

Language:       <e.g. Java / Python / Go / TypeScript>
Framework:      <e.g. Spring Boot / FastAPI / Gin / Next.js>
Entry points:   <e.g. src/main/java/App.java / cmd/main.go / app/__init__.py>
Key modules:    <e.g. auth, billing, api — names of the main packages or modules>
Maturity threshold: <default | N — module count above which maturity becomes "mature"; default thresholds: <10=low, 10–30=medium, >30=mature>

## Testing

Test command:   <e.g. mvn test / pytest / go test ./... / npm test>
Test location:  <e.g. src/test/java/ / tests/ / __tests__/>
Test patterns:  <e.g. unit tests use mocks; integration tests use @SpringBootTest>

## Development

Build command:  <e.g. mvn package / pip install / go build / npm run build>
Lint command:   <e.g. checkstyle / flake8 / golint / eslint>
Local dev:      <e.g. mvn spring-boot:run / flask run / go run ./cmd/ / npm run dev>

## Commit Message Format

<e.g. TICKET-1234: short description in imperative mood>

## PR Convention

Title:  <e.g. TICKET-1234: short description>
Body:   <e.g. include link to ticket, summary of what changed and why>

## Notes

<Any other repo-specific conventions: file naming, package structure, coding standards, deployment notes>

Incidental file patterns: <comma-separated glob patterns for files that change alongside any step but are never plan targets — e.g. *.lock, package-lock.json, .DS_Store. Leave blank initially; add patterns after Stage 1 false positives appear. Used by the v2 execution skill Rule 2 incidental grace category.>

## Active Context

<Written by /brainstorm — describes the current feature or problem being worked on. Leave blank between features.>

---

## Output Format

A populated reference document with no placeholder text. All fields contain real values specific to this repo.

## Dependencies

None — this is the root reference all other skills depend on.

## Handoff

N/A — conventions is a shared reference, not a workflow phase. After `/setup` populates this file, proceed to `/brainstorm`.
