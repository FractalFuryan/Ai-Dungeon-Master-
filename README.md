# ⚔️ AI Dungeon Master

**A voice-driven, multiplayer tabletop RPG companion**  
Join via QR code · Speak your actions · Hear a voiced DM with personality · Take natural turns

No apps. No accounts. No Discord. Just phones and imagination.

## ✨ Features

- **QR Code Join** – Host creates session → QR appears → Everyone scans → Instant multiplayer
- **Voice In / Voice Out** – Push-to-talk → AI Dungeon Master responds with immersive narration
- **4 Switchable DM Personas** – Classic Fantasy · Gothic Horror · Whimsical · Sci-Fi (each with unique voice + style)
- **Natural Turn System** – Say "my turn" or "next" → Get in queue → Only active player drives the story
- **Persistent Campaigns** – Save and load your ongoing adventure
- **Phone & Tablet First** – Works beautifully on mobile browsers
- **Zero Setup** – Runs in GitHub Codespaces with one click

## 🚀 Quick Start (60 seconds)

1. Open this repo in **GitHub Codespaces** (or run locally)
2. In terminal:
   ```bash
   pip install -r requirements.txt
   uvicorn server.main:app --host 0.0.0.0 --port 8000
   ```
3. In Ports tab → Make port 8000 **Public**
4. Open the forwarded URL
5. Click **Create New Session** → Share the QR code
6. Everyone scans → Say your name → Adventure begins!

> Pro tip: Use a phone for players, laptop/tablet for host (to switch personas & save).

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

- FastAPI + WebSockets (real-time sync)
- OpenAI GPT-4o-mini + TTS (DM brain & voice)
- SQLite (campaign persistence)
- Pure HTML/JS frontend (PWA-ready)

## 🪑 Table Play vs 🌐 Remote Play

- **At the table**: Players roll physical dice and announce results (social trust)
- **Remote play**: Optional system dice mode (coming soon)

AI Dungeon Master adapts to both styles without forcing rules.

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

## 🤝 Contributing

Pull requests welcome! Especially:
- More DM personas
- Optional server dice mode
- Ambient sound effects
- Character sheet integration

## ⭐ Star this repo if you love tabletop RPGs

Let's bring the magic of D&D to every phone.

Made with ❤️ for storytellers everywhere.