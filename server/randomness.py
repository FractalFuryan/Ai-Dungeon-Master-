"""
VoiceDM Randomness System

Implements:
1. Linear deterministic sequences (for controlled progression)
2. Non-linear probabilities (for surprises)
3. OS-backed entropy for true randomness
4. Optional deterministic mode for debugging/replay
"""

import secrets
import hashlib
from typing import Optional, List, Any, Dict
from enum import Enum


class RandomMode(str, Enum):
    """Randomness modes for different use cases"""
    SECURE = "secure"      # OS entropy (default)
    DETERMINISTIC = "deterministic"  # Seeded for replay
    WEIGHTED = "weighted"  # Non-linear probability distributions
    LINEAR = "linear"      # Predictable sequences


class RandomSource:
    """
    Unified randomness source with multiple modes.
    
    Defaults to OS entropy (secure), but can be configured
    for deterministic sequences or weighted probabilities.
    """
    
    def __init__(
        self,
        seed: Optional[str] = None,
        mode: RandomMode = RandomMode.SECURE
    ):
        """
        Initialize random source.
        
        Args:
            seed: Optional seed for deterministic mode
            mode: Randomness mode (secure, deterministic, weighted, linear)
        """
        self.mode = mode
        self._counter = 0
        
        if mode == RandomMode.DETERMINISTIC and seed is None:
            seed = "voicedm_deterministic"
        
        self._seed = seed.encode() if seed else None
        
        # For linear sequences
        self._linear_state = 0
        self._linear_step = 0.01  # Default linear progression
        
        # For weighted distributions
        self._weight_history: List[float] = []
    
    def _get_secure_float(self) -> float:
        """Get float from OS entropy pool"""
        return secrets.randbelow(10**12) / 10**12
    
    def _get_deterministic_float(self) -> float:
        """Get deterministic float from seeded hash chain"""
        self._counter += 1
        h = hashlib.blake2b(
            self._seed + self._counter.to_bytes(8, "big"),
            digest_size=8
        ).digest()
        return int.from_bytes(h, "big") / 2**64
    
    def _get_linear_float(self) -> float:
        """Get linearly progressing value (lengthen/shorten pattern)"""
        self._linear_state = (self._linear_state + self._linear_step) % 1.0
        return self._linear_state
    
    def rand_float(self, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """
        Get random float in range [min_val, max_val).
        
        Args:
            min_val: Minimum value (inclusive)
            max_val: Maximum value (exclusive)
        
        Returns:
            Random float based on current mode
        """
        # Get base value based on mode
        if self.mode == RandomMode.SECURE:
            base = self._get_secure_float()
        elif self.mode == RandomMode.DETERMINISTIC:
            base = self._get_deterministic_float()
        elif self.mode == RandomMode.LINEAR:
            base = self._get_linear_float()
        else:  # WEIGHTED or fallback to SECURE
            base = self._get_secure_float()
        
        # Scale to desired range
        return min_val + base * (max_val - min_val)
    
    def choice(self, items: List[Any], weights: Optional[List[float]] = None) -> Any:
        """
        Choose random item from list.
        
        Args:
            items: List of items to choose from
            weights: Optional weights for weighted selection
        
        Returns:
            Selected item
        """
        if not items:
            raise ValueError("Empty choice list")
        
        # Weighted selection (non-linear probabilities)
        if weights and len(weights) == len(items):
            return self._weighted_choice(items, weights)
        
        # Simple random selection
        idx = int(self.rand_float(0, len(items)))
        return items[min(idx, len(items) - 1)]
    
    def _weighted_choice(self, items: List[Any], weights: List[float]) -> Any:
        """Weighted random choice with non-linear probabilities"""
        # Normalize weights
        total = sum(weights)
        if total <= 0:
            return self.choice(items)
        
        normalized = [w / total for w in weights]
        
        # Apply non-linear transformation (1.5 exponent creates non-linearity)
        transformed = [w**1.5 for w in normalized]
        
        # Re-normalize
        transformed_total = sum(transformed)
        if transformed_total <= 0:
            return self.choice(items)
        
        normalized_transformed = [w / transformed_total for w in transformed]
        
        # Weighted random selection
        r = self.rand_float()
        cumulative = 0.0
        
        for item, weight in zip(items, normalized_transformed):
            cumulative += weight
            if r <= cumulative:
                self._weight_history.append(weight)
                if len(self._weight_history) > 100:
                    self._weight_history.pop(0)
                return item
        
        return items[-1]
    
    def randint(self, a: int, b: int) -> int:
        """
        Get random integer in range [a, b] (inclusive).
        
        Args:
            a: Minimum value
            b: Maximum value
        
        Returns:
            Random integer
        """
        if a > b:
            a, b = b, a
        span = b - a + 1
        return a + int(self.rand_float(0, span))
    
    def shuffle(self, items: List[Any]) -> List[Any]:
        """Shuffle list using current random mode"""
        shuffled = items.copy()
        
        # Fisher-Yates shuffle
        for i in range(len(shuffled) - 1, 0, -1):
            j = self.randint(0, i)
            shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
        
        return shuffled
    
    def sample(self, items: List[Any], k: int) -> List[Any]:
        """Sample k items without replacement"""
        if k > len(items):
            raise ValueError("Sample larger than population")
        
        if k == len(items):
            return self.shuffle(items)
        
        # Simple reservoir sampling
        result = items[:k]
        
        for i in range(k, len(items)):
            j = self.randint(0, i)
            if j < k:
                result[j] = items[i]
        
        return result
    
    def set_linear_progression(self, step: float = 0.01) -> None:
        """Set linear progression step size"""
        self._linear_step = max(0.001, min(0.5, step))
    
    def get_entropy_quality(self) -> Dict[str, Any]:
        """Get information about randomness quality"""
        # Check if we can access OS entropy
        try:
            with open('/dev/urandom', 'rb') as f:
                test_bytes = f.read(16)
            os_entropy_available = len(test_bytes) == 16
        except:
            os_entropy_available = False
        
        # Check weight history diversity
        weight_diversity = 0.0
        if len(self._weight_history) >= 10:
            unique_weights = len(set(round(w, 2) for w in self._weight_history))
            weight_diversity = unique_weights / len(self._weight_history)
        
        return {
            "mode": self.mode,
            "deterministic": self.mode == RandomMode.DETERMINISTIC,
            "os_entropy_available": os_entropy_available,
            "weight_history_size": len(self._weight_history),
            "weight_diversity": round(weight_diversity, 3),
            "linear_step": self._linear_step if self.mode == RandomMode.LINEAR else None
        }


# Global random source (secure by default)
_global_rng = RandomSource()


def get_global_rng() -> RandomSource:
    """Get the global random source"""
    return _global_rng


def set_global_seed(seed: Optional[str] = None, mode: RandomMode = RandomMode.SECURE):
    """Set global random seed and mode"""
    global _global_rng
    _global_rng = RandomSource(seed=seed, mode=mode)


def get_session_rng(session_id: str) -> RandomSource:
    """
    Get a random source for a specific session.
    Creates deterministic but unique randomness per session.
    """
    session_hash = hashlib.sha256(session_id.encode()).hexdigest()[:16]
    return RandomSource(seed=f"session_{session_hash}", mode=RandomMode.DETERMINISTIC)


def get_weighted_random(
    items: List[Any],
    base_weights: Optional[List[float]] = None,
    bias: float = 0.0,
    non_linear: bool = True
) -> Any:
    """Get item with weighted non-linear probability"""
    if not items:
        raise ValueError("No items to choose from")
    
    rng = get_global_rng()
    
    # Default to equal weights
    if base_weights is None:
        base_weights = [1.0] * len(items)
    
    if len(base_weights) != len(items):
        raise ValueError("Weights must match items length")
    
    # Apply bias for non-linear distribution
    if non_linear and bias > 0:
        transformed = [w ** (1.0 + bias) for w in base_weights]
    else:
        transformed = base_weights.copy()
    
    # Normalize
    total = sum(transformed)
    if total <= 0:
        return rng.choice(items)
    
    normalized = [w / total for w in transformed]
    
    return rng.choice(items, normalized)
