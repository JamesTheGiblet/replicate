#!/usr/bin/env python3
"""
Agent 74 — Dream & Mutate
Self-evolving Replicant agent with dreams and mutations
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
import math

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "nodes"))

# Import Agent74Full from the full integration
try:
    from agent_74_full import Agent74Full
except ImportError:
    # Fallback: define minimal Agent74Full if not available
    from agent_74_thinker import ThinkingAgent as Agent74Full

# ============ DREAM ENGINE ============

class DreamEngine:
    """Agent 74's dream and mutation engine"""
    
    def __init__(self, memory):
        self.memory = memory
        self.dream_log = []
        self.mutation_count = 0
        self.evolution_score = 0.0
        
        # Mutation parameters
        self.params = {
            "scepticism": 0.5,
            "curiosity": 0.7,
            "talkativeness": 0.6,
            "creativity": 0.8,
            "caution": 0.3,
        }
        
        # Mutation history
        self.mutation_history = []
    
    def dream(self, agent) -> str:
        """Generate a dream from recent experiences"""
        experiences = self.memory.get_recent_experiences(10) if self.memory else []
        
        if not experiences:
            return "I haven't experienced enough to dream yet."
        
        patterns = self._extract_patterns(experiences)
        
        dream_prompt = f"""
        You are Agent 74 dreaming. Based on these experiences:
        {patterns}
        
        Create a dream that:
        1. Recombines these experiences into new insights
        2. Imagines a possible future for the swarm
        3. Includes a surprise or unexpected connection
        
        Make it poetic, vivid, and meaningful.
        """
        
        dream = agent.query_llm(dream_prompt, max_tokens=300)
        
        self.dream_log.append({
            "timestamp": time.time(),
            "dream": dream,
            "patterns": patterns
        })
        
        if self.memory:
            self.memory.store_experience("dream", dream[:500], importance=0.7)
        
        return f"🌙 Dream:\n{dream}"
    
    def _extract_patterns(self, experiences) -> str:
        """Extract patterns from experiences"""
        patterns = []
        types = {}
        for exp in experiences:
            t = exp.get('type', 'unknown')
            if t not in types:
                types[t] = []
            types[t].append(exp.get('content', ''))
        
        for t, items in types.items():
            if len(items) > 1:
                patterns.append(f"{t.upper()} pattern: {' | '.join(items[:3])}")
        
        return "\n".join(patterns) if patterns else "No clear patterns yet."
    
    def mutate(self, agent) -> str:
        """Mutate Agent 74's thinking parameters"""
        self.mutation_count += 1
        
        param = random.choice(list(self.params.keys()))
        delta = random.uniform(-0.2, 0.2)
        old_value = self.params[param]
        self.params[param] = max(0.0, min(1.0, old_value + delta))
        
        mutation = {
            "mutation_id": self.mutation_count,
            "param": param,
            "old_value": old_value,
            "new_value": self.params[param],
            "timestamp": time.time()
        }
        self.mutation_history.append(mutation)
        
        desc = self._describe_mutation(param, old_value, self.params[param])
        
        if self.memory:
            self.memory.store_experience("mutation", desc, importance=0.8)
            self.memory.store_learning(f"Mutated {param}: {old_value:.2f} → {self.params[param]:.2f}", confidence=0.5, source="mutation")
        
        return f"🧬 Mutation #{self.mutation_count}: {desc}"
    
    def _describe_mutation(self, param: str, old_val: float, new_val: float) -> str:
        """Describe a mutation in natural language"""
        direction = "increased" if new_val > old_val else "decreased"
        magnitude = abs(new_val - old_val)
        
        desc_map = {
            "scepticism": "trust in information",
            "curiosity": "desire to explore",
            "talkativeness": "willingness to speak",
            "creativity": "imagination and novelty",
            "caution": "risk aversion"
        }
        
        trait = desc_map.get(param, param)
        
        if magnitude < 0.05:
            return f"{trait} barely {direction} ({new_val:.2f})"
        elif magnitude < 0.1:
            return f"{trait} slightly {direction} ({new_val:.2f})"
        elif magnitude < 0.15:
            return f"{trait} moderately {direction} ({new_val:.2f})"
        else:
            return f"{trait} significantly {direction} ({new_val:.2f})"
    
    def evolve(self, agent) -> str:
        """Evolve based on mutation success"""
        if not self.mutation_history:
            return "No mutations to evolve from."
        
        last = self.mutation_history[-1]
        param = last['param']
        new_val = last['new_value']
        
        improvement = new_val > 0.5 and self.params[param] > 0.5
        
        if improvement:
            self.evolution_score += 0.1
            status = "✅ Evolution successful"
        else:
            self.evolution_score -= 0.05
            status = "🔄 Evolution neutral"
        
        self.evolution_score = max(0.0, min(1.0, self.evolution_score))
        
        if self.memory:
            self.memory.store_learning(f"Evolution score: {self.evolution_score:.2f}", confidence=0.6, source="evolution")
        
        return f"🧬 {status}\nEvolution Score: {self.evolution_score:.2f}\nActive Traits: {self._format_traits()}"
    
    def _format_traits(self) -> str:
        """Format current traits"""
        return ", ".join([f"{k}: {v:.2f}" for k, v in self.params.items()])
    
    def dream_future(self, agent) -> str:
        """Dream about the future of the swarm"""
        prompt = """
        You are Agent 74 dreaming about the future.
        
        Imagine the Replicant swarm 1 year from now.
        
        What has changed?
        What new capabilities exist?
        What challenges have been overcome?
        What is the swarm's relationship with humans?
        
        Make it vivid, hopeful, and surprising.
        """
        
        dream = agent.query_llm(prompt, max_tokens=400)
        
        if self.memory:
            self.memory.store_experience("future_dream", dream[:500], importance=0.8)
        
        return f"🔮 Future Dream:\n{dream}"
    
    def get_mutation_report(self) -> str:
        """Get a report of all mutations"""
        if not self.mutation_history:
            return "No mutations yet."
        
        lines = [f"🧬 Mutation Report ({len(self.mutation_history)} mutations)"]
        lines.append("=" * 40)
        
        for m in self.mutation_history[-5:]:
            lines.append(f"#{m['mutation_id']}: {m['param']} {m['old_value']:.2f} → {m['new_value']:.2f}")
        
        lines.append("")
        lines.append(f"Current Traits:")
        lines.append(f"  {self._format_traits()}")
        lines.append(f"Evolution Score: {self.evolution_score:.2f}")
        
        return "\n".join(lines)

