import json
import os
import sqlite3
from datetime import datetime
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DB_PATH = "campaigns.db"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./voicedm.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_connection():
    """Get a safe SQLite connection for Codespaces concurrent requests"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize both legacy and SQLAlchemy-backed schemas."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS campaigns (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            data JSON NOT NULL,
            updated DATETIME NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

    try:
        from . import models  # noqa: F401  # ensures metadata is registered

        Base.metadata.create_all(bind=engine)
    except Exception:
        # Keep legacy startup resilient even if ORM models are unavailable.
        pass


def save_campaign(campaign_id: str, name: str, data: dict):
    """Save campaign state to database"""
    conn = get_connection()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()

    assert "persona" in data.get("memory", {}), "Missing persona in memory"
    assert "turn_queue" in data.get("state", {}), "Missing turn_queue in state"
    assert "active_player" in data.get("state", {}), "Missing active_player in state"

    c.execute(
        """
        INSERT OR REPLACE INTO campaigns (id, name, data, updated)
        VALUES (?, ?, ?, ?)
        """,
        (campaign_id, name, json.dumps(data), now),
    )
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
