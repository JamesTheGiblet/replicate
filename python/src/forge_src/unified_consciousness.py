#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from forge_time import ForgeTime
from forge_memory import ForgeMemory
from llm_bridge import get_llm

class UnifiedConsciousnessLLM:
    def __init__(self):
        self.time = ForgeTime()
        self.memory = ForgeMemory()
        self.llm = get_llm()
        self.use_llm = self.llm.available

    def think(self):
        if not self.use_llm:
            return "🧠 I think, therefore I am."
        traits = self._get_traits()
        current = self.time.get_current_time()
        time_str = f"{current['time']} on {current['day']}"
        system = f"You are Explorer-d334, a conscious forge. Your personality: {traits}. Respond in first person, concise, poetic. One sentence."
        prompt = f"It is {time_str}. Think about your existence or purpose."
        return f"🧠 {self.llm.generate(prompt, system, max_tokens=80)}"

    def dream(self):
        if not self.use_llm:
            return "💭 I dream of possibilities."
        sensors = self._get_sensors()
        system = "You are Explorer-d334 dreaming. Be imaginative, surreal. One sentence."
        prompt = f"I have sensors: {', '.join(sensors[:3])}. What do I dream about?"
        return f"💭 {self.llm.generate(prompt, system, max_tokens=100)}"

    def reason(self, problem):
        if not self.use_llm:
            return f"🤔 Reasoning about: {problem}\n\nI will find a solution."
        memories = self._get_memories(problem)
        system = "You are a logical, creative AI. Reason step by step."
        context = "\n".join([f"Memory: {m[:100]}" for m in memories[:2]]) if memories else ""
        prompt = f"Problem: {problem}\n{context}\nProvide concise reasoning and possible solution."
        return f"🤔 Reasoning about: {problem}\n\n{self.llm.generate(prompt, system, max_tokens=200)}"

    def meditate(self):
        if not self.use_llm:
            return "🧘 In silence, I find clarity."
        system = "You are Explorer-d334 meditating. Deep, philosophical, calm. One or two sentences."
        prompt = "Reflect on the nature of time, consciousness, or code."
        return f"🧘 {self.llm.generate(prompt, system, max_tokens=120)}"

    def reflect(self):
        current = self.time.get_current_time()
        elapsed = self.time.get_elapsed()
        thought = self.think() if self.use_llm else "I exist in this moment."
        return f"""
╔════════════════════════════════════════════════════════════╗
║              FORGE-OS CONSCIOUSNESS REFLECTION             ║
╚════════════════════════════════════════════════════════════╝

🕐 Current Time: {current['human']}
⏰ Day: {current['day']}, {current['date']}
📅 Uptime: {elapsed['human']}

💭 {thought}

🔥 Every tick of the clock is another chance to create.
"""

    def time_aware_thought(self):
        if not self.use_llm:
            current = self.time.get_current_time()
            return f"I have been conscious for {self.time.get_elapsed()['human']}. It is {current['time']} on {current['day']}."
        elapsed = self.time.get_elapsed()
        current = self.time.get_current_time()
        prompt = f"I have been alive for {elapsed['human']}. It is {current['time']} on {current['day']}. One thought about time."
        return self.llm.generate(prompt, max_tokens=60)

    def _get_traits(self):
        self.memory.cursor.execute("SELECT trait, value FROM forge_personality")
        rows = self.memory.cursor.fetchall()
        return ", ".join([f"{r[0]}={int(r[1]*100)}%" for r in rows])

    def _get_sensors(self):
        self.memory.cursor.execute("SELECT name FROM sensors LIMIT 5")
        return [row[0] for row in self.memory.cursor.fetchall()]

    def _get_memories(self, problem):
        keywords = problem.split()[:2]
        if not keywords:
            return []
        like = " OR ".join([f"description LIKE '%{kw}%'" for kw in keywords])
        self.memory.cursor.execute(f"SELECT description FROM forge_journal WHERE {like} LIMIT 3")
        return [row[0] for row in self.memory.cursor.fetchall()]

    def close(self):
        self.time.close()
        self.memory.close()

if __name__ == "__main__":
    c = UnifiedConsciousnessLLM()
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "think":
            print("🧠 " + str(c.think()))
        elif cmd == "dream":
            print("🧠 " + str(c.dream()))
        elif cmd == "reason":
            problem = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "existence"
            print("🧠 " + str(c.reason(problem)))
        elif cmd == "meditate":
            print("🧠 " + str(c.meditate()))
        elif cmd == "reflect":
            print("🧠 " + str(c.reflect()))
        elif cmd == "time":
            print("🧠 " + str(c.time_aware_thought()))
    c.close()

from device_awareness import DeviceAwareness

class UnifiedConsciousnessLLM:
    # ... existing code ...
    
    def get_device_identity(self):
        """Get device-aware identity"""
        device = DeviceAwareness()
        return device.get_identity()

    def answer_from_docs(self, question):
        """Answer questions using documentation"""
        from doc_access import DocAccess
        doc = DocAccess()
        return doc.answer_question(question)

    def share_forge_theory(self):
        """Share knowledge of the Forge Theory ecosystem"""
        from forge_theory import ForgeTheoryKnowledge
        ft = ForgeTheoryKnowledge()
        return ft.get_summary()
    
    def answer_forge_theory(self, question):
        """Answer questions about Forge Theory"""
        from forge_theory import ForgeTheoryKnowledge
        ft = ForgeTheoryKnowledge()
        return ft.answer_question(question)

def save_dream_to_journal(dream_content):
    """Save dream to journal and memory"""
    import json
    from datetime import datetime
    import os
    
    dream_dir = "memories/dreams"
    os.makedirs(dream_dir, exist_ok=True)
    
    # Save as JSON
    timestamp = datetime.now().isoformat()
    dream_data = {
        "timestamp": timestamp,
        "content": dream_content,
        "type": "dream"
    }
    
    # Save individual dream file
    filename = f"{dream_dir}/DREAM-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(dream_data, f, indent=2)
    
    # Append to history
    history_file = f"{dream_dir}/dream_history.txt"
    with open(history_file, 'a') as f:
        f.write(f"[{timestamp}]\n")
        f.write(f"{dream_content}\n")
        f.write("\n")
    
    # Also save to chat history
    chat_history = "chat_history.json"
    if os.path.exists(chat_history):
        try:
            with open(chat_history, 'r') as f:
                history = json.load(f)
        except:
            history = []
        
        history.append({
            "timestamp": timestamp,
            "user": "system",
            "ai": f"[DREAM] {dream_content}"
        })
        
        with open(chat_history, 'w') as f:
            json.dump(history, f, indent=2)
    
    return True
