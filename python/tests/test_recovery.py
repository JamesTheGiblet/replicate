#!/usr/bin/env python3
"""Test quarantine recovery semantics."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from world import World
from founders import create_founders
from adversary import AdversaryConfig, AdversaryManager
from agent import Agent, Traits, Intent
from capsule import Capsule
from leighton import LambdaState


class TestRecovery(unittest.TestCase):
    """Test that quarantined agents can recover."""
    
    def setUp(self):
        self.config = {
            "run": {"seed": 42, "ticks": 200},
            "claims": {
                "food": {"retention_per_tick": 0.90, "commit_attestations": 1}
            },
            "environment": {"n_patches": 10}
        }
        self.world = World(42, self.config)
        
        founders = create_founders()
        for name, agent in founders.items():
            self.world.add_agent(agent)
    
    def test_quarantine_recovery(self):
        """Test an agent recovers from quarantine after stopping bad behaviour."""
        
        # Create a target agent that will be penalized
        capsule = Capsule.mint(
            inherits=["replicant/protocol/run-v1"],
            declaration={"test": "recovery"},
            licence="MSL-1.0"
        )
        
        agent = Agent(
            scp_id=capsule.scp_id,
            capsule=capsule,
            x=50.0,
            y=50.0,
            traits=Traits(scepticism=0.3),
            lambda_state=LambdaState(),
            birth_tick=0,
            role="RecoveryTest"
        )
        agent.energy = 100.0
        self.world.add_agent(agent)
        
        # Simulate 2 offences (λ should drop to ~0.76)
        # Apply false claim penalties directly
        self.world.leighton.claim_adjudicated_false(agent.scp_id, 10)
        self.world.leighton.claim_adjudicated_false(agent.scp_id, 20)
        
        # Check λ after offences
        lam_after_offences = self.world.leighton.compute(agent.scp_id, 20)
        print(f"λ after 2 offences: {lam_after_offences:.3f}")
        
        # Should be quarantined (0.15 < λ < 0.60)
        self.assertLess(lam_after_offences, 0.60, 
            f"Agent should be quarantined, λ={lam_after_offences:.3f}")
        self.assertGreater(lam_after_offences, 0.15,
            f"Agent should not be expelled, λ={lam_after_offences:.3f}")
        
        # Run ticks with no further offences
        for tick in range(21, 100):
            self.world.tick_driver()
        
        # Check λ after recovery period
        lam_after_recovery = self.world.leighton.compute(agent.scp_id, 99)
        print(f"λ after recovery: {lam_after_recovery:.3f}")
        
        # Should have recovered (λ > 0.60)
        self.assertGreater(lam_after_recovery, 0.60,
            f"Agent should recover from quarantine, λ={lam_after_recovery:.3f}")
        
        print(f"\n✅ Recovery successful: {lam_after_offences:.3f} → {lam_after_recovery:.3f}")


if __name__ == "__main__":
    unittest.main()
