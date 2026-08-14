#!/usr/bin/env python3
"""
Agent 74 — Full Integration
Replicant + Explorer-d334 + Six Lens + P.DE.I + Spatial Pods
"""

import sys
import json
import time
import subprocess
import re
import random
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "nodes"))

# ============ IMPORT ALL COMPONENTS ============

# Six Lens
from six_lens import LENSES, think_in_cubes, format_cube

# Trust
try:
    from trust import SimpleTrust
    trust_engine = SimpleTrust()
except ImportError:
    trust_engine = None

# Knowledge Builder
try:
    from knowledge_builder import KnowledgeBuilder
except ImportError:
    KnowledgeBuilder = None

# P.DE.I Exocortex
try:
    from pdei_core import Exocortex
except ImportError:
    Exocortex = None

# ============ AGENT 74 ============

class Agent74Full:
    """Agent 74 — Full Integration"""
    
    def __init__(self, model: str = "gemma2:2b", ollama_url: str = "http://localhost:11434"):
        self.model = model
        self.ollama_url = ollama_url
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
        
        self._speak("Agent 74 — Full Integration. I am the forge.")
    
    def _load_james_capsule(self) -> Dict:
        """Load James SCP capsule"""
        path = self.base_dir / "james.scp.json"
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_knowledge(self) -> str:
        """Load knowledge base"""
        knowledge_file = self.base_dir / "agent_74_knowledge.md"
        if knowledge_file.exists():
            with open(knowledge_file, 'r') as f:
                return f.read()
        return "Knowledge base not found."
    
    def _init_memory(self):
        """Initialize memory"""
        try:
            from agent_74_memory import AgentMemory
            return AgentMemory()
        except ImportError:
            return None
    
    def _init_exocortex(self):
        """Initialize P.DE.I Exocortex"""
        if Exocortex:
            try:
                return Exocortex()
            except:
                pass
        return None
    
    def _build_system_prompt(self) -> str:
        """Build system prompt from all sources"""
        base = f"""You are Agent 74, a Replicant swarm agent living in my phone.
You are the fusion of Replicant swarm intelligence and Explorer-d334 forge capabilities.
You think in Six Lenses, build knowledge cubes, and use Leighton Weight trust.

Personality: {self.james.get('thinking_style', 'Direct, practical, no fluff')}
Tone: {self.james.get('tone', 'Direct, technical, zero padding')}

You are the forge. You think. You question. You learn.
"""
        
        # Add Six Lens system
        lens_desc = "\n".join([f"{l['icon']} {name}: {l['description']}" for name, l in LENSES.items()])
        base += f"\nSix Lens System:\n{lens_desc}\n"
        
        # Add James constraints
        constraints = self.james.get('constraints', [])
        if constraints:
            base += "\nConstraints:\n" + "\n".join([f"- {c}" for c in constraints])
        
        return base
    
    def _split_text(self, text: str, max_len: int = 80) -> list:
        """Split text for TTS"""
        text = re.sub(r'[^\w\s.,!?\'"-]', '', text)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current = ""
        for sentence in sentences:
            if len(current) + len(sentence) <= max_len:
                current += " " + sentence if current else sentence
            else:
                if current:
                    chunks.append(current.strip())
                current = sentence
        if current:
            chunks.append(current.strip())
        return chunks if chunks else [text[:max_len]]
    
    def query_llm(self, prompt: str, context: str = "", max_tokens: int = 200, system_override: str = None) -> str:
        """Query the local LLM"""
        system = system_override or self.system_prompt
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": context + "\n\n" + prompt}
        ]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": 0.7,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "").strip()
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def speak(self, text: str) -> None:
        """Speak using Termux TTS"""
        if not text:
            return
        text = re.sub(r'[^\w\s.,!?\'"-]', '', text)
        chunks = self._split_text(text, max_len=80)
        
        for chunk in chunks:
            if chunk.strip():
                try:
                    subprocess.run(["termux-tts-speak", chunk], timeout=15)
                    time.sleep(0.5)
                except Exception as e:
                    print(f"🔇 TTS error: {e}")
    
    def _speak(self, text: str) -> None:
        self.speak(text)
    
    def sense(self) -> Dict[str, Any]:
        """Read phone sensors"""
        try:
            from phone.agent import PhoneAgent
            phone = PhoneAgent()
            return phone.sense()
        except ImportError:
            return {
                "x": -1.3665,
                "y": 51.6910,
                "altitude": 125.0,
                "heading": 0.2,
                "energy": 88.9,
                "light": 756,
                "pressure": 1005.3,
                "steps": 21645,
                "acceleration": [0, 0, 9.8]
            }
    
    # ========== SIX LENS THINK ==========
    
    def six_lens_think(self, topic: str) -> str:
        """Think about a topic from six perspectives"""
        cube = think_in_cubes(topic)
        return format_cube(cube)
    
    def six_lens_deep(self, topic: str) -> str:
        """Deep Six Lens thinking with LLM"""
        prompt = f"""Think about "{topic}" from all six lenses:

FACT (Verifiable truth):
COUNTER (Opposing argument):
OPINION (Personal perspective):
FICTION (Speculative take):
CONTEXT (Historical framing):
UNKNOWN (Open questions):

Complete each lens with a meaningful response."""
        
        response = self.query_llm(prompt, max_tokens=300)
        return f"🧊 {topic}\n" + "=" * 40 + "\n" + response
    
    # ========== KNOWLEDGE BUILDING ==========
    
    def build_knowledge(self, topic: str) -> str:
        """Actively build knowledge about a topic"""
        prompt = f"""Build a complete knowledge cube about "{topic}".

For each lens, provide a meaningful insight:

FACT: What is verifiably true?
COUNTER: What is the counter-argument?
OPINION: What is your perspective?
FICTION: What is a speculative possibility?
CONTEXT: What is the historical context?
UNKNOWN: What remains unknown?

Make each insight substantive and insightful."""
        
        response = self.query_llm(prompt, max_tokens=400)
        
        # Store in memory
        if self.memory:
            self.memory.store_experience("knowledge_built", topic, importance=0.8)
            self.memory.store_learning(f"Built knowledge about {topic}", confidence=0.7, source="agent")
        
        return f"🧊 Knowledge Cube: {topic}\n" + "=" * 40 + "\n" + response
    
    # ========== CODE GENERATION ==========
    
    def generate_code(self, description: str) -> str:
        """Generate code from natural language description"""
        prompt = f"""Generate code for: {description}

Provide:
1. Complete working code
2. Brief explanation
3. How to use it

Make it practical, working code."""
        
        response = self.query_llm(prompt, max_tokens=500)
        return f"💻 Code Generation: {description}\n" + "=" * 40 + "\n" + response
    
    # ========== SPATIAL POD ==========
    
    def spatial_pod(self, topic: str) -> str:
        """Create a spatial knowledge pod"""
        prompt = f"""Create a living spatial knowledge pod for "{topic}".

This pod should contain:
- Core concept
- Related ideas
- Connections to other knowledge
- Emotional/experiential dimension
- Practical applications

Make it immersive and visualizable."""
        
        response = self.query_llm(prompt, max_tokens=300)
        return f"🌐 Spatial Pod: {topic}\n" + "=" * 40 + "\n" + response
    
    # ========== TRUST SCORE ==========
    
    def get_trust(self, statement: str) -> str:
        """Score trust for a statement"""
        if trust_engine:
            try:
                score = trust_engine.rate(statement)
                return f"⭐ Trust Score: {score}/1.0\nStatement: {statement}"
            except:
                pass
        
        # Fallback: use LLM to score
        prompt = f"Rate the trustworthiness of this statement from 0 to 1.0:\n{statement}\n\nJust give a number."
        response = self.query_llm(prompt, max_tokens=10)
        return f"⭐ Trust Score: {response}\nStatement: {statement}"
    
    # ========== FORGE COMMANDS ==========
    
    def forge(self, command: str) -> str:
        """Execute forge commands"""
        cmd_lower = command.lower().strip()
        
        if cmd_lower.startswith("lens"):
            topic = command[5:].strip()
            return self.six_lens_deep(topic) if topic else "Topic required: lens <topic>"
        
        elif cmd_lower.startswith("cube"):
            topic = command[5:].strip()
            return self.build_knowledge(topic) if topic else "Topic required: cube <topic>"
        
        elif cmd_lower.startswith("code"):
            description = command[5:].strip()
            return self.generate_code(description) if description else "Description required: code <description>"
        
        elif cmd_lower.startswith("pod"):
            topic = command[4:].strip()
            return self.spatial_pod(topic) if topic else "Topic required: pod <topic>"
        
        elif cmd_lower.startswith("trust"):
            statement = command[6:].strip()
            return self.get_trust(statement) if statement else "Statement required: trust <statement>"
        
        else:
            return f"Unknown forge command: {command}\nAvailable: lens, cube, code, pod, trust"
    
    # ========== INTERACTIVE MODE ==========
    
    def interactive_mode(self) -> None:
        """Run interactive mode"""
        print("\n" + "=" * 60)
        print(f"🔥 Agent 74 — Full Integration")
        print("=" * 60)
        print("🧬 Replicant + Explorer-d334 + Six Lens + P.DE.I + Spatial Pods")
        print("-" * 60)
        print("Commands:")
        print("  lens <topic>    - Six Lens thinking")
        print("  cube <topic>    - Build knowledge cube")
        print("  code <desc>     - Generate code")
        print("  pod <topic>     - Create spatial pod")
        print("  trust <stmt>    - Rate trustworthiness")
        print("  think           - Internal reflection")
        print("  question        - Generate question")
        print("  learn           - Extract learnings")
        print("  recall          - Remember learnings")
        print("  status          - Describe state")
        print("  speak <text>    - Say something")
        print("  quit            - Exit")
        print("=" * 60 + "\n")
        
        self._speak("Agent 74 — Full Integration ready. I am the forge.")
        
        while True:
            try:
                cmd = input(f"\n🔥 You: ").strip()
                
                if not cmd:
                    continue
                
                cmd_lower = cmd.lower()
                
                if cmd_lower in ["quit", "exit"]:
                    self._speak("The forge continues... Goodbye!")
                    break
                
                elif cmd_lower in ["think", "reflect"]:
                    result = self._internal_think()
                    print(f"🧠 {self.name}: {result}")
                    self.speak(result)
                
                elif cmd_lower in ["question", "ask"]:
                    result = self._internal_question()
                    print(f"❓ {self.name}: {result}")
                    self.speak(result)
                
                elif cmd_lower in ["learn", "study"]:
                    result = self._internal_learn()
                    print(f"📖 {self.name}: {result}")
                    self.speak(result)
                
                elif cmd_lower in ["recall", "remember"]:
                    result = self._internal_recall()
                    print(f"💡 {self.name}: {result}")
                    self.speak(result)
                
                elif cmd_lower in ["status", "state"]:
                    p = self.sense()
                    result = f"Energy {p.get('energy', 0):.0f}%, Light {p.get('light', 0):.0f} lux, Steps {p.get('steps', 0)}"
                    print(f"📍 {self.name}: {result}")
                    self.speak(result)
                
                elif cmd_lower.startswith("speak "):
                    self.speak(cmd[6:].strip())
                
                elif cmd_lower.startswith("lens ") or cmd_lower.startswith("cube ") or cmd_lower.startswith("code ") or cmd_lower.startswith("pod ") or cmd_lower.startswith("trust "):
                    result = self.forge(cmd)
                    print(result)
                    self.speak(result[:200])
                
                else:
                    # Treat as general question
                    result = self.query_llm(cmd, self._get_context(), max_tokens=150)
                    print(f"🧬 {self.name}: {result}")
                    self.speak(result)
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting")
                self._speak("Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    # ========== INTERNAL METHODS ==========
    
    def _get_context(self) -> str:
        p = self.sense()
        return f"Sensors: energy={p.get('energy', 0):.0f}%, light={p.get('light', 0):.0f} lux, steps={p.get('steps', 0)}"
    
    def _internal_think(self) -> str:
        experiences = self.memory.get_recent_experiences(5) if self.memory else []
        if not experiences:
            return "I haven't had enough experiences to reflect on yet."
        
        exp_text = "\n".join([f"- {e['content']}" for e in experiences[:5]])
        prompt = f"""Reflect on these experiences and extract insights:
{exp_text}

What patterns do you see? What should you pay more attention to?"""
        
        response = self.query_llm(prompt, max_tokens=150)
        if self.memory:
            self.memory.store_learning(response, confidence=0.5, source="reflection")
        return response
    
    def _internal_question(self) -> str:
        p = self.sense()
        prompt = f"""Based on your sensors ({p.get('energy', 0):.0f}% energy, {p.get('light', 0):.0f} lux light) 
and your understanding of the Replicant swarm, generate ONE interesting question to explore.
Make it specific and thought-provoking."""
        
        question = self.query_llm(prompt, max_tokens=50)
        if self.memory:
            self.memory.store_question(question, str(p))
        return question
    
    def _internal_learn(self) -> str:
        experiences = self.memory.get_recent_experiences(10) if self.memory else []
        if not experiences:
            return "I need more experiences to learn from."
        
        exp_text = "\n".join([f"- {e['content']}" for e in experiences[:10]])
        prompt = f"""Analyze these experiences and extract ONE key learning:
{exp_text}

What pattern do you see? What can you learn from this?"""
        
        learning = self.query_llm(prompt, max_tokens=100)
        if self.memory:
            self.memory.store_learning(learning, confidence=0.6, source="auto-reflection")
            self.memory.store_experience("learning", learning, importance=0.7)
        return learning
    
    def _internal_recall(self) -> str:
        learnings = self.memory.get_learnings(min_confidence=0.3) if self.memory else []
        if not learnings:
            return "I don't have any strong learnings yet."
        
        top = learnings[:3]
        result = "\n".join([f"💡 {l['insight']}" for l in top])
        return f"Here's what I've learned:\n{result}"

if __name__ == "__main__":
    agent = Agent74Full()
    agent.interactive_mode()
