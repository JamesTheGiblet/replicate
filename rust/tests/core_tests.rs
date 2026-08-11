//! Core module tests

#[cfg(test)]
mod core_tests {
    use replicant::core::*;

    #[test]
    fn test_lambda_state_default() {
        let state = LambdaState::default();
        assert_eq!(state.base, 1.0);
        assert_eq!(state.event_count(), 0);
        assert_eq!(state.compute(0), 1.0);
    }

    #[test]
    fn test_lambda_state_new() {
        let state = LambdaState::new(1.5);
        assert_eq!(state.base, 1.5);
        assert_eq!(state.event_count(), 0);
    }

    #[test]
    fn test_lambda_event_addition() {
        let mut state = LambdaState::new(1.0);
        state.add_event(0, -0.20, 0.005, "test".to_string());
        assert_eq!(state.event_count(), 1);
        
        // At tick 0, λ = 1.0 - 0.20 = 0.80
        let lam = state.compute(0);
        assert!((lam - 0.80).abs() < 0.001);
    }

    #[test]
    fn test_lambda_decay() {
        let mut state = LambdaState::new(1.5);
        state.add_event(0, -0.50, 0.05, "test".to_string());
        
        // At t=0: λ = 1.5 - 0.5 = 1.0
        let lam0 = state.compute(0);
        assert!((lam0 - 1.0).abs() < 0.001);
        
        // At t=100: should decay toward base (1.5)
        let lam100 = state.compute(100);
        assert!(lam100 > 1.0);
        assert!(lam100 < 1.5);
    }

    #[test]
    fn test_lambda_clamping() {
        let mut state = LambdaState::new(1.0);
        
        // Test floor
        state.add_event(0, -2.0, 0.01, "test".to_string());
        let lam = state.compute(0);
        assert_eq!(lam, 0.0);
    }

    #[test]
    fn test_lambda_ceiling() {
        let mut state = LambdaState::new(1.0);
        state.add_event(0, 2.0, 0.01, "test".to_string());
        let lam = state.compute(0);
        assert_eq!(lam, 2.0);
    }

    #[test]
    fn test_lambda_compact() {
        let mut state = LambdaState::new(1.0);
        
        // Add many events
        for i in 0..50 {
            state.add_event(i, 0.01, 0.1, "test".to_string());
        }
        
        assert_eq!(state.event_count(), 50);
        state.compact(100, 1e-3);
        // Some events should be compacted
        assert!(state.event_count() < 50);
    }
}
