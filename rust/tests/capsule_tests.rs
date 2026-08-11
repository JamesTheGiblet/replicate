//! Capsule tests

#[cfg(test)]
mod capsule_tests {
    use replicant::core::Capsule;

    #[test]
    fn test_capsule_mint() {
        let capsule = Capsule::mint(
            vec!["replicant/protocol/run-v1".to_string()],
            serde_json::json!({"test": "value"})
        );
        
        assert!(capsule.scp_id.starts_with("replicant/agent/"));
        assert_eq!(capsule.inherits.len(), 1);
        assert_eq!(capsule.inherits[0], "replicant/protocol/run-v1");
        assert_eq!(capsule.licence, "MSL-1.0");
    }

    #[test]
    fn test_capsule_inherits() {
        let parent = Capsule::mint(
            vec!["replicant/protocol/run-v1".to_string()],
            serde_json::json!({"name": "Parent"})
        );
        
        let child = Capsule::mint(
            vec![parent.scp_id.clone(), "replicant/protocol/run-v1".to_string()],
            serde_json::json!({"name": "Child"})
        );
        
        assert_eq!(child.inherits[0], parent.scp_id);
    }
}
