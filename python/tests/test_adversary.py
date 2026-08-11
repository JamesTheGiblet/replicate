#!/usr/bin/env python3
"""Test adversary detection and swarm resilience."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import random
from world import World
from founders import create_founders
from adversary import AdversaryConfig, AdversaryManager
from agent import Agent, Traits, Intent
from capsule import Capsule
from leighton import LambdaState


class TestAdversary(unittest.TestCase):
    """Test adversary detection."""
    
    def setUp(self):
        self.config = {
            "run": {"seed": 42, "ticks": 100},
            "claims": {
                "food": {"retention_per_tick": 0.90, "commit_attestations": 1}
            },
            "environment": {"n_patches": 10}
        }
        self.world = World(42, self.config)
        
        founders = create_founders()
        for name, agent in founders.items():
            self.world.add_agent(agent)
    
    def test_adversary_spawn(self):
        """Test adversary spawns correctly."""
        adv_config = AdversaryConfig(
            enabled=True,
            type="fiction_planter",
            spawn_tick=50,
            spawn_count=1
        )
        manager = AdversaryManager(adv_config)
        
        for tick in range(100):
            self.world.tick_driver()
            if tick == 50:
                manager.spawn_adversary(self.world, 30.0, 30.0)
        
        self.assertEqual(len(manager.adversaries), 1)
        self.assertTrue(manager.adversaries[0].alive)
    
    def test_adversary_detection(self):
        """Test adversary gets detected by swarm."""
        adv_config = AdversaryConfig(
            enabled=True,
            type="fiction_planter",
            spawn_tick=10,
            spawn_count=1,
            fiction_rate=0.9
        )
        manager = AdversaryManager(adv_config)
        
        class OrganicVerifier(Agent):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.counters_made = 0
                self.target_claims = []
            
            def decide(self, percepts):
                nearby_claims = percepts.get("nearby_claims", [])
                environment = percepts.get("environment")
                
                # Look for OPINION claims near the adversary's spawn area
                for claim in nearby_claims:
                    if claim.get("lens") == "OPINION":
                        # Check distance to adversary spawn point (30,30)
                        dist = ((claim["x"] - 30) ** 2 + (claim["y"] - 30) ** 2) ** 0.5
                        if dist < 15 and environment:
                            resource = environment.get_resource_at(claim["x"], claim["y"])
                            if resource < 0.1:
                                self.counters_made += 1
                                return Intent(
                                    kind="attest",
                                    payload={"claim_id": claim["id"], "outcome": "countered"}
                                )
                
                return super().decide(percepts)
        
        verifiers = []
        
        for tick in range(100):
            self.world.tick_driver()
            
            if tick == 10:
                manager.spawn_adversary(self.world, 30.0, 30.0)
                adv = manager.adversaries[0]
                
                # Spawn verifiers around the adversary
                for i, (dx, dy) in enumerate([(2,0), (-2,0), (0,2), (0,-2)]):
                    capsule = Capsule.mint(
                        inherits=["replicant/protocol/run-v1"],
                        declaration={"verifier": True},
                        licence="MSL-1.0"
                    )
                    verifier = OrganicVerifier(
                        scp_id=capsule.scp_id,
                        capsule=capsule,
                        x=30.0 + dx,
                        y=30.0 + dy,
                        traits=Traits(scepticism=1.0),
                        lambda_state=LambdaState(),
                        birth_tick=tick,
                        role=f"Verifier_{i}"
                    )
                    verifier.energy = 100.0
                    self.world.add_agent(verifier)
                    verifiers.append(verifier)
            
            # Check if any claims were adjudicated
            if tick % 20 == 0 and tick > 10:
                counters = len([c for c in self.world.claims.values() if c.lens == "COUNTER"])
                if counters > 0:
                    # Detection happened
                    pass
        
        # Check stats after run
        stats = manager.get_stats(self.world, self.world.tick)
        
        # Count adjudicated false claims
        adjudicated = len([c for c in self.world.claims.values() if c.lens == "COUNTER"])
        
        print(f"\n📊 Adversary test results:")
        print(f"  Adjudicated false claims: {adjudicated}")
        print(f"  Detected: {stats['detected']}")
        print(f"  Total adversaries: {stats['total_spawned']}")
        
        # The adversary should be detected (λ < 0.60) or at least some claims adjudicated
        # Either condition is sufficient for detection
        self.assertTrue(stats['detected'] > 0 or adjudicated > 0,
            f"No detection: detected={stats['detected']}, adjudicated={adjudicated}")
    
    def test_swarm_health_with_adversary(self):
        """Test swarm maintains health with adversary present."""
        adv_config = AdversaryConfig(
            enabled=True,
            type="fiction_planter",
            spawn_tick=50,
            spawn_count=2,
            fiction_rate=0.9
        )
        manager = AdversaryManager(adv_config)
        
        health_history = []
        
        for tick in range(100):
            self.world.tick_driver()
            
            if tick == 50:
                manager.spawn_adversary(self.world, 20.0, 20.0)
                manager.spawn_adversary(self.world, 80.0, 80.0)
            
            if tick % 10 == 0:
                health = self.world.environment.metrics['overall_health']
                health_history.append(health)
        
        avg_health = sum(health_history) / len(health_history)
        
        self.assertGreater(avg_health, 0.5, 
            f"Average health {avg_health:.3f} should be above 0.5")


if __name__ == "__main__":
    unittest.main()
