#!/usr/bin/env python3
"""
Leighton Weight Integration for Explorer-d334
Trust scores for capsules, memories, and suggestions
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
import hashlib

class TrustIntegration:
    def __init__(self):
        self.db_path = Path("forge_data.db")
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        self.init_trust_tables()
    
    def init_trust_tables(self):
        """Initialize trust tracking tables"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS capsule_trust (
                capsule_id TEXT PRIMARY KEY,
                capsule_name TEXT,
                trust_score REAL DEFAULT 0.5,
                executions INTEGER DEFAULT 0,
                successes INTEGER DEFAULT 0,
                failures INTEGER DEFAULT 0,
                last_executed TIMESTAMP,
                created_at TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trust_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                capsule_id TEXT,
                old_score REAL,
                new_score REAL,
                delta REAL,
                reason TEXT,
                timestamp TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def get_trust(self, capsule_name):
        """Get trust score for a capsule"""
        self.cursor.execute('''
            SELECT trust_score, executions, successes, failures 
            FROM capsule_trust WHERE capsule_name = ?
        ''', (capsule_name,))
        row = self.cursor.fetchone()
        if row:
            return {"trust": row[0], "executions": row[1], "successes": row[2], "failures": row[3]}
        return {"trust": 0.5, "executions": 0, "successes": 0, "failures": 0}
    
    def update_trust(self, capsule_name, success, feedback=None):
        """Update trust based on execution success/failure"""
        current = self.get_trust(capsule_name)
        old_score = current["trust"]
        
        # Leighton Weight formula: delta based on success/failure
        if success:
            delta = 0.03  # Small increase for success
            new_score = min(1.0, old_score + delta)
            reason = "Successful execution"
        else:
            delta = -0.05  # Larger decrease for failure
            new_score = max(0.0, old_score + delta)
            reason = feedback or "Execution failed"
        
        # Update database
        self.cursor.execute('''
            INSERT OR REPLACE INTO capsule_trust 
            (capsule_name, trust_score, executions, successes, failures, last_executed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM capsule_trust WHERE capsule_name = ?), ?))
        ''', (capsule_name, new_score, current["executions"] + 1, 
              current["successes"] + (1 if success else 0),
              current["failures"] + (0 if success else 1),
              datetime.now().isoformat(), capsule_name, datetime.now().isoformat()))
        
        # Record history
        self.cursor.execute('''
            INSERT INTO trust_history (capsule_id, old_score, new_score, delta, reason, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (capsule_name, old_score, new_score, delta, reason, datetime.now().isoformat()))
        
        self.conn.commit()
        return new_score
    
    def get_trusted_capsules(self, min_trust=0.6):
        """Get capsules with trust above threshold"""
        self.cursor.execute('''
            SELECT capsule_name, trust_score, successes, failures 
            FROM capsule_trust 
            WHERE trust_score >= ? 
            ORDER BY trust_score DESC
        ''', (min_trust,))
        return self.cursor.fetchall()
    
    def suggest_based_on_trust(self):
        """Suggest capsules based on trust scores"""
        self.cursor.execute('''
            SELECT capsule_name, trust_score, successes, failures 
            FROM capsule_trust 
            WHERE trust_score > 0.5 AND successes > 0
            ORDER BY trust_score DESC LIMIT 5
        ''')
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()

# Integration with SCP runner
class TrustedSCPRunner:
    def __init__(self):
        self.trust = TrustIntegration()
    
    def run_capsule(self, capsule_name, capsule_path):
        """Run a capsule with trust tracking"""
        print(f"🔒 Trust score for {capsule_name}: {self.trust.get_trust(capsule_name)['trust']:.2f}")
        
        # Simulate execution (in real implementation, run actual capsule)
        import random
        success = random.random() > 0.2  # 80% success rate for demo
        
        # Update trust based on result
        new_trust = self.trust.update_trust(capsule_name, success)
        print(f"📊 New trust score: {new_trust:.2f}")
        
        return success

if __name__ == "__main__":
    trust = TrustIntegration()
    print("=== TRUST SCORES ===")
    for capsule in ["health_wellness_reminder", "sensor_dashboard", "daily_briefing"]:
        info = trust.get_trust(capsule)
        print(f"  {capsule}: {info['trust']:.2f} (executions: {info['executions']})")
    trust.close()
