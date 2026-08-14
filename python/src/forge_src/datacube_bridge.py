#!/usr/bin/env python3
"""
Bridge between Explorer-d334 and Data Cube Visualization
Syncs memory, dreams, and knowledge into the 3D cube system
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

class DataCubeBridge:
    def __init__(self):
        self.cube_data = self.load_cube_data()
    
    def load_cube_data(self):
        """Load existing cube data from localStorage equivalent"""
        cube_file = Path("datacube_knowledge.json")
        if cube_file.exists():
            with open(cube_file, 'r') as f:
                return json.load(f)
        return {"nodes": [], "clusters": [], "metadata": {}}
    
    def export_to_datacube(self, forge_data):
        """Export forge memory to Data Cube format"""
        
        # Convert SCP memories to cube nodes
        memories_dir = Path("memories")
        for mem_type in ["thoughts", "dreams", "milestones"]:
            mem_path = memories_dir / mem_type
            if mem_path.exists():
                for mem_file in mem_path.glob("*.json"):
                    with open(mem_file, 'r') as f:
                        data = json.load(f)
                    
                    # Create a cube node from memory
                    node = {
                        "id": data.get('id', hashlib.md5(data.get('content', '').encode()).hexdigest()[:8]),
                        "topic": data.get('title', 'Untitled'),
                        "entries": [
                            {
                                "lens": self.get_lens_for_type(mem_type),
                                "text": data.get('content', ''),
                                "addedAt": data.get('timestamp', datetime.now().isoformat()),
                                "confidence": data.get('trust_score', 65)
                            }
                        ],
                        "memory": self.extract_keywords(data.get('content', '')),
                        "velocity": {"x": 0, "y": 0, "z": 0}
                    }
                    self.cube_data["nodes"].append(node)
        
        # Save updated cube data
        with open("datacube_knowledge.json", 'w') as f:
            json.dump(self.cube_data, f, indent=2)
        
        return self.cube_data
    
    def get_lens_for_type(self, mem_type):
        """Map forge memory types to Data Cube lenses"""
        lens_map = {
            "thoughts": "OPINION",
            "dreams": "FICTION",
            "milestones": "FACT",
            "interactions": "CONTEXT",
            "validations": "COUNTER"
        }
        return lens_map.get(mem_type, "FACT")
    
    def extract_keywords(self, text):
        """Extract keywords for gravity/clustering"""
        words = text.lower().split()
        stopwords = {'the', 'and', 'to', 'of', 'a', 'in', 'is', 'it', 'for', 'with', 'on', 'at', 'by'}
        keywords = [w for w in words if len(w) > 3 and w not in stopwords]
        
        freq = {}
        for kw in keywords[:10]:
            freq[kw] = freq.get(kw, 0) + 1
        return freq
    
    def sync_from_forge(self):
        """Sync all forge data to Data Cube"""
        print("🔄 Syncing forge memory to Data Cube...")
        
        # Get daily memories
        import subprocess
        result = subprocess.run(["./forge", "today"], capture_output=True, text=True)
        if result.stdout:
            self.add_to_cube("daily_interactions", result.stdout[:200])
        
        # Get dreams
        result = subprocess.run(["./forge", "dreams"], capture_output=True, text=True)
        if result.stdout:
            self.add_to_cube("dreams", result.stdout)
        
        # Get thoughts
        result = subprocess.run(["./forge", "think"], capture_output=True, text=True)
        if result.stdout:
            self.add_to_cube("thoughts", result.stdout)
        
        # Export to file
        self.export_to_datacube({})
        print("✅ Data Cube knowledge file updated")
        return True
    
    def add_to_cube(self, cube_type, content):
        """Add content to specific cube type"""
        # Implementation for adding to cube visualization
        pass

if __name__ == "__main__":
    bridge = DataCubeBridge()
    bridge.sync_from_forge()
