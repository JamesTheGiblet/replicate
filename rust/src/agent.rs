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
            attest_cost: 0.20,
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
    pub config: AgentConfig,
    pub lambda_state: LambdaState,
    pub role: Role,
    pub alive: bool,
    /// An innate, immutable archetype defining the agent's core decision logic.
    pub archetype: Archetype,
    pub is_rogue: bool,
    pub birth_tick: u32,
    pub tasks_done: u32,
    pub can_replicate: bool,
    pub replication_cooldown: u32,
    /// Ticks remaining before this agent may switch roles again (emergent role allocation)
    pub role_cooldown: u32,
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
        archetype: Archetype,
        birth_tick: u32,
    ) -> Self {
        Self {
            scp_id,
            capsule,
            x,
            y,
            energy: 100.0,
            traits,
            config: AgentConfig::default(),
            lambda_state,
            role,
            alive: true,
            archetype,
            is_rogue: false,
            birth_tick,
            tasks_done: 0,
            can_replicate: true,
            replication_cooldown: 0,
            role_cooldown: 0,
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

        // Role-switch cooldown
        if self.role_cooldown > 0 {
            self.role_cooldown -= 1;
        }

        // 1. Attestation (scepticism) - only if energy is high
        if percepts.energy > 50.0 && !percepts.nearby_claims.is_empty() && rng.gen_bool((self.traits.scepticism * 0.4) as f64) {
            let claim = &percepts.nearby_claims[0];
            // Organic Detection: Check the environment at the agent's location. If there's
            // a resource here, the claim is likely true. This replaces the placeholder guess.
            // A more advanced agent might walk to the claim's location first.
            let resource_present = percepts.local_resource > 1.0;

            let outcome = if resource_present { "confirmed" } else { "countered" };
            return Intent::Attest {
                claim_id: claim.id.clone(),
                outcome: outcome.to_string(),
            };
        }

        // 2. Forage if energy is getting low - or migrate if the local area is depleted
        if percepts.energy < 60.0 {
            if percepts.local_resource < 5.0 {
                if let Some((dx, dy)) = percepts.migration_direction {
                    return Intent::Migrate { dx, dy };
                }
            }
            // Walk toward the nearest patch if not already close enough to harvest it
            if let Some((dx, dy, dist)) = percepts.nearest_patch_direction {
                if dist > 2.5 {
                    return Intent::Move { dx: dx * 0.8, dy: dy * 0.8 };
                }
            }
            return Intent::Forage;
        }

        // Builders terraform depleted territory into new resource patches
        if self.role == Role::Builder && self.energy >= 80.0 && percepts.local_resource < 5.0 && rng.gen_bool(0.05) {
            return Intent::Terraform;
        }

        // Scouts and Explorers search unexplored territory for unknown resource patches
        if matches!(self.role, Role::Scout | Role::Explorer) && percepts.local_resource < 1.0 && rng.gen_bool(0.05) {
            return Intent::Discover;
        }

        // Emergent role allocation: periodically re-specialize to fill whatever gap
        // the local swarm has, instead of keeping a role for life.
        // The rng.gen_bool(0.1) check is critical to prevent a "thundering herd"
        // where all agents switch roles simultaneously. This stochastic check
        // ensures only a subset of agents consider switching each tick.
        let switch_chance = if self.archetype == Archetype::Purist { 0.02 } else { 0.1 }; // Purists are 5x less likely to switch
        if self.role_cooldown == 0
            && !matches!(self.role, Role::Adversary)
            && rng.gen_bool(switch_chance)
        {
            let needed_role = match self.archetype {
                Archetype::Purist => {
                // **Specialist Logic:** Proactive, trait-based, and long-term.
                // Ignores immediate swarm needs and focuses on innate strengths.
                if self.traits.scepticism > 0.8 {
                    Some(Role::Attester)
                } else if self.traits.forage_bias > 0.8 {
                    Some(Role::Explorer)
                } else if self.traits.deposit_rate > 0.8 {
                    Some(Role::Builder)
                } else {
                    // Default to a rare, valuable role if no strong trait signal.
                    Some(Role::Observer)
                }
                }
                Archetype::Generalist | _ => { // Other archetypes default to Generalist for now
                // **Generalist Logic:** Reactive, filling immediate gaps in the swarm
                // based on global task priorities.
                let mut role_options: Vec<(f32, Role)> = Vec::new();

                // Prioritize based on global needs
                role_options.push((percepts.global_forager_need, Role::Forager));
                role_options.push((percepts.global_builder_need, Role::Builder));
                role_options.push((percepts.global_attester_need, Role::Attester));
                role_options.push((percepts.global_explorer_need, Role::Explorer));
                role_options.push((percepts.global_replicator_need, Role::Founder)); // Founder for replication

                // Add some trait-based bias for generalists too
                role_options.push((percepts.global_forager_need * self.traits.forage_bias, Role::Healer));
                role_options.push((percepts.global_explorer_need * self.traits.forage_bias, Role::Scout));
                role_options.push((percepts.global_attester_need * self.traits.scepticism, Role::Attester));

                // Filter out roles that don't make sense (e.g., Builder without enough energy)
                role_options.retain(|(_, role)| {
                    match role {
                        Role::Builder => self.energy >= 60.0,
                        Role::Founder => self.can_replicate && self.energy >= self.config.replication_threshold,
                        _ => true,
                    }
                });

                // Select the role with the highest priority
                if let Some((_priority, role)) = role_options.iter().max_by(|(p1, _), (p2, _)| p1.partial_cmp(p2).unwrap_or(std::cmp::Ordering::Equal)) {
                    Some(*role)
                } else {
                    // Fallback to local needs if no global priority is strong enough
                    let group_size = (percepts.nearby_agents.len() + 1) as f32;
                    let count_of = |target: &[Role]| {
                        percepts.nearby_agents.iter().filter(|a| target.contains(&a.role)).count()
                            + if target.contains(&self.role) { 1 } else { 0 }
                    };
                    let forager_ratio = count_of(&[Role::Forager, Role::Healer]) as f32 / group_size;
                    if forager_ratio < 0.3 { Some(Role::Forager) } else { None } // Simple local fallback
                }
                }
            };

            if let Some(role) = needed_role {
                if role != self.role {
                    self.role_cooldown = 50; // Add a cooldown to prevent rapid switching
                    return Intent::AdoptRole(role);
                }
            }
        }

        // 3. Follow strongest pheromone (Ant-inspired)
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

        // 4. Explore or exploit based on forage_bias
        if rng.gen_bool(self.traits.forage_bias as f64) {
            let dx = rng.gen_range(-1.0..1.0);
            let dy = rng.gen_range(-1.0..1.0);
            return Intent::Move { dx, dy };
        }

        // 5. Find resource and deposit
        if rng.gen_bool(0.2) {
            // The strength of the claim should be based on the actual resources found.
            // We'll use the `local_resource` percept, normalized.
            let quality = (percepts.local_resource / 50.0).clamp(0.0, 1.0);
            return Intent::Deposit {
                kind: "food".to_string(),
                lens: Lens::Opinion,
                strength: quality,
            };
        }

        // 6. Replicate (Aphid mode)
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
                self.energy -= self.config.attest_cost;
                self.tasks_done += 1;
            }
            Intent::Replicate => {
                if self.can_replicate && self.energy >= self.config.replication_threshold {
                    self.energy -= self.config.replication_cost;
                    self.can_replicate = false;
                    self.replication_cooldown = 25;
                }
            }
            Intent::Forage => {
                // Energy gain is handled by the world, but we can add a small cost for the action itself
                self.energy -= 0.02;
            }
            Intent::Recharge => {
                self.energy += self.config.recharge_rate;
                self.energy = self.energy.min(100.0);
            }
            Intent::Migrate { dx, dy } => {
                // A longer, costlier stride toward a richer, known area
                self.x += dx * 2.0;
                self.y += dy * 2.0;
                self.energy -= 0.20;
                self.energy = self.energy.max(0.0);
            }
            Intent::Discover => {
                self.energy -= 0.05;
            }
            Intent::AdoptRole(role) => {
                self.role = *role;
                self.role_cooldown = 30;
                self.energy -= 0.5;
            }
            Intent::Terraform => {
                if self.energy >= 30.0 {
                    self.energy -= 30.0;
                    self.tasks_done += 1;
                }
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
    /// Total resource energy sensed within foraging range of the agent's current position
    pub local_resource: f32,
    /// Direction toward the richest known, non-depleted patch, if the local area is scarce
    pub migration_direction: Option<(f32, f32)>,
    /// Direction and distance to the nearest non-depleted patch, for walking to food
    pub nearest_patch_direction: Option<(f32, f32, f32)>,
    /// Global need for foragers (0.0-1.0, higher means more needed)
    pub global_forager_need: f32,
    /// Global need for builders (0.0-1.0, higher means more needed)
    pub global_builder_need: f32,
    /// Global need for attesters (0.0-1.0, higher means more needed)
    pub global_attester_need: f32,
    /// Global need for explorers (0.0-1.0, higher means more needed)
    pub global_explorer_need: f32,
    /// Global need for replicators (0.0-1.0, higher means more needed)
    pub global_replicator_need: f32,
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
    pub tick: u32,
    pub attestations: usize,
    pub agent_id: String,
}
