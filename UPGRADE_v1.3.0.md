# ⬆️ Upgrade Guide: v1.2.0 → v1.3.0

Quick reference for upgrading to Featherweight Hybrid AI architecture.

## 📋 TL;DR

- ✅ **Fully backward compatible** – No breaking changes
- ✅ **Zero-config option** – Works without API keys now
- ✅ **All intelligence preserved** – Imagination, railroading, frames still work
- ⚠️ **Behavior change:** Defaults to template mode (not LLM)

## 🚀 Upgrade Steps

### For Existing v1.2.0 Deployments

#### Option A: Keep Exact v1.2.0 Behavior
```bash
# Update code
git pull origin main

# Add to .env (or keep existing)
NARRATION_MODE=llm
OPENAI_API_KEY=sk-...

# Restart server
# No behavior change - works exactly like v1.2.0
```

#### Option B: Try Featherweight (Recommended)
```bash
# Update code
git pull origin main

# Remove or comment out in .env
# OPENAI_API_KEY=...

# Add (or let it default)
NARRATION_MODE=template

# Restart server
# Zero dependencies, instant responses, zero cost
```

#### Option C: Hybrid Mode (Best of Both)
```bash
# Update code
git pull origin main

# Add to .env
NARRATION_MODE=hybrid
OPENAI_API_KEY=sk-...

# Restart server
# Templates + LLM polish, graceful fallback
```

## 🧪 Testing

### Verify Zero-Dependency Operation
```bash
# Run comprehensive test suite
python3 test_featherweight.py

# Should see:
# ✅ ALL FEATHERWEIGHT TESTS PASSED
# Dependencies Required: 0
# Response Time: <1ms
```

### Verify Your Deployment
```bash
# Start server
uvicorn server.main:app --host 0.0.0.0 --port 8000

# Check health endpoint
curl http://localhost:8000/health

# Should show:
# {
#   "status": "healthy",
#   "version": "1.3.0",
#   "narration_mode": "template",  # or "hybrid"/"llm"
#   "narration_stats": {
#     "frames": 6,
#     "tones": 22,
#     "variations": 256,
#     "required_dependencies": 0
#   }
# }
```

## 📝 Configuration Changes

### New Environment Variables

```bash
# .env file

# NEW: Narration mode (template/hybrid/llm)
NARRATION_MODE=template

# CHANGED: Now optional (only needed for hybrid/llm modes)
OPENAI_API_KEY=sk-...

# Unchanged from v1.2.0
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SESSION_TIMEOUT=3600
```

### Default Behavior (No .env)

| Setting         | v1.2.0        | v1.3.0        |
|-----------------|---------------|---------------|
| Narration Mode  | (LLM always)  | `template`    |
| API Key         | Required      | Optional      |
| Dependencies    | 1 (OpenAI)    | 0             |
| Startup         | Fails if no key | Always works |

## 🔄 What Changed

### New Files
- ✅ `server/template_engine.py` - Pure template narration
- ✅ `server/hybrid_engine.py` - Mode orchestration
- ✅ `test_featherweight.py` - Comprehensive testing
- ✅ `FEATHERWEIGHT_GUIDE.md` - Architecture docs
- ✅ `V1.3.0_SUMMARY.md` - Release summary
- ✅ This file - Upgrade guide

### Modified Files
- ✅ `server/config.py` - Added `NarrationMode` enum
- ✅ `server/llm.py` - Lazy client initialization
- ✅ `server/dm_engine.py` - Uses hybrid_engine
- ✅ `server/main.py` - Health check shows narration stats
- ✅ `.env.example` - Shows new NARRATION_MODE variable
- ✅ `README.md` - Updated feature list

### Unchanged (100% Compatible)
- ✅ All v1.2.0 intelligence systems (imagination, railroading, frames)
- ✅ Session management and cleanup
- ✅ Character tracking
- ✅ Input validation
- ✅ Roll20 integration
- ✅ Database schema
- ✅ API endpoints
- ✅ WebSocket protocol

## 🎯 Migration Scenarios

### Scenario 1: Development / Testing
**Recommendation:** Template mode

```bash
NARRATION_MODE=template
# No API key needed
```

**Benefits:**
- Zero cost during development
- Instant responses for rapid iteration
- Works offline
- Deterministic output for testing

### Scenario 2: Production (Low Cost)
**Recommendation:** Template mode with optional hybrid for special events

```bash
# Default config
NARRATION_MODE=template

# Special events: temporarily switch to hybrid
# NARRATION_MODE=hybrid
# OPENAI_API_KEY=sk-...
```

**Benefits:**
- Free baseline operation
- Scales infinitely
- Pay only for premium moments

### Scenario 3: Production (Premium)
**Recommendation:** Hybrid mode

```bash
NARRATION_MODE=hybrid
OPENAI_API_KEY=sk-...
```

**Benefits:**
- Best narrative quality
- Graceful fallback if API fails
- Still deterministic reasoning
- Cost: ~$0.0001/request (10x cheaper than full LLM)

### Scenario 4: Legacy (Keep v1.2.0)
**Recommendation:** LLM mode

