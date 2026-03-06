# 🌌 Release v1.4.0: Living Mythology Systems — READY

## ✅ Release Status

Implementation, docs, migrations, and focused regression tests are complete.

---

## 📦 What Was Shipped

### Engine Layer
- ✅ `server/engine/party_origin_engine.py` (Triatic Litany party origins)
- ✅ `server/engine/reverence_engine.py` (XP economy + strain thresholds)
- ✅ `server/engine/bond_engine.py` (typed bond event handling)
- ✅ `server/engine/artifact_engine.py` (discover/use/transfer artifact flow)
- ✅ `server/engine/litany_oracle.py` (composition-based litany weighting)
- ✅ `server/engine/effects.py` (unified `EngineEffects` + `PartyEffectResult`)
- ✅ `server/engine/services.py` (`party_service`, `world_service`, `narrative_service`)

### API Layer
- ✅ `server/api/party.py`
- ✅ `server/api/artifacts.py`
- ✅ `server/api/world_state.py` snapshot endpoint
- ✅ `server/api/dependencies.py` enhanced with optional `party_id`
- ✅ Router wiring in `server/main.py` and `server/api/__init__.py`

### Persistence + Migration
- ✅ `server/persistence/models.py` party/myth tables
- ✅ `server/persistence/repositories.py` repository abstraction
- ✅ Alembic `20260306_0004_add_party_myth_tables.py`
- ✅ Migration chain validated from `0001` through `0004`

### Validation
- ✅ `.venv/bin/pytest -q tests/test_anchor.py tests/test_veil_nodes.py tests/test_mechanics.py tests/test_party_myth_systems.py`
- ✅ Result: `18 passed`

---

## 🚀 Release Actions

### 1. Prepare Commit
```bash
git add .
git commit -m "Release v1.4.0: Living Mythology Systems

- Add Triatic Litany party origin engine
- Add bond/reverence/strain/artifact systems
- Add litany-weighted oracle (composition)
- Add service-oriented world orchestration
- Add party + artifact API routes
- Add repository layer + Alembic 0004 migration
- Update README, CHANGELOG, RELEASE_NOTES and release docs

Breaking Changes: None intended
Migration: run alembic upgrade head"
```

### 2. Tag and Push
```bash
git tag -a v1.4.0 -m "Living Mythology Systems release"
git push origin main --tags
```

### 3. Publish GitHub Release
- Tag: `v1.4.0`
- Title: `v1.4.0: Living Mythology Systems 🌌⚔️`
- Body: copy from `RELEASE_NOTES.md`
- Verify changelog links and docs render correctly

---

## 🎯 Operational Checks

- [ ] `python -m alembic upgrade head` succeeds on deployment target
- [ ] `/api/world/state?world_id=<id>` returns snapshot
- [ ] `/api/party/create` can create party origin with litany cut
- [ ] `/api/artifacts/` endpoints respond correctly
- [ ] Existing `/api/resolve/action` flow remains functional

---

## 🧭 Next Candidate Work (Post-Release)

- Schema-based request/response models for party/artifact endpoints
- Artifact catalog loading from seed JSON or DB rulesets
- Pressure graph sourcing from persisted world topology

---

**Release posture:** ready to ship once tag + release page are published.
