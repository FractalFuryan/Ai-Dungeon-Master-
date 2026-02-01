# ⚔️ VoiceDM Roll20 Harmony

**Adaptive AI Dungeon Master with Deterministic Logic & True Randomness**

Roll20 owns dice, sheets, tokens, and maps.  
This project adds **adaptive narration, memory, and non-linear DM logic** using a GM relay (sandbox-safe), plus a **built-in, zero-dependency dice system** designed for fairness and replayability.

**Voice-driven · Multiplayer · QR Code Join · Zero Dependencies**

No apps. No accounts. No Discord. Just phones and imagination.

![RNG](https://img.shields.io/badge/Randomness-OS_Entropy-blue)
![Dice](https://img.shields.io/badge/Dice-Integrated_System-green)
![LLM](https://img.shields.io/badge/LLM-Optional_Polish-orange)
![Offline](https://img.shields.io/badge/Offline-Zero_API-red)

---

## 🎲 **Headline Feature: Built-in Secure RNG & Dice System**

VoiceDM includes a **complete, zero-dependency randomness and dice system** designed for fairness, replayability, and narrative control — without external services or APIs.

> 🔐 Randomness is a **core system**, intentionally separated from narrative logic and ethics.

### 🧠 Four Randomness Modes

| Mode | Purpose | Description |
|------|---------|-------------|
| **🔐 SECURE (default)** | Live play | Uses OS entropy (`secrets`) seeded by hardware noise. Unpredictable and fair. |
| **📝 DETERMINISTIC** | Replay / testing | Blake2b hash-chain RNG for perfect session replay and audits. |
| **⚖️ WEIGHTED** | Narrative shaping | Probability distributions with configurable bias for rare events. |
| **📐 LINEAR** | Education / puzzles | Predictable progression for teaching or logic puzzles. |

### 🎯 Integrated Dice Engine

VoiceDM includes a full dice engine with:
- **Standard RPG dice**: `d20`, `2d6+3`, `4d6-1`, `d100`
- **Advantage/Disadvantage**: `d20 advantage`, `d20 disadvantage`
- **Critical detection**: Auto-detects nat 20 / nat 1
- **Roll history & statistics**: Track luck, detect patterns
- **Session-seeded determinism**: Same seed = same rolls

**Example usage:**
```python
from server.dice import quick_roll

# Basic roll
quick_roll("d20+5")           # → DiceResult(total=17, ...)

# Advantage
quick_roll("d20 advantage")   # Rolls twice, takes highest

# Session replay (for debugging or consistency)
from server.dice import DiceSystem
dice = DiceSystem(session_id="campaign-01")
dice.roll("d20")  # Always the same sequence
```

### 🔐 What "True Random" Means Here

VoiceDM uses **OS-level entropy pools** (same class used for cryptography and TLS) for secure randomness. This provides:

* ✅ **Hardware-seeded unpredictability** (interrupt timing, thermal noise)
* ✅ **Offline operation** (no API calls, no network)
* ✅ **Zero dependencies** (Python stdlib only)
* ✅ **Cross-platform support** (Linux, macOS, Windows)
* ✅ **Auditable** (seed tracking, history logs)

For tabletop, narrative, and fairness-critical systems, this is the **correct and industry-standard definition of true randomness**.

### 🧭 Design Rule: Bounded Randomness

Randomness is used to:
* Introduce **uncertainty** and **tension**
* Create **memorable moments** (critical hits/fails)
* Prevent **optimization certainty**
* Add **narrative surprise**

Randomness is **never** used to:
* Decide **ethics** or **morality**
* Override **player agency**
* Force **narrative outcomes**
* Hide **railroading patterns**
* Replace **GM judgment**

> 🎲 *"If it rolls dice, it should be fair. If it tells stories, it should be honest."*

---

## 📱 **QR-Based Rule Scanner (NEW)**

VoiceDM now includes a **mobile-friendly rule scanner** that lets you load RPG rulesets via QR codes or camera input.

### How It Works

1. **Scan a QR code** containing a ruleset identifier (e.g., `dnd5e_basic`)
2. **Pre-indexed JSON rules** load instantly from `server/rulesets/`
3. **Rules integrate** with the existing dice and randomness systems
4. **Zero breaking changes** — scanner is an optional add-on

### Access the Scanner

Visit **[http://localhost:8000/scanner](http://localhost:8000/scanner)** after starting the server.

### API Endpoints

- `GET /api/scanner/rulesets` - List available rulesets
- `POST /api/scanner/load` - Load ruleset from QR data
- `GET /scanner` - Mobile scanner interface

### Supported QR Formats

```
voicedm://rules/dnd5e/basic
{"ruleset": "dnd5e", "version": "basic"}
dnd5e_basic.json
dnd5e_basic
```

### Pre-Loaded Rulesets

- **D&D 5e Basic**: Combat, skills, spells, ability checks
- *(More rulesets coming: Pathfinder, Call of Cthulhu, custom systems)*

### Design Principles

- **Lightweight**: No OCR, no complex parsing (yet)
- **Pre-indexed**: JSON rulesets, not live scanning
- **Camera-ready**: HTML5 camera access on mobile
- **Fallback input**: Manual QR entry if camera unavailable
- **Zero dependencies**: Python stdlib only

---

## ✨ Core Principles

- **Player imagination is first-class input**
- **Anti-rail narrative logic** with visual warnings
- **Living character trajectories** (not profiling)
- **Non-linear success conditions**
- **GM/AI is first servant to the process**
- **Randomness decorates outcomes — never decides values**

## 🚀 Features

### Voice-Driven Multiplayer Experience
- **QR Code Join** – Host creates session → QR appears → Everyone scans → Instant multiplayer
- **Voice In / Voice Out** – Push-to-talk → AI Dungeon Master responds with immersive narration
- **4 Switchable DM Personas** – Classic Fantasy · Gothic Horror · Whimsical · Sci-Fi (each with unique voice + style)
- **Natural Turn System** – Say "my turn" or "next" → Get in queue → Only active player drives the story
- **Persistent Campaigns** – Save and load your ongoing adventure
- **Phone & Tablet First** – Works beautifully on mobile browsers

### Advanced Intelligence (v1.2.0+)
- **Imagination Analysis** – Detects creative, detailed player input and rewards it
- **Anti-Railroading Detection** – Warns when GM forces outcomes inappropriately
- **6 Adaptive Narrative Frames** – Story structures adapt to player creativity and risk
- **Session Management** – Isolated campaigns with auto-cleanup

### Foll20 Integration
- **GM Relay System** – No Roll20 HTTP calls, no ToS violations, no vendor lock-in
- **Chat-based Commands** – Players type `!aidm ...`, GM pastes JSON, system responds
- **Sandbox-Safe** – Works within Roll20's security model
- **See [ROLL20_GUIDE.md](ROLL20_GUIDE.md)** for complete setup

## 🚀 How It Works

### Voice-Driven Mode (Local/Mobile Play)
1. **Host creates session** → QR code appears
2. **Players scan** → Join instantly on their phones
3. **Push-to-talk** → Speak your action
4. **AI responds** → Immersive narration with character voice
5. **Natural turns** → Say "my turn" to drive the story

### Roll20 Relay Mode (Virtual Tabletop)
1. **Players type** `!aidm ...` in Roll20 chat
2. **GM runs** `!aidm_dump` to collect actions
3. **GM pastes** JSON into the VoiceDM relay page
4. **VoiceDM processes** using deterministic logic + optional randomness
5. **System returns** copy-ready narration + dice roll commands
6. **GM pastes** back into Roll20 chat

**No Roll20 HTTP calls. No ToS violations. No vendor lock-in.**

## 🪶 Quick Start

### Option 1: Zero Dependencies (Recommended)
```bash
# Clone and run
git clone https://github.com/FractalFuryan
- **Roll20 Integration** – Chat-based AI DM companion for virtual tabletops
- **Zero Setup** – Runs in GitHub Codespaces with one click

## 🚀 Quick Start (60 seconds)

### Option 1: Zero Dependencies (Recommended)
```bash
# Clone and run
git clone https://github.com/yourusername/Ai-Dungeon-Master-.git  
✅ **Full dice system** – Secure RNG, session replay, critical detection

### Option 2: With LLM Enhancement
```bash
# Add to .env file
NARRATION_MODE=hybrid  # or 'llm' for v1.2.0 behavior
OPENAI_API_KEY=sk-...
```
✅ **Templates + LLM polish** – Best of both worlds  
✅ **Graceful fallback** – Works offline if API unavailable  
✅ **Cost effective** – Templates for common actions, LLM for special moments

### Option 3: Configuration Examples

**Pure Template Mode** (Recommended for most users)
```env
NARRATION_MODE=template
RANDOMNESS_MODE=secure
DEFAULT_PERSONA=gothic
LOG_LEVEL=INFO
# No API keys needed!
```

**Hybrid Mode** (Templates + optional LLM polish)
```env
NARRATION_MODE=hybrid
RANDOMNESS_MODE=secure
OPENAI_API_KEY=sk-...
NON_LINEAR_BIAS=0.5  # More narrative surprises
```

**Debug/Replay Mode** (Deterministic for testing)
```env
NARRATION_MODE=template
RANDOMNESS_MODE=deterministic
RANDOMNESS_SEED=my_campaign_2024
# Same inputs = s & Narrative Frames

VoiceDM includes multiple narrative personas and frames that work **with or without LLMs**:

| Persona             | Voice   | Style                              | Best For                     | Template Coverage |
|---------------------|---------|------------------------------------|------------------------------|-------------------|
| **Classic Fantasy** | Alloy   | Warm, heroic, vivid descriptions   | Traditional D&D adventures   | ✅ Full          |
| **Gothic Horror**   | Echo    | Brooding, ominous, atmospheric     | Ravenloft / Call of Cthulhu  | ✅ Full          |
| **Whimsical**       | Fable   | Playful, punny, fairy-tale charm   | Light-hearted family games   | ✅ Full          |
| **Sci-Fi Overseer** | Onyx    | Cold, clinical, technical          | Cyberpunk / space opera      | ✅ Full          |

**Narrative Frames** (deterministic selection):
- **Straightforward** — Predictable outcomes
- **Unexpected Ally** — Help arrives
- **Hidden Cost** — Success with price
- **Moral Inversion** — Ethical complications
- **Foreshadowing** — Hints of future events
- **Layered Consequences** — Complex ripple effects

Host can switch personas
### Quick Test
```bash
# Test zero-dependency operation
python3 test_featherweight.py

# Start server
uvicorn server.main:app --host 0.0.0.0 --port 8000
```

### GitHub Codespaces
1. Open this repo in Codespaces
2. In Ports tab → Make port 8000 **Public**
3. Open forwarded URL
4. Click **Create New Session** → Share QR code
5. Everyone scans → Say your name → Adventure begins!

> 💡 **Pro tip:** Start with template mode (zero cost), upgrade to hybrid for special sessions.

## 🎭 DM Personas

| Persona             | Voice   | Style                              | Best For                     |
|---------------------|---------|------------------------------------|------------------------------|
| Classic Fantasy     | Alloy   | Warm, heroic, vivid descriptions   | Traditional D&D adventures   |
| Gothic Horror       | Echo    | Brooding, ominous, atmospheric     | Ravenloft / Call of Cthulhu  |
| Whimsical           | Fable   | Playful, punny, fairy-tale charm   | Light-hearted family games   |
| Sci-Fi Overseer     | Onyx    | Cold, clinical, technical          | Cyberpunk / space opera      |

Host can switch live — everyone hears the change instantly.

## ⏱ Turn System

- Say **"my turn"**, **"me"**, **"next"**, or **"I go"** → You're added to queue
- Only the active player's actions advance the story
- Others get gentle whisper: "(Waiting for Elise's turn…)"
- Host can manually **Pass Turn** if needed
 & Architecture

### Core Framework:
- FastAPI + WebSockets (real-time sync)
- Pydantic v2 (type-safe configuration with pydantic-settings)
- SQLite (campaign persistence)
- Pure HTML/JS frontend (PWA-ready)

### Intelligence Stack (All Deterministic):
```
[Deterministic Logic] → [Template Engine] → [Optional LLM Polish]
        ↓                     ↓                     ↓
[Ethics Engine]        [Randomness Engine]    [Narration Output]
        ↓                     ↓                     ↓
[Memory System]        [Dice System]          [Roll20 Relay]
```

**AI/Intelligence:**
- **Template Engine** (default) – 6 narrative frames, 22 tone combinations, pure Python
- **Hybrid Engine** (optional) – Template + LLM polish with graceful degradation
- **Randomness Engine** (v1.3.1) – 4 RNG modes with OS entropy, session replay
- **Dice System** (v1.3.1) – Full RPG dice with expressions, advantage/disadvantage
- **OpenAI GPT-4o-mini + TTS** (optional) – For hybrid/llm narration modes

**Intelligence Systems (Deterministic):**
- Imagination analysis (creative input scoring: 0.0-1.0)
- Anti-railroading detection (pattern warnings with visual alerts)
- Adaptive frame selection (6 narrative structures)
- Session management (isolated campaigns, auto-cleanup)
- Character tracking (momentum, creativity signals)
- Session-specific RNG (deterministic replay per campaign)

## 🪶 Narration Modes

### At the Table vs Remote Play

- **At the table**: Players roll physical dice and announce results (social trust)
- **Remote play**: Built-in dice system with session replay
- **Roll20 integration**: Chat-based AI DM companion for virtual tabletops
- **Dice modes**: SECURE (default, OS entropy), DETERMINISTIC (replay), WEIGHTED (dramatic), LINEAR (puzzles)

### Dice Command Integration

```python
# In-game dice commands (processed through system)
quick_roll("d20+5")
quick_roll("2d6+3")
quick_roll("d20 advantage")
quick_roll("d20 disadvantage")

# With session replay
dice = DiceSystem(session_id="campaign-alpha")
dice.roll("d20")  # Deterministic per campaign
```� Design Philosophy

> **"Reasoning is deterministic. Language is optional. Randomness is bounded."**

VoiceDM is built on three pillars:

1. **Deterministic Core** — Ethics, logic, and memory never rely on randomness
2. **Optional Polish** — LLMs enhance language, never control outcomes
3. **Bounded Randomness** — OS entropy for fairness, deterministic for replay

This creates a system that's:
- **Fair** (auditable dice, no hidden RNG)
- **Honest** (no illusion of intelligence)
- **Resilient** (works offline, no API dependencies)
- **Empowering** (GM always in control)

### Anti-Railroad Detection

VoiceDM monitors for repetitive outcomes and warns GMs:
```
⚠️ PATTERN DETECTED: Players tried 5 different approaches 
but got only 2 distinct outcomes. Consider offering more 
branching possibilities.
```

## 🪶 Narration Modes

| Mode     | API Key Required | Response Time | Cost/Request | Best For                           |
|----------|------------------|---------------|--------------|-------------------------------------|
| template | ❌ No           | <1ms          | $0           | Local dev, offline, high-volume     |
| hybrid   | ✅ Yes          | 50-200ms      | ~$0.0001     | Premium experience, graceful backup |
| llm      | ✅ Yes          | 100-500ms     | ~$0.001      | Full generation (v1.2.0 legacy)     |

**Default:** `template` mode (zero dependencies)  
**Configure:** Set `NARRATION_MODE=hybrid` or `llm` in `.env`  
**Learn more:** See [FEATHERWEIGHT_GUIDE.md](FEATHERWEIGHT_GUIDE.md)

## 🪑 Table Play vs 🌐 Remote Play

- **At the table**: Players roll physical dice and announce results (social trust)
- **Remote play**: Built-in dice system with session replay (`quick_roll("d20")`)
- **Roll20 integration**: Chat-based AI DM companion for virtual tabletops (see [ROLL20_GUIDE.md](ROLL20_GUIDE.md))
- **Dice modes**: SECURE (default, OS entropy), DETERMINISTIC (replay), WEIGHTED (dramatic), LINEAR (puzzles)

**Learn more:** See [RANDOMNESS_GUIDE.md](RANDOMNESS_GUIDE.md)

AI Dungeon Master adapts to all play styles without forcing rules.

## 🎲 Design Philosophy

The AI facilitates — never overrides — human ritual.

## � Build Native iOS & Android Apps

This repo is **pre-configured** for native mobile apps using **Capacitor**.

### One-Time Setup (5 minutes)
```bash
cd client
npm install
npx cap add ios
npx cap add android
```

That's it. `package.json` and `capacitor.config.ts` are already included.

### Hosting Your Backend + Frontend

**Critical:** Mobile apps need a live URL for your web app + backend.

Options:
- **Recommended:** Deploy full stack (FastAPI + static client) to **Render.com** (free tier works)
- Also good: Fly.io, Railway, Heroku
- **Note:** Vercel/Netlify host frontend only; you'd need separate backend hosting

**Important:** Your hosting provider must support **WebSockets** (FastAPI requirement).

### Build & Deploy
1. Deploy server + client to your hosting URL
2. Update `capacitor.config.ts` with your live URL
3. Sync web assets:
## 📱 Build Native iOS & Android Apps

This repo is **pre-configured** for native mobile apps using **Capacitor**.

### One-Time Setup (5 minutes)
```bash
cd client
npm install
npx cap add ios
npx cap add android
```

That's it. `package.json` and `capacitor.config.ts` are already included.

### Hosting Your Backend + Frontend

**Critical:** Mobile apps need a live URL for your web app + backend.

Options:
- **Recommended:** Deploy full stack (FastAPI + static client) to **Render.com** (free tier works)
- Also good: Fly.io, Railway, Heroku
- **Note:** Vercel/Netlify host frontend only; you'd need separate backend hosting

**Important:** Your hosting provider must support **WebSockets** (FastAPI requirement).

### Build & Deploy
1. Deploy server + client to your hosting URL
2. Update `capacitor.config.ts` with your live URL
3. Sync web assets:
   ```bash
   npx cap sync
   ```
4. Open in Xcode/Android Studio:
   ```bash
   npx cap open ios      # Build & run on iPhone/simulator
   npx cap open android  # Build & run on device/emulator
   ```

### Publish to Stores
- **iOS:** Apple Developer ($99/yr) → App Store Connect
- **Android:** Google Play Console ($25 one-time) → Upload .aab

### Fork & Publish Your Own Version
Change `appId` in `capacitor.config.ts`, add your icon/splash, submit—your branded app published!

See [MOBILE_GUIDE.md](MOBILE_GUIDE.md) for step-by-step details.

## 🤝 Contributing

We welcome contributions, especially:
- New **template variations** for existing personas
- Additional **dice system features** (custom dice, new systems)
- **Anti-railroad improvements** and detection algorithms
- **Documentation** and usage examples
- More DM personas and voices
- Character sheet integration
- Ambient sound effects

## 🎲 Acknowledgments

Built with ❤️ for storytellers who believe that:
- **Dice should be fair**
- **Stories should be honest**  
- **Tools should be transparent**
- **GMs should be empowered**

---

**VoiceDM v1.3.1** — *Deterministic logic, true randomness, zero vendor lock-in.*

## ⭐ Star this repo if you love tabletop RPGs

Let's bring the magic of D&D to every phone and table.