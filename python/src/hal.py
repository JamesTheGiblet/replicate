"""HAL - Human Accountability Layer."""

# Tier definitions for Replicant
TIERS = {
    1: {"name": "Routine", "actions": ["move", "sense", "deposit_OPINION"], "lambda_required": 0.60},
    2: {"name": "Commit", "actions": ["commit_to_FACT"], "lambda_required": 0.90},
    3: {"name": "Replicate", "actions": ["replicate"], "lambda_required": 1.10},
    4: {"name": "Quarantine", "actions": ["quarantine_agent", "demolish_structure"], "lambda_required": 1.40},
    5: {"name": "Deploy", "actions": ["deploy_hardware", "exceed_population_ceiling"], "lambda_required": 1.70},
}


def can_act(lambda_value: float, tier: int) -> bool:
    """Check if an agent with given λ can perform a tier action."""
    required = TIERS.get(tier, {}).get("lambda_required", 2.00)
    return lambda_value >= required


def seal(action: str, agent_id: str, lambda_value: float, tier: int) -> dict:
    """Issue a seal (mock for beta)."""
    if not can_act(lambda_value, tier):
        return {"issued": False, "reason": f"λ={lambda_value:.2f} below tier {tier} requirement"}
    return {
        "issued": True,
        "action": action,
        "agent_id": agent_id,
        "lambda_at_time": lambda_value,
        "tier": tier,
        "separation": "none",  # Single-operator
        "seal_id": f"seal-{hash(action + agent_id + str(tier))}"
    }