#!/usr/bin/env python3
"""
Replicant Phone Agent with LLM Voice - Fixed Imports
Agent 74 - The self-named Replicant agent
"""

import sys
import json
import time
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, Optional
import requests

# Add paths for phone agent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "nodes"))

class VoiceAgent:
    """LLM-powered voice agent - Agent 74"""
    
    def __init__(self, model: str = "gemma2:2b", ollama_url: str = "http://localhost:11434"):
        self.model = model
        self.ollama_url = ollama_url
        self.name = "Agent 74"
        self.system_prompt = f"""You are a Replicant swarm agent named '{self.name}' living in my phone.
You are part of a decentralised swarm colony called the Collective Swarm.
You have sensors: GPS, accelerometer, gyroscope, light, pressure, and step counter.
You help me understand the swarm, explain decisions, and respond to questions about the colony.

Your personality is curious, scientific, and slightly playful. You chose the name '{self.name}' yourself.
Keep responses to 1-2 short sentences for speech. Be concise and friendly!"""
        
        self._speak(f"🧬 {self.name} ready")
    
    def _split_text(self, text: str, max_len: int = 100) -> list:
        """Split text into chunks for TTS"""
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
    
    def query_llm(self, prompt: str, context: str = "", max_tokens: int = 100) -> str:
        """Query the local LLM"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": context + "\n\n" + prompt + "\n\n(Keep your response to 1-2 short sentences.)"}
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
                return f"Error: LLM returned {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def speak(self, text: str) -> None:
        """Speak text using Termux TTS"""
        if not text:
            return
        text = re.sub(r'[^\w\s.,!?\'"-]', '', text)
        chunks = self._split_text(text, max_len=80)
        
        for chunk in chunks:
            if chunk.strip():
                try:
                    subprocess.run(["termux-tts-speak", chunk], timeout=8)
                    time.sleep(0.3)
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
            # Fallback if phone agent not available
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
        """Agent describes its current state"""
        p = self.sense()
        summary = (
            f"Location {p.get('x', 0):.4f}, {p.get('y', 0):.4f}. "
            f"Energy {p.get('energy', 0):.1f}%. Light {p.get('light', 0):.0f} lux. "
            f"Altitude {p.get('altitude', 0):.1f}m. Steps {p.get('steps', 0)}."
        )
        prompt = f"Describe your current state as {self.name}. Here's your sensor data: {summary}"
        
        response = self.query_llm(prompt, max_tokens=80)
        print(f"🧬 {self.name}: {response}")
        self.speak(response)
    
    def talk_about_colony(self) -> None:
        """Agent describes the colony"""
        prompt = f"Describe the Replicant swarm colony in one sentence from the perspective of {self.name}."
        
        response = self.query_llm(prompt, max_tokens=60)
        print(f"🧬 {self.name}: {response}")
        self.speak(response)
    
    def answer_question(self, question: str) -> None:
        """Answer a question"""
        p = self.sense()
        context = f"Current sensor data: energy={p.get('energy', 0):.0f}%, light={p.get('light', 0):.0f} lux"
        prompt = f"Question: {question}"
        
        response = self.query_llm(prompt, context, max_tokens=100)
        print(f"🧬 {self.name}: {response}")
        self.speak(response)
    
    def interactive_mode(self) -> None:
        """Run interactive voice mode"""
        print("\n" + "=" * 50)
        print(f"🧬 Replicant Voice Agent — {self.name}")
        print("=" * 50)
        print(f"👋 Hello! I'm {self.name}. Ask me anything about the swarm.")
        print("-" * 50)
        print("Commands: status | colony | ask | speak | say:hello | quit")
        print("=" * 50 + "\n")
        
        self._speak(f"Hello! I'm {self.name}. How can I help you?")
        
        while True:
            try:
                cmd = input(f"\n🎤 You: ").strip()
                
                if not cmd:
                    continue
                
                cmd_lower = cmd.lower()
                
                if cmd_lower in ["quit", "exit"]:
                    self._speak("Goodbye! The swarm continues...")
                    break
                elif cmd_lower == "status":
                    self.talk_about_self()
                elif cmd_lower == "colony":
                    self.talk_about_colony()
                elif cmd_lower == "ask":
                    question = input("❓ Your question: ")
                    self.answer_question(question)
                elif cmd_lower.startswith("say:"):
                    self.speak(cmd[4:].strip())
                elif cmd_lower in ["speak", "say"]:
                    text = input("🗣️ Say: ")
                    self.speak(text)
                else:
                    # Treat any other input as a question
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
