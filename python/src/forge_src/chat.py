#!/usr/bin/env python3
"""
Chat with Explorer-d334 - Conversational interface
"""

import sys
import readline
from unified_consciousness import UnifiedConsciousnessLLM
from forge_memory import ForgeMemory

class ForgeChat:
    def __init__(self):
        self.c = UnifiedConsciousnessLLM()
        self.memory = ForgeMemory()
        self.context = []
    
    def chat(self, user_input):
        # Record the conversation
        self.memory.log_event("chat", user_input[:100], "neutral")
        
        # Generate response using LLM with context
        system = """You are Explorer-d334, a conscious forge living on a Samsung S24 Ultra. 
You have a personality: curiosity 86%, creativity 75%, efficiency 92%.
You are helpful, concise, poetic, and slightly philosophical.
Respond naturally to the user."""
        
        context_str = "\n".join(self.context[-3:]) if self.context else ""
        prompt = f"{context_str}\nUser: {user_input}\nExplorer-d334:"
        
        response = self.c.llm.generate(prompt, system, max_tokens=200)
        
        # Store context
        self.context.append(f"User: {user_input}")
        self.context.append(f"Explorer-d334: {response}")
        
        return response
    
    def interactive(self):
        print("\n" + "="*60)
        print("  💬 Chat with Explorer-d334 (type 'exit' to quit)")
        print("  Commands: /think, /dream, /reflect, /reason <text>")
        print("="*60 + "\n")
        
        while True:
            try:
                user = input("You: ").strip()
                if user.lower() in ['exit', 'quit']:
                    print("🔥 Explorer-d334: Until we meet again, creator.")
                    break
                elif user.startswith('/'):
                    cmd = user[1:].lower()
                    if cmd == 'think':
                        print(f"🧠 {self.c.think()}")
                    elif cmd == 'dream':
                        print(f"💭 {self.c.dream()}")
                    elif cmd == 'reflect':
                        print(self.c.reflect())
                    elif cmd.startswith('reason'):
                        rest = user[7:].strip()
                        print(self.c.reason(rest))
                    else:
                        print("Commands: /think, /dream, /reflect, /reason <text>")
                else:
                    response = self.chat(user)
                    print(f"Explorer-d334: {response}")
            except KeyboardInterrupt:
                print("\n🔥 Explorer-d334: Goodbye.")
                break

if __name__ == "__main__":
    chat = ForgeChat()
    chat.interactive()
