# Repo-Local Copilot CLI-First V1

This project will build v1 as a repo-local GitHub Copilot CLI orchestration bundle, not as an IDE/plugin-first system. The foundation must run from normal repository files, especially `AGENTS.md` and `.github/`, without plugin installation, MCP, LSP, admin privileges, or third-party validator dependencies, because managed office laptops may block external installation and policy-controlled plugin loading.

**Considered Options**

- Keep the current JetBrains/plugin-primary workflow bundle.
- Make GitHub Copilot CLI plugin packaging the v1 foundation.
- Build a portable repo-local Copilot CLI orchestration layer first, with plugin packaging deferred.

**Consequences**

V1 optimizes for Safe Default Mode: `/setup -> /plan -> /execute -> /verify` must work with repo instructions, five compact skills, one thin workflow orchestrator agent, JSON artifacts, standard-library validators, graph metadata, and human approval gates. Plugin, MCP, LSP, and enterprise-managed distribution remain optional later modes rather than assumptions in the core architecture.