```bash
NARRATION_MODE=llm
OPENAI_API_KEY=sk-...
```

**Benefits:**
- Exact v1.2.0 behavior
- No surprises
- Full LLM generation

## ⚠️ Important Notes

### API Key Handling
**v1.2.0:**
```python
# Server crashed if no OPENAI_API_KEY
client = OpenAI(api_key=settings.openai_api_key)  # Immediate error
```

**v1.3.0:**
```python
# Server starts successfully without API key
_client = None  # Lazy initialization

def get_client():
    global _client
    if _client is None:
        if settings.openai_api_key:
            _client = OpenAI(api_key=settings.openai_api_key)
        else:
            raise ValueError("OpenAI API key required for this mode")
    return _client
```

### Mode Selection Logic
```python
# In hybrid_engine.py
async def generate_narrative(...):
    # Always generate template first (fast, free, reliable)
    template = render_template(...)
    
    # Optionally enhance with LLM
    if settings.narration_mode == NarrationMode.HYBRID:
        enhanced = await _try_llm_polish(template)
        return enhanced if enhanced else template  # Graceful fallback
    
    elif settings.narration_mode == NarrationMode.LLM:
        # Full generation (v1.2.0 style)
        return await generate_text(...)
    
    else:  # TEMPLATE mode (default)
        return template
```

## 📊 Performance Comparison

### Template Mode (v1.3.0 Default)
- Response time: **<1ms**
- Cost per request: **$0**
- Dependencies: **0**
- Offline capable: **Yes**
- Output variety: **256+ variations**

### Hybrid Mode (v1.3.0 New)
- Response time: **50-200ms**
- Cost per request: **~$0.0001**
- Dependencies: **1 (optional)**
- Offline capable: **Gracefully degrades**
- Output variety: **Infinite (LLM-polished)**

### LLM Mode (v1.2.0 Legacy)
- Response time: **100-500ms**
- Cost per request: **~$0.001**
- Dependencies: **1 (required)**
- Offline capable: **No**
- Output variety: **Infinite**

## 🧰 Troubleshooting

### Issue: Server won't start
**v1.3.0:** Should never happen (template mode has zero dependencies)

**Check:**
```bash
# Verify narration mode
grep NARRATION_MODE .env

# If set to 'llm' or 'hybrid', verify API key
grep OPENAI_API_KEY .env

# If missing, either add key or switch to template mode
echo "NARRATION_MODE=template" >> .env
```

### Issue: Narration seems repetitive
**Solution:** You're in template mode (only 256+ variations)

**Options:**
1. Increase template variety (add custom tones/frames)
2. Switch to hybrid mode (LLM polish)
3. Accept deterministic narration (still sophisticated)

**Add custom tone:**
```python
# In server/template_engine.py
TONE_VARIANTS = {
    "cyberpunk": {  # Your new tone
        "atmosphere": ["neon-lit", "chrome", "synthetic"],
        "actions": ["jacks in", "uploads", "glitches"],
        # ...
    }
}
```

### Issue: Want more control over templates
**Solution:** Templates are fully customizable

**See:** [FEATHERWEIGHT_GUIDE.md](FEATHERWEIGHT_GUIDE.md) - Extension Guide section

## ✅ Validation Checklist

After upgrading, verify:

- [ ] Server starts without errors
- [ ] Health endpoint shows version "1.3.0"
- [ ] Health endpoint shows correct narration_mode
- [ ] Test event generates narrative
- [ ] Session management works (create/access session)
- [ ] Intelligence systems working (imagination, railroading)
- [ ] Frame selection adapting to actions
- [ ] (If hybrid/llm) LLM generation working
- [ ] (If template) Zero-dependency operation confirmed

```bash
# Quick validation
curl http://localhost:8000/health | jq .

# Expected output:
# {
#   "status": "healthy",
#   "version": "1.3.0",
#   "narration_mode": "template",  # or your chosen mode
#   "active_sessions": 0
# }
```

## 📚 Further Reading

- **Architecture Overview:** [FEATHERWEIGHT_GUIDE.md](FEATHERWEIGHT_GUIDE.md)
- **Release Summary:** [V1.3.0_SUMMARY.md](V1.3.0_SUMMARY.md)
- **v1.2.0 Features:** [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Testing:** Run `python3 test_featherweight.py`

## 🎉 Summary

v1.3.0 "Featherweight" is a **non-breaking enhancement** that:

1. Makes OpenAI API key **optional** instead of required
2. Adds **template mode** (zero dependencies, instant, free)
3. Adds **hybrid mode** (templates + LLM polish, graceful fallback)
4. Preserves **llm mode** (exact v1.2.0 behavior)
5. Keeps **all intelligence deterministic** (imagination, railroading, frames)

**No action required** if you want to keep v1.2.0 behavior - just set `NARRATION_MODE=llm`.

**Recommended:** Try template mode first (zero cost), upgrade to hybrid for special occasions.

---

**Questions?** See [FEATHERWEIGHT_GUIDE.md](FEATHERWEIGHT_GUIDE.md) or raise an issue.
