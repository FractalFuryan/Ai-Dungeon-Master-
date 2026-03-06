from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import random
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class OracleIntent(Enum):
    CLARITY = "clarity"
    DIRECTION = "direction"
    WARNING = "warning"
    MYSTERY = "mystery"
    RESOLUTION = "resolution"


@dataclass
class SymbolDraw:
    symbol: str
    archetype: Optional[str]
    meaning: str
    resonance: List[str]
    intensity: float


class OracleEngine:
    SYMBOLS = [
        {"name": "mirror", "archetype": "reflection", "meanings": ["self-discovery", "illusion", "truth", "duality"]},
        {"name": "bone", "archetype": "death", "meanings": ["mortality", "foundation", "remains", "ancestry"]},
        {"name": "ash", "archetype": "destruction", "meanings": ["ending", "remnants", "purification", "grief"]},
        {"name": "blood", "archetype": "life", "meanings": ["sacrifice", "family", "violence", "vitality"]},
        {"name": "shadow", "archetype": "concealment", "meanings": ["hidden truth", "fear", "companion", "absence"]},
        {"name": "crown", "archetype": "authority", "meanings": ["power", "burden", "legitimacy", "ambition"]},
        {"name": "throne", "archetype": "dominion", "meanings": ["seat of power", "vacancy", "usurpation", "inheritance"]},
        {"name": "chain", "archetype": "bondage", "meanings": ["connection", "imprisonment", "obligation", "strength"]},
        {"name": "key", "archetype": "access", "meanings": ["solution", "imprisonment", "mystery", "opportunity"]},
        {"name": "door", "archetype": "transition", "meanings": ["choice", "boundary", "opportunity", "threshold"]},
        {"name": "flame", "archetype": "transformation", "meanings": ["destruction", "passion", "renewal", "guidance"]},
        {"name": "water", "archetype": "fluidity", "meanings": ["emotion", "change", "depth", "purity"]},
        {"name": "stone", "archetype": "permanence", "meanings": ["endurance", "burden", "foundation", "obstacle"]},
        {"name": "wind", "archetype": "freedom", "meanings": ["change", "voice", "invisible force", "journey"]},
        {"name": "root", "archetype": "foundation", "meanings": ["origin", "connection", "nourishment", "entrapment"]},
        {"name": "wing", "archetype": "transcendence", "meanings": ["freedom", "protection", "aspiration", "escape"]},
        {"name": "mask", "archetype": "identity", "meanings": ["deception", "role", "protection", "true self"]},
        {"name": "well", "archetype": "depth", "meanings": ["source", "mystery", "descent", "supply"]},
    ]

    RESONANCE_MATRIX = {
        tuple(sorted(["mirror", "mask"])): "The reflection wears many faces",
        tuple(sorted(["bone", "ash"])): "What remains after the fire",
        tuple(sorted(["blood", "crown"])): "Power demands sacrifice",
        tuple(sorted(["shadow", "mirror"])): "The darkness shows what light cannot",
        tuple(sorted(["key", "door"])): "The threshold awaits",
        tuple(sorted(["throne", "chain"])): "Power binds as much as it elevates",
    }

    def __init__(self):
        self.symbol_deck = self.SYMBOLS.copy()
        self.draw_history: List[Dict[str, Optional[str]]] = []

    def draw_symbol(self, intent: Optional[OracleIntent] = None, context: Optional[str] = None) -> SymbolDraw:
        if not self.symbol_deck:
            self.symbol_deck = self.SYMBOLS.copy()
            random.shuffle(self.symbol_deck)

        symbol_data = random.choice(self.symbol_deck)
        self.symbol_deck.remove(symbol_data)

        meaning = self._interpret_symbol(symbol_data, intent, context)
        resonance = self._check_resonance(symbol_data["name"])
        intensity = self._calculate_intensity(intent, context)

        draw = SymbolDraw(
            symbol=symbol_data["name"],
            archetype=symbol_data["archetype"],
            meaning=meaning,
            resonance=resonance,
            intensity=intensity,
        )

        self.draw_history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "symbol": draw.symbol,
                "meaning": draw.meaning,
                "intent": intent.value if intent else None,
                "context": context,
            }
        )
        return draw

    def _interpret_symbol(self, symbol_data: Dict[str, object], intent: Optional[OracleIntent], context: Optional[str]) -> str:
        base_meaning = random.choice(symbol_data["meanings"])  # type: ignore[index]
        if intent == OracleIntent.CLARITY:
            return f"{base_meaning} becomes clear"
        if intent == OracleIntent.DIRECTION:
            return f"Follow the {base_meaning}"
        if intent == OracleIntent.WARNING:
            return f"Beware false {base_meaning}"
        if intent == OracleIntent.MYSTERY:
            return f"The {base_meaning} deepens"
        if intent == OracleIntent.RESOLUTION:
            return f"{base_meaning} finds conclusion"
        return str(base_meaning)

    def _check_resonance(self, symbol: str) -> List[str]:
        resonances: List[str] = []
        recent = [d.get("symbol") for d in self.draw_history[-3:]]
        for recent_symbol in recent:
            if not recent_symbol:
                continue
            pair = tuple(sorted([symbol, recent_symbol]))
            if pair in self.RESONANCE_MATRIX:
                resonances.append(self.RESONANCE_MATRIX[pair])
        return resonances

    def _calculate_intensity(self, intent: Optional[OracleIntent], context: Optional[str]) -> float:
        base = 0.5
        if intent:
            intent_intensity = {
                OracleIntent.CLARITY: 0.4,
                OracleIntent.DIRECTION: 0.6,
                OracleIntent.WARNING: 0.8,
                OracleIntent.MYSTERY: 0.7,
                OracleIntent.RESOLUTION: 0.5,
            }
            base = intent_intensity.get(intent, 0.5)

        if context and len(context) > 50:
            base += 0.1
        return min(1.0, base + random.uniform(-0.1, 0.1))

    def get_spread(self, count: int = 3, intent: Optional[OracleIntent] = None) -> List[SymbolDraw]:
        return [self.draw_symbol(intent) for _ in range(max(1, count))]

    def interpret_spread(self, symbols: List[SymbolDraw]) -> str:
        if len(symbols) == 1:
            return f"The {symbols[0].symbol} appears. {symbols[0].meaning}."
        if len(symbols) == 2:
            return (
                f"{symbols[0].symbol} and {symbols[1].symbol} appear together. "
                f"{symbols[0].meaning} leads to {symbols[1].meaning}."
            )
        if len(symbols) == 3:
            return (
                f"The {symbols[0].symbol} of the past ({symbols[0].meaning}) flows through the "
                f"{symbols[1].symbol} of present ({symbols[1].meaning}) toward the "
                f"{symbols[2].symbol} of future ({symbols[2].meaning})."
            )
        return f"Multiple symbols appear: {', '.join([s.symbol for s in symbols])}"

    def reset_deck(self) -> None:
        self.symbol_deck = self.SYMBOLS.copy()
        self.draw_history = []
