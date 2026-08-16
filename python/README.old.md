# 🧬 Replicant

**A hybrid bio-inspired swarm framework consumer, written in Rust, built on the Forge Stack.**

*Born pregnant. Born ready. Born signed.*

> **Status: pre-alpha. Nothing is built yet.** This document is the design spec. Every code block below is a contract, not a copy-paste. No benchmarks are quoted because no benchmarks have been run.

Replicant is a **consumer** of the Forge Stack, living in `consumer/replicant/`. It holds its own capsule namespace, its own consumer ledger anchored to the root chain, and inherits governance under **MSL-1.0** via the `inherits` field of every capsule it mints.

---

## 🎯 The actual question

Replicant cherry-picks mechanisms from ants, bees, termites, spiders, wasps, mole-rats and aphids, and asks a specific question: **what happens when a stigmergic swarm can pay energy to make more of itself — and every claim it makes is classified, scored and witnessed?**

Most swarm frameworks fix the population and study coordination. Replicant makes population a decision variable and studies the trade-off.

An agent that spends 40 energy to make a child is an agent that isn't foraging. A swarm that doubles is a swarm that halves its per-agent energy reserve. The interesting result is not "the swarm grows" — that's trivial. It's **where growth stops on its own**, and whether that ceiling tracks the environment's energy throughput.

The second question is the one the stack makes askable: **a pheromone trail is a claim, not a fact.** Classical stigmergy treats a deposit as ground truth. It isn't. It's one agent's assertion, possibly stale, possibly wrong, possibly hostile. Replicant runs the whole signalling layer through the Forge Stack spine: **Declare → Classify → Trust-score → Audit → Act**, so the swarm's belief state is inspectable rather than implied.

If the sim can't produce a swarm that shrinks when the environment gets poorer, or one that recovers from a poisoned trail network, the model is wrong.

---

## 🏛️ Your Place in the Stack

As a Forge Stack consumer, Replicant is a self-contained project that lives in `consumer/replicant/`. It:

- **Leverages core infrastructure** — SCP for identity, DataCube for classification, ChronoSCRIBE for audit, Leighton Weight Engine for trust, HAL for oversight.
- **Holds its own ledger** — `consumer/replicant/ledger.jsonl`, hash-chained and anchored to the root chain.
- **Has its own mission and roadmap** — defined in this README and ROADMAP.md.
- **Is governed by the stack's protocols** — every significant action is witnessed, every claim is classified, every agent is signed.

> *"You are a citizen, not a subject."* — Forge Stack Consumer Onboarding Protocol

---

## 🦸 Source mechanisms

| Animal | Mechanism | What it becomes here |
|--------|-----------|---------------------|
| 🐜 Ant | Pheromone stigmergy | Decaying claim field, `N(t) = N₀·e^(−kt)` per kind |
| 🐝 Honey bee | Waggle dance | Quality + direction broadcast, weighted by the sender's λ |
| 🪵 Termite | Blueprint-less construction | Structure claims; committed deposits bias future deposits |
| 🕷️ Social spider | Collective capture | Formation tightening under a corroborated threat claim |
| 🐝 Paper wasp | Individual recognition | **Replaced by the Leighton Weight Engine** — see below |
| 🐀 Naked mole-rat | Hypoxia tolerance | Reduced drain in a genuine low-energy state |
| 🐜 **Aphid** | **Viviparous parthenogenesis** | **Replication that costs the parent and mints a new sc** |

Seven mechanisms in isolation is a zoo, not an architecture. The couplings are the design — and the spine is what couples them.

---

## 🔩 The Forge Stack spine, mapped onto the swarm

| Stage | System → artefact | In Replicant |
|-------|-------------------|--------------|
| **Declare** | SCP → `sc` | Every agent is born with a signed genome capsule. `inherits` records the parent's `scp_id`. A child is a **new identity, not a revision.** |
| **Classify** | DataCube → `cube` | Every deposit and broadcast enters the store under a lens: FACT, COUNTER, OPINION, FICTION, CONTEXT, UNKNOWN. |
| **Trust-score** | Leighton Weight Engine → λ | Each agent holds a λ (0.00–2.00) derived from its observation stream. Not stored on capsules — signed/unsigned is binary provenance, distinct from λ. |
| **Audit** | ChronoSCRIBE → ledger | Births, deaths, attestations and seals are hash-chained events in `consumer/replicant/`, anchored to root via `event.ledger.anchor.root`. |
| **Act** | HAL → seal | Irreversible or escalating actions require a seal, and the seal refuses to issue if the authoriser's λ is below the tier threshold. |

