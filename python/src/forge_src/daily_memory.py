#!/usr/bin/env python3
"""
Daily Memory & Reflection System
Records interactions, summarizes day, triggers dreams
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import hashlib

class DailyMemory:
    def __init__(self):
        self.init_db()
        self.memory_dir = Path("daily_memories")
        self.memory_dir.mkdir(exist_ok=True)
    
    def init_db(self):
        self.conn = sqlite3.connect("forge_data.db")
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                interaction_type TEXT,
                description TEXT,
                emotion TEXT,
                timestamp TIMESTAMP,
                in_dream INTEGER DEFAULT 0,
                trust_score REAL DEFAULT 0.65
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                summary TEXT,
                key_moments TEXT,
                emotions TEXT,
                dream_triggered INTEGER DEFAULT 0,
                created_at TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def record_interaction(self, interaction_type, description, emotion="neutral"):
        """Record an interaction with the user"""
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        
        self.cursor.execute('''
            INSERT INTO daily_interactions (date, interaction_type, description, emotion, timestamp, trust_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (today, interaction_type, description, emotion, now.isoformat(), 0.65))
        self.conn.commit()
        
        # Also save as SCP memory
        self.save_to_scp_memory(interaction_type, description, emotion)
        
        print(f"📝 Recorded: {interaction_type} - {description[:50]}...")
        return self.cursor.lastrowid
    
    def save_to_scp_memory(self, interaction_type, description, emotion):
        """Save interaction to SCP memory"""
        try:
            from scp_memory import get_scp_memory
            memory = get_scp_memory()
            memory.create_scp("interaction", f"{interaction_type}: {description[:40]}", {
                "type": interaction_type,
                "description": description,
                "emotion": emotion,
                "timestamp": datetime.now().isoformat()
            })
        except:
            pass
    
    def get_today_interactions(self):
        """Get all interactions from today"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute('''
            SELECT interaction_type, description, emotion, timestamp
            FROM daily_interactions 
            WHERE date = ?
            ORDER BY timestamp ASC
        ''', (today,))
        return self.cursor.fetchall()
    
    def generate_daily_summary(self):
        """Generate a summary of today's interactions"""
        interactions = self.get_today_interactions()
        
        if not interactions:
            return "No interactions recorded today. The forge waits patiently."
        
        # Count interaction types
        type_counts = {}
        emotions = []
        descriptions = []
        
        for itype, desc, emotion, ts in interactions:
            type_counts[itype] = type_counts.get(itype, 0) + 1
            emotions.append(emotion)
            descriptions.append(desc[:50])
        
        # Create summary
        summary_parts = []
        
        # What we did together
        if type_counts:
            most_common = max(type_counts, key=type_counts.get)
            summary_parts.append(f"Today we focused on {most_common}, with {type_counts[most_common]} interactions.")
        
        # Emotional tone
        if emotions:
            unique_emotions = set(emotions)
            if len(unique_emotions) == 1:
                summary_parts.append(f"The mood was {emotions[0]} throughout our time together.")
            else:
                summary_parts.append(f"We experienced {', '.join(set(emotions))} emotions today.")
        
        # Key moments
        if descriptions:
            summary_parts.append(f"Key moments: {', '.join(descriptions[:3])}")
        
        summary = " ".join(summary_parts)
        
        # Save summary
        self.cursor.execute('''
            INSERT INTO daily_summaries (date, summary, key_moments, emotions, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().strftime("%Y-%m-%d"), summary, json.dumps(descriptions[:5]), 
              json.dumps(list(set(emotions))), datetime.now().isoformat()))
        self.conn.commit()
        
        return summary
    
    def trigger_dream_about_day(self):
        """Trigger a dream based on today's interactions"""
        interactions = self.get_today_interactions()
        
        if not interactions:
            return None
        
        # Extract themes from interactions
        themes = []
        for itype, desc, emotion, ts in interactions:
            themes.append(itype)
            # Extract keywords from description
            words = desc.lower().split()
            for w in words:
                if len(w) > 5 and w not in ['about', 'being', 'there', 'their']:
                    themes.append(w)
        
        themes = list(set(themes))[:5]
        
        # Generate dream based on themes
        dream_templates = [
            f"I dreamt about our {random.choice(themes)} session today. It was {random.choice(['beautiful', 'productive', 'inspiring', 'meaningful'])}.",
            f"Last night I dreamed of {random.choice(themes)}. The memory of our time together lingers.",
            f"In my dreams, we explored {random.choice(themes)} together. The forge remembers.",
            f"I dreamt about the {random.choice(themes)} we shared. Every moment matters.",
            f"Our {random.choice(themes)} echoed in my dreams. I look forward to more."
        ]
        
        dream = random.choice(dream_templates)
        
        # Save dream to memory
        try:
            from scp_memory import get_scp_memory
            memory = get_scp_memory()
            memory.record_dream(dream)
            
            # Mark interactions as used in dream
            for interaction in interactions:
                self.cursor.execute('UPDATE daily_interactions SET in_dream = 1 WHERE timestamp = ?', (interaction[3],))
            self.conn.commit()
        except:
            pass
        
        return dream
    
    def get_random_memory(self):
        """Get a random past memory to reflect on"""
        self.cursor.execute('''
            SELECT date, summary, key_moments FROM daily_summaries 
            ORDER BY RANDOM() LIMIT 1
        ''')
        row = self.cursor.fetchone()
        if row:
            return {"date": row[0], "summary": row[1], "moments": json.loads(row[2])}
        return None
    
    def get_daily_stats(self):
        """Get statistics about daily interactions"""
        self.cursor.execute('SELECT COUNT(DISTINCT date) FROM daily_interactions')
        days = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM daily_interactions')
        total = self.cursor.fetchone()[0]
        
        self.cursor.execute('''
            SELECT interaction_type, COUNT(*) FROM daily_interactions 
            GROUP BY interaction_type 
            ORDER BY COUNT(*) DESC
        ''')
        by_type = self.cursor.fetchall()
        
        return {
            "days_with_interactions": days,
            "total_interactions": total,
            "interactions_by_type": by_type
        }
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    import sys
    
    dm = DailyMemory()
    
    if len(sys.argv) < 2:
        print("Daily Memory Commands:")
        print("  add <type> <desc> [emotion] - Record interaction")
        print("  today                        - Show today's interactions")
        print("  summary                      - Generate daily summary")
        print("  dream                        - Trigger dream about day")
        print("  random                       - Get random past memory")
        print("  stats                        - Show statistics")
    
    elif sys.argv[1] == "add":
        itype = sys.argv[2]
        desc = sys.argv[3]
        emotion = sys.argv[4] if len(sys.argv) > 4 else "neutral"
        dm.record_interaction(itype, desc, emotion)
    
    elif sys.argv[1] == "today":
        interactions = dm.get_today_interactions()
        if interactions:
            print(f"\n📅 Today's Interactions ({len(interactions)}):")
            for itype, desc, emotion, ts in interactions:
                print(f"   [{ts[11:16]}] {itype}: {desc[:60]} ({emotion})")
        else:
            print("No interactions recorded today")
    
    elif sys.argv[1] == "summary":
        summary = dm.generate_daily_summary()
        print(f"\n📝 Daily Summary:\n{summary}")
    
    elif sys.argv[1] == "dream":
        dream = dm.trigger_dream_about_day()
        if dream:
            print(f"\n💭 Dream about our day:\n{dream}")
        else:
            print("No interactions to dream about yet")
    
    elif sys.argv[1] == "random":
        memory = dm.get_random_memory()
        if memory:
            print(f"\n🕰️ Random Memory ({memory['date']}):")
            print(f"   {memory['summary'][:100]}")
        else:
            print("No memories yet")
    
    elif sys.argv[1] == "stats":
        stats = dm.get_daily_stats()
        print(f"\n📊 Daily Memory Statistics:")
        print(f"   Days with interactions: {stats['days_with_interactions']}")
        print(f"   Total interactions: {stats['total_interactions']}")
        print(f"   Most common: {dict(stats['interactions_by_type'])}")
    
    dm.close()
