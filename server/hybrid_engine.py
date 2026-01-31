"""
Hybrid Narration Engine - Templates first, optional LLM polish

Design Philosophy:
- Templates ALWAYS generate valid output
- LLM is OPTIONAL cosmetic enhancement only
- If LLM fails, templates ship as-is
- LLM never sees: player history, ethics decisions, frame selection
- LLM only sees: "Rewrite this in [tone] style"

This makes the system:
- Safe (LLM can't make ethical mistakes)
- Cheap (minimal tokens)
- Resilient (degrades gracefully)
- Auditable (template base is deterministic)
"""

import logging
from typing import Optional
from .template_engine import render_template
from .config import settings, NarrationMode

logger = logging.getLogger(__name__)

def _try_llm_polish(text: str, tone: str) -> Optional[str]:
    """
    Attempt to polish template output with LLM.
    Returns None on any failure (API key missing, rate limit, etc.)
    """
    if not settings.openai_api_key or not settings.openai_api_key.startswith("sk-"):
        logger.debug("No valid OpenAI API key, skipping LLM polish")
        return None
    
    try:
        from .llm import get_client
        
        client = get_client()
        
        # Minimal, safe prompt - LLM only does linguistic polish
        polish_prompt = f"""Rewrite this game narration in a {tone} tone. Keep the same meaning and all options. Make it flow naturally.

Original:
{text}

Rewritten:"""
        
        response = client.chat.completions.create(
            model=settings.openai_model,
            temperature=0.7,
            max_tokens=300,  # Keep it brief
            messages=[
                {"role": "system", "content": "You are a narrative polisher. Preserve meaning, enhance style."},
                {"role": "user", "content": polish_prompt}
            ]
        )
        
        polished = response.choices[0].message.content.strip()
        logger.debug(f"LLM polish successful ({len(polished)} chars)")
        return polished
        
    except Exception as e:
        logger.warning(f"LLM polish failed (falling back to template): {e}")
        return None

def generate_narrative(
    frame_key: str,
    tone: str = "classic",
    scene_context: str = "",
    player_action: str = "",
    imagination_signals: list = None
) -> str:
    """
    Generate narrative using the configured narration mode.
    
    Modes:
    - TEMPLATE: Pure templates, instant, zero dependencies
    - HYBRID: Templates + optional LLM polish (degrades gracefully)
    - LLM: Full LLM generation (legacy mode, requires API key)
    
    Returns:
        Narrative text (always succeeds, even if LLM unavailable)
    """
    mode = settings.narration_mode
    
    # Always generate template base first
    template_output = render_template(
        frame_key=frame_key,
        tone=tone,
        scene_context=scene_context,
        player_action=player_action,
        imagination_signals=imagination_signals
    )
    
    if mode == NarrationMode.TEMPLATE:
        # Pure template mode - return immediately
        logger.debug(f"Template mode: {len(template_output)} chars")
        return template_output
    
    elif mode == NarrationMode.HYBRID:
        # Try LLM polish, fall back to template
        polished = _try_llm_polish(template_output, tone)
        if polished:
            logger.debug("Hybrid mode: LLM polish applied")
            return polished
        else:
            logger.debug("Hybrid mode: Using template (LLM unavailable)")
            return template_output
    
    elif mode == NarrationMode.LLM:
        # Legacy full LLM mode
        try:
            from .llm import generate_text
            
            # Build full LLM prompt (legacy behavior)
            prompt = f"""
SCENE: {scene_context}
PLAYER ACTION: {player_action}
FRAME: {frame_key}

Narrate what happens next in a {tone} style. Then offer 2-4 meaningful choices.
Keep under 150 words.
"""
            result = generate_text(tone, prompt)
            logger.debug(f"LLM mode: Full generation ({len(result)} chars)")
            return result
            
        except Exception as e:
            logger.warning(f"LLM mode failed, falling back to template: {e}")
            return template_output
    
    # Shouldn't reach here, but safety fallback
    return template_output

def get_narration_stats() -> dict:
    """Get statistics about current narration mode"""
    from .template_engine import get_template_stats
    
    template_stats = get_template_stats()
    
    return {
        "mode": settings.narration_mode.value,
        "llm_available": bool(settings.openai_api_key and settings.openai_api_key.startswith("sk-")),
        "llm_model": settings.openai_model if settings.narration_mode == NarrationMode.LLM else None,
        "template_stats": template_stats,
        "fallback_strategy": "templates" if settings.narration_mode != NarrationMode.TEMPLATE else "none_needed",
        "dependencies_required": 0 if settings.narration_mode == NarrationMode.TEMPLATE else 1
    }
