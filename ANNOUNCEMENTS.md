# Announcement Templates

Copy-paste these for your release announcements.

---

## Twitter/X Post

```
Released: AI Dungeon Master v1.4.0 - Living Mythology Systems.

New in this version:
- Triatic Litany party origins
- Bond and reverence progression
- Artifact-symbol interactions
- Service-oriented world orchestration
- World snapshot API

Open source (MIT), self-hostable, and migration-ready.

#TabletopRPG #DnD #OpenSource #AI

https://github.com/FractalFuryan/Ai-Dungeon-Master-
```

Suggested image: world snapshot response or party state UI/log output.

---

## Reddit Post (r/rpg, r/DnD, r/gamedev)

### Title
```
[OC] I released v1.4.0 of my open-source AI Dungeon Master: party origins, bond/reverence systems, and myth simulation
```

### Body
```
I just released v1.4.0 of AI Dungeon Master.

This update focuses on persistent narrative systems that make long campaigns evolve around party identity, not just one-off action resolution.

What shipped:
- Triatic Litany party origins (No Patron, Incompetent Heroes, Glory Not Binding)
- Bond engine (shared trauma/victory progression)
- Reverence + strain systems
- Artifact discovery/use/transfer tied to symbolic world effects
- Litany-weighted oracle (composition-based)
- World snapshot API and additive persistence migrations

Tech notes:
- FastAPI + SQLAlchemy + Alembic
- Service-oriented orchestration split (party/world/narrative services)
- Repository layer added for easier testing
- Migration chain validated through 20260306_0004

Quick start:
1) `pip install -r requirements.txt`
2) `python -m alembic upgrade head`
3) `uvicorn server.main:app --reload --host 0.0.0.0 --port 8000`

Repo: https://github.com/FractalFuryan/Ai-Dungeon-Master-
License: MIT

Feedback on encounter pacing, pressure graphs, and artifact modding is especially welcome.
```

---

## Hacker News Post

### Title
```
Show HN: AI Dungeon Master v1.4.0 - persistent party mythology systems
```

### URL
```
https://github.com/FractalFuryan/Ai-Dungeon-Master-
```

### Comment
```
I shipped v1.4.0 of an open-source AI Dungeon Master focused on long-form campaign memory and myth simulation.

Highlights:
- Party origin cuts that alter progression behavior
- Bond/reverence systems and artifact-symbol interactions
- Service-oriented architecture split in the world engine
- Additive Alembic migrations and API surfaces for party/artifact/world state

I wanted to avoid a pure text-generator DM and move toward systems that produce durable consequences between sessions.

Would love feedback from folks who care about engine architecture, persistence design, and how to keep narrative systems testable.
```

---

## GitHub Discussions Post

### Title
```
v1.4.0 Released: Living Mythology Systems
```

### Body
```
v1.4.0 is now released.

Major additions:
- Triatic Litany party origin engine
- Bond/reverence/strain progression layers
- Artifact symbol integration
- Litany-weighted oracle
- Service-oriented world orchestration
- World snapshot endpoint
- Alembic migration 0004 for party/myth tables

Docs updated:
- README.md
- CHANGELOG.md
- RELEASE_NOTES.md
- RELEASE_SUMMARY.md
- RELEASE_CHECKLIST.md

If you are upgrading from v1.3.x, run:
`python -m alembic upgrade head`

Please share issues or design feedback in Discussions/Issues.
```

---

## Discord Server Announcement

```
Release live: AI Dungeon Master v1.4.0

Living Mythology Systems are now in:
- Party origin cuts
- Bond/reverence/strain progression
- Artifact-symbol interactions
- World snapshot API

Upgrade steps:
1. Pull latest main
2. Run alembic migrations
3. Start server and test /api/world/state

Repo: https://github.com/FractalFuryan/Ai-Dungeon-Master-
```

---

## Usage Tips

Twitter/X:
- Keep post under 8 lines.
- Include one concrete technical detail and one gameplay detail.

Reddit:
- Lead with what changed since last version.
- Include migration command and one example endpoint.

Hacker News:
- Focus on architecture and tradeoffs over feature marketing.
- Be explicit about what is deterministic vs generative.

GitHub:
- Pin the release discussion.
- Link changelog and release notes directly.
