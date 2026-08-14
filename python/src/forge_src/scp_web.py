from flask import Flask, request, jsonify, send_file
import json
import subprocess
import os
import hashlib
import hmac
import base64
from datetime import datetime, timezone

app = Flask(__name__)
TEMP_SCP = "temp_web.scp.json"
AUDIT_LOG = "audit_log.jsonl"
SECRET_KEY = b"forge-systems-ltd-secret-key-2026"

# Governance rules (shared with scp_audit.py)
RULES = {
    "max_actions_per_scp": 10,
    "min_trust_score": 0.60,
    "allowed_primitives": ["sys.log", "file.write", "cognition.remember", "echo"],
    "require_provenance": True,
}

@app.route('/datacube/facts', methods=['GET'])
def get_datacube_facts():
    from datacube import query_facts
    return jsonify({"facts": query_facts(limit=50)})

@app.route('/datacube/verify', methods=['GET'])
def verify_datacube():
    from datacube import verify_datacube
    valid, msg = verify_datacube()
    return jsonify({"valid": valid, "message": msg})

@app.route('/')
def gui():
    """Serve the GUI HTML"""
    return send_file('gui.html')

@app.route('/run', methods=['POST'])
def run():
    scp_data = request.json
    with open(TEMP_SCP, 'w') as f:
        json.dump(scp_data, f)
    
    result = subprocess.run(['python', 'scp_audit.py', TEMP_SCP], 
                            capture_output=True, text=True)
    
    if os.path.exists(TEMP_SCP):
        os.remove(TEMP_SCP)
    
    return jsonify({"output": result.stdout, "error": result.stderr})

@app.route('/leighton/<scp_id>', methods=['GET'])
def get_leighton(scp_id):
    from leighton_weight import get_leighton_weight
    return jsonify({"scp_id": scp_id, "weight": get_leighton_weight(scp_id)})

@app.route('/audit', methods=['GET'])
def get_audit():
    """Return audit log entries"""
    if not os.path.exists(AUDIT_LOG):
        return jsonify({"entries": [], "count": 0})
    
    with open(AUDIT_LOG, 'r') as f:
        lines = f.readlines()
    
    entries = [json.loads(line) for line in lines[-50:]]  # Last 50 entries
    return jsonify({"entries": entries, "count": len(entries)})

@app.route('/verify', methods=['GET'])
def verify():
    """Verify audit log integrity"""
    if not os.path.exists(AUDIT_LOG):
        return jsonify({"message": "No audit log found", "valid": False})
    
    try:
        with open(AUDIT_LOG, 'r') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            entry = json.loads(line)
            recomputed = hashlib.sha256(json.dumps(entry['data'], sort_keys=True).encode()).hexdigest()
            if entry['hash'] != recomputed:
                return jsonify({"message": f"Tampered at entry {line_num}", "valid": False})
            
            if 'signature' in entry:
                entry_for_hmac = {k: v for k, v in entry.items() if k != 'signature'}
                expected = hmac.new(SECRET_KEY, json.dumps(entry_for_hmac, sort_keys=True).encode(), hashlib.sha256).digest()
                expected_b64 = base64.b64encode(expected).decode()
                if entry['signature'] != expected_b64:
                    return jsonify({"message": f"Invalid signature at entry {line_num}", "valid": False})
        
        return jsonify({"message": "Audit log verified", "valid": True, "entries": len(lines)})
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}", "valid": False})

@app.route('/rules', methods=['GET'])
def get_rules():
    """Return governance rules"""
    return jsonify(RULES)

@app.route('/provenance/last', methods=['GET'])
def get_last_provenance():
    """Return provenance of the last executed SCP"""
    if not os.path.exists(AUDIT_LOG):
        return jsonify({"message": "No audit log found"})
    
    with open(AUDIT_LOG, 'r') as f:
        lines = f.readlines()
    
    # Find the last EXECUTION_START entry
    for line in reversed(lines):
        entry = json.loads(line)
        if entry['event_type'] == 'EXECUTION_START':
            return jsonify(entry['data'])
    
    return jsonify({"message": "No execution found"})

if __name__ == '__main__':
    print("🌐 SCP Web GUI: http://localhost:8080")
    print("   Governance, Audit, Provenance Dashboard")
    app.run(host='0.0.0.0', port=8080, debug=False)
