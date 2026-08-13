# Computational Self-Awareness Spec

## Purpose
Implement bounded self-modeling and self-modification in the Replicant system to improve behavior over time while maintaining strict safety constraints.

## Scope
- In scope: self-state tracking, fitness evaluation, bounded parameter mutation, rollback, safety gating.
- Out of scope: claims of consciousness or unrestricted runtime code rewriting.

## Runtime Targets
- Rust core simulation.
- Optional WASM-compatible telemetry output.
- Deterministic mode via fixed seed for reproducible tests.

## Functional Requirements
1. Self model
- Track confidence (0.0-1.0), recent reward, anomaly rate, safety strikes, mode.
- Keep short-term and long-term performance baselines.

2. Meta evaluator
- Compute fitness score with weighted terms:
- Task success rate.
- Energy efficiency.
- Stability variance penalty.
- Safety violation penalty.

3. Adaptation engine
- Mutate only bounded policy parameters.
- Enforce per-parameter min/max clamps.
- Enforce max change per adaptation step.

4. Policy manager
- Champion/challenger policy workflow.
- Sliding-window evaluation.
- Promote challenger only if improvement threshold is met and safety checks pass.

5. Safety supervisor
- Hard constraints override all adaptive decisions.
- Freeze adaptation after repeated safety failures.
- Roll back to last known-good checkpoint automatically.

## Data Model
- `SelfState`
- `confidence: f32`
- `recent_reward: f32`
- `anomaly_rate: f32`
- `safety_strikes: u32`
- `mode: enum { Normal, Cautious, Recovery }`

- `PolicyGenome`
- `version: u64`
- `parent_version: Option<u64>`
- `parameters: Vec<f32>` with fixed order and per-index bounds
- `validated: bool`

- `Checkpoint`
- `policy_version: u64`
- `fitness_summary: f32`
- `timestamp_tick: u32`
- `rollback_reason: Option<String>`

## Safety Constraints
- Emergency stop behaviors are not mutable.
- Mutation allowed only for approved parameter indices.
- Maximum adaptation frequency: configurable, default 1 Hz equivalent in simulation ticks.
- Failed promotion must revert within one adaptation cycle.

## Acceptance Criteria
- >= 10% improvement over baseline fitness within 10k ticks (fixed-seed A/B run).
- 0 critical safety violations during adaptation tests.
- No unbounded memory growth in 24-hour soak simulation.
- Rollback success rate 100% in injected-failure tests.

## Validation Plan
1. Deterministic baseline run.
2. Deterministic adaptation run.
3. Fault injection: noisy observations, sparse rewards, delayed feedback.
4. Compare medians and confidence intervals across seeds.
5. Regression gates for core non-adaptive behaviors.

## Implementation Notes
- Use fixed-size ring buffers for historical metrics.
- Avoid dynamic structure growth in tight loops.
- Emit telemetry snapshots suitable for WASM dashboard visualization.
