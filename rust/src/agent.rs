//! Agent module - individual swarm agents

use crate::core::*;
use rand::Rng;

/// Agent configuration
#[derive(Debug, Clone)]
pub struct AgentConfig {
    pub initial_energy: f32,
    pub move_cost: f32,
    pub deposit_cost: f32,
    pub attest_cost: f32,
    pub recharge_rate: f32,
    pub replication_threshold: f32,
    pub replication_cost: f32,
}

impl Default for AgentConfig {
    fn default() -> Self {
        Self {
            initial_energy: 100.0,
            move_cost: 0.10,
            deposit_cost: 0.05,
            attest_cost: 0.50,
            recharge_rate: 0.5,
            replication_threshold: 70.0,
            replication_cost: 40.0,
        }
    }
}

/// A single agent in the swarm
#[derive(Debug, Clone)]
pub struct Agent {
    pub scp_id: String,
    pub capsule: Capsule,
    pub x: f32,
    pub y: f32,
    pub energy: f32,
    pub traits: Traits,
    pub lambda_state: LambdaState,
    pub role: Role,
    pub alive: bool,
    pub is_rogue: bool,
    pub birth_tick: u32,
    pub tasks_done: u32,
    pub can_replicate: bool,
    pub replication_cooldown: u32,
    pub last_find_quality: f32,
    pub last_find_dir: f32,
}

impl Agent {
    pub fn new(
        scp_id: String,
        capsule: Capsule,
        x: f32,
        y: f32,
        traits: Traits,
        lambda_state: LambdaState,
        role: Role,
        birth_tick: u32,
    ) -> Self {
        Self {
            scp_id,
            capsule,
            x,
            y,
            energy: 100.0,
            traits,
            lambda_state,
            role,
            alive: true,
            is_rogue: false,
            birth_tick,
            tasks_done: 0,
            can_replicate: true,
            replication_cooldown: 0,
            last_find_quality: 0.0,
            last_find_dir: 0.0,
        }
    }

    /// Get lambda from the engine
    pub fn get_lambda(&self, current_tick: u32, engine: &mut LeightonEngine) -> f32 {
        engine.compute(&self.scp_id, current_tick)
    }

    /// Sense the environment
    pub fn sense(&self, percepts: &Percepts) -> Percepts {
        percepts.clone()
    }

    /// Decide what to do - full logic
    pub fn decide(&mut self, percepts: &Percepts, rng: &mut impl Rng) -> Intent {
        if !self.alive || self.is_rogue {
            return Intent::Idle;
        }

        // Replication cooldown
        if self.replication_cooldown > 0 {
            self.replication_cooldown -= 1;
            if self.replication_cooldown == 0 {
                self.can_replicate = true;
            }
        }

        // 1. Attestation (scepticism) - check claims first
        if !percepts.nearby_claims.is_empty() && rng.gen_bool((self.traits.scepticism * 0.4) as f64) {
            let claim = &percepts.nearby_claims[0];
            // Check if resource exists (simplified for now)
            let resource_present = rng.gen_bool(0.7);
            let outcome = if resource_present { "confirmed" } else { "countered" };
            return Intent::Attest {
                claim_id: claim.id.clone(),
                outcome: outcome.to_string(),
            };
        }

        // 2. Follow strongest pheromone (Ant-inspired)
        if !percepts.nearby_pheromones.is_empty() {
            let strongest = percepts
                .nearby_pheromones
                .iter()
                .max_by(|a, b| a.strength.partial_cmp(&b.strength).unwrap());
            if let Some(p) = strongest {
                let angle = (p.y - self.y).atan2(p.x - self.x);
                return Intent::Move {
                    dx: angle.cos() * 0.5,
                    dy: angle.sin() * 0.5,
                };
            }
        }

        // 3. Explore or exploit based on forage_bias
        if rng.gen_bool(self.traits.forage_bias as f64) {
            let dx = rng.gen_range(-1.0..1.0);
            let dy = rng.gen_range(-1.0..1.0);
            return Intent::Move { dx, dy };
        }

        // 4. Find resource and deposit
        if rng.gen_bool(0.2) {
            let quality: f32 = rng.gen();
            return Intent::Deposit {
                kind: "food".to_string(),
                lens: Lens::Opinion,
                strength: quality * 0.5,
            };
        }

        // 5. Replicate (Aphid mode)
        if self.can_replicate && self.energy >= 70.0 && percepts.lambda >= 1.10 {
            return Intent::Replicate;
        }

        // 6. Recharge
        if self.energy < 25.0 {
            return Intent::Recharge;
        }

        Intent::Idle
    }

    /// Apply an intent (mutates agent state)
    pub fn apply_intent(&mut self, intent: &Intent) {
        match intent {
            Intent::Move { dx, dy } => {
                self.x += dx;
                self.y += dy;
                self.energy -= 0.10;
                self.energy = self.energy.max(0.0);
            }
            Intent::Deposit { .. } => {
                self.energy -= 0.05;
                self.tasks_done += 1;
            }
            Intent::Attest { .. } => {
                self.energy -= 0.50;
                self.tasks_done += 1;
            }
            Intent::Replicate => {
                if self.can_replicate && self.energy >= 70.0 {
                    self.energy -= 40.0;
                    self.can_replicate = false;
                    self.replication_cooldown = 25;
                }
            }
            Intent::Recharge => {
                self.energy += 0.5;
                self.energy = self.energy.min(100.0);
            }
            Intent::Idle => {}
        }
    }

    /// Mutate traits (Aphid-inspired)
    pub fn mutate_traits(&self, sigma: f32) -> Traits {
        self.traits.mutate(sigma)
    }
}

/// Percepts - what an agent senses
#[derive(Debug, Clone)]
pub struct Percepts {
    pub nearby_pheromones: Vec<Pheromone>,
    pub nearby_agents: Vec<AgentRef>,
    pub nearby_claims: Vec<ClaimRef>,
    pub energy: f32,
    pub lambda: f32,
    pub can_replicate: bool,
}

/// Pheromone trail
#[derive(Debug, Clone)]
pub struct Pheromone {
    pub x: f32,
    pub y: f32,
    pub agent_id: String,
    pub kind: String,
    pub lens: Lens,
    pub strength: f32,
    pub tick: u32,
}

/// Agent reference (for sense)
#[derive(Debug, Clone)]
pub struct AgentRef {
    pub id: String,
    pub x: f32,
    pub y: f32,
    pub energy: f32,
    pub role: Role,
}

/// Claim reference (for sense)
#[derive(Debug, Clone)]
pub struct ClaimRef {
    pub id: String,
    pub x: f32,
    pub y: f32,
    pub lens: Lens,
    pub kind: String,
    pub attestations: usize,
    pub agent_id: String,
}
