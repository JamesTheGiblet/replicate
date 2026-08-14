# 🧬 Replicant Feature Parity Specification

**Version: 0.1**
**Status: Proposed**

---

## 1. Purpose

This document serves as a living specification to track the feature parity and implementation status of key Replicant capabilities across its Python prototype and Rust production implementations. Its goal is to provide a clear overview of what has been built, what is in progress, and what remains to be implemented in each language, ensuring both versions can eventually achieve full functional equivalence and serve their respective roles (rapid prototyping/analysis vs. high-performance production/WASM).

---

## 2. Feature Categories

Features are grouped by logical components of the Replicant system.

### 2.1. Core Simulation Mechanics

| Feature | Python Status | Rust Status | Notes |
|---|---|---|---|
| **Agent Lifecycle (Birth, Death, Energy)** | ✅ Implemented | ✅ Implemented | Core agent mechanics, including energy consumption for movement, sensing, etc. |
| **Aphid-style Replication** | ✅ Implemented | ✅ Implemented | Parent pays cost, child minted. Fixed population collapse in Rust. |
| **Dynamic Environment** | ✅ Implemented | ✅ Implemented | Resource patches (deplete/regenerate), threat zones (appear/decay), seasonal cycles. |
| **Stigmergic Claim Network** | ✅ Implemented | ✅ Implemented | Agents deposit claims (pheromones) that decay over time. |
| **Leighton Weight Engine (λ)** | ✅ Implemented | ✅ Implemented | Append-only event ledger for reputation, computed on read. |
| **Recidivism Escalation** | ✅ Implemented | ✅ Implemented | Penalties for false claims increase with prior offenses. |
| **Organic Adversary Detection** | ✅ Implemented | ✅ Implemented | Swarm detects lies by checking environment, no `FICTION` label. |
| **Derived Rogue Status (Quarantine/Expulsion)** | ✅ Implemented | ✅ Implemented | Agent status computed from λ, not latched booleans. |
| **Tick Contract (Phased Execution)** | ✅ Implemented | ✅ Implemented | Double-buffered state, parallel sense/decide, single-threaded resolve. |
| **Energy Conservation** | ✅ Implemented | ✅ Implemented | All energy accounted for (sources/sinks), replication is lossy. |

### 2.2. Agent Cognitive & Social Diversity

| Feature | Python Status | Rust Status | Notes |
|---|---|---|---|
| **Agent Archetypes (Generalist, Purist)** | ❌ Not Implemented | ✅ Implemented | Phase 1 of `agent-diversity-spec.md` completed in Rust. Python uses simpler `is_specialist`. |
| **Archetype: Contrarian** | 💡 Design Only | ❌ Not Implemented | Defined in `agent-diversity-spec.md`. |
| **Archetype: Opportunist** | 💡 Design Only | ❌ Not Implemented | Defined in `agent-diversity-spec.md`. |
| **Archetype: Historian** | 💡 Design Only | ❌ Not Implemented | Defined in `agent-diversity-spec.md`. Requires Agent Memory. |
| **Archetype: Messenger** | 💡 Design Only | ❌ Not Implemented | Defined in `agent-diversity-spec.md`. |
| **Archetype: Gamewright** | 💡 Design Only | ❌ Not Implemented | Defined in `agent-diversity-spec.md`. |
| **Swarm Task Priority System** | ❌ Not Implemented | ✅ Implemented | Global needs (forager, builder, explorer, etc.) calculated by World, used by Generalists. |
| **Agent Memory (Chronicle)** | 💡 Design Only | ❌ Not Implemented | Defined in `agent-diversity-spec.md`. |
| **Gender & Mating** | 💡 Design Only | ❌ Not Implemented | Defined in `agent-diversity-spec.md`. |
| **Cultural Memes** | 💡 Design Only | ❌ Not Implemented | Defined in `agent-diversity-spec.md`. |
| **Game Invention & Play** | 💡 Design Only | ❌ Not Implemented | Defined in `agent-diversity-spec.md`. |

### 2.3. Governance & Auditability (Forge Stack Integration)

| Feature | Python Status | Rust Status | Notes |
|---|---|---|---|
| **SCP (Semantic Capsule Primitive)** | ✅ Implemented | ✅ Implemented | Every agent is a signed genome capsule. |
| **DataCube (Claim Classification)** | ✅ Implemented | ✅ Implemented | Claims classified by Lens (OPINION, FACT, COUNTER, etc.). |
| **ChronoSCRIBE (Ledger)** | ✅ Implemented | ✅ Implemented | Hash-chained event ledger for auditability. |
| **HAL (Seal)** | 🚧 Mocked | ❌ Not Implemented | Python has a mock. Rust needs full implementation. |
| **Tick-level Capsule Signing (Merkle Roots)** | 💡 Design Only | ❌ Not Implemented | Essential for performance at scale. |

### 2.4. Performance, Visualization & Debugging

| Feature | Python Status | Rust Status | Notes |
|---|---|---|---|
| **Terminal Visualization** | ✅ Implemented | ❌ Not Implemented | Python has rich ASCII viz. Rust has basic terminal output. |
| **WASM Browser Visualization** | ❌ Not Implemented | ✅ Implemented | Live, interactive, shows agents, claims, health. |
| **Optimized Spatial Queries** | ❌ Not Implemented | ❌ Not Implemented | Both use linear scans. |
| **Configuration Management (TOML)** | ❌ Not Implemented | ❌ Not Implemented | Python uses dict. Rust uses struct. Neither uses TOML file. |
| **Ledger Export** | ❌ Not Implemented | ✅ Implemented | Rust WASM can export JSON snapshots. Python prints to console. |
| **Statistical Analysis Framework** | ✅ Implemented | ❌ Not Implemented | Python has `analyze_results.py`. |
| **Enhanced Debugging Tools** | ❌ Not Implemented | ❌ Not Implemented | |

### 2.5. Self-Awareness & Robotics

| Feature | Python Status | Rust Status | Notes |
|---|---|---|---|
| **Computational Self-Awareness Module** | 💡 Design Only | 💡 Design Only | Defined in `self-awareness-spec.md`. |
| **ESP32 Robotics Extension** | 💡 Design Only | 💡 Design Only | Defined in `esp32-robotics-extension-spec.md`. |

---

## 3. Roadmap Alignment

This document directly supports the roadmap defined in `agent-diversity-spec.md` by providing a granular view of implementation progress for each feature. As phases are completed, their status in this document will be updated.