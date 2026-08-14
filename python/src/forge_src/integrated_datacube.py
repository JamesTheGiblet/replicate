#!/usr/bin/env python3
"""
Integrated Data Cube + Database Storage
"""

import json
import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class IntegratedDataCube:
    def __init__(self, cube_file="datacube.jsonl", db_file="forge_data.db"):
        self.cube_file = Path(cube_file)
        self.db_conn = sqlite3.connect(db_file)
        self.db_conn.row_factory = sqlite3.Row
        self.init_database()
    
    def init_database(self):
        """Initialize database tables for data cube integration"""
        self.db_conn.execute('''
            CREATE TABLE IF NOT EXISTS data_cube_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact_hash TEXT UNIQUE NOT NULL,
                fact_data TEXT NOT NULL,
                timestamp TIMESTAMP,
                signature TEXT,
                verified BOOLEAN DEFAULT 0
            )
        ''')
        
        self.db_conn.execute('''
            CREATE TABLE IF NOT EXISTS data_cube_chain (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                previous_hash TEXT,
                current_hash TEXT,
                timestamp TIMESTAMP,
                block_number INTEGER
            )
        ''')
        
        self.db_conn.commit()
    
    def add_fact(self, fact_data: Dict, signature: str = None) -> str:
        """Add an immutable fact to the data cube"""
        fact_str = json.dumps(fact_data, sort_keys=True)
        fact_hash = hashlib.sha256(fact_str.encode()).hexdigest()
        
        # Check if already exists
        cursor = self.db_conn.execute(
            "SELECT fact_hash FROM data_cube_facts WHERE fact_hash = ?", 
            (fact_hash,)
        )
        if cursor.fetchone():
            return fact_hash
        
        # Add to database
        self.db_conn.execute('''
            INSERT INTO data_cube_facts (fact_hash, fact_data, timestamp, signature, verified)
            VALUES (?, ?, ?, ?, ?)
        ''', (fact_hash, fact_str, datetime.now().isoformat(), signature, 1 if signature else 0))
        
        # Add to chain - FIXED: use row['current_hash'] instead of row['current_hash']
        cursor = self.db_conn.execute(
            "SELECT current_hash FROM data_cube_chain ORDER BY block_number DESC LIMIT 1"
        )
        row = cursor.fetchone()
        previous_hash = row['current_hash'] if row else "GENESIS"
        
        cursor = self.db_conn.execute(
            "SELECT MAX(block_number) as max_block FROM data_cube_chain"
        )
        max_block = cursor.fetchone()
        block_number = (max_block['max_block'] + 1) if max_block and max_block['max_block'] is not None else 0
        
        self.db_conn.execute('''
            INSERT INTO data_cube_chain (previous_hash, current_hash, timestamp, block_number)
            VALUES (?, ?, ?, ?)
        ''', (previous_hash, fact_hash, datetime.now().isoformat(), block_number))
        
        # Also append to JSONL file
        with open(self.cube_file, 'a') as f:
            record = {
                "hash": fact_hash,
                "data": fact_data,
                "timestamp": datetime.now().isoformat(),
                "signature": signature,
                "previous": previous_hash
            }
            f.write(json.dumps(record) + '\n')
        
        self.db_conn.commit()
        return fact_hash
    
    def get_fact(self, fact_hash: str) -> Dict:
        """Retrieve a fact by its hash"""
        cursor = self.db_conn.execute(
            "SELECT fact_data, timestamp, signature FROM data_cube_facts WHERE fact_hash = ?",
            (fact_hash,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "data": json.loads(row['fact_data']),
                "timestamp": row['timestamp'],
                "signature": row['signature']
            }
        return None
    
    def verify_chain(self) -> bool:
        """Verify the integrity of the entire data cube chain"""
        cursor = self.db_conn.execute(
            "SELECT previous_hash, current_hash FROM data_cube_chain ORDER BY block_number"
        )
        chain = cursor.fetchall()
        
        if not chain:
            return True
        
        for i, block in enumerate(chain):
            if i == 0:
                if block['previous_hash'] != "GENESIS":
                    return False
            else:
                if block['previous_hash'] != chain[i-1]['current_hash']:
                    return False
        return True
    
    def get_chain_length(self) -> int:
        """Get the length of the data cube chain"""
        cursor = self.db_conn.execute("SELECT COUNT(*) as count FROM data_cube_chain")
        result = cursor.fetchone()
        return result['count'] if result else 0
    
    def show_status(self):
        """Show data cube status"""
        print("\n" + "="*50)
        print("DATA CUBE STATUS")
        print("="*50)
        
        verified = self.verify_chain()
        length = self.get_chain_length()
        
        print(f"\n📦 Data Cube Status:")
        print(f"   Chain length: {length} blocks")
        print(f"   Chain verified: {verified}")
        print(f"   Storage: SQLite + JSONL")
        
        # Get latest facts
        cursor = self.db_conn.execute('''
            SELECT fact_data, timestamp FROM data_cube_facts 
            ORDER BY id DESC LIMIT 5
        ''')
        facts = cursor.fetchall()
        
        if facts:
            print(f"\n📋 Latest facts:")
            for fact in facts:
                data = json.loads(fact['fact_data'])
                print(f"   [{fact['timestamp'][:19]}] {data.get('type', 'unknown')}")
        
        print("="*50)
    
    def close(self):
        self.db_conn.close()

if __name__ == "__main__":
    import sys
    
    cube = IntegratedDataCube()
    
    if len(sys.argv) < 2:
        cube.show_status()
    elif sys.argv[1] == "status":
        cube.show_status()
    elif sys.argv[1] == "verify":
        print(f"Chain valid: {cube.verify_chain()}")
    elif sys.argv[1] == "add":
        fact = {"message": " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "test"}
        hash_val = cube.add_fact(fact)
        print(f"✅ Added fact: {hash_val[:16]}...")
    elif sys.argv[1] == "import":
        print("Importing SCPs to data cube...")
        from pathlib import Path
        import json
        scp_dir = Path("scp_prompts")
        if scp_dir.exists():
            count = 0
            for scp_file in scp_dir.glob("*.json"):
                with open(scp_file) as f:
                    scp_data = json.load(f)
                fact = {
                    "type": "scp_prompt",
                    "name": scp_file.stem,
                    "data": scp_data
                }
                cube.add_fact(fact)
                count += 1
            print(f"✅ Imported {count} SCPs to data cube")
    
    cube.close()
