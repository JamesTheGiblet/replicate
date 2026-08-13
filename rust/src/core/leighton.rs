//! Leighton Weight Engine - λ reputation with event-ledger semantics

use std::collections::HashMap;
use super::*;

#[derive(Debug, Clone)]
pub struct LeightonEngine {
    states: HashMap<String, LambdaState>,
}

impl LeightonEngine {
    // Rate constants (half-lives)
    pub const K_FORAGE: f32 = 0.02;
    pub const K_FALSE_CLAIM: f32 = 0.005;
    pub const K_ATTACK: f32 = 0.001;

    // Base deltas
    pub const DELTA_VERIFIED: f32 = 0.05;
    pub const DELTA_FALSE_CLAIM: f32 = -0.20;
    pub const DELTA_ATTACK: f32 = -0.30;
    pub const DELTA_COUNTER_REWARD: f32 = 0.03;
    pub const DELTA_CREDULITY_PENALTY: f32 = -0.05;

    // Recidivism parameters
    pub const RECIDIVISM_STEP: f32 = 1.0;
    pub const FLOOR_FALSE_CLAIM: f32 = 0.7;

    pub fn new() -> Self {
        Self {
            states: HashMap::new(),
        }
    }

    pub fn get_state(&mut self, agent_id: &str) -> &mut LambdaState {
        self.states.entry(agent_id.to_string()).or_insert_with(LambdaState::default)
    }

    pub fn compute(&mut self, agent_id: &str, current_tick: u32) -> f32 {
        self.get_state(agent_id).compute(current_tick)
    }

    pub fn apply_event(&mut self, agent_id: &str, tick: u32, delta: f32, k: f32, reason: &str) {
        let state = self.get_state(agent_id);
        state.add_event(tick, delta, k, reason.to_string());
        if state.events.len() > 100 {
            state.compact(tick, 1e-4);
        }
    }

    pub fn sweep(&mut self, current_tick: u32) {
        for state in self.states.values_mut() {
            state.compact(current_tick, 1e-4);
        }
    }

    fn apply_with_recidivism(&mut self, agent_id: &str, tick: u32, delta_base: f32, k: f32, reason: &str) {
        let state = self.get_state(agent_id);
        let priors = state.offences.get(reason).copied().unwrap_or(0);
        let multiplier = 1.0 + Self::RECIDIVISM_STEP * (priors as f32);
        let delta = delta_base * multiplier.min(5.0);
        state.offences.insert(reason.to_string(), priors + 1);
        state.add_event(tick, delta, k, reason.to_string());
        if state.events.len() > 100 {
            state.compact(tick, 1e-4);
        }
    }

    pub fn claim_verified(&mut self, agent_id: &str, tick: u32) {
        self.apply_event(agent_id, tick, Self::DELTA_VERIFIED, Self::K_FORAGE, "claim_verified");
    }

    pub fn claim_adjudicated_false(&mut self, agent_id: &str, tick: u32) {
        self.apply_with_recidivism(agent_id, tick, Self::DELTA_FALSE_CLAIM, Self::K_FALSE_CLAIM, "claim_false");
    }

    pub fn attack_detected(&mut self, agent_id: &str, tick: u32) {
        self.apply_with_recidivism(agent_id, tick, Self::DELTA_ATTACK, Self::K_ATTACK, "attack");
    }

    pub fn counter_reward(&mut self, agent_id: &str, tick: u32) {
        self.apply_event(agent_id, tick, Self::DELTA_COUNTER_REWARD, Self::K_FORAGE, "counter_reward");
    }

    pub fn credulity_penalty(&mut self, agent_id: &str, tick: u32) {
        self.apply_event(agent_id, tick, Self::DELTA_CREDULITY_PENALTY, Self::K_FORAGE, "credulity");
    }

    pub fn get_state_snapshot(&mut self, agent_id: &str, current_tick: u32) -> serde_json::Value {
        let lambda = self.compute(agent_id, current_tick);
        let state = self.get_state(agent_id);
        serde_json::json!({
            "agent_id": agent_id,
            "lambda": lambda,
            "event_count": state.events.len(),
            "offences": state.offences,
            "base": state.base,
        })
    }
}
