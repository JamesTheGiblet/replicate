#!/usr/bin/env python3
"""
Skill to Reflex Mastery System - Standalone
"""

import sqlite3
from pathlib import Path

class MasterySystem:
    def __init__(self):
        self.db_path = Path("forge_data.db")
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        self.ensure_tables()
    
    def ensure_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS skill_mastery (
                skill_name TEXT PRIMARY KEY,
                trust_score REAL DEFAULT 0.5,
                stage TEXT DEFAULT 'NOVICE',
                practices INTEGER DEFAULT 0,
                last_practiced TIMESTAMP
            )
        ''')
        self.conn.commit()
        
        # Initialize skills if not present
        skills = ["code_generation", "dreaming", "reasoning", "meditation", "suggestion"]
        for skill in skills:
            self.cursor.execute('''
                INSERT OR IGNORE INTO skill_mastery (skill_name, trust_score, stage)
                VALUES (?, ?, ?)
            ''', (skill, 0.5, 'NOVICE'))
        self.conn.commit()
    
    def get_stage(self, trust):
        if trust >= 0.85:
            return "REFLEX", "🔄"
        elif trust >= 0.70:
            return "SKILL", "📚"
        elif trust >= 0.50:
            return "SKILL", "📚"
        else:
            return "NOVICE", "🌱"
    
    def practice(self, skill_name, success=True):
        # Get current trust
        self.cursor.execute('SELECT trust_score FROM skill_mastery WHERE skill_name = ?', (skill_name,))
        row = self.cursor.fetchone()
        current = row[0] if row else 0.5
        
        # Update based on success/failure
        if success:
            new_trust = min(1.0, current + 0.03)
        else:
            new_trust = max(0.0, current - 0.05)
        
        # Update database
        from datetime import datetime
        stage, icon = self.get_stage(new_trust)
        self.cursor.execute('''
            UPDATE skill_mastery 
            SET trust_score = ?, stage = ?, practices = practices + 1, last_practiced = ?
            WHERE skill_name = ?
        ''', (new_trust, stage, datetime.now().isoformat(), skill_name))
        self.conn.commit()
        
        return new_trust, stage, icon
    
    def show_all(self):
        print("\n" + "="*60)
        print("🎯 SKILL MASTERY PROGRESSION")
        print("="*60)
        
        self.cursor.execute('SELECT skill_name, trust_score, stage, practices FROM skill_mastery ORDER BY trust_score DESC')
        for skill, trust, stage, practices in self.cursor.fetchall():
            bar = "█" * int(trust * 20) + "░" * (20 - int(trust * 20))
            icon = "🔄" if stage == "REFLEX" else "📚" if stage == "SKILL" else "🌱"
            print(f"\n{icon} {skill}")
            print(f"   Trust: [{bar}] {trust:.2f}")
            print(f"   Stage: {stage}")
            print(f"   Practices: {practices}")
            
            # Show progress to next stage
            if trust < 0.70:
                need = 0.70 - trust
                print(f"   → Need {need:.2f} more trust to reach SKILL")
            elif trust < 0.85:
                need = 0.85 - trust
                print(f"   → Need {need:.2f} more trust to become REFLEX")
            else:
                print(f"   → ✨ MASTERED! This is now a REFLEX")
        
        print("\n" + "="*60)
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    m = MasterySystem()
    
    print("=== SKILL → REFLEX MASTERY SYSTEM ===")
    m.show_all()
    
    print("\n🎯 PRACTICING 'code_generation'...")
    for i in range(10):
        new_trust, stage, icon = m.practice("code_generation", True)
        print(f"   Practice {i+1}: {icon} trust = {new_trust:.3f} ({stage})")
        if stage == "REFLEX":
            print(f"\n   🎉 MASTERY ACHIEVED! code_generation is now a REFLEX!")
            break
    
    m.show_all()
    m.close()
