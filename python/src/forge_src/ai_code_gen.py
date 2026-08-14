#!/usr/bin/env python3
from llm_bridge import get_llm

def generate_c_from_description(desc):
    llm = get_llm()
    if not llm.available:
        return "// LLM not available. Please start ollama serve."
    prompt = f"Write a C function that {desc}. Only output the code, no explanation. The function signature should be appropriate."
    return llm.generate(prompt, max_tokens=400)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(generate_c_from_description(" ".join(sys.argv[1:])))
    else:
        print("Usage: python ai_code_gen.py 'description'")
