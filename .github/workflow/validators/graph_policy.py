def graph_refs_max(config: dict) -> int:
    return config.get("plan_contract", {}).get("graph_refs_max", 5)
