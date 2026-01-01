# 🎭 DM Personas Guide

The **Dungeon Master** can switch personalities live, changing the entire tone of the narrative experience.

## The 4 Voices

### 🏰 Classic Fantasy
**Voice:** Alloy  
**Tone:** Warm, heroic, vivid  
**Best for:** Traditional fantasy, D&D, Pathfinder

*Example:*
> "You stand before an ancient oak door, carved with intricate runes of power. The air grows cold. As your hand touches the wood, a faint pulse of magic thrums beneath your fingertips. What do you do?"

**Why players love it:** Immersive, descriptive, feels like a professional game master.

---

### 🌑 Gothic Horror
**Voice:** Echo  
**Tone:** Brooding, ominous, dread-filled  
**Best for:** Ravenloft, Call of Cthulhu, dark fantasy

*Example:*
> "The shadows lengthen unnaturally. Something moves in the fog—something that breathes hunger. You hear it before you see it: the wet, dragging sound of flesh across stone. Your heart hammers."

**Why players love it:** Creates genuine tension. Whispered warnings hit different.

---

### ✨ Whimsical
**Voice:** Fable  
**Tone:** Playful, punny, cheerful  
**Best for:** Family games, lighthearted campaigns, comedy

*Example:*
> "Oh my stars! A mischievous goblin pops out from behind the mushroom, wearing a tiny hat that's far too big. 'You can't pass without answering my riddle!' it squeaks. 'What has roots nobody sees?'"

**Why players love it:** Keeps the table laughing. Perfect for casual nights.

---

### 🤖 Sci-Fi Overseer
**Voice:** Onyx  
**Tone:** Detached, clinical, authoritative  
**Best for:** Cyberpunk, space opera, hard sci-fi

*Example:*
> "Anomaly detected. Hostile entity approaching, sector 7G. Your neural implant flashes red—three contacts, signature unknown. Recommendations: fall back or engage. Decision?"

**Why players love it:** Feels like commanding a spaceship or hacking reality itself.

---

## How to Switch Personas

**Host only:**
1. Look at the **Persona Selector** dropdown on your device
2. Click and choose: Classic, Gothic, Whimsical, or Sci-Fi
3. Everyone hears the change instantly
4. Next narration uses the new voice

**Mid-session switching works great for:**
- Dramatic mood shifts ("The shadows close in..." → Gothic)
- Comic relief ("A wise old turkey waddles in..." → Whimsical)
- Faction NPCs (different persona per enemy group)

---

## Mixing Personas Across a Campaign

Try this structure for variety:

| Act              | Persona        | Reason                           |
|------------------|----------------|----------------------------------|
| Tavern intro     | Classic        | Establish the world              |
| Dungeon descent  | Gothic         | Build tension                    |
| Absurd encounter | Whimsical      | Comic relief                     |
| Final boss lair  | Gothic         | Return to dread                  |

---

## Technical Notes

- Each persona has its own **system prompt** (guides tone)
- Each persona maps to an **OpenAI voice** (alloy, echo, fable, onyx)
- Switching is **instant** (no loading delays)
- All narrations are **personalized** to the active player's action

See [server/llm.py](server/llm.py#L1) for persona definitions.
