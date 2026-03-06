from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy.orm import Session

from server.engine.effects import PartyEffectResult
from server.persistence.repositories import PartyRepository, ReverenceTokenRepository, ThreadRepository

logger = logging.getLogger(__name__)


class LitanyCut(str, Enum):
    NO_PATRON = "no_patron"
    INCOMPETENT_HEROES = "incompetent_heroes"
    GLORY_NOT_BINDING = "glory_not_binding"


@dataclass
class PartyBond:
    value: int = 0
    shared_traumas: List[str] = field(default_factory=list)
    shared_victories: List[str] = field(default_factory=list)
    last_bond_event: Optional[datetime] = None

    def add_trauma(self, description: str) -> None:
        self.shared_traumas.append(description)
        self.value += 2
        self.last_bond_event = datetime.utcnow()

    def add_victory(self, description: str) -> None:
        self.shared_victories.append(description)
        self.value += 1
        self.last_bond_event = datetime.utcnow()

    def get_bonus(self) -> Dict[str, Any]:
        if self.value >= 5:
            return {"revive_per_session": 1, "group_saves": 2}
        if self.value >= 3:
            return {"group_saves": 1}
        return {}


@dataclass
class ReverenceToken:
    id: str
    character_id: str
    earned_at: datetime
    description: str
    used: bool = False
    used_at: Optional[datetime] = None


class PartyOrigin:
    def __init__(self, cut: LitanyCut, party_name: str = "The Unbound"):
        self.id = str(uuid.uuid4())
        self.cut = cut
        self.party_name = party_name
        self.created_at = datetime.utcnow()
        self.bond = PartyBond()
        self.reverence_tokens: List[ReverenceToken] = []
        self.memythic_strain: float = 0.0
        self.tested_threads: List[Dict[str, Any]] = []
        self.modifiers: Dict[str, Any] = {}
        self._initialize_cut_effects()

    def _initialize_cut_effects(self) -> None:
        if self.cut == LitanyCut.NO_PATRON:
            self.modifiers = {
                "rumor_spawn_rate": 1.2,
                "oracle_intensity": 1.1,
                "patron_quests": False,
                "starting_bond": 1,
                "description": "No patron's grace means the world speaks directly to you.",
            }
            self.bond.value = 1
        elif self.cut == LitanyCut.INCOMPETENT_HEROES:
            self.modifiers = {
                "stat_penalty": -1,
                "xp_gain_multiplier": 1.25,
                "symbol_charge_rate": 1.1,
                "skill_failure_bonus": 0.25,
                "description": "Incompetence is its own kind of wisdom.",
            }
        else:
            self.modifiers = {
                "bond_from_failure": 2,
                "bond_from_success": 1,
                "shared_trauma_bonus": True,
                "description": "Glory fades, but shared wounds endure.",
            }

    def record_thread(self, thread: str, player_id: str, note: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        row = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "thread": thread,
            "player_id": player_id,
            "note": note,
            "session_id": session_id,
        }
        self.tested_threads.append(row)
        return row

    def add_reverence_token(self, character_id: str, description: str) -> ReverenceToken:
        token = ReverenceToken(
            id=str(uuid.uuid4()),
            character_id=character_id,
            earned_at=datetime.utcnow(),
            description=description,
        )
        self.reverence_tokens.append(token)
        return token

    def use_reverence_token(self, token_id: str) -> bool:
        for token in self.reverence_tokens:
            if token.id == token_id and not token.used:
                token.used = True
                token.used_at = datetime.utcnow()
                return True
        return False

    def get_unused_tokens(self, character_id: Optional[str] = None) -> List[ReverenceToken]:
        tokens = [t for t in self.reverence_tokens if not t.used]
        if character_id:
            tokens = [t for t in tokens if t.character_id == character_id]
        return tokens

    def add_memythic_strain(self, amount: float) -> float:
        self.memythic_strain += float(amount)
        return self.memythic_strain

    def process_failure(self, character: Any, roll_result: Any, context: Dict[str, Any]) -> PartyEffectResult:
        result = PartyEffectResult()
        character_id = getattr(character, "id", None) or context.get("character_id", "unknown")
        character_name = getattr(character, "name", character_id)
        action = context.get("action", "unknown")

        if self.cut == LitanyCut.GLORY_NOT_BINDING:
            self.bond.add_trauma(f"{character_name} failed: {action}")
            result.bond_change = 2
            result.notes.append("Shared trauma increased party bond.")
        elif self.cut == LitanyCut.INCOMPETENT_HEROES and getattr(roll_result, "is_critical_failure", False):
            token = self.add_reverence_token(character_id, f"Learned from critical failure: {action}")
            result.reverence_token_id = token.id
            result.notes.append("Critical failure generated reverence token.")
        elif self.cut == LitanyCut.NO_PATRON:
            result.strain_change = 0.2
            self.add_memythic_strain(result.strain_change)
            result.notes.append("Failure increased memythic strain.")

        return result

    def process_success(self, character: Any, roll_result: Any, context: Dict[str, Any]) -> PartyEffectResult:
        result = PartyEffectResult()
        character_id = getattr(character, "id", None) or context.get("character_id", "unknown")
        character_name = getattr(character, "name", character_id)
        action = context.get("action", "unknown")

        if self.cut == LitanyCut.GLORY_NOT_BINDING:
            self.bond.add_victory(f"{character_name} succeeded: {action}")
            result.bond_change = 1
            result.notes.append("Shared victory strengthened bond.")
        elif self.cut == LitanyCut.INCOMPETENT_HEROES and getattr(roll_result, "is_critical_success", False):
            result.legendary_moment = True
            result.notes.append("Incompetent heroes achieved a legendary moment.")

        return result

    def get_state(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "party_name": self.party_name,
            "litany_cut": self.cut.value,
            "description": self.modifiers.get("description", ""),
            "bond": {
                "value": self.bond.value,
                "traumas": len(self.bond.shared_traumas),
                "victories": len(self.bond.shared_victories),
                "bonuses": self.bond.get_bonus(),
            },
            "reverence_tokens": {
                "total": len(self.reverence_tokens),
                "unused": len([t for t in self.reverence_tokens if not t.used]),
            },
            "memythic_strain": self.memythic_strain,
            "threads_tested": len(self.tested_threads),
            "modifiers": self.modifiers,
        }


