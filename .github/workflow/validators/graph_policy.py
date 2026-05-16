def is_graph_light_quick_task(record: dict) -> bool:
    """Three-field quick-task predicate (no approval check).

    check-graph wraps this with an approval check for defense-in-depth when
    invoked standalone, since it may run without check-plan having run first.
    """
    quick = record.get("quick_task_classification") or {}
    return (
        quick.get("is_quick_task") is True
        and quick.get("graph_light_planning_allowed") is True
        and record.get("risk") == "low"
    )


def graph_refs_max(config: dict) -> int:
    return config.get("plan_contract", {}).get("graph_refs_max", 5)
