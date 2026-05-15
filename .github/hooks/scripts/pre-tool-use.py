#!/usr/bin/env python3
"""preToolUse risk guard for GitHub Copilot CLI Enhanced Local Mode.

Reads official Copilot hook stdin: {timestamp, cwd, toolName, toolArgs}.
Outputs JSON guard decision. Exits non-zero for risky tools to signal block.
Note: whether non-zero exit blocks execution depends on Copilot hook protocol.
Validators and human gates remain authoritative regardless.
"""
import json
import sys

RISK_PATTERNS = {
    "destructive_shell": ["rm -rf", "git reset --hard", "git clean -fd", "mkfs", "chmod -R 777"],
    "network_commands": ["curl ", "wget ", "ssh ", "scp ", "rsync ", "gh api", "git clone"],
    "dependency_installation": ["pip install", "npm install", "yarn add", "pnpm add", "brew install", "uv tool install"],
    "graph_regeneration": ["graphify update", "graphify .", "graphify --"],
    "git_push": ["git push"],
    "secret_or_credential_access": [".env", "id_rsa", "secrets", "credential", "token"],
}
GOVERNANCE_PREFIXES = (
    ".github/copilot-instructions.md",
    ".github/instructions/",
    ".github/skills/",
    ".github/agents/",
    ".github/hooks/",
    ".github/workflow/",
    "AGENTS.md",
)
WRITE_TOOLS = {"write_file", "edit_file", "create_file", "delete_file", "str_replace_editor"}


def read_payload():
    if sys.stdin.isatty():
        return {}
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def parse_tool_args(raw):
    if not raw:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return {"raw": str(raw)}


def build_haystack(payload, tool_args):
    parts = [
        payload.get("toolName", ""),
        tool_args.get("command", ""),
        tool_args.get("cmd", ""),
        tool_args.get("file_path", ""),
        " ".join(tool_args.get("file_paths", []) if isinstance(tool_args.get("file_paths"), list) else []),
    ]
    return " ".join(str(p) for p in parts if p).lower()


def extract_file_paths(tool_args):
    paths = []
    for key in ("file_path", "path"):
        val = tool_args.get(key)
        if val:
            paths.append(str(val))
    for val in (tool_args.get("file_paths") or []):
        if val:
            paths.append(str(val))
    return paths


payload = read_payload()
tool_args = parse_tool_args(payload.get("toolArgs"))
tool_name = payload.get("toolName", "")
haystack = build_haystack(payload, tool_args)
file_paths = extract_file_paths(tool_args)

categories = []
for category, patterns in RISK_PATTERNS.items():
    if any(p in haystack for p in patterns):
        categories.append(category)

if tool_name in WRITE_TOOLS:
    for path in file_paths:
        if any(path.startswith(prefix) for prefix in GOVERNANCE_PREFIXES):
            categories.append("workflow_governance_edits")
            break

categories = sorted(set(categories))
risky = bool(categories)
decision = "deny" if risky else "allow"
reason = "human approval required for risky tool use" if risky else "no risky category detected"

print(json.dumps({
    "decision": decision,
    "risk_categories": categories,
    "reason": reason,
    "tool": tool_name,
    "redacted": True,
}, sort_keys=True))

if risky:
    sys.exit(1)
