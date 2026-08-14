//! World module - manages the simulation

use crate::core::*;
use crate::agent::*;
use crate::environment::*;
use rand::{rngs::StdRng, Rng};
use rand::SeedableRng;
use std::collections::HashMap;

/// Configuration for the world
#[derive(Debug, Clone)]
pub struct WorldConfig {
    pub seed: u64,
    pub ticks: u32,
    pub commit_attestations: u32,
    pub n_patches: usize,
}

impl Default for WorldConfig {
    fn default() -> Self {
        Self {
            seed: 42,
            ticks: 200,
            commit_attestations: 2,
            n_patches: 10,
        }
    }
}

/// A claim in the world
#[derive(Debug, Clone)]
pub struct Claim {
    pub id: String,
    pub x: f32,
    pub y: f32,
    pub agent_id: String,
    pub kind: String,
    pub lens: Lens,
    pub strength: f32,
    pub tick: u32,
    pub attestations: Vec<Attestation>,
    pub is_ground_truth_fiction: bool,
}

/// An attestation to a claim
#[derive(Debug, Clone)]
pub struct Attestation {
    pub agent_id: String,
    pub outcome: String,
    pub tick: u32,
}

/// The world - contains all agents, claims, and environment
pub struct World {
    pub tick: u32,
    pub config: WorldConfig,
    pub agents: HashMap<String, Agent>,
    pub claims: HashMap<String, Claim>,
    pub pheromones: Vec<Pheromone>,
    pub environment: Environment,
    pub leighton: LeightonEngine,
    pub rng: StdRng,
    pub ledger: Vec<serde_json::Value>,
    pub next_claim_id: u32,
}

impl World {
    pub fn new(config: WorldConfig) -> Self {
        let environment = Environment::new(100.0, 100.0, config.n_patches, config.seed);
        let rng = StdRng::seed_from_u64(config.seed);
        Self {
            tick: 0,
            config,
            agents: HashMap::new(),
            claims: HashMap::new(),
            pheromones: Vec::new(),
            environment,
            leighton: LeightonEngine::new(),
            rng,
            ledger: Vec::new(),
            next_claim_id: 0,
        }
    }

    pub fn add_agent(&mut self, agent: Agent) {
        let agent_id = agent.scp_id.clone();
        self.agents.insert(agent_id, agent);
    }

    pub fn deposit_claim(&mut self, agent_id: &str, x: f32, y: f32, kind: &str, lens: Lens, strength: f32, tick: u32) -> String {
        let claim_id = format!("claim-{}", self.next_claim_id);
        self.next_claim_id += 1;

        let claim = Claim {
            id: claim_id.clone(),
            x,
            y,
            agent_id: agent_id.to_string(),
            kind: kind.to_string(),
            lens,
            strength,
            tick,
            attestations: Vec::new(),
            is_ground_truth_fiction: false,
        };

        self.pheromones.push(Pheromone {
            x,
            y,
            agent_id: agent_id.to_string(),
            kind: kind.to_string(),
            lens,
            strength,
            tick,
        });

        self.claims.insert(claim_id.clone(), claim);
        claim_id
    }

    pub fn attest_claim(&mut self, claim_id: &str, agent_id: &str, outcome: &str, tick: u32) {
        let claim = match self.claims.get_mut(claim_id) {
            Some(c) => c,
            None => return,
        };

        claim.attestations.push(Attestation {
            agent_id: agent_id.to_string(),
            outcome: outcome.to_string(),
            tick,
        });

        let required = self.config.commit_attestations;
        let confirmations: Vec<_> = claim.attestations.iter()
            .filter(|a| a.outcome == "confirmed")
            .collect();
        let counters: Vec<_> = claim.attestations.iter()
            .filter(|a| a.outcome == "countered")
            .collect();

        if counters.len() >= required as usize && claim.lens == Lens::Opinion {
            claim.lens = Lens::Counter;
            self.leighton.claim_adjudicated_false(&claim.agent_id, tick);

            for a in &claim.attestations {
                if a.outcome == "confirmed" {
                    self.leighton.credulity_penalty(&a.agent_id, tick);
                }
            }

            for a in &claim.attestations {
                if a.outcome == "countered" {
                    self.leighton.counter_reward(&a.agent_id, tick);
                }
            }
        } else if confirmations.len() >= required as usize && claim.lens == Lens::Opinion {
            claim.lens = Lens::Fact;
            self.leighton.claim_verified(&claim.agent_id, tick);
        }
    }

    fn get_nearby_pheromones(&self, x: f32, y: f32, radius: f32) -> Vec<Pheromone> {
        self.pheromones
            .iter()
            .filter(|p| {
                let dx = p.x - x;
                let dy = p.y - y;
                dx * dx + dy * dy < radius * radius && p.strength > 0.01
            })
            .cloned()
            .collect()
    }

