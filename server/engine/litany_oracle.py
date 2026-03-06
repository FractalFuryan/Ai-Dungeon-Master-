from datetime import datetime
import random
from typing import List, Optional

from server.engine.oracle_engine import OracleEngine, OracleIntent, SymbolDraw
from server.engine.party_origin_engine import LitanyCut, PartyOrigin


class LitanyWeightedOracle:
    """Composition wrapper that applies litany-aware weighting over a base oracle."""

    LITANY_WEIGHTS = {
        LitanyCut.NO_PATRON: {
            "symbols": ["mirror", "shadow", "wind", "door"],
            "multiplier": 1.5,
        },
        LitanyCut.INCOMPETENT_HEROES: {
            "symbols": ["bone", "ash", "chain", "stone"],
            "multiplier": 1.5,
        },
        LitanyCut.GLORY_NOT_BINDING: {
            "symbols": ["blood", "root", "crown", "throne"],
            "multiplier": 1.5,
        },
    }

    def __init__(self, base_oracle: OracleEngine, party_origin: Optional[PartyOrigin]):
        self.base_oracle = base_oracle
        self.party_origin = party_origin
        self.litany = party_origin.cut if party_origin else None

    def draw_symbol(self, intent: Optional[OracleIntent] = None, context: Optional[str] = None) -> SymbolDraw:
        if not self.litany:
            return self.base_oracle.draw_symbol(intent, context)

        weights = self.LITANY_WEIGHTS[self.litany]
        boosted = set(weights["symbols"])
        multiplier = float(weights["multiplier"])

        weighted_deck = []
        for symbol_data in self.base_oracle.SYMBOLS:
            copies = 10
            if symbol_data["name"] in boosted:
                copies = int(copies * multiplier)
            weighted_deck.extend([symbol_data] * max(1, copies))

        symbol_data = random.choice(weighted_deck)
        meaning = self.base_oracle._interpret_symbol(symbol_data, intent, context)
        resonance = self.base_oracle._check_resonance(symbol_data["name"])
        intensity = min(1.0, self.base_oracle._calculate_intensity(intent, context) * multiplier)

        draw = SymbolDraw(
            symbol=symbol_data["name"],
            archetype=symbol_data["archetype"],
            meaning=meaning,
            resonance=resonance,
            intensity=intensity,
        )

        self.base_oracle.draw_history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "symbol": draw.symbol,
                "meaning": draw.meaning,
                "intent": intent.value if intent else None,
                "context": context,
                "litany": self.litany.value,
            }
        )
        return draw

    def get_spread(self, count: int = 3, intent: Optional[OracleIntent] = None) -> List[SymbolDraw]:
        return [self.draw_symbol(intent=intent) for _ in range(max(1, count))]

    def interpret_spread(self, symbols: List[SymbolDraw]) -> str:
        base = self.base_oracle.interpret_spread(symbols)
        if not self.litany:
            return base
        if self.litany == LitanyCut.NO_PATRON:
            return f"Without patron, the fates speak directly: {base}"
        if self.litany == LitanyCut.INCOMPETENT_HEROES:
            return f"Through struggle, wisdom emerges: {base}"
        return f"Shared symbols bind where glory failed: {base}"
