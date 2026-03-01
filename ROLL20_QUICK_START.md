# 🚀 Roll20 Quick Start (5 Minutes)

Get AI narration in your Roll20 game in 5 minutes.

## What You Need

- Roll20 **Pro subscription** (for API scripts)
- A deployed backend (instructions below)
- Modern browser (Chrome, Firefox, Safari, Edge)

---

## Step 1: Deploy Backend (2 minutes)

### Option A: Render.com (Recommended - Free Tier)

1. Go to [render.com](https://render.com) and sign up
2. Click **New** → **Web Service**
3. Connect your GitHub repo: `FractalFuryan/Ai-Dungeon-Master-`
4. Configure:
   - **Name:** `ai-dungeon-master`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn server.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable:
   - **Key:** `OPENAI_API_KEY`
   - **Value:** Your OpenAI API key
6. Click **Create Web Service**
7. Wait 2-3 minutes for deployment
8. **Copy your deployed URL** (e.g., `https://ai-dungeon-master-xyz.onrender.com`)

### Option B: Other Platforms

- **Fly.io:** `fly launch` → Follow prompts
- **Railway:** Connect repo → Deploy
- **Heroku:** `git push heroku main`

All support Python + WebSockets.

---

## Step 2: Install Roll20 API Script (1 minute)

1. Open your Roll20 game as **GM**
2. Go to **Settings** → **API Scripts**
3. Click **New Script**
4. Name it: `AI DM`
5. Copy **all of** [`roll20/aidm-roll20.js`](../roll20/aidm-roll20.js)
6. Paste into script editor
7. Click **Save Script**

You should see: `AI Dungeon Master API script loaded successfully.`

---

## Step 3: Open Relay Page (30 seconds)

1. Open [`relay/roll20-relay.html`](../relay/roll20-relay.html) in a browser tab
   - You can open it directly from your local files
   - Or host it on GitHub Pages / Netlify for easier access
2. Update **Backend URL** field with your deployed URL from Step 1
3. Keep this tab open during your game

**Bookmark it** for future sessions.

---

## Step 4: Test It (1 minute)

In Roll20 chat:

```
!aidm help
```

You should get a whispered command reference.

Now try:

```
!aidm The heroes gather in a torch-lit tavern
```

As GM:

```
!aidm_dump
```

Copy the whispered `AIDM_QUEUE:...` → Paste into relay page → Click **Process Queue**

You'll get back rich narration. Copy it and paste into Roll20 chat.

**It works!** 🎉

---

## Usage Flow (During Play)

1. Players type `!aidm` commands
2. Commands queue up automatically
3. When ready, GM types `!aidm_dump`
4. Copy JSON → Paste into relay page → Click Process
5. Copy narration → Paste into Roll20 chat

**Tip:** Process every 2-3 commands for natural flow.

---

## Common Player Commands

```
!aidm I search the room for traps
!aidm I attempt to persuade the guard
!aidm persona gothic          (switches DM mood)
!aidm roll stealth            (select your token first)
!aidm myturn                  (join turn queue)
```

---

## Troubleshooting

### "Queue is empty"
- Try `!aidm help` to test if script is running
- Check Settings → API Scripts is showing the script as active

### "Backend URL not configured"
- Update the relay page with your deployed URL
- Include `https://` and no trailing slash

### "Only the GM can dump"
- `!aidm_dump` is GM-only for security
- Regular players use `!aidm` for actions

---

## Next Steps

- Read [ROLL20_GUIDE.md](../ROLL20_GUIDE.md) for full documentation
- Check [roll20/macros.example](../roll20/macros.example) for Roll20 macros
- Try different personas: `!aidm persona whimsical`

---

## Need Help?

- [GitHub Issues](https://github.com/FractalFuryan/Ai-Dungeon-Master-/issues)
- [GitHub Discussions](https://github.com/FractalFuryan/Ai-Dungeon-Master-/discussions)

---

**Ready to narrate!** ⚔️🎲

Your Roll20 game just got a professional AI Dungeon Master.
