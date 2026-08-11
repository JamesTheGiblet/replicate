#!/usr/bin/env python3
"""Statistical analysis of Replicant runs."""

import json
from src.world import World
from src.founders import create_founders

results = []

for seed in range(5):
    config = {
        'run': {'seed': seed, 'ticks': 500},
        'leighton': {'k_per_day_forage': 0.05, 'k_per_day_signal': 0.02},
        'claims': {'food': {'retention_per_tick': 0.90, 'commit_attestations': 2}},
        'environment': {'n_patches': 12}
    }

    world = World(seed, config)
    for name, agent in create_founders().items():
        world.add_agent(agent)

    for tick in range(500):
        world.tick_driver()

    alive = len([a for a in world.agents.values() if a.alive])
    counters = len([c for c in world.claims.values() if c.lens == 'COUNTER'])
    health = world.environment.metrics['overall_health']
    season = world.environment.get_health_report()['season']

    results.append({
        'seed': seed,
        'alive': alive,
        'counters': counters,
        'health': health,
        'season': season
    })

print('📊 REPLICANT STATISTICAL ANALYSIS')
print('=' * 50)
print(f'Seeds tested: 5')
print('-' * 50)
for r in results:
    print(f"Seed {r['seed']:2d} | Alive: {r['alive']:2d} | COUNTER: {r['counters']:2d} | Health: {r['health']:.3f} | {r['season']}")
print('-' * 50)

avg_alive = sum(r['alive'] for r in results) / len(results)
avg_counters = sum(r['counters'] for r in results) / len(results)
avg_health = sum(r['health'] for r in results) / len(results)

print(f"Average alive:   {avg_alive:.1f}")
print(f"Average COUNTER: {avg_counters:.1f}")
print(f"Average health:  {avg_health:.3f}")
print('=' * 50)
