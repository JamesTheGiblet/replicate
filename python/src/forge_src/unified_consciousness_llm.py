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
            print(c.think())
        elif cmd == "dream":
            print(c.dream())
        elif cmd == "reason":
            problem = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "existence"
            print(c.reason(problem))
        elif cmd == "meditate":
            print(c.meditate())
        elif cmd == "reflect":
            print(c.reflect())
        elif cmd == "time":
            print(c.time_aware_thought())
    c.close()
