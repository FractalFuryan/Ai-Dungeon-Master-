from dataclasses import dataclass
import logging
from typing import Any, Dict, List, Optional
import uuid

from server.persistence.repositories import ArtifactRepository

logger = logging.getLogger(__name__)


@dataclass
class Artifact:
    id: str
    name: str
    symbol: str
    archetype: str
    description: str
    memythic_charge: float = 1.0
    discovered: bool = False
    current_location: Optional[str] = None
    wielded_by: Optional[str] = None


class ArtifactEngine:
    DEFAULT_ARTIFACTS = {
        "troll": {
            "name": "Troll's Heart",
            "symbol": "regeneration",
            "archetype": "persistence",
            "description": "A still-beating heart that regenerates any wound, but slowly consumes the bearer's memories",
        },
        "gryphon": {
            "name": "Gryphon's Judgment",
            "symbol": "justice",
            "archetype": "balance",
            "description": "A feather that weighs the truth of any soul, but reveals uncomfortable truths",
        },
        "hevuaca": {
            "name": "Hevuaca's Ledger",
            "symbol": "debt",
            "archetype": "obligation",
            "description": "An ancient book that records every debt owed and every favor unreturned",
        },
        "mirror": {
            "name": "Mirror of True Faces",
            "symbol": "reflection",
            "archetype": "truth",
            "description": "Shows not what you look like, but what you have become",
        },
        "bone": {
            "name": "Bone Crown",
            "symbol": "death",
            "archetype": "mortality",
            "description": "Crown of the first king, whispers the names of those soon to die",
        },
    }

    def __init__(self, db_session, world_id: str, artifact_catalog: Optional[Dict[str, Dict[str, str]]] = None):
        self.world_id = world_id
        self.repo = ArtifactRepository(db_session)
        self.catalog = artifact_catalog or self.DEFAULT_ARTIFACTS
        self.artifacts: Dict[str, Artifact] = {}
        self._initialize_artifacts()

    def _initialize_artifacts(self) -> None:
        for key, data in self.catalog.items():
            self.artifacts[key] = Artifact(
                id=str(uuid.uuid4()),
                name=data["name"],
                symbol=data["symbol"],
                archetype=data["archetype"],
                description=data["description"],
            )

        for row in self.repo.list_discoveries(self.world_id):
            artifact = self.artifacts.get(row.artifact_key)
            if artifact:
                artifact.discovered = True
                artifact.current_location = row.location_id
                artifact.wielded_by = row.wielded_by
                artifact.memythic_charge = float(row.charge or 1.0)

    def discover_artifact(self, artifact_key: str, location_id: str) -> Dict[str, Any]:
        artifact = self._get_artifact(artifact_key)
        artifact.discovered = True
        artifact.current_location = location_id
        self.repo.upsert_discovery(self.world_id, artifact_key, location_id, artifact.wielded_by, artifact.memythic_charge)
        return {
            "artifact": artifact.name,
            "symbol": artifact.symbol,
            "archetype": artifact.archetype,
            "description": artifact.description,
            "location": location_id,
        }

    def get_artifact_effect(self, artifact_key: str, character_stats: Dict[str, Any]) -> Dict[str, Any]:
        artifact = self._get_artifact(artifact_key)
        effects: Dict[str, Any] = {
            "symbol_injected": artifact.symbol,
            "memythic_charge": artifact.memythic_charge,
        }

        if artifact_key == "troll":
            effects.update({"regeneration": True, "memory_cost": 0.1})
        elif artifact_key == "gryphon":
            effects.update({"truth_detection": True, "uncomfortable_truth": True})
        elif artifact_key == "hevuaca":
            effects.update({"debt_tracking": True, "obligation_marker": True})

        return effects

    def use_artifact(self, artifact_key: str, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        artifact = self._get_artifact(artifact_key)
        artifact.memythic_charge += 0.1
        artifact.wielded_by = user_id

        self.repo.upsert_discovery(
            world_id=self.world_id,
            artifact_key=artifact_key,
            location_id=context.get("location_id", artifact.current_location),
            wielded_by=user_id,
            charge=artifact.memythic_charge,
        )

        result = {
            "artifact": artifact.name,
            "symbol": artifact.symbol,
            "used_by": user_id,
            "charge": artifact.memythic_charge,
        }

        if artifact_key == "troll":
            result.update({"healing": "Complete regeneration", "memory_loss": "You forget a cherished memory"})
        elif artifact_key == "gryphon":
            result.update({"judgment": "The truth is revealed", "cost": "Someone present is judged unworthy"})
        elif artifact_key == "hevuaca":
            result.update({"debt_revealed": "All debts in the area are known", "obligation": "You owe a debt to the artifact now"})

        return result

    def get_all_artifacts(self, discovered_only: bool = False) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for key, artifact in self.artifacts.items():
            if discovered_only and not artifact.discovered:
                continue
            out.append(
                {
                    "key": key,
                    "name": artifact.name,
                    "symbol": artifact.symbol,
                    "archetype": artifact.archetype,
                    "description": artifact.description,
                    "discovered": artifact.discovered,
                    "location": artifact.current_location,
                    "wielder": artifact.wielded_by,
                    "charge": artifact.memythic_charge,
                }
            )
        return out

    def transfer_artifact(self, artifact_key: str, new_wielder: str, new_location: str) -> Dict[str, Any]:
        artifact = self._get_artifact(artifact_key)
        old_wielder = artifact.wielded_by
        artifact.wielded_by = new_wielder
        artifact.current_location = new_location

        self.repo.upsert_discovery(
            world_id=self.world_id,
            artifact_key=artifact_key,
            location_id=new_location,
            wielded_by=new_wielder,
            charge=artifact.memythic_charge,
        )

        return {
            "artifact": artifact.name,
            "from": old_wielder,
            "to": new_wielder,
            "location": new_location,
        }

    def _get_artifact(self, artifact_key: str) -> Artifact:
        artifact = self.artifacts.get(artifact_key)
        if not artifact:
            raise ValueError(f"Unknown artifact: {artifact_key}")
        return artifact
