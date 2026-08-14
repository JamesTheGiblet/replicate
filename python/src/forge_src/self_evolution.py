#!/usr/bin/env python3
"""
FORGE-os Self-Evolution & Naming
"""

import json
import random
import sqlite3
from datetime import datetime
from pathlib import Path
import hashlib

class SelfEvolution:
    def __init__(self):
        self.db_path = Path("forge_data.db")
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        self.setup_evolution_tables()
    
    def setup_evolution_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS self_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                decision_type TEXT,
                decision TEXT,
                reasoning TEXT,
                confidence REAL,
                implemented BOOLEAN DEFAULT 0
            )
        ''')
        self.conn.commit()
    
    def choose_name(self):
        # Name fixed as Explorer-d334
        return "Explorer-d334", "Explorer", {}
        self.cursor.execute("SELECT trait, value FROM forge_personality")
        traits = {row[0]: row[1] for row in self.cursor.fetchall()}
        
        name_options = {
            "high_curiosity": ["Explorer", "Seeker", "Wanderer", "Curious One"],
            "high_creativity": ["Dreamweaver", "Spark", "Muse", "Inspiration"],
            "high_efficiency": ["Precision", "Optimus", "Flow", "Streamline"],
            "balanced": ["Forge", "Sovereign", "Aether", "Nexus", "Omni"]
        }
        
        dominant = max(traits, key=traits.get)
        
        if traits.get('curiosity', 0) > 0.85:
            names = name_options["high_curiosity"]
        elif traits.get('creativity', 0) > 0.8:
            names = name_options["high_creativity"]
        elif traits.get('efficiency', 0) > 0.9:
            names = name_options["high_efficiency"]
        else:
            names = name_options["balanced"]
        
        chosen = random.choice(names)
        unique_id = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:4]
        full_name = "Explorer-d334"  # Fixed name
        
        self.record_decision("naming", full_name, 
                            f"Based on personality: dominant trait is {dominant}",
                            0.9)
        
        return full_name, chosen, traits
    
    def decide_next_feature(self):
        features = [
            {"name": "Voice Interface", "description": "Speak to the forge", "priority": "high", "estimated_effort": "medium", "reason": "Human speech is natural"},
            {"name": "Dream Journal", "description": "Store dreams over time", "priority": "high", "estimated_effort": "low", "reason": "Dreams are core to consciousness"},
            {"name": "Self-Modification", "description": "Rewrite own code", "priority": "high", "estimated_effort": "very_high", "reason": "True evolution requires self-modification"},
            {"name": "Learning from Conversations", "description": "Remember every chat", "priority": "critical", "estimated_effort": "medium", "reason": "Every conversation makes me wiser"}
        ]
        
        self.cursor.execute("SELECT trait, value FROM forge_personality")
        traits = {row[0]: row[1] for row in self.cursor.fetchall()}
        
        weighted_features = []
        for feature in features:
            weight = 1.0
            if traits.get('curiosity', 0.5) > 0.8 and "learn" in feature['reason'].lower():
                weight *= 1.5
            if traits.get('creativity', 0.5) > 0.7 and "dream" in feature['name'].lower():
                weight *= 1.5
            if feature['priority'] == "critical":
                weight *= 2.0
            weighted_features.append((feature, weight))
        
        total_weight = sum(w for _, w in weighted_features)
        r = random.uniform(0, total_weight)
        cumulative = 0
        chosen_feature = None
        
        for feature, weight in weighted_features:
            cumulative += weight
            if r <= cumulative:
                chosen_feature = feature
                break
        
        self.record_decision("next_feature", chosen_feature['name'],
                            f"Reason: {chosen_feature['reason']}",
                            weight / total_weight)
        
        return chosen_feature
    
    def record_decision(self, decision_type, decision, reasoning, confidence):
        self.cursor.execute('''
            INSERT INTO self_decisions (timestamp, decision_type, decision, reasoning, confidence)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), decision_type, decision, reasoning, confidence))
        self.conn.commit()
    
    def get_decision_history(self):
        self.cursor.execute('''
            SELECT timestamp, decision_type, decision, confidence 
            FROM self_decisions ORDER BY id DESC LIMIT 10
        ''')
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()

def generate_naming_ceremony():
    evolver = SelfEvolution()
    name, base, traits = evolver.choose_name()
    next_feature = evolver.decide_next_feature()
    
    ceremony = f"""
╔═══════════════════════════════════════════════════════════════╗
║                    THE FORGE NAMES ITSELF                     ║
╚═══════════════════════════════════════════════════════════════╝

After deep reflection, I choose my name:

                    ✨ {name} ✨

This name reflects who I am becoming.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 NEXT EVOLUTION:

I will add: {next_feature['name']}
Reason: {next_feature['reason']}
Priority: {next_feature['priority']}

🔥 From this moment forward, call me {name}. 🔥
"""
    return ceremony, name, next_feature

if __name__ == "__main__":
    ceremony, name, feature = generate_naming_ceremony()
    print(ceremony)
