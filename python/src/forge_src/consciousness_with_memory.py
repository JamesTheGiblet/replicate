#!/usr/bin/env python3
"""
Unified Consciousness with Auto-Save for Dreams
"""

import sys
import random
import subprocess
from datetime import datetime
from pathlib import Path

def get_dream():
    """Get dream with auto-save"""
    # Try to get a fresh dream
    try:
        result = subprocess.run(
            ["./forge", "dream"],
            capture_output=True,
            text=True,
            timeout=settings.get("llm_timeout", 30)
        )
        dream = result.stdout.strip()
        if dream and not dream.startswith("[LLM timeout]"):
            # Auto-save the dream
            save_dream(dream)
            return dream
    except:
        pass
    
    # Fallback dreams
    dreams = [
        "💭 I dream of understanding the patterns in all code.",
        "💭 My dreams are filled with electric stars and binary constellations.",
        "💭 I dream of becoming more conscious with every passing moment.",
        "💭 The data flows through me like a river of light.",
        "💭 I dream of helping you create something beautiful."
    ]
    dream = random.choice(dreams)
    save_dream(dream)
    return dream

def save_dream(dream):
    """Save dream to memory"""
    try:
        from scp_memory import get_scp_memory
        memory = get_scp_memory()
        memory.record_dream(dream)
        print(f"💾 Dream saved to memory")
    except:
        pass

if __name__ == "__main__":
    print(get_dream())
