//! Integration tests for Replicant

#[cfg(test)]
mod integration_tests {
    use replicant::*;

    #[test]
    fn test_world_creation() {
        let config = WorldConfig::default();
        let world = World::new(config);
        assert_eq!(world.tick, 0);
        assert!(world.agents.is_empty());
        assert!(world.claims.is_empty());
    }

    #[test]
    fn test_agent_creation() {
        let capsule = Capsule::mint(
            vec!["test/protocol/v1".to_string()],
            serde_json::json!({"name": "TestAgent"})
        );
        
        let agent = Agent::new(
            capsule.scp_id.clone(),
            capsule,
            50.0,
            50.0,
            Traits::default(),
            LambdaState::default(),
            Role::Founder,
            0,
        );
        
        assert_eq!(agent.x, 50.0);
        assert_eq!(agent.y, 50.0);
        assert!(agent.alive);
        assert!(!agent.is_rogue);
    }

    #[test]
    fn test_claim_deposit_and_attest() {
        let config = WorldConfig::default();
        let mut world = World::new(config);
        
        let claim_id = world.deposit_claim(
            "test_agent",
            50.0,
            50.0,
            "food",
            Lens::Opinion,
            0.5,
            0,
        );
        
        assert_eq!(world.claims.len(), 1);
        
        world.attest_claim(&claim_id, "attester1", "confirmed", 10);
        world.attest_claim(&claim_id, "attester2", "confirmed", 20);
        
        let claim = world.claims.get(&claim_id).unwrap();
        assert_eq!(claim.lens, Lens::Fact);
        assert_eq!(claim.attestations.len(), 2);
    }

    #[test]
    fn test_adversary_creation() {
        let config = AdversaryConfig::default();
        let manager = AdversaryManager::new(config);
        
        assert_eq!(manager.adversaries.len(), 0);
        assert!(manager.detection_history.is_empty());
    }

    #[test]
    fn test_environment_creation() {
        let env = Environment::new(100.0, 100.0, 10, 42);
        assert_eq!(env.patches.len(), 10);
        assert!(env.threats.is_empty());
        assert!(env.metrics.overall_health > 0.0);
    }

    #[test]
    fn test_lambda_recidivism() {
        let mut engine = LeightonEngine::new();
        let agent_id = "test_agent";
        
        // First offence
        engine.claim_adjudicated_false(agent_id, 10);
        let lam1 = engine.compute(agent_id, 10);
        assert!((lam1 - 0.80).abs() < 0.01);
        
        // Second offence (escalated)
        engine.claim_adjudicated_false(agent_id, 20);
        let lam2 = engine.compute(agent_id, 20);
        assert!(lam2 < 0.50);
        
        // Third offence
        engine.claim_adjudicated_false(agent_id, 30);
        let lam3 = engine.compute(agent_id, 30);
        assert!(lam3 < 0.10);
    }
}
