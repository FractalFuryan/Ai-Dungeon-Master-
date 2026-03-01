# ⚡ Quick Start (60 Seconds)

## Step 1: Setup (30 seconds)

Open terminal:
```bash
pip install -r requirements.txt
uvicorn server.main:app --host 0.0.0.0 --port 8000
```

✅ Server running on `http://localhost:8000`

## Step 2: Make it Public (20 seconds)

If using **GitHub Codespaces**:
- Look for **Ports** tab at bottom
- Right-click port `8000`
- Select **Make Public**
- Copy the forwarded URL

If running **locally**:
- Just use `http://localhost:8000`

## Step 3: Play (10 seconds)

1. Open the URL in your browser
2. Click **Create New Session**
3. A **QR code** appears
4. Everyone scans it on their phone
5. Say your name
6. **Adventure begins!**

---

## Pro Tips

- **Host device:** Use laptop/tablet (easier to switch personas & save)
- **Player devices:** Use phones (push-to-talk is perfect on mobile)
- **Persona switching:** Host's persona dropdown = instant vibe change
- **Save progress:** Click "Save Campaign" after sessions
- **Load next week:** "Load Campaign" restores all progress

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Camera permission denied" | Click allow when browser asks for microphone + camera |
| "WebSocket connection failed" | Make sure port 8000 is Public (Codespaces) or correct URL (local) |
| "Voice doesn't work" | Reload page, check mic permissions, try Chrome/Firefox |
| "QR won't scan" | Make sure screen brightness is high, zoom to 100% |

---

## Next Steps

- Read [TURN_SYSTEM_GUIDE.md](TURN_SYSTEM_GUIDE.md) to understand group dynamics
- Check [PERSONA_GUIDE.md](PERSONA_GUIDE.md) for vibe options
- See [PERSISTENCE_GUIDE.md](PERSISTENCE_GUIDE.md) for campaign management

**Ready to play? Go create a session and invite your table.** 🎲⚔️

---

## What Each Persona Sounds Like

🎭 **Classic Fantasy** (alloy)
> *"The goblin's blade meets your armor with a metallic clang. What do you do, brave adventurer?"*

🌙 **Gothic Horror** (echo)
> *"The shadows deepen... something ancient stirs in the darkness. You sense a terrible presence watching."*

✨ **Whimsical** (fable)
> *"Pop! The confetti-spewing goblin tumbles backward! How delightfully silly! What's next, hero?"*

🤖 **Sci-Fi** (onyx)
> *"ALERT: Hostile entity engaged. Tactical assessment: Situation critical. Recommend immediate evasive action."*

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **WebSocket fails** | Check port 8000 is **Public** in Ports tab |
| **No audio** | Browser TTS fallback works; check speaker volume |
| **Persona doesn't change** | Ensure `.env` has valid `OPENAI_API_KEY` |
| **Turn queue stuck** | Refresh page; session state resets |
| **QR won't scan** | Use phone camera app → opens URL directly |

---

## Files You Changed

- `server/main.py` — Turn endpoints + session state
- `server/dm_engine.py` — Turn claim detection + enforcement
- `server/llm.py` — Persona system + TTS
- `client/app.js` — Turn UI + WebSocket handlers
- `client/index.html` — Turn display + persona dropdown

## Full Details

See `TURN_SYSTEM_GUIDE.md` for deep dive.

---

## What's Next?

Your system now handles:
- ✅ Multi-player voice sessions
- ✅ Fair turn management
- ✅ Voiced persona switching
- ✅ Real-time narration

Next highest-impact features:
1. **Persistent campaigns** (save/load)
2. **Dice integration** (wire rolls into narration)
3. **Combat mode** (initiative + HP)
4. **Grok API** (faster LLM)

Ship what you have. Add features based on play feedback. ⚔️
