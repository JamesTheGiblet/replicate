//! Core types and utilities

mod leighton;
pub use leighton::*;

/// Semantic Capsule Primitive - atomic unit of identity
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct Capsule {
    pub scp_id: String,
    pub inherits: Vec<String>,
    pub declaration: serde_json::Value,
    pub licence: String,
    pub signature: Option<Signature>,
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct Signature {
    pub key_id: String,
    pub algorithm: String,
    pub value: String,
}

impl Capsule {
    pub fn mint(inherits: Vec<String>, declaration: serde_json::Value) -> Self {
        Self {
            scp_id: format!("replicant/agent/{}", uuid::Uuid::new_v4()),
            inherits,
            declaration,
            licence: "MSL-1.0".to_string(),
            signature: None,
        }
    }
}

/// Agent traits - genetic traits that mutate
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
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
        use rand::Rng;
        let mut rng = rand::thread_rng();
        Self {
            forage_bias: (self.forage_bias + rng.gen_range(-sigma..sigma)).clamp(0.0, 1.0),
            deposit_rate: (self.deposit_rate + rng.gen_range(-sigma..sigma)).clamp(0.0, 1.0),
            scepticism: (self.scepticism + rng.gen_range(-sigma..sigma)).clamp(0.0, 1.0),
            broadcast_cost: (self.broadcast_cost + rng.gen_range(-sigma..sigma)).clamp(0.0, 1.0),
        }
    }
}

/// Agent role
#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
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

/// Lens classification for claims
#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub enum Lens {
    Opinion,
    Fact,
    Counter,
    Fiction,
    Context,
    Unknown,
}

impl Lens {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Opinion => "OPINION",
            Self::Fact => "FACT",
            Self::Counter => "COUNTER",
            Self::Fiction => "FICTION",
            Self::Context => "CONTEXT",
            Self::Unknown => "UNKNOWN",
        }
    }
}

/// Agent intent - what an agent decides to do
#[derive(Debug, Clone)]
pub enum Intent {
    Move { dx: f32, dy: f32 },
    Deposit { kind: String, lens: Lens, strength: f32 },
    Attest { claim_id: String, outcome: String },
    Replicate,
    Recharge,
    Idle,
}

/// LambdaEvent - append-only reputation event
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct LambdaEvent {
    pub tick: u32,
    pub delta: f32,
    pub k: f32,
    pub reason: String,
}

/// LambdaState - event-ledger reputation
#[derive(Debug, Clone)]
pub struct LambdaState {
    pub base: f32,
    pub events: Vec<LambdaEvent>,
    pub offences: std::collections::HashMap<String, u32>,
}

impl Default for LambdaState {
    fn default() -> Self {
        Self {
            base: 1.0,
            events: Vec::new(),
            offences: std::collections::HashMap::new(),
        }
    }
}

impl LambdaState {
    pub fn new(base: f32) -> Self {
        Self {
            base,
            events: Vec::new(),
            offences: std::collections::HashMap::new(),
        }
    }

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

    pub fn add_event(&mut self, tick: u32, delta: f32, k: f32, reason: String) {
        self.events.push(LambdaEvent { tick, delta, k, reason });
    }

    pub fn compact(&mut self, current_tick: u32, threshold: f32) {
        self.events.retain(|e| {
            let dt = (current_tick as f32 - e.tick as f32).max(0.0);
            e.delta.abs() * (-e.k * dt).exp() > threshold
        });
    }

    pub fn event_count(&self) -> usize {
        self.events.len()
    }
}
