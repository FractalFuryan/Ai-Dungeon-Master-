# In-memory; upgrade to Redis
memory_store = {}

def get_memory(session_id: str) -> dict:
    return memory_store.get(session_id, {})

def update_memory(session_id: str, key: str, value):
    if session_id not in memory_store:
        memory_store[session_id] = {}
    memory_store[session_id][key] = value
