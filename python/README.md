# 🧬 Replicant — Python

**The Python implementation of the Replicant swarm.** Reference implementation for the simulation mechanics, and the home of the analysis and visualisation tooling.

For the design — the questions, the source mechanisms, the Forge Stack spine — see the [root README](../README.md). This document covers running it.

> **Status: v1.0.** 35 tests passing in ~1.5s. Runs on a Samsung S24 Ultra under Termux; 990+ continuous ticks validated.

---

## 🚀 Quick start

```sh
cd python
python scripts/run.py                   # run the simulation
python -m pytest -q                     # 35 tests
python scripts/run_viz.py               # terminal ASCII visualisation
```

**Dependencies:** the simulation core is pure standard library — no numpy, no scipy, nothing to compile. That is what makes it run unmodified on a phone. `requirements.txt` covers only the API server:

```sh
pip install -r requirements.txt         # Flask, Flask-Cors
pip install pytest                      # not in requirements; needed for the test suite
```

---

## 📂 Structure

```
python/
├── README.md                   # this document
├── CHANGELOG.md                # Good/Bad/Ugly per phase, oldest first
├── ROADMAP.md                  # what is deliberately not built yet
├── config.toml                 # simulation parameters
├── requirements.txt
├── src/                        # implementation
├── tests/                      # 35 tests
├── scripts/                    # entry points and analysis
├── nodes/                      # hardware nodes — phone, esp32, gateway
├── sc/                         # semantic capsules (replicant/)
└── wasm/www/                   # browser assets
```

### `src/` — the simulation core

Nine files are the swarm itself:

| File | What it holds |
|---|---|
| `world.py` | The tick driver, claim store, consequence application |
| `agent.py` | `sense` → `decide` → `apply_intent`, traits, mutation |
| `leighton.py` | λ as an append-only event ledger, computed on read |
| `capsule.py` | `sc` minting, lineage, canonical JSON |
| `environment.py` | Resource patches, threat zones, seasons, homeostasis metrics |
| `adversary.py` | Fabricated claims — structurally identical to honest ones |
| `founders.py` | The starting ten, with custom λ and birth ticks |
| `hal.py` | Seal tiers (mocked — see ROADMAP) |
| `config.py` | Loads `config.toml` |

**`src/` also holds work that is not the swarm.** `agent_74.py`, `six_lens.py`, `trust.py`, `knowledge_builder.py`, `pdei_core/`, `personalities/`, `skills/`, `reflexes/` and the business directories are other Forge Stack work sharing this tree. They are not imported by the simulation, and the simulation does not depend on them. If you came here for the swarm, the nine files above are the whole of it.

### `scripts/` — entry points

| Script | Purpose |
|---|---|
| `run.py` | Run a simulation from `config.toml` |
| `run_viz.py` | Terminal ASCII visualisation — agent roles, energy bars, λ, resource density, threat zones |
| `analyze_results.py` | Multi-seed statistical analysis: population stability, COUNTER generation, health consistency |
| `season_analysis.py` | Rich vs Poor season comparison |
| `debug_adversary.py` | Adversary behaviour inspection |
| `api_server.py` | Flask HTTP interface |

Terminal visualisation rather than a GUI is deliberate: macroquad needs OpenGL, which Termux does not provide. ASCII works perfectly on a phone.

### `tests/`

```
test_agent.py            test_leighton.py         test_conservation.py
test_world.py            test_capsule.py          test_stabilization.py
test_adversary.py        test_recovery.py         test_determinism_simple.py
```

Three worth knowing about:

- **`test_conservation.py`** — energy is the only currency and must not appear from nowhere. This is the test that catches an accounting leak.
- **`test_recovery.py`** — a quarantined agent can climb back out by stopping the behaviour. Validated at λ 0.410 → 0.602.
- **`test_determinism_simple.py`** — structural equality across runs on the same seed. UUID-based agent IDs make exact ledger-hash comparison unreliable, so this checks agent count, claim count and ledger length rather than a hash.

### `nodes/` — hardware

`phone/`, `esp32/`, `gateway/` and `common/`, with [its own README](nodes/README.md). The phone node feeds real sensor readings into the simulation as an agent; see [`replicant-esp32-bridge.md`](replicant-esp32-bridge.md) for the microcontroller side.

---

## ⚙️ Configuration

All parameters live in `config.toml`. The defaults:

```toml
[run]
seed = 42
ticks = 200

[swarm]
initial_agents = 10
max_agents = 1000            # diagnostic ceiling — hitting it means costs are wrong

[replication]
threshold = 70.0
cost = 40.0
birth_overhead = 10.0
required_lambda = 1.10       # HAL tier 3

[energy]
attest_cost = 0.50           # scepticism is not free
low_power_threshold = 25.0
```

**Every number is a guess written down so it can be falsified.** The two that carry the most weight:

- **`attest_cost`** — if checking a trail is free, everyone checks everything and the COUNTER bin fills trivially. If it is too dear, nobody checks and the swarm runs on unverified OPINION until a poisoned trail starves it. The interesting band is between.
- **`max_agents`** — a diagnostic, not a design parameter. Hitting the ceiling means the environment is too rich or the costs too cheap.

---

## 📊 What the runs show

- Population self-regulates to **6.8 ± 1.2** from an initial 10, without the cap being reached
- Health stabilises at **0.791 ± 0.018** across seasons and seeds
- COUNTER averages **13.8 ± 3.2** per run and tracks claim count closely at every scale
- 15+ independent runs, 7,500+ total ticks

**An empty COUNTER bin would mean disconfirmation was never sought** — a swarm that never checks rather than one that is always right. It is the sharpest health metric here, and it stays populated.

---

## 🆚 Relative to the Rust implementation

Python and Rust are parallel implementations, not a prototype and a port. Python currently **leads** on analysis and visualisation tooling and has a mocked HAL; Rust **leads** on agent archetypes and the swarm task priority system. Full breakdown in [`feature-parity-spec.md`](../feature-parity-spec.md).

---

## 🤖 Agent 74

`src/agent_74.py` is a phone-resident LLM agent — a separate concern from the swarm, sharing this directory. It has its own memory, autonomy loop and voice, and talks to a remote model over HTTP.

```sh
export AGENT74_REMOTE_URL="http://<host>:5000/api/chat"
export AGENT74_VPS_KEY="<key>"
python src/agent_74.py -p cloud
```

Presets: `default` (local Ollama), `tiny`, `cloud`, `smart`, `sleep`. For background running under Termux, `termux-wake-lock` first — Android freezes the process under Doze the moment the screen goes off, and the autonomy loop stops with it.

---

## 🛣️ Not yet built

See [ROADMAP.md](ROADMAP.md). The two largest items:

- **Tick-level capsule signing (Merkle roots)** — `Capsule.mint` currently mocks signatures. Signing every birth individually will not scale; the design calls for one signed ledger row per tick, with individual capsules verifiable by inclusion proof.
- **Optimised spatial queries** — `get_nearby_pheromones`, `get_nearby_agents` and `get_nearby_claims` are linear scans. A spatial index is needed before agent counts grow, and which structure has not been decided.

---

> *"The swarm learns. The liar pays."*
