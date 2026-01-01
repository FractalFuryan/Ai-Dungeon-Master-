# Turn System + DM Personas Implementation Guide

## What's New ⚔️🎭⏱️

Your AI Dungeon Master now has:

### 1. **DM Personas** (Voice + Tone)
- 🎭 **Classic Fantasy DM** - Warm, gravitas, vivid (voice: `alloy`)
- 🌙 **Gothic Horror Master** - Eerie, foreboding, tension (voice: `echo`)
- ✨ **Whimsical Storyteller** - Cheerful, puns, delightful (voice: `fable`)
- 🤖 **Sci-Fi Overseer** - Cold, clinical, authoritative (voice: `onyx`)

### 2. **Voice-First Turn System**
- Players say **"my turn", "me", "next", "i go"** → added to queue
- **Only active player** gets full DM narration
- **Others hear whisper**: "(Waiting for Alice's turn...)"
- **Host can pass turn** with "Pass Turn" button
- **Auto-advance** on freeform actions when no one has turn

### 3. **Real-Time Turn Display**
- Shows **who's currently active**
- Shows **upcoming queue** (next 5 players)
- Updates all players in **real-time** via WebSocket

---

## How to Play

### Host Creates Session
1. Click **"Create New Session"**
2. QR code appears
3. **Persona dropdown** and **Pass Turn button** appear (host only)
4. Change persona anytime → all players hear new voice instantly

### Players Join
1. Scan QR or use session ID
2. Enter their name
3. See **turn display** showing current active player

### During Gameplay

**To claim turn:**
- Say: "**My turn**", "**Me**", "**Next**", "**I go**", "**I act**"
- Added to queue automatically
- Becomes active when it's their turn

**Active player:**
- Say action: "I attack the goblin"
- Get full DM narration + audio response
- Turn auto-passes to next in queue (optional—see code)

**Waiting player:**
- Say anything → get whisper: "(Waiting for Alex...)"
- No action taken yet
- Encourages hand-raising protocol

**Host override:**
- Click **"Pass Turn →"** button anytime
- Advances to next in queue
- Useful if someone's AFK

---

## Code Architecture

### Backend (Python)

**`server/llm.py`** — Personas
```python
PERSONAS = {
    "classic": {"name": "...", "system_prompt": "...", "voice": "alloy"},
    "dark": {...},
    "whimsical": {...},
    "scifi": {...}
}

generate_narration_with_persona(session_id, prompt, persona_key)
# Returns: {"text", "audio_base64", "voice", "persona_name"}
```

**`server/dm_engine.py`** — Turn Logic
```python
TURN_CLAIM_PHRASES = ["my turn", "me", "i go", "next", "i'm next", ...]

is_turn_claim(text) → bool

process_action(session_id, player_name, action_text)
# Detects turn claims
# Enforces active player
# Returns narration or whisper
```

**`server/main.py`** — Endpoints
```
POST /session/set_persona?persona=dark
POST /session/next_turn
WebSocket /ws/{session_id}
  - Broadcasts turn_update, persona_update, narration
```

### Frontend (JavaScript)

**`client/app.js`** — Turn Display + Persona UI
```javascript
myName, isHost, sessionId
connectWebSocket() → handles all message types
addLog(text, type) → displays narration/system/whisper
ws.send({"type": "voice_input", "text", "player_name"})
```

**`client/index.html`** — UI
```html
#persona-controls    → dropdown (host only)
#turn-display        → active player + queue
#pass-turn button    → manual turn advance (host only)
#log                 → chat history
```

---

## Testing Checklist

- [ ] **Session Create**: QR generates, host controls appear
- [ ] **Join via QR**: Auto-joins, prompts name
- [ ] **Persona Switch**: Dropdown changes voice instantly (all hear it)
- [ ] **Turn Claim**: Say "my turn" → added to queue
- [ ] **Active Narration**: Only active player gets full DM response
- [ ] **Whisper Non-Active**: Non-active says something → gets whisper
- [ ] **Pass Turn**: Host clicks button → next player becomes active
- [ ] **Audio Playback**: Narration plays TTS audio in browser
- [ ] **Multi-Player**: 2+ phones in same session → see same turn queue
- [ ] **Graceful Fallback**: Works without audio if TTS fails

---

## Known Limitations & Future Work

1. **Turn Auto-Advance** (optional)
   - Currently commented out in `dm_engine.py`
   - Uncomment if you want turn to pass automatically after action
   - Keep commented for host control

2. **Async Broadcasting**
   - Turn updates use `asyncio.create_task()` to avoid blocking
   - Safe but slightly async-heavy; upgrade to proper broadcast channel in prod

3. **Queue Persistence**
   - Queue clears when session ends
   - No persistence across sessions (add Redis for this)

4. **Voice Recognition Latency**
   - Browser SpeechRecognition has ~1-2s delay
   - Server processes immediately; small visual lag expected

5. **No Persona Lock**
   - Only host can change persona currently
   - Could add role-based access in future

---

## Quick Debugging

**"Turn system not updating?"**
- Check WebSocket is open (browser DevTools → Network)
- Verify `player_name` is being sent in voice_input

**"Persona not changing?"**
- Ensure `/session/set_persona` endpoint is callable (check CORS)
- Check OpenAI API key in `.env`

**"No audio?"**
- Browser TTS fallback should kick in
- Check browser speaker volume & permissions
- Server TTS requires valid OpenAI API key

---

## Next Moves

Pick one:

1. **Persistent Campaigns** — Save/load via SQLite
2. **Combat Mode** — Initiative auto-sort, HP tracking
3. **Dice Integration** — Wire `/dice/roll` into narration
4. **Grok API** — Drop-in OpenAI replacement

You've built something genuinely playable. Ship it. ⚔️🎙️⏳
