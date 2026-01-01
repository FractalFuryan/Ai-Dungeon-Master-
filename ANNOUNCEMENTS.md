# 📢 Announcement Templates

Copy-paste these for your release announcements!

---

## Twitter/X Post

```
🎲⚔️ Just launched AI Dungeon Master v1.1.0!

Voice-first tabletop RPG companion:
✨ QR code join → instant multiplayer
🎤 Push-to-talk AI narration
🎭 6 voiced DM personas
💾 Persistent campaigns
📱 Mobile apps (iOS/Android)
🎲 Roll20 integration

Respects physical dice. Open source. Fork it!

#TabletopRPG #DnD #AI #OpenSource

https://github.com/FractalFuryan/Ai-Dungeon-Master-
```

**With image:** Screenshot of QR join screen or Roll20 narration

---

## Reddit Post (r/rpg, r/DnD, r/Roll20)

### Title
```
[OC] I built an open-source voice-first AI Dungeon Master (v1.1.0 with Roll20 integration)
```

### Body
```
Hey folks! I just released v1.1.0 of AI Dungeon Master — a voice-first tabletop RPG companion that respects the table and physical dice.

**Core Features:**
- 🎤 Voice in/out: Push-to-talk → AI DM responds with narration
- 🎭 6 switchable personas (Classic Fantasy, Gothic Horror, Whimsical, Sci-Fi, Noir, Tavern)
- ✨ QR code join: Create session → scan → everyone's in
- 💾 Persistent campaigns with save/load
- 📱 Mobile-ready (pre-configured for iOS/Android apps)
- 🎲 **NEW:** Roll20 integration via chat commands (!aidm)

**Philosophy:**
- Dice belong to players (table trust by default)
- AI facilitates, never dictates
- GM has final authority
- Respects VTT constraints (Roll20 ToS-compliant)

**Tech Stack:**
- FastAPI + WebSockets
- OpenAI GPT-4o-mini + TTS
- SQLite persistence
- Pure HTML/JS (PWA-ready)
- Capacitor for mobile

**Roll20 Mode:**
- Chat-based AI DM via `!aidm` commands
- Uses Roll20's native dice (AI never rolls)
- Persistent memory per campaign
- ToS-compliant relay pattern

**Quick Start:**
```bash
pip install -r requirements.txt
uvicorn server.main:app --host 0.0.0.0 --port 8000
```
Open in browser → create session → share QR → play!

**GitHub:** https://github.com/FractalFuryan/Ai-Dungeon-Master-  
**License:** MIT (fork it!)  
**Docs:** Quick start, Roll20 guide, persona guide, mobile build guide

Looking for feedback and contributions! PRs welcome.

The narrative awakens. ⚔️🎲

---

**FAQ:**

*Q: Does it replace the GM?*  
A: No! It's a facilitator. GM controls personas, turns, saves. Players drive the story.

*Q: What about dice?*  
A: Players roll physical dice by default (table trust). Roll20 mode uses Roll20's native rolls.

*Q: Can I use it for [system]?*  
A: It's system-agnostic. Works for D&D, Pathfinder, CoC, homebrew, etc.

*Q: Is voice required?*  
A: No. Roll20 mode is chat-only. Web mode supports voice but can work text-only too.

*Q: How much does it cost?*  
A: Free to self-host. Requires OpenAI API key (pay-as-you-go, ~$0.01/session).
```

---

## Hacker News Post

### Title
```
AI Dungeon Master – Voice-first tabletop RPG companion (open source)
```

### URL
```
https://github.com/FractalFuryan/Ai-Dungeon-Master-
```

### Comment (if posting as "Show HN")
```
Hey HN! I built a voice-first AI Dungeon Master for tabletop RPGs.

**Why this exists:**
- Virtual D&D sessions lack narrative immersion
- GMs need help with consistent NPC voices and world-building
- Remote tables want easy multiplayer without Discord
- Roll20 has mechanics but weak memory/narrative continuity

**What makes it different:**
- Voice-first: Push-to-talk → AI narrates in character
- Switchable personas: 6 DM styles with distinct voices (via OpenAI TTS)
- QR join: No accounts, just scan and play
- Table trust: Respects physical dice by default
- Roll20 mode: Chat-based AI that uses VTT's native rolls

**Tech:**
- FastAPI + WebSockets for real-time multiplayer
- GPT-4o-mini for narration (cheap, fast, creative)
- SQLite for campaign persistence
- Pure JS frontend (mobile via Capacitor)
- ToS-compliant Roll20 integration (relay pattern, no sandbox violations)

**Philosophy:**
The AI facilitates, never dictates. Players roll dice, GM has authority, AI provides depth.

**GitHub:** https://github.com/FractalFuryan/Ai-Dungeon-Master-  
**License:** MIT

Happy to answer questions about the architecture, AI prompting strategy, or design choices!
```

