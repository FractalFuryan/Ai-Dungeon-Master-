# Git Commands for Release v1.4.0

## Stage All Files
```bash
git add .
```

## Commit Message (Copy This)
```
Release v1.4.0: Living Mythology Systems

MAJOR FEATURE: Party-aware mythology simulation with persistent world effects.

Engine:
- Add party origin engine with Triatic Litany cuts
- Add bond/reverence/strain engines
- Add artifact engine and litany-weighted oracle (composition)
- Add unified EngineEffects envelope
- Add service split: party_service, world_service, narrative_service

API:
- Add /api/party routes
- Add /api/artifacts routes
- Keep world snapshot at /api/world/state
- Preserve resolve route compatibility

Persistence:
- Add party/myth tables via Alembic 0004
- Add repository layer for party, thread, token, artifact, bond

Validation:
- Focused tests passing (anchor, veil, mechanics, party/myth)
- Migration chain verified through 20260306_0004

Docs:
- Update README, CHANGELOG, RELEASE_NOTES
- Sync release summary/checklist/commands docs

Breaking Changes: None intended
Migration: run alembic upgrade head
```

## Create Tag
```bash
git tag -a v1.4.0 -m "Living Mythology Systems release"
```

## Push to GitHub
```bash
git push origin main --tags
```

## Verify
```bash
git log --oneline -1
git tag -l | rg '^v1\\.4\\.0$' || git tag -l
```

---

## Post-Push: Create GitHub Release

1. Go to: `https://github.com/FractalFuryan/Ai-Dungeon-Master-/releases/new`
2. Select tag: `v1.4.0`
3. Release title:
   `v1.4.0: Living Mythology Systems 🌌⚔️`
4. Copy release body from `RELEASE_NOTES.md`
5. Click **Publish Release**

---

## Quick Sanity Checks

```bash
# Migrations
python -m alembic upgrade head

# Focused tests
.venv/bin/pytest -q tests/test_anchor.py tests/test_veil_nodes.py tests/test_mechanics.py tests/test_party_myth_systems.py
```

If both pass, release is ready.
