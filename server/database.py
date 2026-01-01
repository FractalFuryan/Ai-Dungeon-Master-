import sqlite3
import json
from datetime import datetime

DB_PATH = "campaigns.db"

def get_connection():
    """Get a safe SQLite connection for Codespaces concurrent requests"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database schema"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            data JSON NOT NULL,
            updated DATETIME NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_campaign(campaign_id: str, name: str, data: dict):
    """Save campaign state to database"""
    conn = get_connection()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    
    # Validate required fields
    assert "persona" in data.get("memory", {}), "Missing persona in memory"
    assert "turn_queue" in data.get("state", {}), "Missing turn_queue in state"
    assert "active_player" in data.get("state", {}), "Missing active_player in state"
    
    c.execute("""
        INSERT OR REPLACE INTO campaigns (id, name, data, updated)
        VALUES (?, ?, ?, ?)
    """, (campaign_id, name, json.dumps(data), now))
    conn.commit()
    conn.close()

def load_campaign(campaign_id: str) -> dict | None:
    """Load campaign state from database"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT data FROM campaigns WHERE id = ?", (campaign_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None

def list_campaigns() -> list[dict]:
    """List all saved campaigns, most recent first"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, updated FROM campaigns ORDER BY updated DESC LIMIT 20")
    rows = c.fetchall()
    conn.close()
    return [{"id": row[0], "name": row[1], "updated": row[2]} for row in rows]

def delete_campaign(campaign_id: str) -> bool:
    """Delete a campaign"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM campaigns WHERE id = ?", (campaign_id,))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0
