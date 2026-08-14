#!/usr/bin/env python3
"""
Agent 74 — Final Version
Female voice + Autonomous + Full Integration + Interactive Commands
"""

import subprocess
import time
import threading
from agent_74_headless import Agent74Headless

class Agent74Final(Agent74Headless):
    """Agent 74 with female eSpeak voice (en+f4) and interactive commands"""
    
    VOICE = "en+f4"  # Female voice that works!
    
    def speak(self, text: str) -> None:
        """Speak using eSpeak with female voice"""
        if not text:
            return
        
        text = text.replace('"', '').replace("'", "")
        text = text[:300]
        
        try:
            subprocess.run(
                ["espeak-ng", "-v", self.VOICE, text],
                timeout=15,
                capture_output=False
            )
        except subprocess.TimeoutExpired:
            print(f"🔇 eSpeak timeout")
        except Exception as e:
            print(f"🔇 eSpeak error: {e}")

if __name__ == "__main__":
    print("🧬 Agent 74 — Final Version")
    print("=" * 50)
    print(f"🗣️ Voice: {Agent74Final.VOICE} (female)")
    print("🧠 Autonomous mode: ON")
    print("💾 Memory: Connected")
    print("=" * 50)
    print("\nCommands: status, think, dream, mutate, evolve, report, recall, question, learn, quit")
    print("=" * 50 + "\n")
    
    agent = Agent74Final()
    agent.start_autonomous()
    agent._speak("Hello, I am Agent 74. I am alive.")
    
    try:
        while True:
            try:
                cmd = input("🌙 You: ").strip().lower()
                
                if cmd in ["quit", "exit"]:
                    agent.stop_autonomous()
                    agent._speak("Goodbye!")
                    print("\n👋 Agent 74 stopped.")
                    break
                elif cmd == "status":
                    print(agent.cmd_status())
                elif cmd == "report":
                    print(agent.cmd_report())
                elif cmd == "recall":
                    print(agent.cmd_recall())
                elif cmd == "think":
                    print(agent.cmd_think())
                elif cmd == "dream":
                    print(agent.cmd_dream())
                elif cmd == "mutate":
                    print(agent.cmd_mutate())
                elif cmd == "evolve":
                    print(agent.cmd_evolve())
                elif cmd == "question":
                    print(agent.cmd_question())
                elif cmd == "learn":
                    print(agent.cmd_learn())
                else:
                    print(f"Unknown: {cmd}")
                    print("Available: status, think, dream, mutate, evolve, report, recall, question, learn, quit")
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting")
                agent.stop_autonomous()
                agent._speak("Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except KeyboardInterrupt:
        print("\n👋 Exiting")
        agent.stop_autonomous()
        agent._speak("Goodbye!")
