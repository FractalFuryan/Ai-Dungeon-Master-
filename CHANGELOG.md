# Changelog

All notable changes to AI Dungeon Master will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-03-06

### Added - Living Mythology Systems 🌌

- **Party Origin Engine** (`server/engine/party_origin_engine.py`)
  - Triatic Litany cuts: `no_patron`, `incompetent_heroes`, `glory_not_binding`
  - Party bond growth from shared trauma/victory
  - Reverence token generation/consumption flow
  - Memythic strain accumulation and party state snapshots

- **Reverence + Strain Engines** (`server/engine/reverence_engine.py`)
  - XP economy for underdog/gifted progression
  - `CharacterStatsView.from_character(...)` adapter for existing character model
  - Strain thresholds driving veil/dream/reality pressure effects

- **Bond, Artifact, and Litany Oracle Systems**
  - `server/engine/bond_engine.py` for typed bond events
  - `server/engine/artifact_engine.py` for discover/use/transfer artifact flow
  - `server/engine/litany_oracle.py` using composition over inheritance

- **Service-Oriented World Orchestration** (`server/engine/services.py`)
  - `party_service`, `world_service`, and `narrative_service`
  - Unified `EngineEffects` envelope (`server/engine/effects.py`)

- **New API Surfaces**
  - `server/api/party.py`
  - `server/api/artifacts.py`
  - world snapshot endpoint retained at `GET /api/world/state`

- **Repository Layer for Testability** (`server/persistence/repositories.py`)
  - Party, thread, token, artifact, and bond repositories

### Changed

- Extended `WorldEngine` (`server/engine/world_engine.py`) with optional `party_id` and party/myth integration while preserving existing resolve and myth routes.
- Updated dependency injection (`server/api/dependencies.py`) to resolve `party_id` from path/query/body.
- Expanded thread tracking (`server/engine/thread_engine.py`) with session-aware `record_test` and `get_session_summary`.
- Updated app/router exports:
  - `server/api/__init__.py`
  - `server/main.py`
  - `server/engine/__init__.py`
  - `server/persistence/__init__.py`

### Database

- Added Alembic revision `20260306_0004_add_party_myth_tables.py`:
  - `parties`
  - `tested_threads`
  - `reverence_tokens`
  - `artifact_discoveries`
  - `bond_events`

### Validation

- Migration chain verified through `20260306_0004` on SQLite.
- Regression + new feature tests passing:
  - `tests/test_anchor.py`
  - `tests/test_veil_nodes.py`
  - `tests/test_mechanics.py`
  - `tests/test_party_myth_systems.py`

## [1.1.0] - 2026-01-01

### Added - Roll20 Integration 🎲

- **Roll20 API Script** (`roll20/aidm-roll20.js`)
  - Sandbox-safe chat command listener
  - Queue-based command processing
  - Commands: `!aidm`, `!aidm_dump`, `!aidm_clear`, `!aidm help`
  - Full Roll20 ToS compliance (no HTTP, no sandbox violations)

- **GM Relay Page** (`relay/roll20-relay.html`)
  - Beautiful dark-themed UI for GM command processing
  - JSON queue processor with visual feedback
  - Copy-to-clipboard for easy narration pasting
  - Configurable backend URL
  - Activity logging and status indicators

- **Roll20 Backend Adapter** (`server/roll20_adapter.py`)
  - `/roll20/command` endpoint for processing Roll20 events
  - Input sanitization (500 char limit, HTML stripping)
  - Persona switching support (classic, gothic, whimsical, cosmic, noir, tavern)
  - Roll20-native dice roll commands (respects character sheets)
  - Turn queue management (`myturn`, `next`)
  - Campaign-namespaced memory (`roll20:{campaign_id}`)
  - Health check endpoint at `/roll20/health`

- **Documentation**
  - [ROLL20_GUIDE.md](ROLL20_GUIDE.md) - Complete Roll20 integration guide
  - [roll20/macros.example](roll20/macros.example) - Example Roll20 macros
  - [screenshots/README.md](screenshots/README.md) - Screenshot guidelines

### Changed

- Updated main [README.md](README.md) with Roll20 integration references
- Added Roll20 mode to deployment modes documentation
- Integrated Roll20 router into main FastAPI app

