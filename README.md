# 🧬 Replicant

**Hybrid bio-inspired swarm framework**  
*Born pregnant. Born ready. Born signed.*

Replicant cherry-picks mechanisms from ants, bees, termites, spiders, wasps, mole-rats and aphids, and asks: **what happens when a stigmergic swarm can pay energy to make more of itself — and every claim it makes is classified, scored and witnessed?**

---

## 🏆 Status

| Component | Language | Tests | Status |
|-----------|----------|-------|--------|
| **Prototype** | Python | 35/35 | ✅ Complete |
| **Production** | Rust | 26/26 | ✅ Complete |
| **WASM Demo** | JavaScript | - | ✅ Working |

---

## 📊 Key Metrics

```

✅ 61 total tests (35 Python + 26 Rust) all passing
✅ Self-replicating swarm (Aphid mode)
✅ Event-ledger reputation (append-only LambdaState)
✅ Recidivism escalation (step=1.0, floor=0.7)
✅ Organic adversary detection
✅ Real energy tracking
✅ Recovery from quarantine
✅ Runs on S24 Ultra (Termux)
✅ WASM browser demo

```

---

## 🚀 Quick Start

### Python
```bash
cd python
pip install -r requirements.txt
python run.py
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
python -m http.server 8080
# Open http://localhost:8080
```

---

🧬 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    REPLICANT v1.0                              │
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
│  ✅ Runs on S24 Ultra (Termux)                                 │
│  ✅ WASM browser demo                                          │
│                                                                 │
│              "The swarm learns. The liar pays."                 │
└─────────────────────────────────────────────────────────────────┘
```

---

📁 Structure

```
replicant-repo/
├── python/          # Python prototype (35/35 tests)
├── rust/            # Rust production (26/26 tests)
├── wasm/www/        # WASM browser demo
├── docs/            # Documentation
└── README.md        # This file
```

---

📜 License

MSL-1.0 (Meaning Sovereignty Licence)

---

"The swarm learns. The liar pays."
