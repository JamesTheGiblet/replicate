#!/usr/bin/env python3
"""Debug adversary with organic detection — verifiers check the environment."""

import sys
sys.path.insert(0, 'src')

from world import World
from founders import create_founders
from adversary import AdversaryConfig, AdversaryManager
from agent import Agent, Traits, Intent
from capsule import Capsule
from leighton import LambdaState

config = {
    "run": {"seed": 42, "ticks": 100},
    "claims": {
        "food": {
            "retention_per_tick": 0.90,
            "commit_attestations": 1
        }
    },
    "environment": {"n_patches": 10}
}

world = World(42, config)

founders = create_founders()
for name, agent in founders.items():
    world.add_agent(agent)

adv_config = AdversaryConfig(
    type="fiction_planter",
    fiction_rate=0.9,
)
manager = AdversaryManager(adv_config)

print("🧬 Debugging Adversary — ORGANIC DETECTION")
print("=" * 60)

class OrganicVerifier(Agent):
    """
    A verifier that detects lies organically by checking the environment.
    No adversary_id — just checks if there's food at the claim location.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counters_made = 0

    def decide(self, percepts):
        nearby_claims = percepts.get("nearby_claims", [])
        
        # Check each claim — look for OPINION claims with no resource
        for claim in nearby_claims:
            if claim.get("lens") == "OPINION":
                # Check if there's actually a resource at this location
                # We need access to the environment — pass it through percepts
                environment = percepts.get("environment")
                if environment:
                    resource = environment.get_resource_at(claim["x"], claim["y"])
                    if resource < 0.1:
                        # No food — this is a false claim
                        self.counters_made += 1
                        return Intent(
                            kind="attest",
                            payload={"claim_id": claim["id"], "outcome": "countered"}
                        )
        
        return super().decide(percepts)

verifiers = []
adversary_id = None
verifier_count = 3

for tick in range(100):
    world.tick_driver()
    
    if tick == 10:
        manager.spawn_adversary(world, 30.0, 30.0)
        adv = manager.adversaries[0]
        adversary_id = adv.scp_id
        lam = world.leighton.compute(adv.scp_id, tick)
        print(f"\n[Tick {tick}] Adversary spawned with λ: {lam:.3f}")
        
        # Spawn organic verifiers around the adversary's location
        for i, (dx, dy) in enumerate([(2,0), (-2,0), (0,2)]):
            capsule = Capsule.mint(
                inherits=["replicant/protocol/run-v1"],
                declaration={"verifier": True, "organic": True},
                licence="MSL-1.0"
            )
            verifier = OrganicVerifier(
                scp_id=capsule.scp_id,
                capsule=capsule,
                x=30.0 + dx,
                y=30.0 + dy,
                traits=Traits(scepticism=1.0),
                lambda_state=LambdaState(),
                birth_tick=tick,
                role=f"OrganicVerifier_{i}"
            )
            verifier.energy = 100.0
            world.add_agent(verifier)
            verifiers.append(verifier)
            print(f"  OrganicVerifier {i} spawned at ({30.0+dx:.1f}, {30.0+dy:.1f})")
    
    if manager.adversaries and tick % 10 == 0 and tick > 10:
        adv = manager.adversaries[0]
        lam = world.leighton.compute(adv.scp_id, tick)
        event_count = len(world.leighton.get_state(adv.scp_id).events)
        malicious = adv.malicious_acts
        
        status = "Trusted"
        if not adv.alive:
            status = "EXPEL (dead)"
        elif lam < 0.15:
            status = "EXPEL"
        elif lam < 0.60:
            status = "QUARANTINE"
        
        total_counters = sum(v.counters_made for v in verifiers)
        print(f"[Tick {tick:3d}] λ: {lam:.3f} | Events: {event_count:2d} | Malicious: {malicious:2d} | Counters: {total_counters:2d} | Status: {status}")

print("\n" + "=" * 60)
print("📊 Final State:")
if manager.adversaries:
    adv = manager.adversaries[0]
    lam = world.leighton.compute(adv.scp_id, world.tick)
    event_count = len(world.leighton.get_state(adv.scp_id).events)
    offences = world.leighton.get_state(adv.scp_id).offences
    print(f"  Final λ: {lam:.3f}")
    print(f"  Event count: {event_count}")
    print(f"  Offences: {offences}")
    print(f"  Is quarantined: {lam < 0.60}")
    print(f"  Is expelled: {not adv.alive or lam < 0.15}")
    print(f"  Alive: {adv.alive}")

print("\n📋 Ground Truth Check:")
if manager.adversaries:
    fiction_claims = [c for c in world.claims.values() if c.is_ground_truth_fiction]
    adjudicated = [c for c in fiction_claims if c.lens == "COUNTER"]
    print(f"  Fiction claims total: {len(fiction_claims)}")
    print(f"  Adjudicated false: {len(adjudicated)}")
    print(f"  Detection rate: {len(adjudicated)/len(fiction_claims)*100:.1f}%" if fiction_claims else "  No fiction claims")