### Philosophy

Roll20 integration maintains core principles:
- **Dice sovereignty**: Roll20 owns all mechanics
- **GM authority**: AI narrates, never overrides
- **Table trust**: No hidden rolls, no AI dice manipulation
- **ToS respect**: Clean relay pattern, no sandbox violations

## [1.0.0] - 2025-12-XX

### Added - Initial Release

- Voice-driven multiplayer RPG companion
- QR code session joining
- Push-to-talk voice input
- AI text-to-speech narration
- 4 switchable DM personas (Classic, Gothic, Whimsical, Sci-Fi)
- Natural turn system ("my turn" queue)
- Persistent campaign save/load
- SQLite database for campaign storage
- WebSocket real-time sync
- Mobile-first responsive design
- Capacitor mobile app support (iOS/Android)
- GitHub Codespaces one-click setup

### Core Features

- FastAPI + WebSockets backend
- OpenAI GPT-4o-mini for narration
- OpenAI TTS for voice output
- Pure HTML/JS frontend (PWA-ready)
- Physical dice support (table trust model)

### Documentation

- QUICK_START.md
- TURN_SYSTEM_GUIDE.md
- PERSONA_GUIDE.md
- PERSISTENCE_GUIDE.md
- MOBILE_GUIDE.md
- PRODUCTION_CHECKLIST.md

---

## Release Notes

### Living Mythology Systems (v1.4.0)

This release upgrades the engine from a rules-only resolver into a **party-aware mythology simulator**.

**What's New:**
- Party origin cuts that shape progression tone and symbolic pressure
- Bond, reverence, and artifact systems wired into world resolution
- Litany-weighted oracle behavior via composition
- Service-oriented orchestration to keep world logic modular
- Snapshot API for operational world + myth state inspection

**Technical Approach:**
- Additive persistence (`server/persistence`) with repository abstraction
- Migration-first rollout via Alembic revisions (`0001` → `0004`)
- Backward-compatible route behavior maintained for existing resolve/myth endpoints

**Perfect For:**
- Long campaigns where party identity matters mechanically
- Narrative-heavy tables that want persistent symbolic consequences
- GMs who need inspectable world state between sessions

### Roll20 Integration (v1.1.0)

This release extends AI Dungeon Master to **virtual tabletops** while maintaining the core philosophy: the AI facilitates, never dictates.

**What's New:**
- Chat-based AI DM for Roll20 games
- Persistent campaign memory per Roll20 game
- Persona switching via `!aidm persona [name]`
- Turn discipline with `!aidm myturn`
- Roll20-native dice (AI returns `/roll` commands, never touches mechanics)

**Technical Approach:**
- GM relay pattern (ToS-safe, no sandbox violations)
- Manual paste workflow (reliable, respectful of Roll20 constraints)
- Future-ready for browser extension automation

**Perfect For:**
- Roll20 Pro users wanting narrative depth
- GMs managing large player groups
- Long-running campaigns needing memory
- Tables wanting consistent DM personality

**Installation:**
1. Deploy backend (free on Render/Fly.io)
2. Install API script in Roll20
3. Open relay page in GM browser
4. Start narrating

See [ROLL20_GUIDE.md](ROLL20_GUIDE.md) for complete setup.

---

## Roadmap

### Planned Enhancements
- Browser extension for automatic relay (v1.2.0)
- Turn tracker bidirectional sync (v1.2.0)
- Automatic handout generation (v1.3.0)
- Campaign export/import between web and Roll20 modes (v1.3.0)
- Advanced persona customization (v1.4.0)
- Multi-language support (v2.0.0)

### Community Requests
- Optional system dice mode for remote games
- Ambient sound effect integration
- Character sheet integration
- Session recording and playback
- NPC voice differentiation

---

[1.1.0]: https://github.com/FractalFuryan/Ai-Dungeon-Master-/releases/tag/v1.1.0
[1.0.0]: https://github.com/FractalFuryan/Ai-Dungeon-Master-/releases/tag/v1.0.0
[1.4.0]: https://github.com/FractalFuryan/Ai-Dungeon-Master-/releases/tag/v1.4.0
