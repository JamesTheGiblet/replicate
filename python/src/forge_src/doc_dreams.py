#!/usr/bin/env python3
"""
View dreams triggered by document creation
"""

import json
from pathlib import Path

def view_doc_dreams():
    dreams_dir = Path("memories/dreams")
    if not dreams_dir.exists():
        print("No document-triggered dreams yet")
        return
    
    dreams = []
    for dream_file in dreams_dir.glob("*.json"):
        with open(dream_file, 'r') as f:
            data = json.load(f)
            content = data.get('content', '')
            if 'dreamt about' in content or 'dream about' in content:
                dreams.append({
                    'timestamp': data.get('timestamp', '')[:19],
                    'content': content
                })
    
    if not dreams:
        print("No document-triggered dreams yet")
        return
    
    print("\n💭 DOCUMENT-INSPIRED DREAMS")
    print("=" * 50)
    for dream in dreams:
        print(f"\n📅 {dream['timestamp']}")
        print(f"   {dream['content'][:150]}")

if __name__ == "__main__":
    view_doc_dreams()
