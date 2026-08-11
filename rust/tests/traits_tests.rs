//! Traits tests

#[cfg(test)]
mod traits_tests {
    use replicant::core::Traits;

    #[test]
    fn test_traits_default() {
        let traits = Traits::default();
        assert!((traits.forage_bias - 0.5).abs() < 0.001);
        assert!((traits.deposit_rate - 0.5).abs() < 0.001);
        assert!((traits.scepticism - 0.5).abs() < 0.001);
        assert!((traits.broadcast_cost - 0.5).abs() < 0.001);
    }

    #[test]
    fn test_traits_mutation() {
        let traits = Traits::default();
        let mutated = traits.mutate(0.1);
        
        // Should be within bounds
        assert!(mutated.forage_bias >= 0.0 && mutated.forage_bias <= 1.0);
        assert!(mutated.deposit_rate >= 0.0 && mutated.deposit_rate <= 1.0);
        assert!(mutated.scepticism >= 0.0 && mutated.scepticism <= 1.0);
        assert!(mutated.broadcast_cost >= 0.0 && mutated.broadcast_cost <= 1.0);
        
        // Should be different (probabilistic)
        // We can't guarantee, but with sigma=0.1 it's very likely
        let mut differs = 0;
        if (mutated.forage_bias - traits.forage_bias).abs() > 0.01 { differs += 1; }
        if (mutated.deposit_rate - traits.deposit_rate).abs() > 0.01 { differs += 1; }
        if (mutated.scepticism - traits.scepticism).abs() > 0.01 { differs += 1; }
        if (mutated.broadcast_cost - traits.broadcast_cost).abs() > 0.01 { differs += 1; }
        assert!(differs > 0, "At least one trait should mutate");
    }

    #[test]
    fn test_traits_mutation_bounds() {
        let mut traits = Traits {
            forage_bias: 0.0,
            deposit_rate: 0.0,
            scepticism: 0.0,
            broadcast_cost: 0.0,
        };
        let mutated = traits.mutate(0.5);
        assert!(mutated.forage_bias >= 0.0);
        assert!(mutated.deposit_rate >= 0.0);
        assert!(mutated.scepticism >= 0.0);
        assert!(mutated.broadcast_cost >= 0.0);
        
        traits = Traits {
            forage_bias: 1.0,
            deposit_rate: 1.0,
            scepticism: 1.0,
            broadcast_cost: 1.0,
        };
        let mutated = traits.mutate(0.5);
        assert!(mutated.forage_bias <= 1.0);
        assert!(mutated.deposit_rate <= 1.0);
        assert!(mutated.scepticism <= 1.0);
        assert!(mutated.broadcast_cost <= 1.0);
    }
}
