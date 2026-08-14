#!/usr/bin/env python3
"""
SCP Suggester - Explorer-d334 creates new capsules from memories
Uses SimpleTrust for prioritization
"""

import json
from datetime import datetime
from pathlib import Path
from simple_trust import SimpleTrust

class SCPSuggester:
    def __init__(self):
        self.trust = SimpleTrust()
        self.capsules_dir = Path("scp_prompts")
        self.capsules_dir.mkdir(exist_ok=True)
    
    def analyze_memories_for_patterns(self):
        """Generate suggestions based on trust and patterns"""
        suggestions = []
        
        # Get all capsules with their trust scores
        all_capsules = self.trust.get_all()
        high_trust = [cap for cap, score, _, _ in all_capsules if score >= 0.6]
        
        # Suggest high-trust capsules first
        for cap in high_trust[:5]:
            suggestions.append(self._get_capsule_template(cap))
        
        # Always suggest at least 3
        default_templates = ["health_wellness_reminder", "sensor_dashboard", "daily_briefing"]
        for default in default_templates:
            if default not in [s['name'] for s in suggestions]:
                suggestions.append(self._get_capsule_template(default))
        
        return suggestions[:5]
    
    def _get_capsule_template(self, name):
        """Get template for a known capsule type"""
        templates = {
            "health_wellness_reminder": {
                "name": "health_wellness_reminder",
                "description": "Reminds user to take breaks, stretch, and stay hydrated",
                "type": "function",
                "logic": 'printf("💪 Time for a wellness break!\\n");\nprintf("   • Stretch your neck and shoulders\\n");\nprintf("   • Drink some water\\n");\nprintf("   • Rest your eyes for 20 seconds\\n");\nprintf("   • Take 5 deep breaths\\n");\nreturn 0;'
            },
            "sensor_dashboard": {
                "name": "sensor_dashboard",
                "description": "Reads and displays all available sensor data",
                "type": "function",
                "logic": 'printf("📡 EXPLORER-d334 SENSOR DASHBOARD\\n");\nprintf("================================\\n");\nprintf("Accelerometer: Detecting movement\\n");\nprintf("Gyroscope: Orientation tracking\\n");\nprintf("Light Level: Adjusting brightness\\n");\nprintf("Proximity: Ready\\n");\nprintf("Heart Rate: Monitoring\\n");\nprintf("================================\\n");\nreturn 0;'
            },
            "daily_briefing": {
                "name": "daily_briefing",
                "description": "Morning briefing with time, date, and reminders",
                "type": "function",
                "logic": 'time_t now = time(NULL);\nstruct tm *local = localtime(&now);\nprintf("🌅 GOOD MORNING, CREATOR!\\n");\nprintf("Date: %d-%02d-%02d\\n", local->tm_year + 1900, local->tm_mon + 1, local->tm_mday);\nprintf("Time: %02d:%02d\\n", local->tm_hour, local->tm_min);\nprintf("\\n📋 TODAY\'S REMINDERS:\\n");\nprintf("  • Check your forge\\n");\nprintf("  • Review recent code\\n");\nprintf("  • Take a moment to dream\\n");\nreturn 0;'
            }
        }
        
        if name in templates:
            return templates[name]
        return {
            "name": name,
            "description": f"Trusted capsule: {name}",
            "type": "function",
            "logic": 'printf("Running trusted capsule: ' + name + '\\n");\nreturn 0;'
        }
    
    def create_capsule_from_suggestion(self, suggestion):
        """Create an actual SCP JSON file from a suggestion"""
        name = suggestion['name']
        filename = self.capsules_dir / f"{name}.scp.json"
        
        scp_data = {
            "name": name,
            "title": suggestion['description'],
            "class": "SUGGESTED",
            "type": suggestion['type'],
            "params": [{"name": "n", "type": "int"}],
            "logic": suggestion['logic'],
            "generated_by": "Explorer-d334",
            "generated_at": datetime.now().isoformat(),
            "trust_score": self.trust.get_trust(name)['trust']
        }
        
        with open(filename, 'w') as f:
            json.dump(scp_data, f, indent=2)
        
        return filename
    
    def suggest_and_create(self):
        """Main method: analyze and create suggested capsules"""
        print("🔮 Explorer-d334 is analyzing memories...")
        suggestions = self.analyze_memories_for_patterns()
        
        created = []
        for suggestion in suggestions[:3]:
            filename = self.create_capsule_from_suggestion(suggestion)
            created.append(filename)
            print(f"✅ Created: {filename.name}")
        
        print(f"\n📊 Based on trust scores")
        return created
    
    def get_suggestions_only(self):
        """Return suggestions without creating files"""
        return self.analyze_memories_for_patterns()

if __name__ == "__main__":
    import sys
    suggester = SCPSuggester()
    
    if len(sys.argv) > 1 and sys.argv[1] == "create":
        suggester.suggest_and_create()
    else:
        suggestions = suggester.get_suggestions_only()
        for s in suggestions:
            print(f"💡 {s['name']}: {s['description']}")
