"""
Phone Node Bridge - Connect S24 Ultra to Replicant Colony
"""

import sys
import json
import time
import threading
from pathlib import Path

# Add Replicant to path
REPLICANT_PATH = Path(__file__).parent.parent.parent / "python"
sys.path.insert(0, str(REPLICANT_PATH))
sys.path.insert(0, str(REPLICANT_PATH / "src"))

from agent import PhoneAgent
from world import World
from founders import create_founders

class PhoneBridge:
    """Bridge between phone sensors and Replicant simulation"""
    
    def __init__(self):
        self.phone = PhoneAgent()
        self.world = None
        self.running = False
    
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
        
        print(f"✅ World initialized with {len(self.world.agents)} agents")
    
    def update_phone_agent(self):
        """Update phone agent state in the world"""
        percepts = self.phone.sense()
        
        # Find or create phone agent in world
        phone_agent_id = "phone-001"
        if phone_agent_id not in self.world.agents:
            # Create phone agent in world
            from capsule import Capsule
            from leighton import LambdaState
            from agent import Agent, Traits
            
            capsule = Capsule.mint(
                inherits=["replicant/protocol/run-v1"],
                declaration={"type": "phone", "name": "Phone Agent"},
                licence="MSL-1.0"
            )
            
            phone_agent = Agent(
                scp_id=phone_agent_id,
                capsule=capsule,
                x=percepts.get("x", 0),
                y=percepts.get("y", 0),
                traits=Traits(),
                lambda_state=LambdaState(),
                birth_tick=self.world.tick,
                role="Phone"
            )
            phone_agent.energy = percepts.get("energy", 100)
            self.world.add_agent(phone_agent)
            print("📱 Phone agent added to world")
        else:
            # Update existing phone agent
            agent = self.world.agents[phone_agent_id]
            agent.x = percepts.get("x", agent.x)
            agent.y = percepts.get("y", agent.y)
            agent.energy = percepts.get("energy", agent.energy)
    
    def run(self, ticks: int = 10):
        """Run the bridge"""
        print("🧬 Phone Bridge - Connecting to Replicant Colony")
        print("=" * 50)
        
        self.init_world()
        self.running = True
        
        try:
            for tick in range(ticks):
                print(f"\n🔄 Tick {tick + 1}/{ticks}")
                
                # Update phone sensor data
                self.update_phone_agent()
                
                # Run world tick
                self.world.tick_driver()
                
                # Show status
                alive = len([a for a in self.world.agents.values() if a.alive])
                claims = len(self.world.claims)
                counters = len([c for c in self.world.claims.values() if c.lens == "COUNTER"])
                health = self.world.environment.metrics["overall_health"]
                
                print(f"  👥 Agents: {alive}")
                print(f"  📋 Claims: {claims}")
                print(f"  🔍 COUNTER: {counters}")
                print(f"  🌿 Health: {health:.3f}")
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n👋 Stopped")
        finally:
            self.running = False

if __name__ == "__main__":
    bridge = PhoneBridge()
    bridge.run(ticks=10)
