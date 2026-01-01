# AI Dungeon Master for Roll20

**Voice-first AI Dungeon Master companion for Roll20 — narration, memory, and turns via chat**

This integration brings intelligent AI narration and campaign memory to your Roll20 games while **fully respecting Roll20's authority** over dice, character sheets, tokens, and turn tracker.

---

## What This Does

✅ **AI narration** via chat commands  
✅ **Persistent campaign memory** across sessions  
✅ **DM persona switching** (gothic, whimsical, cosmic, etc.)  
✅ **Turn discipline** with queue management  
✅ **Roll20-native dice** (AI never touches mechanics)

---

## What This Does NOT Do

❌ Roll dice for you (Roll20 handles that)  
❌ Override GM authority  
❌ Control tokens or character sheets  
❌ Replace Roll20's voice/video  
❌ Require Pro subscription upgrades (API scripts need Pro)

---

## Architecture (The Real Deal)

Roll20 has a strict API sandbox that **does not allow outbound HTTP requests**. This integration uses a **GM relay pattern** that is:

- ✅ **ToS-compliant**
- ✅ **Sandbox-safe**
- ✅ **No hacks or workarounds**

```
Players type !aidm commands
    ↓
Roll20 API script captures & queues
    ↓
GM dumps queue via !aidm_dump
    ↓
GM pastes into relay page (browser tab)
    ↓
Relay sends to AI DM backend
    ↓
AI returns narration
    ↓
GM pastes narration into Roll20 chat
```

**Yes, there's manual pasting involved in the MVP.** This is intentional and aligns with how serious Roll20 tools work. Future enhancement: browser extension for auto-relay (still ToS-safe).

---

## Installation

### Prerequisites

- Roll20 **Pro subscription** (required for API scripts)
- Deployed AI DM backend (see main README for deployment options)
- Modern web browser (for GM relay page)

### Step 1: Deploy the Backend

Follow the deployment guide in the main README to get your backend running on Render, Fly.io, or similar.

**Note your deployed URL** — you'll need it for the relay page.

### Step 2: Install the Roll20 API Script

1. Open your Roll20 game as GM
2. Go to **Settings → API Scripts**
3. Click **New Script**
4. Name it `AI DM`
5. Copy the entire contents of [`roll20/aidm-roll20.js`](roll20/aidm-roll20.js)
6. Paste into the script editor
7. Click **Save Script**

You should see in the API console:
```
AI Dungeon Master API script loaded successfully.
```

### Step 3: Set Up the GM Relay Page

1. Open [`relay/roll20-relay.html`](relay/roll20-relay.html) in a browser tab
2. Update the **Backend URL** field with your deployed URL
3. Keep this tab open during your game session
4. Bookmark it for future sessions

**Optional:** Host this page on GitHub Pages or Netlify for easier access.

---

## Usage

### Basic Workflow (GM)

1. Players type `!aidm` commands in Roll20 chat
2. Roll20 API script captures and queues them
3. When ready to process, GM types: `!aidm_dump`
4. Copy the whispered `AIDM_QUEUE:...` JSON
5. Paste into the relay page
6. Click **Process Queue**
7. Copy the returned narration
8. Paste into Roll20 chat

**Tip:** Process every 2-3 commands for smooth flow, or batch at natural breaks.

---

## Player Commands

All commands start with `!aidm`:

### Narrative Actions (Default)
```
!aidm I carefully push open the heavy oak door
!aidm I search the room for traps
!aidm I attempt to persuade the guard
```

AI DM responds with vivid narration based on your action.

### Dice Rolls (Roll20-Native)
```
!aidm roll stealth
!aidm roll perception
!aidm roll attack
```

**Returns a Roll20 roll command** that uses your character sheet stats.  
**Select your token first** for accurate modifiers.

### Turn Queue
```
!aidm myturn
```

Adds you to the speaking queue. GM processes with `!aidm next`.

### DM Persona
```
!aidm persona gothic
!aidm persona whimsical
!aidm persona cosmic
```

Changes the AI DM's narrative style. Available personas:
- `classic` — Traditional fantasy narrator
- `gothic` — Dark, atmospheric, Ravenloft vibes
- `whimsical` — Lighthearted, Terry Pratchett energy
- `noir` — Gritty detective, shadows and rain
- `cosmic` — Eldritch horror, vast and unknowable
- `tavern` — Casual, conversational, "around the table" feel

