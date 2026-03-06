# Release v1.4.0: Living Mythology Systems 🌌⚔️

## What's New

**AI Dungeon Master now supports party-aware myth simulation.**

This release adds persistent party origins, bond/reverence dynamics, artifact-symbol interactions, and service-oriented world orchestration while keeping existing resolve/myth routes compatible.

### Key Features

✅ **Triatic Litany party origins** - `no_patron`, `incompetent_heroes`, `glory_not_binding`  
✅ **Party bond engine** - shared trauma/victory events with progression bonuses  
✅ **Reverence economy + strain thresholds** - underdog/gifted dynamics and escalating world effects  
✅ **Artifact system** - discover/use/transfer mythic artifacts that inject symbols  
✅ **Litany-weighted oracle (composition-based)** - cleaner testing and oracle swapping  
✅ **Unified effects envelope** - standardized engine effect output shape  
✅ **Service split in world orchestration** - party/world/narrative services to reduce coordinator bloat  
✅ **World snapshot endpoint** - inspect runtime world + myth + party state at once

### New API Endpoints

- `POST /api/party/create`
- `GET /api/party/{party_id}`
- `POST /api/party/{party_id}/thread`
- `GET /api/party/{party_id}/threads`
- `POST /api/party/{party_id}/bond`
- `GET /api/party/{party_id}/bond`
- `POST /api/party/{party_id}/reverence/token`
- `POST /api/party/{party_id}/reverence/use`
- `GET /api/artifacts/`
- `POST /api/artifacts/{artifact_key}/discover`
- `POST /api/artifacts/{artifact_key}/use`
- `POST /api/artifacts/{artifact_key}/transfer`
- `GET /api/world/state`

---

## Philosophy

This release keeps the same core principles:

- **Rules-first resolution** (dice and guardrails remain explicit)
- **Persistent consequences** (threads, bonds, and symbols accumulate over time)
- **Modular architecture** (services + repositories for maintainability and testability)
- **Backwards-compatible evolution** (existing resolution surfaces continue to work)

---

## Technical Details

### New/Updated Core Files

- `server/engine/party_origin_engine.py`
- `server/engine/reverence_engine.py`
- `server/engine/bond_engine.py`
- `server/engine/artifact_engine.py`
- `server/engine/litany_oracle.py`
- `server/engine/effects.py`
- `server/engine/services.py`
- `server/engine/world_engine.py`
- `server/engine/thread_engine.py` (session-aware tracking additions)
- `server/persistence/repositories.py`
- `server/persistence/models.py` (party/myth tables)
- `server/api/party.py`
- `server/api/artifacts.py`

### Database and Migrations

Alembic chain validated through:

- `20260306_0001_add_v2_engine_tables.py`
- `20260306_0002_add_shards_table.py`
- `20260306_0003_add_narrative_threads.py`
- `20260306_0004_add_party_myth_tables.py`

New tables in `0004`:

- `parties`
- `tested_threads`
- `reverence_tokens`
- `artifact_discoveries`
- `bond_events`

### Architecture

```
Action Resolve
    ↓
WorldEngine (coordinator)
    ├── PartyService (party origin, bond/reverence/artifact effects)
    ├── WorldService (world updates)
    └── NarrativeService (narrative output)
```

This keeps world coordination centralized while reducing direct cross-engine coupling.

---

## Example in Play

**Party Origin:** `glory_not_binding`  
**Scene:** shared failure during a ritual breach

**Engine outcome:**
- Bond increases from shared trauma
- Thread test recorded under party history
- Potential reverence token/strain changes based on context
- Symbolic world state updated and queryable via `/api/world/state`

---

## Breaking Changes

None intended.

This is an additive release with compatibility-preserving updates to existing world resolution paths.

---

## Migration Guide

**From v1.3.x to v1.4.0:**

1. Pull latest code
2. Install dev dependencies if needed:
   ```bash
   pip install -r requirements-dev.txt
   ```
3. Run migrations:
   ```bash
   python -m alembic upgrade head
   ```
4. Start server as usual

Optional: create a party to enable litany-weighted behavior for that party context.

---

## Known Limitations

- Artifact catalog is bootstrap-defined in code (seed/DB-driven modding can be expanded next).
- Pressure graph supports topology input but depends on caller-provided location graph data.
- New party/myth APIs currently use lightweight parameter forms; strict request schema hardening is a natural next step.

---

## Community

**Feedback welcome!**

- 💬 [GitHub Discussions](https://github.com/FractalFuryan/Ai-Dungeon-Master-/discussions)
- 🐛 [Report Issues](https://github.com/FractalFuryan/Ai-Dungeon-Master-/issues)
- ⭐ Star if you love it!
- 🔀 Fork to make it your own

---

## Full Changelog

See [CHANGELOG.md](https://github.com/FractalFuryan/Ai-Dungeon-Master-/blob/main/CHANGELOG.md)

---

**Ready to run party-aware myth campaigns?**

Upgrade, migrate, and let your world remember what your party becomes. ⚔️🌌
