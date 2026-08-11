import random
import hashlib
import json
import copy
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

try:
    from .agent import Agent, Traits, Intent
    from .leighton import LeightonEngine, LambdaState
    from .capsule import Capsule
    from .environment import Environment
except ImportError:
    from agent import Agent, Traits, Intent
    from leighton import LeightonEngine, LambdaState
    from capsule import Capsule
    from environment import Environment


@dataclass
class Pheromone:
    x: float
    y: float
    agent_id: str
    kind: str
    lens: str
    strength: float
    tick: int


@dataclass
class Claim:
    id: str
    x: float
    y: float
    agent_id: str
    kind: str
    lens: str
    strength: float
    tick: int
    attestations: List[Dict] = field(default_factory=list)
    is_ground_truth_fiction: bool = False


class World:
    def __init__(self, seed: int, config: Dict[str, Any]):
        self.seed = seed
        self.config = config
        random.seed(seed)

        self.tick = 0
        self.agents: Dict[str, Agent] = {}
        self.pheromones: List[Pheromone] = []
        self.claims: Dict[str, Claim] = {}
        self.ledger: List[Dict] = []

        self.leighton = LeightonEngine()
        self._next_claim_id = 0
        
        self.environment = Environment(
            width=100.0,
            height=100.0,
            n_patches=config.get("environment", {}).get("n_patches", 10),
            seed=seed
        )
        
        self.adversary_stats = {
            "fiction_deposits": 0,
            "detection_time": None,
            "false_positives": 0,
            "swarm_cost": 0.0,  # Now tracks real energy
            "total_distance_travelled": 0.0,
            "claims_verified": 0,
        }

    def add_agent(self, agent: Agent) -> None:
        self.agents[agent.scp_id] = agent
        self._log_event({
            "type": "agent.born",
            "agent_id": agent.scp_id,
            "role": agent.role,
            "tick": self.tick,
            "energy": agent.energy,
            "x": agent.x,
            "y": agent.y
        })

    def get_nearby_pheromones(self, x: float, y: float, radius: float) -> List[Dict]:
        result = []
        for p in self.pheromones:
            if ((p.x - x)**2 + (p.y - y)**2)**0.5 < radius and p.strength > 0.01:
                result.append({"x": p.x, "y": p.y, "strength": p.strength, "kind": p.kind, "lens": p.lens})
        return result

    def get_nearby_agents(self, self_id: str, x: float, y: float, radius: float) -> List[Dict]:
        result = []
        for aid, agent in self.agents.items():
            if aid != self_id and agent.alive and ((agent.x - x)**2 + (agent.y - y)**2)**0.5 < radius:
                result.append({"id": aid, "x": agent.x, "y": agent.y, "energy": agent.energy, "role": agent.role})
        return result

    def get_nearby_claims(self, x: float, y: float, radius: float) -> List[Dict]:
        result = []
        for cid, claim in self.claims.items():
            if ((claim.x - x)**2 + (claim.y - y)**2)**0.5 < radius:
                result.append({
                    "id": cid,
                    "x": claim.x,
                    "y": claim.y,
                    "lens": claim.lens,
                    "kind": claim.kind,
                    "attestations": len(claim.attestations),
                    "agent_id": claim.agent_id
                })
        return result

    def deposit_claim(self, agent_id: str, x: float, y: float, kind: str, lens: str, strength: float, tick: int, is_fiction_ground_truth: bool = False) -> None:
        claim = Claim(
            id=f"claim-{self._next_claim_id}",
            x=x, y=y,
            agent_id=agent_id,
            kind=kind,
            lens=lens,
            strength=strength,
            tick=tick,
            is_ground_truth_fiction=is_fiction_ground_truth
        )
        self._next_claim_id += 1
        self.claims[claim.id] = claim
        
        self.pheromones.append(Pheromone(
            x=x, y=y,
            agent_id=agent_id,
            kind=kind,
            lens=lens,
            strength=strength,
            tick=tick
        ))
        
        self._log_event({
            "type": "claim.deposited",
            "claim_id": claim.id,
            "agent_id": agent_id,
            "x": x, "y": y,
            "kind": kind,
            "lens": lens,
            "strength": strength,
            "tick": tick,
            "domain": kind
        })

    def attest_claim(self, claim_id: str, agent_id: str, outcome: str, tick: int) -> None:
        if claim_id not in self.claims:
            return
        
        claim = self.claims[claim_id]
        claim.attestations.append({"agent_id": agent_id, "outcome": outcome, "tick": tick})
        
        required = self.config.get("claims", {}).get(claim.kind, {}).get("commit_attestations", 2)
        confirmations = [a for a in claim.attestations if a["outcome"] == "confirmed"]
        counters = [a for a in claim.attestations if a["outcome"] == "countered"]
        
        if len(counters) >= required and claim.lens == "OPINION":
            claim.lens = "COUNTER"
            
            # Track real energy cost for swarm
            # Calculate distance from each counter to the claim
            total_distance = 0.0
            for a in claim.attestations:
                if a["outcome"] == "countered":
                    agent = self.agents.get(a["agent_id"])
                    if agent:
                        dist = ((agent.x - claim.x)**2 + (agent.y - claim.y)**2)**0.5
                        total_distance += dist
                        # Deduct energy from agent for travelling to verify
                        agent.energy -= dist * 0.05
            
            # Track swarm cost as actual energy spent
            self.adversary_stats["swarm_cost"] += total_distance * 0.05
            self.adversary_stats["total_distance_travelled"] += total_distance
            
            # Penalize the depositor
            self.leighton.claim_adjudicated_false(claim.agent_id, tick)
            
            # Penalize agents who attested FOR it (credulity)
            for a in claim.attestations:
                if a["outcome"] == "confirmed":
                    self.leighton.credulity_penalty(a["agent_id"], tick)
            
            # Reward agents who countered it
            for a in claim.attestations:
                if a["outcome"] == "countered":
                    self.leighton.counter_reward(a["agent_id"], tick)
            
            self._log_event({
                "type": "claim.adjudicated_false",
                "claim_id": claim_id,
                "depositor": claim.agent_id,
                "counters": len(counters),
                "total_distance": total_distance,
                "swarm_cost": total_distance * 0.05,
                "tick": tick
            })
        
        elif len(confirmations) >= required and claim.lens == "OPINION":
            claim.lens = "FACT"
            self.leighton.claim_verified(claim.agent_id, tick)
            self.adversary_stats["claims_verified"] += 1
            
            self._log_event({
                "type": "claim.confirmed",
                "claim_id": claim_id,
                "depositor": claim.agent_id,
                "confirmations": len(confirmations),
                "tick": tick
            })
        
        self._log_event({
            "type": "claim.attested",
            "claim_id": claim_id,
            "agent_id": agent_id,
            "outcome": outcome,
            "tick": tick,
            "domain": claim.kind
        })

    def spawn_child(self, parent_scp_id: str, x: float, y: float, energy: float, traits: Optional[Traits], tick: int) -> None:
        capsule = Capsule.mint(
            inherits=[parent_scp_id, "replicant/protocol/run-v1"],
            declaration={
                "parent": parent_scp_id,
                "traits": traits.__dict__ if traits else None,
                "birth_tick": tick,
                "birth_pos": [x, y]
            },
            licence="MSL-1.0"
        )
        
        lambda_state = LambdaState()
        
        agent = Agent(
            scp_id=capsule.scp_id,
            capsule=capsule,
            x=x, y=y,
            traits=traits,
            lambda_state=lambda_state,
            birth_tick=tick,
            role="child"
        )
        agent.energy = energy
        
        self.add_agent(agent)

    def tick_driver(self) -> None:
        self.environment.update(self)
        
        intents = {}
        for aid, agent in self.agents.items():
            if agent.alive and not agent.is_rogue:
                percepts = agent.sense(self)
                percepts["resource_energy"] = self.environment.get_resource_at(agent.x, agent.y)
                percepts["threat_detected"], percepts["threat_intensity"] = self.environment.detect_threat(agent.x, agent.y)
                percepts["nearby_agents_count"] = len(self.get_nearby_agents(aid, agent.x, agent.y, 5.0))
                percepts["environment"] = self.environment
                intents[aid] = agent.decide(percepts)

        for aid in sorted(intents.keys()):
            agent = self.agents.get(aid)
            if agent:
                agent.apply_intent(intents[aid], self, self.tick)

        for aid, agent in self.agents.items():
            if agent.alive:
                lam = self.leighton.compute(aid, self.tick)
                
                if lam < 0.60:
                    agent.is_rogue = True
                    self._log_event({
                        "type": "agent.quarantined",
                        "agent_id": aid,
                        "lambda": lam,
                        "tick": self.tick
                    })
                else:
                    agent.is_rogue = False
                
                if lam < 0.15:
                    agent.alive = False
                    self._log_event({
                        "type": "agent.expelled",
                        "agent_id": aid,
                        "lambda": lam,
                        "tick": self.tick
                    })
                    continue
                
                threat, intensity = self.environment.detect_threat(agent.x, agent.y)
                if threat:
                    damage = intensity * 0.2
                    agent.energy -= damage
                    if agent.energy < 0:
                        agent.alive = False
                        self._log_event({
                            "type": "agent.died",
                            "agent_id": aid,
                            "cause": "threat",
                            "tick": self.tick
                        })
                
                if agent.energy < 0:
                    agent.alive = False
                    self._log_event({
                        "type": "agent.died",
                        "agent_id": aid,
                        "cause": "starvation",
                        "tick": self.tick
                    })

        ledger_hash = self._merkle_root()
        self._log_event({
            "type": "tick.sealed",
            "tick": self.tick,
            "merkle_root": ledger_hash,
            "agent_count": len([a for a in self.agents.values() if a.alive]),
            "environment_health": self.environment.metrics["overall_health"]
        })

        self._decay_pheromones()
        self.leighton.sweep(self.tick)
        
        self.tick += 1

    def _merkle_root(self) -> str:
        events = [e for e in self.ledger if e.get("tick") == self.tick]
        if not events:
            return hashlib.sha256(b"empty").hexdigest()
        combined = "".join(json.dumps(e, sort_keys=True) for e in events)
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()

    def _decay_pheromones(self) -> None:
        retention = self.config.get("claims", {}).get("food", {}).get("retention_per_tick", 0.90)
        for p in self.pheromones:
            p.strength *= retention
        self.pheromones = [p for p in self.pheromones if p.strength > 0.01]

    def _log_event(self, event: Dict) -> None:
        if self.ledger:
            event["prev_hash"] = self.ledger[-1].get("hash")
        else:
            event["prev_hash"] = "genesis"
        canonical = json.dumps(event, sort_keys=True, separators=(',',':'))
        event["hash"] = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
        self.ledger.append(event)

    def get_health_report(self) -> Dict:
        return self.environment.get_health_report()
    
    def get_adversary_stats(self) -> Dict:
        """Get adversary statistics including real energy costs."""
        return self.adversary_stats

    def detect_attack(self, attacker_id: str, target_id: str, tick: int) -> None:
        """Detect an attack and apply consequences."""
        # Apply λ penalty to attacker
        self.leighton.attack_detected(attacker_id, tick)
        
        # Log the attack
        self._log_event({
            "type": "attack_detected",
            "attacker": attacker_id,
            "target": target_id,
            "tick": tick
        })
