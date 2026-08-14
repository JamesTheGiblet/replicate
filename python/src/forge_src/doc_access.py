#!/usr/bin/env python3
"""
EXPLORER-d334 Documentation Ingestion
Allows the Forge to read its own architectural blueprints and self-reflect.
"""

import subprocess
from pathlib import Path

def main():
    docs_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "docs"
    if not docs_dir.exists():
        print("❌ No docs directory found.")
        return
        
    print("🧠 Initiating Architectural Self-Reflection...")
    
    for doc in docs_dir.glob("*.md"):
        print(f"  [*] Reading {doc.name}...")
        content = doc.read_text(encoding="utf-8")
        
        # Extract a brief summary/intro to feed into the remember command
        # Taking the first 400 characters to avoid shell limits, focusing on the core definition
        summary = content[:400].replace('\n', ' ').replace('"', "'").strip()
        
        memory_string = f"Self-Documentation: I have read my blueprint '{doc.name}'. Contents begin with: {summary}..."
        
        try:
            subprocess.run(["./forge", "remember", memory_string], capture_output=True, text=True)
            print(f"      ✅ Ingested {doc.name} into Data Cube.")
        except Exception as e:
            print(f"      ❌ Failed to ingest {doc.name}: {e}")
            
    print("\n✨ The Forge is now aware of its own architecture.")
    print("   It will dream of its distributed nature tonight.")

if __name__ == "__main__":
    import os
    main()