### Help
```
!aidm help
```

Shows command reference (whispered to you).

---

## GM Commands

### Process Queue
```
!aidm_dump
```

Exports queued commands as JSON (whispered to GM). Copy this to the relay page.

### Clear Queue (Emergency)
```
!aidm_clear
```

Clears all pending commands without processing them.

### Advance Turn
```
!aidm next
```

Calls the next player from the turn queue.

---

## Example Session Flow

**Player (Elise):** `!aidm I light a torch and peer into the darkness`  
**Player (Theron):** `!aidm I ready my crossbow and cover her`

**GM:** `!aidm_dump`  
*(Copies JSON, pastes into relay, clicks Process)*

**Relay returns:**
```
<div style='font-style: italic; color: #8B4513;'>
The torch flares to life, casting dancing shadows down the corridor. 
Stone walls glisten with moisture, and you hear the distant echo of 
dripping water. Theron's crossbow clicks softly as he takes aim into 
the black void ahead.
</div>
```

**GM:** *(Pastes into Roll20 chat)*

**Player (Elise):** `!aidm roll perception`  
**Relay returns:** `/roll 1d20 + @{selected|perception_mod} for perception`  
**GM:** *(Pastes — Roll20 executes the roll using Elise's sheet)*

---

## Campaign Persistence

Each Roll20 campaign gets its own persistent memory automatically:

- **Campaign ID** from Roll20 is used as the session key
- **Memory persists** across game sessions
- **Persona preferences** saved per campaign
- **Turn queues** maintained between dumps

No manual session management required.

---

## Voice Integration (Optional)

The AI DM also supports **voice mode** for richer immersion:

1. Open the web client on a phone/tablet: `https://your-backend.com`
2. Create or join the same session ID
3. Use voice input alongside Roll20 chat commands

Voice and Roll20 share the same campaign memory.

---

## Troubleshooting

### "Queue is empty" when dumping
- No `!aidm` commands were captured
- Check that the API script is running (Settings → API Scripts)
- Try `!aidm help` to test

### "Backend URL not configured"
- Update the relay page with your deployed backend URL
- Must include `https://` and no trailing slash

### "JSON parse error"
- Make sure you copied the **entire** whisper starting with `AIDM_QUEUE:`
- Check for truncation in very large dumps

### "Only the GM can dump the queue"
- API commands like `!aidm_dump` are GM-only
- Regular players use `!aidm` for actions

### Persona not changing
- Typo in persona name? Try `!aidm persona classic`
- Check valid personas with `!aidm help`
- Persona applies to **future** narration, not past messages

---

## Performance Tips

- **Batch processing:** Dump every 3-5 commands for natural flow
- **Use macros:** Create Roll20 macros for common commands
- **Token selection:** Always select your token before `!aidm roll` commands
- **Relay tab:** Keep it open in a separate window for quick access

---

## Future Enhancements (Not MVP)

These are **planned but not required** for the current release:

- 🔧 Browser extension for automatic relay (zero manual pasting)
- 🔧 Bidirectional turn tracker sync with Roll20
- 🔧 Auto-generated handouts for NPCs and locations
- 🔧 Campaign export/import between web and Roll20 modes

The MVP is fully functional and respectful of Roll20's ecosystem.

---

## Philosophy

This integration follows the core AI Dungeon Master principles:

> **The table is the authority.**  
> **The AI is a facilitator, not a dictator.**  
> **Dice rolls belong to the players and the VTT, not the AI.**

Roll20 handles:
- Dice mechanics
- Character sheets
- Token movement
- Turn order visualization
- GM authority

AI DM handles:
- Rich narration
- Campaign memory
- Atmospheric mood
- Turn discipline
- Persona consistency

They complement, never compete.

---

## Support & Feedback

- **Issues:** [GitHub Issues](https://github.com/FractalFuryan/Ai-Dungeon-Master-/issues)
- **Discussions:** [GitHub Discussions](https://github.com/FractalFuryan/Ai-Dungeon-Master-/discussions)
- **Main Docs:** [README.md](../README.md)

---

## License

Same as main project — see [LICENSE](../LICENSE)

---

**Ready to enhance your Roll20 game with AI narration?**  
Install the API script and open the relay page. ⚔️🎲
