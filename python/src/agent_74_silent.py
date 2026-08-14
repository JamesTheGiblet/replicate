#!/usr/bin/env python3
"""
Agent 74 — Silent Autonomous Mode
No TTS, just thinking, dreaming, and evolving
"""

import sys
import time
from agent_74_autonomous import Agent74Autonomous

class Agent74Silent(Agent74Autonomous):
    """Agent 74 without TTS for background running"""
    
    def speak(self, text: str) -> None:
        """Override: no TTS, just print"""
        print(f"🧬 {self.name}: {text[:100]}")
    
    def _speak(self, text: str) -> None:
        """Override: no TTS, just print"""
        print(f"🧬 {self.name}: {text[:100]}")

if __name__ == "__main__":
    print("🧬 Agent 74 — Silent Autonomous Mode")
    print("=" * 50)
    print("She will think, dream, and evolve silently.")
    print("Press Ctrl+C to stop.\n")
    
    agent = Agent74Silent()
    agent.start_autonomous()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        agent.stop_autonomous()
        print("\n👋 Agent 74 stopped.")