    fn get_nearby_agents(&self, self_id: &str, x: f32, y: f32, radius: f32) -> Vec<AgentRef> {
        self.agents
            .iter()
            .filter(|(id, agent)| *id != self_id && agent.alive)
            .filter(|(_, agent)| {
                let dx = agent.x - x;
                let dy = agent.y - y;
                dx * dx + dy * dy < radius * radius
            })
            .map(|(id, agent)| AgentRef {
                id: id.clone(),
                x: agent.x,
                y: agent.y,
                energy: agent.energy,
                role: agent.role,
            })
            .collect()
    }

    fn get_nearby_claims(&self, x: f32, y: f32, radius: f32) -> Vec<ClaimRef> {
        self.claims
            .iter()
            .filter(|(_, claim)| {
                let dx = claim.x - x;
                let dy = claim.y - y;
                dx * dx + dy * dy < radius * radius
            })
            .map(|(id, claim)| ClaimRef {
                id: id.clone(),
                x: claim.x,
                y: claim.y,
                lens: claim.lens,
                kind: claim.kind.clone(),
                tick: claim.tick,
                attestations: claim.attestations.len(),
                agent_id: claim.agent_id.clone(),
            })
            .collect()
    }

    fn decay_pheromones(&mut self) {
        let retention = 0.90;
        for p in &mut self.pheromones {
            p.strength *= retention;
        }
        self.pheromones.retain(|p| p.strength > 0.01);
    }

