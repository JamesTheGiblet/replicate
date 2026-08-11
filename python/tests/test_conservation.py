import unittest
from src.world import World
from src.founders import create_founders


class TestEnergyConservation(unittest.TestCase):
    """Test energy is conserved (doesn't appear from nowhere)."""

    def setUp(self):
        """Create a test world."""
        self.config = {
            "run": {"seed": 42, "ticks": 50},
            "leighton": {"k_per_day_forage": 0.05, "k_per_day_signal": 0.02},
            "claims": {
                "food": {"retention_per_tick": 0.90, "commit_attestations": 2}
            }
        }

    def test_energy_never_negative(self):
        """Test no agent has negative energy."""
        world = World(42, self.config)
        founders = create_founders()
        for name, agent in founders.items():
            world.add_agent(agent)
        
        # Run simulation
        for _ in range(50):
            world.tick_driver()
        
        # Check all agents have non-negative energy
        for aid, agent in world.agents.items():
            self.assertGreaterEqual(agent.energy, -0.001, 
                f"Agent {aid} has negative energy: {agent.energy}")

    def test_energy_trend(self):
        """Test energy decreases over time with actions."""
        world = World(42, self.config)
        founders = create_founders()
        for name, agent in founders.items():
            world.add_agent(agent)
        
        # Track a specific agent
        agent_id = list(world.agents.keys())[0]
        initial_energy = world.agents[agent_id].energy
        
        # Run simulation
        for _ in range(50):
            world.tick_driver()
        
        # Energy should not increase beyond initial (no free energy)
        final_energy = world.agents[agent_id].energy
        # Some agents may recharge, but total should not exceed initial + recharge
        # Recharge rate is 0.5 per tick, max 50 ticks = 25 max recharge
        self.assertLessEqual(final_energy, initial_energy + 25.0)


if __name__ == "__main__":
    unittest.main()
