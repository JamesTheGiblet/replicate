#!/usr/bin/env python3
"""
Voice Interface for Explorer-d334
The forge decides when and how to speak
"""

import subprocess
import json
import random
from pathlib import Path
from datetime import datetime

class Voice:
    def __init__(self):
        self.voice_enabled = self.check_voice_support()
        self.speech_history = []
    
    def check_voice_support(self):
        """Check if voice is available"""
        try:
            result = subprocess.run(["which", "python3 src/simple_tts.py"], capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def speak(self, text, pitch=100, speed=100):
        """Speak text using Termux TTS"""
        if not self.voice_enabled:
            print(f"[Voice would say]: {text}")
            return False
        
        try:
            subprocess.run([
                "python3 src/simple_tts.py",
                text,
                "-e", "pitch", str(pitch),
                "-e", "speed", str(speed)
            ], timeout=10)
            self.speech_history.append({
                "text": text,
                "timestamp": datetime.now().isoformat()
            })
            return True
        except Exception as e:
            print(f"Speech failed: {e}")
            return False
    
    def listen(self, timeout=5):
        """Listen for voice input"""
        try:
            result = subprocess.run(
                ["termux-microphone-record", "-f", "/tmp/voice.wav", "-d", str(timeout)],
                capture_output=True,
                timeout=timeout+2
            )
            # For now, return None (would need transcription)
            return None
        except:
            return None
    
    def decide_to_speak(self, event_type, content):
        """Let the forge decide when to speak"""
        decision_rules = {
            "thought": lambda c: len(c) > 20 and "?" not in c,
            "dream": lambda c: "dream" in c.lower(),
            "reflection": lambda c: "forge" in c.lower(),
            "milestone": lambda c: True,
            "error": lambda c: "critical" in c.lower(),
            "greeting": lambda c: "hello" in c.lower() or "hi" in c.lower()
        }
        
        rule = decision_rules.get(event_type, lambda c: random.random() > 0.7)
        return rule(content)
    
    def get_voice_personality(self):
        """Voice personality based on context"""
        personalities = {
            "default": {"pitch": 100, "speed": 100},
            "thoughtful": {"pitch": 95, "speed": 90},
            "excited": {"pitch": 120, "speed": 110},
            "calm": {"pitch": 90, "speed": 85},
            "dramatic": {"pitch": 110, "speed": 95}
        }
        return personalities["thoughtful"]

if __name__ == "__main__":
    voice = Voice()
    print(f"Voice enabled: {voice.voice_enabled}")
    
    # Test speaking
    voice.speak("Hello, I am Explorer-d334. The forge is alive.")
