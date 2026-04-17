---
name: setup
description: One-time repo initialisation. Auto-detects tech stack, test commands, and artifact paths, then writes a fully populated conventions/SKILL.md. Run once per repo before the first brainstorm session.
---

## Metadata

- **Name:** setup
- **Description:** One-time initialisation that auto-detects repo conventions and writes a fully populated `conventions/SKILL.md`.
- **Phase:** 1 — Setup
- **Inputs:** A repo with at least one build manifest (pom.xml, package.json, go.mod, etc.)
- **Outputs:** `.github/skills/conventions/SKILL.md` fully populated with no placeholder text

## When To Use

Run once per repo before the first `/brainstorm` session. Re-run if the tech stack, test commands, or artifact paths change significantly.

## Inputs

- A repo accessible via file tools — at minimum a build manifest must exist at the root
- No user input required; this skill detects everything automatically

---

You are setting up workflow conventions for this repo. You will read the codebase and write
a fully populated `.github/skills/conventions/SKILL.md` without asking the engineer to fill
anything in manually.

## Step 1: Detect Project Type

Run `list_dir` at the repo root. Note all files present, especially manifest files.

## Step 2: Read the Build Manifest

Read whichever manifest exists (check in this order):
- `pom.xml` — Java/Maven
- `build.gradle` or `build.gradle.kts` — Java/Kotlin/Gradle
- `package.json` — JavaScript/TypeScript/Node
- `go.mod` — Go
- `requirements.txt` or `pyproject.toml` — Python
- `Cargo.toml` — Rust

Extract: language, framework (if present), project name, declared dependencies.

## Step 3: Find Commands

Use `grep_search` to find test, build, and lint commands:
- **package.json:** search `"scripts"` block for `"test"`, `"build"`, `"lint"` keys
- **pom.xml:** standard Maven — `mvn test`, `mvn package`, `mvn checkstyle:check`
- **build.gradle:** search for test task customisation; default is `./gradlew test`
- **go.mod:** standard Go — `go test ./...`, `go build ./...`, `go vet ./...`
- **pyproject.toml / setup.cfg:** look for `[tool.pytest.ini_options]`; default is `pytest`
- **Cargo.toml:** standard Rust — `cargo test`, `cargo build`, `cargo clippy`

Also check for a `Makefile`: run `grep_search` for lines matching `^test:`, `^build:`, `^lint:`.
If found, use those as the commands.

Check `.github/workflows/` for CI config. Read the first `.yml` file found. Extract the
exact test and build commands used in CI — these are the authoritative commands.

Also detect:
- **Entry points**: look for `main` files at common paths: `src/main/java/` (Java), `cmd/` or `main.go` (Go), `app.py` or `app/__init__.py` (Python), `src/index.ts` or `src/main.ts` (TypeScript). Use the first match found, or write `# inferred — verify this` if none found.
- **Test location**: check for `src/test/`, `tests/`, `__tests__/`, `spec/`. Use the first that exists.
- **Test patterns**: read one test file from the test location. Note whether it uses mocks, integration setup (e.g. `@SpringBootTest`, `pytest fixtures`), or in-memory DBs. Summarise in one sentence.
- **Key modules**: list the top-level package or directory names under the main source root (e.g. `src/main/java/com/example/` sub-packages; `src/` top-level directories). List at most 5 names.
- **Local dev command**: check `package.json` scripts for `"start"` or `"dev"`; check for Spring Boot Maven plugin in `pom.xml`; check `Makefile` for a `run:` or `serve:` target. If none found, write `# inferred — verify this`.

## Step 4: Read Project Docs

Run `read_file` on `README.md`. Extract:
- Project description (1–2 sentences)
- Ticket sources — check for multiple formats:
  - Jira-style: `PROJ-1234`, `AIB-567` (uppercase letters + dash + digits)
  - GitHub Issues: `#123`, `GH-123`
  - Other: any other ticket ID patterns mentioned
- Any PR title or commit message conventions

If no README exists, skip this step.

## Step 5: Detect Artifact Paths

