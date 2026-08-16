# 🧬 Replicant — WASM

**The Rust simulation, compiled to run in the browser.**

For the design, see the [root README](../README.md). For the Rust implementation this is built from, see [`rust/README.md`](../rust/README.md).

> **Status: builds clean.** One crate, one build script, no duplication.

---

## What's actually here

This directory holds the **built output** — `www/index.html`, `replicant.js`, `replicant_bg.wasm` — produced by `wasm-pack` from the real WASM crate, which lives one level up at [`rust/wasm/`](../rust/wasm/).

That crate — package name `replicant-wasm`, source at `rust/wasm/src/lib.rs` — depends on the main `replicant` crate (`rust = { path = ".." }`) and wraps it in a `#[wasm_bindgen]` struct: `new`, `start`, `pause`, `step`, `render`, `get_stats`, `export_state`. `step()` runs one full tick of the real simulation and redraws the canvas; nothing about the sim itself is reimplemented for the browser.

## Build

```sh
cd rust/wasm
./build.sh
```

Runs `wasm-pack build --target web --out-dir www --scope replicant`, then copies the demo `index.html` into `www/`. Output lands in `rust/wasm/www/` — this directory (`wasm/`) is a separate, older copy and is not kept in sync automatically. If you rebuild, copy the fresh output here by hand, or point your server at `rust/wasm/www/` directly and skip the copy.

Serve it:

```sh
python -m http.server 8080 --directory rust/wasm/www
```

**Must be built off the `noexec` mount.** `/storage/emulated/0/...` on Android won't execute build scripts or compiled binaries — `cargo` and `wasm-pack` both fail there with `Permission denied (os error 13)`. Work from Termux home (`~/replicate`), same as the rest of Rust — see `rust/README.md` for the full explanation.

## What was wrong, and what's fixed

This build didn't compile for most of its life. Three separate bugs, found in the order a real build hits them:

1. **`build.sh` copied a file onto itself.** `cp wasm/www/index.html wasm/www/` — source and destination were the same path, so the script failed immediately, before `wasm-pack` ever ran.
2. **`Agent::new` was missing an argument.** The Archetype refactor (see root `CHANGELOG.md`, "The Cognitive Leap") added an `archetype` parameter and updated `world.rs` and `adversary.rs` to match — but missed a third call site. Fixed by passing `Archetype::Generalist`, the same default `replicant_bench.rs` already used.
3. **Two complete, separate copies of the WASM bindings existed and linked against each other.** `rust/src/wasm/mod.rs` — gated `#[cfg(target_arch = "wasm32")]`, so no native build ever compiled it or noticed — defined the exact same `#[wasm_bindgen] struct ReplicantWASM` as `rust/wasm/src/lib.rs`. The only build path that touches both is the one this file describes, and nobody had reached it end-to-end before. The duplicate module is gone; `rust/wasm/src/lib.rs` is the one real implementation.

Two smaller ones inside `rust/wasm/src/lib.rs` itself:

- **f32/f64 mismatches throughout `render()`.** The core sim's coordinates (`agent.x`, `patch.x`, `threat.radius`, `agent.energy`) are `f32`; the canvas API (`fill_rect`, `arc`) wants `f64`. Every sim value is now cast to `f64` at the point it enters the rendering pipeline.
- **`JsValue::from_serde` no longer exists** in current `wasm-bindgen`. Replaced with `serde_wasm_bindgen::to_value` — already a dependency in `Cargo.toml`, just unused until now.

## Known gaps

- **`telemetry_history`** is collected in `step()` and never read anywhere — dead field, flagged by the compiler as unused. `mod.rs`, before it was removed, had a matching `get_telemetry()` method that was never finished either. Recording history for the browser dashboard looks like it was attempted twice and completed neither time.
- **Deprecated canvas API.** `set_fill_style`/`set_stroke_style` take a plain value in the `web-sys` version this depends on; newer `web-sys` wants a different signature. Compiles and runs fine, just warns.
- **This directory doesn't auto-update.** `rust/wasm/www/` is the live build target; this one is a manually-copied snapshot. Treat `rust/wasm/www/` as the source of truth if the two ever disagree.

## Two other things in the repo named "wasm" — not this

- **`python/wasm/www/`** isn't WASM. It's a browser front end for the *Python* implementation, backed by Flask (`python/scripts/api_server.py`). Same visual idea, entirely different mechanism — no compiled module, just polling an HTTP API.
- **`rust/wasm/exports/`** holds JSON state snapshots exported from a running browser session, analysed by root's `analyze_exports.py`. That's how the population-collapse bug (see root `CHANGELOG.md`, "The Great Extinction") was originally diagnosed.
