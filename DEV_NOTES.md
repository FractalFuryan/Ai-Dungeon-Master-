# Dev Notes

- LLM: In llm.py, swap OpenAI for Grok/Anthropic if needed.
- Memory: Currently in-memory dict; upgrade to Redis for persistence.
- Voice: Uses browser SpeechRecognition/SpeechSynthesis for client-side STT/TTS. Fallback to server if needed.
- Turns: Add in dm_engine.py with state machine.
- Personas: Extend dm_engine with presets.
