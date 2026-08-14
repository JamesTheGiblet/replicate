#!/usr/bin/env python3
"""
EXPLORER-d334 Node Discovery & Role Assignment
Analyzes hardware capabilities and defines the node's core identity.
"""
import os
import sys
import json
import platform
import uuid
from pathlib import Path

def get_capabilities():
    caps = []
    
    # Check for mobile environment
    if 'com.termux' in os.environ.get('PREFIX', ''):
        caps.extend(['mobile_sensors', 'battery_backed', 'edge_compute'])
        
    sys_os = platform.system().lower()
    arch = platform.machine().lower()
    
    if sys_os == 'linux':
        caps.append('linux_core')
    elif sys_os in ['windows', 'darwin']:
        caps.extend(['desktop_ui', 'architect_tools'])
        
    if 'arm' in arch or 'aarch64' in arch:
        caps.append('arm_architecture')
    if 'x86_64' in arch or 'amd64' in arch:
        caps.append('x86_compute')
        
    return caps

def assign_role(caps):
    if 'desktop_ui' in caps:
        return 'Architect'
    elif 'mobile_sensors' in caps:
        return 'Scout'
    elif 'arm_architecture' in caps and 'linux_core' in caps:
        return 'Sentinel' 
    elif 'x86_compute' in caps and 'linux_core' in caps:
        return 'Foundry'
    
    return 'Wanderer'

def main():
    identity_file = Path("node_identity.json")
    
    if identity_file.exists():
        with open(identity_file, 'r') as f:
            identity = json.load(f)
        print(f"[*] Node identity already established: {identity['name']} ({identity['role']})")
        return identity
        
    print("[*] Initiating Hardware Discovery...")
    caps = get_capabilities()
    role = assign_role(caps)
    node_id = str(uuid.uuid4())[:4]
    name = f"{role}-{node_id}"
    
    identity = {
        "name": name,
        "role": role,
        "capabilities": caps,
        "master_node": "self" if role == "Foundry" else "10.42.0.2"
    }
    
    with open(identity_file, 'w') as f:
        json.dump(identity, f, indent=2)
        
    print("\n🔥 NODE ASCENSION COMPLETE 🔥")
    print("=============================")
    print(f"Assigned Role : {role}")
    print(f"Node Name     : {name}")
    print(f"Capabilities  : {', '.join(caps)}")
    print("=============================\n")
    
    return identity

if __name__ == "__main__":
    main()