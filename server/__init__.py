"""
VoiceDM Roll20 Harmony - Featherweight Hybrid AI Dungeon Master
"""
__version__ = "1.3.0"
__all__ = [
    "RandomSource",
    "RandomMode",
    "get_global_rng",
    "get_session_rng",
    "get_weighted_random",
    "DiceSystem",
    "quick_roll"
]

# Import randomness utilities
from .randomness import (
    RandomSource,
    RandomMode,
    get_global_rng,
    get_session_rng,
    get_weighted_random
)

# Import dice utilities
from .dice import (
    DiceSystem,
    quick_roll
)