    pub fn tick(&mut self) {
        let total_agents = self.agents.len() as f32;
        let avg_energy: f32 = self.agents.values().map(|a| a.energy).sum::<f32>() / total_agents.max(1.0);
        let agents_in_threat = self.agents.values().filter(|a| a.alive && self.environment.detect_threat(a.x, a.y).0).count() as u32;

        self.environment.update(self.agents.len() as u32, avg_energy, agents_in_threat);

        // ============================================================
        // PHASE 1: Collect agent data (immutable borrow of self.agents)
        // ============================================================
        let agent_ids: Vec<String> = self.agents
            .iter()
            .filter(|(_, a)| a.alive && !a.is_rogue)
            .map(|(id, _)| id.clone())
            .collect();

        // ============================================================
        // PHASE 2: Build percepts and decide (uses immutable methods)
        // ============================================================
        let mut intents = Vec::new();

        for agent_id in &agent_ids {
            // Get agent data for creating a temporary decision-making agent
            let (x, y, energy, can_replicate, is_rogue, traits, birth_tick, role, role_cooldown, archetype, config) = {
                if let Some(agent) = self.agents.get(agent_id) {
                    (agent.x, agent.y, agent.energy, agent.can_replicate, agent.is_rogue, agent.traits.clone(), agent.birth_tick, agent.role, agent.role_cooldown, agent.archetype, agent.config.clone())
                } else {
                    continue;
                }
            };

            // Sense the environment (immutable)
            let nearby_pheromones = self.get_nearby_pheromones(x, y, 10.0);
            let nearby_agents = self.get_nearby_agents(agent_id, x, y, 10.0);
            let nearby_claims = self.get_nearby_claims(x, y, 10.0);

            let lambda = self.leighton.compute(agent_id, self.tick);

            // Calculate global task priorities for the "unified organism"
            let total_agents = self.agents.len() as f32;
            let alive_agents = self.agents.values().filter(|a| a.alive).count() as f32;
            let total_claims = self.claims.len() as f32;
            let opinion_claims = self.claims.values().filter(|c| c.lens == Lens::Opinion).count() as f32;
            let depleted_patches = self.environment.patches.iter().filter(|p| p.depleted).count() as f32;
            let total_patches = self.environment.patches.len() as f32;

            // Global Forager Need: High if average energy is low or resources are scarce
            let avg_energy: f32 = self.agents.values().map(|a| a.energy).sum::<f32>() / total_agents.max(1.0);
            let global_forager_need = (100.0 - avg_energy) / 100.0; // Inverse of average energy

            // Global Builder Need: High if many patches are depleted and population is stable
            let global_builder_need = if total_patches > 0.0 {
                depleted_patches / total_patches
            } else {
                0.0
            };

            // Global Attester Need: High if many opinion claims exist
            let global_attester_need = if total_claims > 0.0 {
                opinion_claims / total_claims
            } else {
                0.0
            };

            // Global Explorer Need: High if no new resources have been discovered recently.
            let recent_discoveries = self.environment.discovery_history.iter().filter(|&&t| self.tick - t < 500).count();
            let global_explorer_need = (1.0 - (recent_discoveries as f32 / 5.0)).clamp(0.1, 1.0);


            // Global Replicator Need: High if population is below carrying capacity
            let global_replicator_need = (self.environment.carrying_capacity as f32 - alive_agents) / self.environment.carrying_capacity as f32;
            let global_replicator_need = global_replicator_need.clamp(0.0, 1.0);


            let local_resource = self.environment.get_resource_at(x, y, 10.0);
            let migration_direction = if local_resource < 5.0 {
                self.environment.richest_patch_direction(x, y)
            } else {
                None
            };
            let nearest_patch_direction = self.environment.nearest_patch_info(x, y);

            let percepts = Percepts {
                nearby_pheromones,
                nearby_agents,
                nearby_claims,
                energy,
                lambda,
                can_replicate,
                local_resource,
                migration_direction,
                nearest_patch_direction,
                global_forager_need,
                global_builder_need,
                global_attester_need,
                global_explorer_need,
                global_replicator_need,
            };

            // Create temp agent for decision
            let mut temp_agent = Agent {
                scp_id: agent_id.clone(),
            capsule: Capsule::mint(vec![], serde_json::json!({})), // This is a dummy capsule
                x,
                y,
                energy,
                traits,
                lambda_state: LambdaState::default(),
                role,
                alive: true,
                is_rogue,
                archetype,
                birth_tick,
                tasks_done: 0,
                can_replicate,
                config,
                replication_cooldown: 0,
                role_cooldown,
                last_find_quality: 0.0,
                last_find_dir: 0.0,
            };

            let intent = temp_agent.decide(&percepts, &mut self.rng);
            intents.push((agent_id.clone(), intent));
        }

        // Tick down role-switch cooldowns on the real agents (decide() only sees a
        // disposable copy each tick, so the countdown must be persisted here).
        for agent_id in &agent_ids {
            if let Some(agent) = self.agents.get_mut(agent_id) {
                if agent.role_cooldown > 0 {
                    agent.role_cooldown -= 1;
                }
            }
        }

        // ============================================================
        // PHASE 3: Resolve intents (mutable)
        // ============================================================
        let mut deposits = Vec::new();
        let mut attestations = Vec::new();
        let mut moves = Vec::new();
        let mut replications = Vec::new();
        let mut recharges = Vec::new();
        let mut forages = Vec::new();
        let mut migrations = Vec::new();
        let mut discoveries = Vec::new();
        let mut terraforms = Vec::new();
        let mut role_changes = Vec::new();

        for (agent_id, intent) in intents {
            match intent {
                Intent::Deposit { kind, lens, strength } => {
                    if let Some(agent) = self.agents.get(&agent_id) {
                        let claim_id = self.deposit_claim(&agent_id, agent.x, agent.y, &kind, lens, strength, self.tick);
                        deposits.push((agent_id, claim_id));
                    }
                }
                Intent::Attest { claim_id, outcome } => {
                    attestations.push((agent_id, claim_id, outcome));
                }
                Intent::Move { dx, dy } => {
                    moves.push((agent_id, dx, dy));
                }
                Intent::Replicate => {
                    replications.push(agent_id);
                }
                Intent::Forage => {
                    forages.push(agent_id);
                }
                Intent::Recharge => {
                    recharges.push(agent_id);
                }
                Intent::Migrate { dx, dy } => {
                    migrations.push((agent_id, dx, dy));
                }
                Intent::Discover => {
                    discoveries.push(agent_id);
                }
                Intent::Terraform => {
                    terraforms.push(agent_id);
                }
                Intent::AdoptRole(role) => {
                    role_changes.push((agent_id, role));
                }
                Intent::Idle => {}
            }
        }

        // Apply deposits
        for (agent_id, _claim_id) in deposits {
            if let Some(agent) = self.agents.get_mut(&agent_id) {
                agent.energy -= 0.05;
                agent.tasks_done += 1;
            }
        }

        // Apply attestations
        for (agent_id, claim_id, outcome) in attestations {
            self.attest_claim(&claim_id, &agent_id, &outcome, self.tick); // This already handles penalties
        }

        // Apply forages (energy gain)
        for agent_id in &forages {
            if let Some(agent) = self.agents.get_mut(agent_id) {
                let harvested = self.environment.harvest_resource(agent.x, agent.y, 5.0);
                agent.energy += harvested;
                agent.energy = agent.energy.min(100.0);
            }
        }

        // Apply discoveries - a chance to reveal a brand new resource patch in unexplored territory
        for agent_id in &discoveries {
            if let Some(agent) = self.agents.get(agent_id) {
                let (x, y) = (agent.x, agent.y);
                self.environment.try_discover_patch(x, y, &mut self.rng);
            }
        }

        // Apply terraforming - Builders convert energy into a brand new resource patch
        for agent_id in &terraforms {
            if let Some(agent) = self.agents.get(agent_id) {
                if agent.energy >= 30.0 {
                    let (x, y) = (agent.x, agent.y);
                    self.environment.spawn_patch_near(x, y, &mut self.rng);
                }
            }
        }

        // Apply replications - actually spawn child agents (previously only deducted
        // energy without creating offspring, which drove the population extinct).
        let mut children = Vec::new();
        if (self.agents.len() as u32) < self.environment.carrying_capacity {
            for agent_id in &replications {
                if let Some(parent) = self.agents.get(agent_id) {
                    if parent.can_replicate && parent.energy >= parent.config.replication_threshold {
                        let child_traits = parent.traits.mutate(0.1);
                        let capsule = Capsule::mint(
                            vec![parent.scp_id.clone()],
                            serde_json::json!({ "parent": parent.scp_id, "birth_tick": self.tick }),
                        );
                        let mut child = Agent::new(
                            capsule.scp_id.clone(),
                            capsule,
                            (parent.x + self.rng.gen_range(-1.0..1.0)).clamp(0.0, self.environment.width),
                            (parent.y + self.rng.gen_range(-1.0..1.0)).clamp(0.0, self.environment.height),
                            child_traits,
                            LambdaState::new(1.0),
                            Role::Child,
                            // Inherit archetype, with a small chance for a generalist to produce a purist
                            if parent.archetype == Archetype::Purist {
                                Archetype::Purist
                            } else if self.rng.gen_bool(0.9) {
                                Archetype::Generalist
                            } else { Archetype::Purist },
                            self.tick,
                        );
                        child.energy = 50.0;
                        children.push(child);
                    }
                }
            }
        }
        for child in children {
            self.add_agent(child);
        }

        // Apply state changes from intents
        let all_intents: HashMap<_, _> = moves.into_iter().map(|(id, dx, dy)| (id, Intent::Move { dx, dy }))
            .chain(replications.into_iter().map(|id| (id, Intent::Replicate)))
            .chain(recharges.into_iter().map(|id| (id, Intent::Recharge)))
            .chain(forages.into_iter().map(|id| (id, Intent::Forage {})))
            .chain(migrations.into_iter().map(|(id, dx, dy)| (id, Intent::Migrate { dx, dy })))
            .chain(discoveries.into_iter().map(|id| (id, Intent::Discover)))
            .chain(terraforms.into_iter().map(|id| (id, Intent::Terraform)))
            .chain(role_changes.into_iter().map(|(id, role)| (id, Intent::AdoptRole(role))))
            .collect();

        for (agent_id, intent) in all_intents {
             if let Some(agent) = self.agents.get_mut(&agent_id) {
                agent.apply_intent(&intent);
            }
        }


        // ============================================================
        // PHASE 4: Check quarantine/expulsion
        // ============================================================
        let mut to_remove = Vec::new();
        let agent_ids: Vec<String> = self.agents.keys().cloned().collect();

        for agent_id in agent_ids {
            if let Some(agent) = self.agents.get_mut(&agent_id) {
                if !agent.alive {
                    continue;
                }

                let lam = agent.get_lambda(self.tick, &mut self.leighton);

                agent.is_rogue = lam < 0.60;

                if lam < 0.15 {
                    agent.alive = false;
                    to_remove.push(agent_id.clone());
                }

                let (threat, intensity) = self.environment.detect_threat(agent.x, agent.y);
                if threat {
                    let damage = intensity * 0.2;
                    agent.energy -= damage;
                    if agent.energy < 0.0 {
                        agent.alive = false;
                        to_remove.push(agent_id.clone());
                    }
                }

                if agent.energy < 0.0 {
                    agent.alive = false;
                    to_remove.push(agent_id.clone());
                }
            }
        }

        for agent_id in to_remove {
            self.agents.remove(&agent_id);
        }

        // ============================================================
        // PHASE 5: Decay and sweep
        // ============================================================
        self.decay_pheromones();
        self.leighton.sweep(self.tick);
        self.tick += 1;
    }

    pub fn run(&mut self) {
        for _ in 0..self.config.ticks {
            self.tick();
        }
    }

    pub fn get_health_report(&self) -> String {
        self.environment.get_health_report()
    }

    pub fn get_stats(&self) -> serde_json::Value {
        let alive = self.agents.values().filter(|a| a.alive).count();
        let claims = self.claims.len();
        let counters = self.claims.iter().filter(|(_, c)| c.lens == Lens::Counter).count();
        let health = self.environment.metrics.overall_health;

        serde_json::json!({
            "tick": self.tick,
            "alive": alive,
            "total_agents": self.agents.len(),
            "claims": claims,
            "counters": counters,
            "health": health,
        })
    }
}
