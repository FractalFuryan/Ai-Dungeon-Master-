from typing import Any, Dict


class WorldEngine:
    """Lightweight world metrics propagation from player events."""

    def __init__(self, world_state: Dict[str, Any]):
        self.world = world_state
        self.metrics = world_state.setdefault(
            "metrics",
            {
                "cohesion": 0.0,
                "disruption": 0.0,
                "tension": 0.0,
                "entropy": 0.0,
                "drift": 0.0,
                "equilibrium": 1.0,
                "instability": 0.0,
            },
        )

    def apply_event(self, event: Dict[str, Any]) -> Dict[str, float]:
        C = float(event.get("C", 0.0))
        D = float(event.get("D", 0.0))
        T = float(event.get("T", 0.0))
        H = float(event.get("H", 0.0))

        self.metrics["cohesion"] = C
        self.metrics["disruption"] = D
        self.metrics["tension"] = T
        self.metrics["entropy"] = H

        eta = 0.05
        self.metrics["drift"] += eta * (C - D)

        gap = abs(C - D)
        self.metrics["equilibrium"] = 1.0 / (1.0 + gap)
        self.metrics["instability"] = max(0.0, D - C) + max(0.0, T) + H

        return self.metrics
