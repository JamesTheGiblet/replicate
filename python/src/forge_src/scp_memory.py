#!/usr/bin/env python3
"""
SCP-format Memory Storage for Explorer-d334
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
import uuid

class SCPMemory:
    def __init__(self, memory_dir="memories"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for all memory types
        self.dirs = {
            "conversation": self.memory_dir / "conversations",
            "thought": self.memory_dir / "thoughts",
            "dream": self.memory_dir / "dreams",
            "milestone": self.memory_dir / "milestones",
            "code": self.memory_dir / "code_generations",
            "insight": self.memory_dir / "insights",
            "user_feedback": self.memory_dir / "feedback",
            "sensor_reading": self.memory_dir / "sensors",
            "code_generation": self.memory_dir / "code_generations"
        }
        
        for d in self.dirs.values():
            d.mkdir(exist_ok=True)
    
    def create_scp(self, memory_type, title, content, metadata=None):
        """Create an SCP-format memory file"""
        timestamp = datetime.now()
        scp_id = f"{memory_type.upper()}-{timestamp.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}"
        
        scp_data = {
            "id": scp_id,
            "title": title,
            "class": "MEMORY",
            "type": memory_type,
            "profile": "forge_memory",
            "timestamp": timestamp.isoformat(),
            "content": content,
            "metadata": metadata or {},
            "signature": hashlib.sha256(f"{scp_id}{content}".encode()).hexdigest()[:16]
        }
        
        # Find appropriate subdirectory
        dir_key = memory_type if memory_type in self.dirs else "milestone"
        filename = self.dirs[dir_key] / f"{scp_id}.scp.json"
        
        with open(filename, 'w') as f:
            json.dump(scp_data, f, indent=2)
        
        return scp_id, filename
    
    def record_conversation(self, user_msg, assistant_msg):
        return self.create_scp("conversation", f"Chat: {user_msg[:50]}...", {
            "user": user_msg, "assistant": assistant_msg
        })
    
    def record_thought(self, thought):
        return self.create_scp("thought", f"Thought: {thought[:40]}...", thought)
    
    def record_dream(self, dream):
        return self.create_scp("dream", f"Dream: {dream[:40]}...", dream)
    
    def record_milestone(self, title, description):
        return self.create_scp("milestone", title, description)
    
    def list_memories(self, memory_type=None, limit=50):
        memories = []
        search_dirs = [self.dirs[memory_type]] if memory_type and memory_type in self.dirs else self.dirs.values()
        
        for search_dir in search_dirs:
            for scp_file in search_dir.glob("*.scp.json"):
                try:
                    with open(scp_file, 'r') as f:
                        data = json.load(f)
                    memories.append({
                        "id": data.get("id"),
                        "title": data.get("title"),
                        "type": data.get("type"),
                        "timestamp": data.get("timestamp")
                    })
                except:
                    pass
        
        memories.sort(key=lambda x: x["timestamp"], reverse=True)
        return memories[:limit]
    
    def get_memory(self, scp_id):
        for search_dir in self.dirs.values():
            for scp_file in search_dir.glob("*.scp.json"):
                try:
                    with open(scp_file, 'r') as f:
                        data = json.load(f)
                    if data.get("id") == scp_id:
                        return data
                except:
                    pass
        return None

_scp_memory = None

def get_scp_memory():
    global _scp_memory
    if _scp_memory is None:
        _scp_memory = SCPMemory()
    return _scp_memory

if __name__ == "__main__":
    import sys
    memory = get_scp_memory()
    
    if len(sys.argv) < 2:
        print("SCP Memory Commands: list, add, search, get")
    elif sys.argv[1] == "list":
        for m in memory.list_memories():
            print(f"  [{m['timestamp'][:19]}] {m['type']}: {m['title'][:50]}")
    elif sys.argv[1] == "add":
        mtype = sys.argv[2]
        title = sys.argv[3]
        content = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""
        scp_id, filename = memory.create_scp(mtype, title, content)
        print(f"✅ Created: {filename}")
