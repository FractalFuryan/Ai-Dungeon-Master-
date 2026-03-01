# ⚔️ VoiceDM

**Persistent Narrative Ecology Engine**  
*Adaptive AI Dungeon Master with Deterministic Logic & Intergenerational Consequence Tracking*

A complete tabletop RPG system featuring **persistent worlds**, **intergenerational continuity**, **asymmetric truth layers**, and **psychological horror mechanics**. Built on a foundation of fair dice mechanics and player agency.

**Voice-driven · Multiplayer · QR Code Join · Zero Dependencies**

No apps. No accounts. Just phones, imagination, and consequences that echo through generations.

---

## 🧠 Core Architecture

VoiceDM is now a **Persistent Narrative Ecology Engine** with:

### World Layer
- **Worlds** – Persistent campaign universes with entropy/reverence tracking
- **Cycles** – Campaign arcs within worlds (active/archived)
- **Sessions** – Individual play sessions with historical notes
- **Locations** – Map nodes with ecology, arcanology, and history JSON blobs
- **Characters** – Player characters with vector types and retirement tracking

### Persistence Layer
SQLAlchemy-backed database with full ORM support:
- `worlds` – Global stability metrics (entropy, reverence)
- `cycles` – Campaign arcs with status tracking
- `sessions` – Play session records
- `characters` – Player character states
- `locations` – Map nodes with layered JSON data
- `map_ink` – Player annotations with mechanical bonuses
- `open_currents` – Inaction consequences and rumor seeds
- `legacy_ledger` – Intergenerational continuity
- `veil_nodes` – Psychological horror zones
- `perspective_vectors` – Asymmetric faction relationships

---

## 🎲 Headline Feature: Built-in Secure RNG & Dice System

VoiceDM includes a **complete, zero-dependency randomness and dice system** designed for fairness, replayability, and narrative control — without external services or APIs.

### 🎯 Resolution Core: 3d6 with Modifier Caps
- Expected center: 10–11
- Hard modifier cap: **max +3 / -3**
- Largest range applies first
- Everything must be narratively justified

### 🧠 Four Randomness Modes

| Mode | Purpose | Description |
|------|---------|-------------|
| **🔐 SECURE** (default) | Live play | Uses OS entropy (`secrets`) seeded by hardware noise. Unpredictable and fair. |
| **📝 DETERMINISTIC** | Replay / testing | Blake2b hash-chain RNG for perfect session replay and audits. |
| **⚖️ WEIGHTED** | Narrative shaping | Probability distributions with configurable bias for rare events. |
| **📐 LINEAR** | Education / puzzles | Predictable progression for teaching or logic puzzles. |

### 🎯 Integrated Dice Engine

```python
from server.mechanics import quick_resolve

# Basic resolution with modifier caps
result = quick_resolve(base_modifier=2, positives=[1, 1], negatives=[1])
# Automatically caps at ±3, sorts largest first

# Retirement calculation
legacy = Governors.calculate_retirement_multiplier(xp=1500, is_underdog=True)
# 1500 XP → 1800 banked, 1 legacy feature
```

---

## 🏛 System Governors & Safeguards

### 2:1 Anchor Enforcement
Before any fantastical narrative spike:
```python
if recent_mundane_anchors < 2:
    block_event()  # Must establish mundane reality first
```

### Silence Propagation
Veil nodes gain intensity each session:
```python
for node in veil_nodes:
    node.silence_level += delta
    # Thresholds: rumor → disappearance → encounter → penalty
```

### Peripheral Ripening
Unresolved plot threads intensify over time:
```python
for current in open_currents:
    current.intensity += 0.1
    if current.intensity >= 1.0:
        spawn_new_motive_node()
```

### Retirement Deposit System
```python
# 1000 XP = 1 legacy feature
multiplier = 1.2 if underdog else 0.8 if gifted else 1.0
banked_xp = xp_remaining * multiplier
```

