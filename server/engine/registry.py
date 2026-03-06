from typing import Any, Dict, Optional


class EngineRegistry:
    """Simple runtime registry that decouples engine construction from access."""

    def __init__(self):
        self.engines: Dict[str, Any] = {}

    def register(self, name: str, engine: Any) -> None:
        self.engines[name] = engine

    def get(self, name: str) -> Optional[Any]:
        return self.engines.get(name)

    def snapshot(self) -> Dict[str, str]:
        return {name: engine.__class__.__name__ for name, engine in self.engines.items()}
