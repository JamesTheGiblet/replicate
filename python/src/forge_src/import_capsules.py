#!/usr/bin/env python3
import json
import sqlite3
from pathlib import Path
from datetime import datetime

def import_capsules():
    db_path = Path("forge_data.db")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    capsules_dir = Path("capsules")
    if not capsules_dir.exists():
        print("capsules directory not found")
        return
    
    count = 0
    for json_file in capsules_dir.rglob("*.json"):
        try:
            with open(json_file) as f:
                scp = json.load(f)
            name = json_file.stem
            # Insert into scp_prompts table
            cursor.execute('''
                INSERT OR REPLACE INTO scp_prompts
                (name, scp_type, params, logic, created_at, updated_at, version, hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name,
                scp.get('type', 'function'),
                json.dumps(scp.get('params', [])),
                scp.get('logic', ''),
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                1,
                ''
            ))
            count += 1
            print(f"Imported: {name}")
        except Exception as e:
            print(f"Error importing {json_file}: {e}")
    
    conn.commit()
    conn.close()
    print(f"\n✅ Imported {count} capsules from capsules/")

if __name__ == "__main__":
    import_capsules()
