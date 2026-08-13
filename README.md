# 🧬 Replicant

**Hybrid bio-inspired swarm framework**  
*Born pregnant. Born ready. Born signed.*

Replicant cherry-picks mechanisms from ants, bees, termites, spiders, wasps, mole-rats and aphids, and asks: **what happens when a stigmergic swarm can pay energy to make more of itself — and every claim it makes is classified, scored and witnessed?**

---

## 🏆 Status

| Component | Language | Tests | Status |
|-----------|----------|-------|--------|
| **Prototype** | Python | 35/35 | ✅ Complete |
| **Production** | Rust | 20/20 | ✅ Complete |
| **Self-Awareness** | Rust | - | ✅ Implemented |
| **WASM Demo** | JavaScript | - | ⚠️ Partial (static agents) |

---

## 📊 Key Metrics

```

✅ 55 total tests (35 Python + 20 Rust) all passing
✅ Self-replicating swarm (Aphid mode)
✅ Event-ledger reputation (append-only LambdaState)
✅ Recidivism escalation (step=1.0, floor=0.7)
✅ Organic adversary detection
✅ Real energy tracking
✅ Recovery from quarantine
✅ Self-awareness (confidence, fitness, safety)
✅ Runs on S24 Ultra (Termux)
⚠️ WASM demo: visualisation only (agents static)

```

---

## 🧬 Architecture

```

┌─────────────────────────────────────────────────────────────────┐
│                    REPLICANT v1.2                              │
│                                                                 │
│  ✅ Self-replicating swarm (Aphid mode)                        │
│  ✅ Sceptical agents (COUNTER claims)                          │
│  ✅ Event-ledger LambdaState (append-only)                     │
│  ✅ Recidivism escalation (step=1.0, floor=0.7)                │
│  ✅ World applies consequences (no agent penalties)            │
│  ✅ Organic detection (verifiers check the environment)        │
│  ✅ No FICTION label (claims are structurally identical)       │
│  ✅ Derived quarantine/expulsion (no latched state)            │
│  ✅ Real energy tracking (distance-based costs)                │
│  ✅ Recovery semantics (quarantined agents recover)            │
│  ✅ Self-awareness (confidence, fitness, safety)               │
│  ✅ Runs on S24 Ultra (Termux)                                 │
│  ⚠️ WASM demo: visualisation only (agents static)              │
│                                                                 │
│              "The swarm learns. The liar pays."                 │
│              "The swarm reflects. The agent adapts."            │
└─────────────────────────────────────────────────────────────────┘

```

---

## 🚀 Quick Start

### Python
```bash
cd python
pip install -r requirements.txt
PYTHONPATH=src python scripts/run.py
```

Rust

```bash
cd rust
cargo build
cargo test
```

WASM Demo

```bash
cd wasm/www
python -m http.server 8081
# Open http://localhost:8081
```

---

🧠 Self-Awareness Module

Replicant v1.2 includes a Computational Self-Awareness module that allows agents to:

Component Description
SelfState Tracks confidence (0-1), recent reward, anomaly rate, safety strikes, mode
FitnessEvaluator Weighted fitness: success + efficiency - stability - safety
AdaptationEngine Bounded mutation of policy parameters with min/max clamps
PolicyManager Champion/Challenger workflow with 10% improvement threshold
SafetySupervisor Hard overrides, freeze after repeated failures, rollback

Self-Awareness Metrics

· 🧠 Confidence: Agent's belief in its own decisions (0.0 – 1.0)
· 💪 Fitness: Weighted performance score (0.0 – 1.0)
· ⚠️ Safety Strikes: Cumulative violations (freeze after 3, expel after 5)
· 📦 Version: Policy genome version
· Mode: Normal (green), Cautious (orange), Recovery (red)

---

📊 Performance Summary

Load Python Rust Speedup
10 agents, 200 ticks 0.076s 0.137s 0.6×
50 agents, 200 ticks 0.626s 0.142s 4.4×
100 agents, 200 ticks 1.985s 0.187s 10.6×
100 agents, 500 ticks 3.499s 0.399s 8.8×

Rust is up to 10.6× faster than Python at scale.

---

📁 Structure

```
replicant-repo/
├── python/          # Python prototype (35/35 tests)
├── rust/            # Rust production (20/20 tests)
├── wasm/www/        # WASM browser demo
├── docs/            # Documentation
├── CHANGELOG.md     # Full changelog
└── README.md        # This file
```

---

⚠️ Known Issues

WASM Demo: Agents Are Static

· Issue: In the WASM browser demo, agents are rendered but do not move or update their positions.
· Status: Under investigation.
· Workaround: Use the Python or Rust terminal versions for full swarm behavior.
· Fix planned: Add proper agent decision-making and movement logic to the WASM step() function.

---

📜 License

MSL-1.0 (Meaning Sovereignty Licence)

---

"The swarm learns. The liar pays."
"The swarm reflects. The agent adapts."
