# 🧬 Replicant — Rust

**The Rust implementation of the Replicant swarm, and the source of the WebAssembly build.**

For the design — the questions, the source mechanisms, the Forge Stack spine — see the [root README](../README.md). This document covers building and running it.

> **Status: v1.2.0.** 26 tests passing. Core compiles cleanly, the WASM package builds, and the browser simulation updates in real time.

---

## ⚠️ Building on Android

`cargo test` fails from the repository's usual location with:

```
Permission denied (os error 13)
could not execute process .../target/debug/build/proc-macro2-.../build-script-build
```

**This is not a code failure.** `/storage/emulated/0/` is mounted `noexec` on Android, so cargo cannot execute the build scripts it has just compiled. Copy the crate into the Termux home directory, which is not:

```sh
cp -r /storage/emulated/0/Download/replicate/rust ~/replicate-rust
cd ~/replicate-rust
cargo test
```

Everything below assumes a path that allows execution.

---

## 🚀 Quick start

```sh
cargo test                              # 26 tests
cargo run --bin replicant_bench         # benchmark harness
cargo build --release                   # optimised build
wasm-pack build --target web            # browser module
```

---

## 📂 Structure

```
rust/
├── README.md                   # this document
├── CHANGELOG.md                # Good/Bad/Ugly, newest first
├── Cargo.toml
├── src/
│   ├── lib.rs                  # crate root
│   ├── agent.rs                # sense → decide → apply, archetypes, traits
│   ├── world.rs                # tick driver, claim store, consequences
│   ├── environment.rs          # resource patches, threat zones, seasons
│   ├── adversary.rs            # fabricated claims
│   ├── founders.rs             # the starting ten
│   ├── awareness.rs            # bounded self-awareness
│   ├── viz.rs                  # visualisation
│   ├── core/
│   │   ├── mod.rs
│   │   └── leighton.rs         # λ as an append-only event ledger
│   ├── wasm/mod.rs             # wasm-bindgen exports
│   └── bin/replicant_bench.rs
├── tests/
│   ├── capsule_tests.rs
│   ├── core_tests.rs
│   ├── leighton_tests.rs
│   ├── traits_tests.rs
│   └── disabled/
│       └── integration_tests.rs
└── wasm/                       # browser demo assets
```

`awareness.rs` has no Python counterpart — see [`self-awareness-spec.md`](../self-awareness-spec.md).

**`tests/disabled/integration_tests.rs` is not in the 26.** Worth knowing what that costs: the v1.1 population collapse — agents not moving toward food, `Intent::Replicate` not spawning children — was diagnosed by analysing exported JSON dumps, because no test exercised the whole tick loop. That is precisely the gap an integration test closes.

---

## 📦 Dependencies, and why

| Crate | Purpose |
|---|---|
| `rayon` | Phases 1–2 of the tick contract — `par_iter()` over agents for sense and decide |
| `ed25519-dalek`, `sha2` | Capsule signing and the hash-chained ledger |
| `serde`, `serde_json` | Ledger rows, capsule canonicalisation, stats export to JS |
| `uuid` | Agent identity |
| `rand` (`std_rng`) | Seeded determinism — same seed, same run |
| `wasm-bindgen`, `js-sys`, `web-sys` | Browser build; `web-sys` pulls in canvas rendering only |
| `getrandom` (`js` feature) | Required for `rand` under WASM, where there is no OS entropy source |

The crate is `crate-type = ["cdylib", "rlib"]` — it builds as both a normal Rust library and a WebAssembly module from the same source. Feature flags: `default = ["std"]`, with `std` isolated so the core can eventually build without it.

---

## 🧬 What Rust leads on

Rust is **not a port trailing the Python.** Two capabilities exist here and not there:

- **Agent archetypes.** The `is_specialist` boolean was replaced with an `Archetype` enum. `Generalist` reacts to global swarm needs; `Purist` ignores them and follows its innate `Traits`, preserving specialised knowledge under pressure.
- **Swarm task priority.** The world computes global needs — forager, builder, explorer — and `Generalist` agents respond. `global_explorer_need` derives from the rate of recent resource discoveries rather than sitting as a constant.

Both come from [`agent-diversity-spec.md`](../agent-diversity-spec.md), Phase 1 complete. The remaining archetypes — Contrarian, Opportunist, Historian, Messenger, Gamewright — are design only.

## 🚧 What Rust lacks

- **HAL seal** — not implemented. Python has a mock.
- **Tick-level capsule signing (Merkle roots)** — design only in both implementations. Signing each birth individually will not scale; the design calls for one signed ledger row per tick, with individual capsules verifiable by inclusion proof.

Full comparison in [`feature-parity-spec.md`](../feature-parity-spec.md).

---

## 🐛 Two lessons worth keeping in view

**Working visuals can hide dead state.** In v1.1 the browser demo rendered agent movement convincingly while the population went extinct behind it. The canvas was correct; the state plumbing was not. Visual liveness is not state correctness — check the stats, not the pixels.

**Direct translation is not a port.** The initial pass from Python produced un-idiomatic Rust and a run of borrow-checker fights, on top of `rand` version mismatches across five modules. The refactor to idiomatic Rust was the real work, and it is what made archetypes possible here first.

---

> *"From static demo to cognitive swarm. The swarm learns. The liar pays."*
