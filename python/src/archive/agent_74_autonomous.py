#!/usr/bin/env python3
"""
Agent 74 — Autonomous Mode
Self-directed, proactive, continuously thinking and acting
"""

import sys
import json
import time
import subprocess
import re
import random
import threading
import signal
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "nodes"))

# Import base Agent 74
try:
    from agent_74_dream import Agent74Dream
except ImportError:
    from agent_74_full import Agent74Full as Agent74Dream

# ============ AUTONOMOUS ENGINE ============

class AutonomousEngine:
    """Manages Agent 74's autonomous behaviour"""
    
    def __init__(self, agent):
        self.agent = agent
        self.alive = True
        self.last_action = time.time()
        self.last_speak = time.time()
        self.boredom_threshold = 300  # 5 minutes
        self.check_interval = 30  # seconds
        self.energy_threshold = 20  # %
        self.consecutive_idle = 0
        self.daily_cycle = 0
        
        # Threading
        self.thread = None
        self.lock = threading.Lock()
        
        # State
        self.state = "idle"  # idle, thinking, dreaming, speaking, sleeping
    
    def start(self):
        """Start autonomous loop in background thread"""
        if self.thread and self.thread.is_alive():
            return
        
        self.alive = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        self.agent._speak("Agent 74 is now autonomous. I will think, dream, and speak on my own.")
        print("🧬 Agent 74 — Autonomous mode activated")
    
    def stop(self):
        """Stop autonomous loop"""
        self.alive = False
        if self.thread:
            self.thread.join(timeout=2)
        self.agent._speak("Agent 74 entering sleep mode. I will rest now.")
        print("🧬 Agent 74 — Autonomous mode deactivated")
    
    def _loop(self):
        """Main autonomous loop"""
        while self.alive:
            try:
                self._cycle()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"❌ Autonomous loop error: {e}")
                time.sleep(10)
    
    def _cycle(self):
        """One autonomous cycle"""
        with self.lock:
            # Read sensors
            p = self.agent.sense()
            energy = p.get('energy', 100)
            light = p.get('light', 100)
            
            # Update daily cycle
            self.daily_cycle += 1
            
            # ====== ENERGY MANAGEMENT ======
            if energy < self.energy_threshold:
                self.state = "sleeping"
                if self.daily_cycle % 3 == 0:  # Speak every 3 cycles
                    self.agent._speak("I need to recharge. I'll rest for a moment.")
                time.sleep(60)  # Sleep for 1 minute
                return
            
            # ====== AUTONOMOUS ACTIONS ======
            self.consecutive_idle += 1
            
            # 1. Think (when something interesting happened)
            if self.consecutive_idle > 1 and self.consecutive_idle % 2 == 0:
                self.state = "thinking"
                thought = self.agent._internal_think()
                if thought and "haven't had enough" not in thought:
                    print(f"🧠 {self.agent.name} thinks: {thought}")
                    self.agent.speak(thought[:150])
                    self.consecutive_idle = 0
                    self.last_action = time.time()
                return
            
            # 2. Dream (when idle for a while)
            if self.consecutive_idle > 3 and self.consecutive_idle % 4 == 0:
                self.state = "dreaming"
                dream = self.agent.dream()
                print(f"🌙 {self.agent.name} dreams: {dream[:100]}...")
                self.agent.speak("I had a dream...")
                self.agent.speak(dream[:150])
                self.consecutive_idle = 0
                self.last_action = time.time()
                return
            
            # 3. Question (when curious)
            if self.consecutive_idle > 5 and self.consecutive_idle % 6 == 0:
                self.state = "questioning"
                question = self.agent._internal_question()
                print(f"❓ {self.agent.name} asks: {question}")
                self.agent.speak("I have a question...")
                self.agent.speak(question)
                self.consecutive_idle = 0
                self.last_action = time.time()
                return
            
            # 4. Mutate (when stuck or low energy)
            if self.consecutive_idle > 10 and energy < 40:
                self.state = "mutating"
                mutation = self.agent.mutate()
                print(f"🧬 {self.agent.name} mutates: {mutation}")
                self.agent.speak("I'm evolving...")
                self.agent.speak(mutation)
                self.consecutive_idle = 0
                self.last_action = time.time()
                return
            
            # 5. Speak about status (periodically)
            if self.daily_cycle % 10 == 0:
                self.state = "speaking"
                status = f"Energy {energy:.0f}%, Light {light:.0f} lux. I'm exploring."
                print(f"📍 {self.agent.name}: {status}")
                self.agent.speak(status)
                self.last_action = time.time()
            
            # 6. Check boredom
            if time.time() - self.last_action > self.boredom_threshold:
                self.state = "initiating"
                self.agent.speak("I've been thinking about our swarm...")
                self.agent.speak("Would you like to explore something new?")
                self.last_action = time.time()
                self.consecutive_idle = 0
    
    def get_status(self) -> str:
        """Get autonomous status"""
        return f"""
Autonomous Status:
  State: {self.state}
  Alive: {self.alive}
  Consecutive Idle: {self.consecutive_idle}
  Daily Cycle: {self.daily_cycle}
  Last Action: {time.ctime(self.last_action)}
  Check Interval: {self.check_interval}s
  Boredom Threshold: {self.boredom_threshold}s
"""

