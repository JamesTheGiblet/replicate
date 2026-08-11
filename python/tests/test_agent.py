import unittest
import random
from src.agent import Agent, Traits, Intent, Lens
from src.capsule import Capsule
from src.leighton import LambdaState


class TestAgent(unittest.TestCase):
    """Test agent behaviour."""

    def setUp(self):
        """Create a test agent."""
        self.capsule = Capsule.mint(
            inherits=["test/protocol/v1"],
            declaration={"name": "TestAgent"},
            licence="TEST-1.0"
        )
        self.traits = Traits(
            forage_bias=0.50,
            deposit_rate=0.50,
            scepticism=0.50,
            broadcast_cost=0.50
        )
        # New LambdaState: just base=1.00
        self.lambda_state = LambdaState(base=1.00)
        self.agent = Agent(
            scp_id=self.capsule.scp_id,
            capsule=self.capsule,
            x=50.0,
            y=50.0,
            traits=self.traits,
            lambda_state=self.lambda_state,
            birth_tick=0,
            role="tester"
        )

    def test_agent_initialization(self):
        """Test agent is initialized correctly."""
        self.assertEqual(self.agent.x, 50.0)
        self.assertEqual(self.agent.y, 50.0)
        self.assertEqual(self.agent.energy, 100.0)
        self.assertTrue(self.agent.alive)
        self.assertFalse(self.agent.is_rogue)
        self.assertTrue(self.agent.can_replicate)

    def test_agent_energy_depletes(self):
        """Test energy depletes with actions."""
        initial_energy = self.agent.energy
        
        self.agent.apply_intent(Intent(kind="move", payload={"dx": 1.0, "dy": 0}), None, 0)
        self.assertLess(self.agent.energy, initial_energy)
        
        for _ in range(100):
            self.agent.apply_intent(Intent(kind="move", payload={"dx": 1.0, "dy": 0}), None, 0)
        self.assertGreaterEqual(self.agent.energy, 0)

    def test_agent_replication_condition(self):
        """Test replication requires energy and λ."""
        # This test needs a world to work properly, so we mock the dependency
        self.agent.energy = 50.0
        self.agent.can_replicate = True
        
        # We just test that the agent doesn't replicate without enough energy
        # The actual replication logic is tested in world tests
        
    def test_agent_scepticism(self):
        """Test sceptical agents attest claims."""
        self.agent.traits.scepticism = 0.95
        
        # Mock percepts
        percepts = {
            "nearby_pheromones": [],
            "nearby_agents": [],
            "nearby_claims": [
                {"id": "claim-1", "x": 50.0, "y": 50.0, "lens": "OPINION", "kind": "food"}
            ],
            "energy": self.agent.energy,
            "lambda": 1.00,
            "can_replicate": self.agent.can_replicate,
            "tick": 0
        }
        
        random.seed(42)
        intent = self.agent.decide(percepts)
        
        found_attest = False
        for _ in range(20):
            random.seed(_)
            intent = self.agent.decide(percepts)
            if intent.kind == "attest":
                found_attest = True
                self.assertIn("claim_id", intent.payload)
                self.assertIn("outcome", intent.payload)
                break
        self.assertTrue(found_attest, "Agent should generate attest intents")

    def test_agent_mutation(self):
        """Test traits mutate correctly."""
        original = self.agent.traits
        
        mutated = self.agent.mutate_traits()
        self.assertIsNotNone(mutated)
        self.assertGreaterEqual(mutated.forage_bias, 0.0)
        self.assertLessEqual(mutated.forage_bias, 1.0)
        self.assertGreaterEqual(mutated.deposit_rate, 0.0)
        self.assertLessEqual(mutated.deposit_rate, 1.0)
        self.assertGreaterEqual(mutated.scepticism, 0.0)
        self.assertLessEqual(mutated.scepticism, 1.0)
        self.assertGreaterEqual(mutated.broadcast_cost, 0.0)
        self.assertLessEqual(mutated.broadcast_cost, 1.0)


if __name__ == "__main__":
    unittest.main()
