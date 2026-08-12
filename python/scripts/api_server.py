#!/usr/bin/env python3
"""Replicant API Server - serves swarm data to browser."""

import sys
import os

# Adjust path to find the 'src' directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from src.world import World
from src.founders import create_founders
from src.config import get_default_config

# Define the path for the static frontend files (wasm/www)
static_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'wasm', 'www'))

app = Flask(__name__, static_folder=static_folder_path)
CORS(app)

config = get_default_config()
config['run']['seed'] = 42 # Ensure consistent seed for the web UI

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
    alive = sum(1 for a in world.agents.values() if a.alive)
    claims = len(world.claims)
    counters = sum(1 for c in world.claims.values() if c.lens == "COUNTER")
    health = world.environment.metrics["overall_health"]
    
    # Get season from environment
    season = "Unknown"
    
    return jsonify({
        "tick": world.tick,
        "agents": alive,
        "total_agents": len(world.agents),
        "claims": claims,
        "counters": counters,
        "health": round(health, 3),
        "season": season,
        "threats": len(world.environment.threats),
    })

@app.route('/api/step')
def step():
    world.tick_driver()
    return status()

@app.route('/api/run/<int:ticks>')
def run(ticks):
    for _ in range(min(ticks, 100)):
        world.tick_driver()
    return status()

@app.route('/api/agents')
def agents():
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

@app.route('/api/environment')
def environment():
    """Returns the state of the environment (patches, threats)."""
    patches = []
    for patch in world.environment.patches:
        patches.append({
            "x": patch.x,
            "y": patch.y,
            "energy": patch.energy,
            "max_energy": patch.max_energy,
            "depleted": patch.depleted,
        })
    
    threats = []
    for threat in world.environment.threats:
        threats.append({
            "x": threat.x,
            "y": threat.y,
            "radius": threat.radius,
            "intensity": threat.intensity,
        })
    return jsonify({"patches": patches, "threats": threats, "width": world.environment.width, "height": world.environment.height})

@app.route('/')
def serve_index():
    """Serves the main index.html file."""
    return send_from_directory(app.static_folder or static_folder_path, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serves other static files like CSS, JS, or images."""
    return send_from_directory(app.static_folder or static_folder_path, path)

@app.route('/api/reset')
def reset():
    global world
    world = World(42, config)
    founders = create_founders()
    for name, agent in founders.items():
        world.add_agent(agent)
    return status()

if __name__ == '__main__':
    print("\n🧬 Replicant API Server")
    print("=" * 40)
    print("🌐 Server running on http://localhost:5000")
    print("📊 Endpoints:")
    print("  GET /          - Serves the web-based visualizer")
    print("  GET /api/status  - Current swarm status")
    print("  GET /api/step    - Advance one tick")
    print("  GET /api/run/10  - Advance 10 ticks")
    print("  GET /api/environment - Get environment state (patches, threats)")
    print("  GET /api/agents  - List all agents")
    print("=" * 40)
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
