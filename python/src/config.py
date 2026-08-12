"""
Shared configuration loader for Replicant.
Ensures all scripts run with the same parameters.
"""

def get_default_config() -> dict:
    """Returns the default simulation configuration."""
    return {
        "run": {"seed": 42, "ticks": 200},
        "leighton": {"k_per_day_forage": 0.05, "k_per_day_signal": 0.02},
        "claims": {"food": {"retention_per_tick": 0.90, "commit_attestations": 2}},
        "environment": {"n_patches": 10}
    }