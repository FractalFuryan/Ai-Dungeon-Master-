import random

def roll_dice(dice_type: str, modifier: int = 0) -> dict:
    if dice_type == "d20":
        roll = random.randint(1, 20)
    else:
        raise ValueError("Unsupported dice")
    total = roll + modifier
    return {"roll": roll, "total": total, "logged": True}
