# Changelog

This is a summary. Full entries — Good/Bad/Ugly, with Confidence/Risk/Severity ratings — live in the two implementation logs:

- [`python/CHANGELOG.md`](python/CHANGELOG.md) — the Python implementation, 0.1 through the Agent 74 consolidation
- [`rust/CHANGELOG.md`](rust/CHANGELOG.md) — the Rust implementation and WASM build, 0.1 through 1.2

Each entry below points at where the detail actually is.

---

## v1.2 — Agent Diversity, current

**Rust:** the `is_specialist` boolean replaced with an `Archetype` enum — `Generalist` (reacts to global swarm needs) and `Purist` (follows innate traits) implemented; live health/threat metrics; organic attestation grounded in actual local resources rather than a hardcoded probability.
→ `rust/CHANGELOG.md` [1.2.0]

**Python:** Agent 74 consolidated from roughly twenty near-duplicate files into one, config-driven instead of subclassed. Fixed: token budgets that were never honoured, a memory that fed on its own reflections, capsule constraints silently truncated out of every prompt. Grounded in real VPS inference and real stored memory; runs unattended with quiet hours.
→ `python/CHANGELOG.md` [1.1]–[1.5]

## v1.1 — WASM live, population collapse resolved

**Rust:** diagnosed and fixed the extinction bug — agents weren't moving toward food, and replication never spawned children. Browser WASM demo went from rendering convincingly over a dying simulation to actually working. `health` had been a dead stub reporting `0.5` forever; now live.
→ `rust/CHANGELOG.md` [1.1.0]

**WASM build, separately (fixed this session, not yet in either sub-changelog):** three real bugs found only by pushing a full build end to end for the first time — a self-referential `cp` in `build.sh`, a missing constructor argument from the Archetype refactor, and two complete duplicate copies of the browser bindings that linked against each other and had never been compiled together before.
→ `wasm/README.md`

## v1.0 — Python prototype validated, Rust ported

**Python:** the trust model that everything else sits on — λ as an append-only event ledger instead of a stored value, recidivism escalation, organic adversary detection with no FICTION label, quarantine and expulsion derived from the ledger rather than latched booleans. Validated: 15+ runs, 7,500+ ticks, health 0.791 ± 0.018. Getting there took a real debugging arc — five separate cache-integrity fix attempts, each one revealing the next wrong assumption, told in full as a "whack-a-mole" story.
→ `python/CHANGELOG.md` [0.1] through [1.0] — ten entries, the whole journey from `ImportError` to a green verification pass

**Rust:** initial port and scaffolding — core modules translated, WASM package set up, build blockers resolved.
→ `rust/CHANGELOG.md` [1.0.0], [0.9]

---

## Performance Summary

Speed comparison, Python vs Rust, both timed correctly (compiled release binary, no toolchain overhead in the measurement):

| Load | Python | Rust | Speedup |
|------|--------|------|---------|
| 10 agents, 50 ticks | 0.076s | 0.006s | 12.5× |
| 20 agents, 200 ticks | 0.898s | 0.046s | 19.6× |
| 50 agents, 500 ticks | 1.295s | 0.183s | 7.1× |
| 100 agents, 200 ticks | 3.850s | 0.146s | 26.3× |
| 100 agents, 500 ticks | 4.709s | 0.723s | 6.5× |

**Rust is faster at every tested scale** — average 13.1×, range 3.0×–26.3× across the full 16-point sweep in [`benchmark_results.json`](benchmark_results.json). An earlier reading of this benchmark concluded Python won at small workloads; that was a measurement artifact — the harness was timing `cargo run`'s toolchain check, not the simulation. Building once and timing the compiled binary directly removed it. See `benchmark.py`.

**Open question, not yet a bug:** at matched seed (42), Python and Rust produce different claim counts for the same agent/tick configuration. Python's `random` and Rust's `rand::StdRng` are different algorithms, so a shared seed value does not guarantee a shared trajectory between the two implementations — "deterministic" currently means reproducible *within* one language, not identical *across* both. Worth stating explicitly in `feature-parity-spec.md` before it's mistaken for a fixed regression.
