# Running in GitHub Codespaces

## Quick Start (4 steps)

### 1. Set your OpenAI API key
```bash
echo "OPENAI_API_KEY=your_actual_key" > .env
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the backend (Terminal 1)
```bash
uvicorn server.main:app --host 0.0.0.0 --port 8000
```

Go to **Ports tab** → right-click port **8000** → **Make Public**

### 4. Start the frontend (Terminal 2)
```bash
cd client && python -m http.server 3000
```

Go to **Ports tab** → right-click port **3000** → **Make Public** → **Open in Browser**

---

## What's Fixed for Codespaces

✅ **API URL** - Dynamically detects forwarded URL (no hardcoded localhost)  
✅ **WebSocket** - Auto-upgrades to WSS when HTTPS  
✅ **CORS** - Backend allows all origins (safe for dev)  
✅ **QR Auto-join** - Scan QR → automatically join session  
✅ **Port forwarding** - Both ports correctly configured  

---

## Testing Flow

1. **Create Session**
   - Click "Create Session" button
   - QR code appears (this is your session)

2. **Join Session (same browser)**
   - Open QR in new tab
   - Auto-joins as Player1

3. **Join Session (phone)**
   - Get port 3000 URL from Ports tab
   - Scan QR with phone camera
   - Opens in browser → auto-joins

4. **Voice Test**
   - Click "Push to Talk"
   - Say something (e.g., "I attack the goblin")
   - Get narration + TTS response

---

## Debugging

**WebSocket fails?**
- Check port 8000 is **Public**
- Check backend is running (`uvicorn` still in Terminal 1)

**Mic permission denied?**
- Codespaces requires HTTPS for mic
- Ensure you're using the forwarded **HTTPS URL** (port 3000)

**QR won't scan?**
- Use QR scanner app (camera app on iPhone)
- Or manually copy session ID

---

## Next: Add Features

See DEV_NOTES.md for:
- DM Personas
- Turn manager
- Campaign persistence
- Voice changer
