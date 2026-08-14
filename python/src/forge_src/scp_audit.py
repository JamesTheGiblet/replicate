#!/usr/bin/env python3
"""
SCP Audit Module — Governance, Auditability, Provenance, Leighton Weight
"""

import json
import hashlib
import time
import os
import hmac
import base64
from datetime import datetime, timezone
from leighton_weight import get_leighton_weight, update_leighton_weight, should_execute

AUDIT_LOG = "audit_log.jsonl"
SECRET_KEY = b"forge-systems-ltd-secret-key-2026"

# --- Governance Rules ---
RULES = {
    "max_actions_per_scp": 10,
    "min_trust_score": 0.60,
    "allowed_primitives": ["sys.log", "file.write", "cognition.remember", "echo"],
    "require_provenance": True,
    "use_leighton_weight": True,
}

def sign_entry(entry):
    signature = hmac.new(SECRET_KEY, json.dumps(entry, sort_keys=True).encode(), hashlib.sha256).digest()
    entry["signature"] = base64.b64encode(signature).decode()
    return entry

def audit_log(event_type, data):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "data": data,
        "hash": hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    }
    entry = sign_entry(entry)
    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry["hash"]

def check_governance(scp_data):
    violations = []
    trust = scp_data.get("trust_score", 0.0)
    if trust < RULES["min_trust_score"]:
        violations.append(f"Trust score {trust} below minimum {RULES['min_trust_score']}")
    
    actions = scp_data.get("actions", [])
    if len(actions) > RULES["max_actions_per_scp"]:
        violations.append(f"Too many actions: {len(actions)} > {RULES['max_actions_per_scp']}")
    
    for action in actions:
        prim = action.get("primitive")
        if prim not in RULES["allowed_primitives"]:
            violations.append(f"Primitive '{prim}' not allowed")
    
    if RULES["require_provenance"] and "provenance" not in scp_data:
        violations.append("Missing provenance block")
    
    return violations

def check_leighton_weight_gate(scp_data):
    scp_id = scp_data.get("id", "unknown")
    weight = get_leighton_weight(scp_id)
    if weight < 0.60:
        return False, weight
    return True, weight

def execute_with_governance(scp_data):
    violations = check_governance(scp_data)
    if violations:
        audit_log("GOVERNANCE_DENIED", {"violations": violations, "scp": scp_data})
        return {"status": "denied", "violations": violations}
    
    lw_ok, lw_weight = check_leighton_weight_gate(scp_data)
    if not lw_ok:
        audit_log("LEIGHTON_QUARANTINE", {"scp_id": scp_data.get("id", "unknown"), "weight": lw_weight})
        return {"status": "quarantined", "leighton_weight": lw_weight}
    
    execution_id = audit_log("EXECUTION_START", {
        "scp_id": scp_data.get("id", "unknown"),
        "trust": scp_data.get("trust_score"),
        "leighton_weight": lw_weight,
        "created_by": "james@forge",
    })
    
    results = []
    outcome = "success"
    for action in scp_data.get("actions", []):
        prim = action.get("primitive")
        inp = action.get("input", {})
        results.append({"primitive": prim, "result": "simulated_ok"})
    
    audit_log("EXECUTION_END", {"execution_id": execution_id, "results": results})
    
    # Update Leighton Weight based on outcome
    new_weight, state = update_leighton_weight(scp_data.get("id", "unknown"), outcome)
    audit_log("LEIGHTON_UPDATE", {"scp_id": scp_data.get("id"), "old_weight": lw_weight, "new_weight": new_weight, "state": state})
    
    return {"status": "executed", "execution_id": execution_id, "results": results, "leighton_weight": new_weight}

def view_audit_log(limit=10):
    if not os.path.exists(AUDIT_LOG):
        return []
    with open(AUDIT_LOG, 'r') as f:
        lines = f.readlines()
    entries = [json.loads(line) for line in lines[-limit:]]
    return entries

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scp_audit.py <file.scp.json>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        scp = json.load(f)
    
    result = execute_with_governance(scp)
    print(json.dumps(result, indent=2))
    print("\n📋 Recent Audit Log:")
    for entry in view_audit_log(5):
        print(f"  {entry['timestamp']} — {entry['event_type']}")

# --- Data Cube Integration ---
from datacube import insert_fact, query_facts, verify_datacube

def prim_datacube_insert(input_data):
    """Primitive: Insert a fact into the Data Cube"""
    fact = input_data.get("fact")
    source = input_data.get("source", "scp")
    trust = input_data.get("trust", 0.50)
    fact_id = insert_fact(fact, source, trust, input_data.get("metadata"))
    return {"status": "ok", "fact_id": fact_id}

def prim_datacube_query(input_data):
    """Primitive: Query facts from the Data Cube"""
    min_trust = input_data.get("min_trust", 0.0)
    source = input_data.get("source")
    limit = input_data.get("limit", 20)
    
    facts = query_facts(limit=limit)
    if source:
        facts = [f for f in facts if f.get("source") == source]
    if min_trust:
        facts = [f for f in facts if f.get("trust_score", 0) >= min_trust]
    
    return {"status": "ok", "facts": facts, "count": len(facts)}

# Add to RULES["allowed_primitives"]
# "datacube.insert", "datacube.query"
