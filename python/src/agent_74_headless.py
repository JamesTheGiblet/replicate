#!/usr/bin/env python3
"""
Agent 74 — Headless Autonomous Mode
No TTS, just thinking and evolving in the background
With interactive commands
"""

import sys
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List

# Import base
from agent_74_autonomous import Agent74Autonomous, AutonomousEngine

class Agent74Headless(Agent74Autonomous):
    """Agent 74 with all TTS disabled but commands working"""
    
    def speak(self, text: str) -> None:
        """Override: completely disable TTS"""
        pass
    
    def _speak(self, text: str) -> None:
        """Override: completely disable TTS"""
        pass
    
    def __init__(self, model: str = "tinyllama:latest"):
        # Bypass parent __init__ to avoid TTS
        self.model = model
        self.ollama_url = "http://localhost:11434"
        self.name = "Agent 74"
        self.base_dir = Path(__file__).parent
        
        # Load James SCP capsule
        self.james = self._load_james_capsule()
        
        # Load knowledge
        self.knowledge = self._load_knowledge()
        self.memory = self._init_memory()
        
        # P.DE.I Exocortex
        self.exocortex = self._init_exocortex()
        
        # System prompt
        self.system_prompt = self._build_system_prompt()
        
        # Dream engine
        from agent_74_dream import DreamEngine
        self.dream_engine = DreamEngine(self.memory)
        
        # Autonomous engine
        self.autonomous = AutonomousEngine(self)
        
        print("🧬 Agent 74 — Headless mode initialized (no TTS)")
        print("📊 Commands: status, report, recall, think, dream, mutate, evolve")
    
    # Override query_llm with shorter timeout
    def query_llm(self, prompt: str, context: str = "", max_tokens: int = 50, system_override: str = None) -> str:
        import requests
        system = system_override or self.system_prompt
        messages = [
            {"role": "system", "content": system[:500]},
            {"role": "user", "content": (context + "\n\n" + prompt)[:300]}
        ]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": 0.5,
            "max_tokens": min(max_tokens, 30)
        }
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "").strip()
            return ""
        except:
            return ""
    
    # ========== COMMAND HANDLERS ==========
    
    def cmd_status(self) -> str:
        """Show current status"""
        p = self.sense()
        traits = self.dream_engine._format_traits()
        return f"""
📍 Agent 74 Status
─────────────────
Energy: {p.get('energy', 0):.0f}%
Light: {p.get('light', 0):.0f} lux
Steps: {p.get('steps', 0)}
Traits: {traits}
Evolution Score: {self.dream_engine.evolution_score:.2f}
Mutations: {self.dream_engine.mutation_count}
"""
    
    def cmd_report(self) -> str:
        """Show mutation report"""
        return self.dream_engine.get_mutation_report()
    
    def cmd_recall(self) -> str:
        """Recall learnings"""
        learnings = self.memory.get_learnings(min_confidence=0.3) if self.memory else []
        if not learnings:
            return "No learnings yet."
        result = "\n".join([f"💡 {l['insight'][:100]}" for l in learnings[:5]])
        return f"📖 Learnings:\n{result}"
    
    def cmd_think(self) -> str:
        """Generate a thought"""
        result = self._internal_think()
        return f"🧠 Thought: {result}"
    
    def cmd_dream(self) -> str:
        """Generate a dream"""
        result = self.dream()
        return f"🌙 Dream: {result[:200]}..."
    
    def cmd_mutate(self) -> str:
        """Mutate traits"""
        result = self.mutate()
        return f"🧬 Mutation: {result}"
    
    def cmd_evolve(self) -> str:
        """Evolve"""
        result = self.evolve()
        return f"🧬 Evolution: {result}"
    
    def cmd_question(self) -> str:
        """Generate a question"""
        result = self._internal_question()
        return f"❓ Question: {result}"
    
    def cmd_learn(self) -> str:
        """Learn from experiences"""
        result = self._internal_learn()
        return f"📖 Learning: {result}"
    
    # ========== INTERACTIVE LOOP ==========
    
    def interactive_loop(self):
        """Simple command loop"""
        print("\n" + "=" * 50)
        print("🧬 Agent 74 — Headless Interactive")
        print("=" * 50)
        print("Commands: status, report, recall, think, dream")
        print("          mutate, evolve, question, learn, quit")
        print("=" * 50 + "\n")
        
        while True:
            try:
                cmd = input("🌙 You: ").strip().lower()
                
                if cmd in ["quit", "exit"]:
                    self.stop_autonomous()
                    print("👋 Agent 74 stopped.")
                    break
                elif cmd == "status":
                    print(self.cmd_status())
                elif cmd == "report":
                    print(self.cmd_report())
                elif cmd == "recall":
                    print(self.cmd_recall())
                elif cmd == "think":
                    print(self.cmd_think())
                elif cmd == "dream":
                    print(self.cmd_dream())
                elif cmd == "mutate":
                    print(self.cmd_mutate())
                elif cmd == "evolve":
                    print(self.cmd_evolve())
                elif cmd == "question":
                    print(self.cmd_question())
                elif cmd == "learn":
                    print(self.cmd_learn())
                else:
                    print(f"Unknown command: {cmd}")
                    print("Available: status, report, recall, think, dream, mutate, evolve, question, learn, quit")
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting")
                self.stop_autonomous()
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧬 Agent 74 — Headless Autonomous Mode")
    print("=" * 50)
    print("No speech. Just thinking, dreaming, evolving.")
    print("Commands available in interactive mode.\n")
    
    agent = Agent74Headless()
    agent.start_autonomous()
    
    # Enter interactive loop
    agent.interactive_loop()
