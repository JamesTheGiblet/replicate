# Replicant Consumer Roadmap

This document outlines what is not yet built and what is intentionally deferred for the `Replicant` consumer. It is the forward-looking complement to `CHANGELOG.md`'s backward-looking record.

When an item here is completed, it is removed from this document and a corresponding entry is made in `CHANGELOG.md`.

---

## 1. Scaling & Performance

### 1.1. Tick-level Capsule Signing (Merkle Roots)

* ***What is missing:** The current `Capsule.mint` mocks signatures for individual agents. For large-scale simulations, signing every agent birth is computationally prohibitive. The `README.md` explicitly calls for "sign the tick, not the birth."
* ***Why it matters:** Direct signing of every agent birth will cause the simulation's tick loop to become extremely slow and unscalable. Accumulating capsule hashes into a Merkle root and emitting one signed ledger row per tick is essential for performance while maintaining auditability via inclusion proofs.
* ***What blocks it:** A **capability not yet buildable**. Requires integration with `freeze.py` and `ledger.py` to generate Merkle roots for all capsules minted within a tick and to verify inclusion proofs.

### 1.2. Optimized Spatial Queries

* ***What is missing:** The current `get_nearby_pheromones`, `get_nearby_agents`, and `get_nearby_claims` functions perform linear scans.
* ***Why it matters:** As the number of agents, pheromones, and claims grows, these linear scans will become a performance bottleneck, slowing down the `sense` phase of the simulation.
* ***What blocks it:** A **decision not yet made**. Requires choosing and implementing a spatial indexing structure (e.g., k-d tree, quadtree) suitable for the simulation's needs.

---

## 2. Agent Behavior & Ecology

### 2.1. Disconfirmation Seeking

* ***What is missing:** Agents currently do not actively seek out disconfirmation for claims. The simulation consistently reports "COUNTER claims: 0".
* ***Why it matters:** A core diagnostic of the `Replicant` simulation is to observe whether the swarm can recover from poisoned trail networks. This requires agents to actively challenge claims and generate counter-evidence.
* ***What blocks it:** A **decision not yet made**. Requires designing new agent intents and updating the `decide` logic to include strategies for investigating and attesting `COUNTER` claims.

### 2.2. Dynamic Trait Evolution

* ***What is missing:** Agent traits mutate randomly, but there's no explicit selection pressure or mechanism for successful traits to propagate more effectively.
* ***Why it matters:** To study the "trade-off" of population as a decision variable and how growth stops on its own, the simulation needs a more sophisticated mechanism for trait evolution that responds to environmental conditions.
* ***What blocks it:** A **decision not yet made**. Requires defining fitness functions, more complex mutation strategies, and potentially a genetic algorithm-like selection process within the `replicate` intent.

### 2.3. Response to HAL Seals

* ***What is missing:** Agents do not currently react to HAL seals (e.g., an agent being quarantined).
* ***Why it matters:** For HAL to be an effective governance layer, agents must be able to perceive and respond to its decisions, such as avoiding quarantined agents or respecting demolition seals.
* ***What blocks it:** A **decision not yet made**. Requires updating the `sense` and `decide` logic to incorporate information about HAL seals and to formulate appropriate responses.

---

## 3. Governance & Auditability

### 3.1. Full HAL Integration for Critical Actions

* ***What is missing:** The current `hal.py` is a mock for beta, and agent actions do not explicitly request seals for high-consequence actions beyond replication.
* ***Why it matters:** To fully realize the Forge Stack's governance model, agents should explicitly request and receive HAL seals for actions like quarantining other agents, demolishing structures, or exceeding population ceilings.
* ***What blocks it:** A **capability not yet buildable**. Requires a more sophisticated HAL implementation in `hal.py` and `world.py` to handle seal requests, and potentially a mechanism for external human validators to issue seals.

### 3.2. Configuration Management via `config.toml`

* ***What is missing:** Simulation parameters are currently hardcoded in `run.py`'s `load_config` function.
* ***Why it matters:** The `README.md` emphasizes that "Every number here is a guess. They're written down so they can be falsified, not because they're right." A robust configuration system is crucial for systematic experimentation and falsification of these parameters.
* ***What blocks it:** A **capability not yet buildable**. Requires implementing a TOML parser and integrating it into the simulation's initialization.

### 3.3. Ledger Export and Analysis

* ***What is missing:** The simulation's ledger is currently only printed to console. There is no mechanism to save it to a file for post-simulation analysis.
* ***Why it matters:** The ledger is the immutable record of the simulation's history. Exporting it allows for detailed, offline analysis and verification of simulation runs.
* ***What blocks it:** A **capability not yet buildable**. Requires adding a function to `run.py` to write the `world.ledger` to a `.jsonl` file.

---

## 4. Visualization & Debugging

### 4.1. Real-time Simulation Visualization

* ***What is missing:** While a basic web-based visualization is now functional, it lacks detailed rendering of agent roles, energy levels, and pheromone trails. The current visualization is also limited to basic shapes and colors.
* ***Why it matters:** Richer visualizations are crucial for deeper insights into swarm behavior, especially for debugging complex interactions and emergent properties.
* ***What blocks it:** A **decision not yet made**. Requires further development of the web frontend (JavaScript/Canvas) to consume more detailed API data and render it effectively. This includes implementing agent role-based coloring, energy indicators, and potentially pheromone trail rendering.

### 4.2. Enhanced Debugging Tools

* ***What is missing:** Tools to inspect the state of individual agents, claims, or the world at specific ticks.
* ***Why it matters:** When `MISMATCH DETECTED!` or other unexpected behaviors occur, detailed state inspection is crucial for identifying the root cause.
* **What blocks it:** A **decision not yet made**. Requires designing a debugging interface or logging system that can capture and present granular state information.
