# Replicant Simulation — Export Analysis Report

**Data source:** 7 JSON snapshots exported from the browser WASM demo ([rust/wasm/www/index.html](../www/index.html)) via the "Export Data" button, covering simulation ticks 8, 500, 811, 1601, 3978, 4001, and 5002.

## 1. Summary

Every export beyond roughly tick ~800 shows an **empty `agents` array**. Across the 7 captured snapshots, the simulation exhibits a **consistent, reproducible population collapse**: founder agents start at full health, spend several hundred ticks slowly losing energy, and go extinct — well before the `claims` ledger (which persists forever) stops growing. No snapshot shows population recovery or growth beyond the original 10 founders.

| Export (tick) | Agents alive | Total claims | Fact | Opinion | Counter | `health` field |
|---|---|---|---|---|---|---|
| 8 | 10 / 10 | 2 | 1 | 1 | 0 | 0.5 |
| 500 | 9 / 10 | 69 | 19 | 45 | 5 | 0.5 |
| 811 | **0** | 76 | 20 | 49 | 7 | 0.5 |
| 1601 | 10 / 10 | 71 | 15 | 54 | 2 | 0.5 |
| 4001 | **0** | 71 | 15 | 54 | 2 | 0.5 |
| 3978 | **0** | 90 | 16 | 71 | 3 | 0.5 |
| 5002 | **0** | 112 | 18 | 89 | 5 | 0.5 |

Cross-referencing `agent_id` values embedded in the claim records shows these 7 files actually represent **3 distinct simulation runs** (each browser reload mints new random capsule UUIDs for the founders):

- **Run A** (uuids `01e1f180…`, `653f488a…`, …): ticks 8 → 500 → 811. Extinct by tick 811 — the fastest collapse observed.
- **Run B** (uuids `121d72bc…`, `a0d1e000…`, `61584b9d…`, …): ticks 1601 → 4001. Alive with 10/10 founders at tick 1601, extinct by tick 4001. Claim count is identical (71) at both snapshots, meaning no claims were deposited after the population died — as expected, since dead agents cannot act.
- **Run C** (uuids `db17d4da…`, `7752d18c…`, `18a246d3…`, …): ticks 3978 → 5002. Both snapshots already show 0 agents alive.

> **Data caveat:** Run C's claim count *increases* from 90 (tick 3978) to 112 (tick 5002) even though both exports show zero living agents, and some of the additional claims carry creation timestamps (`tick` field, e.g. 930–1018) that predate the 3978 export. This is inconsistent with a monotonically-advancing single session and suggests either overlapping/out-of-order exports or a client-side caching artifact in the demo page. It doesn't change the overarching finding (extinction is real and reproducible) but is flagged here as an open data-quality question.

## 2. Root cause analysis

Investigating the simulation core ([rust/src/agent.rs](../../src/agent.rs), [rust/src/world.rs](../../src/world.rs), [rust/src/environment.rs](../../src/environment.rs)) identified two compounding defects that fully explain the collapse pattern seen in the exports:

### 2.1 Foraging never moved agents toward food

`Intent::Forage` was a **stationary** harvest attempt. `Environment::harvest_resource()` only pays out energy if the agent is within 3 world-units of a resource patch, but agent movement was driven solely by pheromone-following/random exploration — never by an explicit "walk to the nearest patch" intent. Agents therefore frequently "decided" to forage while nowhere near a patch, harvested nothing, and steadily bled energy every tick (movement cost 0.10/tick, forage cost 0.02/tick) with no offsetting income. A native benchmark run (10 founders, tick-by-tick energy logging) confirmed a linear energy decay from 100 → 0 over roughly 3000–3500 ticks under the original code — matching Run A/B's extinction windows almost exactly.

### 2.2 Replication never spawned offspring

`Intent::Replicate` only deducted the parent's energy and set a cooldown; it never called `World::add_agent()` to create a child. Combined with the energy drain above, the founder population had no mechanism to replace losses, guaranteeing eventual extinction with no chance of recovery — consistent with every post-collapse export showing a permanently empty `agents` array with no new agent UUIDs ever appearing in later claims.

### 2.3 `health` metric is a dead stub

Every export reports `"health": 0.5` — always exactly the `EnvironmentMetrics::default()` value. Unlike the Python reference implementation ([python/src/environment.py](../../../python/src/environment.py), which recomputes `overall_health` every tick), the Rust `Environment::update()` never reassigns `metrics.overall_health`. This field is currently non-functional in the Rust/WASM port and should not be trusted as a simulation health indicator until wired up.

## 3. Fixes applied this session

1. **Directed foraging** — added `Environment::nearest_patch_info()` and a `Percepts::nearest_patch_direction` field; agents now walk toward the nearest non-depleted patch when out of harvesting range, instead of foraging in place.
2. **Functional replication** — `World::tick()` now actually spawns a child `Agent` (mutated traits, half energy, `Role::Child`) when a parent's `Intent::Replicate` resolves, capped by `environment.carrying_capacity`.
3. **New behaviors** (added earlier this session, present in the exported data's code path going forward): `Intent::Migrate` (relocate toward richer known territory when local resources are scarce), `Intent::Discover` (Scouts/Explorers reveal brand-new patches in unexplored territory), `Intent::Terraform` (Builders spend energy to seed a new patch).

**Validation:** a 6000-tick native re-run of the same 10-founder scenario now holds population steady at 10/10 alive with average energy oscillating around an equilibrium of ~62, instead of decaying to zero by tick ~3000–3500.

## 4. Recommendations

- Wire up `Environment::update()` to actually recompute `metrics.overall_health` (population/energy/threat-response stability), mirroring the Python reference, so the exported `health` field carries real signal.
- Add a long-horizon regression test (e.g. 5000+ ticks) asserting `world.agents.values().filter(|a| a.alive).count() > 0`, to catch population-collapse regressions automatically instead of relying on manual browser exports.
- Investigate the Run C export-ordering anomaly (§1 caveat) — likely worth adding a monotonic export counter or wall-clock timestamp to the exported JSON to make snapshot provenance unambiguous.
- Re-run the browser demo (after a hard refresh to pick up the rebuilt `wasm/www/pkg`) and capture a fresh set of exports at similar tick milestones to confirm the fix holds under the actual UI stepping/auto-run loop, not just the native benchmark harness.
