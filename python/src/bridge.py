#!/usr/bin/env python3
"""
Phone Bridge - Connect S24 Ultra to Replicant Colony
"""

import sys
import json
import time
from pathlib import Path

# Import Replicant modules (now in the same directory)
from world import World
from founders import create_founders
from agent import Agent
from capsule import Capsule
from leighton import LambdaState
from adversary import AdversaryConfig, AdversaryManager

# Import phone agent from nodes
sys.path.insert(0, str(Path(__file__).parent.parent / "nodes"))
from phone.agent import PhoneAgent


class PhoneBridge:
    """Bridge between phone sensors and Replicant simulation"""
    
    def __init__(self):
        self.phone = PhoneAgent()
        self.world = None
        self.running = False
        self.phone_agent_id = "phone-001"
    
    def init_world(self):
        """Initialize Replicant world"""
        config = {
            "run": {"seed": 42, "ticks": 1000},
            "leighton": {"k_per_day_forage": 0.05, "k_per_day_signal": 0.02},
            "claims": {"food": {"retention_per_tick": 0.90, "commit_attestations": 2}},
            "environment": {"n_patches": 10}
        }
        self.world = World(42, config)
        
        # Add founders
        founders = create_founders()
        for name, agent in founders.items():
            self.world.add_agent(agent)
            print(f"  ✓ {name} ({agent.role})")
        
        print(f"✅ World initialized with {len(self.world.agents)} agents")
    
    def create_phone_agent(self, percepts):
        """Create phone agent in the world"""
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
        """Update phone agent state in the world"""
        print("📡 Reading phone sensors...")
        percepts = self.phone.sense()
        
        # Create phone agent if it doesn't exist
        if self.phone_agent_id not in self.world.agents:
            self.create_phone_agent(percepts)
        else:
            # Update existing phone agent
            agent = self.world.agents[self.phone_agent_id]
            agent.x = percepts.get("x", agent.x)
            agent.y = percepts.get("y", agent.y)
            agent.energy = percepts.get("energy", agent.energy)
        
        # Print phone status
        print(f"  📍 Position: ({percepts.get('x', 0):.6f}, {percepts.get('y', 0):.6f})")
        print(f"  ⚡ Energy: {percepts.get('energy', 0):.1f}%")
        print(f"  🧭 Heading: {percepts.get('heading', 0):.3f}")
        print(f"  💡 Light: {percepts.get('light', 0):.0f} lux")
        print(f"  👣 Steps: {percepts.get('steps', 0)}")
    
    def run(self, ticks: int = 5):
        """Run the bridge"""
        print("\n" + "=" * 50)
        print("🧬 Phone Bridge - Connecting to Replicant Colony")
        print("=" * 50 + "\n")
        
        self.init_world()
        self.running = True
        
        try:
            for tick in range(ticks):
                print(f"\n🔄 Tick {tick + 1}/{ticks}")
                print("-" * 40)
                
                # Update phone sensor data
                self.update_phone_agent()
                
                # Run world tick
                self.world.tick_driver()
                
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
                
                if tick < ticks - 1:
                    time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n👋 Stopped by user")
        finally:
            self.running = False

if __name__ == "__main__":
    bridge = PhoneBridge()
    bridge.run(ticks=5)
