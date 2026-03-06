from enum import Enum
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings

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


class Config(BaseSettings):
    # Database
    DATABASE_URL: str = Field(default="sqlite:///./voicedm.db", description="Database connection URL")

    # Randomness
    RANDOMNESS_MODE: Literal["secure", "det", "weighted", "linear"] = Field(
        default="secure", description="Randomness generation mode"
    )
    RANDOMNESS_SEED: Optional[str] = Field(default=None, description="Seed for deterministic mode")

    # Narration
    NARRATION_MODE: Literal["template", "hybrid", "llm"] = Field(
        default="template", description="Narration generation mode"
    )
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key for LLM narration")
    OLLAMA_URL: Optional[str] = Field(default="http://localhost:11434", description="Ollama server URL")

    # Server
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    LOG_LEVEL: Literal["debug", "info", "warning", "error"] = Field(
        default="info", description="Logging level"
    )

    # World Settings
    WORLD_TICK_INTERVAL: int = Field(
        default=3600, description="World tick interval in seconds (default: 1 hour)"
    )
    MAX_MODIFIER: int = Field(default=3, description="Maximum dice modifier")
    MIN_MODIFIER: int = Field(default=-3, description="Minimum dice modifier")

    class Config:
        env_file = ".env"
        case_sensitive = True


config = Config()

# Initialize global randomness based on config
try:
    from .randomness import set_global_seed
    if settings.randomness_mode == RandomMode.DETERMINISTIC and settings.randomness_seed:
        set_global_seed(seed=settings.randomness_seed, mode=RandomMode.DETERMINISTIC)
    else:
        set_global_seed(mode=settings.randomness_mode)
except ImportError:
    pass  # Randomness module not yet loaded
