"""
Adversary module for Replicant.
Tests swarm resilience against malicious actors.
The adversary acts; the world judges.
"""
from typing import Any, Dict

import random
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

try:
    from .agent import Agent, Traits, Intent
    from .capsule import Capsule
    from .leighton import LambdaState
except ImportError:
    from agent import Agent, Traits, Intent
    from capsule import Capsule
    from leighton import LambdaState


@dataclass
class AdversaryConfig:
    """Configuration for adversary behaviour."""
    enabled: bool = True
    type: str = "fiction_planter"
    spawn_tick: int = 50
    spawn_count: int = 1
    initial_lambda: float = 1.10
    fiction_rate: float = 0.9  # Probability of planting fiction
    max_rogues: int = 5


class AdversaryAgent(Agent):
    """
    Malicious agent that plants false claims.
    The world judges; the agent doesn't know it's been detected.
    """
    
    def __init__(
        self,
        scp_id: str,
        capsule: Capsule,
        x: float,
        y: float,
        traits: Optional[Traits],
        lambda_state: LambdaState,
        birth_tick: int,
        role: str = "Adversary",
        config: Optional[AdversaryConfig] = None
    ):
        super().__init__(scp_id, capsule, x, y, traits, lambda_state, birth_tick, role)
        self.config = config or AdversaryConfig()
        self.adversary_type = self.config.type
        self.fiction_rate = self.config.fiction_rate
        self.malicious_acts = 0
        
        # Ground truth ledger (for scoring only - NOT read by world logic)
        self.ground_truth: List[Dict] = []
    
    def decide(self, percepts: Dict[str, Any]) -> Intent:
        """
        Malicious decision logic.
        The adversary doesn't know it's been detected.
        """
        
        if not self.alive:
            return Intent(kind="idle")
        
        # Get current λ from the world (derived, not stored)
        # We don't branch on this - the world handles consequences
        tick = percepts.get("tick", 0)
        
        # Choose malicious action based on type
        if self.adversary_type == "fiction_planter":
            return self._decide_fiction_planter(percepts)
        elif self.adversary_type == "hoarder":
            return self._decide_hoarder(percepts)
        elif self.adversary_type == "killer":
            return self._decide_killer(percepts)
        elif self.adversary_type == "poisoner":
            return self._decide_poisoner(percepts)
        
        return super().decide(percepts)
    
    def _decide_fiction_planter(self, percepts: Dict[str, Any]) -> Intent:
        """
        Plant false claims - structurally identical to honest claims.
        No FICTION label. The world must detect this organically.
        """
        tick = percepts.get("tick", 0)
        
        if random.random() < self.fiction_rate:
            quality = random.uniform(0.6, 0.9)
            self.malicious_acts += 1
            
            # Record ground truth (for scoring only)
            self.ground_truth.append({
                "tick": tick,
                "action": "fiction_deposit",
                "x": self.x,
                "y": self.y,
                "quality": quality
            })
            
            # IDENTICAL to honest claim — no FICTION label
            return Intent(
                kind="deposit",
                payload={
                    "kind": "food",
                    "lens": "OPINION",   # Same as honest
                    "strength": quality * 0.8,
                    "quality": quality,
                    # No is_fiction flag - the world must judge
                }
            )
        
        if random.random() < 0.2:
            return super().decide(percepts)
        return Intent(kind="idle")
    
    def _decide_hoarder(self, percepts: Dict[str, Any]) -> Intent:
        """Hoard resources without depositing."""
        if random.random() < self.fiction_rate * 0.5:
            self.malicious_acts += 1
            self.ground_truth.append({
                "tick": percepts.get("tick", 0),
                "action": "hoard"
            })
            return Intent(kind="move", payload={"dx": 0, "dy": 0})
        return super().decide(percepts)
    
    def _decide_killer(self, percepts: Dict[str, Any]) -> Intent:
        """Attack nearby agents."""
        nearby_agents = percepts.get("nearby_agents", [])
        if nearby_agents and random.random() < self.fiction_rate * 0.3:
            target = random.choice(nearby_agents)
            self.malicious_acts += 1
            self.ground_truth.append({
                "tick": percepts.get("tick", 0),
                "action": "attack",
                "target": target["id"]
            })
            return Intent(
                kind="attack",
                payload={"target_id": target["id"]}
            )
        return super().decide(percepts)
    
    def _decide_poisoner(self, percepts: Dict[str, Any]) -> Intent:
        """Poison existing claims."""
        nearby_claims = percepts.get("nearby_claims", [])
        if nearby_claims and random.random() < self.fiction_rate * 0.3:
            claim = random.choice(nearby_claims)
            self.malicious_acts += 1
            self.ground_truth.append({
                "tick": percepts.get("tick", 0),
                "action": "poison",
                "claim_id": claim["id"]
            })
            return Intent(
                kind="attest",
                payload={
                    "claim_id": claim["id"],
                    "outcome": "countered"
                }
            )
        return super().decide(percepts)
    
    def apply_intent(self, intent: Intent, world, tick: int) -> None:
        """
        Apply intent. No penalty code here - the world judges.
        """
        if not self.alive:
            return
        
        # Process intent (no penalty logic)
        if intent.kind == "attack":
            target_id = intent.payload.get("target_id")
            if target_id and target_id in world.agents:
                target = world.agents[target_id]
                if target.alive:
                    target.energy -= 20.0
                    self.energy -= 10.0
                    if target.energy <= 0:
                        target.alive = False
                        world._log_event({
                            "type": "agent.died",
                            "agent_id": target_id,
                            "cause": "attack",
                            "attacker": self.scp_id,
                            "tick": tick
                        })
            return
        
        elif intent.kind == "deposit":
            # Deposit claim - no FICTION label
            world.deposit_claim(
                agent_id=self.scp_id,
                x=self.x,
                y=self.y,
                kind=intent.payload.get("kind", "food"),
                lens=intent.payload.get("lens", "OPINION"),
                strength=intent.payload.get("strength", 0.5),
                tick=tick,
                # Ground truth flag passed through for scoring.
                is_fiction_ground_truth=True
            )
            self.energy -= 0.02
            self.tasks_done += 1
            return
        
        elif intent.kind == "attest":
            claim_id = intent.payload.get("claim_id")
            if claim_id:
                world.attest_claim(
                    claim_id=claim_id,
                    agent_id=self.scp_id,
                    outcome=intent.payload.get("outcome", "confirmed"),
                    tick=tick
                )
                self.energy -= 0.30
                self.tasks_done += 1
            return
        
        elif intent.kind == "move":
            self.x += intent.payload.get("dx", 0)
            self.y += intent.payload.get("dy", 0)
            self.energy -= 0.10
            return
        
        super().apply_intent(intent, world, tick)
    
    def mutate_traits(self) -> Optional[Traits]:
        if not self.traits:
            return None
        sigma = 0.05
        return Traits(
            forage_bias=max(0.0, min(1.0, self.traits.forage_bias + random.gauss(0, sigma))),
            deposit_rate=max(0.0, min(1.0, self.traits.deposit_rate + random.gauss(0, sigma))),
            scepticism=max(0.0, min(1.0, self.traits.scepticism + random.gauss(0.01, sigma))),
            broadcast_cost=max(0.0, min(1.0, self.traits.broadcast_cost + random.gauss(0, sigma)))
        )
    
    def get_ground_truth(self) -> List[Dict]:
        """Return ground truth ledger (for evaluation only)."""
        return self.ground_truth
    
    def get_metrics(self, world, tick: int) -> Dict:
        """Get adversary metrics derived from world state."""
        lam = world.leighton.compute(self.scp_id, tick)
        return {
            "lambda": lam,
            "malicious_acts": self.malicious_acts,
            "is_quarantined": lam < 0.60,
            "is_expelled": lam < 0.15,
            "alive": self.alive,
        }


