#!/usr/bin/env python3
"""
Simple Trust System for Explorer-d334
No duplicates, proper updates, clean data
"""

import sqlite3
from datetime import datetime
from pathlib import Path

class SimpleTrust:
    def __init__(self):
        self.db_path = Path("forge_data.db")
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        self.cursor.execute('PRAGMA journal_mode=WAL;')
        self.cursor.execute('PRAGMA synchronous=NORMAL;')
        self.init_table()
    
    def init_table(self):
        """Single clean table for trust"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trust (
                capsule_name TEXT PRIMARY KEY,
                trust_score REAL DEFAULT 0.5,
                successes INTEGER DEFAULT 0,
                failures INTEGER DEFAULT 0,
                last_updated TIMESTAMP
            )
        ''')
        self.conn.commit()
        
        # Initialize known capsules
        capsules = [
            "health_wellness_reminder", "dream_imagination_explorer",
            "dream_logic_explorer", "sensor_dashboard", "daily_briefing",
            "test_func", "square", "fibonacci_calculator", "factorial"
        ]
        
        for cap in capsules:
            self.cursor.execute('''
                INSERT OR IGNORE INTO trust (capsule_name, trust_score, last_updated)
                VALUES (?, ?, ?)
            ''', (cap, 0.65 if "dream" in cap or "health" in cap or "sensor" in cap or "daily" in cap else 0.5, 
                  datetime.now().isoformat()))
        
        self.conn.commit()
    
    def update(self, capsule_name, success):
        """Update trust based on success or failure"""
        # Get current trust
        self.cursor.execute('SELECT trust_score, successes, failures FROM trust WHERE capsule_name = ?', (capsule_name,))
        row = self.cursor.fetchone()
        
        if not row:
            old_trust = 0.5
            successes = 0
            failures = 0
        else:
            old_trust = row[0]
            successes = row[1]
            failures = row[2]
        
        # Leighton Weight formula
        if success:
            delta = 0.03
            new_trust = min(1.0, old_trust + delta)
            successes += 1
        else:
            delta = -0.05
            new_trust = max(0.0, old_trust + delta)
            failures += 1
        
        # Update database
        self.cursor.execute('''
            INSERT OR REPLACE INTO trust (capsule_name, trust_score, successes, failures, last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', (capsule_name, new_trust, successes, failures, datetime.now().isoformat()))
        
        self.conn.commit()
        return new_trust
    
    def get_trust(self, capsule_name):
        """Get trust for a capsule"""
        self.cursor.execute('SELECT trust_score, successes, failures FROM trust WHERE capsule_name = ?', (capsule_name,))
        row = self.cursor.fetchone()
        if row:
            return {"trust": row[0], "successes": row[1], "failures": row[2]}
        return {"trust": 0.5, "successes": 0, "failures": 0}
    
    def get_all(self):
        """Get all capsules sorted by trust"""
        self.cursor.execute('SELECT capsule_name, trust_score, successes, failures FROM trust ORDER BY trust_score DESC')
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    trust = SimpleTrust()
    
    print("=== SIMPLE TRUST SYSTEM ===")
    print("\n📊 All capsules:")
    for cap, score, successes, failures in trust.get_all():
        print(f"   {cap}: {score:.3f} (✓{successes} ✗{failures})")
    
    # Test update
    print("\n🔄 Testing trust evolution:")
    test_cap = "daily_briefing"
    initial = trust.get_trust(test_cap)['trust']
    print(f"   Initial: {initial:.3f}")
    
    for i in range(5):
        trust.update(test_cap, True)
        print(f"   After success {i+1}: {trust.get_trust(test_cap)['trust']:.3f}")
    
    for i in range(2):
        trust.update(test_cap, False)
        print(f"   After failure {i+1}: {trust.get_trust(test_cap)['trust']:.3f}")
    
    trust.close()
