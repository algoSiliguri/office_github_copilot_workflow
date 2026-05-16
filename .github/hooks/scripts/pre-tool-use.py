#!/usr/bin/env python3
"""preToolUse risk guard for GitHub Copilot CLI Enhanced Local Mode.

Reads official Copilot hook stdin: {timestamp, cwd, toolName, toolArgs}.
Outputs official Copilot preToolUse JSON guard decisions.
Validators and human gates remain authoritative regardless.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "workflow" / "lib"))

from hooklib import event_record, normalize_payload, read_active_task, read_payload, risk_level, write_event
from path_policy import PathPolicy

_orchestration_path = Path(__file__).resolve().parent.parent.parent / "workflow" / "orchestration.json"
with _orchestration_path.open(encoding="utf-8") as _f:
    _orchestration = json.load(_f)
_path_policy = PathPolicy(_orchestration)

RISK_PATTERNS = {
    "destructive_shell": ["rm -rf", "git reset --hard", "git clean -fd", "mkfs", "chmod -R 777"],
    "network_commands": ["curl ", "wget ", "ssh ", "scp ", "rsync ", "gh api", "git clone"],
    "dependency_installation": ["pip install", "npm install", "yarn add", "pnpm add", "brew install", "uv tool install"],
    "graph_regeneration": ["graphify update", "graphify .", "graphify --"],
    "git_push": ["git push"],
    "secret_or_credential_access": [".env", "id_rsa", "secrets", "credential", "token"],
}
WRITE_TOOLS = {
    "create",
    "edit",
    "write_file",
    "edit_file",
    "create_file",
    "delete_file",
    "str_replace_editor",
}


def build_haystack(normalized):
    tool_args = normalized["tool_args"]
    parts = [
        normalized.get("tool_name", ""),
        tool_args.get("command", ""),
        tool_args.get("cmd", ""),
        tool_args.get("file_path", ""),
        " ".join(tool_args.get("file_paths", []) if isinstance(tool_args.get("file_paths"), list) else []),
    ]
    return " ".join(str(p) for p in parts if p).lower()


payload = read_payload(sys.stdin)
normalized = normalize_payload(payload, "preToolUse")
tool_name = normalized["tool_name"]
haystack = build_haystack(normalized)
file_paths = normalized["target_files"]
task_id = read_active_task(normalized["cwd"])

categories = []
for category, patterns in RISK_PATTERNS.items():
    if any(p in haystack for p in patterns):
        categories.append(category)

if tool_name in WRITE_TOOLS:
    for path in file_paths:
        if _path_policy.is_governance(path):
            categories.append("workflow_governance_edits")
            break
    for path in file_paths:
        if _path_policy.is_memory(path):
            categories.append("memory_writes")
            break

if normalized["command"] and not task_id and normalized["phase"] in {"execute", "verify", "review"}:
    categories.append("phase_sensitive_without_task")

categories = sorted(set(categories))
risky = bool(categories)
decision = "deny" if risky else "allow"
reason = "human approval required for risky tool use" if risky else "no risky category detected"
risk = risk_level(categories)

event_type = "tool.requested"
if normalized["command"]:
    event_type = "command.execution_attempt"
if file_paths and tool_name in WRITE_TOOLS:
    event_type = "file.edit_attempt"
if "workflow_governance_edits" in categories:
    event_type = "governance_file.edit_attempt"
if "check-verification" in normalized["command"]:
    event_type = "verification.command_execution"

event = event_record(
    normalized,
    task_id=task_id,
    event_type=event_type,
    decision=decision,
    reason=reason,
    risk=risk,
    target_files=file_paths,
)
event["metadata"] = {
    "risk_categories": categories,
    "hook_event": normalized["hook_event"],
}

written_path = None
log_ok = True
log_error = None
try:
    written_path = write_event(normalized["cwd"], event)
except Exception as exc:
    log_ok = False
    log_error = str(exc)[:240]
    if not risky and normalized["phase"] in {"execute", "verify", "review"}:
        decision = "ask"
        reason = "traceability log failed for phase-sensitive tool use"

output = {
    "permissionDecision": decision,
    "riskCategories": categories,
    "tool": tool_name,
    "redacted": True,
    "traceEventId": event["event_id"],
    "traceWrittenPath": written_path,
    "traceLogOk": log_ok,
}
if decision != "allow":
    output["permissionDecisionReason"] = reason
if log_error:
    output["traceLogError"] = log_error

print(json.dumps(output, sort_keys=True))