---

### Declare — the genome capsule

Replication mints an `sc`. The parent's `scp_id` goes in `inherits`; the child's traits go in `declaration`; the run's signing key signs over canonicalised JSON (`sort_keys=True`, `separators=(',',':')`, `ensure_ascii=True`), signature object excluded, no pre-hash.

```
sc/replicant/lineage/agent-<id>.sc.json
  scp_id      replicant/agent/<uuid>
  inherits    [replicant/agent/<parent-uuid>, replicant/protocol/run-v1]
  declaration { traits, birth_tick, birth_energy }
  licence     MSL-1.0
  signature   { key_id: did:key:z6Mktu…, algorithm: Ed25519, value }
```

This gives you something the original design couldn't: a **verifiable phylogeny**. You can prove a given agent descends from a given founder, and you can replay a lineage's trait drift without trusting the sim's own logs.

**Performance warning, stated up front:** Ed25519 signing is on the order of tens of microseconds. At a thousand births per tick, per-birth signing is a five-figure microsecond bill and the tick loop dies. The mitigation is to **sign the tick, not the birth** — accumulate the tick's capsule hashes into a Merkle root and emit one signed ledger row per tick. Individual capsules stay verifiable via inclusion proof. This is not optional; it is the difference between a working sim and a demo that manages 200 agents.

---

### Classify — stigmergy as a claim network (DataCube)

A trail is an assertion. The lens says what kind.

| Lens | Deposited when |
|------|----------------|
| **OPINION** | An agent finds a resource and marks it. Default state of every new trail. |
| **FACT** | A second, independent agent follows the trail and confirms the resource. Committed. |
| **COUNTER** | An agent follows the trail and finds nothing. Counterevidence only — never "the opposite claim". |
| **FICTION** | A deliberately fabricated trail. The adversary's instrument. |
| **CONTEXT** | Terrain, `Home` markers, boundaries. Environmental, not asserted. |
| **UNKNOWN** | Unexplored space. Not absence of resource — absence of observation. |

Cube namespaces: `event.deposit.*`, `state.field.*`, `domain.terrain.*`, `behaviour.agent.*` — independent of the lens names.

The critical diagnostic falls straight out of the stack's own rule: **an empty COUNTER bin means disconfirmation was never sought.** A swarm whose COUNTER bin stays empty is not a swarm that's always right. It's a swarm that never checks. That single number is the sharpest health metric in the sim, and it doesn't exist in any conventional ant-colony implementation.

---

### Trust-score — Leighton Weight Engine (λ)

The wasp-inspired `trust_score` + `is_rogue` boolean is cut. λ replaces it wholesale, and answers three questions the original design left open:

- **λ is computed on the fly from an observation stream, never stored as truth.** An agent's reputation is derived, not asserted.
- **Neutral-attractor decay:** `λ(t) = 1.00 + (λ₀ − 1.00) · e^(−k·t)`. Silence pulls an agent back toward *unknown* (1.00), not toward *distrusted*. A quiet scout doesn't get quarantined for being quiet.
- **New agents start at λ = 1.00.** N₀ = 0 would have meant every newborn was born quarantined, unable to act, therefore unable to earn trust. Deadlock. The stack already solved this; Replicant gets the fix for free.
- **Quarantine below 0.60.** A quarantined agent's deposits are ignored by receivers and its broadcasts dropped. It is isolated by the arithmetic, not by a boolean flag.

**Attestations are the Leighton Loop's missing arrow, and in a swarm they're free.** An agent arriving at a trail and finding food *is* an attestation on the depositor's claim — a signed ledger event hash-linked to the original deposit. Disputes resolve via counter-attestation, scored with the disputing attester's λ snapshotted **strictly before** its attestation, so winning a dispute can't retroactively inflate the λ that won it.

`k` is per-domain and never called λ. Forage claims decay fast; structural claims decay slowly. Forge Theory owns the decay maths — pheromone strength and λ are the same equation with different constants, which is a genuine unification rather than a coincidence.

**Honest tension:** "never stored" is doing real work in a governance context and is expensive in a tick loop. Recomputing λ from a full observation history for 10,000 agents every tick is O(n·h) and unaffordable. The closed form is incrementally computable from `(λ₀, t₀)` plus new observations, so the runtime keeps a two-field cache and the ledger keeps the stream. That is a cache, not a stored score — but the distinction needs writing down in the capsule before someone reasonably accuses it of being a stored score with extra steps.

