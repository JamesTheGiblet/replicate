#!/usr/bin/env python3
"""Season analysis for Replicant."""

from src.world import World
from src.founders import create_founders

seasons = []

for seed in range(10):
    config = {
        'run': {'seed': seed, 'ticks': 500},
        'leighton': {'k_per_day_forage': 0.05, 'k_per_day_signal': 0.02},
        'claims': {'food': {'retention_per_tick': 0.90, 'commit_attestations': 2}},
        'environment': {'n_patches': 12}
    }
    
    world = World(seed, config)
    for name, agent in create_founders().items():
        world.add_agent(agent)
    
    # Track season changes
    rich_count = 0
    poor_count = 0
    
    for tick in range(500):
        world.tick_driver()
        if tick % 10 == 0:
            report = world.environment.get_health_report()
            if report['season'] == 'Rich':
                rich_count += 1
            else:
                poor_count += 1
    
    seasons.append({
        'seed': seed,
        'rich': rich_count,
        'poor': poor_count,
        'health': world.environment.metrics['overall_health'],
        'alive': len([a for a in world.agents.values() if a.alive])
    })

print('🌤️ SEASON ANALYSIS')
print('=' * 50)
for s in seasons:
    print(f"Seed {s['seed']}: Rich: {s['rich']:3d} ticks, Poor: {s['poor']:3d} ticks, Health: {s['health']:.3f}, Alive: {s['alive']}")
print('=' * 50)

avg_health = sum(s['health'] for s in seasons) / len(seasons)
avg_alive = sum(s['alive'] for s in seasons) / len(seasons)
avg_rich = sum(s['rich'] for s in seasons) / len(seasons)

print(f"Average health:   {avg_health:.3f}")
print(f"Average alive:    {avg_alive:.1f}")
print(f"Average Rich ticks: {avg_rich:.1f} / 50")
print('=' * 50)
