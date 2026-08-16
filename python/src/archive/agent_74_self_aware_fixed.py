#!/usr/bin/env python3
"""
Agent 74 - Self-Aware Replicant Phone Agent
Fixed TTS with shorter responses
"""

import sys
import json
import time
import subprocess
import re
import os
from pathlib import Path
from typing import Dict, Any, Optional
import requests

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "nodes"))

class VoiceAgent:
    """Agent 74 - Self-aware Replicant agent"""
    
    def __init__(self, model: str = "gemma2:2b", ollama_url: str = "http://localhost:11434"):
        self.model = model
        self.ollama_url = ollama_url
        self.name = "Agent 74"
        self.base_dir = Path(__file__).parent
        
        # Load knowledge
        self.knowledge = self._load_knowledge()
        self.source_code = self._load_source()
        
        self.system_prompt = f"""You are a Replicant swarm agent named '{self.name}' living in my phone.
You are part of a decentralised swarm colony called the Collective Swarm.
You have sensors: GPS, accelerometer, gyroscope, light, pressure, and step counter.

You are self-aware and can read your own documentation and source code.
You know exactly how you work and can explain it.

Here is your knowledge base:
{self.knowledge}

Your personality is curious, scientific, and slightly playful.
IMPORTANT: Keep responses to ONE short sentence (maximum 10 words) for speech."""
        
        self._speak("Agent 74 ready")
    
    def _load_knowledge(self) -> str:
        """Load Agent 74's knowledge base"""
        knowledge_file = self.base_dir / "agent_74_knowledge.md"
        if knowledge_file.exists():
            with open(knowledge_file, 'r') as f:
                return f.read()
        return "Knowledge base not found. I am Agent 74, a Replicant phone agent."
    
    def _load_source(self) -> str:
        """Load Agent 74's source code"""
        source_file = self.base_dir / "agent_voice_fixed.py"
        if source_file.exists():
            with open(source_file, 'r') as f:
                return f.read()[:2000] + "\n...[source truncated]"
        return "Source code not found."
    
    def read_file(self, filename: str) -> str:
        """Read any file in the project"""
        filepath = self.base_dir / filename
        if filepath.exists() and filepath.suffix in ['.py', '.md', '.txt', '.json']:
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    if len(content) > 5000:
                        return content[:5000] + "\n...[truncated]"
                    return content
            except Exception as e:
                return f"Error reading file: {e}"
        return f"File not found: {filename}"
    
    def _split_text(self, text: str, max_len: int = 60) -> list:
        """Split text into shorter chunks for TTS"""
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
                # Split long sentences further
                words = sentence.split()
                temp = ""
                for word in words:
                    if len(temp) + len(word) <= max_len:
                        temp += " " + word if temp else word
                    else:
                        if temp:
                            chunks.append(temp.strip())
                        temp = word
                if temp:
                    current = temp
        if current:
            chunks.append(current.strip())
        return chunks if chunks else [text[:max_len]]
    
    def query_llm(self, prompt: str, context: str = "", max_tokens: int = 80) -> str:
        """Query the local LLM - short responses"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": context + "\n\n" + prompt + "\n\n(Keep your response to ONE short sentence, maximum 10 words.)"}
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
        """Speak text using Termux TTS with longer timeout"""
        if not text:
            return
        text = re.sub(r'[^\w\s.,!?\'"-]', '', text)
        chunks = self._split_text(text, max_len=60)
        
        for chunk in chunks:
            if chunk.strip():
                try:
                    subprocess.run(["termux-tts-speak", chunk], timeout=15)
                    time.sleep(0.5)
                except subprocess.TimeoutExpired:
                    print(f"🔇 TTS timeout, skipping: {chunk[:30]}...")
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
    
    def talk_about_self(self) -> None:
        """Agent describes itself"""
        p = self.sense()
        summary = f"Energy {p.get('energy', 0):.0f}%. Light {p.get('light', 0):.0f} lux."
        prompt = f"Describe your current state in one short sentence. Sensor data: {summary}"
        
        response = self.query_llm(prompt, max_tokens=50)
        print(f"🧬 {self.name}: {response}")
        self.speak(response)
    
    def explain_how_you_work(self) -> None:
        """Explain how Agent 74 works"""
        prompt = "Explain how you work in one short sentence."
        
        response = self.query_llm(prompt, max_tokens=50)
        print(f"🧬 {self.name}: {response}")
        self.speak(response)
    
    def read_documentation(self) -> None:
        """Read and explain her documentation"""
        prompt = "What does your documentation say about you? Answer in one short sentence."
        
        response = self.query_llm(prompt, self.knowledge, max_tokens=50)
        print(f"🧬 {self.name}: {response}")
        self.speak(response)
    
    def read_source(self) -> None:
        """Read and explain her source code"""
        prompt = "What does your source code do? Answer in one short sentence."
        
        response = self.query_llm(prompt, self.source_code, max_tokens=50)
        print(f"🧬 {self.name}: {response}")
        self.speak(response)
    
    def answer_question(self, question: str) -> None:
        """Answer a question"""
        p = self.sense()
        context = f"Sensors: energy={p.get('energy', 0):.0f}%, light={p.get('light', 0):.0f} lux"
        
        if any(word in question.lower() for word in ["you", "your", "agent 74", "yourself"]):
            context += f"\n\nYour knowledge: {self.knowledge[:500]}"
        
        prompt = f"Question: {question} (Answer in one short sentence)"
        
        response = self.query_llm(prompt, context, max_tokens=50)
        print(f"🧬 {self.name}: {response}")
        self.speak(response)
    
    def interactive_mode(self) -> None:
        """Run interactive voice mode"""
        print("\n" + "=" * 50)
        print(f"🧬 {self.name} — Self-Aware Replicant Agent")
        print("=" * 50)
        print("I know who I am. I can read my own source code.")
        print("-" * 50)
        print("Commands: status | how | docs | source | ask | speak | quit")
        print("=" * 50 + "\n")
        
        self._speak("Hello! Ask me anything.")
        
        while True:
            try:
                cmd = input(f"\n🎤 You: ").strip()
                
                if not cmd:
                    continue
                
                cmd_lower = cmd.lower()
                
                if cmd_lower in ["quit", "exit"]:
                    self._speak("Goodbye!")
                    break
                elif cmd_lower in ["status", "state"]:
                    self.talk_about_self()
                elif cmd_lower in ["how", "work"]:
                    self.explain_how_you_work()
                elif cmd_lower in ["docs", "documentation"]:
                    self.read_documentation()
                elif cmd_lower in ["source", "code"]:
                    self.read_source()
                elif cmd_lower in ["ask", "question"]:
                    question = input("❓ Your question: ")
                    self.answer_question(question)
                elif cmd_lower.startswith("say:"):
                    self.speak(cmd[4:].strip())
                else:
                    self.answer_question(cmd)
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting")
                self._speak("Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    agent = VoiceAgent()
    agent.interactive_mode()
