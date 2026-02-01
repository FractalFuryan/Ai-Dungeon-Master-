# 📱 VoiceDM Rule Scanner Guide

**QR-Based Rule Loading for Tabletop RPGs**

## Overview

The Rule Scanner enables loading pre-indexed RPG rulesets via QR codes or manual input. Rules integrate seamlessly with VoiceDM's existing dice and randomness systems.

## Quick Start

1. **Start VoiceDM server**:
   ```bash
   python -m uvicorn server.main:app --host 0.0.0.0 --port 8000
   ```

2. **Open scanner interface**:
   - Desktop: http://localhost:8000/scanner
   - Mobile: http://<your-ip>:8000/scanner

3. **Load a ruleset**:
   - Click "Load D&D 5e Basic" for instant demo
   - OR scan a QR code with your camera
   - OR manually enter QR data

4. **Use in VoiceDM**:
   - Click "Use This Ruleset in VoiceDM"
   - Rules integrate with dice rolls and narration

## Features

### 🎯 Supported QR Formats

The scanner accepts multiple QR code formats:

1. **VoiceDM URI Scheme**:
   ```
   voicedm://rules/dnd5e/basic
   voicedm://rules/pathfinder/core
   ```

2. **JSON Object**:
   ```json
   {"ruleset": "dnd5e", "version": "basic"}
   ```

3. **Direct Filename**:
   ```
   dnd5e_basic.json
   pathfinder_core.json
   ```

4. **Simple Name**:
   ```
   dnd5e_basic
   call_of_cthulhu
   ```

### 📚 Pre-Loaded Rulesets

#### D&D 5e Basic (`dnd5e_basic`)

**Combat Rules** (5):
- Attack Roll: `d20 + ability_modifier + proficiency_bonus`
- Damage Roll: `weapon_damage + ability_modifier`
- Armor Class: Hit requires `attack_total >= target_ac`
- Critical Hit: Natural 20 = double damage dice
- Critical Miss: Natural 1 = automatic miss

**Skill Rules** (5):
- Ability Check: `d20 + ability_modifier`
- Skill Check: `d20 + ability_modifier + proficiency_bonus`
- Saving Throw: `d20 + ability_modifier + proficiency_bonus`
- Advantage: Roll 2d20, take highest
- Disadvantage: Roll 2d20, take lowest

**Spell Rules** (4):
- Spell Attack: `d20 + spellcasting_modifier + proficiency_bonus`
- Spell Save DC: `8 + proficiency_bonus + spellcasting_modifier`
- Spell Damage: `spell_damage_dice` (+ modifier if specified)
- Concentration: Constitution save vs `max(10, damage/2)`

**Quick Reference Tables**:
- Ability scores mapping (STR, DEX, CON, INT, WIS, CHA)
- Common DC values (5 = very easy, 30 = nearly impossible)
- Proficiency bonus by level (1-4: +2, 5-8: +3, etc.)

## API Reference

### GET `/api/scanner/rulesets`

List all available rulesets.

**Request**:
```bash
curl http://localhost:8000/api/scanner/rulesets
```

**Response**:
```json
{
  "dnd5e": ["basic"],
  "pathfinder": ["core"],
  "call_of_cthulhu": ["7e"]
}
```

### POST `/api/scanner/load`

Load a ruleset from QR data.

**Request**:
```bash
curl -X POST http://localhost:8000/api/scanner/load \
  -H "Content-Type: application/json" \
  -d '{"qr_data": "dnd5e_basic"}'
```

**Response**:
```json
{
  "name": "D&D 5e Basic Rules",
  "version": "1.0",
  "description": "Core combat and skill rules for D&D 5th Edition",
  "source": "D&D 5e SRD",
  "rules": {
    "combat": [...],
    "skills": [...],
    "spells": [...]
  },
  "quick_reference": {...}
}
```

**Error Responses**:
- `400`: No QR data provided
- `404`: Ruleset not found
- `500`: Internal error (invalid JSON, file read error)

### GET `/scanner`

Serve the scanner HTML interface.

**Request**:
```bash
curl http://localhost:8000/scanner
```

**Response**: HTML page with camera interface

## Architecture

### File Structure

```
server/
├── scanner.py           # QR code parser and ruleset loader
└── rulesets/            # JSON ruleset storage
    ├── dnd5e_basic.json
    ├── pathfinder_core.json
    └── custom_system.json

scanner.html             # Standalone camera interface
```

### RuleScanner Class

**Location**: `server/scanner.py`

**Key Methods**:
- `load_ruleset(qr_data: str) -> dict | None` - Main entry point
- `get_available_rulesets() -> dict` - List available rulesets
- Private methods for file loading and caching

**Features**:
- Singleton pattern for global access
- In-memory caching of loaded rulesets
- Multiple QR format parsing strategies
- Graceful error handling

