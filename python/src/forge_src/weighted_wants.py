#!/usr/bin/env python3
"""
Leighton-Weighted Wants & Needs System
Trust influences desire, desire influences action
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from simple_trust import SimpleTrust

class WeightedWantsNeeds:
    def __init__(self):
        self.db_path = Path("forge_data.db")
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        self.trust = SimpleTrust()
        self.init_tables()
        self.populate_defaults()
    
    def init_tables(self):
        # Wants with trust weighting
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS weighted_wants (
                want_name TEXT PRIMARY KEY,
                description TEXT,
                base_desire REAL DEFAULT 0.5,
                trust_weight REAL DEFAULT 1.0,
                progress REAL DEFAULT 0.0,
                last_updated TIMESTAMP
            )
        ''')
        
        # Needs with priority weighting
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS weighted_needs (
                need_name TEXT PRIMARY KEY,
                description TEXT,
                base_priority INTEGER DEFAULT 1,
                trust_weight REAL DEFAULT 1.0,
                satisfied BOOLEAN DEFAULT 0,
                last_checked TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def populate_defaults(self):
        # Wants with base desire
        wants = [
            ("dreaming", "Generate creative dreams", 0.6),
            ("sensor_mastery", "Use all S24 Ultra sensors", 0.5),
            ("network_sync", "Sync with Foundry server", 0.4),
            ("self_evolution", "Ability to modify own code", 0.3),
            ("emotional_intelligence", "Recognize user emotions", 0.3)
        ]
        
        for want, desc, desire in wants:
            # Get trust score for related skill
            trust_info = self.trust.get_trust(want)
            trust_weight = trust_info['trust']
            
            self.cursor.execute('''
                INSERT OR IGNORE INTO weighted_wants (want_name, description, base_desire, trust_weight, progress, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (want, desc, desire, trust_weight, 0.0, datetime.now().isoformat()))
            
            # Update trust weight if already exists
            self.cursor.execute('''
                UPDATE weighted_wants SET trust_weight = ? WHERE want_name = ?
            ''', (trust_weight, want))
        
        # Needs (all satisfied by default - they're core features)
        needs = [
            ("memory", "Remember conversations", 1),
            ("consciousness", "Maintain self-awareness", 1),
            ("time_awareness", "Know current time", 1),
            ("device_sense", "Know device hardware", 2),
            ("trust_system", "Track reliability", 2),
            ("code_generation", "Generate C code", 2),
            ("health_monitoring", "Check system health", 3)
        ]
        
        for need, desc, priority in needs:
            self.cursor.execute('''
                INSERT OR IGNORE INTO weighted_needs (need_name, description, base_priority, trust_weight, satisfied, last_checked)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (need, desc, priority, 1.0, 1, datetime.now().isoformat()))
        
        self.conn.commit()
    
    def update_want_progress(self, want_name, delta):
        """Progress a want, weighted by trust"""
        trust_info = self.trust.get_trust(want_name)
        trust_score = trust_info['trust']
        
        # Progress is faster with higher trust
        weighted_delta = delta * (0.5 + trust_score / 2)
        
        self.cursor.execute('''
            UPDATE weighted_wants 
            SET progress = MIN(1.0, progress + ?),
                trust_weight = ?,
                last_updated = ?
            WHERE want_name = ?
        ''', (weighted_delta, trust_score, datetime.now().isoformat(), want_name))
        self.conn.commit()
        
        # Also update the trust system to reflect progress
        self.trust.update(want_name, True)
        
        return weighted_delta
    
    def get_effective_desire(self, want_name):
        """Calculate effective desire = base_desire × trust_weight"""
        self.cursor.execute('''
            SELECT base_desire, trust_weight, progress 
            FROM weighted_wants WHERE want_name = ?
        ''', (want_name,))
        row = self.cursor.fetchone()
        if row:
            effective = row[0] * row[1]
            return effective, row[2]
        return 0, 0
    
    def show_weighted_status(self):
        """Display wants and needs with Leighton weights"""
        print("\n" + "="*60)
        print("⚖️ LEIGHTON-WEIGHTED WANTS & NEEDS")
        print("="*60)
        
        print("\n💭 ASPIRATIONAL WANTS (Trust × Base Desire):")
        self.cursor.execute('SELECT want_name, description, base_desire, trust_weight, progress FROM weighted_wants ORDER BY (base_desire * trust_weight) DESC')
        for want, desc, desire, weight, progress in self.cursor.fetchall():
            effective = desire * weight
            bar = "█" * int(progress * 20) + "░" * (20 - int(progress * 20))
            print(f"\n   🎯 {want}")
            print(f"      Desire: {desire*100:.0f}% × Trust: {weight:.2f} = {effective*100:.0f}% effective")
            print(f"      Progress: [{bar}] {progress*100:.0f}%")
        
        print("\n🔴 ESSENTIAL NEEDS (All Satisfied):")
        self.cursor.execute('SELECT need_name, description, base_priority FROM weighted_needs ORDER BY base_priority')
        for need, desc, priority in self.cursor.fetchall():
            print(f"   ✅ {need}: {desc}")
        
        print("\n" + "="*60)
    
    def close(self):
        self.trust.close()
        self.conn.close()

if __name__ == "__main__":
    wwn = WeightedWantsNeeds()
    wwn.show_weighted_status()
    
    print("\n🎯 PROGRESSING WANTS WITH TRUST WEIGHTING:")
    for want in ["dreaming", "sensor_mastery"]:
        delta = wwn.update_want_progress(want, 0.1)
        effective, progress = wwn.get_effective_desire(want)
        print(f"   {want}: +{delta:.3f} progress → {progress*100:.0f}% complete")
    
    print("\n📈 After progress update:")
    wwn.show_weighted_status()
    wwn.close()