---

## GitHub Discussions Post

### Title
```
🎉 v1.1.0 Released - Roll20 Integration + Full Guides
```

### Body
```
The v1.1.0 release is now live! 🎲⚔️

**What's New:**
- Roll20 chat integration (`!aidm` commands)
- 6 DM personas (added Noir, Cosmic, Tavern)
- Complete Roll20 setup guide (ROLL20_GUIDE.md)
- Deployment guide (DEPLOYMENT.md)
- Example Roll20 macros
- Release automation scripts

**Quick Links:**
- [Release Notes](https://github.com/FractalFuryan/Ai-Dungeon-Master-/releases/tag/v1.1.0)
- [Roll20 Guide](https://github.com/FractalFuryan/Ai-Dungeon-Master-/blob/main/ROLL20_GUIDE.md)
- [Deployment Guide](https://github.com/FractalFuryan/Ai-Dungeon-Master-/blob/main/DEPLOYMENT.md)

**Try It:**
1. Deploy backend (Render free tier works)
2. Install Roll20 API script
3. Use `!aidm I enter the tavern`
4. Watch AI narration appear

**Next Up (v1.2.0):**
- Browser extension for Roll20 auto-relay
- Turn tracker sync
- Advanced persona customization

Feedback welcome! What would you like to see next?

The narrative awakens. ⚔️🎲
```

---

## Email to Gaming Communities (if applicable)

### Subject
```
New Open-Source Tool: Voice AI Dungeon Master for Tabletop RPGs
```

### Body
```
Hi [Community Name],

I wanted to share a project I've been working on that might interest tabletop RPG players and GMs.

AI Dungeon Master is an open-source voice-first companion for tabletop games. It provides:

- Voice narration with switchable personas (Gothic Horror, Whimsical, Sci-Fi, etc.)
- QR code multiplayer (no accounts needed)
- Persistent campaign memory
- Roll20 integration for virtual tables
- Mobile app builds (iOS/Android)

The philosophy is simple: the AI facilitates, never dictates. Players roll dice, GMs have authority, and the AI adds narrative depth.

It's free to use (requires OpenAI API key) and fully open source (MIT license).

**GitHub:** https://github.com/FractalFuryan/Ai-Dungeon-Master-  
**Quick Start:** 5 minutes from clone to playing

Would love feedback from experienced GMs and players!

Thanks,
[Your Name]
```

---

## ProductHunt Post (Optional)

### Tagline
```
Voice-first AI Dungeon Master for tabletop RPG tables
```

### Description
```
AI Dungeon Master brings immersive narration to your tabletop RPG sessions with voice-driven AI, switchable personas, and seamless multiplayer.

Perfect for D&D, Pathfinder, Call of Cthulhu, or any tabletop game.

Key Features:
🎤 Voice in/out with push-to-talk
🎭 6 distinct DM personas with unique voices
✨ QR code join (no accounts)
💾 Save/load campaigns
📱 Mobile apps (iOS/Android)
🎲 Roll20 chat integration
⚔️ Respects physical dice and GM authority

Open source (MIT) | Self-hostable | Privacy-first
```

---

## Discord Server Announcement

```
@everyone

🎉 **AI Dungeon Master v1.1.0 is LIVE!** 🎲⚔️

Voice-first tabletop RPG companion now with Roll20 integration.

**Features:**
✨ QR join → instant multiplayer
🎤 Voice AI narration (6 personas)
💾 Persistent campaigns
🎲 Roll20 chat mode (!aidm commands)
📱 Mobile-ready

**Try it:**
https://github.com/FractalFuryan/Ai-Dungeon-Master-

**Quick deploy:** Render/Fly.io free tier  
**License:** MIT (fork it!)

Looking for playtesters and contributors!

Questions? Ask in #ai-dungeon-master
```

---

## Usage Tips for Maximum Reach

**Twitter/X:**
- Post during peak hours (10am-2pm EST)
- Use GIF/video of QR join or voice narration
- Tag: @OpenAI (if they engage with community projects)
- Repost to @rpg and tabletop hashtags

**Reddit:**
- Post to r/rpg first (most general)
- Cross-post to r/DnD, r/Roll20, r/opensource
- Respond to comments actively (first hour is critical)
- Include "I'm the developer, AMA" in comments

**Hacker News:**
- Post as "Show HN: AI Dungeon Master..."
- Respond to technical questions thoroughly
- Post Tuesday-Thursday for best traction

**GitHub:**
- Enable Discussions immediately
- Add topics: `tabletop-rpg`, `ai`, `voice-assistant`, `roll20`
- Create Issues template for bug reports

---

**Ready to announce?** Pick 2-3 platforms to start. The narrative awakens. 📢🎲
