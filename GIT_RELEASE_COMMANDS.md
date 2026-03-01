# Git Commands for Release v1.1.0

## Stage All Files
```bash
git add .
```

## Commit Message (Copy This)
```
Release v1.1.0: Roll20 Integration

MAJOR FEATURE: AI Dungeon Master now integrates with Roll20! 🎲⚔️

New Files:
- roll20/aidm-roll20.js - Sandbox-safe Roll20 API script
- relay/roll20-relay.html - GM relay page for command processing
- server/roll20_adapter.py - Backend adapter with input sanitization
- ROLL20_GUIDE.md - Complete integration documentation
- ROLL20_QUICK_START.md - 5-minute setup guide
- roll20/macros.example - Ready-to-use Roll20 macros

Documentation:
- CHANGELOG.md - Full release history
- RELEASE_NOTES.md - GitHub release template
- LICENSE - MIT License
- screenshots/ - Screenshot guidelines

Infrastructure:
- scripts/release-prep.sh - Automated release validation
- Updated README.md - Roll20 mode prominently featured
- Updated server/main.py - Roll20 router integrated

Features:
✅ Chat-based AI DM via !aidm commands
✅ Persistent campaign memory per Roll20 game
✅ 6 switchable DM personas (classic, gothic, whimsical, cosmic, noir, tavern)
✅ Turn queue system with !aidm myturn
✅ Roll20-native dice (AI returns /roll commands, never touches mechanics)

Philosophy:
✅ Dice sovereignty - Roll20 owns all rolls
✅ GM authority - AI narrates, never overrides
✅ Table trust - No hidden mechanics
✅ ToS respect - Clean relay pattern, no sandbox violations

Technical:
- GM relay pattern (manual paste workflow, ToS-safe)
- Input sanitization (500 char limit, HTML stripping)
- Campaign-namespaced memory (roll20:{campaign_id})
- Health check endpoint (/roll20/health)
- Browser extension-ready architecture

This release extends AI Dungeon Master to virtual tabletops while
maintaining core principles: the AI facilitates, never dictates.

Breaking Changes: None
Migration: No changes needed for existing web/mobile users

See ROLL20_GUIDE.md for complete setup instructions.
See CHANGELOG.md for full release notes.

The narrative awakens. ⚔️🎲
```

## Create Tag
```bash
git tag -a v1.1.0 -m "Roll20 Integration Release - AI DM for virtual tabletops"
```

## Push to GitHub
```bash
git push origin main --tags
```

## Verify Release
```bash
git log --oneline -1
git tag -l
```

---

## Post-Push: Create GitHub Release

1. Go to: https://github.com/FractalFuryan/Ai-Dungeon-Master-/releases/new

2. Select tag: `v1.1.0`

3. Release title:  
   `v1.1.0: Roll20 Integration 🎲⚔️`

4. Copy body from `RELEASE_NOTES.md`

5. Optional attachments:
   - Zip of `relay/roll20-relay.html` (standalone relay page)
   - Zip of `roll20/aidm-roll20.js` (API script)

6. Click **Publish Release**

---

## Quick Deployment Test

After pushing, verify the integration works:

```bash
# Start backend locally
uvicorn server.main:app --reload

# In browser:
# 1. Open relay/roll20-relay.html
# 2. Set backend URL to http://localhost:8000
# 3. Paste test JSON:
AIDM_QUEUE:[{"campaign_id":"test123","player_name":"TestPlayer","text":"I search the room","selected":[]}]

# 4. Click Process Queue
# 5. Verify you get narration response
```

Expected response structure:
```json
{
  "chat": "<div style='...'>The dimly lit chamber reveals...</div>"
}
```

If this works → Backend integration is good → Ready for production deployment

---

**Release Status: READY TO SHIP** ✅🚀

The narrative awakens. Go make it live. ⚔️🎲
