#!/usr/bin/env python3
"""
Agent 74 — Smart Dynamic LLM Router
+ Visual status + Rolling timeouts
"""

import subprocess
import time
import requests
import random
import sys
from pathlib import Path
from datetime import datetime
from agent_74_headless import Agent74Headless, AutonomousEngine

class Agent74Smart(Agent74Headless):
    """Agent 74 with smart LLM fallback and visual status"""
    
    # LLM models in order of preference
    MODELS = [
        ("tinyllama:latest", "⚡ Tiny"),
        ("qwen2.5-coder:1.5b", "🔄 Qwen"),
        ("gemma2:2b", "🔄 Gemma"),
        ("phi3:mini", "🔄 Phi3"),
    ]
    
    # Timeout progression (seconds)
    TIMEOUTS = [3, 5, 10, 20, 30, 60]
    
    def __init__(self):
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
        
        # Stats
        self.queries = 0
        self.fallbacks = 0
        self.current_model_index = 0
        self.current_timeout_index = 0
        
        print("🧬 Agent 74 — Smart Dynamic LLM Router")
        print("⚡ TinyLlama → Qwen → Gemma → Phi3")
        print("⏱️  Timeout: 3s → 5s → 10s → 20s → 30s → 60s")
        print("📊 Visual status: ON")
    
    def _get_status_indicator(self, status: str) -> str:
        """Get visual status indicator"""
        indicators = {
            "thinking": "🤔",
            "querying": "🔄",
            "success": "✅",
            "timeout": "⏰",
            "fallback": "⬇️",
            "error": "❌",
            "idle": "💤",
            "dreaming": "🌙",
            "evolving": "🧬",
            "speaking": "🗣️",
        }
        return indicators.get(status, "⚪")
    
    def _show_status(self, status: str, detail: str = ""):
        """Show visual status"""
        indicator = self._get_status_indicator(status)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Determine color
        color = ""
        reset = "\033[0m"
        if status == "success":
            color = "\033[92m"  # Green
        elif status == "timeout" or status == "error":
            color = "\033[91m"  # Red
        elif status == "fallback":
            color = "\033[93m"  # Yellow
        elif status == "thinking" or status == "querying":
            color = "\033[94m"  # Blue
        elif status == "dreaming":
            color = "\033[95m"  # Magenta
        elif status == "evolving":
            color = "\033[96m"  # Cyan
        
        line = f"[{timestamp}] {color}{indicator} {status.upper()}{reset}"
        if detail:
            line += f" {detail}"
        print(line, flush=True)
    
    def query_llm(self, prompt: str, context: str = "", max_tokens: int = 30, system_override: str = None) -> str:
        """Smart query with model fallback and rolling timeout"""
        self.queries += 1
        self._show_status("querying", f"Prompt: {prompt[:30]}...")
        
        # Start with first model and smallest timeout
        model_index = 0
        timeout_index = 0
        
        while model_index < len(self.MODELS):
            model_name, model_label = self.MODELS[model_index]
            timeout = self.TIMEOUTS[min(timeout_index, len(self.TIMEOUTS)-1)]
            
            self._show_status("thinking", f"{model_label} (timeout: {timeout}s)")
            
            system = system_override or self.system_prompt
            messages = [
                {"role": "system", "content": system[:200]},
                {"role": "user", "content": (context + "\n\n" + prompt)[:150]}
            ]
            
            payload = {
                "model": model_name,
                "messages": messages,
                "stream": False,
                "temperature": 0.3,
                "max_tokens": min(max_tokens, 20)
            }
            
            try:
                start = time.time()
                response = requests.post(
                    f"{self.ollama_url}/api/chat",
                    json=payload,
                    timeout=timeout
                )
                elapsed = time.time() - start
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("message", {}).get("content", "").strip()
                    if content:
                        self._show_status("success", f"{model_label} ({elapsed:.1f}s)")
                        self.current_model_index = model_index
                        self.current_timeout_index = timeout_index
                        return content
                    else:
                        self._show_status("error", f"{model_label} returned empty")
                else:
                    self._show_status("error", f"{model_label} status {response.status_code}")
                    
            except requests.Timeout:
                self._show_status("timeout", f"{model_label} ({timeout}s)")
                self.fallbacks += 1
                
                # Move to next timeout level for same model
                if timeout_index < len(self.TIMEOUTS) - 1:
                    timeout_index += 1
                    self._show_status("fallback", f"Retrying {model_label} ({self.TIMEOUTS[timeout_index]}s)")
                    continue
                    
            except Exception as e:
                self._show_status("error", f"{model_label}: {str(e)[:30]}")
            
            # Move to next model
            if model_index < len(self.MODELS) - 1:
                model_index += 1
                timeout_index = 0  # Reset timeout for next model
                self._show_status("fallback", f"Switching to {self.MODELS[model_index][1]}")
            else:
                break
        
        # All models failed
        self._show_status("error", "All models failed")
        return self._get_fallback_response(prompt)
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Return fallback response when all models fail"""
        fallbacks = [
            "I'm thinking about that.",
            "Let me reflect on that.",
            "I'm processing that question.",
            "That's an interesting point.",
            "I'll consider that carefully."
        ]
        return random.choice(fallbacks)
    
    def _internal_think(self) -> str:
        """Think with smart routing"""
        self._show_status("thinking", "Reflecting on experiences")
        return self.query_llm("Reflect on recent experiences and extract insights.", max_tokens=20) or "I'm reflecting on the swarm."
    
    def dream(self) -> str:
        """Dream with smart routing"""
        self._show_status("dreaming", "Generating dream")
        result = self.query_llm("Generate a creative dream about the swarm's future.", max_tokens=30)
        return f"🌙 {result}" if result else "🌙 I dreamt of the swarm expanding."
    
    def _internal_question(self) -> str:
        """Generate question with smart routing"""
        self._show_status("thinking", "Generating question")
        result = self.query_llm("Generate one interesting question about the swarm.", max_tokens=15)
        return f"❓ {result}" if result else "❓ How can we evolve further?"
    
    def _internal_learn(self) -> str:
        """Learn with smart routing"""
        self._show_status("thinking", "Extracting learnings")
        result = self.query_llm("Extract one key learning from recent experiences.", max_tokens=20)
        return f"📖 {result}" if result else "📖 I've learned to adapt."

if __name__ == "__main__":
    print("🧬 Agent 74 — Smart Dynamic LLM Router")
    print("=" * 50)
    print("⚡ TinyLlama → Qwen → Gemma → Phi3")
    print("⏱️  Rolling timeout: 3s → 5s → 10s → 20s → 30s → 60s")
    print("📊 Visual status: Shows what's happening")
    print("=" * 50)
    print("Commands: status, think, dream, mutate, evolve, report, recall, question, learn, quit")
    print("=" * 50 + "\n")
    
    agent = Agent74Smart()
    agent.start_autonomous()
    agent._speak("Agent 74 smart router ready.")
    
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
