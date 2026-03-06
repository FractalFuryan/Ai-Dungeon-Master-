from datetime import datetime
import logging
import random
from typing import Any, Dict, List, Optional
import uuid

from server.engine.largess_bank_engine import LargessBankEngine
from server.engine.largess_engine import LargessSeed, LargessType, NewShardDawn, ShardGrave, ShardTransition

logger = logging.getLogger(__name__)


class ReweaveDirectorEngine:
    """Director layer for reweave transitions between shard graves and new dawns."""

    def __init__(self, bank: LargessBankEngine):
        self.bank = bank
        self.current_dawn: Optional[NewShardDawn] = None

    def closing_arc_rite(
        self,
        players: List[Dict[str, Any]],
        open_currents: List[Dict[str, Any]],
        retired_characters: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        del retired_characters
        logger.info("CLOSING ARC RITE BEGIN")

        ritual_words = []
        seeds_created = []

        for player in players:
            player_id = player["id"]
            character_name = player.get("character_name", "Unknown")
            largess = self._generate_largess_prompt(player, open_currents)

            ritual_words.append(
                {
                    "player_id": player_id,
                    "character": character_name,
                    "words": largess["words"],
                    "seed_type": largess["type"].value,
                }
            )

            seed = LargessSeed(
                id=str(uuid.uuid4()),
                seed_type=largess["type"],
                description=largess["words"],
                source_character=character_name,
                source_player=player_id,
                created_at=datetime.utcnow(),
                campaign_id="current",
                weight=float(largess.get("weight", 1.0)),
            )
            seeds_created.append(seed)
            self.bank.seeds[seed.id] = seed

        return {
            "ritual": "closing_arc",
            "words": ritual_words,
            "seeds_created": [s.to_dict() for s in seeds_created],
            "message": "The largess is spoken. The grave accepts its seeds.",
        }

    def _generate_largess_prompt(self, player: Dict[str, Any], open_currents: List[Dict[str, Any]]) -> Dict[str, Any]:
        del player, open_currents
        types = [
            LargessType.WYRD_THREAD,
            LargessType.RUMOR,
            LargessType.REVERENCE_ECHO,
            LargessType.CHARACTER_INTENT,
        ]
        seed_type = random.choice(types)

        templates = {
            LargessType.WYRD_THREAD: [
                "I leave the thread I never pulled - the unresolved thread that still calls.",
                "The mysterious figure I never spoke to now waits in the ruins.",
                "My unfinished business with Hevuaca becomes a question for the next.",
            ],
            LargessType.RUMOR: [
                "The rumor about buried treasure never reached the right ears. Let it ripen.",
                "Whispers of the forgotten shrine follow me into the grave.",
                "They say the true name is still hidden where I left it.",
            ],
            LargessType.REVERENCE_ECHO: [
                "My reverence for the old ways now echoes in the empty shrine.",
                "The underdog's struggle becomes a lesson carved in stone.",
                "My final act of mercy leaves a mark on this place.",
            ],
            LargessType.CHARACTER_INTENT: [
                "I meant to found a village. Let another finish what I started.",
                "The dream of peace outlives me.",
                "My purpose remains, waiting for new hands.",
            ],
        }

        return {
            "type": seed_type,
            "words": random.choice(templates[seed_type]),
            "weight": random.uniform(0.5, 1.5),
        }

    def reweave_dawn_rite(
        self,
        shard_name: str,
        transition_type: ShardTransition,
        source_grave_id: str,
        players: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        logger.info("REWEAVE DAWN RITE: %s (%s)", shard_name, transition_type.value)

        dawn = self.bank.dawn_new_shard(
            name=shard_name,
            transition_type=transition_type,
            source_grave_id=source_grave_id,
            player_count=len(players),
        )
        self.current_dawn = dawn
        grave = self.bank.graves[source_grave_id]
        options = self._describe_transition_options(grave, transition_type)

        return {
            "ritual": "reweave_dawn",
            "dawn": dawn.to_dict(),
            "grave": grave.to_dict(),
            "options": options,
            "message": f"The grave of {grave.shard_name} awaits. What do you claim?",
        }

    def _describe_transition_options(self, grave: ShardGrave, chosen: ShardTransition) -> Dict[str, Any]:
        options: Dict[str, Any] = {}
        options["forward_flow"] = {
            "name": "Forward Flow",
            "description": (
                "Same table, same tropes, forward flow. Legacy Ledger continues. "
                "New characters are descendants or wyrd inheritors."
            ),
            "available": True,
        }
        options["rewound"] = {
            "name": "Rewound",
            "description": (
                "Same setting rewound to an earlier point. "
                "Old village ruins become the sandbox starting zone."
            ),
            "available": True,
        }
        options["remix"] = {
            "name": "Remix Lattice",
            "description": (
                "Same players, same basic roles, but largess remixed through inverted assumptions."
            ),
            "available": len(grave.largess_seeds) >= 3,
        }
        options["chosen"] = chosen.value
        return options

    def grave_interview(self, player_id: str, character_name: str, seed_id: str, intent: str) -> Dict[str, Any]:
        if not self.current_dawn:
            raise ValueError("No active dawn rite")

        seed = self.bank.claim_seed(seed_id, character_name, player_id, intent)
        finding = self._describe_finding(seed, intent)

        self.current_dawn.claimed_seeds.append(seed_id)
        self.current_dawn.player_intents.append(
            {
                "player_id": player_id,
                "character_name": character_name,
                "seed_id": seed_id,
                "intent": intent,
                "finding": finding,
            }
        )

        return {
            "ritual": "grave_interview",
            "character": character_name,
            "seed": seed.to_dict(),
            "finding": finding,
            "intent": intent,
        }

    def _describe_finding(self, seed: LargessSeed, intent: str) -> str:
        del intent
        templates = {
            LargessType.WYRD_THREAD: [
                f"You find a loose thread, still waving. It leads to {seed.description[:50]}",
                f"A message, half-finished, addressed to you: '{seed.description[:50]}'",
            ],
            LargessType.RUMOR: [
                f"An old rumor confirmed: {seed.description[:100]}",
                f"The villagers whisper of {seed.description[:50]} - now you know it's true.",
            ],
            LargessType.VILLAGE_RUIN: [
                f"You stand where {seed.description[:50]} once stood. The foundation stones remember.",
                f"Among the ruins, you find {seed.description[:100]}",
            ],
            LargessType.REVERENCE_ECHO: [
                f"A warmth lingers here. {seed.description[:100]}",
                "The reverence of the past still hums in these stones.",
            ],
            LargessType.CHARACTER_INTENT: [
                f"Someone's unfinished purpose calls to you: {seed.description[:100]}",
                f"A dream, left behind, now becomes yours: {seed.description[:100]}",
            ],
        }
        template_list = templates.get(seed.seed_type, [f"You find {seed.description}"])
        return random.choice(template_list)

    def closing_largess_ritual(self, players: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not self.current_dawn:
            raise ValueError("No active dawn rite")

        final_words = []
        for player in players:
            player_id = player["id"]
            character_name = player.get("character_name", "Unknown")
            claimed = [p for p in self.current_dawn.player_intents if p.get("player_id") == player_id]

            if claimed:
                claim = claimed[-1]
                words = (
                    f"From the grave of the last shard, I have claimed {claim['finding']}. "
                    f"My intent: {claim['intent']}"
                )
            else:
                words = "I stand at the grave, ready to weave new intent into these ruins."

            final_words.append({"player_id": player_id, "character": character_name, "words": words})

        grave = self.bank.graves.get(self.current_dawn.source_grave_id)
        if grave:
            grave.final_ritual_words.extend([w["words"] for w in final_words])

        return {
            "ritual": "closing_largess",
            "dawn": self.current_dawn.to_dict(),
            "final_words": final_words,
            "message": "The grave and the seed are one. The cycle continues.",
        }

    def get_reweave_state(self) -> Dict[str, Any]:
        return {
            "current_dawn": self.current_dawn.to_dict() if self.current_dawn else None,
            "bank_state": self.bank.get_bank_state(),
        }
