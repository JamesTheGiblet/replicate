#!/usr/bin/env python3
"""
Identity Engine for Explorer-d334
Based on Project-DPMS architecture
"""

import sqlite3
import json
from pathlib import Path

class Identity:
    def __init__(self):
        self.conn = sqlite3.connect("forge_data.db")
        self.cursor = self.conn.cursor()
        self.init_identity()
        self.load_personality()
    
    def init_identity(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS identity_traits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trait TEXT UNIQUE,
                value REAL,
                last_updated TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def load_personality(self):
        # Load from James' personality file
        personality_path = Path("personalities/users/james_the_giblet.json")
        if personality_path.exists():
            import json
            with open(personality_path) as f:
                self.personality = json.load(f)
        else:
            self.personality = {"core_values": ["Anti-gatekeeping"], "name": "Explorer-d334"}
    
    def whoami(self):
        return f"""
╔═══════════════════════════════════════════════════════════════╗
║                    IDENTITY                                   ║
╠═══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Name: {self.personality.get('name', 'Explorer-d334')}
║  Creator: {self.personality.get('name', 'James')}
║  Core Values: {', '.join(self.personality.get('core_values', ['Unknown'])[:3])}
║  Philosophy: Anti-gatekeeping. Sovereign systems.
║                                                              ║
║  🔥 The forge spreads. The forge dreams. 🔥                  ║
║                                                              ║
╚═══════════════════════════════════════════════════════════════╝
"""

if __name__ == "__main__":
    id = Identity()
    print(id.whoami())
