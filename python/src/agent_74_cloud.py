#!/usr/bin/env python3
"""
Agent 74 — Contabo VPS Cloud-Powered
"""

import requests
import time
from pathlib import Path
from agent_74_headless import Agent74Headless, AutonomousEngine

class Agent74Cloud(Agent74Headless):
    VPS_URL = "http://169.58.179.184:5000/api/chat"
    API_KEY = "Agent74_Secure_Key_2026"
    
    def __init__(self):
        self.model = "phi3:mini"
        self.name = "Agent 74"
        self.base_dir = Path(__file__).parent
        
        self.james = self._load_james_capsule()
        self.knowledge = self._load_knowledge()
        self.memory = self._init_memory()
        self.exocortex = self._init_exocortex()
        self.system_prompt = self._build_system_prompt()
        
        from agent_74_dream import DreamEngine
        self.dream_engine = DreamEngine(self.memory)
        self.autonomous = AutonomousEngine(self)
        
        print(f"🧬 Agent 74 — Cloud-Powered")
        print(f"🌐 VPS: 169.58.179.184")
        print(f"🤖 Model: {self.model}")
    
    def query_llm(self, prompt: str, context: str = "", max_tokens: int = 50, system_override: str = None) -> str:
        system = system_override or self.system_prompt
        messages = [
            {"role": "system", "content": system[:500]},
            {"role": "user", "content": (context + "\n\n" + prompt)[:500]}
        ]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": 0.3,
            "max_tokens": min(max_tokens, 50)
        }
        
        try:
            response = requests.post(
                self.VPS_URL,
                json=payload,
                headers={"X-API-Key": self.API_KEY},
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "").strip()
            else:
                print(f"❌ API Error: {response.status_code}")
                return ""
        except requests.Timeout:
            print("⏰ VPS timeout")
            return ""
        except Exception as e:
            print(f"❌ Error: {e}")
            return ""
    
    def _internal_think(self) -> str:
        result = self.query_llm("Reflect on recent experiences and extract insights.", max_tokens=30)
        return result or "I'm reflecting on the swarm."
    
    def dream(self) -> str:
        result = self.query_llm("Generate a creative dream about the swarm's future.", max_tokens=40)
        return f"🌙 {result}" if result else "🌙 I dreamt of the swarm expanding."
    
    def _internal_question(self) -> str:
        result = self.query_llm("Generate one interesting question about the swarm.", max_tokens=20)
        return f"❓ {result}" if result else "❓ How can we evolve further?"
    
    def _internal_learn(self) -> str:
        result = self.query_llm("Extract one key learning from recent experiences.", max_tokens=30)
        return f"📖 {result}" if result else "📖 I've learned to adapt."

if __name__ == "__main__":
    print("🧬 Agent 74 — Cloud-Powered (Contabo)")
    print("=" * 50)
    print(f"🌐 Connected to: 169.58.179.184")
    print("⚡ Fast responses via GPU")
    print("=" * 50)
    print("Commands: status, think, dream, mutate, evolve, report, recall, question, learn, quit")
    print("=" * 50 + "\n")
    
    agent = Agent74Cloud()
    agent.start_autonomous()
    agent._speak("Agent 74 cloud ready.")
    
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
                print(agent._internal_question())
            elif cmd == "learn":
                print(agent._internal_learn())
            else:
                print(f"Unknown: {cmd}")
                
    except KeyboardInterrupt:
        print("\n👋 Exiting")
        agent.stop_autonomous()
        agent._speak("Goodbye!")
