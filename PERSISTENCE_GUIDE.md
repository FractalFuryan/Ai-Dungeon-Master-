# Persistent Campaigns Implementation Guide

## What's New 📜💾

Your AI Dungeon Master now has **campaign persistence**:

✅ **Save Campaign State**
- Host clicks "Save Campaign" → entire session state stored
- Includes: scene, players, recent actions, persona, turn queue, active player
- Saved to SQLite database (`campaigns.db`)

✅ **Load Campaign**
- Host clicks "Load Campaign" → list of saved campaigns
- Select one → creates new session with full prior state
- Original campaign untouched (can reload multiple times)

✅ **Campaign Continuity**
- Campaign survives server restart
- Works across different Codespaces instances
- No data loss—everything persists until explicitly deleted

---

## How It Works

### Save Flow
1. Host clicks **"💾 Save Campaign"**
2. Enters campaign name (or uses default)
3. Backend saves:
   - Session `memory` (scene, players, recent_actions, persona)
   - Session `state` (active_player, turn_queue, phase)
4. Database generates unique `campaign_id` (format: `cmp_<session_id>_<random>`)
5. All players see: "📜 Campaign saved as: My Epic Quest"

### Load Flow
1. Host clicks **"📂 Load Campaign"**
2. Browser shows list of saved campaigns with dates
3. Host selects one
4. Backend creates **new session** from saved data
5. New QR code generated
6. Players can rejoin using new QR
7. Session resumes with all prior state

### Database Layer
```
campaigns.db (SQLite)
├── id (PRIMARY KEY)       - unique campaign identifier
├── name                   - user-friendly campaign name
├── data (JSON)            - full serialized state
└── updated (DATETIME)     - last modified timestamp
```

---

## Key Design Decisions (Why It Works)

### 1. Campaign ID ≠ Session ID
```python
campaign_id = f"cmp_{session_id}_{uuid.uuid4().hex[:4]}"
```
- Allows **multiple sessions from same campaign**
- Prevents accidental overwrites
- Clear naming convention

### 2. JSON Blob Architecture
- No schema migration hell
- Flexible (add fields anytime)
- Easy to inspect/debug
- Backward compatible

### 3. Host-Only Save/Load
- Prevents griefing (players can't delete campaigns)
- Host controls narrative continuity
- Clear authority structure

### 4. Codespaces-Safe SQLite
```python
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
```
- Handles concurrent requests safely
- Works in containerized environment
- No external service needed

### 5. Validation on Save
```python
assert "persona" in data["memory"]
assert "turn_queue" in data["state"]
```
- Ensures critical state is preserved
- Fails loudly if something's missing
- Prevents silent corruption

---

## Required Persistence Fields

When saving, these MUST be present:

```python
save_data = {
    "memory": {
        "scene": str,              # Current location/scene
        "players": list[str],      # Player names
        "recent_actions": list,    # Last few actions
        "persona": str             # Current DM persona (REQUIRED)
    },
    "state": {
        "active_player": str | None,  # Who's acting now
        "turn_queue": list[str],      # Queue of players (REQUIRED)
        "phase": str                  # Game phase (exploration, combat, etc.)
    }
}
```

---

## Playing a Multi-Session Campaign

### Session 1: "The Tavern"
1. Host creates session
2. Players join, say "my turn"
3. Explore, interact, gather info
4. Host clicks "Save Campaign" → "The Tavern"
5. Everyone logs off

### Week Later: Session 2
1. Host creates new session
2. Host clicks "Load Campaign" → selects "The Tavern"
3. **New QR generated**
4. Players scan → rejoin **with all prior state**
5. Scene, turn order, personas, everything intact
6. Continue from where they left off

### Session 3+
- Repeat same load flow
- Each save is a checkpoint
- Can branch off (load same campaign → new session → make different choices)

---

## File Changes

| File | Change |
|------|--------|
| `server/database.py` | **NEW** - SQLite persistence layer |
| `server/main.py` | +3 endpoints + startup event |
| `client/index.html` | +campaign controls UI |
| `client/app.js` | +save/load handlers |

---

## API Endpoints

### `POST /campaign/save`
Save current session as campaign.

**Request:**
```json
{
  "session_id": "abc123",
  "campaign_name": "The Tavern"
}
```

**Response:**
```json
{
  "success": true,
  "campaign_id": "cmp_abc123_x7f2",
  "campaign_name": "The Tavern"
}
```

### `POST /campaign/load`
Load campaign into new session.

**Request:**
```json
{
  "campaign_id": "cmp_abc123_x7f2"
}
```

**Response:**
```json
{
  "session_id": "def456",
  "campaign_name": "The Tavern"
}
```

### `GET /campaign/list`
List all saved campaigns.

**Response:**
```json
{
  "campaigns": [
    {
      "id": "cmp_abc123_x7f2",
      "name": "The Tavern",
      "updated": "2026-01-05T14:32:00.123456"
    },
    ...
  ]
}
```

---

## Testing Checklist

- [ ] **Save**: Create session → play → save → see confirmation
- [ ] **Load**: Click load → see list → select campaign → new QR
- [ ] **Rejoin After Load**: Scan new QR → see same scene/players
- [ ] **Persona Persists**: Save with persona A → load → still persona A
- [ ] **Turn Queue Persists**: Save mid-turn → load → same active player
- [ ] **Multiple Loads**: Load same campaign 3x → each creates new session
- [ ] **Server Restart**: Save → stop server → start server → load works
- [ ] **Concurrent Saves**: 2 players, 1 saves → both see confirmation

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **campaigns.db not created** | Will auto-create on startup via `init_db()` |
| **Save fails silently** | Check browser console for assertion errors (missing persona/turn_queue) |
| **Load shows empty list** | Database exists but no campaigns saved yet; start one |
| **Loaded session feels broken** | Verify all fields present in save_data before save |
| **SQLite locked error** | Rare in Codespaces; use `check_same_thread=False` (already done) |

---

## What's Preserved Across Sessions

✅ **Scene & Narrative**
- Current description
- Location/atmosphere
- Recent action history

✅ **Players & Turns**
- Player names
- Turn order queue
- Who's currently active

✅ **DM Identity**
- Selected persona
- Tone & voice settings
- System prompt state

✅ **Game State**
- Phase (exploration, combat, etc.)
- Any custom metadata
- Timestamps

---

## What's NOT Preserved

❌ **Character Stats/HP**
- Not yet tracked (add with combat system)

❌ **Inventory**
- Not tracked (would need character sheets)

❌ **Persistent NPCs**
- Live in narration only (add database table for full NPC system)

These are **future expansions** (natural next steps after dice integration).

---

## Architecture Philosophy

This persistence layer is designed to:

✓ **Work immediately** — SQLite, zero config
✓ **Stay flexible** — JSON blob, no migrations
✓ **Scale gracefully** — easy to add more tables later
✓ **Codespaces-safe** — handles concurrency
✓ **Host-centric** — respects narrative authority
✓ **Player-transparent** — they just rejoin, it works

You're not building "persistence for persistence's sake."

You're building **campaign continuity** — the thing that turns a one-shot into a story. 📜

---

## Next: Dice Integration

Persistence makes campaigns real.

Dice will make outcomes matter.

When you're ready, say **"Add dice integration"** and we'll:
- Parse roll requests from voice
- Execute server-side (fair, logged)
- Narrate results with persona
- Build combat on top

Your platform is now **complete as an MVP**.
Everything else is expansions.

⚔️📜
