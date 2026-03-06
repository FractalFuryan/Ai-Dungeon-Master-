# 🚀 FINAL RELEASE CHECKLIST — v1.4.0

## ✅ Implementation State

- [x] Party origin, bond, reverence, strain, artifact, and litany oracle systems implemented
- [x] Service-oriented orchestration integrated into `WorldEngine`
- [x] New party/artifact API routes integrated
- [x] Persistence models and repositories added
- [x] Alembic migration `20260306_0004` added and validated
- [x] README, CHANGELOG, and RELEASE_NOTES updated
- [x] Focused regression + feature tests passing (`18 passed`)

---

## 🎯 Release Actions (Do in Order)

### 1. Final Local Verification

```bash
cd /workspaces/Ai-Dungeon-Master-
.venv/bin/pytest -q tests/test_anchor.py tests/test_veil_nodes.py tests/test_mechanics.py tests/test_party_myth_systems.py
DATABASE_URL=sqlite:///./voicedm.db python -m alembic upgrade head
```

### 2. Commit + Tag

```bash
git add .
git commit -m "Release v1.4.0: Living Mythology Systems"
git tag -a v1.4.0 -m "Living Mythology Systems release"
git push origin main --tags
```

### 3. Create GitHub Release Page

- Go to: `https://github.com/FractalFuryan/Ai-Dungeon-Master-/releases/new`
- Tag: `v1.4.0`
- Title: `v1.4.0: Living Mythology Systems 🌌⚔️`
- Description: copy from `RELEASE_NOTES.md`
- Click **Publish release**

---

## 🔍 Post-Publish Smoke Tests

- [ ] `GET /health` returns healthy status
- [ ] `GET /api/world/state?world_id=<world_id>` returns snapshot payload
- [ ] `POST /api/party/create` creates party with valid litany cut
- [ ] `POST /api/artifacts/{artifact_key}/discover` updates artifact state
- [ ] `POST /api/resolve/action` still resolves action normally

---

## 📢 Announcement Snippet

```text
🌌⚔️ Released: AI Dungeon Master v1.4.0 — Living Mythology Systems

New in this release:
- Triatic Litany party origins
- Bond/reverence/strain progression systems
- Artifact-symbol interactions
- Service-oriented world orchestration
- Party + artifact API routes
- Alembic migration chain through 0004

Docs and migration steps:
README.md, CHANGELOG.md, RELEASE_NOTES.md
```

---

## 🧱 Rollback Plan (If Needed)

- Roll back app deployment to previous image/revision
- Keep DB snapshot before migration
- If required, execute Alembic downgrade to prior stable revision

---

## ✅ Final Status Template

- Version: `v1.4.0`
- Branch: `main`
- Migration: `head` applied
- Tests: passing
- Release page: published
