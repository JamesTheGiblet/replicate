"""
Phone Bridge with SQLite + Replicant Ledger
Full data persistence and audit trail
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Import Replicant modules
from world import World
from founders import create_founders
from agent import Agent
from capsule import Capsule
from leighton import LambdaState

# Import phone and database
sys.path.insert(0, str(Path(__file__).parent.parent / "nodes"))
from phone.agent import PhoneAgent
from phone_db import PhoneDatabase


class PhoneBridgeWithLedger:
    """Phone bridge with SQLite storage and Replicant ledger"""
    
    def __init__(self, db_path="phone_data.db"):
        self.phone = PhoneAgent()
        self.world = None
        self.db = PhoneDatabase(db_path)
        self.phone_agent_id = "phone-001"
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.tick_count = 0
        self.entry_count = 0
        
        print(f"📊 Session: {self.session_id}")
        self.db.start_session(self.session_id, self.phone_agent_id)
    
    def init_world(self):
        """Initialize Replicant world"""
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
        
        # Log to ledger
        self.db.insert_world_event(self.session_id, self.tick_count, {
            "type": "phone.agent.created",
            "agent_id": self.phone_agent_id,
            "x": percepts.get("x", 0),
            "y": percepts.get("y", 0),
        })
    
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
        
        # Print status
        print(f"  📍 Position: ({percepts.get('x', 0):.6f}, {percepts.get('y', 0):.6f})")
        print(f"  ⚡ Energy: {percepts.get('energy', 0):.1f}%")
        print(f"  🧭 Heading: {percepts.get('heading', 0):.3f}")
        print(f"  💡 Light: {percepts.get('light', 0):.0f} lux")
        print(f"  👣 Steps: {percepts.get('steps', 0)}")
        print(f"  💾 Saved to SQLite: {self.entry_count} entries")
        
        return percepts
    
    def log_world_events(self):
        """Log world events to database"""
        # Log claims
        for claim_id, claim in self.world.claims.items():
            self.db.insert_world_event(self.session_id, self.tick_count, {
                "type": "claim",
                "claim_id": claim_id,
                "agent_id": claim.agent_id,
                "lens": claim.lens,
                "x": claim.x,
                "y": claim.y,
            })
        
        # Log COUNTER events
        for claim in self.world.claims.values():
            if claim.lens == "COUNTER":
                self.db.insert_world_event(self.session_id, self.tick_count, {
                    "type": "adjudicated_false",
                    "claim_id": claim.id,
                    "agent_id": claim.agent_id,
                })
    
    def run(self, ticks: int = 10):
        """Run the bridge with full persistence"""
        print("\n" + "=" * 50)
        print("🧬 Phone Bridge with SQLite + Ledger")
        print(f"📁 Database: {self.db.db_path}")
        print("=" * 50 + "\n")
        
        self.init_world()
        
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
                
                if tick < ticks - 1:
                    time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n👋 Stopped by user")
        finally:

            # Export BEFORE closing
            export_file = f"session_{self.session_id}.json"
            self.db.export_to_json(self.session_id, export_file)

            # End session and close database
            self.db.end_session(self.session_id, self.tick_count, self.entry_count)
            self.db.close()

            print(f"\n📊 Session Summary:")
            print(f"  📋 Readings: {self.entry_count}")
            print(f"  🏷️  Session: {self.session_id}")
            print(f"  📁 Database: {self.db.db_path}")
            print(f"  📄 Exported: {export_file}")


if __name__ == "__main__":
    ticks = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    bridge = PhoneBridgeWithLedger()
    bridge.run(ticks=ticks)