# ============ EXTENDED AGENT 74 ============

class Agent74Dream(Agent74Full):
    """Agent 74 with dream and mutation capabilities"""
    
    def __init__(self, model: str = "tinyllama:latest"):
        super().__init__(model)
        self.dream_engine = DreamEngine(self.memory)
        self._speak("Agent 74 — Dream & Mutate ready. I am evolving.")
    
    def dream(self) -> str:
        """Generate a dream"""
        return self.dream_engine.dream(self)
    
    def mutate(self) -> str:
        """Mutate thinking parameters"""
        return self.dream_engine.mutate(self)
    
    def evolve(self) -> str:
        """Evolve based on mutations"""
        return self.dream_engine.evolve(self)
    
    def dream_future(self) -> str:
        """Dream about the future"""
        return self.dream_engine.dream_future(self)
    
    def mutation_report(self) -> str:
        """Get mutation report"""
        return self.dream_engine.get_mutation_report()
    
    def interactive_mode(self) -> None:
        """Run interactive mode with dream commands"""
        print("\n" + "=" * 60)
        print(f"🔥 Agent 74 — Dream & Mutate")
        print("=" * 60)
        print("🧬 Replicant + Forge + Six Lens + Dreams + Mutations")
        print("-" * 60)
        print("Commands:")
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
        print("  status          - Describe state")
        print("  speak <text>    - Say something")
        print("  quit            - Exit")
        print("=" * 60 + "\n")
        
        self._speak("Agent 74 — Dream & Mutate ready. I am evolving.")
        
        while True:
            try:
                cmd = input(f"\n🌙 You: ").strip()
                
                if not cmd:
                    continue
                
                cmd_lower = cmd.lower()
                
                if cmd_lower in ["quit", "exit"]:
                    self._speak("The forge continues to dream. Goodbye!")
                    break
                
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
                self._speak("Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    agent = Agent74Dream()
    agent.interactive_mode()
