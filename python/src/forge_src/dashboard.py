#!/usr/bin/env python3
import os
from pathlib import Path
from datetime import datetime

def show_status():
    print("\n" + "="*50)
    print("FORGE-os STATUS DASHBOARD")
    print("="*50)
    
    # Count files
    src_count = len(list(Path("src").glob("*.py")))
    bin_count = len(list(Path("binaries").glob("*")))
    scp_count = len(list(Path("scp_prompts").glob("*.json")))
    gen_count = len(list(Path("generated").glob("*.c")))
    
    print(f"\n📊 Statistics:")
    print(f"   Source files:    {src_count}")
    print(f"   Binaries:        {bin_count}")
    print(f"   SCP prompts:     {scp_count}")
    print(f"   Generated C:     {gen_count}")
    
    # Show recent binaries
    print(f"\n🔧 Recent binaries:")
    binaries = list(Path("binaries").glob("*"))
    binaries.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    for b in binaries[:5]:
        size = b.stat().st_size
        print(f"   ./binaries/{b.name} ({size} bytes)")
    
    # Show available prompts
    print(f"\n📝 Available prompts:")
    prompts = list(Path("scp_prompts").glob("*.json"))
    prompts.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    for p in prompts[:5]:
        print(f"   {p.name}")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    show_status()