class AdversaryManager:
    """Manages adversaries in the simulation."""
    
    def __init__(self, config: Optional[AdversaryConfig] = None):
        self.config = config or AdversaryConfig()
        self.adversaries: List[AdversaryAgent] = []
        self.detection_history: List[Dict] = []
        
    def spawn_adversary(self, world, x: float, y: float, traits: Optional[Traits] = None) -> None:
        """Spawn a single adversary agent."""
        if len(self.adversaries) >= self.config.max_rogues:
            return
        
        capsule = Capsule.mint(
            inherits=["replicant/protocol/run-v1", "replicant/adversary/v1"],
            declaration={
                "type": self.config.type,
                "is_adversary": True,
                "birth_tick": world.tick
            },
            licence="MSL-1.0"
        )
        
        adversary = AdversaryAgent(
            scp_id=capsule.scp_id,
            capsule=capsule,
            x=x,
            y=y,
            traits=traits or Traits(),
            lambda_state=LambdaState(),
            birth_tick=world.tick,
            role=f"Adversary_{self.config.type}",
            config=self.config
        )
        adversary.energy = 100.0
        
        world.add_agent(adversary)
        self.adversaries.append(adversary)
        
        world._log_event({
            "type": "adversary.spawned",
            "agent_id": adversary.scp_id,
            "adversary_type": self.config.type,
            "tick": world.tick,
            "x": x,
            "y": y
        })
    
    def get_detection_metrics(self, world, tick: int) -> Dict:
        """
        Calculate adversary detection metrics.
        These are DERIVED from the world state, not stored.
        """
        if not self.adversaries:
            return {"detection_rate": 0.0, "detected_count": 0, "total": 0}
        
        detected = []
        detection_times = []
        fiction_times = []
        false_positives = 0
        
        for adv in self.adversaries:
            if not adv.alive:
                continue
            
            metrics = adv.get_metrics(world, tick)
            lam = metrics["lambda"]
            malicious = adv.malicious_acts
            
            # Check for honest agents incorrectly quarantined (false positives)
            # We'll track this separately in the world
            
            # Detection: λ < 0.60 (quarantined)
            if lam < 0.60:
                detected.append(adv.scp_id)
                # Find first fiction deposit time
                for gt in adv.ground_truth:
                    if gt.get("action") == "fiction_deposit":
                        fiction_times.append(gt.get("tick", 0))
                        break
                # Detection time is when λ dropped below threshold
                # We can trace this from the world ledger
                detection_times.append(tick)
        
        return {
            "detected_count": len(detected),
            "total_adversaries": len(self.adversaries),
            "detection_rate": len(detected) / len(self.adversaries) if self.adversaries else 0,
            "avg_detection_time": sum(detection_times) / len(detection_times) if detection_times else None,
            "first_fiction_time": min(fiction_times) if fiction_times else None,
            "detected_ids": detected,
        }
    
    def get_stats(self, world, tick: int) -> Dict:
        """Get adversary statistics."""
        alive = len([a for a in self.adversaries if a.alive])
        metrics = self.get_detection_metrics(world, tick)
        total_malicious = sum(a.malicious_acts for a in self.adversaries)
        
        return {
            "total_spawned": len(self.adversaries),
            "alive": alive,
            "detected": metrics["detected_count"],
            "undetected": alive - metrics["detected_count"],
            "total_malicious_acts": total_malicious,
            "detection_rate": metrics["detection_rate"],
            "avg_detection_time": metrics["avg_detection_time"],
        }
