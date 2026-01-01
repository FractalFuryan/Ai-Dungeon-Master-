# Release v1.1.0: Roll20 Integration 🎲⚔️

## What's New

**AI Dungeon Master now integrates with Roll20!**

Bring persistent memory, switchable personas, and intelligent narration to your Roll20 games — all via chat commands.

### Key Features

✅ **Chat-based AI DM** - Use `!aidm` commands for narration  
✅ **Roll20-native dice** - AI returns `/roll` commands using your character sheet stats  
✅ **Persistent campaign memory** - Story continuity across sessions  
✅ **Switchable personas** - 6 DM personalities (classic, gothic, whimsical, cosmic, noir, tavern)  
✅ **Turn queue system** - `!aidm myturn` for organized large groups  
✅ **ToS-compliant** - Sandbox-safe, no violations, no hacks

### Installation

1. Deploy the backend (free on Render/Fly.io)
2. Install the API script in your Roll20 game (Pro required)
3. Open the relay page in your GM browser
4. Start narrating!

**Full guide:** [ROLL20_GUIDE.md](https://github.com/FractalFuryan/Ai-Dungeon-Master-/blob/main/ROLL20_GUIDE.md)

---

## Philosophy

This integration respects Roll20's authority:

- **Dice belong to Roll20** (AI never rolls)
- **Mechanics belong to Roll20** (AI never overrides)
- **Story belongs to the AI** (persistent memory and narration)

We enhance. We never replace.

---

## Technical Details

### New Files

- `roll20/aidm-roll20.js` - Sandbox-safe Roll20 API script
- `relay/roll20-relay.html` - GM relay page for command processing
- `server/roll20_adapter.py` - Backend adapter with input sanitization
- `roll20/macros.example` - Example Roll20 macros for quick commands

### Architecture

```
Players (!aidm commands)
    ↓
Roll20 API Script (queue)
    ↓
GM Relay Page
    ↓
AI DM Backend
    ↓
Narration Response
    ↓
Roll20 Chat
```

Manual paste workflow ensures ToS compliance and reliability.

---

## Example in Play

**Player:** `!aidm I carefully pick the lock on the ancient chest`

**AI DM Response:**  
*The rusted lock resists at first, then yields with a soft click. Inside, glinting in torchlight, lies a silver amulet engraved with draconic runes...*

**GM:** *(pastes into Roll20 chat)*

**Player:** Selects token → `!aidm roll perception`  
**Roll20:** `/roll 1d20 + @{selected|perception_mod} for perception`  
*(Uses character sheet stats, animated roll, full Roll20 experience)*

---

## Roadmap

Next enhancements:
- Browser extension for automatic relay (v1.2.0)
- Turn tracker bidirectional sync
- Automatic handout generation
- Campaign import/export between web and Roll20 modes

---

## Breaking Changes

None. This is an additive feature.

Existing web/mobile voice mode continues to work identically.

---

## Migration Guide

**From v1.0.0 to v1.1.0:**

No migration needed for existing web/mobile users.

**To add Roll20 support:**
1. Pull latest code
2. Install dependencies (no new requirements)
3. Deploy updated backend
4. Follow [ROLL20_GUIDE.md](https://github.com/FractalFuryan/Ai-Dungeon-Master-/blob/main/ROLL20_GUIDE.md)

---

## Known Limitations

- Requires Roll20 Pro subscription (for API scripts)
- Manual paste workflow (browser extension coming in v1.2.0)
- GM must process queue via relay page

These are intentional design choices for ToS compliance and reliability.

---

## Community

**Feedback welcome!**

- 💬 [GitHub Discussions](https://github.com/FractalFuryan/Ai-Dungeon-Master-/discussions)
- 🐛 [Report Issues](https://github.com/FractalFuryan/Ai-Dungeon-Master-/issues)
- ⭐ Star if you love it!
- 🔀 Fork to make it your own

---

## Credits

Built with respect for:
- Roll20's API constraints
- Tabletop gaming culture
- The sanctity of physical (and VTT) dice

**Made for storytellers. By storytellers.**

---

## Full Changelog

See [CHANGELOG.md](https://github.com/FractalFuryan/Ai-Dungeon-Master-/blob/main/CHANGELOG.md)

---

**Ready to enhance your Roll20 game?**

Download the release, follow the guide, and bring AI narration to your virtual table. ⚔️🎲

*The narrative awakens.*
