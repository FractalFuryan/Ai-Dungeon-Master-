"""
Template-based narrative engine - Zero dependencies, deterministic output

Design Philosophy:
- Reasoning is deterministic (already handled by frame_engine.py)
- Language is optional (this module provides it without ML)
- Templates are composable, not scripted
- Surprise comes from structure, not linguistics
"""
import random
from typing import Dict, List, Tuple

# Expanded template library with tone variations
TEMPLATE_LIBRARY = {
    "straight": {
        "description": "The action proceeds as expected",
        "tones": {
            "classic": {
                "atmosphere": [
                    "Your action unfolds with predictable precision.",
                    "The world responds to your choice without surprise.",
                    "Events transpire as one might reasonably expect."
                ],
                "consequence": [
                    "The situation stabilizes, leaving you in control.",
                    "You achieve what you set out to do, cleanly.",
                    "Success is yours, but without flourish or fanfare."
                ],
                "options": [
                    "Press the advantage while you can",
                    "Take a moment to assess your position",
                    "Reinforce what you've established",
                    "Move cautiously to the next challenge"
                ]
            },
            "gothic": {
                "atmosphere": [
                    "Your action unfolds beneath a heavy, watchful silence.",
                    "The world yields to your will, but grudgingly.",
                    "What transpires feels inevitable, almost predestined."
                ],
                "consequence": [
                    "You succeed, but the shadows seem deeper now.",
                    "Victory tastes of dust and old stones.",
                    "The outcome is yours, yet something feels incomplete."
                ],
                "options": [
                    "Proceed deeper into the gloom",
                    "Question what was truly gained",
                    "Listen for what follows success",
                    "Steel yourself for the cost"
                ]
            },
            "whimsical": {
                "atmosphere": [
                    "Your action proceeds like a well-rehearsed dance!",
                    "The world responds with cheerful cooperation.",
                    "Everything happens just as you imagined it would."
                ],
                "consequence": [
                    "Success arrives with a pleasant little chime.",
                    "You accomplish your goal, and the air feels lighter.",
                    "All is well, and perhaps a bit sparklier than before."
                ],
                "options": [
                    "Celebrate with a happy twirl",
                    "See what else wants to cooperate",
                    "Share the success with someone nearby",
                    "Skip merrily to the next adventure"
                ]
            },
            "scifi": {
                "atmosphere": [
                    "Your action executes within expected parameters.",
                    "The system responds with algorithmic precision.",
                    "Causality unfolds along predictable pathways."
                ],
                "consequence": [
                    "Objective achieved. Efficiency: 94.7%",
                    "The desired outcome materializes without anomaly.",
                    "Success registers in the event log."
                ],
                "options": [
                    "Proceed to next operational phase",
                    "Run diagnostics on the outcome",
                    "Optimize the approach for future iterations",
                    "Update mission parameters"
                ]
            }
        }
    },
    
    "unexpected_ally": {
        "description": "Help arrives from an unexpected quarter",
        "tones": {
            "classic": {
                "atmosphere": [
                    "From the edge of perception, a new presence makes itself known.",
                    "An unexpected figure steps forward, drawn by your actions.",
                    "You are not alone in this moment.",
                    "Fortune brings an unforeseen companion to your side."
                ],
                "consequence": [
                    "The balance shifts, but intentions remain unclear.",
                    "An opportunity presents itself, wrapped in mystery.",
                    "Your path forward now includes another's shadow.",
                    "Aid arrives from a quarter you didn't anticipate."
                ],
                "options": [
                    "Greet the newcomer warily",
                    "Test their allegiance through action",
                    "Accept the aid but keep distance",
                    "Ask what brings them to your cause"
                ]
            },
            "gothic": {
                "atmosphere": [
                    "From the shadows, a form detaches itself—neither hostile nor friendly.",
                    "Something that was watching now chooses to be seen.",
                    "The dark yields a companion you did not invite.",
                    "A figure emerges from the gloom, drawn by necessity or design."
                ],
                "consequence": [
                    "The geometry of power shifts in unsettling ways.",
                    "You gain an advantage that feels like a debt.",
                    "Help arrives wearing a stranger's face.",
                    "The price of this aid remains unspoken."
                ],
                "options": [
                    "Demand to know its nature",
                    "Use the aid but trust nothing",
                    "Withdraw from the offered hand",
                    "Accept the alliance with eyes open"
                ]
            },
            "whimsical": {
                "atmosphere": [
                    "A cheerful stranger pops into view with perfect timing!",
                    "Just when you needed it most, help arrives unannounced.",
                    "Someone new joins the adventure, smiling brightly.",
                    "A friendly face appears, as if summoned by good fortune!"
                ],
                "consequence": [
                    "The situation brightens with unexpected friendship.",
                    "A new possibility dances into existence.",
                    "Things just got more interesting and fun!",
                    "Your party grows by one delightful addition."
                ],
                "options": [
                    "Welcome them with open arms",
                    "Ask what brought them here",
                    "Include them in your next move",
                    "Share stories and become friends"
                ]
            },
            "scifi": {
                "atmosphere": [
                    "An unidentified entity enters operational vicinity.",
                    "Sensors detect non-hostile intervention from unknown origin.",
                    "Third-party engagement initiated without prior authorization.",
                    "Auxiliary unit materializes in tactical space."
                ],
                "consequence": [
                    "Tactical probabilities recalculated with new variable.",
                    "Mission parameters expanded to include auxiliary actor.",
                    "Assistance rendered; motives unconfirmed.",
                    "Alliance coefficient fluctuates in positive range."
                ],
                "options": [
                    "Query the entity's designation",
                    "Integrate aid into current objective",
                    "Maintain defensive protocols while observing",
                    "Establish communication protocols"
                ]
            }
        }
    },
    
    "hidden_cost": {
        "description": "Success comes with an unexpected price",
        "tones": {
            "classic": {
                "atmosphere": [
                    "Victory is achieved, but at a subtle toll.",
                    "The cost of success reveals itself only after the fact.",
                    "You gain what you sought, but lose what you didn't know you had.",
                    "The price paid emerges from the shadows of triumph."
                ],
                "consequence": [
                    "The price paid changes the nature of the victory.",
                    "What was won feels different in your hands now.",
                    "Success arrives wearing the clothes of sacrifice.",
                    "Something precious slips away in the moment of triumph."
                ],
                "options": [
                    "Investigate what was truly lost",
                    "Accept the cost and continue forward",
                    "Attempt to reverse or mitigate the damage",
                    "Weigh whether the price was worth paying"
                ]
            },
            "gothic": {
                "atmosphere": [
                    "The price of your success whispers from the edges.",
                    "What you gained is now stained with consequence.",
                    "Victory tastes of ash and forgotten promises.",
                    "In winning, you've paid with a coin you didn't know you carried."
                ],
                "consequence": [
                    "The cost exacts itself in silent, personal currency.",
                    "You've won, but something essential has been altered.",
                    "Success arrives hand-in-hand with irreversible change.",
                    "The shadows claim their due, as they always do."
                ],
                "options": [
                    "Trace the cost to its source",
                    "Embrace the sacrifice as necessary",
                    "Search for redemption in the aftermath",
                    "Accept the darkness that comes with power"
                ]
            },
            "whimsical": {
                "atmosphere": [
                    "You win! But wait... something's missing.",
                    "Success! Though it came at an unexpected little cost.",
                    "Hooray! Except for that one tiny detail...",
                    "Victory! And also a small oopsie on the side."
                ],
                "consequence": [
                    "You got what you wanted, but also lost something dear.",
                    "The win comes with a bittersweet surprise.",
                    "Success arrived, but it brought along a little sadness.",
                    "You're ahead, but your pockets feel lighter."
                ],
                "options": [
                    "Try to get back what was lost",
                    "Shrug it off and stay cheerful",
                    "Learn from the experience",
                    "Make the best of the situation"
                ]
            },
            "scifi": {
                "atmosphere": [
                    "Objective complete. Warning: unintended resource depletion detected.",
                    "Mission success confirmed. Anomaly: unexpected system degradation.",
                    "Target achieved at cost of secondary parameters.",
                    "Primary goal reached. Collateral impact: significant."
                ],
                "consequence": [
                    "The victory exacts a toll on ship's integrity.",
                    "Success logged. Cost assessment: higher than projected.",
                    "Mission viable, but auxiliary systems compromised.",
                    "Achievement unlocked. Price: quantifiable loss."
                ],
                "options": [
                    "Run full diagnostic on losses",
                    "Proceed despite degradation",
                    "Initiate damage control protocols",
                    "Reassess cost-benefit ratio"
                ]
            }
        }
    },
    
    "moral_inversion": {
        "description": "The situation reveals an ethical complication",
        "tones": {
            "classic": {
                "atmosphere": [
                    "The moral landscape shifts beneath your feet.",
                    "What seemed clear now reveals troubling complexity.",
                    "The right action wears an unexpected face.",
                    "Certainty gives way to difficult questions."
                ],
                "consequence": [
                    "Your certainty is replaced by ethical ambiguity.",
                    "The path forward is paved with moral nuance.",
                    "Clarity fractures into shades of grey.",
                    "What's just and what's necessary diverge."
                ],
                "options": [
                    "Reevaluate your position carefully",
                    "Choose the lesser of two complications",
                    "Seek counsel before proceeding",
                    "Stand by your principles despite doubt"
                ]
            },
            "gothic": {
                "atmosphere": [
                    "The line between hero and villain blurs in the darkness.",
                    "Your righteous action casts a shadow of its own.",
                    "Good and evil dance together in this moment.",
                    "The moral architecture of the world cracks and shifts."
                ],
                "consequence": [
                    "Your soul bears the weight of necessary evil.",
                    "Righteousness reveals its dark twin.",
                    "The cost of justice is paid in conscience.",
                    "You've become what you sought to prevent."
                ],
                "options": [
                    "Accept the darkness you've embraced",
                    "Seek absolution for necessary sins",
                    "Question everything you believed",
                    "Find meaning in the moral ruins"
                ]
            },
            "scifi": {
                "atmosphere": [
                    "Ethical subroutines encounter contradictory parameters.",
                    "The trolley problem manifests in real-time.",
                    "Moral calculus yields no clean solution.",
                    "Decision tree branches into ethical paradox."
                ],
                "consequence": [
                    "All outcomes violate some core directive.",
                    "The optimal choice is suboptimal for someone.",
                    "Logic fails where ethics and pragmatism intersect.",
                    "Mission parameters conflict with ethical protocols."
                ],
                "options": [
                    "Apply utilitarian calculation",
                    "Default to core ethical imperatives",
                    "Delay decision pending more data",
                    "Override ethics protocols (emergency only)"
                ]
            }
        }
    },
    
    "foreshadowing": {
        "description": "A hint of future events or deeper truths",
        "tones": {
            "classic": {
                "atmosphere": [
                    "A glimpse of what's to come shimmers at the edge of events.",
                    "The present moment contains echoes of future significance.",
                    "Something larger makes its presence subtly known.",
                    "Destiny whispers through the immediate outcome."
                ],
                "consequence": [
                    "Your action resonates with coming importance.",
                    "The immediate outcome whispers of grander patterns.",
                    "Success today feels like prologue to greater events.",
                    "A thread of fate reveals itself in the tapestry."
                ],
                "options": [
                    "Pursue the hinted revelation",
                    "Note the sign and continue your course",
                    "Prepare for what may be coming",
                    "Seek to understand the larger pattern"
                ]
            },
            "gothic": {
                "atmosphere": [
                    "The future casts its long shadow over the present.",
                    "What will be has already begun to shape what is.",
                    "The coming horror announces itself with subtle signs.",
                    "Fate's dark messenger delivers its cryptic warning."
                ],
                "consequence": [
                    "Your success feels like delay, not prevention.",
                    "The victory is real, but its context grows ominous.",
                    "You win a battle, but the war's nature changes.",
                    "What you've done has awakened something patient and vast."
                ],
                "options": [
                    "Heed the warning and change course",
                    "Arm yourself against what approaches",
                    "Seek to understand the coming threat",
                    "Deny the portent and press forward"
                ]
            },
            "whimsical": {
                "atmosphere": [
                    "A little sparkle hints at big adventures ahead!",
                    "Something wonderful is on its way, you can feel it!",
                    "The universe winks at you knowingly.",
                    "A mysterious promise glimmers in the air."
                ],
                "consequence": [
                    "Your success plants seeds for future excitement!",
                    "What you've done will matter in delightful ways later.",
                    "The story is just getting started, and it knows it!",
                    "Today's win is tomorrow's wonderful surprise."
                ],
                "options": [
                    "Get excited about what's coming",
                    "Keep an eye out for more hints",
                    "Prepare for grand adventures",
                    "Trust that good things await"
                ]
            },
            "scifi": {
                "atmosphere": [
                    "Long-term probability matrices spike unexpectedly.",
                    "The event horizon of causality ripples outward.",
                    "Temporal echoes suggest future-state importance.",
                    "Pattern recognition flags this moment as significant."
                ],
                "consequence": [
                    "Current actions register in deep timeline analysis.",
                    "The data suggests this is a branching point.",
                    "Causal chains extend beyond immediate observation.",
                    "System predicts elevated relevance in future states."
                ],
                "options": [
                    "Log the anomaly for future reference",
                    "Increase monitoring of related variables",
                    "Prepare contingencies for predicted outcomes",
                    "Analyze the causal pattern more deeply"
                ]
            }
        }
    },
    
    "lateral_escape": {
        "description": "A clever alternative to direct confrontation",
        "tones": {
            "classic": {
                "atmosphere": [
                    "An unconventional solution presents itself.",
                    "The problem yields to creativity rather than force.",
                    "A sideways approach succeeds where direct assault would fail.",
                    "Cleverness finds the path brute strength would miss."
                ],
                "consequence": [
                    "Your ingenuity opens an unexpected door.",
                    "The situation resolves through wit, not power.",
                    "A third option emerges from lateral thinking.",
                    "Success arrives via the path less obvious."
                ],
                "options": [
                    "Exploit the clever advantage gained",
                    "Apply this thinking to other challenges",
                    "Share the innovative approach",
                    "Build on the unconventional solution"
                ]
            },
            "gothic": {
                "atmosphere": [
                    "The shadows themselves suggest an alternative.",
                    "What cannot be faced can perhaps be circumvented.",
                    "The darkness offers passage to those who think obliquely.",
                    "Power yields where cunning finds purchase."
                ],
                "consequence": [
                    "You slip past the obstacle like smoke through fingers.",
                    "The direct path was a trap; the crooked way succeeds.",
                    "What was impossible becomes inevitable through guile.",
                    "Victory achieved through the wisdom of indirection."
                ],
                "options": [
                    "Follow the shadowed path further",
                    "Embrace the indirect approach",
                    "Question why the obvious way was blocked",
                    "Use cunning as your primary weapon"
                ]
            },
            "scifi": {
                "atmosphere": [
                    "Solution matrix identifies non-standard pathway.",
                    "Lateral algorithm bypasses primary obstacle.",
                    "The system rewards unconventional thinking.",
                    "Optimization achieved through parametric reframing."
                ],
                "consequence": [
                    "The challenge resolves via elegant workaround.",
                    "Efficiency gained through solution-space creativity.",
                    "Problem redefined until it became solvable.",
                    "Victory via cognitive flexibility protocols."
                ],
                "options": [
                    "Archive the solution for future reference",
                    "Apply the methodology systematically",
                    "Investigate why standard approach failed",
                    "Prioritize creative problem-solving"
                ]
            }
        }
    }
}

