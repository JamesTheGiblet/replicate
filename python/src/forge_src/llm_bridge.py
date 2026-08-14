#!/usr/env python3
"""
LLM Bridge for FORGE-os - Uses `ollama run` subprocess (reliable)
"""

import subprocess
import shlex

class LLMBridge:
    def __init__(self, model="gemma2:2b"):
        self.model = model
        self.available = self._check()

    def _check(self) -> bool:
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return self.model in result.stdout
        except:
            return False

    def generate(self, prompt: str, system: str = None, max_tokens: int = 200, temp: float = 0.8) -> str:
        if not self.available:
            return "[LLM not available. Run 'ollama serve' and pull gemma2:2b]"

        full_prompt = f"{system}\n\n{prompt}" if system else prompt

        # Escape the prompt for shell safety (simple)
        safe_prompt = full_prompt.replace('"', '\\"')
        cmd = f'ollama run {self.model} "{safe_prompt}"'

        try:
            proc = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            if proc.returncode == 0:
                output = proc.stdout.strip()
                # Truncate excessively long responses
                if len(output) > max_tokens * 5:
                    output = output[:max_tokens*5] + "..."
                return output
            else:
                return f"[LLM error: {proc.stderr[:200]}]"
        except subprocess.TimeoutExpired:
            return "[LLM timeout]"
        except Exception as e:
            return f"[LLM exception: {e}]"

_llm = None
def get_llm():
    global _llm
    if _llm is None:
        _llm = LLMBridge()
    return _llm

if __name__ == "__main__":
    llm = get_llm()
    print(f"LLM available: {llm.available}")
    if llm.available:
        print("Test generation:")
        print(llm.generate("Say hello in one word."))
