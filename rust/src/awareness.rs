//! Computational Self-Awareness module

use serde::{Serialize, Deserialize};

/// The mode of the agent's self-awareness engine.
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
pub enum AwarenessMode {
    Normal,
    Cautious,
    Recovery,
}

/// The agent's internal model of its own state and performance.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SelfState {
    pub confidence: f32,
    pub recent_reward: f32,
    pub anomaly_rate: f32,
    pub safety_strikes: u32,
    pub mode: AwarenessMode,
}

impl Default for SelfState {
    fn default() -> Self {
        Self {
            confidence: 1.0,
            recent_reward: 0.0,
            anomaly_rate: 0.0,
            safety_strikes: 0,
            mode: AwarenessMode::Normal,
        }
    }
}

/// A versioned set of policy parameters for an agent.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicyGenome {
    pub version: u64,
    pub parent_version: Option<u64>,
    pub parameters: Vec<f32>, // Corresponds to agent's `Traits`
    pub validated: bool,
}

/// A snapshot of an agent's state for potential rollback.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Checkpoint {
    pub policy_version: u64,
    pub fitness_summary: f32,
    pub timestamp_tick: u32,
    pub rollback_reason: Option<String>,
}