#!/usr/bin/env python3
"""
Test whether Replicant can stabilize a dynamic environment.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import random
from world import World
from founders import create_founders
from environment import Environment


class TestStabilization(unittest.TestCase):
    """Test Replicant's ability to stabilize the system."""
    
    def setUp(self):
        self.config = {
            "run": {"seed": 42, "ticks": 200},
            "leighton": {"k_per_day_forage": 0.05, "k_per_day_signal": 0.02},
            "claims": {
                "food": {"retention_per_tick": 0.90, "commit_attestations": 2}
            },
            "environment": {"n_patches": 10}
        }
        self.world = World(42, self.config)
        
        # Add founders
        founders = create_founders()
        for name, agent in founders.items():
            self.world.add_agent(agent)

    def test_system_stabilizes(self):
        """Test the system reaches and maintains stability."""
        print("\n🌍 Testing Replicant Stabilization...")
        print("=" * 50)
        
        stability_history = []
        
        for tick in range(200):
            self.world.tick_driver()
            
            if tick % 10 == 0:
                report = self.world.get_health_report()
                health = report["overall_health"]
                stability_history.append(health)
        
        # Check if system stabilized
        final_health = stability_history[-1] if stability_history else 0
        
        if len(stability_history) >= 20:
            early_avg = sum(stability_history[:10]) / 10
            late_avg = sum(stability_history[-10:]) / 10
            improvement = late_avg - early_avg
            
            print(f"\n📊 Stabilization Analysis:")
            print(f"  Early health (avg): {early_avg:.3f}")
            print(f"  Late health (avg):  {late_avg:.3f}")
            print(f"  Improvement:        {improvement:+.3f}")
        
        print(f"\n✅ System stabilized with health {final_health:.3f}")
        
        # Assert health is maintained (not necessarily improving)
        self.assertGreaterEqual(final_health, 0.4,
            f"Final health {final_health:.3f} should be at least 0.4")
        
        # Check stability (low variance in later ticks)
        if len(stability_history) >= 20:
            late_health = stability_history[-10:]
            variance = sum((h - sum(late_health)/len(late_health))**2 for h in late_health) / len(late_health)
            self.assertLess(variance, 0.01,
                f"Health variance {variance:.4f} should be low (system is stable)")

    def test_threat_response(self):
        """Test swarm responds to threats (survival, not elimination)."""
        print("\n⚔️ Testing Threat Response...")
        print("=" * 50)
        
        # Track health during threats
        health_during_threats = []
        health_without_threats = []
        
        for tick in range(200):
            self.world.tick_driver()
            if tick % 10 == 0:
                report = self.world.get_health_report()
                health = report["overall_health"]
                threats = report["threat_count"]
                
                if threats > 0:
                    health_during_threats.append(health)
                else:
                    health_without_threats.append(health)
        
        print(f"\n  Health during threats: {sum(health_during_threats)/len(health_during_threats) if health_during_threats else 0:.3f}")
        print(f"  Health without threats: {sum(health_without_threats)/len(health_without_threats) if health_without_threats else 0:.3f}")
        
        # Assert the swarm maintains health during threats
        if health_during_threats and health_without_threats:
            avg_threat_health = sum(health_during_threats) / len(health_during_threats)
            avg_no_threat_health = sum(health_without_threats) / len(health_without_threats)
            
            # Health during threats should be at least 70% of health without threats
            self.assertGreaterEqual(avg_threat_health, avg_no_threat_health * 0.7,
                f"Health during threats ({avg_threat_health:.3f}) should be at least 70% of health without threats ({avg_no_threat_health:.3f})")

    def test_resource_utilization(self):
        """Test swarm efficiently uses resources (not over-exploiting)."""
        print("\n🌿 Testing Resource Utilization...")
        print("=" * 50)
        
        resource_history = []
        depletion_count = 0
        
        for tick in range(200):
            self.world.tick_driver()
            if tick % 10 == 0:
                report = self.world.get_health_report()
                resource_history.append(report["metrics"]["resource_utilization"])
                depletion_count = report["depleted_patches"]
        
        avg_util = sum(resource_history) / len(resource_history) if resource_history else 0
        
        print(f"\n  Average resource utilization: {avg_util:.3f}")
        print(f"  (0 = unused, 1 = fully utilized)")
        print(f"  Depleted patches: {depletion_count}")
        
        # Assert the swarm is using resources sustainably
        # Not over-exploiting (utilization should be low)
        # Not completely ignoring resources (utilization > 0)
        self.assertGreater(avg_util, 0.01,
            f"Resource utilization {avg_util:.3f} should be above 0.01 (resources are being used)")
        
        # Check that not all patches are depleted
        self.assertLess(depletion_count, 8,
            f"Depleted patches {depletion_count} should be less than 8 (resources not over-exploited)")


