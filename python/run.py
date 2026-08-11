#!/usr/bin/env python3
"""Replicant Beta - Python prototype on Termux."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from founders import create_founders
from world import World


def load_config():
    return {
        "run": {"seed": 42, "ticks": 200},
        "leighton": {"k_per_day_forage": 0.05, "k_per_day_signal": 0.02},
        "claims": {"food": {"retention_per_tick": 0.90, "commit_attestations": 2}}
    }


def main():
    print("🧬 Replicant Beta (Python on Termux)")
    print("Born pregnant. Born ready. Born signed.\n")

    config = load_config()
    world = World(config["run"]["seed"], config)

    print("🌟 Founding 10 agents...")
    founders = create_founders()
    for name, agent in founders.items():
        world.add_agent(agent)
        print(f"  ✓ {name} ({agent.role}) - {agent.scp_id}")

    print(f"\n🔄 Running {config['run']['ticks']} ticks...\n")

    for tick in range(config["run"]["ticks"]):
        world.tick_driver()
        if tick % 10 == 0:
            alive = sum(1 for a in world.agents.values() if a.alive)
            counters = sum(1 for c in world.claims.values() if c.lens == "COUNTER")
            print(f"Tick {tick:4d} | Alive: {alive:3d} | Claims: {len(world.claims):4d} | COUNTER: {counters:3d}")

        if sum(1 for a in world.agents.values() if a.alive) == 0:
            print(f"\n💀 All agents dead at tick {tick}")
            break

    print("\n" + "="*50)
    print("📊 Final Report")
    print("="*50)

    alive = sum(1 for a in world.agents.values() if a.alive)
    print(f"Agents alive: {alive}/{len(world.agents)}")
    print(f"Total claims: {len(world.claims)}")
    print(f"Ledger entries: {len(world.ledger)}")

    # Check λ state for each agent
    print("\n🔬 λ Status:")
    for aid, agent in world.agents.items():
        if agent.alive:
            lam = world.leighton.compute(aid, world.tick)
            event_count = len(world.leighton.get_state(aid).events)
            status = "Trusted"
            if lam < 0.15:
                status = "EXPEL"
            elif lam < 0.60:
                status = "QUARANTINE"
            print(f"  {agent.role:12} | λ: {lam:.3f} | Events: {event_count:2d} | {status}")

    counters = [c for c in world.claims.values() if c.lens == "COUNTER"]
    print(f"\n📋 COUNTER claims: {len(counters)}")
    if len(counters) == 0:
        print("  ⚠️  WARNING: No disconfirmation ever sought!")

    print("\n✅ Done.")


if __name__ == "__main__":
    main()
