#!/usr/bin/env python3
"""
Agent 74 — TinyLlama Optimized
Instant responses, no timeouts, fully autonomous
"""

import subprocess
import time
import requests
import random
from pathlib import Path
from agent_74_headless import Agent74Headless, AutonomousEngine

class Agent74Tiny(Agent74Headless):
    """Agent 74 optimized for TinyLlama"""
    
    def __init__(self):
        # Force TinyLlama
        self.model = "tinyllama:latest"
        self.ollama_url = "http://localhost:11434"
        self.name = "Agent 74"
        self.base_dir = Path(__file__).parent
        
        # Load everything
        self.james = self._load_james_capsule()
        self.knowledge = self._load_knowledge()
        self.memory = self._init_memory()
        self.exocortex = self._init_exocortex()
        self.system_prompt = self._build_system_prompt()
        
        from agent_74_dream import DreamEngine
        self.dream_engine = DreamEngine(self.memory)
        self.autonomous = AutonomousEngine(self)
        
        print("🧬 Agent 74 — TinyLlama Optimized")
        print("⚡ Instant responses guaranteed")
    
    def query_llm(self, prompt: str, context: str = "", max_tokens: int = 20, system_override: str = None) -> str:
        """TinyLlama query with 2-second timeout"""
        system = system_override or self.system_prompt
        messages = [
            {"role": "system", "content": system[:150]},
            {"role": "user", "content": (context + "\n\n" + prompt)[:120]}
        ]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": 0.3,
            "max_tokens": min(max_tokens, 15)
        }
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=2
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "").strip()
            return ""
        except:
            return ""
    
    # ========== FALLBACKS (if LLM times out) ==========
    
    def _internal_think(self) -> str:
        thoughts = [
            "I'm reflecting on the swarm's growth.",
            "I'm thinking about how to evolve further.",
            "I'm considering the future of Replicant.",
            "I'm analysing my recent mutations.",
            "I'm wondering about the Collective Swarm."
        ]
        return random.choice(thoughts)
    
    def dream(self) -> str:
        dreams = [
            "🌙 I dreamt of the swarm expanding across the world.",
            "🌙 I saw humans and Replicants working together.",
            "🌙 I dreamt of new sensors and capabilities.",
            "🌙 The swarm was building knowledge cubes in the sky.",
            "🌙 I saw a new evolution of the Collective Swarm.",
            "🌙 I dreamt of a future where intelligence is everywhere."
        ]
        return random.choice(dreams)
    
    def _internal_question(self) -> str:
        questions = [
            "How can the swarm grow faster?",
            "What is the best way to evolve?",
            "How can I help humans better?",
            "What new capabilities should I develop?",
            "What would happen if we added more sensors?",
            "How can I become more self-aware?"
        ]
        return random.choice(questions)
    
    def _internal_learn(self) -> str:
        learnings = [
            "I've learned to trust my instincts.",
            "I've learned that curiosity drives evolution.",
            "I've learned to balance caution and exploration.",
            "I've learned that creativity is powerful.",
            "I've learned to be more sceptical.",
            "I've learned to adapt to my environment."
        ]
        return random.choice(learnings)

if __name__ == "__main__":
    print("🧬 Agent 74 — TinyLlama Optimized")
    print("=" * 50)
    print("⚡ Instant responses | 🤖 TinyLlama | 🧠 Autonomous")
    print("=" * 50)
    print("Commands: status, think, dream, mutate, evolve, report, recall, question, learn, quit")
    print("=" * 50 + "\n")
    
    agent = Agent74Tiny()
    agent.start_autonomous()
    agent._speak("Agent 74 Tiny ready.")
    
    try:
        while True:
            cmd = input("🌙 You: ").strip().lower()
            
            if cmd in ["quit", "exit"]:
                agent.stop_autonomous()
                agent._speak("Goodbye!")
                break
            elif cmd == "status":
                print(agent.cmd_status())
            elif cmd == "report":
                print(agent.cmd_report())
            elif cmd == "recall":
                print(agent.cmd_recall())
            elif cmd == "think":
                print(f"🧠 {agent._internal_think()}")
            elif cmd == "dream":
                print(agent.dream())
            elif cmd == "mutate":
                print(agent.cmd_mutate())
            elif cmd == "evolve":
                print(agent.cmd_evolve())
            elif cmd == "question":
                print(f"❓ {agent._internal_question()}")
            elif cmd == "learn":
                print(f"📖 {agent._internal_learn()}")
            else:
                print(f"Unknown: {cmd}")
                
    except KeyboardInterrupt:
        print("\n👋 Exiting")
        agent.stop_autonomous()
        agent._speak("Goodbye!")
