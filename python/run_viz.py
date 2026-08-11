#!/usr/bin/env python3
"""Run Replicant with enhanced terminal visualization."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from world import World
from founders import create_founders
from viz_terminal_enhanced import EnhancedTerminalViz
import time

def main():
    print("🧬 Replicant with Enhanced Visualization")
    print("Press Ctrl+C to exit\n")
    
    config = {
        'run': {'seed': 42, 'ticks': 200},
        'leighton': {'k_per_day_forage': 0.05, 'k_per_day_signal': 0.02},
        'claims': {'food': {'retention_per_tick': 0.90, 'commit_attestations': 2}},
        'environment': {'n_patches': 10}
    }
    
    world = World(42, config)
    founders = create_founders()
    for name, agent in founders.items():
        world.add_agent(agent)
    
    viz = EnhancedTerminalViz()
    
    try:
        for tick in range(200):
            world.tick_driver()
            viz.render(world, tick)
            time.sleep(0.15)
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
    
    # Final summary
    alive = len([a for a in world.agents.values() if a.alive])
    counters = len([c for c in world.claims.values() if c.lens == "COUNTER"])
    health = world.environment.metrics["overall_health"]
    
    print("\n" + "="*50)
    print("📊 FINAL SUMMARY")
    print("="*50)
    print(f"  Agents alive:     {alive}")
    print(f"  COUNTER claims:   {counters}")
    print(f"  Overall health:   {health:.3f}")
    print("="*50)

if __name__ == "__main__":
    main()
