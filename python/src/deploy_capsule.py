#!/usr/bin/env python3
"""
FORGE-os Architect Deployment Tool
Pushes locally developed capsules from the Architect node to the Foundry.
"""

import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

# Set this to the Sentinel's Tailscale IP (or localhost if testing on PC)
FOUNDRY_IP = "127.0.0.1" 
PORT = 8085

def deploy_capsule(file_path_str):
    file_path = Path(file_path_str)
    
    if not file_path.exists():
        print(f"❌ Error: Could not find file '{file_path_str}'")
        return
        
    print(f"[*] Reading {file_path.name}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            capsule_content = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: {file_path.name} is not valid JSON.\nDetails: {e}")
        return
        
    url = f"http://{FOUNDRY_IP}:{PORT}/api/capsule/upload"
    payload = json.dumps({
        "filename": file_path.name,
        "content": capsule_content
    }).encode('utf-8')
    
    print(f"🚀 Deploying to Foundry at {FOUNDRY_IP}:{PORT}...")
    try:
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✅ {result.get('message')}")
    except urllib.error.URLError as e:
        print(f"❌ Deployment failed. Is the Foundry online?\nDetails: {e.reason}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deploy_capsule.py <path_to_capsule.scp.json>")
        sys.exit(1)
        
    deploy_capsule(sys.argv[1])