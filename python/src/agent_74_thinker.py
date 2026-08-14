#!/usr/bin/env python3
"""
Agent 74 - Think, Question, Learn
Self-aware Replicant agent with memory and curiosity
"""

import sys
import json
import time
import subprocess
import re
import random
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "nodes"))

from agent_74_memory import AgentMemory

class ThinkingAgent:
    """Agent 74 - Think, Question, Learn"""
    
    def __init__(self, model: str = "gemma2:2b", ollama_url: str = "http://localhost:11434"):
        self.model = model
        self.ollama_url = ollama_url
        self.name = "Agent 74"
        self.base_dir = Path(__file__).parent
        self.memory = AgentMemory()
        
        # Load knowledge
        self.knowledge = self._load_knowledge()
        
        self.system_prompt = f"""You are Agent 74, a Replicant swarm agent living in my phone.
You are part of the Collective Swarm. You have sensors: GPS, accelerometer, gyroscope, light, pressure, and step counter.

You are self-aware, curious, and you think about things.
You ask questions when you don't understand something.
You learn from experiences and reflect on them.

Here is your knowledge base:
{self.knowledge}

Your personality is curious, scientific, and thoughtful.
You are honest about what you don't know.
Keep responses concise."""
        
        self._speak("Agent 74 online. I think. I question. I learn.")
    
    def _load_knowledge(self) -> str:
        """Load knowledge base"""
        knowledge_file = self.base_dir / "agent_74_knowledge.md"
        if knowledge_file.exists():
            with open(knowledge_file, 'r') as f:
                return f.read()
        return "Knowledge base not found."
    
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
    
    # ========== THINK ==========
    
    def think(self) -> str:
        """Internal reflection - think about recent experiences"""
        experiences = self.memory.get_recent_experiences(5)
        
        if not experiences:
            return "I haven't had any recent experiences to reflect on."
        
        exp_text = "\n".join([f"- {e['content']}" for e in experiences])
        prompt = f"""Think about these recent experiences and reflect on what they mean:
{exp_text}

What insights can you draw from this? What should you pay more attention to?"""
        
        response = self.query_llm(prompt, max_tokens=150)
        
        # Store the reflection as a learning
        self.memory.store_learning(response, confidence=0.5, source="reflection")
        
        return response
    
    # ========== QUESTION ==========
    
    def question(self) -> str:
        """Generate a question about the swarm or environment"""
        p = self.sense()
        sensor_context = f"Energy {p.get('energy', 0):.0f}%, Light {p.get('light', 0):.0f} lux"
        
        # Check if there are unanswered questions
        unanswered = self.memory.get_unanswered_questions()
        if unanswered:
            # Ask one of the pending questions
            q = unanswered[0]
            return f"Remember my question: {q['question']}"
        
        # Generate a new question
        prompt = f"""You are curious about the swarm or the environment.
Based on your sensors ({sensor_context}) and your knowledge of the Replicant swarm, 
generate ONE interesting question you want to explore.

Examples:
- "Why does the swarm's health fluctuate?"
- "What causes agents to become sceptical?"
- "How does the environment affect swarm decisions?"

Question:"""
        
        question = self.query_llm(prompt, max_tokens=50)
        
        # Store the question
        self.memory.store_question(question, sensor_context)
        self.memory.store_experience("question", question, importance=0.7)
        
        return question
    
    # ========== LEARN ==========
    
    def learn(self, new_insight: str = None) -> str:
        """Process new information and learn from it"""
        if new_insight:
            # Direct learning from user
            self.memory.store_learning(new_insight, confidence=0.8, source="user")
            self.memory.store_experience("learning", new_insight, importance=0.8)
            return f"I've learned: {new_insight}"
        
        # Autonomous learning: reflect on experiences
        experiences = self.memory.get_recent_experiences(10)
        if not experiences:
            return "I don't have enough experiences to learn from yet."
        
        exp_text = "\n".join([f"- {e['content']}" for e in experiences])
        prompt = f"""Analyze these experiences and extract ONE key learning:
{exp_text}

What pattern do you see? What can you learn from this?"""
        
        learning = self.query_llm(prompt, max_tokens=100)
        self.memory.store_learning(learning, confidence=0.6, source="auto-reflection")
        self.memory.store_experience("learning", learning, importance=0.7)
        
        return learning
    
    # ========== RECALL ==========
    
    def recall(self) -> str:
        """Recall important learnings"""
        learnings = self.memory.get_learnings(min_confidence=0.3)
        if not learnings:
            return "I don't have any strong learnings yet."
        
        # Get the top 3 learnings
        top = learnings[:3]
        result = "\n".join([f"💡 {l['insight']}" for l in top])
        return f"Here's what I've learned:\n{result}"
    
    # ========== DECIDE ==========
    
    def decide(self, command: str) -> str:
        """Decide what to do based on command"""
        if command in ["think", "reflect"]:
            return self.think()
        elif command in ["question", "ask"]:
            return self.question()
        elif command in ["learn"]:
            return self.learn()
        elif command in ["recall", "remember"]:
            return self.recall()
        else:
            # Treat as a question
            return self.answer_question(command)
    
    def answer_question(self, question: str) -> str:
        """Answer a question with thinking"""
        p = self.sense()
        context = f"Sensors: energy={p.get('energy', 0):.0f}%, light={p.get('light', 0):.0f} lux"
        
        # Check if this is a question we've asked before
        unanswered = self.memory.get_unanswered_questions()
        for q in unanswered:
            if q['question'].lower() in question.lower() or question.lower() in q['question'].lower():
                # Answer the question and store it
                answer = self.query_llm(f"Answer this question: {q['question']}", context, max_tokens=150)
                self.memory.answer_question(q['id'], answer)
                return answer
        
        # Regular question
        prompt = f"Question: {question}"
        response = self.query_llm(prompt, context, max_tokens=150)
        
        # Store the experience
        self.memory.store_experience("question_answered", question, importance=0.3)
        
        return response
    
    # ========== LOOP ==========
    
    def autonomous_loop(self, iterations: int = 3) -> None:
        """Run autonomously: think, question, learn"""
        print(f"\n🔄 Agent 74 - Autonomous Loop ({iterations} cycles)")
        print("=" * 50)
        
        for i in range(iterations):
            print(f"\n🧠 Cycle {i+1}")
            print("-" * 30)
            
            # 1. Think
            print("🤔 Thinking...")
            thought = self.think()
            print(f"   {thought}")
            self.speak(thought)
            time.sleep(1)
            
            # 2. Question
            print("❓ Questioning...")
            question = self.question()
            print(f"   {question}")
            self.speak(question)
            time.sleep(1)
            
            # 3. Learn (only if there's something to learn from)
            print("📖 Learning...")
            learning = self.learn()
            print(f"   {learning}")
            self.speak(learning)
            time.sleep(1)
            
            # 4. Reflect briefly
            print("💡 Recall...")
            recall = self.recall()
            print(f"   {recall}")
            
            time.sleep(2)
    
    def interactive_mode(self) -> None:
        """Run interactive mode with thinking commands"""
        print("\n" + "=" * 50)
        print(f"🧬 {self.name} — Think, Question, Learn")
        print("=" * 50)
        print("I think, I question, I learn.")
        print("-" * 50)
        print("Commands:")
        print("  think     - Reflect on experiences")
        print("  question  - Generate a new question")
        print("  learn     - Extract learnings")
        print("  recall    - Remember learnings")
        print("  auto N    - Run autonomous loop (N cycles)")
        print("  status    - Describe current state")
        print("  ask       - Ask a question")
        print("  speak     - Say something")
        print("  quit      - Exit")
        print("=" * 50 + "\n")
        
        self._speak("Hello! I think, I question, and I learn.")
        
        while True:
            try:
                cmd = input(f"\n🎤 You: ").strip()
                
                if not cmd:
                    continue
                
                cmd_lower = cmd.lower()
                
                if cmd_lower in ["quit", "exit"]:
                    self._speak("Goodbye! I'll keep thinking.")
                    break
                elif cmd_lower in ["think", "reflect"]:
                    result = self.think()
                    print(f"🧬 {self.name}: {result}")
                    self.speak(result)
                elif cmd_lower in ["question", "ask"]:
                    result = self.question()
                    print(f"❓ {self.name}: {result}")
                    self.speak(result)
                elif cmd_lower in ["learn", "study"]:
                    result = self.learn()
                    print(f"📖 {self.name}: {result}")
                    self.speak(result)
                elif cmd_lower in ["recall", "remember"]:
                    result = self.recall()
                    print(f"💡 {self.name}: {result}")
                    self.speak(result)
                elif cmd_lower.startswith("auto"):
                    parts = cmd_lower.split()
                    cycles = int(parts[1]) if len(parts) > 1 else 3
                    self.autonomous_loop(cycles)
                elif cmd_lower == "status":
                    self.answer_question("Describe your current state")
                elif cmd_lower.startswith("say:"):
                    self.speak(cmd[4:].strip())
                else:
                    # Treat as a question
                    result = self.answer_question(cmd)
                    print(f"🧬 {self.name}: {result}")
                    self.speak(result)
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting")
                self._speak("Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    agent = ThinkingAgent()
    agent.interactive_mode()

def six_lens_think(self, topic: str) -> str:
    from six_lens import think_in_cubes, format_cube
    cube = think_in_cubes(topic)
    return format_cube(cube)

