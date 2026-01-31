# ⚔️ AI Dungeon Master

**A voice-driven, multiplayer tabletop RPG companion**  
Join via QR code · Speak your actions · Hear a voiced DM with personality · Take natural turns

No apps. No accounts. No Discord. Just phones and imagination.

> **NEW in v1.3.0:** 🪶 **Featherweight Hybrid AI** – Works with ZERO dependencies by default! Optional LLM enhancement for premium narration. See [FEATHERWEIGHT_GUIDE.md](FEATHERWEIGHT_GUIDE.md).

> **Roll20 Integration** available! See [ROLL20_GUIDE.md](ROLL20_GUIDE.md) for chat-based AI DM companion mode.

## ✨ Features

### Core Experience
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

### Featherweight Architecture (v1.3.0+)
- **Zero Dependencies by Default** – Works offline with pure template narration
- **3 Narration Modes:**
  - `template` (default) – 256+ variations, <1ms response, $0 cost
  - `hybrid` – Templates + optional LLM polish with graceful fallback
  - `llm` (legacy) – Full generation (v1.2.0 behavior)
- **No Platform Lock-In** – Swap language models without changing code
- **Deterministic & Auditable** – All reasoning in code, not black-box ML

### Integrations
- **Roll20 Integration** – Chat-based AI DM companion for virtual tabletops
- **Zero Setup** – Runs in GitHub Codespaces with one click

## 🚀 Quick Start (60 seconds)

### Option 1: Zero Dependencies (Recommended)
```bash
# Clone and run
git clone https://github.com/yourusername/Ai-Dungeon-Master-.git
cd Ai-Dungeon-Master-
pip install -r requirements.txt
uvicorn server.main:app --host 0.0.0.0 --port 8000
```
✅ **Works immediately** – No API keys required  
✅ **Template narration** – 256+ variations, <1ms response  
✅ **All intelligence active** – Imagination analysis, anti-railroading, adaptive frames

### Option 2: With LLM Enhancement
```bash
# Add to .env file
NARRATION_MODE=hybrid  # or 'llm' for v1.2.0 behavior
OPENAI_API_KEY=sk-...
```
✅ **Templates + LLM polish** – Best of both worlds  
✅ **Graceful fallback** – Works offline if API unavailable  
✅ **Cost effective** – Templates for common actions, LLM for special moments

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

Keeps large groups orderly without feeling restrictive.

## 📜 Persistent Campaigns

- Host clicks **Save Campaign** → Name it → Stored locally in SQLite until you delete it
- Next session → **Load Campaign** → New QR with all progress restored

Perfect for weekly games.

## 🛠 Tech Stack

**Core Framework:**
- FastAPI + WebSockets (real-time sync)
- Pydantic v2 (type-safe configuration)
- SQLite (campaign persistence)
- Pure HTML/JS frontend (PWA-ready)

**AI/Intelligence:**
- **Template Engine** (default) – 6 narrative frames, 22 tone combinations, pure Python
- **Hybrid Engine** (optional) – Template + LLM polish with graceful degradation
- **OpenAI GPT-4o-mini + TTS** (optional) – For hybrid/llm narration modes

**Intelligence Systems (Deterministic):**
- Imagination analysis (creative input scoring)
- Anti-railroading detection (pattern warnings)
- Adaptive frame selection (6 narrative structures)
- Session management (isolated campaigns, auto-cleanup)
- Character tracking (momentum, creativity signals)

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
- **Remote play**: Optional system dice mode (coming soon)
- **Roll20 integration**: Chat-based AI DM companion for virtual tabletops (see [ROLL20_GUIDE.md](ROLL20_GUIDE.md))

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

## �🚀 Run Locally or in Codespaces

```bash
git clone https://github.com/yourusername/Ai-Dungeon-Master.git
cd Ai-Dungeon-Master
pip install -r requirements.txt
uvicorn server.main:app --host 0.0.0.0 --port 8000
```

Open in browser → Play!

## 📚 Documentation

- [QUICK_START.md](QUICK_START.md) – Get playing in 60 seconds
- [TURN_SYSTEM_GUIDE.md](TURN_SYSTEM_GUIDE.md) – How turns work
- [PERSONA_GUIDE.md](PERSONA_GUIDE.md) – The 4 DM voices explained
- [PERSISTENCE_GUIDE.md](PERSISTENCE_GUIDE.md) – Save/load campaigns
- [ROLL20_GUIDE.md](ROLL20_GUIDE.md) – **NEW:** Virtual tabletop integration
- [MOBILE_GUIDE.md](MOBILE_GUIDE.md) – Build native iOS/Android apps

## 🤝 Contributing

Pull requests welcome! Especially:
- More DM personas
- Optional server dice mode
- Ambient sound effects
- Character sheet integration

## ⭐ Star this repo if you love tabletop RPGs

Let's bring the magic of D&D to every phone.

Made with ❤️ for storytellers everywhere.