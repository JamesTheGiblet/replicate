#!/usr/bin/env python3
"""
Leighton Weight — Universal Trust Coefficient
Range: 0.00 (Quarantine) to 2.00 (Reflex)
"""

import json
import os
import hashlib
from datetime import datetime, timezone

WEIGHT_FILE = "leighton_weight.jsonl"
DEFAULT_WEIGHT = 0.50
REFLEX_THRESHOLD = 1.80
QUARANTINE_THRESHOLD = 0.60

# Outcome multipliers
OUTCOME_MULTIPLIERS = {
    "success": 0.05,      # +0.05 on success
    "failure": -0.10,     # -0.10 on failure
    "exceptional": 0.10,  # +0.10 for exceptional success
    "critical_failure": -0.20,  # -0.20 for critical failure
}

def get_leighton_weight(scp_id):
    """Get current Leighton Weight for an SCP"""
    if not os.path.exists(WEIGHT_FILE):
        return DEFAULT_WEIGHT
    
    with open(WEIGHT_FILE, 'r') as f:
        lines = f.readlines()
    
    # Find most recent entry for this SCP
    for line in reversed(lines):
        entry = json.loads(line)
        if entry.get('scp_id') == scp_id:
            return entry.get('weight', DEFAULT_WEIGHT)
    
    return DEFAULT_WEIGHT

def update_leighton_weight(scp_id, outcome, metadata=None):
    """Update Leighton Weight based on outcome"""
    current = get_leighton_weight(scp_id)
    multiplier = OUTCOME_MULTIPLIERS.get(outcome, 0.0)
    
    new_weight = current + multiplier
    
    # Clamp to range 0.00 - 2.00
    new_weight = max(0.00, min(2.00, new_weight))
    
    # Determine state
    if new_weight >= REFLEX_THRESHOLD:
        state = "REFLEX"
    elif new_weight >= 1.40:
        state = "PROMOTABLE"
    elif new_weight >= 1.00:
        state = "STABLE"
    elif new_weight >= QUARANTINE_THRESHOLD:
        state = "DEGRADED"
    else:
        state = "QUARANTINE"
    
    entry = {
        "scp_id": scp_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "previous_weight": current,
        "outcome": outcome,
        "delta": multiplier,
        "new_weight": new_weight,
        "state": state,
        "metadata": metadata or {},
        "hash": hashlib.sha256(f"{scp_id}{timestamp}{new_weight}".encode()).hexdigest()
    }
    
    with open(WEIGHT_FILE, 'a') as f:
        f.write(json.dumps(entry) + "\n")
    
    return new_weight, state

def should_execute(scp_id, required_weight=QUARANTINE_THRESHOLD):
    """Check if SCP should execute based on Leighton Weight"""
    weight = get_leighton_weight(scp_id)
    return weight >= required_weight

def get_leighton_history(scp_id, limit=20):
    """Get weight history for an SCP"""
    if not os.path.exists(WEIGHT_FILE):
        return []
    
    history = []
    with open(WEIGHT_FILE, 'r') as f:
        for line in f:
            entry = json.loads(line)
            if entry.get('scp_id') == scp_id:
                history.append(entry)
    
    return history[-limit:]

def get_all_weights():
    """Get current weight for all tracked SCPs"""
    if not os.path.exists(WEIGHT_FILE):
        return {}
    
    weights = {}
    with open(WEIGHT_FILE, 'r') as f:
        for line in f:
            entry = json.loads(line)
            scp_id = entry.get('scp_id')
            if scp_id:
                weights[scp_id] = entry.get('new_weight', DEFAULT_WEIGHT)
    
    return weights

if __name__ == "__main__":
    # Test the system
    print("🔷 Leighton Weight Test")
    print(f"   Default weight: {DEFAULT_WEIGHT}")
    print(f"   Reflex threshold: {REFLEX_THRESHOLD}")
    print(f"   Quarantine threshold: {QUARANTINE_THRESHOLD}")
    
    # Simulate some updates
    update_leighton_weight("test_scp", "success")
    update_leighton_weight("test_scp", "success")
    update_leighton_weight("test_scp", "exceptional")
    update_leighton_weight("test_scp", "failure")
    
    final_weight = get_leighton_weight("test_scp")
    should_run = should_execute("test_scp")
    
    print(f"\n📊 Test SCP final weight: {final_weight}")
    print(f"   Should execute: {should_run}")
    
    print("\n📜 History:")
    for entry in get_leighton_history("test_scp"):
        print(f"   {entry['timestamp'][:19]} — {entry['outcome']}: {entry['previous_weight']:.2f} → {entry['new_weight']:.2f} ({entry['state']})")
