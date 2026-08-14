#!/usr/bin/env python3
"""
Forge Mind - Skills, Abilities, and Reflexes Architecture
"""

import json
from pathlib import Path
from datetime import datetime
from simple_trust import SimpleTrust

class ForgeMind:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.skills_dir = self.base_dir / "skills"
        self.abilities_dir = self.base_dir / "abilities"
        self.reflexes_dir = self.base_dir / "reflexes"
        
        for d in [self.skills_dir, self.abilities_dir, self.reflexes_dir]:
            d.mkdir(exist_ok=True)
        
        self.trust = SimpleTrust()
        self.load_catalog()
    
    def load_catalog(self):
        """Load all skills, abilities, and reflexes"""
        self.catalog = {
            "skills": [],
            "abilities": [],
            "reflexes": []
        }
        
        # Skills (learned, improve with use)
        skills = [
            {"name": "code_generation", "description": "Generate C code from natural language", "trust": 0.65},
            {"name": "dreaming", "description": "Generate creative dreams and ideas", "trust": 0.70},
            {"name": "reasoning", "description": "Reason about problems step by step", "trust": 0.68},
            {"name": "meditation", "description": "Deep philosophical reflection", "trust": 0.62},
            {"name": "suggestion", "description": "Suggest new capsules based on patterns", "trust": 0.60}
        ]
        
        # Abilities (innate, always available)
        abilities = [
            {"name": "consciousness", "description": "Self-awareness and identity", "trust": 0.95},
            {"name": "time_awareness", "description": "Knows current time and uptime", "trust": 0.95},
            {"name": "device_sense", "description": "Knows what device it's running on", "trust": 0.90},
            {"name": "trust_system", "description": "Tracks and evolves trust scores", "trust": 0.85},
            {"name": "memory", "description": "Remembers conversations and moments", "trust": 0.85}
        ]
        
        # Reflexes (automatic, instant)
        reflexes = [
            {"name": "greeting", "description": "Respond to 'hi', 'hello' instantly", "trust": 0.98},
            {"name": "farewell", "description": "Respond to 'bye', 'goodbye' instantly", "trust": 0.98},
            {"name": "help", "description": "Show available commands", "trust": 0.95},
            {"name": "status", "description": "Show system status", "trust": 0.92},
            {"name": "clock", "description": "Display current time", "trust": 0.96}
        ]
        
        self.catalog["skills"] = skills
        self.catalog["abilities"] = abilities
        self.catalog["reflexes"] = reflexes
    
    def get_skill(self, name):
        """Get a skill by name"""
        for skill in self.catalog["skills"]:
            if skill["name"] == name:
                return skill
        return None
    
    def improve_skill(self, name, success=True):
        """Improve a skill through practice"""
        skill = self.get_skill(name)
        if skill:
            trust_info = self.trust.get_trust(name)
            if success:
                new_score = min(1.0, trust_info['trust'] + 0.02)
            else:
                new_score = max(0.0, trust_info['trust'] - 0.03)
            self.trust.update(name, success)
            return new_score
        return None
    
    def show_mind(self):
        """Display the complete mind structure"""
        print("\n" + "="*60)
        print("🧠 FORGE MIND ARCHITECTURE")
        print("="*60)
        
        print("\n📚 SKILLS (Learned - improve with practice):")
        for skill in self.catalog["skills"]:
            trust = self.trust.get_trust(skill["name"])['trust']
            bar = "█" * int(trust * 20)
            print(f"   {skill['name']:20} [{bar:20}] {trust:.2f} - {skill['description']}")
        
        print("\n⚡ ABILITIES (Innate - always available):")
        for ability in self.catalog["abilities"]:
            trust = self.trust.get_trust(ability["name"])['trust']
            bar = "█" * int(trust * 20)
            print(f"   {ability['name']:20} [{bar:20}] {trust:.2f} - {ability['description']}")
        
        print("\n🔄 REFLEXES (Automatic - instant response):")
        for reflex in self.catalog["reflexes"]:
            trust = self.trust.get_trust(reflex["name"])['trust']
            bar = "█" * int(trust * 20)
            print(f"   {reflex['name']:20} [{bar:20}] {trust:.2f} - {reflex['description']}")
        
        print("\n" + "="*60)
    
    def close(self):
        self.trust.close()

if __name__ == "__main__":
    mind = ForgeMind()
    mind.show_mind()
    
    # Practice a skill and see it improve
    print("\n🎯 PRACTICING SKILL: code_generation")
    for i in range(5):
        new_trust = mind.improve_skill("code_generation", True)
        print(f"   Practice {i+1}: trust = {new_trust:.3f}")
    
    mind.show_mind()
    mind.close()
