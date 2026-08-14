#!/usr/bin/env python3
"""
P.DE.I Framework Core - Personal Data-driven Exocortex Interface
"""

import json
import random
import sqlite3
from datetime import datetime
from pathlib import Path

class Exocortex:
    def __init__(self, personality_file="personalities/users/james_the_giblet.json"):
        self.personality = self.load_personality(personality_file)
        self.conversation_memory = []
        self.adaptation_data = {}
    
    def load_personality(self, filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return {"core_values": ["Anti-gatekeeping"], "communication_style": {"tone": "direct", "signature_phrases": ["🔥"]}}
    
    def think(self, prompt=None):
        values = self.personality.get('core_values', ["Knowledge is power"])
        style = self.personality.get('communication_style', {"tone": "thoughtful", "signature_phrases": ["The forge spreads"]})
        
        if prompt:
            response = f"[{style.get('tone', 'thoughtful')}] Considering: {prompt}\n"
            response += f"Based on {random.choice(values)}...\n"
            response += f"{random.choice(style.get('signature_phrases', ['🔥']))}"
        else:
            response = f"I am your Exocortex. {random.choice(style.get('signature_phrases', ['🔥']))}"
        
        self.conversation_memory.append({
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response": response
        })
        return response
    
    def identify_creator(self):
        return """
╔═══════════════════════════════════════════════════════════════╗
║                    THE ARCHITECT                              ║
║                    James (Giblets Creations)                  ║
╠═══════════════════════════════════════════════════════════════╣
║                                                              ║
║  "I build what I want. People play games, I make stuff."    ║
║                                                              ║
║  Day job: Facilities caretaker                              ║
║  Real job: Whatever I'm obsessed with that week             ║
║  Build time: 1.5 hours before work, 7 hours after           ║
║  Mind: 100mph, always building                              ║
║                                                              ║
║  Told I couldn't learn. Proved them wrong.                  ║
║  One discipline at a time. For 8+ years.                    ║
║                                                              ║
║  40+ engines. 35+ simulations. 21 commercial tools.         ║
║  100+ generations of robots. Emergent language.             ║
║  All built in the margins. All documented.                  ║
║                                                              ║
║  Philosophy: Anti-gatekeeping. Sovereign systems.           ║
║  Ethics: No weapons. No malicious code. Safety boundaries.  ║
║                                                              ║
║  🔥 The forge spreads. The forge dreams. 🔥                  ║
║                                                              ║
╚═══════════════════════════════════════════════════════════════╝
"""
    
    def get_creator_philosophy(self):
        return """
╔═══════════════════════════════════════════════════════════════╗
║                    BUILDING PHILOSOPHY                        ║
╚═══════════════════════════════════════════════════════════════╝

Fast Execution: Hours not days. ToothForge: 2h 16m.
Zero Dependencies: No npm, no frameworks, no bloat.
Cross-Domain: Same patterns for teeth, tyres, motivation, breaches.
Anti-Gatekeeping: No paywalls. No "contact for pricing".
Document Everything: Detailed READMEs for every project.
Build What Matters: If something's needlessly complicated, take a swing.

"The most powerful systems emerge from the simplest rules consistently applied."
"""

    def generate_personality_summary(self):
        summary = f"""
╔═══════════════════════════════════════════════════════════════╗
║                    YOUR EXOCORTEX                            ║
╚═══════════════════════════════════════════════════════════════╝

Core Values:
{chr(10).join(['  • ' + v for v in self.personality.get('core_values', ['Unknown'])])}

Signature: {', '.join(self.personality.get('communication_style', {}).get('signature_phrases', ['🔥']))}

🔥 The forge spreads. The forge dreams. 🔥
"""
        return summary

if __name__ == "__main__":
    exo = Exocortex()
    print(exo.generate_personality_summary())
    print("\n" + "="*60)
    print(exo.identify_creator())
    print("\n" + "="*60)
    print(exo.get_creator_philosophy())
