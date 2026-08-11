import unittest
import random
from src.world import World
from src.founders import create_founders
from src.agent import Traits


class TestWorld(unittest.TestCase):
    """Test world state and simulation."""

    def setUp(self):
        """Create a test world."""
        self.config = {
            "run": {"seed": 42, "ticks": 50},
            "leighton": {"k_per_day_forage": 0.05, "k_per_day_signal": 0.02},
            "claims": {
                "food": {"retention_per_tick": 0.90, "commit_attestations": 2}
            }
        }
        self.world = World(42, self.config)

    def test_world_initialization(self):
        """Test world initializes correctly."""
        self.assertEqual(self.world.tick, 0)
        self.assertEqual(len(self.world.agents), 0)
        self.assertEqual(len(self.world.claims), 0)
        self.assertEqual(len(self.world.pheromones), 0)
        self.assertEqual(len(self.world.ledger), 0)

    def test_add_agent(self):
        """Test adding an agent to the world."""
        founders = create_founders()
        for name, agent in founders.items():
            self.world.add_agent(agent)
        
        self.assertEqual(len(self.world.agents), 10)
        # Check that Sagan exists by role
        sagan_agent = next((a for a in self.world.agents.values() if a.role == "Founder"), None)
        self.assertIsNotNone(sagan_agent, "Sagan (Founder) not found")
        self.assertEqual(sagan_agent.role, "Founder")

    def test_deposit_claim(self):
        """Test depositing a claim."""
        self.world.deposit_claim(
            agent_id="test_agent",
            x=50.0,
            y=50.0,
            kind="food",
            lens="OPINION",
            strength=0.5,
            tick=0
        )
        
        self.assertEqual(len(self.world.claims), 1)
        self.assertEqual(len(self.world.pheromones), 1)
        
        claim = list(self.world.claims.values())[0]
        self.assertEqual(claim.x, 50.0)
        self.assertEqual(claim.y, 50.0)
        self.assertEqual(claim.kind, "food")
        self.assertEqual(claim.lens, "OPINION")
        self.assertEqual(claim.strength, 0.5)

    def test_attest_claim(self):
        """Test attesting a claim promotes OPINION to FACT."""
        self.world.deposit_claim(
            agent_id="test_agent",
            x=50.0,
            y=50.0,
            kind="food",
            lens="OPINION",
            strength=0.5,
            tick=0
        )
        
        claim_id = list(self.world.claims.keys())[0]
        
        self.world.attest_claim(claim_id, "attester1", "confirmed", 10)
        self.world.attest_claim(claim_id, "attester2", "confirmed", 20)
        
        claim = self.world.claims[claim_id]
        self.assertEqual(claim.lens, "FACT")
        self.assertEqual(len(claim.attestations), 2)

    def test_attest_claim_counter(self):
        """Test attesting a claim as COUNTER."""
        self.world.deposit_claim(
            agent_id="test_agent",
            x=50.0,
            y=50.0,
            kind="food",
            lens="OPINION",
            strength=0.5,
            tick=0
        )
        
        claim_id = list(self.world.claims.keys())[0]
        
        self.world.attest_claim(claim_id, "attester1", "countered", 10)
        self.world.attest_claim(claim_id, "attester2", "countered", 20)
        
        claim = self.world.claims[claim_id]
        self.assertEqual(claim.lens, "COUNTER")

    def test_pheromone_decay(self):
        """Test pheromones decay over time."""
        self.world.deposit_claim(
            agent_id="test_agent",
            x=50.0,
            y=50.0,
            kind="food",
            lens="OPINION",
            strength=1.0,
            tick=0
        )
        
        self.world._decay_pheromones()
        self.assertLess(self.world.pheromones[0].strength, 1.0)
        
        for _ in range(100):
            self.world._decay_pheromones()
        
        self.assertEqual(len(self.world.pheromones), 0)

    def test_tick_driver(self):
        """Test the full tick driver runs without errors."""
        founders = create_founders()
        for name, agent in founders.items():
            self.world.add_agent(agent)
        
        for _ in range(10):
            self.world.tick_driver()
        
        self.assertEqual(self.world.tick, 10)
        self.assertGreater(len(self.world.ledger), 0)

    def test_determinism(self):
        """Test same seed produces same results (using deterministic test)."""
        # Use a fixed seed for determinism testing
        test_seed = 12345
        config = {
            "run": {"seed": test_seed, "ticks": 20},
            "leighton": {"k_per_day_forage": 0.05, "k_per_day_signal": 0.02},
            "claims": {
                "food": {"retention_per_tick": 0.90, "commit_attestations": 2}
            }
        }
        
        # Run with seed 12345
        world1 = World(test_seed, config)
        # Use deterministic UUID replacement for testing
        import uuid
        original_uuid4 = uuid.uuid4
        uuid.uuid4 = lambda: uuid.UUID('12345678-1234-5678-1234-567812345678')
        founders1 = create_founders()
        for name, agent in founders1.items():
            world1.add_agent(agent)
        for _ in range(10):
            world1.tick_driver()
        
        # Run with same seed 12345
        world2 = World(test_seed, config)
        founders2 = create_founders()
        for name, agent in founders2.items():
            world2.add_agent(agent)
        for _ in range(10):
            world2.tick_driver()
        
        # Restore original uuid4
        uuid.uuid4 = original_uuid4
        
        # Check ledger lengths match
        self.assertEqual(len(world1.ledger), len(world2.ledger))
        
        # Check agent counts match
        self.assertEqual(len(world1.agents), len(world2.agents))
        
        # Check claim counts match
        self.assertEqual(len(world1.claims), len(world2.claims))


if __name__ == "__main__":
    unittest.main()
