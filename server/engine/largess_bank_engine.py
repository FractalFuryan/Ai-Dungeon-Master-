from datetime import datetime
import logging
import random
from typing import Any, Dict, List, Optional
import uuid

from server.engine.largess_engine import LargessSeed, LargessType, NewShardDawn, ShardGrave, ShardTransition

logger = logging.getLogger(__name__)


class LargessBankEngine:
    """Bank of unused narrative potential across shard transitions."""

    def __init__(self, db_session: Optional[Any] = None, world_id: Optional[str] = None):
        self.db = db_session
        self.world_id = world_id
        self.graves: Dict[str, ShardGrave] = {}
        self.seeds: Dict[str, LargessSeed] = {}
        self.dawns: Dict[str, NewShardDawn] = {}

        if self.db is not None and self.world_id:
            self._load_from_db()

        logger.info("LargessBankEngine initialized")

    def _load_from_db(self) -> None:
        from server.persistence.models import LargessSeedModel, ShardDawnModel, ShardGraveModel

        seed_rows = self.db.query(LargessSeedModel).filter(LargessSeedModel.world_id == self.world_id).all()
        for row in seed_rows:
            seed = LargessSeed(
                id=row.id,
                seed_type=LargessType(row.seed_type),
                description=row.description,
                source_character=row.source_character,
                source_player=row.source_player,
                created_at=row.created_at,
                campaign_id=row.campaign_id,
                weight=float(row.weight or 1.0),
                claimed=bool(row.claimed),
                claimed_by=row.claimed_by,
                claimed_at=row.claimed_at,
                original_trope=row.original_trope,
                remixed_trope=row.remixed_trope,
            )
            setattr(seed, "grave_id", row.grave_id)
            self.seeds[seed.id] = seed

        grave_rows = self.db.query(ShardGraveModel).filter(ShardGraveModel.world_id == self.world_id).all()
        for row in grave_rows:
            grave = ShardGrave(
                id=row.id,
                shard_name=row.shard_name,
                completed_at=row.completed_at,
                campaign_id=row.campaign_id,
                legacy_ledger_id=row.legacy_ledger_id,
                largess_seeds=[s for s in self.seeds.values() if getattr(s, "grave_id", None) == row.id],
                final_ritual_words=list(row.final_ritual_words or []),
                total_retirements=int(row.total_retirements or 0),
                total_reverence=int(row.total_reverence or 0),
                major_plot=row.major_plot or "",
            )
            self.graves[grave.id] = grave

        dawn_rows = self.db.query(ShardDawnModel).filter(ShardDawnModel.world_id == self.world_id).all()
        for row in dawn_rows:
            dawn = NewShardDawn(
                id=row.id,
                name=row.name,
                transition_type=ShardTransition(row.transition_type),
                source_grave_id=row.source_grave_id,
                created_at=row.created_at,
                claimed_seeds=list(row.claimed_seeds or []),
                player_intents=list(row.player_intents or []),
                starting_motive_nodes=list(row.starting_motive_nodes or []),
            )
            self.dawns[dawn.id] = dawn

    def _persist_seed(self, seed: LargessSeed, grave_id: Optional[str] = None) -> None:
        if self.db is None or not self.world_id:
            return

        from server.persistence.models import LargessSeedModel

        row = self.db.query(LargessSeedModel).filter(LargessSeedModel.id == seed.id).first()
        if not row:
            row = LargessSeedModel(id=seed.id, world_id=self.world_id)
            self.db.add(row)

        row.grave_id = grave_id
        row.seed_type = seed.seed_type.value
        row.description = seed.description
        row.source_character = seed.source_character
        row.source_player = seed.source_player
        row.created_at = seed.created_at
        row.campaign_id = seed.campaign_id
        row.weight = seed.weight
        row.claimed = seed.claimed
        row.claimed_by = seed.claimed_by
        row.claimed_at = seed.claimed_at
        row.original_trope = seed.original_trope
        row.remixed_trope = seed.remixed_trope

        self.db.commit()

    def _persist_grave(self, grave: ShardGrave) -> None:
        if self.db is None or not self.world_id:
            return

        from server.persistence.models import ShardGraveModel

        row = self.db.query(ShardGraveModel).filter(ShardGraveModel.id == grave.id).first()
        if not row:
            row = ShardGraveModel(id=grave.id, world_id=self.world_id)
            self.db.add(row)

        row.shard_name = grave.shard_name
        row.completed_at = grave.completed_at
        row.campaign_id = grave.campaign_id
        row.legacy_ledger_id = grave.legacy_ledger_id
        row.final_ritual_words = grave.final_ritual_words
        row.total_retirements = grave.total_retirements
        row.total_reverence = grave.total_reverence
        row.major_plot = grave.major_plot
        self.db.commit()

    def _persist_dawn(self, dawn: NewShardDawn) -> None:
        if self.db is None or not self.world_id:
            return

        from server.persistence.models import ShardDawnModel

        row = self.db.query(ShardDawnModel).filter(ShardDawnModel.id == dawn.id).first()
        if not row:
            row = ShardDawnModel(id=dawn.id, world_id=self.world_id)
            self.db.add(row)

        row.name = dawn.name
        row.transition_type = dawn.transition_type.value
        row.source_grave_id = dawn.source_grave_id
        row.created_at = dawn.created_at
        row.claimed_seeds = dawn.claimed_seeds
        row.player_intents = dawn.player_intents
        row.starting_motive_nodes = dawn.starting_motive_nodes
        self.db.commit()

    def add_seed(self, seed: LargessSeed, grave_id: Optional[str] = None) -> None:
        self.seeds[seed.id] = seed
        # Attach synthetic attribute for reconstruction.
        setattr(seed, "grave_id", grave_id)
        self._persist_seed(seed, grave_id=grave_id)

    def persist_grave(self, grave: ShardGrave) -> None:
        self._persist_grave(grave)

    def persist_dawn(self, dawn: NewShardDawn) -> None:
        self._persist_dawn(dawn)

    def close_shard(
        self,
        shard_name: str,
        campaign_id: str,
        legacy_ledger_id: str,
        final_ritual_words: List[str],
        open_currents: List[Dict[str, Any]],
        retired_characters: List[Dict[str, Any]],
        player_intents: List[Dict[str, Any]],
    ) -> ShardGrave:
        logger.info("CLOSING SHARD: %s", shard_name)

        grave = ShardGrave(
            id=str(uuid.uuid4()),
            shard_name=shard_name,
            completed_at=datetime.utcnow(),
            campaign_id=campaign_id,
            legacy_ledger_id=legacy_ledger_id,
            final_ritual_words=final_ritual_words,
            total_retirements=len(retired_characters),
            total_reverence=sum(int(r.get("reverence_points", 0)) for r in retired_characters),
        )

        for current in open_currents:
            ripeness = current.get("ripeness", 0.5)
            if isinstance(ripeness, str):
                ripeness_weight = {
                    "fresh": 0.5,
                    "ripening": 1.0,
                    "fermented": 1.5,
                    "burst": 2.0,
                }.get(ripeness.lower(), 0.5)
            else:
                try:
                    ripeness_weight = float(ripeness)
                except (TypeError, ValueError):
                    ripeness_weight = 0.5

            seed = LargessSeed(
                id=str(uuid.uuid4()),
                seed_type=LargessType.OPEN_CURRENT,
                description=str(current.get("description", "An unresolved current")),
                source_character=None,
                source_player="system",
                created_at=datetime.utcnow(),
                campaign_id=campaign_id,
                weight=max(0.1, ripeness_weight * 2),
                original_trope=str(current.get("type", "unknown")),
            )
            self.add_seed(seed, grave_id=grave.id)
            grave.largess_seeds.append(seed)

        for intent in player_intents:
            seed = LargessSeed(
                id=str(uuid.uuid4()),
                seed_type=LargessType.CHARACTER_INTENT,
                description=str(intent.get("intent", "A player's unfulfilled intent")),
                source_character=intent.get("character_name"),
                source_player=str(intent.get("player_id", "unknown")),
                created_at=datetime.utcnow(),
                campaign_id=campaign_id,
                weight=1.0,
            )
            self.add_seed(seed, grave_id=grave.id)
            grave.largess_seeds.append(seed)

        self.graves[grave.id] = grave
        self._persist_grave(grave)
        logger.info("Shard closed %s with %s seeds", shard_name, len(grave.largess_seeds))
        return grave

    def dawn_new_shard(
        self,
        name: str,
        transition_type: ShardTransition,
        source_grave_id: str,
        player_count: int,
    ) -> NewShardDawn:
        if source_grave_id not in self.graves:
            raise ValueError(f"Grave {source_grave_id} not found")

        grave = self.graves[source_grave_id]
        logger.info("DAWN OF NEW SHARD: %s from %s", name, grave.shard_name)

        dawn = NewShardDawn(
            id=str(uuid.uuid4()),
            name=name,
            transition_type=transition_type,
            source_grave_id=source_grave_id,
            created_at=datetime.utcnow(),
        )
        dawn.starting_motive_nodes = self._generate_motive_nodes_from_seeds(grave, transition_type, player_count)
        self.dawns[dawn.id] = dawn
        self._persist_dawn(dawn)
        return dawn

    def _generate_motive_nodes_from_seeds(
        self,
        grave: ShardGrave,
        transition: ShardTransition,
        player_count: int,
    ) -> List[Dict[str, Any]]:
        del player_count
        nodes: List[Dict[str, Any]] = []
        available_seeds = [s for s in grave.largess_seeds if not s.claimed]
        random.shuffle(available_seeds)
        selected = available_seeds[: min(5, len(available_seeds))]

        for seed in selected:
            if transition == ShardTransition.FORWARD_FLOW:
                node = {
                    "id": str(uuid.uuid4()),
                    "name": f"Echo of {seed.source_character or 'the past'}",
                    "description": self._forward_flow_description(seed),
                    "pressure_type": "time",
                    "pressure": "The past echoes in the present",
                    "mundane_anchors": ["Visit the old ruins", "Speak with elders who remember"],
                    "seed_id": seed.id,
                }
            elif transition == ShardTransition.REWOUND:
                node = {
                    "id": str(uuid.uuid4()),
                    "name": "What Lies Beneath",
                    "description": self._rewound_description(seed),
                    "pressure_type": "mystery",
                    "pressure": "The past buried, but not forgotten",
                    "mundane_anchors": ["Explore the village ruins", "Dig through old records"],
                    "seed_id": seed.id,
                }
            else:
                node = {
                    "id": str(uuid.uuid4()),
                    "name": "Inverted Echo",
                    "description": self._remix_description(seed),
                    "pressure_type": "moral",
                    "pressure": "Nothing is as it was",
                    "mundane_anchors": ["Question old assumptions", "Listen to both sides"],
                    "seed_id": seed.id,
                }
                seed.remixed_trope = self._invert_trope(seed.original_trope or "unknown")
                self._persist_seed(seed, grave_id=getattr(seed, "grave_id", None))

            nodes.append(node)
        return nodes

    def _forward_flow_description(self, seed: LargessSeed) -> str:
        templates = [
            f"The {seed.description[:50]} still echoes. Descendants must now face it.",
            f"What was left unfinished now calls to a new generation. {seed.description[:100]}",
            f"The village built where {seed.description[:50]} now stands. But something stirs beneath.",
        ]
        return random.choice(templates)

    def _rewound_description(self, seed: LargessSeed) -> str:
        templates = [
            f"Before the fall, {seed.description[:100]} was just beginning.",
            f"In the days before, {seed.description[:100]} was a rumor, not yet a threat.",
            f"The ruins are fresh. {seed.description[:100]} is still a choice waiting to be made.",
        ]
        return random.choice(templates)

    def _remix_description(self, seed: LargessSeed) -> str:
        templates = [
            f"Everything is the same, but different. {seed.description[:100]} now means something else.",
            f"The menace is mercy now. {seed.description[:100]} has inverted.",
            f"Where there was once {seed.original_trope or 'danger'}, now there is opportunity.",
        ]
        return random.choice(templates)

    def _invert_trope(self, trope: str) -> str:
        inversions = {
            "threat": "ally",
            "enemy": "friend",
            "danger": "opportunity",
            "curse": "blessing",
            "death": "rebirth",
            "fear": "respect",
            "ignorance": "wisdom",
            "ruin": "foundation",
        }
        return inversions.get(trope.lower(), f"inverted_{trope}")

    def claim_seed(self, seed_id: str, new_character_id: str, player_id: str, intent: str) -> LargessSeed:
        if seed_id not in self.seeds:
            raise ValueError(f"Seed {seed_id} not found")

        seed = self.seeds[seed_id]
        seed.claimed = True
        seed.claimed_by = new_character_id
        seed.claimed_at = datetime.utcnow()
        self._persist_seed(seed, grave_id=getattr(seed, "grave_id", None))

        for grave in self.graves.values():
            if seed in grave.largess_seeds:
                for dawn in self.dawns.values():
                    if dawn.source_grave_id == grave.id:
                        dawn.player_intents.append(
                            {
                                "player_id": player_id,
                                "character_id": new_character_id,
                                "seed_id": seed_id,
                                "intent": intent,
                                "claimed_at": seed.claimed_at.isoformat(),
                            }
                        )
                        self._persist_dawn(dawn)
                        break
                break

        logger.info("Seed %s claimed by %s", seed_id, new_character_id)
        return seed

    def get_grave_interview_prompt(self, grave_id: str) -> List[Dict[str, Any]]:
        if grave_id not in self.graves:
            return []

        grave = self.graves[grave_id]
        unclaimed = [s for s in grave.largess_seeds if not s.claimed]
        prompts = []
        for seed in unclaimed[:5]:
            prompts.append(
                {
                    "seed_id": seed.id,
                    "type": seed.seed_type.value,
                    "prompt": f"You dig in the ruins and find: {seed.description[:100]}",
                    "question": "What does this mean to your character?",
                    "weight": seed.weight,
                }
            )
        return prompts

    def calculate_starting_boons(self, grave_id: str, claimed_seeds: List[str]) -> Dict[str, Any]:
        grave = self.graves.get(grave_id)
        if not grave:
            return {}

        total_reverence = grave.total_reverence
        claimed_count = len(claimed_seeds)
        boons: Dict[str, Any] = {
            "starting_xp_bonus": min(500, total_reverence * 50),
            "reputation_with_past": claimed_count * 10,
            "known_secrets": claimed_count,
            "inherited_items": claimed_count // 2,
        }

        for seed_id in claimed_seeds:
            seed = self.seeds.get(seed_id)
            if not seed:
                continue
            if seed.seed_type == LargessType.REVERENCE_ECHO:
                boons["reverence_starting"] = boons.get("reverence_starting", 0) + 1
            elif seed.seed_type == LargessType.RETIRED_LEGACY:
                boons["legacy_bonus"] = boons.get("legacy_bonus", 0) + 1

        return boons

    def get_bank_state(self) -> Dict[str, Any]:
        return {
            "graves": {
                "total": len(self.graves),
                "recent": [
                    {
                        "id": g.id,
                        "name": g.shard_name,
                        "completed": g.completed_at.isoformat(),
                        "seeds": len(g.largess_seeds),
                        "unclaimed": len([s for s in g.largess_seeds if not s.claimed]),
                    }
                    for g in sorted(self.graves.values(), key=lambda x: x.completed_at, reverse=True)[:5]
                ],
            },
            "seeds": {
                "total": len(self.seeds),
                "unclaimed": len([s for s in self.seeds.values() if not s.claimed]),
                "by_type": {
                    t.value: len([s for s in self.seeds.values() if s.seed_type == t and not s.claimed])
                    for t in LargessType
                },
            },
            "dawns": {
                "total": len(self.dawns),
                "active": [d.to_dict() for d in self.dawns.values()][-3:],
            },
        }
