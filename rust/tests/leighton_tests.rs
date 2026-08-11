//! Leighton Weight Engine tests

#[cfg(test)]
mod leighton_tests {
    use replicant::core::LeightonEngine;

    #[test]
    fn test_default_lambda() {
        let mut engine = LeightonEngine::new();
        let lam = engine.compute("unknown_agent", 0);
        assert!((lam - 1.0).abs() < 0.001);
    }

    #[test]
    fn test_claim_verified() {
        let mut engine = LeightonEngine::new();
        let agent_id = "test_agent";
        
        engine.claim_verified(agent_id, 10);
        let lam = engine.compute(agent_id, 10);
        assert!(lam > 1.0);
        // λ = 1.0 + 0.05 = 1.05 (at tick 10, no decay yet)
        assert!((lam - 1.05).abs() < 0.001);
    }

    #[test]
    fn test_claim_adjudicated_false() {
        let mut engine = LeightonEngine::new();
        let agent_id = "test_agent";
        
        engine.claim_adjudicated_false(agent_id, 10);
        let lam = engine.compute(agent_id, 10);
        assert!(lam < 1.0);
        // λ = 1.0 - 0.20 = 0.80 (at tick 10, no decay yet)
        assert!((lam - 0.80).abs() < 0.001);
    }

    #[test]
    fn test_recidivism_escalation() {
        let mut engine = LeightonEngine::new();
        let agent_id = "test_agent";
        
        // First offence: -0.20 at tick 10
        engine.claim_adjudicated_false(agent_id, 10);
        let lam1 = engine.compute(agent_id, 10);
        assert!((lam1 - 0.80).abs() < 0.001);
        
        // Second offence: -0.40 at tick 20
        engine.claim_adjudicated_false(agent_id, 20);
        let lam2 = engine.compute(agent_id, 20);
        // λ = 1.0 - 0.20*exp(-0.005*10) - 0.40 = 1.0 - 0.190 - 0.40 = 0.410
        assert!((lam2 - 0.410).abs() < 0.01);
        
        // Third offence: -0.60 at tick 30
        engine.claim_adjudicated_false(agent_id, 30);
        let lam3 = engine.compute(agent_id, 30);
        // λ = 1.0 - 0.20*exp(-0.005*20) - 0.40*exp(-0.005*10) - 0.60
        //   = 1.0 - 0.181 - 0.380 - 0.60 = -0.161 → clamped to 0.0
        assert!(lam3 < 0.10);
        
        // Check offences tracking
        let state = engine.get_state(agent_id);
        assert_eq!(state.offences.get("claim_false"), Some(&3));
    }

    #[test]
    fn test_counter_reward() {
        let mut engine = LeightonEngine::new();
        let agent_id = "test_agent";
        
        engine.counter_reward(agent_id, 10);
        let lam = engine.compute(agent_id, 10);
        // λ = 1.0 + 0.03 = 1.03
        assert!((lam - 1.03).abs() < 0.001);
    }

    #[test]
    fn test_credulity_penalty() {
        let mut engine = LeightonEngine::new();
        let agent_id = "test_agent";
        
        engine.credulity_penalty(agent_id, 10);
        let lam = engine.compute(agent_id, 10);
        // λ = 1.0 - 0.05 = 0.95
        assert!((lam - 0.95).abs() < 0.001);
    }

    #[test]
    fn test_attack_detected() {
        let mut engine = LeightonEngine::new();
        let agent_id = "test_agent";
        
        engine.attack_detected(agent_id, 10);
        let lam = engine.compute(agent_id, 10);
        // λ = 1.0 - 0.30 = 0.70
        assert!((lam - 0.70).abs() < 0.001);
    }

    #[test]
    fn test_multiple_events() {
        let mut engine = LeightonEngine::new();
        let agent_id = "test_agent";
        
        // Sequence: verified → false → counter → credulity
        engine.claim_verified(agent_id, 5);
        engine.claim_adjudicated_false(agent_id, 10);
        engine.counter_reward(agent_id, 15);
        engine.credulity_penalty(agent_id, 20);
        
        let lam = engine.compute(agent_id, 20);
        // Expected: 1.0 + 0.05*exp(-0.02*15) - 0.20*exp(-0.005*10) + 0.03 - 0.05
        // Approx: 1.0 + 0.037 - 0.190 + 0.03 - 0.05 = 0.827
        assert!(lam > 0.80);
        assert!(lam < 0.85);
    }
}
