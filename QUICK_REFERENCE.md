# 🎯 Quick Reference: VoiceDM Roll20 Harmony v1.2.0

## 🚀 Quick Start (3 Steps)

### 1. Configure
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-...
```

### 2. Install & Run
```bash
pip install -r requirements.txt
uvicorn server.main:app --host 0.0.0.0 --port 8000
```

### 3. Open Browser
Visit: **http://localhost:8000**

## 📚 Documentation

| Guide | Purpose |
|-------|---------|
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Complete feature overview |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production deployment |
| [QUICK_START.md](QUICK_START.md) | Getting started guide |
| [ROLL20_GUIDE.md](ROLL20_GUIDE.md) | Roll20 integration |

## ✨ What's New in v1.2.0

### Intelligence Features
- **🧠 Imagination Analysis**: Detects creative player input (0.0-1.0 score)
- **⚖️ Anti-Railroading**: Warns GM when limiting player choices
- **🎭 Narrative Frames**: 6 dynamic story frames adapt to player style
- **📊 Character Tracking**: Monitors player creativity & momentum

### Production Features
- **⚙️ Config Management**: Environment-based settings with `.env`
- **🔒 Input Validation**: Safety checks & sanitization
- **📈 Session Management**: Auto-cleanup, statistics, isolation
- **🩺 Health Monitoring**: `/health` and `/stats` endpoints
- **📝 Enhanced Logging**: Detailed debug info for GMs

### Interface Improvements
- **🖥️ Built-in Relay**: Interactive UI at `/` (no external hosting needed)
- **🔌 Connection Testing**: One-click backend verification
- **📊 Debug Output**: Full transparency on AI decisions

## 🎮 Roll20 Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `!aidm [action]` | Submit action | `!aidm I search for traps` |
| `!aidm_dump` | Get queue JSON | Copy to relay interface |
| `persona [name]` | Change DM style | `persona gothic` |
| `myturn` | Claim turn | Player indicates readiness |
| `scene` | View current scene | Shows where you are |
| `roll [dice]` | Roll dice | `roll 1d20+5` |

## 🎭 Available Personas

- **classic**: Traditional D&D fantasy
- **gothic**: Dark, atmospheric horror
- **whimsical**: Light-hearted fairy tale
- **scifi**: Hard sci-fi AI overseer

## 🔧 Architecture Overview

```
┌─────────────┐
│  Roll20 API │
│  (!aidm)    │
└──────┬──────┘
       │
       v
┌─────────────────┐
│  Relay UI (/)   │
│  JSON Queue     │
└──────┬──────────┘
       │
       v
┌────────────────────────────────────────┐
│  FastAPI Server (port 8000)            │
├────────────────────────────────────────┤
│  Input Validation → Imagination        │
│  Analysis → Frame Selection → LLM      │
│  → Response + Debug Info               │
└────────────────────────────────────────┘
```

## 📊 Narrative Frames

| Frame | Wonder | Risk | Best For |
|-------|--------|------|----------|
| Straightforward | 0.2 | 0.2 | Simple actions |
| Hidden Cost | 0.4 | 0.4 | Complications |
| Unexpected Ally | 0.6 | 0.3 | Serendipity |
| Moral Inversion | 0.7 | 0.5 | Ethical dilemmas |
| Foreshadowing | 0.8 | 0.2 | Plot hooks |
| Lateral Escape | 0.5 | 0.6 | Creative solutions |

## 🛠️ Troubleshooting

### Module Not Found
```bash
pip install -r requirements.txt
```

### Config Error
```bash
cp .env.example .env
# Add your OpenAI API key to .env
```

### Connection Failed
```bash
# Check server is running
curl http://localhost:8000/health
```

## 📈 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

Returns:
```json
{
  "status": "healthy",
  "service": "VoiceDM Roll20 Harmony",
  "version": "1.2.0",
  "openai_configured": true,
  "default_persona": "classic"
}
```

### Session Stats
```bash
curl http://localhost:8000/stats
```

Returns:
```json
{
  "active_sessions": 3,
  "session_ids": ["abc123", "def456", ...]
}
```

## 🎯 Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Interactive relay UI |
| `/health` | GET | Health check |
| `/stats` | GET | Session statistics |
| `/api/v1/roll20/command_batch` | POST | Process Roll20 events |
| `/docs` | GET | API documentation |

## 💡 Tips for GMs

1. **Check Debug Info**: Review imagination scores to understand player engagement
2. **Watch for Railroading**: System warns when variety drops
3. **Use Personas**: Switch style mid-session for mood changes
4. **Monitor Momentum**: High momentum = players are engaged
5. **Review Frame Selection**: Understand why certain outcomes were chosen

## 🌟 Advanced Features

### Session Timeout
- Default: 1 hour
- Automatic cleanup of inactive sessions
- Configure in `server/memory.py`

### Imagination Signals
- `detailed`, `elaborate`: Length-based
- `hypothetical`, `risky`: Creative phrases
- `tactical`, `clever`: Problem-solving
- `dialogue`, `metaphoric`: Roleplaying

### Anti-Railroading Detection
Triggers when:
- Action variety > outcome variety
- Confidence > 0.3
- Provides GM suggestions automatically

## 📦 File Structure

```
Ai-Dungeon-Master-/
├── server/
│   ├── __init__.py          # Package init
│   ├── config.py            # Settings
│   ├── main.py              # FastAPI app
│   ├── memory.py            # Sessions
│   ├── dm_engine.py         # Core logic
│   ├── llm.py               # OpenAI
│   ├── resonance.py         # Imagination
│   ├── ethics.py            # Safety
│   ├── frame_engine.py      # Frames
│   ├── character.py         # Tracking
│   └── roll20_adapter.py    # API adapter
├── roll20/
│   └── aidm-roll20.js       # Roll20 script
├── .env.example             # Config template
├── requirements.txt         # Dependencies
└── DEPLOYMENT.md            # Deploy guide
```

## 🚀 Deploy to Production

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Render.com (recommended)
- Railway.app
- Fly.io
- Environment variables
- Production checklist

---

**Version**: 1.2.0  
**Status**: ✅ Production Ready  
**License**: See [LICENSE](LICENSE)  
**Documentation**: See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