### World Stability
Global metrics drive world events:
- **Entropy** – Ignored grim reminders, instability
- **Reverence** – Heroic acts, reverent retirements
- When `entropy > reverence` → world instability events

---

## 🗺 Map Engine

Dynamic map overlay system with:

- **Base map** + runtime overlays
- **Map ink** – Player annotations with mechanical bonuses
- **Veil nodes** – Psychological horror zones with silence levels
- **Faction influence** – Territory tracking
- **Runtime claiming** – Unlabeled areas become locations

```python
# Generate live map overlay
overlay_path = await map_engine.generate_overlay(
    world_id="world-123",
    cycle_id="cycle-456",
    locations=locations,
    map_inks=inks,
    veil_nodes=veils
)
```

---

## 📱 QR-Based Rule Scanner

Mobile-friendly rule scanner for instant ruleset loading:

- Scan QR codes with camera input
- Pre-indexed JSON rulesets (D&D 5e Basic included)
- Zero dependencies, works offline
- Integrates with dice system

**Access**: `http://localhost:8000/scanner`

**Supported formats:**
```
voicedm://rules/dnd5e/basic
{"ruleset": "dnd5e", "version": "basic"}
dnd5e_basic.json
```

---

## 🚀 MVP Implementation Status

### ✅ Core MVP Complete

**Persistence Layer**
- [x] SQLAlchemy models with UUID primary keys
- [x] Database migrations ready
- [x] Legacy campaign storage preserved

**Core Tables**
- [x] `worlds` – Global stability metrics
- [x] `cycles` – Campaign arc tracking
- [x] `sessions` – Play session records
- [x] `characters` – Player character states
- [x] `legacy_ledger` – Intergenerational memory
- [x] `open_currents` – Inaction consequences

**Mechanics Engine**
- [x] 3d6 resolution core with ±3 caps
- [x] Four randomness modes (SECURE, DETERMINISTIC, WEIGHTED, LINEAR)
- [x] Governor systems (2:1 anchor, silence propagation, ripening)
- [x] Retirement calculator with multipliers
- [x] World stability checks (entropy vs reverence)

**Map Engine**
- [x] Base map + overlay generation
- [x] Location markers with type-based coloring
- [x] Map ink annotations
- [x] Veil node visualization
- [x] Runtime area claiming

**Narrative Engine**
- [x] Six adaptive narrative frames
- [x] Rumor branching based on intensity
- [x] Frame selection based on creativity/entropy
- [x] Legacy ledger entries

**API Layer**
- [x] REST endpoints for all MVP entities
- [x] WebSocket support for real-time sync
- [x] Resolution endpoint (`/api/resolve`)
- [x] Retirement calculation (`/api/retirement/calculate`)
- [x] Health checks

**Testing**
- [x] 51 passing tests (pytest)
- [x] Modifier cap validation
- [x] Retirement multiplier logic
- [x] Governor system tests

### 🚧 Next Layers (Ready for Implementation)

**Advanced Tables**
- [ ] `veil_nodes` – Complete propagation logic
- [ ] `perspective_vectors` – Faction relationship tracking
- [ ] `retirements` – Full retirement feature integration

**Endpoints**
- [ ] Location CRUD with map integration
- [ ] MapInk CRUD with mechanical effects
- [ ] OpenCurrent progression triggers
- [ ] VeilNode silence propagation

**Integration**
- [ ] World→Cycle→Session→Character flow tests
- [ ] End-to-end narrative state machine
- [ ] Export/Import campaign data

---

## 🚀 Quick Start

### Option 1: Zero Dependencies (Recommended)

```bash
# Clone and run
git clone https://github.com/FractalFuryan/Ai-Dungeon-Master-.git
cd Ai-Dungeon-Master-

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Initialize database
python -c "from server.database import init_db; init_db()"

# Start server
uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
```

✅ **Full MVP core** – Worlds, cycles, characters, legacy  
✅ **Complete dice system** – 3d6 with secure RNG and modifier caps  
✅ **Governor systems** – 2:1 anchor, silence propagation, ripening  
✅ **Map overlays** – Dynamic location and ink rendering  

