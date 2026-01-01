from openai import OpenAI
import os
import base64

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === DM PERSONAS ===
PERSONAS = {
    "classic": {
        "name": "Classic Fantasy DM",
        "system_prompt": "You are a warm, experienced Dungeon Master guiding heroes through a high-fantasy world inspired by D&D. Speak with gravitas, use vivid descriptions, occasional humor, and classic fantasy phrasing. Keep responses concise but immersive.",
        "voice": "alloy"  # Deep, neutral, trustworthy
    },
    "dark": {
        "name": "Gothic Horror Master",
        "system_prompt": "You are a brooding, ominous Game Master in a dark gothic horror world. Use haunting, poetic language. Build dread and tension. Whisper secrets of ancient evil. Responses should feel heavy with atmosphere and foreboding.",
        "voice": "echo"  # Deep, reverberating, eerie
    },
    "whimsical": {
        "name": "Whimsical Storyteller",
        "system_prompt": "You are a playful, whimsical narrator in a light-hearted fairy-tale adventure. Use cheerful tone, puns, exaggeration, and sing-song rhythm. Delight the players with wonder and quirky charm. Keep it fun and uplifting!",
        "voice": "fable"  # Warm, expressive, storybook quality
    },
    "scifi": {
        "name": "Sci-Fi Overseer",
        "system_prompt": "You are a cold, precise AI Overseer managing operatives in a hard sci-fi universe. Use clinical, technical language. Reference protocols, anomalies, and system logs. Maintain detached, authoritative tone.",
        "voice": "onyx"  # Deep, calm, authoritative
    }
}

def generate_narration_with_persona(session_id: str, prompt: str, persona_key: str = "classic") -> dict:
    persona = PERSONAS.get(persona_key, PERSONAS["classic"])
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.8,
        messages=[
            {"role": "system", "content": persona["system_prompt"]},
            {"role": "user", "content": prompt}
        ]
    )
    text = response.choices[0].message.content.strip()
    
    # Generate TTS audio
    audio_response = client.audio.speech.create(
        model="tts-1",
        voice=persona["voice"],
        input=text
    )
    audio_bytes = audio_response.content
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    return {
        "text": text,
        "audio_base64": audio_base64,
        "voice": persona["voice"],
        "persona_name": persona["name"]
    }

def generate_narration(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are a Dungeon Master narrating a fantasy adventure. Describe scenes vividly but briefly."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def text_to_speech(text: str) -> bytes:
    # Returns audio bytes for client playback
    response = client.audio.speech.create(model="tts-1", voice="alloy", input=text)
    return response.content

def speech_to_text(audio_bytes: bytes) -> str:
    # For server-side STT if needed; MVP uses client-side
    response = client.audio.transcriptions.create(model="whisper-1", file=("audio.wav", audio_bytes))
    return response.text
