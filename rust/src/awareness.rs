//! Computational Self-Awareness Module
//!
//! Implements bounded self-modeling and self-modification for agents.
//! Safety constraints override all adaptive decisions.

use crate::core::*;
use crate::agent::*;
use serde::{Deserialize, Serialize};
use std::collections::VecDeque;

// ============================================================
// Data Models
// ============================================================

/// Self-state of an agent – tracks internal metrics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SelfState {
    pub confidence: f32,        // 0.0 – 1.0
    pub recent_reward: f32,     // weighted average of recent rewards
    pub anomaly_rate: f32,      // fraction of unusual observations
    pub safety_strikes: u32,    // cumulative safety violations
    pub mode: Mode,             // Normal, Cautious, Recovery
    pub last_update_tick: u32,
}

impl Default for SelfState {
    fn default() -> Self {
        Self {
            confidence: 0.5,
            recent_reward: 0.0,
            anomaly_rate: 0.0,
            safety_strikes: 0,
            mode: Mode::Normal,
            last_update_tick: 0,
        }
    }
}

/// Agent mode – determines adaptation aggressiveness
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Mode {
    Normal,
    Cautious,
    Recovery,
}

/// Policy genome – the set of parameters an agent can adapt
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicyGenome {
    pub version: u64,
    pub parent_version: Option<u64>,
    pub parameters: Vec<f32>,   // fixed order, per-index bounds
    pub validated: bool,
}

impl Default for PolicyGenome {
    fn default() -> Self {
        Self {
            version: 0,
            parent_version: None,
            parameters: vec![0.5, 0.5, 0.5, 0.5], // forage_bias, deposit_rate, scepticism, broadcast_cost
            validated: false,
        }
    }
}

/// Checkpoint – snapshot of a policy version with fitness
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Checkpoint {
    pub policy_version: u64,
    pub fitness_summary: f32,
    pub timestamp_tick: u32,
    pub rollback_reason: Option<String>,
}

// ============================================================
// Fitness Evaluator
// ============================================================

pub struct FitnessEvaluator {
    pub success_weight: f32,
    pub efficiency_weight: f32,
    pub stability_penalty: f32,
    pub safety_penalty: f32,
    pub window_size: usize,
    pub history: VecDeque<f32>,
}

impl Default for FitnessEvaluator {
    fn default() -> Self {
        Self {
            success_weight: 0.4,
            efficiency_weight: 0.3,
            stability_penalty: 0.2,
            safety_penalty: 0.1,
            window_size: 100,
            history: VecDeque::with_capacity(100),
        }
    }
}

impl FitnessEvaluator {
    pub fn new() -> Self {
        Self::default()
    }

    /// Compute fitness score from agent metrics
    pub fn evaluate(&mut self, state: &SelfState, agent: &Agent) -> f32 {
        // Reward: task success (e.g., claims deposited, tasks done)
        let success_score = (agent.tasks_done as f32 / 100.0).min(1.0);

        // Efficiency: energy management
        let efficiency_score = (agent.energy / 100.0).min(1.0);

        // Stability: variance in recent reward
        let stability_score = 1.0 - state.anomaly_rate.min(0.5);

        // Safety: strikes penalise heavily
        let safety_score = (1.0 - (state.safety_strikes as f32 / 10.0).min(1.0)).max(0.0);

        let fitness = self.success_weight * success_score
            + self.efficiency_weight * efficiency_score
            + self.stability_penalty * stability_score
            + self.safety_penalty * safety_score;

        // Clamp and record history
        let fitness = fitness.clamp(0.0, 1.0);
        self.history.push_back(fitness);
        if self.history.len() > self.window_size {
            self.history.pop_front();
        }

        fitness
    }

    /// Get recent fitness average
    pub fn recent_average(&self) -> f32 {
        if self.history.is_empty() {
            return 0.0;
        }
        self.history.iter().sum::<f32>() / self.history.len() as f32
    }

    /// Check if improvement threshold (10%) is met
    pub fn improvement_met(&self, baseline: f32) -> bool {
        let current = self.recent_average();
        current > baseline * 1.10
    }
}

// ============================================================
// Adaptation Engine
// ============================================================

pub struct AdaptationEngine {
    pub max_change_per_step: f32,
    pub min_clamp: f32,
    pub max_clamp: f32,
    pub adaptation_frequency_ticks: u32,
    pub last_adaptation_tick: u32,
    pub mutation_rate: f32,
}

impl Default for AdaptationEngine {
    fn default() -> Self {
        Self {
            max_change_per_step: 0.05,
            min_clamp: 0.0,
            max_clamp: 1.0,
            adaptation_frequency_ticks: 100,
            last_adaptation_tick: 0,
            mutation_rate: 0.1,
        }
    }
}

impl AdaptationEngine {
    pub fn new() -> Self {
        Self::default()
    }

