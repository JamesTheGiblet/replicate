import unittest
from src.world import World


class TestDeterminism(unittest.TestCase):
    """Test deterministic behavior of the simulation."""

    def test_same_seed_same_results(self):
        """Test same seed produces same results (structural equality)."""
        # Run with deterministic configuration
        config = {
            "run": {"seed": 42, "ticks": 10},
            "leighton": {"k_per_day_forage": 0.05, "k_per_day_signal": 0.02},
            "claims": {
                "food": {"retention_per_tick": 0.90, "commit_attestations": 2}
            }
        }
        
        # Create and run world 1
        world1 = World(42, config)
        # Add agents deterministically (using static ones)
        from src.agent import Agent, Traits
        from src.capsule import Capsule
        from src.leighton import LambdaState
        
        # Create deterministic agents directly
        for i in range(5):
            capsule = Capsule.mint(
                inherits=["test/protocol/v1"],
                declaration={"id": i, "test": True},
                licence="TEST-1.0"
            )
            agent = Agent(
                scp_id=f"test/agent/{i}",
                capsule=capsule,
                x=float(i * 10),
                y=float(i * 10),
                traits=Traits(),
                lambda_state=LambdaState(1.00, 0),
                birth_tick=0,
                role=f"tester_{i}"
            )
            world1.add_agent(agent)
        
        for _ in range(10):
            world1.tick_driver()
        
        # Create and run world 2 with same seed
        world2 = World(42, config)
        for i in range(5):
            capsule = Capsule.mint(
                inherits=["test/protocol/v1"],
                declaration={"id": i, "test": True},
                licence="TEST-1.0"
            )
            agent = Agent(
                scp_id=f"test/agent/{i}",
                capsule=capsule,
                x=float(i * 10),
                y=float(i * 10),
                traits=Traits(),
                lambda_state=LambdaState(1.00, 0),
                birth_tick=0,
                role=f"tester_{i}"
            )
            world2.add_agent(agent)
        
        for _ in range(10):
            world2.tick_driver()
        
        # Check structural equality (not exact hash equality)
        self.assertEqual(len(world1.agents), len(world2.agents))
        self.assertEqual(len(world1.claims), len(world2.claims))
        self.assertEqual(len(world1.ledger), len(world2.ledger))
        self.assertEqual(len(world1.pheromones), len(world2.pheromones))


if __name__ == "__main__":
    unittest.main()
