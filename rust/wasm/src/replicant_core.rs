//! Replicant core for WASM - simplified version

use serde::Serialize;
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize)]
pub struct Capsule {
    pub scp_id: String,
    pub inherits: Vec<String>,
    pub declaration: serde_json::Value,
    pub licence: String,
}

impl Capsule {
    pub fn mint(inherits: Vec<String>, declaration: serde_json::Value) -> Self {
        let scp_id = format!("replicant/agent/{}", uuid::Uuid::new_v4());
        Self {
            scp_id,
            inherits,
            declaration,
            licence: "MSL-1.0".to_string(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub enum Role {
    Founder,
    Scout,
    Builder,
    Attester,
    Forager,
    Broadcaster,
    Explorer,
    Healer,
    Signal,
    Observer,
    Child,
    Adversary,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub enum Lens {
    Opinion,
    Fact,
    Counter,
    Fiction,
    Context,
    Unknown,
}

#[derive(Debug, Clone, Serialize)]
pub struct Traits {
    pub forage_bias: f32,
    pub deposit_rate: f32,
    pub scepticism: f32,
    pub broadcast_cost: f32,
}

impl Default for Traits {
    fn default() -> Self {
        Self {
            forage_bias: 0.5,
            deposit_rate: 0.5,
            scepticism: 0.5,
            broadcast_cost: 0.5,
        }
    }
}

impl Traits {
    pub fn mutate(&self, sigma: f32) -> Self {
        let mut rng = rand::rng();
        Self {
            forage_bias: (self.forage_bias + rng.random_range(-sigma..sigma)).clamp(0.0, 1.0),
            deposit_rate: (self.deposit_rate + rng.random_range(-sigma..sigma)).clamp(0.0, 1.0),
            scepticism: (self.scepticism + rng.random_range(-sigma..sigma)).clamp(0.0, 1.0),
            broadcast_cost: (self.broadcast_cost + rng.random_range(-sigma..sigma)).clamp(0.0, 1.0),
        }
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct LambdaEvent {
    pub tick: u32,
    pub delta: f32,
    pub k: f32,
    pub reason: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct LambdaState {
    pub base: f32,
    pub events: Vec<LambdaEvent>,
    pub offences: HashMap<String, u32>,
}

impl Default for LambdaState {
    fn default() -> Self {
        Self {
            base: 1.0,
            events: Vec::new(),
            offences: HashMap::new(),
        }
    }
}

impl LambdaState {
    pub fn compute(&self, current_tick: u32) -> f32 {
        let mut total = self.base;
        for event in &self.events {
            let dt = current_tick as f32 - event.tick as f32;
            if dt < 0.0 {
                continue;
            }
            total += event.delta * (-event.k * dt).exp();
        }
        total.clamp(0.0, 2.0)
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct LeightonEngine {
    states: HashMap<String, LambdaState>,
}

impl LeightonEngine {
    pub fn new() -> Self {
        Self {
            states: HashMap::new(),
        }
    }
    
    pub fn compute(&mut self, agent_id: &str, current_tick: u32) -> f32 {
        let state = self.states.entry(agent_id.to_string()).or_insert_with(LambdaState::default);
        state.compute(current_tick)
    }
    
    pub fn claim_adjudicated_false(&mut self, agent_id: &str, tick: u32) {
        let state = self.states.entry(agent_id.to_string()).or_insert_with(LambdaState::default);
        state.events.push(LambdaEvent {
            tick,
            delta: -0.20,
            k: 0.005,
            reason: "claim_false".to_string(),
        });
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct Agent {
    pub scp_id: String,
    pub x: f32,
    pub y: f32,
    pub energy: f32,
    pub traits: Traits,
    pub lambda_state: LambdaState,
    pub role: Role,
    pub alive: bool,
    pub is_rogue: bool,
}

impl Agent {
    pub fn new(scp_id: String, x: f32, y: f32, traits: Traits, role: Role) -> Self {
        Self {
            scp_id,
            x,
            y,
            energy: 100.0,
            traits,
            lambda_state: LambdaState::default(),
            role,
            alive: true,
            is_rogue: false,
        }
    }
    
    pub fn get_lambda(&self, current_tick: u32, engine: &mut LeightonEngine) -> f32 {
        engine.compute(&self.scp_id, current_tick)
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct ResourcePatch {
    pub x: f32,
    pub y: f32,
    pub energy: f32,
    pub max_energy: f32,
    pub depleted: bool,
}

#[derive(Debug, Clone, Serialize)]
pub struct ThreatZone {
    pub x: f32,
    pub y: f32,
    pub radius: f32,
    pub intensity: f32,
    pub active: bool,
}

#[derive(Debug, Clone, Serialize)]
pub struct EnvironmentMetrics {
    pub overall_health: f32,
}

impl Default for EnvironmentMetrics {
    fn default() -> Self {
        Self { overall_health: 0.5 }
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct Environment {
    pub patches: Vec<ResourcePatch>,
    pub threats: Vec<ThreatZone>,
    pub metrics: EnvironmentMetrics,
}

impl Environment {
    pub fn new(n_patches: usize) -> Self {
        let mut rng = rand::rng();
        let mut patches = Vec::new();
        for _ in 0..n_patches {
            patches.push(ResourcePatch {
                x: rng.random_range(10.0..90.0),
                y: rng.random_range(10.0..90.0),
                energy: rng.random_range(50.0..100.0),
                max_energy: 100.0,
                depleted: false,
            });
        }
        Self {
            patches,
            threats: Vec::new(),
            metrics: EnvironmentMetrics::default(),
        }
    }
    
    pub fn season_factor(&self) -> f32 {
        1.0
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct Claim {
    pub id: String,
    pub x: f32,
    pub y: f32,
    pub agent_id: String,
    pub lens: Lens,
    pub attestations: Vec<Attestation>,
}

#[derive(Debug, Clone, Serialize)]
pub struct Attestation {
    pub agent_id: String,
    pub outcome: String,
    pub tick: u32,
}

#[derive(Debug, Clone, Serialize)]
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
            ticks: 1000,
            commit_attestations: 2,
            n_patches: 10,
        }
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct World {
    pub tick: u32,
    pub agents: HashMap<String, Agent>,
    pub claims: HashMap<String, Claim>,
    pub environment: Environment,
    pub leighton: LeightonEngine,
}

impl World {
    pub fn new(config: WorldConfig) -> Self {
        Self {
            tick: 0,
            agents: HashMap::new(),
            claims: HashMap::new(),
            environment: Environment::new(config.n_patches),
            leighton: LeightonEngine::new(),
        }
    }
    
    pub fn tick(&mut self) {
        self.tick += 1;
        
        // Simple agent movement for demo
        // Agents move randomly and occasionally deposit claims
        let mut rng = rand::rng();
        let agent_ids: Vec<String> = self.agents.keys().cloned().collect();
        
        for id in agent_ids {
            if let Some(agent) = self.agents.get_mut(&id) {
                if !agent.alive {
                    continue;
                }
                
                // Move randomly
                let dx = rng.random_range(-1.0..1.0);
                let dy = rng.random_range(-1.0..1.0);
                agent.x = (agent.x + dx).clamp(0.0, 100.0);
                agent.y = (agent.y + dy).clamp(0.0, 100.0);
                
                // Occasionally deposit a claim
                if rng.random_bool(0.05) {
                    let claim_id = format!("claim-{}", self.claims.len());
                    self.claims.insert(claim_id.clone(), Claim {
                        id: claim_id,
                        x: agent.x,
                        y: agent.y,
                        agent_id: id.clone(),
                        lens: Lens::Opinion,
                        attestations: Vec::new(),
                    });
                }
                
                // Recharge
                agent.energy = (agent.energy + 0.1).min(100.0);
            }
        }
    }
}

pub fn create_founders() -> Vec<(String, Agent)> {
    let names = vec!["Sagan", "Dyson", "Lovelace", "Turing", "Curie", "Newton", "Tesla", "Pasteur", "Shannon", "Darwin"];
    let roles = vec![
        Role::Founder, Role::Scout, Role::Builder, Role::Attester, Role::Forager,
        Role::Broadcaster, Role::Explorer, Role::Healer, Role::Signal, Role::Observer,
    ];
    
    let mut rng = rand::rng();
    let mut founders = Vec::new();
    
    for (i, name) in names.iter().enumerate() {
        let scp_id = format!("replicant/agent/{}", name);
        let x = rng.random_range(20.0..80.0);
        let y = rng.random_range(20.0..80.0);
        let traits = Traits::default();
        let agent = Agent::new(scp_id, x, y, traits, roles[i].clone());
        founders.push((name.to_string(), agent));
    }
    
    founders
}
