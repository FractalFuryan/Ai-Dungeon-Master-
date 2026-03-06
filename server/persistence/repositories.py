from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from server.persistence.models import (
    ArtifactDiscoveryModel,
    BondEventModel,
    Party,
    ReverenceTokenModel,
    TestedThread,
)


class PartyRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, world_id: str, party_id: str, name: str, litany_cut: str, bond_value: int, memythic_strain: float, created_at: datetime) -> Party:
        party = Party(
            id=party_id,
            world_id=world_id,
            name=name,
            litany_cut=litany_cut,
            bond_value=bond_value,
            memythic_strain=memythic_strain,
            created_at=created_at,
        )
        self.db.add(party)
        self.db.commit()
        return party

    def get(self, party_id: str) -> Optional[Party]:
        return self.db.query(Party).filter(Party.id == party_id).first()

    def update_state(self, party_id: str, bond_value: int, memythic_strain: float) -> None:
        party = self.get(party_id)
        if not party:
            return
        party.bond_value = bond_value
        party.memythic_strain = memythic_strain
        party.updated_at = datetime.utcnow()
        self.db.commit()


class ThreadRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_test(self, party_id: str, player_id: str, thread: str, note: str, timestamp: datetime, session_id: Optional[str] = None) -> TestedThread:
        row = TestedThread(
            party_id=party_id,
            player_id=player_id,
            thread=thread,
            note=note,
            timestamp=timestamp,
            session_id=session_id,
        )
        self.db.add(row)
        self.db.commit()
        return row

    def list_for_party(self, party_id: str) -> List[TestedThread]:
        return self.db.query(TestedThread).filter(TestedThread.party_id == party_id).order_by(TestedThread.timestamp.asc()).all()


class ReverenceTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, party_id: str, character_id: str, description: str, earned_at: datetime) -> ReverenceTokenModel:
        token = ReverenceTokenModel(
            party_id=party_id,
            character_id=character_id,
            description=description,
            earned_at=earned_at,
            used=False,
        )
        self.db.add(token)
        self.db.commit()
        return token

    def mark_used(self, token_id: str, used_at: datetime) -> bool:
        token = self.db.query(ReverenceTokenModel).filter(ReverenceTokenModel.id == token_id).first()
        if not token or token.used:
            return False
        token.used = True
        token.used_at = used_at
        self.db.commit()
        return True

    def list_unused(self, party_id: str, character_id: Optional[str] = None) -> List[ReverenceTokenModel]:
        query = self.db.query(ReverenceTokenModel).filter(
            ReverenceTokenModel.party_id == party_id,
            ReverenceTokenModel.used.is_(False),
        )
        if character_id:
            query = query.filter(ReverenceTokenModel.character_id == character_id)
        return query.order_by(ReverenceTokenModel.earned_at.asc()).all()


class ArtifactRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert_discovery(self, world_id: str, artifact_key: str, location_id: Optional[str], wielded_by: Optional[str], charge: float) -> ArtifactDiscoveryModel:
        row = (
            self.db.query(ArtifactDiscoveryModel)
            .filter(
                ArtifactDiscoveryModel.world_id == world_id,
                ArtifactDiscoveryModel.artifact_key == artifact_key,
            )
            .first()
        )

        if not row:
            row = ArtifactDiscoveryModel(
                world_id=world_id,
                artifact_key=artifact_key,
                location_id=location_id,
                wielded_by=wielded_by,
                charge=charge,
            )
            self.db.add(row)
        else:
            row.location_id = location_id
            row.wielded_by = wielded_by
            row.charge = charge
            row.last_used_at = datetime.utcnow()

        self.db.commit()
        return row

    def list_discoveries(self, world_id: str) -> List[ArtifactDiscoveryModel]:
        return self.db.query(ArtifactDiscoveryModel).filter(ArtifactDiscoveryModel.world_id == world_id).all()


class BondRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_event(self, party_id: str, event_type: str, description: str, characters_involved: List[str], bond_change: int, timestamp: datetime, payload: Optional[Dict[str, Any]] = None) -> BondEventModel:
        row = BondEventModel(
            party_id=party_id,
            event_type=event_type,
            description=description,
            characters_involved=characters_involved,
            bond_change=bond_change,
            timestamp=timestamp,
            payload=payload or {},
        )
        self.db.add(row)
        self.db.commit()
        return row

    def list_for_party(self, party_id: str) -> List[BondEventModel]:
        return self.db.query(BondEventModel).filter(BondEventModel.party_id == party_id).order_by(BondEventModel.timestamp.asc()).all()
