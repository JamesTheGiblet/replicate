# Changelog

All notable changes to the Replicant project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
but adapted to a narrative "Good/Bad/Ugly" format to capture the journey of discovery.

---

## [1.2.0] - The Cognitive Leap

### The Good
- **Agent Diversity Framework Implemented (Phase 1):** Replaced the simple `is_specialist` boolean with a more sophisticated `Archetype` enum. Implemented the first two archetypes:
  - **`Generalist`:** Reacts dynamically to global swarm needs (e.g., `global_forager_need`).
  - **`Purist`:** Ignores swarm needs to focus on roles that match its innate `Traits`, preserving specialized knowledge.
- **Dynamic Explorer Need:** Replaced the static `global_explorer_need` placeholder with a dynamic calculation based on the rate of recent resource discoveries. The swarm now intelligently balances exploration and exploitation.
- **Live Health & Threat Metrics:** Fixed the static `health` and `threat_response` metrics. They are now live, dynamic indicators of the swarm's ability to maintain homeostasis and avoid danger.
- **Organic Attestation Logic:** Replaced the hardcoded `rng.gen_bool(0.7)` for attestation. Agents now check the actual `local_resource` in their percepts to confirm or counter claims, grounding their scepticism in reality.
- **Evidence-Based Claim Strength:** The strength of new `Deposit` claims is now proportional to the actual resources an agent has found, making the claim network more informative.
- **Unified Design Document:** Consolidated all future-facing features (Gender, Culture, Memes, Games) into the `agent-diversity-spec.md`, creating a single, comprehensive roadmap for achieving AGI.

### The Bad
- The introduction of the `Archetype` system caused a cascade of compiler errors, as agent constructors in `world.rs` and `adversary.rs` needed to be updated. This was a necessary friction to ensure system-wide consistency.

### The Ugly
- The process of fixing the placeholder logic revealed just how many "good enough for now" shortcuts were in the codebase. It served as a valuable reminder that a solid foundation requires replacing all stubs with dynamic, principled logic.

---

## [1.1.0] - The Great Extinction & The Rust Port

### The Good
- **Population Collapse Solved:** Diagnosed and fixed the critical simulation-ending bugs identified in `ANALYSIS_REPORT.md`. This resolved the consistent, reproducible population collapse observed in early Rust/WASM exports.
  - **Root Cause 1: Foraging never moved agents toward food.** `Intent::Forage` was a stationary harvest attempt, leading agents to starve while "foraging" in barren areas.
  - **Fix 1: Directed foraging.** Agents now use `Environment::nearest_patch_info()` to actively walk toward the nearest non-depleted patch when out of harvesting range.
  - **Root Cause 2: Replication never spawned offspring.** `Intent::Replicate` only deducted parent energy; it never created a child agent.
  - **Fix 2: Functional replication.** `World::tick()` now correctly spawns a child `Agent` (with mutated traits and half energy) when a parent's `Intent::Replicate` resolves, capped by `environment.carrying_capacity`.
- **WASM Demo Is Fully Live:** Resolved the "Static Agents" issue. The browser visualization now accurately renders agent movement, claim network evolution, and live health metrics, making it a viable tool for observation and analysis.

### The Bad
- The population collapse was a severe, systemic failure that required detailed analysis of exported JSON snapshots to diagnose. It highlighted the need for more robust integration testing.

### The Ugly
- The `health` metric was a dead stub, always reporting `0.5`, masking the true severity of the population collapse. This was a critical failure in observability.
- The fact that the simulation *looked* like it was working in the browser while the population was going extinct was a stark lesson: visual liveness is not state correctness.

---

## [1.0.0] - The Python Prototype & The Liar Who Pays

### The Good
- **Python Prototype Completed & Validated:** Built and stabilized the initial Python simulation, proving the core concepts were viable. The system demonstrated stable homeostasis over thousands of ticks and across multiple random seeds.
- **Event-Ledger Reputation Implemented:** The Leighton Weight Engine, with its append-only `LambdaEvent` ledger, was implemented. This permanently solved the "cache vs. ledger" integrity issues that plagued earlier versions.
- **Economic Model Proven:** The system successfully demonstrated that a swarm can self-regulate its population based on energy costs, and that scepticism (attesting `COUNTER` claims) is an economically viable strategy.

### The Bad
- Numerous cache‑fix attempts, each uncovering deeper issues (domain tracking, genesis state).
- `verify_cache` function repeatedly caught subtle bugs – it worked by failing.

### The Ugly
- The journey to a verifiable Leighton Weight implementation was a painful but necessary process of "whack-a-mole," where fixing one incorrect assumption in the verification logic only revealed another. This process was the ultimate validation of the "trust but verify" philosophy.

---

## Performance Summary (as of 1.1.0)

| Load | Python | Rust | Speedup |
|------|--------|------|---------|
| 10 agents, 200 ticks | 0.076s | 0.137s | 0.6× |
| 50 agents, 200 ticks | 0.626s | 0.142s | **4.4×** |
| 100 agents, 200 ticks | 1.985s | 0.187s | **10.6×** |
| 100 agents, 500 ticks | 3.499s | 0.399s | **8.8×** |
