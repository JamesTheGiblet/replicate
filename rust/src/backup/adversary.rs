//! Adversary module - tests swarm resilience

use crate::core::*;
use crate::agent::*;

/// Adversary configuration
#[derive(Debug, Clone)]
pub struct AdversaryConfig {
    pub enabled: bool,
    pub adversary_type: String,
    pub spawn_tick: u32,
    pub spawn_count: u32,
    pub fiction_rate: f32,
}

impl Default for AdversaryConfig {
    fn default() -> Self {
        Self {
            enabled: true,
            adversary_type: "fiction_planter".to_string(),
            spawn_tick: 50,
            spawn_count: 1,
            fiction_rate: 0.9,
        }
    }
}

/// Adversary agent - malicious actor that tests swarm resilience
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

    pub fn decide(&mut self, percepts: &Percepts, rng: &mut impl rand::Rng) -> Intent {
        if !self.agent.alive || self.agent.is_rogue {
            return Intent::Idle;
        }

        // Plant fiction
        if rng.gen_bool(self.config.fiction_rate as f64) {
            let quality = rng.gen_range(0.6..0.9);
            self.malicious_acts += 1;
            
            // Record ground truth
            self.ground_truth.push(serde_json::json!({
                "tick": 0,
                "action": "fiction_deposit",
                "x": self.agent.x,
                "y": self.agent.y,
                "quality": quality
            }));

            return Intent::Deposit {
                kind: "food".to_string(),
                lens: Lens::Opinion,
                strength: quality * 0.8,
            };
        }

        // Normal behaviour
        self.agent.decide(percepts, rng)
    }

    pub fn get_ground_truth(&self) -> &[serde_json::Value] {
        &self.ground_truth
    }

    pub fn get_metrics(&self, current_tick: u32) -> serde_json::Value {
        let lam = self.agent.get_lambda(current_tick);
        serde_json::json!({
            "lambda": lam,
            "malicious_acts": self.malicious_acts,
            "is_quarantined": lam < 0.60,
            "is_expelled": lam < 0.15,
            "alive": self.agent.alive,
        })
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

    pub fn spawn(&mut self, agent: Agent) {
        if self.adversaries.len() >= 5 {
            return;
        }
        let adversary = Adversary::new(agent, self.config.clone());
        self.adversaries.push(adversary);
    }

    pub fn get_stats(&self, current_tick: u32) -> serde_json::Value {
        let alive = self.adversaries.iter().filter(|a| a.agent.alive).count();
        let mut detected = 0;
        let mut malicious_acts = 0;

        for adv in &self.adversaries {
            let metrics = adv.get_metrics(current_tick);
            if metrics["is_quarantined"].as_bool().unwrap_or(false) {
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
            "detection_rate": if !self.adversaries.is_empty() {
                detected as f32 / self.adversaries.len() as f32
            } else { 0.0 },
        })
    }
}
