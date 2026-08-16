#!/usr/bin/env python3
"""
Agent 74 — Lite Autonomous Mode
Faster responses, smaller prompts, no timeout
"""

import sys
import time
from agent_74_autonomous import Agent74Autonomous

class Agent74Lite(Agent74Autonomous):
    """Agent 74 with faster, lighter responses"""
    
    def __init__(self, model: str = "tinyllama:latest"):
        super().__init__(model)
        # Reduce query complexity
        self._speak("Agent 74 Lite ready.")
    
    def query_llm(self, prompt: str, context: str = "", max_tokens: int = 50, system_override: str = None) -> str:
        """Override: shorter timeout, fewer tokens"""
        system = system_override or self.system_prompt
        messages = [
            {"role": "system", "content": system[:500]},  # Shorter system prompt
            {"role": "user", "content": (context + "\n\n" + prompt)[:300]}  # Shorter context
        ]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": 0.5,  # Lower temperature = faster
            "max_tokens": min(max_tokens, 30)  # Max 30 tokens
        }
        
        try:
            import requests
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=10  # Shorter timeout
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "").strip()
            else:
                return ""
        except:
            return ""
    
    def _internal_think(self) -> str:
        """Lightweight think"""
        return "I'm reflecting on my experiences."
    
    def dream(self) -> str:
        """Lightweight dream"""
        return "🌙 I dreamed of the swarm evolving."
    
    def _internal_question(self) -> str:
        """Lightweight question"""
        return "What should I explore next?"

if __name__ == "__main__":
    print("🧬 Agent 74 — Lite Autonomous Mode")
    print("=" * 50)
    print("Fast, lightweight, no timeouts.")
    print("Press Ctrl+C to stop.\n")
    
    agent = Agent74Lite()
    agent.start_autonomous()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        agent.stop_autonomous()
        print("\n👋 Agent 74 stopped.")