def run_stabilization_demo():
    """Run a full stabilization demo with output."""
    config = {
        "run": {"seed": 42, "ticks": 300},
        "leighton": {"k_per_day_forage": 0.05, "k_per_day_signal": 0.02},
        "claims": {
            "food": {"retention_per_tick": 0.90, "commit_attestations": 2}
        },
        "environment": {"n_patches": 12}
    }
    
    print("\n🧬 REPLICANT STABILIZATION DEMO")
    print("=" * 60)
    print("Testing whether Replicant can stabilize a dynamic ecosystem.")
    print("Features: seasonal cycles, threats, resource depletion/regeneration")
    print("=" * 60 + "\n")
    
    world = World(42, config)
    
    # Add founders
    founders = create_founders()
    for name, agent in founders.items():
        world.add_agent(agent)
    
    # Track metrics
    health_history = []
    pop_history = []
    threat_history = []
    energy_history = []
    
    for tick in range(300):
        world.tick_driver()
        
        if tick % 20 == 0:
            report = world.get_health_report()
            health = report["overall_health"]
            pop = len([a for a in world.agents.values() if a.alive])
            threats = report["threat_count"]
            energy = report["total_energy"]
            
            health_history.append(health)
            pop_history.append(pop)
            threat_history.append(threats)
            energy_history.append(energy)
            
            print(f"T{str(tick).rjust(4)} | Health: {health:.3f} | "
                  f"Pop: {str(pop).rjust(2)} | "
                  f"Threats: {threats} | "
                  f"Energy: {energy:.1f} | "
                  f"Season: {report['season']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 STABILIZATION SUMMARY")
    print("=" * 60)
    
    if health_history:
        final_health = health_history[-1]
        avg_health = sum(health_history) / len(health_history)
        max_health = max(health_history)
        
        print(f"  Average Health:     {avg_health:.3f}")
        print(f"  Max Health:         {max_health:.3f}")
        print(f"  Final Health:       {final_health:.3f}")
        
        if len(health_history) >= 5:
            early_avg = sum(health_history[:5]) / 5
            late_avg = sum(health_history[-5:]) / 5
            print(f"  Improvement:        {late_avg - early_avg:+.3f}")
    
    if pop_history:
        print(f"  Final Population:   {pop_history[-1]}")
        print(f"  Max Population:     {max(pop_history)}")
    
    if threat_history:
        total_threats = sum(threat_history)
        avg_threats = total_threats / len(threat_history)
        print(f"  Average Threats:    {avg_threats:.2f}")
    
    print("\n" + "=" * 60)
    
    if health_history and health_history[-1] > 0.6:
        print("✅ SYSTEM STABILIZED!")
        print("   Replicant successfully maintained homeostasis.")
    else:
        print("⚠️  SYSTEM PARTIALLY STABILIZED")
        print("   Replicant showed adaptive behaviour but needs tuning.")
    
    return health_history[-1] if health_history else 0


if __name__ == "__main__":
    # Run demo
    score = run_stabilization_demo()
    
    # Run tests
    print("\n🧪 Running formal tests...")
    unittest.main(argv=[''], verbosity=2, exit=False)