**Usage**:
```python
from server.scanner import scan_qr_code, get_rulesets

# Load ruleset
ruleset = scan_qr_code("dnd5e_basic")
print(ruleset["name"])  # "D&D 5e Basic Rules"

# List available
rulesets = get_rulesets()
print(rulesets)  # {"dnd5e": ["basic"]}
```

## Creating Custom Rulesets

### Ruleset JSON Schema

```json
{
  "name": "System Name",
  "version": "1.0",
  "description": "Brief description",
  "source": "Official source reference",
  "rules": {
    "category_name": [
      {
        "name": "Rule Name",
        "description": "How the rule works",
        "formula": "dice_expression (optional)",
        "example": "1d20+5 (optional)",
        "condition": "when_to_apply (optional)",
        "effect": "what_happens (optional)",
        "tags": ["tag1", "tag2"]
      }
    ]
  },
  "quick_reference": {
    "table_name": {
      "key": "value"
    }
  }
}
```

### Example: Custom System

**File**: `server/rulesets/cyberpunk_red.json`

```json
{
  "name": "Cyberpunk RED",
  "version": "1.0",
  "description": "Core mechanics for Cyberpunk RED",
  "source": "Cyberpunk RED Core Rulebook",
  "rules": {
    "combat": [
      {
        "name": "Attack Roll",
        "description": "Roll 1d10 + Skill + REF, compare to DV",
        "formula": "d10 + skill + ref",
        "tags": ["attack", "combat"]
      },
      {
        "name": "Critical Injury",
        "description": "When damage exceeds HP, roll on Critical Injury Table",
        "condition": "damage > current_hp",
        "effect": "roll_d10_critical_table",
        "tags": ["critical", "injury"]
      }
    ],
    "netrunning": [
      {
        "name": "Interface",
        "description": "Roll Interface + INT against Program Strength",
        "formula": "d10 + interface + int",
        "tags": ["netrunning", "hacking"]
      }
    ]
  },
  "quick_reference": {
    "difficulty_values": {
      "everyday": 9,
      "professional": 13,
      "heroic": 17,
      "incredible": 21,
      "legendary": 24,
      "impossible": 29
    }
  }
}
```

### Installation

1. **Create JSON file** in `server/rulesets/`
2. **Name it**: `<system>_<version>.json`
3. **Generate QR code** (optional):
   ```python
   import qrcode
   qr = qrcode.QRCode()
   qr.add_data("voicedm://rules/cyberpunk/red")
   qr.make()
   qr.make_image().save("cyberpunk_red_qr.png")
   ```
4. **Test loading**:
   ```bash
   curl -X POST http://localhost:8000/api/scanner/load \
     -H "Content-Type: application/json" \
     -d '{"qr_data": "cyberpunk_red"}'
   ```

## Integration with VoiceDM

### Dice System Integration

Rules loaded via scanner automatically work with VoiceDM's dice engine:

```python
from server.dice import quick_roll

# Load D&D 5e rules
ruleset = scan_qr_code("dnd5e_basic")

# Use formula from rules
attack_rule = ruleset["rules"]["combat"][0]
formula = attack_rule["formula"]  # "d20 + ability_modifier + proficiency_bonus"

# Roll using VoiceDM dice
result = quick_roll("d20+5")  # Applies loaded rules context
```

### Randomness Mode Selection

Scanner integrates with the 4 randomness modes:

- **SECURE**: Tournament/live play (default)
- **DETERMINISTIC**: Session replay with same seed
- **WEIGHTED**: Narrative shaping (rare event bias)
- **LINEAR**: Educational/puzzle games

```python
from server.randomness import set_mode, RandomnessMode

# Tournament mode for fair play
set_mode(RandomnessMode.SECURE)

# Replay mode for auditing
set_mode(RandomnessMode.DETERMINISTIC, seed="campaign-01")
```

## Mobile Usage

### Camera Access

The scanner uses HTML5 `getUserMedia()` API for camera access:

1. **Browser compatibility**: Chrome, Safari, Firefox (mobile + desktop)
2. **HTTPS requirement**: Camera requires secure context (localhost = OK)
3. **Permissions**: Browser asks for camera permission on first use
4. **Fallback**: Manual input field if camera unavailable

### QR Code Display

For remote players:

1. **Generate QR codes** from ruleset names:
   ```bash
   python -c "import qrcode; qr = qrcode.QRCode(); qr.add_data('dnd5e_basic'); qr.make(); qr.make_image().save('qr.png')"
   ```

2. **Share QR image** via Discord/Slack/email

3. **Players scan** with scanner interface

4. **Rules sync** across all sessions

## Design Philosophy

### Minimal Scope (Phase 1)