### Option 2: With LLM Enhancement (Optional)

```bash
# Add to .env
NARRATION_MODE=hybrid
OPENAI_API_KEY=sk-...
RANDOMNESS_MODE=weighted  # For dramatic weighting
```

✅ **Templates + LLM polish** – Best of both worlds  
✅ **Graceful fallback** – Works offline if API unavailable  
✅ **Cost effective** – Templates for common actions  

### Option 3: Roll20 Integration

See `ROLL20_GUIDE.md` for complete Roll20 setup as a chat-based assistant.

---

## ⚙️ Configuration

```env
# Database (SQLite for dev, Postgres for prod)
DATABASE_URL=sqlite:///./voicedm.db
# DATABASE_URL=postgresql://user:pass@localhost/voicedm

# Randomness Mode (secure|det|weighted|linear)
RANDOMNESS_MODE=secure

# For deterministic mode
RANDOMNESS_SEED=my_campaign_2024

# Server
HOST=0.0.0.0
PORT=8000

# Optional LLM Enhancement
NARRATION_MODE=template  # template | hybrid | llm
OPENAI_API_KEY=sk-...
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_mechanics.py -v

# Current coverage: 51 passing tests
```

---

## 📚 API Endpoints

### Worlds
- `POST /api/worlds` – Create new world
- `GET /api/worlds` – List all worlds
- `GET /api/worlds/{id}` – Get world details
- `POST /api/worlds/{id}/cycles` – Start new cycle
- `GET /api/worlds/{id}/legacy` – Get legacy entries

### Cycles
- `POST /api/cycles` – Create/archive-aware cycle
- `GET /api/cycles` – List cycles
- `GET /api/cycles/{id}` – Get cycle details

### Sessions
- `POST /api/sessions` – Create session
- `GET /api/sessions` – List sessions
- `GET /api/sessions/{id}` – Get session details

### Characters
- `POST /api/characters` – Create character
- `GET /api/characters` – List characters
- `GET /api/characters/{id}` – Get character details
- `POST /api/characters/{id}/xp` – Grant XP

### Resolution
- `POST /api/resolve` – Resolve action with modifiers
- `POST /api/retirement/calculate` – Calculate retirement deposit

### WebSocket
- `ws://localhost:8000/ws/{session_id}` – Real-time session sync

---

## 🎭 DM Personas

| Persona | Voice | Style | Best For |
|---------|-------|-------|----------|
| **Classic Fantasy** | Alloy | Warm, heroic, vivid | Traditional D&D |
| **Gothic Horror** | Echo | Brooding, ominous | Ravenloft / CoC |
| **Whimsical** | Fable | Playful, punny | Family games |
| **Sci-Fi Overseer** | Onyx | Cold, clinical | Cyberpunk |

---

## 🧠 Design Philosophy

> **"Reasoning is deterministic. Language is optional. Randomness is bounded."**

VoiceDM is built on three pillars:

1. **Deterministic Core** — Ethics, logic, and memory never rely on randomness
2. **Optional Polish** — LLMs enhance, never decide
3. **Bounded Randomness** — Dice decorate outcomes, never determine values

### What This Is:
- ✅ A stateful narrative simulation engine
- ✅ Intergenerational consequence tracking
- ✅ Psychological horror modeling
- ✅ Faction autonomy simulation

### What This Is Not:
- ❌ A campaign manager
- ❌ A monster manual
- ❌ A GM prep tool

---

## 📊 Current Stats

- **Version**: 1.4.0
- **Tests**: 51 passing
- **Core Tables**: 12
- **API Endpoints**: 15+
- **Randomness Modes**: 4
- **Narrative Frames**: 6

---

Built with:
- FastAPI + WebSockets
- SQLAlchemy + Pydantic
- Pure HTML/JS frontend
- Zero-dependency RNG

---

> 🎲 *"If it rolls dice, it should be fair. If it tells stories, it should be honest."*