---

### Audit — ChronoSCRIBE (ledger)

`consumer/replicant/ledger.jsonl`, hash-chained, first row `event.ledger.anchor.root` pinning the root chain's head. Ledger rows pin `scp_id` + `sha256`, never file paths.

Event kinds:

```
event.agent.born          event.claim.deposited
event.agent.died          event.claim.attested
event.agent.quarantined   event.claim.disputed
event.tick.sealed         event.hal.seal.issued
```

This replaces the determinism test with something stronger: **same seed → identical ledger head hash.** Not "the final state looks the same" — a cryptographic equality over the entire causal history of the run. If two runs on seed 42 diverge at tick 4,000, the chain tells you the tick and the event.

Published rows are permanent. Unpublished local rows may be discarded; anything pushed never can.

---

### Act — HAL (seal)

Not every swarm action needs a human. Most need none. The ladder is consumer-defined; Replicant defines it as:

| Tier | Action class | λ required |
|------|--------------|------------|
| 1 | Routine: move, sense, deposit OPINION | ≥ 0.60 |
| 2 | Commit a claim to FACT | ≥ 0.90 |
| 3 | Replicate | ≥ 1.10 |
| 4 | Quarantine another agent; demolish a structure | ≥ 1.40 |
| 5 | Deploy to physical hardware; exceed the population ceiling | ≥ 1.70 + seal |

`hal seal` requires a verified authoriser score file. No manual λ input, ever. It refuses to seal if λ is insufficient for the tier.

**Single-operator limitation, stated rather than hidden:** every seal carries a `separation` field. In a sim where one `did:key` signs the run, the operator, and the authoriser score, that field reads `none` — meaning the seal records deliberation and intent, not enforced separation of duties. It becomes `verified` only when a distinct identity issues the score. Claiming otherwise would be the exact failure mode the stack was built to prevent.

---

## ⚙️ The tick contract

This is the part the design lives or dies on. Rust will not let agents mutate each other during a parallel pass, and pretending otherwise is how this project fails in week one.

**State is double-buffered.** Each tick reads a frozen world and writes a new one.

```
Tick(N) → Tick(N+1)

  Phase 1  SENSE      parallel, read-only     world[N] → percepts
  Phase 2  DECIDE     parallel, pure          percepts → Vec<Intent>
  Phase 3  RESOLVE    single-threaded         intents  → world[N+1]
  Phase 4  CLASSIFY   single-threaded         claims   → cube store
  Phase 5  SCORE      parallel, disjoint      attestations → λ update
  Phase 6  WITNESS    single-threaded         Merkle root → one signed ledger row
  Phase 7  DECAY      parallel, disjoint      field + λ decay
```

- Phases 1–2 are `par_iter()` over agents. No agent sees a partial update, so runs are deterministic for a given seed.
- Phase 3 is where every mutation happens: births, deaths, deposits, energy transfers, conflict arbitration.
- Phase 6 is the one signature per tick. Not one per event.
- Nothing writes to another agent's fields. Ever. A waggle dance is an `Intent::Broadcast`, resolved in phase 3 and classified in phase 4.

```rust
enum Intent {
    Move { dx: f32, dy: f32 },
    Deposit { kind: ClaimKind, lens: Lens, strength: f32 },
    Broadcast { quality: f32, dir: f32, radius: f32 },
    Attest { claim: ClaimId, outcome: Outcome },
    Replicate,
    Recharge,
}
```

Conflict rules must be explicit and total, or determinism dies: two agents claiming one resource resolve by lower `AgentId`; simultaneous replication requests resolve in ID order until the energy pool is dry.

---

## 🔋 Energy conservation

Energy is the only currency, and it does not appear from nowhere.

- **Sources:** resource nodes carry finite energy. Recharging at `Home` draws from a shared store agents must have filled.
- **Sinks:** movement, sensing, broadcast radius, attestation, and birth overhead.
- **Replication is a transfer with loss.** The parent pays; the child receives less than the parent paid.

```
parent.energy >= REPLICATION_THRESHOLD
parent.lambda >= 1.10                    // tier 3
parent.energy -= REPLICATION_COST
child.energy   = REPLICATION_COST - BIRTH_OVERHEAD
child.lambda   = 1.00                    // neutral, not inherited
```

