#!/usr/bin/env python3
"""
Demo: VoiceDM Randomness & Dice Systems

Shows all features in action with zero dependencies.
"""

from server.randomness import RandomSource, RandomMode, get_session_rng, get_weighted_random
from server.dice import DiceSystem, quick_roll


def demo_randomness_modes():
    """Demonstrate all 4 randomness modes"""
    print("=" * 60)
    print("RANDOMNESS MODES DEMO")
    print("=" * 60)
    
    # 1. SECURE mode (default)
    print("\n1. SECURE MODE (OS Entropy)")
    print("-" * 60)
    rng = RandomSource(mode=RandomMode.SECURE)
    print(f"Three d20 rolls: {[rng.randint(1, 20) for _ in range(3)]}")
    print("✓ Cryptographically secure, non-predictable")
    
    # 2. DETERMINISTIC mode
    print("\n2. DETERMINISTIC MODE (Seeded)")
    print("-" * 60)
    rng1 = RandomSource(mode=RandomMode.DETERMINISTIC, seed="demo-seed")
    rng2 = RandomSource(mode=RandomMode.DETERMINISTIC, seed="demo-seed")
    rolls1 = [rng1.randint(1, 20) for _ in range(3)]
    rolls2 = [rng2.randint(1, 20) for _ in range(3)]
    print(f"RNG 1: {rolls1}")
    print(f"RNG 2: {rolls2}")
    print(f"✓ Identical: {rolls1 == rolls2}")
    
    # 3. WEIGHTED mode
    print("\n3. WEIGHTED MODE (Non-linear)")
    print("-" * 60)
    rng = RandomSource(mode=RandomMode.WEIGHTED)
    options = ["rare", "common", "common", "common"]
    results = [rng.choice(options) for _ in range(20)]
    common_count = results.count("common")
    rare_count = results.count("rare")
    print(f"20 rolls: common={common_count}, rare={rare_count}")
    print(f"✓ Weighted distribution favors 'common'")
    
    # 4. LINEAR mode
    print("\n4. LINEAR MODE (Predictable)")
    print("-" * 60)
    rng = RandomSource(mode=RandomMode.LINEAR, seed="linear-demo")
    values = [round(rng.rand_float(0.0, 10.0), 2) for _ in range(5)]
    print(f"Evenly spaced values: {values}")
    print("✓ Predictable progression")


def demo_dice_rolling():
    """Demonstrate dice rolling features"""
    print("\n" + "=" * 60)
    print("DICE ROLLING DEMO")
    print("=" * 60)
    
    # Basic rolls
    print("\n1. BASIC ROLLS")
    print("-" * 60)
    for expr in ["d20", "2d6", "3d8+2", "d12-1"]:
        result = quick_roll(expr)
        print(f"{expr:12} = {result.total:3} {result.rolls}")
    
    # Advantage/Disadvantage
    print("\n2. ADVANTAGE & DISADVANTAGE")
    print("-" * 60)
    adv = quick_roll("d20 advantage")
    print(f"Advantage:    rolls={adv.rolls}, result={max(adv.rolls)} (higher)")
    dis = quick_roll("d20 disadvantage")
    print(f"Disadvantage: rolls={dis.rolls}, result={min(dis.rolls)} (lower)")
    
    # Critical detection
    print("\n3. CRITICAL DETECTION")
    print("-" * 60)
    dice = DiceSystem(session_id="crit-demo")
    print("Rolling d20 until we get a critical...")
    for i in range(100):
        result = dice.roll("d20")
        if result.metadata.get("critical"):
            crit_type = result.metadata["critical_type"]
            print(f"  Roll #{i+1}: {result.total} - {crit_type.upper()}!")
            if crit_type == "success":
                break
    
    # Roll history
    print("\n4. ROLL HISTORY")
    print("-" * 60)
    dice = DiceSystem()
    dice.roll("d20")
    dice.roll("2d6+3")
    dice.roll("4d6")
    print("Last 3 rolls:")
    for roll in dice.get_history(limit=3):
        print(f"  {roll.expression:10} = {roll.total:3} (avg: {roll.average:.1f})")


def demo_session_rng():
    """Demonstrate session-specific RNG"""
    print("\n" + "=" * 60)
    print("SESSION-SPECIFIC RNG DEMO")
    print("=" * 60)
    
    # Campaign A
    print("\nCampaign A (session: alpha)")
    dice_a = DiceSystem(session_id="alpha")
    rolls_a = [dice_a.roll("d20").total for _ in range(5)]
    print(f"  Rolls: {rolls_a}")
    
    # Campaign B
    print("\nCampaign B (session: beta)")
    dice_b = DiceSystem(session_id="beta")
    rolls_b = [dice_b.roll("d20").total for _ in range(5)]
    print(f"  Rolls: {rolls_b}")
    
    # Replay Campaign A
    print("\nReplay Campaign A (session: alpha)")
    replay_a = DiceSystem(session_id="alpha")
    replay_rolls = [replay_a.roll("d20").total for _ in range(5)]
    print(f"  Rolls: {replay_rolls}")
    print(f"  ✓ Identical to first run: {rolls_a == replay_rolls}")


def demo_weighted_selection():
    """Demonstrate weighted random selection"""
    print("\n" + "=" * 60)
    print("WEIGHTED SELECTION DEMO")
    print("=" * 60)
    
    # Encounter table
    print("\nRandom Encounter Table:")
    encounters = {
        "Goblin Patrol": 0.5,
        "Orc Warband": 0.3,
        "Ancient Dragon": 0.05,
        "Treasure Hoard": 0.15
    }
    
    print("Weights:")
    for name, weight in encounters.items():
        print(f"  {name:20} {weight:5.0%}")
    
    print("\n10 Random Encounters:")
    for i in range(10):
        encounter = get_weighted_random(encounters, bias=0.3)
        print(f"  {i+1:2}. {encounter}")
    
    # Count distribution over many rolls
    print("\nDistribution over 1000 encounters:")
    results = [get_weighted_random(encounters, bias=0.3) for _ in range(1000)]
    for name in encounters:
        count = results.count(name)
        print(f"  {name:20} {count:4} ({count/10:.1f}%)")


def demo_statistics():
    """Show dice statistics"""
    print("\n" + "=" * 60)
    print("STATISTICS DEMO")
    print("=" * 60)
    
    result = quick_roll("5d6+10")
    
    print(f"\nRoll: {result.expression}")
    print("-" * 60)
    print(f"Individual rolls: {result.rolls}")
    print(f"Total:            {result.total}")
    print(f"Average roll:     {result.average:.2f}")
    print(f"Min roll:         {result.min_roll}")
    print(f"Max roll:         {result.max_roll}")
    print(f"Dice used:        {len(result.rolls)}d{result.faces[0]}")
    
    # Serialization
    print("\nSerialized (JSON-ready):")
    import json
    print(json.dumps(result.to_dict(), indent=2))


def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  VoiceDM Randomness & Dice Systems Demo".center(58) + "║")
    print("║" + "  Zero Dependencies | <1ms Response | Featherweight".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    demo_randomness_modes()
    demo_dice_rolling()
    demo_session_rng()
    demo_weighted_selection()
    demo_statistics()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\n✓ All features demonstrated")
    print("✓ Zero external dependencies")
    print("✓ Stdlib only (secrets, hashlib, re)")
    print("✓ Production-ready")
    print("\nSee RANDOMNESS_GUIDE.md for full documentation.\n")


if __name__ == "__main__":
    main()
