# /setup-workflow

Detect the tech stack of this repo and write `.github/workflow/config.yaml`.

## Detection order

Scan the repo root for the following files and infer tech stack:

| File | Language | Framework |
|---|---|---|
| `build.gradle` / `build.gradle.kts` | Java/Kotlin | Gradle |
| `pom.xml` | Java | Maven |
| `package.json` | JavaScript/TypeScript | Node (check `scripts` for framework hints) |
| `pyproject.toml` / `setup.py` / `requirements.txt` | Python | (check imports/deps for Django/FastAPI/Flask) |
| `Cargo.toml` | Rust | Cargo |
| `Makefile` | (check contents) | (infer from targets) |
| `go.mod` | Go | Go modules |
| none of the above, docs-only repo | Markdown or mixed docs | none |

## Required output

Write `.github/workflow/config.yaml` with all fields populated — no empty strings allowed.

```yaml
project:
  name: <repo directory name>
  description: <one-line description from README or package.json, or infer from repo structure>
  primary_language: <detected language>
  framework: <detected framework, or "none">

commands:
  build: <exact command, e.g. "gradle build" or "npm run build">
  test: <exact command to run tests>
  verify: <command to verify correctness, e.g. "./gradlew test" or "pytest">
  lint: <lint command, or "none" if not present>

workflow:
  cli_handoff_allowed: true
  task_path: .github/tasks
  instruction_version: v1
```

## Rules

- Do not ask the user for values — detect everything from repo files
- If a command cannot be detected with confidence, write the most likely default for the stack
- For repos without a build system, use `none` for missing build, test, or lint commands
- Do not modify any file other than `.github/workflow/config.yaml`
- After writing, output a STATUS block:

```
STATUS: setup-workflow complete
DETECTED: <language> / <framework>
COMMANDS: build=<cmd> | test=<cmd> | verify=<cmd> | lint=<cmd>
NEXT: /grill or /quick-task
```
