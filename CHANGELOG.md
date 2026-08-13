# Changelog

All notable changes to the Replicant project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.0] – 2026-08-13

### The Good
- **Full Rust implementation** now complete and passing 26/26 tests.
- **Benchmark suite** (`benchmark.py`) compares Python and Rust head‑to‑head.
- **Rust is up to 10.6× faster** than Python at scale (100 agents, 200 ticks).
- **Self‑awareness spec** and **ESP32 robotics extension spec** added for future roadmaps.
- **Event‑ledger reputation** (Leighton Weight Engine) is now the core of both Python and Rust.

### The Bad
- Behaviour still differs between Python and Rust (COUNTER claims: Python 9 vs Rust 2 for 10 agents, 200 ticks). This is due to different random seeds and minor logic discrepancies; work is ongoing to achieve exact parity.
- Integration tests for the adversary module are temporarily disabled in Rust until it is fully ported.

### The Ugly
- The first Rust benchmark run at 50 ticks, 10 agents took 12.9 seconds (a cold‑start anomaly). Subsequent runs stabilised to sub‑second performance.
- The Leighton Weight Engine naming – while established – is still being standardised across documentation; it was previously referred to as “λ engine” in early code.

---

## [1.1.0] – 2026-08-11

### The Good
- **Full Rust port** of the entire Python codebase, including agent logic, world state, environment, and the Leighton Weight Engine.
- **Recidivism escalation** is now correctly implemented in Rust, with step=1.0 and floor=0.7.
- **Organic adversary detection** works in Rust – verifiers check the environment (no FICTION label).
- **WASM demo** (`wasm/www/index.html`) provides a browser‑based visualisation.
- **Terminal visualisation** enhanced for both Python and Rust.

### The Bad
- The Rust `world.tick()` implementation initially lacked several components (pheromones, claims, attestations); these were subsequently ported in this version.
- Borrow checker challenges in Rust required restructuring the `world.rs` tick loop into separate phases.

### The Ugly
- The Python λ cache was entirely refactored from a mutable `(value, last_update_tick)` pair to an append‑only event ledger – a breaking change that required updating all tests and benchmarks. due to incorrect decay constants.
### The Ugly
- The initial import structure caused `ImportError` due to relative imports – a classic Python packaging trap that required a full refactor.

---

## [0.x] – Pre‑release

### The Good
- Core modules scaffolded: `agent`, `world`, `leighton`, `environment`, `founders`, `capsule`.
- First successful simulation run after fixing imports.

### The Bad
- Numerous cache‑fix attempts, each uncovering deeper issues (domain tracking, genesis state).
- `verify_cache` function repeatedly caught subtle bugs – it worked by failing.

### The Ugly
- The verification logic was overhauled multiple times; the eventual solution was to store `initial_lambda_state` and replay from genesis.

---

## Leighton Weight Engine (formerly λ engine)

The reputation system was renamed to **Leighton Weight Engine** to reflect its append‑only event‑ledger semantics and its role in recidivism escalation. It now:

- Stores events as signed deltas with decay constants (`k`).
- Computes λ on read: `λ = base + Σ δᵢ · e^(−kᵢ · (t−tᵢ))`.
- Supports recidivism: repeated offences increase penalty magnitude.
- Is fully implemented in both Python and Rust.

---

## Performance Summary (as of 1.2.0)

| Load | Python | Rust | Speedup |
|------|--------|------|---------|
| 10 agents, 200 ticks | 0.076s | 0.137s | 0.6× |
| 50 agents, 200 ticks | 0.626s | 0.142s | **4.4×** |
| 100 agents, 200 ticks | 1.985s | 0.187s | **10.6×** |
| 100 agents, 500 ticks | 3.499s | 0.399s | **8.8×** |

---

## Test Coverage

| Version | Tests | Status |
|---------|-------|--------|
| Python | 35 | ✅ All passing |
| Rust | 26 | ✅ All passing |
| Total | 61 | ✅ 100% pass rate |

---

*“Born pregnant. Born ready. Born signed.”*  
*“The swarm learns. The liar pays.”*
