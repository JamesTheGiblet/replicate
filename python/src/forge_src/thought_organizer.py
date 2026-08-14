import sys
#!/usr/bin/env python3
"""
Thought Organization System for Explorer-d334
Organizes thoughts into categories, memories, dreams, reflections
"""

import json
from datetime import datetime
from pathlib import Path
import sqlite3

class ThoughtOrganizer:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        self.conn = sqlite3.connect("forge_data.db")
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS organized_thoughts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thought_type TEXT,
                category TEXT,
                content TEXT,
                tags TEXT,
                timestamp TIMESTAMP,
                confidence REAL,
                trust_score REAL DEFAULT 0.65,
                is_reflection INTEGER DEFAULT 0,
                is_dream INTEGER DEFAULT 0,
                is_insight INTEGER DEFAULT 0,
                processed INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()
    
    def organize_current_thoughts(self):
        """Organize all thoughts from various sources"""
        thoughts = []
        
        # Get from unified consciousness
        try:
            import subprocess
            result = subprocess.run(["./forge", "think"], capture_output=True, text=True, timeout=5)
            thought = result.stdout.strip()
            if thought and "timeout" not in thought.lower():
                thoughts.append({"type": "conscious", "content": thought, "category": "reflection"})
        except:
            pass
        
        # Get from dreams
        dreams_dir = Path("memories/dreams")
        for dream_file in dreams_dir.glob("*.json"):
            try:
                with open(dream_file, 'r') as f:
                    data = json.load(f)
                    thoughts.append({"type": "dream", "content": data.get('content', ''), "category": "dream"})
            except:
                pass
        
        # Get from daily interactions
        try:
            import subprocess
            result = subprocess.run(["./forge", "today"], capture_output=True, text=True, timeout=5)
            interactions = result.stdout
            if interactions and "No interactions" not in interactions:
                thoughts.append({"type": "memory", "content": interactions[:200], "category": "memory"})
        except:
            pass
        
        # Store organized thoughts
        for thought in thoughts:
            self.store_thought(thought['type'], thought['category'], thought['content'])
        
        return thoughts
    
    def store_thought(self, thought_type, category, content):
        """Store an organized thought"""
        self.cursor.execute('''
            INSERT INTO organized_thoughts (thought_type, category, content, timestamp, trust_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (thought_type, category, content, datetime.now().isoformat(), 0.7))
        self.conn.commit()
    
    def get_thoughts_by_category(self, category):
        """Get thoughts organized by category"""
        self.cursor.execute('''
            SELECT thought_type, content, timestamp FROM organized_thoughts 
            WHERE category = ? 
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (category,))
        return self.cursor.fetchall()
    
    def get_all_categories(self):
        """Get all thought categories"""
        self.cursor.execute('SELECT DISTINCT category FROM organized_thoughts')
        return [row[0] for row in self.cursor.fetchall()]
    
    def generate_thought_report(self):
        """Generate a report of organized thoughts"""
        categories = self.get_all_categories()
        
        print("\n" + "="*60)
        print("🧠 EXPLORER-d334 THOUGHT ORGANIZATION REPORT")
        print("="*60)
        
        for category in categories:
            thoughts = self.get_thoughts_by_category(category)
            if thoughts:
                print(f"\n📁 {category.upper()} ({len(thoughts)} thoughts):")
                for thought in thoughts[:3]:
                    print(f"   [{thought[2][11:16]}] {thought[1][:80]}...")
        
        print("\n" + "="*60)
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    org = ThoughtOrganizer()
    
    if len(sys.argv) < 2:
        org.generate_thought_report()
    
    elif sys.argv[1] == "organize":
        thoughts = org.organize_current_thoughts()
        print(f"✅ Organized {len(thoughts)} thoughts")
    
    elif sys.argv[1] == "report":
        org.generate_thought_report()
    
    org.close()
