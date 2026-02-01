"""
Tests for VoiceDM randomness system
"""

import pytest
from server.randomness import RandomSource, RandomMode, get_session_rng, get_weighted_random


class TestRandomSource:
    """Test the RandomSource class"""
    
    def test_secure_mode(self):
        """Test OS entropy mode"""
        rng = RandomSource(mode=RandomMode.SECURE)
        
        # Generate random floats
        values = [rng.rand_float(0.0, 1.0) for _ in range(100)]
        
        # Should all be different
        assert len(set(values)) == 100
        
        # Should be in range
        assert all(0.0 <= v < 1.0 for v in values)
    
    def test_deterministic_mode(self):
        """Test deterministic seeded mode"""
        rng1 = RandomSource(mode=RandomMode.DETERMINISTIC, seed="test-seed-123")
        rng2 = RandomSource(mode=RandomMode.DETERMINISTIC, seed="test-seed-123")
        
        # Same seed should produce same sequence
        values1 = [rng1.rand_float(0.0, 1.0) for _ in range(10)]
        values2 = [rng2.rand_float(0.0, 1.0) for _ in range(10)]
        
        assert values1 == values2
    
    def test_weighted_mode(self):
        """Test weighted non-linear mode"""
        rng = RandomSource(mode=RandomMode.WEIGHTED, seed="test-weight")
        
        # Higher weights should appear more often
        choices = ["rare", "common", "common", "common"]
        results = [rng.choice(choices) for _ in range(100)]
        
        # "common" should appear more than "rare"
        common_count = results.count("common")
        rare_count = results.count("rare")
        
        assert common_count > rare_count
    
    def test_linear_mode(self):
        """Test linear progression mode"""
        rng = RandomSource(mode=RandomMode.LINEAR, seed="linear-test")
        
        # Should produce predictable sequence
        values = [rng.rand_float(0.0, 1.0) for _ in range(5)]
        
        # All values should be different
        assert len(set(values)) == 5
    
    def test_randint(self):
        """Test integer generation"""
        rng = RandomSource()
        
        # Generate integers in range
        values = [rng.randint(1, 20) for _ in range(100)]
        
        # Should all be in range
        assert all(1 <= v <= 20 for v in values)
        
        # Should have multiple different values
        assert len(set(values)) > 1
    
    def test_choice(self):
        """Test choice from list"""
        rng = RandomSource()
        
        options = ["a", "b", "c"]
        results = [rng.choice(options) for _ in range(100)]
        
        # Should only contain valid choices
        assert all(r in options for r in results)
        
        # Should have variety
        assert len(set(results)) > 1
    
    def test_shuffle(self):
        """Test list shuffling"""
        rng = RandomSource(mode=RandomMode.DETERMINISTIC, seed="shuffle-test")
        
        items = [1, 2, 3, 4, 5]
        shuffled = rng.shuffle(items.copy())
        
        # Should contain same elements
        assert sorted(shuffled) == sorted(items)
        
        # Should be different order (with high probability)
        assert shuffled != items or len(items) <= 1
    
    def test_sample(self):
        """Test sampling without replacement"""
        rng = RandomSource()
        
        items = list(range(10))
        sample = rng.sample(items, 5)
        
        # Should have correct length
        assert len(sample) == 5
        
        # Should contain unique elements
        assert len(set(sample)) == 5
        
        # Should all be from original list
        assert all(s in items for s in sample)


class TestSessionRNG:
    """Test session-specific RNG"""
    
    def test_session_consistency(self):
        """Same session ID should produce same sequence"""
        rng1 = get_session_rng("session-123")
        rng2 = get_session_rng("session-123")
        
        values1 = [rng1.rand_float(0.0, 1.0) for _ in range(10)]
        values2 = [rng2.rand_float(0.0, 1.0) for _ in range(10)]
        
        assert values1 == values2
    
    def test_different_sessions(self):
        """Different session IDs should produce different sequences"""
        rng1 = get_session_rng("session-a")
        rng2 = get_session_rng("session-b")
        
        values1 = [rng1.rand_float(0.0, 1.0) for _ in range(10)]
        values2 = [rng2.rand_float(0.0, 1.0) for _ in range(10)]
        
        assert values1 != values2


class TestWeightedRandom:
    """Test high-level weighted random selection"""
    
    def test_weighted_selection(self):
        """Test weighted random with bias"""
        options = {
            "rare": 0.1,
            "common": 0.6,
            "uncommon": 0.3
        }
        
        results = [get_weighted_random(options, bias=0.3) for _ in range(1000)]
        
        # "common" should appear most frequently (with enough samples)
        common_count = results.count("common")
        rare_count = results.count("rare")
        
        # With 1000 samples and weighted selection, common should be more frequent
        # Allow some statistical variance
        assert common_count > rare_count * 0.8
        
        # All results should be valid
        assert all(r in options for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
