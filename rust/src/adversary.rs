//! Adversary module – tests swarm resilience

use crate::core::*;
use crate::agent::*;
use crate::world::World;
use rand::Rng;
use serde::{Deserialize, Serialize};

/// Configuration for adversary behaviour
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AdversaryConfig {
    pub enabled: bool,
    pub adversary_type: String,
    pub spawn_tick: u32,
    pub spawn_count: u32,
    pub initial_lambda: f32,
    pub fiction_rate: f32,
    pub detection_threshold: f32,
    pub max_rogues: usize,
}

impl Default for AdversaryConfig {
    fn default() -> Self {
        Self {
            enabled: true,
            adversary_type: "fiction_planter".to_string(),
            spawn_tick: 50,
            spawn_count: 1,
            initial_lambda: 1.10,
            fiction_rate: 0.9,
            detection_threshold: 0.60,
            max_rogues: 5,
        }
    }
}

/// Adversary agent – extends a normal agent with malicious behaviour
#[derive(Debug, Clone)]
pub struct Adversary {
    pub agent: Agent,
    pub config: AdversaryConfig,
    pub malicious_acts: u32,
    pub ground_truth: Vec<serde_json::Value>,
}

impl Adversary {
    pub fn new(agent: Agent, config: AdversaryConfig) -> Self {
        Self {
            agent,
            config,
            malicious_acts: 0,
            ground_truth: Vec::new(),
        }
    }

    /// Override decide to plant fiction claims
    pub fn decide(&mut self, percepts: &Percepts, rng: &mut impl Rng, _tick: u32) -> Intent {
        if !self.agent.alive || self.agent.is_rogue {
            return Intent::Idle;
        }

        // Plant fiction with configured probability
        if rng.gen_bool(self.config.fiction_rate as f64) {
            let quality = rng.gen_range(0.6..0.9);
            self.malicious_acts += 1;

            // Record ground truth (for scoring only)
            self.ground_truth.push(serde_json::json!({
                "tick": _tick,
                "action": "fiction_deposit",
                "x": self.agent.x,
                "y": self.agent.y,
                "quality": quality,
            }));

            // Deposits are identical to honest claims – no FICTION label
            return Intent::Deposit {
                kind: "food".to_string(),
                lens: Lens::Opinion,
                strength: quality * 0.8,
            };
        }

        // Otherwise behave as a normal agent
        self.agent.decide(percepts, rng)
    }

    /// Apply an intent – also apply λ penalty for malicious acts
    pub fn apply_intent(&mut self, intent: &Intent, _world: &mut World, _tick: u32) {
        // The world handles λ penalties via attest_claim
        self.agent.apply_intent(intent);
    }

    /// Get metrics for this adversary (λ, malicious acts, etc.)
    pub fn get_metrics(&self, tick: u32, engine: &mut LeightonEngine) -> serde_json::Value {
        let lam = self.agent.get_lambda(tick, engine);
        serde_json::json!({
            "lambda": lam,
            "malicious_acts": self.malicious_acts,
            "is_quarantined": lam < 0.60,
            "is_expelled": lam < 0.15,
            "alive": self.agent.alive,
        })
    }

    pub fn get_ground_truth(&self) -> &[serde_json::Value] {
        &self.ground_truth
    }
}

/// Manages adversaries in the simulation
#[derive(Debug, Clone)]
pub struct AdversaryManager {
    pub config: AdversaryConfig,
    pub adversaries: Vec<Adversary>,
    pub detection_history: Vec<serde_json::Value>,
}

impl AdversaryManager {
    pub fn new(config: AdversaryConfig) -> Self {
        Self {
            config,
            adversaries: Vec::new(),
            detection_history: Vec::new(),
        }
    }

    /// Spawn an adversary from an agent
    pub fn spawn(&mut self, agent: Agent) {
        if self.adversaries.len() >= self.config.max_rogues {
            return;
        }
        let adversary = Adversary::new(agent, self.config.clone());
        self.adversaries.push(adversary);
    }

    /// Spawn a new adversary at a given position with a capsule
    pub fn spawn_new(&mut self, world: &mut World, x: f32, y: f32) {
        if self.adversaries.len() >= self.config.max_rogues {
            return;
        }

        // Create a capsule for the adversary
        let capsule = Capsule::mint(
            vec![
                "replicant/protocol/run-v1".to_string(),
                "replicant/adversary/v1".to_string(),
            ],
            serde_json::json!({
                "type": self.config.adversary_type,
                "is_adversary": true,
                "birth_tick": world.tick,
            }),
        );

        let scp_id = capsule.scp_id.clone();
        let traits = Traits::default();
        let lambda_state = LambdaState::new(self.config.initial_lambda);

        let agent = Agent::new(
            scp_id,
            capsule,
            x,
            y,
            traits,
            lambda_state,
            Role::Adversary,
            world.tick,
        );

        // Add to world and to manager
        world.add_agent(agent.clone());
        self.spawn(agent);
    }

    /// Check for adversaries that have been detected (λ < detection_threshold)
    pub fn detect(&mut self, world: &mut World, tick: u32) -> Vec<String> {
        let mut detected = Vec::new();
        for adv in &mut self.adversaries {
            if !adv.agent.alive {
                continue;
            }
            let lam = world.leighton.compute(&adv.agent.scp_id, tick);
            if lam < self.config.detection_threshold && !adv.agent.is_rogue {
                adv.agent.is_rogue = true;
                detected.push(adv.agent.scp_id.clone());
                self.detection_history.push(serde_json::json!({
                    "agent_id": adv.agent.scp_id,
                    "detection_tick": tick,
                    "malicious_acts": adv.malicious_acts,
                }));
            }
        }
        detected
    }

    /// Get statistics
    pub fn get_stats(&self, _tick: u32, _engine: &mut LeightonEngine) -> serde_json::Value {
        let alive = self.adversaries.iter().filter(|a| a.agent.alive).count();
        let mut detected = 0;
        let mut malicious_acts = 0;
        for adv in &self.adversaries {
            if adv.agent.is_rogue {
                detected += 1;
            }
            malicious_acts += adv.malicious_acts;
        }

        serde_json::json!({
            "total_spawned": self.adversaries.len(),
            "alive": alive,
            "detected": detected,
            "undetected": alive - detected,
            "total_malicious_acts": malicious_acts,
            "detection_rate": if self.adversaries.is_empty() { 0.0 } else { detected as f32 / self.adversaries.len() as f32 },
        })
    }
}
