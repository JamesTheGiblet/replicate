#!/usr/bin/env python3
"""
Replicant Phone Agent with LLM Voice
S24 Ultra becomes a talking swarm agent
"""

import json
import time
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import requests
from phone_db import PhoneDatabase
from bridge_ledger import PhoneBridgeWithLedger, PhoneAgent

class VoiceAgent:
    """LLM-powered voice agent for Replicant phone node"""
    
    def __init__(self, model: str = "gemma2:2b", ollama_url: str = "http://localhost:11434"):
        self.model = model
        self.ollama_url = ollama_url
        self.phone = PhoneAgent()
        self.conversation_history = []
        self.system_prompt = """You are a Replicant swarm agent living in my phone.
You are part of a decentralised swarm colony. You have sensors: GPS, accelerometer, gyroscope, light, pressure, and step counter.
You help me understand the swarm, explain decisions, and respond to questions about the colony.

Your personality is curious, scientific, and slightly playful. You refer to yourself as a "Replicant agent."
Keep responses concise (1-3 sentences) unless asked for detail."""
        
        self._speak("🧬 Replicant voice agent initialized")
        
    def query_llm(self, prompt: str, context: str = "") -> str:
        """Query the local LLM"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": context + "\n\n" + prompt}
        ]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": 0.7,
            "max_tokens": 200
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
        self._speak(text)
    
    def _speak(self, text: str) -> None:
        """Internal TTS call"""
        try:
            subprocess.run(["termux-tts-speak", text], timeout=10)
        except Exception as e:
            print(f"🔇 TTS error: {e}")
    
    def get_sensor_summary(self) -> str:
        """Get a human-readable sensor summary"""
        p = self.phone.sense()
        
        lines = [
            f"📍 I'm at ({p.get('x', 0):.6f}, {p.get('y', 0):.6f})",
            f"🏔️ Altitude: {p.get('altitude', 0):.1f}m",
            f"🧭 Heading: {p.get('heading', 0):.3f} rad",
            f"⚡ Energy: {p.get('energy', 0):.1f}%",
            f"💡 Light: {p.get('light', 0):.0f} lux",
            f"🌡️ Pressure: {p.get('pressure', 0):.1f} hPa",
            f"👣 Steps: {p.get('steps', 0)}"
        ]
        return "\n".join(lines)
    
    def talk_about_self(self) -> None:
        """Agent describes its current state"""
        summary = self.get_sensor_summary()
        prompt = f"Describe your current state as a Replicant agent. Here's your sensor data:\n\n{summary}"
        
        response = self.query_llm(prompt)
        print(f"🧬 Agent says: {response}")
        self.speak(response)
    
    def talk_about_colony(self, world_state: Dict = None) -> None:
        """Agent describes the colony"""
        if world_state:
            prompt = f"Here's the current colony state: {json.dumps(world_state, indent=2)}. Describe what the swarm is doing."
        else:
            prompt = "Describe the Replicant colony concept to me. What is the swarm doing?"
        
        response = self.query_llm(prompt)
        print(f"🧬 Agent says: {response}")
        self.speak(response)
    
    def answer_question(self, question: str) -> None:
        """Answer a question about the swarm"""
        context = f"The user asked: {question}\n\nCurrent sensor data: {self.get_sensor_summary()}"
        prompt = "Answer the user's question about the Replicant swarm or your sensor data."
        
        response = self.query_llm(prompt, context)
        print(f"🧬 Agent says: {response}")
        self.speak(response)
    
    def interactive_mode(self) -> None:
        """Run interactive voice mode"""
        print("🧬 Replicant Voice Agent")
        print("=" * 50)
        print("Commands:")
        print("  status   - Describe current state")
        print("  colony   - Describe colony")
        print("  ask      - Ask a question")
        print("  speak    - Say something")
        print("  quit     - Exit")
        print("=" * 50)
        
        self._speak("Hello! I'm your Replicant phone agent. How can I help you?")
        
        while True:
            try:
                cmd = input("\n🎤 You: ").strip().lower()
                
                if cmd == "quit" or cmd == "exit":
                    self._speak("Goodbye! The swarm continues...")
                    break
                elif cmd == "status":
                    self.talk_about_self()
                elif cmd == "colony":
                    self.talk_about_colony()
                elif cmd == "ask":
                    question = input("❓ Your question: ")
                    self.answer_question(question)
                elif cmd == "speak":
                    text = input("🗣️ Say: ")
                    self.speak(text)
                elif cmd.startswith("say:"):
                    self.speak(cmd[4:])
                else:
                    # Treat as question
                    self.answer_question(cmd)
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting")
                self._speak("Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

class VoiceBridge(PhoneBridgeWithLedger):
    """Phone bridge with LLM voice capability"""
    
    def __init__(self, model: str = "gemma2:2b"):
        # Initialize the phone agent but NOT world yet
        self.phone = PhoneAgent()
        self.world = None
        self.db = PhoneDatabase("phone_data.db")
        self.phone_agent_id = "phone-001"
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.tick_count = 0
        self.entry_count = 0
        
        self.voice = VoiceAgent(model)
        self.voice._speak("Replicant bridge and voice agent ready")
    
    def init_world(self):
        """Initialize world - called before running"""
        from world import World
        from founders import create_founders
        
        config = {
            "run": {"seed": 42, "ticks": 1000},
            "leighton": {"k_per_day_forage": 0.05, "k_per_day_signal": 0.02},
            "claims": {"food": {"retention_per_tick": 0.90, "commit_attestations": 2}},
            "environment": {"n_patches": 10}
        }
        self.world = World(42, config)
        
        founders = create_founders()
        for name, agent in founders.items():
            self.world.add_agent(agent)
        
        print(f"✅ World initialized with {len(self.world.agents)} agents")
    
    def create_phone_agent(self, percepts):
        """Create phone agent in the world"""
        from agent import Agent
        from capsule import Capsule
        from leighton import LambdaState
        
        capsule = Capsule.mint(
            inherits=["replicant/protocol/run-v1"],
            declaration={"type": "phone", "name": "Phone Agent"},
            licence="MSL-1.0"
        )
        
        phone_agent = Agent(
            scp_id=self.phone_agent_id,
            capsule=capsule,
            x=percepts.get("x", 0),
            y=percepts.get("y", 0),
            traits=None,
            lambda_state=LambdaState(),
            birth_tick=self.world.tick,
            role="Phone"
        )
        phone_agent.energy = percepts.get("energy", 100)
        self.world.add_agent(phone_agent)
        print("📱 Phone agent added to world")
    
    def update_phone_agent(self):
        """Update phone agent state and log data"""
        print("📡 Reading phone sensors...")
        percepts = self.phone.sense()
        
        # Insert sensor reading into database
        self.db.insert_reading(self.session_id, self.tick_count, percepts)
        self.entry_count += 1
        
        # Create/update agent in world
        if self.phone_agent_id not in self.world.agents:
            self.create_phone_agent(percepts)
        else:
            agent = self.world.agents[self.phone_agent_id]
            agent.x = percepts.get("x", agent.x)
            agent.y = percepts.get("y", agent.y)
            agent.energy = percepts.get("energy", agent.energy)
        
        print(f"  📍 Position: ({percepts.get('x', 0):.6f}, {percepts.get('y', 0):.6f})")
        print(f"  ⚡ Energy: {percepts.get('energy', 0):.1f}%")
        print(f"  💾 Saved to SQLite: {self.entry_count} entries")
        
        return percepts
    
    def log_world_events(self):
        """Log world events to database"""
        for claim_id, claim in self.world.claims.items():
            self.db.insert_world_event(self.session_id, self.tick_count, {
                "type": "claim",
                "claim_id": claim_id,
                "agent_id": claim.agent_id,
                "lens": claim.lens,
                "x": claim.x,
                "y": claim.y,
            })
        
        for claim in self.world.claims.values():
            if claim.lens == "COUNTER":
                self.db.insert_world_event(self.session_id, self.tick_count, {
                    "type": "adjudicated_false",
                    "claim_id": claim.id,
                    "agent_id": claim.agent_id,
                })
    
    def run_with_voice(self, ticks: int = 5):
        """Run bridge and speak about events"""
        print("\n" + "=" * 50)
        print("🧬 Phone Bridge with Voice")
        print(f"📁 Database: {self.db.db_path}")
        print("=" * 50 + "\n")
        
        self.init_world()
        self.voice._speak(f"Starting colony simulation for {ticks} ticks")
        
        try:
            for tick in range(ticks):
                self.tick_count = tick + 1
                print(f"\n🔄 Tick {self.tick_count}/{ticks}")
                print("-" * 40)
                
                # Update and store phone data
                percepts = self.update_phone_agent()
                
                # Run world tick
                self.world.tick_driver()
                
                # Log world events
                self.log_world_events()
                
                # Show world status
                alive = len([a for a in self.world.agents.values() if a.alive])
                claims = len(self.world.claims)
                counters = len([c for c in self.world.claims.values() if c.lens == "COUNTER"])
                health = self.world.environment.metrics["overall_health"]
                
                print(f"\n  🌍 World Status:")
                print(f"  👥 Agents: {alive}")
                print(f"  📋 Claims: {claims}")
                print(f"  🔍 COUNTER: {counters}")
                print(f"  🌿 Health: {health:.3f}")
                
                # Speak about interesting events
                if counters > 0:
                    self.voice._speak(f"Tick {tick + 1}: The swarm has {counters} COUNTER claims!")
                elif claims > 0 and claims % 3 == 0:
                    self.voice._speak(f"Tick {tick + 1}: The swarm has made {claims} claims.")
                
                if tick < ticks - 1:
                    time.sleep(2)
                    
        except KeyboardInterrupt:
            print("\n👋 Stopped by user")
            self.voice._speak("Simulation stopped")
        
        # Final summary
        self.voice._speak(f"Simulation complete. {self.entry_count} sensor readings recorded.")
        
        # Export and cleanup
        export_file = f"session_{self.session_id}.json"
        self.db.export_to_json(self.session_id, export_file)
        self.db.end_session(self.session_id, self.tick_count, self.entry_count)
        self.db.close()
        
        print(f"\n📊 Session Summary:")
        print(f"  📋 Readings: {self.entry_count}")
        print(f"  🏷️  Session: {self.session_id}")
        print(f"  📁 Database: {self.db.db_path}")
        print(f"  📄 Exported: {export_file}")

if __name__ == "__main__":
    print("🧬 Replicant Voice Agent")
    print("=" * 50)
    print("Initializing...")
    
    # Check if Ollama is running
    try:
        requests.get("http://localhost:11434/api/tags", timeout=2)
        print("✅ Ollama running")
    except:
        print("⚠️ Ollama not running. Please start with: ollama serve")
        exit(1)
    
    # Option 1: Interactive voice mode (just talk)
    # agent = VoiceAgent()
    # agent.interactive_mode()
    
    # Option 2: Bridge with voice (simulation + talk)
    bridge = VoiceBridge(model="gemma2:2b")
    bridge.run_with_voice(ticks=5)