class PartyOriginEngine:
    def __init__(self, db_session: Session, world_id: str):
        self.db = db_session
        self.world_id = world_id
        self.parties = PartyRepository(db_session)
        self.threads = ThreadRepository(db_session)
        self.tokens = ReverenceTokenRepository(db_session)
        self.active_origins: Dict[str, PartyOrigin] = {}

    def create_party(self, cut: LitanyCut, party_name: str) -> PartyOrigin:
        party = PartyOrigin(cut, party_name)
        self.parties.create(
            world_id=self.world_id,
            party_id=party.id,
            name=party_name,
            litany_cut=cut.value,
            bond_value=party.bond.value,
            memythic_strain=party.memythic_strain,
            created_at=party.created_at,
        )
        self.active_origins[party.id] = party
        return party

    def get_party(self, party_id: str) -> Optional[PartyOrigin]:
        if party_id in self.active_origins:
            return self.active_origins[party_id]

        db_party = self.parties.get(party_id)
        if not db_party:
            return None

        party = PartyOrigin(LitanyCut(db_party.litany_cut), db_party.name)
        party.id = db_party.id
        party.bond.value = int(db_party.bond_value or 0)
        party.memythic_strain = float(db_party.memythic_strain or 0.0)
        party.created_at = db_party.created_at or datetime.utcnow()

        for row in self.threads.list_for_party(party_id):
            party.tested_threads.append(
                {
                    "id": row.id,
                    "thread": row.thread,
                    "player_id": row.player_id,
                    "note": row.note,
                    "session_id": row.session_id,
                    "timestamp": row.timestamp.isoformat() if row.timestamp else None,
                }
            )

        for token in self.tokens.list_unused(party_id):
            party.reverence_tokens.append(
                ReverenceToken(
                    id=token.id,
                    character_id=token.character_id,
                    description=token.description,
                    earned_at=token.earned_at or datetime.utcnow(),
                    used=bool(token.used),
                    used_at=token.used_at,
                )
            )

        self.active_origins[party_id] = party
        return party

    def record_thread(self, party_id: str, thread: str, player_id: str, note: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        party = self.get_party(party_id)
        if not party:
            raise ValueError(f"Party {party_id} not found")

        record = party.record_thread(thread, player_id, note, session_id=session_id)
        self.threads.add_test(
            party_id=party_id,
            player_id=player_id,
            thread=thread,
            note=note,
            session_id=session_id,
            timestamp=datetime.fromisoformat(record["timestamp"]),
        )
        return record

    def persist_party_state(self, party: PartyOrigin) -> None:
        self.parties.update_state(
            party_id=party.id,
            bond_value=party.bond.value,
            memythic_strain=party.memythic_strain,
        )
