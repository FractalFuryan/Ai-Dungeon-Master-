import os
from pydantic_settings import BaseSettings
from enum import Enum

try:
    from .randomness import RandomMode
except ImportError:
    # Define locally if randomness module not yet loaded
    class RandomMode(str, Enum):
        SECURE = "secure"
        DETERMINISTIC = "deterministic"
        WEIGHTED = "weighted"
        LINEAR = "linear"

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
    randomness_mode: RandomMode = RandomMode.SECURE  # Default to OS entropy
    randomness_seed: str = ""  # Only used for deterministic mode
    non_linear_bias: float = 0.3  # 0=linear, 1=highly non-linear
    
    class Config:
        env_file = ".env"

settings = Settings()

# Initialize global randomness based on config
try:
    from .randomness import set_global_seed
    if settings.randomness_mode == RandomMode.DETERMINISTIC and settings.randomness_seed:
        set_global_seed(seed=settings.randomness_seed, mode=RandomMode.DETERMINISTIC)
    else:
        set_global_seed(mode=settings.randomness_mode)
except ImportError:
    pass  # Randomness module not yet loaded