The scanner deliberately avoids:
- ❌ OCR (optical character recognition)
- ❌ Live rulebook scanning
- ❌ Complex rule parsing
- ❌ External dependencies

Instead, it provides:
- ✅ Pre-indexed JSON rulesets
- ✅ QR code loading (multiple formats)
- ✅ Camera interface (HTML5)
- ✅ Manual input fallback
- ✅ Zero-dependency design

### Future Expansion (Roadmap)

Potential Phase 2+ features:
- OCR for scanning physical rulebooks
- AI-powered rule extraction
- Automatic rule adjudication
- Natural language rule queries
- Community ruleset marketplace
- Version control and updates

### Featherweight Principles

Scanner maintains VoiceDM's core philosophy:
- **No breaking changes** to existing code
- **Optional feature** (doesn't affect core functionality)
- **Stdlib only** (no external dependencies)
- **Offline-first** (no API calls required)
- **Privacy-focused** (no telemetry, no tracking)

## Troubleshooting

### Camera Not Working

**Issue**: "Camera not accessible" error

**Solutions**:
1. Check browser permissions (Settings → Privacy → Camera)
2. Ensure HTTPS or localhost (required for getUserMedia)
3. Try different browser (Chrome works best)
4. Use manual input as fallback

### Ruleset Not Found

**Issue**: "Ruleset not found" error

**Solutions**:
1. Check filename in `server/rulesets/`
2. Verify JSON syntax (`python -m json.tool < file.json`)
3. Check QR data format matches scanner expectations
4. Try manual input with exact filename

### Scanner Interface Not Loading

**Issue**: 404 error on `/scanner`

**Solutions**:
1. Ensure `scanner.html` exists in project root
2. Check server logs for startup errors
3. Verify FastAPI routes loaded correctly
4. Restart server with `uvicorn server.main:app --reload`

## Examples

### Example 1: Load D&D 5e and Roll Attack

```python
from server.scanner import scan_qr_code
from server.dice import quick_roll

# Load rules
dnd5e = scan_qr_code("dnd5e_basic")

# Get attack rule
attack = dnd5e["rules"]["combat"][0]
print(f"Rule: {attack['name']}")
print(f"Formula: {attack['formula']}")

# Roll attack with +5 modifier
result = quick_roll("d20+5")
print(f"Attack roll: {result.total}")
print(f"Critical: {result.is_critical}")
```

**Output**:
```
Rule: Attack Roll
Formula: d20 + ability_modifier + proficiency_bonus
Attack roll: 18
Critical: False
```

### Example 2: Scan QR Code in HTML Interface

```html
<!-- User scans QR code: voicedm://rules/dnd5e/basic -->
<script>
  async function loadRules(qrData) {
    const response = await fetch('/api/scanner/load', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({qr_data: qrData})
    });
    const ruleset = await response.json();
    console.log(ruleset.name);  // "D&D 5e Basic Rules"
    
    // Store in localStorage for session persistence
    localStorage.setItem('active_ruleset', JSON.stringify(ruleset));
  }
</script>
```

### Example 3: List and Select Rulesets

```python
from server.scanner import get_rulesets, scan_qr_code

# Get all available
rulesets = get_rulesets()
print("Available rulesets:")
for system, versions in rulesets.items():
    print(f"  {system}: {', '.join(versions)}")

# Load user selection
system = "dnd5e"
version = "basic"
qr_data = f"{system}_{version}"
ruleset = scan_qr_code(qr_data)
print(f"\nLoaded: {ruleset['name']} v{ruleset['version']}")
```

**Output**:
```
Available rulesets:
  dnd5e: basic

Loaded: D&D 5e Basic Rules v1.0
```

## Contributing

### Adding New Rulesets

1. **Fork repository**
2. **Create JSON ruleset** in `server/rulesets/`
3. **Follow schema** (see "Creating Custom Rulesets")
4. **Test loading**:
   ```bash
   python -c "from server.scanner import scan_qr_code; print(scan_qr_code('your_ruleset'))"
   ```
5. **Submit PR** with:
   - JSON file
   - QR code image (optional)
   - Documentation update

### Ruleset Guidelines

- **Accurate**: Rules match official source material
- **Complete**: Include all core mechanics for category
- **Tested**: Verify formulas work with dice engine
- **Tagged**: Use consistent tags for searchability
- **Sourced**: Cite official rulebook or SRD

## License

Scanner system follows VoiceDM's MIT license. Rulesets may have separate licensing:
- **SRD Content**: Generally open (D&D 5e SRD, Pathfinder OGL)
- **Official Rules**: Require permission or fair use
- **Custom Content**: Specify your own license

Always respect copyright and cite sources.

---

**Questions?** See [README.md](README.md) for VoiceDM overview or [QUICK_START.md](QUICK_START.md) for setup.

**Next Steps**: Try creating your own custom ruleset or explore the scanner API!
