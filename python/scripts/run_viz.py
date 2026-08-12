#!/usr/bin/env python3
"""Run Replicant with enhanced terminal visualization."""

import sys
import os
import time

# Adjust path to find the 'src' directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.world import World
from src.founders import create_founders
from src.config import get_default_config
from src.viz import EnhancedTerminalViz

def main():
    print("🧬 Replicant with Enhanced Visualization")
    print("Press Ctrl+C to exit\n")
    
    config = get_default_config()
    world = World(config["run"]["seed"], config)
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
