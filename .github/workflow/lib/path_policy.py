class PathPolicy:
    """Classify paths as governance or memory based on orchestration config.

    Config is injected (not loaded here) so callers own I/O and this module
    stays testable with a plain dict.  Reads execute_contract.governance_prefixes
    and execute_contract.memory_prefixes from the orchestration config.
    """

    def __init__(self, config: dict):
        execute = config.get("execute_contract", {})
        self._governance = tuple(execute.get("governance_prefixes", []))
        self._memory = tuple(execute.get("memory_prefixes", []))

    def is_governance(self, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in self._governance)

    def is_memory(self, path: str) -> bool:
        return any(
            path.startswith(prefix) or ("/" + prefix.lstrip("/")) in path
            for prefix in self._memory
        )
