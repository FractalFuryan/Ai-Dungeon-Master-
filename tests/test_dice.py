"""
Tests for VoiceDM dice system
"""

import pytest
from server.dice import DiceSystem, quick_roll, RollMode


class TestDiceSystem:
    """Test the DiceSystem class"""
    
    def test_single_die(self):
        """Test rolling a single die"""
        dice = DiceSystem()
        result = dice.roll("d20")
        
        assert 1 <= result.total <= 20
        assert len(result.rolls) == 1
        assert result.faces[0] == 20
    
    def test_multiple_dice(self):
        """Test rolling multiple dice"""
        dice = DiceSystem()
        result = dice.roll("3d6")
        
        assert 3 <= result.total <= 18
        assert len(result.rolls) == 3
        assert all(f == 6 for f in result.faces)
    
    def test_modifier(self):
        """Test dice with modifier"""
        dice = DiceSystem()
        result = dice.roll("d20+5")
        
        assert 6 <= result.total <= 25
        assert len(result.rolls) == 1
    
    def test_negative_modifier(self):
        """Test dice with negative modifier"""
        dice = DiceSystem()
        result = dice.roll("d20-2")
        
        assert -1 <= result.total <= 18
        assert len(result.rolls) == 1
    
    def test_advantage(self):
        """Test rolling with advantage"""
        dice = DiceSystem()
        result = dice.roll("d20 advantage")
        
        assert result.mode == RollMode.ADVANTAGE
        assert len(result.rolls) == 2
        assert result.total == max(result.rolls)
    
    def test_disadvantage(self):
        """Test rolling with disadvantage"""
        dice = DiceSystem()
        result = dice.roll("d20 disadvantage")
        
        assert result.mode == RollMode.DISADVANTAGE
        assert len(result.rolls) == 2
        assert result.total == min(result.rolls)
    
    def test_critical_success(self):
        """Test critical success detection"""
        dice = DiceSystem(session_id="test-crit-success")
        
        # Roll many times to get a critical
        criticals = []
        for _ in range(100):
            result = dice.roll("d20")
            if 20 in result.rolls:
                criticals.append(result)
        
        # Should have some criticals
        assert len(criticals) > 0
        
        # Check metadata
        for crit in criticals:
            assert crit.metadata.get("critical") is True
            assert crit.metadata.get("critical_type") == "success"
    
    def test_critical_failure(self):
        """Test critical failure detection"""
        dice = DiceSystem(session_id="test-crit-fail")
        
        # Roll many times to get a critical failure
        failures = []
        for _ in range(100):
            result = dice.roll("d20")
            if 1 in result.rolls:
                failures.append(result)
        
        # Should have some failures
        assert len(failures) > 0
        
        # Check metadata
        for fail in failures:
            assert fail.metadata.get("critical") is True
            assert fail.metadata.get("critical_type") == "failure"
    
    def test_roll_history(self):
        """Test roll history tracking"""
        dice = DiceSystem()
        
        # Make several rolls
        dice.roll("d20")
        dice.roll("2d6+3")
        dice.roll("d12")
        
        history = dice.get_history()
        assert len(history) == 3
        
        # Check history limit
        for _ in range(20):
            dice.roll("d6")
        
        history = dice.get_history(limit=5)
        assert len(history) == 5
    
    def test_statistics(self):
        """Test result statistics"""
        dice = DiceSystem()
        result = dice.roll("3d6")
        
        assert result.average == sum(result.rolls) / len(result.rolls)
        assert result.min_roll == min(result.rolls)
        assert result.max_roll == max(result.rolls)
    
    def test_to_dict(self):
        """Test serialization to dictionary"""
        dice = DiceSystem()
        result = dice.roll("2d6+3")
        
        data = result.to_dict()
        
        assert "expression" in data
        assert "total" in data
        assert "rolls" in data
        assert "faces" in data
        assert "statistics" in data
        assert "metadata" in data


class TestQuickRoll:
    """Test the quick_roll helper"""
    
    def test_quick_roll(self):
        """Test quick roll without DiceSystem instance"""
        result = quick_roll("d20")
        
        assert 1 <= result.total <= 20
        assert len(result.rolls) == 1
    
    def test_quick_roll_session(self):
        """Test quick roll with session ID"""
        result1 = quick_roll("d20", session_id="test-session")
        result2 = quick_roll("d20", session_id="test-session")
        
        # Same session should produce same result
        assert result1.total == result2.total


class TestDiceExpressions:
    """Test various dice expressions"""
    
    def test_standard_dice(self):
        """Test standard RPG dice"""
        expressions = ["d4", "d6", "d8", "d10", "d12", "d20", "d100"]
        
        for expr in expressions:
            result = quick_roll(expr)
            sides = int(expr[1:])
            assert 1 <= result.total <= sides
    
    def test_complex_expressions(self):
        """Test complex dice expressions"""
        expressions = [
            "2d6+3",
            "3d8-2",
            "d20+5",
            "4d6",
            "d20 advantage",
            "d20 disadvantage"
        ]
        
        for expr in expressions:
            result = quick_roll(expr)
            assert result.total > 0 or "-" in expr
    
    def test_invalid_expression(self):
        """Test invalid dice expression"""
        with pytest.raises(ValueError):
            quick_roll("invalid")
        
        with pytest.raises(ValueError):
            quick_roll("2x6")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
