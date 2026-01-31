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
                "active_player": None,
                "world_flags": {},
                "session_stats": {
                    "total_actions": 0,
                    "avg_imagination": 0.0,
                    "frame_uses": {}
                }
            }
            logger.info(f"Created new session: {self.session_id[:8]}...")
        
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

def update_memory(session_id: str, key: str, value):
    """Legacy compatibility - updates session memory"""
    session = SessionMemory(session_id)
    mem = session.get()
    mem[key] = value

