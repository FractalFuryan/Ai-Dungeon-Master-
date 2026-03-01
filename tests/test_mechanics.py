from server.mechanics import DiceSystem, Governors, RandomnessMode, quick_resolve


def test_dice_caps():
    result = quick_resolve(5, [2, 2, 2, 2], [])
    assert result.modifier == 3

    result = quick_resolve(0, [], [2, 2, 2, 2])
    assert result.modifier == -3


def test_3d6_range():
    dice = DiceSystem(RandomnessMode.LINEAR)
    total, rolls = dice.roll_3d6()
    assert 3 <= total <= 18
    assert len(rolls) == 3


def test_2to1_anchor():
    assert not Governors.check_2_to_1_anchor(1)
    assert Governors.check_2_to_1_anchor(2)
    assert Governors.check_2_to_1_anchor(5)


def test_retirement_calculation():
    result = Governors.calculate_retirement_multiplier(1000, is_underdog=True)
    assert result["banked_xp"] == 1200
    assert result["legacy_features"] == 1

    result = Governors.calculate_retirement_multiplier(1000, is_gifted=True)
    assert result["banked_xp"] == 800
    assert result["legacy_features"] == 0

    result = Governors.calculate_retirement_multiplier(2500)
    assert result["banked_xp"] == 2500
    assert result["legacy_features"] == 2
