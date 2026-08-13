//! World module - manages the simulation

use crate::core::*;
use crate::agent::*;
use crate::environment::*;
use rand::rngs::StdRng;
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
        self.environment.update(self.agents.len() as u32);

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
            // Get agent data
            let (x, y, energy, can_replicate, is_rogue, traits, birth_tick) = {
                if let Some(agent) = self.agents.get(agent_id) {
                    (agent.x, agent.y, agent.energy, agent.can_replicate, agent.is_rogue, agent.traits.clone(), agent.birth_tick)
                } else {
                    continue;
                }
            };

            // Sense the environment (immutable)
            let nearby_pheromones = self.get_nearby_pheromones(x, y, 10.0);
            let nearby_agents = self.get_nearby_agents(agent_id, x, y, 10.0);
            let nearby_claims = self.get_nearby_claims(x, y, 10.0);

            let lambda = self.leighton.compute(agent_id, self.tick);

            let percepts = Percepts {
                nearby_pheromones,
                nearby_agents,
                nearby_claims,
                energy,
                lambda,
                can_replicate,
            };

            // Create temp agent for decision
            let mut temp_agent = Agent {
                scp_id: agent_id.clone(),
                capsule: Capsule::mint(vec![], serde_json::json!({})),
                x,
                y,
                energy,
                traits,
                lambda_state: LambdaState::default(),
                role: Role::Forager,
                alive: true,
                is_rogue,
                birth_tick,
                tasks_done: 0,
                can_replicate,
                replication_cooldown: 0,
                last_find_quality: 0.0,
                last_find_dir: 0.0,
            };

            let intent = temp_agent.decide(&percepts, &mut self.rng);
            intents.push((agent_id.clone(), intent));
        }

        // ============================================================
        // PHASE 3: Resolve intents (mutable)
        // ============================================================
        let mut deposits = Vec::new();
        let mut attestations = Vec::new();
        let mut moves = Vec::new();
        let mut replications = Vec::new();
        let mut recharges = Vec::new();

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
                Intent::Recharge => {
                    recharges.push(agent_id);
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
            self.attest_claim(&claim_id, &agent_id, &outcome, self.tick);
            if let Some(agent) = self.agents.get_mut(&agent_id) {
                agent.energy -= 0.50;
                agent.tasks_done += 1;
            }
        }

        // Apply moves
        for (agent_id, dx, dy) in moves {
            if let Some(agent) = self.agents.get_mut(&agent_id) {
                agent.x += dx;
                agent.y += dy;
                agent.energy -= 0.10;
                agent.energy = agent.energy.max(0.0);
            }
        }

        // Apply replications
        for agent_id in replications {
            if let Some(agent) = self.agents.get_mut(&agent_id) {
                if agent.can_replicate && agent.energy >= 70.0 {
                    agent.energy -= 40.0;
                    agent.can_replicate = false;
                    agent.replication_cooldown = 25;
                }
            }
        }

        // Apply recharges
        for agent_id in recharges {
            if let Some(agent) = self.agents.get_mut(&agent_id) {
                agent.energy += 0.5;
                agent.energy = agent.energy.min(100.0);
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
