import time
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

_MEM: Dict[str, Dict[str, Any]] = {}
_MEM_LOCK: Dict[str, bool] = {}
_SESSION_TIMEOUT = 3600  # 1 hour

class SessionMemory:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self._ensure_session()
    
    def _ensure_session(self):
        if self.session_id not in _MEM:
            _MEM[self.session_id] = {
                "created": time.time(),
                "last_access": time.time(),
                "scene": "You stand in a place of beginnings. What do you do?",
                "persona": "classic",
                "players": {},
                "recent_actions": [],
                "recent_outcomes": [],
                "turn_queue": [],
                "turn_scores": {},
                "active_player": None,
                "world_flags": {},
                "world_graph": {
                    "metrics": {
                        "cohesion": 0.0,
                        "disruption": 0.0,
                        "tension": 0.0,
                        "entropy": 0.0,
                        "drift": 0.0,
                        "equilibrium": 1.0,
                        "instability": 0.0,
                    },
                    "factions": {
                        "thieves_guild": {
                            "name": "Shadow Exchange",
                            "power": 5.0,
                            "territory": ["docks", "market_district"],
                            "attitude": {
                                "players": 0.2,
                                "city_guard": -0.7,
                                "merchant_guild": -0.3,
                            },
                            "goals": ["expand_docks", "recruit_informants"],
                            "resources": {"gold": 1000, "influence": 3},
                        },
                        "city_guard": {
                            "name": "City Guard",
                            "power": 6.0,
                            "territory": ["gate_district", "market_district"],
                            "attitude": {
                                "players": 0.0,
                                "thieves_guild": -0.6,
                                "merchant_guild": 0.3,
                            },
                            "goals": ["reduce_crime", "stabilize_market_district"],
                            "resources": {"gold": 600, "influence": 5},
                        },
                        "merchant_guild": {
                            "name": "Merchant Guild",
                            "power": 4.5,
                            "territory": ["market_district"],
                            "attitude": {
                                "players": 0.1,
                                "thieves_guild": -0.3,
                                "city_guard": 0.4,
                            },
                            "goals": ["secure_trade_routes", "expand_market_district"],
                            "resources": {"gold": 1500, "influence": 4},
                        },
                    },
                    "npcs": {
                        "elara": {
                            "faction": "thieves_guild",
                            "loyalty": 0.8,
                            "trust": {"players": 0.3},
                            "memory": [],
                            "hooks": {
                                "fear": "guards_discover_secret",
                                "desire": "rise_in_guild",
                                "debt": "owes_player_favor",
                            },
                        }
                    },
                    "pending_hooks": [],
                    "faction_log": [],
                },
                "geomancer_enabled": True,
                "geomancer": {
                    "C": 0.0,
                    "D": 0.0,
                    "T": 0.0,
                    "H": 0.0,
                    "drift": 0.0,
                    "equilibrium": 1.0,
                    "instability": 0.0,
                    "history": []
                },
                "session_stats": {
                    "total_actions": 0,
                    "avg_imagination": 0.0,
                    "frame_uses": {}
                }
            }
            logger.info(f"Created new session: {self.session_id[:8]}...")

        # Backward compatibility for existing sessions created before new fields
        mem = _MEM[self.session_id]
        mem.setdefault("turn_scores", {})
        world_graph = mem.setdefault("world_graph", {})
        metrics = world_graph.setdefault("metrics", {})
        metrics.setdefault("cohesion", 0.0)
        metrics.setdefault("disruption", 0.0)
        metrics.setdefault("tension", 0.0)
        metrics.setdefault("entropy", 0.0)
        metrics.setdefault("drift", 0.0)
        metrics.setdefault("equilibrium", 1.0)
        metrics.setdefault("instability", 0.0)
        world_graph.setdefault("factions", {})
        world_graph.setdefault("npcs", {})
        world_graph.setdefault("pending_hooks", [])
        world_graph.setdefault("faction_log", [])
        mem.setdefault("geomancer_enabled", True)
        geomancer = mem.setdefault("geomancer", {})
        geomancer.setdefault("C", 0.0)
        geomancer.setdefault("D", 0.0)
        geomancer.setdefault("T", 0.0)
        geomancer.setdefault("H", 0.0)
        geomancer.setdefault("drift", 0.0)
        geomancer.setdefault("equilibrium", 1.0)
        geomancer.setdefault("instability", 0.0)
        geomancer.setdefault("history", [])
        
        _MEM[self.session_id]["last_access"] = time.time()
    
    def get(self) -> Dict[str, Any]:
        return _MEM[self.session_id]
    
    def update_scene(self, new_scene: str):
        mem = self.get()
        mem["scene"] = new_scene
        mem["recent_actions"].append(f"Scene update: {new_scene[:50]}...")
        if len(mem["recent_actions"]) > 20:
            mem["recent_actions"] = mem["recent_actions"][-20:]
    
    def record_action(self, player: str, action: str, outcome: str, imagination: float):
        mem = self.get()
        mem["session_stats"]["total_actions"] += 1
        
        # Update imagination average
        stats = mem["session_stats"]
        old_avg = stats["avg_imagination"]
        total = stats["total_actions"]
        stats["avg_imagination"] = (old_avg * (total - 1) + imagination) / total
        
        # Track frame usage
        stats["frame_uses"][outcome] = stats["frame_uses"].get(outcome, 0) + 1

def cleanup_old_sessions():
    """Remove sessions older than timeout"""
    now = time.time()
    to_remove = []
    for session_id, mem in _MEM.items():
        if now - mem["last_access"] > _SESSION_TIMEOUT:
            to_remove.append(session_id)
    
    for session_id in to_remove:
        del _MEM[session_id]
        logger.info(f"Cleaned up stale session: {session_id[:8]}...")

# Legacy compatibility functions
def get_memory(session_id: str) -> dict:
    """Legacy compatibility - returns session memory dict"""
    session = SessionMemory(session_id)
    return session.get()

def update_memory(session_id: str, key: str, value=None):
    """Legacy compatibility - updates session memory.

    Supports both:
    - update_memory(session_id, "key", value)
    - update_memory(session_id, {"key": value, ...})
    """
    session = SessionMemory(session_id)
    mem = session.get()
    if isinstance(key, dict):
        mem.update(key)
    else:
        mem[key] = value

