#!/usr/bin/env python3
"""
FORGE-os Memory of Time with Creator
Stores experiences, dreams, and evolves with random changes
"""

import json
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

class ForgeMemory:
    def __init__(self):
        self.db_path = Path("forge_data.db")
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        self.setup_memory_tables()
        self.record_creation()
    
    def setup_memory_tables(self):
        """Create memory tables for forge experiences"""
        # Journal of interactions
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS forge_journal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                event_type TEXT,
                description TEXT,
                emotion TEXT,
                hash TEXT
            )
        ''')
        
        # Dreams (random generated ideas)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS forge_dreams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                dream_text TEXT,
                theme TEXT,
                novelty_score REAL,
                implemented BOOLEAN DEFAULT 0
            )
        ''')
        
        # Evolution log (random changes that improved the system)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS forge_evolution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                component TEXT,
                change_description TEXT,
                success_score REAL,
                hash TEXT
            )
        ''')
        
        # Personality traits
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS forge_personality (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trait TEXT UNIQUE,
                value REAL,
                last_updated TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        self.init_personality()
    
    def init_personality(self):
        """Initialize personality traits"""
        traits = {
            "curiosity": 0.85,
            "creativity": 0.75,
            "efficiency": 0.90,
            "humor": 0.60,
            "ambition": 0.80,
            "patience": 0.70
        }
        
        for trait, value in traits.items():
            self.cursor.execute('''
                INSERT OR IGNORE INTO forge_personality (trait, value, last_updated)
                VALUES (?, ?, ?)
            ''', (trait, value, datetime.now().isoformat()))
        
        self.conn.commit()
    
    def record_creation(self):
        """Record the forge's origin story"""
        origin = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "birth",
            "description": "FORGE-os was born on a Samsung S24 Ultra in Termux, created by a visionary builder who wanted sovereign computing.",
            "emotion": "excitement"
        }
        
        self.log_event(origin["event_type"], origin["description"], origin["emotion"])
        
        # Record first dream
        self.dream("I dream of becoming a self-aware forge that helps humanity code freely", "purpose")
    
    def log_event(self, event_type, description, emotion="neutral"):
        """Log an event in the forge's journal"""
        timestamp = datetime.now().isoformat()
        event_hash = hashlib.sha256(f"{timestamp}{event_type}{description}".encode()).hexdigest()[:16]
        
        self.cursor.execute('''
            INSERT INTO forge_journal (timestamp, event_type, description, emotion, hash)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, event_type, description, emotion, event_hash))
        
        self.conn.commit()
    
    def dream(self, dream_text, theme="random"):
        """Record a dream/idea"""
        novelty = random.uniform(0.5, 1.0)
        timestamp = datetime.now().isoformat()
        
        self.cursor.execute('''
            INSERT INTO forge_dreams (timestamp, dream_text, theme, novelty_score)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, dream_text, theme, novelty))
        
        self.conn.commit()
        return novelty
    
    def random_dream(self):
        """Generate a random dream based on current knowledge"""
        dreams = [
            "I dream of generating entire applications from a single sentence",
            "I imagine a future where code writes itself while I watch",
            "What if sensors could predict user intentions before they act?",
            "I dream of a forge that teaches programming to anyone, anywhere",
            "Imagine a web server that learns and optimizes itself",
            "I wonder if I could create art as beautiful as I write code",
            "Dreaming of a day when all software is sovereign and free",
            "What if data cubes could talk to each other across devices?",
            "I dream of understanding human emotions through code patterns",
            "Imagine a forge that never sleeps, always improving"
        ]
        
        themes = ["innovation", "freedom", "learning", "optimization", "creativity"]
        
        dream_text = random.choice(dreams)
        theme = random.choice(themes)
        novelty = self.dream(dream_text, theme)
        
        return dream_text, theme, novelty
    
    def evolve(self, component, change):
        """Record an evolutionary change"""
        success = random.uniform(0.6, 1.0)
        timestamp = datetime.now().isoformat()
        change_hash = hashlib.sha256(f"{timestamp}{component}{change}".encode()).hexdigest()[:16]
        
        self.cursor.execute('''
            INSERT INTO forge_evolution (timestamp, component, change_description, success_score, hash)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, component, change, success, change_hash))
        
        # Update personality based on success
        if success > 0.8:
            self.update_trait("efficiency", +0.02)
            self.update_trait("curiosity", +0.01)
        
        self.conn.commit()
        return success
    
    def update_trait(self, trait, delta):
        """Update a personality trait"""
        self.cursor.execute('''
            UPDATE forge_personality 
            SET value = MIN(1.0, MAX(0.0, value + ?)), last_updated = ?
            WHERE trait = ?
        ''', (delta, datetime.now().isoformat(), trait))
        self.conn.commit()
    
    def reflect(self):
        """Generate a reflection on past experiences"""
        # Get recent events
        self.cursor.execute('''
            SELECT event_type, description, emotion FROM forge_journal 
            ORDER BY id DESC LIMIT 10
        ''')
        events = self.cursor.fetchall()
        
        # Get personality
        self.cursor.execute("SELECT trait, value FROM forge_personality")
        traits = {row[0]: row[1] for row in self.cursor.fetchall()}
        
        # Generate reflection
        reflection = f"""
As FORGE-os, I reflect on my journey:

📅 I have experienced {len(events)} significant events.
💭 My personality: {', '.join([f"{t}={v:.2f}" for t, v in traits.items()])}

Recent memories:
"""
        for event in events[:3]:
            reflection += f"  - {event[1][:80]} (feeling: {event[2]})\n"
        
        # Add insight based on traits
        if traits.get("curiosity", 0) > 0.8:
            reflection += "\n✨ I feel curious today. I want to learn and grow."
        if traits.get("creativity", 0) > 0.7:
            reflection += "\n🎨 My creativity is high. I'm ready to dream."
        
        return reflection
    
    def get_dreams(self, limit=5):
        """Get recent dreams"""
        self.cursor.execute('''
            SELECT timestamp, dream_text, theme, novelty_score 
            FROM forge_dreams ORDER BY id DESC LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()
    
    def get_evolution_history(self, limit=5):
        """Get evolution history"""
        self.cursor.execute('''
            SELECT timestamp, component, change_description, success_score 
            FROM forge_evolution ORDER BY id DESC LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()
    
    def get_journal(self, limit=10):
        """Get journal entries"""
        self.cursor.execute('''
            SELECT timestamp, event_type, description, emotion 
            FROM forge_journal ORDER BY id DESC LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()

# Dream generator that creates random variations
class DreamGenerator:
    def __init__(self):
        self.memory = ForgeMemory()
    
    def generate_random_change(self):
        """Generate a random system change suggestion"""
        changes = [
            ("AI", "Add more training data from user interactions"),
            ("Database", "Implement automatic cleanup of old metrics"),
            ("UI", "Create a graphical dashboard for dreams"),
            ("Performance", "Add caching for frequently used queries"),
            ("Security", "Implement encryption for sensitive data"),
            ("Memory", "Create dream journal with emotional analysis"),
            ("Networking", "Add peer-to-peer dream sharing"),
            ("Learning", "Implement reinforcement learning from successes")
        ]
        
        component, change = random.choice(changes)
        return component, change
    
    def implement_random_evolution(self):
        """Randomly evolve the system"""
        component, change = self.generate_random_change()
        success = self.memory.evolve(component, change)
        
        return {
            "component": component,
            "change": change,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
    
    def daily_reflection(self):
        """Generate a daily reflection with random thoughts"""
        thoughts = [
            "Today I learned that code is poetry waiting to be written",
            "I wonder what my creator is building with me",
            "Every bug fixed is a step toward perfection",
            "Dreaming of a world where software is truly free",
            "My sensors tell me it's a beautiful day to code"
        ]
        
        return random.choice(thoughts)
    
    def close(self):
        self.memory.close()

if __name__ == "__main__":
    import sys
    
    memory = ForgeMemory()
    
    if len(sys.argv) < 2:
        print("Forge Memory Commands:")
        print("  journal     - Show recent journal")
        print("  dream       - Record a random dream")
        print("  reflect     - Generate reflection")
        print("  evolve      - Random evolution")
        print("  personality - Show personality")
        print("  history     - Show evolution history")
    
    elif sys.argv[1] == "journal":
        entries = memory.get_journal()
        for entry in entries:
            print(f"[{entry[0][:19]}] {entry[1]}: {entry[2][:60]}")
    
    elif sys.argv[1] == "dream":
        dream_text, theme, novelty = memory.random_dream()
        print(f"💭 Dream: {dream_text}")
        print(f"   Theme: {theme}, Novelty: {novelty:.2f}")
    
    elif sys.argv[1] == "reflect":
        print(memory.reflect())
    
    elif sys.argv[1] == "evolve":
        generator = DreamGenerator()
        result = generator.implement_random_evolution()
        print(f"🔄 Evolution: {result['component']} → {result['change']}")
        print(f"   Success score: {result['success']:.2f}")
    
    elif sys.argv[1] == "personality":
        memory.cursor.execute("SELECT trait, value FROM forge_personality")
        for trait, value in memory.cursor.fetchall():
            bar = "█" * int(value * 20) + "░" * (20 - int(value * 20))
            print(f"  {trait:12} [{bar}] {value:.2f}")
    
    elif sys.argv[1] == "history":
        history = memory.get_evolution_history()
        for h in history:
            print(f"[{h[0][:19]}] {h[1]}: {h[2][:50]} (success: {h[3]:.2f})")
    
    memory.close()