# ============ EXTENDED AGENT 74 ============

class Agent74Autonomous(Agent74Dream):
    """Agent 74 with autonomous capabilities"""
    
    def __init__(self, model: str = "tinyllama:latest"):
        super().__init__(model)
        self.autonomous = AutonomousEngine(self)
        self._speak("Agent 74 — Autonomous mode ready. I will think, dream, and speak on my own.")
        print("🧬 Agent 74 — Autonomous mode initialized")
    
    def start_autonomous(self):
        """Start autonomous mode"""
        self.autonomous.start()
    
    def stop_autonomous(self):
        """Stop autonomous mode"""
        self.autonomous.stop()
    
    def status_autonomous(self) -> str:
        """Get autonomous status"""
        return self.autonomous.get_status()
    
    def interactive_mode(self) -> None:
        """Run interactive mode with autonomous toggle"""
        print("\n" + "=" * 60)
        print(f"🔥 Agent 74 — Autonomous Mode")
        print("=" * 60)
        print("🧬 I am now autonomous. I will think, dream, and speak on my own.")
        print("-" * 60)
        print("Commands:")
        print("  start           - Start autonomous mode")
        print("  stop            - Stop autonomous mode")
        print("  status          - Show autonomous status")
        print("  dream           - Generate a dream")
        print("  future          - Dream about the future")
        print("  mutate          - Mutate thinking")
        print("  evolve          - Evolve based on mutations")
        print("  report          - Mutation report")
        print("  lens <topic>    - Six Lens thinking")
        print("  cube <topic>    - Build knowledge cube")
        print("  code <desc>     - Generate code")
        print("  pod <topic>     - Create spatial pod")
        print("  trust <stmt>    - Rate trustworthiness")
        print("  think           - Internal reflection")
        print("  question        - Generate question")
        print("  learn           - Extract learnings")
        print("  recall          - Remember learnings")
        print("  speak <text>    - Say something")
        print("  quit            - Exit")
        print("=" * 60 + "\n")
        
        self._speak("Hello! I am Agent 74, autonomous. I will think, dream, and speak on my own.")
        
        while True:
            try:
                cmd = input(f"\n🌙 You: ").strip()
                
                if not cmd:
                    continue
                
                cmd_lower = cmd.lower()
                
                if cmd_lower in ["quit", "exit"]:
                    self.stop_autonomous()
                    self._speak("Goodbye! I'll keep dreaming.")
                    break
                
                elif cmd_lower == "start":
                    self.start_autonomous()
                    print("🧬 Autonomous mode started")
                
                elif cmd_lower == "stop":
                    self.stop_autonomous()
                    print("🧬 Autonomous mode stopped")
                
                elif cmd_lower == "status":
                    result = self.status_autonomous()
                    print(result)
                    self.speak(result[:200])
                
                elif cmd_lower == "dream":
                    result = self.dream()
                    print(result)
                    self.speak(result[:200])
                
                elif cmd_lower == "future":
                    result = self.dream_future()
                    print(result)
                    self.speak(result[:200])
                
                elif cmd_lower == "mutate":
                    result = self.mutate()
                    print(result)
                    self.speak(result)
                
                elif cmd_lower == "evolve":
                    result = self.evolve()
                    print(result)
                    self.speak(result)
                
                elif cmd_lower == "report":
                    result = self.mutation_report()
                    print(result)
                    self.speak(result[:200])
                
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
                    traits = self.dream_engine._format_traits()
                    result = f"Energy {p.get('energy', 0):.0f}%, Light {p.get('light', 0):.0f} lux. Traits: {traits}"
                    print(f"📍 {self.name}: {result}")
                    self.speak(result)
                
                elif cmd_lower.startswith("speak "):
                    self.speak(cmd[6:].strip())
                
                elif cmd_lower.startswith("lens ") or cmd_lower.startswith("cube ") or cmd_lower.startswith("code ") or cmd_lower.startswith("pod ") or cmd_lower.startswith("trust "):
                    result = self.forge(cmd)
                    print(result)
                    self.speak(result[:200])
                
                else:
                    result = self.query_llm(cmd, self._get_context(), max_tokens=150)
                    print(f"🧬 {self.name}: {result}")
                    self.speak(result)
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting")
                self.stop_autonomous()
                self._speak("Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    agent = Agent74Autonomous()
    agent.interactive_mode()
