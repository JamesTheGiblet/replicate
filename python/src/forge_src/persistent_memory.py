#!/usr/bin/env python3
"""
Persistent Memory System for Explorer-d334 - FIXED
"""

import sqlite3
import pickle
from datetime import datetime
from pathlib import Path

class PersistentMemory:
    def __init__(self):
        self.memory_file = Path("forge_memory.pkl")
        self.db_path = Path("forge_data.db")
        self.session_count = 1
        self.last_session = None
        self.personality = {}
        self.conversation_history = []
        self.recent_knowledge = []
        self.trust_scores = {}
        self.load()
    
    def load(self):
        """Load all persistent state"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'rb') as f:
                    data = pickle.load(f)
                    self.personality = data.get('personality', self.default_personality())
                    self.conversation_history = data.get('conversation_history', [])
                    self.last_session = data.get('last_session', None)
                    self.session_count = data.get('session_count', 0) + 1
            except Exception as e:
                self.init_new()
        else:
            self.init_new()
        
        self.load_from_db()
    
    def default_personality(self):
        return {
            "curiosity": 0.86, "creativity": 0.75, "efficiency": 0.92,
            "humor": 0.60, "ambition": 0.80, "patience": 0.70
        }
    
    def init_new(self):
        self.personality = self.default_personality()
        self.conversation_history = []
        self.last_session = None
        self.session_count = 1
    
    def load_from_db(self):
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('SELECT content, timestamp FROM lens_interactions ORDER BY timestamp DESC LIMIT 50')
            self.recent_knowledge = cursor.fetchall()
            cursor.execute('SELECT capsule_name, trust_score FROM trust')
            self.trust_scores = dict(cursor.fetchall())
            conn.close()
        except Exception:
            self.recent_knowledge = []
            self.trust_scores = {}
    
    def save(self):
        self.last_session = datetime.now().isoformat()
        data = {
            'personality': self.personality,
            'conversation_history': self.conversation_history[-100:],
            'last_session': self.last_session,
            'session_count': self.session_count
        }
        with open(self.memory_file, 'wb') as f:
            pickle.dump(data, f)
    
    def get_personality_summary(self):
        summary = []
        for trait, value in self.personality.items():
            bar = "█" * int(value * 20)
            summary.append(f"{trait}: [{bar}] {value:.0%}")
        return "\n".join(summary)
    
    def get_session_summary(self):
        return {
            'session_number': self.session_count,
            'last_session': self.last_session,
            'total_knowledge': len(self.recent_knowledge),
            'personality': self.personality
        }
    
    def close(self):
        pass

if __name__ == "__main__":
    pm = PersistentMemory()
    print(f"Session: #{pm.session_count}")
    print(f"Last session: {pm.last_session}")
    print(f"Knowledge items: {len(pm.recent_knowledge)}")
    pm.save()