def get_tone_variants(frame_key: str) -> List[str]:
    """Get available tones for a given frame"""
    frame = TEMPLATE_LIBRARY.get(frame_key)
    if not frame:
        return ["classic"]
    return list(frame["tones"].keys())

def render_template(
    frame_key: str,
    tone: str = "classic",
    scene_context: str = "",
    player_action: str = "",
    imagination_signals: List[str] = None
) -> str:
    """
    Generate narrative from templates. Pure deterministic, zero ML.
    
    Args:
        frame_key: Narrative frame (e.g., "unexpected_ally")
        tone: Narrative style (classic, gothic, whimsical, scifi)
        scene_context: Current scene description (for context only)
        player_action: What the player just did (for context only)
        imagination_signals: Creative signals from player input (unused but available)
    
    Returns:
        Formatted narrative text with atmosphere + consequence + options
    """
    frame = TEMPLATE_LIBRARY.get(frame_key, TEMPLATE_LIBRARY["straight"])
    
    # Fallback to classic if tone not available
    tone_data = frame["tones"].get(tone)
    if not tone_data:
        # Try classic as fallback
        tone_data = frame["tones"].get("classic", list(frame["tones"].values())[0])
    
    # Select random elements for variety
    atmosphere = random.choice(tone_data["atmosphere"])
    consequence = random.choice(tone_data["consequence"])
    
    # Select 2-3 options randomly
    all_options = tone_data["options"].copy()
    random.shuffle(all_options)
    num_options = random.randint(2, min(3, len(all_options)))
    selected_options = all_options[:num_options]
    
    # Compose the narrative
    narrative = f"{atmosphere}\n\n{consequence}\n\n"
    narrative += "What do you do?\n"
    for i, option in enumerate(selected_options, 1):
        narrative += f"{i}. {option}\n"
    
    return narrative.strip()

def get_template_stats() -> Dict:
    """Get statistics about the template library"""
    total_frames = len(TEMPLATE_LIBRARY)
    total_tones = sum(len(f["tones"]) for f in TEMPLATE_LIBRARY.values())
    total_variations = sum(
        len(t["atmosphere"]) + len(t["consequence"]) + len(t["options"])
        for frame in TEMPLATE_LIBRARY.values()
        for t in frame["tones"].values()
    )
    
    return {
        "frames": total_frames,
        "tones": total_tones,
        "total_text_variations": total_variations,
        "estimated_unique_outputs": total_variations * 2,  # Conservative estimate
        "dependencies": 0,
        "model_size_mb": 0,
        "response_time_ms": "<1"
    }
