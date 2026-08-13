//! World module - manages the simulation

use crate::core::*;
use crate::agent::*;
use crate::environment::*;
use std::collections::HashMap;
use serde::{Serialize, Deserialize};

/// Configuration for the world
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorldConfig {
    pub seed: u64,
    pub ticks: u32,
    #[serde(default = "default_commit_attestations")]
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

fn default_commit_attestations() -> u32 {
    2
}

/// The world - contains all agents, claims, and environment
pub struct World {
    pub tick: u32,
    pub config: WorldConfig,
    pub agents: HashMap<String, Agent>,
    pub claims: HashMap<String, Claim>,
    pub environment: Environment,
    pub leighton: LeightonEngine,
    pub ledger: Vec<serde_json::Value>,
}

impl World {
    pub fn new(config: WorldConfig) -> Self {
        let environment = Environment::new(100.0, 100.0, config.n_patches, config.seed);
        Self {
            tick: 0,
            config,
            agents: HashMap::new(),
            claims: HashMap::new(),
            environment,
            leighton: LeightonEngine::new(),
            ledger: Vec::new(),
        }
    }

    pub fn add_agent(&mut self, agent: Agent) {
        self.agents.insert(agent.scp_id.clone(), agent);
    }

    pub fn deposit_claim(&mut self, agent_id: &str, x: f32, y: f32, kind: &str, lens: Lens, strength: f32, tick: u32) -> String {
        let claim_id = format!("claim-{}", self.claims.len());
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

    pub fn tick(&mut self) {
        self.environment.update(self.agents.len() as u32);

        let mut intents = Vec::new();
        let mut rng = rand::thread_rng();

        for (agent_id, agent) in self.agents.iter_mut() {
            if !agent.alive || agent.is_rogue {
                continue;
            }

            // Sense nearby claims
            let nearby_claims: Vec<ClaimRef> = self.claims.values()
                .filter(|c| ((c.x - agent.x).powi(2) + (c.y - agent.y).powi(2)).sqrt() < 5.0)
                .map(|c| ClaimRef {
                    id: c.id.clone(),
                    x: c.x, y: c.y, lens: c.lens, kind: c.kind.clone(),
                    attestations: c.attestations.len(), agent_id: c.agent_id.clone()
                })
                .collect();

            let nearby_pheromones = Vec::new();
            let nearby_agents = Vec::new();

            let percepts = Percepts {
                nearby_pheromones,
                nearby_agents,
                nearby_claims,
                energy: agent.energy,
                lambda: agent.get_lambda(self.tick),
                can_replicate: agent.can_replicate,
            };

            let intent = agent.decide(&percepts, &mut rng);
            intents.push((agent_id.clone(), intent));
        }

        let mut pending_deposits: Vec<(String, f32, f32, String, Lens, f32)> = Vec::new();
        let mut pending_attestations: Vec<(String, String, String)> = Vec::new();

        for (agent_id, intent) in intents {
            if let Some(agent) = self.agents.get_mut(&agent_id) {
                agent.apply_intent(&intent);

                match intent {
                    Intent::Deposit { kind, lens, strength } => {
                        pending_deposits.push((
                            agent_id.clone(),
                            agent.x,
                            agent.y,
                            kind,
                            lens,
                            strength,
                        ));
                    }
                    Intent::Attest { claim_id, outcome } => {
                        pending_attestations.push((claim_id, agent_id.clone(), outcome));
                    }
                    _ => {}
                }
            }
        }

        for (agent_id, x, y, kind, lens, strength) in pending_deposits {
            self.deposit_claim(&agent_id, x, y, &kind, lens, strength, self.tick);
        }

        for (claim_id, agent_id, outcome) in pending_attestations {
            self.attest_claim(&claim_id, &agent_id, &outcome, self.tick);
        }

        let mut to_remove = Vec::new();
        for (agent_id, agent) in self.agents.iter_mut() {
            if !agent.alive {
                continue;
            }

            let lam = agent.get_lambda(self.tick);
            if lam < 0.60 {
                agent.is_rogue = true;
            } else {
                agent.is_rogue = false;
            }

            if lam < 0.15 {
                agent.alive = false;
                to_remove.push(agent_id.clone());
            }
        }

        for agent_id in to_remove {
            self.agents.remove(&agent_id);
        }

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
