#!/usr/bin/env python3
"""
Edge Node Sync Client
Pulls down distributed capsules from the Foundry via the Sentinel relay.
"""
import sys
import json
import urllib.request
import urllib.error
import os
from pathlib import Path

# Dynamically load the FOUNDRY_IP from umbilical_client.py
base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, str(base_dir))
try:
    from umbilical_client import FOUNDRY_IP, PORT
except ImportError:
    FOUNDRY_IP = "127.0.0.1"
    PORT = 8085

def sync_from_foundry():
    url = f"http://{FOUNDRY_IP}:{PORT}/api/capsules/sync"
    capsules_dir = base_dir / "capsules"
    capsules_dir.mkdir(exist_ok=True)
    
    print(f"🔄 Requesting capsule distribution from Foundry ({FOUNDRY_IP})...")
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            capsules = data.get('capsules', {})
            
            count = 0
            for filename, content in capsules.items():
                file_path = capsules_dir / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(content, f, indent=2)
                count += 1
                    
            print(f"✅ Distribution complete. Edge node synced {count} capsules.")
    except urllib.error.URLError as e:
        print(f"❌ Sync failed. Is the Sentinel proxy online?\nDetails: {e.reason}")
    except Exception as e:
        print(f"❌ Error during sync: {e}")

if __name__ == "__main__":
    sync_from_foundry()