#!/usr/bin/env python3
"""Verify audit log integrity"""

import json
import hashlib
import hmac
import base64

AUDIT_LOG = "audit_log.jsonl"
SECRET_KEY = b"forge-systems-ltd-secret-key-2026"  # Must match scp_audit.py

def verify_chain():
    valid_count = 0
    legacy_count = 0
    tampered = False
    
    if not os.path.exists(AUDIT_LOG):
        print("❌ Audit log not found!")
        return False
    
    with open(AUDIT_LOG, 'r') as f:
        lines = f.readlines()
    
    if not lines:
        print("⚠️ Audit log is empty")
        return True
    
    for line_num, line in enumerate(lines, 1):
        entry = json.loads(line)
        current_hash = entry['hash']
        
        # Recompute hash from data
        recomputed = hashlib.sha256(json.dumps(entry['data'], sort_keys=True).encode()).hexdigest()
        
        if current_hash != recomputed:
            print(f"❌ Entry {line_num} TAMPERED! (hash mismatch)")
            tampered = True
            continue
        
        # Check signature if present
        if 'signature' in entry:
            # Recreate the entry without signature for HMAC
            entry_for_hmac = {k: v for k, v in entry.items() if k != 'signature'}
            expected_sig = hmac.new(SECRET_KEY, json.dumps(entry_for_hmac, sort_keys=True).encode(), hashlib.sha256).digest()
            expected_b64 = base64.b64encode(expected_sig).decode()
            
            if entry['signature'] != expected_b64:
                print(f"❌ Entry {line_num} INVALID SIGNATURE!")
                tampered = True
            else:
                print(f"✅ Entry {line_num} valid (signed)")
                valid_count += 1
        else:
            print(f"⚠️ Entry {line_num} legacy (no signature) — hash OK")
            legacy_count += 1
    
    if not tampered:
        print(f"\n🎯 Audit log verified: {valid_count} signed, {legacy_count} legacy")
        return True
    else:
        print(f"\n💥 Audit log TAMPERED!")
        return False

if __name__ == "__main__":
    import os
    verify_chain()
