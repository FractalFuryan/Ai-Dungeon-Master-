# 🚀 Deployment Guide — Production Ready

## Quick Deploy Options

### Option 1: Render.com (Recommended - Free Tier)

**Time: 5 minutes**

1. **Sign up:** https://render.com
2. **New Web Service** → Connect GitHub repo
3. **Configure:**
   ```
   Name: ai-dungeon-master
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn server.main:app --host 0.0.0.0 --port $PORT
   ```
4. **Environment Variables:**
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
5. **Deploy** → Wait 2-3 minutes
6. **Copy URL:** e.g., `https://ai-dungeon-master-xyz.onrender.com`

**Test:**
```bash
curl https://your-app.onrender.com/session/create
# Should return: {"session_id": "..."}
```

---

### Option 2: Fly.io (Also Free Tier)

**Time: 5 minutes**

1. **Install CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login:**
   ```bash
   fly auth login
   ```

3. **Launch:**
   ```bash
   fly launch
   # Follow prompts, select region
   ```

4. **Set secrets:**
   ```bash
   fly secrets set OPENAI_API_KEY=your_key_here
   ```

5. **Deploy:**
   ```bash
   fly deploy
   ```

**Get URL:**
```bash
fly status
# Copy URL from output
```

---

### Option 3: Railway (Simple)

1. **Sign up:** https://railway.app
2. **New Project** → Deploy from GitHub repo
3. **Add variables:**
   - `OPENAI_API_KEY`
4. **Deploy** → Auto-deployed

**URL:** Railway provides it automatically

---

## Post-Deployment

### 1. Update Client (If Hosting Frontend Separately)

Edit `client/app.js`:
```javascript
const API_BASE = 'https://your-deployed-backend.com';
```

### 2. Enable CORS (Already configured in main.py)

✅ Already set to allow all origins for Codespaces
- For production, consider restricting to your domain

### 3. Test All Endpoints

```bash
BACKEND_URL="https://your-app.onrender.com"

# Create session
curl -X POST $BACKEND_URL/session/create

# Health check (Roll20)
curl $BACKEND_URL/roll20/health
# Should return: {"status":"ok","integration":"roll20","version":"1.0.0"}

# Test narration (requires session)
curl -X POST $BACKEND_URL/session/narrate \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","text":"The adventurers enter the tavern"}'
```

---

## Mobile App Deployment

### iOS (requires macOS + Xcode)

```bash
cd client
npm install
npx cap add ios
```

**Update `capacitor.config.ts`:**
```typescript
const config: CapacitorConfig = {
  appId: 'com.yourname.aidm',
  appName: 'AI Dungeon Master',
  webDir: '.',
  server: {
    url: 'https://your-deployed-backend.com',
    cleartext: true
  }
};
```

**Build:**
```bash
npx cap sync
npx cap open ios
# Xcode opens → Build & run
```

**For App Store:**
1. Update `appId` in capacitor.config.ts
2. Add icons/splash (use `cordova-res`)
3. Xcode → Product → Archive
4. Upload to App Store Connect
5. Submit for review

**Cost:** $99/year (Apple Developer)

---

### Android

```bash
cd client
npm install
npx cap add android
```

**Update `capacitor.config.ts`:** (same as iOS above)

**Build:**
```bash
npx cap sync
npx cap open android
# Android Studio opens → Build APK
```

**For Google Play:**
1. Build → Generate Signed Bundle (AAB)
2. Upload to Google Play Console
3. Submit for review

**Cost:** $25 one-time (Google Play)

---

## Roll20 Deployment

**Already integrated! Just need to:**

1. **Deploy backend** (see above)
2. **Update relay page:**
   - Open `relay/roll20-relay.html`
   - Change backend URL input default to your deployed URL
3. **Install in Roll20:**
   - Copy `roll20/aidm-roll20.js` to Roll20 API Scripts
   - Open relay page in browser
   - Use `!aidm` commands

**See:** [ROLL20_GUIDE.md](ROLL20_GUIDE.md) for full setup

---

## Environment Variables

Required:
```
OPENAI_API_KEY=sk-...
```

Optional:
```
PORT=8000                    # Auto-set by most platforms
DATABASE_PATH=./campaigns.db  # SQLite location
LOG_LEVEL=info               # debug|info|warning|error
```

---

## Monitoring & Logs

### Render.com
- Dashboard → Logs (real-time)
- Metrics → CPU/Memory usage

### Fly.io
```bash
fly logs
fly status
```

### Railway
- Dashboard → Deployments → View Logs

---

## Scaling (If You Get Popular)

### Free Tier Limits
- **Render:** 750 hours/month (always-on if only app)
- **Fly.io:** 3 VMs free (256MB RAM each)
- **Railway:** $5 free credit/month

### Upgrade When:
- >1000 concurrent sessions
- Response times >2s
- Memory >512MB consistently

**Render Pro:** $7/month  
**Fly Scale:** Pay-as-you-go  
**Railway Pro:** $5-20/month

---

## Troubleshooting

### WebSocket Issues
- Ensure platform supports WebSockets (all above do)
- Check CORS settings
- Verify `wss://` protocol in production

### Voice Not Working
- Check HTTPS (required for microphone access)
- Verify OpenAI API key is set
- Test TTS endpoint separately

### Database Errors
- Ensure writable volume (Render/Fly auto-configure)
- Check SQLite permissions

---

## Security Checklist

- [x] HTTPS enabled (auto on all platforms)
- [x] CORS configured
- [ ] API key in environment (not code)
- [ ] Rate limiting (add if needed)
- [ ] Input validation (already in roll20_adapter.py)

---

## Next Steps After Deployment

1. ✅ Test web mode (create session, share QR)
2. ✅ Test Roll20 mode (if using)
3. ✅ Update README with deployed URL
4. ✅ Announce release!

**Your backend is now live at:**
```
https://your-app.onrender.com
```

**Ready to DM.** ⚔️🎲
