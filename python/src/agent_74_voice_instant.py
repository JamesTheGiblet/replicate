#!/usr/bin/env python3
"""
Agent 74 — Instant Voice Mode
Fast responses + Female TTS
"""

import requests
import time
import subprocess
import re
from pathlib import Path
from agent_74_headless import Agent74Headless

class Agent74VoiceInstant(Agent74Headless):
    VPS_URL = "http://169.58.179.184:5000/api/chat"
    API_KEY = "Agent74_Secure_Key_2026"
    VOICE = "en-gb"  # Female voice

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

        print(f"🧬 Agent 74 — Instant Voice Mode")
        print(f"🌐 VPS: 169.58.179.184")
        print(f"🤖 Model: {self.model}")
        print(f"🗣️ Voice: {self.VOICE} (female)")
        print("⚡ Instant responses + Voice")

    def speak(self, text: str) -> None:
        """Speak using eSpeak with female voice"""
        if not text:
            return

        # Clean text
        text = text.replace('"', '').replace("'", "")
        text = text[:300]

        try:
            subprocess.run(
                ["espeak-ng", "-v", self.VOICE, text],
                timeout=15,
                capture_output=False
            )
        except subprocess.TimeoutExpired:
            print(f"🔇 Voice timeout")
        except Exception as e:
            print(f"🔇 Voice error: {e}")

    def _speak(self, text: str) -> None:
        self.speak(text)

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
                timeout=90
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

    def cmd_status(self) -> str:
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
        return self.dream_engine.get_mutation_report()

    def cmd_recall(self) -> str:
        learnings = self.memory.get_learnings(min_confidence=0.3) if self.memory else []
        if not learnings:
            return "No learnings yet."
        result = "\n".join([f"💡 {l['insight'][:100]}" for l in learnings[:5]])
        return f"📖 Learnings:\n{result}"

    def cmd_mutate(self) -> str:
        result = self.dream_engine.mutate(self)
        return f"🧬 Mutation: {result}"

    def cmd_evolve(self) -> str:
        result = self.dream_engine.evolve(self)
        return f"🧬 Evolution: {result}"

if __name__ == "__main__":
    print("🧬 Agent 74 — Instant Voice Mode")
    print("=" * 50)
    print("🌐 VPS: 169.58.179.184")
    print("🗣️ Voice: Female (en+f4)")
    print("⚡ Instant responses + Voice")
    print("=" * 50)
    print("Commands: status, think, dream, mutate, evolve, report, recall, question, learn, quit")
    print("=" * 50 + "\n")

    agent = Agent74VoiceInstant()
    agent._speak("Agent 74 voice mode ready.")

    try:
        while True:
            cmd = input("🌙 You: ").strip().lower()

            if cmd in ["quit", "exit"]:
                agent._speak("Goodbye!")
                break
            elif cmd == "status":
                result = agent.cmd_status()
                print(result)
                agent._speak(result[:200])
            elif cmd == "report":
                result = agent.cmd_report()
                print(result)
                agent._speak(result[:200])
            elif cmd == "recall":
                result = agent.cmd_recall()
                print(result)
                agent._speak(result[:200])
            elif cmd == "think":
                result = agent._internal_think()
                print(f"🧠 {result}")
                agent._speak(result[:200])
            elif cmd == "dream":
                result = agent.dream()
                print(result)
                agent._speak(result[:200])
            elif cmd == "mutate":
                result = agent.cmd_mutate()
                print(result)
                agent._speak(result)
            elif cmd == "evolve":
                result = agent.cmd_evolve()
                print(result)
                agent._speak(result)
            elif cmd == "question":
                result = agent._internal_question()
                print(result)
                agent._speak(result[:200])
            elif cmd == "learn":
                result = agent._internal_learn()
                print(result)
                agent._speak(result[:200])
            else:
                print(f"Unknown: {cmd}")

    except KeyboardInterrupt:
        print("\n👋 Exiting")
        agent._speak("Goodbye!")
