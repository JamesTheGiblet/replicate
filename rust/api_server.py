#!/usr/bin/env python3
"""Replicant API Server - serves swarm data to browser."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask, jsonify
from flask_cors import CORS

# Import Replicant modules
from world import World
from founders import create_founders

app = Flask(__name__)
CORS(app)

# Initialize Replicant
config = {
    "run": {"seed": 42, "ticks": 1000},
    "leighton": {"k_per_day_forage": 0.05, "k_per_day_signal": 0.02},
    "claims": {"food": {"retention_per_tick": 0.90, "commit_attestations": 2}},
    "environment": {"n_patches": 10}
}

print("🧬 Initializing Replicant World...")
world = World(42, config)

print("🌟 Creating founders...")
founders = create_founders()
for name, agent in founders.items():
    world.add_agent(agent)
    print(f"  ✓ {name} ({agent.role})")

print(f"✅ Ready! {len(world.agents)} agents created.")

@app.route('/api/status')
def status():
    """Get current swarm status."""
    alive = sum(1 for a in world.agents.values() if a.alive)
    claims = len(world.claims)
    counters = sum(1 for c in world.claims.values() if c.lens == "COUNTER")
    health = world.environment.metrics["overall_health"]
    
    return jsonify({
        "tick": world.tick,
        "agents": alive,
        "total_agents": len(world.agents),
        "claims": claims,
        "counters": counters,
        "health": round(health, 3),
        "season": "Rich" if world.environment.season_factor() > 1.0 else "Poor",
        "threats": len(world.environment.threats),
    })

@app.route('/api/step')
def step():
    """Advance the simulation by one tick."""
    world.tick_driver()
    return status()

@app.route('/api/run/<int:ticks>')
def run(ticks):
    """Run multiple ticks."""
    for _ in range(min(ticks, 100)):
        world.tick_driver()
    return status()

@app.route('/api/health')
def health():
    """Get detailed health report."""
    report = world.get_health_report()
    return jsonify(report)

@app.route('/api/agents')
def agents():
    """Get agent list."""
    agent_list = []
    for aid, agent in world.agents.items():
        if agent.alive:
            lam = world.leighton.compute(aid, world.tick)
            agent_list.append({
                "id": aid[:8],
                "role": agent.role,
                "x": round(agent.x, 1),
                "y": round(agent.y, 1),
                "energy": round(agent.energy, 1),
                "lambda": round(lam, 3),
                "rogue": agent.is_rogue,
            })
    return jsonify(agent_list)

@app.route('/api/reset')
def reset():
    """Reset the simulation."""
    global world
    world = World(42, config)
    founders = create_founders()
    for name, agent in founders.items():
        world.add_agent(agent)
    return status()

if __name__ == '__main__':
    print("\n🧬 Replicant API Server")
    print("=" * 40)
    print(f"🌐 Server running on http://localhost:5000")
    print(f"📊 Endpoints:")
    print(f"  GET /api/status  - Current swarm status")
    print(f"  GET /api/step    - Advance one tick")
    print(f"  GET /api/run/10  - Advance 10 ticks")
    print(f"  GET /api/agents  - List all agents")
    print(f"  GET /api/health  - Detailed health report")
    print("=" * 40)
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
