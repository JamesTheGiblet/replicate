#!/usr/bin/env python3
"""
Data Cube — Immutable Fact Ledger
Append-only. Tamper-evident. Provable.
"""

import json
import os
import hashlib
import hmac
import base64
from datetime import datetime, timezone

DATACUBE_FILE = "datacube.jsonl"
SECRET_KEY = b"forge-systems-ltd-secret-key-2026"

def sign_fact(fact_entry):
    """Add HMAC signature to fact entry"""
    entry_for_sig = {k: v for k, v in fact_entry.items() if k != 'signature'}
    signature = hmac.new(SECRET_KEY, json.dumps(entry_for_sig, sort_keys=True).encode(), hashlib.sha256).digest()
    fact_entry["signature"] = base64.b64encode(signature).decode()
    return fact_entry

def insert_fact(fact, source, trust_score=0.50, metadata=None):
    """Insert a fact into the Data Cube"""
    fact_entry = {
        "id": hashlib.sha256(f"{datetime.now(timezone.utc).isoformat()}{fact}".encode()).hexdigest()[:16],
        "fact": fact,
        "source": source,
        "trust_score": trust_score,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {},
        "previous_hash": get_last_hash(),
        "hash": None,  # Will compute after entry is built
    }
    
    # Compute hash of the entry (excluding the hash field itself)
    entry_for_hash = {k: v for k, v in fact_entry.items() if k != 'hash'}
    fact_entry["hash"] = hashlib.sha256(json.dumps(entry_for_hash, sort_keys=True).encode()).hexdigest()
    
    # Sign the entry
    fact_entry = sign_fact(fact_entry)
    
    with open(DATACUBE_FILE, "a") as f:
        f.write(json.dumps(fact_entry) + "\n")
    
    return fact_entry["id"]

def get_last_hash():
    """Get the hash of the last fact in the cube"""
    if not os.path.exists(DATACUBE_FILE):
        return "0" * 64
    
    with open(DATACUBE_FILE, "r") as f:
        lines = f.readlines()
    
    if not lines:
        return "0" * 64
    
    last_entry = json.loads(lines[-1])
    return last_entry.get("hash", "0" * 64)

def query_facts(filter_func=None, limit=50):
    """Query facts from the Data Cube"""
    if not os.path.exists(DATACUBE_FILE):
        return []
    
    facts = []
    with open(DATACUBE_FILE, "r") as f:
        for line in f:
            fact = json.loads(line)
            if filter_func is None or filter_func(fact):
                facts.append(fact)
    
    return facts[-limit:]

def query_by_source(source):
    """Get all facts from a specific source"""
    return query_facts(lambda f: f.get("source") == source)

def query_by_trust_threshold(min_trust):
    """Get facts with trust score above threshold"""
    return query_facts(lambda f: f.get("trust_score", 0) >= min_trust)

def query_by_time_range(start_time, end_time):
    """Get facts within a time range"""
    def in_range(f):
        ts = f.get("timestamp", "")
        return start_time <= ts <= end_time
    return query_facts(in_range)

def verify_datacube():
    """Verify the entire Data Cube integrity"""
    if not os.path.exists(DATACUBE_FILE):
        return True, "No Data Cube found"
    
    previous_hash = "0" * 64
    with open(DATACUBE_FILE, "r") as f:
        for line_num, line in enumerate(f, 1):
            entry = json.loads(line)
            
            # Verify hash chain
            if entry.get("previous_hash") != previous_hash:
                return False, f"Chain broken at entry {line_num}"
            
            # Recompute hash
            entry_for_hash = {k: v for k, v in entry.items() if k not in ['hash', 'signature']}
            recomputed = hashlib.sha256(json.dumps(entry_for_hash, sort_keys=True).encode()).hexdigest()
            if entry.get("hash") != recomputed:
                return False, f"Hash mismatch at entry {line_num}"
            
            # Verify signature
            entry_for_sig = {k: v for k, v in entry.items() if k != 'signature'}
            expected_sig = hmac.new(SECRET_KEY, json.dumps(entry_for_sig, sort_keys=True).encode(), hashlib.sha256).digest()
            expected_b64 = base64.b64encode(expected_sig).decode()
            if entry.get("signature") != expected_b64:
                return False, f"Invalid signature at entry {line_num}"
            
            previous_hash = entry.get("hash")
    
    return True, f"Verified {line_num} entries"

def get_datacube_stats():
    """Get statistics about the Data Cube"""
    if not os.path.exists(DATACUBE_FILE):
        return {"count": 0, "sources": [], "avg_trust": 0}
    
    facts = []
    with open(DATACUBE_FILE, "r") as f:
        facts = [json.loads(line) for line in f]
    
    sources = list(set([f.get("source", "unknown") for f in facts]))
    avg_trust = sum(f.get("trust_score", 0) for f in facts) / len(facts) if facts else 0
    
    return {
        "count": len(facts),
        "sources": sources,
        "avg_trust": round(avg_trust, 2),
        "first_entry": facts[0]["timestamp"] if facts else None,
        "last_entry": facts[-1]["timestamp"] if facts else None,
    }

if __name__ == "__main__":
    print("🔷 Data Cube Test")
    
    # Insert some facts
    insert_fact("GFO runs on a Ryzen 3300U", "james@forge", 0.95)
    insert_fact("Leighton Weight tracks trust", "james@forge", 0.90)
    insert_fact("SCP is the Semantic Capsule Protocol", "james@forge", 0.85)
    
    # Query facts
    print("\n📦 All Facts:")
    for fact in query_facts(limit=10):
        print(f"   [{fact['trust_score']}] {fact['fact']} (from {fact['source']})")
    
    # Verify integrity
    valid, msg = verify_datacube()
    print(f"\n🔒 Integrity: {msg}")
    
    # Stats
    stats = get_datacube_stats()
    print(f"\n📊 Stats: {stats['count']} facts, avg trust {stats['avg_trust']}")
