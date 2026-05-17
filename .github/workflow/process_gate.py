#!/usr/bin/env python3
"""Data-driven validator runner. Reads enterprise_pipeline from orchestration.json,
interpolates {active_task} and {tasks_root} from state.json, and invokes each
validator as a subprocess. Zero business logic or validator knowledge.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
ORCHESTRATION = ROOT / ".github/workflow/orchestration.json"
STATE = ROOT / ".github/workflow/state.json"


def load_json(path, label):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        print(f"process_gate: error: missing required file: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"process_gate: error: invalid JSON in {path}: {exc}", file=sys.stderr)
        sys.exit(1)


def run_pipeline_phase(phase_name):
    state = load_json(STATE, "state.json")
    config = load_json(ORCHESTRATION, "orchestration.json")

    active_task = state.get("active_task")
    context = {
        "active_task": active_task,
        "tasks_root": ".github/tasks",
    }

    pipeline_steps = config.get("enterprise_pipeline", {}).get(phase_name, [])
    if not pipeline_steps:
        print(f"process_gate: no steps registered for phase '{phase_name}'", file=sys.stderr)
        sys.exit(1)

    # Guard: fail fast if any step needs active_task but it is null.
    needs_task = any(
        "{active_task}" in arg
        for step in pipeline_steps
        for arg in step.get("args", [])
    )
    if needs_task and active_task is None:
        print(
            f"process_gate: governance failure: no active_task in state.json "
            f"for phase '{phase_name}'. Complete the prerequisite phase first.",
            file=sys.stderr,
        )
        sys.exit(1)

    for step in pipeline_steps:
        script = step["script"]
        raw_args = step.get("args", [])
        try:
            interpolated = [arg.format(**context) for arg in raw_args]
        except KeyError as exc:
            print(
                f"process_gate: error: unknown interpolation token {exc} in step {script}",
                file=sys.stderr,
            )
            sys.exit(1)

        command = [sys.executable, script] + interpolated
        result = subprocess.run(command)
        if result.returncode != 0:
            print(
                f"process_gate: governance failure: {script} exited {result.returncode}",
                file=sys.stderr,
            )
            sys.exit(result.returncode)

    print(f"process_gate: phase '{phase_name}' passed")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python process_gate.py <phase_name>", file=sys.stderr)
        sys.exit(1)
    run_pipeline_phase(sys.argv[1])