This makes `max_agents` a diagnostic, not a design parameter. If the swarm hits the cap, the environment is too rich or the costs are too cheap — a finding, not a feature.

**Attestation costs energy.** This is the load-bearing economic decision in the whole design. If checking a trail is free, every agent checks everything and the COUNTER bin fills trivially. If it's too expensive, nobody checks and the swarm runs on unverified OPINION until a poisoned trail starves it. Somewhere between those is a swarm that allocates scepticism efficiently, and finding that band is the experiment.

**Low-power mode triggers when energy is genuinely low** (below ~25%), not below 80% — otherwise agents spend almost their entire lives in the efficient state and the mechanism does no work.

---

## 📂 Consumer Structure

```
consumer/replicant/
├── README.md                 # This document
├── ROADMAP.md                # Strategic vision
├── ledger.jsonl              # Consumer-specific audit ledger
├── config.toml               # Configuration
├── sc/                       # Semantic capsules
│   └── replicant/
│       ├── protocol/run-v1.sc.json
│       └── lineage/
├── src/                      # Rust source code
└── tests/                    # Test suite
```

---

## ⚙️ Config

```toml
[run]
seed = 42
ticks = 1000
key_id = "did:key:z6Mktu…"

[swarm]
initial_agents = 10
max_agents = 1000            # diagnostic ceiling — hitting it means costs are wrong

[replication]
threshold = 70.0
cost = 40.0
birth_overhead = 10.0
cooldown = 25
mutation_sigma = 0.05
required_lambda = 1.10       # HAL tier 3

[energy]
max = 100.0
move_cost = 0.10
sense_cost = 0.01
attest_cost = 0.50           # scepticism is not free
broadcast_cost_per_radius = 0.02
low_power_threshold = 25.0
low_power_multiplier = 0.2
recharge_rate = 0.5

[claims.food]
retention_per_tick = 0.90
commit_attestations = 2      # OPINION → FACT
min_strength = 0.01

[claims.structure]
retention_per_tick = 0.995
commit_attestations = 3
min_strength = 0.001

[claims.threat]
retention_per_tick = 0.70
commit_attestations = 1
min_strength = 0.05

[leighton]
initial = 1.00               # neutral, never 0.00
quarantine_below = 0.60
k_per_day_forage = 0.05      # mandatory, per-domain, no default
k_per_day_signal = 0.02

[hal]
separation = "none"          # single operator — records intent, not enforced separation
```

Every number here is a guess. They're written down so they can be falsified, not because they're right.

---

## 📜 Governance

Replicant inherits governance under **MSL-1.0** via the Forge Stack. The `inherits` field of every capsule records the governance in force at signing — historical, not a live pointer. Superseding governance does not invalidate prior declarations.

**Single-operator disclosure:** This project currently runs in a stack without multiple independent validators. All seals carry `separation = "none"`. This is stated honestly in every seal and in this README.

---

## 🛣️ Roadmap

See [ROADMAP.md](ROADMAP.md) for the forward-looking plan. Every completed phase is recorded in [CHANGELOG.md](CHANGELOG.md) per the stack's phase completion criteria:

1. **Build** — implementation exists and runs.
2. **Testing** — implementation has been exercised, including a deterministic re-run check.
3. **Validation** — result independently verified, including a fresh-clone check for anything published.
4. **Documentation update** — README.md, ROADMAP.md, and relevant docs updated.
5. **Changelog entry** — Good/Bad/Ugly with Confidence/Risk/Severity ratings.

---

## 🤝 Contributing

Wanted: Rust systems programmers, swarm-robotics people, RL researchers, and entomologists willing to say which of these mechanisms we've oversimplified into uselessness.

Open an issue. Reality checks are the most valuable PRs.

---

> *"No single ant is smart. But the colony is a genius. Now make the colony pay for every new member — and sign the receipt."*
```

---

This README now properly situates Replicant as a Forge Stack consumer, adhering to:
- **Consumer Onboarding Protocol** — self-contained project in `consumer/replicant/`, own ledger, own capsules
- **Documentation Style** — British English, correct terminology (SCP/sc, DataCube/cube, ChronoSCRIBE/ledger, Leighton Weight Engine/λ, HAL/seal)
- **Roadmap Process** — completion criteria (Build → Testing → Validation → Documentation → Changelog)
- **Tools Reference** — accurate descriptions of each stage and tool
- **Changelog Discipline** — Good/Bad/Ugly format, 0-10 ratings (never 0.00-2.00, reserved for λ)