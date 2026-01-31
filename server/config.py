import os
from pydantic_settings import BaseSettings
from enum import Enum

class NarrationMode(str, Enum):
    TEMPLATE = "template"  # Pure templates, zero dependencies
    HYBRID = "hybrid"      # Templates + optional LLM polish
    LLM = "llm"           # Full LLM generation (legacy)

class Settings(BaseSettings):
    openai_api_key: str = ""  # Now optional
    openai_model: str = "gpt-4o-mini"
    default_persona: str = "classic"
    log_level: str = "INFO"
    narration_mode: NarrationMode = NarrationMode.TEMPLATE  # Default to no dependencies
    
    class Config:
        env_file = ".env"

settings = Settings()
