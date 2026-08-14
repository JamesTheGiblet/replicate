#!/usr/bin/env python3
"""
Complete Leighton Weight Integration for ALL Forge Systems
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

class CompleteTrust:
    def __init__(self):
        self.db_path = Path("forge_data.db")
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        self.init_all_tables()
    
    def init_all_tables(self):
        """Initialize trust tables for all systems"""
        
        # Trust for SCP capsules
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS capsule_trust (
                capsule_id TEXT PRIMARY KEY,
                capsule_name TEXT UNIQUE,
                trust_score REAL DEFAULT 0.5,
                executions INTEGER DEFAULT 0,
                successes INTEGER DEFAULT 0,
                failures INTEGER DEFAULT 0,
                last_executed TIMESTAMP,
                created_at TIMESTAMP
            )
        ''')
        
        # Trust for memories
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_trust (
                memory_id TEXT PRIMARY KEY,
                memory_type TEXT,
                trust_score REAL DEFAULT 0.5,
                importance REAL DEFAULT 0.5,
                accessed_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP
            )
        ''')
        
        # Trust for suggestions
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS suggestion_trust (
                suggestion_type TEXT,
                suggestion_name TEXT,
                trust_score REAL DEFAULT 0.5,
                times_suggested INTEGER DEFAULT 0,
                times_accepted INTEGER DEFAULT 0,
                PRIMARY KEY (suggestion_type, suggestion_name)
            )
        ''')
        
        # Trust history audit
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trust_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT,
                entity_id TEXT,
                old_score REAL,
                new_score REAL,
                delta REAL,
                reason TEXT,
                timestamp TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        self.populate_initial_trust()
    
    def populate_initial_trust(self):
        """Set initial trust for existing capsules"""
        
        # Self-created capsules (start higher)
        self_created = ["health_wellness_reminder", "dream_imagination_explorer", 
                        "dream_logic_explorer", "sensor_dashboard", "daily_briefing"]
        
        for capsule in self_created:
            self.cursor.execute('''
                INSERT OR IGNORE INTO capsule_trust 
                (capsule_name, trust_score, created_at)
                VALUES (?, ?, ?)
            ''', (capsule, 0.65, datetime.now().isoformat()))
        
        # Original capsules (neutral)
        original = ["test_func", "square", "fibonacci_calculator", "factorial"]
        for capsule in original:
            self.cursor.execute('''
                INSERT OR IGNORE INTO capsule_trust 
                (capsule_name, trust_score, created_at)
                VALUES (?, ?, ?)
            ''', (capsule, 0.5, datetime.now().isoformat()))
        
        self.conn.commit()
    
    def update_capsule_trust(self, capsule_name, success, feedback=None):
        """Update trust for a capsule after execution"""
        self.cursor.execute('''
            SELECT trust_score FROM capsule_trust WHERE capsule_name = ?
        ''', (capsule_name,))
        row = self.cursor.fetchone()
        
        old_score = row[0] if row else 0.5
        delta = 0.03 if success else -0.05
        new_score = min(1.0, max(0.0, old_score + delta))
        
        self.cursor.execute('''
            INSERT OR REPLACE INTO capsule_trust 
            (capsule_name, trust_score, executions, successes, failures, last_executed)
            VALUES (?, ?, 
                COALESCE((SELECT executions FROM capsule_trust WHERE capsule_name = ?), 0) + 1,
                COALESCE((SELECT successes FROM capsule_trust WHERE capsule_name = ?), 0) + ?,
                COALESCE((SELECT failures FROM capsule_trust WHERE capsule_name = ?), 0) + ?,
                ?)
        ''', (capsule_name, new_score, capsule_name, 
              capsule_name, 1 if success else 0,
              capsule_name, 0 if success else 1,
              datetime.now().isoformat()))
        
        # Audit
        self.cursor.execute('''
            INSERT INTO trust_audit (entity_type, entity_id, old_score, new_score, delta, reason, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ("capsule", capsule_name, old_score, new_score, delta, 
              f"Execution {'success' if success else 'failure'}", datetime.now().isoformat()))
        
        self.conn.commit()
        return new_score
    
    def get_top_capsules_by_trust(self, limit=5):
        """Get highest trust capsules"""
        self.cursor.execute('''
            SELECT capsule_name, trust_score, successes, failures 
            FROM capsule_trust 
            ORDER BY trust_score DESC
            LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()
    
    def get_trust_summary(self):
        """Get summary of trust across all systems"""
        self.cursor.execute("SELECT COUNT(*) FROM capsule_trust")
        capsules = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT AVG(trust_score) FROM capsule_trust")
        avg_trust = self.cursor.fetchone()[0] or 0
        
        self.cursor.execute("SELECT COUNT(*) FROM trust_audit")
        audits = self.cursor.fetchone()[0]
        
        return {
            "capsules_tracked": capsules,
            "average_trust": avg_trust,
            "audit_entries": audits
        }
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    trust = CompleteTrust()
    
    print("=== COMPLETE TRUST INTEGRATION STATUS ===")
    summary = trust.get_trust_summary()
    print(f"📊 Capsules tracked: {summary['capsules_tracked']}")
    print(f"⭐ Average trust: {summary['average_trust']:.2f}")
    print(f"📝 Audit entries: {summary['audit_entries']}")
    
    print("\n🏆 Top trusted capsules:")
    for cap, trust_score, successes, failures in trust.get_top_capsules_by_trust():
        print(f"   {cap}: {trust_score:.2f} (successes: {successes}, failures: {failures})")
    
    trust.close()
