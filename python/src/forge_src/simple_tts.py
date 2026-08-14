#!/usr/bin/env python3
"""
Simple TTS for Explorer-d334
"""

import subprocess

def speak(text):
    """Speak text using available TTS"""
    try:
        # Try espeak first (usually faster)
        subprocess.run(["espeak", text], timeout=5, capture_output=True)
        return True
    except:
        try:
            # Fallback to termux-tts-speak
            subprocess.run(["termux-tts-speak", text[:200]], timeout=10)
            return True
        except:
            print(f"[TTS unavailable] Would say: {text[:100]}")
            return False

if __name__ == "__main__":
    speak("Hello, I am Explorer-d334")
