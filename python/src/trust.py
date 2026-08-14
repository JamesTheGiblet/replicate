#!/usr/bin/env python3
"""
Simple Trust System - Standalone
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
    
    def get_trust(self, capsule_name):
        self.cursor.execute('SELECT trust_score, successes, failures FROM trust WHERE capsule_name = ?', (capsule_name,))
        row = self.cursor.fetchone()
        if row:
            return {"trust": row[0], "successes": row[1], "failures": row[2]}
        return {"trust": 0.5, "successes": 0, "failures": 0}
    
    def update(self, capsule_name, success):
        info = self.get_trust(capsule_name)
        if success:
            new_trust = min(1.0, info['trust'] + 0.03)
            successes = info['successes'] + 1
            failures = info['failures']
        else:
            new_trust = max(0.0, info['trust'] - 0.05)
            successes = info['successes']
            failures = info['failures'] + 1
        
        self.cursor.execute('''
            INSERT OR REPLACE INTO trust (capsule_name, trust_score, successes, failures, last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', (capsule_name, new_trust, successes, failures, datetime.now().isoformat()))
        self.conn.commit()
        return new_trust
    
    def get_all(self):
        self.cursor.execute('SELECT capsule_name, trust_score, successes, failures FROM trust ORDER BY trust_score DESC')
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()
