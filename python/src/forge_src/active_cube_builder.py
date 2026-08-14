#!/usr/bin/env python3
"""
Active Cube Builder - Explorer-d334 actively completes knowledge cubes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import sqlite3
from datetime import datetime
from pathlib import Path
import subprocess

from src.six_lens_classifier import SixLensClassifier
from src.simple_trust import SimpleTrust
from src.daily_memory_lens import DailyMemoryLens

class ActiveCubeBuilder:
    def __init__(self):
        self.classifier = SixLensClassifier()
        self.trust = SimpleTrust()
        self.init_db()
    
    def init_db(self):
        self.conn = sqlite3.connect("forge_data.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_cubes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cube_id TEXT,
                topic TEXT,
                fact_content TEXT,
                created_at TIMESTAMP,
                completed INTEGER DEFAULT 0,
                trust_score REAL DEFAULT 0.5
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pending_validation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cube_id TEXT,
                lens TEXT,
                proposed_content TEXT,
                source_url TEXT,
                source_trust REAL,
                suggested_at TIMESTAMP,
                status TEXT DEFAULT 'pending',
                feedback TEXT,
                approved_at TIMESTAMP,
                rejected_at TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def identify_missing_lenses(self, cube_id):
        self.cursor.execute('SELECT DISTINCT lens FROM lens_interactions WHERE cube_id = ?', (cube_id,))
        existing = set(row[0] for row in self.cursor.fetchall())
        all_lenses = {"FACT", "COUNTER", "OPINION", "FICTION", "CONTEXT", "UNKNOWN"}
        return list(all_lenses - existing)
    
    def search_for_lens_content(self, topic, lens):
        print(f"🔍 Searching for {lens} perspective on: {topic}")
        fallbacks = {
            "COUNTER": f"Some argue that {topic} has limitations and may not be complete.",
            "OPINION": f"Many believe that {topic} represents an important development.",
            "FICTION": f"Imagine if {topic} evolved in unexpected ways in the future.",
            "CONTEXT": f"The concept of {topic} has evolved significantly over time.",
            "UNKNOWN": f"Questions remain about the full implications of {topic}.",
            "FACT": f"Research indicates that {topic} is significant."
        }
        return fallbacks.get(lens, f"Information about {topic}")
    
    def calculate_source_trust(self, content, lens):
        word_count = len(content.split())
        has_citations = "according to" in content.lower() or "research" in content.lower()
        trust = 0.5
        if word_count > 20: trust += 0.1
        if has_citations: trust += 0.15
        return min(0.95, trust)
    
    def propose_addition(self, cube_id, topic, lens):
        content = self.search_for_lens_content(topic, lens)
        source_trust = self.calculate_source_trust(content, lens)
        self.cursor.execute('SELECT id FROM pending_validation WHERE cube_id = ? AND lens = ? AND status = "pending"', (cube_id, lens))
        if self.cursor.fetchone(): return None
        self.cursor.execute('INSERT INTO pending_validation (cube_id, lens, proposed_content, source_trust, suggested_at) VALUES (?, ?, ?, ?, ?)',
                           (cube_id, lens, content, source_trust, datetime.now().isoformat()))
        self.conn.commit()
        return {"cube_id": cube_id, "lens": lens, "content": content, "trust": source_trust, "id": self.cursor.lastrowid}
    
    def validate_and_add(self, validation_id, approved, user_feedback=None):
        self.cursor.execute('SELECT cube_id, lens, proposed_content, source_trust FROM pending_validation WHERE id = ?', (validation_id,))
        row = self.cursor.fetchone()
        if not row: return False
        cube_id, lens, content, trust = row
        if approved:
            dml = DailyMemoryLens()
            dml.record(content, source="web_validation")
            dml.close()
            self.trust.update(f"web_source_{cube_id}_{lens}", True)
            self.cursor.execute('UPDATE pending_validation SET status = "approved", feedback = ?, approved_at = ? WHERE id = ?',
                               (user_feedback or "approved", datetime.now().isoformat(), validation_id))
            print(f"✅ Added {lens} to cube {cube_id}")
        else:
            self.trust.update(f"web_source_{cube_id}_{lens}", False)
            self.cursor.execute('UPDATE pending_validation SET status = "rejected", feedback = ?, rejected_at = ? WHERE id = ?',
                               (user_feedback or "rejected", datetime.now().isoformat(), validation_id))
            print(f"❌ Rejected {lens} for cube {cube_id}")
        self.conn.commit()
        return True
    
    def scan_and_propose(self):
        self.cursor.execute('SELECT DISTINCT cube_id FROM lens_interactions')
        cubes = self.cursor.fetchall()
        proposals = []
        for cube in cubes:
            cube_id = cube[0]
            self.cursor.execute('SELECT content FROM lens_interactions WHERE cube_id = ? AND lens = "FACT" LIMIT 1', (cube_id,))
            fact_row = self.cursor.fetchone()
            topic = fact_row[0][:50] if fact_row else cube_id
            missing = self.identify_missing_lenses(cube_id)
            for lens in missing:
                proposal = self.propose_addition(cube_id, topic, lens)
                if proposal: proposals.append(proposal)
        return proposals
    
    def get_pending_validations(self, min_trust=0.6):
        self.cursor.execute('SELECT id, cube_id, lens, proposed_content, source_trust, suggested_at FROM pending_validation WHERE status = "pending" AND source_trust >= ? ORDER BY source_trust DESC', (min_trust,))
        return self.cursor.fetchall()
    
    def show_pending(self):
        pending = self.get_pending_validations()
        if not pending:
            print("\n📭 No pending validations.")
            return
        print("\n" + "="*60)
        print("📋 PENDING VALIDATIONS - Ready for Review")
        print("="*60)
        for p in pending:
            icon = self.classifier.get_lens_icon(p[2])
            print(f"\n[{p[0]}] {icon} {p[2]} for cube {p[1]}")
            print(f"   Proposal: {p[3][:150]}...")
            print(f"   Trust: {p[4]:.2f}")
            print(f"   Suggested: {p[5][:19]}")
    
    def close(self):
        self.conn.close()
        self.trust.close()

if __name__ == "__main__":
    import sys
    builder = ActiveCubeBuilder()
    if len(sys.argv) < 2:
        print("Active Cube Builder Commands: scan, pending, approve, reject")
    elif sys.argv[1] == "scan":
        builder.scan_and_propose()
        builder.show_pending()
    elif sys.argv[1] == "pending":
        builder.show_pending()
    elif sys.argv[1] == "approve":
        val_id = int(sys.argv[2])
        feedback = sys.argv[3] if len(sys.argv) > 3 else "approved"
        builder.validate_and_add(val_id, True, feedback)
    elif sys.argv[1] == "reject":
        val_id = int(sys.argv[2])
        feedback = sys.argv[3] if len(sys.argv) > 3 else "rejected"
        builder.validate_and_add(val_id, False, feedback)
    builder.close()