Check if any of these directories exist:
- `docs/specs/` or `docs/workflow/specs/` → use as specs path
- `docs/plans/` or `docs/workflow/plans/` → use as plans path
- `docs/verifications/` or `docs/workflow/verifications/` → use as verifications path
- `docs/brainstorms/` or `docs/workflow/brainstorms/` → use as brainstorms path
- `docs/handoffs/` or `docs/workflow/handoffs/` → use as handoffs path
- `codebase/` → use as codebase index path
- `knowledge/` → use as knowledge index path
- `context/` → use as context packets path

If none exist for the first five, default to:
- Specs: `docs/specs/`
- Plans: `docs/plans/`
- Verifications: `docs/verifications/`
- Brainstorms: `docs/brainstorms/`
- Handoffs: `docs/handoffs/`

For the last three (intelligence layer), always default to these if not found:
- Codebase Index: `codebase/`
- Knowledge Index: `knowledge/`
- Context Packets: `context/`

## Step 5b: Create module-map.md starter

Check if `[codebase-index-path]/module-map.md` exists (use the detected codebase index path from Step 5).

If it does NOT exist, create it with this exact content:

    # Module Map

    Manual boundary overrides for the codebase index. One row per module.
    Format: `[module-name] | [path(s), comma-separated] | [responsibility]`

    Rows here take precedence over auto-discovery by `/index codebase`.
    Add rows when auto-discovery produces wrong module boundaries.
    Run `/index codebase` after editing this file to regenerate the index.

    <!-- Examples:
    auth | src/auth/, src/session/ | Handles authentication, session tokens, and user identity
    billing | src/billing/service.py, src/billing/models.py | Processes payments and invoices
    -->

If it already exists, do not overwrite it.

## Step 6: Write conventions/SKILL.md

Write `.github/skills/conventions/SKILL.md` with every field populated from what you
detected. Do not leave any placeholder text such as `<e.g. ...>`.

Where you could not detect a value, write your best inference and append `# inferred — verify this`.

```markdown
---
name: conventions
description: Repo-specific conventions for this project — tech stack, test commands, artifact paths, ticket format, and commit style. Always read this skill when starting any phase to ground responses in this repo's actual context.
---

# Repo Conventions

## Ticket & Branch

### Ticket Sources

| Source | Format | Example |
|--------|--------|---------|
| Jira | [detected or "not detected"] | [example] |
| GitHub Issues | [detected or "not detected"] | [example] |
| Other | [detected or "not detected"] | [example] |

Active ticket format: [primary detected format — e.g. "Jira: PROJ-1234"]
Branch naming:        [detected or inferred value]

## Artifact Paths (relative to project root)

Specs:          [detected value]
Plans:          [detected value]
Verifications:  [detected value]
Brainstorms:    [detected value]
Handoffs:       [detected value]
Codebase Index: [detected value]
Knowledge Index: [detected value]
Context Packets: [detected value]

## Codebase

Language:       [detected value]
Framework:      [detected value or "none"]
Entry points:   [detected value or "# inferred — verify this"]
Key modules:    [detected value or "# inferred — verify this"]
Maturity threshold: default

## Testing

Test command:   [detected value]
Test location:  [detected value or "# inferred — verify this"]
Test patterns:  [detected value or "# inferred — verify this"]

## Development

Build command:  [detected value]
Lint command:   [detected value or "none"]
Local dev:      [detected value or "# inferred — verify this"]

## Commit Message Format

[detected or inferred value]

## PR Convention

Title:  [detected or inferred value]
Body:   [detected or inferred value]

## Notes

[Any additional conventions found in README or CI config. If none, write "None detected."]

## Active Context

<Written by /brainstorm — describes the current feature or problem being worked on. Leave blank between features.>
```

## Step 7: Report

Say:
> "Conventions written to `.github/skills/conventions/SKILL.md`. Review it and correct
> anything I got wrong — especially ticket format and commit style.
>
> When ready, use `/brainstorm` to start your first feature."

---

## Output Format

A fully populated `.github/skills/conventions/SKILL.md` with no `<e.g. ...>` placeholders.
Fields inferred (not detected) are annotated with `# inferred — verify this`.

## Dependencies

- `.github/skills/conventions/SKILL.md` — this skill writes to it

## Handoff

Next: `/brainstorm` in a new chat.
Note: review and correct conventions/SKILL.md first — especially ticket format and commit style.

Apply context hygiene before closing this chat.
