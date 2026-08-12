import math
import random
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum

try:
    from .capsule import Capsule
    from .leighton import LambdaState
except ImportError:
    from capsule import Capsule
    from leighton import LambdaState


class Lens(Enum):
    OPINION = "OPINION"
    FACT = "FACT"
    COUNTER = "COUNTER"
    FICTION = "FICTION"
    CONTEXT = "CONTEXT"
    UNKNOWN = "UNKNOWN"


@dataclass
class Traits:
    forage_bias: float = 0.50
    deposit_rate: float = 0.50
    scepticism: float = 0.50
    broadcast_cost: float = 0.50


@dataclass
class Intent:
    """Agent decision output."""
    kind: str
    payload: Dict[str, Any] = field(default_factory=dict)


class Agent:
    def __init__(
        self,
        scp_id: str,
        capsule: Capsule,
        x: float,
        y: float,
        traits: Optional[Traits],
        lambda_state: LambdaState,
        birth_tick: int,
        role: str = "generic"
    ):
        self.scp_id = scp_id
        self.capsule = capsule
        self.x = x
        self.y = y
        self.traits = traits
        self.lambda_state = lambda_state
        self.birth_tick = birth_tick
        self.role = role

        self.energy = 100.0
        self.alive = True
        self.tasks_done = 0
        self.is_rogue = False
        self.can_replicate = True
        self.replication_cooldown = 0

        self.last_find_quality = 0.0
        self.last_find_dir = 0.0

    def sense(self, world) -> Dict[str, Any]:
        """Phase 1: Read-only percepts."""
        return {
            "nearby_pheromones": world.get_nearby_pheromones(self.x, self.y, radius=10.0),
            "nearby_agents": world.get_nearby_agents(self.scp_id, self.x, self.y, radius=10.0),
            "nearby_claims": world.get_nearby_claims(self.x, self.y, radius=10.0),
            "energy": self.energy,
            "lambda": world.leighton.compute(self.scp_id, world.tick),
            "can_replicate": self.can_replicate,
            "tick": world.tick,
            "environment": world.environment
        }

    def decide(self, percepts: Dict[str, Any]) -> Intent:
        """Phase 2: Pure function from percepts to Intent."""

        if not self.alive:
            return Intent(kind="idle")

        if self.replication_cooldown > 0:
            self.replication_cooldown -= 1
            if self.replication_cooldown == 0:
                self.can_replicate = True

        # ATTESTATION FIRST - scepticism drives verification
        nearby_claims = percepts.get("nearby_claims", [])
        if self.traits and nearby_claims and random.random() < self.traits.scepticism * 0.4:
            claim_to_check = random.choice(nearby_claims)

            if claim_to_check.get("lens") == "OPINION":
                # Organic detection: prefer environment evidence when available.
                environment = percepts.get("environment")
                outcome = "confirmed"
                if environment:
                    resource_at_claim = environment.get_resource_at(claim_to_check["x"], claim_to_check["y"])
                    outcome = "confirmed" if resource_at_claim > 0.1 else "countered"

                return Intent(
                    kind="attest",
                    payload={"claim_id": claim_to_check["id"], "outcome": outcome}
                )

        # Ant: follow strongest pheromone
        pheromones = percepts.get("nearby_pheromones", [])
        if pheromones:
            strongest = max(pheromones, key=lambda p: p["strength"])
            angle = math.atan2(strongest["y"] - self.y, strongest["x"] - self.x)
            return Intent(
                kind="move",
                payload={"dx": math.cos(angle) * 0.5, "dy": math.sin(angle) * 0.5}
            )

        # Explore or exploit
        if self.traits and random.random() < self.traits.forage_bias:
            return Intent(
                kind="move",
                payload={"dx": random.uniform(-1.0, 1.0), "dy": random.uniform(-1.0, 1.0)}
            )

        # Find resource and deposit
        if random.random() < 0.2:
            quality = random.random()
            return Intent(
                kind="deposit",
                payload={
                    "kind": "food",
                    "lens": "OPINION",
                    "strength": quality * 0.5,
                    "quality": quality
                }
            )

        # Replicate
        if self.can_replicate and self.energy >= 70.0 and percepts["lambda"] >= 1.10:
            return Intent(kind="replicate", payload={})

        # Recharge
        if self.energy < 25.0:
            return Intent(kind="recharge", payload={})

        return Intent(kind="idle")

    def apply_intent(self, intent: Intent, world, tick: int) -> None:
        """Phase 3: Apply intent (mutates world). Called by resolver."""

        if not self.alive:
            return

        if intent.kind == "move":
            self.x += intent.payload.get("dx", 0)
            self.y += intent.payload.get("dy", 0)
            self.energy -= 0.10
            self.energy = max(0, self.energy)

        elif intent.kind == "deposit":
            world.deposit_claim(
                agent_id=self.scp_id,
                x=self.x,
                y=self.y,
                kind=intent.payload.get("kind", "food"),
                lens=intent.payload.get("lens", "OPINION"),
                strength=intent.payload.get("strength", 0.5),
                tick=tick,
                is_fiction_ground_truth=False
            )
            self.energy -= 0.05
            self.tasks_done += 1

        elif intent.kind == "attest":
            claim_id = intent.payload.get("claim_id")
            outcome = intent.payload.get("outcome")
            if claim_id and outcome:
                world.attest_claim(
                    claim_id=claim_id,
                    agent_id=self.scp_id,
                    outcome=outcome,
                    tick=tick
                )
                self.energy -= 0.50
                self.tasks_done += 1

        elif intent.kind == "replicate":
            if self.can_replicate and self.energy >= 70.0:
                cost = 40.0
                self.energy -= cost
                self.can_replicate = False
                self.replication_cooldown = 25

                child_energy = cost - 10.0
                world.spawn_child(
                    parent_scp_id=self.scp_id,
                    x=self.x + random.uniform(-1.0, 1.0),
                    y=self.y + random.uniform(-1.0, 1.0),
                    energy=child_energy,
                    traits=self.mutate_traits(),
                    tick=tick
                )

        elif intent.kind == "recharge":
            self.energy += 0.5
            self.energy = min(100.0, self.energy)

        # Attack detection - if this agent was attacked, it's detected elsewhere
        # The world handles attack detection when an attack is logged

    def mutate_traits(self) -> Optional[Traits]:
        """Aphid-inspired mutation: small perturbation."""
        if not self.traits:
            return None

        sigma = 0.05
        return Traits(
            forage_bias=max(0.0, min(1.0, self.traits.forage_bias + random.gauss(0, sigma))),
            deposit_rate=max(0.0, min(1.0, self.traits.deposit_rate + random.gauss(0, sigma))),
            scepticism=max(0.0, min(1.0, self.traits.scepticism + random.gauss(0, sigma))),
            broadcast_cost=max(0.0, min(1.0, self.traits.broadcast_cost + random.gauss(0, sigma)))
        )
