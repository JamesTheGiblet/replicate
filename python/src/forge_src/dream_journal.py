#!/usr/bin/env python3
"""
Dream Journal - View all dreams
"""

import json
from pathlib import Path

def view_all_dreams():
    dreams_dir = Path("memories/dreams")
    if not dreams_dir.exists():
        print("No dreams recorded yet")
        return
    
    dreams = []
    for dream_file in dreams_dir.glob("*.json"):
        with open(dream_file, 'r') as f:
            data = json.load(f)
            dreams.append({
                'timestamp': data.get('timestamp', 'unknown')[:19],
                'dream': data.get('content', '')
            })
    
    dreams.sort(key=lambda x: x['timestamp'], reverse=True)
    
    print("\n" + "="*60)
    print("💭 EXPLORER-d334 DREAM JOURNAL")
    print("="*60)
    
    for dream in dreams:
        print(f"\n📅 {dream['timestamp']}")
        print(f"   {dream['dream']}")
    
    print("\n" + "="*60)
    print(f"Total dreams: {len(dreams)}")

if __name__ == "__main__":
    view_all_dreams()