    /// Mutate a policy genome with bounded changes
    pub fn mutate(&self, genome: &PolicyGenome, rng: &mut impl rand::Rng) -> PolicyGenome {
        let mut new_params = genome.parameters.clone();
        let sigma = self.mutation_rate;

        for param in &mut new_params {
            let delta = rng.gen_range(-sigma..sigma);
            *param = (*param + delta).clamp(self.min_clamp, self.max_clamp);
        }

        PolicyGenome {
            version: genome.version + 1,
            parent_version: Some(genome.version),
            parameters: new_params,
            validated: false,
        }
    }

    /// Apply a genome to an agent's traits
    pub fn apply_genome(&self, agent: &mut Agent, genome: &PolicyGenome) {
        if genome.parameters.len() >= 4 {
            agent.traits.forage_bias = genome.parameters[0].clamp(self.min_clamp, self.max_clamp);
            agent.traits.deposit_rate = genome.parameters[1].clamp(self.min_clamp, self.max_clamp);
            agent.traits.scepticism = genome.parameters[2].clamp(self.min_clamp, self.max_clamp);
            agent.traits.broadcast_cost = genome.parameters[3].clamp(self.min_clamp, self.max_clamp);
        }
    }

    /// Extract a genome from an agent's traits
    pub fn extract_genome(&self, agent: &Agent) -> PolicyGenome {
        PolicyGenome {
            version: 0,
            parent_version: None,
            parameters: vec![
                agent.traits.forage_bias,
                agent.traits.deposit_rate,
                agent.traits.scepticism,
                agent.traits.broadcast_cost,
            ],
            validated: true,
        }
    }
}

// ============================================================
// Policy Manager (Champion/Challenger)
// ============================================================

pub struct PolicyManager {
    pub champion: PolicyGenome,
    pub challenger: Option<PolicyGenome>,
    pub baseline_fitness: f32,
    pub current_fitness: f32,
    pub improvement_threshold: f32, // 10% default
    pub evaluation_window: usize,
    pub fitness_history: VecDeque<f32>,
}

impl Default for PolicyManager {
    fn default() -> Self {
        Self {
            champion: PolicyGenome::default(),
            challenger: None,
            baseline_fitness: 0.0,
            current_fitness: 0.0,
            improvement_threshold: 0.10,
            evaluation_window: 100,
            fitness_history: VecDeque::new(),
        }
    }
}

impl PolicyManager {
    pub fn new(initial_genome: PolicyGenome) -> Self {
        Self {
            champion: initial_genome,
            challenger: None,
            baseline_fitness: 0.0,
            current_fitness: 0.0,
            improvement_threshold: 0.10,
            evaluation_window: 100,
            fitness_history: VecDeque::new(),
        }
    }

    /// Evaluate and decide whether to promote challenger
    pub fn update(&mut self, fitness: f32) -> bool {
        self.fitness_history.push_back(fitness);
        if self.fitness_history.len() > self.evaluation_window {
            self.fitness_history.pop_front();
        }

        let avg_fitness = if self.fitness_history.is_empty() {
            fitness
        } else {
            self.fitness_history.iter().sum::<f32>() / self.fitness_history.len() as f32
        };

        self.current_fitness = avg_fitness;

        if self.baseline_fitness == 0.0 {
            self.baseline_fitness = avg_fitness;
            return false;
        }

        // If challenger exists, check if it's better
        if let Some(ref challenger) = self.challenger {
            // Check improvement threshold
            if avg_fitness > self.baseline_fitness * (1.0 + self.improvement_threshold) {
                // Promote challenger
                self.champion = challenger.clone();
                self.baseline_fitness = avg_fitness;
                self.challenger = None;
                return true; // Promotion occurred
            }
        }

        false
    }

    /// Accept a new challenger
    pub fn propose_challenger(&mut self, challenger: PolicyGenome) {
        self.challenger = Some(challenger);
    }
}

// ============================================================
// Safety Supervisor
// ============================================================

pub struct SafetySupervisor {
    pub max_safety_strikes: u32,
    pub freeze_after_strikes: u32,
    pub rollback_on_failure: bool,
    pub freeze_active: bool,
}

impl Default for SafetySupervisor {
    fn default() -> Self {
        Self {
            max_safety_strikes: 5,
            freeze_after_strikes: 3,
            rollback_on_failure: true,
            freeze_active: false,
        }
    }
}

impl SafetySupervisor {
    pub fn new() -> Self {
        Self::default()
    }

    /// Check a safety condition; increment strikes if violated
    pub fn inspect(&mut self, condition: bool, state: &mut SelfState) -> bool {
        if !condition {
            state.safety_strikes += 1;
            if state.safety_strikes >= self.freeze_after_strikes {
                self.freeze_active = true;
                state.mode = Mode::Cautious;
            }
            if state.safety_strikes >= self.max_safety_strikes {
                state.mode = Mode::Recovery;
            }
            return false;
        }
        true
    }

