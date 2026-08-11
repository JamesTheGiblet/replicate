"""
Replicant Environment Simulator
Tests whether the swarm can stabilize a dynamic system.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class ResourcePatch:
    """A patch of energy resources."""
    x: float
    y: float
    energy: float
    max_energy: float
    regeneration_rate: float
    depleted: bool = False
    depletion_tick: int = 0


@dataclass
class ThreatZone:
    """A dangerous area that damages agents."""
    x: float
    y: float
    radius: float
    intensity: float
    active: bool = True
    tick_created: int = 0
    tick_decay: int = 0


class Environment:
    """
    A dynamic environment for Replicant to stabilize.
    
    Features:
    - Resource patches with depletion/regeneration
    - Threat zones that appear and fade
    - Seasonal cycles (rich/poor)
    - Population pressure (overcrowding penalty)
    - Homeostasis metrics
    """

    def __init__(
        self,
        width: float = 100.0,
        height: float = 100.0,
        n_patches: int = 10,
        seed: Optional[int] = None
    ):
        self.width = width
        self.height = height
        self.tick = 0
        
        if seed is not None:
            random.seed(seed)
        
        # Create resource patches
        self.patches: List[ResourcePatch] = []
        for _ in range(n_patches):
            x = random.uniform(5, width - 5)
            y = random.uniform(5, height - 5)
            max_energy = random.uniform(80, 120)
            regeneration_rate = random.uniform(0.5, 1.5)
            self.patches.append(ResourcePatch(
                x=x, y=y,
                energy=max_energy * random.uniform(0.5, 1.0),
                max_energy=max_energy,
                regeneration_rate=regeneration_rate
            ))
        
        # Threat zones
        self.threats: List[ThreatZone] = []
        
        # Season parameters
        self.season_cycle = 50  # ticks per season
        self.season_phase = 0
        
        # Homeostasis metrics
        self.metrics = {
            "population_stability": 0.0,
            "energy_stability": 0.0,
            "threat_response": 0.0,
            "resource_utilization": 0.0,
            "overall_health": 0.0
        }
        
        # History for stability tracking
        self.population_history: List[int] = []
        self.energy_history: List[float] = []
        self.threat_history: List[int] = []
        
        # Population pressure
        self.carrying_capacity = 20
        
        # Counter tracking
        self.threats_handled = 0
        self.resource_crises = 0

    def get_resource_at(self, x: float, y: float, radius: float = 2.0) -> float:
        """Get total energy available at a location."""
        total = 0.0
        for patch in self.patches:
            dist = math.hypot(patch.x - x, patch.y - y)
            if dist < radius and not patch.depleted:
                total += patch.energy * (1 - dist / radius)
        return total

    def harvest_resource(self, x: float, y: float, amount: float) -> float:
        """Harvest energy from nearby patches. Returns actual harvested amount."""
        harvested = 0.0
        for patch in self.patches:
            dist = math.hypot(patch.x - x, patch.y - y)
            if dist < 3.0 and not patch.depleted:
                available = patch.energy
                take = min(amount - harvested, available * 0.5)
                if take > 0:
                    patch.energy -= take
                    harvested += take
                    if patch.energy < 1.0:
                        patch.depleted = True
                        patch.depletion_tick = self.tick
                if harvested >= amount:
                    break
        return harvested

    def detect_threat(self, x: float, y: float) -> Tuple[bool, float]:
        """Check if a location is in a threat zone."""
        for threat in self.threats:
            if threat.active:
                dist = math.hypot(threat.x - x, threat.y - y)
                if dist < threat.radius:
                    return True, threat.intensity * (1 - dist / threat.radius)
        return False, 0.0

    def get_nearby_agents(self, world, x: float, y: float, radius: float) -> List:
        """Get agents near a location."""
        nearby = []
        for aid, agent in world.agents.items():
            if agent.alive:
                dist = math.hypot(agent.x - x, agent.y - y)
                if dist < radius:
                    nearby.append(agent)
        return nearby

    def update(self, world) -> None:
        """Update the environment each tick."""
        self.tick += 1
        self.season_phase = (self.season_phase + 1) % self.season_cycle
        
        # 1. Regenerate patches
        season_factor = self._season_factor()
        for patch in self.patches:
            if patch.depleted:
                # Depleted patches take longer to regenerate
                if self.tick - patch.depletion_tick > 20:
                    patch.depleted = False
                    patch.energy = patch.max_energy * 0.1
            else:
                regen = patch.regeneration_rate * season_factor
                patch.energy = min(patch.max_energy, patch.energy + regen)
        
        # 2. Spawn occasional threats
        self._spawn_threats()
        
        # 3. Decay threats
        self._decay_threats()
        
        # 4. Track population pressure
        alive = len([a for a in world.agents.values() if a.alive])
        self.population_history.append(alive)
        if len(self.population_history) > 100:
            self.population_history.pop(0)
        
        # 5. Check resource crisis
        total_energy = sum(p.energy for p in self.patches)
        self.energy_history.append(total_energy)
        if len(self.energy_history) > 100:
            self.energy_history.pop(0)
        
        # 6. Apply population pressure
        self._apply_population_pressure(world)
        
        # 7. Update metrics
        self._update_metrics(world)

    def _season_factor(self) -> float:
        """Seasonal factor affecting resource regeneration."""
        # 0.5 = winter (scarce), 1.5 = summer (abundant)
        phase = self.season_phase / self.season_cycle
        return 1.0 + 0.5 * math.sin(phase * 2 * math.pi)

    def _spawn_threats(self) -> None:
        """Spawn random threats if conditions are right."""
        # 5% chance per tick, more likely during poor seasons
        season = self._season_factor()
        base_chance = 0.02 / (season + 0.5)
        
        if random.random() < base_chance and len(self.threats) < 3:
            x = random.uniform(10, self.width - 10)
            y = random.uniform(10, self.height - 10)
            radius = random.uniform(3, 8)
            intensity = random.uniform(0.3, 0.8)
            self.threats.append(ThreatZone(
                x=x, y=y,
                radius=radius,
                intensity=intensity,
                tick_created=self.tick,
                tick_decay=self.tick + random.randint(10, 30)
            ))

    def _decay_threats(self) -> None:
        """Remove decayed threats."""
        for threat in self.threats:
            if self.tick > threat.tick_decay:
                threat.active = False
        self.threats = [t for t in self.threats if t.active]

    def _apply_population_pressure(self, world) -> None:
        """Apply penalties if population exceeds carrying capacity."""
        alive = len([a for a in world.agents.values() if a.alive])
        if alive > self.carrying_capacity:
            penalty = (alive - self.carrying_capacity) / self.carrying_capacity
            # Reduce energy regeneration globally
            for patch in self.patches:
                patch.energy -= penalty * 0.1
                patch.energy = max(0, patch.energy)

    def _update_metrics(self, world) -> None:
        """Calculate homeostasis metrics."""
        alive = len([a for a in world.agents.values() if a.alive])
        
        # Population stability: low variance over last 20 ticks
        if len(self.population_history) >= 20:
            recent = self.population_history[-20:]
            mean = sum(recent) / len(recent)
            variance = sum((p - mean) ** 2 for p in recent) / len(recent)
            self.metrics["population_stability"] = max(0, 1 - variance / 10)
        else:
            self.metrics["population_stability"] = 0.5
        
        # Energy stability: patches aren't all depleted
        depleted = sum(1 for p in self.patches if p.depleted)
        self.metrics["energy_stability"] = 1 - (depleted / len(self.patches))
        
        # Threat response: threats handled vs spawned
        # (tracked externally)
        
        # Resource utilization: energy being used vs available
        total_energy = sum(p.energy for p in self.patches)
        max_energy = sum(p.max_energy for p in self.patches)
        if max_energy > 0:
            self.metrics["resource_utilization"] = 1 - (total_energy / max_energy)
        
        # Overall health: weighted average
        self.metrics["overall_health"] = (
            self.metrics["population_stability"] * 0.3 +
            self.metrics["energy_stability"] * 0.3 +
            self.metrics["resource_utilization"] * 0.2 +
            (1 - len(self.threats) / 10) * 0.2
        )

    def get_health_report(self) -> Dict:
        """Get a complete health report."""
        return {
            "tick": self.tick,
            "metrics": self.metrics,
            "patch_count": len(self.patches),
            "depleted_patches": sum(1 for p in self.patches if p.depleted),
            "threat_count": len(self.threats),
            "total_energy": sum(p.energy for p in self.patches),
            "season": "Rich" if self._season_factor() > 1.0 else "Poor",
            "population": len([a for a in self.patches if hasattr(a, 'population')]),
            "overall_health": self.metrics["overall_health"]
        }

    def is_stable(self, threshold: float = 0.7) -> bool:
        """Check if the system has stabilized."""
        return self.metrics["overall_health"] > threshold
