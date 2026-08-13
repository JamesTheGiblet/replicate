//! Founders module - creates the initial set of agents

use crate::core::*;
use crate::agent::*;
use std::collections::HashMap;

pub fn create_founders() -> HashMap<String, Agent> {
    let mut founders = HashMap::new();

    let sagan_capsule = Capsule::mint(
        vec!["replicant/protocol/run-v1".to_string()],
        serde_json::json!({"name": "Sagan"})
    );
    let sagan = Agent::new(
        sagan_capsule.scp_id.clone(),
        sagan_capsule,
        50.0, 50.0,
        Traits { forage_bias: 0.6, deposit_rate: 0.7, scepticism: 0.4, broadcast_cost: 0.6 },
        LambdaState::new(1.2),
        Role::Founder,
        0,
    );
    founders.insert("Sagan".to_string(), sagan);

    let dyson_capsule = Capsule::mint(vec![], serde_json::json!({"name": "Dyson"}));
    let dyson = Agent::new(
        dyson_capsule.scp_id.clone(),
        dyson_capsule,
        45.0, 55.0,
        Traits { forage_bias: 0.8, deposit_rate: 0.3, scepticism: 0.6, broadcast_cost: 0.4 },
        LambdaState::new(1.0),
        Role::Scout,
        0,
    );
    founders.insert("Dyson".to_string(), dyson);

    let lovelace_capsule = Capsule::mint(vec![], serde_json::json!({"name": "Lovelace"}));
    let lovelace = Agent::new(
        lovelace_capsule.scp_id.clone(),
        lovelace_capsule,
        55.0, 45.0,
        Traits { forage_bias: 0.4, deposit_rate: 0.8, scepticism: 0.5, broadcast_cost: 0.7 },
        LambdaState::new(0.9),
        Role::Builder,
        0,
    );
    founders.insert("Lovelace".to_string(), lovelace);

    let turing_capsule = Capsule::mint(vec![], serde_json::json!({"name": "Turing"}));
    let turing = Agent::new(
        turing_capsule.scp_id.clone(),
        turing_capsule,
        52.0, 52.0,
        Traits { forage_bias: 0.3, deposit_rate: 0.2, scepticism: 0.9, broadcast_cost: 0.3 },
        LambdaState::new(1.1),
        Role::Attester,
        0,
    );
    founders.insert("Turing".to_string(), turing);

    let curie_capsule = Capsule::mint(vec![], serde_json::json!({"name": "Curie"}));
    let curie = Agent::new(
        curie_capsule.scp_id.clone(),
        curie_capsule,
        48.0, 48.0,
        Traits { forage_bias: 0.9, deposit_rate: 0.6, scepticism: 0.3, broadcast_cost: 0.2 },
        LambdaState::new(0.8),
        Role::Forager,
        0,
    );
    founders.insert("Curie".to_string(), curie);

    let newton_capsule = Capsule::mint(vec![], serde_json::json!({"name": "Newton"}));
    let newton = Agent::new(newton_capsule.scp_id.clone(), newton_capsule, 60.0, 60.0, Traits::default(), LambdaState::default(), Role::Broadcaster, 0);
    founders.insert("Newton".to_string(), newton);

    let tesla_capsule = Capsule::mint(vec![], serde_json::json!({"name": "Tesla"}));
    let tesla = Agent::new(tesla_capsule.scp_id.clone(), tesla_capsule, 40.0, 40.0, Traits::default(), LambdaState::default(), Role::Explorer, 0);
    founders.insert("Tesla".to_string(), tesla);

    let pasteur_capsule = Capsule::mint(vec![], serde_json::json!({"name": "Pasteur"}));
    let pasteur = Agent::new(pasteur_capsule.scp_id.clone(), pasteur_capsule, 35.0, 65.0, Traits::default(), LambdaState::default(), Role::Healer, 0);
    founders.insert("Pasteur".to_string(), pasteur);

    let shannon_capsule = Capsule::mint(vec![], serde_json::json!({"name": "Shannon"}));
    let shannon = Agent::new(shannon_capsule.scp_id.clone(), shannon_capsule, 65.0, 35.0, Traits::default(), LambdaState::default(), Role::Signal, 0);
    founders.insert("Shannon".to_string(), shannon);

    let darwin_capsule = Capsule::mint(vec![], serde_json::json!({"name": "Darwin"}));
    let darwin = Agent::new(darwin_capsule.scp_id.clone(), darwin_capsule, 50.0, 50.0, Traits::default(), LambdaState::default(), Role::Observer, 0);
    founders.insert("Darwin".to_string(), darwin);

    founders
}