    /// Roll back to a previous checkpoint
    pub fn rollback(&mut self, checkpoint: &Checkpoint, agent: &mut Agent, engine: &mut AdaptationEngine) {
        if !self.rollback_on_failure {
            return;
        }

        // Revert traits to checkpoint values (simplified: we reset to defaults)
        agent.traits = Traits::default();
        engine.last_adaptation_tick = checkpoint.timestamp_tick;

        // Reset safety strikes
        agent.lambda_state = LambdaState::default();

        // Unfreeze if conditions allow
        self.freeze_active = false;
    }

    /// Check if adaptation is allowed
    pub fn can_adapt(&self) -> bool {
        !self.freeze_active
    }
}

// ============================================================
// SelfAwareAgent - Wraps an agent with self-awareness
// ============================================================

pub struct SelfAwareAgent {
    pub agent: Agent,
    pub self_state: SelfState,
    pub genome: PolicyGenome,
    pub fitness_evaluator: FitnessEvaluator,
    pub adaptation_engine: AdaptationEngine,
    pub policy_manager: PolicyManager,
    pub safety_supervisor: SafetySupervisor,
    pub checkpoints: Vec<Checkpoint>,
}

impl SelfAwareAgent {
    pub fn new(agent: Agent) -> Self {
        let genome = PolicyGenome::default();
        Self {
            agent,
            self_state: SelfState::default(),
            genome: genome.clone(),
            fitness_evaluator: FitnessEvaluator::new(),
            adaptation_engine: AdaptationEngine::new(),
            policy_manager: PolicyManager::new(genome),
            safety_supervisor: SafetySupervisor::new(),
            checkpoints: Vec::new(),
        }
    }

    /// Update self-state based on recent behaviour
    pub fn update_self_state(&mut self, tick: u32) {
        // Update confidence based on recent fitness
        let fitness = self.fitness_evaluator.recent_average();
        self.self_state.confidence = (self.self_state.confidence * 0.9 + fitness * 0.1).clamp(0.0, 1.0);

        // Update anomaly rate (simplified)
        self.self_state.anomaly_rate = (self.self_state.anomaly_rate * 0.95 + 0.01).clamp(0.0, 0.5);

        // Update mode based on safety strikes
        if self.self_state.safety_strikes >= 5 {
            self.self_state.mode = Mode::Recovery;
        } else if self.self_state.safety_strikes >= 3 {
            self.self_state.mode = Mode::Cautious;
        } else {
            self.self_state.mode = Mode::Normal;
        }

        self.self_state.last_update_tick = tick;
    }

    /// Check for adaptation opportunity
    pub fn adapt(&mut self, tick: u32, rng: &mut impl rand::Rng) -> bool {
        // Check adaptation frequency
        if tick - self.adaptation_engine.last_adaptation_tick < self.adaptation_engine.adaptation_frequency_ticks {
            return false;
        }

        // Check safety
        if !self.safety_supervisor.can_adapt() {
            return false;
        }

        // Evaluate current fitness
        let fitness = self.fitness_evaluator.evaluate(&self.self_state, &self.agent);

        // Update policy manager
        let promoted = self.policy_manager.update(fitness);

        if promoted {
            // Apply champion genome
            self.adaptation_engine.apply_genome(&mut self.agent, &self.policy_manager.champion);
            self.genome = self.policy_manager.champion.clone();

            // Create checkpoint
            let checkpoint = Checkpoint {
                policy_version: self.genome.version,
                fitness_summary: fitness,
                timestamp_tick: tick,
                rollback_reason: None,
            };
            self.checkpoints.push(checkpoint);

            self.adaptation_engine.last_adaptation_tick = tick;
            return true;
        }

        // If no champion, propose a challenger
        if self.policy_manager.challenger.is_none() {
            let challenger = self.adaptation_engine.mutate(&self.genome, rng);
            self.policy_manager.propose_challenger(challenger);
        }

        self.adaptation_engine.last_adaptation_tick = tick;
        false
    }

    /// Safety check – inspect a condition and react
    pub fn safety_check(&mut self, condition: bool) -> bool {
        let passed = self.safety_supervisor.inspect(condition, &mut self.self_state);
        if !passed && self.safety_supervisor.rollback_on_failure {
            // Attempt rollback to last checkpoint
            if let Some(last_checkpoint) = self.checkpoints.last() {
                self.safety_supervisor.rollback(
                    last_checkpoint,
                    &mut self.agent,
                    &mut self.adaptation_engine,
                );
            }
        }
        passed
    }

    /// Get metrics for telemetry
    pub fn get_metrics(&self) -> serde_json::Value {
        serde_json::json!({
            "confidence": self.self_state.confidence,
            "fitness": self.fitness_evaluator.recent_average(),
            "mode": format!("{:?}", self.self_state.mode),
            "safety_strikes": self.self_state.safety_strikes,
            "version": self.genome.version,
            "checkpoints": self.checkpoints.len(),
            "parameters": self.genome.parameters,
        })
    }
}
