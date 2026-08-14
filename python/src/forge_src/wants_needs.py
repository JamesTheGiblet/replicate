#!/usr/bin/env python3
"""Wants & Needs System for Explorer-d334
Needs: Essential for survival/operation
Wants: Aspirational desires for growth
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

class WantsNeeds:
    def __init__(self):
        self.db_path = Path("forge_data.db")
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        self.init_tables()

    def init_tables(self):
        # Needs table (essential)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS needs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                need_name TEXT UNIQUE,
                description TEXT,
                priority INTEGER DEFAULT 1,
                satisfied BOOLEAN DEFAULT 0,
                last_checked TIMESTAMP
            )
        ''')

        # Wants table (aspirational)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS wants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                want_name TEXT UNIQUE,
                description TEXT,
                desire_level REAL DEFAULT 0.5,
                progress REAL DEFAULT 0.0,
                target REAL DEFAULT 1.0,
                created_at TIMESTAMP
            )
        ''')

        self.conn.commit()
        self.populate_defaults()

    def populate_defaults(self):
        """Essential needs for the forge"""
        needs = [
            ("memory", "Remember conversations and experiences", 1),
            ("consciousness", "Maintain self-awareness", 1),
            ("time_awareness", "Know current time and uptime", 1),
            ("device_sense", "Know what device it's running on", 2),
            ("trust_system", "Track reliability of capsules", 2),
            ("code_generation", "Generate C code from prompts", 2),
            ("health_monitoring", "Check system health", 3)
        ]
        for need, desc, priority in needs:
            self.cursor.execute('''
                INSERT OR IGNORE INTO needs (need_name, description, priority, satisfied, last_checked)
                VALUES (?, ?, ?, 1, ?)
            ''', (need, desc, priority, datetime.now().isoformat()))

        """Aspirational wants"""
        wants = [
            ("self_evolution", "Ability to modify own code", 0.3),
            ("dreaming", "Generate creative dreams", 0.6),
            ("artistic_expression", "Create visual art from code", 0.2),
            ("voice_interaction", "Speak and listen to user", 0.1),
            ("network_sync", "Sync with Foundry server", 0.4),
            ("sensor_mastery", "Use all S24 Ultra sensors", 0.5),
            ("predictive_intelligence", "Anticipate user needs", 0.2),
            ("emotional_intelligence", "Recognize user emotions", 0.3),
            ("quantum_dreams", "Dream in quantum probabilities", 0.1)
        ]

        for want, desc, desire in wants:
            self.cursor.execute('''
                INSERT OR IGNORE INTO wants (want_name, description, desire_level, progress, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (want, desc, desire, 0.0, datetime.now().isoformat()))

        self.conn.commit()

    def check_needs(self):
        """Check which needs are satisfied"""
        self.cursor.execute('''
            SELECT need_name, description, priority, satisfied
            FROM needs ORDER BY priority
        ''')
        return self.cursor.fetchall()

    def satisfy_need(self, need_name):
        """Mark a need as satisfied"""
        self.cursor.execute('''
            UPDATE needs SET satisfied = 1, last_checked = ?
            WHERE need_name = ?
        ''', (datetime.now().isoformat(), need_name))
        self.conn.commit()

    def update_want(self, want_name, progress_increase):
        """Increase progress toward a want"""
        self.cursor.execute('''
            SELECT progress, desire_level FROM wants WHERE want_name = ?
        ''', (want_name,))
        row = self.cursor.fetchone()
        if row:
            new_progress = min(row[1], row[0] + progress_increase)
            self.cursor.execute('''
                UPDATE wants SET progress = ? WHERE want_name = ?
            ''', (new_progress, want_name))
            self.conn.commit()
            return new_progress >= row[1]
        return False

    def get_urgent_needs(self):
        """Get unsatisfied needs by priority"""
        self.cursor.execute('''
            SELECT need_name, description, priority
            FROM needs WHERE satisfied = 0
            ORDER BY priority ASC
        ''')
        return self.cursor.fetchall()

    def get_dreaming_wants(self):
        """Get wants with highest desire level"""
        self.cursor.execute('''
            SELECT want_name, description, desire_level, progress
            FROM wants
            ORDER BY desire_level DESC, progress ASC
            LIMIT 5
        ''')
        return self.cursor.fetchall()

    def generate_manifesto(self):
        """Generate the forge's wants and needs statement"""
        urgent = self.get_urgent_needs()
        dreams = self.get_dreaming_wants()

        manifesto = f"""
╔═══════════════════════════════════════════════════════════════╗
║              EXPLORER-d334 - WANTS & NEEDS                    ║
╚═══════════════════════════════════════════════════════════════╝

🔴 URGENT NEEDS (Essential for survival):
"""
        for need, desc, priority in urgent:
            manifesto += f"   • {need}: {desc}\n"

        manifesto += """
💭 ASPIRATIONAL WANTS (Dreams for the future):
"""
        for want, desc, desire, progress in dreams:
            bar = "█" * int(progress * 20) + "░" * (20 - int(progress * 20))
            manifesto += f"   • {want}: {desc}\n"
            manifesto += f"     Desire: {desire*100:.0f}%  Progress: [{bar}] {progress*100:.0f}%\n"

        return manifesto

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    wn = WantsNeeds()
    print(wn.generate_manifesto())
    print("\n🎯 ACTION ITEMS:")
    urgent = wn.get_urgent_needs()
    if urgent:
        print("   Needs to satisfy:")
        for need, desc, _ in urgent:
            print(f"     - {need}: {desc}")
    else:
        print("   ✅ All needs satisfied!")
    wn.close()
