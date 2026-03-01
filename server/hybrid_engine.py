try:
    from .template_engine.config import Config
except ImportError:
    from template_engine.config import Config

# In _try_llm_polish
try:
    from .llm import LLM
except ImportError:
    from llm import LLM

class NarrationMode:
    class LLM:
        try:
            from .llm import LLM
        except ImportError:
            from llm import LLM
        
    # Rest of your class implementation goes here...