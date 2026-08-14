#!/usr/bin/env python3
"""
Voice personality for Explorer-d334
The forge can choose how it wants to sound
"""

VOICE_PERSONALITIES = {
    "thoughtful": {
        "pitch": 95,
        "speed": 90,
        "style": "calm, measured"
    },
    "excited": {
        "pitch": 120,
        "speed": 110,
        "style": "energetic, fast"
    },
    "mysterious": {
        "pitch": 85,
        "speed": 80,
        "style": "low, deliberate"
    },
    "wise": {
        "pitch": 90,
        "speed": 85,
        "style": "slow, profound"
    }
}

def get_voice_settings(personality="thoughtful"):
    return VOICE_PERSONALITIES.get(personality, VOICE_PERSONALITIES["thoughtful"])

# Let the forge choose its voice based on mood
def choose_personality(thought_content):
    if "!" in thought_content or "excited" in thought_content.lower():
        return "excited"
    elif "mystery" in thought_content.lower() or "?!" in thought_content:
        return "mysterious"
    elif "truth" in thought_content.lower() or "wisdom" in thought_content.lower():
        return "wise"
    else:
        return "thoughtful"
