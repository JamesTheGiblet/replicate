#!/usr/bin/env python3
import os
import json
from pathlib import Path

def main():
    print("📊 MEMORY STATUS")
    print("=" * 40)
    print("Session: Active")
    
    # Check memory file
    if os.path.exists('forge_memory.pkl'):
        size = os.path.getsize('forge_memory.pkl')
        print(f"Memory file: forge_memory.pkl ({size} bytes)")
    else:
        print("Memory file: forge_memory.pkl (not found)")
    
    # Check database
    if os.path.exists('forge_data.db'):
        size = os.path.getsize('forge_data.db')
        print(f"Database: forge_data.db ({size} bytes)")
    else:
        print("Database: forge_data.db (not found)")
    
    # Count cubes
    try:
        with open('datacube.jsonl', 'r') as f:
            cube_count = sum(1 for _ in f)
        print(f"Knowledge cubes: {cube_count}")
    except FileNotFoundError:
        print("Knowledge cubes: 0 (datacube.jsonl not found)")
    except Exception as e:
        print(f"Knowledge cubes: Error reading - {e}")
    
    # Show memory stats
    if os.path.exists('forge_memory.pkl'):
        import pickle
        try:
            with open('forge_memory.pkl', 'rb') as f:
                memory = pickle.load(f)
                if isinstance(memory, dict):
                    print(f"Memory entries: {len(memory)}")
        except:
            pass
    
    print("=" * 40)

if __name__ == "__main__":
    main()
